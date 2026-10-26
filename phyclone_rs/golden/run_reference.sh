#!/usr/bin/env bash
# Freeze the original (Python) PhyClone: copy the golden inputs, then run each reference run in
# runs.tsv with a fixed seed and short settings, and keep its command, outputs, trace and time.
# Every run adds: -b 20 -n 200 --num-chains 1 --seed 1, outliers off (PhyClone default).
# Usage (from the repo root): bash phyclone_rs/golden/run_reference.sh
set -euo pipefail
G=phyclone_rs/golden
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
COMMON=(-b 20 -n 200 --num-chains 1 --seed 1)

tail -n +2 $G/cases.tsv | while IFS=$'\t' read -r case src _; do
  mkdir -p "$G/cases/$case/input"
  if [[ $case == upstream_* ]]; then
    cp "$src"/mixing_small.tsv "$src"/mixing_small_clusters.tsv "$G/cases/$case/input/"
  else
    cp "$src"/input/*.tsv "$G/cases/$case/input/"
    mkdir -p "$G/cases/$case/truth"
    cp "$src"/truth/truth.tsv "$src"/truth/truth_tree.tsv "$G/cases/$case/truth/"
  fi
done

one() {
  local run=$1 case=$2 argv=$3 R=$G/runs/$1 I=$G/cases/$2/input
  mkdir -p "$R"
  argv=${argv//\{in\}/$I}
  echo "tools/phyclone_hp.py $argv ${COMMON[*]} -o $R/trace.h5" > "$R/command.txt"
  local t0 t1
  t0=$(date +%s.%N)
  # shellcheck disable=SC2086
  $PY tools/phyclone_hp.py $argv "${COMMON[@]}" -o "$R/trace.h5" > "$R/run.log" 2>&1
  t1=$(date +%s.%N)
  echo "$t1 - $t0" | bc > "$R/run_seconds.txt"
  local cli=($PY -c "from phyclone.cli import main; main()")
  "${cli[@]}" map -i "$R/trace.h5" -t "$R/map_tree.nwk" -o "$R/map_table.tsv" \
    -s "$R/map_sample_prev.tsv" >> "$R/post.log" 2>&1
  "${cli[@]}" consensus -i "$R/trace.h5" -t "$R/consensus_tree.nwk" -o "$R/consensus_table.tsv" \
    -s "$R/consensus_sample_prev.tsv" >> "$R/post.log" 2>&1
  "${cli[@]}" topology-report -i "$R/trace.h5" -o "$R/topology_report.tsv" \
    -t "$R/topologies.tar.gz" >> "$R/post.log" 2>&1
}
export -f one
export G PY
export COMMON_STR="${COMMON[*]}"
tail -n +2 $G/runs.tsv | while IFS=$'\t' read -r run case argv; do
  printf '%s\0%s\0%s\0' "$run" "$case" "$argv"
done | xargs -0 -n 3 -P 7 bash -c 'COMMON=($COMMON_STR); one "$0" "$1" "$2"'
