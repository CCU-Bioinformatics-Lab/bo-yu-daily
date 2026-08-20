"""Build a deterministic, BAM-free 20-site input-contract fixture."""

from __future__ import annotations

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from .provenance import (
    atomic_write_gzip_tsv,
    atomic_write_json,
    atomic_write_text,
    canonical_chrom,
    file_record,
    normalize_ascat_segments,
    project_sites_to_ascat,
    read_ascat_purity,
    read_tsv,
    sha256_file,
)


FIXTURE_NAME = "hcc1395_tp20_v1"
FIXTURE_SEED = "hcc1395_tp20_v1"
HP_TAGS = (".", "1", "2", "3", "4", "1-1", "2-1", "1-2", "2-2", "other")
REQUIRED_ELIGIBLE_FEATURES = (
    "major3_minor1",
    "cn1",
    "cn_gain",
    "diploid",
    "loh_like",
    "hp1_alt",
    "hp2_alt",
    "primary_hp_missing",
)


def _key(row: Mapping[str, Any]) -> tuple[str, int, str, str]:
    return (
        canonical_chrom(row["chrom"]),
        int(row["pos"]),
        str(row["ref"]).upper(),
        str(row["alt"]).upper(),
    )


def _identifier(key: tuple[str, int, str, str]) -> str:
    return f"{key[0]}:{key[1]}:{key[2]}>{key[3]}"


def _score(key: tuple[str, int, str, str], seed: str) -> str:
    return hashlib.sha256(f"{seed}|{_identifier(key)}".encode()).hexdigest()


def _portable_artifact_record(path: Path, root: Path) -> dict[str, Any]:
    """Hash fixture content without embedding build time or workspace path."""

    return {
        "path": str(path.relative_to(root)),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _group_hp(rows: Iterable[Mapping[str, str]]) -> dict[tuple[str, int, str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, int, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[_key(row)].append(dict(row))
    for key, site_rows in grouped.items():
        tags = [row["hp_tag"] for row in site_rows]
        if len(tags) != len(HP_TAGS) or set(tags) != set(HP_TAGS):
            raise ValueError(f"source HP domain is invalid for {_identifier(key)}")
    return grouped


def _features(
    cn: Mapping[str, str], hp_rows: Iterable[Mapping[str, str]]
) -> set[str]:
    if cn.get("cnv_status") != "mapped_nonzero_cn":
        return set()
    major = int(cn["major_cn"])
    minor = int(cn["minor_cn"])
    total = int(cn["total_cn"])
    hp_alt = {row["hp_tag"]: int(row["alt_count"]) for row in hp_rows}
    features: set[str] = set()
    if total == 1:
        features.add("cn1")
    if total == 2:
        features.add("diploid")
    if total > 2:
        features.add("cn_gain")
    if minor == 0 and total > 0:
        features.add("loh_like")
    if hp_alt.get("1-1", 0) > 0:
        features.add("hp1_alt")
    if hp_alt.get("2-1", 0) > 0:
        features.add("hp2_alt")
    if hp_alt.get("1-1", 0) + hp_alt.get("2-1", 0) == 0:
        features.add("primary_hp_missing")
    # Keep the explicit state available in the fixture manifest.
    features.add(f"major{major}_minor{minor}")
    return features


def _select(
    bulk: Mapping[tuple[str, int, str, str], Mapping[str, str]],
    hp: Mapping[tuple[str, int, str, str], list[dict[str, str]]],
    cn: Mapping[tuple[str, int, str, str], Mapping[str, str]],
    *,
    seed: str,
) -> tuple[list[tuple[str, int, str, str]], dict[tuple[str, int, str, str], list[str]]]:
    if not set(bulk) == set(hp) == set(cn):
        raise ValueError("fixture source bulk/HP/CN site universes differ")
    strata = {key: sorted(_features(cn[key], hp[key])) for key in bulk}
    eligible = [
        key
        for key in bulk
        if cn[key].get("cnv_status") == "mapped_nonzero_cn"
        and int(bulk[key].get("bulk_usable_depth", bulk[key].get("bulk_depth", "0"))) > 0
    ]
    eligible.sort(key=lambda key: _score(key, seed))
    selected: list[tuple[str, int, str, str]] = []
    for feature in REQUIRED_ELIGIBLE_FEATURES:
        candidate = next(
            (key for key in eligible if feature in strata[key] and key not in selected),
            None,
        )
        if candidate is None:
            raise ValueError(f"fixture source has no distinct eligible site for {feature}")
        selected.append(candidate)
    remaining = [key for key in eligible if key not in selected]
    selected.extend(remaining[: 16 - len(selected)])
    if len(selected) != 16:
        raise ValueError(f"fixture requires 16 eligible sites, found {len(selected)}")
    for status in ("cn_zero", "unmapped_segment"):
        candidates = sorted(
            (key for key in bulk if cn[key].get("cnv_status") == status),
            key=lambda key: _score(key, seed),
        )
        if len(candidates) < 2:
            raise ValueError(f"fixture source requires two {status} sites")
        selected.extend(candidates[:2])
    if len(set(selected)) != 20:
        raise AssertionError("fixture selection is not 20 unique sites")
    return sorted(selected), strata


def generate_hcc1395_tp20_fixture(
    *,
    source_counts_dir: Path,
    purity_file: Path,
    outdir: Path,
    site_cnv_qc: Path | None = None,
    ascat_segments: Path | None = None,
    seed: str = FIXTURE_SEED,
) -> Path:
    """Create the checked-in 20-site fixture from validated count tables.

    ``site_cnv_qc`` may be supplied directly.  Otherwise ASCAT segments are
    normalized and projected onto the count-table sites; neither path reads a
    BAM.
    """

    source_counts_dir = Path(source_counts_dir)
    outdir = Path(outdir)
    source_paths = {
        "bulk_counts": source_counts_dir / "snv_bulk_counts.tsv.gz",
        "hp_counts": source_counts_dir / "snv_hp_counts.tsv.gz",
        "hp_qc": source_counts_dir / "snv_hp_qc.tsv.gz",
        "count_manifest": source_counts_dir / "site_counts_manifest.json",
        "ascat_purity": Path(purity_file),
    }
    for path in source_paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    bulk_rows = read_tsv(source_paths["bulk_counts"])
    hp_rows = read_tsv(source_paths["hp_counts"])
    hp_qc_rows = read_tsv(source_paths["hp_qc"])
    bulk = {_key(row): row for row in bulk_rows}
    if len(bulk) != len(bulk_rows):
        raise ValueError("duplicate bulk source keys")
    hp = _group_hp(hp_rows)
    hp_qc = {_key(row): row for row in hp_qc_rows}
    if len(hp_qc) != len(hp_qc_rows):
        raise ValueError("duplicate HP-QC source keys")

    if site_cnv_qc is not None:
        source_paths["site_cnv_qc"] = Path(site_cnv_qc)
        cn_rows = read_tsv(Path(site_cnv_qc))
    else:
        if ascat_segments is None:
            raise ValueError("provide site_cnv_qc or ascat_segments")
        source_paths["ascat_segments"] = Path(ascat_segments)
        raw_segments = read_tsv(Path(ascat_segments))
        normalized_segments = normalize_ascat_segments(raw_segments)
        cn_rows = project_sites_to_ascat(bulk_rows, normalized_segments)
    cn = {_key(row): row for row in cn_rows}
    if len(cn) != len(cn_rows):
        raise ValueError("duplicate site-CN source keys")

    selected, strata = _select(bulk, hp, cn, seed=seed)
    selected_set = set(selected)
    selected_bulk = [bulk[key] for key in selected]
    selected_hp = [row for key in selected for row in hp[key]]
    selected_qc = [hp_qc[key] for key in selected]
    selected_cn = [cn[key] for key in selected]
    counts_outdir = outdir / "counts"
    atomic_write_gzip_tsv(
        counts_outdir / "snv_bulk_counts.tsv.gz",
        selected_bulk,
        list(bulk_rows[0]),
    )
    atomic_write_gzip_tsv(
        counts_outdir / "snv_hp_counts.tsv.gz",
        selected_hp,
        list(hp_rows[0]),
    )
    atomic_write_gzip_tsv(
        counts_outdir / "snv_hp_qc.tsv.gz",
        selected_qc,
        list(hp_qc_rows[0]),
    )
    cn_fields = [
        "chrom",
        "pos",
        "ref",
        "alt",
        "vcf_ps",
        "cnv_status",
        "segment_id",
        "major_cn",
        "minor_cn",
        "total_cn",
        "loh_state",
        "cnv_confidence",
        "segment_count",
    ]
    atomic_write_gzip_tsv(outdir / "site_cnv_qc.tsv.gz", selected_cn, cn_fields)
    purity_text = Path(purity_file).read_text(encoding="utf-8")
    atomic_write_text(outdir / "purity_ploidy.txt", purity_text)
    purity = read_ascat_purity(outdir / "purity_ploidy.txt", expected_sample="HCC1395")

    count_manifest = {
        "fixture": FIXTURE_NAME,
        "selection_seed": seed,
        "sample": "HCC1395",
        "output_sites": 20,
        "hp_rows": 200,
        "hp_domain": list(HP_TAGS),
        "single_site_only": True,
        "same_read_joint_evidence": False,
        "source_count_manifest": file_record(source_paths["count_manifest"]),
    }
    atomic_write_json(counts_outdir / "site_counts_manifest.json", count_manifest)

    expected_status = {
        "mapped_nonzero_cn": "eligible",
        "cn_zero": "excluded_cn_zero",
        "unmapped_segment": "excluded_unmapped_segment",
    }
    selection = [
        {
            "mutation_id": _identifier(key),
            "selection_sha256": _score(key, seed),
            "strata": strata[key],
            "source_cnv_status": cn[key]["cnv_status"],
            "expected_model_status": expected_status[cn[key]["cnv_status"]],
        }
        for key in selected
    ]
    artifact_paths = {
        "bulk_counts": counts_outdir / "snv_bulk_counts.tsv.gz",
        "hp_counts": counts_outdir / "snv_hp_counts.tsv.gz",
        "hp_qc": counts_outdir / "snv_hp_qc.tsv.gz",
        "count_manifest": counts_outdir / "site_counts_manifest.json",
        "site_cnv_qc": outdir / "site_cnv_qc.tsv.gz",
        "ascat_purity": outdir / "purity_ploidy.txt",
    }
    fixture_manifest = {
        "fixture": FIXTURE_NAME,
        "selection_seed": seed,
        "selection_rule": "minimum SHA256(seed|mutation_id), with distinct required strata selected first",
        "source_artifacts": {
            name: file_record(path) for name, path in source_paths.items()
        },
        "fixture_artifacts": {
            name: _portable_artifact_record(path, outdir)
            for name, path in artifact_paths.items()
        },
        "purity": purity,
        "expected": {
            "rows": 20,
            "eligible": 16,
            "excluded_cn_zero": 2,
            "excluded_unmapped_segment": 2,
            "hp_rows": 200,
        },
        "required_eligible_features": list(REQUIRED_ELIGIBLE_FEATURES),
        "mutation_ids": [_identifier(key) for key in selected],
        "selection": selection,
        "bam_read_required": False,
    }
    if len(selected_set) != fixture_manifest["expected"]["rows"]:
        raise AssertionError("fixture row-count invariant failed")
    manifest_path = outdir / "fixture_manifest.json"
    atomic_write_json(manifest_path, fixture_manifest)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-counts-dir", type=Path, required=True)
    parser.add_argument("--purity-file", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--site-cnv-qc", type=Path)
    inputs.add_argument("--ascat-segments", type=Path)
    parser.add_argument("--seed", default=FIXTURE_SEED)
    args = parser.parse_args()
    manifest = generate_hcc1395_tp20_fixture(
        source_counts_dir=args.source_counts_dir,
        purity_file=args.purity_file,
        outdir=args.outdir,
        site_cnv_qc=args.site_cnv_qc,
        ascat_segments=args.ascat_segments,
        seed=args.seed,
    )
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
