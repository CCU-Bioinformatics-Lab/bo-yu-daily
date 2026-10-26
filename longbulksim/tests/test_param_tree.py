"""Parametric tree specs (param_tree.py) and the generate CLI."""
import collections
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from longbulksim.model import HPS, load_spec, parse_spec, replay
from longbulksim.param_tree import Params, categorize, draw_spec, load_pools

POOLS = load_pools()
ROOT = Path(__file__).resolve().parent.parent


def specs(p, n, seed=0):
    rng = np.random.default_rng(seed)
    return [draw_spec(rng, POOLS, p) for _ in range(n)]


def n_children(raw):
    return collections.Counter(v["parent"] for v in raw["clones"].values() if v["parent"])


class Tree(unittest.TestCase):
    def test_clone_count_and_shape(self):
        for shape, linear in (("linear", True), ("branched", False)):
            for raw in specs(Params(n_clones=5, tree_shape=shape), 30):
                self.assertEqual(len(raw["clones"]), 5)
                self.assertEqual(max(n_children(raw).values()) == 1, linear, shape)

    def test_random_shape_rate(self):
        lin = [max(n_children(r).values()) == 1 for r in specs(Params(n_snv=40, n_segments=10), 400)]
        self.assertLess(abs(np.mean(lin) - 0.63), 4 * np.sqrt(0.63 * 0.37 / 400))

    def test_ccf_rules(self):
        p = Params(n_clones=4, min_ccf=0.1, min_gap=0.08)
        for raw in specs(p, 50):
            ccf = raw["source"]["ccf"]
            self.assertAlmostEqual(sum(v["fraction"] for v in raw["clones"].values()), 1, 6)
            for c, v in raw["clones"].items():
                if v["parent"]:
                    self.assertGreaterEqual(ccf[c], 0.1 - 1e-4)
                    self.assertGreaterEqual(ccf[v["parent"]] - ccf[c], 0.08 - 1e-4)

    def test_one_clone(self):
        raw = specs(Params(n_clones=1, n_snv=50), 1)[0]
        self.assertEqual(list(raw["clones"]), ["C1"])


class Mutations(unittest.TestCase):
    def test_prop_truncal(self):
        for raw in specs(Params(prop_truncal=0.6, n_snv=200), 20):
            sp = parse_spec(raw)
            got = np.mean([r.clone == "C1" for r in sp.roles.values()])
            self.assertLess(abs(got - 0.6), 0.05)

    def test_cn_shares(self):
        # gain is never removed by SNV drops, so its SNV-weighted share matches the setting
        p = Params(wgd=False, prop_gain=0.3, prop_loh=0.1, n_snv=200)
        gain, loss = [], []
        for raw in specs(p, 200):
            sp = parse_spec(raw)
            g = replay(sp)
            cat = [categorize(*(len(g["C1"][r.segment][h]) for h in HPS), 1) for r in sp.roles.values()]
            gain.append(np.mean([c == "gain" for c in cat]))
            loss.append(np.mean([c == "loss" for c in cat]))
        self.assertLess(abs(np.mean(gain) - 0.3), 0.03)
        self.assertEqual(max(loss), 0)  # without WGD every loss below 1 copy is LOH

    def test_shares_over_one(self):
        with self.assertRaises(ValueError):
            specs(Params(prop_gain=0.5, prop_loss=0.4, prop_loh=0.3), 1)

    def test_specs_replay(self):
        for raw in specs(replace(Params(), n_clones=4), 30):
            replay(parse_spec(raw))


class GenerateCLI(unittest.TestCase):
    def test_end_to_end(self):
        out = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, "-m", "longbulksim.generate", str(out), "--n-sims", "2",
                        "--n-snv", "60", "--n-segments", "20", "--n-clones", "4",
                        "--purity", "0.3", "--depth", "20"],
                       cwd=ROOT, check=True, capture_output=True)
        for i in range(2):
            d = out / f"sim_{i:04d}"
            for f in ("input/data.tsv", "input/data_hp.tsv", "input/pairs.tsv",
                      "truth/truth_tree.tsv", "truth/spec.yaml"):
                self.assertTrue((d / f).exists(), f)
            m = json.loads((d / "manifest.json").read_text())
            self.assertEqual(m["params"]["n_clones"], 4)
            self.assertEqual(m["purity"], 0.3)
            self.assertEqual(len(load_spec(d / "truth/spec.yaml").parent), 4)


if __name__ == "__main__":
    unittest.main()
