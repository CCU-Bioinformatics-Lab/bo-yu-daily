"""Opening pages of the 2026-11-18 deck: outline (p1) and tasks (p2).

python3 -I gen_open.py  -> project/slides/{outline,tasks}.html
Content follows BRIEF.md rows 1-2 and meeting_record/2026_11_11_meeting_summary.md appendix C, D.
Every picture here is 示意 (icons only); no measured numbers on these two pages.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slidekit import ORDER, S, page, tag, write_page  # noqa: E402


def pno(pid):
    return ORDER.index(pid) + 1


# ---- small pictograms (kept here so slidekit stays untouched) ----

def tick(s, x, y, c="stok", k=1.0):
    s.path(f"M{x - 8 * k:.1f} {y:.1f} L{x - 2 * k:.1f} {y + 6 * k:.1f} L{x + 9 * k:.1f} {y - 7 * k:.1f}", c, 3.5 * k)


def badge(s, x, y, kind, r=20):
    """Status stamp: ok (tick, done) or now (arrow, in progress)."""
    edge = {"ok": "stok", "now": "hp1"}[kind]
    s.circle(x, y, r, "on", edge, 3)
    if kind == "ok":
        tick(s, x, y, k=r / 17)
    else:
        s.arrow(x - r * .55, y, x + r * .6, y, c="hp1", sw=3.5, head=9)


def tube(s, cx, y, w=24, h=64, fill="c2"):
    """One 選殖株: a test tube with culture at the bottom."""
    s.rect(cx - w / 2 - 3, y, w + 6, 6, "panel3", r=2)
    s.path(f"M{cx - w / 2:.1f} {y + 6:.1f} L{cx - w / 2:.1f} {y + h - w / 2:.1f} "
           f"A{w / 2:.1f} {w / 2:.1f} 0 0 0 {cx + w / 2:.1f} {y + h - w / 2:.1f} L{cx + w / 2:.1f} {y + 6:.1f}",
           "cellline", 2, "on")
    s.path(f"M{cx - w / 2 + 2:.1f} {y + h * .55:.1f} L{cx - w / 2 + 2:.1f} {y + h - w / 2:.1f} "
           f"A{w / 2 - 2:.1f} {w / 2 - 2:.1f} 0 0 0 {cx + w / 2 - 2:.1f} {y + h - w / 2:.1f} L{cx + w / 2 - 2:.1f} {y + h * .55:.1f} Z",
           None, 0, fill, op=.75)


def tree(s, x, y, sc=1.0, dash=False, lc="line2", cols=("c1", "c2", "c3")):
    """Root on top, one child, two leaves. (x, y) = root."""
    a, b = (x, y), (x, y + 34 * sc)
    l1, l2 = (x - 28 * sc, y + 68 * sc), (x + 28 * sc, y + 68 * sc)
    for p, q in [(a, b), (b, l1), (b, l2)]:
        s.line(*p, *q, lc, 3, dash=dash)
    s.circle(*a, 9 * sc, "normal", "cellline", dash=dash)
    for p, col in [(b, cols[0]), (l1, cols[1]), (l2, cols[2])]:
        s.circle(*p, 10 * sc, col, "cellline", dash=dash)


def doc(s, x, y, w=54, h=70, lines=4, head=None):
    s.rect(x, y, w, h, "on", "cellline", r=5, sw=2)
    if head:
        s.rect(x, y, w, 14, head, r=5)
    for i in range(lines):
        s.line(x + 9, y + 24 + i * 12, x + w - 9, y + 24 + i * 12, "line2", 2.5)


def gear(s, x, y, r=24):
    pts = []
    for i in range(32):
        a = i * math.pi / 16
        rr = r if (i // 2) % 2 == 0 else r * .74
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    s.poly(pts, "line2")
    s.circle(x, y, r * .35, "on")


def bulk(s, cx, cy, rx=40, ry=30):
    """A bulk tumor sample: a packed cluster of mixed clone cells."""
    palette = ["c1", "c2", "c3", "c1", "c2"]
    s.cluster(cx, cy, rx, ry, lambda u, v: palette[int((u + 1) * 2.3 + (v + 1) * 1.7) % 5], r=6)


def magnifier(s, x, y, r=16):
    s.circle(x, y, r, None, "ink2", 3.5)
    s.line(x + r * .7, y + r * .7, x + r * 1.6, y + r * 1.6, "ink2", 5)


def hp_bars(s, x, y, w=110):
    s.bar(x, y, w, "hp1", 14)
    s.bar(x, y + 26, w, "hp2", 14)
    s.star(x + w * .3, y, 9)
    s.star(x + w * .7, y + 26, 9)


# ---- p1 outline ----
# Title = the main question (BRIEF row 1). Five items of the 11-11 meeting, one icon each,
# with ✓ / → status (W-3). Items 3 and 4 are the two routes that answer the main question.

def p_outline():
    pid = "outline"
    s = S(pid, 1200, 500)
    s.text(10, 26, "上次會議（11-11）定的五項", "h")
    cw, gap, x0, y0, ch = 224, 15, 10, 44, 330
    items = [
        ("ok", "參考樹怎麼產生", "流程圖完成"),
        ("ok", "讀兩篇論文", "作者結論整理完"),
        ("ok", "模擬驗證", "10 棵樹比完"),
        ("now", "HG008 bulk 驗證", "第一輪重建完成"),
        ("ok", "AI 環境改善", f"第 {ORDER.index('ai-env') + 1} 頁"),
    ]
    for i, (st, head, sub) in enumerate(items):
        x = x0 + i * (cw + gap)
        cx = x + cw / 2
        s.rect(x, y0, cw, ch, "panel", "hp1" if st == "now" else None, r=12, sw=2.5)
        s.circle(x + 26, y0 + 28, 16, "ink2")
        s.text(x + 26, y0 + 35, str(i + 1), "b", "middle", "on")
        badge(s, x + cw - 28, y0 + 30, st)
        iy = y0 + 70  # icon band: y0+70 .. y0+220
        if i == 0:
            for k in range(3):
                tube(s, x + 40 + k * 30, iy + 20, fill=("c1", "c2", "c3")[k])
            for k in range(4):
                s.circle(x + 40 + (k % 2) * 22, iy + 120 + (k // 2) * 22, 8, "on", "cellline", 1.8)
            s.arrow(x + 120, iy + 75, x + 150, iy + 75, c="ink2", sw=3)
            tree(s, x + 185, iy + 40, .85)
        elif i == 1:
            doc(s, x + 38, iy + 10, head="hp1")
            doc(s, x + 104, iy + 22, head="hp2")
            magnifier(s, x + 180, iy + 60)
            hp_bars(s, x + 50, iy + 120, 126)
        elif i == 2:
            gear(s, x + 52, iy + 30)
            s.arrow(x + 82, iy + 30, x + 120, iy + 30, c="ink2", sw=3)
            tree(s, x + 160, iy + 4, .6)
            tree(s, x + 70, iy + 82, .7)
            s.text(cx, iy + 128, "vs", "b", "middle")
            tree(s, x + 156, iy + 82, .7, dash=True)
        elif i == 3:
            bulk(s, x + 62, iy + 60)
            s.arrow(x + 110, iy + 60, x + 145, iy + 60, c="hp1", sw=3)
            tree(s, x + 178, iy + 26, .7, cols=("c2", "panel2", "panel2"))
            s.text(x + 178, iy + 150, "找回兩層", "s", "middle", "hp1")
        else:
            doc(s, x + 50, iy + 30, head="hp1")
            s.arrow(x + 118, iy + 74, x + 148, iy + 74, c="ink2", sw=3)
            gear(s, x + 180, iy + 74)
        s.text(cx, y0 + 262, head, "b", "middle")
        s.text(cx, y0 + 296, sub, "s", "middle", "hp1" if st == "now" else None)

    # The two routes that answer the main question (items 3 and 4).
    xa = x0 + 2 * (cw + gap)
    xb = x0 + 4 * (cw + gap) - gap
    yb = y0 + ch + 18
    s.path(f"M{xa + 10} {yb} L{xa + 10} {yb + 16} L{xb - 10} {yb + 16} L{xb - 10} {yb}", "hp1", 3)
    s.line((xa + xb) / 2, yb + 16, (xa + xb) / 2, yb + 34, "hp1", 3)
    s.text((xa + xb) / 2, yb + 62, "主問題的兩條路線：模擬、HG008", "b", "middle", "hp1")
    # Legend.
    badge(s, 30, yb + 44, "ok", r=15)
    s.text(54, yb + 51, "完成", "s")
    badge(s, 130, yb + 44, "now", r=15)
    s.text(154, yb + 51, "進行中", "s")

    notes = ("這週的主問題就是標題這句：把 HP 加進樹重建，在模擬和 HG008 上各看到什麼。HP 是 haplotype，指 SNV 落在 HP1 或 HP2 哪一條同源染色體上。"
             "這一排是上次會議定的五項。第一項，參考樹怎麼產生，流程圖已經完成。"
             "第二項，兩篇論文讀完，作者結論整理好了。"
             "第三項，模擬驗證，10 棵樹已經比完。"
             "第四項，HG008 的 bulk 驗證，藍色箭頭表示還在進行：第一輪重建跑完，找回兩層，還有兩層找不回來。"
             "第五項，AI 環境改善，放在這次報告最後一頁。"
             "下面藍色括號標出第三、第四項，就是回答主問題的兩條路線：模擬一條、HG008 一條，兩條分開報告。")
    title = "把 HP 加進樹重建，在模擬和 HG008 上各看到什麼？"
    write_page(pid, page(pid, title, s, "", notes))


# ---- p2 tasks ----
# Four questions this week, one icon each (BRIEF row 2). Page pointers come from ORDER.

def p_tasks():
    pid = "tasks"
    s = S(pid, 1200, 530)
    cw, gap, y0, ch = 285, 20, 44, 480
    cards = [
        ("參考樹怎麼來", "選殖株＋單細胞", "ref-tree"),
        ("論文怎麼說", "HP 比例的依據", "papers"),
        ("模擬有沒有差", "加 HP vs 不加 HP", "sim-method"),
        ("HG008 能不能比", "bulk vs 參考樹", "hg-plan"),
    ]
    for i, (q, sub, target) in enumerate(cards):
        x = 10 + i * (cw + gap)
        cx = x + cw / 2
        s.rect(x, y0, cw, ch, "panel", r=14)
        s.circle(x + 30, y0 + 32, 18, "ink2")
        s.text(x + 30, y0 + 39, str(i + 1), "b", "middle", "on")
        iy = y0 + 70  # icon band: iy .. iy+250
        if i == 0:
            for k in range(3):
                tube(s, x + 50 + k * 34, iy + 10, 26, 72, ("c1", "c2", "c3")[k])
            for r in range(3):
                for c in range(4):
                    s.circle(x + 44 + c * 22, iy + 130 + r * 22, 8, "on", "cellline", 1.8)
            s.arrow(x + 160, iy + 110, x + 196, iy + 110, c="ink2", sw=3.5)
            tree(s, x + 236, iy + 70, .85)
        elif i == 1:
            doc(s, x + 60, iy + 4, 66, 86, 5, "hp1")
            doc(s, x + 150, iy + 18, 66, 86, 5, "hp2")
            magnifier(s, x + 214, iy + 100, 18)
            hp_bars(s, x + 70, iy + 160, 150)
            s.text(x + 50, iy + 166, "1", "s", "middle")
            s.text(x + 50, iy + 192, "2", "s", "middle")
        elif i == 2:
            s.text(cx, iy + 4, "真值樹", "s", "middle")
            tree(s, cx, iy + 20, .65)
            s.line(x + 50, iy + 92, x + 235, iy + 92, "line2", 2, dash=True)
            tree(s, x + 80, iy + 110, .65)
            tree(s, x + 205, iy + 110, .65)
            hp_bars(s, x + 40, iy + 186, 80)
            s.text(x + 80, iy + 240, "加 HP", "s", "middle")
            s.text(x + 205, iy + 240, "不加 HP", "s", "middle")
        else:
            bulk(s, cx, iy + 40, 52, 34)
            s.arrow(x + 80, iy + 80, x + 80, iy + 112, c="ink2", sw=3.5)
            tree(s, x + 80, iy + 122, .65, dash=True, cols=("panel2", "panel2", "panel2"))
            s.text(x + 80, iy + 196, "重建", "s", "middle")
            s.text(cx, iy + 164, "vs", "b", "middle")
            tree(s, x + 205, iy + 122, .65)
            s.text(x + 205, iy + 196, "參考樹", "s", "middle")
        s.circle(x + cw - 30, y0 + 32, 18, "on", "stgap", 2.5)
        s.text(x + cw - 30, y0 + 41, "?", "big", "middle", "stgap")
        s.text(cx, y0 + 370, q, "h", "middle")
        s.text(cx, y0 + 408, sub, "s", "middle")
        s.text(cx, y0 + 450, f"→ 第 {pno(target)} 頁", "s", "middle", "hp1")
    tag(s, 1110, 26, "示意", "demo")

    notes = ("這週要回答四件事，一格一件。"
             "第一格，參考樹怎麼來：左邊是選殖株的試管和單細胞，怎麼變成右邊這棵樹。"
             "第二格，論文怎麼說：兩篇論文對 SNV 落在 HP1 還是 HP2 有什麼說法，這決定模擬器的 HP 比例。"
             "第三格，模擬有沒有差：上面是已知的真值樹，下面兩棵是重建結果，左邊加 HP、右邊不加，看哪一棵比較接近真值。"
             "第四格，HG008 能不能比：從 bulk 重建一棵樹，就是左下虛線這棵，再和右邊的參考樹比較。"
             "每格下方寫了結果在哪一頁。右上角標了示意，這些圖都只是示意。接下來先從第一格，參考樹怎麼來開始。")
    title = "這週回答四件事：參考樹、論文、模擬、HG008"
    write_page(pid, page(pid, title, s, "", notes))


if __name__ == "__main__":
    p_outline()
    p_tasks()
