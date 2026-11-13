#!/usr/bin/env python3
"""Paired summary of tools/run_diplosim_haploclone_batch.py results (2026-11-12).

Rule set before the batch ran (lab_report/2026-11-12_diplosim_haploclone_hp_vs_base/README.md):
  per tree, average the haploclone seeds within each mode, then take A1 - base;
  report the mean difference over trees with a t 95% CI;
  "no difference" on pair_acc = the CI contains 0 and |mean| < 0.02.
Seed noise: |seed 1 - seed 2| within the same tree and mode.

Usage: python3 tools/summarize_diplosim_haploclone_batch.py RESULTS_TSV
"""
import csv
import statistics as st
import sys
from collections import defaultdict

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 19: 2.093, 24: 2.064, 29: 2.045}
MEASURES = ["pair_acc", "ari", "ccf_mae", "n_clones"]

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
by = defaultdict(list)
for r in rows:
    by[(r["sim_seed"], r["mode"])].append(r)
trees = sorted({r["sim_seed"] for r in rows}, key=int)

print("per tree (mean over haploclone seeds):")
print(f"{'tree':>5} {'purity':>6} {'true':>4} | " + " | ".join(f"{m:>17}" for m in MEASURES))
print(f"{'':>5} {'':>6} {'':>4} | " + " | ".join(f"{'base':>8} {'a1':>8}" for _ in MEASURES))
diffs = defaultdict(list)
for t in trees:
    cells = []
    for m in MEASURES:
        b = st.mean(float(r[m]) for r in by[(t, "base")])
        a = st.mean(float(r[m]) for r in by[(t, "a1")])
        diffs[m].append(a - b)
        cells.append(f"{b:8.3f} {a:8.3f}")
    r0 = by[(t, "base")][0]
    print(f"{t:>5} {float(r0['purity']):6.2f} {r0['true_clones']:>4} | " + " | ".join(cells))

print("\nA1 - base over trees (mean, t 95% CI):")
for m in MEASURES:
    d = diffs[m]
    mean = st.mean(d)
    half = T975.get(len(d) - 1, 1.96) * st.stdev(d) / len(d) ** 0.5 if len(d) > 1 else float("nan")
    wins = sum(x > 1e-9 for x in d), sum(x < -1e-9 for x in d)
    print(f"  {m:>8}: {mean:+.4f}  [{mean - half:+.4f}, {mean + half:+.4f}]   A1 higher {wins[0]}, lower {wins[1]}, tied {len(d) - sum(wins)}")

print("\nseed noise |seed a - seed b| within tree and mode (mean, max):")
for m in MEASURES:
    gaps = [abs(float(v[0][m]) - float(v[1][m])) for v in by.values() if len(v) >= 2]
    if gaps:
        print(f"  {m:>8}: mean {st.mean(gaps):.4f}, max {max(gaps):.4f}  (n {len(gaps)})")

d = diffs["pair_acc"]
mean = st.mean(d)
half = T975.get(len(d) - 1, 1.96) * st.stdev(d) / len(d) ** 0.5
verdict = "no difference" if (mean - half) <= 0 <= (mean + half) and abs(mean) < 0.02 else "difference or inconclusive"
print(f"\npre-set rule on pair_acc: {verdict}")
