"""Truth vs MAP vs an over-split control under several tree priors (README §8).

Usage: python3 -I score_priors.py BATCH_ROOT > priors_summary.txt   (writes priors.tsv)
"""
import csv
import statistics as st
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], sys.argv[1]]
SCORE = "/bip8_disk/boyu114/haploclone/rust/target/release/examples/score_tree"
SETS = [("5.3", "center"), ("20", "d20"), ("50", "d50"), ("100", "d100")]
PRIORS = ["crp:1", "crp:0.5", "crp:0.2", "crp:0.05", "uniform", "py:0.25", "py:0.5", "py:0.75"]
MODE, USABLE = "a1c4pool", 15


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


def score(inp, assign, parent, alpha, tmp, tag):
    fa, ft = Path(tmp) / f"{tag}_a.tsv", Path(tmp) / f"{tag}_t.tsv"
    fa.write_text("mutation_id\tnode\n" + "".join(f"{m}\t{c}\n" for m, c in assign.items()))
    ft.write_text("node\tparent\n" + "".join(f"{c}\t{p}\n" for c, p in parent.items()))
    out = subprocess.run([SCORE, inp / "data_hp.tsv", inp / "segments.tsv", inp / "pairs.tsv", fa, ft, repr(alpha), "pool",
                          ",".join(PRIORS)], check=True, capture_output=True, text=True).stdout.splitlines()
    base = dict(zip(out[0].split("\t"), map(float, out[1].split("\t"))))
    pri = {l.split("\t")[1]: float(l.split("\t")[2]) for l in out[2:]}
    assert abs(pri["crp:1"] - base["prior"]) < 1e-3
    return {p: base["data"] + base["pair"] + v for p, v in pri.items()}


def oversplit(truth, tpar, inp):
    sizes = {}
    for c in truth.values():
        sizes[c] = sizes.get(c, 0) + 1
    c = max((k for k in sizes if tpar[k] != "root"), key=lambda k: sizes[k])
    vaf = {}
    for r in read(inp / "data_hp.tsv"):
        if truth[r["mutation_id"]] == c:
            h = "1" if r["snv_hp"] == "HP1" else "2"
            a, n = int(r[f"alt_hp{h}"]), int(r[f"alt_hp{h}"]) + int(r[f"ref_hp{h}"])
            vaf[r["mutation_id"]] = a / max(n, 1)
    order = sorted(vaf, key=lambda m: -vaf[m])
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
    oa, op = oversplit(truth, tpar, inp)
    with tempfile.TemporaryDirectory() as tmp:
        return dict(dens=dens, tree=s, seed=h, truth=score(inp, truth, tpar, alpha, tmp, "t"),
                    map=score(inp, mp, mpar, alpha, tmp, "m"), over=score(inp, oa, op, alpha, tmp, "o"))


jobs = [(d, n, s, h) for d, n in SETS for s in range(1, 11) for h in (1, 2)]
with ThreadPoolExecutor(16) as ex:
    res = list(ex.map(one, jobs))

with open(HERE / "priors.tsv", "w") as fh:
    fh.write("snvs_per_mb\ttree\tseed\tprior\ttruth_minus_map\ttruth_minus_oversplit\n")
    for r in res:
        for p in PRIORS:
            fh.write(f"{r['dens']}\t{r['tree']}\t{r['seed']}\t{p}\t{r['truth'][p] - r['map'][p]:.2f}\t{r['truth'][p] - r['over'][p]:.2f}\n")

print("runs (of 20) where the score prefers the truth; medians of truth minus the other tree")
print("SNVs/Mb  prior      truth>MAP (median)   truth>oversplit (median)   both   usable(>=15)")
for d, _ in SETS:
    rr = [r for r in res if r["dens"] == d]
    for p in PRIORS:
        a = [r["truth"][p] - r["map"][p] for r in rr]
        b = [r["truth"][p] - r["over"][p] for r in rr]
        both = sum(x > 0 and y > 0 for x, y in zip(a, b))
        print(f"{d:>7}  {p:<9}  {sum(x > 0 for x in a):>3}/20 ({st.median(a):>+7.1f})     {sum(x > 0 for x in b):>3}/20 ({st.median(b):>+7.1f})"
              f"        {both:>2}/20   {'yes' if both >= USABLE else 'no'}")
    print()
