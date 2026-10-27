"""V4: run Python PhyClone 0.8.0 and haploclone (Rust) on the paper-benchmark subset, then score.

Jobs come from lab_report/2026-10-27_v4_evaluator/proposed_subset.tsv (one row = trial x program).
Each job runs `run` with the paper settings, then `map` (joint-likelihood) and
`topology-report -t topologies.tar.gz`, in OUT_ROOT/<impl>/<job key>/:
  command.txt, run.log, map.log, topo.log, trace (trace.h5 | trace/), map_table.tsv, map_tree.nwk,
  map_prev.tsv, topology_report.tsv, topologies.tar.gz, status.json (written last, atomically).
A job with status.json is not rerun (a failed one only with --retry-failed), so a rerun resumes.
Jobs start longest first by the paper's wall time. No job starts after --launch-deadline seconds.
Each finished job appends one line to OUT_ROOT/<impl>/progress.tsv.

Usage:
  run_v4.py run --impl python080|rust [--slots 14] [--launch-deadline 7200]
  run_v4.py progress
  run_v4.py score      # writes results.tsv and summary.tsv next to this script
"""
import argparse
import csv
import json
import math
import os
import shlex
import statistics
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
import eval_phyclone_dataset as ev  # noqa: E402

DATA = "/big8_disk/boyu114/phyclone_dataset"
OUT_ROOT = "/big8_disk/boyu114/phyclone_v4"
EVAL_DIR = os.path.join(REPO, "lab_report", "2026-10-27_v4_evaluator")
SUBSET = os.path.join(EVAL_DIR, "proposed_subset.tsv")
PAPER = os.path.join(EVAL_DIR, "validation_paper_outputs.tsv")
PHYCLONE_SRC = os.path.join(REPO, "research", "phyclone_research", "PhyClone")
PYTHON = os.path.expanduser("~/venvs/phyclone/bin/python")
RUST = "/bip8_disk/boyu114/haploclone/rust/target/release/haploclone"
PAPER_ARGS = ["--num-chains", "4", "-b", "100", "-n", "5000", "--num-particles", "100",
              "-d", "beta-binomial", "-p", "semi-adapted", "--seed", "1"]
LOSS_ARGS = {"PhyClone": ["--assign-loss-prob"], "PhyClone-N": []}
INPUT_DIR = {"PhyClone": "phyclone_outliers", "PhyClone-N": "phyclone_naive"}
CLUSTER_FILES = ("results.tsv.gz", "results.tsv", "clusters.tsv.gz")
SINGLE_THREAD = {k: "1" for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                  "NUMBA_NUM_THREADS")}
IMPLS = ("python080", "rust")


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def job_key(row):
    return row["trial"].replace("/data_archive/", "/").replace("/", "__") + "." + row["program"]


def jobs():
    return sorted(read_tsv(SUBSET), key=lambda r: -float(r["paper_wall_s"]))


def inputs(row):
    d = os.path.join(DATA, row["trial"], "program_inputs", INPUT_DIR[row["program"]])
    clusters = [os.path.join(d, f) for f in CLUSTER_FILES if os.path.exists(os.path.join(d, f))]
    assert len(clusters) == 1, (d, clusters)
    return os.path.join(d, "data.tsv"), clusters[0]


def commands(impl, row, out):
    data, clusters = inputs(row)
    if impl == "python080":
        base = [PYTHON, "-c", "from phyclone.cli import main; main()"]
        trace = os.path.join(out, "trace.h5")
        run = base + ["run", "-i", data, "-c", clusters, "-o", trace]
    else:
        base = [RUST]
        trace = os.path.join(out, "trace")
        run = base + ["run", "-i", data, "-c", clusters, "-o", trace]
    run += PAPER_ARGS + LOSS_ARGS[row["program"]]
    mp = base + ["map", "-i", trace, "-o", os.path.join(out, "map_table.tsv"),
                 "-t", os.path.join(out, "map_tree.nwk"), "-s", os.path.join(out, "map_prev.tsv")]
    topo = base + ["topology-report", "-i", trace, "-o", os.path.join(out, "topology_report.tsv"),
                   "-t", os.path.join(out, "topologies.tar.gz")]
    return [("run", run), ("map", mp), ("topo", topo)]


def env_for(impl):
    env = dict(os.environ, **SINGLE_THREAD)
    if impl == "python080":
        env["PYTHONPATH"] = PHYCLONE_SRC
    return env


def run_job(impl, row, lock):
    out = os.path.join(OUT_ROOT, impl, job_key(row))
    os.makedirs(out, exist_ok=True)
    cmds = commands(impl, row, out)
    with open(os.path.join(out, "command.txt"), "w") as fh:
        for _, c in cmds:
            fh.write(shlex.join(c) + "\n")
    status = {"impl": impl, "key": job_key(row), "start": time.time(), "steps": {}}
    for step, cmd in cmds:
        t0 = time.time()
        with open(os.path.join(out, step + ".log"), "w") as log:
            rc = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT, env=env_for(impl), cwd=out)
        status["steps"][step] = {"exit": rc, "wall_s": time.time() - t0}
        if rc != 0:
            break
    status["ok"] = all(s["exit"] == 0 for s in status["steps"].values()) and len(status["steps"]) == 3
    tmp = os.path.join(out, "status.json.tmp")
    with open(tmp, "w") as fh:
        json.dump(status, fh, indent=1)
    os.replace(tmp, os.path.join(out, "status.json"))
    with lock, open(os.path.join(OUT_ROOT, impl, "progress.tsv"), "a") as fh:
        run_s = status["steps"]["run"]["wall_s"]
        fh.write(f"{time.strftime('%H:%M:%S')}\t{job_key(row)}\t{'ok' if status['ok'] else 'FAIL'}"
                 f"\trun_s={run_s:.0f}\tpaper_s={float(row['paper_wall_s']):.0f}\n")


def status_of(impl, row):
    p = os.path.join(OUT_ROOT, impl, job_key(row), "status.json")
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def cmd_run(a):
    os.makedirs(os.path.join(OUT_ROOT, a.impl), exist_ok=True)
    todo = [r for r in jobs() if (s := status_of(a.impl, r)) is None or (a.retry_failed and not s["ok"])]
    t_start, lock = time.time(), threading.Lock()

    def guarded(row):
        if time.time() - t_start > a.launch_deadline:
            with lock, open(os.path.join(OUT_ROOT, a.impl, "progress.tsv"), "a") as fh:
                fh.write(f"{time.strftime('%H:%M:%S')}\t{job_key(row)}\tNOT_LAUNCHED (deadline)\n")
            return
        run_job(a.impl, row, lock)

    with open(os.path.join(OUT_ROOT, a.impl, "progress.tsv"), "a") as fh:
        fh.write(f"# {time.strftime('%F %T')} start impl={a.impl} slots={a.slots} jobs={len(todo)}\n")
    with ThreadPoolExecutor(a.slots) as pool:
        list(pool.map(guarded, todo))
    with open(os.path.join(OUT_ROOT, a.impl, "progress.tsv"), "a") as fh:
        fh.write(f"# {time.strftime('%F %T')} end impl={a.impl} wall_s={time.time() - t_start:.0f}\n")


def cmd_progress(_):
    rows = jobs()
    for impl in IMPLS:
        st = [status_of(impl, r) for r in rows]
        done = sum(1 for s in st if s and s["ok"])
        failed = [s["key"] for s in st if s and not s["ok"]]
        running = [job_key(r) for r, s in zip(rows, st) if s is None
                   and os.path.exists(os.path.join(OUT_ROOT, impl, job_key(r), "command.txt"))]
        print(f"{impl}: done {done}/{len(rows)}, running {len(running)}, failed {len(failed)}")
        for k in failed:
            print(f"  FAILED {k}")
        prog = os.path.join(OUT_ROOT, impl, "progress.tsv")
        if os.path.exists(prog):
            with open(prog) as fh:
                lines = [l for l in fh if l.startswith("#")]
            print("  " + "  ".join(lines[-2:]).rstrip())


# ---------------------------------------------------------------- scoring

def group_of(row):
    ds = "HGSOC" if row["ds"].startswith("HGSOC") else row["ds"]
    return ds + ("/N" if row["program"] == "PhyClone-N" else "")


def map_stats(table):
    rows = read_tsv(table)
    clones = {r["clone_id"] for r in rows if r["clone_id"] != ev.OUTLIER}
    outliers = {r["mutation_id"] for r in rows if r["clone_id"] == ev.OUTLIER}
    return len(clones), len(outliers)


def cmd_score(_):
    paper = {(r["program"], r["trial"]): r for r in read_tsv(PAPER)}
    out = []
    for row in jobs():
        trial_dir = os.path.join(DATA, row["trial"])
        truth = ev.tree_from_json(os.path.join(trial_dir, "ground_truth", "tree.json"))
        p = paper[(row["program"], row["trial"])]
        pdir = os.path.join(trial_dir, "program_outputs", INPUT_DIR[row["program"]])
        sources = [("paper070", pdir, os.path.join(pdir, "results.tsv"), float(p["time"]))]  # V, AD from the xlsx
        for impl in IMPLS:
            s = status_of(impl, row)
            d = os.path.join(OUT_ROOT, impl, job_key(row))
            sources.append((impl, d if s and s["ok"] else None, os.path.join(d, "map_table.tsv"),
                            s["steps"]["run"]["wall_s"] if s else float("nan")))
        for impl, d, table, wall in sources:
            rec = {"group": group_of(row), "ds": row["ds"], "program": row["program"], "trial": row["trial"],
                   "impl": impl, "run_wall_s": f"{wall:.1f}"}
            if d is None:
                rec.update(v_measure="nan", ad_f="nan", n_pred="", n_true="", n_clones="", n_outliers="", ok=0)
            elif impl == "paper070":
                n_clones, n_out = map_stats(table)
                rec.update(v_measure=p["xlsx_v_measure"], ad_f=p["xlsx_ancestor_descendant_f_score"],
                           n_pred=int(float(p["xlsx_num_mutations_pred"])),
                           n_true=int(float(p["xlsx_num_mutations_true"])),
                           n_clones=n_clones, n_outliers=n_out, ok=1)
            else:
                with open(os.path.join(d, "map_tree.nwk")) as fh:
                    assert not any(c.isspace() for c in fh.read().strip()), f"whitespace in {d}/map_tree.nwk"
                sc = ev.score(truth, ev.read_prediction(d, "table"))
                n_clones, n_out = map_stats(table)
                rec.update(v_measure=repr(sc["v_measure"]), ad_f=repr(sc["ancestor_descendant_f_score"]),
                           n_pred=sc["num_mutations_pred"], n_true=sc["num_mutations_true"],
                           n_clones=n_clones, n_outliers=n_out, ok=1)
            out.append(rec)
    with open(os.path.join(HERE, "results.tsv"), "w") as fh:
        w = csv.DictWriter(fh, list(out[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    summarize(out)


def wilcoxon_sign(d):
    from scipy.stats import binomtest, wilcoxon
    nz = [x for x in d if x != 0]
    pos, neg = sum(x > 0 for x in nz), sum(x < 0 for x in nz)
    p_w = wilcoxon(nz).pvalue if len(nz) >= 1 and any(nz) else 1.0
    p_s = binomtest(pos, pos + neg).pvalue if nz else 1.0
    return p_w, p_s, pos, neg


def p3_ad(trial):
    return trial.startswith("HGSOC/p3")


def summarize(rows):
    by = {}
    for r in rows:
        by.setdefault((r["program"], r["trial"]), {})[r["impl"]] = r
    pairs = [("rust", "python080"), ("rust", "paper070"), ("python080", "paper070")]
    groups = sorted({r["group"] for r in rows}) + ["ALL"]
    out = []
    for g in groups:
        trials = [t for t in by.values() if g == "ALL" or t["paper070"]["group"] == g]
        for metric in ("v_measure", "ad_f"):
            rec = {"group": g, "metric": metric, "n_trials": len(trials)}
            for impl in ("paper070", "python080", "rust"):
                xs = [float(t[impl][metric]) for t in trials
                      if not (metric == "ad_f" and impl == "paper070" and p3_ad(t[impl]["trial"]))]
                xs = [x for x in xs if not math.isnan(x)]
                rec[f"mean_{impl}"] = f"{statistics.mean(xs):.4f}" if xs else ""
            for a, b in pairs:
                d = [float(t[a][metric]) - float(t[b][metric]) for t in trials
                     if not (metric == "ad_f" and "paper070" in (a, b) and p3_ad(t[a]["trial"]))]
                d = [x for x in d if not math.isnan(x)]
                tag = f"{a}-{b}"
                if not d:
                    continue
                p_w, p_s, pos, neg = wilcoxon_sign(d)
                rec.update({f"{tag}_n": len(d), f"{tag}_mean": f"{statistics.mean(d):+.4f}",
                            f"{tag}_median": f"{statistics.median(d):+.4f}",
                            f"{tag}_pos_neg": f"{pos}/{neg}", f"{tag}_p_wilcoxon": f"{p_w:.3g}",
                            f"{tag}_p_sign": f"{p_s:.3g}", f"{tag}_n_worse_0.05": sum(x < -0.05 for x in d)})
            out.append(rec)
        walls = [(float(t["paper070"]["run_wall_s"]), float(t["python080"]["run_wall_s"]),
                  float(t["rust"]["run_wall_s"])) for t in trials]
        walls = [w for w in walls if not any(math.isnan(x) for x in w)]
        if walls:
            rec = {"group": g, "metric": "run_wall_s", "n_trials": len(walls)}
            for i, impl in enumerate(("paper070", "python080", "rust")):
                rec[f"mean_{impl}"] = f"{statistics.mean(w[i] for w in walls):.1f}"
                rec[f"sum_h_{impl}"] = f"{sum(w[i] for w in walls) / 3600:.3f}"
            rec["median_python_over_rust"] = f"{statistics.median(w[1] / w[2] for w in walls):.1f}"
            rec["median_python_over_paper"] = f"{statistics.median(w[1] / w[0] for w in walls):.2f}"
            out.append(rec)
    keys =list(dict.fromkeys(k for r in out for k in r))
    with open(os.path.join(HERE, "summary.tsv"), "w") as fh:
        w = csv.DictWriter(fh, keys, delimiter="\t", lineterminator="\n", restval="")
        w.writeheader()
        w.writerows(out)
    for r in out:
        if r["group"] == "ALL" and "rust-python080_median" in r:
            med = float(r["rust-python080_median"])
            p = float(r["rust-python080_p_wilcoxon"])
            mean = float(r["rust-python080_mean"])
            verdict = ("PASS" if abs(med) <= 0.01 and p >= 0.01 else
                       "WORSE" if med < -0.01 or mean < 0 else "DIFFERENT (Rust better)")
            print(f"{r['metric']}: rust-python median {med:+.4f}, wilcoxon p {p:.3g} -> {verdict}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--impl", choices=IMPLS, required=True)
    r.add_argument("--slots", type=int, default=14)
    r.add_argument("--launch-deadline", type=float, default=7200)
    r.add_argument("--retry-failed", action="store_true")
    sub.add_parser("progress")
    sub.add_parser("score")
    a = ap.parse_args()
    {"run": cmd_run, "progress": cmd_progress, "score": cmd_score}[a.cmd](a)


if __name__ == "__main__":
    main()
