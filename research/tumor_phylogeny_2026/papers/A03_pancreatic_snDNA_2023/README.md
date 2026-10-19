---
paper_id: A03
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_patient_sc_reference"
sc_truth_strength: "reference_tree"
title: "Application of high-throughput single-nucleus DNA sequencing in pancreatic cancer"
year: 2023
doc_type: "application"
material: "human_patient"
platform_class: "short_or_unspecified"
platform_detail: ["Tapestri snDNA amplicon panel (Illumina)"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "patient_scdna_reference_tree"
single_cell_tech: ["Tapestri snDNA"]
input_is_single_cell: true
tree_type: ["clone_tree", "mutation_tree"]
cross_tags: ["amplicon_panel", "metastasis"]
keywords_en: ["pdac", "pancreatic cancer", "sndna-seq", "tapestri", "amplicon panel", "scg", "smad4 deletion", "kras", "allelic dropout", "doublet", "mutual exclusivity", "clone phylogeny"]
keywords_zh: ["胰臟癌", "單核DNA定序", "擴增子面板", "互斥變異", "等位基因脫落", "克隆樹"]
summary_zh: "Tapestri snDNA 建 PA04 的 SNV+SMAD4 刪除 clone 樹。"
category_index: "../../../PAPER_CATEGORIES.md"
---

# A03 — 胰臟癌病人 single-nucleus SNV＋CNV 演化樹

Zhang, H. et al. **Application of high-throughput single-nucleus DNA sequencing in pancreatic cancer.** *Nature Communications* **14**, 749 (2023). DOI: [10.1038/s41467-023-36344-z](https://doi.org/10.1038/s41467-023-36344-z)。本目錄保存官方正式期刊版。

[官方正文](https://www.nature.com/articles/s41467-023-36344-z) · [官方 PDF](https://www.nature.com/articles/s41467-023-36344-z.pdf) · [本機 PDF](paper.pdf) · [完整文字](paper.txt)

## 收錄理由與實際讀到的位置

第一類 A：16 名真正 PDAC 病人的 frozen tumor samples，包含原發多區域切除與轉移 autopsy 組織。34 個生物樣本產生 38 個 snDNA libraries，平均每樣本 2,867 nuclei；使用 Tapestri 186 amplicons/93 genes 的 **DNA panel**，不是 scRNA 推 CNV。matched bulk WES/WGS 用來驗證重要 variants。主要完整 clone tree 是 **PA04 一名病人**的 3 個區域樣本，不能聲稱 16 名病人都建立了全基因組高解析演化樹。沒有 long-read 或 linked-read 推樹。

PDF 實體頁與本文頁碼相同，從 1 起算：p.1–3 cohort、技術驗證；p.6–7/ Fig.3–4 描述互斥 variants；p.7「Seven clusters」；p.9 Fig.6 圖、p.10 圖說與限制；p.10 Methods 的 patient sampling/purity；p.11–12 genotype、ADO、per-amplicon ploidy；p.12 Data/Code availability。SCG 參數細節移到 Supplementary Methods；本次沒有把未下載的補充參數當成已精讀證據。

## 從哪些證據建立樹

PA04 合併 8,061 nuclei，以 **25 個 bulk-validated germline/somatic SNV genotypes**，加上 **8 個 SMAD4 amplicons 的 homozygous-deletion 狀態**，使用 single-cell genotyper（SCG）的 multilayer/multistate clustering 分成 7 群。Fig.6b 再將 cluster-defining SNV/CNV events 排成 clone phylogeny，呈現 driver SNV、廣泛 CN 及逐步 focal deletion 的關係。8 個 amplicons 代表該 panel 覆蓋區域，不能推成完整無缺口的整個 gene/genome 刪除真值。

此資料能直接檢查變異在**同一細胞**是否共存，較 bulk VAF 有更強的 clonal architecture 證據。例如同病人不同 KRAS variants 可屬互斥細胞群；SMAD4 不同中間 deletion patterns 支持逐步演化與 pathway 的 convergent inactivation。但 single-cell 同存仍沒有觀測到祖先細胞的出生順序；Fig.6 的事件排序是由已取樣 genotype/CN pattern 推論，不是 lineage recorder 產生的已知拓樸。

## 技術限制與關鍵字

VAF 同時用於 bulk 對照、single-cell QC 與 genotype；CN/ploidy 由 per-amplicon depth 正規化，再以 putative normal cell 群當 diploid baseline，並有 microarray 驗證。normal 群常以 KRAS-WT 或已知 variants 全 WT 定義，可能受 dropout/腫瘤異質性影響。paper 特別承認病理的 tumor-occupied **2D area fraction**，與 snDNA 的 tumor-nuclei fraction 不同；這兩者又都不是 DNA fraction。

PCR allelic dropout 可把 HET 看成 HOM/WT；doublets 可製造假共存。作者混合不同病人的樣本估計整流程 doublet rate 約 3–5%，並用 matched-normal SNPs 估 ADO。結果建議 mean depth 至少約 100 才適合其分析，不能把此數字泛化成所有 scDNA 技術門檻。LOH 不能只由 homozygous variant call 或低 coverage 判定。本文未進行 LongPhase-style haplotype phasing，也沒有 phase set/HP 標籤輸出；`HaplotypeCaller` 是 variant caller 名字，不等於完成 read phasing。CCF 不是此研究獨立的完整估計主題。

## 可取得資料

EGA **EGAS00001006024**：Tapestri FASTQ、有效 cell barcode 的 BAM/HDF5，以及部分 matched WES/WGS。受 MSKCC MDP DAA 與 DAC 管制。公開 Supplementary Data 列出 **PA04-SCG_input**、PA04 bulk MAF/allele counts，可先做 matrix 層級重現，不必宣稱 raw BAM 已公開免申請。

[EGA study](https://ega-archive.org/studies/EGAS00001006024) · [custom Mosaic](https://github.com/haochenz96/mosaic) · [Mosaic archived code](https://doi.org/10.5281/zenodo.7236672) · [SCG fork](https://github.com/haochenz96/scg)。本次未下載受控 reads。

## 對本 repo 的具體用處（尚未實作）

C0 要保留 per-locus missingness、depth、CN evidence，不能以 no-call 當 reference；C1 schema 明分 tumor-cell fraction 與 DNA fraction。C2 multiplicity prior 需要允許 CN loss 導致 mutation loss，否則祖先與後代關係會被錯排；C3 比較 phased/unphased likelihood 時，要把 dropout/錯配造成的零值與真 CN=0 分開。C4 中 same-read 共現是 same-copy 證據，強於此文的 same-cell 共存；但本篇互斥細胞群可作 topology constraint 的外部檢查。C5 以 SNV-only vs SNV+CNV clustering 展示是否真的增加可辨識 clone；C6 報 germline/不確定 somatic 標籤及 deletion-mediated conflicts。

最小 benchmark：使用公開 PA04-SCG_input 的 25 SNV＋8 CN features，先重現 7 群與 Fig.6 事件矩陣，再用細胞重採樣建立 pseudobulk counts。比較只用 driver SNV、加入 CN、CN-aware loss 三種；用 clone recovery、mutually-exclusive/ancestral mutation-pair precision 及 dropout sensitivity 評估。答案標記為「PA04 curated reference」，對未定序區域不計準確率；沒有 long reads 時不計 C4 的 empirical gain。
