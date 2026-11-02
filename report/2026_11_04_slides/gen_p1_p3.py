import math, pathlib

OUT = pathlib.Path("/bip8_disk/boyu114/main_work/report/2026_11_04_slides/project/slides")
SANS = "Noto Sans TC, Arial, sans-serif"
FOOT_TXT = "2026-11-04 diplosim：兩台機器與真實 long read"


def t(x, y, s, size=24, color="#1F2A37", weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{SANS}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{s}</text>')


def arrow(x1, y1, x2, y2, color, w=4, head=14):
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = -math.sin(ang) * head * 0.55, math.cos(ang) * head * 0.55
    return (f'<line x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<polygon points="{x2},{y2} {bx+px:.1f},{by+py:.1f} {bx-px:.1f},{by-py:.1f}" fill="{color}"/>')


def machine(x, y, s, body, stripes):
    inner = (f'<polygon points="20,2 52,2 44,14 28,14" fill="{body}"/>'
             f'<rect x="6" y="14" width="60" height="34" rx="6" fill="{body}"/>')
    if stripes:
        inner += ('<rect x="14" y="24" width="14" height="6" rx="3" fill="#2C5F9E"/>'
                  '<rect x="30" y="24" width="14" height="6" rx="3" fill="#D9772B"/>'
                  '<rect x="46" y="24" width="12" height="6" rx="3" fill="#9AA3AE"/>')
    else:
        inner += '<rect x="18" y="24" width="36" height="6" rx="3" fill="#C3CAD3"/>'
    inner += '<rect x="24" y="48" width="24" height="6" fill="#C3CAD3"/>'
    return f'<g transform="translate({x},{y}) scale({s})">{inner}</g>'


def footer(n):
    p = "font-family:'Noto Sans TC', Arial, sans-serif; font-size:24px; color:#6b7480"
    return ('  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">\n'
            f'    <p style="{p}">{FOOT_TXT}</p>\n'
            f'    <p style="{p}">{n} / 12</p>\n  </div>\n')


LABEL = "font-family:'Noto Sans TC', Arial, sans-serif; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5"
H2 = "font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37"
SEC = "display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2"

# ---------------------------------------------------------------- p1 outline
BLUE, ORANGE, GRAY = "#2F6DB5", "#C96A1B", "#6B7480"


def badge(cx, cy, kind, color):
    g = f'<circle cx="{cx}" cy="{cy}" r="22" fill="{color}"/>'
    if kind == "check":
        g += f'<polyline points="{cx-10},{cy} {cx-3},{cy+8} {cx+11},{cy-8}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    elif kind == "arrow":
        g += arrow(cx - 11, cy, cx + 12, cy, "#FFFFFF", w=5, head=11)
    elif kind == "x":
        g += (f'<line x1="{cx-8}" y1="{cy-8}" x2="{cx+8}" y2="{cy+8}" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>'
              f'<line x1="{cx+8}" y1="{cy-8}" x2="{cx-8}" y2="{cy+8}" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>')
    elif kind == "pause":
        g += (f'<rect x="{cx-9}" y="{cy-9}" width="6" height="18" fill="#FFFFFF"/>'
              f'<rect x="{cx+3}" y="{cy-9}" width="6" height="18" fill="#FFFFFF"/>')
    return g


def icon(kind, x, cy):
    if kind == "machine":
        return machine(x + 8, cy - 22, 0.8, "#2F6DB5", True)
    if kind == "compare":
        return (f'<rect x="{x}" y="{cy-14}" width="64" height="9" rx="4" fill="#2F6DB5"/>'
                f'<rect x="{x}" y="{cy+5}" width="64" height="9" rx="4" fill="#3B5B7A"/>'
                f'<line x1="{x+70}" y1="{cy-10}" x2="{x+70}" y2="{cy+10}" stroke="#1F2A37" stroke-width="3"/>'
                f'<polygon points="{x+70},{cy-16} {x+65},{cy-8} {x+75},{cy-8}" fill="#1F2A37"/>'
                f'<polygon points="{x+70},{cy+16} {x+65},{cy+8} {x+75},{cy+8}" fill="#1F2A37"/>')
    if kind == "short":
        g = ""
        for i, (dx, dy) in enumerate([(0, -12), (26, -12), (52, -12), (12, 4), (40, 4), (0, 20), (28, 20)]):
            g += f'<rect x="{x+dx}" y="{cy+dy-4}" width="20" height="8" rx="4" fill="#9AA3AE"/>'
        return g
    if kind == "flow":
        g = ""
        for i in range(3):
            g += f'<rect x="{x+i*28}" y="{cy-10}" width="18" height="20" rx="3" fill="none" stroke="#1F2A37" stroke-width="3"/>'
        g += f'<line x1="{x+19}" y1="{cy}" x2="{x+27}" y2="{cy}" stroke="#1F2A37" stroke-width="3"/>'
        g += f'<line x1="{x+47}" y1="{cy}" x2="{x+55}" y2="{cy}" stroke="#1F2A37" stroke-width="3"/>'
        return g
    if kind == "options":
        g = ""
        for i in range(3):
            stroke = "#C96A1B" if i == 1 else "#9AA3AE"
            g += f'<rect x="{x+i*28}" y="{cy-16}" width="22" height="32" rx="4" fill="#FFFFFF" stroke="{stroke}" stroke-width="3"/>'
        g += f'<polyline points="{x+31},{cy+2} {x+37},{cy+9} {x+46},{cy-6}" fill="none" stroke="#C96A1B" stroke-width="3"/>'
        return g
    if kind == "cooccur":
        return (f'<path d="M{x+16},{cy-2} Q{x+40},{cy-26} {x+64},{cy-2}" fill="none" stroke="#C96A1B" stroke-width="3" stroke-dasharray="4 4"/>'
                f'<line x1="{x}" y1="{cy+8}" x2="{x+80}" y2="{cy+8}" stroke="#8FB3E0" stroke-width="8" stroke-linecap="round"/>'
                f'<circle cx="{x+16}" cy="{cy+8}" r="7" fill="#D23A2E"/><circle cx="{x+64}" cy="{cy+8}" r="7" fill="#D23A2E"/>')


rows = [
    ("check", BLUE, "回應", "machine", "說清楚改了什麼", "8 個旋鈕、每組一頁、兩台機器", "p2–p7"),
    ("check", BLUE, "回應", "options", "先比 2–3 個方案再選", "這版沒有放方案比較頁", "—"),
    ("check", BLUE, "回應", "flow", "用流程圖呈現中間思考", "每頁一張主圖", "每頁"),
]

L = ['<rect x="1" y="1" width="838" height="538" rx="16" fill="#FFFFFF" stroke="#E3E1DA" stroke-width="2"/>',
     t(32, 52, "上次（10-28）會議的 3 項要求", 30, "#1F2A37", 700),
     '<rect x="24" y="74" width="792" height="144" rx="12" fill="#F7F6F2"/>',
     t(44, 108, "目的", 26, BLUE, 700),
     machine(63, 116, 1.2, "#2F6DB5", True),
     t(106, 210, "diplosim", 24, BLUE, 700, "middle"),
     arrow(176, 156, 236, 156, "#1F2A37"),
     t(405, 108, "模擬的 long read bulk", 24, "#1F2A37", 700, "middle"),
     t(248, 146, "HP1", 24, "#2C5F9E", 700), t(248, 196, "HP2", 24, "#D9772B", 700),
     '<line x1="310" y1="128" x2="500" y2="128" stroke="#8FB3E0" stroke-width="8" stroke-linecap="round"/>',
     '<circle cx="400" cy="128" r="7" fill="#D23A2E"/>',
     '<line x1="326" y1="146" x2="506" y2="146" stroke="#2C5F9E" stroke-width="8" stroke-linecap="round"/>',
     '<line x1="314" y1="174" x2="494" y2="174" stroke="#D9772B" stroke-width="8" stroke-linecap="round"/>',
     '<line x1="330" y1="192" x2="506" y2="192" stroke="#D9772B" stroke-width="8" stroke-linecap="round"/>',
     '<line x1="524" y1="160" x2="572" y2="160" stroke="#9AA3AE" stroke-width="4" stroke-dasharray="8 6"/>',
     '<polygon points="586,160 572,152 572,168" fill="#9AA3AE"/>',
     '<rect x="592" y="118" width="214" height="86" rx="10" fill="#FFFFFF" stroke="#9AA3AE" stroke-width="2" stroke-dasharray="8 6"/>',
     t(699, 154, "之後測 PhyClone", 24, "#6B7480", 400, "middle"),
     t(699, 188, "的 HP 擴充", 24, "#6B7480", 400, "middle"),
     ]
for i, (b, col, word, ic, phrase, how, seg) in enumerate(rows):
    cy = 280 + i * 96
    if i:
        L.append(f'<line x1="24" y1="{cy-48}" x2="816" y2="{cy-48}" stroke="#E3E1DA" stroke-width="2"/>')
    L.append(badge(54, cy, b, col))
    L.append(t(88, cy + 9, word, 24, col, 700))
    L.append(icon(ic, 170, cy))
    L.append(t(270, cy - 4, phrase, 26, "#1F2A37", 700))
    L.append(t(270, cy + 30, how, 24, "#6B7480"))
    L.append(f'<rect x="704" y="{cy-20}" width="112" height="40" rx="20" fill="#FFFFFF" stroke="#2F6DB5" stroke-width="2"/>')
    L.append(t(760, cy + 9, seg, 24, BLUE, 700, "middle"))
left = ('<svg xmlns="http://www.w3.org/2000/svg" aria-label="上次會議的 3 項要求與本週回應：目的是用 diplosim 產生帶 HP1、HP2 的模擬 long read bulk，之後用來測 PhyClone 的 HP 擴充；'
        '說清楚改了什麼見 p2 到 p7；先比 2 到 3 個方案再選這版沒有放；用流程圖呈現中間思考見每頁" '
        'viewBox="0 0 840 540" style="width:840px; height:540px">' + "".join(L) + '</svg>')

R = []
panels = [
    ("1 · 兩台機器", ["比旋鈕（輸入）與輸出"]),
    ("2 · 怎麼檢查接近真實", ["HCC1395 真實 long read", "5 種 purity"]),
    ("3 · 結果　4 · 懂／不懂", None),
]
for i, (title, lines) in enumerate(panels):
    y0 = i * 186
    R.append(f'<rect x="1" y="{y0+1}" width="798" height="166" rx="16" fill="#FFFFFF" stroke="#E3E1DA" stroke-width="2"/>')
    R.append(f'<rect x="1" y="{y0+1}" width="10" height="166" rx="4" fill="#2F6DB5"/>')
    R.append(t(316, y0 + 64, title, 32, "#1F2A37", 700))
    if lines:
        for j, s in enumerate(lines):
            R.append(t(316, y0 + 108 + j * 34, s, 26, "#1F2A37"))
# panel 1: two machines
R.append(machine(40, 18, 1.3, "#4A5568", False))
R.append(machine(176, 18, 1.3, "#2F6DB5", True))
R.append(t(87, 136, "CONIPHER", 24, "#4A5568", 700, "middle"))
R.append(t(223, 136, "diplosim", 24, "#2F6DB5", 700, "middle"))
# panel 2: five purity bars + magnifier
y0 = 186
for j, frac in enumerate([1.0, 0.8, 0.6, 0.4, 0.2]):
    y = y0 + 24 + j * 25
    R.append(f'<rect x="40" y="{y}" width="{190*frac:.0f}" height="17" fill="#3B5B7A"/>')
    if frac < 1:
        R.append(f'<rect x="{40+190*frac:.0f}" y="{y}" width="{190*(1-frac):.0f}" height="17" fill="#B8C0CA"/>')
R.append(f'<circle cx="236" cy="{y0+96}" r="32" fill="#FFFFFF" fill-opacity="0.6" stroke="#1F2A37" stroke-width="5"/>')
R.append(f'<line x1="259" y1="{y0+119}" x2="284" y2="{y0+146}" stroke="#1F2A37" stroke-width="8" stroke-linecap="round"/>')
# panel 3: small line chart + check / question
y0 = 372
R.append(f'<line x1="40" y1="{y0+24}" x2="40" y2="{y0+140}" stroke="#4A5568" stroke-width="3"/>')
R.append(f'<line x1="40" y1="{y0+140}" x2="180" y2="{y0+140}" stroke="#4A5568" stroke-width="3"/>')
pts = [(56, 40), (88, 62), (120, 92), (152, 112)]
R.append('<polyline points="' + " ".join(f"{x},{y0+y}" for x, y in pts) + '" fill="none" stroke="#2F6DB5" stroke-width="4"/>')
for x, y in pts:
    R.append(f'<circle cx="{x}" cy="{y0+y}" r="7" fill="#2F6DB5"/>')
R.append(badge(236, y0 + 50, "check", BLUE))
R.append(f'<circle cx="236" cy="{y0+114}" r="22" fill="{ORANGE}"/>')
R.append(t(236, y0 + 124, "?", 30, "#FFFFFF", 700, "middle"))
R.append(t(316, y0 + 108, "真實資料的目標值", 26))
R.append(t(316, y0 + 142, "已確認", 26, BLUE, 700))
R.append(t(400, y0 + 142, "·", 26, GRAY, 700))
R.append(t(420, y0 + 142, "還不確定", 26, ORANGE, 700))
right = ('<svg xmlns="http://www.w3.org/2000/svg" aria-label="今天的 3 段：兩台機器；用 HCC1395 5 種 purity 的真實 long read 檢查；結果與懂、不懂" '
         'viewBox="0 0 800 540" style="width:800px; height:540px">' + "".join(R) + '</svg>')

notes1 = ("這週要回答兩個問題：diplosim 多輸出哪些 long read 資訊，以及怎麼檢查它接近真實。"
          "左邊先接回上次會議。最上面是研究目的：用模擬資料生成器 diplosim，產生帶 HP1、HP2 的 long read bulk 資料；右邊灰色虛線框是之後的用途，拿這些資料測 PhyClone 的 HP 擴充。"
          "下面是上次會議的三項要求，以及這週在哪裡回應。第一，說清楚改了什麼，用 8 個旋鈕、每組旋鈕一頁，以及兩台機器的輸出比較說明，在第 2 到第 7 頁。"
          "第二，先比兩到三個方案再選，這一版沒有放方案比較的頁面。"
          "第三，用流程圖呈現中間思考，每一頁都有一張主圖。"
          "右邊是今天的順序：先比兩台機器的旋鈕與輸出，再用五種 purity 的 HCC1395 真實 long read 檢查，最後是目標值，以及已確認和還不確定的事。")

p1 = (f'<section id="outline" style="{SEC}; font-family:\'Noto Sans TC\', Arial, sans-serif; color:#1f2a37">\n'
      f'  <p style="{LABEL}">本週大綱</p>\n'
      f'  <h2 style="{H2}">diplosim 比 CONIPHER 多輸出哪些 long read 資訊？怎麼檢查它接近真實資料？</h2>\n'
      f'  <div style="display:flex; flex-direction:row; gap:24px">\n    {left}\n    {right}\n  </div>\n'
      + footer(1) + f'  <aside>{notes1}</aside>\n</section>\n')

# ---------------------------------------------------------------- p3 knobs
K = []
K.append('<rect x="2" y="2" width="1660" height="230" rx="16" fill="#FFFFFF" stroke="#2F6DB5" stroke-width="3"/>')
K.append(machine(18, 10, 0.75, "#2F6DB5", True))
K.append(t(80, 44, "diplosim 面板", 28, "#1F2A37", 700))

# groups: (x0, x1, title, knobs[(cx, name, value, on)], arrow target (x,y) or None, grey)
groups = [
    (16, 176, "depth", [(96, "額外變異", "關閉", False)], (115, 350), False),
    (192, 412, "copy number", [(302, "第二個 CN 事件", "0", False)], (406, 350), False),
    (428, 608, "CONIPHER", [(483, "", "", None), (553, "", "", None)], None, True),
    (624, 1054, "read 錯誤", [(701, "鹼基讀錯", "關閉", False), (839, "HP 標錯", "關閉", False), (977, "標錯集中", "關閉", False)], (1121, 350), False),
    (1070, 1370, "HP 標記", [(1145, "標記比例", "0.8", True), (1295, "位點間差異", "關閉", False)], (1269, 350), False),
    (1386, 1648, "SNV 的 allele", [(1517, "allele B 機率", "0.5", True)], (1522, 350), False),
]
for x0, x1, title, knobs, tgt, grey in groups:
    if grey:
        K.append(f'<rect x="{x0}" y="58" width="{x1-x0}" height="162" rx="12" fill="#F7F6F2" stroke="#9AA3AE" stroke-width="2" stroke-dasharray="6 6"/>')
        K.append(t((x0 + x1) // 2, 90, title, 24, "#6B7480", 700, "middle"))
        K.append(t((x0 + x1) // 2, 200, "沿用參數", 24, "#6B7480", 400, "middle"))
    else:
        K.append(f'<rect x="{x0}" y="58" width="{x1-x0}" height="162" rx="12" fill="#F7F6F2"/>')
        K.append(t((x0 + x1) // 2, 90, title, 26, "#1F2A37", 700, "middle"))
    for cx, name, val, on in knobs:
        cy = 128 if not grey else 140
        r = 22 if not grey else 18
        stroke = "#4A5568" if not grey else "#9AA3AE"
        K.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" stroke="{stroke}" stroke-width="3"/>')
        if on is None:
            K.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-r+5}" stroke="#9AA3AE" stroke-width="4" stroke-linecap="round"/>')
        elif on:
            ang = math.radians(-60 if val == "0.8" else -90)
            K.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+16*math.cos(ang):.1f}" y2="{cy+16*math.sin(ang):.1f}" stroke="#2F6DB5" stroke-width="5" stroke-linecap="round"/>')
        else:
            ang = math.radians(135)
            K.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+16*math.cos(ang):.1f}" y2="{cy+16*math.sin(ang):.1f}" stroke="#9AA3AE" stroke-width="5" stroke-linecap="round"/>')
        K.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{stroke}"/>')
        if name:
            K.append(t(cx, 180, name, 24, "#1F2A37", 400, "middle"))
            K.append(t(cx, 210, val, 24, "#2F6DB5", 700, "middle"))
    if tgt:
        cx = (x0 + x1) // 2
        K.append(f'<circle cx="{cx}" cy="232" r="6" fill="#C96A1B"/>')
        K.append(arrow(cx, 238, tgt[0], tgt[1] - 2, "#C96A1B", w=4, head=16))

# output row
cells = [
    (0, 230, "depth", "ref 36、alt 21", True),
    (246, 566, "allele A、B copy number", "1、1", True),
    (582, 762, "clone、CCF", "trunk、1.0", False),
]
for x0, x1, head, val, hit in cells:
    K.append(f'<rect x="{x0+1}" y="350" width="{x1-x0-2}" height="92" rx="10" fill="#FFFFFF" stroke="{"#C96A1B" if hit else "#E3E1DA"}" stroke-width="{3 if hit else 2}"/>')
    K.append(t((x0 + x1) // 2, 384, head, 24, "#6B7480", 400, "middle"))
    K.append(t((x0 + x1) // 2, 424, val, 26, "#1F2A37", 700, "middle"))
hp = [(778, 968, "HP1", "#2C5F9E", "ref 0", "alt 19", None),
      (976, 1166, "HP2", "#D9772B", "ref 27", "alt 0", "alt"),
      (1174, 1364, "unphased", "#6B7480", "ref 9", "alt 2", "all")]
for x0, x1, name, col, ref, alt, hit in hp:
    K.append(f'<rect x="{x0+1}" y="350" width="{x1-x0-2}" height="92" rx="10" fill="#FFFFFF" stroke="{"#C96A1B" if hit == "all" else "#E3E1DA"}" stroke-width="{3 if hit == "all" else 2}"/>')
    bar = "#9AA3AE" if name == "unphased" else col
    K.append(f'<line x1="{x0+16}" y1="376" x2="{x0+40}" y2="376" stroke="{bar}" stroke-width="8" stroke-linecap="round"/>')
    K.append(t(x0 + 52, 384, name, 24, col, 700))
    K.append(t(x0 + 14, 424, ref, 24))
    if hit == "alt":
        K.append(f'<rect x="{x0+100}" y="398" width="82" height="36" rx="8" fill="none" stroke="#C96A1B" stroke-width="3"/>')
    K.append(t(x0 + 110, 424, alt, 24, "#1F2A37", 700 if hit == "alt" else 400))
K.append('<rect x="1381" y="350" width="282" height="92" rx="10" fill="#FFFFFF" stroke="#C96A1B" stroke-width="3"/>')
K.append(t(1522, 384, "真值：SNV 在 allele", 24, "#6B7480", 400, "middle"))
K.append(t(1522, 424, "A（HP1）", 26, "#1F2A37", 700, "middle"))
# caption under row
K.append(t(0, 476, "SNV1 的輸出一列", 24, "#1F2A37", 700))
K.append('<rect x="200" y="452" width="120" height="34" rx="17" fill="none" stroke="#C96A1B" stroke-width="2"/>')
K.append(t(260, 477, "實際結果", 24, "#C96A1B", 700, "middle"))
K.append('<line x1="344" y1="469" x2="380" y2="469" stroke="#C96A1B" stroke-width="4"/>')
K.append(t(390, 477, "旋鈕改動的欄位", 24, "#6B7480"))
# small tag strip
tags = [
    (0, 330, [("拿掉", "#C96A1B", 700), ("sample 數相關參數", "#1F2A37", 400)]),
    (346, 640, [("改名", "#C96A1B", 700), ("clone 數、SNV 數", "#1F2A37", 400)]),
    (656, 1420, [("新旋鈕設回 CONIPHER 值 → 等於 CONIPHER", "#1F2A37", 700), ("程式推得，未實測", "#6B7480", 400)]),
]
for x0, x1, parts in tags:
    K.append(f'<rect x="{x0+1}" y="494" width="{x1-x0-2}" height="44" rx="22" fill="#FFFFFF" stroke="#E3E1DA" stroke-width="2"/>')
    first, second = parts
    K.append(f'<text x="{x0+20}" y="525" font-family="{SANS}" font-size="24">'
             f'<tspan font-weight="{first[2]}" fill="{first[1]}">{first[0]}</tspan>'
             f'<tspan dx="14" font-weight="{second[2]}" fill="{second[1]}">{second[0]}</tspan></text>')

knobs_svg = ('<svg xmlns="http://www.w3.org/2000/svg" aria-label="diplosim 面板上 5 組新旋鈕與預設值，各拉一條箭頭到 SNV1 輸出一列中它改動的欄位：'
             'depth 到 ref、alt；copy number 到 allele A、B copy number；read 錯誤到 HP2 的 alt；HP 標記到 unphased；SNV 的 allele 到真值" '
             'viewBox="0 0 1664 540" style="width:1664px; height:540px">' + "".join(K) + '</svg>')

notes3 = ("這頁要看的是：diplosim 沿用 CONIPHER 參數，新增 8 個旋鈕，分 5 組，各改輸出的一部分。"
          "上面藍框是面板，下面是 SNV1 實際輸出的一列，橘色箭頭指到改動的欄位。"
          "depth 的額外變異改 ref、alt 的總數；第二個 CN 事件改 allele A、B 的 copy number；灰色虛線這組沿用 CONIPHER。"
          "read 錯誤會讓 alt 出現在另一條 HP，這裡是 HP2 的 alt；HP 標記比例 0.8 決定 unphased 有多少；allele B 機率 0.5 決定真值在哪條 allele。"
          "灰色指針是預設關閉。最下面：拿掉 sample 數相關參數，clone 數、SNV 數改名；新旋鈕設回 CONIPHER 值就等於 CONIPHER，這是程式推得，還沒實測。接下來一組一組看，每組旋鈕模仿真實 long read 的什麼。")

p3 = (f'<section id="t1-knobs" style="{SEC}">\n'
      f'  <p style="{LABEL}">1 · 兩台機器</p>\n'
      f'  <h2 style="{H2}">diplosim 沿用 CONIPHER 參數，新增 8 個旋鈕，分 5 組各改輸出的一部分</h2>\n'
      f'  {knobs_svg}\n' + footer(2) + f'  <aside>{notes3}</aside>\n</section>\n')

(OUT / "outline.html").write_text(p1)
(OUT / "t1-knobs.html").write_text(p3)
for n in (notes1, notes3):
    print(len("".join(n.split())))
