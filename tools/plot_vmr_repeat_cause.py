#!/usr/bin/env python3
"""Why real HCC1395 t50 depth VMR sits just above the diplosim 95% band: one mechanism figure.

Panel 1 (schematic): reads from several copies of a repeat all map to the one copy in the reference.
Panel 2 (schematic): depth along SNV sites, real (rare spikes) vs diplosim (no spikes).
Panel 3 (measured): VMR split into CN part / same-CN part / repeat sites, real vs diplosim, with a zoom
on the 95% band.
Usage: python3 tools/plot_vmr_repeat_cause.py   (matplotlib is not visible under -I)
Writes lab_report/2026-11-03_diplosim_vmr_t50_repeats/vmr_cause.png
"""
import csv
import random
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
LR = ROOT / "lab_report"
OUT = LR / "2026-11-03_diplosim_vmr_t50_repeats"
REAL_T = LR / "2026-11-01_diplosim_detection_curve/t50_n00/tables/real_per_snv.tsv"
REAL_N = LR / "2026-11-01_diplosim_phi_from_normal/tables/real_per_snv.tsv"   # t00_n25, same sites
ASCAT = LR / "2026-10-30_ascat_hcc1395_5khz/tables/snv_cn.tsv"
PPC = LR / "2026-11-03_diplosim_mask_ig_loci/t50_n00/tables/ppc_stats.tsv"
SIM_CN = OUT / "tables/sim_cn_part.tsv"
IG = [("chr14", 105586437, 106879844), ("chr2", 88857361, 90235368), ("chr22", 22026076, 22922913)]
REPEAT_FOLD = 3        # normal depth >= 3 x its median = repeat site

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

BG, INK, SUB, LINE = "#f7f6f2", "#1f2a37", "#6b7480", "#e3e1da"
REAL, SIM, REP, SNV = "#c96a1b", "#2f6db5", "#7b4fa8", "#D23A2E"
READ, CHROM = "#b8bec6", "#d9d6cc"
REAL_L, SIM_L = "#f0cfae", "#c4d6ee"


def cols(r):
    return [int(r[k]) for k in ("ref1", "alt1", "ref2", "alt2", "ref0", "alt0")]


def measure():
    tum = {(r["chrom"], int(r["pos"])): cols(r) for r in csv.DictReader(open(REAL_T), delimiter="\t")}
    nor = {(r["chrom"], int(r["pos"])): sum(cols(r)) for r in csv.DictReader(open(REAL_N), delimiter="\t")}
    cn = {(r["chrom"], int(r["pos"])): int(r["total_cn"]) for r in csv.DictReader(open(ASCAT), delimiter="\t")}
    sites = []
    for k, v in tum.items():
        d, a = sum(v), v[1] + v[3] + v[5]
        if a >= 5 and a / d >= 0.10 and not any(k[0] == c and lo <= k[1] <= hi for c, lo, hi in IG):
            sites.append((d, nor[k], cn.get(k)))
    vmr = lambda ds: st.pvariance(ds) / st.fmean(ds)
    nmed = st.median(n for _, n, _ in sites)
    rep = [s for s in sites if s[1] >= REPEAT_FOLD * nmed]
    keep = [s for s in sites if s[1] < REPEAT_FOLD * nmed]
    by = {}
    for d, _, c in keep:
        by.setdefault(c, []).append(d)
    mu = {c: st.fmean(v) for c, v in by.items()}
    m = {"all": vmr([d for d, _, _ in sites]), "no_rep": vmr([d for d, _, _ in keep]),
         "cn": vmr([mu[c] for _, _, c in keep]), "n_rep": len(rep), "nmed": nmed,
         "rep_norm_fold": (min(n for _, n, _ in rep) / nmed, max(n for _, n, _ in rep) / nmed)}
    ppc = {r["statistic"]: r for r in csv.DictReader(open(PPC), delimiter="\t")}["depth_VMR"]
    m.update(sim_med=float(ppc["sim_median"]), sim_lo=float(ppc["sim_q2.5"]), sim_hi=float(ppc["sim_q97.5"]))
    simcn = [float(r["VMR_between_CN"]) for r in csv.DictReader(open(SIM_CN), delimiter="\t")]
    m.update(sim_cn=st.median(simcn), sim_cn_lo=min(simcn), sim_cn_hi=max(simcn))
    return m


def rbar(ax, x, y, w, h, color, z=2, ec="none", lw=0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={min(h, w) / 2}",
                                fc=color, ec=ec, lw=lw, zorder=z))


def chrom(ax, x, y, w, h=0.32, label=None):
    rbar(ax, x, y, w, h, CHROM, z=1)
    if label:
        ax.text(x - 0.15, y + h / 2, label, ha="right", va="center", fontsize=13, color=SUB)


def panel_mechanism(ax, m):
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
    ax.text(0, 11.6, "① reference 上的重複序列", fontsize=18, weight="bold", color=INK, va="top")
    ax.text(0, 10.7, "細胞裡的 DNA（normal、tumor 都一樣）", fontsize=13, color=SUB, va="top")
    # four genomic copies of the same repeat, each with its own reads
    rows = [(9.3, "chr21"), (8.2, "chr4"), (7.1, "其他位置"), (6.0, "其他位置")]
    for y, lab in rows:
        chrom(ax, 2.0, y, 7.2, label=lab)
        ax.add_patch(Rectangle((5.0, y), 1.2, 0.32, fc=REP, ec="none", zorder=2))
        for i in range(3):                   # three reads over this copy
            rbar(ax, 4.6 + 0.3 * i, y + 0.45 + 0.18 * i, 1.2, 0.13, READ, z=3)
    ax.text(6.35, 9.46, "重複序列", fontsize=12, color=REP, va="center", weight="bold")
    # mapping arrow
    ax.add_patch(FancyArrowPatch((5.6, 5.75), (5.6, 4.35), arrowstyle="-|>", mutation_scale=28, lw=3,
                                 color=INK, zorder=4))
    ax.text(5.95, 5.05, "比對", fontsize=14, color=INK, va="center", weight="bold")
    # reference with one copy: every read piles onto it
    ax.text(0, 4.0, "reference 只有 1 份", fontsize=13, color=SUB, va="top")
    y0 = 0.6
    chrom(ax, 1.0, y0, 8.4)
    ax.add_patch(Rectangle((5.0, y0), 1.2, 0.32, fc=REP, ec="none", zorder=2))
    ax.add_patch(plt.Circle((5.6, y0 + 0.16), 0.13, fc=SNV, ec="white", lw=1.5, zorder=5))
    ax.add_patch(plt.Circle((2.4, y0 + 0.16), 0.13, fc=SNV, ec="white", lw=1.5, zorder=5))
    for i in range(2):                       # ordinary site: two reads
        rbar(ax, 1.7 + 0.25 * i, y0 + 0.45 + i * 0.18, 1.3, 0.13, READ, z=3)
    for i in range(12):                      # repeat: reads from all four copies
        rbar(ax, 4.6 + (i % 3) * 0.3, y0 + 0.45 + i * 0.18, 1.2, 0.13, READ, z=3)
    ax.annotate("", xy=(2.45, y0 + 0.86), xytext=(2.45, y0 + 0.4),
                arrowprops=dict(arrowstyle="<->", color=SUB, lw=1.5))
    ax.text(2.6, y0 + 1.25, f"一般位點\nnormal 約 {m['nmed']:.0f}×", fontsize=12, color=SUB, va="bottom")
    ax.annotate("", xy=(7.0, y0 + 2.75), xytext=(7.0, y0 + 0.4),
                arrowprops=dict(arrowstyle="<->", color=REP, lw=2))
    lo, hi = m["rep_norm_fold"]
    ax.text(7.2, y0 + 1.6, f"depth 暴增\nnormal {lo:.0f}–{hi:.0f} 倍", fontsize=13, color=REP, va="center",
            weight="bold")
    ax.add_patch(plt.Circle((0.25, 0.25), 0.13, fc=SNV, ec="white", lw=1.5, zorder=5))
    ax.text(0.5, 0.25, "SNV 位點", fontsize=11, color=SUB, va="center")
    ax.text(9.9, 0.1, "示意（倍數為實際結果）", fontsize=11, color=SUB, ha="right")


def panel_tracks(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
    ax.text(0, 11.6, "② SNV 位點的 depth", fontsize=18, weight="bold", color=INK, va="top")
    rng = random.Random(3)
    n, spikes = 46, {9: 3.9, 10: 4.3, 31: 3.6}
    for base, lab, col, sp in ((6.2, "真實 HCC1395", REAL, True), (0.9, "diplosim", SIM, False)):
        ax.text(0, base + 4.0, lab, fontsize=14, color=col, weight="bold", va="center")
        ax.text(9.7, base + 4.0, "每根＝1 個 SNV 位點", fontsize=11, color=SUB, va="center", ha="right")
        chrom(ax, 0.3, base - 0.45, 9.4, h=0.28)
        for i in range(n):
            x = 0.4 + i * 0.2
            h = max(0.35, rng.gauss(1.3, 0.35))
            is_rep = sp and i in spikes
            if is_rep:
                h = spikes[i] * 0.75
            ax.add_patch(Rectangle((x, base), 0.14, h, fc=REP if is_rep else col, ec="none", zorder=2))
            if is_rep:
                ax.add_patch(Rectangle((x - 0.02, base - 0.45), 0.18, 0.28, fc=REP, ec="none", zorder=3))
        ax.axhline(base, xmin=0.03, xmax=0.97, color=LINE, lw=1, zorder=1)
    ax.text(2.6, 6.2 + 3.35, "◀ 少數位點暴增", fontsize=12, color=REP, va="center", weight="bold")
    ax.text(5.0, 0.9 + 2.9, "只有小幅高低\n沒有暴增", fontsize=12, color=SIM, va="center", ha="center")
    ax.text(9.9, 0.1, "示意", fontsize=11, color=SUB, ha="right")


def panel_vmr(fig, ax, m):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINE)
    ax.tick_params(colors=SUB, labelsize=12)
    ax.set_xlim(-1.0, 1.75); ax.set_ylim(0, 10.6)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["真實", "diplosim"], fontsize=14, color=INK)
    ax.set_ylabel("depth 變異÷平均（VMR）", fontsize=13, color=SUB)
    ax.set_title("③ VMR 拆開看（t50，實際結果）", fontsize=18, weight="bold", color=INK, loc="left", pad=14)
    w, gap = 0.5, 0.04
    segs = [(0, [(m["cn"], REAL_L), (m["no_rep"] - m["cn"], REAL), (m["all"] - m["no_rep"], REP)]),
            (1, [(m["sim_cn"], SIM_L), (m["sim_med"] - m["sim_cn"], SIM)])]
    for x, parts in segs:
        y = 0
        for h, c in parts:
            ax.add_patch(Rectangle((x - w / 2, y), w, max(h - gap, 0.02), fc=c, ec="none", zorder=2))
            y += h
    ax.axhspan(m["sim_lo"], m["sim_hi"], color=SIM_L, alpha=0.45, zorder=0)
    ax.axhline(m["sim_hi"], color=SIM, lw=1.5, ls="--", zorder=1)
    ax.text(1.0, m["sim_hi"] + 0.15, f"diplosim 95% 上限 {m['sim_hi']:.2f}", fontsize=11, color=SIM,
            va="bottom", ha="center")
    ax.text(-0.29, m["cn"] / 2, f"CN 不同\n{m['cn']:.1f}", fontsize=12, color=INK, va="center", ha="right")
    ax.text(1.29, m["sim_cn"] / 2, f"CN 不同\n{m['sim_cn_lo']:.1f}–{m['sim_cn_hi']:.1f}", fontsize=12,
            color=INK, va="center")
    ax.text(-0.29, m["cn"] + (m["no_rep"] - m["cn"]) / 2 - 0.2, "同 CN\n小幅高低", fontsize=12, color=INK,
            va="center", ha="right")
    ax.text(1.29, m["sim_cn"] + (m["sim_med"] - m["sim_cn"]) / 2 - 0.2, "同 CN\n小幅高低", fontsize=12,
            color=INK, va="center")
    ax.text(1, m["sim_med"] - 0.25, "中位數", fontsize=11, color="white", ha="center", va="top")
    ax.text(-0.29, m["all"] + 0.05, "重複序列", fontsize=12, color=REP, ha="right", va="center", weight="bold")
    # zoom on the band edge
    z = fig.add_axes([0.885, 0.50, 0.10, 0.34])
    z.set_facecolor("white")
    z.set_xlim(0, 1); z.set_ylim(8.9, 9.55)
    z.axhspan(8.9, m["sim_hi"], color=SIM_L, alpha=0.6)
    z.axhline(m["sim_hi"], color=SIM, lw=1.5, ls="--")
    z.scatter([0.5], [m["all"]], s=110, fc="white", ec=REAL, lw=2.5, zorder=3)
    z.scatter([0.5], [m["no_rep"]], s=110, fc=REAL, ec="white", lw=1.5, zorder=3)
    z.add_patch(FancyArrowPatch((0.5, m["all"] - 0.03), (0.5, m["no_rep"] + 0.04), arrowstyle="-|>",
                                mutation_scale=16, lw=1.8, color=REP))
    z.text(0.62, m["all"], f"✗ {m['all']:.2f}", fontsize=12, color=INK, va="center")
    z.text(0.62, m["no_rep"], f"✓ {m['no_rep']:.2f}", fontsize=12, color=INK, va="center")
    z.text(0.5, 9.33 - 0.12, f"拿掉 {m['n_rep']} 個\n重複序列位點", fontsize=11, color=REP, ha="center",
           va="top")
    z.set_xticks([]); z.tick_params(colors=SUB, labelsize=10)
    for s in z.spines.values():
        s.set_color(LINE)
    z.set_title("放大", fontsize=12, color=SUB)


def main():
    m = measure()
    fig = plt.figure(figsize=(20, 8.4), facecolor=BG)
    a1 = fig.add_axes([0.01, 0.03, 0.40, 0.94]); a1.set_facecolor(BG)
    a2 = fig.add_axes([0.42, 0.03, 0.22, 0.94]); a2.set_facecolor(BG)
    a3 = fig.add_axes([0.685, 0.08, 0.17, 0.80])
    panel_mechanism(a1, m)
    panel_tracks(a2)
    panel_vmr(fig, a3, m)
    fig.savefig(OUT / "vmr_cause.png", dpi=150, facecolor=BG)
    print(OUT / "vmr_cause.png", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})


if __name__ == "__main__":
    main()
