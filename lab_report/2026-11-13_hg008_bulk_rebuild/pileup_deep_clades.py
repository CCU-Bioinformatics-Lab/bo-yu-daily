"""HG008 (2026-11-13): raw ONT tumor alt counts at the deeper clone-tree clade SNVs, and whether ClairS PASS / LowQual called them.
Run from repo root: python3 -I lab_report/2026-11-13_hg008_bulk_rebuild/pileup_deep_clades.py"""
import gzip, subprocess, collections as co
TAB = 'lab_report/2026-11-07_hg008_tree_rebuild/tables/snv_classes_vaf0.25_qual20.tsv'
CL = '/bip8_disk/boyu114/hg008_clairs_ont/out/output.vcf.gz'
BAM = '/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'
NBAM = '/big8_disk/yungjen114/data/HG008/ONT/HG008-N-D.bam'
REF = '/big8_disk/yungjen114/data/HG008/reference/GRCh38-GIABv3/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta'
CLADES = {'SC14,SC24,SC28,SC9': '48 cells', 'SC14,SC28': '16 cells', 'SC24,SC9': 'unverified', '2D6,2E6': 'partial'}
filt = {}
for l in gzip.open(CL, 'rt'):
    if l[0] != '#':
        f = l.split('\t'); filt[(f[0], int(f[1]), f[3], f[4])] = f[6]
sites = []
for l in open(TAB):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'chrom' and f[5] == 'shared_clean':
        p = ','.join(sorted(f[4].split(',')))
        if p in CLADES: sites.append((f[0], int(f[1]), f[2], f[3], p))
def counts(bam, c, pos, alt):
    out = subprocess.run(['samtools', 'mpileup', '-r', f'{c}:{pos}-{pos}', '-f', REF, '-Q', '0', '-q', '20', bam],
                         capture_output=True, text=True).stdout.split('\t')
    if len(out) < 5: return 0, 0
    b = out[4].upper(); import re
    b = re.sub(r'\^.', '', b).replace('$', '')
    b = re.sub(r'[+-](\d+)', lambda m: '\0' * 0 + '#' * 0 + f'<{m.group(1)}>', b)
    import re as r2
    seq, i, n = [], 0, b
    while i < len(n):
        if n[i] == '<':
            j = n.index('>', i); k = int(n[i+1:j]); i = j + 1 + k; continue
        seq.append(n[i]); i += 1
    return int(out[3]), sum(ch == alt for ch in seq)
rows = co.defaultdict(list)
print('clade\tchrom\tpos\tclairs\ttumor_depth\ttumor_alt\tnormal_alt')
for c, pos, ref, alt, p in sites:
    d, a = counts(BAM, c, pos, alt); nd, na = counts(NBAM, c, pos, alt)
    fl = filt.get((c, pos, ref, alt), 'none')
    rows[p].append((d, a, na, fl))
    print(f'{p}\t{c}\t{pos}\t{fl}\t{d}\t{a}\t{na}')
print('\nsummary\tsites\tclairs PASS/LowQual/none\tmedian depth\tsites with alt>=2\tpooled tumor VAF\tnormal alt>0')
import statistics as st
for p, r in rows.items():
    fc = co.Counter(x[3] for x in r)
    print(f'{p} ({CLADES[p]})\t{len(r)}\t{fc["PASS"]}/{fc["LowQual"]}/{fc["none"]}\t{st.median(x[0] for x in r):.0f}\t'
          f'{sum(x[1] >= 2 for x in r)}\t{sum(x[1] for x in r)/max(1,sum(x[0] for x in r)):.3f}\t{sum(x[2] > 0 for x in r)}')
