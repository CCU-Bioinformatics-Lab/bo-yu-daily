"""Estimate diplosim knobs directly from real data, one formula per knob, no simulation.

Each knob gets its own subcommand. Values come out of the data and are not tuned afterwards.

  phi  PER_SNV_TSV   depth overdispersion from a normal-only pileup (no CN change).
                     diplosim draws depth ~ Poisson(lambda * Gamma(1/phi, phi)) (diplosim/src/sequencing.rs),
                     so Var = mu + phi * mu^2 and phi = (Var / mu - 1) / mu.

  detect NORMAL_TSV CURVE_DIR CALLS_ROOT OUT_TSV
                     ClairS detection curve P(called | alt reads) per subsample, only over sites that ClairS's
                     normal-AF filter keeps (that filter is simulated separately). Sites = t50 calls piled up
                     on each subsample (CURVE_DIR/<name>/tables/real_per_snv.tsv); called = in that
                     subsample's ClairS PASS ∩ HC set (CALLS_ROOT/<name>/tables/clairs_hc_sites.tsv);
                     NORMAL_TSV = the t00_n25 pileup at the same sites (same reads as ClairS's normal).

PER_SNV_TSV is the real_per_snv.tsv written by `tools/diplosim_ppc_hcc1395.py real`
(depth = ref + alt reads over HP1/HP2/HP0, same filters as the tumour pileups).
"""
import random
import statistics
import sys


def load_depth(path):
    with open(path) as f:
        next(f)
        return [sum(int(x) for x in line.split("\t")[2:8]) for line in f]


def phi_of(depth):
    mu = statistics.fmean(depth)
    vmr = statistics.pvariance(depth) / mu
    return mu, vmr, (vmr - 1) / mu


def trimmed(depth, frac):
    d = sorted(depth)
    k = int(len(d) * frac)
    return d[k:len(d) - k]


def cmd_phi(path, n_boot=1000, seed=1):
    depth = load_depth(path)
    mu, vmr, phi = phi_of(depth)
    rng = random.Random(seed)
    boot = sorted(phi_of(rng.choices(depth, k=len(depth)))[2] for _ in range(n_boot))
    print("estimate\tn_sites\tmean_depth\tVMR\tphi\tphi_q2.5\tphi_q97.5")
    print(f"all_sites\t{len(depth)}\t{mu:.2f}\t{vmr:.3f}\t{phi:.5f}\t{boot[int(0.025 * n_boot)]:.5f}\t{boot[int(0.975 * n_boot)]:.5f}")
    # sensitivity: a few outlier sites (CN changes in the normal line, mapping artefacts) inflate the variance
    for frac in (0.005, 0.01):
        t = trimmed(depth, frac)
        m, v, p = phi_of(t)
        print(f"trim_{frac}\t{len(t)}\t{m:.2f}\t{v:.3f}\t{p:.5f}\tNA\tNA")


DETECT_SUBS = ["t40_n10", "t30_n20", "t20_n30", "t10_n40"]
ALT_CAP = 30


def load_counts(path):
    import csv
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            a = int(r["alt1"]) + int(r["alt2"]) + int(r["alt0"])
            out[(r["chrom"], r["pos"])] = (a, a + int(r["ref1"]) + int(r["ref2"]) + int(r["ref0"]))
    return out


def cmd_detect(normal_tsv, curve_dir, calls_root, out_tsv):
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from diplosim_ppc_hcc1395 import clairs_normal_drop
    normal = load_counts(normal_tsv)
    tab = {}
    for sub in DETECT_SUBS:
        called = set()
        with open(Path(calls_root) / sub / "tables" / "clairs_hc_sites.tsv") as f:
            for line in f:
                called.add(tuple(line.split("\t")[:2]))
        n, k = [0] * (ALT_CAP + 1), [0] * (ALT_CAP + 1)
        for site, (a, d) in load_counts(Path(curve_dir) / sub / "tables" / "real_per_snv.tsv").items():
            na, nd = normal.get(site, (0, 0))
            if d == 0 or clairs_normal_drop(a, d, na, nd):
                continue
            b = min(a, ALT_CAP)
            n[b] += 1
            k[b] += site in called
        tab[sub] = (n, k)
    with open(out_tsv, "w") as f:
        f.write("alt\t" + "\t".join(f"{s}_n\t{s}_p" for s in DETECT_SUBS) + "\n")
        for b in range(ALT_CAP + 1):
            f.write(f"{b}\t" + "\t".join(f"{tab[s][0][b]}\t{tab[s][1][b] / tab[s][0][b]:.4f}" if tab[s][0][b] else f"0\tNA"
                                         for s in DETECT_SUBS) + "\n")
    print(open(out_tsv).read())


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "phi":
        cmd_phi(sys.argv[2])
    elif len(sys.argv) == 6 and sys.argv[1] == "detect":
        cmd_detect(*sys.argv[2:6])
    else:
        sys.exit(__doc__)
