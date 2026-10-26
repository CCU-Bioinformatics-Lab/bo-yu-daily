"""Calibrate compare.py's rule on Python itself, and check its power on broken samplers.

False fail: for each config, split the 15 Python ref seeds into 10 reference + 5 candidate in all
C(15, 5) = 3003 ways and apply the rule to every split (same exact permutation test as
compare.py). Per cell the FAIL rate is <= ALPHA_FAIL by construction; what this measures is
the rate of at least one FAIL (or INCONCLUSIVE) per config and per whole table, where the
summaries are correlated. Table level uses the same seed split in every config.

Power: Python ref seeds 1-10 vs 5 seeds of a broken sampler:
  np20        --num-particles 20 (weaker PG sampler, same model)
  alphafixed  --no-concentration-update (alpha stays 1.0: a wrong prior/alpha move)
  noc4        the C4 pair term left out (C4 configs only: a model term the port forgot)
  permuted    Python ref seeds 11-15 with mutation labels shuffled in every tree (wrong
              assignment bookkeeping; num_nodes, alpha, log_p_one are untouched)

Writes baseline/calibration/{false_fail.tsv,false_fail_by_config.tsv,
false_fail_table_count.tsv,power.tsv}.
Usage: env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
         phyclone_rs/v3/calibrate.py
"""
import os
import shutil
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np

V3 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, V3)
import compare as C  # noqa: E402
import summaries as S  # noqa: E402
from trace_io import read_trace, write_tsv_dir  # noqa: E402

SUM = os.path.join(V3, "baseline", "summaries")
RUNS = os.path.join(V3, "baseline", "runs")
OUT = os.path.join(V3, "baseline", "calibration")
REF_SEEDS = [f"seed{s:02d}" for s in range(1, 11)]
HOLD_SEEDS = [f"seed{s:02d}" for s in range(11, 16)]


def permuted_one(args):
    run, seed = args
    tr = read_trace(os.path.join(RUNS, "ref", run, seed, "trace.h5"))
    tmp = tempfile.mkdtemp()
    try:  # through the TSV writer + reader, the path a Rust trace takes
        write_tsv_dir(tr, os.path.join(tmp, seed), permute_seed=int(seed[4:]))
        trp = read_trace(os.path.join(tmp, seed))
        return run, seed, S.run_summaries(trp, S.truth_for(run)), trp.mutations
    finally:
        shutil.rmtree(tmp)


def permuted(runs):
    path = {r: os.path.join(SUM, f"{r}.permuted.json.gz") for r in runs}
    todo = [(r, s) for r in runs if not os.path.exists(path[r]) for s in HOLD_SEEDS]
    got = {}
    with ProcessPoolExecutor(16) as ex:
        for run, seed, d, muts in ex.map(permuted_one, todo):
            got.setdefault(run, ({}, muts))[0][seed] = d
    for run, (per_seed, muts) in got.items():
        S.save(path[run], per_seed, muts, {"variant": "permuted", "run": run,
                                           "source_seeds": HOLD_SEEDS})
    return {r: S.load(path[r])[0] for r in runs}


def all_split_verdicts(X, kind):
    """Verdict of every 10-vs-5 split of the pooled 15 runs X (rows ordered by seed)."""
    n, m = len(X), 5
    M, exact, total = C.split_masks(n, m, n_perm=10 ** 9)
    T = C.split_stats(X, M, kind)
    order = np.sort(T)
    # p of split s = fraction of splits with T >= T_s (exact enumeration, as compare.py)
    p = 1.0 - np.searchsorted(order, T - C.TIE * np.maximum(1.0, np.abs(T)), side="left") / len(T)
    pmin = C.min_p(total, n_perm=10 ** 9)
    return M, np.array([C.verdict(x, pmin) for x in p])


def false_fail(configs):
    rows, by_config, table_fail, table_inc, masks = [], [], None, None, None
    table_count = 0
    for c in configs:
        per_seed, _ = S.load(os.path.join(SUM, f"{c}.json.gz"))
        seeds = sorted(per_seed)
        if len(seeds) != 15:
            print(f"# {c}: {len(seeds)} seeds, skipped", file=sys.stderr)
            continue
        runs = [per_seed[s] for s in seeds]
        any_fail, any_inc = 0, 0
        for name in C.summary_names(runs, runs):
            X = np.vstack([r[name] for r in runs])
            M, v = all_split_verdicts(X, S.KIND[name])
            if masks is None:
                masks = M
            assert np.array_equal(M, masks)
            rows.append((c, name, len(v), np.mean(v == "FAIL"), np.mean(v == "INCONCLUSIVE")))
            any_fail = any_fail | (v == "FAIL")
            any_inc = any_inc | (v != "PASS")
            table_count = table_count + (v != "PASS")
        by_config.append((c, len(any_fail), np.mean(any_fail), np.mean(any_inc)))
        table_fail = any_fail if table_fail is None else table_fail | any_fail
        table_inc = any_inc if table_inc is None else table_inc | any_inc
    return rows, by_config, (np.mean(table_fail), np.mean(table_inc)), table_count


def power(configs):
    perm = permuted([c for c in configs if "." not in c])
    rows = []
    for c in configs:
        if "." in c:
            continue
        ref_seeds, _ = S.load(os.path.join(SUM, f"{c}.json.gz"))
        ref = [ref_seeds[s] for s in REF_SEEDS]
        for variant in ("np20", "alphafixed", "noc4", "permuted"):
            if variant == "permuted":
                cand = list(perm[c].values())
            else:
                f = os.path.join(SUM, f"{c}.{variant}.json.gz")
                if not os.path.exists(f):
                    continue
                cand = list(S.load(f)[0].values())
            for name in C.summary_names(ref, cand):
                r = C.compare_one(ref, cand, name)
                rows.append((c, variant, name, len(ref), len(cand), r["effect"], r["p"], r["verdict"],
                             r["python"], r["candidate"]))
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sorted(f[:-8] for f in os.listdir(SUM) if f.endswith(".json.gz"))
    configs = [c for c in names if "." not in c or c.endswith(".chains4")]
    rows, by_config, (tf, ti), count = false_fail(configs)
    with open(os.path.join(OUT, "false_fail.tsv"), "w") as fh:
        fh.write("config\tsummary\tn_splits\tfail_rate\tinconclusive_rate\n")
        for r in rows:
            fh.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]:.4f}\t{r[4]:.4f}\n")
    with open(os.path.join(OUT, "false_fail_by_config.tsv"), "w") as fh:
        fh.write("config\tn_splits\tany_fail_rate\tany_not_pass_rate\n")
        for r in by_config:
            fh.write(f"{r[0]}\t{r[1]}\t{r[2]:.4f}\t{r[3]:.4f}\n")
        fh.write(f"TABLE\t{by_config[0][1] if by_config else 0}\t{tf:.4f}\t{ti:.4f}\n")
    with open(os.path.join(OUT, "false_fail_table_count.tsv"), "w") as fh:
        fh.write("non_pass_cells_at_least\tfraction_of_splits\n")
        for k in range(int(count.max()) + 1):
            fh.write(f"{k}\t{np.mean(count >= k):.4f}\n")
    prow = power(configs)
    with open(os.path.join(OUT, "power.tsv"), "w") as fh:
        fh.write("config\tbroken\tsummary\tn_python\tn_broken\teffect\tp\tverdict\tpython\tbroken_value\n")
        for r in prow:
            fh.write("\t".join([r[0], r[1], r[2], str(r[3]), str(r[4]), f"{r[5]:.3g}", f"{r[6]:.4g}",
                                r[7], r[8], r[9]]) + "\n")
    print(open(os.path.join(OUT, "false_fail_by_config.tsv")).read())
    for variant in ("np20", "alphafixed", "noc4", "permuted"):
        v = [r for r in prow if r[1] == variant]
        print(variant, {k: sum(r[7] == k for r in v) for k in ("PASS", "INCONCLUSIVE", "FAIL")},
              "configs with >=1 FAIL:", len({r[0] for r in v if r[7] == "FAIL"}), "/", len({r[0] for r in v}))


if __name__ == "__main__":
    main()
