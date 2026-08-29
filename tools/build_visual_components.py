#!/usr/bin/env python3
"""Delegate project component specs to the global SVG component skill."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSER = Path.home() / ".codex" / "skills" / "svg-component-builder" / "scripts" / "compose_svg_component.py"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="Project-owned semantic component JSON spec")
    parser.add_argument("--assets-dir", type=Path, default=ROOT / "assets")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if not COMPOSER.is_file():
        raise SystemExit(f"global skill renderer is not installed: {COMPOSER}")

    command = [
        sys.executable,
        str(COMPOSER),
        "--spec",
        str(args.spec),
        "--assets-dir",
        str(args.assets_dir),
        "--output",
        str(args.output),
    ]
    if args.report:
        command.extend(("--report", str(args.report)))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
