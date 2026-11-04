#!/usr/bin/env bash
# base vs A1 vs A2 emission on the single-sample HP truth tree.
# data seeds x methods x MCMC seeds, all in parallel; each run: run + map + topology-report, trace deleted.
# usage: bash lab_report/2026-10-25_hp_a1a2_vs_base/run_all.sh "1 2 3" "1 2 3"
set -u
D=lab_report/2026-10-25_hp_a1a2_vs_base
DATA_SEEDS=${1:-"1 2 3"}
MCMC_SEEDS=${2:-"1 2 3"}
PY="$HOME/venvs/phyclone/bin/python"
export PYTHONPATH=research/phyclone_research/PhyClone
ph() { "$PY" -c "from phyclone.cli import main; main()" "$@"; }
one() {  # $1 data seed, $2 method, $3 mcmc seed
  local I=$D/data_s$1 R=$D/runs/data_s$1/$2_m$3
  mkdir -p "$R"
  local runner
  case $2 in
    base) runner=(ph run -i "$I/data.tsv") ;;
    a1)   runner=("$PY" tools/phyclone_hp.py --hp-mode a1 run -i "$I/data_hp.tsv") ;;
    a2)   runner=("$PY" tools/phyclone_hp.py --hp-mode a2 --segments "$I/segments.tsv" run -i "$I/data_hp.tsv") ;;
  esac
  { "${runner[@]}" -o "$R/trace.h5" -d binomial -b 100 -n 1000 --num-chains 4 --seed "$3" --print-freq 500 &&
    ph map -i "$R/trace.h5" -t "$R/map_tree.nwk" -o "$R/map_table.tsv" &&
    ph topology-report -i "$R/trace.h5" -o "$R/topology_report.tsv" -t "$R/topologies.tar.gz" &&
    rm -f "$R/trace.h5"
  } > "$R/run.log" 2>&1 || echo "FAILED $R"
}
for ds in $DATA_SEEDS; do
  python3 tools/hp_truth_tree_to_phyclone.py $D/data_s$ds --per-role 10 --depth 200 --seed $ds
  for m in base a1 a2; do
    for ms in $MCMC_SEEDS; do one $ds $m $ms & done
  done
done
wait
echo done
