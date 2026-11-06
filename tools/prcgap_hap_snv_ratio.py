#!/usr/bin/env python3
"""PRCGAP (Sakamoto 2026): somatic SNV density on the two haplotypes of each chromosome, in 8 cancer cell lines.

Usage: python3 tools/prcgap_hap_snv_ratio.py <extracted_dir> <out_dir>

hap1 and hap2 are arbitrary across chromosomes, so a genome-wide hap1 total has no meaning. Every comparison stays
inside one chromosome or one window. A haplotype bin counts as retained when its CBS segment has copy number >= 0.5.
The depth and flag filters were checked against the GIAB HG008 benchmark (see the report).

The main comparison is the balanced window: 20 Mb on CHM13 where both haplotypes are retained with equal copy number.
It compares SNV counts directly, because per-chromosome rates follow copy number and contig lengths can be wrong.
Windows are located through the contig-to-CHM13 table with a linear scale along each contig, which is coarse.
Chromosome rates use a Poisson test on log(rate) with exposure taken as fixed; they are kept as a confounded view.
"""
import bisect
import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"

csv.field_size_limit(10**8)
SAMPLES = ["COLO829", "HG008", "H1437", "H2009", "H209", "H2126", "HCC1937", "HCC1954"]
NORMAL = dict(COLO829="COLO829BL", HG008="HG008N", H1437="BL1437", H2009="BL2009", H209="BL209", H2126="BL2126", HCC1937="HCC1937BL", HCC1954="HCC1954BL")
CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]
BIN = 50_000
MIN_CN = 0.5
MIN_MB = 20  # both haplotypes need this much retained sequence before a chromosome is compared
MIN_SNV = 10  # a comparison also needs this many SNVs in total
MAX_CN_GAP = .3  # a window is balanced when mean copy numbers differ by less than this
WINDOW = 20_000_000
INK, MUTE, LINE = "#1c2a26", "#5a6a62", "#d4dcd6"


def base_filter(r):
    """The paper's thresholds that this deposit lets us apply. Normal_depth is 0 in every row, so it is not used."""
    try:
        return (r["misassembly"] == "False" and r["gnomAD"] in ("-", "") and float(r["Depth"]) >= 10 and float(r["VAF"]) >= .05
                and float(r["Kmer_ratio"]) >= .8 and r["Haplotype"] in ("haplotype1", "haplotype2"))
    except ValueError:
        return False


def strict_filter(r):
    """base plus two undocumented columns. On HG008 this set agrees with GIAB at 99.9%, but it favors clonal SNVs."""
    return base_filter(r) and r["point_mutation_other"] == "True" and r["GRCh38_flag"] == "True"


def compare(n1, mb1, n2, mb2):
    """Rate ratio hap1 / hap2 with 0.5 added to each count, its 95% CI and two-sided p."""
    a, b = n1 + .5, n2 + .5
    r = (a / mb1) / (b / mb2)
    se = math.sqrt(1 / a + 1 / b)
    z = math.log(r) / se
    return r, r * math.exp(-1.96 * se), r * math.exp(1.96 * se), math.erfc(abs(z) / math.sqrt(2)), z


def tsv(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_sample(root, s):
    """Return contig info, retained index intervals and the CHM13 placement of each haplotype's contigs."""
    contigs, retained, placement = {}, {}, {}
    for h in ("hap1", "hap2"):
        for row in tsv(root / s / "copynumber" / f"{s}.{h}.copynumber.txt"):
            c = contigs.setdefault(row["contig"], dict(chrom=row["chrom"], hap=h, first=float(row["index"]), n=0))
            c["n"] += 1
        segs = defaultdict(list)
        for row in tsv(root / s / "copynumber" / f"{s}.{h}.cbs.split.txt"):
            if float(row["copynumber"]) >= MIN_CN:
                chrom = row["chrom"] if row["chrom"].startswith("chr") else "chr" + row["chrom"]
                segs[chrom].append((float(row["start_index"]), float(row["end_index"]), int(row["bins"]), float(row["copynumber"])))
        retained[h] = {k: sorted(v) for k, v in segs.items()}
        for line in open(root / s / "ref_table" / f"{NORMAL[s]}.{h}.ref.table"):
            f = line.split()
            placement.setdefault(f[0], []).append(dict(cs=int(f[1]), ce=int(f[2]), strand=f[3], chrom=f[4], rs=int(f[5]), re=int(f[6])))
    return contigs, retained, placement


def index_of(info, placement, contig, pos):
    """The plot index of a contig position. Bins follow the contig, reversed when the contig maps to the minus strand."""
    i = pos // BIN
    p = placement.get(contig, [])
    if p and p[0]["strand"] == "-":
        i = info["n"] - 1 - i
    return info["first"] + i


def segment_cn(segs, idx):
    """Copy number of the retained segment holding this index, or None."""
    i = bisect.bisect_right(segs, (idx, 1e18)) - 1
    return segs[i][3] if i >= 0 and segs[i][0] <= idx <= segs[i][1] + 1 else None


def retained_windows(info_by_contig, retained, placement, hap):
    """Retained bins and summed copy number in each 20 Mb CHM13 window for one haplotype, placing bins linearly."""
    hit, cn = defaultdict(int), defaultdict(float)
    for contig, info in info_by_contig.items():
        if info["hap"] != hap or contig not in placement:
            continue
        segs = retained[hap].get(info["chrom"], [])
        for b in range(info["n"]):
            value = segment_cn(segs, index_of(info, placement, contig, b * BIN))
            if value is None:
                continue
            pos = b * BIN
            for p in placement[contig]:
                if p["cs"] <= pos < p["ce"]:
                    frac = (pos - p["cs"]) / max(p["ce"] - p["cs"], 1)
                    ref = p["rs"] + frac * (p["re"] - p["rs"]) if p["strand"] == "+" else p["re"] - frac * (p["re"] - p["rs"])
                    hit[(p["chrom"], int(ref // WINDOW))] += 1
                    cn[(p["chrom"], int(ref // WINDOW))] += value
                    break
    return hit, cn


def cn_on_chrom(segs):
    """Mean copy number over the retained segments of one haplotype on one chromosome."""
    return sum(x[2] * x[3] for x in segs) / sum(x[2] for x in segs)


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    chrom_rows, summary, window_rows = [], [], []
    for s in SAMPLES:
        contigs, retained, placement = load_sample(root, s)
        rows = tsv(root / s / "point_mutation" / f"{s}.deepsomatic.snv.annotated_checked_gnomad.txt")
        strict = [r for r in rows if strict_filter(r)]
        base_n = sum(base_filter(r) for r in rows)
        n = defaultdict(int)
        windows = defaultdict(lambda: [0, 0])
        kept = outside = 0
        for r in strict:
            info = contigs.get(r["Contig"])
            hap = "hap" + r["Haplotype"][-1]
            if info is None or info["hap"] != hap:
                continue
            if segment_cn(retained[hap].get(info["chrom"], []), index_of(info, placement, r["Contig"], int(r["Start"]))) is not None:
                kept += 1
                n[(info["chrom"], hap)] += 1
                if r["chm13_pos"].isdigit() and r["chm13_contig"] == info["chrom"]:
                    windows[(info["chrom"], int(r["chm13_pos"]) // WINDOW)][int(hap[-1]) - 1] += 1
            else:
                outside += 1
        mb = {(c, h): sum(x[2] for x in retained[h].get(c, [])) * BIN / 1e6 for c in CHROMS for h in ("hap1", "hap2")}
        tested = [c for c in CHROMS if mb[(c, "hap1")] >= MIN_MB and mb[(c, "hap2")] >= MIN_MB and n[(c, "hap1")] + n[(c, "hap2")] >= MIN_SNV]
        autos = [c for c in tested if c != "chrX"]
        chi2, log_ratios, sig = 0, [], []
        for c in CHROMS:
            m1, m2 = mb[(c, "hap1")], mb[(c, "hap2")]
            row = dict(sample=s, chrom=c, hap1_snv=n[(c, "hap1")], hap1_mb=round(m1, 1), hap2_snv=n[(c, "hap2")], hap2_mb=round(m2, 1), state="", ratio="", ci_low="", ci_high="", p="", p_bonferroni="")
            row["state"] = "both" if m1 >= MIN_MB and m2 >= MIN_MB else ("hap1_only" if m1 >= MIN_MB else ("hap2_only" if m2 >= MIN_MB else "little_retained"))
            if c in tested:
                r, lo, hi, p, z = compare(n[(c, "hap1")], m1, n[(c, "hap2")], m2)
                pb = min(1, p * len(tested))
                row.update(ratio=round(r, 3), ci_low=round(lo, 3), ci_high=round(hi, 3), p=f"{p:.2g}", p_bonferroni=f"{pb:.2g}")
                if c != "chrX":
                    chi2 += z * z
                    log_ratios.append(abs(math.log2(r)))
                if pb < .05:
                    sig.append(f"{c}({r:.2f})")
            chrom_rows.append(row)

        hit1, cn1 = retained_windows(contigs, retained, placement, "hap1")
        hit2, cn2 = retained_windows(contigs, retained, placement, "hap2")
        full = WINDOW / BIN
        keys = [k for k in windows if k[0] != "chrX" and hit1[k] / full >= .8 and hit2[k] / full >= .8 and sum(windows[k]) >= MIN_SNV]
        balanced = [k for k in keys if abs(cn1[k] / hit1[k] - cn2[k] / hit2[k]) < MAX_CN_GAP]
        sig_w, chi_w, folds, more = 0, 0, [], 0
        for k in sorted(balanced, key=lambda x: (CHROMS.index(x[0]), x[1])):
            a, b = windows[k]
            r, lo, hi, p, z = compare(a, 1, b, 1)
            pb = min(1, p * len(balanced))
            sig_w += pb < .05
            chi_w += z * z
            folds.append(abs(math.log2(r)))
            more += max(a, b)
            window_rows.append(dict(sample=s, chrom=k[0], start_mb=k[1] * 20, hap1_snv=a, hap2_snv=b, hap1_cn=round(cn1[k] / hit1[k], 2), hap2_cn=round(cn2[k] / hit2[k], 2), ratio=round(r, 3), p=f"{p:.2g}", p_bonferroni=f"{pb:.2g}"))
        total_w = sum(sum(windows[k]) for k in balanced)
        xs, ys = [], []
        for c in autos:
            m = [cn_on_chrom(retained[h].get(c, [])) for h in ("hap1", "hap2")]
            r = compare(n[(c, "hap1")], mb[(c, "hap1")], n[(c, "hap2")], mb[(c, "hap2")])[0]
            xs.append(math.log2(m[0] / m[1]))
            ys.append(math.log2(r))
        cn_corr = round(statistics.correlation(xs, ys), 2) if len(xs) > 2 else ""
        ordered = sorted(log_ratios)
        n1, n2 = sum(n[(c, "hap1")] for c in autos), sum(n[(c, "hap2")] for c in autos)
        m1, m2 = sum(mb[(c, "hap1")] for c in autos), sum(mb[(c, "hap2")] for c in autos)
        summary.append(dict(sample=s, all_rows=len(rows), base_snv=base_n, strict_snv=len(strict), strict_retained=kept, strict_outside=outside,
                            chroms_compared=len(tested), autosomes_compared=len(autos), median_abs_log2_ratio=round(ordered[len(ordered) // 2], 3) if ordered else "",
                            chi2_per_df=round(chi2 / len(autos), 2) if autos else "", pooled_autosome_ratio=round((n1 / m1) / (n2 / m2), 3) if n2 else "",
                            single_hap_chroms=sum(1 for r in chrom_rows if r["sample"] == s and r["state"] in ("hap1_only", "hap2_only")),
                            cn_density_corr=cn_corr, chrom_significant=" ".join(sig), windows_with_both=len(keys), balanced_windows=len(balanced), balanced_snv=total_w,
                            balanced_chi2_per_df=round(chi_w / len(balanced), 2) if balanced else "", balanced_median_abs_log2=round(statistics.median(folds), 3) if folds else "",
                            balanced_larger_side_share=round(more / total_w, 3) if total_w else "", balanced_significant=sig_w))
        print(summary[-1])

    for name, data in (("per_chromosome.tsv", chrom_rows), ("summary.tsv", summary), ("per_window_20mb.tsv", window_rows)):
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, data[0].keys(), delimiter="\t")
            w.writeheader()
            w.writerows(data)
    plot(window_rows, out)


def plot(windows, out):
    """Each dot is a balanced window. Labels are arbitrary, so the axis shows the size of the difference, not its side."""
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=170)
    hue = "#1f6f8b"
    for y, s in enumerate(SAMPLES):
        data = [w for w in windows if w["sample"] == s]
        for i, w in enumerate(data):
            x = min(abs(math.log2(float(w["ratio"]))), 3)
            sig = float(w["p_bonferroni"]) < .05
            jitter = ((i * 7) % 11 - 5) * .04
            ax.scatter(x, y + jitter, s=26, facecolor=hue if sig else "white", edgecolor=hue, linewidth=.9, zorder=2)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(range(len(SAMPLES)), SAMPLES, fontsize=9, color=INK)
    ax.set_ylim(len(SAMPLES) - .4, -.6)
    ax.set_xticks([0, 0.585, 1, 2, 3], ["一樣多", "1.5 倍", "2 倍", "4 倍", "≥8 倍"], fontsize=8.5, color=MUTE)
    ax.set_xlabel("兩條拷貝數相同的 20 Mb 區段：較多那條是較少那條的幾倍", fontsize=9.5, color=INK)
    ax.grid(axis="x", color=LINE, lw=.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(length=0)
    ax.scatter([], [], s=26, facecolor=hue, edgecolor=hue, label="校正後顯著")
    ax.scatter([], [], s=26, facecolor="white", edgecolor=hue, label="不顯著")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "balanced_window_difference.png")


if __name__ == "__main__":
    main()
