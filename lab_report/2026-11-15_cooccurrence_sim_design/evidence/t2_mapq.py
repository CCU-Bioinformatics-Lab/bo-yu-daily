import pysam, numpy as np, sys, random, collections
from multiprocessing import Pool
D=sys.argv[1]; BAM='/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'
W=[('chr16',55811907,55827280),('chr15',101874129,101892548),('chr15',82469612,82487933),('chr16',88159049,88184761),
   ('chr15',75253793,75296517),('chr20',29914918,29959578),('chr18',15330619,15357970),('chr7',54321360,54323683),('chr20',26604023,26607900),('chr12',11414,94894)]
random.seed(2)
fai=[l.split('\t') for l in open('/big8_disk/yungjen114/data/HG008/reference/GRCh38-GIABv3/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta.fai')]
chrs=[(f[0],int(f[1])) for f in fai if f[0] in ['chr%d'%i for i in range(1,23)]]
tot=sum(l for c,l in chrs)
R=[]
for i in range(30):
    x=random.randrange(tot)
    for c,l in chrs:
        if x<l: R.append((c,x,x+20000)); break
        x-=l
def mq(r):
    c,s,e=r; b=pysam.AlignmentFile(BAM); m=[]; dep=0
    for a in b.fetch(c,s,e):
        if a.is_secondary or a.is_supplementary or a.is_unmapped: continue
        m.append(a.mapping_quality)
    # depth at midpoint, mapq>=20 primary
    mid=(s+e)//2
    for col in b.pileup(c,mid,mid+1,truncate=True,min_mapping_quality=20,min_base_quality=0,stepper='nofilter'):
        dep=sum(1 for p in col.pileups if not p.alignment.is_secondary and not p.alignment.is_supplementary)
    return r,np.array(m),dep
with Pool(8) as p: res=p.map(mq,W+R)
o=open(D+'/t2_mapq.txt','w')
def desc(m): return f'reads={len(m)} MAPQ q10/q50={np.quantile(m,.1):.0f}/{np.median(m):.0f} frac<20={np.mean(m<20):.3f} frac<5={np.mean(m<5):.3f} frac==60={np.mean(m==60):.3f}'
for r,m,dep in res[:len(W)]: print(f'{r[0]}:{r[1]}-{r[2]}',desc(m),'depth_mid_MQ20=',dep,file=o)
g=np.concatenate([m for r,m,d in res[len(W):]]); deps=[d for r,m,d in res[len(W):]]
print('genome-wide 30 random 20kb autosomal',desc(g),'depth_mid_MQ20 median=',np.median(deps),file=o)
