"""Pure provenance, PS-audit, and ASCAT projection helpers.

The heavy BAM/VCF readers belong in the workflow boundary.  Functions in
this module consume ordinary mappings so they can be tested without opening a
BAM and can be reused by the production wrapper after it has collected read
observations.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import os
import tempfile
from bisect import bisect_right
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


def sha256_file(path: Path, block_size: int = 4 * 1024 * 1024) -> str:
    """Return the content SHA-256 for *path*."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    """Describe a required source artifact with a content hash."""

    if not path.is_file():
        raise FileNotFoundError(path)
    stat = path.stat()
    return {
        "path": str(path.resolve()),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(path),
    }


@contextmanager
def atomic_target(path: Path, *, mode: int = 0o664) -> Iterator[Path]:
    """Yield a same-directory temporary path and atomically install it.

    A same-filesystem ``os.replace`` prevents readers from seeing partial
    tables or manifests.  Failed writes remove the temporary file.
    """

    missing: list[Path] = []
    cursor = path.parent
    while not cursor.exists():
        missing.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    path.parent.mkdir(parents=True, exist_ok=True)
    # Workflow artifacts are shared by the project group.  Re-apply the mode
    # even when the directory already existed so callers do not depend on the
    # launching shell's umask.
    for directory in reversed(missing):
        directory.chmod(0o2775)
    path.parent.chmod(0o2775)
    descriptor, raw_temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(raw_temporary)
    try:
        yield temporary
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_text(path: Path, text: str) -> None:
    with atomic_target(path) as temporary:
        temporary.write_text(text, encoding="utf-8")


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def atomic_write_gzip_tsv(
    path: Path,
    rows: Iterable[Mapping[str, Any]],
    fieldnames: Sequence[str],
) -> None:
    """Write a deterministic gzip TSV and install it atomically."""

    with atomic_target(path) as temporary:
        with temporary.open("wb") as raw_handle:
            # Empty filename and mtime=0 make identical fixture content hash
            # identically across rebuilds.
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw_handle, mtime=0
            ) as gzip_handle:
                with io.TextIOWrapper(
                    gzip_handle, encoding="utf-8", newline=""
                ) as text_handle:
                    writer = csv.DictWriter(
                        text_handle,
                        fieldnames=list(fieldnames),
                        delimiter="\t",
                        lineterminator="\n",
                        extrasaction="ignore",
                    )
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(
                            {
                                field: "" if row.get(field) is None else row.get(field)
                                for field in fieldnames
                            }
                        )


def open_text_table(path: Path):
    return gzip.open(path, "rt", encoding="utf-8", newline="") if path.suffix == ".gz" else path.open("r", encoding="utf-8", newline="")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with open_text_table(path) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames:
            raise ValueError(f"TSV has no header: {path}")
        return list(reader)


def read_ascat_purity(path: Path, *, expected_sample: str | None = None) -> dict[str, Any]:
    """Read exactly one finite purity value from ``purity_ploidy.txt``."""

    rows = read_tsv(path)
    observed: list[tuple[str, float]] = []
    for row in rows:
        raw = str(row.get("purity", "")).strip()
        if not raw:
            continue
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"invalid ASCAT purity in {path}: {raw!r}") from exc
        if not math.isfinite(value) or not 0.0 < value <= 1.0:
            raise ValueError(f"ASCAT purity must be in (0, 1] in {path}: {value!r}")
        sample = str(row.get("sample", row.get("Sample", ""))).strip()
        observed.append((sample, value))
    if len(observed) != 1:
        raise ValueError(
            f"expected exactly one ASCAT purity value in {path}, found {len(observed)}"
        )
    sample, value = observed[0]
    if expected_sample:
        if not sample:
            raise ValueError("ASCAT purity table has no sample provenance")
        if expected_sample.lower() not in sample.lower():
            raise ValueError(
                f"ASCAT purity sample mismatch: expected {expected_sample!r}, observed {sample!r}"
            )
    return {"sample": sample or expected_sample or "", "value": value}


def canonical_chrom(value: Any) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("empty chromosome")
    core = text[3:] if text.lower().startswith("chr") else text
    return f"chr{core}"


def _strict_nonnegative_integer(value: Any, label: str) -> int:
    try:
        numeric = float(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(numeric) or numeric < 0 or not numeric.is_integer():
        raise ValueError(f"{label} must be a non-negative integer: {value!r}")
    return int(numeric)


def normalize_ascat_segments(
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Normalize ASCAT rows to non-overlapping 1-based inclusive segments."""

    normalized: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, 2):
        try:
            chrom = canonical_chrom(row.get("chr", row.get("chrom", "")))
            start = _strict_nonnegative_integer(
                row.get("startpos", row.get("start")), "ASCAT start"
            )
            end = _strict_nonnegative_integer(
                row.get("endpos", row.get("end")), "ASCAT end"
            )
            major = _strict_nonnegative_integer(
                row.get("nMajor", row.get("major_cn")), "ASCAT major CN"
            )
            minor = _strict_nonnegative_integer(
                row.get("nMinor", row.get("minor_cn")), "ASCAT minor CN"
            )
        except ValueError as exc:
            raise ValueError(f"invalid ASCAT row {row_number}: {row}") from exc
        if start < 1 or end < start:
            raise ValueError(f"invalid ASCAT coordinates at row {row_number}: {start}-{end}")
        if major < minor:
            raise ValueError(
                f"ASCAT major CN is smaller than minor CN at row {row_number}: {major}/{minor}"
            )
        total = major + minor
        loh_state = (
            "homozygous_deletion"
            if total == 0
            else "loh_like" if minor == 0 else "non_loh"
        )
        normalized.append(
            {
                "segment_id": str(row.get("segment_id") or f"{chrom}:{start}-{end}"),
                "sample": str(row.get("sample", "")),
                "chr": chrom,
                "start": start,
                "end": end,
                "major_cn": major,
                "minor_cn": minor,
                "total_cn": total,
                "loh_state": loh_state,
                "caller": "ASCAT",
                "confidence": str(row.get("confidence", "global_fit_only")),
            }
        )
    normalized.sort(key=lambda row: (row["chr"], row["start"], row["end"]))
    previous: dict[str, dict[str, Any]] = {}
    for segment in normalized:
        prior = previous.get(segment["chr"])
        if prior and segment["start"] <= prior["end"]:
            raise ValueError(
                "overlapping ASCAT segments: "
                f"{prior['segment_id']} and {segment['segment_id']}"
            )
        previous[segment["chr"]] = segment
    if not normalized:
        raise ValueError("ASCAT segment table is empty")
    return normalized


def project_sites_to_ascat(
    sites: Iterable[Mapping[str, Any]],
    segments: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Project SNVs onto normalized ASCAT segments without imputing CN."""

    by_chrom: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for segment in segments:
        by_chrom[canonical_chrom(segment["chr"])].append(segment)
    index = {
        chrom: ([int(row["start"]) for row in rows], rows)
        for chrom, rows in by_chrom.items()
    }
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str, str]] = set()
    for site in sites:
        chrom = canonical_chrom(site["chrom"])
        pos = _strict_nonnegative_integer(site["pos"], "SNV position")
        ref = str(site["ref"]).upper()
        alt = str(site["alt"]).upper()
        key = (chrom, pos, ref, alt)
        if key in seen:
            raise ValueError(f"duplicate site for ASCAT projection: {key}")
        seen.add(key)
        candidates: list[Mapping[str, Any]] = []
        if chrom in index:
            starts, chromosome_segments = index[chrom]
            candidate_index = bisect_right(starts, pos) - 1
            for offset in range(max(0, candidate_index - 1), min(len(chromosome_segments), candidate_index + 3)):
                segment = chromosome_segments[offset]
                if int(segment["start"]) <= pos <= int(segment["end"]):
                    candidates.append(segment)
        row: dict[str, Any] = {
            **site,
            "chrom": chrom,
            "pos": pos,
            "ref": ref,
            "alt": alt,
            "segment_count": len(candidates),
        }
        if not candidates:
            row.update(
                {
                    "cnv_status": "unmapped_segment",
                    "segment_id": "",
                    "major_cn": "",
                    "minor_cn": "",
                    "total_cn": "",
                    "loh_state": "",
                    "cnv_confidence": "",
                }
            )
        elif len(candidates) > 1:
            row.update(
                {
                    "cnv_status": "segment_overlap",
                    "segment_id": ";".join(str(item["segment_id"]) for item in candidates),
                    "major_cn": "",
                    "minor_cn": "",
                    "total_cn": "",
                    "loh_state": "",
                    "cnv_confidence": "",
                }
            )
        else:
            segment = candidates[0]
            total = int(segment["total_cn"])
            row.update(
                {
                    "cnv_status": "cn_zero" if total == 0 else "mapped_nonzero_cn",
                    "segment_id": segment["segment_id"],
                    "major_cn": int(segment["major_cn"]),
                    "minor_cn": int(segment["minor_cn"]),
                    "total_cn": total,
                    "loh_state": segment["loh_state"],
                    "cnv_confidence": segment.get("confidence", "global_fit_only"),
                }
            )
        output.append(row)
    return output


def normalize_ps(value: Any) -> str:
    return "" if value in (None, "", ".") else str(value)


def audit_ps_site(
    site: Mapping[str, Any],
    read_observations: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Classify one VCF PS against prefiltered read-level observations.

    Each observation has ``query_name``, ``allele`` (``ref``/``alt``), and
    optional ``ps``.  The first observation per query name is used, matching
    the canonical pileup deduplication contract.
    """

    vcf_ps = normalize_ps(site.get("vcf_ps", site.get("ps")))
    all_ps: Counter[str] = Counter()
    alt_ps: Counter[str] = Counter()
    counts: Counter[str] = Counter()
    seen: set[str] = set()
    for index, observation in enumerate(read_observations):
        if observation.get("callable", True) is not True:
            counts["filtered_reads"] += 1
            continue
        query_name = str(observation.get("query_name", f"anonymous_{index}"))
        if query_name in seen:
            counts["duplicate_query_name"] += 1
            continue
        seen.add(query_name)
        allele = str(observation.get("allele", "")).lower()
        if allele not in {"ref", "alt"}:
            counts["other_allele"] += 1
            continue
        counts[f"{allele}_reads"] += 1
        ps = normalize_ps(observation.get("ps"))
        if ps:
            counts["ps_tagged_reads"] += 1
            all_ps[ps] += 1
            if allele == "alt":
                alt_ps[ps] += 1
    alt_match = bool(vcf_ps and vcf_ps in alt_ps)
    any_match = bool(vcf_ps and vcf_ps in all_ps)
    allele_reads = counts["ref_reads"] + counts["alt_reads"]
    if not vcf_ps:
        status = "vcf_ps_missing"
    elif counts["alt_reads"] and alt_match:
        status = "match_alt"
    elif counts["alt_reads"] and alt_ps:
        status = "discordant_alt"
    elif allele_reads == 0:
        status = "no_callable_reads"
    elif counts["ps_tagged_reads"] == 0:
        status = "bam_ps_missing"
    elif any_match:
        status = "match_ref_only"
    else:
        status = "discordant_no_alt_match"
    all_mode, all_mode_count = all_ps.most_common(1)[0] if all_ps else ("", 0)
    alt_mode, alt_mode_count = alt_ps.most_common(1)[0] if alt_ps else ("", 0)
    return {
        **site,
        "vcf_ps": vcf_ps,
        "status": status,
        "bam_ps_mode": all_mode,
        "bam_ps_mode_count": all_mode_count,
        "bam_ps_alt_mode": alt_mode,
        "bam_ps_alt_mode_count": alt_mode_count,
        "bam_ps_alt_match": int(alt_match),
        "bam_ps_any_match": int(any_match),
        "ref_reads": counts["ref_reads"],
        "alt_reads": counts["alt_reads"],
        "allele_reads": allele_reads,
        "ps_tagged_reads": counts["ps_tagged_reads"],
        "duplicate_query_name": counts["duplicate_query_name"],
        "all_ps_counts": ";".join(f"{key}:{value}" for key, value in sorted(all_ps.items())),
        "alt_ps_counts": ";".join(f"{key}:{value}" for key, value in sorted(alt_ps.items())),
    }


def summarize_ps_audit(
    rows: Iterable[Mapping[str, Any]], *, max_discordance_fraction: float = 0.01
) -> dict[str, Any]:
    """Summarize PS audit rows.

    PS is upstream phasing metadata: it helps establish consistent HP labels
    before the count table is built.  The PS value itself remains QC,
    provenance, and grouped-holdout metadata rather than a direct downstream
    model variable.
    """

    if not 0.0 <= max_discordance_fraction <= 1.0:
        raise ValueError("max_discordance_fraction must be in [0, 1]")
    materialized = list(rows)
    statuses = Counter(str(row.get("status", "unknown")) for row in materialized)
    auditable = statuses["match_alt"] + statuses["discordant_alt"]
    discordance = statuses["discordant_alt"] / auditable if auditable else 0.0
    return {
        "status": "pass" if auditable > 0 and discordance <= max_discordance_fraction else "review",
        "selected_sites": len(materialized),
        "status_counts": dict(statuses),
        "auditable_alt_ps_sites": auditable,
        "discordant_alt_sites": statuses["discordant_alt"],
        "discordance_fraction": discordance,
        "max_discordance_fraction": max_discordance_fraction,
        "model_role": "provenance_qc_and_grouped_holdout_only",
    }
