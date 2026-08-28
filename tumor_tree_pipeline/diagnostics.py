"""Fail-closed diagnostics for the annealed SMC tumor-tree inference.

This module checks particle effective sample size, particle/ancestor diversity,
repeat stability and strict holdout prediction.  It never interprets weighted
particles as independent posterior draws and never applies MCMC convergence statistics.
"""

from __future__ import annotations

import math
import gzip
import json
from collections.abc import Mapping, Sequence
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    from scipy.special import logsumexp as scipy_logsumexp
except ImportError as exc:  # pragma: no cover - production fail-closed guard
    raise RuntimeError(
        "tumor_tree_pipeline diagnostics require the local SciPy installation; "
        "no approximate or network-installed fallback is allowed"
    ) from exc

from .contracts import GateThresholds


class DiagnosticError(ValueError):
    """Raised when samples cannot support a requested formal diagnostic."""


def _assignment_pair_agreement(left: Sequence[Any], right: Sequence[Any]) -> float:
    if len(left) != len(right) or not left:
        raise DiagnosticError("assignment maps must be non-empty and have equal site counts")
    left_labels = sorted(set(left), key=str)
    right_labels = sorted(set(right), key=str)
    confusion = np.zeros((len(left_labels), len(right_labels)), dtype=np.int64)
    left_index = {label: index for index, label in enumerate(left_labels)}
    right_index = {label: index for index, label in enumerate(right_labels)}
    for left_label, right_label in zip(left, right):
        confusion[left_index[left_label], right_index[right_label]] += 1
    rows, columns = linear_sum_assignment(-confusion)
    return float(confusion[rows, columns].sum() / len(left))


def minimum_assignment_agreement(assignment_maps: Sequence[Sequence[Any]]) -> float:
    if len(assignment_maps) < 2:
        raise DiagnosticError("assignment agreement requires at least two independent repeats")
    return min(
        _assignment_pair_agreement(assignment_maps[left], assignment_maps[right])
        for left, right in combinations(range(len(assignment_maps)), 2)
    )


def _edge_set(draw: Any) -> frozenset[tuple[str, str]]:
    if isinstance(draw, Mapping):
        return frozenset((str(parent), str(child)) for child, parent in draw.items())
    try:
        return frozenset((str(parent), str(child)) for parent, child in draw)
    except (TypeError, ValueError) as exc:
        raise DiagnosticError("edge draws must be parent mappings or (parent, child) pairs") from exc


def maximum_edge_support_difference(edge_draws: Sequence[Sequence[Any]]) -> float:
    if len(edge_draws) < 2 or any(not draws for draws in edge_draws):
        raise DiagnosticError("edge-support comparison requires non-empty draws from two independent repeats")
    normalized = [[_edge_set(draw) for draw in repeat] for repeat in edge_draws]
    all_edges = set().union(*(set().union(*repeat) for repeat in normalized))
    supports = [
        {edge: sum(edge in draw for draw in repeat) / len(repeat) for edge in all_edges}
        for repeat in normalized
    ]
    if not all_edges:
        return 0.0
    return max(
        abs(supports[left][edge] - supports[right][edge])
        for left, right in combinations(range(len(supports)), 2)
        for edge in all_edges
    )


def strict_holdout_predictive_metrics(
    table_path: Path,
    samples: Sequence[Mapping[str, Any]],
    holdout_ids: frozenset[str],
    purity: float,
) -> dict[str, float]:
    """Score sites excluded from fitting under the posterior clone mixture.

    The strict score uses the Model A bulk/CN/purity/multiplicity emission.
    HP counts are retained in the canonical table and validated by the loader,
    but are not used by this predictive score. Coverage is the central 90%
    interval of the posterior VAF mixture, using the sampler's local clone
    masses when present. Holdout prediction starts from the CN-constrained
    candidate prior because holdout sites are excluded from fitting;
    fitted-site multiplicity responsibilities are emitted separately by the
    C++ sampler.
    """

    from .model import (
        ModelData,
        compile_model,
        expected_alt_probability_for_candidate,
        load_model_table,
    )

    if not samples or not holdout_ids:
        raise DiagnosticError("strict holdout scoring requires posterior samples and holdout IDs")
    all_data = load_model_table(Path(table_path), purity)
    sites = tuple(site for site in all_data.sites if site.mutation_id in holdout_ids)
    if not sites:
        raise DiagnosticError("none of the requested strict holdout IDs are eligible model sites")
    data = ModelData(sites=sites, purity=purity)
    compiled = compile_model(data)
    sample_scores: list[np.ndarray] = []
    phi_draws: list[np.ndarray] = []
    weight_draws: list[np.ndarray] = []
    for sample in samples:
        phi = np.asarray(sample["phi"], dtype=float)
        occupancy = np.asarray(sample["occupancy"], dtype=float)
        if phi.ndim != 1 or occupancy.shape != phi.shape:
            raise DiagnosticError("sample phi/occupancy dimensions are inconsistent")
        local_mass = sample.get("eta")
        if local_mass is not None:
            weights = np.asarray(local_mass, dtype=float)
            if weights.shape != phi.shape or not np.isfinite(weights).all() or np.any(weights <= 0.0):
                raise DiagnosticError("sample eta/phi dimensions or positivity are inconsistent")
        else:
            raise DiagnosticError("sample is missing eta; legacy occupancy-only artifacts are unsupported")
        weights /= weights.sum()
        # ``CompiledModel.likelihood_matrix`` is the single Model A scoring
        # path, so strict holdout cannot accidentally introduce an unvalidated
        # HP likelihood term.
        matrix = compiled.likelihood_matrix(phi)
        sample_scores.append(scipy_logsumexp(matrix + np.log(weights)[None, :], axis=1))
        phi_draws.append(phi)
        weight_draws.append(weights)
    stacked_scores = np.stack(sample_scores)
    site_log_scores = scipy_logsumexp(stacked_scores, axis=0) - math.log(len(samples))

    covered = 0
    for site in sites:
        values: list[float] = []
        weights: list[float] = []
        for phi, clone_weights in zip(phi_draws, weight_draws):
            for clone_phi, clone_weight in zip(phi, clone_weights):
                for candidate in site.genotype_candidates:
                    values.append(
                        expected_alt_probability_for_candidate(
                            site, float(clone_phi), candidate
                        )
                    )
                    weights.append(
                        float(clone_weight * candidate.prior / len(phi_draws))
                    )
        order = np.argsort(values)
        ordered_values = np.asarray(values, dtype=float)[order]
        ordered_weights = np.asarray(weights, dtype=float)[order]
        cumulative = np.cumsum(ordered_weights)
        cumulative /= cumulative[-1]
        low = float(ordered_values[np.searchsorted(cumulative, 0.05, side="left")])
        high = float(ordered_values[np.searchsorted(cumulative, 0.95, side="left")])
        observed = site.alt_reads / site.total_reads
        covered += int(low <= observed <= high)
    return {
        "predictive_coverage": covered / len(sites),
        "predictive_log_score": float(np.mean(site_log_scores)),
    }


def _smc_edge_draw(sample: Mapping[str, Any]) -> list[tuple[str, str]]:
    parents = [int(parent) for parent in sample.get("parents", ())]
    if len(parents) < 2 or parents.count(-1) != 1:
        raise DiagnosticError("SMC particle has an invalid single-founder topology")
    for child, parent in enumerate(parents):
        if parent != -1 and (not 0 <= parent < len(parents) or parent == child):
            raise DiagnosticError("SMC particle has an invalid parent index")
        seen = {child}
        cursor = parent
        while cursor != -1:
            if cursor in seen:
                raise DiagnosticError("SMC particle topology contains a cycle")
            seen.add(cursor)
            cursor = parents[cursor]
    return [
        (
            "tumor_root" if parent == -1 else f"clone_{parent + 1}",
            f"clone_{child + 1}",
        )
        for child, parent in enumerate(parents)
    ]


def smc_artifact_payload(
    *,
    samples_path: Path,
    representative_tree_path: Path,
    diagnostics_path: Path,
    table_path: Path,
    holdout_ids: frozenset[str],
    purity: float,
) -> dict[str, Any]:
    """Adapt one SMC repeat to the run-level SMC diagnostics contract."""

    with gzip.open(samples_path, "rt", encoding="utf-8") as handle:
        samples = [json.loads(line) for line in handle if line.strip()]
    if not samples:
        raise DiagnosticError(f"SMC backend produced no posterior particles: {samples_path}")
    if any(sample.get("sample_kind") != "smc_particle" for sample in samples):
        raise DiagnosticError("SMC samples must be explicitly tagged sample_kind=smc_particle")
    diagnostic_payload = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    if diagnostic_payload.get("algorithm") != "rao_blackwellized_annealed_smc":
        raise DiagnosticError("repeat diagnostics do not identify rao_blackwellized_annealed_smc")
    if diagnostic_payload.get("sample_semantics") != "smc_particle":
        raise DiagnosticError("repeat diagnostics do not identify smc_particle artifacts")
    representative = json.loads(representative_tree_path.read_text(encoding="utf-8"))
    assignment_mapping = representative.get("posterior_map_assignments", {})
    if not assignment_mapping:
        raise DiagnosticError("SMC representative tree lacks posterior_map_assignments")
    assignment_map = [
        assignment_mapping[mutation_id]["node"]
        for mutation_id in sorted(assignment_mapping)
    ]
    predictive = strict_holdout_predictive_metrics(
        table_path,
        samples,
        holdout_ids,
        purity,
    )
    return {
        "sample_kind": "smc_particle",
        "prevalence_draws": [sample["phi"] for sample in samples],
        "assignment_map": assignment_map,
        "edge_draws": [_smc_edge_draw(sample) for sample in samples],
        "smc_diagnostics": diagnostic_payload,
        **predictive,
    }


def _pairwise_ccf_stability(prevalence: Sequence[np.ndarray]) -> float:
    if len(prevalence) < 2:
        raise DiagnosticError("SMC repeat stability requires at least two independent repeats")
    means = [np.mean(np.sort(values, axis=1)[:, ::-1], axis=0) for values in prevalence]
    distances = [
        float(np.mean(np.abs(means[left] - means[right])))
        for left, right in combinations(range(len(means)), 2)
    ]
    return max(0.0, min(1.0, 1.0 - max(distances)))


def summarize_smc_repeats(
    repeat_results: Sequence[Mapping[str, Any]],
    *,
    allow_single_repeat: bool = False,
) -> dict[str, Any]:
    """Summarize SMC repeats without MCMC chain diagnostics.

    A quick pilot may intentionally contain one repeat to measure the full
    data path.  In that mode per-repeat SMC diagnostics are still reported,
    while repeat-to-repeat stability metrics are explicitly marked as not
    evaluated.  Normal pilot and formal callers keep the strict two-repeat
    contract by leaving ``allow_single_repeat`` false.
    """

    if not repeat_results:
        raise DiagnosticError("SMC diagnostics require at least one independent repeat")
    if len(repeat_results) < 2 and not allow_single_repeat:
        raise DiagnosticError("SMC diagnostics require at least two independent repeats")
    prevalence = [np.asarray(result["prevalence_draws"], dtype=float) for result in repeat_results]
    if any(values.ndim != 2 or values.shape[1] == 0 for values in prevalence):
        raise DiagnosticError("SMC prevalence_draws must be non-empty particle-by-K matrices")
    node_count = prevalence[0].shape[1]
    if any(values.shape[1] != node_count for values in prevalence):
        raise DiagnosticError("all SMC repeats must have the same fixed K")
    smc_payloads = [result.get("smc_diagnostics") for result in repeat_results]
    if any(not isinstance(payload, Mapping) for payload in smc_payloads):
        raise DiagnosticError("each SMC repeat must include its diagnostics payload")

    metric_names = (
        "conditional_ess_fraction",
        "weighted_particle_ess_fraction",
        "particle_diversity",
        "ancestor_diversity",
        "eta_acceptance",
        "topology_acceptance",
        "topology_change_rate",
    )
    repeat_metrics = []
    for payload in smc_payloads:
        assert isinstance(payload, Mapping)
        if payload.get("algorithm") != "rao_blackwellized_annealed_smc":
            raise DiagnosticError("all repeat diagnostics must use the active SMC algorithm")
        if float(payload.get("annealing", {}).get("final_beta", -1.0)) < 1.0 - 1e-12:
            raise DiagnosticError("SMC repeat did not reach beta=1")
        repeat_metrics.append(
            {
                name: float(payload[name])
                for name in metric_names
            }
            | {
                "resampling_count": int(payload.get("resampling_count", 0)),
                "rejuvenation_sweeps": list(payload.get("rejuvenation_sweeps", [])),
            }
        )
    coverages = [float(result["predictive_coverage"]) for result in repeat_results]
    log_scores = [float(result["predictive_log_score"]) for result in repeat_results]
    if not np.isfinite(coverages).all() or not np.isfinite(log_scores).all():
        raise DiagnosticError("SMC holdout coverage and log scores must be finite")
    repeat_stability_evaluated = len(repeat_results) >= 2
    if repeat_stability_evaluated:
        ccf_stability: float | None = _pairwise_ccf_stability(prevalence)
        min_assignment_agreement: float | None = minimum_assignment_agreement(
            [list(result["assignment_map"]) for result in repeat_results]
        )
        max_edge_support_difference: float | None = maximum_edge_support_difference(
            [list(result["edge_draws"]) for result in repeat_results]
        )
    else:
        ccf_stability = None
        min_assignment_agreement = None
        max_edge_support_difference = None
    return {
        "repeat_count": len(repeat_results),
        "repeat_stability_evaluated": repeat_stability_evaluated,
        "finite_k": node_count,
        "repeat_metrics": repeat_metrics,
        "min_conditional_ess_fraction": min(item["conditional_ess_fraction"] for item in repeat_metrics),
        "min_weighted_particle_ess_fraction": min(item["weighted_particle_ess_fraction"] for item in repeat_metrics),
        "min_particle_diversity": min(item["particle_diversity"] for item in repeat_metrics),
        "min_ancestor_diversity": min(item["ancestor_diversity"] for item in repeat_metrics),
        "min_eta_acceptance": min(item["eta_acceptance"] for item in repeat_metrics),
        "min_topology_acceptance": min(item["topology_acceptance"] for item in repeat_metrics),
        "ccf_stability": ccf_stability,
        "min_assignment_agreement": min_assignment_agreement,
        "max_edge_support_difference": max_edge_support_difference,
        "predictive_coverage_by_repeat": coverages,
        "predictive_log_score_by_repeat": log_scores,
        "min_predictive_log_score": min(log_scores),
        "implementation": "SMC conditional ESS, weighted particle ESS, diversity, annealing, rejuvenation, and repeat stability",
        "smc_particle_gate": True,
    }


def evaluate_smc_gates(
    diagnostics: Mapping[str, Any],
    thresholds: Any,
    *,
    min_predictive_log_score: float,
) -> dict[str, Any]:
    """Evaluate formal particle and repeat gates."""

    thresholds.validate()
    checks = {
        "conditional_ess": float(diagnostics["min_conditional_ess_fraction"])
        >= thresholds.min_conditional_ess_fraction,
        "weighted_particle_ess": float(diagnostics["min_weighted_particle_ess_fraction"])
        >= thresholds.min_weighted_particle_ess_fraction,
        "particle_diversity": float(diagnostics["min_particle_diversity"])
        >= thresholds.min_particle_diversity,
        "ancestor_diversity": float(diagnostics["min_ancestor_diversity"])
        >= thresholds.min_ancestor_diversity,
        "ccf_stability": float(diagnostics["ccf_stability"]) >= thresholds.min_ccf_stability,
        "assignment_agreement": float(diagnostics["min_assignment_agreement"])
        >= thresholds.min_assignment_agreement,
        "edge_support": float(diagnostics["max_edge_support_difference"])
        <= thresholds.max_edge_support_difference,
        "predictive_coverage": all(
            thresholds.min_predictive_coverage <= float(value) <= thresholds.max_predictive_coverage
            for value in diagnostics["predictive_coverage_by_repeat"]
        ),
        "predictive_log_score": float(diagnostics["min_predictive_log_score"])
        >= min_predictive_log_score,
    }
    finite_keys = {
        "min_conditional_ess_fraction",
        "min_weighted_particle_ess_fraction",
        "min_particle_diversity",
        "min_ancestor_diversity",
        "ccf_stability",
        "min_assignment_agreement",
        "max_edge_support_difference",
        "min_predictive_log_score",
    }
    checks["finite_metrics"] = all(
        math.isfinite(float(diagnostics[key])) for key in finite_keys if key in diagnostics
    ) and diagnostics.get("algorithm", "rao_blackwellized_annealed_smc") == "rao_blackwellized_annealed_smc"
    return {"passed": all(checks.values()), "checks": checks, "contract": "smc_gates_v1"}


def pilot_smc_report(diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    """Report pilot particle diagnostics without treating them as convergence gates."""

    report = {
        "pilot_particle_diversity": float(diagnostics["min_particle_diversity"]),
        "pilot_ancestor_diversity": float(diagnostics["min_ancestor_diversity"]),
        "formal_gate_not_evaluated": True,
        "smc_particle_gate": True,
    }
    if diagnostics.get("repeat_stability_evaluated") is True:
        report["pilot_ccf_stability"] = float(diagnostics["ccf_stability"])
    else:
        report["pilot_repeat_stability"] = "not_evaluated_single_repeat"
    return report
