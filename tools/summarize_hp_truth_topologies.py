"""Posterior summary of PhyClone topologies for the designed HP-aware truth tree.

Reads every topology in RUN_DIR/topologies.tar.gz (from `phyclone topology-report -t`) and
weights it by its `count` in RUN_DIR/topology_report.tsv. Each sampled tree is reduced to the
questions the truth tree was built to ask:

  n_clones        clones in the tree (outlier node excluded)
  c1c2_merged     s3 (C1) and s4 (C2) majority clones are the same
  c3_under_c4     the clone holding most s6/s7 (C3) is a descendant of the clone holding most
                  s5 (C4); truth = False (C3 is a sibling of C2)
  c3_child_of_trunk  the C3 clone's parent is the s3 (C1) clone; matches the truth shape once
                  C1 and C2 are merged
  c2_c4_correct   C2 (s4) clone hangs off the trunk and C4 (s5) clone hangs off C2; needs
                  C1 and C2 to be separate clones
  s10_fake_above_c3  s10 forms its own clone (no s3/s4/s6 majority there) that is the parent
                  of the C3 clone: a spurious ancestor created by the cnLOH loss
  s10_with_c3     most s10 replicates sit in the C3 clone
  s10_in_trunk / s2_in_trunk  fraction of s10 / s2 replicates in the s3 (C1) clone; truth = 1
  s2_split        s2 replicates spread over >1 clone
  loss_outliers   s2 + s10 replicates assigned to the outlier node

Usage: python3 tools/summarize_hp_truth_topologies.py INPUT_DIR RUN_DIR [RUN_DIR ...]
Prints one row per run, weighted fractions over all posterior samples.
"""
import csv
import io
import os
import sys
import tarfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_hp_truth_phyclone import newick_parents  # noqa: E402


def majority(clones):
    return Counter(clones).most_common(1)[0][0]


def is_descendant(node, anc, parent):
    while node in parent:
        node = parent[node]
        if node == anc:
            return True
    return False


def summarize(inp, run):
    with open(os.path.join(inp, "truth.tsv")) as fh:
        role = {r["mutation_id"]: r["role"] for r in csv.DictReader(fh, delimiter="\t")}
    with open(os.path.join(run, "topology_report.tsv")) as fh:
        count = {r["topology_id"]: int(r["count"]) for r in csv.DictReader(fh, delimiter="\t")}

    tables, trees = {}, {}
    # stream mode: one sequential pass (random access on .tar.gz re-decompresses per member)
    with tarfile.open(os.path.join(run, "topologies.tar.gz"), "r|gz") as tar:
        for m in tar:
            if not m.isfile():
                continue
            tid = m.name.split("/")[0]
            text = tar.extractfile(m).read().decode()
            if m.name.endswith("_results_table.tsv"):
                tables[tid] = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
            elif m.name.endswith(".nwk"):
                trees[tid] = newick_parents(text)

    tot = Counter()
    n_clone_dist = Counter()
    weight = 0
    for tid, rows in tables.items():
        w = count[tid]
        weight += w
        parent = trees[tid]
        # one row per mutation x sample; a mutation has one clone, so keep the first row
        clone_of = {}
        for r in rows:
            clone_of.setdefault(r["mutation_id"], r["clone_id"])
        by_role = defaultdict(list)
        for mid, c in clone_of.items():
            by_role[role[mid]].append(c)
        clones = set(clone_of.values()) - {"-1"}
        n_clone_dist[len(clones)] += w
        c3 = majority(by_role["s6"] + by_role["s7"])
        c4 = majority(by_role["s5"])
        tot["c1c2_merged"] += w * (majority(by_role["s3"]) == majority(by_role["s4"]))
        tot["c3_under_c4"] += w * is_descendant(c3, c4, parent)
        tot["c3_child_of_trunk"] += w * (parent.get(c3) == majority(by_role["s3"]))
        trunk, c2 = majority(by_role["s3"]), majority(by_role["s4"])
        c10 = majority(by_role["s10"])
        tot["c2_c4_correct"] += w * (c2 != trunk and parent.get(c2) == trunk and parent.get(c4) == c2)
        tot["s10_fake_above_c3"] += w * (c10 not in (trunk, c2, c3) and parent.get(c3) == c10)
        tot["s10_with_c3"] += w * (majority(by_role["s10"]) == c3)
        tot["s10_in_trunk"] += w * sum(c == trunk for c in by_role["s10"]) / len(by_role["s10"])
        tot["s2_in_trunk"] += w * sum(c == trunk for c in by_role["s2"]) / len(by_role["s2"])
        tot["s2_split"] += w * (len(set(by_role["s2"])) > 1)
        tot["loss_outliers"] += w * sum(c == "-1" for c in by_role["s2"] + by_role["s10"])
        tot["any_outlier"] += w * ("-1" in clone_of.values())
    res = {k: v / weight for k, v in tot.items()}
    res["n_samples"] = weight
    res["n_unique"] = len(tables)
    res["n_clones"] = ",".join(f"{k}:{v / weight:.2f}" for k, v in sorted(n_clone_dist.items()))
    return res


def main():
    inp, runs = sys.argv[1], sys.argv[2:]
    cols = ["run", "n_samples", "n_unique", "n_clones", "c1c2_merged", "c3_under_c4",
            "c3_child_of_trunk", "c2_c4_correct", "s10_fake_above_c3", "s10_with_c3",
            "s10_in_trunk", "s2_in_trunk", "s2_split", "loss_outliers", "any_outlier"]
    print("\t".join(cols))
    for run in runs:
        r = summarize(inp, run)
        print("\t".join([os.path.basename(run.rstrip("/"))] +
                        [str(r[c]) if c in ("n_samples", "n_unique", "n_clones") else f"{r[c]:.3f}"
                         for c in cols[1:]]))


if __name__ == "__main__":
    main()
