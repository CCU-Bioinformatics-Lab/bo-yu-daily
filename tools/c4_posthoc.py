"""Post-hoc tree selection with read co-occurrence pairs, on a finished PhyClone run (no MCMC).

The run's sampled trees (topology_report.tsv counts + topologies.tar.gz) are a sample of the
posterior without C4. Two ways to use the pairs afterwards:

  soft  importance reweighting: weight = count x exp(C4 pair term). In theory this targets the
        same posterior as C4 inside the model, but only over trees the run already sampled.
  hard  pair calls with read-count thresholds, as in Sakamoto 2022 (B04): a pair is called
          branch      n10 >= k and n01 >= k and n11 <= t
          i before j  n11 >= k and n10 >= k and n01 <= t   (i's node is an ancestor of j's)
          j before i  n11 >= k and n01 >= k and n10 <= t
        and is not called otherwise. A tree violates a call when the relation of the two
        nodes differs. Trees with the fewest violations are kept, with their counts.

Each output dir looks like a run dir (topology_report.tsv with new integer counts, a link to
topologies.tar.gz, map_table.tsv / map_tree.nwk of the heaviest tree), so the summarizers read
it as is. posthoc.json has the ESS (soft) or violation counts (hard).

Usage: python tools/c4_posthoc.py RUN_DIR INPUT_DIR OUT_PREFIX [--eps 0.01] [--min-reads 3]
       [--tol 1]   -> writes OUT_PREFIX_soft/ and OUT_PREFIX_hard/
"""
import argparse
import csv
import io
import json
import os
import sys
import tarfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_hp_truth_phyclone import newick_parents  # noqa: E402
from phyclone_pairs import PairTable  # noqa: E402

SCALE = 1_000_000  # total integer count of a reweighted posterior


def eligible_pairs(inp, eps):
    """Eligible pairs (phyclone_pairs rules) with their counts."""
    table = PairTable.from_files(f"{inp}/pairs.tsv", f"{inp}/data_hp.tsv", f"{inp}/segments.tsv", eps)
    pairs = pd.read_csv(f"{inp}/pairs.tsv", sep="\t")
    key = set(zip(table.mut_i, table.mut_j))
    snv = pd.read_csv(f"{inp}/data_hp.tsv", sep="\t").drop_duplicates("mutation_id").set_index(
        "mutation_id")
    hp = snv.snv_hp.reindex(pairs.mutation_i).to_numpy()
    ok = [(i, j) in key and h == hap for i, j, h, hap in
          zip(pairs.mutation_i, pairs.mutation_j, hp, pairs.hap)]
    return table, pairs[ok].reset_index(drop=True)


def calls(pairs, k, t):
    """Allowed relation (RELATIONS index) per called pair."""
    out = []
    for r in pairs.itertuples():
        if r.n10 >= k and r.n01 >= k and r.n11 <= t:
            out.append((r.mutation_i, r.mutation_j, 3))
        elif r.n11 >= k and r.n10 >= k and r.n01 <= t:
            out.append((r.mutation_i, r.mutation_j, 1))
        elif r.n11 >= k and r.n01 >= k and r.n10 <= t:
            out.append((r.mutation_i, r.mutation_j, 2))
    return out


def relation(x, y, ancestors):
    if x == y:
        return 0
    if x in ancestors[y]:
        return 1
    if y in ancestors[x]:
        return 2
    return 3


def load_run(run):
    with open(os.path.join(run, "topology_report.tsv")) as fh:
        count = {r["topology_id"]: int(r["count"]) for r in csv.DictReader(fh, delimiter="\t")}
    tables, trees, raw = {}, {}, {}
    with tarfile.open(os.path.join(run, "topologies.tar.gz"), "r|gz") as tar:
        for m in tar:
            if not m.isfile():
                continue
            tid = m.name.split("/")[0]
            text = tar.extractfile(m).read().decode()
            if m.name.endswith("_results_table.tsv"):
                tables[tid] = text
            elif m.name.endswith(".nwk"):
                trees[tid] = newick_parents(text)
                raw[tid] = text
    return count, tables, trees, raw


def assignment(table_text, parent):
    node_of = {}
    for r in csv.DictReader(io.StringIO(table_text), delimiter="\t"):
        if r["clone_id"] != "-1":
            node_of.setdefault(r["mutation_id"], r["clone_id"])
    ancestors = {}
    for n in set(node_of.values()):
        a, x = set(), n
        while x in parent and parent[x] != "root":
            x = parent[x]
            a.add(x)
        ancestors[n] = a
    return node_of, ancestors


def write_run(out, run, weights, tables, raw, info):
    os.makedirs(out, exist_ok=True)
    tids = list(weights)
    w = np.array([weights[t] for t in tids], float)
    n = np.round(w / w.sum() * SCALE).astype(int)
    with open(os.path.join(out, "topology_report.tsv"), "w") as fh:
        fh.write("topology_id\tcount\n")
        fh.writelines(f"{t}\t{c}\n" for t, c in zip(tids, n))
    link = os.path.join(out, "topologies.tar.gz")
    if os.path.lexists(link):
        os.remove(link)
    os.symlink(os.path.relpath(os.path.join(run, "topologies.tar.gz"), out), link)
    top = tids[int(np.argmax(w))]
    with open(os.path.join(out, "map_tree.nwk"), "w") as fh:
        fh.write(raw[top])
    with open(os.path.join(out, "map_table.tsv"), "w") as fh:
        fh.write(tables[top])
    with open(os.path.join(out, "posthoc.json"), "w") as fh:
        json.dump({**info, "map_topology": top}, fh, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("input")
    ap.add_argument("out_prefix")
    ap.add_argument("--eps", type=float, default=0.01)
    ap.add_argument("--min-reads", type=int, default=3)
    ap.add_argument("--tol", type=int, default=1)
    a = ap.parse_args()

    table, pairs = eligible_pairs(a.input, a.eps)
    called = calls(pairs, a.min_reads, a.tol)
    count, tables, trees, raw = load_run(a.run)
    term, viol = {}, {}
    for tid in count:
        node_of, anc = assignment(tables[tid], trees[tid])
        term[tid] = table.term(node_of, anc)
        viol[tid] = sum(relation(node_of[i], node_of[j], anc) != want for i, j, want in called
                        if i in node_of and j in node_of)

    tids = list(count)
    logw = np.array([np.log(count[t]) + term[t] for t in tids])
    w = np.exp(logw - logw.max())
    p = w / w.sum()
    write_run(f"{a.out_prefix}_soft", a.run, dict(zip(tids, w)), tables, raw,
              {"method": "soft", "eps": a.eps, "eligible_pairs": len(table),
               "n_topologies": len(tids), "n_samples": sum(count.values()),
               "ess": float(1 / (p ** 2).sum()), "max_weight": float(p.max())})

    best = min(viol.values())
    kept = {t: count[t] * (viol[t] == best) for t in tids}  # every topology listed, for the summarizers
    tot = sum(count.values())
    write_run(f"{a.out_prefix}_hard", a.run, kept, tables, raw,
              {"method": "hard", "min_reads": a.min_reads, "tol": a.tol,
               "called_pairs": len(called),
               "called_by_relation": {r: sum(c == i for *_, c in called)
                                      for i, r in enumerate(("same", "ancestor", "descendant",
                                                             "branch")) if i},
               "min_violations": best, "kept_topologies": sum(v > 0 for v in kept.values()),
               "kept_fraction": sum(kept.values()) / tot,
               "zero_violation_fraction": sum(c for t, c in count.items() if viol[t] == 0) / tot})
    print(json.dumps({"soft_ess": float(1 / (p ** 2).sum()), "called": len(called),
                      "min_violations": best, "kept_fraction": sum(kept.values()) / tot}))


if __name__ == "__main__":
    main()
