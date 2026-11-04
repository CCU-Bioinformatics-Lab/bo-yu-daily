"""Neighbour counts of somatic SNVs: SEQC2 HCC1395 truth vs uniform placement vs longbulksim sims.

For each SNV, the number of other SNVs within d bp on the same chromosome (sims: same segment).
Uniform null: the same number of SNVs placed uniformly inside the SEQC2 high-confidence regions,
so region gaps affect it the same way as the truth and only clustering differs.

Usage: python3 tools/seqc2_snv_neighbors.py TRUTH.vcf.gz HC.bed SIM_ROOT OUT_DIR [--seed 1]
"""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

DISTANCES = (1_000, 5_000, 20_000, 50_000)


def read_vcf(path):
    pos = defaultdict(list)
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.split("\t", 5)
            if len(f[3]) == 1 and len(f[4]) == 1:
                pos[f[0]].append(int(f[1]))
    return {c: np.sort(np.array(p)) for c, p in pos.items()}


def read_bed(path):
    reg = defaultdict(list)
    with open(path) as fh:
        for line in fh:
            c, s, e = line.split()[:3]
            reg[c].append((int(s), int(e)))
    return reg


def uniform_in(rng, reg, n):
    chroms = [c for c in reg]
    starts = np.array([s for c in chroms for s, _ in reg[c]])
    lens = np.array([e - s for c in chroms for s, e in reg[c]])
    owner = np.array([c for c in chroms for _ in reg[c]])
    k = rng.choice(len(lens), size=n, p=lens / lens.sum())
    p = starts[k] + (rng.random(n) * lens[k]).astype(np.int64)
    return {c: np.sort(p[owner[k] == c]) for c in chroms}


def neighbours(groups):
    """Per SNV, number of others within each distance; groups = {key: sorted positions}."""
    out = {d: [] for d in DISTANCES}
    for p in groups.values():
        for d in DISTANCES:
            out[d].append(np.searchsorted(p, p + d, "right") - np.searchsorted(p, p - d, "left") - 1)
    return {d: np.concatenate(v) for d, v in out.items()}


def summary(nb):
    return {f"{d // 1000}kb": {"mean": float(v.mean()), "share_ge1": float((v >= 1).mean())}
            for d, v in nb.items()}


def sim_positions(root):
    groups = defaultdict(list)
    for t in sorted(Path(root).glob("sim_*/truth/truth.tsv")):
        with open(t) as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                groups[(t.parent.parent.name, r["segment"])].append(int(r["pos"]))
    return {k: np.sort(np.array(v)) for k, v in groups.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vcf")
    ap.add_argument("bed")
    ap.add_argument("sim_root")
    ap.add_argument("out_dir")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    truth = read_vcf(a.vcf)
    reg = read_bed(a.bed)
    n = sum(len(p) for p in truth.values())
    hc_bp = sum(e - s for r in reg.values() for s, e in r)
    sims = sim_positions(a.sim_root)
    res = {"n_truth_snv": n, "hc_bp": hc_bp, "truth_density_per_mb_in_hc": n / hc_bp * 1e6,
           "n_sim_snv": int(sum(len(p) for p in sims.values())),
           "truth": summary(neighbours(truth)),
           "uniform_in_hc": summary(neighbours(uniform_in(rng, reg, n))),
           "longbulksim": summary(neighbours(sims))}
    nb = neighbours(truth)[1_000]
    res["truth_1kb_neighbour_quantiles"] = {q: float(np.quantile(nb, q)) for q in (0.5, 0.9, 0.99, 0.999)}
    (out / "result.json").write_text(json.dumps(res, indent=1))
    print(f"truth SNVs {n}, HC {hc_bp / 1e9:.2f} Gb, density in HC {res['truth_density_per_mb_in_hc']:.1f}/Mb; "
          f"sim SNVs {res['n_sim_snv']}")
    print(f"{'':6s}" + "".join(f"{k:>34s}" for k in ("truth", "uniform_in_hc", "longbulksim")))
    for d in res["truth"]:
        print(f"{d:6s}" + "".join(f"   mean {res[k][d]['mean']:8.3f} >=1 {res[k][d]['share_ge1']:6.3f}"
                                  for k in ("truth", "uniform_in_hc", "longbulksim")))
    print("truth 1 kb neighbour quantiles", res["truth_1kb_neighbour_quantiles"])


if __name__ == "__main__":
    main()
