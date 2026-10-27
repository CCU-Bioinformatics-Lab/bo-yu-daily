"""V5: time Python PhyClone 0.8.0 and haploclone (Rust) builds on the same configs, 3 reps each.

Each job runs only `run` and records its wall time. Jobs of all implementations are shuffled with a
fixed seed and packed onto at most --cores cores (a job takes one core per chain), so every
implementation sees the same background. Before each launch the script reads the 1-minute load
average; if the load from other users (load minus the cores this script holds) is above
--max-other-load, it waits, and after --load-wait seconds it stops launching.

A job counts as done only if its trace is complete: Python's trace.h5 exists; Rust's
iterations.tsv has chains x num_iters rows.

Output: OUT/<impl>/<config>/rep<r>/ (command.txt, run.log, trace) and one row per job in
OUT/timings.tsv (append-only; finished jobs are skipped on a rerun).

Usage (from the repo root):
  python3 phyclone_rs/v5/bench.py OUT --impl python080 --impl rust_f05b615=BIN ... [--reps 3]
"""
import argparse
import csv
import os
import random
import shlex
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "phyclone_rs", "v4"))
import run_v4  # noqa: E402

GOLDEN = os.path.join(REPO, "phyclone_rs", "golden")
PYTHON = os.path.expanduser("~/venvs/phyclone/bin/python")
PHYCLONE_SRC = os.path.join(REPO, "research", "phyclone_research", "PhyClone")
GOLDEN_CONFIGS = ["e0_base_bin", "b03_base_err003_hpu", "real_a2_err004", "e0_out001", "e0_out001_fully",
                  "upstream_grid1000", "fscrp_assign_loss"]
GOLDEN_ARGS = ["-b", "20", "-n", "200", "--num-chains", "1", "--seed", "1"]
V4_TRIALS = [
    ("v4_fscrp_out", "FS-CRP_Loss/data_archive/loss_prop_0.2_run2", "PhyClone"),
    ("v4_pairtree", "Pairtree/data_archive/sim_K10_S10_T1000_M1000_run1", "PhyClone"),
    ("v4_conipher", "CONIPHER_No-Noise/data_archive/LTXSIM002", "PhyClone"),
]
SINGLE_THREAD = {k: "1" for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                  "NUMBA_NUM_THREADS")}
FIELDS = ["config", "impl", "rep", "chains", "iters", "wall_s", "rc", "complete", "load1_start",
          "load1_end", "started"]


def configs():
    """(config, chains, iters, python argv, rust argv); argv excludes the program and -o."""
    with open(os.path.join(GOLDEN, "runs.tsv")) as fh:
        runs = {r["run"]: r for r in csv.DictReader(fh, delimiter="\t")}
    for name in GOLDEN_CONFIGS:
        r = runs[name]
        argv = r["argv"].replace("{in}", os.path.join(GOLDEN, "cases", r["case"], "input")).split()
        yield name, 1, 200, ["tools/phyclone_hp.py", *argv, *GOLDEN_ARGS], [*argv, *GOLDEN_ARGS]
    for name, trial, program in V4_TRIALS:
        data, clusters = run_v4.inputs({"trial": trial, "program": program})
        argv = ["run", "-i", data, "-c", clusters, *run_v4.PAPER_ARGS, *run_v4.LOSS_ARGS[program]]
        yield name, 4, 5000, ["-c", "from phyclone.cli import main; main()", *argv], argv


def command(impl, binary, py_argv, rust_argv, out):
    if impl.startswith("python"):
        return [PYTHON, *py_argv, "-o", os.path.join(out, "trace.h5")]
    return [binary, *rust_argv, "-o", os.path.join(out, "trace")]


def complete(impl, out, chains, iters):
    if impl.startswith("python"):
        return os.path.exists(os.path.join(out, "trace.h5"))
    path = os.path.join(out, "trace", "iterations.tsv")
    if not os.path.exists(path):
        return False
    with open(path) as fh:
        return sum(1 for _ in fh) - 1 == chains * iters


def load1():
    with open("/proc/loadavg") as fh:
        return float(fh.read().split()[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--impl", action="append", required=True,
                    help="python080, or NAME=BINARY for a haploclone build")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--cores", type=int, default=16)
    ap.add_argument("--max-other-load", type=float, default=60)
    ap.add_argument("--load-wait", type=float, default=1800)
    ap.add_argument("--only", action="append", help="limit to these configs")
    a = ap.parse_args()

    impls = dict(i.split("=", 1) if "=" in i else (i, None) for i in a.impl)
    table = os.path.join(a.out, "timings.tsv")
    done = set()
    if os.path.exists(table):
        with open(table) as fh:
            done = {(r["config"], r["impl"], r["rep"]) for r in csv.DictReader(fh, delimiter="\t")
                    if r["complete"] == "1"}
    else:
        os.makedirs(a.out, exist_ok=True)
        with open(table, "w") as fh:
            fh.write("\t".join(FIELDS) + "\n")

    jobs = [(c, impl, rep, chains, iters, py, rs)
            for c, chains, iters, py, rs in configs() if not a.only or c in a.only
            for impl in impls for rep in range(1, a.reps + 1)
            if (c, impl, str(rep)) not in done]
    random.Random(1).shuffle(jobs)

    lock = threading.Condition()
    state = {"used": 0, "stop": False}

    def run(job):
        c, impl, rep, chains, iters, py, rs = job
        out = os.path.join(a.out, impl, c, f"rep{rep}")
        os.makedirs(out, exist_ok=True)
        cmd = command(impl, impls[impl], py, rs, out)
        with open(os.path.join(out, "command.txt"), "w") as fh:
            fh.write(shlex.join(cmd) + "\n")
        env = dict(os.environ, **SINGLE_THREAD)
        if impl.startswith("python"):
            env["PYTHONPATH"] = PHYCLONE_SRC
        l0, started, t = load1(), time.strftime("%Y-%m-%dT%H:%M:%S"), time.time()
        with open(os.path.join(out, "run.log"), "w") as log:
            rc = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=REPO)
        wall = time.time() - t
        ok = rc == 0 and complete(impl, out, chains, iters)
        row = [c, impl, rep, chains, iters, f"{wall:.3f}", rc, int(ok), l0, load1(), started]
        with lock:
            with open(table, "a") as fh:
                fh.write("\t".join(map(str, row)) + "\n")
            print(f"{c}\t{impl}\trep{rep}\t{wall:.1f}s\trc={rc}\tcomplete={int(ok)}", flush=True)
            state["used"] -= chains
            lock.notify_all()

    threads = []
    for job in jobs:
        chains = job[3]
        with lock:
            waited = 0.0
            while True:
                if state["used"] + chains <= a.cores:
                    other = load1() - state["used"]
                    if other <= a.max_other_load:
                        break
                    if waited >= a.load_wait:
                        state["stop"] = True
                        break
                    print(f"load from others {other:.1f} > {a.max_other_load}; waiting", flush=True)
                    lock.wait(60)
                    waited += 60
                else:
                    lock.wait()
            if state["stop"]:
                print("stopping: other load stayed high", flush=True)
                break
            state["used"] += chains
        th = threading.Thread(target=run, args=(job,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()


if __name__ == "__main__":
    main()
