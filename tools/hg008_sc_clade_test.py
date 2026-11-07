#!/usr/bin/env python3
"""Test the rebuilt HG008 clone tree against the 119 PTA single cells.

A cell's truncal recall is its sensitivity. For a branch, rel = (branch recall) / (truncal recall).
Rules fixed before the first look at the cell results:
  carrier when rel >= 0.5, non-carrier when rel <= 0.2, otherwise uncertain.
  Cells with truncal recall < MIN_SENS are left out. Branches with < MIN_SITES sites are not tested.
  Branch SNVs are the CN-clean SNVs of a chosen clade, or the private SNVs of one clone.
Tree predictions:
  nested clades: a carrier of the inner clade must not be a non-carrier of the outer clade.
  disjoint branches: no cell carries both.
Controls: low-QUAL patterns with at least MIN_SITES sites should stay near zero.

Clones and cells are different samples, so a clade with no carrier cell does not refute it: its
lineage may be rare at p23. Only rel values and the nesting can support or contradict the tree.

Output (OUT_DIR): cell_by_branch.tsv, cell_sensitivity.tsv, branch_summary.tsv, nesting.tsv,
batch.tsv, control_patterns.tsv
Usage: python3 -I tools/hg008_sc_clade_test.py SNV_CLASSES.tsv CLADES.tsv SC_CALLS.tsv.gz SC_VCF_DIR OUT_DIR
"""
import collections
import csv
import gzip
import itertools
import re
import statistics
import sys
from pathlib import Path

CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
TRUNCAL = ",".join(CLONES)
CARRIER, NON_CARRIER = 0.5, 0.2
MIN_SENS = 0.3
MIN_SITES = 10


def state(rel):
    return "carrier" if rel >= CARRIER else ("non" if rel <= NON_CARRIER else "uncertain")


def main():
    classes_path, clades_path, calls_path, vcf_dir, out = sys.argv[1:6]
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    site = {}
    with open(classes_path) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            site[(r["chrom"], int(r["pos"]))] = (r["pattern"], r["class"])
    with open(clades_path) as fh:
        clades = [r["clade"] for r in csv.DictReader(fh, delimiter="\t")]

    def branch_of(pattern, kind):
        if pattern == TRUNCAL and kind == "truncal":
            return "truncal"
        if kind == "private":
            return pattern
        if kind == "shared_clean" and pattern in clades:
            return pattern
        if kind == "low_qual":
            return "lowqual:" + pattern
        return None

    size = collections.Counter(branch_of(*v) for v in site.values())
    del size[None]
    plate = {}
    for path in Path(vcf_dir).glob("*.vcf.gz"):
        m = re.match(r"(\d+)-NIST-PL01-(SC\d+)-", path.name)
        plate[m.group(2)] = m.group(1)
    called = collections.defaultdict(collections.Counter)
    with gzip.open(calls_path, "rt") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            value = site.get((r["chrom"], int(r["pos"])))
            if value:
                called[r["cell"]][branch_of(*value)] += 1

    sens = {cell: called[cell]["truncal"] / size["truncal"] for cell in plate}
    kept = sorted(c for c in plate if sens[c] >= MIN_SENS)
    with open(out / "cell_sensitivity.tsv", "w") as fh:
        fh.write("cell\tplate\ttruncal_called\ttruncal_sites\tsensitivity\tkept\n")
        for cell in sorted(plate):
            fh.write(f"{cell}\t{plate[cell]}\t{called[cell]['truncal']}\t{size['truncal']}\t{sens[cell]:.4f}\t{int(cell in kept)}\n")

    branches = [b for b in clades + CLONES if size[b] >= MIN_SITES]
    rel = {c: {b: called[c][b] / size[b] / sens[c] for b in size if b != "truncal"} for c in kept}
    with open(out / "cell_by_branch.tsv", "w") as fh:
        fh.write("cell\tplate\tsensitivity\t" + "\t".join(branches) + "\n")
        for c in kept:
            fh.write(f"{c}\t{plate[c]}\t{sens[c]:.3f}\t" + "\t".join(f"{rel[c][b]:.3f}" for b in branches) + "\n")

    states = {b: {c: state(rel[c][b]) for c in kept} for b in branches}
    with open(out / "branch_summary.tsv", "w") as fh:
        fh.write("branch\tkind\tn_sites\tcarrier\tuncertain\tnon_carrier\tmedian_rel_carrier\tmedian_rel_non\n")
        for b in clades + CLONES:
            if size[b] < MIN_SITES:
                fh.write(f"{b}\t{'clade' if b in clades else 'private'}\t{size[b]}\tNA\tNA\tNA\tNA\tNA\n")
                continue
            n = collections.Counter(states[b].values())
            carrier = [rel[c][b] for c in kept if states[b][c] == "carrier"]
            non = [rel[c][b] for c in kept if states[b][c] == "non"]
            fh.write(f"{b}\t{'clade' if b in clades else 'private'}\t{size[b]}\t{n['carrier']}\t{n['uncertain']}\t{n['non']}\t"
                     f"{statistics.median(carrier) if carrier else float('nan'):.3f}\t{statistics.median(non) if non else float('nan'):.3f}\n")

    with open(out / "nesting.tsv", "w") as fh:
        fh.write("branch_a\tbranch_b\tprediction\tcarriers_a\tcarriers_b\tcarriers_both\tviolations\tviolating_cells\n")
        for a, b in itertools.combinations(branches, 2):
            sa, sb = set(a.split(",")), set(b.split(","))
            if sa < sb or sb < sa:
                inner, outer = (a, b) if sa < sb else (b, a)
                bad = [c for c in kept if states[inner][c] == "carrier" and states[outer][c] == "non"]
                prediction = f"{inner} inside {outer}"
            elif not sa & sb:
                bad = [c for c in kept if states[a][c] == "carrier" and states[b][c] == "carrier"]
                prediction = "disjoint"
            else:
                continue
            ca = sum(states[a][c] == "carrier" for c in kept)
            cb = sum(states[b][c] == "carrier" for c in kept)
            both = sum(states[a][c] == "carrier" and states[b][c] == "carrier" for c in kept)
            fh.write(f"{a}\t{b}\t{prediction}\t{ca}\t{cb}\t{both}\t{len(bad)}\t{','.join(bad)}\n")

    plates = sorted(set(plate.values()))
    with open(out / "batch.tsv", "w") as fh:
        fh.write("branch\t" + "\t".join(f"{p}_carrier\t{p}_cells" for p in plates) + "\n")
        for b in branches:
            cols = []
            for p in plates:
                cells = [c for c in kept if plate[c] == p]
                cols += [str(sum(states[b][c] == "carrier" for c in cells)), str(len(cells))]
            fh.write(b + "\t" + "\t".join(cols) + "\n")

    with open(out / "control_patterns.tsv", "w") as fh:
        fh.write("pattern\tn_sites\tcarrier\tuncertain\tnon_carrier\tmedian_rel\n")
        for name, n in size.most_common():
            if name.startswith("lowqual:") and n >= MIN_SITES:
                values = [rel[c][name] for c in kept]
                count = collections.Counter(state(v) for v in values)
                fh.write(f"{name[8:]}\t{n}\t{count['carrier']}\t{count['uncertain']}\t{count['non']}\t{statistics.median(values):.3f}\n")
    print(f"{len(plate)} cells, kept {len(kept)}; median sensitivity {statistics.median(sens.values()):.3f}")


if __name__ == "__main__":
    main()
