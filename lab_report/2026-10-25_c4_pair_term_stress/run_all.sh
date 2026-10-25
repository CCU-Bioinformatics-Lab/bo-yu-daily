#!/usr/bin/env bash
# C4 read co-occurrence term on the stress truth tree: density x1 / x10, data seeds 1-3,
# methods base / base+C4 / a2 / a2+C4. Each run: run + map + topology-report; trace kept local.
# Usage: bash run_all.sh   (from the repo root; sims/ must exist, see README)
set -euo pipefail
L=lab_report/2026-10-25_c4_pair_term_stress
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
one() {
  local sim=$1 m=$2 I=$L/sims/$1/input R=$L/sims/$1/run_$2
  [[ -s $R/topology_report.tsv ]] && return 0
  mkdir -p "$R"
  local emit=(--hp-mode base) data=$I/data.tsv
  [[ $m == a2* ]] && emit=(--hp-mode a2 --segments "$I/segments.tsv") && data=$I/data_hp.tsv
  local pairs=()
  [[ $m == *c4 ]] && pairs=(--pairs "$I/pairs.tsv" --hp-data "$I/data_hp.tsv" --segments "$I/segments.tsv")
  $PY tools/phyclone_hp.py "${emit[@]}" "${pairs[@]}" run -i "$data" -o "$R/trace.h5" \
    -d binomial -b 100 -n 1000 --num-chains 4 --seed 1 > "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" map -i "$R/trace.h5" -t "$R/map_tree.nwk" \
    -o "$R/map_table.tsv" >> "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" topology-report -i "$R/trace.h5" \
    -o "$R/topology_report.tsv" -t "$R/topologies.tar.gz" >> "$R/run.log" 2>&1
}
export -f one
export L PY
for s in $(ls $L/sims); do for m in base base_c4 a2 a2_c4; do echo "$s $m"; done; done |
  xargs -P 24 -L1 bash -c 'one $0 $1'
for s in $(ls $L/sims); do
  python3 tools/summarize_hp_truth_topologies.py $L/sims/$s/truth $L/sims/$s/run_{base,base_c4,a2,a2_c4}
done > $L/topology_summary.tsv
