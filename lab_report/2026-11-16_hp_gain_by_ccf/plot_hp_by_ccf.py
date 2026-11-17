"""Figure hp_by_ccf.png from hp_by_ccf_per_clone.tsv. Run: python3 plot_hp_by_ccf.py (needs matplotlib, so not -I)"""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = list(csv.DictReader(open("hp_by_ccf_per_clone.tsv"), delimiter="\t"))
CB = [("<0.3", 0, .3), ("0.3-0.6", .3, .6), ("0.6-0.8", .6, .8), (">=0.8", .8, 9)]
fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
for a, (col, title, gsel) in zip(ax, [("found", "Clones found (80/80 rule)", lambda g: True),
                                       ("found", "Clones found, CCF gap >= 0.1 only", lambda g: g >= 0.1),
                                       ("snv_correct", "Share of the clone's SNVs assigned correctly", lambda g: True)]):
    for k, (mode, color, lab) in enumerate([("base", "#999999", "without HP"), ("a1", "#1b6ca8", "with HP (A1)")]):
        ys, ns = [], []
        for _, lo, hi in CB:
            rr = [float(r[col]) for r in R if r["mode"] == mode and lo <= float(r["ccf"]) < hi and gsel(float(r["gap"]))]
            ys.append(100 * sum(rr) / max(len(rr), 1)); ns.append(len(rr))
        xs = [i + (k - 0.5) * 0.38 for i in range(4)]
        a.bar(xs, ys, 0.36, color=color, label=lab)
        for x, y in zip(xs, ys):
            a.text(x, y + 1.5, f"{y:.0f}", ha="center", fontsize=8)
    a.set_xticks(range(4)); a.set_xticklabels([f"{c[0]}\n(n={n})" for c, n in zip(CB, ns)])
    a.set_ylim(0, 100); a.set_xlabel("clone CCF"); a.set_ylabel("%"); a.set_title(title, fontsize=10)
ax[0].legend(fontsize=8)
fig.suptitle("Ceiling with known CCFs: 300 diplosim trees, 5 clones, 1,000 SNVs, 60x, purity 0.9, all 1+1 (non-truncal clones)", fontsize=9)
fig.tight_layout(); fig.savefig("hp_by_ccf.png", dpi=150)
