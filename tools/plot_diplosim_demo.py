"""Show what each new diplosim parameter adds, using three runs of the same seed.

Usage: python3 tools/plot_diplosim_demo.py RUN_B0_T1 RUN_B05_T1 RUN_B05_T08 OUT_PNG
  RUN_B0_T1   --prop-snv-on-b 0   --prop-tagged 1   (CONIPHER-equivalent labels)
  RUN_B05_T1  --prop-snv-on-b 0.5 --prop-tagged 1
  RUN_B05_T08 defaults (--prop-snv-on-b 0.5 --prop-tagged 0.8)
A seed fixes the tree, depth and alt counts across these runs; only allele labels and HP tags differ.
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

INK, MUTED, LINE, BAND = "#17201D", "#5B6864", "#CDD5D2", "#F2F4F3"
HP1, HP2, HP0, NORMAL = "#2D5EA6", "#BF522E", "#A3ADA9", "#A3ADA9"
GOOD, COST = "#2C7A4C", "#AE3838"
CLONE_COLORS = ["#2C6E72", "#A86E12", "#67498F", "#2C7A4C", "#AE3838", "#3F7FBF", "#8C6D46", "#5B6864"]


def read_tsv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load(run):
    run = Path(run)
    return dict(
        rows=read_tsv(run / "diplosim.tsv"),
        edges=read_tsv(run / "diplosim_treeedges.tsv"),
        props=read_tsv(run / "diplosim_cloneprops.tsv"),
        info={r["parameter"]: r["value"] for r in read_tsv(run / "diplosim_info.tsv")},
    )


def hp_vaf(r, hp):
    alt, ref = int(r[f"{hp}_ALT"]), int(r[f"{hp}_REF"])
    return alt / (alt + ref) if alt + ref else 0.0


def own_hp(r):
    return "HP1" if r["ALLELE"] == "A" else "HP2"


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=12, color=INK)
    ax.spines[["top", "right"]].set_visible(False)


def draw_tree(ax, run, color_of):
    children = defaultdict(list)
    for e in run["edges"]:
        children[int(e["Parent"])].append(int(e["Child"]))
    root = next(int(p["Clone"]) for p in run["props"] if p["Is_Normal"] == "Yes")
    prop = {int(p["Clone"]): float(p["Proportion"]) for p in run["props"]}
    pos, next_x = {}, [0]

    def visit(n, depth):
        if not children[n]:
            pos[n] = (next_x[0], -depth)
            next_x[0] += 1
            return
        for c in children[n]:
            visit(c, depth + 1)
        pos[n] = (sum(pos[c][0] for c in children[n]) / len(children[n]), -depth)

    visit(root, 0)
    for e in run["edges"]:
        (x0, y0), (x1, y1) = pos[int(e["Parent"])], pos[int(e["Child"])]
        ax.plot([x0, x1], [y0, y1], color=LINE, lw=2.5, zorder=1)
        ax.text((x0 + x1) / 2 + 0.1, (y0 + y1) / 2, f"{e['SNVs']} SNV", fontsize=9, color=INK, va="center")
    for n, (x, y) in pos.items():
        if n == root:
            ax.scatter(x, y, s=380, marker="s", color=NORMAL, zorder=2)
            ax.text(x, y, "N", ha="center", va="center", color="white", weight="bold", fontsize=10, zorder=3)
            continue
        ax.scatter(x, y, s=420, color=color_of(n), zorder=2)
        ax.text(x, y, str(n), ha="center", va="center", color="white", weight="bold", fontsize=10, zorder=3)
        ax.text(x - 0.2, y, f"{prop[n]:.1%}", ha="right", va="center", fontsize=8.5, color=MUTED)
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 0.8, max(xs) + 0.9)
    ax.set_ylim(min(ys) - 0.4, max(ys) + 0.4)
    ax.axis("off")
    ax.set_title("真值樹（三次執行相同）", loc="left", fontsize=12, color=INK)


def hp_scatter(ax, rows, title):
    for allele, col, name in (("A", HP1, "SNV 在 HP1"), ("B", HP2, "SNV 在 HP2")):
        sel = [r for r in rows if r["ALLELE"] == allele]
        ax.scatter([hp_vaf(r, "HP1") for r in sel], [hp_vaf(r, "HP2") for r in sel], s=12, color=col,
                   alpha=0.7, label=f"{name}：{len(sel)} 個")
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("HP1 內的 VAF")
    ax.set_ylabel("HP2 內的 VAF")
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    style(ax, title)


def band(fig, y, title, good, cost):
    fig.patches.append(plt.Rectangle((0.03, y - 0.005), 0.94, 0.05, transform=fig.transFigure, color=BAND, zorder=0))
    fig.text(0.04, y + 0.027, title, fontsize=15, weight="bold", color=INK, va="center")
    fig.text(0.04, y + 0.006, "改善：" + good, fontsize=11, color=GOOD, va="center")
    fig.text(0.52, y + 0.006, "代價：" + cost, fontsize=11, color=COST, va="center")


def main(run_b0, run_b05, run_def, out):
    b0, b05, dft = load(run_b0), load(run_b05), load(run_def)
    info = dft["info"]
    clones = sorted({int(r["CLUSTER"]) for r in dft["rows"]})
    color_of = lambda n: CLONE_COLORS[clones.index(n) % len(CLONE_COLORS)] if n in clones else MUTED

    fig = plt.figure(figsize=(16, 15.5), dpi=110)
    fig.patch.set_facecolor("white")
    fig.text(0.03, 0.975, "diplosim 兩個新參數，各自多了什麼", fontsize=20, weight="bold", color=INK)
    fig.text(0.03, 0.955, f"同一個 seed {info['random_seed']}：{info['n_clones']} 個 clone、{info['n_snv']} 個 SNV、"
             f"purity {float(info['purity']):.2f}、coverage {float(info['coverage']):.0f}。三次執行的樹、depth、alt "
             "完全相同，只改兩個新參數。", fontsize=11.5, color=MUTED)

    gs = fig.add_gridspec(3, 3, height_ratios=[0.75, 1, 1], hspace=0.75, wspace=0.28,
                          left=0.06, right=0.97, top=0.92, bottom=0.05)

    draw_tree(fig.add_subplot(gs[0, 0]), dft, color_of)
    ax = fig.add_subplot(gs[0, 1:])
    ax.axis("off")
    ax.set_title("三次執行", loc="left", fontsize=12, color=INK)
    table = [("執行", "prop_snv_on_b", "prop_tagged", "等於"),
             ("①", "0", "1.0", "CONIPHER（SNV 全在 A，read 全有 tag）"),
             ("②", "0.5", "1.0", "只打開 prop_snv_on_b"),
             ("③", "0.5", "0.8", "diplosim 預設（兩個都打開）")]
    for i, row in enumerate(table):
        y = 0.82 - i * 0.2
        for x, cell in zip((0.0, 0.1, 0.3, 0.48), row):
            ax.text(x, y, cell, fontsize=12 if i else 11, color=INK if i else MUTED,
                    weight="bold" if i and x == 0.0 else "normal", transform=ax.transAxes, va="center")
    ax.text(0.0, -0.04, "第 1 列比較 ① 和 ②：只看 prop_snv_on_b 的效果。第 2 列比較 ② 和 ③：只看 prop_tagged 的效果。",
            fontsize=10.5, color=MUTED, transform=ax.transAxes)

    ax_r1 = fig.add_subplot(gs[1, 0])
    band(fig, ax_r1.get_position().y1 + 0.03, "prop_snv_on_b（預設 0.5）：SNV 可以在 HP2",
         "兩條 haplotype 都帶突變，像真實的雙套體腫瘤", "沒有；depth、alt 不變，只改 SNV 在哪條 HP")
    hp_scatter(ax_r1, b0["rows"], "① prop_snv_on_b = 0：HP2 是空的")
    hp_scatter(fig.add_subplot(gs[1, 1]), b05["rows"], "② prop_snv_on_b = 0.5：兩條都有")
    ax = fig.add_subplot(gs[1, 2])
    rows = b05["rows"]
    for i, c in enumerate(clones):
        a = sum(1 for r in rows if int(r["CLUSTER"]) == c and r["ALLELE"] == "A")
        b = sum(1 for r in rows if int(r["CLUSTER"]) == c and r["ALLELE"] == "B")
        ax.barh(i, a, color=HP1)
        ax.barh(i, b, left=a, color=HP2)
        ax.text(a + b + 2, i, f"{a}／{b}", va="center", fontsize=9.5, color=INK)
    ax.set_yticks(range(len(clones)), [f"clone {c}" for c in clones])
    ax.invert_yaxis()
    ax.set_xlabel("SNV 數（藍＝HP1，橘＝HP2）")
    style(ax, "② 每個 clone 的 SNV 分散在兩條 HP")

    ax = fig.add_subplot(gs[2, 0])
    band(fig, ax.get_position().y1 + 0.03, "prop_tagged（預設 0.8）：一部分 read 沒有 HP tag（HP0）",
         "更接近真實 long read，可以測 tag 不足對建樹的影響", "每個 SNV 能用的 HP read 少約 20%，HP 內 VAF 變吵")
    for j, (run, name) in enumerate(((b05, "② 1.0"), (dft, "③ 0.8"))):
        tot = {hp: sum(int(r[f"{hp}_REF"]) + int(r[f"{hp}_ALT"]) for r in run["rows"]) for hp in ("HP1", "HP2", "HP0")}
        s, bottom = sum(tot.values()), 0
        for hp, col in (("HP1", HP1), ("HP2", HP2), ("HP0", HP0)):
            ax.bar(j, tot[hp] / s, bottom=bottom, color=col, width=0.6)
            if tot[hp]:
                ax.text(j, bottom + tot[hp] / s / 2, f"{hp} {tot[hp] / s:.0%}", ha="center", va="center",
                        color="white", fontsize=10, weight="bold")
            bottom += tot[hp] / s
    ax.set_xticks([0, 1], ["② prop_tagged 1.0", "③ prop_tagged 0.8"])
    ax.set_ylabel("占全部 read")
    style(ax, "read 分到哪條 HP")

    ax = fig.add_subplot(gs[2, 1])
    own = lambda run: [int(r[f"{own_hp(r)}_REF"]) + int(r[f"{own_hp(r)}_ALT"]) for r in run["rows"]]
    d1, d8 = own(b05), own(dft)
    bins = range(0, max(d1) + 20, 20)
    ax.hist(d1, bins=bins, color=MUTED, alpha=0.45, label=f"② 1.0：平均 {sum(d1) / len(d1):.0f}")
    ax.hist(d8, bins=bins, color=HP2, alpha=0.6, label=f"③ 0.8：平均 {sum(d8) / len(d8):.0f}")
    ax.set_xlabel("每個 SNV 在自己那條 HP 上的 read 數")
    ax.set_ylabel("SNV 數")
    ax.legend(frameon=False, fontsize=9.5)
    style(ax, "能用的 HP read 變少")

    ax = fig.add_subplot(gs[2, 2])
    v1 = [hp_vaf(r, own_hp(r)) for r in b05["rows"]]
    v8 = [hp_vaf(r, own_hp(r)) for r in dft["rows"]]
    rms = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v8)) / len(v1))
    ax.plot([0, 1], [0, 1], color=LINE, lw=1.2)
    ax.scatter(v1, v8, s=12, color=HP2, alpha=0.6)
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("② 1.0：自己那條 HP 內的 VAF")
    ax.set_ylabel("③ 0.8：自己那條 HP 內的 VAF")
    ax.text(0.03, 0.93, f"同一個 SNV 的差異（RMS）＝ {rms:.3f}", transform=ax.transAxes, fontsize=10.5, color=INK)
    style(ax, "同一個 SNV，HP 內 VAF 偏離對角線")

    fig.savefig(out, facecolor="white")
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:5])
