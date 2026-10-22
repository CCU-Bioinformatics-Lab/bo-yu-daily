"""Check PhyClone's CONIPHER benchmark files against a rerun of the TRACERx simulation tool.

usage: python tools/conipher_sim_check.py RERUN_DIR [PHYCLONE_DIR] [--out OUT_TSV]

RERUN_DIR: output of tools/conipher_sim_rerun.py (<name>/sim/<name>{.tsv,_treeedges.tsv}).
PHYCLONE_DIR: default /big8_disk/boyu114/phyclone_dataset/CONIPHER_No-Noise/data_archive.

The PhyClone authors' conversion code is not public. Rules read off their files:
  full_truth_with_mut_id.tsv  = simulator <name>.tsv + mutation_id "s<VAR_POS>", rows reordered
  data.tsv                    = same rows; ref/alt = REF_COUNT/VAR_COUNT, tumour_content = PURITY,
                                chrom = CHR, normal_cn = 2,
                                major_cn = round(max(CN_A, CN_B)), minor_cn = round(min(CN_A, CN_B))
  tree.json                   = edges from _treeedges.tsv without the Truncal edge from the normal
                                root; a clone left with no non-noise SNV is removed and its children
                                attach to its nearest ancestor that has SNVs; node snvs = mutations per CLUSTER (noise rows excluded), plus
                                an id -1 outlier node that holds the noise mutations (empty without noise)
The row order is not reproduced (rule unknown), so row-level checks sort both sides first.
First used in lab_report/2026-10-22_pairtree_conipher_sim_rerun/.
"""
import json, sys
from pathlib import Path

import numpy as np
import pandas as pd

PHYCLONE = "/big8_disk/boyu114/phyclone_dataset/CONIPHER_No-Noise/data_archive"
KEY = ["mutation_id", "sample_id"]


def to_phyclone(sim):
    hi, lo = np.maximum(sim.CN_A, sim.CN_B), np.minimum(sim.CN_A, sim.CN_B)
    return pd.DataFrame({
        "mutation_id": "s" + sim.VAR_POS.astype(str), "sample_id": sim.SAMPLE,
        "ref_counts": sim.REF_COUNT, "alt_counts": sim.VAR_COUNT,
        "major_cn": np.round(hi).astype(int), "minor_cn": np.round(lo).astype(int), "normal_cn": 2,
        "tumour_content": sim.PURITY, "chrom": sim.CHR})


def contracted_edges(edges, keep):
    """Tumour edges after removing clones not in keep; children move up to the nearest kept ancestor."""
    tumour = edges[edges.Truncal == "No"]
    parent = dict(zip(tumour.Child, tumour.Parent))
    out = set()
    for c in parent:
        if c not in keep:
            continue
        p = parent[c]
        while p not in keep and p in parent:
            p = parent[p]
        if p in keep:
            out.add((p, c))
    return out


def sort(df):
    return df.sort_values(KEY if "sample_id" in df else ["SAMPLE", "VAR_POS"]).reset_index(drop=True)


def check(rerun, auth, name):
    sim = pd.read_csv(rerun / name / "sim" / f"{name}.tsv", sep="\t")
    gt = auth / name / "ground_truth"
    truth = pd.read_csv(gt / f"{name}_full_truth_with_mut_id.tsv", sep="\t")
    data = pd.read_csv(auth / name / "program_inputs" / "phyclone_outliers" / "data.tsv", sep="\t")
    tree = json.loads((gt / "tree.json").read_text())
    edges = pd.read_csv(rerun / name / "sim" / f"{name}_treeedges.tsv", sep="\t")
    sim_mut = sim.assign(mutation_id="s" + sim.VAR_POS.astype(str))
    muts = sim_mut.drop_duplicates("mutation_id")
    clusters = muts[~muts.NOISE].groupby("CLUSTER").mutation_id.apply(set).to_dict()
    nodes = {n["id"]: set(n["snvs"]) for n in tree["nodes"]}
    return {
        "name": name,
        "treeedges_identical": (gt / f"{name}_treeedges.tsv").read_bytes()
                               == (rerun / name / "sim" / f"{name}_treeedges.tsv").read_bytes(),
        "full_truth_same_rows": sort(truth).equals(sort(sim_mut)),
        "full_truth_same_order": truth.drop(columns="mutation_id").equals(sim),
        "data_tsv_same_rows": sort(data).equals(sort(to_phyclone(sim))),
        "data_tsv_order=full_truth": bool((data.mutation_id.values == truth.mutation_id.values).all()
                                          and (data.sample_id.values == truth.SAMPLE.values).all()),
        "tree_edges=treeedges": {(e["parent"], e["child"]) for e in tree["edges"]}
                                == contracted_edges(edges, set(clusters)),
        "tree_nodes=clusters": {i: v for i, v in nodes.items() if i != -1} == clusters,
        "tree_node_-1=noise": nodes.get(-1) == set(muts[muts.NOISE].mutation_id),
        "n_rows": len(sim), "n_clusters": len(clusters),
    }


def main(argv):
    rerun = Path(argv[0])
    auth = Path(argv[1]) if len(argv) > 1 and not argv[1].startswith("--") else Path(PHYCLONE)
    names = sorted(d.name for d in auth.iterdir() if d.name.startswith("LTXSIM"))
    df = pd.DataFrame([check(rerun, auth, n) for n in names])
    print(f"datasets: {len(df)}")
    for c in df.columns[1:-2]:
        print(f"{c}: {int(df[c].sum())}/{len(df)}")
    if "--out" in argv:
        df.to_csv(argv[argv.index("--out") + 1], sep="\t", index=False)


if __name__ == "__main__":
    main(sys.argv[1:])
