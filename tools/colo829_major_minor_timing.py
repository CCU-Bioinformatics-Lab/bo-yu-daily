#!/usr/bin/env python3
"""Split SNVs on the 2-copy haplotype of COLO829 2:1 regions into early and late, and test symmetry.

Usage: python3 tools/colo829_major_minor_timing.py <snv_phase.tsv> <clairs_snv.vcf.gz> <out_dir>

With three copies (major 2, minor 1) and purity near 1:
  major, before the duplication: on 2 of 3 copies, VAF about 0.67 (early)
  major, after the duplication:  on 1 of 3 copies, VAF about 0.33 (late)
  minor, any time:               on 1 of 3 copies, VAF about 0.33 (cannot be split)
If each copy mutates at the same rate, minor = early + late / 2, because after the duplication the major
haplotype has two copies and the minor haplotype one. Each count is treated as Poisson for the z score.
"""
import csv
import subprocess
import sys
from collections import Counter, defaultdict
from math import erfc, sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"
CORE = ["chr1p", "chr2", "chr6", "chr10", "chr12", "chr17", "chr18", "chr19", "chr21"]
INK, MUTE, LINE, MAJOR, MINOR = "#1c2a26", "#5a6a62", "#d4dcd6", "#3f8fb0", "#8a9aa8"


def side(share):
    return "minor" if share < .42 else ("major" if share > .58 else "balanced")


def test(minor, early, late):
    expected = early + late / 2
    var = minor + early + late / 4
    z = (minor - expected) / sqrt(var) if var else 0
    return expected, z, erfc(abs(z) / sqrt(2))


def main():
    phase, vcf, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    q = subprocess.run(["bcftools", "query", "-f", "%CHROM\t%POS[\t%AF\t%DP]\n", vcf], capture_output=True, text=True).stdout
    af = {}
    for line in q.splitlines():
        c, p, a, d = line.split("\t")
        if a not in (".", ""):
            af[(c, int(p))] = float(a)
    groups = defaultdict(lambda: {"major": [], "minor": []})
    for r in csv.DictReader(open(phase), delimiter="\t"):
        if r["result"] != "linked":
            continue
        pos = int(r["pos"])
        region = "chr1p" if r["chrom"] == "chr1" and pos < 85_000_000 else (r["chrom"] if r["state"] == "2:1" else None)
        if region not in CORE or (r["chrom"], pos) not in af:
            continue
        s = side(float(r["allele_share"]))
        if s in ("major", "minor"):
            groups[region][s].append(af[(r["chrom"], pos)])

    rows = []
    for cut in (.45, .50, .55):
        E = L = M = 0
        for region in CORE:
            maj, mi = groups[region]["major"], groups[region]["minor"]
            e, l, m = sum(v >= cut for v in maj), sum(v < cut for v in maj), len(mi)
            E, L, M = E + e, L + l, M + m
            exp, z, p = test(m, e, l)
            rows.append(dict(cut=cut, region=region, early_major=e, late_major=l, minor=m, expected_minor=round(exp, 1), ratio=round(m / exp, 3) if exp else "", z=round(z, 2), p=round(p, 4)))
        exp, z, p = test(M, E, L)
        rows.append(dict(cut=cut, region="ALL", early_major=E, late_major=L, minor=M, expected_minor=round(exp, 1), ratio=round(M / exp, 3), z=round(z, 2), p=round(p, 4)))
        print(f"cut {cut}: early {E} late {L} minor {M} expected {exp:.1f} ratio {M / exp:.3f} z {z:.2f} p {p:.3g}")
    with open(out / "early_late_major_minor.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys(), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    maj = [v for g in CORE for v in groups[g]["major"]]
    mi = [v for g in CORE for v in groups[g]["minor"]]
    print("minor VAF >= 0.5:", sum(v >= .5 for v in mi), "of", len(mi))
    print("VAF deciles major", [Counter(int(v * 10) for v in maj)[i] for i in range(11)])
    print("VAF deciles minor", [Counter(int(v * 10) for v in mi)[i] for i in range(11)])

    fig, ax = plt.subplots(2, 1, figsize=(7.5, 4.8), dpi=170, sharex=True)
    bins = [i / 40 for i in range(41)]
    ax[0].hist(maj, bins=bins, color=MAJOR, edgecolor="white", linewidth=.5)
    ax[1].hist(mi, bins=bins, color=MINOR, edgecolor="white", linewidth=.5)
    ax[0].set_title(f"2 份那條（{len(maj):,} 個突變）", loc="left", fontsize=10.5, color=INK, fontweight="bold")
    ax[1].set_title(f"1 份那條（{len(mi):,} 個突變）", loc="left", fontsize=10.5, color=INK, fontweight="bold")
    ax[1].set_xlabel("ClairS VAF", fontsize=9.5, color=INK)
    for a in ax:
        a.axvline(.5, color=INK, lw=1, ls="--")
        a.set_ylabel("突變數", fontsize=9, color=INK)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.spines["left"].set_color(LINE)
        a.spines["bottom"].set_color(LINE)
        a.tick_params(colors=MUTE, labelsize=8.5)
    fig.tight_layout()
    fig.savefig(out / "vaf_major_minor.png")


if __name__ == "__main__":
    main()
