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
    s = S("hg008-tree", 1200, 462)
    s.text(0, 26, "沒有真值樹；樹由 8 株選殖株推論；用 short read 單細胞獨立檢查", "h")

    # Left: how the tree was inferred.
    s.rect(0, 50, 222, 400, "panel", None, r=10)
    s.text(111, 80, "8 株選殖株", "b", "middle")
    for i in range(8):
        tube(s, 22 + i * 25.5, 96, w=14, h=36)
    s.text(111, 160, "PacBio long read", "s", "middle")
    pill(s, 30, 196, "多株＝上限參考")
    s.arrow(111, 214, 111, 238, sw=2.5)
    s.poly([(36, 244), (186, 244), (126, 296), (96, 296)], "panel3")
    s.text(111, 322, "排除因流失才缺", "s", "middle")
    s.text(111, 345, "的共有 SNV", "s", "middle")
    s.rect(18, 362, 186 * 261 / 301, 26, "c4", None, r=3)
    s.rect(18 + 186 * 261 / 301 + 2, 362, 186 * 40 / 301 - 2, 26, "panel3", None, r=3)
    s.text(18, 412, "261 相容", "s", "start", "c4")
    s.text(204, 412, "40 不相容", "s", "end")
    s.text(111, 438, "共 301 個", "s", "middle")
    s.arrow(228, 200, 262, 200, sw=2.5)

    # Middle: the candidate tree (elbow layout). Leaf order H G A B E F C D.
    P = hg008_tree(s, 292, 62, (62, 120, 176, 232, 288), 318, numbers=True)
    tag(s, 640, 64, "推論", "infer")
    s.text(712, 64, "數字＝SNV 數", "s", "start", "mute")

    tree_legend(s, [(262, 432), (450, 432), (616, 432)])

    # Right: 119 single cells, nested.
    cx, yb = 892, 336
    s.text(cx, 96, "119 顆單細胞", "b", "middle")
    for r, n, fill in [(108, "119", "panel"), (88, "111", "panel2"), (60, "48", "panel3"), (34, "16", "line2")]:
        s.circle(cx, yb - r, r, fill, "cellline", 2)
    s.text(cx, 186, "111", "b", "middle")
    s.text(cx, 244, "48", "b", "middle")
    s.text(cx, 309, "16", "b", "middle", "on")
    # Leader lines from each ring to the branch it supports.
    for (rx, ry), (tx, ty) in [((818, 200), (P["x7"], 90)), ((841, 244), (P["xCDEF"], 204)), ((858, 302), (P["xCD"], 262))]:
        s.path(f"M{rx} {ry} L770 {ty} L{tx + 6} {ty}", "c4", 2.5, dash=True)
        s.circle(tx, ty, 6, "c4")
    s.text(cx, 368, "short read，獨立量測", "s", "middle")

    # Bottom right: copy number that does not fit the tree.
    for i, (chrom, a, b) in enumerate([("chr5", .62, .9), ("chr12", .05, .3)]):
        y = 400 + i * 38
        s.text(768, y + 6, chrom, "s")
        s.bar(830, y, 150, "panel3", h=14)
        s.rect(830 + 150 * a, y - 7, 150 * (b - a), 14, "mut", None, r=3)
        s.xmark(998, y, 8)
    s.text(1012, 440, "拷貝數不符", "s")
    n3_ladder(s, 1046, 300, lit=(1,))
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
    n3_ladder(s, rx + 65, 420, lit=(1,))
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
        "這頁要看的是：HG008 沒有真值樹，但主要的 3 層有單細胞支持。"
        "左邊是推論步驟：8 株選殖株用 PacBio long read 定序，排除因為流失才缺的共有 SNV，301 個有 261 個相容。"
        "中間是這棵候選樹，枝上的數字是 SNV 數。實線那三層，127、14、68，右邊的單細胞都看得到：119 顆裡 111 顆、48 顆、16 顆，一層包一層。"
        "A、B 那段只有部分支持；只有 4 個 SNV 的那層最弱，虛線的部分還沒驗證。"
        "右下角 chr5、chr12 的拷貝數和樹不符。所以只支持到克隆結構，多株只當上限參考。"
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
    "hg008-tree": "HG008 候選樹：單細胞支持 3 層巢狀分枝",
    "tree-shape": "HG008 和 diplosim 的樹形：分岔形狀在範圍內，枝長在邊緣",
    "not-yet": "還做不到的三件事：COLO829 對照、親源資料、HG008 末端",
}
CAPTIONS = {
    "hg008-tree": "實線三層有單細胞支持；A、B 只部分支持，其餘末端還沒驗證。",
    "tree-shape": "HG008 只有一棵樹，所以只能說不矛盾。",
    "not-yet": "",
}

if __name__ == "__main__":
    # p13 not-yet was deleted by the user in the deck editor on 2026-11-08; p13() is kept for reference only.
    for pid, fn in [("hg008-tree", p11), ("tree-shape", p12)]:
        s = fn()
        write_page(pid, page(pid, TITLES[pid], s, CAPTIONS[pid], NOTES[pid]))
        print(pid, "notes chars:", len(NOTES[pid]))
