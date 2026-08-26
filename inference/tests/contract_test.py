#!/usr/bin/env python3
"""Black-box contract tests for the C++ annealed-SMC inference executable.

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
    "posterior_summary.tsv.gz",
    "topology_summary.tsv",
    "diagnostics.json",
    "representative_tree.json",
    "checkpoint.json.gz",
    "smc_complete.json",
    "particle_history.jsonl.gz",
)

SMC_ALGORITHM = "rao_blackwellized_annealed_smc"


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


def fixture_rows(*, hp_shift: int = 0, purity: str = "0.99", sites: int = 2) -> list[dict[str, str]]:
    """Return the minimal deterministic synthetic table with active columns.

    The alternate HP layout keeps bulk/CN/purity fixed while changing the
    tagged-read allocation.  Model A must accept both layouts and produce the
    same likelihood/posterior because HP is schema-validated supplementary
    evidence, not a primary likelihood feature.
    """

    rows: list[dict[str, str]] = []
    for index in range(1, sites + 1):
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
    independent_repeats: int = 1,
    threads: int = 1,
    annealing_stages: int = 24,
    particles: int = 32,
    num_nodes: int = 2,
    rho_ascat: str = "0.99",
    algorithm: str = SMC_ALGORITHM,
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
        "--repeats",
        str(independent_repeats),
        "--threads",
        str(threads),
        "--annealing-stages",
        str(annealing_stages),
        "--num-nodes",
        str(num_nodes),
        "--particles",
        str(particles),
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
        all(record.get("sample_kind") == "smc_particle" for record in records),
        f"samples do not identify particle semantics: {path}",
    )
    check(
        all(isinstance(record.get("log_weight"), (int, float)) for record in records),
        f"samples do not expose numeric log_weight values: {path}",
    )
    return records


def decompressed_bytes(path: Path) -> bytes:
    with gzip.open(path, "rb") as handle:
        return handle.read()


def public_output_semantics(output_dir: Path) -> dict[str, Any]:
    """Return parsed public artifacts, ignoring gzip/runtime-only encoding.

    The checkpoint RNG stream is an audit detail, not a posterior output
    semantic.  Excluding it lets thread tests protect observable results
    without coupling them to runtime-specific checkpoint metadata.
    """

    checkpoint = read_gzip_json(output_dir / "checkpoint.json.gz")
    checkpoint.pop("rng_state", None)
    return {
        "samples": read_jsonl_gz(output_dir / "samples.jsonl.gz"),
        "multiplicity_posterior": decompressed_bytes(
            output_dir / "multiplicity_posterior.tsv.gz"
        ),
        "posterior_summary": decompressed_bytes(output_dir / "posterior_summary.tsv.gz"),
        "topology_summary": (output_dir / "topology_summary.tsv").read_bytes(),
        "diagnostics": read_json(output_dir / "diagnostics.json"),
        "representative_tree": read_json(output_dir / "representative_tree.json"),
        "checkpoint": checkpoint,
        "particle_history": read_jsonl_gz(output_dir / "particle_history.jsonl.gz"),
        "completion": read_json(output_dir / "smc_complete.json"),
    }


def _ancestor_path(parents: list[int], node: int) -> set[int]:
    ancestors: set[int] = set()
    cursor = parents[node]
    while cursor != -1:
        ancestors.add(cursor)
        cursor = parents[cursor]
    return ancestors


def assert_smc_artifacts(output_dir: Path, *, expected_sites: int = 2) -> dict[str, Any]:
    for artifact in ARTIFACTS:
        check((output_dir / artifact).is_file(), f"missing SMC artifact {artifact} in {output_dir}")

    diagnostics = read_json(output_dir / "diagnostics.json")
    completion = read_json(output_dir / "smc_complete.json")
    tree = read_json(output_dir / "representative_tree.json")
    checkpoint = read_gzip_json(output_dir / "checkpoint.json.gz")
    samples = read_jsonl_gz(output_dir / "samples.jsonl.gz")
    history = read_jsonl_gz(output_dir / "particle_history.jsonl.gz")
    with gzip.open(output_dir / "multiplicity_posterior.tsv.gz", "rt", encoding="utf-8") as handle:
        posterior_lines = [line.rstrip("\n") for line in handle if line.strip()]
    check(
        posterior_lines
        and posterior_lines[0] == "mutation_id\tmultiplicity\tprior\tposterior_mean",
        "multiplicity posterior artifact has the wrong header",
    )
    config = diagnostics.get("config")
    check(isinstance(config, dict), "diagnostics.config is missing")
    check(config.get("global_topology_moves") == 1,
          "C++ diagnostics do not expose the active global topology move setting")
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
    with gzip.open(output_dir / "posterior_summary.tsv.gz", "rt", encoding="utf-8") as handle:
        ccf_lines = [line.rstrip("\n") for line in handle if line.strip()]
    check(
        ccf_lines
        and ccf_lines[0] == "clone\tccf_median\tccf_q025\tccf_q975\tphi_median\tphi_q025\tphi_q975",
        "posterior summary artifact has the wrong header",
    )
    check(len(ccf_lines) == 1 + int(config.get("num_nodes", 0)),
          "posterior summary must contain one row per fixed-K clone")
    with (output_dir / "topology_summary.tsv").open(encoding="utf-8") as handle:
        topology_lines = [line.rstrip("\n") for line in handle if line.strip()]
    check(
        topology_lines
        and topology_lines[0] == "parent\tchild\tsupport_count\tretained_samples\tsupport_fraction",
        "topology summary artifact has the wrong header",
    )
    check(len(topology_lines) > 1, "topology summary artifact is empty")

    algorithm = str(diagnostics.get("algorithm", ""))
    model = str(diagnostics.get("model", ""))
    check(algorithm == SMC_ALGORITHM, "diagnostics do not identify the annealed SMC sampler")
    check(diagnostics.get("sample_semantics") == "smc_particle", "samples are not marked as SMC particles")
    check(
        diagnostics.get("checkpoint_semantics") == "smc_stage_particle_state",
        "checkpoint semantics are not marked as SMC particle state",
    )
    check(diagnostics.get("input_schema") == SCHEMA_VERSION, "input schema is not recorded")
    check(diagnostics.get("observed_sites") == expected_sites, "observed site count is wrong")
    check(diagnostics.get("annealing", {}).get("final_beta") == 1.0,
          "diagnostics do not record completion at beta=1")
    check("topology_change_rate" in diagnostics,
          "diagnostics do not record topology change rate")
    check(
        diagnostics.get("rejuvenation", {}).get("topology_kernel")
        == "local_conditional_SPR_plus_global_legal_tree_MH",
        "diagnostics do not identify the PhyClone-inspired topology kernel",
    )
    check(
        diagnostics.get("state_variables") == ["topology", "eta"],
        "the SMC particle state must be topology/eta",
    )
    check(config.get("ascat_purity") == 0.99, "diagnostics did not record rho_ASCAT=0.99")
    phi_mean = diagnostics.get("phi_mean")
    check(
        isinstance(phi_mean, list)
        and len(phi_mean) == config.get("num_nodes")
        and all(isinstance(value, (int, float)) for value in phi_mean),
        "diagnostics.phi_mean is missing or has the wrong shape",
    )
    num_nodes = config.get("num_nodes")
    check(isinstance(num_nodes, int) and num_nodes >= 2, "fixed-K num_nodes is missing")
    selected_edges = tree.get("selected_edges")
    check(isinstance(selected_edges, list), "representative tree is missing selected_edges")
    check(
        len(selected_edges) == num_nodes,
        "fixed-K tree must expose exactly one edge per candidate clone node",
    )
    root_edges = [
        edge for edge in selected_edges
        if isinstance(edge, dict) and edge.get("parent") == "tumor_root"
    ]
    check(
        len(root_edges) == 1,
        "tree violates exactly-one-founder contract: expected one tumor_root child",
    )
    expected_children = {f"clone_{index}" for index in range(1, num_nodes + 1)}
    actual_children = {
        edge.get("child") for edge in selected_edges if isinstance(edge, dict)
    }
    check(actual_children == expected_children, "fixed-K tree child labels are incomplete")
    for sample in samples:
        topology = sample.get("topology")
        check(isinstance(topology, dict), "SMC particle is missing topology state")
        parents = topology.get("parents")
        eta = sample.get("eta")
        phi = sample.get("phi")
        check(
            isinstance(parents, list)
            and len(parents) == num_nodes
            and parents.count(-1) == 1,
            "posterior sample violates exactly-one-founder/fixed-K contract",
        )
        check(
            isinstance(eta, list)
            and len(eta) == num_nodes
            and all(isinstance(value, (int, float)) and value > 0.0 for value in eta)
            and abs(sum(eta) - 1.0) < 1e-9,
            "posterior sample eta is not a positive simplex",
        )
        check(
            isinstance(phi, list)
            and len(phi) == num_nodes
            and all(isinstance(value, (int, float)) and 0.0 <= value <= 1.0 for value in phi),
            "posterior sample phi is missing or out of range",
        )
        for child, parent in enumerate(parents):
            check(
                isinstance(parent, int)
                and -1 <= parent < num_nodes
                and parent != child,
                "posterior sample contains an invalid parent index",
            )
            seen = {child}
            cursor = parent
            while cursor != -1:
                check(cursor not in seen, "posterior sample contains a topology cycle")
                seen.add(cursor)
                cursor = parents[cursor]
        for node in range(num_nodes):
            expected_phi = sum(
                eta[descendant]
                for descendant in range(num_nodes)
                if descendant == node
                or node in _ancestor_path(parents, descendant)
            )
            check(
                abs(phi[node] - expected_phi) < 1e-9,
                "posterior sample phi is not the descendant-sum of eta",
            )
            if parents[node] != -1:
                check(
                    phi[parents[node]] + 1e-12 >= phi[node],
                    "posterior sample parent CCF is smaller than child CCF",
                )
        founder = parents.index(-1)
        check(abs(phi[founder] - 1.0) < 1e-9, "tumor founder phi must equal one")
    target = diagnostics.get("target")
    check(isinstance(target, dict), "diagnostics.target is missing")
    check(
        "joint_multiplicity_responsibility" in str(target.get("site_terms", "")),
        "diagnostics do not record Rao-Blackwellized multiplicity responsibilities",
    )
    check(
        diagnostics.get("multiplicity_semantics")
        == "weighted_joint_responsibility_marginalized_over_clone",
        "multiplicity output is not identified as weighted joint responsibility",
    )
    annealing = diagnostics.get("annealing")
    check(isinstance(annealing, dict), "annealing diagnostics are missing")
    stages = annealing.get("stages")
    check(isinstance(stages, list) and stages, "annealing stage diagnostics are empty")
    check(annealing.get("beta_schedule", [])[0] == 0.0, "annealing must start at beta=0")
    check(annealing.get("beta_schedule", [])[-1] == 1.0, "annealing must finish at beta=1")
    for stage in stages:
        check(0.0 <= float(stage["beta"]) <= 1.0, "annealing beta is out of range")
        check(float(stage["conditional_ess"]) > 0.0, "conditional ESS is missing")
        check(float(stage["weighted_ess"]) > 0.0, "weighted particle ESS is missing")
        check("resampled" in stage and "ancestor_diversity" in stage, "ESS ancestry decision is missing")
    check(
        annealing.get("weighted_ess_resampling_threshold_fraction") == 0.5,
        "weighted ESS resampling threshold is not recorded",
    )
    rejuvenation = diagnostics.get("rejuvenation")
    check(isinstance(rejuvenation, dict), "rejuvenation diagnostics are missing")
    for stage in rejuvenation.get("stages", []):
        check(3 <= int(stage["sweeps"]) <= 20, "rejuvenation sweep count is outside the contract")
        check(stage.get("stop_reason"), "rejuvenation stop reason is missing")
        check("eta_acceptance" in stage and "topology_acceptance" in stage, "rejuvenation rates are missing")
    check(completion.get("status") == "complete", "completion status is not complete")
    check(completion.get("sample_semantics") == "smc_particle", "completion is not marked as particle output")
    check(set(ARTIFACTS).issubset(set(completion.get("artifacts", []))), "completion manifest omits SMC artifacts")
    check(checkpoint.get("sample_semantics") == "smc_particle", "checkpoint is not marked as particle output")
    check(checkpoint.get("checkpoint_semantics") == "smc_stage_particle_state", "checkpoint stage semantics are missing")
    check(isinstance(checkpoint.get("particles"), list) and checkpoint["particles"], "checkpoint particles are missing")
    weights = checkpoint.get("weights")
    check(isinstance(weights, list) and abs(sum(weights) - 1.0) < 1e-9, "checkpoint weights do not normalize")
    check(len(checkpoint.get("ancestor_indices", [])) == len(checkpoint["particles"]), "checkpoint ancestry is incomplete")
    check(history and all(record.get("sample_kind") == "smc_particle" for record in history), "particle history semantics are missing")
    check(tree.get("model") == diagnostics.get("algorithm"), "tree/model contract mismatch")
    check("mcmc" not in json.dumps(diagnostics).lower(), "SMC diagnostics contain MCMC semantics")
    return diagnostics


def assert_failed_output_is_not_complete(path: Path) -> None:
    if not path.exists():
        return
    check(
        not list(path.glob("**/smc_complete.json")),
        f"failed invocation left a completed output behind: {path}",
    )


def test_optimized_backend_preserves_existing_output_semantics(binary: Path, root: Path) -> None:
    """The active optimized CLI keeps the Python-facing SMC artifact contract."""

    canonical = root / "canonical_output_semantics.tsv"
    output = root / "optimized_output_semantics"
    write_tsv(canonical, fixture_rows(sites=3), REQUIRED_COLUMNS)
    assert_success(
        invoke(
            binary,
            input_path=canonical,
            output_path=output,
            annealing_stages=8,
            particles=12,
        ),
        "optimized backend output semantics",
    )

    diagnostics = assert_smc_artifacts(output, expected_sites=3)
    samples = read_jsonl_gz(output / "samples.jsonl.gz")
    history = read_jsonl_gz(output / "particle_history.jsonl.gz")
    stages = diagnostics["annealing"]["stages"]
    completion = read_json(output / "smc_complete.json")
    check(diagnostics.get("posterior_samples") == 12, "optimized backend changed posterior sample count")
    check(diagnostics.get("particle_count") == 12, "optimized backend changed particle count semantics")
    check(len(samples) == 12, "optimized backend did not publish one sample per particle")
    check(
        all("z" not in sample and sample.get("sample_kind") == "smc_particle" for sample in samples),
        "optimized backend exposed legacy assignment/MCMC sample semantics",
    )
    check(
        len(history) == len(stages) * len(samples),
        "optimized backend particle history is not stage-by-particle bounded",
    )
    check(
        set(ARTIFACTS).issubset(set(completion.get("artifacts", []))),
        "optimized backend completion manifest changed existing artifact semantics",
    )


def test_model_a_ignores_hp_counts(binary: Path, root: Path) -> None:
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
    assert_smc_artifacts(baseline)
    assert_smc_artifacts(changed_hp)

    baseline_scores = [
        record["log_weight"]
        for record in read_jsonl_gz(baseline / "samples.jsonl.gz")
    ]
    changed_scores = [
        record["log_weight"]
        for record in read_jsonl_gz(changed_hp / "samples.jsonl.gz")
    ]
    check(
        baseline_scores == changed_scores,
        "Model A posterior changed after only HP counts changed; "
        "HP counts must remain supplementary until Model B is defined",
    )
    check(
        decompressed_bytes(baseline / "multiplicity_posterior.tsv.gz")
        == decompressed_bytes(changed_hp / "multiplicity_posterior.tsv.gz"),
        "Model A multiplicity posterior changed after only HP counts changed",
    )


def test_particle_thread_policy(binary: Path, root: Path) -> None:
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
    diag_one = assert_smc_artifacts(one)
    diag_two = assert_smc_artifacts(two)
    # Compare parsed public artifacts rather than compressed bytes.  This
    # protects output semantics while allowing gzip/runtime encoding details
    # to change.
    check(
        public_output_semantics(one) == public_output_semantics(two),
        "threads=1 and threads=2 changed public output semantics",
    )
    check(
        diag_one.get("config", {}).get("seed") == diag_two.get("config", {}).get("seed"),
        "thread comparison changed the requested seed",
    )

    # Exercise the active site-parallel scorer threshold as well as the
    # repeat-parallel path above.  The public posterior must remain identical
    # when deterministic site work is moved between workers.
    parallel_canonical = root / "canonical_site_parallel.tsv"
    parallel_one = root / "site_parallel_threads_1"
    parallel_two = root / "site_parallel_threads_2"
    write_tsv(parallel_canonical, fixture_rows(sites=1024), REQUIRED_COLUMNS)
    for output, thread_count in ((parallel_one, 1), (parallel_two, 2)):
        assert_success(
            invoke(
                binary,
                input_path=parallel_canonical,
                output_path=output,
                threads=thread_count,
                annealing_stages=4,
                particles=4,
                num_nodes=2,
            ),
            f"site scorer threads={thread_count}",
        )
        assert_smc_artifacts(output, expected_sites=1024)
    check(
        public_output_semantics(parallel_one) == public_output_semantics(parallel_two),
        "site-parallel threads changed public output semantics",
    )


def test_independent_repeats_have_distinct_seeded_particles(binary: Path, root: Path) -> None:
    canonical = root / "canonical_repeats.tsv"
    output = root / "repeats_2"
    write_tsv(canonical, fixture_rows(), REQUIRED_COLUMNS)
    assert_success(
        invoke(binary, input_path=canonical, output_path=output, independent_repeats=2, threads=2),
        "two independent SMC repeats",
    )
    repeat_one = output / "repeat_01"
    repeat_two = output / "repeat_02"
    diag_one = assert_smc_artifacts(repeat_one)
    diag_two = assert_smc_artifacts(repeat_two)
    seed_one = diag_one.get("derived_seed", diag_one.get("config", {}).get("seed"))
    seed_two = diag_two.get("derived_seed", diag_two.get("config", {}).get("seed"))
    check(isinstance(seed_one, int) and isinstance(seed_two, int), "repeat seeds are not recorded")
    check(seed_one != seed_two, "independent SMC repeats reused the same seed")
    check(diag_one.get("sample_semantics") == "smc_particle", "repeat_01 lacks particle semantics")
    check(diag_two.get("sample_semantics") == "smc_particle", "repeat_02 lacks particle semantics")


def test_seed_and_repeat_are_deterministic(binary: Path, root: Path) -> None:
    canonical = root / "canonical_seed_repeat.tsv"
    first = root / "seed_repeat_first"
    second = root / "seed_repeat_second"
    write_tsv(canonical, fixture_rows(sites=3), REQUIRED_COLUMNS)

    for output in (first, second):
        assert_success(
            invoke(
                binary,
                input_path=canonical,
                output_path=output,
                seed=20260824,
                independent_repeats=2,
                threads=2,
                annealing_stages=8,
                particles=12,
            ),
            f"deterministic two-repeat run: {output.name}",
        )

    repeat_seeds: list[int] = []
    for repeat_index in (1, 2):
        first_repeat = first / f"repeat_{repeat_index:02d}"
        second_repeat = second / f"repeat_{repeat_index:02d}"
        first_diagnostics = assert_smc_artifacts(first_repeat, expected_sites=3)
        second_diagnostics = assert_smc_artifacts(second_repeat, expected_sites=3)
        first_seed = first_diagnostics.get("derived_seed")
        second_seed = second_diagnostics.get("derived_seed")
        check(isinstance(first_seed, int) and isinstance(second_seed, int), "repeat seed is not recorded")
        check(first_seed == second_seed, "same seed/repeat index produced different derived seeds")
        repeat_seeds.append(first_seed)
        check(
            public_output_semantics(first_repeat) == public_output_semantics(second_repeat),
            f"same seed/repeat index changed output semantics for repeat_{repeat_index:02d}",
        )
    check(repeat_seeds[0] != repeat_seeds[1], "independent repeat indices reused the same derived seed")


def test_performance_smoke_uses_bounded_work_contract(binary: Path, root: Path) -> None:
    """Exercise a larger-than-minimal workload without a wall-clock threshold."""

    canonical = root / "canonical_performance_smoke.tsv"
    output = root / "performance_smoke"
    particle_count = 16
    max_stages = 8
    write_tsv(canonical, fixture_rows(sites=12), REQUIRED_COLUMNS)
    assert_success(
        invoke(
            binary,
            input_path=canonical,
            output_path=output,
            annealing_stages=max_stages,
            particles=particle_count,
        ),
        "performance smoke workload",
    )

    diagnostics = assert_smc_artifacts(output, expected_sites=12)
    stages = diagnostics["annealing"]["stages"]
    history = read_jsonl_gz(output / "particle_history.jsonl.gz")
    check(diagnostics.get("particle_count") == particle_count, "performance smoke changed requested particle work")
    check(diagnostics.get("posterior_samples") == particle_count, "performance smoke did not complete the particle population")
    check(1 <= len(stages) <= max_stages, "performance smoke exceeded its configured annealing work bound")
    check(
        len(history) == len(stages) * particle_count,
        "performance smoke particle history is not bounded by stage x particle work",
    )


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
        test_optimized_backend_preserves_existing_output_semantics(binary, root)
        test_model_a_ignores_hp_counts(binary, root)
        test_particle_thread_policy(binary, root)
        test_independent_repeats_have_distinct_seeded_particles(binary, root)
        test_seed_and_repeat_are_deterministic(binary, root)
        test_performance_smoke_uses_bounded_work_contract(binary, root)
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
    print(
        "inference contract PASSED: output semantics, schema, particles, annealing, "
        "threads, deterministic seed/repeats, bounded performance smoke, fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
