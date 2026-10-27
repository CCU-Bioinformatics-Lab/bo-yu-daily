"""--user-provided-loss-prob: a mutation whose rows in the cluster file carry two different
outlier_prob values is counted twice (its likelihood grid is added twice and the cluster size
grows by one), and the cluster takes the first row's value.

Usage (from the repo root): env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \\
  phyclone_rs/golden/probes/cluster_outlier_prob_rows.py
"""
import contextlib
import io
import os
import tempfile

import numpy as np
import pandas as pd
from phyclone.data.pyclone import load_data

D = "phyclone_rs/golden/cases/fscrp_loss_0.2_run0/input/"


def load(cluster_file):
    with contextlib.redirect_stdout(io.StringIO()):
        data = load_data(D + "data.tsv", np.random.default_rng(1), 0.4, False, True,
                         cluster_file=cluster_file, outlier_prob=1e-4)[0]
    return {str(x.name): x for x in data}


c = pd.read_csv(D + "results_user_loss.tsv", sep="\t")
m = c.mutation_id[c.cluster_id == 8].iloc[0]  # cluster 8 holds one mutation
c.loc[(c.mutation_id == m) & (c.sample_id == "s0"), "outlier_prob"] = 0.5
with tempfile.TemporaryDirectory() as tmp:
    edited = os.path.join(tmp, "clusters.tsv")
    c.to_csv(edited, sep="\t", index=False)
    a, b = load(D + "results_user_loss.tsv"), load(edited)
print("cluster 8 outlier_prob", a["8"].outlier_prob, "->", b["8"].outlier_prob,
      "(log 0.5 x 2 =", 2 * np.log(0.5), "); likelihood doubled:", np.allclose(b["8"].value, 2 * a["8"].value))
