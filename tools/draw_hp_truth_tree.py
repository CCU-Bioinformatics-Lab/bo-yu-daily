"""Draw a conceptual HP-aware tumour evolution tree and the bulk data a simulator must emit.

The tree is a designed example, not a run of any simulator. It packs seven test targets into
one truth: low purity, subclonal CN, mutation loss, a low-CCF clone, HP1/HP2 labels that are
consistent across loci (SISTEM allele 0/1 style), copy-neutral LOH, and an SNV that arises
after a gain on the same HP. The right panel samples one bulk run from that truth (binomial
counts, partial phasing) and shows the per-SNV CCF that PhyClone's likelihood would give.

Usage: python3 tools/draw_hp_truth_tree.py OUT.png
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from scipy.stats import binom

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

HP1, HP2 = "#2b6cb0", "#dd6b20"
LOSS, NOTE, GREY, PURPLE = "#c53030", "#2f855a", "#718096", "#6b46c1"

# ---------------------------------------------------------------- truth
PURITY = 0.40
PROP = {"C1": 0.10, "C2": 0.35, "C3": 0.10, "C4": 0.45}  # fraction of tumour cells
CHILDREN = {"C1": ["C2", "C3"], "C2": ["C4"], "C3": [], "C4": []}
SEGS = ["A", "B", "C", "D"]


def ccf(c):
    return PROP[c] + sum(ccf(k) for k in CHILDREN[c])


# SNV -> (origin clone, HP, segment)
SNV = {
    "s1": ("C1", "HP1", "A"), "s2": ("C1", "HP2", "B"), "s3": ("C1", "HP1", "C"),
    "s4": ("C2", "HP2", "C"), "s5": ("C4", "HP1", "C"),
    "s6": ("C3", "HP2", "C"), "s7": ("C3", "HP1", "C"),
    "s8": ("C4", "HP1", "A"),
    "s9": ("C1", "HP1", "D"), "s10": ("C1", "HP2", "D"),
}

# per clone: segment -> HP -> list of copies, each copy = SNVs it carries
GENOME = {
    "N": {s: {"HP1": [[]], "HP2": [[]]} for s in SEGS},
    "C1": {"A": {"HP1": [["s1"]], "HP2": [[]]}, "B": {"HP1": [[]], "HP2": [["s2"]]},
           "C": {"HP1": [["s3"]], "HP2": [[]]}, "D": {"HP1": [["s9"]], "HP2": [["s10"]]}},
    "C2": {"A": {"HP1": [["s1"], ["s1"]], "HP2": [[]]}, "B": {"HP1": [[]], "HP2": [["s2"]]},
           "C": {"HP1": [["s3"]], "HP2": [["s4"]]}, "D": {"HP1": [["s9"], ["s9"]], "HP2": []}},
    "C4": {"A": {"HP1": [["s1", "s8"], ["s1"]], "HP2": [[]]}, "B": {"HP1": [[]], "HP2": []},
           "C": {"HP1": [["s3", "s5"]], "HP2": [["s4"]]}, "D": {"HP1": [["s9"], ["s9"]], "HP2": []}},
    "C3": {"A": {"HP1": [["s1"]], "HP2": [[]]}, "B": {"HP1": [[]], "HP2": [["s2"]]},
           "C": {"HP1": [["s3", "s7"]], "HP2": [["s6"]]}, "D": {"HP1": [["s9"]], "HP2": [["s10"]]}},
}
LOST = {"C2": [("D", "HP2", "s10")], "C4": [("B", "HP2", "s2"), ("D", "HP2", "s10")]}

# cell fractions in the bulk sample, normal included
CELL = {"N": 1 - PURITY, **{c: PURITY * p for c, p in PROP.items()}}


def copies(clone, seg, hp, snv=None):
    cps = GENOME[clone][seg][hp]
    return len(cps) if snv is None else sum(snv in cp for cp in cps)


def snv_truth(s):
    _, hp, seg = SNV[s]
    tot = sum(f * (copies(c, seg, "HP1") + copies(c, seg, "HP2")) for c, f in CELL.items())
    alt = sum(f * copies(c, seg, hp, s) for c, f in CELL.items())
    hp_tot = {h: sum(f * copies(c, seg, h) for c, f in CELL.items()) for h in ("HP1", "HP2")}
    return tot, alt, hp_tot


def carrier_fraction(s):
    """Fraction of tumour cells that still carry the SNV (after any loss)."""
    _, hp, seg = SNV[s]
    return sum(p for c, p in PROP.items() if copies(c, seg, hp, s) > 0)


def dominant_cn(seg):
    """Integer major/minor CN a bulk caller would report: the tumour state with most cells."""
    w = {}
    for c, p in PROP.items():
        st = (copies(c, seg, "HP1"), copies(c, seg, "HP2"))
        w[st] = w.get(st, 0) + p
    st = max(w, key=w.get)
    return max(st), min(st)


def phyclone_ccf(ref, alt, major, minor, t, normal_cn=2, err=1e-3):
    """Per-SNV MLE of f under PhyClone's genotype prior and binomial likelihood.

    Mirrors phyclone/data/pyclone.py::get_major_cn_prior and
    phyclone/utils/math_utils.py::log_pyclone_binomial_pdf.
    """
    total = major + minor
    cn = [(normal_cn, normal_cn, total) for _ in range(1, major + 1)]
    mu = [(err, err, min(1 - err, x / total)) for x in range(1, major + 1)]
    if total != normal_cn:
        cn.append((normal_cn, total, total))
        mu.append((err, err, min(1 - err, 1 / total)))
    cn, mu = np.array(cn, float), np.array(mu, float)
    fs = np.linspace(0, 1, 401)
    ll = []
    for f in fs:
        prior = np.array([1 - t, t * (1 - f), t * f])
        e_cn = cn * prior
        vaf = (e_cn * mu).sum(1) / e_cn.sum(1)
        ll.append(np.logaddexp.reduce(binom.logpmf(alt, ref + alt, vaf)) - np.log(len(cn)))
    return fs[int(np.argmax(ll))]


def expected_counts(s, mean_depth):
    """Noise-free ref/alt at the mean depth, to separate model bias from sampling noise."""
    tot, alt, _ = snv_truth(s)
    dp = mean_depth * tot / 2
    a = round(dp * alt / tot)
    return round(dp) - a, a


def simulate(rng, mean_depth=200, phased=0.85):
    rows = []
    for s in SNV:
        tot, alt, hp_tot = snv_truth(s)
        hp = SNV[s][1]
        other = "HP2" if hp == "HP1" else "HP1"
        dp = rng.poisson(mean_depth * tot / 2)
        a = rng.binomial(dp, alt / tot)
        r = dp - a
        a_ph = rng.binomial(a, phased)
        r_ph = rng.binomial(r, phased)
        # ref reads split by ref copies on each HP
        ref_hp = hp_tot[hp] - alt
        r_hp = rng.binomial(r_ph, ref_hp / (ref_hp + hp_tot[other]))
        maj, mnr = dominant_cn(SNV[s][2])
        cnt = {hp: (r_hp, a_ph), other: (r_ph - r_hp, 0)}
        rows.append(dict(id=s, ref=r, alt=a, vaf=alt / tot, maj=maj, mnr=mnr,
                         r1=cnt["HP1"][0], a1=cnt["HP1"][1], r2=cnt["HP2"][0], a2=cnt["HP2"][1],
                         unph=dp - a_ph - r_ph,
                         f_hat=phyclone_ccf(r, a, maj, mnr, PURITY),
                         f_exp=phyclone_ccf(*expected_counts(s, mean_depth), maj, mnr, PURITY)))
    return rows


def cooccur(rng, a, b, n_reads):
    """Reads on one HP spanning SNVs a and b: counts of (a,b) presence patterns."""
    hp, seg = SNV[a][1], SNV[a][2]
    w = {c: f * copies(c, seg, hp) for c, f in CELL.items()}
    cells = list(w)
    p = np.array([w[c] for c in cells]) / sum(w.values())
    out = {"++": 0, "+-": 0, "-+": 0, "--": 0}
    for c in rng.choice(cells, size=n_reads, p=p):
        cp = GENOME[c][seg][hp][0] if GENOME[c][seg][hp] else []
        out[("+" if a in cp else "-") + ("+" if b in cp else "-")] += 1
    return out


# ---------------------------------------------------------------- drawing helpers
def box(ax, x, y, w, h, fc="white", ec="#4a5568", lw=1.2, r=1.2, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls))


def badge(ax, x, y, k):
    ax.text(x, y, str(k), ha="center", va="center", fontsize=10, color="white", weight="bold",
            bbox=dict(boxstyle="circle,pad=0.25", fc=LOSS, ec="none"))


W, H = 37, 25


def draw_clone(ax, x, y, name, title, sub):
    box(ax, x, y, W, H, fc="#f7fafc" if name != "N" else "#edf2f7")
    ax.text(x + W / 2, y + H - 2.2, title, ha="center", va="center", fontsize=11, weight="bold")
    ax.text(x + W / 2, y + H - 5.0, sub, ha="center", va="center", fontsize=8.5, color="#2d3748")
    segx = {s: x + 5.5 + 8 * i for i, s in enumerate(SEGS)}
    for seg, sx in segx.items():
        ax.text(sx + 3, y + 1.3, f"seg {seg}", ha="center", fontsize=7, color=GREY)
    base = {"HP1": y + 11.5, "HP2": y + 4.2}
    for hp, by in base.items():
        ax.text(x + 2.6, by + 1.2, hp, ha="center", va="center", fontsize=7.5,
                color=HP1 if hp == "HP1" else HP2, weight="bold")
        for seg, sx in segx.items():
            cps = GENOME[name][seg][hp]
            for i, cp in enumerate(cps):
                yy = by + i * 2.6
                ax.plot([sx, sx + 6], [yy, yy], color=HP1 if hp == "HP1" else HP2, lw=3.2,
                        solid_capstyle="round")
                for j, s in enumerate(cp):
                    px = sx + 1 + j * 2.2 if seg == "C" else (sx + 1.6 + j * 2.8 if len(cp) > 1
                                                              or seg == "A" else sx + 3)
                    ax.plot(px, yy, "o", ms=4.5, mfc="black", mec="white", mew=0.6)
                    ax.text(px, yy + 1.0, s, ha="center", va="bottom", fontsize=6.5)
            for (lseg, lhp, ls) in LOST.get(name, []):
                if lseg == seg and lhp == hp:
                    ax.plot([sx, sx + 6], [by, by], color=GREY, lw=1.5, ls=(0, (2, 2)))
                    ax.plot(sx + 3, by, "x", ms=7, mew=2, color=LOSS)
                    ax.text(sx + 3, by + 1.0, ls, ha="center", va="bottom", fontsize=6.5,
                            color=LOSS, weight="bold")
                    if seg == "D":
                        ax.text(sx + 3, by - 1.6, "cnLOH", ha="center", va="center",
                                fontsize=6.5, color=PURPLE, weight="bold")


def edge(ax, p, q, label, color="#2d3748", lx=None, ly=None, ha="center"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#4a5568",
                                                     shrinkA=0, shrinkB=0))
    if label:
        mx = (p[0] + q[0]) / 2 if lx is None else lx
        my = (p[1] + q[1]) / 2 if ly is None else ly
        ax.text(mx, my, label, ha=ha, va="center", fontsize=8.5, color=color, linespacing=1.4,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#cbd5e0", lw=0.8))


def table(ax, x, y, cols, rows, widths, fs=7.8, rh=2.35, head_fc="#edf2f7", colors=None):
    tw = sum(widths)
    box(ax, x, y - rh, tw, rh, fc=head_fc, ec="none", r=0.4)
    cx = x
    for c, w in zip(cols, widths):
        ax.text(cx + w / 2, y - rh / 2, c, ha="center", va="center", fontsize=fs, weight="bold",
                color=(colors or {}).get(c, "#1a202c"))
        cx += w
    for i, r in enumerate(rows):
        yy = y - rh * (i + 1.5)
        if i % 2:
            box(ax, x, yy - rh / 2, tw, rh, fc="#f7fafc", ec="none", r=0.2)
        cx = x
        for v, w in zip(r, widths):
            col = v[1] if isinstance(v, tuple) else "#1a202c"
            txt = v[0] if isinstance(v, tuple) else v
            ax.text(cx + w / 2, yy, txt, ha="center", va="center", fontsize=fs, color=col)
            cx += w
    return y - rh * (len(rows) + 1)


# PhyClone panel: why each SNV misfits, keyed by SNV (judged on the noise-free estimate)
PHY_NOTE = {
    "s1": ("subclonal gain → 低估", LOSS),
    "s2": ("遺失 → 不像任何 clone", LOSS),
    "s8": ("gain 之後，mult 1 正確", NOTE),
    "s9": ("cnLOH 只在 C2/C4 → 低估", LOSS),
    "s10": ("cnLOH 遺失 → 像 C3", LOSS),
}


# ---------------------------------------------------------------- figure
def main(out):
    rng = np.random.default_rng(7)
    rows = simulate(rng)
    co46 = cooccur(rng, "s4", "s6", 80)
    co35 = cooccur(rng, "s3", "s5", 80)

    fig = plt.figure(figsize=(26, 14), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 260)
    ax.set_ylim(0, 140)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(2, 136, "HP-aware 腫瘤演化樹真值（設計範例）→ bulk 定序模擬資料 → PhyClone 會怎麼錯",
            fontsize=19, weight="bold", va="center")
    ax.text(2, 132, "一棵樹放入 7 個測試目標。HP1／HP2 標籤全基因組一致（SISTEM allele 0／1 型真值），"
            "不是 CONIPHER 逐位點的 A／B。", fontsize=10.5, color="#4a5568", va="center")

    # ---- tree
    pos = {"N": (2, 62), "C1": (46, 62), "C2": (90, 98), "C3": (90, 33), "C4": (134, 98)}
    sub = {c: f"tumour 內 {PROP[c]:.0%}｜CCF {ccf(c):.2f}｜cell prev. {PURITY * ccf(c):.2f}"
           for c in PROP}
    draw_clone(ax, *pos["N"], "N", "Normal（root）", f"樣本中 {1 - PURITY:.0%} normal cell")
    for c in PROP:
        t = {"C1": "C1 truncal", "C2": "C2", "C3": "C3 低 CCF", "C4": "C4"}[c]
        draw_clone(ax, *pos[c], c, t, sub[c])

    edge(ax, (2 + W, 62 + H / 2), (46, 62 + H / 2), "+s1 s3 s9 (HP1)   +s2 s10 (HP2)",
         lx=41.5, ly=62 + H + 4)
    edge(ax, (46 + W / 2, 62 + H), (90, 98 + H / 2),
         "+s4 (HP2)\nseg A HP1 gain（在 s1 之後）→ s1 multiplicity 2\n"
         "seg D cnLOH（HP2 被 HP1 複本取代）\n→ s9 multiplicity 2、s10 遺失",
         lx=60, ly=113, color=NOTE)
    edge(ax, (46 + W / 2, 62), (90, 33 + H / 2), "+s6 (HP2)  +s7 (HP1)", lx=66, ly=50)
    edge(ax, (90 + W, 98 + H / 2), (134, 98 + H / 2),
         "+s5 (HP1)\n+s8 (HP1, seg A, gain 之後 → multiplicity 1)\nseg B HP2 deletion → s2 遺失",
         lx=140, ly=129, color=LOSS)

    badge(ax, 3.5, 62 + H - 1.5, 1)
    badge(ax, 44.6, 114.2, 2)
    badge(ax, 44.6, 110.8, 6)
    badge(ax, 125.8, 126.7, 3)
    badge(ax, 154.2, 129, 7)
    badge(ax, 91.5, 33 + H - 1.5, 4)
    badge(ax, 47.5, 62 + H - 1.5, 5)

    # ---- legend of targets (bottom strip, two columns)
    box(ax, 2, 2, 170, 27, fc="white", ec="#cbd5e0")
    ax.text(4, 26.5, "每個測試目標在資料中的訊號", fontsize=12, weight="bold", va="center")
    items = [
        (1, "低 purity", f"purity {PURITY:.2f}（實際值，不是 nominal）。VAF 被 normal 稀釋；\n"
                       "tumour_content 要給真值。"),
        (2, "subclonal CN", "seg A 的 HP1 gain 只在 C2、C4。HP1 alt 比例升高，HP2 不變；\n"
                           "整數 major／minor 欄位表達不了。"),
        (3, "突變遺失", "s2 在 C4 隨 HP2 deletion 消失。s2 的 CCF 看起來 < C1，\n"
                      "但 seg B 的 HP2 depth 同時下降。"),
        (4, "低 CCF clone", f"C3 cell prev. {PURITY * ccf('C3'):.2f}。帶 s6 的 HP2 read 從不帶 s4\n"
                          "→ C3 不在 C2 之下（拓樸）。"),
        (5, "HP1／HP2 細分", "每個 SNV 有 HP 真值。同 HP 的 SNV 可在同一條 read 上共現；\n"
                          "不同 HP 的 SNV 不會。"),
        (6, "cnLOH", "seg D 的 total CN 一直是 2，total depth 看不到。只有 HP 看得到：\n"
                     "HP2 depth 降到只剩 C1、C3 與 normal；s9 ×2、s10 遺失。"),
        (7, "CN timing", "s1、s8 都在 seg A 的 HP1。s1 在 gain 之前（multiplicity 2），\n"
                         "s8 在 gain 之後（multiplicity 1）。"),
    ]
    for i, (k, name, desc) in enumerate(items):
        cx, cy = (4, 88)[i // 4], 21.3 - (i % 4) * 5.3
        badge(ax, cx + 1.5, cy, k)
        ax.text(cx + 4, cy, name, fontsize=10, weight="bold", va="center")
        ax.text(cx + 18, cy, desc, fontsize=8.3, va="center", color="#2d3748", linespacing=1.3)
    ax.text(92, 5.4, "圖例：黑點 = SNV；同一條色線 = 同一份 copy；\n虛線＋× = 被刪除的 copy 與遺失的 SNV",
            fontsize=8.3, color=GREY, va="center", linespacing=1.3)

    # ---- big arrow
    ax.add_patch(FancyArrowPatch((172.5, 70), (181.5, 70), arrowstyle="simple,head_width=4,head_length=3",
                                 mutation_scale=12, fc="#4a5568", ec="none"))
    ax.text(177, 78, "bulk 定序\n模擬", ha="center", va="center", fontsize=11, weight="bold")
    ax.text(177, 62, "binomial 抽樣\n部分 phasing\nmean 200×", ha="center", va="center",
            fontsize=8, color=GREY)

    # ---- right panel
    rx = 184.5
    box(ax, rx - 1.5, 2, 76, 128, fc="#fcfcfd", ec="#a0aec0", lw=1.4)
    ax.text(rx, 127, "模擬器必須輸出的資料（seed 7 抽樣一次）", fontsize=13, weight="bold", va="center")

    ax.text(rx, 122.5, "① 每個 SNV 的計數：PhyClone 現有欄位＋新增 HP 拆分", fontsize=10,
            weight="bold", va="center")
    cols = ["SNV", "ref", "alt", "major", "minor", "ref_HP1", "alt_HP1", "ref_HP2", "alt_HP2",
            "unphased"]
    widths = [6, 6.5, 6, 6.5, 6.5, 8, 8, 8, 8, 9]
    trows = [[r["id"], r["ref"], r["alt"], r["maj"], r["mnr"], r["r1"],
              (str(r["a1"]), HP1 if r["a1"] else "#1a202c"), r["r2"],
              (str(r["a2"]), HP2 if r["a2"] else "#1a202c"), r["unph"]] for r in rows]
    y = table(ax, rx, 120.5, cols, trows, widths,
              colors={"ref_HP1": HP1, "alt_HP1": HP1, "ref_HP2": HP2, "alt_HP2": HP2})
    ax.text(rx, y - 1.6, f"normal_cn = 2、tumour_content = {PURITY:.2f}（所有列相同）。"
            "major／minor = 細胞數最多的 tumour 狀態。藍／橘 = 新增欄位",
            fontsize=7.6, color=GREY, va="center")
    y -= 3.2

    ax.text(rx, y - 2.5, "② 新增：read 層級 SNV 共現（同一 HP、跨兩個 SNV 的 80 條 read）",
            fontsize=10, weight="bold", va="center")
    cols = ["SNV 對", "HP", "兩者都有", "只有前者", "只有後者", "都沒有", "解讀"]
    widths = [8, 5, 8, 8, 8, 7, 28.5]
    trows = [["s4 – s6", ("HP2", HP2), (str(co46["++"]), LOSS), co46["+-"], co46["-+"], co46["--"],
              "s6 從不和 s4 同 read → C3 ⊄ C2"],
             ["s3 – s5", ("HP1", HP1), co35["++"], co35["+-"], (str(co35["-+"]), LOSS), co35["--"],
              "s5 必帶 s3 → C4 在 C1 之下"]]
    y = table(ax, rx, y - 4.5, cols, trows, widths)

    ax.text(rx, y - 2.5, "③ 新增：phasing 層", fontsize=10, weight="bold", va="center")
    lines = ["• germline het SNP（phasing 錨點）、PS block 邊界、每個 block 的 HP 方向隨機翻轉",
             "• switch error、unphased read 比例"]
    for i, t in enumerate(lines):
        ax.text(rx + 1, y - 5.8 - i * 2.8, t, fontsize=8.4, va="center")
    y = y - 5.8 - len(lines) * 2.8

    ax.text(rx, y - 1.8, "④ PhyClone 會怎麼錯：單一 SNV 的 CCF 最大概似值", fontsize=10,
            weight="bold", va="center")
    cols = ["SNV", "真值 clone", "起源 CCF", "實際帶突變", "估計：期望", "估計：抽樣", "問題"]
    widths = [5.5, 8, 8, 9, 9, 9, 24]
    trows = []
    for r in rows:
        s = r["id"]
        org = SNV[s][0]
        note, col = PHY_NOTE.get(s, ("一致", GREY))
        if s not in PHY_NOTE and abs(r["f_hat"] - r["f_exp"]) > 0.08:
            note, col = ("一致；抽樣誤差", GREY)
        hl = LOSS if col == LOSS else "#1a202c"
        trows.append([s, org, f"{ccf(org):.2f}", f"{carrier_fraction(s):.2f}",
                      (f"{r['f_exp']:.2f}", hl), f"{r['f_hat']:.2f}", (note, col)])
    y = table(ax, rx, y - 3.8, cols, trows, widths)
    ax.text(rx, y - 1.6, "用 PhyClone 的 genotype prior＋binomial likelihood 逐 SNV 求 f 的 MLE（不是完整 run，"
            "沒有 clustering）。期望 = 無抽樣誤差的計數。", fontsize=7.6, color=GREY, va="center")
    ax.text(rx, y - 4.0, "真值檔（評估用）：tree.nwk、clone 比例、purity、SNV→clone／HP、"
            "clone × segment haplotype CN、mutation loss 清單。", fontsize=7.6, color=GREY,
            va="center")

    fig.savefig(out, dpi=150, facecolor="white")
    for r in rows:
        print(r["id"], r["ref"], r["alt"], r["maj"], r["mnr"], round(r["vaf"], 3), r["f_hat"], r["f_exp"],
              carrier_fraction(r["id"]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hp_truth_tree.png")
