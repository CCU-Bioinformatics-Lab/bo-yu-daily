"""Truncal (clonal) share of HCC1395 somatic SNVs from SEQC2 truth VAF and ASCAT consensus CN.

u = TVAF * (p*CN + 2*(1-p)) / p is the mean number of mutant copies per tumour cell.
At 1+1 sites the multiplicity is 1, so CCF = u with no guessing; that is the main estimate.
Other CN states use m = clip(round(u), 1, major) and are reported only as a cross-check.
TVAF combines the 21 SEQC2 WGS replicates and 3 aligners (very deep). p defaults to 0.99 (SEQC2 paper).

Usage: python3 tools/seqc2_hcc1395_clonality.py OUT_DIR [--purity 0.99]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from seqc2_hcc1395_purity import SNV_VCF, ascat_consensus, load_sites  # noqa: E402

THRESHOLDS = (0.7, 0.8, 0.9)


def tvaf():
    out = subprocess.run(["bcftools", "query", "-i", 'FILTER~"HighConf"', "-f", "%CHROM\t%POS\t%INFO/TVAF\n",
                          str(SNV_VCF)], capture_output=True, text=True, check=True).stdout
    return {(c, p): float(v) for c, p, v in (l.split("\t") for l in out.splitlines()) if v != "."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--purity", type=float, default=0.99)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = a.purity

    sites = load_sites()
    cons = ascat_consensus(sites)
    vaf = tvaf()
    rows = []
    for (ch, pos), (tot, minor) in cons.items():
        if (ch, pos) not in vaf or tot == 0:
            continue
        u = vaf[(ch, pos)] * (p * tot + 2 * (1 - p)) / p
        major = tot - minor
        m = int(min(max(round(u), 1), max(major, 1)))
        rows.append((ch, int(pos), tot, minor, vaf[(ch, pos)], u, m, u / m))
    with open(out / "snv_ccf.tsv", "w") as fh:
        fh.write("chrom\tpos\ttotal_cn\tminor_cn\ttvaf\tmutant_copies\tmultiplicity\tccf\n")
        fh.writelines("\t".join(map(str, r[:4])) + f"\t{r[4]:.4f}\t{r[5]:.3f}\t{r[6]}\t{r[7]:.3f}\n" for r in rows)

    def share(ccf):
        ccf = np.asarray(ccf)
        return {"n": int(len(ccf)), "median_ccf": float(np.median(ccf)),
                **{f"ccf>={t}": float((ccf >= t).mean()) for t in THRESHOLDS},
                "hist_0.1": np.histogram(np.clip(ccf, 0, 1.5), bins=np.arange(0, 1.51, 0.1))[0].tolist()}

    one_one = [r[7] for r in rows if r[2] == 2 and r[3] == 1]
    res = {"purity": p, "n_highconf": len(sites), "n_with_cn_and_vaf": len(rows),
           "cn_1+1": share(one_one), "all_cn": share([r[7] for r in rows])}
    by_state = {}
    for r in rows:
        by_state.setdefault(f"{r[2] - r[3]}+{r[3]}", []).append(r[7])
    res["by_state"] = {k: share(v) for k, v in sorted(by_state.items(), key=lambda kv: -len(kv[1])) if len(v) >= 500}
    (out / "result.json").write_text(json.dumps(res, indent=1))
    print(f"purity {p}; HighConf {len(sites)}, with CN+VAF {len(rows)}")
    for k in ("cn_1+1", "all_cn"):
        s = res[k]
        print(f"{k:8s} n {s['n']:6d} median CCF {s['median_ccf']:.2f}  " +
              "  ".join(f">={t}: {s[f'ccf>={t}']:.1%}" for t in THRESHOLDS))
        print("         hist(0-1.5 by 0.1):", s["hist_0.1"])
    for k, s in res["by_state"].items():
        print(f"  state {k:5s} n {s['n']:6d} median {s['median_ccf']:.2f} >=0.8 {s['ccf>=0.8']:.1%}")


if __name__ == "__main__":
    main()
