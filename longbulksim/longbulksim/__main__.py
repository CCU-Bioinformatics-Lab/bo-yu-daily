"""Usage: python3 -m longbulksim SPEC.yaml OUT_DIR [--seed 1] [--depth D] [--phased F]
       [--mistag R] [--switch-rate R_PER_MB] [--base-error R] [--het-map NPZ]
       [--caller none|clairs|deepsomatic]"""
import argparse
import dataclasses
import json
from pathlib import Path

from .model import load_spec
from .simulate import run


def main():
    ap = argparse.ArgumentParser(prog="longbulksim")
    ap.add_argument("spec")
    ap.add_argument("out_dir")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--depth", type=float, help="override the spec's depth")
    ap.add_argument("--phased", type=float, help="override the spec's phased_fraction")
    ap.add_argument("--mistag", type=float, help="override the spec's mistag_rate")
    ap.add_argument("--switch-rate", type=float, help="override the spec's switch_rate_per_mb")
    ap.add_argument("--base-error", type=float, help="override the spec's base_error")
    ap.add_argument("--het-map", help="phased het SNP map (.npz); tags reads by the longphase-s rule")
    ap.add_argument("--caller", help="drop SNVs this caller would miss: none, clairs, deepsomatic")
    a = ap.parse_args()
    spec = load_spec(a.spec)
    if a.depth is not None:
        spec = dataclasses.replace(spec, depth=a.depth)
    if a.phased is not None:
        spec = dataclasses.replace(spec, phased_fraction=a.phased)
    for arg, field in (("mistag", "mistag_rate"), ("switch_rate", "switch_rate_per_mb"),
                       ("base_error", "base_error")):
        if getattr(a, arg) is not None:
            spec = dataclasses.replace(spec, **{field: getattr(a, arg)})
    if a.caller is not None:
        spec = dataclasses.replace(spec, caller=a.caller)
    if a.het_map is not None:
        spec = dataclasses.replace(spec, het_map=Path(a.het_map))
    print(json.dumps(run(spec, a.seed, a.out_dir), indent=1))


if __name__ == "__main__":
    main()
