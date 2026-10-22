"""Check simulated FS-CRP datasets: rule checks per run, then distributions vs the authors' data.

usage: python3 tools/phyclone_sim_check.py RERUN_DIR [AUTHOR_DIR] [--out OUT_TSV]

RERUN_DIR: output of tools/phyclone_sim_rerun.py (run*/ground_truth/{data.tsv,tree.json}).
AUTHOR_DIR: default /big8_disk/boyu114/phyclone_dataset/FS-CRP_Loss/data_archive;
            uses loss_prop_0.0_run*/ground_truth (the runs without mutation loss).

Rule checks (each run, both sources), from the code in
phyclone/tests/utilities/{fscrp.py,sim_data_on_tree.py}:
  depth      ref + alt equals one fixed depth
  mu         mu recomputed from g_n, g_r, g_v, ccf, purity equals the stored mu
  genotype   g_r is AA or all-A; g_v follows the before/after-CN-event rule
  ccf        ccf column equals the cluster's cellular_prev
  tree       one root; cellular = clonal + sum(children); root cellular = 1
  size       parent SNV count >= child SNV count
Nodes without SNVs (the authors' trees have an isolated id -1 node) are skipped and counted.
Prints one table: rule pass counts, then summary statistics side by side.
"""
import glob, json, sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

AUTHOR = "/big8_disk/boyu114/phyclone_dataset/FS-CRP_Loss/data_archive"


def expected_mu(r):
    def mu(g):
        a, b = g.count("A"), g.count("B")
        return 1 - r.error_rate if a == 0 else r.error_rate if b == 0 else b / (a + b)
    t, f = r.tumour_content, r.ccf
    p = np.array([(1 - t) * len(r.g_n), t * (1 - f) * len(r.g_r), t * f * len(r.g_v)])
    return float(p @ [mu(r.g_n), mu(r.g_r), mu(r.g_v)] / p.sum())


def genotype_ok(r):
    tot = r.major_cn + r.minor_cn
    if r.g_r not in (r.g_n, "A" * tot):
        return False
    if r.g_r == r.g_n:  # mutation before the CN event
        ok = {"A" * r.minor_cn + "B" * r.major_cn}
        if r.minor_cn > 0:
            ok.add("A" * r.major_cn + "B" * r.minor_cn)
        return r.g_v in ok
    return r.g_v == "A" * (tot - 1) + "B"


def check_run(d):
    df = pd.read_csv(d / "data.tsv", sep="\t")
    tr = json.loads((d / "tree.json").read_text())
    empty = [n["id"] for n in tr["nodes"] if not n["snvs"]]  # authors' trees carry an empty id -1 node
    nodes = {n["id"]: n for n in tr["nodes"] if n["snvs"]}
    kids = {i: [] for i in nodes}
    for e in tr["edges"]:
        kids[e["parent"]].append(e["child"])
    roots = set(nodes) - {e["child"] for e in tr["edges"]}
    cell = {i: np.array(n["cellular_prev"]) for i, n in nodes.items()}
    clon = {i: np.array(n["clonal_prev"]) for i, n in nodes.items()}
    size = {i: len(n["snvs"]) for i, n in nodes.items()}
    sidx = df.sample_id.str[1:].astype(int)
    root = next(iter(roots)) if len(roots) == 1 else None
    res = {
        "depth": (df.ref_counts + df.alt_counts).nunique() == 1,
        "mu": np.allclose(df.apply(expected_mu, axis=1), df.mu, rtol=0, atol=1e-12),
        "genotype": bool(df.apply(genotype_ok, axis=1).all()),
        "ccf": np.allclose([cell[c][s] for c, s in zip(df.cluster, sidx)], df.ccf, atol=1e-12),
        "tree": root is not None and np.allclose(cell[root], 1)
                and all(np.allclose(cell[i], clon[i] + sum((cell[k] for k in kids[i]), 0 * clon[i]))
                        for i in nodes),
        "size": all(size[p] >= size[k] for p in kids for k in kids[p]),
    }
    one = df[df.sample_id == "s0"]
    combos = one.groupby("cluster").apply(lambda g: len(set(zip(g.major_cn, g.minor_cn))), include_groups=False)
    stats = {
        "empty_nodes": len(empty),
        "clusters": len(nodes),
        "root_is_largest": root is not None and size[root] == max(size.values()),
        "root_children": len(kids[root]) if root is not None else np.nan,
        "edges_equal_size": sum(size[p] == size[k] for p in kids for k in kids[p]),
        "frac_before_cn": (df.g_r == df.g_n).mean(),
        "frac_minor1": (df.minor_cn == 1).mean(),
        "mean_total_cn": (df.major_cn + df.minor_cn).mean(),
        "vaf_median": (df.alt_counts / (df.ref_counts + df.alt_counts)).median(),
        "cn_combos_per_cluster_s0": combos[combos.index.map(size) >= 10].mean(),
    }
    return res, stats


def summarize(label, dirs):
    rules, stats = Counter(), []
    for d in dirs:
        r, s = check_run(d)
        rules.update(k for k, v in r.items() if v)
        stats.append(s)
    return label, len(dirs), rules, pd.DataFrame(stats)


def main(argv):
    rerun = Path(argv[0])
    author = Path(argv[1]) if len(argv) > 1 and not argv[1].startswith("--") else Path(AUTHOR)
    sets = [
        summarize("rerun", sorted(p.parent for p in rerun.glob("run*/ground_truth/data.tsv"))),
        summarize("author", sorted(Path(p) for p in glob.glob(str(author / "loss_prop_0.0_run*/ground_truth")))),
    ]
    print("## rule checks (runs passing / runs)")
    for label, n, rules, _ in sets:
        print(label, " ".join(f"{k}={rules[k]}/{n}" for k in ["depth", "mu", "genotype", "ccf", "tree", "size"]))
    print("\n## statistics (mean [5%, 95%] over runs)")
    table = {}
    for label, n, _, df in sets:
        table[label] = {c: f"{df[c].astype(float).mean():.3f} [{df[c].astype(float).quantile(.05):.2f}, "
                           f"{df[c].astype(float).quantile(.95):.2f}]" for c in df.columns}
    out = pd.DataFrame(table)
    print(out.to_string())
    if "--out" in argv:
        out.to_csv(argv[argv.index("--out") + 1], sep="\t")


if __name__ == "__main__":
    main(sys.argv[1:])
