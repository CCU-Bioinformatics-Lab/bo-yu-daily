import numpy as np
from scipy.special import betaln
rng=np.random.default_rng(1)
L1=lambda x: np.log1p(-x)
def scores(n11,n10,n01,eps=0.01):
    le,l1,l2=np.log(eps),L1(eps),L1(2*eps)
    same=(n10+n01)*le+n11*l2
    anc=n01*le+(n11+n10)*l1+betaln(n11+1,n10+1)
    desc=n10*le+(n11+n01)*l1+betaln(n11+1,n01+1)
    br=n11*le+(n10+n01)*l1+betaln(n10+1,n01+1)
    return same,anc,desc,br
def sim(probs,m,K,e,eps,R=4000):
    # probs over 11,10,01,00; m reads/pair, K pairs, R reps; e = per-read flip of one allele
    c=rng.multinomial(m,probs,size=(R,K))  # R,K,4
    if e>0:
        # flip: each read with prob e flips allele i or j (1/2 each)
        out=np.zeros_like(c)
        # transitions for flip of allele i: 11<->01, 10<->00 ; allele j: 11<->10, 01<->00
        fi={0:2,1:3,2:0,3:1}; fj={0:1,1:0,2:3,3:2}
        for s in range(4):
            k=c[...,s]; nf=rng.binomial(k,e); ni=rng.binomial(nf,0.5); nj=nf-ni
            out[...,s]+=k-nf; out[...,fi[s]]+=ni; out[...,fj[s]]+=nj
        c=out
    n11,n10,n01=c[...,0].astype(float),c[...,1].astype(float),c[...,2].astype(float)
    S=[x.sum(-1) for x in scores(n11,n10,n01,eps)]
    return S
def lin_probs(t,fX,fY): return [t*fY,t*(fX-fY),0,1-t*fX]
def sib_probs(t,fX,fY): return [0,t*fX,t*fY,1-t*(fX+fY)]
if __name__=="__main__":
    import sys
    t=0.9; fY=0.5
    print("Q1 linear: P(anc>same), fY=0.5,fX=fY+g, t=0.9; also t=0.6")
    for tt in (0.9,0.6):
     for e in (0,0.005,0.01,0.02):
      for eps in (0.01,0.03):
        if e==0 and eps==0.03: continue
        for m in (5,15,30):
          row=[]
          for g in (0.01,0.03,0.05,0.1,0.2):
            need='>1000'
            for K in (1,2,3,5,10,20,30,50,100,200,500,1000):
                s,a,d,b=sim(lin_probs(tt,fY+g,fY),m,K,e,eps,R=1000 if K>=200 else 3000)
                if np.mean(a>s)>=0.95: need=str(K);break
            row.append(f"g={g}:{need}")
          print(f"t={tt} e={e} eps={eps} m={m}: "+"  ".join(row))
    print("\nQ3 false-positive: truly same clone (f=0.5), P(anc>same) with K pairs, m=15")
    for e in (0,0.005,0.01,0.02,0.04):
      for eps in (0.01,0.03):
        r=[]
        for K in (10,50,200):
          s,a,d,b=sim([t*0.5,0,0,1-t*0.5],15,K,e,eps,R=2000)
          r.append(f"K={K}:{np.mean(np.maximum(a,d)>s):.3f}")
        print(f"e={e} eps={eps}: "+" ".join(r))
    print("\nQ2 siblings fX=0.3,fY=0.3-g? use fX=0.35,fY=0.35-g; P(branch>max(same,anc,desc))")
    for e in (0,0.01,0.02):
      for m in (5,15,30):
        r=[]
        for g in (0.01,0.05,0.1):
          need='>200'
          for K in (1,2,3,5,10,20,50,100,200):
            s,a,d,b=sim(sib_probs(t,0.35,0.35-g),m,K,e,0.01,R=2000)
            if np.mean(b>np.maximum.reduce([s,a,d]))>=0.95: need=str(K);break
          r.append(f"g={g}:{need}")
        print(f"e={e} m={m}: "+" ".join(r))
