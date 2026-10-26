"""Time the convolution and the C4 pair term of one golden run without cProfile.

cProfile adds a fixed cost to every Python call, so code made of many tiny calls (the pair loop
does ~446M dict.get calls) looks more expensive under it than it is. This run wraps only three
entry points with perf_counter accumulators (a few hundred ns per call):
  tree_node.compute_log_S         convolution of child log R values, incl. its array-hash cache
  phyclone_pairs.tree_assignment  mutation -> node and node -> ancestors for the pair term
  phyclone_pairs.PairTable.term   the Python loop over eligible pairs

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \
      phyclone_rs/profile/time_run.py RUN
Writes phyclone_rs/profile/<RUN>.timed.{json,trace.h5}.
"""
import json
import os
import sys
import time

from profile_run import OUT, REPO, run_argv

T0 = time.perf_counter()
TIMERS = {}


def timed(name, f):
    acc = TIMERS.setdefault(name, [0.0, 0])

    def w(*a, **k):
        t = time.perf_counter()
        try:
            return f(*a, **k)
        finally:
            acc[0] += time.perf_counter() - t
            acc[1] += 1
    return w


def main():
    run = sys.argv[1]
    trace = os.path.join(OUT, f"{run}.timed.trace.h5")
    sys.argv = [os.path.join(REPO, "tools", "phyclone_hp.py")] + run_argv(run, trace)
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import phyclone.tree.tree_node as tn
    import phyclone_hp
    import phyclone_pairs

    tn.compute_log_S = timed("compute_log_S", tn.compute_log_S)
    phyclone_pairs.tree_assignment = timed("tree_assignment", phyclone_pairs.tree_assignment)
    phyclone_pairs.PairTable.term = timed("PairTable.term", phyclone_pairs.PairTable.term)
    t_main = time.perf_counter()
    try:
        phyclone_hp.main()
    except SystemExit:
        pass
    wall = time.perf_counter() - t_main
    meta = {"run": run, "wall_main_s": wall, "wall_script_s": time.perf_counter() - T0,
            "timers": {k: {"s": v[0], "calls": v[1], "pct_of_main": 100 * v[0] / wall}
                       for k, v in TIMERS.items()},
            "loadavg_end": os.getloadavg()}
    with open(os.path.join(OUT, f"{run}.timed.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(json.dumps(meta), file=sys.stderr)


if __name__ == "__main__":
    main()
