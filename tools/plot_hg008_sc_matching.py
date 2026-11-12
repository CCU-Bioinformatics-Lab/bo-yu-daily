#!/usr/bin/env python3
"""Explainer: how a single cell is shown to carry a clone-tree branch (2026-11-12).

Wording agreed with the user 2026-11-12: a single cell is one VCF. Take the clones' somatic SNVs, look up the same
position and the same ALT in the cell's VCF (called, GT not 0/0). If most SNVs of one branch are found, the cell
carries that branch. Single cells prove that a branch exists, not each mutation one by one.

Real numbers (checked 2026-11-12):
  SC01 VCF 037113-NIST-PL01-SC01-...vep.PASS_filtered.vcf.gz: 3,610,962 PASS rows.
  chr1:166282757 A>G  -> SC01 row 0/1, AD 4,6;  chr1:176599272 G>T -> 0/1, AD 10,4;  chr11:58467817 C>A -> no row.
  127-SNV branch: SC01 found 115/127; truncal 6,936/7,784 = 0.891 (cell_sensitivity.tsv).
  14-SNV branch: SC02 found 0/14; truncal 6,578/7,784 = 0.845.
  Rule: carrier when found rate >= half of the truncal rate; non-carrier <= 0.2 of it (tools/hg008_sc_clade_test.py:4-7).
Source code for the matching: tools/hg008_sc_tree_check.py:39-56.

Usage: python3 tools/plot_hg008_sc_matching.py OUT.png
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED = "#1F2A37", "#7A8A82"
PAPER, PANEL, EDGE = "#F6F4EE", "#FFFFFF", "#D9D4C7"
RED, PURPLE, GREEN, BAD, GERM, TRUNC = "#D23A2E", "#8456C4", "#2E8B57", "#C0392B", "#C9CFC9", "#6F8F84"
MONO = "DejaVu Sans Mono"

fig = plt.figure(figsize=(24, 13.5), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 240)
ax.set_ylim(0, 135)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(PAPER)


def text(x, y, s, size=15, color=INK, weight="normal", ha="center", va="center", family=None):
    kw = {"family": family} if family else {}
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, zorder=6, **kw)


def box(x0, y0, w, h, fc=PANEL, ec=EDGE, lw=1.8, z=1, r=1.8):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def arrow(x0, y0, x1, y1, color=MUTED, lw=3):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=26, color=color, lw=lw,
                                 zorder=3))


def step(x0, num, title, sub):
    box(x0, 6, 72, 100)
    ax.add_patch(Circle((x0 + 4.5, 100), 3, fc=INK, ec="none", zorder=3))
    text(x0 + 4.5, 100, num, 17, "#FFFFFF", "bold")
    text(x0 + 9.5, 100.5, title, 18, weight="bold", ha="left")
    text(x0 + 9.5, 95, sub, 13, MUTED, ha="left")


text(6, 125, "單細胞怎麼證明一個分支存在", 30, weight="bold", ha="left")
text(6, 118, "單細胞是一個 VCF。拿選殖株的體細胞 SNV，到細胞的 VCF 查「同位置、同 ALT」有沒有被 call；"
             "一個分支的 SNV 大部分都查到 → 這顆細胞帶這個分支", 15, INK, ha="left")

# ---------------- step 1: clone list ----------------
x = 5
step(x, "1", "選殖株給清單", "腫瘤 vs 正常比出來，只有體細胞突變")
text(x + 36, 86, "每個 SNV 都知道是哪幾株有", 14, ha="center")
rows = [("chr1:166,282,757", "A→G"), ("chr1:176,599,272", "G→T"), ("chr11:58,467,817", "C→A"), ("…", "")]
box(x + 5, 44, 62, 37, fc="#FBF1F0", ec=RED, lw=2.2)
text(x + 36, 77, "同一個分支：除了 3E4 的 7 株都有", 14, RED, "bold")
for i, (pos, sub) in enumerate(rows):
    y = 70 - i * 6.5
    text(x + 10, y, pos, 14, family=MONO, ha="left")
    text(x + 55, y, sub, 14, family=MONO, ha="left")
text(x + 36, 48, "共 127 個 SNV", 15, RED, "bold")
text(x + 36, 34, "另外：7,784 個共同祖先突變", 14, TRUNC, "bold")
text(x + 36, 29, "（8 株都有，每顆細胞都該有）", 13, MUTED)
text(x + 36, 16, "germline 已經扣掉", 14, INK)
text(x + 36, 11.5, "所以清單上的位置都是體細胞突變", 13, MUTED)

arrow(78, 62, 84, 62)

# ---------------- step 2: lookup in the cell's VCF ----------------
x = 85
step(x, "2", "到細胞的 VCF 逐一查", "例：SC01，一顆腫瘤細胞")
text(x + 36, 86, "VCF 有 3,610,962 列，大多是 germline", 14)
# a strip of rows: grey germline, coloured somatic
for i in range(60):
    col = GERM if i % 9 else RED
    ax.add_patch(Rectangle((x + 6 + i * 1.0, 80), 0.75, 3, fc=col, ec="none", zorder=3))
text(x + 67, 81.5, "…", 14, MUTED)
text(x + 36, 76.5, "灰 = germline　紅 = 清單上的體細胞位置", 12, MUTED)

checks = [("chr1:166,282,757 A→G", "0/1　ref 4、alt 6", "查到", GREEN),
          ("chr1:176,599,272 G→T", "0/1　ref 10、alt 4", "查到", GREEN),
          ("chr11:58,467,817 C→A", "VCF 裡沒有這一列", "沒查到", BAD)]
for i, (pos, row, verdict, col) in enumerate(checks):
    y = 66 - i * 12
    box(x + 4, y - 4.5, 64, 9.5, ec=col, lw=2)
    text(x + 7, y + 1.8, pos, 13, family=MONO, ha="left")
    text(x + 7, y - 2.2, row, 12, MUTED, ha="left")
    text(x + 62, y, verdict, 15, col, "bold")
box(x + 4, 10, 64, 21, fc="#F3F5F3", ec=EDGE)
text(x + 36, 26.5, "查到 ＝ 同位置 ＋ 同 ALT ＋ GT 不是 0/0", 14, weight="bold")
text(x + 36, 21, "不要求 read 數一樣：細胞和選殖株的深度不同", 13, MUTED)
text(x + 36, 15.5, "沒查到不代表沒有：單細胞約漏測一成", 13, MUTED)

arrow(158, 62, 164, 62)

# ---------------- step 3: decide per branch ----------------
x = 165
step(x, "3", "整個分支一起判", "不是一個一個 SNV 判")


def bar(y, label, frac, col, note):
    text(x + 6, y + 5, label, 13, ha="left")
    box(x + 6, y - 2, 46, 4.6, fc="#EEECE6", ec="none", r=1)
    if frac > 0:
        box(x + 6, y - 2, 46 * frac, 4.6, fc=col, ec="none", r=1, z=2)
    text(x + 54, y + 0.3, note, 14, col, "bold", ha="left")


text(x + 6, 86, "SC01", 16, weight="bold", ha="left")
bar(77, "共同祖先 7,784 個：查到 6,936", 0.891, TRUNC, "89%")
bar(66, "這個分支 127 個：查到 115", 115 / 127, RED, "91%")
text(x + 36, 58, "和 89% 差不多 → 帶這個分支", 15, GREEN, "bold")

text(x + 6, 49, "SC02", 16, weight="bold", ha="left")
bar(40, "共同祖先 7,784 個：查到 6,578", 0.845, TRUNC, "85%")
bar(29, "EFCD 分支 14 個：查到 0", 0.0, PURPLE, "0%")
text(x + 36, 21.5, "幾乎查不到 → 不帶這個分支", 15, BAD, "bold")

text(x + 36, 14, "≥ 共同祖先查到率的一半 → 帶", 13, INK)
text(x + 36, 9.5, "≤ 兩成 → 不帶；中間 → 不確定", 13, INK)

fig.savefig(sys.argv[1], dpi=150, facecolor=PAPER)
