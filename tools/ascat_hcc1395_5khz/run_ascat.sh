#!/usr/bin/env bash
# Run ASCAT on HCC1395 ONT 5kHz tumour/normal. Output: WORK_DIR/{segments, purity_ploidy.txt, plots, run.log}.
# Reference files (ASCAT hg38 WGS set, zenodo 14008443) must be unzipped in WORK_DIR/ref.
# Usage: bash tools/ascat_hcc1395_5khz/run_ascat.sh [WORK_DIR] [NTHREADS]
set -euo pipefail
W=${1:-/big8_disk/boyu114/hcc1395_ascat_5khz}
T=${2:-23}
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$W"
Rscript "$HERE/run_ascat.R" "$W" "$T" > run.log 2>&1
echo "exit=$?" >> run.log
