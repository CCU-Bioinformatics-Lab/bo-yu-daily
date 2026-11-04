#!/usr/bin/env bash
# Run PhyClone on input/data.tsv for several seeds and both outlier modes, then map + topology-report.
# usage: bash lab_report/2026-10-24_hp_truth_tree_phyclone/run_seeds.sh SEED...
#   env IN=<input dir> OUT=<run root>: put every seed under OUT/{no_outlier,outlier05}_s<seed>
#   (default: the single-sample layout, seed 1 in run_*/, others in seeds/)
#   env KEEP_TRACE=1 keeps trace.h5 (default: delete it after map + topology-report)
set -u
D=lab_report/2026-10-24_hp_truth_tree_phyclone
IN=${IN:-$D/input}
OUT=${OUT:-}
KEEP_TRACE=${KEEP_TRACE:-0}
ph() { env PYTHONPATH=research/phyclone_research/PhyClone "$HOME/venvs/phyclone/bin/python" -c "from phyclone.cli import main; main()" "$@"; }
one() {  # $1 = run dir, $2 = seed, rest = extra run args
  local R=$1 S=$2; shift 2
  mkdir -p "$R"
  local L="$R/run.log"; [ -f "$R/trace.h5" ] && L="$R/post.log"  # keep the original run log
  { { [ -f "$R/trace.h5" ] || ph run -i $IN/data.tsv -o "$R/trace.h5" -d binomial -b 100 -n 1000 --num-chains 4 --seed "$S" --print-freq 500 "$@"; } &&
    ph map -i "$R/trace.h5" -t "$R/map_tree.nwk" -o "$R/map_table.tsv" &&
    ph topology-report -i "$R/trace.h5" -o "$R/topology_report.tsv" -t "$R/topologies.tar.gz" &&
    { [ "$KEEP_TRACE" = 1 ] || rm -f "$R/trace.h5"; }
  } > "$L" 2>&1 || echo "FAILED $R"
}
for s in "$@"; do
  if [ -n "$OUT" ]; then a=$OUT/no_outlier_s$s; b=$OUT/outlier05_s$s
  elif [ "$s" = 1 ]; then a=$D/run_no_outlier; b=$D/run_outlier05; else a=$D/seeds/no_outlier_s$s; b=$D/seeds/outlier05_s$s; fi
  one "$a" "$s" &
  one "$b" "$s" -l 0.05 &
done
wait
echo done
