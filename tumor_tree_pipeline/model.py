"""Canonical observation model for finite-K tumor-tree inference.

This module owns the narrow boundary between the versioned site table and the
sampler.  It deliberately has no legacy loader: malformed or incomplete
canonical input is an error.  The loader derives CN-constrained multiplicity
candidate support/prior from the canonical ASCAT major/minor CN fields instead
of accepting a precomputed multiplicity table column; the emission can then
return a posterior responsibility for each candidate.
"""

from __future__ import annotations

import csv
import gzip
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

from .contracts import MODEL_FORBIDDEN_COLUMNS, MODEL_REQUIRED_COLUMNS


DEFAULT_ERROR_RATE = 0.005


class CanonicalInputError(ValueError):
    """The canonical model table violates its versioned schema contract."""


@dataclass(frozen=True)
class SiteObservation:
    mutation_id: str
    chrom: str
    pos: int
    ref: str
    alt: str
    ref_reads: int
    alt_reads: int
    hp1_ref: int
    hp1_alt: int
    hp2_ref: int
    hp2_alt: int
    major_cn: float
    minor_cn: float
    total_cn: float
    purity: float
    multiplicities: tuple[float, ...]
    multiplicity_prior: tuple[float, ...]

    @property
    def total_reads(self) -> int:
        return self.ref_reads + self.alt_reads


@dataclass(frozen=True)
class ModelData:
    sites: tuple[SiteObservation, ...]
    purity: float

    @property
    def mutation_ids(self) -> tuple[str, ...]:
        return tuple(site.mutation_id for site in self.sites)


@dataclass(frozen=True)
class CompiledModel:
    """Vectorized form of :class:`ModelData` reused across MCMC proposals."""

    data: ModelData
    ref: np.ndarray
    alt: np.ndarray
    total_cn: np.ndarray
    hp1_ref: np.ndarray
    hp1_alt: np.ndarray
    hp2_ref: np.ndarray
    hp2_alt: np.ndarray
    multiplicities: np.ndarray
    log_prior: np.ndarray
    binomial_coefficient: np.ndarray
    alt_allocation_coefficient: np.ndarray
    ref_allocation_coefficient: np.ndarray

    def likelihood_matrix(self, phi_values: Sequence[float]) -> np.ndarray:
        """Evaluate all sites, clones, multiplicities, and HP-side states."""

        phi_values = np.asarray(phi_values, dtype=float)
        if phi_values.ndim != 1 or np.any(phi_values < 0.0) or np.any(phi_values > 1.0):
            raise ValueError("phi_values must be a one-dimensional vector in [0, 1]")
        n_sites = len(self.ref)
        result = np.empty((n_sites, len(phi_values)), dtype=float)
        ref = self.ref[:, None]
        alt = self.alt[:, None]
        total_cn = self.total_cn[:, None]
        multiplicities = self.multiplicities[None, :]
        purity = self.data.purity
        error = DEFAULT_ERROR_RATE
        denominator = (1.0 - purity) * 2.0 + purity * total_cn
        hp1_ref = self.hp1_ref[:, None]
        hp1_alt = self.hp1_alt[:, None]
        hp2_ref = self.hp2_ref[:, None]
        hp2_alt = self.hp2_alt[:, None]
        tagged = hp1_ref + hp1_alt + hp2_ref + hp2_alt
        has_hp = tagged[:, 0] > 0
        depth = ref + alt
        tag_fraction = np.clip(tagged / depth, 1e-9, 1.0 - 1e-9)
        half_tag = tag_fraction * 0.5
        untagged_fraction = 1.0 - tag_fraction
        untag_alt = alt - hp1_alt - hp2_alt
        untag_ref = ref - hp1_ref - hp2_ref
        q_ref = np.full((n_sites, len(self.multiplicities)), error, dtype=float)

        def allocation(
            hp1_q: np.ndarray, hp2_q: np.ndarray, q_bulk: np.ndarray
        ) -> np.ndarray:
            alt_weights = np.stack(
                [half_tag * hp1_q, half_tag * hp2_q, untagged_fraction * q_bulk], axis=2
            )
            ref_weights = np.stack(
                [half_tag * (1.0 - hp1_q), half_tag * (1.0 - hp2_q),
                 untagged_fraction * (1.0 - q_bulk)],
                axis=2,
            )
            alt_weights /= np.maximum(1e-300, alt_weights.sum(axis=2, keepdims=True))
            ref_weights /= np.maximum(1e-300, ref_weights.sum(axis=2, keepdims=True))
            alt_counts = np.stack(
                [np.broadcast_to(hp1_alt, q_bulk.shape),
                 np.broadcast_to(hp2_alt, q_bulk.shape),
                 np.broadcast_to(untag_alt, q_bulk.shape)],
                axis=2,
            )
            ref_counts = np.stack(
                [np.broadcast_to(hp1_ref, q_bulk.shape),
                 np.broadcast_to(hp2_ref, q_bulk.shape),
                 np.broadcast_to(untag_ref, q_bulk.shape)],
                axis=2,
            )
            value = (
                self.alt_allocation_coefficient[:, None]
                + np.sum(alt_counts * np.log(np.clip(alt_weights, 1e-300, 1.0)), axis=2)
                + self.ref_allocation_coefficient[:, None]
                + np.sum(ref_counts * np.log(np.clip(ref_weights, 1e-300, 1.0)), axis=2)
            )
            value[~has_hp, :] = 0.0
            return value

        for node_index, phi in enumerate(phi_values):
            cellular_fraction = purity * phi * multiplicities / denominator
            q_bulk = np.clip(error + (1.0 - 2.0 * error) * cellular_fraction, 1e-12, 1.0 - 1e-12)
            bulk = (
                self.binomial_coefficient[:, None]
                + alt * np.log(q_bulk)
                + ref * np.log1p(-q_bulk)
            )
            hp_side0 = allocation(q_bulk, q_ref, q_bulk)
            hp_side1 = allocation(q_ref, q_bulk, q_bulk)
            hp = np.logaddexp(math.log(0.5) + hp_side0, math.log(0.5) + hp_side1)
            components = self.log_prior + bulk + hp
            top = np.max(components, axis=1)
            result[:, node_index] = top + np.log(
                np.sum(np.exp(components - top[:, None]), axis=1)
            )
        return result


def _open_text(path: Path):
    return gzip.open(path, "rt", newline="") if path.suffix == ".gz" else path.open("r", newline="")


def _required_text(row: Mapping[str, str], key: str, mutation_id: str) -> str:
    value = str(row.get(key, "")).strip()
    if not value:
        raise CanonicalInputError(f"row {mutation_id!r} is missing {key}")
    return value


def _integer(row: Mapping[str, str], key: str, mutation_id: str) -> int:
    text = _required_text(row, key, mutation_id)
    try:
        value = int(text)
    except ValueError as exc:
        raise CanonicalInputError(f"row {mutation_id!r} has non-integer {key}={text!r}") from exc
    if value < 0:
        raise CanonicalInputError(f"row {mutation_id!r} has negative {key}={value}")
    return value


def _number(row: Mapping[str, str], key: str, mutation_id: str) -> float:
    text = _required_text(row, key, mutation_id)
    try:
        value = float(text)
    except ValueError as exc:
        raise CanonicalInputError(f"row {mutation_id!r} has non-numeric {key}={text!r}") from exc
    if not math.isfinite(value):
        raise CanonicalInputError(f"row {mutation_id!r} has non-finite {key}={text!r}")
    return value


def derive_cn_multiplicity_prior(
    major_cn: float, minor_cn: float, mutation_id: str = "<unknown>"
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Derive CN-constrained multiplicity candidates and initial prior.

    Each extant ASCAT homolog side receives equal total mass, then uniform
    mass over ``m=1..side_CN``.  Equal multiplicities are combined.  Thus
    major=3/minor=1 gives ``m=(1, 2, 3)`` and initial
    ``P=(2/3, 1/6, 1/6)``.  The final data-conditioned responsibility is
    returned by :func:`site_multiplicity_posterior`.
    """

    if (
        not math.isfinite(major_cn)
        or not math.isfinite(minor_cn)
        or not major_cn.is_integer()
        or not minor_cn.is_integer()
        or major_cn <= 0
        or minor_cn < 0
        or major_cn < minor_cn
    ):
        raise CanonicalInputError(
            f"row {mutation_id!r} has invalid major/minor CN state "
            f"{major_cn}/{minor_cn}"
        )
    sides = [int(major_cn)] + ([int(minor_cn)] if minor_cn > 0 else [])
    side_mass = 1.0 / len(sides)
    weights: dict[int, float] = {}
    for copy_count in sides:
        within_side_mass = side_mass / copy_count
        for multiplicity in range(1, copy_count + 1):
            weights[multiplicity] = weights.get(multiplicity, 0.0) + within_side_mass
    total = math.fsum(weights.values())
    if not math.isfinite(total) or total <= 0.0:
        raise CanonicalInputError(f"row {mutation_id!r} has invalid multiplicity normalization")
    candidates = tuple(float(value) for value in sorted(weights))
    prior = tuple(weights[int(value)] / total for value in candidates)
    if not math.isclose(math.fsum(prior), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise CanonicalInputError(f"row {mutation_id!r} multiplicity prior is not normalized")
    return candidates, prior


def load_model_table(
    path: Path,
    requested_purity: float,
    *,
    exclude_ids: Iterable[str] = frozenset(),
) -> ModelData:
    """Load eligible observations from the sole supported canonical schema.

    Every active likelihood observation must be present in the table.  The
    loader derives the multiplicity candidate map from ASCAT major/minor CN;
    there is no total-CN=2 fallback, precomputed multiplicity-map column, or
    legacy file fallback.  The data-conditioned candidate posterior is
    computed by :func:`site_multiplicity_posterior`, not loaded from a file.
    Additional metadata columns (including PS) are
    ignored by the downstream sampler: PS is upstream phasing provenance used
    to derive HP labels/counts, not a direct likelihood state variable.
    """

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"canonical integrated input does not exist: {path}")
    if not 0.0 < requested_purity <= 1.0:
        raise ValueError("requested ASCAT purity must be in (0, 1]")
    excluded = frozenset(exclude_ids)
    sites: list[SiteObservation] = []
    seen_ids: set[str] = set()
    with _open_text(path) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = tuple(reader.fieldnames or ())
        if len(fieldnames) != len(set(fieldnames)):
            raise CanonicalInputError("canonical table contains duplicate column names")
        missing = sorted(set(MODEL_REQUIRED_COLUMNS) - set(fieldnames))
        if missing:
            raise CanonicalInputError(
                "canonical table is missing required columns: " + ", ".join(missing)
            )
        forbidden = sorted(set(MODEL_FORBIDDEN_COLUMNS) & set(fieldnames))
        if forbidden:
            raise CanonicalInputError(
                "canonical table contains forbidden legacy columns: " + ", ".join(forbidden)
            )
        for row_number, row in enumerate(reader, start=2):
            mutation_id = str(row.get("mutation_id", "")).strip()
            if not mutation_id:
                raise CanonicalInputError(f"row {row_number} has empty mutation_id")
            if mutation_id in seen_ids:
                raise CanonicalInputError(f"duplicate mutation_id: {mutation_id}")
            seen_ids.add(mutation_id)
            include = str(row.get("model_include", "")).strip().lower()
            status = str(row.get("model_status", "")).strip()
            if include not in {"yes", "no"}:
                raise CanonicalInputError(
                    f"row {mutation_id!r} model_include must be yes or no"
                )
            if include != "yes" or status != "eligible":
                continue

            ref_reads = _integer(row, "ref_reads", mutation_id)
            alt_reads = _integer(row, "alt_reads", mutation_id)
            total_reads = _integer(row, "total_reads", mutation_id)
            if total_reads != ref_reads + alt_reads or total_reads <= 0:
                raise CanonicalInputError(
                    f"row {mutation_id!r} total_reads must equal ref_reads + alt_reads and be positive"
                )
            hp1_ref = _integer(row, "hp1_1_ref", mutation_id)
            hp1_alt = _integer(row, "hp1_1_alt", mutation_id)
            hp2_ref = _integer(row, "hp2_1_ref", mutation_id)
            hp2_alt = _integer(row, "hp2_1_alt", mutation_id)
            if hp1_ref + hp2_ref > ref_reads or hp1_alt + hp2_alt > alt_reads:
                raise CanonicalInputError(
                    f"row {mutation_id!r} HP allocations exceed the corresponding bulk counts"
                )

            major_cn = _number(row, "major_cn", mutation_id)
            minor_cn = _number(row, "minor_cn", mutation_id)
            total_cn = _number(row, "total_cn", mutation_id)
            if minor_cn < 0 or major_cn < minor_cn or total_cn <= 0:
                raise CanonicalInputError(f"row {mutation_id!r} has invalid ASCAT CN state")
            if not math.isclose(major_cn + minor_cn, total_cn, rel_tol=0.0, abs_tol=1e-6):
                raise CanonicalInputError(
                    f"row {mutation_id!r} total_cn disagrees with major_cn + minor_cn"
                )

            row_purity = _number(row, "rho_ASCAT", mutation_id)
            if not 0.0 < row_purity <= 1.0:
                raise CanonicalInputError(
                    f"row {mutation_id!r} has invalid rho_ASCAT={row_purity}"
                )
            if not math.isclose(row_purity, requested_purity, rel_tol=0.0, abs_tol=1e-9):
                raise CanonicalInputError(
                    f"row {mutation_id!r} rho_ASCAT={row_purity} disagrees with requested "
                    f"ASCAT purity={requested_purity}"
                )

            candidates, prior = derive_cn_multiplicity_prior(
                major_cn, minor_cn, mutation_id
            )
            if candidates[-1] > total_cn + 1e-9:
                raise CanonicalInputError(
                    f"row {mutation_id!r} multiplicity exceeds total_cn"
                )
            if mutation_id in excluded:
                continue

            sites.append(
                SiteObservation(
                    mutation_id=mutation_id,
                    chrom=_required_text(row, "chrom", mutation_id),
                    pos=_integer(row, "pos", mutation_id),
                    ref=_required_text(row, "ref", mutation_id),
                    alt=_required_text(row, "alt", mutation_id),
                    ref_reads=ref_reads,
                    alt_reads=alt_reads,
                    hp1_ref=hp1_ref,
                    hp1_alt=hp1_alt,
                    hp2_ref=hp2_ref,
                    hp2_alt=hp2_alt,
                    major_cn=major_cn,
                    minor_cn=minor_cn,
                    total_cn=total_cn,
                    purity=row_purity,
                    multiplicities=candidates,
                    multiplicity_prior=prior,
                )
            )
    if not sites:
        raise CanonicalInputError("canonical table contains no eligible, non-excluded observations")
    return ModelData(tuple(sites), requested_purity)


def logsumexp(values: Sequence[float]) -> float:
    if not values:
        return float("-inf")
    top = max(values)
    if not math.isfinite(top):
        return top
    return top + math.log(math.fsum(math.exp(value - top) for value in values))


def expected_alt_probability(
    site: SiteObservation,
    phi: float,
    multiplicity: float,
    *,
    error_rate: float = DEFAULT_ERROR_RATE,
) -> float:
    """Purity-aware ALT probability for one clone prevalence/multiplicity."""

    denominator = (1.0 - site.purity) * 2.0 + site.purity * site.total_cn
    cellular_alt_fraction = site.purity * phi * multiplicity / denominator
    probability = error_rate + (1.0 - 2.0 * error_rate) * cellular_alt_fraction
    return min(1.0 - 1e-12, max(1e-12, probability))


def log_binomial(ref_count: int, alt_count: int, probability: float) -> float:
    probability = min(1.0 - 1e-12, max(1e-12, probability))
    depth = ref_count + alt_count
    coefficient = math.lgamma(depth + 1) - math.lgamma(ref_count + 1) - math.lgamma(alt_count + 1)
    return coefficient + alt_count * math.log(probability) + ref_count * math.log1p(-probability)


def bulk_log_likelihood(
    site: SiteObservation, phi: float, multiplicity: float, *, error_rate: float = DEFAULT_ERROR_RATE
) -> float:
    return log_binomial(
        site.ref_reads,
        site.alt_reads,
        expected_alt_probability(site, phi, multiplicity, error_rate=error_rate),
    )


def _log_multinomial(counts: Sequence[int], weights: Sequence[float]) -> float:
    total_weight = math.fsum(weights)
    if total_weight <= 0:
        return float("-inf")
    probabilities = [max(1e-12, weight / total_weight) for weight in weights]
    normalizer = math.fsum(probabilities)
    probabilities = [probability / normalizer for probability in probabilities]
    total = sum(counts)
    coefficient = math.lgamma(total + 1) - math.fsum(math.lgamma(count + 1) for count in counts)
    return coefficient + math.fsum(
        count * math.log(probability) for count, probability in zip(counts, probabilities)
    )


def conditional_hp_log_likelihood(
    site: SiteObservation,
    phi: float,
    multiplicity: float,
    mutated_side: int,
    *,
    error_rate: float = DEFAULT_ERROR_RATE,
) -> float:
    """Conditional allocation of already-counted bulk ALT/REF observations.

    Bulk depth is not introduced here.  Given aggregate ALT and REF totals,
    this term asks only whether those reads were allocated to HP1, HP2, or an
    untagged channel as expected under one of the two mutation-side states.
    """

    tagged = site.hp1_ref + site.hp1_alt + site.hp2_ref + site.hp2_alt
    if tagged == 0:
        return 0.0
    q_bulk = expected_alt_probability(site, phi, multiplicity, error_rate=error_rate)
    q_mut = q_bulk
    q_ref = error_rate
    tag_fraction = min(1.0 - 1e-9, max(1e-9, tagged / site.total_reads))
    half_tag = tag_fraction / 2.0
    untagged = 1.0 - tag_fraction
    untag_alt = site.alt_reads - site.hp1_alt - site.hp2_alt
    untag_ref = site.ref_reads - site.hp1_ref - site.hp2_ref
    if mutated_side == 0:
        hp1_q, hp2_q = q_mut, q_ref
    elif mutated_side == 1:
        hp1_q, hp2_q = q_ref, q_mut
    else:
        raise ValueError("mutated_side must be 0 (HP1) or 1 (HP2)")
    alt_term = _log_multinomial(
        (site.hp1_alt, site.hp2_alt, untag_alt),
        (half_tag * hp1_q, half_tag * hp2_q, untagged * q_bulk),
    )
    ref_term = _log_multinomial(
        (site.hp1_ref, site.hp2_ref, untag_ref),
        (half_tag * (1.0 - hp1_q), half_tag * (1.0 - hp2_q), untagged * (1.0 - q_bulk)),
    )
    return alt_term + ref_term


def _multiplicity_log_components(
    site: SiteObservation, phi: float, *, error_rate: float = DEFAULT_ERROR_RATE
) -> list[float]:
    if not 0.0 <= phi <= 1.0:
        return [float("-inf")] * len(site.multiplicities)
    components: list[float] = []
    for multiplicity, prior in zip(site.multiplicities, site.multiplicity_prior):
        bulk = bulk_log_likelihood(site, phi, multiplicity, error_rate=error_rate)
        hp0 = conditional_hp_log_likelihood(
            site, phi, multiplicity, 0, error_rate=error_rate
        )
        hp1 = conditional_hp_log_likelihood(
            site, phi, multiplicity, 1, error_rate=error_rate
        )
        hp_marginal = logsumexp((math.log(0.5) + hp0, math.log(0.5) + hp1))
        components.append(math.log(prior) + bulk + hp_marginal)
    return components


def site_multiplicity_posterior(
    site: SiteObservation, phi: float, *, error_rate: float = DEFAULT_ERROR_RATE
) -> tuple[float, ...]:
    """Return ``P(m | D, H, CN, purity, phi)`` for loader-derived candidates.

    This is a model-implied latent-state posterior responsibility.  It does
    not overwrite the observed ``alt_reads / total_reads`` fraction and does
    not add a multiplicity column to the canonical input table.
    """

    components = _multiplicity_log_components(site, phi, error_rate=error_rate)
    normalizer = logsumexp(components)
    if not math.isfinite(normalizer):
        return tuple(0.0 for _ in components)
    return tuple(math.exp(component - normalizer) for component in components)


def site_log_likelihood(
    site: SiteObservation, phi: float, *, error_rate: float = DEFAULT_ERROR_RATE
) -> float:
    """Marginalize the CN-constrained multiplicity candidates and HP side."""

    components = _multiplicity_log_components(site, phi, error_rate=error_rate)
    return logsumexp(components)


def likelihood_matrix(data: ModelData, phi_values: Sequence[float]) -> list[list[float]]:
    """Return an n-sites by n-clones log-likelihood matrix."""

    return [
        [site_log_likelihood(site, float(phi)) for phi in phi_values]
        for site in data.sites
    ]


def _log_factorial_coefficients(rows: Sequence[Sequence[int]]) -> np.ndarray:
    return np.asarray(
        [
            math.lgamma(sum(row) + 1) - math.fsum(math.lgamma(value + 1) for value in row)
            for row in rows
        ],
        dtype=float,
    )


def compile_model(data: ModelData) -> CompiledModel:
    """Compile immutable site records into arrays for repeated MCMC scoring."""

    support = tuple(sorted({m for site in data.sites for m in site.multiplicities}))
    log_prior = np.full((len(data.sites), len(support)), -np.inf, dtype=float)
    support_index = {value: index for index, value in enumerate(support)}
    for row_index, site in enumerate(data.sites):
        for multiplicity, probability in zip(site.multiplicities, site.multiplicity_prior):
            log_prior[row_index, support_index[multiplicity]] = math.log(probability)
    ref = np.asarray([site.ref_reads for site in data.sites], dtype=float)
    alt = np.asarray([site.alt_reads for site in data.sites], dtype=float)
    hp1_ref = np.asarray([site.hp1_ref for site in data.sites], dtype=float)
    hp1_alt = np.asarray([site.hp1_alt for site in data.sites], dtype=float)
    hp2_ref = np.asarray([site.hp2_ref for site in data.sites], dtype=float)
    hp2_alt = np.asarray([site.hp2_alt for site in data.sites], dtype=float)
    binomial_coefficient = np.asarray(
        [
            math.lgamma(int(r + a) + 1) - math.lgamma(int(r) + 1) - math.lgamma(int(a) + 1)
            for r, a in zip(ref, alt)
        ],
        dtype=float,
    )
    return CompiledModel(
        data=data,
        ref=ref,
        alt=alt,
        total_cn=np.asarray([site.total_cn for site in data.sites], dtype=float),
        hp1_ref=hp1_ref,
        hp1_alt=hp1_alt,
        hp2_ref=hp2_ref,
        hp2_alt=hp2_alt,
        multiplicities=np.asarray(support, dtype=float),
        log_prior=log_prior,
        binomial_coefficient=binomial_coefficient,
        alt_allocation_coefficient=_log_factorial_coefficients(
            [(site.hp1_alt, site.hp2_alt, site.alt_reads - site.hp1_alt - site.hp2_alt)
             for site in data.sites]
        ),
        ref_allocation_coefficient=_log_factorial_coefficients(
            [(site.hp1_ref, site.hp2_ref, site.ref_reads - site.hp1_ref - site.hp2_ref)
             for site in data.sites]
        ),
    )
