"""Truncal SNV multiplicity under CONIPHER's clonal WGD (no CNAs).

Runs CONIPHER's own topology + evolution code and reports, per seed, the share of truncal SNVs
with 2 mutant copies (SNV before the WGD) and 1 copy (after). graphviz is only used for plots,
so it is stubbed out.

Usage: python3 tools/conipher_wgd_multiplicity.py [--seeds 1 2 3] [--n-positions 2000]
"""
import argparse
import sys
import types
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parents[1] / \
    "research/simulation_pipeline_research/upstream/TRACERx_simulation_tool/src"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--n-positions", type=int, default=2000)
    ap.add_argument("--n-nodes", type=int, default=5)
    ap.add_argument("--prop-truncal", type=float, default=0.5)
    a = ap.parse_args()

    sys.modules.setdefault("graphviz", types.SimpleNamespace(Digraph=None))
    sys.path.insert(0, str(SRC))
    from evolution import tree_profiles
    from topology import simulate_topology

    print("seed\tn_truncal\tmult2\tmult1")
    for seed in a.seeds:
        np.random.seed(seed)
        nodes, edges, root, icc = simulate_topology(a.n_nodes)
        parents, children = np.array(list(zip(*edges)))
        leaves = children[~np.isin(children, parents)]
        # args after n_positions: prop_truncal, min_branch_length, prop_pos_gained, prop_pos_lost,
        # prop_gained_truncal, prop_lost_truncal, clonal_wgd, subclonal_wgd
        total, _, snv_edge, *_ = tree_profiles(nodes, edges, leaves, root, icc, a.n_positions,
                                               a.prop_truncal, 1, 0.0, 0.0, 1, 1, True, False)
        trunk = [p for e, ps in snv_edge.items() if e[0] == root for p in ps]
        m = np.array([total[icc][p][2] for p in trunk])
        print(f"{seed}\t{len(trunk)}\t{np.mean(m == 2):.3f}\t{np.mean(m == 1):.3f}")


if __name__ == "__main__":
    main()
