#!/usr/bin/env bash
# One HCC1395 ONT subsample of the diplosim purity holdout: haplotag, ClairS HC sites, pileup,
# 200 diplosim runs with the t50_n00-calibrated knobs locked, compare.
# Usage: bash tools/diplosim_purity_holdout_one.sh NAME PURITY COVERAGE   (run from repo root)
# COVERAGE: genome-wide median depth of the subsample (52 for t10-t40, 53 for t50_n00).
set -euo pipefail
N=$1; P=$2; COV=$3
H=/big8_disk/boyu114/hcc1395_hp_split
CRAM=/big8_disk/data/HCC1395/ONT/subsample/$N/HCC1395_$N.cram
D=lab_report/2026-10-31_diplosim_purity_holdout/$N
K="--prop-pos-lost 0.45 --loss-events cnloh_B --prop-pos-second-cna 0.5 --gain-events gain_A,gain_B,gain_B,gain_both \
   --prop-truncal-snvs 0.8 --depth-dispersion 0.03 --base-error 0.01 --mistag-rate 0.005 --prop-tagged 0.862 --tag-concentration 1"
mkdir -p $D/tables
if [[ ! -s $H/tagged_$N.cram.crai ]]; then
  /bip8_disk/boyu114/longphase-s-origin/longphase-s haplotag -s $H/phased_fix.vcf.gz -b $CRAM \
    -r /big8_disk/ref/GRCh38_no_alt_analysis_set.fasta -t 32 --cram -o $H/tagged_$N > $H/haplotag_$N.log 2>&1
  samtools index -@ 32 $H/tagged_$N.cram
fi
bcftools view -H -R /big8_disk/boyu114/benchmark_data/SEQC2/release_v1.2.1/High-Confidence_Regions_v1.2.bed \
  -f PASS -v snps -m2 -M2 /big8_disk/data/HCC1395/ONT/subsample/$N/ClairS_v0_4_1/output.vcf.gz |
  awk -F'\t' 'BEGIN{OFS="\t"}{split($10,a,":"); split(a[5],ad,","); print $1,$2,$4,$5,a[3],ad[2],a[4]}' |
  sort -u -k1,1V -k2,2n > $D/tables/clairs_hc_sites.tsv
python3 -I tools/diplosim_ppc_hcc1395.py real $D $D/tables/clairs_hc_sites.tsv $H/tagged_$N.cram
echo "coverage $COV purity $P"
python3 -I tools/diplosim_ppc_hcc1395.py sim $D 200 $K --min-tumour-purity $P --max-tumour-purity $P --coverage $COV
python3 -I tools/diplosim_ppc_hcc1395.py compare $D > /dev/null
python3 tools/plot_diplosim_ppc_hcc1395.py $D
rm -rf $D/sim
echo "DONE $N"
