#!/usr/bin/env python3
"""Posterior predictive check of diplosim (free mode) against real HCC1395 ONT t50_n00.

Real side: ClairS v0.4.1 PASS SNVs (paired, t50_n00 vs normal 25x) inside the SEQC2
High-Confidence regions, piled up on the haplotagged CRAM (tools/hcc1395_hp_split_prepare.sh).
Sim side: diplosim with its own random tree and CN per seed; coverage and purity matched,
every other parameter at its default. Both sides go through the same caller-like filter
(alt >= 3, VAF >= 0.08, the ClairS call minimum on this sample) and the same statistics.

Usage:
  python3 -I tools/diplosim_ppc_hcc1395.py real    OUT_DIR SITES_TSV   # pileup -> OUT/tables/real_per_snv.tsv
  python3 -I tools/diplosim_ppc_hcc1395.py sim     OUT_DIR [N_SEEDS] [DIPLOSIM_ARGS...]   # diplosim runs -> OUT/sim/
  python3 -I tools/diplosim_ppc_hcc1395.py compare OUT_DIR             # stats + figure
"""
import csv
import json
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

MIN_ALT, MIN_VAF = 3, 0.08    # ClairS minimum on this sample (min AD alt 3, min AF 0.0806)
MIN_TAGGED_ALT, ASSIGN_FRAC = 3, 0.9
COVERAGE = 53                 # median depth of t50_n00 (lab_report/2026-10-25_seqc2_hcc1395_measured_purity)
PURITY = 1.0                  # t50_n00 is pure tumour by definition
N_CLONES = (2, 8)             # drawn per seed; HCC1395 has no known tree

COLS = ["ref1", "alt1", "ref2", "alt2", "ref0", "alt0"]


def run_real(out, sites_tsv):
    import hcc1395_hp_split as hs
    hs.CRAM = CRAM
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
    # extra args may set their own purity; diplosim rejects a flag given twice
    purity = [] if "--min-tumour-purity" in extra else ["--min-tumour-purity", str(PURITY), "--max-tumour-purity", str(PURITY)]
    subprocess.run([DIPLOSIM, "--n-clones", str(n_clones), "--n-snv", str(n_snv), "--seed", str(seed),
                    "--coverage", str(COVERAGE), *purity, "--out", outdir, *extra],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # CONIPHER aborts on a duplicate CHR/POS label (~16% of seeds at 31,595 SNVs); skip those seeds
    ok = (Path(outdir) / "diplosim.tsv").exists()
    if not ok:
        subprocess.run(["rm", "-rf", outdir])
    return ok


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
    print(f"sim: {done} seeds x {n_snv} SNV ({skipped} seeds skipped on duplicate CHR/POS)")


def load_real(out):
    with open(out / "tables" / "real_per_snv.tsv") as f:
        return [tuple(int(r[k]) for k in COLS) for r in csv.DictReader(f, delimiter="\t")]


def load_sim(run_dir):
    with open(run_dir / "diplosim.tsv") as f:
        return [tuple(int(r[k]) for k in ("HP1_REF", "HP1_ALT", "HP2_REF", "HP2_ALT", "HP0_REF", "HP0_ALT"))
                for r in csv.DictReader(f, delimiter="\t")]


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
    sims = []
    for d in sorted((out / "sim").iterdir()):
        sims.append(stats(load_sim(d)))
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
        run_real(out, sys.argv[3])
    elif mode == "sim":
        run_sim(out, int(sys.argv[3]) if len(sys.argv) > 3 else 200, sys.argv[4:])
    else:
        run_compare(out)
