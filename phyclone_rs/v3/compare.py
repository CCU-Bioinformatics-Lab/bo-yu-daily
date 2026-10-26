"""V3 verdict table: Rust (or any candidate) runs vs the Python seed-to-seed baseline.

For each config and summary, pool the N Python runs and the M candidate runs (one run = one seed)
and run a permutation test on T = weighted L1 distance between the two groups' mean summary
vectors (weights per KIND in summaries.py; they depend only on the pooled runs, so the test is
exact under the null that both samplers give exchangeable runs). Verdict:
  FAIL          p < ALPHA_FAIL
  INCONCLUSIVE  ALPHA_FAIL <= p < ALPHA_WARN (rerun with more seeds), or the seed counts cannot
                reach p < ALPHA_FAIL at all, or the summary is missing on one side
  PASS          p >= ALPHA_WARN
`effect` = T_obs / median T over the permutations (about 1 under the null).
Overall: FAIL if any cell FAILs; INCONCLUSIVE if >= TABLE_INCONCLUSIVE cells are INCONCLUSIVE
(a few are expected by chance, see README); else PASS.

Layout of CANDIDATE_ROOT: <config>/<seed dir>/ holding a TSV trace dir (meta.json, ...) or a
trace.h5. <config> is a golden run name (golden/runs.tsv), or <run>.<variant> for a non-ref
variant of variants.tsv (e.g. e0_base_bin.chains4). Python summaries come from
baseline/summaries/<config>.json.gz (summarize_baseline.py).

Usage:
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
    phyclone_rs/v3/compare.py CANDIDATE_ROOT [--out verdicts.tsv] [--configs a b ...]
Exit status 1 if any cell is FAIL.
"""
import argparse
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations

import numpy as np

V3 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, V3)
import summaries as S  # noqa: E402

ALPHA_FAIL = 0.001
ALPHA_WARN = 0.01
TABLE_INCONCLUSIVE = 3  # Python vs Python: >= 3 non-PASS cells in 4.9% of table splits
N_PERM = 10000
TIE = 1e-9  # relative size below which two statistics are equal (float rounding of means)
CHUNK = 256


def weights(X, kind):
    d = X.shape[1]
    if kind == "dist":
        return np.full(d, 0.5)
    if kind == "matrix":
        return np.full(d, 1.0 / d)
    if kind == "quant":
        sd = X.std(axis=0, ddof=1) if len(X) > 1 else np.zeros(d)
        live = sd > TIE * (1.0 + np.abs(X).max(axis=0))  # a constant component stays constant
        return np.where(live, 1.0 / (d * np.where(live, sd, 1.0)), 0.0)
    return np.ones(d)


def split_masks(n, m, n_perm=N_PERM, seed=0):
    """Rows = candidate-group indicator over n pooled runs; row 0 is the observed split
    (candidates last). Exact enumeration when C(n, m) <= n_perm."""
    total = math.comb(n, m)
    if total <= n_perm:
        rows = [list(c) for c in combinations(range(n), m)]
        rows.remove(list(range(n - m, n)))
        rows.insert(0, list(range(n - m, n)))
        exact = True
    else:
        rng = np.random.default_rng(seed)
        rows = [list(range(n - m, n))] + [sorted(rng.choice(n, m, replace=False))
                                          for _ in range(n_perm - 1)]
        exact = False
    M = np.zeros((len(rows), n))
    for i, r in enumerate(rows):
        M[i, r] = 1.0
    return M, exact, total


def split_stats(X, M, kind):
    """T for every split row of M over the pooled runs X (n x d)."""
    w = weights(X, kind)
    m = M[0].sum()
    scale = float(np.abs(X).max(axis=0) @ w)
    n = X.shape[0]
    out = np.empty(len(M))
    tot = X.sum(axis=0)
    for i in range(0, len(M), CHUNK):
        sb = M[i:i + CHUNK] @ X
        diff = sb / m - (tot - sb) / (n - m)
        out[i:i + CHUNK] = np.abs(diff) @ w
    return np.where(out < TIE * max(1.0, scale), 0.0, out)


def p_values(T, exact):
    """p for row 0 of T (one-sided: large T = groups differ)."""
    tol = TIE * max(1.0, abs(T[0]))
    return float(np.mean(T >= T[0] - tol)) if exact else float((np.sum(T[1:] >= T[0] - tol) + 1) / len(T))


def min_p(total, n_perm=N_PERM):
    return 1.0 / total if total <= n_perm else 1.0 / n_perm


def verdict(p, pmin):
    if pmin >= ALPHA_FAIL:
        return "INCONCLUSIVE"
    if p < ALPHA_FAIL:
        return "FAIL"
    if p < ALPHA_WARN:
        return "INCONCLUSIVE"
    return "PASS"


def describe(X):
    """Short text for a group: mean (and range) of a scalar, else the dimension."""
    if X.shape[1] == 1:
        return f"{X.mean():.4g} [{X.min():.4g},{X.max():.4g}]"
    return f"d={X.shape[1]}"


def compare_one(ref, cand, name):
    """ref, cand: lists of per-run summary dicts. Returns a result row dict for summary name."""
    kind = S.KIND[name]
    if not ref or not cand or name not in ref[0] or name not in cand[0]:
        return {"summary": name, "kind": kind, "p": float("nan"), "effect": float("nan"),
                "verdict": "INCONCLUSIVE", "python": "missing" if not ref or name not in ref[0] else "",
                "candidate": "missing" if not cand or name not in cand[0] else ""}
    A = np.vstack([r[name] for r in ref])
    B = np.vstack([r[name] for r in cand])
    X = np.vstack([A, B])
    M, exact, total = split_masks(len(X), len(B))
    T = split_stats(X, M, kind)
    p = p_values(T, exact)
    med = float(np.median(T))
    effect = T[0] / med if med > 0 else (0.0 if T[0] == 0 else float("inf"))
    return {"summary": name, "kind": kind, "p": p, "effect": effect,
            "verdict": verdict(p, min_p(total)), "python": describe(A), "candidate": describe(B)}


def summary_names(ref, cand):
    keys = list(S.KIND)
    return [k for k in keys if (ref and k in ref[0]) or (cand and k in cand[0])]


def _summarize(args):
    root, config, seed = args
    res, muts = S.summarize_root(root, config, [seed])
    return config, seed, res[seed], muts


def summarize_candidates(root, configs, jobs=16):
    tasks = [(root, c, s) for c in configs for s in sorted(os.listdir(os.path.join(root, c)))
             if os.path.isdir(os.path.join(root, c, s))]
    out = {c: {} for c in configs}
    muts = {}
    with ProcessPoolExecutor(jobs) as ex:
        for c, s, d, m in ex.map(_summarize, tasks):
            out[c][s] = d
            muts.setdefault(c, m)
            if muts[c] != m:
                raise ValueError(f"{root}/{c}/{s}: mutation set differs between seeds")
    return out, muts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate_root")
    ap.add_argument("--baseline", default=os.path.join(V3, "baseline", "summaries"))
    ap.add_argument("--configs", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()

    have = {f[:-8] for f in os.listdir(a.baseline) if f.endswith(".json.gz")}
    present = {c for c in os.listdir(a.candidate_root) if os.path.isdir(os.path.join(a.candidate_root, c))}
    configs = sorted((set(a.configs) if a.configs else present) & present)
    missing = sorted(present - have)
    if missing:
        print(f"# no Python baseline for: {', '.join(missing)}", file=sys.stderr)
    configs = [c for c in configs if c in have]
    cand, cmuts = summarize_candidates(a.candidate_root, configs, a.jobs)

    cols = ["config", "summary", "kind", "n_python", "n_candidate", "python", "candidate",
            "effect", "p", "verdict"]
    lines = ["\t".join(cols)]
    worst = []
    for c in configs:
        ref_seeds, ref_muts = S.load(os.path.join(a.baseline, f"{c}.json.gz"))
        if cmuts[c] != ref_muts:
            raise SystemExit(f"{c}: candidate mutation set differs from the Python baseline")
        ref = list(ref_seeds.values())
        cn = list(cand[c].values())
        for name in summary_names(ref, cn):
            r = compare_one(ref, cn, name)
            worst.append(r["verdict"])
            lines.append("\t".join([c, name, r["kind"], str(len(ref)), str(len(cn)), r["python"],
                                    r["candidate"], f"{r['effect']:.3g}", f"{r['p']:.4g}",
                                    r["verdict"]]))
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    counts = {v: worst.count(v) for v in ("PASS", "INCONCLUSIVE", "FAIL")}
    overall = ("FAIL" if counts["FAIL"] else
               "INCONCLUSIVE" if counts["INCONCLUSIVE"] >= TABLE_INCONCLUSIVE else "PASS")
    print(f"# overall {overall}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
