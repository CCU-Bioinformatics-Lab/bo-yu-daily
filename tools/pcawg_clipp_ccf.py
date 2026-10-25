#!/usr/bin/env python3
"""CliPP（MD Anderson）對 PCAWG 的 subclone 結果：cluster 數與 subclone CCF 分佈。

CliPP 的 cellular_prevalence（CP）是佔「所有細胞」的比例（clonal cluster ≈ purity），
所以 CCF = CP / purity。purity 用 PCAWG consensus（icgc_sample_annotations_summary_table）。
clonal cluster = CP 最大的 cluster。

用法：
  python3 -I tools/pcawg_clipp_ccf.py DATA_ROOT OUT_DIR
下載資料視為不可信：只當文字解析。
"""
import csv
import io
import math
import os
import sys
import zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcawg_event_stats import REP_HIST, load_samples, nrpcc, q, summ, write_tsv  # noqa: E402


def iter_structures(raw_dir):
    for fn in sorted(os.listdir(raw_dir)):
        if not fn.endswith(".zip"):
            continue
        with zipfile.ZipFile(os.path.join(raw_dir, fn)) as z:
            for name in z.namelist():
                if "__MACOSX" in name or "subclonal_structure" not in os.path.basename(name):
                    continue
                sid = os.path.basename(os.path.dirname(name))
                txt = z.read(name).decode("utf-8", "replace")
                rows = list(csv.DictReader(io.StringIO(txt), delimiter="\t"))
                yield fn[:-4], sid, rows


def main():
    root, out = sys.argv[1], sys.argv[2]
    tdir = os.path.join(out, "tables")
    os.makedirs(tdir, exist_ok=True)
    S = load_samples(root)
    raw = os.path.join(root, "CliPP_mdacc/raw")
    per = []
    sub_ccf = defaultdict(list)       # group -> subclone CCF list
    nclu = defaultdict(list)
    projects = Counter()
    seen = set()
    for proj, sid, rows in iter_structures(raw):
        projects[proj] += 1
        if sid in seen:  # 同一樣本可能有多個 lambda 檔或跨 project 重複，只取第一個
            continue
        seen.add(sid)
        if sid not in S or S[sid]["purity"] is None or not rows:
            continue
        p = S[sid]["purity"]
        cps = []
        for r in rows:
            try:
                cps.append((float(r["cellular_prevalence"]), int(float(r["num_SNV"]))))
            except (KeyError, ValueError):
                pass
        if not cps:
            continue
        cps.sort(reverse=True)
        ccfs = [min(c / p, 1.5) for c, _ in cps]
        subs = ccfs[1:]
        h = S[sid]["hist"]
        for g in ("ALL", h):
            sub_ccf[g].extend(subs)
            nclu[g].append(len(cps))
        per.append([sid, h, proj, p, S[sid]["nrpcc"], len(cps), cps[0][0] / p,
                    ";".join(f"{x:.3f}" for x in subs), min(subs) if subs else ""])
    write_tsv(os.path.join(tdir, "b_clipp_per_sample.tsv"),
              ["sample", "histology", "clipp_project", "purity", "nrpcc", "n_clusters", "clonal_ccf",
               "subclone_ccfs", "min_subclone_ccf"], per)
    rows = []
    for g in ["ALL"] + REP_HIST:
        c, n = sub_ccf.get(g, []), nclu.get(g, [])
        if not n:
            continue
        cnt = Counter(n)
        has_low = [r for r in per if (g == "ALL" or r[1] == g)]
        frac_low = sum(1 for r in has_low if r[8] != "" and r[8] <= 0.15) / len(has_low)
        rows.append([g, len(n), cnt[1] / len(n), cnt[2] / len(n), cnt[3] / len(n), sum(v >= 4 for v in n) / len(n),
                     len(c), summ(c)["median"], summ(c)["q25"], summ(c)["q75"],
                     sum(x <= 0.15 for x in c) / max(len(c), 1), sum(x < 0.30 for x in c) / max(len(c), 1),
                     frac_low])
    write_tsv(os.path.join(tdir, "b_clipp_subclone_ccf_summary.tsv"),
              ["group", "n_samples", "frac_1_cluster", "frac_2_clusters", "frac_3_clusters", "frac_ge4_clusters",
               "n_subclones", "subclone_ccf_median", "subclone_ccf_q25", "subclone_ccf_q75",
               "frac_subclones_ccf_le_0.15", "frac_subclones_ccf_lt_0.30", "frac_samples_with_subclone_ccf_le_0.15"],
              rows)
    # NRPCC 分層：低 CCF subclone 是否只在高 NRPCC 出現
    strata = [(0, 10), (10, 20), (20, 1e9)]
    srows = []
    for lo, hi in strata:
        rr = [r for r in per if r[4] is not None and lo <= r[4] < hi]
        cc = [float(x) for r in rr for x in r[7].split(";") if x]
        if rr:
            srows.append([f"{lo}-{hi if hi < 1e9 else 'inf'}", len(rr), summ(cc)["median"],
                          sum(x <= 0.15 for x in cc) / max(len(cc), 1),
                          sum(1 for r in rr if r[8] != "" and r[8] <= 0.15) / len(rr)])
    write_tsv(os.path.join(tdir, "b_clipp_ccf_by_nrpcc.tsv"),
              ["nrpcc_bin", "n_samples", "subclone_ccf_median", "frac_subclones_ccf_le_0.15",
               "frac_samples_with_subclone_ccf_le_0.15"], srows)
    hist = []
    c = sub_ccf.get("ALL", [])
    for i in range(10):
        lo, hi = i / 10, (i + 1) / 10
        hist.append([f"{lo:.1f}-{hi:.1f}", sum(lo < x <= hi for x in c)])
    hist.append([">1.0", sum(x > 1.0 for x in c)])
    write_tsv(os.path.join(tdir, "b_clipp_subclone_ccf_histogram.tsv"), ["ccf_bin", "n_subclones"], hist)
    print("projects:", dict(projects), "matched samples:", len(per), file=sys.stderr)


if __name__ == "__main__":
    main()
