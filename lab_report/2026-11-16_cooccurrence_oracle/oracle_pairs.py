"""Ceiling with read co-occurrence (2026-11-16, step 1). Rules are in README §2, written before the run.

Known truth: clone CCFs, share of SNVs per clone, the tree. No search over trees.
Part A, per-SNV assignment, scored with the 80/80 rule (same as ../2026-11-15_close_ccf_oracle/oracle_ccf.py, a1 mode):
  counts   log(share) + binomial ll of the SNV's HP counts                       (must reproduce 2.40 clones)
  joint    counts + pair read patterns, all SNVs assigned together (ICM from the counts answer)
  nbr      counts + pair read patterns, the true clone of every neighbour is given (generous upper bound)
Part B, per close clone pair (|CCF diff| < 0.1): does the data say "two clones" rather than "one"?
  split  = true CCFs, true relation;  merged = one pooled CCF, pairs scored as same clone
  two clones if 2 * (ll_split - ll_merged) > 2 * ln(n_snv)   (BIC, 2 extra parameters)

Usage: python3 -I oracle_pairs.py BATCH_ROOT > oracle_pairs_summary.txt   (writes oracle_pairs_per_clone.tsv)
"""
import collections as co
import csv
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
REC, PREC, ERR, PAIR_EPS = 0.8, 0.8, 1e-3, 0.01   # PAIR_EPS = haploclone --pair-eps default
SETS = [("5.3", "center"), ("20", "d20"), ("50", "d50"), ("100", "d100")]
BINS = [("<0.05", 0, .05), ("0.05-0.1", .05, .10), ("0.1-0.2", .10, .20), (">=0.2", .20, 9)]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def binom_ll(k, n, p):
    p = min(max(p, ERR), 1 - ERR)
    return k * math.log(p) + (n - k) * math.log(1 - p)


def ancestors(parent, c):
    out = set()
    while parent[c] != "root":
        c = parent[c]
        out.add(c)
    return out


def pattern_logp(t, ca, cb, rel):
    """log P(11, 10, 01, 00) for a read on the SNVs' HP; rel of clone a to clone b: same / anc / desc / other."""
    if rel == "same":
        p = (t * ca, 0, 0, 1 - t * ca)
    elif rel == "anc":      # a is an ancestor of b
        p = (t * cb, t * (ca - cb), 0, 1 - t * ca)
    elif rel == "desc":     # a is a descendant of b
        p = (t * ca, 0, t * (cb - ca), 1 - t * cb)
    else:
        p = (0, t * ca, t * cb, 1 - t * (ca + cb))
    return [math.log((1 - PAIR_EPS) * max(x, 0) + PAIR_EPS / 4) for x in p]


def found_by_clone(truth, assign):
    n_true, n_rec = co.Counter(truth.values()), co.Counter(assign.values())
    pair = co.Counter((truth[m], assign[m]) for m in truth)
    out = {}
    for c in n_true:
        b = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
        out[c] = pair[b] / n_true[c] >= REC and pair[b] / n_rec[b[1]] >= PREC
    return out


rows_out, summary, pair_rows, lp_gain = [], [], [], []
for dens, name in SETS:
    W = ROOT / name / "work"
    found = co.defaultdict(list)
    npairs = []
    for s in range(1, 11):
        truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
        tt = read(W / f"in{s}/truth_tree.tsv")
        ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
        parent = {r["clone"]: r["parent"] for r in tt}
        anc = {c: ancestors(parent, c) for c in ccf}
        clones = list(ccf)
        share = {c: n / len(truth) for c, n in co.Counter(truth.values()).items()}
        cnt, t = {}, None
        for r in read(W / f"in{s}/data_hp.tsv"):
            t = float(r["tumour_content"])
            h = "1" if r["snv_hp"] == "HP1" else "2"
            cnt[r["mutation_id"]] = (int(r[f"alt_hp{h}"]), int(r[f"ref_hp{h}"]) + int(r[f"alt_hp{h}"]))
        rel = {(a, b): "same" if a == b else "anc" if a in anc[b] else "desc" if b in anc[a] else "other"
               for a in clones for b in clones}
        LP = {(a, b): pattern_logp(t, ccf[a], ccf[b], rel[a, b]) for a in clones for b in clones}
        unary = {m: {c: math.log(share[c]) + binom_ll(k, n, t * ccf[c]) for c in clones} for m, (k, n) in cnt.items()}
        nbr = co.defaultdict(list)   # m -> [(other, (n11, n10, n01, n00) seen from m)]
        prs = read(W / f"in{s}/pairs.tsv")
        npairs.append(len(prs))
        for r in prs:
            i, j = r["mutation_i"], r["mutation_j"]
            n11, n10, n01, n00 = (int(r[x]) for x in ("n11", "n10", "n01", "n00"))
            nbr[i].append((j, (n11, n10, n01, n00)))
            nbr[j].append((i, (n11, n01, n10, n00)))

        def best(m, other):
            def sc(c):
                return unary[m][c] + sum(sum(x * y for x, y in zip(pat, LP[c, other[j]])) for j, pat in nbr[m])
            return max(clones, key=sc)

        a_counts = {m: max(clones, key=lambda c: unary[m][c]) for m in truth}
        a_nbr = {m: best(m, truth) for m in truth}

        def icm(start):   # SNVs without any pair always keep the counts answer
            a = {m: start[m] if nbr[m] else a_counts[m] for m in truth}
            for _ in range(100):
                changed = 0
                for m in truth:
                    if nbr[m]:
                        c = best(m, a)
                        changed += c != a[m]
                        a[m] = c
                if not changed:
                    break
            return a

        def logpost(a):
            return sum(unary[m][a[m]] for m in truth) + sum(
                sum(x * y for x, y in zip(pat, LP[a[m], a[j]])) for m in truth for j, pat in nbr[m]) / 2

        res = {"counts": a_counts, "joint": icm(a_counts), "joint_from_truth": icm(truth), "nbr": a_nbr}
        lp_gain.append((dens, s, logpost(res["joint_from_truth"]) - logpost(res["joint"])))
        gap = {c: min(abs(ccf[c] - v) for o, v in ccf.items() if o != c) for c in ccf}
        for mode, a in res.items():
            fb = found_by_clone(truth, a)
            found[mode].append(sum(fb.values()))
            for c in ccf:
                rows_out.append((dens, s, c, parent[c], ccf[c], gap[c], mode, int(fb[c])))

        # Part B: close clone pairs
        members = co.defaultdict(list)
        for m, c in truth.items():
            members[c].append(m)
        pen = 2 * math.log(len(truth))
        for x, a in enumerate(clones):
            for b in clones[x + 1:]:
                d = abs(ccf[a] - ccf[b])
                if d >= 0.1:
                    continue
                ms = members[a] + members[b]
                K, N = sum(cnt[m][0] for m in ms), sum(cnt[m][1] for m in ms)
                cm = min(K / (N * t), 1.0)
                c_split = sum(binom_ll(*cnt[m], t * ccf[truth[m]]) for m in ms)
                c_merge = sum(binom_ll(*cnt[m], t * cm) for m in ms)
                lp_m = pattern_logp(t, cm, cm, "same")
                p_split = p_merge = 0.0
                n_cross = 0
                inset = set(ms)
                for r in prs:
                    i, j = r["mutation_i"], r["mutation_j"]
                    if i in inset and j in inset:
                        pat = [int(r[k]) for k in ("n11", "n10", "n01", "n00")]
                        p_split += sum(u * v for u, v in zip(pat, LP[truth[i], truth[j]]))
                        p_merge += sum(u * v for u, v in zip(pat, lp_m))
                        n_cross += truth[i] != truth[j]
                r_ = "anc" if rel[a, b] in ("anc", "desc") else "sib"
                pair_rows.append((dens, s, a, b, r_, d, len(members[a]), len(members[b]), n_cross,
                                  2 * (c_split - c_merge), 2 * (c_split - c_merge + p_split - p_merge), pen))
    summary.append((dens, st.mean(npairs), {m: st.mean(v) for m, v in found.items()}))

with open(HERE / "oracle_pairs_per_clone.tsv", "w") as fh:
    fh.write("snvs_per_mb\ttree\tclone\tparent\tccf\tgap\tmode\tfound\n")
    for r in rows_out:
        fh.write("\t".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in r) + "\n")
with open(HERE / "oracle_pairs_clone_pairs.tsv", "w") as fh:
    fh.write("snvs_per_mb\ttree\tclone_a\tclone_b\trelation\tccf_diff\tn_a\tn_b\tcross_pairs\tstat_counts\tstat_counts_pairs\tthreshold\n")
    for r in pair_rows:
        fh.write("\t".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in r) + "\n")

print("Part A: clones found (80/80), mean of 10 trees, 5 true clones, 60x, purity 0.9, A1 counts")
print("SNVs/Mb  pairs/tree  counts  joint  joint_from_truth  nbr_known")
for dens, npr, f in summary:
    print(f"{dens:>7}  {npr:>10.0f}  {f['counts']:>6.2f}  {f['joint']:>5.2f}  {f['joint_from_truth']:>16.2f}  {f['nbr']:>9.2f}")
print("\nnon-truncal clones found by CCF gap to the nearest other clone")
for mode in ("counts", "joint", "joint_from_truth", "nbr"):
    print(f" {mode}")
    for dens, _ in SETS:
        cells = []
        for lab, lo, hi in BINS:
            rr = [r for r in rows_out if r[0] == dens and r[6] == mode and r[3] != "root" and lo <= r[5] < hi]
            cells.append(f"{lab} {sum(r[7] for r in rr)}/{len(rr)} ({sum(r[7] for r in rr) / max(len(rr), 1):.0%})")
        print(f"   {dens:>5}/Mb  " + "   ".join(cells))

print("\nPart B: close clone pairs (CCF diff < 0.1) where the data prefer two clones over one (BIC)")
print("SNVs/Mb  relation  ccf_diff   n   median cross pairs   counts only   counts + pairs")
for dens, _ in SETS:
    for r_ in ("sib", "anc"):
        for lab, lo, hi in BINS[:2]:
            rr = [r for r in pair_rows if r[0] == dens and r[4] == r_ and lo <= r[5] < hi]
            if rr:
                print(f"{dens:>7}  {r_:<8}  {lab:<8} {len(rr):>3}   {st.median(r[8] for r in rr):>18.0f}   "
                      f"{sum(r[9] > r[11] for r in rr):>6}/{len(rr)}   {sum(r[10] > r[11] for r in rr):>9}/{len(rr)}")
    rr = [r for r in pair_rows if r[0] == dens]
    print(f"{dens:>7}  all                {len(rr):>3}   {st.median(r[8] for r in rr):>18.0f}   "
          f"{sum(r[9] > r[11] for r in rr):>6}/{len(rr)}   {sum(r[10] > r[11] for r in rr):>9}/{len(rr)}")

print("\nlog-posterior of joint_from_truth minus joint, per tree (> 0: the answer near the truth scores higher)")
for dens, _ in SETS:
    d = [g for dd, _, g in lp_gain if dd == dens]
    print(f"{dens:>7}  " + " ".join(f"{g:+.0f}" for g in d) + f"   trees > 0: {sum(g > 1e-6 for g in d)}/10")
