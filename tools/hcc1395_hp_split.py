#!/usr/bin/env python3
"""Measure HP (haplotype) signals of real somatic SNVs in HCC1395 ONT reads.

Input: the haplotagged pure-tumour CRAM from tools/hcc1395_hp_split_prepare.sh, SEQC2 HighConf
somatic SNVs, and SEQC2 ASCAT allele-specific CN (consensus, as in seqc2_hcc1395_purity.py).

  A. HP assignment: per SNV, alt/ref reads on HP1 / HP2 / untagged. An SNV is assignable when
     >= MIN_ALT tagged alt reads and >= ASSIGN_FRAC of them on one HP.
  B. HP depth vs CN: minor-HP depth fraction min(HP1,HP2)/(HP1+HP2) by ASCAT (total, minor) CN.
     HP orientation is arbitrary per phase block, so only the minor fraction is used.
  C. Read co-occurrence: for adjacent SNV pairs, reads spanning both sites and reads with both
     ALT alleles.

Usage: python3 -I tools/hcc1395_hp_split.py [CRAM] [OUT_DIR]
"""
import collections
import os
import statistics
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seqc2_hcc1395_purity as P  # noqa: E402

CRAM = sys.argv[1] if len(sys.argv) > 1 else "/big8_disk/boyu114/hcc1395_hp_split/tagged_t50_n00.cram"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "lab_report/2026-10-25_hcc1395_hp_split")
CHROMS = [f"chr{i}" for i in range(1, 23)] + ["chrX"]
MIN_ALT = 3          # tagged alt reads needed to call an HP
ASSIGN_FRAC = 0.9    # share of tagged alt reads on one HP
PAIR_MAX_DIST = 100_000


def parse_bases(s):
    """Split an mpileup base string into one token per read: 'ref', a base, or None (deletion)."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "^":
            i += 2
            continue
        if c == "$":
            i += 1
            continue
        if c in "+-":
            j = i + 1
            while s[j].isdigit():
                j += 1
            i = j + int(s[i + 1:j])
            continue
        out.append("ref" if c in ".," else (None if c in "*#" else c.upper()))
        i += 1
    return out


def pileup_chrom(args):
    chrom, sites_file, alt_of = args
    cmd = ["samtools", "mpileup", "-r", chrom, "-l", sites_file, "-f", P.REF, "-B", "-Q", "7", "-q", "20",
           "--ff", "UNMAP,SECONDARY,QCFAIL,DUP,SUPPLEMENTARY", "-d", "0", "--output-extra", "QNAME,HP", CRAM]
    res = {}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    for line in proc.stdout:
        f = line.rstrip("\n").split("\t")
        key = (f[0], f[1])
        if key not in alt_of or f[3] == "0":
            continue
        bases = parse_bases(f[4])
        names, hps = f[6].split(","), f[7].split(",")
        if not (len(bases) == len(names) == len(hps)):
            continue
        alt = alt_of[key]
        reads = {}
        for b, n, h in zip(bases, names, hps):
            if b is None:
                continue
            allele = "alt" if b == alt else ("ref" if b == "ref" else "other")
            reads[n] = (allele, h if h in ("1", "2") else "0")
        res[key] = reads
    proc.wait()
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tab = OUT / "tables"
    tab.mkdir(exist_ok=True)
    sites = P.load_sites()
    alt_of = {(c, p): a for c, p, _, a in sites}
    sites_file = OUT / "sites.tsv"
    sites_file.write_text("".join(f"{c}\t{p}\n" for c, p, _, _ in sites))
    cons = P.ascat_consensus(sites)
    with ProcessPoolExecutor(len(CHROMS)) as ex:
        reads = {}
        for r in ex.map(pileup_chrom, [(c, str(sites_file), alt_of) for c in CHROMS]):
            reads.update(r)
    sites_file.unlink()

    # A. HP assignment
    rows, summ = [], collections.Counter()
    alt_tagged = alt_total = 0
    for (c, p), rd in reads.items():
        cnt = collections.Counter(rd.values())
        a = {h: cnt[("alt", h)] for h in "120"}
        r = {h: cnt[("ref", h)] for h in "120"}
        at = a["1"] + a["2"]
        alt_tagged += at
        alt_total += at + a["0"]
        if at < MIN_ALT:
            call = "too few tagged alt"
        elif max(a["1"], a["2"]) / at >= ASSIGN_FRAC:
            call = "assigned"
        else:
            call = "split"
        summ[call] += 1
        tt, tm = cons.get((c, p), (None, None))
        rows.append((c, p, a["1"], a["2"], a["0"], r["1"], r["2"], r["0"], call, tt, tm))
    with open(tab / "per_snv_hp.tsv", "w") as f:
        f.write("chrom\tpos\talt_hp1\talt_hp2\talt_untagged\tref_hp1\tref_hp2\tref_untagged\tcall\tascat_total\tascat_minor\n")
        f.writelines("\t".join(map(str, x)) + "\n" for x in rows)
    n = len(rows)
    a_lines = [f"SNVs with pileup\t{n}",
               f"alt reads tagged (pooled)\t{alt_tagged / alt_total:.3f}"]
    a_lines += [f"{k}\t{v}\t{v / n:.3f}" for k, v in summ.most_common()]
    assigned = [x for x in rows if x[8] == "assigned"]
    hp1 = sum(1 for x in assigned if x[2] > x[3])
    a_lines.append(f"assigned HP1 : HP2\t{hp1} : {len(assigned) - hp1}")

    # B. minor-HP depth fraction by ASCAT CN (all reads at the site, tagged only)
    by_cn = collections.defaultdict(list)
    for x in rows:
        if x[9] is None:
            continue
        d1, d2 = x[2] + x[5], x[3] + x[6]
        if d1 + d2 >= 10:
            by_cn[(x[9], x[10])].append(min(d1, d2) / (d1 + d2))
    b_rows = []
    for (tt, tm), v in sorted(by_cn.items()):
        if len(v) < 100:
            continue
        exp = tm / tt if tt else float("nan")
        b_rows.append((tt, tm, len(v), f"{exp:.3f}", f"{statistics.median(v):.3f}",
                       f"{sum(1 for z in v if z < 0.1) / len(v):.3f}"))
    with open(tab / "hp_depth_by_cn.tsv", "w") as f:
        f.write("ascat_total\tascat_minor\tn_snv\texpected_minor_frac\tmedian_minor_hp_frac\tfrac_sites_minor_lt_0.1\n")
        f.writelines("\t".join(map(str, x)) + "\n" for x in b_rows)

    # C. co-occurrence for adjacent SNV pairs
    by_chr = collections.defaultdict(list)
    for (c, p) in reads:
        by_chr[c].append(int(p))
    dist_bins = [(0, 1_000), (1_000, 5_000), (5_000, 20_000), (20_000, 50_000), (50_000, PAIR_MAX_DIST)]
    pair_stats = {b: [] for b in dist_bins}
    cis_rows = []
    for c, ps in by_chr.items():
        ps.sort()
        for p1, p2 in zip(ps, ps[1:]):
            d = p2 - p1
            if d >= PAIR_MAX_DIST:
                continue
            r1, r2 = reads[(c, str(p1))], reads[(c, str(p2))]
            span = set(r1) & set(r2)
            both = sum(1 for q in span if r1[q][0] == "alt" and r2[q][0] == "alt")
            one = sum(1 for q in span if (r1[q][0] == "alt") != (r2[q][0] == "alt"))
            b = next(b for b in dist_bins if b[0] <= d < b[1])
            pair_stats[b].append(len(span))
            cis_rows.append((c, p1, p2, d, len(span), both, one))
    with open(tab / "snv_pairs.tsv", "w") as f:
        f.write("chrom\tpos1\tpos2\tdistance\tspanning_reads\treads_both_alt\treads_one_alt\n")
        f.writelines("\t".join(map(str, x)) + "\n" for x in cis_rows)
    n_adj = sum(len(ps) - 1 for ps in by_chr.values())
    c_lines = [f"adjacent SNV pairs (genome)\t{n_adj}",
               f"adjacent pairs < {PAIR_MAX_DIST // 1000} kb\t{len(cis_rows)}"]
    c_rows = []
    for b in dist_bins:
        v = pair_stats[b]
        if v:
            c_rows.append((f"{b[0] // 1000}-{b[1] // 1000} kb", len(v), statistics.median(v),
                           f"{sum(1 for z in v if z >= 1) / len(v):.3f}", f"{sum(1 for z in v if z >= 10) / len(v):.3f}"))
    with open(tab / "pair_spanning_by_distance.tsv", "w") as f:
        f.write("distance\tn_pairs\tmedian_spanning_reads\tfrac_ge1\tfrac_ge10\n")
        f.writelines("\t".join(map(str, x)) + "\n" for x in c_rows)
    informative = sum(1 for x in cis_rows if x[5] >= 1)
    c_lines.append(f"pairs with >=1 read carrying both ALT\t{informative}")
    c_lines.append(f"pairs with >=1 read carrying exactly one ALT\t{sum(1 for x in cis_rows if x[6] >= 1)}")

    (tab / "summary.txt").write_text("## A. HP assignment\n" + "\n".join(a_lines) +
                                     "\n\n## C. co-occurrence\n" + "\n".join(c_lines) + "\n")
    for name in ("summary.txt", "hp_depth_by_cn.tsv", "pair_spanning_by_distance.tsv"):
        print(f"### {name}\n{(tab / name).read_text()}")


if __name__ == "__main__":
    main()
