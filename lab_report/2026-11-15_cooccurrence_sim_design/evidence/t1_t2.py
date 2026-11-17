import numpy as np, pysam, collections, sys
D=sys.argv[1]
B='/big8_disk/yungjen114/data/HG008/NIST/somatic-stvar-CNV_v0.6_20261006/GRCh38/GRCh38_HG008-T-V0.6_somatic-CNV_PASS.draftbenchmark.calls.bed'
FA='/big8_disk/yungjen114/data/HG008/reference/GRCh38-GIABv3/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta'
I='/bip8_disk/boyu114/hg008_haploclone/input/'
lab={};
for l in open(I+'labels.tsv').readlines()[1:]:
    f=l.split('\t'); lab[f[0]]=f[1]
snv=[]
for l in open(I+'data_hp.tsv').readlines()[1:]:
    f=l.rstrip('\n').split('\t'); c,p,r,a=f[0].split('_')
    rc,ac=int(f[2]),int(f[3]); snv.append((c,int(p),r,a,ac/(rc+ac),f[8],lab[f[0]],f[0]))
reg=collections.defaultdict(list)
for l in open(B):
    f=l.split('\t')
    if f[4]=='1' and f[5]=='1': reg[f[0]].append((int(f[1]),int(f[2])))
# check SNVs inside regions
def nn(pos_by_chr):
    out=[]
    for c,ps in pos_by_chr.items():
        ps=np.sort(np.array(ps))
        if len(ps)<2: continue
        d=np.diff(ps); n=np.full(len(ps),np.inf); n[:-1]=d; n[1:]=np.minimum(n[1:],d); out.append(n)
    return np.concatenate(out)
def bychr(sel):
    d=collections.defaultdict(list)
    for s in sel: d[s[0]].append(s[1])
    return d
rng=np.random.default_rng(1)
allreg=[(c,s,e) for c in reg for s,e in reg[c]]; L=np.array([e-s for c,s,e in allreg],float); tot=L.sum()
# per-chrom uniform: keep same per-chrom counts? use same total count across all 1+1 regions (genome-wide) — also per-chrom variant
def unif(sel, perchr):
    d=collections.defaultdict(list)
    if perchr:
        cnt=collections.Counter(s[0] for s in sel)
        for c,n in cnt.items():
            rs=reg[c]; ll=np.array([e-s for s,e in rs],float)
            k=rng.choice(len(rs),n,p=ll/ll.sum())
            for i in k: d[c].append(rng.integers(rs[i][0],rs[i][1]))
    else:
        k=rng.choice(len(allreg),len(sel),p=L/tot)
        for i in k: c,s,e=allreg[i]; d[c].append(rng.integers(s,e))
    return d
TH=[1e3,5e3,2e4,5e4,1e5]
o=open(D+'/t1_distance.txt','w')
print('1+1 total bp',tot,'n regions',len(allreg),file=o)
inside=sum(any(s<=x[1]<e for s,e in reg[x[0]]) for x in snv); print('SNVs inside 1+1 bed',inside,len(snv),file=o)
for name,sel in [('labelled',[s for s in snv if s[6]!='none']),('all',snv),('none',[s for s in snv if s[6]=='none'])]:
    ob=nn(bychr(sel))
    print(f'\n== {name} n={len(sel)}',file=o)
    def row(tag,x): print(tag,'q10,25,50,75,90=',[int(v) for v in np.quantile(x,[.1,.25,.5,.75,.9])],'frac<1k,5k,20k,50k,100k=',[round(float((x<t).mean()),4) for t in TH],file=o)
    row('observed',ob)
    for perchr in (False,True):
        reps=[nn(unif(sel,perchr)) for _ in range(5)]
        q=np.mean([np.quantile(r,[.1,.25,.5,.75,.9]) for r in reps],0); fr=np.mean([[ (r<t).mean() for t in TH] for r in reps],0)
        print('uniform'+('_perchr' if perchr else '_genome'),'(5 reps mean) q=',[int(v) for v in q],'frac=',[round(float(v),4) for v in fr],file=o)
# Task2 clusters
fa=pysam.FastaFile(FA)
comp=str.maketrans('ACGT','TGCA')
def ctx(c,p,r,a):
    t=fa.fetch(c,p-2,p+1).upper()
    if r in 'GA': t=t.translate(comp)[::-1]; r=r.translate(comp); a=a.translate(comp)
    return t,f'{r}>{a}'
snv.sort(key=lambda s:(s[0],s[1]))
for kind in ('all','labelled'):
  sel=[s for s in snv if kind=='all' or s[6]!='none']
  bc=collections.defaultdict(list)
  for s in sel: bc[s[0]].append(s)
  # rule A: consecutive <1kb, size>=2 ; rule B: SigProfilerClusters-like: IMD < mean IMD/100? use threshold = expected IMD (tot/n)/100
  exp=tot/len(sel)
  for rule,thr,minsize in [('A_lt1kb',1000,2),('B_imd<exp/100',exp/100,3)]:
    cl=[]
    for c,ss in bc.items():
        cur=[ss[0]]
        for s in ss[1:]:
            if s[1]-cur[-1][1]<thr: cur.append(s)
            else:
                if len(cur)>=minsize: cl.append(cur)
                cur=[s]
        if len(cur)>=minsize: cl.append(cur)
    sizes=np.array([len(x) for x in cl]); spans=np.array([x[-1][1]-x[0][1] for x in cl])
    print(f'\n== clusters {kind} rule {rule} thr={thr:.0f} minsize={minsize}: n={len(cl)} SNVs_in={sizes.sum()} size q50/max={np.median(sizes)}/{sizes.max()} span q50/max={int(np.median(spans))}/{spans.max()}',file=o)
    print(' size hist',sorted(collections.Counter(sizes).items()),file=o)
    print(' layers in clusters',collections.Counter(s[6] for x in cl for s in x),file=o)
    # signature
    sig=collections.Counter(); apo=0; n=0; samehp=0; pairs=0
    for x in cl:
        for s in x:
            t,m=ctx(*s[:4]); sig[m]+=1; n+=1
            if t[0]=='T' and m in('C>T','C>G') and t[2] in 'AT': apo+=1
        hps=[s[5] for s in x if s[5]!='NA']
        for i in range(len(hps)-1): pairs+=1; samehp+= hps[i]==hps[i+1]
    print(' subs',dict(sig),'APOBEC TCW>T/G frac',round(apo/n,3),'adjacent same-HP',samehp,'/',pairs,file=o)
    if kind=='all' and rule=='A_lt1kb':
        cl.sort(key=len,reverse=True)
        with open(D+'/t2_clusters_lt1kb_all.tsv','w') as w:
            w.write('chr\tstart\tend\tn\tlayers\thp\tsubs\tAPOBEC_frac\tVAF_median\n')
            for x in cl:
                cs=[ctx(*s[:4]) for s in x]
                ap=sum(t[0]=='T' and m in('C>T','C>G') and t[2] in 'AT' for t,m in cs)/len(x)
                w.write(f"{x[0][0]}\t{x[0][1]}\t{x[-1][1]}\t{len(x)}\t{dict(collections.Counter(s[6] for s in x))}\t{dict(collections.Counter(s[5] for s in x))}\t{dict(collections.Counter(m for t,m in cs))}\t{ap:.2f}\t{np.median([s[4] for s in x]):.3f}\n")
# genome-wide signature of labelled vs none
for name,sel in [('labelled',[s for s in snv if s[6]!='none']),('none',[s for s in snv if s[6]=='none'])]:
    cs=[ctx(*s[:4]) for s in sel]
    ap=sum(t[0]=='T' and m in('C>T','C>G') and t[2] in 'AT' for t,m in cs)/len(cs)
    print(f'\n== signature {name}: subs',dict(collections.Counter(m for t,m in cs)),'APOBEC frac',round(ap,3),'VAF median',round(float(np.median([s[4] for s in sel])),3),file=o)
# dense windows 100kb
print('\n== densest 100kb windows (all SNVs)',file=o)
win=collections.Counter((s[0],s[1]//100000) for s in snv)
import pickle; pickle.dump(snv,open(D+'/snv.pkl','wb'))
for (c,w),n in win.most_common(12):
    x=[s for s in snv if s[0]==c and s[1]//100000==w]
    cs=[ctx(*s[:4]) for s in x]
    ap=sum(t[0]=='T' and m in('C>T','C>G') and t[2] in 'AT' for t,m in cs)/len(x)
    print(f'{c}:{w/10:.1f}Mb n={n} span={x[0][1]}-{x[-1][1]} layers={dict(collections.Counter(s[6] for s in x))} hp={dict(collections.Counter(s[5] for s in x))} subs={dict(collections.Counter(m for t,m in cs))} APOBEC={ap:.2f} ctx_top={collections.Counter(t+":"+m for t,m in cs).most_common(4)} VAF q25/50/75={np.round(np.quantile([s[4] for s in x],[.25,.5,.75]),3).tolist()}',file=o)
