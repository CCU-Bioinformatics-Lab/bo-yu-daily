"""Compare rerun pearsim truth pickles with the authors' Pairtree benchmark pickles.

usage: python tools/pairtree_sim_check.py RERUN_PICKLE_DIR [AUTHOR_DIR] [--out OUT_TSV]

RERUN_PICKLE_DIR: *.truth.pickle written by pairtree/simulator/make_simulated_data.sh.
AUTHOR_DIR: default /big8_disk/boyu114/phyclone_dataset/Pairtree/data_archive.

Prints:
  1. job names: rerun set vs author set
  2. format: pickle keys, args (paths and seed excluded), variant keys
  3. identity: how many rerun pickles equal the author pickle of the same name
  4. rule checks per dataset, from pearsim 0b9b249 simulator.py (both sources)
  5. statistics, mean over datasets, with a two-sample KS p-value
First used in lab_report/2026-10-22_pairtree_conipher_sim_rerun/.
"""
import pickle, re, sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

AUTHOR = "/big8_disk/boyu114/phyclone_dataset/Pairtree/data_archive"
PATH_ARGS = {"numpy_fn", "truthfn", "paramsfn", "ssmfn", "seed"}


def ancestral(parents):
    K = len(parents) + 1
    Z = np.eye(K)
    for c in range(1, K):
        p = parents[c - 1]
        while True:
            Z[p, c] = 1
            if p == 0:
                break
            p = parents[p - 1]
    return Z


def depth(parents):
    d = {0: 0}
    for c in range(1, len(parents) + 1):
        d[c] = d[parents[c - 1]] + 1
    return max(d.values())


def rules(p):
    a = p["args"]
    V = np.array([v["var_reads"] for v in p["variants"].values()])
    T = np.array([v["total_reads"] for v in p["variants"].values()])
    phi_v = np.array([v["phi"] for v in p["variants"].values()])
    pops = np.asarray(p["ssm_pops"])
    return {
        "phi=Z.eta": np.allclose(ancestral(p["structure"]) @ p["eta"], p["phi"]),
        "root_phi=1": np.allclose(p["phi"][0], 1),
        # eta is clamped at 1e-30, then renormalised, so the floor lands just under 1e-30
        "eta_floor_1e-30": bool((p["eta"] >= 0.99e-30).all()),
        "parent<child_id": all(par < c + 1 for c, par in enumerate(p["structure"])),
        "every_cluster_has_ssm": set(pops) == set(range(1, a["K"] + 1)),
        "clusters=ssm_pops": all(pops[int(s[1:])] == k + 1 for k, cl in enumerate(p["clusters"]) for s in cl),
        "variant_phi=cluster_phi": np.allclose(phi_v, p["phi"][pops]),
        "total_reads=T": bool((T == a["T"]).all()),
        "omega=0.5": all(np.all(v["omega_v"] == 0.5) for v in p["variants"].values()),
        "no_cna": len(p["cna_events"]) == 0 and bool((p["alleles"] == 1).all()),
        "M_variants": len(p["variants"]) == a["M"],
    }, V, T, phi_v


def stats(p, V, T, phi_v):
    par = np.asarray(p["structure"])
    K = len(par)
    exp = 0.5 * phi_v * T
    var = np.maximum(T * 0.5 * phi_v * (1 - 0.5 * phi_v), 1e-12)
    sizes = np.bincount(p["ssm_pops"], minlength=K + 1)[1:]
    return {
        "root_children": int((par == 0).sum()),
        "frac_chain_ext": float(np.mean(par == np.arange(K))),  # parent == previous node
        "depth_over_K": depth(par) / K,
        "eta_max": float(p["eta"].max(axis=0).mean()),
        "eta_root": float(p["eta"][0].mean()),
        "cluster_size_cv": float(sizes.std() / sizes.mean()),
        "vaf_mean": float((V / T).mean()),
        "frac_zero_var": float((V == 0).mean()),
        "binom_z_mean": float(((V - exp) / np.sqrt(var)).mean()),
        "binom_z_var": float((((V - exp) / np.sqrt(var)) ** 2).mean()),
    }


def load(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def same(a, b):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and not isinstance(a, np.ndarray):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return np.array_equal(a, b)


def main(argv):
    rerun = Path(argv[0])
    author = Path(argv[1]) if len(argv) > 1 and not argv[1].startswith("--") else Path(AUTHOR)
    r_files = {re.sub("_G0_", "_", f.name.replace(".truth.pickle", "")): f for f in rerun.glob("*.truth.pickle")}
    a_files = {d.name: next((d / "ground_truth").glob("*.pickle")) for d in author.glob("sim_*")}
    print(f"## 1. job names: rerun {len(r_files)}, author {len(a_files)}, "
          f"shared {len(r_files.keys() & a_files.keys())}")

    fmt, ident, pass_ = Counter(), 0, {"rerun": Counter(), "author": Counter()}
    rows = {"rerun": [], "author": []}
    for name in sorted(r_files.keys() & a_files.keys()):
        r, a = load(r_files[name]), load(a_files[name])
        fmt["pickle_keys"] += r.keys() == a.keys()
        fmt["args"] += ({k: v for k, v in r["args"].items() if k not in PATH_ARGS}
                        == {k: v for k, v in a["args"].items() if k not in PATH_ARGS})
        fmt["variant_keys"] += next(iter(r["variants"].values())).keys() == next(iter(a["variants"].values())).keys()
        fmt["args_seed_none"] += r["args"]["seed"] is None and a["args"]["seed"] is None
        ident += same({k: v for k, v in r.items() if k not in ("args", "seed")},
                      {k: v for k, v in a.items() if k not in ("args", "seed")})
        for label, p in (("rerun", r), ("author", a)):
            res, V, T, phi_v = rules(p)
            pass_[label].update(k for k, v in res.items() if v)
            rows[label].append({"name": name, "K": p["args"]["K"], **stats(p, V, T, phi_v)})
    n = len(rows["rerun"])
    print("\n## 2. format (datasets matching / shared)")
    for k, v in fmt.items():
        print(f"{k}: {v}/{n}")
    print(f"\n## 3. identical simulated content (args and seed excluded): {ident}/{n}")
    print("\n## 4. rule checks (datasets passing / datasets)")
    for k in pass_["author"].keys() | pass_["rerun"].keys():
        print(f"{k}: rerun {pass_['rerun'][k]}/{n}, author {pass_['author'][k]}/{n}")
    R, A = pd.DataFrame(rows["rerun"]), pd.DataFrame(rows["author"])
    table = []
    for c in R.columns[2:]:
        table.append({"stat": c, "rerun_mean": R[c].mean(), "author_mean": A[c].mean(),
                      "ks_p": ks_2samp(R[c], A[c]).pvalue})
        for K in sorted(R.K.unique()):
            table.append({"stat": f"{c} (K={K})", "rerun_mean": R[R.K == K][c].mean(),
                          "author_mean": A[A.K == K][c].mean(),
                          "ks_p": ks_2samp(R[R.K == K][c], A[A.K == K][c]).pvalue})
    out = pd.DataFrame(table)
    print("\n## 5. statistics (mean over datasets; KS test rerun vs author)")
    print(out[~out.stat.str.contains(r"\(K=")].to_string(index=False, float_format="%.4f"))
    if "--out" in argv:
        out.to_csv(argv[argv.index("--out") + 1], sep="\t", index=False, float_format="%.6g")


if __name__ == "__main__":
    main(sys.argv[1:])
