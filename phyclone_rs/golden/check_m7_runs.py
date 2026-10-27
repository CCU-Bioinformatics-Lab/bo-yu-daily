"""Properties of the M7 reference runs that a port can check on its own traces, too.

  thin       e0_thin5 holds exactly iterations 0, 5, 10, ... of e0_base_bin, tree for tree and
             value for value: --thin only decides what is stored, it draws no random numbers
  alpha      e0_alpha25_fixed stores alpha = 2.5 in every sample
  max-time   e0_maxtime0 (--max-time 0) stores one sample, iteration 0
  chains     e0_chains4 has 4 chains of 200 samples; sample for sample it equals the V3 baseline
             chains4 seed 1 (same argv) when that run exists. The h5 files differ there in node
             labels and tree storage of chains 1-3, so the comparison is at sample level
  outliers   number of samples with >= 1 outlier, and the largest outlier count, per run

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
    phyclone_rs/golden/check_m7_runs.py
"""
import os
import sys

import numpy as np

G = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(G), "v3"))
from trace_io import read_h5  # noqa: E402


RUNS = os.path.join(G, "runs")
V3_CHAINS4 = os.path.join(os.path.dirname(G), "v3", "baseline", "runs", "chains4", "e0_base_bin",
                          "seed01", "trace.h5")


def trace(run):
    return read_h5(os.path.join(RUNS, run, "trace.h5"))


def rows(tr):
    return [(int(tr.chain[i]), int(tr.iter[i]), float(tr.alpha[i]), float(tr.log_p_one[i]),
             int(tr.num_nodes[i]), int(tr.num_roots[i]), tr.trees[tr.tree_idx[i]])
            for i in range(len(tr))]


def main():
    ok = True

    def report(name, cond, detail):
        nonlocal ok
        ok &= bool(cond)
        print(f"{name}\t{'OK' if cond else 'FAIL'}\t{detail}")

    base, thin = rows(trace("e0_base_bin")), rows(trace("e0_thin5"))
    report("thin", thin == [r for r in base if r[1] % 5 == 0],
           f"{len(thin)} samples vs every 5th of {len(base)}")
    alphas = {r[2] for r in rows(trace("e0_alpha25_fixed"))}
    report("alpha", alphas == {2.5}, f"alphas {sorted(alphas)}")
    mt = rows(trace("e0_maxtime0"))
    report("max-time", len(mt) == 1 and mt[0][1] == 0, f"{len(mt)} sample(s), iters {[r[1] for r in mt]}")
    c4 = rows(trace("e0_chains4"))
    per_chain = {c: sum(r[0] == c for r in c4) for c in sorted({r[0] for r in c4})}
    report("chains", per_chain == {0: 200, 1: 200, 2: 200, 3: 200}, f"samples per chain {per_chain}")
    if os.path.exists(V3_CHAINS4):
        v3 = rows(read_h5(V3_CHAINS4))
        report("chains=v3", c4 == v3, f"{len(c4)} samples (chain, iter, alpha, log_p_one, counts, "
                                      f"canonical tree) vs v3 chains4 seed01")
    for run in ("e0_out001", "e0_out001_boot", "e0_out001_fully", "real_a2_err004_out001",
                "fscrp_out", "fscrp_assign_loss", "fscrp_user_loss"):
        tr = trace(run)
        n_out = np.array([sum(n < 0 for n in tr.trees[k].node_of) for k in tr.tree_idx])
        print(f"outliers\t{run}\t{np.sum(n_out > 0)}/{len(n_out)} samples with outliers, "
              f"max {n_out.max()} of {len(tr.mutations)} mutations")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
