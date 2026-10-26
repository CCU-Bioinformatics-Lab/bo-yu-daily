#!/usr/bin/env bash
# One row per finished run: sim, method, eps, stress-tree metrics and truth compatibility,
# over all kept roles and over segment C only (s3-s7; the only segment with eligible C4 pairs).
# Usage: bash summarize.sh > topology_summary.tsv   (from the repo root)
set -euo pipefail
L=lab_report/2026-10-25_c4_robustness
first=1
for R in $L/sims/*/run_*; do
  [[ -s $R/topology_report.tsv ]] || continue
  sim=$(basename "$(dirname "$R")") run=$(basename "$R")
  T=$L/sims/$sim/truth
  a=$(python3 tools/summarize_hp_truth_topologies.py "$T" "$R" | cut -f2-)
  b=$(python3 tools/summarize_c4_robustness.py "$T" "$R" | cut -f2-)
  c=$(python3 tools/summarize_c4_robustness.py --roles s3,s4,s5,s6,s7 "$T" "$R" | cut -f2-6 |
      sed '1s/[^\t]*/segC_&/g')
  if [[ -n $first ]]; then
    paste <(echo "sim	run") <(head -1 <<<"$a") <(head -1 <<<"$b") <(head -1 <<<"$c")
    first=
  fi
  paste <(echo "$sim	$run") <(tail -1 <<<"$a") <(tail -1 <<<"$b") <(tail -1 <<<"$c")
done
