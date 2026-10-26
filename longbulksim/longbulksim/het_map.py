"""Germline phased het SNP map: decides which reads get an HP tag.

longphase-s germline haplotag (src/haplotag/HaplotagStrategy.cpp, judgeReadHap) leaves a read
untagged when it covers no phased het SNP, or when the het SNPs it covers lie in more than one
phase set (PS). It also needs >= 60% of those alleles to agree; reads here carry the true
haplotype at every het SNP, so that rule never fires. The tag rate then follows the real het
SNP density and PS block layout, with no free parameter.

The map is an .npz with <chrom>_pos (sorted, 1-based) and <chrom>_ps (block index) per chrom.
PS blocks are contiguous position intervals, so a read lies in one block iff its first and last
covered het SNP share a block.

Build: python3 -m longbulksim.het_map PHASED.vcf.gz OUT.npz
"""
import gzip
import sys
from pathlib import Path

import numpy as np

EMPTY = (np.zeros(0, np.int64), np.zeros(0, np.int64))


def build(vcf, out):
    pos, ps = {}, {}
    with gzip.open(vcf, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.split("\t", 10)
            fmt, val = f[8].split(":"), f[9].rstrip("\n").split(":")
            if "|" not in val[fmt.index("GT")]:
                continue
            pos.setdefault(f[0], []).append(int(f[1]))
            ps.setdefault(f[0], []).append(int(val[fmt.index("PS")]))
    arr = {}
    for c in pos:
        p, s = np.array(pos[c]), np.array(ps[c])
        o = np.argsort(p, kind="stable")
        p, s = p[o], s[o]
        if (s[1:] != s[:-1]).sum() + 1 != len(set(s.tolist())):
            raise ValueError(f"{c}: PS blocks interleave; the first/last het rule needs intervals")
        _, block = np.unique(s, return_inverse=True)
        arr[f"{c}_pos"] = p.astype(np.int32)
        arr[f"{c}_ps"] = block.astype(np.int32)
    np.savez_compressed(out, **arr)


def load(path):
    """chrom -> (positions, block index); unknown chroms have no het SNPs."""
    with np.load(path) as z:
        chroms = {k.rsplit("_", 1)[0] for k in z.files}
        return {c: (z[f"{c}_pos"].astype(np.int64), z[f"{c}_ps"].astype(np.int64))
                for c in chroms}


def tagged(het, chrom, start, end):
    """Reads [start, end) that longphase-s germline haplotag would tag."""
    pos, ps = het.get(chrom, EMPTY)
    lo = np.searchsorted(pos, start, side="left")
    hi = np.searchsorted(pos, end, side="left")
    ok = hi > lo
    out = np.zeros(len(start), bool)
    out[ok] = ps[lo[ok]] == ps[hi[ok] - 1]
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(Path(sys.argv[1]), Path(sys.argv[2]))
