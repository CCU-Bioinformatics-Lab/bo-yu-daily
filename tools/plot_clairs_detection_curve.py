#!/usr/bin/env python3
"""ClairS detection curve on HCC1395 ONT: P(called | alt reads) and P(called | VAF), one line per purity.

Sites = the t50_n00 ClairS PASS ∩ HC SNVs (taken as true SNVs). For each lower-purity subsample the
sites are piled up on its haplotagged CRAM (tools/diplosim_ppc_hcc1395.py real); "called" = the site
is in that subsample's own ClairS PASS ∩ HC set.

Usage: python3 tools/plot_clairs_detection_curve.py CURVE_DIR CALLS_ROOT
  CURVE_DIR/<name>/tables/real_per_snv.tsv   pileup at t50 sites
  CALLS_ROOT/<name>/tables/clairs_hc_sites.tsv   ClairS calls of that subsample
Writes CURVE_DIR/detection_by_alt.tsv, detection_by_vaf.tsv, detection_curve.png.
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED, GRID = "#17201D", "#5B6864", "#D9DEDC"
# purity is ordinal: one blue ramp, light (low purity) -> dark (high purity)
SUBS = [("t10_n40", 0.14, "#86b6ef"), ("t20_n30", 0.29, "#3987e5"), ("t30_n20", 0.48, "#256abf"), ("t40_n10", 0.70, "#0d366b")]
ALT_MAX = 30
VAF_BINS = [i / 50 for i in range(0, 31)]   # 0, 0.02, ..., 0.60


def load(curve_dir, calls_root, name):
    called = set()
    with open(Path(calls_root) / name / "tables" / "clairs_hc_sites.tsv") as f:
        for line in f:
            c, p = line.split("\t")[:2]
            called.add((c, p))
    rows = []
    with open(Path(curve_dir) / name / "tables" / "real_per_snv.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            alt = int(r["alt1"]) + int(r["alt2"]) + int(r["alt0"])
            depth = alt + int(r["ref1"]) + int(r["ref2"]) + int(r["ref0"])
            if depth:
                rows.append((alt, depth, (r["chrom"], r["pos"]) in called))
    return rows


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def by_bin(rows, key, edges):
    out = []
    for i, lo in enumerate(edges):
        hi = edges[i + 1] if i + 1 < len(edges) else float("inf")
        sel = [r for r in rows if lo <= key(r) < hi]
        k = sum(r[2] for r in sel)
        out.append((lo, len(sel), k))
    return out


def main(curve_dir, calls_root):
    data = {n: load(curve_dir, calls_root, n) for n, _, _ in SUBS}
    alt_edges = list(range(0, ALT_MAX + 1))
    tabs = {}
    for label, key, edges, fname in (("alt", lambda r: r[0], alt_edges, "detection_by_alt.tsv"),
                                     ("vaf", lambda r: r[0] / r[1], VAF_BINS, "detection_by_vaf.tsv")):
        tabs[label] = {n: by_bin(data[n], key, edges) for n, _, _ in SUBS}
        with open(Path(curve_dir) / fname, "w") as f:
            f.write(f"{label}_bin_lo\t" + "\t".join(f"{n}_n\t{n}_called\t{n}_p" for n, _, _ in SUBS) + "\n")
            for i, lo in enumerate(edges):
                cells = []
                for n, _, _ in SUBS:
                    _, m, k = tabs[label][n][i]
                    cells.append(f"{m}\t{k}\t{k / m:.4f}" if m else f"0\t0\tNA")
                f.write(f"{lo:g}\t" + "\t".join(cells) + "\n")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), dpi=150)
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.06, right=0.98, wspace=0.18)
    panels = (("alt", "SNV 的 alt read 數", "alt read 數（30 = 30 以上）"),
              ("vaf", "SNV 的 VAF", "VAF（每格 0.02）"))
    for ax, (label, title, xlab) in zip(axes, panels):
        for n, pur, col in SUBS:
            xs, ys, lo_, hi_ = [], [], [], []
            for lo, m, k in tabs[label][n]:
                if m < 20:          # too few sites for a stable proportion
                    continue
                x = lo if label == "alt" else lo + 0.01
                a, b = wilson(k, m)
                xs.append(x); ys.append(k / m); lo_.append(a); hi_.append(b)
            ax.fill_between(xs, lo_, hi_, color=col, alpha=0.18, linewidth=0)
            ax.plot(xs, ys, color=col, lw=2, label=f"{n.split('_')[0]}（purity {pur:.2f}）")
        if label == "alt":
            ax.axvline(5, color=MUTED, lw=1, ls="--")
            ax.text(5.3, 0.04, "目前硬門檻 alt ≥ 5", color=MUTED, fontsize=9)
        else:
            ax.axvline(0.10, color=MUTED, lw=1, ls="--")
            ax.text(0.105, 0.04, "目前硬門檻 VAF ≥ 0.10", color=MUTED, fontsize=9)
        ax.set_title(title, loc="left", fontsize=13, color=INK, weight="bold")
        ax.set_xlabel(xlab, color=MUTED)
        ax.set_ylim(0, 1.02)
        ax.grid(color=GRID, lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=MUTED)
    axes[0].set_ylabel("被 ClairS 叫出的比例", color=MUTED)
    axes[0].legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle("ClairS 偵測曲線：同一組 SNV 在不同 purity 下被叫出的比例", fontsize=16, weight="bold",
                 x=0.06, ha="left", y=0.97, color=INK)
    fig.text(0.06, 0.885, "位點＝t50_n00 的 31,595 個 ClairS call（當作真 SNV）。線＝比例，色帶＝95% Wilson 區間；少於 20 個位點的格子不畫。",
             fontsize=10, color=MUTED)
    out = Path(curve_dir) / "detection_curve.png"
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:3])
