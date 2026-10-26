"""Molecule-level read sampling.

Each read is one DNA molecule: one lineage (normal or a clone), one HP and one copy of that HP.
Every SNV the read covers is observed from that same molecule, so read co-occurrence of SNVs
follows the tree. A read's lineage, HP and copy are drawn with probability proportional to the
lineage's bulk cell fraction (each copy is one molecule template). Read starts are uniform and
read spans come from a measured ONT span distribution, so the number of reads that span two
SNVs depends on their distance as in real data. With a het map, a read is tagged by the
longphase-s rule (het_map.py); otherwise each read is tagged with probability phased_fraction.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import het_map
from .model import HPS


@dataclass(frozen=True)
class Mutation:
    id: str
    role: str
    segment: str
    pos: int


@dataclass(frozen=True)
class Molecule:
    lineage: str
    hp: str
    copy: int
    roles: frozenset[str]


@dataclass(frozen=True)
class Reads:
    """Reads of one segment, sorted by start."""
    molecules: tuple[Molecule, ...]
    start: np.ndarray
    end: np.ndarray
    mol: np.ndarray     # index into molecules
    tagged: np.ndarray  # read carries an HP tag
    obs_hp: np.ndarray  # HP the tag says (str); differs from the molecule's HP after a mistag
                        # or an odd number of phase switches before the read midpoint
    switches: np.ndarray  # phase switch positions in the segment, ascending
    max_span: int

    def covering(self, pos):
        """Indices of reads that cover pos, ascending."""
        lo = np.searchsorted(self.start, pos - self.max_span, side="right")
        hi = np.searchsorted(self.start, pos, side="right")
        idx = np.arange(lo, hi)
        return idx[self.end[idx] > pos]

    def carries(self, role):
        return np.array([role in m.roles for m in self.molecules])


def load_read_span(path):
    rows = [ln.split("\t") for ln in Path(path).read_text().splitlines() if ln[:1].isdigit()]
    q, span = np.array(rows, dtype=float).T
    return q, span


def place_mutations(rng, spec):
    """Distinct uniform positions per segment, shared by all roles in that segment."""
    by_seg = {}
    for role in spec.roles.values():
        by_seg.setdefault(role.segment, []).append(role)
    out = []
    for seg_id, roles in by_seg.items():
        seg = spec.segments[seg_id]
        n = sum(r.count for r in roles)
        pos = seg.start + rng.choice(seg.length, size=n, replace=False)
        k = 0
        for r in roles:
            for i in range(r.count):
                out.append(Mutation(f"{r.id}_{i:02d}", r.id, seg_id, int(pos[k])))
                k += 1
    return out


def sample_segment(rng, spec, genomes, seg_id, span_q, het=None):
    q, span = span_q
    mean_span = np.trapezoid(span, q)
    max_span = int(span[-1])
    seg = spec.segments[seg_id]
    mols, w = [], []
    for lineage, cw in spec.cell_weight().items():
        for hp in HPS:
            for k, roles in enumerate(genomes[lineage][seg_id][hp]):
                mols.append(Molecule(lineage, hp, k, roles))
                w.append(cw)
    w = np.asarray(w)
    # depth is the mean coverage of a diploid normal genome, so one copy gives depth/2
    lam = spec.depth / 2 * w.sum() * (seg.length + max_span) / mean_span
    n = rng.poisson(lam)
    start = rng.integers(seg.start - max_span, seg.end, size=n)
    order = np.argsort(start, kind="stable")
    start = start[order]
    end = start + np.interp(rng.random(n), q, span).astype(np.int64)
    mol = rng.choice(len(mols), size=n, p=w / w.sum())
    if het is None:
        tagged = rng.random(n) < spec.phased_fraction
    else:
        tagged = het_map.tagged(het, seg.chrom, start, end)
    # errors draw no random numbers when their rate is 0, so v0.1 seeds give the same reads
    flip = np.zeros(n, bool)
    if spec.mistag_rate > 0:
        flip ^= rng.random(n) < spec.mistag_rate
    switches = np.zeros(0, np.int64)
    if spec.switch_rate_per_mb > 0:
        k = rng.poisson(spec.switch_rate_per_mb * seg.length / 1e6)
        switches = np.sort(rng.integers(seg.start, seg.end, size=k))
        flip ^= np.searchsorted(switches, (start + end) // 2, side="right") % 2 == 1
    true_hp = np.array([HPS.index(m.hp) for m in mols], dtype=np.int64)[mol]
    obs_hp = np.array(HPS)[true_hp ^ flip]
    keep = end > seg.start
    return Reads(tuple(mols), start[keep], end[keep], mol[keep], tagged[keep], obs_hp[keep],
                 switches, max_span)
