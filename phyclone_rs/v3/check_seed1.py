"""Seed-1 reproduction: baseline/runs/ref/<run>/seed01 must equal golden/runs/<run>/trace.h5.

Compares, per sample in (chain, iter) order: alpha, log_p_one, num_nodes, num_roots bit for bit,
and the tree (mutation -> node, node -> parent, canonical labels). Prints one row per run.
Usage: env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
         phyclone_rs/v3/check_seed1.py
"""
import os
import sys

import numpy as np

V3 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, V3)
import summaries as S  # noqa: E402
from trace_io import read_trace  # noqa: E402


def main():
    bad = 0
    for run in S.config_case():
        new = os.path.join(V3, "baseline", "runs", "ref", run, "seed01", "trace.h5")
        if not os.path.exists(new):
            print(f"{run}\tmissing")
            bad += 1
            continue
        a = read_trace(os.path.join(S.GOLDEN, "runs", run, "trace.h5"))
        b = read_trace(new)
        same = (len(a) == len(b) and a.mutations == b.mutations
                and all(np.array_equal(getattr(a, f), getattr(b, f))
                        for f in ("chain", "iter", "alpha", "log_p_one", "num_nodes", "num_roots"))
                and all(a.trees[i] == b.trees[j] for i, j in zip(a.tree_idx, b.tree_idx)))
        bad += not same
        print(f"{run}\tsamples={len(a)}\tunique_trees={len(a.trees)}\t{'identical' if same else 'DIFFERENT'}")
    print("OK" if not bad else f"{bad} run(s) differ")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
