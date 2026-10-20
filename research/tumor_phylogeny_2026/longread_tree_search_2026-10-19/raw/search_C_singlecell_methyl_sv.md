# Search C: single-cell or low-input long read, long-read methylation lineage, long-read SV/ecDNA phylogeny

Search date: 2026-10-19. Tools: WebSearch and WebFetch.
Rule: a paper counts only when a tree-building step exists. I verified each claim below from a fetched page, unless it is marked **UNVERIFIED**.

## Conclusion

- One new paper passes the inclusion rule with a long-read-specific feature as tree input: **Hackett et al. 2026 (PCDH methylation barcodes)**.
- One new paper has a long-read SV-based "molecular phylogeny" of ecDNA. The tree is hand-built parsimony, so it is **borderline / does not count**.
- No published method builds a tree from single-cell long-read DNA (scNanoSeq-style) or from long-read scRNA isoform SNVs. This is a gap.
- The rest are validation-only or have no tree step.

---

## A. Included

### A1. In vivo lineage tracing across human tissues using methylation barcodes in the protocadherin gene cluster

- **Authors:** Samuel F. Hackett (first) ... Jamie Blundell (last).
- **Year / venue:** 2026, bioRxiv preprint.
- **DOI / URL:** 10.64898/2026.02.23.707349, https://www.biorxiv.org/content/10.64898/2026.02.23.707349v1.full
- **Software / code:** No named tool. Methods mention "custom workflow and scripts". I found no code URL in the fetched text (not fully read; **code availability UNVERIFIED**).
- **Platform:** ONT PromethION, whole-genome long-read methylation sequencing. The main barcode work also uses short-read data; the long-read part is an extension.
- **Single-cell or bulk:** Bulk. Each long read is one molecule from one cell, so each read acts as a single-cell barcode.
- **Material:** Peripheral blood. PD6646 = myeloproliferative neoplasm patient (granulocytes). KX004 = healthy donor (PBMC, polyclonal control).
- **Long-read feature:** Haplotype-phased 5mC epialleles. Reads are split by haplotype with WhatsHap (in the Clair3 workflow) and LongPhase v1.7. Each row of the matrix is one read across many PCDH CpGs.
- **Role:** tree_input.
- **Tree type and algorithm:** Read x CpG matrix per haplotype. Missing CpGs are imputed by kNN (k=3, Hamming). Then hierarchical clustering with Hamming distance and average linkage (UPGMA) gives a dendrogram.
- **Ground truth / evaluation:** Single-cell (colony) WGS phylogeny of the same patient PD6646. Dendrograms "closely resembled the ground truth phylogenetic tree". Clonal fractions matched. Branch lengths did not match well (semi-quantitative only). The two haplotype dendrograms were concordant.
- **Evidence quotes (fetched):**
  - "we carried out whole genome, long-read methylation sequencing on the Oxford Nanopore Technologies (ONT) platform"
  - "To assign ONT sequencing long-reads to their respective haploid genomes, we used the Whatshap software package"
  - "we carried out hierarchical clustering using Hamming distance and average linkage (UPGMA)"
  - "yielded dendrogram topologies that closely resembled the ground truth phylogenetic tree"
  - Source: https://www.biorxiv.org/content/10.64898/2026.02.23.707349v1.full
- **Relevance to PhyClone + longphase-s HP1/HP2:** It shows that LongPhase HP tags can split reads per haplotype and that per-read multi-CpG patterns carry lineage signal; a PhyClone extension could use HP-split per-read epialleles as an extra clone-assignment likelihood term.

---

## B. Borderline (tree exists but is manual) - does not count under the rule

### B1. An Atlas of Extrachromosomal DNA Structures Illuminates Its Evolution and Biogenesis in Cancer

- **Authors:** Chee Hong Wong (first, co-first with Kuo-Chen Wei) ... Kou-Juey Wu and Chia-Lin Wei (corresponding / last).
- **Year / venue:** 2025, bioRxiv preprint (posted 2025-12-25).
- **DOI / URL:** 10.64898/2025.12.24.696443, https://www.biorxiv.org/content/10.64898/2025.12.24.696443.full.pdf
- **Software / code:** ecLego3, https://github.com/cheehongsg/ecLego (ecDNA reconstruction, not a tree tool).
- **Platform:** ONT long reads (HMW DNA); PacBio size selection is also mentioned in methods.
- **Single-cell or bulk:** Bulk; primary (n=10) and recurrent (n=10) GBM tumors, plus models.
- **Long-read feature:** Full ecDNA circular structures and SV junctions that define ecDNA "subspecies".
- **Role:** tree_input (for the ecDNA molecular phylogeny), but the tree step is manual.
- **Tree type and algorithm:** "Molecular phylogeny" of ecDNA subspecies. Nodes are subspecies; edges are stepwise SV/deletion acquisitions. The paper describes it as parsimonious. I found no named algorithm; methods mention "rigorous manual inspection". So I classify it as a **manual tree**.
- **Ground truth / evaluation:** None for the tree.
- **Evidence quotes (fetched PDF text):**
  - "Comparative analysis of acquired deletions among the subspecies enabled us to reconstruct their molecular phylogenies and reveal parsimonious evolutionary paths"
  - "Reconstructed molecular phylogeny illustrating the parsimonious evolution of ecDNA subspecies in A15_P. Nodes represent individual subspecies"
- **Relevance to PhyClone + longphase-s:** Low; it shows SV-junction characters on single long reads can order ecDNA variants, but it is not a clone tree of SNVs.

---

## C. Validation only

### C1. Ongoing chromothripsis underpins osteosarcoma genome complexity and clonal evolution

- **Authors:** Jose Espejo Valle-Inclan (first) ... Isidro Cortés-Ciriano (last).
- **Year / venue:** 2025, Cell 188:352-370; preprint bioRxiv 2023.
- **DOI / URL:** 10.1016/j.cell.2024.12.005; preprint https://www.biorxiv.org/content/10.1101/2023.12.29.573403v1.full
- **Platform:** Multi-region short-read WGS; ONT WGS on selected cases.
- **Long-read feature:** SV breakpoints (LTA chromothripsis), copy number.
- **Role:** validation_only. Trees come from short-read SNVs/SVs; the tree tool is not named in the fetched part.
- **Evidence quote:** "using long-read nanopore WGS of selected cases" (validation of LTA chromothripsis); "constructed tumour phylogenies using multi-region WGS data from 46 tumours".
- **Relevance:** Low; long reads only confirm SVs.

### C2. Resolving clonal evolution and selection of extrachromosomal DNA at single-cell resolution (ecSingle)

- **Authors:** Josephine Deleuran Hendriksen (first) ... Joachim Weischenfeldt (last).
- **Year / venue:** 2026, Genome Biology 27:10. DOI 10.1186/s13059-026-03933-2.
- **URL fetched:** https://research.regionh.dk/da/publications/resolving-clonal-evolution-and-selection-of-extrachromosomal-dna-/
- **Role:** validation_only for long reads. ecDNA is called from short-read scRNA-seq. The abstract shows "the superiority of single-molecule long-read sequencing for resolving ecDNA". The fetched page does not mention a phylogenetic tree (**tree step UNVERIFIED / likely absent**).

---

## D. No tree step (excluded by the rule)

| Paper | Why excluded | Fetched URL |
|---|---|---|
| SMOOTH-seq, Fan X ... Tang F, Genome Biology 2021 (10.1186/s13059-021-02406-y) | Single-cell long-read (PacBio/ONT) WGS; calls CNV/SV/ecDNA/SNV; no tree tool. | https://pmc.ncbi.nlm.nih.gov/articles/PMC8247186 |
| Hård J ... Ameur A, "Long-read whole-genome analysis of human single cells", Nat Commun 2023 (dMDA + HiFi) | Normal CD8+ T-cell clones A/B; no tree. | https://www.biorxiv.org/content/10.1101/2021.04.13.439527v2.full |
| scNanoGPS, Nat Commun 2023 (Gao lab) | Single-cell ONT RNA; genotype + CopyKAT; no tree. Tumor evolution only named as future use. | https://pmc.ncbi.nlm.nih.gov/articles/PMC10336110/ |
| LongSom, Dondi A ... Beerenwinkel N, Genome Research 2025; code https://github.com/cbg-ethz/LongSom | PacBio long-read scRNA; SNV/mtSNV/fusion/CNA; clones via BnpC clustering and inferCNV; no tree. | https://pmc.ncbi.nlm.nih.gov/articles/PMC12047253/ |
| nanoranger, Penter L ... Wu CJ, Nat Commun 2024; code https://github.com/mehdiborji/nanoranger | ONT single-cell cDNA; SNV/mtDNA/fusion genotyping; clonal tracking only, no tree. | https://pmc.ncbi.nlm.nih.gov/articles/PMC10762175/ |

## E. Already known (not re-analysed)

- Liu Y ... Kolmogorov M / Sahinalp SC, "Long-read sequencing of single cell-derived melanoma sublines ...", Nat Commun 2026 (s41467-026-75172-9); bioRxiv 10.1101/2025.08.28.672865. ScisTree tree; TreeHarmonizer places SV/CNA/methylation. A related NCM 2023 talk (https://nanoporetech.com/resource-centre/ncm-2023-houston-analysis-melanoma-evolution-using-nanopore-long-read-sequencing) reports a phylogeny from phased CpG methylation of 24 sublines; tool not named on the page. -> **already_known**.
- Sakamoto 2022 lung cancer long-read phasing -> already_known.
- SIGNALS / DLP+ 2022 (ONT validation) -> already_known.

## F. Seen in search results only (UNVERIFIED, not fetched successfully)

- PoreMeth2 (Genome Research 35:2501, 2025): nanopore epiallele DMR tool, "decoding the evolution of methylome alterations". Page fetch was blocked. I have no evidence of a tree step. **UNVERIFIED**.
- Decoil (Genome Research 2024): ONT ecDNA structure reconstruction in neuroblastoma; search snippet says structure/heterogeneity, not lineage. **UNVERIFIED, likely no tree**.
- ULI-HiFi (Wang et al., Genome Research 36:1305, 2026; medRxiv 10.1101/2025.07.25.25332067): low-input HiFi on FAP normal/polyp/adenocarcinoma. Fetch returned 403. Tree step **UNVERIFIED**.
- Sgootr (UMD thesis): single-cell methylation tree, but bisulfite short-read, not long-read -> out of scope.

---

## Summary table

| ID | Paper | Year | Platform | SC/bulk | Long-read feature | Role | Tree method | Status |
|---|---|---|---|---|---|---|---|---|
| A1 | Hackett ... Blundell, PCDH methylation barcodes | 2026 | ONT | bulk (read = cell) | HP-phased 5mC epialleles (WhatsHap, LongPhase) | tree_input | kNN impute + UPGMA (Hamming) | **include (new)** |
| B1 | Wong ... Wei, ecDNA atlas (ecLego3) | 2025 | ONT | bulk | ecDNA SV junctions | tree_input (manual) | manual parsimony | borderline / exclude |
| C1 | Espejo Valle-Inclan ... Cortés-Ciriano, osteosarcoma | 2025 | Illumina + ONT | bulk multi-region | SV breakpoints | validation_only | not named | exclude |
| C2 | Hendriksen ... Weischenfeldt, ecSingle | 2026 | scRNA + LR | sc + bulk | ecDNA structure | validation_only | none seen | exclude |
| D | SMOOTH-seq; Hård 2023; scNanoGPS; LongSom; nanoranger | 2021-2025 | PacBio/ONT | single-cell | SV/ecDNA/SNV/isoform | none | no tree | exclude |
| E | Mouse melanoma sublines (ScisTree, TreeHarmonizer) | 2026 | ONT | sc-derived sublines | SV, phased 5mC | tree_input / placement | ScisTree | already_known |

## Failed or empty searches

- "single-cell nanopore tumor phylogeny" / "scNanoSeq copy number phylogeny": no scNanoSeq paper found; no single-cell ONT DNA CNV tree method found.
- "long-read single-cell DNA lineage tree", "haplotype-resolved single-cell long read cancer": only SMOOTH-seq, Hård 2023 (no trees) and the known melanoma paper.
- "PTA + nanopore single-cell SV phylogeny": nothing found.
- "long-read scRNA isoform SNV phylogeny": only LongSom / nanoranger / scNanoGPS (no trees).
- "epimutation lineage tree long read" (beyond A1): only the melanoma NCM talk (known) and short-read methods (Gaiti 2019, EPI-Clone, MethylTree, Sgootr).
- "structural variant phylogeny long-read tumor": only short-read SV phylogeny tools (Meltos 2019/2020, Eaton 2018) and the known melanoma work.
- "ecDNA evolution long read phylogeny": only B1 (manual) and ecSingle/CoRAL/Decoil (no tree).
- "somatic mosaicism lineage tree long-read HiFi": nothing with a long-read tree. HiDEF-seq not searched in depth (single-molecule duplex; no tree expected).
- "clonal hematopoiesis long-read phylogeny": only A1.
