#!/usr/bin/env python3
"""Draw the plain-language COLO829 haplotype figure in the style of the learning site.

Usage (from the repo root):
  python3 -I tools/draw_colo829_hap_explainer.py <somatic_snvs.vcf.gz> <out.html>

Mutation ticks use real positions from the VCF. One tick stands for 20 SNVs, because every SNV would
merge into a solid bar at this size. hap1 and hap2 are grey on purpose: on the site blue and orange mean
dad and mom, and the parent of each haplotype here is unknown.
"""
import gzip
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research/literature/surveys/tumor_evolution_history_2026-11-05/site"))
from lib import PROBLEMS, S  # noqa: E402

PAIRS = [("chr1", "haplotype1-0000012", "haplotype2-0000059", 249.1, 248.3), ("chr4", "haplotype1-0000013", "haplotype2-0000060", 191.3, 191.3),
         ("chr3", "haplotype1-0000011", "haplotype2-0000058", 200.1, 201.9)]
TICK_EVERY = 20
CSS = """
:root{--paper:#fbfcfb;--panel:#eef2ef;--panel3:#bcc7c0;--ink:#1c2a26;--ink2:#46574f;--mute:#5a6a62;--line:#d4dcd6;--line2:#8a9a91;--mut:#d3263f;--hap1:#56666e;--hap2:#a3b0a9;--on:#ffffff;
--sans:"Noto Sans TC","PingFang TC","Microsoft JhengHei","Noto Sans CJK JP",sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#141a18;--panel:#1f2825;--panel3:#55655d;--ink:#e8efea;--ink2:#b9c6be;--mute:#a4b3aa;--line:#33403b;--line2:#7d8f85;--mut:#ef5168;--hap1:#7f909a;--hap2:#4d5b55;--on:#ffffff;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#141a18;--panel:#1f2825;--panel3:#55655d;--ink:#e8efea;--ink2:#b9c6be;--mute:#a4b3aa;--line:#33403b;--line2:#7d8f85;--mut:#ef5168;--hap1:#7f909a;--hap2:#4d5b55;--on:#ffffff;color-scheme:dark}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.75}
.wrap{max-width:920px;margin:0 auto;padding-block:26px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1{font-size:29px;line-height:1.3;margin:0 0 8px;text-wrap:balance}
p{margin:0;max-width:44em}.lead{font-size:18px;color:var(--ink2);margin-bottom:22px}
.draw{overflow-x:auto}.draw svg{display:block;width:100%;min-width:660px;height:auto}
figcaption{font-size:17.5px;margin-top:14px;max-width:44em}
.note{font-size:15px;color:var(--ink2);margin-top:10px;max-width:46em}
svg text{font-family:var(--sans);fill:var(--ink)}
svg .t{font-size:14px}svg .s{font-size:12.5px;fill:var(--ink2)}svg .h{font-size:15px;font-weight:700}svg .b{font-size:14px;font-weight:700}svg .n{font-size:13px}svg .big{font-size:22px;font-weight:700}
"""


def read_positions(path):
    pos = defaultdict(list)
    with gzip.open(path, "rt") as f:
        for line in f:
            if not line.startswith("#"):
                c = line.split("\t", 2)
                pos[c[0]].append(int(c[1]))
    return pos


def chrom_row(s, x0, y, scale, length, positions, fill, label, lost=False):
    w = length * scale
    s.text(x0 - 10, y + 4, label, "s", "end")
    s.bar(x0, y, w, fill, 12, dash=lost)
    for p in sorted(positions)[::TICK_EVERY]:
        s.line(x0 + p / 1e6 * scale, y - 8, x0 + p / 1e6 * scale, y + 8, "mut", 1.1)


def main():
    pos = read_positions(sys.argv[1])
    s = S("colo829", 800, 800)

    # Step 1: raw counts, to scale
    def step(y, n, title):
        s.circle(40, y - 5, 13, "ink")
        s.text(40, y, n, "b", "middle", "paper")
        s.text(62, y, title, "h")
    step(26, "1", "直接數突變：hap1 看起來多很多")
    x0, full = 110, 500
    for y, name, n, c in [(46, "hap1", 27410, "hap1"), (86, "hap2", 17400, "hap2")]:
        w = full * n / 27410
        s.rect(x0, y, w, 30, c, r=4)
        s.text(x0 - 10, y + 20, name, "t", "end")
        s.text(x0 + w + 10, y + 20, f"{n:,}", "b")
    s.text(740, 69, "61%", "big", "end"); s.text(740, 109, "39%", "big", "end")

    # Step 2: real chromosomes
    step(160, "2", "看染色體：有些 hap2 沒有任何突變")
    y = 192
    scale = 1.92
    for name, a, b, la, lb in PAIRS:
        na, nb = len(pos.get(a, [])), len(pos.get(b, []))
        chrom_row(s, x0, y, scale, la, pos.get(a, []), "hap1", f"{name} hap1")
        chrom_row(s, x0, y + 24, scale, lb, pos.get(b, []), "hap2", "hap2", lost=nb == 0)
        s.text(x0 + 500, y + 4, f"{na:,}", "b"); s.text(x0 + 500, y + 28, f"{nb:,}", "b")
        if nb == 0:
            s.rect(x0 + 118, y + 15, 244, 18, "paper", r=3)
            s.text(x0 + 240, y + 29, "沒有任何突變：很可能已被腫瘤丟掉", "s", "middle")
            s.text(x0 + 560, y + 28, "少了一條", "s")
        else:
            s.text(x0 + 560, y + 16, "差不多", "s")
        y += 70
    s.line(x0, y - 16, x0, y - 6, "mut", 1.6)
    s.text(x0 + 10, y - 6, f"每條紅線代表 {TICK_EVERY} 個突變，位置來自真實資料。圖上只畫 3 對做例子。", "s")
    s.rect(30, y + 8, 740, 40, "panel")
    s.text(400, y + 33, "全基因組有 844 Mb 的 hap2 沒有任何突變，hap1 只有 1 Mb。沒有那段 DNA，就數不到它的突變。", "t", "middle")

    # Step 3: density, to scale
    y += 88
    step(y, "3", "只算還留著的片段：兩條幾乎一樣")
    y += 22
    rows = [("hap1", 27410, 2934, 9.34, "hap1"), ("hap2", 17400, 1869, 9.31, "hap2")]
    for i, (name, n, ln, d, c) in enumerate(rows):
        yy = y + i * 44
        s.text(x0 - 10, yy + 21, name, "t", "end")
        s.text(x0, yy + 21, f"{n:,} 個突變 ÷ {ln:,} Mb", "t")
        s.rect(x0 + 200, yy, 300 * d / 10, 30, c, r=4)
        s.text(x0 + 200 + 300 * d / 10 + 10, yy + 21, f"{d:g} 個／Mb", "b")
    s.text(x0 + 200, y + 104, "長條長度代表每 Mb 的突變數（0 到 10）。比值 1.004，95% CI 0.985–1.023。", "s")

    # Limits
    y += 124
    s.rect(30, y, 740, 76, "panel")
    s.text(50, y + 28, "這只是一個黑色素瘤細胞株，而且不知道 hap1、hap2 哪條是爸爸。", "t")
    s.text(50, y + 54, "灰色只分兩條，不代表爸媽。丟掉那條原本有多少突變，已經無從得知。", "t")
    s.h = int(y + 86)
    svg = s.svg("COLO829 的突變原始比例是 61 比 39，主要因為部分 hap2 流失；只算留下的片段，密度幾乎相同")
    if PROBLEMS:
        print("\n".join(PROBLEMS))
    html = f"""<title>COLO829 兩條單倍型</title><meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap"><style>{CSS}</style>
<div class="wrap"><h1>突變數差很多，密度卻幾乎一樣</h1>
<p class="lead">用 COLO829 的公開突變資料，比較腫瘤裡兩條單倍型的突變。</p>
<figure style="margin:0"><div class="draw">{svg}</div>
<figcaption>看起來 hap1 的突變多很多，主要是因為腫瘤丟掉了部分 hap2。只算還留著的片段，兩條每 Mb 的突變數幾乎相同。</figcaption></figure>
<p class="note">資料：Sohn 2026, Cell 公開的 VCF，long read。比例是本 repo 計算的，不是論文結論。「留著的片段」是扣掉連續超過 5 Mb 沒有突變的部分，這個定義本身來自突變位置，所以這是密度比較，不是獨立證明。兩條都保留的 11 對中，chr14、chr16 偏離預期較多。不同批的 COLO829 不完全一樣：實驗室另一批的 chr1p 還留著另一條，所以這張圖只代表 Sohn 那批。細節見 lab_report/2026-11-06_colo829_loss_events/。</p></div>"""
    Path(sys.argv[2]).write_text(html, encoding="utf-8")
    print("height", s.h, "problems", len(PROBLEMS))


if __name__ == "__main__":
    main()
