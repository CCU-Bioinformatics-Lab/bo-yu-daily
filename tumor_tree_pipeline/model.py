"""Canonical observation model for finite-K tumor-tree inference.

This module owns the narrow boundary between the versioned site table and the
sampler.  It deliberately has no legacy loader: malformed or incomplete
canonical input is an error.  The loader derives PyClone-VI-style CN/timing
genotype candidates from the canonical ASCAT major/minor/total CN fields
instead of accepting a precomputed multiplicity table column; the emission can
then return a posterior responsibility for each candidate.
"""

from __future__ import annotations

import csv
import gzip
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

from .contracts import MODEL_FORBIDDEN_COLUMNS, MODEL_REQUIRED_COLUMNS


class CanonicalInputError(ValueError):
    """The canonical model table violates its versioned schema contract."""


NORMAL_COPY_NUMBER = 2.0
PHYCLONE_ERROR_RATE = 1e-3


@dataclass(frozen=True)
class GenotypeCandidate:
    """One PyClone-VI-style CN/timing candidate for a site."""

    multiplicity: float
    normal_cn: float
    reference_cn: float
    variant_cn: float
    normal_alt_probability: float
    reference_alt_probability: float
    variant_alt_probability: float
    prior: float


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
    genotype_candidates: tuple[GenotypeCandidate, ...]

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
    """Vectorized form of :class:`ModelData` reused across SMC particle scoring."""

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
    candidate_normal_cn: np.ndarray
    candidate_reference_cn: np.ndarray
    candidate_variant_cn: np.ndarray
    candidate_normal_alt_probability: np.ndarray
    candidate_reference_alt_probability: np.ndarray
    candidate_variant_alt_probability: np.ndarray
    candidate_log_prior: np.ndarray
    binomial_coefficient: np.ndarray
    alt_allocation_coefficient: np.ndarray
    ref_allocation_coefficient: np.ndarray

    def likelihood_matrix(self, phi_values: Sequence[float]) -> np.ndarray:
        """Evaluate the Model A PhyClone-VI-style xi likelihood.

        The HP arrays remain part of the compiled observation for schema and
        supplementary-data compatibility, but Model A deliberately does not
        score them.  The conditional HP helper below is reserved for a future
        Model B and must not be folded into this primary emission.
        """

        phi_values = np.asarray(phi_values, dtype=float)
        if phi_values.ndim != 1 or np.any(phi_values < 0.0) or np.any(phi_values > 1.0):
            raise ValueError("phi_values must be a one-dimensional vector in [0, 1]")
        n_sites = len(self.ref)
        result = np.empty((n_sites, len(phi_values)), dtype=float)
        ref = self.ref[:, None]
        alt = self.alt[:, None]
        purity = self.data.purity
        normal_weight = 1.0 - purity

        for node_index, phi in enumerate(phi_values):
            reference_weight = purity * (1.0 - phi)
            variant_weight = purity * phi
            denominator = (
                normal_weight * self.candidate_normal_cn
                + reference_weight * self.candidate_reference_cn
                + variant_weight * self.candidate_variant_cn
            )
            numerator = (
                normal_weight * self.candidate_normal_cn * self.candidate_normal_alt_probability
                + reference_weight * self.candidate_reference_cn * self.candidate_reference_alt_probability
                + variant_weight * self.candidate_variant_cn * self.candidate_variant_alt_probability
            )
            q_bulk = np.clip(numerator / denominator, 1e-12, 1.0 - 1e-12)
            bulk = (
                self.binomial_coefficient[:, None]
                + alt * np.log(q_bulk)
                + ref * np.log1p(-q_bulk)
            )
            components = self.candidate_log_prior + bulk
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


def _derive_genotype_candidates(
    major_cn: float,
    minor_cn: float,
    total_cn: float,
    mutation_id: str = "<unknown>",
) -> tuple[GenotypeCandidate, ...]:
    """Build the PyClone-VI major-CN prior and timing candidates."""
    major_cn = float(major_cn)
    minor_cn = float(minor_cn)
    total_cn = float(total_cn)
    if (
        not math.isfinite(major_cn)
        or not math.isfinite(minor_cn)
        or not math.isfinite(total_cn)
        or not major_cn.is_integer()
        or not minor_cn.is_integer()
        or not total_cn.is_integer()
        or major_cn <= 0
        or minor_cn < 0
        or major_cn < minor_cn
        or int(total_cn) != int(major_cn) + int(minor_cn)
    ):
        raise CanonicalInputError(
            f"row {mutation_id!r} has invalid major/minor CN state "
            f"{major_cn}/{minor_cn}/{total_cn}"
        )
    total = float(int(total_cn))
    candidates = [
        GenotypeCandidate(
            multiplicity=float(multiplicity),
            normal_cn=NORMAL_COPY_NUMBER,
            reference_cn=NORMAL_COPY_NUMBER,
            variant_cn=total,
            normal_alt_probability=PHYCLONE_ERROR_RATE,
            reference_alt_probability=PHYCLONE_ERROR_RATE,
            variant_alt_probability=min(
                1.0 - PHYCLONE_ERROR_RATE, float(multiplicity) / total
            ),
            prior=0.0,
        )
        for multiplicity in range(1, int(major_cn) + 1)
    ]
    if int(total_cn) != int(NORMAL_COPY_NUMBER):
        candidates.append(
            GenotypeCandidate(
                multiplicity=1.0,
                normal_cn=NORMAL_COPY_NUMBER,
                reference_cn=total,
                variant_cn=total,
                normal_alt_probability=PHYCLONE_ERROR_RATE,
                reference_alt_probability=PHYCLONE_ERROR_RATE,
                variant_alt_probability=min(1.0 - PHYCLONE_ERROR_RATE, 1.0 / total),
                prior=0.0,
            )
        )
    if not candidates:
        raise CanonicalInputError(f"row {mutation_id!r} has no valid genotype candidates")
    prior = 1.0 / len(candidates)
    return tuple(replace(candidate, prior=prior) for candidate in candidates)


def derive_cn_multiplicity_prior(
    major_cn: float, minor_cn: float, mutation_id: str = "<unknown>", total_cn: float | None = None
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return candidate-aligned multiplicities and PyClone-VI priors.

    Unlike the old side-mass baseline, the returned support may contain the
    same multiplicity more than once because mutation-before-CN and
    mutation-after-CN are distinct genotype candidates.
    """

    resolved_total_cn = major_cn + minor_cn if total_cn is None else total_cn
    candidates = _derive_genotype_candidates(major_cn, minor_cn, resolved_total_cn, mutation_id)
    return (
        tuple(candidate.multiplicity for candidate in candidates),
        tuple(candidate.prior for candidate in candidates),
    )


def load_model_table(
    path: Path,
    requested_purity: float,
    *,
    exclude_ids: Iterable[str] = frozenset(),
) -> ModelData:
    """Load eligible observations from the sole supported canonical schema.

    Every active likelihood observation must be present in the table.  The
    loader derives the genotype/timing candidate map from ASCAT major/minor/total
    CN; normal CN=2 and error_rate=0.001 are fixed model-side assumptions. There
    is no precomputed multiplicity-map column or legacy file fallback. The
    data-conditioned candidate posterior is
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

            genotype_candidates = _derive_genotype_candidates(
                major_cn, minor_cn, total_cn, mutation_id
            )
            candidates = tuple(candidate.multiplicity for candidate in genotype_candidates)
            prior = tuple(candidate.prior for candidate in genotype_candidates)
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
                    genotype_candidates=genotype_candidates,
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
) -> float:
    """Return expected ALT probability for the first candidate with this m.

    This compatibility helper is used by supplementary predictive code.  The
    primary emission iterates candidate objects directly because two timing
    candidates can share the same multiplicity.
    """

    candidate = next(
        (candidate for candidate in site.genotype_candidates
         if candidate.multiplicity == multiplicity),
        None,
    )
    if candidate is None:
        raise ValueError(f"multiplicity {multiplicity} is not a candidate for {site.mutation_id}")
    return expected_alt_probability_for_candidate(site, phi, candidate)


def expected_alt_probability_for_candidate(
    site: SiteObservation,
    phi: float,
    candidate: GenotypeCandidate,
) -> float:
    """Compute PyClone-VI's DNA-copy-weighted expected ALT probability."""

    normal_weight = 1.0 - site.purity
    reference_weight = site.purity * (1.0 - phi)
    variant_weight = site.purity * phi
    denominator = (
        normal_weight * candidate.normal_cn
        + reference_weight * candidate.reference_cn
        + variant_weight * candidate.variant_cn
    )
    numerator = (
        normal_weight * candidate.normal_cn * candidate.normal_alt_probability
        + reference_weight * candidate.reference_cn * candidate.reference_alt_probability
        + variant_weight * candidate.variant_cn * candidate.variant_alt_probability
    )
    if not math.isfinite(denominator) or denominator <= 0.0 or not math.isfinite(numerator):
        raise ValueError(f"invalid genotype candidate denominator for {site.mutation_id}")
    return min(1.0 - 1e-12, max(1e-12, numerator / denominator))


def log_binomial(ref_count: int, alt_count: int, probability: float) -> float:
    probability = min(1.0 - 1e-12, max(1e-12, probability))
    depth = ref_count + alt_count
    coefficient = math.lgamma(depth + 1) - math.lgamma(ref_count + 1) - math.lgamma(alt_count + 1)
    return coefficient + alt_count * math.log(probability) + ref_count * math.log1p(-probability)


def bulk_log_likelihood(site: SiteObservation, phi: float, multiplicity: float) -> float:
    return log_binomial(
        site.ref_reads,
        site.alt_reads,
        expected_alt_probability(site, phi, multiplicity),
    )


def bulk_log_likelihood_for_candidate(
    site: SiteObservation, phi: float, candidate: GenotypeCandidate
) -> float:
    return log_binomial(
        site.ref_reads,
        site.alt_reads,
        expected_alt_probability_for_candidate(site, phi, candidate),
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
) -> float:
    """Conditional allocation of already-counted bulk ALT/REF observations.

    Bulk depth is not introduced here.  Given aggregate ALT and REF totals,
    this term asks only whether those reads were allocated to HP1, HP2, or an
    untagged channel as expected under one of the two mutation-side states.
    """

    tagged = site.hp1_ref + site.hp1_alt + site.hp2_ref + site.hp2_alt
    if tagged == 0:
        return 0.0
    q_bulk = expected_alt_probability(site, phi, multiplicity)
    q_mut = q_bulk
    q_ref = 0.0
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


def _multiplicity_log_components(site: SiteObservation, phi: float) -> list[float]:
    """Return Model A multiplicity components for one site and clone fraction.

    HP counts are intentionally absent.  They are validated and retained as
    supplementary observations by the loader, while ``conditional_hp_log_likelihood``
    remains available for a separately specified Model B.
    """

    if not 0.0 <= phi <= 1.0:
        return [float("-inf")] * len(site.genotype_candidates)
    components: list[float] = []
    for candidate in site.genotype_candidates:
        bulk = bulk_log_likelihood_for_candidate(site, phi, candidate)
        components.append(math.log(candidate.prior) + bulk)
    return components


def site_multiplicity_posterior(
    site: SiteObservation, phi: float
) -> tuple[float, ...]:
    """Return ``P(m | D, CN, purity, phi)`` for loader-derived candidates.

    This is a model-implied latent-state posterior responsibility.  It does
    not overwrite the observed ``alt_reads / total_reads`` fraction and does
    not add a multiplicity column to the canonical input table.  HP counts are
    supplementary data and are intentionally excluded from Model A.
    """

    components = _multiplicity_log_components(site, phi)
    normalizer = logsumexp(components)
    if not math.isfinite(normalizer):
        return tuple(0.0 for _ in components)
    return tuple(math.exp(component - normalizer) for component in components)


def site_log_likelihood(
    site: SiteObservation, phi: float
) -> float:
    """Marginalize CN-constrained multiplicity candidates for Model A."""

    components = _multiplicity_log_components(site, phi)
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
    """Compile immutable site records into arrays for repeated particle scoring."""

    support = tuple(sorted({m for site in data.sites for m in site.multiplicities}))
    log_prior = np.full((len(data.sites), len(support)), -np.inf, dtype=float)
    support_index = {value: index for index, value in enumerate(support)}
    for row_index, site in enumerate(data.sites):
        for multiplicity, probability in zip(site.multiplicities, site.multiplicity_prior):
            index = support_index[multiplicity]
            log_prior[row_index, index] = np.logaddexp(
                log_prior[row_index, index], math.log(probability)
            )
    max_candidates = max(len(site.genotype_candidates) for site in data.sites)
    candidate_arrays = {
        # Padded candidate slots have -inf prior and are never selected.  Give
        # them a finite, neutral copy-number context so the vectorized xi
        # calculation cannot evaluate 0 / 0 before the prior masks them out.
        name: np.full(
            (len(data.sites), max_candidates),
            NORMAL_COPY_NUMBER if name.endswith("_cn") else PHYCLONE_ERROR_RATE,
            dtype=float,
        )
        for name in (
            "normal_cn",
            "reference_cn",
            "variant_cn",
            "normal_alt_probability",
            "reference_alt_probability",
            "variant_alt_probability",
        )
    }
    candidate_log_prior = np.full(
        (len(data.sites), max_candidates), -np.inf, dtype=float
    )
    for row_index, site in enumerate(data.sites):
        for candidate_index, candidate in enumerate(site.genotype_candidates):
            candidate_arrays["normal_cn"][row_index, candidate_index] = candidate.normal_cn
            candidate_arrays["reference_cn"][row_index, candidate_index] = candidate.reference_cn
            candidate_arrays["variant_cn"][row_index, candidate_index] = candidate.variant_cn
            candidate_arrays["normal_alt_probability"][row_index, candidate_index] = candidate.normal_alt_probability
            candidate_arrays["reference_alt_probability"][row_index, candidate_index] = candidate.reference_alt_probability
            candidate_arrays["variant_alt_probability"][row_index, candidate_index] = candidate.variant_alt_probability
            candidate_log_prior[row_index, candidate_index] = math.log(candidate.prior)
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
        candidate_normal_cn=candidate_arrays["normal_cn"],
        candidate_reference_cn=candidate_arrays["reference_cn"],
        candidate_variant_cn=candidate_arrays["variant_cn"],
        candidate_normal_alt_probability=candidate_arrays["normal_alt_probability"],
        candidate_reference_alt_probability=candidate_arrays["reference_alt_probability"],
        candidate_variant_alt_probability=candidate_arrays["variant_alt_probability"],
        candidate_log_prior=candidate_log_prior,
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
