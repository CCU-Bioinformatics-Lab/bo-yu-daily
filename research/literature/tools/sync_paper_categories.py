#!/usr/bin/env python3
"""Sync paper classification from research/literature/paper_categories.tsv (single source of truth).

Writes:
  1. YAML front-matter at the top of every paper README (and extra_readmes).
  2. Symlink tree research/literature/papers_by_category/<category>/<subtype>/<ID> -> paper directory.
  3. The generated table block inside research/PAPER_CATEGORIES.md.

Usage (from anywhere):
  python3 research/literature/tools/sync_paper_categories.py          # write
  python3 research/literature/tools/sync_paper_categories.py --check  # report drift, exit 1 if any
"""
import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # research/literature/
RESEARCH = ROOT.parent  # TSV dir/readme paths are relative to research/
TSV = ROOT / "paper_categories.tsv"
INDEX = ROOT / "PAPER_CATEGORIES.md"
LINKS = ROOT / "papers_by_category"

CATEGORY_DIRS = {
    "C1": "C1_short_read_or_unspecified",
    "C2": "C2_long_read_feature",
    "C3a": "C3a_sc_truth_x_short_read",
    "C3b": "C3b_sc_truth_x_long_read",
}
CATEGORY_LABELS = {
    "C1": "短讀或未說平台（無 single-cell 真值）",
    "C2": "long-read 特徵輔助建樹（無 single-cell 真值）",
    "C3a": "single-cell 真值樹 × 短讀或未說平台",
    "C3b": "single-cell 真值樹 × long-read 特徵",
}
LIST_FIELDS = {"platform_detail", "long_read_features", "single_cell_tech", "tree_type",
               "cross_tags", "keywords_en", "keywords_zh"}
FM_FIELDS = ["category", "subtype", "sc_truth_strength", "title", "year", "doc_type", "material",
             "platform_class", "platform_detail", "long_read_role", "long_read_features",
             "single_cell_truth", "single_cell_tech", "input_is_single_cell", "tree_type",
             "cross_tags", "keywords_en", "keywords_zh", "summary_zh"]
BEGIN, END = "<!-- BEGIN GENERATED: paper table -->", "<!-- END GENERATED: paper table -->"


def load_rows():
    with TSV.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def split(value):
    return [v.strip() for v in value.split(";") if v.strip()]


def front_matter(row, readme):
    # JSON scalars and flow lists are valid YAML and keep each field on one grep-able line.
    lines = ["---", f"paper_id: {row['id']}"]
    for key in FM_FIELDS:
        value = row[key]
        if key in LIST_FIELDS:
            lines.append(f"{key}: {json.dumps(split(value), ensure_ascii=False)}")
        elif key == "input_is_single_cell":
            lines.append(f"{key}: {value or 'false'}")
        elif key == "year":
            lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        if key == "category":
            lines.append(f"category_label: {json.dumps(CATEGORY_LABELS[value], ensure_ascii=False)}")
    rel_index = os.path.relpath(INDEX, readme.parent)
    lines.append(f"category_index: {json.dumps(rel_index)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def strip_front_matter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1 and "paper_id:" in text[4:end]:
            return text[end + 5:].lstrip("\n")
    return text


def desired_readmes(rows):
    out = {}
    for row in rows:
        for rel in [row["readme"], *split(row["extra_readmes"])]:
            path = RESEARCH / rel
            out[path] = front_matter(row, path) + "\n" + strip_front_matter(path.read_text())
    return out


def desired_links(rows):
    out = {}
    for row in rows:
        link = LINKS / CATEGORY_DIRS[row["category"]] / row["subtype"] / row["id"]
        out[link] = os.path.relpath(RESEARCH / row["dir"], link.parent)
    return out


def md_link(text, target):
    return f"[{text}]({os.path.relpath(RESEARCH / target, INDEX.parent)})"


def table_block(rows):
    parts = [BEGIN, ""]
    for cat in CATEGORY_DIRS:
        sub = [r for r in rows if r["category"] == cat]
        parts.append(f"### {cat}｜{CATEGORY_LABELS[cat]}（{len(sub)} 篇）")
        parts.append("")
        parts.append("| ID | 子類 | 年 | 論文 | 平台（建樹資料） | long-read 角色 | sc 真值 | 一句話 |")
        parts.append("|---|---|---|---|---|---|---|---|")
        for r in sub:
            title = r["title"].replace("|", "/")
            parts.append(
                f"| {md_link(r['id'], r['readme'])} | `{r['subtype']}` | {r['year']} | {title} | "
                f"{r['platform_detail']} | `{r['long_read_role']}` | `{r['single_cell_truth']}`"
                f"（{r['sc_truth_strength']}） | {r['summary_zh']} |")
        parts.append("")
    parts.append(END)
    return "\n".join(parts)


def desired_index(rows):
    text = INDEX.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + table_block(rows) + tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rows = load_rows()
    readmes, links, index = desired_readmes(rows), desired_links(rows), desired_index(rows)

    drift = [p for p, t in readmes.items() if p.read_text() != t]
    drift += [l for l, t in links.items() if not l.is_symlink() or os.readlink(l) != t]
    existing = {p for p in LINKS.rglob("*") if p.is_symlink()} if LINKS.exists() else set()
    drift += sorted(existing - set(links))
    if INDEX.read_text() != index:
        drift.append(INDEX)

    if args.check:
        for p in drift:
            print("drift:", p.relative_to(RESEARCH))
        print(f"{len(rows)} papers; {len(drift)} drifted")
        sys.exit(1 if drift else 0)

    for path, text in readmes.items():
        path.write_text(text)
    if LINKS.exists():
        shutil.rmtree(LINKS)
    for link, target in links.items():
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)
    INDEX.write_text(index)
    print(f"synced {len(rows)} papers, {len(readmes)} READMEs, {len(links)} links")


if __name__ == "__main__":
    main()
