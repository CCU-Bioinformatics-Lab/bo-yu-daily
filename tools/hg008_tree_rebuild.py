#!/usr/bin/env python3
"""Rebuild the HG008 clone tree from the 8 clones' DeepSomatic SNVs and PURPLE copy number.

1. A clone carries an SNV when VAF >= MIN_VAF. An SNV with a weak call (0 < VAF < MIN_VAF) in any
   clone is set aside, so a weak call never counts as presence or absence. An SNV whose median QUAL
   among carriers is below MIN_QUAL is also set aside. QUAL is bimodal with a valley near 20, and
   about 2.4% of truncal SNVs (true by construction) fall below 20.
2. An SNV shared by 2-7 clones is "CN clean" when every clone without it has the carriers' copy
   number or more on both alleles and still holds both haplotypes (minor CN >= 1). PURPLE does not
   name the retained haplotype: two clones at 2+0 can hold different ones, so absence in an LOH
   state may be a lost allele, not a later origin. Such SNVs are counted as "absent_in_loh".
3. Among CN-clean SNVs, an exact dynamic program picks the set of pairwise compatible clades
   (nested or disjoint) with the most SNVs. Bootstrap resamples the SNVs.

Clades are candidates. The single-cell check (hg008_sc_tree_check.py) is the independent test.

Output (OUT_DIR):
  pattern_summary_<SET>.tsv  pattern, n_clones, n_snv, n_cn_clean, median VAF and QUAL of carriers
  clades_<SET>.tsv           chosen clades, CN-clean SNVs, bootstrap support
  tree_summary.tsv           SNV classes and share compatible with the chosen clades, per setting
  SET = vaf<MIN_VAF>_qual<MIN_QUAL>; the main setting is vaf0.25_qual20
  snv_classes_vaf0.25_qual20.tsv  every SNV of the main setting with its pattern and class

Usage: python3 -I tools/hg008_tree_rebuild.py HG008_DIR OUT_DIR
"""
import collections
import csv
import gzip
import random
import re
import statistics
import sys
from pathlib import Path

HG008 = Path(sys.argv[1])
OUT = Path(sys.argv[2])
CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
FULL = (1 << len(CLONES)) - 1
MAIN = re.compile(r"chr([0-9]+|X)$")
SETTINGS = [(0.25, 20), (0.25, 0), (0.25, 28), (0.15, 20), (0.35, 20)]
N_BOOT = 1000
SEED = 20261107


def read_calls(name):
    path = next((HG008 / "clones").rglob(f"HG008T-{name}.deepsomatic.vcf.gz"))
    calls = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.rstrip("\n").split("\t")
            if f[6] != "PASS" or len(f[3]) != 1 or len(f[4]) != 1 or not MAIN.match(f[0]):
                continue
            fmt = dict(zip(f[8].split(":"), f[9].split(":")))
            calls[(f[0], int(f[1]), f[3], f[4])] = (float(fmt["VAF"]), float(f[5]))
    return calls


def read_segments(name):
    path = next((HG008 / "clones").rglob(f"HG008T-{name}.purple.segment.tsv"))
    segs = collections.defaultdict(list)
    with open(path) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if int(r["depthWindowCount"]) == 0:
                continue
            alleles = sorted((max(0, round(float(r["minorAlleleCopyNumber"]))),
                              max(0, round(float(r["majorAlleleCopyNumber"])))))
            segs[r["chromosome"]].append((int(r["start"]), int(r["end"]), tuple(alleles)))
    return segs


def state_at(segs, chrom, pos):
    for start, end, state in segs.get(chrom, ()):
        if start <= pos <= end:
            return state
    return None


def cn_status(key, carriers, absent, segs):
    """'lost' (an absent clone has fewer copies than the carriers), 'absent_in_loh', 'no_cn' or 'clean'."""
    chrom, pos = key[0], key[1]
    states = [state_at(segs[c], chrom, pos) for c in carriers]
    known = [s for s in states if s]
    if not known:
        return "no_cn"
    modal = collections.Counter(known).most_common(1)[0][0]
    status = "clean"
    for c in absent:
        mine = state_at(segs[c], chrom, pos)
        if mine is None:
            status = "no_cn"
        elif mine[0] < modal[0] or mine[1] < modal[1]:
            return "lost"
        elif mine[0] == 0 and status == "clean":
            status = "absent_in_loh"
    return status


def lowest_bit(x):
    return x & -x


def best_laminar(weight):
    """Maximum-weight set of pairwise nested-or-disjoint clades, exact, over all clone subsets."""
    with_clade = [0] * (FULL + 1)  # the best set inside S, with S itself counted
    split = [0] * (FULL + 1)       # the best set inside S from a partition of S into 2+ blocks
    choice = [0] * (FULL + 1)
    for s in sorted(range(1, FULL + 1), key=lambda m: bin(m).count("1")):
        if s & (s - 1):
            low = lowest_bit(s)
            rest = s ^ low
            best, pick = -1, 0
            sub = rest
            while True:  # the block holding `low` is low + sub; sub == rest is S itself, so skip it
                sub = (sub - 1) & rest
                block = low | sub
                score = with_clade[block] + with_clade[s ^ block]
                if score > best:
                    best, pick = score, block
                if sub == 0:
                    break
            split[s], choice[s] = best, pick
        with_clade[s] = split[s] + weight.get(s, 0)
    chosen = []

    def walk(s):
        if not s & (s - 1):
            return
        if s != FULL and weight.get(s, 0):
            chosen.append(s)
        walk(choice[s])
        walk(s ^ choice[s])

    walk(FULL)
    return set(chosen)


def names(mask):
    return ",".join(c for i, c in enumerate(CLONES) if mask >> i & 1)


def compatible(a, b):
    return a & b == 0 or a & b == a or a & b == b


def analyse(calls, segs, min_vaf, min_qual):
    tag = f"vaf{min_vaf:.2f}_qual{min_qual}"
    rows = collections.defaultdict(lambda: {"n": 0, "clean": 0, "loh": 0, "chroms": set(), "vaf": [], "qual": []})
    classes = collections.Counter()
    snv_rows = []
    for key in sorted(set().union(*calls.values()), key=lambda k: (k[0], k[1])):
        got = {c: calls[c][key] for c in CLONES if key in calls[c]}
        if any(v < min_vaf for v, _ in got.values()):
            classes["weak_call_set_aside"] += 1
            continue
        if statistics.median(q for _, q in got.values()) < min_qual:
            classes["low_qual_set_aside"] += 1
            snv_rows.append((key, ",".join(c for c in CLONES if c in got), "low_qual"))
            continue
        mask = sum(1 << i for i, c in enumerate(CLONES) if c in got)
        row = rows[mask]
        row["n"] += 1
        row["vaf"].append(statistics.median(v for v, _ in got.values()))
        row["qual"].append(statistics.median(q for _, q in got.values()))
        size = bin(mask).count("1")
        if mask == FULL:
            classes["truncal"] += 1
            snv_rows.append((key, names(mask), "truncal"))
        elif size == 1:
            classes["private"] += 1
            snv_rows.append((key, names(mask), "private"))
        else:
            status = cn_status(key, list(got), [c for c in CLONES if c not in got], segs)
            classes["shared_" + status] += 1
            snv_rows.append((key, names(mask), "shared_" + status))
            if status == "clean":
                row["clean"] += 1
                row["chroms"].add(key[0])
            elif status == "absent_in_loh":
                row["loh"] += 1

    if (min_vaf, min_qual) == SETTINGS[0]:
        with open(OUT / f"snv_classes_{tag}.tsv", "w") as out:
            out.write("chrom\tpos\tref\talt\tpattern\tclass\n")
            for key, pattern, kind in snv_rows:
                out.write(f"{key[0]}\t{key[1]}\t{key[2]}\t{key[3]}\t{pattern}\t{kind}\n")
    weight = {m: r["clean"] for m, r in rows.items() if 2 <= bin(m).count("1") <= 7 and r["clean"]}
    chosen = best_laminar(weight)
    pool = [m for m, n in weight.items() for _ in range(n)]
    rng = random.Random(SEED)
    support = collections.Counter()
    for _ in range(N_BOOT):
        support.update(best_laminar(collections.Counter(rng.choices(pool, k=len(pool)))))
    in_tree = sum(weight[m] for m in chosen)
    conflicts = {m: n for m, n in weight.items() if any(not compatible(m, c) for c in chosen)}
    ceiling = max(conflicts.values(), default=0)

    with open(OUT / f"pattern_summary_{tag}.tsv", "w") as out:
        out.write("pattern\tn_clones\tn_snv\tn_cn_clean\tn_absent_in_loh\tin_chosen_tree\tmedian_vaf\tmedian_qual\n")
        for m, r in sorted(rows.items(), key=lambda x: -x[1]["n"]):
            out.write(f"{names(m)}\t{bin(m).count('1')}\t{r['n']}\t{r['clean']}\t{r['loh']}\t{int(m in chosen)}\t"
                      f"{statistics.median(r['vaf']):.2f}\t{statistics.median(r['qual']):.1f}\n")
    with open(OUT / f"clades_{tag}.tsv", "w") as out:
        out.write("clade\tn_clones\tn_cn_clean\tn_chromosomes\tbootstrap\tabove_conflict_ceiling\n")
        for m in sorted(chosen, key=lambda x: (-bin(x).count("1"), -weight[x])):
            out.write(f"{names(m)}\t{bin(m).count('1')}\t{weight[m]}\t{len(rows[m]['chroms'])}\t{support[m] / N_BOOT:.3f}\t"
                      f"{int(weight[m] > ceiling)}\n")
    total = sum(weight.values())
    return {"setting": tag, **classes, "shared_clean_total": total, "in_chosen_clades": in_tree,
            "conflicting_chosen": sum(conflicts.values()), "largest_conflicting_pattern": ceiling,
            "n_chosen_clades": len(chosen)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    calls = {c: read_calls(c) for c in CLONES}
    segs = {c: read_segments(c) for c in CLONES}
    results = [analyse(calls, segs, v, q) for v, q in SETTINGS]
    fields = list(dict.fromkeys(k for r in results for k in r))
    with open(OUT / "tree_summary.tsv", "w") as out:
        out.write("field\t" + "\t".join(r["setting"] for r in results) + "\n")
        for f in fields[1:]:
            out.write(f + "\t" + "\t".join(str(r.get(f, 0)) for r in results) + "\n")


if __name__ == "__main__":
    main()
