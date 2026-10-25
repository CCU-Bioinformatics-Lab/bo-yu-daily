#!/usr/bin/env bash
# Phase SEQC2 HCC1395BL germline het SNPs on the ONT normal, then haplotag the ONT t50_n00 tumour.
# Output feeds tools/hcc1395_hp_split.py.
#
# longphase-s haplotag needs two VCF fixes, or it aborts with "stoi":
#   - every ##contig line needs length=;
#   - unphased records (PS ".") and IDs with "|" are dropped / cleared.
#
# Usage: bash tools/hcc1395_hp_split_prepare.sh [WORK_DIR]
set -euo pipefail

W=${1:-/big8_disk/boyu114/hcc1395_hp_split}
L=/bip8_disk/boyu114/longphase-s-origin/longphase-s
REF=/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta
GERM=/big8_disk/boyu114/benchmark_data/SEQC2/release_v1.0/HCC1395BL_highConfident_germline_variants.txt.gz
NORMAL=/big8_disk/data/HCC1395/ONT/HCC1395BL.cram
TUMOR=/big8_disk/data/HCC1395/ONT/subsample/t50_n00/HCC1395_t50_n00.cram
T=32
mkdir -p "$W"
cd "$W"

contigs() {  # ##contig lines with length, chr1-22 and chrX
  awk '$1 ~ /^chr([0-9]+|X)$/ {print "##contig=<ID=" $1 ",length=" $2 ">"}' "$REF.fai"
}

# 1. germline het SNPs (SNV only, chr1-22/X), sorted
if [[ ! -s germline_het_snp.vcf.gz ]]; then
  {
    zcat "$GERM" | grep '^##' | grep -v '^##contig'
    contigs
    zcat "$GERM" | grep '^#CHROM'
    zcat "$GERM" | grep -v '^#' |
      awk -F'\t' 'BEGIN{OFS="\t"} length($4)==1 && length($5)==1 && ($10=="0/1"||$10=="1/0") &&
                  $1 ~ /^chr([0-9]+|X)$/ {$3="."; $10="0/1"; print}' |
      sort -k1,1V -k2,2n
  } | bgzip > germline_het_snp.vcf.gz
  tabix -f -p vcf germline_het_snp.vcf.gz
fi

# 2. phase on the normal only (tumour LOH would distort phasing)
if [[ ! -s phased_fix.vcf.gz ]]; then
  "$L" phase -s germline_het_snp.vcf.gz -b "$NORMAL" -r "$REF" --ont -t $T -o phased
  {
    grep '^##' phased.vcf | grep -v '^##contig'
    contigs
    grep '^#CHROM' phased.vcf
    grep -v '^#' phased.vcf | awk -F'\t' 'BEGIN{OFS="\t"} $10 ~ /\|/ {$3="."; print}'
  } | bgzip > phased_fix.vcf.gz
  tabix -f -p vcf phased_fix.vcf.gz
fi

# 3. haplotag the pure-tumour subsample
if [[ ! -s tagged_t50_n00.cram ]]; then
  "$L" haplotag -s phased_fix.vcf.gz -b "$TUMOR" -r "$REF" -t $T --cram -o tagged_t50_n00
  samtools index -@ $T tagged_t50_n00.cram
fi
echo "done: $W"
