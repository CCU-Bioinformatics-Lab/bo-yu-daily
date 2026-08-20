"""Executable contracts for the canonical tumor-tree input bundle."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tumor_tree_pipeline.contracts import (
    MODEL_FORBIDDEN_COLUMNS,
    MODEL_REQUIRED_COLUMNS,
    BuildInputs,
    PuritySpec,
)
from tumor_tree_pipeline.input_table import (
    build_model_table,
    multiplicity_prior,
    parse_prior,
)
from tumor_tree_pipeline.provenance import (
    atomic_write_gzip_tsv,
    audit_ps_site,
    normalize_ascat_segments,
    project_sites_to_ascat,
    read_tsv,
    sha256_file,
    summarize_ps_audit,
)


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "hcc1395_tp20_v1"


class InputContractTests(unittest.TestCase):
    def build(self, outdir: Path, *, fixture: Path = FIXTURE, purity: float = 0.99):
        inputs = BuildInputs(
            counts_dir=fixture / "counts",
            site_cnv_qc=fixture / "site_cnv_qc.tsv.gz",
            purity=PuritySpec(purity, fixture / "purity_ploidy.txt"),
            expected_sites=20,
        )
        return build_model_table(
            inputs,
            outdir,
            command=("tumor-tree-input", "--fixture", "hcc1395_tp20_v1"),
        )

    def test_cn_only_hierarchical_prior_has_equal_side_mass(self):
        prior = multiplicity_prior(3, 1)
        self.assertEqual(set(prior), {1, 2, 3})
        self.assertAlmostEqual(prior[1], 2.0 / 3.0)
        self.assertAlmostEqual(prior[2], 1.0 / 6.0)
        self.assertAlmostEqual(prior[3], 1.0 / 6.0)
        self.assertEqual(multiplicity_prior(3, 0), {1: 1 / 3, 2: 1 / 3, 3: 1 / 3})

    def test_fixture_build_is_20_rows_with_16_eligible_and_no_posterior(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self.build(Path(temporary) / "bundle")
            rows = read_tsv(result.table)
            qa = json.loads(result.qa.read_text())
            self.assertEqual(result.rows, 20)
            self.assertEqual(result.eligible_rows, 16)
            self.assertEqual(qa["status"], "pass")
            self.assertEqual(
                qa["model_status_counts"],
                {
                    "eligible": 16,
                    "excluded_cn_zero": 2,
                    "excluded_unmapped_segment": 2,
                },
            )
            self.assertTrue(set(MODEL_REQUIRED_COLUMNS).issubset(rows[0]))
            self.assertFalse(set(MODEL_FORBIDDEN_COLUMNS) & set(rows[0]))
            self.assertNotIn("ps", MODEL_REQUIRED_COLUMNS)
            self.assertTrue(all(float(row["rho_ASCAT"]) == 0.99 for row in rows))
            excluded = [row for row in rows if row["model_include"] == "no"]
            self.assertTrue(all(not row["multiplicity_prior"] for row in excluded))
            for row in rows:
                if row["major_cn"] == "3" and row["minor_cn"] == "1":
                    prior = parse_prior(row["multiplicity_prior"])
                    self.assertAlmostEqual(prior[1], 2 / 3, places=10)
                    self.assertAlmostEqual(prior[2], 1 / 6, places=10)
                    self.assertAlmostEqual(prior[3], 1 / 6, places=10)
                    break
            else:
                self.fail("fixture lacks the major=3/minor=1 contract case")

    def test_manifest_records_command_schema_sources_outputs_and_purity(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self.build(Path(temporary) / "bundle")
            manifest = json.loads(result.manifest.read_text())
            self.assertEqual(manifest["status"], "pass")
            self.assertEqual(
                manifest["command"]["argv"],
                ["tumor-tree-input", "--fixture", "hcc1395_tp20_v1"],
            )
            self.assertEqual(manifest["purity"]["value"], 0.99)
            self.assertEqual(manifest["purity"]["parameter"], "rho_ASCAT")
            self.assertFalse(manifest["ps"]["active_model_input"])
            self.assertEqual(
                manifest["outputs"]["likelihood_input"]["sha256"],
                sha256_file(result.table),
            )
            self.assertEqual(
                manifest["outputs"]["input_qa"]["sha256"],
                sha256_file(result.qa),
            )
            self.assertIn("site_cnv_qc", manifest["sources"])
            self.assertIn("implementation_sha256", manifest["software"])

    def test_completed_input_bundle_is_immutable(self):
        with tempfile.TemporaryDirectory() as temporary:
            outdir = Path(temporary) / "bundle"
            self.build(outdir)
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                self.build(outdir)

    def test_purity_spec_must_match_the_ascat_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "does not match ASCAT purity file"):
                self.build(Path(temporary) / "bundle", purity=0.95)

    def test_count_conservation_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "fixture"
            shutil.copytree(FIXTURE, copied)
            bulk_path = copied / "counts" / "snv_bulk_counts.tsv.gz"
            rows = read_tsv(bulk_path)
            fields = list(rows[0])
            rows[0]["bulk_usable_depth"] = str(int(rows[0]["bulk_usable_depth"]) + 1)
            atomic_write_gzip_tsv(bulk_path, rows, fields)
            with self.assertRaisesRegex(ValueError, "bulk count conservation failed"):
                self.build(Path(temporary) / "bundle", fixture=copied)

    def test_ps_audit_is_qc_metadata_not_a_model_field(self):
        site = read_tsv(FIXTURE / "counts" / "snv_bulk_counts.tsv.gz")[0]
        ps = site["ps"]
        audit = audit_ps_site(
            {"mutation_id": f"{site['chrom']}:{site['pos']}", "vcf_ps": ps},
            [
                {"query_name": "alt-1", "allele": "alt", "ps": ps},
                {"query_name": "alt-1", "allele": "alt", "ps": "duplicate"},
                {"query_name": "ref-1", "allele": "ref", "ps": ps},
            ],
        )
        self.assertEqual(audit["status"], "match_alt")
        self.assertEqual(audit["duplicate_query_name"], 1)
        summary = summarize_ps_audit([audit])
        self.assertEqual(summary["status"], "pass")
        self.assertEqual(
            summary["model_role"], "provenance_qc_and_grouped_holdout_only"
        )
        self.assertNotIn("ps", MODEL_REQUIRED_COLUMNS)

    def test_ascat_projection_is_one_based_inclusive_and_does_not_impute(self):
        fixture_rows = read_tsv(FIXTURE / "site_cnv_qc.tsv.gz")
        mapped = next(row for row in fixture_rows if row["cnv_status"] == "mapped_nonzero_cn")
        unmapped = next(row for row in fixture_rows if row["cnv_status"] == "unmapped_segment")
        pos = int(mapped["pos"])
        segments = normalize_ascat_segments(
            [
                {
                    "sample": "HCC1395_fixture",
                    "chr": mapped["chrom"],
                    "startpos": pos,
                    "endpos": pos + 10,
                    "nMajor": mapped["major_cn"],
                    "nMinor": mapped["minor_cn"],
                }
            ]
        )
        projected = project_sites_to_ascat(
            [
                {key: mapped[key] for key in ("chrom", "pos", "ref", "alt")},
                {key: unmapped[key] for key in ("chrom", "pos", "ref", "alt")},
            ],
            segments,
        )
        self.assertEqual(projected[0]["cnv_status"], "mapped_nonzero_cn")
        self.assertEqual(projected[0]["pos"], pos)
        self.assertEqual(projected[1]["cnv_status"], "unmapped_segment")
        self.assertEqual(projected[1]["total_cn"], "")

    def test_checked_in_fixture_has_fixed_selection_and_required_strata(self):
        manifest = json.loads((FIXTURE / "fixture_manifest.json").read_text())
        self.assertEqual(manifest["fixture"], "hcc1395_tp20_v1")
        self.assertEqual(manifest["selection_seed"], "hcc1395_tp20_v1")
        self.assertEqual(len(manifest["mutation_ids"]), 20)
        self.assertEqual(len(set(manifest["mutation_ids"])), 20)
        observed_features = {
            feature
            for selection in manifest["selection"]
            for feature in selection["strata"]
        }
        self.assertTrue(
            set(manifest["required_eligible_features"]).issubset(observed_features)
        )
        self.assertFalse(manifest["bam_read_required"])


if __name__ == "__main__":
    unittest.main()
