"""Per truth clone in the one-factor-at-a-time grid (2026-11-14): is it recovered, and how far is its CCF from the nearest other clone?

Same recovery rule as summarize_ofat.py (80/80). "gap" = |CCF - CCF of the nearest other truth clone|, the truncal
clone (CCF 1) included. found_base / found_a1 = in how many of the 2 haploclone seeds the clone was recovered.
Usage: python3 -I per_clone_ofat.py OUT_ROOT > per_clone_c01-c10.tsv
"""
import collections as co
import csv
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
REC, PREC = 0.8, 0.8   # same as summarize_ofat.py


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))
CELLS = ["c01_center", "c02_depth30", "c03_depth120", "c04_depth400", "c05_pur0.3", "c06_pur0.5",
         "c07_pur0.7", "c08_clone3", "c09_clone8", "c10_clone12", "c11_snv5000"]


def recovered(truth, mp):
    n_true, n_rec = co.Counter(truth.values()), co.Counter(mp.values())
    pair = co.Counter((truth[m], mp[m]) for m in truth)
    out = {}
    for c in n_true:
        b = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
        out[c] = pair[b] / n_true[c] >= REC and pair[b] / n_rec[b[1]] >= PREC
    return out


print("cell\ttree\tclone\tparent\tccf\tgap\tn_snv\tfound_base\tfound_a1")
for cell in CELLS:
    W = ROOT / cell / "work"
    if not (ROOT / cell / "results.tsv").exists():
        continue
    for s in range(1, 11):
        truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
        tt = read(W / f"in{s}/truth_tree.tsv")
        ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
        n = co.Counter(truth.values())
        hit = co.Counter()
        for mode in ("base", "a1"):
            for h in (1, 2):
                mp = {r["mutation_id"]: r["clone_id"] for r in read(W / f"run_s{s}_{mode}_h{h}_map.tsv")}
                for c, ok in recovered(truth, mp).items():
                    hit[(c, mode)] += ok
        for r in tt:
            c = r["clone"]
            gap = min(abs(ccf[c] - v) for k, v in ccf.items() if k != c)
            print(f"{cell}\t{s}\t{c}\t{r['parent']}\t{ccf[c]:.3f}\t{gap:.3f}\t{n[c]}\t{hit[(c, 'base')]}\t{hit[(c, 'a1')]}")
