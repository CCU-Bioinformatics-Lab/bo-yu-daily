//! diplosim: Rust port of the CONIPHER/TRACERx bulk simulator (commit facd2d7) for one bulk
//! sample, plus the HP1/HP2 extensions in `hp`. One module per CONIPHER file; see
//! docs/porting_map.md.
pub mod evolution;
pub mod hp;
pub mod noise;
pub mod output;
pub mod params;
pub mod sequencing;
pub mod topology;

use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;

use evolution::Evolution;
use hp::{Allele, HpCounts};
use output::Locus;
use params::Params;
use sequencing::{Sample, VariantRow};
use topology::{NodeId, Tree};

pub type Rng = ChaCha8Rng;

/// Python's `round(x)` on a float: nearest integer, ties to even.
pub fn py_round(x: f64) -> i64 {
    x.round_ties_even() as i64
}

/// numpy/pandas `round(x, 2)`: `rint(x * 100) / 100`.
pub fn np_round2(x: f64) -> f64 {
    (x * 100.0).round_ties_even() / 100.0
}

/// A float as Python's `repr`/pandas `to_csv` writes it (`1.0`, `0.25`, `inf`; NaN as empty).
pub fn py_float(x: f64) -> String {
    if x.is_nan() {
        String::new()
    } else if x.is_finite() && x == x.trunc() && x.abs() < 1e16 {
        format!("{x:.1}")
    } else {
        format!("{x}")
    }
}

/// One simulated patient: the tree, its true genotypes, and the observed sample.
#[derive(Clone, Debug)]
pub struct Simulation {
    pub params: Params,
    pub seed: u64,
    pub tree: Tree,
    /// Genotypes and events after the allele relabel.
    pub evolution: Evolution,
    /// SNV allele per position (A = HP1, B = HP2).
    pub alleles: Vec<Allele>,
    pub sample: Sample,
    /// One row per position, in position order.
    pub rows: Vec<VariantRow>,
    /// Aligned with `rows`.
    pub hp: Vec<HpCounts>,
    pub loci: Vec<Locus>,
    pub noise_clones: Vec<NodeId>,
    pub warnings: Vec<String>,
}

/// simulate.py:13 tx_simulation (with make_a_simulation and simulation) for one sample, plus the
/// two HP steps. The same params and seed always give the same result.
pub fn simulate(params: &Params, seed: u64) -> Result<Simulation, String> {
    params.validate()?;
    let p = params;
    let mut rng = Rng::seed_from_u64(seed);
    let n_noise = p.n_noise();
    let n_pos = p.n_snv + n_noise;

    let tree = topology::simulate_topology(p.n_clones, &mut rng);
    let mut evolution = evolution::tree_profiles(&tree, n_pos, p, &mut rng)?;
    let alleles = hp::draw_alleles(n_pos, p.prop_snv_on_b, &mut rng);
    hp::relabel(&mut evolution, &alleles);

    let sample = sequencing::simulate_sample(&tree, p.min_tumour_purity, p.max_tumour_purity, &mut rng);
    let mut snv_edge = vec![(0, 0); n_pos];
    for (&edge, positions) in tree.edges.iter().zip(&evolution.snv_edges) {
        for &pos in positions {
            snv_edge[pos] = edge;
        }
    }
    let mut rows = sequencing::make_sequencing_data(
        &evolution.total,
        &evolution.dcf,
        &sample,
        tree.root,
        &snv_edge,
        p.coverage,
        &mut rng,
    );
    let noise_clones = if p.fract_noise > 0.0 {
        noise::add_noise(&mut rows, n_noise, p.n_noise_clones, &mut rng)
    } else {
        Vec::new()
    };
    let hp = hp::split_counts(&rows, &evolution.total, &sample, &alleles, p, &mut rng);
    // base_error changes which allele a read shows; the observed alt count follows it.
    for (row, h) in rows.iter_mut().zip(&hp) {
        row.variant_reads = h.alt();
    }
    let loci = output::assign_loci(n_pos, &mut rng)?;

    let mut warnings = evolution.warnings.clone();
    // simulate.py:77-81: SNVs whose rounded TRUE_CCF is 0 are absent from the sample.
    let n_missing = rows.iter().filter(|r| np_round2(r.ccf) == 0.0).count();
    let prop_missing = n_missing as f64 / p.n_snv as f64;
    if prop_missing >= 0.01 {
        warnings.push(format!(
            "WARNING: Due to sampling of clones and mutation removal, {} of mutations are not present at all in samples",
            py_float(prop_missing)
        ));
    }
    Ok(Simulation { params: p.clone(), seed, tree, evolution, alleles, sample, rows, hp, loci, noise_clones, warnings })
}
