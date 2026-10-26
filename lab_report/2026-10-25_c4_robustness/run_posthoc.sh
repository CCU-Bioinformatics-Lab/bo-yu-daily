#!/usr/bin/env bash
# Post-hoc tree selection (tools/c4_posthoc.py) on the runs without C4: for every sim with
# run_base / run_a2, write run_<method>_ph_soft (eps 0.01) and run_<method>_ph_hard (k = 3, t = 1).
# Usage: bash run_posthoc.sh   (from the repo root, after jobs_posthoc.txt finished)
set -euo pipefail
L=lab_report/2026-10-25_c4_robustness
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
for R in $L/sims/*/run_base $L/sims/*/run_a2; do
  [[ -s $R/topologies.tar.gz ]] || continue
  echo "$(basename "$(dirname "$R")") $(basename "$R") \
$($PY tools/c4_posthoc.py "$R" "$(dirname "$R")/input" "${R}_ph" --eps 0.01 --min-reads 3 --tol 1)"
done
