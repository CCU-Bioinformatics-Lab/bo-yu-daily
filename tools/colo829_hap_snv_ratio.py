#!/usr/bin/env python3
"""Compare somatic SNV counts between the two haplotypes of COLO829 (Sohn 2026, Cell, public VCF).

Usage (from the repo root):
  python3 -I tools/colo829_hap_snv_ratio.py <somatic_snvs.vcf.gz> <out_dir>

Three levels, because the raw hap1:hap2 count is not interpretable alone:
  A. raw counts and SNV/Mb over the assembled length;
  B. SNV/Mb over "occupied" length, which drops long SNV-free stretches (lost homologs and deletions);
  C. homolog pairs: hap1 share of SNVs against the share expected from occupied length.

Pairs come from the authors' code (hCN/plot_log2hcn.py) when it names them. Other pairs are inferred:
two contigs are mutual nearest neighbours by length and differ by at most 1%.
hap1 and hap2 are assembly labels, so the direction of a pair says nothing about dad or mom, and
shares from different pairs are not summed into one direction.
"""
import csv
import gzip
import re
import sys
from collections import Counter, defaultdict
from math import exp, lgamma, log, sqrt
from pathlib import Path

AUTHOR_PAIRS = {"chr1": ("haplotype1-0000012", "haplotype2-0000059"), "chr3": ("haplotype1-0000011", "haplotype2-0000058"),
                "chr4": ("haplotype1-0000013", "haplotype2-0000060"), "chr14": ("haplotype1-0000018", "haplotype2-0000070")}
# The authors split chr16 over several contigs, so it is compared as a group.
CHR16 = (["haplotype1-0000008", "haplotype1-0000016"], ["haplotype2-0000055", "haplotype2-0000046", "haplotype2-0000067", "haplotype2-0000066"])
MIN_LEN = 20_000_000
MAX_LEN_DIFF = 0.01


def read_vcf(path):
    lengths, snvs = {}, defaultdict(list)
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("##contig"):
                m = re.search(r"ID=([^,]+),length=(\d+)", line)
                lengths[m[1]] = int(m[2])
            elif not line.startswith("#"):
                c = line.split("\t", 9)
                info = dict(x.split("=", 1) for x in c[7].split(";") if "=" in x)
                snvs[c[0]].append((int(c[1]), info.get("CN", "NA")))
    return lengths, snvs


def occupied(length, positions, gap):
    """Assembled length minus every SNV-free stretch longer than gap, contig ends included."""
    if not positions:
        return 0
    points = [0] + sorted(positions) + [length]
    return length - sum(b - a for a, b in zip(points, points[1:]) if b - a > gap)


def binom_p(k, n, p):
    """Exact two-sided binomial test: sum of outcomes no more likely than k."""
    pmf = [exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log(1 - p)) for i in range(n + 1)]
    return min(1.0, sum(x for x in pmf if x <= pmf[k] * (1 + 1e-7)))


def chi2_sf(x, df):
    """Upper tail of chi-square, from the series for the lower regularized gamma function."""
    a, z = df / 2, x / 2
    if z <= 0:
        return 1.0
    if z > a + 40:
        # Continued fraction for the upper tail when z is far above the mean.
        b, c, d, h = z + 1 - a, 1e300, 1 / (z + 1 - a), 1 / (z + 1 - a)
        for i in range(1, 500):
            an = -i * (i - a)
            b += 2
            d = 1 / (an * d + b)
            c = b + an / c
            h *= d * c
        return exp(-z + a * log(z) - lgamma(a)) * h
    term = total = 1 / a
    for i in range(1, 2000):
        term *= z / (a + i)
        total += term
    return max(0.0, 1 - exp(-z + a * log(z) - lgamma(a)) * total)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def inferred_pairs(lengths, used):
    def nearest(c, others):
        return min(others, key=lambda o: abs(lengths[o] - lengths[c]))
    h1 = [c for c in lengths if c.startswith("haplotype1") and c not in used and lengths[c] >= MIN_LEN]
    h2 = [c for c in lengths if c.startswith("haplotype2") and c not in used and lengths[c] >= MIN_LEN]
    pairs = []
    for a in h1:
        b = nearest(a, h2)
        if nearest(b, h1) == a and abs(lengths[a] - lengths[b]) / max(lengths[a], lengths[b]) <= MAX_LEN_DIFF:
            pairs.append((a, b))
    return pairs


def main():
    vcf, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    lengths, snvs = read_vcf(vcf)
    hap = lambda c: c.split("-")[0]

    # Level A and B
    rows = []
    for gap in (2_000_000, 5_000_000, 10_000_000):
        tot, ln, oc = Counter(), Counter(), Counter()
        for c, L in lengths.items():
            pos = [p for p, _ in snvs.get(c, [])]
            tot[hap(c)] += len(pos)
            ln[hap(c)] += L
            oc[hap(c)] += occupied(L, pos, gap)
        for h in ("haplotype1", "haplotype2"):
            rows.append({"gap_mb": gap // 1_000_000, "hap": h, "snv": tot[h], "length_mb": round(ln[h] / 1e6, 1), "snv_per_mb": round(tot[h] / ln[h] * 1e6, 3),
                         "occupied_mb": round(oc[h] / 1e6, 1), "snv_per_occupied_mb": round(tot[h] / oc[h] * 1e6, 3)})
    with open(out / "haplotype_totals.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys(), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    # Level C
    gap = 5_000_000
    used = {c for p in AUTHOR_PAIRS.values() for c in p} | set(CHR16[0]) | set(CHR16[1])
    pairs = [(name, [a], [b], "authors") for name, (a, b) in AUTHOR_PAIRS.items()]
    pairs.append(("chr16", CHR16[0], CHR16[1], "authors"))
    pairs += [(f"len{lengths[a] // 1_000_000}Mb", [a], [b], "length") for a, b in inferred_pairs(lengths, used)]
    table = []
    for name, group_a, group_b, src in pairs:
        a, b = "+".join(group_a), "+".join(group_b)
        pa = [x for c in group_a for x in snvs.get(c, [])]
        pb = [x for c in group_b for x in snvs.get(c, [])]
        oa = sum(occupied(lengths[c], [p for p, _ in snvs.get(c, [])], gap) for c in group_a)
        ob = sum(occupied(lengths[c], [p for p, _ in snvs.get(c, [])], gap) for c in group_b)
        ca, cb = Counter(x for _, x in pa), Counter(x for _, x in pb)
        n = len(pa) + len(pb)
        row = {"pair": name, "source": src, "hap1_contig": a, "hap2_contig": b, "hap1_mb": round(sum(lengths[c] for c in group_a) / 1e6, 1), "hap2_mb": round(sum(lengths[c] for c in group_b) / 1e6, 1),
               "hap1_snv": len(pa), "hap2_snv": len(pb), "hap1_occupied_mb": round(oa / 1e6, 1), "hap2_occupied_mb": round(ob / 1e6, 1),
               "hap1_main_cn": ca.most_common(1)[0][0] if ca else "", "hap2_main_cn": cb.most_common(1)[0][0] if cb else ""}
        both = bool(pa) and bool(pb)
        row["both_retained"] = both
        pure = both and ca.most_common(1)[0][1] / len(pa) >= .95 and cb.most_common(1)[0][1] / len(pb) >= .95 and ca.most_common(1)[0][0] == cb.most_common(1)[0][0]
        row["same_cn_95pct"] = pure
        if both:
            expected = oa / (oa + ob)
            lo, hi = wilson(len(pa), n)
            row.update(hap1_share=round(len(pa) / n, 4), ci_low=round(lo, 4), ci_high=round(hi, 4), expected_share=round(expected, 4),
                       excess=round(len(pa) / n - expected, 4), p_binom=binom_p(len(pa), n, expected),
                       ratio_density=round((len(pa) / oa) / (len(pb) / ob), 3))
        table.append(row)
    cols = list(dict.fromkeys(k for r in table for k in r))
    with open(out / "homolog_pairs.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, cols, delimiter="\t")
        w.writeheader()
        w.writerows(table)

    # Heterogeneity: is any pair off its expected share, using a chi-square sum over pairs?
    for label, keep in (("both retained", lambda r: r["both_retained"]), ("same CN", lambda r: r["same_cn_95pct"])):
        sel = [r for r in table if keep(r)]
        stat = sum((r["hap1_snv"] + r["hap2_snv"]) * (r["hap1_share"] - r["expected_share"]) ** 2 / (r["expected_share"] * (1 - r["expected_share"])) for r in sel)
        hits = [r["pair"] for r in sel if r["p_binom"] * len(sel) < .05]
        print(f"{label}: pairs {len(sel)}, SNV {sum(r['hap1_snv'] + r['hap2_snv'] for r in sel)}, chi2 {stat:.1f}, p {chi2_sf(stat, len(sel)):.3g}, "
              f"Bonferroni hits {hits}, max |excess| {max(abs(r['excess']) for r in sel):.3f}, "
              f"median |excess| {sorted(abs(r['excess']) for r in sel)[len(sel) // 2]:.3f}")

    for r in rows:
        print(r)
    # Genome-wide rate ratio over occupied length, with a Poisson 95% CI on the log scale.
    r1, r2 = [r for r in rows if r["gap_mb"] == 5]
    rr = r1["snv_per_occupied_mb"] / r2["snv_per_occupied_mb"]
    se = sqrt(1 / r1["snv"] + 1 / r2["snv"])
    print(f"rate ratio hap1/hap2 over occupied length {rr:.4f}, 95% CI {exp(log(rr) - 1.96 * se):.4f}-{exp(log(rr) + 1.96 * se):.4f}")
    unpaired = [(c, round(L / 1e6, 1), len(snvs.get(c, []))) for c, L in lengths.items() if L >= MIN_LEN and c not in {x for _, ga, gb, _ in pairs for x in ga + gb}]
    print("unpaired contigs >= 20 Mb:", unpaired)
    print("zero-SNV contigs >= 20 Mb:", [(c, round(L / 1e6, 1)) for c, L in lengths.items() if L >= MIN_LEN and not snvs.get(c)])
    print("zero-SNV length by hap (Mb):", {h: round(sum(L for c, L in lengths.items() if not snvs.get(c) and c.startswith(h)) / 1e6, 1) for h in ("haplotype1", "haplotype2")})
    print("pairs:")
    for r in table:
        print(" ", r["pair"], r["source"], r["hap1_snv"], r["hap2_snv"], r["hap1_main_cn"], r["hap2_main_cn"], r.get("hap1_share"), r.get("expected_share"), r.get("excess"), f"{r.get('p_binom', 1):.2g}")


if __name__ == "__main__":
    main()
