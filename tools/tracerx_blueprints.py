"""Extract TRACERx 421 single-region trees and CN segments as blueprints for longbulksim.

Region trees use the same single-region view as tools/tracerx_event_stats.py: keep clusters
with region CCF > 0, plus their ancestors. Each row is one clone of one region tree, with its
parent, region CCF, the tumour-level SNV count of its cluster and the clone count of the whole
tumour tree.

CN comes from scna_region.tsv (per-region allele-specific CN; A/B are phased across regions,
so A/B map to one HP each). Per tumour and segment:
  trunk (A, B)   copies on each allele in the trunk
  delta (dA, dB) the change in the other regions' state, or (0, 0)
An allele differs between regions only if its raw CN range is >= 0.8 (the strict rule of
tools/tracerx_event_stats.py); otherwise it takes round(median raw). With two region states,
the one labelled "neutral" versus ploidy is the trunk if the other is not; otherwise the more
common state is (rule column: ploidy / majority). Adjacent segments with the same trunk and
delta are merged.

Usage:
  python3 tools/tracerx_blueprints.py DERIVED_TSV_DIR OUT_DIR
"""
import os
import sys
from collections import Counter, defaultdict

import pandas as pd

STRICT_RANGE = 0.8


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


def segment_states(g):
    """(trunk, delta, rule) for one tumour segment; g has one row per region."""
    cols = []
    for raw in (g.nAraw, g.nBraw):
        if raw.max() - raw.min() >= STRICT_RANGE:
            cols.append(raw.round().clip(lower=0).astype(int).tolist())
        else:
            cols.append([int(round(max(raw.median(), 0)))] * len(g))
    states = Counter(zip(*cols))
    if len(states) == 1:
        return next(iter(states)), (0, 0), "single"
    (s1, _), (s2, _) = states.most_common(2)
    label = {st: set(g.cpn_event_vs_ploidy[[st == x for x in zip(*cols)]]) for st in (s1, s2)}
    neutral = [st for st in (s1, s2) if label[st] == {"neutral"}]
    trunk, rule = (neutral[0], "ploidy") if len(neutral) == 1 else (s1, "majority")
    other = s2 if trunk == s1 else s1
    return trunk, (other[0] - trunk[0], other[1] - trunk[1]), rule


def cn_segments(d):
    sc = pd.read_csv(os.path.join(d, "scna_region.tsv"), sep="\t",
                     usecols=["tumour_id", "sample", "chr", "startpos", "endpos", "nAraw",
                              "nBraw", "cpn_event_vs_ploidy"])
    out = []
    for (t, ch, st, en), g in sc.groupby(["tumour_id", "chr", "startpos", "endpos"], sort=False):
        (a, b), (da, db), rule = segment_states(g)
        row = [t, str(ch), int(st), int(en), a, b, da, db, rule]
        prev = out[-1] if out else None
        if prev and prev[0] == t and prev[1] == row[1] and prev[4:8] == row[4:8]:
            prev[3] = row[3]
        else:
            out.append(row)
    df = pd.DataFrame(out, columns=["tumour_id", "chr", "start", "end", "trunk_a", "trunk_b",
                                    "d_a", "d_b", "rule"])
    df.insert(4, "bp", df.end - df.start)
    return df.sort_values(["tumour_id", "chr", "start"], key=lambda c: (
        c.astype(int) if c.name in ("chr", "start") else c))


def main(derived, out):
    os.makedirs(out, exist_ok=True)
    trees = region_trees(derived)
    trees.to_csv(os.path.join(out, "tracerx421_region_trees.tsv"), sep="\t", index=False)
    cn = cn_segments(derived)
    cn.to_csv(os.path.join(out, "tracerx421_cn_segments.tsv"), sep="\t", index=False)
    sub = (cn.d_a != 0) | (cn.d_b != 0)
    print(f"{trees.groupby(['tumour_id', 'region']).ngroups} region trees, "
          f"{trees.tumour_id.nunique()} tumours; {len(cn)} CN segments, "
          f"{int(sub.sum())} with a subclonal change; trunk rule:\n"
          f"{cn[sub].rule.value_counts().to_string()}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
