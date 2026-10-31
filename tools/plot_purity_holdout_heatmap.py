#!/usr/bin/env python3
"""Heatmap of PPC relative distance per statistic and purity for the diplosim purity holdout.

Usage: python3 tools/plot_purity_holdout_heatmap.py DISTANCE_TSV OUT_PNG
  DISTANCE_TSV: output of tools/ppc_distance_score.py with columns t50 t40 t30 t20 t10.
"""
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import TwoSlopeNorm

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

NAMES = {
    "split_alt_frac": "alt 分在兩條 HP", "depth_VMR": "depth 變異÷平均", "VAF_frac_gt_0.6": "VAF > 0.6 的比例",
    "minorHP_depth_lt_0.1": "minor HP < 0.1 的位點", "VAF_q10": "VAF 10% 分位", "VAF_q50": "VAF 中位數",
    "VAF_q90": "VAF 90% 分位", "tag_frac_lt_0.5_sites": "tag 比例 < 0.5 的位點", "inHP_VAF_q50": "HP 內 VAF 中位數",
    "alt_on_minorHP": "SNV 在 depth 較少那條 HP", "HP0_frac_pooled": "HP0 比例", "tag_frac_SD_sites": "位點 tag 比例 SD",
    "minorHP_depth_q50": "minor HP 比例中位數＊",
}
COLS = [("t50", "t50_n00\n0.97\n（校正用）"), ("t40", "t40_n10\n0.70"), ("t30", "t30_n20\n0.48"),
        ("t20", "t20_n30\n0.29"), ("t10", "t10_n40\n0.14")]


def main():
    rows = {r["statistic"]: r for r in csv.DictReader(open(sys.argv[1]), delimiter="\t") if r["statistic"] in NAMES}
    order = sorted(rows, key=lambda k: -max(abs(float(rows[k][f"{c}_rel"])) for c, _ in COLS if c != "t50"))
    order.remove("minorHP_depth_q50")
    order.append("minorHP_depth_q50")
    vals = [[float(rows[k][f"{c}_rel"]) for c, _ in COLS] for k in order]
    fig, ax = plt.subplots(figsize=(11, 9.5), dpi=110)
    fig.patch.set_facecolor("#F2F4F3")
    clipped = [[max(-1, min(1, v)) for v in r] for r in vals]
    ax.imshow(clipped, cmap="RdBu_r", norm=TwoSlopeNorm(0, -1, 1), aspect="auto")
    for i, r in enumerate(vals):
        for j, v in enumerate(r):
            big = abs(v) > 0.1
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=11,
                    weight="bold" if big else "normal", color="white" if abs(v) > 0.5 else "#17201D")
            if big:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="#17201D", lw=1.6))
    ax.set_xticks(range(len(COLS)))
    ax.set_xticklabels([c[1] for c in COLS], fontsize=10.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([NAMES[k] for k in order], fontsize=11)
    ax.axhline(5.5, color="#17201D", lw=1.5, ls="--")
    fig.text(0.03, 0.965, "purity holdout：哪幾項統計有差？（相對差距＝（模擬 − 真實）÷ 真實）", fontsize=16, weight="bold")
    fig.text(0.03, 0.935, "紅＝模擬偏高，藍＝模擬偏低（色階在 ±1 截斷）；粗框＝|差距| > 0.1。虛線以上 6 項會隨 purity 下降而偏離。",
             fontsize=10.5, color="#5B6864")
    fig.text(0.03, 0.02, "＊minor HP 比例中位數在 t50_n00 跳動（LOH 超過一半時中位數會從約 0.2 跳到 0），不當判定依據。",
             fontsize=9.5, color="#5B6864")
    fig.subplots_adjust(left=0.27, right=0.97, top=0.80, bottom=0.06)
    fig.savefig(sys.argv[2], facecolor=fig.get_facecolor())
    print(sys.argv[2])


if __name__ == "__main__":
    main()
