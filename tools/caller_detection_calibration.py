#!/usr/bin/env python3
"""Calibrate ONT somatic SNV caller sensitivity against SEQC2 HCC1395 truth.

For each SEQC2 v1.2.1 HighConf SNV, count alt reads and depth in the same tumour CRAM that the
callers saw (CASTLE HCC1395, bcftools mpileup -q 20 -Q 7 -B), and mark whether ClairS
(v0.4.0 ssrs) and DeepSomatic report it as a PASS SNV with the same ALT. Then tabulate the
detection rate by alt count and depth, and fit logit P(call) = b0 + b1*log(alt) + b2*log(depth)
on sites with alt >= 1.

Usage: python3 tools/caller_detection_calibration.py OUT_DIR
Writes OUT_DIR/tables/{site_calls.tsv, detection_by_alt.tsv, detection_by_alt_depth.tsv,
logistic_fit.tsv}.
"""
import collections
import gzip
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seqc2_hcc1395_purity as P  # noqa: E402

TUMOUR = "/big8_disk/Google_somatic_data/bams/HCC1395/HCC1395_Tumor_ONT.GRCh38.sorted.cram"
CALLERS = {
    "clairs": "/big8_disk/Somatic_calling/HCC1395/ClairS/v0.4.0-ssrs/output.vcf.gz",
    "deepsomatic": "/big8_disk/Somatic_calling/HCC1395/DeepSomatic/output2/deepsomatic_HCC1395.vcf.gz",
}
CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]
ALT_BINS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50, 10_000]
DEPTH_BINS = [0, 40, 70, 100, 150, 10_000]


def pileup_chrom(args):
    chrom, sites_file, cram = args
    cmd = (f"bcftools mpileup -f {P.REF} -R {sites_file} -a FORMAT/AD -B -q 20 -Q 7 "
           f"--max-depth 5000 -I -Ou {cram} | bcftools query -f '%CHROM\\t%POS\\t%REF\\t%ALT\\t[%AD]\\n'")
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        ch, pos, ref, alts, ad = line.split("\t")
        res[(ch, pos)] = dict(zip([ref] + alts.split(","), (int(x) for x in ad.split(","))))
    return res


def pileup_sites(sites, cram, workdir, tag=""):
    """{(chrom, pos): {allele: reads}} over SEQC2 sites, one bcftools job per chromosome."""
    files = {}
    for ch in CHROMS:  # one sites file per chrom: bcftools refuses -R together with -r
        lines = "".join(f"{c}\t{p}\n" for c, p, _, _ in sites if c == ch)
        if lines:  # SEQC2 HighConf has no chrX sites; bcftools fails on an empty file
            files[ch] = Path(workdir) / f"sites{tag}_{ch}.tsv"
            files[ch].write_text(lines)
    counts = {}
    with ThreadPoolExecutor(len(files)) as ex:
        for r in ex.map(pileup_chrom, [(c, str(f), cram) for c, f in files.items()]):
            counts.update(r)
    for f in files.values():
        f.unlink()
    return counts


def pass_snvs(vcf):
    out = set()
    with gzip.open(vcf, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.split("\t", 8)
            if f[6] == "PASS" and len(f[3]) == 1 and len(f[4]) == 1:
                out.add((f[0], f[1], f[4]))
    return out


def fit_logistic(alt, depth, y):
    X = np.column_stack([np.ones(len(alt)), np.log(alt), np.log(depth)])

    def nll(b):
        z = X @ b
        return np.sum(np.logaddexp(0, z) - y * z)

    return minimize(nll, np.zeros(3), method="BFGS").x


def rate_table(rows, key, bins):
    out = []
    for lo, hi in zip(bins, bins[1:]):
        sel = [r for r in rows if lo <= r[key] < hi]
        if sel:
            out.append([f"{lo}-{hi - 1}" if hi - lo > 1 else str(lo), len(sel),
                        *(f"{np.mean([r[c] for r in sel]):.3f}" for c in CALLERS)])
    return out


def write(path, header, rows):
    path.write_text("\t".join(header) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows))


def main():
    out = Path(sys.argv[1])
    tab = out / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    sites = P.load_sites()
    counts = pileup_sites(sites, TUMOUR, out)
    calls = {k: pass_snvs(v) for k, v in CALLERS.items()}

    rows = []
    for c, p, ref, alt in sites:
        ad = counts.get((c, p))
        if not ad:
            continue
        a, d = ad.get(alt, 0), sum(ad.values())
        rows.append({"chrom": c, "pos": p, "alt": a, "depth": d,
                     **{k: int((c, p, alt) in s) for k, s in calls.items()}})
    write(tab / "site_calls.tsv", ["chrom", "pos", "alt", "depth", *CALLERS],
          [[r["chrom"], r["pos"], r["alt"], r["depth"], *(r[k] for k in CALLERS)] for r in rows])
    write(tab / "detection_by_alt.tsv", ["alt_reads", "n_sites", *CALLERS], rate_table(rows, "alt", ALT_BINS))
    tbl = []
    for lo, hi in zip(DEPTH_BINS, DEPTH_BINS[1:]):
        sub = [r for r in rows if lo <= r["depth"] < hi]
        for line in rate_table(sub, "alt", ALT_BINS):
            tbl.append([f"{lo}-{hi - 1}", *line])
    write(tab / "detection_by_alt_depth.tsv", ["depth", "alt_reads", "n_sites", *CALLERS], tbl)

    fit = []
    use = [r for r in rows if r["alt"] >= 1 and r["depth"] >= 1]
    alt = np.array([r["alt"] for r in use], float)
    dep = np.array([r["depth"] for r in use], float)
    for k in CALLERS:
        b = fit_logistic(alt, dep, np.array([r[k] for r in use], float))
        fit.append([k, *(f"{x:.4f}" for x in b), len(use)])
    write(tab / "logistic_fit.tsv", ["caller", "b0", "b_log_alt", "b_log_depth", "n_sites"], fit)
    summary = [f"sites with pileup\t{len(rows)}",
               f"median depth\t{np.median([r['depth'] for r in rows]):.0f}"]
    summary += [f"{k} recall (all truth)\t{np.mean([r[k] for r in rows]):.3f}" for k in CALLERS]
    summary += [f"{k} recall (alt >= 3)\t{np.mean([r[k] for r in rows if r['alt'] >= 3]):.3f}" for k in CALLERS]
    (tab / "summary.txt").write_text("\n".join(summary) + "\n")
    for f in ("summary.txt", "detection_by_alt.tsv", "logistic_fit.tsv"):
        print(f"### {f}\n{(tab / f).read_text()}")


if __name__ == "__main__":
    main()
