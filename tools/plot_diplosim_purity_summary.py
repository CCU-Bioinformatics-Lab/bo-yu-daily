#!/usr/bin/env python3
"""Summary figures for the 2026-10-31..11-01 diplosim purity holdout work.

progress.png: statistics inside the simulated 95% band (of 13) and mean |rel| per step, one line per purity.
pipeline.png: the comparison pipeline as it stands after the last step, with the source of every knob.
Usage: python3 tools/plot_diplosim_purity_summary.py OUT_DIR
"""
import csv
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED, GRID, BG = "#17201D", "#5B6864", "#D9DEDC", "#FFFFFF"
SUBS = [("t50_n00", "t50（0.97）", "#0d366b"), ("t40_n10", "t40（0.70）", "#256abf"),
        ("t30_n20", "t30（0.48）", "#3987e5"), ("t20_n30", "t20（0.29）", "#86b6ef"),
        ("t10_n40", "t10（0.14）", "#eb6834")]
STEPS = [
    ("2026-10-31_diplosim_purity_holdout_v2", "① 單一值\n（v2 起點）"),
    ("2026-11-01_diplosim_split_alt_mistag", "② 逐位點\nmistag"),
    ("2026-11-01_diplosim_knob_ranges", "③ 旋鈕\n範圍抽樣"),
    ("2026-11-01_diplosim_matched_normal", "④ 配對 normal\n＋ClairS 規則"),
    ("2026-11-01_diplosim_purity_normal_share", "⑤ purity 換算\n加入 c"),
    ("2026-11-01_diplosim_detection_curve", "⑥ ClairS\n偵測曲線"),
]
STATS = ["depth_VMR", "VAF_q10", "VAF_q50", "VAF_q90", "VAF_frac_gt_0.6", "HP0_frac_pooled", "tag_frac_SD_sites",
         "tag_frac_lt_0.5_sites", "split_alt_frac", "inHP_VAF_q50", "minorHP_depth_q50", "minorHP_depth_lt_0.1",
         "alt_on_minorHP"]


def step_scores(step):
    root = Path("lab_report") / step
    inside, rel = {}, {}
    for sub, _, _ in SUBS:
        rows = {r["statistic"]: r for r in csv.DictReader(open(root / sub / "tables" / "ppc_stats.tsv"), delimiter="\t")}
        inside[sub] = sum(rows[k]["verdict"] == "in" for k in STATS)
        rel[sub] = statistics.fmean(abs(float(rows[k]["sim_median"]) - float(rows[k]["real"])) / abs(float(rows[k]["real"]))
                                    for k in STATS)
    return inside, rel


def progress(out):
    scores = [step_scores(s) for s, _ in STEPS]
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6), dpi=150)
    fig.subplots_adjust(top=0.80, bottom=0.2, left=0.05, right=0.98, wspace=0.16)
    x = range(len(STEPS))
    for ax, idx, title, ylab in ((axes[0], 0, "落在模擬 95% 區間內的統計量（共 13 項）", "項數"),
                                 (axes[1], 1, "13 項平均 |相對差距|（越低越好）", "平均 |rel|")):
        for sub, label, col in SUBS:
            ys = [s[idx][sub] for s in scores]
            ax.plot(x, ys, color=col, lw=2.2, marker="o", ms=7, label=label)
            ax.text(len(STEPS) - 1 + 0.12, ys[-1], f"{ys[-1]:.0f}" if idx == 0 else f"{ys[-1]:.2f}",
                    va="center", fontsize=9, color=INK)
        ax.set_xticks(list(x))
        ax.set_xticklabels([lab for _, lab in STEPS], fontsize=9, color=INK)
        ax.set_title(title, loc="left", fontsize=13, weight="bold", color=INK)
        ax.set_ylabel(ylab, color=MUTED)
        ax.grid(axis="y", color=GRID, lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=MUTED)
        ax.set_xlim(-0.3, len(STEPS) - 0.5)
    axes[0].set_ylim(0, 13.5)
    axes[1].axhline(0.1, color=MUTED, lw=1, ls="--")
    axes[1].text(-0.25, 0.108, "目標 |rel| < 0.1", fontsize=9, color=MUTED)
    axes[0].legend(frameon=False, fontsize=9, loc="lower right", title="subsample（purity）", title_fontsize=9)
    fig.suptitle("diplosim purity holdout：每一步改動後，5 個 HCC1395 purity 的對齊程度", fontsize=16,
                 weight="bold", x=0.05, ha="left", y=0.97, color=INK)
    fig.text(0.05, 0.885, "②–⑥ 都在 2026-11-01 完成。③ 起通過標準改為「真實值落在模擬區間內」；區間變寬會讓 ① → ③ 的項數上升，"
             "所以右圖的平均相對差距要一起看。", fontsize=10, color=MUTED)
    fig.savefig(out / "progress.png", facecolor=BG)


def box(ax, x, y, w, h, title, body, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02", fc=color, ec=INK, lw=1))
    ax.text(x + 0.012, y + h - 0.03, title, fontsize=11, weight="bold", color=INK, va="top")
    ax.text(x + 0.012, y + h - 0.085, body, fontsize=8.6, color=INK, va="top", linespacing=1.45)


def pipeline(out):
    fig = plt.figure(figsize=(15, 6.2), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.95, "比較流程（⑥ 之後）：模擬端每一層都對應真實資料的一個步驟", fontsize=16, weight="bold", color=INK)
    ax.text(0.02, 0.905, "灰框＝diplosim 本身（沒改）；藍框＝只在比較腳本 tools/diplosim_ppc_hcc1395.py；"
            "每個旋鈕都寫出範圍與來源。", fontsize=10, color=MUTED)
    W, H, Y = 0.162, 0.58, 0.22
    xs = [0.025 + i * 0.195 for i in range(5)]
    sim_c, scr_c = "#E8EBEA", "#DCE9F8"
    box(ax, xs[0], Y, W, H, "1. diplosim 產生 tumor bulk",
        "同一套 CONIPHER 流程\n（樹、CN、SNV、HP 計數）\n\npurity：換算加入 c 1.2–1.6%\n  t10 0.1433–0.1456\n\n6 個旋鈕範圍抽樣：\n"
        "  φ 0.006–0.025\n  （normal 樣本量測）\n  base error 0.001–0.01\n  mistag 0.005–0.015\n  prop_tagged 0.80–0.90\n"
        "  prop_pos_lost 0.40–0.50\n  prop_truncal 0.6–0.9", sim_c)
    box(ax, xs[1], Y, W, H, "2. 配對 normal 樣本",
        "同一棵樹、同一組 clone\npurity = c，depth 25.1×\n\nc 0.5–2.5%\n  （normal alt 隨 tumor VAF\n   上升的量測）\n"
        "normal base error 0–0.001\n\n真實對應：ClairS 用的\nnormal_25x＝t00_n25\n（總鹼基數逐位相同）", scr_c)
    box(ax, xs[2], Y, W, H, "3. ClairS normal 規則",
        "刪掉 SNV，若：\n  normal depth > 4\n  normal AF ≥ 0.05\n  tumor AF < 6 × normal AF\n\n來源：ClairS v0.4.1\n"
        "extract_pair_candidates.py\n:439-450（固定值，\n不是旋鈕）", scr_c)
    box(ax, xs[3], Y, W, H, "4. ClairS 偵測曲線",
        "依 alt 數決定留下的機率\nP(叫出 | alt)\n\n每個 seed 在 t10 曲線與\nt40 曲線之間抽一條\n\n"
        "alt 5：0.11（t10）–0.36（t40）\nalt ≥ 12：約 0.95–0.99\n\n來源：t50 call 在 t40–t10\nCRAM 上的 pileup", scr_c)
    box(ax, xs[4], Y, W, H, "5. 兩邊同樣的門檻與統計",
        "alt ≥ 5、VAF ≥ 0.10\n（ClairS call 的 1% 分位）\n\n13 項統計量：\n  VAF 分位、depth VMR、\n  HP0、tag 比例、split alt、\n"
        "  minor HP、HP 內 VAF…\n\n通過：真實值落在\n200 個 seed 的 95% 區間", sim_c)
    for i in range(4):
        ax.annotate("", xy=(xs[i + 1] - 0.014, Y + H / 2), xytext=(xs[i] + W + 0.014, Y + H / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.text(0.02, 0.12, "真實端：ClairS v0.4.1（tumor 各 subsample ＋ normal_25x）→ PASS ∩ HC → 我們自己的 pileup → 同一個門檻與 13 項統計。"
            "第 2–4 層只在模擬端做，因為真實端已經跑過 ClairS。", fontsize=10, color=INK)
    ax.text(0.02, 0.07, "限制：c、偵測曲線、normal 規則都只來自 ClairS v0.4.1 + HCC1395 ONT，不當 diplosim 預設值；"
            "t10、t40 的曲線就是從這兩個 holdout 樣本量的。", fontsize=10, color=MUTED)
    fig.savefig(out / "pipeline.png", facecolor=BG)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    progress(out)
    pipeline(out)
    print(out / "progress.png", out / "pipeline.png")
