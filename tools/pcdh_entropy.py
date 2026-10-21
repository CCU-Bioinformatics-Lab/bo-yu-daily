"""PCDH 10-CpG barcode entropy from ONT MM/ML tags.

Adapted from the B09 short-read EM-seq 10-mer entropy, not B09's long-read
method (that is pcdh_longread_matrix.py). Differences from B09: windows are
non-overlapping 10-CpG tiles (B09: every CpG start), and each window is
downsampled to N_SUB reads (B09: all reads above a depth floor).

usage: python3 pcdh_entropy.py CRAM LABEL OUT_TSV [MODS] [--by-hp]

MODS: comma-separated mod codes whose probabilities are summed per CpG
(default "m"; "m,h" = 5mC+5hmC, comparable to EM-seq/bisulfite).
--by-hp: split reads by HP tag (HP:i:1 / HP:z:1-1 -> HP1, ...; untagged
reads dropped) and write one row set per HP, labelled LABEL_HP<n>.
Assumes one PS block over the region; warns on stderr if there are more.

Needs pysam + numpy (do not run with python3 -I: numpy is in user site-packages).
Assumes MM mode '?' (unlisted CpG = missing). Output: one row per
non-overlapping 10-CpG window with >= N_SUB fully called reads.
First used in lab_report/2026-10-20_hcc1395_pcdh_entropy/.
"""
import sys, math, random
from collections import Counter
import numpy as np
import pysam

REF = "/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
CHROM, START, END = "chr5", 140_780_000, 141_520_000   # PCDHA1..PCDHGC5 (GRCh38, approx)
K = 10            # CpGs per barcode
N_SUB = 20        # reads per window after downsampling (paper min 10-mer coverage 20X)
N_REP = 20
MIN_MAPQ = 20
P_HI, P_LO = 0.8, 0.2   # call confidence; between = missing

BY_HP = "--by-hp" in sys.argv
args = [a for a in sys.argv[1:] if a != "--by-hp"]
cram, label, out = args[:3]
MODS = set((args[3] if len(args) > 3 else "m").split(","))
fa = pysam.FastaFile(REF)
seq = fa.fetch(CHROM, START, END + 1).upper()
cpgs = [START + i for i in range(len(seq) - 1) if seq[i:i + 2] == "CG"]
cpg_idx = {p: i for i, p in enumerate(cpgs)}

# per group (HP or all): list of per-read dict cpg_index -> 0/1
groups = {}
ps_seen = Counter()
bam = pysam.AlignmentFile(cram, reference_filename=REF)
for r in bam.fetch(CHROM, START, END):
    if r.is_secondary or r.is_supplementary or r.mapping_quality < MIN_MAPQ:
        continue
    group = label
    if BY_HP:
        if not r.has_tag("HP"):
            continue
        group = f"{label}_HP{str(r.get_tag('HP')).split('-')[0]}"
        if r.has_tag("PS"):
            ps_seen[r.get_tag("PS")] += 1
    mb = r.modified_bases
    if not mb:
        continue
    q2r = dict(r.get_aligned_pairs(matches_only=True))
    probs = Counter()
    for (base, strand, mod), lst in mb.items():
        if mod not in MODS:
            continue
        for qpos, ml in lst:
            probs[qpos] += (ml + 0.5) / 256
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
        groups.setdefault(group, []).append(calls)
bam.close()
if len(ps_seen) > 1:
    print("WARNING: multiple PS blocks", dict(ps_seen), file=sys.stderr)

def entropy(patterns):
    n = len(patterns)
    return -sum(c / n * math.log2(c / n) for c in Counter(patterns).values())

rng = random.Random(0)
with open(out, "w") as fh:
    fh.write("label\twin_start\twin_end\tn_reads\tmean_meth\tentropy_sub20\tn_distinct_sub20\ttop_barcode_frac\n")
    for group in sorted(groups):
        reads = groups[group]
        for w in range(0, len(cpgs) - K + 1, K):
            idx = range(w, w + K)
            pats = []
            for c in reads:
                if all(i in c for i in idx):
                    pats.append("".join(str(c[i]) for i in idx))
            if len(pats) < N_SUB:
                continue
            ents, nd = [], []
            for _ in range(N_REP):
                s = rng.sample(pats, N_SUB)
                ents.append(entropy(s)); nd.append(len(set(s)))
            meth = np.mean([int(ch) for p in pats for ch in p])
            top = Counter(pats).most_common(1)[0][1] / len(pats)
            fh.write(f"{group}\t{cpgs[w]}\t{cpgs[w+K-1]}\t{len(pats)}\t{meth:.3f}\t"
                     f"{np.mean(ents):.3f}\t{np.mean(nd):.2f}\t{top:.3f}\n")
        print(group, "reads", len(reads), "cpgs", len(cpgs), file=sys.stderr)
