#!/usr/bin/env python3
"""Check the HG008 clone tree against the 119 BioSkryb PTA single cells.

For every SNV in the clone tree (snv_patterns.tsv from hg008_clone_tree.py), look up
whether each single cell's PASS VCF calls the same ALT. A cell's recall of truncal SNVs
is its detection sensitivity; branch recall / truncal recall estimates the fraction of a
branch's SNVs the cell carries (~1 = carries the branch, ~0 = does not).

Usage:
  python3 -I tools/hg008_sc_tree_check.py SNV_PATTERNS.tsv SC_VCF_DIR OUT_DIR [N_PROC]
Outputs (OUT_DIR):
  sc_calls.tsv.gz      cell, chrom, pos, alt_reads, depth for every called tree SNV
  sc_branch_recall.tsv cell x branch: n_called, n_snv, recall, recall / truncal recall
"""
import collections
import csv
import gzip
import os
import re
import subprocess
import sys
import tempfile
from multiprocessing import Pool

TRUNCAL = "2D6,2E6,3E4,SC14,SC24,SC28,SC6,SC9"
MIN_BRANCH = 20


def load_snvs(path):
    snvs = {}
    with open(path) as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if not re.fullmatch(r"chr[0-9XY]+", row["chrom"]):
                continue
            snvs[(row["chrom"], int(row["pos"]))] = (row["ref"], row["alt"], row["pattern"])
    return snvs


def query_cell(args):
    vcf, regions, snvs = args
    cell = re.search(r"(SC\d+)-Z\d+", os.path.basename(vcf)).group(1)
    out = subprocess.run(
        ["bcftools", "query", "-R", regions, "-f", "%CHROM\t%POS\t%REF\t%ALT[\t%GT\t%AD\t%DP]\n", vcf],
        capture_output=True, text=True, check=True).stdout
    calls = []
    for line in out.splitlines():
        chrom, pos, ref, alt, gt, ad, dp = line.split("\t")
        key = (chrom, int(pos))
        if key not in snvs or snvs[key][0] != ref:
            continue
        alts = alt.split(",")
        if snvs[key][1] not in alts or gt in ("0/0", "./.", "0|0"):
            continue
        ads = ad.split(",")
        alt_reads = ads[alts.index(snvs[key][1]) + 1] if len(ads) > len(alts) else "."
        calls.append((cell, chrom, int(pos), alt_reads, dp))
    return cell, calls


def main():
    patterns, vcf_dir, out_dir = sys.argv[1:4]
    n_proc = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    os.makedirs(out_dir, exist_ok=True)
    snvs = load_snvs(patterns)
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as fh:
        for chrom, pos in sorted(snvs):
            fh.write(f"{chrom}\t{pos}\n")
        regions = fh.name
    vcfs = sorted(os.path.join(vcf_dir, f) for f in os.listdir(vcf_dir) if f.endswith(".vcf.gz"))
    with Pool(n_proc) as pool:
        results = pool.map(query_cell, [(v, regions, snvs) for v in vcfs])
    os.unlink(regions)

    branch_size = collections.Counter(p for _, _, p in snvs.values())
    branches = [b for b, n in branch_size.most_common() if n >= MIN_BRANCH]
    with gzip.open(os.path.join(out_dir, "sc_calls.tsv.gz"), "wt") as fh:
        fh.write("cell\tchrom\tpos\tpattern\talt_reads\tdepth\n")
        for _, calls in results:
            for cell, chrom, pos, a, d in calls:
                fh.write(f"{cell}\t{chrom}\t{pos}\t{snvs[(chrom, pos)][2]}\t{a}\t{d}\n")
    with open(os.path.join(out_dir, "sc_branch_recall.tsv"), "w") as fh:
        fh.write("cell\tbranch\tn_called\tn_snv\trecall\trel_recall\n")
        for cell, calls in results:
            called = collections.Counter(snvs[(c, p)][2] for _, c, p, _, _ in calls)
            truncal = called[TRUNCAL] / branch_size[TRUNCAL]
            for b in branches:
                r = called[b] / branch_size[b]
                rel = r / truncal if truncal else float("nan")
                fh.write(f"{cell}\t{b}\t{called[b]}\t{branch_size[b]}\t{r:.4f}\t{rel:.3f}\n")
    print(f"{len(results)} cells, {len(snvs)} SNVs, {len(branches)} branches -> {out_dir}")


if __name__ == "__main__":
    main()
