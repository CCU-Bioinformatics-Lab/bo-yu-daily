"""Write a synthetic data.tsv and clusters.tsv with N mutations (3 samples, 10 clusters, 22
chromosomes) to time --assign-loss-prob on large inputs.

Usage: python3 make_loss_input.py N OUTDIR
"""
import os
import random
import sys

n, out = int(sys.argv[1]), sys.argv[2]
os.makedirs(out, exist_ok=True)
rng = random.Random(n)
samples = ["s0", "s1", "s2"]
prev = {c: [rng.random() for _ in samples] for c in range(10)}
prev[0] = [0.95, 0.97, 0.96]
with open(os.path.join(out, "data.tsv"), "w") as d, open(os.path.join(out, "clusters.tsv"), "w") as c:
    d.write("mutation_id\tsample_id\tref_counts\talt_counts\tmajor_cn\tminor_cn\tnormal_cn\ttumour_content\tchrom\n")
    c.write("mutation_id\tsample_id\tcluster_id\tcellular_prevalence\n")
    for i in range(n):
        cl = rng.randrange(10)
        chrom = rng.randrange(1, 23)
        for j, s in enumerate(samples):
            alt = rng.randrange(0, 60)
            d.write(f"m{i}\t{s}\t{100 - alt}\t{alt}\t2\t1\t2\t1.0\t{chrom}\n")
            c.write(f"m{i}\t{s}\t{cl}\t{prev[cl][j]}\n")
