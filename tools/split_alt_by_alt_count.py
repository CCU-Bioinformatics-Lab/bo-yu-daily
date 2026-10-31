#!/usr/bin/env python3
"""Split-alt rate (minor-HP share of tagged alt > 0.1) by tagged alt count, for diplosim runs.
Usage: python3 -I tools/split_alt_by_alt_count.py RUN_DIR_WITH_s*/diplosim.tsv LABEL
"""
import csv, glob, sys
def collect(it):
    rows=[]
    for v in it:
        d=sum(v); a=v[1]+v[3]+v[5]
        if d==0 or a<3 or a/d<0.08: continue
        at=v[1]+v[3]
        if at>=3: rows.append((at,min(v[1],v[3])/at))
    return rows
def rates(rows):
    out=[]
    for lo,hi in ((3,10),(10,20),(20,999)):
        sel=[f for at,f in rows if lo<=at<hi]; out.append(sum(f>0.1 for f in sel)/len(sel))
    return out+[sum(f>0.1 for _,f in rows)/len(rows)]
sim=collect([int(r[k]) for k in ("HP1_REF","HP1_ALT","HP2_REF","HP2_ALT","HP0_REF","HP0_ALT")] for f in glob.glob(sys.argv[1]+"/s*/diplosim.tsv") for r in csv.DictReader(open(f),delimiter="\t"))
print(sys.argv[2], " ".join(f"{x:.4f}" for x in rates(sim)))
