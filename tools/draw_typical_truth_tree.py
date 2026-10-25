"""Draw the typical HP-aware truth tree (tools/typical_truth_tree.py) in the style of
draw_hp_truth_tree.py, with a panel that ties each parameter to measured TRACERx / PCAWG values.

Usage: python3 tools/draw_typical_truth_tree.py OUT.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_hp_truth_tree as T  # noqa: E402
import typical_truth_tree as Y  # noqa: E402

Y.install(T)
plt = T.plt
HP1, HP2, LOSS, NOTE, GREY, PURPLE = T.HP1, T.HP2, T.LOSS, T.NOTE, T.GREY, T.PURPLE

# parameter, stress tree, typical tree, measured basis
PARAMS = [
    ("purity", "0.40", "0.40", "TRACERx 421 tumour 中位 0.39"),
    ("clone 數", "4", "3", "PCAWG-11：21% 有 2 個 subclone"),
    ("樹形", "分岔", "直線", "TRACERx 421 單區域 73% 為直線"),
    ("subclone CCF", ".80/.45/.10", ".58/.29", "TRACERx 421 單區域 中位 .58、q25 .29"),
    ("clonal SNV", "50%", "70%", "TRACERx 100 中位 30% subclonal"),
    ("突變遺失", "20%", "1.5%", "TRACERx 421 Q90 1.4%、最高 11.7%"),
    ("subclonal HP gain", "+1 copy", "+1 copy", "TRACERx 421：91% tumour 有，91% 只差 1"),
    ("gain 區 early 比例", "0.50", "0.30", "PCAWG 2:1 區 中位 0.28（IQR .18–.40）"),
    ("subclonal cnLOH", "CCF .80", "CCF .29", "TRACERx 421：72% tumour 有，中位 7.2 Mb"),
    ("subclonal CN 範圍", "3／4 段", "約 10%", "PCAWG 中位 7.6% 基因組"),
    ("低 CCF clone", "0.10", "無", "TRACERx 421 單區域 8.4% ≤ 0.15"),
    ("depth", "200×", "50×／200×", "PCAWG 中位 48.5×；ONT 多在 30–60×"),
]

ROLE_NOTE = {
    "t1": "gain 前 → mult 2", "t2": "未 gain 的 HP", "t5": "cnLOH 前 → mult 2",
    "t6": "C3 中遺失", "t7": "gain 後 → mult 1", "t10": "cnLOH 後 → mult 1",
}


def main(out):
    fig = plt.figure(figsize=(26, 14), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 260)
    ax.set_ylim(0, 140)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(2, 136, "典型 HP-aware 腫瘤演化樹真值（對照組）：每個參數取自 TRACERx 421／PCAWG 實測",
            fontsize=19, weight="bold", va="center")
    ax.text(2, 132, "和壓力測試樹（hp_truth_tree.png）用同一套事件，但比例與密度改成真實 cohort 的典型值。"
            "共 200 個 SNV；圖中每個點代表一種 SNV 角色。", fontsize=10.5, color="#4a5568", va="center")

    # ---- tree: linear N -> C1 -> C2 -> C3
    W, H, ty = T.W, T.H, 95
    xs = {"N": 2, "C1": 48, "C2": 94, "C3": 140}
    T.draw_clone(ax, xs["N"], ty, "N", "Normal（root）", f"樣本中 {1 - T.PURITY:.0%} normal cell")
    title = {"C1": "C1 truncal", "C2": "C2", "C3": "C3"}
    for c in T.PROP:
        sub = f"tumour 內 {T.PROP[c]:.0%}｜CCF {T.ccf(c):.2f}｜cell prev. {T.PURITY * T.ccf(c):.2f}"
        T.draw_clone(ax, xs[c], ty, c, title[c], sub)
    n = Y.N_SNV
    T.edge(ax, (xs["N"] + W, ty + H / 2), (xs["C1"], ty + H / 2),
           f"+t1×{n['t1']} t3×{n['t3']} t5×{n['t5']} (HP1)\n+t2×{n['t2']} t4×{n['t4']} t6×{n['t6']} (HP2)",
           lx=xs["N"] + W + 4.5, ly=ty + H + 5.5)
    T.edge(ax, (xs["C1"] + W, ty + H / 2), (xs["C2"], ty + H / 2),
           f"+t7×{n['t7']} t8×{n['t8']} (HP1)  +t9×{n['t9']} (HP2)\n"
           "seg A HP1 +1 gain（t1 之後、t7 之前）", lx=xs["C1"] + W + 4.5, ly=ty - 5.5, color=NOTE)
    T.edge(ax, (xs["C2"] + W, ty + H / 2), (xs["C3"], ty + H / 2),
           f"+t10×{n['t10']} t11×{n['t11']} (HP1)  +t12×{n['t12']} (HP2)\n"
           "seg D cnLOH（HP2 被 HP1 複本取代）→ t6 遺失", lx=xs["C2"] + W + 4.5, ly=ty + H + 5.5,
           color=LOSS)

    # ---- SNV role table
    ax.text(2, 84, "SNV 角色（multiplicity = 該 clone 中帶這個 SNV 的 copy 數；0 = 遺失）", fontsize=11,
            weight="bold", va="center")
    cols = ["角色", "個數", "起源", "HP", "seg", "mult C1", "mult C2", "mult C3", "實際帶突變",
            "期望 VAF", "設計目的"]
    widths = [9, 9, 9, 9, 9, 12, 12, 12, 15, 13, 34]
    rows = []
    for s, (org, hp, seg) in T.SNV.items():
        tot, alt, _ = T.snv_truth(s)
        mult = [T.copies(c, seg, hp, s) for c in ("C1", "C2", "C3")]
        clones = ["C1", "C2", "C3"]
        born = clones.index(org)
        mcells = [("—", GREY) if i < born else ((str(m), LOSS) if m == 0 else
                  ((str(m), NOTE) if m > 1 else str(m))) for i, m in enumerate(mult)]
        note = ROLE_NOTE.get(s, "對照")
        rows.append([s, n[s], org, (hp, HP1 if hp == "HP1" else HP2), seg, *mcells,
                     f"{T.carrier_fraction(s):.2f}", f"{alt / tot:.3f}",
                     (note, LOSS if "遺失" in note else (NOTE if "mult 2" in note else "#1a202c"))])
    T.table(ax, 2, 81.5, cols, rows, widths, fs=8.2, rh=2.6)

    # ---- event legend
    T.box(ax, 2, 2, 175, 42, fc="white", ec="#cbd5e0")
    ax.text(4, 41, "7 類測試目標在典型樹中的設定", fontsize=12, weight="bold", va="center")
    items = [
        (1, "低 purity", "purity 0.40，等於 TRACERx 421 的中位數。"),
        (2, "subclonal HP gain", "seg A 的 HP1 +1 copy，只在 C2、C3（58% tumour 細胞）。"),
        (3, "突變遺失", "t6 在 C3 隨 cnLOH 消失：3／200 = 1.5%。"),
        (4, "低 CCF clone", "刻意不放。最小 subclone C3 的 CCF 0.29。"),
        (5, "HP1／HP2 細分", "每個 SNV 有 HP 真值；兩條 HP 上的 SNV 數相近。"),
        (6, "subclonal cnLOH", "seg D 只在 C3（CCF 0.29）變成 HP1×2。total CN 不變。"),
        (7, "CN timing", "seg A：t1 在 gain 前（mult 2），t2／t7 為 mult 1；early 比例 3／10 = 0.30。"),
    ]
    for i, (k, name, desc) in enumerate(items):
        cx, cy = 4, 36.2 - i * 4.6
        T.badge(ax, cx + 1.5, cy, k)
        ax.text(cx + 4, cy, name, fontsize=10, weight="bold", va="center",
                color=GREY if k == 4 else "#1a202c")
        ax.text(cx + 30, cy, desc, fontsize=9, va="center", color=GREY if k == 4 else "#2d3748")
    ax.text(128, 9, "圖例：黑點 = SNV 角色；同一條色線 = 同一份 copy；\n虛線＋× = 被刪除的 copy 與遺失的 SNV",
            fontsize=8.3, color=GREY, va="center", linespacing=1.3)

    # ---- right panel: parameters vs measured data
    rx = 184.5
    T.box(ax, rx - 1.5, 2, 76, 128, fc="#fcfcfd", ec="#a0aec0", lw=1.4)
    ax.text(rx, 127, "參數與真實資料對照", fontsize=13, weight="bold", va="center")
    ax.text(rx, 123, "壓力測試樹偏離典型值的參數以紅字標示", fontsize=8.5, color=GREY, va="center")
    cols = ["參數", "壓力測試樹", "典型樹", "實測依據"]
    widths = [15, 11, 10, 37]
    off = {"clone 數", "樹形", "突變遺失", "gain 區 early 比例", "subclonal CN 範圍", "depth"}
    rows = [[p, (st, LOSS if p in off else "#1a202c"), (ty_, NOTE), basis]
            for p, st, ty_, basis in PARAMS]
    y = T.table(ax, rx, 120, cols, rows, widths, fs=8.2, rh=3.4)

    ax.text(rx, y - 3, "兩棵樹的角色", fontsize=11, weight="bold", va="center")
    notes = [
        "• 壓力測試樹：7 類事件集中、比例偏高。檢查方法在極端情況下的表現。",
        "• 典型樹：同樣的事件，比例與密度取 cohort 中位數或常見值。",
        "  代表只有一個 bulk 樣本時的一般腫瘤。",
        "• 兩棵樹的事件都在真實腫瘤中觀察過（HG008、SEQC2、TRACERx、PCAWG）。",
    ]
    for i, t in enumerate(notes):
        ax.text(rx + 1, y - 7 - i * 3.2, t, fontsize=8.6, va="center", color="#2d3748")
    y = y - 7 - len(notes) * 3.2
    ax.text(rx, y - 2.5, "證據：research/simulation_pipeline_research/truth_evidence_2026-10-25/\n"
            "lab_report/2026-10-25_{tracerx,pcawg}_event_stats/",
            fontsize=7.6, color=GREY, va="top", linespacing=1.4)

    fig.savefig(out, dpi=150, facecolor="white")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "typical_truth_tree.png")
