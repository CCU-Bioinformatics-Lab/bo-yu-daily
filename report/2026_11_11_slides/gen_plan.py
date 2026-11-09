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


def split_bar(s, x, y, w, frac, left, right, h=22):
    """Paternal | maternal share as a grey two-part bar (parents never get a color, F-4)."""
    s.rect(x, y, w * frac, h, "panel3", r=0)
    s.rect(x + w * frac, y, w * (1 - frac), h, "line2", r=0)
    s.line(x + w / 2, y - 5, x + w / 2, y + h + 5, "ink", 2, dash=True)
    s.text(x + 6, y + 17, left, "s", "start", "ink")
    s.text(x + w - 6, y + 17, right, "s", "end", "on")


def p5():
    # 2026-11-08 redesign (user): evidence from papers, not our own statistics. Sources: research/literature/papers/P01-P11
    # and the tumor_evolution_history survey cards E4-26 (Lefèbvre), E4-04 (Jäger), E4-02 (Nik-Zainal), E4-20 (Bergstrom).
    s = S("hypotheses", 1200, 470)
    frame(s, 10, 10, 580, 380, "paper", "c4", 2.5)
    frame(s, 610, 10, 580, 380, "paper", "line2", 2)
    s.text(30, 46, "兩條大致各半", "h", color="c4")
    s.text(610 + 20, 46, "只在這些情境偏一條", "h")

    # left: three evidence rows, each a paternal/maternal split bar
    rows = [
        ("腫瘤 21 人：父母差異 ≤ 5%", "Lefèbvre 2026（預印本，short read）", 0.5, "父", "母"),
        ("家族：受精後突變 52% 在父源", "Sasani 2019（eLife，249／475）", 249 / 475, "父 52%", "母 48%"),
        ("long read 家族：父：母 1.38:1，不顯著", "Porubsky 2025（Nature，P = 0.09）", 1.38 / 2.38, "父 58%", "母 42%"),
    ]
    for i, (head, cite, frac, l, r) in enumerate(rows):
        y = 70 + i * 104
        s.text(30, y + 22, head, "b")
        split_bar(s, 30, y + 38, 300, frac, l, r)
        s.text(30, y + 88, cite, "s", "start", "mute")
    s.text(345, 116, "虛線＝各半", "s", "start", "mute")

    # right: three context-specific biases
    rx = 630
    y = 66
    s.text(rx, y + 22, "失活的 X：Xi 是 Xa 的 1.78 倍", "b")
    s.text(rx, y + 52, "Xa", "s")
    s.text(rx, y + 76, "Xi", "s")
    s.bar(rx + 34, y + 46, 150, "panel3", 12)
    s.bar(rx + 34, y + 70, 150, "ink2", 12)
    stars_on(s, y + 46, [rx + 70, rx + 150])
    stars_on(s, y + 70, [rx + 54, rx + 84, rx + 114, rx + 144, rx + 170])
    s.text(rx, y + 102, "Caballero 2023、Jäger 2013", "s", "start", "mute")

    y = 178
    s.text(rx, y + 22, "成簇突變：同一條，只占 3.7%", "b")
    s.bar(rx + 34, y + 46, 150, "hp1", 12)
    s.bar(rx + 34, y + 70, 150, "hp2", 12)
    stars_on(s, y + 46, [rx + 92, rx + 108, rx + 124, rx + 140])
    stars_on(s, y + 70, [rx + 60])
    s.text(rx, y + 102, "Nik-Zainal 2012、Bergstrom 2022", "s", "start", "mute")

    y = 290
    s.text(rx, y + 22, "少數基因座：JAK2 38／45 和 germline 同一條", "b")
    s.bar(rx + 34, y + 52, 150, "hp1", 12)
    s.circle(rx + 74, y + 52, 6, "ink")
    s.star(rx + 124, y + 52, 8)
    s.path(f"M{rx + 76} {y + 40} Q{rx + 100} {y + 20} {rx + 122} {y + 39}", "ink2", 2)
    s.text(rx + 200, y + 58, "● germline　★ somatic", "s", "start", "mute")
    s.text(rx, y + 86, "Kilpivaara 2009；驅動基因另見 Gorelick 2020", "s", "start", "mute")

    # bottom strip
    s.rect(10, 404, 580, 58, "panel", r=10)
    s.text(30, 440, "對照：germline 新生突變約 80% 在父源（精卵，不是體細胞）", "s")
    s.rect(610, 404, 580, 58, "panel2", r=10)
    s.text(630, 440, "拷貝數改變（LOH、擴增）會改變看到的比例 → 下一階段", "s")

    notes = ("這頁看論文怎麼回答：SNV 偏向一條，還是兩條都有。左邊是兩條大致各半的證據。"
             "腫瘤只有一篇 21 人的預印本，父母差異在 5% 以內；兩個家族研究看受精後的突變，52% 在父源，"
             "long read 家族是 1.38 比 1，都不顯著。右邊是會偏一條的情境：失活的 X 突變率是另一條的 1.78 倍；"
             "成簇突變落在同一條，但只占 3.7%；JAK2 這類少數基因座和 germline 變異在同一條。"
             "下面對照：精卵的新生突變約八成來自父親，那不是體細胞。拷貝數改變留到下一階段。接下來看資料結果。")
    write_page("hypotheses", page("hypotheses", "論文支持 SNV 在兩條大致各半；偏向只在特定情境", s, "", notes))


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
    # 2026-11-08 (user): option C (真值多記一欄親源) removed; two wider cards.
    cols = [10, 610]
    cw = 580
    pad = (cw - 380) / 2  # option_pic draws a 380-wide picture
    for x in cols:
        frame(s, x, 30, cw, 300, "paper", "line2", 1.5)
    s.rect(3, 20, cw + 14, 318, None, "ink", r=16, sw=4)
    pill(s, 10 + cw / 2, 26, "目前傾向，還沒決定", "ink", filled=True)

    pros = [[(True, "和 COLO829、HG008 兩株一致"), (False, "缺近距離成簇")],
            [(True, "更接近真實"), (False, "要大改程式")]]
    for i, x in enumerate(cols):
        s.text(x + cw / 2, 66, OPT_HEADS[i], "h", "middle")
        option_pic(s, i, x + pad, 111)
        s.text(x + cw / 2, 194, OPT_RULES[i], "t", "middle")
        for k, (good, txt) in enumerate(pros[i]):
            ok_line(s, x + pad + 22, 232 + k * 30, good, txt, "t")
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

    notes = ("這頁是模擬器的兩個方案，目前傾向 A，用黑框標出來，還沒決定；兩張圖都是示意。"
             "A 維持每個 SNV 獨立、兩條各半，和 COLO829、HG008 兩株一致；這次的 50% 有實測支持，不是直接設的。缺點是沒有近距離成簇。"
             "B 加座標，讓少數 SNV 在 1 kb 內成簇落在同一條，更接近真實，但要大改程式。"
             "下面左邊，現有模擬器隨機選一份 copy，只在兩條份數相同時是 50%。中間四個工具，模擬時會用座標。"
             "右邊，diplosim 各自定拷貝數，不需要座標；真實資料要靠座標對到拷貝數片段。這兩個方案想請老師決定。")
    write_page("options", page("options", "模擬器的兩個方案，目前傾向維持獨立 50%（根據見結果段）", s, "", notes))


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
    # p7 t2-data was deleted by the user in the deck editor on 2026-11-08; p7() kept for reference only.
