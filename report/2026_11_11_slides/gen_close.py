"""p14 self-check, p15 ai-env, p16 decide. Sketches: sketches/close.md."""
from slidekit import S, page, write_page, n3_ladder, tag  # noqa: F401
from gen_plan import option_pic, pill
from gen_res2 import hg008_tree, tree_legend


# --- small pictograms ------------------------------------------------------------------

def seal(s, x, y, ok, r=17):
    """A round pass/fail seal."""
    s.circle(x, y, r, "c4" if ok else "mut")
    if ok:
        s.path(f"M{x - r * .45:.1f} {y + r * .02:.1f} L{x - r * .1:.1f} {y + r * .38:.1f} L{x + r * .5:.1f} {y - r * .35:.1f}", "on", 3.2)
    else:
        s.xmark(x, y, r * .38, "on", 3.2)


def ico_target(s, x, y):
    s.circle(x, y, 18, None, "ink2", 2)
    s.circle(x, y, 10, None, "ink2", 2)
    s.circle(x, y, 4, "mut")


def ico_doc(s, x, y):
    s.rect(x - 14, y - 18, 28, 36, "on", "ink2", r=3, sw=2)
    for i in range(3):
        s.line(x - 8, y - 9 + i * 8, x + 8, y - 9 + i * 8, "line2", 2)
    s.circle(x + 13, y + 14, 7, "c4")


def ico_grid4(s, x, y):
    for i in range(2):
        for j in range(2):
            s.rect(x - 17 + i * 18, y - 17 + j * 18, 15, 15, "panel3", None, r=2)
    s.rect(x + 1, y + 1, 15, 15, None, "mut", r=2, dash=True, sw=2)


def ico_lens(s, x, y):
    s.circle(x - 4, y - 4, 11, None, "ink2", 3)
    s.line(x + 4, y + 4, x + 14, y + 14, "ink2", 4)


def ico_ai(s, x, y):
    s.rect(x - 19, y - 14, 38, 26, "panel3", None, r=8)
    s.poly([(x - 8, y + 12), (x - 2, y + 12), (x - 10, y + 20)], "panel3")
    s.circle(x - 7, y - 1, 3, "ink")
    s.circle(x + 7, y - 1, 3, "ink")


def ico_person(s, x, y):
    s.person(x, y - 20, h=40)


def ico_back(s, x, y):
    s.path(f"M{x + 16} {y + 10} Q{x + 16} {y - 14} {x - 6} {y - 14} L{x - 10} {y - 14}", "ink2", 3)
    s.poly([(x - 18, y - 14), (x - 8, y - 21), (x - 8, y - 7)], "ink2")


def ico_abc(s, x, y):
    for i in range(3):
        s.rect(x - 20 + i * 14, y - 14 + (1 - i) * 0, 12, 26, "panel3" if i else "c4", None, r=2)


def ico_flow(s, x, y):
    for i in range(3):
        s.rect(x - 24 + i * 18, y - 9, 12, 18, "panel3", None, r=2)
    s.line(x - 12, y, x - 6, y, "ink2", 2.5)
    s.line(x + 6, y, x + 12, y, "ink2", 2.5)


def ico_reads(s, x, y):
    s.bar(x - 20, y - 8, 40, "hp1", 8)
    s.bar(x - 20, y + 8, 40, "hp2", 8)


def ico_hyp(s, x, y):
    s.bar(x - 20, y + 6, 40, "hp1", 12)
    s.star(x + 2, y + 6, 8)
    s.text(x + 10, y - 9, "?", "h", "start", "ink2")


def ico_ladder(s, x, y):
    for i in range(3):
        s.rect(x - 18, y + 8 - i * 12, 36, 9, "c4" if i == 1 else "panel3", None, r=2)


def ico_gear(s, x, y):
    s.circle(x, y, 15, None, "ink2", 7, dash=True)
    s.circle(x, y, 9, "ink2")
    s.circle(x, y, 4, "panel")


# --- p14 ----------------------------------------------------------------------------------

def self_check():
    H = 470
    s = S("self-check", 1200, H)
    panels = [
        ("10-21 會議", 0, 450, [
            (True, ico_target, "每頁第一句對準研究目標", "標題寫成結論"),
            (True, ico_doc, "「可以／沒有」附來源", "實際結果／推論標籤"),
            (False, ico_grid4, "benchmark 寫出四件事", "資料卡缺輸入、生成程式"),
            (False, ico_lens, "「沒找到」附搜尋範圍", "「六個克隆」沒寫查哪裡"),
            (False, ico_ai, "AI 結論標出親自核對處", "結果頁沒標核對過哪些"),
            (False, ico_person, "脫稿講完生成步驟", "本冊沒有生成步驟頁"),
        ]),
        ("10-28 會議", 470, 340, [
            (True, ico_back, "開頭接回上次會議", "第 1、2 頁"),
            (True, ico_abc, "選擇都列候選與理由", "第 6、7 頁"),
            (True, ico_flow, "逐步過程有圖", "第 4、11 頁"),
        ]),
        ("11-04 會議", 830, 370, [
            (True, ico_reads, "分清模擬真值與觀測", "第 2 頁"),
            (True, ico_hyp, "機制附假說與來源", "第 5、6 頁"),
            (True, ico_ladder, "驗證標出支持哪一層", "第 7–12 頁"),
            (True, ico_gear, "有 AI 環境改善頁", "第 15 頁"),
        ]),
    ]
    for name, x, w, rows in panels:
        s.rect(x, 0, w, H, "panel", None, r=10)
        s.text(x + 20, 38, name, "h")
        n_ok = sum(1 for r in rows if r[0])
        n_bad = len(rows) - n_ok
        tx = x + w - 20
        if n_bad:
            s.text(tx, 38, f"{n_bad}", "h", "end", "mut")
            seal(s, tx - 32, 31, False, 12)
            tx -= 60
        s.text(tx, 38, f"{n_ok}", "h", "end", "c4")
        seal(s, tx - 32, 31, True, 12)
        s.line(x + 16, 58, x + w - 16, 58, "line", 2)
        top, bot = 64, H - 6
        step = (bot - top) / len(rows)
        for i, (ok, ico, label, why) in enumerate(rows):
            cy = top + step * (i + .5)
            if not ok:
                s.rect(x + 8, cy - step / 2 + 3, w - 16, step - 6, "on", "mut", r=8, sw=1.5)
            seal(s, x + 32, cy, ok)
            ico(s, x + 84, cy)
            s.text(x + 120, cy - 5, label, "t")
            s.text(x + 120, cy + 21, why, "s", "start", "ink2" if ok else "mut")
    notes = ("這頁是上次會議要我們報告前自己檢查的清單，三次會議加起來 13 條，9 條通過，4 條沒通過。"
             "右邊兩欄，10-28 和 11-04 的 7 條都通過，旁邊寫的是在哪一頁做到。"
             "沒通過的 4 條都在左邊 10-21 這欄，用紅框標出來。"
             "第一，資料卡缺了輸入和生成程式兩件事；第二，「六個克隆」沒有寫查了哪裡；"
             "第三，結果頁沒有標出哪些是我自己核對過的；第四，這次沒有生成步驟頁，所以沒辦法檢查能不能脫稿講完。"
             "這四條下次報告會補上。下一頁是 AI 環境改善：這週加的兩條工作規則。")
    write_page("self-check", page("self-check", "上次會議的檢查清單：9 條通過，4 條未通過", s, notes=notes))


# --- p15 ----------------------------------------------------------------------------------

def strike_pair(s, cx, y, wrong, right):
    """A wrong phrase struck through, an arrow, the corrected phrase."""
    s.text(cx, y, wrong, "t", "middle", "ink2")
    from lib import width
    w = width(wrong, 20)
    s.line(cx - w / 2 - 4, y - 6, cx + w / 2 + 4, y - 6, "mut", 3)
    s.arrow(cx, y + 12, cx, y + 44, c="ink2", sw=2.5)
    s.text(cx, y + 72, right, "t", "middle", "c4")


def ai_env():
    H = 465
    s = S("ai-env", 1200, H)
    # left: the layered knowledge base
    s.rect(0, 0, 400, H, "panel", None, r=10)
    s.text(20, 38, "知識庫分層", "h")
    layers = [("索引", "先找路徑", "panel2"), ("摘要", "重點", "panel2"), ("全文", "找段落", "panel3"), ("第一手資料", "論文・程式", "hl")]
    for i, (name, sub, col) in enumerate(layers):
        y0 = 70 + i * 96
        half_top, half_bot = 170 - i * 26, 170 - (i + 1) * 26
        cx = 215
        s.poly([(cx - half_top, y0), (cx + half_top, y0), (cx + half_bot, y0 + 82), (cx - half_bot, y0 + 82)], col)
        s.text(cx, y0 + 38, name, "h", "middle")
        s.text(cx, y0 + 66, sub, "s", "middle")
    s.arrow(26, 90, 26, 430, c="ink2", sw=2.5)
    s.text(36, 455, "不夠才往下讀", "s")

    # right top: the two rules
    def rule_card(x, title):
        s.rect(x, 0, 375, 215, "panel", None, r=10)
        s.text(x + 20, 38, title, "h")

    rule_card(425, "規則一：畫圖前逐項對原文")
    # draft figure
    fx, fy = 450, 70
    s.rect(fx, fy, 120, 110, "on", "ink2", r=6, sw=2)
    s.bar(fx + 14, fy + 34, 92, "hp1", 12)
    s.bar(fx + 14, fy + 62, 92, "hp2", 12)
    s.star(fx + 40, fy + 34, 8)
    s.star(fx + 78, fy + 62, 8)
    s.text(fx + 60, fy + 98, "圖", "s", "middle")
    # source document
    dx = 655
    s.rect(dx, fy, 120, 110, "hl", "ink2", r=6, sw=2)
    for i in range(5):
        s.line(dx + 14, fy + 18 + i * 14, dx + 106 - (i % 2) * 22, fy + 18 + i * 14, "line2", 2.5)
    s.text(dx + 60, fy + 98, "原文", "s", "middle")
    for i, yy in enumerate((fy + 34, fy + 62)):
        s.line(fx + 124, yy, dx - 4, yy, "ink2", 2, dash=True)
        seal(s, 612, yy, True, 11)
    ico_lens(s, 760, 186)

    rule_card(825, "規則二：設計選項帶到週會")
    for i, L in enumerate("ABC"):
        s.rect(848, 72 + i * 42, 46, 34, "on", "ink2", r=5, sw=2)
        s.text(871, 96 + i * 42, L, "h", "middle")
    s.arrow(905, 125, 960, 125, c="ink2")
    # meeting: a table with people around it
    s.rect(990, 136, 170, 26, "panel3", None, r=13)
    for i, px in enumerate((1010, 1075, 1140)):
        s.person(px, 80, h=52, fill="c4" if i == 1 else "panel3")
    s.text(1075, 195, "週會上選", "s", "middle")


    # right bottom: effective / not effective
    s.rect(425, 235, 775, 230, "panel", None, r=10)
    seal(s, 450, 266, True, 13)
    s.text(472, 274, "有效", "h", "start", "c4")
    seal(s, 1035, 266, False, 13)
    s.text(1057, 274, "無效", "h", "start", "mut")
    tiles = [(530, "查證", "沒有座標", "有座標，沒作用"),
             (718, "大綱審查", "控制拷貝數", "扣掉流失片段"),
             (900, "大綱審查", "兩條都在", "該條 ≥1 份")]
    for cx, who, wrong, right in tiles:
        s.rect(cx - 88, 292, 176, 162, "on", None, r=8)
        s.text(cx, 320, who, "s", "middle")
        strike_pair(s, cx, 354, wrong, right)
    s.line(995, 292, 995, 454, "line2", 2)
    # bad: a summary copied in without checking; one number lands in the wrong cell
    cx = 1105
    s.rect(cx - 88, 292, 176, 162, "on", None, r=8)
    s.text(cx, 320, "子代理摘要", "s", "middle")
    for i in range(3):
        for j in range(3):
            s.rect(cx - 45 + i * 31, 338 + j * 24, 28, 21, "panel2", None, r=2)
    s.rect(cx - 45 + 62, 338, 28, 21, None, "mut", r=2, sw=2, dash=True)
    s.rect(cx - 45 + 0, 338 + 48, 28, 21, "mut", None, r=2)
    s.arrow(cx + 30, 350, cx - 28, 392, c="mut", sw=2)
    s.text(cx, 434, "數字放錯格", "s", "middle", "mut")
    # dashed link from rule one down the gap to the first-hand layer
    s.path("M445 200 Q412 210 412 250 L412 360 Q412 380 392 380 L340 380", "stdis", 2.5, dash=True)
    s.poly([(328, 380), (340, 373), (340, 387)], "stdis")

    notes = ("這週在工作規則裡加了兩條：畫圖前逐項對原文，和設計選項帶到週會。"
             "左邊是知識庫的分層，先看索引和摘要，不夠才往下讀全文，最底下是論文和程式這些第一手資料。"
             "規則一就是畫圖前要讀到最底層，把圖上每一項和原文對過。規則二是設計上的選項，先帶到週會讓老師選，再動手。"
             "右下是實例：有效的三個，查證抓到「沒有座標」寫錯，其實有座標、只是沒作用；大綱審查抓到兩處說法寫錯。"
             "無效的一個是子代理的摘要沒核對就採用，數字放錯格。"
             "最後一頁，是想請老師決定的兩件事。")
    write_page("ai-env", page("ai-env", "本週加了兩條工作規則：畫圖前逐項對原文、設計選項帶到週會", s, notes=notes))


# --- p16 ----------------------------------------------------------------------------------

def decide():
    H = 465
    s = S("decide", 1200, H)
    # card one: the three options, the same pictograms as p6
    s.rect(0, 0, 590, H, "panel", None, r=10)
    s.text(24, 42, "① SNV 階段用哪個方案？", "h")
    names = [("A　維持", "獨立 50%"), ("B　加座標", "近距離成簇"), ("C　真值多記", "一欄親源")]
    for i, (l1, l2) in enumerate(names):
        y0 = 60 + i * 135
        chosen = i == 0
        s.rect(10, y0, 570, 125, "on", "ink" if chosen else None, r=8, sw=3)
        option_pic(s, i, 4, y0 + 52)
        s.text(398, y0 + 40, l1, "b")
        s.text(398, y0 + 68, l2, "b")
        tag(s, 398, y0 + 106, "示意", "demo")
        if chosen:
            pill(s, 515, y0 + 106, "目前傾向", "ink", filled=True)

    # card two: HG008 tree thumbnail (the p11 tree without numbers) and the N3 ladder
    s.rect(610, 0, 590, H, "panel", None, r=10)
    s.text(634, 42, "② HG008 能驗證到哪一層？", "h")
    s.rect(630, 64, 330, 330, "on", None, r=8)
    hg008_tree(s, 665, 37, (104, 144, 184, 224, 264), 300, tube_w=14, tube_h=32, sw=4, stub=16)
    tree_legend(s, [(980, 110), (980, 150), (980, 190)])
    # ladder: clone structure lit, evolutionary path unknown
    n3_ladder(s, 1010, 330, lit=[1])
    s.text(1172, 271, "?", "big", "middle", "mut")
    s.arrow(962, 296, 1004, 296, c="c4", sw=2.5)
    s.text(905, 435, "「像」怎麼定義？", "big", "middle", "mut")

    notes = ("最後有兩件事想請老師決定。左邊第一件是 SNV 階段的模擬器用哪個方案，三張圖和第 6 頁相同，都是示意："
             "A 維持獨立 50%，每個 SNV 各半落在 HP1 或 HP2，這是目前傾向；"
             "B 加座標，讓 1 kb 內的 SNV 近距離成簇落在同一條；C 真值多記一欄爸或媽。"
             "右邊第二件是 HG008 能驗證到哪一層。這是第 11 頁的候選樹，實線有單細胞支持、半實線部分支持，"
             "目前只亮到「克隆結構」，「演化路徑」還是問號。所以想請老師一起定義，模擬和真實資料「像」要怎麼算。")
    write_page("decide", page("decide", "請老師決定：SNV 階段的模擬器方案，以及 HG008 能驗證到哪一層", s, notes=notes))


if __name__ == "__main__":
    self_check()
    ai_env()
    decide()
