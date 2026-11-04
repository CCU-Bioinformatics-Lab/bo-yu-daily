"""Allelic overdispersion of germline het SNVs in a normal sample, as PhyClone's beta-binomial precision.

PhyClone: alt ~ BetaBinomial(n, a = vaf * s, b = (1 - vaf) * s). Germline het sites have vaf 0.5, so
the spread of alt / depth beyond binomial gives s. Het calls are already filtered on AF by the caller,
which hides dispersion; a binomial null with the same depths and the same AF window, fitted the same way,
shows how much s the truncation alone produces.

Usage: python3 tools/normal_allelic_dispersion.py PHASED.vcf.gz OUT_DIR [--seed 1]
"""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln

AUTOSOMES = {f"chr{i}" for i in range(1, 23)}


def read_hets(vcf):
    rows = []
    with gzip.open(vcf, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.rstrip("\n").split("\t")
            if f[0] not in AUTOSOMES or f[6] != "PASS" or len(f[3]) != 1 or len(f[4]) != 1:
                continue
            fmt = dict(zip(f[8].split(":"), f[9].split(":")))
            if fmt.get("GT") not in ("0|1", "1|0") or fmt.get("PS", ".") == ".":
                continue
            ref, alt = (int(x) for x in fmt["AD"].split(","))
            rows.append((ref, alt, int(fmt["GQ"])))
    return np.array(rows, dtype=np.int64)


def bb_nll(params, n, x):
    mu, s = 1 / (1 + np.exp(-params[0])), np.exp(params[1])
    a, b = mu * s, (1 - mu) * s
    ll = (gammaln(n + 1) - gammaln(x + 1) - gammaln(n - x + 1)
          + betaln(x + a, n - x + b) - betaln(a, b))
    return -ll.sum()


def fit(n, x):
    """MLE of (mu, s); s capped at 1e6 (indistinguishable from binomial)."""
    r = minimize(bb_nll, [0.0, np.log(400)], args=(n, x), method="L-BFGS-B",
                 bounds=[(-3, 3), (np.log(1), np.log(1e6))])
    return float(1 / (1 + np.exp(-r.x[0]))), float(np.exp(r.x[1]))


def log_bb_pmf(n, x, mu, s):
    a, b = mu * s, (1 - mu) * s
    return (gammaln(n + 1) - gammaln(x + 1) - gammaln(n - x + 1)
            + betaln(x + a, n - x + b) - betaln(a, b))


def fit_truncated(n, x, lo, hi):
    """MLE of (mu, s) using only sites with lo <= x / n <= hi, each normalised by the mass of its
    window, so neither caller AF filtering nor genotype errors outside the window bias s."""
    ok = (x >= lo * n) & (x <= hi * n)
    n, x = n[ok], x[ok]
    depths, inv = np.unique(n, return_inverse=True)
    grids = [np.arange(int(np.ceil(lo * d)), int(np.floor(hi * d)) + 1) for d in depths]

    def nll(params):
        mu, s = 1 / (1 + np.exp(-params[0])), np.exp(params[1])
        log_z = np.array([np.logaddexp.reduce(log_bb_pmf(d, g, mu, s)) for d, g in zip(depths, grids)])
        return -(log_bb_pmf(n, x, mu, s) - log_z[inv]).sum()

    r = minimize(nll, [0.0, np.log(400)], method="L-BFGS-B",
                 bounds=[(-3, 3), (np.log(1), np.log(1e6))])
    return float(1 / (1 + np.exp(-r.x[0]))), float(np.exp(r.x[1])), int(ok.sum())


def inflation(s, n):
    """Variance of alt / n relative to binomial."""
    return 1 + (n - 1) / (s + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vcf")
    ap.add_argument("out_dir")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    h = read_hets(a.vcf)
    n_all = len(h)
    n = h[:, 0] + h[:, 1]
    med = float(np.median(n))
    keep = (n >= 0.5 * med) & (n <= 1.5 * med)
    h, n = h[keep], n[keep]
    x = h[:, 1]
    af = x / n
    lo, hi = float(af.min()), float(af.max())

    def null_fit(depths):
        xs = rng.binomial(depths, 0.5)
        ok = (xs / depths >= lo) & (xs / depths <= hi)
        return fit(depths[ok], xs[ok])

    res = {"vcf": a.vcf, "phased_het_snv": int(n_all), "kept": int(len(h)), "median_dp": med,
           "af_window": [lo, hi], "strata": []}
    strata = [("all", np.ones(len(h), bool)), ("GQ>=20", h[:, 2] >= 20)]
    q = np.quantile(n, [0, 1 / 3, 2 / 3, 1])
    for i in range(3):
        strata.append((f"DP {int(q[i])}-{int(q[i + 1])}", (n >= q[i]) & (n <= q[i + 1])))
    for name, m in strata:
        mu, s = fit(n[m], x[m])
        _, s0 = null_fit(n[m])
        res["strata"].append({"stratum": name, "sites": int(m.sum()), "mean_dp": float(n[m].mean()),
                              "mu": mu, "s": s, "s_binomial_null": s0,
                              "var_inflation_at_dp50": inflation(s, 50),
                              "var_inflation_at_dp73": inflation(s, 73)})
    res["truncated"] = []
    for lo_w, hi_w in [(0.2, 0.8), (0.3, 0.7)]:
        for name, m in strata[:1] + strata[2:]:
            mu, s, k = fit_truncated(n[m], x[m], lo_w, hi_w)
            xs = rng.binomial(n[m], 0.5)
            _, s0, _ = fit_truncated(n[m], xs, lo_w, hi_w)
            r = {"window": [lo_w, hi_w], "stratum": name, "sites": k, "mu": mu, "s": s,
                 "s_binomial_null": s0, "var_inflation_at_dp50": inflation(s, 50),
                 "var_inflation_at_dp73": inflation(s, 73)}
            res["truncated"].append(r)
            print(f"[{lo_w},{hi_w}] {name:>14} sites {k:>8} mu {mu:.4f} s {s:9.1f} "
                  f"null_s {s0:9.1f} infl@50 {r['var_inflation_at_dp50']:.2f} "
                  f"infl@73 {r['var_inflation_at_dp73']:.2f}")
    hist, edges = np.histogram(af, bins=np.linspace(0, 1, 41))
    res["af_hist"] = {"edges": edges.tolist(), "counts": hist.tolist()}
    (out / "result.json").write_text(json.dumps(res, indent=1))
    for r in res["strata"]:
        print(f"{r['stratum']:>14} sites {r['sites']:>8} dp {r['mean_dp']:5.1f} mu {r['mu']:.4f} "
              f"s {r['s']:9.1f} null_s {r['s_binomial_null']:9.1f} infl@50 {r['var_inflation_at_dp50']:.2f}")
    print(f"kept {len(h)}/{n_all}, median dp {med}, AF window [{lo:.3f}, {hi:.3f}]")


if __name__ == "__main__":
    main()
