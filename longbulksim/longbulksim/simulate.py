"""Run one simulation and write method inputs and truth to separate directories.

OUT/input/  what a method may read (plan.md §5.8.2 rule 7)
  data.tsv       PhyClone input; major/minor = tumour CN state with the most cells
  data_hp.tsv    data.tsv + observed HP columns for tools/phyclone_hp.py; snv_hp is the HP
                 with more tagged alt reads ("." when there are none)
  segments.tsv   per segment: root-clone state A, other state B, true phi (cells in B)
  pairs.tsv      per SNV pair x HP: tagged reads that cover both SNVs, by allele pattern
                 (plan.md §1.3 PAIRS.tsv; ps_block = segment; phase switches stay inside it)
Counts, snv_hp and pairs use the observed HP tag and observed alleles, so mistags, phase
switches and base errors reach every input file the same way.
OUT/truth/
  truth.tsv, truth_tree.tsv, clusters_truth.tsv  same columns as tools/hp_truth_tree_to_phyclone.py
  genome.json    replayed genome: lineage -> segment -> HP -> copies (sorted role lists)
  reads.tsv.gz   every read: segment, start, end, lineage, HP, copy, tagged, observed HP
  phase_switches.tsv  phase switch positions
OUT/manifest.json  spec, seed, read-span source and counts
"""
import gzip
import json
from pathlib import Path

import numpy as np
from scipy.stats import binom

from . import __version__
from .model import HPS, NORMAL, lost, replay
from .sample import load_read_span, place_mutations, sample_segment

SAMPLE = "S1"


def cn_state(genome, seg):
    return tuple(len(genome[seg][h]) for h in HPS)


def dominant_state(spec, genomes, seg):
    w = {}
    for c, f in spec.fraction.items():
        st = cn_state(genomes[c], seg)
        w[st] = w.get(st, 0) + f
    return max(w, key=w.get)


def segment_states(spec, genomes, seg):
    a = cn_state(genomes[spec.root], seg)
    others = {cn_state(genomes[c], seg) for c in spec.fraction} - {a}
    if len(others) > 1:
        raise ValueError(f"segment {seg} has more than two tumour CN states; "
                         "segments.tsv cannot express it")
    b = others.pop() if others else a
    phi = sum(f for c, f in spec.fraction.items() if cn_state(genomes[c], seg) == b) if b != a else 0
    return a, b, phi


def phyclone_ccf(ref, alt, major, minor, t, normal_cn=2, err=1e-3):
    """Per-SNV MLE of f under PhyClone's genotype prior and binomial likelihood
    (copied from tools/draw_hp_truth_tree.py, which mirrors phyclone/data/pyclone.py)."""
    total = major + minor
    cn = [(normal_cn, normal_cn, total) for _ in range(1, major + 1)]
    mu = [(err, err, min(1 - err, x / total)) for x in range(1, major + 1)]
    if total != normal_cn:
        cn.append((normal_cn, total, total))
        mu.append((err, err, min(1 - err, 1 / total)))
    cn, mu = np.array(cn, float), np.array(mu, float)
    fs = np.linspace(0, 1, 401)
    ll = []
    for f in fs:
        e_cn = cn * np.array([1 - t, t * (1 - f), t * f])
        vaf = (e_cn * mu).sum(1) / e_cn.sum(1)
        ll.append(np.logaddexp.reduce(binom.logpmf(alt, ref + alt, vaf)) - np.log(len(cn)))
    return fs[int(np.argmax(ll))]


def role_truth(spec, genomes, role):
    r = spec.roles[role]
    cw = spec.cell_weight()
    tot = sum(w * sum(cn_state(genomes[c], r.segment)) for c, w in cw.items())
    alt = sum(w * sum(role in cp for cp in genomes[c][r.segment][r.hp]) for c, w in cw.items())
    carrier = sum(f for c, f in spec.fraction.items()
                  if any(role in cp for cp in genomes[c][r.segment][r.hp]))
    dom = dominant_state(spec, genomes, r.segment)
    dp = spec.depth * tot / 2
    a = round(dp * alt / tot)
    f_exp = phyclone_ccf(round(dp) - a, a, max(dom), min(dom), spec.purity)
    return {"origin_ccf": spec.ccf(r.clone), "carrier_fraction": carrier,
            "phyclone_ccf_expected": f_exp, "vaf_expected": alt / tot}


def observe(reads, pos, role, rng=None, base_error=0.0):
    """Reads that cover pos and whether each one reads the alt allele."""
    idx = reads.covering(pos)
    alt = reads.carries(role)[reads.mol[idx]]
    if base_error > 0:
        alt = alt ^ (rng.random(len(idx)) < base_error)
    return idx, alt


def counts(reads, idx, alt):
    hp = reads.obs_hp[idx]
    tag = reads.tagged[idx]
    c = {"ref": int((~alt).sum()), "alt": int(alt.sum())}
    for h in HPS:
        sel = tag & (hp == h)
        c[f"ref_{h.lower()}"] = int((~alt & sel).sum())
        c[f"alt_{h.lower()}"] = int((alt & sel).sum())
    c["ref_unphased"] = int((~alt & ~tag).sum())
    c["alt_unphased"] = int((alt & ~tag).sum())
    return c


def pair_rows(spec, reads, muts, obs):
    """Tagged reads that cover both SNVs of a pair, per HP; pairs ordered by mutation id."""
    seg = spec.segments[muts[0].segment]
    muts = sorted(muts, key=lambda m: m.pos)
    rows = []
    for i, mi in enumerate(muts):
        for mj in muts[i + 1:]:
            if mj.pos - mi.pos >= reads.max_span:
                break
            (ii, ai), (ij, aj) = obs[mi.id], obs[mj.id]
            both, ki, kj = np.intersect1d(ii, ij, assume_unique=True, return_indices=True)
            if not len(both):
                continue
            a, b = (mi, mj) if mi.id < mj.id else (mj, mi)
            xa, xb = (ai[ki], aj[kj]) if a is mi else (aj[kj], ai[ki])
            tag, hp = reads.tagged[both], reads.obs_hp[both]
            for h in HPS:
                sel = tag & (hp == h)
                if not sel.any():
                    continue
                n = [int((xa[sel] & xb[sel]).sum()), int((xa[sel] & ~xb[sel]).sum()),
                     int((~xa[sel] & xb[sel]).sum()), int((~xa[sel] & ~xb[sel]).sum())]
                rows.append([a.id, b.id, SAMPLE, seg.chrom, seg.id, h, *n, sum(n),
                             abs(a.pos - b.pos)])
    return rows


def write_tsv(path, header, rows):
    with open(path, "w") as fh:
        fh.write("\t".join(header) + "\n")
        fh.writelines("\t".join(map(str, r)) + "\n" for r in rows)


def run(spec, seed, out_dir):
    out = Path(out_dir)
    (out / "input").mkdir(parents=True, exist_ok=True)
    (out / "truth").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    genomes = replay(spec)
    span_q = load_read_span(spec.read_span)
    muts = place_mutations(rng, spec)
    reads = {s: sample_segment(rng, spec, genomes, s, span_q) for s in spec.segments}
    obs = {m.id: observe(reads[m.segment], m.pos, m.role, rng, spec.base_error) for m in muts}
    truth = {r: role_truth(spec, genomes, r) for r in spec.roles}

    base = ["mutation_id", "sample_id", "ref_counts", "alt_counts", "major_cn", "minor_cn",
            "normal_cn", "tumour_content"]
    hp_cols = ["snv_hp", "segment_id", "cn_hp1", "cn_hp2", "ref_hp1", "alt_hp1", "ref_hp2",
               "alt_hp2", "ref_unphased", "alt_unphased"]
    data, data_hp = [], []
    for m in muts:
        c = counts(reads[m.segment], *obs[m.id])
        dom = dominant_state(spec, genomes, m.segment)
        row = [m.id, SAMPLE, c["ref"], c["alt"], max(dom), min(dom), 2, spec.purity]
        snv_hp = ("." if c["alt_hp1"] == c["alt_hp2"] else
                  "HP1" if c["alt_hp1"] > c["alt_hp2"] else "HP2")
        data.append(row)
        data_hp.append(row + [snv_hp, m.segment, *dom] +
                       [c[k] for k in hp_cols[4:]])
    write_tsv(out / "input/data.tsv", base, data)
    write_tsv(out / "input/data_hp.tsv", base + hp_cols, data_hp)

    seg_rows = []
    for s in spec.segments:
        a, b, phi = segment_states(spec, genomes, s)
        seg_rows.append([s, SAMPLE, *a, *b, f"{phi:.4f}"])
    write_tsv(out / "input/segments.tsv",
              ["segment_id", "sample_id", "a_hp1", "a_hp2", "b_hp1", "b_hp2", "phi"], seg_rows)

    pairs = []
    for s in spec.segments:
        seg_muts = [m for m in muts if m.segment == s]
        if seg_muts:
            pairs += pair_rows(spec, reads[s], seg_muts, obs)
    write_tsv(out / "input/pairs.tsv",
              ["mutation_i", "mutation_j", "sample_id", "chrom", "ps_block", "hap", "n11",
               "n10", "n01", "n00", "callable_pair_reads", "distance"], pairs)

    roles = spec.roles
    write_tsv(out / "truth/truth.tsv",
              ["mutation_id", "role", "origin_clone", "hp", "segment", "chrom", "pos",
               "origin_ccf", "carrier_fraction", "phyclone_ccf_expected", "vaf_expected"],
              [[m.id, m.role, roles[m.role].clone, roles[m.role].hp, m.segment,
                spec.segments[m.segment].chrom, m.pos,
                *(f"{truth[m.role][k]:.4f}" for k in ("origin_ccf", "carrier_fraction",
                                                       "phyclone_ccf_expected", "vaf_expected"))]
               for m in muts])
    write_tsv(out / "truth/clusters_truth.tsv", ["mutation_id", "cluster_id"],
              [[m.id, roles[m.role].clone] for m in muts])
    write_tsv(out / "truth/truth_tree.tsv",
              ["clone", "parent", "sample_id", "purity", "clone_fraction", "ccf"],
              [[c, p or "root", SAMPLE, spec.purity, f"{spec.fraction[c]:.2f}",
                f"{spec.ccf(c):.2f}"] for c, p in spec.parent.items()])
    (out / "truth/genome.json").write_text(json.dumps(
        {"genome": {c: {s: {h: [sorted(cp) for cp in cps] for h, cps in seg.items()}
                        for s, seg in g.items()} for c, g in genomes.items()},
         "lost": lost(spec, genomes)}, indent=1))
    with gzip.open(out / "truth/reads.tsv.gz", "wt") as fh:
        fh.write("read_id\tsegment\tstart\tend\tlineage\thp\tcopy\ttagged\tobs_hp\n")
        for s, r in reads.items():
            for i in range(len(r.start)):
                m = r.molecules[r.mol[i]]
                fh.write(f"{s}_{i}\t{s}\t{r.start[i]}\t{r.end[i]}\t{m.lineage}\t{m.hp}\t"
                         f"{m.copy}\t{int(r.tagged[i])}\t{r.obs_hp[i]}\n")
    write_tsv(out / "truth/phase_switches.tsv", ["segment", "pos"],
              [[s, int(p)] for s, r in reads.items() for p in r.switches])

    manifest = {"longbulksim_version": __version__, "spec": spec.name, "seed": seed,
                "purity": spec.purity, "depth": spec.depth,
                "phased_fraction": spec.phased_fraction, "mistag_rate": spec.mistag_rate,
                "switch_rate_per_mb": spec.switch_rate_per_mb, "base_error": spec.base_error,
                "read_span": str(spec.read_span),
                "n_mutations": len(muts), "n_pairs_rows": len(pairs),
                "n_reads": {s: int(len(r.start)) for s, r in reads.items()},
                "lineages": [NORMAL, *spec.parent]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest
