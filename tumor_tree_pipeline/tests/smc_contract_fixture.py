"""Small deterministic SMC output fixture and its public artifact checks."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any


SMC_ARTIFACTS = (
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


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode()


def _write_gzip(path: Path, text: str) -> None:
    path.write_bytes(gzip.compress(text.encode(), compresslevel=6, mtime=0))


def _ancestor_path(parents: list[int], node: int) -> set[int]:
    result: set[int] = set()
    cursor = parents[node]
    while cursor != -1:
        result.add(cursor)
        cursor = parents[cursor]
    return result


def write_synthetic_smc_run(
    output_dir: Path,
    *,
    seed: int = 20260824,
    independent_repeat: int = 1,
) -> Path:
    """Write the smallest two-site, two-particle SMC contract fixture."""

    output_dir.mkdir(parents=True, exist_ok=True)
    particles = [
        {
            "particle_index": 0,
            "sample_kind": "smc_particle",
            "particle_weight": 0.5,
            "log_weight": -0.2,
            "topology": {"parents": [-1, 0], "canonical_id": "root-1-child-2"},
            "eta": [0.6, 0.4],
            "phi": [1.0, 0.4],
        },
        {
            "particle_index": 1,
            "sample_kind": "smc_particle",
            "particle_weight": 0.5,
            "log_weight": -0.3,
            "topology": {"parents": [1, -1], "canonical_id": "root-2-child-1"},
            "eta": [0.35, 0.65],
            "phi": [0.35, 1.0],
        },
    ]
    sample_lines = "".join(json.dumps(item, separators=(",", ":"), sort_keys=True) + "\n" for item in particles)
    _write_gzip(output_dir / "samples.jsonl.gz", sample_lines)

    multiplicity = (
        "mutation_id\tmultiplicity\tprior\tposterior_mean\n"
        "chr1:101:A>T\t1\t0.75\t0.80\n"
        "chr1:101:A>T\t2\t0.25\t0.20\n"
        "chr1:102:C>G\t1\t0.75\t0.70\n"
        "chr1:102:C>G\t2\t0.25\t0.30\n"
    )
    _write_gzip(output_dir / "multiplicity_posterior.tsv.gz", multiplicity)

    posterior_summary = (
        "clone\tccf_median\tccf_q025\tccf_q975\tphi_median\tphi_q025\tphi_q975\n"
        "clone_1\t0.675\t0.350\t1.000\t0.675\t0.350\t1.000\n"
        "clone_2\t0.700\t0.400\t1.000\t0.700\t0.400\t1.000\n"
    )
    _write_gzip(output_dir / "posterior_summary.tsv.gz", posterior_summary)

    topology_summary = (
        "parent\tchild\tsupport_count\tretained_samples\tsupport_fraction\n"
        "tumor_root\tclone_1\t1\t2\t0.500\n"
        "tumor_root\tclone_2\t1\t2\t0.500\n"
        "clone_1\tclone_2\t1\t2\t0.500\n"
        "clone_2\tclone_1\t1\t2\t0.500\n"
    )
    (output_dir / "topology_summary.tsv").write_text(topology_summary, encoding="utf-8")

    stages = [
        {
            "stage": 1,
            "beta": 0.5,
            "conditional_ess": 1.6,
            "weighted_ess": 1.6,
            "incremental_log_weights": [-0.1, -0.1],
            "resampled": False,
            "ancestor_diversity": 2,
            "log_normalizing_constant_increment": -0.1,
            "particle_diversity": {"unique_topologies": 2, "unique_eta": 2},
        },
        {
            "stage": 2,
            "beta": 1.0,
            "conditional_ess": 1.4,
            "weighted_ess": 1.2,
            "incremental_log_weights": [-0.2, -0.3],
            "resampled": True,
            "ancestor_diversity": 2,
            "log_normalizing_constant_increment": -0.25,
            "particle_diversity": {"unique_topologies": 2, "unique_eta": 2},
        },
    ]
    rejuvenation_stages = [
        {
            "stage": stage["stage"],
            "sweeps": 3,
            "stop_reason": "decorrelated",
            "eta_acceptance": 0.50,
            "eta_change_rate": 0.50,
            "eta_decorrelation": 0.80,
            "topology_acceptance": 0.50,
            "topology_change_rate": 0.50,
            "unique_topologies": 2,
        }
        for stage in stages
    ]
    diagnostics = {
        "algorithm": "rao_blackwellized_annealed_smc",
        "sample_semantics": "smc_particle",
        "checkpoint_semantics": "smc_stage_particle_state",
        "input_schema": "hcc1395_tumor_tree_input/v4",
        "observed_sites": 2,
        "independent_repeat": independent_repeat,
        "particle_count": 2,
        "state_variables": ["topology", "eta"],
        "config": {
            "num_nodes": 2,
            "particle_count": 2,
            "ascat_purity": 0.99,
            "seed": seed,
        },
        "target": {
            "site_terms": "CN_constrained_joint_multiplicity_responsibility_Rao_Blackwellized",
            "likelihood_tempering": "product_site_likelihood_to_beta",
        },
        "annealing": {
            "beta_schedule": [0.0, 0.5, 1.0],
            "stages": stages,
            "conditional_ess_target_fraction": 0.8,
            "weighted_ess_resampling_threshold_fraction": 0.5,
        },
        "rejuvenation": {
            "min_sweeps": 3,
            "max_sweeps": 20,
            "eta_kernel": "adaptive_gaussian_random_walk MH in ALR coordinates",
            "topology_kernel": "local conditional SPR plus global legal single-founder MH",
            "topology_mixture": {"local": 0.8, "global": 0.2},
            "stages": rejuvenation_stages,
        },
        "phi_mean": [0.675, 0.7],
        "multiplicity_semantics": "weighted_joint_responsibility_marginalized_over_clone",
        "ccf_summary_semantics": "particle_weighted_quantiles",
        "topology_summary_semantics": "particle_weighted_canonical_edge_support",
        "predictive": {"coverage": 0.90, "log_score": -1.0},
        "input_sha256": "synthetic-two-site-fixture",
        "particle_history_artifact": "particle_history.jsonl.gz",
    }
    (output_dir / "diagnostics.json").write_bytes(_json_bytes(diagnostics))

    checkpoint = {
        "checkpoint_version": 3,
        "checkpoint_semantics": "smc_stage_particle_state",
        "sample_semantics": "smc_particle",
        "stage": 2,
        "beta": 1.0,
        "input_sha256": diagnostics["input_sha256"],
        "config": diagnostics["config"],
        "particles": [
            {
                "particle_index": item["particle_index"],
                "topology": item["topology"],
                "eta": item["eta"],
                "weight": item["particle_weight"],
            }
            for item in particles
        ],
        "weights": [item["particle_weight"] for item in particles],
        "ancestor_indices": [0, 1],
        "normalizing_constant_log_estimate": -0.35,
        "adaptive_proposal_state": {"alr_covariance_regularization": 1e-6, "scale": 0.1},
        "rng_state": {"seed": seed, "lineage": "synthetic-stage-2"},
    }
    _write_gzip(output_dir / "checkpoint.json.gz", json.dumps(checkpoint, separators=(",", ":"), sort_keys=True) + "\n")

    history_lines = "".join(
        json.dumps(
            {
                "stage": stage["stage"],
                "particle_index": item["particle_index"],
                "sample_kind": "smc_particle",
                "weight": item["particle_weight"],
                "ancestor_index": item["particle_index"],
                "topology": item["topology"],
                "rejuvenation_sweeps": 3,
                "rng_checkpoint_lineage": f"stage-{stage['stage']}-particle-{item['particle_index']}",
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
        for stage in stages
        for item in particles
    )
    _write_gzip(output_dir / "particle_history.jsonl.gz", history_lines)

    completion = {
        "status": "complete",
        "algorithm": diagnostics["algorithm"],
        "sample_semantics": "smc_particle",
        "checkpoint_semantics": "smc_stage_particle_state",
        "particle_count": len(particles),
        "artifacts": list(SMC_ARTIFACTS),
    }
    (output_dir / "smc_complete.json").write_bytes(_json_bytes(completion))

    representative = {
        "model": "rao_blackwellized_annealed_smc",
        "selection_semantics": "highest_posterior_weight_topology_class_then_weighted_ccf_median",
        "selected_edges": [
            {"parent": "tumor_root", "child": "clone_1"},
            {"parent": "clone_1", "child": "clone_2"},
        ],
        "posterior_map_assignments": {
            "chr1:101:A>T": {"node": "clone_1"},
            "chr1:102:C>G": {"node": "clone_2"},
        },
    }
    (output_dir / "representative_tree.json").write_bytes(_json_bytes(representative))
    return output_dir


def assert_smc_artifacts(output_dir: Path, *, expected_sites: int = 2) -> dict[str, Any]:
    for name in SMC_ARTIFACTS:
        assert (output_dir / name).is_file(), f"missing SMC artifact: {name}"

    diagnostics = json.loads((output_dir / "diagnostics.json").read_text(encoding="utf-8"))
    completion = json.loads((output_dir / "smc_complete.json").read_text(encoding="utf-8"))
    checkpoint = json.loads(gzip.decompress((output_dir / "checkpoint.json.gz").read_bytes()))
    samples = [
        json.loads(line)
        for line in gzip.decompress((output_dir / "samples.jsonl.gz").read_bytes()).decode().splitlines()
        if line.strip()
    ]
    history = [
        json.loads(line)
        for line in gzip.decompress((output_dir / "particle_history.jsonl.gz").read_bytes()).decode().splitlines()
        if line.strip()
    ]

    assert diagnostics["algorithm"] == "rao_blackwellized_annealed_smc"
    assert diagnostics["sample_semantics"] == "smc_particle"
    assert diagnostics["checkpoint_semantics"] == "smc_stage_particle_state"
    assert diagnostics["observed_sites"] == expected_sites
    assert diagnostics["state_variables"] == ["topology", "eta"]
    assert "rhat" not in json.dumps(diagnostics).lower()
    assert "chain_ess" not in json.dumps(diagnostics).lower()

    assert len(samples) == diagnostics["particle_count"]
    weights = [float(sample["particle_weight"]) for sample in samples]
    assert abs(sum(weights) - 1.0) < 1e-12
    assert len({round(weight, 12) for weight in weights}) == 1
    num_nodes = diagnostics["config"]["num_nodes"]
    for sample in samples:
        assert sample["sample_kind"] == "smc_particle"
        assert "z" not in sample
        topology = sample["topology"]
        parents = topology["parents"]
        eta = sample["eta"]
        phi = sample["phi"]
        assert len(parents) == len(eta) == len(phi) == num_nodes
        assert parents.count(-1) == 1
        assert all(value > 0.0 for value in eta)
        assert abs(sum(eta) - 1.0) < 1e-12
        assert all(0.0 <= value <= 1.0 for value in phi)
        for child, parent in enumerate(parents):
            assert -1 <= parent < num_nodes and parent != child
            seen = {child}
            cursor = parent
            while cursor != -1:
                assert cursor not in seen
                seen.add(cursor)
                cursor = parents[cursor]
        for node in range(num_nodes):
            expected_phi = sum(
                eta[descendant]
                for descendant in range(num_nodes)
                if descendant == node or node in _ancestor_path(parents, descendant)
            )
            assert abs(phi[node] - expected_phi) < 1e-12

    multiplicity = gzip.decompress((output_dir / "multiplicity_posterior.tsv.gz").read_bytes()).decode().splitlines()
    assert multiplicity[0] == "mutation_id\tmultiplicity\tprior\tposterior_mean"
    posterior_by_site: dict[str, float] = {}
    for line in multiplicity[1:]:
        mutation_id, _multiplicity, _prior, posterior = line.split("\t")
        posterior_by_site[mutation_id] = posterior_by_site.get(mutation_id, 0.0) + float(posterior)
    assert len(posterior_by_site) == expected_sites
    assert all(abs(value - 1.0) < 1e-12 for value in posterior_by_site.values())
    assert diagnostics["multiplicity_semantics"].startswith("weighted_joint_responsibility")

    ccf = gzip.decompress((output_dir / "posterior_summary.tsv.gz").read_bytes()).decode().splitlines()
    assert ccf[0] == "clone\tccf_median\tccf_q025\tccf_q975\tphi_median\tphi_q025\tphi_q975"
    assert len(ccf) == num_nodes + 1
    assert diagnostics["ccf_summary_semantics"] == "particle_weighted_quantiles"

    topology = (output_dir / "topology_summary.tsv").read_text(encoding="utf-8").splitlines()
    assert topology[0] == "parent\tchild\tsupport_count\tretained_samples\tsupport_fraction"
    assert len(topology) > 1
    assert all(0.0 <= float(line.split("\t")[-1]) <= 1.0 for line in topology[1:])
    assert diagnostics["topology_summary_semantics"] == "particle_weighted_canonical_edge_support"

    annealing = diagnostics["annealing"]
    assert annealing["beta_schedule"] == [0.0, 0.5, 1.0]
    assert len(annealing["stages"]) == 2
    assert all(0.0 <= stage["beta"] <= 1.0 for stage in annealing["stages"])
    assert all(stage["conditional_ess"] > 0.0 and stage["weighted_ess"] > 0.0 for stage in annealing["stages"])
    assert all("resampled" in stage and "ancestor_diversity" in stage for stage in annealing["stages"])
    assert annealing["weighted_ess_resampling_threshold_fraction"] == 0.5

    rejuvenation = diagnostics["rejuvenation"]
    assert rejuvenation["min_sweeps"] >= 3
    assert rejuvenation["max_sweeps"] <= 20
    assert len(rejuvenation["stages"]) == len(annealing["stages"])
    assert all(3 <= stage["sweeps"] <= 20 and stage["stop_reason"] for stage in rejuvenation["stages"])
    assert all("eta_acceptance" in stage and "topology_acceptance" in stage for stage in rejuvenation["stages"])

    assert checkpoint["sample_semantics"] == "smc_particle"
    assert checkpoint["checkpoint_semantics"] == "smc_stage_particle_state"
    assert checkpoint["stage"] == len(annealing["stages"])
    assert checkpoint["beta"] == 1.0
    assert len(checkpoint["particles"]) == diagnostics["particle_count"]
    assert abs(sum(checkpoint["weights"]) - 1.0) < 1e-12
    assert len(checkpoint["ancestor_indices"]) == len(checkpoint["particles"])
    assert checkpoint["rng_state"]

    assert completion["status"] == "complete"
    assert completion["sample_semantics"] == "smc_particle"
    assert set(SMC_ARTIFACTS).issubset(completion["artifacts"])
    assert all(record["sample_kind"] == "smc_particle" for record in history)
    assert len(history) == len(annealing["stages"]) * diagnostics["particle_count"]
    return diagnostics
