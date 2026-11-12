#!/usr/bin/env python3
"""Detail figure for steps 7-8 of the HG008 tree: checking the tree with 119 single cells (2026-11-11).

Rules (tools/hg008_sc_clade_test.py:1-35): a cell's truncal detection rate (7,784 sites) is its
sensitivity; rel = branch detection rate / sensitivity; carrier rel >= 0.5, non-carrier rel <= 0.2.
Nesting: a carrier of an inner branch must not be a non-carrier of the outer branch.
Data: lab_report/2026-11-07_hg008_sc_check/tables/cell_by_branch.tsv, branch_summary.tsv, nesting.tsv.
Example cells SC01 and SC02: called counts = rel x sensitivity x sites (cell_by_branch.tsv).
Letters: A 2D6, B 2E6, C SC14, D SC28, E SC24, F SC9, G SC6, H 3E4 (report/2026_11_11_slides/BRIEF.md).

Usage: python3 tools/plot_hg008_sc_check_explainer.py CELL_BY_BRANCH.tsv OUT.png
"""
import csv
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

# matplotlib reads NotoSansCJK.ttc as its first face (JP); it covers the traditional characters used here.
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, INK2, MUTED = "#1F2A37", "#46574F", "#7A8A82"
PAPER, PANEL, EDGE = "#F6F4EE", "#FFFFFF", "#D9D4C7"
GREY, RED, PURPLE, GOLD = "#8A9A91", "#D23A2E", "#8456C4", "#D8A31E"
HAP1, HAP2, OK, BAD, TEAL, AMBER = "#3F7CAC", "#E08A3C", "#2E8B57", "#C0392B", "#6F8F84", "#E0A000"
LEAVES = "HGABEFCD"
COLOR = {"H": GREY, "G": RED, "A": RED, "B": RED, "E": PURPLE, "F": PURPLE, "C": GOLD, "D": GOLD}
B127, B14, B68 = "2D6,2E6,SC14,SC24,SC28,SC6,SC9", "SC14,SC24,SC28,SC9", "SC14,SC28"
HEAT_ROWS = [(B127, "GABEFCD", "127", RED), (B14, "EFCD", "14", PURPLE), (B68, "CD", "68", GOLD),
             ("2D6,2E6", "AB", "31", RED), ("SC24,SC9", "EF", "17", PURPLE), ("3E4", "H", "792", GREY)]

cells = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))

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


def panel(x0, y0, w, h, num, title):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                fc=PANEL, ec=EDGE, lw=1.6, zorder=1))
    ax.add_patch(Circle((x0 + 3.6, y0 + h - 3.6), 2.6, fc=INK, ec="none", zorder=3))
    text(x0 + 3.6, y0 + h - 3.6, num, 15, "#FFFFFF", "bold", zorder=4)
    text(x0 + 7.6, y0 + h - 3.6, title, 17, INK, "bold", ha="left", zorder=4)


def star(x, y, s=160, color=RED, alpha=1.0, z=6):
    ax.scatter([x], [y], marker="*", s=s, c=color, alpha=alpha, edgecolors="none", zorder=z)


def arrow(x0, y0, x1, y1, color=MUTED, lw=2.4, rad=0.0, z=2):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=22, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


def cell_icon(x, y, r, color, fill=0.15):
    ax.add_patch(Circle((x, y), r, fc=color, ec="none", alpha=fill, zorder=3))
    ax.add_patch(Circle((x, y), r, fc="none", ec=color, lw=1.6, zorder=3))
    ax.add_patch(Circle((x + r * 0.2, y + r * 0.1), r * 0.36, fc=color, ec="none", alpha=0.7, zorder=4))


def chips(x, y, pat, size=1.9, gap=0.2, fs=7.5):
    for j, k in enumerate(LEAVES):
        on = k in pat
        ax.add_patch(Rectangle((x + j * (size + gap), y - size / 2), size, size,
                               fc=COLOR[k] if on else "#FFFFFF", ec=COLOR[k] if not on else EDGE, lw=0.7, zorder=4))
        text(x + j * (size + gap) + size / 2, y, k, fs, "#FFFFFF" if on else COLOR[k], "bold", zorder=5)


def blend(col, t):
    t = max(0.0, min(1.0, t))
    r, g, b = to_rgb(col)
    return (1 - t) * 0.94 + t * r, (1 - t) * 0.93 + t * g, (1 - t) * 0.90 + t * b


# ---------------------------------------------------------------- frame
helix(4, 236, 130.3, 1.5, 14, alpha=0.18, lw=2.2)
helix(4, 236, 3.2, 1.2, 16, alpha=0.14, lw=2.0)
text(5, 124.2, "第 ⑦⑧ 步：用 119 顆單細胞檢查樹", 30, INK, "bold", ha="left")
text(110, 124.0, "樹由 8 株選殖株排出；單細胞是另一批、獨立的資料", 18, INK2, ha="left")

# ---------------------------------------------------------------- 7: scoring one cell (simple version)
# SC01: truncal 6,936 / 7,784 = 0.89; 127-branch 115 / 127 = 0.91 -> carrier. SC02: 14-branch 0 / 14 -> non-carrier.
panel(3, 7, 84, 111, "⑦", "一顆細胞帶不帶這個分支？")


def bar(x, y, w, frac, col, label, value):
    ax.add_patch(FancyBboxPatch((x, y - 2.0), w, 4.0, boxstyle="round,pad=0,rounding_size=0.8", fc="#EEEBE3",
                                ec="none", zorder=2))
    if frac > 0:
        ax.add_patch(FancyBboxPatch((x, y - 2.0), w * frac, 4.0, boxstyle="round,pad=0,rounding_size=0.8", fc=col,
                                    ec="none", zorder=3))
    text(x, y + 4.2, label, 12.5, INK2, "bold", ha="left")
    text(x + w + 2.0, y, value, 16, col if frac > 0 else MUTED, "bold", ha="left")


# step 1: eyesight
ax.add_patch(Circle((9.5, 99.0), 2.6, fc=INK, ec="none", zorder=3))
text(9.5, 99.0, "1", 13, "#FFFFFF", "bold", zorder=4)
text(14, 99.0, "先測這顆細胞的「眼力」", 15, INK, "bold", ha="left")
cell_icon(12, 86.0, 4.0, TEAL)
text(12, 79.6, "SC01", 11, MUTED)
bar(20, 86.0, 46, 0.89, TEAL, "每顆細胞都該有的突變（8 株共有）", "89%")
text(20, 79.8, "測不到的 11% 是漏測", 11.5, MUTED, ha="left")

# step 2: one branch
ax.add_patch(Circle((9.5, 70.0), 2.6, fc=INK, ec="none", zorder=3))
text(9.5, 70.0, "2", 13, "#FFFFFF", "bold", zorder=4)
text(14, 70.0, "再看某個分支的突變測到多少", 15, INK, "bold", ha="left")
cell_icon(12, 57.0, 4.0, TEAL)
text(12, 50.6, "SC01", 11, MUTED)
bar(20, 57.0, 46, 0.91, RED, "G A B E F C D 分支的突變（127 個）", "91%")
text(20, 50.8, "和眼力差不多 →", 12.5, INK2, ha="left")
text(34.2, 50.8, "帶", 15, OK, "bold", ha="left")
cell_icon(12, 39.0, 4.0, TEAL)
text(12, 32.6, "SC02", 11, MUTED)
bar(20, 39.0, 46, 0.0, PURPLE, "E F C D 分支的突變（14 個）", "0%")
text(20, 32.8, "幾乎測不到 →", 12.5, INK2, ha="left")
text(32.6, 32.8, "不帶", 15, BAD, "bold", ha="left")

# rule
ax.add_patch(FancyBboxPatch((6, 9.5), 77, 15.5, boxstyle="round,pad=0,rounding_size=1.4", fc="#F4F6F5", ec=EDGE,
                            lw=1.2, zorder=2))
text(9, 21.4, "規則（事先定好）", 13, INK, "bold", ha="left")
text(9, 17.0, "測到的 ≥ 眼力的一半 →", 12.5, INK2, ha="left")
text(35.0, 17.0, "帶", 13.5, OK, "bold", ha="left")
text(9, 12.8, "測到的 ≤ 眼力的兩成 →", 12.5, INK2, ha="left")
text(35.0, 12.8, "不帶", 13.5, BAD, "bold", ha="left")
text(50, 14.9, "中間 → 不確定", 12.5, MUTED, ha="left")

# ---------------------------------------------------------------- heatmap of all cells
panel(91, 7, 80, 111, "⑦", "119 顆細胞 × 6 條分支")
rel = lambda c, b: float(c[b])
groups = []
for c in cells:
    if rel(c, B127) <= 0.2:
        g = 0
    elif rel(c, B68) >= 0.5:
        g = 3
    elif rel(c, B14) >= 0.5:
        g = 2
    else:
        g = 1
    groups.append((g, -float(c["sensitivity"]), c))
groups.sort(key=lambda t: (t[0], t[1]))
HX0, HW = 105.0, 63.0
cwid = HW / len(groups)
for r_i, (b, pat, n, col) in enumerate(HEAT_ROWS):
    y = 90.0 - r_i * 9.0
    chips(93.0, y + 3.2, pat, size=1.35, gap=0.12, fs=6)
    text(93.0, y - 0.4, f"{n} 個", 10, MUTED, ha="left")
    for j, (g, _, c) in enumerate(groups):
        ax.add_patch(Rectangle((HX0 + j * cwid, y - 1.6), cwid * 0.92, 7.0, fc=blend(col, rel(c, b)), ec="none",
                               zorder=3))
bounds = [0]
for g in range(4):
    bounds.append(bounds[-1] + sum(1 for t in groups if t[0] == g))
labels = [("8 顆", "H", GREY), ("63 顆", "G A B", RED), ("32 顆", "E F", PURPLE), ("16 顆", "C D", GOLD)]
for g, (n, lab, col) in enumerate(labels):
    xa, xb = HX0 + bounds[g] * cwid, HX0 + bounds[g + 1] * cwid
    ax.plot([xa, xb - 0.3], [40.0, 40.0], color=col, lw=4, solid_capstyle="butt", zorder=3)
    text((xa + xb) / 2, 36.4, n, 12.5 if g else 11, INK, "bold")
    text((xa + xb) / 2, 33.0, lab, 11, col, "bold")
    if g:
        ax.plot([xa, xa], [40.5, 97.5], color=PANEL, lw=1.6, zorder=4)
text(HX0 + HW / 2, 101.6, "每一欄 = 1 顆細胞；顏色越深 = 越像帶這個分支", 12, MUTED)
text(131, 27.0, "上三列：一塊一塊很清楚 → 有支持", 12.5, OK, "bold")
text(131, 23.2, "A B（31）、E F（17）：顏色很淡 → 沒驗證到", 12.5, BAD, "bold")
text(131, 19.4, "H 專屬（792）：只有左邊 8 顆部分帶", 12.5, AMBER, "bold")
text(131, 12.0, "細胞是第 23 代、另一條培養路線；沒有帶者不代表分支不存在", 11, MUTED)

# ---------------------------------------------------------------- 8: nesting
panel(175, 7, 62, 111, "⑧", "一層套一層的檢查")
text(178, 101.6, "樹預測：帶裡層分支的細胞，一定也帶外層分支", 12.5, INK2, "bold", ha="left")
cx, cy = 210, 78
for (w, h, col, n, lab), dx in zip(((44, 30, RED, "111", "帶 127"), (28, 20, PURPLE, "48", "帶 14"),
                                    (13, 10, GOLD, "16", "帶 68")), (0, 5, 10)):
    ax.add_patch(Ellipse((cx + dx, cy), w, h, fc=col, ec="none", alpha=0.10, zorder=2))
    ax.add_patch(Ellipse((cx + dx, cy), w, h, fc="none", ec=col, lw=2.6, zorder=3))
text(cx - 14.5, cy + 4.0, "111", 16, RED, "bold")
text(cx - 14.5, cy + 0.6, "帶 GABEFCD", 9.5, RED)
text(cx - 1.0, cy + 5.0, "48", 16, PURPLE, "bold")
text(cx - 1.0, cy + 1.8, "帶 EFCD", 9.5, PURPLE)
text(cx + 10, cy + 0.8, "16", 15, GOLD, "bold")
text(cx + 10, cy - 2.4, "帶 CD", 9.5, GOLD)
for x, y in ((181.5, 84), (181.5, 79), (181.5, 74)):
    cell_icon(x, y, 1.1, GREY)
text(181.5, 69.4, "8 顆", 12, GREY, "bold")
text(181.5, 66.2, "都不帶", 10, GREY)
checks = [("帶 EFCD 的 48 顆", "都帶 GABEFCD", "48 / 48"), ("帶 CD 的 16 顆", "都帶 EFCD", "16 / 16"),
          ("帶 CD 的 16 顆", "都帶 GABEFCD", "16 / 16")]
text(178, 59.2, "檢查結果", 13.5, INK, "bold", ha="left")
for i, (a, b, n) in enumerate(checks):
    yy = 54.4 - i * 4.6
    text(178, yy, f"{a} → {b}", 12, INK2, ha="left")
    text(233, yy, n, 12.5, OK, "bold", ha="right")
ax.add_patch(FancyBboxPatch((178, 33.5), 56, 6.2, boxstyle="round,pad=0,rounding_size=1.2", fc="#EEF6F0", ec=OK,
                            lw=1.6, zorder=2))
text(206, 36.6, "違反的細胞：0 顆", 15, OK, "bold")
text(206, 27.6, "→ 樹的主架構有單細胞支持", 13, INK, "bold")
text(206, 22.0, "例外：約 5 顆像兩顆細胞混在一起；", 11, MUTED)
text(206, 18.6, "SC293 的順序和樹不完全一致（1 顆）", 11, MUTED)
text(206, 12.0, "細胞數 8＋63＋32＋16＝119 → 第 ⑨ 步的 5 群", 12, INK2, "bold")

fig.savefig(sys.argv[2], dpi=150, facecolor=PAPER)
