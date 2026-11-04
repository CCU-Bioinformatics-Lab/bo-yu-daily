"""Draw the HG008 clone tree with the truth-tree event types found on real branches.

Numbers came from lab_report/2026-10-27_hg008_clone_tree_hp/ (deleted 2026-11-04, never tracked; 8 single-cell-derived clones,
DeepSomatic + PURPLE + bulk ONT haplotypes); event numbers match the stress truth tree (slide 8).
Topology (updated 2026-10-27 with the 119 PTA single cells, lab_report/2026-10-27_hg008_sc_tree_check/):
truncal -> {3E4 lineage, 7-clone branch (303 SNVs absent from the 8 3E4-sister cells)};
7-clone branch -> {2D6,2E6}, {SC9,SC14,SC24,SC28} -> {SC14,SC28}, SC6. Order inside the 7-clone branch
beyond these clades is not resolved. Green labels = single cells (of 119) carrying the branch.

Usage: python3 tools/draw_hg008_clone_tree.py OUT.png
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

HP1, HP2 = "#2C5F9E", "#D9772B"   # report_rule F-4
LOSS, INK, GREY, EVENT = "#B4442F", "#1F2A37", "#6B7480", "#C53030"
CLONE = {"normal": "#9AA3AE", "trunk": "#3B5B7A", "core": "#5B7FA3", "g1": "#7B5EA7", "g2": "#2E8B8B",
         "g4": "#6BA5A5", "leaf": "#4A5568"}
SC = "#2E7D4F"

# node: (x, y, label, sublabel, colour)
NODES = {
    "normal": (50, 70, "normal", "HG008-N", CLONE["normal"]),
    "trunk": (50, 62, "truncal clone", "7,985 SNV", CLONE["trunk"]),
    "core": (38, 54, "7 株共同枝", "303 SNV", CLONE["core"]),
    "3E4": (86, 54, "3E4", "1,166", CLONE["leaf"]),
    "g1": (14, 46, "{2D6, 2E6}", "59 SNV", CLONE["g1"]),
    "g4": (46, 46, "{SC9, SC14, SC24, SC28}", "24 SNV", CLONE["g4"]),
    "SC6": (72, 46, "SC6", "877", CLONE["leaf"]),
    "2D6": (8, 38, "2D6", "476", CLONE["leaf"]),
    "2E6": (20, 38, "2E6", "646", CLONE["leaf"]),
    "g2": (37, 38, "{SC14, SC28}", "146 SNV", CLONE["g2"]),
    "SC9": (52, 38, "SC9", "495", CLONE["leaf"]),
    "SC24": (61, 38, "SC24", "468", CLONE["leaf"]),
    "SC14": (32, 30, "SC14", "540", CLONE["leaf"]),
    "SC28": (42, 30, "SC28", "544", CLONE["leaf"]),
}
EDGES = [("normal", "trunk"), ("trunk", "core"), ("trunk", "3E4"), ("core", "g1"), ("core", "g4"),
         ("core", "SC6"), ("g1", "2D6"), ("g1", "2E6"), ("g4", "g2"), ("g4", "SC9"), ("g4", "SC24"),
         ("g2", "SC14"), ("g2", "SC28")]
# single-cell support: (node, text) placed right of the node
SC_LABELS = [("trunk", "單細胞 119／119"), ("core", "單細胞 111／119"), ("3E4", "3E4 姊妹細胞 8／119"),
             ("g1", "前段 11 SNV：16／119"), ("g4", "單細胞 48／119"), ("g2", "16／119")]

# event cards: (x, y_top, width, [(number, text, colour)]); number "H" = card header
CARDS = [
    (61, 73.5, 36, [("①", "purity ≈ 1（細胞株；PURPLE 0.99，8 個 clone 都是）", INK)]),
    (0.5, 24.5, 31, [
        ("H", "{2D6, 2E6} 枝", CLONE["g1"]),
        ("②", "subclonal 單一 HP gain：chr2 約 32 Mb，1+1 → 2+1", INK),
        ("⑦", "gain 區 truncal SNV：mult 2 ×56 在被 gain 的 HP，", INK),
        ("", "mult 1 ×46 在另一條 HP", INK),
        ("④", "bulk CCF ≈ 0.03（bulk VAF 中位 0.015）", INK),
        ("H", "2E6", CLONE["leaf"]),
        ("③", "chr10 deletion，遺失 72 個 SNV（HP1）", LOSS),
    ]),
    (32.5, 24.5, 22, [
        ("H", "{SC14, SC28} 枝", CLONE["g2"]),
        ("⑤", "枝上 SNV 分兩條 HP（1+1 區）", INK),
        ("", "HP1 24 個", HP1),
        ("", "HP2 27 個", HP2),
        ("④", "低 CCF：bulk CCF ≈ 0.14", INK),
    ]),
    (55.5, 24.5, 15.5, [
        ("H", "3E4", CLONE["leaf"]),
        ("③", "chr10、chr11 deletion", LOSS),
        ("", "遺失 108 個 SNV（HP2）", LOSS),
    ]),
    (72, 24.5, 27.5, [
        ("H", "SC6", CLONE["leaf"]),
        ("⑥", "chr1q cnLOH 約 100 Mb，1+1 → 2+0", INK),
        ("③", "遺失 205 個 SNV，全在 HP1（被取代的那條）", LOSS),
        ("③", "chrX deletion，遺失 161 個 SNV（HP2）", LOSS),
        ("⑦", "SC6 自己的 SNV 在 cnLOH 區：", INK),
        ("", "mult 2 ×75（cnLOH 前）、mult 1 ×22（後）", INK),
    ]),
]


def node(ax, key):
    x, y, label, sub, col = NODES[key]
    w = {"g4": 16, "core": 10}.get(key, 9.5 if key in ("trunk", "g1", "g2", "normal") else 7)
    ax.add_patch(FancyBboxPatch((x - w / 2, y - 2.3), w, 4.6, boxstyle="round,pad=0.25,rounding_size=1.2",
                                fc=col, ec="none", zorder=3))
    ax.text(x, y + 0.8, label, ha="center", va="center", fontsize=11, color="white", weight="bold", zorder=4)
    ax.text(x, y - 1.2, sub, ha="center", va="center", fontsize=9, color="white", zorder=4)


def card(ax, x, ytop, w, rows):
    h = 1.2 + 2.3 * len(rows)
    ax.add_patch(FancyBboxPatch((x, ytop - h), w, h, boxstyle="round,pad=0.2,rounding_size=0.8",
                                fc="#FDFDFB", ec="#D9DDE3", lw=1, zorder=2))
    for i, (num, text, col) in enumerate(rows):
        yy = ytop - 1.5 - 2.3 * i
        if num == "H":
            ax.text(x + 1.0, yy, text, ha="left", va="center", fontsize=11, color=col, weight="bold", zorder=4)
            continue
        if num:
            ax.text(x + 1.2, yy, num, ha="center", va="center", fontsize=12, color=EVENT, weight="bold", zorder=4)
        if col in (HP1, HP2):
            ax.text(x + 2.6, yy, f" {text} ", ha="left", va="center", fontsize=10, color="white", weight="bold",
                    zorder=4, bbox=dict(boxstyle="round,pad=0.25", fc=col, ec="none"))
        else:
            ax.text(x + 2.6, yy, text, ha="left", va="center", fontsize=10, color=col, zorder=4)


def main(out):
    fig, ax = plt.subplots(figsize=(18, 13.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(-1, 80)
    ax.axis("off")
    ax.text(0.5, 78.5, "HG008 真實 clone 樹：真值樹的 ②–⑦ 事件都出現在 subclone 上", fontsize=18, weight="bold",
            color=INK, va="center")
    ax.text(0.5, 76.2, "8 株單細胞衍生 clone（第 14、19 代）＋ bulk ONT 第 23 代＋ 119 顆 PTA 單細胞（第 23 代）。"
            "節點下的數字是該枝的 SNV 數；葉節點是各 clone 自己的 private SNV；綠字＝帶這條枝的單細胞數。", fontsize=10.5, color=GREY, va="center")
    for a, b in EDGES:
        xa, ya = NODES[a][:2]
        xb, yb = NODES[b][:2]
        ax.plot([xa, xb], [ya - 2.3, yb + 2.3], color="#4A5568", lw=2, zorder=1)
    for k in NODES:
        node(ax, k)
    for k, text in SC_LABELS:
        x, y = NODES[k][:2]
        w = {"g4": 16, "core": 10}.get(k, 9.5 if k in ("trunk", "g1", "g2", "normal") else 7)
        ax.text(x + w / 2 + 0.8, y, text, ha="left", va="center", fontsize=9.5, color=SC, weight="bold", zorder=4)
    for c in CARDS:
        card(ax, *c)
    ax.text(0.5, 3.0, "⑤ 8 條 private 枝都有 phase block 同時含 HP1、HP2 的 SNV（block 內兩條 HP 都有：實際 0.25–0.57，隨機 0.54–0.61）。"
            "HP1／HP2＝HG008-N assembly 的 hap1／hap2，每條染色體各自定義。", fontsize=9.5, color=INK)
    ax.text(0.5, 0.8, "限制：細胞株的體外演化，不是病人腫瘤；CN 是 PURPLE 推論；7 株共同枝下 SC6 與各 clade 的先後未解析；private 枝在單細胞中看不到。"
            "資料：GIAB HG008（DeepSomatic、PURPLE、V0.4 phasing、PTA 單細胞 VCF）；lab_report/2026-10-27_hg008_clone_tree_hp/、2026-10-27_hg008_sc_tree_check/。",
            fontsize=9.5, color=GREY)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")


if __name__ == "__main__":
    main(sys.argv[1])
