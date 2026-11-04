"""Lint a slide deck against the mechanical rules in report/report_rule.md.

usage: python3 tools/check_slides.py report/<deck>/ [--titles]

Reads <deck>/project/deck.json and <deck>/project/slides/<id>.html.
Checks every slide in deck.json "order":
  P-7  footer "n / N" equals the slide's position in order / len(order).
       Every slide needs the footer. Only an old deck's "cover" at position 1 may omit it.
  banned words on the page and in the speaker notes (<aside>), see RULES.
--titles: also print the slide titles (<h1> or <h2>) in order, for the W-3 story check.

Per-slide exception: put <!-- lint-allow T-5: reason --> in the slide file.
The reason is required. The rule is then skipped for that slide only.
Exit code 1 when any error is found.
"""
import html, json, re, sys
from pathlib import Path

# (rule, where, regex, message). where: page = visible text, notes = <aside>, both.
RULES = [
    ("T-10", "both", r"雜訊", "寫具體現象，例如「VAF 估不準」"),
    ("T-13", "both", r"抽(?!象)", "寫「隨機亂數產生」，不寫「抽」"),
    ("T-12", "both", r"每個 ?sample|多 ?sample|\bs\d\b", "本研究只有一個 sample"),
    ("E-4", "both", r"\bm\d{1,4}\b", "不用資料裡的 SNV 編號，改用 SNV1、SNV2"),
    ("B-7", "both", r"長讀", "術語寫 long read"),
    ("T-5", "both", r"\b(?:C[0-3][ab]?|[BKM]\d{2}|W\d|Phase ?\d|F1(?![- ]?score))\b",
     "內部代號是黑話"),
    ("T-5", "both", r"\b(?:tumour_content|major_cn|minor_cn|g_r|g_v|simulate_tree)\b",
     "程式欄位名是黑話，用白話名稱"),
    ("S-5", "notes", r"[\w.-]+/[\w./-]+|\b\w+\.(?:md|py|tsv|json|h5)\b|\b[0-9a-f]{7,40}\b",
     "講稿不放路徑、檔名或 commit 編號"),
]

FOOTER = re.compile(r">\s*(\d+)\s*/\s*(\d+)\s*<")
ALLOW = re.compile(r"<!--\s*lint-allow\s+([\w-]+)\s*:\s*\S.*?-->")


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def check_slide(sid, src, pos, total):
    errors = []
    allowed = set(ALLOW.findall(src))
    notes = " ".join(text_of(a) for a in re.findall(r"<aside\b.*?</aside>", src, re.S))
    page = text_of(re.sub(r"<aside\b.*?</aside>|<!--.*?-->", " ", src, flags=re.S))

    footers = FOOTER.findall(src)
    if not footers and not (pos == 1 and sid == "cover"):  # W-4: new decks have no cover
        errors.append(("P-7", f"沒有頁尾頁碼，應為 {pos} / {total}"))
    for n, m in footers:
        if (int(n), int(m)) != (pos, total):
            errors.append(("P-7", f"頁尾寫 {n} / {m}，應為 {pos} / {total}"))

    for rule, where, pattern, msg in RULES:
        if rule in allowed:
            continue
        for label, text in (("頁面", page), ("講稿", notes)):
            if where not in ("both", "notes" if label == "講稿" else "page"):
                continue
            hits = sorted(set(re.findall(pattern, text)))
            if hits:
                errors.append((rule, f"{label}出現 {'、'.join(hits)}：{msg}"))
    return errors


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    project = Path(argv[0]) / "project"
    order = json.loads((project / "deck.json").read_text())["order"]
    total, n_err = len(order), 0
    for pos, sid in enumerate(order, 1):
        path = project / "slides" / f"{sid}.html"
        if not path.exists():
            print(f"{sid}: [P-7] order 裡有這頁，但找不到 {path}")
            n_err += 1
            continue
        src = path.read_text()
        for rule, msg in check_slide(sid, src, pos, total):
            print(f"{pos:>2} {sid}: [{rule}] {msg}")
            n_err += 1
        if "--titles" in argv:
            h2 = re.search(r"<h[12]\b.*?</h[12]>", src, re.S)
            print(f"   {pos:>2}. {text_of(h2.group()).strip() if h2 else '（沒有標題）'}")
    print(f"{total} 頁，{n_err} 個錯誤")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
