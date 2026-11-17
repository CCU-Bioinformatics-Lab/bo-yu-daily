"""Clone-level scoring (README §6): haploclone MAP vs two mixture-model ceilings, no per-SNV rule.

Run with numpy available (user site, so not -I): python3 group_level.py OUT_ROOT > group_level_summary.txt
"""
import csv
import math
import statistics as st
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-11-14_diplosim_haploclone_ofat"))
ROOT = Path(sys.argv[1])
TOL, ERR, N_RAND = 0.05, 1e-3, 20
CELLS = ["c01_center", "c02_depth30", "c03_depth120", "c04_depth400", "c05_pur0.3", "c06_pur0.5",
         "c07_pur0.7", "c08_clone3", "c09_clone8", "c10_clone12", "c11_snv5000"]
rng = np.random.default_rng(20261115)


def read(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def parse_newick(text):   # same as summarize_ofat.parse_newick (that module runs on import)
    text = text.strip().rstrip(";")
    parent, i, kids = {}, 0, [[]]
    while i < len(text):
        ch = text[i]
        if ch == "(":
            kids.append([]); i += 1
        elif ch in ",)":
            i += 1
            if ch == ")":
                j = i
                while j < len(text) and text[j] not in ",()":
                    j += 1
                name = text[i:j]; i = j
                for k in kids.pop():
                    parent[k] = name
                kids[-1].append(name)
        else:
            j = i
            while j < len(text) and text[j] not in ",()":
                j += 1
            kids[-1].append(text[i:j]); i = j
    return parent


def match(true_ccf, rec_ccf):
    """Order-preserving one-to-one matching (optimal for 1-D |diff|) of min(n, m) pairs. Returns {true: rec}."""
    T = sorted(true_ccf, key=true_ccf.get)
    R = sorted(rec_ccf, key=rec_ccf.get)
    swap = len(T) > len(R)
    A, B, ca, cb = (R, T, rec_ccf, true_ccf) if swap else (T, R, true_ccf, rec_ccf)
    n, m = len(A), len(B)   # n <= m: every A gets one B
    INF = float("inf")
    f = [[INF] * (m + 1) for _ in range(n + 1)]
    f[0] = [0.0] * (m + 1)
    for i in range(1, n + 1):
        for j in range(i, m + 1):
            f[i][j] = min(f[i][j - 1], f[i - 1][j - 1] + abs(ca[A[i - 1]] - cb[B[j - 1]]))
    pairs, i, j = {}, n, m
    while i > 0:
        if j > i and f[i][j] == f[i][j - 1]:
            j -= 1
        else:
            pairs[A[i - 1]] = B[j - 1]; i -= 1; j -= 1
    return {b: a for a, b in pairs.items()} if swap else pairs


def score(true_ccf, tparent, rec_ccf, rparent=None):
    mp = match(true_ccf, rec_ccf)
    found = {c for c, r in mp.items() if abs(true_ccf[c] - rec_ccf[r]) <= TOL}
    count_ok = len(rec_ccf) == len(true_ccf)
    tree_ok = None
    if rparent is not None:
        tree_ok = count_ok and len(found) == len(true_ccf) and all(
            rparent.get(mp[c]) == ("root" if tparent[c] == "root" else mp[tparent[c]]) for c in true_ccf)
    return len(found), count_ok, tree_ok


def em(k, n, scale, init, iters=300):
    """Binomial mixture over CCF; returns (loglik, ccfs)."""
    f = np.array(init, float)
    w = np.full(len(f), 1 / len(f))
    lc = np.array([math.lgamma(a + 1) for a in n]) - np.array([math.lgamma(a + 1) for a in k]) \
        - np.array([math.lgamma(a + 1) for a in n - k])
    prev = -np.inf
    for _ in range(iters):
        p = np.clip(scale[:, None] * f[None, :], ERR, 1 - ERR)
        ll = lc[:, None] + k[:, None] * np.log(p) + (n - k)[:, None] * np.log1p(-p) + np.log(w + 1e-300)[None, :]
        mx = ll.max(1, keepdims=True)
        tot = mx[:, 0] + np.log(np.exp(ll - mx).sum(1))
        cur = tot.sum()
        r = np.exp(ll - tot[:, None])
        w = r.mean(0)
        num, den = (r * k[:, None]).sum(0), (r * (n * scale)[:, None]).sum(0)
        f = np.clip(np.where(den > 0, num / np.maximum(den, 1e-300), f), 0.0, 1.0)
        if cur - prev < 1e-6:
            break
        prev = cur
    return cur, f


def best_em(k, n, scale, K, extra=None):
    starts = [np.sort(rng.uniform(0.02, 1.0, K)) for _ in range(N_RAND)] + ([extra] if extra is not None else [])
    return max((em(k, n, scale, s) for s in starts), key=lambda x: x[0])


print("cell          true | haploclone found base/a1  count_ok  tree_ok | ceilA(K known) found base/a1"
      " | ceilB(BIC) found base/a1  K_ok")
for cell in CELLS:
    W = ROOT / cell / "work"
    acc = {key: [] for key in ("hc_f_base", "hc_f_a1", "hc_c_base", "hc_c_a1", "hc_t_base", "hc_t_a1",
                               "A_base", "A_a1", "B_base", "B_a1", "Bk_base", "Bk_a1")}
    ntrue = []
    for s in range(1, 11):
        tt = read(W / f"in{s}/truth_tree.tsv")
        tccf = {r["clone"]: float(r["true_ccf"]) for r in tt}
        tpar = {r["clone"]: r["parent"] for r in tt}
        ntrue.append(len(tccf))
        for mode, fname in (("base", "data.tsv"), ("a1", "data_hp.tsv")):
            f_, c_, t_ = [], [], []
            for h in (1, 2):
                run = W / f"run_s{s}_{mode}_h{h}"
                rows = read(f"{run}_map.tsv")
                rccf = {r["clone_id"]: float(r["ccf"]) for r in rows}
                fo, co_, tr = score(tccf, tpar, rccf, parse_newick(open(f"{run}_map.nwk").read()))
                f_.append(fo); c_.append(co_); t_.append(tr)
            acc[f"hc_f_{mode}"].append(st.mean(f_)); acc[f"hc_c_{mode}"].append(sum(c_)); acc[f"hc_t_{mode}"].append(sum(t_))
            # counts for the mixture ceilings
            ks, ns, sc = [], [], []
            for r in read(W / f"in{s}/{fname}"):
                t = float(r["tumour_content"])
                if mode == "base":
                    ks.append(int(r["alt_counts"])); ns.append(int(r["ref_counts"]) + int(r["alt_counts"])); sc.append(t / 2)
                else:
                    h = "1" if r["snv_hp"] == "HP1" else "2"
                    ks.append(int(r[f"alt_hp{h}"])); ns.append(int(r[f"ref_hp{h}"]) + int(r[f"alt_hp{h}"])); sc.append(t)
            k, n, scale = np.array(ks, float), np.array(ns, float), np.array(sc)
            K = len(tccf)
            _, fA = best_em(k, n, scale, K, extra=np.array(sorted(tccf.values())))
            acc[f"A_{mode}"].append(score(tccf, tpar, {str(i): v for i, v in enumerate(fA)})[0])
            best = None
            for Kc in range(1, K + 4):
                ll, fB = best_em(k, n, scale, Kc)
                bic = -2 * ll + (2 * Kc - 1) * math.log(len(k))
                if best is None or bic < best[0]:
                    best = (bic, fB)
            fo, co_, _ = score(tccf, tpar, {str(i): v for i, v in enumerate(best[1])})
            acc[f"B_{mode}"].append(fo); acc[f"Bk_{mode}"].append(len(best[1]))
    m = {k2: st.mean(v) for k2, v in acc.items()}
    kok = {md: sum(a == b for a, b in zip(acc[f"Bk_{md}"], ntrue)) for md in ("base", "a1")}
    print(f"{cell:<13} {st.mean(ntrue):>4.0f} | {m['hc_f_base']:>12.2f}/{m['hc_f_a1']:.2f}"
          f"  {sum(acc['hc_c_base']):>3}/{sum(acc['hc_c_a1'])}/20  {sum(acc['hc_t_base']):>2}/{sum(acc['hc_t_a1'])}/20 |"
          f" {m['A_base']:>13.2f}/{m['A_a1']:.2f} | {m['B_base']:>14.2f}/{m['B_a1']:.2f}"
          f"  {kok['base']}/{kok['a1']}/10 (mean K {m['Bk_base']:.1f}/{m['Bk_a1']:.1f})", flush=True)
