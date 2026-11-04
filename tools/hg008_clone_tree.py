#!/usr/bin/env python3
"""Step 1 of the HG008 clone-tree analysis: SNV presence patterns across the 8 single-cell clones.

Input: each clone's DeepSomatic VCF (PacBio Revio vs HG008-N-P, PASS biallelic SNVs).
A clone "has" an SNV when it is called with VAF >= MIN_VAF (clones are single-cell derived, so real
SNVs sit near VAF 0.5 or 1.0). An SNV with a weak call (0 < VAF < MIN_VAF) in any clone is set
aside as ambiguous, so a weak call never counts as presence or absence.

Output (OUT_DIR):
  snv_patterns.tsv   chrom pos ref alt pattern vafs gt ps   (one row per unambiguous SNV)
  pattern_counts.tsv pattern n_snv                           (pattern = clones carrying the SNV)

Usage: python3 -I tools/hg008_clone_tree.py HG008_DIR OUT_DIR
"""
import collections
import gzip
import sys
from pathlib import Path

HG008 = Path(sys.argv[1])
OUT = Path(sys.argv[2])
CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
MIN_VAF = 0.25


def clone_vcf(name):
    hits = list((HG008 / "clones").rglob(f"HG008T-{name}.deepsomatic.vcf.gz"))
    assert len(hits) == 1, (name, hits)
    return hits[0]


def read_calls(path):
    calls = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.rstrip("\n").split("\t")
            if f[6] != "PASS" or len(f[3]) != 1 or len(f[4]) != 1:
                continue
            fmt = dict(zip(f[8].split(":"), f[9].split(":")))
            calls[(f[0], int(f[1]), f[3], f[4])] = (float(fmt["VAF"]), fmt["GT"], fmt.get("PS", "."))
    return calls


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    calls = {c: read_calls(clone_vcf(c)) for c in CLONES}
    keys = sorted(set().union(*calls.values()), key=lambda k: (k[0], k[1]))
    counts = collections.Counter()
    n_ambiguous = 0
    with open(OUT / "snv_patterns.tsv", "w") as out:
        out.write("chrom\tpos\tref\talt\tpattern\tvafs\tgt\tps\n")
        for k in keys:
            got = [calls[c].get(k) for c in CLONES]
            if any(g and g[0] < MIN_VAF for g in got):
                n_ambiguous += 1
                continue
            pattern = ",".join(c for c, g in zip(CLONES, got) if g)
            counts[pattern] += 1
            vafs = ",".join(f"{g[0]:.2f}" if g else "." for g in got)
            gts = ",".join(g[1] if g else "." for g in got)
            pss = ",".join(g[2] if g else "." for g in got)
            out.write(f"{k[0]}\t{k[1]}\t{k[2]}\t{k[3]}\t{pattern}\t{vafs}\t{gts}\t{pss}\n")
    with open(OUT / "pattern_counts.tsv", "w") as out:
        out.write("pattern\tn_clones\tn_snv\n")
        for p, n in counts.most_common():
            out.write(f"{p}\t{p.count(',') + 1}\t{n}\n")
    print(f"SNVs: {len(keys)}; ambiguous (weak call in some clone): {n_ambiguous}")


if __name__ == "__main__":
    main()
