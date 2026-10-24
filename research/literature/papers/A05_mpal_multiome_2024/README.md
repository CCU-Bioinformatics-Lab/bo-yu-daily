---
paper_id: A05
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_patient_sc_reference"
sc_truth_strength: "reference_tree"
title: "Multiomic single cell sequencing identifies stemlike nature of mixed phenotype acute leukemia"
year: 2024
doc_type: "application"
material: "human_patient"
platform_class: "short_or_unspecified"
platform_detail: ["DAb-seq (Tapestri) amplicon", "Illumina NovaSeq"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "patient_scdna_reference_tree"
single_cell_tech: ["DAb-seq scDNA+protein", "CITE-seq"]
input_is_single_cell: true
tree_type: ["mutation_tree", "clone_tree"]
cross_tags: ["amplicon_panel", "phenotype"]
keywords_en: ["mpal", "mixed phenotype acute leukemia", "dab-seq", "tapestri", "scdna", "scite", "mutation tree", "cite-seq", "surface protein", "flt3 itd", "leukemia gene panel"]
keywords_zh: ["混合表型急性白血病", "單細胞DNA", "突變樹", "表面蛋白", "克隆表型", "基因面板"]
summary_zh: "DAb-seq 單細胞 DNA 以 SCITE 建 MPAL 突變樹。"
category_index: "../../PAPER_CATEGORIES.md"
---

# A05 — MPAL 的 single-cell DNA mutation tree 與 phenotype

Peretz, C. A. C., Kennedy, V. E. et al. **Multiomic single cell sequencing identifies stemlike nature of mixed phenotype acute leukemia.** *Nature Communications* **15**, 8191 (2024). DOI: [10.1038/s41467-024-52317-2](https://doi.org/10.1038/s41467-024-52317-2)。2024-09-18 online；保存正式期刊版。

[官方正文](https://www.nature.com/articles/s41467-024-52317-2) · [官方 PDF](https://www.nature.com/articles/s41467-024-52317-2.pdf) · [本機 PDF](paper.pdf) · [完整文字](paper.txt)

## 收錄與閱讀定位

第一類 A：14 名 newly diagnosed adult MPAL 病人接受 **DAb-seq（single-cell DNA＋protein）**，共有 58,807 genotyped cells；另有 12 名病人的 CITE-seq RNA＋protein。DNA 與 RNA 是平行 assay，不能把全部 transcriptomes 和 genotypes 說成同一顆細胞的共同測量。DNA panel 涵蓋 20 個常見 leukemia genes，識別 27 個 pathogenic/likely pathogenic mutations 與 36 個 genetically distinct clones。沒有 long reads/linked reads，亦不是 RNA-only 推樹。

PDF 實體頁與本文頁碼相同：p.1 cohort/摘要；p.8 DNA results 與 SCITE tree 的說明；p.9 Fig.4 genotype landscape；p.11 Fig.5 mutation-tree 圖，p.12 圖說；p.13 DAb-seq 實驗；p.14 Methods「Single-cell DAb-seq data processing and analysis」「Clonal analysis and inference of mutational phylogenies」及 Data/Code availability。全文另指 Supplementary Fig.13 為全 cohort phylogeny；此補充檔本次未下載，因此此筆記以主文 Fig.5 與 Methods 為直接閱讀證據。

## 變異、clone 與樹的定義

Tapestri/DAb-seq 的 short-read DNA amplicons 經 hg19 alignment，GATK calling，另用 ITDseek 找 FLT3 ITD。有效 barcode 要求至少 60% DNA intervals 有 ≥8 reads；低品質 variant/cell 以 quality<30、depth<10、alternate AF<20% 等門檻排除。個別病人的 clonal analyses 使用在 >0.1% 細胞中出現、已知或可能 pathogenic 的 nonintronic somatic variants。

**同 genotype 超過 10 顆細胞**定為一 clone；每個病人用 **SCITE** 推 mutation phylogeny，global false-positive rate 設 1%，false-negative rate 使用平台值。SCITE 的基本 mutation-tree 模型及 error model 強烈影響結果；本研究沒有另加 long-read phase/copy-number multiplicity likelihood，也沒有追蹤實驗標記過的祖先細胞。故樹是人類病人 scDNA 支撐的參考，不是絕對 lineage ground truth。

Fig.5 特別展示 **9 名有至少兩次逐步 mutation acquisitions 的病人**，再比較後代 clone 的 surface proteins。圖上可見 cellular clone proportions 的 posterior credible intervals；這些不是來自 read VAF 的 bulk CCF confidence interval。14 名 DNA cohort、9 名可作 stepwise phenotype 分析及 12 名 RNA cohort 是不同 denominator。

## 與關鍵字及限制的關係

single-cell DNA、mutation coexistence/exclusivity 與 genotype-defined clones 是直接證據。VAF 在此主要用於單細胞 genotype/QC，不能與 tumor cellular purity 或全樣本 CCF 畫等號。文章區分 heterozygous/homozygous mutations，但沒有整合全基因組 allele-specific CN、LOH、phase set 或 haplotype；因此 homozygous call 可能還受 allelic dropout、CN change 與 panel 覆蓋影響，不等於已證明 LOH。

主要生物結果是 phenotype、RNA state 與 genotype 的對應很不單純；隨 mutation acquisitions 可見 immaturity markers 改變，但不同病人有不同模式。對本 repo 的啟示是 methylation/表型相似不能單獨證明 lineage 相同。panel 只看少數 driver genes，未觀測的 passenger mutations 會合併本來不同的 lineages；rare clone 門檻會使小族群消失，固定 error rates 也未必描述每 locus 的 dropout。

## 可取得資料

本研究原始 sequencing FASTQ 及資料：GEO **GSE232074**；比較用既有 scRNA cohort 為 **GSE139369**。兩者不要混成 primary scDNA 證據。[GEO primary study](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE232074) · [分析 scripts](https://github.com/SmithLabUCSF/MPAL)。正文另附 Source Data，宜先確認每檔 assay/sample 身分再計算。此研究較適合用公開小型 genotype matrices 起步；本次未下載病人 raw FASTQ。

## 對本 repo 的最小可執行改進（尚未實作）

C0 把 read-level evidence 和 single-cell genotype 的來源分欄，保留 missingness，不將 no-call 當 reference。C1 schema 記錄 clone cutoff、FP/FN model、pathogenic-only ascertainment；C2/C3 的 CN/haplotype likelihood 應另找具有 CN 的資料驗證，不能在此無 CN panel 直接宣稱優於 baseline。C4 可把 same-cell observed co-occurrence 作外部 relation check，但沒有實測 same-molecule pairs，不能直接填 `n11`。C5 可比較 driver-only clustering 與加入 CN/haplotype 的設計；C6 posterior report 應包含 error-rate、rare-clone threshold 的敏感性。

最小 benchmark：挑 Fig.5 一個 branched、一個 linear case，從細胞 genotype 聚合 pseudobulk；設不同 missingness、dropout 與 clone frequency，比較 VAF-only 與 genotype-informed reference 的 ancestral-pair agreement。以 FP 0.1%/1%/2%、clone cutoff 5/10/20 cells 作敏感性分析。將 protein/RNA 留作 held-out phenotype，不拿 phenotype clustering 定 lineage truth；結果只能支持 genotype/C0-C1/C5-C6 設計，不足以證明 C2-C4 的 long-read 增益。
