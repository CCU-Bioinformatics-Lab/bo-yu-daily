"""C4 pair-term log evidence of the truth tree against alternative trees, with no MCMC.

Every SNV is placed at its truth origin clone; the alternative trees move clones only. The
difference term(truth) - term(alternative) is how strongly the pair term alone prefers the
truth (> 0) or the alternative (< 0). Pairs with an SNV lost in some clone are kept: C4 sees them.

Usage: python3 tools/c4_pair_evidence.py SIM_DIR [SIM_DIR ...] [--eps 0.01,0.03]
Alternatives for the stress tree (truth C1 -> {C2 -> C4, C3}):
  linear  C3 under C4 (P2)        c3_under_c2  C3 under C2
same_vs_split: over eligible pairs of one truth clone, sum of score(same) minus the better of
score(ancestor) and score(descendant); < 0 means the pair term prefers to split the clone.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phyclone_pairs import PairTable  # noqa: E402

ALT = {"linear": {"C2": "C1", "C3": "C4", "C4": "C2"},
       "c3_under_c2": {"C2": "C1", "C3": "C2", "C4": "C2"}}


def ancestors(parent):
    out = {}
    for c in parent:
        a, x = set(), c
        while parent.get(x) not in (None, "root"):
            x = parent[x]
            a.add(x)
        out[c] = a
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sims", nargs="+")
    ap.add_argument("--eps", default="0.001,0.01,0.03,0.1")
    a = ap.parse_args()
    print("sim\teps\tpairs\t" + "\t".join(f"truth_minus_{k}" for k in ALT) + "\tsame_pairs\tsame_vs_split")
    for sim in a.sims:
        with open(os.path.join(sim, "truth/truth.tsv")) as fh:
            node_of = {r["mutation_id"]: r["origin_clone"] for r in csv.DictReader(fh, delimiter="\t")}
        with open(os.path.join(sim, "truth/truth_tree.tsv")) as fh:
            truth = {r["clone"]: r["parent"] for r in csv.DictReader(fh, delimiter="\t")}
        i = os.path.join(sim, "input")
        for eps in map(float, a.eps.split(",")):
            t = PairTable.from_files(f"{i}/pairs.tsv", f"{i}/data_hp.tsv", f"{i}/segments.tsv", eps)
            base = t.term(node_of, ancestors(truth))
            diff = [base - t.term(node_of, ancestors({**truth, **alt})) for alt in ALT.values()]
            same = [k for k, (x, y) in enumerate(zip(t.mut_i, t.mut_j)) if node_of[x] == node_of[y]]
            split = (t.scores[same, 0] - t.scores[same, 1:3].max(1)).sum()
            print(f"{os.path.basename(sim.rstrip('/'))}\t{eps}\t{len(t)}\t" +
                  "\t".join(f"{d:.1f}" for d in diff) + f"\t{len(same)}\t{split:.1f}")


if __name__ == "__main__":
    main()
