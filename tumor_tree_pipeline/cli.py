"""Command-line interface for the immutable tumor-tree workflow."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Sequence

from .workflow import WorkflowError, experiment_matrix, load_config, run_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tumor_tree_pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run an immutable staged experiment")
    run_parser.add_argument("--config", required=True, type=Path)
    run_parser.add_argument(
        "--resume",
        action="store_true",
        help="resume the unfinished run_id named by the config",
    )
    plan_parser = subparsers.add_parser("plan", help="validate a config and print its staged matrix")
    plan_parser.add_argument("--config", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "run" and args.resume:
            config = dataclasses.replace(config, resume=True)
        config.validate()
        if args.command == "plan":
            print(
                json.dumps(
                    [
                        {
                            "stage": cell.stage,
                            "K": cell.num_nodes,
                            "rho_ASCAT": cell.purity,
                            "formal": cell.formal,
                        }
                        for cell in experiment_matrix(config)
                    ],
                    indent=2,
                )
            )
            return 0
        output = run_experiment(config)
        print(output)
        return 0
    except (OSError, ValueError, WorkflowError) as exc:
        print(f"tumor-tree workflow failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
