"""Score PhyClone outputs on the PhyClone paper benchmark datasets with the paper's point metrics.

The paper (Gillis et al. 2025, btaf344) did not publish its evaluation code. The two point metrics
below reproduce every PhyClone / PhyClone-N row of Experiment_Performance_Metrics.xlsx from the
released files (see lab_report/2026-10-27_v4_evaluator/README.md for the evidence):

  v_measure   sklearn-style V-measure (natural log, beta = 1) over the SNVs that are both in the
              predicted tree and in the truth tree. Truth label = truth node id; the truth "-1"
              node (lost / outlier SNVs) is one ordinary label. Predicted outliers (clone_id -1)
              are not in the predicted tree, so they are left out of V.
  ad_f_score  F1 between two sets of ordered SNV pairs (a, d), a's node a strict ancestor of d's
              node. Truth pairs come from the truth tree, predicted pairs from the predicted tree,
              both restricted to truth SNVs. Same-node pairs are not pairs. SNVs in the truth
              "-1" node, predicted outliers, and SNVs absent from one tree take part in no pair.
              Several roots (a forest under PhyClone's "root") give no pair across roots.
  num_mutations_pred = |predicted tree SNVs & truth SNVs|, num_mutations_true = |truth SNVs|.

A predicted tree is read from tree.json (networkx node-link, as in the dataset), or from a clone
table plus Newick: PhyClone 0.7.0 results.tsv + tree.nwk, PhyClone 0.8.0 / haploclone
map_table.tsv + map_tree.nwk. The Newick pseudo-node "root" is not a clone.

Usage:
  eval_phyclone_dataset.py score TRIAL_DIR OUT_DIR [--source json|table]
      TRIAL_DIR has ground_truth/tree.json; OUT_DIR has one of the predicted-tree file sets.
  eval_phyclone_dataset.py validate DATASET_ROOT XLSX OUT.tsv
      Re-scores the paper's own program_outputs/phyclone_{outliers,naive} for every PhyClone /
      PhyClone-N row of the xlsx, from tree.json and from results.tsv + tree.nwk, and writes
      one row per xlsx row with both scores, the xlsx values, trial sizes and runtime.
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_hp_truth_phyclone import newick_parents  # noqa: E402

OUTLIER = "-1"


@dataclass(frozen=True)
class CloneTree:
    node_of: dict      # SNV id -> node id (str); outliers already dropped from predictions
    ancestors: dict    # node id -> frozenset of strict ancestor node ids


def _ancestors(nodes, parent):
    out = {}
    for n in nodes:
        seen, x = set(), n
        while x in parent:
            x = parent[x]
            seen.add(x)
        out[n] = frozenset(seen)
    return out


def tree_from_json(path):
    with open(path) as fh:
        d = json.load(fh)
    node_of = {s: str(n["id"]) for n in d["nodes"] for s in n["snvs"]}
    parent = {str(e["child"]): str(e["parent"]) for e in d["edges"]}
    return CloneTree(node_of, _ancestors({str(n["id"]) for n in d["nodes"]}, parent))


def tree_from_table(table_path, newick_path):
    with open(table_path) as fh:
        node_of = {r["mutation_id"]: r["clone_id"] for r in csv.DictReader(fh, delimiter="\t")
                   if r["clone_id"] != OUTLIER}
    with open(newick_path) as fh:
        parent = {c: p for c, p in newick_parents(fh.read()).items() if p != "root"}
    nodes = set(parent) | set(parent.values()) | set(node_of.values())
    return CloneTree(node_of, _ancestors(nodes, parent))


def read_prediction(out_dir, source=None):
    p = lambda f: os.path.join(out_dir, f)
    if source in (None, "json") and os.path.exists(p("tree.json")):
        return tree_from_json(p("tree.json"))
    for table, nwk in (("map_table.tsv", "map_tree.nwk"), ("results.tsv", "tree.nwk")):
        if source in (None, "table") and os.path.exists(p(table)) and os.path.exists(p(nwk)):
            return tree_from_table(p(table), p(nwk))
    raise FileNotFoundError(f"no predicted tree ({source or 'any'}) in {out_dir}")


def v_measure(truth, pred):
    n = len(truth)
    if n == 0:
        return float("nan")
    ent = lambda xs: -sum(v / n * math.log(v / n) for v in Counter(xs).values())

    def cond(x, y):
        cy = Counter(y)
        return -sum(v / n * math.log(v / cy[k[1]]) for k, v in Counter(zip(x, y)).items())

    hc, hk = ent(truth), ent(pred)
    h = 1.0 if hc == 0 else 1 - cond(truth, pred) / hc
    c = 1.0 if hk == 0 else 1 - cond(pred, truth) / hk
    return 0.0 if h + c == 0 else 2 * h * c / (h + c)


def _ancestor_matrix(tree, index):
    a = np.zeros((len(index),) * 2)
    for node, i in index.items():
        for anc in tree.ancestors.get(node, ()):
            if anc in index:
                a[index[anc], i] = 1
    return a


def ad_counts(truth, pred):
    """(true pairs, predicted pairs, shared pairs), computed on node-level counts."""
    snvs = list(truth.node_of)
    t_nodes = {n: i for i, n in enumerate(sorted(set(truth.node_of.values())))}
    p_nodes = {n: i for i, n in enumerate(sorted(set(pred.node_of.values())))}
    none = len(p_nodes)
    joint = np.zeros((len(t_nodes), none + 1))
    for s in snvs:
        joint[t_nodes[truth.node_of[s]], p_nodes.get(pred.node_of.get(s), none)] += 1
    at = _ancestor_matrix(truth, t_nodes)
    ap = np.zeros((none + 1,) * 2)
    ap[:none, :none] = _ancestor_matrix(pred, p_nodes)
    nt, npred = joint.sum(1), joint.sum(0)
    return float(nt @ at @ nt), float(npred @ ap @ npred), float((joint * (at @ joint @ ap.T)).sum())


def score(truth, pred):
    shared = [s for s in pred.node_of if s in truth.node_of]
    n_true, n_pred, n_tp = ad_counts(truth, pred)
    prec = n_tp / n_pred if n_pred else 0.0
    rec = n_tp / n_true if n_true else 0.0
    return {
        "v_measure": v_measure([truth.node_of[s] for s in shared], [pred.node_of[s] for s in shared]),
        "ancestor_descendant_f_score": 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec),
        "ad_precision": prec,
        "ad_recall": rec,
        "num_mutations_pred": len(shared),
        "num_mutations_true": len(truth.node_of),
    }


# ---------------------------------------------------------------- xlsx (stdlib reader)

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
       "pr": "http://schemas.openxmlformats.org/package/2006/relationships"}


def read_xlsx(path):
    """{sheet name: list of row dicts keyed by the header row}."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
        rels = {r.get("Id"): r.get("Target") for r in
                ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall("pr:Relationship", _NS)}
        sheets = {}
        for sh in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", _NS):
            target = rels[sh.get(f"{{{_NS['r']}}}id")].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            rows = []
            for row in ET.fromstring(z.read(target)).iter(f"{{{_NS['m']}}}row"):
                cells = {}
                for c in row.findall("m:c", _NS):
                    col = "".join(ch for ch in c.get("r") if ch.isalpha())
                    kind, v = c.get("t"), c.find("m:v", _NS)
                    if kind == "inlineStr":
                        val = "".join(t.text or "" for t in c.iter(f"{{{_NS['m']}}}t"))
                    elif v is None:
                        val = None
                    elif kind == "s":
                        val = shared[int(v.text)]
                    elif kind in ("str", "b"):
                        val = v.text
                    else:
                        val = float(v.text)
                    cells[col] = val
                rows.append(cells)
            header = rows[0]
            sheets[sh.get("name")] = [{header[k]: r.get(k) for k in header} for r in rows[1:]]
    return sheets


# ---------------------------------------------------------------- xlsx row -> trial directory

_HGSOC = {"S8": "p2_wgs", "S9": "p2_wgs_t", "S10": "p3_wgs", "S11": "p3_wgs_t",
          "S12": "p9_wgs", "S13": "p9_wgs_t"}
_OUTPUT = {"PhyClone": "phyclone_outliers", "PhyClone-N": "phyclone_naive"}
_i = lambda x: int(float(x))


def trial_paths(sheet_rows):
    """Yield (sheet, xlsx row, dataset, trial relative path) for PhyClone rows of the sheets."""
    for sheet, rows in sheet_rows.items():
        key = sheet.split()[0]
        cn_seen = Counter()
        for r in rows:
            if r["program"] not in _OUTPUT:
                continue
            if key in ("S2", "S3"):
                ds = "TSSB_Low" if key == "S2" else "TSSB_High"
                rel = f"S{_i(r['num_samples'])}_D{_i(r['depth'])}_M{_i(r['num_mutations'])}_run{_i(r['run'])}"
            elif key == "S4":
                ds, rel = "FS-CRP_Loss", f"loss_prop_{float(r['mut_loss_prop']):.1f}_run{_i(r['run'])}"
            elif key == "S5":
                ds = "Pairtree"
                rel = (f"sim_K{_i(r['num_clusters'])}_S{_i(r['num_samples'])}_T{_i(r['depth'])}"
                       f"_M{_i(r['num_mutations'])}_run{_i(r['run'])}")
            elif key in ("S6", "S7"):
                ds, rel = ("CONIPHER_No-Noise" if key == "S6" else "CONIPHER_Noise"), r["sim_name"]
            elif key == "S14":
                # The sheet has no error column; the k-th row of a sim is error level 0.1 * k.
                k = cn_seen[r["sim_name"]]
                cn_seen[r["sim_name"]] += 1
                ds, rel = "Copy_Number_Error", f"{r['sim_name']}_error_{0.1 * k:.1f}"
            elif key in _HGSOC:
                ds, rel = f"HGSOC/{_HGSOC[key]}", r["run"]
            else:
                continue
            yield sheet, r, ds, os.path.join(ds, "data_archive", rel)


def trial_size(trial_dir):
    inp = os.path.join(trial_dir, "program_inputs", "phyclone_outliers")
    with open(os.path.join(inp, "data.tsv")) as fh:
        rows = [(r["mutation_id"], r["sample_id"]) for r in csv.DictReader(fh, delimiter="\t")]
    clusters = set()
    for f in ("results.tsv.gz", "clusters.tsv.gz", "results.tsv"):
        p = os.path.join(inp, f)
        if os.path.exists(p):
            with (gzip.open(p, "rt") if f.endswith(".gz") else open(p)) as fh:
                clusters = {r["cluster_id"] for r in csv.DictReader(fh, delimiter="\t")}
            break
    return {"n_snvs": len({m for m, _ in rows}), "n_samples": len({s for _, s in rows}),
            "n_clusters": len(clusters)}


METRICS = ("v_measure", "ancestor_descendant_f_score", "num_mutations_pred", "num_mutations_true")


def validate(root, xlsx, out_path):
    fields = (["sheet", "program", "trial", "n_snvs", "n_samples", "n_clusters", "time", "memory"]
              + [f"xlsx_{m}" for m in METRICS] + [f"json_{m}" for m in METRICS]
              + [f"table_{m}" for m in METRICS] + ["json_match", "table_match"])
    summary = {}
    with open(out_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for sheet, r, _, rel in trial_paths(read_xlsx(xlsx)):
            tdir = os.path.join(root, rel)
            odir = os.path.join(tdir, "program_outputs", _OUTPUT[r["program"]])
            truth = tree_from_json(os.path.join(tdir, "ground_truth", "tree.json"))
            row = {"sheet": sheet, "program": r["program"], "trial": rel,
                   "time": r["time"], "memory": r["memory"], **trial_size(tdir)}
            for m in METRICS:
                row[f"xlsx_{m}"] = r[m]
            for src in ("json", "table"):
                s = score(truth, read_prediction(odir, src))
                for m in METRICS:
                    row[f"{src}_{m}"] = s[m]
                row[f"{src}_match"] = int(all(abs(s[m] - float(r[m])) <= 1e-9 for m in METRICS))
            w.writerow(row)
            agg = summary.setdefault((sheet, r["program"]), [0, 0, 0, 0.0, 0.0])
            agg[0] += 1
            agg[1] += row["json_match"]
            agg[2] += row["table_match"]
            agg[3] = max(agg[3], abs(row["json_v_measure"] - float(r["v_measure"])))
            agg[4] = max(agg[4], abs(row["json_ancestor_descendant_f_score"]
                                     - float(r["ancestor_descendant_f_score"])))
    print("sheet\tprogram\trows\tjson_match\ttable_match\tmax_abs_dV\tmax_abs_dAD")
    for (sheet, prog), (n, mj, mt, dv, dad) in summary.items():
        print(f"{sheet}\t{prog}\t{n}\t{mj}\t{mt}\t{dv:.3g}\t{dad:.3g}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("trial_dir")
    s.add_argument("out_dir")
    s.add_argument("--source", choices=("json", "table"))
    v = sub.add_parser("validate")
    v.add_argument("dataset_root")
    v.add_argument("xlsx")
    v.add_argument("out_tsv")
    a = ap.parse_args()
    if a.cmd == "score":
        truth = tree_from_json(os.path.join(a.trial_dir, "ground_truth", "tree.json"))
        for k, val in score(truth, read_prediction(a.out_dir, a.source)).items():
            print(f"{k}\t{val}")
    else:
        validate(a.dataset_root, a.xlsx, a.out_tsv)


if __name__ == "__main__":
    main()
