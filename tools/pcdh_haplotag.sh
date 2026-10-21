#!/usr/bin/env bash
# Phase germline het SNPs around PCDH and haplotag reads in the PCDH region.
#
# usage: tools/pcdh_haplotag.sh CLAIRS_TO_SNV_VCF PHASE_CRAM OUT_DIR [TAG_CRAM:PREFIX ...]
#
#   CLAIRS_TO_SNV_VCF  ClairS-TO snv.vcf; NonSomatic sites with AF 0.2-0.8 are
#                      used as het SNPs (ClairS-TO GT is not reliable, so GT is reset to 0/1).
#   PHASE_CRAM         reads used by `longphase-s phase`.
#   TAG_CRAM:PREFIX    each CRAM is haplotagged over PCDH into OUT_DIR/PREFIX.bam
#                      (default: PHASE_CRAM:tagged).
#
# Output: OUT_DIR/het.vcf, OUT_DIR/phased.vcf, OUT_DIR/<prefix>.bam(.bai)
# First used in lab_report/2026-10-20_h1437_pcdh_hp_entropy/.
set -euo pipefail

LP=${LONGPHASE_S:-/bip8_disk/boyu114/longphase-s-origin/longphase-s}
REF=/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta
PCDH=chr5:140780000-141520000
FLANK_START=139500000   # flanks help phasing connect into one PS block
FLANK_END=142800000
THREADS=${THREADS:-16}

vcf=$1; phase_cram=$2; out=$3; shift 3
targets=("$@")
[ ${#targets[@]} -eq 0 ] && targets=("$phase_cram:tagged")
mkdir -p "$out"

awk -v s=$FLANK_START -v e=$FLANK_END 'BEGIN{OFS="\t"} /^#/{print; next}
  $1=="chr5" && $2>=s && $2<=e && $7=="NonSomatic" {
    split($10,a,":"); if (a[4]>=0.2 && a[4]<=0.8) { sub(/^[^:]*/,"0/1",$10); $7="PASS"; print } }' \
  "$vcf" > "$out/het.vcf"

"$LP" phase -s "$out/het.vcf" -b "$phase_cram" -r "$REF" --ont -t "$THREADS" \
  -o "$out/phased" > "$out/phase.log" 2>&1

for t in "${targets[@]}"; do
  cram=${t%%:*}; prefix=${t##*:}
  "$LP" haplotag -s "$out/phased.vcf" -b "$cram" -r "$REF" -q 20 -t "$THREADS" \
    --region "$PCDH" -o "$out/$prefix" > "$out/$prefix.haplotag.log" 2>&1
  samtools index "$out/$prefix.bam"
done
