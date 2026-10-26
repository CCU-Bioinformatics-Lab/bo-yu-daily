"""Run the Python PhyClone baseline for V3: every golden reference config x seeds x variant.

Each job runs tools/phyclone_hp.py with the argv of phyclone_rs/golden/runs.tsv and the golden
common options (-b 20 -n 200 --num-chains 1), then the variant's extra args (a later option wins
in click), then --seed. drop_args removes an option and its value from the golden argv. Output: baseline/runs/<variant>/<run>/seed<NN>/{trace.h5,command.txt,
run.log,run_seconds.txt}. A job whose run_seconds.txt exists is skipped, so a rerun resumes.

Usage (from anywhere):
  ~/venvs/phyclone/bin/python phyclone_rs/v3/run_baseline.py [--jobs 40] [--variant ref ...]
"""
import argparse
import csv
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

V3 = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(V3))
GOLDEN = os.path.join(REPO, "phyclone_rs", "golden")
PHYCLONE = os.path.join(REPO, "research", "phyclone_research", "PhyClone")
PYTHON = os.path.expanduser("~/venvs/phyclone/bin/python")
COMMON = ["-b", "20", "-n", "200", "--num-chains", "1"]


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def seeds(spec):
    lo, hi = spec.split("-")
    return range(int(lo), int(hi) + 1)


def jobs(selected):
    runs = read_tsv(os.path.join(GOLDEN, "runs.tsv"))
    for v in read_tsv(os.path.join(V3, "variants.tsv")):
        if selected and v["variant"] not in selected:
            continue
        for r in runs:
            if v["runs"] != "all" and r["run"] not in v["runs"].split(","):
                continue
            argv = r["argv"].replace("{in}", os.path.join(GOLDEN, "cases", r["case"], "input")).split()
            for opt in v["drop_args"].split():  # drop an option and its value
                i = argv.index(opt)
                del argv[i:i + 2]
            for s in seeds(v["seeds"]):
                out = os.path.join(V3, "baseline", "runs", v["variant"], r["run"], f"seed{s:02d}")
                cmd = (["tools/phyclone_hp.py"] + argv + COMMON + v["extra_args"].split()
                       + ["--seed", str(s), "-o", os.path.join(out, "trace.h5")])
                chains = 4 if "--num-chains 4" in v["extra_args"] else 1
                yield out, cmd, chains


def run(job):
    out, cmd, _ = job
    if os.path.exists(os.path.join(out, "run_seconds.txt")):
        return out, None
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "command.txt"), "w") as fh:
        fh.write(" ".join(cmd) + "\n")
    env = {**os.environ, "PYTHONPATH": PHYCLONE, "OPENBLAS_NUM_THREADS": "1",
           "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        rc = subprocess.call([PYTHON] + cmd, cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    if rc != 0:
        return out, f"exit {rc}"
    with open(os.path.join(out, "run_seconds.txt"), "w") as fh:
        fh.write(f"{dt:.1f}\n")
    return out, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=40, help="parallel 1-chain runs (4-chain = 4)")
    ap.add_argument("--variant", nargs="*", default=[])
    a = ap.parse_args()
    todo = sorted(jobs(a.variant), key=lambda j: -j[2])
    # 4-chain jobs take 4 slots; run them in a smaller pool so total cores stay near --jobs
    big = [j for j in todo if j[2] > 1]
    small = [j for j in todo if j[2] == 1]
    t0 = time.time()
    with ThreadPoolExecutor(max(1, a.jobs // 4)) as pb, ThreadPoolExecutor(a.jobs - a.jobs // 4) as ps:
        futs = [pb.submit(run, j) for j in big] + [ps.submit(run, j) for j in small]
        for f in futs:
            out, res = f.result()
            print(f"{os.path.relpath(out, V3)}\t{res}", flush=True)
    print(f"wall {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
