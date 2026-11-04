#!/usr/bin/env python3
"""Posterior predictive check of longbulksim against real HCC1395 ONT t50_n00.

Simulate HCC1395 at the real SEQC2 SNV positions and ASCAT consensus CN: one clone, purity 1.
Then compute the same statistics as tools/hcc1395_hp_split.py on the real per-site table and
on each simulation, over the same SNV set and the same within-segment adjacent pairs.

Segments are runs of consecutive SNVs with the same ASCAT (total, minor). Major HP is random
per segment. SNV placement models:
  m1   multiplicity 1 on a uniform copy (all SNVs after the CN change)
  mhat multiplicity round(VAF_real * total) clipped to [1, major]; uses real VAF, so VAF
       statistics under mhat are circular and only its pair statistics are a check
Error settings: e0 none; e_sb switch 1/Mb + base 0.004 (no mistag, so split-HP is not
fitted); e_cal e_sb + mistag 0.025 (mistag was calibrated from the real split rate).
--min-vaf drops sites whose real VAF is below it (SEQC2 calls absent from this ONT batch).
--het-map tags reads by the longphase-s rule on that phased het SNP map instead of a flat 0.859.
--depth-map draws read starts from a real normal's start density instead of uniformly.

Usage: python3 tools/longbulksim_ppc.py OUT_DIR [--seeds 3] [--min-vaf 0.05] [--het-map NPZ] [--depth-map NPZ]
"""
import argparse
import collections
import csv
import json
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "longbulksim"))
from longbulksim import depth_map, het_map  # noqa: E402
from longbulksim.model import DATA_DIR, HPS, NORMAL, Segment, Spec  # noqa: E402
from longbulksim.sample import load_read_span, sample_segment  # noqa: E402
from longbulksim.simulate import observe  # noqa: E402

REAL = ROOT / "lab_report/2026-10-25_hcc1395_hp_split/tables"
MIN_ALT, ASSIGN_FRAC, PAIR_MAX = 3, 0.9, 100_000
DIST_BINS = [(0, 1_000), (1_000, 5_000), (5_000, 20_000), (20_000, 50_000), (50_000, PAIR_MAX)]
ERRORS = {"e0": (0, 0, 0), "e_sb": (0, 1.0, 0.004), "e_cal": (0.025, 1.0, 0.004)}
COLS = ("alt_hp1", "alt_hp2", "alt_untagged", "ref_hp1", "ref_hp2", "ref_untagged")
EDGE = 100_000


def load_real(min_vaf=0.0):
    sites = []
    for r in csv.DictReader(open(REAL / "per_snv_hp.tsv"), delimiter="\t"):
        if r["ascat_total"] in ("None", "0"):
            continue
        sites.append({"chrom": r["chrom"], "pos": int(r["pos"]), "total": int(r["ascat_total"]),
                      "minor": int(r["ascat_minor"]), **{k: int(r[k]) for k in COLS}})
    dp = [sum(s[k] for k in COLS) for s in sites]
    return [s for s, d in zip(sites, dp)
            if d and (s["alt_hp1"] + s["alt_hp2"] + s["alt_untagged"]) / d >= min_vaf]


def build_segments(sites):
    """Assign each site a segment id; return segment table."""
    by_chr = collections.defaultdict(list)
    for s in sites:
        by_chr[s["chrom"]].append(s)
    segs = {}
    for chrom, ss in by_chr.items():
        ss.sort(key=lambda s: s["pos"])
        runs = [[ss[0]]]
        for s in ss[1:]:
            prev = runs[-1][-1]
            if (s["total"], s["minor"]) == (prev["total"], prev["minor"]):
                runs[-1].append(s)
            else:
                runs.append([s])
        bounds = [max(1, runs[0][0]["pos"] - EDGE)]
        bounds += [(a[-1]["pos"] + b[0]["pos"]) // 2 + 1 for a, b in zip(runs, runs[1:])]
        bounds.append(runs[-1][-1]["pos"] + EDGE)
        for i, run in enumerate(runs):
            sid = f"{chrom}_{i}"
            segs[sid] = Segment(sid, chrom, bounds[i], bounds[i + 1] - bounds[i])
            for s in run:
                s["seg"] = sid
    return segs


def real_pairs(sites):
    """Within-segment pairs that are adjacent among all SEQC2 sites (as in the real table)."""
    seg_of = {(s["chrom"], s["pos"]): s["seg"] for s in sites}
    out = []
    for r in csv.DictReader(open(REAL / "snv_pairs.tsv"), delimiter="\t"):
        a, b = (r["chrom"], int(r["pos1"])), (r["chrom"], int(r["pos2"]))
        if a in seg_of and seg_of[a] == seg_of.get(b):
            out.append({"a": a, "b": b, "distance": int(r["distance"]),
                        "span": int(r["spanning_reads"]), "both": int(r["reads_both_alt"]),
                        "one": int(r["reads_one_alt"])})
    return out


def build_genome(rng, sites, segs, model):
    """One tumour clone: segment -> HP -> copies (sets of site keys)."""
    major_hp = {sid: HPS[rng.integers(2)] for sid in segs}
    state = {s["seg"]: (s["total"], s["minor"]) for s in sites}
    copies = {}
    for sid, (total, minor) in state.items():
        mh = major_hp[sid]
        n = {mh: total - minor, HPS[1 - HPS.index(mh)]: minor}
        copies[sid] = {h: [set() for _ in range(n[h])] for h in HPS}
    truth_hp = {}
    for s in sites:
        cps = copies[s["seg"]]
        major = s["total"] - s["minor"]
        if model == "m1":
            m = 1
        else:
            dp = sum(s[k] for k in COLS)
            vaf = (s["alt_hp1"] + s["alt_hp2"] + s["alt_untagged"]) / dp if dp else 0
            m = int(min(max(round(vaf * s["total"]), 1), major))
        hps = [h for h in HPS if len(cps[h]) >= m]
        w = np.array([len(cps[h]) for h in hps], float)
        h = hps[rng.choice(len(hps), p=w / w.sum())]
        for k in rng.choice(len(cps[h]), size=m, replace=False):
            cps[h][k].add((s["chrom"], s["pos"]))
        truth_hp[(s["chrom"], s["pos"])] = h
    tumour = {sid: {h: tuple(frozenset(c) for c in cps[h]) for h in HPS}
              for sid, cps in copies.items()}
    normal = {sid: {h: (frozenset(),) for h in HPS} for sid in segs}
    return {NORMAL: normal, "C1": tumour}


def simulate(seed, model, err, sites, segs, pairs, depth, het=None, dmap=None):
    rng = np.random.default_rng(seed)
    mistag, switch, base = ERRORS[err]
    spec = Spec(f"hcc1395_{model}_{err}", 1.0, depth, 0.859,
                DATA_DIR / "hcc1395_ont_t50_n00_read_span.tsv", {"C1": None}, {"C1": 1.0},
                segs, {"C1": ()}, mistag, switch, base)
    genomes = build_genome(rng, sites, segs, model)
    span_q = load_read_span(spec.read_span)
    reads = {sid: sample_segment(rng, spec, genomes, sid, span_q, het, dmap) for sid in segs}
    obs, out = {}, []
    for s in sites:
        r = reads[s["seg"]]
        key = (s["chrom"], s["pos"])
        idx, alt = observe(r, s["pos"], key, rng, base)
        obs[key] = (idx, alt)
        tag, hp = r.tagged[idx], r.obs_hp[idx]
        c = {"alt_untagged": int((alt & ~tag).sum()), "ref_untagged": int((~alt & ~tag).sum())}
        for h in HPS:
            sel = tag & (hp == h)
            c[f"alt_{h.lower()}"] = int((alt & sel).sum())
            c[f"ref_{h.lower()}"] = int((~alt & sel).sum())
        out.append({**s, **c})
    sim_pairs = []
    for p in pairs:
        (ia, xa), (ib, xb) = obs[p["a"]], obs[p["b"]]
        _, ka, kb = np.intersect1d(ia, ib, assume_unique=True, return_indices=True)
        a, b = xa[ka], xb[kb]
        sim_pairs.append({**p, "span": len(ka), "both": int((a & b).sum()), "one": int((a ^ b).sum())})
    return out, sim_pairs


def q(v, p):
    return float(np.quantile(v, p)) if len(v) else float("nan")


def stats(sites, pairs):
    """Same definitions as tools/hcc1395_hp_split.py, plus depth and tag dispersion."""
    st = {}
    at_all = a_all = 0
    calls = collections.Counter()
    by_total = collections.defaultdict(list)
    tagfrac = []
    low = collections.defaultdict(list)
    minor = collections.defaultdict(list)
    vaf = collections.defaultdict(list)
    call_hp = {}
    for s in sites:
        a1, a2, a0 = s["alt_hp1"], s["alt_hp2"], s["alt_untagged"]
        r1, r2, r0 = s["ref_hp1"], s["ref_hp2"], s["ref_untagged"]
        at, dp = a1 + a2, a1 + a2 + a0 + r1 + r2 + r0
        at_all += at
        a_all += at + a0
        call = ("too_few" if at < MIN_ALT else
                "assigned" if max(a1, a2) / at >= ASSIGN_FRAC else "split")
        calls[call] += 1
        if call == "assigned" and s["minor"] > 0:
            call_hp[(s["chrom"], s["pos"])] = a1 > a2
        by_total[s["total"]].append(dp)
        if dp >= 10:
            tagfrac.append((a1 + a2 + r1 + r2) / dp)
            low[s["chrom"]].append((s["pos"], tagfrac[-1] < 0.5))
            vaf[(s["total"], s["minor"])].append((a1 + a2 + a0) / dp)
        d1, d2 = a1 + r1, a2 + r2
        if d1 + d2 >= 10:
            minor[(s["total"], s["minor"])].append(min(d1, d2) / (d1 + d2))
    n = len(sites)
    st["alt_tagged_pooled"] = at_all / a_all
    for k in ("assigned", "too_few", "split"):
        st[f"call_{k}"] = calls[k] / n
    alt3 = calls["assigned"] + calls["split"]
    st["split_among_alt3"] = calls["split"] / alt3
    for t in (2, 3, 4):
        v = by_total[t]
        st[f"depth_cn{t}_median"] = statistics.median(v)
        st[f"depth_cn{t}_vmr"] = statistics.pvariance(v) / statistics.mean(v)
        st[f"depth_cn{t}_q05"] = q(v, 0.05)
        st[f"depth_cn{t}_q95"] = q(v, 0.95)
    st["tagfrac_site_sd"] = float(np.std(tagfrac))
    st["tagfrac_site_q05"] = q(tagfrac, 0.05)
    st["tagfrac_site_lt_0.7"] = float(np.mean(np.array(tagfrac) < 0.7))
    st["tagfrac_site_lt_0.5"] = float(np.mean(np.array(tagfrac) < 0.5))
    nxt = [b for v in low.values() for (_, a), (_, b) in zip(sorted(v), sorted(v)[1:]) if a]
    st["tagfrac_next_low_given_low"] = float(np.mean(nxt)) if nxt else float("nan")
    for cn in ((2, 0), (2, 1), (3, 1), (4, 2), (3, 0), (5, 1)):
        st[f"minorfrac_{cn[0]}{cn[1]}_median"] = q(minor[cn], 0.5)
        st[f"minorfrac_{cn[0]}{cn[1]}_lt0.1"] = float(np.mean(np.array(minor[cn]) < 0.1))
        st[f"vaf_{cn[0]}{cn[1]}_median"] = q(vaf[cn], 0.5)
        st[f"vaf_{cn[0]}{cn[1]}_iqr"] = q(vaf[cn], 0.75) - q(vaf[cn], 0.25)
    st["pairs_n"] = len(pairs)
    for lo, hi in DIST_BINS:
        sel = [p for p in pairs if lo <= p["distance"] < hi]
        tag = f"{lo // 1000}-{hi // 1000}kb"
        st[f"pair_{tag}_span_median"] = q([p["span"] for p in sel], 0.5)
        st[f"pair_{tag}_both_ge1"] = float(np.mean([p["both"] >= 1 for p in sel]))
        st[f"pair_{tag}_one_ge1"] = float(np.mean([p["one"] >= 1 for p in sel]))
    st["pair_all_both_ge1"] = float(np.mean([p["both"] >= 1 for p in pairs]))
    st["pair_all_one_ge1"] = float(np.mean([p["one"] >= 1 for p in pairs]))
    for lo, hi in ((0, 1_000), (1_000, 20_000)):
        hp = [call_hp[p["a"]] == call_hp[p["b"]] for p in pairs
              if lo <= p["distance"] < hi and p["a"] in call_hp and p["b"] in call_hp]
        st[f"pair_{lo // 1000}-{hi // 1000}kb_sameHP_nonLOH"] = float(np.mean(hp))
    near = [p for p in pairs if p["distance"] < 5_000 and p["span"] >= 10]
    st["pair_lt5kb_both_frac_median"] = q([p["both"] / p["span"] for p in near], 0.5)
    st["pair_lt5kb_both0_frac"] = float(np.mean([p["both"] == 0 for p in near]))
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--min-vaf", type=float, default=0.0)
    ap.add_argument("--het-map")
    ap.add_argument("--depth-map")
    a = ap.parse_args()
    out = Path(a.out_dir)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    sites = load_real(a.min_vaf)
    het = het_map.load(a.het_map) if a.het_map else None
    dmap = depth_map.load(a.depth_map) if a.depth_map else None
    segs = build_segments(sites)
    pairs = real_pairs(sites)
    depth = statistics.mean(sum(s[k] for k in COLS) for s in sites if s["total"] == 2)
    if dmap:
        # SEQC2 sites sit in well-mapped regions (map weight > 1 on average); rescale so the
        # simulated mean depth at CN 2 sites matches the real one. Reads covering a site start
        # within one mean read span (13 kb) upstream.
        w = [depth_map.mean_weight(dmap, s["chrom"], s["pos"] - 13_000, s["pos"])
             for s in sites if s["total"] == 2]
        depth /= statistics.mean(w)
    print(f"{len(sites)} sites, {len(segs)} segments, {len(pairs)} pairs, depth {depth:.1f}",
          flush=True)
    results = {"real": stats(sites, pairs)}
    for model in ("m1", "mhat"):
        for err in ERRORS:
            runs = []
            for seed in range(1, a.seeds + 1):
                s_sites, s_pairs = simulate(seed, model, err, sites, segs, pairs, depth, het, dmap)
                runs.append(stats(s_sites, s_pairs))
                print(f"{model} {err} seed {seed} done", flush=True)
            results[f"{model}_{err}"] = {k: float(np.mean([r[k] for r in runs])) for k in runs[0]}
            results[f"{model}_{err}_sd"] = {k: float(np.std([r[k] for r in runs])) for k in runs[0]}
    cols = [c for c in results if not c.endswith("_sd")]
    with open(out / "tables/ppc_stats.tsv", "w") as fh:
        fh.write("stat\t" + "\t".join(cols) + "\n")
        for k in results["real"]:
            fh.write(k + "\t" + "\t".join(f"{results[c][k]:.4g}" for c in cols) + "\n")
    (out / "tables/ppc_stats.json").write_text(json.dumps(
        {"min_vaf": a.min_vaf, "het_map": a.het_map, "depth_map": a.depth_map, "depth": depth, "n_sites": len(sites), "n_segments": len(segs),
         "n_pairs": len(pairs), "results": results}, indent=1))
    print((out / "tables/ppc_stats.tsv").read_text())


if __name__ == "__main__":
    main()
