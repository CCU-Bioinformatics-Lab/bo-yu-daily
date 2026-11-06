#!/usr/bin/env python3
"""HG008: truncal somatic SNV density on each assembly haplotype, using GIAB's own tracks. Read-only on inputs.

Usage: python3 tools/hg008_hap_snv_density.py <out_dir>

Inputs (shared copy): the NIST small variant benchmark v0.4 and the same-haplotype CN track of the SV/CNV benchmark
v0.6, both in HG008-N v6.3 coordinates, where the contig name says the haplotype (chr1_hap1, chr1_hap2).
A base counts when it is in the benchmark BED and its own haplotype has CN >= 1 in the tumor. The CN track does not
depend on where the SNVs are. Each rate ratio uses a Poisson z test on log(rate), with exposure taken as fixed.
"""
import bisect
import csv
import math
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"

ROOT = "/big8_disk/yungjen114/data/HG008/NIST/"
SMALL = ROOT + "somatic-smvar_v0.4_20261006/HG008Nv6.3/HG008-T_somatic_smvar_benchmark_v0.4_HG008Nv6.3"
CN = ROOT + "somatic-stvar-CNV_v0.6_20261006/HG008Nv6.3/HG008Nv6.3_HG008-T-V0.6_somatic-CNV_samehap_withCN1.draftbenchmark.bed"
CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]
MIN_MB = 20  # both haplotypes need this much retained sequence before their rates are compared
HAP1, HAP2 = "#1f6f8b", "#d1603d"
INK, MUTE, LINE = "#1c2a26", "#5a6a62", "#d4dcd6"


def load(path, keep=lambda f: True):
    d = defaultdict(list)
    for line in open(path):
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        if keep(f):
            d[f[0]].append((int(f[1]), int(f[2])))
    return {k: sorted(v) for k, v in d.items()}


def intersect(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        s, e = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if s < e:
            out.append((s, e))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def compare(n1, mb1, n2, mb2):
    """Rate ratio hap1 / hap2, its 95% CI and two-sided p."""
    r = (n1 / mb1) / (n2 / mb2)
    se = math.sqrt(1 / n1 + 1 / n2)
    p = math.erfc(abs(math.log(r) / se) / math.sqrt(2))
    return r, r * math.exp(-1.96 * se), r * math.exp(1.96 * se), p


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    bed = load(SMALL + ".bed")
    cn = load(CN, lambda f: float(f[3]) >= 1)
    kept = {c: intersect(v, cn.get(c, [])) for c, v in bed.items()}
    mb = {c: sum(e - s for s, e in v) / 1e6 for c, v in kept.items()}
    vcf = subprocess.run(["bcftools", "view", "-H", "-v", "snps", SMALL + "_tumorvariants.vcf.gz"], capture_output=True, text=True, check=True).stdout
    raw, n = defaultdict(int), defaultdict(int)
    for line in vcf.splitlines():
        f = line.split("\t")
        c, p = f[0], int(f[1]) - 1
        raw[c] += 1
        v = kept.get(c, [])
        i = bisect.bisect_right(v, (p, 1 << 60)) - 1
        if i >= 0 and v[i][0] <= p < v[i][1]:
            n[c] += 1

    rows = []
    tested = [c for c in CHROMS if mb.get(c + "_hap1", 0) >= MIN_MB and mb.get(c + "_hap2", 0) >= MIN_MB]
    for c in CHROMS:
        a, b = c + "_hap1", c + "_hap2"
        row = dict(chrom=c, hap1_raw=raw[a], hap2_raw=raw[b], hap1_snv=n[a], hap2_snv=n[b], hap1_mb=round(mb.get(a, 0), 1), hap2_mb=round(mb.get(b, 0), 1),
                   hap1_per_mb="", hap2_per_mb="", ratio="", ci_low="", ci_high="", p="", p_bonferroni="")
        if mb.get(a, 0) >= MIN_MB:
            row["hap1_per_mb"] = round(n[a] / mb[a], 2)
        if mb.get(b, 0) >= MIN_MB:
            row["hap2_per_mb"] = round(n[b] / mb[b], 2)
        if c in tested:
            r, lo, hi, p = compare(n[a], mb[a], n[b], mb[b])
            row.update(ratio=round(r, 3), ci_low=round(lo, 3), ci_high=round(hi, 3), p=f"{p:.2g}", p_bonferroni=f"{min(1, p * len(tested)):.2g}")
        rows.append(row)
    with open(out / "per_chromosome.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys(), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    groups = [("raw_all", CHROMS, raw, False), ("retained_all", CHROMS, n, True), ("retained_autosomes", CHROMS[:-1], n, True), ("retained_chrX", ["chrX"], n, True), ("retained_both_haps_autosomes", [c for c in tested if c != "chrX"], n, True)]
    with open(out / "summary.tsv", "w") as f:
        f.write("group\thap1_snv\thap1_mb\thap1_per_mb\thap2_snv\thap2_mb\thap2_per_mb\tratio\tci_low\tci_high\tp\n")
        for name, cs, cnt, use in groups:
            n1, n2 = sum(cnt[c + "_hap1"] for c in cs), sum(cnt[c + "_hap2"] for c in cs)
            if not use:
                line = f"{name}\t{n1}\t\t\t{n2}\t\t\t\t\t\t"
            else:
                m1, m2 = sum(mb.get(c + "_hap1", 0) for c in cs), sum(mb.get(c + "_hap2", 0) for c in cs)
                r, lo, hi, p = compare(n1, m1, n2, m2)
                line = f"{name}\t{n1}\t{m1:.0f}\t{n1 / m1:.2f}\t{n2}\t{m2:.0f}\t{n2 / m2:.2f}\t{r:.3f}\t{lo:.3f}\t{hi:.3f}\t{p:.2g}"
            print(line)
            f.write(line + "\n")

    fig, ax = plt.subplots(figsize=(9, 3.9), dpi=170)
    for i, c in enumerate(CHROMS):
        d1, d2 = rows[i]["hap1_per_mb"], rows[i]["hap2_per_mb"]
        if d1 != "" and d2 != "":
            ax.plot([i, i], [d1, d2], color=LINE, lw=2, zorder=1)
        if d1 != "":
            ax.scatter(i, d1, s=48, color=HAP1, marker="o", edgecolor="white", linewidth=1, zorder=2, label="hap1" if i == 0 else None)
        if d2 != "":
            ax.scatter(i, d2, s=52, color=HAP2, marker="s", edgecolor="white", linewidth=1, zorder=2, label="hap2" if i == 0 else None)
    x = CHROMS.index("chrX")
    ax.annotate("inactive X 那條", (x, rows[x]["hap2_per_mb"]), xytext=(-8, 0), textcoords="offset points", ha="right", va="center", fontsize=9, color=INK)
    ax.set_xticks(range(len(CHROMS)), [c.removeprefix("chr") for c in CHROMS])
    ax.set_ylim(0, 4.2)
    ax.set_xlabel("染色體（只畫留著至少 20 Mb 的那條）", fontsize=9.5, color=INK)
    ax.set_ylabel("Truncal SNV 個／Mb", fontsize=9.5, color=INK)
    ax.grid(axis="y", color=LINE, lw=.6)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(colors=MUTE, labelsize=8.5, length=0)
    ax.legend(loc="lower left", frameon=False, fontsize=9, ncol=2)
    fig.tight_layout()
    fig.savefig(out / "density_by_chromosome.png")


if __name__ == "__main__":
    main()
