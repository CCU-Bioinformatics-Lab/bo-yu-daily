"""Check a longbulksim output against its own truth, without importing longbulksim.

Reads only the sim directory (manifest.json, truth/, input/), so a bug in the simulator cannot
hide in a shared helper. Four layers:

  G  truth semantics   genome.json follows the tree: a role is on its HP, in its origin clone and
                       every descendant, nowhere else, except where truth lists it as lost;
                       truth.tsv vaf_expected equals the cell-weighted copy fraction
  R  read sampling     read (lineage, HP, copy) counts follow cell weight x copies (chi-square);
                       tagged fraction = phased_fraction; obs_hp flips = phase switches XOR mistag
  C  counts recompute  data_hp.tsv and pairs.tsv recomputed from truth/reads.tsv.gz. With no base
                       error they must match exactly; with base error, observed counts are compared
                       with the read-level expectation (each read and site flips with prob. e)
  A  analytic          not conditional on reads: alt ~ Binomial(depth, v(1-e) + (1-v)e), and pair
                       patterns ~ the truth-tree genotype mix on one HP (only with no mistag and no
                       phase switch, so obs_hp = molecule HP)

Statistical checks use disp = sum (obs - mean)^2 / sum var over items (~1 under the stated
mechanism; summing before dividing keeps items with a tiny expected count, e.g. an e^2 pattern,
from dominating), and its p-value from a parametric bootstrap (B draws under the stated
mechanism, two-sided); they pass when p > 1e-3.
The bootstrap draws items independently. That is exact for C snv checks (given the reads, every
read-site flips independently), but C pair and A checks share reads between items, so for those
it is a screen, not an exact test.

v0.1 reads have no obs_hp column; it is then the molecule HP (v0.1 has no HP errors).
truth_tree.tsv rounds clone fractions to 2 decimals. The exact fractions are taken from the spec
when one is found (truth/spec.yaml, written by longbulksim.generate, or ../../specs/<sim>.yaml);
otherwise the rounded ones are used and the vaf tolerance is widened to 1e-3 (`rounded` in value).
Per-segment R1 tests are pooled per sim (sum of X2 and df) and also reported as the smallest
segment p-value times the number of segments (Bonferroni), so a sim with hundreds of segments
does not fail by chance.

Usage: python3 tools/check_sim_expectations.py SIM_DIR [SIM_DIR ...] > checks.tsv
"""
import csv
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import yaml
from scipy.stats import chi2

HPS = ("HP1", "HP2")
PATTERNS = ((1, 1), (1, 0), (0, 1), (0, 0))  # n11, n10, n01, n00
B = 1000
ALPHA = 1e-3


def tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def load(sim):
    man = json.load(open(os.path.join(sim, "manifest.json")))
    g = json.load(open(os.path.join(sim, "truth/genome.json")))
    tree = tsv(os.path.join(sim, "truth/truth_tree.tsv"))
    purity = float(tree[0]["purity"])
    frac = {r["clone"]: float(r["clone_fraction"]) for r in tree}
    exact = False
    name = os.path.basename(sim.rstrip("/"))
    for spec in (os.path.join(sim, "truth/spec.yaml"),
                 os.path.join(sim, "..", "..", "specs", f"{name}.yaml")):
        if os.path.exists(spec):
            clones = yaml.safe_load(open(spec))["clones"]
            if set(clones) == set(frac):
                frac = {c: float(v["fraction"]) for c, v in clones.items()}
                exact = True
            break
    weight = {"N": 1 - purity, **{c: purity * f for c, f in frac.items()}}
    parent = {r["clone"]: r["parent"] for r in tree}
    reads = defaultdict(list)
    with gzip.open(os.path.join(sim, "truth/reads.tsv.gz"), "rt") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            reads[r["segment"]].append((int(r["start"]), int(r["end"]), r["lineage"], r["hp"],
                                        int(r["copy"]), r["tagged"] == "1",
                                        r.get("obs_hp", r["hp"])))
    switches = defaultdict(list)
    p = os.path.join(sim, "truth/phase_switches.tsv")
    if os.path.exists(p):
        for r in tsv(p):
            switches[r["segment"]].append(int(r["pos"]))
    return man, g["genome"], g["lost"], weight, parent, reads, switches, exact


def row(out, sim, layer, check, n, value, expected, ok):
    out.append([sim.rstrip("/"), layer, check, n, value, expected,
                "PASS" if ok else "FAIL"])


def boot(out, sim, layer, check, obs, mean, var, draw, rng):
    """disp of obs against (mean, var) and its bootstrap p-value; draw(rng) -> (B, n) arrays."""
    obs, mean, var = (np.asarray(x, float).ravel() for x in (obs, mean, var))
    keep = var > 1e-12
    if not keep.any():
        return
    stat = lambda x: ((x - mean) ** 2)[..., keep].sum(-1) / var[keep].sum()  # noqa: E731
    d = float(stat(obs))
    sims = stat(draw(rng).reshape(B, -1))
    p = 2 * min((sims >= d).mean(), (sims <= d).mean())
    p = max(p, 1 / B)
    row(out, sim, layer, check, int(keep.sum()),
        f"disp={d:.3f};null={np.median(sims):.3f};p={p:.3g}", f"p > {ALPHA}", p > ALPHA)


def descendants(c, parent):
    out, stack = {c}, [c]
    while stack:
        x = stack.pop()
        for k, p in parent.items():
            if p == x and k not in out:
                out.add(k)
                stack.append(k)
    return out


def emission(e):
    """E[g, o]: P(observed pattern o | true genotype g), each site read flipped with prob. e."""
    site = lambda t, o: 1 - e if t == o else e  # noqa: E731
    return np.array([[site(g[0], o[0]) * site(g[1], o[1]) for o in PATTERNS] for g in PATTERNS])


def check_sim(sim, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    man, genome, lost, weight, parent, reads, switches, exact = load(sim)
    e = float(man.get("base_error", 0) or 0)
    mistag = float(man.get("mistag_rate", 0) or 0)
    sw_rate = float(man.get("switch_rate_per_mb", 0) or 0)
    truth = tsv(os.path.join(sim, "truth/truth.tsv"))
    role = {}
    for r in truth:
        role.setdefault(r["role"], (r["origin_clone"], r["hp"], r["segment"]))

    def carries(seg, i, rl):
        _, _, lin, h, k, _, _ = reads[seg][i]
        return rl in genome[lin][seg][h][k]

    # G1: role placement follows the tree
    bad = 0
    for rl, (o, hp, seg) in role.items():
        carriers = descendants(o, parent)
        for lin, segs in genome.items():
            for h in HPS:
                has = any(rl in cp for cp in segs[seg][h])
                want = h == hp and lin in carriers and rl not in lost.get(lin, [])
                bad += has != want
    row(out, sim, "G", "role_placement", len(role) * len(genome) * 2, bad, 0, bad == 0)

    # G2: vaf_expected = sum_L w_L #copies carrying / sum_L w_L #copies
    def vaf(rl):
        _, hp, seg = role[rl]
        tot = sum(w * sum(len(genome[c][seg][h]) for h in HPS) for c, w in weight.items())
        alt = sum(w * sum(rl in cp for cp in genome[c][seg][hp]) for c, w in weight.items())
        return alt / tot
    diff = max(abs(float(r["vaf_expected"]) - vaf(r["role"])) for r in truth)
    tol = 5.0001e-5 if exact else 1e-3
    row(out, sim, "G", "vaf_expected", len(truth), f"{diff:.2g}" + ("" if exact else ";rounded"),
        f"<= {tol:.2g}", diff <= tol)

    # R1: molecule composition, per segment, pooled per sim
    x2_all, df_all, pmin, extra_all, nseg = 0.0, 0, 1.0, 0, 0
    for seg, rs in sorted(reads.items()):
        cats, p = [], []
        for c, w in weight.items():
            for h in HPS:
                for k in range(len(genome[c][seg][h])):
                    cats.append((c, h, k))
                    p.append(w)
        p = np.array(p) / sum(p)
        cnt = Counter((r[2], r[3], r[4]) for r in rs)
        obs = np.array([cnt.get(k, 0) for k in cats])
        # reads from a molecule genome.json does not have, or from a zero-weight lineage
        extra = sum(cnt.values()) - obs.sum() + int(obs[p == 0].sum())
        exp = p[p > 0] * len(rs)
        x2 = float(((obs[p > 0] - exp) ** 2 / exp).sum())
        df = int((p > 0).sum()) - 1
        if df > 0:
            x2_all, df_all, nseg = x2_all + x2, df_all + df, nseg + 1
            pmin = min(pmin, float(chi2.sf(x2, df)))
        extra_all += extra
    pooled = float(chi2.sf(x2_all, df_all)) if df_all else 1.0
    bonf = min(1.0, pmin * max(nseg, 1))
    row(out, sim, "R", "molecule_mix", len(reads), f"X2={x2_all:.1f};df={df_all};p={pooled:.3g};"
        f"min_seg_p_bonf={bonf:.3g};unknown={extra_all}",
        f"p > {ALPHA}, bonf > {ALPHA}, unknown = 0",
        pooled > ALPHA and bonf > ALPHA and extra_all == 0)

    allr = [r for rs in reads.values() for r in rs]
    n = len(allr)
    if not man.get("het_map"):
        t = sum(r[5] for r in allr)
        f = float(man["phased_fraction"])
        z = (t - n * f) / np.sqrt(n * f * (1 - f))
        row(out, sim, "R", "tagged_fraction", n, f"{t / n:.4f};z={z:.2f}", f"{f}", abs(z) < 4)

    # R3: obs_hp = molecule HP XOR (odd switches before the read midpoint) XOR mistag
    flips = 0
    for seg, rs in reads.items():
        sw = np.array(sorted(switches.get(seg, [])))
        for s0, e0, _, h, _, _, oh in rs:
            by_switch = len(sw) and np.searchsorted(sw, (s0 + e0) // 2, side="right") % 2 == 1
            flips += (oh != h) != bool(by_switch)
    if mistag == 0:
        row(out, sim, "R", "hp_flip_after_switches", n, flips, 0, flips == 0)
    else:
        z = (flips - n * mistag) / np.sqrt(n * mistag * (1 - mistag))
        row(out, sim, "R", "hp_flip_after_switches", n, f"{flips / n:.4f};z={z:.2f}", mistag,
            abs(z) < 4)
    if sw_rate:  # the count is Poisson(rate x segment length); lengths are not in the outputs
        k = sum(len(v) for v in switches.values())
        out.append([sim.rstrip("/"), "R", "switches_recorded", k, k,
                    "Poisson; pooled across sims in the report", "INFO"])

    # C1: per-SNV counts from reads
    data = {r["mutation_id"]: r for r in tsv(os.path.join(sim, "input/data_hp.tsv"))}
    by_id = {r["mutation_id"]: r for r in truth}
    arr = {seg: np.array([(r[0], r[1]) for r in rs]) for seg, rs in reads.items()}
    cover = {}
    keys = ("alt_counts", "alt_hp1", "alt_hp2", "alt_unphased")
    totals = {"alt_counts": ("ref_counts", "alt_counts"), "alt_hp1": ("ref_hp1", "alt_hp1"),
              "alt_hp2": ("ref_hp2", "alt_hp2"), "alt_unphased": ("ref_unphased", "alt_unphased")}
    mismatch = 0
    nc_nn = {k: [] for k in keys}  # (carrier reads, non-carrier reads, observed alt) per SNV
    depth_obs, depth_exp = [], []
    for mid, d in data.items():
        t = by_id[mid]
        seg, pos, rl = t["segment"], int(t["pos"]), t["role"]
        se = arr[seg]
        idx = np.nonzero((se[:, 0] <= pos) & (se[:, 1] > pos))[0]
        cover[mid] = idx
        carry = np.array([carries(seg, i, rl) for i in idx], bool)
        tag = np.array([reads[seg][i][5] for i in idx], bool)
        oh = np.array([reads[seg][i][6] for i in idx])
        sel = {"alt_counts": np.ones(len(idx), bool), "alt_hp1": tag & (oh == "HP1"),
               "alt_hp2": tag & (oh == "HP2"), "alt_unphased": ~tag}
        depth_obs.append(len(idx))
        depth_exp.append(man["depth"] / 2 * sum(w * sum(len(genome[c][seg][h]) for h in HPS)
                                                for c, w in weight.items()))
        for k in keys:
            mismatch += sum(int(d[c]) for c in totals[k]) != sel[k].sum()
            nc = int(carry[sel[k]].sum())
            if e == 0:
                mismatch += int(d[k]) != nc
            nc_nn[k].append((nc, int(sel[k].sum()) - nc, int(d[k])))
    row(out, sim, "C", "snv_counts_exact" if e == 0 else "snv_depths_exact", len(data),
        mismatch, 0, mismatch == 0)
    if e > 0:
        for k in keys:
            nc, nn, ob = np.array(nc_nn[k]).T
            boot(out, sim, "C", f"snv_{k}_vs_reads", ob, nc * (1 - e) + nn * e,
                 (nc + nn) * e * (1 - e),
                 lambda g: g.binomial(nc, 1 - e, (B, len(nc))) + g.binomial(nn, e, (B, len(nn))),
                 rng)

    # C2: pair rows from reads
    pairs = tsv(os.path.join(sim, "input/pairs.tsv"))
    cols = ("n11", "n10", "n01", "n00")
    got = {(r["mutation_i"], r["mutation_j"], r["hap"]): r for r in pairs}
    want, classes, observed = {}, [], []
    by_seg = defaultdict(list)
    for mid in data:
        by_seg[by_id[mid]["segment"]].append(mid)
    exact_bad = 0
    for seg, mids in by_seg.items():
        mids = sorted(mids)
        for a_i, a in enumerate(mids):
            for b in mids[a_i + 1:]:
                both = np.intersect1d(cover[a], cover[b])
                if not len(both):
                    continue
                ra, rb = by_id[a]["role"], by_id[b]["role"]
                for h in HPS:
                    sel = [i for i in both if reads[seg][i][5] and reads[seg][i][6] == h]
                    if not sel:
                        continue
                    want[(a, b, h)] = len(sel)
                    if (a, b, h) not in got:
                        continue
                    g4 = Counter((int(carries(seg, i, ra)), int(carries(seg, i, rb))) for i in sel)
                    cls = [g4[p] for p in PATTERNS]
                    obs = [int(got[(a, b, h)][c]) for c in cols]
                    if e == 0:
                        exact_bad += cls != obs
                    classes.append(cls)
                    observed.append(obs)
    rows_bad = len(set(got) ^ set(want))
    depth_bad = sum(int(got[k]["callable_pair_reads"]) != want[k] for k in set(got) & set(want))
    row(out, sim, "C", "pair_rows_and_depths", len(want), f"rows={rows_bad};depth={depth_bad}", 0,
        rows_bad == 0 and depth_bad == 0)
    if e == 0:
        row(out, sim, "C", "pair_counts_exact", len(got), exact_bad, 0, exact_bad == 0)
    elif classes:
        E = emission(e)
        cls, ob = np.array(classes), np.array(observed)
        mean, var = cls @ E, cls @ (E * (1 - E))

        def draw(g):
            return sum(g.multinomial(cls[:, k], E[k], size=(B, len(cls))) for k in range(4))
        boot(out, sim, "C", "pair_counts_vs_reads", ob, mean, var, draw, rng)

    # A1: alt ~ Binomial(depth, v(1-e) + (1-v)e), not conditional on which reads were drawn
    nd, pa, oa = [], [], []
    for mid, d in data.items():
        v = vaf(by_id[mid]["role"])
        nd.append(int(d["ref_counts"]) + int(d["alt_counts"]))
        pa.append(v * (1 - e) + (1 - v) * e)
        oa.append(int(d["alt_counts"]))
    nd, pa = np.array(nd), np.array(pa)
    boot(out, sim, "A", "snv_alt_binomial", oa, nd * pa, nd * pa * (1 - pa),
         lambda g: g.binomial(nd, pa, (B, len(nd))), rng)

    # A1b: depth vs depth/2 x sum_L w_L #copies (no depth map); pooled over SNVs, since one
    # position's depth varies by more than 15% and segments can hold a single SNV
    if not man.get("depth_map") and depth_obs:
        ratio = sum(depth_obs) / sum(depth_exp)
        row(out, sim, "A", "depth_vs_expected", len(depth_obs), f"{ratio:.3f}", "0.95-1.05",
            0.95 <= ratio <= 1.05)

    # A2: pair patterns ~ truth genotype mix on that HP (obs_hp = molecule HP only)
    if mistag == 0 and sw_rate == 0 and got:
        E = emission(e)
        nn, pr, ob = [], [], []
        for (a, b, h), r in got.items():
            seg = by_id[a]["segment"]
            ra, rb = by_id[a]["role"], by_id[b]["role"]
            mix = np.zeros(4)
            for c, w in weight.items():
                for cp in genome[c][seg][h]:
                    mix[PATTERNS.index((int(ra in cp), int(rb in cp)))] += w
            if mix.sum() == 0:
                continue
            nn.append(int(r["callable_pair_reads"]))
            pr.append(mix / mix.sum() @ E)
            ob.append([int(r[c]) for c in cols])
        nn, pr, ob = np.array(nn), np.array(pr), np.array(ob)
        impossible = int(ob[pr <= 1e-12].sum())
        row(out, sim, "A", "pair_impossible_patterns", len(nn), impossible, 0, impossible == 0)

        def draw(g):
            return g.multinomial(nn[None, :], pr, size=(B, len(nn)))
        boot(out, sim, "A", "pair_patterns_vs_tree", ob, nn[:, None] * pr,
             nn[:, None] * pr * (1 - pr), draw, rng)
    return out


def main():
    lines = ["sim\tlayer\tcheck\tn\tvalue\texpected\tverdict"]
    for sim in sys.argv[1:]:
        lines += ["\t".join(map(str, r)) for r in check_sim(sim)]
    sys.stdout.write("\n".join(lines) + "\n")  # one write, so parallel runs do not interleave


if __name__ == "__main__":
    main()
