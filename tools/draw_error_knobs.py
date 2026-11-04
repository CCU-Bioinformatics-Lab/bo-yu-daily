#!/usr/bin/env python3
"""Schematic (not data) of diplosim's three read-error knobs, as on slide 5 of the 2026-11-04 deck.

  base_error           a read shows the other base at the SNV (ref <-> alt); its HP stays
  mistag_rate          a read keeps its base but carries the other HP's tag; same chance at every site
  mistag_concentration same average mistag, but each site draws its own rate, so errors pile up on few sites
Colours follow report_rule.md F-4. diplosim/src/hp.rs applies these after the HP split.
Usage: python3 tools/draw_error_knobs.py OUT_PNG
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED, BG, CARD, LINE, ORANGE = "#1f2a37", "#6b7480", "#f7f6f2", "#ffffff", "#e3e1da", "#c96a1b"
HP1, HP1S, HP2, HP2S, RED = "#2C5F9E", "#8FB3E0", "#D9772B", "#F2B880", "#D23A2E"


def read(ax, x0, x1, y, col, alt, cx, hl=False):
    ax.plot([x0, x1], [y, y], color=col, lw=9, solid_capstyle="round", zorder=2)
    ax.scatter([cx], [y], s=90, zorder=3, color=RED if alt else "white", edgecolors=INK if not alt else "white",
               linewidths=1.5)
    if hl:
        ax.add_patch(FancyBboxPatch((cx - 0.28, y - 0.2), 0.56, 0.4, boxstyle="round,pad=0.02",
                                    fill=False, ec=ORANGE, lw=2.5, zorder=4))


def site(ax, cx, top, reads, label=None):
    """reads: list of (hp, alt, highlight); hp 1/2 decides the row group and colour."""
    ax.plot([cx, cx], [top + 0.35, top - len(reads) * 0.42 - 0.25], color=MUTED, lw=1.2, ls=(0, (2, 3)), zorder=1)
    for i, (hp, alt, hl) in enumerate(reads):
        y = top - i * 0.42
        col = (HP1S if alt else HP1) if hp == 1 else (HP2S if alt else HP2)
        read(ax, cx - 0.9, cx + 0.9, y, col, alt, cx, hl)
    if label:
        ax.text(cx, top + 0.55, label, ha="center", fontsize=12, weight="bold", color=INK)


def arrow(ax, x0, x1, y, text):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=INK))
    ax.text((x0 + x1) / 2, y + 0.22, text, ha="center", fontsize=11.5, color=INK)


def card(ax, title, knob, foot):
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.1, 5.6)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.1, -0.95), 9.8, 6.45, boxstyle="round,pad=0.02,rounding_size=0.25",
                                fc=CARD, ec=LINE, lw=1.5))
    ax.text(0.45, 5.05, title, fontsize=15, weight="bold", color=INK)
    ax.text(0.45, 4.6, knob, fontsize=11, color=MUTED, family="DejaVu Sans Mono")
    ax.text(5, -0.7, foot, ha="center", fontsize=12, weight="bold", color=ORANGE)


fig, axes = plt.subplots(1, 3, figsize=(17, 6.4), dpi=150)
fig.patch.set_facecolor(BG)
fig.subplots_adjust(left=0.02, right=0.98, top=0.8, bottom=0.04, wspace=0.05)

# 1. base error
ax = axes[0]
card(ax, "① 鹼基讀錯", "base_error", "HP 不變，只有 ref／alt 互換")
before = [(1, True, False), (1, True, False), (2, False, False), (2, False, False)]
after = [(1, True, False), (1, False, True), (2, False, False), (2, True, True)]
site(ax, 2.6, 3.6, before, "DNA 上真的是")
arrow(ax, 3.75, 5.25, 2.95, "定序讀錯")
site(ax, 7.4, 3.6, after, "讀出來變成")

# 2. mistag
ax = axes[1]
card(ax, "② HP 標錯", "mistag_rate", "鹼基不變，read 被貼到另一條 HP")
before = [(1, True, False), (1, True, False), (1, True, False), (2, False, False), (2, False, False)]
after = [(1, True, False), (1, True, False), (2, False, False), (2, False, False), (2, True, True)]
site(ax, 2.6, 3.75, before, "真的來自")
arrow(ax, 3.75, 5.25, 2.9, "HP 貼錯")
site(ax, 7.4, 3.75, after, "標記成")
ax.text(5, 0.95, "一條 HP1 帶 alt 的 read，被標成 HP2", ha="center", fontsize=11, color=MUTED)

# 3. concentration: SNV on HP1, 5 alt reads per site; mistagged reads move to HP2 (light orange)
ax = axes[2]
card(ax, "③ 標錯集中", "mistag_concentration", "標錯集中在少數位點；SNV 原本那條 HP 仍較多")
ax.text(0.45, 4.3, "關閉：每個位點機率相同（各 1 條）", fontsize=11.5, weight="bold", color=INK)
ax.text(0.45, 1.95, "打開：各位點機率不同（集中在 B）", fontsize=11.5, weight="bold", color=INK)
for row, (top, picks) in enumerate(((3.6, (1, 1, 1)), (1.5, (0, 2, 0)))):
    for j, n in enumerate(picks):
        cx = 1.9 + j * 3.1
        reads = [1] * (5 - n) + [2] * n
        for i, hp in enumerate(reads):
            y = top - i * 0.22
            ax.plot([cx - 0.95, cx + 0.95], [y, y], color=HP1S if hp == 1 else HP2S, lw=5,
                    solid_capstyle="round", zorder=2)
            ax.scatter([cx], [y], s=28, color=RED, edgecolors="white", linewidths=0.8, zorder=3)
            if hp == 2:
                ax.add_patch(FancyBboxPatch((cx - 0.22, y - 0.11), 0.44, 0.22, boxstyle="round,pad=0.01",
                                            fill=False, ec=ORANGE, lw=1.8, zorder=4))
        ax.text(cx, top - 5 * 0.22 - 0.2, f"HP1 {5 - n}｜HP2 {n}", ha="center", fontsize=10.5, color=MUTED)
        if row == 0:
            ax.text(cx, top + 0.22, f"位點 {'ABC'[j]}", ha="center", fontsize=11, color=MUTED)
ax.text(5, -0.25, "極少數位點（約 0.7%）錯到超過一半，看起來像整個翻到另一條 HP", ha="center", fontsize=10.5,
        color=MUTED)

handles = [plt.Line2D([0], [0], color=c, lw=7) for c in (HP1, HP1S, HP2, HP2S)]
handles += [plt.Line2D([0], [0], marker="o", ls="", markerfacecolor=RED, markeredgecolor="white", markersize=10),
            plt.Line2D([0], [0], marker="o", ls="", markerfacecolor="white", markeredgecolor=INK, markersize=10),
            plt.Rectangle((0, 0), 1, 1, fill=False, ec=ORANGE, lw=2)]
fig.legend(handles, ["HP1 read", "HP1 帶 alt", "HP2 read", "HP2 帶 alt", "alt", "ref", "錯誤造成的改變"],
           loc="upper center", bbox_to_anchor=(0.5, 0.885), ncol=7, frameon=False, fontsize=11)
fig.suptitle("diplosim 的三個 read 錯誤旋鈕：讀錯鹼基、貼錯 HP、錯誤集中在少數位點", fontsize=17, weight="bold",
             x=0.02, ha="left", y=0.975, color=INK)
fig.savefig(sys.argv[1], facecolor=BG)
print(sys.argv[1])
