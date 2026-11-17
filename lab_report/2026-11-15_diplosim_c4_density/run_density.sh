#!/bin/bash
# SNV density sweep (README §1). Run from main_work.
set -e
cd /bip8_disk/boyu114/main_work
for d in 20 50 100 200; do
  python3 -I tools/run_diplosim_haploclone_batch.py /bip8_disk/boyu114/diplosim_c4_2026-11-15/d$d \
    --sim-seeds 1-10 --hc-seeds 1,2 --coverage 60 --purity 0.9 --read-length 33000 --snvs-per-mb $d \
    --modes a1,a1c4pool --jobs 24
done
