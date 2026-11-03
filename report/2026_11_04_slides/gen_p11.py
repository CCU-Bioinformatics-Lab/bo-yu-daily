"""Slide r-targets (2026-11-04 deck): real HCC1395 vs diplosim at five purities, one small chart per statistic.
Real line, diplosim median (dashed) and diplosim 95% band from the ppc_stats.tsv of each subsample.
User comment 2026-11-02 ("要同時補上兩邊的數值").
2026-11-03: real side masks the immunoglobulin loci (tools/diplosim_ppc_mask_real.py); dice row and
notes follow the user's edits in the online editor. Run: python3 gen_p11.py (writes project/slides/r-targets.html)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "lab_report" / "2026-11-03_diplosim_mask_ig_loci"
OUT = Path(__file__).parent / "project" / "slides" / "r-targets.html"
RUNS = ["t50_n00", "t40_n10", "t30_n20", "t20_n30", "t10_n40"]
PUR = ["0.97", "0.70", "0.48", "0.29", "0.14"]
F = "Noto Sans TC, Arial, sans-serif"
P = "font-family:'Noto Sans TC', Arial, sans-serif"
INK, SUB, BLUE, BAND, ORANGE, LINE = "#1f2a37", "#6b7480", "#2f6db5", "#d6e3f3", "#c96a1b", "#e3e1da"

# (key, card title, y max, y-max label, number format)
STATS = [
    ("HP0_frac_pooled", "unphased read 比例", 0.2, "0.2", "{:.3f}"),
    ("tag_frac_SD_sites", "每個 SNV 位點有 HP1、HP2 標記的比例多寡", 0.4, "0.4", "{:.3f}"),
    ("split_alt_frac", "alt 分在兩條 HP 的 SNV 比例", 0.2, "0.2", "{:.3f}"),
    ("minorHP_depth_lt_0.1", "發生 LOH 的比例", 0.6, "0.6", "{:.3f}"),
    ("depth_VMR", "每個 SNV 的 depth 高低程度", 10, "10", "{:.2f}"),
    ("VAF_q50", "VAF 中位數", 0.5, "0.5", "{:.2f}"),
]


def load():
    d = {}
    for r in RUNS:
        with open(SRC / r / "tables" / "ppc_stats.tsv") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                d[(r, row["statistic"])] = row
    return d


D = load()
XS = [64.0, 196.7, 304.9, 398.3, 472.0]  # same x positions as the earlier version (purity spacing)
Y0, Y1 = 124.0, 38.0


def y(v, vmax):
    return Y0 - (Y0 - Y1) * min(v, vmax) / vmax


def txt(x, yy, s, anchor="middle", fill=SUB, weight=400):
    return (f'<text x="{x}" y="{yy}" text-anchor="{anchor}" font-size="24" font-weight="{weight}" '
            f'fill="{fill}" font-family="{F}">{s}</text>')


def chart(key, title, vmax, vlab, fmt):
    real = [float(D[(r, key)]["real"]) for r in RUNS]
    med = [float(D[(r, key)]["sim_median"]) for r in RUNS]
    lo = [float(D[(r, key)]["sim_q2.5"]) for r in RUNS]
    hi = [float(D[(r, key)]["sim_q97.5"]) for r in RUNS]
    inside = [D[(r, key)]["verdict"] == "in" for r in RUNS]
    s = f'<line x1="64" y1="{Y0}" x2="480" y2="{Y0}" stroke="{LINE}" stroke-width="1.5"/>' + txt(56, Y0 + 8, "0", "end")
    s += f'<line x1="64" y1="{Y1}" x2="480" y2="{Y1}" stroke="{LINE}" stroke-width="1.5"/>' + txt(56, Y1 + 8, vlab, "end")
    band = [f"{x},{y(v, vmax):.1f}" for x, v in zip(XS, hi)] + [f"{x},{y(v, vmax):.1f}" for x, v in zip(XS[::-1], lo[::-1])]
    s += f'<polygon points="{" ".join(band)}" fill="{BAND}"/>'
    s += (f'<polyline points="{" ".join(f"{x},{y(v, vmax):.1f}" for x, v in zip(XS, med))}" fill="none" '
          f'stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 6"/>')
    s += (f'<polyline points="{" ".join(f"{x},{y(v, vmax):.1f}" for x, v in zip(XS, real))}" fill="none" '
          f'stroke="{ORANGE}" stroke-width="3"/>')
    for x, v, ok in zip(XS, real, inside):
        if ok:
            s += f'<circle cx="{x}" cy="{y(v, vmax):.1f}" r="6" fill="{ORANGE}"/>'
        else:  # outside the diplosim 95% band: hollow ring
            s += f'<circle cx="{x}" cy="{y(v, vmax):.1f}" r="7" fill="#ffffff" stroke="{ORANGE}" stroke-width="3"/>'
    for i, xx in enumerate(XS):
        s += txt(xx, 152, PUR[i])
    n_in = sum(inside)
    label = ("真實 " + "、".join(fmt.format(v) for v in real) + "；diplosim 中位數 " + "、".join(fmt.format(v) for v in med)
             + f"；{n_in}/5 個 purity 落在 diplosim 95% 區間內")
    svg = None  # built after the count label is known
    col = BLUE if n_in == 5 else ORANGE
    head = f'<p style="{P}; font-size:24px; font-weight:700; line-height:1.3; color:{INK}">{title}</p>'
    s_count = txt(480, 22, f"{n_in}/5 在區間內", "end", col, 700)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="{title}，換算 purity 0.97 到 0.14：{label}" '
           f'viewBox="0 0 500 156" style="width:500px; height:156px">{s}{s_count}</svg>')
    return (f'<div style="display:flex; flex-direction:column; gap:4px; flex:1; padding:12px 16px; background:#ffffff; '
            f'border:1px solid {LINE}; border-radius:12px">{head}{svg}</div>')


def count(key):
    return sum(D[(r, key)]["verdict"] == "in" for r in RUNS)


cards = [chart(*st) for st in STATS]
n_real = "｜".join(f"{float(D[(r, 'n_called')]['real']):,.0f}" for r in RUNS)
n_sim = "｜".join(f"{float(D[(r, 'n_called')]['sim_median']):,.0f}" for r in RUNS)
loh = [(float(D[(r, "minorHP_depth_lt_0.1")]["real"]), float(D[(r, "minorHP_depth_lt_0.1")]["sim_median"])) for r in RUNS]
vmr50 = D[("t50_n00", "depth_VMR")]

dice = (
    f'<div style="display:flex; flex-direction:row; gap:16px; align-items:center">'
    f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="骰子" viewBox="0 0 48 48" style="width:48px; height:48px"><rect x="3" y="3" width="42" height="42" rx="9" fill="#ffffff" stroke="{BLUE}" stroke-width="3"/>'
    + "".join(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{BLUE}"/>' for cx, cy in ((14, 14), (34, 14), (24, 24), (14, 34), (34, 34)))
    + f'</svg><p style="{P}; font-size:28px; font-weight:700; line-height:1.3; color:{INK}">隨機調整參數 200 次，看輸出的數值能不能接近橘線（真實 HCC1395）</p></div>')
n_mask = sum(1 for _ in open(SRC / "t10_n40" / "tables" / "masked_sites.tsv")) - 1
n_mask50 = sum(1 for _ in open(SRC / "t50_n00" / "tables" / "masked_sites.tsv")) - 1

legend = (
    f'<div style="display:flex; flex-direction:row; gap:32px; align-items:center">'
    f'<div style="display:flex; flex-direction:row; gap:8px; align-items:center"><div style="width:32px; height:6px; background:{ORANGE}; border-radius:3px"></div>'
    f'<p style="{P}; font-size:24px; line-height:1.3; color:{INK}">真實 HCC1395</p></div>'
    f'<div style="display:flex; flex-direction:row; gap:8px; align-items:center"><svg xmlns="http://www.w3.org/2000/svg" aria-label="藍色虛線" viewBox="0 0 32 6" style="width:32px; height:6px"><line x1="0" y1="3" x2="32" y2="3" stroke="{BLUE}" stroke-width="4" stroke-dasharray="8 6"/></svg>'
    f'<p style="{P}; font-size:24px; line-height:1.3; color:{INK}">diplosim 中位數</p></div>'
    f'<div style="display:flex; flex-direction:row; gap:8px; align-items:center"><div style="width:32px; height:20px; background:{BAND}; border-radius:3px"></div>'
    f'<p style="{P}; font-size:24px; line-height:1.3; color:{INK}">diplosim 95% 區間</p></div>'
    f'<div style="display:flex; flex-direction:row; gap:8px; align-items:center"><svg xmlns="http://www.w3.org/2000/svg" aria-label="空心圈" viewBox="0 0 20 20" style="width:20px; height:20px"><circle cx="10" cy="10" r="7" fill="#ffffff" stroke="{ORANGE}" stroke-width="3"/></svg>'
    f'<p style="{P}; font-size:24px; line-height:1.3; color:{INK}">真實值在區間外</p></div>'
    f'<p style="{P}; font-size:24px; line-height:1.3; color:{SUB}">x 軸＝換算 purity</p></div>')

notes = ("這頁把真實 HCC1395 和 diplosim 放在同一張圖比。骰子那一行是做法：隨機調整參數 200 次，看輸出的數值能不能接近真實值。橘色實線是真實值，藍色虛線是 diplosim 的中位數，淺藍色帶是 diplosim 的 95% 區間；"
         "真實值落在藍帶裡，就表示 diplosim 模擬得出這個數值。右上角寫 5 個 purity 中有幾個落在區間內。"
         f"unphased read 比例、每個 SNV 位點有 HP1、HP2 標記的比例多寡、alt 分在兩條 HP 的比例、發生 LOH 的比例、VAF 中位數，5 個 purity 都在區間內；其中標記比例多寡，真實從 {float(D[('t50_n00', 'tag_frac_SD_sites')]['real']):.3f} 到 {float(D[('t10_n40', 'tag_frac_SD_sites')]['real']):.3f}，diplosim 中位數約 0.26。"
         f"每個 SNV 的 depth 高低程度只有 purity 0.97 略高於區間：真實 {float(vmr50['real']):.2f}，區間上限 {float(vmr50['sim_q97.5']):.2f}。"
         f"最下面第一行是真實端排除的區域：抗體基因區，共約 {n_mask}–{n_mask50} 個 SNV。我們的 normal 是 B 細胞株，B 細胞在這裡會切掉一段 DNA，"
         "所以 normal 在這裡也少一條 HP，混再多 normal 也補不回來；這是我們的推論，我們量到 normal 在這段的 depth 只有兩側的一半。diplosim 的 normal 沒有這種區域。"
         f"排除以後，LOH 比例在 purity 0.14 時真實 {loh[4][0]:.4f}、diplosim {loh[4][1]:.4f}，5 個 purity 都在區間內。"
         "第二行是叫出的 SNV 數：高 purity 時 diplosim 偏少，原因是偵測曲線用 t50 的 call 量出來，套回高 purity 時重複扣了一次（推論，見 lab_report 2026-11-01_diplosim_detection_curve）。"
         "接著整理哪些我們已經確定、哪些還沒有。")

html = f'''<section id="r-targets" style="display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2">
  <p style="{P}; font-size:24px; font-weight:700; letter-spacing:2px; color:#2f6db5">3 · 結果</p>
  <h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:64px; font-weight:700; line-height:1.15; color:#1f2a37">真實 HCC1395 對 diplosim：6 個數值中 5 個在 5 個 purity 都落在模擬區間內，depth 高低程度只在 purity 0.97 略偏</h2>
  <div style="display:flex; flex-direction:column; gap:16px; flex:1">
    {dice}
    {legend}
    <div style="display:flex; flex-direction:row; gap:24px">
      {cards[0]}
      {cards[1]}
      {cards[2]}
    </div>
    <div style="display:flex; flex-direction:row; gap:24px">
      {cards[3]}
      {cards[4]}
      {cards[5]}
    </div>
    <div style="display:flex; flex-direction:column; gap:4px">
      <p style="{P}; font-size:24px; line-height:1.3; color:{INK}">真實端排除抗體基因區（normal 細胞在此少一條 HP）：{n_mask}–{n_mask50} 個 SNV</p>
      <p style="{P}; font-size:24px; line-height:1.3; color:{INK}">叫出的 SNV 數　真實：{n_real}　diplosim 中位數：{n_sim}</p>
    </div>
  </div>
  <div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">
    <p style="{P}; font-size:24px; color:#6b7480">2026-11-04 diplosim：兩台機器與真實 long read</p>
    <p style="{P}; font-size:24px; color:#6b7480">14 / 15</p>
  </div>
  <aside>{notes}</aside>
</section>
'''
OUT.write_text(html)
print(OUT, [count(k) for k, *_ in STATS])
