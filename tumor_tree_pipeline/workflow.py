"""Immutable, gated orchestration for HCC1395 tumor-tree experiments."""

from __future__ import annotations

import csv
import dataclasses
import fcntl
import gzip
import hashlib
import inspect
import io
import json
import os
import subprocess
import sys
import traceback
import uuid
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    MODEL_FORBIDDEN_COLUMNS,
    MODEL_INPUT_SCHEMA_VERSION,
    MODEL_REQUIRED_COLUMNS,
    BuildInputs,
    ChainConfig,
    GateThresholds,
    PuritySpec,
)
from .diagnostics import (
    evaluate_formal_gates,
    pilot_report,
    sampler_artifact_payload,
    summarize_chains,
)


class WorkflowError(RuntimeError):
    """Base class for fail-closed workflow failures."""


class GateFailure(WorkflowError):
    """Raised when an executed formal experiment does not pass every gate."""


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for one staged experiment matrix.

    ``mode=all`` performs smoke, K=4/6/8 pilots, then the dependency-ordered
    formal matrix.  Formal execution always starts at K=6/rho=0.99 and stops
    immediately if a required gate fails.
    """

    output_root: Path
    table_path: Path | None = None
    validation_manifest: Path | None = None
    build_inputs: BuildInputs | None = None
    holdout_metadata: Path | None = None
    ps_audit_manifest: Path | None = None
    simulation_manifest: Path | None = None
    mode: str = "formal"
    seed: int = 20_260_819
    main_purity: float = 0.99
    pilot_nodes: tuple[int, ...] = (4, 6, 8)
    sensitivity_purities: tuple[float, ...] = (0.97, 0.95)
    formal_chains: int = 4
    formal_iterations: int = 1_500
    formal_burnin: int = 1_000
    formal_thin: int = 1
    checkpoint_every: int = 100
    ess_extension_batch: int = 500
    formal_max_iterations: int = 5_000
    pilot_chains: int = 4
    pilot_iterations: int = 300
    pilot_burnin: int = 100
    smoke_chains: int = 2
    smoke_iterations: int = 20
    smoke_burnin: int = 5
    holdout_fraction: float = 0.20
    gate_thresholds: GateThresholds = field(default_factory=GateThresholds)
    min_predictive_log_score: float | None = None
    run_id: str | None = None
    git_root: Path | None = None
    resume: bool = False
    allow_dirty_worktree: bool = False

    def validate(self) -> None:
        if self.mode not in {"smoke", "pilot", "formal", "all"}:
            raise ValueError("mode must be smoke, pilot, formal, or all")
        if self.table_path is None and self.build_inputs is None:
            raise ValueError("either table_path or build_inputs is required")
        if self.table_path is not None and self.build_inputs is not None:
            raise ValueError("table_path and build_inputs are mutually exclusive")
        if self.table_path is not None and self.validation_manifest is None:
            raise ValueError("a prebuilt table requires validation_manifest")
        if not 0.0 < self.main_purity <= 1.0:
            raise ValueError("main_purity must be in (0, 1]")
        if abs(self.main_purity - 0.99) > 1e-12:
            raise ValueError("the agreed primary analysis requires ASCAT purity 0.99")
        if tuple(self.pilot_nodes) != (4, 6, 8):
            raise ValueError("the agreed finite-K sensitivity matrix is K=4,6,8")
        if tuple(self.sensitivity_purities) != (0.97, 0.95):
            raise ValueError("the agreed purity sensitivity values are 0.97 and 0.95")
        if self.formal_chains < 4:
            raise ValueError("formal inference requires at least four overdispersed chains")
        if self.formal_iterations < 1_500 or self.formal_burnin < 1_000:
            raise ValueError("formal lower bounds are 1500 iterations and 1000 burn-in")
        if self.formal_iterations <= self.formal_burnin or self.formal_thin != 1:
            raise ValueError("formal chains require iterations > burn-in and thin=1")
        if self.ess_extension_batch <= 0:
            raise ValueError("ess_extension_batch must be positive")
        if self.formal_max_iterations < self.formal_iterations:
            raise ValueError("formal_max_iterations must be >= formal_iterations")
        if self.resume and not self.run_id:
            raise ValueError("resume requires an explicit run_id")
        if not 0.0 < self.holdout_fraction < 1.0:
            raise ValueError("holdout_fraction must be in (0, 1)")
        if self.mode in {"formal", "all"}:
            if self.allow_dirty_worktree:
                raise ValueError("formal/all mode cannot override the clean Git worktree requirement")
            for label, path in (
                ("holdout_metadata", self.holdout_metadata),
                ("ps_audit_manifest", self.ps_audit_manifest),
                ("simulation_manifest", self.simulation_manifest),
            ):
                if path is None:
                    raise ValueError(f"formal mode requires {label}")
            if self.min_predictive_log_score is None:
                raise ValueError(
                    "formal mode requires an explicit min_predictive_log_score; "
                    "the workflow will not invent a study-specific threshold"
                )
        self.gate_thresholds.validate()


@dataclass(frozen=True)
class RunCell:
    stage: str
    num_nodes: int
    purity: float
    formal: bool


def experiment_matrix(config: ExperimentConfig) -> tuple[RunCell, ...]:
    """Return the dependency-ordered staged matrix."""

    cells: list[RunCell] = []
    if config.mode in {"smoke", "all"}:
        cells.append(RunCell("smoke", 6, config.main_purity, False))
    if config.mode in {"pilot", "all"}:
        cells.extend(RunCell("pilot", k, config.main_purity, False) for k in config.pilot_nodes)
    if config.mode in {"formal", "all"}:
        # K=6 is the prerequisite.  K sensitivity and then purity robustness
        # are reached only after every preceding formal cell passes.
        cells.append(RunCell("formal_main", 6, config.main_purity, True))
        cells.extend(RunCell("formal_k_sensitivity", k, config.main_purity, True) for k in (4, 8))
        cells.extend(
            RunCell("formal_purity_sensitivity", 6, purity, True)
            for purity in config.sensitivity_purities
        )
    return tuple(cells)


def _path(value: Any, base: Path) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def _load_mapping(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - environment guard
            raise WorkflowError("YAML config requires the already-installed PyYAML package") from exc
        value = yaml.safe_load(text)
    if not isinstance(value, Mapping):
        raise WorkflowError(f"configuration must contain an object: {path}")
    return value


def load_config(path: Path | str) -> ExperimentConfig:
    config_path = Path(path).resolve()
    raw = dict(_load_mapping(config_path))
    base = config_path.parent
    thresholds_raw = raw.pop("gate_thresholds", {})
    thresholds = GateThresholds(**thresholds_raw)
    build_raw = raw.pop("build_inputs", None)
    build_inputs = None
    if build_raw is not None:
        purity_raw = build_raw["purity"]
        build_inputs = BuildInputs(
            counts_dir=_path(build_raw["counts_dir"], base),
            site_cnv_qc=_path(build_raw["site_cnv_qc"], base),
            purity=PuritySpec(
                value=float(purity_raw["value"]),
                source=_path(purity_raw["source"], base),
                sample=purity_raw.get("sample", "HCC1395"),
            ),
            expected_sites=int(build_raw.get("expected_sites", 30_490)),
        )
    for name in (
        "output_root",
        "table_path",
        "validation_manifest",
        "holdout_metadata",
        "ps_audit_manifest",
        "simulation_manifest",
        "git_root",
    ):
        if name in raw:
            raw[name] = _path(raw[name], base)
    for name in ("pilot_nodes", "sensitivity_purities"):
        if name in raw:
            raw[name] = tuple(raw[name])
    return ExperimentConfig(**raw, build_inputs=build_inputs, gate_thresholds=thresholds)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _set_directory_mode(path: Path) -> None:
    path.chmod(0o2775)


def _mkdir(path: Path, *, exist_ok: bool = True) -> None:
    missing: list[Path] = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    path.mkdir(parents=True, exist_ok=exist_ok)
    for directory in reversed(missing):
        _set_directory_mode(directory)
    if not missing:
        _set_directory_mode(path)


def _atomic_write(path: Path, text: str) -> None:
    _mkdir(path.parent)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o664)
        os.replace(temporary, path)
        path.chmod(0o664)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_write(path, json.dumps(_jsonable(value), indent=2, sort_keys=True, allow_nan=False) + "\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_sha(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise WorkflowError(f"cannot resolve a Git SHA from execution source {root}") from exc
    sha = result.stdout.strip()
    if not sha:
        raise WorkflowError(f"empty Git SHA from execution source {root}")
    return sha


def _git_worktree_state(root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise WorkflowError(f"cannot inspect Git worktree state at {root}") from exc
    lines = [line for line in result.stdout.splitlines() if line]
    return {"clean": not lines, "porcelain": lines}


def _rho_label(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".").replace(".", "p")


def _make_run_id(
    timestamp: datetime,
    git_sha: str,
    purities: Sequence[float],
    nodes: Sequence[int],
    seed: int,
) -> str:
    rho = "-".join(_rho_label(value) for value in dict.fromkeys(purities))
    finite_k = "-".join(str(value) for value in dict.fromkeys(nodes))
    return (
        f"{timestamp.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        f"_{git_sha}_rho{rho}_K{finite_k}_seed{seed}"
    )


def _read_json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise WorkflowError(f"manifest must contain an object: {path}")
    return value


def _nested(mapping: Mapping[str, Any], *paths: Sequence[str]) -> Any:
    for path in paths:
        current: Any = mapping
        for key in path:
            if not isinstance(current, Mapping) or key not in current:
                break
            current = current[key]
        else:
            return current
    return None


def _table_header_and_purities(path: Path) -> tuple[list[str], set[float], int]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        columns = list(reader.fieldnames or [])
        purities: set[float] = set()
        rows = 0
        for row in reader:
            rows += 1
            try:
                purities.add(float(row["rho_ASCAT"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise WorkflowError("every model-table row must contain numeric rho_ASCAT") from exc
    return columns, purities, rows


def _eligible_model_ids(path: Path) -> frozenset[str]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        identifiers = [
            row["mutation_id"]
            for row in reader
            if row.get("model_include", "").strip().lower() == "yes"
            and row.get("model_status", "").strip().lower() == "eligible"
        ]
    if not identifiers:
        raise WorkflowError("canonical model table has no eligible mutation IDs")
    if len(identifiers) != len(set(identifiers)):
        raise WorkflowError("canonical model table has duplicate eligible mutation IDs")
    return frozenset(identifiers)


def validate_model_table_manifest(table_path: Path, manifest_path: Path, expected_rho: float) -> dict[str, Any]:
    """Verify schema, actual table hash, purity and QA before any sampler call."""

    if not table_path.is_file() or not manifest_path.is_file():
        raise WorkflowError("model table and validation manifest must both exist")
    manifest = _read_json(manifest_path)
    schema = _nested(
        manifest,
        ("schema_version",),
        ("model_input_schema_version",),
        ("schema", "version"),
    )
    table_hash = _nested(
        manifest,
        ("table_sha256",),
        ("output", "sha256"),
        ("outputs", "likelihood_input", "sha256"),
        ("artifacts", "model_table", "sha256"),
    )
    rho = _nested(manifest, ("rho_ASCAT",), ("purity", "value"))
    qa_pass = _nested(manifest, ("qa_pass",), ("qa", "pass"), ("validation", "passed"))
    if qa_pass is None:
        qa_pass = manifest.get("status") == "pass"
    if schema != MODEL_INPUT_SCHEMA_VERSION:
        raise WorkflowError(f"schema mismatch: expected {MODEL_INPUT_SCHEMA_VERSION}, got {schema!r}")
    actual_hash = _sha256(table_path)
    if table_hash != actual_hash:
        raise WorkflowError("validation manifest table hash does not match the actual table")
    if rho is None or abs(float(rho) - expected_rho) > 1e-12:
        raise WorkflowError("validation manifest rho_ASCAT does not match the experiment")
    if qa_pass is not True:
        raise WorkflowError("input QA did not pass")

    columns, row_purities, row_count = _table_header_and_purities(table_path)
    missing = sorted(set(MODEL_REQUIRED_COLUMNS) - set(columns))
    forbidden = sorted(set(MODEL_FORBIDDEN_COLUMNS) & set(columns))
    if missing or forbidden:
        raise WorkflowError(f"model-table schema violation: missing={missing}, forbidden={forbidden}")
    if row_count == 0 or row_purities != {expected_rho}:
        raise WorkflowError(
            f"model-table rho_ASCAT rows must all equal {expected_rho}; found {sorted(row_purities)}"
        )
    return {
        "passed": True,
        "schema_version": schema,
        "table_sha256": actual_hash,
        "rho_ASCAT": expected_rho,
        "rows": row_count,
        "manifest": str(manifest_path),
    }


def _derive_purity_sensitivity_table(
    source_table: Path,
    *,
    purity: float,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Create an explicit, hashed table variant for a fixed-purity sensitivity.

    Repeating rho in the canonical table is part of its validation contract,
    so a chain may never override a 0.99 table in memory.  Sensitivity runs get
    their own immutable input artifact derived from the same counts/CN/prior.
    """

    _mkdir(output_dir, exist_ok=False)
    opener = gzip.open if source_table.suffix == ".gz" else open
    buffer = io.StringIO()
    with opener(source_table, "rt", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if not reader.fieldnames or "rho_ASCAT" not in reader.fieldnames:
            raise WorkflowError("source model table lacks rho_ASCAT")
        writer = csv.DictWriter(buffer, fieldnames=reader.fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        rows = 0
        for row in reader:
            row["rho_ASCAT"] = f"{purity:.12g}"
            writer.writerow(row)
            rows += 1
    if rows == 0:
        raise WorkflowError("cannot derive a purity sensitivity from an empty model table")
    table = output_dir / "model_input.tsv"
    _atomic_write(table, buffer.getvalue())
    manifest = output_dir / "validation_manifest.json"
    _atomic_json(
        manifest,
        {
            "schema_version": MODEL_INPUT_SCHEMA_VERSION,
            "table_sha256": _sha256(table),
            "rho_ASCAT": purity,
            "qa_pass": True,
            "rows": rows,
            "analysis_role": "fixed-purity sensitivity; not a replacement ASCAT estimate",
            "derived_from": {
                "path": str(source_table),
                "sha256": _sha256(source_table),
            },
        },
    )
    return table, manifest


def _validate_ps_audit(path: Path) -> dict[str, Any]:
    manifest = _read_json(path)
    passed = _nested(manifest, ("passed",), ("qa_pass",), ("status", "passed"))
    discordance = _nested(
        manifest,
        ("discordance_fraction",),
        ("metrics", "discordance_fraction"),
    )
    if passed is not True or discordance is None or float(discordance) > 0.01:
        raise WorkflowError("PS grouped holdout requires a passing read-level PS audit (discordance <= 0.01)")
    value = float(discordance)
    if not 0.0 <= value <= 1.0:
        raise WorkflowError("PS audit discordance_fraction must be in [0, 1]")
    return {
        "passed": True,
        "discordance_fraction": value,
        "manifest": str(path),
        "sha256": _sha256(path),
    }


def _validate_simulation_gate(path: Path) -> dict[str, Any]:
    manifest = _read_json(path)
    passed = _nested(manifest, ("passed",), ("gate", "passed"), ("simulation_pass",))
    if passed is not True:
        raise WorkflowError("formal execution requires a passing synthetic-recovery manifest")
    return {"passed": True, "manifest": str(path), "sha256": _sha256(path)}


def _read_metadata(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"mutation_id", "chrom", "ps"}
    if not rows or not required.issubset(rows[0]):
        raise WorkflowError(f"holdout metadata requires columns {sorted(required)}")
    has_segment = "ascat_segment_id" in rows[0] or {
        "segment_start",
        "segment_end",
    }.issubset(rows[0])
    if not has_segment:
        raise WorkflowError("holdout metadata requires ASCAT segment identity")
    identifiers = [row["mutation_id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise WorkflowError("holdout metadata mutation_id values must be unique")
    return rows


def _reconcile_holdout_metadata(
    rows: Sequence[Mapping[str, str]], table_path: Path
) -> dict[str, Any]:
    metadata_ids = frozenset(row["mutation_id"] for row in rows)
    eligible_ids = _eligible_model_ids(table_path)
    missing = sorted(eligible_ids - metadata_ids)
    extra = sorted(metadata_ids - eligible_ids)
    if missing or extra:
        raise WorkflowError(
            "holdout metadata must exactly match canonical eligible mutation IDs: "
            f"missing={len(missing)} {missing[:5]}, extra={len(extra)} {extra[:5]}"
        )
    return {"passed": True, "eligible_sites": len(eligible_ids)}


def _holdout_block(row: Mapping[str, str], kind: str) -> str:
    if kind == "ps":
        ps = (row.get("ps") or "").strip()
        return f"{row['chrom']}|PS:{ps}" if ps else f"{row['chrom']}|SINGLE:{row['mutation_id']}"
    if kind == "chromosome":
        return row["chrom"]
    if kind == "ascat_segment":
        segment = (row.get("ascat_segment_id") or "").strip()
        if segment:
            return segment
        return f"{row['chrom']}:{row['segment_start']}-{row['segment_end']}"
    raise ValueError(f"unknown holdout kind: {kind}")


def create_grouped_holdout(
    rows: Sequence[Mapping[str, str]],
    *,
    kind: str,
    fraction: float,
    seed: int,
    output_dir: Path,
) -> dict[str, Any]:
    blocks: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        blocks[_holdout_block(row, kind)].append(row["mutation_id"])
    target = max(1, round(len(rows) * fraction))
    ordered = sorted(
        blocks,
        key=lambda block: hashlib.sha256(f"{seed}|{kind}|{block}".encode()).hexdigest(),
    )
    selected: list[str] = []
    selected_blocks: list[str] = []
    for block in ordered:
        if len(selected) >= target:
            break
        selected_blocks.append(block)
        selected.extend(blocks[block])
    holdout = sorted(set(selected))
    holdout_set = set(holdout)
    train = sorted(row["mutation_id"] for row in rows if row["mutation_id"] not in holdout_set)
    if not train or not holdout:
        raise WorkflowError(f"{kind} holdout produced an empty train or holdout partition")
    _mkdir(output_dir, exist_ok=False)
    _atomic_write(output_dir / "holdout_site_ids.txt", "\n".join(holdout) + "\n")
    _atomic_write(output_dir / "train_site_ids.txt", "\n".join(train) + "\n")
    manifest = {
        "strict": True,
        "kind": kind,
        "hash": "sha256(seed|kind|block) ascending",
        "seed": seed,
        "fraction_requested": fraction,
        "total_sites": len(rows),
        "train_sites": len(train),
        "holdout_sites": len(holdout),
        "holdout_blocks": len(selected_blocks),
    }
    _atomic_json(output_dir / "manifest.json", manifest)
    return {**manifest, "holdout_path": output_dir / "holdout_site_ids.txt"}


def _default_table_builder(build_inputs: BuildInputs, output_dir: Path) -> Any:
    from .input_table import build_model_table

    return build_model_table(build_inputs, output_dir)


def _read_identifier_file(path: Path | None) -> frozenset[str]:
    if path is None:
        return frozenset()
    return frozenset(
        line.strip().split("\t", 1)[0]
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )


def _default_chain_runner(
    *,
    table_path: Path,
    config: ChainConfig,
    output_dir: Path,
    holdout_path: Path | None,
    holdout_kind: str,
    chain_index: int,
    initialization: str,
    resume: bool,
) -> Any:
    from .sampler import run_chain

    if initialization != "overdispersed":
        raise WorkflowError("workflow chains must request overdispersed initialization")
    sampler_signature = inspect.signature(run_chain)
    supports_initialization = "initialization" in sampler_signature.parameters
    if holdout_kind != "none" and not supports_initialization:
        raise WorkflowError(
            "formal execution is blocked: sampler.run_chain does not yet expose "
            "an explicit overdispersed initialization contract"
        )
    holdout_ids = _read_identifier_file(holdout_path)
    complete = output_dir / "chain_complete.json"
    if resume and complete.is_file():
        checkpoint = output_dir / "checkpoint.json.gz"
        payload = _checkpoint_payload(checkpoint)
        if int(payload.get("next_iteration", -1)) != config.iterations:
            raise WorkflowError("completed chain checkpoint does not match requested iterations")
        result = type(
            "ExistingChainResult",
            (),
            {
                "samples": output_dir / "samples.jsonl.gz",
                "representative_tree": output_dir / "representative_tree.json",
            },
        )()
    else:
        sampler_arguments = {
            "integrated_input": table_path,
            "outdir": output_dir,
            "config": config,
            "exclude_ids": holdout_ids,
            "resume": resume,
        }
        if supports_initialization:
            sampler_arguments["initialization"] = initialization
        result = run_chain(**sampler_arguments)
    if holdout_kind == "none":
        # Smoke/pilot diagnostics still need a scoring partition.  They do not
        # control a formal pass and use a deterministic small pseudo-holdout.
        with (gzip.open(table_path, "rt") if table_path.suffix == ".gz" else table_path.open("r")) as handle:
            identifiers = [row["mutation_id"] for row in csv.DictReader(handle, delimiter="\t")]
        holdout_ids = frozenset(
            identifier
            for identifier in identifiers
            if int(hashlib.sha256(identifier.encode()).hexdigest(), 16) % 10 == 0
        )
        if not holdout_ids:
            holdout_ids = frozenset(identifiers[:1])
    return sampler_artifact_payload(
        samples_path=result.samples,
        representative_tree_path=result.representative_tree,
        table_path=table_path,
        holdout_ids=holdout_ids,
        purity=config.ascat_purity,
    )


def _checkpoint_payload(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise WorkflowError(f"checkpoint must contain an object: {path}")
    return value


def _promote_checkpoint_iterations(
    chain_dir: Path, old_config: ChainConfig, new_config: ChainConfig
) -> None:
    """Authorize a bounded ESS extension without changing any other chain input."""

    checkpoint = chain_dir / "checkpoint.json.gz"
    if not checkpoint.is_file():
        raise WorkflowError(f"ESS extension checkpoint is missing: {checkpoint}")
    payload = _checkpoint_payload(checkpoint)
    observed = payload.get("config")
    if observed != dataclasses.asdict(old_config):
        raise WorkflowError("checkpoint config does not match the completed extension batch")
    old_values = dataclasses.asdict(old_config)
    new_values = dataclasses.asdict(new_config)
    differences = {key for key in old_values if old_values[key] != new_values[key]}
    if differences != {"iterations"} or new_config.iterations <= old_config.iterations:
        raise WorkflowError("ESS extension may increase only ChainConfig.iterations")
    next_iteration = int(payload.get("next_iteration", -1))
    if next_iteration != old_config.iterations:
        raise WorkflowError("checkpoint is not at the completed iteration boundary")
    payload["config"] = new_values
    encoded = gzip.compress(
        (
            json.dumps(payload, separators=(",", ":"), sort_keys=True, allow_nan=False)
            + "\n"
        ).encode(),
        compresslevel=6,
        mtime=0,
    )
    temporary = checkpoint.parent / f".{checkpoint.name}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o664)
        os.replace(temporary, checkpoint)
    finally:
        if temporary.exists():
            temporary.unlink()
    complete = chain_dir / "chain_complete.json"
    if complete.exists():
        archive = chain_dir / f"chain_complete.iter_{old_config.iterations}.json"
        if archive.exists():
            raise WorkflowError(f"extension receipt already exists: {archive}")
        os.replace(complete, archive)


def _gate_failures(gate: Mapping[str, Any]) -> frozenset[str]:
    checks = gate.get("checks", {})
    if not isinstance(checks, Mapping):
        return frozenset({"invalid_gate_payload"})
    return frozenset(str(key) for key, passed in checks.items() if passed is not True)


def _artifact_inventory(root: Path) -> dict[str, Any]:
    excluded = {"artifact_inventory.json", "run.lock", "_SUCCESS"}
    artifacts = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded or relative.endswith(".tmp"):
            continue
        artifacts.append(
            {"path": relative, "size_bytes": path.stat().st_size, "sha256": _sha256(path)}
        )
    return {
        "inventory_version": 1,
        "scope": "all regular run files except artifact_inventory.json, run.lock, and _SUCCESS",
        "artifacts": artifacts,
    }


def _artifact_paths(result: Any) -> tuple[Path, Path]:
    if dataclasses.is_dataclass(result):
        result = {field.name: getattr(result, field.name) for field in dataclasses.fields(result)}
    if isinstance(result, Mapping):
        table = result.get("table_path") or result.get("model_table") or result.get("table")
        manifest = (
            result.get("manifest_path")
            or result.get("validation_manifest")
            or result.get("manifest")
        )
        if table and manifest:
            return Path(table), Path(manifest)
    if isinstance(result, (str, Path)):
        directory = Path(result)
        if directory.is_dir():
            candidates = list(directory.glob("*.tsv.gz")) + list(directory.glob("*.tsv"))
            manifests = list(directory.glob("*manifest*.json"))
            if len(candidates) == 1 and len(manifests) == 1:
                return candidates[0], manifests[0]
    raise WorkflowError("build_model_table must return table_path and manifest_path artifacts")


def _chain_payload(result: Any) -> Mapping[str, Any]:
    if dataclasses.is_dataclass(result):
        result = {field.name: getattr(result, field.name) for field in dataclasses.fields(result)}
    if isinstance(result, Mapping):
        return result
    if isinstance(result, (str, Path)):
        path = Path(result)
        payload = path if path.is_file() else path / "chain_result.json"
        return _read_json(payload)
    if hasattr(result, "diagnostic_payload"):
        payload = result.diagnostic_payload()
        if isinstance(payload, Mapping):
            return payload
    raise WorkflowError("run_chain must return a diagnostics payload or chain_result.json path")


def _derive_seed(base_seed: int, cell: RunCell, holdout_kind: str, chain_index: int) -> int:
    material = (
        f"{base_seed}|{cell.stage}|K={cell.num_nodes}|rho={cell.purity:.8f}|"
        f"holdout={holdout_kind}|chain={chain_index}"
    )
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:4], "big") & 0x7FFFFFFF


def _run_cell(
    *,
    experiment_dir: Path,
    timestamp: datetime,
    git_sha: str,
    config: ExperimentConfig,
    cell: RunCell,
    table_paths: Mapping[float, Path],
    holdouts: Mapping[str, Mapping[str, Any]],
    chain_runner: Callable[..., Any],
    ledger: list[dict[str, Any]],
    resume: bool,
) -> dict[str, Any]:
    cell_seed = _derive_seed(config.seed, cell, "cell", 0)
    cell_id = _make_run_id(timestamp, git_sha, (cell.purity,), (cell.num_nodes,), cell_seed)
    cell_dir = experiment_dir / "runs" / f"{cell.stage}_{cell_id}"
    summary_path = cell_dir / "summary.json"
    if resume and summary_path.is_file():
        summary = dict(_read_json(summary_path))
        if summary.get("passed") is not True:
            raise WorkflowError(f"completed cell summary is not passing: {summary_path}")
        return summary
    _mkdir(cell_dir, exist_ok=resume)
    try:
        table_path = table_paths[cell.purity]
    except KeyError as exc:
        raise WorkflowError(f"no validated model table for rho={cell.purity}") from exc
    if cell.stage == "smoke":
        chain_count = config.smoke_chains
        iterations, burnin = config.smoke_iterations, config.smoke_burnin
    elif cell.stage == "pilot":
        chain_count = config.pilot_chains
        iterations, burnin = config.pilot_iterations, config.pilot_burnin
    else:
        chain_count = config.formal_chains
        iterations, burnin = config.formal_iterations, config.formal_burnin
    holdout_items = holdouts.items() if cell.formal else (("none", {"holdout_path": None}),)
    holdout_summaries: dict[str, Any] = {}

    for holdout_kind, holdout in holdout_items:
        fit_dir = cell_dir / holdout_kind
        _mkdir(fit_dir, exist_ok=resume)
        current_iterations = iterations
        prior_iterations: int | None = None
        extension_round = 0
        while True:
            results: list[Mapping[str, Any]] = []
            for chain_index in range(1, chain_count + 1):
                chain_dir = fit_dir / f"chain_{chain_index:02d}"
                chain_exists = chain_dir.exists()
                _mkdir(chain_dir, exist_ok=resume or extension_round > 0)
                seed = _derive_seed(config.seed, cell, holdout_kind, chain_index)
                chain_config = ChainConfig(
                    seed=seed,
                    num_nodes=cell.num_nodes,
                    iterations=current_iterations,
                    burnin=burnin,
                    thin=1,
                    ascat_purity=cell.purity,
                    checkpoint_every=config.checkpoint_every,
                )
                chain_config.validate()
                chain_resume = chain_exists or extension_round > 0
                if extension_round > 0:
                    assert prior_iterations is not None
                    old_config = dataclasses.replace(chain_config, iterations=prior_iterations)
                    _promote_checkpoint_iterations(chain_dir, old_config, chain_config)
                call = {
                    "table_path": table_path,
                    "config": chain_config,
                    "output_dir": chain_dir,
                    "holdout_path": holdout.get("holdout_path"),
                    "holdout_kind": holdout_kind,
                    "chain_index": chain_index,
                    "initialization": "overdispersed",
                    "resume": chain_resume,
                }
                ledger.append(
                    {
                        "adapter": "sampler.run_chain",
                        "action": "ess_extension" if extension_round else ("resume" if chain_resume else "start"),
                        "extension_round": extension_round,
                        "from_iterations": prior_iterations,
                        "to_iterations": current_iterations,
                        "cell": cell_id,
                        "holdout": holdout_kind,
                        "chain": chain_index,
                        "seed": seed,
                        "config": _jsonable(chain_config),
                    }
                )
                _atomic_json(experiment_dir / "command_ledger.json", {"entries": ledger})
                try:
                    result = chain_runner(**call)
                except TypeError as exc:
                    signature = inspect.signature(chain_runner)
                    raise WorkflowError(
                        f"run_chain adapter does not implement the workflow keyword contract {signature}"
                    ) from exc
                results.append(_chain_payload(result))

            try:
                diagnostics = summarize_chains(results)
            except Exception:
                if cell.stage == "smoke":
                    diagnostics = {
                        "formal_diagnostics_available": False,
                        "reason": "smoke validates I/O only",
                    }
                else:
                    raise
            if cell.formal:
                assert config.min_predictive_log_score is not None
                gate = evaluate_formal_gates(
                    diagnostics,
                    config.gate_thresholds,
                    min_predictive_log_score=config.min_predictive_log_score,
                )
                failures = _gate_failures(gate)
                ess_only = bool(failures) and failures <= {"bulk_ess", "tail_ess"}
                if ess_only and current_iterations < config.formal_max_iterations:
                    prior_iterations = current_iterations
                    current_iterations = min(
                        current_iterations + config.ess_extension_batch,
                        config.formal_max_iterations,
                    )
                    extension_round += 1
                    continue
            elif cell.stage == "pilot":
                gate = pilot_report(diagnostics)
            else:
                gate = {"smoke_completed": True, "formal_gate_not_evaluated": True}
            break
        summary = {"diagnostics": diagnostics, "gate": gate}
        _atomic_json(fit_dir / "diagnostics.json", summary)
        holdout_summaries[holdout_kind] = summary
        if cell.formal and gate.get("passed") is not True:
            raise GateFailure(
                f"formal gates failed for K={cell.num_nodes}, rho={cell.purity}, holdout={holdout_kind}"
            )

    cell_summary = {
        "run_id": cell_id,
        "stage": cell.stage,
        "K": cell.num_nodes,
        "rho_ASCAT": cell.purity,
        "seed_derivation": "sha256(base|stage|K|rho|holdout|chain), first 31 bits",
        "chains": chain_count,
        "iterations": current_iterations,
        "initial_iterations": iterations,
        "ess_extension_rounds": extension_round,
        "burnin": burnin,
        "thin": 1,
        "holdouts": holdout_summaries,
        "passed": True,
    }
    _atomic_json(cell_dir / "summary.json", cell_summary)
    return cell_summary


def run_experiment(
    config: ExperimentConfig | Path | str,
    *,
    chain_runner: Callable[..., Any] | None = None,
    table_builder: Callable[[BuildInputs, Path], Any] | None = None,
    now: datetime | None = None,
    git_sha: str | None = None,
) -> Path:
    """Run one immutable experiment and return its directory on success.

    Any exception or failed formal gate writes ``_FAILED`` and is re-raised;
    command-line callers therefore return non-zero.  ``_SUCCESS`` is created
    only after every requested stage and formal sensitivity cell passes.
    """

    if not isinstance(config, ExperimentConfig):
        config = load_config(config)
    config.validate()
    matrix = experiment_matrix(config)
    timestamp = now or datetime.now(timezone.utc)
    source_root = config.git_root or Path(__file__).resolve().parents[1]
    resolved_git_sha = git_sha or _git_sha(source_root)
    git_state = _git_worktree_state(source_root)
    if not git_state["clean"] and not config.allow_dirty_worktree:
        raise WorkflowError(
            "Git worktree is dirty; commit/stash changes before execution "
            "(allow_dirty_worktree is permitted only for smoke/pilot)"
        )
    generated_id = _make_run_id(
        timestamp,
        resolved_git_sha,
        [cell.purity for cell in matrix],
        [cell.num_nodes for cell in matrix],
        config.seed,
    )
    run_id = config.run_id or generated_id
    if config.run_id and not config.resume and config.run_id != generated_id:
        raise WorkflowError(
            "explicit run_id must equal the timestamp+git-sha+rho+K+seed identifier"
        )
    if config.resume:
        try:
            timestamp = datetime.strptime(run_id.split("_", 1)[0], "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc
            )
        except ValueError as exc:
            raise WorkflowError("resume run_id does not begin with a UTC workflow timestamp") from exc
    output_root = config.output_root.resolve()
    _mkdir(output_root)
    experiment_dir = output_root / run_id

    old_umask = os.umask(0o002)
    lock_handle = None
    created = False
    try:
        if config.resume:
            if not experiment_dir.is_dir():
                raise WorkflowError(f"resume run directory does not exist: {experiment_dir}")
            if (experiment_dir / "_SUCCESS").exists():
                raise WorkflowError(f"completed experiment is immutable: {experiment_dir}")
            created = True
        else:
            try:
                _mkdir(experiment_dir, exist_ok=False)
                created = True
            except FileExistsError as exc:
                raise WorkflowError(f"immutable experiment directory already exists: {experiment_dir}") from exc
        lock_path = experiment_dir / "run.lock"
        lock_handle = lock_path.open("r+" if config.resume else "x+")
        lock_path.chmod(0o664)
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise WorkflowError(f"experiment is already locked: {experiment_dir}") from exc

        _mkdir(experiment_dir / "logs", exist_ok=config.resume)
        resume_index = len(list(experiment_dir.glob("resume_command.*.json"))) + 1
        if config.resume and (experiment_dir / "_FAILED").exists():
            failed = experiment_dir / "_FAILED"
            receipt = experiment_dir / "logs" / f"_FAILED.before_resume.{resume_index:03d}"
            os.replace(failed, receipt)
            receipt.chmod(0o664)
        _atomic_json(
            experiment_dir
            / (f"resume_command.{resume_index:03d}.json" if config.resume else "command.json"),
            {
                "argv": sys.argv,
                "cwd": str(Path.cwd()),
                "run_id": run_id,
                "git_sha": resolved_git_sha,
                "git_state": git_state,
                "config": config,
            },
        )
        _atomic_json(experiment_dir / "status.json", {"status": "running", "run_id": run_id})
        ledger_path = experiment_dir / "command_ledger.json"
        ledger = list(_read_json(ledger_path).get("entries", [])) if config.resume and ledger_path.is_file() else []
        runner = chain_runner or _default_chain_runner

        if config.build_inputs is not None:
            config.build_inputs.validate()
            input_dir = experiment_dir / "input"
            if config.resume and input_dir.exists():
                table_path, manifest_path = _artifact_paths(input_dir)
            else:
                _mkdir(input_dir, exist_ok=False)
                builder = table_builder or _default_table_builder
                table_path, manifest_path = _artifact_paths(builder(config.build_inputs, input_dir))
        else:
            table_path = config.table_path
            manifest_path = config.validation_manifest
        assert table_path is not None and manifest_path is not None
        validation = validate_model_table_manifest(table_path, manifest_path, config.main_purity)
        table_paths: dict[float, Path] = {config.main_purity: table_path}
        input_validations: dict[str, Any] = {_rho_label(config.main_purity): validation}
        sensitivity_root = experiment_dir / "input_sensitivity"
        for purity in dict.fromkeys(cell.purity for cell in matrix):
            if purity == config.main_purity:
                continue
            sensitivity_dir = sensitivity_root / f"rho_{_rho_label(purity)}"
            if config.resume and sensitivity_dir.exists():
                derived_table = sensitivity_dir / "model_input.tsv"
                derived_manifest = sensitivity_dir / "validation_manifest.json"
            else:
                derived_table, derived_manifest = _derive_purity_sensitivity_table(
                    table_path,
                    purity=purity,
                    output_dir=sensitivity_dir,
                )
            table_paths[purity] = derived_table
            input_validations[_rho_label(purity)] = validate_model_table_manifest(
                derived_table,
                derived_manifest,
                purity,
            )
        _atomic_json(experiment_dir / "input_validation.json", input_validations)

        formal_requested = any(cell.formal for cell in matrix)
        holdouts: dict[str, Mapping[str, Any]] = {}
        prerequisite_summary: dict[str, Any] = {"input": input_validations}
        if formal_requested:
            assert config.ps_audit_manifest and config.simulation_manifest and config.holdout_metadata
            prerequisite_summary["ps_audit"] = _validate_ps_audit(config.ps_audit_manifest)
            prerequisite_summary["simulation"] = _validate_simulation_gate(config.simulation_manifest)
            rows = _read_metadata(config.holdout_metadata)
            prerequisite_summary["holdout_metadata"] = {
                **_reconcile_holdout_metadata(rows, table_path),
                "path": str(config.holdout_metadata),
                "sha256": _sha256(config.holdout_metadata),
            }
            holdout_root = experiment_dir / "holdouts"
            _mkdir(holdout_root, exist_ok=config.resume)
            for kind in ("ps", "chromosome", "ascat_segment"):
                holdout_dir = holdout_root / kind
                if config.resume and holdout_dir.exists():
                    holdout_manifest = dict(_read_json(holdout_dir / "manifest.json"))
                    holdouts[kind] = {
                        **holdout_manifest,
                        "holdout_path": holdout_dir / "holdout_site_ids.txt",
                    }
                else:
                    holdouts[kind] = create_grouped_holdout(
                        rows,
                        kind=kind,
                        fraction=config.holdout_fraction,
                        seed=config.seed,
                        output_dir=holdout_dir,
                    )
        _atomic_json(experiment_dir / "prerequisites.json", prerequisite_summary)

        cell_summaries = []
        for cell in matrix:
            cell_summaries.append(
                _run_cell(
                    experiment_dir=experiment_dir,
                    timestamp=timestamp,
                    git_sha=resolved_git_sha,
                    config=config,
                    cell=cell,
                    table_paths=table_paths,
                    holdouts=holdouts,
                    chain_runner=runner,
                    ledger=ledger,
                    resume=config.resume,
                )
            )
        manifest = {
            "run_id": run_id,
            "status": "success",
            "git_sha": resolved_git_sha,
            "input_tables": input_validations,
            "cells": cell_summaries,
        }
        _atomic_json(experiment_dir / "manifest.json", manifest)
        _atomic_json(experiment_dir / "status.json", {"status": "success", "run_id": run_id})
        _atomic_json(experiment_dir / "artifact_inventory.json", _artifact_inventory(experiment_dir))
        _atomic_write(experiment_dir / "_SUCCESS", "success\n")
        return experiment_dir
    except Exception as exc:
        if created and experiment_dir.exists():
            failure = {
                "status": "failed",
                "run_id": run_id,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            try:
                _atomic_json(experiment_dir / "status.json", failure)
                _atomic_write(experiment_dir / "logs" / "workflow_error.log", traceback.format_exc())
                _atomic_write(experiment_dir / "_FAILED", f"{type(exc).__name__}: {exc}\n")
            except Exception:
                pass
        if isinstance(exc, WorkflowError):
            raise
        raise WorkflowError(str(exc)) from exc
    finally:
        if lock_handle is not None:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            finally:
                lock_handle.close()
        os.umask(old_umask)
