"""Run PhyClone with an HP-aware per-SNV emission (layers A1 / A2 of
research/phyclone_research/HP_EXTENSION_DESIGN.md), without editing the submodule.

PhyClone turns each SNV into a (samples x CCF grid) log-likelihood table and never looks at
the counts again (phyclone/data/base.py, phyclone/tree/tree_node.py). This wrapper swaps the
loader that builds those tables (phyclone.run.load_data) and then calls the normal CLI, so
trees, SMC/PG, the trace, map and topology-report are all unchanged.

Emission per SNV x sample (SNV on HP h, other HP o, tumour content t, CCF f):
  three cell groups as in PhyClone: normal (1 copy per HP), tumour without the SNV, tumour with
  m mutated copies on h. Phased reads on h:  alt_h ~ Bin(n_h, t*mutated_copies / HP-h copies);
  unphased reads use the same numerator over copies of both HPs. Reads on o carry no f signal.

  a1: every tumour cell has the segment's dominant HP CN (cn_hp1, cn_hp2); m in 1..cn_h.
      If cn_h = 0 (the SNV's HP is absent in the dominant state) cn_h is raised to 1.
  a2: segments.tsv gives ancestral state A, other state B and phi (tumour fraction in B).
      Mixture over how the SNV cells (f) and the B cells (phi) relate:
        E1  B inside SNV cells (CN after SNV, f >= phi): mutated copies change with the CN
            event, including loss (m_B = 0)
        E2  SNV cells inside B (SNV after CN, f <= phi); m_B = 1, because a new SNV sits on
            one copy and no later CN event is modelled
        E3  disjoint branches (f + phi <= 1)
      Each feasible (scenario, multiplicity) combination gets equal prior weight within its
      scenario; scenarios get equal weight. CCF values no scenario allows are floored at
      INFEASIBLE_GAP below the SNV's worst feasible value (PhyClone cannot handle -inf).

Input: data_hp.tsv and segments.tsv from tools/hp_truth_tree_to_phyclone.py.

C4 (--pairs): adds the read co-occurrence tree term of tools/phyclone_pairs.py to every tree
score, with any emission (--hp-mode base keeps PhyClone's own loader and data.tsv).

Usage:
  python tools/phyclone_hp.py --hp-mode a2 --segments SEG.tsv run -i data_hp.tsv -o trace.h5 ...
  python tools/phyclone_hp.py --hp-mode base --pairs PAIRS.tsv --hp-data data_hp.tsv \
      --segments SEG.tsv run -i data.tsv -o trace.h5 ...
  (everything after the wrapper options goes to `phyclone`; only `run` is patched, so map and
   topology-report can be called through this wrapper or the normal CLI)
"""
import argparse
import sys

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import binom

ERR = 1e-3  # same role as PhyClone's default error_rate
INFEASIBLE_GAP = 10.0  # log-units below the worst feasible grid value


def scenarios(f, phi, a_h, a_o, b_h, b_o):
    """Yield (log_weight, mutA, mutB, nomutA, nomutB, m_A, m_B) over the CCF grid f.

    Fractions are of tumour cells; mutA/mutB = SNV cells in state A/B. Infeasible grid points
    get NaN fractions and are masked by the caller.
    """
    combos = []
    if phi <= 0 or (a_h, a_o) == (b_h, b_o):
        h = max(a_h, 1)
        combos.append(("E0", [(m, 0) for m in range(1, h + 1)],
                       (f, 0 * f, 1 - f, 0 * f), h, h))
    else:
        nan = np.full_like(f, np.nan)
        # E1: B cells inside SNV cells
        ok = f >= phi
        pairs = []
        for m_a in range(1, a_h + 1):
            for m_b in transitions(a_h, m_a, b_h):
                pairs.append((m_a, m_b))
        if pairs:
            combos.append(("E1", pairs, (np.where(ok, f - phi, nan), np.where(ok, phi, nan),
                                         np.where(ok, 1 - f, nan), np.where(ok, 0.0, nan)),
                           a_h, b_h))
        # E2: SNV cells inside B cells; the SNV arises after the CN event, on one copy
        ok = f <= phi
        if b_h >= 1:
            combos.append(("E2", [(0, 1)],
                           (np.where(ok, 0.0, nan), np.where(ok, f, nan),
                            np.where(ok, 1 - phi, nan), np.where(ok, phi - f, nan)), a_h, b_h))
        # E3: disjoint
        ok = f + phi <= 1 + 1e-12
        if a_h >= 1:
            combos.append(("E3", [(m, 0) for m in range(1, a_h + 1)],
                           (np.where(ok, f, nan), np.where(ok, 0.0, nan),
                            np.where(ok, 1 - f - phi, nan), np.where(ok, phi, nan)), a_h, b_h))
    log_w_scen = -np.log(len(combos))
    for _, pairs, fr, _, _ in combos:
        for m_a, m_b in pairs:
            yield (log_w_scen - np.log(len(pairs)), *fr, m_a, m_b)


def transitions(a_h, m_a, b_h):
    """Mutated copies on h after the h-copy number goes a_h -> b_h, given m_a mutated before."""
    d = b_h - a_h
    if d >= 0:  # gained copies duplicate mutated or unmutated copies
        lo = d if m_a == a_h else 0
        hi = 0 if m_a == 0 else d
        return [m_a + k for k in range(lo, hi + 1)]
    lost = -d  # lost copies come from mutated or unmutated copies
    return [m_a - k for k in range(max(0, lost - (a_h - m_a)), min(lost, m_a) + 1)]


def snv_grid(row, seg, mode, f):
    """Log-likelihood over the CCF grid. An SNV with no HP-tagged alt read (snv_hp ".") has an
    unknown HP: average the likelihood over the HPs on which it is feasible."""
    hps = [row.snv_hp] if row.snv_hp in ("HP1", "HP2") else ["HP1", "HP2"]
    grids = [g for g in (hp_grid(row, seg, mode, f, hp) for hp in hps) if g is not None]
    out = logsumexp(np.vstack(grids), axis=0) - np.log(len(grids))
    # CCF values no scenario allows (e.g. 1-phi < f < phi when the SNV's HP is lost in B) are
    # -inf; PhyClone's convolution and Gibbs-MH turn -inf into NaN, so floor them just below
    # the worst feasible value of this SNV.
    finite = np.isfinite(out)
    out[~finite] = out[finite].min() - INFEASIBLE_GAP
    return out


def hp_grid(row, seg, mode, f, hp):
    """Log-likelihood over f with the SNV on hp, or None if no scenario allows it."""
    t = row.tumour_content
    h, o = ("hp1", "hp2") if hp == "HP1" else ("hp2", "hp1")
    n_h = getattr(row, f"ref_{h}") + getattr(row, f"alt_{h}")
    k_h = getattr(row, f"alt_{h}")
    n_u = row.ref_unphased + row.alt_unphased
    k_u = row.alt_unphased
    if mode == "a1":
        a_h, a_o = getattr(row, f"cn_{h}"), getattr(row, f"cn_{o}")
        b_h, b_o, phi = a_h, a_o, 0.0
    else:
        a_h, a_o = seg[f"a_{h}"], seg[f"a_{o}"]
        b_h, b_o, phi = seg[f"b_{h}"], seg[f"b_{o}"], seg["phi"]
    if mode == "a1" or phi <= 0:
        a_h = max(a_h, 1)
        b_h = max(b_h, 1)
    in_a, in_b = 1 - phi, phi
    den_h = (1 - t) + t * (in_a * a_h + in_b * b_h)
    den_u = 2 * (1 - t) + t * (in_a * (a_h + a_o) + in_b * (b_h + b_o))
    terms = []
    for log_w, mut_a, mut_b, _, _, m_a, m_b in scenarios(f, phi, a_h, a_o, b_h, b_o):
        num = t * (mut_a * m_a + mut_b * m_b)
        ll = np.full_like(f, -np.inf)
        ok = ~np.isnan(num)
        vh = np.clip(num[ok] / den_h, ERR, 1 - ERR)
        vu = np.clip(num[ok] / den_u, ERR, 1 - ERR)
        ll[ok] = binom.logpmf(k_h, n_h, vh) + binom.logpmf(k_u, n_u, vu)
        terms.append(log_w + ll)
    return logsumexp(np.vstack(terms), axis=0) if terms else None


def make_loader(mode, segments_file):
    from phyclone.data.base import DataPoint
    from phyclone.data.pyclone import compute_outlier_prob

    segs = None
    if mode == "a2":
        sdf = pd.read_csv(segments_file, sep="\t")
        segs = {(r.segment_id, r.sample_id): r._asdict() for r in sdf.itertuples(index=False)}

    def load_data(file_name, rng, high_loss_prob, assign_loss_prob, user_provided_loss_prob,
                  cluster_file=None, density="beta-binomial", grid_size=101, outlier_prob=1e-4,
                  precision=400, min_clust_size=4):
        if cluster_file is not None:
            raise SystemExit("phyclone_hp: a cluster file is not supported")
        if density != "binomial":
            raise SystemExit("phyclone_hp: only -d binomial is implemented")
        df = pd.read_csv(file_name, sep="\t")
        samples = sorted(df["sample_id"].unique())
        f = np.linspace(0, 1, grid_size)  # same grid as PyCloneDataPoint.get_ccf_grid
        out_is, out_not = compute_outlier_prob(outlier_prob, 1)
        data = []
        for idx, (mut, grp) in enumerate(df.groupby("mutation_id", sort=True)):
            grp = grp.set_index("sample_id").loc[samples]
            val = np.vstack([
                snv_grid(r, segs[(r.segment_id, sm)] if segs else None, mode, f)
                for sm, r in zip(samples, grp.itertuples(index=False))
            ])
            data.append(DataPoint(idx, val, name=mut, outlier_prob=out_is, outlier_prob_not=out_not))
        print(f"phyclone_hp: {len(data)} mutations, {len(samples)} samples, emission = {mode}")
        return data, samples, None

    return load_data


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--hp-mode", choices=["base", "a1", "a2"], required=True)
    ap.add_argument("--segments")
    ap.add_argument("--pairs", help="pairs.tsv: add the C4 read co-occurrence tree term")
    ap.add_argument("--hp-data", help="data_hp.tsv with observed snv_hp (needed with --pairs)")
    ap.add_argument("--pair-eps", type=float, default=0.01)
    opts, rest = ap.parse_known_args()
    if opts.hp_mode == "a2" and not opts.segments:
        raise SystemExit("--hp-mode a2 needs --segments")
    if opts.pairs and not (opts.segments and opts.hp_data):
        raise SystemExit("--pairs needs --segments and --hp-data")

    import phyclone.run
    from phyclone.cli import main as cli_main

    if opts.hp_mode != "base":
        phyclone.run.load_data = make_loader(opts.hp_mode, opts.segments)
    if opts.pairs:
        import phyclone_pairs

        table = phyclone_pairs.install_everywhere(opts.pairs, opts.hp_data, opts.segments,
                                                  opts.pair_eps)
        print(f"phyclone_hp: C4 pair term on, {len(table)} eligible pairs, eps = {opts.pair_eps}")
    cli_main(args=rest)


if __name__ == "__main__":
    main()
