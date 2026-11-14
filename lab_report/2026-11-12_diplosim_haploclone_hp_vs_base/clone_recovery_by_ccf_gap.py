"""Per truth clone: was it recovered as its own cluster, and how far is its CCF from the nearest other clone?

User question 2026-11-14: clones with close CCF seem to be mixed up with or without HP; are clones whose
CCF differs a lot from the others recovered well?

Rule (set before looking at the output): a truth clone is "recovered" in one run when one reconstructed
cluster holds >= 80 % of the clone's SNVs (recall) and >= 80 % of that cluster's SNVs come from the clone
(precision). CCF gap = smallest |CCF - CCF of any other truth clone| in the same tree (truncal = 1.0).

Input: the batch work dir of 2026-11-12 (in{s}/truth.tsv, truth_tree.tsv; run_s{s}_{mode}_h{h}_map.tsv).
Usage: python3 -I clone_recovery_by_ccf_gap.py WORK_DIR > clone_recovery_by_ccf_gap.txt
"""
import collections as co
import csv
import sys
from pathlib import Path

W = Path(sys.argv[1])
REC, PREC = 0.8, 0.8
BINS = [(0, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 1.01)]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


rows = []
for s in range(1, 11):
    truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
    ccf = {r["clone"]: float(r["true_ccf"]) for r in read(W / f"in{s}/truth_tree.tsv")}
    n_true = co.Counter(truth.values())
    for mode in ("base", "a1"):
        for h in (1, 2):
            mp = {r["mutation_id"]: r["clone_id"] for r in read(W / f"run_s{s}_{mode}_h{h}_map.tsv")}
            n_rec = co.Counter(mp.values())
            pair = co.Counter((truth[m], mp[m]) for m in truth)
            for c, cc in ccf.items():
                best = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
                recall = pair[best] / n_true[c]
                prec = pair[best] / n_rec[best[1]]
                gap = min(abs(cc - o) for k, o in ccf.items() if k != c)
                rows.append((s, mode, h, c, cc, n_true[c], gap, recall, prec, recall >= REC and prec >= PREC))

print("tree mode seed clone ccf n_snv gap recall precision recovered")
for r in rows:
    print(f"{r[0]:>4} {r[1]:>4} {r[2]} {r[3]:>5} {r[4]:.2f} {r[5]:>5} {r[6]:.3f} {r[7]:.2f} {r[8]:.2f} {'yes' if r[9] else 'no'}")

print("\nrecovered share by CCF gap to the nearest other clone (all runs; each clone counted once per run)")
print("gap bin        clones  base           a1")
for lo, hi in BINS:
    sel = [r for r in rows if lo <= r[6] < hi]
    n_cl = len({(r[0], r[3]) for r in sel})
    out = []
    for mode in ("base", "a1"):
        m = [r for r in sel if r[1] == mode]
        out.append(f"{sum(r[9] for r in m)}/{len(m)} ({sum(r[9] for r in m) / len(m):.0%})" if m else "-")
    print(f"{lo:.2f}-{hi:.2f}   {n_cl:>6}  {out[0]:<14} {out[1]}")

print("\nclones never recovered in any of the 4 runs (tree, clone, CCF, gap, SNVs)")
by = co.defaultdict(list)
for r in rows:
    by[(r[0], r[3])].append(r)
for (s, c), rs in sorted(by.items()):
    if not any(r[9] for r in rs):
        print(f"  tree {s} clone {c}: CCF {rs[0][4]:.2f}, gap {rs[0][6]:.3f}, {rs[0][5]} SNVs")
print("\nclones recovered in some runs only")
for (s, c), rs in sorted(by.items()):
    k = sum(r[9] for r in rs)
    if 0 < k < len(rs):
        det = ", ".join(f"{r[1]}{r[2]}={'Y' if r[9] else 'n'}" for r in rs)
        print(f"  tree {s} clone {c}: CCF {rs[0][4]:.2f}, gap {rs[0][6]:.3f}, {rs[0][5]} SNVs; {det}")
