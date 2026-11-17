import numpy as np, pickle, sys, collections
D=sys.argv[1]; snv=pickle.load(open(D+'/snv.pkl','rb')); x=np.load(D+'/t3_spans.npy'); EL=x.mean()
S=lambda d: np.clip(x-d,0,None).mean()/EL
dep={}
for l in open('/bip8_disk/boyu114/hg008_haploclone/input/data_hp.tsv').readlines()[1:]:
    f=l.split('\t'); dep[f[0]]=int(f[2])+int(f[3])
obs={}
P=[l.rstrip('\n').split('\t') for l in open('/bip8_disk/boyu114/main_work/lab_report/2026-11-15_hg008_snv_pairs/pairs.tsv').readlines()[1:]]
for p in P: obs[(p[0],p[1])]=int(p[7])
lab=[s for s in snv if s[6]!='none']; bc=collections.defaultdict(list)
for s in lab: bc[s[0]].append(s)
o=open(D+'/t4_with_zero_pairs.txt','w')
print('labelled pairs within 100kb incl. pairs with 0 spanning reads (absent from pairs.tsv)',file=o)
bins=[30000,40000,50000,60000,75000,100001]
rows=collections.defaultdict(lambda:[[],[]])
for c,ss in bc.items():
    ss.sort(key=lambda s:s[1])
    for i in range(len(ss)):
        for j in range(i+1,len(ss)):
            d=ss[j][1]-ss[i][1]
            if d>100000: break
            k=(ss[i][7],ss[j][7]); k2=(k[1],k[0])
            ob=obs.get(k,obs.get(k2,0))
            for lo,hi in zip(bins[:-1],bins[1:]):
                if lo<=d<hi: rows[(lo,hi)][0].append(ob); rows[(lo,hi)][1].append((dep[k[0]]+dep[k[1]])/2*S(d))
print('bin | n_pairs | frac>=1 read obs | obs mean | pred mean | P(>=1) pred (Poisson)',file=o)
for (lo,hi),(ob,pr) in sorted(rows.items()):
    ob=np.array(ob);pr=np.array(pr)
    print(f'{lo//1000}-{hi//1000}kb | {len(ob)} | {np.mean(ob>=1):.3f} | {ob.mean():.2f} | {pr.mean():.2f} | {np.mean(1-np.exp(-pr)):.3f}',file=o)
print('\nother pairs 75-100kb with reads (anomaly):',file=o)
print(collections.Counter(p[0].split('_')[0]+':'+str(int(p[0].split('_')[1])//100000/10)+'Mb' for p in P if int(p[2])>=75000 and not(p[5]!='none' and p[6]!='none')).most_common(5),file=o)
