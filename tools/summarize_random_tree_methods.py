"""Paired comparison of PhyClone base / A1 / A2 on the same longbulksim random-tree simulations.

Reads DIR/per_sim.tsv (base), DIR/per_sim_a1.tsv, DIR/per_sim_a2.tsv from
tools/eval_random_tree_phyclone.py. For each metric: per-method median, and the paired
difference (method - base) as mean with a 95% bootstrap CI over simulations. Strata by the
number of detectable true clones (1 vs >= 2). Writes DIR/method_comparison.tsv and prints it.

Usage: python3 tools/summarize_random_tree_methods.py DIR [--boot 10000] [--seed 1]
"""
import argparse
import csv
import os

import numpy as np

METRICS = ["ari", "v_measure", "balanced_relation_acc", "ccf_mae", "clone_count_err"]
METHODS = {"base": "per_sim.tsv", "a1": "per_sim_a1.tsv", "a2": "per_sim_a2.tsv"}


def load(path):
    with open(path) as fh:
        rows = {r["sim"]: r for r in csv.DictReader(fh, delimiter="\t")}
    for r in rows.values():
        r["clone_count_err"] = abs(int(r["n_clones_inferred"]) - int(r["n_clones_detectable"]))
    return rows


def boot_ci(x, rng, n):
    idx = rng.integers(len(x), size=(n, len(x)))
    m = x[idx].mean(1)
    return np.quantile(m, [0.025, 0.975])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    runs = {m: load(os.path.join(a.dir, f)) for m, f in METHODS.items()
            if os.path.exists(os.path.join(a.dir, f))}
    sims = sorted(set.intersection(*(set(r) for r in runs.values())))
    base = runs["base"]
    strata = {"all": sims,
              "detectable=1": [s for s in sims if int(base[s]["n_clones_detectable"]) <= 1],
              "detectable>=2": [s for s in sims if int(base[s]["n_clones_detectable"]) >= 2]}
    rng = np.random.default_rng(a.seed)
    out = []
    for name, ss in strata.items():
        if not ss:
            continue
        for met in METRICS:
            val = {m: np.array([float(runs[m][s][met]) for s in ss]) for m in runs}
            row = [name, len(ss), met] + [f"{np.median(val[m]):.3f}" for m in runs]
            for m in runs:
                if m == "base":
                    continue
                d = val[m] - val["base"]
                lo, hi = boot_ci(d, rng, a.boot)
                row += [f"{d.mean():+.3f}", f"[{lo:+.3f}, {hi:+.3f}]"]
            out.append(row)
    head = ["stratum", "n_sims", "metric"] + [f"median_{m}" for m in runs]
    for m in runs:
        if m != "base":
            head += [f"diff_{m}_mean", f"diff_{m}_ci95"]
    with open(os.path.join(a.dir, "method_comparison.tsv"), "w") as fh:
        fh.write("\t".join(head) + "\n")
        fh.writelines("\t".join(map(str, r)) + "\n" for r in out)
    print("\t".join(head))
    for r in out:
        print("\t".join(map(str, r)))


if __name__ == "__main__":
    main()
