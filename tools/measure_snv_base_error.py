#!/usr/bin/env python3
"""Measure the ONT base error rate at somatic SNV sites in a normal sample (longbulksim base_error).

HCC1395BL (normal) carries none of the SEQC2 HighConf somatic SNVs of HCC1395, so every read
that shows the somatic alt base there is a sequencing (or alignment) error. Per site: reads with
the ref base, the alt base and another base. Pileup filters are the same as
tools/hcc1395_hp_split.py (MAPQ >= 20, BQ >= 7, primary reads only).

  ref_to_alt   alt / (ref + alt + other): ref read as the specific alt base
  any_mismatch (alt + other) / (ref + alt + other): ref read as any other base

Usage: python3 -I tools/measure_snv_base_error.py [CRAM] [OUT_TSV]
"""
import os
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hcc1395_hp_split as H  # noqa: E402
import seqc2_hcc1395_purity as P  # noqa: E402

CRAM = sys.argv[1] if len(sys.argv) > 1 else "/big8_disk/data/HCC1395/ONT/HCC1395BL.cram"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else
           "lab_report/2026-10-25_c4_robustness/calibration/normal_snv_base_error.tsv")
MIN_DEPTH = 10


def main():
    H.CRAM = CRAM
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sites = P.load_sites()
    alt_of = {(c, p): a for c, p, _, a in sites}
    sites_file = OUT.parent / "sites.tmp.tsv"
    sites_file.write_text("".join(f"{c}\t{p}\n" for c, p, _, _ in sites))
    res = {}
    with ProcessPoolExecutor(len(H.CHROMS)) as ex:
        for r in ex.map(H.pileup_chrom, [(c, str(sites_file), alt_of) for c in H.CHROMS]):
            res.update(r)
    sites_file.unlink()
    rows, tot = [], {"ref": 0, "alt": 0, "other": 0}
    for (c, p), reads in sorted(res.items(), key=lambda kv: (H.CHROMS.index(kv[0][0]), int(kv[0][1]))):
        n = {k: 0 for k in tot}
        for allele, _ in reads.values():
            n[allele] += 1
        if sum(n.values()) < MIN_DEPTH:
            continue
        rows.append((c, p, n["ref"], n["alt"], n["other"]))
        for k in tot:
            tot[k] += n[k]
    with open(OUT, "w") as fh:
        fh.write("chrom\tpos\tref\talt\tother\n")
        fh.writelines("\t".join(map(str, r)) + "\n" for r in rows)
    dp = sum(tot.values())
    per_site = [r[3] / (r[2] + r[3] + r[4]) for r in rows]
    print(f"cram\t{CRAM}")
    print(f"sites_depth_ge_{MIN_DEPTH}\t{len(rows)}")
    print(f"reads\t{dp}")
    print(f"ref_to_alt_pooled\t{tot['alt'] / dp:.5f}")
    print(f"any_mismatch_pooled\t{(tot['alt'] + tot['other']) / dp:.5f}")
    print(f"ref_to_alt_site_median\t{statistics.median(per_site):.5f}")
    print(f"ref_to_alt_site_mean\t{statistics.mean(per_site):.5f}")
    q = statistics.quantiles(per_site, n=100)
    print(f"ref_to_alt_site_p90\t{q[89]:.5f}")
    print(f"ref_to_alt_site_p99\t{q[98]:.5f}")
    print(f"sites_ref_to_alt_gt_0.05\t{sum(x > 0.05 for x in per_site)}")


if __name__ == "__main__":
    main()
