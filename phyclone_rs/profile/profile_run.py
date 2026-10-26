"""Profile one golden reference run (phyclone_rs/golden/runs.tsv) in this process.

With --num-chains 1, phyclone/run.py calls run_phyclone_chain directly (no process pool), so a
cProfile of this process covers the chain work. Numba dispatchers are C objects that cProfile
does not record; each one bound in a phyclone module that defines no jitted code is replaced by a thin Python wrapper whose
code object is named nb_<function>, so its time shows up under that name.

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \
      phyclone_rs/profile/profile_run.py RUN [--no-profile] [--no-wrap]
Writes phyclone_rs/profile/<RUN>[.plain].{pstats,trace.h5,json}.
"""
import argparse
import cProfile
import csv
import json
import os
import sys
import time

T0 = time.perf_counter()
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
G = os.path.join(REPO, "phyclone_rs", "golden")
OUT = os.path.join(REPO, "phyclone_rs", "profile")
COMMON = ["-b", "20", "-n", "200", "--num-chains", "1", "--seed", "1"]


def run_argv(run, trace):
    with open(os.path.join(G, "runs.tsv")) as fh:
        rows = {r["run"]: r for r in csv.DictReader(fh, delimiter="\t")}
    r = rows[run]
    argv = r["argv"].replace("{in}", os.path.join(G, "cases", r["case"], "input"))
    return argv.split() + COMMON + ["-o", trace]


def wrap_numba():
    from numba.core.registry import CPUDispatcher
    from numba.np.ufunc.dufunc import DUFunc

    wrapped = {}
    names = []
    for mod_name, mod in list(sys.modules.items()):
        if not mod_name.startswith("phyclone") or mod is None:
            continue
        if any(isinstance(o, (CPUDispatcher, DUFunc)) and getattr(o, "__module__", None) == mod_name
               for o in vars(mod).values()):
            continue  # jitted code here resolves these globals at compile time
        for attr, obj in list(vars(mod).items()):
            if not isinstance(obj, (CPUDispatcher, DUFunc)):
                continue
            if id(obj) not in wrapped:
                def make(f):
                    def w(*a, **k):
                        return f(*a, **k)
                    return w
                w = make(obj)
                w.__code__ = w.__code__.replace(
                    co_name=f"nb_{attr}", co_filename="<numba>/phyclone/utils/math_utils.py")
                wrapped[id(obj)] = w
            setattr(mod, attr, wrapped[id(obj)])
            names.append(f"{mod_name}.{attr}")
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--no-profile", action="store_true")
    ap.add_argument("--no-wrap", action="store_true")
    opts = ap.parse_args()
    tag = opts.run + (".plain" if opts.no_profile else "")
    trace = os.path.join(OUT, f"{tag}.trace.h5")
    sys.argv = [os.path.join(REPO, "tools", "phyclone_hp.py")] + run_argv(opts.run, trace)
    sys.path.insert(0, os.path.join(REPO, "tools"))

    prof = None if opts.no_profile else cProfile.Profile()
    if prof:
        prof.enable()
    t_import = time.perf_counter()
    import phyclone.cli  # noqa: F401  (loads every phyclone module before wrapping)
    import phyclone.run  # noqa: F401
    import phyclone_hp
    wrapped = [] if opts.no_wrap else wrap_numba()
    t_main = time.perf_counter()
    try:
        phyclone_hp.main()
    except SystemExit as e:
        code = e.code
    else:
        code = 0
    t_end = time.perf_counter()
    if prof:
        prof.disable()
        prof.dump_stats(os.path.join(OUT, f"{tag}.pstats"))
    meta = {
        "run": opts.run,
        "argv": sys.argv,
        "exit_code": code,
        "profiled": prof is not None,
        "numba_wrapped": wrapped,
        "wall_script_s": t_end - T0,
        "wall_profiled_region_s": t_end - t_import,
        "wall_main_s": t_end - t_main,
        "loadavg_end": os.getloadavg(),
    }
    with open(os.path.join(OUT, f"{tag}.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != "numba_wrapped"}), file=sys.stderr)


if __name__ == "__main__":
    main()
