"""HG008 (2026-11-13): ClairS (ONT tumor 63x vs normal N-D 94x) PASS SNVs vs NIST and the clone-tree branches.
Run from repo root: python3 -I lab_report/2026-11-13_hg008_bulk_rebuild/count_clairs_branch.py"""
import gzip, statistics as st, collections as co
import sys
CL = sys.argv[1] if len(sys.argv) > 1 else '/bip8_disk/boyu114/hg008_clairs_ont/out/output.vcf.gz'  # PacBio 11-14: pass hg008_clairs_pacbio/out/output.vcf.gz
N = '/big8_disk/yungjen114/data/HG008/NIST/somatic-smvar_v0.4_20261006/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_somatic_tumornormal.vcf.gz'
BED = '/big8_disk/yungjen114/data/HG008/NIST/somatic-smvar_v0.4_20261006/GRCh38/HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_all.bed'
TAB = 'lab_report/2026-11-07_hg008_tree_rebuild/tables/snv_classes_vaf0.25_qual20.tsv'
import bisect
bed = co.defaultdict(list)
for l in open(BED):
    f = l.split('\t'); bed[f[0]].append((int(f[1]), int(f[2])))
for k in bed: bed[k].sort()
bst = {k: [s for s, e in v] for k, v in bed.items()}
def inbed(c, p):
    i = bisect.bisect_right(bst.get(c, []), p - 1) - 1
    return i >= 0 and bed[c][i][0] <= p - 1 < bed[c][i][1]
cl = {}
for l in gzip.open(CL, 'rt'):
    if l[0] == '#': continue
    f = l.rstrip('\n').split('\t')
    if f[6] != 'PASS' or len(f[3]) != 1 or len(f[4]) != 1: continue
    d = dict(zip(f[8].split(':'), f[9].split(':')))
    cl[(f[0], int(f[1]), f[3], f[4])] = (float(d['AF']), int(d['DP']))
nist = set()
for l in gzip.open(N, 'rt'):
    if l[0] != '#':
        f = l.split('\t')
        if len(f[3]) == 1 == len(f[4]): nist.add((f[0], int(f[1]), f[3], f[4]))
print(f'ClairS PASS SNV {len(cl)}; NIST SNV {len(nist)}; both {len(nist & cl.keys())} '
      f'(NIST recall {len(nist & cl.keys())/len(nist):.1%}); ClairS-only {len(cl.keys()-nist)}, of which inside NIST benchmark region {sum(inbed(k[0],k[1]) for k in cl.keys()-nist)}')
def q(v): return 'n/a' if not v else f'median AF {st.median(v):.3f}'
print(f'AF: in NIST {q([cl[k][0] for k in cl if k in nist])}; ClairS-only {q([cl[k][0] for k in cl if k not in nist])}')
cls, pat = {}, {}
for l in open(TAB):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'chrom':
        k = (f[0], int(f[1]), f[2], f[3]); cls[k] = f[5]; pat[k] = ','.join(sorted(f[4].split(',')))
print('\nclass\tclones\tin_NIST\tin_ClairS\tClairS AF')
for c, n in co.Counter(cls.values()).most_common():
    ks = [k for k in cls if cls[k] == c]
    print(f'{c}\t{n}\t{sum(k in nist for k in ks)}\t{sum(k in cl for k in ks)}\t{q([cl[k][0] for k in ks if k in cl])}')
print('\nshared_clean by clade\tclones\tin_NIST\tin_ClairS\tClairS AF')
a = co.Counter(pat[k] for k in cls if cls[k] == 'shared_clean')
for p, n in a.most_common(8):
    ks = [k for k in cls if cls[k] == 'shared_clean' and pat[k] == p]
    print(f'{p}\t{n}\t{sum(k in nist for k in ks)}\t{sum(k in cl for k in ks)}\t{q([cl[k][0] for k in ks if k in cl])}')
print('\nprivate by clone\tclones\tin_ClairS')
pv = co.Counter(pat[k] for k in cls if cls[k] == 'private')
for p, n in pv.most_common():
    print(f'{p}\t{n}\t{sum(1 for k in cls if cls[k]=="private" and pat[k]==p and k in cl)}')
af = [v[0] for k, v in cl.items() if k not in nist]
print('\nClairS-only AF histogram:', {f'{lo:.2f}-{lo+.05:.2f}': sum(lo <= x < lo + .05 for x in af) for lo in [i * .05 for i in range(20)]})
