#!/usr/bin/env python3
"""Detail figure for step 5 of the HG008 tree, drawn as a series of knife cuts (2026-11-11).

How the program works (tools/hg008_tree_rebuild.py best_laminar, lines 104-136): for every set of
clones it tries every way to cut it in two, scores each piece by the CN-clean SNVs whose "which clones
have it" group equals that piece, and keeps the cuts with the highest total. The figure shows the
chosen cuts one by one; the program compares all cut sequences at once.
Numbers: tables/pattern_summary_vaf0.25_qual20.tsv (n_cn_clean) and tree_summary.tsv (261 / 301).
Letters: A 2D6, B 2E6, C SC14, D SC28, E SC24, F SC9, G SC6, H 3E4 (report/2026_11_11_slides/BRIEF.md).

Usage: python3 tools/plot_hg008_tree_ordering.py OUT.png
"""
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon

# matplotlib reads NotoSansCJK.ttc as its first face (JP); it covers the traditional characters used here.
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, INK2, MUTED = "#1F2A37", "#46574F", "#7A8A82"
PAPER, PANEL, EDGE = "#F6F4EE", "#FFFFFF", "#D9D4C7"
GREY, RED, PURPLE, GOLD = "#8A9A91", "#D23A2E", "#8456C4", "#D8A31E"
HAP1, HAP2, OK, BAD, STEEL = "#3F7CAC", "#E08A3C", "#2E8B57", "#C0392B", "#5B6770"
LEAVES = "HGABEFCD"
COLOR = {"H": GREY, "G": RED, "A": RED, "B": RED, "E": PURPLE, "F": PURPLE, "C": GOLD, "D": GOLD}

fig = plt.figure(figsize=(24, 13.5), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 240)
ax.set_ylim(0, 135)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(PAPER)


def text(x, y, s, size=15, color=INK, weight="normal", ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, **kw)


def helix(x0, x1, y, amp, turns, alpha=1.0, lw=2.0):
    n = 300
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for phase, col in ((0, HAP1), (math.pi, HAP2)):
        ys = [y + amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0) + phase) for x in xs]
        ax.plot(xs, ys, color=col, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)
    for i in range(int(turns * 6) + 1):
        x = x0 + (x1 - x0) * i / (turns * 6)
        a = amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0))
        ax.plot([x, x], [y + a, y - a], color=MUTED, lw=lw * 0.5, alpha=alpha * 0.6, zorder=0)


def panel(x0, y0, w, h, title):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                fc=PANEL, ec=EDGE, lw=1.6, zorder=1))
    text(x0 + 3.0, y0 + h - 3.6, title, 17, INK, "bold", ha="left", zorder=4)


def star(x, y, s=160, color=RED, alpha=1.0, z=6):
    ax.scatter([x], [y], marker="*", s=s, c=color, alpha=alpha, edgecolors="none", zorder=z)


def badge(x, y, n, color):
    star(x - 2.0, y, 230, color)
    text(x - 0.4, y, n, 15, color, "bold", ha="left")


def knife(x, y, s=1.0):
    """A kitchen knife pointing down, tip at (x, y)."""
    blade = [(x, y), (x + 1.5 * s, y + 6.5 * s), (x + 1.5 * s, y + 8.2 * s), (x - 0.4 * s, y + 8.2 * s),
             (x - 0.4 * s, y + 1.4 * s)]
    ax.add_patch(Polygon(blade, closed=True, fc="#DDE3E6", ec=STEEL, lw=1.6, zorder=7))
    ax.add_patch(FancyBboxPatch((x - 0.6 * s, y + 8.2 * s), 2.3 * s, 0.7 * s, boxstyle="round,pad=0,rounding_size=0.2",
                                fc=STEEL, ec="none", zorder=7))
    ax.add_patch(FancyBboxPatch((x - 0.15 * s, y + 8.9 * s), 1.4 * s, 4.4 * s, boxstyle="round,pad=0,rounding_size=0.6",
                                fc="#7B5E45", ec="none", zorder=7))


def cross(x, y, s=1.0, color=BAD):
    for d in (1, -1):
        ax.plot([x - 1.3 * s, x + 1.3 * s], [y - 1.3 * s * d, y + 1.3 * s * d], color=color, lw=4 * s,
                solid_capstyle="round", zorder=6)


# ---------------------------------------------------------------- frame
helix(4, 236, 130.3, 1.5, 14, alpha=0.18, lw=2.2)
helix(4, 236, 3.2, 1.2, 16, alpha=0.14, lw=2.0)
text(5, 124.2, "第 ⑤ 步：一刀一刀切出樹", 30, INK, "bold", ha="left")
text(92, 124.0, "每一刀把一群株切成兩半；切口要有 SNV 支持：一半都有、另一半都沒有", 18, INK2, ha="left")

# ---------------------------------------------------------------- left: the cuts
panel(3, 7, 149, 111, "照 SNV 支持的地方下刀")
CW, GAP, LX = 7.0, 0.6, 31.0
xs = {k: LX + j * (CW + GAP) for j, k in enumerate(LEAVES)}
# (group being cut, left piece, right piece, supports: [(piece, n, color)], text lines)
CUTS = [("HGABEFCD", "H", "GABEFCD", [("GABEFCD", "127", RED)],
         ["除了 H，其他 7 株都有的 SNV：127 個", "→ 先把 H 切出去"]),
        ("GABEFCD", "G", "ABEFCD", [("ABEFCD", "4", RED)],
         ["除了 H、G，6 株都有：4 個", "→ 再切出 G（最弱的一刀）"]),
        ("ABEFCD", "AB", "EFCD", [("AB", "31", RED), ("EFCD", "14", PURPLE)],
         ["只有 A、B 有：31 個；只有 E、F、C、D 有：14 個", "→ 兩邊都有支持，從中間切"]),
        ("EFCD", "EF", "CD", [("EF", "17", PURPLE), ("CD", "68", GOLD)],
         ["只有 E、F 有：17 個；只有 C、D 有：68 個", "→ 切成兩對"])]
offset = {k: 0.0 for k in LEAVES}   # pieces drift apart a little more with every cut
for i, (group, left, right, supports, lines) in enumerate(CUTS):
    y = 92.0 - i * 22.5
    for k in group:
        offset[k] += -1.1 if k in left else 1.1
    ax.add_patch(Circle((9.5, y + 3.5), 3.0, fc=INK, ec="none", zorder=3))
    text(9.5, y + 3.5, str(i + 1), 16, "#FFFFFF", "bold", zorder=4)
    text(9.5, y - 1.8, "第 %d 刀" % (i + 1), 12.5, INK2, "bold")
    for k in LEAVES:
        active = k in group
        x = xs[k] + offset[k]
        ax.add_patch(FancyBboxPatch((x, y), CW, CW, boxstyle="round,pad=0,rounding_size=0.8",
                                    fc=COLOR[k], ec="none", alpha=1.0 if active else 0.18, zorder=3))
        text(x + CW / 2, y + CW / 2, k, 15, "#FFFFFF", "bold", alpha=1.0 if active else 0.6, zorder=4)
    lk, rk = left[-1], right[0]
    cut_x = (xs[lk] + offset[lk] + CW + xs[rk] + offset[rk]) / 2
    ax.plot([cut_x, cut_x], [y - 1.6, y + CW + 1.6], color=BAD, lw=2.6, ls=(0, (3, 2)), zorder=5)
    knife(cut_x, y + CW + 1.8, 0.9)
    for piece, n, col in supports:
        px = sum(xs[k] + offset[k] for k in piece) / len(piece) + CW / 2
        badge(px, y + CW + 3.4, n, col)
    text(LX + 8 * (CW + GAP) + 8.0, y + 5.4, lines[0], 13.5, INK, "bold", ha="left")
    text(LX + 8 * (CW + GAP) + 8.0, y + 1.4, lines[1], 13, INK2, ha="left")
text(77.5, 12.0, "剩下的 A｜B、E｜F、C｜D 是最後一層，每株自己的 SNV 不影響怎麼切", 13, MUTED)

# ---------------------------------------------------------------- right top: cuts = tree
panel(156, 47, 81, 71, "切完就是樹")
TX, TW = 163.0, 68.0
lx = {k: TX + TW * (j + 0.5) / 8 for j, k in enumerate(LEAVES)}
yl = 59.0
ab, ef, cd = (lx["A"] + lx["B"]) / 2, (lx["E"] + lx["F"]) / 2, (lx["C"] + lx["D"]) / 2
cdef = (ef + cd) / 2
six = (ab + cdef) / 2
seven = (lx["G"] + six) / 2
root = (lx["H"] + seven) / 2
Y = [yl + 45, yl + 36, yl + 27, yl + 18, yl + 9]
segs = [((root, Y[0]), (lx["H"], yl), GREY), ((root, Y[0]), (seven, Y[1]), RED),
        ((seven, Y[1]), (lx["G"], yl), RED), ((seven, Y[1]), (six, Y[2]), RED),
        ((six, Y[2]), (ab, Y[4]), RED), ((six, Y[2]), (cdef, Y[3]), PURPLE),
        ((ab, Y[4]), (lx["A"], yl), RED), ((ab, Y[4]), (lx["B"], yl), RED),
        ((cdef, Y[3]), (ef, Y[4]), PURPLE), ((cdef, Y[3]), (cd, Y[4]), GOLD),
        ((ef, Y[4]), (lx["E"], yl), PURPLE), ((ef, Y[4]), (lx["F"], yl), PURPLE),
        ((cd, Y[4]), (lx["C"], yl), GOLD), ((cd, Y[4]), (lx["D"], yl), GOLD)]
for (a, b), (c, d), col in segs:
    ax.plot([a, c, c], [b, b, d], color=col, lw=3.0, solid_capstyle="round", zorder=3)
for num, (x, y) in enumerate(((root, Y[0]), (seven, Y[1]), (six, Y[2]), (cdef, Y[3])), start=1):
    ax.add_patch(Circle((x, y), 2.0, fc=INK, ec="#FFFFFF", lw=1.5, zorder=6))
    text(x, y, str(num), 12, "#FFFFFF", "bold", zorder=7)
for x, y, n, col in ((seven, Y[1], "127", RED), (six, Y[2], "4", RED), (ab, Y[4], "31", RED),
                     (cdef, Y[3], "14", PURPLE), (ef, Y[4], "17", PURPLE), (cd, Y[4], "68", GOLD)):
    star(x + 2.6, y + 2.2, 120, col)
    text(x + 3.8, y + 2.2, n, 11.5, col, "bold", ha="left")
for k, x in lx.items():
    ax.add_patch(Circle((x, yl - 2.4), 2.1, fc=COLOR[k], ec="none", zorder=4))
    text(x, yl - 2.4, k, 11.5, "#FFFFFF", "bold", zorder=5)
text(196.5, 51.0, "黑圈數字 = 第幾刀；★ 數字 = 支持的 SNV 數", 12, MUTED)

# ---------------------------------------------------------------- right bottom: a bad cut
panel(156, 7, 81, 36, "為什麼不先切 A｜其他？")
BX, BC = 160.5, 5.0
bx = {k: BX + j * (BC + 0.4) for j, k in enumerate(LEAVES)}
by = 23.0
for k in LEAVES:
    shift = -0.7 if k in "HGA" else 0.7
    ax.add_patch(FancyBboxPatch((bx[k] + shift, by), BC, BC, boxstyle="round,pad=0,rounding_size=0.6",
                                fc=COLOR[k], ec="none", zorder=3))
    text(bx[k] + shift + BC / 2, by + BC / 2, k, 12, "#FFFFFF", "bold", zorder=4)
cx = bx["A"] + BC + 0.2
ax.plot([cx, cx], [by - 1.2, by + BC + 1.2], color=BAD, lw=2.4, ls=(0, (3, 2)), zorder=5)
knife(cx, by + BC + 1.3, 0.45)
text(BX, 18.2, "除了 A 都有：6 個", 13, INK, "bold", ha="left")
text(BX, 14.6, "但它把 A、B 拆開，A、B 共有的 31 個就放不進樹", 12.5, BAD, ha="left")
cross(206.0, by + 2.5, 0.9)
text(210.0, by + 4.2, "6 < 31", 15, BAD, "bold", ha="left")
text(210.0, by + 0.6, "不切", 13, BAD, "bold", ha="left")
text(BX, 10.2, "程式一次比較所有切法的總分，取最高的 261", 12.5, INK2, "bold", ha="left")

fig.savefig(sys.argv[1], dpi=150, facecolor=PAPER)
