"""Slide outline (2026-11-04 deck): week outline rebuilt from pages 2-12. Top band = purpose and the three
requests of the 10-28 meeting with their status; below, four sections in page order, one row per page.
User comment 2026-11-02 ("依照 2 到最後頁數，來設計這周大綱"). Run: python3 gen_p1.py (writes project/slides/outline.html)."""
from pathlib import Path

OUT = Path(__file__).parent / "project" / "slides" / "outline.html"
F = "Noto Sans TC, Arial, sans-serif"
P = "font-family:'Noto Sans TC', Arial, sans-serif"
INK, SUB, BLUE, ORANGE, LINE, BG = "#1F2A37", "#6B7480", "#2F6DB5", "#C96A1B", "#E3E1DA", "#F7F6F2"
HP1, HP1S, HP2, HP0, RED, GREY = "#2C5F9E", "#8FB3E0", "#D9772B", "#9AA3AE", "#D23A2E", "#4A5568"
BAND = "#D6E3F3"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=24, weight=400, fill=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{F}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def rect(x, y, w, h, fill="#FFFFFF", stroke=LINE, sw=2, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def machine(x, y, s, col=BLUE, plain=False):
    inner = (f'<rect x="18" y="24" width="36" height="6" rx="3" fill="#C3CAD3"/>' if plain else
             f'<rect x="14" y="24" width="14" height="6" rx="3" fill="{HP1}"/><rect x="30" y="24" width="14" height="6" rx="3" fill="{HP2}"/>'
             f'<rect x="46" y="24" width="12" height="6" rx="3" fill="{HP0}"/>')
    return (f'<g transform="translate({x},{y}) scale({s})"><polygon points="20,2 52,2 44,14 28,14" fill="{col}"/>'
            f'<rect x="6" y="14" width="60" height="34" rx="6" fill="{col}"/>{inner}'
            f'<rect x="24" y="48" width="24" height="6" fill="#C3CAD3"/></g>')


def status(cx, cy, ok):
    if ok:
        return (f'<circle cx="{cx}" cy="{cy}" r="16" fill="{BLUE}"/>'
                f'<polyline points="{cx - 7},{cy} {cx - 2},{cy + 6} {cx + 8},{cy - 6}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<circle cx="{cx}" cy="{cy}" r="16" fill="{ORANGE}"/>'
            f'<line x1="{cx - 6}" y1="{cy - 6}" x2="{cx + 6}" y2="{cy + 6}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>'
            f'<line x1="{cx + 6}" y1="{cy - 6}" x2="{cx - 6}" y2="{cy + 6}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>')


def arrow(x1, y, x2, col=INK, w=4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y}" x2="{x2 - 14}" y2="{y}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>'
            f'<polygon points="{x2},{y} {x2 - 14},{y - 8} {x2 - 14},{y + 8}" fill="{col}"/>')


W, H = 1664, 540
s = ""

# ---- top band: purpose + last meeting's three requests ----
s += rect(1, 1, W - 2, 112, fill="#FFFFFF")
s += t(24, 46, "目的", 24, 700, BLUE)
s += machine(84, 14, 0.75)
s += arrow(146, 36, 186)
for i, (col, alt) in enumerate(((HP1S, True), (HP1, False), (HP2, False))):
    yy = 22 + i * 14
    s += f'<line x1="{196 + i * 8}" y1="{yy}" x2="{286 + i * 8}" y2="{yy}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>'
    if alt:
        s += f'<circle cx="{240 + i * 8}" cy="{yy}" r="6" fill="{RED}"/>'
s += t(316, 46, "帶 HP1／HP2 的 long read bulk", 24, 700, INK)
s += arrow(686, 36, 730, HP0, 3, "6 5")
s += t(740, 46, "之後測 PhyClone 的 HP 擴充", 24, 400, SUB)
s += f'<line x1="24" y1="64" x2="{W - 24}" y2="64" stroke="{LINE}" stroke-width="2"/>'
s += t(24, 98, "10-28 會議要求", 24, 700, INK)
reqs = ((True, "說清楚改了什麼", "p2–p7"), (False, "先比 2–3 個方案再選", "這版未放"), (True, "用流程圖呈現思考", "每頁主圖"))
x = 228
for ok, label, where in reqs:
    s += status(x, 90, ok)
    s += t(x + 26, 98, label, 24, 700, INK)
    lw = 24 * len(label.replace(" ", "")) - 10 * label.count("–")
    s += t(x + 34 + lw, 98, where, 24, 400, BLUE if ok else ORANGE)
    x += 34 + lw + 24 * 5 + 40

# ---- four sections in page order ----
SECS = [
    ("1", "兩台機器", "diplosim 比 CONIPHER 多了什麼", "p2–p7",
     [("p2", "8 個旋鈕分 5 組"), ("p3", "SNV 落在哪條 allele"), ("p4", "read 的 HP 標記比例"),
      ("p5", "鹼基讀錯、HP 標錯"), ("p6", "同位置第二個 CN 事件"), ("p7", "兩台機器的輸出差異")]),
    ("2", "怎麼檢查", "用真實 HCC1395 long read", "p8–p10",
     [("p8", "先比 bulk，樹之後"), ("p9", "5 種 purity 混合"), ("p10", "12 項數值分 6 類")]),
    ("3", "結果", "真實對 diplosim", "p11",
     [("p11", "5 個數值，3 個全對上")]),
    ("4", "懂／不懂", "已確認與還沒處理", "p12",
     [("p12", "樹、phase block 未驗")]),
]
WID = [496, 396, 364, 348]
GAP = 20
x0, y0, hh = 0, 132, H - 132
for (num, name, ask, pages, rows), w in zip(SECS, WID):
    s += rect(x0 + 1, y0, w - 2, hh - 1)
    s += f'<rect x="{x0 + 1}" y="{y0}" width="10" height="{hh - 1}" rx="4" fill="{BLUE}"/>'
    s += f'<circle cx="{x0 + 44}" cy="{y0 + 40}" r="20" fill="{BLUE}"/>' + t(x0 + 44, y0 + 49, num, 24, 700, "#FFFFFF", "middle")
    s += t(x0 + 76, y0 + 49, name, 30, 700, INK)
    s += rect(x0 + w - 136, y0 + 20, 116, 38, stroke=BLUE, rx=19) + t(x0 + w - 78, y0 + 47, pages, 24, 700, BLUE, "middle")
    s += t(x0 + 28, y0 + 90, ask, 24, 400, SUB)
    # icon strip
    iy = y0 + 112
    if num == "1":
        s += machine(x0 + 40, iy, 1.1, GREY, plain=True) + t(x0 + 80, iy + 88, "CONIPHER", 20, 700, GREY, "middle")
        s += arrow(x0 + 132, iy + 32, x0 + 182, INK, 3)
        s += machine(x0 + 196, iy, 1.1) + t(x0 + 236, iy + 88, "diplosim", 20, 700, BLUE, "middle")
        for k in range(4):  # knobs
            cx = x0 + 330 + k * 44
            s += f'<line x1="{cx}" y1="{iy + 8}" x2="{cx}" y2="{iy + 64}" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
            s += f'<circle cx="{cx}" cy="{iy + 16 + (k * 13) % 44}" r="10" fill="{BLUE}"/>'
    elif num == "2":
        for k, tum in enumerate((100, 70, 48, 29, 14)):
            yy = iy + 4 + k * 16
            tw = 200 * tum / 100
            s += f'<rect x="{x0 + 32}" y="{yy}" width="{tw:.0f}" height="12" rx="3" fill="{INK}"/>'
            if tum < 100:
                s += f'<rect x="{x0 + 32 + tw:.0f}" y="{yy}" width="{200 - tw:.0f}" height="12" rx="3" fill="#D5D2C9"/>'
        s += t(x0 + 252, iy + 36, "tumor＋", 20, 400, SUB) + t(x0 + 252, iy + 62, "normal", 20, 400, SUB)
    elif num == "3":
        bx, by = x0 + 32, iy + 4
        s += f'<polygon points="{bx},{by + 10} {bx + 280},{by + 62} {bx + 280},{by + 76} {bx},{by + 30}" fill="{BAND}"/>'
        s += f'<line x1="{bx}" y1="{by + 20}" x2="{bx + 280}" y2="{by + 69}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 6"/>'
        s += f'<polyline points="{bx},{by + 18} {bx + 93},{by + 38} {bx + 186},{by + 52} {bx + 280},{by + 70}" fill="none" stroke="{ORANGE}" stroke-width="3"/>'
        for px, py in ((bx, by + 18), (bx + 93, by + 38), (bx + 186, by + 52), (bx + 280, by + 70)):
            s += f'<circle cx="{px}" cy="{py}" r="6" fill="{ORANGE}"/>'
    else:
        s += status(x0 + 52, iy + 28, True) + t(x0 + 80, iy + 36, "已確認", 24, 700, BLUE)
        s += (f'<circle cx="{x0 + 52}" cy="{iy + 72}" r="16" fill="{ORANGE}"/>' + t(x0 + 52, iy + 81, "?", 24, 700, "#FFFFFF", "middle")
              + t(x0 + 80, iy + 80, "還不確定", 24, 700, ORANGE))
    # one row per page
    ry = y0 + 226
    for pg, txt in rows:
        s += t(x0 + 28, ry, pg, 24, 700, BLUE) + t(x0 + 90, ry, txt, 24, 400, INK)
        ry += 34
    x0 += w + GAP

aria = ("本週大綱。上方：目的是用 diplosim 產生帶 HP1、HP2 的 long read bulk，之後測 PhyClone 的 HP 擴充；10-28 會議三項要求："
        "說清楚改了什麼見 p2 到 p7，先比 2 到 3 個方案再選這版未放，用流程圖呈現思考見每頁主圖。下方 4 段：1 兩台機器 p2 到 p7；"
        "2 怎麼檢查 p8 到 p10；3 結果 p11；4 懂與不懂 p12，每頁一行寫這頁講什麼")
svg = f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="{aria}" viewBox="0 0 {W} {H}" style="width:{W}px; height:{H}px">{s}</svg>'

notes = ("這週要回答兩個問題：diplosim 比 CONIPHER 多輸出哪些 long read 資訊，以及怎麼檢查它接近真實資料。"
         "最上面先接回上次會議：目的是用 diplosim 產生帶 HP1、HP2 的 long read bulk，之後拿來測 PhyClone 的 HP 擴充。"
         "上次三項要求裡，說清楚改了什麼在第 2 到第 7 頁，流程圖在每頁的主圖；先比方案再選，這一版沒有放。"
         "下面照頁序分 4 段。第 1 段第 2 到第 7 頁，比兩台機器：8 個旋鈕分 5 組，每組一頁，最後比輸出。"
         "第 2 段第 8 到第 10 頁，講怎麼用 5 種 purity 的真實 HCC1395 long read 檢查，以及 12 項數值怎麼分類。"
         "第 3 段第 11 頁是結果：真實和 diplosim 放在同一張圖比。第 4 段第 12 頁整理已確認和還沒處理的事。")

html = f'''<section id="outline" style="display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2; font-family:'Noto Sans TC', Arial, sans-serif; color:#1f2a37">
  <p style="{P}; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5">本週大綱</p>
  <h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37">diplosim 比 CONIPHER 多輸出哪些 long read 資訊？怎麼檢查它接近真實資料？</h2>
  {svg}
  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">
    <p style="{P}; font-size:24px; color:#6b7480">2026-11-04 diplosim：兩台機器與真實 long read</p>
    <p style="{P}; font-size:24px; color:#6b7480">2 / 13</p>
  </div>
  <aside>{notes}</aside>
</section>
'''
OUT.write_text(html)
print(OUT)
