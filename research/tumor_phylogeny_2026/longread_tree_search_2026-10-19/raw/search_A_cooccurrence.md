# Search A: tree tools that use same-read co-occurrence or phasing

Search date: 2026-10-19. Angle: same-read and same-haplotype co-occurrence of somatic SNVs, read-based phasing, PS/HP tags, germline-anchored phasing, and pair ordering.

**Main finding.** No peer-reviewed tool or preprint was found that builds a tumor clone or mutation tree from long-read co-occurrence, HP, or PS evidence. The only tools whose tree model uses read-level SNV co-occurrence are short-read tools (TreeClone; its precursor PairClone has no tree). BitPhylogeny uses a read-level multi-locus pattern, but for methylation. The long-read papers found either use phasing only for interpretation or validation, or phase without building a tree (LongPhase-S, LongPhase-TO).

---

## 1. TreeClone: tumor subclone phylogeny from mutation pairs  [already_known]
- **Authors:** Tianjian Zhou ... Yuan Ji (with S. Sengupta and P. Mueller). arXiv 2017. Published in Annals of Applied Statistics 13(2), 2019.
- **DOI/URL:** 10.1214/18-AOAS1224; https://arxiv.org/abs/1703.03853
- **Software:** TreeClone, http://www.compgenome.org/treeclone. LocHap extracts the mutation pairs.
- **Platform/material:** Illumina paired-end, 100 bp reads, WES. Real data: 4 lung adenocarcinoma samples from 1 patient (69 pairs). Also simulations.
- **Long-read feature:** same-read co-occurrence of 2 nearby SNVs (local haplotype). Reads are complete or missing one locus.
- **Role:** transferable_only (tree_input in its own model, but built for short reads).
- **Tree/algorithm:** Each subclone has a 2x2 binary haplotype matrix per pair. The model is Bayesian latent feature allocation with a tree prior (parent vector, children inherit and add mutations). Inference: MCMC with Gibbs/MH steps, parallel tempering, and trans-dimensional moves.
- **Evaluation:** simulation truth (error rates for subclone number, tree, genotypes, and proportions). Compared with Cloe, PhyloWGS, and PairClone. Real data has no truth; the authors used goodness-of-fit checks instead.
- **Limits:** CN-neutral regions only ("We focus our analysis in copy number neutral regions"). Uses only 2-SNV pairs.
- **Evidence:** "pairs of two proximal SNVs that can be mapped by the same short reads"; "The use of the tree structure in the prior greatly strengthens inference." Source: https://arxiv.org/abs/1703.03853 and https://arxiv.org/html/1703.03853v2
- **Relevance to PhyClone + longphase-s:** This is the closest model template. Replace short-read pairs with long-read k-SNV haplotypes and HP tags. Then lift the CN-neutral restriction using haplotype-specific CN.

## 2. PairClone: Bayesian subclone caller from mutation pairs  [new; no tree, near-miss]
- **Authors:** Tianjian Zhou ... Yuan Ji. arXiv 2017. Published in JRSS Series C 68(3), 2019.
- **DOI/URL:** 10.1111/rssc.12328; https://arxiv.org/abs/1702.07465
- **Software:** http://www.compgenome.org/pairclone
- **Platform/material:** short reads, real and simulated data.
- **Feature:** same-read SNV pair co-occurrence.
- **Role:** transferable_only. **It fails the tree-building inclusion rule.** The model uses a categorical IBP over subclone genotypes and has no tree. It is listed only because TreeClone builds on it.
- **Evidence:** "model short reads mapped to pairs of proximal SNVs ... estimate posterior probabilities of the number, genotypes and population frequencies of subclones." Source: https://arxiv.org/abs/1702.07465
- **Relevance:** It shows the pair likelihood before the tree prior is added. This is useful for ablation designs.

## 3. BitPhylogeny: probabilistic intra-tumor phylogenies  [new; transferable]
- **Authors:** Ke Yuan ... Niko Beerenwinkel (with Sakoparnig and Markowetz). Genome Biology 16:36, 2015.
- **DOI/URL:** 10.1186/s13059-015-0592-6; https://pmc.ncbi.nlm.nih.gov/articles/PMC4359483
- **Software:** https://bitbucket.org/ke_yuan/bitphylogeny (Python/R, GPL3).
- **Platform/material:** bisulfite methylation tag sequencing (454/Roche) of colon cancer glands. Also single-cell exome of MPN and simulations.
- **Feature:** a read-level multi-locus binary pattern ("methyltype"), i.e. co-occurrence on one molecule. Here the pattern is CpG methylation, not SNVs.
- **Role:** transferable_only (tree_input in its own model).
- **Tree/algorithm:** tree-structured stick-breaking process (TSSB) mixture. Clones can be inner or leaf nodes. Inference is MCMC (Gibbs plus a swap-clone move).
- **Evaluation:** simulations with known truth, compared with other methods. Real data has no truth.
- **Evidence:** "the phasing of SNVs can be improved with longer reads"; the model "does not rely on mutation frequencies." Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC4359483
- **Relevance:** It treats each read haplotype as one draw from a clone on a TSSB tree. The same idea could work for long-read multi-SNV haplotypes. Note that PhyClone already uses a related tree prior.

## 4. Sakamoto et al., phasing analysis of lung cancer genomes with a long-read sequencer  [already_known]
- **Authors:** Yoshitaka Sakamoto ... Ayako Suzuki. Nature Communications 2022. DOI 10.1038/s41467-022-31133-6.
- **URL fetched:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9203510/
- **Software:** no new tool. Uses WhatsHap (phasing/haplotag), PyClone-VI, ClonEvol, and FACETS.
- **Platform/material:** ONT plus short reads, 20 NSCLC patients. scDNA-seq validated 2 cases.
- **Feature:** same-read co-occurrence of mutation pairs and HP-tagged reads.
- **Role:** **validation_only.** The tree comes from VAF (PyClone-VI to ClonEvol). Phased pairs were compared with that tree afterward.
- **Evidence:** "44 mutation pairs were successfully assigned to different clones"; "a large fraction of the mutation pairs were still mapped to the same clones".
- **Relevance:** This is a real-data case where pair phasing disagrees with VAF clones. It motivates using pairs as a constraint inside PhyClone.

## 5. Liu et al., long-read sequencing of single-cell-derived mouse melanoma sublines  [already_known]
- **Authors:** Yuelin Liu ... Mikhail Kolmogorov. Nature Communications 17:8740, 2026. DOI 10.1038/s41467-026-75172-9. bioRxiv 10.1101/2025.08.28.672865.
- **URL fetched:** https://pmc.ncbi.nlm.nih.gov/articles/PMC13493970/
- **Software:** ScisTree for the tree. Margin and WhatsHap for phasing. Wakhan in unphased mode.
- **Platform/material:** ONT, 23 single-cell-derived mouse melanoma sublines.
- **Feature:** the tree input is SNV presence or absence per subline. Haplotagging is done, but the paper does not use it for the tree. Germline phasing was limited because the strain is inbred.
- **Role:** tree_input for SNV genotypes only. Phasing is **not** a tree input. Other events (SV, CN, methylation) are placed on the tree afterward.
- **Evidence:** BAMs "were phased and haplotagged using margin and Whatshap"; tree from 10,862 filtered SNVs via ScisTree.
- **Relevance:** It is a long-read cell-line design with subline truth. It does not model co-occurrence.

## 6. Foltz et al., somatic mutation phasing and haplotype extension using linked reads in multiple myeloma  [new; no tree, near-miss]
- **Authors:** Steven M. Foltz ... Li Ding. bioRxiv 2024 (10.1101/2024.08.09.607342). PMC11326269.
- **Software:** SomaticHaplotype, https://github.com/ding-lab/SomaticHaplotype
- **Platform/material:** 10x linked reads, 23 samples from 14 MM patients. 79.4% of 20,705 somatic mutations were phased.
- **Feature:** barcode co-occurrence of REF/ALT at mutation pairs, and haplotype assignment.
- **Role:** **interpretation only. No tree is built, so it fails the inclusion rule.** It is not the excluded Liu 2021 MM paper. However, it may overlap with the project's removed "B02 myeloma" entry. Check this before you cite it.
- **Evidence:** "we directly observed both mutations occurring without the other, and we never observed them together" (two NRAS hotspot mutations in different subclones). Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11326269/
- **Relevance:** Its pair logic (both alone, never together, so branching) is the evidence type PhyClone would need. It gives no tree algorithm.

## 7. LongPhase-S: purity estimation and variant recalibration with somatic haplotyping  [new; phasing only, no tree]
- **Authors:** Ming-En Ho ... Yao-Ting Huang. bioRxiv, posted 2025-11-24. DOI 10.1101/2025.11.20.689492.
- **Software:** https://github.com/CCU-Bioinformatics-Lab/longphase-s
- **Platform/material:** paired tumor-normal long reads (ONT/PacBio), cell lines.
- **Feature:** somatic haplotags HP1-1, HP2-1, and HP3. These anchor somatic reads to germline HP1/HP2. The tool also outputs a purity estimate.
- **Role:** upstream feature producer. **No tree.** The authors say a "fully joint model of purity, ploidy, and subclonality" is future work.
- **Evidence:** "HP1-1 and HP2-1 represent the somatically altered descendants of HP1 and HP2". Source: https://www.biorxiv.org/content/10.1101/2025.11.20.689492v1.full
- **Relevance:** This is the project's own input source. No downstream tree method that consumes its tags was found.

## 8. LongPhase-TO: somatic haplotype reconstruction from tumor-only long reads  [new; phasing only, no tree]
- **Authors:** Zhen-Yu Chen ... Yao-Ting Huang. bioRxiv 2026 (DOI 10.64898/2026.09.14.751225).
- **Software:** https://github.com/CCU-Bioinformatics-Lab/longphase-to
- **Platform/material:** tumor-only long reads, 8 datasets from 6 cancer cell lines. Median 2.9x haplotype block N50 versus germline phasers.
- **Feature:** joint germline and somatic phasing graph with lineage-aware branching (HP1 to HP1-1).
- **Role:** upstream only. **No clone tree is built.**
- **Evidence:** "This lineage-aware traversal preserves clonal ancestry (e.g., HP1-1 from HP1)". Source: https://www.biorxiv.org/content/10.64898/2026.09.14.751225v1.full
- **Relevance:** Its parent-to-descendant haplotype graph is a natural constraint source for HP-aware clone assignment in PhyClone.

## Seen but excluded
- Donmez & Kolmogorov, AACR 2026 abstract 6912 (pair timing from read co-occurrence). Excluded by rule. Seen at https://www.synapsesocial.com/papers/69d1fc4fa79560c99a0a1f07
- RCK (Aganezov & Raphael, Genome Research 2020): clone- and haplotype-specific karyotypes. It can use long-read SV linkage. It has no SNV tree, so it is off-angle. Seen only in a search snippet (unverified detail).
- LongSom (Dondi ... Beerenwinkel, Genome Research 2025): long-read scRNA somatic SNVs. Clones come from clustering. A tree was not confirmed (unverified).
- Numbat, CNAHap, Wakhan, HATCHet: haplotype-specific CN tools. None uses read-level SNV co-occurrence for a tree.

## Summary table

| # | Paper | Year | Platform | Feature | Role | Tree? | Status |
|---|---|---|---|---|---|---|---|
| 1 | TreeClone (Zhou...Ji) | 2017/2019 | short PE | SNV pair co-occurrence | transferable_only | Yes (Bayesian tree prior, MCMC) | already_known |
| 2 | PairClone (Zhou...Ji) | 2017/2019 | short PE | SNV pair co-occurrence | transferable_only | No (IBP) | near-miss |
| 3 | BitPhylogeny (Yuan...Beerenwinkel) | 2015 | bisulfite reads / scDNA | read-level multi-locus pattern | transferable_only | Yes (TSSB, MCMC) | new |
| 4 | Sakamoto...Suzuki | 2022 | ONT + short | pair co-occurrence, HP | validation_only | Yes (PyClone-VI + ClonEvol, VAF only) | already_known |
| 5 | Liu...Kolmogorov melanoma | 2026 | ONT | SNV genotypes; HP not used | tree_input (SNV only) | Yes (ScisTree) | already_known |
| 6 | Foltz...Ding | 2024 | 10x linked | barcode pair co-occurrence | interpretation only | No | near-miss |
| 7 | LongPhase-S (Ho...Huang) | 2025 | long read T/N | HP1-1/HP2-1/HP3 | upstream feature | No | new (no tree) |
| 8 | LongPhase-TO (Chen...Huang) | 2026 | long read T-only | lineage haplotype graph | upstream feature | No | new (no tree) |

## Searches that returned nothing useful (no new qualifying tool)
- "nanopore long-read tumor phylogeny phased somatic SNV clone tree method 2025"
- "haplotype-aware clonal tree inference long reads allele-specific copy number phylogeny tool"
- "PacBio HiFi tumor subclonal phylogeny haplotype-resolved somatic mutations clone tree"
- "linked reads 10x tumor clonal phylogeny phasing somatic mutations" (only Foltz, which has no tree)
- "mutually exclusive mutations phasing branching evolution single sample ... read co-occurrence"
- "single-molecule amplicon nanopore phased mutations clonal architecture leukemia clone tree"
- "ordering of mutations from haplotype phasing ... multiplicity method phylogeny"
- "RECOMB ISMB 2025 2026 phylogeny inference using read phasing ... long reads"
- "clone tree inference incorporating phasing constraints mutation pairs long reads combinatorial"
- "haplotype clonal deconvolution long-read germline SNP anchored ... tree"
- "haplotype-resolved CN phylogeny single-cell long-read DNA"
- "github tumor clone tree long reads phased reads co-occurrence tool"
- Supporting statement (practical guide review, PMC7867630, seen only in a snippet): "there is no published method that can automatically leverage the potential of mutually exclusive mutations".
