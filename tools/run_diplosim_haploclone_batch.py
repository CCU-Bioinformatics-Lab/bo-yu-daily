#!/usr/bin/env python3
"""Batch: several diplosim trees x haploclone base / A1 x several haploclone seeds (2026-11-12).

For each simulation seed: diplosim (defaults: SNV-only, 50% HP) -> tools/diplosim_to_haploclone.py ->
haploclone run + map for every (mode, haploclone seed) -> tools/eval_diplosim_haploclone.py.
Both modes use -d binomial (A1 only implements binomial). Runs execute in parallel.

Writes OUT_DIR/results.tsv: sim_seed, mode, hc_seed, purity, n_clones, true_clones, ari, pair_acc, ccf_mae.
Traces stay under OUT_DIR/work/ (large; not meant for the repo).

Usage: python3 tools/run_diplosim_haploclone_batch.py OUT_DIR --sim-seeds 1-10 --hc-seeds 1,2
       [--n-clones 5] [--n-snv 1000] [--burnin 1000] [--iters 3000] [--chains 4] [--jobs 24]
"""
import argparse
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_diplosim_haploclone import evaluate  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DIPLOSIM = REPO / "diplosim/target/release/diplosim"
HAPLOCLONE = Path("/bip8_disk/boyu114/haploclone/rust/target/release/haploclone")


def seeds(text):
    out = []
    for part in text.split(","):
        a, _, b = part.partition("-")
        out += range(int(a), int(b or a) + 1)
    return out


def sh(cmd, log):
    with open(log, "w") as fh:
        subprocess.run([str(c) for c in cmd], check=True, stdout=fh, stderr=subprocess.STDOUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--sim-seeds", type=seeds, required=True)
    ap.add_argument("--hc-seeds", type=seeds, required=True)
    ap.add_argument("--n-clones", type=int, default=5)
    ap.add_argument("--n-snv", type=int, default=1000)
    ap.add_argument("--burnin", type=int, default=1000)
    ap.add_argument("--iters", type=int, default=3000)
    ap.add_argument("--chains", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=24)
    a = ap.parse_args()
    work = a.out_dir / "work"
    work.mkdir(parents=True, exist_ok=True)

    for s in a.sim_seeds:
        sim, inp = work / f"sim{s}", work / f"in{s}"
        sh([DIPLOSIM, "--n-clones", a.n_clones, "--n-snv", a.n_snv, "--seed", s, "--out", sim], work / f"sim{s}.log")
        sh([sys.executable, "-I", REPO / "tools/diplosim_to_haploclone.py", sim, inp], work / f"in{s}.log")

    def job(task):
        s, mode, h = task
        inp, run = work / f"in{s}", work / f"run_s{s}_{mode}_h{h}"
        data = inp / ("data_hp.tsv" if mode == "a1" else "data.tsv")
        sh([HAPLOCLONE, "--hp-mode", mode, "run", "-i", data, "-o", run, "-d", "binomial", "-b", a.burnin,
            "-n", a.iters, "--num-chains", a.chains, "--seed", h], f"{run}.log")
        table, tree = f"{run}_map.tsv", f"{run}_map.nwk"
        sh([HAPLOCLONE, "--hp-mode", mode, "map", "-i", run, "-o", table, "-t", tree], f"{run}_map.log")
        purity = next(csv.DictReader(open(inp / "data.tsv"), delimiter="\t"))["tumour_content"]
        r = evaluate(inp, table, tree)
        print(f"done sim {s} {mode} hc {h}: pair_acc {r['pair_acc']:.3f}", flush=True)
        return {"sim_seed": s, "mode": mode, "hc_seed": h, "purity": purity, **r}

    tasks = [(s, m, h) for s in a.sim_seeds for m in ("base", "a1") for h in a.hc_seeds]
    with ThreadPoolExecutor(a.jobs) as pool:
        rows = list(pool.map(job, tasks))
    with open(a.out_dir / "results.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, rows[0].keys(), delimiter="\t")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
