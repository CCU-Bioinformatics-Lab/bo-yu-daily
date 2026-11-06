#!/usr/bin/env python3
"""Collect COLO829 evidence that does not depend on somatic SNV counts.

  python3 -I tools/colo829_event_evidence.py coverage <somatic_snvs.vcf.gz> <out.tsv>
      Sample Fiber-seq coverage per contig on the donor assembly, tumor and blood, through the UCSC API.
  python3 tools/colo829_event_evidence.py baf-regions <out.bed>
      List sampled windows on GRCh38.
  python3 tools/colo829_event_evidence.py baf-window <chrom> <start> <end>
      For one window of the lab's ONT R10 CRAMs, print blood het sites with both samples' allele depths.

Coverage answers "is the DNA there?". Allele depth at blood het sites answers the same question on an
independent data set, a different platform and a different reference.

  python3 tools/colo829_event_evidence.py baf-summary <baf_raw.tsv> <windows.tsv>
      Summarize each sampled window: depth ratio, minor allele fraction, allelic state.
  python3 tools/colo829_event_evidence.py phase-snv <clairs_snv.vcf.gz> <windows.tsv> <out.tsv>
      For sampled somatic SNVs, use reads that span the SNV and a nearby blood het site to find the allele
      the SNV sits on, and that allele's share of tumor reads. In 2:1 regions this labels major or minor.
"""
import gzip
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GENOME = "hub_6753970_DSA_COLO829BL_v3.0.0"
TRACKS = {"tumor": "COLO829T_DSA-all-FIRE-nucleosome", "blood": "COLO829BL_DSA-all-FIRE-nucleosome"}
MIN_LEN = 20_000_000
N_WINDOWS = 10
WINDOW = 2_000
REF = "/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
TUMOR = os.environ.get("COLO_TUMOR", "/big8_disk/data/COLO829/ONT_R10/COLO829.cram")
BLOOD = os.environ.get("COLO_BLOOD", "/big8_disk/data/COLO829/ONT_R10/COLO829BL.cram")
FAI_CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]


def fetch_mean(track, chrom, start, end):
    q = urllib.parse.urlencode({"genome": GENOME, "track": track, "chrom": chrom, "start": start, "end": end})
    url = f"https://api.genome.ucsc.edu/getData/track?{q}"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                d = json.load(r)
            items = d.get(track, [])
            covered = sum((x["end"] - x["start"]) * x["value"] for x in items)
            return covered / (end - start)
        except Exception as e:
            err = e
            time.sleep(5 + attempt * 15)
    print(f"failed {chrom}:{start} {err}", file=sys.stderr)
    return None


def coverage(vcf, out):
    lengths = {}
    with gzip.open(vcf, "rt") as f:
        for line in f:
            if not line.startswith("##"):
                break
            m = re.search(r"##contig=<ID=([^,]+),length=(\d+)", line)
            if m:
                lengths[m[1]] = int(m[2])
    jobs = []
    for c, L in lengths.items():
        if L < MIN_LEN:
            continue
        for i in range(N_WINDOWS):
            start = int(L * (i + 0.5) / N_WINDOWS)
            jobs.append((c, L, start))
    done = set()
    out = Path(out)
    if out.exists():
        done = {tuple(line.split("\t")[:2]) for line in out.read_text().splitlines()[1:]}
    else:
        out.write_text("contig\tstart\tlength\ttumor\tblood\n")

    def one(job):
        c, L, s = job
        if (c, str(s)) in done:
            return None
        t = fetch_mean(TRACKS["tumor"], c, s, s + WINDOW)
        b = fetch_mean(TRACKS["blood"], c, s, s + WINDOW)
        return f"{c}\t{s}\t{L}\t{t}\t{b}\n"

    with ThreadPoolExecutor(3) as ex, out.open("a") as f:
        for i, row in enumerate(ex.map(one, jobs)):
            if row:
                f.write(row)
                f.flush()
            if i % 50 == 0:
                print(f"{i}/{len(jobs)}", file=sys.stderr, flush=True)


def baf_regions(out):
    lines = []
    for line in open(REF + ".fai"):
        c, L = line.split("\t")[:2]
        if c in FAI_CHROMS:
            for s in range(1_000_000, int(L) - 200_000, 3_000_000):
                lines.append(f"{c}\t{s}\t{s + 100_000}\n")
    Path(out).write_text("".join(lines))
    print(len(lines), "windows")


def baf_window(chrom, start, end):
    """One line per SNP that looks het in blood: chrom pos blood_ref blood_alt tumor_ref tumor_alt."""
    region = f"{chrom}:{int(start) + 1}-{end}"
    cmd = ["bcftools", "mpileup", "-f", REF, "-r", region, "-q", "20", "-Q", "15", "-a", "FORMAT/AD", "--max-depth", "400", "-I", "-Ou", BLOOD, TUMOR]
    q = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    r = subprocess.run(["bcftools", "query", "-f", "%CHROM\t%POS\t%REF\t%ALT[\t%AD]\n"], stdin=q.stdout, capture_output=True, text=True)
    rows = dp_b = dp_t = n = 0
    for line in r.stdout.splitlines():
        c, pos, ref, alt, adb, adt = line.split("\t")
        ab, at = adb.split(","), adt.split(",")
        b_tot, t_tot = sum(map(int, ab)), sum(map(int, at))
        dp_b += b_tot
        dp_t += t_tot
        n += 1
        if "<*>" == alt or len(ab) < 2:
            continue
        b_alt = int(ab[1])
        if b_tot >= 12 and .33 <= b_alt / b_tot <= .67 and len(alt.split(",")[0]) == 1:
            print(f"S\t{c}\t{pos}\t{ab[0]}\t{ab[1]}\t{at[0]}\t{at[1]}")
    if n:
        print(f"W\t{chrom}\t{start}\t{end}\t{dp_b / n:.1f}\t{dp_t / n:.1f}")


def state(ratio, maf):
    """Allelic state from depth ratio and minor allele fraction. Ratio per copy is about 0.75 in this sample."""
    if ratio is None or maf is None:
        return "NA"
    if maf < .1:
        return "LOH"
    if .25 <= maf <= .40 and 1.9 <= ratio <= 2.65:
        return "2:1"
    if maf > .40 and ratio >= 2.6:
        return "2:2"
    return "other"


def baf_summary(raw, out):
    from statistics import median
    wins, sites = {}, defaultdict(list)
    for line in open(raw):
        f = line.rstrip("\n").split("\t")
        if f[0] == "W":
            wins[(f[1], int(f[2]))] = (int(f[3]), float(f[4]), float(f[5]))
        else:
            rt, at = int(f[5]), int(f[6])
            if rt + at >= 20:
                sites[(f[1], (int(f[2]) - 1) // 3_000_000)].append(at / (rt + at))
    with open(out, "w") as w:
        w.write("chrom\tstart\tend\tblood_depth\ttumor_depth\tratio\tmaf\tn_het\tstate\n")
        for (c, s), (e, db, dt) in sorted(wins.items()):
            v = sites.get((c, s // 3_000_000), [])
            maf = median(min(x, 1 - x) for x in v) if len(v) >= 5 else None
            ratio = dt / db if db else None
            w.write(f"{c}\t{s}\t{e}\t{db}\t{dt}\t{ratio}\t{maf}\t{len(v)}\t{state(ratio, maf)}\n")


def phase_one(job):
    chrom, pos, ref, alt, st = job
    import pysam
    lines = subprocess.run([sys.executable, __file__, "baf-window", chrom, str(max(0, pos - 10_000)), str(pos + 10_000)], capture_output=True, text=True).stdout
    hets = []
    for line in lines.splitlines():
        f = line.split("\t")
        if f[0] == "S" and int(f[2]) != pos:
            rt, at = int(f[5]), int(f[6])
            if rt + at >= 20:
                hets.append((int(f[2]), at / (rt + at)))
    base = dict(chrom=chrom, pos=pos, state=st, n_het=len(hets))
    if not hets:
        return {**base, "result": "no_het"}
    hets = sorted(hets, key=lambda x: abs(x[0] - pos))[:8]
    tally = defaultdict(lambda: [0, 0])  # het pos -> reads with the SNV alt on the het ref / alt allele
    other = defaultdict(lambda: [0, 0])  # the same for reads without the SNV alt
    refseq = pysam.FastaFile(REF)
    het_alleles = {}
    with pysam.AlignmentFile(TUMOR, "rc", reference_filename=REF) as bam:
        for read in bam.fetch(chrom, pos - 1, pos):
            if read.is_secondary or read.is_supplementary or read.is_duplicate or read.mapping_quality < 20:
                continue
            pairs = {r: q for q, r in read.get_aligned_pairs(matches_only=True)}
            q = pairs.get(pos - 1)
            if q is None:
                continue
            carrying = read.query_sequence[q] == alt
            for h, _ in hets:
                qh = pairs.get(h - 1)
                if qh is None:
                    continue
                r_h = refseq.fetch(chrom, h - 1, h).upper()
                is_ref = read.query_sequence[qh] == r_h
                (tally if carrying else other)[h][0 if is_ref else 1] += 1
    votes = []
    for h, af in hets:
        a, b = tally[h]
        if a + b < 3 or max(a, b) / (a + b) < .8:
            continue
        on_alt = b > a
        votes.append(af if on_alt else 1 - af)
    if not votes:
        return {**base, "result": "unlinked"}
    votes.sort()
    return {**base, "result": "linked", "allele_share": round(votes[len(votes) // 2], 3), "n_linked_het": len(votes)}


def phase_snv(vcf, windows, out):
    import csv
    import random
    from multiprocessing import Pool
    table = {}
    for r in csv.DictReader(open(windows), delimiter="\t"):
        table[(r["chrom"], int(r["start"]))] = r["state"]
    def nearest(chrom, pos):
        s = (pos - 1_000_000) // 3_000_000 * 3_000_000 + 1_000_000
        return table.get((chrom, s), "NA")
    calls = subprocess.run(["bcftools", "query", "-f", "%CHROM\t%POS\t%REF\t%ALT\n", "-i", 'FILTER="PASS"', vcf], capture_output=True, text=True).stdout
    by = defaultdict(list)
    for line in calls.splitlines():
        c, p, r, a = line.split("\t")
        if c in FAI_CHROMS and len(r) == 1 and len(a) == 1:
            st = nearest(c, int(p))
            if c == "chr1" and int(p) < 85_000_000:
                by["chr1p"].append((c, int(p), r, a, st))
            elif st == "2:1":
                by["2:1:" + c].append((c, int(p), r, a, st))
            else:
                by[st].append((c, int(p), r, a, st))
    random.seed(829)
    jobs = list(by.pop("chr1p", []))
    for k, v in by.items():
        n = 300 if k.startswith("2:1:") else (400 if k == "2:2" else (200 if k == "LOH" else 0))
        jobs += random.sample(v, min(n, len(v)))
    print(len(jobs), "SNVs", {k: len(v) for k, v in by.items()}, flush=True)
    cols = ["chrom", "pos", "state", "n_het", "result", "allele_share", "n_linked_het"]
    with Pool(8) as pool, open(out, "w") as w:
        w.write("\t".join(cols) + "\n")
        for i, r in enumerate(pool.imap_unordered(phase_one, jobs, chunksize=4)):
            w.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
            if i % 200 == 0:
                w.flush()
                print(i, flush=True)


def main():
    cmd = sys.argv[1]
    if cmd == "baf-summary":
        baf_summary(sys.argv[2], sys.argv[3])
    if cmd == "phase-snv":
        phase_snv(sys.argv[2], sys.argv[3], sys.argv[4])
    if cmd == "coverage":
        coverage(sys.argv[2], sys.argv[3])
    elif cmd == "baf-regions":
        baf_regions(sys.argv[2])
    elif cmd == "baf-window":
        baf_window(*sys.argv[2:5])


if __name__ == "__main__":
    main()
