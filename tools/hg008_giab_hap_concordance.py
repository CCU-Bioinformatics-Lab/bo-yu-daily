#!/usr/bin/env python3
"""Compare the haplotype of HG008 SNVs between PRCGAP (Sakamoto 2026) and the GIAB benchmark v0.4.

Both sides label haplotypes from their own assembly, so a whole chromosome can have swapped labels.
Steps: lift PRCGAP SNVs to GRCh38 with its own columns, keep the paper's reconstructable filter plus
point_mutation_other, find the same site and alleles in the GIAB tumorvariants VCF (positions +0 or
+1, either strand, as PRCGAP positions are not guaranteed to be 1-based), read GIAB's haplotype from
HG008Nv63SOMATICVARIANT, and count same-label and swapped-label SNVs per chromosome.
Agreement allows one swap per chromosome: the larger of the two counts is taken as agreeing.

Output (OUT_DIR): per_chromosome.tsv, summary.tsv
Usage: python3 -I tools/hg008_giab_hap_concordance.py PRCGAP_EXTRACTED OUT_DIR
"""
import collections
import csv
import re
import subprocess
import sys
from pathlib import Path

GIAB = "/big8_disk/yungjen114/data/HG008/NIST/somatic-smvar_v0.4_20261006/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_tumorvariants.vcf.gz"
COMPLEMENT = str.maketrans("ACGT", "TGCA")
csv.field_size_limit(10**8)


def read_giab():
    out = subprocess.run(["bcftools", "view", "-H", "-v", "snps", GIAB], capture_output=True, text=True, check=True).stdout
    sites = {}
    for line in out.splitlines():
        f = line.split("\t")
        sites[(f[0], int(f[1]), f[3], f[4])] = re.findall(r"chr\w+_hap([12])", f[7])
    return sites


def keep(r):
    return (r["misassembly"] == "False" and r["gnomAD"] in ("-", "") and float(r["Depth"]) >= 10 and float(r["VAF"]) >= .05
            and float(r["Kmer_ratio"] or 0) >= .8 and r["Haplotype"] in ("haplotype1", "haplotype2")
            and r["point_mutation_other"] == "True" and r["GRCh38_pos"].isdigit() and r["GRCh38_contig"].startswith("chr"))


def giab_hap(r, sites):
    """GIAB's haplotypes at this SNV, or None when GIAB has no such SNV."""
    pos = int(r["GRCh38_pos"])
    ref, alt = r["Ref"], r["Alt"]
    for offset in (0, 1):
        for a, b in ((ref, alt), (ref.translate(COMPLEMENT), alt.translate(COMPLEMENT))):
            hit = sites.get((r["GRCh38_contig"], pos + offset, a, b))
            if hit is not None:
                return hit
    return None


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    sites = read_giab()
    table = collections.defaultdict(collections.Counter)
    n_kept = n_found = n_ambiguous = 0
    with open(root / "HG008/point_mutation/HG008.deepsomatic.snv.annotated_checked_gnomad.txt") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if not keep(r):
                continue
            n_kept += 1
            haps = giab_hap(r, sites)
            if haps is None:
                continue
            n_found += 1
            if len(set(haps)) != 1:
                n_ambiguous += 1
                continue
            table[r["GRCh38_contig"]]["same" if r["Haplotype"][-1] == haps[0] else "swap"] += 1
    agree = total = n_swapped = 0
    with open(out / "per_chromosome.tsv", "w") as fh:
        fh.write("chrom\tsame_label\tswapped_label\tagree_after_swap\tshare\n")
        for chrom in sorted(table, key=lambda c: (len(c), c)):
            same, swap = table[chrom]["same"], table[chrom]["swap"]
            best = max(same, swap)
            agree += best
            total += same + swap
            n_swapped += swap > same
            fh.write(f"{chrom}\t{same}\t{swap}\t{best}\t{best / (same + swap):.4f}\n")
    with open(out / "summary.tsv", "w") as fh:
        fh.write("giab_snv\tprcgap_kept\tfound_in_giab\tgiab_hap_ambiguous\tcompared\tagree_after_swap\tshare\tchromosomes\tchromosomes_swapped\n")
        fh.write(f"{len(sites)}\t{n_kept}\t{n_found}\t{n_ambiguous}\t{total}\t{agree}\t{agree / total:.4f}\t{len(table)}\t{n_swapped}\n")


if __name__ == "__main__":
    main()
