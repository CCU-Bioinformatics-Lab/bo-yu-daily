"""Summarize every finished baseline run into baseline/summaries/<config>.json.gz (+ a TSV of the
scalar summaries per seed, baseline/summaries/per_seed.tsv).

<config> = <run> for variant ref, <run>.<variant> otherwise (compare.py's config names).
--configs limits the work to those configs: only their .json.gz files are written, and their rows
in per_seed.tsv are replaced while the other rows are kept as they are.
Usage: env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
         phyclone_rs/v3/summarize_baseline.py [--jobs 16]
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor

V3 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, V3)
import summaries as S  # noqa: E402

RUNS = os.path.join(V3, "baseline", "runs")
OUT = os.path.join(V3, "baseline", "summaries")


def one(args):
    variant, run, seed = args
    res, muts = S.summarize_root(os.path.join(RUNS, variant), run, [seed])
    return variant, run, seed, res[seed], muts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--configs", nargs="*")
    a = ap.parse_args()
    tasks = []
    for variant in sorted(os.listdir(RUNS)):
        for run in sorted(os.listdir(os.path.join(RUNS, variant))):
            for seed in sorted(os.listdir(os.path.join(RUNS, variant, run))):
                config = run if variant == "ref" else f"{run}.{variant}"
                if a.configs and config not in a.configs:
                    continue
                if os.path.exists(os.path.join(RUNS, variant, run, seed, "run_seconds.txt")):
                    tasks.append((variant, run, seed))
    got = {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for variant, run, seed, d, muts in ex.map(one, tasks):
            config = run if variant == "ref" else f"{run}.{variant}"
            got.setdefault(config, ({}, muts, variant, run))[0][seed] = d
    rows = []
    for config, (per_seed, muts, variant, run) in sorted(got.items()):
        secs = {s: float(open(os.path.join(RUNS, variant, run, s, "run_seconds.txt")).read())
                for s in per_seed}
        S.save(os.path.join(OUT, f"{config}.json.gz"), per_seed, muts,
               {"variant": variant, "run": run, "run_seconds": secs})
        for r in S.describe(per_seed):
            rows.append({"config": config, **r, "run_seconds": secs[r["seed"]]})
    cols = ["config", "seed", "run_seconds", "mean_nodes", "mode_nodes", "alpha_median",
            "map_log_p_one", "step_change", "post_ari", "map_ari", "post_compat", "map_compat",
            "post_c3_under_c4"]
    lines = {}  # config -> its rows, so a --configs run keeps every other row verbatim
    table = os.path.join(OUT, "per_seed.tsv")
    if a.configs and os.path.exists(table):
        for line in open(table).readlines()[1:]:
            lines.setdefault(line.split("\t", 1)[0], []).append(line)
    for c in got:
        lines[c] = []
    for r in rows:
        lines[r["config"]].append("\t".join(f"{r[c]:.6g}" if isinstance(r.get(c), float)
                                            else str(r.get(c, "")) for c in cols) + "\n")
    with open(table, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for c in sorted(lines):
            fh.writelines(lines[c])
    print(f"{len(tasks)} runs, {len(got)} configs -> {OUT}")


if __name__ == "__main__":
    main()
