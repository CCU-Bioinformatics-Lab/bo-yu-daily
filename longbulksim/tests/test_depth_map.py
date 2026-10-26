"""Depth map (v0.7): read starts follow a real normal's start density."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from longbulksim import depth_map
from test_errors import flat, reads_tsv
from test_simulate import read_tsv, simulate


def toy_map(weights, bin_size=1_000_000):
    path = Path(tempfile.mkdtemp()) / "m.npz"
    np.savez(path, bin_size=bin_size, chr1=np.asarray(weights, np.float32))
    return path


class Map(unittest.TestCase):
    def test_draw_follows_weights(self):
        dmap = depth_map.load(toy_map([0, 1, 3, 0]))
        s = depth_map.draw_starts(np.random.default_rng(0), dmap, "chr1", 0, 4_000_000, 40_000)
        counts = np.bincount(s // 1_000_000, minlength=4)
        self.assertEqual(counts[0] + counts[3], 0)
        self.assertLess(abs(counts[2] / counts[1] - 3), 0.15)

    def test_partial_bins_and_mean(self):
        dmap = depth_map.load(toy_map([1, 3]))
        self.assertAlmostEqual(depth_map.mean_weight(dmap, "chr1", 500_000, 1_500_000), 2.0)
        s = depth_map.draw_starts(np.random.default_rng(0), dmap, "chr1", 500_000, 1_500_000, 1000)
        self.assertTrue(((s >= 500_000) & (s < 1_500_000)).all())

    def test_unknown_chrom_and_past_end(self):
        dmap = depth_map.load(toy_map([2]))
        self.assertEqual(depth_map.mean_weight(dmap, "chr2", 0, 5_000_000), 1.0)
        self.assertEqual(depth_map.mean_weight(dmap, "chr1", 2_000_000, 3_000_000), 0.0)

    def test_zero_region_gives_no_reads(self):
        dmap = depth_map.load(toy_map([0, 0]))
        self.assertEqual(len(depth_map.draw_starts(np.random.default_rng(0), dmap, "chr1", 0, 2_000_000, 0)), 0)


class Simulation(unittest.TestCase):
    def test_depth_tracks_map(self):
        # segment chr1:1-21 Mb; weight 0.5 on 1-11 Mb, 1.5 on 11-21 Mb
        path = toy_map([0.5] * 11 + [1.5] * 11)
        _, out = simulate(flat(n_snv=400, length=20_000_000, depth=40) | {"depth_map": str(path)})
        truth = {r["mutation_id"]: int(r["pos"]) for r in read_tsv(out / "truth/truth.tsv")}
        lo, hi = [], []
        for r in read_tsv(out / "input/data.tsv"):
            d = int(r["ref_counts"]) + int(r["alt_counts"])
            (lo if truth[r["mutation_id"]] < 10_000_000 else hi).append(d)
        self.assertLess(abs(np.mean(hi) / np.mean(lo) - 3), 0.4)
        self.assertLess(abs(np.mean(lo + hi) - 40), 4)  # mean weight 1 keeps the target depth

    def test_none_is_uniform(self):
        _, out = simulate(flat(n_snv=5, length=1_000_000))
        self.assertTrue(len(reads_tsv(out)) > 0)


if __name__ == "__main__":
    unittest.main()
