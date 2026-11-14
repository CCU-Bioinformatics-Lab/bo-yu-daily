"""HG008 (2026-11-13): ClairS PASS SNVs in NIST 1+1 segments -> haploclone input with per-HP read counts.

D1 ClairS PASS, D2 haplotag at the SNV site, D3 1+1 only, D4 ONT 63x (user decided 2026-11-13).
Writes to OUT_DIR:
  data.tsv     PhyClone format (base): all reads at the site, CN 1/1, tumour_content 1.0
  data_hp.tsv  + snv_hp, cn_hp1, cn_hp2, ref/alt per HP, ref/alt unphased (A1)
  labels.tsv   mutation_id, reference-tree layer (truncal / L111 / L48 / L16 / other_clade / none), never given to haploclone
A read gets HP1/HP2 when it covers >= 2 phased germline het SNVs of HG008-N within +-20 kb and >= 70% agree.
Run from repo root: python3 -I lab_report/2026-11-13_hg008_bulk_rebuild/build_input.py OUT_DIR [--jobs 24]
  PacBio (2026-11-14): add --bam .../PacBio/HG008.bam --clairs /bip8_disk/boyu114/hg008_clairs_pacbio/out/output.vcf.gz --sample HG008_p23_PacBio"""
import argparse, bisect, collections as co, csv, gzip, statistics as st
from multiprocessing import Pool
from pathlib import Path
import pysam

CL = '/bip8_disk/boyu114/hg008_clairs_ont/out/output.vcf.gz'
BAM = '/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'
NIST = '/big8_disk/yungjen114/data/HG008/NIST/somatic-smvar_v0.4_20261006/GRCh38/'
FULL = NIST + 'HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_full_tumornormal.vcf.gz'
CNV = ('/big8_disk/yungjen114/data/HG008/NIST/somatic-stvar-CNV_v0.6_20261006/GRCh38/'
       'GRCh38_HG008-T-V0.6_somatic-CNV_PASS.draftbenchmark.calls.bed')
TAB = 'lab_report/2026-11-07_hg008_tree_rebuild/tables/snv_classes_vaf0.25_qual20.tsv'
WIN, MIN_INF, AGREE, MAPQ = 20_000, 2, 0.7, 20
LAYERS = {'2D6,2E6,3E4,SC14,SC24,SC28,SC6,SC9': 'truncal', '2D6,2E6,SC14,SC24,SC28,SC6,SC9': 'L111',
          'SC14,SC24,SC28,SC9': 'L48', 'SC14,SC28': 'L16'}


def one_one():
    seg = co.defaultdict(list)
    for l in open(CNV):
        f = l.rstrip('\n').split('\t')
        if f[4] == '1' and f[5] == '1':
            seg[f[0]].append((int(f[1]), int(f[2])))
    for k in seg:
        seg[k].sort()
    return seg


def inside(seg, c, p):
    iv = seg.get(c, [])
    i = bisect.bisect_right([s for s, _ in iv], p - 1) - 1
    return i >= 0 and iv[i][0] <= p - 1 < iv[i][1]


def hets(vcf, c, lo, hi):
    """Phased germline het SNVs of HG008-N: pos(0-based) -> (base on HP1, base on HP2)."""
    out = {}
    for r in vcf.fetch(c, max(0, lo), hi):
        if len(r.ref) != 1 or len(r.alts or ()) != 1 or len(r.alts[0]) != 1:
            continue
        s = r.samples['HG008-N']
        gt = s['GT']
        if not s.phased or gt is None or sorted(gt) != [0, 1]:
            continue
        al = (r.ref, r.alts[0])
        out[r.pos - 1] = (al[gt[0]], al[gt[1]])
    return out


def count(site):
    c, pos, ref, alt = site[:4]
    BAM = site[4]
    bam, vcf = pysam.AlignmentFile(BAM), pysam.VariantFile(FULL)
    h = hets(vcf, c, pos - 1 - WIN, pos + WIN)
    n = {k: 0 for k in ('ref_hp1', 'alt_hp1', 'ref_hp2', 'alt_hp2', 'ref_unphased', 'alt_unphased')}
    for rd in bam.fetch(c, pos - 1, pos):
        if rd.is_unmapped or rd.is_secondary or rd.is_supplementary or rd.is_duplicate or rd.mapping_quality < MAPQ:
            continue
        seq, base, v1, v2 = rd.query_sequence, None, 0, 0
        for q, r in rd.get_aligned_pairs(matches_only=True):
            if r == pos - 1:
                base = seq[q]
            elif r in h and abs(r - (pos - 1)) <= WIN:
                b = seq[q]
                v1 += b == h[r][0]
                v2 += b == h[r][1]
        if base not in (ref, alt):
            continue
        tot = v1 + v2
        hp = ('hp1' if v1 / tot >= AGREE else 'hp2' if v2 / tot >= AGREE else 'unphased') if tot >= MIN_INF else 'unphased'
        n[('ref_' if base == ref else 'alt_') + hp] += 1
    return site, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    ap.add_argument('--jobs', type=int, default=24)
    ap.add_argument('--bam', default=BAM)
    ap.add_argument('--clairs', default=CL)
    ap.add_argument('--sample', default='HG008_p23_ONT')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    seg = one_one()
    sites = []
    for l in gzip.open(a.clairs, 'rt'):
        if l[0] == '#':
            continue
        f = l.split('\t')
        if f[6] == 'PASS' and len(f[3]) == 1 == len(f[4]) and inside(seg, f[0], int(f[1])):
            sites.append((f[0], int(f[1]), f[3], f[4], a.bam))
    pat = {}
    for l in open(TAB):
        f = l.rstrip('\n').split('\t')
        if f[0] != 'chrom' and f[5] != 'low_qual':
            pat[(f[0], int(f[1]), f[2], f[3])] = ','.join(sorted(f[4].split(',')))
    print(f'ClairS PASS SNVs in 1+1: {len(sites)}', flush=True)
    with Pool(a.jobs) as pool:
        res = pool.map(count, sites, chunksize=20)
    base_cols = ['mutation_id', 'sample_id', 'ref_counts', 'alt_counts', 'major_cn', 'minor_cn', 'normal_cn', 'tumour_content']
    hp_cols = base_cols + ['snv_hp', 'cn_hp1', 'cn_hp2', 'ref_hp1', 'alt_hp1', 'ref_hp2', 'alt_hp2', 'ref_unphased', 'alt_unphased']
    base, hp, lab, drop = [], [], [], 0
    for (c, pos, r, al, _), n in res:
        refc = n['ref_hp1'] + n['ref_hp2'] + n['ref_unphased']
        altc = n['alt_hp1'] + n['alt_hp2'] + n['alt_unphased']
        if altc == 0:
            drop += 1
            continue
        mid = f'{c}_{pos}_{r}_{al}'
        rec = {'mutation_id': mid, 'sample_id': a.sample, 'ref_counts': refc, 'alt_counts': altc,
               'major_cn': 1, 'minor_cn': 1, 'normal_cn': 2, 'tumour_content': 1.0}
        shp = 'HP1' if n['alt_hp1'] > n['alt_hp2'] else 'HP2' if n['alt_hp2'] > n['alt_hp1'] else 'NA'
        base.append(rec)
        hp.append({**rec, 'snv_hp': shp, 'cn_hp1': 1, 'cn_hp2': 1, **n})
        p = pat.get((c, pos, r, al))
        lab.append({'mutation_id': mid, 'layer': LAYERS.get(p, 'other_clade') if p else 'none', 'pattern': p or ''})
    for name, cols, rows in (('data.tsv', base_cols, base), ('data_hp.tsv', hp_cols, hp),
                             ('labels.tsv', ['mutation_id', 'layer', 'pattern'], lab)):
        with open(a.out / name, 'w', newline='') as fh:
            w = csv.DictWriter(fh, cols, delimiter='\t')
            w.writeheader()
            w.writerows(rows)
    vaf = lambda rows: [x['alt_counts'] / (x['ref_counts'] + x['alt_counts']) for x in rows]
    tr = [b for b, l in zip(base, lab) if l['layer'] == 'truncal']
    alt_tot = sum(x['alt_counts'] for x in base)
    alt_ph = sum(x['alt_hp1'] + x['alt_hp2'] for x in hp)
    print(f'kept {len(base)}, dropped (no alt read at MAPQ>={MAPQ}) {drop}')
    print('layers:', dict(co.Counter(l['layer'] for l in lab)))
    print(f'median depth {st.median(x["ref_counts"] + x["alt_counts"] for x in base)}; median VAF all {st.median(vaf(base)):.3f}; '
          f'truncal {st.median(vaf(tr)):.3f} (purity check: x2 = {2 * st.median(vaf(tr)):.2f})')
    print(f'alt reads phased {alt_ph / alt_tot:.1%}; snv_hp', dict(co.Counter(x['snv_hp'] for x in hp)))
    mixed = sum(x['alt_hp1'] > 0 and x['alt_hp2'] > 0 for x in hp)
    print(f'SNVs with alt reads on both HPs: {mixed}')


if __name__ == '__main__':
    main()
