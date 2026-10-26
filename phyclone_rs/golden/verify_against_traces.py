"""Check that the frozen fixtures reproduce what the Python sampler scored.

For each reference run, rebuild its MAP tree from fixtures/trees, load the run's datapoints and
pair model, and recompute log_p_one at the MAP sample's alpha. It must equal the log_p the trace
stored for that sample (|diff| < 1e-9). A mismatch means the fixture was frozen with the wrong
loader or options, so the fixture would not describe the model the run sampled from.

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
    phyclone_rs/golden/verify_against_traces.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import freeze as f  # noqa: E402
from phyclone_pairs import PairTable, tree_assignment  # noqa: E402

RUNS = {  # run -> (case, loader, pair model or None)
    "e0_base_bin": ("stress_e0_s1", "base_binomial", None),
    "real_a2_err004": ("stress_real_s1", "a2_binomial", "err0.004"),
    "b03_base_eps001": ("stress_b03_s1", "base_binomial", "eps0.01"),
    "b03_base_err003_hpu": ("stress_b03_s1", "base_binomial", "err0.03_hpu"),
    "random_a1_bin": ("random_spec_0000", "a1_binomial", None),
    "random_base_betabin": ("random_spec_0000", "base_betabin", None),
    "upstream_clusters": ("upstream_mixing_small", "upstream_clusters", None),
}


def main():
    from phyclone.tree.distributions import FSCRPDistribution, TreeJointDistribution

    worst = 0.0
    for run, (case, loader, pm) in RUNS.items():
        chain, it, alpha, stored = None, None, None, None
        from phyclone.utils.load_hdf5 import load_chain_trace_data_df
        df = load_chain_trace_data_df(os.path.join(f.G, "runs", run, "trace.h5"))
        m = df.loc[df["log_p"].idxmax()]
        alpha, stored = float(m["alpha"]), float(m["log_p"])
        trees = json.load(open(os.path.join(f.G, "fixtures", "trees", f"{case}.json")))["trees"]
        spec = next(t for t in trees if f"{run}:map" in [t["id"], *t.get("aliases", [])])["nodes"]
        data, _, _ = f.load_datapoints(case, loader)
        tree, _ = f.build(spec, {str(dp.name): dp for dp in data})
        total = TreeJointDistribution(FSCRPDistribution(alpha)).log_p_one(tree)
        if pm:
            inp = os.path.join(f.G, "cases", case, "input")
            t = PairTable.from_files(f"{inp}/pairs.tsv", f"{inp}/data_hp.tsv",
                                     f"{inp}/segments.tsv", **f.PAIR_MODELS[pm])
            total += t.term(*tree_assignment(tree))
        d = total - stored
        worst = max(worst, abs(d))
        print(f"{run}\talpha={alpha:.4f}\tstored={stored:.6f}\trecomputed={total:.6f}\tdiff={d:.2e}")
    print("OK" if worst < 1e-9 else f"MISMATCH (max |diff| = {worst:.2e})")
    sys.exit(0 if worst < 1e-9 else 1)


if __name__ == "__main__":
    main()
