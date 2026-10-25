#!/usr/bin/env python3
"""TRACERx 421（Frankell 2023, Zenodo 7822002；Al Bakir 2023, Zenodo 7649257）事件統計。

計算 HP-aware 真值樹需要的 (a)–(d)：
  (a) SNV 層級突變遺失（區域間：在某區域 clonal、在另一區域 0 alt read，且該區域有 allele 掉到 ~0）
  (b) subclone CCF 分佈，CCF ≤ 0.15 的比例（單一區域與 tumour 平均兩種視角）
  (c) subclonal cnLOH 事件數與長度（區域間）
  (d) 樹形（clone 數、直線 vs 分岔、4-clone 形狀；全樹與單一區域子樹）、MSAI、subclonal haplotype-specific gain
另附 purity 分佈。

先跑 tools/tracerx_export.R 產生 derived_tsv/。用法：
  python3 -I tools/tracerx_event_stats.py \
      --derived /big8_disk/boyu114/benchmark_data/TRACERx/Frankell2023_zenodo7822002/derived_tsv \
      --metrics .../Frankell2023_zenodo7822002/extracted/figurecode/data/20221110_TRACERx421_evolutionary_metrics.tsv \
      --purity  .../AlBakir2023_zenodo7649257/extracted/metsFigures/data/20220808_purityandploidy.txt \
      --out lab_report/2026-10-25_tracerx_event_stats/tables
"""
import argparse
import json
import os
import site
import sys
from collections import defaultdict

# python3 -I 會關掉 user site；numpy／pandas 裝在 ~/.local，所以手動加回（不加 cwd 或資料目錄）。
_us = site.getusersitepackages()
if _us not in sys.path:
    sys.path.append(_us)

import numpy as np
import pandas as pd

# ---- 門檻（集中在這裡，README 會列出） ----
CLONAL_CCF = 0.8        # 某區域 PhyloCCF ≥ 0.8 視為 clonal
CLONAL_MIN_ALT = 5      # 且 alt read ≥ 5
ABSENT_MIN_COV = 50     # 另一區域 depth ≥ 50 且 alt = 0 視為缺席
ALLELE_LOST = 0.25      # 該區域某 allele raw CN < 0.25
ALLELE_KEPT = 0.5       # 在 clonal 區域同一 allele raw CN ≥ 0.5
LOW_CCF = 0.15          # 低 CCF subclone 門檻
MIN_EVENT_BP = 1_000_000  # CN 事件長度下限（合併相鄰 segment 後）
TRUTH = dict(purity=0.40, n_clones=4, low_ccf=0.10, frac_snv_lost=0.20)


def q(x, ps=(0.25, 0.5, 0.75)):
    x = pd.Series(x).dropna()
    if len(x) == 0:
        return dict(n=0)
    d = dict(n=int(len(x)), mean=float(x.mean()))
    for p in ps:
        d[f"q{int(p * 100)}"] = float(x.quantile(p))
    d["min"], d["max"] = float(x.min()), float(x.max())
    return d


# ---------------- (a) 突變遺失 ----------------
def mutation_loss(mr, meta, nreg, mt):
    mr = mr.copy()
    # cpn_removed cluster 的突變不在樹表（ccf_table_pyclone_clean）內，要從 mutation table 算
    mt = mt[mt.PyCloneCluster_SC.notna()].copy()
    mt["cl"] = mt.PyCloneCluster_SC.astype(int).astype(str)
    mt_by_t = {t: g.cl for t, g in mt.groupby("tumour_id")}
    n_sub = mt[mt.PyCloneClonal_SC == "S"].groupby("tumour_id").size()
    multi = nreg[nreg >= 2].index
    mr = mr[mr.tumour_id.isin(multi)]
    rows = []
    for tid, g in mr.groupby("tumour_id", sort=False):
        piv = {c: g.pivot_table(index="mutation_id", columns="region", values=c, aggfunc="first")
               for c in ["phylo_ccf", "var_count", "cov", "nAraw", "nBraw"]}
        regs = list(piv["cov"].columns)
        ccf, alt, cov = piv["phylo_ccf"], piv["var_count"], piv["cov"]
        A, Bc = piv["nAraw"], piv["nBraw"]
        tot = A + Bc
        n_mut = len(cov)
        clonal = (ccf >= CLONAL_CCF) & (alt >= CLONAL_MIN_ALT)
        absent = (alt == 0) & (cov >= ABSENT_MIN_COV)
        any_clonal = clonal.any(axis=1)
        lost_any = pd.Series(False, index=cov.index)
        lost_del = pd.Series(False, index=cov.index)
        lost_cnloh = pd.Series(False, index=cov.index)
        absent_clonal_elsewhere = pd.Series(False, index=cov.index)
        for r2 in regs:
            ab = absent[r2] & any_clonal
            # 以 clonal 的區域當參照（取第一個 clonal 區域）
            for r1 in regs:
                if r1 == r2:
                    continue
                cand = ab & clonal[r1]
                if not cand.any():
                    continue
                absent_clonal_elsewhere |= cand
                a_lost = (A[r2] < ALLELE_LOST) & (A[r1] >= ALLELE_KEPT)
                b_lost = (Bc[r2] < ALLELE_LOST) & (Bc[r1] >= ALLELE_KEPT)
                hit = cand & (a_lost | b_lost)
                lost_any |= hit
                drop = (tot[r1] - tot[r2]) >= 0.5
                lost_del |= hit & drop
                lost_cnloh |= hit & ~drop
        m = meta.get(tid, {})
        cpn_rm = set(str(m.get("cpn_removed", "")).split(",")) - {"", "nan", "NA"}
        clus = mt_by_t.get(tid, pd.Series(dtype=str))
        rows.append(dict(tumour_id=tid, n_regions=len(regs), n_mut=n_mut,
                         n_clonal_somewhere=int(any_clonal.sum()),
                         n_absent_but_clonal_elsewhere=int(absent_clonal_elsewhere.sum()),
                         n_lost_allele_explained=int(lost_any.sum()),
                         n_lost_deletion_type=int(lost_del.sum()),
                         n_lost_cnloh_type=int((lost_cnloh & ~lost_del).sum()),
                         n_mut_clustered=int(len(clus)),
                         n_mut_subclonal_tumour=int(n_sub.get(tid, 0)),
                         n_mut_in_cpn_removed_clusters=int(clus.isin(cpn_rm).sum()),
                         n_cpn_removed_clusters=len(cpn_rm)))
    df = pd.DataFrame(rows)
    df["frac_mut_lost"] = df.n_lost_allele_explained / df.n_mut
    df["frac_mut_absent_clonal_elsewhere"] = df.n_absent_but_clonal_elsewhere / df.n_mut
    df["frac_absences_explained_by_allele_loss"] = (
        df.n_lost_allele_explained / df.n_absent_but_clonal_elsewhere.replace(0, np.nan))
    df["frac_subclonal_mut_lost"] = df.n_lost_allele_explained / df.n_mut_subclonal_tumour.replace(0, np.nan)
    df["frac_mut_cpn_removed"] = df.n_mut_in_cpn_removed_clusters / df.n_mut_clustered
    return df


# ---------------- (b)(d) 樹 ----------------
def tree_struct(edges):
    out = {}
    for tid, g in edges.groupby("tumour_id"):
        ch = defaultdict(list)
        par = {}
        nodes = set(g.parent.astype(str)) | set(g.child.astype(str))
        for p, c in zip(g.parent.astype(str), g.child.astype(str)):
            if p == c:  # 只有 trunk 的 tumour 用 self-edge 表示
                continue
            ch[p].append(c)
            par[c] = p
        roots = [n for n in nodes if n not in par]
        out[tid] = dict(children=ch, parent=par, nodes=nodes, roots=roots)
    return out


def shape_label(ch, root):
    """回傳 canonical 字串，例如 4-clone 真值樹是 '(((.)).)' 的形式。"""
    def canon(n):
        subs = sorted(canon(c) for c in ch.get(n, []))
        return "(" + "".join(subs) + ")"
    return canon(root)


TRUTH_SHAPE = None  # 下面計算


def tree_stats(ts, meta):
    global TRUTH_SHAPE
    tch = {"C1": ["C2", "C3"], "C2": ["C4"]}
    TRUTH_SHAPE = shape_label(tch, "C1")
    rows = []
    for tid, t in ts.items():
        ch, nodes = t["children"], t["nodes"]
        nbranch = sum(1 for n in nodes if len(ch.get(n, [])) >= 2)
        leaves = sum(1 for n in nodes if len(ch.get(n, [])) == 0)
        root = t["roots"][0] if len(t["roots"]) == 1 else None
        rows.append(dict(tumour_id=tid, n_clones=len(nodes), n_roots=len(t["roots"]),
                         n_branch_nodes=nbranch, n_leaves=leaves,
                         linear=nbranch == 0,
                         shape=shape_label(ch, root) if root else "multi-root",
                         n_alt_trees=meta.get(tid, {}).get("n_alt_trees")))
    df = pd.DataFrame(rows)
    df["same_shape_as_truth"] = df["shape"] == TRUTH_SHAPE
    return df


def region_subtrees(ts, cc, purity, min_ccf=0.0):
    """單一區域視角：只保留該區域 CCF > min_ccf 的 cluster（加上其祖先）。"""
    rows, clone_rows = [], []
    for (tid, reg), g in cc.groupby(["tumour_id", "region"]):
        if tid not in ts:
            continue
        t = ts[tid]
        ccf = dict(zip(g.cluster.astype(str), g.ccf_pct / 100.0))
        present = {n for n in t["nodes"] if ccf.get(n, 0) > min_ccf}
        # 加祖先（保持連通）
        keep = set(present)
        for n in list(present):
            while n in t["parent"]:
                n = t["parent"][n]
                keep.add(n)
        ch = {p: [c for c in cs if c in keep] for p, cs in t["children"].items() if p in keep}
        roots = [n for n in keep if t["parent"].get(n) not in keep]
        nb = sum(1 for n in keep if len(ch.get(n, [])) >= 2)
        pur = purity.get(reg)
        trunk = roots[0] if len(roots) == 1 else None
        rows.append(dict(tumour_id=tid, region=reg, purity=pur, n_clones=len(keep), n_branch_nodes=nb,
                         linear=nb == 0, shape=shape_label(ch, trunk) if trunk else "multi-root"))
        for n in keep:
            if n == trunk:
                continue
            clone_rows.append(dict(tumour_id=tid, region=reg, cluster=n, ccf=ccf.get(n, 0.0), purity=pur))
    rdf = pd.DataFrame(rows)
    rdf["same_shape_as_truth"] = rdf["shape"] == TRUTH_SHAPE
    return rdf, pd.DataFrame(clone_rows)


def tumour_mean_ccf(ts, cc):
    rows = []
    for tid, g in cc.groupby("tumour_id"):
        if tid not in ts:
            continue
        t = ts[tid]
        trunk = t["roots"][0] if len(t["roots"]) == 1 else None
        m = g.groupby(g.cluster.astype(str)).ccf_pct.mean() / 100.0
        nreg = g.region.nunique()
        for n in t["nodes"]:
            if n == trunk:
                continue
            rows.append(dict(tumour_id=tid, cluster=n, n_regions=nreg, mean_ccf=float(m.get(n, 0.0)),
                             max_ccf=float(g[g.cluster.astype(str) == n].ccf_pct.max() / 100.0)))
    return pd.DataFrame(rows)


# ---------------- (c)(d) CN ----------------
def merge_events(seg, flag_col, keycols=("chr",)):
    """合併同一 chr 上相鄰且 flag 為 True 的 segment。seg 已依 chr,start 排序。"""
    ev = []
    cur = None
    for r in seg.itertuples(index=False):
        f = getattr(r, flag_col)
        if f and cur is not None and r.chr == cur["chr"]:
            cur["end"] = r.endpos
            cur["n_seg"] += 1
            cur["bp"] += r.endpos - r.startpos
        elif f:
            if cur:
                ev.append(cur)
            cur = dict(chr=r.chr, start=r.startpos, end=r.endpos, n_seg=1, bp=r.endpos - r.startpos)
        else:
            if cur:
                ev.append(cur)
            cur = None
    if cur:
        ev.append(cur)
    return ev


def cn_stats(sc):
    sc = sc.copy()
    sc["seg"] = sc.chr.astype(str) + ":" + sc.startpos.astype(str) + ":" + sc.endpos.astype(str)
    sc["LOH"] = sc.nMinor == 0
    sc["cnLOH"] = (sc.nMinor == 0) & (sc.nMajor >= 2) & (sc.cpn_event_vs_ploidy == "neutral")
    sc["A_int"] = sc.nAraw.round()
    sc["B_int"] = sc.nBraw.round()
    tum_rows, ev_rows = [], []
    genome_bp = 2.88e9  # 約略（autosome+X），只用於比例
    for tid, g in sc.groupby("tumour_id"):
        nreg = g["sample"].nunique()
        agg = g.groupby("seg").agg(chr=("chr", "first"), startpos=("startpos", "first"),
                                    endpos=("endpos", "first"),
                                    n_LOH=("LOH", "sum"), n_cnLOH=("cnLOH", "sum"),
                                    n_het=("nMinor", lambda x: int((x >= 1).sum())),
                                    msai=("MSAI", lambda x: bool((x == True).any())),  # noqa: E712
                                    A_min=("A_int", "min"), A_max=("A_int", "max"),
                                    B_min=("B_int", "min"), B_max=("B_int", "max"),
                                    Ar_rng=("nAraw", lambda x: float(x.max() - x.min())),
                                    Br_rng=("nBraw", lambda x: float(x.max() - x.min())),
                                    T_rng=("cnTotal", lambda x: int(x.max() - x.min())),
                                    nreg=("sample", "nunique")).reset_index()
        agg = agg.sort_values(["chr", "startpos"])
        agg["clonal_cnLOH"] = agg.n_cnLOH == agg.nreg
        agg["subclonal_cnLOH"] = (agg.n_cnLOH >= 1) & (agg.n_het >= 1)
        agg["subclonal_LOH"] = (agg.n_LOH >= 1) & (agg.n_het >= 1)
        # 單一 haplotype 的 subclonal gain：某 allele 的整數 CN 在區域間不同，且最小值 ≥ 1（是增加，不是失去）
        agg["subcl_hap_gain"] = (((agg.A_max > agg.A_min) & (agg.A_min >= 1)) |
                                 ((agg.B_max > agg.B_min) & (agg.B_min >= 1)))
        # 嚴格版：raw 差 ≥ 0.8、整數 total CN 也不同、且另一個 allele 的 raw 變動 < 0.5（只有一個 haplotype 變）
        agg["subcl_hap_gain_strict"] = ((agg.T_rng >= 1) &
                                        (((agg.Ar_rng >= 0.8) & (agg.A_min >= 1) & (agg.Br_rng < 0.5)) |
                                         ((agg.Br_rng >= 0.8) & (agg.B_min >= 1) & (agg.Ar_rng < 0.5))))
        agg["subcl_hap_gain_plus1"] = (((agg.A_max - agg.A_min == 1) & (agg.A_min >= 1)) |
                                       ((agg.B_max - agg.B_min == 1) & (agg.B_min >= 1)))
        agg["bp"] = agg.endpos - agg.startpos
        d = dict(tumour_id=tid, n_regions=nreg, total_bp=float(agg.bp.sum()))
        for col in ["clonal_cnLOH", "subclonal_cnLOH", "subclonal_LOH", "msai", "subcl_hap_gain", "subcl_hap_gain_strict"]:
            evs = [e for e in merge_events(agg, col) if e["bp"] >= MIN_EVENT_BP]
            d[f"n_ev_{col}"] = len(evs)
            d[f"frac_genome_{col}"] = float(agg.loc[agg[col], "bp"].sum() / agg.bp.sum())
            for e in evs:
                ev_rows.append(dict(tumour_id=tid, n_regions=nreg, type=col, **e))
        d["frac_subcl_hap_gain_that_is_plus1"] = (
            float(agg.loc[agg.subcl_hap_gain_plus1, "bp"].sum() / agg.loc[agg.subcl_hap_gain, "bp"].sum())
            if agg.subcl_hap_gain.any() else np.nan)
        tum_rows.append(d)
    return pd.DataFrame(tum_rows), pd.DataFrame(ev_rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--derived", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--purity", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    D = a.derived

    meta_df = pd.read_csv(os.path.join(D, "tree_meta.tsv"), sep="\t", dtype=str, keep_default_na=False)
    meta_df["n_alt_trees"] = meta_df.n_alt_trees.astype(int)
    meta = meta_df.set_index("tumour_id").to_dict("index")
    edges = pd.read_csv(os.path.join(D, "tree_edges.tsv"), sep="\t", dtype=str)
    cc = pd.read_csv(os.path.join(D, "cluster_ccf_region.tsv"), sep="\t", dtype={"cluster": str})
    pur = pd.read_csv(a.purity, sep="\t")
    # 每區域 purity：用 scna table 的 ACF（aberrant cell fraction，覆蓋全部區域）；Al Bakir 檔只覆蓋部分區域，做交叉檢查
    sc = pd.read_csv(os.path.join(D, "scna_region.tsv"), sep="\t")
    acf = sc.drop_duplicates("sample")[["sample", "ACF"]].copy()
    acf["region"] = acf["sample"].str.replace(r"-(R|r)", lambda m: "." + m.group(1), regex=True)
    purity = dict(zip(acf.region, acf.ACF))
    mr_pur = dict(zip(pur.Sample, pur["final.purity"]))
    both = [(purity[k], v) for k, v in mr_pur.items() if k in purity]
    metrics = pd.read_csv(a.metrics, sep="\t")
    hist = pd.read_csv(os.path.join(D, "tumour_histology.tsv"), sep="\t")

    summary = {}

    # purity
    summary["purity_tumour"] = q(metrics.purity)
    summary["purity_tumour_frac_le_0.40"] = float((metrics.purity <= 0.40).mean())
    summary["purity_region_ACF"] = q(acf.ACF)
    summary["purity_region_ACF_frac_le_0.40"] = float((acf.ACF <= 0.40).mean())
    summary["purity_region_AlBakir"] = q(pur["final.purity"])
    summary["purity_ACF_vs_AlBakir_n_matched_maxabsdiff"] = [len(both), float(max(abs(a - b) for a, b in both)) if both else None]

    # (d) trees
    ts = tree_struct(edges)
    tdf = tree_stats(ts, meta)
    nreg = cc.groupby("tumour_id").region.nunique()
    tdf["n_regions"] = tdf.tumour_id.map(nreg)
    tdf = tdf.merge(hist, on="tumour_id", how="left")
    tdf.to_csv(os.path.join(a.out, "tree_per_tumour.tsv"), sep="\t", index=False)
    summary["truth_shape_canonical"] = TRUTH_SHAPE
    summary["tree_n"] = int(len(tdf))
    summary["tree_n_clones"] = q(tdf.n_clones)
    summary["tree_frac_linear"] = float(tdf.linear.mean())
    summary["tree_frac_n_clones_le_4"] = float((tdf.n_clones <= 4).mean())
    summary["tree_frac_n_clones_eq_4"] = float((tdf.n_clones == 4).mean())
    summary["tree_frac_same_shape_as_truth"] = float(tdf.same_shape_as_truth.mean())
    four = tdf[tdf.n_clones == 4]
    summary["tree_4clone_shape_counts"] = four["shape"].value_counts().to_dict()
    summary["tree_frac_multi_alt_trees"] = float((tdf.n_alt_trees > 1).mean())

    rdf, rclones = region_subtrees(ts, cc, purity)
    rdf.to_csv(os.path.join(a.out, "tree_per_region.tsv"), sep="\t", index=False)
    summary["region_tree_n"] = int(len(rdf))
    summary["region_n_clones"] = q(rdf.n_clones)
    summary["region_frac_linear"] = float(rdf.linear.mean())
    summary["region_frac_n_clones_eq_4"] = float((rdf.n_clones == 4).mean())
    summary["region_frac_same_shape_as_truth"] = float(rdf.same_shape_as_truth.mean())
    summary["region_4clone_shape_counts"] = rdf[rdf.n_clones == 4]["shape"].value_counts().to_dict()

    # (b) CCF
    rclones.to_csv(os.path.join(a.out, "subclone_ccf_per_region.tsv"), sep="\t", index=False)
    summary["region_subclone_ccf"] = q(rclones.ccf, ps=(0.1, 0.25, 0.5, 0.75))
    summary["region_subclone_frac_ccf_le_0.15"] = float((rclones.ccf <= LOW_CCF).mean())
    summary["region_subclone_frac_ccf_0.05_0.15"] = float(((rclones.ccf >= 0.05) & (rclones.ccf <= LOW_CCF)).mean())
    per_reg_low = rclones.groupby(["tumour_id", "region"]).ccf.apply(lambda x: (x <= LOW_CCF).any())
    allregs = rdf.set_index(["tumour_id", "region"]).index
    per_reg_low = per_reg_low.reindex(allregs, fill_value=False)
    summary["region_frac_with_ge1_subclone_ccf_le_0.15"] = float(per_reg_low.mean())
    rc = rclones.dropna(subset=["purity"]).copy()
    rc["cell_prev"] = rc.ccf * rc.purity
    summary["region_subclone_cellprev"] = q(rc.cell_prev, ps=(0.1, 0.25, 0.5))
    summary["region_subclone_frac_cellprev_le_0.04"] = float((rc.cell_prev <= 0.04).mean())
    tm = tumour_mean_ccf(ts, cc)
    tm.to_csv(os.path.join(a.out, "subclone_ccf_tumour_mean.tsv"), sep="\t", index=False)
    summary["tumour_mean_subclone_ccf"] = q(tm.mean_ccf, ps=(0.1, 0.25, 0.5, 0.75))
    summary["tumour_mean_subclone_frac_ccf_le_0.15"] = float((tm.mean_ccf <= LOW_CCF).mean())
    summary["tumour_frac_with_ge1_subclone_mean_ccf_le_0.15"] = float(
        tm.groupby("tumour_id").mean_ccf.apply(lambda x: (x <= LOW_CCF).any()).mean())

    # (a) mutation loss
    mr = pd.read_csv(os.path.join(D, "mutation_region_tree.tsv"), sep="\t",
                     dtype={"cluster": str})
    mt = pd.read_csv(os.path.join(D, "mutation_table.tsv"), sep="\t", low_memory=False,
                     usecols=["tumour_id", "PyCloneCluster_SC", "PyCloneClonal_SC"])
    ml = mutation_loss(mr, meta, nreg, mt)
    ml.to_csv(os.path.join(a.out, "mutation_loss_per_tumour.tsv"), sep="\t", index=False)
    summary["loss_n_tumours_multiregion"] = int(len(ml))
    summary["loss_frac_mut_lost"] = q(ml.frac_mut_lost, ps=(0.25, 0.5, 0.75, 0.9))
    summary["loss_frac_subclonal_mut_lost"] = q(ml.frac_subclonal_mut_lost, ps=(0.25, 0.5, 0.75, 0.9))
    summary["loss_frac_tumours_any_lost"] = float((ml.n_lost_allele_explained > 0).mean())
    summary["loss_frac_tumours_ge_20pct"] = float((ml.frac_mut_lost >= 0.20).mean())
    summary["loss_pooled_frac_mut_lost"] = float(ml.n_lost_allele_explained.sum() / ml.n_mut.sum())
    summary["loss_pooled_deletion_vs_cnloh"] = dict(
        deletion=int(ml.n_lost_deletion_type.sum()), cnloh=int(ml.n_lost_cnloh_type.sum()))
    summary["loss_frac_absent_clonal_elsewhere"] = q(ml.frac_mut_absent_clonal_elsewhere)
    summary["loss_frac_absences_explained"] = q(ml.frac_absences_explained_by_allele_loss)
    summary["loss_frac_mut_cpn_removed"] = q(ml.frac_mut_cpn_removed, ps=(0.25, 0.5, 0.75, 0.9))
    summary["loss_pooled_frac_mut_cpn_removed"] = float(ml.n_mut_in_cpn_removed_clusters.sum() / ml.n_mut_clustered.sum())
    summary["loss_frac_tumours_any_cpn_removed_cluster"] = float((ml.n_cpn_removed_clusters > 0).mean())
    # 依區域數分層
    ml["reg_bin"] = pd.cut(ml.n_regions, [1, 2, 3, 5, 100], labels=["2", "3", "4-5", "6+"])
    summary["loss_median_by_n_regions"] = ml.groupby("reg_bin", observed=True).frac_mut_lost.median().to_dict()

    # (c)(d) CN
    cnt, cne = cn_stats(sc)
    cnt.to_csv(os.path.join(a.out, "cn_per_tumour.tsv"), sep="\t", index=False)
    cne.to_csv(os.path.join(a.out, "cn_events.tsv"), sep="\t", index=False)
    multi = cnt[cnt.n_regions >= 2]
    summary["cn_n_tumours"] = int(len(cnt))
    summary["cn_n_tumours_multiregion"] = int(len(multi))
    for col in ["clonal_cnLOH", "subclonal_cnLOH", "subclonal_LOH", "msai", "subcl_hap_gain", "subcl_hap_gain_strict"]:
        base = cnt if col == "clonal_cnLOH" else multi
        summary[f"cn_frac_tumours_any_{col}"] = float((base[f"n_ev_{col}"] > 0).mean())
        summary[f"cn_n_ev_per_tumour_{col}"] = q(base[f"n_ev_{col}"])
        summary[f"cn_frac_genome_{col}"] = q(base[f"frac_genome_{col}"])
        e = cne[cne.type == col]
        summary[f"cn_event_size_Mb_{col}"] = q(e.bp / 1e6, ps=(0.1, 0.25, 0.5, 0.75, 0.9))
    summary["cn_frac_subcl_hap_gain_that_is_plus1"] = q(multi.frac_subcl_hap_gain_that_is_plus1)
    summary["metrics_genom_frac_subclonal_event"] = q(metrics.genom_frac_subclonal_event)
    summary["metrics_wFLOH"] = q(metrics.wFLOH)
    summary["metrics_num_subclones"] = q(metrics.num_subclones)
    summary["metrics_frac_polyclonal_or_branch"] = dict(
        num_branches=q(metrics.num_branches), branching_index=q(metrics.branching_index))
    summary["thresholds"] = dict(CLONAL_CCF=CLONAL_CCF, CLONAL_MIN_ALT=CLONAL_MIN_ALT, ABSENT_MIN_COV=ABSENT_MIN_COV,
                                 ALLELE_LOST=ALLELE_LOST, ALLELE_KEPT=ALLELE_KEPT, LOW_CCF=LOW_CCF,
                                 MIN_EVENT_BP=MIN_EVENT_BP)

    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(summary, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    main()
