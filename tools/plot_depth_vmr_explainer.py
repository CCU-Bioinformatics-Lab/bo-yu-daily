#!/usr/bin/env python3
"""Explain the PPC statistic "depth variance / mean" and how depth_dispersion closed its gap.

Usage: python3 tools/plot_depth_vmr_explainer.py POISSON_RUNS_DIR NB_RUNS_DIR OUT_PNG
  *_RUNS_DIR hold diplosim outputs (s*/diplosim.tsv) of the same setting without and with
  --depth-dispersion. Real depths and CN come from the 10-30 PPC and ASCAT tables.
"""
import csv
import glob
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab_report"
REAL = LAB / "2026-10-31_diplosim_ppc_hcc1395_lost045" / "tables" / "real_per_snv.tsv"  # same table as the deleted 2026-10-30 run
ASCAT = LAB / "2026-10-30_ascat_hcc1395_5khz" / "tables" / "snv_cn.tsv"

INK, MUTED, LINE, BG = "#17201D", "#5B6864", "#CDD5D2", "#F2F4F3"
REAL_C, POIS_C, NB_C = "#17201D", "#A3ADA9", "#2C7A4C"
BETWEEN_C, WITHIN_C = "#2D5EA6", "#BF522E"

STEPS = [  # (label, PPC directory)
    ("預設", "2026-10-30_diplosim_ppc_hcc1395"),  # deleted 2026-11-04, never tracked: this panel can no longer be redrawn
    ("LOH 0.45", "2026-10-31_diplosim_ppc_hcc1395_lost045"),
    ("Beta tag", "2026-10-31_diplosim_ppc_hcc1395_tagbeta"),
    ("多次 CNA\n＋truncal 0.8", "2026-10-31_diplosim_ppc_hcc1395_mult_t0.8"),
    ("base error\n0.01", "2026-10-31_diplosim_ppc_hcc1395_base001"),
    ("gain_B ×2", "2026-10-31_diplosim_ppc_hcc1395_gainB2"),
    ("φ 0.01", "2026-10-31_diplosim_ppc_hcc1395_depthdisp0.01"),
    ("φ 0.02", "2026-10-31_diplosim_ppc_hcc1395_depthdisp0.02"),
    ("φ 0.03", "2026-10-31_diplosim_ppc_hcc1395_depthdisp0.03"),
]


def called(v):
    d, a = sum(v), v[1] + v[3] + v[5]
    return d > 0 and a >= 3 and a / d >= 0.08


def real_by_state():
    cn = {(r["chrom"], r["pos"]): (int(r["total_cn"]), int(r["minor_cn"]))
          for r in csv.DictReader(open(ASCAT), delimiter="\t")}
    out = defaultdict(list)
    for r in csv.DictReader(open(REAL), delimiter="\t"):
        v = [int(r[k]) for k in ("ref1", "alt1", "ref2", "alt2", "ref0", "alt0")]
        k = (r["chrom"], r["pos"])
        if k in cn and called(v):
            out[cn[k]].append(sum(v))
    return out


def sim_by_state(run_dir):
    out = defaultdict(list)
    for f in glob.glob(f"{run_dir}/s*/diplosim.tsv"):
        for r in csv.DictReader(open(f), delimiter="\t"):
            v = [int(r[k]) for k in ("HP1_REF", "HP1_ALT", "HP2_REF", "HP2_ALT", "HP0_REF", "HP0_ALT")]
            if called(v):
                a, b = round(float(r["CN_A"])), round(float(r["CN_B"]))
                out[(a + b, min(a, b))].append(sum(v))
    return out


def decompose(groups):
    """Law of total variance, divided by the overall mean: (between-CN, within-CN) parts of VMR."""
    allx = [x for g in groups.values() for x in g]
    mu, n = statistics.fmean(allx), len(allx)
    within = sum(len(g) * statistics.pvariance(g) for g in groups.values() if len(g) > 1) / n
    between = sum(len(g) * (statistics.fmean(g) - mu) ** 2 for g in groups.values()) / n
    return between / mu, within / mu


def vmr(x):
    return statistics.pvariance(x) / statistics.fmean(x)


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=9.5, colors=MUTED)


def panel_a(ax):
    rng = random.Random(3)
    mean, phi = 50, 0.03
    pois = [poisson(rng, mean) for _ in range(40000)]
    nb = [poisson(rng, mean * rng.gammavariate(1 / phi, phi)) for _ in range(40000)]
    bins = range(10, 111, 2)
    ax.hist(pois, bins=bins, color=POIS_C, alpha=0.85, label=f"Poisson：變異÷平均 ≈ {vmr(pois):.1f}")
    ax.hist(nb, bins=bins, histtype="step", lw=2, color=NB_C, label=f"negative binomial（φ 0.03）：≈ {vmr(nb):.1f}")
    ax.axvline(mean, color=INK, lw=1, ls=":")
    ax.set_xlabel("一個位點的 depth（平均都是 50）", fontsize=10)
    ax.set_yticks([])
    ax.legend(fontsize=9.5, frameon=False, loc="upper right")
    ax.set_title("A　這個統計量是什麼", loc="left", fontsize=14, weight="bold", color=INK)
    ax.text(0.0, -0.17, "depth 變異÷平均 ＝ 所有位點 depth 的變異數 ÷ 平均 depth。"
            "只有隨機抽樣（Poisson）時約等於 1；越大，代表位點之間的 depth 差越多。",
            transform=ax.transAxes, fontsize=10, color=INK, va="top")
    style(ax)


def poisson(rng, lam):
    # Knuth for small means, normal approximation is not used to keep the shape exact
    import math
    if lam > 30:
        # sum of smaller Poissons keeps it exact without overflow
        k, rest = 0, lam
        while rest > 0:
            step = min(rest, 30)
            k += poisson(rng, step)
            rest -= step
        return k
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def panel_b(ax, real, pois, nb):
    rows = [("真實 HCC1395", decompose(real)), ("改動前（Poisson）", decompose(pois)), ("φ 0.03", decompose(nb))]
    for i, (name, (bt, wi)) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, bt, color=BETWEEN_C, height=0.55)
        ax.barh(y, wi, left=bt, color=WITHIN_C, height=0.55)
        ax.text(bt / 2, y, f"{bt:.1f}", color="white", ha="center", va="center", fontsize=10, weight="bold")
        ax.text(bt + wi / 2, y, f"{wi:.1f}", color="white", ha="center", va="center", fontsize=10, weight="bold")
        ax.text(bt + wi + 0.15, y, f"合計 {bt + wi:.1f}", color=INK, va="center", fontsize=10)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=10.5)
    ax.set_xlim(0, 12)
    ax.set_xlabel("depth 變異÷平均（依 CN 狀態拆成兩部分）", fontsize=10)
    handles = [Patch(color=BETWEEN_C, label="CN 之間：CN 不同 → 平均 depth 不同"),
               Patch(color=WITHIN_C, label="CN 之內：CN 相同的位點彼此的差異（Poisson 只給 1）")]
    ax.legend(handles=handles, fontsize=9.5, frameon=False, loc="upper left", bbox_to_anchor=(0.0, -0.17), ncol=1)
    ax.set_title("B　整體變異 ＝ CN 之間 ＋ CN 之內", loc="left", fontsize=14, weight="bold", color=INK)
    style(ax)


def panel_c(ax, real, pois, nb, state=(3, 1)):
    bins = range(10, 111, 3)
    r, p, n = real[state], pois[state], nb[state]
    ax.hist(r, bins=bins, density=True, color="white", edgecolor=REAL_C, lw=1.2, label=f"真實：變異÷平均 {vmr(r):.2f}")
    ax.hist(p, bins=bins, density=True, histtype="step", lw=2, color=POIS_C, label=f"改動前（Poisson）：{vmr(p):.2f}")
    ax.hist(n, bins=bins, density=True, histtype="step", lw=2, color=NB_C, label=f"φ 0.03：{vmr(n):.2f}")
    ax.set_xlabel(f"CN {state} 位點的 depth", fontsize=10)
    ax.set_yticks([])
    ax.legend(fontsize=9.5, frameon=False, loc="upper right")
    ax.set_title(f"C　只看同一種 CN {state}：真實比 Poisson 寬", loc="left", fontsize=14, weight="bold", color=INK)
    style(ax)


def panel_d(ax):
    vals, lo, hi = [], [], []
    real = None
    for _, d in STEPS:
        with open(LAB / d / "tables" / "ppc_stats.tsv") as f:
            row = next(r for r in csv.DictReader(f, delimiter="\t") if r["statistic"] == "depth_VMR")
        real = float(row["real"])
        vals.append(float(row["sim_median"]))
        lo.append(float(row["sim_q2.5"]))
        hi.append(float(row["sim_q97.5"]))
    xs = range(len(STEPS))
    ax.axhline(real, color=REAL_C, lw=1.5, ls="--")
    ax.text(-0.3, real + 0.1, f"真實 {real:.2f}", fontsize=10, color=REAL_C, ha="left")
    colors = [NB_C if s[0].startswith("φ") else POIS_C for s in STEPS]
    ax.vlines(xs, lo, hi, color=colors, lw=3, alpha=0.5)
    ax.scatter(xs, vals, color=colors, s=45, zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v - 0.45, f"{v:.1f}", fontsize=9, ha="center", color=INK)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([s[0] for s in STEPS], fontsize=8.8)
    ax.set_ylim(7, 11)
    ax.set_ylabel("模擬的 depth 變異÷平均", fontsize=10)
    ax.set_title("D　今天每一步的變化（點＝200 次模擬中位數，線＝95% 區間）", loc="left", fontsize=14, weight="bold", color=INK)
    style(ax)


def main():
    pois_dir, nb_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    real, pois, nb = real_by_state(), sim_by_state(pois_dir), sim_by_state(nb_dir)
    fig = plt.figure(figsize=(16, 11), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.text(0.04, 0.955, "depth 變異÷平均：模擬原本太小，加入 depth overdispersion（φ）後對上真實",
             fontsize=19, weight="bold", color=INK)
    fig.text(0.04, 0.925, "注意：這次是把模擬的值「調高」。真實 9.54，改動前模擬 7.94，φ 0.03 後 9.71。",
             fontsize=11.5, color=MUTED)
    axes = [fig.add_axes(r) for r in ([0.05, 0.60, 0.40, 0.27], [0.57, 0.64, 0.38, 0.23],
                                       [0.05, 0.08, 0.40, 0.36], [0.53, 0.10, 0.44, 0.34])]
    for ax in axes:
        ax.set_facecolor("white")
    panel_a(axes[0])
    panel_b(axes[1], real, pois, nb)
    panel_c(axes[2], real, pois, nb)
    panel_d(axes[3])
    fig.savefig(out, facecolor=fig.get_facecolor())
    print(out)


if __name__ == "__main__":
    main()
