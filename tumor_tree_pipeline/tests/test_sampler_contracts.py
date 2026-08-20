from __future__ import annotations

import csv
import gzip
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from tumor_tree_pipeline.contracts import ChainConfig, MODEL_REQUIRED_COLUMNS
from tumor_tree_pipeline.model import (
    CanonicalInputError,
    bulk_log_likelihood,
    compile_model,
    likelihood_matrix,
    load_model_table,
    logsumexp,
    site_log_likelihood,
)
from tumor_tree_pipeline import sampler


def canonical_row(index: int = 1, *, purity: float = 0.99) -> dict[str, str]:
    bulk_ref = 24 + index
    bulk_alt = 6 + index
    return {
        "mutation_id": f"chr1:{100 + index}:A>T",
        "chrom": "chr1",
        "pos": str(100 + index),
        "ref": "A",
        "alt": "T",
        "bulk_ref": str(bulk_ref),
        "bulk_alt": str(bulk_alt),
        "bulk_depth": str(bulk_ref + bulk_alt),
        "hp1_1_ref": str(3 + index % 2),
        "hp1_1_alt": str(2 + index % 3),
        "hp2_1_ref": str(4 + index % 3),
        "hp2_1_alt": "1",
        "major_cn": "3",
        "minor_cn": "1",
        "total_cn": "4",
        "rho_ASCAT": str(purity),
        "multiplicity_candidates": "1;2;3",
        "multiplicity_prior": "1=0.6666666667;2=0.1666666667;3=0.1666666666",
        "model_include": "yes",
        "model_status": "eligible",
    }


def write_table(
    path: Path,
    rows: list[dict[str, str]],
    *,
    fields: list[str] | None = None,
) -> None:
    fields = fields or list(MODEL_REQUIRED_COLUMNS)
    opener = gzip.open if path.suffix == ".gz" else path.open
    if path.suffix == ".gz":
        handle = opener(path, "wt", newline="")
    else:
        handle = opener("w", newline="")
    with handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


class CanonicalSamplerContracts(unittest.TestCase):
    def test_loader_has_no_missing_file_or_schema_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                load_model_table(root / "absent.tsv.gz", 0.99)

            missing_cn = root / "missing_total_cn.tsv.gz"
            fields = [field for field in MODEL_REQUIRED_COLUMNS if field != "total_cn"]
            write_table(missing_cn, [canonical_row()], fields=fields)
            with self.assertRaisesRegex(CanonicalInputError, "total_cn"):
                load_model_table(missing_cn, 0.99)

            forbidden = root / "posterior.tsv.gz"
            fields = list(MODEL_REQUIRED_COLUMNS) + ["multiplicity_posteriors"]
            row = canonical_row()
            row["multiplicity_posteriors"] = "1=1"
            write_table(forbidden, [row], fields=fields)
            with self.assertRaisesRegex(CanonicalInputError, "forbidden legacy columns"):
                load_model_table(forbidden, 0.99)

    def test_bulk_counts_enter_once_under_cn_only_multiplicity_prior(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canonical.tsv.gz"
            row = canonical_row()
            row.update(
                {
                    "hp1_1_ref": "0",
                    "hp1_1_alt": "0",
                    "hp2_1_ref": "0",
                    "hp2_1_alt": "0",
                    # Extra PS metadata is accepted but not loaded.
                    "ps": "123456",
                }
            )
            write_table(path, [row], fields=list(MODEL_REQUIRED_COLUMNS) + ["ps"])
            data = load_model_table(path, 0.99)
            site = data.sites[0]
            phi = 0.43
            expected = logsumexp(
                [
                    math.log(probability) + bulk_log_likelihood(site, phi, multiplicity)
                    for multiplicity, probability in zip(
                        site.multiplicities, site.multiplicity_prior
                    )
                ]
            )
            self.assertAlmostEqual(site_log_likelihood(site, phi), expected, places=10)
            self.assertFalse(hasattr(site, "ps"))

    def test_eta_root_is_tumor_residual_and_not_one_minus_purity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canonical.tsv.gz"
            write_table(path, [canonical_row(index) for index in range(1, 5)])
            compiled = compile_model(load_model_table(path, 0.99))
            parents, eta, _ = sampler._initial_state(compiled, 2)
            self.assertAlmostEqual(float(eta[0]), 0.10)
            self.assertNotAlmostEqual(float(eta[0]), 1.0 - 0.99)
            self.assertAlmostEqual(float(eta.sum()), 1.0)
            self.assertTrue(np.all(sampler.cumulative_phi(parents, eta) <= 1.0))

    def test_initial_state_has_only_tree_population_and_site_assignments(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canonical.tsv.gz"
            write_table(path, [canonical_row(index) for index in range(1, 7)])
            compiled = compile_model(load_model_table(path, 0.99))

            state = sampler._initial_state(compiled, 6)

            self.assertEqual(len(state), 3)
            parents, eta, z = state
            self.assertEqual(len(parents), 6)
            self.assertEqual(len(eta), 7)
            self.assertEqual(len(z), len(compiled.data.sites))
            self.assertAlmostEqual(float(eta.sum()), 1.0)
            self.assertTrue(np.issubdtype(np.asarray(z).dtype, np.integer))

    def test_vectorized_production_likelihood_matches_scalar_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canonical.tsv.gz"
            write_table(path, [canonical_row(index) for index in range(1, 5)])
            data = load_model_table(path, 0.99)
            phi = [0.2, 0.7]
            scalar = np.asarray(likelihood_matrix(data, phi))
            vectorized = compile_model(data).likelihood_matrix(phi)
            np.testing.assert_allclose(vectorized, scalar, rtol=0.0, atol=1e-10)

    def test_run_chain_writes_required_outputs_and_completed_dir_is_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            table = root / "canonical.tsv.gz"
            write_table(table, [canonical_row(index) for index in range(1, 7)])
            outdir = root / "chain"
            config = ChainConfig(
                seed=7,
                num_nodes=2,
                iterations=8,
                burnin=2,
                thin=1,
                ascat_purity=0.99,
                checkpoint_every=2,
            )
            result = sampler.run_chain(table, outdir, config)
            self.assertEqual(result.posterior_samples, 6)
            self.assertTrue((outdir / "samples.jsonl.gz").is_file())
            self.assertTrue((outdir / "diagnostics.json").is_file())
            self.assertTrue((outdir / "representative_tree.json").is_file())
            self.assertTrue((outdir / "checkpoint.json.gz").is_file())
            self.assertTrue((outdir / "chain_complete.json").is_file())

            with gzip.open(outdir / "checkpoint.json.gz", "rt", encoding="utf-8") as handle:
                checkpoint = json.load(handle)
            self.assertGreaterEqual(int(checkpoint["checkpoint_version"]), 2)
            self.assertTrue({"parents", "eta", "z"}.issubset(checkpoint))
            self.assertFalse(
                {"assignment_weights", "reference_eta", "initialization"}.intersection(checkpoint)
            )

            diagnostics = json.loads((outdir / "diagnostics.json").read_text(encoding="utf-8"))
            self.assertEqual(diagnostics["model"], "finite_K_metropolis_hastings")
            self.assertEqual(
                set(diagnostics["counters"]),
                {
                    "assignment_proposals",
                    "assignment_accepted",
                    "eta_proposals",
                    "eta_accepted",
                    "topology_proposals",
                    "topology_accepted",
                },
            )
            self.assertEqual(
                sum(diagnostics["counters"][name] for name in (
                    "assignment_proposals",
                    "eta_proposals",
                    "topology_proposals",
                )),
                config.iterations,
            )
            self.assertNotIn("eta_bridge_acceptance", diagnostics)
            self.assertNotIn("eta_bridge_proposals", diagnostics)
            self.assertNotIn("eta_bridge_accepted", diagnostics)
            self.assertNotIn("gibbs", json.dumps(diagnostics).lower())

            with gzip.open(outdir / "samples.jsonl.gz", "rt", encoding="utf-8") as handle:
                sample = json.loads(next(handle))
            self.assertTrue({"parents", "eta", "phi", "occupancy"}.issubset(sample))
            self.assertNotIn("assignment_weights", sample)
            self.assertNotIn("reference_eta", sample)
            with self.assertRaisesRegex(FileExistsError, "immutable"):
                sampler.run_chain(table, outdir, config)
            with self.assertRaisesRegex(FileExistsError, "immutable"):
                sampler.run_chain(table, outdir, config, resume=True)

    def test_atomic_checkpoint_resume_matches_uninterrupted_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            table = root / "canonical.tsv.gz"
            write_table(table, [canonical_row(index) for index in range(1, 7)])
            config = ChainConfig(
                seed=17,
                num_nodes=2,
                iterations=10,
                burnin=2,
                thin=1,
                ascat_purity=0.99,
                checkpoint_every=2,
            )
            clean = root / "clean"
            sampler.run_chain(table, clean, config)

            interrupted = root / "interrupted"
            real_checkpoint = sampler._write_checkpoint_atomic

            def write_then_interrupt(path, payload):
                real_checkpoint(path, payload)
                if payload["next_iteration"] == 2:
                    raise RuntimeError("simulated interruption")

            with mock.patch.object(
                sampler, "_write_checkpoint_atomic", side_effect=write_then_interrupt
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                    sampler.run_chain(table, interrupted, config)

            resumed = sampler.run_chain(table, interrupted, config, resume=True)
            self.assertTrue(resumed.resumed)
            with gzip.open(clean / "samples.jsonl.gz", "rt") as handle:
                clean_samples = handle.read()
            with gzip.open(interrupted / "samples.jsonl.gz", "rt") as handle:
                resumed_samples = handle.read()
            self.assertEqual(resumed_samples, clean_samples)


if __name__ == "__main__":
    unittest.main()
