"""Generate simulations from summary parameters (CONIPHER-style); no tree spec needed.

Each simulation i goes to OUT_DIR/sim_<i>/ with the usual input/, truth/ and manifest.json
(simulate.run). The drawn spec is saved as truth/spec.yaml and the parameters in manifest.json.
Defaults are TRACERx 421 single-region medians (param_tree.py).

Usage: python3 -m longbulksim.generate OUT_DIR [--n-sims 1] [--seed 1] [--n-clones 3] ...
       python3 -m longbulksim.generate --help
"""
import argparse
import dataclasses
import json
from pathlib import Path

import numpy as np
import yaml

from .model import parse_spec
from .param_tree import Params, draw_spec, load_pools
from .simulate import run


def main():
    d = Params()
    ap = argparse.ArgumentParser(prog="longbulksim.generate",
                                 description="defaults: TRACERx 421 single-region medians")
    ap.add_argument("out_dir")
    ap.add_argument("--n-sims", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    g = ap.add_argument_group("tree")
    g.add_argument("--n-clones", type=int, default=d.n_clones, help="clones incl. the trunk")
    g.add_argument("--tree-shape", choices=("random", "linear", "branched"), default=d.tree_shape)
    g.add_argument("--p-linear", type=float, default=d.p_linear, help="for --tree-shape random")
    g.add_argument("--ccf-alpha", type=float, default=d.ccf_alpha)
    g.add_argument("--min-ccf", type=float, default=d.min_ccf)
    g.add_argument("--min-gap", type=float, default=d.min_gap, help="min parent - child CCF")
    g = ap.add_argument_group("mutations and CN")
    g.add_argument("--n-snv", type=int, default=d.n_snv)
    g.add_argument("--prop-truncal", type=float, default=d.prop_truncal)
    g.add_argument("--n-segments", type=int, default=d.n_segments)
    g.add_argument("--wgd", choices=("yes", "no"), default="yes" if d.wgd else "no")
    g.add_argument("--prop-gain", type=float, help="bp share; default TRACERx median of the WGD group")
    g.add_argument("--prop-loss", type=float)
    g.add_argument("--prop-loh", type=float)
    g.add_argument("--prop-subclonal-cn", type=float, default=d.prop_subclonal_cn)
    g = ap.add_argument_group("sample and reads")
    g.add_argument("--purity", type=float, default=d.purity)
    g.add_argument("--depth", type=float, default=d.depth)
    g.add_argument("--snv-density", type=float, default=d.density_per_mb, help="SNVs per Mb")
    g.add_argument("--phased", type=float, default=d.phased_fraction, help="without --het-map")
    g.add_argument("--het-map", help="phased het SNP map (.npz)")
    g.add_argument("--mistag", type=float, default=0.0)
    g.add_argument("--switch-rate", type=float, default=0.0, help="per Mb")
    g.add_argument("--base-error", type=float, default=0.0)
    a = ap.parse_args()

    p = Params(n_clones=a.n_clones, tree_shape=a.tree_shape, p_linear=a.p_linear,
               ccf_alpha=a.ccf_alpha, min_ccf=a.min_ccf, min_gap=a.min_gap, n_snv=a.n_snv,
               prop_truncal=a.prop_truncal, n_segments=a.n_segments, wgd=a.wgd == "yes",
               prop_gain=a.prop_gain, prop_loss=a.prop_loss, prop_loh=a.prop_loh,
               prop_subclonal_cn=a.prop_subclonal_cn, purity=a.purity, depth=a.depth,
               density_per_mb=a.snv_density, phased_fraction=a.phased)
    p.cn_shares()  # fail early on shares > 1
    pools = load_pools()
    out = Path(a.out_dir)
    for i in range(a.n_sims):
        rng = np.random.default_rng([a.seed, i])
        name = f"sim_{i:04d}"
        raw = draw_spec(rng, pools, p, name)
        raw.update(mistag_rate=a.mistag, switch_rate_per_mb=a.switch_rate, base_error=a.base_error)
        if a.het_map:
            raw["het_map"] = str(Path(a.het_map).resolve())
        sim_seed = int(rng.integers(2**31))
        manifest = run(parse_spec(raw), sim_seed, out / name)
        (out / name / "truth/spec.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
        manifest["params"] = dataclasses.asdict(p)
        manifest["generate_seed"] = [a.seed, i]
        (out / name / "manifest.json").write_text(json.dumps(manifest, indent=1))
        print(f"{name}: {len(raw['clones'])} clones, {manifest['n_mutations']} SNVs")


if __name__ == "__main__":
    main()
