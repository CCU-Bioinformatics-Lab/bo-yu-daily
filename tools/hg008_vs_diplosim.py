#!/usr/bin/env python3
"""Compare the rebuilt HG008 clone tree with diplosim trees that have the same number of leaves.

diplosim has no leaf-count parameter. Two scenarios, both reduced to 8 leaves with one-child chains
merged, because HG008 lines are compared to leaves:
  exactly_8_leaves   runs with n_clones in NCLONES whose tree has 8 leaves
  sample_8_of_more   runs with n_clones in SUBSAMPLE_NCLONES; 8 random leaves of a larger tree, as
                     the 8 lines are a sample of a larger population
prop_truncal_snvs is set to the HG008 value, so the truncal share is an input, not a test.

Statistics (each one a value per tree):
  colless          tree imbalance (0 = balanced)
  terminal_share   share of non-truncal SNVs on edges that end in a leaf
  internal_per_terminal  mean SNVs per internal edge / mean SNVs per terminal edge
  terminal_cv      coefficient of variation of the terminal edge lengths

Output (OUT_DIR): diplosim_trees.tsv (one row per kept run), comparison.tsv (HG008 value and its
percentile among the runs), leaf_counts.tsv (leaf-count distribution per n_clones).

Usage: python3 -I tools/hg008_vs_diplosim.py TABLE_DIR DIPLOSIM_BIN OUT_DIR [RUNS_PER_N_CLONES]
"""
import collections
import csv
import random
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

TAB = Path(sys.argv[1])
BIN = sys.argv[2]
OUT = Path(sys.argv[3])
RUNS = int(sys.argv[4]) if len(sys.argv) > 4 else 300
MAIN_SET = "vaf0.25_qual20"
STRICT_SET = "vaf0.35_qual20"
SUBSAMPLE_NCLONES = [30, 60, 120]
SEED = 20261107
CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
NCLONES = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
N_SNV = 3000
STATS = ["colless", "terminal_share", "internal_per_terminal", "terminal_cv"]


def colless_from_children(children, root):
    """Colless index of the tree under root, skipping one-child nodes."""
    total = 0

    def leaves(node):
        nonlocal total
        kids = children.get(node, [])
        if not kids:
            return 1
        counts = [leaves(k) for k in kids]
        if len(counts) == 2:
            total += abs(counts[0] - counts[1])
        return sum(counts)

    leaves(root)
    return total


def stats_from_edges(terminal, internal, colless):
    subclonal = sum(terminal) + sum(internal)
    return {
        "colless": colless,
        "terminal_share": sum(terminal) / subclonal,
        "internal_per_terminal": statistics.mean(internal) / statistics.mean(terminal) if internal else 0.0,
        "terminal_cv": statistics.pstdev(terminal) / statistics.mean(terminal),
    }


def hg008_stats(setting):
    """HG008 edge lengths use all high-quality SNVs of a pattern, so a clade keeps its CN-affected SNVs."""
    with open(TAB / f"clades_{setting}.tsv") as fh:
        clades = [frozenset(r["clade"].split(",")) for r in csv.DictReader(fh, delimiter="\t")]
    counts = {}
    with open(TAB / f"pattern_summary_{setting}.tsv") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            counts[frozenset(r["pattern"].split(","))] = int(r["n_snv"])
    nodes = sorted(clades + [frozenset(CLONES)], key=len)
    children = collections.defaultdict(list)
    for clone in CLONES:
        parent = next(n for n in nodes if clone in n)
        children[parent].append(frozenset([clone]))
    for clade in clades:
        parent = next(n for n in nodes if clade < n)
        children[parent].append(clade)
    terminal = [counts.get(frozenset([c]), 0) for c in CLONES]
    internal = [counts.get(c, 0) for c in clades]
    return stats_from_edges(terminal, internal, colless_from_children(children, frozenset(CLONES))), counts


def run_tree(n_clones, seed, prop_truncal):
    with tempfile.TemporaryDirectory() as tmp:
        done = subprocess.run([BIN, "--n-clones", str(n_clones), "--n-snv", str(N_SNV),
                               "--prop-truncal-snvs", f"{prop_truncal:.4f}", "--seed", str(seed), "--out", tmp, "--name", "x"],
                              capture_output=True, text=True)
        if "duplicate CHR/POS" in done.stderr:  # CONIPHER rejects these seeds too
            return None
        done.check_returncode()
        with open(Path(tmp) / "x_treeedges.tsv") as fh:
            return list(csv.DictReader(fh, delimiter="\t"))


def sampled_tree(edges, keep):
    """Reduce a diplosim tree to the leaves in `keep`: drop other branches, merge one-child chains.

    SNVs above the kept leaves' common ancestor count as truncal, as they would in HG008.
    Returns terminal edge lengths, internal edge lengths and the Colless index.
    """
    children = collections.defaultdict(list)
    snvs = {}
    for e in edges:
        children[e["Parent"]].append(e["Child"])
        snvs[e["Child"]] = int(e["SNVs"])
    kids = set(snvs)
    root = next(e["Parent"] for e in edges if e["Parent"] not in kids)
    has_kept = {}

    def mark(node):
        has_kept[node] = node in keep or any([mark(k) for k in children.get(node, [])])
        return has_kept[node]

    mark(root)
    terminal, internal = [], []
    colless = [0]

    def walk(node, length, top):
        """Returns the kept leaves under node. `length` is the merged edge above node."""
        below = [k for k in children.get(node, []) if has_kept[k]]
        if not below:
            terminal.append(length)
            return 1
        if len(below) == 1:
            return walk(below[0], length + snvs[below[0]], top)
        if not top:
            internal.append(length)
        counts = [walk(k, snvs[k], False) for k in below]
        colless[0] += abs(counts[0] - counts[1]) if len(counts) == 2 else 0
        return sum(counts)

    walk(root, 0, True)
    return terminal, internal, colless[0]


def leaves_of(edges):
    parents = {e["Parent"] for e in edges}
    return [e["Child"] for e in edges if e["Child"] not in parents]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hg, counts = hg008_stats(MAIN_SET)
    hg_strict, _ = hg008_stats(STRICT_SET)
    prop_truncal = counts[frozenset(CLONES)] / sum(counts.values())
    kept = []
    leaf_counts = collections.Counter()
    n_rejected = 0
    rng = random.Random(SEED)
    for n_clones in NCLONES + SUBSAMPLE_NCLONES:
        for seed in range(RUNS):
            edges = run_tree(n_clones, seed, prop_truncal)
            if edges is None:
                n_rejected += 1
                continue
            leaves = leaves_of(edges)
            leaf_counts[(n_clones, len(leaves))] += 1
            if n_clones in NCLONES and len(leaves) == 8:
                scenario = "exactly_8_leaves"
            elif n_clones in SUBSAMPLE_NCLONES and len(leaves) > 8:
                scenario = "sample_8_of_more"
            else:
                continue
            terminal, internal, colless = sampled_tree(edges, set(rng.sample(leaves, 8)))
            kept.append({"scenario": scenario, "n_clones": n_clones, "seed": seed, "n_leaves": len(leaves),
                         "n_internal_edges": len(internal), **stats_from_edges(terminal, internal, colless)})
    with open(OUT / "leaf_counts.tsv", "w") as fh:
        fh.write("n_clones\tn_leaves\tn_runs\n")
        for (n_clones, n_leaf), n in sorted(leaf_counts.items()):
            fh.write(f"{n_clones}\t{n_leaf}\t{n}\n")
    with open(OUT / "diplosim_trees.tsv", "w") as fh:
        fields = ["scenario", "n_clones", "seed", "n_leaves", "n_internal_edges"] + STATS
        fh.write("\t".join(fields) + "\n")
        for row in kept:
            fh.write("\t".join(f"{row[f]:.4f}" if isinstance(row[f], float) else str(row[f]) for f in fields) + "\n")
    with open(OUT / "comparison.tsv", "w") as fh:
        fh.write("scenario\tstatistic\thg008\thg008_vaf0.35\tdiplosim_p2.5\tdiplosim_median\tdiplosim_p97.5\t"
                 "hg008_percentile\tn_runs\n")
        for scenario in sorted({r["scenario"] for r in kept}):
            rows = [r for r in kept if r["scenario"] == scenario]
            for stat in STATS:
                values = sorted(r[stat] for r in rows)
                low, mid, high = (values[int(q * (len(values) - 1))] for q in (0.025, 0.5, 0.975))
                pct = 100 * sum(v <= hg[stat] for v in values) / len(values)
                fh.write(f"{scenario}\t{stat}\t{hg[stat]:.3f}\t{hg_strict[stat]:.3f}\t{low:.3f}\t{mid:.3f}\t{high:.3f}\t"
                         f"{pct:.1f}\t{len(values)}\n")
    print(f"prop_truncal {prop_truncal:.3f}; kept {len(kept)} trees; {n_rejected} seeds rejected for duplicate positions")


if __name__ == "__main__":
    main()
