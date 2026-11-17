"""HG008 C4 input (2026-11-15, README §2): pairs.tsv (HP-tagged read patterns), data_hp.tsv + segment_id, segments.tsv.

Run from repo root (pysam is in the user site, so no -I):
python3 lab_report/2026-11-15_hg008_c4_rebuild/build_pairs.py /bip8_disk/boyu114/hg008_haploclone/c4 [--jobs 16]"""
import argparse, bisect, collections as co, csv
from multiprocessing import Pool
from pathlib import Path
import pysam

INP = Path('/bip8_disk/boyu114/hg008_haploclone/input')
BAM = '/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'
FULL = ('/big8_disk/yungjen114/data/HG008/NIST/somatic-smvar_v0.4_20261006/GRCh38/'
        'HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_full_tumornormal.vcf.gz')
MAXD, WIN, MIN_INF, AGREE, MAPQ = 100_000, 20_000, 2, 0.7, 20


def column(bam, c, pos0):
    """read name -> base at 0-based pos0."""
    out = {}
    for col in bam.pileup(c, pos0, pos0 + 1, truncate=True, min_mapping_quality=MAPQ, min_base_quality=0,
                          ignore_orphans=False, max_depth=100000):
        for pr in col.pileups:
            if not (pr.is_del or pr.is_refskip):
                out[pr.alignment.query_name] = pr.alignment.query_sequence[pr.query_position]
    return out


def window(job):
    """One merged window: per-SNV calls and per-read HP votes from germline hets within +-WIN of each SNV."""
    c, snvs = job   # snvs: [(pos1, ref, alt)]
    bam, vcf = pysam.AlignmentFile(BAM), pysam.VariantFile(FULL)
    calls = {}
    for p, ref, alt in snvs:
        col = column(bam, c, p - 1)
        calls[p] = {n: ('1' if b == alt else '0' if b == ref else None) for n, b in col.items()}
    het = {}
    lo, hi = min(p for p, _, _ in snvs) - WIN, max(p for p, _, _ in snvs) + WIN
    for r in vcf.fetch(c, max(0, lo - 1), hi):
        if len(r.ref) != 1 or len(r.alts or ()) != 1 or len(r.alts[0]) != 1:
            continue
        s = r.samples['HG008-N']
        if not s.phased or s['GT'] is None or sorted(s['GT']) != [0, 1]:
            continue
        al = (r.ref, r.alts[0])
        het[r.pos - 1] = (al[s['GT'][0]], al[s['GT'][1]])
    # votes per (read, snv): hets within +-WIN of that SNV, as in build_input.py
    hp_at = {}
    het_pos = sorted(het)
    cache = {}
    for p, _, _ in snvs:
        v1, v2 = co.Counter(), co.Counter()
        for h in het_pos[bisect.bisect_left(het_pos, p - 1 - WIN):bisect.bisect_right(het_pos, p - 1 + WIN)]:
            if h not in cache:
                cache[h] = column(bam, c, h)
            for n, b in cache[h].items():
                if n in calls[p]:
                    v1[n] += b == het[h][0]
                    v2[n] += b == het[h][1]
        for n in calls[p]:
            tot = v1[n] + v2[n]
            hp_at[(p, n)] = ('HP1' if v1[n] / tot >= AGREE else 'HP2' if v2[n] / tot >= AGREE else None) if tot >= MIN_INF else None
    return c, calls, hp_at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    ap.add_argument('--jobs', type=int, default=16)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(INP / 'data_hp.tsv'), delimiter='\t'))
    hp = {r['mutation_id']: r['snv_hp'] for r in rows}
    by = co.defaultdict(list)
    for m in hp:
        c, p, r, al = m.rsplit('_', 3)
        by[c].append((int(p), m, r, al))
    pairs = []
    for c, v in by.items():
        v.sort()
        ps = [x[0] for x in v]
        for i, x in enumerate(v):
            for y in v[i + 1:bisect.bisect_right(ps, x[0] + MAXD)]:
                if hp[x[1]] == hp[y[1]] != 'NA':
                    pairs.append((c, x, y))
    need = co.defaultdict(set)
    for c, x, y in pairs:
        need[c] |= {(x[0], x[2], x[3]), (y[0], y[2], y[3])}
    jobs = []   # merge SNVs into windows separated by > MAXD
    for c, s in need.items():
        s = sorted(s)
        cur = [s[0]]
        for t in s[1:]:
            if t[0] - cur[-1][0] > MAXD:
                jobs.append((c, cur)); cur = []
            cur.append(t)
        jobs.append((c, cur))
    print(f'same-HP pairs <= {MAXD // 1000} kb: {len(pairs)}; SNVs {sum(len(s) for s in need.values())}; windows {len(jobs)}', flush=True)
    with Pool(a.jobs) as pool:
        res = pool.map(window, sorted(jobs, key=lambda j: -len(j[1])), chunksize=1)
    calls, hp_at = {}, {}
    for c, cl, h in res:
        calls.update({(c, p): v for p, v in cl.items()})
        hp_at.update({(c, p, n): v for (p, n), v in h.items()})
    out, kept = [], 0
    for c, x, y in pairs:
        h = hp[x[1]]
        cx, cy = calls[(c, x[0])], calls[(c, y[0])]
        n = co.Counter()
        for r in cx.keys() & cy.keys():
            # the read's HP: votes at either SNV (same read); keep it when both agree or one is unknown
            hs = {hp_at.get((c, x[0], r)), hp_at.get((c, y[0], r))} - {None}
            if hs != {h} or cx[r] is None or cy[r] is None:
                continue
            n[cx[r] + cy[r]] += 1
        if sum(n.values()) == 0:
            continue
        kept += 1
        out.append({'mutation_i': x[1], 'mutation_j': y[1], 'hap': h,
                    'n11': n['11'], 'n10': n['10'], 'n01': n['01'], 'n00': n['00']})
    with open(a.out / 'pairs.tsv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, ['mutation_i', 'mutation_j', 'hap', 'n11', 'n10', 'n01', 'n00'], delimiter='\t')
        w.writeheader(); w.writerows(out)
    with open(a.out / 'data_hp.tsv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()) + ['segment_id'], delimiter='\t')
        w.writeheader(); w.writerows({**r, 'segment_id': 's1'} for r in rows)
    with open(a.out / 'segments.tsv', 'w') as fh:
        fh.write('segment_id\tsample_id\ta_hp1\ta_hp2\tb_hp1\tb_hp2\tphi\n')
        fh.write(f's1\t{rows[0]["sample_id"]}\t1\t1\t1\t1\t0\n')
    print(f'pairs with >= 1 tagged read on their HP: {kept}')
    tot = co.Counter()
    for r in out:
        for k in ('n11', 'n10', 'n01', 'n00'):
            tot[k] += r[k]
    print('reads summed over pairs:', dict(tot))


if __name__ == '__main__':
    main()
