#!/usr/bin/env python3
"""Illustration: how diplosim's prop_tagged and tag_concentration change unphased reads across sites.

Three panels of 10 sites each (illustration, not measured data):
  1. prop_tagged 0.8, tag_concentration off -> every site 80% tagged
  2. prop_tagged 0.6, tag_concentration off -> every site 60% tagged (the average moves)
  3. prop_tagged 0.8, tag_concentration 1   -> each site its own rate from Beta(0.8, 0.2); average still ~0.8
Tagged reads are split HP1:HP2 = 1:1 (CN 1:1). diplosim/src/hp.rs site_rate does the Beta draw.
Usage: python3 tools/draw_tag_knobs.py OUT_PNG
"""
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED, BG = "#1f2a37", "#6b7480", "#f7f6f2"
HP1, HP2, HP0 = "#2C5F9E", "#D9772B", "#9AA3AE"
N = 10


def beta_rates(mean, kappa, seed):
    rng = random.Random(seed)
    for _ in range(1000):   # pick a draw whose average sits near the mean, so the panel reads clearly
        r = [rng.betavariate(kappa * mean, kappa * (1 - mean)) for _ in range(N)]
        if abs(sum(r) / N - mean) < 0.02:
            return r
    return r


panels = [
    ("prop_tagged 0.8｜tag_concentration 關閉", "每個位點都一樣：80% 分得出 HP", [0.8] * N),
    ("prop_tagged 0.6｜tag_concentration 關閉", "平均往下移：每個位點都 60%", [0.6] * N),
    ("prop_tagged 0.8｜tag_concentration 打開", "平均仍約 80%，但位點之間差很多", beta_rates(0.8, 1.0, 7)),
]

fig, axes = plt.subplots(1, 3, figsize=(16, 6.2), dpi=150, sharey=True)
fig.patch.set_facecolor(BG)
fig.subplots_adjust(top=0.72, bottom=0.2, left=0.05, right=0.99, wspace=0.08)
for ax, (title, sub, rates) in zip(axes, panels):
    ax.set_facecolor(BG)
    x = range(1, N + 1)
    hp = [r / 2 for r in rates]
    ax.bar(x, hp, color=HP1, width=0.75, edgecolor=BG, linewidth=1.5)
    ax.bar(x, hp, bottom=hp, color=HP2, width=0.75, edgecolor=BG, linewidth=1.5)
    ax.bar(x, [1 - r for r in rates], bottom=rates, color=HP0, width=0.75, edgecolor=BG, linewidth=1.5)
    mean = sum(rates) / N
    ax.axhline(mean, color=INK, lw=1.5, ls="--")
    ax.text(N + 0.45, mean, f"平均 {mean:.2f}", va="bottom", ha="right", fontsize=11, color=INK)
    ax.set_title(title, loc="left", fontsize=13, weight="bold", color=INK, pad=34)
    ax.text(0.0, 1.025, sub, transform=ax.transAxes, fontsize=11.5, color=MUTED, va="bottom")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{i}" for i in x], fontsize=10, color=MUTED)
    ax.set_xlabel("位點", color=MUTED, fontsize=11)
    ax.set_ylim(0, 1.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED)
axes[0].set_ylabel("該位點 read 的比例", color=MUTED, fontsize=11)

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (HP1, HP2, HP0)]
fig.legend(handles, ["HP1", "HP2", "unphased（分不出 HP）"], loc="lower center", ncol=3, frameon=False, fontsize=11)
fig.suptitle("prop_tagged 調「平均有多少 read 分得出 HP」；tag_concentration 調「各位點之間差多少」",
             fontsize=15, weight="bold", x=0.05, ha="left", y=0.97, color=INK)
fig.text(0.05, 0.875, "示意：10 個位點，HP1：HP2 固定 1：1；第 3 張的位點比例由隨機亂數產生，不是實測。"
         "兩個旋鈕都只動「分得出／分不出 HP」，不動 HP1 與 HP2 之間的比例。",
         fontsize=11, color=MUTED)
fig.savefig(sys.argv[1], facecolor=BG)
print(sys.argv[1])
