#!/usr/bin/env python3
"""Compare a haploclone MAP result with the diplosim truth tree (2026-11-12).

Inputs: TRUTH_DIR from tools/diplosim_to_haploclone.py (truth.tsv, truth_tree.tsv) and a MAP table
and tree from `haploclone map` (columns mutation_id, clone_id, sample_id, ccf; minimal newick).
Measures, one sample only:
  n_clones      inferred clones vs true clones
  ARI           adjusted Rand index of the SNV clustering (1 = same partition)
  pair_accuracy share of SNV pairs whose relation (same clone, ancestor, descendant, other branch)
                matches the truth; the tree measure of the PhyClone paper
  ccf_mae       mean |inferred CCF - true CCF| over SNVs
Also prints a truth-clone x inferred-clone table, the inferred tree, and per true clone where its
SNVs went.

Usage: python3 tools/eval_diplosim_haploclone.py TRUTH_DIR MAP_TABLE MAP_TREE [LABEL]
Other scripts can import evaluate(truth_dir, map_table, map_tree), which returns the four measures.
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from math import comb

tsv = lambda p: list(csv.DictReader(open(p), delimiter="\t"))


def newick_parents(text):
    """{node: parent} for a minimal newick with labelled internal nodes, e.g. (((2)1)0)root;"""
    text = re.sub(r"\s+|:[0-9.eE+-]+", "", text.strip().rstrip(";"))
    parent, stack, pending, i = {}, [], [], 0
    tok = re.compile(r"[^(),]+")
    while i < len(text):
        ch = text[i]
        if ch == "(":
            stack.append([])
            i += 1
        elif ch == ",":
            i += 1
        elif ch == ")":
            m = tok.match(text, i + 1)
            name = m.group(0)
            i = m.end()
            for kid in stack.pop():
                parent[kid] = name
            (stack[-1] if stack else pending).append(name)
        else:
            m = tok.match(text, i)
            (stack[-1] if stack else pending).append(m.group(0))
            i = m.end()
    return parent


def ancestors(node, parent):
    out = []
    while node in parent:
        node = parent[node]
        out.append(node)
    return out


def relation(a, b, parent):
    if a == b:
        return "same"
    if b in ancestors(a, parent):
        return "desc"
    if a in ancestors(b, parent):
        return "anc"
    return "branch"


def evaluate(truth_dir, map_table, map_tree, label=None, verbose=False):
    truth = {r["mutation_id"]: r for r in tsv(f"{truth_dir}/truth.tsv")}
    t_parent = {r["clone"]: r["parent"] for r in tsv(f"{truth_dir}/truth_tree.tsv")}
    inf = {r["mutation_id"]: r for r in tsv(map_table)}
    i_parent = newick_parents(open(map_tree).read())
    muts = sorted(truth)
    assert set(inf) == set(muts), "MAP table and truth have different SNVs"
    tc = [truth[m]["clone"] for m in muts]
    ic = [inf[m]["clone_id"] for m in muts]

    # ARI
    n = len(muts)
    cont = Counter(zip(tc, ic))
    sum_ij = sum(comb(v, 2) for v in cont.values())
    sum_a = sum(comb(v, 2) for v in Counter(tc).values())
    sum_b = sum(comb(v, 2) for v in Counter(ic).values())
    expected = sum_a * sum_b / comb(n, 2)
    ari = (sum_ij - expected) / ((sum_a + sum_b) / 2 - expected)

    # Pair relations, counted over clone pairs weighted by SNV counts (same result as all SNV pairs).
    tclones, iclones = sorted(set(tc)), sorted(set(ic))
    correct = total = 0
    for (t1, i1), n1 in cont.items():
        for (t2, i2), n2 in cont.items():
            pairs = n1 * (n1 - 1) if (t1, i1) == (t2, i2) else n1 * n2
            total += pairs
            if relation(t1, t2, t_parent) == relation(i1, i2, i_parent):
                correct += pairs
    pair_acc = correct / total

    ccf_mae = sum(abs(float(inf[m]["ccf"]) - float(truth[m]["true_ccf"])) for m in muts) / n

    result = {"n_clones": len(iclones), "true_clones": len(tclones), "ari": ari, "pair_acc": pair_acc, "ccf_mae": ccf_mae}
    if not verbose:
        return result
    print(f"== {label}")
    print(f"clones: inferred {len(iclones)}, true {len(tclones)}")
    print(f"ARI {ari:.3f}   pair_accuracy {pair_acc:.3f}   ccf_mae {ccf_mae:.3f}")
    inf_ccf = {c: float(next(inf[m]['ccf'] for m in muts if inf[m]['clone_id'] == c)) for c in iclones}
    true_ccf = {r["clone"]: float(r["true_ccf"]) for r in tsv(f"{truth_dir}/truth_tree.tsv")}
    print("inferred tree (clone <- parent, CCF, n SNV):")
    for c in iclones:
        print(f"  {c} <- {i_parent.get(c, '?')}  CCF {inf_ccf[c]:.2f}  n {Counter(ic)[c]}")
    print("true tree:")
    for c in tclones:
        print(f"  {c} <- {t_parent[c]}  CCF {true_ccf[c]:.2f}  n {Counter(tc)[c]}")
    print("truth clone x inferred clone (SNV counts):")
    print("        " + "".join(f"{c:>6}" for c in iclones))
    for t in tclones:
        print(f"  {t:>5} " + "".join(f"{cont.get((t, c), 0):>6}" for c in iclones))
    return result


if __name__ == "__main__":
    evaluate(*sys.argv[1:4], label=sys.argv[4] if len(sys.argv) > 4 else sys.argv[2], verbose=True)
