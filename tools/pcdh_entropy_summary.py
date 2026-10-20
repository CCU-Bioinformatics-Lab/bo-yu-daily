"""Summarise pcdh_entropy.py outputs per cell line (tumor vs normal).

usage: python3 pcdh_entropy_summary.py LINE:TUMOR_TSV:NORMAL_TSV [...] > OUT_TSV

Columns: window counts, median mean_meth and entropy, fraction of tumor
windows <= 1 bit, tumor mid-methylation (0.4-0.8) window count, shared-window
tumor-minus-normal entropy, and median methylation per PCDH sub-cluster.
First used in lab_report/2026-10-20_pcdh_entropy_panel/.
"""
import sys, csv, statistics as st

SUB = {"alpha": (140.78e6, 141.02e6), "beta": (141.05e6, 141.25e6),
       "gamma": (141.33e6, 141.52e6)}   # GRCh38, approx


def load(f):
    return {int(r["win_start"]): r for r in csv.DictReader(open(f), delimiter="\t")}


def col(d, ks, c):
    return [float(d[k][c]) for k in ks]


def sub_meth(d):
    out = []
    for a, b in SUB.values():
        ks = [k for k in d if a <= k < b]
        out.append(f"{st.median(col(d, ks, 'mean_meth')):.2f}" if ks else "NA")
    return "/".join(out)


head = ["line", "tumor_windows", "normal_windows", "tumor_meth", "normal_meth",
        "tumor_entropy", "tumor_entropy_q1", "tumor_entropy_q3", "normal_entropy",
        "tumor_le1bit_frac", "tumor_mid_meth_windows", "shared_windows",
        "shared_tumor_lower", "shared_entropy_diff",
        "tumor_meth_alpha/beta/gamma", "normal_meth_alpha/beta/gamma"]
print("\t".join(head))
for arg in sys.argv[1:]:
    line, tf, nf = arg.split(":")
    T, N = load(tf), load(nf)
    et = col(T, T, "entropy_sub20")
    q = st.quantiles(et, n=4)
    sh = sorted(set(T) & set(N))
    d = [a - b for a, b in zip(col(T, sh, "entropy_sub20"), col(N, sh, "entropy_sub20"))]
    mid = sum(0.4 <= float(r["mean_meth"]) < 0.8 for r in T.values())
    row = [line, len(T), len(N),
           f"{st.median(col(T, T, 'mean_meth')):.2f}", f"{st.median(col(N, N, 'mean_meth')):.2f}",
           f"{st.median(et):.2f}", f"{q[0]:.2f}", f"{q[2]:.2f}",
           f"{st.median(col(N, N, 'entropy_sub20')):.2f}",
           f"{sum(x <= 1 for x in et) / len(et):.2f}", mid, len(sh),
           sum(x < 0 for x in d), f"{st.median(d):+.2f}", sub_meth(T), sub_meth(N)]
    print("\t".join(map(str, row)))
