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
    s = S("p5", 1200, 505)
    boxes = [(0, 205, "1 已知樹（模擬）"), (245, 205, "2 計數"), (490, 230, "3 重建"),
             (760, 195, "4 和真值比"), (995, 205, "5 得分")]
    for i, (x, w, t) in enumerate(boxes):
        s.rect(x, 0, w, 245, "panel", None, r=10)
        s.text(x + w / 2, 30, t, "h", "middle")
        if i:
            px = boxes[i - 1][0] + boxes[i - 1][1]
            s.arrow(px + 4, 115, x - 4, 115, c="ink2", sw=3)
    # 1 known tree
    tree7(s, 102, 62)
    for sx, sy in [(78, 76), (126, 76), (58, 125), (146, 125)]:
        s.star(sx, sy, 7)
    s.text(102, 192, "5 clone、1,000 SNV", "s", "middle")
    s.text(102, 218, "全部 1+1（各一份）", "s", "middle")
    # 2 counts
    doc(s, 290, 46, 112, 124)
    for k, hp in enumerate(["hp1", "hp2", "hp1", "hp2"]):
        y = 72 + k * 26
        s.rect(300, y - 7, 14, 14, hp, None, r=3)
        s.rect(322, y - 5, 44, 10, "panel3", None, r=3)
        s.rect(366, y - 5, 18 + 6 * (k % 2), 10, "mut", None, r=3)
    s.text(347, 192, "ref／alt 計數＋HP", "s", "middle")
    s.text(347, 216, "直接產生，沒有 read", "s", "middle")
    s.text(347, 240, "HP 完全已知", "s", "middle")
    # 3 rebuild: same program, two inputs
    for k, (lab, hp) in enumerate([("加 HP", True), ("不加 HP", False)]):
        y = 82 + k * 78
        s.rect(500, y - 22, 104, 40, "on", "line2", r=8, sw=2)
        if hp:
            s.rect(506, y - 14, 7, 24, "hp1", None, r=2)
            s.rect(515, y - 14, 7, 24, "hp2", None, r=2)
        s.text(560 if hp else 552, y + 6, lab, "b", "middle")
        s.arrow(608, y - 2, 632, y - 2, c="ink2", sw=2.5)
        tree_small(s, 672, y - 30, ["c1", "c2", "c3"], dx=22, dy=24, r=7)
    s.text(605, 216, "同一個程式，兩種輸入", "s", "middle")
    s.text(605, 240, "每棵樹各跑 2 次", "s", "middle")
    # 4 compare with truth
    tree_small(s, 812, 62, ["c1", "c2", "c3"], dx=22, dy=32, r=8)
    s.text(812, 158, "真值", "s", "middle")
    s.text(857, 102, "↔", "h", "middle")
    tree_small(s, 902, 62, ["c1", "c2", "c3"], dx=22, dy=32, r=8)
    s.text(902, 158, "重建", "s", "middle")
    s.text(857, 192, "SNV 分群", "s", "middle")
    s.text(857, 216, "樹形、CCF", "s", "middle")
    # 5 scores
    for k, (lab, w) in enumerate([("樹關係正確率", 66), ("ARI", 58), ("CCF 誤差", 22)]):
        y = 74 + k * 36
        s.text(1007, y + 6, lab, "s")
        s.rect(1124, y - 7, 62, 14, "panel2", None, r=3)
        s.rect(1124, y - 7, w * 62 / 66, 14, "ink2", None, r=3)
    s.text(1097, 192, "加 HP − 不加 HP", "s", "middle")
    s.text(1097, 218, "CCF：帶 SNV 細胞比例", "s", "middle")

    # lower row: three metric sketches
    y0 = 262
    s.rect(0, y0, 590, 243, "panel", None, r=10)
    s.text(16, y0 + 32, "樹關係正確率：任兩個 SNV 的關係", "h")
    tag(s, 510, y0 + 32, "示意", "demo")
    cases = [("同群", "A", "A"), ("祖先", "A", "B"), ("後代", "B", "A"), ("不同支", "B", "C")]
    for i, (lab, n1, n2) in enumerate(cases):
        cx = 80 + i * 143
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
    s.star(398, y0 + 222, 7)
    s.text(408, y0 + 228, "1", "s")
    s.text(424, y0 + 228, "SNV1", "s")
    s.star(494, y0 + 222, 7)
    s.text(504, y0 + 228, "2", "s")
    s.text(520, y0 + 228, "SNV2", "s")

    s.rect(605, y0, 280, 243, "panel", None, r=10)
    s.text(620, y0 + 32, "ARI：只比 SNV 分群", "h")
    rows = [("真值", [(712, ["c1"]), (772, ["c2"]), (832, ["c3"])]),
            ("重建", [(712, ["c1"]), (802, ["c2", "c3"])])]
    for k, (lab, groups) in enumerate(rows):
        y = y0 + 78 + k * 64
        s.text(620, y + 7, lab, "b")
        for gx, cols in groups:
            rx = 26 * len(cols) + (4 if len(cols) > 1 else 0)
            s.raw(f'<ellipse cx="{gx}" cy="{y}" rx="{rx}" ry="22" style="fill:none;stroke:var(--ink2);stroke-width:2"/>')
            dots = [c for c in cols for _ in range(2)]
            for j, c in enumerate(dots):
                s.circle(gx + (j - (len(dots) - 1) / 2) * 22, y, 8, c, "cellline", 1.2)
    s.text(745, y0 + 200, "不看樹形", "b", "middle")
    tag(s, 620, y0 + 228, "示意", "demo")

    s.rect(900, y0, 300, 243, "panel", None, r=10)
    s.text(915, y0 + 32, "事先定的規則", "h")
    tag(s, 1060, y0 + 32, "示意", "demo")
    X = lambda v: 1050 + v * 3000
    s.rect(X(-0.02), y0 + 50, X(0.02) - X(-0.02), 92, "hl", None, r=4)
    s.line(X(0), y0 + 50, X(0), y0 + 142, "line2", 2, dash=True)
    s.line(X(-0.042), y0 + 128, X(0.042), y0 + 128, "ink2", 2)
    for v, lab in [(-0.02, "−0.02"), (0, "0"), (0.02, "+0.02")]:
        s.line(X(v), y0 + 122, X(v), y0 + 134, "ink2", 2)
        s.text(X(v), y0 + 160, lab, "s", "middle")
    s.text(X(-0.013) - 8, y0 + 108, "95% CI", "s", "end")
    s.line(X(-0.013), y0 + 102, X(0.009), y0 + 102, "ink", 4)
    s.circle(X(-0.002), y0 + 102, 7, "ink")
    for k, t in enumerate(["CI 包含 0", "平均差 < 0.02"]):
        check(s, 918, y0 + 192 + k * 28)
        s.text(944, y0 + 192 + k * 28, t, "s")
    s.text(1185, y0 + 206, "→ 沒差", "b", "end")

    notes = '這頁講模擬驗證怎麼做，以及跑之前定好的規則。上排從左到右：模擬產生一棵已知的樹，5 個 clone、1,000 個 SNV，全部 1+1，也就是 HP1、HP2 各一份。模擬直接產生 ref、alt 計數和 HP，沒有 read，HP 完全已知。同一個程式跑加 HP、不加 HP 兩種輸入，每棵樹用兩個亂數起點，也就是 seed，各跑一次，再和真值比、算分數。下排是示意。左邊是主要分數：任兩個 SNV 的關係是同群、祖先、後代或不同支，算和真值一樣的比例。中間 ARI 只看分群。右邊是事先定的規則：95% 信賴區間，也就是 CI，包含 0，而且平均差小於 0.02，就算沒差。'
    write_page("sim-method", page("sim-method", "已知樹 → 加 HP／不加 HP 重建 → 和真值比，差距小於 0.02 算沒差", s, notes=notes))


# ---- p6 sim-result ----------------------------------------------------------------------

def p6():
    d = tree_diffs()
    s = S("p6", 1200, 505)
    s.rect(0, 0, 800, 505, "panel", None, r=10)
    X = lambda v: 470 + v * 3750
    tag(s, 14, 34, "實際結果", "real")
    s.rect(X(-0.02), 72, X(0.02) - X(-0.02), 356, "hl", None, r=4)
    s.text(X(0), 64, "±0.02 內算沒差", "s", "middle")
    s.line(X(0), 72, X(0), 428, "line2", 2, dash=True)
    # seed variation ruler
    s.line(X(-0.0115), 30, X(0.0115), 30, "stgap", 4)
    for v in (-0.0115, 0.0115):
        s.line(X(v), 22, X(v), 38, "stgap", 3)
    s.text(X(0.0115) + 12, 36, "換 seed 重跑，平均差 0.023", "s", "start", "stgap")
    for i, v in enumerate(d):
        y = 92 + i * 30
        s.text(150, y + 6, f"第 {i + 1} 棵", "s", "end")
        s.line(160, y, 780, y, "line", 1)
        s.circle(X(v), y, 7, "ink2")
    y = 404
    s.text(150, y + 7, "平均", "b", "end")
    s.line(X(-0.0357), y, X(0.0131), y, "ink", 5)
    for v in (-0.0357, 0.0131):
        s.line(X(v), y - 10, X(v), y + 10, "ink", 3)
    s.circle(X(-0.0113), y, 10, "ink")
    s.text(X(0.0131) + 22, y + 7, "−0.011（CI −0.036 到 +0.013）", "s")
    s.line(X(-0.08), 440, X(0.08), 440, "ink2", 2)
    for v in (-0.06, -0.04, -0.02, 0, 0.02, 0.04, 0.06):
        s.line(X(v), 434, X(v), 446, "ink2", 2)
        s.text(X(v), 466, "0" if v == 0 else f"{'+' if v > 0 else '−'}{abs(v):.2f}", "s", "middle")
    s.text(X(0), 495, "← 不加 HP 較好　樹關係正確率：加 HP − 不加 HP　加 HP 較好 →", "s", "middle")

    # right: secondary measures
    s.rect(820, 0, 380, 228, "panel", None, r=10)

    def mini(y, title, lo, mean, hi, scale, note, lab):
        s.text(836, y, title, "b")
        Xm = lambda v: 1010 + v * scale
        s.line(Xm(0), y + 16, Xm(0), y + 54, "line2", 2, dash=True)
        s.line(Xm(lo), y + 35, Xm(hi), y + 35, "ink", 4)
        s.circle(Xm(mean), y + 35, 8, "ink")
        s.text(Xm(0), y + 76, "0", "s", "middle")
        s.text(836, y + 41, lab, "s")
        s.text(1184, y + 76, note, "s", "end")

    mini(32, "ARI（SNV 分群）", -0.0015, 0.0232, 0.0479, 2900, "8／10 棵較高", "+0.023")
    mini(140, "CCF 誤差（越小越準）", -0.0035, -0.0019, -0.0003, 22000, "7／10 棵較準", "−0.002")

    s.rect(820, 246, 380, 259, "panel", None, r=10)
    s.text(836, 280, "主要分數對事先規則", "b")
    for k, (ok, t) in enumerate([(True, "CI 包含 0"), (True, "平均差 0.011 < 0.02"),
                                 (False, "CI 下限 −0.036 超出 ±0.02")]):
        check(s, 838, 320 + k * 32, ok)
        s.text(866, 320 + k * 32, t, "s")
    s.line(836, 404, 1184, 404, "line2", 1.5)
    s.text(836, 436, "符合事先規則，", "b")
    s.text(836, 466, "但不足以證明兩者一樣", "b")
    s.text(836, 494, "→ 沒看到 HP 改善樹形", "s", "start", "ink2")

    notes = '這頁要看的是：加 HP 沒有讓樹形變好。左邊每個點是一棵樹，往右是加 HP 較好；10 棵裡左右各 5 棵。最下面黑線是平均負 0.011 和 95% CI。黃色帶是事先定的正負 0.02。上面灰線是換 seed 重跑的平均差 0.023，和加不加 HP 的差一樣大。右下：符合事先規則，但 CI 下限超出黃色帶，所以只說沒看到改善，不說兩者一樣。右上兩個次要分數：ARI 略高但 CI 含 0；CCF 誤差只少 0.002。'
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
    s.text(42, 380, "這組設定下，加 HP 沒改善樹關係，CCF 略準", "s")
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
