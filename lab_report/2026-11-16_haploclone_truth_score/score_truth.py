"""Score the truth tree and the haploclone MAP tree with haploclone's own target (README §2).

Usage: python3 -I score_truth.py BATCH_ROOT > truth_vs_map_summary.txt   (writes truth_vs_map.tsv)
"""
import collections as co
import csv
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
MODE, REC, PREC = "a1c4pool", 0.8, 0.8


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def parse_newick(text):   # same as ../2026-11-15_diplosim_c4_center/summarize_c4.py
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


def n_found(truth, mp):
    n_true, n_rec = co.Counter(truth.values()), co.Counter(mp.values())
    pair = co.Counter((truth[m], mp[m]) for m in truth)
    k = 0
    for c in n_true:
        b = max((x for x in pair if x[0] == c), key=lambda x: pair[x])
        k += pair[b] / n_true[c] >= REC and pair[b] / n_rec[b[1]] >= PREC
    return k


def score(inp, assign, parent, alpha, tmp, tag):
    fa, ft = Path(tmp) / f"{tag}_a.tsv", Path(tmp) / f"{tag}_t.tsv"
    fa.write_text("mutation_id\tnode\n" + "".join(f"{m}\t{c}\n" for m, c in assign.items()))
    ft.write_text("node\tparent\n" + "".join(f"{c}\t{p}\n" for c, p in parent.items()))
    out = subprocess.run([SCORE, inp / "data_hp.tsv", inp / "segments.tsv", inp / "pairs.tsv", fa, ft, repr(alpha), "pool"],
                         check=True, capture_output=True, text=True).stdout.splitlines()
    return dict(zip(out[0].split("\t"), map(float, out[1].split("\t"))))


def one(job):
    dens, name, s, h = job
    W = ROOT / name / "work"
    inp, run = W / f"in{s}", W / f"run_s{s}_{MODE}_h{h}"
    truth = {r["mutation_id"]: r["clone"] for r in read(inp / "truth.tsv")}
    tpar = {r["clone"]: r["parent"] for r in read(inp / "truth_tree.tsv")}
    mp = {r["mutation_id"]: r["clone_id"] for r in read(f"{run}_map.tsv")}
    used = set(mp.values())
    mpar = {c: p for c, p in parse_newick(open(f"{run}_map.nwk").read()).items() if c in used}
    its = read(run / "iterations.tsv")
    best = max(its, key=lambda r: float(r["log_p"]))
    alpha = float(best["alpha"])
    with tempfile.TemporaryDirectory() as tmp:
        t = score(inp, truth, tpar, alpha, tmp, "truth")
        m = score(inp, mp, mpar, alpha, tmp, "map")
    return dict(dens=dens, tree=s, seed=h, alpha=alpha, found=n_found(truth, mp), trace_map=float(best["log_p"]), truth=t, map=m)


jobs = [(d, n, s, h) for d, n in SETS for s in range(1, 11) for h in (1, 2)]
with ThreadPoolExecutor(16) as ex:
    res = list(ex.map(one, jobs))

PARTS = ("log_p_one", "prior", "data", "pair")
with open(HERE / "truth_vs_map.tsv", "w") as fh:
    fh.write("snvs_per_mb\ttree\tseed\talpha\tmap_found\tmap_nodes\tmap_rescored_minus_trace\t" + "\t".join(f"truth_minus_map_{p}" for p in PARTS) + "\n")
    for r in res:
        fh.write(f"{r['dens']}\t{r['tree']}\t{r['seed']}\t{r['alpha']:.4f}\t{r['found']}\t{int(r['map']['num_nodes'])}\t"
                 f"{r['map']['log_p_one'] - r['trace_map']:.2e}\t" + "\t".join(f"{r['truth'][p] - r['map'][p]:.2f}" for p in PARTS) + "\n")

print("check: max |rescored MAP - trace MAP| =", f"{max(abs(r['map']['log_p_one'] - r['trace_map']) for r in res):.2e}")
print("\ntruth minus MAP, haploclone's own score (a1c4pool; 10 trees x 2 seeds per density)")
print("SNVs/Mb  runs  truth>MAP  median total   median prior   data    pair")
for d, _ in SETS:
    for lab, sel in (("all", lambda r: True), ("MAP found 5", lambda r: r["found"] == 5), ("MAP found <5", lambda r: r["found"] < 5)):
        rr = [r for r in res if r["dens"] == d and sel(r)]
        if not rr:
            continue
        df = {p: [r["truth"][p] - r["map"][p] for r in rr] for p in PARTS}
        print(f"{d:>7}  {len(rr):>4}  {sum(x > 0 for x in df['log_p_one']):>6}/{len(rr):<3} {st.median(df['log_p_one']):>12.1f}   "
              f"{st.median(df['prior']):>12.1f}  {st.median(df['data']):>6.1f}  {st.median(df['pair']):>6.1f}   {lab}")
print("\nper run at 100 SNVs/Mb: tree seed found nodes | truth-MAP total prior data pair")
for r in res:
    if r["dens"] == "100":
        print(f"  {r['tree']:>2} {r['seed']}  {r['found']} {int(r['map']['num_nodes'])} | " + "  ".join(f"{r['truth'][p] - r['map'][p]:>8.1f}" for p in PARTS))
