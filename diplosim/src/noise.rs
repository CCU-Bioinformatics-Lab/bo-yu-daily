//! noise.py: move some SNVs to fake clusters off the tree and redraw their alt counts.
use rand::seq::SliceRandom;
use rand::Rng as _;

use crate::sequencing::{binomial, VariantRow};
use crate::topology::NodeId;
use crate::Rng;

/// noise.py:5 add_noise for one sample. Returns the fake cluster labels.
pub fn add_noise(rows: &mut [VariantRow], n_noise: usize, n_noise_clones: usize, rng: &mut Rng) -> Vec<NodeId> {
    let positions: Vec<usize> = (0..rows.len()).collect();
    let mut shuffled = positions.clone();
    let noise_rows = shuffled.partial_shuffle(rng, n_noise).0.to_vec();
    let max_clone = rows.iter().map(|r| r.parent.max(r.child)).max().unwrap_or(0);
    let noisy_clones: Vec<NodeId> = (1..=n_noise_clones as NodeId).map(|i| max_clone + i).collect();
    let ccfs: Vec<f64> = noisy_clones.iter().map(|_| f64::from(rng.gen_range(1..100)) / 100.0).collect();
    let assign: Vec<usize> = positions.iter().map(|_| rng.gen_range(0..noisy_clones.len())).collect();

    for &i in &noise_rows {
        let r = &mut rows[i];
        r.noise = true;
        r.child = noisy_clones[assign[i]];
        r.ccf = ccfs[assign[i]];
        r.fract_variant = r.fract_variant.max(1.0);
    }
    // noise.py:17 recomputes True_VAF for every row, noise or not.
    for r in rows.iter_mut() {
        let vaf = r.fract_variant * r.ccf * r.purity / r.total_fract_cn;
        r.true_vaf = if vaf.is_nan() { vaf } else { vaf.min(1.0) };
    }
    for &i in &noise_rows {
        let r = &mut rows[i];
        r.variant_reads = binomial(rng, r.total_reads, r.true_vaf);
    }
    noisy_clones
}
