"""把 CLAUDE.md 的工作流程畫成一張泳道圖 SVG（一列一種任務，每個節點一個圖示加短標籤）。

用法：python3 tools/draw_claude_md_workflow.py [輸出路徑]
預設輸出 report/claude_md_workflow/claude_md_workflow.svg。CLAUDE.md 改了就要手動更新這裡。
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "report/claude_md_workflow/claude_md_workflow.svg"

W, H = 1400, 0
FONT = "'Noto Sans TC','PingFang TC','Microsoft JhengHei',sans-serif"
C = dict(bg="#f6f7f9", ink="#1d2433", muted="#6b7385", line="#9aa2b3", frame="#d5d9e2", band="#eceff5")
# 節點種類：(底色, 圖示色)
K = dict(step=("#e3eafc", "#3b5bdb"), stop=("#fde4e4", "#c92a2a"), dec=("#ffefd6", "#d9822b"), rule=("#e2f3e9", "#2b8a5a"))

out = []
add = out.append


def text(x, y, s, size=14, weight=700, fill=None, anchor="middle"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill or C["ink"]}" text-anchor="{anchor}">{escape(s)}</text>')


def arrow(pts, dash=False):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    da = ' stroke-dasharray="5 4"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{C["line"]}" stroke-width="2"{da} marker-end="url(#arr)"/>')


def tag(x, y, label):
    w = 10 + sum(8 if ord(ch) < 128 else 13 for ch in label)
    add(f'<rect x="{x - w/2}" y="{y - 9}" width="{w}" height="18" rx="9" fill="{C["ink"]}"/>')
    text(x, y + 4, label, size=11, fill=C["bg"])


# ---- 圖示：以 (cx, cy) 為中心，約 36×36，c 是線條色 ----
def g(c, body):
    return f'<g fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{body}</g>'


def i_doc(x, y, c, extra=""):
    return g(c, f'<path d="M{x-11},{y-15} h15 l7,7 v23 h-22 z"/><path d="M{x-6},{y-3} h12 M{x-6},{y+3} h12 M{x-6},{y+9} h8"/>{extra}')


def i_check(x, y, c):
    return g(c, f'<path d="M{x-14},{y-8} l4,4 l7,-7"/><path d="M{x+2},{y-6} h12"/>'
                f'<path d="M{x-13},{y+5} l6,6 M{x-7},{y+5} l-6,6"/><path d="M{x+2},{y+8} h12"/>')


def i_fork(x, y, c):
    return g(c, f'<path d="M{x-14},{y} h10 M{x-4},{y} q6,0 10,-10 h6 M{x-4},{y} q6,0 10,10 h6"/>'
                f'<circle cx="{x+15}" cy="{y-10}" r="2.5" fill="{c}"/><circle cx="{x+15}" cy="{y+10}" r="2.5" fill="{c}"/>')


def i_cards(x, y, c):
    return g(c, f'<rect x="{x-15}" y="{y-12}" width="18" height="24" rx="3"/><rect x="{x-7}" y="{y-14}" width="18" height="24" rx="3" fill="#fff"/>'
                f'<rect x="{x+1}" y="{y-10}" width="14" height="22" rx="3" fill="#fff"/>')


def i_stop(x, y, c):
    pts = " ".join(f"{x + 16*dx},{y + 16*dy}" for dx, dy in [(-.41, -1), (.41, -1), (1, -.41), (1, .41), (.41, 1), (-.41, 1), (-1, .41), (-1, -.41)])
    return f'<polygon points="{pts}" fill="{c}"/><rect x="{x-8}" y="{y-2.5}" width="16" height="5" rx="2" fill="#fff"/>'


def i_gear(x, y, c):
    return f'<circle cx="{x}" cy="{y}" r="13" fill="none" stroke="{c}" stroke-width="6" stroke-dasharray="5 4.2"/>' + \
        g(c, f'<circle cx="{x}" cy="{y}" r="9"/><circle cx="{x}" cy="{y}" r="3.5"/>')


def i_one(x, y, c):
    return g(c, f'<path d="M{x-16},{y+12} h10 v-8 h10 v-8 h10 v-8"/>') + \
        f'<circle cx="{x-11}" cy="{y+12}" r="4" fill="{c}"/>'


def i_bubble(x, y, c):
    return g(c, f'<path d="M{x-15},{y-12} h30 v19 h-18 l-7,7 v-7 h-5 z"/><path d="M{x-9},{y-5} h18 M{x-9},{y+1} h11"/>')


def i_bulb(x, y, c):
    return g(c, f'<path d="M{x-6},{y+8} q-10,-6 -10,-14 a10,10 0 1 1 20,0 q0,8 -10,14 z"/><path d="M{x-5},{y+12} h10 M{x-3},{y+16} h6"/>'
                f'<path d="M{x-4},{y-6} l3,3 l6,-6"/>')


def i_chart(x, y, c):
    return g(c, f'<path d="M{x-15},{y+14} h30"/>') + \
        "".join(f'<rect x="{x-12 + i*9}" y="{y+14-h}" width="6" height="{h}" rx="1" fill="{c}"/>' for i, h in enumerate([10, 18, 26]))


def i_back(x, y, c):
    return g(c, f'<path d="M{x+14},{y+12} v-8 a10,10 0 0 0 -10,-10 h-16"/><path d="M{x-6},{y-12} l-6,6 l6,6"/>')


def i_flask(x, y, c):
    return g(c, f'<path d="M{x-5},{y-15} v10 l-10,17 q-2,4 3,4 h24 q5,0 3,-4 l-10,-17 v-10 M{x-8},{y-15} h16"/>') + \
        f'<path d="M{x-11},{y+8} h22 l2,4 q1,4 -3,4 h-20 q-4,0 -3,-4 z" fill="{c}"/>'


def i_target(x, y, c):
    return g(c, f'<circle cx="{x}" cy="{y}" r="15"/><circle cx="{x}" cy="{y}" r="9"/>') + f'<circle cx="{x}" cy="{y}" r="3.5" fill="{c}"/>'


def i_clip(x, y, c):
    return g(c, f'<rect x="{x-13}" y="{y-13}" width="26" height="30" rx="3"/><rect x="{x-6}" y="{y-17}" width="12" height="7" rx="2" fill="#fff"/>'
                f'<path d="M{x-8},{y-2} l3,3 l5,-5 M{x-8},{y+9} l3,3 l5,-5 M{x+3},{y} h5 M{x+3},{y+11} h5"/>')


def i_cal(x, y, c):
    return g(c, f'<rect x="{x-15}" y="{y-11}" width="30" height="27" rx="3"/><path d="M{x-15},{y-3} h30 M{x-8},{y-16} v8 M{x+8},{y-16} v8"/>') + \
        f'<rect x="{x-9}" y="{y+3}" width="6" height="6" fill="{c}"/>'


def i_findfile(x, y, c):
    return g(c, f'<path d="M{x-16},{y-10} h10 l3,4 h13 v18 h-26 z"/><circle cx="{x+9}" cy="{y+9}" r="6" fill="#fff"/><path d="M{x+13},{y+13} l5,5"/>')


def i_edit(x, y, c):
    return i_doc(x - 3, y, c, f'<path d="M{x+4},{y+13} l13,-13 l4,4 l-13,13 h-4 z" fill="#fff"/>')


def i_code(x, y, c):
    return g(c, f'<path d="M{x-8},{y-10} l-9,10 l9,10 M{x+8},{y-10} l9,10 l-9,10 M{x+3},{y-13} l-6,26"/>')


def i_tag(x, y, c):
    return g(c, f'<path d="M{x-15},{y-13} h16 l14,13 l-14,13 h-16 z"/><circle cx="{x-8}" cy="{y}" r="3"/>')


def i_search(x, y, c):
    return g(c, f'<circle cx="{x-4}" cy="{y-4}" r="11"/><path d="M{x+4},{y+4} l10,10"/><path d="M{x-10},{y+2} l12,-12"/>')


def i_podium(x, y, c):
    return f'<rect x="{x-16}" y="{y}" width="10" height="14" fill="{c}"/><rect x="{x-5}" y="{y-12}" width="10" height="26" fill="{c}"/>' \
           f'<rect x="{x+6}" y="{y+5}" width="10" height="9" fill="{c}"/>'


def i_four(x, y, c):
    return "".join(f'<rect x="{x-19 + i*10}" y="{y-4}" width="7" height="8" rx="1.5" fill="{c}"/>' for i in range(4)) + \
        g(c, f'<path d="M{x-17},{y-12} h34 M{x+13},{y-15} l4,3 l-4,3"/>')


def i_pencil(x, y, c):
    return g(c, f'<circle cx="{x-10}" cy="{y-9}" r="4"/><circle cx="{x+10}" cy="{y-9}" r="4"/><path d="M{x-6},{y-9} h12"/>'
                f'<path d="M{x-12},{y+16} l3,-8 l14,-14 l5,5 l-14,14 z"/>')


def i_han(x, y, c):
    return f'<text x="{x}" y="{y+8}" font-size="24" font-weight="700" fill="{c}" text-anchor="middle">中</text>'


def i_short(x, y, c):
    return g(c, f'<path d="M{x-14},{y-9} h28 M{x-14},{y} h18 M{x-14},{y+9} h10"/>')


def i_slide(x, y, c):
    return g(c, f'<rect x="{x-16}" y="{y-12}" width="32" height="22" rx="2"/><path d="M{x},{y+10} v6 M{x-7},{y+16} h14"/>') + \
        f'<path d="M{x-4},{y-6} l9,5 l-9,5 z" fill="{c}"/>'


def i_play(x, y, c):
    return f'<path d="M{x-9},{y-13} l22,13 l-22,13 z" fill="{c}"/>'


def i_down(x, y, c):
    return g(c, f'<path d="M{x},{y-14} v26 M{x-9},{y+4} l9,9 l9,-9"/>')


def i_loop(x, y, c):
    return g(c, f'<path d="M{x+12},{y-6} a13,13 0 1 0 1,10"/><path d="M{x+14},{y-16} v10 h-10"/>')


def node(x, y, icon, label, kind="step", r=30):
    fill, c = K[kind]
    if kind == "dec":
        s = r + 7
        add(f'<polygon points="{x},{y-s} {x+s},{y} {x},{y+s} {x-s},{y}" fill="{fill}" stroke="{c}" stroke-width="2"/>')
    else:
        add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="2"/>')
    add(icon(x, y, c))
    text(x, y + r + (26 if kind == "dec" else 22), label, size=15)


def link(x1, x2, y, label=None, k1="step", k2="step"):
    """同一列左右相連；k1/k2 決定節點邊緣（菱形較寬）。"""
    e = lambda k: 37 if k == "dec" else 30
    arrow([(x1 + e(k1), y), (x2 - e(k2) - 3, y)])
    if label:
        text((x1 + x2) / 2, y - 8, label, size=13, fill=C["muted"])


def branch(xd, xb, a, b, label):
    """菱形的「否」分支：從左角繞到下排，避開菱形下方的標籤。"""
    arrow([(xd - 37, a), (xd - 76, a), (xd - 76, b), (xb - 33, b)])
    text(xd - 68, (a + b) / 2 + 18, label, size=13, fill=C["muted"], anchor="start")


# ---- 標題、圖例 ----
text(40, 40, "CLAUDE.md 工作流程", size=24, anchor="start")
text(300, 40, "一列一種任務．由左往右走", size=14, weight=400, fill=C["muted"], anchor="start")
for i, (k, lab) in enumerate([("step", "步驟"), ("dec", "判斷"), ("stop", "停．交給你"), ("rule", "檢查項目")]):
    fill, c = K[k]
    x = 930 + i * 110
    add(f'<circle cx="{x}" cy="34" r="9" fill="{fill}" stroke="{c}" stroke-width="2"/>')
    text(x + 16, 39, lab, size=13, weight=400, fill=C["muted"], anchor="start")

# ---- 永遠適用 ----
add(f'<rect x="40" y="58" width="1320" height="62" rx="12" fill="{C["band"]}"/>')
text(70, 95, "任何回覆", size=15, anchor="start")
for i, (ic, lab) in enumerate([(i_han, "繁中"), (i_short, "短句、結論先寫"), (i_bubble, "問是什麼→先短答")]):
    x = 300 + i * 340
    add(f'<circle cx="{x}" cy="89" r="22" fill="#fff" stroke="{C["frame"]}" stroke-width="1.5"/>')
    add(ic(x, 89, C["ink"]))
    text(x + 34, 95, lab, size=15, anchor="start")

# ---- 泳道 ----
X = [380, 525, 670, 815, 960, 1105, 1250]
# 每列附一個任務例子，說明不同工作走不同流程
lanes = [
    ("任何任務", "開工第一步", i_play, 218, i_clip, "例：做 diplosim 下一步"),
    ("改設計", "怎麼改、怎麼驗證", i_gear, 130, i_flask, "例：模擬器加 WGD"),
    ("評估資料", "benchmark 資料集", i_findfile, 218, i_search, "例：HG008 能當驗證嗎"),
    ("評估程式", "開源工具、模擬器", i_code, 218, i_target, "例：CONIPHER 能沿用嗎"),
    ("寫回答／文件", "每次都對照", i_pencil, 120, i_bubble, "例：解釋 CCF 怎麼算"),
    ("做報告", "投影片、週報", i_slide, 120, i_chart, "例：準備週會投影片"),
    ("開完會", "更新規則", i_cal, 120, i_edit, "例：10-28 會後改規則"),
]
top = 140
tops = []
for n, (name, sub, ic, h, ex_ic, ex) in enumerate(lanes, 1):
    tops.append(top)
    add(f'<rect x="40" y="{top}" width="1320" height="{h}" rx="14" fill="#fff" stroke="{C["frame"]}" stroke-width="1.5"/>')
    add(f'<path d="M54,{top} h216 v{h} h-216 a14,14 0 0 1 -14,-14 v-{h-28} a14,14 0 0 1 14,-14 z" fill="{C["band"]}"/>')
    add(f'<circle cx="84" cy="{top+50}" r="24" fill="#fff" stroke="{C["frame"]}" stroke-width="1.5"/>')
    add(ic(84, top + 50, C["ink"]))
    text(120, top + 47, f"{n}  {name}", size=17, anchor="start")
    text(120, top + 68, sub, size=12, weight=400, fill=C["muted"], anchor="start")
    add(f'<rect x="60" y="{top+82}" width="202" height="26" rx="13" fill="#fff" stroke="{C["frame"]}" stroke-width="1"/>')
    add(f'<g transform="translate(78 {top+95}) scale(0.45) translate(-78 {-(top+95)})">{ex_ic(78, top + 95, C["muted"])}</g>')
    text(94, top + 99, ex, size=12, weight=400, fill=C["ink"], anchor="start")
    top += h + 12

# 1 任何任務
A = tops[0] + 52; B = A + 100
node(X[0], A, i_doc, "讀最新會議")
link(X[0], X[1], A, k2="dec")
node(X[1], A, i_check, "在待辦內？", kind="dec")
link(X[1], X[2], A, "是", k1="dec")
node(X[2], A, i_down, "走下面對應的列")
branch(X[1], X[2], A, B, "否")
node(X[2], B, i_bubble, "先提議，等同意", kind="stop")

# 2 改設計
A = tops[1] + 60
node(X[0], A, i_cards, "列 2–3 個方案")
link(X[0], X[1], A, k2="stop")
node(X[1], A, i_stop, "等你選", kind="stop")
link(X[1], X[2], A)
node(X[2], A, i_one, "一次只做一步")
link(X[2], X[3], A)
node(X[3], A, i_bubble, "白話說明改了什麼")
link(X[3], X[4], A, k2="dec")
node(X[4], A, i_bulb, "你看懂了？", kind="dec")
link(X[4], X[5], A, "是", k1="dec")
node(X[5], A, i_loop, "下一個決策")
arrow([(X[4], A - 37), (X[4], tops[1] + 10), (X[3], tops[1] + 10), (X[3], A - 33)], dash=True)
text((X[3] + X[4]) / 2, tops[1] + 24, "否：再解釋", size=13, fill=C["muted"])

# 3 評估資料
A = tops[2] + 52; B = A + 100
node(X[0], A, i_check, "符合需求表？", kind="dec")
link(X[0], X[1], A, "是", k1="dec")
node(X[1], A, i_podium, "benchmark 寫 4 項")
link(X[1], X[2], A)
node(X[2], A, i_fork, "列出全部驗證路徑")
link(X[2], X[3], A)
node(X[3], A, i_bubble, "寫選擇理由")
branch(X[0], X[1], A, B, "否")
node(X[1], B, i_stop, "排除，寫違反哪條", kind="stop")

# 4 評估程式
A = tops[3] + 52; B = A + 100
node(X[0], A, i_check, "符合需求表？", kind="dec")
link(X[0], X[1], A, "是", k1="dec")
node(X[1], A, i_code, "先讀程式")
link(X[1], X[2], A)
node(X[2], A, i_doc, "寫產生什麼、缺什麼")
link(X[2], X[3], A)
node(X[3], A, i_bubble, "寫選擇理由")
branch(X[0], X[1], A, B, "否")
node(X[1], B, i_stop, "排除，寫違反哪條", kind="stop")

# 5 寫回答／文件（沒有順序，每次都對照）
A = tops[4] + 50
for x, ic, lab in zip(X, [i_tag, i_search, i_four, i_pencil], ["標來源", "寫搜尋範圍", "寫流程", "先畫圖"]):
    node(x, A, ic, lab, kind="rule")

# 6 做報告
A = tops[5] + 50
# 照報告時講的順序；最後一格是交出前的檢查
steps = [(i_back, "接回上次會議", "step"), (i_flask, "本週 1–3 個任務", "step"), (i_cards, "方案與選擇理由", "step"),
         (i_chart, "結果（含失敗）", "step"), (i_target, "懂／不懂", "step"), (i_clip, "交出前自我檢查", "stop")]
for j, (ic, lab, kind) in enumerate(steps):
    node(X[j], A, ic, lab, kind=kind)
    if j:
        link(X[j - 1], X[j], A)

# 7 開完會
A = tops[6] + 50
for j, (ic, lab) in enumerate([(i_cal, "新會議"), (i_findfile, "確認最新一次"), (i_edit, "更新 CLAUDE.md"), (i_loop, "回到第 1 列")]):
    node(X[j], A, ic, lab)
    if j:
        link(X[j - 1], X[j], A)

H = top + 8

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">'
       f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       f'<path d="M0,0 L10,5 L0,10 z" fill="{C["line"]}"/></marker></defs>'
       f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>' + "".join(out) + "</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(OUT)
