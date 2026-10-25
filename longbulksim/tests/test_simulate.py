import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np
import yaml

from longbulksim.model import parse_spec, replay
from longbulksim.sample import load_read_span, sample_segment
from longbulksim.simulate import run

SPECS = Path(__file__).resolve().parents[1] / "specs"


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def simulate(raw, seed=1):
    out = tempfile.mkdtemp()
    spec = parse_spec(raw)
    run(spec, seed, out)
    return spec, Path(out)


def stress(**override):
    raw = yaml.safe_load((SPECS / "stress.yaml").read_text())
    raw.update(override)
    return raw


class SpanningReadsMatchHCC1395(unittest.TestCase):
    """lab_report/2026-10-25_hcc1395_hp_split: median reads spanning an SNV pair, ONT ~50x."""
    MEASURED = [((0, 1e3), 52), ((1e3, 5e3), 44), ((5e3, 2e4), 21), ((2e4, 5e4), 2),
                ((5e4, 1e5), 0)]

    def test_spanning_by_distance(self):
        raw = {"name": "flat", "purity": 1.0, "depth": 52,
               "clones": {"C1": {"parent": None, "fraction": 1.0}},
               "segments": {"A": {"chrom": "chr1", "start": 1_000_000, "length": 20_000_000}}}
        spec = parse_spec(raw)
        rng = np.random.default_rng(0)
        reads = sample_segment(rng, spec, replay(spec), "A", load_read_span(spec.read_span))
        for (lo, hi), want in self.MEASURED:
            n = []
            for p in rng.integers(2_000_000, 19_000_000, 400):
                d = int(rng.uniform(lo, hi))
                n.append(len(np.intersect1d(reads.covering(p), reads.covering(p + d))))
            got = np.median(n)
            tol = max(2, 0.2 * want)
            self.assertLessEqual(abs(got - want), tol, f"{lo}-{hi} bp: {got} vs {want}")


class ReadCooccurrenceFollowsTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        segs = stress()["segments"]
        segs["C"]["length"] = 60_000  # 50 SNVs in 60 kb, so most pairs share reads
        cls.spec, cls.out = simulate(stress(segments=segs))
        cls.pairs = read_tsv(cls.out / "input/pairs.tsv")

    def pattern(self, a, b, cell):
        rows = [r for r in self.pairs if r["mutation_i"].startswith(a + "_")
                and r["mutation_j"].startswith(b + "_")]
        self.assertGreater(sum(int(r["callable_pair_reads"]) for r in rows), 100)
        return sum(int(r[cell]) for r in rows)

    def test_branch_pair_never_on_one_read(self):
        self.assertEqual(self.pattern("s4", "s6", "n11"), 0)  # C2 vs C3, both HP2

    def test_descendant_never_without_ancestor(self):
        self.assertEqual(self.pattern("s3", "s5", "n01"), 0)  # C1 then C4, both HP1
        self.assertGreater(self.pattern("s3", "s5", "n11"), 0)

    def test_alt_reads_only_on_the_snv_hp(self):
        truth = {r["mutation_id"]: r["hp"] for r in read_tsv(self.out / "truth/truth.tsv")}
        for r in read_tsv(self.out / "input/data_hp.tsv"):
            other = "alt_hp2" if truth[r["mutation_id"]] == "HP1" else "alt_hp1"
            self.assertEqual(r[other], "0", r["mutation_id"])


class CountsMatchExpectedVAF(unittest.TestCase):
    def test_role_mean_vaf_and_depth(self):
        raw = stress(depth=100)
        for edge in raw["edges"].values():
            for e in edge:
                if "snv" in e:
                    e["count"] = 200
        for s in raw["segments"].values():
            s["length"] *= 20
        _, out = simulate(raw)
        truth = {r["mutation_id"]: r for r in read_tsv(out / "truth/truth.tsv")}
        by_role = {}
        for r in read_tsv(out / "input/data.tsv"):
            t = truth[r["mutation_id"]]
            by_role.setdefault(t["role"], []).append(
                (int(r["alt_counts"]), int(r["ref_counts"]) + int(r["alt_counts"])))
        for role, xs in by_role.items():
            alt, dp = np.array(xs).T
            v = float(next(t["vaf_expected"] for t in truth.values() if t["role"] == role))
            se = np.sqrt(v * (1 - v) / dp.sum())
            self.assertLess(abs(alt.sum() / dp.sum() - v), 4 * se, role)
        dp_c = [d for role, xs in by_role.items() if role in ("s3", "s4", "s5", "s6", "s7")
                for _, d in xs]  # segment C is diploid in every clone
        self.assertAlmostEqual(np.mean(dp_c) / 100, 1, delta=0.03)


class Reproducible(unittest.TestCase):
    def test_same_seed_same_files(self):
        _, a = simulate(stress(), seed=7)
        _, b = simulate(stress(), seed=7)
        for f in ("input/data_hp.tsv", "input/pairs.tsv", "truth/truth.tsv"):
            self.assertEqual((a / f).read_text(), (b / f).read_text(), f)


if __name__ == "__main__":
    unittest.main()
