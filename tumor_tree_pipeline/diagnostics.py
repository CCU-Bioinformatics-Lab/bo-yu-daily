"""Fail-closed multi-chain diagnostics for finite-K tumor-tree inference.

The implementation intentionally depends only on NumPy and SciPy.  It follows
the rank-normalized split/folded R-hat and rank-based bulk/tail ESS definitions
used by modern MCMC practice closely enough to enforce the pipeline contract;
it does not silently fall back to the legacy, unranked diagnostic.
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
    from scipy.stats import norm, rankdata
except ImportError as exc:  # pragma: no cover - production fail-closed guard
    raise RuntimeError(
        "tumor_tree_pipeline diagnostics require the local SciPy installation; "
        "no approximate or network-installed fallback is allowed"
    ) from exc

from .contracts import GateThresholds


class DiagnosticError(ValueError):
    """Raised when samples cannot support a requested formal diagnostic."""


def _equal_chains(chains: Sequence[Sequence[float]], *, minimum_draws: int = 8) -> np.ndarray:
    if len(chains) < 2:
        raise DiagnosticError("at least two independent chains are required")
    arrays = [np.asarray(chain, dtype=float).reshape(-1) for chain in chains]
    draw_count = min((array.size for array in arrays), default=0)
    if draw_count < minimum_draws:
        raise DiagnosticError(
            f"at least {minimum_draws} retained draws per chain are required; got {draw_count}"
        )
    values = np.stack([array[-draw_count:] for array in arrays])
    if not np.isfinite(values).all():
        raise DiagnosticError("diagnostic samples contain NaN or infinite values")
    return values


def _split_chains(chains: Sequence[Sequence[float]]) -> np.ndarray:
    values = _equal_chains(chains)
    half = values.shape[1] // 2
    if half < 4:
        raise DiagnosticError("split diagnostics require at least four draws per half-chain")
    return np.concatenate((values[:, :half], values[:, -half:]), axis=0)


def _rank_normalize(values: np.ndarray) -> np.ndarray:
    flat = np.asarray(values, dtype=float).reshape(-1)
    ranks = rankdata(flat, method="average")
    probabilities = (ranks - 3.0 / 8.0) / (flat.size + 1.0 / 4.0)
    normalized = norm.ppf(probabilities)
    return normalized.reshape(values.shape)


def _basic_rhat(values: np.ndarray) -> float:
    chain_count, draw_count = values.shape
    if chain_count < 2 or draw_count < 2:
        raise DiagnosticError("R-hat requires at least two chains and two draws")
    chain_variances = np.var(values, axis=1, ddof=1)
    within = float(np.mean(chain_variances))
    between = float(draw_count * np.var(np.mean(values, axis=1), ddof=1))
    if not math.isfinite(within) or within <= np.finfo(float).eps:
        return math.inf
    variance_plus = ((draw_count - 1.0) / draw_count) * within + between / draw_count
    return max(1.0, math.sqrt(max(0.0, variance_plus / within)))


def rank_normalized_split_folded_rhat(chains: Sequence[Sequence[float]]) -> dict[str, float]:
    """Return rank-normalized split and folded R-hat.

    A constant or otherwise degenerate trace returns infinite R-hat.  Treating
    such a trace as converged would violate the formal fail-closed contract.
    """

    split = _split_chains(chains)
    rank_rhat = _basic_rhat(_rank_normalize(split))
    folded = np.abs(split - np.median(split))
    folded_rhat = _basic_rhat(_rank_normalize(folded))
    return {
        "rank_normalized_split_rhat": rank_rhat,
        "folded_rhat": folded_rhat,
        "max_rhat": max(rank_rhat, folded_rhat),
    }


def _autocovariance(values: np.ndarray, lag: int) -> float:
    centered = values - np.mean(values)
    if lag == 0:
        return float(np.dot(centered, centered) / values.size)
    return float(np.dot(centered[:-lag], centered[lag:]) / values.size)


def _multi_chain_ess(values: np.ndarray) -> float:
    """Estimate total ESS with Geyer's initial-positive monotone sequence."""

    chain_count, draw_count = values.shape
    autocovariances = np.asarray(
        [[_autocovariance(chain, lag) for lag in range(draw_count)] for chain in values],
        dtype=float,
    )
    within = float(np.mean(autocovariances[:, 0]))
    between = float(draw_count * np.var(np.mean(values, axis=1), ddof=1))
    variance_plus = ((draw_count - 1.0) / draw_count) * within + between / draw_count
    if not math.isfinite(variance_plus) or variance_plus <= np.finfo(float).eps:
        return 0.0

    rho = np.empty(draw_count, dtype=float)
    rho[0] = 1.0
    for lag in range(1, draw_count):
        rho[lag] = 1.0 - (within - float(np.mean(autocovariances[:, lag]))) / variance_plus

    pair_sums: list[float] = []
    for lag in range(0, draw_count - 1, 2):
        pair = float(rho[lag] + rho[lag + 1])
        if pair <= 0.0:
            break
        if pair_sums:
            pair = min(pair, pair_sums[-1])
        pair_sums.append(pair)
    if not pair_sums:
        return 0.0
    tau = max(1.0, -1.0 + 2.0 * sum(pair_sums))
    return float(min(chain_count * draw_count, chain_count * draw_count / tau))


def bulk_tail_ess(chains: Sequence[Sequence[float]]) -> dict[str, float]:
    """Return total rank-based bulk ESS and the minimum 5%/95% tail ESS."""

    split = _split_chains(chains)
    bulk = _multi_chain_ess(_rank_normalize(split))
    pooled = split.reshape(-1)
    low, high = np.quantile(pooled, (0.05, 0.95))
    low_indicator = (split <= low).astype(float)
    high_indicator = (split >= high).astype(float)
    tail = min(_multi_chain_ess(low_indicator), _multi_chain_ess(high_indicator))
    return {"bulk_ess_total": bulk, "tail_ess_total": tail}


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
        raise DiagnosticError("assignment agreement requires at least two chains")
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
        raise DiagnosticError("edge-support comparison requires non-empty draws from two chains")
    normalized = [[_edge_set(draw) for draw in chain] for chain in edge_draws]
    all_edges = set().union(*(set().union(*chain) for chain in normalized))
    supports = [
        {edge: sum(edge in draw for draw in chain) / len(chain) for edge in all_edges}
        for chain in normalized
    ]
    if not all_edges:
        return 0.0
    return max(
        abs(supports[left][edge] - supports[right][edge])
        for left, right in combinations(range(len(supports)), 2)
        for edge in all_edges
    )


def summarize_chains(chain_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Create formal diagnostics from the stable ``run_chain`` result payload."""

    if len(chain_results) < 2:
        raise DiagnosticError("multi-chain diagnostics require at least two chain results")
    prevalence = [np.asarray(result["prevalence_draws"], dtype=float) for result in chain_results]
    if any(draws.ndim != 2 or draws.shape[1] == 0 for draws in prevalence):
        raise DiagnosticError("prevalence_draws must be a non-empty draws-by-K matrix")
    node_count = prevalence[0].shape[1]
    if any(draws.shape[1] != node_count for draws in prevalence):
        raise DiagnosticError("all chains must have the same finite K")

    rank_metrics: dict[str, dict[str, float]] = {}
    for rank in range(node_count):
        series = [np.sort(draws, axis=1)[:, ::-1][:, rank] for draws in prevalence]
        metrics = rank_normalized_split_folded_rhat(series)
        metrics.update(bulk_tail_ess(series))
        rank_metrics[f"prevalence_rank_{rank + 1}"] = metrics

    assignment = minimum_assignment_agreement(
        [list(result["assignment_map"]) for result in chain_results]
    )
    edge_difference = maximum_edge_support_difference(
        [list(result["edge_draws"]) for result in chain_results]
    )
    coverages = [float(result["predictive_coverage"]) for result in chain_results]
    log_scores = [float(result["predictive_log_score"]) for result in chain_results]
    if not np.isfinite(coverages).all() or not np.isfinite(log_scores).all():
        raise DiagnosticError("holdout coverage and log scores must be finite")

    return {
        "chain_count": len(chain_results),
        "finite_k": node_count,
        "prevalence_ranks": rank_metrics,
        "max_rank_normalized_split_folded_rhat": max(
            metric["max_rhat"] for metric in rank_metrics.values()
        ),
        "min_bulk_ess_total": min(metric["bulk_ess_total"] for metric in rank_metrics.values()),
        "min_tail_ess_total": min(metric["tail_ess_total"] for metric in rank_metrics.values()),
        "min_assignment_agreement": assignment,
        "max_edge_support_difference": edge_difference,
        "predictive_coverage_by_chain": coverages,
        "predictive_log_score_by_chain": log_scores,
        "min_predictive_log_score": min(log_scores),
        "implementation": "numpy/scipy rank-normalized split/folded R-hat and rank ESS",
    }


def strict_holdout_predictive_metrics(
    table_path: Path,
    samples: Sequence[Mapping[str, Any]],
    holdout_ids: frozenset[str],
    purity: float,
) -> dict[str, float]:
    """Score sites excluded from fitting under the posterior clone mixture.

    The log score uses the complete bulk+conditional-HP emission.  Coverage is
    the legacy-compatible central 90% interval of the posterior VAF mixture,
    now using the CN-only multiplicity prior rather than a data-derived
    multiplicity posterior.
    """

    from .model import ModelData, compile_model, expected_alt_probability, load_model_table

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
        weights = occupancy + 1.0
        weights /= weights.sum()
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
                for multiplicity, multiplicity_weight in zip(
                    site.multiplicities, site.multiplicity_prior
                ):
                    values.append(expected_alt_probability(site, float(clone_phi), multiplicity))
                    weights.append(
                        float(clone_weight * multiplicity_weight / len(phi_draws))
                    )
        order = np.argsort(values)
        ordered_values = np.asarray(values, dtype=float)[order]
        ordered_weights = np.asarray(weights, dtype=float)[order]
        cumulative = np.cumsum(ordered_weights)
        cumulative /= cumulative[-1]
        low = float(ordered_values[np.searchsorted(cumulative, 0.05, side="left")])
        high = float(ordered_values[np.searchsorted(cumulative, 0.95, side="left")])
        observed = site.bulk_alt / site.bulk_depth
        covered += int(low <= observed <= high)
    return {
        "predictive_coverage": covered / len(sites),
        "predictive_log_score": float(np.mean(site_log_scores)),
    }


def sampler_artifact_payload(
    *,
    samples_path: Path,
    representative_tree_path: Path,
    table_path: Path,
    holdout_ids: frozenset[str],
    purity: float,
) -> dict[str, Any]:
    """Adapt stable sampler artifacts to :func:`summarize_chains` input."""

    with gzip.open(samples_path, "rt", encoding="utf-8") as handle:
        samples = [json.loads(line) for line in handle if line.strip()]
    if not samples:
        raise DiagnosticError(f"sampler produced no posterior samples: {samples_path}")
    representative = json.loads(representative_tree_path.read_text(encoding="utf-8"))
    assignment_mapping = representative.get("posterior_map_assignments", {})
    if not assignment_mapping:
        raise DiagnosticError("representative tree lacks posterior_map_assignments")
    assignment_map = [
        assignment_mapping[mutation_id]["node"]
        for mutation_id in sorted(assignment_mapping)
    ]
    edge_draws = []
    for sample in samples:
        parents = [int(parent) for parent in sample["parents"]]
        phi = [float(value) for value in sample["phi"]]
        children = [[] for _ in parents]
        for child, parent in enumerate(parents):
            if parent != -1:
                children[parent].append(child)

        def depth(node: int) -> int:
            observed = {node}
            value = 1
            parent = parents[node]
            while parent != -1:
                if parent in observed:
                    raise DiagnosticError("sampler emitted a cyclic topology")
                observed.add(parent)
                value += 1
                parent = parents[parent]
            return value

        order = sorted(
            range(len(parents)),
            key=lambda node: (-phi[node], depth(node), -len(children[node]), node),
        )
        rank = {node: f"node_{index + 1}" for index, node in enumerate(order)}
        edges = [
            (
                "tumor_root" if parent == -1 else rank[parent],
                rank[child],
            )
            for child, parent in enumerate(parents)
        ]
        edge_draws.append(edges)
    predictive = strict_holdout_predictive_metrics(
        table_path,
        samples,
        holdout_ids,
        purity,
    )
    return {
        "prevalence_draws": [sample["phi"] for sample in samples],
        "assignment_map": assignment_map,
        "edge_draws": edge_draws,
        **predictive,
    }


def evaluate_formal_gates(
    diagnostics: Mapping[str, Any],
    thresholds: GateThresholds,
    *,
    min_predictive_log_score: float,
) -> dict[str, Any]:
    """Evaluate every formal gate; missing or non-finite metrics fail."""

    thresholds.validate()
    checks = {
        "rhat": float(diagnostics["max_rank_normalized_split_folded_rhat"])
        < thresholds.max_rank_normalized_rhat,
        "bulk_ess": float(diagnostics["min_bulk_ess_total"]) >= thresholds.min_bulk_ess_total,
        "tail_ess": float(diagnostics["min_tail_ess_total"]) >= thresholds.min_tail_ess_total,
        "assignment_agreement": float(diagnostics["min_assignment_agreement"])
        >= thresholds.min_assignment_agreement,
        "edge_support": float(diagnostics["max_edge_support_difference"])
        <= thresholds.max_edge_support_difference,
        "predictive_coverage": all(
            thresholds.min_predictive_coverage <= float(value) <= thresholds.max_predictive_coverage
            for value in diagnostics["predictive_coverage_by_chain"]
        ),
        "predictive_log_score": float(diagnostics["min_predictive_log_score"])
        >= min_predictive_log_score,
    }
    finite = all(
        math.isfinite(float(value))
        for key, value in diagnostics.items()
        if key
        in {
            "max_rank_normalized_split_folded_rhat",
            "min_bulk_ess_total",
            "min_tail_ess_total",
            "min_assignment_agreement",
            "max_edge_support_difference",
            "min_predictive_log_score",
        }
    )
    checks["finite_metrics"] = finite
    return {"passed": all(checks.values()), "checks": checks}


def pilot_report(diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    """Report the agreed loose pilot signal without weakening formal gates."""

    rhat = float(diagnostics["max_rank_normalized_split_folded_rhat"])
    return {
        "pilot_rhat_threshold": 1.10,
        "pilot_rhat_report_pass": math.isfinite(rhat) and rhat <= 1.10,
        "formal_gate_not_evaluated": True,
    }
