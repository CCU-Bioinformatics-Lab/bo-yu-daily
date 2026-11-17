"""HG008 ONT: reads spanning two somatic SNVs (README §4). Run from repo root:
python3 lab_report/2026-11-15_hg008_snv_pairs/count_pairs.py [--jobs 24] > lab_report/2026-11-15_hg008_snv_pairs/pairs_summary.txt
Writes pairs.tsv next to this script (every SNV pair <= 100 kb with >= 1 spanning read)."""
import argparse, bisect, collections as co, csv
from multiprocessing import Pool
from pathlib import Path
import pysam

HERE = Path(__file__).resolve().parent
INP = Path('/bip8_disk/boyu114/hg008_haploclone/input')
BAM = '/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'
MAXD, MAPQ = 100_000, 20


def calls(site):
    """read name -> 'A' (alt) / 'R' (ref) / 'O' (other base) at one SNV."""
    c, pos, ref, alt = site
    out = {}
    with pysam.AlignmentFile(BAM) as bam:
        for col in bam.pileup(c, pos - 1, pos, truncate=True, min_mapping_quality=MAPQ, min_base_quality=0,
                              ignore_orphans=False, max_depth=100000):
            for pr in col.pileups:
                if pr.is_del or pr.is_refskip:
                    continue
                b = pr.alignment.query_sequence[pr.query_position]
                out[pr.alignment.query_name] = 'A' if b == alt else 'R' if b == ref else 'O'
    return site, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=24)
    a = ap.parse_args()
    hp = {r['mutation_id']: r['snv_hp'] for r in csv.DictReader(open(INP / 'data_hp.tsv'), delimiter='\t')}
    lab = {r['mutation_id']: r['layer'] for r in csv.DictReader(open(INP / 'labels.tsv'), delimiter='\t')}
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
                pairs.append((c, x, y))
    need = sorted({(c, x[0], x[2], x[3]) for c, x, y in pairs} | {(c, y[0], y[2], y[3]) for c, x, y in pairs})
    print(f'SNVs {len(hp)}; pairs <= {MAXD // 1000} kb: {len(pairs)}; SNVs in a pair: {len(need)}', flush=True)
    with Pool(a.jobs) as pool:
        got = dict(pool.map(calls, need, chunksize=10))
    rows = []
    for c, x, y in pairs:
        cx, cy = got[(c, x[0], x[2], x[3])], got[(c, y[0], y[2], y[3])]
        pat = co.Counter(cx[n] + cy[n] for n in cx.keys() & cy.keys())
        n = sum(pat.values())
        if n == 0:
            continue
        lx, ly = lab[x[1]], lab[y[1]]
        rows.append({'snv1': x[1], 'snv2': y[1], 'dist': y[0] - x[0], 'hp1': hp[x[1]], 'hp2': hp[y[1]],
                     'layer1': lx, 'layer2': ly, 'reads': n,
                     **{k: pat[k] for k in ('AA', 'AR', 'RA', 'RR')}, 'other': n - sum(pat[k] for k in ('AA', 'AR', 'RA', 'RR'))})
    cols = ['snv1', 'snv2', 'dist', 'hp1', 'hp2', 'layer1', 'layer2', 'reads', 'AA', 'AR', 'RA', 'RR', 'other']
    with open(HERE / 'pairs.tsv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, cols, delimiter='\t')
        w.writeheader()
        w.writerows(rows)

    labeled = lambda r: r['layer1'] != 'none' and r['layer2'] != 'none'
    for name, sel in (('both labeled', labeled), ('other', lambda r: not labeled(r))):
        rr = [r for r in rows if sel(r)]
        same = [r for r in rr if r['hp1'] == r['hp2'] != 'NA']
        print(f'\n[{name}] pairs with >=1 spanning read: {len(rr)}; >=5: {sum(r["reads"] >= 5 for r in rr)}; '
              f'same HP: {len(same)} (>=5 reads: {sum(r["reads"] >= 5 for r in same)})')
        print('  layer pairs:', co.Counter(tuple(sorted((r['layer1'], r['layer2']))) for r in rr).most_common(10))
        if rr:
            ds = sorted(r['dist'] for r in rr)
            print(f'  distance median {ds[len(ds) // 2]} bp; reads per pair median {sorted(r["reads"] for r in rr)[len(rr) // 2]}')
    tl = [r for r in rows if {r['layer1'], r['layer2']} == {'truncal', 'L111'}]
    print(f'\n[truncal x L111] pairs with >=1 spanning read: {len(tl)}')
    for r in tl:
        print('  ', r)


if __name__ == '__main__':
    main()
