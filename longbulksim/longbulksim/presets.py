"""Cohort presets for the parametric mode (param_tree.Params).

A preset sets the genome and sample parameters from one cohort. Tree parameters (n_clones,
p_linear, ccf_alpha, min_ccf, min_gap) always stay at the TRACERx 421 values, and observation
parameters (het map, errors, caller) are never set by a preset.

  tracerx               TRACERx 421 single-region medians (the Params defaults)
  pcawg                 PCAWG medians over all 2,658 preferred samples
  pcawg:<histology>     PCAWG medians of one histology with >= 20 samples, e.g. pcawg:Lung-AdenoCA

PCAWG values come from the open files in /big8_disk/boyu114/benchmark_data/PCAWG (GRCh37):
  n_snv            median clonal + subclonal SNVs (WGS)
  density_per_mb   n_snv / 2,881 Mb
  prop_truncal     median clonal share among samples with >= 1 subclone (presets keep >= 2 clones)
  purity, depth    median consensus purity and tumour coverage
  wgd_prob         share of samples with wgd_status = wgd
  n_segments       median autosomal consensus CN segments
  prop_subclonal_cn  median bp share where Battenberg has two states
  gain/loss/loh    median bp shares of trunk CN category relative to 1:1 (2:2 with WGD), per group
Exact CN states and subclonal changes are still resampled from TRACERx (param_tree.load_pools).

Build: python3 -m longbulksim.presets build PCAWG_DIR   (writes data/pcawg_presets.tsv)
       python3 -m longbulksim.presets list
"""
import csv
import io
import sys
import tarfile
from pathlib import Path

import numpy as np

from .model import DATA_DIR

TABLE = DATA_DIR / "pcawg_presets.tsv"
GENOME_MB = 2881
MIN_SAMPLES = 20
GROUP_MIN = 5  # fewer samples in a WGD group: use the all-PCAWG value of that group
FIELDS = ("n_snv", "density_per_mb", "prop_truncal", "purity", "depth", "wgd_prob", "n_segments",
          "prop_subclonal_cn", "gain_wgd", "loss_wgd", "loh_wgd", "gain_nowgd", "loss_nowgd",
          "loh_nowgd")
INT_FIELDS = ("n_snv", "n_segments")
TRACERX = {}  # Params defaults


def names():
    return ["tracerx"] + ([r["preset"] for r in _rows()] if TABLE.exists() else [])


def load(name):
    """Params field values of a preset ({} for tracerx)."""
    if name == "tracerx":
        return dict(TRACERX)
    for r in _rows():
        if r["preset"] == name:
            return {k: (int(float(r[k])) if k in INT_FIELDS else float(r[k])) for k in FIELDS}
    raise ValueError(f"unknown preset {name!r}; choose from: {', '.join(names())}")


def _f(x):
    try:
        return float(x)
    except ValueError:
        return float("nan")


def _sample_cn(rows, wgd):
    base = 2 if wgd else 1
    bp = {"gain": 0, "loss": 0, "loh": 0}
    tot = sub = nseg = 0
    for r in rows:
        if r["chromosome"] in ("X", "Y"):
            continue
        a, b = _f(r["major_cn"]), _f(r["minor_cn"])
        if np.isnan(a) or np.isnan(b):
            continue
        length = int(float(r["end"])) - int(float(r["start"])) + 1
        nseg += 1
        tot += length
        if max(a, b) > 0 and min(a, b) == 0:
            bp["loh"] += length
        elif a < base or b < base:
            bp["loss"] += length if max(a, b) > 0 else 0
        elif a > base or b > base:
            bp["gain"] += length
        if _f(r.get("battenberg_frac1_A", "nan")) < 1:
            sub += length
    if not tot:
        return None
    return {"n_segments": nseg, "prop_subclonal_cn": sub / tot, **{k: v / tot for k, v in bp.items()}}


def _summarise(samples, fallback=None):
    med = lambda k, s: float(np.nanmedian([x[k] for x in s])) if s else float("nan")
    withsub = [x for x in samples if x["n_subclones"] >= 1]
    out = {"n_samples": len(samples), "n_snv": med("n_snv", samples),
           "prop_truncal": med("truncal", withsub), "purity": med("purity", samples),
           "depth": med("depth", samples), "wgd_prob": float(np.mean([x["wgd"] for x in samples])),
           "n_segments": med("n_segments", samples),
           "prop_subclonal_cn": med("prop_subclonal_cn", samples)}
    out["density_per_mb"] = out["n_snv"] / GENOME_MB
    for wgd, tag in ((True, "wgd"), (False, "nowgd")):
        grp = [x for x in samples if x["wgd"] == wgd]
        for k in ("gain", "loss", "loh"):
            v = med(k, grp) if len(grp) >= GROUP_MIN else (fallback or {}).get(f"{k}_{tag}", float("nan"))
            out[f"{k}_{tag}"] = v
    return out


def build(pcawg_dir, out=TABLE):
    root = Path(pcawg_dir) / "icgc25k_open"
    ann = {r["tumour_aliquot_id"]: r for r in csv.DictReader(
        open(root / "evolution_and_heterogeneity/icgc_sample_annotations_summary_table.txt"),
        delimiter="\t") if r["is_preferred"] == "TRUE"}
    samples = []
    with tarfile.open(root / "consensus_cnv/consensus.20170119.somatic.cna.annotated.tar.gz") as t:
        for m in t:
            aid = m.name.split("/")[-1].split(".")[0]
            if not m.isfile() or aid not in ann:
                continue
            a = ann[aid]
            wgd = a["wgd_status"] == "wgd"
            cn = _sample_cn(csv.DictReader(io.TextIOWrapper(t.extractfile(m)), delimiter="\t"), wgd)
            if cn is None:
                continue
            c, s = _f(a["num_clonal_snvs"]), _f(a["num_subclonal_snvs"])
            samples.append({"histology": a["histology_abbreviation"], "wgd": wgd,
                            "n_subclones": _f(a["num_subclones"]), "n_snv": c + s,
                            "truncal": c / (c + s) if c + s else float("nan"),
                            "purity": _f(a["purity"]), "depth": _f(a["cov_tumour"]), **cn})
    rows = [("pcawg", _summarise(samples))]
    hist = sorted({x["histology"] for x in samples})
    for h in hist:
        sel = [x for x in samples if x["histology"] == h]
        if len(sel) >= MIN_SAMPLES:
            rows.append((f"pcawg:{h}", _summarise(sel, rows[0][1])))
    with open(out, "w") as fh:
        fh.write("# PCAWG presets; built by python3 -m longbulksim.presets build (see presets.py)\n")
        fh.write("\t".join(("preset", "n_samples") + FIELDS) + "\n")
        for name, v in rows:
            fh.write("\t".join([name, str(v["n_samples"])] +
                               [f"{v[k]:.4g}" for k in FIELDS]) + "\n")
    return out


def _rows():
    with open(TABLE) as fh:
        return list(csv.DictReader((ln for ln in fh if ln[0] != "#"), delimiter="\t"))


def main():
    if sys.argv[1:2] == ["build"] and len(sys.argv) == 3:
        print(build(sys.argv[2]))
    elif sys.argv[1:] == ["list"]:
        print("tracerx\t(TRACERx 421 single-region medians; Params defaults)")
        for r in _rows():
            print(f"{r['preset']}\t(n = {r['n_samples']})")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
