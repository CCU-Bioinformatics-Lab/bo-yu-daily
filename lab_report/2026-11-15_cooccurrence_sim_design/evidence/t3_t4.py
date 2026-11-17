import pysam, numpy as np, sys, random, collections
from multiprocessing import Pool
D=sys.argv[1]; BAM='/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'
B='/big8_disk/yungjen114/data/HG008/NIST/somatic-stvar-CNV_v0.6_20261006/GRCh38/GRCh38_HG008-T-V0.6_somatic-CNV_PASS.draftbenchmark.calls.bed'
regs=[]
for l in open(B):
    f=l.split('\t')
    if f[4]=='1' and f[5]=='1' and int(f[2])-int(f[1])>3_000_000: regs.append((f[0],int(f[1]),int(f[2])))
random.seed(3); L=np.array([e-s for c,s,e in regs],float)
R=[]
for i in range(40):
    c,s,e=regs[np.random.default_rng(i).choice(len(regs),p=L/L.sum())]
    x=random.randrange(s+200000,e-1200000); R.append((c,x,x+1_000_000))
def run(r):
    c,s,e=r; b=pysam.AlignmentFile(BAM); out=[]
    for a in b.fetch(c,s,e):
        if a.is_secondary or a.is_supplementary or a.is_unmapped or a.mapping_quality<20: continue
        if s<=a.reference_start<e: out.append(a.reference_end-a.reference_start)
    return out
with Pool(8) as p: res=p.map(run,R)
x=np.concatenate([np.array(r) for r in res]); np.save(D+'/t3_spans.npy',x)
o=open(D+'/t3_readlen.txt','w')
xs=np.sort(x)[::-1]; n50=xs[np.searchsorted(np.cumsum(xs),xs.sum()/2)]
print(f'regions=40 x 1Mb in 1+1 segments; primary MAPQ>=20 reads starting in region: n={len(x)}',file=o)
print(f'ref span median={np.median(x):.0f} mean={x.mean():.0f} N50={n50} q90={np.quantile(x,.9):.0f} q99={np.quantile(x,.99):.0f} max={x.max()}',file=o)
for t in (1e4,2e4,5e4,1e5): print(f' frac reads >{int(t/1000)}kb = {np.mean(x>t):.4f} ; frac of bases in reads >{int(t/1000)}kb = {x[x>t].sum()/x.sum():.4f}',file=o)
print(f' implied depth = sum(span)/40Mb = {x.sum()/40e6:.1f}x',file=o)
# Task 4
EL=x.mean()
def S(d): return np.clip(x-d,0,None).mean()/EL   # P(a covering read also covers pos+d)
dep={}
for l in open('/bip8_disk/boyu114/hg008_haploclone/input/data_hp.tsv').readlines()[1:]:
    f=l.split('\t'); dep[f[0]]=int(f[2])+int(f[3])
P=[l.rstrip('\n').split('\t') for l in open('/bip8_disk/boyu114/main_work/lab_report/2026-11-15_hg008_snv_pairs/pairs.tsv').readlines()[1:]]
bins=[0,1000,5000,10000,20000,30000,50000,75000,100001]
print('\n== Task4: predicted reads spanning pair = mean(depth of 2 SNVs from data_hp ref+alt) x S(d), S(d)=E[(L-d)+]/E[L]',file=o)
print('S(d) for d=1,5,10,20,50,100kb:',[round(S(d),4) for d in (1e3,5e3,1e4,2e4,5e4,1e5)],file=o)
for grp in ('labelled','other'):
    print(f'\n-- {grp}: bin | n_pairs | obs median/mean | pred median/mean | obs/pred mean ratio',file=o)
    for lo,hi in zip(bins[:-1],bins[1:]):
        ob=[];pr=[]
        for p in P:
            lab = p[5]!='none' and p[6]!='none'
            if (grp=='labelled')!=lab: continue
            d=int(p[2])
            if not lo<=d<hi: continue
            ob.append(int(p[7])); pr.append((dep[p[0]]+dep[p[1]])/2*S(d))
        if not ob: continue
        ob=np.array(ob);pr=np.array(pr)
        print(f'{lo//1000}-{hi//1000}kb | {len(ob)} | {np.median(ob):.1f}/{ob.mean():.1f} | {np.median(pr):.1f}/{pr.mean():.1f} | {ob.mean()/pr.mean():.2f}',file=o)
