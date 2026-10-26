"""One in-memory form for a PhyClone trace, read from a Python trace.h5 or a Rust TSV trace dir.

A Trace is a list of posterior samples. Each sample has chain, iter, alpha, log_p_one, num_nodes,
num_roots and an index into `trees`. A Tree is the clone tree at mutation level:
  node_of[m]  node of mutation m (index into Trace.mutations), OUTLIER for the outlier node
  parent[n]   parent node of node n, ROOT when n hangs off PhyClone's dummy root
Nodes are relabelled canonically (see canonical_tree), so two traces that sampled the same tree
hold equal Tree values whatever node names their samplers used. A cluster-file run is expanded
from cluster ids to mutation ids, so Python and Rust compare at the same unit either way.

TSV layout (phyclone_rs/PORTING.md section 5): meta.json, iterations.tsv, trees.tsv,
assignments.tsv, optional clusters.tsv. Extra columns are ignored. meta.json may rename columns:
  {"columns": {"iterations.tsv": {"log_p_one": "<name in file>", ...}, ...},
   "outlier_node": <node id used for outliers in assignments.tsv>}
Rows of iterations.tsv with a `phase` column other than "sample" are dropped (burn-in rows), so
a writer that also stores burn-in stays comparable with the Python trace, which does not.
"""
import csv
import json
import os
from dataclasses import dataclass

import numpy as np

ROOT = -1
OUTLIER = -1

ITER_COLS = ("chain", "iter", "alpha", "log_p_one", "num_nodes", "num_roots", "tree_id")
TREE_COLS = ("tree_id", "node", "parent")
ASSIGN_COLS = ("tree_id", "mutation", "node")


@dataclass(frozen=True)
class Tree:
    node_of: tuple
    parent: tuple

    @property
    def num_nodes(self):
        return len(self.parent)


@dataclass
class Trace:
    mutations: list
    chain: np.ndarray
    iter: np.ndarray
    alpha: np.ndarray
    log_p_one: np.ndarray
    num_nodes: np.ndarray
    num_roots: np.ndarray
    tree_idx: np.ndarray
    trees: list
    meta: dict

    def __len__(self):
        return len(self.iter)


def canonical_tree(node_of, parent):
    """Relabel nodes by the first mutation they hold (mutation order), empty nodes last."""
    order = []
    for n in node_of:
        if n != OUTLIER and n not in order:
            order.append(n)
    order += sorted(n for n in parent if n not in order)
    new = {old: i for i, old in enumerate(order)}
    return Tree(tuple(new[n] if n != OUTLIER else OUTLIER for n in node_of),
                tuple(ROOT if parent[old] == ROOT else new[parent[old]] for old in order))


class _Builder:
    """Collects samples; dedupes trees by their canonical value."""

    def __init__(self, mutations, meta):
        self.mutations = mutations
        self.meta = meta
        self.trees, self.index, self.rows = [], {}, []

    def tree(self, tree):
        if tree not in self.index:
            self.index[tree] = len(self.trees)
            self.trees.append(tree)
        return self.index[tree]

    def add(self, chain, it, alpha, log_p_one, num_nodes, num_roots, tree_idx):
        self.rows.append((chain, it, alpha, log_p_one, num_nodes, num_roots, tree_idx))

    def build(self):
        rows = sorted(self.rows, key=lambda r: (r[0], r[1]))
        cols = list(zip(*rows))
        dt = (int, int, float, float, int, int, int)
        a = [np.asarray(c, dtype=t) for c, t in zip(cols, dt)]
        return Trace(self.mutations, *a, self.trees, self.meta)


def _expand(names_per_unit, clusters):
    """unit name -> list of mutation ids (identity without a cluster table)."""
    if not clusters:
        return {u: [u] for u in names_per_unit}
    return {u: sorted(clusters[u]) for u in names_per_unit}


def read_h5(path):
    import h5py

    def s(x):
        return x.decode() if isinstance(x, bytes) else str(x)

    with h5py.File(path, "r") as fh:
        dps = fh["data"]["datapoints"]
        unit = {int(g.attrs["idx"]): s(g.attrs["name"]) for g in dps.values()}
        clusters = {}
        if "clusters" in fh:
            for c, m in zip(fh["clusters"]["cluster_id"][()], fh["clusters"]["mutation_id"][()]):
                clusters.setdefault(s(c), []).append(s(m))
        members = _expand(unit.values(), clusters)
        mutations = sorted(m for ms in members.values() for m in ms)
        mpos = {m: i for i, m in enumerate(mutations)}
        meta = {"source": os.path.abspath(path), "format": "phyclone-h5",
                "rng_seed": s(fh["run_info"].attrs.get("rng_seed", "")),
                "samples": [s(x) for x in fh["samples"][()]]}
        b = _Builder(mutations, meta)
        by_group = {}
        for chain_grp in fh["trace"]["chains"].values():
            chain = int(chain_grp.attrs["chain_idx"])
            td = chain_grp["trace_data"]
            iters = td["iter"][()]
            cols = {k: td[k][()] for k in ("alpha", "log_p", "num_nodes", "num_roots")}
            for i, it in enumerate(iters):
                ref = chain_grp["trees"][f"tree_{it}"].attrs["tree_group"]
                g = fh[ref]
                if g.name not in by_group:
                    by_group[g.name] = b.tree(_h5_tree(g, unit, members, mpos))
                b.add(chain, int(it), cols["alpha"][i], cols["log_p"][i],
                      cols["num_nodes"][i], cols["num_roots"][i], by_group[g.name])
    return b.build()


def _h5_tree(g, unit, members, mpos):
    def s(x):
        return x.decode() if isinstance(x, bytes) else str(x)

    idx_of = {s(k): int(v) for k, v in zip(g["node_idx/str_nodes/keys"][()],
                                            g["node_idx/str_nodes/values"][()])}
    idx_of.update({s(k): int(v) for k, v in zip(g["node_idx/int_nodes/keys"][()],
                                                 g["node_idx/int_nodes/values"][()])})
    name_of = {v: k for k, v in idx_of.items()}
    root = idx_of["root"]
    parent = {}
    for p, c in g["graph"][()]:
        parent[name_of[int(c)]] = ROOT if int(p) == root else name_of[int(p)]
    node_of = [OUTLIER] * len(mpos)
    for sub in ("int_nodes", "str_nodes"):
        for k, dp_idx in zip(g[f"node_data/{sub}/keys"][()], g[f"node_data/{sub}/values"][()]):
            k = s(k)
            if k == "root":
                continue
            for d in dp_idx:
                for m in members[unit[int(d)]]:
                    node_of[mpos[m]] = OUTLIER if k == "-1" else k
    return canonical_tree(node_of, parent)


def _read_tsv(path, wanted, rename):
    with open(path) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)
    header = set(reader.fieldnames or ())
    # The Rust writer's meta.json maps column names to descriptions, not to other column names,
    # so a value only renames a column when it is a column of this file.
    names = {c: rename[c] if rename.get(c) in header else c for c in wanted}
    if rows:
        missing = [n for n in names.values() if n not in rows[0]]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
    return rows, names


def read_tsv_dir(path):
    with open(os.path.join(path, "meta.json")) as fh:
        meta = json.load(fh)
    meta = {**meta, "source": os.path.abspath(path), "format": "tsv-trace"}
    rename = meta.get("columns", {})
    outlier = meta.get("outlier_node")
    outlier = None if outlier is None else str(outlier)

    clusters = {}
    cpath = os.path.join(path, "clusters.tsv")
    if os.path.exists(cpath):
        rows, n = _read_tsv(cpath, ("cluster_id", "mutation_id"), rename.get("clusters.tsv", {}))
        for r in rows:
            clusters.setdefault(r[n["cluster_id"]], []).append(r[n["mutation_id"]])

    rows, n = _read_tsv(os.path.join(path, "assignments.tsv"), ASSIGN_COLS,
                        rename.get("assignments.tsv", {}))
    units = {r[n["mutation"]] for r in rows}
    # assignments may name clusters (expand them) or the mutations themselves
    members = _expand(units, clusters if clusters and units <= set(clusters) else {})
    mutations = sorted(m for ms in members.values() for m in ms)
    mpos = {m: i for i, m in enumerate(mutations)}
    node_of = {}
    for r in rows:
        tid, node = r[n["tree_id"]], r[n["node"]]
        arr = node_of.setdefault(tid, [None] * len(mutations))
        for m in members[r[n["mutation"]]]:
            arr[mpos[m]] = OUTLIER if node == outlier else node

    rows, n = _read_tsv(os.path.join(path, "trees.tsv"), TREE_COLS, rename.get("trees.tsv", {}))
    parent = {}
    for r in rows:
        p = r[n["parent"]]
        parent.setdefault(r[n["tree_id"]], {})[r[n["node"]]] = ROOT if p == "-1" else p

    b = _Builder(mutations, meta)
    tree_index = {}
    for tid, arr in node_of.items():
        if None in arr:
            raise ValueError(f"tree {tid}: mutation {mutations[arr.index(None)]} has no node")
        tree_index[tid] = b.tree(canonical_tree(arr, parent.get(tid, {})))

    rows, n = _read_tsv(os.path.join(path, "iterations.tsv"), ITER_COLS,
                        rename.get("iterations.tsv", {}))
    for r in rows:
        if r.get("phase", "sample") != "sample":
            continue
        b.add(int(r[n["chain"]]), int(r[n["iter"]]), float(r[n["alpha"]]),
              float(r[n["log_p_one"]]), int(r[n["num_nodes"]]), int(r[n["num_roots"]]),
              tree_index[r[n["tree_id"]]])
    return b.build()


def read_trace(path):
    """A Python trace.h5 (file, or a dir holding trace.h5) or a TSV trace dir (has meta.json)."""
    if os.path.isdir(path):
        if os.path.exists(os.path.join(path, "meta.json")):
            return read_tsv_dir(path)
        path = os.path.join(path, "trace.h5")
    return read_h5(path)


def write_tsv_dir(trace, path, permute_seed=None):
    """Write a Trace in the TSV layout. permute_seed shuffles mutation labels (a broken trace)."""
    os.makedirs(path, exist_ok=True)
    names = list(trace.mutations)
    if permute_seed is not None:
        np.random.default_rng(permute_seed).shuffle(names)
    meta = {"format_version": 1, "writer": "phyclone_rs/v3/trace_io.py",
            "converted_from": trace.meta.get("source"), "rng_seed": trace.meta.get("rng_seed"),
            "permute_seed": permute_seed}
    if any(OUTLIER in t.node_of for t in trace.trees):
        meta["outlier_node"] = "outlier"
    with open(os.path.join(path, "meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    with open(os.path.join(path, "iterations.tsv"), "w") as fh:
        fh.write("chain\titer\talpha\tlog_p\tlog_p_one\tnum_nodes\tnum_outliers\tnum_roots\ttree_id\n")
        for i in range(len(trace)):
            t = trace.trees[trace.tree_idx[i]]
            a, lp = float(trace.alpha[i]), float(trace.log_p_one[i])
            fh.write(f"{trace.chain[i]}\t{trace.iter[i]}\t{a!r}\t{lp!r}\t"
                     f"{lp!r}\t{trace.num_nodes[i]}\t{t.node_of.count(OUTLIER)}\t"
                     f"{trace.num_roots[i]}\t{trace.tree_idx[i]}\n")
    with open(os.path.join(path, "trees.tsv"), "w") as fh:
        fh.write("tree_id\tnode\tparent\tlog_prior\n")
        for k, t in enumerate(trace.trees):
            for node, p in enumerate(t.parent):
                fh.write(f"{k}\t{node}\t{p}\tnan\n")
    with open(os.path.join(path, "assignments.tsv"), "w") as fh:
        fh.write("tree_id\tmutation\tnode\n")
        for k, t in enumerate(trace.trees):
            for m, node in zip(names, t.node_of):
                fh.write(f"{k}\t{m}\t{node if node != OUTLIER else 'outlier'}\n")


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Convert a trace (h5 or TSV dir) to a TSV trace dir.")
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--permute-seed", type=int, help="shuffle mutation labels (a broken trace)")
    a = ap.parse_args()
    write_tsv_dir(read_trace(a.src), a.dst, a.permute_seed)


if __name__ == "__main__":
    main()
