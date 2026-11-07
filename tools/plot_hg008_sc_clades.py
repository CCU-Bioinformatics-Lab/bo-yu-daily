#!/usr/bin/env python3
"""Heatmap of the 119 HG008 single cells across the rebuilt clone-tree branches.

Cells are grouped with the rules of hg008_sc_clade_test.py. Color is rel, capped at 1.
Usage: python3 tools/plot_hg008_sc_clades.py CELL_BY_BRANCH.tsv OUT.png
"""
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"

INK, MUTE = "#0b0b0b", "#52514e"
RAMP = LinearSegmentedColormap.from_list("rel", ["#f1f5fb", "#a9c8ee", "#2a78d6", "#123f7a"])
SEVEN, FOUR, TWO = "2D6,2E6,SC14,SC24,SC28,SC6,SC9", "SC14,SC24,SC28,SC9", "SC14,SC28"
ROWS = [(SEVEN, "除了 3E4 的 7 株（127）"), (FOUR, "SC14, SC24, SC28, SC9（14）"), (TWO, "SC14, SC28（68）"),
        ("2D6,2E6", "2D6, 2E6（31）"), ("SC24,SC9", "SC24, SC9（17）"), ("3E4", "3E4 private（792）")]
GROUPS = ["不帶 7 株分枝", "只帶 7 株分枝", "也帶 4 株分枝", "也帶 2 株分枝"]
GAP = 2


def group_of(row):
    if float(row[SEVEN]) <= .2:
        return 0
    if float(row[TWO]) >= .5:
        return 3
    return 2 if float(row[FOUR]) >= .5 else 1


def main():
    with open(sys.argv[1]) as fh:
        cells = list(csv.DictReader(fh, delimiter="\t"))
    fig, ax = plt.subplots(figsize=(12, 3.7), dpi=170)
    x = 0
    ticks = []
    for g, name in enumerate(GROUPS):
        members = sorted((c for c in cells if group_of(c) == g), key=lambda c: (-float(c["2D6,2E6"]), -float(c["3E4"])))
        start = x
        for cell in members:
            for y, (branch, _) in enumerate(ROWS):
                ax.add_patch(plt.Rectangle((x, y), .88, .88, color=RAMP(min(float(cell[branch]), 1.0)), lw=0))
            x += 1
        ticks.append((start, x, f"{name}（{len(members)}）"))
        x += GAP
    for start, end, label in ticks:
        ax.text((start + end) / 2, -.28, label, ha="center", fontsize=9.5, color=INK)
    ax.set_yticks([i + .44 for i in range(len(ROWS))], [label for _, label in ROWS], fontsize=9, color=INK)
    ax.set_xticks([])
    ax.set_xlim(-.5, x - GAP + .5)
    ax.set_ylim(len(ROWS), -.7)
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    bar = fig.add_axes([.86, .035, .11, .035])
    bar.imshow([[i / 100 for i in range(101)]], cmap=RAMP, aspect="auto", extent=(0, 1, 0, 1))
    bar.set_yticks([])
    bar.set_xticks([0, 1], ["0", "≥1"], fontsize=7.5, color=MUTE)
    bar.tick_params(length=0)
    for side in bar.spines.values():
        side.set_visible(False)
    fig.text(.01, .955, "每一欄是一顆細胞：單細胞支持 3 層巢狀分枝", fontsize=12, color=INK)
    fig.text(.01, .03, "括號是用來檢查的 SNV 數。顏色是該分枝的 SNV 偵出比例除以該細胞的 truncal 偵測率，1 代表和 truncal 一樣常被偵測到。", fontsize=8, color=MUTE)
    fig.subplots_adjust(left=.17, right=.99, top=.88, bottom=.13)
    fig.savefig(sys.argv[2])


if __name__ == "__main__":
    main()
