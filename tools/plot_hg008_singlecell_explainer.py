#!/usr/bin/env python3
"""Background figure: how the 119 HG008 single cells were sequenced, and what they add over the 8 clones.

Facts (2026-11-11):
  GIAB README_Bioskryb-Ultima.md (copy at /big8_disk/boyu114/benchmark_data/GIAB/HG008/single_cell_vcf/):
    cells = MGH batch 0823p23 (passage 23); BioSkryb made 120 ResolveDNA single-cell libraries; the same
    libraries were converted for Ultima UG100, single-end 300 bp; 119/120 passed QC; GRCh38 CRAM + VCF.
  GIAB README_Bioskryb.md (Liss_lab/Bioskryb_ResolveDNA_20230914): snap-frozen cells, 120 cells,
    low-pass sequencing, CNV with Ginkgo at 1 Mb bins.
  NIST_Bioskryb_QC_measures.csv: mean coverage 12.1-47.6x, median 23.1x.
  VCF header: DeepVariant 1.4.0, VEP annotation, PASS-filtered.
  sc check: lab_report/2026-11-07_hg008_sc_check/README.md (111 / 48 / 16 / 8 cells).
Usage: python3 tools/plot_hg008_singlecell_explainer.py OUT.png
"""
import math
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

# matplotlib reads NotoSansCJK.ttc as its first face (JP); it covers the traditional characters used here.
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, INK2, MUTED = "#1F2A37", "#46574F", "#7A8A82"
PAPER, PANEL, EDGE = "#F6F4EE", "#FFFFFF", "#D9D4C7"
GREY, RED, PURPLE, GOLD = "#8A9A91", "#D23A2E", "#8456C4", "#D8A31E"
HAP1, HAP2, TEAL, BLUE, OK, BAD = "#3F7CAC", "#E08A3C", "#6F8F84", "#3F7CAC", "#2E8B57", "#C0392B"

fig = plt.figure(figsize=(24, 13.5), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 240)
ax.set_ylim(0, 135)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(PAPER)


def text(x, y, s, size=15, color=INK, weight="normal", ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, **kw)


def helix(x0, x1, y, amp, turns, alpha=1.0, lw=2.0, rungs=True, z=1):
    n = 300
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for phase, col in ((0, HAP1), (math.pi, HAP2)):
        ys = [y + amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0) + phase) for x in xs]
        ax.plot(xs, ys, color=col, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z)
    if rungs:
        for i in range(int(turns * 6) + 1):
            x = x0 + (x1 - x0) * i / (turns * 6)
            a = amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0))
            ax.plot([x, x], [y + a, y - a], color=MUTED, lw=lw * 0.5, alpha=alpha * 0.6, zorder=z - 1)


def panel(x0, y0, w, h, num, title, fc=PANEL):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                fc=fc, ec=EDGE, lw=1.6, zorder=1))
    if num is not None:
        ax.add_patch(Circle((x0 + 3.6, y0 + h - 3.6), 2.6, fc=INK, ec="none", zorder=3))
        text(x0 + 3.6, y0 + h - 3.6, str(num), 15, "#FFFFFF", "bold", zorder=4)
    text(x0 + (7.6 if num is not None else 3.0), y0 + h - 3.6, title, 17, INK, "bold", ha="left", zorder=4)


def cell(x, y, r, color, fill_alpha=0.3, nucleus=True, z=3, ls="-"):
    ax.add_patch(Circle((x, y), r, fc="none", ec=color, lw=1.2, zorder=z, ls=ls))
    ax.add_patch(Circle((x, y), r, fc=color, ec="none", alpha=fill_alpha, zorder=z))
    if nucleus:
        ax.add_patch(Circle((x + r * 0.15, y + r * 0.1), r * 0.38, fc=color, ec="none", alpha=0.8, zorder=z + 1))


def star(x, y, s=160, color=RED, alpha=1.0, z=6):
    ax.scatter([x], [y], marker="*", s=s, c=color, alpha=alpha, edgecolors="none", zorder=z)


def arrow(x0, y0, x1, y1, color=MUTED, lw=2.6, rad=0.0, z=2, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=26, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z, linestyle=ls))


def flask(x, y, w, h, z=2):
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h * 0.72), (x + w * 0.62, y + h * 0.82),
                          (x + w * 0.62, y + h), (x + w * 0.38, y + h), (x + w * 0.38, y + h * 0.82),
                          (x, y + h * 0.72)], closed=True, fc="#F1F6F4", ec=MUTED, lw=2.0, zorder=z))
    ax.add_patch(Rectangle((x + w * 0.34, y + h), w * 0.32, h * 0.08, fc="#C9D3CF", ec=MUTED, lw=1.6, zorder=z))


def mixed_cells(x0, y0, w, h, r, seed, n_each=(4, 3, 2, 2)):
    rnd = random.Random(seed)
    for col, n in zip((RED, PURPLE, GOLD, GREY), n_each):
        for _ in range(n):
            cell(x0 + rnd.random() * w, y0 + rnd.random() * h, r, col, 0.35, r > 0.7, z=4)


def check(x, y, s=1.0, color=OK):
    ax.plot([x - 1.4 * s, x - 0.3 * s, x + 1.7 * s], [y, y - 1.2 * s, y + 1.4 * s], color=color, lw=4 * s,
            solid_capstyle="round", zorder=6)


def minus(x, y, s=1.0, color=BAD):
    ax.plot([x - 1.4 * s, x + 1.4 * s], [y, y], color=color, lw=4 * s, solid_capstyle="round", zorder=6)


# ---------------------------------------------------------------- frame
helix(4, 236, 130.3, 1.5, 14, alpha=0.18, lw=2.2)
helix(4, 236, 3.2, 1.2, 16, alpha=0.14, lw=2.0)
text(5, 124.2, "119 顆單細胞怎麼定序出來", 30, INK, "bold", ha="left")
text(96, 124.0, "一顆細胞只有一份 DNA，要先放大才能定序", 18, INK2, ha="left")

TOP, H = 64, 54
# ---------------------------------------------------------------- 1 cells
panel(3, TOP, 30, H, 1, "細胞株")
flask(8, TOP + 15, 20, 25)
mixed_cells(10.5, TOP + 17.5, 15, 12, 1.0, 1)
text(18, TOP + 9.8, "MGH 第 23 代", 14, INK, "bold")
text(18, TOP + 5.8, "冷凍細胞", 12.5, MUTED)

# ---------------------------------------------------------------- 2 separate single cells
X2 = 37
panel(X2, TOP, 36, H, 2, "一顆一顆分開")
for r in range(4):
    for c in range(5):
        cx, cy = X2 + 7 + c * 5.6, TOP + 37 - r * 6.4
        ax.add_patch(Circle((cx, cy), 2.3, fc="#FFFFFF", ec=EDGE, lw=1.1, zorder=3))
        col = (RED, PURPLE, GOLD, GREY, RED)[(r * 5 + c) % 5 if (r + c) % 3 else 0]
        cell(cx, cy, 1.0, col, 0.4, True, z=4)
text(X2 + 18, TOP + 9.8, "1 孔 1 顆細胞", 14, INK, "bold")
text(X2 + 18, TOP + 5.8, "共 120 顆", 12.5, MUTED)

# ---------------------------------------------------------------- 3 PTA amplification
X3 = 77
panel(X3, TOP, 40, H, 3, "放大 DNA（PTA）")
cell(X3 + 7.5, TOP + 30, 4.2, RED, 0.12, False)
helix(X3 + 4.6, X3 + 10.4, TOP + 30, 0.9, 1, lw=1.8, rungs=False, z=5)
arrow(X3 + 12.5, TOP + 30, X3 + 17.5, TOP + 30)
for i in range(7):
    y = TOP + 42 - i * 3.0
    helix(X3 + 19.5, X3 + 36, y, 0.75, 2, lw=1.5, rungs=False, z=3, alpha=1.0 if i != 4 else 0.25)
star(X3 + 30.0, TOP + 36.0, 120, RED)
ax.add_patch(Rectangle((X3 + 19.0, TOP + 29.2), 17.5, 1.6, fc="none", ec=BAD, lw=1.4, ls=(0, (2, 2)), zorder=4))
text(X3 + 7.5, TOP + 22.5, "1 份", 13, INK2, "bold")
text(X3 + 28, TOP + 18.6, "很多份", 13, INK2, "bold")
text(X3 + 20, TOP + 9.8, "BioSkryb ResolveDNA", 13, INK, "bold")
text(X3 + 20, TOP + 5.8, "有的片段放大失敗（漏測）", 12.5, BAD)

# ---------------------------------------------------------------- 4 two sequencing runs
X4 = 121
panel(X4, TOP, 52, H, 4, "同一批 library 定序兩次")
# low-pass branch (not downloaded)
ly, hy = TOP + 36, TOP + 18
arrow(X4 + 4, (ly + hy) / 2, X4 + 10, ly, rad=-0.2)
arrow(X4 + 4, (ly + hy) / 2, X4 + 10, hy, rad=0.2)
for i in range(6):
    ax.add_patch(Rectangle((X4 + 11 + i * 2.2, ly - 1.2 + (i % 2) * 0.6), 1.6, 0.9, fc=GREY, ec="none", zorder=3))
text(X4 + 33, ly + 2.0, "低深度 Illumina", 13, INK2, "bold", ha="left")
text(X4 + 33, ly - 2.2, "→ 每顆的拷貝數", 12.5, MUTED, ha="left")
text(X4 + 33, ly - 6.0, "（本機沒下載）", 11.5, MUTED, ha="left")
for k in range(4):
    for i in range(8):
        ax.add_patch(Rectangle((X4 + 11 + i * 2.6, hy + 2.2 - k * 1.6), 2.3, 0.9, fc=TEAL, ec="none", zorder=3))
text(X4 + 33, hy + 2.0, "Ultima UG100", 13, INK, "bold", ha="left")
text(X4 + 33, hy - 2.2, "short read · 約 23×", 12.5, INK2, ha="left")
text(X4 + 33, hy - 6.0, "119 顆通過品管", 12.5, INK2, ha="left")
text(X4 + 26, TOP + 5.8, "我們用的是下面這一路", 12.5, MUTED)

# ---------------------------------------------------------------- 5 variant calling and our query
X5 = 177
panel(X5, TOP, 60, H, 5, "找突變，再對照樹")
for i in range(3):
    ax.add_patch(FancyBboxPatch((X5 + 5 + i * 1.4, TOP + 25 - i * 1.4), 13, 15, boxstyle="round,pad=0,rounding_size=1",
                                fc="#FFFFFF", ec=MUTED, lw=1.4, zorder=3 + i))
for j in range(5):
    ax.add_patch(Rectangle((X5 + 9.2, TOP + 34.0 - j * 2.3), 8.0, 0.8, fc=EDGE, ec="none", zorder=7))
text(X5 + 13.0, TOP + 18.4, "每顆 1 個 VCF", 12.5, INK2, "bold")
text(X5 + 13.0, TOP + 15.2, "DeepVariant", 12, MUTED)
arrow(X5 + 23, TOP + 28, X5 + 29, TOP + 28)
# tree SNV lookup: stars vs a cell
for j, col in enumerate((GREY, RED, PURPLE, GOLD)):
    star(X5 + 33 + j * 5.2, TOP + 38, 260, col)
cell(X5 + 40.8, TOP + 26.5, 5.4, PURPLE, 0.15, False)
for j, (col, has) in enumerate(((GREY, True), (RED, True), (PURPLE, True), (GOLD, False))):
    x = X5 + 37.6 + j * 2.15
    if has:
        star(x, TOP + 26.5, 120, col)
    else:
        ax.add_patch(Circle((x, TOP + 26.5), 0.8, fc="none", ec=EDGE, lw=1.4, zorder=6))
text(X5 + 52, TOP + 30.0, "帶紅、紫", 12.5, INK2, "bold", ha="left")
text(X5 + 52, TOP + 26.4, "不帶金", 12.5, INK2, "bold", ha="left")
text(X5 + 30, TOP + 9.8, "每顆細胞帶不帶每個分支", 13.5, INK, "bold")
text(X5 + 30, TOP + 5.8, "（我們的分析）", 12.5, MUTED)

for x0, x1 in ((33, 37), (73, 77), (117, 121), (173, 177)):
    arrow(x0 + 0.2, TOP + H / 2, x1 - 0.2, TOP + H / 2)

# ---------------------------------------------------------------- bottom: compared with the 8 clones
BOT, HB = 7, 52
panel(3, BOT, 234, HB, None, "比 8 株選殖株多了什麼、少了什麼")
COLX = (60, 112, 188)  # icon column for clones, icon column for single cells, verdict text
text(COLX[0], BOT + 41.4, "8 株選殖株", 14, MUTED, "bold")
text(COLX[1], BOT + 41.4, "119 顆單細胞", 14, MUTED, "bold")
rows_y = (BOT + 33.5, BOT + 24.5, BOT + 15.5, BOT + 6.5)
labels = ("個數", "怎麼放大", "培養路線", "代價")
for y, lab in zip(rows_y, labels):
    text(8, y, lab, 14.5, INK, "bold", ha="left")
    ax.plot([7, 233], [y + 4.5, y + 4.5], color=EDGE, lw=1.0, zorder=2)

# row 1: count -> proportions
y = rows_y[0]
for i, col in enumerate((RED, RED, GREY, RED, PURPLE, GOLD, PURPLE, GOLD)):
    cell(COLX[0] - 12.6 + i * 3.6, y, 1.3, col, 0.35, False)
rnd = random.Random(4)
seq = [GREY] * 1 + [RED] * 8 + [PURPLE] * 4 + [GOLD] * 2
for i, col in enumerate(seq):
    cell(COLX[1] - 15.4 + i * 2.2, y, 0.85, col, 0.35, False)
text(COLX[1] + 18.5, y, "…", 15, MUTED)
check(150, y, 0.8)
text(155, y + 0.2, "看得到比例：111 顆帶紅色分支，8 顆在灰色那側", 14, INK, ha="left")

# row 2: amplification
y = rows_y[1]
cell(COLX[0] - 10, y, 1.3, RED, 0.4)
arrow(COLX[0] - 7.6, y, COLX[0] - 3.6, y)
for i in range(6):
    cell(COLX[0] + 0.6 + (i % 3) * 2.8, y + (2.0 if i < 3 else -0.6), 1.1, RED, 0.35, False)
star(COLX[0] + 6.2, y - 0.6, 90, "#2B2B2B", z=8)
text(COLX[0], y - 3.3, "細胞分裂長成一株（★ 新突變）", 11, MUTED)
cell(COLX[1] - 10, y, 1.3, RED, 0.4)
arrow(COLX[1] - 7.6, y, COLX[1] - 3.6, y)
for i in range(3):
    helix(COLX[1] - 2.0, COLX[1] + 8.0, y + 2.2 - i * 1.4, 0.45, 1.5, lw=1.2, rungs=False, z=3)
text(COLX[1], y - 3.3, "只放大 DNA，細胞不分裂", 11, MUTED)
check(150, y, 0.8)
text(155, y + 0.2, "沒有擴增期間新長出的突變（選殖株的 ★ 有一部分是這樣來的）", 14, INK, ha="left")

# row 3: culture line
y = rows_y[2]
ax.plot([COLX[0] - 10, COLX[0] + 10], [y, y], color=TEAL, lw=3, solid_capstyle="round")
text(COLX[0], y - 2.8, "NIST · 第 14、19 代 · PacBio", 11.5, TEAL)
ax.plot([COLX[1] - 10, COLX[1] + 10], [y, y], color=BLUE, lw=3, solid_capstyle="round")
text(COLX[1], y - 2.8, "MGH · 第 23 代 · Ultima", 11.5, BLUE)
check(150, y, 0.8)
text(155, y + 0.2, "不同培養、不同平台：能排除選殖株的批次假象", 14, INK, ha="left")

# row 4: costs
y = rows_y[3]
minus(150, y, 0.8)
text(155, y + 0.2, "放大會漏測和出錯；short read 不能定相 HP；「沒 call」≠「沒突變」", 14, BAD, ha="left")
for i, a in enumerate((1.0, 1.0, 0.25, 1.0, 0.25, 1.0)):
    star(COLX[1] - 6 + i * 2.6, y, 120, RED, alpha=a)
text(COLX[1] + 10.5, y, "漏測", 12, BAD, ha="left")
for i in range(6):
    star(COLX[0] - 6 + i * 2.6, y, 120, RED)
text(COLX[0] + 10.5, y, "深、long read", 12, MUTED, ha="left")

fig.savefig(sys.argv[1], dpi=150, facecolor=PAPER)
