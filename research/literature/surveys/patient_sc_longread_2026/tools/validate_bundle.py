#!/usr/bin/env python3
"""Validate a literature bundle and generate provenance manifests from real files."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT.parents[1] / "papers"  # shared research/literature/papers/


def inspect_pdf(path):
    with path.open("rb") as stream:
        header = stream.read(1024)
    if b"%PDF-" not in header:
        raise ValueError("not a PDF (possibly HTML/challenge page)")
    proc = subprocess.run(["pdfinfo", str(path)], text=True, capture_output=True)
    if proc.returncode:
        raise ValueError(proc.stderr.strip())
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.M)
    if not match or int(match[1]) < 1:
        raise ValueError("pdfinfo could not establish positive page count")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"pages": int(match[1]), "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def local_link_errors():
    errors = []
    for path in sorted(ROOT.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = match[1].strip().strip("<>")
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target = re.sub(r":\d+$", "", unquote(urlsplit(target).path))
            if not target:
                continue
            dest = Path(target) if target.startswith("/") else path.parent / target
            if not dest.exists():
                line = content.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(ROOT)}:{line}: broken link {match[1]}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    records, errors = [], []
    papers = catalog["papers"]
    for key in ("id", "doi", "directory"):
        vals = [paper[key] for paper in papers]
        if len(vals) != len(set(vals)):
            errors.append(f"duplicate catalog {key}")
    for paper in papers:
        directory = PAPERS / paper["directory"]
        for name in ("README.md", "paper.txt", "paper.pdf"):
            if not (directory / name).is_file():
                errors.append(f"{paper['id']}: missing {name}")
        text_path = directory / "paper.txt"
        if text_path.is_file():
            extracted = text_path.read_text(encoding="utf-8", errors="replace")
            if len(extracted.strip()) < 3000:
                errors.append(f"{paper['id']}: unexpectedly little extracted paper text")
        notes = directory / "README.md"
        if notes.is_file() and paper["doi"].lower() not in notes.read_text(encoding="utf-8").lower():
            errors.append(f"{paper['id']}: formal DOI missing from notes")
        for pdf in sorted(directory.glob("*.pdf")):
            try:
                info = inspect_pdf(pdf)
            except (OSError, ValueError) as exc:
                errors.append(f"{os.path.relpath(pdf, ROOT)}: {exc}")
                continue
            records.append({
                "id": paper["id"], "selection": paper["selection"],
                "doi": paper["doi"], "file": os.path.relpath(pdf, ROOT),
                "version": paper["pdf_version"] if pdf.name == "paper.pdf" else "supplement",
                "source_url": paper["pdf_url"] if pdf.name == "paper.pdf" else "see paper README",
                **info,
            })
    errors.extend(local_link_errors())
    summary = {
        "date": catalog["cutoff_date"], "catalog_papers": len(papers),
        "A_core": sum(p["selection"] == "A_core" for p in papers),
        "B_core": sum(p["selection"] == "B_core" for p in papers),
        "valid_pdf_files": len(records), "pdf_pages": sum(r["pages"] for r in records),
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        return 1
    if args.write_manifest:
        manifest = {"validation": summary, "files": records}
        (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(records[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
        (ROOT / "manifest.tsv").write_text(buf.getvalue(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
