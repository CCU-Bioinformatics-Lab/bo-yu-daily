"""Clone-level scoring (../2026-11-15_close_ccf_oracle/README.md §6 rule: one-to-one CCF matching, found when
|CCF diff| <= 0.05) of the center batch by mode. Usage: python3 -I group_level_c4.py BATCH_DIR"""
import csv, statistics as st, sys
from pathlib import Path

W = Path(sys.argv[1]) / "work"
rd = lambda p: list(csv.DictReader(open(p), delimiter="\t"))
TOL = 0.05


def parse_newick(text):
    text = text.strip().rstrip(";"); parent, i, kids = {}, 0, [[]]
    while i < len(text):
        ch = text[i]
        if ch == "(":
            kids.append([]); i += 1
        elif ch in ",)":
            i += 1
            if ch == ")":
                j = i
                while j < len(text) and text[j] not in ",()": j += 1
                name = text[i:j]; i = j
                for k in kids.pop(): parent[k] = name
                kids[-1].append(name)
        else:
            j = i
            while j < len(text) and text[j] not in ",()": j += 1
            kids[-1].append(text[i:j]); i = j
    return parent


def match(tc, rc):   # order-preserving 1-D matching of min(n, m) pairs (same as group_level.py)
    T, R = sorted(tc, key=tc.get), sorted(rc, key=rc.get)
    swap = len(T) > len(R)
    A, B, ca, cb = (R, T, rc, tc) if swap else (T, R, tc, rc)
    n, m, INF = len(A), len(B), float("inf")
    f = [[INF] * (m + 1) for _ in range(n + 1)]; f[0] = [0.0] * (m + 1)
    for i in range(1, n + 1):
        for j in range(i, m + 1):
            f[i][j] = min(f[i][j - 1], f[i - 1][j - 1] + abs(ca[A[i - 1]] - cb[B[j - 1]]))
    pairs, i, j = {}, n, m
    while i > 0:
        if j > i and f[i][j] == f[i][j - 1]: j -= 1
        else: pairs[A[i - 1]] = B[j - 1]; i -= 1; j -= 1
    return {b: a for a, b in pairs.items()} if swap else pairs


print("mode       found(clone level)  count_ok  tree_ok   (10 trees x 2 seeds)")
for mode in ("a1", "a1c4", "a1c4pool"):
    fo, co_, tr = [], 0, 0
    for s in range(1, 11):
        tt = rd(W / f"in{s}/truth_tree.tsv")
        tc = {r["clone"]: float(r["true_ccf"]) for r in tt}; tp = {r["clone"]: r["parent"] for r in tt}
        vals = []
        for h in (1, 2):
            run = W / f"run_s{s}_{mode}_h{h}"
            rc = {r["clone_id"]: float(r["ccf"]) for r in rd(f"{run}_map.tsv")}
            rp = parse_newick(open(f"{run}_map.nwk").read())
            mp = match(tc, rc)
            found = {c for c, r in mp.items() if abs(tc[c] - rc[r]) <= TOL}
            ok = len(rc) == len(tc)
            co_ += ok
            tr += ok and len(found) == len(tc) and all(rp.get(mp[c]) == ("root" if tp[c] == "root" else mp[tp[c]]) for c in tc)
            vals.append(len(found))
        fo.append(st.mean(vals))
    print(f"{mode:<10} {st.mean(fo):>8.2f}            {co_:>2}/20     {tr:>2}/20")
