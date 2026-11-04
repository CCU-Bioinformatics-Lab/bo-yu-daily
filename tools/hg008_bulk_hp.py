#!/usr/bin/env python3
"""Step 3 of the HG008 clone-tree analysis: assembly haplotype (hap1/hap2) of branch SNVs from bulk ONT reads.

For each SNV carried by 2-7 of the 8 clones (shared subclone branches), take bulk tumour ONT reads
(passage 23) with the ALT base, read their alleles at nearby germline het SNPs, and vote: a read is
hap1 or hap2 when >= READ_FRAC of its informative het alleles agree. The SNV gets the hap of
>= SNV_FRAC of its hap-assigned ALT reads.

Het source: the HG008-N column (first sample) of the GIAB V0.4 full_tumornormal VCF, phased against
the HG008-N v6.3 assembly, so hap1/hap2 match the V0.4 SNV and V0.6 CNV labels on each chromosome.
Do not use the clone pipeline's HG008-N-P.dipcall.germline.vcf.gz: its orientation flips between
phase blocks (checked 2026-10-27: 50% agreement with V0.4 truncal SNV haplotypes; this source: 291/291).

Output: bulk_hp.tsv (chrom pos pattern alt_reads ref_reads alt_hap1 alt_hap2 hap)
Usage: python3 tools/hg008_bulk_hp.py BULK_BAM FULL_TUMORNORMAL_VCF TABLE_DIR [THREADS]
(no -I: pysam is a user-site package; run from the repo root, not from a data directory)
"""
import bisect
import collections
import csv
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pysam

BAM, DIPCALL, TAB = sys.argv[1], sys.argv[2], Path(sys.argv[3])
THREADS = int(sys.argv[4]) if len(sys.argv) > 4 else 8
N_CLONES = 8
CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX"}
WINDOW = 20_000
READ_FRAC = 0.8
SNV_FRAC = 0.8
MIN_HAP_READS = 2


def load_hets(chrom):
    """Phased biallelic het SNPs on one chromosome: sorted positions and (ref, alt, alt_hap)."""
    pos, info = [], []
    with pysam.TabixFile(DIPCALL) as tb:
        for line in tb.fetch(chrom):
            f = line.split("\t")
            gt = f[9].split(":")[0]
            if gt not in ("0|1", "1|0") or len(f[3]) != 1 or len(f[4]) != 1:
                continue
            pos.append(int(f[1]))
            info.append((f[3], f[4], 2 if gt == "0|1" else 1))
    return pos, info


def run_chrom(args):
    chrom, snvs = args
    part = TAB / f".bulk_hp_{chrom}.tsv"
    if part.exists():
        return [l.rstrip("\n").split("\t") for l in open(part)]
    hpos, hinfo = load_hets(chrom)
    bam = pysam.AlignmentFile(BAM)
    rows = []
    for s in snvs:
        p = int(s["pos"])
        lo, hi = bisect.bisect_left(hpos, p - WINDOW), bisect.bisect_right(hpos, p + WINDOW)
        n_alt = n_ref = 0
        h = [0, 0]
        for a in bam.fetch(chrom, p - 1, p):
            if a.is_secondary or a.is_supplementary or a.is_duplicate or a.mapping_quality < 20:
                continue
            ref2q = {r: q for q, r in a.get_aligned_pairs(matches_only=True)}
            q = ref2q.get(p - 1)
            if q is None:
                continue
            base = a.query_sequence[q]
            if base == s["ref"]:
                n_ref += 1
            if base != s["alt"]:
                continue
            n_alt += 1
            v = [0, 0]
            for i in range(lo, hi):
                qi = ref2q.get(hpos[i] - 1)
                if qi is None:
                    continue
                ref, alt, alt_hap = hinfo[i]
                b = a.query_sequence[qi]
                if b in (ref, alt):
                    v[(alt_hap if b == alt else 3 - alt_hap) - 1] += 1
            tot = v[0] + v[1]
            if tot and max(v) / tot >= READ_FRAC:
                h[v.index(max(v))] += 1
        hap = "."
        if sum(h) >= MIN_HAP_READS and max(h) / sum(h) >= SNV_FRAC:
            hap = "hap1" if h[0] > h[1] else "hap2"
        rows.append([chrom, str(p), s["pattern"], str(n_alt), str(n_ref), str(h[0]), str(h[1]), hap])
    with open(part, "w") as out:
        for r in rows:
            out.write("\t".join(r) + "\n")
    return rows


def main():
    by_chrom = collections.defaultdict(list)
    with open(TAB / "snv_patterns.tsv") as fh:
        for s in csv.DictReader(fh, delimiter="\t"):
            if s["chrom"] in CHROMS and 2 <= s["pattern"].count(",") + 1 <= N_CLONES - 1:
                by_chrom[s["chrom"]].append(s)
    with ProcessPoolExecutor(THREADS) as ex:
        results = list(ex.map(run_chrom, sorted(by_chrom.items())))
    with open(TAB / "bulk_hp.tsv", "w") as out:
        out.write("chrom\tpos\tpattern\talt_reads\tref_reads\talt_hap1\talt_hap2\thap\n")
        for rows in results:
            for r in rows:
                out.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
