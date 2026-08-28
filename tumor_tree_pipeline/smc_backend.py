"""Python adapter for the Rao--Blackwellized annealed SMC backend.

The adapter owns particle state and artifact publication inside the workflow
package.  It consumes the same validated canonical table and holdout exclude
    IDs as the C++ backend, and it never emits MCMC-chain semantics: latent
assignments and multiplicities are integrated through site responsibilities.
"""

from __future__ import annotations

import dataclasses
import gzip
import json
import math
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from .contracts import INFERENCE_ALGORITHM_ID, SMC_SAMPLE_KIND, SMCConfig
from .model import (
    ModelData,
    bulk_log_likelihood_for_candidate,
    compile_model,
    load_model_table,
)
from .provenance import sha256_file


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


@dataclass
class _Particle:
    parents: np.ndarray
    eta: np.ndarray
    log_likelihood: float
    log_prior: float = 0.0


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(raw_temporary)
    try:
        temporary.write_bytes(payload)
        temporary.chmod(0o664)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_text(path: Path, text: str) -> None:
    _atomic_write(path, text.encode("utf-8"))


def _atomic_gzip_text(path: Path, text: str) -> None:
    encoded = gzip.compress(text.encode("utf-8"), compresslevel=6, mtime=0)
    _atomic_write(path, encoded)


def _json_line(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n"


def _logsumexp(values: np.ndarray) -> float:
    top = float(np.max(values))
    if not math.isfinite(top):
        return top
    return top + math.log(float(np.exp(values - top).sum()))


def _softmax(values: np.ndarray) -> np.ndarray:
    top = float(np.max(values))
    shifted = np.exp(values - top)
    return shifted / shifted.sum()


def _eta_to_alr(eta: np.ndarray) -> np.ndarray:
    return np.log(eta[:-1] / eta[-1])


def _alr_to_eta(values: np.ndarray) -> np.ndarray:
    return _softmax(np.concatenate((values, np.zeros(1, dtype=float))))


def _log_simplex_jacobian(eta: np.ndarray) -> float:
    return float(np.log(eta).sum())


def _random_tree(rng: np.random.Generator, num_nodes: int) -> np.ndarray:
    # Parent indices are always earlier than the child.  This gives exactly
    # one founder under the structural root and makes descendant accumulation
    # deterministic without changing the canonical input contract.
    parents = np.full(num_nodes, -1, dtype=np.int64)
    for child in range(1, num_nodes):
        parents[child] = int(rng.integers(0, child))
    return parents


def _tree_log_prior(parents: np.ndarray) -> float:
    if len(parents) < 2 or parents[0] != -1:
        raise ValueError("SMC topology must have one founder at index zero")
    for child, parent in enumerate(parents[1:], start=1):
        if not 0 <= int(parent) < child:
            raise ValueError("SMC topology contains an invalid parent index")
    return float(-sum(math.log(child) for child in range(1, len(parents))))


def _phi(parents: np.ndarray, eta: np.ndarray) -> np.ndarray:
    result = np.asarray(eta, dtype=float).copy()
    for child in range(len(parents) - 1, 0, -1):
        result[int(parents[child])] += result[child]
    # Descendant sums are mathematically bounded by one; clip round-off at
    # the boundary before passing them to the strict canonical likelihood API.
    return np.clip(result, 0.0, 1.0)


def _score(compiled: Any, parents: np.ndarray, eta: np.ndarray) -> float:
    return float(compiled.likelihood_matrix(_phi(parents, eta)).sum())


def _particle_count_by_topology(particles: Iterable[_Particle]) -> Counter[tuple[int, ...]]:
    return Counter(tuple(int(value) for value in particle.parents) for particle in particles)


def _particle_diversity(particles: list[_Particle]) -> float:
    return len(_particle_count_by_topology(particles)) / len(particles)


def _weighted_ess(log_weights: np.ndarray) -> float:
    normalized = np.exp(log_weights - _logsumexp(log_weights))
    return float(1.0 / np.square(normalized).sum())


def _conditional_ess(log_likelihood: np.ndarray, delta_beta: float) -> float:
    log_increment = delta_beta * log_likelihood
    normalized = np.exp(log_increment - _logsumexp(log_increment))
    return float(1.0 / np.square(normalized).sum())


def _next_beta(
    beta: float,
    log_likelihood: np.ndarray,
    target_fraction: float,
) -> tuple[float, float]:
    remaining = 1.0 - beta
    if remaining <= 1e-12:
        return 1.0, float(len(log_likelihood))
    target = target_fraction * len(log_likelihood)
    if _conditional_ess(log_likelihood, remaining) >= target:
        return 1.0, _conditional_ess(log_likelihood, remaining)
    low, high = 0.0, remaining
    for _ in range(48):
        middle = (low + high) / 2.0
        if _conditional_ess(log_likelihood, middle) >= target:
            low = middle
        else:
            high = middle
    delta = max(low, np.finfo(float).eps)
    return beta + delta, _conditional_ess(log_likelihood, delta)


def _systematic_indices(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    count = len(weights)
    cumulative = np.cumsum(weights)
    positions = (rng.random() + np.arange(count)) / count
    return np.searchsorted(cumulative, positions, side="right").clip(0, count - 1)


def _copy_particles(particles: list[_Particle], indices: np.ndarray) -> list[_Particle]:
    return [
        _Particle(
            parents=particles[int(index)].parents.copy(),
            eta=particles[int(index)].eta.copy(),
            log_likelihood=particles[int(index)].log_likelihood,
            log_prior=particles[int(index)].log_prior,
        )
        for index in indices
    ]


def _rejuvenate(
    particles: list[_Particle],
    *,
    compiled: Any,
    beta: float,
    config: SMCConfig,
    rng: np.random.Generator,
) -> dict[str, Any]:
    etas = np.asarray([particle.eta for particle in particles], dtype=float)
    covariance = np.var(etas[:, :-1], axis=0) + 1e-6
    eta_proposals = eta_accepted = 0
    topology_proposals = topology_accepted = 0
    eta_moves: list[float] = []
    topology_changes = 0
    sweeps = 0
    stop_reason = "maximum_sweeps"

    for sweep in range(config.max_rejuvenation_sweeps):
        sweeps = sweep + 1
        for particle in particles:
            old_eta = particle.eta
            old_phi = _phi(particle.parents, old_eta)
            proposed_alr = _eta_to_alr(old_eta) + rng.normal(
                0.0, config.eta_rw_scale * np.sqrt(covariance)
            )
            proposed_eta = _alr_to_eta(proposed_alr)
            proposed_phi = _phi(particle.parents, proposed_eta)
            proposed_ll = _score(compiled, particle.parents, proposed_eta)
            log_accept = (
                beta * (proposed_ll - particle.log_likelihood)
                + _log_simplex_jacobian(proposed_eta)
                - _log_simplex_jacobian(old_eta)
            )
            eta_proposals += 1
            eta_moves.append(float(np.abs(proposed_eta - old_eta).sum()))
            if math.log(rng.random()) < min(0.0, log_accept):
                particle.eta = proposed_eta
                particle.log_likelihood = proposed_ll
                eta_accepted += 1

            child = int(rng.integers(1, config.num_nodes))
            candidate = particle.parents.copy()
            candidate[child] = int(rng.integers(0, child))
            if not np.array_equal(candidate, particle.parents):
                candidate_prior = _tree_log_prior(candidate)
                candidate_ll = _score(compiled, candidate, particle.eta)
                log_accept = (
                    beta * (candidate_ll - particle.log_likelihood)
                    + candidate_prior - particle.log_prior
                )
                topology_proposals += 1
                if math.log(rng.random()) < min(0.0, log_accept):
                    particle.parents = candidate
                    particle.log_likelihood = candidate_ll
                    particle.log_prior = candidate_prior
                    topology_accepted += 1
                    topology_changes += 1

            for _ in range(config.global_topology_moves):
                candidate = _random_tree(rng, config.num_nodes)
                if np.array_equal(candidate, particle.parents):
                    continue
                candidate_prior = _tree_log_prior(candidate)
                candidate_ll = _score(compiled, candidate, particle.eta)
                log_accept = (
                    beta * (candidate_ll - particle.log_likelihood)
                    + candidate_prior - particle.log_prior
                )
                topology_proposals += 1
                if math.log(rng.random()) < min(0.0, log_accept):
                    particle.parents = candidate
                    particle.log_likelihood = candidate_ll
                    particle.log_prior = candidate_prior
                    topology_accepted += 1
                    topology_changes += 1

        eta_rate = eta_accepted / max(1, eta_proposals)
        topology_rate = topology_accepted / max(1, topology_proposals)
        if sweeps >= config.min_rejuvenation_sweeps and (
            topology_changes > 0 and eta_rate >= 0.05 and topology_rate >= 0.01
        ):
            stop_reason = "decorrelation_signal"
            break

    return {
        "sweeps": sweeps,
        "stop_reason": stop_reason,
        "eta_acceptance": eta_accepted / max(1, eta_proposals),
        "topology_acceptance": topology_accepted / max(1, topology_proposals),
        "eta_mean_move": float(np.mean(eta_moves)) if eta_moves else 0.0,
        "eta_covariance_regularization": 1e-6,
        "topology_change_rate": topology_changes / max(1, topology_proposals),
        "eta_proposals": eta_proposals,
        "topology_proposals": topology_proposals,
    }


def _sample_record(particle: _Particle, particle_id: int) -> dict[str, Any]:
    phi = _phi(particle.parents, particle.eta)
    return {
        "sample_kind": SMC_SAMPLE_KIND,
        "particle_id": particle_id,
        "parents": [int(value) for value in particle.parents],
        "eta": [float(value) for value in particle.eta],
        "occupancy": [float(value) for value in particle.eta],
        "phi": [float(value) for value in phi],
        "log_likelihood": float(particle.log_likelihood),
    }


def _posterior_quantile(values: np.ndarray, probability: float) -> float:
    return float(np.quantile(values, probability, method="linear"))


def _summary_tsv(particles: list[_Particle]) -> str:
    matrix = np.asarray([_phi(p.parents, p.eta) for p in particles], dtype=float)
    lines = ["clone\tccf_median\tccf_q025\tccf_q975\tphi_median\tphi_q025\tphi_q975"]
    for index in range(matrix.shape[1]):
        q025 = _posterior_quantile(matrix[:, index], 0.025)
        median = _posterior_quantile(matrix[:, index], 0.5)
        q975 = _posterior_quantile(matrix[:, index], 0.975)
        lines.append(f"clone_{index + 1}\t{median:.17g}\t{q025:.17g}\t{q975:.17g}\t{median:.17g}\t{q025:.17g}\t{q975:.17g}")
    return "\n".join(lines) + "\n"


def _topology_tsv(particles: list[_Particle]) -> str:
    counts: Counter[tuple[str, str]] = Counter()
    for particle in particles:
        for child, parent in enumerate(particle.parents):
            parent_label = "tumor_root" if int(parent) == -1 else f"clone_{int(parent) + 1}"
            counts[(parent_label, f"clone_{child + 1}")] += 1
    lines = ["parent\tchild\tsupport_count\tretained_samples\tsupport_fraction"]
    for (parent, child), count in sorted(counts.items()):
        lines.append(f"{parent}\t{child}\t{count}\t{len(particles)}\t{count / len(particles):.17g}")
    return "\n".join(lines) + "\n"


def _responsibilities(
    data: ModelData, particles: list[_Particle]
) -> tuple[np.ndarray, np.ndarray]:
    assignment = np.zeros((len(data.sites), len(particles[0].eta)), dtype=float)
    multiplicities = tuple(sorted({m for site in data.sites for m in site.multiplicities}))
    multiplicity_index = {value: index for index, value in enumerate(multiplicities)}
    posterior = np.zeros((len(data.sites), len(multiplicities)), dtype=float)
    for particle in particles:
        phi = _phi(particle.parents, particle.eta)
        for site_index, site in enumerate(data.sites):
            components: list[tuple[int, int, float]] = []
            for node, clone_phi in enumerate(phi):
                for candidate in site.genotype_candidates:
                    value = (
                        math.log(float(particle.eta[node]))
                        + math.log(float(candidate.prior))
                        + bulk_log_likelihood_for_candidate(site, float(clone_phi), candidate)
                    )
                    components.append((node, multiplicity_index[candidate.multiplicity], value))
            normalizer = _logsumexp(np.asarray([item[2] for item in components], dtype=float))
            for node, multiplicity_index_value, value in components:
                responsibility = math.exp(value - normalizer) / len(particles)
                assignment[site_index, node] += responsibility
                posterior[site_index, multiplicity_index_value] += responsibility
    return assignment, posterior


def _representative(
    data: ModelData,
    particles: list[_Particle],
    assignment: np.ndarray,
) -> dict[str, Any]:
    topology = _particle_count_by_topology(particles).most_common(1)[0][0]
    candidates = [particle for particle in particles if tuple(particle.parents) == topology]
    median_phi = np.median(np.asarray([_phi(p.parents, p.eta) for p in particles]), axis=0)
    representative_particle = min(
        candidates,
        key=lambda particle: float(np.abs(_phi(particle.parents, particle.eta) - median_phi).sum()),
    )
    map_assignments = {
        site.mutation_id: {
            "node": f"clone_{int(np.argmax(assignment[index])) + 1}",
            "probability": float(np.max(assignment[index])),
        }
        for index, site in enumerate(data.sites)
    }
    selected_edges = [
        {
            "parent": "tumor_root" if int(parent) == -1 else f"clone_{int(parent) + 1}",
            "child": f"clone_{child + 1}",
        }
        for child, parent in enumerate(representative_particle.parents)
    ]
    return {
        "model": "finite_K_rao_blackwellized_smc_target",
        "algorithm": INFERENCE_ALGORITHM_ID,
        "posterior_status": "diagnostic_only",
        "root": "tumor_root",
        "root_semantics": "structural_root_with_frequency_one; eta_contains_clone_masses_only",
        "selected_edges": selected_edges,
        "best_sample": _sample_record(representative_particle, -1),
        "posterior_map_assignments": map_assignments,
    }


def _multiplicity_tsv(data: ModelData, posterior: np.ndarray) -> str:
    supports = tuple(sorted({m for site in data.sites for m in site.multiplicities}))
    lines = ["mutation_id\tmultiplicity\tprior\tposterior_mean"]
    for site_index, site in enumerate(data.sites):
        prior_by_m: dict[float, float] = {}
        for candidate in site.genotype_candidates:
            prior_by_m[candidate.multiplicity] = (
                prior_by_m.get(candidate.multiplicity, 0.0) + candidate.prior
            )
        for multiplicity in sorted(prior_by_m):
            index = supports.index(multiplicity)
            lines.append(
                f"{site.mutation_id}\t{multiplicity:.17g}\t{prior_by_m[multiplicity]:.17g}\t{posterior[site_index, index]:.17g}"
            )
    return "\n".join(lines) + "\n"


def _validate_completed_output(output_path: Path) -> int:
    missing = [name for name in SMC_ARTIFACTS if not (output_path / name).is_file()]
    if missing:
        raise RuntimeError("completed SMC repeat is missing artifacts: " + ", ".join(missing))
    payload = json.loads((output_path / "diagnostics.json").read_text(encoding="utf-8"))
    if payload.get("algorithm") != INFERENCE_ALGORITHM_ID or payload.get("sample_kind") != SMC_SAMPLE_KIND:
        raise RuntimeError("completed output is not an rao_blackwellized_annealed_smc artifact")
    count = payload.get("posterior_samples")
    if not isinstance(count, int) or count <= 0:
        raise RuntimeError("completed SMC diagnostics has invalid posterior_samples")
    return count


def run_smc(
    *,
    integrated_input: Path,
    outdir: Path,
    config: SMCConfig,
    algorithm: str = INFERENCE_ALGORITHM_ID,
    exclude_ids: frozenset[str] = frozenset(),
    repeat_index: int = 1,
    resume: bool = False,
) -> SMCResult:
    """Run one independent SMC repeat and publish the stable artifact set."""

    config.validate()
    if algorithm != INFERENCE_ALGORITHM_ID:
        raise ValueError(f"SMC adapter only supports algorithm={INFERENCE_ALGORITHM_ID!r}")
    input_path = Path(integrated_input).resolve()
    output_path = Path(outdir).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"canonical integrated input does not exist: {input_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    complete = output_path / "smc_complete.json"
    if resume and complete.is_file():
        posterior_samples = _validate_completed_output(output_path)
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
            resumed=True,
        )
    existing = [path for path in output_path.iterdir() if path.name != ".holdout.ids"]
    if existing:
        raise RuntimeError(f"SMC output directory is not empty: {output_path}")

    data = load_model_table(input_path, config.ascat_purity, exclude_ids=exclude_ids)
    compiled = compile_model(data)
    rng = np.random.default_rng(config.seed)
    particles = [
        _Particle(
            parents=_random_tree(rng, config.num_nodes),
            eta=rng.dirichlet(np.ones(config.num_nodes, dtype=float)),
            log_likelihood=0.0,
        )
        for _ in range(config.particles)
    ]
    for particle in particles:
        particle.log_prior = _tree_log_prior(particle.parents)
        particle.log_likelihood = _score(compiled, particle.parents, particle.eta)

    beta = 0.0
    log_normalizer = 0.0
    log_weights = np.full(config.particles, -math.log(config.particles), dtype=float)
    history: list[dict[str, Any]] = []
    stage_diagnostics: list[dict[str, Any]] = []
    while beta < 1.0 - 1e-12:
        if len(stage_diagnostics) >= config.max_annealing_stages:
            raise RuntimeError("SMC did not reach beta=1 within max_annealing_stages")
        old_beta = beta
        log_likelihood = np.asarray([particle.log_likelihood for particle in particles], dtype=float)
        beta, conditional_ess = _next_beta(beta, log_likelihood, config.conditional_ess_target)
        delta_beta = beta - old_beta
        previous_log_weights = log_weights.copy()
        incremental = previous_log_weights + delta_beta * log_likelihood
        incremental_log_normalizer = _logsumexp(incremental)
        log_normalizer += incremental_log_normalizer
        log_weights = incremental - incremental_log_normalizer
        weighted_ess = _weighted_ess(log_weights)
        resampled = weighted_ess / config.particles < config.resample_ess_threshold or beta >= 1.0 - 1e-12
        ancestor_diversity = 1.0
        if resampled:
            weights = np.exp(log_weights)
            indices = _systematic_indices(weights, rng)
            ancestor_diversity = len(set(int(index) for index in indices)) / config.particles
            particles = _copy_particles(particles, indices)
            log_weights = np.full(config.particles, -math.log(config.particles), dtype=float)
        rejuvenation = _rejuvenate(
            particles,
            compiled=compiled,
            beta=beta,
            config=config,
            rng=rng,
        )
        diversity = _particle_diversity(particles)
        stage = {
            "stage": len(stage_diagnostics) + 1,
            "beta_before": old_beta,
            "beta_after": beta,
            "delta_beta": delta_beta,
            "conditional_ess": conditional_ess,
            "conditional_ess_fraction": conditional_ess / config.particles,
            "weighted_particle_ess": weighted_ess,
            "weighted_particle_ess_fraction": weighted_ess / config.particles,
            "resampled": resampled,
            "ancestor_diversity": ancestor_diversity,
            "particle_diversity": diversity,
            "log_normalizer_increment": incremental_log_normalizer,
            "log_normalizer_estimate": log_normalizer,
            "rejuvenation": rejuvenation,
        }
        stage_diagnostics.append(stage)
        history.append(
            {
                "stage": stage["stage"],
                "beta": beta,
                "particle_count": config.particles,
                "particle_diversity": diversity,
                "ancestor_diversity": ancestor_diversity,
                "resampled": resampled,
                "rejuvenation": rejuvenation,
            }
        )

    # The output contract is an equal-weight posterior particle sample.  A
    # final systematic resample makes that semantics explicit even when the
    # final annealing step did not trigger the diversity threshold.
    final_weights = np.exp(log_weights - _logsumexp(log_weights))
    final_indices = _systematic_indices(final_weights, rng)
    final_ancestor_diversity = len(set(int(index) for index in final_indices)) / config.particles
    particles = _copy_particles(particles, final_indices)
    samples = [_sample_record(particle, index) for index, particle in enumerate(particles)]
    assignment, multiplicity = _responsibilities(data, particles)
    representative = _representative(data, particles, assignment)
    final_stage = stage_diagnostics[-1]
    posterior_diagnostics = {
        "model": "finite_K_rao_blackwellized_smc_target",
        "algorithm": INFERENCE_ALGORITHM_ID,
        "sample_kind": SMC_SAMPLE_KIND,
        "input_schema": "hcc1395_tumor_tree_input/v4",
        "input_sha256": sha256_file(input_path),
        "observed_sites": len(data.sites),
        "excluded_sites": len(exclude_ids),
        "posterior_samples": len(samples),
        "repeat_index": repeat_index,
        "resumed": False,
        "state_variables": ["parents", "eta"],
        "rao_blackwellized_variables": ["assignment", "multiplicity"],
        "target": {
            "tree_prior": "finite_K_single_founder_uniform_parent_prior",
            "eta_prior": "Dirichlet_alpha_one",
            "tempering": "likelihood_only_beta_0_to_1",
            "site_terms": "phyclone_xi_v1_CN_timing_joint_multiplicity_marginalized",
        },
        "vaf_formula": "phyclone_xi_v1",
        "vaf_implementation_status": "synced",
        "error_rate": 1e-3,
        "error_rate_status": "configured",
        "normal_cn_assumption": 2.0,
        "cn_timing_model": "explicit",
        "cn_timing_model_detail": "major_cn_pre_or_post_candidate",
        "tree_constraint": "exactly_one_tumor_founder_under_structural_root",
        "eta_semantics": "simplex_of_local_clone_masses; phi_is_descendant_sum",
        "purity_role": "ASCAT_purity_in_observation_emission",
        "hp_role": "loaded_and_conservation_checked_only; reserved_for_Model_B",
        "multiplicity_role": "Rao_Blackwellized_joint_responsibility; not_a_table_column",
        "config": dataclasses.asdict(config),
        "annealing": {
            "stage_count": len(stage_diagnostics),
            "stages": stage_diagnostics,
            "final_beta": beta,
            "final_log_normalizer_estimate": log_normalizer,
        },
        "weighted_particle_ess_fraction": final_stage["weighted_particle_ess_fraction"],
        "conditional_ess_fraction": min(
            stage["conditional_ess_fraction"] for stage in stage_diagnostics
        ),
        "particle_diversity": _particle_diversity(particles),
        "ancestor_diversity": final_ancestor_diversity,
        "resampling_count": sum(bool(stage["resampled"]) for stage in stage_diagnostics),
        "eta_acceptance": float(np.mean([stage["rejuvenation"]["eta_acceptance"] for stage in stage_diagnostics])),
        "topology_acceptance": float(np.mean([stage["rejuvenation"]["topology_acceptance"] for stage in stage_diagnostics])),
        "topology_change_rate": float(np.mean([stage["rejuvenation"]["topology_change_rate"] for stage in stage_diagnostics])),
        "rejuvenation_sweeps": [stage["rejuvenation"]["sweeps"] for stage in stage_diagnostics],
        "particle_history_artifact": "particle_history.jsonl.gz",
        "posterior_summary_artifact": "posterior_summary.tsv.gz",
        "topology_summary_artifact": "topology_summary.tsv",
        "multiplicity_posterior_artifact": "multiplicity_posterior.tsv.gz",
        "diagnostics_contract": "smc_particle_diagnostics_v1",
        "gate_semantics": "particle_ESS_diversity_annealing_rejuvenation_repeat_stability_predictive; no_R_hat_or_chain_ESS",
    }
    _atomic_gzip_text(output_path / "samples.jsonl.gz", "".join(_json_line(sample) for sample in samples))
    _atomic_gzip_text(output_path / "particle_history.jsonl.gz", "".join(_json_line(item) for item in history))
    _atomic_gzip_text(output_path / "multiplicity_posterior.tsv.gz", _multiplicity_tsv(data, multiplicity))
    _atomic_gzip_text(output_path / "posterior_summary.tsv.gz", _summary_tsv(particles))
    _atomic_text(output_path / "topology_summary.tsv", _topology_tsv(particles))
    _atomic_text(output_path / "diagnostics.json", json.dumps(posterior_diagnostics, indent=2, sort_keys=True, allow_nan=False) + "\n")
    _atomic_text(output_path / "representative_tree.json", json.dumps(representative, indent=2, sort_keys=True, allow_nan=False) + "\n")
    checkpoint = {
        "status": "complete",
        "algorithm": INFERENCE_ALGORITHM_ID,
        "sample_kind": SMC_SAMPLE_KIND,
        "input_sha256": sha256_file(input_path),
        "config": dataclasses.asdict(config),
        "completed_stage": len(stage_diagnostics),
        "beta": beta,
        "log_normalizer_estimate": log_normalizer,
        "particle_semantics": "equal_weight_final_posterior_particles",
        "particles": samples,
    }
    checkpoint_payload = gzip.compress(
        (json.dumps(checkpoint, sort_keys=True, allow_nan=False) + "\n").encode("utf-8"),
        compresslevel=6,
        mtime=0,
    )
    _atomic_write(output_path / "checkpoint.json.gz", checkpoint_payload)
    _atomic_text(
        output_path / "smc_complete.json",
        json.dumps(
            {
                "status": "complete",
                "algorithm": INFERENCE_ALGORITHM_ID,
                "sample_kind": SMC_SAMPLE_KIND,
                "input_sha256": sha256_file(input_path),
                "posterior_samples": len(samples),
                "artifacts": list(SMC_ARTIFACTS[:-1]),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
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
        posterior_samples=len(samples),
        resumed=False,
    )
