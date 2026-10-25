"""Check longbulksim random specs against the TRACERx 421 / PCAWG cohort statistics.

Draws N specs, replays each, and summarises per spec:
  inputs     n_clones, linear, purity, subclone CCF (taken from the blueprint, so they test the
             CCF projection and clone merging)
  emergent   mutation-loss fraction and its mechanism, early fraction in gained segments,
             subclonal CN share of SNVs (set by event order and placement, never tuned)
Then simulates the first --run specs end to end, to check that every output is writable.

Usage: python3 tools/random_tree_validation.py OUT_DIR [--n 1000] [--seed 1] [--run 20]
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "longbulksim"))
from longbulksim.model import HPS, NORMAL, lost, parse_spec, replay  # noqa: E402
from longbulksim.random_tree import draw_spec, load_blueprints  # noqa: E402
from longbulksim.simulate import run  # noqa: E402

# lab_report/2026-10-25_tracerx_event_stats (single region) and _pcawg_event_stats
COHORT = {
    "n_clones_median": ("TRACERx single region (before merging)", 5),
    "frac_linear": ("TRACERx single region", 0.73),
    "purity_median": ("TRACERx region ACF", 0.41),
    "subclone_ccf_median": ("TRACERx single region", 0.58),
    "loss_frac_median": ("TRACERx per tumour, strict lower bound", 0.0),
    "loss_frac_q90": ("TRACERx per tumour", 0.014),
    "loss_frac_max": ("TRACERx per tumour", 0.117),
    "loss_deletion_share": ("TRACERx lost mutations, deletion type", 0.75),
    "early_frac_gain_median": ("PCAWG 2:1 clonal regions; generated = clonal gains", 0.28),
}


def spec_stats(raw):
    spec = parse_spec(raw)
    g = replay(spec)
    clones = list(spec.parent)
    kids = {c: [k for k in clones if spec.parent[k] == c] for c in clones}
    n_snv = sum(r.count for r in spec.roles.values())
    lost_by = lost(spec, g)
    gone = set().union(*lost_by.values()) if lost_by else set()
    # TRACERx definition: deletion type if total CN drops where the SNV is first lost
    mech = {"loss": 0, "cnloh": 0}
    tot = lambda c, seg: sum(len(g[c][seg][h]) for h in HPS)
    for r in gone:
        seg = spec.roles[r].segment
        c = next(c for c in clones if r in lost_by.get(c, ()))
        mech["loss" if tot(c, seg) < tot(spec.parent[c] or NORMAL, seg) else "cnloh"] += 1
    early = {"clonal": [], "subclonal": []}
    for c, ev in spec.edges.items():
        for e in ev:
            if getattr(e, "kind", None) == "gain":
                carried = [sum(r in cp for cp in g[c][e.segment][h])
                           for r, role in spec.roles.items() if role.segment == e.segment
                           for h in HPS if any(r in cp for cp in g[c][e.segment][h])]
                if carried:
                    early["clonal" if c == spec.root else "subclonal"].append(
                        (int((np.array(carried) >= 2).sum()), len(carried)))
    sub_cn = {e.segment for c, ev in spec.edges.items() if c != spec.root for e in ev
              if hasattr(e, "kind")}
    return {
        "n_clones": len(clones),
        "linear": all(len(v) <= 1 for v in kids.values()),
        "purity": spec.purity,
        "subclone_ccf": [spec.ccf(c) for c in clones if c != spec.root],
        "loss_frac": len(gone) / n_snv,
        "loss_mech": mech,
        "early": early,
        "subclonal_cn_snv_frac": sum(r.count for r in spec.roles.values()
                                     if r.segment in sub_cn) / n_snv,
        "merged": raw["source"]["merged_clones"],
        "blueprint_clones": raw["source"]["blueprint_clones"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--run", type=int, default=20)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    regions, events = load_blueprints()
    rng = np.random.default_rng(a.seed)
    raws = [draw_spec(rng, regions, events) for _ in range(a.n)]
    st = [spec_stats(r) for r in raws]

    loss = np.array([s["loss_frac"] for s in st])
    mech = {k: sum(s["loss_mech"][k] for s in st) for k in ("loss", "cnloh")}
    # PCAWG pools all SNVs in a sample's 2:1 regions; pool per spec the same way (>= 5 SNVs)
    early = {k: [sum(a for a, _ in s["early"][k]) / sum(n for _, n in s["early"][k])
                 for s in st if sum(n for _, n in s["early"][k]) >= 5]
             for k in ("clonal", "subclonal")}
    ccf = [x for s in st for x in s["subclone_ccf"]]
    got = {
        "n_clones_median": float(np.median([s["n_clones"] for s in st])),
        "frac_linear": float(np.mean([s["linear"] for s in st])),
        "purity_median": float(np.median([s["purity"] for s in st])),
        "subclone_ccf_median": float(np.median(ccf)),
        "loss_frac_median": float(np.median(loss)),
        "loss_frac_q90": float(np.quantile(loss, 0.9)),
        "loss_frac_max": float(loss.max()),
        "loss_deletion_share": mech["loss"] / max(sum(mech.values()), 1),
        "early_frac_gain_median": float(np.median(early["clonal"])) if early["clonal"] else None,
    }
    extra = {
        "n_specs": a.n,
        "blueprint_n_clones_median": float(np.median([s["blueprint_clones"] for s in st])),
        "frac_specs_with_merge": float(np.mean([s["merged"] > 0 for s in st])),
        "frac_specs_with_loss": float(np.mean(loss > 0)),
        "n_lost_roles": mech,
        "n_specs_with_gain_snvs_ge5": {k: len(v) for k, v in early.items()},
        "early_frac_subclonal_gain_median": float(np.median(early["subclonal"])),
        "subclonal_cn_snv_frac_median": float(np.median([s["subclonal_cn_snv_frac"] for s in st])),
        "n_clones_hist": {int(k): int(v) for k, v in zip(*np.unique(
            [s["n_clones"] for s in st], return_counts=True))},
    }
    rows = [[k, COHORT[k][0], COHORT[k][1], None if got[k] is None else round(got[k], 4)]
            for k in COHORT]
    with open(out / "cohort_vs_generated.tsv", "w") as fh:
        fh.write("metric\tcohort_source\tcohort\tgenerated\n")
        fh.writelines("\t".join(map(str, r)) + "\n" for r in rows)
    with open(out / "per_spec.tsv", "w") as fh:
        fh.write("spec\tsource_region\tn_clones\tlinear\tpurity\tloss_frac\t"
                 "subclonal_cn_snv_frac\tmerged\n")
        for i, (r, s) in enumerate(zip(raws, st)):
            fh.write(f"{i}\t{r['source']['region']}\t{s['n_clones']}\t{s['linear']}\t"
                     f"{s['purity']}\t{s['loss_frac']:.4f}\t{s['subclonal_cn_snv_frac']:.4f}\t"
                     f"{s['merged']}\n")

    ran = 0
    for r in raws[:a.run]:
        with tempfile.TemporaryDirectory() as d:
            run(parse_spec(r), 1, d)
            ran += (Path(d) / "input/pairs.tsv").exists()
    extra["end_to_end_runs_ok"] = f"{ran}/{min(a.run, a.n)}"
    (out / "summary.json").write_text(json.dumps({"cohort_vs_generated": got, **extra}, indent=1))
    for r in rows:
        print("\t".join(map(str, r)))
    print(json.dumps(extra, indent=1))


if __name__ == "__main__":
    main()
