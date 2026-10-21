"""Compare pcdh_entropy.py outputs across labels (unphased vs HP1/HP2, tumor vs normal).

usage: python3 pcdh_hp_compare.py TSV [TSV ...] TUMOR_LABEL NORMAL_LABEL

Per label: window count, median methylation/entropy. Pairs compare medians on
shared windows. First used in lab_report/2026-10-20_h1437_pcdh_hp_entropy/.
"""
import csv, sys, statistics as st, collections
rows=collections.defaultdict(dict)
for f in sys.argv[1:-2]:
    for r in csv.DictReader(open(f),delimiter='\t'): rows[r['label']][int(r['win_start'])]=r
E=lambda l,ks:[float(rows[l][w]['entropy_sub20']) for w in ks]
M=lambda l,ks:[float(rows[l][w]['mean_meth']) for w in ks]
for l in sorted(rows):
    ks=list(rows[l]); e=E(l,ks); q=st.quantiles(e,n=4) if len(e)>3 else [float('nan')]*3
    print(f"{l:26} win={len(ks):5} meth={st.median(M(l,ks)):.2f} ent={st.median(e):.2f} ({q[0]:.2f}-{q[2]:.2f}) <=1:{sum(x<=1 for x in e)/len(e):.0%} >=3:{sum(x>=3 for x in e)/len(e):.0%}")
def pair(a,b,name):
    sh=sorted(set(rows[a])&set(rows[b]))
    if len(sh)<3: print(name,'shared',len(sh)); return
    d=[x-y for x,y in zip(E(a,sh),E(b,sh))]
    print(f"{name}: shared {len(sh)} ent {st.median(E(a,sh)):.2f} vs {st.median(E(b,sh)):.2f} diff {st.median(d):+.2f} (first lower {sum(x<0 for x in d)}/{len(sh)}) meth {st.median(M(a,sh)):.2f} vs {st.median(M(b,sh)):.2f}")
T, N = sys.argv[-2:]
print()
pair(T+'_HP1',T,'tumor HP1 vs unphased'); pair(T+'_HP2',T,'tumor HP2 vs unphased')
pair(N+'_HP1',N,'normal HP1 vs unphased'); pair(N+'_HP2',N,'normal HP2 vs unphased')
pair(T+'_HP1',N+'_HP1','HP1 tumor vs normal'); pair(T+'_HP2',N+'_HP2','HP2 tumor vs normal')
pair(T+'_HP1',T+'_HP2','tumor HP1 vs HP2'); pair(N+'_HP1',N+'_HP2','normal HP1 vs HP2')
for l in [T+'_HP1',T+'_HP2',N+'_HP1',N+'_HP2']:
    d=rows[l]; mid=[w for w in d if 0.4<=float(d[w]['mean_meth'])<0.8]
    if mid: print(l,'mid-meth windows',len(mid),'ent %.2f top_frac %.2f'%(st.median(E(l,mid)),st.median([float(d[w]['top_barcode_frac']) for w in mid])))
