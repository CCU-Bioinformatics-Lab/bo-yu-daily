"""Opening pages of the 2026-11-11 deck: outline (p1), n-fixes (p2), tasks (p3).

python3 gen_open.py  -> project/slides/{outline,n-fixes,tasks}.html
Sketches: sketches/open.md. Every picture here is 示意 except the 14／23 count on p3 (實際結果).
"""
import math

from slidekit import ORDER, S, n3_ladder, page, tag, write_page
from gen_res2 import tube as res_tube


def pno(pid):
    return ORDER.index(pid) + 1


# ---- small pictograms (defined here so slidekit stays untouched) ----

def tick(s, x, y, c="stok", k=1.0):
    s.path(f"M{x - 8 * k:.1f} {y:.1f} L{x - 2 * k:.1f} {y + 6 * k:.1f} L{x + 9 * k:.1f} {y - 7 * k:.1f}", c, 3.5)


def badge(s, x, y, kind):
    """Status stamp: ok (tick), now (arrow, this week), pause (two bars)."""
    edge = {"ok": "stok", "now": "hp1", "pause": "stgap"}[kind]
    s.circle(x, y, 17, "on", edge, 2.5)
    if kind == "ok":
        tick(s, x, y)
    elif kind == "now":
        s.arrow(x - 9, y, x + 10, y, c="hp1", sw=3, head=8)
    else:
        s.rect(x - 7, y - 8, 5, 16, "stgap", r=1)
        s.rect(x + 2, y - 8, 5, 16, "stgap", r=1)


def parent(s, x, y, ch, h=44):
    """Dad / mom: a grey person with 爸 or 媽 under it. Never a color (F-4)."""
    s.person(x, y, h, "panel3", "cellline")
    s.text(x, y + h + 22, ch, "b", "middle")


def reads(s, x, y, cols, w=90, h=8, gap=13):
    for i, c in enumerate(cols):
        s.rect(x + (i % 2) * 10, y + i * gap, w, h, c, r=4)


def tube(s, x, y, w=28, h=78):
    """One 選殖株: the deck's test tube (same as p7, p11), x = left edge."""
    res_tube(s, x + w / 2, y, w=w, h=h)


def mini_tree(s, x, y, sc=1.0, c="line2"):
    """Root on top, one child, two leaves."""
    a, b = (x, y), (x, y + 26 * sc)
    l1, l2 = (x - 20 * sc, y + 52 * sc), (x + 20 * sc, y + 52 * sc)
    for p, q in [(a, b), (b, l1), (b, l2)]:
        s.line(*p, *q, c, 3)
    s.circle(*a, 7 * sc, "normal", "cellline")
    for p, col in [(b, "c1"), (l1, "c2"), (l2, "c3")]:
        s.circle(*p, 8 * sc, col, "cellline")


def gear(s, x, y, r=22):
    pts = []
    for i in range(32):
        a = i * math.pi / 16
        rr = r if (i // 2) % 2 == 0 else r * .74
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    s.poly(pts, "line2")
    s.circle(x, y, r * .35, "on")


def doc(s, x, y, w=44, h=56, lines=4):
    s.rect(x, y, w, h, "on", "cellline", r=4, sw=2)
    for i in range(lines):
        s.line(x + 8, y + 12 + i * 11, x + w - 8, y + 12 + i * 11, "line2", 2.5)


# ---- p1 outline ----
# 2026-11-08 redesign (user): left = key points of the 11-04 meeting (no page numbers),
# right = the two tasks finished this week. The research-purpose row was removed earlier the same day.

def mini_ladder(s, x, y, lit=0):
    """Three stacked steps (觀測特徵 / 克隆結構 / 演化路徑); the lit one is green."""
    for i in range(3):
        s.rect(x, y - i * 14, 46, 11, "c4" if i == lit else "panel3", r=2)


def p_outline():
    pid = "outline"
    s = S(pid, 1200, 440)

    # Left: key points of the last meeting.
    s.rect(10, 6, 520, 428, "panel", r=12)
    s.text(30, 44, "上次會議（11-04）重點", "h")
    rows = [
        ("不模擬 unphased read", "演化中沒有「unphased」這條染色體"),
        ("模擬不過擬合 HCC1395 或其他癌種", ""),
        ("先聚焦單點突變", "先查生物假說，再改模擬器"),
        ("報告加 AI 環境改善", "記錄改了哪些工作規則"),
    ]
    for i, (head, sub) in enumerate(rows):
        y = 74 + i * 90
        cx = 72
        if i == 0:
            reads(s, cx - 42, y + 14, ["hp1", "hp2", "unphased"], w=72, h=8, gap=15)
            s.xmark(cx + 44, y + 44, 8)
        elif i == 1:
            s.text(cx, y + 54, "≈", "big", "middle")
        elif i == 2:
            s.bar(cx - 42, y + 36, 84, "hp1", 14)
            s.star(cx, y + 36, 10)
        else:
            doc(s, cx - 18, y + 12, w=36, h=48)
        s.text(140, y + 36, head, "b")
        s.text(140, y + 64, sub, "s")

    # Middle arrow: this week.
    s.arrow(540, 220, 600, 220, c="hp1", sw=5, head=14)
    s.text(570, 202, "本週", "b", "middle", "hp1")

    # Right: the two tasks finished this week.
    s.text(620, 44, "這星期完成的任務", "h")
    cards = [
        ("SNV 落在哪條的證據", ["8 株細胞株：兩條份數相同時", "HP1、HP2 接近各半", "整理假說，列出模擬器 3 個方案"]),
        ("克隆結構的獨立驗證資料", ["HG008：8 株選殖株＋119 顆單細胞", "盤點資源：各自能提供什麼"]),
    ]
    for j, (head, lines) in enumerate(cards):
        y0 = 66 + j * 186
        s.rect(610, y0, 580, 170, "paper", "line", r=12, sw=1.5)
        badge(s, 1158, y0 + 30, "ok")
        if j == 0:
            s.bar(632, y0 + 70, 120, "hp1", 14)
            s.bar(632, y0 + 100, 120, "hp2", 14)
            for x in (662, 722):
                s.star(x, y0 + 70, 10)
            s.star(692, y0 + 100, 10)
        else:
            for k in range(3):
                tube(s, 628 + k * 26, y0 + 50, 18, 56)
            for k in range(4):
                s.circle(718 + (k % 2) * 18, y0 + 62 + (k // 2) * 20, 7, "on", "cellline", 1.6)
        s.text(780, y0 + 38, head, "b")
        for k, ln in enumerate(lines):
            s.text(780, y0 + 74 + k * 28, ln, "s")

    notes = ("這週要回答的主問題，就是標題這句：單點突變階段的模擬，有哪些證據支持、能用什麼驗證。"
             "左邊是上次會議的四個重點：不模擬 unphased read，因為演化中沒有「unphased」這條染色體，每條 read 都來自 HP1 或 HP2；模擬結果不應該過擬合 HCC1395 或其他癌種；"
             "先聚焦單點突變，先查假說再改模擬器；報告加 AI 環境改善。"
             "右邊是這星期完成的兩個任務。第一個是 SNV 落在哪條的證據：8 株細胞株在兩條份數相同時接近各半，也整理了假說和模擬器的三個方案。"
             "第二個是克隆結構的獨立驗證資料：盤點 HG008 有哪些資源、各自能提供什麼。")
    title = "單點突變階段的模擬，有哪些證據支持、能用什麼驗證？"
    write_page(pid, page(pid, title, s, "", notes))


# ---- p2 n-fixes ----

def p_fixes():
    pid = "n-fixes"
    s = S(pid, 1200, 434)
    s.text(300, 28, "上次的問題", "h", "middle")
    s.text(870, 28, "這週的做法", "h", "middle")
    heights = [78, 78, 78, 78, 78]
    rows = [
        ("模擬也做了沒分組的 read", "混了真值和觀測限制", "每條 read 只屬 HP1 或 HP2", "沒分組的 read 從模擬器移除"),
        ("直接加 50% 隨機參數", "沒先查生物假說", "先查假說，再改程式", "寫成標來源的知識文件"),
        ("BAM 像真實資料就當驗證", "不同路徑可得到相似資料", "暫時想不到驗證方法", "BAM 相似不能證明演化對"),
        ("一次加 CNA、LOH、多倍體", "看不出哪個設定合理", "一次一個機制", "先做單點突變"),
        ("只叫 AI 給 2–3 個選項", "前提錯，選項全偏", "研究目標寫進專案知識", "AI 列方案前先對照目標"),
    ]
    y = 44
    for i, (h, (p1, p2, f1, f2)) in enumerate(zip(heights, rows)):
        yc = y + h / 2
        s.rect(10, y + 3, 1180, h - 6, "panel" if i % 2 == 0 else "paper", r=8)
        # problem pictogram (x 30-190) and fix pictogram (x 620-830)
        if i == 0:
            reads(s, 55, yc - 22, ["hp1", "hp2", "unphased"], w=95, h=9, gap=16)
            reads(s, 650, yc - 22, ["hp1", "hp2"], w=95, h=9, gap=16)
            s.rect(660, yc + 10, 95, 9, None, "unphased", r=4, dash=True)
            s.xmark(780, yc + 14, 9)
        elif i == 1:
            s.rect(70, yc - 24, 48, 48, "on", "ink2", r=8, sw=2)
            for dx, dy in [(-12, -12), (0, 0), (12, 12)]:
                s.circle(94 + dx, yc + dy, 4, "ink2")
            s.text(132, yc + 7, "50%", "n")
            doc(s, 640, yc - 28)
            s.arrow(692, yc, 728, yc)
            s.rect(740, yc - 24, 70, 48, "on", "ink2", r=6, sw=2)
            s.text(775, yc + 7, "程式", "s", "middle")
        elif i == 2:
            for k, dx in enumerate((45, 125)):
                for r in range(4):
                    s.rect(dx + (r % 2) * 6, yc - 26 + r * 12, 50, 7, "panel3", r=3)
                s.star(dx + 28, yc - 22 + (1 + k) * 12, 6)
            s.text(110, yc + 8, "≈", "big", "middle")
            # 2026-11-08 (user): the three-layer ladder was replaced; no validation method yet.
            s.circle(700, yc, 24, "on", "stgap", 3)
            s.text(700, yc + 11, "?", "big", "middle", "stgap")
        elif i == 3:
            s.bar(45, yc - 14, 140, "hp1", 12)
            s.star(70, yc - 14, 8)
            for k in range(3):
                s.rect(95 + k * 30, yc + 2, 26, 16, "c2", r=8)
                s.rect(95 + k * 30, yc - 22, 26, 16, "c3", r=8)
            s.circle(655, yc, 18, "hl", "hp1", 2.5)
            s.star(655, yc, 10)
            for k in range(3):
                s.arrow(675 + k * 50, yc, 700 + k * 50, yc, c="line2", sw=2)
                s.circle(718 + k * 50, yc, 14, None, "line2", 2, dash=True)
        else:
            for k in range(3):
                s.rect(45 + k * 46, yc - 22, 38, 44, "on", "line2", r=4, sw=2)
                s.xmark(64 + k * 46, yc, 8)
            s.circle(660, yc, 24, "on", "mut", 3)
            s.circle(660, yc, 14, "on", "mut", 3)
            s.circle(660, yc, 5, "mut")
            s.arrow(692, yc, 728, yc)
            for k in range(3):
                s.rect(740 + k * 28, yc - 20, 24, 40, "on", "line2", r=4, sw=2)
        s.text(210, yc - 6, p1, "t")
        s.text(210, yc + 22, p2, "s")
        s.arrow(540, yc, 600, yc, c="hp1", sw=3.5, head=11)
        fx = 845
        s.text(fx, yc - 6, f1, "b")
        s.text(fx, yc + 22, f2, "s")
        y += h

    notes = ("這頁看的是上次指出的五個問題，這週各改了什麼；其中驗證方法還沒想到。"
             "第一列，模擬器原本也做了沒分組的 read，混了真值和觀測限制；現在拿掉了，每條 read 只屬 HP1 或 HP2。"
             "第二列，不再直接加 50% 的隨機參數，先查假說、寫成知識文件，再改程式。"
             "第三列，BAM 像真實資料不能當驗證，因為不同的演化路徑可以得到相似的資料；能驗證演化路徑的方法，我們暫時還想不到。"
             "第四列，一次只加一個機制，先做單點突變。第五列，研究目標寫進專案知識，AI 列方案前先對照目標。"
             "照這些做法，這週定了兩個任務，下一頁說明。")
    write_page(pid, page(pid, "上次指出的五個問題：四個已改做法，驗證方法還沒想到", s, "", notes))


# ---- p3 tasks ----

def p_tasks():
    pid = "tasks"
    s = S(pid, 1200, 480)
    s.rect(10, 6, 585, 468, "panel", r=12)
    s.rect(610, 6, 580, 468, "panel", r=12)
    # Left: task 1.
    s.text(30, 46, "任務 1：SNV 落在哪條 HP？", "h")
    tag(s, 480, 46, "示意", "demo")
    s.text(30, 106, "HP1", "b")
    s.text(30, 150, "HP2", "b")
    s.bar(90, 100, 470, "hp1", 22)
    s.bar(90, 144, 470, "hp2", 22)
    for x in (170, 330, 470):
        s.star(x, 100, 13)
    for x in (250, 410):
        s.star(x, 144, 13)
    s.line(30, 186, 575, 186, "line2", 1.5, dash=True)
    s.text(30, 222, "HG008 兩份組裝給同一條染色體的組名", "s")
    s.text(30, 270, "組裝一", "t")
    s.bar(105, 252, 130, "hp1", 14)
    s.bar(105, 278, 130, "hp2", 14)
    s.text(258, 274, "⇄", "big", "middle")
    s.text(290, 270, "組裝二", "t")
    s.bar(365, 252, 130, "hp2", 14)
    s.bar(365, 278, 130, "hp1", 14)
    s.text(30, 336, "23 條染色體中 14 條組名對調", "b")
    tag(s, 340, 336, "實際結果", "real")
    s.text(30, 418, "HP1、HP2 是組名", "t")
    s.text(220, 424, "≠", "big", "middle")
    parent(s, 285, 362, "爸", 58)
    parent(s, 360, 362, "媽", 58)
    # Right: task 2.
    s.text(630, 46, "任務 2：克隆結構的獨立驗證資料", "h")
    s.text(630, 88, "HG008", "b")
    for k, lab in enumerate("ABCDEFGH"):
        x = 648 + k * 66
        tube(s, x, 108, 30, 82)
        s.text(x + 15, 222, lab, "b", "middle")
    s.text(900, 256, "8 株選殖株：分離後各自培養", "t", "middle")
    n = 0
    for r in range(5):
        for c in range(24):
            if n == 119:
                break
            s.circle(668 + c * 20.5, 290 + r * 22, 7.5, "on", "cellline", 1.6)
            n += 1
    s.text(900, 420, "119 顆單細胞", "t", "middle")

    notes = ("本週有兩個任務。先看左邊任務一：SNV 落在哪條 HP。上面藍色是 HP1、橘色是 HP2，紅星是 SNV，這是示意。"
             "要注意，HP1、HP2 只是組名，不等於爸爸媽媽。我們拿 HG008 的兩份組裝比對同一條染色體，23 條染色體中有 14 條的組名是對調的，這是實際結果。"
             "再看右邊任務二：找克隆結構的獨立驗證資料。HG008 有 8 株選殖株，也就是分離後各自培養的細胞株，另外還有 119 顆單細胞。"
             "要回答任務一，先要知道我們看到的 HP 比例是怎麼來的，下一段就從這裡開始。")
    write_page(pid, page(pid, "本週兩個任務：SNV 落在哪條的證據、克隆結構的獨立驗證資料", s, "", notes))


if __name__ == "__main__":
    p_outline()
    p_fixes()
    p_tasks()
