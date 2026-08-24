from __future__ import annotations

import gzip
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tumor_tree_pipeline.diagnostics import (
    DiagnosticError,
    _smc_edge_draw,
    smc_artifact_payload,
    summarize_smc_repeats,
)
from tumor_tree_pipeline.tests.smc_contract_fixture import (
    SMC_ARTIFACTS,
    assert_smc_artifacts,
    write_synthetic_smc_run,
)


class SyntheticSMCContractTests(unittest.TestCase):
    def test_single_repeat_is_only_allowed_for_explicit_quick_pilot_mode(self) -> None:
        result = {
            "prevalence_draws": [[0.8, 0.2], [0.7, 0.3]],
            "assignment_map": ["clone_1", "clone_2"],
            "edge_draws": [[("tumor_root", "clone_1")]],
            "predictive_coverage": 0.9,
            "predictive_log_score": -1.0,
            "smc_diagnostics": {
                "algorithm": "rao_blackwellized_annealed_smc",
                "annealing": {"final_beta": 1.0},
                "conditional_ess_fraction": 0.8,
                "weighted_particle_ess_fraction": 0.8,
                "particle_diversity": 0.5,
                "ancestor_diversity": 0.5,
                "eta_acceptance": 0.2,
                "topology_acceptance": 0.2,
                "topology_change_rate": 0.2,
            },
        }
        with self.assertRaisesRegex(DiagnosticError, "at least two"):
            summarize_smc_repeats([result])
        diagnostics = summarize_smc_repeats([result], allow_single_repeat=True)
        self.assertFalse(diagnostics["repeat_stability_evaluated"])
        self.assertIsNone(diagnostics["ccf_stability"])
        self.assertIsNone(diagnostics["min_assignment_agreement"])
        self.assertIsNone(diagnostics["max_edge_support_difference"])

    def test_minimal_fixture_is_complete_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = write_synthetic_smc_run(root / "first")
            second = write_synthetic_smc_run(root / "second")

            first_diagnostics = assert_smc_artifacts(first)
            second_diagnostics = assert_smc_artifacts(second)
            self.assertEqual(first_diagnostics, second_diagnostics)
            for artifact in SMC_ARTIFACTS:
                self.assertEqual(
                    (first / artifact).read_bytes(),
                    (second / artifact).read_bytes(),
                    artifact,
                )

    def test_weighted_ess_and_rejuvenation_are_stage_level_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = write_synthetic_smc_run(Path(temporary) / "smc")
            diagnostics = assert_smc_artifacts(output)
            stages = diagnostics["annealing"]["stages"]
            self.assertTrue(all("conditional_ess" in stage for stage in stages))
            self.assertTrue(all("weighted_ess" in stage for stage in stages))
            self.assertTrue(any(stage["resampled"] for stage in stages))
            self.assertEqual(
                len(diagnostics["rejuvenation"]["stages"]),
                len(stages),
            )

    def test_compatibility_filenames_are_explicitly_particle_semantic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = write_synthetic_smc_run(Path(temporary) / "smc")
            completion = json.loads((output / "smc_complete.json").read_text(encoding="utf-8"))
            checkpoint = json.loads(gzip.decompress((output / "checkpoint.json.gz").read_bytes()))
            self.assertEqual(completion["sample_semantics"], "smc_particle")
            self.assertEqual(completion["checkpoint_semantics"], "smc_stage_particle_state")
            self.assertEqual(checkpoint["sample_semantics"], "smc_particle")
            self.assertEqual(checkpoint["checkpoint_semantics"], "smc_stage_particle_state")

    def test_workflow_adapter_accepts_cpp_diagnostic_sample_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = write_synthetic_smc_run(Path(temporary) / "smc")
            with mock.patch(
                "tumor_tree_pipeline.diagnostics.strict_holdout_predictive_metrics",
                return_value={"coverage": 0.9, "log_score": -1.0},
            ):
                payload = smc_artifact_payload(
                    samples_path=output / "samples.jsonl.gz",
                    representative_tree_path=output / "representative_tree.json",
                    diagnostics_path=output / "diagnostics.json",
                    table_path=output / "unused.tsv",
                    holdout_ids=frozenset({"chr1:101:A>T"}),
                    purity=0.99,
                )
            self.assertEqual(payload["sample_kind"], "smc_particle")

    def test_workflow_adapter_accepts_non_topologically_numbered_cpp_tree(self) -> None:
        edges = _smc_edge_draw({"parents": [-1, 3, 3, 4, 0, 1]})
        self.assertIn(("clone_4", "clone_2"), edges)
        self.assertIn(("clone_5", "clone_4"), edges)


if __name__ == "__main__":
    unittest.main()
