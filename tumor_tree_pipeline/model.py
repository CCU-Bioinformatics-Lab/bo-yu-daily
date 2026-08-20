"""Canonical observation model for finite-K tumor-tree inference.

This module owns the narrow boundary between the versioned site table and the
sampler.  It deliberately has no legacy loader: malformed or incomplete
canonical input is an error, never a request to synthesize CN or multiplicity.
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
    bulk_ref: int
    bulk_alt: int
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
    def bulk_depth(self) -> int:
        return self.bulk_ref + self.bulk_alt


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


def parse_multiplicity_candidates(text: str, mutation_id: str = "<unknown>") -> tuple[float, ...]:
    """Parse the canonical ``1;2;...`` multiplicity support strictly."""

    values: list[float] = []
    for token in text.split(";"):
        token = token.strip()
        if not token:
            continue
        try:
            value = float(token)
        except ValueError as exc:
            raise CanonicalInputError(
                f"row {mutation_id!r} has invalid multiplicity candidate {token!r}"
            ) from exc
        if not math.isfinite(value) or value <= 0 or not value.is_integer():
            raise CanonicalInputError(
                f"row {mutation_id!r} multiplicity candidates must be positive integers"
            )
        values.append(value)
    if not values or len(values) != len(set(values)) or values != sorted(values):
        raise CanonicalInputError(
            f"row {mutation_id!r} multiplicity_candidates must be sorted, unique, and non-empty"
        )
    return tuple(values)


def parse_probability_map(
    text: str, mutation_id: str = "<unknown>"
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Parse a normalized ``multiplicity_prior`` without silently repairing it."""

    values: dict[float, float] = {}
    for token in text.split(";"):
        token = token.strip()
        if not token:
            continue
        if token.count("=") != 1:
            raise CanonicalInputError(
                f"row {mutation_id!r} has invalid multiplicity_prior token {token!r}"
            )
        raw_key, raw_probability = token.split("=", 1)
        try:
            key = float(raw_key)
            probability = float(raw_probability)
        except ValueError as exc:
            raise CanonicalInputError(
                f"row {mutation_id!r} has non-numeric multiplicity_prior token {token!r}"
            ) from exc
        if (
            not math.isfinite(key)
            or key <= 0
            or not key.is_integer()
            or not math.isfinite(probability)
            or probability <= 0
            or key in values
        ):
            raise CanonicalInputError(
                f"row {mutation_id!r} has invalid multiplicity_prior token {token!r}"
            )
        values[key] = probability
    if not values:
        raise CanonicalInputError(f"row {mutation_id!r} has empty multiplicity_prior")
    keys = tuple(sorted(values))
    probabilities = tuple(values[key] for key in keys)
    total = math.fsum(probabilities)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-6):
        raise CanonicalInputError(
            f"row {mutation_id!r} multiplicity_prior sums to {total:.12g}, not 1"
        )
    return keys, probabilities


def load_model_table(
    path: Path,
    requested_purity: float,
    *,
    exclude_ids: Iterable[str] = frozenset(),
) -> ModelData:
    """Load eligible observations from the sole supported canonical schema.

    Every active likelihood value must be present in the table.  In
    particular, there is no total-CN=2, multiplicity-map, posterior, or legacy
    file fallback.  Additional metadata columns (including PS) are ignored.
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

            bulk_ref = _integer(row, "bulk_ref", mutation_id)
            bulk_alt = _integer(row, "bulk_alt", mutation_id)
            bulk_depth = _integer(row, "bulk_depth", mutation_id)
            if bulk_depth != bulk_ref + bulk_alt or bulk_depth <= 0:
                raise CanonicalInputError(
                    f"row {mutation_id!r} bulk_depth must equal bulk_ref + bulk_alt and be positive"
                )
            hp1_ref = _integer(row, "hp1_1_ref", mutation_id)
            hp1_alt = _integer(row, "hp1_1_alt", mutation_id)
            hp2_ref = _integer(row, "hp2_1_ref", mutation_id)
            hp2_alt = _integer(row, "hp2_1_alt", mutation_id)
            if hp1_ref + hp2_ref > bulk_ref or hp1_alt + hp2_alt > bulk_alt:
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

            candidates = parse_multiplicity_candidates(
                _required_text(row, "multiplicity_candidates", mutation_id), mutation_id
            )
            prior_candidates, prior = parse_probability_map(
                _required_text(row, "multiplicity_prior", mutation_id), mutation_id
            )
            if candidates != prior_candidates:
                raise CanonicalInputError(
                    f"row {mutation_id!r} multiplicity_candidates disagree with multiplicity_prior"
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
                    bulk_ref=bulk_ref,
                    bulk_alt=bulk_alt,
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
        site.bulk_ref,
        site.bulk_alt,
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
    tag_fraction = min(1.0 - 1e-9, max(1e-9, tagged / site.bulk_depth))
    half_tag = tag_fraction / 2.0
    untagged = 1.0 - tag_fraction
    untag_alt = site.bulk_alt - site.hp1_alt - site.hp2_alt
    untag_ref = site.bulk_ref - site.hp1_ref - site.hp2_ref
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


def site_log_likelihood(
    site: SiteObservation, phi: float, *, error_rate: float = DEFAULT_ERROR_RATE
) -> float:
    """Marginalize the CN-only multiplicity prior and unknown HP side."""

    if not 0.0 <= phi <= 1.0:
        return float("-inf")
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
    ref = np.asarray([site.bulk_ref for site in data.sites], dtype=float)
    alt = np.asarray([site.bulk_alt for site in data.sites], dtype=float)
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
            [(site.hp1_alt, site.hp2_alt, site.bulk_alt - site.hp1_alt - site.hp2_alt)
             for site in data.sites]
        ),
        ref_allocation_coefficient=_log_factorial_coefficients(
            [(site.hp1_ref, site.hp2_ref, site.bulk_ref - site.hp1_ref - site.hp2_ref)
             for site in data.sites]
        ),
    )
