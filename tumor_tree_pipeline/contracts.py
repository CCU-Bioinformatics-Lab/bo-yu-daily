"""Shared interfaces and invariants for the tumor-tree pipeline.

Callers and tests cross these interfaces.  Individual modules may have
internal helpers, but they must not weaken these fail-closed contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


MODEL_INPUT_SCHEMA_VERSION = "hcc1395_tumor_tree_input/v2"

MODEL_REQUIRED_COLUMNS = (
    "mutation_id",
    "chrom",
    "pos",
    "ref",
    "alt",
    "bulk_ref",
    "bulk_alt",
    "bulk_depth",
    "hp1_1_ref",
    "hp1_1_alt",
    "hp2_1_ref",
    "hp2_1_alt",
    "major_cn",
    "minor_cn",
    "total_cn",
    "rho_ASCAT",
    "multiplicity_candidates",
    "multiplicity_prior",
    "model_include",
    "model_status",
)

MODEL_FORBIDDEN_COLUMNS = (
    "tumor_dna_fraction",
    "multiplicity_posteriors",
)


@dataclass(frozen=True)
class PuritySpec:
    """One externally measured ASCAT purity value and its provenance file."""

    value: float
    source: Path
    sample: str = "HCC1395"

    def validate(self) -> None:
        if not 0.0 < self.value <= 1.0:
            raise ValueError("ASCAT purity must be in (0, 1]")
        if not self.source.is_file():
            raise FileNotFoundError(f"ASCAT purity source does not exist: {self.source}")


@dataclass(frozen=True)
class BuildInputs:
    """Validated files required by ``build_model_table``.

    PS is deliberately absent from the canonical downstream likelihood table.
    The upstream phase block still matters when it is used to derive the HP
    labels and counts; downstream, those resulting counts are the observed
    haplotype evidence.  PS can also be retained as audit and grouped-holdout
    metadata, but is not an explicit sampler state or likelihood column.
    """

    counts_dir: Path
    site_cnv_qc: Path
    purity: PuritySpec
    expected_sites: int = 30_490

    def validate(self) -> None:
        self.purity.validate()
        if not self.counts_dir.is_dir():
            raise FileNotFoundError(f"counts directory does not exist: {self.counts_dir}")
        if not self.site_cnv_qc.is_file():
            raise FileNotFoundError(f"site-CNV table does not exist: {self.site_cnv_qc}")
        if self.expected_sites <= 0:
            raise ValueError("expected_sites must be positive")


@dataclass(frozen=True)
class ChainConfig:
    """One finite-K chain configuration.

    Each chain is a seeded finite-K PhyloWGS-inspired compound MCMC chain:
    assignment Gibbs, local-mass independence MH, and conditional topology
    Gibbs. The workflow may run several independent seeds so that convergence
    diagnostics can compare chains, but that outer wrapper is not part of this
    per-chain contract.

    The defaults are the agreed formal lower bound, not a claim that a fixed
    number of iterations proves convergence.
    """

    seed: int
    num_nodes: int = 6
    iterations: int = 1_500
    burnin: int = 1_000
    thin: int = 1
    ascat_purity: float = 0.99
    checkpoint_every: int = 100

    def validate(self) -> None:
        if not 2 <= self.num_nodes <= 8:
            raise ValueError("num_nodes must be between 2 and 8")
        if self.iterations <= self.burnin:
            raise ValueError("iterations must exceed burnin")
        if self.thin != 1:
            raise ValueError("formal runs require thin=1")
        if not 0.0 < self.ascat_purity <= 1.0:
            raise ValueError("ascat_purity must be in (0, 1]")
        if self.checkpoint_every <= 0:
            raise ValueError("checkpoint_every must be positive")


@dataclass(frozen=True)
class GateThresholds:
    """Formal numerical gates; pilot workflows may report looser diagnostics."""

    max_rank_normalized_rhat: float = 1.01
    min_bulk_ess_total: float = 400.0
    min_tail_ess_total: float = 400.0
    min_assignment_agreement: float = 0.90
    max_edge_support_difference: float = 0.10
    min_predictive_coverage: float = 0.85
    max_predictive_coverage: float = 0.95

    def validate(self) -> None:
        if not 1.0 < self.max_rank_normalized_rhat <= 1.10:
            raise ValueError("formal R-hat threshold must be in (1, 1.10]")
        if self.min_bulk_ess_total <= 0 or self.min_tail_ess_total <= 0:
            raise ValueError("ESS thresholds must be positive")
        if not 0.0 <= self.min_assignment_agreement <= 1.0:
            raise ValueError("assignment agreement must be in [0, 1]")
        if not 0.0 <= self.max_edge_support_difference <= 1.0:
            raise ValueError("edge support difference must be in [0, 1]")
        if not 0.0 <= self.min_predictive_coverage <= self.max_predictive_coverage <= 1.0:
            raise ValueError("predictive coverage interval is invalid")
