"""Summarise <run>.pstats from profile_run.py as markdown tables.

Each function's own time (tottime) goes to one bucket (a Rust module of PORTING.md section 2).
Time in numpy / scipy / builtins / rustworkx is not a bucket of its own: it is handed up the
call graph, split by the caller edges' tottime, to the nearest phyclone or tools frame. Numba
compile frames and import machinery stop the walk and get buckets of their own.

Usage: python3 phyclone_rs/profile/analyze.py RUN [RUN ...]
"""
import json
import os
import pstats
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CONV = {"fft_convolve_two_children", "np_conv_dims", "compute_log_S", "compute_log_D",
        "_convolve_two_children"}


def own_bucket(func):
    path, _, name = func
    p = path.replace("\\", "/")
    if "/numba/" in p or "/llvmlite/" in p:
        return "jit compile (numba)"
    if "importlib" in p or p.startswith("<frozen"):
        return "startup (import)"
    if p.startswith("<numba>"):
        return "math (numba)"
    if p.endswith("tools/phyclone_hp.py"):
        return "data::hp"
    if p.endswith("tools/phyclone_pairs.py"):
        return "pairs"
    if "site-packages/" in p or "/phyclone/" not in p:
        return None
    if p.endswith("utils/math_utils.py") and name == "<listcomp>" and 247 <= func[1] <= 253:
        return "tree::conv"  # the per-sample np.convolve loop inside np_conv_dims
    if name in CONV and (p.endswith("tree/utils.py") or p.endswith("utils/math_utils.py")):
        return "tree::conv"
    if p.endswith("utils/math_utils.py"):
        return "math"
    if "/phyclone/data/" in p:
        return "data"
    if p.endswith("tree/distributions.py"):
        return "prior/joint"
    if "/phyclone/tree/" in p:
        return "tree/" + p.rsplit("/", 1)[1]
    if p.endswith(("utils/cache.py", "utils/hashing_utils.py", "utils/__init__.py")):
        return "tree::conv (array-hash cache)"  # only compute_log_S / _convolve_two_children use it
    if "/phyclone/smc/" in p:
        return "smc"
    if "/phyclone/mcmc/" in p:
        return "mcmc"
    if p.endswith("phyclone/run.py"):
        return "run"
    if "/process_trace/" in p or p.endswith(("save_hdf5.py", "load_hdf5.py")):
        return "trace"
    if p.endswith("phyclone/cli.py"):
        return "cli"
    return "other phyclone"


GROUPS = {"tree::conv": "tree: convolution (compute_log_S/D + cache)",
          "tree": "tree: structure, copy, node updates",
          "jit compile": "startup (import, numba jit)", "startup": "startup (import, numba jit)",
          "data::hp": "data", "unattributed": "other", "other phyclone": "other",
          "cli": "run/cli", "run": "run/cli"}


def group_of(bucket):
    key = bucket.split(" (")[0]
    if key.startswith("tree/"):
        key = "tree"
    return GROUPS.get(key, key)


def owner_shares(stats):
    """func -> {owner func or bucket: fraction}; owner = nearest frame that has a bucket."""
    memo = {}

    def shares(func, stack):
        if func in memo:
            return memo[func]
        if own_bucket(func) is not None:
            return {func: 1.0}
        if func in stack:
            return {("cycle",): 1.0}
        callers = stats[func][4]
        weights = {c: v[2] for c, v in callers.items()}
        tot = sum(weights.values())
        if tot <= 0:
            weights = {c: v[1] for c, v in callers.items()}
            tot = sum(weights.values())
        if not callers or tot <= 0:
            out = {("root",): 1.0}
        else:
            out = defaultdict(float)
            for c, w in weights.items():
                for o, f in shares(c, stack | {func}).items():
                    out[o] += f * w / tot
        memo[func] = dict(out)
        return memo[func]

    return {f: shares(f, frozenset()) for f in stats}


def label(func):
    path, line, name = func
    if path == "~":
        return name
    p = path.replace("\\", "/")
    for key in ("site-packages/", "/phyclone/", "tools/"):
        if key in p:
            p = p.split(key, 1)[1] if key != "/phyclone/" else "phyclone/" + p.split(key, 1)[1]
            break
    return f"{p}:{line}({name})"


def summarise(run):
    st = pstats.Stats(os.path.join(HERE, f"{run}.pstats"))
    stats = st.stats
    meta = json.load(open(os.path.join(HERE, f"{run}.json")))
    total = st.total_tt
    shares = owner_shares(stats)
    attributed = defaultdict(float)  # owner frame -> own + handed-up external time
    for f, (_, _, tt, _, _) in stats.items():
        for o, frac in shares[f].items():
            attributed[o] += tt * frac
    buckets = defaultdict(float)
    for o, t in attributed.items():
        b = own_bucket(o) if len(o) == 3 else "unattributed"
        buckets[b] += t

    out = [f"### {run}", ""]
    out.append(f"- profiled total (sum of tottime): {total:.1f} s")
    out.append(f"- wall of the profiled region: {meta['wall_profiled_region_s']:.1f} s; "
               f"wall of phyclone_hp.main: {meta['wall_main_s']:.1f} s; exit code {meta['exit_code']}")
    groups = defaultdict(float)
    for b, t in buckets.items():
        g = group_of(b)
        groups[g] += t
    out += ["", "| Rust module (PORTING.md 2) | s | % |", "|---|---:|---:|"]
    for g, t in sorted(groups.items(), key=lambda x: -x[1]):
        out.append(f"| {g} | {t:.1f} | {100 * t / total:.1f} |")
    out += ["", "| bucket (finer) | s | % |", "|---|---:|---:|"]
    for b, t in sorted(buckets.items(), key=lambda x: -x[1]):
        out.append(f"| {b} | {t:.1f} | {100 * t / total:.1f} |")

    def table(title, key, n=15):
        rows = sorted(stats.items(), key=lambda kv: -key(kv[1]))[:n]
        lines = ["", f"#### {title}", "", "| function | ncalls | tottime s | cumtime s | % of total |",
                 "|---|---:|---:|---:|---:|"]
        for f, (cc, nc, tt, ct, _) in rows:
            v = key((cc, nc, tt, ct, None))
            lines.append(f"| `{label(f)}` | {nc} | {tt:.1f} | {ct:.1f} | {100 * v / total:.1f} |")
        return lines

    out += table("top 15 by tottime", lambda s: s[2])
    out += table("top 15 by cumtime", lambda s: s[3])
    out += ["", "#### top 15 phyclone/tools frames by attributed time (own + numpy/scipy/builtins below them)",
            "", "| function | bucket | attributed s | % |", "|---|---|---:|---:|"]
    for o, t in sorted(((o, t) for o, t in attributed.items() if len(o) == 3),
                       key=lambda x: -x[1])[:15]:
        out.append(f"| `{label(o)}` | {own_bucket(o)} | {t:.1f} | {100 * t / total:.1f} |")
    return "\n".join(out)


if __name__ == "__main__":
    print("\n\n".join(summarise(r) for r in sys.argv[1:]))
