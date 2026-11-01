"""Estimate diplosim knobs directly from real data, one formula per knob, no simulation.

Each knob gets its own subcommand. Values come out of the data and are not tuned afterwards.

  phi  PER_SNV_TSV   depth overdispersion from a normal-only pileup (no CN change).
                     diplosim draws depth ~ Poisson(lambda * Gamma(1/phi, phi)) (diplosim/src/sequencing.rs),
                     so Var = mu + phi * mu^2 and phi = (Var / mu - 1) / mu.

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


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "phi":
        sys.exit(__doc__)
    cmd_phi(sys.argv[2])
