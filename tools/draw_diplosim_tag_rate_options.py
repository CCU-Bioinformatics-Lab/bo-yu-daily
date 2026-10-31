"""Draw one PNG per candidate for giving each diplosim site its own tag rate (方案 ②).

Output: diplosim/docs/figs/tag_rate_option_{1,2,3}.png
The histogram panel uses the real HCC1395 t50_n00 depths (ClairS HC sites, depth >= 20, caller
filter) and draws each site's tagged reads as Binomial(depth, site tag rate). Model values
(mean 0.862, kappa 1, 3.5% unphasable) are picked to match HCC1395 and are illustrative only.
"""
import csv
import random
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "diplosim" / "docs" / "figs"
REAL = ROOT / "lab_report" / "2026-10-30_diplosim_ppc_hcc1395" / "tables" / "real_per_snv.tsv"

INK, MUTED, LINE = "#17201D", "#5B6864", "#CDD5D2"
CON, CON_SOFT = "#2C6E72", "#E1EEEE"
HP1, HP2, HP0 = "#2D5EA6", "#BF522E", "#A3ADA9"
ADD, ADD_SOFT, DEL = "#2C7A4C", "#E3F1E8", "#AE3838"
REAL_C = "#17201D"

MEAN, KAPPA, UNPHASABLE, BLOCK = 0.862, 1.0, 0.035, 20
BINS = [0, 0.05, 0.2, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0001]
BIN_LABELS = ["<0.05", "0.05–0.2", "0.2–0.5", "0.5–0.7", "0.7–0.8", "0.8–0.9", "0.9–0.95", "≥0.95"]


def real_sites():
    depth, frac = [], []
    with open(REAL) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            v = [int(r[k]) for k in ("ref1", "alt1", "ref2", "alt2", "ref0", "alt0")]
            d, a = sum(v), v[1] + v[3] + v[5]
            if d < 20 or a < 3 or a / d < 0.08:
                continue
            depth.append(d)
            frac.append((d - v[4] - v[5]) / d)
    return depth, frac


def rate_beta(rng, _i):
    return rng.betavariate(KAPPA * MEAN, KAPPA * (1 - MEAN))


def rate_two_class(rng, _i):
    return 0.0 if rng.random() < UNPHASABLE else MEAN / (1 - UNPHASABLE)


def simulate(depths, rate_of, seed=1):
    rng = random.Random(seed)
    out = []
    for i, d in enumerate(depths):
        p = rate_of(rng, i)
        out.append(sum(rng.random() < p for _ in range(d)) / d)
    return out


def block_rates(n, seed=2):
    rng = random.Random(seed)
    rates = []
    while len(rates) < n:
        rates += [rate_beta(rng, 0)] * BLOCK
    return rates[:n]


def hist(x):
    return [sum(lo <= v < hi for v in x) / len(x) for lo, hi in zip(BINS, BINS[1:])]


def summary(x):
    return statistics.pstdev(x), sum(v >= 0.95 for v in x) / len(x), sum(v < 0.05 for v in x) / len(x)


def box(ax, x, y, w, h, fc, ec, lw=1.2, r=0.012):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, transform=ax.transAxes))


def arrow(ax, x0, y0, x1, y1, color=MUTED):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14,
                                 color=color, lw=1.4, transform=ax.transAxes))


def draw_steps(ax, steps):
    ax.text(0.03, 0.80, "步驟", fontsize=13, color=MUTED, weight="bold", transform=ax.transAxes)
    n = len(steps)
    top, bottom, h = 0.75, 0.30, 0.075
    gap = (top - bottom - n * h) / max(n - 1, 1)
    for i, (label, src, kind) in enumerate(steps):
        y = top - h - i * (h + gap)
        fc, ec = (CON_SOFT, CON) if kind == "con" else (ADD_SOFT, ADD)
        box(ax, 0.03, y, 0.27, h, fc, ec)
        ax.text(0.042, y + h * 0.62, label, fontsize=12, color=INK, va="center", transform=ax.transAxes)
        ax.text(0.042, y + h * 0.24, src, fontsize=9.5, color=ec, va="center", transform=ax.transAxes)
        if i < n - 1:
            arrow(ax, 0.165, y - 0.004, 0.165, y - gap + 0.004)


def draw_sites(ax, kind):
    """Six sites as columns of 10 reads; colour = tagged, grey = HP0."""
    x0 = 0.33
    title = {"beta": "位點示意：每個位點各自抽 tag 機率", "two": "位點示意：可 phase／不可 phase",
             "block": "位點示意：同一個 PS block 共用 tag 機率"}[kind]
    ax.text(x0, 0.80, title, fontsize=13, color=MUTED, weight="bold", transform=ax.transAxes)
    rates = {"beta": [0.98, 0.91, 0.55, 1.0, 0.25, 0.86], "two": [0.9, 0.9, 0.0, 0.9, 0.9, 0.0],
             "block": [0.95, 0.95, 0.95, 0.35, 0.35, 0.35]}[kind]
    rng = random.Random(7)
    for s, p in enumerate(rates):
        cx = x0 + 0.02 + s * 0.048
        n_tag = round(p * 10)
        cells = [True] * n_tag + [False] * (10 - n_tag)
        rng.shuffle(cells)
        for k, tagged in enumerate(cells):
            y = 0.72 - k * 0.036
            c = (HP1 if k % 2 else HP2) if tagged else HP0
            ax.plot([cx - 0.016, cx + 0.016], [y, y], color=c, lw=4, solid_capstyle="round", transform=ax.transAxes)
        ax.text(cx, 0.34, f"{p:.2f}", fontsize=10.5, color=INK, ha="center", transform=ax.transAxes)
        ax.text(cx, 0.31, f"s{s + 1}", fontsize=9.5, color=MUTED, ha="center", transform=ax.transAxes)
    ax.text(x0, 0.275, "數字＝該位點的 tag 機率", fontsize=10, color=MUTED, transform=ax.transAxes)
    if kind == "two":
        for s in (2, 5):
            cx = x0 + 0.02 + s * 0.048
            box(ax, cx - 0.022, 0.37, 0.044, 0.38, "none", DEL, lw=1.4, r=0.006)
        ax.text(x0 + 0.17, 0.765, "紅框＝不可 phase（全部 HP0）", fontsize=10, color=DEL, transform=ax.transAxes)
    if kind == "block":
        for b, (a, z) in enumerate(((0, 2), (3, 5))):
            xa, xz = x0 + 0.02 + a * 0.048 - 0.02, x0 + 0.02 + z * 0.048 + 0.02
            ax.plot([xa, xa, xz, xz], [0.755, 0.765, 0.765, 0.755], color=CON, lw=1.4, transform=ax.transAxes)
            ax.text((xa + xz) / 2, 0.772, f"PS block {b + 1}", fontsize=10, color=CON, ha="center", transform=ax.transAxes)


def draw_hist(fig, model, real, current, label):
    ax = fig.add_axes([0.665, 0.31, 0.31, 0.44])
    xs = range(len(BINS) - 1)
    hm, hr, hc = hist(model), hist(real), hist(current)
    ax.bar([x - 0.2 for x in xs], hr, width=0.4, color="white", edgecolor=REAL_C, lw=1.3, label="真實 HCC1395")
    ax.bar([x + 0.2 for x in xs], hm, width=0.4, color=ADD, label=label)
    ax.plot(list(xs), hc, "o-", color=HP0, ms=4, lw=1.2, label="現在（prop_tagged 0.8）")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(BIN_LABELS, fontsize=8.5, rotation=30)
    ax.set_ylabel("位點比例", fontsize=10)
    ax.set_xlabel("位點的 tag 比例（帶 tag 的 read ÷ depth）", fontsize=10)
    ax.tick_params(labelsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    sd_r, hi_r, lo_r = summary(real)
    sd_m, hi_m, lo_m = summary(model)
    sd_c, hi_c, lo_c = summary(current)
    fig.text(0.665, 0.795, "位點 tag 比例分布（用真實 depth 抽樣）", fontsize=13, color=MUTED, weight="bold")
    rows = [("真實", sd_r, hi_r, lo_r), ("此方案", sd_m, hi_m, lo_m), ("現在", sd_c, hi_c, lo_c)]
    lines = [f"{name}：SD {sd:.3f}・≥0.95 {hi:.2f}・<0.05 {lo:.3f}" for name, sd, hi, lo in rows]
    fig.text(0.665, 0.765, "\n".join(lines), fontsize=9.5, color=INK, va="top", linespacing=1.4)
    ax.set_position([0.665, 0.31, 0.31, 0.37])


def draw_notes(ax, opt):
    cols = [("優點", opt["pros"], ADD), ("風險", opt["cons"], DEL), ("怎麼驗證", opt["check"], CON)]
    for i, (head, items, c) in enumerate(cols):
        x = 0.03 + i * 0.325
        box(ax, x, 0.03, 0.30, 0.17, "white", LINE)
        ax.text(x + 0.012, 0.165, head, fontsize=12.5, color=c, weight="bold", transform=ax.transAxes)
        for j, t in enumerate(items):
            ax.text(x + 0.012, 0.125 - j * 0.036, "・" + t, fontsize=10.5, color=INK, transform=ax.transAxes)


OPTIONS = [
    dict(
        no="①", title="每個位點從 Beta 分布抽 tag 機率", tag="建議", kind="beta",
        steps=[("depth、alt、HP 拆分、讀錯", "沿用 diplosim 現有步驟", "con"),
               ("每個位點抽 p ~ Beta(κm, κ(1−m))", "新寫：m = prop_tagged，新參數 κ", "new"),
               ("每條 read 以 1 − p 變成 HP0", "改寫：原本用固定的 prop_tagged", "new")],
        legend="此方案（m 0.862、κ 1）",
        pros=["只加 1 個參數 tag_concentration（κ）", "κ = ∞ 時等於現在，預設輸出不變", "主體與 SD 都能對上"],
        cons=["幾乎沒有 tag 的位點偏少（左尾不夠）", "m、κ 是看 HCC1395 選的，只當實驗設定", "相鄰位點各自獨立"],
        check=["單元測試：κ = ∞ 時輸出逐位元相同", "PPC：HP0、tag SD、tag < 0.5 三項", "比較這張分布圖"],
    ),
    dict(
        no="②", title="兩類位點：可 phase／不可 phase", tag="", kind="two",
        steps=[("depth、alt、HP 拆分、讀錯", "沿用 diplosim 現有步驟", "con"),
               ("每個位點以 q 的機率設為不可 phase", "新寫：新參數 prop_site_unphasable", "new"),
               ("不可 phase：全部 HP0；其餘照 prop_tagged", "改寫 untag", "new")],
        legend="此方案（q 0.035、其餘 0.893）",
        pros=["物理意義清楚：附近沒有 het SNP、PS block 外", "左尾（<0.05）可以準確對上", "q = 0 時等於現在"],
        cons=["只有兩個值，中間 0.2–0.9 的位點做不出來", "SD 可能不夠", "要補中間就得再加參數"],
        check=["單元測試：q = 0 時輸出逐位元相同", "PPC：同 ①", "比較這張分布圖"],
    ),
    dict(
        no="③", title="PS block：相鄰位點共用 tag 機率", tag="", kind="block",
        steps=[("depth、alt、HP 拆分、讀錯", "沿用 diplosim 現有步驟", "con"),
               ("位點依座標分成 PS block", "新寫：需要座標（10-28 暫緩）", "new"),
               ("每個 block 抽 p ~ Beta，block 內共用", "新寫", "new"),
               ("每條 read 以 1 − p 變成 HP0", "改寫 untag", "new")],
        legend=f"此方案（每 {BLOCK} 個位點一個 block）",
        pros=["最接近真實機制", "之後做同 read 共現也需要 block", "相鄰位點的 tag 比例會相關"],
        cons=["位置目前只是標籤，沒有「相鄰」", "要先決定座標與 block 長度", "PPC 統計量不看相鄰，分布和 ① 一樣"],
        check=["相鄰位點 tag 比例的相關係數 > 0", "PPC：同 ①", "要先有看相鄰關係的統計量"],
    ),
]


def draw(opt, real_depth, real_frac, current, path):
    model = (simulate(real_depth, rate_beta) if opt["kind"] == "beta" else
             simulate(real_depth, rate_two_class) if opt["kind"] == "two" else
             simulate(real_depth, lambda rng, i, r=block_rates(len(real_depth)): r[i]))
    fig = plt.figure(figsize=(16, 9), dpi=110)
    fig.patch.set_facecolor("#F2F4F3")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(0.03, 0.92, f"方案 {opt['no']}", fontsize=24, color=INK, weight="bold", transform=ax.transAxes)
    ax.text(0.115, 0.92, opt["title"], fontsize=21, color=INK, transform=ax.transAxes)
    if opt["tag"]:
        box(ax, 0.88, 0.915, 0.08, 0.045, ADD, ADD)
        ax.text(0.92, 0.937, opt["tag"], fontsize=13, color="white", ha="center", va="center",
                weight="bold", transform=ax.transAxes)
    ax.text(0.03, 0.875, "diplosim tag 機制（方案 ②）：讓每個位點有自己的 tag 比例　｜　"
            "藍綠框＝沿用，綠框＝新寫／改寫　｜　分布圖的模型值是看 HCC1395 選的，只供示意",
            fontsize=11, color=MUTED, transform=ax.transAxes)
    draw_steps(ax, opt["steps"])
    draw_sites(ax, opt["kind"])
    draw_hist(fig, model, real_frac, current, opt["legend"])
    draw_notes(ax, opt)
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    depth, frac = real_sites()
    current = simulate(depth, lambda rng, i: 0.8)
    for i, opt in enumerate(OPTIONS, 1):
        p = OUT / f"tag_rate_option_{i}.png"
        draw(opt, depth, frac, current, p)
        print(p)


if __name__ == "__main__":
    main()
