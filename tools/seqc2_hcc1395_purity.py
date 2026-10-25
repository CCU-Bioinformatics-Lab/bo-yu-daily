#!/usr/bin/env python3
"""用 SEQC2 HCC1395 somatic SNV 真值，量測本機 ONT subsample（tX_nY）的實測 purity。

原理：tumor total CN = k 的位點，subsample 與同系列 t50_n00（100% tumor）的合併 VAF 比值
    r = p*k / (p*k + 2*(1-p))，k = 2 時 r = p（細胞 purity）。
k 由 SEQC2 21 份 ASCAT 重複的共識決定。結果寫到 OUT_DIR/tables/。tumor DNA（read）比例 d = p*psi / (p*psi + 2*(1-p))。

用法：python3 -I tools/seqc2_hcc1395_purity.py [OUT_DIR]
"""
import collections
import glob
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "lab_report/2026-10-25_seqc2_hcc1395_measured_purity")
REF = "/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
SEQC2 = Path("/big8_disk/boyu114/benchmark_data/SEQC2")
SNV_VCF = SEQC2 / "release_v1.2.1/high-confidence_sSNV_in_HC_regions_v1.2.1.vcf.gz"
ASCAT = sorted(glob.glob(str(SEQC2 / "CNV/WGS/ascat/*.caveman.csv")))
SERIES = {
    "ONT": ["t00_n25", "t10_n40", "t20_n30", "t30_n20", "t40_n10", "t50_n00"],
    "ONT_Dorado": ["t00_n25", "t7_n29", "t19_n29", "t30_n20", "t40_n10", "t50_n00"],
}
CN_AGREE = 18          # 至少 18/21 份 ASCAT 同意，才採用該位點的 tumor total CN
PSI_SEQC2_PAPER = 2.85  # Fang 2021 報的 ploidy
N_BOOT = 500


def cram(series, label):
    return f"/big8_disk/data/HCC1395/{series}/subsample/{label}/HCC1395_{label}.cram"


def nominal(label):
    x, y = (int(v[1:]) for v in label.split("_"))
    return x / (x + y)


def load_sites():
    out = subprocess.run(["bcftools", "query", "-i", 'FILTER~"HighConf"', "-f", "%CHROM\t%POS\t%REF\t%ALT\n", str(SNV_VCF)],
                         capture_output=True, text=True, check=True).stdout
    return [tuple(l.split("\t")) for l in out.splitlines()]


def ascat_consensus(sites):
    """回傳 {(chrom,pos): (tumor_total, tumor_minor)}，只收 >= CN_AGREE 份一致的位點。"""
    by_site = collections.defaultdict(collections.Counter)
    for f in ASCAT:
        segs = collections.defaultdict(list)
        for line in open(f):
            _, ch, a, b, _, _, tt, tm = line.strip().split(",")
            segs[ch].append((int(a), int(b), int(tt), int(tm)))
        for ch in segs:
            segs[ch].sort()
        for ch, pos, _, _ in sites:
            p = int(pos)
            for a, b, tt, tm in segs.get(ch, []):  # 每條染色體區段數少，線性掃描即可
                if a <= p <= b:
                    by_site[(ch, pos)][(tt, tm)] += 1
                    break
    cons = {}
    for k, c in by_site.items():
        tot = collections.Counter()
        for (tt, _), n in c.items():
            tot[tt] += n
        tt, n = tot.most_common(1)[0]
        if n >= CN_AGREE:
            tm = max((m for (t, m) in c if t == tt), key=lambda m: c[(tt, m)])
            cons[k] = (tt, tm)
    return cons


def pileup(path, sites_file):
    """回傳 {(chrom,pos): (alt_count, depth)}；alt 只算 SEQC2 指定的 ALT 鹼基。"""
    cmd = (f"bcftools mpileup -f {REF} -R {sites_file} -a FORMAT/AD -B -q 20 -Q 7 --max-depth 5000 -I -Ou {path} "
           f"| bcftools query -f '%CHROM\\t%POS\\t%REF\\t%ALT\\t[%AD]\\n'")
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        ch, pos, ref, alts, ad = line.split("\t")
        alleles = [ref] + alts.split(",")
        counts = dict(zip(alleles, (int(x) for x in ad.split(","))))
        res[(ch, pos)] = counts
    return res


def ratio(keys, sub, pure):
    a_s = sum(sub[k][0] for k in keys); d_s = sum(sub[k][1] for k in keys)
    a_p = sum(pure[k][0] for k in keys); d_p = sum(pure[k][1] for k in keys)
    return (a_s / d_s) / (a_p / d_p) if d_s and d_p and a_p else float("nan")


def p_from_r(r, k):
    return 2 * r / (k * (1 - r) + 2 * r)


def d_from_p(p, psi):
    return p * psi / (p * psi + 2 * (1 - p))


def main():
    TAB = OUT / "tables"
    TAB.mkdir(parents=True, exist_ok=True)
    sites = load_sites()
    alt_of = {(c, p): a for c, p, _, a in sites}
    sites_file = OUT / "sites.tsv"  # 中間檔，結束時刪除
    sites_file.write_text("".join(f"{c}\t{p}\n" for c, p, _, _ in sites))
    cons = ascat_consensus(sites)

    # ASCAT autosome ploidy（長度加權平均，取 21 份中位數）
    psis = []
    for f in ASCAT:
        tot = s = 0
        for line in open(f):
            _, ch, a, b, _, _, tt, _ = line.strip().split(",")
            if ch in ("chrX", "chrY"):
                continue
            tot += int(b) - int(a); s += (int(b) - int(a)) * int(tt)
        psis.append(s / tot)
    psi_ascat = sorted(psis)[len(psis) // 2]

    jobs = [(s, l) for s, ls in SERIES.items() for l in ls]
    with ThreadPoolExecutor(len(jobs)) as ex:
        raw = dict(zip(jobs, ex.map(lambda j: pileup(cram(*j), sites_file), jobs)))
    counts = {}
    for j, res in raw.items():
        counts[j] = {k: (c.get(alt_of[k], 0), sum(c.values())) for k, c in res.items()}

    rows = []
    cn_rows = []
    rng = random.Random(1)
    for series, labels in SERIES.items():
        pure = counts[(series, "t50_n00")]
        for label in labels:
            sub = counts[(series, label)]
            common = [k for k in sub if k in pure and pure[k][1] >= 10 and sub[k][1] >= 5]
            by_cn = collections.defaultdict(list)
            for k in common:
                if k in cons:
                    by_cn[cons[k][0]].append(k)
            k2 = by_cn[2]
            p2 = ratio(k2, sub, pure)
            boot = sorted(ratio([rng.choice(k2) for _ in k2], sub, pure) for _ in range(N_BOOT))
            lo, hi = boot[int(0.025 * N_BOOT)], boot[int(0.975 * N_BOOT) - 1]
            vaf_all = sum(sub[k][0] for k in common) / max(1, sum(sub[k][1] for k in common))
            depth = sorted(sub[k][1] for k in common)[len(common) // 2] if common else 0
            rows.append((series, label, f"{nominal(label):.3f}", len(k2), depth, f"{vaf_all:.4f}",
                         f"{p2:.3f}", f"{lo:.3f}", f"{hi:.3f}",
                         f"{d_from_p(p2, psi_ascat):.3f}", f"{d_from_p(p2, PSI_SEQC2_PAPER):.3f}"))
            for cn in sorted(by_cn):
                if len(by_cn[cn]) < 200 or cn == 0:
                    continue
                r = ratio(by_cn[cn], sub, pure)
                cn_rows.append((series, label, cn, len(by_cn[cn]), f"{r:.3f}", f"{p_from_r(r, cn):.3f}"))

    hdr = ["series", "label", "nominal_fraction", "n_sites_CN2", "median_depth", "pooled_VAF_all_sites",
           "purity_cell_CN2", "ci95_lo", "ci95_hi", f"tumor_DNA_frac_psi{psi_ascat:.2f}", f"tumor_DNA_frac_psi{PSI_SEQC2_PAPER}"]
    with open(TAB / "measured_purity.tsv", "w") as f:
        f.write("\t".join(hdr) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows))
    with open(TAB / "purity_by_cn.tsv", "w") as f:
        f.write("series\tlabel\ttumor_total_CN\tn_sites\tVAF_ratio_vs_t50\tpurity_from_this_CN\n")
        f.write("".join("\t".join(map(str, r)) + "\n" for r in cn_rows))
    cnc = collections.Counter(v[0] for v in cons.values())
    with open(TAB / "site_cn_summary.tsv", "w") as f:
        f.write(f"# SNV sites (HighConf)\t{len(sites)}\n# sites with ASCAT consensus (>= {CN_AGREE}/21)\t{len(cons)}\n")
        f.write(f"# ASCAT autosome ploidy median\t{psi_ascat:.3f}\n tumor_total_CN\tn_sites\n")
        f.write("".join(f"{k}\t{n}\n" for k, n in sorted(cnc.items())))
    for p in ("site_cn_summary.tsv", "measured_purity.tsv", "purity_by_cn.tsv"):
        print(f"### {p}\n{(TAB / p).read_text()}")
    sites_file.unlink()


if __name__ == "__main__":
    main()
