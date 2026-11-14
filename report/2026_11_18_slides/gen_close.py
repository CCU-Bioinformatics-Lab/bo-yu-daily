"""Closing pages: decide (p10, what the advisor is asked to decide) and ai-env (p11, AI environment changes).

Sources: decide -> lab_report/2026-11-13_hg008_bulk_rebuild/README.md (four questions, 1+1 share 43.4 %),
lab_report/2026-11-12_diplosim_haploclone_hp_vs_base/README.md §6-§7 (HP needs copy-number differences or
same-read co-occurrence), CLAUDE.md 「研究範圍」(11-11 SNV only) 「研究目標」(11-04 co-occurrence not a requirement),
haploclone rust/docs/plan.md header (A2 and the read-pair term already ported).
ai-env -> BRIEF.md 「AI 環境」 (three items, all effective; no open problems, user 11-13).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python3 -I drops the script dir
from slidekit import S, page, write_page, tag  # noqa: E402
from lib import width  # noqa: E402
from gen_hg import tube, doc  # noqa: E402
from gen_hg2 import square  # noqa: E402

H = 500


def seal(s, x, y, ok=True, r=17):
    s.circle(x, y, r, "c4" if ok else "mut")
    if ok:
        s.path(f"M{x - r * .45:.1f} {y + r * .02:.1f} L{x - r * .1:.1f} {y + r * .38:.1f} L{x + r * .5:.1f} {y - r * .35:.1f}", "on", 3.2)
    else:
        s.xmark(x, y, r * .38, "on", 3.2)


def tick(s, x, y, c="c4"):
    s.path(f"M{x - 8} {y} L{x - 2} {y + 6} L{x + 9} {y - 7}", c, 3.5)


def mark_line(s, x, y, kind, text):
    """✓ / ✗ / ⇄ (how to check) followed by a short phrase."""
    if kind == "ok":
        tick(s, x + 8, y - 7)
    elif kind == "bad":
        s.xmark(x + 8, y - 7, 7, "mut", 3)
    else:
        s.text(x + 8, y, "⇄", "s", "middle", "ink2")
    s.text(x + 26, y, text, "s", "start", "ink" if kind != "chk" else "ink2")


def pill(s, cx, y, text, col="ink2", filled=False):
    w = width(text, 18) + 24
    s.rect(cx - w / 2, y - 21, w, 30, col if filled else "paper", col, r=15, sw=2)
    s.text(cx, y, text, "s", "middle", "on" if filled else col)
    return w


# ---- p10 decide ---------------------------------------------------------------------------

def decide():
    s = S("decide", 1200, 520)
    # top: HG008 has too few deep-branch SNVs with a reference label; two ways to get more
    s.rect(0, 0, 1200, 166, "panel", None, r=10)
    s.text(16, 30, "① HG008：能拿來對答案的深層 SNV 太少，怎麼補？", "h")
    pill(s, 1184 - (width("目前傾向：未定", 18) + 24) / 2, 30, "目前傾向：未定", "ink")
    cards = [("放寬判斷門檻", [("ok", "沒判出的深層位點也收進來"), ("bad", "多出約三萬個，多半是假的")]),
             ("用 119 顆單細胞核對", [("ok", "不改重建輸入，只多評分點"), ("bad", "單細胞定序淺，可能漏判")])]
    for k, (name, rows) in enumerate(cards):
        x = 10 + k * 594
        s.rect(x, 48, 586, 110, "on", None, r=8)
        if k == 0:
            for i, kind in enumerate(("pass", "pass", "read", "read", "read")):
                square(s, x + 16 + i * 20, 92, kind)
            s.line(x + 12, 84, x + 116, 84, "ink2", 2, dash=True)
            s.arrow(x + 64, 62, x + 64, 80, c="ink2", sw=2.5, head=7)
        else:
            for i in range(6):
                s.circle(x + 26 + (i % 3) * 30, 82 + (i // 3) * 30, 11, ("c2", "c3", "c1")[i % 3], "on", 1.5)
            tick(s, x + 112, 128)
        s.text(x + 136, 80, name, "b")
        for j, (kind, text) in enumerate(rows):
            mark_line(s, x + 130, 112 + j * 34, kind, text)

    # bottom: two ways HP could help the tree, each reopens one earlier decision
    s.text(16, 194, "② 只有 SNV 時 HP 幫不上樹形：要改哪個舊決定？", "h")
    y0, ch, cw2 = 208, 312, 590
    opts = [
        dict(name="加拷貝數變化", rule="要改 11-11「只模擬 SNV」", idea="一條 HP 多一份或少一份",
             rows=[("ok", "重建程式已有對應計算"), ("bad", "HG008 兩條份數不同只占約 2%"),
                   ("bad", "拷貝數估錯，CCF 跟著錯"), ("chk", "同 10 棵樹，比加／不加 HP")],
             lean="目前傾向：未定", filled=False),
        dict(name="同一條 read 上的共現", rule="要改 11-04「先不列需求」", idea="兩個 SNV 在同一條 read",
             rows=[("ok", "直接看出兩個 SNV 的關係"), ("bad", "模擬器要改成產生 read"),
                   ("bad", "兩個 SNV 要夠近才同 read"), ("chk", "同 10 棵樹，比加／不加共現")],
             lean="目前傾向：未定", filled=False),
    ]
    for k, o in enumerate(opts):
        x = k * (cw2 + 20)
        s.rect(x, y0, cw2, ch, "panel", "ink" if o["filled"] else None, r=10, sw=2.5)
        s.text(x + 16, y0 + 36, o["name"], "h")
        pill(s, x + cw2 - 16 - (width(o["rule"], 18) + 24) / 2, y0 + 36, o["rule"], "mut")
        # mechanism picture (示意)
        px, py = x + 16, y0 + 58
        s.rect(px, py, 250, 196, "on", None, r=8)
        if k == 0:
            s.text(px + 50, py + 26, "變化前", "s", "middle", "ink2")
            s.bar(px + 14, py + 62, 72, "hp1", 13)
            s.star(px + 44, py + 62, 9)
            s.bar(px + 14, py + 86, 72, "hp2", 13)
            s.arrow(px + 96, py + 74, px + 140, py + 74, c="ink2", sw=2.5, head=9)
            s.text(px + 200, py + 26, "HP1 多一份", "s", "middle", "ink2")
            for j in range(2):
                s.bar(px + 160, py + 50 + j * 24, 72, "hp1", 13)
                s.star(px + 190, py + 50 + j * 24, 9)
            s.bar(px + 160, py + 98, 72, "hp2", 13)
            s.text(px + 125, py + 146, "HP1 上的 SNV", "s", "middle")
            s.text(px + 125, py + 172, "份數一起變", "s", "middle")
        else:
            for j, (b, lab) in enumerate([(True, "同一條線"), (False, "一前一後或不同支")]):
                yy = py + 48 + j * 84
                s.bar(px + 18, yy, 214, "panel3", 14)
                s.circle(px + 70, yy, 10, "mut", "ink2", 1.5)
                s.circle(px + 170, yy, 10, "mut" if b else "on", "ink2", 1.5)
                s.text(px + 125, yy + 40, lab, "s", "middle")
            s.circle(px + 168, py + 18, 6, "mut", "ink2", 1.5)
            s.text(px + 180, py + 24, "alt", "s", "start", "ink2")
            s.circle(px + 214, py + 18, 6, "on", "ink2", 1.5)
            s.text(px + 226, py + 24, "ref", "s", "start", "ink2")
        tag(s, px + 8, py + 222, "示意", "demo")
        # idea + pros / cons / check
        rx = x + 282
        s.text(rx, y0 + 84, o["idea"], "b")
        for j, (kind, text) in enumerate(o["rows"]):
            mark_line(s, rx, y0 + 128 + j * 40, kind, text)
        pill(s, rx + (width(o["lean"], 18) + 24) / 2, y0 + 290, o["lean"], "ink", filled=o["filled"])

    notes = ("最後請老師決定兩件事。上排是 HG008 能對答案的深層 SNV 太少：左邊放寬判斷門檻，多收深層位點，但多出約三萬個，多半是假的；"
             "右邊用 119 顆單細胞核對沒標籤的 SNV，不改重建，缺點是單細胞定序淺。"
             "下排：只有 SNV 時 HP 幫不上樹形，要改一個舊決定。左邊加拷貝數變化，改 11-11『只模擬 SNV』，HP1 多一份時上面的 SNV 一起變；但 HG008 份數不同的區域只約 2%。"
             "右邊同一條 read 上的共現，改 11-04『先不列需求』：兩個都是 alt 表示在同一條線上；缺點是模擬器要產生 read。兩件事我們都沒有傾向。")
    write_page("decide", page("decide", "請老師決定：深層 SNV 怎麼補，以及 HP 要靠拷貝數還是 read 共現", s, notes=notes))
    return notes


# ---- p11 ai-env ---------------------------------------------------------------------------

def rule_doc(s, x, y, w, h, n, colors=None):
    """A rules file: a sheet with n short lines; colors marks some lines."""
    c = w * .22
    s.poly([(x, y), (x + w - c, y), (x + w, y + c), (x + w, y + h), (x, y + h)], "on", "ink2", 2)
    s.poly([(x + w - c, y), (x + w - c, y + c), (x + w, y + c)], "line", "ink2", 1.5)
    step = (h - c - 10) / n
    for i in range(n):
        yy = y + c + 6 + i * step
        col = (colors or {}).get(i, "line2")
        s.line(x + 12, yy, x + w - 16, yy, col, 4 if col != "line2" else 2.5)


def ai_env():
    s = S("ai-env", 1200, H)
    cw = 388
    items = [
        ("工作規則加「本週主軸」", "和「暫停清單」", [("ok", "工作都在五項內"), ("ok", "沒再提暫停項目的實驗")]),
        ("上次週會的六條規則", "寫進工作規則", [("ok", "論文先寫作者結論"), ("ok", "模擬和 HG008 分開報告")]),
        ("設計選擇整理成方案", "帶到週會，週間不請我選", [("ok", "HG008 四件事先收成方案"), ("ok", "HP 兩個選項收成方案")]),
    ]
    for i, (l1, l2, rows) in enumerate(items):
        x = i * (cw + 18)
        cx = x + cw / 2
        s.rect(x, 0, cw, H, "panel", None, r=10)
        seal(s, x + 30, 30, True, 16)
        s.text(x + 56, 37, "有效", "h", "start", "c4")
        # picture area
        s.rect(x + 14, 58, cw - 28, 220, "on", None, r=8)
        if i == 0:
            rule_doc(s, cx - 150, 82, 120, 170, 7, {0: "c1", 1: "c1", 2: "c1", 3: "c1", 4: "c1"})
            for k in range(5):
                s.text(cx - 150 - 12, 82 + 120 * .22 + 12 + k * ((170 - 26 - 10) / 7), str(k + 1), "s", "end", "c1")
            # pause list: pause sign and struck items
            s.rect(cx + 34, 92, 14, 46, "ink2", None, r=3)
            s.rect(cx + 58, 92, 14, 46, "ink2", None, r=3)
            for k in range(3):
                yy = 170 + k * 30
                s.line(cx + 20, yy, cx + 130, yy, "line2", 5)
                s.line(cx + 14, yy, cx + 136, yy, "mut", 2.5)
            s.text(cx - 90, 272, "本週五項", "s", "middle", "c1")
            s.text(cx + 76, 272, "暫停", "s", "middle", "ink2")
        elif i == 1:
            for k in range(3):
                s.person(cx - 140 + k * 40, 100, h=64)
            s.text(cx - 100, 196, "週會", "s", "middle", "ink2")
            s.arrow(cx - 30, 130, cx + 12, 130, c="ink2", sw=3, head=10)
            rule_doc(s, cx + 20, 76, 130, 180, 8, {k: "c4" for k in range(2, 8)})
            s.text(cx - 100, 236, "＋6 條", "b", "middle", "c4")
        else:
            for k, lab in enumerate(("A", "B")):
                bx = cx - 150 + k * 56
                s.rect(bx, 96 + k * 14, 70, 90, "on", "ink2", r=6, sw=2)
                s.text(bx + 35, 150 + k * 14, lab, "big", "middle")
            s.arrow(cx - 10, 150, cx + 40, 150, c="ink2", sw=3, head=10)
            # calendar = the weekly meeting
            s.rect(cx + 54, 92, 112, 112, "on", "ink2", r=8, sw=2)
            s.rect(cx + 54, 92, 112, 26, "stdis", None, r=6)
            for r_ in range(3):
                for c_ in range(4):
                    s.rect(cx + 64 + c_ * 25, 128 + r_ * 24, 16, 16, "c4" if (r_, c_) == (2, 1) else "panel2", None, r=3)
            s.text(cx - 100, 236, "方案", "s", "middle", "ink2")
            s.text(cx + 110, 236, "週會決定", "s", "middle", "ink2")
        s.text(cx, 316, l1, "b", "middle")
        s.text(cx, 346, l2, "b", "middle")
        s.line(x + 20, 370, x + cw - 20, 370, "line", 2)
        for j, (kind, text) in enumerate(rows):
            mark_line(s, x + 24, 412 + j * 44, kind, text)

    notes = ("這頁是 AI 環境改善：這週調整了三項工作規則，三項都有效。"
             "左邊第一項，在工作規則裡加上本週主軸五項和暫停清單；結果這週的工作都在五項裡面，也沒有再提暫停項目的實驗。"
             "中間第二項，把上次週會的六條規則寫進工作規則；效果是讀論文時先寫作者自己的結論，"
             "模擬和 HG008 也分成兩條路線、分開報告，就像今天的投影片。"
             "右邊第三項，設計選擇先整理成方案，帶到週會決定，週間不請我選；"
             "所以 HG008 的四件事先整理成方案，我才在週間決定先跑；HP 的兩個選項整理成前一頁的方案，請老師決定。")
    write_page("ai-env", page("ai-env", "這週三項工作規則調整都有效", s, notes=notes))
    return notes


if __name__ == "__main__":
    decide()
    ai_env()
