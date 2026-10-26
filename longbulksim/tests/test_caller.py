"""Somatic caller sensitivity (v0.5): missed SNVs leave every input file."""
import unittest

import numpy as np

from longbulksim.simulate import detect, load_caller
from test_errors import flat
from test_simulate import read_tsv, simulate


def low_purity(caller, n_snv=300):
    raw = flat(n_snv=n_snv, length=10_000_000, depth=50)
    raw.update(purity=0.25, caller=caller)
    return raw


class Curve(unittest.TestCase):
    def test_shape(self):
        rng = np.random.default_rng(0)
        coef = load_caller("clairs")
        n = 20_000
        rate = lambda a, d: detect(rng, coef, [a] * n, [d] * n).mean()
        self.assertEqual(rate(0, 50), 0)
        self.assertLess(rate(3, 80), 0.01)
        self.assertGreater(rate(30, 80), 0.97)
        self.assertLess(rate(10, 150), rate(10, 50))  # same alt, higher depth = lower VAF

    def test_deepsomatic_more_sensitive(self):
        rng = np.random.default_rng(0)
        a = detect(rng, load_caller("clairs"), [6] * 20_000, [60] * 20_000).mean()
        b = detect(rng, load_caller("deepsomatic"), [6] * 20_000, [60] * 20_000).mean()
        self.assertLess(a, b)

    def test_unknown_caller(self):
        with self.assertRaises(ValueError):
            load_caller("mutect2")


class Simulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.out = simulate(low_purity("clairs"))
        cls.truth = read_tsv(cls.out / "truth/truth.tsv")

    def test_missed_snvs_leave_inputs(self):
        called = {r["mutation_id"] for r in self.truth if r["detected"] == "1"}
        self.assertGreater(len(called), 0)
        self.assertLess(len(called), len(self.truth))  # purity 0.25 at 50x: some are missed
        for f in ("data.tsv", "data_hp.tsv"):
            self.assertEqual({r["mutation_id"] for r in read_tsv(self.out / "input" / f)}, called, f)
        for r in read_tsv(self.out / "input/pairs.tsv"):
            self.assertIn(r["mutation_i"], called)
            self.assertIn(r["mutation_j"], called)

    def test_rate_matches_curve(self):
        # recount alt/depth of every SNV with caller none and the same seed (same reads)
        _, out0 = simulate(low_purity("none"))
        data = {r["mutation_id"]: r for r in read_tsv(out0 / "input/data.tsv")}
        coef = load_caller("clairs")
        p = []
        for r in self.truth:
            a = int(data[r["mutation_id"]]["alt_counts"])
            d = a + int(data[r["mutation_id"]]["ref_counts"])
            z = coef[0] + coef[1] * np.log(a) + coef[2] * np.log(d) if a else -np.inf
            p.append(1 / (1 + np.exp(-z)))
        got = sum(r["detected"] == "1" for r in self.truth)
        se = np.sqrt(sum(x * (1 - x) for x in p))
        self.assertLess(abs(got - sum(p)), 4 * se + 1)

    def test_none_keeps_all(self):
        _, out = simulate(low_purity("none", n_snv=50))
        truth = read_tsv(out / "truth/truth.tsv")
        self.assertTrue(all(r["detected"] == "1" for r in truth))
        self.assertEqual(len(read_tsv(out / "input/data.tsv")), len(truth))


if __name__ == "__main__":
    unittest.main()
