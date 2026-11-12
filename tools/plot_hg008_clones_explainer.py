#!/usr/bin/env python3
"""Background figure: what the 8 HG008 clones are (2026-11-11).

Facts from the GIAB README (README_HG008.md, NIST HG008-T_clones section, copy beside the data at
/big8_disk/boyu114/benchmark_data/GIAB/HG008/README_HG008.md):
  HG008-T is a PDAC tumor cell line from a female patient (2020), developed by the Liss lab (MGH).
  NIST received passage 13 in 2024 and made clonal cell lines by single-cell plating:
  directory {A}p{B}/{C}/p{D}plus{E} = bulk start date, passage at plating, clone ID,
  clone start passage (B+1), extra passages before harvest.
  20240718p14: 2D6 (p15+12), 2E6 (p15+11), 3E4 (p15+7)
  20240805p19: SC14 (p20+13), SC24 (p20+8), SC28 (p20+7), SC6 (p20+15), SC9 (p20+13)
  The 119 single cells are Liss lab batch 0823p23 (README_Bioskryb-Ultima.md).
Clone letters and colors follow report/2026_11_11_slides/BRIEF.md and tools/plot_hg008_tree_method.py.

Usage: python3 tools/plot_hg008_clones_explainer.py OUT.png
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
HAP1, HAP2, TEAL, BLUE = "#3F7CAC", "#E08A3C", "#6F8F84", "#3F7CAC"
CLONES = [("2D6", "A", RED, 14, 12), ("2E6", "B", RED, 14, 11), ("3E4", "H", GREY, 14, 7),
          ("SC6", "G", RED, 19, 15), ("SC9", "F", PURPLE, 19, 13), ("SC14", "C", GOLD, 19, 13),
          ("SC24", "E", PURPLE, 19, 8), ("SC28", "D", GOLD, 19, 7)]

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
    n = 300
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for phase, col in ((0, HAP1), (math.pi, HAP2)):
        ys = [y + amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0) + phase) for x in xs]
        ax.plot(xs, ys, color=col, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)
    if rungs:
        for i in range(int(turns * 6) + 1):
            x = x0 + (x1 - x0) * i / (turns * 6)
            a = amp * math.sin(2 * math.pi * turns * (x - x0) / (x1 - x0))
            ax.plot([x, x], [y + a, y - a], color=MUTED, lw=lw * 0.5, alpha=alpha * 0.6, zorder=0)


def panel(x0, y0, w, h, num, title):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                fc=PANEL, ec=EDGE, lw=1.6, zorder=1))
    ax.add_patch(Circle((x0 + 3.6, y0 + h - 3.6), 2.6, fc=INK, ec="none", zorder=3))
    text(x0 + 3.6, y0 + h - 3.6, str(num), 15, "#FFFFFF", "bold", zorder=4)
    text(x0 + 7.6, y0 + h - 3.6, title, 17, INK, "bold", ha="left", zorder=4)


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
    """Culture flask: body plus neck, cells drawn by the caller."""
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h * 0.72), (x + w * 0.62, y + h * 0.82),
                          (x + w * 0.62, y + h), (x + w * 0.38, y + h), (x + w * 0.38, y + h * 0.82),
                          (x, y + h * 0.72)], closed=True, fc="#F1F6F4", ec=MUTED, lw=2.0, zorder=z))
    ax.add_patch(Rectangle((x + w * 0.34, y + h), w * 0.32, h * 0.08, fc="#C9D3CF", ec=MUTED, lw=1.6, zorder=z))


def plate(x, y, cols, rows, pitch, picks):
    ax.add_patch(FancyBboxPatch((x - 1.6, y - 1.6), (cols - 1) * pitch + 3.2, (rows - 1) * pitch + 3.2,
                                boxstyle="round,pad=0,rounding_size=1.2", fc="#ECEFEA", ec=MUTED, lw=1.6, zorder=2))
    for r in range(rows):
        for c in range(cols):
            cx, cy = x + c * pitch, y + (rows - 1 - r) * pitch
            ax.add_patch(Circle((cx, cy), pitch * 0.38, fc="#FFFFFF", ec=EDGE, lw=1.0, zorder=3))
            if (r, c) in picks:
                cell(cx, cy, pitch * 0.2, picks[(r, c)], 0.5, False, z=4)


def colony(x, y, r, color, n=11, seed=0):
    ax.add_patch(Circle((x, y), r, fc="#FBFBF8", ec=EDGE, lw=1.4, zorder=2))
    rnd = random.Random(seed)
    for _ in range(n):
        a, rr = rnd.random() * 6.28, rnd.random() * r * 0.62
        cell(x + rr * math.cos(a), y + rr * math.sin(a), r * 0.17, color, 0.35, True, z=3)


# ---------------------------------------------------------------- frame
helix(4, 236, 130.3, 1.5, 14, alpha=0.18, lw=2.2)
helix(4, 236, 3.2, 1.2, 16, alpha=0.14, lw=2.0)
text(5, 124.2, "8 株選殖株是什麼", 30, INK, "bold", ha="left")
text(66, 124.0, "從腫瘤細胞株挑出單一顆細胞，讓它長成一整株", 18, INK2, ha="left")

TOP, H = 64, 54
# ---------------------------------------------------------------- 1 patient -> cell line
panel(3, TOP, 46, H, 1, "腫瘤細胞株")
px, py = 11.5, TOP + 26
ax.add_patch(Circle((px, py + 9.0), 3.3, fc="#C9D3CF", ec=MUTED, lw=1.6, zorder=3))
ax.add_patch(FancyBboxPatch((px - 5.0, py - 7.5), 10.0, 12.5, boxstyle="round,pad=0,rounding_size=4",
                            fc="#C9D3CF", ec=MUTED, lw=1.6, zorder=3))
ax.add_patch(Circle((px + 1.6, py - 0.5), 1.6, fc=RED, ec="none", alpha=0.85, zorder=4))
text(px, py - 12.0, "病人", 14, INK, "bold")
text(px, py - 15.6, "2020 · 胰臟癌", 12, MUTED)
arrow(18.5, py, 24.5, py)
flask(26, py - 13, 19, 25)
rnd = random.Random(5)
for col in [RED] * 6 + [PURPLE] * 4 + [GOLD] * 3 + [GREY] * 4:
    x, y = 28.5 + rnd.random() * 14, py - 10.5 + rnd.random() * 12
    cell(x, y, 0.95, col, 0.35, True, z=4)
text(35.5, py - 17.6, "HG008-T", 14, INK, "bold")
text(35.5, py - 21.2, "多種細胞混在一起", 12, MUTED)

# ---------------------------------------------------------------- 2 single-cell plating at NIST
X2 = 53
panel(X2, TOP, 92, H, 2, "NIST 把一顆一顆細胞種進培養孔（2024）")
ty = TOP + 9.0
ax.plot([X2 + 6, X2 + 86], [ty, ty], color=MUTED, lw=3, solid_capstyle="round", zorder=2)
for x, lab in ((X2 + 8, "第 13 代\n收到"), (X2 + 30, "第 14 代"), (X2 + 66, "第 19 代")):
    ax.plot([x, x], [ty - 1.4, ty + 1.4], color=INK2, lw=3, zorder=3)
    text(x, ty - 4.4, lab, 12.5, INK2, "bold", linespacing=1.1)
flask(X2 + 4.5, ty + 5, 8, 10)
rnd = random.Random(9)
for col in [RED] * 3 + [PURPLE] * 2 + [GOLD] * 2 + [GREY] * 2:
    cell(X2 + 5.6 + rnd.random() * 5.8, ty + 6.4 + rnd.random() * 4.6, 0.55, col, 0.35, False, z=4)
picks14 = {(0, 1): RED, (1, 3): RED, (2, 4): GREY}
picks19 = {(0, 0): RED, (0, 4): PURPLE, (1, 2): GOLD, (2, 1): PURPLE, (2, 5): GOLD}
plate(X2 + 21, ty + 10, 6, 4, 3.6, picks14)
plate(X2 + 57, ty + 10, 6, 4, 3.6, picks19)
arrow(X2 + 30, ty + 2.0, X2 + 30, ty + 8.0, color=INK2, lw=2.2)
arrow(X2 + 66, ty + 2.0, X2 + 66, ty + 8.0, color=INK2, lw=2.2)
text(X2 + 30, ty + 25.5, "3 株", 15, INK, "bold")
text(X2 + 66, ty + 25.5, "5 株", 15, INK, "bold")
ax.add_patch(Circle((X2 + 46.5, ty + 18.5), 3.0, fc="#FFFFFF", ec=EDGE, lw=1.4, zorder=3))
cell(X2 + 46.5, ty + 18.5, 1.4, RED, 0.5, True, z=4)
text(X2 + 46.5, ty + 13.2, "1 孔 1 顆", 13, INK2, "bold")

# ---------------------------------------------------------------- 3 grow and sequence
X3 = 149
panel(X3, TOP, 88, H, 3, "長成一整株，再定序")
gy = TOP + 34
ax.add_patch(Circle((X3 + 7, gy), 3.2, fc="#FFFFFF", ec=EDGE, lw=1.4, zorder=3))
cell(X3 + 7, gy, 1.3, RED, 0.5, True, z=4)
arrow(X3 + 11, gy, X3 + 16, gy)
colony(X3 + 21.5, gy, 5.2, RED, 13, 2)
text(X3 + 14.5, gy - 8.6, "再養 7–15 代", 12.5, INK2, "bold")
arrow(X3 + 27.5, gy, X3 + 32.5, gy)
helix(X3 + 34, X3 + 47, gy, 1.6, 2, lw=2.2)
text(X3 + 40.5, gy - 5.2, "PacBio", 13, INK2, "bold")
text(X3 + 40.5, gy - 8.6, "Revio", 13, INK2, "bold")
# the 8 clones: row 1 = picked at passage 14, row 2 = picked at passage 19
for i, (name, letter, col, p, plus) in enumerate(CLONES):
    row = 0 if p == 14 else 1
    k = i if row == 0 else i - 3
    pitch = 7.2
    cx = X3 + 51.5 + k * pitch + (pitch if row == 0 else 0)
    cy = TOP + 37 - row * 19.5
    colony(cx, cy, 3.0, col, 7, i)
    text(cx, cy - 5.0, name, 12, INK, "bold")
    text(cx, cy - 7.9, letter, 11, col, "bold")
text(X3 + 66.0, TOP + 44.6, "第 14 代挑的 3 株", 12, MUTED)
text(X3 + 66.0, TOP + 25.0, "第 19 代挑的 5 株", 12, MUTED)
text(X3 + 12.0, TOP + 4.0, "每株的細胞都來自同一顆細胞", 13, INK, "bold", ha="left")
for x0, x1 in ((49, 53), (145, 149)):
    arrow(x0 + 0.2, TOP + H / 2, x1 - 0.2, TOP + H / 2)

# ---------------------------------------------------------------- 4 why it lets us build a tree
BOT, HB = 7, 52
panel(3, BOT, 118, HB, 4, "為什麼選殖株可以排樹")
# cell lineage inside the culture: ancestor -> two lineages -> cells
root = (20, BOT + 36)
mids = {"red": (36, BOT + 41), "purple": (36, BOT + 27)}
leaves = {"r1": (52, BOT + 46, RED), "r2": (52, BOT + 37, RED), "p1": (52, BOT + 30, PURPLE),
          "p2": (52, BOT + 21, GOLD)}
lw = dict(color=MUTED, lw=2.4, zorder=2, solid_capstyle="round")
ax.plot([root[0], mids["red"][0]], [root[1], mids["red"][1]], **{**lw, "color": RED})
ax.plot([root[0], mids["purple"][0]], [root[1], mids["purple"][1]], **{**lw, "color": PURPLE})
ax.plot([mids["red"][0], leaves["r1"][0]], [mids["red"][1], leaves["r1"][1]], **{**lw, "color": RED})
ax.plot([mids["red"][0], leaves["r2"][0]], [mids["red"][1], leaves["r2"][1]], **{**lw, "color": RED})
ax.plot([mids["purple"][0], leaves["p1"][0]], [mids["purple"][1], leaves["p1"][1]], **{**lw, "color": PURPLE})
ax.plot([mids["purple"][0], leaves["p2"][0]], [mids["purple"][1], leaves["p2"][1]], **{**lw, "color": GOLD})
cell(*root, 2.4, GREY, 0.3)
star(root[0], root[1] + 4.0, 200, GREY)
text(root[0], root[1] - 4.6, "共同祖先", 13, INK2, "bold")
star(28, BOT + 41.6, 200, RED)
star(28, BOT + 33.4, 200, PURPLE)
star(44, BOT + 26.8, 200, GOLD)
for k, (x, y, col) in leaves.items():
    cell(x, y, 1.9, col, 0.35)
text(36, BOT + 13.0, "細胞分裂時突變（★）會傳給後代", 13, INK2, "bold")
# pick two cells -> clones -> star sets
for (k, y) in (("r1", BOT + 44), ("p2", BOT + 23)):
    x, ly, col = leaves[k]
    ax.add_patch(Circle((x, ly), 3.0, fc="none", ec=INK, lw=1.8, ls=(0, (3, 2)), zorder=4))
    arrow(x + 3.4, ly, 63, y)
    colony(68.5, y, 4.6, col, 10, 3 if k == "r1" else 4)
    arrow(74, y, 79, y)
sets = ((BOT + 44, (GREY, RED)), (BOT + 23, (GREY, PURPLE, GOLD)))
for y, cols in sets:
    for j, col in enumerate(cols):
        star(82.5 + j * 4.8, y, 330, col)
text(80.5, BOT + 33.6, "比較「誰有、誰沒有」", 14, INK, "bold", ha="left")
text(80.5, BOT + 29.6, "→ 排出分支順序", 14, INK, "bold", ha="left")
text(80.5, BOT + 12.6, "整株只來自一顆細胞，", 12.5, MUTED, ha="left")
text(80.5, BOT + 9.0, "訊號不被其他細胞稀釋", 12.5, MUTED, ha="left")

# ---------------------------------------------------------------- 5 two culture lines
X5 = 125
panel(X5, BOT, 112, HB, 5, "選殖株和其他 HG008 資料不是同一批培養")
sy = BOT + 26
flask(X5 + 6, sy - 7, 10, 13)
rnd = random.Random(13)
for col in [RED] * 3 + [PURPLE] * 2 + [GOLD] * 2 + [GREY] * 2:
    cell(X5 + 7.4 + rnd.random() * 7.2, sy - 5.6 + rnd.random() * 6.0, 0.6, col, 0.35, False, z=4)
text(X5 + 11, sy - 11.6, "第 13 代以前", 12.5, INK2, "bold")
text(X5 + 11, sy - 15.0, "同一條細胞株", 12, MUTED)
ax.plot([X5 + 17, X5 + 25], [sy, sy], color=MUTED, lw=3, zorder=2)
ax.plot([X5 + 25, X5 + 32, X5 + 44], [sy, sy + 11, sy + 11], color=TEAL, lw=3, zorder=2, solid_capstyle="round")
ax.plot([X5 + 25, X5 + 32, X5 + 44], [sy, sy - 11, sy - 11], color=BLUE, lw=3, zorder=2, solid_capstyle="round")
arrow(X5 + 44, sy + 11, X5 + 49, sy + 11, color=TEAL)
arrow(X5 + 44, sy - 11, X5 + 49, sy - 11, color=BLUE)
text(X5 + 36, sy + 14.6, "NIST · 2024", 12.5, TEAL, "bold")
text(X5 + 36, sy - 7.4, "MGH · 2023", 12.5, BLUE, "bold")
# NIST branch: 8 clones
for i, (name, letter, col, p, plus) in enumerate(CLONES):
    colony(X5 + 52.5 + i * 4.3, sy + 11, 1.9, col, 4, 20 + i)
text(X5 + 67.5, sy + 16.4, "第 14、19 代挑 8 株", 13, INK, "bold")
text(X5 + 67.5, sy + 5.6, "PacBio · 建樹", 12, MUTED)
# MGH branch: bulk + single cells
flask(X5 + 51, sy - 18, 8, 11)
rnd = random.Random(12)
for col in [RED] * 3 + [PURPLE] * 2 + [GOLD] * 2 + [GREY] * 2:
    cell(X5 + 52.2 + rnd.random() * 5.6, sy - 16.6 + rnd.random() * 5.2, 0.5, col, 0.35, False, z=4)
for i in range(14):
    cell(X5 + 64 + (i % 7) * 3.0, sy - 9.5 - (i // 7) * 3.0, 1.0, TEAL, 0.15, True)
text(X5 + 49.6, sy - 13.0, "bulk", 12, MUTED, ha="right")
text(X5 + 73, sy - 18.4, "119 顆單細胞 · 檢查", 12, MUTED)
text(X5 + 73, sy - 5.6, "第 23 代", 13, INK, "bold")
text(X5 + 6.0, BOT + 4.0, "選殖株擴增時也會多出新突變；兩條路線分開後各自累積", 12.5, MUTED, ha="left")

fig.savefig(sys.argv[1], dpi=150, facecolor=PAPER)
