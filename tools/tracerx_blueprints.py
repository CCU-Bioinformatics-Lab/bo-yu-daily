"""Extract TRACERx 421 single-region trees and CN events as blueprints for longbulksim.

Region trees use the same single-region view as tools/tracerx_event_stats.py: keep clusters
with region CCF > 0, plus their ancestors. Each row is one clone of one region tree, with its
parent, region CCF, the tumour-level SNV count of its cluster and the clone count of the whole
tumour tree.

CN events come from lab_report/2026-10-25_tracerx_event_stats/tables/cn_events.tsv (multi-region
calls, >= 1 Mb). longbulksim kinds:
  clonal_cnloh      clonal_cnLOH
  subclonal_cnloh   subclonal_cnLOH
  subclonal_loss    subclonal_LOH not overlapping a subclonal_cnLOH (deletion type)
  subclonal_gain    subcl_hap_gain_strict (one HP changes; 91-95% are +1)

Usage:
  python3 tools/tracerx_blueprints.py DERIVED_TSV_DIR CN_EVENTS.tsv OUT_DIR
"""
import os
import sys
from collections import defaultdict

import pandas as pd

KINDS = {"clonal_cnLOH": "clonal_cnloh", "subclonal_cnLOH": "subclonal_cnloh",
         "subcl_hap_gain_strict": "subclonal_gain"}


def region_trees(d):
    edges = pd.read_csv(os.path.join(d, "tree_edges.tsv"), sep="\t", dtype=str)
    cc = pd.read_csv(os.path.join(d, "cluster_ccf_region.tsv"), sep="\t", dtype={"cluster": str})
    sc = pd.read_csv(os.path.join(d, "scna_region.tsv"), sep="\t", usecols=["sample", "ACF"])
    acf = sc.drop_duplicates("sample")
    region = acf["sample"].str.replace(r"-(R|r)", lambda m: "." + m.group(1), regex=True)
    purity = dict(zip(region, acf.ACF))
    mut = pd.read_csv(os.path.join(d, "mutation_region_tree.tsv"), sep="\t",
                      usecols=["tumour_id", "mutation_id", "cluster"], dtype=str)
    n_mut = mut.drop_duplicates(["tumour_id", "mutation_id"]).groupby(
        ["tumour_id", "cluster"]).size().to_dict()
    parent = defaultdict(dict)
    nodes = defaultdict(set)
    for t, p, c in zip(edges.tumour_id, edges.parent, edges.child):
        nodes[t] |= {p, c}
        if p != c:
            parent[t][c] = p
    rows = []
    for (t, reg), g in cc.groupby(["tumour_id", "region"]):
        if t not in nodes or reg not in purity:
            continue
        roots = [n for n in nodes[t] if n not in parent[t]]
        if len(roots) != 1:
            continue
        ccf = dict(zip(g.cluster, g.ccf_pct / 100.0))
        keep = set()
        for n in nodes[t]:
            if ccf.get(n, 0) > 0:
                while n is not None and n not in keep:
                    keep.add(n)
                    n = parent[t].get(n)
        keep.add(roots[0])
        for n in sorted(keep):
            rows.append([t, reg, purity[reg], len(nodes[t]), n, parent[t].get(n, "root"),
                         ccf.get(n, 0.0), n_mut.get((t, n), 0)])
    return pd.DataFrame(rows, columns=["tumour_id", "region", "purity", "tumour_n_clones",
                                       "clone", "parent", "ccf", "n_mut"])


def overlaps(a, b):
    return a.start < b.end and b.start < a.end


def cn_events(path):
    ev = pd.read_csv(path, sep="\t", dtype={"chr": str})
    out = []
    for t, g in ev.groupby("tumour_id"):
        cnloh = g[g.type == "subclonal_cnLOH"]
        for e in g.itertuples():
            if e.type in KINDS:
                out.append([t, KINDS[e.type], e.chr, e.start, e.end, e.bp])
            elif e.type == "subclonal_LOH" and not any(
                    overlaps(e, c) for c in cnloh.itertuples() if c.chr == e.chr):
                out.append([t, "subclonal_loss", e.chr, e.start, e.end, e.bp])
    return pd.DataFrame(out, columns=["tumour_id", "kind", "chr", "start", "end", "bp"])


def main(derived, cn_path, out):
    os.makedirs(out, exist_ok=True)
    trees = region_trees(derived)
    trees.to_csv(os.path.join(out, "tracerx421_region_trees.tsv"), sep="\t", index=False)
    ev = cn_events(cn_path)
    ev.to_csv(os.path.join(out, "tracerx421_cn_events.tsv"), sep="\t", index=False)
    print(f"{trees.groupby(['tumour_id', 'region']).ngroups} region trees, "
          f"{trees.tumour_id.nunique()} tumours; {len(ev)} CN events:\n"
          f"{ev.kind.value_counts().to_string()}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
