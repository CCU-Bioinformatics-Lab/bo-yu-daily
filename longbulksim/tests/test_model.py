import importlib
import sys
import unittest
from collections import Counter
from pathlib import Path

from longbulksim.model import load_spec, lost, parse_spec, replay

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
sys.path.insert(0, str(ROOT.parent / "tools"))


def hand_tree(name):
    """GENOME/LOST of the hand-written trees in tools/, as replay() would return them."""
    T = importlib.reload(importlib.import_module("draw_hp_truth_tree"))
    if name == "typical":
        importlib.import_module("typical_truth_tree").install(T)
    genome = {c: {s: {h: Counter(map(frozenset, cps)) for h, cps in seg.items()}
                  for s, seg in g.items()} for c, g in T.GENOME.items()}
    lost_roles = {c: sorted(r for _, _, r in v) for c, v in T.LOST.items()}
    return genome, lost_roles


class ReplayMatchesHandTrees(unittest.TestCase):
    def check(self, name):
        spec = load_spec(SPECS / f"{name}.yaml")
        genomes = replay(spec)
        want, want_lost = hand_tree(name)
        got = {c: {s: {h: Counter(cps) for h, cps in seg.items()} for s, seg in g.items()}
               for c, g in genomes.items()}
        self.assertEqual(got, want)
        self.assertEqual(lost(spec, genomes), want_lost)

    def test_stress(self):
        self.check("stress")

    def test_typical(self):
        self.check("typical")


class SpecValidation(unittest.TestCase):
    BASE = {"name": "x", "purity": 0.5, "depth": 50,
            "clones": {"C1": {"parent": None, "fraction": 1.0}},
            "segments": {"A": {"chrom": "chr1", "start": 0, "length": 1000}}}

    def spec(self, **edges):
        return parse_spec({**self.BASE, "edges": edges})

    def test_snv_on_deleted_hp_is_rejected(self):
        spec = self.spec(C1=[{"loss": "A", "hp": "HP2"},
                             {"snv": "s1", "hp": "HP2", "segment": "A"}])
        with self.assertRaisesRegex(ValueError, "has 0 copies"):
            replay(spec)

    def test_unknown_segment_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown segment"):
            self.spec(C1=[{"snv": "s1", "hp": "HP1", "segment": "Z"}])

    def test_fractions_must_sum_to_one(self):
        with self.assertRaisesRegex(ValueError, "sum to"):
            parse_spec({**self.BASE, "clones": {"C1": {"parent": None, "fraction": 0.7}}})


if __name__ == "__main__":
    unittest.main()
