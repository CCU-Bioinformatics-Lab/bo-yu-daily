"""Generate the four knob pages k-allele, k-tag, k-error, k-cn (2026-11-04 deck)."""
import sys
from pathlib import Path

OUT = Path("/bip8_disk/boyu114/main_work/report/2026_11_04_slides/project/slides")
W, H = 1664, 572
F = "Noto Sans TC, Arial, sans-serif"
HP1, HP1S, HP2, HP2S, RED, HP0 = "#2C5F9E", "#8FB3E0", "#D9772B", "#F2B880", "#D23A2E", "#9AA3AE"
INK, SUB, BLUE, ORANGE, LINE = "#1F2A37", "#6B7480", "#2F6DB5", "#C96A1B", "#E3E1DA"
HL = "#FCEBDA"  # changed-field fill

# column x ranges
LX, LW = 0, 668
MX, MW = 742, 330
RX, RW = 1146, 518


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=24, weight=400, fill=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{F}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def rect(x, y, w, h, fill="#FFFFFF", stroke=LINE, sw=2, rx=12, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')


def line(x1, y1, x2, y2, color, w=10, extra=""):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round"{extra}/>')


def pill(x, y, s, color, w=None):
    w = w or 24 * len(s) + 24
    return (rect(x, y, w, 34, fill="none", stroke=color, sw=2, rx=17)
            + t(x + w / 2, y + 25, s, 24, 700, color, "middle")), w


def alt_dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="{RED}" stroke="#FFFFFF" stroke-width="2"/>'


def ref_dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>'


def read(x1, x2, y, color, sites=()):
    """sites: list of (x, 'alt'|'ref')."""
    s = line(x1, y, x2, y, color, 12)
    for sx, kind in sites:
        s += alt_dot(sx, y) if kind == "alt" else ref_dot(sx, y)
    return s


def arrow(x1, y, x2, color, label):
    return (line(x1, y, x2 - 14, y, color, 5)
            + f'<polygon points="{x2},{y} {x2 - 18},{y - 11} {x2 - 18},{y + 11}" fill="{color}"/>'
            + t((x1 + x2) / 2, y - 18, label, 24, 700, color, "middle"))


def varrow(x, y1, y2, color, w=4):
    return (line(x, y1, x, y2 - 12, color, w)
            + f'<polygon points="{x},{y2} {x - 9},{y2 - 14} {x + 9},{y2 - 14}" fill="{color}"/>')


def harrow(x1, y, x2, color, w=4):
    return (line(x1, y, x2 - 12, y, color, w)
            + f'<polygon points="{x2},{y} {x2 - 14},{y - 9} {x2 - 14},{y + 9}" fill="{color}"/>')


def machine(x, y, scale=0.75):
    return (f'<g transform="translate({x},{y}) scale({scale})"><polygon points="20,2 52,2 44,14 28,14" fill="{BLUE}"/>'
            f'<rect x="6" y="14" width="60" height="34" rx="6" fill="{BLUE}"/>'
            f'<rect x="14" y="24" width="14" height="6" rx="3" fill="{HP1}"/>'
            f'<rect x="30" y="24" width="14" height="6" rx="3" fill="{HP2}"/>'
            f'<rect x="46" y="24" width="12" height="6" rx="3" fill="{HP0}"/>'
            f'<rect x="24" y="48" width="24" height="6" fill="#C3CAD3"/></g>')


def knob(cx, cy, mode):
    """mode: 'up' (0.5), 'upright' (0.8), 'off' (as on the overview page)."""
    end = {"up": (cx, cy - 16, BLUE), "upright": (cx + 8.0, cy - 13.9, BLUE),
           "off": (cx - 11.3, cy + 11.3, HP0)}[mode]
    return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="#FFFFFF" stroke="#4A5568" stroke-width="3"/>'
            + line(cx, cy, end[0], end[1], end[2], 5)
            + f'<circle cx="{cx}" cy="{cy}" r="4" fill="#4A5568"/>')


HATCH = ('<defs><pattern id="{id}" width="14" height="14" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><rect width="14" height="14" fill="#f7f6f2"/>'
         '<rect width="5" height="14" fill="#e3e1da"/></pattern></defs>')


def column_heads():
    return (t(LX, 30, "真實 long read 看到什麼", 28, 700, INK)
            + t(MX + MW / 2, 30, "旋鈕", 28, 700, INK, "middle")
            + t(RX, 30, "輸出多了什麼", 28, 700, INK))


def left_frames(source):
    """Two stacked cards: schematic (示意) on top, real numbers (實際結果) below."""
    s = rect(LX + 1, 48, LW - 2, 262)
    p, _ = pill(LX + 16, 60, "示意", SUB)
    s += p
    s += rect(LX + 1, 324, LW - 2, 246)
    p, w = pill(LX + 16, 336, "實際結果", ORANGE)
    s += p + t(LX + 16 + w + 14, 361, source, 24, 400, SUB)
    return s


def middle(group, knobs, coni_note, hid):
    """knobs: list of (label, value, mode)."""
    s = rect(MX + 1, 48, MW - 2, 372, stroke=BLUE, sw=3, rx=16)
    s += machine(MX + 16, 60) + t(MX + 80, 92, "diplosim 面板", 26, 700, INK)
    s += rect(MX + 16, 116, MW - 32, 290, fill="#F7F6F2", stroke="none", sw=0)
    s += t(MX + MW / 2, 152, group, 26, 700, INK, "middle")
    n = len(knobs)
    gap = 224 / n
    for i, (label, value, mode) in enumerate(knobs):
        cy = 170 + gap * (i + 0.5) + 6
        s += knob(MX + 56, cy, mode)
        s += t(MX + 92, cy - 4, label, 24, 400, INK)
        s += t(MX + 92, cy + 26, value, 24, 700, BLUE if mode != "off" else BLUE)
    # CONIPHER: none (hatched)
    s += HATCH.format(id=hid)
    s += (f'<rect x="{MX + 1}" y="436" width="{MW - 2}" height="134" rx="12" fill="url(#{hid})" '
          f'stroke="{LINE}" stroke-width="2"/>')
    s += rect(MX + 24, 452, MW - 48, 102, fill="#F7F6F2", stroke="none", sw=0, rx=8)
    s += t(MX + MW / 2, 490, "CONIPHER：沒有", 24, 700, SUB, "middle")
    s += t(MX + MW / 2, 530, coni_note, 24, 400, SUB, "middle")
    return s


ROWS = [  # key, label, value(s)
    ("count", "ref、alt", "ref 36、alt 21"),
    ("cn", "allele A、B copy number", "1、1"),
    ("mult", "帶 SNV 的份數", "1"),
    ("clone", "clone、CCF", "trunk、1.0"),
    ("hp1", "HP1", ("ref 0", "alt 19")),
    ("hp2", "HP2", ("ref 27", "alt 0")),
    ("hp0", "unphased", ("ref 9", "alt 2")),
    ("truth", "真值：SNV 在 allele", "A（HP1）"),
]
HPCOL = {"hp1": HP1, "hp2": HP2, "hp0": HP0}


def right(rows_hl, cells_hl, note, override=None, head="SNV1 的輸出一列"):
    """rows_hl: keys of whole rows to highlight; cells_hl: (key, 0|1) single cells;
    override: {key: value} shown instead of the default SNV1 row (a rerun with knobs on)."""
    s = t(RX, 72, head, 24, 700, INK)
    p, _ = pill(RX + 196, 48, "實際結果", ORANGE)
    s += p
    y0, rh = 92, 50
    for i, (key, label, val) in enumerate(ROWS):
        val = (override or {}).get(key, val)
        y = y0 + i * (rh + 6)
        hl = key in rows_hl
        s += rect(RX + 1, y, RW - 2, rh, fill=HL if hl else "#FFFFFF",
                  stroke=ORANGE if hl else LINE, sw=3 if hl else 2, rx=10)
        ty = y + 34
        if key in HPCOL:
            s += line(RX + 16, y + rh / 2, RX + 40, y + rh / 2, HPCOL[key], 8)
            s += t(RX + 52, ty, label, 24, 700, HPCOL[key] if key != "hp0" else SUB)
            for j, v in enumerate(val):
                vx = RX + 270 + j * 120
                if (key, j) in cells_hl:
                    s += rect(vx - 8, y + 7, 106, 36, fill=HL, stroke=ORANGE, sw=3, rx=8)
                s += t(vx, ty, v, 24, 700 if (key, j) in cells_hl else 400, INK)
        else:
            s += t(RX + 16, ty, label, 24, 400, SUB)
            s += t(RX + RW - 16, ty, val, 24, 700, INK, "end")
    ly = y0 + 8 * (rh + 6) + 6
    s += rect(RX + 1, ly, 40, 26, fill=HL, stroke=ORANGE, sw=3, rx=6)
    s += t(RX + 54, ly + 22, note, 24, 400, SUB)
    return s


def svg(label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="{esc(label)}" viewBox="0 0 {W} {H}" '
            f'style="width:{W}px; height:{H}px">{body}</svg>')


def arrows():
    return (arrow(LX + LW + 8, 300, MX - 8, SUB, "模仿")
            + arrow(MX + MW + 8, 300, RX - 8, ORANGE, "改動"))


# ---------------------------------------------------------------- k-allele
def left_allele():
    s = ""
    a, b = 200, 470  # SNV1, SNV2 sites
    s += t(a, 82, "SNV1", 24, 700, INK, "middle") + t(b, 82, "SNV2", 24, 700, INK, "middle")
    for x in (a, b):
        s += line(x, 94, x, 296, SUB, 2, ' stroke-dasharray="4 6"')
    s += t(24, 140, "HP1", 24, 700, HP1) + t(24, 236, "HP2", 24, 700, HP2)
    for i, y in enumerate((112, 136, 160)):
        s += read(110 + i * 20, 280 + i * 12, y, HP1S, [(a, "alt")])
        s += read(380 + i * 18, 560 - i * 10, y, HP1, [(b, "ref")])
    for i, y in enumerate((208, 232, 256)):
        s += read(120 + i * 16, 290 - i * 14, y, HP2, [(a, "ref")])
        s += read(390 + i * 10, 580 - i * 16, y, HP2S, [(b, "alt")])
    s += alt_dot(628, 112) + t(628, 150, "alt", 24, 400, INK, "middle")
    s += ref_dot(628, 196) + t(628, 234, "ref", 24, 400, INK, "middle")
    # real numbers
    s += t(24, 412, "alt 集中在一條 HP 的 SNV", 24, 700, INK)
    bx, bw, by = 24, 620, 432
    w1 = round(bw * 14707 / (14707 + 14261))
    s += rect(bx, by, w1, 60, fill=HP1, stroke="none", sw=0, rx=6)
    s += rect(bx + w1, by, bw - w1, 60, fill=HP2, stroke="none", sw=0, rx=6)
    s += t(bx + 18, by + 40, "HP1  14,707", 24, 700, "#FFFFFF")
    s += t(bx + bw - 18, by + 40, "HP2  14,261", 24, 700, "#FFFFFF", "end")
    mid = bx + bw / 2
    s += line(mid, by - 6, mid, by + 76, INK, 2, ' stroke-dasharray="4 4"')
    s += t(mid, by + 104, "一半", 24, 400, SUB, "middle")
    s += t(bx + bw, by + 104, "HP2 占 49.2%", 24, 700, HP2, "end")
    return s


def page(sid, n, title, svg_label, body, aside):
    return f'''<section id="{sid}" style="display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2">
  <p style="font-family:'Noto Sans TC', Arial, sans-serif; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5">1 · 兩台機器</p>
  <h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37">{esc(title)}</h2>
  {svg(svg_label, body)}
  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">
    <p style="font-family:'Noto Sans TC', Arial, sans-serif; font-size:24px; color:#6b7480">2026-11-04 diplosim：兩台機器與真實 long read</p>
    <p style="font-family:'Noto Sans TC', Arial, sans-serif; font-size:24px; color:#6b7480">{n + 1} / 13</p>
  </div>
  <aside>{esc(aside)}</aside>
</section>
'''


SRC = "HCC1395 long read，ASCAT 估計 purity 0.97"
REAL_PER_SNV = "/bip8_disk/boyu114/main_work/lab_report/2026-10-31_diplosim_ppc_hcc1395_lost045/tables/real_per_snv.tsv"

pages = {}

pages["k-allele"] = page(
    "k-allele", 3,
    "真實 SNV 約一半在 HP2（49.2%）；diplosim 預設讓 SNV 以 0.5 的機率落在 allele B",
    "左：真實 long read 中，SNV1 的 alt 只在 HP1 的 read，SNV2 的 alt 只在 HP2；HCC1395 實際有 14,707 個 SNV 在 HP1、14,261 個在 HP2。中：diplosim 面板的 SNV 的 allele 旋鈕，allele B 機率預設 0.5；CONIPHER 沒有，SNV 一律在 allele A。右：SNV1 輸出一列中，真值欄與 HP1、HP2 的 alt 被改動",
    column_heads() + left_frames(SRC) + left_allele()
    + middle("SNV 的 allele", [("allele B 機率", "0.5", "up")], "SNV 一律在 allele A", "hatchKA")
    + arrows()
    + right({"truth"}, {("hp1", 1), ("hp2", 1)}, "這組旋鈕改動的欄位"),
    "這頁要看的是：真實資料的 SNV 大約一半在 HP2；diplosim 預設讓 SNV 以 0.5 的機率落在 allele B。"
    "左上示意，SNV1 的 alt 只在 HP1 的 read，SNV2 的 alt 只在 HP2。"
    "左下是 HCC1395 實際結果：HP1 14,707 個，HP2 14,261 個，HP2 占 49.2%。"
    "中間旋鈕 allele B 機率預設 0.5；斜線框是 CONIPHER，SNV 一律在 allele A。"
    "右邊 SNV1 這列，橘色是改動的欄位：真值在 allele A，所以 HP1 有 alt 19 條，HP2 是 0。"
    "下一頁看 HP 標記。",
)


# ---------------------------------------------------------------- k-tag
def left_tag():
    s = ""
    snv = 330
    s += t(snv, 82, "SNV", 24, 700, INK, "middle")
    s += line(snv, 94, snv, 296, SUB, 2, ' stroke-dasharray="4 6"')
    diamonds = (120, 540)
    for dx in diamonds:
        s += f'<polygon points="{dx},92 {dx + 10},104 {dx},116 {dx - 10},104" fill="{INK}"/>'
    s += read(100, 360, 140, HP1, [(snv, "ref")])
    s += read(110, 380, 164, HP1S, [(snv, "alt")])
    s += read(300, 560, 188, HP2, [(snv, "ref")])
    s += read(310, 580, 212, HP2, [(snv, "ref")])
    s += read(250, 430, 240, HP0, [(snv, "alt")])
    s += t(24, 150, "HP1", 24, 700, HP1) + t(24, 208, "HP2", 24, 700, HP2)
    s += t(450, 248, "沒蓋到 ◆", 24, 700, SUB)
    s += t(450, 280, "→ unphased", 24, 700, SUB)
    s += f'<polygon points="34,268 44,280 34,292 24,280" fill="{INK}"/>'
    s += t(54, 289, "germline 差異位置", 24, 400, INK)
    p, _ = pill(LX + LW - 96, 60, "推論", SUB, 80)
    s += p
    # real numbers: 20 real HCC1395 t50 sites, picked at the 2.5%, 7.5%, ..., 97.5% quantiles of the
    # per-site tagged fraction (same site filter as tools/diplosim_ppc_hcc1395.py stats(): alt >= 5,
    # VAF >= 0.10, depth >= 20); each bar is that site's HP1 / HP2 / unphased read share.
    import csv as _csv
    sites = []
    with open(REAL_PER_SNV) as f:
        for r in _csv.DictReader(f, delimiter="\t"):
            x = [int(r[k]) for k in ("ref1", "alt1", "ref2", "alt2", "ref0", "alt0")]
            d, a = sum(x), x[1] + x[3] + x[5]
            if a >= 5 and a / d >= 0.10 and d >= 20:
                sites.append(((x[0] + x[1]) / d, (x[2] + x[3]) / d, (x[4] + x[5]) / d))
    sites.sort(key=lambda v: v[0] + v[1])
    pick = [sites[int((i + 0.5) / 20 * len(sites))] for i in range(20)]
    s += t(24, 392, "20 個真實位點（依有標記的比例排序）", 24, 400, SUB)
    bx, by, bh, bw, gap = 24, 408, 120, 16, 6
    for i, (h1, h2, h0) in enumerate(pick):
        x = bx + i * (bw + gap)
        y0 = by + bh
        for frac, col in ((h1, HP1), (h2, HP2), (h0, HP0)):
            hgt = frac * bh
            s += f'<rect x="{x}" y="{y0 - hgt:.1f}" width="{bw}" height="{hgt:.1f}" fill="{col}"/>'
            y0 -= hgt
        if h1 + h2 < 0.5:
            s += f'<polygon points="{x + bw / 2},{by + bh + 6} {x + bw / 2 - 7},{by + bh + 18} {x + bw / 2 + 7},{by + bh + 18}" fill="{ORANGE}"/>'
    mean_y = by + bh * (1 - 0.862)
    s += f'<line x1="{bx - 4}" y1="{mean_y:.1f}" x2="{bx + 20 * (bw + gap)}" y2="{mean_y:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>'
    rx = bx + 20 * (bw + gap) + 18
    s += t(rx, 424, "虛線＝平均", 24, 400, INK)
    s += t(rx, 454, "有標記 86.2%", 24, 700, INK)
    s += f'<polygon points="{rx + 8},{488} {rx + 1},{500} {rx + 15},{500}" fill="{ORANGE}"/>'
    s += t(rx + 22, 500, "標記 < 0.5", 24, 400, INK)
    s += t(rx, 530, "的位點 10.3%", 24, 700, ORANGE)
    return s


pages["k-tag"] = page(
    "k-tag", 4,
    "真實有 13.8% 的 read 沒有 HP 標記，而且各位點不同，所以 diplosim 加上標記比例與位點間差異",
    "左：read 沒蓋到 germline 差異位置就分不出 HP，成為 unphased（推論）；HCC1395 實際：20 個真實位點的 HP1、HP2、unphased read 比例長條，平均有標記 86.2%，標記比例小於 0.5 的位點 10.3%。中：HP 標記旋鈕，標記比例預設 0.8，位點間差異預設關閉；CONIPHER 沒有，不分 HP。右：SNV1 輸出一列中 unphased 的 ref 9、alt 2 被改動",
    column_heads() + left_frames(SRC) + left_tag()
    + middle("HP 標記", [("標記比例", "0.8（暫定）", "upright"), ("位點間差異", "關閉", "off")],
             "不分 HP", "hatchKT")
    + arrows()
    + right({"hp0"}, set(), "這組旋鈕改動的欄位"),
    "這頁要看的是：真實有 13.8% 的 read 沒有 HP 標記，而且各位點不同。"
    "左上示意：read 蓋到黑色菱形，也就是 germline 差異位置，才分得出 HP；灰色這條沒蓋到，就是 unphased，這是我們的推論。"
    "左下是實際結果：20 根長條是 20 個真實位點，各自的 HP1、HP2、unphased read 比例。大部分位點幾乎沒有灰色，但左邊有橘色三角形的位點，分得出 HP 的 read 不到一半，這種位點占 10.3%；虛線是平均，86.2% 的 read 有標記。"
    "中間兩個旋鈕：標記比例 0.8，暫定；位點間差異預設關閉。CONIPHER 不分 HP。"
    "右邊橘色的 unphased ref 9、alt 2 就是改動的欄位。下一頁看 read 錯誤。",
)


# ---------------------------------------------------------------- k-error
def left_error():
    s = ""
    a, b = 175, 365
    s += t(a, 82, "SNV1", 24, 700, INK, "middle") + t(b, 82, "SNV2", 24, 700, INK, "middle")
    for x in (a, b):
        s += line(x, 94, x, 296, SUB, 2, ' stroke-dasharray="4 6"')
    s += t(24, 140, "HP1", 24, 700, HP1) + t(24, 236, "HP2", 24, 700, HP2)
    # SNV1: alt on HP1; one base error (1), one mistag (2)
    s += read(105, 245, 112, HP1S, [(a, "alt")])
    s += read(115, 235, 136, HP1S, [(a, "alt")])
    s += read(110, 240, 160, HP1, [(a, "ref")])
    s += read(105, 245, 208, HP2, [(a, "ref")])
    s += read(115, 240, 232, HP2S, [(a, "alt")])
    s += read(110, 235, 256, HP2, [(a, "ref")])
    # SNV2: alt on HP1; two mistags (3, concentrated)
    s += read(295, 435, 112, HP1S, [(b, "alt")])
    s += read(305, 425, 136, HP1S, [(b, "alt")])
    s += read(300, 430, 160, HP1S, [(b, "alt")])
    s += read(295, 430, 208, HP2S, [(b, "alt")])
    s += read(305, 435, 232, HP2S, [(b, "alt")])
    s += read(300, 425, 256, HP2, [(b, "ref")])
    s += f'<rect x="{b - 24}" y="194" width="48" height="52" rx="8" fill="none" stroke="{ORANGE}" stroke-width="3"/>'
    s += t(262, 168, "①", 24, 700, ORANGE) + t(262, 240, "②", 24, 700, ORANGE)
    s += t(450, 230, "③", 24, 700, ORANGE)
    s += t(490, 150, "① 鹼基讀錯", 24, 400, INK)
    s += t(490, 200, "② HP 標錯", 24, 400, INK)
    s += t(490, 250, "③ 標錯集中", 24, 400, INK)
    # real numbers drawn like figs/read_error_knobs.png: HCC1395 t50 sites (alt >= 5, VAF >= 0.10, tagged alt
    # >= 3, n = 29,777) grouped by alt reads on the other HP: 0 -> 90.4%, 1 -> 7.2%, >= 2 -> 2.3%; with one
    # common rate (0.62% per alt read) the >= 2 group would be 1.1% (recomputed 2026-11-01).
    s += t(24, 392, "另一條 HP 上有幾條 alt", 24, 400, SUB)
    groups = (("0 條", 0, "90.4%"), ("1 條", 1, "7.2%"), ("≥ 2 條", 2, "2.3%"))
    for j, (lab, k, pct) in enumerate(groups):
        cx = 92 + j * 150
        s += t(cx, 424, lab, 24, 700, INK, "middle")
        for i in range(5):
            y = 442 + i * 16
            mis = i >= 5 - k
            s += line(cx - 52, y, cx + 52, y, HP2S if mis else HP1S, 8)
            s += f'<circle cx="{cx}" cy="{y}" r="5" fill="{RED}" stroke="#FFFFFF" stroke-width="1.5"/>'
            if mis:
                s += f'<rect x="{cx - 12}" y="{y - 8}" width="24" height="16" rx="3" fill="none" stroke="{ORANGE}" stroke-width="2.5"/>'
        s += t(cx, 548, pct, 32, 700, ORANGE if k == 2 else INK, "middle")
    s += f'<line x1="478" y1="404" x2="478" y2="556" stroke="{LINE}" stroke-width="2"/>'
    s += t(496, 432, "若每個位點", 24, 400, SUB)
    s += t(496, 462, "機率相同，", 24, 400, SUB)
    s += t(496, 492, "≥ 2 條只有", 24, 400, SUB)
    s += t(496, 548, "1.1%", 32, 700, SUB)
    return s


pages["k-error"] = page(
    "k-error", 5,
    "真實約一成的 SNV 在另一條 HP 也有 alt，而且集中在少數位點，所以 diplosim 加上鹼基讀錯、HP 標錯與標錯集中",
    "左：示意 read 錯誤，① 鹼基讀錯讓 alt 顯示成 ref，② HP 標錯讓 alt 跑到 HP2，③ 標錯集中在 SNV2；HCC1395 實際：另一條 HP 上沒有 alt 的位點 90.4%、1 條 7.2%、2 條以上 2.3%；若每個位點機率相同，2 條以上只有 1.1%。中：read 錯誤旋鈕，鹼基讀錯設 0.01、HP 標錯設 0.05（預設都是 0），標錯集中關閉；CONIPHER 沒有。右：把鹼基讀錯設 0.01、HP 標錯設 0.05 重跑同一個 SNV，HP1 ref 3、alt 16，HP2 ref 25、alt 2，unphased ref 8、alt 3",
    column_heads() + left_frames(SRC) + left_error()
    + middle("read 錯誤", [("鹼基讀錯", "0.01（預設 0）", "upright"), ("HP 標錯", "0.05（預設 0）", "upright"),
                          ("標錯集中", "關閉", "off")], "沒有 read 錯誤", "hatchKE")
    + arrows()
    + right(set(), {("hp1", 0), ("hp2", 1)}, "旋鈕打開後重跑同一個 SNV（示意設定）",
            {"hp1": ("ref 3", "alt 16"), "hp2": ("ref 25", "alt 2"), "hp0": ("ref 8", "alt 3")}),
    "這頁要看的是：真實約一成的 SNV，在另一條 HP 也有 alt，而且集中在少數位點，所以 diplosim 加上三個 read 錯誤旋鈕。"
    "左上示意：圈 1 鹼基讀錯，HP1 的 read 變成 ref；圈 2 HP 標錯，alt 跑到 HP2；圈 3 是 SNV2 有兩條，標錯集中。"
    "左下是實際結果，畫法和上面一樣：每個小圖是一種位點，五條帶 alt 的 read，橘框是跑到另一條 HP 的。九成的位點完全沒有，7.2% 有 1 條，2.3% 有 2 條以上；如果每個位點機率都一樣，2 條以上應該只有 1.1%，實際多一倍，所以錯誤會集中在少數位點。"
    "中間三個旋鈕預設都是 0 或關閉，這頁把鹼基讀錯設 0.01、HP 標錯設 0.05 來示範；CONIPHER 沒有這些旋鈕。"
    "右邊是把鹼基讀錯設 0.01、HP 標錯設 0.05，重跑同一個 SNV 的實際輸出：ref 36、alt 21 不變，但 HP2 多了 2 條 alt，HP1 多了 3 條 ref，這些就是錯誤造成的。下一頁看 copy number。",
)


# ---------------------------------------------------------------- k-cn
def copies(x, y, cols, mut):
    """Stack of copy bars from bottom; cols: list of colors; mut: indices carrying the SNV."""
    s = ""
    for i, c in enumerate(cols):
        yy = y - i * 30
        s += rect(x, yy, 96, 20, fill=c, stroke="none", sw=0, rx=5)
        if i in mut:
            s += alt_dot(x + 48, yy + 10)
    return s


def igv_site(x, y, tracks):
    """IGV-like pile-up of one site: tracks = (label, color, ref, alt); one thin line per read, alt reads on top
    with a red tick at the site, as IGV shows a mismatching base. Reads start/end at fixed pseudo-random offsets."""
    s = t(x, y + 10, "chr5:161,912,274　ASCAT 3＋0", 22, 700, INK)
    site = x + 206
    yy = y + 22
    top = yy
    for label, col, ref, alt in tracks:
        n = ref + alt
        s += t(x, yy + 16, label, 22, 700, col)
        if n == 0:
            s += t(site + 16, yy + 18, "0 條 read", 22, 700, col)
            yy += 30
            continue
        for i in range(n):
            a = x + 118 + (i * 37) % 56
            b = x + 236 + (i * 53) % 60
            ry = yy + 4 + i * 4
            s += f'<line x1="{a}" y1="{ry}" x2="{b}" y2="{ry}" stroke="{col}" stroke-width="3"/>'
            if i < alt:
                s += f'<rect x="{site - 3}" y="{ry - 2}" width="6" height="4" fill="{RED}"/>'
        if n > 8:
            s += t(x + 312, yy + 34, f"alt {alt}", 22, 700, RED) + t(x + 312, yy + 62, f"ref {ref}", 22, 400, SUB)
        else:
            s += t(x + 312, yy + 18, f"alt {alt}、ref {ref}", 22, 700, RED)
        yy += max(n * 4 + 8, 30)
    s += line(site, top - 2, site, yy - 4, SUB, 1.5, ' stroke-dasharray="3 4"')
    return s

def left_cn():
    s = ""
    xs = [24, 192, 360, 528]
    base = 196
    s += copies(xs[0], base, [HP1, HP2], [])
    s += copies(xs[1], base, [HP1, HP1], [])
    s += copies(xs[2], base, [HP1, HP1], [1])
    s += copies(xs[3], base, [HP1, HP1, HP1], [1, 2])
    labels = ["LOH", "SNV", "gain"]
    for i, lab in enumerate(labels):
        x1, x2 = xs[i] + 104, xs[i + 1] - 8
        s += harrow(x1, 191, x2, ORANGE)
        s += t((x1 + x2) / 2, 177, lab, 24, 700, ORANGE, "middle")
    caps = [("1＋1", "事件前"), ("2＋0", "LOH 後"), ("2＋0", "SNV 出現"), ("3＋0", "gain 後")]
    for x, (c1, c2) in zip(xs, caps):
        s += t(x + 48, 252, c1, 24, 700, INK, "middle")
        s += t(x + 48, 286, c2, 24, 400, SUB, "middle")
    s += t(xs[3] + 48, 124, "帶 SNV 2 份", 24, 700, RED, "middle")
    s += rect(300, 70, 30, 14, fill=HP1, stroke="none", sw=0, rx=4) + t(338, 85, "HP1", 24, 700, HP1)
    s += rect(410, 70, 30, 14, fill=HP2, stroke="none", sw=0, rx=4) + t(448, 85, "HP2", 24, 700, HP2)
    s += t(170, 85, "份數", 24, 400, SUB)
    # real numbers: one real HCC1395 site drawn like IGV (one line per read, red tick = alt base), plus the three
    # site fractions. chr5:161912274, ASCAT (3,0); HP1 ref 5 alt 17, HP2 0 reads, unphased ref 0 alt 6
    # (lab_report/2026-10-31_diplosim_ppc_hcc1395_lost045/tables/real_per_snv.tsv; CN from 2026-10-30_ascat_hcc1395_5khz).
    s += igv_site(24, 384, [("HP1", HP1, 5, 17), ("HP2", HP2, 0, 0), ("unphased", HP0, 0, 6)])
    s += f'<line x1="470" y1="384" x2="470" y2="556" stroke="{LINE}" stroke-width="2"/>'
    s += t(486, 396, "全部位點", 22, 400, SUB)
    for i, (lab, v) in enumerate((("先 LOH 再 gain", "20.7%"), ("帶 SNV ≥ 2 份", "43.9%"),
                                  ("少的 HP 沒 read", "48.2%"))):
        y = 428 + i * 46
        s += t(486, y, lab, 22, 400, INK) + t(486, y + 26, v, 26, 700, ORANGE)
    return s


pages["k-cn"] = page(
    "k-cn", 6,
    "真實 20.7% 的 SNV 位點是「先 LOH 再 gain」，所以 diplosim 加上同一位置的第二個 CN 事件",
    "左：時間順序示意，事件前 HP1、HP2 各 1 份，LOH 後 HP1 2 份，SNV 出現在其中一份，gain 後 HP1 3 份、帶 SNV 2 份；HCC1395 實際一個 ASCAT 3＋0 位點 chr5:161912274 的 read：HP1 有 17 條 alt、5 條 ref，HP2 沒有 read，unphased 6 條 alt；全部位點中先 LOH 再 gain 的位點 20.7%，帶 SNV 2 份以上的位點 43.9%，較少那條 HP depth 小於 0.1 的位點 48.2%。中：copy number 旋鈕，第二個 CN 事件機率設 0.5（預設 0）；CONIPHER 沒有，每位置最多 1 個 CN 事件。右：旋鈕打開後的 SNV3，ref 26、alt 41，allele A、B copy number 3、0，帶 SNV 2 份，HP1 ref 17、alt 30，HP2 ref 2、alt 0，unphased ref 7、alt 11",
    column_heads() + left_frames("HCC1395 long read，CN 由 ASCAT 推論") + left_cn()
    + middle("copy number", [("第二個 CN 事件", "0.5（預設 0）", "upright")], "每位置最多 1 個 CN 事件", "hatchKC")
    + arrows()
    # rerun of seed 1 with the HCC1395 CN knobs (--prop-pos-lost 0.45 --loss-events cnloh_B --prop-pos-second-cna 0.5
    # --gain-events gain_A,gain_B,gain_B,gain_both); VAR_POS 33 is one of 9 SNVs at (3,0) with 2 mutated copies
    + right({"cn", "mult"}, set(), "旋鈕打開後的一個 SNV（示意設定）",
            {"count": "ref 26、alt 41", "cn": "3、0", "mult": "2", "hp1": ("ref 17", "alt 30"),
             "hp2": ("ref 2", "alt 0"), "hp0": ("ref 7", "alt 11")}, "SNV3 的輸出一列"),
    "這頁要看的是：真實有 20.7% 的 SNV 位點是先 LOH 再 gain，所以 diplosim 加上第二個 CN 事件。"
    "左上照時間看：HP1、HP2 各 1 份；LOH 後 HP2 沒了；SNV 出現後再 gain，3 份中 2 份帶 SNV。"
    "左下實際結果，用 IGV 的畫法看真實 HCC1395 的一個位點：ASCAT 推論這裡是 3＋0，也就是先 LOH 再 gain。每一條線是一條 read，紅色小方塊是 alt。HP1 有 22 條 read，其中 17 條帶 alt，大約 3 份中 2 份，和左上示意一樣；HP2 一條 read 都沒有，因為那份染色體已經丟了。右邊是全部位點的比例：先 LOH 再 gain 20.7%，帶 SNV 2 份以上 43.9%，較少那條 HP 幾乎沒有 read（depth 小於 0.1）的有 48.2%。"
    "中間旋鈕預設 0，這頁設 0.5 來示範；CONIPHER 每位置最多 1 個 CN 事件。"
    "右邊是把第二個 CN 事件機率設 0.5 實際跑出的一個 SNV，叫它 SNV3：allele A、B copy number 3 和 0，帶 SNV 2 份，和左上一樣；HP2 只剩 2 條 ref，來自 normal 細胞。接下來比較兩台機器的輸出。",
)

for sid, html in pages.items():
    (OUT / f"{sid}.html").write_text(html)
    print(sid, len(html.encode()), "bytes")
