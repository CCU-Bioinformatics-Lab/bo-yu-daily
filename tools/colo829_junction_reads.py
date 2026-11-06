#!/usr/bin/env python3
"""Find ONT reads that join chr1 and chr10 near the t(1;10) truth-set breakpoint, and read blood het alleles on them.

Usage: python3 tools/colo829_junction_reads.py [flank_bp]

For reads whose alignment on chr1 or chr10 has a supplementary alignment on the other chromosome, each blood het
site on the read is labelled by the allele it carries and by that allele's share of all tumor reads. A junction
carried on the minor allele means the third copy of the 2:1 region is the one on the rearranged chromosome.
"""
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

import pysam

REF = "/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
TUMOR = os.environ.get("COLO_TUMOR", "/big8_disk/data/COLO829/ONT_R10/COLO829.cram")
BLOOD = os.environ.get("COLO_BLOOD", "/big8_disk/data/COLO829/ONT_R10/COLO829BL.cram")
FLANK = int(sys.argv[1]) if len(sys.argv) > 1 else 300_000
# The truth set is on hg19 (chr1:87,337,011 and chr10:36,119,127). The GRCh38 positions are about 0.3-0.5 Mb lower.
SEARCH = {"chr1": (86_400_000, 87_400_000), "chr10": (35_400_000, 36_200_000)}


def het_sites(chrom, start, end):
    cmd = ["bcftools", "mpileup", "-f", REF, "-r", f"{chrom}:{start}-{end}", "-q", "20", "-Q", "15", "-a", "FORMAT/AD", "--max-depth", "400", "-I", "-Ou", BLOOD, TUMOR]
    q = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    r = subprocess.run(["bcftools", "query", "-f", "%POS\t%REF\t%ALT[\t%AD]\n"], stdin=q.stdout, capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        pos, ref, alt, adb, adt = line.split("\t")
        ab, at = list(map(int, adb.split(","))), list(map(int, adt.split(",")))
        if len(ab) < 2 or sum(ab) < 12 or not .33 <= ab[1] / sum(ab) <= .67 or len(alt.split(",")[0]) != 1:
            continue
        if at[0] + at[1] >= 20:
            out[int(pos)] = (ref, alt.split(",")[0], at[1] / (at[0] + at[1]))
    return out


def main():
    bam = pysam.AlignmentFile(TUMOR, "rc", reference_filename=REF)
    junction = defaultdict(list)
    for chrom, (a, b) in SEARCH.items():
        other = "chr10" if chrom == "chr1" else "chr1"
        o_a, o_b = SEARCH[other]
        for read in bam.fetch(chrom, a, b):
            if read.is_secondary or read.is_duplicate or read.mapping_quality < 20 or not read.has_tag("SA"):
                continue
            for sa in read.get_tag("SA").split(";"):
                if not sa:
                    continue
                c, p = sa.split(",")[:2]
                if c == other and o_a - 500_000 <= int(p) <= o_b + 500_000:
                    bp = read.reference_end if read.cigartuples[-1][0] in (4, 5) else read.reference_start
                    junction[chrom].append((read, bp, c, int(p)))
    print({k: len(v) for k, v in junction.items()})
    for chrom, items in junction.items():
        bps = Counter(round(bp, -2) for _, bp, _, _ in items)
        print(chrom, "breakpoint clusters (100 bp bins):", bps.most_common(5))
        if not items:
            continue
        lo = min(r.reference_start for r, *_ in items)
        hi = max(r.reference_end for r, *_ in items)
        hets = het_sites(chrom, lo, hi)
        shares = []
        for read, *_ in items:
            pairs = {r: q for q, r in read.get_aligned_pairs(matches_only=True)}
            for pos, (ref, alt, af) in hets.items():
                q = pairs.get(pos - 1)
                if q is None:
                    continue
                base = read.query_sequence[q]
                if base == alt:
                    shares.append(af)
                elif base == ref:
                    shares.append(1 - af)
        minor = sum(s < .42 for s in shares)
        major = sum(s > .58 for s in shares)
        print(chrom, f"het sites in span {len(hets)}, allele observations {len(shares)}, on minor allele {minor}, on major allele {major}, balanced {len(shares) - minor - major}")
        rl = sorted(r.query_length for r, *_ in items)
        print(chrom, "read length median", rl[len(rl) // 2], "max", rl[-1], "span", lo, hi)


if __name__ == "__main__":
    main()
