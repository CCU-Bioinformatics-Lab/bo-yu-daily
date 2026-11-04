#!/usr/bin/env python3
"""How many SNVs and subclones a simulated ONT somatic caller misses (longbulksim v0.5 curves).

GRID_DIR holds one directory per grid cell (p<purity>_d<depth>/sim_*/), made by
longbulksim.generate with --caller none, so input/data.tsv has every SNV. Detection is the
last random step in the simulator, so applying the caller curve to these counts gives the same
distribution as rerunning with --caller.

A subclone is visible when >= 2 of its SNVs are called.

Usage: python3 tools/caller_impact.py GRID_DIR OUT_TSV_PREFIX
Writes <prefix>_by_cell.tsv and <prefix>_by_ccf.tsv.
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "longbulksim"))
from longbulksim.simulate import detect, load_caller  # noqa: E402

CALLERS = ("clairs", "deepsomatic")
CCF_BINS = [(0, 0.2), (0.2, 0.5), (0.5, 1.01)]
MIN_VISIBLE = 2


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sim_stats(sim, rng, coef):
    truth = {r["mutation_id"]: r for r in read_tsv(sim / "truth/truth.tsv")}
    data = read_tsv(sim / "input/data.tsv")
    alt = [int(r["alt_counts"]) for r in data]
    dep = [int(r["alt_counts"]) + int(r["ref_counts"]) for r in data]
    root = next(r["clone"] for r in read_tsv(sim / "truth/truth_tree.tsv") if r["parent"] in ("root", "N"))
    out = {}
    for c in CALLERS:
        hit = detect(rng, coef[c], alt, dep)
        n = defaultdict(int)
        k = defaultdict(int)
        ccf = {}
        for r, h in zip(data, hit):
            t = truth[r["mutation_id"]]
            n[t["origin_clone"]] += 1
            k[t["origin_clone"]] += int(h)
            ccf[t["origin_clone"]] = float(t["origin_ccf"])
        subs = [x for x in n if x != root]
        out[c] = {
            "called": hit.mean(),
            "called_truncal": k[root] / n[root],
            "called_subclonal": (sum(k[x] for x in subs) / sum(n[x] for x in subs)
                                 if subs else float("nan")),
            "subclones": len(subs),
            "subclones_visible": sum(k[x] >= MIN_VISIBLE for x in subs),
            "subclone_rows": [(ccf[x], k[x] >= MIN_VISIBLE, k[x] / n[x]) for x in subs],
        }
    return out


def main(grid, prefix):
    coef = {c: load_caller(c) for c in CALLERS}
    rng = np.random.default_rng(1)
    cells, by_ccf = [], defaultdict(list)
    for cell in sorted(Path(grid).iterdir()):
        m = re.fullmatch(r"p([\d.]+)_d([\d.]+)", cell.name)
        if not m:
            continue
        purity, depth = float(m.group(1)), float(m.group(2))
        sims = [sim_stats(s, rng, coef) for s in sorted(cell.glob("sim_*"))]
        for c in CALLERS:
            v = [s[c] for s in sims]
            subs = sum(x["subclones"] for x in v)
            cells.append([purity, depth, c, len(v),
                          f"{np.mean([x['called'] for x in v]):.3f}",
                          f"{np.mean([x['called_truncal'] for x in v]):.3f}",
                          f"{np.nanmean([x['called_subclonal'] for x in v]):.3f}",
                          subs, sum(x["subclones_visible"] for x in v),
                          f"{sum(x['subclones_visible'] for x in v) / subs:.3f}" if subs else "nan"])
            for x in v:
                for row in x["subclone_rows"]:
                    by_ccf[(purity, depth, c)].append(row)
    with open(f"{prefix}_by_cell.tsv", "w") as fh:
        fh.write("purity\tdepth\tcaller\tn_sims\tcalled_all\tcalled_truncal\tcalled_subclonal\t"
                 "subclones\tsubclones_visible\tfrac_visible\n")
        fh.writelines("\t".join(map(str, r)) + "\n" for r in cells)
    with open(f"{prefix}_by_ccf.tsv", "w") as fh:
        fh.write("purity\tdepth\tcaller\tccf_bin\tsubclones\tfrac_visible\tmean_called\n")
        for (p, d, c), rows in sorted(by_ccf.items()):
            for lo, hi in CCF_BINS:
                sel = [r for r in rows if lo <= r[0] < hi]
                if sel:
                    fh.write(f"{p}\t{d}\t{c}\t{lo}-{min(hi, 1)}\t{len(sel)}\t"
                             f"{np.mean([r[1] for r in sel]):.3f}\t{np.mean([r[2] for r in sel]):.3f}\n")
    print(Path(f"{prefix}_by_cell.tsv").read_text())
    print(Path(f"{prefix}_by_ccf.tsv").read_text())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
