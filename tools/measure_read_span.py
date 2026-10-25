"""Measure the reference span of ONT reads, for the longbulksim read-length model.

Takes primary, mapped reads (MAPQ >= 1) that START inside each region, so every read is
counted once and the sample is not length-biased. Writes the span distribution as 1,001
quantiles (q = 0.000, 0.001, ..., 1.000); longbulksim draws read spans from them.

Usage: python3 tools/measure_read_span.py CRAM OUT.tsv [--ref FASTA] [--region chr1:20000000-60000000 ...]
"""
import argparse

import numpy as np
import pysam

REGIONS = ["chr1:20000000-60000000", "chr5:40000000-80000000", "chr12:30000000-70000000"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cram")
    ap.add_argument("out")
    ap.add_argument("--ref", default="/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta")
    ap.add_argument("--region", nargs="+", default=REGIONS)
    a = ap.parse_args()
    spans = []
    with pysam.AlignmentFile(a.cram, reference_filename=a.ref, threads=4) as f:
        for reg in a.region:
            chrom, rng = reg.split(":")
            start, end = map(int, rng.split("-"))
            for r in f.fetch(chrom, start, end):
                if (r.is_unmapped or r.is_secondary or r.is_supplementary
                        or r.mapping_quality < 1 or not start <= r.reference_start < end):
                    continue
                spans.append(r.reference_length)
    spans = np.asarray(spans)
    q = np.linspace(0, 1, 1001)
    with open(a.out, "w") as fh:
        fh.write(f"# source\t{a.cram}\n# regions\t{','.join(a.region)}\n# n_reads\t{len(spans)}\n"
                 f"# mean_span\t{spans.mean():.1f}\n")
        fh.write("quantile\tspan\n")
        fh.writelines(f"{qi:.3f}\t{int(v)}\n" for qi, v in zip(q, np.quantile(spans, q)))
    l50 = np.sort(spans)[::-1]
    n50 = l50[np.searchsorted(np.cumsum(l50), l50.sum() / 2)]
    print(f"n={len(spans)} mean={spans.mean():.0f} median={np.median(spans):.0f} N50={n50}")


if __name__ == "__main__":
    main()
