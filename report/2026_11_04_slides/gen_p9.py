"""Slide t2-validation (2026-11-04 deck): diplosim gives long read bulk data and a truth tree; this week only
the bulk data is checked against real HCC1395 long reads at five tumour/normal mixes. Schematic, little text.
User comment 2026-11-02. Run: python3 gen_p9.py (writes project/slides/t2-validation.html)."""
from pathlib import Path

OUT = Path(__file__).parent / "project" / "slides" / "t2-validation.html"
F = "Noto Sans TC, Arial, sans-serif"
INK, SUB, BLUE, ORANGE, LINE = "#1F2A37", "#6B7480", "#2F6DB5", "#C96A1B", "#E3E1DA"
HP1, HP1S, HP2, HP2S, RED, HP0 = "#2C5F9E", "#8FB3E0", "#D9772B", "#F2B880", "#D23A2E", "#9AA3AE"
TUM, NOR = "#1F2A37", "#D5D2C9"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=24, weight=400, fill=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{F}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def rect(x, y, w, h, fill="#FFFFFF", stroke=LINE, sw=2, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def arrow(x1, y1, x2, y2, color=INK, w=5, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - 18 * math.cos(a), y2 - 18 * math.sin(a)
    px, py = -math.sin(a) * 10, math.cos(a) * 10
    return (f'<line x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{d}/>'
            f'<polygon points="{x2},{y2} {bx + px:.1f},{by + py:.1f} {bx - px:.1f},{by - py:.1f}" fill="{color}"/>')


def machine(x, y, s):
    return (f'<g transform="translate({x},{y}) scale({s})"><polygon points="20,2 52,2 44,14 28,14" fill="{BLUE}"/>'
            f'<rect x="6" y="14" width="60" height="34" rx="6" fill="{BLUE}"/>'
            f'<rect x="14" y="24" width="14" height="6" rx="3" fill="{HP1}"/><rect x="30" y="24" width="14" height="6" rx="3" fill="{HP2}"/>'
            f'<rect x="46" y="24" width="12" height="6" rx="3" fill="{HP0}"/><rect x="24" y="48" width="24" height="6" fill="#C3CAD3"/></g>')


def reads(x, y, rows):
    """rows: (colour, alt) from top; each read 150 px long, 22 px apart."""
    s = ""
    for i, (col, alt) in enumerate(rows):
        yy = y + i * 22
        off = (i % 3) * 14
        s += f'<line x1="{x + off}" y1="{yy}" x2="{x + off + 150}" y2="{yy}" stroke="{col}" stroke-width="10" stroke-linecap="round"/>'
        s += (f'<circle cx="{x + 80}" cy="{yy}" r="7" fill="{RED if alt else "#FFFFFF"}" '
              f'stroke="{"#FFFFFF" if alt else INK}" stroke-width="2"/>')
    return s


W, H = 1664, 640
s = ""
# diplosim machine
s += machine(20, 200, 2.6)
s += t(114, 380, "diplosim", 30, 700, BLUE, "middle")

# output 1: long read bulk (this week)
s += arrow(212, 250, 300, 170, INK)
s += rect(310, 40, 420, 270, stroke=ORANGE, sw=4)
s += rect(326, 56, 120, 38, fill=ORANGE, stroke=ORANGE, rx=19)
s += t(386, 84, "本週重點", 24, 700, "#FFFFFF", "middle")
s += t(520, 132, "long read bulk 資料", 28, 700, INK, "middle")
s += reads(430, 166, [(HP1S, True), (HP1, False), (HP2, False), (HP2, False), (HP0, True), (HP1S, True)])

# output 2: truth tree (later)
s += arrow(212, 330, 300, 450, SUB, 4, "10 8")
s += rect(310, 400, 420, 210, fill="#F7F6F2", stroke=SUB, dash="10 8")
s += t(520, 446, "真值樹", 28, 700, SUB, "middle")
for (x1, y1, x2, y2) in ((520, 478, 450, 540), (520, 478, 590, 540), (590, 540, 550, 590), (590, 540, 630, 590)):
    s += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{SUB}" stroke-width="4"/>'
for (cx, cy) in ((520, 478), (450, 540), (590, 540), (550, 590), (630, 590)):
    s += f'<circle cx="{cx}" cy="{cy}" r="14" fill="#C3CAD3" stroke="#FFFFFF" stroke-width="2"/>'
s += rect(326, 416, 120, 38, fill=SUB, stroke=SUB, rx=19)
s += t(386, 444, "之後再驗", 24, 700, "#FFFFFF", "middle")

# compare
s += arrow(744, 175, 880, 175, ORANGE, 6)
s += t(812, 150, "比較", 26, 700, ORANGE, "middle")

# real HCC1395 at five mixes
s += rect(896, 40, 750, 570)
s += t(1271, 92, "真實 HCC1395 long read", 28, 700, INK, "middle")
mixes = ((100, "0.97"), (80, "0.70"), (60, "0.48"), (40, "0.29"), (20, "0.14"))
bx, bw, by0 = 960, 420, 136
for i, (tum, pur) in enumerate(mixes):
    y = by0 + i * 84
    tw = bw * tum / 100
    s += f'<rect x="{bx}" y="{y}" width="{tw:.0f}" height="48" rx="8" fill="{TUM}"/>'
    if tum < 100:
        s += f'<rect x="{bx + tw:.0f}" y="{y}" width="{bw - tw:.0f}" height="48" rx="8" fill="{NOR}"/>'
    s += arrow(bx + bw + 16, y + 24, bx + bw + 76, y + 24, SUB, 4)
    s += t(bx + bw + 96, y + 34, pur, 30, 700, ORANGE)
s += t(bx + bw + 96, 128 - 8, "purity", 24, 400, SUB)
ly = by0 + 5 * 84 + 6
s += f'<rect x="{bx}" y="{ly}" width="28" height="28" rx="6" fill="{TUM}"/>' + t(bx + 40, ly + 23, "tumor read", 24, 400, INK)
s += f'<rect x="{bx + 230}" y="{ly}" width="28" height="28" rx="6" fill="{NOR}"/>' + t(bx + 270, ly + 23, "normal read", 24, 400, INK)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="diplosim 吐出 long read bulk 資料（本週重點）與真值樹（之後再驗）；'
       f'bulk 資料拿去和真實 HCC1395 long read 比較，真實樣本有 5 種 tumor、normal read 混合比例，換算 purity 0.97、0.70、0.48、0.29、0.14" '
       f'viewBox="0 0 {W} {H}" style="width:{W}px; height:{H}px">{s}</svg>')

notes = ("這頁要看的是：diplosim 會吐出兩樣東西，long read bulk 資料和真值樹。這週先專心在左上橘框的 bulk 資料，"
         "灰色虛線的真值樹之後再驗。bulk 資料要拿去和右邊真實 HCC1395 的 long read 比。右邊這 5 條是同一株細胞的 5 種混合，"
         "深色是 tumor read，淺色是 normal read，換算成 purity 從 0.97 到 0.14。下一頁看這 5 種混合怎麼來、怎麼比。")

P = "font-family:'Noto Sans TC', Arial, sans-serif"
html = f'''<section id="t2-validation" style="display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2">
  <p style="{P}; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5">2 · 怎麼檢查接近真實</p>
  <h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37">diplosim 吐出 bulk 資料與真值樹；本週先比 bulk 資料和 5 種 purity 的真實 HCC1395</h2>
  {svg}
  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">
    <p style="{P}; font-size:24px; color:#6b7480">2026-11-04 diplosim：兩台機器與真實 long read</p>
    <p style="{P}; font-size:24px; color:#6b7480">9 / 13</p>
  </div>
  <aside>{notes}</aside>
</section>
'''
OUT.write_text(html)
print(OUT)
