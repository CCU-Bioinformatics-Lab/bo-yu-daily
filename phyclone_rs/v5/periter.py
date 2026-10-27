"""Split run time into a fixed cost and a per-iteration cost: run each config with -b 0 and
-n 2 or -n 202 (1 chain, seed 1), 3 reps, and fit per_iter = (t202 - t2) / 200, fixed = t2.

Usage (from the repo root): python3 phyclone_rs/v5/periter.py OUT NAME=BIN ... > periter.tsv
"""
import csv
import os
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GOLDEN = os.path.join(REPO, "phyclone_rs", "golden")
PYTHON = os.path.expanduser("~/venvs/phyclone/bin/python")
CONFIGS = ["e0_base_bin", "fscrp_assign_loss", "upstream_grid1000"]
ENV = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
           NUMBA_NUM_THREADS="1",
           PYTHONPATH=os.path.join(REPO, "research", "phyclone_research", "PhyClone"))


def main():
    out, *impls = sys.argv[1:]
    impls = [("python080", None)] + [tuple(i.split("=", 1)) for i in impls]
    with open(os.path.join(GOLDEN, "runs.tsv")) as fh:
        runs = {r["run"]: r for r in csv.DictReader(fh, delimiter="\t")}
    print("config\timpl\tfixed_s_median\tper_iter_ms_median\tper_iter_ms_min\tper_iter_ms_max")
    for c in CONFIGS:
        r = runs[c]
        argv = r["argv"].replace("{in}", os.path.join(GOLDEN, "cases", r["case"], "input")).split()
        for name, binary in impls:
            t = {2: [], 202: []}
            for rep in range(3):
                for n in (2, 202):
                    d = os.path.join(out, name, c, f"n{n}_rep{rep}")
                    os.makedirs(d, exist_ok=True)
                    args = [*argv, "-b", "0", "-n", str(n), "--num-chains", "1", "--seed", "1"]
                    cmd = ([PYTHON, "tools/phyclone_hp.py", *args, "-o", os.path.join(d, "trace.h5")]
                           if binary is None else [binary, *args, "-o", os.path.join(d, "trace")])
                    s = time.time()
                    subprocess.run(cmd, check=True, cwd=REPO, env=ENV,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    t[n].append(time.time() - s)
            per = [(b - a) / 200 * 1000 for a, b in zip(t[2], t[202])]
            print(f"{c}\t{name}\t{statistics.median(t[2]):.2f}\t{statistics.median(per):.2f}\t"
                  f"{min(per):.2f}\t{max(per):.2f}", flush=True)


if __name__ == "__main__":
    main()
