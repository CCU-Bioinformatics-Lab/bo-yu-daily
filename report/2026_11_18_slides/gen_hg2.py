"""HG008 results: hg-clairs (SNVs from reads: deep-branch SNVs are in the reads, few are called) and
hg-rebuild (the rebuilt trees against the reference layers, ONT and PacBio, with and without HP).

Sources (BRIEF R5, R6): lab_report/2026-11-13_hg008_bulk_rebuild/README.md sections 「ClairS」「原始 read 逐點數 alt」
「重建結果」「PacBio 結果」; pileup_deep_clades.txt (per-site status), clairs_branch_pacbio.txt,
haploclone_eval.txt, haploclone_eval_pacbio.txt (clone CCF, parent, SNV counts per layer).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python3 -I drops the script dir
from slidekit import S, page, write_page, tag  # noqa: E402
from lib import width  # noqa: E402
from gen_hg import LAYER  # noqa: E402

H = 500


def verdict_boxes(s, by, boxes, bottom=H):
    """能證明 / 不能證明 / next, as on hg-nist. A body with "\n" is drawn as several lines."""
    for x, w, ok, head, body in boxes:
        s.rect(x, by, w, bottom - by, "on", "c4" if ok else ("mut" if ok is False else "ink2"), r=10, sw=2)
        if ok:
            s.path(f"M{x + 18} {by + 32} L{x + 26} {by + 40} L{x + 42} {by + 22}", "c4", 4)
        elif ok is False:
            s.xmark(x + 30, by + 31, 9, "mut", 3.5)
        else:
            s.arrow(x + 16, by + 31, x + 44, by + 31, c="ink2", sw=3, head=10)
        s.text(x + 54, by + 38, head, "b", "start", "c4" if ok else ("mut" if ok is False else "ink"))
        for j, line in enumerate(body.split("\n")):
            s.text(x + 18, by + 76 + j * 30, line, "t")


# ---- hg-clairs ------------------------------------------------------------------------------
# pileup_deep_clades.txt, ONT: (PASS, read has >= 2 alt reads but not PASS, < 2 alt reads)
SITES = [("48 顆那層", "48", 6, 8, 0), ("16 顆那層", "16", 3, 47, 18), ("對照：未驗證分支", None, 0, 0, 17)]
VAF = [("48", .141, 48 / 119 / 2), ("16", .057, 16 / 119 / 2), (None, .001, None)]


def square(s, x, y, kind, a=15):
    if kind == "pass":
        s.rect(x, y, a, a, "mut", None, r=2)
    elif kind == "read":
        s.rect(x, y, a, a, "on", "mut", r=2, sw=2)
        s.rect(x + 4, y + 4, a - 8, a - 8, "mut", None, r=1, op=.35)
    else:
        s.rect(x, y, a, a, "panel3", None, r=2)


def hg_clairs():
    s = S("hg-clairs", 1200, H)
    TH = 392
    s.rect(0, 0, 700, TH, "panel", None, r=10)
    s.text(16, 30, "參考樹分支上的位點，逐點數 read", "h")
    tag(s, 586, 30, "實際結果", "real")
    y = 74
    for lab, key, npass, nread, nnone in SITES:
        tot = npass + nread + nnone
        s.circle(26, y + 2, 9, LAYER[key] if key else "unphased")
        s.text(42, y + 9, lab, "b")
        s.text(42, y + 37, f"{tot} 個位點", "s", "start", "ink2")
        kinds = ["pass"] * npass + ["read"] * nread + ["none"] * nnone
        for i, k in enumerate(kinds):
            square(s, 236 + (i % 17) * 20, y - 6 + (i // 17) * 20, k)
        rows = math.ceil(tot / 17)
        s.text(600, y + 9, f"判出 {npass}", "s", "start", "mut" if npass else "ink2")
        s.text(600, y + 37, f"read 有 {npass + nread}", "s", "start", "ink")
        y += max(rows * 20, 40) + 32
    # legend
    ly = 334
    for i, (k, t) in enumerate([("pass", "判出"), ("read", "read 有、沒判出"), ("none", "read 沒有")]):
        x = 16 + i * 210
        square(s, x, ly - 14, k)
        s.text(x + 24, ly, t, "s")
    s.text(16, 374, "ONT 63×；PacBio 116× 判出 7／14、3／68", "s", "start", "ink2")

    # right: pooled VAF, measured vs expected
    px = 716
    s.rect(px, 0, 484, TH, "panel", None, r=10)
    s.text(px + 16, 30, "合併起來的 VAF", "h")
    ax0, ax1 = px + 150, px + 450

    def X(v):
        return ax0 + (ax1 - ax0) * v / .25
    rows = [("48 顆", "48"), ("16 顆", "16"), ("對照", None)]
    for i, ((lab, key), (_, meas, exp)) in enumerate(zip(rows, VAF)):
        yy = 96 + i * 70
        s.circle(px + 26, yy - 7, 8, LAYER[key] if key else "unphased")
        s.text(px + 42, yy, lab, "t")
        s.line(ax0, yy - 7, ax1, yy - 7, "line", 2)
        if exp:
            s.circle(X(exp), yy - 7, 10, "on", LAYER[key], 3)
        s.circle(X(meas), yy - 7, 9, "mut")
        s.text(X(meas), yy + 26, f"{meas:.3f}", "s", "middle", "mut")
    s.line(ax0, 300, ax1, 300, "ink2", 2)
    for v in (0, .1, .2):
        s.line(X(v), 294, X(v), 306, "ink2", 2)
        s.text(X(v), 330, f"{v:g}", "s", "middle", "ink2")
    s.text(px + 16, 330, "VAF", "s", "start", "ink2")
    s.circle(px + 26, 366, 8, "mut")
    s.text(px + 42, 372, "實測", "s")
    s.circle(px + 136, 366, 9, "on", "ink2", 3)
    s.text(px + 152, 372, "預期＝細胞比例÷2", "s")
    tag(s, px + 340, 372, "推論", "infer")

    verdict_boxes(s, 408, [(0, 400, True, "能證明", "深層 SNV 在 bulk 的 read 裡"),
                           (412, 400, False, "不能證明", "沒有名單時也分得出真假"),
                           (824, 376, None, "下一步", "用判出的 SNV 重建")])

    notes = ("這頁要看的是：深層分支的突變在 bulk 的 read 裡，只是大多沒被判出來。"
             "我們用 ClairS，一個比對腫瘤和正常 read 找體細胞突變的程式。"
             "左邊每個方塊是參考樹上的一個位點：實心紅是判出，空心紅是 read 裡有、沒判出，灰色是 read 裡沒有。"
             "48 顆那層 14 個全部有，只判出 6 個；16 顆那層 68 個有 50 個，只判出 3 個；最下面未驗證分支是對照，幾乎沒有。"
             "右邊把位點合起來算 VAF，就是帶突變的 read 比例：紅點實測，空心圈是預期，兩層都接近。"
             "所以漏掉是判斷門檻，不是沒有突變。下一頁用判出的 SNV 重建。")
    write_page("hg-clairs", page("hg-clairs", "從 read 找：深層分支的 SNV 在 read 裡，但大多沒被判出", s, notes=notes))
    return notes


# ---- hg-rebuild ----------------------------------------------------------------------------
# clone: (ccf, parent, n_snv, fill, ring); fill/ring = the layer whose SNVs mostly fall in this clone
# (pre-set rule in the lab_report); "grey" = mostly SNVs with no reference label. haploclone_eval*.txt.
RUNS = [
    ("ONT 63×", "不加 HP", [[(.96, None, 5267, "all", "111"), (.45, 0, 549, "48", "16")],
                           [(.96, None, 5295, "all", "111"), (.44, 0, 521, "48", "16")]]),
    ("ONT 63×", "加 HP", [[(.97, None, 5191, "all", "111"), (.59, 0, 264, "grey", None), (.34, 0, 361, "48", "16")],
                         [(.97, None, 5229, "all", "111"), (.44, 0, 519, "48", None), (.20, 1, 68, "grey", None)]]),
    ("PacBio 116×", "不加 HP", [[(1.0, None, 4774, "all", "111"), (.56, 0, 181, "grey", None), (.30, 1, 40, "48", "16")],
                               [(1.0, None, 4767, "all", "111"), (.56, 0, 195, "grey", None), (.28, 1, 33, "48", "16")]]),
    ("PacBio 116×", "加 HP", [[(1.0, None, 4481, "all", "111"), (.90, 0, 296, "grey", "part"), (.55, 1, 188, "grey", None), (.24, 2, 30, "48", "16")],
                             [(1.0, None, 4477, "all", "111"), (.90, 0, 296, "grey", "part"), (.55, 1, 192, "grey", None), (.24, 2, 30, "48", "16")]]),
]
# pre-set checks per run (seed 1, seed 2): 111 layer split from all cells; 48-layer clone CCF within 0.1 of 0.40
CHECKS = [((False, False), (True, True)), ((False, False), (True, True)),
          ((False, False), (False, False)), ((False, False), (False, False))]


def hg_rebuild():
    s = S("hg-rebuild", 1200, 664)
    top, bot = 80, 350

    def Y(v):
        return bot - (bot - top) * v
    s.rect(0, 0, 1200, 520, "panel", None, r=10)
    tag(s, 1088, 30, "實際結果", "real")
    # CCF axis
    ax = 96
    s.line(ax, top, ax, bot, "ink2", 2)
    for v in (0, .5, 1):
        s.line(ax - 6, Y(v), ax, Y(v), "ink2", 2)
        s.text(ax - 12, Y(v) + 6, f"{v:g}", "s", "end", "ink2")
    s.text(ax - 12, top - 22, "CCF", "b", "end")
    # 48-layer band: 0.40 +- 0.1 (the pre-set CCF match)
    s.rect(ax + 4, Y(.503), 1080, Y(.303) - Y(.503), "hl", None, r=4, op=.7)
    for v, key in ((1.0, "all"), (111 / 119, "111"), (48 / 119, "48"), (16 / 119, "16")):
        s.line(ax + 4, Y(v), 1184, Y(v), LAYER[key], 1.5, dash=True, op=.6)
    # reference column
    rx = 170
    ref = [(1.0, "all", "全部"), (111 / 119, "111", "111 顆"), (48 / 119, "48", "48 顆"), (16 / 119, "16", "16 顆")]
    for (v, key, lab), nxt in zip(ref, ref[1:] + [None]):
        if nxt:
            s.line(rx, Y(v), rx, Y(nxt[0]), "ink2", 3)
    for v, key, lab in ref:
        s.circle(rx, Y(v), 10, LAYER[key])
    s.text(rx + 16, Y(1.0) - 10, "全部", "s", "start", "ink")
    s.text(rx + 16, Y(111 / 119) + 18, "111 顆", "s", "start", LAYER["111"])
    s.text(rx + 16, Y(48 / 119) + 6, "48 顆", "s", "start", LAYER["48"])
    s.text(rx + 16, Y(16 / 119) + 6, "16 顆", "s", "start", LAYER["16"])
    s.text(rx, 384, "參考樹", "b", "middle")
    s.text(rx, 410, "單細胞比例", "s", "middle")

    # rebuilt trees: four runs x two seeds
    cols = [380, 580, 800, 1010]
    for (plat, mode, seeds), cx, chk in zip(RUNS, cols, CHECKS):
        for k, clones in enumerate(seeds):
            x0 = cx - 34 + k * 68
            xs = []
            for i, (v, par, n, fill, ring) in enumerate(clones):
                sib = par is not None and sum(1 for c in clones if c[1] == par) > 1
                x = x0 + (0 if not sib else (-16 if i == min(j for j, c in enumerate(clones) if c[1] == par) else 16))
                xs.append(x)
            for i, (v, par, n, fill, ring) in enumerate(clones):
                if par is not None:
                    s.line(xs[par], Y(clones[par][0]), xs[i], Y(v), "ink2", 2.5)
            for i, (v, par, n, fill, ring) in enumerate(clones):
                r = 4 + 3 * math.log10(n)
                if ring == "part":
                    s.circle(xs[i], Y(v), r + 5, None, LAYER["111"], 3, dash=True)
                elif ring:
                    s.circle(xs[i], Y(v), r + 4, None, LAYER[ring], 3)
                s.circle(xs[i], Y(v), r, "unphased" if fill == "grey" else LAYER[fill], "on", 1.5)
            s.text(x0, 438, f"seed {k + 1}", "s", "middle", "ink2")
        s.text(cx, 384, plat, "b", "middle")
        s.text(cx, 410, mode, "s", "middle", "hp1" if mode == "加 HP" else "ink2")
        # checks: 111 split / 48 CCF
        for row, pair in enumerate(chk):
            for k, ok in enumerate(pair):
                xx, yy = cx - 34 + k * 68, 472 + row * 32
                if ok:
                    s.path(f"M{xx - 7} {yy - 6} L{xx - 2} {yy - 1} L{xx + 8} {yy - 12}", "c4", 3)
                else:
                    s.xmark(xx, yy - 6, 6, "mut", 2.5)
    s.text(16, 472, "111 顆分開", "s")
    s.text(16, 504, "48 顆 CCF ±0.1", "s")
    # annotation for the PacBio + HP clone at 0.90
    s.text(1068, Y(.90) + 6, "111 顆的 35%", "s", "start", LAYER["111"])
    s.text(1184, Y(.46) + 6, "黃帶：0.40±0.1", "s", "end", "ink2")
    verdict_boxes(s, 536, [(0, 392, True, "能證明", "全部細胞那層的 CCF 估得準\nONT 的 48 顆層也對上"),
                           (404, 392, False, "不能證明", "方法做不到：能對答案的\n深層 SNV 只有 5、2 個"),
                           (808, 392, False, "不能證明", "差異來自平台：平台、\n腫瘤、正常深度一起變")], bottom=664)
    # legend (top)
    lx = 150
    s.circle(lx, 24, 9, "unphased", "on", 1.5)
    s.text(lx + 16, 30, "大多沒有參考標籤", "s")
    s.circle(lx + 220, 24, 9, None, LAYER["16"], 3)
    s.text(lx + 236, 30, "外圈：那層的 SNV 也在這群", "s")
    s.text(lx + 640, 30, "圓越大，SNV 越多", "s", "start", "ink2")

    notes = ("這頁要看的是：重建找回了全部細胞和約四成細胞這兩層，111 顆和 16 顆兩層找不回來。"
             "縱軸是 CCF，帶突變的細胞比例。左邊是參考樹四層，右邊四組重建，各兩個 seed。"
             "黑點是全部細胞那群，綠圈表示 111 顆那層也併在裡面。紫點是 48 顆那層：ONT 在黃帶裡，PacBio 偏低。"
             "PacBio 加 HP 多一個 0.90 的群，收了 111 顆那層約三成五。"
             "兩列事先定的檢查：111 顆都沒分開；48 顆的 CCF，ONT 對上、PacBio 沒有。"
             "最下面：能對答案的深層 SNV 太少，不能說方法做不到；換平台時深度也變了，差異不能只怪平台。")
    write_page("hg-rebuild", page("hg-rebuild", "重建找回全部細胞和約四成細胞兩層；111、16 顆兩層找不回來", s, notes=notes))
    return notes


if __name__ == "__main__":
    for f in (hg_clairs, hg_rebuild):
        n = f()
        print(f.__name__, "notes", len(n), "chars")
