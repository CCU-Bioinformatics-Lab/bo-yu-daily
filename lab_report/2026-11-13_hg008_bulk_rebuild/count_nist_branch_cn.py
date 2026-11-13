"""HG008 (2026-11-13): NIST somatic SNVs vs clone-tree classes/clades, and 1+1 share (NIST CNV v0.6 PASS).
Run from repo root: python3 -I lab_report/2026-11-13_hg008_bulk_rebuild/count_nist_branch_cn.py"""
import gzip, bisect, collections as co
N = '/big8_disk/yungjen114/data/HG008/NIST/somatic-smvar_v0.4_20261006/GRCh38/'
C = '/big8_disk/yungjen114/data/HG008/NIST/somatic-stvar-CNV_v0.6_20261006/GRCh38/GRCh38_HG008-T-V0.6_somatic-CNV_PASS.draftbenchmark.calls.bed'
TAB = 'lab_report/2026-11-07_hg008_tree_rebuild/tables/snv_classes_vaf0.25_qual20.tsv'
cn = co.defaultdict(list)
for l in open(C):
    f = l.rstrip('\n').split('\t'); cn[f[0]].append((int(f[1]), int(f[2]), f[4] + '+' + f[5]))  # cols: CN_total, hap1, hap2
for k in cn: cn[k].sort()
starts = {k: [s for s, e, v in iv] for k, iv in cn.items()}
def state(c, p):
    iv = cn.get(c, []); i = bisect.bisect_right(starts.get(c, []), p - 1) - 1
    return iv[i][2] if i >= 0 and iv[i][0] <= p - 1 < iv[i][1] else 'no_call'
L = co.Counter(); [L.update({v: e - s}) for iv in cn.values() for s, e, v in iv]
T = sum(L.values())
print(f'CNV PASS tiling {T/1e6:.0f} Mb:', ', '.join(f'{k} {v/1e6:.0f} Mb ({v/T:.1%})' for k, v in L.most_common(5)))
nist = set()
for l in gzip.open(N + 'HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_somatic_tumornormal.vcf.gz', 'rt'):
    if l[0] != '#':
        f = l.split('\t')
        if len(f[3]) == 1 == len(f[4]): nist.add((f[0], int(f[1]), f[3], f[4]))
s = co.Counter(state(k[0], k[1]) for k in nist)
print(f'NIST SNV {len(nist)} by CN state:', ', '.join(f'{k} {v} ({v/len(nist):.1%})' for k, v in s.most_common(6)))
cls, pat = {}, {}
for l in open(TAB):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'chrom':
        k = (f[0], int(f[1]), f[2], f[3]); cls[k] = f[5]; pat[k] = ','.join(sorted(f[4].split(',')))
print('\nclass\tclones\tin_NIST\tin_NIST_1+1')
tot = co.Counter(cls.values())
for c, n in tot.most_common():
    ks = [k for k in cls if cls[k] == c and k in nist]
    print(f'{c}\t{n}\t{len(ks)}\t{sum(state(k[0], k[1]) == "1+1" for k in ks)}')
print(f'NIST SNV not in any clone call: {sum(k not in cls for k in nist)}')
print('\nshared_clean by clade pattern\tclones\tin_NIST\tin_NIST_1+1')
a = co.Counter(pat[k] for k in cls if cls[k] == 'shared_clean')
for p, n in a.most_common(8):
    ks = [k for k in cls if cls[k] == 'shared_clean' and pat[k] == p and k in nist]
    print(f'{p}\t{n}\t{len(ks)}\t{sum(state(k[0], k[1]) == "1+1" for k in ks)}')
