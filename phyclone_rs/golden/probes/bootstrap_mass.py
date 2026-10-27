"""Sampled vs logged proposal mass of the 0.8.0 bootstrap kernel with outliers on (semi-adapted for contrast).

Usage (from the repo root): env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
  phyclone_rs/golden/probes/bootstrap_mass.py
"""
import collections, contextlib, io, numpy as np
from phyclone.data.pyclone import load_data
from phyclone.smc.kernels import BootstrapKernel, SemiAdaptedKernel
from phyclone.tree import FSCRPDistribution, TreeJointDistribution
from phyclone.utils.cache import clear_proposal_dist_caches
with contextlib.redirect_stdout(io.StringIO()):
    data, _, _ = load_data("phyclone_rs/golden/cases/stress_e0_s1/input/data.tsv", np.random.default_rng(0), 0.4, False, False, density="binomial", outlier_prob=0.01)
for K in (BootstrapKernel, SemiAdaptedKernel):
    rng = np.random.default_rng(5)
    k = K(TreeJointDistribution(FSCRPDistribution(1.0), True), rng, outlier_modelling_active=True)
    parents = {}
    while len(parents) < 2:  # a first particle on a node (1 root) and one on the outlier node (0 roots)
        clear_proposal_dist_caches()
        p = k.propose_particle(data[0], None)
        parents.setdefault(len(p.tree_roots), p)
    for roots, parent in sorted(parents.items()):
        clear_proposal_dist_caches()
        q = k.get_proposal_distribution(data[1], parent)
        n, seen, cnt = 40000, {}, collections.Counter()
        for _ in range(n):
            t = q.sample()
            node = t.labels[data[1].idx]
            cat = "outlier" if node == t.outlier_node_name else ("existing" if node in set(parent.tree_roots) else "new")
            cnt[cat] += 1
            seen[t] = (cat, float(np.exp(q.log_p(t))))
        logged = collections.Counter()
        for cat, m in seen.values():
            logged[cat] += m
        print(K.__name__, f"parent roots={roots}", {c: (round(cnt[c] / n, 3), round(logged[c], 3)) for c in ("outlier", "existing", "new")})
