#!/usr/bin/env python3
"""Delegate project component specs to the global SVG component skill."""
from __future__ import annotations

import argparse
import json
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

    # The composer emits a root rect for every canvas.  For transparent
    # components that rect is a no-op in SVG viewers, but ImageMagick can
    # rasterize it as an opaque white nested-image background.  Keep the
    # component-builder output and normalize only this transparent no-op.
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    background = spec.get("canvas", {}).get("background")
    if background in {"none", "transparent"}:
        output = args.output
        svg = output.read_text(encoding="utf-8")
        transparent_rect = f'<rect width="100%" height="100%" fill="{background}"/>'
        output.write_text(svg.replace(transparent_rect, "", 1), encoding="utf-8")


if __name__ == "__main__":
    main()
