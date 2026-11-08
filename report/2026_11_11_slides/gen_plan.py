"""Section 交付 3 (方案與選擇理由): p4 ratio-flow, p5 hypotheses, p6 options, p7 t2-data.

Sketches: sketches/plan.md. Sources: parental_snv_2026-11-07/summary.md (p4-p6),
notes/10_SNV_COORDINATES.md (p6), independent_evidence_2026-11-06/summary.md (p7).
"""
import math

from slidekit import S, page, write_page, n3_ladder, tag
import lib  # noqa: E402  (slidekit puts the site folder on sys.path)
from gen_res2 import tube as res_tube

W = lib.width


# ---- small pictograms ------------------------------------------------------------

def pill(s, cx, y, text, col="ink2", filled=False, cls="s"):
    """A rounded label centered at cx; y is the text baseline."""
    w = W(text, lib.SIZES[cls]) + 22
    s.rect(cx - w / 2, y - 21, w, 29, col if filled else "paper", col, r=14, sw=2)
    s.text(cx, y, text, cls, "middle", "on" if filled else col)
    return w


def tick(s, x, y, c="stok"):
    s.path(f"M{x - 8} {y} L{x - 2} {y + 6} L{x + 9} {y - 7}", c, 3.5)


def ok_line(s, x, y, good, text, cls="t"):
    """✓ or ✗ followed by a short phrase (F-5: result is a mark plus words)."""
    if good:
        tick(s, x + 8, y - 6)
    else:
        s.xmark(x + 8, y - 6, 7, "mut", 3)
    s.text(x + 26, y, text, cls)


def stars_on(s, y, xs, r=7):
    for x in xs:
        s.star(x, y, r)


def ghost(s, x, y, w, c="hp2", h=12, mark=True):
    """A copy that is gone: dashed outline, with a cross at its end."""
    s.bar(x, y, w, c, h, dash=True)
    if mark:
        s.xmark(x + w + 14, y, 6, "mut", 2.5)


def tube(s, x, y, h=30):
    """One test tube = one isolated cell line (選殖株): the same tube as p3 and p11, small."""
    res_tube(s, x, y, w=10, h=h)


def sc(s, x, y, r=4.5):
    """One single cell: small grey-edged circle (single cells are independent short read data)."""
    s.circle(x, y, r, "normal", "line2", 1.3)


def parent(s, x, y, label, h=50, cross=False):
    """Parent-of-origin icon: a grey person with 「爸」 or 「媽」 under it. Parents never get a color."""
    s.person(x, y, h, "panel3")
    s.text(x, y + h + 22, label, "b", "middle")
    if cross:
        s.xmark(x, y + h * .55, 13, "mut", 3)


def gear(s, cx, cy, ro=34, ri=26, n=8):
    pts = []
    for i in range(n * 4):
        a = 2 * math.pi * i / (n * 4)
        r = ro if (i % 4) in (1, 2) else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    s.poly(pts, "panel3")
    s.circle(cx, cy, 10, "paper")


def frame(s, x, y, w, h, fill="panel", stroke=None, sw=1.5, r=12):
    s.rect(x, y, w, h, fill, stroke, r=r, sw=sw)


# ---- p4 ratio-flow ---------------------------------------------------------------

def p4():
    s = S("ratio-flow", 1200, 466)
    for x0, x1 in [(20, 370), (410, 790), (830, 1180)]:
        frame(s, x0, 10, x1 - x0, 392)
    tag(s, 1100, 44, "示意", "demo")

    # ① where each mutation landed
    s.text(195, 46, "① 突變落在哪條", "h", "middle")
    s.rect(225, 114, 125, 128, "hl", r=6)
    s.text(287, 102, "之後 LOH 的一段", "s", "middle")
    s.text(32, 154, "HP1", "b", color="hp1")
    s.text(32, 212, "HP2", "b", color="hp2")
    s.bar(80, 148, 270, "hp1", 16)
    s.bar(80, 206, 270, "hp2", 16)
    stars_on(s, 148, [112, 175, 255, 320], 9)
    stars_on(s, 206, [140, 200, 245, 300], 9)
    s.text(195, 286, "兩條大致各半", "t", "middle")
    s.text(195, 332, "4 : 4", "big", "middle")
    s.text(195, 368, "（兩條上的 SNV 數）", "s", "middle")

    s.arrow(373, 220, 407, 220, "LOH", sw=3)

    # ② the segment becomes LOH: one version left, 1, 2 or more copies
    s.text(600, 46, "② 這段變成 LOH", "h", "middle")
    s.text(600, 74, "兩種版本只剩一種", "s", "middle")
    bx, bw, sx = 610, 140, [640, 705]
    rows = [("刪除", "剩 1 份", 1, 120), ("copy-neutral", "仍是 2 份", 2, 212), ("擴增", "3 份或更多", 3, 310)]
    for name, cn, k, y0 in rows:
        s.text(428, y0 + 6, name, "b")
        s.text(428, y0 + 30, cn, "s")
        for j in range(k):
            yy = y0 - (k - 1) * 10 + j * 20
            s.bar(bx, yy, bw, "hp1", 14)
            stars_on(s, yy, sx, 8)
        ghost(s, bx, y0 - (k - 1) * 10 + k * 20, bw, h=14)
    s.line(424, 166, 776, 166, "line", 1.5)
    s.line(424, 264, 776, 264, "line", 1.5)
    s.text(600, 390, "藍條上的突變跟著每一份複製；橘條的消失", "s", "middle")

    s.arrow(793, 220, 827, 220, sw=3)

    # ③ what bulk sequencing shows
    s.text(990, 46, "③ 我們看到的", "h", "middle")
    s.text(1005, 76, "數兩條上的 SNV", "s", "middle")
    s.text(846, 146, "HP1", "b", color="hp1")
    s.text(846, 206, "HP2", "b", color="hp2")
    for k in range(4):
        x = 902 + k * 66
        s.rect(x, 128, 56, 22, "hp1l", r=5)
        s.star(x + 28, 139, 8)
        if k < 2:
            s.rect(x, 188, 56, 22, "hp2l", r=5)
            s.star(x + 28, 199, 8)
        else:
            s.rect(x, 188, 56, 22, None, "hp2", r=5, dash=True)
    s.text(1005, 278, "4 : 2", "big", "middle")
    s.text(1005, 314, "看起來偏向 HP1", "t", "middle")
    s.text(1005, 346, "當初其實是 4 : 4", "s", "middle")
    s.text(1005, 376, "三種份數都看到 4 : 2", "s", "middle")

    # first stage
    s.rect(20, 412, 350, 48, None, "c4", r=10, sw=3)
    s.text(195, 443, "第一階段只模擬 ①", "b", "middle", "c4")
    s.rect(410, 412, 380, 48, "panel2", r=10)
    s.text(600, 443, "② 留到拷貝數階段", "b", "middle", "mute")

    notes = ("這頁要看的是，我們在資料裡看到的 HP 比例，其實是兩件事疊在一起。"
             "左邊第一格，突變當初落在 HP1 或 HP2，大致各半，這個例子是 4 比 4。"
             "中間第二格，黃色那一段後來變成 LOH，也就是兩種版本只剩一種；份數可能剩 1 份、仍是 2 份，或擴增到 3 份以上。"
             "藍條上原本的突變跟著每一份複製，橘條上的突變就消失了。"
             "右邊第三格，我們數兩條上的 SNV，三種情況都變成 4 比 2，看起來偏向 HP1，但當初其實是 4 比 4。"
             "所以第一階段只模擬第一格，第二格留到拷貝數階段。圖上的星星和份數都是示意。")
    write_page("ratio-flow", page("ratio-flow", "我們看到的 HP 比例＝突變當初落在哪條＋之後的拷貝數改變", s, "", notes))


# ---- p5 hypotheses ---------------------------------------------------------------

def card(s, x, y, w, h, name, stamp, grey=False, stamp_col="ink2"):
    s.rect(x, y, w, h, "panel2" if grey else "paper", "line2", r=10, sw=1.5)
    s.text(x + w / 2, y + 30, name, "b", "middle", "mute" if grey else None)
    pill(s, x + w / 2, y + h - 16, stamp, stamp_col)
    return x + w / 2, (y + 42 + y + h - 40) / 2


def p5():
    s = S("hypotheses", 1200, 470)
    frame(s, 10, 10, 762, 452, "paper", "line2", 2)
    frame(s, 790, 10, 400, 452, "paper", "line2", 2)
    s.text(30, 44, "SNV 階段", "h")
    s.text(810, 44, "拷貝數階段", "h")
    pill(s, 1000, 44, "下一階段", "mute")
    s.text(30, 74, "有資料", "b", color="c4")
    s.text(810, 74, "改變的是看到幾個", "s")

    cw, ch1, ch2 = 176, 180, 176
    xs = [20 + i * (cw + 12) for i in range(4)]
    y1, y2 = 82, 276
    s.text(xs[3] + cw / 2, y2 + 90, "只限致癌突變", "b", "middle", "mute")
    s.text(xs[3] + cw / 2, y2 + 118, "或證據不足", "b", "middle", "mute")

    # balanced: half and half
    cx, cy = card(s, xs[0], y1, cw, ch1, "兩條各半", "兩株沒有否定", stamp_col="c4")
    s.text(cx, y1 + ch1 - 42, "COLO829、HG008", "s", "middle")
    cy -= 10
    s.poly([(cx, cy - 14), (cx - 16, cy + 34), (cx + 16, cy + 34)], "panel3")
    s.line(cx - 62, cy - 14, cx + 62, cy - 14, "ink2", 3)
    for side, c in [(-1, "hp1"), (1, "hp2")]:
        ex = cx + side * 58
        s.line(ex, cy - 14, ex - 22, cy + 14, "line2", 1.5)
        s.line(ex, cy - 14, ex + 22, cy + 14, "line2", 1.5)
        s.bar(ex - 26, cy + 16, 52, c, 10)
        s.star(ex - 11, cy + 6, 7)
        s.star(ex + 11, cy + 6, 7)

    # independence, except very close pairs
    cx, cy = card(s, xs[1], y1, cw, ch1, "相鄰 SNV 獨立", "<1 kb 內例外", stamp_col="c4")
    s.bar(cx - 70, cy - 2, 140, "hp1", 12)
    s.bar(cx - 70, cy + 26, 140, "hp2", 12)
    stars_on(s, cy - 2, [cx - 50, cx + 18, cx + 30])
    stars_on(s, cy + 26, [cx - 20, cx + 52])
    s.text(cx + 24, cy - 18, "<1 kb", "s", "middle")

    # parents differ?
    cx, cy = card(s, xs[2], y1, cw, ch1, "爸媽本身不同", "沒測到差異", stamp_col="c4")
    parent(s, cx - 42, cy - 40, "爸", 46)
    parent(s, cx + 42, cy - 40, "媽", 46)
    s.text(cx, cy - 2, "？", "h", "middle")

    # Xi has more mutations
    cx, cy = card(s, xs[3], y1, cw, ch1, "失活的 X 較多", "共識，只在 chrX", stamp_col="c4")
    s.text(cx - 78, cy + 2, "Xa", "s")
    s.text(cx - 78, cy + 32, "Xi", "s")
    s.bar(cx - 50, cy - 4, 124, "panel3", 12)
    s.bar(cx - 50, cy + 26, 124, "ink2", 12)
    stars_on(s, cy - 4, [cx - 20, cx + 40])
    stars_on(s, cy + 26, [cx - 34, cx - 4, cx + 26, cx + 54])

    # grey row
    cx, cy = card(s, xs[0], y2, cw, ch2, "兩次打擊分兩條", "只限致癌突變", grey=True)
    s.rect(cx - 2, cy - 22, 34, 58, None, "ink", r=4, sw=2)
    s.bar(cx - 70, cy - 4, 140, "hp1", 12)
    s.bar(cx - 70, cy + 20, 140, "hp2", 12)
    s.star(cx + 15, cy - 4, 7)
    s.star(cx + 15, cy + 20, 7)

    cx, cy = card(s, xs[1], y2, cw, ch2, "複製時間不同", "證據不足", grey=True)
    s.bar(cx - 76, cy - 4, 100, "hp1", 12)
    s.bar(cx - 76, cy + 20, 100, "hp2", 12)
    s.circle(cx + 52, cy + 8, 22, "paper", "ink2", 2)
    s.line(cx + 52, cy + 8, cx + 52, cy - 6, "ink2", 2.5)
    s.line(cx + 52, cy + 8, cx + 62, cy + 14, "ink2", 2.5)

    cx, cy = card(s, xs[2], y2, cw, ch2, "germline 影響", "證據不足", grey=True)
    s.bar(cx - 70, cy + 14, 140, "hp1", 12)
    s.circle(cx - 30, cy + 14, 6, "ink")
    s.star(cx + 34, cy + 14, 8)
    s.path(f"M{cx - 28} {cy + 2} Q{cx + 2} {cy - 26} {cx + 30} {cy + 1}", "ink2", 2)
    s.poly([(cx + 33, cy + 4), (cx + 24, cy - 2), (cx + 34, cy - 7)], "ink2")

    # copy number stage
    rx = [800, 996]
    rw = 184
    cx, cy = card(s, rx[0], y1, rw, ch1, "LOH 改寫比例", "確定", stamp_col="c4")
    for j in range(2):
        s.bar(cx - 66, cy - 14 + j * 18, 120, "hp1", 11)
        stars_on(s, cy - 14 + j * 18, [cx - 36, cx + 20], 6)
    ghost(s, cx - 66, cy + 22, 120, h=11)

    cx, cy = card(s, rx[1], y1, rw, ch1, "平行事件", "確定", stamp_col="c4")
    root, a, b = (cx, cy - 30), (cx - 44, cy + 2), (cx + 44, cy + 2)
    s.line(*root, *a, "line2", 2.5)
    s.line(*root, *b, "line2", 2.5)
    s.circle(*root, 9, "normal", "cellline")
    s.circle(*a, 11, "c1", "cellline")
    s.circle(*b, 11, "c2", "cellline")
    s.bar(a[0] - 26, cy + 24, 52, "hp2", 8)
    s.bar(a[0] - 26, cy + 36, 52, "hp1", 8, dash=True)
    s.bar(b[0] - 26, cy + 24, 52, "hp1", 8)
    s.bar(b[0] - 26, cy + 36, 52, "hp2", 8, dash=True)

    cx, cy = card(s, rx[0], y2, rw, ch2, "印記：只表現一親", "局部、部分爭議")
    parent(s, cx - 40, cy - 34, "爸", 40)
    parent(s, cx + 40, cy - 34, "媽", 40, cross=True)

    cx, cy = card(s, rx[1], y2, rw, ch2, "致癌突變那條擴增", "只限致癌突變")
    for j in range(2):
        yy = cy - 14 + j * 18
        s.bar(cx - 66, yy, 120, "hp1", 11)
        s.star(cx - 6, yy, 6)
    s.rect(cx - 20, cy - 24, 28, 46, None, "ink", r=4, sw=2)
    s.bar(cx - 66, cy + 26, 120, "hp2", 11)

    notes = ("這頁把假說分成兩堆。左邊是 SNV 階段，一共七個。上面四個有資料：兩條各半，COLO829、HG008 兩株都沒有否定；"
             "相鄰 SNV 彼此獨立，只有 1 kb 內是例外；爸媽本身不同，目前沒測到差異；"
             "失活的 X，圖上的 Xi，突變比較多，這是共識，但只在 chrX。"
             "下面三張灰卡，兩次打擊分兩條只限致癌突變，複製時間和 germline 影響證據不足。"
             "右邊是拷貝數階段：LOH、平行事件、只表現一親的印記區、致癌突變那條擴增，"
             "它們改變的是我們看到幾個，所以留到下一階段。")
    write_page("hypotheses", page("hypotheses", "SNV 階段有 7 個假說，4 個有資料；其餘屬拷貝數階段", s, "", notes))


# ---- p6 options ------------------------------------------------------------------

OPT_HEADS = ["A　維持獨立 50%", "B　加座標、近距離成簇", "C　真值多記一欄親源"]
OPT_RULES = ["各半、彼此獨立", "少數 SNV 成簇落在同一條", "多一欄：每條是爸或媽"]


def option_pic(s, i, x, y):
    """The A / B / C pictogram (p6 and p16 draw it with this one function, F-4).

    x = left edge of a 380-wide card, y = the HP1 bar; the picture spans y - 34 .. y + 72.
    """
    star1 = [[100, 165, 250, 315], [90, 196, 208, 220, 310], [100, 160, 215, 265]]
    star2 = [[130, 210, 285], [140, 265], [130, 195, 250]]
    bar_end = 290 if i == 2 else 345
    s.text(x + 18, y + 6, "HP1", "s", color="hp1")
    s.text(x + 18, y + 46, "HP2", "s", color="hp2")
    s.bar(x + 62, y, bar_end - 62, "hp1", 14)
    s.bar(x + 62, y + 40, bar_end - 62, "hp2", 14)
    stars_on(s, y, [x + v for v in star1[i]], 7.5)
    stars_on(s, y + 40, [x + v for v in star2[i]], 7.5)
    if i == 1:
        s.text(x + 208, y - 19, "<1 kb", "s", "middle")
    if i == 2:
        parent(s, x + 318, y - 19, "", 30)
        parent(s, x + 318, y + 21, "", 30)
        s.text(x + 340, y + 9, "爸", "b")
        s.text(x + 340, y + 49, "媽", "b")


def src_tag(s, x, y, a="start"):
    s.text(x, y, "〔程式〕", "s", a, "mute")


def p6():
    s = S("options", 1200, 470)
    cols = [10, 410, 810]
    cw = 380
    for x in cols:
        frame(s, x, 30, cw, 300, "paper", "line2", 1.5)
    s.rect(3, 20, 394, 318, None, "ink", r=16, sw=4)
    pill(s, 200, 26, "目前傾向，還沒決定", "ink", filled=True)

    pros = [[(True, "和 COLO829、HG008 兩株一致"), (False, "缺近距離成簇")],
            [(True, "更接近真實"), (False, "要大改程式")],
            [(True, "之後的印記區用得到"), (False, "SNV 階段沒新資訊")]]
    for i, x in enumerate(cols):
        s.text(x + cw / 2, 66, OPT_HEADS[i], "h", "middle")
        option_pic(s, i, x, 111)
        s.text(x + cw / 2, 194, OPT_RULES[i], "t", "middle")
        for k, (good, txt) in enumerate(pros[i]):
            ok_line(s, x + 22, 232 + k * 30, good, txt, "t")
        tag(s, x + cw - 80, 318, "示意", "demo")
    s.text(32, 318, "50% 有實測支持，不是直接設", "s", "start", "c4")

    # bottom strip
    for x0, x1 in [(10, 390), (400, 790), (800, 1190)]:
        frame(s, x0, 344, x1 - x0, 124, "panel")
    s.text(22, 372, "現有模擬器：隨機選一份 copy", "b")
    src_tag(s, 384, 372, "end")
    for j, c in enumerate(["hp1", "hp2"]):
        s.bar(34, 404 + j * 18, 70, c, 11)
    s.text(116, 420, "＝ 50%", "t")
    for j, c in enumerate(["hp1", "hp1", "hp2"]):
        s.bar(214, 396 + j * 16, 70, c, 11)
    s.text(296, 420, "≠ 50%", "t")
    s.text(200, 458, "只在兩條份數相同時等於 50%", "s", "middle")

    s.text(412, 372, "模擬時會用座標的工具", "b")
    src_tag(s, 780, 372, "end")
    for cx, y, name in [(500, 410, "SISTEM"), (672, 410, "HeteroGenesis"), (500, 452, "SMC-Het"), (672, 452, "TNSim")]:
        pill(s, cx, y, name, "ink2")

    s.text(816, 384, "diplosim", "b")
    src_tag(s, 812, 408)
    for x, cn in [(930, "2"), (975, "3"), (1020, "1")]:
        s.star(x, 374, 8)
        s.text(x, 402, cn, "n", "middle")
    s.text(1050, 378, "各自定拷貝數", "s")
    s.text(1050, 402, "不需要座標", "s")
    s.line(812, 416, 1178, 416, "line2", 1)
    s.text(816, 446, "真實資料", "b")
    s.rect(915, 426, 60, 14, "panel3", r=7)
    s.rect(975, 426, 60, 14, "ink2", r=7)
    s.star(940, 433, 7)
    s.star(1002, 433, 7)
    s.text(945, 461, "2", "n", "middle")
    s.text(1005, 461, "3", "n", "middle")
    s.text(1050, 436, "靠座標對到", "s")
    s.text(1050, 460, "拷貝數片段", "s")

    notes = ("這頁是模擬器的三個方案，目前傾向 A，用黑框標出來，還沒決定；三張圖都是示意。"
             "A 維持每個 SNV 獨立、兩條各半，和 COLO829、HG008 兩株一致；這次的 50% 有實測支持，不是直接設的。缺點是沒有近距離成簇。"
             "B 加座標，讓少數 SNV 在 1 kb 內成簇落在同一條，更接近真實，但要大改程式。C 多記一欄爸或媽，SNV 階段沒新資訊。"
             "下面左邊，現有模擬器隨機選一份 copy，只在兩條份數相同時是 50%。中間四個工具，模擬時會用座標。"
             "右邊，diplosim 各自定拷貝數，不需要座標；真實資料要靠座標對到拷貝數片段。")
    write_page("options", page("options", "模擬器的三個方案，目前傾向維持獨立 50%（根據見結果段）", s, "", notes))


# ---- p7 t2-data ------------------------------------------------------------------

def p7():
    s = S("t2-data", 1200, 468)
    names = ["模擬內部檢查", "真實 bulk 統計", "單細胞／克隆分群"]
    lits = [(0,), (0,), (0, 1)]
    for i in range(3):
        x0 = 10 + i * 397
        chosen = i == 2
        frame(s, x0, 22, 383, 156, "paper", "ink" if chosen else "line2", 4 if chosen else 1.5)
        gx, gy = x0 + 92, 92
        if i == 0:
            gear(s, gx, gy)
        elif i == 1:
            for k in range(7):
                y = gy - 34 + k * 10
                xo = ((k * 17) % 21) - 10
                s.rect(gx - 52 + xo, y, 104, 6, "read", r=3)
                if k in (1, 3, 5):
                    s.star(gx + 6, y + 3, 4.5)
        else:
            for dx, dy, f in [(-46, -10, "c1"), (-30, 12, "c1"), (-52, 18, "c1"), (30, -12, "c2"), (48, 8, "c2"), (26, 16, "c2")]:
                s.cell(gx + dx, gy + dy, 11, f)
            s.path(f"M{gx - 72} {gy + 4} a 34 30 0 1 0 68 0 a 34 30 0 1 0 -68 0", "line2", 1.5, dash=True)
            s.path(f"M{gx + 4} {gy + 2} a 34 30 0 1 0 68 0 a 34 30 0 1 0 -68 0", "line2", 1.5, dash=True)
        s.text(gx, 162, names[i], "b", "middle")
        n3_ladder(s, x0 + 218, 132, lits[i])
    pill(s, 10 + 2 * 397 + 92, 30, "本週選這條", "ink", filled=True)

    # requirement table
    c1, c2, c3, c4 = 20, 480, 720, 1020
    s.text(c1, 214, "候選資料", "b")
    s.text(c2, 214, "long read", "b", "middle")
    s.text(c3, 214, "獨立量測克隆結構", "b", "middle")
    s.text(c4, 214, "✓／✗ 只看需求表", "s", "middle")
    rows = [224, 304, 384]
    for k, y in enumerate(rows):
        s.rect(10, y, 1180, 76, "panel" if k % 2 == 0 else "paper", r=8)

    # HG008
    y = rows[0]
    s.text(c1, y + 30, "HG008", "b")
    for k in range(8):
        tube(s, 110 + k * 15, y + 8, 28)
    for k in range(16):
        sc(s, 232 + (k % 8) * 13, y + 16 + (k // 8) * 13)
    s.text(c1, y + 58, "8 株選殖株＋119 顆單細胞", "s")
    ok_line(s, c2 - 90, y + 30, True, "PacBio Revio", "s")
    s.text(c2 - 64, y + 56, "單細胞：例外", "s")
    ok_line(s, c3 - 80, y + 42, True, "多株＋單細胞", "s")
    pill(s, c4, y + 32, "多株＝上限參考", "ink2")
    s.text(c4, y + 60, "不等於單一 bulk", "s", "middle")

    # HCC1395
    y = rows[1]
    s.text(c1, y + 30, "HCC1395／SEQC2", "b")
    tube(s, 40, y + 38, 24)
    s.arrow(54, y + 50, 92, y + 50, sw=2, head=7)
    s.line(124, y + 38, 108, y + 60, "line2", 2, dash=True)
    s.line(124, y + 38, 140, y + 60, "line2", 2, dash=True)
    for p in [(124, y + 38), (108, y + 60), (140, y + 60)]:
        s.circle(*p, 5, "panel3")
    ok_line(s, c2 - 90, y + 42, False, "主要 short read", "s")
    ok_line(s, c3 - 92, y + 30, False, "樹由 bulk 推論", "s")
    s.text(c3 - 66, y + 56, "單細胞只有拷貝數", "s")
    s.text(c4, y + 30, "五個克隆群：已找到出處", "s", "middle")
    s.text(c4, y + 58, "六個：沒對上", "s", "middle")

    # COLO829
    y = rows[2]
    s.text(c1, y + 30, "COLO829", "b")
    tube(s, 40, y + 38, 24)
    s.text(60, y + 58, "一份 bulk", "s")
    ok_line(s, c2 - 90, y + 42, True, "long read bulk", "s")
    ok_line(s, c3 - 80, y + 42, False, "只有一份 bulk", "s")

    notes = ("這頁回答能用什麼驗證。上面三條路徑，模擬內部檢查和真實 bulk 統計都只支持到觀測特徵；"
             "單細胞或克隆分群能支持到克隆結構，本週選第三條。"
             "下面三個候選資料，勾叉只看需求表。HG008 有 PacBio 的 8 株選殖株和 119 顆單細胞，單細胞屬於例外；"
             "多株只是上限參考。HCC1395 主要是 short read，樹由 bulk 推論，單細胞只有拷貝數；"
             "上次的五個克隆群已找到出處，六個沒有對上。"
             "COLO829 是 long read，但只有一份 bulk。"
             "接下來看結果，先回到任務一，下一頁是 8 株的全部 SNV 怎麼分在兩條。")
    write_page("t2-data", page("t2-data", "能驗證克隆結構的只有 HG008：long read 多株＋獨立單細胞", s, "", notes))


if __name__ == "__main__":
    p4()
    p5()
    p6()
    p7()
