"""How heavy is the C4 pair term? Two diagnostics on a sim with a finished run without C4.

  1. Scale: over all posterior samples of RUN_DIR (a run without C4; each topology weighted by
     its count), the 5-95% range and SD of the base log_p (topology_report.tsv) against those of
     the C4 pair term of the same trees. Pair term >> base means the pair term alone sets the
     posterior.
  2. Read reuse: eligible pairs treat each pair as independent, but a read that covers m SNVs
     sits in up to m(m-1)/2 pairs. Counts tagged reads (truth/reads.tsv.gz: start, end, tagged,
     obs_hp, all observable) that span each eligible pair on its HP: pair-read incidences
     against unique reads. mean = incidences / unique reads is the composite-likelihood
     reuse factor; 1 / mean is the weight of C4_COMPOSITE_WEIGHT_PLAN.md.

Usage: python tools/c4_pair_weight_diagnostics.py SIM_DIR [SIM_DIR ...] [--run run_base]
       [--eps 0.01]
"""
import argparse
import csv
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c4_posthoc as C  # noqa: E402


def weighted(x, w):
    """(5-95% range, SD) of x with integer weights w."""
    v = np.repeat(np.asarray(x, float), np.asarray(w, int))
    lo, hi = np.percentile(v, [5, 95])
    return hi - lo, v.std()


def scale(sim, run, eps):
    table, _ = C.eligible_pairs(f"{sim}/input", eps)
    count, tables, trees, _ = C.load_run(f"{sim}/{run}")
    log_p = pd.read_csv(f"{sim}/{run}/topology_report.tsv", sep="\t").set_index("topology_id").log_p
    ids = list(count)
    term = [table.term(*C.assignment(tables[t], trees[t])) for t in ids]
    w = [count[t] for t in ids]
    (br, bs), (pr, ps) = weighted(log_p.reindex(ids), w), weighted(term, w)
    return {"base_range": br, "base_sd": bs, "pair_range": pr, "pair_sd": ps}


def reuse(sim, eps):
    _, pairs = C.eligible_pairs(f"{sim}/input", eps)
    with open(f"{sim}/truth/truth.tsv") as fh:
        pos = {r["mutation_id"]: (r["segment"], int(r["pos"])) for r in csv.DictReader(fh, delimiter="\t")}
    reads = pd.read_csv(f"{sim}/truth/reads.tsv.gz", sep="\t")
    reads = reads[reads.tagged == 1]
    per_read = {}
    for r in pairs.itertuples():
        (seg, pi), (_, pj) = pos[r.mutation_i], pos[r.mutation_j]
        sel = reads[(reads.segment == seg) & (reads.obs_hp == r.hap) &
                    (reads.start <= min(pi, pj)) & (reads.end > max(pi, pj))]
        for x in sel.read_id:
            per_read[x] = per_read.get(x, 0) + 1
    v = np.array(list(per_read.values()))
    return {"pairs": len(pairs), "incidences": int(v.sum()), "callable_sum":
            int(pairs.callable_pair_reads.sum()), "unique_reads": len(v),
            "pairs_per_read_mean": v.mean(), "pairs_per_read_max": int(v.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sims", nargs="+")
    ap.add_argument("--run", default="run_base")
    ap.add_argument("--eps", type=float, default=0.01)
    a = ap.parse_args()
    cols = ["base_range", "base_sd", "pair_range", "pair_sd", "pairs", "incidences",
            "callable_sum", "unique_reads", "pairs_per_read_mean", "pairs_per_read_max"]
    print("\t".join(["sim"] + cols))
    for sim in a.sims:
        r = {**scale(sim, a.run, a.eps), **reuse(sim, a.eps)}
        print("\t".join([os.path.basename(sim.rstrip("/"))] +
                        [f"{r[c]:.2f}" if isinstance(r[c], float) else str(r[c]) for c in cols]))


if __name__ == "__main__":
    main()
