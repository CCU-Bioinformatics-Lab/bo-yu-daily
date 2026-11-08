"""Result pages p8 colo-loh (8-line totals), p9 balance, p10 local (2026-11-11 deck).

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


# ---------------------------------------------------------------- p8 colo-loh (2026-11-08: all SNVs, 8 lines)
def load_totals():
    """Sum hap1 / hap2 SNVs over all 23 chromosomes (no region removed) for each PRCGAP line."""
    out = {}
    for r in csv.DictReader(open(LAB / "2026-11-06_prcgap_hap_snv_ratio/per_chromosome.tsv"), delimiter="\t"):
        d = out.setdefault(r["sample"], [0, 0])
        d[0] += int(r["hap1_snv"])
        d[1] += int(r["hap2_snv"])
    return out


def p8():
    pid = "colo-loh"
    s = S(pid, 1200, 460)
    tot = load_totals()
    assert sorted(tot) == sorted(P9_ORDER), tot
    s.text(10, 30, "資料：PRCGAP（Sakamoto 2026 預印本）8 株癌細胞株，long read 組裝出兩條", "h")
    tag(s, 10, 64, "實際結果")
    s.text(128, 64, "全部 SNV，不扣任何區域", "s")

    # one 100 % bar per cell line
    bx, bw, y0, dy, bh = 140, 520, 104, 44, 30
    s.line(bx + bw / 2, y0 - 8, bx + bw / 2, y0 + dy * 7 + bh + 8, "ink2", 2, dash=True)
    s.text(bx + bw / 2, y0 - 14, "50%", "s", "middle")
    s.text(bx + bw + 20, y0 - 14, "SNV 數", "s")
    for i, name in enumerate(P9_ORDER):
        a, b = tot[name]
        f = a / (a + b)
        y = y0 + i * dy
        s.text(20, y + 22, name, "b")
        s.rect(bx, y, bw * f, bh, "hp1", r=0)
        s.rect(bx + bw * f, y, bw * (1 - f), bh, "hp2", r=0)
        s.text(bx + 10, y + 22, f"HP1 {f * 100:.1f}%", "s", "start", "on")
        s.text(bx + bw - 10, y + 22, f"HP2 {(1 - f) * 100:.1f}%", "s", "end", "on")
        s.text(bx + bw + 20, y + 22, f"{a + b:,}", "s")

    # right: why the sum is only a reference
    s.rect(800, 92, 390, 214, "panel", r=10)
    s.text(818, 124, "HP1、HP2 編號", "h")
    tag(s, 1112, 124, "示意", "demo")
    s.text(818, 152, "跨染色體不對應", "s")
    for j, (chrom, swap) in enumerate((("chr1", False), ("chr4", True))):
        y = 164 + j * 52
        s.text(818, y + 24, chrom, "b")
        top, bot = ("hp2", "hp1") if swap else ("hp1", "hp2")
        s.bar(890, y + 4, 150, top, 14)
        s.bar(890, y + 28, 150, bot, 14)
        s.text(1052, y + 22, "可能對調" if swap else "", "s", "start", "stdis")
    s.text(818, 288, "HG008 對 GIAB：14／23 條對調", "s")
    s.text(808, 350, "→ 加總只能參考", "b", "start", "stdis")
    n3_ladder(s, LADDER_X, 410, lit=[0])

    lo = min(P9_ORDER, key=lambda n: tot[n][0] / sum(tot[n]))
    hi = max(P9_ORDER, key=lambda n: tot[n][0] / sum(tot[n]))
    flo = tot[lo][0] / sum(tot[lo]) * 100
    fhi = tot[hi][0] / sum(tot[hi]) * 100
    notes = ("這頁先看最原始的數字。資料是 PRCGAP，Sakamoto 團隊 2026 年的預印本，公開 8 株癌細胞株，"
             "每株用 long read 組裝出兩條參考。每一列一株，全部 SNV 直接加總，藍色 HP1、橘色 HP2。"
             f"從 {hi} 的 {fhi:.1f}% 到 {lo} 的 {flo:.1f}%。"
             "但右邊要注意，組裝軟體是每條染色體各自決定哪一條叫 HP1，所以 HP1 編號跨染色體不對應。HG008 和 GIAB 比，23 條有 14 條對調，"
             "所以這個加總只能參考。下一頁只比兩條份數相同的區段。")
    write_page(pid, page(pid, f"全部 SNV 加總，HP1 占 {flo:.0f}–{fhi:.0f}%；HP1 編號跨染色體不對應，只能參考", s,
                         "", notes))
    return notes


# ---------------------------------------------------------------- p9 balance
# PRCGAP 8 cell lines, windows where both haplotypes have the same copy number (lab report rule:
# both retained >= 80 %, mean CN difference < 0.3, >= 10 SNVs, autosomes, 20 Mb on CHM13).
P9_ORDER = ["COLO829", "HG008", "H1437", "H2009", "H209", "H2126", "HCC1937", "HCC1954"]
# Independent check of PRCGAP's haplotype calls: only HG008 (vs GIAB, 97.4 %). COLO829 has our own read
# linkage phasing, but it was never compared call by call with PRCGAP, so it counts as unverified.
P9_CHECK = {"HG008": ("GIAB 核對 ✓", "c4")}


def expected_larger(n):
    """E[max(X, n-X)] for X ~ Binomial(n, 1/2): the larger side's count under pure chance."""
    from math import comb
    return sum(comb(n, k) * max(k, n - k) for k in range(n + 1)) / 2 ** n


def load_balanced():
    rows = csv.DictReader(open(LAB / "2026-11-06_prcgap_hap_snv_ratio/per_window_20mb.tsv"), delimiter="\t")
    out = {}
    for r in rows:
        a, b = int(r["hap1_snv"]), int(r["hap2_snv"])
        d = out.setdefault(r["sample"], [0, 0, 0.0, 0])  # windows, larger, expected larger, total
        d[0] += 1
        d[1] += max(a, b)
        d[2] += expected_larger(a + b)
        d[3] += a + b
    return {k: (w, lg / t, ex / t) for k, (w, lg, ex, t) in out.items()}


def mini_balance(s, cx, y, w=76):
    """A level beam with an HP1 pan and an HP2 pan."""
    s.poly([(cx, y), (cx - 12, y + 24), (cx + 12, y + 24)], "ink2")
    s.line(cx - w / 2 - 6, y, cx + w / 2 + 6, y, "ink2", 4)
    for side, c in ((-1, "hp1"), (1, "hp2")):
        px = cx + side * w / 2
        s.line(px - 20, y + 30, px, y, "line2", 1.2)
        s.line(px + 20, y + 30, px, y, "line2", 1.2)
        s.path(f"M{px - 24} {y + 30} Q{px} {y + 50} {px + 24} {y + 30} Z", None, 0, "panel2")
        s.bar(px - 19, y + 33, 38, c, 9)
        stars_on_bar(s, px - 19, 38, y + 33, 2, r=4)


def p9():
    pid = "balance"
    s = S(pid, 1200, 460)
    data = load_balanced()
    assert sorted(data) == sorted(P9_ORDER) and sum(v[0] for v in data.values()) == 229, data
    n3_ladder(s, LADDER_X, LADDER_Y, lit=[0])

    # inset: which 20 Mb windows are counted
    s.rect(10, 6, 740, 134, "panel", r=10)
    s.text(28, 36, "只算兩條份數相同的 20 Mb 區段", "h")
    tag(s, 360, 36, "示意", "demo")
    cases = [  # (HP1 copies, HP2 copies, HP2 lost, counted)
        (1, 1, False, True), (2, 1, False, False), (1, 0, True, False)]
    for i, (n1, n2, lost, ok) in enumerate(cases):
        x = 30 + i * 240
        y = 62
        for k in range(n1):
            s.bar(x, y + k * 16, 100, "hp1", 10)
            stars_on_bar(s, x, 100, y + k * 16, 3, r=5)
        y2 = y + n1 * 16 + 4
        if lost:
            s.bar(x, y2, 100, "hp2", 10, dash=True)
        for k in range(n2):
            s.bar(x, y2 + k * 16, 100, "hp2", 10)
            stars_on_bar(s, x, 100, y2 + k * 16, 3, r=5)
        lab = {0: "1 份 : 1 份", 1: "2 份 : 1 份", 2: "一條流失"}[i]
        s.text(x + 112, 84, lab, "b")
        s.text(x + 112, 114, "算 ✓" if ok else "不算 ✗", "b", "start", "c4" if ok else "stdis")

    # 8 cell lines
    tag(s, 770, 132, "實際結果")
    s.text(900, 132, "▼ 8 株", "s")
    s.text(770, 40, "實測＝SNV 較多那條的占比", "s")
    s.text(770, 70, "純隨機也會大於 50%", "s")
    cw, ch, gx, gy = 292, 148, 10, 152
    for i, name in enumerate(P9_ORDER):
        win, obs, exp = data[name]
        x = gx + (i % 4) * (cw + 4)
        y = gy + (i // 4) * (ch + 6)
        s.rect(x, y, cw, ch, "panel", r=10)
        s.text(x + 14, y + 30, name, "h")
        chk, col = P9_CHECK.get(name, ("未獨立驗證", "mute"))
        s.text(x + cw - 12, y + 30, chk, "s", "end", col)
        mini_balance(s, x + 70, y + 62)
        s.text(x + 150, y + 96, f"實測 {obs * 100:.1f}%", "b")
    # random expectation and window counts were dropped from the page on 2026-11-08 (user request);
    # they stay in BRIEF.md.
    print("p9 obs-random gap (pp):", [f"{(data[n][1] - data[n][2]) * 100:.1f}" for n in P9_ORDER])

    notes = ("這頁看 PRCGAP 這個公開資料集的 8 株細胞株。上面是算法：只算兩條份數相同的 20 Mb 區段，"
             "1 份對 1 份就算，2 份對 1 份或一條流失就不算。下面一格一株。"
             "實測是每個區段裡 SNV 較多那條的占比，這個數字一定大於一半，純隨機也會大於一半。"
             "8 株落在 51.9% 到 58.3%，都接近一半。"
             "右上角是有沒有獨立核對，只有 HG008 核對過。")
    write_page(pid, page(pid, "只比兩條份數相同的區段，8 株的 HP1、HP2 SNV 數大致相等", s, "", notes))
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

    # what "same strand" means: one 20 Mb window of the phased assembly, two stars on the same HP
    s.rect(138, 10, 120, 44, None, "ink2", r=4, dash=True)
    s.bar(146, 22, 104, "hp1", 10)
    s.bar(146, 42, 104, "hp2", 10)
    s.star(178, 22, 7)
    s.star(214, 22, 7)
    s.text(268, 30, "同一個 20 Mb 區段內（組裝定相）同一個 HP＝「同一條」", "s")
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

    notes = "這頁要看的是兩個局部例外。左邊是相鄰 SNV 在同一條的比例，同一條是指同一個 20 Mb 區段內，組裝定相的同一個 HP。粗線左邊是 1 kb 內，用全部 SNV：HG008 是 0.97、0.96、0.82；COLO829 只有 0 到 100 bp 高，0.85。對照是檢查近距離定相能否用，COLO829 是 0.658，沒過門檻 0.8。粗線右邊把成簇 SNV 併成一個，多數靠近 0.5，問號是未定的點。右邊 HG008 的 X，失活那條 3.71、另一條 2.46，比值 0.66。任務一到這裡；下一頁回到任務二，看 HG008 的候選樹。"
    write_page(pid, page(pid, "兩個局部例外：很近的 SNV 常在同一條、失活的 X 突變較多", s,
                         "1 kb 以上多數接近 0.5，問號點未定。", notes))
    return notes


if __name__ == "__main__":
    for f in (p8, p9, p10):
        n = f()
        print(f.__name__, "notes chars:", len(n))
