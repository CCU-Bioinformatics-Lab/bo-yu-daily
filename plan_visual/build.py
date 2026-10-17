"""Assemble plan.html from shell.html and parts/*.html."""
from pathlib import Path

root = Path(__file__).parent
html = (root / "shell.html").read_text(encoding="utf-8")
for name in ("arch", "hp", "c2c3", "c4"):
    part = root / "parts" / f"{name}.html"
    html = html.replace(f"<!--PART:{name}-->", part.read_text(encoding="utf-8"))
(root / "plan.html").write_text(html, encoding="utf-8")
print("wrote", root / "plan.html", len(html), "bytes")
