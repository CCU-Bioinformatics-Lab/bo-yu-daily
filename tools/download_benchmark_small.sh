#!/usr/bin/env bash
# 下載 truth_evidence_2026-10-25 列出的小檔基準（VCF／BED／CN 表，不含 BAM/CRAM/assembly）。
# 清單來源：research/simulation_pipeline_research/truth_evidence_2026-10-25/0{1,2,3}_*.md
# 用法：bash tools/download_benchmark_small.sh [OUT_ROOT]
set -uo pipefail

OUT=${1:-/big8_disk/boyu114/benchmark_data}
GIAB=https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab
SEQC=https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/seqc/Somatic_Mutation_WG
ONT=s3://ont-open-data/giab_2025.01/analysis/wf-human-variation/sup/HG002/PAW70337/output
ZEN=https://zenodo.org/api/records
FAILED=()

# get URL DEST_DIR [NAME]
get() {
  local url=$1 dir=$2 name=${3:-$(basename "$1")}
  mkdir -p "$dir"
  [[ -s $dir/$name ]] && return 0
  wget -q --tries=3 -O "$dir/$name.part" "$url" && mv "$dir/$name.part" "$dir/$name" \
    || { rm -f "$dir/$name.part"; FAILED+=("$url"); }
}

# mirror URL_DIR DEST_DIR CUT_DIRS [REJECT]：遞迴抓一個 HTTP 目錄
mirror() {
  local url=$1 dir=$2 cut=$3 reject=${4:-}
  mkdir -p "$dir"
  wget -q -r -np -nH --cut-dirs="$cut" -N -e robots=off -R "index.html*,*.bam,*.bai,*.cram,*.fa,*.fasta*${reject:+,$reject}" \
    -P "$dir" "$url" || FAILED+=("$url")
  find "$dir" -name 'index.html*' -delete
}

# ---------- T2T-Q100 / GIAB v5.0q（HG002）----------
Q=$OUT/T2T_Q100
V5=$GIAB/release/AshkenazimTrio/HG002_NA24385_son/v5.0q
for f in NIST_HG002_v5.0q_variant-benchmarksets_README.md checksum.md5; do get "$V5/$f" "$Q/GIAB_v5.0q"; done
for t in smvar stvar; do
  for s in vcf.gz vcf.gz.tbi benchmark.bed exclusion_stats.txt; do
    get "$V5/HG002_GRCh38_v5.0q_$t.$s" "$Q/GIAB_v5.0q/GRCh38"
  done
done
for s in dip.vcf.gz dip.vcf.gz.tbi dip.bed; do
  get "$V5/dipcall_output/GRCh38_HG2-T2TQ100-V1.1_dipcall-z2k.$s" "$Q/GIAB_v5.0q/dipcall_GRCh38"
done
for f in SAMPLE.wf_snp.vcf.gz SAMPLE.wf_snp.vcf.gz.tbi SAMPLE.wf_snp.haploblocks.gtf \
         SAMPLE.mosdepth.summary.txt SAMPLE.flagstat.tsv SAMPLE.stats.json SAMPLE.wf_cnv.vcf.gz SAMPLE.wf_cnv.vcf.gz.tbi; do
  d=$Q/ONT_giab_2025.01/sup/PAW70337; mkdir -p "$d"
  [[ -s $d/$f ]] || aws s3 cp --quiet --no-sign-request "$ONT/$f" "$d/$f" || FAILED+=("$ONT/$f")
done

# ---------- GIAB HG008 somatic、mosaic、stratifications ----------
G=$OUT/GIAB
SM=$GIAB/data_somatic/HG008/Liss_lab/analysis/NIST_HG008-T_somatic-smvar_DraftBenchmark_V0.4-20261006
SV=$GIAB/data_somatic/HG008/Liss_lab/analysis/NIST_HG008-T_somatic-stvar-CNV_DraftBenchmark_V0.6-20261006
for f in README.md checksums.md5; do get "$SM/$f" "$G/HG008/smvar_V0.4"; get "$SV/$f" "$G/HG008/stvar-CNV_V0.6"; done
mirror "$SM/GRCh38/"     "$G/HG008/smvar_V0.4/GRCh38"      8 "*nogermlinewithin50bp.bed"
mirror "$SM/HG008Nv6.3/" "$G/HG008/smvar_V0.4/HG008Nv6.3"  8 "*nogermlinewithin50bp.bed"
mirror "$SV/GRCh38/"     "$G/HG008/stvar-CNV_V0.6/GRCh38"  8
mirror "$SV/HG008Nv6.3/" "$G/HG008/stvar-CNV_V0.6/HG008Nv6.3" 8

MO=$GIAB/release/AshkenazimTrio/HG002_NA24385_son/mosaic_v1.10/GRCh38/SNV
for f in README.md checksum.md5 HG002_GRCh38_MosaicSNVv1.1.bed HG002_GRCh38_MosaicSNVv1.1.vcf.gz HG002_GRCh38_MosaicSNVv1.1.vcf.gz.tbi; do
  get "$MO/$f" "$G/HG002/mosaic_v1.1"
done

ST=$GIAB/release/genome-stratifications/v3.6/GRCh38@all
for f in GRCh38-README.md GRCh38-all-stratifications.tsv GRCh38-genome-stratifications-md5s.txt; do get "$ST/$f" "$G/stratifications_v3.6/GRCh38"; done
for sub in Union Mappability SegmentalDuplications; do
  mirror "$ST/$sub/" "$G/stratifications_v3.6/GRCh38/$sub" 7
done

# ---------- SEQC2 HCC1395 ----------
S=$OUT/SEQC2
for f in high-confidence_sSNV_in_HC_regions_v1.2.1.vcf.gz high-confidence_sINDEL_in_HC_regions_v1.2.1.vcf.gz \
         High-Confidence_Regions_v1.2.bed README.md; do
  get "$SEQC/release/latest/$f" "$S/release_v1.2.1"
done
get "$SEQC/release/v1.0/HCC1395BL_highConfident_germline_variants.txt.gz" "$S/release_v1.0"
get "$SEQC/analysis/CNVs/SEQC_CNV_raw_data.zip" "$S/CNV"
get "$SEQC/analysis/CNVs/orthogonal_technologies/affy_array/HCC1395.segments.txt" "$S/CNV/affy_array"
for set in SPP WGS; do
  for tool in hatchet facets ascat dragen; do
    mirror "$SEQC/analysis/CNVs/$set/$tool/" "$S/CNV/$set/$tool" 7
  done
done

# ---------- COLO829（Valle-Inclan 2022, Zenodo 3988185）----------
C=$OUT/COLO829/zenodo_3988185
for f in truthset_somaticSVs_COLO829.vcf COLO829_somaticSV_copynumber.zip COLO829_somaticSV_rawSVcalling.zip; do
  get "$ZEN/3988185/files/$f/content" "$C" "$f"
done

# ---------- CASTLE / Wakhan（Zenodo 21611881）----------
W=$OUT/CASTLE/wakhan_zenodo_21611881
for f in tools_cmd.tar.gz timing_scripts.tar.gz cna_profiles_visualization_castle.tar.gz benchmarking.tar.gz; do
  get "$ZEN/21611881/files/$f/content" "$W" "$f"
done

echo "done: $(du -sh "$OUT" | cut -f1) in $OUT"
if ((${#FAILED[@]})); then printf 'FAILED: %s\n' "${FAILED[@]}"; exit 1; fi
