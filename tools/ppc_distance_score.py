#!/usr/bin/env python3
"""Score diplosim PPC runs by distance instead of in/out counts.

z   = (real - sim mean) / sim SD over the 200 seeds (SD floored at 1e-3 of |real|, or 1e-6)
rel = (sim median - real) / |real|
Usage: python3 -I tools/ppc_distance_score.py LABEL=OUT_DIR ...
"""
import json
import statistics
import sys

STATS = ["depth_VMR", "VAF_q10", "VAF_q50", "VAF_q90", "VAF_frac_gt_0.6",
         "HP0_frac_pooled", "tag_frac_SD_sites", "tag_frac_lt_0.5_sites", "split_alt_frac",
         "inHP_VAF_q50", "minorHP_depth_q50", "minorHP_depth_lt_0.1", "alt_on_minorHP"]
CN = ["depth_VMR", "VAF_q10", "VAF_q50", "VAF_frac_gt_0.6", "minorHP_depth_lt_0.1", "alt_on_minorHP"]


def score(out):
    real = json.load(open(f"{out}/tables/real_stats.json"))
    sims = json.load(open(f"{out}/tables/sim_stats.json"))
    res = {}
    for k in STATS:
        v = [s[k] for s in sims]
        sd = max(statistics.pstdev(v), 1e-3 * abs(real[k]), 1e-6)
        res[k] = ((real[k] - statistics.fmean(v)) / sd, (statistics.median(v) - real[k]) / abs(real[k]))
    return res


if __name__ == "__main__":
    runs = [a.split("=", 1) for a in sys.argv[1:]]
    scores = {lab: score(out) for lab, out in runs}
    print("statistic\t" + "\t".join(f"{lab}_z\t{lab}_rel" for lab, _ in runs))
    for k in STATS:
        print(k + "\t" + "\t".join(f"{scores[lab][k][0]:.1f}\t{scores[lab][k][1]:+.3f}" for lab, _ in runs))
    for name, keys in (("CN6", CN), ("all13", STATS)):
        print(f"median|z| {name}\t" + "\t".join(f"{statistics.median(abs(scores[l][k][0]) for k in keys):.1f}\t" for l, _ in runs))
        print(f"mean|rel| {name}\t" + "\t".join(f"\t{statistics.fmean(abs(scores[l][k][1]) for k in keys):.3f}" for l, _ in runs))
