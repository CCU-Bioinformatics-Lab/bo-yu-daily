#!/usr/bin/env python3
"""Summarize COLO829 allelic states and SNV phasing, and draw the event figure.

Usage: python3 tools/colo829_event_summary.py <baf_windows.tsv> <snv_phase.tsv> <out_dir>
Input tables come from tools/colo829_event_evidence.py.
"""
import csv
import sys
from collections import Counter, defaultdict
from math import exp, lgamma, log
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "Noto Sans CJK JP"
INK, MUTE, LINE = "#1c2a26", "#5a6a62", "#d4dcd6"
COLORS = {"LOH, 2 份": "#f2b8a2", "LOH, 3 份": "#d96b4a", "LOH, 4 份": "#8f2a18", "2:1": "#3f8fb0", "2:2": "#b9c7d6", "其他": "#e7ebe8", "無資料": "#ffffff"}
CORE = ["chr1p", "chr2", "chr6", "chr10", "chr12", "chr17", "chr18", "chr19", "chr21"]
CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]


def binom_p(k, n):
    pm = [exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + n * log(.5)) for i in range(n + 1)]
    return min(1.0, sum(x for x in pm if x <= pm[k] * (1 + 1e-7)))


def label(r):
    st = r["state"]
    ratio = float(r["ratio"]) if r["ratio"] not in ("None", "") else None
    if st == "LOH" and ratio:
        return "LOH, 2 份" if ratio < 1.9 else ("LOH, 3 份" if ratio < 2.6 else "LOH, 4 份")
    return {"2:1": "2:1", "2:2": "2:2", "other": "其他"}.get(st, "無資料")


def side(share):
    return "minor" if share < .42 else ("major" if share > .58 else "balanced")


def main():
    windows, phase, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    W = list(csv.DictReader(open(windows), delimiter="\t"))
    for r in W:
        r["label"] = label(r)
    totals = Counter(r["label"] for r in W)
    with open(out / "state_totals.tsv", "w") as f:
        f.write("state\twindows\tapprox_mb\n")
        for k, v in totals.most_common():
            f.write(f"{k}\t{v}\t{v * 3}\n")

    R = list(csv.DictReader(open(phase), delimiter="\t"))
    by = defaultdict(Counter)
    control = Counter()
    for r in R:
        chr1p = r["chrom"] == "chr1" and int(r["pos"]) < 85_000_000
        if r["result"] != "linked":
            continue
        s = side(float(r["allele_share"]))
        if r["state"] == "LOH":
            control[s] += 1
        if chr1p:
            by["chr1p"][s] += 1
        elif r["state"] == "2:1":
            by[r["chrom"]][s] += 1
    rows = []
    for c, v in by.items():
        n = v["major"] + v["minor"]
        rows.append(dict(region=c, used=c in CORE, major=v["major"], minor=v["minor"], balanced=v["balanced"], minor_share=round(v["minor"] / n, 3) if n else "", p=round(binom_p(v["minor"], n), 4) if n else ""))
    rows.sort(key=lambda r: (not r["used"], CORE.index(r["region"]) if r["region"] in CORE else 0))
    with open(out / "major_minor_snv.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys(), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    M = sum(r["major"] for r in rows if r["used"])
    m = sum(r["minor"] for r in rows if r["used"])
    print("state Mb", {k: v * 3 for k, v in totals.items()})
    print("core major minor", M, m, "minor share", round(m / (M + m), 3), "ratio", round(M / m, 3), "p", binom_p(m, M + m))
    print("LOH control", dict(control), "phase results", Counter(r["result"] for r in R))

    # Figure: allelic state along each chromosome, then major and minor counts
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 6.6), dpi=170, gridspec_kw={"width_ratios": [2.3, 1]})
    for i, c in enumerate(CHROMS):
        y = len(CHROMS) - i
        v = sorted((r for r in W if r["chrom"] == c), key=lambda r: int(r["start"]))
        for r in v:
            a.barh(y, 3, left=int(r["start"]) / 1e6 - 1, height=.72, color=COLORS[r["label"]], edgecolor="none")
    a.set_yticks([len(CHROMS) - i for i in range(len(CHROMS))], [c.replace("chr", "") for c in CHROMS], fontsize=8.5, color=INK)
    a.set_xlabel("GRCh38 位置（Mb），每 3 Mb 抽 1 個視窗", fontsize=9.5, color=INK)
    a.set_title("每段留下幾條、各幾份（ONT R10）", fontsize=11, color=INK, loc="left", fontweight="bold")
    a.set_xlim(0, 250)
    a.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=COLORS[k]) for k in list(COLORS)[:6]], labels=["只剩一條，2 份", "只剩一條，3 份", "只剩一條，4 份", "兩條 2:1", "兩條 2:2", "其他"],
             loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK)
    core = [r for r in rows if r["used"]]
    for i, r in enumerate(core):
        y = len(core) - i
        s = r["major"] + r["minor"]
        b.barh(y, r["major"] / s, height=.68, color="#3f8fb0", edgecolor="white", linewidth=1.5)
        b.barh(y, r["minor"] / s, left=r["major"] / s, height=.68, color="#b9c7d6", edgecolor="white", linewidth=1.5)
        b.text(r["major"] / s / 2, y, str(r["major"]), ha="center", va="center", color="white", fontsize=8.5)
        b.text(r["major"] / s + r["minor"] / s / 2, y, str(r["minor"]), ha="center", va="center", color=INK, fontsize=8.5)
    b.axvline(.5, color=INK, lw=1.1)
    b.set_yticks([len(core) - i for i in range(len(core))], [r["region"].replace("chr", "") for r in core], fontsize=8.5, color=INK)
    b.set_xlim(0, 1)
    b.set_xlabel("兩條的突變比例", fontsize=9.5, color=INK)
    b.set_title("2:1 區：突變在哪一條", fontsize=11, color=INK, loc="left", fontweight="bold")
    b.text(.02, -0.17, "深色：2 份那條　淺色：1 份那條", transform=b.transAxes, fontsize=8.5, color=MUTE)
    for ax in (a, b):
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(LINE)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", colors=MUTE, labelsize=8.5)
    fig.tight_layout()
    fig.savefig(out / "allelic_states.png")


if __name__ == "__main__":
    main()
