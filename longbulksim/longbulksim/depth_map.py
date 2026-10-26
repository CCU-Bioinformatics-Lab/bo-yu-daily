"""Position-dependent read start density from a real normal sample (depth overdispersion).

Real ONT depth varies along the genome more than Poisson sampling: at HCC1395 SEQC2 sites the
variance/mean of depth is 1.3-1.9 in the 25x normal and 2.4-3.1 in the tumour, against 1.0 for
uniform read starts. The normal's excess is regional (neighbouring sites < 100 kb correlate
0.38) and carries over to the tumour (lab_report/2026-10-26_longbulksim_depth_map/). So the map
counts primary reads with MAPQ >= 20 that start in each fixed bin of a normal sample, scaled
to mean 1 over autosomal bins; mappability and other technical effects are inside the counts.
The rest of the tumour excess follows CN calls, not sequencing, and is not modelled here.

The map is an .npz with bin_size and one weight array per chrom (<chrom> keys).

Build: python3 -m longbulksim.depth_map NORMAL.cram REF.fa OUT.npz [--bin 10000] [--mapq 20]
"""
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]


def _count(args):
    cram, ref, chrom, length, bin_size, mapq = args
    n = np.zeros(length // bin_size + 1, np.int64)
    cmd = ["samtools", "view", "-T", ref, "-F", "0x904", "-q", str(mapq), cram, chrom]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as p:
        for line in p.stdout:
            n[(int(line.split("\t", 4)[3]) - 1) // bin_size] += 1
    if p.returncode:
        raise RuntimeError(f"samtools view failed on {chrom}")
    return chrom, n


def build(cram, ref, out, bin_size=10_000, mapq=20, threads=len(CHROMS)):
    lengths = {ln.split("\t")[0]: int(ln.split("\t")[1]) for ln in open(f"{ref}.fai")}
    jobs = [(str(cram), str(ref), c, lengths[c], bin_size, mapq) for c in CHROMS if c in lengths]
    with ThreadPoolExecutor(threads) as ex:
        counts = dict(ex.map(_count, jobs))
    mean = np.mean(np.concatenate([v for c, v in counts.items() if c != "chrX"]))
    np.savez_compressed(out, bin_size=bin_size,
                        **{c: (v / mean).astype(np.float32) for c, v in counts.items()})


def load(path):
    with np.load(path) as z:
        return int(z["bin_size"]), {k: z[k].astype(float) for k in z.files if k != "bin_size"}


def weights(dmap, chrom, lo, hi):
    """Per-bin start weights and bin starts covering [lo, hi); unknown chroms are flat 1."""
    bin_size, w = dmap
    first, last = max(lo, 0) // bin_size, (max(hi, 1) - 1) // bin_size
    starts = np.arange(first, last + 1) * bin_size
    arr = w.get(chrom)
    if arr is None:
        return starts, np.ones(len(starts))
    idx = np.arange(first, last + 1)
    vals = np.where(idx < len(arr), arr[np.minimum(idx, len(arr) - 1)], 0.0)
    return starts, vals


def draw_starts(rng, dmap, chrom, lo, hi, n):
    """n read starts in [lo, hi) with density proportional to the map."""
    bin_size = dmap[0]
    starts, w = weights(dmap, chrom, lo, hi)
    seg_lo, seg_hi = np.maximum(starts, lo), np.minimum(starts + bin_size, hi)
    mass = w * (seg_hi - seg_lo)
    if n == 0 or mass.sum() == 0:  # e.g. a segment inside an N gap: no reads start there
        return np.zeros(0, np.int64)
    b = rng.choice(len(mass), size=n, p=mass / mass.sum())
    return seg_lo[b] + (rng.random(n) * (seg_hi[b] - seg_lo[b])).astype(np.int64)


def mean_weight(dmap, chrom, lo, hi):
    """Length-weighted mean start weight over [lo, hi)."""
    bin_size = dmap[0]
    starts, w = weights(dmap, chrom, lo, hi)
    span = np.minimum(starts + bin_size, hi) - np.maximum(starts, lo)
    return float((w * span).sum() / span.sum())


def main():
    ap = argparse.ArgumentParser(prog="longbulksim.depth_map")
    ap.add_argument("cram")
    ap.add_argument("ref")
    ap.add_argument("out")
    ap.add_argument("--bin", type=int, default=10_000)
    ap.add_argument("--mapq", type=int, default=20)
    a = ap.parse_args()
    build(Path(a.cram), Path(a.ref), Path(a.out), a.bin, a.mapq)


if __name__ == "__main__":
    main()
