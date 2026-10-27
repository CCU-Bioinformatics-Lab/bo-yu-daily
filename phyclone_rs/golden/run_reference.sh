#!/usr/bin/env bash
# Freeze the original (Python) PhyClone: copy the golden inputs, then run each reference run in
# runs.tsv with a fixed seed and short settings, and keep its command, outputs, trace and time.
# Every run adds: -b 20 -n 200 --num-chains 1 --seed 1, unless its argv sets that option itself.
# Outliers are off (PhyClone default) unless the argv turns them on.
# Usage (from the repo root): bash phyclone_rs/golden/run_reference.sh [run ...]   (default: all)
set -euo pipefail
G=phyclone_rs/golden
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
COMMON=(-b 20 -n 200 --num-chains 1 --seed 1)

tail -n +2 $G/cases.tsv | while IFS=$'\t' read -r case src _; do
  mkdir -p "$G/cases/$case/input"
  if [[ $case == upstream_* ]]; then
    cp "$src"/mixing_small.tsv "$src"/mixing_small_clusters.tsv "$G/cases/$case/input/"
  elif [[ $case == fscrp_* ]]; then
    # PhyClone paper FS-CRP_Loss trial: the phyclone_outliers inputs, the truth and the paper's
    # 0.7.0 output (for V4). results_user_loss.tsv adds an outlier_prob column for
    # --user-provided-loss-prob: 0.001 * (cluster + 1), except cluster 3 -> 0 and cluster 9 -> 0.4.
    cp "$src"/program_inputs/phyclone_outliers/{data.tsv,results.tsv.gz} "$G/cases/$case/input/"
    zcat "$src"/program_inputs/phyclone_outliers/results.tsv.gz | awk -F'\t' -v OFS='\t' '
      NR == 1 { print $0, "outlier_prob"; next }
      { k = $3; p = (k == 3) ? 0 : (k == 9) ? 0.4 : 0.001 * (k + 1); print $0, p }' \
      > "$G/cases/$case/input/results_user_loss.tsv"
    mkdir -p "$G/cases/$case/ground_truth" "$G/cases/$case/paper_output"
    cp "$src"/ground_truth/* "$G/cases/$case/ground_truth/"
    cp "$src"/program_outputs/phyclone_outliers/* "$G/cases/$case/paper_output/"
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
  local common=() i
  for ((i = 0; i < ${#COMMON[@]}; i += 2)); do  # an option in the run's argv wins over COMMON
    [[ " $argv " == *" ${COMMON[i]} "* ]] || common+=("${COMMON[i]}" "${COMMON[i + 1]}")
  done
  echo "tools/phyclone_hp.py $argv ${common[*]} -o $R/trace.h5" > "$R/command.txt"
  local t0 t1
  t0=$(date +%s.%N)
  # shellcheck disable=SC2086
  $PY tools/phyclone_hp.py $argv "${common[@]}" -o "$R/trace.h5" > "$R/run.log" 2>&1
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
selected=" $* "
tail -n +2 $G/runs.tsv | while IFS=$'\t' read -r run case argv; do
  if [[ $# -eq 0 || $selected == *" $run "* ]]; then
    printf '%s\0%s\0%s\0' "$run" "$case" "$argv"
  fi
done | xargs -0 -n 3 -P 24 bash -c 'COMMON=($COMMON_STR); one "$0" "$1" "$2"'
