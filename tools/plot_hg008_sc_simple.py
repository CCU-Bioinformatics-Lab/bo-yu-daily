#!/usr/bin/env python3
"""Simple figure: which clone group each of the 119 HG008 single cells falls into (2026-11-12).

Each cell goes to the deepest branch it carries (carrier = rel >= 0.5, tools/hg008_sc_clade_test.py:4-7):
no 127-SNV branch -> H; 127 but not 14 -> G+A+B; 14 but not 68 -> E+F; 68 -> C+D.
Cells with 0.2 < rel < 0.5 on a branch stay one level up (4 cells; listed in the footnote).
Data: lab_report/2026-11-07_hg008_sc_check/tables/cell_by_branch.tsv.
Letters: A 2D6, B 2E6, C SC14, D SC28, E SC24, F SC9, G SC6, H 3E4 (report/2026_11_11_slides/BRIEF.md).

Usage: python3 tools/plot_hg008_sc_simple.py CELL_BY_BRANCH.tsv OUT.png
"""
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED = "#1F2A37", "#7A8A82"
PAPER, PANEL, EDGE = "#F6F4EE", "#FFFFFF", "#D9D4C7"
GREY, RED, PURPLE, GOLD, ROOT = "#8A9A91", "#D23A2E", "#8456C4", "#D8A31E", "#46574F"
B127, B14, B68 = "2D6,2E6,SC14,SC24,SC28,SC6,SC9", "SC14,SC24,SC28,SC9", "SC14,SC28"

counts = {"H": 0, "GAB": 0, "EF": 0, "CD": 0}
border = []
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    a, b, d = (float(r[k]) for k in (B127, B14, B68))
    g = "CD" if d >= 0.5 else "EF" if b >= 0.5 else "GAB" if a >= 0.5 else "H"
    counts[g] += 1
    if any(0.2 < v < 0.5 for v in (a, b, d)):
        border.append(r["cell"])
assert sum(counts.values()) == 119, counts

fig = plt.figure(figsize=(24, 13.5), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 240)
ax.set_ylim(0, 135)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(PAPER)


def text(x, y, s, size=16, color=INK, weight="normal", ha="center", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, zorder=6)


def box(x, y, w, h, fc=PANEL, ec=EDGE, lw=1.8, z=2):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def line(pts, color, lw=4):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)


def arrow(x0, y0, x1, y1, color=MUTED):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=22, color=color,
                                 lw=2.4, zorder=3))


def cells(x, y, n, color, cols=8, r=1.05, gap=2.7):
    rows = (n + cols - 1) // cols
    for i in range(n):
        cx = x + (i % cols - (min(n, cols) - 1) / 2) * gap
        cy = y - (i // cols - (rows - 1) / 2) * gap
        ax.add_patch(Circle((cx, cy), r, fc=color, ec="none", alpha=0.85, zorder=4))


text(6, 125, "119 顆單細胞，各落在哪一群 clone？", 30, weight="bold", ha="left")
text(6, 118, "樹由 8 株選殖株排出；單細胞是另一批獨立的資料，只拿來檢查", 16, MUTED, ha="left")

# ---------------- left: the tree, each group with its cells ----------------
box(76, 57, 148, 104, z=0)
ry = 99
box(76, ry, 44, 10, fc="#EEF1EE", ec=ROOT)
text(76, ry + 1.8, "共同祖先", 17, weight="bold")
text(76, ry - 2.4, "7,784 個突變，每顆細胞都有", 13, MUTED)

leaf_y, ny1, ny2, ny3 = 38, 84, 72, 64
X = {"H": 22, "GAB": 58, "EF": 97, "CD": 131}
n1x, n2x = 96, 114
line([(76, ry - 5), (76, ny1 + 4), (X["H"], ny1 + 4), (X["H"], leaf_y + 17)], GREY)
line([(76, ny1 + 4), (n1x, ny1 + 4), (n1x, ny2 + 4)], RED)
line([(n1x, ny2 + 4), (X["GAB"], ny2 + 4), (X["GAB"], leaf_y + 17)], RED)
line([(n1x, ny2 + 4), (n2x, ny2 + 4), (n2x, ny3)], PURPLE)
line([(n2x, ny3), (X["EF"], ny3), (X["EF"], leaf_y + 17)], PURPLE)
line([(n2x, ny3), (X["CD"], ny3), (X["CD"], leaf_y + 17)], GOLD)


def tag(x, y, s, color):
    box(x, y, len(s) * 1.75 + 4, 5.4, fc=PANEL, ec=color, lw=2.2, z=5)
    text(x, y, s, 14, color, "bold")


tag(n1x + 0.5, ny1 - 1.5, "+127 個突變", RED)
tag(n2x + 1, ny2 - 1.5, "+14 個", PURPLE)
tag(X["CD"], ny3 - 4.5, "+68 個", GOLD)
text(X["H"] + 1.5, ny1 - 2, "沒有那 127 個", 13, GREY, ha="left")

LEAF = [("H", "H", "3E4", GREY), ("GAB", "G A B", "SC6、2D6、2E6", RED),
        ("EF", "E F", "SC24、SC9", PURPLE), ("CD", "C D", "SC14、SC28", GOLD)]
for key, name, clones, col in LEAF:
    x = X[key]
    box(x, leaf_y - 3, 31, 40, ec=col, lw=2.4)
    text(x, leaf_y + 13.5, name, 20, col, "bold")
    text(x, leaf_y + 9, clones, 12, MUTED)
    text(x, leaf_y + 2.5, f"{counts[key]} 顆", 30, col, "bold")
    cells(x, leaf_y - 13, counts[key], col, cols=10, r=0.95, gap=2.6)
text(76, 9, f"{counts['H']} ＋ {counts['GAB']} ＋ {counts['EF']} ＋ {counts['CD']} ＝ 119 顆　｜　"
             "共同祖先是第 5 群，樣本裡沒有細胞", 15, INK, "bold")

# ---------------- right: three yes/no questions ----------------
box(196, 57, 80, 104, z=0)
text(160, 101, "一顆細胞怎麼分群：問三題", 19, weight="bold", ha="left")
Q = [(86, "有那 127 個突變嗎？", RED, "H", GREY), (66, "有那 14 個突變嗎？", PURPLE, "G A B", RED),
     (46, "有那 68 個突變嗎？", GOLD, "E F", PURPLE)]
for y, q, col, no, nocol in Q:
    box(184, y, 40, 9, ec=col, lw=2.4)
    text(184, y, q, 16, col, "bold")
    arrow(204.5, y, 214, y)
    text(209, y + 2.4, "沒有", 12, MUTED)
    box(222, y, 14, 7, fc=PANEL, ec=nocol, lw=2.2)
    text(222, y, no, 15, nocol, "bold")
    arrow(184, y - 4.8, 184, y - 15.2)
    text(186.5, y - 10, "有", 12, MUTED, ha="left")
box(184, 26, 14, 7, fc=PANEL, ec=GOLD, lw=2.2)
text(184, 26, "C D", 15, GOLD, "bold")

text(160, 16, "「有」＝ 測到的比例 ≥ 這顆細胞平均偵測率的一半", 13, INK, ha="left")
text(160, 11.5, "（單細胞會漏測約 1 成，所以不要求全部測到）", 12, MUTED, ha="left")
text(160, 7, f"邊界的 {len(border)} 顆（{'、'.join(border)}）放在上一層", 12, MUTED, ha="left")

fig.savefig(sys.argv[2], dpi=150, facecolor=PAPER)
print(counts, border)
