#!/usr/bin/env bash
# HG008 (2026-11-15): A1 + C4 pair term, seeds 1, 2; everything else as 2026-11-13 (README §2).
# Usage: bash lab_report/2026-11-15_hg008_c4_rebuild/run_c4_param.sh /bip8_disk/boyu114/hg008_haploclone/c4 [EXTRA_FLAGS TAG]
#   pooled (README §2b): ... c4 --pair-pool a1c4pool
set -euo pipefail
W=$1; HC=/bip8_disk/boyu114/haploclone/rust/target/release/haploclone
C4="--pairs $W/pairs.tsv --hp-data $W/data_hp.tsv --segments $W/segments.tsv"
job() {  # $2 = extra flags, $3 = run tag
  seed=$1; extra=${2:-}; tag=${3:-a1c4}; run=$W/run_${tag}_h${seed}
  $HC --hp-mode a1 $C4 $extra run -i $W/data_hp.tsv -o $run -d binomial -b 1000 -n 3000 --num-chains 4 --seed $seed > $run.log 2>&1
  $HC --hp-mode a1 $C4 $extra map -i $run -o ${run}_map.tsv -t ${run}_map.nwk > ${run}_map.log 2>&1
  echo "done seed $seed"
}
EXTRA=${2:-}; TAG=${3:-a1c4}
for s in 1 2; do job $s "$EXTRA" "$TAG" & done
wait
