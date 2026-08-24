"""Reproducible HCC1395 tumor-tree inference pipeline.

The package exposes three deep-module seams:

``build_model_table``
    Convert validated site counts and ASCAT projection into the canonical
    likelihood table.
``run_smc_cpp``
    Invoke the active C++17 finite-K annealed-SMC backend.
``run_experiment``
    Orchestrate immutable, gated multi-repeat experiments.

The public functions are imported lazily by their owning modules to keep the
package import cheap for command-line validation and fixture tests.
"""

from .contracts import (
    MODEL_INPUT_SCHEMA_VERSION,
    INFERENCE_ALGORITHM_ID,
    BuildInputs,
    GateThresholds,
    PuritySpec,
    SMCConfig,
)

__all__ = [
    "MODEL_INPUT_SCHEMA_VERSION",
    "INFERENCE_ALGORITHM_ID",
    "BuildInputs",
    "SMCConfig",
    "GateThresholds",
    "PuritySpec",
]

__version__ = "0.1.0"
