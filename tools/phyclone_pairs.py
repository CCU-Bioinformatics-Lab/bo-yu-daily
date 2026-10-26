"""Read co-occurrence topology factor (plan.md C4 / HP_EXTENSION_DESIGN.md layer B).

A read covering two SNVs on the same HP is one molecule, so its allele pattern (11, 10, 01, 00)
says whether both mutations sit in the same cells. Each SNV pair gets a log score for each tree
relation of its two nodes (plan.md §4.5.3; n00 is not modelled; Beta(1,1) over the allowed
cells' unknown split):

  same        eps^(n10+n01) (1-2eps)^n11
  ancestor    eps^n01 (1-eps)^(n11+n10) B(n11+1, n10+1)     i's node is an ancestor of j's
  descendant  eps^n10 (1-eps)^(n11+n01) B(n11+1, n01+1)
  branch      eps^n11 (1-eps)^(n10+n01) B(n10+1, n01+1)

The tree term is the sum over eligible pairs whose SNVs are both in the tree. A pair is eligible
(plan.md §4.5.1, from observed inputs only) when both SNVs have the same observed snv_hp equal
to the read HP, lie in the same segment (same PS, no CN breakpoint), and that HP has exactly one
copy in both CN states of the segment (segments.tsv a_* and b_*; phi is not used).

With an error rate e (--pair-error), error_relation_scores replaces the eps scores. Each read is
one molecule with a true genotype in {11, 10, 01, 00}; a relation allows only some genotypes
(same: 11, 00; ancestor: 11, 10, 00; descendant: 11, 01, 00; branch: 10, 01, 00). Each site is
then read as the other allele with probability e, so a forbidden pattern can only come from an
error, and n00 reads are modelled too: with many 00 reads, a few 10/01 reads are expected from
ref -> alt errors alone. Prior: pi00 ~ U(0,1) and the split of the non-00 genotypes ~ flat
Dirichlet, so a pair with no alt reads scores the same under every relation; as e -> 0 the
scores reduce to the Beta structure above. The integral is a midpoint grid.

The scores can be scaled by a composite-likelihood weight w (C4_COMPOSITE_WEIGHT_PLAN.md). A read
covering m SNVs enters m(m-1)/2 pairs, so the unweighted sum counts each read several times;
w ~ 1 / (pairs per read) brings the total evidence back to about one count per read.
"""
import numpy as np
import pandas as pd
from scipy.special import betaln

RELATIONS = ("same", "ancestor", "descendant", "branch")


def relation_scores(n11, n10, n01, eps):
    """(pairs x 4) log scores in RELATIONS order."""
    n11, n10, n01 = (np.asarray(x, float) for x in (n11, n10, n01))
    le, l1e, l2e = np.log(eps), np.log1p(-eps), np.log1p(-2 * eps)
    return np.column_stack([
        (n10 + n01) * le + n11 * l2e,
        n01 * le + (n11 + n10) * l1e + betaln(n11 + 1, n10 + 1),
        n10 * le + (n11 + n01) * l1e + betaln(n11 + 1, n01 + 1),
        n11 * le + (n10 + n01) * l1e + betaln(n10 + 1, n01 + 1),
    ])


_ALLOWED = (("11",), ("11", "10"), ("11", "01"), ("10", "01"))  # non-00 genotypes, RELATIONS order
_PATTERNS = ("11", "10", "01", "00")


def error_relation_scores(n11, n10, n01, n00, err, grid=400):
    """(pairs x 4) log marginal likelihoods in RELATIONS order under per-site error err."""
    counts = np.column_stack([np.asarray(x, float) for x in (n11, n10, n01, n00)])
    site = {("1", "1"): 1 - err, ("1", "0"): err, ("0", "1"): err, ("0", "0"): 1 - err}
    emit = {(o, g): site[o[0], g[0]] * site[o[1], g[1]] for o in _PATTERNS for g in _PATTERNS}
    pi00 = (np.arange(grid) + 0.5) / grid
    out = np.empty((len(counts), 4))
    for r, allowed in enumerate(_ALLOWED):
        if len(allowed) == 1:
            mix = {allowed[0]: 1 - pi00, "00": pi00}
        else:
            rho = (np.arange(grid // 2) + 0.5) / (grid // 2)
            a, b = np.meshgrid(pi00, rho, indexing="ij")
            a, b = a.ravel(), b.ravel()
            mix = {allowed[0]: (1 - a) * b, allowed[1]: (1 - a) * (1 - b), "00": a}
        logq = np.log(np.stack([sum(w * emit[o, g] for g, w in mix.items()) for o in _PATTERNS]))
        n = len(mix["00"])
        for start in range(0, len(counts), 256):
            ll = counts[start:start + 256] @ logq
            m = ll.max(1, keepdims=True)
            out[start:start + 256, r] = (m[:, 0] + np.log(np.exp(ll - m).sum(1))) - np.log(n)
    return out


class PairTable:
    """Eligible SNV pairs and their relation scores; `term` scores one tree assignment."""

    def __init__(self, mut_i, mut_j, scores):
        self.mut_i, self.mut_j = list(mut_i), list(mut_j)
        self.scores = np.asarray(scores, float).reshape(-1, 4)

    def __len__(self):
        return len(self.mut_i)

    @classmethod
    def from_files(cls, pairs_tsv, data_hp_tsv, segments_tsv, eps=0.01, weight=1.0, err=None):
        pairs = pd.read_csv(pairs_tsv, sep="\t")
        snv = pd.read_csv(data_hp_tsv, sep="\t").drop_duplicates("mutation_id").set_index(
            "mutation_id")
        seg = pd.read_csv(segments_tsv, sep="\t").drop_duplicates("segment_id").set_index(
            "segment_id")
        hp_i = snv.snv_hp.reindex(pairs.mutation_i).to_numpy()
        hp_j = snv.snv_hp.reindex(pairs.mutation_j).to_numpy()
        seg_i = snv.segment_id.reindex(pairs.mutation_i).to_numpy()
        seg_j = snv.segment_id.reindex(pairs.mutation_j).to_numpy()
        one_copy = np.array([
            s in seg.index and seg.at[s, f"a_{h.lower()}"] == 1 and seg.at[s, f"b_{h.lower()}"] == 1
            if h in ("HP1", "HP2") else False for s, h in zip(seg_i, pairs.hap)])
        ok = (hp_i == pairs.hap) & (hp_j == pairs.hap) & (seg_i == seg_j) & one_copy
        p = pairs[ok]
        if err is None:
            scores = relation_scores(p.n11, p.n10, p.n01, eps)
        else:
            scores = error_relation_scores(p.n11, p.n10, p.n01, p.n00, err)
        return cls(p.mutation_i, p.mutation_j, weight * scores)

    def term(self, node_of, ancestors):
        """Sum of pair scores. node_of: mutation -> node; ancestors: node -> set of ancestors."""
        total = 0.0
        for k, (a, b) in enumerate(zip(self.mut_i, self.mut_j)):
            x, y = node_of.get(a), node_of.get(b)
            if x is None or y is None:
                continue
            if x == y:
                r = 0
            elif x in ancestors[y]:
                r = 1
            elif y in ancestors[x]:
                r = 2
            else:
                r = 3
            total += self.scores[k, r]
        return total


def tree_assignment(tree):
    """(mutation -> node, node -> ancestors) for a PhyClone tree, outliers left out.

    Works on Tree and on the TreeHolderBuilder that SMC scores, which has no get_parent, so it
    reads the rustworkx graph and node index maps that both share (phyclone/tree/base.py).
    """
    import rustworkx as rx

    node_of = {dp.name: node for node, dps in tree.node_data.items()
               if node != tree.outlier_node_name for dp in dps}
    g, idx, rev, root = tree._graph, tree._node_indices, tree._node_indices_rev, tree.root_node_name
    ancestors = {n: {rev[a] for a in rx.ancestors(g, idx[n])} - {root}
                 for n in set(node_of.values())}
    return node_of, ancestors


def install(pair_table):
    """Add the pair term to TreeJointDistribution.log_p / log_p_one / both."""
    from phyclone.tree.distributions import TreeJointDistribution as T

    base_p, base_one, base_both = T.log_p, T.log_p_one, T.compute_log_p_and_log_p_one

    def extra(tree):
        return pair_table.term(*tree_assignment(tree))

    def log_p(self, tree):
        return base_p(self, tree) + extra(tree)

    def log_p_one(self, tree):
        return base_one(self, tree) + extra(tree)

    def both(self, tree):
        p, one = base_both(self, tree)
        e = extra(tree)
        return p + e, one + e

    T.log_p, T.log_p_one, T.compute_log_p_and_log_p_one = log_p, log_p_one, both
    T.c4_pair_table = pair_table


def _init_worker(pairs_tsv, data_hp_tsv, segments_tsv, eps, weight, err):
    install(PairTable.from_files(pairs_tsv, data_hp_tsv, segments_tsv, eps, weight, err))


def install_everywhere(pairs_tsv, data_hp_tsv, segments_tsv, eps=0.01, weight=1.0, err=None):
    """Install the pair term here and in every chain worker.

    phyclone/run.py runs chains in ProcessPoolExecutor(mp_context=get_context("spawn")); spawned
    workers re-import phyclone, so a patch made only in this process never reaches them. The
    pool gets an initializer that installs the term again in each worker.
    """
    import functools

    import phyclone.run

    table = PairTable.from_files(pairs_tsv, data_hp_tsv, segments_tsv, eps, weight, err)
    install(table)
    phyclone.run.ProcessPoolExecutor = functools.partial(
        phyclone.run.ProcessPoolExecutor, initializer=_init_worker,
        initargs=(pairs_tsv, data_hp_tsv, segments_tsv, eps, weight, err))
    return table
