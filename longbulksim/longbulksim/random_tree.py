"""Random tree specs drawn from TRACERx 421 single-region blueprints.

One spec = one real region tree (topology, region CCFs, purity, relative cluster sizes) plus
the CN events of the same tumour. Nothing about the tree is drawn from a parametric prior:

  tree      region subtree (clusters with region CCF > 0 and their ancestors)
  CCF       region CCF, projected onto the sum rule: an ancestor gets at least the sum of its
            children, then CCFs are capped at 1 from the root down; a clone whose CCF is within
            merge_gap of its parent's is merged into the parent (one bulk sample cannot tell
            them apart)
  purity    region ACF
  SNVs      n_snv split across clones in proportion to the tumour's cluster sizes (>= 2 each);
            segment by genome fraction, HP uniform (the other HP if this lineage lost it)
  CN        the tumour's own events. A clonal event goes on the root edge. A subclonal event
            (it differs between regions) goes to a uniform non-trunk clone of the whole tumour
            tree; it is kept only if that clone is in this region, on the edge of the clone
            that absorbed it (the root edge if it merged into the trunk). Events sit in random
            order with that edge's SNVs, so CN timing and mutation loss follow from the order
            instead of being set
Each segment carries at most one event. Physical segment lengths keep the SNV density at
`density_per_mb`, so read co-occurrence matches the density, not the event size.

Usage: python3 -m longbulksim.random_tree OUT_DIR [--count 1] [--seed 1] [--n-snv 200]
                                                  [--depth 50]
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .model import DATA_DIR, HPS, parse_spec, replay, roles_in

GENOME_BP = 2.88e9
TREES = DATA_DIR / "tracerx421_region_trees.tsv"
EVENTS = DATA_DIR / "tracerx421_cn_events.tsv"


def load_blueprints():
    trees = pd.read_csv(TREES, sep="\t", dtype={"clone": str, "parent": str})
    events = pd.read_csv(EVENTS, sep="\t")
    regions = [(k, g) for k, g in trees.groupby(["tumour_id", "region"])]
    return regions, {t: g for t, g in events.groupby("tumour_id")}


def project_ccf(parent, ccf, merge_gap):
    """Sum-rule-consistent CCFs, with near-identical parent/child pairs merged.

    Returns (parent, ccf, merged_into) over the kept clones; merged_into maps every
    blueprint clone to the kept clone that absorbed it.
    """
    parent, ccf = dict(parent), {c: min(v, 1.0) for c, v in ccf.items()}
    root = next(c for c, p in parent.items() if p is None)
    kids = lambda n: [c for c, p in parent.items() if p == n]

    def lift(n):
        ccf[n] = max(ccf[n], sum(lift(k) for k in kids(n)))
        return ccf[n]

    def cap(n, top):
        ccf[n] = min(ccf[n], top)
        s = sum(ccf[k] for k in kids(n))
        for k in kids(n):
            cap(k, ccf[k] * (ccf[n] / s if s > ccf[n] else 1))

    lift(root)
    ccf[root] = 1.0
    cap(root, 1.0)
    merged = {c: c for c in parent}
    changed = True
    while changed:
        changed = False
        for c, p in list(parent.items()):
            if p is not None and ccf[p] - ccf[c] < merge_gap:
                for k in kids(c):
                    parent[k] = p
                del parent[c], ccf[c]
                merged = {b: (p if m == c else m) for b, m in merged.items()}
                changed = True
                break
    return parent, ccf, merged


def allocate(rng, weights, n, minimum=2):
    """Integer counts >= minimum that sum to n, proportional to weights."""
    keys = list(weights)
    base = np.full(len(keys), minimum)
    w = np.asarray([weights[k] for k in keys], float)
    rest = rng.multinomial(max(n - base.sum(), 0), w / w.sum())
    return dict(zip(keys, (base + rest).tolist()))


def draw_spec(rng, regions, events, n_snv=200, depth=50, merge_gap=0.05,
              density_per_mb=12.9, max_cn_fraction=0.9, phased_fraction=0.859):
    (tumour, region), g = regions[rng.integers(len(regions))]
    bp_parent = {r.clone: (None if r.parent == "root" else r.parent) for r in g.itertuples()}
    parent, ccf, merged = project_ccf(bp_parent, dict(zip(g.clone, g.ccf)), merge_gap)
    size = {c: 0 for c in parent}
    for r in g.itertuples():
        size[merged[r.clone]] += r.n_mut
    names = {c: f"C{i + 1}" for i, c in enumerate(sorted(parent, key=lambda c: -ccf[c]))}
    root = next(c for c, p in parent.items() if p is None)
    fraction = {c: max(ccf[c] - sum(ccf[k] for k, p in parent.items() if p == c), 0.0)
                for c in parent}

    ev = events.get(tumour, pd.DataFrame(columns=["kind", "bp"]))
    ev = ev.iloc[rng.permutation(len(ev))]
    bp_root = next(c for c, p in bp_parent.items() if p is None)
    bp_sub = [c for c in bp_parent if c != bp_root]
    n_tumour_sub = int(g.tumour_n_clones.iloc[0]) - 1
    cn, used, dropped, absent = [], 0.0, 0, 0
    for e in ev.itertuples():
        if e.kind == "clonal_cnloh":
            clone = root
        else:
            i = rng.integers(max(n_tumour_sub, 1))
            if i >= len(bp_sub):
                absent += 1
                continue
            clone = merged[bp_sub[i]]
        f = e.bp / GENOME_BP
        if used + f > max_cn_fraction:
            dropped += 1
            continue
        used += f
        cn.append((e.kind.split("_")[1], clone, f, HPS[rng.integers(2)]))

    n_by_clone = allocate(rng, {c: max(size[c], 1) for c in parent}, n_snv)
    seg_frac = np.array([1 - used] + [f for _, _, f, _ in cn])
    items = {c: [] for c in parent}  # clone -> [(sort key, item)]
    k = 0
    for c, n in n_by_clone.items():
        for s in rng.choice(len(seg_frac), size=n, p=seg_frac / seg_frac.sum()):
            k += 1
            items[c].append((rng.random(), ("snv", f"s{k}", int(s))))
    for i, (kind, clone, _, hp) in enumerate(cn, start=1):
        items[clone].append((rng.random(), (kind, hp, i)))

    order = [root]
    for c in order:
        order += [k for k, p in parent.items() if p == c]
    gone = {root: set()}  # clone -> {(segment, HP)} no longer present
    edges = {}
    for c in order:
        lost = set(gone[parent[c]]) if parent[c] else set()
        out = []
        for _, it in sorted(items[c]):
            if it[0] == "snv":
                seg = f"G{it[2]}"
                hp = HPS[rng.integers(2)]
                if (seg, hp) in lost:
                    hp = HPS[1 - HPS.index(hp)]
                out.append({"snv": it[1], "hp": hp, "segment": seg})
            else:
                kind, hp, s = it
                seg = f"G{s}"
                if kind == "gain":
                    out.append({"gain": seg, "hp": hp})
                elif kind == "loss":
                    out.append({"loss": seg, "hp": hp})
                    lost.add((seg, hp))
                else:
                    out.append({"cnloh": seg, "keep": hp})
                    lost.add((seg, HPS[1 - HPS.index(hp)]))
        gone[c] = lost
        if out:
            edges[names[c]] = out

    raw = {
        "name": f"tracerx_{region}",
        "source": {"tumour_id": tumour, "region": region, "blueprint_clones": len(bp_parent),
                   "merged_clones": len(bp_parent) - len(parent), "cn_events_used": len(cn),
                   "cn_events_not_in_region": absent, "cn_events_dropped": dropped, "cn_genome_fraction": round(used, 4)},
        "purity": float(g.purity.iloc[0]), "depth": depth, "phased_fraction": phased_fraction,
        "clones": {names[c]: {"parent": names[parent[c]] if parent[c] else None,
                              "fraction": fraction[c] / sum(fraction.values())} for c in order},
        "segments": {f"G{s}": {"chrom": "chr1", "start": 0, "length": 1}
                     for s in range(len(seg_frac))},
        "edges": edges,
    }
    return drop_unobservable(raw, density_per_mb)


def drop_unobservable(raw, density_per_mb):
    """Remove SNVs that no clone carries (lost on the edge where they arose, e.g. a truncal SNV
    before a clonal cnLOH of its HP): real data never contains them. Then size the segments
    that still hold SNVs and drop CN events on empty segments."""
    g = replay(parse_spec(raw))
    present = set().union(*(roles_in(g[c]) for c in raw["clones"]))
    snvs = [e for ev in raw["edges"].values() for e in ev if "snv" in e]
    n_seg = {}
    for e in snvs:
        if e["snv"] in present:
            n_seg[e["segment"]] = n_seg.get(e["segment"], 0) + 1
    keep = lambda e: (e["snv"] in present if "snv" in e else
                      next(e[k] for k in ("gain", "loss", "cnloh") if k in e) in n_seg)
    raw["edges"] = {c: [e for e in ev if keep(e)] for c, ev in raw["edges"].items()}
    raw["edges"] = {c: ev for c, ev in raw["edges"].items() if ev}
    raw["source"]["unobservable_snvs_dropped"] = len(snvs) - len(present)
    segments, offset = {}, {}
    for seg, n in n_seg.items():
        chrom = f"chr{len(segments) % 22 + 1}"
        length = int(np.ceil(n / density_per_mb * 1e6))
        start = offset.get(chrom, 1_000_000)
        offset[chrom] = start + length + 1_000_000
        segments[seg] = {"chrom": chrom, "start": start, "length": length}
    raw["segments"] = segments
    return raw


def main():
    ap = argparse.ArgumentParser(prog="longbulksim.random_tree")
    ap.add_argument("out_dir")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n-snv", type=int, default=200)
    ap.add_argument("--depth", type=float, default=50)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    regions, events = load_blueprints()
    rng = np.random.default_rng(a.seed)
    for i in range(a.count):
        spec = draw_spec(rng, regions, events, n_snv=a.n_snv, depth=a.depth)
        (out / f"spec_{i:04d}.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))


if __name__ == "__main__":
    main()
