---
paper_id: B07
category: "C1"
category_label: "短讀或未說平台（無 single-cell 真值）"
subtype: "c1_single_cell_input_no_truth"
sc_truth_strength: "none"
title: "Haplotype-aware analysis of somatic copy number variations from single-cell transcriptomes (Numbat)"
year: 2022
doc_type: "method"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["10x scRNA-seq (short read)", "Eagle2 population phasing reference"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "scrna_only"
single_cell_tech: ["10x scRNA-seq", "NCI-N87 paired scDNA (CN check only)"]
input_is_single_cell: true
tree_type: ["cell_tree", "cn_event_tree"]
cross_tags: ["single_cell_input", "haplotype_specific_cn", "population_phasing"]
keywords_en: ["numbat", "scrna-seq", "haplotype-aware hmm", "allele-specific copy number", "cnloh", "eagle2 population phasing", "perfect phylogeny", "scistree", "multiple myeloma", "anaplastic thyroid cancer", "single-cell cnv", "clonal architecture"]
keywords_zh: ["單細胞轉錄體", "單倍型感知", "拷貝數變異", "族群相位", "中性拷貝數LOH", "細胞演化樹"]
summary_zh: "scRNA 加族群 phasing 推 CNV 細胞樹；不是 long read。"
category_index: "../../../PAPER_CATEGORIES.md"
---

# B07 — Numbat：把 haplotype／allele-specific CN 與 LOH 用於 single-cell 樹

## 書目與實際閱讀版本

正式論文：Gao T, Soldatov R, Sarkar H et al. **Haplotype-aware analysis of somatic copy number variations from single-cell transcriptomes**. *Nature Biotechnology* 41, 417–426 (2023)，2022-09-26 online。DOI：[10.1038/s41587-022-01468-y](https://doi.org/10.1038/s41587-022-01468-y)。本目錄以 online 年命名，不把2023期刊年當另一篇研究。[出版社書目](https://www.nature.com/articles/s41587-022-01468-y)

已下載並閱讀40頁 [paper.pdf](paper.pdf) 及 [paper.txt](paper.txt)，但此 PDF 是作者公開的 **2022-02-10 bioRxiv v1 preprint**，題名 **Haplotype-enhanced inference of somatic copy number profiles from single-cell transcriptomes**，DOI [10.1101/2022.02.07.479314](https://doi.org/10.1101/2022.02.07.479314)，來源為 [bioRxiv PDF](https://www.biorxiv.org/content/10.1101/2022.02.07.479314v1.full.pdf)。正式出版社PDF回傳付費存取HTML，PMC PDF回傳challenge頁，因此沒有冒稱取得正式PDF。

另已下載並閱讀正式版本的 [NIH PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10289836/)，本地保留 [final_pmc.html](final_pmc.html)。以下 **p. 是本地 preprint PDF 實體頁；正式版則以段落ID、圖或Methods小節定位**。兩個版本屬同一研究，只計一篇。版本差異有實質影響：preprint為21 samples，正式版增加gastric cell line而成22 samples、59,878 cells；部分accession對應也有更正，本文以正式版為準。

本地PDF已以`pdfinfo`驗證40頁，並實際渲染核對p.24 Fig.3。SHA-256：`b2edf784a9d2f5c435e072e32afa8ed7188cb95ac810d7bb58df9f4cbde4a9e3`。

## 收錄理由與真值界線

分類 **B3：非實測 long-read，但確實以 haplotype/CNV/LOH 特徵推理 topology**。其相位來自 Eagle2 + TOPMed/1000 Genomes population phasing，不是 ONT/PacBio，也不是同一DNA long read上的somatic SNV共現。Numbat既估計CN，也重新搜尋單細胞樹，不能只歸成上游CN caller；但不能算作第五篇「實測long-read入樹」。正式Discussion明確把experimental haplotype resolution列為可改善未來準確性的方向，並沒有聲稱本文完成long-read實驗。[正式P19、P28、P50；preprint pp.6、9、14]

真實病人single-cell RNA資料確實存在；其CN tree仍是模型推論。matched bulk WGS確認CN、mtRNA variants支持部分clone、細胞株paired scDNA/scRNA提供獨立技術比較，均不等於已知道病人每個祖先的完整真樹。與第二類「single-cell但不具病人真值」高度相關；同時可供第一類比較，但應標明reference tree。

## 方法：相位不只是註記，而會改變CN證據與樹

Numbat從 scRNA-seq 的expression count與germline SNP allele count出發。population haplotype讓原本分散的弱BAF訊號有共同方向，可跨SNP累積證據。其haplotype-aware HMM同時使用expression shift、allelic imbalance與phase-switch probability。expression模型採Poisson-lognormal，allele count採Beta-binomial以容納transcription／allele-specific expression過度離散。population phase隨genetic distance不確定性增加，因此用paired mirrored states與transition處理phase switch，並非把整條染色體HP當絕對已知。[preprint pp.3–5、10–12；正式Methods「Statistical modeling of expression and allele data」「Phase switch probabilities」]

推論採交替最佳化：沿目前樹的subtrees建立lineage pseudobulks→HMM找CNV與consensus segments→以Bayesian模型估計每個細胞每個CNV的genotype probability→ScisTree式maximum-likelihood perfect phylogeny搜尋topology與mutation placement→再更新pseudobulks。正式版Methods用NJ與UPGMA兩棵候選初始樹，比較genotype likelihood後以nearest-neighbor interchange搜尋；不能將preprint所述單一初始化細節無條件當正式實作。[preprint p.6、p.14，Fig.3在p.24；正式P19、P50]

這個框架與PhyClone有明顯差別：它是single-cell CNV presence／absence的不確定genotype建樹；PhyClone的基本觀測是bulk SNV ref/alt、purity、CN所對應的CCF likelihood grid。Numbat的haplotype fraction不是somatic VAF或CCF，allele-CN也沒有自動解除multiplicity ambiguity；不可直接把其CNLoH機率當成PhyClone的SNV-CCF。

## 實驗與可以重用的證據

| 實驗 | 發現與適當解讀 | 閱讀定位 |
|---|---|---|
| 5個MM matched flow-sorted WGS | CN events可由DNA比對；CN-neutral LOH只有allele訊號，expression-only方法會漏 | preprint p.5，Fig.2 p.23；正式Fig.2 |
| 稀釋／pseudobulk混合 | 在不同tumor cell fraction測allelic imbalance與CN detection；驗證的是CN辨識與迭代效益，並非已知真樹的整棵topology準確率 | preprint pp.4–5；正式Extended Data Fig.8、P21 |
| TNBC1與ATC1 | TNBC1有兩lineages、branch-specific CNLoH，以及chr15 mirrored haplotype amplification；ATC1有chr7/17不同allele-CN狀態 | preprint p.7，Fig.4 p.25；正式Fig.4、P22–P23 |
| MM患者27522四時間點 | primary→remission→兩次relapse，推得g1/g2/g3 CN clones與治療後擴張，subclonal deletions有相應DNA支持 | preprint pp.7–9，Fig.5 p.26；正式P24、Fig.5 |
| NCI-N87 gastric cell line | paired scRNA/scDNA支持其CN landscape與subclonal architecture；是細胞株，不是真實病人的single-cell truth | **正式版新增**P21、Extended Data Fig.9；本地preprint未包含 |

另須避免重複計算證據：27522與MM資料來源和本研究集B02的2021 linked-read myeloma研究相關，Numbat重分析並非一個獨立招募的第二批病人。這兩篇回答不同問題，但不能把相同cohort當獨立臨床重現。

主要限制為single-cell RNA的coverage、allele-specific expression與baseline ploidy不確定性；rare subclones可能在pseudobulk時被稀釋；可信clone數仍需檢視。whole-genome duplication或幾乎全基因組異常時，diploid baseline仍可能要人工校正。其perfect phylogeny假設與MEDICC2容許反覆CN變化的模型不同，不適合無限制地外推到所有parallel／recurrent CNA。[preprint pp.9–10；正式P29–P30、P50]

## 資料與程式

正式版 `Data availability`（本地HTML段落P63）提供：MM/WASHU **PRJNA694128**；MDA CopyKAT **GSE148673 / PRJNA625321**；NCI-N87 **GSE142750 / PRJNA498809**；normal reference **syn21041850**。preprint p.17的MM／MDA accession配對不一致，這裡採正式版更正。程式：[kharchenkolab/numbat](https://github.com/kharchenkolab/numbat)；原論文重現：[NumbatAnalysis](https://github.com/kharchenkolab/NumbatAnalysis)。本輪只下載論文檔，不代表上述raw data已下載或完成重跑。

## 對本 repo 的可行改進與ablation

以下為 **inferred 建議**，對應 `plan.md:194–200` 的C0–C6，而非已實作結果。

1. **C0/C1：相位可信度與觀測來源分開。** 每個PS保留phased/unphased counts、tagging／switch uncertainty及phase provenance。Numbat證明phase error應進模型；本repo的HP只能在同PS比較，跨PS需要額外實測橋接，不能照抄population phasing當真值。
2. **C2/C3：測試soft phase posterior。** 用 `π_i(h)` 混合候選haplotype，而非單一硬判斷；評估phased與unphased抽樣偏差及overdispersion。Numbat的RNA allele模型不可直接複製到DNA，但其保留uncertainty原則可移植。
3. **C4：先守住CN邊界。** mirrored amplification或CNLoH顯示「同major/minor」不代表相同歷史。對amplified／subclonal CN，不可把read pair互斥直接解為branch；維持第一版同PS、同HP、`C_h=1`限制，另將反覆CN事件列成擴充研究。
4. **C5/C6：分群與樹相互檢查。** 目前PyClone-VI預分群若已混合不同multiplicity／haplotype，後續PhyClone無法修回；可借鑑Numbat的迭代概念，先以HP/link conflicts找可疑cluster，再比較重新分群前後的tree，而不是把RNA expression clusters視為genetic clones。

建議同資料做 total-CN／major-minor、haplotype-CN硬相位、soft相位三層ablation；注入PS切換、低purity、CNLoH、MSAI、CN±1錯誤並記錄clone/ancestor relation、multiplicity與CCF calibration。對single-cell reference tree只比較可靠splits與支持區間，另外報CN calling及phase準確度。這篇最能啟發的改進是 **讓phasing與CN的不確定性一路保留到樹，而非把haplotype當無誤差標籤**。
