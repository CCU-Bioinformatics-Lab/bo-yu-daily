#!/usr/bin/env python3
"""Detail figure for step 6 of the HG008 tree: is the tree stable? (2026-11-11)

Two checks in tools/hg008_tree_rebuild.py:
  bootstrap (lines 190-194): resample the 301 CN-clean SNVs with replacement, rerun best_laminar,
    1,000 times; count how often each branch comes back.
  thresholds (line 40): rerun the whole analysis with 5 VAF / QUAL settings.
Numbers: lab_report/2026-11-07_hg008_tree_rebuild/tables/clades_vaf*_qual*.tsv, tree_summary.tsv.
Letters: A 2D6, B 2E6, C SC14, D SC28, E SC24, F SC9, G SC6, H 3E4 (report/2026_11_11_slides/BRIEF.md).

Usage: python3 tools/plot_hg008_tree_stability.py OUT.png
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
GREY, RED, PURPLE, GOLD, DARK = "#8A9A91", "#D23A2E", "#8456C4", "#D8A31E", "#8E1F17"
HAP1, HAP2, OK, BAD = "#3F7CAC", "#E08A3C", "#2E8B57", "#C0392B"
LEAVES = "HGABEFCD"
COLOR = {"H": GREY, "G": RED, "A": RED, "B": RED, "E": PURPLE, "F": PURPLE, "C": GOLD, "D": GOLD}
# branches: (clones, SNVs at the main setting, bootstrap at the main setting, dot color)
BRANCHES = [("GABEFCD", 127, 1.000, RED), ("CD", 68, 1.000, GOLD), ("AB", 31, 1.000, "#E57A70"),
            ("EF", 17, 1.000, PURPLE), ("EFCD", 14, 1.000, "#B49AE0"), ("ABEFCD", 4, 0.947, DARK)]
SETTINGS = [("0.15", "20", [129, 68, 32, 17, 14, 4], 0.950), ("0.25", "0", [134, 69, 31, 18, 15, 4], 0.869),
            ("0.25", "20", [127, 68, 31, 17, 14, 4], 0.947), ("0.25", "28", [121, 66, 30, 17, 14, 4], 0.942),
            ("0.35", "20", [99, 59, 29, 17, 12, 2], 0.774)]

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


def panel(x0, y0, w, h, title, sub=None):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                fc=PANEL, ec=EDGE, lw=1.6, zorder=1))
    text(x0 + 3.0, y0 + h - 3.6, title, 17, INK, "bold", ha="left", zorder=4)
    if sub:
        text(x0 + 3.0, y0 + h - 7.6, sub, 12.5, MUTED, ha="left", zorder=4)


def arrow(x0, y0, x1, y1, color=MUTED, lw=2.4, rad=0.0, z=2):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=22, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


def star(x, y, s=160, color=RED, alpha=1.0, z=6):
    ax.scatter([x], [y], marker="*", s=s, c=color, alpha=alpha, edgecolors="none", zorder=z)


def check(x, y, s=1.0, color=OK):
    ax.plot([x - 1.4 * s, x - 0.3 * s, x + 1.7 * s], [y, y - 1.2 * s, y + 1.4 * s], color=color, lw=4 * s,
            solid_capstyle="round", zorder=6)


def jar(x, y, w, h, counts, seed, r):
    """A jar of SNV dots: counts = dots per branch color (plus grey conflicts)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.6", fc="#F7F9F8", ec=MUTED,
                                lw=1.8, zorder=2))
    ax.add_patch(Rectangle((x + w * 0.2, y + h), w * 0.6, h * 0.08, fc="#C9D3CF", ec=MUTED, lw=1.4, zorder=2))
    dots = [c for c, n in counts for _ in range(n)]
    random.Random(seed).shuffle(dots)
    cols = max(1, int((w - 1.2) / (2.2 * r)))
    for i, c in enumerate(dots):
        cx = x + 0.6 + r + (i % cols) * 2.2 * r
        cy = y + 0.6 + r + (i // cols) * 2.2 * r
        ax.add_patch(Circle((cx, cy), r, fc=c, ec="none", zorder=3))


def mini_tree(x0, y0, w, h, lw=2.0, drop_six=False, labels=True):
    xs = {k: x0 + w * (i + 0.5) / 8 for i, k in enumerate(LEAVES)}
    yl, step = y0, h / 5
    ab, ef, cd = (xs["A"] + xs["B"]) / 2, (xs["E"] + xs["F"]) / 2, (xs["C"] + xs["D"]) / 2
    cdef = (ef + cd) / 2
    six = (ab + cdef) / 2
    seven = (xs["G"] + six) / 2
    root = (xs["H"] + seven) / 2
    ys = {"root": yl + 5 * step, "seven": yl + 4 * step, "six": yl + 3 * step, "cdef": yl + 2 * step,
          "pair": yl + step}
    segs = [((root, ys["root"]), (xs["H"], yl), GREY), ((root, ys["root"]), (seven, ys["seven"]), RED),
            ((ab, ys["pair"]), (xs["A"], yl), RED), ((ab, ys["pair"]), (xs["B"], yl), RED),
            ((cdef, ys["cdef"]), (ef, ys["pair"]), PURPLE), ((cdef, ys["cdef"]), (cd, ys["pair"]), GOLD),
            ((ef, ys["pair"]), (xs["E"], yl), PURPLE), ((ef, ys["pair"]), (xs["F"], yl), PURPLE),
            ((cd, ys["pair"]), (xs["C"], yl), GOLD), ((cd, ys["pair"]), (xs["D"], yl), GOLD)]
    if drop_six:  # the 4-SNV branch is gone: G, (A,B) and (E,F,C,D) hang from one node
        segs += [((seven, ys["seven"]), (xs["G"], yl), RED), ((seven, ys["seven"]), (ab, ys["pair"]), RED),
                 ((seven, ys["seven"]), (cdef, ys["cdef"]), PURPLE)]
    else:
        segs += [((seven, ys["seven"]), (xs["G"], yl), RED), ((seven, ys["seven"]), (six, ys["six"]), DARK),
                 ((six, ys["six"]), (ab, ys["pair"]), RED), ((six, ys["six"]), (cdef, ys["cdef"]), PURPLE)]
    for (a, b), (c, d), col in segs:
        ax.plot([a, c, c], [b, b, d], color=col, lw=lw, solid_capstyle="round", zorder=4)
    if labels:
        for k, x in xs.items():
            ax.add_patch(Circle((x, yl - 1.3), 1.0, fc=COLOR[k], ec="none", zorder=4))
    return (six, ys["six"]), (seven, ys["seven"])


# ---------------------------------------------------------------- frame
helix(4, 236, 130.3, 1.5, 14, alpha=0.18, lw=2.2)
helix(4, 236, 3.2, 1.2, 16, alpha=0.14, lw=2.0)
text(5, 124.2, "第 ⑥ 步：這棵樹穩不穩", 30, INK, "bold", ha="left")
text(80, 124.0, "換一批 SNV、換一組門檻重排，看樹會不會變", 18, INK2, ha="left")

# ---------------------------------------------------------------- left: bootstrap
panel(3, 7, 125, 111, "檢查 1：隨機重抽 SNV，重排 1,000 次", "bootstrap：從 301 個 SNV 裡抽 301 個，可以重複抽到同一個")
# Two real draws of the program's bootstrap (seed 20261107, recomputed 2026-11-11 with the module's own
# functions): draw 1 keeps all 6 cuts; draw 45 is the first that loses the 4-SNV cut. In draw 45 the group
# "G, E, F, C, D" (1 SNV originally) was drawn 4 times and "A, B, E, F, C, D" (4 originally) only 2 times,
# so the second cut moves: A, B are cut off before G.
TEAL = "#1F8A8A"


def chips(x, y, pat, size=2.6, gap=0.25):
    """8 squares in H..D order with letters: filled = this clone has the SNV."""
    for j, k in enumerate(LEAVES):
        on = k in pat
        ax.add_patch(Rectangle((x + j * (size + gap), y - size / 2), size, size,
                               fc=COLOR[k] if on else "#FFFFFF", ec=COLOR[k] if not on else EDGE, lw=0.8, zorder=4))
        text(x + j * (size + gap) + size / 2, y, k, 8.5, "#FFFFFF" if on else COLOR[k], "bold", zorder=5)


def knife_s(x, y, s):
    ax.add_patch(Polygon([(x, y), (x + 1.2 * s, y + 4.6 * s), (x + 1.2 * s, y + 5.8 * s), (x - 0.3 * s, y + 5.8 * s),
                          (x - 0.3 * s, y + 1.0 * s)], closed=True, fc="#DDE3E6", ec="#5B6770", lw=1.2, zorder=7))
    ax.add_patch(Rectangle((x - 0.1 * s, y + 5.8 * s), 1.1 * s, 3.0 * s, fc="#7B5E45", ec="none", zorder=7))


def cut_rows(x0, y0, cuts, hl, order):
    """cuts: list of (group, left piece); order: letter order of this tree. Pieces drift apart cut by cut."""
    cw, gap = 3.3, 0.3
    off = {k: 0.0 for k in LEAVES}
    order = list(order)
    for i, (group, left) in enumerate(cuts):
        y = y0 - i * 6.2
        for k in group:
            off[k] += -0.45 if k in left else 0.45
        if i == hl:
            ax.add_patch(FancyBboxPatch((x0 - 7.0, y - 1.6), 44.5, 5.6, boxstyle="round,pad=0,rounding_size=0.8",
                                        fc="#FFF3C4", ec="#E0B000", lw=1.6, zorder=2))
        text(x0 - 3.6, y + 1.2, f"第 {i + 1} 刀", 10.5, INK2, "bold")
        for k in order:
            xk = x0 + order.index(k) * (cw + gap) + off[k]
            ax.add_patch(FancyBboxPatch((xk, y), cw, 2.6, boxstyle="round,pad=0,rounding_size=0.4",
                                        fc=COLOR[k], ec="none", alpha=1.0 if k in group else 0.15, zorder=3))
            text(xk + cw / 2, y + 1.3, k, 9.5, "#FFFFFF", "bold", alpha=1.0 if k in group else 0.5, zorder=4)
        lk = [k for k in order if k in left][-1]
        rk = [k for k in order if k in group and k not in left][0]
        cx = (x0 + order.index(lk) * (cw + gap) + off[lk] + cw + x0 + order.index(rk) * (cw + gap) + off[rk]) / 2
        ax.plot([cx, cx], [y - 0.8, y + 3.4], color=BAD, lw=1.8, ls=(0, (2, 1.5)), zorder=5)
        knife_s(cx, y + 3.2, 0.42)


DRAWS = [("第 1 次抽樣：6 刀都在", 6, 2, [("HGABEFCD", "H"), ("GABEFCD", "G"), ("ABEFCD", "AB"), ("EFCD", "EF")],
          "→ 第 2 刀先切 G（6 > 2）", OK, "129、30、18、9、76", "HGABEFCD"),
         ("第 45 次抽樣：第 2 刀換位置", 2, 4, [("HGABEFCD", "H"), ("GABEFCD", "AB"), ("GEFCD", "G"), ("EFCD", "EF")],
          "→ 第 2 刀先切 A、B（4 > 2）", BAD, "125、44、18、11、63", "HABGEFCD")]
for c, (title, n_six, n_alt, cuts, verdict, vcol, others, order) in enumerate(DRAWS):
    x = 6.0 + c * 61.0
    ax.add_patch(FancyBboxPatch((x, 51.5), 58, 54.5, boxstyle="round,pad=0,rounding_size=1.6",
                                fc="#FBFBF8", ec=vcol, lw=2.0, zorder=1.5))
    text(x + 2.0, 102.6, title, 14, vcol, "bold", ha="left")
    text(x + 2.0, 98.4, "抽到的 SNV：實心 = 這幾株有（括號 = 原本個數）", 11.5, MUTED, ha="left")
    chips(x + 2.0, 94.4, "ABEFCD")
    text(x + 25.5, 94.4, f"{n_six} 個（4）", 13, DARK, "bold", ha="left")
    text(x + 39.0, 94.4, "→ 支持先切 G", 11, MUTED, ha="left")
    chips(x + 2.0, 90.0, "GEFCD")
    text(x + 25.5, 90.0, f"{n_alt} 個（1）", 13, TEAL, "bold", ha="left")
    text(x + 39.0, 90.0, "→ 支持先切 A、B", 11, MUTED, ha="left")
    text(x + 2.0, 85.8, f"其他 5 組：{others}", 10.5, MUTED, ha="left")
    text(x + 2.0, 81.6, verdict, 12.5, vcol, "bold", ha="left")
    cut_rows(x + 11.0, 72.6, cuts, 1, order)
text(125.0, 110.4, "同一個程式，只是抽到的 SNV 不同", 12.5, INK2, "bold", ha="right")

# tally: the full trees the 1,000 bootstrap draws produced (recomputed 2026-11-11 with the module's own
# functions, seed 20261107): original tree 947, "A, B split before G" 48, unresolved G / AB / EFCD 5.
TREES = [(("H", ("G", (("A", "B"), (("E", "F"), ("C", "D"))))), 947, "原本的樹：G 先分出", OK, ("ABEFCD",)),
         (("H", (("A", "B"), ("G", (("E", "F"), ("C", "D"))))), 48, "A、B 先分出", BAD, ("GEFCD",)),
         (("H", ("G", ("A", "B"), (("E", "F"), ("C", "D")))), 5, "G、A＋B、E＋F＋C＋D 分不出先後", BAD, ("POLY",))]


def leaves_of(t):
    return [t] if isinstance(t, str) else [x for c in t for x in leaves_of(c)]


def draw_tree(t, x0, y0, w, h, key):
    order = leaves_of(t)
    lx = {k: x0 + w * (i + 0.5) / len(order) for i, k in enumerate(order)}

    def depth(n):
        return 0 if isinstance(n, str) else 1 + max(depth(c) for c in n)
    step = h / depth(t)

    def walk(n, yn):
        if isinstance(n, str):
            return lx[n]
        kids = [walk(c, yn - step if not isinstance(c, str) else None) for c in n]
        xn = sum(kids) / len(kids)
        name = "".join(sorted(leaves_of(n)))
        hl = (key == ("POLY",) and len(n) == 3) or name in ["".join(sorted(k)) for k in key]
        for c, xc in zip(n, kids):
            yc = y0 if isinstance(c, str) else yn - step
            ax.plot([xn, xc, xc], [yn, yn, yc], color=BAD if hl else INK2, lw=3.0 if hl else 2.0,
                    solid_capstyle="round", zorder=4 if hl else 3)
        if hl:
            star(xn, yn + 1.6, 200, BAD, z=7)
        return xn

    walk(t, y0 + h)
    for k, x in lx.items():
        ax.add_patch(Circle((x, y0 - 2.0), 1.6, fc=COLOR[k], ec="none", zorder=5))
        text(x, y0 - 2.0, k, 10.5, "#FFFFFF", "bold", zorder=6)


text(7, 47.5, "1,000 次重抽，排出哪幾種完整的樹", 14.5, INK, "bold", ha="left")
for i, (t, n, label, col, key) in enumerate(TREES):
    x = 7.0 + i * 39.5
    draw_tree(t, x, 24.0, 34.0, 16.0, key)
    text(x + 17.0, 18.6, label, 12, col, "bold")
    ax.add_patch(Rectangle((x + 2.0, 12.6), 30.0, 2.6, fc="#EEEBE3", ec="none", zorder=2))
    ax.add_patch(Rectangle((x + 2.0, 12.6), 30.0 * n / 1000, 2.6, fc=col, ec="none", zorder=3))
    text(x + 17.0, 9.4, f"{n} 次", 15, col, "bold")
text(66, 44.2, "其他 5 刀每次都一樣；只有紅色★那一層（G 和 A、B 誰先分出）會變", 12, MUTED)

# ---------------------------------------------------------------- right: thresholds
panel(132, 7, 105, 111, "檢查 2：換門檻，從頭重跑", "第 ② 步的 VAF、QUAL 門檻換成 5 種組合")
TW = 19.2
for i, (vaf, qual, counts, boot) in enumerate(SETTINGS):
    x = 135.5 + i * (TW + 0.9)
    main = (vaf, qual) == ("0.25", "20")
    ax.add_patch(FancyBboxPatch((x, 72), TW, 31, boxstyle="round,pad=0,rounding_size=1.4",
                                fc="#FBFBF8" if not main else "#FFF6F2", ec=INK if main else EDGE,
                                lw=2.2 if main else 1.4, zorder=2))
    text(x + TW / 2, 99.6, f"VAF ≥ {vaf}", 12, INK, "bold")
    text(x + TW / 2, 96.4, f"QUAL ≥ {qual}", 12, INK, "bold")
    mini_tree(x + 1.2, 79.5, TW - 2.4, 12.5, lw=1.8)
    check(x + TW / 2 - 1.0, 75.0, 0.6)
    if main:
        text(x + TW / 2, 106.0, "主設定", 12, INK, "bold")
text(184.5, 68.0, "5 種門檻都切出同一棵樹（同樣 6 刀）", 14, OK, "bold")

# table: SNVs per branch for each setting
text(135.5, 61.5, "每一刀有幾個 SNV 支持（紅底 = 最弱的那刀）", 13.5, INK, "bold", ha="left")
for i, (pat, n, boot, col) in enumerate(BRANCHES):
    y = 56.0 - i * 4.6
    weak = pat == "ABEFCD"
    if weak:
        ax.add_patch(Rectangle((134.5, y - 2.1), 101, 4.2, fc="#FBE9E6", ec="none", zorder=2))
    for j, k in enumerate(LEAVES):
        ax.add_patch(Rectangle((135.2 + j * 1.6, y - 0.7), 1.4, 1.4, fc=COLOR[k] if k in pat else "#FFFFFF",
                               ec=EDGE, lw=0.6, zorder=3))
    for s_i, (_, _, counts, _) in enumerate(SETTINGS):
        x = 135.5 + s_i * (TW + 0.9) + TW / 2 + 6.0
        text(x, y, str(counts[i]), 12.5, BAD if weak else INK, "bold" if weak else "normal")
y = 56.0 - 6 * 4.6
text(135.2, y, "bootstrap", 11.5, BAD, ha="left")
for s_i, (_, _, _, boot) in enumerate(SETTINGS):
    x = 135.5 + s_i * (TW + 0.9) + TW / 2 + 6.0
    text(x, y, f"{boot:.2f}", 12, BAD, "bold")

# what it can / cannot show
ax.add_patch(FancyBboxPatch((135, 9.5), 48, 13, boxstyle="round,pad=0,rounding_size=1.4", fc="#EEF6F0", ec=OK,
                            lw=1.6, zorder=2))
text(137, 19.6, "能證明", 13.5, OK, "bold", ha="left")
text(137, 15.6, "樹形不是少數 SNV 或", 12, INK2, ha="left")
text(137, 12.4, "某個門檻撐起來的", 12, INK2, ha="left")
ax.add_patch(FancyBboxPatch((186, 9.5), 49, 13, boxstyle="round,pad=0,rounding_size=1.4", fc="#FBEDEB", ec=BAD,
                            lw=1.6, zorder=2))
text(188, 19.6, "不能證明", 13.5, BAD, "bold", ha="left")
text(188, 15.6, "樹是對的：批次等系統性錯誤", 12, INK2, ha="left")
text(188, 12.4, "重抽也會一樣 → 要靠單細胞（⑦⑧）", 12, INK2, ha="left")

fig.savefig(sys.argv[1], dpi=150, facecolor=PAPER)
