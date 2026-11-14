#!/usr/bin/env bash
# HG008 (2026-11-13): haploclone base and A1 x seeds 1, 2 on the build_input.py output; same settings as the simulation route.
# Usage: bash lab_report/2026-11-13_hg008_bulk_rebuild/run_haploclone.sh /bip8_disk/boyu114/hg008_haploclone
set -euo pipefail
W=$1; HC=/bip8_disk/boyu114/haploclone/rust/target/release/haploclone
job() {
  mode=$1; seed=$2; data=$W/input/data.tsv; [ "$mode" = a1 ] && data=$W/input/data_hp.tsv
  run=$W/run_${mode}_h${seed}
  $HC --hp-mode $mode run -i $data -o $run -d binomial -b 1000 -n 3000 --num-chains 4 --seed $seed > $run.log 2>&1
  $HC --hp-mode $mode map -i $run -o ${run}_map.tsv -t ${run}_map.nwk > ${run}_map.log 2>&1
  echo "done $mode seed $seed"
}
for m in base a1; do for s in 1 2; do job $m $s & done; done
wait
