#!/usr/bin/env python3
"""CN state (total, minor) and rough multiplicity: ASCAT 5kHz on real HCC1395 SNVs vs diplosim --prop-pos-lost 0.45.
Usage: python3 -I tools/cn_state_ascat_vs_diplosim.py TMP_DIR [DIPLOSIM_ARGS...]   (run from repo root;
       default args: --prop-pos-lost 0.45)
"""
import csv, random, subprocess, sys, os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
S=sys.argv[1]; EXTRA=sys.argv[2:] or ["--prop-pos-lost","0.45"]; D="diplosim/target/release/diplosim"
def ok(alt,d): return alt>=3 and alt/d>=0.08
def run(seed):
    out=f"{S}/s{seed}"; n=random.Random(seed).randint(2,8)
    subprocess.run([D,"--n-clones",str(n),"--n-snv","31595","--seed",str(seed),"--coverage","53","--min-tumour-purity","1","--max-tumour-purity","1","--out",out,*EXTRA],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    f=f"{out}/diplosim.tsv"
    if not os.path.exists(f): return None
    c=Counter(); m=Counter(); vt=[]
    for r in csv.DictReader(open(f),delimiter="\t"):
        alt,d=int(r["VAR_COUNT"]),int(r["DEPTH"])
        if d==0 or not ok(alt,d): continue
        a,b=round(float(r["CN_A"])),round(float(r["CN_B"])); t=a+b
        c[(t,min(a,b))]+=1
        m[min(round(alt/d*t),t) if t else 0]+=1
    subprocess.run(["rm","-rf",out]); return c,m
if __name__=="__main__":
    # ASCAT on real called SNVs
    cn={(r["chrom"],r["pos"]):(int(r["total_cn"]),int(r["minor_cn"])) for r in csv.DictReader(open("lab_report/2026-10-30_ascat_hcc1395_5khz/tables/snv_cn.tsv"),delimiter="\t")}
    rc=Counter(); rm_=Counter()
    for r in csv.DictReader(open("lab_report/2026-10-31_diplosim_ppc_hcc1395_lost045/tables/real_per_snv.tsv"),delimiter="\t"):
        k=(r["chrom"],r["pos"]); v=[int(r[x]) for x in ("ref1","alt1","ref2","alt2","ref0","alt0")]
        d=sum(v); alt=v[1]+v[3]+v[5]
        if d==0 or not ok(alt,d) or k not in cn: continue
        t,mi=cn[k]; rc[(t,mi)]+=1; rm_[min(round(alt/d*t),t)]+=1
    sc=Counter(); sm=Counter(); n=0
    with ProcessPoolExecutor(16) as ex:
        for res in ex.map(run,range(1,41)):
            if res: sc.update(res[0]); sm.update(res[1]); n+=1
    print("sim seeds",n)
    R=sum(rc.values()); Ss=sum(sc.values())
    keys=sorted(set(rc)|set(sc),key=lambda k:-(rc[k]/R+sc[k]/Ss))
    print("state(total,minor)\tASCAT\tdiplosim")
    for k in keys[:16]: print(f"{k}\t{rc[k]/R:.3f}\t{sc[k]/Ss:.3f}")
    def grp(c,T):
        g=Counter()
        for (t,mi),v in c.items():
            g["LOH" if mi==0 else "het"]+=v/T
            g[f"total={t}" if t<=4 else "total>=5"]+=v/T
            g["balanced(major==minor)" if t-mi==mi and t>0 else "unbal"]+=v/T
        return g
    gr,gs=grp(rc,R),grp(sc,Ss)
    print("\nsummary\tASCAT\tdiplosim")
    for k in ["LOH","het","total=1","total=2","total=3","total=4","total>=5","balanced(major==minor)"]: print(f"{k}\t{gr[k]:.3f}\t{gs[k]:.3f}")
    print("mean total CN\t%.2f\t%.2f"%(sum(t*v for (t,_),v in rc.items())/R, sum(t*v for (t,_),v in sc.items())/Ss))
    MR=sum(rm_.values()); MS=sum(sm.values())
    print("\nest. multiplicity (round(VAF*total))\tASCAT\tdiplosim")
    for k in range(0,6): print(f"{k}\t{rm_[k]/MR:.3f}\t{sm[k]/MS:.3f}")
