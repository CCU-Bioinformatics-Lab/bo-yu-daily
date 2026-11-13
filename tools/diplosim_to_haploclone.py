#!/usr/bin/env python3
"""Turn one diplosim run into haploclone input, keeping the truth in separate files (2026-11-12).

Input: a diplosim output directory (<name>.tsv, <name>_treeedges.tsv, <name>_cloneprops.tsv).
Writes to OUT_DIR:
  data.tsv     PhyClone format for --hp-mode base: mutation_id, sample_id, ref_counts, alt_counts,
               major_cn, minor_cn, normal_cn, tumour_content. No truth.
  data_hp.tsv  data.tsv + the A1 columns: snv_hp, cn_hp1, cn_hp2, ref/alt_hp1, ref/alt_hp2,
               ref/alt_unphased (always 0: diplosim has no unphased reads, DECISIONS 2026-11-06).
               snv_hp is the observed HP, the one carrying alt reads; "NA" when there is no alt read.
  truth.tsv    mutation_id, clone (where the SNV arose = diplosim CLUSTER), allele (A = HP1, B = HP2),
               true_ccf
  truth_tree.tsv  clone, parent, true_ccf (normal excluded; the truncal clone has parent "root")

tumour_content is diplosim's true purity, as PhyClone expects a given purity.
cn_hp1 / cn_hp2 are CN_A / CN_B (A = HP1). In the SNV-only stage they are all 1 / 1.

Usage: python3 tools/diplosim_to_haploclone.py DIPLOSIM_OUT_DIR OUT_DIR [NAME]
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
name = sys.argv[3] if len(sys.argv) > 3 else "diplosim"
out.mkdir(parents=True, exist_ok=True)
tsv = lambda p: list(csv.DictReader(open(p), delimiter="\t"))
rows = tsv(src / f"{name}.tsv")
edges = tsv(src / f"{name}_treeedges.tsv")
props = {r["Clone"]: (float(r["Proportion"]), r["Is_Normal"] == "Yes") for r in tsv(src / f"{name}_cloneprops.tsv")}

base_cols = ["mutation_id", "sample_id", "ref_counts", "alt_counts", "major_cn", "minor_cn", "normal_cn", "tumour_content"]
hp_cols = base_cols + ["snv_hp", "cn_hp1", "cn_hp2", "ref_hp1", "alt_hp1", "ref_hp2", "alt_hp2", "ref_unphased", "alt_unphased"]
base, hp, truth = [], [], []
for r in rows:
    i = lambda c: int(float(r[c]))
    cn_a, cn_b = i("CN_A"), i("CN_B")
    rec = {"mutation_id": f"m{r['VAR_POS']}", "sample_id": "S1", "ref_counts": i("REF_COUNT"), "alt_counts": i("VAR_COUNT"),
           "major_cn": max(cn_a, cn_b), "minor_cn": min(cn_a, cn_b), "normal_cn": 2, "tumour_content": r["PURITY"]}
    assert rec["ref_counts"] == i("HP1_REF") + i("HP2_REF") and rec["alt_counts"] == i("HP1_ALT") + i("HP2_ALT")
    a1, a2 = i("HP1_ALT"), i("HP2_ALT")
    assert a1 == 0 or a2 == 0, "diplosim puts every alt read on the SNV's HP"
    observed = "HP1" if a1 > 0 else "HP2" if a2 > 0 else "NA"
    base.append(rec)
    hp.append({**rec, "snv_hp": observed, "cn_hp1": cn_a, "cn_hp2": cn_b, "ref_hp1": i("HP1_REF"), "alt_hp1": a1,
               "ref_hp2": i("HP2_REF"), "alt_hp2": a2, "ref_unphased": 0, "alt_unphased": 0})
    truth.append({"mutation_id": rec["mutation_id"], "clone": r["CLUSTER"], "allele": r["ALLELE"], "true_ccf": r["TRUE_CCF"]})

for fname, cols, data in (("data.tsv", base_cols, base), ("data_hp.tsv", hp_cols, hp),
                          ("truth.tsv", ["mutation_id", "clone", "allele", "true_ccf"], truth)):
    with open(out / fname, "w", newline="") as f:
        w = csv.DictWriter(f, cols, delimiter="\t")
        w.writeheader()
        w.writerows(data)

root = next(c for c, (_, normal) in props.items() if normal)
purity = 1 - props[root][0]
children = defaultdict(list)
parent = {}
for e in edges:
    children[e["Parent"]].append(e["Child"])
    parent[e["Child"]] = e["Parent"]


def subtree(n):
    return [n] + [m for c in children[n] for m in subtree(c)]


with open(out / "truth_tree.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["clone", "parent", "true_ccf"])
    for c in subtree(root)[1:]:
        w.writerow([c, "root" if parent[c] == root else parent[c], round(sum(props[m][0] for m in subtree(c)) / purity, 4)])
n_na = sum(r["snv_hp"] == "NA" for r in hp)
print(f"{len(base)} SNVs, purity {float(rows[0]['PURITY']):.3f}, {len(props) - 1} clones, snv_hp NA {n_na}")
