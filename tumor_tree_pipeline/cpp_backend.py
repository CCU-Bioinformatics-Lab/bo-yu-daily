"""Small adapter from the Python workflow to the C++ annealed-SMC backend.

The workflow owns canonical-input validation, holdout selection and repeat
diagnostics.  The C++ executable owns the particle population, adaptive
annealing, systematic resampling, rejuvenation and posterior artifacts.  A
single adapter keeps this seam replaceable without maintaining a second
production sampler in Python.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .contracts import INFERENCE_ALGORITHM_ID, SMCConfig


SMC_ARTIFACTS = (
    "samples.jsonl.gz",
    "multiplicity_posterior.tsv.gz",
    "posterior_summary.tsv.gz",
    "topology_summary.tsv",
    "diagnostics.json",
    "representative_tree.json",
    "checkpoint.json.gz",
    "particle_history.jsonl.gz",
    "smc_complete.json",
)


@dataclass(frozen=True)
class SMCResult:
    outdir: Path
    samples: Path
    multiplicity_posterior: Path
    posterior_summary: Path
    topology_summary: Path
    diagnostics: Path
    representative_tree: Path
    checkpoint: Path
    particle_history: Path
    posterior_samples: int
    resumed: bool


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_inference_binary() -> Path:
    """Find the configured or standard local C++ SMC executable."""

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
        "C++ SMC backend is not built; expected an executable at "
        f"{searched}. Build it with: cmake -S inference -B inference/build "
        "-DCMAKE_BUILD_TYPE=Release && cmake --build inference/build --parallel"
    )


def _write_exclude_file(ids: frozenset[str], directory: Path) -> Path | None:
    if not ids:
        return None
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=".holdout.",
        suffix=".ids",
        dir=directory,
        delete=False,
    )
    try:
        with handle:
            handle.write("\n".join(sorted(ids)) + "\n")
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise
    return Path(handle.name)


def _result(output_path: Path, *, resumed: bool) -> SMCResult:
    missing = [name for name in SMC_ARTIFACTS if not (output_path / name).is_file()]
    if missing:
        raise RuntimeError(
            "C++ SMC output is incomplete; missing artifacts: " + ", ".join(missing)
        )
    payload = json.loads((output_path / "diagnostics.json").read_text(encoding="utf-8"))
    posterior_samples = payload.get("posterior_samples")
    if not isinstance(posterior_samples, int) or posterior_samples <= 0:
        raise RuntimeError("C++ SMC diagnostics has invalid posterior_samples")
    return SMCResult(
        outdir=output_path,
        samples=output_path / "samples.jsonl.gz",
        multiplicity_posterior=output_path / "multiplicity_posterior.tsv.gz",
        posterior_summary=output_path / "posterior_summary.tsv.gz",
        topology_summary=output_path / "topology_summary.tsv",
        diagnostics=output_path / "diagnostics.json",
        representative_tree=output_path / "representative_tree.json",
        checkpoint=output_path / "checkpoint.json.gz",
        particle_history=output_path / "particle_history.jsonl.gz",
        posterior_samples=posterior_samples,
        resumed=resumed,
    )


def run_smc_cpp(
    *,
    integrated_input: Path,
    outdir: Path,
    config: SMCConfig,
    algorithm: str = INFERENCE_ALGORITHM_ID,
    exclude_ids: frozenset[str] = frozenset(),
    repeat_index: int = 1,
    resume: bool = False,
) -> SMCResult:
    """Run one independent C++ SMC repeat."""

    config.validate()
    if algorithm != INFERENCE_ALGORITHM_ID:
        raise ValueError(f"only {INFERENCE_ALGORITHM_ID} is available")
    input_path = Path(integrated_input).resolve()
    output_path = Path(outdir).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"canonical integrated input does not exist: {input_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    if resume and (output_path / "smc_complete.json").is_file():
        return _result(output_path, resumed=True)
    if resume:
        raise RuntimeError(
            "C++ SMC checkpoint restore is not implemented; resume requires a completed immutable repeat"
        )
    binary = find_inference_binary()
    try:
        site_threads = int(os.environ.get("TUMOR_TREE_INFERENCE_THREADS", "1"))
    except ValueError as exc:
        raise ValueError("TUMOR_TREE_INFERENCE_THREADS must be a positive integer") from exc
    if site_threads < 1:
        raise ValueError("TUMOR_TREE_INFERENCE_THREADS must be positive")

    annealing_stages = config.max_annealing_stages
    exclude_path = _write_exclude_file(frozenset(exclude_ids), output_path.parent)
    command = [
        str(binary),
        "--algorithm",
        INFERENCE_ALGORITHM_ID,
        "--input",
        str(input_path),
        "--outdir",
        str(output_path),
        "--seed",
        str(config.seed + max(0, repeat_index - 1)),
        "--num-nodes",
        str(config.num_nodes),
        "--annealing-stages",
        str(annealing_stages),
        "--particles",
        str(config.particles),
        "--conditional-ess-target",
        f"{config.conditional_ess_target:.17g}",
        "--ess-threshold",
        f"{config.resample_ess_threshold:.17g}",
        "--rejuvenation-sweeps",
        str(config.min_rejuvenation_sweeps),
        "--purity",
        f"{config.ascat_purity:.17g}",
        "--checkpoint-every",
        str(config.checkpoint_every),
        "--threads",
        str(site_threads),
        "--repeats",
        "1",
    ]
    if exclude_path is not None:
        command.extend(("--exclude-file", str(exclude_path)))
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
        raise RuntimeError(f"C++ SMC backend failed with exit {completed.returncode}: {detail}")
    return _result(output_path, resumed=False)


run_smc = run_smc_cpp
