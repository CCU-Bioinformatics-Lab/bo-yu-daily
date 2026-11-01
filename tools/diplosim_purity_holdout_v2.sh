#!/usr/bin/env bash
# Purity holdout v2: every purity simulates the full 31,595 SNVs and both sides go through one
# fixed ClairS-like filter (alt >= 5, VAF >= 0.10). Real pileups are reused from v1 / 10-30.
# Usage: bash tools/diplosim_purity_holdout_v2.sh NAME PURITY COVERAGE REAL_DIR   (run from repo root)
# OUT_ROOT and KNOBS override the report directory and the locked knobs (defaults = v2).
set -euo pipefail
N=$1; P=$2; COV=$3; REAL=$4
D=${OUT_ROOT:-lab_report/2026-10-31_diplosim_purity_holdout_v2}/$N
K=${KNOBS:-"--prop-pos-lost 0.45 --loss-events cnloh_B --prop-pos-second-cna 0.5 --gain-events gain_A,gain_B,gain_B,gain_both \
   --prop-truncal-snvs 0.8 --depth-dispersion 0.03 --base-error 0.01 --mistag-rate 0.005 --prop-tagged 0.862 --tag-concentration 1"}
export DIPLOSIM_PPC_MIN_ALT=5 DIPLOSIM_PPC_MIN_VAF=0.10
mkdir -p $D/tables
cp $REAL/tables/real_per_snv.tsv $D/tables/
python3 -I tools/diplosim_ppc_hcc1395.py sim $D 200 $K --min-tumour-purity $P --max-tumour-purity $P --coverage $COV --n-snv 31595
python3 -I tools/diplosim_ppc_hcc1395.py compare $D > /dev/null
python3 tools/plot_diplosim_ppc_hcc1395.py $D
rm -rf $D/sim
echo "DONE $N"
