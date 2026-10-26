"""Run the Rust port (haploclone) on the golden reference configs, laid out for compare.py.

Writes OUT/<config>/seed<S>/ (a TSV trace directory) for every golden run in runs.tsv and
OUT/e0_base_bin.chains4/seed<S>/ for the 4-chain config, with the same argv as the Python
baseline (run_baseline.py COMMON options). Existing trace directories are skipped.

Usage (from the repo root):
  python3 phyclone_rs/v3/run_rust.py OUT [--seeds 1-10] [--bin PATH] [--jobs 16]
"""
import argparse
import csv
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GOLDEN = os.path.join(ROOT, "phyclone_rs", "golden")
BIN = "/bip8_disk/boyu114/haploclone/rust/target/release/haploclone"
COMMON = ["-b", "20", "-n", "200"]


def seeds(spec):
    lo, _, hi = spec.partition("-")
    return range(int(lo), int(hi or lo) + 1)


def jobs(out, seed_list, binary):
    with open(os.path.join(GOLDEN, "runs.tsv")) as fh:
        runs = list(csv.DictReader(fh, delimiter="\t"))
    for r in runs:
        argv = r["argv"].replace("{in}", os.path.join(GOLDEN, "cases", r["case"], "input")).split()
        configs = [(r["run"], 1)]
        if r["run"] == "e0_base_bin":
            configs.append(("e0_base_bin.chains4", 4))
        for config, chains in configs:
            for s in seed_list:
                d = os.path.join(out, config, f"seed{s}")
                cmd = [binary, *argv, *COMMON, "--num-chains", str(chains), "--seed", str(s), "-o", d]
                yield d, cmd


def run(job):
    d, cmd = job
    if os.path.exists(os.path.join(d, "iterations.tsv")):
        return d, 0, 0.0
    os.makedirs(os.path.dirname(d), exist_ok=True)
    t = time.time()
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        print(f"FAILED {d}: {p.stderr.strip()[-300:]}")
    return d, p.returncode, time.time() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seeds", default="1-10")
    ap.add_argument("--bin", default=BIN)
    ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()
    todo = list(jobs(a.out, seeds(a.seeds), a.bin))
    t = time.time()
    with ThreadPoolExecutor(a.jobs) as pool:
        results = list(pool.map(run, todo))
    bad = [d for d, rc, _ in results if rc]
    print(f"{len(results)} runs, {len(bad)} failed, {time.time() - t:.1f} s wall, "
          f"{sum(s for _, _, s in results):.1f} s summed")


if __name__ == "__main__":
    main()
