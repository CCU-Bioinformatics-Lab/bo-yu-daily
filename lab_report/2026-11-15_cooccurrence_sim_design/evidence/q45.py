import numpy as np, re, sys
sys.path.insert(0,'.')
from power import scores
f='/bip8_disk/boyu114/main_work/lab_report/2026-11-15_hg008_snv_pairs/truncal_L111_same_hp.txt'
rows=[tuple(map(int,m)) for m in re.findall(r'\((\d+), (\d+), (\d+), (\d+)\)',open(f).read())]
c=np.array(rows,float); print(len(c),c.sum(0))
for eps in (0.01,0.02,0.03,0.05):
    s,a,d,b=[x.sum() for x in scores(c[:,0],c[:,1],c[:,2],eps)]
    print(f"Q5 eps={eps}: same={s:.2f} anc={a:.2f} desc={d:.2f} br={b:.2f} anc-same={a-s:.2f}")
# per-pair contributions eps=0.01
s,a,d,b=scores(c[:,0],c[:,1],c[:,2],0.01)
print("per-pair anc-same:",np.round(a-s,2))
# Q4 density
G=3.1e9; L=2e4; Dh=30
rng=np.random.default_rng(2)
def count(pos,clone,hp,X=0,Y=1):
    o=np.argsort(pos); p,cl,h=pos[o],clone[o],hp[o]
    npair=0; reads=[]
    for i in range(len(p)):
        j=i+1
        while j<len(p) and p[j]-p[i]<L:
            if h[i]==h[j] and {cl[i],cl[j]}=={X,Y}:
                npair+=1; reads.append(Dh*(1-(p[j]-p[i])/L))
            j+=1
    return npair,np.mean(reads) if reads else 0
def uniform(N): return rng.uniform(0,G,N)
def clustered(N,a=0.2,b=0.01):
    k=rng.binomial(N,a); nb=100; starts=rng.uniform(0,G,nb); w=b*G/nb
    hot=starts[rng.integers(0,nb,k)]+rng.uniform(0,w,k)
    return np.concatenate([hot,rng.uniform(0,G,N-k)])
for name,N,fn in [("uniform 1000",1000,uniform),("uniform 2600",2600,uniform),("clustered a=.2 b=.01 N=1000",1000,clustered),("clustered N=2600",2600,clustered),("uniform 10000",10000,uniform)]:
    res=[]
    for r in range(200 if N<5000 else 30):
        pos=fn(N); cl=rng.integers(0,5,N); hp=rng.integers(0,2,N)
        res.append(count(pos,cl,hp))
    res=np.array(res); print(f"Q4 {name}: mean XY same-HP pairs={res[:,0].mean():.2f} P(>=1)={np.mean(res[:,0]>=1):.2f} mean reads/pair={res[res[:,0]>0,1].mean():.1f}")
n=lambda N:(N/5)**2*2*L/G*0.5
print("analytic uniform:",{N:round(n(N),3) for N in (1000,2600,10000,30000)}, "clustered factor", 0.2**2/0.01+0.8**2/0.99)
