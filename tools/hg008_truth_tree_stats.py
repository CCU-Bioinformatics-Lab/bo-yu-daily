#!/usr/bin/env python3
"""HG008-T（GIAB 胰臟癌細胞株）CN／SNV 統計：檢查 hp_truth_tree.png 的事件在真實腫瘤中是否存在。

輸入：GIAB HG008 smvar V0.4 與 stvar-CNV V0.6（GRCh38）。
輸出：TSV 表格到 OUT_DIR，摘要印到 stdout。
用法：python3 -I tools/hg008_truth_tree_stats.py [DATA_DIR] [OUT_DIR]
"""
import bisect
import collections
import csv
import subprocess
import sys
from pathlib import Path

DATA = Path(sys.argv[1] if len(sys.argv) > 1 else "/big8_disk/boyu114/benchmark_data/GIAB/HG008")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "lab_report/2026-10-25_hg008_truth_tree_plausibility/tables")
CNV_BED = DATA / "stvar-CNV_V0.6/GRCh38/GRCh38_HG008-T-V0.6_somatic-CNV_PASS.draftbenchmark.calls.bed"
CNV_BEDPE = DATA / "stvar-CNV_V0.6/GRCh38/GRCh38_HG008-T-V0.6_somatic-CNV_ALL.draftbenchmark.calls.bedpe"
# tumorvariants.vcf.gz 把「沒有突變」也寫成 "."，無法分辨刪除；改用 tumor/normal 檔的 HG008-T 欄位。
SMVAR_VCF = DATA / "smvar_V0.4/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_somatic_tumornormal.vcf.gz"
FULL_VCF = DATA / "smvar_V0.4/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_full_tumornormal.vcf.gz"
SMVAR_BED = DATA / "smvar_V0.4/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_all.bed"


def cn_class(h1, h2):
    """把 (CN_HAP1, CN_HAP2) 分到真值樹用到的事件類別。"""
    lo, hi = sorted((h1, h2))
    if lo == hi == 1:
        return "balanced 1+1"
    if lo == 0 and hi == 0:
        return "homdel 0+0"
    if lo == 0 and hi == 1:
        return "LOH-deletion 1+0"
    if lo == 0 and hi == 2:
        return "cnLOH 2+0"
    if lo == 0:
        return "LOH-gain >2+0"
    if lo == hi:
        return "balanced gain"
    return "hap-specific gain"


def read_cnv():
    segs = collections.defaultdict(list)
    for row in csv.reader(open(CNV_BED), delimiter="\t"):
        chrom, s, e, tot, h1, h2, cid = row[:7]
        segs[chrom].append((int(s), int(e), int(h1), int(h2), cid))
    for v in segs.values():
        v.sort()
    return segs


def read_bed(path):
    segs = collections.defaultdict(list)
    for row in csv.reader(open(path), delimiter="\t"):
        segs[row[0]].append((int(row[1]), int(row[2])))
    for v in segs.values():
        v.sort()
    return segs


def lookup(segs, chrom, pos0):
    v = segs.get(chrom, [])
    i = bisect.bisect_right(v, (pos0, float("inf"))) - 1
    if i >= 0 and v[i][0] <= pos0 < v[i][1]:
        return v[i]
    return None


def overlap_len(a, b):
    """兩組已排序、不重疊區間的交集長度。"""
    i = j = n = 0
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        n += max(0, hi - lo)
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return n


def write_tsv(name, header, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


def main():
    cnv = read_cnv()
    bench = read_bed(SMVAR_BED)

    # 1. CN 狀態佔基因組比例（全部 PASS CNV 與 smvar benchmark 區內）
    gen, inb = collections.Counter(), collections.Counter()
    state = collections.Counter()
    for chrom, v in cnv.items():
        for s, e, h1, h2, _ in v:
            k = cn_class(h1, h2)
            gen[k] += e - s
            state[(h1 + h2, f"{h1}/{h2}", k)] += e - s
            inb[k] += overlap_len([(s, e)], bench.get(chrom, []))
    tg, tb = sum(gen.values()), sum(inb.values())
    write_tsv("cn_class_genome.tsv", ["cn_class", "Mb", "pct_genome", "Mb_in_smvar_benchmark", "pct_benchmark"],
              [(k, f"{gen[k]/1e6:.1f}", f"{100*gen[k]/tg:.1f}", f"{inb[k]/1e6:.1f}", f"{100*inb[k]/tb:.1f}")
               for k in sorted(gen, key=gen.get, reverse=True)])
    write_tsv("cn_state_genome.tsv", ["CN_total", "CN_HAP1/CN_HAP2", "cn_class", "Mb"],
              [(t, hh, k, f"{L/1e6:.2f}") for (t, hh, k), L in sorted(state.items(), key=lambda x: -x[1])])

    # 2. somatic SNV × CN 狀態 × tumor GT × TAC/TCN
    q = subprocess.run(["bcftools", "query", "-s", "HG008-T", "-i", 'TYPE="snp"', "-f", "%CHROM\t%POS\t[%GT\t%TAC\t%TCN]\n", str(SMVAR_VCF)],
                       capture_output=True, text=True, check=True).stdout
    tab = collections.Counter()
    consistency = collections.Counter()
    for line in q.splitlines():
        chrom, pos, gt, tac, tcn = line.split("\t")
        seg = lookup(cnv, chrom, int(pos) - 1)
        if seg is None:
            tab[("no CNV call", "-", gt, tac, tcn)] += 1
            continue
        _, _, h1, h2, _ = seg
        tab[(cn_class(h1, h2), f"{h1}/{h2}", gt, tac, tcn)] += 1
        # hap 標籤一致性：CN 為 0 的 haplotype，SNV GT 應為 "."
        a1, a2 = gt.split("|")
        deleted = 1 if h1 == 0 else 2 if h2 == 0 else 0
        gt_deleted = 1 if a1 == "." else 2 if a2 == "." else 0
        if deleted == gt_deleted:
            consistency["same"] += 1
        elif deleted and gt_deleted:
            consistency["swapped"] += 1
        else:
            consistency[f"CNV del hap{deleted or '-'} vs GT del hap{gt_deleted or '-'}"] += 1
    write_tsv("snv_by_cn_gt_tac.tsv", ["cn_class", "CN_HAP1/CN_HAP2", "tumor_GT", "TAC", "TCN", "n_SNV"],
              [(*k, n) for k, n in sorted(tab.items(), key=lambda x: (x[0][0], -x[1]))])
    write_tsv("hap_label_consistency.tsv", ["deleted_hap_in_CNV_vs_GT", "n_SNV"], consistency.most_common())

    # 2b. germline het SNP 在各 CN 狀態是否保留（驗證 CN_HAP 與 LOH 一致）
    q = subprocess.run(["bcftools", "query", "-f", "%CHROM\t%POS[\t%GT]\n", str(FULL_VCF)],
                       capture_output=True, text=True, check=True).stdout
    het = collections.Counter()
    for line in q.splitlines():
        chrom, pos, gn, gt = line.split("\t")
        if gn not in ("0|1", "1|0"):
            continue
        seg = lookup(cnv, chrom, int(pos) - 1)
        st = f"{seg[2]}/{seg[3]}" if seg else "no CNV call"
        a = gt.split("|")
        het[(st, "LOH" if "." in a else "het kept" if a[0] != a[1] else "hom")] += 1
    tot = collections.Counter()
    for (st, _), n in het.items():
        tot[st] += n
    write_tsv("germline_het_by_cn.tsv", ["CN_HAP1/CN_HAP2", "n_germline_het", "pct_het_kept", "pct_LOH"],
              [(st, tot[st], f"{100*het[(st, 'het kept')]/tot[st]:.1f}", f"{100*het[(st, 'LOH')]/tot[st]:.1f}")
               for st in sorted(tot, key=tot.get, reverse=True)])

    # 3. 可能 subclonal 的 CNV／SV（bedpe 的 possibly_subclonal 欄）
    sub = collections.Counter()
    sub_rows = []
    with open(CNV_BEDPE) as f:
        r = csv.reader(f, delimiter="\t")
        hdr = next(r)
        i_sub, i_type, i_h1, i_h2 = hdr.index("possibly_subclonal"), hdr.index("SVTYPE"), hdr.index("CN_HAP1"), hdr.index("CN_HAP2")
        for row in r:
            flag = row[i_sub]
            svlen = row[hdr.index("SVLEN_max")]
            sub[(flag, row[i_type])] += 1
            if flag == "y":
                sub_rows.append((row[0], row[1], row[4], row[hdr.index("ID")], row[i_type], row[i_h1], row[i_h2], svlen,
                                 row[hdr.index("SVVIZ_VAF_ALL")]))
    write_tsv("sv_cnv_subclonal_flag.tsv", ["possibly_subclonal", "SVTYPE", "n"], [(*k, n) for k, n in sorted(sub.items())])
    write_tsv("subclonal_events.tsv", ["chrom", "start1", "end1", "ID", "SVTYPE", "CN_HAP1", "CN_HAP2", "SVLEN_max", "SVVIZ_VAF_ALL"], sub_rows)

    for name in sorted(OUT.glob("*.tsv")):
        print(f"### {name.name}")
        print(name.read_text())


if __name__ == "__main__":
    main()
