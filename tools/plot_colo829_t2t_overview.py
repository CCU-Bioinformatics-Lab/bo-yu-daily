#!/usr/bin/env python3
"""Draw what the COLO829 T2T somatic SNV table (Sohn 2026) looks like.

Left: the 14 homolog pairs of the personal diploid assembly, hap1 / hap2 bars to scale, one red tick per SNV.
Right: one VCF record explained, and the whole-file totals.

Usage: python3 tools/plot_colo829_t2t_overview.py <somatic_snvs.vcf.gz> <lab_report_dir>
Reads <lab_report_dir>/homolog_pairs.tsv; writes <lab_report_dir>/t2t_overview.png.
"""
import csv
import gzip
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"
HP1, HP2, MUT, INK, MUTE, PANEL = "#2C5F9E", "#D9772B", "#D23A2E", "#1F2A37", "#5A6A62", "#EEF2EF"
LIGHT = {HP1: "#C9D9EF", HP2: "#F6DCC2"}

vcf, out = Path(sys.argv[1]), Path(sys.argv[2])

lengths, pos, gts = {}, defaultdict(list), Counter()
first = None
with gzip.open(vcf, "rt") as fh:
    for line in fh:
        if line.startswith("##contig"):
            body = line.strip()[len("##contig=<"):-1]
            kv = dict(x.split("=", 1) for x in body.split(","))
            lengths[kv["ID"]] = int(kv["length"])
        elif not line.startswith("#"):
            f = line.rstrip("\n").split("\t")
            pos[f[0]].append(int(f[1]))
            gts[f[9].split(":")[0]] += 1
            if first is None:
                first = f
total = sum(len(v) for v in pos.values())
hap_tot = Counter(c.split("-")[0] for c, v in pos.items() for _ in v)

pairs = list(csv.DictReader(open(out / "homolog_pairs.tsv"), delimiter="\t"))
pairs.sort(key=lambda r: -float(r["hap1_mb"]))


def track(contigs):
    """Concatenate contigs (a+b) into one track: (length Mb, SNV positions Mb)."""
    off, xs = 0, []
    for c in contigs.split("+"):
        xs += [(off + p) / 1e6 for p in pos.get(c, [])]
        off += lengths[c]
    return off / 1e6, xs


fig = plt.figure(figsize=(14, 8.2), dpi=150)
fig.patch.set_facecolor("#FBFBF8")
ax = fig.add_axes([0.105, 0.115, 0.56, 0.765])
ax.set_facecolor("#FBFBF8")
n = len(pairs)
h = 0.30
for i, r in enumerate(pairs):
    y = n - 1 - i
    for dy, col, key in ((0.19, HP1, "hap1_contig"), (-0.19, HP2, "hap2_contig")):
        L, xs = track(r[key])
        yy = y + dy
        if xs:
            ax.add_patch(Rectangle((0, yy - h / 2), L, h, fc=LIGHT[col], ec=col, lw=1.0))
            ax.vlines(xs, yy - h / 2 + 0.03, yy + h / 2 - 0.03, color=MUT, lw=0.25, alpha=0.45)
        else:
            ax.add_patch(Rectangle((0, yy - h / 2), L, h, fill=False, ec=col, lw=1.4, ls=(0, (4, 3))))
            ax.text(L / 2, yy, "0 個 SNV", color=col, fontsize=9, ha="center", va="center", weight="bold")
    a, b = int(r["hap1_snv"]), int(r["hap2_snv"])
    ax.text(262, y, f"{a:,} : {b:,}", va="center", ha="left", fontsize=9.5, color=INK)
    lab = r["pair"] if r["source"] == "authors" else r["pair"].replace("len", "").replace("Mb", " Mb*")
    ax.text(-4, y, lab, va="center", ha="right", fontsize=10.5, color=INK, weight="bold")
ax.set_xlim(0, 300)
ax.set_ylim(-0.7, n - 0.3)
ax.set_yticks([])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTE)
ax.set_xticks([0, 50, 100, 150, 200, 250])
ax.tick_params(colors=MUTE, labelsize=9)
ax.set_xlabel("contig 長度（Mb）", color=MUTE, fontsize=10)
ax.text(262, n - 0.25, "hap1 : hap2", fontsize=9.5, color=MUTE, ha="left")
fig.text(0.02, 0.945, "COLO829 T2T 長什麼樣子：同一位病人自己的兩套染色體，每個 SNV 直接落在其中一套",
         fontsize=15, weight="bold", color=INK)
fig.text(0.02, 0.905, "實際資料　Sohn 2026（Cell）體細胞 SNV，long read（Fiber-seq），COLO829T Passage B",
         fontsize=10.5, color="#2F8F6A")
fig.text(0.105, 0.018, f"每條紅線＝1 個 SNV，越密越多；淺色空白段＝這段沒有 SNV。* 依長度配對，染色體編號未知。另有 {len(lengths) - sum(len(r['hap1_contig'].split('+')) + len(r['hap2_contig'].split('+')) for r in pairs)} 條較短或未配對的 contig 沒畫。",
         fontsize=9, color=MUTE)

# right: one record, then totals
bx = fig.add_axes([0.70, 0.08, 0.28, 0.80])
bx.set_xlim(0, 10)
bx.set_ylim(0, 10)
bx.axis("off")
bx.add_patch(FancyBboxPatch((0.1, 4.55), 9.8, 5.3, boxstyle="round,pad=0.02,rounding_size=0.25", fc=PANEL, ec="none"))
bx.text(0.4, 9.35, "一筆資料（VCF 第一列）", fontsize=11.5, weight="bold", color=INK)
fmt = dict(zip(first[8].split(":"), first[9].split(":")))
info = dict(x.split("=", 1) for x in first[7].split(";"))
rows = [("contig", first[0], "名稱就寫了 hap1 → 落在 hap1"),
        ("位置", f"{int(first[1]):,}", "在這條 contig 上的座標"),
        ("變化", f"{first[3]} → {first[4]}", "一個鹼基換掉"),
        ("GT", fmt["GT"], "這條上幾乎每條 read 都帶"),
        ("VAF", f"{float(fmt['VAF']):.2f}", f"{fmt['AD'].split(',')[1]}／{fmt['DP']} 條 read"),
        ("CN", info["CN"].replace("CN", ""), "這一段有 2 份")]
for k, (key, val, note) in enumerate(rows):
    y = 8.65 - k * 0.6
    bx.text(0.4, y, key, fontsize=9.5, color=MUTE)
    bx.text(2.0, y, val, fontsize=9.5, color=INK, weight="bold")
    bx.text(2.0, y - 0.28, note, fontsize=8.5, color=MUTE)
# mini picture of the record: hap1 with a star, hap2 without
bx.add_patch(Rectangle((0.6, 5.08), 8.2, 0.22, color=HP1, lw=0))
bx.add_patch(Rectangle((0.6, 4.75), 8.2, 0.22, color=HP2, lw=0))
bx.plot([3.2], [5.19], marker="*", ms=12, color=MUT, mec="white", mew=0.6)
bx.text(9.0, 5.19, "hap1", fontsize=8.5, color=HP1, va="center")
bx.text(9.0, 4.86, "hap2", fontsize=8.5, color=HP2, va="center")

bx.text(0.4, 3.75, "整份檔案", fontsize=11.5, weight="bold", color=INK)
f1 = hap_tot["haplotype1"] / total
bx.add_patch(Rectangle((0.4, 2.85), 9.2 * f1, 0.5, color=HP1, lw=0))
bx.add_patch(Rectangle((0.4 + 9.2 * f1, 2.85), 9.2 * (1 - f1), 0.5, color=HP2, lw=0))
bx.text(0.6, 3.1, f"hap1 {hap_tot['haplotype1']:,}", fontsize=9, color="white", va="center")
bx.text(9.4, 3.1, f"hap2 {hap_tot['haplotype2']:,}", fontsize=9, color="white", va="center", ha="right")
lines = [f"共 {total:,} 個 SNV，{len(lengths)} 條 contig",
         f"GT 1/1：{gts['1/1']:,}　0/1：{gts['0/1']:,}（大多是固定突變）",
         "hap2 少：有幾段整段沒有 SNV（虛線、空白段）",
         "hap1、hap2 是組裝標籤，不是爸媽"]
for k, t in enumerate(lines):
    bx.text(0.4, 2.3 - k * 0.55, t, fontsize=9.3, color=INK if k < 2 else MUTE)

fig.savefig(out / "t2t_overview.png", facecolor=fig.get_facecolor())
print("wrote", out / "t2t_overview.png", total, dict(hap_tot), dict(gts))
