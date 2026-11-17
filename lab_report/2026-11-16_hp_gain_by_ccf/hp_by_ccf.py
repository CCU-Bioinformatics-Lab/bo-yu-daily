"""HP gain by clone CCF (README §2). Generates diplosim trees (no haploclone) and runs the per-SNV oracle.

Usage: python3 -I hp_by_ccf.py OUT_ROOT FIRST_SEED LAST_SEED > hp_by_ccf_summary.txt   (writes hp_by_ccf_per_clone.tsv)
"""
import collections as co
import csv
import math
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT, S0, S1 = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DIPLOSIM = REPO / "diplosim/target/release/diplosim"
REC, PREC, ERR = 0.8, 0.8, 1e-3
CB = [("<0.3", 0, .3), ("0.3-0.6", .3, .6), ("0.6-0.8", .6, .8), (">=0.8", .8, 9)]
GB = [("<0.05", 0, .05), ("0.05-0.1", .05, .10), ("0.1-0.2", .10, .20), (">=0.2", .20, 9)]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def gen(s):
    sim, inp = OUT / f"sim{s}", OUT / f"in{s}"
    if not (inp / "truth_tree.tsv").exists():
        for cmd in ([DIPLOSIM, "--n-clones", 5, "--n-snv", 1000, "--coverage", 60, "--min-tumour-purity", 0.9,
                     "--max-tumour-purity", 0.9, "--seed", s, "--out", sim],
                    [sys.executable, "-I", REPO / "tools/diplosim_to_haploclone.py", sim, inp]):
            subprocess.run([str(c) for c in cmd], check=True, capture_output=True)
    return s


def binom_ll(k, n, p):
    p = min(max(p, ERR), 1 - ERR)
    return k * math.log(p) + (n - k) * math.log(1 - p)


def analyse(s):
    inp = OUT / f"in{s}"
    truth = {r["mutation_id"]: r["clone"] for r in read(inp / "truth.tsv")}
    tt = read(inp / "truth_tree.tsv")
    ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
    par = {r["clone"]: r["parent"] for r in tt}
    n_true = co.Counter(truth.values())
    share = {c: n / len(truth) for c, n in n_true.items()}
    out = []
    for mode, fname in (("base", "data.tsv"), ("a1", "data_hp.tsv")):
        assign = {}
        for r in read(inp / fname):
            t = float(r["tumour_content"])
            if mode == "base":
                k, n, scale = int(r["alt_counts"]), int(r["ref_counts"]) + int(r["alt_counts"]), t / 2
            else:
                h = "1" if r["snv_hp"] == "HP1" else "2"
                k, n, scale = int(r[f"alt_hp{h}"]), int(r[f"ref_hp{h}"]) + int(r[f"alt_hp{h}"]), t
            assign[r["mutation_id"]] = max(ccf, key=lambda c: math.log(share[c]) + binom_ll(k, n, scale * ccf[c]))
        n_rec = co.Counter(assign.values())
        pair = co.Counter((truth[m], assign[m]) for m in truth)
        for c in ccf:
            if par[c] == "root":
                continue
            b = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
            found = pair[b] / n_true[c] >= REC and pair[b] / n_rec[b[1]] >= PREC
            gap = min(abs(ccf[c] - v) for o, v in ccf.items() if o != c)
            out.append((s, c, ccf[c], gap, n_true[c], mode, int(found), pair[(c, c)] / n_true[c]))
    return out


seeds = range(S0, S1 + 1)
OUT.mkdir(parents=True, exist_ok=True)
with ThreadPoolExecutor(24) as ex:
    list(ex.map(gen, seeds))
    rows = [r for rs in ex.map(analyse, seeds) for r in rs]
with open(HERE / "hp_by_ccf_per_clone.tsv", "w") as fh:
    fh.write("seed\tclone\tccf\tgap\tn_snv\tmode\tfound\tsnv_correct\n")
    for r in rows:
        fh.write("\t".join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in r) + "\n")


def cell(sel):
    b = [r for r in rows if r[5] == "base" and sel(r)]
    a = [r for r in rows if r[5] == "a1" and sel(r)]
    if not b:
        return "n=0"
    f = lambda rr, i: sum(r[i] for r in rr) / len(rr)
    return f"n={len(b):<4} found {f(b, 6):>4.0%} -> {f(a, 6):>4.0%} ({100 * (f(a, 6) - f(b, 6)):>+4.0f})  snv_correct {f(b, 7):.2f} -> {f(a, 7):.2f}"


print(f"{len(seeds)} trees (seeds {S0}-{S1}), 5 clones, 1,000 SNVs, 60x, purity 0.9; non-truncal clones; base -> A1 (difference in points)")
print("\nby clone CCF (theory: depth multiplier (1 - t*CCF/2) / (1 - t*CCF), t = 0.9)")
for lab, lo, hi in CB:
    print(f"  CCF {lab:<8} {cell(lambda r: lo <= r[2] < hi)}")
print("\nby clone CCF within each CCF-gap stratum")
for gl, glo, ghi in GB:
    print(f" gap {gl}")
    for lab, lo, hi in CB:
        print(f"  CCF {lab:<8} {cell(lambda r: lo <= r[2] < hi and glo <= r[3] < ghi)}")
