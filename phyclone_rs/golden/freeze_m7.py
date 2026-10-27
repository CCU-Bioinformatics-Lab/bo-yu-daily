"""M7 fixtures: the outlier model, the loss prior options, --precision and --grid-size >= 1000.

Called by freeze.py after its own fixtures, through the same write() (so `freeze.py --check`
covers these files too and SHA256SUMS lists them). freeze.py's own fixtures do not pass through
this module, so they cannot change because of it.

  outlier/terms.json                         compute_outlier_prob for p x cluster size, and the
                                             outlier marginal of a constant likelihood (the
                                             published integral is 0 there)
  datapoints/<case>__<loader>.json           value grid plus outlier_prob, outlier_prob_not,
                                             outlier_marginal_prob per data point; for cluster
                                             loaders the raw per-cluster outlier probability;
                                             for --assign-loss-prob the whole Monte Carlo test
  trees/<case>__m7.json, trees/<new case>.json
                                             trees with data points on the outlier node, from
                                             the M7 reference traces and seeded random trees;
                                             FSCRP prior parts, num_outliers, C4 pair terms
  scores/<case>__<loader>.json               per tree: data_log_likelihood, the outlier prior
                                             and outlier marginal terms alone, the data terms
                                             alone, and log_p / log_p_one of
                                             TreeJointDistribution(outlier_modelling_active =
                                             outlier_prob > 0) at each alpha; MAP clone tables
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

import freeze as F

ALPHAS = F.ALPHAS
CASES_DIR = os.path.join(F.G, "cases")
FSCRP = "fscrp_loss_0.2_run0"

# loader id -> how to load. kind: base (PhyClone load_data on a SNV file), hp (tools/ loader),
# clusters (load_data with a cluster file). seed: rng seed handed to load_data; it only matters
# for --assign-loss-prob, and 1 is the seed of the reference runs.
LOADERS = {
    "base_binomial_out0.01": dict(kind="base", file="data.tsv", density="binomial", outlier_prob=0.01),
    "base_binomial_grid1000": dict(kind="base", file="data.tsv", density="binomial", outlier_prob=0,
                                   grid_size=1000),
    "a2_binomial_out0.01": dict(kind="hp", mode="a2", file="data_hp.tsv", density="binomial",
                                outlier_prob=0.01),
    "clusters_out0.01": dict(kind="clusters", file="data.tsv", clusters="results.tsv.gz",
                             outlier_prob=0.01),
    "clusters_assign_loss": dict(kind="clusters", file="data.tsv", clusters="results.tsv.gz",
                                 outlier_prob=1e-4, assign_loss_prob=True, high_loss_prob=0.4),
    "clusters_user_loss": dict(kind="clusters", file="data.tsv", clusters="results_user_loss.tsv",
                               outlier_prob=1e-4, user_provided_loss_prob=True),
    "clusters_user_loss_nocol": dict(kind="clusters", file="data.tsv", clusters="results.tsv.gz",
                                     outlier_prob=1e-4, user_provided_loss_prob=True),
    "upstream_clusters_grid1000": dict(kind="clusters", file="mixing_small.tsv",
                                       clusters="mixing_small_clusters.tsv", outlier_prob=0,
                                       grid_size=1000),
    "upstream_clusters_prec100": dict(kind="clusters", file="mixing_small.tsv",
                                      clusters="mixing_small_clusters.tsv", outlier_prob=0,
                                      precision=100),
}
# case -> loaders, reference traces the trees come from, pair models for the pair term,
# whether score files are written (prec100 only changes the data points)
CASES = {
    "stress_e0_s1": dict(trees="stress_e0_s1__m7", loaders=["base_binomial_out0.01", "base_binomial_grid1000"],
                         traces=["e0_out001", "e0_out001_boot", "e0_out001_fully"], pairs=True),
    "stress_real_s1": dict(trees="stress_real_s1__m7", loaders=["a2_binomial_out0.01"],
                           traces=["real_a2_err004_out001"], pairs=True),
    FSCRP: dict(trees=FSCRP, loaders=["clusters_out0.01", "clusters_assign_loss",
                                      "clusters_user_loss", "clusters_user_loss_nocol"],
                traces=["fscrp_out", "fscrp_assign_loss", "fscrp_user_loss"], pairs=False),
    "upstream_mixing_small": dict(trees="upstream_mixing_small__m7",
                                  loaders=["upstream_clusters_grid1000", "upstream_clusters_prec100"],
                                  traces=["upstream_grid1000"], pairs=False,
                                  no_scores=["upstream_clusters_prec100"]),
}
RANDOM_TREES = 15
TERM_PROBS = (0.0, 1e-300, 1e-4, 0.01, 0.4, 0.999, 1.0)
TERM_SIZES = (1, 2, 58)


def load(case, loader):
    """(data, samples, clusters, spec) for one loader, as PhyClone's run() would load it."""
    from phyclone.data.pyclone import load_data

    s = {"grid_size": F.GRID, "precision": F.PRECISION, "density": "beta-binomial",
         "assign_loss_prob": False, "user_provided_loss_prob": False, "high_loss_prob": 0.4,
         "seed": 1, **LOADERS[loader]}
    inp = os.path.join(CASES_DIR, case, "input")
    rng = np.random.default_rng(s["seed"])
    common = dict(density=s["density"], grid_size=s["grid_size"], outlier_prob=s["outlier_prob"],
                  precision=s["precision"])
    args = (os.path.join(inp, s["file"]), rng, s["high_loss_prob"], s["assign_loss_prob"],
            s["user_provided_loss_prob"])
    if s["kind"] == "clusters":
        data, samples, clusters = load_data(*args, cluster_file=os.path.join(inp, s["clusters"]),
                                            **common)
    elif s["kind"] == "hp":
        fn = F.phyclone_hp.make_loader(s["mode"], os.path.join(inp, "segments.tsv"))
        data, samples, clusters = fn(*args, **common)
    else:
        data, samples, clusters = load_data(*args, **common)
    return data, list(samples), clusters, s


def loss_assignment(case, s, data):
    """The --assign-loss-prob Monte Carlo test step by step, with the same rng draws as
    _assign_out_prob (cluster_outlier_probabilities.py), so a port can check each quantity."""
    from phyclone.data import cluster_outlier_probabilities as co
    from phyclone.data.pyclone import _get_raw_cluster_df, load_pyclone_data

    inp = os.path.join(CASES_DIR, case, "input")
    _, _, data_df = load_pyclone_data(os.path.join(inp, s["file"]))
    df, _ = _get_raw_cluster_df(os.path.join(inp, s["clusters"]), data_df)
    rng = np.random.default_rng(s["seed"])
    truncal = co._define_truncal_cluster(df)
    info = co._build_cluster_info_dict(df)
    truncal_dists = co._get_truncal_chrom_arr(df, truncal)
    rows, lost = [], []
    for cluster, c in info.items():  # same loop and rng order as _define_possibly_lost_clusters
        row = {"cluster_id": str(cluster), "num_mutations": c.num_mutations,
               "num_unique_chromosomes": c.num_unique_chromosomes, "tested": False}
        if cluster != truncal and c.num_mutations >= 4:
            tester = (np.resize(truncal_dists, c.num_mutations)
                      if c.num_mutations > len(truncal_dists) else truncal_dists)
            fewer = unique_sum = 0
            for _ in range(10000):
                k = len(np.unique(rng.choice(tester, size=c.num_mutations, replace=False)))
                unique_sum += k
                fewer += k < c.num_unique_chromosomes
            pvalue = (fewer or 1) / 10000
            estimate = (unique_sum / 10000) / c.num_unique_chromosomes
            row.update(tested=True, samples_fewer=fewer, num_unique_sum=unique_sum,
                       pvalue=pvalue, estimate=estimate,
                       resized=bool(c.num_mutations > len(truncal_dists)))
            if pvalue < 0.01 and estimate > 1:
                lost.append(str(cluster))
        rows.append(row)
    flagged = sorted(str(dp.name) for dp in data
                     if np.isclose(dp.outlier_prob, np.log(s["high_loss_prob"]) * size_of(case, s, dp)))
    assert sorted(lost) == flagged, (lost, flagged)
    return {"truncal_cluster": str(truncal), "truncal_chroms": [str(x) for x in truncal_dists],
            "min_clust_size": 4, "test_iters": 10000, "clusters": rows, "lost_clusters": lost}


def size_of(case, s, dp):
    c = pd.read_csv(os.path.join(CASES_DIR, case, "input", s["clusters"]), sep="\t")
    return c.loc[c.cluster_id.astype(str) == str(dp.name), "mutation_id"].nunique()


def cluster_probs(case, s, data):
    """Raw per-cluster outlier probability as the loader settled it (before the log)."""
    c = pd.read_csv(os.path.join(CASES_DIR, case, "input", s["clusters"]), sep="\t")
    sizes = c.groupby(c.cluster_id.astype(str)).mutation_id.nunique()
    return {str(dp.name): {"size": int(sizes[str(dp.name)]),
                           "outlier_prob_raw": F.num(np.exp(dp.outlier_prob / sizes[str(dp.name)]))}
            for dp in data}


def spec_of(tree):
    return {"nodes": F.tree_spec(tree), "outliers": sorted(str(dp.name) for dp in tree.outliers)}


def build(tr, dps):
    tree, made = F.build(tr["nodes"], dps)
    for m in tr["outliers"]:
        tree.add_data_point_to_outliers(dps[m])
    return tree


def trees_for(case, names):
    """MAP + evenly spaced iterations of each M7 reference trace, a few fixed trees, and seeded
    random trees whose data points are split between up to 8 nodes and the outlier node."""
    from phyclone.utils.load_hdf5 import (build_datapoints_dict_from_trace,
                                          build_map_tree_from_trace, load_chain_trace_data_df)

    out, seen = [], {}

    def add(name, spec):
        key = json.dumps(spec, sort_keys=True)
        if key in seen:
            seen[key].setdefault("aliases", []).append(name)
        else:
            seen[key] = {"id": name, **spec}
            out.append(seen[key])

    for run in CASES[case]["traces"]:
        tr = os.path.join(F.G, "runs", run, "trace.h5")
        df = load_chain_trace_data_df(tr)
        dps = build_datapoints_dict_from_trace(tr)
        m = df.loc[df["log_p"].idxmax()]
        add(f"{run}:map", spec_of(build_map_tree_from_trace(tr, int(m.chain_num), int(m.iter), dps)))
        for i in np.linspace(0, len(df) - 1, F.TREES_PER_TRACE).round().astype(int):
            r = df.iloc[i]
            add(f"{run}:iter{int(r['iter'])}",
                spec_of(build_map_tree_from_trace(tr, int(r.chain_num), int(r["iter"]), dps)))
    names = sorted(names)
    add("all_outliers", {"nodes": {}, "outliers": names})
    add("one_node", {"nodes": {"0": {"parent": "root", "mutations": names}}, "outliers": []})
    add("one_node_one_outlier", {"nodes": {"0": {"parent": "root", "mutations": names[1:]}},
                                 "outliers": names[:1]})
    rng = np.random.default_rng(int(hashlib.sha256(f"{case}:m7".encode()).hexdigest()[:8], 16))
    for k in range(RANDOM_TREES):
        n_out = int(rng.integers(1, max(1, len(names) // 3) + 1))
        order = rng.permutation(len(names))
        outliers = sorted(names[j] for j in order[:n_out])
        rest = [names[j] for j in sorted(order[n_out:])]
        n_nodes = int(rng.integers(1, min(F.MAX_RANDOM_NODES, len(rest)) + 1))
        perm = rng.permutation(len(rest))
        node = np.empty(len(rest), int)
        node[perm[:n_nodes]] = np.arange(n_nodes)
        node[perm[n_nodes:]] = rng.integers(0, n_nodes, len(rest) - n_nodes)
        parent = ["root"] + [("root" if rng.random() < 0.2 else str(int(rng.integers(0, i))))
                             for i in range(1, n_nodes)]
        add(f"random:{k}", {"nodes": {str(i): {"parent": parent[i],
                                               "mutations": [rest[j] for j in np.nonzero(node == i)[0]]}
                                      for i in range(n_nodes)}, "outliers": outliers})
    return out


def outlier_terms():
    from phyclone.data.base import DataPoint
    from phyclone.data.pyclone import compute_outlier_prob

    terms = []
    for p in TERM_PROBS:
        for n in TERM_SIZES:
            a, b = compute_outlier_prob(p, n)
            terms.append({"p": p, "size": n, "outlier_prob": F.num(a), "outlier_prob_not": F.num(b)})
    flat = []
    for g in (11, 101, 1000):  # likelihood 1 everywhere: the published integral is log 1 = 0
        flat.append({"grid_size": g, "num_samples": 2, "published": 0.0,
                     "outlier_marginal_prob": F.num(DataPoint(0, np.zeros((2, g))).outlier_marginal_prob),
                     "closed_form": F.num(2 * np.log((g + 1) / (2 * g)))})
    return {"compute_outlier_prob": terms, "constant_likelihood_marginal": flat}


def freeze_case(case, write):
    from phyclone.process_trace.process_trace import get_clone_table
    from phyclone.tree.distributions import FSCRPDistribution, TreeJointDistribution
    from phyclone.utils.math_utils import log_sum_exp_over_dims

    cfg = CASES[case]
    loaded = {ld: load(case, ld) for ld in cfg["loaders"]}
    for ld, (data, samples, _, s) in loaded.items():
        doc = {"case": case, "loader": ld, "settings": {k: v for k, v in s.items()},
               "samples": samples,
               "datapoints": [{"idx": int(dp.idx), "name": str(dp.name),
                               "outlier_prob": F.num(dp.outlier_prob),
                               "outlier_prob_not": F.num(dp.outlier_prob_not),
                               "outlier_marginal_prob": F.num(dp.outlier_marginal_prob),
                               "value": F.num(dp.value.tolist())} for dp in data]}
        if s["kind"] == "clusters":
            doc["clusters"] = cluster_probs(case, s, data)
        if s["assign_loss_prob"]:
            doc["loss_assignment"] = loss_assignment(case, s, data)
        write(f"datapoints/{case}__{ld}.json", doc)

    first = next(iter(loaded.values()))
    any_dps = {str(dp.name): dp for dp in first[0]}
    trees = trees_for(case, list(any_dps))
    tables = {}
    if cfg["pairs"]:
        inp = os.path.join(CASES_DIR, case, "input")
        tables = {pm: F.PairTable.from_files(f"{inp}/pairs.tsv", f"{inp}/data_hp.tsv",
                                             f"{inp}/segments.tsv", **kw)
                  for pm, kw in F.PAIR_MODELS.items()}
    rows = []
    for tr in trees:
        tree = build(tr, any_dps)
        row = {**tr, "num_outliers": len(tr["outliers"]),
               "prior": [F.prior_parts(tree, a) for a in ALPHAS]}
        if tables:
            row["pair_term"] = {pm: F.num(t.term(*F.tree_assignment(tree))) for pm, t in tables.items()}
        rows.append(row)
    write(f"trees/{cfg['trees']}.json", {"case": case, "alphas": list(ALPHAS), "trees": rows})

    for ld, (data, samples, clusters, s) in loaded.items():
        if ld in cfg.get("no_scores", []):
            continue
        active = s["outlier_prob"] > 0
        dps = {str(dp.name): dp for dp in data}
        out = []
        for tr in trees:
            tree = build(tr, dps)
            has_nodes = tree.get_number_of_children(tree.root_node_name) > 0
            j0 = TreeJointDistribution(FSCRPDistribution(1.0), active)
            r = {"id": tr["id"], "num_outliers": len(tr["outliers"]),
                 "data_log_likelihood": F.num(tree.data_log_likelihood.tolist()),
                 "data_log_p": F.num(log_sum_exp_over_dims(tree.data_log_likelihood) if has_nodes else 0.0),
                 "data_log_p_one": F.num(tree.data_log_likelihood[:, -1].sum() if has_nodes else 0.0),
                 "outlier_prior": F.num(j0.outlier_prior(tree)),
                 "outlier_marginal": F.num(j0.outlier_marginal_prob(tree))}
            for a in ALPHAS:
                j = TreeJointDistribution(FSCRPDistribution(a), active)
                lp, lp1 = j.log_p(tree), j.log_p_one(tree)
                both = j.compute_log_p_and_log_p_one(tree)
                assert abs(both[0] - lp) < 1e-9 and abs(both[1] - lp1) < 1e-9, (tr["id"], a)
                r[f"log_p@{a}"], r[f"log_p_one@{a}"] = F.num(lp), F.num(lp1)
            ids = [tr["id"], *tr.get("aliases", [])]
            if any(i.endswith(":map") for i in ids):
                table, _ = get_clone_table({dp.idx: dp for dp in data}, samples, tree, clusters=clusters)
                table = table.sort_values(["mutation_id", "sample_id"]).reset_index(drop=True)
                r["clone_table"] = {c: (F.num(table[c].tolist()) if table[c].dtype.kind == "f"
                                        else [str(v) for v in table[c]]) for c in table.columns}
            out.append(r)
        if s["grid_size"] >= 1000:
            direct_conv_scores(trees, dps, active, out)
        write(f"scores/{case}__{ld}.json", {"case": case, "loader": ld, "alphas": list(ALPHAS),
                                            "outlier_modelling_active": active,
                                            "grid_size": s["grid_size"], "trees": out})


def direct_conv_scores(trees, dps, active, out):
    """grid >= 1000 convolves by FFT (tree/utils.py _convolve_two_children). Score the same trees
    with np.convolve too: where the two differ, the FFT round-off floor (~1e-16 of the product
    of the children's maxima) sets the result, so a port can only match within its own FFT's
    round-off there."""
    import phyclone.tree.utils as U
    from phyclone.tree.distributions import FSCRPDistribution, TreeJointDistribution
    from phyclone.utils.cache import clear_convolution_caches
    from phyclone.utils.math_utils import np_conv_dims

    def direct(c1, c2):
        r = np_conv_dims(c1, c2)
        r.setflags(write=False)
        return r

    fft = U._convolve_two_children
    clear_convolution_caches()
    U._convolve_two_children = direct
    try:
        for tr, r in zip(trees, out):
            j = TreeJointDistribution(FSCRPDistribution(1.0), active)
            tree = build(tr, dps)
            r["log_p@1.0_direct_conv"] = F.num(j.log_p(tree))
            r["log_p_one@1.0_direct_conv"] = F.num(j.log_p_one(tree))
            r["fft_noise_dominated"] = bool(abs(r["log_p_one@1.0_direct_conv"] - r["log_p_one@1.0"]) > 1e-6)
    finally:
        U._convolve_two_children = fft
        clear_convolution_caches()


def freeze_all(write):
    write("outlier/terms.json", outlier_terms())
    for case in CASES:
        freeze_case(case, write)


if __name__ == "__main__":
    sys.exit("run freeze.py; it writes these fixtures too")
