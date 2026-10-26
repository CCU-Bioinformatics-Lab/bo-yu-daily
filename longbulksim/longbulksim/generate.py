"""Generate simulations from summary parameters (CONIPHER-style); no tree spec needed.

Each simulation i goes to OUT_DIR/sim_<i>/ with the usual input/, truth/ and manifest.json
(simulate.run). The drawn spec is saved as truth/spec.yaml and the parameters in manifest.json.
Parameter values come from, highest first: explicit options, the --preset (presets.py), and the
TRACERx 421 single-region medians (param_tree.py).

Usage: python3 -m longbulksim.generate OUT_DIR [--preset pcawg] [--n-sims 1] [--seed 1] ...
       python3 -m longbulksim.generate --list-presets
       python3 -m longbulksim.generate --help
"""
import argparse
import dataclasses
import json
import sys
from pathlib import Path

import numpy as np
import yaml

from . import presets
from .model import parse_spec
from .param_tree import Params, draw_spec, load_pools
from .simulate import run

# option dest -> Params field, for options that override the preset
FIELD = {"n_clones": "n_clones", "tree_shape": "tree_shape", "p_linear": "p_linear",
         "ccf_alpha": "ccf_alpha", "min_ccf": "min_ccf", "min_gap": "min_gap",
         "n_snv": "n_snv", "prop_truncal": "prop_truncal", "n_segments": "n_segments",
         "wgd_prob": "wgd_prob", "prop_gain": "prop_gain", "prop_loss": "prop_loss",
         "prop_loh": "prop_loh", "prop_subclonal_cn": "prop_subclonal_cn", "purity": "purity",
         "depth": "depth", "snv_density": "density_per_mb", "phased": "phased_fraction"}


def resolve(a):
    """Params from the preset, then the explicit options."""
    values = presets.load(a.preset)
    values.update({f: getattr(a, k) for k, f in FIELD.items() if getattr(a, k) is not None})
    if a.wgd != "auto":
        values["wgd"] = a.wgd == "yes"
    return Params(**values)


def main():
    d = Params()
    ap = argparse.ArgumentParser(
        prog="longbulksim.generate",
        description="Values not given come from --preset (default tracerx = TRACERx 421 medians).")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--preset", default="tracerx", help="tracerx, pcawg or pcawg:<histology>")
    ap.add_argument("--list-presets", action="store_true")
    ap.add_argument("--n-sims", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    g = ap.add_argument_group("tree (always TRACERx unless given)")
    g.add_argument("--n-clones", type=int, help=f"clones incl. the trunk (default {d.n_clones})")
    g.add_argument("--tree-shape", choices=("random", "linear", "branched"))
    g.add_argument("--p-linear", type=float, help=f"for --tree-shape random (default {d.p_linear})")
    g.add_argument("--ccf-alpha", type=float, help=f"default {d.ccf_alpha}")
    g.add_argument("--min-ccf", type=float, help=f"default {d.min_ccf}")
    g.add_argument("--min-gap", type=float, help=f"min parent - child CCF (default {d.min_gap})")
    g = ap.add_argument_group("mutations and CN (preset)")
    g.add_argument("--n-snv", type=int)
    g.add_argument("--prop-truncal", type=float)
    g.add_argument("--n-segments", type=int)
    g.add_argument("--wgd", choices=("auto", "yes", "no"), default="auto",
                   help="auto: draw WGD per simulation with --wgd-prob")
    g.add_argument("--wgd-prob", type=float)
    g.add_argument("--prop-gain", type=float, help="bp share for both WGD groups")
    g.add_argument("--prop-loss", type=float)
    g.add_argument("--prop-loh", type=float)
    g.add_argument("--prop-subclonal-cn", type=float)
    g = ap.add_argument_group("sample and reads (preset for purity, depth, density)")
    g.add_argument("--purity", type=float)
    g.add_argument("--depth", type=float)
    g.add_argument("--snv-density", type=float, help="SNVs per Mb")
    g.add_argument("--phased", type=float, help=f"without --het-map (default {d.phased_fraction})")
    g.add_argument("--het-map", help="phased het SNP map (.npz)")
    g.add_argument("--depth-map", help="read start density map (.npz) from a real normal")
    g.add_argument("--mistag", type=float, default=0.0)
    g.add_argument("--switch-rate", type=float, default=0.0, help="per Mb")
    g.add_argument("--base-error", type=float, default=0.0)
    g.add_argument("--caller", choices=("none", "clairs", "deepsomatic"), default="none",
                   help="drop SNVs this ONT somatic caller would miss")
    a = ap.parse_args()
    if a.list_presets:
        print("\n".join(presets.names()))
        return
    if not a.out_dir:
        ap.error("OUT_DIR is required")

    try:
        p = resolve(a)
        p.cn_shares(True), p.cn_shares(False)  # fail early on shares > 1
    except ValueError as e:
        sys.exit(f"longbulksim.generate: {e}")
    pools = load_pools()
    out = Path(a.out_dir)
    for i in range(a.n_sims):
        rng = np.random.default_rng([a.seed, i])
        name = f"sim_{i:04d}"
        raw = draw_spec(rng, pools, p, name)
        raw["source"]["preset"] = a.preset
        raw.update(mistag_rate=a.mistag, switch_rate_per_mb=a.switch_rate, base_error=a.base_error,
                   caller=a.caller)
        if a.het_map:
            raw["het_map"] = str(Path(a.het_map).resolve())
        if a.depth_map:
            raw["depth_map"] = str(Path(a.depth_map).resolve())
        sim_seed = int(rng.integers(2**31))
        manifest = run(parse_spec(raw), sim_seed, out / name)
        (out / name / "truth/spec.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
        manifest["preset"] = a.preset
        manifest["params"] = dataclasses.asdict(p)
        manifest["wgd"] = raw["source"]["wgd"]
        manifest["generate_seed"] = [a.seed, i]
        (out / name / "manifest.json").write_text(json.dumps(manifest, indent=1))
        print(f"{name}: {len(raw['clones'])} clones, WGD {'yes' if manifest['wgd'] else 'no'}, "
              f"{manifest['n_mutations']} SNVs, {manifest['n_detected']} called")


if __name__ == "__main__":
    main()
