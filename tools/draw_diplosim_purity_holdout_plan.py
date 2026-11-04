#!/usr/bin/env python3
"""Draw the diplosim purity-holdout plan: diplosim as a machine with knobs, real HCC1395 subsamples on the side.

Usage: python3 tools/draw_diplosim_purity_holdout_plan.py OUT.svg
Styles are inline (no CSS classes) so ImageMagick / rsvg previews render the same as browsers.
"""
import sys
from xml.sax.saxutils import escape

INK, MUTED, LINE, BG = "#17201D", "#5B6864", "#CDD5D2", "#F2F4F3"
MACHINE, PANEL = "#2C3E3A", "#3D524D"
LOCK, LOCK_SOFT = "#8A9692", "#E4E8E6"
DIAL, DIAL_SOFT = "#C2541F", "#F7E3D8"
REAL, REAL_SOFT = "#2D5EA6", "#E2EAF5"
SIM, SIM_SOFT = "#2C7A4C", "#E3F1E8"
TUMOR, NORMAL = "#BF522E", "#A3ADA9"

# (label, purity, tumor x, normal x, ClairS PASS SNVs in HC regions)
SAMPLES = [("t50_n00", "0.97", 50, 0, "31,595"), ("t40_n10", "≈ 0.70", 40, 10, "29,508"),
           ("t30_n20", "≈ 0.48", 30, 20, "26,058"), ("t20_n30", "≈ 0.29", 20, 30, "19,277"),
           ("t10_n40", "≈ 0.14", 10, 40, "7,452")]

KNOB_GROUPS = [
    ("CN 事件", [("prop_pos_lost", "0.45"), ("loss_events", "cnloh_B"), ("second CNA", "0.5"),
                 ("gain_B 比重", "×2"), ("truncal SNV", "0.8")]),
    ("定序雜訊", [("depth φ", "0.03"), ("base_error", "0.01"), ("mistag", "0.005")]),
    ("HP tag", [("prop_tagged", "0.862"), ("tag κ", "1")]),
]

out = []


def T(x, y, s, size=14, color=INK, weight="normal", anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
               f'text-anchor="{anchor}" font-family="Noto Sans CJK TC">{escape(s)}</text>')


def R(x, y, w, h, fill, stroke="none", rx=10, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(x0, y0, x1, y1, color=MUTED, sw=2.5):
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{sw}" marker-end="url(#ah)"/>')


def knob(cx, cy, r, color, soft, angle_deg, locked):
    import math
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{soft}" stroke="{color}" stroke-width="3"/>')
    a = math.radians(angle_deg)
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + 0.75 * r * math.cos(a):.1f}" y2="{cy + 0.75 * r * math.sin(a):.1f}" '
               f'stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
    if locked:  # small padlock
        lx, ly = cx + r - 4, cy - r + 2
        out.append(f'<rect x="{lx - 6}" y="{ly}" width="12" height="9" rx="2" fill="{LOCK}"/>')
        out.append(f'<path d="M{lx - 4} {ly} v-3 a4 4 0 0 1 8 0 v3" fill="none" stroke="{LOCK}" stroke-width="2"/>')


def step_badge(x, y, n):
    out.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{INK}"/>')
    T(x, y + 5, str(n), 15, "white", "bold", "middle")


W, H = 1500, 1010
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
out.append(f'<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
           f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>')
R(0, 0, W, H, BG, rx=0)
T(40, 50, "diplosim purity holdout：同一台機器、鎖住旋鈕，只轉 purity，能不能吐出各 purity 的 HCC1395 bulk 資料？", 22, INK, "bold")
T(40, 80, "旋鈕值都是在 t50_n00 上校正的（commit b63cebd）。其餘 4 個 subsample 從沒用來調參數，所以是 holdout。", 14, MUTED)

# ---- machine ----
mx, my, mw, mh = 40, 110, 610, 650
R(mx, my, mw, mh, MACHINE, rx=22)
T(mx + 24, my + 42, "diplosim 機器", 22, "white", "bold")
T(mx + 24, my + 66, "CONIPHER 骨架：樹 → SNV／CNA 事件 → clone 比例 → read 計數 → HP 拆分", 12.5, "#C9D3D0")
gy = my + 90
for title, knobs in KNOB_GROUPS:
    rows = (len(knobs) + 2) // 3
    gh = 30 + rows * 78
    R(mx + 18, gy, mw - 36, gh, PANEL, rx=12)
    T(mx + 32, gy + 24, title + "（鎖住）", 14, "#E4E8E6", "bold")
    for i, (name, val) in enumerate(knobs):
        cx = mx + 90 + (i % 3) * 190
        cy = gy + 62 + (i // 3) * 78
        knob(cx, cy, 24, LOCK, LOCK_SOFT, -60 + 37 * i, True)
        T(cx + 36, cy - 4, name, 13, "white")
        T(cx + 36, cy + 16, val, 15, "#F7E3D8", "bold")
    gy += gh + 12
# adjustable sample knobs
R(mx + 18, gy, mw - 36, 104, DIAL_SOFT, DIAL, rx=12, sw=2.5)
T(mx + 32, gy + 24, "樣本旋鈕（每個 subsample 只轉這裡）", 14, DIAL, "bold")
knob(mx + 90, gy + 70, 28, DIAL, "white", 20, False)
T(mx + 128, gy + 64, "purity", 15, INK, "bold")
T(mx + 128, gy + 86, "0.97 → 0.14", 14, DIAL, "bold")
knob(mx + 330, gy + 70, 28, DIAL, "white", -40, False)
T(mx + 368, gy + 64, "coverage、SNV 數", 15, INK, "bold")
T(mx + 368, gy + 86, "照各 subsample 實際值", 13, DIAL)
step_badge(mx + mw - 30, my + 30, 1)

# ---- output chute and simulated sheets ----
arrow(mx + mw, my + 300, 760, my + 300, SIM, 4)
T(668, my + 288, "吐出", 13, SIM, "bold")
sx, sy = 770, 140
T(sx, sy - 12, "模擬 bulk 資料（每個 purity 200 次）", 15, SIM, "bold")
for i, (lab, pur, *_r) in enumerate(SAMPLES):
    y = sy + i * 82
    for k in range(3):
        R(sx + 8 - k * 4, y + 8 - k * 4, 190, 62, "white", SIM, rx=6, sw=1.2)
    T(sx + 14, y + 28, f"purity {pur}", 14, INK, "bold")
    T(sx + 14, y + 50, "depth、alt、HP1／HP2／HP0", 11.5, MUTED)
step_badge(sx - 22, sy - 17, 3)

# ---- real samples ----
rx0 = 1110
T(rx0, sy - 12, "真實 HCC1395 ONT subsample", 15, REAL, "bold")
for i, (lab, pur, t, n, calls) in enumerate(SAMPLES):
    y = sy + i * 82
    R(rx0, y, 350, 66, "white", REAL, rx=8, sw=1.5)
    T(rx0 + 12, y + 24, lab, 15, INK, "bold")
    bw = 150
    R(rx0 + 12, y + 34, bw * t / 50, 14, TUMOR, rx=3)
    R(rx0 + 12 + bw * t / 50, y + 34, bw * n / 50, 14, NORMAL, rx=3)
    T(rx0 + 175, y + 24, f"purity {pur}", 13, REAL, "bold")
    T(rx0 + 175, y + 46, f"ClairS {calls} SNV", 12, MUTED)
    if i == 0:
        T(rx0 + 290, y + 46, "已用來校正", 11, DIAL, "bold")
T(rx0, sy + 5 * 82 + 6, "條形：紅＝tumor reads，灰＝normal reads（各 0–50×）", 11.5, MUTED)
step_badge(rx0 - 22, sy - 17, 2)

# ---- comparison ----
cy0 = 590
R(770, cy0, 690, 150, "white", INK, rx=14, sw=2)
T(790, cy0 + 30, "比較：每個 purity 各自做 PPC", 16, INK, "bold")
T(790, cy0 + 56, "・13 項統計量的相對差距（同一個 stats() 函式）", 13)
T(790, cy0 + 78, "・holdout 分布：VAF、depth、alt 的 KS 距離；LOH 區 minor HP 的形狀", 13)
T(790, cy0 + 100, "・趨勢：哪一項隨 purity 下降而系統性變差", 13)
T(790, cy0 + 126, "通過：每個 purity 平均 |rel| ≲ 0.1，且沒有統計量隨 purity 一路變差", 13, SIM, "bold")
arrow(970, sy + 5 * 82 - 10, 970, cy0 - 4, SIM, 3)
arrow(1285, sy + 5 * 82 + 16, 1285, cy0 - 4, REAL, 3)
step_badge(1440, cy0 + 22, 4)

# ---- verdict strip ----
vy = 790
R(40, vy, 1420, 190, "white", LINE, rx=14)
T(60, vy + 32, "判讀：差距隨 purity 怎麼變，指向哪個零件要改", 16, INK, "bold")
step_badge(1440, vy + 22, 5)
rows = [
    ("各 purity 都接近", "機制可以推廣到不同 purity；旋鈕值仍只代表 HCC1395", SIM),
    ("低 purity 時 VAF 低端、SNV 數不對", "模擬的 caller 門檻太簡化（ClairS 對低 VAF 的漏抓沒模擬）", DIAL),
    ("低 purity 時 HP、minor HP 不對", "normal 細胞的 read 在 HP 拆分中的處理有問題", DIAL),
    ("所有 purity 都偏同一方向", "t50_n00 上的校正值本身有偏差，或少了某個機制", DIAL),
]
for i, (cond, meaning, c) in enumerate(rows):
    y = vy + 64 + i * 32
    out.append(f'<circle cx="68" cy="{y - 5}" r="6" fill="{c}"/>')
    T(84, y, cond, 14, INK, "bold")
    T(470, y, "→ " + meaning, 14, INK)

out.append("</svg>")
open(sys.argv[1], "w").write("\n".join(out))
print(sys.argv[1])
