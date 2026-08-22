#!/usr/bin/env python3
"""Black-box contract tests for the C++ inference executable.

The tests intentionally use only the Python standard library. They exercise
the executable through its CLI and inspect only the public input/output
contract; no C++ implementation details are imported.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "hcc1395_tumor_tree_input/v4"
REQUIRED_COLUMNS = (
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

ARTIFACTS = (
    "samples.jsonl.gz",
    "multiplicity_posterior.tsv.gz",
    "diagnostics.json",
    "representative_tree.json",
    "checkpoint.json.gz",
    "chain_complete.json",
)


class ContractFailure(AssertionError):
    """A user-facing contract assertion with command context."""


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ContractFailure(message)


def write_tsv(path: Path, rows: list[dict[str, str]], fields: Iterable[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fields),
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def fixture_rows(*, hp_shift: int = 0, purity: str = "0.99") -> list[dict[str, str]]:
    """Return a small valid table with all active observation columns.

    The alternate HP layout is used to detect an implementation that accepts
    HP columns syntactically but silently omits them from the likelihood.
    """

    rows: list[dict[str, str]] = []
    for index in range(1, 7):
        ref_reads = 22 + index
        alt_reads = 8 + (index % 3)
        hp1_ref = 3 + (index % 2)
        hp1_alt = 2 + (index % 3)
        hp2_ref = 2 + ((index + 1) % 2)
        hp2_alt = 1 + (index % 2)
        if hp_shift:
            # Change the observed REF/ALT evidence, rather than merely
            # swapping HP labels (the likelihood may marginalize HP side).
            hp1_ref -= hp_shift
            hp1_alt += hp_shift
        rows.append(
            {
                "mutation_id": f"chr1:{1000 + index}:A>T",
                "chrom": "chr1",
                "pos": str(1000 + index),
                "ref": "A",
                "alt": "T",
                "ref_reads": str(ref_reads),
                "alt_reads": str(alt_reads),
                "total_reads": str(ref_reads + alt_reads),
                "hp1_1_ref": str(hp1_ref),
                "hp1_1_alt": str(hp1_alt),
                "hp2_1_ref": str(hp2_ref),
                "hp2_1_alt": str(hp2_alt),
                "major_cn": "3",
                "minor_cn": "1",
                "total_cn": "4",
                "rho_ASCAT": purity,
                "model_include": "yes",
                "model_status": "eligible",
            }
        )
    return rows


def invoke(
    binary: Path,
    *,
    input_path: Path,
    output_path: Path,
    seed: int = 20260820,
    chains: int = 1,
    threads: int = 1,
    rho_ascat: str = "0.99",
    algorithm: str = "phylowgs_inspired_tssb_mcmc",
) -> subprocess.CompletedProcess[str]:
    command = [
        str(binary),
        "run",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--algorithm",
        algorithm,
        "--seed",
        str(seed),
        "--chains",
        str(chains),
        "--threads",
        str(threads),
        "--iterations",
        "24",
        "--burnin",
        "8",
        "--thin",
        "1",
        "--num-nodes",
        "2",
        "--rho-ascat",
        rho_ascat,
    ]
    return subprocess.run(command, text=True, capture_output=True, check=False)


def assert_success(result: subprocess.CompletedProcess[str], context: str) -> None:
    check(
        result.returncode == 0,
        f"{context} failed with exit {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
    )


def assert_failure(result: subprocess.CompletedProcess[str], context: str) -> None:
    check(
        result.returncode != 0,
        f"{context} unexpectedly succeeded\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
    )


def read_json(path: Path) -> dict[str, Any]:
    check(path.is_file(), f"missing JSON artifact: {path}")
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    check(isinstance(value, dict), f"JSON artifact is not an object: {path}")
    return value


def read_gzip_json(path: Path) -> dict[str, Any]:
    check(path.is_file(), f"missing JSON artifact: {path}")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    check(isinstance(value, dict), f"gzip JSON artifact is not an object: {path}")
    return value


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    check(path.is_file(), f"missing JSONL artifact: {path}")
    records: list[dict[str, Any]] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ContractFailure(
                    f"invalid JSONL at {path}:{line_number}: {exc}"
                ) from exc
            check(isinstance(value, dict), f"JSONL record is not an object: {path}:{line_number}")
            records.append(value)
    check(records, f"samples artifact is empty: {path}")
    check(
        all(isinstance(record.get("log_posterior"), (int, float)) for record in records),
        f"samples do not expose numeric log_posterior values: {path}",
    )
    return records


def decompressed_bytes(path: Path) -> bytes:
    with gzip.open(path, "rb") as handle:
        return handle.read()


def assert_chain_artifacts(chain_dir: Path, *, expected_sites: int = 6) -> dict[str, Any]:
    for artifact in ARTIFACTS:
        check((chain_dir / artifact).is_file(), f"missing {artifact} in {chain_dir}")

    diagnostics = read_json(chain_dir / "diagnostics.json")
    completion = read_json(chain_dir / "chain_complete.json")
    tree = read_json(chain_dir / "representative_tree.json")
    read_gzip_json(chain_dir / "checkpoint.json.gz")
    samples = read_jsonl_gz(chain_dir / "samples.jsonl.gz")
    with gzip.open(chain_dir / "multiplicity_posterior.tsv.gz", "rt", encoding="utf-8") as handle:
        posterior_lines = [line.rstrip("\n") for line in handle if line.strip()]
    check(
        posterior_lines
        and posterior_lines[0] == "mutation_id\tmultiplicity\tprior\tposterior_mean",
        "multiplicity posterior artifact has the wrong header",
    )
    posterior_by_site: dict[str, float] = {}
    for line in posterior_lines[1:]:
        fields = line.split("\t")
        check(len(fields) == 4, "multiplicity posterior row has the wrong field count")
        posterior_by_site[fields[0]] = posterior_by_site.get(fields[0], 0.0) + float(fields[3])
    check(posterior_by_site, "multiplicity posterior artifact is empty")
    check(
        all(abs(value - 1.0) < 1e-9 for value in posterior_by_site.values()),
        "multiplicity posterior probabilities do not normalize per SNV",
    )

    algorithm = str(diagnostics.get("algorithm", ""))
    model = str(diagnostics.get("model", ""))
    check(
        "phylowgs_inspired_tssb_mcmc" in algorithm,
        f"diagnostics do not identify the PhyloWGS-inspired sampler: {chain_dir}",
    )
    check(diagnostics.get("input_schema") == SCHEMA_VERSION, "input schema is not recorded")
    check(diagnostics.get("observed_sites") == expected_sites, "observed site count is wrong")
    check(
        diagnostics.get("state_variables") == ["parents", "eta", "z"],
        "the sampler state must be parents/eta/z",
    )
    config = diagnostics.get("config")
    check(isinstance(config, dict), "diagnostics.config is missing")
    check(config.get("ascat_purity") == 0.99, "diagnostics did not record rho_ASCAT=0.99")
    phi_mean = diagnostics.get("phi_mean")
    check(
        isinstance(phi_mean, list)
        and len(phi_mean) == config.get("num_nodes")
        and all(isinstance(value, (int, float)) for value in phi_mean),
        "diagnostics.phi_mean is missing or has the wrong shape",
    )
    target = diagnostics.get("target")
    check(isinstance(target, dict), "diagnostics.target is missing")
    check(
        "CN_constrained_multiplicity_candidates_marginalized_with_emission_posterior"
        in str(target.get("site_terms", "")),
        "CN-constrained multiplicity posterior is not recorded as the site likelihood term",
    )
    check(
        diagnostics.get("multiplicity_role")
        == "CN_constrained_latent_state_with_per_site_posterior; not_a_table_column",
        "diagnostics do not record model-owned multiplicity posterior derivation",
    )
    check(
        set(diagnostics.get("counters", {}))
        == {
            "assignment_accepted",
            "assignment_proposals",
            "eta_accepted",
            "eta_proposals",
            "topology_accepted",
            "topology_proposals",
        },
        "sampler counters contain an unexpected move field",
    )
    check(completion.get("status") == "complete", "chain completion status is not complete")
    check(
        "multiplicity_posterior.tsv.gz" in completion.get("artifacts", []),
        "completion manifest does not list multiplicity posterior output",
    )
    check(tree.get("model") == diagnostics.get("model"), "tree/model contract mismatch")
    check(len(samples) > 0, "no retained posterior samples")
    return diagnostics


def assert_failed_output_is_not_complete(path: Path) -> None:
    if not path.exists():
        return
    check(
        not list(path.glob("**/chain_complete.json")),
        f"failed invocation left a completed output behind: {path}",
    )


def test_valid_input_and_hp_likelihood(binary: Path, root: Path) -> None:
    canonical = root / "canonical.tsv"
    shifted = root / "canonical_hp_shift.tsv"
    write_tsv(canonical, fixture_rows(), REQUIRED_COLUMNS)
    write_tsv(shifted, fixture_rows(hp_shift=1), REQUIRED_COLUMNS)

    baseline = root / "baseline"
    changed_hp = root / "changed_hp"
    assert_success(
        invoke(binary, input_path=canonical, output_path=baseline),
        "valid canonical TSV",
    )
    assert_success(
        invoke(binary, input_path=shifted, output_path=changed_hp),
        "canonical TSV with changed HP evidence",
    )
    assert_chain_artifacts(baseline)
    assert_chain_artifacts(changed_hp)

    baseline_scores = [
        record["log_posterior"]
        for record in read_jsonl_gz(baseline / "samples.jsonl.gz")
    ]
    changed_scores = [
        record["log_posterior"]
        for record in read_jsonl_gz(changed_hp / "samples.jsonl.gz")
    ]
    check(
        baseline_scores != changed_scores,
        "changing HP1-1/HP2-1 counts did not change the posterior trace; "
        "HP columns may be ignored by the likelihood",
    )


def test_thread_policy(binary: Path, root: Path) -> None:
    canonical = root / "canonical_threads.tsv"
    write_tsv(canonical, fixture_rows(), REQUIRED_COLUMNS)
    one = root / "threads_1"
    two = root / "threads_2"
    assert_success(
        invoke(binary, input_path=canonical, output_path=one, threads=1),
        "threads=1",
    )
    assert_success(
        invoke(binary, input_path=canonical, output_path=two, threads=2),
        "threads=2",
    )
    diag_one = assert_chain_artifacts(one)
    diag_two = assert_chain_artifacts(two)
    # Retained posterior samples are the deterministic cross-thread contract.
    # Checkpoint is an audit/state snapshot and must not be compared byte-for-
    # byte because runtime metadata may legitimately differ.
    check(
        decompressed_bytes(one / "samples.jsonl.gz")
        == decompressed_bytes(two / "samples.jsonl.gz"),
        "threads=1 and threads=2 changed retained posterior samples",
    )
    check(
        diag_one.get("config", {}).get("seed") == diag_two.get("config", {}).get("seed"),
        "thread comparison changed the requested seed",
    )


def test_multiple_chains_have_distinct_seeded_outputs(binary: Path, root: Path) -> None:
    canonical = root / "canonical_chains.tsv"
    output = root / "chains_2"
    write_tsv(canonical, fixture_rows(), REQUIRED_COLUMNS)
    assert_success(
        invoke(binary, input_path=canonical, output_path=output, chains=2, threads=2),
        "chains=2",
    )
    chain_one = output / "chain_01"
    chain_two = output / "chain_02"
    diag_one = assert_chain_artifacts(chain_one)
    diag_two = assert_chain_artifacts(chain_two)
    seed_one = diag_one.get("derived_seed")
    seed_two = diag_two.get("derived_seed")
    check(isinstance(seed_one, int) and isinstance(seed_two, int), "chain seeds are not recorded")
    check(seed_one != seed_two, "chain_01 and chain_02 reused the same seed")


def test_fail_closed(binary: Path, root: Path) -> None:
    valid = root / "valid_for_fail_closed.tsv"
    write_tsv(valid, fixture_rows(), REQUIRED_COLUMNS)

    invalid_schema = root / "invalid_schema.tsv"
    write_tsv(
        invalid_schema,
        fixture_rows(),
        [column for column in REQUIRED_COLUMNS if column != "hp2_1_alt"],
    )
    invalid_out = root / "invalid_schema_out"
    assert_failure(
        invoke(binary, input_path=invalid_schema, output_path=invalid_out),
        "missing required schema column",
    )
    assert_failed_output_is_not_complete(invalid_out)

    legacy_multiplicity = root / "legacy_multiplicity_columns.tsv"
    write_tsv(
        legacy_multiplicity,
        fixture_rows(),
        [*REQUIRED_COLUMNS, "multiplicity_candidates", "multiplicity_prior"],
    )
    legacy_out = root / "legacy_multiplicity_columns_out"
    assert_failure(
        invoke(binary, input_path=legacy_multiplicity, output_path=legacy_out),
        "removed multiplicity table columns",
    )
    assert_failed_output_is_not_complete(legacy_out)

    mismatch = root / "purity_mismatch.tsv"
    write_tsv(mismatch, fixture_rows(purity="0.95"), REQUIRED_COLUMNS)
    mismatch_out = root / "purity_mismatch_out"
    assert_failure(
        invoke(binary, input_path=mismatch, output_path=mismatch_out),
        "rho_ASCAT mismatch",
    )
    assert_failed_output_is_not_complete(mismatch_out)

    unknown_algorithm_out = root / "unknown_algorithm_out"
    assert_failure(
        invoke(
            binary,
            input_path=valid,
            output_path=unknown_algorithm_out,
            algorithm="gibbs",
        ),
        "unknown algorithm",
    )
    assert_failed_output_is_not_complete(unknown_algorithm_out)

    completed = root / "completed_output"
    assert_success(
        invoke(binary, input_path=valid, output_path=completed),
        "first write to output directory",
    )
    assert_failure(
        invoke(binary, input_path=valid, output_path=completed),
        "overwrite of completed output directory",
    )


def run(binary: Path) -> None:
    check(binary.is_file(), f"inference binary does not exist: {binary}")
    check(binary.stat().st_mode & 0o111, f"inference binary is not executable: {binary}")
    with tempfile.TemporaryDirectory(prefix="inference-contract-") as temporary:
        root = Path(temporary)
        test_valid_input_and_hp_likelihood(binary, root)
        test_thread_policy(binary, root)
        test_multiple_chains_have_distinct_seeded_outputs(binary, root)
        test_fail_closed(binary, root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        run(args.binary)
    except ContractFailure as exc:
        print(f"inference contract FAILED: {exc}", file=sys.stderr)
        return 1
    print("inference contract PASSED: schema, likelihood, threads, chains, artifacts, fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
