"""Rerun PhyClone's test-utility simulator and write the FS-CRP benchmark file format.

usage: python tools/phyclone_sim_rerun.py OUT_DIR [--seed N] [--reps N] [--alpha A]

Calls the unmodified phyclone/tests/utilities/fscrp.py (simulate_fscrp_tree) and
sim_data_on_tree.py (simulate_data). Those functions write no files and do not keep
g_r, g_v or mu, so this script wraps get_parental_copy_number and simulate_counts
with recorders that call the originals with the same arguments (the rng call order
is unchanged). It then writes, per replicate OUT_DIR/run<i>/:
  ground_truth/data.tsv   same 17 columns as FS-CRP_Loss/.../ground_truth/data.tsv
  ground_truth/tree.json  same node-link schema (snvs, clonal_prev, cellular_prev)
  phyclone_input.tsv      only the 9 columns PhyClone reads (no truth columns)
and OUT_DIR/params.json.

Defaults reproduce the settings inferred from FS-CRP_Loss loss_prop_0.0_run* data:
600 SNVs, 8 samples, depth 1000, purity 1.0, total CN 2-6, minor CN >= 1.
alpha is not recorded by the authors; the program default is 1.0.

--cn-x-inclusive is a hypothesis test, not the published code: it draws the CN split
point x from 0..total_cn (inclusive) instead of 0..total_cn-1. The authors' data fit
the inclusive rule (see lab_report/2026-10-21_phyclone_sim_rerun/).

Needs PhyClone importable: PYTHONPATH=research/phyclone_research/PhyClone
First used in lab_report/2026-10-21_phyclone_sim_rerun/.
"""
import argparse, json, sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

import phyclone.tests.utilities.fscrp as fscrp
import phyclone.tests.utilities.sim_data_on_tree as sim

ERROR_RATE = 1e-3
INPUT_COLS = ["mutation_id", "sample_id", "ref_counts", "alt_counts", "major_cn",
              "minor_cn", "normal_cn", "tumour_content", "error_rate"]


ORIG_CN, ORIG_COUNTS = sim.get_parental_copy_number, sim.simulate_counts


def cn_x_inclusive(min_cn, max_cn, rng, min_minor_cn=0):
    total_cn = rng.integers(min_cn, max_cn + 1)
    x = rng.integers(0, total_cn + 1)
    minor_cn = max(min_minor_cn, min(total_cn - x, x))
    return minor_cn, total_cn - minor_cn


def record_calls(cn_x_inclusive_rule=False):
    """Wrap the two simulator functions; return the list the wrappers append to."""
    calls = []
    orig_cn = cn_x_inclusive if cn_x_inclusive_rule else ORIG_CN
    orig_counts = ORIG_COUNTS

    def cn(*args, **kwargs):
        minor, major = orig_cn(*args, **kwargs)
        calls.append({"minor_cn": minor, "major_cn": major})
        return minor, major

    def counts(f, t, depth, error_rate, g_n, g_r, g_v, rng):
        ref, var, mu = orig_counts(f, t, depth, error_rate, g_n, g_r, g_v, rng)
        calls[-1].update(ccf=f, g_n=g_n, g_r=g_r, g_v=g_v, ref_counts=ref, alt_counts=var, mu=mu)
        return ref, var, mu

    sim.get_parental_copy_number, sim.simulate_counts = cn, counts
    return calls


def simulate_one(rng, a):
    tree = fscrp.simulate_fscrp_tree(rng, alpha=a.alpha, dim=a.samples, num_data_points=a.snvs)
    calls = record_calls(a.cn_x_inclusive)
    sim.simulate_data(tree, rng, a.samples, depth=a.depth, error_rate=ERROR_RATE,
                      max_cn=a.max_cn, min_cn=a.min_cn, min_minor_cn=a.min_minor_cn,
                      tumour_content=a.purity)
    rows, it = [], iter(calls)
    for node in tree.nodes:  # same loop order as simulate_data: node -> snv -> sample
        for snv in tree.nodes[node]["snvs"]:
            for s in range(a.samples):
                c = next(it)
                dp = tree.nodes[node]["converted_sample_dp"][s][snv]
                assert (dp.a, dp.b) == (c["ref_counts"], c["alt_counts"])
                rows.append({"mutation_id": snv, "sample_id": f"s{s}",
                             "ref_counts": c["ref_counts"], "alt_counts": c["alt_counts"],
                             "major_cn": c["major_cn"], "minor_cn": c["minor_cn"], "normal_cn": 2,
                             "tumour_content": a.purity, "error_rate": ERROR_RATE,
                             "g_n": c["g_n"], "g_r": c["g_r"], "g_v": c["g_v"],
                             "ccf": c["ccf"], "mu": c["mu"], "cluster": node,
                             "coord": int(snv[1:]), "chrom": 19})
    assert next(it, None) is None
    return tree, pd.DataFrame(rows)


def tree_json(tree):
    nodes = [{"snvs": tree.nodes[n]["snvs"], "clonal_prev": tree.nodes[n]["clonal_prev"].tolist(),
              "cellular_prev": tree.nodes[n]["cellular_prev"].tolist(), "id": int(n)} for n in tree.nodes]
    edges = [{"parent": int(p), "child": int(c)} for p, c in tree.edges]
    return {"directed": True, "multigraph": False,
            "graph": {"Method_Name": "Ground-Truth", "root": int(tree.graph["root"])},
            "nodes": nodes, "edges": edges}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=20261021)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--alpha", type=float, default=1.0)
    ap.add_argument("--snvs", type=int, default=600)
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--depth", type=int, default=1000)
    ap.add_argument("--purity", type=float, default=1.0)
    ap.add_argument("--min-cn", type=int, default=2)
    ap.add_argument("--max-cn", type=int, default=6)
    ap.add_argument("--min-minor-cn", type=int, default=1)
    ap.add_argument("--cn-x-inclusive", action="store_true", help="hypothesis test, not the published code")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)  # never overwrite an earlier rerun
    (out / "params.json").write_text(json.dumps(
        {**vars(a), "error_rate": ERROR_RATE, "numpy": np.__version__, "networkx": nx.__version__,
         "python": sys.version.split()[0]}, indent=2))
    for i in range(a.reps):
        rng = np.random.default_rng([a.seed, i])
        tree, df = simulate_one(rng, a)
        d = out / f"run{i}"
        (d / "ground_truth").mkdir(parents=True)
        df.to_csv(d / "ground_truth" / "data.tsv", sep="\t", index=False)
        (d / "ground_truth" / "tree.json").write_text(json.dumps(tree_json(tree), indent=4))
        df[INPUT_COLS].to_csv(d / "phyclone_input.tsv", sep="\t", index=False)
        print(f"run{i}: {tree.number_of_nodes()} clusters, {len(df)} rows", flush=True)


if __name__ == "__main__":
    main()
