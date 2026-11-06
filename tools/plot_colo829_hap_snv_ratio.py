#!/usr/bin/env python3
"""Plot the COLO829 hap1 share per homolog pair. Usage: python3 tools/plot_colo829_hap_snv_ratio.py <out_dir>"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"
INK, MUTE, LINE, MARK = "#1c2a26", "#5a6a62", "#d4dcd6", "#1f6f8b"
out = Path(sys.argv[1])
rows = [r for r in csv.DictReader(open(out / "homolog_pairs.tsv"), delimiter="\t") if r["both_retained"] == "True"]
rows.sort(key=lambda r: (r["source"] != "authors", -int(r["hap1_snv"]) - int(r["hap2_snv"])))
fig, ax = plt.subplots(figsize=(8, 0.42 * len(rows) + 1.5), dpi=170)
for i, r in enumerate(rows):
    y = len(rows) - i
    e = float(r["expected_share"])
    d, lo, hi = float(r["hap1_share"]) - e, float(r["ci_low"]) - e, float(r["ci_high"]) - e
    filled = r["source"] == "authors"
    ax.plot([lo, hi], [y, y], color=MARK, lw=2, solid_capstyle="round", zorder=2)
    ax.scatter([d], [y], s=62, zorder=3, facecolor=MARK if filled else "white", edgecolor=MARK, linewidth=1.6)
    ax.text(0.205, y, f"{r['hap1_snv']} : {r['hap2_snv']}", va="center", ha="right", color=MUTE, fontsize=8.5)
ax.axvline(0, color=INK, lw=1.2, zorder=1)
ax.set_yticks([len(rows) - i for i in range(len(rows))], [r["pair"].replace("len", "").replace("Mb", " Mb") for r in rows], color=INK, fontsize=9)
ax.set_xlim(-0.2, 0.21)
ax.set_ylim(0.3, len(rows) + 0.7)
ax.set_xlabel("hap1 突變比例 − 依長度預期的比例（95% CI）", color=INK, fontsize=9.5)
ax.grid(axis="x", color=LINE, lw=.7)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(LINE)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=MUTE, labelsize=8.5)
ax.scatter([], [], s=62, facecolor=MARK, edgecolor=MARK, linewidth=1.6, label="作者標明的配對")
ax.scatter([], [], s=62, facecolor="white", edgecolor=MARK, linewidth=1.6, label="依長度推論的配對")
ax.legend(loc="lower left", frameon=False, fontsize=8.5, labelcolor=INK)
fig.tight_layout()
fig.savefig(out / "hap1_share_by_pair.png")
