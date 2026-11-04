#!/usr/bin/env bash
# Truth tree vs MAP tree scores (tools/c4_truth_vs_map.py) for every C4 robustness, composite-weight
# and error-model run that still has its trace.h5. The C4 options come from the run dir name:
# run_base / run_a2: no C4; *_c4_eEPS: eps; *_c4_eEPS_wW: eps + weight; *_c4_errE: error model;
# *_c4_errE_hpu: error model with HP uncertainty.
# Usage: bash run_all.sh > scores.tsv   (from the repo root)
set -euo pipefail
SIMS=lab_report/2026-10-25_c4_robustness/sims
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"

one() {
  local sim=$1 R=$2 run opts
  run=$(basename "$R")
  case $run in
    run_base|run_a2) opts=(--c4 none) ;;
    *_c4_err*_hpu) local e=${run##*_err}
                   opts=(--c4 error --error "${e%_hpu}" --hp-uncertain) ;;
    *_c4_err*) opts=(--c4 error --error "${run##*_err}") ;;
    *_c4_e*_w*) local ew=${run##*_c4_e}
                opts=(--c4 eps --eps "${ew%_w*}" --weight "${ew##*_w}") ;;
    *_c4_e*) opts=(--c4 eps --eps "${run##*_c4_e}") ;;
    *) return 0 ;;
  esac
  $PY tools/c4_truth_vs_map.py "$SIMS/$sim" "$R" "${opts[@]}" --contract-all --opt --no-header |
    awk -v r="$R" 'BEGIN{OFS="\t"} {$2 = r; print}'
}
export -f one
export SIMS PY

echo -e "sim\trun_dir\ttree\talpha\tn_nodes\tcompat\tlog_p_one\tprior\tdata_ll\tpair_term\tminus_map\tcheck"
for T in $SIMS/*/run_*/trace.h5 lab_report/2026-10-26_c4_{composite_weight,error_model,hp_uncertain}/runs/*/run_*/trace.h5; do
  [[ -s $T ]] || continue
  R=$(dirname "$T")
  [[ -s $R/topologies.tar.gz ]] || continue      # skip runs still in progress
  echo "$(basename "$(dirname "$R")") $R"
done | xargs -P "${PAR:-8}" -L1 bash -c 'one $0 $1'
