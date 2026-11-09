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


def doc_icon(s, x, y, w, h, fill="on", stroke="ink2", lines=3, label=None):
    """A sheet with a folded corner; optional short label inside."""
    c = min(w, h) * 0.28
    s.poly([(x, y), (x + w - c, y), (x + w, y + c), (x + w, y + h), (x, y + h)], fill, stroke, 2)
    s.poly([(x + w - c, y), (x + w - c, y + c), (x + w, y + c)], "line", stroke, 1.5)
    for i in range(lines):
        yy = y + c + 8 + i * (h - c - 16) / max(lines, 1)
        s.line(x + 8, yy, x + w - 10, yy, "line2", 2)
    if label:
        s.text(x + w / 2, y + h - 8, label, "s", "middle", "ink")


def table_icon(s, x, y, w, rows, rh=20, new_row=None):
    s.rect(x, y, w, rh, "panel3", "ink2", r=0, sw=1.5)
    for i in range(rows):
        last = new_row is not None and i == rows - 1
        s.rect(x, y + rh * (i + 1), w, rh, "hl" if last else "on", "ink2", r=0, sw=1.5)
    for f in (0.28, 0.62):
        s.line(x + w * f, y, x + w * f, y + rh * (rows + 1), "ink2", 1.2)
    if new_row:
        s.text(x + 8, y + rh * rows + rh - 5, new_row, "s", "start", "ink")


def robot(s, cx, cy):
    s.line(cx, cy - 36, cx, cy - 50, "ink2", 3)
    s.circle(cx, cy - 54, 6, "mut")
    s.rect(cx - 40, cy - 36, 80, 66, "ink2", None, r=16)
    s.circle(cx - 17, cy - 6, 9, "on")
    s.circle(cx + 17, cy - 6, 9, "on")
    s.circle(cx - 17, cy - 6, 4, "ink")
    s.circle(cx + 17, cy - 6, 4, "ink")
    s.rect(cx - 14, cy + 14, 28, 5, "on", None, r=2)


def ai_env():
    # 2026-11-09 redesign v2 (user): ~80 % pictures, ~20 % text (report_rule F-16). Sources:
    # research/literature/README.md 「規則」 (ingest), research/index.md 檔頭「檢索順序」 (retrieval).
    H = 470
    s = S("ai-env", 1200, H)

    # (1) one paper goes in: paper -> folder of three files -> one new index row
    s.rect(0, 0, 1200, 208, "panel", None, r=10)
    s.text(20, 34, "① 放進知識庫", "h")
    doc_icon(s, 70, 54, 96, 118, "on", "ink2", 4, "PDF")
    s.text(118, 198, "論文", "b", "middle")
    s.arrow(186, 113, 286, 113, c="ink2", sw=3, head=12)
    # folder
    s.poly([(300, 58), (392, 58), (408, 72), (300, 72)], "c3")
    s.rect(300, 70, 330, 108, "hl", "c3", r=8, sw=2)
    s.text(316, 64, "P01", "s", "start", "ink")
    for i, lab in enumerate(("全文", "摘要", "來源")):
        doc_icon(s, 326 + i * 100, 84, 74, 84, "on", "ink2", 2, lab)
    s.text(465, 198, "一篇一個資料夾", "b", "middle")
    s.arrow(648, 113, 738, 113, c="ink2", sw=3, head=12)
    table_icon(s, 752, 50, 300, 5, 21, "P01")
    s.circle(1080, 166, 16, "c4")
    s.text(1080, 173, "+", "h", "middle", "on")
    s.text(902, 198, "索引加一列", "b", "middle")

    # (2) how the agent looks it up: a staircase index -> summary -> full text -> original
    s.rect(0, 220, 1200, 250, "panel2", None, r=10)
    s.text(20, 254, "② agent 怎麼找", "h")
    seal(s, 950, 247, True, r=11)
    s.text(968, 254, "夠了就回答", "s", "start", "c4")
    s.text(1180, 254, "↘ 不夠才往下", "s", "end", "ink2")
    robot(s, 92, 338)
    s.arrow(150, 318, 220, 302, c="ink2", sw=2.5, head=10)
    s.rect(14, 400, 176, 50, "on", "line2", r=14, sw=1.5)
    s.poly([(82, 400), (96, 400), (92, 386)], "on", "line2", 1.5)
    s.text(102, 432, "哪幾篇支持各半？", "s", "middle", "ink")

    sw, sh = 210, 60
    steps = []
    for i, lab in enumerate(("索引", "摘要", "全文", "原文")):
        x, y = 228 + i * 238, 272 + i * 44
        steps.append((x, y))
        last = i == 3
        s.rect(x, y, sw, sh, "hl" if last else "on", "ink2", r=10, sw=1.8)
        ix, iy = x + 14, y + 8
        if i == 0:
            table_icon(s, ix, iy + 2, 64, 3, 10)
        elif i == 1:
            doc_icon(s, ix + 10, iy, 36, 44, "on", "ink2", 2)
        elif i == 2:
            doc_icon(s, ix + 4, iy - 2, 40, 48, "on", "ink2", 4)
            s.circle(ix + 46, iy + 30, 10, None, "mut", 3)
            s.line(ix + 53, iy + 37, ix + 61, iy + 45, "mut", 3.5)
        else:
            doc_icon(s, ix + 6, iy, 40, 46, "on", "ink2", 0, None)
            s.text(ix + 26, iy + 38, "PDF", "s", "middle", "mut")
        s.text(x + 128, y + 39, lab, "h", "middle")
        if i < 3:
            seal(s, x + sw - 6, y + 4, True, r=11)
    for i in range(3):
        (x1, y1), (x2, y2) = steps[i], steps[i + 1]
        s.arrow(x1 + sw + 4, y1 + 36, x2 - 4, y2 + 30, c="ink2", sw=2.5, head=10)
    # feedback: what the bottom layer finds is written back (dashed, F-6)
    (xs, ys), (xe, ye) = steps[3], steps[1]
    s.path(f"M{xs + sw / 2} {ys} L{xs + sw / 2} {ye + sh / 2} L{xe + sw + 6} {ye + sh / 2}", "c4", 2.5, dash=True)
    s.poly([(xe + sw + 2, ye + sh / 2), (xe + sw + 14, ye + sh / 2 - 7), (xe + sw + 14, ye + sh / 2 + 7)], "c4")
    s.text(xs + sw / 2 + 12, ye + sh / 2 - 8, "補回", "s", "start", "c4")

    notes = ("這頁畫知識庫怎麼用。上面是放一篇論文：拿到論文，開一個資料夾，放全文、摘要、來源三個檔，"
             "最後在索引加一列，寫路徑、一句話和關鍵字。下面是 agent 怎麼找：先查索引，再讀摘要，"
             "打勾表示夠了就回答；不夠才讀全文，最後才看 PDF 或補充表。"
             "最底層找到的新資料會補回摘要，像今天 Lefèbvre 的癌別和 purity。回答時標來源和讀到第幾層。"
             "下一頁回到模擬器的三個方案。")
    write_page("ai-env", page("ai-env", "知識庫：論文一篇一個資料夾，agent 從索引一層層往下找", s, notes=notes))
    return notes


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
