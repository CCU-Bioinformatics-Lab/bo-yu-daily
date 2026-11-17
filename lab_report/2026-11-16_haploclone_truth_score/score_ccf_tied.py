"""Option A offline (README §9): pair proportions tied to the node CCFs, for truth / MAP / over-split trees.

Usage: python3 -I score_ccf_tied.py BATCH_ROOT > ccf_tied_summary.txt   (writes ccf_tied.tsv)
"""
import csv
import math
import statistics as st
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
SCORE = "/bip8_disk/boyu114/haploclone/rust/target/release/examples/score_tree"
SETS = [("5.3", "center"), ("20", "d20"), ("50", "d50"), ("100", "d100")]
PRIORS = ["crp:1", "crp:0.5", "crp:0.2", "crp:0.05", "uniform", "py:0.25", "py:0.5", "py:0.75"]
MODE, USABLE, EPS = "a1c4pool", 15, 0.01
LE, L1E, L2E = math.log(EPS), math.log1p(-EPS), math.log1p(-2 * EPS)


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def parse_newick(text):   # same as score_truth.py
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


def lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def pair_terms(assign, parent, counts, t, pairs):
    """(current pooled score, CCF-tied score) of a tree."""
    K, N = {}, {}
    for m, c in assign.items():
        K[c] = K.get(c, 0) + counts[m][0]
        N[c] = N.get(c, 0) + counts[m][1]
    ccf = {c: min(K[c] / max(N[c] * t, 1e-9), 1.0) for c in K}

    def anc(c):
        out = set()
        while parent[c] != "root":
            c = parent[c]
            out.add(c)
        return out

    A = {c: anc(c) for c in ccf}
    same = 0.0
    groups = {}   # (upper or first node, other node, is_ancestor) -> [n11, n_first_only, n_other_only]
    for i, j, n11, n10, n01 in pairs:
        a, b = assign[i], assign[j]
        if a == b:
            same += (n10 + n01) * LE + n11 * L2E
            continue
        if b in A[a]:              # b is the ancestor: orient the ancestor first
            a, b, n10, n01 = b, a, n01, n10
        is_anc = a in A[b]
        if not is_anc and a > b:   # branch: fixed orientation
            a, b, n10, n01 = b, a, n01, n10
        g = groups.setdefault((a, b, is_anc), [0, 0, 0])
        g[0] += n11
        g[1] += n10
        g[2] += n01
    cur = tied = same
    for (a, b, is_anc), (n11, n10, n01) in groups.items():
        clip = lambda x: min(max(x, EPS), 1 - EPS)
        if is_anc:
            rho = clip((ccf[a] - ccf[b]) / max(ccf[a], 1e-9))
            base = n01 * LE + (n11 + n10) * L1E
            cur += base + lbeta(n11 + 1, n10 + 1)
            tied += base + n10 * math.log(rho) + n11 * math.log(1 - rho)
        else:
            rho = clip(ccf[a] / max(ccf[a] + ccf[b], 1e-9))
            base = n11 * LE + (n10 + n01) * L1E
            cur += base + lbeta(n10 + 1, n01 + 1)
            tied += base + n10 * math.log(rho) + n01 * math.log(1 - rho)
    return cur, tied


def score(inp, assign, parent, alpha, tmp, tag, counts, t, pairs):
    fa, ft = Path(tmp) / f"{tag}_a.tsv", Path(tmp) / f"{tag}_t.tsv"
    fa.write_text("mutation_id\tnode\n" + "".join(f"{m}\t{c}\n" for m, c in assign.items()))
    ft.write_text("node\tparent\n" + "".join(f"{c}\t{p}\n" for c, p in parent.items()))
    out = subprocess.run([SCORE, inp / "data_hp.tsv", inp / "segments.tsv", inp / "pairs.tsv", fa, ft, repr(alpha), "pool",
                          ",".join(PRIORS)], check=True, capture_output=True, text=True).stdout.splitlines()
    base = dict(zip(out[0].split("\t"), map(float, out[1].split("\t"))))
    pri = {l.split("\t")[1]: float(l.split("\t")[2]) for l in out[2:]}
    cur, tied = pair_terms(assign, parent, counts, t, pairs)
    return dict(data=base["data"], pri=pri, cur=cur, tied=tied, check=abs(cur - base["pair"]))


def oversplit(truth, tpar, counts):   # same rule as score_priors.py
    sizes = {}
    for c in truth.values():
        sizes[c] = sizes.get(c, 0) + 1
    c = max((k for k in sizes if tpar[k] != "root"), key=lambda k: sizes[k])
    ms = [m for m in truth if truth[m] == c]
    order = sorted(ms, key=lambda m: -(counts[m][0] / max(counts[m][1], 1)))
    low = set(order[len(order) // 2:])
    assign = {m: ("split" if m in low else k) for m, k in truth.items()}
    par = {k: ("split" if p == c else p) for k, p in tpar.items()}
    par["split"] = c
    return assign, par


def one(job):
    dens, name, s, h = job
    W = ROOT / name / "work"
    inp, run = W / f"in{s}", W / f"run_s{s}_{MODE}_h{h}"
    truth = {r["mutation_id"]: r["clone"] for r in read(inp / "truth.tsv")}
    tpar = {r["clone"]: r["parent"] for r in read(inp / "truth_tree.tsv")}
    mp = {r["mutation_id"]: r["clone_id"] for r in read(f"{run}_map.tsv")}
    used = set(mp.values())
    mpar = {c: p for c, p in parse_newick(open(f"{run}_map.nwk").read()).items() if c in used}
    alpha = float(max(read(run / "iterations.tsv"), key=lambda r: float(r["log_p"]))["alpha"])
    counts, t, hp = {}, None, {}
    for r in read(inp / "data_hp.tsv"):
        t = float(r["tumour_content"])
        hp[r["mutation_id"]] = r["snv_hp"]
        x = "1" if r["snv_hp"] == "HP1" else "2"
        counts[r["mutation_id"]] = (int(r[f"alt_hp{x}"]), int(r[f"alt_hp{x}"]) + int(r[f"ref_hp{x}"]))
    pairs = [(r["mutation_i"], r["mutation_j"], int(r["n11"]), int(r["n10"]), int(r["n01"])) for r in read(inp / "pairs.tsv")
             if hp[r["mutation_i"]] == r["hap"] == hp[r["mutation_j"]]]   # haploclone's eligibility (pairs.rs from_files)
    oa, op = oversplit(truth, tpar, counts)
    with tempfile.TemporaryDirectory() as tmp:
        f = lambda a, p, tag: score(inp, a, p, alpha, tmp, tag, counts, t, pairs)
        return dict(dens=dens, tree=s, seed=h, truth=f(truth, tpar, "t"), map=f(mp, mpar, "m"), over=f(oa, op, "o"))


jobs = [(d, n, s, h) for d, n in SETS for s in range(1, 11) for h in (1, 2)]
with ThreadPoolExecutor(16) as ex:
    res = list(ex.map(one, jobs))

tot = lambda x, p, k: x["data"] + x["pri"][p] + x[k]
print("check: max |python current pair score - score_tree pair score| =",
      f"{max(r[k]['check'] for r in res for k in ('truth', 'map', 'over')):.2e}")
with open(HERE / "ccf_tied.tsv", "w") as fh:
    fh.write("snvs_per_mb\ttree\tseed\tprior\tpair_score\ttruth_minus_map\ttruth_minus_oversplit\n")
    for r in res:
        for p in PRIORS:
            for k in ("cur", "tied"):
                fh.write(f"{r['dens']}\t{r['tree']}\t{r['seed']}\t{p}\t{k}\t{tot(r['truth'], p, k) - tot(r['map'], p, k):.2f}\t"
                         f"{tot(r['truth'], p, k) - tot(r['over'], p, k):.2f}\n")

print("\npair term alone, truth minus other tree (median of 20): current score -> CCF-tied score")
print("SNVs/Mb   vs MAP              vs over-split")
for d, _ in SETS:
    rr = [r for r in res if r["dens"] == d]
    m = lambda o, k: st.median(r["truth"][k] - r[o][k] for r in rr)
    print(f"{d:>7}   {m('map', 'cur'):>+7.1f} -> {m('map', 'tied'):>+7.1f}   {m('over', 'cur'):>+7.1f} -> {m('over', 'tied'):>+7.1f}")

print("\nCCF-tied pair score: runs (of 20) where the total score prefers the truth")
print("SNVs/Mb  prior      truth>MAP (median)   truth>oversplit (median)   both   usable(>=15)   [both, current score]")
for d, _ in SETS:
    rr = [r for r in res if r["dens"] == d]
    for p in PRIORS:
        a = [tot(r["truth"], p, "tied") - tot(r["map"], p, "tied") for r in rr]
        b = [tot(r["truth"], p, "tied") - tot(r["over"], p, "tied") for r in rr]
        both = sum(x > 0 and y > 0 for x, y in zip(a, b))
        old = sum(tot(r["truth"], p, "cur") > tot(r["map"], p, "cur") and tot(r["truth"], p, "cur") > tot(r["over"], p, "cur") for r in rr)
        print(f"{d:>7}  {p:<9}  {sum(x > 0 for x in a):>3}/20 ({st.median(a):>+7.1f})     {sum(x > 0 for x in b):>3}/20 ({st.median(b):>+7.1f})"
              f"        {both:>2}/20   {'yes' if both >= USABLE else 'no':<3}            [{old}/20]")
    print()
