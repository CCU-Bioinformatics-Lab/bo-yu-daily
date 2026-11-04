"""One row per run from c4_truth_vs_map.py scores: MAP score, best truth-compatible score, verdict.

best_compat = the highest log_p_one over the truth tree, its contractions and their _opt rows,
among those that are role-level truth-compatible (compat = 1). map_compat comes from the scores
and is checked against the topology summary (map_compat_summary).
verdict (only when the MAP tree is not truth-compatible):
  tie       |best_compat - MAP| <= TIE (2 log units, posterior odds <= e^2): the model barely
            prefers either tree, so the posterior splits between them
  sampling  best_compat > MAP + TIE: the model prefers a truth-compatible tree the run did not find
  model     best_compat < MAP - TIE: the model itself prefers the wrong MAP tree on this data
Since _opt is a local search, `model` means "no compatible tree found that beats the MAP".

Usage: python3 tools/summarize_truth_vs_map.py scores.tsv TOPOLOGY_SUMMARY.tsv [...] > out.tsv
(max_wrong and map_compat_summary are blank for runs not in any topology summary.)
"""
import sys

import pandas as pd

TIE = 2.0

s = pd.read_csv(sys.argv[1], sep="\t")
s["run"] = s.run_dir.str.rsplit("/", n=1).str[-1]
topo = pd.concat([pd.read_csv(f, sep="\t") for f in sys.argv[2:]]).drop_duplicates(["sim", "run"])
rows = []
for (sim, run_dir), g in s.groupby(["sim", "run_dir"]):
    m = g[g.tree == "map"].iloc[0]
    t = g[g.tree.str.startswith("truth") & (g.compat == 1)]
    best = t.loc[t.log_p_one.idxmax()]
    rows.append({"sim": sim, "run": m.run, "run_dir": run_dir, "map_nodes": m.n_nodes,
                 "map_compat": m.compat,
                 "map_log_p": m.log_p_one, "best_compat": best.tree,
                 "best_compat_nodes": best.n_nodes, "best_minus_map": best.log_p_one - m.log_p_one,
                 "map_pair": m.pair_term, "best_pair": best.pair_term,
                 "map_data_ll": m.data_ll, "best_data_ll": best.data_ll,
                 "map_prior": m.prior, "best_prior": best.prior})
topo = topo.rename(columns={"map_compat": "map_compat_summary"})
d = pd.DataFrame(rows).merge(topo[["sim", "run", "map_compat_summary", "max_wrong"]],
                             on=["sim", "run"], how="left")
d["verdict"] = "ok"
wrong = d.map_compat == 0
d.loc[wrong & (d.best_minus_map.abs() <= TIE), "verdict"] = "tie"
d.loc[wrong & (d.best_minus_map > TIE), "verdict"] = "sampling"
d.loc[wrong & (d.best_minus_map < -TIE), "verdict"] = "model"
d.drop(columns="run_dir").to_csv(sys.stdout, sep="\t", index=False, float_format="%.2f")
