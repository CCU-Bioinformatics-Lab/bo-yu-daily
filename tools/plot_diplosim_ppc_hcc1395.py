#!/usr/bin/env python3
"""Figure for tools/diplosim_ppc_hcc1395.py: one panel per statistic, sim distribution vs real.

Usage: python3 tools/plot_diplosim_ppc_hcc1395.py OUT_DIR
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for w in ("Regular", "Bold"):
    font_manager.fontManager.addfont(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc")
plt.rcParams["font.family"] = "Noto Sans CJK JP"

# (key, label, what it checks)
PANELS = [
    ("depth_median", "depth 中位數", "coverage（輸入）"),
    ("depth_VMR", "depth 變異÷平均", "Poisson depth"),
    ("VAF_q10", "VAF 10% 分位", "CN、clone 比例"),
    ("VAF_q50", "VAF 中位數", "CN、clone 比例"),
    ("VAF_q90", "VAF 90% 分位", "CN、clone 比例"),
    ("VAF_frac_gt_0.6", "VAF > 0.6 的比例", "LOH、multiplicity"),
    ("HP0_frac_pooled", "HP0 read 比例", "prop_tagged"),
    ("tag_frac_SD_sites", "位點 tag 比例的 SD", "prop_tagged"),
    ("tag_frac_lt_0.5_sites", "tag 比例 < 0.5 的位點", "prop_tagged"),
    ("split_alt_frac", "alt 分在兩條 HP 的 SNV", "HP split ②"),
    ("inHP_VAF_q50", "HP 內 VAF 中位數", "HP split ②"),
    ("minorHP_depth_q50", "minor HP depth 比例中位數", "CN（LOH）"),
    ("minorHP_depth_lt_0.1", "minor HP depth < 0.1 的位點", "CN（LOH）"),
    ("alt_on_minorHP", "SNV 在 depth 較少那條 HP", "prop_snv_on_b＋CN"),
]
IN, OUT = "#3b7dd8", "#d0573a"


def main():
    out = Path(sys.argv[1])
    real = json.loads((out / "tables" / "real_stats.json").read_text())
    sims = json.loads((out / "tables" / "sim_stats.json").read_text())
    fig, axes = plt.subplots(3, 5, figsize=(19, 10.5))
    for ax, (k, label, what) in zip(axes.flat, PANELS):
        sv = sorted(s[k] for s in sims)
        lo, hi = sv[int(0.025 * len(sv))], sv[min(len(sv) - 1, int(0.975 * len(sv)))]
        r = real[k]
        ok = lo <= r <= hi
        ax.hist(sv, bins=30, color="#b9c4d0", edgecolor="white")
        ax.axvspan(lo, hi, color="#b9c4d0", alpha=0.25, lw=0)
        ax.axvline(r, color=IN if ok else OUT, lw=2.5)
        span = max(sv + [r]) - min(sv + [r]) or 1
        ax.set_xlim(min(sv + [r]) - 0.08 * span, max(sv + [r]) + 0.08 * span)
        ax.set_title(f"{label}\n檢查：{what}", fontsize=10.5, loc="left", pad=22)
        ax.text(0, 1.02, f"真實 {r:.3g}　模擬中位 {sv[len(sv) // 2]:.3g}　{'在範圍內' if ok else '超出範圍'}",
                transform=ax.transAxes, ha="left", va="bottom", fontsize=9.5,
                color=IN if ok else OUT, fontweight="bold")
        ax.set_yticks([])
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
    leg = axes.flat[-1]
    leg.axis("off")
    leg.text(0, 1.0, "怎麼看", fontsize=13, fontweight="bold", va="top")
    leg.text(0, 0.86,
             "灰色：diplosim 200 個 seed 的分佈\n淺灰底：模擬的 95% 區間\n"
             "藍線：真實值落在區間內\n紅線：真實值超出區間\n\n"
             "真實：HCC1395 ONT t50_n00\nClairS PASS，HC 區域，31,595 SNV\n"
             "模擬：coverage 53，purity 1\n其他參數用 diplosim 預設值\n"
             "兩邊都套用 alt ≥ 3、VAF ≥ 0.08", fontsize=10.5, va="top", linespacing=1.5)
    fig.suptitle("diplosim PPC（自由模式）：真實 HCC1395 long read vs 200 次模擬", fontsize=15,
                 fontweight="bold", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out / "diplosim_ppc_hcc1395.png", dpi=130)


if __name__ == "__main__":
    main()
