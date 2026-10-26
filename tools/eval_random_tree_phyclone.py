"""Score PhyClone MAP results on longbulksim random-tree simulations.

For each SIM_DIR/<name>/ with truth/ (longbulksim output) and RUN/map_table.tsv + RUN/map_tree.nwk,
computes against the origin clone of each SNV:
  n_clones_true / n_clones_inferred   clones that hold >= 1 SNV
  n_clones_detectable                 true clones whose SNVs have a median expected alt count
                                      (vaf_expected x observed depth) >= 3
  ari, v_measure                      clustering of SNVs into clones
  relation_acc                        SNV pairs whose relation (same / ancestor / descendant /
                                      branch) is the same in the inferred and true trees
  recall_<relation>                   the same, per true relation
  balanced_relation_acc               mean of the recalls over relations present in the truth
  ccf_mae                             |inferred clone CCF - true origin CCF| per SNV
Truth features (purity, depth, loss fraction, true linearity) come from the spec and truth files.

Usage: python3 tools/eval_random_tree_phyclone.py SIM_DIR OUT.tsv [RUN]   (RUN defaults to "run")
"""
import csv
import math
import os
import sys
from collections import Counter
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_hp_truth_phyclone import newick_parents  # noqa: E402

RELATIONS = ("same", "ancestor", "descendant", "branch")


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def ari(a, b):
    n = len(a)
    comb = lambda x: x * (x - 1) / 2
    nij = sum(comb(v) for v in Counter(zip(a, b)).values())
    ai = sum(comb(v) for v in Counter(a).values())
    bj = sum(comb(v) for v in Counter(b).values())
    exp = ai * bj / comb(n)
    top = (ai + bj) / 2
    return 1.0 if top == exp else (nij - exp) / (top - exp)


def v_measure(truth, pred):
    n = len(truth)
    H = lambda xs: -sum(v / n * math.log(v / n) for v in Counter(xs).values())
    def cond(x, y):  # H(x | y)
        cy = Counter(y)
        return -sum(v / n * math.log(v / cy[k[1]]) for k, v in
                    Counter(zip(x, y)).items())
    hc, hk = H(truth), H(pred)
    h = 1.0 if hc == 0 else 1 - cond(truth, pred) / hc
    c = 1.0 if hk == 0 else 1 - cond(pred, truth) / hk
    return 0.0 if h + c == 0 else 2 * h * c / (h + c)


def ancestry(parent):
    def up(n):
        out = []
        while n in parent:
            n = parent[n]
            out.append(n)
        return out
    return {n: set(up(n)) for n in set(parent) | set(parent.values())}


def relation(x, y, anc):
    if x == y:
        return "same"
    if x in anc.get(y, ()):
        return "ancestor"
    if y in anc.get(x, ()):
        return "descendant"
    return "branch"


def score(sim, run):
    # SNVs a simulated caller missed (detected = 0) are not in the method input
    truth = {r["mutation_id"]: r for r in read_tsv(os.path.join(sim, "truth/truth.tsv"))
             if r.get("detected", "1") == "1"}
    tree = read_tsv(os.path.join(sim, "truth/truth_tree.tsv"))
    t_parent = {r["clone"]: r["parent"] for r in tree if r["parent"] != "root"}
    table = {r["mutation_id"]: r for r in read_tsv(os.path.join(sim, run, "map_table.tsv"))}
    with open(os.path.join(sim, run, "map_tree.nwk")) as fh:
        p_parent = {k: v for k, v in newick_parents(fh.read()).items() if v != "root"}
    data = {r["mutation_id"]: r for r in read_tsv(os.path.join(sim, "input/data.tsv"))}
    ids = sorted(truth)
    exp_alt = {}
    for m in ids:
        dp = int(data[m]["ref_counts"]) + int(data[m]["alt_counts"])
        exp_alt.setdefault(truth[m]["origin_clone"], []).append(
            float(truth[m]["vaf_expected"]) * dp)
    median = lambda xs: sorted(xs)[len(xs) // 2]
    t_lab = [truth[m]["origin_clone"] for m in ids]
    p_lab = [table[m]["clone_id"] for m in ids]
    t_anc, p_anc = ancestry(t_parent), ancestry(p_parent)
    hit, tot = Counter(), Counter()
    for i, j in combinations(range(len(ids)), 2):
        r = relation(t_lab[i], t_lab[j], t_anc)
        tot[r] += 1
        hit[r] += relation(p_lab[i], p_lab[j], p_anc) == r
    kids = Counter(t_parent.values())
    row = {
        "sim": os.path.basename(sim),
        "n_snv": len(ids),
        "n_clones_true": len(set(t_lab)),
        "n_clones_detectable": sum(median(v) >= 3 for v in exp_alt.values()),
        "n_clones_inferred": len(set(p_lab)),
        "true_linear": all(v <= 1 for v in kids.values()),
        "purity": float(tree[0]["purity"]),
        "loss_frac": sum(float(truth[m]["carrier_fraction"]) < float(truth[m]["origin_ccf"]) - 1e-9
                         for m in ids) / len(ids),
        "ari": ari(t_lab, p_lab),
        "v_measure": v_measure(t_lab, p_lab),
        "relation_acc": sum(hit.values()) / sum(tot.values()),
        "ccf_mae": sum(abs(float(table[m]["ccf"]) - float(truth[m]["origin_ccf"]))
                       for m in ids) / len(ids),
    }
    for r in RELATIONS:
        row[f"recall_{r}"] = hit[r] / tot[r] if tot[r] else float("nan")
    rec = [hit[r] / tot[r] for r in RELATIONS if tot[r]]
    row["balanced_relation_acc"] = sum(rec) / len(rec)
    return row


def main(sim_dir, out, run="run"):
    rows = [score(os.path.join(sim_dir, d), run) for d in sorted(os.listdir(sim_dir))
            if os.path.exists(os.path.join(sim_dir, d, run, "map_table.tsv"))]
    cols = list(rows[0])
    with open(out, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(f"{v:.4f}" if isinstance(v, float) else str(v)
                               for v in r.values()) + "\n")
    print(f"{len(rows)} simulations scored -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
