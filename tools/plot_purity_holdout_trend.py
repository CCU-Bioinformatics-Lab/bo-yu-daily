#!/usr/bin/env python3
"""Purity vs PPC statistic for the diplosim purity holdout: real value (dot) vs sim 95% band.

Usage: python3 tools/plot_purity_holdout_trend.py OUT_PNG LABEL=PURITY=DIR ...
"""
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED, BG, REAL, SIM = "#17201D", "#5B6864", "#F2F4F3", "#2D5EA6", "#2C7A4C"
PANELS = [
    ("split_alt_frac", "alt 分在兩條 HP 的 SNV", "base_error、mistag"),
    ("depth_VMR", "depth 變異÷平均", "depth φ＋CN"),
    ("VAF_q50", "VAF 中位數", "CN、clone 比例、caller"),
    ("VAF_q10", "VAF 10% 分位", "caller 門檻"),
    ("minorHP_depth_lt_0.1", "minor HP depth < 0.1 的位點", "LOH＋normal 細胞"),
    ("tag_frac_lt_0.5_sites", "tag 比例 < 0.5 的位點", "tag κ"),
    ("HP0_frac_pooled", "HP0 read 比例", "prop_tagged"),
    ("tag_frac_SD_sites", "位點 tag 比例 SD", "tag κ"),
    ("alt_on_minorHP", "SNV 在 depth 較少那條 HP", "gain_B 比重"),
]


def load(d):
    with open(f"{d}/tables/ppc_stats.tsv") as f:
        return {r["statistic"]: r for r in csv.DictReader(f, delimiter="\t")}


def main():
    out = sys.argv[1]
    runs = []
    for a in sys.argv[2:]:
        lab, pur, d = a.split("=", 2)
        runs.append((lab, float(pur), load(d)))
    runs.sort(key=lambda r: r[1])
    fig, axes = plt.subplots(3, 3, figsize=(16, 12), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.suptitle("diplosim purity holdout：旋鈕在 t50_n00 校正後鎖住，只轉 purity", fontsize=18, weight="bold", x=0.03, ha="left", y=0.985)
    fig.text(0.03, 0.948, "藍點＝真實 HCC1395 subsample；綠帶＝200 次模擬的 95% 區間，綠線＝中位數。alt 分在兩條 HP、depth 變異、VAF 低端隨 purity 下降而偏離；minor HP < 0.1、HP0 比例的趨勢都跟得上。",
             fontsize=11.5, color=MUTED)
    xs = [r[1] for r in runs]
    for ax, (key, title, knob) in zip(axes.flat, PANELS):
        real = [float(r[2][key]["real"]) for r in runs]
        med = [float(r[2][key]["sim_median"]) for r in runs]
        lo = [float(r[2][key]["sim_q2.5"]) for r in runs]
        hi = [float(r[2][key]["sim_q97.5"]) for r in runs]
        ax.fill_between(xs, lo, hi, color=SIM, alpha=0.18)
        ax.plot(xs, med, color=SIM, lw=2)
        ax.plot(xs, real, "o-", color=REAL, ms=7, lw=1.2)
        ax.set_title(title, fontsize=13, weight="bold", color=INK, loc="left", pad=20)
        ax.text(0.0, 1.03, f"相關旋鈕：{knob}", transform=ax.transAxes, fontsize=9.5, color=MUTED, va="bottom")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{r[0]}\n{r[1]:.2f}" for r in runs], fontsize=8.5)
        ax.tick_params(labelsize=9)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_facecolor("white")
    fig.subplots_adjust(left=0.05, right=0.98, top=0.88, bottom=0.06, hspace=0.62, wspace=0.22)
    fig.savefig(out, facecolor=fig.get_facecolor())
    print(out)


if __name__ == "__main__":
    main()
