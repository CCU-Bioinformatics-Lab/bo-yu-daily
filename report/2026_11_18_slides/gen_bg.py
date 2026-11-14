"""Background result page of the 2026-11-18 deck: papers (two papers + 50%). The HG008 reference-tree pages moved to gen_ref.py.

Shared pictograms (tube, mark, dice) are also used by gen_ref.py.

Sources (BRIEF R1-R3):
- ref-tree: lab_report/2026-11-07_hg008_tree_rebuild/HOW_TREE_WAS_BUILT.md and README.md (tree shape, branch SNV
  counts 127 / 4 / 31 / 14 / 68 / 17, truncal 7,784); lab_report/2026-11-07_hg008_sc_check/README.md (119 cells,
  111 / 48 / 16 carriers, nesting violations 0). Clone names A-H follow report/2026_11_11_slides/BRIEF.md.
- papers: research/literature/papers/P12_prcgap_8lines_2026/summary.md and P13_colo829_t2t_2026/summary.md
  (「深讀結果」); diplosim/DECISIONS.md 2026-11-12 first row (50% basis: COLO829 0.993 (0.974-1.012),
  HG008 0.97 (0.93-1.01)); ratios from lab_report/2026-11-06_colo829_hap_snv_ratio/ and 2026-11-06_hg008_hap_snv_ratio/.

The tree drawing is copied (and recoloured) from report/2026_11_11_slides/gen_res2.py `hg008_tree`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python3 -I does not add the script folder
from slidekit import S, page, write_page, tag  # noqa: E402
from lib import width  # noqa: E402

RED, PUR, GOLD = "c1", "c2", "c3"     # the three branches single cells support: 127, 14, 68 SNVs


# ---- small pictograms ---------------------------------------------------------------

def tube(s, x, top, w=16, h=32, label=None):
    """One test tube = one clone line."""
    r = w / 2
    body = f"M{x - r:.1f} {top:.1f} L{x - r:.1f} {top + h - r:.1f} A{r:.1f} {r:.1f} 0 0 0 {x + r:.1f} {top + h - r:.1f} L{x + r:.1f} {top:.1f}"
    liquid = f"M{x - r:.1f} {top + h * .45:.1f} L{x - r:.1f} {top + h - r:.1f} A{r:.1f} {r:.1f} 0 0 0 {x + r:.1f} {top + h - r:.1f} L{x + r:.1f} {top + h * .45:.1f} Z"
    s.path(liquid, None, 0, "panel3")
    s.path(body, "ink2", 2)
    s.line(x - r - 3, top, x + r + 3, top, "ink2", 2.5)
    if label:
        s.text(x, top + h + 22, label, "b", "middle")


def pill(s, x, y, text, col="ink2", fill=None):
    w = width(text, 18) + 24
    s.rect(x, y - 21, w, 30, fill, col, r=15, sw=2)
    s.text(x + w / 2, y, text, "s", "middle", col)
    return w


def doc(s, x, y, w=46, h=60):
    """A paper / file icon with a folded corner."""
    f = 14
    s.path(f"M{x} {y} L{x + w - f} {y} L{x + w} {y + f} L{x + w} {y + h} L{x} {y + h} Z", "ink2", 2, "on")
    s.path(f"M{x + w - f} {y} L{x + w - f} {y + f} L{x + w} {y + f}", "ink2", 2)
    for i in range(3):
        s.line(x + 9, y + 26 + i * 10, x + w - 9, y + 26 + i * 10, "line2", 2)


def mark(s, x, y, ok, r=9):
    """✓ (green) or ✗ (red) drawn as strokes so they never depend on the font."""
    if ok:
        s.path(f"M{x - r} {y} L{x - r * .3} {y + r * .7} L{x + r} {y - r * .8}", "c4", 4)
    else:
        s.xmark(x, y, r * .8, "mut", 4)


def dice(s, x, y, r=34):
    s.rect(x, y, r, r, "on", "ink2", r=7, sw=2.5)
    for px, py in ((.27, .27), (.5, .5), (.73, .73), (.73, .27), (.27, .73)):
        s.circle(x + px * r, y + py * r, 3.2, "ink2")


def fraction(s, x, y, num, den, col="ink"):
    s.text(x, y - 6, num, "b", "middle", col)
    s.line(x - 12, y, x + 12, y, col, 2)
    s.text(x, y + 22, den, "b", "middle", col)


# ---- page 4: papers -----------------------------------------------------------------

def papers():
    s = S("papers", 1200, 570)

    # left: two paper cards
    cards = [("8 株癌細胞株", "預印本 2026", "每個 SNV 標上 haplotype"),
             ("COLO829 近 T2T", "Cell 2026；組裝配對正常細胞", "haplotype 解析的突變地圖")]
    for i, (name, sub, did) in enumerate(cards):
        y = 6 + i * 196
        s.rect(0, y, 450, 176, "panel", "line2", r=12, sw=2)
        doc(s, 16, y + 16)
        s.text(78, y + 36, name, "h")
        s.text(78, y + 62, sub, "s", "start", "ink2")
        mark(s, 30, y + 108, True)
        s.text(50, y + 115, did, "s")
        mark(s, 30, y + 150, False)
        s.text(50, y + 157, "比較兩條 haplotype 的 SNV 數", "s", "start", "mut")
    s.text(0, 418, "在這兩篇論文裡沒找到", "s", "start", "ink2")
    s.text(0, 446, "兩條 haplotype 的比較", "s", "start", "ink2")
    s.text(0, 474, "（主文、補充、程式）", "s", "start", "mute")

    # middle: our re-analysis, HP1 / HP2 SNV density ratio with 95% CI (actual result)
    mx0, mx1 = 520, 800

    def xv(v):
        return mx0 + (v - 0.9) / 0.2 * (mx1 - mx0)
    s.text(500, 30, "再分析（我們算的）", "h")
    s.text(500, 58, "HP1 ÷ HP2 的 SNV 密度", "s", "start", "ink2")
    s.line(xv(1.0), 84, xv(1.0), 330, "ink2", 2, dash=True)
    s.text(xv(1.0), 354, "1:1", "b", "middle", "ink2")
    for v in (0.9, 1.1):
        s.text(xv(v), 354, f"{v}", "n", "middle", "mute")
    s.line(mx0, 330, mx1, 330, "line2", 2)
    rows = [("COLO829", 0.993, 0.974, 1.012, 150), ("HG008", 0.97, 0.93, 1.01, 262)]
    for name, v, lo, hi, y in rows:
        s.text(mx0, y - 26, name, "b")
        s.line(xv(lo), y, xv(hi), y, "ink", 4)
        s.line(xv(lo), y - 9, xv(lo), y + 9, "ink", 3)
        s.line(xv(hi), y - 9, xv(hi), y + 9, "ink", 3)
        s.circle(xv(v), y, 8, "ink")
        s.text(mx1, y - 26, f"{v}", "n", "end", "ink2")
    s.text(500, 400, "只算體染色體", "s", "start", "ink2")
    mark(s, 512, 434, True)
    s.text(530, 440, "CI 含 1：沒有否定 1:1", "s")
    mark(s, 512, 474, False)
    s.text(530, 480, "是累積數，不是每次的機率", "s", "start", "mut")
    mark(s, 512, 514, False)
    s.text(530, 520, "HP 跨染色體會對調：不是父母源", "s", "start", "mut")
    tag(s, 500, 556, "實際結果", "real")

    # arrows into the decision card
    s.arrow(455, 200, 488, 200, c="ink2", sw=3, head=10)
    s.arrow(820, 220, 850, 220, c="ink2", sw=3, head=10)

    # right: the decision card (user decided 11-12)
    cx = 860
    s.rect(cx, 6, 340, 478, "on", "ink2", r=14, sw=2.5)
    pill(s, cx + 16, 40, "使用者 11-12 決定", "ink", "hl")
    s.text(cx + 16, 82, "每個 SNV 各自隨機亂數產生", "s", "start", "ink2")
    s.bar(cx + 20, 116, 210, "hp1", h=16)
    s.bar(cx + 20, 150, 210, "hp2", h=16)
    s.text(cx + 238, 122, "HP1", "b", "start", "hp1")
    s.text(cx + 238, 156, "HP2", "b", "start", "hp2")
    for x in (52, 128, 196):
        s.star(cx + x, 116, 10)
    for x in (88, 160):
        s.star(cx + x, 150, 10)
    dice(s, cx + 286, 100, 32)
    fraction(s, cx + 302, 166, "1", "2")
    s.text(cx + 16, 222, "HP1、HP2 各 50%，彼此獨立", "b")
    items = [(True, "範圍：體染色體"), (True, "　扣掉丟失一條的區域"), (True, "再分析沒有否定"),
             (False, "不算證實"), (False, "1 kb 內聚集：沒有模擬")]
    for i, (ok, t) in enumerate(items):
        y = 284 + i * 40
        if not t.startswith("　"):
            mark(s, cx + 26, y - 6, ok, r=8)
        s.text(cx + 44, y, t.strip("　"), "s", "start", "ink" if ok else "mut")
    return s


def notes_papers():
    return ("這頁要看的是：兩篇論文都沒比較兩條 haplotype，所以 HP 先用各半。"
            "左邊是八株癌細胞株的預印本，和 COLO829 近 T2T 的 Cell 論文。"
            "兩篇都標了 haplotype，但主文、補充和程式裡沒找到兩條的比較。"
            "中間是我們的再分析：兩株的比值，信賴區間都含 1。它是累積數，不是每次突變的機率；HP 跨染色體會對調，不能說成父母源。"
            "右邊是我 11 月 12 日的決定：每個 SNV 各一半機率落在 HP1 或 HP2。"
            "範圍是體染色體，扣掉丟失一條的區域；沒有否定，但不算證實；1 kb 內的聚集沒有模擬。"
            "接下來看模擬驗證。")


def main():
    write_page("papers", page("papers", "兩篇論文都沒比較兩條 haplotype，所以 HP 先用 50%、每個 SNV 獨立",
                              papers(), notes=notes_papers()))
    for f in (notes_papers,):
        print(f.__name__, len(f()), "chars")


if __name__ == "__main__":
    main()
