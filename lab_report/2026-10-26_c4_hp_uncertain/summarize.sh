#!/usr/bin/env bash
# One row per finished run, same columns as lab_report/2026-10-25_c4_robustness/summarize.sh, plus
# the eps-model reference rows (run_base_c4_e0.01, run_a2_c4_e0.01) of the same sims.
# Usage: bash summarize.sh > topology_summary.tsv   (from the repo root)
set -euo pipefail
L=lab_report/2026-10-26_c4_hp_uncertain
SIMS=lab_report/2026-10-25_c4_robustness/sims
first=1
row() {
  local sim=$1 run=$2 R=$3 T=$SIMS/$1/truth a b c
  a=$(python3 tools/summarize_hp_truth_topologies.py "$T" "$R" | cut -f2-)
  b=$(python3 tools/summarize_c4_robustness.py "$T" "$R" | cut -f2-)
  c=$(python3 tools/summarize_c4_robustness.py --roles s3,s4,s5,s6,s7 "$T" "$R" | cut -f2-6 |
      sed '1s/[^\t]*/segC_&/g')
  if [[ -n $first ]]; then
    paste <(echo "sim	run") <(head -1 <<<"$a") <(head -1 <<<"$b") <(head -1 <<<"$c")
    first=
  fi
  paste <(echo "$sim	$run") <(tail -1 <<<"$a") <(tail -1 <<<"$b") <(tail -1 <<<"$c")
}
for D in $L/runs/*; do
  sim=$(basename "$D")
  for m in base_c4 a2_c4; do
    R=$SIMS/$sim/run_${m}_e0.01
    [[ -s $R/topology_report.tsv ]] && row "$sim" "run_${m}_e0.01" "$R"
  done
  for R in $D/run_*; do
    [[ -s $R/topologies.tar.gz ]] && row "$sim" "$(basename "$R")" "$R"
  done
done
