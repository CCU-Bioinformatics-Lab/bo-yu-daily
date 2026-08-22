from __future__ import annotations

import csv
import dataclasses
import gzip
import hashlib
import json
import math
import stat
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import numpy as np

from tumor_tree_pipeline.contracts import (
    MODEL_INPUT_SCHEMA_VERSION,
    MODEL_REQUIRED_COLUMNS,
    GateThresholds,
)
from tumor_tree_pipeline.cli import main as cli_main
from tumor_tree_pipeline.provenance import atomic_write_text
from tumor_tree_pipeline.diagnostics import (
    bulk_tail_ess,
    rank_normalized_split_folded_rhat,
)
from tumor_tree_pipeline.workflow import (
    ExperimentConfig,
    GateFailure,
    WorkflowError,
    experiment_matrix,
    run_experiment,
)


FIXED_NOW = datetime(2026, 8, 19, 12, 34, 56, tzinfo=timezone.utc)
GIT_SHA = "abc123def456"


def _write_table_bundle(root: Path, rows: int = 20) -> tuple[Path, Path, Path]:
    table = root / "model_input.tsv"
    metadata = root / "holdout_metadata.tsv"
    with table.open("w", newline="", encoding="utf-8") as handle, metadata.open(
        "w", newline="", encoding="utf-8"
    ) as metadata_handle:
        writer = csv.DictWriter(handle, fieldnames=MODEL_REQUIRED_COLUMNS, delimiter="\t")
        writer.writeheader()
        metadata_writer = csv.DictWriter(
            metadata_handle,
            fieldnames=("mutation_id", "chrom", "ps", "ascat_segment_id"),
            delimiter="\t",
        )
        metadata_writer.writeheader()
        for index in range(rows):
            mutation_id = f"chr{index % 5 + 1}:{1000 + index}:A>T"
            row = {
                "mutation_id": mutation_id,
                "chrom": f"chr{index % 5 + 1}",
                "pos": 1000 + index,
                "ref": "A",
                "alt": "T",
                "bulk_ref": 80,
                "bulk_alt": 20,
                "bulk_depth": 100,
                "hp1_1_ref": 10,
                "hp1_1_alt": 4,
                "hp2_1_ref": 11,
                "hp2_1_alt": 3,
                "major_cn": 1,
                "minor_cn": 1,
                "total_cn": 2,
                "rho_ASCAT": 0.99,
                "multiplicity_candidates": "1",
                "multiplicity_prior": "1=1",
                "model_include": "yes",
                "model_status": "eligible",
            }
            writer.writerow(row)
            metadata_writer.writerow(
                {
                    "mutation_id": mutation_id,
                    "chrom": row["chrom"],
                    "ps": f"PS{index // 2}",
                    "ascat_segment_id": f"SEG{index // 3}",
                }
            )
    digest = hashlib.sha256(table.read_bytes()).hexdigest()
    manifest = root / "validation_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": MODEL_INPUT_SCHEMA_VERSION,
                "table_sha256": digest,
                "rho_ASCAT": 0.99,
                "qa_pass": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return table, manifest, metadata


def _write_formal_prerequisites(root: Path) -> tuple[Path, Path]:
    ps = root / "ps_audit.json"
    ps.write_text(
        json.dumps({"passed": True, "discordance_fraction": 0.000667}) + "\n",
        encoding="utf-8",
    )
    simulation = root / "simulation.json"
    simulation.write_text(json.dumps({"passed": True}) + "\n", encoding="utf-8")
    return ps, simulation


def _passing_diagnostics() -> dict[str, object]:
    return {
        "max_rank_normalized_split_folded_rhat": 1.001,
        "min_bulk_ess_total": 500.0,
        "min_tail_ess_total": 500.0,
        "min_assignment_agreement": 0.95,
        "max_edge_support_difference": 0.05,
        "predictive_coverage_by_chain": [0.90] * 4,
        "predictive_log_score_by_chain": [-1.0] * 4,
        "min_predictive_log_score": -1.0,
    }


class DiagnosticContractTests(unittest.TestCase):
    def test_rank_normalized_diagnostics_are_finite_for_mixed_iid_chains(self) -> None:
        rng = np.random.default_rng(20260819)
        chains = [rng.normal(size=600) for _ in range(4)]
        rhat = rank_normalized_split_folded_rhat(chains)
        ess = bulk_tail_ess(chains)
        self.assertLess(rhat["max_rhat"], 1.05)
        self.assertGreater(ess["bulk_ess_total"], 200)
        self.assertGreater(ess["tail_ess_total"], 200)

    def test_constant_trace_fails_closed_instead_of_reporting_convergence(self) -> None:
        rhat = rank_normalized_split_folded_rhat([[1.0] * 20 for _ in range(4)])
        self.assertTrue(math.isinf(rhat["max_rhat"]))


class WorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.git_state_patch = mock.patch(
            "tumor_tree_pipeline.workflow._git_worktree_state",
            return_value={"clean": True, "porcelain": []},
        )
        self.git_state = self.git_state_patch.start()
        self.addCleanup(self.git_state_patch.stop)

    def test_cli_returns_nonzero_when_a_formal_gate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text("{}\n", encoding="utf-8")
            fake_config = mock.Mock()
            fake_config.validate.return_value = None
            with mock.patch("tumor_tree_pipeline.cli.load_config", return_value=fake_config), mock.patch(
                "tumor_tree_pipeline.cli.run_experiment",
                side_effect=GateFailure("formal diagnostic gate failed"),
            ):
                self.assertEqual(cli_main(["run", "--config", str(config_path)]), 2)

    def test_cli_resume_sets_explicit_resume_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text("{}\n", encoding="utf-8")
            fake_config = mock.Mock()
            resumed_config = mock.Mock()
            resumed_config.validate.return_value = None
            with mock.patch("tumor_tree_pipeline.cli.load_config", return_value=fake_config), mock.patch(
                "tumor_tree_pipeline.cli.dataclasses.replace",
                return_value=resumed_config,
            ) as replace, mock.patch(
                "tumor_tree_pipeline.cli.run_experiment", return_value=Path("/tmp/resumed")
            ) as run:
                self.assertEqual(cli_main(["run", "--config", str(config_path), "--resume"]), 0)
                replace.assert_called_once_with(fake_config, resume=True)
                run.assert_called_once_with(resumed_config)

    def test_formal_matrix_orders_main_then_k_then_purity_sensitivity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            ps, simulation = _write_formal_prerequisites(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                min_predictive_log_score=-5.0,
            )
            observed = [(cell.stage, cell.num_nodes, cell.purity) for cell in experiment_matrix(config)]
            self.assertEqual(
                observed,
                [
                    ("formal_main", 6, 0.99),
                    ("formal_k_sensitivity", 4, 0.99),
                    ("formal_k_sensitivity", 8, 0.99),
                    ("formal_purity_sensitivity", 6, 0.97),
                    ("formal_purity_sensitivity", 6, 0.95),
                ],
            )

    def test_smoke_is_immutable_and_publishes_success_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )

            def fake_runner(**kwargs):
                return {}

            output = run_experiment(
                config,
                chain_runner=fake_runner,
                now=FIXED_NOW,
                git_sha=GIT_SHA,
            )
            self.assertTrue((output / "_SUCCESS").is_file())
            self.assertFalse((output / "_FAILED").exists())
            self.assertIn("20260819T123456Z", output.name)
            self.assertIn(GIT_SHA, output.name)
            self.assertIn("rho0p99", output.name)
            self.assertIn("K6", output.name)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o2775)
            self.assertEqual(stat.S_IMODE((output / "manifest.json").stat().st_mode), 0o664)
            trace = [
                json.loads(line)
                for line in (output / "execution_trace.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(trace[0]["event"], "workflow_started")
            self.assertEqual(trace[-1]["event"], "workflow_completed")
            self.assertIn("chain_completed", {event["event"] for event in trace})
            inventory = json.loads((output / "artifact_inventory.json").read_text())
            inventory_paths = {item["path"] for item in inventory["artifacts"]}
            self.assertIn("manifest.json", inventory_paths)
            self.assertNotIn("_SUCCESS", inventory_paths)
            success_before = (output / "_SUCCESS").read_text()
            with self.assertRaises(WorkflowError):
                run_experiment(
                    config,
                    chain_runner=fake_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            self.assertEqual((output / "_SUCCESS").read_text(), success_before)
            self.assertFalse((output / "_FAILED").exists())

    def test_default_sampler_adapter_completes_only_the_tiny_smoke_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root, rows=8)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
                smoke_iterations=10,
                smoke_burnin=2,
            )
            output = run_experiment(config, now=FIXED_NOW, git_sha=GIT_SHA)
            self.assertTrue((output / "_SUCCESS").is_file())
            completed = list(output.glob("runs/**/chain_complete.json"))
            self.assertEqual(len(completed), 2)
            diagnostics = [
                json.loads((path.parent / "diagnostics.json").read_text(encoding="utf-8"))
                for path in completed
            ]
            self.assertEqual(len(diagnostics), 2)
            for payload in diagnostics:
                self.assertEqual(payload["model"], "finite_K_tssb_inspired")
                self.assertEqual(
                    set(payload["counters"]),
                    {
                        "assignment_proposals",
                        "assignment_accepted",
                        "eta_proposals",
                        "eta_accepted",
                        "topology_proposals",
                        "topology_accepted",
                    },
                )
                self.assertNotIn("eta_bridge_acceptance", payload)
                self.assertNotIn("eta_bridge_proposals", payload)
                self.assertIn("gibbs", json.dumps(payload).lower())

    def test_formal_gate_failure_is_non_success_and_stops_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            ps, simulation = _write_formal_prerequisites(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                min_predictive_log_score=-5.0,
            )
            calls = []

            def fake_runner(**kwargs):
                calls.append(kwargs)
                return {}

            failed = dict(_passing_diagnostics())
            failed["max_rank_normalized_split_folded_rhat"] = 1.5
            with mock.patch("tumor_tree_pipeline.workflow.summarize_chains", return_value=failed):
                with self.assertRaises(GateFailure):
                    run_experiment(
                        config,
                        chain_runner=fake_runner,
                        now=FIXED_NOW,
                        git_sha=GIT_SHA,
                    )
            outputs = list((root / "out").iterdir())
            self.assertEqual(len(outputs), 1)
            output = outputs[0]
            self.assertTrue((output / "_FAILED").is_file())
            self.assertFalse((output / "_SUCCESS").exists())
            self.assertEqual(len(calls), 4, "the first failed holdout must stop later cells")
            status = json.loads((output / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["failed_stage"], "formal_main")
            self.assertEqual(status["failed_scope"], "K=6,rho_ASCAT=0.990000")
            trace = [
                json.loads(line)
                for line in (output / "execution_trace.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(trace[-1]["event"], "workflow_failed")
            self.assertEqual(trace[-1]["stage"], "formal_main")
            self.assertEqual(trace[-1]["status"], "failed")
            self.assertTrue(any(event["event"] == "holdout_failed" for event in trace))

    def test_formal_success_runs_all_holdouts_and_purity_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            ps, simulation = _write_formal_prerequisites(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                gate_thresholds=GateThresholds(),
                min_predictive_log_score=-5.0,
            )
            calls = []

            def fake_runner(**kwargs):
                calls.append(kwargs)
                with Path(kwargs["table_path"]).open("r", encoding="utf-8") as handle:
                    first = next(csv.DictReader(handle, delimiter="\t"))
                self.assertAlmostEqual(float(first["rho_ASCAT"]), kwargs["config"].ascat_purity)
                return {}

            with mock.patch(
                "tumor_tree_pipeline.workflow.summarize_chains",
                return_value=_passing_diagnostics(),
            ):
                output = run_experiment(
                    config,
                    chain_runner=fake_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            self.assertTrue((output / "_SUCCESS").is_file())
            self.assertEqual(len(calls), 5 * 3 * 4)
            self.assertEqual({call["holdout_kind"] for call in calls}, {"ps", "chromosome", "ascat_segment"})
            self.assertEqual({call["config"].num_nodes for call in calls}, {4, 6, 8})
            self.assertEqual({call["config"].ascat_purity for call in calls}, {0.99, 0.97, 0.95})
            self.assertTrue(all(call["config"].iterations == 1500 for call in calls))
            self.assertTrue(all(call["config"].burnin == 1000 for call in calls))
            self.assertEqual(len({call["config"].seed for call in calls}), len(calls))

    def test_formal_dirty_tree_fails_closed_and_smoke_override_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            ps, simulation = _write_formal_prerequisites(root)
            self.git_state.return_value = {"clean": False, "porcelain": [" M workflow.py"]}
            formal = ExperimentConfig(
                output_root=root / "formal",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                min_predictive_log_score=-5.0,
            )
            with self.assertRaisesRegex(WorkflowError, "worktree is dirty"):
                run_experiment(formal, chain_runner=lambda **_: {}, now=FIXED_NOW, git_sha=GIT_SHA)
            smoke = ExperimentConfig(
                output_root=root / "smoke",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
                allow_dirty_worktree=True,
            )
            output = run_experiment(smoke, chain_runner=lambda **_: {}, now=FIXED_NOW, git_sha=GIT_SHA)
            self.assertTrue((output / "_SUCCESS").is_file())

    def test_holdout_metadata_must_exactly_match_eligible_model_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            rows = metadata.read_text(encoding="utf-8").splitlines()
            metadata.write_text("\n".join(rows[:-1]) + "\n", encoding="utf-8")
            ps, simulation = _write_formal_prerequisites(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                min_predictive_log_score=-5.0,
            )
            with self.assertRaisesRegex(WorkflowError, "exactly match"):
                run_experiment(config, chain_runner=lambda **_: {}, now=FIXED_NOW, git_sha=GIT_SHA)

    def test_failed_run_can_resume_same_run_but_success_cannot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )
            with self.assertRaises(WorkflowError):
                run_experiment(
                    config,
                    chain_runner=mock.Mock(side_effect=RuntimeError("interrupt")),
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            run_dir = next((root / "out").iterdir())
            resumed_calls = []

            def resumed_runner(**kwargs):
                resumed_calls.append(kwargs)
                return {}

            resumed = dataclasses.replace(config, run_id=run_dir.name, resume=True)
            output = run_experiment(resumed, chain_runner=resumed_runner, git_sha=GIT_SHA)
            self.assertEqual(output, run_dir)
            self.assertTrue(any(call["resume"] for call in resumed_calls))
            with self.assertRaisesRegex(WorkflowError, "completed experiment is immutable"):
                run_experiment(resumed, chain_runner=resumed_runner, git_sha=GIT_SHA)

    def test_ess_only_failure_extends_checkpoints_with_bounded_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            ps, simulation = _write_formal_prerequisites(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                min_predictive_log_score=-5.0,
                formal_max_iterations=2_000,
                ess_extension_batch=500,
            )
            calls = []

            def checkpoint_runner(**kwargs):
                calls.append(kwargs)
                chain_dir = Path(kwargs["output_dir"])
                payload = {
                    "config": dataclasses.asdict(kwargs["config"]),
                    "next_iteration": kwargs["config"].iterations,
                }
                with gzip.open(chain_dir / "checkpoint.json.gz", "wt", encoding="utf-8") as handle:
                    json.dump(payload, handle)
                (chain_dir / "chain_complete.json").write_text("{}\n", encoding="utf-8")
                return {}

            ess_failed = _passing_diagnostics()
            ess_failed["min_bulk_ess_total"] = 100.0
            diagnostics = [ess_failed, _passing_diagnostics()]

            def diagnostic_side_effect(_results):
                return diagnostics.pop(0) if diagnostics else _passing_diagnostics()

            with mock.patch(
                "tumor_tree_pipeline.workflow.summarize_chains",
                side_effect=diagnostic_side_effect,
            ):
                output = run_experiment(
                    config,
                    chain_runner=checkpoint_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            extension_calls = [call for call in calls if call["config"].iterations == 2_000]
            self.assertEqual(len(extension_calls), 4)
            self.assertTrue(all(call["resume"] for call in extension_calls))
            ledger = json.loads((output / "command_ledger.json").read_text())["entries"]
            extension_entries = [entry for entry in ledger if entry["action"] == "ess_extension"]
            self.assertEqual(len(extension_entries), 4)
            self.assertTrue(all(entry["from_iterations"] == 1_500 for entry in extension_entries))

    def test_prerequisites_record_ps_and_holdout_hashes_and_dirs_are_group_shared(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, metadata = _write_table_bundle(root)
            ps, simulation = _write_formal_prerequisites(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                holdout_metadata=metadata,
                ps_audit_manifest=ps,
                simulation_manifest=simulation,
                min_predictive_log_score=-5.0,
            )
            with mock.patch(
                "tumor_tree_pipeline.workflow.summarize_chains",
                return_value=_passing_diagnostics(),
            ):
                output = run_experiment(
                    config,
                    chain_runner=lambda **_: {},
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            prerequisites = json.loads((output / "prerequisites.json").read_text())
            self.assertEqual(prerequisites["ps_audit"]["sha256"], hashlib.sha256(ps.read_bytes()).hexdigest())
            self.assertEqual(
                prerequisites["holdout_metadata"]["sha256"],
                hashlib.sha256(metadata.read_bytes()).hexdigest(),
            )
            for directory in [output, output / "holdouts", output / "holdouts" / "ps"]:
                self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o2775)

    def test_provenance_writer_sets_every_created_directory_to_2775(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "one" / "two" / "receipt.txt"
            atomic_write_text(target, "receipt\n")
            self.assertEqual(stat.S_IMODE((root / "one").stat().st_mode), 0o2775)
            self.assertEqual(stat.S_IMODE((root / "one" / "two").stat().st_mode), 0o2775)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o664)


if __name__ == "__main__":
    unittest.main()
