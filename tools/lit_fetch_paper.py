#!/usr/bin/env python3
"""Fetch a paper as plain text from NCBI: PMC full text if available, else the PubMed abstract.

Usage: python3 -I tools/lit_fetch_paper.py <DOI> <short_id> [<out_dir>]
Writes <out_dir>/<short_id>.txt, whose first line says FULLTEXT or ABSTRACT_ONLY.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DEFAULT_OUT = Path("research/literature/surveys/tumor_evolution_history_2026-11-05/fulltext_cache")
SKIP_TAGS = {"ref-list", "table-wrap-foot", "xref", "fn-group", "ack"}


def get(endpoint, **params):
    url = EUTILS + endpoint + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:  # rate limit (429) or transient failure: back off and retry
            last = e
            time.sleep(2 + attempt * 3)
    raise SystemExit(f"NCBI request failed: {last}")


def esearch(db, term):
    body = get("esearch.fcgi", db=db, term=term, retmode="json")
    return json.loads(body)["esearchresult"]["idlist"]


def text_of(el):
    if el.tag in SKIP_TAGS:
        return el.tail or ""
    parts = [el.text or ""]
    for child in el:
        parts.append(text_of(child))
    if el.tag in {"p", "title", "article-title", "abstract", "sec", "td", "th", "tr"}:
        parts.append("\n")
    parts.append(el.tail or "")
    return "".join(parts)


def main():
    doi, short_id = sys.argv[1], sys.argv[2]
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{short_id}.txt"

    # The PMC [DOI] search can return an unrelated article, so check the DOI inside each record.
    for pmc_id in esearch("pmc", f'"{doi}"[DOI]')[:5]:
        root = ET.fromstring(get("efetch.fcgi", db="pmc", id=pmc_id, rettype="xml"))
        article = root.find(".//article")
        if article is None or article.find(".//body") is None:
            continue
        ids = [(e.text or "").strip().lower() for e in article.findall("./front/article-meta/article-id")]
        if doi.lower() not in ids:
            continue
        parts = []
        for path in (".//article-title", ".//abstract", ".//body"):
            el = article.find(path)
            if el is not None:
                parts.append(text_of(el))
        text = re.sub(r"\n\s*\n+", "\n", "\n".join(parts))
        out.write_text(f"FULLTEXT PMC{pmc_id} doi:{doi}\n{text}", encoding="utf-8")
        print(f"FULLTEXT PMC{pmc_id} {len(text)} chars -> {out}\nTITLE: {text[:150]!r}")
        return

    pubmed = esearch("pubmed", f"{doi}[AID]")
    if len(pubmed) != 1:
        raise SystemExit(f"NOT FOUND uniquely in PubMed ({len(pubmed)} hits): {doi}. Check the DOI, or use WebFetch and say so.")
    text = get("efetch.fcgi", db="pubmed", id=pubmed[0], rettype="abstract", retmode="text").decode("utf-8")
    if doi.lower() not in text.lower():
        raise SystemExit(f"PubMed record {pubmed[0]} does not contain DOI {doi}.")
    out.write_text(f"ABSTRACT_ONLY PMID{pubmed[0]} doi:{doi}\n{text}", encoding="utf-8")
    print(f"ABSTRACT_ONLY PMID{pubmed[0]} {len(text)} chars -> {out}\nTITLE: {text[:200]!r}")


if __name__ == "__main__":
    main()
