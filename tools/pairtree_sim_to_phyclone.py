"""Convert pearsim truth pickles to the PhyClone benchmark layout (Pairtree dataset).

usage: python tools/pairtree_sim_to_phyclone.py PICKLE_DIR OUT_DIR [--seed N]
       python tools/pairtree_sim_to_phyclone.py --check-author [AUTHOR_DIR]

PICKLE_DIR holds sim_K*_S*_T*_M*_G0_run*.truth.pickle (output of
pairtree/simulator/make_simulated_data.sh). For each pickle this writes
OUT_DIR/<name without _G0>/:
  ground_truth/<pickle file>                     copy of the pickle
  ground_truth/tree.json                         nodes 0..K: snvs, clonal_prev = eta, cellular_prev = phi
  program_inputs/phyclone_outliers/data.tsv      PhyClone input, 9 columns

Rules were read off the authors' files in /big8_disk/boyu114/phyclone_dataset/Pairtree:
every column is a function of the pickle except chrom, which is one random value in
1..22 per mutation. chrom here comes from --seed, so it never matches the authors'.

--check-author rebuilds tree.json and data.tsv from each author pickle and compares
them with the author files (tree.json byte for byte; data.tsv on every column but chrom).
First used in lab_report/2026-10-22_pairtree_conipher_sim_rerun/.
"""
import glob, json, pickle, re, shutil, sys
from pathlib import Path

import numpy as np
import pandas as pd

AUTHOR = "/big8_disk/boyu114/phyclone_dataset/Pairtree/data_archive"


def tree_json(p):
    nodes = []
    for i in range(len(p["eta"])):
        snvs = ["S_" + s[1:] for s in p["clusters"][i - 1]] if i > 0 else []
        prev = {"cellular_prev": p["phi"][i].tolist(), "clonal_prev": p["eta"][i].tolist()}
        # authors' key order: root has clonal_prev first, other nodes cellular_prev first
        order = ["clonal_prev", "cellular_prev"] if i == 0 else ["cellular_prev", "clonal_prev"]
        nodes.append({"snvs": snvs, **{k: prev[k] for k in order}, "id": i})
    edges = [{"parent": int(par), "child": c + 1} for c, par in enumerate(p["structure"])]
    edges.sort(key=lambda e: (e["parent"], e["child"]))
    return {"directed": True, "multigraph": False,
            "graph": {"samples": p["sampnames"], "Method_Name": "Ground-Truth"},
            "nodes": nodes, "edges": edges}


def data_tsv(p, chrom):
    rows = []
    for v in p["variants"].values():
        for s, name in enumerate(p["sampnames"]):
            rows.append({"mutation_id": v["name"], "sample_id": name,
                         "ref_counts": int(v["ref_reads"][s]), "alt_counts": int(v["var_reads"][s]),
                         "major_cn": 1, "minor_cn": 1, "normal_cn": 2, "tumour_content": 1.0,
                         "chrom": chrom[v["name"]]})
    return pd.DataFrame(rows)


def check_author(author):
    n, tree_ok, data_ok = 0, 0, 0
    for d in sorted(Path(author).glob("sim_*")):
        p = pickle.load(open(next((d / "ground_truth").glob("*.pickle")), "rb"))
        ref_tree = (d / "ground_truth" / "tree.json").read_text()
        tree_ok += json.dumps(tree_json(p), indent=4) == ref_tree
        ref = pd.read_csv(d / "program_inputs" / "phyclone_outliers" / "data.tsv", sep="\t")
        chrom = dict(zip(ref.mutation_id, ref.chrom))
        mine = data_tsv(p, chrom)
        data_ok += mine.equals(ref)
        n += 1
    print(f"tree.json identical: {tree_ok}/{n}")
    print(f"data.tsv identical (chrom taken from author file): {data_ok}/{n}")


def main(argv):
    if argv and argv[0] == "--check-author":
        return check_author(argv[1] if len(argv) > 1 else AUTHOR)
    src, out = Path(argv[0]), Path(argv[1])
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 20261022
    out.mkdir(parents=True, exist_ok=False)
    for i, pk in enumerate(sorted(src.glob("*.truth.pickle"))):
        name = re.sub(r"_G0_", "_", pk.name.replace(".truth.pickle", ""))
        p = pickle.load(open(pk, "rb"))
        rng = np.random.default_rng([seed, i])
        chrom = {v["name"]: int(c) for v, c in zip(p["variants"].values(),
                                                   rng.integers(1, 23, len(p["variants"])))}
        gt = out / name / "ground_truth"
        inp = out / name / "program_inputs" / "phyclone_outliers"
        gt.mkdir(parents=True)
        inp.mkdir(parents=True)
        shutil.copy(pk, gt / pk.name)
        (gt / "tree.json").write_text(json.dumps(tree_json(p), indent=4))
        data_tsv(p, chrom).to_csv(inp / "data.tsv", sep="\t", index=False)
    print(f"wrote {i + 1} datasets to {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
