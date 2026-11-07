#!/usr/bin/env python3
"""Test whether neighbouring somatic SNVs fall on the two haplotypes independently (diplosim's assumption).

Statistic: among consecutive SNV pairs, the share on the same haplotype, per distance bin.

Inputs, all restricted to autosomes with equal copy number on both haplotypes:
  assembly_<line>  COLO829 and HG008 in PRCGAP: the contig's haplotype and the GRCh38 position, with
                   the strict filter and the 20 Mb balanced windows of prcgap_hap_snv_ratio.py.
                   Hap labels are arbitrary between chromosomes, so only comparisons within a window count.
  read_truncal_<clone>, read_private  HG008 clones: DeepSomatic GT and PS from HiPhase, QUAL >= 20,
                   VAF 0.25-0.75, PURPLE state 1+1 (all 8 clones for truncal, the carrier for private).
                   The 8 truncal rows share SNVs, so only the clone with the most pairs is a primary test.

Clusters: SNVs closer than CLUSTER_BP keep only their first SNV for the main bins. The <1 kb bin
uses all SNVs and is the positive control: nearby SNVs share a read or a kataegis track, so a working
phase signal must show them mostly on one haplotype.

Null: hap labels shuffled within each group (window or phase block), which keeps each group's own
hap ratio and tests structure below the group's scale. Phase switch errors push pairs toward 0.5.

Rule fixed before the first run. Independence is rejected at a distance when both the assembly and
the read data show same-hap share above the null mean by >= MIN_EFFECT with Bonferroni p < 0.05
over the primary tests. If the positive control fails (< CONTROL_MIN), the check does not count.

Added after the first run, because COLO829 missed CONTROL_MIN: control_detail.tsv splits the <1 kb bin
and gives the pairs expected by chance from SNV density (gaps taken as exponential within each group).
It explains the control result and does not change the rule above.

Output (OUT_DIR): pairs_by_distance.tsv, input_summary.tsv, control_detail.tsv
Usage: python3 tools/snv_hp_independence.py PRCGAP_EXTRACTED HG008_DIR OUT_DIR
"""
import collections
import csv
import gzip
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prcgap_hap_snv_ratio as prcgap  # noqa: E402

CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
AUTOSOME = re.compile(r"chr[0-9]+$")
CLUSTER_BP = 1_000
BINS = [(1_000, 10_000, "1-10 kb"), (10_000, 100_000, "10-100 kb"), (100_000, 1_000_000, "100 kb-1 Mb"),
        (1_000_000, 20_000_000, ">=1 Mb")]
CONTROL_BIN = (0, 1_000, "<1 kb (control)")
MIN_QUAL = 20
VAF_RANGE = (0.25, 0.75)
N_PERM = 5000
MIN_EFFECT = 0.05
CONTROL_MIN = 0.8
CONTROL_SPLIT = [(0, 100), (100, 300), (300, 1_000)]
SEED = 20261107


def assembly_groups(root, line):
    """Balanced 20 Mb windows of a PRCGAP line: {(chrom, window): [(GRCh38 pos, hap)]}."""
    contigs, retained, placement = prcgap.load_sample(root, line)
    rows = prcgap.tsv(root / line / "point_mutation" / f"{line}.deepsomatic.snv.annotated_checked_gnomad.txt")
    windows = collections.defaultdict(list)
    for r in rows:
        if not prcgap.strict_filter(r):
            continue
        info = contigs.get(r["Contig"])
        hap = "hap" + r["Haplotype"][-1]
        if info is None or info["hap"] != hap or not AUTOSOME.match(info["chrom"]):
            continue
        if prcgap.segment_cn(retained[hap].get(info["chrom"], []), prcgap.index_of(info, placement, r["Contig"], int(r["Start"]))) is None:
            continue
        if r["chm13_pos"].isdigit() and r["chm13_contig"] == info["chrom"] and r["GRCh38_pos"].isdigit() and r["GRCh38_contig"] == info["chrom"]:
            windows[(info["chrom"], int(r["chm13_pos"]) // prcgap.WINDOW)].append((int(r["GRCh38_pos"]), int(hap[-1])))
    hit1, cn1 = prcgap.retained_windows(contigs, retained, placement, "hap1")
    hit2, cn2 = prcgap.retained_windows(contigs, retained, placement, "hap2")
    full = prcgap.WINDOW / prcgap.BIN
    return {k: v for k, v in windows.items()
            if hit1[k] / full >= .8 and hit2[k] / full >= .8 and len(v) >= prcgap.MIN_SNV
            and abs(cn1[k] / hit1[k] - cn2[k] / hit2[k]) < prcgap.MAX_CN_GAP}


def read_clone(hg008, clone):
    path = next((hg008 / "clones").rglob(f"HG008T-{clone}.deepsomatic.vcf.gz"))
    calls = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.rstrip("\n").split("\t")
            if f[6] != "PASS" or len(f[3]) != 1 or len(f[4]) != 1 or not AUTOSOME.match(f[0]):
                continue
            fmt = dict(zip(f[8].split(":"), f[9].split(":")))
            calls[(f[0], int(f[1]), f[3], f[4])] = (float(fmt["VAF"]), float(f[5]), fmt["GT"], fmt.get("PS", "."))
    return calls


def read_one_one(hg008, clone):
    """Sorted segments with rounded PURPLE state 1+1, per chromosome."""
    path = next((hg008 / "clones").rglob(f"HG008T-{clone}.purple.segment.tsv"))
    segs = collections.defaultdict(list)
    with open(path) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if int(r["depthWindowCount"]) and round(float(r["majorAlleleCopyNumber"])) == 1 and round(float(r["minorAlleleCopyNumber"])) == 1:
                segs[r["chromosome"]].append((int(r["start"]), int(r["end"])))
    return segs


def in_segments(segs, chrom, pos):
    return any(start <= pos <= end for start, end in segs.get(chrom, ()))


def read_groups(hg008):
    """Phase blocks: truncal per clone and private pooled, {name: {block: [(pos, hap)]}}."""
    calls = {c: read_clone(hg008, c) for c in CLONES}
    one_one = {c: read_one_one(hg008, c) for c in CLONES}
    carriers = collections.defaultdict(list)
    for clone in CLONES:
        for key in calls[clone]:
            carriers[key].append(clone)
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for key, have in carriers.items():
        if len(have) not in (1, len(CLONES)):
            continue
        got = [calls[c][key] for c in have]
        if any(not VAF_RANGE[0] <= g[0] <= VAF_RANGE[1] for g in got) or np.median([g[1] for g in got]) < MIN_QUAL:
            continue
        chrom, pos = key[0], key[1]
        if not all(in_segments(one_one[c], chrom, pos) for c in (CLONES if len(have) > 1 else have)):
            continue
        for clone, g in zip(have, got):
            if g[2] not in ("0|1", "1|0") or g[3] == ".":
                continue
            if len(have) == 1:
                groups["read_private"][(clone, chrom, g[3])].append((pos, int(g[2] == "1|0")))
            else:
                groups[f"read_truncal_{clone}"][(chrom, g[3])].append((pos, int(g[2] == "1|0")))
    return groups


def decluster(snvs):
    """Keeps the first SNV of each run with gaps below CLUSTER_BP."""
    kept, previous = [], None
    for pos, hap in sorted(snvs):
        if previous is None or pos - previous >= CLUSTER_BP:
            kept.append((pos, hap))
        previous = pos
    return kept


def test_bins(groups, bins, rng):
    """Observed same-hap pairs and their null distribution per bin, shuffling within each group."""
    observed = np.zeros(len(bins), dtype=int)
    totals = np.zeros(len(bins), dtype=int)
    null = np.zeros((N_PERM, len(bins)), dtype=int)
    for snvs in groups:
        if len(snvs) < 2:
            continue
        pos = np.array([s[0] for s in snvs])
        hap = np.array([s[1] for s in snvs])
        gaps = np.diff(pos)
        shuffled = rng.permuted(np.tile(hap, (N_PERM, 1)), axis=1)
        same_null = shuffled[:, :-1] == shuffled[:, 1:]
        same_obs = hap[:-1] == hap[1:]
        for i, (low, high, _) in enumerate(bins):
            mask = (gaps >= low) & (gaps < high)
            if mask.any():
                observed[i] += same_obs[mask].sum()
                totals[i] += mask.sum()
                null[:, i] += same_null[:, mask].sum(axis=1)
    return observed, totals, null


def control_detail(name, groups):
    """Same-hap share below 1 kb by distance, with chance pairs from density. Rows for one dataset."""
    rows = []
    for low, high in CONTROL_SPLIT:
        same = total = 0
        chance = 0.0
        for snvs in groups:
            if len(snvs) < 2:
                continue
            pos = np.array([s[0] for s in snvs])
            hap = np.array([s[1] for s in snvs])
            gaps = np.diff(pos)
            mask = (gaps >= low) & (gaps < high)
            same += (hap[:-1] == hap[1:])[mask].sum()
            total += mask.sum()
            rate = len(snvs) / max(pos[-1] - pos[0], 1)
            chance += (len(snvs) - 1) * (np.exp(-rate * low) - np.exp(-rate * high))
        rows.append((name, f"{low}-{high}", total, same, same / total if total else float("nan"), chance))
    return rows


def main():
    root, hg008, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    data = {f"assembly_{line}": assembly_groups(root, line) for line in ("COLO829", "HG008")}
    data.update(read_groups(hg008))
    rng = np.random.default_rng(SEED)
    results, summary, details = {}, [], []
    for name, groups in data.items():
        full = [sorted(v) for v in groups.values()]
        details += control_detail(name, full)
        clean = [decluster(v) for v in full]
        control = test_bins(full, [CONTROL_BIN], rng)
        main_bins = test_bins(clean, BINS, rng)
        results[name] = (control, main_bins)
        summary.append(dict(dataset=name, n_groups=len(full), n_snv=sum(map(len, full)), n_snv_declustered=sum(map(len, clean))))

    truncal = [n for n in results if n.startswith("read_truncal_")]
    primary_truncal = max(truncal, key=lambda n: results[n][1][1].sum())
    primary = ["assembly_COLO829", "assembly_HG008", primary_truncal, "read_private"]
    n_tests = len(primary) * len(BINS)
    with open(out / "pairs_by_distance.tsv", "w") as fh:
        fh.write("dataset\tprimary\tdistance\tn_pairs\tsame_hap\tshare_same\tnull_mean\tnull_low95\tnull_high95\texcess\tp\tp_bonferroni\n")
        for name, (control, main_bins) in results.items():
            for (observed, totals, null), bins, is_main in ((control, [CONTROL_BIN], False), (main_bins, BINS, True)):
                for i, (_, _, label) in enumerate(bins):
                    if not totals[i]:
                        continue
                    share = null[:, i] / totals[i]
                    obs = observed[i] / totals[i]
                    tail = min((null[:, i] >= observed[i]).sum(), (null[:, i] <= observed[i]).sum())
                    p = min(1.0, 2 * (tail + 1) / (N_PERM + 1))
                    is_primary = is_main and name in primary
                    corrected = f"{min(1.0, p * n_tests):.4g}" if is_primary else "NA"
                    fh.write(f"{name}\t{int(is_primary)}\t{label}\t{totals[i]}\t{observed[i]}\t{obs:.3f}\t{share.mean():.3f}\t"
                             f"{np.quantile(share, .025):.3f}\t{np.quantile(share, .975):.3f}\t{obs - share.mean():+.3f}\t{p:.4g}\t{corrected}\n")
    with open(out / "control_detail.tsv", "w") as fh:
        fh.write("dataset\tdistance_bp\tn_pairs\tsame_hap\tshare_same\tpairs_expected_by_chance\n")
        for name, label, total, same, share, chance in details:
            fh.write(f"{name}\t{label}\t{total}\t{same}\t{share:.3f}\t{chance:.1f}\n")
    with open(out / "input_summary.tsv", "w") as fh:
        fh.write("dataset\tn_groups\tn_snv\tn_snv_declustered\n")
        for row in summary:
            fh.write("\t".join(str(v) for v in row.values()) + "\n")


if __name__ == "__main__":
    main()
