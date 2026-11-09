"""Result pages, second half: p11 hg008-tree, p12 tree-shape (p13 not-yet deleted 2026-11-08).

Numbers come from lab_report/2026-11-07_hg008_tree_rebuild/ and 2026-11-07_hg008_sc_check/ (BRIEF R10, R11).
p12 histograms read the real per-tree values (diplosim_trees.tsv, scenario sample_8_of_more).
"""
import csv
from pathlib import Path

from slidekit import S, page, write_page, n3_ladder, tag
from lib import width

ROOT = Path(__file__).resolve().parents[2]
TREES = ROOT / "lab_report/2026-11-07_hg008_tree_rebuild/tables/diplosim/diplosim_trees.tsv"
COMP = ROOT / "lab_report/2026-11-07_hg008_tree_rebuild/tables/diplosim/comparison.tsv"


# ---- small pictograms ---------------------------------------------------------------

def tube(s, x, top, w=18, h=42, label=None):
    """One test tube (a clone line): open top, round bottom, liquid in the lower half. No clone colors."""
    r = w / 2
    body = f"M{x - r:.1f} {top:.1f} L{x - r:.1f} {top + h - r:.1f} A{r:.1f} {r:.1f} 0 0 0 {x + r:.1f} {top + h - r:.1f} L{x + r:.1f} {top:.1f}"
    liquid = f"M{x - r:.1f} {top + h * .45:.1f} L{x - r:.1f} {top + h - r:.1f} A{r:.1f} {r:.1f} 0 0 0 {x + r:.1f} {top + h - r:.1f} L{x + r:.1f} {top + h * .45:.1f} Z"
    s.path(liquid, None, 0, "panel3")
    s.path(body, "ink2", 2)
    s.line(x - r - 3, top, x + r + 3, top, "ink2", 2.5)
    if label:
        s.text(x, top + h + 24, label, "b", "middle")


def branch(s, x1, y1, x2, y2, style, c="ink", sw=4.5):
    """style: solid = single cells support, half = partly, dash = not checked."""
    if style == "solid":
        s.line(x1, y1, x2, y2, c, sw)
    elif style == "half":
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        s.line(x1, y1, mx, my, c, sw)
        s.line(mx, my, x2, y2, c, sw - 1.5, dash=True)
    else:
        s.line(x1, y1, x2, y2, "line2", 2.5, dash=True)


def pill(s, x, y, text, col="ink2"):
    w = width(text, 18) + 24
    s.rect(x, y - 21, w, 30, None, col, r=15, sw=2)
    s.text(x + w / 2, y, text, "s", "middle", col)
    return w


LEAVES = "HGABEFCD"


def hg008_tree(s, x0, dx, ys, leaf, tube_w=18, tube_h=42, sw=4.5, stub=22, numbers=False, lab=True):
    """The HG008 candidate tree (p11, p13, p16 draw it with this one function, F-4).

    Leaf order H G A B E F C D. Solid = single cells support (127, 14, 68 SNVs), half = partly ({A, B}),
    dashed = not checked. Returns the x of each leaf and internal node.
    """
    X = {k: x0 + i * dx for i, k in enumerate(LEAVES)}
    yR, y7, y6, y4, y2 = ys
    xAB = (X["A"] + X["B"]) / 2
    xEF = (X["E"] + X["F"]) / 2
    xCD = (X["C"] + X["D"]) / 2
    xCDEF = (xEF + xCD) / 2
    x6 = (xAB + xCDEF) / 2
    x7 = (X["G"] + x6) / 2
    xR = (X["H"] + x7) / 2
    for a, b, y in [(X["H"], x7, yR), (X["G"], x6, y7), (xAB, xCDEF, y6), (X["A"], X["B"], y4),
                    (xEF, xCD, y4), (X["E"], X["F"], y2), (X["C"], X["D"], y2)]:
        s.line(a, y, b, y, "ink2", 2.5)
    s.line(xR, yR - stub, xR, yR, "ink2", 2.5)
    branch(s, x7, yR, x7, y7, "solid", sw=sw)
    branch(s, x6, y7, x6, y6, "dash")
    branch(s, xAB, y6, xAB, y4, "half", sw=sw)
    branch(s, xCDEF, y6, xCDEF, y4, "solid", sw=sw)
    branch(s, xCD, y4, xCD, y2, "solid", sw=sw)
    branch(s, xEF, y4, xEF, y2, "dash")
    for k, y0 in [("H", yR), ("G", y7), ("A", y4), ("B", y4), ("E", y2), ("F", y2), ("C", y2), ("D", y2)]:
        branch(s, X[k], y0, X[k], leaf, "dash")
        tube(s, X[k], leaf, w=tube_w, h=tube_h, label=k if lab else None)
    if numbers:
        def mid(a, b):
            return (a + b) / 2 + 7
        s.text(x7 - 10, mid(yR, y7), "127", "b", "end")
        s.text(x6 + 10, mid(y7, y6), "4", "b")
        s.text(x6 + 30, mid(y7, y6), "最弱", "s", "start", "stdis")
        s.text(xAB - 10, mid(y6, y4), "31", "b", "end")
        s.text(xCDEF - 10, mid(y6, y4), "14", "b", "end")
        s.text(xEF - 10, mid(y4, y2), "17", "b", "end")
        s.text(xCD - 10, mid(y4, y2), "68", "b", "end")
    return dict(X=X, ys=ys, xAB=xAB, xEF=xEF, xCD=xCD, xCDEF=xCDEF, x6=x6, x7=x7, xR=xR)


def tree_legend(s, pts, sw=4):
    """Line-style legend for the HG008 tree. pts: three (x, y) for solid / half / dash."""
    for (x0, ly), (st, lab) in zip(pts, [("solid", "單細胞支持"), ("half", "部分支持"), ("dash", "未驗證")]):
        branch(s, x0, ly - 6, x0 + 40, ly - 6, st, sw=sw)
        s.text(x0 + 46, ly, lab, "s")


# ---- p11 ---------------------------------------------------------------------------

def p11():
    # 2026-11-09 v2 (user): show only the 4 groups the single cells support. A clone group is a circle of cells,
    # cells carry the branch mutations (stars). Numbers: lab_report/2026-11-07_hg008_sc_check/ branch_summary
    # (127 -> 111 cells, 14 -> 48, 68 -> 16, 8 cells without 127). Groups: 8, 111-48, 48-16, 16.
    # Clone letters per group follow the candidate tree (H | G, A, B | E, F | C, D); the 4-, 31- and 17-SNV
    # branches are not confirmed by single cells and are merged into their group.
    import math
    s = S("hg008-tree", 1200, 462)
    RED, PUR, GOLD = "mut", "c2", "c3"
    s.text(0, 26, "8 株選殖株（long read）推出的樹，用 119 顆單細胞（short read）檢查後，可靠的是這 4 群", "h")

    gx = [150, 450, 750, 1050]       # group centres
    gy, gr = 344, 68
    groups = [(8, 0, "選殖株 H"), (63, 1, "G、A、B"), (32, 2, "E、F"), (16, 3, "C、D")]
    # binary tree (2026-11-09 v3, user): root -> (group 1, R); R -> (group 2, P); P -> (group 3, group 4).
    # Internal nodes sit above the middle of their children; edges are straight lines.
    top = gy - gr
    P = ((gx[2] + gx[3]) / 2, 204)
    R = ((gx[1] + P[0]) / 2, 126)
    root = ((gx[0] + R[0]) / 2, 50)
    edges = [(root, (gx[0], top), None), (root, R, (RED, "127")),
             (R, (gx[1], top), None), (R, P, (PUR, "14")),
             (P, (gx[2], top), None), (P, (gx[3], top), (GOLD, "68"))]
    for (x1, y1), (x2, y2), mut in edges:
        if mut:
            col, lab = mut
            s.line(x1, y1, x2, y2, col, 6)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            s.star(mx - 4, my - 16, 10, col)
            s.text(mx + 16, my - 8, f"{lab} 個 SNV", "b", "start", col)
        else:
            s.line(x1, y1, x2, y2, "ink2", 2.5)
    for nx, ny in (root, R, P):
        s.circle(nx, ny, 7, "ink2")

    def cell(x, y, stars):
        s.circle(x, y, 12, "on", "cellline", 1.5)
        cols = [RED, PUR, GOLD][:stars]
        for j, c in enumerate(cols):
            s.star(x + (j - (len(cols) - 1) / 2) * 7.5, y + 1, 3.8, c)

    fills = ["panel", "panel2", "panel3", "hl"]
    for (n, stars, clones), x, fill in zip(groups, gx, fills):
        s.circle(x, gy, gr, fill, "cellline", 2.5)
        s.text(x, gy - gr + 26, f"{n} 顆", "h", "middle")
        k = max(3, round(n / 6))                                   # one drawn cell ~ 6 real cells (示意)
        pts = []                                                   # hexagonal packing, nearest the centre first
        for row in range(-3, 4):
            for col in range(-3, 4):
                px, py = col * 27 + (row % 2) * 13.5, row * 24
                if math.hypot(px, py) <= 42:
                    pts.append((math.hypot(px, py), px, py))
        for _, px, py in sorted(pts)[:k]:
            cell(x + px, gy + 10 + py, stars)
        s.text(x, gy + gr + 28, clones, "b", "middle", "ink2")

    s.text(1180, 64, "★ 同一組突變：選殖株和單細胞都看到", "s", "end", "ink2")
    tag(s, 976, 98, "細胞數量示意", "demo")
    s.text(1180, 128, "顆數是實際結果", "s", "end", "mute")
    s.text(0, 64, "另外 4、31、17 個 SNV 的分枝", "s", "start", "mute")
    s.text(0, 88, "單細胞還沒證實，併在同一群", "s", "start", "mute")
    return s


# ---- p12 ---------------------------------------------------------------------------

STATS = [
    # key, name, HG008 value shown, verdict, weak, bins (lo, hi, step), clip
    ("colless", "分岔不平衡（Colless）", "13", "ok", False, (0, 22, 1)),
    ("terminal_share", "末端枝 SNV 比例", "0.85", "edge", True, (0.2, 1.0, 0.05)),
    ("internal_per_terminal", "內部／末端枝長比", "0.24", "edge", False, (0.0, 2.0, 0.1)),
    ("terminal_cv", "末端枝長變異係數", "0.38", "edge", True, (0.2, 1.8, 0.1)),
]


def p12():
    rows = [r for r in csv.DictReader(TREES.open(), delimiter="\t") if r["scenario"] == "sample_8_of_more"]
    comp = {(r["scenario"], r["statistic"]): r for r in csv.DictReader(COMP.open(), delimiter="\t")}
    n = len(rows)
    s = S("tree-shape", 1200, 462)
    s.text(0, 26, f"灰柱＝diplosim {n:,} 棵樹（各取 8 葉）的實際分布；紅線＝HG008", "t")
    tag(s, 660, 26, "實際結果", "real")
    PW, PH = 438, 190
    for i, (key, name, hv, verdict, weak, (lo, hi, step)) in enumerate(STATS):
        c = comp[("sample_8_of_more", key)]
        px, py = (i % 2) * (PW + 16), 42 + (i // 2) * (PH + 10)
        col = "stok" if verdict == "ok" else "stdis"
        s.rect(px, py, PW, PH, "paper", col, r=8, sw=2.5)
        s.text(px + 14, py + 28, name, "b")
        vt = "範圍內" if verdict == "ok" else "邊緣"
        vw = width(vt, 18) + 24
        pill(s, px + PW - 14 - vw, py + 28, vt, col)
        if weak:
            pill(s, px + PW - 14 - vw - 8 - (width("證據弱", 18) + 24), py + 28, "證據弱", "mut")
        # Histogram.
        hx0, hx1, hy0, hy1 = px + 18, px + PW - 18, py + 70, py + PH - 34
        nb = round((hi - lo) / step)
        counts = [0] * nb
        for r in rows:
            v = min(max(float(r[key]), lo), hi - 1e-9)
            counts[int((v - lo) / step)] += 1
        top = max(counts)
        bw = (hx1 - hx0) / nb

        def xpos(v):
            return hx0 + (min(max(v, lo), hi) - lo) / (hi - lo) * (hx1 - hx0)
        a, b = xpos(float(c["diplosim_p2.5"])), xpos(float(c["diplosim_p97.5"]))
        s.rect(a, hy0, b - a, hy1 - hy0, "hl", None, r=0)
        for k, cnt in enumerate(counts):
            h = (hy1 - hy0 - 6) * cnt / top
            s.rect(hx0 + k * bw + 1, hy1 - h, bw - 2, h, "panel3", None, r=1)
        s.line(hx0, hy1, hx1, hy1, "ink2", 2)
        hxv = xpos(float(c["hg008"]))
        s.line(hxv, py + 40, hxv, hy1 + 4, "mut", 4)
        pct = c["hg008_percentile"]
        lab = f"HG008 {hv}：第 {pct} 百分位"
        a_ = "end" if hxv > px + PW / 2 else "start"
        s.text(hxv + (-8 if a_ == "end" else 8), py + 58, lab, "s", a_, "mut")
        s.text(hx0, hy1 + 22, f"{lo:g}", "s")
        s.text(hx1, hy1 + 22, f"{hi:g}" + ("+" if key != "colless" else ""), "s", "end")
        if key == "terminal_cv":
            e8 = comp[("exactly_8_leaves", key)]["hg008_percentile"]
            s.text(hx1, hy0 + 30, f"剛好 8 葉時：第 {e8} 百分位", "s", "end", "mut")
        if i == 0:
            s.text((a + b) / 2, hy1 + 22, "淺底＝中間 95%", "s", "middle", "mute")
    s.text(0, 455, "百分位＝diplosim 樹中 ≤ HG008 的比例，不是 p 值", "s", "start", "mute")

    # Right column: the two trees are not the same kind of tree.
    rx = 920
    s.rect(rx, 42, 280, 182, "panel", None, r=10)
    s.text(rx + 140, 68, "兩種樹不完全相同", "b", "middle")
    for j, (cx, lab1, lab2, kind) in enumerate([(rx + 70, "HG008", "細胞株譜系", "tube"),
                                                  (rx + 210, "diplosim 亞群", "clone tree", "node")]):
        top, mid, bot = 84, 112, 146
        s.line(cx, top, cx, mid, "ink2", 2.5)
        s.line(cx - 34, mid, cx + 34, mid, "ink2", 2.5)
        for dx in (-34, 0, 34):
            s.line(cx + dx, mid, cx + dx, bot - 4, "ink2", 2.5)
            if kind == "tube":
                tube(s, cx + dx, bot - 4, w=12, h=26)
            else:
                s.circle(cx + dx, bot + 8, 10, ("c1", "c2", "c3")[(dx + 34) // 34], "cellline")
        s.text(cx, 194, lab1, "s", "middle")
        s.text(cx, 216, lab2, "s", "middle")
    s.text(rx + 140, 140, "≠", "big", "middle")
    # Fixed comparison: merge one-child chains.
    s.rect(rx, 234, 280, 82, "panel", None, r=10)
    for k in range(3):
        s.circle(rx + 30, 251 + k * 24, 7, "panel3", "cellline")
        if k:
            s.line(rx + 30, 251 + (k - 1) * 24 + 7, rx + 30, 251 + k * 24 - 7, "ink2", 2)
    s.arrow(rx + 48, 275, rx + 82, 275, sw=2.5)
    s.circle(rx + 100, 275, 7, "panel3", "cellline")
    s.text(rx + 118, 268, "直鏈併成一點", "s")
    s.text(rx + 118, 294, "首次漏做，已修正", "s", "start", "mute")
    # 2026-11-08: the three-layer validation ladder was removed at the user's request (not agreed).
    return s


# ---- p13 ---------------------------------------------------------------------------

def p13():
    s = S("not-yet", 1200, 462)
    W, G = 388, 18
    heads = ["COLO829 近距離對照沒過", "沒有親源資料", "HG008 末端難驗證"]
    for i, hd in enumerate(heads):
        x = i * (W + G)
        s.rect(x, 0, W, 462, "panel", None, r=10)
        s.circle(x + 28, 32, 15, "mut")
        s.text(x + 28, 39, str(i + 1), "b", "middle", "on")
        s.text(x + 54, 39, hd, "h")

    # 1. A double-base change sits on one read, so the pair is always "same strand".
    x = 0
    s.text(x + 194, 90, "一個雙鹼基突變（例：CC>TT）", "s", "middle")
    s.rect(x + 40, 112, 308, 16, "panel3", None, r=8)
    s.star(x + 186, 120, 11); s.star(x + 204, 120, 11)
    s.text(x + 160, 164, "相鄰 1 bp：必然同一條", "s", "middle")
    tag(s, x + 272, 164, "推論", "infer")
    s.arrow(x + 194, 178, x + 194, 206, sw=2.5)
    s.text(x + 194, 230, "被算成 <1 kb 的 SNV 配對", "s", "middle")
    # Control bar vs threshold.
    by0, by1 = 250, 420
    def yv(v):
        return by1 - (v - 0.4) / 0.6 * (by1 - by0)
    s.line(x + 70, by1, x + 330, by1, "ink2", 2)
    s.rect(x + 90, yv(0.658), 80, by1 - yv(0.658), "panel3", None, r=3)
    s.rect(x + 90, yv(0.658), 80, 20, "stdis", None, r=3, op=.55)
    s.text(x + 130, yv(0.658) - 8, "0.658", "b", "middle")
    s.line(x + 80, yv(0.8), x + 330, yv(0.8), "ink", 2.5, dash=True)
    s.text(x + 330, yv(0.8) - 8, "門檻 0.8", "s", "end")
    s.xmark(x + 290, yv(0.70), 11)
    s.text(x + 308, yv(0.70) + 7, "未過", "b", "start", "mut")
    s.text(x + 130, by1 + 26, "同一條比例", "s", "middle")
    s.text(x + 180, yv(0.658) + 17, "可能被撐高：", "s", "start", "stdis")
    s.text(x + 180, yv(0.658) + 41, "真正的值可能更低", "s", "start", "stdis")

    # 2. Only group names, no parent labels.
    x = W + G
    cx = x + W / 2
    for dx, who in [(-80, "爸"), (80, "媽")]:
        s.person(cx + dx, 84, 70, "panel3")
        s.text(cx + dx, 182, who + "？", "h", "middle")
    s.bar(x + 60, 236, 268, "hp1", h=16)
    s.bar(x + 60, 276, 268, "hp2", h=16)
    s.text(x + 60, 262, "HP1", "s", "start", "hp1")
    s.text(x + 60, 304, "HP2", "s", "start", "hp2")
    s.text(cx, 340, "資料只有組名", "t", "middle")
    s.arrow(cx, 354, cx, 382, sw=2.5)
    s.rect(x + 74, 392, W - 148, 40, "paper", "ink2", r=8, sw=2)
    s.text(cx, 419, "需要親代定序", "b", "middle")
    for dx in (-80, 80):
        s.line(cx + dx, 194, cx + dx, 222, "line2", 2, dash=True)

    # 3. The tips of the HG008 tree.
    x = 2 * (W + G)
    LEAF = 300
    yR, y7, y6, y4, y2 = 96, 132, 166, 200, 236
    P = hg008_tree(s, x + 46, 42, (yR, y7, y6, y4, y2), LEAF, tube_w=14, tube_h=32, sw=4, stub=16)
    X, xAB, xEF = P["X"], P["xAB"], P["xEF"]
    s.rect(xAB - 30, y6 + 6, 60, y4 - y6 + 8, None, "stdis", r=6, sw=2.5)
    s.text(xAB, y6 - 10, "部分", "s", "middle", "stdis")
    s.rect(xEF - 26, y4 + 4, 52, y2 - y4 + 6, None, "stdis", r=6, sw=2.5)
    s.text(xEF + 30, y4 + 22, "0 顆", "s", "start", "stdis")
    s.rect(x + 22, LEAF - 30, W - 44, 26, "hl", None, r=4, op=.6)
    s.cell(X["H"] + 22, LEAF - 17, 9, "panel3")
    s.text(x + W / 2, 394, "8 條末端枝：只有 H 有 1 顆帶者", "s", "middle")
    s.text(x + W / 2, 424, "細胞圓＝達到帶者標準的單細胞", "s", "middle", "mute")
    return s


NOTES = {
    "hg008-tree": (
        "這頁要看的是：HG008 的樹，用單細胞檢查後，可靠的是 4 群。"
        "每個大圓是一群細胞，小圓是細胞，裡面的星星是它帶的突變。"
        "最左邊 8 顆沒有紅星，對應選殖株 H；紅星那段有 127 個 SNV，只帶紅星的有 63 顆，對應 G、A、B；"
        "再往右多了紫星 14 個 SNV，32 顆，對應 E、F；最右邊三種星都有，金星 68 個 SNV，16 顆，對應 C、D。"
        "選殖株和單細胞看到同一組突變，所以這 4 群互相確認。底下那幾段分枝，單細胞還沒證實，併在同一群。"
    ),
    "tree-shape": (
        "這裡可以看到，HG008 的分岔形狀落在 diplosim 的範圍內，跟枝長有關的三個指標在邊緣。"
        "灰柱是 diplosim 一千一百多棵樹的實際分布，紅線是 HG008。"
        "左上的分岔不平衡在第 87 百分位，綠框，範圍內。"
        "末端枝比例在第 94，內部對末端枝長比在第 6，末端枝長變異係數在第 3，剛好 8 葉時是第 1.2，這三個是棕框的邊緣，兩個標了證據弱。"
        "百分位不是 p 值。右邊提醒，HG008 是細胞株的譜系，diplosim 是亞群的 clone tree，兩種樹不完全相同；第一次比時沒把直鏈併成一點，已修正。"
        "結果段到這裡，下一頁是自我檢查。"
    ),
    "not-yet": (
        "這頁列出三件現在還做不到的事。"
        "第一格，COLO829 近距離的對照是 0.658，沒過 0.8 的門檻。像 CC 變 TT 這種雙鹼基突變，兩個位置只差 1 bp，必然在同一條，可能把比例撐高，也就是真正的值可能更低；這是我們的推論，還要重算。"
        "第二格，資料只有 HP1、HP2 這種組名，沒有爸爸、媽媽的標籤，要有親代定序才能定。"
        "第三格，HG008 樹的末端：A、B 那段只有部分支持，E、F 那段沒有細胞達標，8 條末端枝只有 H 有 1 顆帶者。"
        "結果段到這裡。接下來是自我檢查，下一頁對照上次會議的檢查清單。"
    ),
}

TITLES = {
    "hg008-tree": "HG008 候選樹：選殖株和單細胞都支持 4 群",
    "tree-shape": "HG008 和 diplosim 的樹形：分岔形狀在範圍內，枝長在邊緣",
    "not-yet": "還做不到的三件事：COLO829 對照、親源資料、HG008 末端",
}
CAPTIONS = {
    "hg008-tree": "",
    "tree-shape": "HG008 只有一棵樹，所以只能說不矛盾。",
    "not-yet": "",
}

if __name__ == "__main__":
    # p13 not-yet was deleted by the user in the deck editor on 2026-11-08; p13() is kept for reference only.
    # tree-shape was deleted by the user in the deck editor on 2026-11-08; p12() kept for reference only.
    for pid, fn in [("hg008-tree", p11)]:
        s = fn()
        write_page(pid, page(pid, TITLES[pid], s, CAPTIONS[pid], NOTES[pid]))
        print(pid, "notes chars:", len(NOTES[pid]))
