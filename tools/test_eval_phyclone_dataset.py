"""Unit tests for eval_phyclone_dataset.py. Run: python3 -m unittest tools/test_eval_phyclone_dataset.py"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eval_phyclone_dataset as ev  # noqa: E402


def write(d, name, text):
    with open(os.path.join(d, name), "w") as fh:
        fh.write(text)


def node_link(nodes, edges):
    return json.dumps({"directed": True, "multigraph": False, "graph": {},
                       "nodes": [{"id": i, "snvs": s} for i, s in nodes],
                       "edges": [{"parent": p, "child": c} for p, c in edges]})


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        # truth: 0 -> 1 -> 2, lost SNV m5 in node -1
        write(self.dir, "truth.json", node_link(
            [(0, ["m0", "m1"]), (1, ["m2"]), (2, ["m3", "m4"]), (-1, ["m5"])], [(0, 1), (1, 2)]))
        self.truth = ev.tree_from_json(os.path.join(self.dir, "truth.json"))

    def test_perfect_prediction_with_outlier(self):
        rows = ["mutation_id\tclone_id\tsample_id"] + [
            f"{m}\t{c}\ts0" for m, c in [("m0", 5), ("m1", 5), ("m2", 6), ("m3", 7), ("m4", 7), ("m5", -1)]]
        write(self.dir, "map_table.tsv", "\n".join(rows) + "\n")
        write(self.dir, "map_tree.nwk", "(((7)6)5)root;")
        s = ev.score(self.truth, ev.read_prediction(self.dir))
        self.assertEqual(s["num_mutations_pred"], 5)
        self.assertEqual(s["num_mutations_true"], 6)
        self.assertAlmostEqual(s["v_measure"], 1.0)
        self.assertAlmostEqual(s["ancestor_descendant_f_score"], 1.0)

    def test_forest_gives_no_cross_root_pairs(self):
        # truth pairs: 0>1 (2), 0>2 (4), 1>2 (2) = 8; prediction puts node 2 under its own root
        write(self.dir, "pred.json", node_link(
            [(0, ["m0", "m1"]), (1, ["m2"]), (2, ["m3", "m4", "m5"])], [(0, 1)]))
        s = ev.score(self.truth, ev.tree_from_json(os.path.join(self.dir, "pred.json")))
        self.assertAlmostEqual(s["ad_precision"], 1.0)
        self.assertAlmostEqual(s["ad_recall"], 2 / 8)
        self.assertEqual(s["num_mutations_pred"], 6)

    def test_same_node_is_not_a_pair(self):
        write(self.dir, "pred.json", node_link([(0, ["m0", "m1", "m2", "m3", "m4"])], []))
        s = ev.score(self.truth, ev.tree_from_json(os.path.join(self.dir, "pred.json")))
        self.assertEqual(s["ancestor_descendant_f_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
