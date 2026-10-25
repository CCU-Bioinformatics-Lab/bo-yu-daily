import unittest

import numpy as np

from longbulksim.model import lost, parse_spec, replay, roles_in
from longbulksim.random_tree import draw_spec, load_blueprints, project_ccf
from longbulksim.simulate import segment_states

REGIONS, EVENTS = load_blueprints()


def blueprint(g):
    return {r.clone: (None if r.parent == "root" else r.parent) for r in g.itertuples()}


class CCFProjection(unittest.TestCase):
    def test_every_blueprint_obeys_the_sum_rule(self):
        for _, g in REGIONS:
            parent, ccf, _ = project_ccf(blueprint(g), dict(zip(g.clone, g.ccf)), 0.05)
            root = next(c for c, p in parent.items() if p is None)
            self.assertEqual(ccf[root], 1.0)
            for c in parent:
                kids = sum(ccf[k] for k, p in parent.items() if p == c)
                self.assertLessEqual(kids, ccf[c] + 1e-9)

    def test_without_merging_the_clone_count_is_kept(self):
        for _, g in REGIONS[:200]:
            parent, _, _ = project_ccf(blueprint(g), dict(zip(g.clone, g.ccf)), 0.0)
            self.assertEqual(len(parent), len(g))

    def test_merge_absorbs_child_with_parent_ccf(self):
        parent, ccf, merged = project_ccf({"a": None, "b": "a", "c": "b"},
                                          {"a": 1.0, "b": 0.98, "c": 0.3}, 0.05)
        self.assertEqual(parent, {"a": None, "c": "a"})
        self.assertEqual(merged["b"], "a")


class DrawnSpecs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(3)
        cls.raws = [draw_spec(rng, REGIONS, EVENTS) for _ in range(100)]

    def test_specs_replay_and_every_snv_is_observable(self):
        for raw in self.raws:
            spec = parse_spec(raw)
            g = replay(spec)
            present = set().union(*(roles_in(g[c]) for c in spec.parent))
            self.assertEqual(set(spec.roles), present, raw["name"])

    def test_segments_have_at_most_two_tumour_states(self):
        for raw in self.raws:
            spec = parse_spec(raw)
            g = replay(spec)
            for s in spec.segments:
                segment_states(spec, g, s)

    def test_snvs_are_lost_by_non_loh_deletion(self):
        """A copy carrying the SNV is deleted while its HP keeps another copy (3+1 -> 2+1)."""
        n = 0
        for raw in self.raws:
            spec = parse_spec(raw)
            g = replay(spec)
            for c, roles in lost(spec, g).items():
                n += sum(len(g[c][spec.roles[r].segment][spec.roles[r].hp]) > 0 for r in roles)
        self.assertGreater(n, 0)

    def test_same_seed_same_spec(self):
        a = draw_spec(np.random.default_rng(5), REGIONS, EVENTS)
        b = draw_spec(np.random.default_rng(5), REGIONS, EVENTS)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
