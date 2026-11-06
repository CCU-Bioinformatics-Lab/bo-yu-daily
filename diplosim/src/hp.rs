//! diplosim extensions (新寫; DECISIONS 2026-10-30): which allele carries each SNV, and how the
//! CONIPHER read counts split into HP1 (allele A) and HP2 (allele B).
use std::collections::BTreeMap;

use rand::Rng as _;

use crate::evolution::{Evolution, Genotype};
use crate::sequencing::{binomial, Sample, VariantRow};
use crate::topology::NodeId;
use crate::Rng;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Allele {
    A,
    B,
}

impl Allele {
    pub fn name(self) -> &'static str {
        match self {
            Allele::A => "A",
            Allele::B => "B",
        }
    }
}

/// Each position's SNV allele: B with probability `prop_snv_on_b`, independently.
pub fn draw_alleles(n_positions: usize, prop_snv_on_b: f64, rng: &mut Rng) -> Vec<Allele> {
    // One uniform per position for any prop, so a seed gives the same tree, depth and alt across
    // prop_snv_on_b values and only the allele labels change.
    (0..n_positions).map(|_| if rng.gen::<f64>() < prop_snv_on_b { Allele::B } else { Allele::A }).collect()
}

/// Symmetric relabel: at every B position swap A and B in all genotypes (total and DCF) and in
/// the event names. CONIPHER's event rules treat A and B symmetrically and each SNV has its own
/// position, so this equals simulating that SNV on B.
pub fn relabel(evo: &mut Evolution, alleles: &[Allele]) {
    for profiles in [&mut evo.total, &mut evo.dcf] {
        for profile in profiles.values_mut() {
            for (g, &al) in profile.iter_mut().zip(alleles) {
                if al == Allele::B {
                    *g = g.swapped();
                }
            }
        }
    }
    for by_pos in evo.events.values_mut() {
        for (&pos, list) in by_pos.iter_mut() {
            if alleles[pos] == Allele::B {
                list.iter_mut().for_each(|e| *e = e.mirrored());
            }
        }
    }
}

/// Read counts per haplotype. `*_REF` sums to REF_COUNT and `*_ALT` to VAR_COUNT.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct HpCounts {
    pub hp1_ref: u64,
    pub hp1_alt: u64,
    pub hp2_ref: u64,
    pub hp2_alt: u64,
}

/// Option ②: all alt reads go to the SNV's haplotype X. Ref reads split by the expected ref
/// molecules on each allele over the mixture: X carries F_X - M of them, the other allele O
/// carries F_O.
pub fn split_counts(
    rows: &[VariantRow],
    total: &BTreeMap<NodeId, Vec<Genotype>>,
    sample: &Sample,
    alleles: &[Allele],
    rng: &mut Rng,
) -> Vec<HpCounts> {
    rows.iter()
        .map(|row| {
            let x = alleles[row.pos];
            let (mut f_x, mut f_o, mut m) = (0.0, 0.0, 0.0);
            for (clone, &p) in &sample.proportions {
                let g = total[clone][row.pos];
                let (cn_x, cn_o) = match x {
                    Allele::A => (g.a, g.b),
                    Allele::B => (g.b, g.a),
                };
                f_x += p * f64::from(cn_x);
                f_o += p * f64::from(cn_o);
                m += p * f64::from(g.mutated);
            }
            let alt = row.variant_reads;
            let ref_reads = row.total_reads - alt;
            let denom = f_x - m + f_o;
            // No ref-carrying copy anywhere: the VAF is 1, so there are no ref reads to split.
            let p_other = if denom > 0.0 { f_o / denom } else { 0.5 };
            let ref_o = binomial(rng, ref_reads, p_other);
            let ref_x = ref_reads - ref_o;
            match x {
                Allele::A => HpCounts { hp1_ref: ref_x, hp1_alt: alt, hp2_ref: ref_o, hp2_alt: 0 },
                Allele::B => HpCounts { hp1_ref: ref_o, hp1_alt: 0, hp2_ref: ref_x, hp2_alt: alt },
            }
        })
        .collect()
}
