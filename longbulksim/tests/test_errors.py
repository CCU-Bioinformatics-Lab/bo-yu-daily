"""Observation errors (v0.2): HP mistag, phase switches, base errors."""
import csv
import gzip
import hashlib
import unittest

import numpy as np

from test_simulate import read_tsv, simulate, stress

# sha256 of v0.1.0 output: python3 -m longbulksim specs/stress.yaml OUT --seed 7
V01_STRESS_SEED7 = {
    "input/data.tsv": "9195e5764665523448508dd6ec86593b758917745768a33fb2db7995adf2d4a0",
    "input/data_hp.tsv": "3a0c5a921c8eded65c070c1c3cf116f278236dc7a850f8920f40bc1d043e5251",
    "input/pairs.tsv": "6560b6eb5d4f4b13b9fb287656383da9a2b419e34e6f18f5b472cb3794259731",
    "input/segments.tsv": "b9feec350807017e80629fac350dac29097bc985fcc114a129194f532904c4a4",
}


def flat(n_snv=1, length=20_000_000, depth=50, **errors):
    """One clonal HP1 SNV role in one diploid segment, purity 1."""
    return {"name": "flat", "purity": 1.0, "depth": depth, **errors,
            "clones": {"C1": {"parent": None, "fraction": 1.0}},
            "segments": {"A": {"chrom": "chr1", "start": 1_000_000, "length": length}},
            "edges": {"C1": [{"snv": "s1", "hp": "HP1", "segment": "A", "count": n_snv}]}}


def reads_tsv(out):
    with gzip.open(out / "truth/reads.tsv.gz", "rt") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def within(test, got, n, p, msg=""):
    se = np.sqrt(p * (1 - p) / n)
    test.assertLess(abs(got / n - p), 4 * se, f"{msg}: {got}/{n} vs {p}")


class ZeroErrorsMatchV01(unittest.TestCase):
    def test_input_files_unchanged(self):
        _, out = simulate(stress(mistag_rate=0, switch_rate_per_mb=0, base_error=0), seed=7)
        for f, want in V01_STRESS_SEED7.items():
            self.assertEqual(hashlib.sha256((out / f).read_bytes()).hexdigest(), want, f)


class MistagRate(unittest.TestCase):
    def test_measured_rate(self):
        _, out = simulate(flat(length=5_000_000, mistag_rate=0.05))
        tagged = [r for r in reads_tsv(out) if r["tagged"] == "1"]
        within(self, sum(r["obs_hp"] != r["hp"] for r in tagged), len(tagged), 0.05, "mistag")

    def test_untouched_without_errors(self):
        _, out = simulate(flat(length=2_000_000))
        self.assertTrue(all(r["obs_hp"] == r["hp"] for r in reads_tsv(out)))


class BaseErrorRate(unittest.TestCase):
    def test_flipped_alleles(self):
        # clonal HP1 SNV, purity 1: HP2 reads are ref and HP1 reads are alt without errors
        _, out = simulate(flat(n_snv=300, base_error=0.03))
        c = {k: sum(int(r[k]) for r in read_tsv(out / "input/data_hp.tsv"))
             for k in ("ref_hp1", "alt_hp1", "ref_hp2", "alt_hp2")}
        within(self, c["ref_hp1"], c["ref_hp1"] + c["alt_hp1"], 0.03, "HP1 alt read as ref")
        within(self, c["alt_hp2"], c["ref_hp2"] + c["alt_hp2"], 0.03, "HP2 ref read as alt")


class PhaseSwitches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rate = 2.0
        _, cls.out = simulate(flat(length=50_000_000, depth=10, switch_rate_per_mb=cls.rate))
        cls.switches = np.array([int(r["pos"]) for r in read_tsv(cls.out / "truth/phase_switches.tsv")])

    def test_switch_count(self):
        want = self.rate * 50
        self.assertLess(abs(len(self.switches) - want), 4 * np.sqrt(want))

    def test_tag_flips_after_odd_switches(self):
        rows = reads_tsv(self.out)
        mid = np.array([(int(r["start"]) + int(r["end"])) // 2 for r in rows])
        odd = np.searchsorted(self.switches, mid, side="right") % 2 == 1
        flipped = np.array([r["obs_hp"] != r["hp"] for r in rows])
        np.testing.assert_array_equal(flipped, odd)
        self.assertGreater(odd.mean(), 0.3)


class ErrorsReachPairs(unittest.TestCase):
    """Segment C of the stress tree: s3 (C1, HP1), s4 (C2, HP2), s6 (C3, HP2)."""

    def cells(self, a, b, hap, **errors):
        segs = stress()["segments"]
        segs["C"]["length"] = 60_000  # 50 SNVs in 60 kb, so most pairs share reads
        _, out = simulate(stress(segments=segs, **errors))
        rows = [r for r in read_tsv(out / "input/pairs.tsv")
                if r["mutation_i"].startswith(a + "_") and r["mutation_j"].startswith(b + "_")
                and r["hap"] == hap]
        return {k: sum(int(r[k]) for r in rows) for k in ("n11", "n10", "n01", "n00")}

    def test_base_error_puts_branch_pair_on_one_read(self):
        self.assertEqual(self.cells("s4", "s6", "HP2")["n11"], 0)
        self.assertGreater(self.cells("s4", "s6", "HP2", base_error=0.03)["n11"], 0)

    def test_mistag_moves_whole_reads_only(self):
        # a mistagged HP1 read carries neither HP2 SNV, so it lands in n00 of the HP2 pair
        self.assertEqual(self.cells("s4", "s6", "HP2", mistag_rate=0.05)["n11"], 0)
        # a mistagged HP2 read carrying s4 shows up as n01 of s3 x s4 on HP1
        self.assertGreater(self.cells("s3", "s4", "HP1", mistag_rate=0.05)["n01"], 0)

    def test_switch_puts_other_hp_alt_on_the_tag(self):
        self.assertEqual(self.cells("s3", "s4", "HP1")["n01"], 0)
        self.assertGreater(self.cells("s3", "s4", "HP1", switch_rate_per_mb=50)["n01"], 0)


if __name__ == "__main__":
    unittest.main()
