"""Freeze the deterministic parts of the original (Python) PhyClone + tools/ extensions.

Writes JSON fixtures under phyclone_rs/golden/fixtures/ for a reimplementation to match:

  datapoints/<case>__<loader>.json   per-SNV log-likelihood grids (samples x grid) from each loader
  pairs/<case>__<pair model>.json    eligible pairs and their 4 relation scores
  trees/<case>.json                  trees (from the reference traces, the truth tree and seeded
                                     random trees with up to 8 nodes and several roots), and for
                                     each tree: FSCRP prior parts at fixed alphas, multiplicity,
                                     and the C4 pair term under each pair model
  scores/<case>__<loader>.json       per tree: data_log_likelihood (samples x grid), log_p and
                                     log_p_one of TreeJointDistribution (no pair term, outliers
                                     off) at each alpha, and the MAP clone table (ccf, clonal_prev)

freeze_m7.py adds the M7 fixtures (outlier model, loss prior options, --precision, grid >= 1000)
through the same writer.

Nothing here is random. Run it twice and the outputs must be byte-identical (`--check` compares
against the files on disk instead of writing them).

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
    phyclone_rs/golden/freeze.py [--check]
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phyclone_hp  # noqa: E402
from phyclone_pairs import PairTable, tree_assignment  # noqa: E402

G = os.path.join(ROOT, "phyclone_rs", "golden")
GRID = 101
PRECISION = 400
ALPHAS = (0.5, 1.0, 2.5)
TREES_PER_TRACE = 25
RANDOM_TREES = 15  # seeded random trees per case: short reference runs can stay on one tree
MAX_RANDOM_NODES = 8

# loader id -> (hp mode, density, input file); base uses PhyClone's own load_data
LOADERS = {
    "base_binomial": ("base", "binomial", "data.tsv"),
    "base_betabin": ("base", "beta-binomial", "data.tsv"),
    "a1_binomial": ("a1", "binomial", "data_hp.tsv"),
    "a2_binomial": ("a2", "binomial", "data_hp.tsv"),
}
# pair model id -> PairTable.from_files keyword arguments
PAIR_MODELS = {
    "eps0.01": dict(eps=0.01),
    "eps0.01_w0.3": dict(eps=0.01, weight=0.3),
    "err0.004": dict(err=0.004),
    "err0.03": dict(err=0.03),
    "err0.004_hpu": dict(err=0.004, hp_uncertain=True),
    "err0.03_hpu": dict(err=0.03, hp_uncertain=True),
}
CASES = {
    "stress_e0_s1": dict(loaders=["base_binomial", "base_betabin", "a1_binomial", "a2_binomial"],
                         pairs=True, traces=["e0_base_bin"]),
    "stress_real_s1": dict(loaders=["base_binomial", "a2_binomial"], pairs=True,
                           traces=["real_a2_err004"]),
    "stress_b03_s1": dict(loaders=["base_binomial"], pairs=True,
                          traces=["b03_base_eps001", "b03_base_err003_hpu"]),
    "random_spec_0000": dict(loaders=["base_binomial", "base_betabin", "a1_binomial", "a2_binomial"],
                             pairs=True, traces=["random_a1_bin", "random_base_betabin"]),
    "upstream_mixing_small": dict(loaders=["upstream_clusters"], pairs=False,
                                  traces=["upstream_clusters"]),
}


def num(x):
    """Floats as round-trip decimal strings are what json writes; keep inf/nan explicit."""
    if isinstance(x, (list, tuple)):
        return [num(v) for v in x]
    x = float(x)
    if np.isnan(x):
        return "nan"
    if np.isinf(x):
        return "inf" if x > 0 else "-inf"
    return x


def load_datapoints(case, loader):
    from phyclone.data.pyclone import load_data

    inp = os.path.join(G, "cases", case, "input")
    rng = np.random.default_rng(0)  # only used with a cluster file and assign_loss_prob
    if loader == "upstream_clusters":
        data, samples, clusters = load_data(
            os.path.join(inp, "mixing_small.tsv"), rng, 0.4, False, False,
            cluster_file=os.path.join(inp, "mixing_small_clusters.tsv"),
            density="beta-binomial", grid_size=GRID, outlier_prob=0, precision=PRECISION)
        return data, list(samples), clusters
    mode, density, fname = LOADERS[loader]
    fn = load_data if mode == "base" else phyclone_hp.make_loader(
        mode, os.path.join(inp, "segments.tsv") if mode == "a2" else None)
    data, samples, clusters = fn(os.path.join(inp, fname), rng, 0.4, False, False,
                                 density=density, grid_size=GRID, outlier_prob=0,
                                 precision=PRECISION)
    return data, list(samples), clusters


def tree_spec(tree):
    """{node: {"parent": node or "root", "mutations": [...]}} with nodes relabelled 0..K-1."""
    node_of, _ = tree_assignment(tree)
    node_of = {str(m): n for m, n in node_of.items()}  # cluster ids are integers
    nodes = sorted(set(node_of.values()), key=lambda n: min(m for m, v in node_of.items() if v == n))
    label = {n: i for i, n in enumerate(nodes)}
    root = tree.root_node_name
    spec = {}
    for n in nodes:
        p = tree.get_parent(n)
        spec[str(label[n])] = {"parent": "root" if p == root else str(label[p]),
                               "mutations": sorted(m for m, v in node_of.items() if v == n)}
    return spec


def build(spec, datapoints):
    """PhyClone Tree from a spec; datapoints: name -> DataPoint."""
    from phyclone.tree import Tree

    children = {}
    for n, v in spec.items():
        children.setdefault(v["parent"], []).append(n)
    tree = Tree(next(iter(datapoints.values())).value.shape)
    made = {}

    def make(n):
        kids = [make(k) for k in sorted(children.get(n, []), key=int)]
        made[n] = tree.create_root_node(children=kids,
                                        data=[datapoints[m] for m in spec[n]["mutations"]])
        return made[n]

    for n in sorted(children.get("root", []), key=int):
        make(n)
    return tree, made


def trees_for(case, datapoints_any):
    """Reference-trace trees (evenly spaced iterations, deduplicated) plus the MAP and truth."""
    from phyclone.utils.load_hdf5 import (build_datapoints_dict_from_trace,
                                          build_map_tree_from_trace, load_chain_trace_data_df)

    out, seen = [], {}

    def add(name, spec):  # a tree seen before keeps its first id and lists this one as an alias
        key = json.dumps(spec, sort_keys=True)
        if key in seen:
            seen[key].setdefault("aliases", []).append(name)
        else:
            seen[key] = {"id": name, "nodes": spec}
            out.append(seen[key])

    for run in CASES[case]["traces"]:
        tr = os.path.join(G, "runs", run, "trace.h5")
        df = load_chain_trace_data_df(tr)
        dps = build_datapoints_dict_from_trace(tr)
        m = df.loc[df["log_p"].idxmax()]
        add(f"{run}:map", tree_spec(build_map_tree_from_trace(tr, int(m.chain_num), int(m.iter), dps)))
        idx = np.linspace(0, len(df) - 1, TREES_PER_TRACE).round().astype(int)
        for i in idx:
            r = df.iloc[i]
            add(f"{run}:iter{int(r['iter'])}",
                tree_spec(build_map_tree_from_trace(tr, int(r.chain_num), int(r['iter']), dps)))
    truth = os.path.join(G, "cases", case, "truth", "truth.tsv")
    if os.path.exists(truth):
        t = pd.read_csv(truth, sep="\t")
        tt = pd.read_csv(os.path.join(G, "cases", case, "truth", "truth_tree.tsv"), sep="\t")
        names = set(datapoints_any)
        clones = [c for c in tt.clone if (t.origin_clone == c).any()]
        label = {c: str(i) for i, c in enumerate(clones)}
        par = dict(zip(tt.clone, tt.parent))

        def up(c):  # nearest ancestor that holds SNVs
            p = par[c]
            while p != "root" and p not in label:
                p = par[p]
            return "root" if p == "root" else label[p]
        add("truth", {label[c]: {"parent": up(c),
                                 "mutations": sorted(m for m in t.mutation_id[t.origin_clone == c]
                                                     if m in names)} for c in clones})
    seed = int(hashlib.sha256(case.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    names = sorted(datapoints_any)
    for k in range(RANDOM_TREES):
        n_nodes = int(rng.integers(1, min(MAX_RANDOM_NODES, len(names)) + 1))
        order = rng.permutation(len(names))
        node = np.empty(len(names), int)
        node[order[:n_nodes]] = np.arange(n_nodes)          # every node gets at least one SNV
        node[order[n_nodes:]] = rng.integers(0, n_nodes, len(names) - n_nodes)
        parent = ["root"] + [("root" if rng.random() < 0.2 else str(int(rng.integers(0, i))))
                             for i in range(1, n_nodes)]
        add(f"random:{k}", {str(i): {"parent": parent[i],
                                     "mutations": [names[j] for j in np.nonzero(node == i)[0]]}
                            for i in range(n_nodes)})
    return out


def prior_parts(tree, alpha):
    from phyclone.tree.distributions import FSCRPDistribution
    from phyclone.utils.math_utils import cached_log_factorial

    p = FSCRPDistribution(alpha)
    crp, k = p.compute_CRP_prior(tree)
    sizes = [len(v) for n, v in tree.node_data.items() if n != tree.outlier_node_name]
    roots = tree.roots
    return {"alpha": alpha, "num_nodes": k, "num_roots": len(roots),
            "crp": num(crp), "sum_log_factorial_size_minus_1":
                num(sum(cached_log_factorial(s - 1) for s in sizes)),
            "r_term": num(p._compute_r_term(len(roots), k)),
            "multiplicity": num(tree.multiplicity),
            "prior_log_p": num(p.log_p(tree)), "prior_log_p_one": num(p.log_p_one(tree))}


def freeze_case(case, write):
    cfg = CASES[case]
    inp = os.path.join(G, "cases", case, "input")
    loaded = {ld: load_datapoints(case, ld) for ld in cfg["loaders"]}
    first = next(iter(loaded.values()))
    any_dps = {str(dp.name): dp for dp in first[0]}
    trees = trees_for(case, any_dps)

    for ld, (data, samples, _) in loaded.items():
        write(f"datapoints/{case}__{ld}.json", {
            "case": case, "loader": ld, "grid_size": GRID, "precision": PRECISION,
            "samples": samples,
            "datapoints": [{"idx": int(dp.idx), "name": str(dp.name), "value": num(dp.value.tolist())}
                           for dp in data]})

    tables = {}
    if cfg["pairs"]:
        for pm, kw in PAIR_MODELS.items():
            t = PairTable.from_files(f"{inp}/pairs.tsv", f"{inp}/data_hp.tsv",
                                     f"{inp}/segments.tsv", **kw)
            tables[pm] = t
            write(f"pairs/{case}__{pm}.json", {
                "case": case, "pair_model": pm, "options": kw,
                "relations": ["same", "ancestor", "descendant", "branch"],
                "pairs": [{"i": a, "j": b, "scores": num(s.tolist())}
                          for a, b, s in zip(t.mut_i, t.mut_j, t.scores)]})

    tree_rows = []
    for tr in trees:
        tree, _ = build(tr["nodes"], any_dps)
        row = {**tr, "prior": [prior_parts(tree, a) for a in ALPHAS]}
        if tables:
            row["pair_term"] = {pm: num(t.term(*tree_assignment(tree))) for pm, t in tables.items()}
        tree_rows.append(row)
    write(f"trees/{case}.json", {"case": case, "alphas": list(ALPHAS), "trees": tree_rows})

    from phyclone.process_trace.process_trace import get_clone_table
    from phyclone.tree.distributions import FSCRPDistribution, TreeJointDistribution

    for ld, (data, samples, clusters) in loaded.items():
        dps = {str(dp.name): dp for dp in data}
        rows = []
        for tr in trees:
            tree, _ = build(tr["nodes"], dps)
            r = {"id": tr["id"], "data_log_likelihood": num(tree.data_log_likelihood.tolist())}
            for a in ALPHAS:
                j = TreeJointDistribution(FSCRPDistribution(a))
                r[f"log_p@{a}"] = num(j.log_p(tree))
                r[f"log_p_one@{a}"] = num(j.log_p_one(tree))
            ids = [tr["id"], *tr.get("aliases", [])]
            if any(i.endswith(":map") for i in ids) or "truth" in ids:
                table, _ = get_clone_table({dp.idx: dp for dp in data}, samples, tree,
                                           clusters=clusters)
                table = table.sort_values(["mutation_id", "sample_id"]).reset_index(drop=True)
                r["clone_table"] = {c: (num(table[c].tolist()) if table[c].dtype.kind == "f"
                                        else [str(v) for v in table[c]]) for c in table.columns}
            rows.append(r)
        write(f"scores/{case}__{ld}.json", {"case": case, "loader": ld, "alphas": list(ALPHAS),
                                            "trees": rows})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare with the files on disk")
    a = ap.parse_args()
    out = os.path.join(G, "fixtures")
    bad, written = [], {}

    def write(rel, obj):
        text = json.dumps(obj, indent=None, separators=(",", ":"), sort_keys=True) + "\n"
        path = os.path.join(out, rel)
        written[rel] = hashlib.sha256(text.encode()).hexdigest()
        if a.check:
            if not os.path.exists(path) or open(path).read() != text:
                bad.append(rel)
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(text)

    for case in CASES:
        freeze_case(case, write)
    import freeze_m7  # outlier model, loss priors, precision, grid >= 1000 (M7)
    freeze_m7.freeze_all(write)
    if a.check:
        print("identical" if not bad else f"DIFFERENT: {bad}")
        sys.exit(1 if bad else 0)
    with open(os.path.join(out, "SHA256SUMS"), "w") as fh:
        fh.writelines(f"{h}  {rel}\n" for rel, h in sorted(written.items()))
    print(f"wrote {len(written)} fixtures")


if __name__ == "__main__":
    main()
