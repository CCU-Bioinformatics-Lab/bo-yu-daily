"""Summarise pcdh_longread_matrix.py outputs by sample x HP.

usage: python3 pcdh_longread_summary.py TSV [TSV ...]

Per group: window count, median matrix size, median z (column-permutation
null) and z_ff (fixed row/column-sum null), fraction of windows with
p_ff <= 0.01, median top-split minor fraction. Then paired z_ff comparisons on
shared windows, and the per-window HP1 vs HP2 minor fractions in each sample
(a subclone should split both haplotypes at a similar fraction).
First used in lab_report/2026-10-21_h1437_pcdh_longread_matrix/.
"""
import sys, csv, statistics as st
from collections import defaultdict

rows = [r for f in sys.argv[1:] for r in csv.DictReader(open(f), delimiter="\t")]
groups = defaultdict(list)
idx = {}
for r in rows:
    groups[(r["label"], r["hp"])].append(r)
    idx[(r["label"], r["hp"], r["win_start"])] = r


def med(rs, c):
    return st.median(float(r[c]) for r in rs)


print("label\thp\twindows\tn_cpgs\tn_reads\tmean_meth\tz_col\tz_ff\tsig_ff\tminor_frac")
for (lab, hp), rs in sorted(groups.items()):
    sig = sum(float(r["p_ff"]) <= 0.01 for r in rs) / len(rs)
    print(f"{lab}\t{hp}\t{len(rs)}\t{med(rs, 'n_cpgs'):.0f}\t{med(rs, 'n_reads'):.0f}\t"
          f"{med(rs, 'mean_meth'):.2f}\t{med(rs, 'z'):.2f}\t{med(rs, 'z_ff'):.2f}\t{sig:.2f}\t"
          f"{med(rs, 'top_minor_frac'):.3f}")


def paired(a, b):
    ws = [r["win_start"] for r in groups[a] if (*b, r["win_start"]) in idx]
    if not ws:
        return
    za = [float(idx[(*a, w)]["z_ff"]) for w in ws]
    zb = [float(idx[(*b, w)]["z_ff"]) for w in ws]
    hi = sum(x > y for x, y in zip(za, zb))
    print(f"{a[0]} {a[1]} vs {b[0]} {b[1]}\tshared={len(ws)}\tz_ff {st.median(za):.2f} vs "
          f"{st.median(zb):.2f}\tfirst_higher={hi}/{len(ws)}")


labels = sorted({k[0] for k in groups})
print()
for lab in labels:
    paired((lab, "HP1"), (lab, "HP2"))
for i, a in enumerate(labels):
    for b in labels[i + 1:]:
        for hp in ("HP1", "HP2"):
            paired((a, hp), (b, hp))

print()
for lab in labels:
    ws = [r["win_start"] for r in groups[(lab, "HP1")] if (lab, "HP2", r["win_start"]) in idx]
    if len(ws) < 3:
        continue
    m1 = [float(idx[(lab, "HP1", w)]["top_minor_frac"]) for w in ws]
    m2 = [float(idx[(lab, "HP2", w)]["top_minor_frac"]) for w in ws]
    both = sum(float(idx[(lab, "HP1", w)]["p_ff"]) <= 0.01 and float(idx[(lab, "HP2", w)]["p_ff"]) <= 0.01
               for w in ws)
    close = sum(abs(x - y) <= 0.1 for x, y in zip(m1, m2))
    big1 = sum(x >= 0.25 for x in m1)
    big2 = sum(y >= 0.25 for y in m2)
    print(f"{lab}\tshared={len(ws)}\tboth_sig={both}\tminor HP1 {st.median(m1):.3f} HP2 {st.median(m2):.3f}"
          f"\t|diff|<=0.1: {close}\tminor>=0.25: HP1 {big1} HP2 {big2}")
