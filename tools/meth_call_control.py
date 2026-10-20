"""5mC call-confidence (ML) histogram and confident-methylated fraction per region.

usage: python3 meth_call_control.py CRAM

Platform/calibration control for pcdh_entropy.py: housekeeping promoters
should be unmethylated in both tumor and normal.
First used in lab_report/2026-10-20_hcc1395_pcdh_entropy/.
"""
import sys, pysam, collections
REF="/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
regions={"PCDH":("chr5",140780000,141520000),"GAPDH_prom":("chr12",6533500,6535000),"ACTB_prom":("chr7",5529000,5531000)}
f=sys.argv[1]; bam=pysam.AlignmentFile(f,reference_filename=REF)
for name,(c,s,e) in regions.items():
    h=collections.Counter(); n=0
    for r in bam.fetch(c,s,e):
        if r.is_secondary or r.is_supplementary or r.mapping_quality<20: continue
        mb=r.modified_bases
        if not mb: continue
        q2r=dict(r.get_aligned_pairs(matches_only=True))
        for (b,st,m),l in mb.items():
            if m!='m': continue
            for q,ml in l:
                rp=q2r.get(q)
                if rp is not None and s<=rp<e: h[min(ml//51,4)]+=1
    tot=sum(h.values())
    fr=[h[i]/tot for i in range(5)]
    hi=sum(h[i] for i in range(5) if i>=4); lo=h[0]
    print(f"{name}\tcalls={tot}\tML bins(0-50,51-101,102-152,153-203,204-255)="+",".join(f"{x:.3f}" for x in fr)+f"\tconf_meth_frac={hi/(hi+lo):.3f}")
