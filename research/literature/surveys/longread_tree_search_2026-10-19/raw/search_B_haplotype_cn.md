# Search B: haplotype-specific CN, phased-SNV timing, and long-read tumor evolution

Search date: 2026-10-19. Each claim below comes from a page fetched in this session (URL given). The note "search-snippet only" marks claims taken from search results only.

## Conclusion

- No 2024–2026 paper was found that builds a clone tree **inside one model** that uses long-read HP1/HP2 phasing (for example, phased-SNV multiplicity, haplotype-specific CN, or WGD timing from phased reads).
- One paper meets the inclusion rule: Liu et al. (melanoma sublines). It uses ScisTree for the tree and TreeHarmonizer for event placement. Long-read features (Severus SVs, Wakhan CN/LOH) enter **after** the tree is built, as placed events. Phasing is not a tree constraint.
- Every other long-read haplotype tool found is a feature producer: Wakhan, Severus, SAVANA, LongPhase-S, LongPhase-TO, ClairS-TO, and ChromoDethripsis.
- No method was found for WGD timing or CN-gain timing from phased long reads. This gap is open. The only related work found is the excluded Donmez & Kolmogorov AACR 2026 abstract.

---

## Section A: Tree, ordering, and timing methods (main section)

### A1. Long-read sequencing of single cell-derived melanoma subclones/sublines (TreeHarmonizer framework)
- **Authors:** Yuelin Liu (first) … Mikhail Kolmogorov (last). Corresponding authors: C.-P. Day, S.C. Sahinalp, M. Kolmogorov.
- **Year/venue:** bioRxiv 2025, DOI 10.1101/2025.08.28.672865 (PMC12424993). The PMC page says that a peer-reviewed version is in Nature Communications. A search result lists it as https://www.nature.com/articles/s41467-026-75172-9 (title "...melanoma sublines..."). The Nature page redirected to a login, so the journal version was **not fetched**.
- **Software:** TreeHarmonizer, https://github.com/KolmogorovLab/TreeHarmonizer (README fetched). It also uses ScisTree, Severus, Wakhan, DeepVariant, Margin/WhatsHap, and Padfoot (https://github.com/KolmogorovLab/Padfoot).
- **Platform/material:** ONT long reads from 23 single-cell-derived sublines of a mouse melanoma cell line, plus a splenocyte normal.
- **Long-read features:** reads phased and haplotagged with Margin/WhatsHap; Severus multi-sample phased SVs; Wakhan CN and LOH ("tumor phased VCFs to detect LOH"); 5mC methylation; SNVs.
- **Role:** tree_input (SNVs into ScisTree) plus event placement (SV/CNA onto branches). Phasing is **not** a topology constraint. In TreeHarmonizer, haplotype logic is only a parsimony rule: "we assume that the loss occurred on the other haplotype".
- **Tree/event type and algorithm:** ScisTree (a neighbor-joining-based cell-lineage tree search) on 10,862 informative SNVs, with a grid search over FP/FN priors. TreeHarmonizer then places each SNV/SV/CNA at the MRCA of the sublines that carry it (trunk = clonal, internal = subclonal, leaf = private). It uses a clade-size support threshold. It also re-genotypes SNVs that Wakhan CN=0/1 or SV deletions explain. CNA placement is a per-node summary, not a per-event placement (README).
- **Evaluation:** No ground-truth tree. Placement is checked with a partition-function score (Mehrabadi et al. 2025). The study compares calls to bulk WES and scRNA-seq. Pseudobulk mixtures of sublines serve as caller benchmarks.
- **Evidence:** "TreeHarmonizer takes as input (i) a phylogenetic tree and (ii) individual SNV, SV, and CNA calls for every subline." / "We develop a computational framework for harmonization and joint analysis of different variant types" — https://pmc.ncbi.nlm.nih.gov/articles/PMC12424993/ ; README: "a utility for placing called variants onto a pre-existing phylogenetic tree" — https://github.com/KolmogorovLab/TreeHarmonizer
- **Relevance to PhyClone + longphase-s:** This paper uses a sequencing design (single-cell-derived sublines) where long-read SV/CN events are placed onto a tree after it is built. PhyClone could use the same post-hoc placement for HP-tagged SV/CN events. The design does not apply directly to bulk mixtures like our `tX_nY` samples.
- **Status:** new (not in the known list). A search result says that an AACR 2025 abstract from the same group used Trisicell for the tree. This claim is search-snippet only.

### A2. Already-known tree methods found again
- **MEDICC2** (Kaufmann … Schwarz, Genome Biology 2022): a WGD-aware phylogeny from haplotype-specific CN. **already_known**. No long-read application was found ("no evidence of MEDICC2 on nanopore" from the search). Source (search result only): https://www.mdc-berlin.de/research/publications/medicc2-whole-genome-doubling-aware-copy-number-phylogenies-cancer-evolution
- **Sakamoto 2022 lung long-read phasing** (Nat Commun, PMC9203510): **already_known**. Seen only in search results.

### A3. Related but out of scope (short-read or not long-read)
- **Refphase** (Watkins … Schwarz; bioRxiv 10.1101/2022.10.13.511885; PLoS Comput Biol 2023). It infers haplotype-specific CN by multi-sample reference phasing and detects parallel evolution around WGD. It uses short reads only and has no long-read input. Fetched: https://www.biorxiv.org/content/10.1101/2022.10.13.511885v1 . Quote: "We introduce Refphase, an algorithm that leverages this multi-sampling approach to infer haplotype-specific copy numbers". Relevance: it is a template for HP-specific CN across `tX_nY` subsamples.
- **CNVeil** (Yuan … Zhou; bioRxiv 2026, 10.64898/2026.07.20.739667; PMC13419527). It infers single-cell haplotype-specific CN and then builds a tree with MEDICC2. The fetched text does not mention long reads. **Not long-read**, so it is excluded from the main list. Fetched: https://pmc.ncbi.nlm.nih.gov/articles/PMC13419527/

---

## Section B: Feature-producing tools (no tree or ordering)

### B1. Wakhan — haplotype-specific CN from long reads
- **Authors:** Tanveer Ahmad (first) … Mikhail Kolmogorov (last). medRxiv, posted 2025-12-15, DOI 10.64898/2025.12.11.25342098.
- **Code:** https://github.com/KolmogorovLab/Wakhan (MIT).
- **Platform/material:** tumor/normal long reads (ONT/PacBio), CASTLE cell-line panel with de novo assemblies, breast cancer, and pediatric cancers.
- **Long-read feature:** phased germline SNPs. Wakhan extends phasing to chromosome scale through haplotype coverage imbalance and fixes phase switches. It uses Severus phased SV breakpoints as segment boundaries. A haplotype coverage model gives integer HP-specific CN.
- **Role:** feature_only. Segments that deviate from the model are flagged as subclonal. It does **not** model a clone mixture.
- **Evidence:** "Wakhan also marks CNA segments with substantial deviation from the coverage model as subclonal." / "does not explicitly model a mixture of tumor clones" / "unambiguous clonal deconvolution requires multiple matching tumor samples as input." — https://www.medrxiv.org/content/10.64898/2025.12.11.25342098v1.full-text
- **Relevance:** This is the best existing source of HP1/HP2 integer CN per segment. PhyClone needs HP-specific major/minor CN with haplotype labels, and Wakhan can supply them.

### B2. Severus — phased somatic SV caller
- **Authors:** Ayse Keskus … Mikhail Kolmogorov. medRxiv 2024 (10.1101/2024.03.22.24304756; PMC10996739). The page says that a Nature Biotechnology version exists.
- **Code:** https://github.com/KolmogorovLab/Severus
- **Feature:** assigns haplotypes to reads, reports SVs in cis/trans, and groups complex events in a phased breakpoint graph (cluster ID).
- **Role:** feature_only. "None is described" for tree or ordering (fetched summary).
- **Evidence:** "SVs identified as part of a complex event contain a cluster ID." — https://pmc.ncbi.nlm.nih.gov/articles/PMC10996739/
- **Relevance:** HP-tagged SV breakpoints could become extra events or CN-segment boundaries in a PhyClone extension.

### B3. SAVANA — somatic SV + SCNA + purity/ploidy
- **Authors:** Hillary Elrick … Isidro Cortes-Ciriano. Nature Methods 2025;22(7):1436–1446, DOI 10.1038/s41592-025-02708-0.
- **Code:** https://github.com/cortes-ciriano-lab/savana
- **Feature:** allele-specific CN, SVs at single-haplotype resolution with phased BAMs, purity from BAF in LOH regions, and a ploidy grid search.
- **Role:** feature_only. No subclonal CN model and no tree.
- **Evidence:** "SAVANA provides functionalities to detect somatic SVs at single-haplotype resolution" — https://pmc.ncbi.nlm.nih.gov/articles/PMC12240814/
- **Relevance:** It provides a purity estimate and CN input for PhyClone. It does not produce HP labels on SNVs.

### B4. LongPhase-S — somatic haplotyping + purity
- **Authors:** Ming-En Ho … Yao-Ting Huang (with Zhenxian Zheng and Ruibang Luo). bioRxiv, posted 2025-11-24, DOI 10.1101/2025.11.20.689492.
- **Code:** not given on the fetched page.
- **Feature:** anchors each somatic read to a parental germline haplotype. It trains a phase-aware purity estimator and recalibrates somatic variants.
- **Role:** feature_only. No clone tree or timing is mentioned.
- **Evidence:** "Building on somatic haplotyping, LongPhase-S trains a phase-aware purity estimator that outperformed existing methods." — https://www.biorxiv.org/content/10.1101/2025.11.20.689492v1
- **Relevance:** This is our own upstream tool. It supplies the per-SNV HP1/HP2 anchor and a purity estimate that PhyClone currently lacks.

### B5. LongPhase-TO — tumor-only somatic haplotype graph (new, about 1 month old)
- **Authors:** Zhen-Yu Chen … Yao-Ting Huang. bioRxiv 2026, DOI 10.64898/2026.09.14.751225.
- **Code:** https://github.com/CCU-Bioinformatics-Lab/longphase-to
- **Feature:** joint graph of germline and somatic alleles. A somatic allele branches from its parental haplotype (for example, HP2-1 from HP2). It detects arm-level LOH and estimates tumor **DNA fraction** (not cellular purity) from haplotype imbalance. It recalibrates ClairS-TO and DeepSomatic-TO calls.
- **Role:** feature_only. The HP-x-y lineage is a phasing construct. The paper does not present it as a phylogeny.
- **Evidence:** "resolves LOH and tumor DNA fraction internally from heterozygosity depletion and haplotype imbalance" — https://www.biorxiv.org/content/10.64898/2026.09.14.751225v1.full
- **Relevance:** The HP2-1-under-HP2 encoding is very close to a per-SNV "parental haplotype + somatic branch" label. This label could constrain PhyClone's multiplicity and the haplotype that a CN event acts on. Note one caveat: the DNA fraction it estimates is not the same as cellular purity.

### B6. ClairS-TO — tumor-only somatic small-variant caller
- Lei Chen, Zhenxian Zheng … Ruibang Luo. Nature Communications 2025, DOI 10.1038/s41467-025-64547-z. Code: HKU-BAL/ClairS-TO. **Source: search snippet only**; the paper was not fetched.
- Role: feature_only (SNV input).

### B7. ChromoDethripsis — haplotype-specific assembly of chromothriptic chromosomes
- **Authors:** Jannat Ijaz … Peter J. Campbell. Cell Genomics 2024;4(2):100484 (PMC10879010).
- **Code:** https://github.com/jannatjiaz/ChromoDethripsis ; https://github.com/jannatjiaz/AssemblyBasedHaplotypeResolution
- **Material:** esophageal adenocarcinoma (HiFi, Hi-C, and others).
- **Role:** feature_only. It builds haplotype-resolved assemblies and does **no** chromothripsis timing. The study compares initial and relapse samples only for epigenome stability.
- **Evidence:** "haplotype-aware de novo methods were required to generate contiguous cancer genome assemblies" — https://pmc.ncbi.nlm.nih.gov/articles/PMC10879010/

### B8. Other items seen in search results only (not fetched; unverified)
- Garg et al. 2023 Nat Commun: COLO829 chromosome-scale haplotype-resolved reconstruction (PMC10011606). Assembly only.
- Decoil: ecDNA reconstruction from nanopore, using a breakpoint graph and LASSO. No haplotype CN or tree.
- NanoSV / Cretu Stancu et al. 2017: phasing of chromothripsis breakpoints in germline cases. Not a tumor-evolution study.
- An ONT poster, "clone- and haplotype-specific CNV inference in heterogeneous bulk", and an NIH CCR 2022 webinar describe count-based clone- and allele-specific CNV inference from phased nanopore reads. The NIH page (fetched: https://bioinformatics.ccr.cancer.gov/btep/classes/characterizing-copy-number-variations-and-extrachromosomal-dna-amplicons-in-heterogeneous-cancer-samples-with-nanopore-sequencing) gives **no tool name, author, or paper**. The ONT page returned 404. **Unverified; worth a follow-up.**
- DeepSomatic and nanomonsv: no page fetched. Not verified in this search.
- Vo et al. medRxiv 2026, "Long-Read Haplotype Phasing Resolves Allelic Configuration…": a clinical cis/trans study with no tree. Search snippet only.

### Excluded (seen and dropped by rule)
- Donmez & Kolmogorov AACR 2026 abstract 6912 (point-mutation timing on H2009/H1437). It came up in search results and was removed under the exclusion list.

---

## Summary table

| # | Tool / paper | Year, venue | Builds tree/order? | Long-read feature | Role | Status |
|---|---|---|---|---|---|---|
| A1 | TreeHarmonizer + ScisTree (Liu…Kolmogorov, melanoma sublines) | 2025 bioRxiv → Nat Commun 2026 | Yes (ScisTree tree + variant placement) | phased SVs (Severus), Wakhan CN/LOH, methylation | tree_input + post-hoc placement | new |
| A2 | MEDICC2 | 2022 Genome Biol | Yes | none (short read) | — | already_known |
| A2 | Sakamoto 2022 lung | 2022 Nat Commun | — | phasing | — | already_known |
| A3 | Refphase | 2022/2023 | HS-CN, parallel evolution | none | out of scope | — |
| A3 | CNVeil (+MEDICC2) | 2026 bioRxiv | Yes (via MEDICC2) | none (scDNA) | out of scope | — |
| B1 | Wakhan | 2025 medRxiv | No | HP-specific CN, phase extension | feature_only | new |
| B2 | Severus | 2024 medRxiv / Nat Biotech | No | phased SV, cis/trans | feature_only | new |
| B3 | SAVANA | 2025 Nat Methods | No | haplotype SV, ASCN, purity | feature_only | new |
| B4 | LongPhase-S | 2025 bioRxiv | No | somatic haplotyping, purity | feature_only | new |
| B5 | LongPhase-TO | 2026 bioRxiv | No | somatic haplotype graph, LOH, DNA fraction | feature_only | new |
| B6 | ClairS-TO | 2025 Nat Commun | No | somatic SNV | feature_only | snippet only |
| B7 | ChromoDethripsis | 2024 Cell Genomics | No | haplotype-specific assembly | feature_only | new |

## Failed or empty searches
- "whole genome doubling timing phased long reads multiplicity": no long-read WGD-timing method found.
- "molecular timing copy number gains phased long reads": only short-read timing tools (MutationTimeR, AmplificationTimeR, GRITIC) came up.
- "chromothripsis timing long reads": only assembly or breakpoint phasing (Ijaz 2024, Cretu Stancu 2017). No timing.
- "HATCHet long reads": no HATCHet/HATCHet2 long-read application found.
- "MEDICC2 long-read nanopore": no application found.
- "single-cell long-read WGS CN phylogeny": no results.
- "multi-region long-read allele-specific CN phylogeny": no results.
- HG008 T2T tumor-normal assembly: a dataset paper and NIST draft only. No evolution analysis.
- Fetch failures: the Nature Comms melanoma page (login redirect), the AACR 2025 abstract 5049 "Haplotype-specific copy number profiling from long reads" (HTTP 403; probably Wakhan, unverified), the ONT clone/haplotype CNV poster (404), and the UMD talk page (SSL error).
