"""Figure ceiling_vs_density.png. Numbers are typed from oracle_pairs_summary.txt (ceilings) and
../2026-11-15_diplosim_c4_center/summary_center.txt, ../2026-11-15_diplosim_c4_density/summary_d*.txt (haploclone).
Run: python3 plot_ceiling.py   (needs matplotlib, so not -I)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

x = [5.3, 20, 50, 100]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ser = [("ceiling with pairs (neighbours known)", [2.40, 2.70, 3.20, 4.00], "#1b6ca8", "o-"),
       ("ceiling, simple search from counts", [2.40, 2.40, 3.00, 3.30], "#6aa9d8", "s--"),
       ("haploclone A1 + pairs (pooled)", [2.15, 2.15, 2.35, 3.00], "#d1603d", "^-"),
       ("haploclone A1 (counts only)", [1.95] * 4, "#999999", "x:")]
for lab, y, c, f in ser:
    ax[0].plot(x, y, f, color=c, label=lab)
ax[0].axhline(5, color="k", lw=.6)
ax[0].text(6, 4.85, "5 true clones", va="top", fontsize=8)
ax[0].set_xscale("log"); ax[0].set_xticks(x); ax[0].set_xticklabels(["5.3\n(HG008 level)", "20", "50", "100"])
ax[0].set_ylim(0, 5.2); ax[0].set_xlabel("SNVs per Mb"); ax[0].set_ylabel("clones found (80/80 rule, of 5)")
ax[0].set_title("All clones"); ax[0].legend(fontsize=7.5, loc="lower left")
ser2 = [("ceiling with pairs (neighbours known)", [1 / 17, 2 / 17, 4 / 17, 10 / 17], "#1b6ca8", "o-"),
        ("ceiling, simple search from counts", [1 / 17, 1 / 17, 3 / 17, 4 / 17], "#6aa9d8", "s--"),
        ("haploclone A1 + pairs (pooled)", [2 / 34, 2 / 34, 4 / 34, 4 / 34], "#d1603d", "^-")]
for lab, y, c, f in ser2:
    ax[1].plot(x, [100 * v for v in y], f, color=c, label=lab)
ax[1].set_xscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels(["5.3", "20", "50", "100"])
ax[1].set_ylim(0, 100); ax[1].set_xlabel("SNVs per Mb"); ax[1].set_ylabel("% of clones found")
ax[1].set_title("Clones with CCF gap < 0.1 (17 clones)")
fig.suptitle("60x, purity 0.9, 1+1, 1,000 SNVs, 10 trees, no sequencing error", fontsize=9)
fig.tight_layout(); fig.savefig("ceiling_vs_density.png", dpi=150)
