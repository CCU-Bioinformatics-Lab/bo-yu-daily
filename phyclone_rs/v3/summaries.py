"""Posterior summaries of one run (one seed; all its chains pooled), as fixed-length vectors.

Every summary is a 1-D float vector per run, so compare.py can test any of them with the same
permutation test on the difference of group means. KIND sets the distance:
  dist      a probability vector; distance = total variation of the mean vectors
  quant     several quantiles; each component is scaled by its SD across all pooled runs
  scalar    one number; distance = |difference of means|
  matrix    a flattened pair matrix; distance = mean |difference| over pairs

The trace holds only post-burn-in samples (PhyClone stores no SMC burn-in rows; the TSV reader
drops `phase` != sample), so every sample is used.

Truth summaries (configs whose case has golden/cases/<case>/truth/) reuse the project's metrics:
ARI from tools/eval_random_tree_phyclone.py, `compat` from tools/summarize_c4_robustness.py
(role-level truth compatibility, lost roles from the source sim's genome.json), `c3_under_c4`
from tools/summarize_hp_truth_topologies.py.
"""
import csv
import gzip
import json
import os
import sys

import numpy as np

from trace_io import OUTLIER, ROOT

V3 = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(V3))
GOLDEN = os.path.join(REPO, "phyclone_rs", "golden")
sys.path.insert(0, os.path.join(REPO, "tools"))

MAX_NODES = 16  # num_nodes / num_roots histogram; the last bin holds >= MAX_NODES

KIND = {
    "num_nodes": "dist", "num_roots": "dist", "log_alpha_q": "quant", "log_p_one_q": "quant",
    "map_log_p_one": "scalar", "step_change": "scalar", "coclust": "matrix", "ancestor": "matrix",
    "post_ari": "scalar", "map_ari": "scalar", "post_compat": "scalar", "map_compat": "scalar",
    "post_c3_under_c4": "scalar",
}
QUANTILES = (0.1, 0.5, 0.9)
DECIMALS = 6


def _hist(x):
    h = np.bincount(np.minimum(x, MAX_NODES), minlength=MAX_NODES + 1).astype(float)
    return h / h.sum()


def _ancestors(parent):
    """anc[a, d] = node a is a strict ancestor of node d."""
    k = len(parent)
    anc = np.zeros((k, k), dtype=bool)
    for d in range(k):
        p = parent[d]
        while p != ROOT:
            anc[p, d] = True
            p = parent[p]
    return anc


def _pair_matrices(tree):
    no = np.asarray(tree.node_of)
    ok = no != OUTLIER
    safe = np.where(ok, no, 0)
    both = ok[:, None] & ok[None, :]
    same = (no[:, None] == no[None, :]) & both
    anc = _ancestors(tree.parent)[safe[:, None], safe[None, :]] & both
    iu = np.triu_indices(len(no), 1)
    off = ~np.eye(len(no), dtype=bool)
    return same[iu], anc[off]


def run_summaries(trace, truth=None):
    """dict name -> np.ndarray for one run."""
    counts = np.bincount(trace.tree_idx, minlength=len(trace.trees)).astype(float)
    w = counts / counts.sum()
    out = {
        "num_nodes": _hist(trace.num_nodes),
        "num_roots": _hist(trace.num_roots),
        "log_alpha_q": np.quantile(np.log(trace.alpha), QUANTILES),
        "log_p_one_q": np.quantile(trace.log_p_one, QUANTILES),
        "map_log_p_one": np.array([trace.log_p_one.max()]),
    }
    co, an, pairs = 0.0, 0.0, {}
    for k, t in enumerate(trace.trees):
        if counts[k]:
            pairs[k] = _pair_matrices(t)
            co, an = co + w[k] * pairs[k][0], an + w[k] * pairs[k][1]
    out["coclust"], out["ancestor"] = np.asarray(co, float), np.asarray(an, float)
    flips = []
    for c in np.unique(trace.chain):
        t = trace.tree_idx[trace.chain == c]
        flips += [np.mean(pairs[a][0] != pairs[b][0]) for a, b in zip(t[:-1], t[1:])]
    out["step_change"] = np.array([np.mean(flips) if flips else 0.0])
    if truth is not None:
        out.update(truth.summaries(trace, w))
    # one rounding for every reader and the JSON cache, so a cached and a fresh run compare equal
    return {k: np.round(v, DECIMALS) for k, v in out.items()}


class Truth:
    """Truth of a simulated case, aligned to a trace's mutation order on use."""

    def __init__(self, case):
        from summarize_c4_robustness import load_truth

        tdir = os.path.join(GOLDEN, "cases", case, "truth")
        with open(os.path.join(tdir, "truth.tsv")) as fh:
            self.origin = {r["mutation_id"]: r["origin_clone"]
                           for r in csv.DictReader(fh, delimiter="\t")}
        self.roles = None
        src = _case_source(case)
        if os.path.exists(os.path.join(src, "truth", "genome.json")):
            with open(os.path.join(tdir, "truth.tsv")) as fh:
                roles = {r["role"] for r in csv.DictReader(fh, delimiter="\t")}
            if {"s5", "s6", "s7"} <= roles:  # the stress tree: role-level metrics apply
                self.roles = load_truth(os.path.join(src, "truth"))

    def summaries(self, trace, w):
        from eval_random_tree_phyclone import ari
        from summarize_c4_robustness import classify
        from summarize_hp_truth_topologies import is_descendant, majority

        missing = [m for m in trace.mutations if m not in self.origin]
        if missing:
            raise ValueError(f"mutations without truth: {missing[:3]}")
        truth_labels = [self.origin[m] for m in trace.mutations]
        imap = int(np.argmax(trace.log_p_one))
        map_k = trace.tree_idx[imap]
        per = {"ari": np.zeros(len(trace.trees))}
        if self.roles:
            per["compat"] = np.zeros(len(trace.trees))
            per["c3"] = np.zeros(len(trace.trees))
            role = self.roles[0]
        for k, t in enumerate(trace.trees):
            if not w[k] and k != map_k:
                continue
            per["ari"][k] = ari(truth_labels, list(t.node_of))
            if self.roles:
                clone_of = dict(zip(trace.mutations, t.node_of))
                parent = {n: p for n, p in enumerate(t.parent) if p != ROOT}
                per["compat"][k] = classify(clone_of, parent, *self.roles)[1]
                by_role = {}
                for m, n in clone_of.items():
                    by_role.setdefault(role[m], []).append(n)
                c3 = majority(by_role["s6"] + by_role["s7"])
                per["c3"][k] = is_descendant(c3, majority(by_role["s5"]), parent)
        out = {"post_ari": np.array([w @ per["ari"]]), "map_ari": np.array([per["ari"][map_k]])}
        if self.roles:
            out["post_compat"] = np.array([w @ per["compat"]])
            out["map_compat"] = np.array([per["compat"][map_k]])
            out["post_c3_under_c4"] = np.array([w @ per["c3"]])
        return out


def _case_source(case):
    with open(os.path.join(GOLDEN, "cases.tsv")) as fh:
        src = {r["case"]: r["source"] for r in csv.DictReader(fh, delimiter="\t")}
    return os.path.join(REPO, src[case])


def config_case():
    with open(os.path.join(GOLDEN, "runs.tsv")) as fh:
        return {r["run"]: r["case"] for r in csv.DictReader(fh, delimiter="\t")}


def truth_for(run):
    case = config_case()[run]
    return Truth(case) if os.path.isdir(os.path.join(GOLDEN, "cases", case, "truth")) else None


def summarize_root(root, config, seed_dirs=None):
    """{seed dir name: summaries} for every seed dir under root/config (trace.h5 or TSV dir).
    config is a golden run name, optionally with a .<variant> suffix."""
    from trace_io import read_trace

    truth = truth_for(config.split(".")[0])
    base = os.path.join(root, config)
    names = seed_dirs or sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    res, mutations = {}, None
    for name in names:
        tr = read_trace(os.path.join(base, name))
        if mutations is None:
            mutations = tr.mutations
        elif tr.mutations != mutations:
            raise ValueError(f"{base}/{name}: mutation set differs from the first seed")
        res[name] = run_summaries(tr, truth)
    return res, mutations


def save(path, per_seed, mutations, meta=None):
    """gzip JSON cache of per-run summaries (already rounded by run_summaries)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = {"meta": meta or {}, "mutations": mutations, "kind": KIND,
           "seeds": {s: {k: v.tolist() for k, v in d.items()}
                     for s, d in per_seed.items()}}
    with gzip.open(path, "wt") as fh:
        json.dump(doc, fh, separators=(",", ":"))


def load(path):
    with gzip.open(path, "rt") as fh:
        doc = json.load(fh)
    per_seed = {s: {k: np.asarray(v, float) for k, v in d.items()} for s, d in doc["seeds"].items()}
    return per_seed, doc["mutations"]


def describe(per_seed):
    """Short human-readable per-seed table rows for the README tables."""
    rows = []
    for s, d in per_seed.items():
        nn = d["num_nodes"]
        rows.append({"seed": s,
                     "mean_nodes": float(nn @ np.arange(len(nn))),
                     "mode_nodes": int(np.argmax(nn)),
                     "alpha_median": float(np.exp(d["log_alpha_q"][1])),
                     "map_log_p_one": float(d["map_log_p_one"][0]),
                     "step_change": float(d["step_change"][0]),
                     **{k: float(d[k][0]) for k in ("post_ari", "map_ari", "post_compat",
                                                     "map_compat", "post_c3_under_c4") if k in d}})
    return rows

