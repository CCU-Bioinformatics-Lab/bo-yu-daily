from __future__ import annotations

import csv
import dataclasses
import hashlib
import json
import os
import signal
import stat
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from tumor_tree_pipeline.contracts import (
    MODEL_INPUT_SCHEMA_VERSION,
    MODEL_REQUIRED_COLUMNS,
    GateThresholds,
)
import tumor_tree_pipeline.workflow as workflow_module
from tumor_tree_pipeline.cli import main as cli_main
from tumor_tree_pipeline.provenance import atomic_write_text
from tumor_tree_pipeline.tests.smc_contract_fixture import (
    assert_smc_artifacts,
    write_synthetic_smc_run,
)
from tumor_tree_pipeline.diagnostics import evaluate_smc_gates
from tumor_tree_pipeline.workflow import (
    ExperimentConfig,
    GateFailure,
    WorkflowError,
    _make_run_id,
    _validate_simulation_gate,
    experiment_matrix,
    load_config,
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
                "ref_reads": 80,
                "alt_reads": 20,
                "total_reads": 100,
                "hp1_1_ref": 10,
                "hp1_1_alt": 4,
                "hp2_1_ref": 11,
                "hp2_1_alt": 3,
                "major_cn": 1,
                "minor_cn": 1,
                "total_cn": 2,
                "rho_ASCAT": 0.99,
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
    simulation.write_text(
        json.dumps(
            {
                "schema": "synthetic_recovery_gate/v1",
                "passed": True,
                "inference_algorithm": "rao_blackwellized_annealed_smc",
                "validation": {"input_schema": MODEL_INPUT_SCHEMA_VERSION},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return ps, simulation


def _passing_smc_diagnostics() -> dict[str, object]:
    return {
        "algorithm": "rao_blackwellized_annealed_smc",
        "sample_semantics": "smc_particle",
        "smc_particle_gate": True,
        "min_conditional_ess_fraction": 0.80,
        "min_weighted_particle_ess_fraction": 0.80,
        "min_particle_diversity": 0.50,
        "min_ancestor_diversity": 0.50,
        "min_eta_acceptance": 0.20,
        "min_topology_acceptance": 0.20,
        "ccf_stability": 0.95,
        "min_assignment_agreement": 0.95,
        "max_edge_support_difference": 0.05,
        "predictive_coverage_by_repeat": [0.90] * 4,
        "predictive_log_score_by_repeat": [-1.0] * 4,
        "min_predictive_log_score": -1.0,
    }


def _fake_smc_payload(*, nodes: int = 6, rows: int = 20) -> dict[str, object]:
    """Return the smallest sampler payload accepted by the SMC workflow."""

    particles = [
        [0.75] + [0.25 / (nodes - 1)] * (nodes - 1),
        [0.70] + [0.30 / (nodes - 1)] * (nodes - 1),
    ]
    return {
        "sample_kind": "smc_particle",
        "prevalence_draws": particles,
        "assignment_map": ["clone_1"] * rows,
        "edge_draws": [[("tumor_root", "node_1")], [("tumor_root", "node_1")]],
        "predictive_coverage": 0.90,
        "predictive_log_score": -1.0,
        "smc_diagnostics": {
            "algorithm": "rao_blackwellized_annealed_smc",
            "annealing": {"final_beta": 1.0},
            "conditional_ess_fraction": 0.80,
            "weighted_particle_ess_fraction": 0.80,
            "particle_diversity": 0.50,
            "ancestor_diversity": 0.50,
            "eta_acceptance": 0.20,
            "topology_acceptance": 0.20,
            "topology_change_rate": 0.20,
            "resampling_count": 1,
            "rejuvenation_sweeps": [3],
        },
    }


class DiagnosticContractTests(unittest.TestCase):
    def test_weighted_particle_ess_is_the_primary_effective_sample_gate(self) -> None:
        passing = _passing_smc_diagnostics()
        self.assertTrue(
            evaluate_smc_gates(passing, GateThresholds(), min_predictive_log_score=-5.0)["passed"]
        )
        low_ess = dict(passing)
        low_ess["min_weighted_particle_ess_fraction"] = 0.49
        self.assertFalse(
            evaluate_smc_gates(low_ess, GateThresholds(), min_predictive_log_score=-5.0)["passed"]
        )
        self.assertNotIn("rhat", json.dumps(passing).lower())
        self.assertNotIn("chain_ess", json.dumps(passing).lower())


class WorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.git_state_patch = mock.patch(
            "tumor_tree_pipeline.workflow._git_worktree_state",
            return_value={"clean": True, "porcelain": []},
        )
        self.git_state = self.git_state_patch.start()
        self.addCleanup(self.git_state_patch.stop)

    def test_formal_synthetic_gate_rejects_retired_input_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "synthetic_gate.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "synthetic_recovery_gate/v1",
                        "passed": True,
                        "inference_algorithm": "rao_blackwellized_annealed_smc",
                        "validation": {"input_schema": "hcc1395_tumor_tree_input/v2"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(WorkflowError, "input schema"):
                _validate_simulation_gate(manifest)

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
                return _fake_smc_payload()

            output = run_experiment(
                config,
                sampler_runner=fake_runner,
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
            self.assertIn("holdout_completed", {event["event"] for event in trace})
            inventory = json.loads((output / "artifact_inventory.json").read_text())
            inventory_paths = {item["path"] for item in inventory["artifacts"]}
            self.assertIn("manifest.json", inventory_paths)
            self.assertNotIn("_SUCCESS", inventory_paths)
            success_before = (output / "_SUCCESS").read_text()
            with self.assertRaises(WorkflowError):
                run_experiment(
                    config,
                    sampler_runner=fake_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            self.assertEqual((output / "_SUCCESS").read_text(), success_before)
            self.assertFalse((output / "_FAILED").exists())

    def test_minimal_smc_fixture_covers_the_complete_output_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = write_synthetic_smc_run(Path(temporary) / "smc")
            diagnostics = assert_smc_artifacts(output)
            self.assertEqual(diagnostics["algorithm"], "rao_blackwellized_annealed_smc")
            self.assertEqual(diagnostics["sample_semantics"], "smc_particle")

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
                return _fake_smc_payload(nodes=kwargs["config"].num_nodes)

            failed = dict(_passing_smc_diagnostics())
            failed["min_weighted_particle_ess_fraction"] = 0.10
            with mock.patch("tumor_tree_pipeline.workflow.summarize_smc_repeats", return_value=failed):
                with self.assertRaises(GateFailure):
                    run_experiment(
                        config,
                        sampler_runner=fake_runner,
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
                return _fake_smc_payload(nodes=kwargs["config"].num_nodes)

            with mock.patch(
                "tumor_tree_pipeline.workflow.summarize_smc_repeats",
                return_value=_passing_smc_diagnostics(),
            ):
                output = run_experiment(
                    config,
                    sampler_runner=fake_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            self.assertTrue((output / "_SUCCESS").is_file())
            self.assertEqual(len(calls), 5 * 3 * 4)
            self.assertEqual({call["holdout_kind"] for call in calls}, {"ps", "chromosome", "ascat_segment"})
            self.assertEqual({call["config"].num_nodes for call in calls}, {4, 6, 8})
            self.assertEqual({call["config"].ascat_purity for call in calls}, {0.99, 0.97, 0.95})
            self.assertTrue(all(call["config"].max_annealing_stages == 64 for call in calls))
            self.assertTrue(all(call["config"].particles == 1_024 for call in calls))
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
                run_experiment(formal, sampler_runner=lambda **_: _fake_smc_payload(), now=FIXED_NOW, git_sha=GIT_SHA)
            smoke = ExperimentConfig(
                output_root=root / "smoke",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
                allow_dirty_worktree=True,
            )
            output = run_experiment(smoke, sampler_runner=lambda **_: _fake_smc_payload(), now=FIXED_NOW, git_sha=GIT_SHA)
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
                run_experiment(config, sampler_runner=lambda **_: _fake_smc_payload(), now=FIXED_NOW, git_sha=GIT_SHA)

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
                    sampler_runner=mock.Mock(side_effect=RuntimeError("interrupt")),
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            run_dir = next((root / "out").iterdir())
            resumed_calls = []

            def resumed_runner(**kwargs):
                resumed_calls.append(kwargs)
                return _fake_smc_payload()

            resumed = dataclasses.replace(config, run_id=run_dir.name, resume=True)
            output = run_experiment(resumed, sampler_runner=resumed_runner, git_sha=GIT_SHA)
            self.assertEqual(output, run_dir)
            self.assertTrue(any(call["resume"] for call in resumed_calls))
            with self.assertRaisesRegex(WorkflowError, "completed experiment is immutable"):
                run_experiment(resumed, sampler_runner=resumed_runner, git_sha=GIT_SHA)

    def test_sigint_writes_interrupted_failure_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )

            def interrupted_runner(**_: object) -> object:
                os.kill(os.getpid(), signal.SIGINT)
                raise AssertionError("SIGINT handler should interrupt the runner")

            with self.assertRaisesRegex(WorkflowError, "SIGINT"):
                run_experiment(
                    config,
                    sampler_runner=interrupted_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            output = next((root / "out").iterdir())
            status = json.loads((output / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["status"], "interrupted")
            self.assertEqual(status["signal"], "SIGINT")
            self.assertEqual(status["context"]["holdout"], "none")
            self.assertEqual(status["context"]["repeat"], 1)
            self.assertIn("seed", status["context"])
            self.assertTrue((output / "_FAILED").is_file())
            self.assertFalse((output / "_SUCCESS").exists())
            trace = [
                json.loads(line)
                for line in (output / "execution_trace.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(trace[-1]["event"], "workflow_interrupted")

    def test_sigterm_writes_interrupted_failure_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )

            def interrupted_runner(**_: object) -> object:
                os.kill(os.getpid(), signal.SIGTERM)
                raise AssertionError("SIGTERM handler should interrupt the runner")

            with self.assertRaisesRegex(WorkflowError, "SIGTERM"):
                run_experiment(
                    config,
                    sampler_runner=interrupted_runner,
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            output = next((root / "out").iterdir())
            status = json.loads((output / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["status"], "interrupted")
            self.assertEqual(status["signal"], "SIGTERM")
            self.assertEqual(status["holdout"], "none")
            self.assertEqual(status["repeat"], 1)
            self.assertIn("seed", status)
            self.assertIn("interrupted_at", status)
            self.assertTrue((output / "_FAILED").is_file())
            self.assertFalse((output / "_SUCCESS").exists())

    def test_resume_rejects_fresh_heartbeat_even_if_process_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )
            run_id = _make_run_id(FIXED_NOW, GIT_SHA, (0.99,), (6,), config.seed)
            output = root / "out" / run_id
            output.mkdir(parents=True)
            (output / "run.lock").touch()
            (output / "status.json").write_text(
                json.dumps({"status": "running", "run_id": run_id}) + "\n",
                encoding="utf-8",
            )
            (output / "heartbeat.json").write_text(
                json.dumps(
                    {
                        "pid": -1,
                        "process_commandline": None,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            resumed = dataclasses.replace(config, run_id=run_id, resume=True)
            with self.assertRaisesRegex(WorkflowError, "heartbeat is not expired"):
                run_experiment(
                    resumed,
                    sampler_runner=lambda **_: _fake_smc_payload(),
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )

    def test_resume_rejects_live_process_with_expired_heartbeat(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )
            run_id = _make_run_id(FIXED_NOW, GIT_SHA, (0.99,), (6,), config.seed)
            output = root / "out" / run_id
            output.mkdir(parents=True)
            (output / "run.lock").touch()
            (output / "status.json").write_text(
                json.dumps({"status": "running", "run_id": run_id}) + "\n",
                encoding="utf-8",
            )
            (output / "heartbeat.json").write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "process_commandline": workflow_module._process_commandline(os.getpid()),
                        "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            resumed = dataclasses.replace(config, run_id=run_id, resume=True)
            with self.assertRaisesRegex(WorkflowError, "process is still alive"):
                run_experiment(
                    resumed,
                    sampler_runner=lambda **_: _fake_smc_payload(),
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )

    def test_resume_marks_expired_dead_run_stale_before_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )
            run_id = _make_run_id(FIXED_NOW, GIT_SHA, (0.99,), (6,), config.seed)
            output = root / "out" / run_id
            output.mkdir(parents=True)
            (output / "run.lock").touch()
            (output / "status.json").write_text(
                json.dumps({"status": "running", "run_id": run_id}) + "\n",
                encoding="utf-8",
            )
            (output / "heartbeat.json").write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "process_commandline": "not-this-process",
                        "updated_at": (FIXED_NOW - timedelta(minutes=10)).isoformat(),
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            resumed = dataclasses.replace(config, run_id=run_id, resume=True)
            recovered = run_experiment(
                resumed,
                sampler_runner=lambda **_: _fake_smc_payload(),
                now=FIXED_NOW,
                git_sha=GIT_SHA,
            )
            self.assertEqual(recovered, output)
            self.assertTrue((output / "_SUCCESS").is_file())
            stale_receipts = list((output / "logs").glob("_FAILED.before_resume.*"))
            self.assertEqual(len(stale_receipts), 1)
            self.assertIn("stale", stale_receipts[0].read_text(encoding="utf-8"))

    def test_quick_pilot_config_is_one_k_and_one_repeat(self) -> None:
        config = load_config(Path("tumor_tree_pipeline/configs/pilot.quick.active.json"))
        cells = experiment_matrix(config)
        self.assertEqual([(cell.stage, cell.num_nodes) for cell in cells], [("pilot", 6)])
        self.assertEqual(config.pilot_repeats, 1)
        self.assertEqual(config.pilot_particles, 64)
        self.assertEqual(config.max_annealing_stages, 16)

    def test_success_publication_ignores_signal_until_marker_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )
            real_atomic_write = workflow_module._atomic_write

            def interrupt_during_marker(path: Path, text: str) -> None:
                if path.name == "_SUCCESS":
                    os.kill(os.getpid(), signal.SIGINT)
                real_atomic_write(path, text)

            with mock.patch.object(workflow_module, "_atomic_write", side_effect=interrupt_during_marker):
                output = run_experiment(
                    config,
                    sampler_runner=lambda **_: _fake_smc_payload(),
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            self.assertTrue((output / "_SUCCESS").is_file())
            self.assertFalse((output / "_FAILED").exists())

    def test_signal_after_success_marker_does_not_create_failed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            table, manifest, _ = _write_table_bundle(root)
            config = ExperimentConfig(
                output_root=root / "out",
                table_path=table,
                validation_manifest=manifest,
                mode="smoke",
            )
            real_signal = workflow_module.signal.signal
            real_atomic_write = workflow_module._atomic_write
            state = {"marker_written": False, "signal_sent": False}

            def atomic_write(path: Path, text: str) -> None:
                real_atomic_write(path, text)
                if path.name == "_SUCCESS":
                    state["marker_written"] = True

            def signal_spy(signum: int, handler: object) -> object:
                result = real_signal(signum, handler)
                if (
                    state["marker_written"]
                    and not state["signal_sent"]
                    and handler is not workflow_module.signal.SIG_IGN
                ):
                    state["signal_sent"] = True
                    os.kill(os.getpid(), signal.SIGINT)
                return result

            with (
                mock.patch.object(workflow_module, "_atomic_write", side_effect=atomic_write),
                mock.patch.object(workflow_module.signal, "signal", side_effect=signal_spy),
            ):
                output = run_experiment(
                    config,
                    sampler_runner=lambda **_: _fake_smc_payload(),
                    now=FIXED_NOW,
                    git_sha=GIT_SHA,
                )
            self.assertTrue(state["signal_sent"])
            self.assertTrue((output / "_SUCCESS").is_file())
            self.assertFalse((output / "_FAILED").exists())

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
                "tumor_tree_pipeline.workflow.summarize_smc_repeats",
                return_value=_passing_smc_diagnostics(),
            ):
                output = run_experiment(
                    config,
                    sampler_runner=lambda **_: _fake_smc_payload(),
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
