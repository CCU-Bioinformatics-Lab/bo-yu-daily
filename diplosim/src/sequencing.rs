//! sequencing.py for one bulk sample that holds every clone.
use std::collections::BTreeMap;

use rand::Rng as _;
use rand_distr::{Binomial, Dirichlet, Distribution, Gamma, Poisson};

use crate::evolution::{Genotype, Pos};
use crate::topology::{NodeId, Tree};
use crate::Rng;

/// One bulk sample: drawn purity and the fraction of cells from each clone, normal included.
#[derive(Clone, Debug)]
pub struct Sample {
    pub purity: f64,
    pub proportions: BTreeMap<NodeId, f64>,
}

/// One row of CONIPHER's variant_df (sequencing.py:134-146 plus the edge merge, simulate.py:157).
#[derive(Clone, Debug)]
pub struct VariantRow {
    pub pos: Pos,
    pub variant_reads: u64,
    pub total_reads: u64,
    pub true_vaf: f64,
    pub ccf: f64,
    pub dcf: f64,
    pub total_fract_cn: f64,
    pub fract_variant: f64,
    pub fract_a: f64,
    pub fract_b: f64,
    pub cn_prevalence: f64,
    pub purity: f64,
    pub parent: NodeId,
    pub child: NodeId,
    pub noise: bool,
}

impl VariantRow {
    /// `Est_VAF` (sequencing.py:145); NaN when there are no reads.
    pub fn est_vaf(&self) -> f64 {
        self.variant_reads as f64 / self.total_reads as f64
    }
}

pub fn poisson(rng: &mut Rng, lambda: f64) -> u64 {
    if lambda > 0.0 {
        Poisson::new(lambda).unwrap().sample(rng) as u64
    } else {
        0
    }
}

pub fn binomial(rng: &mut Rng, n: u64, p: f64) -> u64 {
    let p = if p.is_nan() { 0.0 } else { p.clamp(0.0, 1.0) };
    Binomial::new(n, p).unwrap().sample(rng)
}

/// sequencing.py:51 all_samples + :28 simulate_sample_leaves with n_samples = 1 and every
/// non-root clone present: purity ~ U(min, max); clones ~ Dirichlet(1, ..., 1) * purity.
pub fn simulate_sample(tree: &Tree, min_purity: f64, max_purity: f64, rng: &mut Rng) -> Sample {
    let purity = min_purity + (max_purity - min_purity) * rng.gen::<f64>();
    let clones: Vec<NodeId> = tree.nodes.iter().copied().filter(|&n| n != tree.root).collect();
    let weights: Vec<f64> = Dirichlet::new(&vec![1.0; clones.len()]).unwrap().sample(rng);
    let mut proportions: BTreeMap<NodeId, f64> =
        clones.into_iter().zip(weights).map(|(c, w)| (c, w * purity)).collect();
    proportions.insert(tree.root, 1.0 - purity);
    Sample { purity, proportions }
}

/// Per-position values of calculate_vaf (sequencing.py:66), calculate_ccf (:107) and
/// calculate_dcf (:115).
struct Expected {
    fract_copy_num: f64,
    vaf: f64,
    fract_variant: f64,
    fract_a: f64,
    fract_b: f64,
    cn_prevalence: f64,
    ccf: f64,
    dcf: f64,
}

fn expected(
    pos: Pos,
    total: &BTreeMap<NodeId, Vec<Genotype>>,
    dcf_profiles: &BTreeMap<NodeId, Vec<Genotype>>,
    sample: &Sample,
    root: NodeId,
) -> Expected {
    let mut e = Expected {
        fract_copy_num: 0.0,
        vaf: 0.0,
        fract_variant: 0.0,
        fract_a: 0.0,
        fract_b: 0.0,
        cn_prevalence: 0.0,
        ccf: 0.0,
        dcf: 0.0,
    };
    let mut fract_variant_cn = 0.0;
    let mut normalisation = 0.0;
    for (&clone, &p) in &sample.proportions {
        let g = total[&clone][pos];
        let d = dcf_profiles[&clone][pos];
        assert!(g.mutated <= d.mutated, "total mutated copies exceed DCF ones (sequencing.py:118)");
        e.fract_copy_num += f64::from(g.a + g.b) * p;
        if clone != root {
            fract_variant_cn += f64::from(g.mutated) * p;
            e.fract_a += f64::from(g.a) * p;
            e.fract_b += f64::from(g.b) * p;
        }
        if g.mutated > 0 {
            normalisation += p;
            e.ccf += p;
        }
        if d.mutated > 0 {
            e.dcf += p;
        }
        if g.a != 1 || g.b != 1 {
            e.cn_prevalence += p;
        }
    }
    e.fract_variant = if normalisation != 0.0 { fract_variant_cn / normalisation } else { 0.0 };
    e.vaf = fract_variant_cn / e.fract_copy_num;
    e.fract_a /= sample.purity;
    e.fract_b /= sample.purity;
    e.ccf /= sample.purity;
    e.dcf /= sample.purity;
    e
}

/// sequencing.py:7 make_sequencing_data, then the edge merge (simulate.py:157). `snv_edge`
/// gives each position's (parent, child).
pub fn make_sequencing_data(
    total: &BTreeMap<NodeId, Vec<Genotype>>,
    dcf_profiles: &BTreeMap<NodeId, Vec<Genotype>>,
    sample: &Sample,
    root: NodeId,
    snv_edge: &[(NodeId, NodeId)],
    coverage: f64,
    depth_dispersion: Option<f64>,
    rng: &mut Rng,
) -> Vec<VariantRow> {
    let exp: Vec<Expected> =
        (0..snv_edge.len()).map(|pos| expected(pos, total, dcf_profiles, sample, root)).collect();
    // get_total_reads (sequencing.py:95): depth ~ Poisson(coverage * cn / mean cn). diplosim
    // (DECISIONS 2026-10-31): with depth_dispersion phi the Poisson mean is first scaled by a
    // per-site Gamma(1/phi, phi) factor (mean 1, variance phi), so depth ~ negative binomial.
    let fbar = exp.iter().map(|e| e.fract_copy_num).sum::<f64>() / exp.len() as f64;
    exp.into_iter()
        .enumerate()
        .map(|(pos, e)| {
            let mut lambda = e.fract_copy_num * (coverage / fbar);
            if let Some(phi) = depth_dispersion {
                lambda *= Gamma::new(1.0 / phi, phi).unwrap().sample(rng);
            }
            let total_reads = poisson(rng, lambda);
            let variant_reads = binomial(rng, total_reads, e.vaf);
            VariantRow {
                pos,
                variant_reads,
                total_reads,
                true_vaf: e.vaf,
                ccf: e.ccf,
                dcf: e.dcf,
                total_fract_cn: e.fract_copy_num,
                fract_variant: e.fract_variant,
                fract_a: e.fract_a,
                fract_b: e.fract_b,
                cn_prevalence: e.cn_prevalence,
                purity: sample.purity,
                parent: snv_edge[pos].0,
                child: snv_edge[pos].1,
                noise: false,
            }
        })
        .collect()
}
