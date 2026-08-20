"""Build the fail-closed site table consumed by tumor-tree inference.

Multiplicity is a CN-only prior.  Bulk counts and ASCAT purity are never used
to construct it; they remain observations/parameters for the downstream
likelihood and therefore enter the statistical model exactly once.  LongPhase-S
PS blocks are upstream phasing metadata used when HP1-1/HP2-1 counts are
formed; the PS label itself is not copied into the downstream likelihood row.
"""

from __future__ import annotations

import json
import math
import platform
import shlex
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import __version__
from .contracts import (
    MODEL_FORBIDDEN_COLUMNS,
    MODEL_INPUT_SCHEMA_VERSION,
    MODEL_REQUIRED_COLUMNS,
    BuildInputs,
)
from .provenance import (
    atomic_write_gzip_tsv,
    atomic_write_json,
    canonical_chrom,
    file_record,
    read_ascat_purity,
    read_tsv,
    sha256_file,
)


ALL_HP_TAGS = (".", "1", "2", "3", "4", "1-1", "2-1", "1-2", "2-2", "other")
OPTIONAL_AUDIT_COLUMNS = (
    "phased_gt",
    "cnv_status",
    "segment_id",
    "loh_state",
    "cnv_confidence",
    "somatic_hp_evidence_status",
)
OUTPUT_COLUMNS = MODEL_REQUIRED_COLUMNS + OPTIONAL_AUDIT_COLUMNS


@dataclass(frozen=True)
class BuildResult:
    table: Path
    qa: Path
    manifest: Path
    rows: int
    eligible_rows: int


def _strict_integer(value: Any, label: str) -> int:
    try:
        numeric = float(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid integer {label}={value!r}") from exc
    if not math.isfinite(numeric) or numeric < 0 or not numeric.is_integer():
        raise ValueError(f"{label} must be a non-negative integer: {value!r}")
    return int(numeric)


def _site_key(row: Mapping[str, Any]) -> tuple[str, int, str, str]:
    chrom = canonical_chrom(row.get("chrom", row.get("chr", "")))
    pos = _strict_integer(row.get("pos"), "pos")
    ref = str(row.get("ref", "")).upper()
    alt = str(row.get("alt", "")).upper()
    if pos < 1 or ref not in "ACGT" or alt not in "ACGT" or ref == alt:
        raise ValueError(f"invalid SNV key: {chrom}:{pos}:{ref}>{alt}")
    return chrom, pos, ref, alt


def _mutation_id(key: tuple[str, int, str, str]) -> str:
    chrom, pos, ref, alt = key
    return f"{chrom}:{pos}:{ref}>{alt}"


def _load_unique(path: Path, label: str) -> dict[tuple[str, int, str, str], dict[str, str]]:
    output: dict[tuple[str, int, str, str], dict[str, str]] = {}
    for row in read_tsv(path):
        key = _site_key(row)
        if key in output:
            raise ValueError(f"duplicate {label} row for {_mutation_id(key)}")
        output[key] = row
    if not output:
        raise ValueError(f"{label} table is empty: {path}")
    return output


def _load_hp(
    path: Path,
) -> dict[tuple[str, int, str, str], dict[str, int]]:
    grouped: dict[tuple[str, int, str, str], dict[str, int]] = {}
    observed_tags: dict[tuple[str, int, str, str], set[str]] = {}
    for row in read_tsv(path):
        key = _site_key(row)
        tag = str(row.get("hp_tag", ""))
        if tag not in ALL_HP_TAGS:
            raise ValueError(f"unexpected HP tag {tag!r} for {_mutation_id(key)}")
        tags = observed_tags.setdefault(key, set())
        if tag in tags:
            raise ValueError(f"duplicate HP category {tag!r} for {_mutation_id(key)}")
        tags.add(tag)
        values = grouped.setdefault(key, {})
        values[f"{tag}_ref"] = _strict_integer(row.get("ref_count"), "HP ref_count")
        values[f"{tag}_alt"] = _strict_integer(row.get("alt_count"), "HP alt_count")
    for key, tags in observed_tags.items():
        if tags != set(ALL_HP_TAGS):
            missing = sorted(set(ALL_HP_TAGS) - tags)
            extra = sorted(tags - set(ALL_HP_TAGS))
            raise ValueError(
                f"HP domain mismatch for {_mutation_id(key)}: missing={missing}, extra={extra}"
            )
    if not grouped:
        raise ValueError(f"HP table is empty: {path}")
    return grouped


def multiplicity_prior(major_cn: int, minor_cn: int) -> dict[int, float]:
    """Return the hierarchical CN-only prior over mutation multiplicity.

    Extant major/minor homolog sides receive equal total mass.  Each side's
    mass is then uniform over ``m=1..side_CN``.  Equal multiplicities from the
    two sides are summed.  With major=3/minor=1 this yields 2/3, 1/6, 1/6.
    """

    if major_cn < minor_cn or minor_cn < 0 or major_cn <= 0:
        raise ValueError(f"invalid major/minor CN: {major_cn}/{minor_cn}")
    sides = [major_cn] + ([minor_cn] if minor_cn > 0 else [])
    side_mass = 1.0 / len(sides)
    weights: Counter[int] = Counter()
    for copy_count in sides:
        within_side_mass = side_mass / copy_count
        for multiplicity in range(1, copy_count + 1):
            weights[multiplicity] += within_side_mass
    total = sum(weights.values())
    prior = {key: value / total for key, value in sorted(weights.items())}
    if abs(sum(prior.values()) - 1.0) > 1e-12:
        raise AssertionError("internal multiplicity-prior normalization failure")
    return prior


def _format_prior(prior: Mapping[int, float]) -> str:
    return ";".join(f"{key}={prior[key]:.12g}" for key in sorted(prior))


def parse_prior(text: str) -> dict[int, float]:
    parsed: dict[int, float] = {}
    for token in str(text).split(";"):
        if not token:
            continue
        if "=" not in token:
            raise ValueError(f"invalid multiplicity-prior token: {token!r}")
        raw_key, raw_value = token.split("=", 1)
        try:
            key = int(raw_key)
            value = float(raw_value)
        except ValueError as exc:
            raise ValueError(f"invalid multiplicity-prior token: {token!r}") from exc
        if key <= 0 or not math.isfinite(value) or value < 0:
            raise ValueError(f"invalid multiplicity-prior token: {token!r}")
        if key in parsed:
            raise ValueError(f"duplicate multiplicity in prior: {key}")
        parsed[key] = value
    return parsed


def _validate_count_manifest(path: Path, expected_sites: int) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid count manifest: {path}") from exc
    if manifest.get("single_site_only") is not True:
        raise ValueError("count manifest must declare single_site_only=true")
    observed = manifest.get("output_sites")
    if observed is not None and int(observed) != expected_sites:
        raise ValueError(
            f"count manifest output_sites mismatch: expected {expected_sites}, observed {observed}"
        )
    return manifest


def _validate_hp_qc(
    path: Path,
    expected_keys: set[tuple[str, int, str, str]],
) -> None:
    rows = _load_unique(path, "HP-QC")
    if set(rows) != expected_keys:
        raise ValueError("HP-QC site keys do not exactly match bulk site keys")
    for key, row in rows.items():
        for field in ("bulk_hp_ref_delta", "bulk_hp_alt_delta"):
            raw = str(row.get(field, "")).strip()
            if raw and float(raw) != 0.0:
                raise ValueError(
                    f"nonzero {field} for {_mutation_id(key)}: {raw}"
                )


def _build_rows(
    bulk_rows: Mapping[tuple[str, int, str, str], Mapping[str, str]],
    hp_rows: Mapping[tuple[str, int, str, str], Mapping[str, int]],
    cn_rows: Mapping[tuple[str, int, str, str], Mapping[str, str]],
    rho_ascat: float,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    key_sets = (set(bulk_rows), set(hp_rows), set(cn_rows))
    if not key_sets[0] == key_sets[1] == key_sets[2]:
        raise ValueError(
            "site-key mismatch among bulk/HP/CN tables: "
            f"bulk={len(key_sets[0])}, hp={len(key_sets[1])}, cn={len(key_sets[2])}"
        )
    output: list[dict[str, Any]] = []
    statuses: Counter[str] = Counter()
    for key in sorted(bulk_rows):
        bulk = bulk_rows[key]
        hp = hp_rows[key]
        cn = cn_rows[key]
        bulk_ref = _strict_integer(bulk.get("bulk_ref"), "bulk_ref")
        bulk_alt = _strict_integer(bulk.get("bulk_alt"), "bulk_alt")
        raw_depth = bulk.get("bulk_depth", bulk.get("bulk_usable_depth"))
        bulk_depth = _strict_integer(raw_depth, "bulk_depth")
        if bulk_depth != bulk_ref + bulk_alt:
            raise ValueError(
                f"bulk count conservation failed for {_mutation_id(key)}: "
                f"depth={bulk_depth}, ref+alt={bulk_ref + bulk_alt}"
            )
        hp_ref = sum(hp[f"{tag}_ref"] for tag in ALL_HP_TAGS)
        hp_alt = sum(hp[f"{tag}_alt"] for tag in ALL_HP_TAGS)
        if (hp_ref, hp_alt) != (bulk_ref, bulk_alt):
            raise ValueError(
                f"bulk/HP conservation failed for {_mutation_id(key)}: "
                f"bulk=({bulk_ref},{bulk_alt}), hp=({hp_ref},{hp_alt})"
            )
        hp1_ref, hp1_alt = hp["1-1_ref"], hp["1-1_alt"]
        hp2_ref, hp2_alt = hp["2-1_ref"], hp["2-1_alt"]
        if hp1_alt and hp2_alt:
            hp_status = "both_primary_tags_observed"
        elif hp1_alt:
            hp_status = "hp1_1_alt_observed"
        elif hp2_alt:
            hp_status = "hp2_1_alt_observed"
        else:
            hp_status = "no_primary_somatic_alt_tag"

        cnv_status = str(cn.get("cnv_status", ""))
        if cnv_status not in {
            "mapped_nonzero_cn",
            "cn_zero",
            "unmapped_segment",
            "segment_overlap",
        }:
            raise ValueError(
                f"unknown CN status for {_mutation_id(key)}: {cnv_status!r}"
            )
        major: int | str = ""
        minor: int | str = ""
        total: int | str = ""
        model_include = "no"
        prior_text = ""
        candidates = ""
        if cnv_status in {"unmapped_segment", "segment_overlap"}:
            model_status = f"excluded_{cnv_status}"
        else:
            major = _strict_integer(cn.get("major_cn"), "major_cn")
            minor = _strict_integer(cn.get("minor_cn"), "minor_cn")
            total = _strict_integer(cn.get("total_cn"), "total_cn")
            if major < minor or total != major + minor:
                raise ValueError(
                    f"invalid CN state for {_mutation_id(key)}: {major}/{minor}/{total}"
                )
            if cnv_status == "cn_zero":
                if total != 0:
                    raise ValueError(f"cn_zero row has nonzero CN for {_mutation_id(key)}")
                model_status = "excluded_cn_zero"
            else:
                if total <= 0:
                    raise ValueError(
                        f"mapped_nonzero_cn row has zero CN for {_mutation_id(key)}"
                    )
                if bulk_depth == 0:
                    model_status = "excluded_zero_depth"
                else:
                    model_include = "yes"
                    model_status = "eligible"
                    prior = multiplicity_prior(major, minor)
                    candidates = ";".join(str(value) for value in prior)
                    prior_text = _format_prior(prior)

        row = {
            "mutation_id": _mutation_id(key),
            "chrom": key[0],
            "pos": key[1],
            "ref": key[2],
            "alt": key[3],
            "bulk_ref": bulk_ref,
            "bulk_alt": bulk_alt,
            "bulk_depth": bulk_depth,
            "hp1_1_ref": hp1_ref,
            "hp1_1_alt": hp1_alt,
            "hp2_1_ref": hp2_ref,
            "hp2_1_alt": hp2_alt,
            "major_cn": major,
            "minor_cn": minor,
            "total_cn": total,
            "rho_ASCAT": f"{rho_ascat:.12g}",
            "multiplicity_candidates": candidates,
            "multiplicity_prior": prior_text,
            "model_include": model_include,
            "model_status": model_status,
            # Optional audit metadata.  It is intentionally outside
            # MODEL_REQUIRED_COLUMNS and must not enter the likelihood.
            "phased_gt": bulk.get("phased_gt", ""),
            "cnv_status": cnv_status,
            "segment_id": cn.get("segment_id", ""),
            "loh_state": cn.get("loh_state", ""),
            "cnv_confidence": cn.get("cnv_confidence", ""),
            "somatic_hp_evidence_status": hp_status,
        }
        statuses[model_status] += 1
        output.append(row)
    return output, statuses


def _validate_output_rows(
    rows: Sequence[Mapping[str, Any]], expected_sites: int, expected_purity: float
) -> dict[str, Any]:
    issues: list[str] = []
    identifiers: set[str] = set()
    status_counts: Counter[str] = Counter()
    for row in rows:
        identifier = str(row.get("mutation_id", ""))
        if not identifier or identifier in identifiers:
            issues.append(f"duplicate or missing mutation_id: {identifier!r}")
        identifiers.add(identifier)
        status_counts[str(row.get("model_status", ""))] += 1
        if abs(float(row["rho_ASCAT"]) - expected_purity) > 1e-12:
            issues.append(f"{identifier}: rho_ASCAT differs from ASCAT source")
        include = row.get("model_include") == "yes"
        if include != (row.get("model_status") == "eligible"):
            issues.append(f"{identifier}: model_include/status mismatch")
        if include:
            prior = parse_prior(str(row.get("multiplicity_prior", "")))
            candidates = [
                int(value)
                for value in str(row.get("multiplicity_candidates", "")).split(";")
                if value
            ]
            if not prior or sorted(prior) != candidates:
                issues.append(f"{identifier}: multiplicity support mismatch")
            elif abs(sum(prior.values()) - 1.0) > 1e-9:
                issues.append(f"{identifier}: multiplicity prior does not sum to one")
            elif max(prior) > int(row["major_cn"]):
                issues.append(f"{identifier}: multiplicity exceeds major CN")
        elif row.get("multiplicity_prior") or row.get("multiplicity_candidates"):
            issues.append(f"{identifier}: excluded row carries multiplicity prior")
    forbidden = sorted(set(OUTPUT_COLUMNS) & set(MODEL_FORBIDDEN_COLUMNS))
    checks = {
        "expected_site_count": len(rows) == expected_sites,
        "unique_mutation_ids": len(identifiers) == len(rows),
        "eligible_sites_present": status_counts["eligible"] > 0,
        "required_columns_declared": set(MODEL_REQUIRED_COLUMNS).issubset(OUTPUT_COLUMNS),
        "forbidden_columns_absent": not forbidden,
        "all_rows_valid": not issues,
    }
    return {
        "schema_version": MODEL_INPUT_SCHEMA_VERSION,
        "status": "pass" if all(checks.values()) else "fail",
        "rows": len(rows),
        "eligible_rows": status_counts["eligible"],
        "excluded_rows": len(rows) - status_counts["eligible"],
        "model_status_counts": dict(status_counts),
        "checks": checks,
        "issues_preview": issues[:20],
        "active_model_columns": list(MODEL_REQUIRED_COLUMNS),
        "optional_audit_columns": list(OPTIONAL_AUDIT_COLUMNS),
        "forbidden_columns": list(MODEL_FORBIDDEN_COLUMNS),
        "ps_model_role": "provenance_qc_and_grouped_holdout_only",
    }


def build_model_table(
    inputs: BuildInputs,
    outdir: Path,
    *,
    command: Sequence[str] = (),
) -> BuildResult:
    """Build and atomically publish the canonical likelihood input bundle."""

    inputs.validate()
    command = tuple(str(value) for value in command)
    outdir = Path(outdir)
    table_path = outdir / "likelihood_input.tsv.gz"
    qa_path = outdir / "input_qa.json"
    manifest_path = outdir / "manifest.json"
    existing = [path for path in (table_path, qa_path, manifest_path) if path.exists()]
    if existing:
        raise FileExistsError(
            "refusing to overwrite immutable input bundle: "
            + ", ".join(str(path) for path in existing)
        )

    count_paths = {
        "bulk_counts": inputs.counts_dir / "snv_bulk_counts.tsv.gz",
        "hp_counts": inputs.counts_dir / "snv_hp_counts.tsv.gz",
        "hp_qc": inputs.counts_dir / "snv_hp_qc.tsv.gz",
        "count_manifest": inputs.counts_dir / "site_counts_manifest.json",
    }
    for path in (*count_paths.values(), inputs.site_cnv_qc, inputs.purity.source):
        if not path.is_file():
            raise FileNotFoundError(path)

    observed_purity = read_ascat_purity(
        inputs.purity.source, expected_sample=inputs.purity.sample
    )
    if abs(observed_purity["value"] - inputs.purity.value) > 1e-12:
        raise ValueError(
            "PuritySpec does not match ASCAT purity file: "
            f"spec={inputs.purity.value}, file={observed_purity['value']}"
        )

    bulk = _load_unique(count_paths["bulk_counts"], "bulk")
    hp = _load_hp(count_paths["hp_counts"])
    cn = _load_unique(inputs.site_cnv_qc, "site-CNV")
    if len(bulk) != inputs.expected_sites:
        raise ValueError(
            f"site count mismatch: expected {inputs.expected_sites}, observed {len(bulk)}"
        )
    _validate_count_manifest(count_paths["count_manifest"], inputs.expected_sites)
    _validate_hp_qc(count_paths["hp_qc"], set(bulk))

    rows, source_statuses = _build_rows(bulk, hp, cn, observed_purity["value"])
    qa = _validate_output_rows(rows, inputs.expected_sites, observed_purity["value"])
    qa["source_status_counts"] = dict(source_statuses)
    if qa["status"] != "pass":
        raise ValueError(f"canonical input QA failed: {qa['issues_preview']}")

    atomic_write_gzip_tsv(table_path, rows, OUTPUT_COLUMNS)
    atomic_write_json(qa_path, qa)

    source_records = {
        name: file_record(path) for name, path in count_paths.items()
    }
    source_records["site_cnv_qc"] = file_record(inputs.site_cnv_qc)
    source_records["ascat_purity"] = file_record(inputs.purity.source)
    module_root = Path(__file__).resolve().parent
    manifest = {
        "schema_version": MODEL_INPUT_SCHEMA_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "command": {
            "argv": list(command),
            "shell_rendered": shlex.join(command) if command else "",
        },
        "software": {
            "package": "tumor_tree_pipeline",
            "version": __version__,
            "python": platform.python_version(),
            "implementation_sha256": {
                name: sha256_file(module_root / name)
                for name in ("contracts.py", "input_table.py", "provenance.py")
            },
        },
        "purity": {
            "parameter": "rho_ASCAT",
            "value": observed_purity["value"],
            "expected_sample": inputs.purity.sample,
            "observed_sample": observed_purity["sample"],
            "source_path": str(inputs.purity.source.resolve()),
            "source_sha256": source_records["ascat_purity"]["sha256"],
            "role": "fixed global likelihood input; never used to build multiplicity_prior",
        },
        "multiplicity": {
            "field": "multiplicity_prior",
            "rule": "equal mass across extant major/minor homolog sides, then uniform over m=1..side_CN",
            "uses": ["major_cn", "minor_cn"],
            "does_not_use": ["bulk_ref", "bulk_alt", "bulk_depth", "VAF", "rho_ASCAT"],
        },
        "ps": {
            "active_model_input": False,
            "role": "provenance_qc_and_grouped_holdout_only",
        },
        "sources": source_records,
        "outputs": {
            "likelihood_input": file_record(table_path),
            "input_qa": file_record(qa_path),
        },
        "site_universe": {
            "expected_sites": inputs.expected_sites,
            "observed_sites": len(rows),
            "eligible_sites": qa["eligible_rows"],
            "model_status_counts": qa["model_status_counts"],
        },
        "active_model_columns": list(MODEL_REQUIRED_COLUMNS),
        "optional_audit_columns": list(OPTIONAL_AUDIT_COLUMNS),
        "forbidden_columns": list(MODEL_FORBIDDEN_COLUMNS),
    }
    atomic_write_json(manifest_path, manifest)
    return BuildResult(
        table=table_path,
        qa=qa_path,
        manifest=manifest_path,
        rows=len(rows),
        eligible_rows=qa["eligible_rows"],
    )
