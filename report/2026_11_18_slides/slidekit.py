"""Shared kit for the 2026-11-18 deck (copied from the 11-11 deck): the learning site's drawing language on slides.

Figures are drawn with the site's `S` helper (cells are circles, chromosomes are bars, a mutation is a red
star) on a 1200 x H canvas, then shown 1664 px wide. CSS variables become fixed hex colors (F-4), and the
site's text classes become inline font sizes that stay >= 24 px after scaling.

Usage in a page script:
    from slidekit import S, page, write_page
    s = S("p9", 1200, 460); ...draw...
    write_page("p9-balance", page("p9-balance", eyebrow, title, s, caption, notes))
"""
import re
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[1] / "research/literature/surveys/tumor_evolution_history_2026-11-05/site"
sys.path.insert(0, str(SITE))
import lib  # noqa: E402

# Text classes at slide size: 1200-wide canvas shown at 1664 px (x1.387), so 18 -> 25 px.
SIZES = {"t": 20, "s": 18, "h": 22, "b": 20, "n": 18, "big": 30}
lib.SIZES.update(SIZES)
S = lib.S
PROBLEMS = lib.PROBLEMS

# F-4 colors plus the site's light theme. dad/mom bars stand for HP1/HP2 on these slides.
COLORS = {
    "paper": "#FBFBF8", "panel": "#EEF2EF", "panel2": "#DFE6E1", "panel3": "#BCC7C0",
    "ink": "#1F2A37", "ink2": "#46574F", "mute": "#5A6A62", "line": "#D4DCD6", "line2": "#8A9A91",
    "read": "#D8DFDA", "normal": "#E3E8E4", "cellline": "#6F7F76", "fishline": "#FFFFFF",
    "dad": "#2C5F9E", "mom": "#D9772B", "hp1": "#2C5F9E", "hp2": "#D9772B",
    "hp1l": "#8FB3E0", "hp2l": "#F2B880", "unphased": "#9AA3AE",
    "mut": "#D23A2E", "star2": "#1A3A78", "star3": "#46574F",
    "c1": "#2EA57F", "c2": "#8456C4", "c3": "#D8A31E", "c4": "#2F8F6A",
    "drug": "#7B2D4E", "vessel": "#C2697B", "gene": "#2F8F6A", "hl": "#FBEEB4", "on": "#FFFFFF",
    "stok": "#2F8F6A", "stdis": "#8B5E3C", "stgap": "#6A6A86",
}
WEIGHT = {"h": 700, "b": 700, "big": 700}
FONT = "Noto Sans TC, Arial, sans-serif"
MONO = "JetBrains Mono, Courier New, monospace"

DECK_TITLE = "2026-11-18 HP 加進樹重建：模擬與 HG008"
ORDER = ["outline", "tasks", "ref-tree", "papers", "sim-method", "sim-result", "sim-why", "hg-plan", "hg-nist", "hg-clairs", "hg-rebuild", "decide", "ai-env"]
SECTIONS = {
 "outline": "接回上次會議",
 "tasks": "本週任務",
 "ref-tree": "結果：HG008 參考樹",
 "papers": "結果：論文與 HP 比例",
 "sim-method": "模擬驗證：方案",
 "sim-result": "模擬驗證：結果",
 "sim-why": "模擬驗證：結果",
 "hg-plan": "HG008 驗證：方案",
 "hg-nist": "HG008 驗證：結果",
 "hg-clairs": "HG008 驗證：結果",
 "hg-rebuild": "HG008 驗證：結果",
 "decide": "請老師決定",
 "ai-env": "AI 環境改善"
}


def svg_markup(s, label):
    """The site SVG with hex colors and inline fonts, sized to the slide."""
    raw = s.svg(label)
    raw = re.sub(r"var\(--([a-z0-9]+)\)", lambda m: COLORS[m.group(1)], raw)

    def fix_text(m):
        attrs = m.group(1)
        cls = re.search(r'class="(\w+)"', attrs).group(1)
        size, weight = SIZES[cls], WEIGHT.get(cls, 400)
        fam = MONO if cls == "n" else FONT
        fill = re.search(r"fill:(#[0-9A-Fa-f]{6})", attrs)
        color = fill.group(1) if fill else (COLORS["ink2"] if cls == "s" else COLORS["ink"])
        attrs = re.sub(r'\s*class="\w+"', "", attrs)
        attrs = re.sub(r'\s*style="fill:#[0-9A-Fa-f]{6}"', "", attrs)
        return f'<text{attrs} font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{color}">'
    raw = re.sub(r"<text([^>]*)>", fix_text, raw)
    width = 1664
    height = round(width * s.h / s.w)
    raw = raw.replace("<svg ", f'<svg width="{s.w}" height="{s.h}" style="width:{width}px; height:{height}px" ', 1)
    if len(raw.encode()) > 52_000:
        PROBLEMS.append(f"{s.name}: svg {len(raw.encode())} bytes > 52 KB")
    return raw


def page(pid, title, s, caption="", notes="", label=None):
    """One slide: section label, title (the conclusion), the figure, at most one caption line, footer, notes."""
    n = ORDER.index(pid) + 1
    total = len(ORDER)
    cap = (f'<p style="font-size:30px; line-height:1.35; color:#46574F">{escape(caption)}</p>' if caption else "")
    return f"""<section id="{pid}" style="background:#FBFBF8; color:#1F2A37; font-family:'Noto Sans TC', Arial, sans-serif; display:flex; flex-direction:column; gap:18px; padding:88px 128px 150px">
<p style="font-size:24px; font-weight:700; letter-spacing:2px; color:#2C5F9E">{escape(SECTIONS[pid])}</p>
<h2 style="font-family:'Noto Serif TC', Georgia, serif; font-size:50px; font-weight:700; line-height:1.18; color:#1F2A37">{escape(title)}</h2>
{svg_markup(s, label or title)}
{cap}
<div style="position:absolute; left:128px; right:128px; bottom:64px; display:flex; flex-direction:row; justify-content:space-between">
<p style="font-size:24px; color:#5A6A62">{escape(DECK_TITLE)}</p>
<p style="font-size:24px; color:#5A6A62">{n} / {total}</p>
</div>
<aside>{escape(notes)}</aside>
</section>
"""


def write_page(pid, html):
    out = HERE / "project" / "slides" / f"{pid}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out.name, "problems so far:", len(PROBLEMS))
    for p in PROBLEMS:
        print("  ", p)


# Small shared pictograms ------------------------------------------------------------

def tag(s, x, y, text, kind="real"):
    """A pill: 實際結果 / 示意 / 推論 (E-3)."""
    col = {"real": "c4", "demo": "line2", "infer": "stdis"}[kind]
    w = lib.width(text, SIZES["s"]) + 24
    s.rect(x, y - 21, w, 30, None, col, r=15, sw=2)
    s.text(x + w / 2, y, text, "s", "middle", col)
    return w
