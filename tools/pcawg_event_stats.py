#!/usr/bin/env python3
"""PCAWG open-access 事件統計，對照 HP-aware 真值樹參數。

輸入（全部 open access，見 /big8_disk/boyu114/benchmark_data/PCAWG/README.md）：
  icgc25k_open/evolution_and_heterogeneity/icgc_sample_annotations_summary_table.txt
  icgc25k_open/consensus_cnv/consensus.20170119.somatic.cna.annotated.tar.gz
  icgc25k_open/consensus_snv_indel/final_consensus_passonly.snv_mnv_indel.icgc.public.maf.gz

輸出：OUT/tables/*.tsv，並在 stdout 印摘要。

用法：
  python3 -I tools/pcawg_event_stats.py DATA_ROOT OUT_DIR [--skip-maf]

下載資料視為不可信：只當文字解析，不 eval、不 import。
"""
import argparse
import bisect
import csv
import gzip
import io
import math
import os
import statistics as st
import sys
import tarfile
from collections import Counter, defaultdict

AUTOSOMES = {str(i) for i in range(1, 23)}
REP_HIST = ["Breast-AdenoCA", "Lung-AdenoCA", "Lung-SCC", "Prost-AdenoCA",
            "Liver-HCC", "Panc-AdenoCA", "Skin-Melanoma", "Ovary-AdenoCA",
            "ColoRect-AdenoCA", "CNS-GBM", "Kidney-RCC.clearcell"]

# 真值樹參數（tools/draw_hp_truth_tree.py）
TRUTH = dict(purity=0.40, depth=200, ploidy=2.0, ccf_low=0.10)


def fnum(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def q(vals, p):
    v = sorted(vals)
    if not v:
        return float("nan")
    k = (len(v) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def summ(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return dict(n=0, median=float("nan"), q25=float("nan"), q75=float("nan"), mean=float("nan"))
    return dict(n=len(vals), median=q(vals, .5), q25=q(vals, .25), q75=q(vals, .75), mean=st.mean(vals))


def nrpcc(cov, p, ploidy):
    return cov * p / (p * ploidy + 2 * (1 - p))


def write_tsv(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([f"{x:.4g}" if isinstance(x, float) else x for x in r])


# ---------------------------------------------------------------- samples
def load_samples(root):
    path = os.path.join(root, "icgc25k_open/evolution_and_heterogeneity/icgc_sample_annotations_summary_table.txt")
    out = {}
    with open(path) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["is_preferred"] != "TRUE":
                continue
            out[r["tumour_aliquot_id"]] = dict(
                hist=r["histology_abbreviation"], purity=fnum(r["purity"]), ploidy=fnum(r["ploidy"]),
                wgd=r["wgd_status"] == "wgd", nsub=int(r["num_subclones"]) if r["num_subclones"] not in ("", "NA") else None,
                ncl=fnum(r["num_clonal_snvs"]), nsc=fnum(r["num_subclonal_snvs"]),
                cov=fnum(r["cov_tumour"]), nrpcc=fnum(r["nrpcc"]))
    return out


def sample_stats(S, tdir):
    groups = {"ALL": list(S)}
    for h in REP_HIST:
        groups[h] = [k for k, v in S.items() if v["hist"] == h]
    rows = []
    for g, ids in groups.items():
        pur = [S[i]["purity"] for i in ids if S[i]["purity"] is not None]
        cov = [S[i]["cov"] for i in ids if S[i]["cov"] is not None]
        nr = [S[i]["nrpcc"] for i in ids if S[i]["nrpcc"] is not None]
        ns = [S[i]["nsub"] for i in ids if S[i]["nsub"] is not None]
        fsc = [S[i]["nsc"] / (S[i]["nsc"] + S[i]["ncl"]) for i in ids
               if S[i]["nsc"] is not None and S[i]["ncl"] is not None and S[i]["nsc"] + S[i]["ncl"] > 0]
        sp, sc, sn = summ(pur), summ(cov), summ(nr)
        nsc_ = Counter(ns)
        rows.append([g, len(ids), sp["median"], sp["q25"], sp["q75"],
                     sum(p <= 0.40 for p in pur) / max(len(pur), 1),
                     sum(p <= 0.30 for p in pur) / max(len(pur), 1),
                     sc["median"], sn["median"], sum(x >= 10 for x in nr) / max(len(nr), 1),
                     sum(x >= 40 for x in nr) / max(len(nr), 1),
                     nsc_[0] / max(len(ns), 1), nsc_[1] / max(len(ns), 1), nsc_[2] / max(len(ns), 1),
                     sum(v >= 3 for v in ns) / max(len(ns), 1),
                     summ(fsc)["median"]])
    hdr = ["group", "n_samples", "purity_median", "purity_q25", "purity_q75", "frac_purity_le_0.40",
           "frac_purity_le_0.30", "cov_tumour_median", "nrpcc_median", "frac_nrpcc_ge_10", "frac_nrpcc_ge_40",
           "frac_0_subclones", "frac_1_subclone", "frac_2_subclones", "frac_ge3_subclones",
           "subclonal_snv_frac_median"]
    write_tsv(os.path.join(tdir, "d_purity_depth_subclones.tsv"), hdr, rows)
    # purity histogram
    bins = [i / 10 for i in range(11)]
    pur = [v["purity"] for v in S.values() if v["purity"] is not None]
    hist = [[f"{bins[i]:.1f}-{bins[i+1]:.1f}", sum(bins[i] < p <= bins[i + 1] or (i == 0 and p == 0) for p in pur)]
            for i in range(10)]
    write_tsv(os.path.join(tdir, "d_purity_histogram.tsv"), ["purity_bin", "n_samples"], hist)
    return rows


def detectability(S, tdir):
    """期望 alt read 數 = NRPCC × CCF（multiplicity 1、heterozygous）。"""
    rows = []
    nr = [v["nrpcc"] for v in S.values() if v["nrpcc"] is not None]
    t_nr = nrpcc(TRUTH["depth"], TRUTH["purity"], TRUTH["ploidy"])
    scen = [("truth_tree_200x", TRUTH["purity"], 200), ("truth_tree_at_pcawg_median_depth", TRUTH["purity"],
            q([v["cov"] for v in S.values() if v["cov"]], .5)), ("truth_tree_60x", TRUTH["purity"], 60),
            ("truth_tree_40x", TRUTH["purity"], 40)]
    for name, p, d in scen:
        n_ = nrpcc(d, p, TRUTH["ploidy"])
        lam = n_ * TRUTH["ccf_low"]
        p_ge3 = 1 - sum(math.exp(-lam) * lam ** k / math.factorial(k) for k in range(3))
        rows.append([name, p, d, n_, lam, p_ge3, sum(x >= n_ for x in nr) / len(nr), ""])
    for ccf in (0.10, 0.15, 0.30):
        lams = [x * ccf for x in nr]
        rows.append([f"pcawg_samples_ccf{ccf:.2f}", "per-sample", "per-sample", q(nr, .5), q(lams, .5),
                     st.mean(1 - sum(math.exp(-l) * l ** k / math.factorial(k) for k in range(3)) for l in lams),
                     "", sum(l >= 4 for l in lams) / len(lams)])
    write_tsv(os.path.join(tdir, "b_detectability.tsv"),
              ["scenario", "purity", "depth", "nrpcc", "exp_alt_reads_at_ccf", "P(alt>=3)",
               "frac_pcawg_nrpcc_ge_this", "frac_pcawg_exp_alt_ge4"], rows)
    return t_nr, rows


# ---------------------------------------------------------------- copy number
def iter_cn(root):
    path = os.path.join(root, "icgc25k_open/consensus_cnv/consensus.20170119.somatic.cna.annotated.tar.gz")
    with tarfile.open(path, "r:gz") as tf:
        for m in tf:
            if not m.isfile() or not m.name.endswith(".txt"):
                continue
            sid = os.path.basename(m.name).split(".")[0]
            fh = io.TextIOWrapper(tf.extractfile(m))
            yield sid, list(csv.DictReader(fh, delimiter="\t"))


def bb_states(r):
    M1, m1, f1 = fnum(r["battenberg_nMaj1_A"]), fnum(r["battenberg_nMin1_A"]), fnum(r["battenberg_frac1_A"])
    if M1 is None or m1 is None or f1 is None:
        return None
    M2, m2 = fnum(r["battenberg_nMaj2_A"]), fnum(r["battenberg_nMin2_A"])
    if M2 is None or m2 is None or f1 >= 0.999:
        return [(M1, m1, 1.0)]
    return [(M1, m1, f1), (M2, m2, 1 - f1)]


def cn_stats(root, S, tdir):
    per = {}
    seg_index = {}       # sid -> chrom -> (starts, ends, label)
    ev_len = defaultdict(list)   # event -> list of Mb
    ev_ccf = defaultdict(list)
    for sid, rows in iter_cn(root):
        if sid not in S:
            continue
        wgd = S[sid]["wgd"]
        base = 4 if wgd else 2
        d = Counter()
        idx = defaultdict(lambda: ([], [], []))
        for r in rows:
            ch = r["chromosome"]
            if ch not in AUTOSOMES:
                continue
            s, e = int(float(r["start"])), int(float(r["end"]))
            L = e - s + 1
            Mj, mn, tot = fnum(r["major_cn"]), fnum(r["minor_cn"]), fnum(r["total_cn"])
            star = fnum(r["star"])
            st_ = bb_states(r)
            if Mj is not None and mn is not None:
                d["cons_bp"] += L
                if mn == 0:
                    d["cons_loh_bp"] += L
                    if tot == base:
                        d["cons_cnloh_bp"] += L
                        ev_len["clonal_cnLOH(consensus)"].append(L / 1e6)
                        if L >= 10e6:
                            d["cnloh_ge10"] = 1
                if tot is not None and tot > base:
                    d["gain_bp"] += L
                    if tot == base + 1:
                        d["gain1_bp"] += L
            label = None
            if st_ is not None:
                d["bb_bp"] += L
                if len(st_) == 2:
                    d["bb_sub_bp"] += L
                    (M1, m1, f1), (M2, m2, f2) = st_
                    t1, t2 = M1 + m1, M2 + m2
                    loh1, loh2 = m1 == 0, m2 == 0
                    # 註：Battenberg 兩狀態只差一個 allele 的一個 copy，(1,1)/(2,0) 這類 subclonal cnLOH
                    # 無法表示，所以 subclonal cnLOH 在此資料恆為 0（資料不支援），不輸出。
                    if loh1 != loh2:
                        d["bb_sub_loh_bp"] += L
                        ev_len["subclonal_LOH"].append(L / 1e6)
                        if L >= 10e6:
                            d["subloh_ge10"] = 1
                        ev_ccf["subclonal_LOH"].append(f1 if loh1 else f2)  # LOH 狀態必為 derived
                    if abs(t1 - t2) == 1:
                        d["bb_sub_1copy_bp"] += L
                        if t1 > base or t2 > base:
                            d["bb_sub_gain1_bp"] += L
                            ev_len["subclonal_1copy_gain"].append(L / 1e6)
                            ev_ccf["subclonal_1copy_gain"].append(f1 if t1 > t2 else f2)  # 假設高 CN 狀態為 derived
                    # 一個狀態的 total CN 低於基準（2；WGD 為 4）→ subclonal deletion，突變遺失的候選區
                    if min(t1, t2) < base:
                        d["bb_sub_del_bp"] += L
                        ev_len["subclonal_deletion(total<base)"].append(L / 1e6)
                        ev_ccf["subclonal_deletion(total<base)"].append(f1 if t1 < t2 else f2)  # 假設低 CN 狀態為 derived
                    label = "sub"
                else:
                    label = (st_[0][0], st_[0][1]) if star is not None and star >= 2 else None
            if label is not None and label != "sub":
                a = idx[ch]
                a[0].append(s); a[1].append(e); a[2].append(label)
        per[sid] = d
        seg_index[sid] = dict(idx)

    def frac(d, a, b):
        return d[a] / d[b] if d[b] > 0 else None

    groups = {"ALL": [k for k in per]}
    for h in REP_HIST:
        groups[h] = [k for k in per if S[k]["hist"] == h]
    out = []
    for g, ids in groups.items():
        f_sub = [frac(per[i], "bb_sub_bp", "bb_bp") for i in ids]
        f_subloh = [frac(per[i], "bb_sub_loh_bp", "bb_bp") for i in ids]
        f_cnloh = [frac(per[i], "cons_cnloh_bp", "cons_bp") for i in ids]
        f_loss = [frac(per[i], "bb_sub_del_bp", "bb_bp") for i in ids]
        g1 = [frac(per[i], "gain1_bp", "gain_bp") for i in ids]
        has_subloh = [per[i]["bb_sub_loh_bp"] > 0 for i in ids if per[i]["bb_bp"] > 0]
        has_cnloh = [per[i]["cons_cnloh_bp"] > 0 for i in ids if per[i]["cons_bp"] > 0]
        tot_gain = sum(per[i]["gain_bp"] for i in ids)
        tot_g1 = sum(per[i]["gain1_bp"] for i in ids)
        out.append([g, len(ids), summ(f_sub)["median"], summ(f_sub)["q75"],
                    sum(x is not None and x > 0.2 for x in f_sub) / max(len(ids), 1),
                    st.mean(has_subloh) if has_subloh else None, summ(f_subloh)["median"],
                    sum(per[i]["subloh_ge10"] for i in ids) / max(len(ids), 1),
                    st.mean(has_cnloh) if has_cnloh else None,
                    sum(per[i]["cnloh_ge10"] for i in ids) / max(len(ids), 1), summ(f_cnloh)["median"],
                    summ(f_loss)["median"], summ(f_loss)["q75"],
                    tot_g1 / tot_gain if tot_gain else None, summ(g1)["median"]])
    hdr = ["group", "n_samples", "subclonalCN_genome_frac_median", "subclonalCN_genome_frac_q75",
           "frac_samples_subclonalCN_gt_20pct", "frac_samples_with_subclonal_LOH", "subclonal_LOH_genome_frac_median",
           "frac_samples_subclonal_LOH_seg_ge10Mb",
           "frac_samples_with_clonal_cnLOH", "frac_samples_clonal_cnLOH_seg_ge10Mb", "clonal_cnLOH_genome_frac_median",
           "subclonal_deletion_genome_frac_median(proxy_a)", "subclonal_deletion_genome_frac_q75",
           "pooled_frac_gain_bp_single_copy", "per_sample_frac_gain_bp_single_copy_median"]
    write_tsv(os.path.join(tdir, "c_copy_number_events.tsv"), hdr, out)
    ps = []
    for i in sorted(per):
        d = per[i]
        ps.append([i, S[i]["hist"], S[i]["purity"], int(S[i]["wgd"]), frac(d, "bb_sub_bp", "bb_bp"),
                   frac(d, "bb_sub_loh_bp", "bb_bp"), frac(d, "bb_sub_del_bp", "bb_bp"),
                   frac(d, "cons_cnloh_bp", "cons_bp"), frac(d, "gain1_bp", "gain_bp")])
    write_tsv(os.path.join(tdir, "c_copy_number_per_sample.tsv"),
              ["sample", "histology", "purity", "wgd", "subclonalCN_frac", "subclonal_LOH_frac",
               "subclonal_deletion_frac", "clonal_cnLOH_frac", "single_copy_gain_frac_of_gain"], ps)
    ev = []
    for k in sorted(ev_len):
        s1 = summ(ev_len[k])
        s2 = summ(ev_ccf.get(k, []))
        ev.append([k, s1["n"], s1["median"], s1["q25"], s1["q75"], sum(x >= 10 for x in ev_len[k]) / s1["n"],
                   s2["median"], s2["q25"], s2["q75"]])
    write_tsv(os.path.join(tdir, "c_event_segment_lengths.tsv"),
              ["event", "n_segments", "len_Mb_median", "len_Mb_q25", "len_Mb_q75", "frac_len_ge_10Mb",
               "derived_state_tumour_frac_median", "derived_state_tumour_frac_q25", "derived_state_tumour_frac_q75"], ev)
    return per, seg_index, out, ev


# ---------------------------------------------------------------- multiplicity
def binom_logpmf(k, n, p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log(1 - p)


def em_timing(snvs, p, M, m):
    """在 clonal major:minor 段內，用 EM 估計 {multiplicity 2..M clonal, m=1 clonal, subclonal} 權重。"""
    N = p * (M + m) + 2 * (1 - p)
    comps = [("m%d" % k, [(k * p / N, 1.0)]) for k in range(1, M + 1)]
    grid = [c / 20 for c in range(2, 18)]  # subclonal CCF 0.10–0.85
    comps.append(("sub", [(c * p / N, 1 / len(grid)) for c in grid]))
    L = []
    for alt, dep in snvs:
        row = []
        for _, pts in comps:
            row.append(math.log(sum(w * math.exp(binom_logpmf(alt, dep, f)) for f, w in pts) + 1e-300))
        L.append(row)
    w = [1 / len(comps)] * len(comps)
    for _ in range(100):
        acc = [0.0] * len(comps)
        for row in L:
            mx = max(math.log(w[j]) + row[j] for j in range(len(comps)))
            r = [math.exp(math.log(w[j]) + row[j] - mx) for j in range(len(comps))]
            s = sum(r)
            for j in range(len(comps)):
                acc[j] += r[j] / s
        nw = [max(a / len(L), 1e-9) for a in acc]
        if max(abs(a - b) for a, b in zip(nw, w)) < 1e-5:
            w = nw
            break
        w = nw
    return {name: w[j] for j, (name, _) in enumerate(comps)}


def maf_stats(root, S, seg_index, tdir, min_snv=30, min_nrpcc=10):
    path = os.path.join(root, "icgc25k_open/consensus_snv_indel/final_consensus_passonly.snv_mnv_indel.icgc.public.maf.gz")
    targets = {(2, 1): "2:1", (2, 0): "2:0(cnLOH)"}
    keep = {sid for sid, v in S.items() if not v["wgd"] and v["nrpcc"] and v["nrpcc"] >= min_nrpcc
            and sid in seg_index}
    bucket = defaultdict(list)
    with gzip.open(path, "rt") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in fh:
            f = line.split("\t")
            if f[ix["Variant_Type"]] != "SNP":
                continue
            sid = f[ix["Tumor_Sample_Barcode"]]
            if sid not in keep:
                continue
            ch = f[ix["Chromosome"]]
            idx = seg_index[sid].get(ch)
            if not idx:
                continue
            pos = int(f[ix["Start_position"]])
            k = bisect.bisect_right(idx[0], pos) - 1
            if k < 0 or pos > idx[1][k]:
                continue
            lab = targets.get(idx[2][k])
            if lab is None:
                continue
            try:
                a, r = int(f[ix["t_alt_count"]]), int(f[ix["t_ref_count"]])
            except ValueError:
                continue
            if a + r > 0:
                bucket[(sid, lab)].append((a, a + r))
    rows, pooled = [], defaultdict(lambda: defaultdict(float))
    for (sid, lab), snvs in sorted(bucket.items()):
        if len(snvs) < min_snv:
            continue
        M, m = (2, 1) if lab == "2:1" else (2, 0)
        w = em_timing(snvs, S[sid]["purity"], M, m)
        clonal = w["m1"] + w["m2"]
        early = w["m2"] / clonal if clonal > 0 else None
        # MutationTimeR 風格 molecular time（單一 gain，major 2）：t = (M+m)·n2 / (n1 + (M+m)·n2) 的簡化；
        # 2:1: t = 3 n2 / (2 n2 + n1)；2:0: t = 2 n2 / (2 n2 + n1)
        n1, n2 = w["m1"], w["m2"]
        t = (3 * n2 / (2 * n2 + n1)) if lab == "2:1" else (2 * n2 / (2 * n2 + n1))
        rows.append([sid, S[sid]["hist"], lab, len(snvs), S[sid]["purity"], S[sid]["nrpcc"],
                     w["m2"], w["m1"], w["sub"], early, min(t, 1.0)])
        for kk, vv in w.items():
            pooled[lab][kk] += vv * len(snvs)
    write_tsv(os.path.join(tdir, "e_gain_multiplicity_per_sample.tsv"),
              ["sample", "histology", "segment_state", "n_snv", "purity", "nrpcc", "w_mult2_clonal",
               "w_mult1_clonal", "w_subclonal", "early_frac_of_clonal", "molecular_time_approx"], rows)
    summ_rows = []
    for lab in ("2:1", "2:0(cnLOH)"):
        sub = [r for r in rows if r[2] == lab]
        for g in ["ALL"] + REP_HIST:
            gg = [r for r in sub if g == "ALL" or r[1] == g]
            if not gg:
                continue
            P = pooled[lab] if g == "ALL" else None
            pooled_early = (P["m2"] / (P["m1"] + P["m2"])) if P else None
            pooled_m2_all = (P["m2"] / sum(P.values())) if P else None
            summ_rows.append([lab, g, len(gg), sum(r[3] for r in gg), summ([r[9] for r in gg])["median"],
                              summ([r[9] for r in gg])["q25"], summ([r[9] for r in gg])["q75"],
                              summ([r[10] for r in gg])["median"], summ([r[8] for r in gg])["median"],
                              pooled_early, pooled_m2_all])
    write_tsv(os.path.join(tdir, "e_gain_multiplicity_summary.tsv"),
              ["segment_state", "group", "n_samples", "n_snv", "early_frac_median", "early_frac_q25",
               "early_frac_q75", "molecular_time_median", "subclonal_weight_median",
               "pooled_early_frac_of_clonal", "pooled_mult2_frac_of_all"], summ_rows)
    return summ_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("out")
    ap.add_argument("--skip-maf", action="store_true")
    a = ap.parse_args()
    tdir = os.path.join(a.out, "tables")
    os.makedirs(tdir, exist_ok=True)
    S = load_samples(a.root)
    print("samples(preferred):", len(S), file=sys.stderr)
    sample_stats(S, tdir)
    t_nr, _ = detectability(S, tdir)
    print("truth NRPCC:", round(t_nr, 2), file=sys.stderr)
    per, seg_index, _, _ = cn_stats(a.root, S, tdir)
    print("CN samples:", len(per), file=sys.stderr)
    if not a.skip_maf:
        maf_stats(a.root, S, seg_index, tdir)
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
