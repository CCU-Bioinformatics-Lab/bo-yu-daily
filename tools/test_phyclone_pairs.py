"""Run: env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python -m unittest tools/test_phyclone_pairs.py"""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phyclone_pairs import RELATIONS, PairTable, relation_scores, tree_assignment  # noqa: E402


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


class SpawnedChainWorkers(unittest.TestCase):
    def test_pair_term_reaches_spawned_workers(self):
        """PhyClone runs chains in spawned processes; the term must be installed there too."""
        import tempfile
        from multiprocessing import get_context

        import phyclone.run
        from phyclone_pairs import install_everywhere

        d = tempfile.mkdtemp()
        for name, text in {
            "pairs.tsv": "mutation_i\tmutation_j\tsample_id\tchrom\tps_block\thap\tn11\tn10\tn01"
                         "\tn00\tcallable_pair_reads\tdistance\na\tb\tS1\tchr1\tA\tHP1\t3\t0\t0\t1\t4\t10\n",
            "data_hp.tsv": "mutation_id\tsnv_hp\tsegment_id\na\tHP1\tA\nb\tHP1\tA\n",
            "segments.tsv": "segment_id\ta_hp1\ta_hp2\tb_hp1\tb_hp2\nA\t1\t1\t1\t1\n",
        }.items():
            with open(os.path.join(d, name), "w") as fh:
                fh.write(text)
        original = phyclone.run.ProcessPoolExecutor
        try:
            table = install_everywhere(*(os.path.join(d, f) for f in
                                         ("pairs.tsv", "data_hp.tsv", "segments.tsv")))
            self.assertEqual(len(table), 1)
            with phyclone.run.ProcessPoolExecutor(max_workers=1,
                                                  mp_context=get_context("spawn")) as pool:
                name = pool.submit(_worker_has_pair_term).result()
            self.assertIn("install.<locals>", name)
        finally:
            phyclone.run.ProcessPoolExecutor = original


if __name__ == "__main__":
    unittest.main()
