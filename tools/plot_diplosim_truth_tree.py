#!/usr/bin/env python3
"""Draw the truth tree of one diplosim run (2026-11-12).

Reads from a diplosim output directory:
  <name>_treeedges.tsv   Parent, Child, SNVs, Truncal (one row per edge)
  <name>_cloneprops.tsv  Clone, Proportion, Is_Normal (share of all cells in the sample)
  truth/snv_edges.tsv    VAR_POS, PARENT, CHILD, ALLELE (A = HP1, B = HP2)
  <name>_info.tsv        parameters, purity
Each edge shows how many SNVs arose on it and how many sit on HP1 / HP2. Each clone shows its share
of the sample and its CCF (its own cells plus all descendants, over tumour cells).

Usage: python3 tools/plot_diplosim_truth_tree.py DIPLOSIM_OUT_DIR OUT.png [NAME]
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
INK, MUTED, PAPER, PANEL, EDGE = "#1F2A37", "#7A8A82", "#F6F4EE", "#FFFFFF", "#D9D4C7"
HP1, HP2, NORMAL, TRUNK = "#3F7CAC", "#E08A3C", "#8A9A91", "#46574F"
CLONE_COLORS = ["#D23A2E", "#8456C4", "#D8A31E", "#2E8B57", "#C2185B", "#00838F", "#6D4C41", "#5C6BC0"]

d = Path(sys.argv[1])
name = sys.argv[3] if len(sys.argv) > 3 else "diplosim"
tsv = lambda p: list(csv.DictReader(open(p), delimiter="\t"))
edges = tsv(d / f"{name}_treeedges.tsv")
props = {r["Clone"]: (float(r["Proportion"]), r["Is_Normal"] == "Yes") for r in tsv(d / f"{name}_cloneprops.tsv")}
info = {r["parameter"]: r["value"] for r in tsv(d / f"{name}_info.tsv")}
hp = defaultdict(Counter)
for r in tsv(d / "truth" / "snv_edges.tsv"):
    hp[(r["PARENT"], r["CHILD"])][r["ALLELE"]] += 1

children = defaultdict(list)
parent = {}
for e in edges:
    children[e["Parent"]].append(e["Child"])
    parent[e["Child"]] = e["Parent"]
root = next(c for c, (_, normal) in props.items() if normal)
purity = 1 - props[root][0]


def subtree(n):
    return [n] + [m for c in children[n] for m in subtree(c)]


ccf = {n: sum(props[m][0] for m in subtree(n)) / purity for n in props if n != root}

# Tidy layout: leaves spread evenly, parents centred over children.
pos, depth = {}, {}
leaf_x = iter(range(100))


def place(n, dep):
    depth[n] = dep
    for c in sorted(children[n], key=lambda c: -len(subtree(c))):
        place(c, dep + 1)
    xs = [pos[c][0] for c in children[n]]
    pos[n] = (sum(xs) / len(xs) if xs else next(leaf_x), dep)


place(root, 0)
n_leaves = max(x for x, _ in pos.values()) + 1
max_dep = max(depth.values())

fig = plt.figure(figsize=(24, 13.5), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 240)
ax.set_ylim(0, 135)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(PAPER)


def text(x, y, s, size=15, color=INK, weight="normal", ha="center", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, zorder=8)


X0, X1, Y0, Y1 = 14, 160, 100, 18
to_xy = lambda n: (X0 + (X1 - X0) * (pos[n][0] + 0.5) / n_leaves, Y0 - (Y0 - Y1) * pos[n][1] / max_dep)

text(6, 125, "diplosim 模擬出的真值演化樹", 30, weight="bold", ha="left")
text(6, 118, f"{info['n_clones']} 個 clone、{info['n_snv']} 個 SNV、seed {info['random_seed']}；"
             f"只有 SNV（拷貝數事件預設 0），每個 SNV 以 50% 落在 HP2", 16, MUTED, ha="left")
ax.add_patch(FancyBboxPatch((6, 6), 166, 104, boxstyle="round,pad=0,rounding_size=2", fc=PANEL, ec=EDGE, lw=1.6))

colors, k = {}, 0
for n in subtree(root):
    if n == root:
        colors[n] = NORMAL
    elif parent[n] == root:
        colors[n] = TRUNK
    else:
        colors[n] = CLONE_COLORS[k % len(CLONE_COLORS)]
        k += 1

for e in edges:
    a, b = e["Parent"], e["Child"]
    (xa, ya), (xb, yb) = to_xy(a), to_xy(b)
    ax.plot([xa, xb, xb], [ya, ya, yb], color=colors[b], lw=4, solid_capstyle="round", zorder=1)
    c = hp[(a, b)]
    n_snv, n1, n2 = int(e["SNVs"]), c["A"], c["B"]
    assert n1 + n2 == n_snv, (a, b, n1, n2, n_snv)
    ym = (ya + yb) / 2 + (2 if e["Truncal"] == "Yes" else 0)
    w = 21
    ax.add_patch(FancyBboxPatch((xb + 2, ym - 4.6), w, 9.2, boxstyle="round,pad=0,rounding_size=1.2", fc=PANEL,
                                ec=colors[b], lw=2, zorder=5))
    label = "truncal　" if e["Truncal"] == "Yes" else ""
    text(xb + 2 + w / 2, ym + 1.9, f"{label}+{n_snv} SNV", 13, colors[b], "bold")
    share = n1 / n_snv
    ax.add_patch(FancyBboxPatch((xb + 4, ym - 3.3), (w - 4) * share, 2.4, boxstyle="square,pad=0", fc=HP1, ec="none", zorder=6))
    ax.add_patch(FancyBboxPatch((xb + 4 + (w - 4) * share, ym - 3.3), (w - 4) * (1 - share), 2.4, boxstyle="square,pad=0",
                                fc=HP2, ec="none", zorder=6))
    text(xb + 2 + w / 2, ym - 2.1, f"{n1} : {n2}", 10, "#FFFFFF", "bold")

for n in props:
    x, y = to_xy(n)
    ax.add_patch(Circle((x, y), 4.2, fc=colors[n], ec="#FFFFFF", lw=2.5, zorder=7))
    if n == root:
        text(x, y, "N", 15, "#FFFFFF", "bold")
        text(x + 6, y + 0.8, f"normal 細胞 {props[n][0]:.0%}", 14, NORMAL, "bold", ha="left")
        text(x + 6, y - 3.4, f"purity {purity:.2f}", 12, MUTED, ha="left")
    else:
        text(x, y, n, 15, "#FFFFFF", "bold")
        text(x + 5.5, y + 1.6, f"自己 {props[n][0]:.0%}", 12, INK, ha="left")
        text(x + 5.5, y - 2.2, f"CCF {ccf[n]:.2f}", 12, INK, ha="left")

# ---------------- right: how to read ----------------
ax.add_patch(FancyBboxPatch((178, 6), 56, 104, boxstyle="round,pad=0,rounding_size=2", fc=PANEL, ec=EDGE, lw=1.6))
text(182, 102, "怎麼讀", 19, weight="bold", ha="left")
rows = [
    ("圓圈", "一個 clone（數字是 clone 編號）；N 是 normal"),
    ("自己 %", "這個 clone 的細胞占整個樣本的比例"),
    ("CCF", "自己＋所有後代，占腫瘤細胞的比例"),
    ("+n SNV", "在這條邊上新產生的 SNV，子孫都會帶"),
    ("藍：橘", "這些 SNV 在 HP1 和 HP2 各幾個"),
]
for i, (k_, v) in enumerate(rows):
    y = 92 - i * 10
    text(182, y, k_, 15, INK, "bold", ha="left")
    text(182, y - 4.2, v, 12, MUTED, ha="left")
ax.add_patch(FancyBboxPatch((182, 37), 4, 2.4, boxstyle="square,pad=0", fc=HP1, ec="none"))
text(188, 38.2, "HP1", 13, HP1, "bold", ha="left")
ax.add_patch(FancyBboxPatch((200, 37), 4, 2.4, boxstyle="square,pad=0", fc=HP2, ec="none"))
text(206, 38.2, "HP2", 13, HP2, "bold", ha="left")
tot = Counter()
for c in hp.values():
    tot.update(c)
text(182, 28, f"全部 SNV：HP1 {tot['A']}、HP2 {tot['B']}", 14, INK, "bold", ha="left")
text(182, 22, "這些是真值：重建工具只拿到", 12, MUTED, ha="left")
text(182, 17.5, "每個 SNV 的 read 數（含 HP1／HP2），", 12, MUTED, ha="left")
text(182, 13, "要自己推回這棵樹", 12, MUTED, ha="left")

fig.savefig(sys.argv[2], dpi=150, facecolor=PAPER)
print("purity", round(purity, 3), "HP1/HP2", dict(tot), "CCF", {k: round(v, 3) for k, v in ccf.items()})
