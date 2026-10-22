"""Rerun the CONIPHER benchmark simulations (TRACERx_simulation_tool) from their recorded seeds.

usage: python tools/conipher_sim_rerun.py TOOL_SRC ZENODO_DATASET_DIR OUT_DIR [--names LTXSIM001,...]
                                          [--cov-window N]

TOOL_SRC: src/ of TRACERx_simulation_tool, checked out at 8c8d173 (same simulation path as the
          2022-04-30 version that existed when the Zenodo files were written on 2022-06-16).
ZENODO_DATASET_DIR: unzipped Zenodo 10048165 dataset2 (no noise) or dataset1 (noise), with
          <name>/sim/<name>_info.tsv and the other six outputs.

For each simulation this calls tx_simulation() with the parameters and random_seed from
<name>_info.tsv. Arguments that _info.tsv does not record are taken from
scripts/make_tx_simulations.ipynb defaults (min/max clones 3/8, max_positions 20,
minimum_branch_length 1, all_leaf_observed True, noise_type random); n_noise_clones is the
length of the recorded noise_clones list. Two inputs are not recorded, so they are searched:
  prop_mutloss_positions   only the realised, rounded prop_mut_lost is recorded. Tried in order:
                           the recorded value, then the notebook's np.arange(0.1, 0.26, 0.01).
                           Kept: the first whose _info.tsv and _treeedges.tsv are byte-identical
                           and whose _cloneprops.tsv matches to 1e-12 (all three are fixed before
                           coverage is used); else the first that matches all but _info.tsv.
                           _info.tsv matters when the input was capped: the cap adds a warning.
  coverage                 tried as integers round(mean author DEPTH) +- --cov-window;
                           kept: the first whose DEPTH and VAR_COUNT match exactly
Writes OUT_DIR/<name>/sim/ (the tool's own six files plus the png) and OUT_DIR/compare.tsv,
which says per file whether the rerun is byte-identical to the Zenodo file.
Needs ~/venvs/txsim (numpy 1.22.4, pandas 1.4.2, scipy 1.8.1, graphviz 0.20, ipython).
First used in lab_report/2026-10-22_pairtree_conipher_sim_rerun/.
"""
import argparse, ast, contextlib, io, sys
from pathlib import Path

import numpy as np
import pandas as pd

SUFFIXES = ["_info.tsv", ".tsv", "_TX.tsv", "_cloneprops.tsv", "_treeedges.tsv", "_events.tsv"]


def read_info(path):
    raw = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False).set_index("0")["1"].to_dict()
    def num(k):
        return ast.literal_eval(raw[k])
    return raw, {
        "n_nodes": num("n_nodes"), "n_positions": num("n_positions"), "n_samples": num("n_samples"),
        "min_clones_per_sample": num("min_clones_per_sample"), "max_clones_per_sample": num("max_clones_per_sample"),
        "prop_truncal_snvs": num("prop_truncal_snvs"), "prop_pos_gained": num("prop_pos_gained"),
        "prop_pos_lost": num("prop_pos_lost"), "prop_gained_truncal": num("prop_gained_truncal"),
        "prop_lost_truncal": num("prop_lost_truncal"), "clonal_wgd": num("clonal_wgd"),
        "subclonal_wgd": num("subclonal_wgd"), "n_subclonal_wgd": num("n_subclonal_wgd"),
        "constant_multiplicity": num("constant_multiplicity"), "prop_mutloss_positions": num("prop_mut_lost"),
        "mutloss_truncal": num("mutloss_truncal"), "min_tumour_purity": num("min_tumour_purity"),
        "max_tumour_purity": num("max_tumour_purity"), "fract_noise": num("fract_noise"),
        "noise_type": raw["noise_type"], "rs": num("random_seed"),
    }


def n_noise_clones(raw):
    return len(ast.literal_eval(raw["noise_clones"])) if raw["noise_clones"] else 1


def csv_bytes(df):
    return df.to_csv(index=False, sep="\t").encode()


def run(tx_simulation, name, p, coverage, out_dir=None):
    kw = dict(p, max_positions=20, minimum_branch_length=1, gain_events=None, loss_events=None,
              all_leaf_observed=True, coverage=coverage, display_plots=False,
              ccf_vaf_plots=False, display_output=True)
    if out_dir is None:
        kw.update(output_directory=None, save_output=False)
    else:
        kw.update(output_directory=str(out_dir), save_output=True)
    with contextlib.redirect_stdout(io.StringIO()):
        return tx_simulation(name, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tool_src")
    ap.add_argument("zenodo")
    ap.add_argument("out")
    ap.add_argument("--names")
    ap.add_argument("--cov-window", type=int, default=10)
    a = ap.parse_args()
    sys.path.insert(0, a.tool_src)
    from simulate import tx_simulation

    zen, out = Path(a.zenodo), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = a.names.split(",") if a.names else sorted(d.name for d in zen.iterdir() if d.name.startswith("LTXSIM"))
    rows = []
    for name in names:
        src = zen / name / "sim"
        if (out / name).exists():
            print(f"{name}: exists, skipped", flush=True)
            continue
        raw, p = read_info(src / f"{name}_info.tsv")
        ref = pd.read_csv(src / f"{name}.tsv", sep="\t")
        est = int(round(ref.DEPTH.mean()))
        p["n_noise_clones"] = n_noise_clones(raw)
        want_info = (src / f"{name}_info.tsv").read_bytes()
        want_edges = (src / f"{name}_treeedges.tsv").read_bytes()
        want_clones = pd.read_csv(src / f"{name}_cloneprops.tsv", sep="\t")
        mutloss, mutloss_info = None, None
        for m in dict.fromkeys([p["prop_mutloss_positions"], *np.arange(0.1, 0.26, 0.01)]):
            info_df, _, clone_df, edges_df = run(tx_simulation, name, dict(p, prop_mutloss_positions=m), est)[:4]
            clones = clone_df.reset_index(drop=True)
            if not (csv_bytes(edges_df) == want_edges and clones[["Sample", "Clone", "Is_Normal"]].equals(
                    want_clones[["Sample", "Clone", "Is_Normal"]])
                    and np.allclose(clones.Proportion, want_clones.Proportion, rtol=1e-12, atol=0)):
                continue
            if mutloss is None:
                mutloss = m
            if csv_bytes(info_df) == want_info:
                mutloss = mutloss_info = m
                break
        p["prop_mutloss_positions"] = mutloss if mutloss is not None else p["prop_mutloss_positions"]
        cov, tried = None, 0
        for c in sorted(range(est - a.cov_window, est + a.cov_window + 1), key=lambda c: abs(c - est)):
            tried += 1
            variant_df = run(tx_simulation, name, p, c)[1]
            if (np.array_equal(variant_df.DEPTH.values, ref.DEPTH.values)
                    and np.array_equal(variant_df.VAR_COUNT.values, ref.VAR_COUNT.values)):
                cov = c
                break
        run(tx_simulation, name, p, cov if cov is not None else est, out)
        row = {"name": name, "seed": p["rs"], "mutloss_found": mutloss, "mutloss_info_match": mutloss_info is not None,
               "prop_mut_lost_recorded": raw["prop_mut_lost"],
               "coverage_found": cov, "coverage_est": est, "coverage_tried": tried}
        for suf in SUFFIXES:
            row[suf] = (out / name / "sim" / f"{name}{suf}").read_bytes() == (src / f"{name}{suf}").read_bytes()
        rows.append(row)
        print(" ".join(f"{k}={v}" for k, v in row.items()), flush=True)
    df = pd.DataFrame(rows)
    path = out / "compare.tsv"
    if path.exists():
        df = pd.concat([pd.read_csv(path, sep="\t"), df])
    df.to_csv(path, sep="\t", index=False)


if __name__ == "__main__":
    main()
