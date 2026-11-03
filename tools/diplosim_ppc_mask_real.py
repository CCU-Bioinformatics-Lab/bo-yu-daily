#!/usr/bin/env python3
"""Recompute the real side of a diplosim PPC with regions masked, reusing the stored sim statistics.

Why: the normal HCC1395BL is a B-lymphoblastoid line. V(D)J recombination deletes part of the
immunoglobulin loci on one allele, so in a tumour/normal mix the normal reads cannot raise the
minor HP there, and the "minor HP < 0.1" sites stay at every purity
(lab_report/2026-11-03_diplosim_mask_ig_loci). diplosim's normal is diploid everywhere and uses
artificial coordinates, so only the real side is masked and the sim statistics are reused as is.

Usage:
  python3 -I tools/diplosim_ppc_mask_real.py SRC_DIR OUT_DIR
    SRC_DIR: a run with tables/real_per_snv.tsv and tables/sim_stats.json (e.g. one purity of
             lab_report/2026-11-01_diplosim_detection_curve)
    OUT_DIR: gets tables/ppc_stats.tsv, real_stats.json, masked_sites.tsv
The caller filter comes from DIPLOSIM_PPC_MIN_ALT / DIPLOSIM_PPC_MIN_VAF, as in the source run.
"""
import csv
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diplosim_ppc_hcc1395 import COLS, q, stats  # noqa: E402

# GRCh38 immunoglobulin loci (NCBI Gene: IGH, IGK, IGL).
MASK = [("chr14", 105586437, 106879844, "IGH"),
        ("chr2", 88857361, 90235368, "IGK"),
        ("chr22", 22026076, 22922913, "IGL")]


def masked(chrom, pos):
    return next((name for c, lo, hi, name in MASK if c == chrom and lo <= pos <= hi), None)


def main(src, out):
    (out / "tables").mkdir(parents=True, exist_ok=True)
    kept, dropped = [], []
    with open(src / "tables" / "real_per_snv.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            name = masked(r["chrom"], int(r["pos"]))
            (dropped if name else kept).append((r, name))
    real = stats([tuple(int(r[k]) for k in COLS) for r, _ in kept])
    sims = json.loads((src / "tables" / "sim_stats.json").read_text())
    with open(out / "tables" / "ppc_stats.tsv", "w") as f:
        f.write("statistic\treal\tsim_median\tsim_q2.5\tsim_q97.5\treal_rank_in_sim\tverdict\n")
        for k, v in real.items():
            sv = [s[k] for s in sims]
            lo, hi = q(sv, 0.025), q(sv, 0.975)
            rank = sum(x < v for x in sv) / len(sv)
            f.write(f"{k}\t{v:.4g}\t{statistics.median(sv):.4g}\t{lo:.4g}\t{hi:.4g}\t{rank:.3f}\t"
                    f"{'in' if lo <= v <= hi else 'OUT'}\n")
    (out / "tables" / "real_stats.json").write_text(json.dumps(real))
    with open(out / "tables" / "masked_sites.tsv", "w") as f:
        f.write("chrom\tpos\tlocus\n")
        f.writelines(f"{r['chrom']}\t{r['pos']}\t{n}\n" for r, n in dropped)
    print(f"{src.name}: masked {len(dropped)} of {len(kept) + len(dropped)} real SNVs")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
