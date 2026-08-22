from __future__ import annotations

import csv
import gzip
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tumor_tree_pipeline.contracts import MODEL_REQUIRED_COLUMNS
from tumor_tree_pipeline.model import (
    CanonicalInputError,
    bulk_log_likelihood,
    compile_model,
    likelihood_matrix,
    load_model_table,
    logsumexp,
    site_log_likelihood,
    site_multiplicity_posterior,
)


def canonical_row(index: int = 1, *, purity: float = 0.99) -> dict[str, str]:
    ref_reads = 24 + index
    alt_reads = 6 + index
    return {
        "mutation_id": f"chr1:{100 + index}:A>T",
        "chrom": "chr1",
        "pos": str(100 + index),
        "ref": "A",
        "alt": "T",
        "ref_reads": str(ref_reads),
        "alt_reads": str(alt_reads),
        "total_reads": str(ref_reads + alt_reads),
        "hp1_1_ref": str(3 + index % 2),
        "hp1_1_alt": str(2 + index % 3),
        "hp2_1_ref": str(4 + index % 3),
        "hp2_1_alt": "1",
        "major_cn": "3",
        "minor_cn": "1",
        "total_cn": "4",
        "rho_ASCAT": str(purity),
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


class CanonicalModelContracts(unittest.TestCase):
    def test_loader_rejects_pre_v4_bulk_column_names(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pre_v4.tsv.gz"
            row = canonical_row()
            row["bulk_ref"] = row.pop("ref_reads")
            row["bulk_alt"] = row.pop("alt_reads")
            row["bulk_depth"] = row.pop("total_reads")
            old_names = {
                "ref_reads": "bulk_ref",
                "alt_reads": "bulk_alt",
                "total_reads": "bulk_depth",
            }
            fields = [old_names.get(field, field) for field in MODEL_REQUIRED_COLUMNS]
            write_table(path, [row], fields=fields)
            with self.assertRaisesRegex(CanonicalInputError, "missing required columns"):
                load_model_table(path, 0.99)

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

            old_multiplicity = root / "old_multiplicity.tsv.gz"
            fields = list(MODEL_REQUIRED_COLUMNS) + [
                "multiplicity_candidates",
                "multiplicity_prior",
            ]
            row = canonical_row()
            row["multiplicity_candidates"] = "1;2;3"
            row["multiplicity_prior"] = "1=0.6666666667;2=0.1666666667;3=0.1666666666"
            write_table(old_multiplicity, [row], fields=fields)
            with self.assertRaisesRegex(CanonicalInputError, "forbidden legacy columns"):
                load_model_table(old_multiplicity, 0.99)

    def test_loader_derives_cn_only_multiplicity_prior_before_likelihood(self):
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
            self.assertEqual(site.multiplicities, (1.0, 2.0, 3.0))
            self.assertAlmostEqual(site.multiplicity_prior[0], 2.0 / 3.0)
            self.assertAlmostEqual(site.multiplicity_prior[1], 1.0 / 6.0)
            self.assertAlmostEqual(site.multiplicity_prior[2], 1.0 / 6.0)
            phi = 0.43
            posterior = site_multiplicity_posterior(site, phi)
            self.assertAlmostEqual(sum(posterior), 1.0, places=12)
            self.assertTrue(all(0.0 <= value <= 1.0 for value in posterior))
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

    def test_vectorized_production_likelihood_matches_scalar_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canonical.tsv.gz"
            write_table(path, [canonical_row(index) for index in range(1, 5)])
            data = load_model_table(path, 0.99)
            phi = [0.2, 0.7]
            scalar = np.asarray(likelihood_matrix(data, phi))
            vectorized = compile_model(data).likelihood_matrix(phi)
            np.testing.assert_allclose(vectorized, scalar, rtol=0.0, atol=1e-10)


if __name__ == "__main__":
    unittest.main()
