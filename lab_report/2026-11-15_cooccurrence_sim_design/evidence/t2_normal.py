import pysam, pickle, sys, numpy as np, collections
from multiprocessing import Pool
D=sys.argv[1]; snv=pickle.load(open(D+'/snv.pkl','rb'))
T='/big8_disk/yungjen114/data/HG008/ONT/HG008.bam'; N='/big8_disk/yungjen114/data/HG008/ONT/HG008-N-D.bam'
W={'chr16:55.8':('chr16',55811907,55827280),'chr15:101.8':('chr15',101874129,101892548),'chr15:82.4':('chr15',82469612,82487933),
   'chr16:88.1':('chr16',88159049,88184761),'chr20:29.9':('chr20',29914918,29959578),'chr20:26.6':('chr20',26604023,26607900),'chr7:54.3':('chr7',54321360,54323683)}
def af(args):
    bam,c,p,a=args; b=pysam.AlignmentFile(bam); n=k=0
    for col in b.pileup(c,p-1,p,truncate=True,min_mapping_quality=20,min_base_quality=0):
        for q in col.pileups:
            if q.is_del or q.is_refskip: continue
            n+=1; k+= q.alignment.query_sequence[q.query_position]==a
    return k,n
jobs=[];keys=[]
for w,(c,s,e) in W.items():
    x=[t for t in snv if t[0]==c and s<=t[1]<=e]; x=x[::max(1,len(x)//12)][:12]
    for t in x:
        for bam in (T,N): jobs.append((bam,c,t[1],t[3])); keys.append((w,bam==N))
# control: 30 labelled truncal SNVs
ctrl=[t for t in snv if t[6]=='truncal'][::100][:30]
for t in ctrl:
    for bam in (T,N): jobs.append((bam,t[0],t[1],t[3])); keys.append(('truncal_ctrl',bam==N))
with Pool(8) as p: r=p.map(af,jobs)
agg=collections.defaultdict(lambda:[[],[]])
for (w,isn),(k,n) in zip(keys,r): agg[w][isn].append((k,n))
o=open(D+'/t2_normal_alt.txt','w')
for w,(tu,no) in agg.items():
    f=lambda L:(np.median([k/n for k,n in L if n]),np.median([n for k,n in L]),sum(k>=2 for k,n in L))
    a,b,c=f(tu); d,e,g=f(no)
    print(f'{w} sites={len(tu)} tumourVAF_med={a:.3f} tumour_depth_med={b:.0f} | normal(N-D 94x) VAF_med={d:.3f} depth_med={e:.0f} sites_with_alt>=2={g}/{len(no)}',file=o)
