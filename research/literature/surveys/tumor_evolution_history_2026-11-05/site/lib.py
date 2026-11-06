"""Drawing helpers for the tumor evolution primer.

One visual language across the site:
  cells are circles, tumors are clusters of cells, chromosomes are horizontal bars,
  a mutation is always a red star, blue is always dad, orange is always mom,
  clones are green, purple, gold, grey is normal.
S.check() reports labels that leave the viewBox or overlap.
"""
import math
import unicodedata
from html import escape

PROBLEMS = []
SIZES = {"t": 14, "s": 12.5, "h": 15, "b": 14, "n": 13, "big": 22}


def width(text, size):
    return sum(size if unicodedata.east_asian_width(c) in "WF" else size * 0.58 for c in text)


def smooth(points, t):
    """Smoothstep interpolation through (t, value) points."""
    if t <= points[0][0]:
        return points[0][1]
    for (a, va), (b, vb) in zip(points, points[1:]):
        if t <= b:
            u = (t - a) / (b - a)
            u = u * u * (3 - 2 * u)
            return va + (vb - va) * u
    return points[-1][1]


class S:
    def __init__(self, name, w, h):
        self.name, self.w, self.h = name, w, h
        self.items, self.boxes = [], []

    def raw(self, s):
        self.items.append(s)

    def text(self, x, y, s, cls="t", a="start", color=None):
        if not s:
            return
        size = SIZES.get(cls, 14)
        wd = width(s, size)
        x0 = x if a == "start" else (x - wd / 2 if a == "middle" else x - wd)
        self.boxes.append((x0, y - size * 0.85, x0 + wd, y + size * 0.25, s))
        st = f' style="fill:var(--{color})"' if color else ""
        self.items.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{a}"{st}>{escape(s)}</text>')

    def lines(self, x, y, rows, cls="t", a="middle", gap=19, color=None):
        for i, r in enumerate(rows):
            self.text(x, y + i * gap, r, cls, a, color)

    def rect(self, x, y, w, h, fill="panel", stroke=None, r=4, dash=False, sw=1.5, op=None):
        d = ' stroke-dasharray="5 4"' if dash else ""
        o = f";opacity:{op}" if op is not None else ""
        f = "fill:none" if fill is None else f"fill:var(--{fill})"
        st = "stroke:none" if stroke is None else f"stroke:var(--{stroke})"
        self.items.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" style="{f};{st};stroke-width:{sw}{o}"{d}/>')

    def line(self, x1, y1, x2, y2, c="line2", sw=2, dash=False, op=None):
        d = ' stroke-dasharray="5 4"' if dash else ""
        o = f";opacity:{op}" if op is not None else ""
        self.items.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" style="stroke:var(--{c});stroke-width:{sw};stroke-linecap:round{o}"{d}/>')

    def arrow(self, x1, y1, x2, y2, label=None, c="ink2", sw=2.5, dash=False, up=True, head=9):
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
        self.line(x1, y1, bx, by, c, sw, dash)
        p = [(x2, y2), (bx + head * .6 * math.sin(ang), by - head * .6 * math.cos(ang)), (bx - head * .6 * math.sin(ang), by + head * .6 * math.cos(ang))]
        self.poly(p, c)
        if label:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 + (-9 if up else 19), label, "s", "middle")

    def poly(self, pts, fill="ink", stroke=None, sw=1, op=None):
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        st = f"stroke:var(--{stroke});stroke-width:{sw}" if stroke else "stroke:none"
        o = f";opacity:{op}" if op is not None else ""
        self.items.append(f'<polygon points="{d}" style="fill:var(--{fill});{st}{o}"/>')

    def path(self, d, c="line2", sw=2, fill=None, dash=False, op=None):
        f = "fill:none" if fill is None else f"fill:var(--{fill})"
        da = ' stroke-dasharray="5 4"' if dash else ""
        o = f";opacity:{op}" if op is not None else ""
        st = "stroke:none" if c is None else f"stroke:var(--{c})"
        self.items.append(f'<path d="{d}" style="{f};{st};stroke-width:{sw};stroke-linejoin:round;stroke-linecap:round{o}"{da}/>')

    def circle(self, x, y, r, fill="panel", stroke=None, sw=1.5, dash=False, op=None):
        st = f"stroke:var(--{stroke});stroke-width:{sw}" if stroke else "stroke:none"
        d = ' stroke-dasharray="4 3"' if dash else ""
        f = "fill:none" if fill is None else f"fill:var(--{fill})"
        o = f";opacity:{op}" if op is not None else ""
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" style="{f};{st}{o}"{d}/>')

    def star(self, x, y, r=7, fill="mut"):
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * .45
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        self.poly(pts, fill)

    def xmark(self, x, y, r=7, c="mut", sw=3):
        self.line(x - r, y - r, x + r, y + r, c, sw)
        self.line(x - r, y + r, x + r, y - r, c, sw)

    def cell(self, x, y, r=16, fill="normal", stars=(), dash=False, op=None):
        """A cell: a circle with a darker edge; stars show the mutations it carries."""
        self.circle(x, y, r, fill, "cellline", 1.5, dash, op)
        n = len(stars)
        if n:
            sr = min(r * (.42 if n < 3 else .31), 7)
            step = sr * (1.9 if n < 3 else 1.7)
            for i, c in enumerate(stars):
                self.star(x + (i - (n - 1) / 2) * step, y, sr, c)

    def bar(self, x, y, w, c="dad", h=14, dash=False):
        """A chromosome: a horizontal bar. y is the center line."""
        if dash:
            self.rect(x, y - h / 2, w, h, None, c, r=h / 2, dash=True)
        else:
            self.rect(x, y - h / 2, w, h, c, None, r=h / 2)

    def cluster(self, cx, cy, rx, ry, colorfn, r=6, gap=1.0, edge="cellline"):
        """A tumor drawn as a packed cluster of cells inside an ellipse."""
        step = r * 2 * gap
        row = 0
        y = cy - ry
        while y <= cy + ry:
            off = step / 2 if row % 2 else 0
            x = cx - rx + off
            while x <= cx + rx:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    self.circle(x, y, r * .92, colorfn((x - cx) / rx, (y - cy) / ry), edge, .7)
                x += step
            y += step * .88
            row += 1

    def person(self, x, y, h=70, fill="panel3", stroke=None, dash=False):
        """A simple person: head and body. (x, y) is the top center."""
        hr = h * .15
        self.circle(x, y + hr, hr, fill, stroke, 1.5, dash)
        w = h * .23
        top = y + hr * 2 + h * .03
        bot = y + h
        self.path(f"M{x - w:.1f} {bot:.1f} L{x - w:.1f} {top + w:.1f} Q{x - w:.1f} {top:.1f} {x:.1f} {top:.1f} Q{x + w:.1f} {top:.1f} {x + w:.1f} {top + w:.1f} L{x + w:.1f} {bot:.1f} Z",
                  stroke, 1.5, fill, dash)

    def fish(self, x, y, w, h, tree, scale=None, samples=70):
        """A fish plot. tree = (color, [(t, clade share)], [children]); t runs 0 to 1.
        A child grows from inside its parent. scale(t) optionally sets the total size."""
        cy = y + h / 2
        def draw(node, lo, hi, ts):
            color, pts, kids = node
            up = [f"{x + t * w:.1f} {lo[i]:.2f}" for i, t in enumerate(ts)]
            dn = [f"{x + t * w:.1f} {hi[i]:.2f}" for i, t in reversed(list(enumerate(ts)))]
            self.path("M" + " L".join(up + dn) + "Z", "fishline", .8, color)
            n = len(kids)
            if not n:
                return
            spans = [[(smooth(k[1], t) * h * (scale(t) if scale else 1)) for t in ts] for k in kids]
            los = [[0] * len(ts) for _ in kids]
            his = [[0] * len(ts) for _ in kids]
            for i in range(len(ts)):
                total = sum(sp[i] for sp in spans)
                room = max(hi[i] - lo[i] - total, 0)
                g = room / (n + 1)
                cur = lo[i] + g
                for j in range(n):
                    los[j][i] = cur
                    his[j][i] = cur + spans[j][i]
                    cur = his[j][i] + g
            for j, k in enumerate(kids):
                idx = [i for i in range(len(ts)) if spans[j][i] > .01]
                if idx:
                    draw(k, [los[j][i] for i in idx], [his[j][i] for i in idx], [ts[i] for i in idx])
        ts = [i / samples for i in range(samples + 1)]
        tops = [smooth(tree[1], t) * h * (scale(t) if scale else 1) for t in ts]
        idx = [i for i in range(len(ts)) if tops[i] > .01]
        draw(tree, [cy - tops[i] / 2 for i in idx], [cy + tops[i] / 2 for i in idx], [ts[i] for i in idx])

    def check(self):
        for x0, y0, x1, y1, s in self.boxes:
            if x0 < -1 or y0 < -1 or x1 > self.w + 1 or y1 > self.h + 1:
                PROBLEMS.append(f"{self.name}: outside viewBox: {s} ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) of {self.w}x{self.h}")
        for i, a in enumerate(self.boxes):
            for b in self.boxes[i + 1:]:
                if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                    PROBLEMS.append(f"{self.name}: overlap: {a[4]} / {b[4]}")

    def svg(self, label):
        self.check()
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(label)}" '
                f'xmlns="http://www.w3.org/2000/svg">{"".join(self.items)}</svg>')


STATE = {"確定": "ok", "還在爭論": "dis", "還不知道": "gap"}


class Book:
    def __init__(self):
        self.chapters = []
        self.used = set()

    def chapter(self, cid, title, lead):
        self.chapters.append({"id": cid, "title": title, "lead": lead, "figs": [], "n": len(self.chapters)})

    def fig(self, s, title, plain, trap=None, real=None, state=None, src=()):
        """plain: one plain sentence. trap: a common misreading. real: a measured fact. state: how settled it is."""
        ch = self.chapters[-1]
        self.used.update(src)
        no = f"{ch['n']}.{len(ch['figs']) + 1}"
        cite = "".join(f'<a class="src" href="#refs" data-ref="{escape(x)}">{escape(x)}</a>' for x in src)
        st = f'<span class="state st-{STATE[state]}">{state}</span>' if state else ""
        parts = ""
        if trap:
            parts += f'<p class="note"><b>容易誤會：</b>{escape(trap)}</p>'
        if real:
            parts += f'<p class="note"><b>真實資料：</b>{escape(real)}</p>'
        if cite:
            parts += f'<p class="note srcs">來源：{cite}</p>'
        label = "常見誤解和真實資料" if trap and real else ("常見誤解" if trap else ("真實資料" if real else "來源"))
        more = f'<details class="more"><summary>{label}{st}</summary>{parts}</details>' if parts else ""
        ch["figs"].append(f"""<figure id="f{no.replace('.', '-')}">
<h2><span class="no">{no}</span>{escape(title)}</h2>
<div class="draw">{s.svg(title)}</div>
<figcaption>{escape(plain)}</figcaption>{more}
</figure>""")
