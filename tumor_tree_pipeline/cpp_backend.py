"""Adapter from the Python workflow contract to the C++ inference backend.

The Python layer remains responsible for canonical-table construction,
holdout selection, provenance, and diagnostics.  The C++ executable owns the
stateful plain-MH chain.  Keeping this adapter small makes the algorithm seam
replaceable without duplicating the workflow.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .contracts import ChainConfig
from .sampler import ChainResult


_ARTIFACTS = (
    "samples.jsonl.gz",
    "diagnostics.json",
    "representative_tree.json",
    "checkpoint.json.gz",
    "chain_complete.json",
)


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_inference_binary() -> Path:
    """Find the explicitly configured or standard local C++ executable."""

    configured = os.environ.get("TUMOR_TREE_INFERENCE_BIN")
    candidates = [Path(configured)] if configured else []
    root = _repository_root()
    candidates.extend(
        (
            root / "inference" / "build" / "tumor_tree_inference",
            root / "inference" / "build-release" / "tumor_tree_inference",
        )
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    searched = ", ".join(str(path) for path in candidates)
    raise RuntimeError(
        "C++ inference backend is not built; expected an executable at "
        f"{searched}. Build it with: cmake -S inference -B inference/build "
        "-DCMAKE_BUILD_TYPE=Release && cmake --build inference/build --parallel"
    )


def _write_exclude_file(ids: frozenset[str], directory: Path) -> Path | None:
    if not ids:
        return None
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", prefix=".holdout.", suffix=".ids", dir=directory, delete=False
    )
    try:
        with handle:
            handle.write("\n".join(sorted(ids)) + "\n")
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise
    return Path(handle.name)


def run_chain_cpp(
    *,
    integrated_input: Path,
    outdir: Path,
    config: ChainConfig,
    algorithm: str = "plain_metropolis_hastings",
    exclude_ids: frozenset[str] = frozenset(),
    resume: bool = False,
) -> ChainResult:
    """Execute one C++ chain and return the existing Python result contract."""

    config.validate()
    input_path = Path(integrated_input).resolve()
    output_path = Path(outdir).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"canonical integrated input does not exist: {input_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    binary = find_inference_binary()
    try:
        site_threads = int(os.environ.get("TUMOR_TREE_INFERENCE_THREADS", "1"))
    except ValueError as exc:
        raise ValueError("TUMOR_TREE_INFERENCE_THREADS must be a positive integer") from exc
    if site_threads < 1:
        raise ValueError("TUMOR_TREE_INFERENCE_THREADS must be positive")
    # Keep the transient file outside the chain directory: the C++ backend
    # treats any non-empty output directory as an overwrite hazard.
    exclude_path = _write_exclude_file(frozenset(exclude_ids), output_path.parent)
    command = [
        str(binary),
        "--algorithm",
        algorithm,
        "--input",
        str(input_path),
        "--outdir",
        str(output_path),
        "--seed",
        str(config.seed),
        "--num-nodes",
        str(config.num_nodes),
        "--iterations",
        str(config.iterations),
        "--burnin",
        str(config.burnin),
        "--thin",
        str(config.thin),
        "--purity",
        f"{config.ascat_purity:.17g}",
        "--checkpoint-every",
        str(config.checkpoint_every),
        "--threads",
        str(site_threads),
        "--chains",
        "1",
    ]
    if exclude_path is not None:
        command.extend(("--exclude-file", str(exclude_path)))
    if resume:
        command.append("--resume")
    try:
        completed = subprocess.run(
            command,
            cwd=_repository_root(),
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        if exclude_path is not None:
            exclude_path.unlink(missing_ok=True)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(
            f"C++ inference backend failed with exit {completed.returncode}: {detail}"
        )
    missing = [name for name in _ARTIFACTS if not (output_path / name).is_file()]
    if missing:
        raise RuntimeError(
            "C++ inference backend exited successfully but did not produce "
            f"required artifacts: {', '.join(missing)}"
        )
    return ChainResult(
        outdir=output_path,
        samples=output_path / "samples.jsonl.gz",
        diagnostics=output_path / "diagnostics.json",
        representative_tree=output_path / "representative_tree.json",
        checkpoint=output_path / "checkpoint.json.gz",
        posterior_samples=_posterior_sample_count(output_path / "diagnostics.json"),
        resumed=resume,
    )


def _posterior_sample_count(path: Path) -> int:
    import json

    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    value = payload.get("posterior_samples") if isinstance(payload, dict) else None
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"C++ diagnostics has invalid posterior_samples: {path}")
    return value
