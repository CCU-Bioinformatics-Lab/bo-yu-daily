"""Shared interfaces and invariants for the tumor-tree pipeline.

Callers and tests cross these interfaces.  Individual modules may have
internal helpers, but they must not weaken these fail-closed contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


MODEL_INPUT_SCHEMA_VERSION = "hcc1395_tumor_tree_input/v4"
INFERENCE_ALGORITHM_ID = "rao_blackwellized_annealed_smc"
SMC_SAMPLE_KIND = "smc_particle"

MODEL_REQUIRED_COLUMNS = (
    "mutation_id",
    "chrom",
    "pos",
    "ref",
    "alt",
    "ref_reads",
    "alt_reads",
    "total_reads",
    "hp1_1_ref",
    "hp1_1_alt",
    "hp2_1_ref",
    "hp2_1_alt",
    "major_cn",
    "minor_cn",
    "total_cn",
    "rho_ASCAT",
    "model_include",
    "model_status",
)

MODEL_FORBIDDEN_COLUMNS = (
    "tumor_dna_fraction",
    "multiplicity_candidates",
    "multiplicity_prior",
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
class SMCConfig:
    """One independent repeat of the active Rao--Blackwellized SMC backend."""

    seed: int
    num_nodes: int = 6
    particles: int = 1_024
    max_annealing_stages: int = 64
    conditional_ess_target: float = 0.80
    resample_ess_threshold: float = 0.50
    min_rejuvenation_sweeps: int = 3
    max_rejuvenation_sweeps: int = 3
    eta_rw_scale: float = 0.10
    topology_global_probability: float = 0.20
    global_topology_moves: int = 1
    ascat_purity: float = 0.99
    checkpoint_every: int = 1

    def validate(self) -> None:
        if not 2 <= self.num_nodes <= 8:
            raise ValueError("num_nodes must be between 2 and 8")
        if self.particles < 2:
            raise ValueError("particles must be at least 2")
        if self.max_annealing_stages <= 0:
            raise ValueError("max_annealing_stages must be positive")
        if not 0.0 < self.resample_ess_threshold < self.conditional_ess_target <= 1.0:
            raise ValueError(
                "SMC ESS thresholds must satisfy 0 < resample_ess_threshold "
                "< conditional_ess_target <= 1"
            )
        if not 1 <= self.min_rejuvenation_sweeps <= self.max_rejuvenation_sweeps:
            raise ValueError("rejuvenation sweep bounds are invalid")
        if not 0.0 < self.eta_rw_scale:
            raise ValueError("eta_rw_scale must be positive")
        if not 0.0 <= self.topology_global_probability <= 1.0:
            raise ValueError("topology_global_probability must be in [0, 1]")
        if self.global_topology_moves < 0:
            raise ValueError("global_topology_moves must be non-negative")
        if not 0.0 < self.ascat_purity <= 1.0:
            raise ValueError("ascat_purity must be in (0, 1]")
        if self.checkpoint_every <= 0:
            raise ValueError("checkpoint_every must be positive")


@dataclass(frozen=True)
class GateThresholds:
    """Formal SMC gates; particle ESS and repeat-stability metrics define this contract."""

    min_conditional_ess_fraction: float = 0.50
    min_weighted_particle_ess_fraction: float = 0.50
    min_particle_diversity: float = 0.25
    min_ancestor_diversity: float = 0.25
    min_ccf_stability: float = 0.90
    min_assignment_agreement: float = 0.90
    max_edge_support_difference: float = 0.10
    min_predictive_coverage: float = 0.85
    max_predictive_coverage: float = 0.95

    def validate(self) -> None:
        for name, value in (
            ("min_conditional_ess_fraction", self.min_conditional_ess_fraction),
            ("min_weighted_particle_ess_fraction", self.min_weighted_particle_ess_fraction),
            ("min_particle_diversity", self.min_particle_diversity),
            ("min_ancestor_diversity", self.min_ancestor_diversity),
            ("min_ccf_stability", self.min_ccf_stability),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if not 0.0 <= self.min_assignment_agreement <= 1.0:
            raise ValueError("assignment agreement must be in [0, 1]")
        if not 0.0 <= self.max_edge_support_difference <= 1.0:
            raise ValueError("edge support difference must be in [0, 1]")
        if not 0.0 <= self.min_predictive_coverage <= self.max_predictive_coverage <= 1.0:
            raise ValueError("predictive coverage interval is invalid")
