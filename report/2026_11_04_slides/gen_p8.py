"""Slide t1-machines (2026-11-04 deck, page 8): every long read field in diplosim's simulated bulk output,
each with a small schematic, SNV1 on HP1 and SNV2 on HP2 side by side. User comment 2026-11-02.
Values: data/diplosim_default_seed1 (n_clones 3, n_snv 450, seed 1, coverage 53, purity 0.9):
  SNV1 = VAR_POS 3 (ALLELE A), SNV2 = VAR_POS 7 (ALLELE B), LOH example = VAR_POS 2 (events snv,loss_A).
CONIPHER comparison: upstream TRACERx_simulation_tool/src/evolution.py:169-194 (A/B events exist, SNV always on A).
Run: python3 gen_p8.py (writes project/slides/t1-machines.html)."""
import csv
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "project" / "slides" / "t1-machines.html"
DATA = HERE / "data" / "diplosim_default_seed1"
F = "Noto Sans TC, Arial, sans-serif"
P = "font-family:'Noto Sans TC', Arial, sans-serif"
INK, SUB, BLUE, ORANGE, LINE, BG = "#1F2A37", "#6B7480", "#2F6DB5", "#C96A1B", "#E3E1DA", "#F7F6F2"
HP1, HP1S, HP2, HP2S, HP0, RED = "#2C5F9E", "#8FB3E0", "#D9772B", "#F2B880", "#9AA3AE", "#D23A2E"

ROWS = {r["VAR_POS"]: r for r in csv.DictReader(open(DATA / "diplosim.tsv"), delimiter="\t")}
S1, S2, LOH = ROWS["3"], ROWS["7"], ROWS["2"]
assert S1["ALLELE"] == "A" and S2["ALLELE"] == "B"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=24, weight=400, fill=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{F}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def rect(x, y, w, h, fill="#FFFFFF", stroke=LINE, sw=2, rx=12, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def ln(x1, y1, x2, y2, col, w=10, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{extra}/>'


def dot(x, y, alt, r=7):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RED}" stroke="#FFFFFF" stroke-width="2"/>' if alt else
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>')


def n(v):
    return str(int(float(v)))


W, H = 1664, 572
s = ""

# ---------------- left: schematic of one bulk sample ----------------
LW = 600
A, B = 200, 430  # SNV1, SNV2 x
s += rect(1, 1, LW - 2, H - 2)
s += rect(16, 14, 72, 34, fill="none", stroke=SUB, sw=2, rx=17) + t(52, 39, "示意", 24, 700, SUB, "middle")
s += t(104, 40, "腫瘤細胞的兩條 HP", 24, 700, INK)
s += t(A, 78, "SNV1", 22, 700, INK, "middle") + t(B, 78, "SNV2", 22, 700, INK, "middle")
s += t(24, 112, "HP1", 24, 700, HP1) + ln(96, 104, 560, 104, HP1, 16)
s += t(24, 152, "HP2", 24, 700, HP2) + ln(96, 144, 560, 144, HP2, 16)
s += dot(A, 104, True, 9) + dot(B, 144, True, 9)
for x in (A, B):
    s += ln(x, 88, x, 452, SUB, 2, ' stroke-dasharray="4 6"')
s += t(24, 196, "定序後的 long read", 24, 700, INK)
groups = [("HP1 read", HP1, HP1S, HP1, (True, False)), ("HP2 read", HP2, HP2, HP2S, (False, True)),
          ("unphased", HP0, HP0, HP0, None)]
y = 222
for label, lab_col, c_a, c_b, alts in groups:
    s += t(24, y + 26, label, 20, 700, lab_col if label != "unphased" else SUB)
    for i in range(3):
        yy = y + i * 18
        off = (i * 23) % 40
        if alts is None:  # unphased: tumour reads from either HP, colour unknown
            a_alt, b_alt = (i == 0), (i == 2)
            s += ln(130 + off, yy, 300 + off, yy, HP0, 9) + dot(A, yy, a_alt, 6)
            s += ln(360 - off, yy, 540 - off, yy, HP0, 9) + dot(B, yy, b_alt, 6)
        else:
            # long reads near SNV1 and SNV2; alt only on the HP that carries the SNV (a normal-cell read is ref)
            s += ln(130 + off, yy, 300 + off, yy, c_a, 9) + dot(A, yy, alts[0] and i < 2, 6)
            s += ln(360 - off, yy, 540 - off, yy, c_b, 9) + dot(B, yy, alts[1] and i < 2, 6)
    y += 76
s += dot(40, 470, True, 7) + t(56, 478, "alt", 22, 400, INK) + dot(120, 470, False, 7) + t(136, 478, "ref", 22, 400, INK)
s += t(24, 516, "diplosim 不輸出 read，只輸出每個 SNV", 22, 400, SUB)
s += t(24, 546, "的 read 計數與真值 →", 22, 400, SUB)

# ---------------- right: the long read fields ----------------
RX = LW + 24
RW = W - RX
C1, C2 = RX + 640, RX + 840  # SNV1, SNV2 value columns (centres)
s += t(RX + 8, 30, "輸出裡的 long read 資訊", 26, 700, INK)
s += t(C1, 30, "SNV1（在 HP1）", 22, 700, HP1, "middle") + t(C2, 30, "SNV2（在 HP2）", 22, 700, HP2, "middle")
rows = [
    ("new", "① 依 HP 分開的 read 數", "HP1_／HP2_／HP0_ REF、ALT", "reads"),
    ("new", "② SNV 在哪條 HP", "ALLELE（A＝HP1、B＝HP2）", "allele"),
    ("keep", "③ 每條 HP 的 copy number", "CN_A、CN_B", "cn"),
    ("keep", "④ 每條 HP 的 CN 事件（真值）", "truth/events.tsv", "events"),
    ("none", "⑤ 同一條 read 上兩個 SNV", "共現、phase block", "none"),
]
y0, rh, gap = 46, 96, 8
for i, (kind, name, cols, key) in enumerate(rows):
    y = y0 + i * (rh + gap)
    if kind == "none":
        s += rect(RX + 1, y, RW - 2, rh, fill=BG, stroke=SUB, dash="8 6")
    else:
        s += rect(RX + 1, y, RW - 2, rh, stroke=BLUE if kind == "new" else LINE, sw=3 if kind == "new" else 2)
    # mini icon
    ix, iy = RX + 18, y + 18
    if key == "reads":
        for j, c in enumerate((HP1, HP2, HP0)):
            s += ln(ix, iy + 6 + j * 20, ix + 70, iy + 6 + j * 20, c, 9)
    elif key == "allele":
        s += ln(ix, iy + 14, ix + 70, iy + 14, HP1, 12) + ln(ix, iy + 44, ix + 70, iy + 44, HP2, 12)
        s += dot(ix + 24, iy + 14, True, 7) + dot(ix + 50, iy + 44, True, 7)
    elif key == "cn":
        for j in range(2):
            s += f'<rect x="{ix}" y="{iy + 4 + j * 16}" width="30" height="12" rx="3" fill="{HP1}"/>'
        s += f'<rect x="{ix + 40}" y="{iy + 20}" width="30" height="12" rx="3" fill="{HP2}"/>'
        s += t(ix + 15, iy + 56, "2", 20, 700, HP1, "middle") + t(ix + 55, iy + 56, "1", 20, 700, HP2, "middle")
    elif key == "events":
        s += f'<rect x="{ix}" y="{iy + 4}" width="30" height="12" rx="3" fill="{HP1}"/>'
        s += f'<rect x="{ix}" y="{iy + 24}" width="30" height="12" rx="3" fill="none" stroke="{HP2}" stroke-width="2" stroke-dasharray="4 3"/>'
        s += (f'<line x1="{ix + 36}" y1="{iy + 20}" x2="{ix + 52}" y2="{iy + 20}" stroke="{ORANGE}" stroke-width="3"/>'
              f'<polygon points="{ix + 60},{iy + 20} {ix + 50},{iy + 14} {ix + 50},{iy + 26}" fill="{ORANGE}"/>')
        s += t(ix + 30, iy + 58, "loss", 20, 700, ORANGE, "middle")
    else:
        s += ln(ix, iy + 28, ix + 74, iy + 28, HP0, 10) + dot(ix + 18, iy + 28, True, 6) + dot(ix + 56, iy + 28, True, 6)
        s += t(ix + 37, iy + 12, "?", 22, 700, ORANGE, "middle")
    tx = RX + 112
    s += t(tx, y + 38, name, 26, 700, SUB if kind == "none" else INK)
    s += t(tx, y + 72, cols, 20, 400, SUB)
    tag = {"new": ("新寫", BLUE), "keep": ("沿用 CONIPHER", SUB), "none": ("還沒有", ORANGE)}[kind]
    s += t(RX + 528, y + 72, tag[0], 20, 700, tag[1], "end")
    # values
    vy = y + 30
    if key == "reads":
        for cx, r in ((C1, S1), (C2, S2)):
            for j, (lab, col, rk, ak) in enumerate((("HP1", HP1, "HP1_REF", "HP1_ALT"), ("HP2", HP2, "HP2_REF", "HP2_ALT"),
                                                    ("未分", SUB, "HP0_REF", "HP0_ALT"))):
                s += t(cx - 84, vy - 4 + j * 26, lab, 20, 700, col)
                s += t(cx + 90, vy - 4 + j * 26, f"ref {r[rk]}、alt {r[ak]}", 20, 400, INK, "end")
    elif key == "allele":
        s += t(C1, vy + 22, "A（HP1）", 24, 700, HP1, "middle") + t(C2, vy + 22, "B（HP2）", 24, 700, HP2, "middle")
    elif key == "cn":
        for cx, r in ((C1, S1), (C2, S2)):
            s += t(cx, vy + 22, f"{n(r['CN_A'])}、{n(r['CN_B'])}", 24, 700, INK, "middle")
    elif key == "events":
        s += t((C1 + C2) / 2, vy + 4, "例：位置 2 是 snv、loss_A", 22, 700, INK, "middle")
        s += t((C1 + C2) / 2, vy + 36, f"→ CN {n(LOH['CN_A'])}、{n(LOH['CN_B'])}，HP1 只剩 ref {LOH['HP1_REF']} 條", 22, 400, INK, "middle")
    else:
        s += t((C1 + C2) / 2, vy + 4, "diplosim 只輸出計數，不產生 read", 22, 700, ORANGE, "middle")
        s += t((C1 + C2) / 2, vy + 36, "要共現需改成逐條 read 產生", 22, 400, SUB, "middle")

aria = (f"左：示意一個 bulk 樣本，HP1、HP2 兩條 HP，SNV1 在 HP1，SNV2 在 HP2；定序後 HP1 read 在 SNV1 帶 alt，HP2 read 在 SNV2 帶 alt，"
        f"unphased read 分不出 HP；diplosim 不輸出 read，只輸出計數與真值。右：輸出裡的 long read 資訊，"
        f"① 依 HP 分開的 read 數（新寫）：SNV1 HP1 ref {S1['HP1_REF']} alt {S1['HP1_ALT']}、HP2 ref {S1['HP2_REF']} alt {S1['HP2_ALT']}、未分 ref {S1['HP0_REF']} alt {S1['HP0_ALT']}；"
        f"SNV2 HP1 ref {S2['HP1_REF']} alt {S2['HP1_ALT']}、HP2 ref {S2['HP2_REF']} alt {S2['HP2_ALT']}、未分 ref {S2['HP0_REF']} alt {S2['HP0_ALT']}。"
        f"② SNV 在哪條 HP（新寫）：SNV1 A 即 HP1，SNV2 B 即 HP2。③ 每條 HP 的 copy number（沿用 CONIPHER，A、B 對上 HP）：兩個都是 1、1。"
        f"④ 每條 HP 的 CN 事件真值：例如位置 2 是 snv、loss_A，CN 0、1，HP1 只剩 {LOH['HP1_REF']} 條 ref。⑤ 還沒有：同一條 read 上兩個 SNV 的共現與 phase block")
svg = f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="{esc(aria)}" viewBox="0 0 {W} {H}" style="width:{W}px; height:{H}px">{s}</svg>'

notes = ("這頁整理 diplosim 模擬的 bulk 資料裡，全部的 long read 資訊。左邊是示意：腫瘤細胞有兩條 HP，SNV1 在 HP1，SNV2 在 HP2。"
         "定序後，HP1 的 read 在 SNV1 帶 alt，HP2 的 read 在 SNV2 帶 alt；灰色是分不出 HP 的 unphased read。diplosim 不輸出 read 本身，只輸出每個 SNV 的計數和真值。"
         f"右邊五項。第一，依 HP 分開的 read 數，是新寫的：SNV1 的 alt {S1['HP1_ALT']} 條都在 HP1，SNV2 的 alt 大多在 HP2，有 {S2['HP2_ALT']} 條。"
         "第二，SNV 在哪條 HP，也是新寫的；CONIPHER 的 SNV 一律在 allele A。"
         "第三和第四，每條 HP 的 copy number 和 CN 事件，CONIPHER 本來就有 A、B，diplosim 沿用，差別是把 A 對到 HP1、B 對到 HP2，和 read 數對得起來。"
         f"例如位置 2 先有 SNV 再丟掉 allele A，copy number 變成 0 和 1，HP1 只剩 {LOH['HP1_REF']} 條 ref，來自 normal 細胞。"
         "第五項還沒有：同一條 read 上兩個 SNV 是否一起出現，以及 phase block。diplosim 只輸出計數，要有共現得改成逐條 read 產生。接下來看怎麼檢查這些輸出接近真實。")

html = f'''<section id="t1-machines" style="display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2">
  <p style="{P}; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5">1 · 兩台機器</p>
  <h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37">diplosim 每個 SNV 多記 HP1／HP2 的 read 數與 SNV 所在的 HP；同一條 read 的共現還沒有</h2>
  {svg}
  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">
    <p style="{P}; font-size:24px; color:#6b7480">2026-11-04 diplosim：兩台機器與真實 long read</p>
    <p style="{P}; font-size:24px; color:#6b7480">8 / 13</p>
  </div>
  <aside>{esc(notes)}</aside>
</section>
'''
OUT.write_text(html)
print(OUT)
