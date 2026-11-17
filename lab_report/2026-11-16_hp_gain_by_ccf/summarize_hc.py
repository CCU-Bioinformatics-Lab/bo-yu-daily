"""haploclone base vs A1 by clone CCF (README §9). Usage: python3 -I summarize_hc.py BATCH_DIR > hc_summary.txt"""
import collections as co
import csv
import random
import sys
from pathlib import Path

W = Path(sys.argv[1]) / "work"
HERE = Path(__file__).resolve().parent
REC, PREC = 0.8, 0.8
CB = [("<0.3", 0, .3), ("0.3-0.6", .3, .6), ("0.6-0.8", .6, .8), (">=0.8", .8, 9)]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def found(truth, mp):
    n_true, n_rec = co.Counter(truth.values()), co.Counter(mp.values())
    pair = co.Counter((truth[m], mp[m]) for m in truth)
    out = {}
    for c in n_true:
        b = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
        out[c] = pair[b] / n_true[c] >= REC and pair[b] / n_rec[b[1]] >= PREC
    return out


trees = sorted(int(p.name[2:]) for p in W.glob("in*") if p.is_dir())
rows, missing = [], 0   # (tree, clone, ccf, gap, base, a1): share of the 2 seeds that found the clone
for s in trees:
    truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
    tt = read(W / f"in{s}/truth_tree.tsv")
    ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
    par = {r["clone"]: r["parent"] for r in tt}
    f = {}
    for m in ("base", "a1"):
        runs = [W / f"run_s{s}_{m}_h{h}_map.tsv" for h in (1, 2)]
        if not all(p.exists() for p in runs):
            missing += 1
            break
        fs = [found(truth, {r["mutation_id"]: r["clone_id"] for r in read(p)}) for p in runs]
        f[m] = {c: sum(x[c] for x in fs) / 2 for c in ccf}
    else:
        for c in ccf:
            if par[c] != "root":
                gap = min(abs(ccf[c] - v) for o, v in ccf.items() if o != c)
                rows.append((s, c, ccf[c], gap, f["base"][c], f["a1"][c]))

oracle = {}
for r in read(HERE / "hp_by_ccf_per_clone.tsv"):
    oracle[(int(r["seed"]), r["clone"], r["mode"])] = int(r["found"])
with open(HERE / "hc_per_clone.tsv", "w") as fh:
    fh.write("seed\tclone\tccf\tgap\thc_base\thc_a1\toracle_base\toracle_a1\n")
    for s, c, v, g, b, a in rows:
        fh.write(f"{s}\t{c}\t{v:.4f}\t{g:.4f}\t{b}\t{a}\t{oracle[(s, c, 'base')]}\t{oracle[(s, c, 'a1')]}\n")


def stat(sel, rr):
    x = [r for r in rr if sel(r)]
    if not x:
        return None
    return sum(r[4] for r in x) / len(x), sum(r[5] for r in x) / len(x), len(x)


def line(lab, sel):
    b, a, n = stat(sel, rows)
    rng = random.Random(20261116)
    by = co.defaultdict(list)
    for r in rows:
        by[r[0]].append(r)
    ts, gains = list(by), []
    for _ in range(2000):
        st_ = stat(sel, [r for t in rng.choices(ts, k=len(ts)) for r in by[t]])
        if st_:
            gains.append(st_[1] - st_[0])
    gains.sort()
    lo, hi = gains[int(.025 * len(gains))], gains[int(.975 * len(gains)) - 1]
    x = [r for r in rows if sel(r)]
    ob = sum(oracle[(r[0], r[1], "base")] for r in x) / n
    oa = sum(oracle[(r[0], r[1], "a1")] for r in x) / n
    print(f"  {lab:<22} n={n:<4} haploclone {b:>4.0%} -> {a:>4.0%}  gain {100 * (a - b):>+5.1f} [{100 * lo:>+5.1f}, {100 * hi:>+5.1f}]"
          f"   ceiling {ob:>4.0%} -> {oa:>4.0%} ({100 * (oa - ob):>+4.0f})")


print(f"{len(trees) - missing} of {len(trees)} trees complete; non-truncal clones; found = mean of 2 haploclone seeds; base -> A1; 95% CI by tree bootstrap")
print("by clone CCF")
for lab, lo, hi in CB:
    line(f"CCF {lab}", lambda r, lo=lo, hi=hi: lo <= r[2] < hi)
print("by CCF gap to the nearest clone")
line("gap < 0.1", lambda r: r[3] < 0.1)
line("gap >= 0.1", lambda r: r[3] >= 0.1)
line("CCF 0.6-0.8, gap >= 0.2", lambda r: .6 <= r[2] < .8 and r[3] >= .2)
line("all", lambda r: True)
