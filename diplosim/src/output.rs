//! conversion.py (CHR/POS, REF/ALT, tree-building columns) and the files tx_simulation saves
//! (simulate.py:100-106), plus the HP columns and `truth/`.
use std::fs;
use std::io::{self, Write};
use std::path::Path;

use rand::distributions::WeightedIndex;
use rand::seq::SliceRandom;
use rand::Rng as _;
use rand_distr::Distribution;

use crate::{np_round2, py_float, Rng, Simulation};

/// conversion.py:36 chr_lengths (chromosomes 1-22).
const CHR_LENGTHS: [u64; 22] = [
    247199719, 242751149, 199446827, 191263063, 180837866, 170896993, 158821424, 146274826, 140442298,
    135374737, 134452384, 132289534, 114127980, 106360585, 100338915, 88822254, 78654742, 76117153,
    63806651, 62435965, 46944323, 49528953,
];

/// A position's label. Only a label: no step reads it back.
#[derive(Clone, Debug)]
pub struct Locus {
    pub chr: u32,
    pub pos: u64,
    pub ref_base: char,
    pub alt_base: char,
}

/// conversion.py:35 assign_chr_pos_correct and the REF/ALT draw (conversion.py:12).
pub fn assign_loci(n_positions: usize, rng: &mut Rng) -> Result<Vec<Locus>, String> {
    let chr_dist = WeightedIndex::new(CHR_LENGTHS).unwrap();
    let mut loci: Vec<Locus> = (0..n_positions)
        .map(|_| {
            let c = chr_dist.sample(rng);
            Locus { chr: c as u32 + 1, pos: rng.gen_range(1..CHR_LENGTHS[c]), ref_base: 'N', alt_base: 'N' }
        })
        .collect();
    let mut seen: Vec<(u32, u64)> = loci.iter().map(|l| (l.chr, l.pos)).collect();
    seen.sort_unstable();
    if seen.windows(2).any(|w| w[0] == w[1]) {
        return Err("duplicate CHR/POS drawn (CONIPHER asserts here, conversion.py:42); try another seed".into());
    }
    for l in &mut loci {
        let pair: Vec<char> = ['A', 'C', 'T', 'G'].choose_multiple(rng, 2).copied().collect();
        (l.ref_base, l.alt_base) = (pair[0], pair[1]);
    }
    Ok(loci)
}

/// The derived columns of conversion.py:4-27 for one row, before rounding.
struct Converted {
    ccf_obs: f64,
    total_copy: f64,
}

fn fill0(x: f64) -> f64 {
    if x.is_nan() {
        0.0
    } else {
        x
    }
}

fn r2(x: f64) -> String {
    py_float(np_round2(fill0(x)))
}

fn write_tsv(path: &Path, header: &[&str], rows: impl IntoIterator<Item = Vec<String>>) -> io::Result<()> {
    let mut w = io::BufWriter::new(fs::File::create(path)?);
    writeln!(w, "{}", header.join("\t"))?;
    for row in rows {
        writeln!(w, "{}", row.join("\t"))?;
    }
    w.flush()
}

fn py_bool(b: bool) -> String {
    if b { "True" } else { "False" }.to_string()
}

/// Writes `<name>.tsv`, `<name>_TX.tsv`, `<name>_treeedges.tsv`, `<name>_cloneprops.tsv`,
/// `<name>_info.tsv` and `truth/` into `dir`.
pub fn write_all(sim: &Simulation, dir: &Path, name: &str) -> io::Result<()> {
    fs::create_dir_all(dir.join("truth"))?;
    let sample_name = format!("U_{name}_SU_T1.R1");
    let converted: Vec<Converted> = sim
        .rows
        .iter()
        .map(|r| Converted {
            ccf_obs: (r.est_vaf() * r.total_fract_cn) / (r.fract_variant * r.purity),
            total_copy: r.fract_a + r.fract_b,
        })
        .collect();
    let ploidy = converted.iter().map(|c| c.total_copy).sum::<f64>() / converted.len() as f64;

    let og_header = [
        "PATIENT", "SAMPLE", "VAR_POS", "CHR", "POS", "REF", "ALT", "REF_COUNT", "VAR_COUNT", "DEPTH",
        "TRUE_VAF", "VAF_OBS", "TRUE_CCF", "TRUE_DCF", "CCF_OBS", "MUT_CN", "CN_A", "CN_B", "TOTAL_CN",
        "CN_PREVALENCE", "PURITY", "PLOIDY", "CLUSTER", "NOISE", "ALLELE", "HP1_REF", "HP1_ALT",
        "HP2_REF", "HP2_ALT", "HP0_REF", "HP0_ALT",
    ];
    let og_rows = sim.rows.iter().zip(&converted).zip(&sim.hp).map(|((r, c), h)| {
        let l = &sim.loci[r.pos];
        vec![
            name.to_string(),
            sample_name.clone(),
            r.pos.to_string(),
            l.chr.to_string(),
            l.pos.to_string(),
            l.ref_base.to_string(),
            l.alt_base.to_string(),
            (r.total_reads - r.variant_reads).to_string(),
            r.variant_reads.to_string(),
            r.total_reads.to_string(),
            r2(r.true_vaf),
            r2(r.est_vaf()),
            r2(r.ccf),
            r2(r.dcf),
            r2(c.ccf_obs),
            r2(r.fract_variant),
            r2(r.fract_a),
            r2(r.fract_b),
            r2(c.total_copy),
            r2(r.cn_prevalence),
            r2(r.purity),
            r2(ploidy),
            r.child.to_string(),
            py_bool(r.noise),
            sim.alleles[r.pos].name().to_string(),
            h.hp1_ref.to_string(),
            h.hp1_alt.to_string(),
            h.hp2_ref.to_string(),
            h.hp2_alt.to_string(),
            h.hp0_ref.to_string(),
            h.hp0_alt.to_string(),
        ]
    });
    write_tsv(&dir.join(format!("{name}.tsv")), &og_header, og_rows)?;

    let tx_header = [
        "PATIENT", "SAMPLE", "CHR", "POS", "REF", "ALT", "REF_COUNT", "VAR_COUNT", "DEPTH", "CLUSTER",
        "CCF_PHYLO", "CCF_OBS", "MUT_COPY", "COPY_NUMBER_A", "COPY_NUMBER_B", "ACF", "PLOIDY",
    ];
    let tx_rows = sim.rows.iter().zip(&converted).map(|(r, c)| {
        let l = &sim.loci[r.pos];
        vec![
            name.to_string(),
            sample_name.clone(),
            l.chr.to_string(),
            l.pos.to_string(),
            l.ref_base.to_string(),
            l.alt_base.to_string(),
            (r.total_reads - r.variant_reads).to_string(),
            r.variant_reads.to_string(),
            r.total_reads.to_string(),
            r.child.to_string(),
            r2(c.ccf_obs),
            r2(c.ccf_obs),
            r2(r.fract_variant),
            r2(r.fract_a),
            r2(r.fract_b),
            r2(r.purity),
            r2(ploidy),
        ]
    });
    write_tsv(&dir.join(format!("{name}_TX.tsv")), &tx_header, tx_rows)?;

    let tree = &sim.tree;
    let edge_rows = tree.edges.iter().zip(&sim.evolution.edge_labels).map(|(&(parent, child), lab)| {
        vec![
            parent.to_string(),
            child.to_string(),
            lab.cna_gains.to_string(),
            lab.cna_losses.to_string(),
            lab.snvs.to_string(),
            lab.wgd.to_string(),
            if parent == tree.root { "Yes" } else { "No" }.to_string(),
        ]
    });
    write_tsv(
        &dir.join(format!("{name}_treeedges.tsv")),
        &["Parent", "Child", "CNA_gains", "CNA_losses", "SNVs", "WGD", "Truncal"],
        edge_rows,
    )?;

    let prop_rows = sim.sample.proportions.iter().map(|(&clone, &p)| {
        vec![
            "Sample 1".to_string(),
            clone.to_string(),
            py_float(p),
            if clone == tree.root { "Yes" } else { "No" }.to_string(),
        ]
    });
    write_tsv(&dir.join(format!("{name}_cloneprops.tsv")), &["Sample", "Clone", "Proportion", "Is_Normal"], prop_rows)?;

    write_tsv(&dir.join(format!("{name}_info.tsv")), &["parameter", "value"], info_rows(sim, name))?;
    write_truth(sim, &dir.join("truth"))
}

fn join<T: ToString>(xs: impl IntoIterator<Item = T>) -> String {
    xs.into_iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
}

fn info_rows(sim: &Simulation, name: &str) -> Vec<Vec<String>> {
    let p = &sim.params;
    let rows: Vec<(&str, String)> = vec![
        ("patient_name", name.to_string()),
        ("n_clones", p.n_clones.to_string()),
        ("n_snv", p.n_snv.to_string()),
        ("prop_truncal_snvs", py_float(p.prop_truncal_snvs)),
        ("prop_pos_gained", py_float(p.prop_pos_gained)),
        ("prop_pos_lost", py_float(p.prop_pos_lost)),
        ("prop_gained_truncal", py_float(p.prop_gained_truncal)),
        ("prop_lost_truncal", py_float(p.prop_lost_truncal)),
        ("prop_pos_second_cna", py_float(p.prop_pos_second_cna)),
        ("gain_events", join(p.gain_events.iter().map(|e| e.name()))),
        ("loss_events", join(p.loss_events.iter().map(|e| e.name()))),
        ("prop_mutloss_positions", py_float(p.prop_mutloss_positions)),
        ("mutloss_truncal", py_bool(p.mutloss_truncal)),
        ("constant_multiplicity", py_bool(p.constant_multiplicity)),
        ("clonal_wgd", py_bool(p.clonal_wgd)),
        ("subclonal_wgd", py_bool(p.subclonal_wgd)),
        ("n_subclonal_wgd", p.n_subclonal_wgd.to_string()),
        ("minimum_branch_length", p.minimum_branch_length.to_string()),
        ("coverage", py_float(p.coverage)),
        ("min_tumour_purity", py_float(p.min_tumour_purity)),
        ("max_tumour_purity", py_float(p.max_tumour_purity)),
        ("fract_noise", py_float(p.fract_noise)),
        ("n_noise_clones", p.n_noise_clones.to_string()),
        ("prop_snv_on_b", py_float(p.prop_snv_on_b)),
        ("prop_tagged", py_float(p.prop_tagged)),
        ("tag_concentration", p.tag_concentration.map_or("None".to_string(), py_float)),
        ("mistag_rate", py_float(p.mistag_rate)),
        ("base_error", py_float(p.base_error)),
        ("random_seed", sim.seed.to_string()),
        ("purity", py_float(sim.sample.purity)),
        ("prop_mut_lost", py_float(sim.evolution.prop_mutation_loss)),
        ("noise_clones", join(&sim.noise_clones)),
        ("simulation_warnings", sim.warnings.join(" | ")),
    ];
    rows.into_iter().map(|(k, v)| vec![k.to_string(), v]).collect()
}

fn write_truth(sim: &Simulation, dir: &Path) -> io::Result<()> {
    let evo = &sim.evolution;
    let n_pos = sim.alleles.len();
    let geno_rows = (0..n_pos).flat_map(|pos| {
        evo.total.iter().map(move |(&clone, profile)| {
            let g = profile[pos];
            vec![
                pos.to_string(),
                clone.to_string(),
                g.a.to_string(),
                g.b.to_string(),
                g.mutated.to_string(),
                evo.dcf[&clone][pos].mutated.to_string(),
            ]
        })
    });
    write_tsv(&dir.join("genotypes.tsv"), &["VAR_POS", "CLONE", "A", "B", "MUT", "MUT_DCF"], geno_rows)?;

    let mut snv_rows: Vec<(usize, Vec<String>)> = sim
        .tree
        .edges
        .iter()
        .zip(&evo.snv_edges)
        .flat_map(|(&(parent, child), positions)| {
            positions.iter().map(move |&pos| {
                (pos, vec![pos.to_string(), parent.to_string(), child.to_string(), sim.alleles[pos].name().to_string()])
            })
        })
        .collect();
    snv_rows.sort_by_key(|(pos, _)| *pos);
    write_tsv(
        &dir.join("snv_edges.tsv"),
        &["VAR_POS", "PARENT", "CHILD", "ALLELE"],
        snv_rows.into_iter().map(|(_, r)| r),
    )?;

    let event_rows = evo.events.iter().flat_map(|(&node, by_pos)| {
        by_pos.iter().map(move |(&pos, list)| {
            vec![node.to_string(), pos.to_string(), join(list.iter().map(|e| e.name()))]
        })
    });
    write_tsv(&dir.join("events.tsv"), &["CLONE", "VAR_POS", "EVENTS"], event_rows)
}
