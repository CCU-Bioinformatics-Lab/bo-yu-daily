#!/usr/bin/env python3
"""Posterior predictive check of diplosim (free mode) against real HCC1395 ONT t50_n00.

Real side: ClairS v0.4.1 PASS SNVs (paired, t50_n00 vs normal 25x) inside the SEQC2
High-Confidence regions, piled up on the haplotagged CRAM (tools/hcc1395_hp_split_prepare.sh).
Sim side: diplosim with its own random tree and CN per seed; coverage and purity matched,
every other parameter at its default. Both sides go through the same caller-like filter
(alt >= 3, VAF >= 0.08, the ClairS call minimum on this sample) and the same statistics.

Usage:
  python3 -I tools/diplosim_ppc_hcc1395.py real    OUT_DIR SITES_TSV [CRAM]   # pileup -> OUT/tables/real_per_snv.tsv
  python3 -I tools/diplosim_ppc_hcc1395.py sim     OUT_DIR [N_SEEDS] [DIPLOSIM_ARGS...]   # diplosim runs -> OUT/sim/
  python3 -I tools/diplosim_ppc_hcc1395.py compare OUT_DIR             # stats + figure

DIPLOSIM_PPC_RANGES=RANGES_TSV makes each seed draw the listed knobs from ranges (flag, lo, hi, lin|log)
instead of the fixed values in DIPLOSIM_ARGS; the drawn values go to OUT/tables/sim_knobs.tsv.

A range row named normal_tumour_fraction (no leading --) is not passed to diplosim. With it, each seed
also gets a matched normal sample: same tree and clones at purity c, NORMAL_COVERAGE depth. The sim side
then drops SNVs the way ClairS v0.4.1 does before the caller-like filter: normal AF >= 0.05 and tumour
AF < 6 x normal AF, when normal depth > 4 (src/extract_pair_candidates.py:439-450, shared/param.py:38,120).
The real side already went through ClairS, so the rule is not applied there.
"""
import csv
import json
import math
import os
import random
import statistics
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DIPLOSIM = os.path.join(HERE, "..", "diplosim", "target", "release", "diplosim")
CRAM = "/big8_disk/boyu114/hcc1395_hp_split/tagged_t50_n00.cram"
CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]

# Caller-like filter. Default: ClairS minimum on t50_n00 (min AD alt 3, min AF 0.0806). The env vars
# DIPLOSIM_PPC_MIN_ALT / DIPLOSIM_PPC_MIN_VAF override it (purity holdout v2: 5 / 0.10, the ClairS
# 1% quantiles, which stay about the same at every purity).
MIN_ALT = int(os.environ.get("DIPLOSIM_PPC_MIN_ALT", 3))
MIN_VAF = float(os.environ.get("DIPLOSIM_PPC_MIN_VAF", 0.08))
MIN_TAGGED_ALT, ASSIGN_FRAC = 3, 0.9
COVERAGE = 53                 # median depth of t50_n00 (lab_report/2026-10-25_seqc2_hcc1395_measured_purity)
PURITY = 1.0                  # t50_n00 is pure tumour by definition
N_CLONES = (2, 8)             # drawn per seed; HCC1395 has no known tree

RANGES = os.environ.get("DIPLOSIM_PPC_RANGES")
NORMAL_KNOB = "normal_tumour_fraction"
NORMAL_COVERAGE = 25.1            # mean depth of t00_n25 at the t50 SNV sites (= ClairS's normal_25x)
CLAIRS_NORMAL_MAX_AF, CLAIRS_UPPER_BETA, CLAIRS_MIN_COVERAGE = 0.05, 6, 4


def load_ranges(path):
    with open(path) as f:
        rows = [l.split() for l in f if l.strip() and not l.startswith(("#", "flag"))]
    return [(flag, float(lo), float(hi), scale) for flag, lo, hi, scale in rows]


def draw_knobs(seed, ranges):
    rng = random.Random(f"knobs{seed}")   # own stream: n_clones per seed stays the same as without ranges
    out = {}
    for flag, lo, hi, scale in ranges:
        u = rng.random()
        out[flag] = lo * (hi / lo) ** u if scale == "log" else lo + (hi - lo) * u
    return out


def strip_flags(extra, flags):
    res, skip = [], False
    for a in extra:
        if skip:
            skip = False
        elif a in flags:
            skip = True
        else:
            res.append(a)
    return res


COLS = ["ref1", "alt1", "ref2", "alt2", "ref0", "alt0"]


def run_real(out, sites_tsv, cram=CRAM):
    import hcc1395_hp_split as hs
    hs.CRAM = cram
    alt_of = {}
    with open(sites_tsv) as f:
        for line in f:
            c, p, _, a = line.split("\t")[:4]
            alt_of[(c, p)] = a
    sites_file = out / "sites.tmp"
    sites_file.write_text("".join(f"{c}\t{p}\n" for c, p in alt_of))
    reads = {}
    with ProcessPoolExecutor(len(CHROMS)) as ex:
        for r in ex.map(hs.pileup_chrom, [(c, str(sites_file), alt_of) for c in CHROMS]):
            reads.update(r)
    sites_file.unlink()
    with open(out / "tables" / "real_per_snv.tsv", "w") as f:
        f.write("chrom\tpos\t" + "\t".join(COLS) + "\n")
        for (c, p), rd in reads.items():
            n = {k: 0 for k in COLS}
            for allele, h in rd.values():
                if allele != "other":
                    n[f"{allele}{h}"] += 1
            f.write(f"{c}\t{p}\t" + "\t".join(str(n[k]) for k in COLS) + "\n")
    print(f"real: {len(reads)} SNVs with pileup")


def run_one(args):
    seed, n_snv, outdir, extra = args
    n_clones = random.Random(seed).randint(*N_CLONES)
    knobs = draw_knobs(seed, load_ranges(RANGES)) if RANGES else {}
    flags = {f: v for f, v in knobs.items() if f.startswith("--")}
    extra = strip_flags(extra, flags) + [x for f, v in flags.items() for x in (f, f"{v:.6g}")]
    # extra args may set their own purity, coverage or SNV count; diplosim rejects a flag given twice
    purity = [] if "--min-tumour-purity" in extra else ["--min-tumour-purity", str(PURITY), "--max-tumour-purity", str(PURITY)]
    coverage = [] if "--coverage" in extra else ["--coverage", str(COVERAGE)]
    n = [] if "--n-snv" in extra else ["--n-snv", str(n_snv)]
    subprocess.run([DIPLOSIM, "--n-clones", str(n_clones), *n, "--seed", str(seed),
                    *coverage, *purity, "--out", outdir, *extra],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # CONIPHER aborts on a duplicate CHR/POS label (~16% of seeds at 31,595 SNVs); skip those seeds
    ok = (Path(outdir) / "diplosim.tsv").exists()
    if not ok:
        subprocess.run(["rm", "-rf", outdir])
    elif knobs:
        (Path(outdir) / "knobs.json").write_text(json.dumps({"n_clones": n_clones, **knobs}))
        if NORMAL_KNOB in knobs:
            write_normal(Path(outdir), seed, knobs[NORMAL_KNOB], extra)
    return ok


def flag_value(extra, flag, default):
    return float(extra[extra.index(flag) + 1]) if flag in extra else default


def normal_vaf(run_dir, c):
    """Expected VAF per VAR_POS in a sample of the same clones at purity c (diplosim/src/sequencing.rs:83
    expected(): mutated copies over all copies, tumour clone proportions rescaled to sum to c).
    Returns {VAR_POS: (vaf, mean copy number)}."""
    prop, normal = {}, None
    with open(run_dir / "diplosim_cloneprops.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            prop[r["Clone"]] = float(r["Proportion"])
            if r["Is_Normal"] == "Yes":
                normal = r["Clone"]
    purity = 1 - prop[normal]
    w = {k: (1 - c if k == normal else v * c / purity) for k, v in prop.items()}
    num, den = {}, {}
    with open(run_dir / "truth" / "genotypes.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            k, cl = r["VAR_POS"], r["CLONE"]
            den[k] = den.get(k, 0.0) + (int(r["A"]) + int(r["B"])) * w[cl]
            if cl != normal:
                num[k] = num.get(k, 0.0) + int(r["MUT"]) * w[cl]
    return {k: (num.get(k, 0.0) / den[k], den[k]) for k in den}


def write_normal(run_dir, seed, c, extra):
    """Matched normal counts: depth ~ Poisson(cov * cn / mean cn * Gamma(1/phi, phi)), alt ~ Binomial with
    the seed's base error applied both ways (as diplosim/src/hp.rs swap_some)."""
    rng = random.Random(f"normal{seed}")
    phi = flag_value(extra, "--depth-dispersion", 0.0)
    err = flag_value(extra, "--base-error", 0.0)
    exp = normal_vaf(run_dir, c)
    fbar = statistics.fmean(cn for _, cn in exp.values())
    with open(run_dir / "normal.tsv", "w") as f:
        f.write("VAR_POS\tNORMAL_REF\tNORMAL_ALT\n")
        for k, (vaf, cn) in exp.items():
            lam = cn * NORMAL_COVERAGE / fbar
            if phi > 0:
                lam *= rng.gammavariate(1 / phi, phi)
            depth = poisson(rng, lam)
            pa = vaf * (1 - err) + (1 - vaf) * err
            alt = sum(rng.random() < pa for _ in range(depth))
            f.write(f"{k}\t{depth - alt}\t{alt}\n")


def poisson(rng, lam):
    """Poisson draw by inversion (lam is about 25 here; stdlib random has no Poisson in Python 3.10)."""
    u, k, p = rng.random(), 0, math.exp(-lam)
    s = p
    while u > s:
        k += 1
        p *= lam / k
        s += p
    return k


def clairs_normal_drop(tumour_alt, tumour_depth, normal_alt, normal_depth):
    """True when ClairS v0.4.1 removes the candidate because of alt reads in the normal."""
    if normal_depth <= CLAIRS_MIN_COVERAGE or normal_alt == 0 or tumour_alt == 0:
        return False
    naf = normal_alt / normal_depth
    return naf >= CLAIRS_NORMAL_MAX_AF and tumour_alt / tumour_depth < naf * CLAIRS_UPPER_BETA


def run_sim(out, n_seeds, extra=()):
    n_snv = sum(1 for _ in open(out / "tables" / "real_per_snv.tsv")) - 1
    (out / "sim").mkdir(exist_ok=True)
    done, seed, skipped = 0, 0, 0
    with ProcessPoolExecutor(16) as ex:
        while done < n_seeds:
            batch = [(s, n_snv, str(out / "sim" / f"seed{s}"), list(extra)) for s in range(seed + 1, seed + 1 + n_seeds - done)]
            seed += len(batch)
            res = list(ex.map(run_one, batch))
            done += sum(res)
            skipped += len(res) - sum(res)
    if "--n-snv" in extra:
        n_snv = extra[list(extra).index("--n-snv") + 1]
    print(f"sim: {done} seeds x {n_snv} SNV ({skipped} seeds skipped on duplicate CHR/POS)")


def load_real(out):
    with open(out / "tables" / "real_per_snv.tsv") as f:
        return [tuple(int(r[k]) for k in COLS) for r in csv.DictReader(f, delimiter="\t")]


def load_sim(run_dir):
    with open(run_dir / "diplosim.tsv") as f:
        rows = [(r["VAR_POS"], tuple(int(r[k]) for k in ("HP1_REF", "HP1_ALT", "HP2_REF", "HP2_ALT", "HP0_REF", "HP0_ALT")))
                for r in csv.DictReader(f, delimiter="\t")]
    if not (run_dir / "normal.tsv").exists():
        return [x for _, x in rows]
    with open(run_dir / "normal.tsv") as f:
        nm = {r["VAR_POS"]: (int(r["NORMAL_REF"]), int(r["NORMAL_ALT"])) for r in csv.DictReader(f, delimiter="\t")}
    # a dropped SNV keeps its row with alt set to 0, so it fails the caller filter and frac_called keeps
    # the same denominator
    out = []
    for k, x in rows:
        nref, nalt = nm[k]
        if clairs_normal_drop(x[1] + x[3] + x[5], sum(x), nalt, nref + nalt):
            x = (x[0] + x[1], 0, x[2] + x[3], 0, x[4] + x[5], 0)
        out.append(x)
    return out


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else float("nan")


def stats(rows):
    """Statistics on SNVs that pass the caller-like filter. rows: (ref1, alt1, ref2, alt2, ref0, alt0)."""
    kept = []
    for r1, a1, r2, a2, r0, a0 in rows:
        d, a = r1 + a1 + r2 + a2 + r0 + a0, a1 + a2 + a0
        if a >= MIN_ALT and a / d >= MIN_VAF:
            kept.append((r1, a1, r2, a2, r0, a0, d, a))
    depth = [x[6] for x in kept]
    vaf = [x[7] / x[6] for x in kept]
    mu = statistics.fmean(depth)
    tag_frac = [(x[6] - x[4] - x[5]) / x[6] for x in kept if x[6] >= 20]
    assigned, split, in_hp_vaf, alt_on_minor = 0, 0, [], []
    minor_frac = []
    for r1, a1, r2, a2, r0, a0, d, a in kept:
        d1, d2 = r1 + a1, r2 + a2
        if d1 + d2 >= 10:
            minor_frac.append(min(d1, d2) / (d1 + d2))
        at = a1 + a2
        if at < MIN_TAGGED_ALT:
            continue
        if max(a1, a2) / at < ASSIGN_FRAC:
            split += 1
            continue
        assigned += 1
        h_alt, h_d = (a1, d1) if a1 > a2 else (a2, d2)
        in_hp_vaf.append(h_alt / h_d)
        if d1 != d2:
            alt_on_minor.append(1.0 if h_d == min(d1, d2) else 0.0)
    tot = sum(depth)
    return {
        "n_called": len(kept),
        "frac_called": len(kept) / len(rows),
        "depth_median": statistics.median(depth),
        "depth_VMR": statistics.pvariance(depth) / mu,
        "VAF_q10": q(vaf, 0.10), "VAF_q50": q(vaf, 0.50), "VAF_q90": q(vaf, 0.90),
        "VAF_frac_gt_0.6": sum(v > 0.6 for v in vaf) / len(vaf),
        "HP0_frac_pooled": sum(x[4] + x[5] for x in kept) / tot,
        "tag_frac_SD_sites": statistics.pstdev(tag_frac),
        "tag_frac_lt_0.5_sites": sum(t < 0.5 for t in tag_frac) / len(tag_frac),
        "split_alt_frac": split / (split + assigned),
        "inHP_VAF_q50": q(in_hp_vaf, 0.50), "inHP_VAF_q90": q(in_hp_vaf, 0.90),
        "minorHP_depth_q50": q(minor_frac, 0.50),
        "minorHP_depth_lt_0.1": sum(m < 0.1 for m in minor_frac) / len(minor_frac),
        "alt_on_minorHP": statistics.fmean(alt_on_minor),
    }


def run_compare(out):
    real = stats(load_real(out))
    sims, knobs = [], []
    for d in sorted((out / "sim").iterdir()):
        sims.append(stats(load_sim(d)))
        if (d / "knobs.json").exists():
            knobs.append({"run": d.name, **json.loads((d / "knobs.json").read_text())})
    if knobs:
        with open(out / "tables" / "sim_knobs.tsv", "w") as f:
            f.write("\t".join(knobs[0]) + "\n")
            f.writelines("\t".join(str(r[k]) for k in knobs[0]) + "\n" for r in knobs)
    rows = []
    for k, v in real.items():
        sv = [s[k] for s in sims]
        lo, hi = q(sv, 0.025), q(sv, 0.975)
        rank = sum(x < v for x in sv) / len(sv)
        rows.append((k, v, statistics.median(sv), lo, hi, rank, "in" if lo <= v <= hi else "OUT"))
    with open(out / "tables" / "ppc_stats.tsv", "w") as f:
        f.write("statistic\treal\tsim_median\tsim_q2.5\tsim_q97.5\treal_rank_in_sim\tverdict\n")
        for r in rows:
            f.write(f"{r[0]}\t{r[1]:.4g}\t{r[2]:.4g}\t{r[3]:.4g}\t{r[4]:.4g}\t{r[5]:.3f}\t{r[6]}\n")
    (out / "tables" / "sim_stats.json").write_text(json.dumps(sims))
    (out / "tables" / "real_stats.json").write_text(json.dumps(real))
    print((out / "tables" / "ppc_stats.tsv").read_text())


if __name__ == "__main__":
    mode, out = sys.argv[1], Path(sys.argv[2])
    (out / "tables").mkdir(parents=True, exist_ok=True)
    if mode == "real":
        run_real(out, sys.argv[3], *sys.argv[4:5])
    elif mode == "sim":
        run_sim(out, int(sys.argv[3]) if len(sys.argv) > 3 else 200, sys.argv[4:])
    else:
        run_compare(out)
