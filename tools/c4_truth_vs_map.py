"""Score the truth tree against the MAP tree under the exact model a PhyClone run sampled from.

If the truth tree scores higher than the MAP tree, the model prefers the truth and the run
failed to find it (a sampling problem). If it scores lower, the model itself prefers the wrong
tree on this data (a model or data problem). Scores are log_p_one, the quantity PhyClone stores
in the trace and maximises for the MAP, split into FSCRP prior, data log likelihood and the C4
pair term, all at the MAP sample's alpha.

The datapoints come from trace.h5, so the SNV likelihoods (base or A2) are the ones the run
used. The C4 options must match the run; the MAP row recomputes the stored log_p as a check
(`check` column = recomputed - stored, ~0 when the options match). `compat` is the role-level
truth compatibility of summarize_c4_robustness.py (lost roles left out), so an _opt row that moved
a role's majority to another clone is marked 0.

Truth tree: every SNV at its truth origin clone (truth/truth.tsv), clone parents from
truth/truth_tree.tsv; clones with no SNVs are contracted into their parent. --merge C1+C2 adds
a variant with those clones merged into the first one (repeatable). --contract-all adds every
contraction of the truth tree (each subset of parent-child edges merged), i.e. every tree that is
still compatible with the truth.

The exact truth placement can be unfair: a model with no loss scenario (base) cannot fit a lost
SNV at its origin clone. --opt adds, for each truth variant, a row `<name>_opt`: the same
topology with each SNV moved to its best-scoring node (coordinate ascent until no move helps).
A move is not allowed if it empties a clone or makes the tree role-level incompatible, so every
_opt row is compatible. It is a lower bound on the best compatible score of that topology (the
search is local).

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
    tools/c4_truth_vs_map.py SIM_DIR RUN_DIR [--c4 eps|error|none] [--eps 0.01] [--weight 1]
    [--error 0.004] [--hp-uncertain] [--merge C1+C2] [--contract-all] [--opt]
"""
import argparse
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phyclone_pairs import PairTable, install, tree_assignment  # noqa: E402
from summarize_c4_robustness import classify, load_truth  # noqa: E402

COLUMNS = ("run", "tree", "alpha", "n_nodes", "compat", "log_p_one", "prior", "data_ll",
           "pair_term", "minus_map", "check")


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def contractions(parent):
    """Every merge list obtained by contracting a subset of the clone tree's edges."""
    import itertools

    edges = [(c, p) for c, p in sorted(parent.items()) if p != "root"]
    out = []
    for k in range(1, len(edges) + 1):
        for subset in itertools.combinations(edges, k):
            top = {c: c for c in parent}

            def find(x):
                while top[x] != x:
                    x = top[x]
                return x

            for c, p in subset:
                top[find(c)] = find(p)
            groups = {}
            for c in sorted(parent):
                groups.setdefault(find(c), []).append(c)
            out.append([[g] + [c for c in members if c != g]
                        for g, members in sorted(groups.items()) if len(members) > 1])
    return out


def map_entry(trace):
    from phyclone.utils.load_hdf5 import load_chain_trace_data_df

    df = load_chain_trace_data_df(trace)
    row = df.loc[df["log_p"].idxmax()]
    return int(row["chain_num"]), int(row["iter"]), float(row["alpha"]), float(row["log_p"])


def build_tree(datapoints, origin, parent, merge=()):
    """PhyClone Tree with each datapoint at origin[name]; parent: clone -> parent clone or root."""
    from phyclone.tree import Tree

    rep = {c: c for c in parent}
    for group in merge:
        for c in group[1:]:
            rep[c] = group[0]
    data = {}
    for dp in datapoints:
        data.setdefault(rep[origin[dp.name]], []).append(dp)

    def kept_parent(c):  # nearest ancestor (after merging) that holds data, or "root"
        p = parent[c]
        while p != "root" and (rep[p] == rep[c] or rep[p] not in data):
            p = parent[p]
        return "root" if p == "root" else rep[p]

    children = {}
    for c in {rep[c] for c in parent} & set(data):
        children.setdefault(kept_parent(c), []).append(c)

    first = next(iter(datapoints))
    tree = Tree(first.value.shape)

    def make(c):
        return tree.create_root_node(children=[make(k) for k in sorted(children.get(c, []))],
                                     data=data[c])

    for c in sorted(children.get("root", [])):
        make(c)
    return tree


def optimise(datapoints, origin, parent, merge, alpha, table, truth_roles, max_passes=10):
    """Coordinate ascent over SNV placements on a fixed truth topology; returns (tree, moves)."""
    rep = {c: c for c in parent}
    for group in merge:
        for c in group[1:]:
            rep[c] = group[0]
    place = {dp.name: rep[origin[dp.name]] for dp in datapoints}
    nodes = sorted(set(place.values()))
    sizes = {c: sum(v == c for v in place.values()) for c in nodes}

    def total(pl):
        tree = build_tree(datapoints, pl, parent, merge)
        return sum(score(tree, alpha, table)) if is_compat(tree, truth_roles) else -np.inf

    best, moves = total(place), 0
    for _ in range(max_passes):
        moved = False
        for dp in datapoints:
            here = place[dp.name]
            if sizes[here] == 1:
                continue
            for c in nodes:
                if c == here:
                    continue
                trial = {**place, dp.name: c}
                t = total(trial)
                if t > best + 1e-9:
                    best, place, moved, moves = t, trial, True, moves + 1
                    sizes[here] -= 1
                    sizes[c] += 1
                    here = c
        if not moved:
            break
    return build_tree(datapoints, place, parent, merge), moves


def is_compat(tree, truth_roles):
    node_of, _ = tree_assignment(tree)
    root = tree.root_node_name
    parent = {}
    for n in set(node_of.values()):
        p = tree.get_parent(n)
        parent[n] = "root" if p == root else p
    return int(classify(node_of, parent, *truth_roles)[1])


def score(tree, alpha, table):
    from phyclone.tree.distributions import FSCRPDistribution

    prior = FSCRPDistribution(alpha).log_p_one(tree)
    data_ll = float(tree.data_log_likelihood[:, -1].sum())
    pair = table.term(*tree_assignment(tree)) if table is not None else 0.0
    return prior, data_ll, pair


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sim")
    ap.add_argument("run")
    ap.add_argument("--c4", choices=["eps", "error", "none"], default="eps")
    ap.add_argument("--eps", type=float, default=0.01)
    ap.add_argument("--weight", type=float, default=1.0)
    ap.add_argument("--error", type=float, default=0.004)
    ap.add_argument("--hp-uncertain", action="store_true", help="with --c4 error")
    ap.add_argument("--merge", action="append", default=[], help="e.g. C1+C2")
    ap.add_argument("--contract-all", action="store_true", help="add every truth contraction")
    ap.add_argument("--opt", action="store_true", help="add <truth variant>_opt rows")
    ap.add_argument("--no-header", action="store_true")
    a = ap.parse_args()

    from phyclone.tree.distributions import FSCRPDistribution, TreeJointDistribution
    from phyclone.utils.load_hdf5 import build_datapoints_dict_from_trace, build_map_tree_from_trace

    trace = os.path.join(a.run, "trace.h5")
    i = os.path.join(a.sim, "input")
    table = None
    if a.c4 != "none":
        table = PairTable.from_files(f"{i}/pairs.tsv", f"{i}/data_hp.tsv", f"{i}/segments.tsv",
                                     a.eps, a.weight, a.error if a.c4 == "error" else None,
                                     a.hp_uncertain)
        install(table)

    chain, it, alpha, stored = map_entry(trace)
    datapoints = build_datapoints_dict_from_trace(trace)
    origin = {r["mutation_id"]: r["origin_clone"] for r in read_tsv(f"{a.sim}/truth/truth.tsv")}
    parent = {r["clone"]: "root" if r["parent"] == "N" else r["parent"]
              for r in read_tsv(f"{a.sim}/truth/truth_tree.tsv")}

    dps = list(datapoints.values())
    truth_roles = load_truth(f"{a.sim}/truth")
    trees = [("map", build_map_tree_from_trace(trace, chain, it, datapoints))]
    variants = [("truth", [])] + [(f"truth_merge_{m}", [m.split("+")]) for m in a.merge]
    if a.contract_all:
        variants += [("truth_merge_" + ",".join("+".join(g) for g in merge), merge)
                     for merge in contractions(parent)]
    for name, merge in variants:
        trees.append((name, build_tree(dps, origin, parent, merge)))
        if a.opt:
            trees.append((f"{name}_opt",
                          optimise(dps, origin, parent, merge, alpha, table, truth_roles)[0]))

    joint = TreeJointDistribution(FSCRPDistribution(alpha))
    rows, map_total = [], None
    for name, tree in trees:
        prior, data_ll, pair = score(tree, alpha, table)
        total = prior + data_ll + pair
        if map_total is None:
            map_total = total
        check = total - stored if name == "map" else np.nan
        # the patched joint distribution must agree with the hand-summed parts
        assert abs(joint.log_p_one(tree) - total) < 1e-6, (name, joint.log_p_one(tree), total)
        rows.append((os.path.basename(a.run.rstrip("/")), name, f"{alpha:.4g}",
                     tree.get_number_of_nodes(), is_compat(tree, truth_roles), f"{total:.2f}", f"{prior:.2f}", f"{data_ll:.2f}",
                     f"{pair:.2f}", f"{total - map_total:.2f}", f"{check:.2g}"))
    if not a.no_header:
        print("sim\t" + "\t".join(COLUMNS))
    for r in rows:
        print(os.path.basename(a.sim.rstrip("/")) + "\t" + "\t".join(map(str, r)))


if __name__ == "__main__":
    main()
