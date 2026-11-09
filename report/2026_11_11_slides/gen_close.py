"""p14 self-check, p15 ai-env, p16 decide. Sketches: sketches/close.md."""
from slidekit import S, page, write_page, n3_ladder, tag, ORDER  # noqa: F401
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
            (True, ico_back, "開頭接回上次會議", f"第 {'、'.join(str(ORDER.index(i) + 1) for i in ('outline', 'n-fixes',))} 頁"),
            (True, ico_abc, "選擇都列候選與理由", f"第 {'、'.join(str(ORDER.index(i) + 1) for i in ('hypotheses', 'options',))} 頁"),
            (True, ico_flow, "逐步過程有圖", f"第 {'、'.join(str(ORDER.index(i) + 1) for i in ('ratio-flow', 'hg008-tree',))} 頁"),
        ]),
        ("11-04 會議", 830, 370, [
            (True, ico_reads, "分清模擬真值與觀測", f"第 {'、'.join(str(ORDER.index(i) + 1) for i in ('n-fixes',))} 頁"),
            (True, ico_hyp, "機制附假說與來源", f"第 {'、'.join(str(ORDER.index(i) + 1) for i in ('hypotheses', 'options',))} 頁"),
            (False, ico_lens, "驗證標出支持哪一層", "三層標示未定案，已移除"),
            (True, ico_gear, "有 AI 環境改善頁", f"第 {ORDER.index('ai-env') + 1} 頁"),
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
    notes = ("這頁是上次會議要我們報告前自己檢查的清單，三次會議加起來 13 條，8 條通過，5 條沒通過。"
             "中間 10-28 的 3 條都通過，旁邊寫的是在哪一頁做到；右邊 11-04 有 1 條沒通過：驗證支持哪一層，這個標示還沒定案，這次先拿掉。"
             "左邊 10-21 這欄有 4 條沒通過，用紅框標出來。"
             "第一，資料卡缺了輸入和生成程式兩件事；第二，「六個克隆」沒有寫查了哪裡；"
             "第三，結果頁沒有標出哪些是我自己核對過的；第四，這次沒有生成步驟頁，所以沒辦法檢查能不能脫稿講完。"
             "這四條下次報告會補上。下一頁是 AI 環境改善：這週加的兩條工作規則。")
    write_page("self-check", page("self-check", "上次會議的檢查清單：8 條通過，5 條未通過", s, notes=notes))


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
    # 2026-11-08 (user comment): keep only the knowledge-base layers; the two rules and the examples were removed.
    H = 440
    s = S("ai-env", 1200, H)
    s.rect(0, 0, 1200, H, "panel", None, r=10)
    layers = [("索引", "先找路徑", "panel2", "research/index.md：每篇一列，路徑＋一句話＋關鍵字"),
              ("摘要", "重點", "panel2", "summary.md：結論與數字，標〔論文〕〔推論〕"),
              ("全文", "找段落", "panel3", "fulltext.md：用關鍵字找原句（只留本機）"),
              ("第一手資料", "論文・程式", "hl", "source.md 指向 PDF、DOI、程式 commit")]
    cx = 250
    for i, (name, sub, col, what) in enumerate(layers):
        y0 = 24 + i * 100
        half_top, half_bot = 220 - i * 34, 220 - (i + 1) * 34
        s.poly([(cx - half_top, y0), (cx + half_top, y0), (cx + half_bot, y0 + 86), (cx - half_bot, y0 + 86)], col)
        s.text(cx, y0 + 40, name, "h", "middle")
        s.text(cx, y0 + 68, sub, "s", "middle")
        s.line(cx + half_top + 14, y0 + 43, 520, y0 + 43, "line2", 1.5, dash=True)
        s.text(536, y0 + 50, what, "t")
    s.arrow(14, 40, 14, 400, c="ink2", sw=2.5)
    s.text(24, 428, "不夠才往下讀", "s")

    notes = ("這週的 AI 環境改善，是把研究知識庫分成四層。"
             "最上面是索引，每篇論文一列，先在這裡找路徑；第二層是摘要，寫結論和數字，標出哪些是論文、哪些是推論；"
             "摘要不夠，再到第三層全文，用關鍵字找原句；最底下是第一手資料，就是 PDF、DOI 和程式。"
             "AI 回答時先從上往下找，不夠才往下讀。"
             "最後一頁是模擬器的兩個方案。")
    write_page("ai-env", page("ai-env", "本週把研究知識庫分成四層：索引、摘要、全文、第一手資料", s, notes=notes))


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
    s.text(634, 42, "② HG008 的候選樹能驗證什麼？", "h")
    s.rect(630, 64, 330, 330, "on", None, r=8)
    hg008_tree(s, 665, 37, (104, 144, 184, 224, 264), 300, tube_w=14, tube_h=32, sw=4, stub=16)
    tree_legend(s, [(980, 110), (980, 150), (980, 190)])
    # 2026-11-08: the three-layer validation ladder was removed at the user's request (not agreed).
    s.text(905, 435, "「像」怎麼定義？", "big", "middle", "mut")

    notes = ("最後有兩件事想請老師決定。左邊第一件是 SNV 階段的模擬器用哪個方案，三張圖和前一頁相同，都是示意："
             "A 維持獨立 50%，每個 SNV 各半落在 HP1 或 HP2，這是目前傾向；"
             "B 加座標，讓 1 kb 內的 SNV 近距離成簇落在同一條；C 真值多記一欄爸或媽。"
             "右邊第二件是 HG008 的候選樹能驗證什麼。實線有單細胞支持、半實線部分支持。"
             "想請老師一起定義，模擬和真實資料「像」要怎麼算。")
    write_page("decide", page("decide", "請老師決定：SNV 階段的模擬器方案，以及 HG008 的候選樹能驗證什麼", s, notes=notes))


if __name__ == "__main__":
    # self-check was deleted by the user in the deck editor on 2026-11-08; self_check() kept for reference only.
    ai_env()
    # decide was deleted by the user in the deck editor on 2026-11-08; decide() kept for reference only.
