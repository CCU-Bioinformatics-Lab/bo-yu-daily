#!/usr/bin/env python3
"""Plot the same-haplotype share of neighbouring SNVs against its shuffled range, one panel per primary dataset.

Usage: python3 tools/plot_snv_hp_independence.py REPORT_DIR
Input: REPORT_DIR/pairs_by_distance.tsv. Output: REPORT_DIR/same_hap_by_distance.png
"""
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"

INK, MUTE, GRID, BAND, MARK = "#0b0b0b", "#52514e", "#e4e3df", "#d6d5d0", "#2a78d6"
ORDER = ["<1 kb (control)", "1-10 kb", "10-100 kb", "100 kb-1 Mb", ">=1 Mb"]
LABEL = {"<1 kb (control)": "<1 kb\n對照", "1-10 kb": "1–10\nkb", "10-100 kb": "10–100\nkb", "100 kb-1 Mb": "100 kb–\n1 Mb", ">=1 Mb": "≥1\nMb"}
TITLES = {"assembly_COLO829": "COLO829（組裝定相）", "assembly_HG008": "HG008（組裝定相）", "read_private": "HG008 private（read 定相）"}
MIN_PAIRS = 20


def main():
    folder = Path(sys.argv[1])
    with open(folder / "pairs_by_distance.tsv") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    primary = list(dict.fromkeys(r["dataset"] for r in rows if r["primary"] == "1"))
    fig, axes = plt.subplots(1, len(primary), figsize=(11.5, 3.9), dpi=170, sharey=True)
    for ax, name in zip(axes, primary):
        data = {r["distance"]: r for r in rows if r["dataset"] == name}
        for x, distance in enumerate(ORDER):
            r = data.get(distance)
            if not r or int(r["n_pairs"]) < MIN_PAIRS:
                continue
            low, high = float(r["null_low95"]), float(r["null_high95"])
            ax.fill_between([x - .32, x + .32], low, high, color=BAND, lw=0, zorder=1)
            share = float(r["share_same"])
            ax.scatter(x, share, s=46, color=MARK, edgecolor="white", linewidth=1.2, zorder=3)
            ax.annotate(f"n={r['n_pairs']}", (x, .34), ha="center", fontsize=7.5, color=MUTE)
        ax.axhline(.5, color=MUTE, lw=.8, zorder=0)
        title = TITLES.get(name, f"HG008 truncal，{name.rsplit('_', 1)[1]}（read 定相）")
        ax.set_title(title, fontsize=10, color=INK, loc="left")
        ax.set_xticks(range(len(ORDER)), [LABEL[d] for d in ORDER], fontsize=8, color=MUTE)
        ax.set_xlim(-.6, len(ORDER) - .4)
        ax.set_ylim(.3, 1.02)
        ax.tick_params(length=0, colors=MUTE, labelsize=8)
        ax.grid(axis="y", color=GRID, lw=.6)
        ax.set_axisbelow(True)
        for side in ax.spines.values():
            side.set_visible(False)
    axes[0].set_ylabel("相鄰 SNV 在同一條 HP 的比例", fontsize=9.5, color=INK)
    fig.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=MARK, label="實際"),
                        plt.Rectangle((0, 0), 1, 1, color=BAND, label="區段內打亂 HP 的 95% 範圍")],
               loc="upper right", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(.99, 1.0))
    fig.suptitle("1 kb 以上，相鄰 SNV 沒有明顯偏向同一條 HP", x=.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(folder / "same_hap_by_distance.png")


if __name__ == "__main__":
    main()
