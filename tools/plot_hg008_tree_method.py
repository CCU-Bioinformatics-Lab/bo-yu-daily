#!/usr/bin/env python3
"""Draw how the HG008 reference tree was built, as one pictorial flow figure (2026-11-11).

Steps and numbers follow lab_report/2026-11-07_hg008_tree_rebuild/HOW_TREE_WAS_BUILT.md
(tree_summary.tsv, clades_vaf0.25_qual20.tsv, sc_check branch_summary.tsv). Clone letters follow
report/2026_11_11_slides/BRIEF.md: A 2D6, B 2E6, C SC14, D SC28, E SC24, F SC9, G SC6, H 3E4.

Usage: python3 -I tools/plot_hg008_tree_method.py OUT.png
"""
import math
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

# matplotlib reads NotoSansCJK.ttc as its first face (JP); it covers the traditional characters used here.
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, INK2, MUTED = "#1F2A37", "#46574F", "#7A8A82"
PAPER, PANEL, EDGE = "#F6F4EE", "#FFFFFF", "#D9D4C7"
GREY, RED, PURPLE, GOLD = "#8A9A91", "#D23A2E", "#8456C4", "#D8A31E"
HAP1, HAP2, OK, BAD = "#3F7CAC", "#E08A3C", "#2E8B57", "#C0392B"
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


def helix(x0, x1, y, amp, turns, alpha=1.0, lw=2.0, rungs=True):
    n = 400
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for phase, col in ((0, HAP1), (math.pi, HAP2)):
        ys = [y + amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0) + phase) for x in xs]
        ax.plot(xs, ys, color=col, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)
    if rungs:
        for i in range(int(turns * 6) + 1):
            x = x0 + (x1 - x0) * i / (turns * 6)
            a = amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0))
            ax.plot([x, x], [y + a, y - a], color=MUTED, lw=lw * 0.5, alpha=alpha * 0.6, zorder=0)


def panel(x0, y0, w, h, num=None, title=None):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                fc=PANEL, ec=EDGE, lw=1.6, zorder=1))
    if num is not None:
        ax.add_patch(Circle((x0 + 3.6, y0 + h - 3.6), 2.6, fc=INK, ec="none", zorder=3))
        text(x0 + 3.6, y0 + h - 3.6, str(num), 15, "#FFFFFF", "bold", zorder=4)
    if title:
        text(x0 + (7.6 if num is not None else w / 2), y0 + h - 3.6, title, 17, INK, "bold",
             ha="left" if num is not None else "center", zorder=4)


def cell(x, y, r, color, fill_alpha=0.25, nucleus=True, ls="-", z=3):
    ax.add_patch(Circle((x, y), r, fc=color, ec=color, lw=1.2, alpha=1, zorder=z, ls=ls,
                        fill=False))
    ax.add_patch(Circle((x, y), r, fc=color, ec="none", alpha=fill_alpha, zorder=z))
    if nucleus:
        ax.add_patch(Circle((x + r * 0.15, y + r * 0.1), r * 0.38, fc=color, ec="none", alpha=0.75, zorder=z + 1))


def star(x, y, s=180, color=RED, alpha=1.0, z=5):
    ax.scatter([x], [y], marker="*", s=s, c=color, alpha=alpha, edgecolors="none", zorder=z)


def arrow(x0, y0, x1, y1, color=MUTED, lw=2.6, rad=0.0, z=2, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=26, color=color,
                                 lw=lw, connectionstyle=f"arc3,rad={rad}", zorder=z, linestyle=ls))


def chromosome(x, y, length, w, color, gap=None, z=3, snv=None):
    """Vertical chromosome with a centromere pinch; gap = (lo, hi) fraction drawn as lost."""
    cen = 0.62
    segs = [(0, cen - 0.04), (cen + 0.04, 1)]
    for lo, hi in segs:
        parts = [(lo, hi)]
        if gap:
            parts = []
            for a, b in ((lo, min(hi, gap[0])), (max(lo, gap[1]), hi)):
                if b > a:
                    parts.append((a, b))
        for a, b in parts:
            ax.add_patch(FancyBboxPatch((x - w / 2, y + a * length), w, (b - a) * length,
                                        boxstyle=f"round,pad=0,rounding_size={w / 2.2}",
                                        fc=color, ec="none", zorder=z))
    ax.add_patch(Ellipse((x, y + cen * length), w * 0.55, length * 0.08, fc=color, ec="none", zorder=z))
    if gap:
        ax.add_patch(Rectangle((x - w / 2, y + gap[0] * length), w, (gap[1] - gap[0]) * length,
                               fc="none", ec=color, lw=1.4, ls=(0, (2, 2)), zorder=z))
    if snv is not None:
        star(x, y + snv * length, 150, "#FFFFFF", z=z + 2)
        star(x, y + snv * length, 70, INK, z=z + 3)


def check(x, y, s=1.0, color=OK):
    ax.plot([x - 1.4 * s, x - 0.3 * s, x + 1.7 * s], [y, y - 1.2 * s, y + 1.4 * s], color=color, lw=4 * s,
            solid_capstyle="round", zorder=6)


def cross(x, y, s=1.0, color=BAD):
    for d in (1, -1):
        ax.plot([x - 1.3 * s, x + 1.3 * s], [y - 1.3 * s * d, y + 1.3 * s * d], color=color, lw=4 * s,
                solid_capstyle="round", zorder=6)


def mini_tree(x0, y0, w, h, lw=2.4, labels=True, alpha=1.0, stars=True, z=3):
    """The 8-leaf candidate tree (H | (G | ((A,B) | ((E,F) | (C,D))))), leaves along the bottom."""
    xs = {k: x0 + w * (i + 0.5) / 8 for i, k in enumerate(LEAVES)}
    yl, step = y0, h / 5
    ab, ef, cd = (xs["A"] + xs["B"]) / 2, (xs["E"] + xs["F"]) / 2, (xs["C"] + xs["D"]) / 2
    cdef = (ef + cd) / 2
    six = (ab + cdef) / 2
    seven = (xs["G"] + six) / 2
    root = (xs["H"] + seven) / 2
    ys = {"root": yl + 5 * step, "seven": yl + 4 * step, "six": yl + 3 * step, "cdef": yl + 2 * step,
          "pair": yl + 1 * step}
    col = dict(c=MUTED, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z)
    segs = [((root, ys["root"]), (xs["H"], yl), GREY), ((root, ys["root"]), (seven, ys["seven"]), RED),
            ((seven, ys["seven"]), (xs["G"], yl), RED), ((seven, ys["seven"]), (six, ys["six"]), RED),
            ((six, ys["six"]), (ab, ys["pair"]), RED), ((six, ys["six"]), (cdef, ys["cdef"]), PURPLE),
            ((ab, ys["pair"]), (xs["A"], yl), RED), ((ab, ys["pair"]), (xs["B"], yl), RED),
            ((cdef, ys["cdef"]), (ef, ys["pair"]), PURPLE), ((cdef, ys["cdef"]), (cd, ys["pair"]), GOLD),
            ((ef, ys["pair"]), (xs["E"], yl), PURPLE), ((ef, ys["pair"]), (xs["F"], yl), PURPLE),
            ((cd, ys["pair"]), (xs["C"], yl), GOLD), ((cd, ys["pair"]), (xs["D"], yl), GOLD)]
    for (a, b), (c, d), color in segs:
        ax.plot([a, c, c], [b, b, d], **{**col, "c": color})
    if stars:
        star((root + seven) / 2, ys["seven"] + 0.4, 160, RED, alpha, z + 2)
        star((six + cdef) / 2, ys["cdef"] + 0.4, 160, PURPLE, alpha, z + 2)
        star(cd, ys["pair"] + step * 0.45, 160, GOLD, alpha, z + 2)
    if labels:
        for k, x in xs.items():
            ax.add_patch(Circle((x, yl - 2.0), 1.5, fc=COLOR[k], ec="none", alpha=alpha, zorder=z))
            text(x, yl - 2.0, k, 10, "#FFFFFF", "bold", zorder=z + 1)
    return ys["root"], root


# ---------------------------------------------------------------- background and title
helix(4, 236, 130.3, 1.5, 14, alpha=0.18, lw=2.2)
helix(4, 236, 3.2, 1.2, 16, alpha=0.14, lw=2.0)
text(5, 124.2, "HG008 參考樹怎麼產生", 30, INK, "bold", ha="left")
text(83, 124.0, "8 株選殖株建樹  ·  119 顆單細胞獨立檢查", 18, INK2, ha="left")

# ---------------------------------------------------------------- row A: clones build the tree
TOP, H = 66, 52
# source: 8 clones
panel(3, TOP, 27, H, title="8 株選殖株")
helix(6, 27, TOP + H - 9.5, 1.3, 3, lw=2.0)
for i, k in enumerate(LEAVES):
    cx, cy = 7.8 + (i % 4) * 6.2, TOP + 27 - (i // 4) * 12
    ax.add_patch(Circle((cx, cy), 2.8, fc="#FBFBF8", ec=EDGE, lw=1.4, zorder=2))
    rnd = random.Random(i)
    for _ in range(5):
        a, r = rnd.random() * 6.28, rnd.random() * 1.6
        ax.add_patch(Circle((cx + r * math.cos(a), cy + r * math.sin(a)), 0.55, fc=COLOR[k], ec="none", zorder=3))
    text(cx, cy - 4.4, k, 13, COLOR[k], "bold")
text(16.5, TOP + 4.2, "PacBio long read", 12, MUTED)

# step 1: presence matrix (rows = SNVs, columns = clones; filled = the clone has the SNV)
X1 = 34
panel(X1, TOP, 23, H, 1, "誰有這個 SNV")
CW, MX = 2.2, X1 + 2.7          # cell size, left edge of the matrix
blocks = [("8 株都有 → 共同祖先", INK2, ["HGABEFCD"] * 3),
          ("部分株有 → 分支", RED, ["GABEFCD", "EFCD", "CD", "AB"]),
          ("1 株有 → private", MUTED, ["H"])]
for j, k in enumerate(LEAVES):   # column header: clone letters
    ax.add_patch(Rectangle((MX + j * CW, TOP + 41.2), CW, CW, fc=COLOR[k], ec=PANEL, lw=1.2, zorder=3))
    text(MX + j * CW + CW / 2, TOP + 41.2 + CW / 2, k, 10, "#FFFFFF", "bold", zorder=4)
y = TOP + 41.2
for label, lcol, rows in blocks:
    y -= 3.0
    text(MX - 0.2, y, label, 11.5, lcol, "bold", ha="left")
    y -= 1.5
    for r in rows:
        y -= CW
        for j, k in enumerate(LEAVES):
            has = k in r
            ax.add_patch(Rectangle((MX + j * CW, y), CW, CW, fc=COLOR[k] if has else "#FFFFFF",
                                   ec=EDGE, lw=1.0, zorder=3))
# legend
ly = TOP + 6.2
ax.add_patch(Rectangle((X1 + 3.0, ly - 1.0), 2.0, 2.0, fc=RED, ec=EDGE, lw=1.0, zorder=3))
text(X1 + 5.8, ly, "有", 12, INK2, ha="left")
ax.add_patch(Rectangle((X1 + 11.0, ly - 1.0), 2.0, 2.0, fc="#FFFFFF", ec=EDGE, lw=1.0, zorder=3))
text(X1 + 13.8, ly, "沒有", 12, INK2, ha="left")
text(X1 + 11.5, TOP + 2.4, "每列 = 1 個 SNV，每欄 = 1 株", 10.5, MUTED)

# step 2: filter funnel
X2 = 60
panel(X2, TOP, 23, H, 2, "去掉弱 call")
ax.add_patch(Polygon([(X2 + 3, TOP + 38), (X2 + 20, TOP + 38), (X2 + 13.2, TOP + 24), (X2 + 13.2, TOP + 15),
                      (X2 + 9.8, TOP + 15), (X2 + 9.8, TOP + 24)], closed=True, fc="#EEF3F1", ec=MUTED, lw=1.8,
                     zorder=2))
rnd = random.Random(7)
for _ in range(16):
    x, y = X2 + 5 + rnd.random() * 13, TOP + 31 + rnd.random() * 6
    ax.add_patch(Circle((x, y), 0.8, fc=RED if rnd.random() < 0.5 else GOLD, ec="none", zorder=3))
for x, y in ((X2 + 11.5, TOP + 21), (X2 + 11.5, TOP + 17.5), (X2 + 11.5, TOP + 12)):
    ax.add_patch(Circle((x, y), 0.8, fc=RED, ec="none", zorder=3))
for x, y in ((X2 + 19.5, TOP + 30), (X2 + 21, TOP + 26)):
    ax.add_patch(Circle((x, y), 0.8, fc=GREY, ec="none", alpha=0.35, zorder=3))
    cross(x, y, 0.55)
text(X2 + 11.5, TOP + 6.8, "VAF ≥ 0.25", 12.5, INK2)
text(X2 + 11.5, TOP + 3.2, "QUAL ≥ 20", 12.5, INK2)

# step 3: group by pattern
X3 = 86
panel(X3, TOP, 23, H, 3, "依株數分組")
groups = [("HGABEFCD", "8 株", "7,784", "共同祖先"), ("GABEFCD", "2–7 株", "1,203", "分支候選"),
          ("C", "1 株", "3,593", "private")]
for i, (pat, lab, n, note) in enumerate(groups):
    y = TOP + 35 - i * 12
    for j, k in enumerate(LEAVES):
        x = X3 + 3.0 + j * 2.3
        if k in pat:
            col = GREY if i == 0 else COLOR[k]
            ax.add_patch(Circle((x, y), 0.95, fc=col, ec="none", zorder=3))
        else:
            ax.add_patch(Circle((x, y), 0.6, fc="none", ec=EDGE, lw=1.0, zorder=3))
    text(X3 + 2.0, y - 4.0, lab, 12, MUTED, ha="left")
    text(X3 + 21.2, y - 4.0, n, 14, INK, "bold", ha="right")

# step 4: copy number check, only for SNVs shared by 2-7 clones (hg008_tree_rebuild.py:80-97).
# Question: a clone without the SNV (B) -- is the absence real, or did B lose that stretch (copy loss / LOH)?
# B must keep both haplotypes with no fewer copies than the carriers (A). Otherwise the SNV is dropped.
# Counts (main setting): dropped 900 (B LOH with A normal 637, both LOH 261, B fewer copies 2), kept 301.
X4 = 112
panel(X4, TOP, 23, H, 4, "拷貝數檢查")
text(X4 + 11.5, TOP + 44.2, "只查 2–7 株共有的 1,203 個", 10.5, INK2, "bold")
text(X4 + 11.5, TOP + 41.7, "8 株都有、1 株有的不決定分支", 9.5, MUTED)
L, W = 7.0, 1.5


def ghost(x, y, length, w, color):
    ax.add_patch(FancyBboxPatch((x - w / 2, y), w, length, boxstyle=f"round,pad=0,rounding_size={w / 2.2}",
                                fc="none", ec=color, lw=1.4, ls=(0, (2, 2)), zorder=3))


cA = X4 + 11.5
text(cA, TOP + 38.6, "A 株有 ★", 11.5, INK, "bold")
chromosome(cA - 1.1, TOP + 29.6, L, W, HAP1, snv=0.3)
chromosome(cA + 1.1, TOP + 29.6, L, W, HAP2)
text(cA, TOP + 27.4, "B 株沒有 ★，為什麼？", 11, INK2, "bold")
cL, cR, yB = X4 + 6.0, X4 + 17.0, TOP + 14.5
arrow(cA - 2.5, TOP + 25.6, cL + 0.5, yB + L + 1.2, color=MUTED, lw=1.8)
arrow(cA + 2.5, TOP + 25.6, cR - 0.5, yB + L + 1.2, color=MUTED, lw=1.8)
# left: B lost the mutated copy -> cannot tell -> dropped
ghost(cL - 1.1, yB, L, W, HAP1)
star(cL - 1.1, yB + 0.3 * L, 70, INK, alpha=0.25, z=6)
chromosome(cL + 1.1, yB, L, W, HAP2)
text(cL, yB - 2.0, "掉了一條", 10.5, BAD, "bold")
text(cL, yB - 4.4, "copy loss／LOH", 9.5, MUTED)
cross(cL - 3.0, TOP + 5.6, 0.5)
text(cL + 0.8, TOP + 5.6, "過濾 900", 11, BAD, "bold")
# right: B keeps both copies -> the absence is real -> kept
chromosome(cR - 1.1, yB, L, W, HAP1)
chromosome(cR + 1.1, yB, L, W, HAP2)
text(cR, yB - 2.0, "兩條都在", 10.5, OK, "bold")
text(cR, yB - 4.4, "真的沒有", 9.5, MUTED)
check(cR - 3.0, TOP + 5.6, 0.5)
text(cR + 0.8, TOP + 5.6, "保留 301", 11, OK, "bold")
text(X4 + 11.5, TOP + 2.2, "藍／橘 = 兩條 haplotype，不分爸媽", 9.5, MUTED)

# step 5: build the tree
X5 = 138
panel(X5, TOP, 23, H, 5, "排成樹")
# groups of clones that share SNVs, drawn as boxes over the clone letters (details: how_tree_is_ordered.png)
C5, LX, LY = 2.35, X5 + 2.1, TOP + 20.5
for j, k in enumerate(LEAVES):
    ax.add_patch(Rectangle((LX + j * C5, LY), C5, C5, fc=COLOR[k], ec=PANEL, lw=1.0, zorder=3))
    text(LX + j * C5 + C5 / 2, LY + C5 / 2, k, 9, "#FFFFFF", "bold", zorder=4)
for pat, h, lab, col in (("GABEFCD", 17.0, "127", RED), ("ABEFCD", 13.4, "4", RED), ("EFCD", 9.8, "14", PURPLE),
                         ("AB", 6.2, "31", RED), ("EF", 6.2, "17", PURPLE), ("CD", 6.2, "68", GOLD)):
    idx = [j for j, k in enumerate(LEAVES) if k in pat]
    a, b = min(idx), max(idx)
    ax.add_patch(FancyBboxPatch((LX + a * C5 + 0.15, LY + C5 + 0.3), (b - a + 1) * C5 - 0.3, h,
                                boxstyle="round,pad=0,rounding_size=0.6", fc=col, ec="none", alpha=0.06, zorder=2))
    ax.add_patch(FancyBboxPatch((LX + a * C5 + 0.15, LY + C5 + 0.3), (b - a + 1) * C5 - 0.3, h,
                                boxstyle="round,pad=0,rounding_size=0.6", fc="none", ec=col, lw=1.8, zorder=3))
    text(LX + (a + b + 1) * C5 / 2, LY + C5 + h - 1.2, lab, 9.5, col, "bold", zorder=5)
arrow(X5 + 11.5, LY - 0.4, X5 + 11.5, LY - 3.4, color=INK2, lw=2.0)
mini_tree(LX, TOP + 8.0, 8 * C5, 8.5, lw=1.8, labels=False, stars=False)
text(X5 + 11.5, TOP + 4.6, "包住或不重疊的組疊成樹", 10.5, INK2, "bold")
text(X5 + 11.5, TOP + 1.9, "261 / 301 符合", 10.5, MUTED)

# step 6: stability
X6 = 164
panel(X6, TOP, 18, H, 6, "穩不穩")
for i, (dx, dy, a) in enumerate(((2.4, 2.4, 0.18), (1.2, 1.2, 0.35), (0, 0, 1.0))):
    mini_tree(X6 + 1.8 + dx, TOP + 15 + dy, 13.5, 18, lw=1.8, labels=False, alpha=a, stars=(i == 2))
text(X6 + 9, TOP + 7.2, "×1,000 重抽", 12.5, INK2)
check(X6 + 3.6, TOP + 3.2, 0.6)
text(X6 + 10.0, TOP + 3.2, "5 種門檻同一棵", 11.5, INK2)

# arrows along row A
for xa, xb in ((30, 34), (57, 60), (83, 86), (109, 112), (135, 138), (161, 164)):
    arrow(xa + 0.2, TOP + H / 2, xb - 0.2, TOP + H / 2)

# ---------------------------------------------------------------- row B: single cells check it
BOT, HB = 7, 52
panel(3, BOT, 50, HB, title="119 顆單細胞")
rnd = random.Random(3)
for i in range(119):
    c, r = i % 17, i // 17
    x, y = 6.2 + c * 2.65 + (r % 2) * 0.6, BOT + 38 - r * 4.4
    cell(x, y, 1.05, "#6F8F84", fill_alpha=0.15, nucleus=True)
text(28, BOT + 4.4, "PTA 放大 · short read · 第 23 代", 12, MUTED)

# candidate tree drops from step 6 to step 7
arrow(173, TOP - 0.4, 92, BOT + HB + 0.6, color=INK2, lw=2.8, rad=0.04)
text(128, 62.4, "候選樹", 14, INK2, "bold", bbox=dict(boxstyle="round,pad=0.25", fc=PAPER, ec="none"), zorder=6)

# step 7: compare every cell
X7 = 58
panel(X7, BOT, 58, HB, 7, "每顆細胞帶不帶這個分支")
cell(X7 + 9, BOT + 25, 6.0, "#6F8F84", fill_alpha=0.12, nucleus=False)
helix(X7 + 5.0, X7 + 13.0, BOT + 25, 1.0, 1.5, lw=1.6, rungs=False)
star(X7 + 7.2, BOT + 26.0, 120, RED)
star(X7 + 10.4, BOT + 24.0, 120, PURPLE)
arrow(X7 + 16, BOT + 25, X7 + 21, BOT + 25)
# heat strip: rows = 3 supported clades, columns = cells (sorted: H side, GAB, EF, CD)
order = [GREY] * 3 + [RED] * 9 + [PURPLE] * 5 + [GOLD] * 3
hx0, hw = X7 + 22.5, 1.55
for ci, grp in enumerate(order):
    x = hx0 + ci * hw
    for ri, (clade, col) in enumerate(((RED, RED), (PURPLE, PURPLE), (GOLD, GOLD))):
        y = BOT + 33 - ri * 6
        carries = (clade == RED and grp in (RED, PURPLE, GOLD)) or (clade == PURPLE and grp in (PURPLE, GOLD)) \
            or (clade == GOLD and grp == GOLD)
        ax.add_patch(Rectangle((x, y), hw * 0.88, 5.0, fc=col if carries else "#EEEBE3", ec="none", zorder=3))
for ri, (n, col) in enumerate((("127", RED), ("14", PURPLE), ("68", GOLD))):
    star(hx0 - 1.6, BOT + 35.5 - ri * 6, 110, col)
for ci, grp in enumerate(order):
    cell(hx0 + ci * hw + hw * 0.44, BOT + 17.5, 0.62, grp, fill_alpha=0.3, nucleus=False)
text(X7 + 38, BOT + 11.5, "每格 = 1 顆細胞 × 1 個分支", 11.5, MUTED)
text(X7 + 29, BOT + 4.2, "帶 ≥ 0.5", 13, INK, "bold")
text(X7 + 45, BOT + 4.2, "不帶 ≤ 0.2", 13, MUTED, "bold")
ax.add_patch(Rectangle((X7 + 23.0, BOT + 3.0), 2.2, 2.4, fc=RED, ec="none", zorder=3))
ax.add_patch(Rectangle((X7 + 38.6, BOT + 3.0), 2.2, 2.4, fc="#EEEBE3", ec="none", zorder=3))
text(X7 + 9, BOT + 15.5, "扣掉漏測", 11.5, MUTED)

# step 8: nesting
X8 = 121
panel(X8, BOT, 58, HB, 8, "一層套一層")
cx, cy = X8 + 32, BOT + 22
for (w, h, col, n), dx in zip(((40, 34, RED, "111"), (26, 22, PURPLE, "48"), (13, 11, GOLD, "16")), (0, 4.5, 8.0)):
    ax.add_patch(Ellipse((cx + dx, cy), w, h, fc=col, ec=col, alpha=0.10, lw=0, zorder=2))
    ax.add_patch(Ellipse((cx + dx, cy), w, h, fc="none", ec=col, lw=2.6, zorder=3))
text(cx - 13.0, cy + 9.0, "111", 17, RED, "bold")
text(cx + 0.5, cy + 5.5, "48", 17, PURPLE, "bold")
text(cx + 8.0, cy + 0.2, "16", 17, GOLD, "bold")
for x, y in ((cx - 14.5, cy + 4), (cx - 15.5, cy - 3), (cx - 12.5, cy - 9), (cx - 9.0, cy + 11),
             (cx - 8.0, cy - 13.5), (cx + 3.0, cy - 14.5), (cx + 11.0, cy + 13.0)):
    cell(x, y, 0.75, RED, 0.3, False)
for x, y in ((cx - 3.5, cy - 3.0), (cx - 1.5, cy - 8.0), (cx + 4.0, cy + 7.5)):
    cell(x, y, 0.75, PURPLE, 0.3, False)
for x, y in ((cx + 6.5, cy - 2.5), (cx + 10.0, cy - 2.8)):
    cell(x, y, 0.75, GOLD, 0.3, False)
for x, y in ((cx - 26.5, cy + 6), (cx - 27.5, cy), (cx - 26.0, cy - 6), (cx - 23.5, cy - 11)):
    cell(x, y, 0.85, GREY, 0.3, False, ls="--")
text(cx - 25.5, cy + 11.8, "8", 15, GREY, "bold")
check(X8 + 6.0, BOT + 4.2, 0.7)
text(X8 + 18.0, BOT + 4.2, "違反 0 顆", 13.5, INK, "bold")

# arrows along row B
arrow(53.2, BOT + HB / 2, 57.8, BOT + HB / 2)
arrow(116.2, BOT + HB / 2, 120.8, BOT + HB / 2)
arrow(179.2, BOT + HB / 2, 185.8, BOT + 40, rad=0.2)

# ---------------------------------------------------------------- step 9: the result
X9, Y9, W9, H9 = 186, 7, 51, 111
panel(X9, Y9, W9, H9, 9, "結果")
text(X9 + 25.5, Y9 + H9 - 10.5, "5 群 clone", 22, INK, "bold")
text(X9 + 25.5, Y9 + H9 - 15.5, "單細胞支持其中 4 群", 16, INK2, "bold")


def clone(x, y, r, col, n_cells, dashed=False, empty=False):
    ax.add_patch(Circle((x, y), r, fc=col if not empty else "#FBFBF8", ec=col if not empty else MUTED,
                        alpha=1, lw=2.4, zorder=3, fill=empty, ls=(0, (4, 3)) if dashed else "-"))
    if not empty:
        ax.add_patch(Circle((x, y), r, fc=col, ec="none", alpha=0.14, zorder=3))
        rnd = random.Random(n_cells)
        for _ in range(min(n_cells, 9)):
            a, rr = rnd.random() * 6.28, rnd.random() * r * 0.55
            cell(x + rr * math.cos(a), y + rr * math.sin(a), r * 0.17, col, 0.35, True, z=4)


ra, rc = 5.2, 5.0
pa = (X9 + 27, Y9 + 78)
ph, pg, pe, pc = (X9 + 11, Y9 + 59), (X9 + 36, Y9 + 59), (X9 + 36, Y9 + 37), (X9 + 36, Y9 + 15)
segs = ((pa, ph, GREY, "+792", -1), (pa, pg, RED, "+127", 1), (pg, pe, PURPLE, "+14", 1), (pe, pc, GOLD, "+68", 1))
for a, b, col, lab, side in segs:
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    arrow(a[0] + ux * ra, a[1] + uy * ra, b[0] - ux * rc, b[1] - uy * rc, color=col, lw=4.0)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    star(mx + side * 2.6, my + 0.6, 260, col, alpha=0.55 if col == GREY else 1.0)
    text(mx + side * 5.0, my - 0.2, lab, 15, col if col != GREY else INK2, "bold", ha="left" if side > 0 else "right")
clone(*pa, ra, MUTED, 0, empty=True)
text(pa[0], pa[1] + 0.4, "祖先", 13, INK2, "bold")
text(pa[0], pa[1] + 8.6, "8 株共有 7,784 SNV", 13, INK2, "bold")
clone(*ph, rc, GREY, 8, dashed=True)
clone(*pg, rc, RED, 63)
clone(*pe, rc, PURPLE, 32)
clone(*pc, rc, GOLD, 16)
for (x, y), n, lab in ((ph, 8, "H"), (pg, 63, "G A B"), (pe, 32, "E F"), (pc, 16, "C D")):
    side = -1 if lab == "H" else 1
    text(x + side * 7.0 if lab != "H" else x, y - 8.2 if lab == "H" else y + 1.6, f"{n} 顆", 16, INK, "bold",
         ha="center" if lab == "H" else "left")
    text(x + side * 7.0 if lab != "H" else x, y - 11.8 if lab == "H" else y - 2.2, lab, 13, MUTED,
         ha="center" if lab == "H" else "left")
text(X9 + 13.0, Y9 + 30.5, "未證實的分支", 11.5, MUTED)
text(X9 + 13.0, Y9 + 27.3, "4、31、17 SNV", 11.5, MUTED)
text(X9 + 13.0, Y9 + 24.1, "併入上一群", 11.5, MUTED)

fig.savefig(sys.argv[1], dpi=150, facecolor=PAPER)
