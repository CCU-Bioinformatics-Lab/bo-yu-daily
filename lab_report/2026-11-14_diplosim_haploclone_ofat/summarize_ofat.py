"""Summarize the one-factor-at-a-time grid (2026-11-14): per cell, clones recovered and exact trees, A1 vs base.

Rules (fixed in README §3 before any result was seen):
- A truth clone is "recovered" in one run when one reconstructed cluster holds >= 80 % of the clone's SNVs
  and >= 80 % of that cluster's SNVs come from the clone (same rule as 2026-11-12 §8).
- Exact tree: every truth clone recovered, as many clusters as truth clones (one-to-one), and each recovered
  clone's parent cluster is the cluster of its truth parent (truncal clone sits under the root).
- Per tree: average the 2 haploclone seeds, then A1 - base. Report the mean over trees and a t 95 % CI.
  "HP improves" = mean >= +0.3 clones and the CI excludes 0.

Input: OUT_ROOT/<cell>/work/{in{s}/truth.tsv, in{s}/truth_tree.tsv, run_s{s}_{mode}_h{h}_map.tsv, ..._map.nwk}
and OUT_ROOT/<cell>/results.tsv (ccf_mae). Cells without results.tsv are skipped.
Usage: python3 -I summarize_ofat.py OUT_ROOT > summary.txt
"""
import collections as co
import csv
import statistics as st
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
REC, PREC, MIN_GAIN = 0.8, 0.8, 0.3
T975 = {9: 2.262}   # t quantile for 10 trees
CELLS = ["c01_center", "c02_depth30", "c03_depth120", "c04_depth400", "c05_pur0.3", "c06_pur0.5",
         "c07_pur0.7", "c08_clone3", "c09_clone8", "c10_clone12", "c11_snv5000"]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def parse_newick(text):
    """'(((2)1)0)root;' -> {child: parent}; a node's name follows its closing parenthesis."""
    text = text.strip().rstrip(";")
    parent, stack, i, pending = {}, [], 0, []
    # walk: '(' opens a group, names are read after ')' or at leaves, ',' separates siblings
    kids = [[]]
    while i < len(text):
        ch = text[i]
        if ch == "(":
            kids.append([])
            i += 1
        elif ch in ",)":
            i += 1
            if ch == ")":
                j = i
                while j < len(text) and text[j] not in ",()":
                    j += 1
                name = text[i:j]
                i = j
                for k in kids.pop():
                    parent[k] = name
                kids[-1].append(name)
        else:
            j = i
            while j < len(text) and text[j] not in ",()":
                j += 1
            kids[-1].append(text[i:j])
            i = j
    return parent


def one_run(truth, tparent, mp, rparent):
    n_true = co.Counter(truth.values())
    n_rec = co.Counter(mp.values())
    pair = co.Counter((truth[m], mp[m]) for m in truth)
    match = {}
    for c in n_true:
        best = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
        if pair[best] / n_true[c] >= REC and pair[best] / n_rec[best[1]] >= PREC:
            match[c] = best[1]
    found = len(match)
    exact = found == len(n_true) == len(n_rec) and len(set(match.values())) == found
    if exact:
        for c, k in match.items():
            tp = tparent[c]
            want = "root" if tp == "root" else match[tp]
            if rparent.get(k) != want:
                exact = False
                break
    return found, exact


def ci(xs):
    m = st.mean(xs)
    h = T975[len(xs) - 1] * st.stdev(xs) / len(xs) ** 0.5
    return m, m - h, m + h


print("cell           trees  true  found_base  found_a1  diff(a1-base) [95% CI]      exact_base exact_a1  "
      "ccf_mae base/a1   a1>base/a1<base  HP improves?")
detail = []
for cell in CELLS:
    d = ROOT / cell
    if not (d / "results.tsv").exists():
        print(f"{cell:<14} (not finished)")
        continue
    W = d / "work"
    res = read(d / "results.tsv")
    mae = {m: st.mean(float(r["ccf_mae"]) for r in res if r["mode"] == m) for m in ("base", "a1")}
    per_tree, exact, ntrue, gaps = {}, co.Counter(), [], []
    for s in range(1, 11):
        truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
        tt = read(W / f"in{s}/truth_tree.tsv")
        tparent = {r["clone"]: r["parent"] for r in tt}
        ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
        gaps += [min(abs(v - o) for k, o in ccf.items() if k != c) for c, v in ccf.items()]
        ntrue.append(len(tparent))
        f = {}
        for mode in ("base", "a1"):
            vals = []
            for h in (1, 2):
                run = W / f"run_s{s}_{mode}_h{h}"
                mp = {r["mutation_id"]: r["clone_id"] for r in read(f"{run}_map.tsv")}
                rparent = parse_newick(open(f"{run}_map.nwk").read())
                found, ex = one_run(truth, tparent, mp, rparent)
                vals.append(found)
                exact[mode] += ex
                detail.append((cell, s, mode, h, len(tparent), found, ex))
            f[mode] = st.mean(vals)
        per_tree[s] = f
    diffs = [per_tree[s]["a1"] - per_tree[s]["base"] for s in per_tree]
    m, lo, hi = ci(diffs)
    fb = st.mean(per_tree[s]["base"] for s in per_tree)
    fa = st.mean(per_tree[s]["a1"] for s in per_tree)
    better = sum(x > 0 for x in diffs)
    worse = sum(x < 0 for x in diffs)
    verdict = "yes" if (m >= MIN_GAIN and lo > 0) else "no"
    print(f"{cell:<14} {len(per_tree):>5}  {st.mean(ntrue):>4.1f}  {fb:>10.2f}  {fa:>8.2f}  "
          f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]{'':<8} {exact['base']:>4}/20  {exact['a1']:>4}/20  "
          f"{mae['base']:.4f}/{mae['a1']:.4f}   {better}/{worse}{'':<12} {verdict}")
    detail.append((cell, "gap", sorted(gaps)))

print("\nCCF gap to nearest other truth clone (all clones incl. truncal, 10 trees): median, share < 0.10")
for row in detail:
    if row[1] == "gap":
        g = row[2]
        print(f"  {row[0]:<14} n={len(g):>3}  median {st.median(g):.3f}  <0.10: {sum(x < 0.10 for x in g) / len(g):.0%}")

print("\nper run: cell tree mode seed true_clones found exact")
for row in detail:
    if row[1] != "gap":
        print(" ".join(str(x) for x in row))
