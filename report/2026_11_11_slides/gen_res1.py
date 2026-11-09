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
    # 2026-11-08: three-layer ladder removed at the user's request.

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


# ---------------------------------------------------------------- p7 colo829-t2t (added 2026-11-08, user)
# Numbers: lab_report/2026-11-06_colo829_hap_snv_ratio (haplotype_totals.tsv, gap 5 Mb), from Sohn 2026 somatic_snvs.vcf.gz.
def p_t2t():
    pid = "colo829-t2t"
    s = S(pid, 1200, 460)
    s.text(10, 30, "資料：COLO829 T2T（Sohn 2026，Cell），long read 體細胞 SNV 44,810 個", "h")
    tag(s, 10, 64, "實際結果")
    s.text(128, 64, "hap1／hap2 是組裝標籤，不是爸媽", "s")

    # left: raw totals and the lost stretch
    s.rect(10, 84, 560, 372, "panel", r=10)
    s.text(28, 118, "原始比例", "h")
    x0, w = 28, 520
    f = 27410 / (27410 + 17400)
    s.rect(x0, 134, w * f, 34, "hp1", r=0)
    s.rect(x0 + w * f, 134, w * (1 - f), 34, "hp2", r=0)
    s.text(x0 + 10, 158, "hap1 27,410（61.2%）", "s", "start", "on")
    s.text(x0 + w - 10, 158, "hap2 17,400", "s", "end", "on")
    s.text(28, 222, "hap1", "b", "start", "hp1")
    s.bar(90, 208, 440, "hp1", 16)
    stars_on_bar(s, 90, 440, 208, 11, r=6)
    s.text(28, 262, "hap2", "b", "start", "hp2")
    s.bar(90, 248, 270, "hp2", 16)
    stars_on_bar(s, 90, 270, 248, 7, r=6)
    s.bar(364, 248, 166, "hp2", 16, dash=True)
    s.text(447, 296, "844 Mb 沒有 SNV", "b", "middle", "hp2")
    s.text(447, 322, "（7 條 contig）", "s", "middle")
    s.text(28, 380, "腫瘤丟掉這段 → hap2 的 SNV 少了一截", "t")
    tag(s, 28, 430, "染色體示意", "demo")

    # arrow
    s.arrow(578, 270, 622, 270, c="ink2", sw=3, head=12)

    # right: same 100 % bar as the left, after removing long empty stretches.
    # 2026-11-09 user comment: show the same kind of ratio as the left, not SNV per Mb.
    # Share = density1 / (density1 + density2): the hap1 share if both haplotypes kept the same length.
    # lab_report/2026-11-06_colo829_hap_snv_ratio/haplotype_totals.tsv, gap 5 Mb.
    d1, d2 = 27410 / 2934.0, 17400 / 1869.3
    g = d1 / (d1 + d2)
    ci = [r / (1 + r) for r in (0.985, 1.023)]
    s.rect(630, 84, 560, 372, "panel", r=10)
    s.text(648, 118, "扣掉 >5 Mb 沒有 SNV 的片段後", "h")
    x1 = 648
    s.rect(x1, 134, w * g, 34, "hp1", r=0)
    s.rect(x1 + w * g, 134, w * (1 - g), 34, "hp2", r=0)
    s.line(x1 + w / 2, 128, x1 + w / 2, 174, "ink", 1.5, dash=True)
    s.text(x1 + 10, 158, f"hap1 {g * 100:.1f}%", "s", "start", "on")
    s.text(x1 + w - 10, 158, f"hap2 {(1 - g) * 100:.1f}%", "s", "end", "on")
    s.text(648, 222, "hap1", "b", "start", "hp1")
    s.bar(710, 208, 440, "hp1", 16)
    stars_on_bar(s, 710, 440, 208, 11, r=6)
    s.text(648, 262, "hap2", "b", "start", "hp2")
    s.bar(710, 248, 270, "hp2", 16)
    stars_on_bar(s, 710, 270, 248, 7, r=6)
    s.text(648, 304, "兩條一樣長時的比例", "t")
    s.text(648, 352, f"約 50:50 ✓", "big", "start", "c4")
    s.text(648, 384, f"95% CI hap1 {ci[0] * 100:.1f}%–{ci[1] * 100:.1f}%", "s")
    tag(s, 648, 430, "染色體示意", "demo")
    # 2026-11-08: three-layer ladder removed at the user's request.

    notes = ("這頁看其中一株 COLO829 的細節，資料是 Sohn 2026 在 Cell 公開的 long read 體細胞 SNV，共 44,810 個。"
             "左邊是原始比例，hap1 27,410、hap2 17,400，大約 61 比 39。原因在下面：hap2 有 844 Mb、7 條 contig 一個 SNV 都沒有，"
             "就是腫瘤丟掉的那段。右邊扣掉超過 5 Mb 沒有 SNV 的片段，再換算成兩條一樣長時的比例，"
             f"是 {g * 100:.1f} 比 {(1 - g) * 100:.1f}，信賴區間 {ci[0] * 100:.1f}% 到 {ci[1] * 100:.1f}%，幾乎各半；"
             "原始數字是每 Mb 9.34 對 9.31。"
             "任務一到這裡；下一頁回到任務二，看 HG008 有哪些資源。")
    write_page(pid, page(pid, "COLO829 T2T：原始 61:39，扣掉一條丟失的片段後約 50:50", s, "", notes))
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


def load_balanced_hp():
    """HP1 / HP2 SNV sums over the same balanced windows (2026-11-09: user wants both sides per line)."""
    out = {}
    for r in csv.DictReader(open(LAB / "2026-11-06_prcgap_hap_snv_ratio/per_window_20mb.tsv"), delimiter="\t"):
        d = out.setdefault(r["sample"], [0, 0])
        d[0] += int(r["hap1_snv"])
        d[1] += int(r["hap2_snv"])
    return out


def p9():
    pid = "balance"
    s = S(pid, 1200, 460)
    data = load_balanced()
    assert sorted(data) == sorted(P9_ORDER) and sum(v[0] for v in data.values()) == 229, data
    # 2026-11-08: three-layer ladder removed at the user's request.

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
    hp = load_balanced_hp()
    assert sorted(hp) == sorted(P9_ORDER), hp
    s.text(770, 40, "每格：這些區段的 SNV 加總", "s")
    s.bar(770, 58, 40, "hp1", 14)
    s.text(818, 70, "HP1", "s", "start", "hp1")
    s.bar(870, 58, 40, "hp2", 14)
    s.text(918, 70, "HP2", "s", "start", "hp2")
    s.text(770, 100, "HP1 編號跨染色體可能對調（上一頁）", "s")
    cw, ch, gx, gy = 292, 148, 10, 152
    fr = {}
    for i, name in enumerate(P9_ORDER):
        a, b = hp[name]
        f = a / (a + b)
        fr[name] = f
        x = gx + (i % 4) * (cw + 4)
        y = gy + (i // 4) * (ch + 6)
        s.rect(x, y, cw, ch, "panel", r=10)
        s.text(x + 14, y + 30, name, "h")
        chk, col = P9_CHECK.get(name, ("未獨立驗證", "mute"))
        s.text(x + cw - 12, y + 30, chk, "s", "end", col)
        bx, bw, by, bh = x + 14, cw - 28, y + 52, 36
        s.rect(bx, by, bw * f, bh, "hp1", r=0)
        s.rect(bx + bw * f, by, bw * (1 - f), bh, "hp2", r=0)
        s.line(bx + bw / 2, by - 5, bx + bw / 2, by + bh + 5, "ink", 1.5, dash=True)
        s.text(bx + 8, by + 25, f"HP1 {f * 100:.1f}%", "s", "start", "on")
        s.text(bx + bw - 8, by + 25, f"HP2 {(1 - f) * 100:.1f}%", "s", "end", "on")
        s.text(bx, y + 124, f"{a + b:,} 個 SNV", "s", "start", "mute")
    # random expectation and window counts were dropped from the page on 2026-11-08 (user request);
    # they stay in BRIEF.md. 2026-11-09: larger-side share replaced by HP1 / HP2 shares (user comment).
    print("p9 obs-random gap (pp):", [f"{(data[n][1] - data[n][2]) * 100:.1f}" for n in P9_ORDER])
    print("p9 HP1 share (%):", {n: round(fr[n] * 100, 1) for n in P9_ORDER})
    lo, hi = min(fr.values()) * 100, max(fr.values()) * 100

    notes = ("這頁看 PRCGAP 這個公開資料集的 8 株細胞株。上面是算法：只算兩條份數相同的 20 Mb 區段，"
             "1 份對 1 份就算，2 份對 1 份或一條流失就不算。下面一格一株，"
             "把這些區段的 SNV 加總，藍色是 HP1、橘色是 HP2，虛線是一半。"
             f"8 株的 HP1 落在 {lo:.1f}% 到 {hi:.1f}%，都接近一半。"
             "要注意 HP1 編號跨染色體可能對調，所以加總只能參考。"
             "右上角是有沒有獨立核對，只有 HG008 核對過。下一頁看其中一株 COLO829 的細節。")
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
    # p10 local was deleted by the user in the deck editor on 2026-11-08; p10() kept for reference only.
    for f in (p8, p_t2t, p9):
        n = f()
        print(f.__name__, "notes chars:", len(n))
