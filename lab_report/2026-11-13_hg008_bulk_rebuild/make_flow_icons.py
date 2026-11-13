"""Icon-style flowchart for the HG008 bulk rebuild plan (2026-11-13). Writes plan_flow_icons.html; screenshot to PNG."""
import math, pathlib
HP1, HP1S, HP2, HP2S, SNV, UNP = "#2C5F9E", "#8FB3E0", "#D9772B", "#F2B880", "#D23A2E", "#9AA3AE"
TUM, INK = "#6B4FA0", "#2D3748"
W, H = 1920, 1180

def star(cx, cy, r, fill=SNV):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#fff" stroke-width="1.2"/>'

def t(x, y, s, size=20, w=700, c=INK, anchor="middle"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{s}</text>'

# ---------- icons: each drawn in a 150x110 box at (x, y) ----------
def ic_tube(x, y):
    s = f'<path d="M{x+50},{y+5} h50 v70 a25,25 0 0 1 -50,0 z" fill="#fff" stroke="{INK}" stroke-width="3"/>'
    s += f'<rect x="{x+44}" y="{y}" width="62" height="10" rx="4" fill="{INK}"/>'
    for i, (dx, dy, c) in enumerate([(62,40,TUM),(80,38,TUM),(70,55,UNP),(88,58,TUM),(60,70,TUM),(78,76,TUM),(70,90,UNP)]):
        s += f'<circle cx="{x+dx}" cy="{y+dy}" r="7" fill="{c}"/>'
    return s

def ic_doc(x, y, star_on=True, label="VCF"):
    s = f'<path d="M{x+40},{y} h52 l20,20 v90 h-72 z" fill="#fff" stroke="{INK}" stroke-width="3"/>'
    s += f'<path d="M{x+92},{y} v20 h20" fill="none" stroke="{INK}" stroke-width="3"/>'
    for i in range(4):
        s += f'<rect x="{x+50}" y="{y+32+i*14}" width="{40 if i%2 else 50}" height="5" rx="2" fill="{UNP}"/>'
    if star_on: s += star(x + 100, y + 88, 16)
    s += t(x + 70, y + 26, label, 13, 800, INK)
    return s

def ic_reads(x, y):
    s = ""
    rows = [(HP1, 10), (HP1S, 30), (HP1S, 0), (HP2, 20), (HP2S, 5), (HP2, 35)]
    for i, (c, off) in enumerate(rows):
        yy = y + 8 + i * 16 + (8 if i >= 3 else 0)
        s += f'<rect x="{x+10+off}" y="{yy}" width="105" height="10" rx="5" fill="{c}"/>'
    s += f'<line x1="{x+75}" y1="{y}" x2="{x+75}" y2="{y+112}" stroke="{SNV}" stroke-width="2" stroke-dasharray="4 3"/>'
    s += f'<circle cx="{x+75}" cy="{y+29}" r="5" fill="{SNV}"/><circle cx="{x+75}" cy="{y+45}" r="5" fill="{SNV}"/>'
    s += f'<circle cx="{x+75}" cy="{y+93}" r="5" fill="{SNV}"/>'
    s += t(x + 138, y + 30, "HP1", 13, 800, HP1) + t(x + 138, y + 85, "HP2", 13, 800, HP2)
    return s

def ic_counts(x, y):
    s = f'<line x1="{x+10}" y1="{y+100}" x2="{x+140}" y2="{y+100}" stroke="{INK}" stroke-width="2"/>'
    bars = [(20, 70, "#fff", HP1), (45, 40, SNV, HP1), (85, 60, "#fff", HP2), (110, 30, SNV, HP2)]
    for bx, h, f, edge in bars:
        s += f'<rect x="{x+bx}" y="{y+100-h}" width="20" height="{h}" fill="{f}" stroke="{edge}" stroke-width="3"/>'
    s += t(x + 42, y + 118, "HP1", 13, 800, HP1) + t(x + 107, y + 118, "HP2", 13, 800, HP2)
    s += f'<circle cx="{x+20}" cy="{y+8}" r="5" fill="#fff" stroke="{INK}" stroke-width="2"/>' + t(x + 38, y + 13, "ref", 12, 600, INK)
    s += f'<circle cx="{x+80}" cy="{y+8}" r="5" fill="{SNV}"/>' + t(x + 98, y + 13, "alt", 12, 600, INK)
    return s

def ic_cn(x, y):
    s = ""
    for i, c in enumerate([HP1, HP2]):
        yy = y + 22 + i * 38
        s += f'<rect x="{x+10}" y="{yy}" width="130" height="18" rx="9" fill="{c}"/>'
    s += f'<rect x="{x+90}" y="{y+2}" width="50" height="16" rx="8" fill="{HP1}" opacity="0.55"/>'
    s += f'<rect x="{x+10}" y="{y+95}" width="70" height="16" rx="4" fill="#E3F4EA" stroke="#2F855A" stroke-width="2"/>'
    s += t(x + 45, y + 108, "1+1 ✓", 13, 800, "#2F855A")
    s += f'<rect x="{x+88}" y="{y+95}" width="52" height="16" rx="4" fill="#FDE2E2" stroke="{SNV}" stroke-width="2"/>'
    s += t(x + 114, y + 108, "2+1", 13, 800, SNV)
    return s

def ic_pie(x, y):
    cx, cy, r = x + 60, y + 55, 48
    a = 2 * math.pi * 0.8
    ex, ey = cx + r * math.sin(a), cy - r * math.cos(a)
    s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{UNP}"/>'
    s += f'<path d="M{cx},{cy} L{cx},{cy-r} A{r},{r} 0 1 1 {ex:.1f},{ey:.1f} z" fill="{TUM}"/>'
    s += f'<circle cx="{x+130}" cy="{y+35}" r="9" fill="{TUM}"/>' + t(x + 130, y + 62, "腫瘤", 13, 700, TUM)
    s += f'<circle cx="{x+130}" cy="{y+80}" r="9" fill="{UNP}"/>' + t(x + 130, y + 107, "正常", 13, 700, "#5A6472")
    return s

def ic_table(x, y):
    s = f'<rect x="{x+15}" y="{y+5}" width="120" height="100" rx="8" fill="#fff" stroke="{INK}" stroke-width="3"/>'
    s += f'<rect x="{x+15}" y="{y+5}" width="120" height="22" rx="8" fill="{INK}"/>'
    for i in range(1, 4):
        s += f'<line x1="{x+15}" y1="{y+27+i*19}" x2="{x+135}" y2="{y+27+i*19}" stroke="{UNP}" stroke-width="2"/>'
    for j, c in enumerate([UNP, HP1, HP2]):
        s += f'<line x1="{x+55+j*27}" y1="{y+27}" x2="{x+55+j*27}" y2="{y+105}" stroke="{UNP}" stroke-width="2"/>'
        for i in range(4):
            s += f'<rect x="{x+60+j*27}" y="{y+32+i*19}" width="17" height="9" rx="3" fill="{c}"/>'
    for i in range(4): s += star(x + 35, y + 37 + i * 19, 7)
    return s

def mini_tree(x, y, cols, scale=1.0, ok=None):
    # root -> A -> (B, C); A -> D
    pos = {"r": (60, 10), "a": (60, 45), "b": (25, 85), "c": (95, 85), "d": (60, 85)}
    edges = [("r", "a"), ("a", "b"), ("a", "c"), ("a", "d")]
    s = ""
    for p, q in edges:
        (x1, y1), (x2, y2) = pos[p], pos[q]
        s += f'<line x1="{x+x1*scale}" y1="{y+y1*scale}" x2="{x+x2*scale}" y2="{y+y2*scale}" stroke="{INK}" stroke-width="3"/>'
    for k, c in zip(["r", "a", "b", "c", "d"], cols):
        px, py = pos[k]
        s += f'<circle cx="{x+px*scale}" cy="{y+py*scale}" r="{11*scale}" fill="{c}" stroke="#fff" stroke-width="2"/>'
    return s

CL = ["#1A202C", "#4A5568", "#38A169", "#D69E2E", "#3182CE"]

def ic_haplo(x, y):
    s = ""
    cx, cy = x + 30, y + 30
    for i in range(8):
        a = i * math.pi / 4
        s += f'<rect x="{cx-6}" y="{cy-30}" width="12" height="14" rx="2" fill="{UNP}" transform="rotate({i*45} {cx} {cy})"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="20" fill="{UNP}"/><circle cx="{cx}" cy="{cy}" r="8" fill="#fff"/>'
    s += f'<path d="M{x+52},{y+40} q20,0 30,15" fill="none" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/>'
    s += mini_tree(x + 70, y + 8, CL, 0.85)
    return s

def ic_dishes(x, y):
    s = ""
    for i in range(8):
        cx, cy = x + 22 + (i % 4) * 36, y + 30 + (i // 4) * 48
        s += f'<circle cx="{cx}" cy="{cy}" r="16" fill="#fff" stroke="{INK}" stroke-width="2.5"/>'
        s += f'<circle cx="{cx-4}" cy="{cy-3}" r="5" fill="{CL[2+i%3]}"/><circle cx="{cx+5}" cy="{cy+4}" r="5" fill="{CL[2+i%3]}"/>'
    return s

def ic_cells(x, y):
    s = ""
    import random
    random.seed(3)
    for i in range(26):
        cx, cy = x + 15 + random.random() * 120, y + 12 + random.random() * 90
        c = CL[1 + (i % 4)]
        s += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="8" fill="{c}" stroke="#fff" stroke-width="1.5"/>'
    return s

def ic_bars(x, y):
    s = ""
    segs = [(CL[1], 0.07), (CL[2], 0.53), (CL[3], 0.27), (CL[4], 0.13)]
    xx = x + 10
    for c, f in segs:
        w = 130 * f
        s += f'<rect x="{xx:.1f}" y="{y+40}" width="{w:.1f}" height="34" fill="{c}"/>'
        xx += w
    s += f'<rect x="{x+10}" y="{y+40}" width="130" height="34" fill="none" stroke="{INK}" stroke-width="2.5" rx="3"/>'
    return s

def ic_link(x, y):
    s = star(x + 30, y + 50, 22)
    s += f'<path d="M{x+58},{y+50} h30" stroke="{INK}" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#ah)"/>'
    s += mini_tree(x + 85, y + 10, CL, 0.6)
    s += star(x + 85 + 95 * 0.6, y + 10 + 85 * 0.6 - 2, 9)
    return s

# ---------- layout ----------
out = []
A = out.append
A(f'<rect width="{W}" height="{H}" fill="#FBFAF7"/>')
A(t(W / 2, 62, "HG008 bulk 重建 vs 參考樹：怎麼做", 40, 900))
A(t(W / 2, 98, "規劃（2026-11-13）・還沒跑", 20, 500, "#718096"))
A(f'<rect x="1530" y="80" width="150" height="30" rx="15" fill="#E3F4EA"/>' + t(1605, 101, "沿用現有工具", 15, 700, "#2F855A"))
A(f'<rect x="1695" y="80" width="150" height="30" rx="15" fill="#FEF3C7"/>' + t(1770, 101, "新寫／改寫", 15, 700, "#B7791F"))

def lane(x, y, w, h, fill, edge, label, color):
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28" fill="{fill}" stroke="{edge}" stroke-width="2"/>')
    A(f'<rect x="{x+24}" y="{y-18}" width="{len(label)*24+40}" height="36" rx="18" fill="{color}"/>')
    A(t(x + 44 + len(label) * 12, y + 8, label, 21, 800, "#fff"))

def card(cx, y, num, title, tool, icon, reuse=True, badge=None):
    x = cx - 105
    A(f'<rect x="{x}" y="{y}" width="210" height="250" rx="22" fill="#fff" stroke="#E2E8F0" stroke-width="2" filter="url(#sh)"/>')
    if num:
        A(f'<circle cx="{x+26}" cy="{y+26}" r="18" fill="{INK}"/>' + t(x + 26, y + 33, num, 19, 800, "#fff"))
    A(icon(cx - 75, y + 40))
    A(t(cx, y + 188, title, 23, 800))
    chip = "#E3F4EA" if reuse else "#FEF3C7"
    tc = "#2F855A" if reuse else "#B7791F"
    A(f'<rect x="{x+16}" y="{y+204}" width="178" height="30" rx="15" fill="{chip}"/>')
    A(t(cx, y + 225, tool, 15, 700, tc))
    if badge:
        bx, by = x + 192, y + 4
        A(f'<rect x="{bx-17}" y="{by-17}" width="34" height="34" rx="5" fill="#FDE2E2" stroke="{SNV}" stroke-width="2.5" transform="rotate(45 {bx} {by})"/>')
        A(t(bx, by + 6, badge, 15, 900, SNV))

def arrow(x1, y1, x2, y2, dash=False, color=INK):
    d = ' stroke-dasharray="9 7"' if dash else ""
    A(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="4" fill="none"{d} marker-end="url(#ah)"/>')

# lane A
lane(30, 150, 1860, 330, "#EAF2FB", "#BFD3EE", "路線 A：bulk → 重建", HP1)
xs = [150 + i * 230 for i in range(8)]
yA = 195
specs = [
    ("", "bulk（p23）", "ONT 或 PacBio", ic_tube, True, "D4"),
    ("1", "SNV 名單", "bcftools", lambda x, y: ic_doc(x, y), True, "D1"),
    ("2", "read 標 HP", "longphase-s", ic_reads, True, "D2"),
    ("3", "分 HP 計數", "samtools＋改寫", ic_counts, False, None),
    ("4", "拷貝數", "NIST CNV・新寫", ic_cn, False, "D3"),
    ("5", "purity", "新寫", ic_pie, False, None),
    ("6", "輸入表", "改寫轉檔", ic_table, False, None),
    ("7", "重建樹", "haploclone", ic_haplo, True, None),
]
for cx, (n, ti, to, ic, re, b) in zip(xs, specs):
    card(cx, yA, n, ti, to, ic, re, b)
for a, b in zip(xs, xs[1:]):
    arrow(a + 108, yA + 125, b - 112, yA + 125)

# lane B
lane(30, 560, 1000, 560, "#F3EEFB", "#D6C9EF", "路線 B：參考答案", TUM)
yB1, yB2 = 600, 860
card(150, yB1, "", "8 株選殖株", "p14／p19", ic_dishes, True)
card(380, yB1, "R1", "參考樹形", "已跑（11-07）", lambda x, y: mini_tree(x + 15, y + 5, CL, 1.0), True)
card(150, yB2, "", "119 顆單細胞", "p23", ic_cells, True)
card(380, yB2, "R2", "分支比例", "已跑（11-07）", ic_bars, True)
card(780, yB1, "R3", "SNV 對上分支", "新寫", ic_link, False)
arrow(258, yB1 + 125, 272, yB1 + 125)
arrow(258, yB2 + 125, 272, yB2 + 125)
arrow(488, yB1 + 125, 672, yB1 + 125)
# SNV list feeds R3 (dashed)
arrow(380, yA + 252, 740, yB1 - 4, dash=True, color=SNV)

# compare
cx8, y8 = 1450, 610
A(f'<rect x="{cx8-390}" y="{y8-10}" width="800" height="300" rx="28" fill="#E3F4EA" stroke="#9AE6B4" stroke-width="2"/>')
A(f'<circle cx="{cx8-360}" cy="{y8+22}" r="18" fill="{INK}"/>' + t(cx8 - 360, y8 + 29, "8", 19, 800, "#fff"))
A(t(cx8 - 330, y8 + 31, "比對", 26, 900, INK, "start"))
# tree vs tree
A(mini_tree(cx8 - 330, y8 + 70, CL, 1.0))
A(t(cx8 - 200, y8 + 125, "⇄", 40, 800))
A(mini_tree(cx8 - 150, y8 + 70, CL, 1.0))
A(t(cx8 - 210, y8 + 210, "樹形：重建 ⇄ R1", 20, 800))
# bars vs bars
for k, yy in enumerate([y8 + 85, y8 + 140]):
    xx = cx8 + 90
    for c, f in [(CL[1], .07), (CL[2], .53), (CL[3], .27), (CL[4], .13)] if k else [(CL[1], .10), (CL[2], .48), (CL[3], .30), (CL[4], .12)]:
        A(f'<rect x="{xx:.0f}" y="{yy}" width="{220*f:.0f}" height="30" fill="{c}"/>'); xx += 220 * f
    A(t(cx8 + 80, yy + 22, "重建" if k == 0 else "R2", 16, 700, INK, "end"))
A(t(cx8 + 200, y8 + 210, "組成：CCF ⇄ 單細胞比例", 20, 800))
A(f'<rect x="{cx8-330}" y="{y8+232}" width="680" height="42" rx="21" fill="#fff"/>')
A(t(cx8 + 10, y8 + 260, "base 和 A1（加 HP）各跑一次，分開比", 19, 700, "#2F855A"))
arrow(xs[-1], yA + 252, xs[-1] - 30, y8 - 14)
arrow(888, yB1 + 125, cx8 - 395, y8 + 125)
arrow(488, yB2 + 125, cx8 - 395, y8 + 200)

# decisions + risks strip
yR = 940
A(f'<rect x="1060" y="{yR-20}" width="830" height="200" rx="28" fill="#FFF5F5" stroke="#FEB2B2" stroke-width="2"/>')
A(t(1090, yR + 16, "帶週會決定", 22, 900, SNV, "start"))
dec = [("D1", "SNV 來源", "NIST／ClairS-TO"), ("D2", "HP 來源", "標 read／NIST hap"),
       ("D3", "區域", "只 1+1／全部"), ("D4", "平台", "ONT／PacBio")]
for i, (d, a, b) in enumerate(dec):
    bx, by = 1110 + i * 200, yR + 70
    A(f'<rect x="{bx-17}" y="{by-17}" width="34" height="34" rx="5" fill="#FDE2E2" stroke="{SNV}" stroke-width="2.5" transform="rotate(45 {bx} {by})"/>')
    A(t(bx, by + 6, d, 15, 900, SNV))
    A(t(bx + 30, by + 7, a, 19, 800, INK, "start"))
    A(t(bx - 20, by + 50, b, 15, 600, "#4A5568", "start"))
A(t(1475, yR + 165, "⚠ 選殖株和 bulk 不同代：選殖株只比樹形・NIST SNV 偏 truncal・選殖株的分支 SNV 只有約 300 個", 17, 700, "#9C4221"))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Noto Sans CJK TC, sans-serif">
<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>
<filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.12"/></filter></defs>
{"".join(out)}</svg>'''
here = pathlib.Path(__file__).parent
(here / "plan_flow_icons.svg").write_text(svg)
(here / "plan_flow_icons.html").write_text(f'<!doctype html><meta charset="utf-8"><title>HG008 bulk plan</title><style>body{{margin:0;background:#FBFAF7}}</style>{svg}')
