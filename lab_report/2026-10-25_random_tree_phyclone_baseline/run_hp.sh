#!/usr/bin/env bash
# A1 / A2 HP-aware emission (tools/phyclone_hp.py) on the same simulations as run_all.sh.
# A2 reads segments.tsv, whose phi is the true value, so A2 is a "phi known" upper bound.
# Usage: bash run_hp.sh [PARALLEL]   (run from the repo root, after run_all.sh)
set -euo pipefail
P=${1:-25}
D=lab_report/2026-10-25_random_tree_phyclone_baseline
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"

run_one() {
  local s=$1 m=$2 I=$D/sims/$1/input R=$D/sims/$1/run_$2
  [[ -s $R/map_table.tsv ]] && return 0
  mkdir -p "$R"
  local seg=()
  [[ $m == a2 ]] && seg=(--segments "$I/segments.tsv")
  local t0=$SECONDS
  $PY tools/phyclone_hp.py --hp-mode "$m" "${seg[@]}" run -i "$I/data_hp.tsv" \
    -o "$R/trace.h5" -d binomial -b 100 -n 1000 --num-chains 4 --seed 1 > "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" map -i "$R/trace.h5" \
    -t "$R/map_tree.nwk" -o "$R/map_table.tsv" >> "$R/run.log" 2>&1
  echo $((SECONDS - t0)) > "$R/seconds"
}
export -f run_one
export D PY
for m in a1 a2; do ls $D/sims | sed "s/$/ $m/"; done | xargs -P "$P" -L1 bash -c 'run_one $0 $1'
for m in a1 a2; do
  python3 tools/eval_random_tree_phyclone.py $D/sims $D/per_sim_$m.tsv run_$m
done
