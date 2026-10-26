"""Usage: python3 -m longbulksim SPEC.yaml OUT_DIR [--seed 1] [--depth D] [--phased F]
       [--mistag R] [--switch-rate R_PER_MB] [--base-error R]"""
import argparse
import dataclasses
import json

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
    print(json.dumps(run(spec, a.seed, a.out_dir), indent=1))


if __name__ == "__main__":
    main()
