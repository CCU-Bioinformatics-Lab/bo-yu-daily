"""Slide m-axis (2026-11-04 deck, page 1): the main axis of the 10-28 meeting is this week's main axis.
Left: research purpose (CONIPHER -> diplosim -> long read bulk + truth tree -> later test PhyClone HP).
Right: the 10-28 to-dos with this week's status icons and the pages that answer them.
Source: meeting_record/2026_10_28_meeting_record.md (決議 1-4, 待辦). User request 2026-11-02.
Run: python3 gen_p0.py (writes project/slides/m-axis.html)."""
from pathlib import Path

OUT = Path(__file__).parent / "project" / "slides" / "m-axis.html"
F = "Noto Sans TC, Arial, sans-serif"
P = "font-family:'Noto Sans TC', Arial, sans-serif"
INK, SUB, BLUE, ORANGE, LINE, BG = "#1F2A37", "#6B7480", "#2F6DB5", "#C96A1B", "#E3E1DA", "#F7F6F2"
HP1, HP1S, HP2, HP0, RED, GREY = "#2C5F9E", "#8FB3E0", "#D9772B", "#9AA3AE", "#D23A2E", "#4A5568"


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


def varrow(x, y1, y2, col=INK, w=4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - 14}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>'
            f'<polygon points="{x},{y2} {x - 8},{y2 - 14} {x + 8},{y2 - 14}" fill="{col}"/>')


def status(cx, cy, kind):
    if kind == "ok":
        return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="{BLUE}"/>'
                f'<polyline points="{cx - 10},{cy} {cx - 3},{cy + 8} {cx + 11},{cy - 8}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "go":
        return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="{GREY}"/>'
                f'<line x1="{cx - 10}" y1="{cy}" x2="{cx + 6}" y2="{cy}" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>'
                f'<polyline points="{cx},{cy - 8} {cx + 9},{cy} {cx},{cy + 8}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="{ORANGE}"/>'
            f'<line x1="{cx - 8}" y1="{cy - 8}" x2="{cx + 8}" y2="{cy + 8}" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>'
            f'<line x1="{cx + 8}" y1="{cy - 8}" x2="{cx - 8}" y2="{cy + 8}" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>')


W, H = 1664, 540
s = ""

# ---- left: research purpose, top to bottom ----
LW = 600
s += rect(1, 1, LW - 2, H - 2)
s += t(28, 48, "研究目的（不變）", 28, 700, BLUE)
# row 1: CONIPHER -> diplosim
s += machine(60, 80, 1.3, GREY, plain=True) + t(107, 176, "CONIPHER", 22, 700, GREY, "middle")
s += t(107, 204, "不分 HP", 22, 400, SUB, "middle")
s += (f'<line x1="170" y1="114" x2="300" y2="114" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
      f'<polygon points="314,114 300,106 300,122" fill="{INK}"/>')
s += t(242, 100, "改成雙套體", 22, 700, INK, "middle")
s += machine(330, 80, 1.3) + t(377, 176, "diplosim", 22, 700, BLUE, "middle")
s += t(377, 204, "分 HP1／HP2", 22, 400, SUB, "middle")
# row 2: outputs
s += varrow(377, 216, 262)
s += rect(40, 270, 520, 120, fill=BG, stroke=BG)
s += t(60, 304, "long read bulk", 24, 700, INK)
for i, (col, alt) in enumerate(((HP1S, True), (HP1, False), (HP2, False), (HP0, True))):
    yy = 326 + i * 16
    s += f'<line x1="{64 + (i % 2) * 10}" y1="{yy}" x2="{234 + (i % 2) * 10}" y2="{yy}" stroke="{col}" stroke-width="9" stroke-linecap="round"/>'
    s += f'<circle cx="150" cy="{yy}" r="6" fill="{RED if alt else "#FFFFFF"}" stroke="{"#FFFFFF" if alt else INK}" stroke-width="2"/>'
s += t(330, 304, "真值樹", 24, 700, INK)
for (x1, y1, x2, y2) in ((390, 330, 350, 372), (390, 330, 430, 372)):
    s += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{SUB}" stroke-width="4"/>'
for (cx, cy) in ((390, 330), (350, 372), (430, 372)):
    s += f'<circle cx="{cx}" cy="{cy}" r="11" fill="#C3CAD3" stroke="#FFFFFF" stroke-width="2"/>'
# row 3: later use
s += varrow(300, 398, 444, HP0, 3, "6 5")
s += rect(130, 452, 340, 64, fill="#FFFFFF", stroke=HP0, dash="8 6")
s += t(300, 494, "之後測 PhyClone 的 HP 擴充", 24, 400, SUB, "middle")

# ---- right: 10-28 to-dos and this week's status ----
RX = LW + 24
RW = W - RX
s += rect(RX + 1, 1, RW - 2, H - 2)
s += t(RX + 28, 48, "10-28 會議的待辦 → 本週狀態", 28, 700, INK)
rows = [
    ("ok", "說清楚 diplosim 比 CONIPHER 改了什麼、為什麼", "8 個旋鈕分 5 組，每組一頁", "p3–p8"),
    ("go", "想 2–3 種驗證方法，看真實資料能驗什麼", "先做 HCC1395 5 種 purity 比 bulk；驗樹未定", "p9–p13"),
    ("no", "關鍵設計先比 2–3 個候選方案再選", "這版沒有放方案比較", "—"),
    ("ok", "用流程圖、示意圖呈現中間思考", "每頁一張主圖", "每頁"),
]
y = 86
for kind, ask, now, where in rows:
    s += status(RX + 52, y + 30, kind)
    s += t(RX + 92, y + 22, ask, 26, 700, INK)
    s += t(RX + 92, y + 58, now, 24, 400, ORANGE if kind == "no" else SUB)
    s += rect(RX + RW - 140, y + 4, 116, 40, stroke=BLUE if kind != "no" else ORANGE, rx=20)
    s += t(RX + RW - 82, y + 32, where, 24, 700, BLUE if kind != "no" else ORANGE, "middle")
    y += 96
    if y < 470:
        s += f'<line x1="{RX + 24}" y1="{y - 12}" x2="{RX + RW - 24}" y2="{y - 12}" stroke="{LINE}" stroke-width="2"/>'
# legend
lx, ly = RX + 28, H - 34
for kind, lab in (("ok", "已回應"), ("go", "進行中"), ("no", "未做")):
    s += f'<g transform="translate({lx},{ly}) scale(0.6) translate({-lx},{-ly})">{status(lx, ly, kind)}</g>'
    s += t(lx + 22, ly + 8, lab, 22, 400, SUB)
    lx += 140

aria = ("接回 10-28 會議。左：研究目的不變，把不分 HP 的 CONIPHER 改成分 HP1、HP2 的 diplosim，輸出 long read bulk 與真值樹，之後測 PhyClone 的 HP 擴充。"
        "右：10-28 會議 4 項待辦的本週狀態：說清楚改了什麼，已回應，p3 到 p8；想 2 到 3 種驗證方法，進行中，先做 HCC1395 5 種 purity，驗樹未定，p9 到 p13；"
        "先比 2 到 3 個候選方案，未做；用圖呈現中間思考，已回應，每頁")
svg = f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="{aria}" viewBox="0 0 {W} {H}" style="width:{W}px; height:{H}px">{s}</svg>'

notes = ("先接回 10-28 的會議。上次的主軸，就是這週的主軸：把現有的模擬器 CONIPHER 改成雙套體的 diplosim，說清楚改了什麼、為什麼這樣改，再想怎麼驗證它接近真實。"
         "左邊是研究目的，和上次一樣：CONIPHER 不分 HP，diplosim 把 SNV 和 read 分到 HP1、HP2，輸出 long read bulk 和真值樹，之後拿來測 PhyClone 的 HP 擴充。"
         "右邊是上次的四項待辦。第一，說清楚改了什麼，在第 3 到第 8 頁。第二，驗證方法目前只做了一種：用 HCC1395 五種 purity 比 bulk 資料，在第 9 到第 13 頁；驗樹還沒定。"
         "第三，先比兩到三個候選方案再選，這一版沒有放。第四，每頁都用一張主圖說明。下一頁看 diplosim 的流程和本週大綱。")

html = f'''<section id="m-axis" style="display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2; font-family:'Noto Sans TC', Arial, sans-serif; color:#1f2a37">
  <p style="{P}; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5">接回 10-28 會議</p>
  <h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37">上週主軸就是本週主軸：把 CONIPHER 改成雙套體的 diplosim，說清楚改了什麼，再檢查它接近真實</h2>
  {svg}
  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">
    <p style="{P}; font-size:24px; color:#6b7480">2026-11-04 diplosim：兩台機器與真實 long read</p>
    <p style="{P}; font-size:24px; color:#6b7480">1 / 13</p>
  </div>
  <aside>{notes}</aside>
</section>
'''
OUT.write_text(html)
print(OUT)
