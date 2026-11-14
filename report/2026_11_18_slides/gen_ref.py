"""HG008 reference tree, two pages (user 2026-11-14: split "how 8 clones build the tree" from "how single cells check it").

ref-tree  (p3): 8 clone lines -> six plain steps -> the tree; resampling check.
ref-check (p4): 119 single cells -> four plain steps -> 5 clones, single cells in 4; can / cannot prove.

Sources (BRIEF R1): lab_report/2026-11-07_hg008_tree_rebuild/HOW_TREE_WAS_BUILT.md steps 1-9 (7,784 / 1,203 / 3,593;
301 clean shared SNVs, 261 on the tree; branch SNV counts 127 / 4 / 31 / 14 / 17 / 68; bootstrap 1,000; 5 thresholds);
lab_report/2026-11-07_hg008_sc_check/ (119 cells; 111 / 48 / 16 carriers, 0 violations; example cell: truncal 89 %
(6,936 / 7,784), 127-branch 91 % (115 / 127); another cell 14-branch 0 %; clones 8 / 63 / 32 / 16).
The tree copies report/2026_11_11_slides/gen_res2.py p_tree (user 11-14: draw it as last week); +792 = H private.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python3 -I does not add the script folder
from slidekit import S, page, write_page, tag  # noqa: E402
from gen_bg import tube, mark, dice  # noqa: E402

RED, PUR, GOLD = "c1", "c2", "c3"     # the three branches single cells support: 127, 14, 68 SNVs
LEAVES = "HGABEFCD"
H = 660


CARD_H = 256


def card(s, x, w, n, title, sub):
    """One step: number badge, icon area y 40-190 (drawn by the caller), plain title, one short line."""
    s.rect(x, 0, w, CARD_H, "panel", None, r=12)
    s.circle(x + 22, 24, 15, "ink2")
    s.text(x + 22, 31, str(n), "b", "middle", "on")
    s.text(x + w / 2, 214, title, "b", "middle")
    s.text(x + w / 2, 242, sub, "s", "middle", "ink2")


def step_arrows(s, xs, w, y=120):
    """w: one width for all cards, or a list of widths."""
    ws = w if isinstance(w, list) else [w] * len(xs)
    for x, cw in zip(xs[:-1], ws):
        s.poly([(x + cw + 3, y - 9), (x + cw + 13, y), (x + cw + 3, y + 9)], "ink2")


def funnel(s, cx, top):
    s.path(f"M{cx - 54} {top} L{cx + 54} {top} L{cx + 12} {top + 70} L{cx + 12} {top + 112} "
           f"L{cx - 12} {top + 112} L{cx - 12} {top + 70} Z", "ink2", 2.5, "on")
    for dx, dy in ((-30, 16), (0, 26), (26, 14), (-12, 44)):
        s.star(cx + dx, top + dy, 8, "mut")
    for dx, dy in ((70, 30), (70, 66)):           # weak calls pushed aside
        s.star(cx + dx, top + dy, 8, "panel3")
        s.xmark(cx + dx, top + dy, 9, "mut", 2.5)
    s.star(cx, top + 134, 8, "mut")


HEX = [(0, 0), (-20, 0), (20, 0), (-10, -17), (10, -17), (-10, 17), (10, 17)]


def clone_tree(s, by, mode):
    """The 11-11 deck's clone tree (report/2026_11_11_slides/gen_res2.py p_tree), same layout, a bit smaller:
    ancestor at the top; H down-left (dashed: defined only by lacking the +127); G A B down-right; then E F and
    C D straight below. Labels left of each circle, new SNVs beside each arrow.
    mode "clones": circles hold the clone lines (tubes). mode "cells": circles hold cells with their stars + counts."""
    r = 34
    root, gH, g2, g3, g4 = (360, by + 44), (180, by + 142), (560, by + 142), (560, by + 240), (560, by + 336)

    def cell(x, y, k):
        s.circle(x, y, 10, "on", "cellline", 1.4)
        if k == "H":
            s.star(x, y + 1, 4.2, "line2")
            return
        cols = [RED, PUR, GOLD][:k]
        for j, c in enumerate(cols):
            s.star(x + (j - (len(cols) - 1) / 2) * 6.5, y + 1, 3.3, c)

    def clone(xy, n, k, tint, letters, dashed=False):
        x, y = xy
        if tint:
            s.circle(x, y, r, tint, None, op=0.16)
        s.circle(x, y, r, None if tint else "paper", "cellline", 2.2, dash=dashed)
        if mode == "cells":
            for px, py in HEX[:min(7, max(3, round(n / 9)))]:
                cell(x + px, y + py, k)
        else:
            ks = letters.split("、")
            for i, L in enumerate(ks):
                tube(s, x + (i - (len(ks) - 1) / 2) * 22, y - 17, w=14, h=30)

    def arrow(p, q, col, n, left=False):
        (x1, y1), (x2, y2) = p, q
        s.arrow(x1, y1, x2, y2, c=col, sw=4, head=11)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if left:
            s.star(mx - 30, my, 9, col)
            s.text(mx - 46, my + 7, f"+{n} 個 SNV", "b", "end", "mute" if col == "line2" else col)
        else:
            s.star(mx + 22, my, 9, col)
            s.text(mx + 38, my + 7, f"+{n} 個 SNV", "b", "start", col)

    # root: common ancestor (no sampled cell carries only these)
    s.circle(*root, r, "paper", "cellline", 2.2)
    s.text(root[0] - 48, root[1] - 4 if mode == "cells" else root[1] + 7, "共同祖先", "h", "end")
    if mode == "cells":
        s.text(root[0] - 48, root[1] + 22, "樣本裡 0 顆細胞", "s", "end", "ink2")
    s.text(root[0] + 48, root[1] - 4, "8 株都有的", "s", "start", "ink2")
    s.text(root[0] + 48, root[1] + 20, "7,784 個 SNV", "b", "start", "ink2")
    arrow((root[0] - 26, root[1] + 24), (gH[0] + 18, gH[1] - 31), "line2", 792, left=True)
    arrow((root[0] + 26, root[1] + 24), (g2[0] - 18, g2[1] - 31), RED, 127)
    arrow((g2[0], g2[1] + r), (g3[0], g3[1] - r), PUR, 14)
    arrow((g3[0], g3[1] + r), (g4[0], g4[1] - r), GOLD, 68)
    groups = [(gH, 8, "H", None, "H", True), (g2, 63, 1, RED, "G、A、B", False),
              (g3, 32, 2, PUR, "E、F", False), (g4, 16, 3, GOLD, "C、D", False)]
    for xy, n, k, tint, letters, dashed in groups:
        clone(xy, n, k, tint, letters, dashed)
        x, y = xy
        if mode == "cells":
            s.text(x - 48, y - 4, f"{n} 顆細胞", "h", "end")
            s.text(x - 48, y + 22, f"選殖株 {letters}", "s", "end", "ink2")
        else:
            s.text(x - 48, y + 7, f"選殖株 {letters}", "h", "end")
    if mode == "cells":
        s.star(gH[0] - 30, gH[1] + 58, 8, "line2")
        s.text(gH[0] - 18, gH[1] + 64, "H 專屬，部分支持", "s", "start", "mute")

    # legend (bottom left, as in the 11-11 deck's right column)
    lx, ly = 0, by + 262
    s.text(lx, ly, "每個圓＝一群（一個 clone）", "s", "start", "ink2")
    s.circle(lx + 12, ly + 26, 11, None, "cellline", 2, dash=True)
    s.text(lx + 30, ly + 32, "只靠「沒有 +127」定義", "s", "start", "ink2")
    s.text(lx, ly + 66, "另外 4、31、17 個 SNV 的小分支", "s", "start", "mute")
    s.text(lx, ly + 90, "還沒證實，併在同一群", "s", "start", "mute")


# ---- p3 ref-tree: how the 8 clones build the tree -----------------------------------------

def ref_tree():
    s = S("ref-tree", 1200, H)
    ws, gap = [160, 160, 160, 160, 240, 240], 16   # steps 5 and 6 are the hard ones: give them room
    xs = [sum(ws[:i]) + i * gap for i in range(6)]
    step_arrows(s, xs, ws)
    cw = 160

    # 1 eight clone lines, each grown from one cell
    x = xs[0]
    card(s, x, cw, 1, "8 株各自定序", "各從一顆細胞長成")
    for i, k in enumerate(LEAVES):
        tube(s, x + 26 + (i % 4) * 36, 50 + (i // 4) * 76, w=16, h=34, label=k)

    # 2 which clone has which SNV (grid: column = clone, row = SNV)
    x = xs[1]
    card(s, x, cw, 2, "列出每株的突變", "每列＝一個突變")
    rows = ["11111111", "11111111", "01111111", "00000011", "00011111", "00100000"]
    for r, pat in enumerate(rows):
        for c, v in enumerate(pat):
            s.rect(x + 16 + c * 16, 56 + r * 20, 14, 16, "mut" if v == "1" else "on", "line2", r=2, sw=1)
    for c, k in enumerate(LEAVES):
        s.text(x + 23 + c * 16, 188, k, "n", "middle", "mute")

    # 3 drop unreliable calls
    x = xs[2]
    card(s, x, cw, 3, "去掉不可靠的", "read 少、品質低")
    funnel(s, x + 66, 48)

    # 4 sort by how many clones carry the SNV
    x = xs[3]
    card(s, x, cw, 4, "依幾株有分類", "8 株都有＝祖先")
    groups = [(8, "ink", "7,784"), (4, "mut", "1,203"), (1, "panel3", "3,593")]
    for r, (n, col, num) in enumerate(groups):
        y = 60 + r * 44
        for c in range(8):
            s.circle(x + 12 + c * 10, y, 4, col if c < n else "on", "line2", 1.2)
        s.text(x + cw - 10, y + 7, num, "n", "end", "ink" if r < 2 else "mute")
    s.text(x + 12, 184, "1 株才有：不用", "s", "start", "mute")

    # 5 a clone "lacks" the SNV only because that stretch of chromosome was lost -> do not count it
    x, cw = xs[4], ws[4]
    card(s, x, cw, 5, "排除假的「沒有」", "掉了一段 → 這個突變不用")
    s.text(x + 50, 30, "同一個突變，三株：", "s", "start", "ink2")
    rows5 = [("A", "has", "有"), ("B", "lost", "不用"), ("C", "none", "真的沒有")]
    for r, (k, kind, lab) in enumerate(rows5):
        y = 70 + r * 50
        s.text(x + 20, y + 7, k, "b", "middle")
        if kind == "lost":
            s.bar(x + 36, y - 8, 28, "panel3", h=16)
            s.rect(x + 66, y - 8, 24, 16, None, "mut", r=3, dash=True, sw=2)
            s.bar(x + 92, y - 8, 18, "panel3", h=16)
        else:
            s.bar(x + 36, y - 8, 74, "panel3", h=16)
        if kind == "has":
            s.star(x + 78, y, 10, "mut")
        mark(s, x + 128, y, kind != "lost", r=8)
        s.text(x + 142, y + 7, lab, "s", "start", "mut" if kind == "lost" else "ink2")

    # 6 arrange into one tree: groups of clones must nest or stay apart; crossing groups are set aside
    x, cw = xs[5], ws[5]
    card(s, x, cw, 6, "排成一棵樹", "分支要包住或分開")

    def half(x0, letters, groups, ok, label):
        lx = [x0 + 14 + i * 26 for i in range(len(letters))]
        for i, k in enumerate(letters):
            s.text(lx[i], 186, k, "b", "middle", "ink2")
        for i, j, y, c, dash in groups:
            s.path(f"M{lx[i] - 8} {y + 12} L{lx[i] - 8} {y} L{lx[j] + 8} {y} L{lx[j] + 8} {y + 12}", c, 4, dash=dash)
        mid = (lx[0] + lx[-1]) / 2
        mark(s, mid - 26, 66, ok, r=9)
        s.text(mid - 10, 73, label, "s", "start", "c4" if ok else "mut")
    half(x + 12, "EFCD", [(0, 3, 112, PUR, False), (2, 3, 146, GOLD, False)], True, "包住")
    s.line(x + cw / 2, 54, x + cw / 2, 190, "line2", 1.5, dash=True)
    half(x + cw / 2 + 4, "ABEF", [(1, 2, 112, "mut", True), (2, 3, 146, "ink2", False)], False, "交叉")

    # bottom: the tree as drawn in the 11-11 deck (clone lines inside each circle)
    by = 272
    clone_tree(s, by, "clones")

    # bottom right: is it stable?
    rx = 820
    s.rect(rx, by, 1200 - rx, H - by, "on", "line2", r=12, sw=2)
    s.text(rx + 18, by + 34, "穩不穩？", "h")
    tag(s, 1200 - 112, by + 34, "實際結果", "real")
    dice(s, rx + 18, by + 58, 32)
    s.text(rx + 62, by + 82, "突變隨機重選 1,000 次", "s")
    mark(s, rx + 30, by + 128, True)
    s.text(rx + 48, by + 134, "5 個分支每次都在", "b", "start", "c4")
    mark(s, rx + 30, by + 180, True)
    s.text(rx + 48, by + 186, "換 5 種門檻：樹一樣", "b", "start", "c4")
    mark(s, rx + 30, by + 240, False)
    s.text(rx + 48, by + 246, "不能證明樹是對的", "b", "start", "mut")
    s.arrow(rx + 48, by + 290, rx + 88, by + 290, c="ink2", sw=3, head=10)
    s.text(rx + 98, by + 296, "下一頁：用單細胞檢查", "s", "start", "ink2")

    notes = ("這頁要看的是：8 株選殖株怎麼排出演化樹。上排六步。"
             "第一步，8 株各從一顆細胞長成，各自定序。第二步，列出每株的突變。"
             "第三步，read 少或品質低的先放旁邊。"
             "第四步，8 株都有的 7,784 個是共同祖先，2 到 7 株有的 1,203 個是分支。"
             "第五步，B 株看起來沒有，但它在那個位置掉了一段染色體，這個突變就先不用；C 株完整卻沒有，才算。"
             "第六步，左邊 E F C D 包住 C D，可以；右邊交叉的放旁邊。排成下面這棵樹，每個圓是一群株。"
             "右下：突變隨機重選 1,000 次再排，5 個分支每次都在；但這不能證明樹是對的，下一頁用單細胞檢查。")
    write_page("ref-tree", page("ref-tree", "8 株選殖株依共有突變排出演化樹，隨機重選 1,000 次都一樣",
                                s, notes=notes))
    return notes


# ---- p4 ref-check: single cells check the branches ----------------------------------------

def ref_check():
    s = S("ref-check", 1200, H)
    cw, gap = 282, 24
    xs = [i * (cw + gap) for i in range(4)]
    step_arrows(s, xs, cw)

    # 1 119 single cells, same batch as the bulk
    x = xs[0]
    card(s, x, cw, 1, "119 顆單細胞", "和 bulk 同一批（第 23 代）")
    for i in range(119):
        s.circle(x + 30 + (i % 17) * 13.5, 56 + (i // 17) * 17, 5.5, "on", "cellline", 1.2)
    s.text(x + cw / 2, 184, "各自定序", "s", "middle", "ink2")

    # 2 look up each branch's SNVs in the cell
    x = xs[1]
    card(s, x, cw, 2, "查樹上每個分支的突變", "這顆細胞測到幾成")
    s.circle(x + 58, 118, 40, "on", "cellline", 2)
    for dx, dy, c in ((-16, -12, RED), (14, -6, PUR), (-2, 18, GOLD)):
        s.star(x + 58 + dx, 118 + dy, 11, c)
    s.arrow(x + 104, 118, x + 132, 118, c="ink2", sw=3, head=9)
    for r, (c, n) in enumerate([(RED, "127 個"), (PUR, "14 個"), (GOLD, "68 個")]):
        y = 74 + r * 44
        s.star(x + 152, y, 10, c)
        s.text(x + 170, y + 7, n, "s")
        s.text(x + cw - 16, y + 7, "?", "b", "end", "ink2")

    # 3 carrier or not: compare with the common-ancestor rate (real example cells)
    x = xs[2]
    card(s, x, cw, 3, "判斷帶不帶", "和共同祖先測到的比例比")
    bw = 106
    rows = [("共同祖先", "ink", .89, "89%", None), ("綠色分支", RED, .91, "91%", True), ("紫色分支", PUR, 0, "0%", False)]
    for r, (lab, c, v, t, ok) in enumerate(rows):
        y = 54 + r * 42
        s.text(x + 16, y + 15, lab, "s")
        s.rect(x + 100, y, bw, 18, "on", "line2", r=3, sw=1.5)
        if v:
            s.rect(x + 100, y, bw * v, 18, c, None, r=3)
        s.text(x + 100 + bw + 6, y + 15, t, "n", "start", "ink2")
        if ok is not None:
            mark(s, x + cw - 18, y + 9, ok, r=8)
    s.text(x + 16, 184, "差不多＝帶，幾乎沒有＝不帶", "s", "start", "ink2")
    tag(s, x + cw - 108, 30, "實際例子", "real")

    # 4 nested: every inner carrier also carries the outer branch
    x = xs[3]
    card(s, x, cw, 4, "一層套一層", "違反 0 顆")
    for (c, n, cx, cy, rx_, ry) in [(RED, "111 顆", 140, 112, 122, 70), (PUR, "48 顆", 166, 124, 86, 50),
                                    (GOLD, "16 顆", 186, 134, 44, 28)]:
        s.raw(f'<ellipse cx="{x + cx}" cy="{cy}" rx="{rx_}" ry="{ry}" style="fill:none;stroke:{_hex(c)};stroke-width:3"/>')
    s.text(x + 46, 119, "111", "b", "middle", RED)
    s.text(x + 116, 131, "48", "b", "middle", PUR)
    s.text(x + 186, 141, "16", "b", "middle", GOLD)

    # bottom: the 11-11 deck's tree, cells inside each circle
    by = 272
    clone_tree(s, by, "cells")

    # bottom right: what this proves
    rx = 820
    s.rect(rx, by, 1200 - rx, H - by, "on", "line2", r=12, sw=2)
    items = [(True, "三層分支在細胞裡真的有"), (True, "細胞和 bulk 同一批"),
             (False, "末端小分支沒驗證"), (False, "參考樹，不是真值")]
    for i, (ok, txt) in enumerate(items):
        y = by + 50 + i * 56
        mark(s, rx + 30, y - 6, ok)
        s.text(rx + 48, y, txt, "b", "start", "c4" if ok else "mut")
    s.rect(rx + 14, by + 270, 1200 - rx - 28, 70, "hl", None, r=10)
    s.text((rx + 1200) / 2, by + 300, "可當 bulk 重建的", "b", "middle")
    s.text((rx + 1200) / 2, by + 328, "驗證標準", "b", "middle")

    notes = ("這頁要看的是：單細胞證明樹上的三層分支真的存在。上排四步。"
             "第一步，119 顆單細胞，和 bulk 同一批，各自定序。"
             "第二步，每顆細胞查樹上每個分支的突變測到幾成。"
             "第三步，單細胞會漏測，所以和共同祖先測到的比例比：這個例子共同祖先 89%、綠色 91%，判帶；另一顆紫色 0%，判不帶。"
             "第四步，帶黃色的都帶紫色，帶紫色的都帶綠色，違反 0 顆。"
             "下面是結果：5 群，細胞落在其中 4 群。右下：末端小分支沒驗證，它是參考樹不是真值，但三層主結構可當驗證標準。"
             "接著看 HP 比例怎麼設。")
    write_page("ref-check", page("ref-check", "119 顆單細胞帶著樹上三層分支的突變，所以這棵樹可當驗證標準",
                                 s, notes=notes))
    return notes


def _hex(c):
    from slidekit import COLORS
    return COLORS.get(c, c)


if __name__ == "__main__":
    for f in (ref_tree, ref_check):
        n = f()
        print(f.__name__, "notes", len(n), "chars")
