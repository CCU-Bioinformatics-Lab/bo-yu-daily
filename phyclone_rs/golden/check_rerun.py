"""Rerun golden reference runs with the same command and check that nothing changed.

For each run: rerun runs/<run>/command.txt with the trace written to a temporary directory, run
map, consensus and topology-report on it, then compare with runs/<run>/:
  trace.h5   every dataset and attribute, except the wall-clock `time` columns
  outputs    map_*, consensus_*, topology_report.tsv byte by byte (topologies.tar.gz holds file
             times, so its members are compared instead)
A post-processing step that failed in the golden run must fail the same way.

Usage (from the repo root):
  env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
    phyclone_rs/golden/check_rerun.py RUN [RUN ...] [--jobs N]
"""
import argparse
import filecmp
import os
import subprocess
import sys
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor

import h5py
import numpy as np

G = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(G))
PY = os.path.expanduser("~/venvs/phyclone/bin/python")
ENV = {**os.environ, "PYTHONPATH": os.path.join(ROOT, "research", "phyclone_research", "PhyClone")}
CLI = [PY, "-c", "from phyclone.cli import main; main()"]
OUTPUTS = ["map_tree.nwk", "map_table.tsv", "map_sample_prev.tsv", "consensus_tree.nwk",
           "consensus_table.tsv", "consensus_sample_prev.tsv", "topology_report.tsv"]


def h5_items(path):
    out = {}
    with h5py.File(path, "r") as f:
        def visit(name, obj):
            for k, v in obj.attrs.items():  # an object reference is compared by its target
                out[f"{name}@{k}"] = f[v].name if isinstance(v, h5py.Reference) else np.asarray(v)
            if isinstance(obj, h5py.Dataset) and not name.endswith("/time"):
                out[name] = obj[()]
        out.update({f"@{k}": np.asarray(v) for k, v in f.attrs.items()})
        f.visititems(visit)
    return out


def same(a, b):
    if not isinstance(a, np.ndarray) and not isinstance(b, np.ndarray):
        return type(a) is type(b) and a == b
    a, b = np.asarray(a), np.asarray(b)
    if a.dtype != b.dtype or a.shape != b.shape:
        return False
    if a.dtype.kind == "O":
        return all(same(x, y) for x, y in zip(a.ravel().tolist(), b.ravel().tolist()))
    if a.dtype.kind == "f":
        return np.array_equal(a, b, equal_nan=True)
    return a.tobytes() == b.tobytes()


def tar_members(path):
    with tarfile.open(path) as t:
        return {m.name: t.extractfile(m).read() for m in t.getmembers() if m.isfile()}


def check(run):
    R = os.path.join(G, "runs", run)
    cmd = open(os.path.join(R, "command.txt")).read().split()
    golden_trace = cmd[cmd.index("-o") + 1]
    with tempfile.TemporaryDirectory() as tmp:
        cmd[cmd.index("-o") + 1] = os.path.join(tmp, "trace.h5")
        subprocess.run([PY] + cmd, cwd=ROOT, env=ENV, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
        t = os.path.join(tmp, "trace.h5")
        post = {
            "map": ["map", "-i", t, "-t", f"{tmp}/map_tree.nwk", "-o", f"{tmp}/map_table.tsv",
                    "-s", f"{tmp}/map_sample_prev.tsv"],
            "consensus": ["consensus", "-i", t, "-t", f"{tmp}/consensus_tree.nwk",
                          "-o", f"{tmp}/consensus_table.tsv", "-s", f"{tmp}/consensus_sample_prev.tsv"],
            "topology-report": ["topology-report", "-i", t, "-o", f"{tmp}/topology_report.tsv",
                                "-t", f"{tmp}/topologies.tar.gz"]}
        for args in post.values():
            subprocess.run(CLI + args, cwd=ROOT, env=ENV, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        a, b = h5_items(os.path.join(ROOT, golden_trace)), h5_items(t)
        bad = sorted(k for k in set(a) | set(b) if k not in a or k not in b or not same(a[k], b[k]))
        for f in OUTPUTS:
            g, n = os.path.join(R, f), os.path.join(tmp, f)
            if os.path.exists(g) != os.path.exists(n) or (os.path.exists(g) and
                                                         not filecmp.cmp(g, n, shallow=False)):
                bad.append(f)
        if tar_members(os.path.join(R, "topologies.tar.gz")) != tar_members(f"{tmp}/topologies.tar.gz"):
            bad.append("topologies.tar.gz members")
        return run, len(a), bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(check, a.runs))
    for run, n, bad in results:
        print(f"{run}\t{n} h5 items\t{'identical' if not bad else 'DIFFERENT: ' + ', '.join(bad[:8])}")
    sys.exit(1 if any(bad for _, _, bad in results) else 0)


if __name__ == "__main__":
    main()
