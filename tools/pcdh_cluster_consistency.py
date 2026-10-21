"""Cross-window consistency of per-read UPGMA 2-cluster assignments.

usage: python3 pcdh_cluster_consistency.py MATRIX_TSV [MATRIX_TSV ...]

MATRIX_TSV is a pcdh_longread_matrix.py output; its .clusters.tsv must sit
next to it. For each window, pair it with the next window (start <= 45 kb
later) whose CpG interval does not overlap (overlapping intervals share data,
so agreement would be trivial). On reads in both matrices, agreement = share
of read pairs whose same/different-cluster status matches between the two
windows (label-switch free). Shuffled = mean agreement after permuting the
second window's labels among shared reads (200 times). Pairs where either
window puts all shared reads in one cluster are skipped.
First used in lab_report/2026-10-21_h1437_pcdh_longread_matrix/.
"""
import sys, csv, random, statistics as st
from collections import defaultdict

MAX_GAP, MIN_SHARED, N_SHUF = 45_000, 6, 200
random.seed(0)


def agreement(a, b, reads):
    pairs = [(x, y) for k, x in enumerate(reads) for y in reads[k + 1:]]
    return sum((a[x] == a[y]) == (b[x] == b[y]) for x, y in pairs) / len(pairs)


print("label\thp\twindow_pairs\tshared_reads\tagreement\tshuffled\tabove_shuffled\tagreement_ge_0.9")
for f in sys.argv[1:]:
    clusters = defaultdict(dict)
    interval = {}
    for r in csv.DictReader(open(f.rsplit(".tsv", 1)[0] + ".clusters.tsv"), delimiter="\t"):
        clusters[(r["label"], r["hp"], int(r["win_start"]))][r["read"]] = int(r["c2"])
    for r in csv.DictReader(open(f), delimiter="\t"):
        interval[(r["label"], r["hp"], int(r["win_start"]))] = (int(r["cpg_from"]), int(r["cpg_to"]))
    for lab, hp in sorted({k[:2] for k in clusters}):
        ws = sorted(k[2] for k in clusters if k[:2] == (lab, hp))
        res, shuf, nsh = [], [], []
        for i, w in enumerate(ws):
            for w2 in ws[i + 1:]:
                if w2 - w > MAX_GAP:
                    break
                (a0, a1), (b0, b1) = interval[(lab, hp, w)], interval[(lab, hp, w2)]
                if not (a1 < b0 or b1 < a0):
                    continue
                a, b = clusters[(lab, hp, w)], clusters[(lab, hp, w2)]
                sh = [x for x in a if x in b]
                if len(sh) < MIN_SHARED or len({a[x] for x in sh}) < 2 or len({b[x] for x in sh}) < 2:
                    continue
                res.append(agreement(a, b, sh))
                null = []
                for _ in range(N_SHUF):
                    lab_b = [b[x] for x in sh]
                    random.shuffle(lab_b)
                    null.append(agreement(a, dict(zip(sh, lab_b)), sh))
                shuf.append(st.mean(null))
                nsh.append(len(sh))
                break
        if res:
            print(f"{lab}\t{hp}\t{len(res)}\t{st.median(nsh)}\t{st.median(res):.2f}\t{st.median(shuf):.2f}\t"
                  f"{sum(x > y for x, y in zip(res, shuf))}\t{sum(x >= 0.9 for x in res)}")
        else:
            print(f"{lab}\t{hp}\t0\t-\t-\t-\t-\t-")
