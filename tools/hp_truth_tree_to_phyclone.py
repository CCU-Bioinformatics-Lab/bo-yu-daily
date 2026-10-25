"""Turn the designed HP-aware truth tree (tools/draw_hp_truth_tree.py) into PhyClone input.

Each of the 10 SNV roles (s1..s10) is replicated N times at distinct positions in the same
segment, so every role has the same CN history and the same expected VAF. Counts are drawn
with the same model as the figure: DP ~ Poisson(depth * meanCN / 2), alt ~ Binomial(DP, VAF).
major/minor = the tumour CN state with the most cells (what a bulk caller would report).

Writes to OUT_DIR:
  data.tsv     PhyClone input (8 columns, no truth)
  truth.tsv    per mutation: role, origin clone, HP, segment, origin CCF, carrier fraction,
               noise-free PhyClone-likelihood CCF estimate
  clusters_truth.tsv  mutation_id -> origin clone (for a truth-cluster run)
  truth_tree.tsv      clone -> parent, CCF (per sample)
  data_hp.tsv  data.tsv + HP columns for the A1/A2 emission (tools/phyclone_hp.py):
               snv_hp, segment_id, cn_hp1, cn_hp2 (dominant state), ref/alt_hp1, ref/alt_hp2,
               ref/alt_unphased. Totals equal data.tsv; phased alt reads all carry the SNV's HP,
               phased ref reads split by ref copies per HP. A separate RNG draws the split,
               so data.tsv stays the same as without HP output.
  segments.tsv per segment x sample: ancestral state A (= C1), other state B, phi = fraction
               of tumour cells in B (true value; --phi-noise adds Gaussian noise)

With --two-sample, a second sample S2 is added with other clone proportions and purity
(SAMPLES below). The tree, CN and SNV-to-HP truth stay the same; only the cell mix changes.
In S2, C3 (0.40) > C4 (0.10), so a tree with C3 under C4 breaks the CCF sum rule.

With --tree typical, the typical control tree (tools/typical_truth_tree.py) is used instead.
Its roles have their own SNV counts (N_SNV), so --per-role is ignored; --two-sample is not
supported for it.

Usage: python3 tools/hp_truth_tree_to_phyclone.py OUT_DIR [--per-role 10] [--depth 200] [--seed 1]
                                                   [--two-sample] [--phased 0.85] [--phi-noise 0]
                                                   [--tree stress|typical]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_hp_truth_tree as T  # noqa: E402

# sample -> (fraction of tumour cells per clone, purity); S1 is the figure's sample
SAMPLES = {
    "S1": (dict(T.PROP), T.PURITY),
    "S2": ({"C1": 0.30, "C2": 0.20, "C3": 0.40, "C4": 0.10}, 0.60),
}


def set_sample(name):
    """Point the truth module at one sample's cell mix (its helpers read these globals)."""
    prop, purity = SAMPLES[name]
    T.PROP, T.PURITY = dict(prop), purity
    T.CELL = {"N": 1 - purity, **{c: purity * p for c, p in prop.items()}}


def hp_cn(clone, seg):
    return T.copies(clone, seg, "HP1"), T.copies(clone, seg, "HP2")


def dominant_hp_cn(seg):
    """(HP1, HP2) CN of the tumour state with the most cells; HP-aware version of dominant_cn."""
    w = {}
    for c, p in T.PROP.items():
        w[hp_cn(c, seg)] = w.get(hp_cn(c, seg), 0) + p
    return max(w, key=w.get)


def segment_states(seg):
    """Ancestral state A (truncal clone C1), the other tumour state B, and phi = its fraction."""
    a = hp_cn("C1", seg)
    others = {hp_cn(c, seg) for c in T.PROP} - {a}
    assert len(others) <= 1, f"segment {seg} has more than two tumour CN states"
    b = others.pop() if others else a
    phi = sum(p for c, p in T.PROP.items() if hp_cn(c, seg) == b) if b != a else 0.0
    return a, b, phi


def hp_split(rng, s, ref, alt, alt_copies, hp_tot, dom, phased):
    """HP columns for one SNV x sample, consistent with the total ref/alt counts."""
    hp = T.SNV[s][1]
    other = "HP2" if hp == "HP1" else "HP1"
    a_ph = rng.binomial(alt, phased)
    r_ph = rng.binomial(ref, phased)
    ref_hp_copies = hp_tot[hp] - alt_copies
    r_h = rng.binomial(r_ph, ref_hp_copies / (ref_hp_copies + hp_tot[other]))
    cnt = {hp: (r_h, a_ph), other: (r_ph - r_h, 0)}
    return "\t".join(map(str, [hp, T.SNV[s][2], dom[0], dom[1], *cnt["HP1"], *cnt["HP2"],
                                ref - r_ph, alt - a_ph]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--per-role", type=int, default=10)
    ap.add_argument("--depth", type=float, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--two-sample", action="store_true")
    ap.add_argument("--phased", type=float, default=0.85, help="fraction of reads with an HP tag")
    ap.add_argument("--phi-noise", type=float, default=0.0, help="SD of Gaussian noise on phi")
    ap.add_argument("--tree", choices=["stress", "typical"], default="stress")
    a = ap.parse_args()
    if a.tree == "typical":
        if a.two_sample:
            ap.error("--two-sample is only defined for the stress tree")
        import typical_truth_tree
        typical_truth_tree.install(T)
        SAMPLES["S1"] = (dict(T.PROP), T.PURITY)
    n_snv = getattr(T, "N_SNV", {})
    os.makedirs(a.out_dir, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    rng_hp = np.random.default_rng([a.seed, 1])  # HP split and phi noise only

    samples = ["S1", "S2"] if a.two_sample else ["S1"]
    data, truth, clus, data_hp = [], [], [], []
    for s, (org, hp, seg) in T.SNV.items():
        per_sample = {}
        for sm in samples:
            set_sample(sm)
            tot, alt, _ = T.snv_truth(s)
            maj, mnr = T.dominant_cn(seg)
            f_exp = T.phyclone_ccf(*T.expected_counts(s, a.depth), maj, mnr, T.PURITY)
            _, _, hp_tot = T.snv_truth(s)
            dom = dominant_hp_cn(seg)
            per_sample[sm] = (tot, alt, maj, mnr, T.PURITY, hp_tot, dom,
                              f"{T.ccf(org):.3f}\t{T.carrier_fraction(s):.3f}\t{f_exp:.3f}\t"
                              f"{alt / tot:.4f}")
        for i in range(n_snv.get(s, a.per_role)):
            mid = f"{s}_{i:02d}"
            for sm, (tot, alt, maj, mnr, pur, hp_tot, dom, _) in per_sample.items():
                dp = rng.poisson(a.depth * tot / 2)
                k = rng.binomial(dp, alt / tot)
                row = f"{mid}\t{sm}\t{dp - k}\t{k}\t{maj}\t{mnr}\t2\t{pur}"
                data.append(row)
                data_hp.append(row + "\t" + hp_split(rng_hp, s, dp - k, k, alt, hp_tot, dom,
                                                      a.phased))
            truth.append(f"{mid}\t{s}\t{org}\t{hp}\t{seg}\t" +
                         "\t".join(v[-1] for v in per_sample.values()))
            clus.append(f"{mid}\t{org}")

    def write(name, header, rows):
        with open(os.path.join(a.out_dir, name), "w") as fh:
            fh.write(header + "\n" + "\n".join(rows) + "\n")

    base_cols = ("mutation_id\tsample_id\tref_counts\talt_counts\tmajor_cn\tminor_cn\t"
                 "normal_cn\ttumour_content")
    write("data.tsv", base_cols, data)
    write("data_hp.tsv", base_cols + "\tsnv_hp\tsegment_id\tcn_hp1\tcn_hp2\tref_hp1\talt_hp1\t"
          "ref_hp2\talt_hp2\tref_unphased\talt_unphased", data_hp)
    seg_rows = []
    for sm in samples:
        set_sample(sm)
        for seg in T.SEGS:
            (a1, a2), (b1, b2), phi = segment_states(seg)
            if a.phi_noise > 0 and phi > 0:
                phi = float(np.clip(phi + rng_hp.normal(0, a.phi_noise), 0.01, 0.99))
            seg_rows.append(f"{seg}\t{sm}\t{a1}\t{a2}\t{b1}\t{b2}\t{phi:.4f}")
    write("segments.tsv", "segment_id\tsample_id\ta_hp1\ta_hp2\tb_hp1\tb_hp2\tphi", seg_rows)
    per = ["origin_ccf", "carrier_fraction", "phyclone_ccf_expected", "vaf_expected"]
    # first sample keeps the plain column names; later samples get a _<sample> suffix
    cols = per + [f"{c}_{sm}" for sm in samples[1:] for c in per]
    write("truth.tsv", "mutation_id\trole\torigin_clone\thp\tsegment\t" + "\t".join(cols), truth)
    write("clusters_truth.tsv", "mutation_id\tcluster_id", clus)
    parent = {k: p for p, ks in T.CHILDREN.items() for k in ks}
    rows = []
    for sm in samples:
        set_sample(sm)
        rows += [f"{c}\t{parent.get(c, 'root')}\t{sm}\t{T.PURITY}\t{T.PROP[c]:.2f}\t{T.ccf(c):.2f}"
                 for c in T.PROP]
    write("truth_tree.tsv", "clone\tparent\tsample_id\tpurity\tclone_fraction\tccf", rows)


if __name__ == "__main__":
    main()
