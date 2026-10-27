import csv
import json
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

V3 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, V3)
import compare as C  # noqa: E402
import summaries as S  # noqa: E402
import trace_io as T  # noqa: E402

FIXTURE = os.path.join(V3, "tests", "fixture_trace")
GOLDEN_RUNS = os.path.join(S.GOLDEN, "runs")


class TsvReader(unittest.TestCase):
    def test_fixture_reads_into_the_common_form(self):
        tr = T.read_trace(FIXTURE)
        self.assertEqual(tr.mutations, ["m1", "m2", "m3", "m4"])
        self.assertEqual(len(tr), 3, "burn-in row dropped")
        self.assertEqual(tr.log_p_one.tolist(), [-10.25, -9.75, -12.5], "renamed column via meta.json")
        self.assertEqual(tr.chain.tolist(), [0, 0, 1])
        t7 = tr.trees[tr.tree_idx[0]]
        self.assertEqual(t7, T.Tree((0, 1, 2, T.OUTLIER), (T.ROOT, 0, T.ROOT)))
        self.assertEqual(tr.trees[tr.tree_idx[2]], T.Tree((0, 0, 0, 0), (T.ROOT,)))

    def test_fixture_summaries(self):
        d = S.run_summaries(T.read_trace(FIXTURE))
        np.testing.assert_allclose(d["coclust"], np.full(6, 1 / 3), atol=1e-6)
        expect_anc = np.zeros(12)
        expect_anc[0] = 2 / 3  # m1 (node 0) is the parent of m2 in the 3-node tree
        np.testing.assert_allclose(d["ancestor"], expect_anc, atol=1e-6)
        self.assertAlmostEqual(d["num_nodes"][3], 2 / 3, places=6)
        self.assertAlmostEqual(d["num_roots"][1], 1 / 3, places=6)
        self.assertEqual(d["map_log_p_one"][0], -9.75)
        self.assertEqual(d["step_change"][0], 0.0, "only a repeated tree; chain 1 has one sample")

    def test_cluster_ids_expand_to_mutations(self):
        tmp = tempfile.mkdtemp()
        try:
            for f in os.listdir(FIXTURE):
                shutil.copy(os.path.join(FIXTURE, f), tmp)
            with open(os.path.join(tmp, "assignments.tsv")) as fh:
                text = fh.read()
            for m, c in (("m1", "c1"), ("m2", "c2"), ("m3", "c3"), ("m4", "c4")):
                text = text.replace(m, c)
            with open(os.path.join(tmp, "assignments.tsv"), "w") as fh:
                fh.write(text)
            with open(os.path.join(tmp, "clusters.tsv"), "w") as fh:
                fh.write("cluster_id\tmutation_id\nc1\tm1\nc1\tm1b\nc2\tm2\nc3\tm3\nc4\tm4\n")
            tr = T.read_trace(tmp)
            self.assertEqual(tr.mutations, ["m1", "m1b", "m2", "m3", "m4"])
            self.assertEqual(tr.trees[tr.tree_idx[0]].node_of, (0, 0, 1, 2, T.OUTLIER))
        finally:
            shutil.rmtree(tmp)

    def test_missing_column_is_an_error(self):
        tmp = tempfile.mkdtemp()
        try:
            for f in os.listdir(FIXTURE):
                shutil.copy(os.path.join(FIXTURE, f), tmp)
            with open(os.path.join(tmp, "meta.json"), "w") as fh:
                json.dump({"format_version": 1, "outlier_node": 99}, fh)
            with self.assertRaises(ValueError):
                T.read_trace(tmp)
        finally:
            shutil.rmtree(tmp)


@unittest.skipUnless(os.path.isdir(GOLDEN_RUNS), "golden runs not present")
class H5Reader(unittest.TestCase):
    def test_counts_match_the_stored_columns(self):
        for run in ("e0_base_bin", "upstream_clusters"):
            tr = T.read_trace(os.path.join(GOLDEN_RUNS, run, "trace.h5"))
            nodes = [tr.trees[i].num_nodes for i in tr.tree_idx]
            roots = [sum(p == T.ROOT for p in tr.trees[i].parent) for i in tr.tree_idx]
            self.assertEqual(tr.num_nodes.tolist(), nodes, run)
            self.assertEqual(tr.num_roots.tolist(), roots, run)

    def test_map_tree_matches_the_golden_fixture(self):
        with open(os.path.join(S.GOLDEN, "runs.tsv")) as fh:
            argv = {r["run"]: r["argv"] for r in csv.DictReader(fh, delimiter="\t")}
        compared = 0
        for run, case in S.config_case().items():
            if " -c " in argv[run]:
                continue  # fixture lists cluster ids; the common form is per mutation
            trees = []
            for name in (case, f"{case}__m7"):  # M7 runs keep their trees in <case>__m7.json
                path = os.path.join(S.GOLDEN, "fixtures", "trees", f"{name}.json")
                if os.path.exists(path):
                    with open(path) as fh:
                        trees += json.load(fh)["trees"]
            spec = next((t["nodes"] for t in trees
                         if f"{run}:map" in [t["id"], *t.get("aliases", [])]), None)
            if spec is None:
                continue  # option-only M7 runs (thin, max-time, ...) have no frozen trees
            compared += 1
            tr = T.read_trace(os.path.join(GOLDEN_RUNS, run, "trace.h5"))
            node_of = {m: n for n, v in spec.items() for m in v["mutations"]}
            parent = {n: (T.ROOT if v["parent"] in (None, "root", "-1") else v["parent"])
                      for n, v in spec.items()}
            want = T.canonical_tree([node_of.get(m, T.OUTLIER) for m in tr.mutations], parent)
            got = tr.trees[tr.tree_idx[int(np.argmax(tr.log_p_one))]]
            self.assertEqual(got, want, run)
        self.assertEqual(compared, 10)  # 6 original SNV-level runs + 4 M7 outlier runs

    def test_h5_and_tsv_give_the_same_summaries(self):
        tmp = tempfile.mkdtemp()
        try:
            src = T.read_trace(os.path.join(GOLDEN_RUNS, "real_a2_err004", "trace.h5"))
            T.write_tsv_dir(src, tmp)
            a = S.run_summaries(src, S.truth_for("real_a2_err004"))
            b = S.run_summaries(T.read_trace(tmp), S.truth_for("real_a2_err004"))
            self.assertEqual(sorted(a), sorted(b))
            for k in a:
                np.testing.assert_array_equal(a[k], b[k], k)
        finally:
            shutil.rmtree(tmp)


class PermutationRule(unittest.TestCase):
    def runs(self, values):
        return [{"map_log_p_one": np.array([v])} for v in values]

    def test_same_distribution_passes(self):
        rng = np.random.default_rng(3)
        r = C.compare_one(self.runs(rng.normal(size=15)), self.runs(rng.normal(size=10)), "map_log_p_one")
        self.assertEqual(r["verdict"], "PASS")

    def test_shift_fails(self):
        rng = np.random.default_rng(3)
        r = C.compare_one(self.runs(rng.normal(size=15)), self.runs(rng.normal(size=10) + 5),
                          "map_log_p_one")
        self.assertEqual(r["verdict"], "FAIL")

    def test_too_few_seeds_cannot_fail(self):
        r = C.compare_one(self.runs(range(5)), self.runs([100, 101]), "map_log_p_one")
        self.assertEqual(r["verdict"], "INCONCLUSIVE")

    def test_exact_p_counts_the_observed_split(self):
        r = C.compare_one(self.runs([0.0] * 10), self.runs([0.0] * 5), "map_log_p_one")
        self.assertEqual((r["p"], r["verdict"]), (1.0, "PASS"))


if __name__ == "__main__":
    unittest.main()
