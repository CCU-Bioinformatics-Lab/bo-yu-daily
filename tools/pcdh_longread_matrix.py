"""PCDH long-read epiallele matrices per haplotype (B09 long-read method, re-implemented).

usage: python3 pcdh_longread_matrix.py TAGGED_BAM LABEL OUT_TSV [MODS] [--fixed N]
       python3 pcdh_longread_matrix.py --selftest

--fixed N: every matrix is exactly N CpGs x MIN_READS reads (the N-CpG interval
with the most passing reads, then a random MIN_READS of them), so groups with
different depth get the same test power. Default: greedy (paper-like).
--selftest: run both nulls on simulated matrices (no structure, per-read
offset only, monoclonal, two clones) and print z / z_ff.

Writes OUT_TSV (one row per window x HP) and OUT_TSV with suffix
.clusters.tsv (per-read UPGMA cluster at 2 and 5 clusters).

Follows B09 Methods ("Clustering of barcode matrices ..."); B09 has no public
code, so the choices marked [ours] are this repo's, not the paper's.
  1. Per HP (HP tag from longphase-s haplotag), per read: confident CpG calls
     (p >= 0.8 -> 1, <= 0.2 -> 0, else dropout) [ours: thresholds; paper used
     modkit extract calls defaults].
  2. Semi-sliding windows over PCDH [ours: 30 kb, step 15 kb; paper: "~3-exon",
     mean 29.5 kb].
  3. Greedy matrix per window: the contiguous CpG interval [ours: contiguous]
     with the most CpGs such that >= MIN_READS reads have <= 20% dropout and
     <= 5 contiguous dropouts on it (paper thresholds). MIN_READS / MIN_CPGS
     are lowered for our depth [ours; paper targeted >50-100 reads at 266X].
  4. Hamming kNN imputation (k=3, normalised Hamming on shared sites, majority
     vote, fallback column majority), then UPGMA (average linkage, Hamming);
     report top-bifurcation minor fraction and 5-cluster fractions (paper).
  5. Structure test [ours, not in paper]: variance of pairwise normalised
     Hamming distances on observed (pre-imputation) shared sites, against a
     null that permutes observed values among reads within each CpG column
     (missing mask fixed). Linkage between CpGs on the same read (clone or
     copy structure) raises the variance; independent per-CpG noise does not.
     A per-read methylation offset (biological or a per-read calling bias)
     also raises it, so a second, stricter null keeps every read's and every
     CpG's methylated count (curveball trades between read pairs on columns
     both reads observe). Only co-varying CpG combinations survive that null.
"""
import sys
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

REF = "/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
CHROM, START, END = "chr5", 140_780_000, 141_520_000   # PCDHA1..PCDHGC5 (GRCh38, approx)
WIN, STEP = 30_000, 15_000
MIN_READS, MIN_CPGS = 20, 25
MAX_DROPOUT, MAX_RUN = 0.20, 5
K_NN = 3
N_PERM = 200
MIN_MAPQ = 20
P_HI, P_LO = 0.8, 0.2


def load_reads(bam_path, mods):
    """CpG positions and, per HP, a list of (read name, dict cpg_index -> 0/1)"""
    import pysam
    fa = pysam.FastaFile(REF)
    seq = fa.fetch(CHROM, START, END + 1).upper()
    cpgs = np.array([START + i for i in range(len(seq) - 1) if seq[i:i + 2] == "CG"])
    cpg_idx = {int(p): i for i, p in enumerate(cpgs)}
    by_hp = {}
    bam = pysam.AlignmentFile(bam_path, reference_filename=REF)
    for r in bam.fetch(CHROM, START, END):
        if r.is_secondary or r.is_supplementary or r.mapping_quality < MIN_MAPQ:
            continue
        if not r.has_tag("HP"):
            continue
        hp = str(r.get_tag("HP")).split("-")[0]
        mb = r.modified_bases
        if not mb:
            continue
        q2r = dict(r.get_aligned_pairs(matches_only=True))
        probs = {}
        for (base, strand, mod), lst in mb.items():
            if mod not in mods:
                continue
            for qpos, ml in lst:
                probs[qpos] = probs.get(qpos, 0.0) + (ml + 0.5) / 256
        calls = {}
        for qpos, p in probs.items():
            rp = q2r.get(qpos)
            if rp is None:
                continue
            c = rp if not r.is_reverse else rp - 1   # minus-strand call sits on the G
            i = cpg_idx.get(c)
            if i is None:
                continue
            if p >= P_HI:
                calls[i] = 1
            elif p <= P_LO:
                calls[i] = 0
        if calls:
            by_hp.setdefault(hp, []).append((r.query_name, calls))
    bam.close()
    return cpgs, by_hp


def max_runs(S):
    """per row: longest run of missing (-1) values"""
    cur = np.zeros(S.shape[0], int)
    best = np.zeros(S.shape[0], int)
    for k in range(S.shape[1]):
        cur = (cur + 1) * (S[:, k] < 0)
        best = np.maximum(best, cur)
    return best


def best_matrix(M):
    """greedy: largest contiguous CpG interval with >= MIN_READS passing reads"""
    called = (M >= 0).astype(int)
    cs = np.concatenate([np.zeros((M.shape[0], 1), int), np.cumsum(called, axis=1)], axis=1)
    best = None
    n = M.shape[1]
    for i in range(0, n - MIN_CPGS + 1, 5):
        for j in range(i + MIN_CPGS, n + 1, 5):
            frac = (cs[:, j] - cs[:, i]) / (j - i)
            cand = np.where(frac >= 1 - MAX_DROPOUT)[0]
            if len(cand) < MIN_READS:
                break
            if best is not None and j - i < best[1] - best[0]:
                continue
            rows = cand[max_runs(M[cand, i:j]) <= MAX_RUN]
            if len(rows) >= MIN_READS and (best is None or j - i > best[1] - best[0]
                                           or len(rows) > len(best[2])):
                best = (i, j, rows)
    return best


def fixed_matrix(M, n_cpgs, rng):
    """n_cpgs-CpG interval with the most passing reads; random MIN_READS of them"""
    called = (M >= 0).astype(int)
    cs = np.concatenate([np.zeros((M.shape[0], 1), int), np.cumsum(called, axis=1)], axis=1)
    best = None
    for i in range(0, M.shape[1] - n_cpgs + 1, 5):
        j = i + n_cpgs
        cand = np.where((cs[:, j] - cs[:, i]) / n_cpgs >= 1 - MAX_DROPOUT)[0]
        if len(cand) < MIN_READS or (best is not None and len(cand) <= len(best[2])):
            continue
        rows = cand[max_runs(M[cand, i:j]) <= MAX_RUN]
        if len(rows) >= MIN_READS and (best is None or len(rows) > len(best[2])):
            best = (i, j, rows)
    if best is None:
        return None
    i, j, rows = best
    return i, j, np.sort(rng.choice(rows, MIN_READS, replace=False))


def pair_dist(X):
    """normalised Hamming on shared observed sites; nan if no shared site"""
    obs = (X >= 0).astype(float)
    one = (X == 1).astype(float)
    zero = (X == 0).astype(float)
    shared = obs @ obs.T
    diff = one @ zero.T + zero @ one.T
    with np.errstate(invalid="ignore", divide="ignore"):
        D = np.where(shared > 0, diff / shared, np.nan)
    return D


def dist_var(X):
    D = pair_dist(X)
    iu = np.triu_indices(len(X), 1)
    d = D[iu]
    return np.nanvar(d)


def impute(X):
    D = pair_dist(X)
    np.fill_diagonal(D, np.inf)
    D = np.where(np.isnan(D), np.inf, D)
    Y = X.copy()
    col_major = [(1 if (X[:, c] == 1).sum() >= (X[:, c] == 0).sum() else 0) for c in range(X.shape[1])]
    for r in range(len(X)):
        nn = np.argsort(D[r])[:K_NN]
        for c in np.where(X[r] < 0)[0]:
            v = [X[q, c] for q in nn if X[q, c] >= 0 and np.isfinite(D[r, q])]
            ones = sum(v)
            if v and ones * 2 != len(v):
                Y[r, c] = 1 if ones * 2 > len(v) else 0
            else:
                Y[r, c] = col_major[c]
    return Y


def permute(X, rng):
    Y = X.copy()
    for c in range(X.shape[1]):
        rows = np.where(X[:, c] >= 0)[0]
        Y[rows, c] = X[rng.permutation(rows), c]
    return Y


def curveball(X, rng, n_trades):
    """keep row and column sums of observed cells; missing mask fixed"""
    Y = X.copy()
    n = len(Y)
    for _ in range(n_trades):
        a, b = rng.choice(n, 2, replace=False)
        both = (Y[a] >= 0) & (Y[b] >= 0)
        only_a = np.where(both & (Y[a] == 1) & (Y[b] == 0))[0]
        only_b = np.where(both & (Y[a] == 0) & (Y[b] == 1))[0]
        pool = np.concatenate([only_a, only_b])
        if len(only_a) == 0 or len(only_b) == 0:
            continue
        to_a = rng.permutation(pool)[:len(only_a)]
        Y[a, pool], Y[b, pool] = 0, 1
        Y[a, to_a], Y[b, to_a] = 1, 0
    return Y


def null_test(v_obs, null):
    sd = null.std()
    z = (v_obs - null.mean()) / sd if sd > 0 else float("nan")
    p = (1 + (null >= v_obs).sum()) / (len(null) + 1)
    return null.mean(), sd, z, p


def both_nulls(X, rng, n_perm=N_PERM):
    v = dist_var(X)
    col = null_test(v, np.array([dist_var(permute(X, rng)) for _ in range(n_perm)]))
    ff = null_test(v, np.array([dist_var(curveball(X, rng, 5 * len(X))) for _ in range(n_perm)]))
    return v, col, ff


def selftest():
    rng = np.random.default_rng(2)
    n, m = 20, 200

    def noise(X, err=0.03, drop=0.06):
        X = np.where(rng.random(X.shape) < err, 1 - X, X)
        X[rng.random(X.shape) < drop] = -1
        return X

    def clones(f, n_diff, sizes):
        g = f.copy()
        k = rng.choice(m, n_diff, replace=False)
        g[k] = 1 - g[k]
        return np.vstack([np.tile(f, (sizes[0], 1)), np.tile(g, (sizes[1], 1))])

    p = rng.random(m) * 0.8 + 0.1
    off = rng.normal(0, 0.15, n)[:, None]
    f = (rng.random(m) < 0.6).astype(int)
    cases = [
        ("independent CpGs", (rng.random((n, m)) < p).astype(int)),
        ("per-read offset only", (rng.random((n, m)) < np.clip(p + off, 0, 1)).astype(int)),
        ("monoclonal + 3% error", np.tile(f, (n, 1))),
        ("two clones 70/30, 10% CpG differ", clones(f, 20, (14, 6))),
        ("two clones 50/50, 5% CpG differ", clones(f, 10, (10, 10))),
    ]
    for name, X in cases:
        v, col, ff = both_nulls(noise(X), rng, 100)
        print(f"{name:34} z_col={col[2]:6.1f} z_ff={ff[2]:6.1f} p_ff={ff[3]:.3f}")


def main(argv):
    fixed = None
    if "--fixed" in argv:
        k = argv.index("--fixed")
        fixed = int(argv[k + 1])
        del argv[k:k + 2]
    bam_path, label, out = argv[:3]
    mods = set((argv[3] if len(argv) > 3 else "m").split(","))
    cpgs, by_hp = load_reads(bam_path, mods)
    rng = np.random.default_rng(0)
    cols = ["label", "hp", "win_start", "win_end", "cpg_from", "cpg_to", "n_cpgs", "n_reads",
            "dropout_frac", "mean_meth", "dist_var", "null_mean", "null_sd", "z", "p_perm",
            "ff_null_mean", "ff_null_sd", "z_ff", "p_ff", "top_minor_frac", "k5_fracs"]
    with open(out, "w") as fh, open(out.rsplit(".tsv", 1)[0] + ".clusters.tsv", "w") as ch:
        fh.write("\t".join(cols) + "\n")
        ch.write("label\thp\twin_start\tread\tc2\tc5\n")
        for hp in sorted(by_hp):
            reads = by_hp[hp]
            for ws in range(START, END - WIN + STEP, STEP):
                we = min(ws + WIN, END)
                lo, hi = np.searchsorted(cpgs, ws), np.searchsorted(cpgs, we)
                if hi - lo < MIN_CPGS:
                    continue
                sub = [(nm, c) for nm, c in reads if any(lo <= i < hi for i in c)]
                if len(sub) < MIN_READS:
                    continue
                M = np.full((len(sub), hi - lo), -1, dtype=int)
                for r, (nm, c) in enumerate(sub):
                    for i, v in c.items():
                        if lo <= i < hi:
                            M[r, i - lo] = v
                b = best_matrix(M) if fixed is None else fixed_matrix(M, fixed, rng)
                if b is None:
                    continue
                i, j, rows = b
                X = M[rows, i:j]
                v_obs, (nm_, sd, z, p), (fm, fsd, zf, pf) = both_nulls(X, rng)
                Y = impute(X)
                Z = linkage(Y, method="average", metric="hamming")
                c2 = fcluster(Z, 2, criterion="maxclust")
                minor = min(np.bincount(c2)[1:]) / len(c2) if c2.max() > 1 else 0.0
                c5 = fcluster(Z, 5, criterion="maxclust")
                k5 = sorted((np.bincount(c5)[1:] / len(c5)).round(3), reverse=True)
                obs = X[X >= 0]
                fh.write("\t".join(map(str, [
                    label, f"HP{hp}", ws, we, int(cpgs[lo + i]), int(cpgs[lo + j - 1]), j - i, len(rows),
                    f"{(X < 0).mean():.3f}", f"{obs.mean():.3f}", f"{v_obs:.5f}", f"{nm_:.5f}",
                    f"{sd:.5f}", f"{z:.2f}", f"{p:.4f}", f"{fm:.5f}", f"{fsd:.5f}", f"{zf:.2f}", f"{pf:.4f}",
                    f"{minor:.3f}", ",".join(map(str, k5))])) + "\n")
                for r, a2, a5 in zip(rows, c2, c5):
                    ch.write(f"{label}\tHP{hp}\t{ws}\t{sub[r][0]}\t{a2}\t{a5}\n")
            print(label, f"HP{hp}", "reads", len(reads), file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main(sys.argv[1:])
