#!/usr/bin/env python3
"""LOH proxy (minor HP depth < 0.1) before / after masking the Ig loci, against the diplosim 95% band.
Usage: python3 tools/plot_mask_ig_loh.py  (writes lab_report/2026-11-03_diplosim_mask_ig_loci/loh_mask.png)"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1] / "lab_report"
OLD, NEW = ROOT / "2026-11-01_diplosim_detection_curve", ROOT / "2026-11-03_diplosim_mask_ig_loci"
RUNS = ["t50_n00", "t40_n10", "t30_n20", "t20_n30", "t10_n40"]
PUR = [0.97, 0.70, 0.48, 0.29, 0.14]
KEY = "minorHP_depth_lt_0.1"


def get(d, r):
    for row in csv.DictReader(open(d / r / "tables" / "ppc_stats.tsv"), delimiter="\t"):
        if row["statistic"] == KEY:
            return row


old = [get(OLD, r) for r in RUNS]
new = [get(NEW, r) for r in RUNS]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, log in zip(axes, (False, True)):
    lo = [float(x["sim_q2.5"]) for x in new]
    hi = [float(x["sim_q97.5"]) for x in new]
    ax.fill_between(PUR, [max(v, 1e-5) for v in lo] if log else lo, hi, color="#d6e3f3", label="diplosim 95% band")
    ax.plot(PUR, [float(x["sim_median"]) or 1e-5 for x in new], "--", color="#2f6db5", label="diplosim median")
    ax.plot(PUR, [float(x["real"]) for x in old], "o-", color="#9AA3AE", label="real, all sites")
    ax.plot(PUR, [float(x["real"]) for x in new], "o-", color="#c96a1b", label="real, Ig loci masked")
    ax.invert_xaxis()
    ax.set_xlabel("purity (from ASCAT conversion)")
    ax.set_ylabel("fraction of SNVs with minor HP < 0.1")
    if log:
        ax.set_yscale("log")
        ax.set_title("log scale")
    else:
        ax.set_title("linear scale")
axes[0].legend(fontsize=8)
fig.tight_layout()
fig.savefig(NEW / "loh_mask.png", dpi=150)
print(NEW / "loh_mask.png")
