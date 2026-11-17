"""Ceiling for SNV-to-clone assignment from read counts alone (2026-11-15, plan A step 2).

Oracle: the true clone CCFs and the true share of SNVs per clone are known. Each SNV goes to the clone
with the highest posterior: log(share) + binomial log-likelihood of its counts at that clone's CCF.
- base: all reads, VAF = purity * CCF / 2 (1+1, one mutated copy)
- a1:   reads on the SNV's HP only, VAF = purity * CCF (haploclone/rust/src/data/hp.rs:290-345 with 1+1)
VAF clamped to [1e-3, 1 - 1e-3] like hp.rs (ERR). No tree, no prior over trees, no search.
A clone is "found" with the same 80/80 rule as ../2026-11-14_diplosim_haploclone_ofat/summarize_ofat.py.

Usage: python3 -I oracle_ccf.py OUT_ROOT  -> writes oracle_per_clone.tsv, prints a summary
"""
import collections as co
import csv
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
REC, PREC, ERR = 0.8, 0.8, 1e-3
CELLS = ["c01_center", "c02_depth30", "c03_depth120", "c04_depth400", "c05_pur0.3", "c06_pur0.5",
         "c07_pur0.7", "c08_clone3", "c09_clone8", "c10_clone12", "c11_snv5000"]
BINS = [("<0.05", 0, .05), ("0.05-0.1", .05, .10), ("0.1-0.2", .10, .20), (">=0.2", .20, 9)]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def binom_ll(k, n, p):
    p = min(max(p, ERR), 1 - ERR)
    return k * math.log(p) + (n - k) * math.log(1 - p)   # constant C(n, k) is the same for every clone


def found_by_clone(truth, assign):
    n_true, n_rec = co.Counter(truth.values()), co.Counter(assign.values())
    pair = co.Counter((truth[m], assign[m]) for m in truth)
    out = {}
    for c in n_true:
        b = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
        out[c] = pair[b] / n_true[c] >= REC and pair[b] / n_rec[b[1]] >= PREC
    return out


rows_out = []
print("cell           trees  true  oracle_base  oracle_a1  | haploclone base  a1 (summary_c01-c11.txt)")
hc = {}
for line in open(HERE.parent / "2026-11-14_diplosim_haploclone_ofat/summary_c01-c11.txt"):
    f = line.split()
    if len(f) >= 12 and f[0].startswith("c") and f[1].isdigit():   # summary rows only, not per-run rows
        hc[f[0]] = (float(f[3]), float(f[4]))
for cell in CELLS:
    W = ROOT / cell / "work"
    found = {"base": [], "a1": []}
    ntrue = []
    for s in range(1, 11):
        truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
        tt = read(W / f"in{s}/truth_tree.tsv")
        ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
        share = {c: n / len(truth) for c, n in co.Counter(truth.values()).items()}
        ntrue.append(len(ccf))
        for mode, fname in (("base", "data.tsv"), ("a1", "data_hp.tsv")):
            assign = {}
            for r in read(W / f"in{s}/{fname}"):
                t = float(r["tumour_content"])
                if mode == "base":
                    k, n, scale = int(r["alt_counts"]), int(r["ref_counts"]) + int(r["alt_counts"]), t / 2
                else:
                    h = "1" if r["snv_hp"] == "HP1" else "2"
                    k, n, scale = int(r[f"alt_hp{h}"]), int(r[f"ref_hp{h}"]) + int(r[f"alt_hp{h}"]), t
                assign[r["mutation_id"]] = max(ccf, key=lambda c: math.log(share[c]) + binom_ll(k, n, scale * ccf[c]))
            fb = found_by_clone(truth, assign)
            found[mode].append(sum(fb.values()))
            for c in ccf:
                gap = min(abs(ccf[c] - v) for o, v in ccf.items() if o != c)
                rows_out.append((cell, s, c, next(r["parent"] for r in tt if r["clone"] == c), ccf[c], gap, mode, int(fb[c])))
    b, a = hc.get(cell, (float("nan"),) * 2)
    print(f"{cell:<14} {10:>5}  {st.mean(ntrue):>4.1f}  {st.mean(found['base']):>11.2f}  {st.mean(found['a1']):>9.2f}  |"
          f" {b:>15.2f}  {a:>4.2f}")

with open(HERE / "oracle_per_clone.tsv", "w") as fh:
    fh.write("cell\ttree\tclone\tparent\tccf\tgap\tmode\toracle_found\n")
    for r in rows_out:
        fh.write("\t".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in r) + "\n")

print("\nnon-truncal clones found by the oracle, by CCF gap to the nearest other clone (base / a1)")
for cell in CELLS:
    cells = []
    for lab, lo, hi in BINS:
        rr = [r for r in rows_out if r[0] == cell and r[3] != "root" and lo <= r[5] < hi]
        if not rr:
            cells.append(f"{lab} -")
            continue
        fr = {m: sum(r[7] for r in rr if r[6] == m) / sum(1 for r in rr if r[6] == m) for m in ("base", "a1")}
        cells.append(f"{lab} n={len(rr) // 2} {fr['base']:.0%}/{fr['a1']:.0%}")
    print(f"  {cell:<14} " + "   ".join(cells))
