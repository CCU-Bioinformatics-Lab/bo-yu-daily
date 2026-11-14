"""HG008 section: hg-plan (p8, the bulk-vs-reference plan) and hg-nist (p9, what the NIST list alone allows).

Sources (BRIEF R5): lab_report/2026-11-13_hg008_bulk_rebuild/README.md, nist_branch_cn.txt, plan_flow_icons.png
(make_flow_icons.py: icons redrawn here in a shorter form). Tree shape: lab_report/2026-11-07_hg008_tree_rebuild/
README.md 「目前的樹」; clone letters A-H from report/2026_11_11_slides/BRIEF.md (copied, not imported).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python3 -I drops the script dir
from slidekit import S, page, write_page, tag  # noqa: E402
from lib import width  # noqa: E402

H = 500


# ---- small pictograms (shared with gen_close.py, F-3) --------------------------------

def tube(s, x, top, w=18, h=42, label=None, cells=False):
    """A tube: a clone line, or the bulk sample when cells=True."""
    r = w / 2
    body = f"M{x - r:.1f} {top:.1f} L{x - r:.1f} {top + h - r:.1f} A{r:.1f} {r:.1f} 0 0 0 {x + r:.1f} {top + h - r:.1f} L{x + r:.1f} {top:.1f}"
    liquid = f"M{x - r:.1f} {top + h * .45:.1f} L{x - r:.1f} {top + h - r:.1f} A{r:.1f} {r:.1f} 0 0 0 {x + r:.1f} {top + h - r:.1f} L{x + r:.1f} {top + h * .45:.1f} Z"
    s.path(liquid, None, 0, "panel3" if not cells else "panel2")
    s.path(body, "ink2", 2)
    s.line(x - r - 3, top, x + r + 3, top, "ink2", 2.5)
    if cells:
        for dx, dy, c in [(-.25, .5, "c2"), (.2, .55, "c2"), (-.05, .68, "c1"), (.25, .75, "c3"), (-.25, .8, "c2"), (.05, .88, "c2")]:
            s.circle(x + dx * w, top + dy * h, w * .11, c)
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


def badge(s, x, y, n, r=15):
    """A numbered question marker: the same four numbers on hg-plan and decide."""
    s.circle(x, y, r, "stdis")
    s.text(x, y + 6, str(n), "s", "middle", "on")


def doc(s, x, y, w=56, h=70, star=True):
    c = w * .3
    s.poly([(x, y), (x + w - c, y), (x + w, y + c), (x + w, y + h), (x, y + h)], "on", "ink2", 2)
    s.poly([(x + w - c, y), (x + w - c, y + c), (x + w, y + c)], "line", "ink2", 1.5)
    for i in range(3):
        s.line(x + 9, y + c + 6 + i * 11, x + w - 12, y + c + 6 + i * 11, "line2", 2.5)
    if star:
        s.star(x + w - 4, y + h - 6, 13)


def reads_icon(s, cx, cy):
    """Reads tagged HP1 (blue) or HP2 (orange) across one SNV site (red dashed line)."""
    rows = [("hp1", -46, 0), ("hp1l", -34, 1), ("hp1", -52, 2), ("hp2", -40, 3), ("hp2l", -50, 4), ("hp2", -30, 5)]
    for c, off, i in rows:
        yy = cy - 42 + i * 14 + (8 if i >= 3 else 0)
        s.bar(cx + off, yy, 86, c, 9)
    s.line(cx + 2, cy - 52, cx + 2, cy + 44, "mut", 2, dash=True)


def counts_icon(s, cx, base):
    """ref/alt counts split by HP: hollow bar = ref, red bar = alt."""
    for k, c in enumerate(("hp1", "hp2")):
        x = cx - 50 + k * 56
        hr, ha = (52, 30) if k == 0 else (60, 0)
        s.rect(x, base - hr, 20, hr, "on", c, r=2, sw=2.5)
        if ha:
            s.rect(x + 22, base - ha, 20, ha, "mut", None, r=2)
        s.line(x - 4, base, x + 46, base, "ink2", 2)


def cn_icon(s, cx, cy):
    """1+1 (one HP1 + one HP2) kept, 2+1 dropped."""
    s.bar(cx - 74, cy - 14, 62, "hp1", 11)
    s.bar(cx - 74, cy + 4, 62, "hp2", 11)
    s.text(cx - 43, cy + 40, "1+1 ✓", "s", "middle", "c4")
    s.bar(cx + 14, cy - 23, 62, "hp1", 11)
    s.bar(cx + 14, cy - 8, 62, "hp1", 11)
    s.bar(cx + 14, cy + 7, 62, "hp2", 11)
    s.text(cx + 45, cy + 40, "2+1 ✗", "s", "middle", "mut")


def gear(s, x, y, r=17):
    s.circle(x, y, r, None, "ink2", 7, dash=True)
    s.circle(x, y, r * .6, "ink2")
    s.circle(x, y, r * .25, "on")


LAYER = {"all": "ink", "111": "c1", "48": "c2", "16": "c3"}


def mini_tree(s, cx, top, sc=1.0):
    """The reference tree reduced to its nested layers: all cells -> 111 -> 48 -> 16 (plus the one outgroup)."""
    d = 30 * sc
    root, out, n111, n48, n16 = (cx - 14 * sc, top), (cx - 44 * sc, top + d), (cx + 6 * sc, top + d), (cx + 26 * sc, top + 2 * d), (cx + 46 * sc, top + 3 * d)
    side = [(n111, (cx - 18 * sc, top + 2 * d)), (n48, (cx + 2 * sc, top + 3 * d))]
    for a, b in [(root, out), (root, n111), (n111, n48), (n48, n16)] + side:
        s.line(a[0], a[1], b[0], b[1], "ink2", 2.5)
    for (x, y), c in [(root, "ink"), (out, "unphased"), (n111, "c1"), (n48, "c2"), (n16, "c3")]:
        s.circle(x, y, 8 * sc, c)
    for (_, (x, y)) in side:
        s.circle(x, y, 6 * sc, "panel3")


def prop_bar(s, x, y, w, parts, h=22):
    """A stacked bar of cell fractions; parts = [(n, color)]."""
    tot = sum(n for n, _ in parts)
    cur = x
    for n, c in parts:
        ww = w * n / tot
        s.rect(cur, y, ww, h, c, None, r=0)
        cur += ww
    s.rect(x, y, w, h, None, "ink2", r=2, sw=1.5)


P23 = [(8, "unphased"), (63, "c1"), (32, "c2"), (16, "c3")]   # 119 cells: outside 111 / 111 only / 48 only / 16
QUESTIONS = [("SNV 從哪來？", "從 read 找"), ("HP 從哪來？", "read 標 HP"),
             ("只用 1+1 嗎？", "只用 1+1"), ("ONT 還是 PacBio？", "兩個都跑")]


# ---- p8 hg-plan --------------------------------------------------------------------------

def hg_plan():
    s = S("hg-plan", 1200, H)
    # top lane: bulk -> rebuilt tree
    s.rect(0, 0, 1200, 222, "panel", None, r=10)
    s.text(16, 30, "bulk 腫瘤 → 重建樹", "h")
    cw, gap, y0, ch = 180, 18, 44, 168
    cards = [("bulk 腫瘤", "ONT 或 PacBio", 4), ("SNV 名單", "哪些位置有突變", 1), ("read 標 HP", "用已定相 germline", 2),
             ("分 HP 計數", "ref／alt read 數", None), ("挑區域", "HP1、HP2 各一份", 3), ("重建樹", "加 HP／不加 HP", None)]
    for i, (lab, sub, q) in enumerate(cards):
        x = 12 + i * (cw + gap)
        cx = x + cw / 2
        s.rect(x, y0, cw, ch, "on", None, r=10)
        if q:
            badge(s, x + cw - 6, y0 + 6, q)
        if i == 0:
            tube(s, cx, y0 + 18, w=40, h=76, cells=True)
        elif i == 1:
            doc(s, cx - 30, y0 + 20)
        elif i == 2:
            reads_icon(s, cx, y0 + 62)
        elif i == 3:
            s.text(cx - 30, y0 + 30, "HP1", "s", "middle", "hp1")
            s.text(cx + 26, y0 + 30, "HP2", "s", "middle", "hp2")
            counts_icon(s, cx, y0 + 102)
        elif i == 4:
            cn_icon(s, cx, y0 + 46)
        else:
            gear(s, cx - 48, y0 + 54)
            s.arrow(cx - 24, y0 + 54, cx - 4, y0 + 54, c="ink2", sw=2.5, head=8)
            mini_tree(s, cx + 30, y0 + 22, .78)
        s.text(cx, y0 + 128, lab, "b", "middle")
        s.text(cx, y0 + 156, sub, "s", "middle", "ink2")
        if i < 5:
            s.arrow(x + cw + 2, y0 + 70, x + cw + gap - 2, y0 + 70, c="ink2", sw=2.5, head=8)

    # bottom left: the four questions with current leaning
    qx, qy, qw = 0, 240, 340
    s.rect(qx, qy, qw, H - qy, "panel", None, r=10)
    s.text(qx + 16, qy + 32, "四件事", "h")
    s.text(qx + qw - 14, qy + 32, "11-13 先定", "s", "end", "c4")
    for i, (q, lean) in enumerate(QUESTIONS):
        y = qy + 84 + i * 50
        badge(s, qx + 26, y - 7, i + 1)
        s.text(qx + 50, y, q, "t")
        s.text(qx + qw - 14, y, lean, "s", "end", "c4")

    # bottom middle: the reference (not truth)
    rx, rw = 360, 420
    s.rect(rx, qy, rw, H - qy, "panel2", None, r=10)
    s.text(rx + 16, qy + 32, "參考樹（不是真值）", "h")
    # row 1: 8 clone lines -> tree shape
    for k in range(8):
        tube(s, rx + 36 + k * 22, qy + 58, w=14, h=34)
    s.text(rx + 113, qy + 122, "8 株選殖株", "s", "middle")
    s.arrow(rx + 210, qy + 78, rx + 262, qy + 78, c="ink2", sw=2.5, head=8)
    mini_tree(s, rx + 330, qy + 52, .72)
    s.text(rx + 330, qy + 136, "樹形", "s", "middle")
    # row 2: 119 single cells -> fraction per branch
    pts = [(0, 0), (22, 6), (44, -4), (66, 8), (88, 0), (110, 6), (132, -2), (154, 4), (11, 22), (33, 26), (55, 20), (77, 28), (99, 22), (121, 26), (143, 20)]
    cols = ["c1", "c2", "c1", "unphased", "c1", "c3", "c2", "c1", "c2", "c1", "c3", "c1", "c2", "c1", "c1"]
    for (dx, dy), c in zip(pts, cols):
        s.cell(rx + 36 + dx, qy + 168 + dy, r=8, fill=c)
    s.text(rx + 113, qy + 226, "119 顆單細胞", "s", "middle")
    s.arrow(rx + 210, qy + 180, rx + 262, qy + 180, c="ink2", sw=2.5, head=8)
    prop_bar(s, rx + 272, qy + 168, 130, P23)
    s.text(rx + 337, qy + 226, "分支比例", "s", "middle")

    # bottom right: compare
    cx0, cwid = 800, 400
    s.rect(cx0, qy, cwid, H - qy, "panel", "c4", r=10, sw=2.5)
    s.text(cx0 + 16, qy + 32, "比對", "h")
    mini_tree(s, cx0 + 80, qy + 52, .72)
    s.text(cx0 + 80, qy + 136, "重建", "s", "middle")
    s.text(cx0 + 160, qy + 98, "⇄", "big", "middle", "ink2")
    mini_tree(s, cx0 + 240, qy + 52, .72)
    s.text(cx0 + 240, qy + 136, "參考樹", "s", "middle")
    s.text(cx0 + 300, qy + 98, "樹形對嗎？", "s", "start", "c4")
    s.text(cx0 + 16, qy + 182, "重建", "s")
    prop_bar(s, cx0 + 80, qy + 165, 200, [(10, "unphased"), (58, "c1"), (36, "c2"), (15, "c3")])
    tag(s, cx0 + 292, qy + 184, "示意", "demo")
    s.text(cx0 + 16, qy + 222, "單細胞", "s")
    prop_bar(s, cx0 + 80, qy + 205, 200, P23)
    s.text(cx0 + 292, qy + 222, "比例差多少？", "s", "start", "c4")
    # flows into the compare box
    s.arrow(12 + 5 * (cw + gap) + cw / 2, y0 + ch + 2, 12 + 5 * (cw + gap) + cw / 2, qy + 46, c="ink2", sw=3, head=11)
    s.arrow(rx + rw + 2, qy + 92, cx0 - 2, qy + 92, c="ink2", sw=3, head=11)
    s.arrow(rx + rw + 2, qy + 196, cx0 - 2, qy + 196, c="ink2", sw=3, head=11)

    notes = ("這頁要看的是：bulk 重建的樹和參考樹在右下角的比對會合。"
             "上排從左到右：bulk 腫瘤樣本、列出 SNV、用已定相的 germline 把 read 標成 HP1 或 HP2、分 HP 數 read、只留 HP1、HP2 各一份的區域，再各跑一次加 HP 和不加 HP。"
             "下排中間是參考樹，不是真值：8 株選殖株給樹形，119 顆單細胞給分支比例。比對看樹形和比例，重建那條是示意。"
             "左下四件事我在 11 月 13 日先定，好讓這週跑出結果：從 read 找 SNV，read 標 HP，只用 1+1，ONT 和 PacBio 都跑。")
    write_page("hg-plan", page("hg-plan", "HG008：bulk 重建和參考樹在比對步驟會合，四件事已先定", s, notes=notes))
    return notes


# ---- p9 hg-nist --------------------------------------------------------------------------

LEAVES = "HGABEFCD"


def hg_nist():
    s = S("hg-nist", 1200, H)
    TH = 392
    s.rect(0, 0, 660, TH, "panel", None, r=10)
    s.text(16, 30, "參考樹：NIST 名單抓到幾個", "h")
    tag(s, 330, 30, "實際結果", "real")
    X = {k: 56 + i * 64 for i, k in enumerate(LEAVES)}
    yR, y7, y6, y4, y2, leaf = 70, 132, 190, 250, 300, 318
    xAB, xEF, xCD = (X["A"] + X["B"]) / 2, (X["E"] + X["F"]) / 2, (X["C"] + X["D"]) / 2
    xCDEF = (xEF + xCD) / 2
    x6 = (xAB + xCDEF) / 2
    x7 = (X["G"] + x6) / 2
    xR = (X["H"] + x7) / 2
    for a, b, y in [(X["H"], x7, yR), (X["G"], x6, y7), (xAB, xCDEF, y6), (X["A"], X["B"], y4),
                    (xEF, xCD, y4), (X["E"], X["F"], y2), (X["C"], X["D"], y2)]:
        s.line(a, y, b, y, "ink2", 2.5)
    s.line(xR, yR - 18, xR, yR, "ink2", 2.5)
    branch(s, x7, yR, x7, y7, "solid", c="c1")
    branch(s, x6, y7, x6, y6, "dash")
    branch(s, xAB, y6, xAB, y4, "half")
    branch(s, xCDEF, y6, xCDEF, y4, "solid", c="c2")
    branch(s, xCD, y4, xCD, y2, "solid", c="c3")
    branch(s, xEF, y4, xEF, y2, "dash")
    for k, y0 in [("H", yR), ("G", y7), ("A", y4), ("B", y4), ("E", y2), ("F", y2), ("C", y2), ("D", y2)]:
        branch(s, X[k], y0, X[k], leaf, "dash")
        tube(s, X[k], leaf, w=16, h=30, label=k)

    def num(x, y, n, tot, a="start"):
        """NIST count (green if any, red if none) over the clone-SNV count."""
        t1, t2 = f"{n}", f"／{tot}"
        w1, w2 = width(t1, 20), width(t2, 18)
        x0 = x if a == "start" else x - w1 - w2
        s.text(x0, y, t1, "b", "start", "c4" if n else "mut")
        s.text(x0 + w1, y, t2, "s", "start", "ink2")
    num(x7 + 10, (yR + y7) / 2 + 7, 126, 127)
    num(x6 + 10, (y7 + y6) / 2 + 7, 4, 4)
    num(xAB - 10, (y6 + y4) / 2 + 7, 2, 31, "end")
    num(xCDEF + 10, (y6 + y4) / 2 + 7, 0, 14)
    num(xEF - 10, (y4 + y2) / 2 + 3, 0, 17, "end")
    num(xCD + 10, (y4 + y2) / 2 + 3, 0, 68)
    s.text(650, 340, "末端 0／3,593", "s", "end", "mut")
    # legend
    lx, ly = 430, 60
    s.text(lx, ly, "NIST 名單", "b", "start", "c4")
    s.text(lx + width("NIST 名單", 20), ly, "／選殖株 SNV", "s", "start", "ink2")
    for k, (st, lab) in enumerate([("solid", "單細胞支持"), ("half", "部分支持"), ("dash", "未驗證")]):
        yy = ly + 34 + k * 28
        branch(s, lx, yy - 6, lx + 36, yy - 6, st, sw=4)
        s.text(lx + 46, yy, lab, "s")

    # right: cell fraction per layer, and what an assembly sees
    px = 680
    s.rect(px, 0, 520, TH, "panel", None, r=10)
    s.text(px + 16, 30, "每層的細胞比例", "h")
    ax0, ax1 = px + 190, px + 490

    def X01(v):
        return ax0 + (ax1 - ax0) * v
    # shaded zone: what a tumor assembly represents (inference)
    s.rect(X01(.86), 52, X01(1.0) - X01(.86) + 10, 268, "hl", None, r=6)
    s.text(X01(.86) - 6, 76, "組裝只代表多數細胞", "s", "end", "stdis")
    tag(s, X01(.86) - 66, 106, "推論", "infer")
    s.text(px + 16, 136, "細胞", "s", "start", "ink2")
    s.text(px + 120, 136, "NIST", "s", "middle", "ink2")
    rows = [("全部", "all", 1.0, True), ("111 顆", "111", 111 / 119, True), ("48 顆", "48", 48 / 119, False), ("16 顆", "16", 16 / 119, False)]
    for i, (lab, key, v, ok) in enumerate(rows):
        y = 170 + i * 42
        s.circle(px + 24, y - 7, 8, LAYER[key])
        s.text(px + 38, y, lab, "t")
        if ok:
            s.path(f"M{px + 110} {y - 7} L{px + 117} {y} L{px + 131} {y - 15}", "c4", 3.5)
        else:
            s.xmark(px + 120, y - 7, 7, "mut", 3)
        s.line(ax0, y - 7, X01(v), y - 7, LAYER[key], 4)
        s.circle(X01(v), y - 7, 9, LAYER[key])
        if v < .9:
            s.text(X01(v) + 16, y, f"{v:.2f}", "s", "start", "ink")
        else:
            s.text(X01(v) - 14, y - 16, "1.0" if v == 1 else f"{v:.2f}", "s", "end", "ink")
    s.line(ax0, 340, ax1, 340, "ink2", 2)
    for v in (0, .5, 1):
        s.line(X01(v), 334, X01(v), 346, "ink2", 2)
        s.text(X01(v), 370, f"{v:g}", "s", "middle", "ink2")
    s.text(px + 16, 370, "細胞比例", "s", "start", "ink2")

    # bottom: what this shows / does not show / next
    by = 408
    boxes = [(0, 400, True, "能證明", "NIST 名單只到 111 顆那層"),
             (412, 400, False, "不能證明", "48、16 顆那兩層真的沒有 SNV"),
             (824, 376, None, "下一步", "從 read 直接找 SNV（下一頁）")]
    for x, w, ok, head, body in boxes:
        s.rect(x, by, w, H - by, "on", "c4" if ok else ("mut" if ok is False else "ink2"), r=10, sw=2)
        if ok:
            s.path(f"M{x + 18} {by + 32} L{x + 26} {by + 40} L{x + 42} {by + 22}", "c4", 4)
        elif ok is False:
            s.xmark(x + 30, by + 31, 9, "mut", 3.5)
        else:
            s.arrow(x + 16, by + 31, x + 44, by + 31, c="ink2", sw=3, head=10)
        s.text(x + 54, by + 38, head, "b", "start", "c4" if ok else ("mut" if ok is False else "ink"))
        s.text(x + 18, by + 76, body, "t")

    notes = ("這頁要看的是：只用 NIST 名單，就沒有深層分支可比。"
             "左邊參考樹每支標兩個數字：NIST 名單有幾個，斜線後是選殖株找到幾個。"
             "綠色那支 127 個裡有 126 個；往下紫色、黃色兩層一個都沒有，末端也是 0。"
             "右邊是細胞比例：111 顆那層約 0.93，和全部的 1.0 很難分開；48 顆、16 顆兩層名單裡沒有。"
             "我們推論名單來自腫瘤組裝，組裝只代表多數細胞。"
             "所以能證明名單只到 111 顆那層，不能證明深層沒有 SNV。所以改從 read 直接找，下一頁看結果。")
    write_page("hg-nist", page("hg-nist", "只用 NIST 名單比不到深層分支，所以改從 read 找 SNV", s, notes=notes))
    return notes


if __name__ == "__main__":
    hg_plan()
    hg_nist()
