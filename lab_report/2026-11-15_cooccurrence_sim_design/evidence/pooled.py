# pooled alternative: one shared Beta over all X-Y pairs (= fraction (fX-fY)/fX shared by the clone pair)
import numpy as np
from scipy.special import betaln
rng=np.random.default_rng(3)
t=0.9;fY=0.5
def need(g,m,e,eps,R=2000):
    for K in (1,2,3,5,10,20,30,50,100,200,500):
        p=np.array([t*fY,t*g,0,1-t*(fY+g)])
        c=rng.multinomial(m*K,p,size=R).astype(float)
        if e>0:  # false 10 / 01 from flips (approx: 11->10 or 01, 00->10 or 01, rates e/2)
            f11=rng.binomial(c[:,0].astype(int),e); f00=rng.binomial(c[:,3].astype(int),e)
            a=rng.binomial(f11,.5); b=rng.binomial(f00,.5)
            c[:,1]+=a+b; c[:,2]+=(f11-a)+(f00-b); c[:,0]-=f11
        n11,n10,n01=c[:,0],c[:,1],c[:,2]
        le,l1,l2=np.log(eps),np.log1p(-eps),np.log1p(-2*eps)
        d=n10*(l1-le)+n11*(l1-l2)+betaln(n11+1,n10+1)
        if np.mean(d>0)>=.95: return K
    return '>500'
for e in (0,0.01,0.02):
  for eps in (0.01,0.03):
    for m in (5,15,30):
      print(f"pooled e={e} eps={eps} m={m}:",{g:need(g,m,e,eps) for g in (0.01,0.03,0.05,0.1,0.2)})
# false positive pooled: true same clone
for e in (0.005,0.01,0.02,0.04):
  for eps in (0.01,0.03):
    c=rng.multinomial(15*200,[t*.5,0,0,1-t*.5],size=2000).astype(float)
    f11=rng.binomial(c[:,0].astype(int),e);a=rng.binomial(f11,.5);f00=rng.binomial(c[:,3].astype(int),e);b=rng.binomial(f00,.5)
    n11=c[:,0]-f11;n10=a+b
    le,l1,l2=np.log(eps),np.log1p(-eps),np.log1p(-2*eps)
    d=n10*(l1-le)+n11*(l1-l2)+betaln(n11+1,n10+1)
    print(f"pooled FP same-clone K=200 m=15 e={e} eps={eps}: P(anc>same)={np.mean(d>0):.3f}")
