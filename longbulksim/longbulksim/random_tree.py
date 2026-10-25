"""Random tree specs drawn from TRACERx 421 single-region blueprints.

One spec = one real region tree (topology, region CCFs, purity, relative cluster sizes) plus
the allele-specific CN profile of the same tumour. Nothing is drawn from a parametric prior:

  tree      region subtree (clusters with region CCF > 0 and their ancestors)
  CCF       region CCF, projected onto the sum rule: an ancestor gets at least the sum of its
            children, then CCFs are capped at 1 from the root down; a clone whose CCF is within
            merge_gap of its parent's is merged into the parent (one bulk sample cannot tell
            them apart)
  purity    region ACF
  CN        per segment, the trunk state (A, B) becomes gains/losses on the root edge (A and B
            map to HP1 and HP2). A subclonal change (dA, dB) goes to a uniform non-trunk clone
            of the whole tumour tree; it is kept only if that clone is in this region, on the
            edge of the clone that absorbed it (the root edge if it merged into the trunk)
  SNVs      n_snv split across clones in proportion to the tumour's cluster sizes (>= 2 each);
            segment by bp; copy uniform over all copies present at that moment
Each edge holds its SNVs and CN steps in random order (on one segment and HP, gains before
losses), and each gain or loss picks a random copy. So multiplicity, CN timing and mutation
loss (including deletion of one of several copies) follow from the order instead of being set.
Only segments that receive SNVs are kept. Physical segment lengths keep the SNV density at
`density_per_mb`, so read co-occurrence matches the density, not the segment size.

Usage: python3 -m longbulksim.random_tree OUT_DIR [--count 1] [--seed 1] [--n-snv 200]
                                                  [--depth 50]
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .model import DATA_DIR, HPS, parse_spec, replay, roles_in

TREES = DATA_DIR / "tracerx421_region_trees.tsv"
CN_SEGMENTS = DATA_DIR / "tracerx421_cn_segments.tsv"


def load_blueprints():
    trees = pd.read_csv(TREES, sep="\t", dtype={"clone": str, "parent": str})
    cn = pd.read_csv(CN_SEGMENTS, sep="\t", dtype={"chr": str})
    regions = [(k, g) for k, g in trees.groupby(["tumour_id", "region"])]
    return regions, {t: g.reset_index(drop=True) for t, g in cn.groupby("tumour_id")}


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


def cn_steps(d):
    """Gains/losses that change an HP by d copies."""
    return ["gain"] * d if d > 0 else ["loss"] * -d


def draw_spec(rng, regions, cn_profiles, n_snv=200, depth=50, merge_gap=0.05,
              density_per_mb=12.9, phased_fraction=0.859):
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
    order = [root]
    for c in order:
        order += [k for k, p in parent.items() if p == c]

    cn = cn_profiles[tumour]
    n_by_clone = allocate(rng, {c: max(size[c], 1) for c in parent}, n_snv)
    items = {c: [] for c in parent}  # clone -> [(sort key, item)]
    k = 0
    for c, n in n_by_clone.items():
        for s in rng.choice(len(cn), size=n, p=cn.bp / cn.bp.sum()):
            k += 1
            items[c].append((rng.random(), ("snv", f"s{k}", f"G{s}")))

    bp_root = next(c for c, p in bp_parent.items() if p is None)
    bp_sub = [c for c in bp_parent if c != bp_root]
    n_tumour_sub = max(int(g.tumour_n_clones.iloc[0]) - 1, 1)
    used = {seg for its in items.values() for _, (_, _, seg) in its}
    n_sub_kept = n_sub_absent = 0
    for s in sorted(used, key=lambda x: int(x[1:])):
        row = cn.iloc[int(s[1:])]
        steps = {root: [(h, "loss") if t == 0 else None for h, t in
                        zip(HPS, (row.trunk_a, row.trunk_b))]}
        steps[root] = [st for st in steps[root] if st] + [
            (h, "gain") for h, t in zip(HPS, (row.trunk_a, row.trunk_b)) for _ in range(t - 1)]
        if row.d_a or row.d_b:
            i = rng.integers(n_tumour_sub)
            if i < len(bp_sub):
                n_sub_kept += 1
                clone = merged[bp_sub[i]]
                steps.setdefault(clone, [])
                steps[clone] += [(h, op) for h, d in zip(HPS, (row.d_a, row.d_b))
                                 for op in cn_steps(int(d))]
            else:
                n_sub_absent += 1
        for clone, st in steps.items():
            for h in HPS:
                ops = sorted(op for hh, op in st if hh == h)  # "gain" < "loss"
                keys = np.sort(rng.random(len(ops)))
                items[clone] += [(key, (op, h, s)) for key, op in zip(keys, ops)]

    copies = {}  # clone -> {(segment, HP): copy count}
    edges, invalid = {}, 0
    for c in order:
        cps = dict(copies[parent[c]]) if parent[c] else {}
        out = []
        for _, it in sorted(items[c]):
            if it[0] == "snv":
                _, sid, seg = it
                n = [cps.get((seg, h), 1) for h in HPS]
                if sum(n) == 0:
                    continue
                j = int(rng.integers(sum(n)))
                h = HPS[0] if j < n[0] else HPS[1]
                out.append({"snv": sid, "hp": h, "segment": seg,
                            "copy": j if j < n[0] else j - n[0]})
            else:
                op, h, seg = it
                n = cps.get((seg, h), 1)
                if n == 0:
                    invalid += 1
                    continue
                out.append({op: seg, "hp": h, "copy": int(rng.integers(n))})
                cps[(seg, h)] = n + (1 if op == "gain" else -1)
        copies[c] = cps
        if out:
            edges[names[c]] = out

    raw = {
        "name": f"tracerx_{region}",
        "source": {"tumour_id": tumour, "region": region, "blueprint_clones": len(bp_parent),
                   "merged_clones": len(bp_parent) - len(parent),
                   "subclonal_cn_kept": n_sub_kept, "subclonal_cn_not_in_region": n_sub_absent,
                   "cn_steps_invalid": invalid},
        "purity": float(g.purity.iloc[0]), "depth": depth, "phased_fraction": phased_fraction,
        "clones": {names[c]: {"parent": names[parent[c]] if parent[c] else None,
                              "fraction": fraction[c] / sum(fraction.values())} for c in order},
        "segments": {s: {"chrom": "chr1", "start": 0, "length": 1} for s in used},
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
    regions, cn_profiles = load_blueprints()
    rng = np.random.default_rng(a.seed)
    for i in range(a.count):
        spec = draw_spec(rng, regions, cn_profiles, n_snv=a.n_snv, depth=a.depth)
        (out / f"spec_{i:04d}.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))


if __name__ == "__main__":
    main()
