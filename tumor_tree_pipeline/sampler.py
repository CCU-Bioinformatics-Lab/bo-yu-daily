"""Fail-closed finite-K Metropolis-within-Gibbs tumor-tree sampler.

The public seam is :func:`run_chain`.  It accepts exactly one canonical model
table, owns one immutable output directory, and can resume only from its own
atomically written checkpoint.  No legacy input path exists in this module.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .contracts import ChainConfig
from .model import CompiledModel, ModelData, compile_model, load_model_table


ROOT_LABEL = "tumor_root"
CHECKPOINT_NAME = "checkpoint.json.gz"
COMPLETE_NAME = "chain_complete.json"
SAMPLES_NAME = "samples.jsonl.gz"
DIAGNOSTICS_NAME = "diagnostics.json"
TREE_NAME = "representative_tree.json"


@dataclass(frozen=True)
class ChainResult:
    outdir: Path
    samples: Path
    diagnostics: Path
    representative_tree: Path
    checkpoint: Path
    posterior_samples: int
    resumed: bool


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    encoded = (json.dumps(_jsonable(payload), indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    _atomic_write_bytes(path, encoded)


def _atomic_write_gzip_json_lines(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    text = "".join(
        json.dumps(_jsonable(row), separators=(",", ":"), sort_keys=True, allow_nan=False) + "\n"
        for row in rows
    ).encode()
    _atomic_write_bytes(path, gzip.compress(text, compresslevel=6, mtime=0))


def _write_checkpoint_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    """Write one self-contained checkpoint; exposed for interruption tests."""

    encoded = (json.dumps(_jsonable(payload), separators=(",", ":"), sort_keys=True, allow_nan=False) + "\n").encode()
    _atomic_write_bytes(path, gzip.compress(encoded, compresslevel=6, mtime=0))


def _read_checkpoint(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("checkpoint root must be a JSON object")
    return payload


def dirichlet_logpdf(values: Sequence[float], alpha: Sequence[float]) -> float:
    values = np.asarray(values, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    if values.shape != alpha.shape or np.any(values <= 0.0) or np.any(alpha <= 0.0):
        return float("-inf")
    if not math.isclose(float(values.sum()), 1.0, rel_tol=0.0, abs_tol=1e-9):
        return float("-inf")
    return float(
        math.lgamma(float(alpha.sum()))
        - sum(math.lgamma(float(value)) for value in alpha)
        + np.sum((alpha - 1.0) * np.log(values))
    )


def eta_bridge_alpha(reference_eta: Sequence[float], concentration: float = 50.0) -> np.ndarray:
    """Independent bridge density centered on a tumor-only eta scaffold."""

    reference = np.asarray(reference_eta, dtype=float)
    if concentration <= 0.0 or np.any(reference <= 0.0):
        raise ValueError("eta bridge requires positive reference mass and concentration")
    reference = reference / reference.sum()
    return 1.0 + concentration * reference


def independent_eta_bridge_log_acceptance(
    current_score: float,
    proposed_score: float,
    current_eta: Sequence[float],
    proposed_eta: Sequence[float],
    reference_eta: Sequence[float],
    concentration: float = 50.0,
) -> float:
    """Correct independent-MH ratio: target delta + log q(x) - log q(y)."""

    alpha = eta_bridge_alpha(reference_eta, concentration)
    log_q_current = dirichlet_logpdf(current_eta, alpha)
    log_q_proposed = dirichlet_logpdf(proposed_eta, alpha)
    return proposed_score - current_score + log_q_current - log_q_proposed


def _tree_valid(parents: Sequence[int]) -> bool:
    size = len(parents)
    for child, parent in enumerate(parents):
        if parent < -1 or parent >= size or parent == child:
            return False
        seen = {child}
        cursor = parent
        while cursor != -1:
            if cursor in seen:
                return False
            seen.add(cursor)
            cursor = parents[cursor]
    return True


def _children(parents: Sequence[int]) -> list[list[int]]:
    children = [[] for _ in parents]
    for child, parent in enumerate(parents):
        if parent != -1:
            children[parent].append(child)
    return children


def cumulative_phi(parents: Sequence[int], eta: Sequence[float]) -> np.ndarray:
    """Clone cumulative prevalence; ``eta[0]`` is residual tumor root mass."""

    if len(eta) != len(parents) + 1 or not _tree_valid(parents):
        raise ValueError("invalid eta/tree dimensions")
    eta = np.asarray(eta, dtype=float)
    if np.any(eta <= 0.0) or not math.isclose(float(eta.sum()), 1.0, abs_tol=1e-9):
        raise ValueError("eta must be a positive simplex")
    children = _children(parents)
    phi = np.empty(len(parents), dtype=float)

    def visit(node: int) -> float:
        value = float(eta[node + 1]) + sum(visit(child) for child in children[node])
        phi[node] = value
        return value

    for node, parent in enumerate(parents):
        if parent == -1:
            visit(node)
    return phi


def _tree_log_prior(parents: Sequence[int]) -> float:
    children = _children(parents)
    depths: list[int] = []
    for node in range(len(parents)):
        depth = 1
        cursor = parents[node]
        while cursor != -1:
            depth += 1
            cursor = parents[cursor]
        depths.append(depth)
    return float(sum(-0.35 * depth - 0.12 * len(children[node]) ** 2 for node, depth in enumerate(depths)))


def _topology_support(parents: Sequence[int]) -> list[tuple[int, ...]]:
    support: list[tuple[int, ...]] = []
    for child in range(len(parents)):
        for proposed_parent in range(-1, len(parents)):
            if proposed_parent in {child, parents[child]}:
                continue
            proposal = list(parents)
            proposal[child] = proposed_parent
            if _tree_valid(proposal):
                support.append(tuple(proposal))
    return support


def _categorical(probabilities: np.ndarray, rng: np.random.Generator) -> int:
    cumulative = np.cumsum(probabilities)
    return min(int(np.searchsorted(cumulative, rng.random(), side="right")), len(probabilities) - 1)


def _assignment_sweep(
    matrix: np.ndarray, assignment_weights: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    logits = matrix + np.log(np.maximum(assignment_weights, 1e-300))[None, :]
    logits -= logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    return np.asarray([_categorical(row, rng) for row in probabilities], dtype=np.int16)


def _state_score_from_matrix(
    parents: Sequence[int], z: np.ndarray, assignment_weights: np.ndarray, matrix: np.ndarray
) -> float:
    selected = matrix[np.arange(len(z)), z]
    assignment_term = np.log(np.maximum(assignment_weights[z], 1e-300))
    return float(selected.sum() + assignment_term.sum() + _tree_log_prior(parents))


def _score_state(
    compiled: CompiledModel,
    parents: Sequence[int],
    eta: Sequence[float],
    z: np.ndarray,
    assignment_weights: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray]:
    phi = cumulative_phi(parents, eta)
    matrix = compiled.likelihood_matrix(phi)
    return _state_score_from_matrix(parents, z, assignment_weights, matrix), matrix, phi


def _initial_state(
    compiled: CompiledModel,
    num_nodes: int,
    *,
    initialization: str = "deterministic",
    rng: np.random.Generator | None = None,
) -> tuple[tuple[int, ...], np.ndarray, np.ndarray]:
    """Construct an initial state without using purity as a root target.

    ``overdispersed`` draws both topology and population mass from the chain's
    seeded RNG.  It is therefore reproducible while placing independent chains
    in intentionally different regions of state space.
    """

    if initialization == "deterministic":
        parents = tuple([-1] + list(range(num_nodes - 1)))
        eta = np.asarray([0.10] + [0.90 / num_nodes] * num_nodes, dtype=float)
    elif initialization == "overdispersed":
        if rng is None:
            raise ValueError("overdispersed initialization requires an RNG")
        parents = tuple([-1] + [int(rng.integers(0, node)) for node in range(1, num_nodes)])
        # eta[0] is residual tumor mass not assigned to a modeled mutation-
        # bearing clone; it is sampled like the other simplex components and
        # is not anchored to ASCAT purity.
        eta = rng.dirichlet(np.full(num_nodes + 1, 0.30, dtype=float))
    else:
        raise ValueError("initialization must be 'deterministic' or 'overdispersed'")
    phi = cumulative_phi(parents, eta)
    # Initial labels are selected through the same emission used by MCMC.
    # This keeps purity out of topology/root priors and proposal targets.
    z = np.argmax(compiled.likelihood_matrix(phi), axis=1).astype(np.int16)
    return parents, eta, z


def _sample_record(
    iteration: int,
    score: float,
    parents: Sequence[int],
    eta: Sequence[float],
    z: np.ndarray,
) -> dict[str, Any]:
    phi = cumulative_phi(parents, eta)
    occupancy = np.bincount(z, minlength=len(parents))
    return {
        "iteration": iteration,
        "log_posterior": float(score),
        "parents": list(parents),
        "eta": [float(value) for value in eta],
        "phi": [float(value) for value in phi],
        "occupancy": [int(value) for value in occupancy],
    }


def _checkpoint_payload(
    *,
    input_hash: str,
    config: ChainConfig,
    exclude_ids: frozenset[str],
    next_iteration: int,
    parents: Sequence[int],
    eta: np.ndarray,
    reference_eta: np.ndarray,
    z: np.ndarray,
    assignment_weights: np.ndarray,
    score: float,
    counters: Mapping[str, int],
    retained_samples: Sequence[Mapping[str, Any]],
    assignment_counts: np.ndarray,
    best_sample: Mapping[str, Any] | None,
    best_assignments: np.ndarray | None,
    rng: np.random.Generator,
    initialization: str,
) -> dict[str, Any]:
    return {
        "checkpoint_version": 1,
        "input_sha256": input_hash,
        "config": asdict(config),
        "initialization": initialization,
        "exclude_ids": sorted(exclude_ids),
        "next_iteration": next_iteration,
        "parents": list(parents),
        "eta": eta,
        "reference_eta": reference_eta,
        "z": z,
        "assignment_weights": assignment_weights,
        "score": score,
        "counters": dict(counters),
        "retained_samples": list(retained_samples),
        "assignment_counts": assignment_counts,
        "best_sample": best_sample,
        "best_assignments": best_assignments,
        "rng_state": rng.bit_generator.state,
    }


def _prepare_output_directory(outdir: Path, resume: bool) -> tuple[Path, bool]:
    complete = outdir / COMPLETE_NAME
    checkpoint = outdir / CHECKPOINT_NAME
    if complete.exists():
        raise FileExistsError(f"completed chain output is immutable: {outdir}")
    if outdir.exists():
        entries = list(outdir.iterdir())
        if entries and not resume:
            raise FileExistsError(f"refusing to overwrite non-empty chain output: {outdir}")
        if resume and not checkpoint.is_file():
            raise FileNotFoundError(f"resume requested but checkpoint is missing: {checkpoint}")
    elif resume:
        raise FileNotFoundError(f"resume requested but output directory does not exist: {outdir}")
    else:
        outdir.mkdir(parents=True)
    return checkpoint, resume


def run_chain(
    integrated_input: Path,
    outdir: Path,
    config: ChainConfig,
    *,
    exclude_ids: frozenset[str] = frozenset(),
    resume: bool = False,
    initialization: str = "deterministic",
) -> ChainResult:
    """Run or resume one finite-K posterior chain.

    Completion is transactional at the directory level: samples, diagnostics,
    and representative tree are atomically replaced first, then
    ``chain_complete.json`` is created last.  A completed directory is always
    rejected, including when ``resume=True``.
    """

    config.validate()
    if initialization not in {"deterministic", "overdispersed"}:
        raise ValueError("initialization must be 'deterministic' or 'overdispersed'")
    integrated_input = Path(integrated_input)
    outdir = Path(outdir)
    if not integrated_input.is_file():
        raise FileNotFoundError(f"canonical integrated input does not exist: {integrated_input}")
    checkpoint_path, resumed = _prepare_output_directory(outdir, resume)
    exclude_ids = frozenset(exclude_ids)
    input_hash = _sha256(integrated_input)
    data: ModelData = load_model_table(
        integrated_input, config.ascat_purity, exclude_ids=exclude_ids
    )
    compiled = compile_model(data)

    if resume:
        payload = _read_checkpoint(checkpoint_path)
        if payload.get("checkpoint_version") != 1:
            raise ValueError("unsupported checkpoint version")
        if payload.get("input_sha256") != input_hash:
            raise ValueError("checkpoint input hash does not match canonical table")
        if payload.get("config") != asdict(config):
            raise ValueError("checkpoint ChainConfig does not match requested configuration")
        if payload.get("initialization", "deterministic") != initialization:
            raise ValueError("checkpoint initialization does not match requested initialization")
        if payload.get("exclude_ids") != sorted(exclude_ids):
            raise ValueError("checkpoint exclude_ids do not match requested holdout")
        next_iteration = int(payload["next_iteration"])
        parents = tuple(int(value) for value in payload["parents"])
        eta = np.asarray(payload["eta"], dtype=float)
        reference_eta = np.asarray(payload["reference_eta"], dtype=float)
        z = np.asarray(payload["z"], dtype=np.int16)
        assignment_weights = np.asarray(payload["assignment_weights"], dtype=float)
        current_score = float(payload["score"])
        counters = Counter({key: int(value) for key, value in payload["counters"].items()})
        retained_samples = list(payload["retained_samples"])
        assignment_counts = np.asarray(payload["assignment_counts"], dtype=np.int64)
        best_sample = payload.get("best_sample")
        best_assignments_raw = payload.get("best_assignments")
        best_assignments = (
            np.asarray(best_assignments_raw, dtype=np.int16)
            if best_assignments_raw is not None
            else None
        )
        rng = np.random.default_rng()
        rng.bit_generator.state = payload["rng_state"]
        if len(z) != len(data.sites) or len(parents) != config.num_nodes:
            raise ValueError("checkpoint state dimensions disagree with canonical input/config")
        recalculated, _, _ = _score_state(compiled, parents, eta, z, assignment_weights)
        if not math.isclose(recalculated, current_score, rel_tol=1e-10, abs_tol=1e-8):
            raise ValueError("checkpoint score fails deterministic integrity check")
    else:
        rng = np.random.default_rng(config.seed)
        parents, eta, z = _initial_state(
            compiled,
            config.num_nodes,
            initialization=initialization,
            rng=rng,
        )
        reference_eta = eta.copy()
        assignment_weights = rng.dirichlet(
            np.bincount(z, minlength=config.num_nodes).astype(float) + 1.0
        )
        current_score, _, _ = _score_state(
            compiled, parents, eta, z, assignment_weights
        )
        next_iteration = 0
        counters = Counter()
        retained_samples: list[dict[str, Any]] = []
        assignment_counts = np.zeros((len(z), config.num_nodes), dtype=np.int64)
        best_sample: dict[str, Any] | None = None
        best_assignments: np.ndarray | None = None

    for iteration in range(next_iteration, config.iterations):
        # Gibbs: assignment mixture weights and mutation-to-node labels.
        assignment_weights = rng.dirichlet(
            np.bincount(z, minlength=config.num_nodes).astype(float) + 1.0
        )
        _, assignment_matrix, _ = _score_state(
            compiled, parents, eta, z, assignment_weights
        )
        z = _assignment_sweep(assignment_matrix, assignment_weights, rng)
        current_score = _state_score_from_matrix(
            parents, z, assignment_weights, assignment_matrix
        )

        # MH: full eta random walk with explicit forward/reverse densities.
        eta_alpha_forward = 1.0 + 80.0 * eta
        proposed_eta = rng.dirichlet(eta_alpha_forward)
        proposed_score, _, _ = _score_state(
            compiled, parents, proposed_eta, z, assignment_weights
        )
        eta_alpha_reverse = 1.0 + 80.0 * proposed_eta
        log_accept = (
            proposed_score
            - current_score
            + dirichlet_logpdf(eta, eta_alpha_reverse)
            - dirichlet_logpdf(proposed_eta, eta_alpha_forward)
        )
        counters["eta_proposals"] += 1
        if math.log(max(1e-300, rng.random())) < log_accept:
            eta = proposed_eta
            current_score = proposed_score
            counters["eta_accepted"] += 1

        # Independent eta bridge.  Its density is fixed at reference_eta, so
        # q(current)/q(proposed) does not cancel unless both densities match.
        if rng.random() < 0.05:
            bridge_alpha = eta_bridge_alpha(reference_eta)
            bridge_eta = rng.dirichlet(bridge_alpha)
            bridge_score, _, _ = _score_state(
                compiled, parents, bridge_eta, z, assignment_weights
            )
            bridge_accept = independent_eta_bridge_log_acceptance(
                current_score,
                bridge_score,
                eta,
                bridge_eta,
                reference_eta,
            )
            counters["eta_bridge_proposals"] += 1
            if math.log(max(1e-300, rng.random())) < bridge_accept:
                eta = bridge_eta
                current_score = bridge_score
                counters["eta_bridge_accepted"] += 1

        # MH: one valid parent reassignment with exact finite-support q ratio.
        support = _topology_support(parents)
        if support:
            proposal_index = int(rng.integers(0, len(support)))
            proposed_parents = support[proposal_index]
            proposed_score, _, _ = _score_state(
                compiled, proposed_parents, eta, z, assignment_weights
            )
            reverse_support = _topology_support(proposed_parents)
            log_accept = (
                proposed_score
                - current_score
                + math.log(len(support))
                - math.log(len(reverse_support))
            )
            counters["topology_proposals"] += 1
            if math.log(max(1e-300, rng.random())) < log_accept:
                parents = proposed_parents
                current_score = proposed_score
                counters["topology_accepted"] += 1

        completed_iteration = iteration + 1
        if iteration >= config.burnin and (iteration - config.burnin) % config.thin == 0:
            record = _sample_record(
                completed_iteration, current_score, parents, eta, z
            )
            retained_samples.append(record)
            assignment_counts[np.arange(len(z)), z] += 1
            if best_sample is None or current_score > float(best_sample["log_posterior"]):
                best_sample = dict(record)
                best_assignments = z.copy()

        if completed_iteration % config.checkpoint_every == 0:
            _write_checkpoint_atomic(
                checkpoint_path,
                _checkpoint_payload(
                    input_hash=input_hash,
                    config=config,
                    exclude_ids=exclude_ids,
                    next_iteration=completed_iteration,
                    parents=parents,
                    eta=eta,
                    reference_eta=reference_eta,
                    z=z,
                    assignment_weights=assignment_weights,
                    score=current_score,
                    counters=counters,
                    retained_samples=retained_samples,
                    assignment_counts=assignment_counts,
                    best_sample=best_sample,
                    best_assignments=best_assignments,
                    rng=rng,
                    initialization=initialization,
                ),
            )

    if not retained_samples or best_sample is None or best_assignments is None:
        raise RuntimeError("chain retained no posterior samples")

    # Persist a final resumable state before any terminal artifact is written.
    _write_checkpoint_atomic(
        checkpoint_path,
        _checkpoint_payload(
            input_hash=input_hash,
            config=config,
            exclude_ids=exclude_ids,
            next_iteration=config.iterations,
            parents=parents,
            eta=eta,
            reference_eta=reference_eta,
            z=z,
            assignment_weights=assignment_weights,
            score=current_score,
            counters=counters,
            retained_samples=retained_samples,
            assignment_counts=assignment_counts,
            best_sample=best_sample,
            best_assignments=best_assignments,
            rng=rng,
            initialization=initialization,
        ),
    )

    samples_path = outdir / SAMPLES_NAME
    diagnostics_path = outdir / DIAGNOSTICS_NAME
    tree_path = outdir / TREE_NAME
    _atomic_write_gzip_json_lines(samples_path, retained_samples)
    phi_samples = np.asarray([sample["phi"] for sample in retained_samples], dtype=float)
    logpost = np.asarray([sample["log_posterior"] for sample in retained_samples], dtype=float)
    diagnostics = {
        "model": "finite_K_metropolis_within_gibbs",
        "input_schema": "hcc1395_tumor_tree_input/v2",
        "input_sha256": input_hash,
        "observed_sites": len(data.sites),
        "excluded_sites": len(exclude_ids),
        "posterior_samples": len(retained_samples),
        "config": asdict(config),
        "resumed": resumed,
        "eta_root_semantics": "residual_tumor_population_mass",
        "purity_role": "emission_only",
        "multiplicity_role": "CN_only_prior_marginalization",
        "ps_role": "not_loaded_by_likelihood",
        "hastings_correction": {
            "eta_random_walk": True,
            "eta_independent_bridge": True,
            "topology_finite_support": True,
        },
        "eta_acceptance": counters["eta_accepted"] / max(1, counters["eta_proposals"]),
        "eta_bridge_acceptance": counters["eta_bridge_accepted"] / max(1, counters["eta_bridge_proposals"]),
        "topology_acceptance": counters["topology_accepted"] / max(1, counters["topology_proposals"]),
        "counters": dict(counters),
        "log_posterior": {
            "minimum": float(logpost.min()),
            "maximum": float(logpost.max()),
            "mean": float(logpost.mean()),
        },
        "phi_mean": [float(value) for value in phi_samples.mean(axis=0)],
        "checkpoint": CHECKPOINT_NAME,
    }
    assignment_probabilities = assignment_counts / len(retained_samples)
    map_assignments = np.argmax(assignment_probabilities, axis=1)
    best_parents = tuple(int(value) for value in best_sample["parents"])
    representative = {
        "model": "finite_K_metropolis_within_gibbs",
        "posterior_status": "candidate_tree",
        "root": ROOT_LABEL,
        "root_semantics": "residual_tumor_population_mass",
        "selected_edges": [
            {
                "parent": ROOT_LABEL if parent == -1 else f"clone_{parent + 1}",
                "child": f"clone_{child + 1}",
            }
            for child, parent in enumerate(best_parents)
        ],
        "best_sample": best_sample,
        "best_sample_assignments": {
            site.mutation_id: f"clone_{int(node) + 1}"
            for site, node in zip(data.sites, best_assignments)
        },
        "posterior_map_assignments": {
            site.mutation_id: {
                "node": f"clone_{int(map_assignments[index]) + 1}",
                "probability": float(assignment_probabilities[index, map_assignments[index]]),
            }
            for index, site in enumerate(data.sites)
        },
    }
    _atomic_write_json(diagnostics_path, diagnostics)
    _atomic_write_json(tree_path, representative)
    _atomic_write_json(
        outdir / COMPLETE_NAME,
        {
            "status": "complete",
            "input_sha256": input_hash,
            "posterior_samples": len(retained_samples),
            "artifacts": [SAMPLES_NAME, DIAGNOSTICS_NAME, TREE_NAME, CHECKPOINT_NAME],
        },
    )
    return ChainResult(
        outdir=outdir,
        samples=samples_path,
        diagnostics=diagnostics_path,
        representative_tree=tree_path,
        checkpoint=checkpoint_path,
        posterior_samples=len(retained_samples),
        resumed=resumed,
    )
