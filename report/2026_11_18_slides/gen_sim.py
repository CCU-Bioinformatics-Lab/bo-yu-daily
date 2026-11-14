"""Simulation pages: p5 sim-method, p6 sim-result, p7 sim-why (2026-11-18 deck, BRIEF rows 5-7).

Numbers come from lab_report/2026-11-12_diplosim_haploclone_hp_vs_base/ (BRIEF R4): results.tsv for the
per-tree dots (mean of the two haploclone seeds, then 加 HP - 不加 HP), summary.txt for means and CIs,
truth_trees.txt for tree 7. The tree-7 split (0.42 group into the 0.49 and 0.34 groups) is the first trial
run, lab_report/2026-11-12_diplosim_haploclone_first_run/ section 3. HG008 numbers: R5 README (63x ONT,
116x PacBio, 43.4% 1+1) and GIAB note (cell line, purity near 1, not measured).
"""
import csv
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slidekit import S, page, write_page, tag
from lib import width
from gen_bg import dice, fraction  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
R4 = ROOT / "lab_report/2026-11-12_diplosim_haploclone_hp_vs_base"


def tree_diffs():
    rows = list(csv.DictReader(open(R4 / "results.tsv"), delimiter="\t"))
    acc = {}
    for r in rows:
        acc.setdefault((int(r["sim_seed"]), r["mode"]), []).append(float(r["pair_acc"]))
    return [st.mean(acc[(t, "a1")]) - st.mean(acc[(t, "base")]) for t in range(1, 11)]


# ---- small pictograms ---------------------------------------------------------------

def node(s, x, y, col, r=12):
    s.circle(x, y, r, col, "cellline", 1.5)


def edge(s, a, b, sw=3):
    s.line(a[0], a[1], b[0], b[1], "ink2", sw)


def doc(s, x, y, w, h):
    """A file: a page with a folded corner."""
    f = 18
    s.path(f"M{x} {y} L{x + w - f} {y} L{x + w} {y + f} L{x + w} {y + h} L{x} {y + h} Z", "line2", 2, "on")
    s.path(f"M{x + w - f} {y} L{x + w - f} {y + f} L{x + w} {y + f}", "line2", 2)


def tree7(s, cx, top, dx=36, dy=42, r=10):
    """Tree 7 shape (root -> 0.42 -> 0.34; root -> 0.49 -> 0.08), small, no labels."""
    root, a, b = (cx, top), (cx - dx, top + dy), (cx + dx, top + dy)
    a2, b2 = (cx - dx, top + 2 * dy), (cx + dx, top + 2 * dy)
    for p, q in [(root, a), (root, b), (a, a2), (b, b2)]:
        edge(s, p, q, 2.5)
    node(s, *root, "ink", r)
    for p, c in [(a, "c1"), (b, "c2"), (a2, "c3"), (b2, "vessel")]:
        node(s, *p, c, r)


def tree_small(s, cx, top, cols, dx=26, dy=34, r=8):
    """Reconstructed-tree icon: root -> two children -> one grandchild on the left."""
    root, a, b, a2 = (cx, top), (cx - dx, top + dy), (cx + dx, top + dy), (cx - dx, top + 2 * dy)
    for p, q in [(root, a), (root, b), (a, a2)]:
        edge(s, p, q, 2)
    node(s, *root, "ink", r)
    for p, c in zip([a, b, a2], cols):
        node(s, *p, c, r)


def check(s, x, y, ok=True):
    s.text(x, y, "✓" if ok else "✗", "b", "start", "c4" if ok else "stdis")


# ---- p5 sim-method ----------------------------------------------------------------------

def p5():
    s = S("p5", 1200, 560)
    # the question (user 11-14: say what the simulator makes, then what we ask haploclone)
    s.rect(0, 0, 1200, 50, "hl", None, r=10)
    s.text(600, 33, "問題：全部 1+1、只有 SNV 時，加上 HP1／HP2，haploclone 能不能重建出一模一樣的樹？", "b", "middle")

    # frame A: diplosim makes data with a known answer (5 steps); frame B: haploclone (2 steps)
    fy, fh = 64, 236
    s.rect(0, fy, 772, fh, "panel", None, r=10)
    s.text(14, fy + 28, "diplosim：產生已知答案", "h")
    s.rect(788, fy, 412, fh, "panel", None, r=10)
    s.text(802, fy + 28, "haploclone：重建，再和真值比", "h")
    cw, gap, cy = 142, 10, fy + 44
    xs = [10 + i * (cw + gap) for i in range(5)]
    for i, x in enumerate(xs):
        s.rect(x, cy, cw, 182, "on", None, r=8)
        s.circle(x + 16, cy + 16, 11, "ink2")
        s.text(x + 16, cy + 22, str(i + 1), "s", "middle", "on")
    labels = [("隨機產生樹", "5 個 clone"), ("分支放 SNV", "共 1,000 個"), ("隨機選 HP", "HP1、HP2 各半"),
              ("全部 1+1", "兩條各一份"), ("產生計數", "ref／alt 分 HP")]
    for x, (t1, t2) in zip(xs, labels):
        s.text(x + cw / 2, cy + 146, t1, "b", "middle")
        s.text(x + cw / 2, cy + 172, t2, "s", "middle", "ink2")
    # 1 a random tree (tree 7 shape)
    tree7(s, xs[0] + 71, cy + 30, dx=34, dy=40, r=10)
    # 2 new SNVs on each branch
    tree7(s, xs[1] + 71, cy + 30, dx=34, dy=40, r=10)
    for sx, sy in [(-17, 50), (17, 50), (-34, 90), (34, 90)]:
        s.star(xs[1] + 71 + sx - 8, cy + sy - 2, 7)
    # 3 each SNV goes to HP1 or HP2, 50 % each, independently
    x = xs[2]
    dice(s, x + 72, cy + 4, 24)
    fraction(s, x + 118, cy + 20, "1", "2")
    s.text(x + 10, cy + 74, "HP1", "s", "start", "hp1")
    s.text(x + 10, cy + 112, "HP2", "s", "start", "hp2")
    s.bar(x + 50, cy + 62, 82, "hp1", h=12)
    s.bar(x + 50, cy + 100, 82, "hp2", h=12)
    for sx in (66, 112):
        s.star(x + sx, cy + 68, 7)
    s.star(x + 88, cy + 106, 7)
    # 4 every position 1+1
    x = xs[3]
    s.text(x + 10, cy + 70, "HP1", "s", "start", "hp1")
    s.text(x + 10, cy + 108, "HP2", "s", "start", "hp2")
    s.bar(x + 50, cy + 58, 70, "hp1", h=14)
    s.bar(x + 50, cy + 96, 70, "hp2", h=14)
    s.text(x + 130, cy + 70, "1", "b", "middle")
    s.text(x + 130, cy + 108, "1", "b", "middle")
    # 5 read counts per SNV, split by HP (alt only on the SNV's HP)
    x = xs[4]
    for k, (hp, alt) in enumerate([("hp1", 30), ("hp2", 0)]):
        y = cy + 48 + k * 34
        s.rect(x + 10, y - 9, 16, 18, hp, None, r=3)
        s.rect(x + 32, y - 6, 66, 12, "panel3", None, r=3)
        if alt:
            s.rect(x + 98, y - 6, alt, 12, "mut", None, r=3)
    s.text(x + 32, cy + 112, "ref", "s", "start", "ink2")
    s.text(x + 98, cy + 112, "alt", "s", "start", "mut")
    for i in range(4):
        s.arrow(xs[i] + cw + 1, cy + 80, xs[i + 1] - 1, cy + 80, c="ink2", sw=2, head=6)
    s.arrow(774, cy + 80, 796, cy + 80, c="ink2", sw=3, head=9)

    # 6 two inputs to the same program; 7 compare with the truth
    x6, x7 = 798, 1000
    for x, w, n, t1, t2 in [(x6, 192, 6, "兩種輸入", "同一個程式"), (x7, 192, 7, "和真值比", "樹拓樸、屬哪一群")]:
        s.rect(x, cy, w, 182, "on", None, r=8)
        s.circle(x + 16, cy + 16, 11, "ink2")
        s.text(x + 16, cy + 22, str(n), "s", "middle", "on")
        s.text(x + w / 2, cy + 146, t1, "b", "middle")
        s.text(x + w / 2, cy + 172, t2, "s", "middle", "ink2")
    for k, (lab, hp) in enumerate([("不加 HP", False), ("加 HP", True)]):
        y = cy + 50 + k * 54
        s.rect(x6 + 14, y - 18, 100, 36, "on", "line2", r=8, sw=2)
        if hp:
            s.rect(x6 + 20, y - 11, 6, 22, "hp1", None, r=2)
            s.rect(x6 + 28, y - 11, 6, 22, "hp2", None, r=2)
        s.text(x6 + 70 if hp else x6 + 64, y + 6, lab, "s", "middle")
        s.arrow(x6 + 118, y, x6 + 136, y, c="ink2", sw=2)
        tree_small(s, x6 + 166, y - 22, ["c1", "c2", "c3"], dx=14, dy=16, r=5)
    s.arrow(x6 + 192 + 1, cy + 80, x7 - 1, cy + 80, c="ink2", sw=2, head=6)
    tree_small(s, x7 + 56, cy + 34, ["c1", "c2", "c3"], dx=20, dy=28, r=8)
    s.text(x7 + 56, cy + 124, "真值", "s", "middle")
    s.text(x7 + 96, cy + 72, "↔", "h", "middle")
    tree_small(s, x7 + 140, cy + 34, ["c1", "c2", "c3"], dx=20, dy=28, r=8)
    s.text(x7 + 140, cy + 124, "重建", "s", "middle")

    # lower row: the two scores
    y0 = 316
    s.rect(0, y0, 760, 243, "panel", None, r=10)
    s.text(16, y0 + 32, "樹拓樸形狀是否一樣：看任兩個 SNV 的關係", "h")
    tag(s, 680, y0 + 32, "示意", "demo")
    cases = [("同群", "A", "A"), ("祖先", "A", "B"), ("後代", "B", "A"), ("不同支", "B", "C")]
    for i, (lab, n1, n2) in enumerate(cases):
        cx = 96 + i * 186
        P = {"R": (cx - 6, y0 + 66), "A": (cx - 34, y0 + 108), "C": (cx + 22, y0 + 108), "B": (cx - 34, y0 + 150)}
        for p, q in [("R", "A"), ("R", "C"), ("A", "B")]:
            edge(s, P[p], P[q], 2.5)
        node(s, *P["R"], "ink", 9)
        for k, c in [("A", "c1"), ("C", "c2"), ("B", "c3")]:
            node(s, *P[k], c, 10)
        for num, nd, dy in [("1", n1, -9 if n1 == n2 else 0), ("2", n2, 11 if n1 == n2 else 0)]:
            nx, ny = P[nd]
            s.star(nx + 20, ny + dy, 7)
            s.text(nx + 30, ny + dy + 6, num, "s")
        s.text(cx, y0 + 190, lab, "b", "middle")
    s.text(16, y0 + 228, "得分＝關係和真值相同的 SNV 對比例", "s")
    s.star(568, y0 + 222, 7)
    s.text(578, y0 + 228, "1", "s")
    s.text(594, y0 + 228, "SNV1", "s")
    s.star(664, y0 + 222, 7)
    s.text(674, y0 + 228, "2", "s")
    s.text(690, y0 + 228, "SNV2", "s")

    ax = 776
    s.rect(ax, y0, 1200 - ax, 243, "panel", None, r=10)
    s.text(ax + 16, y0 + 32, "SNV 屬於哪一個 clone 群", "h")
    rows = [("真值", [(ax + 150, ["c1"]), (ax + 222, ["c2"]), (ax + 294, ["c3"])]),
            ("重建", [(ax + 150, ["c1"]), (ax + 258, ["c2", "c3"])])]
    for k, (lab, groups) in enumerate(rows):
        y = y0 + 78 + k * 64
        s.text(ax + 16, y + 7, lab, "b")
        for gx, cols in groups:
            rx = 26 * len(cols) + (4 if len(cols) > 1 else 0)
            s.raw(f'<ellipse cx="{gx}" cy="{y}" rx="{rx}" ry="22" style="fill:none;stroke:var(--ink2);stroke-width:2"/>')
            dots = [c for c in cols for _ in range(2)]
            for j, c in enumerate(dots):
                s.circle(gx + (j - (len(dots) - 1) / 2) * 22, y, 8, c, "cellline", 1.2)
    s.text(ax + 212, y0 + 200, "不看樹形", "b", "middle")
    tag(s, ax + 16, y0 + 228, "示意", "demo")

    notes = ('這頁要看的是模擬怎麼產生答案、要問什麼。最上面是問題：全部 1+1、只有 SNV 時，加上 HP1、HP2，haploclone 能不能重建出一模一樣的樹。左邊是 diplosim 五步：隨機產生 5 個 clone 的樹；每個分支放新的 SNV，共 1,000 個；每個 SNV 隨機一半放 HP1、一半放 HP2；每個位置 HP1、HP2 各一份；最後產生每個 SNV 的 ref、alt 計數，alt 只在 SNV 那條 HP 上。右邊同一個程式跑不加 HP 和加 HP，再和真值比：下面左邊是樹拓樸是否一樣，右邊是每個 SNV 屬於哪一群。')
    write_page("sim-method", page("sim-method", "模擬已知樹：全部 1+1、SNV 各半放 HP，看加 HP 能否重建得一樣", s, notes=notes))


# ---- p6 sim-result ----------------------------------------------------------------------

# Tree 7, haploclone seed 1 (= lab_report/2026-11-12_diplosim_haploclone_first_run/map/, same rows as the batch
# results.tsv sim_seed 7 hc_seed 1). Truth clone -> colour as in tree7(): 6 root, 7 (0.42) c1, 9 (0.49) c2,
# 8 (0.34) c3, 5 (0.08) vessel. Each reconstructed clone lists (truth clone, SNV count) from map_*.tsv x truth.tsv.
T7COL = {"6": "ink", "7": "c1", "9": "c2", "8": "c3", "5": "vessel"}
T7_TRUTH = {"6": (None, 1.00, 500), "7": ("6", 0.42, 50), "8": ("7", 0.34, 190), "9": ("6", 0.49, 91), "5": ("9", 0.08, 169)}
T7_REC = {
    "base": {"0": (None, 1.00, [("6", 500)]), "1": ("0", 0.48, [("9", 84), ("7", 30), ("8", 7)]),
             "2": ("1", 0.08, [("5", 169)]), "3": ("0", 0.34, [("8", 183), ("7", 20), ("9", 7)])},
    "a1": {"0": (None, 1.00, [("6", 500)]), "1": ("0", 0.48, [("9", 89), ("7", 27), ("8", 12)]),
           "2": ("1", 0.08, [("5", 169)]), "3": ("1", 0.34, [("8", 178), ("7", 23), ("9", 2)])},
}
T7_SCORE = {"base": (0.952, 0.951), "a1": (0.927, 0.949)}   # pair_acc, ARI (results.tsv, tree 7 seed 1)


def p6():
    s = S("p6", 1200, 520)
    # ---- left: one case, tree 7 -------------------------------------------------------------
    s.rect(0, 0, 784, 520, "panel", None, r=10)
    s.text(16, 32, "例：第 7 棵樹", "h")
    tag(s, 680, 32, "實際結果", "real")
    R, Y = 22, (100, 216, 332)

    def draw(cx, nodes, pos, comp=None, wrong=()):
        for k, (par, ccf, _) in nodes.items():
            if par is not None:
                (x1, y1), (x2, y2) = pos[par], pos[k]
                bad = (par, k) in wrong
                y0 = y1 + R + (44 if comp else 32)          # start below the parent's labels
                s.line(x1, y0, x2, y2 - R, "mut" if bad else "ink2", 3, dash=bad)
                if bad:
                    mx, my = (x1 + x2) / 2, (y0 + y2 - R) / 2
                    s.xmark(mx - 14, my, 8, "mut", 3)
                    s.text(mx - 28, my + 7, "接錯", "s", "end", "mut")
        for k, (par, ccf, n) in nodes.items():
            x, y = pos[k]
            if comp:
                parts = n
                col = T7COL[max(parts, key=lambda p: p[1])[0]]
                tot = sum(c for _, c in parts)
            else:
                col, tot = T7COL[k], n
            s.circle(x, y, R, col, "cellline", 1.5)
            s.text(x, y + 6, "1" if ccf == 1 else f"{ccf:.2f}".lstrip("0"), "s", "middle", "on")
            if comp:
                bx, bw = x - 36, 72
                cur = bx
                for tc, c in parts:
                    w = bw * c / tot
                    s.rect(cur, y + R + 6, w, 11, T7COL[tc], None, r=0)
                    cur += w
                s.rect(bx, y + R + 6, bw, 11, None, "cellline", r=2, sw=1)
                s.text(x, y + R + 38, f"{tot} 個", "s", "middle", "ink2")
            else:
                s.text(x, y + R + 24, f"{tot} 個", "s", "middle", "ink2")

    cols = [(130, "真值"), (392, "不加 HP"), (654, "加 HP")]
    for cx, lab in cols:
        s.text(cx, 72, lab, "b", "middle", "hp1" if lab == "加 HP" else None)
    cx = cols[0][0]
    draw(cx, T7_TRUTH, {"6": (cx, Y[0]), "7": (cx - 62, Y[1]), "9": (cx + 62, Y[1]), "8": (cx - 62, Y[2]), "5": (cx + 62, Y[2])})
    cx = cols[1][0]
    draw(cx, T7_REC["base"], {"0": (cx, Y[0]), "3": (cx - 62, Y[1]), "1": (cx + 62, Y[1]), "2": (cx + 62, Y[2])}, comp=True)
    cx = cols[2][0]
    draw(cx, T7_REC["a1"], {"0": (cx, Y[0]), "1": (cx, Y[1]), "3": (cx - 62, Y[2]), "2": (cx + 62, Y[2])}, comp=True,
         wrong={("1", "3")})
    # what went wrong in both
    s.line(262, 52, 262, 484, "line2", 1.5, dash=True)
    s.text(16, 446, "綠色 .42 那群（50 個）", "s", "start", "c1")
    s.text(16, 472, "兩種重建都拆進兩群", "s", "start", "ink2")
    for k, (cx, _) in enumerate(cols[1:]):
        mode = ("base", "a1")[k]
        pa, ari = T7_SCORE[mode]
        s.text(cx - 96, 446, "樹拓樸", "s", "start", "ink2")
        s.text(cx + 96, 446, f"{pa:.3f}", "b", "end")
        s.text(cx - 96, 474, "屬哪一群", "s", "start", "ink2")
        s.text(cx + 96, 474, f"{ari:.3f}", "b", "end")
    s.text(16, 508, "圓的顏色＝主要來自哪個真值 clone；色條＝這群的 SNV 從哪些真值 clone 來", "s", "start", "ink2")

    # ---- right: overall scores over 10 trees --------------------------------------------------
    rx = 800
    s.rect(rx, 0, 400, 520, "on", "line2", r=10, sw=2)
    s.text(rx + 16, 32, "10 棵樹總體：分得好不好", "h")
    bx, bw = rx + 120, 200

    def block(y, title, base, a1, line1, line2):
        s.text(rx + 16, y, title, "b")
        for k, (lab, v, c) in enumerate([("不加 HP", base, "ink2"), ("加 HP", a1, "hp1")]):
            yy = y + 30 + k * 32
            s.text(rx + 16, yy + 6, lab, "s", "start", c)
            s.rect(bx, yy - 9, bw, 18, "panel", None, r=3)
            s.rect(bx, yy - 9, bw * v, 18, c, None, r=3)
            s.text(bx + bw + 8, yy + 6, f"{v:.2f}", "s", "start")
        s.text(rx + 16, y + 104, line1, "s", "start", "ink2")
        s.text(rx + 16, y + 128, line2, "s", "start", "ink2")
    block(72, "樹拓樸一樣的比例", 0.917, 0.906, "差 −0.011，CI 含 0", "加 HP 較高 5 棵、較低 5 棵")
    block(244, "SNV 屬於哪一群", 0.917, 0.940, "差 +0.023，CI 含 0", "加 HP 較高 8 棵")
    s.text(rx + 16, 404, "CCF 誤差：0.008 → 0.006（只準 0.002）", "s", "start", "ink2")
    s.rect(rx + 14, 420, 372, 86, "hl", None, r=10)
    s.text(rx + 200, 454, "兩種都分得好（約 0.9）", "b", "middle")
    s.text(rx + 200, 486, "加 HP 沒有明顯更好", "b", "middle")

    notes = ('這頁要看的是：加 HP 沒有讓樹變好。左邊用第 7 棵樹當例子：最左是真值，中間不加 HP，右邊加 HP。'
             '圓的顏色是主要來自哪個真值 clone，下面色條是這群的 SNV 從哪裡來。'
             '綠色 0.42 那群在兩種重建都被拆進兩群；加 HP 還把黃色那群接錯到紫色下面。'
             '兩種的樹拓樸分數是 0.952 和 0.927，屬哪一群都是 0.95。'
             '右邊是 10 棵樹的平均：兩種都約 0.9，分得好；樹拓樸差 −0.011，屬哪一群差 +0.023，CI 都含 0，所以加 HP 沒有明顯更好；CCF 只準 0.002。')
    write_page("sim-result", page("sim-result", "全部 1+1 時，10 棵樹沒看到 HP 改善樹形，CCF 只準 0.002", s, notes=notes))


# ---- p7 sim-why -------------------------------------------------------------------------

def p7():
    s = S("p7", 1200, 505)
    # a: truth tree 7
    s.rect(0, 0, 370, 300, "panel", None, r=10)
    s.text(14, 32, "第 7 棵真值樹", "h")
    tag(s, 180, 32, "實際結果", "real")
    R, A, B, A2, B2 = (185, 76), (100, 148), (270, 148), (100, 222), (270, 222)
    for p, q in [(R, A), (R, B), (A, A2), (B, B2)]:
        edge(s, p, q)
    s.raw('<ellipse cx="185" cy="148" rx="168" ry="32" style="fill:none;stroke:var(--stdis);stroke-width:2.5" stroke-dasharray="7 5"/>')
    for p, c, v in [(R, "ink", "1.00"), (A, "c1", "0.42"), (B, "c2", "0.49"), (A2, "c3", "0.34"), (B2, "vessel", "0.08")]:
        node(s, *p, c, 14)
        s.text(p[0] + 22, p[1] + 7, v, "b", "start", c)
    s.text(185, 207, "CCF 接近", "s", "middle", "stdis")
    s.text(185, 284, "數字＝CCF", "s", "middle")

    # b: rebuild result
    s.rect(385, 0, 395, 300, "panel", None, r=10)
    s.text(399, 32, "重建：5 群只找回 4 群", "h")
    tag(s, 640, 32, "實際結果", "real")
    node(s, 470, 150, "c1", 32)
    for k in range(3):
        s.star(452 + k * 18, 150, 8)
    s.text(470, 205, "0.42 那群", "b", "middle", "c1")
    for y, c, lab in [(92, "c2", "0.49 群"), (208, "c3", "0.34 群")]:
        s.arrow(500, 150 + (y - 150) * .25, 622, y, c="ink2", sw=2.5)
        node(s, 645, y, c, 18)
        s.text(672, y + 7, lab, "b", "start", c)
    s.text(562, 155, "拆開併入", "s", "middle")
    s.text(582, 256, "拆開方式：第一次試跑所見", "s", "middle", "ink2")
    s.text(582, 284, "加 HP、不加 HP 都是 4 群", "s", "middle")

    # c: two arrangements
    s.rect(795, 0, 405, 300, "panel", None, r=10)
    s.text(809, 32, "兩種排法都說得通", "h")
    w = tag(s, 1000, 32, "示意", "demo")
    tag(s, 1000 + w + 8, 32, "推論", "infer")
    r0, c1, c2 = (890, 72), (850, 136), (930, 136)
    edge(s, r0, c1)
    edge(s, r0, c2)
    node(s, *r0, "ink", 11)
    node(s, *c1, "c2", 12)
    node(s, *c2, "c1", 12)
    s.text(850, 170, "0.49", "s", "middle", "c2")
    s.text(930, 170, "0.42", "s", "middle", "c1")
    s.text(890, 204, "兄弟", "b", "middle")
    s.text(890, 230, "0.49+0.42 ≤ 1 ✓", "s", "middle")
    l0, l1, l2 = (1095, 62), (1095, 108), (1095, 154)
    edge(s, l0, l1)
    edge(s, l1, l2)
    node(s, *l0, "ink", 11)
    node(s, *l1, "c2", 12)
    node(s, *l2, "c1", 12)
    s.text(1117, 114, "0.49", "s", "start", "c2")
    s.text(1117, 160, "0.42", "s", "start", "c1")
    s.text(1095, 204, "一條線", "b", "middle")
    s.text(1095, 230, "0.42 ≤ 0.49 ✓", "s", "middle")
    s.bar(815, 262, 34, "hp1", h=10)
    s.bar(815, 278, 34, "hp2", h=10)
    s.text(860, 277, "全部 1+1：HP 分不出這兩種", "s")

    # bottom left: can / cannot prove
    s.rect(0, 318, 520, 187, "panel", None, r=10)
    check(s, 16, 352)
    s.text(42, 352, "能證明", "b")
    s.text(42, 380, "這組設定下，加 HP 沒改善樹拓樸，CCF 略準", "s")
    check(s, 16, 422, False)
    s.text(42, 422, "不能證明", "b")
    s.text(42, 450, "其他設定也一樣（深度、clone 數、拷貝數變化）", "s")
    s.text(42, 478, "HP 對樹重建一定沒用", "s")

    # bottom right: simulation vs HG008
    s.rect(535, 318, 665, 187, "panel", None, r=10)
    s.text(770, 348, "模擬設定", "b", "middle")
    s.text(1030, 348, "HG008", "b", "middle")
    rows = [("coverage", (100, None, "400×"), (16, 29, "63×／116×")),
            ("purity", (90, 70, "0.7–0.9"), (100, None, "推測約 1，未實測")),
            ("1+1 區域", (100, None, "全部"), (43, None, "43%（全基因組）"))]
    for k, (lab, sim, hg) in enumerate(rows):
        y = 392 + k * 42
        s.text(552, y + 6, lab, "b")
        for x0, (full, part, txt) in [(670, sim), (930, hg)]:
            s.rect(x0, y - 8, 100, 16, "panel2", None, r=3)
            if lab == "purity" and part:
                s.rect(x0 + part, y - 8, full - part, 16, "ink2", None, r=3)
            else:
                s.rect(x0, y - 8, full, 16, "ink2", None, r=3)
                if part:
                    s.rect(x0 + full, y - 8, part - full, 16, "line2", None, r=3)
            s.text(x0 + 108, y + 6, txt, "s")

    notes = '這頁講為什麼 HP 幫不上。左上是第 7 棵真值樹，0.42 和 0.49 兩群 CCF 很接近。中間是實際結果：加不加 HP 都只找回 4 群；第一次試跑時看得到，0.42 那群被拆開，併入 0.49 和 0.34 兩群。右上是我們的推論：兩群排成兄弟或一條線，CCF 都說得通；全部 1+1 時，HP 分不出這兩種。左下：這組設定下能說沒改善，不能推到其他設定。右下和 HG008 比：深度、1+1 比例都不同；purity 是腫瘤細胞占的比例，HG008 是細胞株，推測接近 1，但沒有實測。所以結果不能直接搬過去，接下來看真實資料 HG008。'
    write_page("sim-why", page("sim-why", "兩個原因讓 HP 幫不上：CCF 接近的群被併掉；兄弟或一條線分不出來", s, notes=notes))


if __name__ == "__main__":
    p5()
    p6()
    p7()
