"""Truth compatibility of PhyClone posterior trees, for the C4 robustness test.

Each tree is reduced to the relation of every pair of SNV roles (majority clone of each role):
same, ancestor, descendant or branch. A tree is exact when every pair has its truth relation.
It is truth-compatible when it is the truth tree after merging some clones into their parents
(one bulk sample may not resolve a parent-child pair, e.g. C1/C2 or C2/C4 of the stress tree).
A wrong order or a wrong branch point (the linear tree, C3 under C4) is never compatible.
Roles lost in some clone (truth/genome.json "lost") are left out: their placement is A2's job,
not C4's.

  exact          posterior fraction of exact trees
  compat         posterior fraction of truth-compatible trees
  map_compat     the MAP tree (map_table.tsv + map_tree.nwk) is truth-compatible
  max_wrong      largest posterior of one incompatible role-level tree
  top_class      role-level tree with the largest posterior, and its posterior

Usage: python3 tools/summarize_c4_robustness.py [--roles s3,s4,...] TRUTH_DIR RUN_DIR [...]
--roles keeps only those roles (e.g. the roles of the segments where C4 has eligible pairs).
"""
import csv
import io
import json
import os
import sys
import tarfile
from collections import Counter, defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_hp_truth_phyclone import newick_parents  # noqa: E402
from summarize_hp_truth_topologies import is_descendant, majority  # noqa: E402


def relation(x, y, parent):
    if x == y:
        return "same"
    if is_descendant(y, x, parent):
        return "ancestor"
    if is_descendant(x, y, parent):
        return "descendant"
    return "branch"


def load_truth(truth, keep=None):
    with open(os.path.join(truth, "truth.tsv")) as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    with open(os.path.join(truth, "truth_tree.tsv")) as fh:
        parent = {r["clone"]: r["parent"] for r in csv.DictReader(fh, delimiter="\t")}
    with open(os.path.join(truth, "genome.json")) as fh:
        lost = {r for rs in json.load(fh)["lost"].values() for r in rs}
    role = {r["mutation_id"]: r["role"] for r in rows}
    clone = {r["role"]: r["origin_clone"] for r in rows}
    roles = sorted(set(clone) - lost)
    if keep:
        roles = [r for r in roles if r in keep]
    edges = [c for c, p in parent.items() if p != "root"]
    allowed = []  # role-pair relations of every contraction; [0] is the uncontracted truth
    for k in range(len(edges) + 1):
        for merged in combinations(edges, k):
            rep = {}
            for c in parent:  # truth_tree.tsv lists parents first
                rep[c] = rep[parent[c]] if c in merged else c
            par = {rep[c]: rep[parent[c]] for c in parent if c not in merged and parent[c] != "root"}
            allowed.append({(a, b): relation(rep[clone[a]], rep[clone[b]], par)
                            for a, b in combinations(roles, 2)})
    return role, roles, allowed


def classify(clone_of, parent, role, roles, allowed):
    """(exact, compatible, role-level key) of one tree."""
    by_role = defaultdict(list)
    for mid, c in clone_of.items():
        by_role[role[mid]].append(c)
    node = {r: majority(by_role[r]) for r in roles}
    got = {(a, b): relation(node[a], node[b], parent) for a, b in combinations(roles, 2)}
    exact, ok = got == allowed[0], got in allowed
    members = defaultdict(set)
    for r, n in node.items():
        members[n].add(r)
    label = {n: "+".join(sorted(rs)) for n, rs in members.items()}

    def up(n):  # nearest ancestor that holds a kept role
        while n in parent:
            n = parent[n]
            if n in label:
                return label[n]
        return "root"
    key = ";".join(sorted(f"{label[n]}<{up(n)}" for n in members))
    return exact, ok, key


def summarize(truth, run, keep=None):
    role, roles, allowed = load_truth(truth, keep)
    with open(os.path.join(run, "topology_report.tsv")) as fh:
        count = {r["topology_id"]: int(r["count"]) for r in csv.DictReader(fh, delimiter="\t")}
    tables, trees = {}, {}
    with tarfile.open(os.path.join(run, "topologies.tar.gz"), "r|gz") as tar:
        for m in tar:
            if not m.isfile():
                continue
            tid = m.name.split("/")[0]
            text = tar.extractfile(m).read().decode()
            if m.name.endswith("_results_table.tsv"):
                clone_of = {}
                for r in csv.DictReader(io.StringIO(text), delimiter="\t"):
                    clone_of.setdefault(r["mutation_id"], r["clone_id"])
                tables[tid] = clone_of
            elif m.name.endswith(".nwk"):
                trees[tid] = newick_parents(text)
    classes, exact, compat, weight = Counter(), 0, 0, 0
    bad = set()
    for tid, clone_of in tables.items():
        ex, ok, key = classify(clone_of, trees[tid], role, roles, allowed)
        classes[key] += count[tid]
        weight += count[tid]
        exact += count[tid] * ex
        compat += count[tid] * ok
        if not ok:
            bad.add(key)
    with open(os.path.join(run, "map_table.tsv")) as fh:
        map_of = {}
        for r in csv.DictReader(fh, delimiter="\t"):
            map_of.setdefault(r["mutation_id"], r["clone_id"])
    with open(os.path.join(run, "map_tree.nwk")) as fh:
        _, map_ok, _ = classify(map_of, newick_parents(fh.read()), role, roles, allowed)
    top, top_w = classes.most_common(1)[0]
    return {"exact": exact / weight, "compat": compat / weight, "map_compat": int(map_ok),
            "max_wrong": max((classes[k] for k in bad), default=0) / weight,
            "top_class": top, "top_post": top_w / weight}


def main():
    args, keep = sys.argv[1:], None
    if args[0] == "--roles":
        keep, args = set(args[1].split(",")), args[2:]
    truth, runs = args[0], args[1:]
    cols = ["exact", "compat", "map_compat", "max_wrong", "top_post", "top_class"]
    print("\t".join(["run"] + cols))
    for run in runs:
        r = summarize(truth, run, keep)
        print("\t".join([os.path.basename(run.rstrip("/"))] +
                        [f"{r[c]:.3f}" if isinstance(r[c], float) else str(r[c]) for c in cols]))


if __name__ == "__main__":
    main()
