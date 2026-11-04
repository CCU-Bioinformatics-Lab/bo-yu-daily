#!/usr/bin/env python3
"""Validate the longbulksim caller curves on lower-purity HCC1395 subsamples.

The curves were fit on the CASTLE HCC1395 tumour (purity ~1). Here they predict the calls of
ClairS v0.4.0 ssrs and DeepSomatic v1.8.0 run on the HKU ONT subsamples t10_n40 .. t50_n00
(another sequencing batch; normal 25x). The BAMs those callers read are now the CRAMs under
/big8_disk/data/HCC1395/ONT/subsample/ (same reads, converted). For every SEQC2
HighConf site: alt reads and depth, observed PASS call, and the curve's P(call).

Sites are also split by their VAF in t50_n00 (purity 1): "clonal-like" (VAF >= 0.2) vs
"low-VAF". At low purity both have few alt reads; if the curve, learnt mostly from low-VAF
sites, under-predicts clonal-like sites, it overstates dropout at low purity.

Usage: python3 tools/caller_detection_validation.py OUT_DIR
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "longbulksim"))
import caller_detection_calibration as C  # noqa: E402
import seqc2_hcc1395_purity as P  # noqa: E402
from longbulksim.simulate import load_caller  # noqa: E402

BASE = "/big8_disk/mingen112/test_data/HCC1395/ONT/subsample_bam"
CRAM = "/big8_disk/data/HCC1395/ONT/subsample"
LABELS = {"t10_n40": 0.153, "t20_n30": 0.321, "t30_n20": 0.513, "t40_n10": 0.737, "t50_n00": 1.0}
VCF = {"clairs": "{b}/{t}/clairS/v0_4_0/ont_r10_dorado_sup_5khz_ssrs/output.vcf.gz",
       "deepsomatic": "{b}/{t}/deepSomatic/v1_8_0/output.vcf.gz"}
ALT_BINS = [1, 3, 5, 8, 10, 15, 20, 30, 10_000]
CLONAL_VAF = 0.2


def prob(coef, alt, depth):
    alt, depth = np.asarray(alt, float), np.asarray(depth, float)
    z = np.full(len(alt), -np.inf)
    ok = alt > 0
    z[ok] = coef[0] + coef[1] * np.log(alt[ok]) + coef[2] * np.log(depth[ok])
    return 1 / (1 + np.exp(-z))


def main():
    out = Path(sys.argv[1])
    tab = out / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    sites = P.load_sites()
    coef = {c: load_caller(c) for c in VCF}
    data = {}
    for t in LABELS:
        counts = C.pileup_sites(sites, f"{CRAM}/{t}/HCC1395_{t}.cram", out, tag=f"_{t}")
        calls = {c: C.pass_snvs(v.format(b=BASE, t=t)) for c, v in VCF.items()}
        rows = []
        for c, p, _, a in sites:
            ad = counts.get((c, p))
            if ad:
                rows.append((c, p, ad.get(a, 0), sum(ad.values()),
                             *(int((c, p, a) in calls[k]) for k in VCF)))
        data[t] = rows
        print(f"{t}: {len(rows)} sites", flush=True)
    pure = {(r[0], r[1]): r[2] / r[3] for r in data["t50_n00"] if r[3]}

    summary, by_alt = [], []
    for t, purity in LABELS.items():
        rows = data[t]
        alt = np.array([r[2] for r in rows])
        dep = np.array([r[3] for r in rows])
        clonal = np.array([pure.get((r[0], r[1]), 0) >= CLONAL_VAF for r in rows])
        for i, k in enumerate(VCF):
            obs = np.array([r[4 + i] for r in rows])
            pred = prob(coef[k], alt, np.maximum(dep, 1))
            for name, sel in (("all", np.ones(len(rows), bool)), ("clonal_like", clonal),
                              ("low_vaf", ~clonal)):
                summary.append([t, purity, k, name, int(sel.sum()), f"{np.median(dep[sel]):.0f}",
                                f"{obs[sel].mean():.3f}", f"{pred[sel].mean():.3f}"])
            for name, sel0 in (("clonal_like", clonal), ("low_vaf", ~clonal)):
                for lo, hi in zip(ALT_BINS, ALT_BINS[1:]):
                    sel = sel0 & (alt >= lo) & (alt < hi)
                    if sel.sum() >= 20:
                        by_alt.append([t, purity, k, name, f"{lo}-{hi - 1}", int(sel.sum()),
                                       f"{obs[sel].mean():.3f}", f"{pred[sel].mean():.3f}"])
    C.write(tab / "validation_summary.tsv",
            ["label", "purity", "caller", "sites", "n", "median_depth", "observed", "predicted"], summary)
    C.write(tab / "validation_by_alt.tsv",
            ["label", "purity", "caller", "sites", "alt_reads", "n", "observed", "predicted"], by_alt)
    print((tab / "validation_summary.tsv").read_text())


if __name__ == "__main__":
    main()
