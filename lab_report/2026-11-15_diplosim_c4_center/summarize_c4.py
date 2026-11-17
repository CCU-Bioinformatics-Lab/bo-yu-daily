"""Score one batch directory by mode (README §2): clones found (80/80), exact trees, diff vs a1 with t CI,
and the share of non-truncal clones found by CCF gap to the nearest other clone.

Rules are those of ../2026-11-14_diplosim_haploclone_ofat/summarize_ofat.py (copied here because that
script runs on import). Usage: python3 -I summarize_c4.py BATCH_DIR [modes, default a1,a1c4,a1c4pool]
"""
import collections as co
import csv
import statistics as st
import sys
from pathlib import Path

W = Path(sys.argv[1]) / "work"
MODES = (sys.argv[2] if len(sys.argv) > 2 else "a1,a1c4,a1c4pool").split(",")
REC, PREC, MIN_GAIN, T975 = 0.8, 0.8, 0.3, 2.262   # t quantile for 10 trees
BINS = [("<0.05", 0, .05), ("0.05-0.1", .05, .10), ("0.1-0.2", .10, .20), (">=0.2", .20, 9)]


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def parse_newick(text):
    text = text.strip().rstrip(";")
    parent, i, kids = {}, 0, [[]]
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
    n_true, n_rec = co.Counter(truth.values()), co.Counter(mp.values())
    pair = co.Counter((truth[m], mp[m]) for m in truth)
    match = {}
    for c in n_true:
        best = max((k for k in pair if k[0] == c), key=lambda k: pair[k])
        if pair[best] / n_true[c] >= REC and pair[best] / n_rec[best[1]] >= PREC:
            match[c] = best[1]
    exact = len(match) == len(n_true) == len(n_rec) and len(set(match.values())) == len(match)
    if exact:
        exact = all(rparent.get(k) == ("root" if tparent[c] == "root" else match[tparent[c]]) for c, k in match.items())
    return match, exact


trees = sorted(int(p.name[2:]) for p in W.glob("in*") if p.is_dir())
found = {m: {} for m in MODES}
exact = co.Counter()
bins = {m: co.defaultdict(lambda: [0, 0]) for m in MODES}
for s in trees:
    truth = {r["mutation_id"]: r["clone"] for r in read(W / f"in{s}/truth.tsv")}
    tt = read(W / f"in{s}/truth_tree.tsv")
    tparent = {r["clone"]: r["parent"] for r in tt}
    ccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
    gap = {c: min(abs(v - o) for k, o in ccf.items() if k != c) for c, v in ccf.items()}
    for m in MODES:
        vals = []
        for h in (1, 2):
            run = W / f"run_s{s}_{m}_h{h}"
            mp = {r["mutation_id"]: r["clone_id"] for r in read(f"{run}_map.tsv")}
            match, ex = one_run(truth, tparent, mp, parse_newick(open(f"{run}_map.nwk").read()))
            vals.append(len(match))
            exact[m] += ex
            for c in ccf:
                if tparent[c] == "root":
                    continue
                b = next(lab for lab, lo, hi in BINS if lo <= gap[c] < hi)
                bins[m][b][0] += c in match
                bins[m][b][1] += 1
        found[m][s] = st.mean(vals)

n = len(trees)
print(f"{n} trees x 2 haploclone seeds; true clones 5")
print("mode       found   exact   diff vs a1 [95% CI]        better/worse  improves?")
for m in MODES:
    line = f"{m:<10} {st.mean(found[m].values()):>5.2f}   {exact[m]:>2}/{2 * n}"
    if m != "a1" and "a1" in MODES:
        d = [found[m][s] - found["a1"][s] for s in trees]
        mu = st.mean(d)
        h = T975 * st.stdev(d) / n ** 0.5 if n > 1 else float("nan")
        verdict = "yes" if mu >= MIN_GAIN and mu - h > 0 else "no"
        line += f"   {mu:+.2f} [{mu - h:+.2f}, {mu + h:+.2f}]      {sum(x > 0 for x in d)}/{sum(x < 0 for x in d)}          {verdict}"
    print(line)
print("\nnon-truncal clones found, by CCF gap to the nearest other clone (both seeds)")
for m in MODES:
    print(f"  {m:<10} " + "   ".join(f"{lab} {bins[m][lab][0]}/{bins[m][lab][1]} ({bins[m][lab][0] / max(bins[m][lab][1], 1):.0%})" for lab, _, _ in BINS))
print("\nper tree found (mean of 2 seeds):")
for s in trees:
    print(f"  tree {s:>2}: " + "  ".join(f"{m} {found[m][s]:.1f}" for m in MODES))
