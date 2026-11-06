#!/usr/bin/env python3
"""Check that each quote in a claims TSV occurs verbatim in the fetched source text.

Usage: python3 -I tools/lit_check_quotes.py <claims.tsv> [<more.tsv> ...]
TSV columns (with header): paper_id  doi  source_file  category  claim_zh  quote
source_file is a file name inside the fulltext directory, or WEB:<url> for a page read with
WebFetch (reported as UNCHECKED, because no local copy exists).
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

FULLTEXT = Path("research/literature/surveys/tumor_evolution_history_2026-11-05/fulltext_cache")
csv.field_size_limit(10_000_000)


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    return re.sub(r"\s+", "", s)


def main():
    totals = {"OK": 0, "MISSING": 0, "UNCHECKED": 0, "NOFILE": 0}
    cache = {}
    for path in sys.argv[1:]:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                src = (row.get("source_file") or "").strip()
                quote = (row.get("quote") or "").strip()
                if src.startswith("WEB:"):
                    status = "UNCHECKED"
                else:
                    file = FULLTEXT / src
                    if not file.exists():
                        status = "NOFILE"
                    else:
                        text = cache.setdefault(src, norm(file.read_text(encoding="utf-8")))
                        status = "OK" if quote and norm(quote) in text else "MISSING"
                totals[status] += 1
                if status != "OK":
                    print(f"{status}\t{Path(path).name}\t{row.get('paper_id')}\t{quote[:120]}")
    print("TOTAL", totals)


if __name__ == "__main__":
    main()
