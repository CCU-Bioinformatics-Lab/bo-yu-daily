"""Result pages p8 colo-loh, p9 balance, p10 local (2026-11-11 deck).

Numbers come from BRIEF.md 「數字怎麼量」. The p9 barcode reads the 229 windows from the PRCGAP
lab report; the p10 points come from the SNV-independence lab report (both read-only).
"""
import csv
from pathlib import Path

from slidekit import S, page, write_page, n3_ladder, tag

LAB = Path(__file__).resolve().parents[2] / "lab_report"
LADDER_X, LADDER_Y = 1035, 104


def stars_on_bar(s, x, w, y, n, r=7, fill="mut"):
    for i in range(n):
        s.star(x + w * (i + 0.5) / n, y, r, fill)


# ---------------------------------------------------------------- p8 colo-loh
def p8():
    pid = "colo-loh"
    s = S(pid, 1200, 460)
    tag(s, 10, 32, "實際結果")
    n3_ladder(s, LADDER_X, 410, lit=[0])

    # raw ratio bar
    s.text(140, 32, "原始比例", "b")
    x0, w = 240, 600
    s.rect(x0, 13, w * 0.61, 30, "hp1", r=6)
    s.rect(x0 + w * 0.61, 13, w * 0.39, 30, "hp2", r=6)
    s.text(x0 + w * 0.305, 35, "HP1 61", "b", "middle", "on")
    s.text(x0 + w * 0.61 + w * 0.195, 35, "HP2 39", "b", "middle", "on")

    # left panel: LOH region
    s.rect(10, 66, 640, 384, "panel", r=10)
    s.text(28, 100, "LOH 區：約 765 Mb", "h")
    s.text(100, 150, "原本", "b", "middle")
    for j, c in enumerate(("hp1", "hp2")):
        y = 196 + j * 40
        s.bar(40, y, 120, c, 16)
        stars_on_bar(s, 40, 120, y, 3)
    s.text(100, 290, "兩條都有 SNV", "s", "middle")
    s.arrow(172, 216, 230, 216, "LOH", sw=3, head=12)

    stacks = [(2, "471 Mb"), (3, "183 Mb"), (4, "111 Mb")]
    for k, (n, mb) in enumerate(stacks):
        cx = 290 + k * 105
        top = 150
        for i in range(n):
            y = top + i * 30
            s.bar(cx - 45, y, 90, "hp1", 16)
            stars_on_bar(s, cx - 45, 90, y, 3, r=6)
        yl = top + n * 30 + 6
        s.bar(cx - 45, yl, 90, "hp2", 16, dash=True)
        s.text(cx, 330, f"{n} 份", "b", "middle")
        s.text(cx, 356, mb, "s", "middle")
    s.text(598, 190, "留下那條", "s", "middle")
    s.text(598, 212, "多份", "s", "middle")
    s.text(598, 280, "流失那條", "s", "middle", "hp2")
    s.text(598, 302, "（虛線）", "s", "middle", "hp2")
    s.text(28, 392, "留下那條畫成 HP1", "s")
    tag(s, 186, 392, "示意", "demo")
    s.text(330, 432, "流失那條的 SNV 一起消失 → 比例偏向留下的那條", "t", "middle")

    # right panel: 2:1 region
    s.rect(666, 66, 524, 384, "panel", r=10)
    s.text(684, 100, "兩條都在的 2:1 區", "h")
    for j in range(2):
        y = 140 + j * 26
        s.bar(690, y, 140, "line2", 14)
        stars_on_bar(s, 690, 140, y, 3, r=6)
    s.bar(690, 210, 140, "panel3", 14)
    stars_on_bar(s, 690, 140, 210, 3, r=6)
    s.path("M842 134 L850 134 L850 172 L842 172", "ink2", 2)
    s.text(862, 159, "2 份那條 1,639", "b")
    s.text(862, 217, "1 份那條 1,425", "b")

    # gauge: predicted vs actual for the 1-copy side
    s.text(684, 268, "1 份那條：預測＝每份突變率相同", "s")
    scale = 230 / 1588
    s.text(700, 306, "預測", "s")
    s.rect(750, 290, 1588 * scale, 22, None, "ink2", r=4, dash=True, sw=2)
    s.text(990, 307, "1,588", "s")
    s.text(700, 342, "實際", "s")
    s.rect(750, 326, 1425 * scale, 22, "panel3", r=4)
    s.text(970, 343, "1,425", "s")
    s.text(684, 392, "少約 10%，p≈0.003", "b")
    tag(s, 892, 392, "原因未定", "infer")

    notes = "這頁要看的是，COLO829 原始的 61 比 39，主要來自一條的大片段變成 LOH。左邊 LOH 區大約 765 Mb，原本兩條都有 SNV，後來只剩一種版本，留下的那條多半有 2 到 4 份，分別是 471、183、111 Mb。流失那條的 SNV 一起消失，比例就偏了。右邊是兩條都在的 2:1 區，2 份那條 1,639 個，1 份那條 1,425 個。照每份突變率相同預測，1 份那條應該約 1,588 個，實際少約一成，p 約 0.003，原因還沒確定。階梯上只亮觀測特徵。"
    write_page(pid, page(pid, "COLO829 原始比例 61:39，主要因為一條的大片段變成 LOH", s,
                         "LOH 區留下的那條多半有 2–4 份；兩條都在的地方仍差約 10%。", notes))
    return notes


# ---------------------------------------------------------------- p9 balance
def balance(s, cx, name, rule, nums, ratio, extra=None):
    s.text(cx, 40, name, "h", "middle")
    # fulcrum and beam
    s.poly([(cx, 62), (cx - 18, 96), (cx + 18, 96)], "ink2")
    s.line(cx - 170, 62, cx + 170, 62, "ink2", 5)
    for side, c in ((-1, "hp1"), (1, "hp2")):
        px = cx + side * 150
        s.line(px - 70, 112, px, 62, "line2", 1.5)
        s.line(px + 70, 112, px, 62, "line2", 1.5)
        s.path(f"M{px - 80} 112 Q{px} 150 {px + 80} 112 Z", None, 0, "panel2")
        s.bar(px - 66, 122, 132, c, 18)
        stars_on_bar(s, px - 66, 132, 122, 5, r=7)
        s.text(px, 172, "HP1" if c == "hp1" else "HP2", "b", "middle", c)
    s.text(cx, 200, rule, "s", "middle")
    s.text(cx, 228, nums, "b", "middle")
    s.text(cx, 256, ratio, "b", "middle", "c4")
    if extra:
        s.text(cx, 280, extra, "s", "middle", "mute")


def p9():
    pid = "balance"
    s = S(pid, 1200, 460)
    tag(s, 10, 32, "實際結果")
    n3_ladder(s, LADDER_X, LADDER_Y, lit=[0])
    balance(s, 260, "COLO829", "整個組裝扣掉 >5 Mb 無 SNV 的片段", "9.34 vs 9.31 個／Mb", "比值 1.004 ✓",
            "每 Mb、扣掉流失片段；和第 8 頁的 2:1 區算法不同")
    balance(s, 760, "HG008", "體染色體，只算該條在腫瘤裡 ≥ 1 份的片段", "2.31 vs 2.39 個／Mb", "比值 0.97 ✓")
    s.line(510, 30, 510, 270, "line", 2)
    tag(s, 950, 180, "星數＝示意", "demo")

    # PRCGAP barcode
    s.rect(10, 290, 1180, 162, "panel", r=10)
    s.text(28, 322, "PRCGAP：公開的 8 株細胞株 long read 組裝（含上面兩株）", "h")
    s.text(28, 350, "229 個 20 Mb 區段，兩條份數相同；一格＝一個區段", "s")
    rows = list(csv.DictReader(open(LAB / "2026-11-06_prcgap_hap_snv_ratio/per_window_20mb.tsv"), delimiter="\t"))
    groups = []
    for r in rows:
        if not groups or groups[-1][0] != r["sample"]:
            groups.append((r["sample"], []))
        groups[-1][1].append(float(r["p_bonferroni"]) < 0.05)
    gap, x, cw = 12, 28.0, (1172 - 28 - 12 * 7) / len(rows)
    y0, hh = 366, 44
    sig = 0
    others = []
    for gi, (name, flags) in enumerate(groups):
        gx = x
        for f in flags:
            s.rect(x + 0.4, y0, cw - 0.8, hh, "ink" if f else "panel3", r=0)
            if f:
                sig += 1
                s.poly([(x + cw / 2, y0 - 2), (x + cw / 2 - 6, y0 - 11), (x + cw / 2 + 6, y0 - 11)], "ink")
            x += cw
        if name in ("COLO829", "HG008"):
            s.text((gx + x) / 2, y0 + hh + 24, name, "s", "middle")
        elif not others:
            others = [gx, 0]
        if others:
            others[1] = x
        x += gap
    assert len(rows) == 229 and sig == 7, (len(rows), sig)
    s.text((others[0] + others[1]) / 2, y0 + hh + 24, "其他 6 株", "s", "middle")
    s.text(1172, 322, "大致各半 ✓　區段間差異比隨機大 ✗", "s", "end")
    s.text(1172, 350, "▼ 深色 7 格＝校正後顯著", "s", "end")

    notes = "這頁要看的是，扣掉流失的片段後，兩條的 SNV 密度接近各半。左邊 COLO829 扣掉超過 5 Mb 沒有 SNV 的片段，每 Mb 9.34 對 9.31，比值 1.004；這是每 Mb 的密度，和第 8 頁 2:1 區的算法不同。中間 HG008 只算體染色體裡、該條在腫瘤至少 1 份的片段，2.31 對 2.39，比值 0.97。下面是 PRCGAP，一個公開的 8 株細胞株 long read 組裝資料。兩條份數相同的 229 個 20 Mb 區段，一格一段，深色 7 格校正後顯著。所以大致各半，但區段之間的差異比隨機大。"
    write_page(pid, page(pid, "扣掉流失片段後，COLO829 和 HG008 的兩條接近各半；8 株的區段比較大致各半但不均勻", s,
                         "扣掉流失片段後，兩條密度接近 1:1；區段之間仍有差異。", notes))
    return notes


# ---------------------------------------------------------------- p10 local
def load_points():
    ctrl = {}
    for r in csv.DictReader(open(LAB / "2026-11-07_snv_hp_independence/control_detail.tsv"), delimiter="\t"):
        ctrl[(r["dataset"], r["distance_bp"])] = float(r["share_same"])
    far = {}
    for r in csv.DictReader(open(LAB / "2026-11-07_snv_hp_independence/pairs_by_distance.tsv"), delimiter="\t"):
        far[(r["dataset"], r["distance"])] = (float(r["share_same"]), int(r["n_pairs"]))
    return ctrl, far


def p10():
    pid = "local"
    s = S(pid, 1200, 460)
    ctrl, far = load_points()
    tag(s, 10, 32, "實際結果")
    n3_ladder(s, LADDER_X, LADDER_Y, lit=[0])

    # what "same strand" means: a phase block with two stars on the same HP
    s.rect(138, 10, 120, 44, None, "ink2", r=4, dash=True)
    s.bar(146, 22, 104, "hp1", 10)
    s.bar(146, 42, 104, "hp2", 10)
    s.star(178, 22, 7)
    s.star(214, 22, 7)
    s.text(268, 30, "phase block 內，兩個 SNV 都在同一個 HP＝「同一條」", "s")
    tag(s, 860, 30, "示意", "demo")

    # axes
    X0, X1 = 90, 755
    bw = (X1 - X0) / 7
    def bx(i):
        return X0 + bw * (i + 0.5)
    def yv(v):
        return 380 - (v - 0.4) * 450
    s.line(X0, yv(1.02), X0, 405, "ink2", 2)
    s.line(X0, 405, X1, 405, "ink2", 2)
    # axis break: the y axis does not start at 0
    s.rect(X0 - 8, 386, 16, 9, "paper", r=0)
    s.path(f"M{X0 - 9} 392 L{X0 + 9} 386 M{X0 - 9} 399 L{X0 + 9} 393", "ink2", 2)
    s.text(X0 - 10, 411, "0", "s", "end")
    for v in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        s.line(X0 - 5, yv(v), X0, yv(v), "ink2", 2)
        s.text(X0 - 10, yv(v) + 6, f"{v:.1f}", "s", "end")
    s.text(10, 84, "同一條比例", "s")
    s.line(X0, yv(0.5), X1, yv(0.5), "ink2", 2, dash=True)

    # two methods: thick divider
    xd = X0 + bw * 3
    s.line(xd, 66, xd, 405, "ink", 5)
    s.text(X0 + bw * 1.5 + 10, 84, "<1 kb：全部 SNV", "b", "middle")
    s.text(xd + bw * 2, 84, "≥1 kb：成簇 SNV 併成一個", "b", "middle")
    labels = ["0–100 bp", "100–300", "300–1000", "1–10 kb", "10–100 kb", "0.1–1 Mb", "≥1 Mb"]
    for i, t in enumerate(labels):
        s.text(bx(i), 430, t, "s", "middle")
    s.text((X0 + X1) / 2, 456, "相鄰 SNV 的距離", "s", "middle")

    near = ["0-100", "100-300", "300-1000"]
    farbins = ["1-10 kb", "10-100 kb", "100 kb-1 Mb", ">=1 Mb"]
    data = {}
    for ds, dx in (("assembly_HG008", -9), ("assembly_COLO829", 9)):
        pts = [(bx(i) + dx, yv(ctrl[(ds, b)]), ctrl[(ds, b)], None) for i, b in enumerate(near)]
        pts += [(bx(3 + i) + dx, yv(far[(ds, b)][0]), far[(ds, b)][0], far[(ds, b)][1]) for i, b in enumerate(farbins)]
        data[ds] = pts
        col = "ink" if ds.endswith("HG008") else "ink2"
        for seg in (pts[:3], pts[3:]):  # connect within one method only
            for a, b in zip(seg, seg[1:]):
                s.line(a[0], a[1], b[0], b[1], col, 1.5, op=.6)
    undecided = {("assembly_HG008", 3), ("assembly_HG008", 6), ("assembly_COLO829", 6)}
    for ds, pts in data.items():
        for i, (x, y, v, n) in enumerate(pts):
            if (ds, i) in undecided:
                s.circle(x, y, 9, "unphased", "ink2", 1.5)
                s.text(x, y + 6, "?", "s", "middle", "on")
            elif ds.endswith("HG008"):
                s.circle(x, y, 8, "ink")
            else:
                s.circle(x, y, 8, "paper", "ink", 2.5)
    hg, co = data["assembly_HG008"], data["assembly_COLO829"]
    for i, t in enumerate(("0.97", "0.96")):
        s.text(hg[i][0], hg[i][1] - 14, t, "s", "middle")
    s.text(hg[2][0] + 14, hg[2][1] + 6, "0.82", "s")
    s.text(co[0][0] + 16, co[0][1] + 6, "0–100 bp 0.85", "s")
    # COLO829 control: the pooled <1 kb share
    yc = yv(0.658)
    s.line(X0 + 12, yc, xd - 12, yc, "stdis", 3, dash=True)
    s.rect(X0 + 8, yc - 70, 202, 66, "paper", r=4, op=.9)
    s.text(X0 + 14, yc - 50, "COLO829 <1 kb 對照", "s", "start", "stdis")
    s.text(X0 + 14, yc - 29, "＝近距離定相能否用", "s", "start", "stdis")
    s.text(X0 + 14, yc - 8, "0.658 ✗ 未過門檻 0.8", "s", "start", "stdis")
    s.text(X0 + 14, yv(0.5) + 24, "獨立的期望 0.5", "s")
    s.text(X0 + 14, 380, "配對數只占 SNV 數的 2.5–4.5%", "s")
    s.text(hg[3][0], hg[3][1] - 18, "未定", "s", "middle", "mute")
    s.text(hg[6][0] - 8, hg[6][1] - 18, "未定", "s", "middle", "mute")
    # legend
    s.circle(xd + 30, 126, 8, "ink")
    s.text(xd + 44, 132, "HG008", "s")
    s.circle(xd + 150, 126, 8, "paper", "ink", 2.5)
    s.text(xd + 164, 132, "COLO829", "s")
    s.circle(xd + 30, 160, 9, "unphased", "ink2", 1.5)
    s.text(xd + 30, 166, "?", "s", "middle", "on")
    s.text(xd + 44, 166, "未定（配對少）", "s")

    # right: chrX
    s.line(782, 150, 782, 450, "line", 2)
    s.text(800, 182, "chrX（HG008）", "h")
    s.text(800, 222, "HP1", "b", "start", "hp1")
    s.bar(800, 246, 260, "hp1", 18)
    stars_on_bar(s, 800, 260, 246, 6, r=8)
    s.text(1070, 252, "2.46 個／Mb", "s")
    s.text(800, 300, "HP2＝Xi（失活的 X）", "b", "start", "hp2")
    s.bar(800, 324, 260, "hp2", 18)
    stars_on_bar(s, 800, 260, 324, 9, r=8)
    s.text(1070, 330, "3.71 個／Mb", "s")
    s.text(800, 376, "比值 0.66", "big")
    s.text(800, 424, "一株；哪條是失活的 X 取自論文", "s")

    notes = "這頁要看的是兩個局部例外。左邊是相鄰 SNV 在同一條的比例，同一條是指同一個 phase block 內的同一個 HP。粗線左邊是 1 kb 內，用全部 SNV：HG008 是 0.97、0.96、0.82；COLO829 只有 0 到 100 bp 高，0.85。對照是檢查近距離定相能否用，COLO829 是 0.658，沒過門檻 0.8。粗線右邊把成簇 SNV 併成一個，多數靠近 0.5，問號是未定的點。右邊 HG008 的 X，失活那條 3.71、另一條 2.46，比值 0.66。任務一到這裡；下一頁回到任務二，看 HG008 的候選樹。"
    write_page(pid, page(pid, "兩個局部例外：很近的 SNV 常在同一條、失活的 X 突變較多", s,
                         "1 kb 以上多數接近 0.5，問號點未定。", notes))
    return notes


if __name__ == "__main__":
    for f in (p8, p9, p10):
        n = f()
        print(f.__name__, "notes chars:", len(n))
