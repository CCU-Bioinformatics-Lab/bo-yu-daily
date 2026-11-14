"""Background result pages of the 2026-11-18 deck: page 3 ref-tree (HG008 reference tree), page 4 papers (two papers + 50%).

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


def branch(s, x1, y1, x2, y2, style, c="ink", sw=5):
    """solid = single cells support, half = partly, dash = not checked."""
    if style == "solid":
        s.line(x1, y1, x2, y2, c, sw)
    elif style == "half":
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        s.line(x1, y1, mx, my, c, sw)
        s.line(mx, my, x2, y2, c, sw - 1.5, dash=True)
    else:
        s.line(x1, y1, x2, y2, "line2", 2.5, dash=True)


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


# ---- page 3: ref-tree --------------------------------------------------------------

LEAVES = "HGABEFCD"


def ref_tree():
    s = S("ref-tree", 1200, 450)

    # top strip: where each data set comes from
    for i in range(8):
        tube(s, 18 + i * 22, 8, w=14, h=30)
    s.text(200, 22, "8 株選殖株：第 14、19 代", "b")
    s.text(200, 48, "PacBio long read → 排出樹形", "s", "start", "ink2")
    for i in range(6):
        s.cell(664 + (i % 3) * 22, 14 + (i // 3) * 22, r=10)
    s.text(740, 22, "119 顆單細胞：第 23 代（和 bulk 同代）", "b")
    s.text(740, 48, "short read（單細胞例外）→ 檢查分支", "s", "start", "ink2")
    s.line(0, 72, 1200, 72, "line", 2)

    # left: the tree from the 8 clones (shape and counts from the lab_report, C-7)
    x0, dx = 50, 62
    X = {k: x0 + i * dx for i, k in enumerate(LEAVES)}
    yR, y7, y6, y4, y2, leaf = 150, 200, 250, 300, 345, 368
    xAB = (X["A"] + X["B"]) / 2
    xEF = (X["E"] + X["F"]) / 2
    xCD = (X["C"] + X["D"]) / 2
    xCDEF = (xEF + xCD) / 2
    x6 = (xAB + xCDEF) / 2
    x7 = (X["G"] + x6) / 2
    xR = (X["H"] + x7) / 2
    for a, b, y in [(X["H"], x7, yR), (X["G"], x6, y7), (xAB, xCDEF, y6), (X["A"], X["B"], y4),
                    (xEF, xCD, y4), (X["E"], X["F"], y2), (X["C"], X["D"], y2)]:
        s.line(a, y, b, y, "ink2", 2.5)
    s.line(xR, yR - 22, xR, yR, "ink2", 2.5)
    s.text(xR + 12, 108, "共同祖先：8 株都有", "s", "start", "ink2")
    s.text(xR + 12, 134, "7,784 個 SNV", "b", "start", "ink2")
    branch(s, x7, yR, x7, y7, "solid", RED)
    branch(s, x6, y7, x6, y6, "dash")
    branch(s, xAB, y6, xAB, y4, "half", "ink2")
    branch(s, xCDEF, y6, xCDEF, y4, "solid", PUR)
    branch(s, xCD, y4, xCD, y2, "solid", GOLD)
    branch(s, xEF, y4, xEF, y2, "dash")
    for k, y0 in [("H", yR), ("G", y7), ("A", y4), ("B", y4), ("E", y2), ("F", y2), ("C", y2), ("D", y2)]:
        branch(s, X[k], y0, X[k], leaf, "dash")
        tube(s, X[k], leaf, w=14, h=30, label=k)

    def num(x, ya, yb, t, col, a="end"):
        s.text(x, (ya + yb) / 2 + 7, t, "b", a, col)
    num(x7 - 10, yR, y7, "127", RED)
    num(x6 + 10, y7, y6, "4", "mute", "start")
    num(xAB - 10, y6, y4, "31", "ink2")
    num(xCDEF - 10, y6, y4, "14", PUR)
    num(xEF - 10, y4, y2, "17", "mute")
    num(xCD - 10, y4, y2, "68", GOLD)

    # legend for line styles + the caveat pill
    pill(s, 336, 128, "參考樹，不是真值", "stdis")
    for i, (st, lab, c) in enumerate([("solid", "單細胞支持", "ink"), ("half", "部分支持", "ink2"), ("dash", "未驗證", "ink")]):
        ly = 180 + i * 30
        branch(s, 420, ly - 6, 456, ly - 6, st, c, sw=4)
        s.text(464, ly, lab, "s")

    # arrow: tree -> cells
    s.arrow(548, 262, 640, 262, c="ink2", sw=3, head=12)
    s.text(594, 248, "比對", "s", "middle", "ink2")

    # right: nested carrier sets from the 119 single cells (actual result)
    s.rect(650, 92, 548, 326, "panel", "line2", r=12, sw=2)
    s.text(668, 122, "119 顆", "h")
    s.text(756, 122, "每顆細胞查：帶不帶這支的 SNV", "s", "start", "ink2")
    sets = [(RED, "111 顆", "帶綠色那支（127 個）", 668, 140, 512, 228),
            (PUR, "48 顆", "其中帶紫色（14 個）", 690, 196, 468, 160),
            (GOLD, "16 顆", "其中帶黃色（68 個）", 712, 252, 424, 92)]
    for col, n, lab, x, y, w, h in sets:
        s.rect(x, y, w, h, col, None, r=10, op=0.10)
        s.rect(x, y, w, h, None, col, r=10, sw=3)
        s.star(x + 22, y + 26, 10, col)
        s.text(x + 40, y + 33, n, "h", "start", col)
        s.text(x + 116, y + 33, lab, "s", "start", "ink2")
    # cells in the innermost set carry all three stars
    for i in range(5):
        s.cell(752 + i * 40, 318, r=15, fill="on", stars=(RED, PUR, GOLD))
    mark(s, 990, 312, True)
    s.text(1008, 318, "違反 0 顆", "b", "start", "c4")
    s.text(668, 404, "另 8 顆不帶綠色：落在 H 這側", "s", "start", "ink2")
    tag(s, 1062, 404, "實際結果", "real")
    return s


def notes_ref_tree():
    return ("這頁要看的是 HG008 參考樹怎麼來。左上是 8 株選殖株，第 14、19 代從單顆細胞長出，用 PacBio long read 定序；"
            "依每個 SNV 是哪幾株有，排出左邊這棵樹，數字是 SNV 個數。"
            "右上是 119 顆單細胞，和 bulk 同是第 23 代；它是 short read，屬於例外。"
            "右邊框裡，111 顆帶綠色那支，其中 48 顆帶紫色，其中 16 顆帶黃色，沒有細胞違反。"
            "所以實線三支有單細胞支持，虛線的末端還沒驗證。"
            "這棵樹是 AI 協助算的，我核對了程式和這三個細胞數。它是參考樹，不是真值。"
            "樹有了，接著看 HP 比例要怎麼設。")


# ---- page 4: papers -----------------------------------------------------------------

def papers():
    s = S("papers", 1200, 490)

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
    tag(s, 500, 476, "實際結果", "real")

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
            "左邊上面是八株癌細胞株的預印本，下面是 COLO829 近 T2T 的 Cell 論文，組裝的是配對正常細胞。"
            "兩篇都把突變標上 haplotype，但在它們的主文、補充和程式裡，沒找到兩條的比較。"
            "中間是我們的再分析，不是作者結論：兩株的比值，信賴區間都含 1。"
            "右邊是我 11 月 12 日的決定：每個 SNV 各自一半機率落在 HP1 或 HP2。"
            "範圍是體染色體，扣掉丟失一條的區域；沒有否定，但不算證實；1 kb 內的聚集沒有模擬。"
            "HP 怎麼設定好了，接下來看模擬驗證怎麼做。")


def main():
    write_page("ref-tree", page("ref-tree", "選殖株排出樹形；和 bulk 同代的單細胞支持三層巢狀分支",
                                ref_tree(), notes=notes_ref_tree()))
    write_page("papers", page("papers", "兩篇論文都沒比較兩條 haplotype，所以 HP 先用 50%、每個 SNV 獨立",
                              papers(), notes=notes_papers()))
    for f in (notes_ref_tree, notes_papers):
        print(f.__name__, len(f()), "chars")


if __name__ == "__main__":
    main()
