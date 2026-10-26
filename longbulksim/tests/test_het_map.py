"""Het-map tagging (v0.3): the longphase-s germline haplotag rule."""
import gzip
import tempfile
import unittest
from pathlib import Path

import numpy as np

from longbulksim import het_map
from longbulksim.model import DATA_DIR
from test_errors import flat, reads_tsv
from test_simulate import simulate

HCC1395BL = DATA_DIR / "hcc1395bl_phased_het.npz"

VCF = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS
chr1\t100\t.\tA\tG\t.\t.\t.\tGT:PS\t0|1:100
chr1\t200\t.\tA\tG\t.\t.\t.\tGT:PS\t1|0:100
chr1\t250\t.\tA\tG\t.\t.\t.\tGT\t0/1
chr1\t300\t.\tA\tG\t.\t.\t.\tGT:PS\t0|1:300
"""


def toy_map():
    tmp = Path(tempfile.mkdtemp())
    with gzip.open(tmp / "p.vcf.gz", "wt") as fh:
        fh.write(VCF)
    het_map.build(tmp / "p.vcf.gz", tmp / "m.npz")
    return het_map.load(tmp / "m.npz")


class Rule(unittest.TestCase):
    def test_build_keeps_phased_only(self):
        pos, ps = toy_map()["chr1"]
        self.assertEqual(pos.tolist(), [100, 200, 300])
        self.assertEqual(ps.tolist(), [0, 0, 1])

    def test_tag_rule(self):
        m = toy_map()
        start = np.array([10, 90, 150, 150, 290, 10, 100])
        end = np.array([90, 210, 250, 310, 400, 100, 101])
        # no het | block 0 | block 0 | blocks 0+1 | block 1 | end is exclusive | single het
        want = [False, True, True, False, True, False, True]
        self.assertEqual(het_map.tagged(m, "chr1", start, end).tolist(), want)

    def test_unknown_chrom_untagged(self):
        self.assertFalse(het_map.tagged(toy_map(), "chr2", np.array([0]), np.array([10**9])).any())


@unittest.skipUnless(HCC1395BL.exists(), "HCC1395BL het map missing")
class SimulatorUsesMap(unittest.TestCase):
    def test_tags_follow_map(self):
        spec, out = simulate(flat(length=3_000_000, het_map=HCC1395BL.name))
        m = het_map.load(HCC1395BL)
        rows = reads_tsv(out)
        start = np.array([int(r["start"]) for r in rows])
        end = np.array([int(r["end"]) for r in rows])
        want = het_map.tagged(m, "chr1", start, end)
        got = np.array([r["tagged"] == "1" for r in rows])
        self.assertTrue((got == want).all())
        # some reads untagged, most tagged
        self.assertGreater(got.mean(), 0.5)
        self.assertLess(got.mean(), 1.0)

    def test_phased_fraction_ignored(self):
        _, a = simulate(flat(length=1_000_000, het_map=HCC1395BL.name, phased_fraction=0.1))
        _, b = simulate(flat(length=1_000_000, het_map=HCC1395BL.name, phased_fraction=0.9))
        self.assertEqual((a / "input/data_hp.tsv").read_bytes(), (b / "input/data_hp.tsv").read_bytes())


if __name__ == "__main__":
    unittest.main()
