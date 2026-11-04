#!/usr/bin/env python3
"""Step 2 of the HG008 clone-tree analysis: put truth-tree event types on real clone-tree branches.

Inputs: snv_patterns.tsv from tools/hg008_clone_tree.py, and each clone's PURPLE allele-specific
copy number (purity 0.99 in all 8 clones, so CN and VAF are read directly).

  B. HP split per branch, without a global haplotype orientation: inside one HiPhase phase block
     (DeepSomatic PS), two SNVs with GT 0|1 and 1|0 sit on different haplotypes. SNVs closer than
     CLUSTER_BP merge into one unit (clustered mutations share a haplotype). Per branch: the share
     of blocks with >= 2 units that hold both haplotypes, and that share under random placement.
  C. Branch CN events: per 1 Mb bin, the rounded (major, minor) CN of each clone. Clones that
     differ from the 8-clone mode carry an event. Runs of bins with one deviation pattern and one
     state change form an event: hap-specific gain (one allele up), cnLOH (total kept, minor -> 0),
     deletion (total down), or het kept (the other clones lost an allele after this clone split off).
  D. Mutation loss: SNVs carried by all clones but one; the missing clone's CN at the SNV.
  E. CN timing on a subclone branch: private SNVs inside that clone's own gain or cnLOH events;
     multiplicity = round(VAF x total CN).

Usage: python3 -I tools/hg008_clone_events.py HG008_DIR TABLE_DIR
"""
import collections
import csv
import statistics
import sys
from pathlib import Path

HG008 = Path(sys.argv[1])
TAB = Path(sys.argv[2])
CLONES = ["2D6", "2E6", "3E4", "SC14", "SC24", "SC28", "SC6", "SC9"]
BIN = 1_000_000
MIN_BRANCH_SNV = 20
MIN_EVENT_MB = 1
CLUSTER_BP = 1_000


def purple_segments(name):
    path = next((HG008 / "clones").rglob(f"HG008T-{name}.purple.segment.tsv"))
    segs = collections.defaultdict(list)
    with open(path) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if int(r["depthWindowCount"]) == 0:
                continue
            major = round(float(r["majorAlleleCopyNumber"]))
            minor = max(0, round(float(r["minorAlleleCopyNumber"])))
            segs[r["chromosome"]].append((int(r["start"]), int(r["end"]), major, minor))
    return segs


def state_at(segs, chrom, pos):
    for s, e, ma, mi in segs.get(chrom, ()):
        if s <= pos <= e:
            return (ma, mi)
    return None


def classify(base, new):
    (bM, bm), (nM, nm) = base, new
    if min(bM, bm) == 0 < min(nM, nm):
        return "het kept (LOH in other clones)"
    if nM + nm > bM + bm and min(nM, nm) >= min(bM, bm):
        return "hap-specific gain" if (nM - bM == 0 or nm - bm == 0 or nM + nm - bM - bm == 1) else "gain (both alleles)"
    if nM + nm == bM + bm and min(nM, nm) == 0 < min(bM, bm):
        return "cnLOH"
    if nM + nm < bM + bm:
        return "deletion" if min(nM, nm) < min(bM, bm) else "loss (other)"
    return "other"


def load_snvs():
    with open(TAB / "snv_patterns.tsv") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def units(gts_pos):
    """Merge SNVs closer than CLUSTER_BP (kataegis-like clusters) into one unit with the majority GT."""
    out, cur = [], []
    for pos, gt in sorted(gts_pos):
        if cur and pos - cur[-1][0] > CLUSTER_BP:
            out.append(cur)
            cur = []
        cur.append((pos, gt))
    if cur:
        out.append(cur)
    res = []
    for u in out:
        a = sum(g == "0|1" for _, g in u)
        if 2 * a != len(u):
            res.append("0|1" if 2 * a > len(u) else "1|0")
    return res


def hp_split(snvs, branches):
    """B: per branch, phase blocks with >= 2 SNV units; observed vs random share with both haplotypes."""
    rows = []
    for pattern in branches:
        members = pattern.split(",")
        clone = members[0]
        ci = CLONES.index(clone)
        blocks = collections.defaultdict(list)
        n_phased = 0
        for s in snvs:
            if s["pattern"] != pattern:
                continue
            gt, ps = s["gt"].split(",")[ci], s["ps"].split(",")[ci]
            if gt in ("0|1", "1|0") and ps != ".":
                n_phased += 1
                blocks[(s["chrom"], ps)].append((int(s["pos"]), gt))
        multi = mixed = 0
        expected = 0.0
        for members_ in blocks.values():
            gts = units(members_)
            if len(gts) < 2:
                continue
            multi += 1
            mixed += len(set(gts)) == 2
            expected += 1 - 2 * 0.5 ** len(gts)
        n_branch = sum(s["pattern"] == pattern for s in snvs)
        rows.append([pattern, len(members), n_branch, clone, n_phased, multi, mixed,
                     f"{mixed / multi:.2f}" if multi else "NA", f"{expected / multi:.2f}" if multi else "NA"])
    with open(TAB / "branch_hp_split.tsv", "w") as out:
        out.write("branch\tn_clones\tn_snv\tphased_in_clone\tn_phased\tblocks_ge2_units\tblocks_both_hp\t"
                  "obs_frac_both_hp\trandom_frac_both_hp\n")
        for r in rows:
            out.write("\t".join(map(str, r)) + "\n")


def cn_events(segs):
    """C: clone-deviation events on 1 Mb bins."""
    chroms = [f"chr{i}" for i in range(1, 23)] + ["chrX"]
    events = []
    for chrom in chroms:
        end = max((e for c in CLONES for _, e, _, _ in segs[c].get(chrom, ())), default=0)
        run = None
        for b in range(0, end, BIN):
            mid = b + BIN // 2
            st = {c: state_at(segs[c], chrom, mid) for c in CLONES}
            if any(v is None for v in st.values()):
                key = None
            else:
                mode, n_mode = collections.Counter(st.values()).most_common(1)[0]
                dev = tuple(c for c in CLONES if st[c] != mode)
                key = (dev, mode, tuple(st[c] for c in dev)) if dev and n_mode >= 4 else None
            if run and key == run[0]:
                run[2] = b + BIN
                continue
            if run and run[0]:
                events.append((chrom, run[1], run[2], run[0]))
            run = [key, b, b + BIN]
        if run and run[0]:
            events.append((chrom, run[1], run[2], run[0]))
    rows = []
    for chrom, s, e, (dev, mode, states) in events:
        if (e - s) / 1e6 < MIN_EVENT_MB:
            continue
        kinds = {classify(mode, st) for st in states}
        kind = kinds.pop() if len(kinds) == 1 else "mixed"
        rows.append((chrom, s, e, ",".join(dev), f"{mode[0]}+{mode[1]}",
                     ",".join(f"{a}+{b}" for a, b in states), kind))
    with open(TAB / "branch_cn_events.tsv", "w") as out:
        out.write("chrom\tstart\tend\tclones_deviating\tother_clones_state\tdeviating_state\tevent\n")
        for r in rows:
            out.write("\t".join(map(str, r)) + "\n")
    return rows


def mutation_loss(snvs, segs):
    """D: SNVs in all clones but one, and the missing clone's CN change at the site."""
    out_rows = collections.Counter()
    for s in snvs:
        members = s["pattern"].split(",")
        if len(members) != len(CLONES) - 1:
            continue
        miss = next(c for c in CLONES if c not in members)
        pos = int(s["pos"])
        others = collections.Counter(state_at(segs[c], s["chrom"], pos) for c in members).most_common(1)[0][0]
        mine = state_at(segs[miss], s["chrom"], pos)
        if mine is None or others is None:
            kind = "no CN"
        elif mine == others:
            kind = "same CN as other clones"
        else:
            kind = classify(others, mine)
        out_rows[(miss, kind)] += 1
    with open(TAB / "mutation_loss.tsv", "w") as out:
        out.write("missing_clone\tcn_change_in_missing_clone\tn_snv\n")
        for (miss, kind), n in sorted(out_rows.items()):
            out.write(f"{miss}\t{kind}\t{n}\n")


def cn_timing(snvs, segs, events):
    """E: multiplicity of each clone's private SNVs inside its own gain / cnLOH events."""
    own = collections.defaultdict(list)
    for chrom, s, e, dev, _, states, kind in events:
        if kind in ("hap-specific gain", "cnLOH") and "," not in dev:
            own[dev].append((chrom, s, e, kind))
    counts = collections.Counter()
    for snv in snvs:
        clone = snv["pattern"]
        if clone not in own:
            continue
        pos = int(snv["pos"])
        for chrom, s, e, kind in own[clone]:
            if snv["chrom"] == chrom and s <= pos < e:
                st = state_at(segs[clone], chrom, pos)
                vaf = float(snv["vafs"].split(",")[CLONES.index(clone)])
                mult = max(1, round(vaf * sum(st)))
                counts[(clone, kind, f"{st[0]}+{st[1]}", mult)] += 1
    with open(TAB / "subclone_cn_timing.tsv", "w") as out:
        out.write("clone\tevent\tstate\tmultiplicity\tn_private_snv\n")
        for k, n in sorted(counts.items()):
            out.write("\t".join(map(str, k)) + f"\t{n}\n")


def main():
    snvs = load_snvs()
    pat_n = collections.Counter(s["pattern"] for s in snvs)
    branches = [p for p, n in pat_n.most_common() if n >= MIN_BRANCH_SNV]
    segs = {c: purple_segments(c) for c in CLONES}
    hp_split(snvs, branches)
    events = cn_events(segs)
    mutation_loss(snvs, segs)
    cn_timing(snvs, segs, events)


if __name__ == "__main__":
    main()
