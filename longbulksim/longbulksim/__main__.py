"""Usage: python3 -m longbulksim SPEC.yaml OUT_DIR [--seed 1] [--depth D] [--phased F]"""
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
    a = ap.parse_args()
    spec = load_spec(a.spec)
    if a.depth is not None:
        spec = dataclasses.replace(spec, depth=a.depth)
    if a.phased is not None:
        spec = dataclasses.replace(spec, phased_fraction=a.phased)
    print(json.dumps(run(spec, a.seed, a.out_dir), indent=1))


if __name__ == "__main__":
    main()
