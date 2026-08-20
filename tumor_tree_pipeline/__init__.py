"""Reproducible HCC1395 tumor-tree inference pipeline.

The package exposes three deep-module seams:

``build_model_table``
    Convert validated site counts and ASCAT projection into the canonical
    likelihood table.
``run_chain``
    Fit one finite-K posterior chain from that table.
``run_experiment``
    Orchestrate immutable, gated multi-chain experiments.

The public functions are imported lazily by their owning modules to keep the
package import cheap for command-line validation and fixture tests.
"""

from .contracts import (
    MODEL_INPUT_SCHEMA_VERSION,
    BuildInputs,
    ChainConfig,
    GateThresholds,
    PuritySpec,
)

__all__ = [
    "MODEL_INPUT_SCHEMA_VERSION",
    "BuildInputs",
    "ChainConfig",
    "GateThresholds",
    "PuritySpec",
]

__version__ = "0.1.0"
