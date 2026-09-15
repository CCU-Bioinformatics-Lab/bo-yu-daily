#!/usr/bin/env python3
"""Extract workbook structure and cell values from XLSX files using stdlib only."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
DOC_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def col_num(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for char in letters:
        n = n * 26 + ord(char) - 64
    return n


def text_of(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(t.text or "" for t in node.findall(".//m:t", NS))


def inspect(path: Path, out_root: Path) -> dict:
    wb_out = out_root / path.stem
    wb_out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = [text_of(si) for si in root.findall("m:si", NS)]
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rel_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in rel_root.findall("r:Relationship", REL_NS)}
        sheets = []
        for sheet in wb.findall("m:sheets/m:sheet", NS):
            name = sheet.attrib["name"]
            state = sheet.attrib.get("state", "visible")
            target = rels[sheet.attrib[DOC_REL]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(zf.read(target))
            dim = root.find("m:dimension", NS)
            merges = [m.attrib["ref"] for m in root.findall("m:mergeCells/m:mergeCell", NS)]
            rows = []
            max_col = 0
            max_row = 0
            formulas = []
            for row in root.findall("m:sheetData/m:row", NS):
                values = []
                for c in row.findall("m:c", NS):
                    ref = c.attrib["r"]
                    typ = c.attrib.get("t")
                    formula_node = c.find("m:f", NS)
                    value_node = c.find("m:v", NS)
                    if typ == "s" and value_node is not None:
                        value = shared[int(value_node.text)]
                    elif typ == "inlineStr":
                        value = text_of(c.find("m:is", NS))
                    elif typ == "b" and value_node is not None:
                        value = "TRUE" if value_node.text == "1" else "FALSE"
                    else:
                        value = value_node.text if value_node is not None else ""
                    if formula_node is not None:
                        formulas.append({"cell": ref, "formula": formula_node.text or "", "cached": value})
                    values.append((ref, value))
                    max_col = max(max_col, col_num(ref))
                    max_row = max(max_row, int(re.search(r"\d+", ref).group(0)))
                rows.append(values)
            safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
            with (wb_out / f"{safe}.cells.tsv").open("w", encoding="utf-8") as handle:
                handle.write("cell\tvalue\n")
                for row in rows:
                    for ref, value in row:
                        handle.write(f"{ref}\t{str(value).replace(chr(9), ' ').replace(chr(10), ' | ')}\n")
            sheets.append({"name": name, "state": state, "dimension": dim.attrib.get("ref") if dim is not None else None,
                           "max_row_seen": max_row, "max_col_seen": max_col, "merges": merges, "formulas": formulas,
                           "cell_dump": f"{safe}.cells.tsv"})
    result = {"workbook": path.name, "sheets": sheets}
    (wb_out / "schema.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    output = Path(sys.argv[1])
    books = [Path(p) for p in sys.argv[2:]]
    summary = [inspect(book, output) for book in books]
    (output / "all_schema.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
