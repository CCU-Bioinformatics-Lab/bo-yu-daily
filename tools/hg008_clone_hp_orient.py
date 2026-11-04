#!/usr/bin/env python3
"""Assembly haplotype (hap1/hap2) of every clone-tree SNV from each clone's own PacBio phasing.

Each clone's HiPhase run phased germline hets (<clone>.dipcall.germline.vcf.gz) and somatic SNVs
(<clone>.deepsomatic.vcf.gz) together, so they share phase-set (PS) ids. A block's local
orientation is random; it is fixed by comparing the block's germline hets with the HG008-N column
of the GIAB V0.4 full_tumornormal VCF (phased against the HG008-N assembly, as in hg008_bulk_hp.py).
A block is oriented when >= MIN_HETS hets are informative and >= BLOCK_FRAC agree on one
orientation. Only SNVs in a 1+1 PURPLE segment of that clone are counted (both haplotypes present).

Checks written to the summary: (a) SNVs shared by several clones get the same hap from each clone;
(b) agreement with the bulk ONT hap from hg008_bulk_hp.py.

Usage: python3 -I tools/hg008_clone_hp_orient.py HG008_DIR CLONE_TABLE_DIR OUT_DIR
Outputs: clone_snv_hp.tsv (chrom pos pattern clone hap), clone_hp_by_branch.tsv
"""
import collections
import csv
import subprocess
import sys
from pathlib import Path

HG008, CTAB, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
FULL_VCF = HG008 / "smvar_V0.4/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_full_tumornormal.vcf.gz"
MIN_HETS = 3
BLOCK_FRAC = 0.8


def query(vcf, fmt, *extra):
    out = subprocess.run(["bcftools", "query", *extra, "-f", fmt, str(vcf)],
                         capture_output=True, text=True, check=True).stdout
    return (l.split("\t") for l in out.splitlines())


def normal_hets():
    """V0.4 HG008-N phased biallelic het SNPs: (chrom, pos) -> (ref, alt, alt_hap)."""
    hets = {}
    for chrom, pos, ref, alt, gt in query(FULL_VCF, "%CHROM\t%POS\t%REF\t%ALT\t[%GT]\n", "-s", "HG008-N"):
        gt = gt.rstrip("\t")
        if gt in ("0|1", "1|0") and len(ref) == 1 and len(alt) == 1:
            hets[(chrom, int(pos))] = (ref, alt, 2 if gt == "0|1" else 1)
    return hets


def clone_file(clone, suffix):
    return next((HG008 / "clones").rglob(f"HG008T-{clone}.{suffix}"))


def purple_11(clone):
    segs = collections.defaultdict(list)
    with open(clone_file(clone, "purple.segment.tsv")) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if int(r["depthWindowCount"]) and round(float(r["majorAlleleCopyNumber"])) == 1 \
                    and round(float(r["minorAlleleCopyNumber"])) == 1:
                segs[r["chromosome"]].append((int(r["start"]), int(r["end"])))
    return segs


def in_segs(segs, chrom, pos):
    return any(s <= pos <= e for s, e in segs.get(chrom, ()))


def block_orientation(clone, hets):
    """(chrom, PS) -> +1 (local hap == assembly hap) or -1 (flipped)."""
    votes = collections.defaultdict(lambda: [0, 0])
    for chrom, pos, ref, alt, gt, ps in query(clone_file(clone, "dipcall.germline.vcf.gz"),
                                              "%CHROM\t%POS\t%REF\t%ALT[\t%GT\t%PS]\n"):
        h = hets.get((chrom, int(pos)))
        if h is None or gt not in ("0|1", "1|0") or ps == "." or (ref, alt) != h[:2]:
            continue
        local = 2 if gt == "0|1" else 1
        votes[(chrom, ps)][0 if local == h[2] else 1] += 1
    orient = {}
    for k, (same, opp) in votes.items():
        n = same + opp
        if n >= MIN_HETS and max(same, opp) >= BLOCK_FRAC * n:
            orient[k] = 1 if same > opp else -1
    return orient, len(votes)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    patterns = {}
    with open(CTAB / "snv_patterns.tsv") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            patterns[(r["chrom"], int(r["pos"]))] = (r["ref"], r["alt"], r["pattern"])
    hets = normal_hets()
    calls = []  # (chrom, pos, pattern, clone, hap)
    log = []
    for clone in CLONES:
        orient, n_blocks = block_orientation(clone, hets)
        segs = purple_11(clone)
        n = collections.Counter()
        for chrom, pos, ref, alt, gt, ps in query(clone_file(clone, "deepsomatic.vcf.gz"),
                                                  "%CHROM\t%POS\t%REF\t%ALT[\t%GT\t%PS]\n", "-f", "PASS"):
            key = (chrom, int(pos))
            if key not in patterns or patterns[key][:2] != (ref, alt) or clone not in patterns[key][2].split(","):
                continue
            if not in_segs(segs, chrom, int(pos)):
                n["not 1+1"] += 1
                continue
            o = orient.get((chrom, ps)) if gt in ("0|1", "1|0") and ps != "." else None
            if o is None:
                n["unoriented"] += 1
                hap = "."
            else:
                local = 2 if gt == "0|1" else 1
                hap = f"hap{local if o == 1 else 3 - local}"
                n[hap] += 1
            calls.append((chrom, int(pos), patterns[key][2], clone, hap))
        log.append(f"{clone}: {len(orient)}/{n_blocks} blocks oriented; SNVs {dict(n)}")

    with open(OUT / "clone_snv_hp.tsv", "w") as fh:
        fh.write("chrom\tpos\tpattern\tclone\thap\n")
        for c in calls:
            fh.write("\t".join(map(str, c)) + "\n")

    per_snv = collections.defaultdict(list)
    for chrom, pos, pat, clone, hap in calls:
        if hap != ".":
            per_snv[(chrom, pos, pat)].append(hap)
    bulk = {}
    with open(CTAB / "bulk_hp.tsv") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["hap"] in ("hap1", "hap2"):
                bulk[(r["chrom"], int(r["pos"]))] = r["hap"]
    rows = collections.defaultdict(collections.Counter)
    agree = collections.Counter()
    for (chrom, pos, pat), haps in per_snv.items():
        c = collections.Counter(haps)
        if len(haps) > 1:
            agree["multi-clone SNVs"] += 1
            agree["all clones agree"] += len(c) == 1
        top, k = c.most_common(1)[0]
        rows[pat][top if k == len(haps) else "conflict"] += 1
        b = bulk.get((chrom, pos))
        if b and k == len(haps):
            agree["bulk compared"] += 1
            agree["bulk agrees"] += b == top
    with open(OUT / "clone_hp_by_branch.tsv", "w") as fh:
        fh.write("pattern\tn_clones\thap1\thap2\tconflict\n")
        for pat, c in sorted(rows.items(), key=lambda x: -sum(x[1].values())):
            fh.write(f"{pat}\t{len(pat.split(','))}\t{c['hap1']}\t{c['hap2']}\t{c['conflict']}\n")
    log.append(f"checks: {dict(agree)}")
    (OUT / "clone_hp_summary.txt").write_text("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
