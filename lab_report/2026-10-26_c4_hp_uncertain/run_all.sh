#!/usr/bin/env bash
# C4 error model with HP uncertainty: the C4 robustness sims (not regenerated), PhyClone + C4
# with --pair-error ERR --pair-hp-uncertain. A job is "SIM METHOD ERR", METHOD = base_c4 | a2_c4.
# Run dir: runs/SIM/run_METHOD_errERR_hpu. Without HP uncertainty: lab_report/2026-10-26_c4_error_model.
# Usage: bash run_all.sh JOBS.txt   (from the repo root; one job per line)
set -euo pipefail
L=lab_report/2026-10-26_c4_hp_uncertain
SIMS=lab_report/2026-10-25_c4_robustness/sims
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"

one() {
  local s=$1 m=$2 err=$3 I=$SIMS/$1/input R=$L/runs/$1/run_$2_err$3_hpu
  [[ -s $R/topologies.tar.gz ]] && return 0
  mkdir -p "$R"
  local emit=(--hp-mode base) data=$I/data.tsv
  [[ $m == a2* ]] && emit=(--hp-mode a2 --segments "$I/segments.tsv") && data=$I/data_hp.tsv
  $PY tools/phyclone_hp.py "${emit[@]}" --pairs "$I/pairs.tsv" --hp-data "$I/data_hp.tsv" \
    --segments "$I/segments.tsv" --pair-error "$err" --pair-hp-uncertain \
    run -i "$data" -o "$R/trace.h5" -d binomial -b 100 -n 1000 --num-chains 4 --seed 1 \
    > "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" map -i "$R/trace.h5" -t "$R/map_tree.nwk" \
    -o "$R/map_table.tsv" >> "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" topology-report -i "$R/trace.h5" \
    -o "$R/topology_report.tsv" -t "$R/topologies.tar.gz" >> "$R/run.log" 2>&1
}

export -f one
export L SIMS PY
xargs -P "${PAR:-24}" -L1 bash -c 'one $0 $1 $2' < "$1"
