#!/usr/bin/env bash
# C4 robustness: stress truth tree, longbulksim v0.2 observation errors, PhyClone +/- C4.
# A job is "SIM METHOD EPS": SIM = <density>_<condition>_s<seed>,
# METHOD = base | a2 (no C4; EPS is "-", run dir run_METHOD) | base_c4 | a2_c4 (run_METHOD_eEPS).
# Usage: bash run_all.sh JOBS.txt   (from the repo root; one job per line; SIM_ONLY=1 stops
#        after simulating)
# Each run: simulate (if missing) + run + map + topology-report; trace kept local.
set -euo pipefail
L=lab_report/2026-10-25_c4_robustness
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"

# condition -> longbulksim error options
declare -A ERR=(
  [e0]=""
  [m01]="--mistag 0.01" [m025]="--mistag 0.025" [m05]="--mistag 0.05"
  [b01]="--base-error 0.01" [b03]="--base-error 0.03"
  [sw1]="--switch-rate 1" [sw5]="--switch-rate 5"
  # real: mistag = HCC1395 split-HP proxy; switch ~ 0.15% per het SNP x ~600 het SNPs/Mb;
  # base error = calibration/normal_snv_base_error.tsv (ref read as the alt, pooled)
  [real]="--mistag 0.025 --switch-rate 1 --base-error 0.004"
)

sim() {
  local name=$1 dens=${1%%_*} seed=${1##*_s} rest cond
  rest=${1#*_}
  cond=${rest%_s*}  # a separate line: `local` expands every word before it assigns any
  [[ -n ${ERR[$cond]+set} ]] || { echo "unknown condition $cond" >&2; return 1; }
  [[ -s $L/sims/$name/input/pairs.tsv ]] && return 0
  env PYTHONPATH=longbulksim python3 -m longbulksim "$L/specs/stress_$dens.yaml" "$L/sims/$name" \
    --seed "$seed" ${ERR[$cond]} > /dev/null
}

one() {
  local s=$1 m=$2 eps=$3 I=$L/sims/$1/input R=$L/sims/$1/run_$2_e$3
  [[ $m == *_c4 ]] || R=$L/sims/$1/run_$2
  [[ -s $R/topology_report.tsv ]] && return 0
  mkdir -p "$R"
  local emit=(--hp-mode base) data=$I/data.tsv pairs=()
  [[ $m == a2* ]] && emit=(--hp-mode a2 --segments "$I/segments.tsv") && data=$I/data_hp.tsv
  [[ $m == *_c4 ]] && pairs=(--pairs "$I/pairs.tsv" --hp-data "$I/data_hp.tsv" \
    --segments "$I/segments.tsv" --pair-eps "$eps")
  $PY tools/phyclone_hp.py "${emit[@]}" "${pairs[@]}" run -i "$data" -o "$R/trace.h5" \
    -d binomial -b 100 -n 1000 --num-chains 4 --seed 1 > "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" map -i "$R/trace.h5" -t "$R/map_tree.nwk" \
    -o "$R/map_table.tsv" >> "$R/run.log" 2>&1
  $PY -c "from phyclone.cli import main; main()" topology-report -i "$R/trace.h5" \
    -o "$R/topology_report.tsv" -t "$R/topologies.tar.gz" >> "$R/run.log" 2>&1
}

jobs=$1
for s in $(cut -d' ' -f1 "$jobs" | sort -u); do sim "$s"; done
[[ -n ${SIM_ONLY:-} ]] && exit 0
export -f one
export L PY
xargs -P 24 -L1 bash -c 'one $0 $1 $2' < "$jobs"
