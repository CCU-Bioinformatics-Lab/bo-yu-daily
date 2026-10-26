"""Run: env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python -m unittest tools/test_phyclone_pairs.py"""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phyclone_pairs import (RELATIONS, PairTable, error_relation_scores, relation_scores,  # noqa: E402
                            tree_assignment)
from scipy.special import betaln  # noqa: E402


class RelationScores(unittest.TestCase):
    def best(self, n11, n10, n01):
        return RELATIONS[int(np.argmax(relation_scores([n11], [n10], [n01], 0.01)[0]))]

    def test_each_pattern_picks_its_relation(self):
        self.assertEqual(self.best(20, 0, 0), "same")
        self.assertEqual(self.best(10, 10, 0), "ancestor")
        self.assertEqual(self.best(10, 0, 10), "descendant")
        self.assertEqual(self.best(0, 10, 10), "branch")

    def test_no_informative_reads_scores_zero_for_all(self):
        self.assertTrue(np.allclose(relation_scores([0], [0], [0], 0.01), 0))


class ErrorModelScores(unittest.TestCase):
    def best(self, n11, n10, n01, n00, err=0.004):
        return RELATIONS[int(np.argmax(error_relation_scores([n11], [n10], [n01], [n00], err)[0]))]

    def test_each_pattern_picks_its_relation(self):
        self.assertEqual(self.best(20, 0, 0, 50), "same")
        self.assertEqual(self.best(10, 10, 0, 50), "ancestor")
        self.assertEqual(self.best(10, 0, 10, 50), "descendant")
        self.assertEqual(self.best(0, 10, 10, 50), "branch")

    def test_no_alt_reads_score_the_same_under_every_relation(self):
        s = error_relation_scores([0], [0], [0], [80], 0.004)[0]
        self.assertTrue(np.allclose(s, s[0], atol=0.01))  # e > 0: a 10 molecule can read as 00

    def test_singletons_expected_from_ref_reads_do_not_split_a_clone(self):
        """Failure mode 1: 3% base error on many 00 reads gives a few 10/01 reads in one clone."""
        old = relation_scores([20], [3], [3], 0.01)[0]
        self.assertNotEqual(RELATIONS[int(np.argmax(old))], "same")
        self.assertEqual(self.best(20, 3, 3, 100, err=0.03), "same")

    def test_branch_evidence_survives_the_error_model(self):
        s = error_relation_scores([0], [10], [10], [100], 0.004)[0]
        self.assertGreater(s[3] - max(s[:3]), 20)

    def test_branch_evidence_weakens_when_errors_explain_the_singletons(self):
        """100 00 reads at 3% error already expect ~3 false 01 reads, so 10 is weak evidence."""
        low, high = (error_relation_scores([0], [10], [10], [100], e)[0] for e in (0.004, 0.03))
        self.assertLess(high[3] - max(high[:3]), low[3] - max(low[:3]))

    def test_small_error_reduces_to_the_beta_structure(self):
        n11, n10, n00 = 5, 4, 30
        s = error_relation_scores([n11], [n10], [0], [n00], 1e-9)[0]
        want = betaln(n00 + 1, n11 + n10 + 1) + betaln(n11 + 1, n10 + 1)
        self.assertAlmostEqual(s[1], want, places=2)

    def test_from_files_uses_the_error_model_and_weight(self):
        files = _write_inputs()
        t = PairTable.from_files(*files, weight=0.5, err=0.004)
        np.testing.assert_allclose(t.scores, 0.5 * error_relation_scores([3], [2], [0], [1], 0.004))


class TreeTerm(unittest.TestCase):
    def test_term_uses_the_tree_relation(self):
        s = relation_scores([5, 0], [5, 6], [0, 7], 0.01)
        table = PairTable(["a", "c"], ["b", "d"], s)
        anc = {"r": set(), "x": {"r"}, "y": {"r"}}
        got = table.term({"a": "r", "b": "x", "c": "x", "d": "y"}, anc)
        self.assertAlmostEqual(got, s[0, 1] + s[1, 3])

    def test_pairs_with_a_missing_snv_are_skipped(self):
        table = PairTable(["a"], ["b"], relation_scores([3], [0], [0], 0.01))
        self.assertEqual(table.term({"a": "r"}, {"r": set()}), 0.0)


def _write_inputs(n11=3):
    import tempfile

    d = tempfile.mkdtemp()
    for name, text in {
        "pairs.tsv": "mutation_i\tmutation_j\tsample_id\tchrom\tps_block\thap\tn11\tn10\tn01"
                     f"\tn00\tcallable_pair_reads\tdistance\na\tb\tS1\tchr1\tA\tHP1\t{n11}\t2\t0\t1\t4\t10\n",
        "data_hp.tsv": "mutation_id\tsnv_hp\tsegment_id\na\tHP1\tA\nb\tHP1\tA\n",
        "segments.tsv": "segment_id\ta_hp1\ta_hp2\tb_hp1\tb_hp2\nA\t1\t1\t1\t1\n",
    }.items():
        with open(os.path.join(d, name), "w") as fh:
            fh.write(text)
    return [os.path.join(d, f) for f in ("pairs.tsv", "data_hp.tsv", "segments.tsv")]


class CompositeWeight(unittest.TestCase):
    def test_weight_one_matches_unweighted_scores(self):
        files = _write_inputs()
        default = PairTable.from_files(*files, eps=0.01)
        one = PairTable.from_files(*files, eps=0.01, weight=1.0)
        np.testing.assert_array_equal(default.scores, one.scores)
        np.testing.assert_array_equal(default.scores, relation_scores([3], [2], [0], 0.01))

    def test_term_scales_linearly_with_weight(self):
        files = _write_inputs()
        anc = {"r": set(), "x": {"r"}}
        trees = [{"a": "r", "b": "r"}, {"a": "r", "b": "x"}, {"a": "x", "b": "r"}]
        full = PairTable.from_files(*files, eps=0.01)
        part = PairTable.from_files(*files, eps=0.01, weight=0.3)
        for node_of in trees:
            self.assertAlmostEqual(part.term(node_of, anc), 0.3 * full.term(node_of, anc))


class OnPhyCloneTree(unittest.TestCase):
    def test_assignment_from_a_real_tree(self):
        from phyclone.data.base import DataPoint
        from phyclone.tree import Tree

        dp = [DataPoint(i, np.zeros((1, 11)), name=n) for i, n in enumerate("abc")]
        tree = Tree((1, 11))
        child = tree.create_root_node(data=[dp[2]])
        top = tree.create_root_node(children=[child], data=[dp[0], dp[1]])
        node_of, anc = tree_assignment(tree)
        self.assertEqual(node_of["a"], top)
        self.assertEqual(anc[node_of["c"]], {top})
        self.assertEqual(anc[top], set())


def _worker_has_pair_term():
    from phyclone.tree.distributions import TreeJointDistribution
    return TreeJointDistribution.log_p.__qualname__


def _worker_pair_scores():
    from phyclone.tree.distributions import TreeJointDistribution
    return TreeJointDistribution.c4_pair_table.scores


class SpawnedChainWorkers(unittest.TestCase):
    def spawn(self, fn, weight, err=None):
        from multiprocessing import get_context

        import phyclone.run
        from phyclone_pairs import install_everywhere

        original = phyclone.run.ProcessPoolExecutor
        try:
            table = install_everywhere(*_write_inputs(), weight=weight, err=err)
            self.assertEqual(len(table), 1)
            with phyclone.run.ProcessPoolExecutor(max_workers=1,
                                                  mp_context=get_context("spawn")) as pool:
                return table, pool.submit(fn).result()
        finally:
            phyclone.run.ProcessPoolExecutor = original

    def test_pair_term_reaches_spawned_workers(self):
        """PhyClone runs chains in spawned processes; the term must be installed there too."""
        _, name = self.spawn(_worker_has_pair_term, 1.0)
        self.assertIn("install.<locals>", name)

    def test_spawned_workers_use_the_weight(self):
        """Without the weight in initargs, workers would rebuild the table with w = 1."""
        table, scores = self.spawn(_worker_pair_scores, 0.3)
        np.testing.assert_allclose(scores, table.scores)
        np.testing.assert_allclose(scores, 0.3 * relation_scores([3], [2], [0], 0.01))

    def test_spawned_workers_use_the_error_model(self):
        table, scores = self.spawn(_worker_pair_scores, 1.0, err=0.004)
        np.testing.assert_allclose(scores, table.scores)
        np.testing.assert_allclose(scores, error_relation_scores([3], [2], [0], [1], 0.004))


if __name__ == "__main__":
    unittest.main()
