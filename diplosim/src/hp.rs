//! diplosim extensions (新寫; DECISIONS 2026-10-30): which allele carries each SNV, and how the
//! CONIPHER read counts split into HP1 (allele A), HP2 (allele B) and HP0 (untagged).
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

/// Read counts per haplotag. Each `*_REF + *_ALT` summed over HP1, HP2 and HP0 gives CONIPHER's
/// REF_COUNT and VAR_COUNT.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct HpCounts {
    pub hp1_ref: u64,
    pub hp1_alt: u64,
    pub hp2_ref: u64,
    pub hp2_alt: u64,
    pub hp0_ref: u64,
    pub hp0_alt: u64,
}

/// Option ②: all alt reads go to the SNV's haplotype X. Ref reads split by the expected ref
/// molecules on each allele over the mixture: X carries F_X - M of them, the other allele O
/// carries F_O. Then every count loses Binomial(count, 1 - prop_tagged) reads to HP0.
pub fn split_counts(
    rows: &[VariantRow],
    total: &BTreeMap<NodeId, Vec<Genotype>>,
    sample: &Sample,
    alleles: &[Allele],
    prop_tagged: f64,
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
            // No ref-carrying copy anywhere: any ref reads (noise SNVs) favour neither allele.
            let p_other = if denom > 0.0 { f_o / denom } else { 0.5 };
            let ref_o = binomial(rng, ref_reads, p_other);
            let ref_x = ref_reads - ref_o;
            let (hp1_ref, hp1_alt, hp2_ref, hp2_alt) = match x {
                Allele::A => (ref_x, alt, ref_o, 0),
                Allele::B => (ref_o, 0, ref_x, alt),
            };
            let mut untag = |tagged: u64| {
                let moved = binomial(rng, tagged, 1.0 - prop_tagged);
                (tagged - moved, moved)
            };
            let (hp1_ref, r1) = untag(hp1_ref);
            let (hp1_alt, a1) = untag(hp1_alt);
            let (hp2_ref, r2) = untag(hp2_ref);
            let (hp2_alt, a2) = untag(hp2_alt);
            HpCounts { hp1_ref, hp1_alt, hp2_ref, hp2_alt, hp0_ref: r1 + r2, hp0_alt: a1 + a2 }
        })
        .collect()
}
