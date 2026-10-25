#!/usr/bin/env bash
# PhyClone baseline on longbulksim random trees: one bulk sample, true purity, no HP features.
# Usage: bash run_all.sh [N_SPECS] [PARALLEL]   (run from the repo root)
set -euo pipefail
N=${1:-40}
P=${2:-25}
D=lab_report/2026-10-25_random_tree_phyclone_baseline
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"

(cd longbulksim && python3 -m longbulksim.random_tree ../$D/specs --count "$N" --seed 2026 --depth 50)
for f in $D/specs/spec_*.yaml; do
  s=$(basename "$f" .yaml)
  [[ -s $D/sims/$s/input/data.tsv ]] || \
    (cd longbulksim && python3 -m longbulksim "../$f" "../$D/sims/$s" --seed 1 > /dev/null)
done

run_one() {
  local s=$1 R=$D/sims/$1/run
  [[ -s $R/map_table.tsv ]] && return 0
  mkdir -p "$R"
  local t0=$SECONDS
  $PY -c "from phyclone.cli import main; main()" run -i "$D/sims/$s/input/data.tsv" \
    -o "$R/trace.h5" -d binomial -b 100 -n 1000 --num-chains 4 --seed 1 > "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" map -i "$R/trace.h5" \
    -t "$R/map_tree.nwk" -o "$R/map_table.tsv" >> "$R/run.log" 2>&1
  echo $((SECONDS - t0)) > "$R/seconds"
}
export -f run_one
export D PY
ls $D/specs | sed 's/.yaml$//' | xargs -P "$P" -I{} bash -c 'run_one {}'
python3 tools/eval_random_tree_phyclone.py $D/sims $D/per_sim.tsv
