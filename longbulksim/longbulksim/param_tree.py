"""Parametric tree specs (CONIPHER-style inputs), with TRACERx 421 single-region medians as defaults.

Unlike random_tree.py (one real region tree per spec), the user sets the summary parameters and
the tree is drawn from them:

  tree      n_clones; shape linear, branched (random recursive tree that is not a chain) or
            random (linear with probability p_linear)
  CCF       exclusive cell fractions ~ Dirichlet(ccf_alpha); redrawn until every subclone has
            CCF >= min_ccf and sits >= min_gap below its parent (one bulk sample cannot split
            closer clones)
  SNVs      round(prop_truncal * n_snv) on the trunk, the rest split over subclones (>= 2 each);
            segment by bp; copy uniform over all copies present at that moment
  segments  n_segments, lengths resampled from TRACERx segment lengths
  CN        per segment a trunk category relative to the baseline (1:1, or 2:2 with WGD):
            gain / loss / loh with the given bp shares, neutral otherwise. The exact state
            (e.g. 3:1) is resampled from TRACERx segments of that category and ploidy group,
            HP orientation random. With probability prop_subclonal_cn a segment also gets one
            subclonal change (resampled from TRACERx (dA, dB)) on a uniform subclone.
Event order on each edge, multiplicity, CN timing and mutation loss then follow
random_tree.build_edges, so they are not set directly.

Defaults are TRACERx 421 single-region medians after the same merge (min_gap 0.05): 3 clones,
63% linear for >= 3 clones, subclone CCF median 0.45 (ccf_alpha 0.5 gives 0.44), 450 SNVs,
91% truncal, purity 0.41, 129 segments, WGD (57% of tumours have ploidy >= 3), gain/loss/loh
bp shares 0.083/0.328/0.267 with WGD and 0.124/0/0.274 without, subclonal CN 0.096 of bp in a
region. depth 50 is the PCAWG median (TRACERx is high-depth WES).
"""
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .model import HPS
from .random_tree import CN_SEGMENTS, add_cn_items, allocate, build_edges, cn_steps, drop_unobservable

CATEGORIES = ("gain", "loss", "loh")
CN_DEFAULTS = {True: {"gain": 0.083, "loss": 0.328, "loh": 0.267},
               False: {"gain": 0.124, "loss": 0.0, "loh": 0.274}}


@dataclass(frozen=True)
class Params:
    n_clones: int = 3
    tree_shape: str = "random"     # random | linear | branched
    p_linear: float = 0.63
    ccf_alpha: float = 0.5
    min_ccf: float = 0.05
    min_gap: float = 0.05
    n_snv: int = 450
    prop_truncal: float = 0.91
    n_segments: int = 129
    wgd: bool = True
    prop_gain: float | None = None   # None: TRACERx median for the WGD group
    prop_loss: float | None = None
    prop_loh: float | None = None
    prop_subclonal_cn: float = 0.096
    purity: float = 0.41
    depth: float = 50
    density_per_mb: float = 12.9
    phased_fraction: float = 0.859

    def cn_shares(self):
        d = CN_DEFAULTS[self.wgd]
        s = {k: d[k] if getattr(self, f"prop_{k}") is None else getattr(self, f"prop_{k}")
             for k in CATEGORIES}
        if sum(s.values()) > 1:
            raise ValueError(f"gain + loss + loh shares exceed 1: {s}")
        return s


def categorize(a, b, base):
    """Trunk CN category of state (a, b) relative to `base` copies per HP."""
    if max(a, b) == 0:
        return "homdel"
    if min(a, b) == 0:
        return "loh"
    if a < base or b < base:
        return "loss"
    if a > base or b > base:
        return "gain"
    return "neutral"


def load_pools(path=CN_SEGMENTS):
    """TRACERx trunk states by (WGD, category) and subclonal changes by WGD, with segment bp."""
    cn = pd.read_csv(path, sep="\t", dtype={"chr": str})
    ploidy = ((cn.trunk_a + cn.trunk_b) * cn.bp).groupby(cn.tumour_id).sum() / cn.bp.groupby(cn.tumour_id).sum()
    wgd = cn.tumour_id.map(ploidy >= 3)
    states, deltas = {}, {}
    for w in (True, False):
        g = cn[wgd == w]
        base = 2 if w else 1
        cat = [categorize(a, b, base) for a, b in zip(g.trunk_a, g.trunk_b)]
        for c in CATEGORIES:
            states[(w, c)] = g.loc[[x == c for x in cat], ["trunk_a", "trunk_b"]].to_numpy()
        sub = g[(g.d_a != 0) | (g.d_b != 0)]
        deltas[w] = sub[["d_a", "d_b"]].to_numpy()
    return states, deltas, cn.bp.to_numpy()


def draw_tree(rng, p):
    """Parent map C1..Cn (C1 = root) of the requested shape."""
    n = p.n_clones
    linear = {f"C{i + 1}": (f"C{i}" if i else None) for i in range(n)}
    shape = p.tree_shape
    if shape == "random":
        shape = "linear" if n < 3 or rng.random() < p.p_linear else "branched"
    if shape == "linear":
        return linear
    if shape != "branched":
        raise ValueError(f"tree_shape must be random, linear or branched: {shape}")
    if n < 3:
        raise ValueError("a branched tree needs >= 3 clones")
    while True:
        parent = {"C1": None, **{f"C{i + 1}": f"C{rng.integers(i) + 1}" for i in range(1, n)}}
        kids = [p_ for p_ in parent.values() if p_]
        if len(kids) != len(set(kids)):
            return parent


def draw_fractions(rng, parent, p):
    clones = list(parent)
    for _ in range(100_000):
        f = dict(zip(clones, rng.dirichlet(np.full(len(clones), p.ccf_alpha))))
        ccf = {}
        for c in reversed(clones):  # children have larger indices than parents
            ccf[c] = f[c] + sum(ccf[k] for k, q in parent.items() if q == c)
        if all(ccf[c] >= p.min_ccf and ccf[parent[c]] - ccf[c] >= p.min_gap
               for c in clones if parent[c]):
            return f, ccf
    raise ValueError(f"no CCFs found for {len(clones)} clones with min_ccf {p.min_ccf} and "
                     f"min_gap {p.min_gap}")


def draw_spec(rng, pools, p=Params(), name="param"):
    states, deltas, seg_bp = pools
    parent = draw_tree(rng, p)
    order = list(parent)
    names = {c: c for c in order}
    fraction, ccf = draw_fractions(rng, parent, p)
    subs = order[1:]

    n_trunk = round(p.prop_truncal * p.n_snv) if subs else p.n_snv
    n_by_clone = {order[0]: n_trunk}
    if subs:
        n_by_clone.update(allocate(rng, {c: 1 for c in subs}, p.n_snv - n_trunk))
    bp = rng.choice(seg_bp, size=p.n_segments)
    items = {c: [] for c in order}
    k = 0
    for c, n in n_by_clone.items():
        for s in rng.choice(p.n_segments, size=n, p=bp / bp.sum()):
            k += 1
            items[c].append((rng.random(), ("snv", f"s{k}", f"G{s}")))

    shares = p.cn_shares()
    cats = ("neutral",) + CATEGORIES
    probs = [1 - sum(shares.values())] + [shares[c] for c in CATEGORIES]
    base = 2 if p.wgd else 1
    used = sorted({seg for its in items.values() for _, (_, _, seg) in its}, key=lambda x: int(x[1:]))
    n_sub_cn = 0
    for s in used:
        cat = cats[rng.choice(len(cats), p=probs)]
        if cat == "neutral":
            a, b = base, base
        else:
            pool = states[(p.wgd, cat)]
            a, b = (int(x) for x in pool[rng.integers(len(pool))])
        if rng.random() < 0.5:
            a, b = b, a
        trunk = [(h, "loss") for h, t in zip(HPS, (a, b)) if t == 0]
        trunk += [(h, "gain") for h, t in zip(HPS, (a, b)) for _ in range(t - 1)]
        steps = {order[0]: trunk}
        if subs and rng.random() < p.prop_subclonal_cn:
            da, db = (int(x) for x in deltas[p.wgd][rng.integers(len(deltas[p.wgd]))])
            if rng.random() < 0.5:
                da, db = db, da
            clone = subs[rng.integers(len(subs))]
            steps[clone] = [(h, op) for h, d in zip(HPS, (da, db)) for op in cn_steps(d)]
            n_sub_cn += 1
        add_cn_items(rng, items, steps, s)
    edges, invalid = build_edges(rng, parent, order, names, items)

    raw = {
        "name": name,
        "source": {"generator": "param_tree", "params": asdict(p),
                   "ccf": {c: round(float(v), 4) for c, v in ccf.items()},
                   "subclonal_cn_segments": n_sub_cn, "cn_steps_invalid": invalid},
        "purity": p.purity, "depth": p.depth, "phased_fraction": p.phased_fraction,
        "clones": {c: {"parent": parent[c], "fraction": float(fraction[c])} for c in order},
        "segments": {s: {"chrom": "chr1", "start": 0, "length": 1} for s in used},
        "edges": edges,
    }
    return drop_unobservable(raw, p.density_per_mb)
