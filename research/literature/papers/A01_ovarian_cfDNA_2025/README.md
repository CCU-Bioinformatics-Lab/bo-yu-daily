---
paper_id: A01
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_patient_sc_reference"
sc_truth_strength: "reference_tree"
title: "Tracking clonal evolution during treatment in ovarian cancer using cell-free DNA"
year: 2025
doc_type: "application"
material: "human_patient"
platform_class: "short_or_unspecified"
platform_detail: ["DLP+ scWGS (Illumina)"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "patient_scdna_reference_tree"
single_cell_tech: ["DLP+ scWGS"]
input_is_single_cell: true
tree_type: ["cell_tree", "clone_tree", "cn_event_tree"]
cross_tags: ["haplotype_specific_cn", "structural_variant", "longitudinal", "cfdna"]
keywords_en: ["hgsoc", "ovarian cancer", "cfdna", "scwgs", "dlp+", "medicc2", "signals", "allele-specific copy number", "structural variants", "ccf calibration", "longitudinal", "wgd"]
keywords_zh: ["卵巢癌", "游離DNA", "單細胞DNA", "等位基因特異拷貝數", "縱向追蹤", "結構變異"]
summary_zh: "病人 scWGS 建 MEDICC2 樹；cfDNA 追蹤抗藥 clone。"
category_index: "../../PAPER_CATEGORIES.md"
---

# A01 — 病人 single-cell DNA 參考樹與 cfDNA 演化追蹤

Williams, M. J. et al. **Tracking clonal evolution during treatment in ovarian cancer using cell-free DNA.** *Nature* **647**, 757–765 (2025). DOI: [10.1038/s41586-025-09580-0](https://doi.org/10.1038/s41586-025-09580-0)。2025-10-01 online；本目錄保存正式期刊版，非 preprint。

[官方正文](https://www.nature.com/articles/s41586-025-09580-0) · [官方 PDF](https://www.nature.com/articles/s41586-025-09580-0.pdf) · [本機 PDF](paper.pdf) · [完整文字](paper.txt)

## 為何納入與證據定位

屬第一類 A：直接取自高級別漿液性卵巢癌（HGSOC）病人的 single-cell whole-genome DNA 資料，建立 genetic phylogeny，再追蹤治療中的克隆比例。24 名病人提供 21,916 顆 tumor cells（每人 232–2,094 顆）；摘要的 **18 名**是主要多年縱向追蹤分析人數，不能和整體 scWGS cohort 混寫。不是 RNA-only 推樹，也不是 cell line。這篇未使用 ONT/PacBio 長讀或 linked reads 建樹，因此不列入第二類 B 的 long-read 方法數目。

頁碼以下皆為下載檔的 **PDF 實體頁，從 1 開始**；正文首篇印刷頁為 757，Methods 後續頁未延續印刷頁碼。實際閱讀定位：p.1 cohort/摘要、p.2「Clone-specific mutations and SVs in scWGS」、p.3 Fig.1、p.10「DLP scWGS processing」「Phylogenetic inference and clone assignments」「Clone-level 10-kb resolution copy-number calling」、p.12「Estimating clone frequencies」與式 (3)(4)、p.13 Data/Code availability。Extended Data Fig.6 給出其他病人的 single-cell CN heatmaps 與 phylogenies。

## 樹如何得到；「答案」有多強

DLP+ 是淺層 short-read scWGS，平均每細胞約 0.088×。先以 HMMcopy 在 500-kb bins 推 integer copy number，剔除低品質、replicating、multiplet 及疑似 multipolar-division cells，再用 SIGNALS v0.7.6 推 haplotype-specific copy number。MEDICC2 以該 allele-specific CN 為輸入建立單細胞樹；研究者再**人工挑選帶有特定 genomic features 的 clades**，把其 descendants 定為 clones。這不是完全自動、獨立盲判的 clone 定義。

合併同 clone 的 reads 後，HMMclone 將 CN 解析度提升至 10 kb；SV 與 CN 的位置關係協助分辨 truncal、clone-specific 及複雜重排。SVtyper 經修改以保留 single-read 支持的低覆蓋細胞訊息，並要求 split read 對到 breakpoint 兩側，避免寬鬆計數。Fig.1 的 OV-004 展示 CN/SV 與樹的共同解讀。

因此可把它當作**病人資料支撐的參考樹**，但不是實驗直接觀測到全部祖先關係的絕對真值。其 topology 仍依 CN 事件模型、取樣、細胞 QC 與人工 clade 選擇；未取樣祖先、克隆消失及後續新生 clone 都不可能由診斷時細胞完整復原。

## purity、VAF、CCF、haplotype 與 CN/LOH

最值得移植的是 VAF 與 CCF 分開處理：研究者先找某 SV 支持細胞的 MRCA，計算 `CCF_tree = n_MRCA_descendants / n_total_cells`，再用 `C = CCF_tree / VAF_pseudobulk` 校正 cfDNA 的 VAF。此校正吸收 variant copy number 的影響，**不能等同通用的 VAF×2 或 purity 校正公式**。將診斷時校正因子用到後續時間點，也依賴標記的拷貝背景與分支歸屬沒有根本改變。

copy number、WGD、haplotype-specific CN 都直接參與；LOH 可在 allele-specific CN 背景中描述，但不是本文獨立的 LOH caller 評測。本文的 haplotype 是 SIGNALS 對 homolog 的區分，並未提供可直接搬入本 repo 的 LongPhase `HP`/`PS` schema。cfDNA tumor fraction、病理/細胞比例與 cellular CCF 是不同量。

主要結果是治療抗性多來自診斷時已存在的小部分 clones 擴張，並可見 WGD、chromothripsis 與 oncogene amplification。SV 因背景錯誤率較低適合作追蹤標記；但 marker 發現和 CCF 校正都依同一 single-cell 參考樹，不能用校正後數值再宣稱獨立驗證該樹。

## 可取得資料與重現入口

Raw reads：dbGaP **phs002857.v3.p1**（受控病人資料）；processed：Synapse **syn66399325**。正文和補充表提供 coverage、cfDNA tumor fractions、clone frequencies、genomic features 與 error rates；資料登錄不等於無條件開放下載。[dbGaP](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs002857.v3.p1) · [Synapse](https://www.synapse.org/Synapse:syn66399325) · [DLP+ pipeline](https://github.com/mondrian-scwgs) · [HMMclone](https://github.com/shahcompbio/HMMclone)。本次只下載論文，不取得受控 raw data。

## 對本 repo 的具體改進（研究提案，尚未實作）

對照 `plan.md` 的 C0–C6：C0 應保留 sample/cell provenance、CN segment、WGD 及 allele-specific CN 的來源；C1 schema 分清 `cellular_purity`、`tumor_DNA_fraction`、`CCF` 和 derived calibration，不能沿用一個 purity 欄位包辦。C2/C3 的 haplotype multiplicity 與 split likelihood，可用 single-cell pseudobulk 的細胞分數檢驗；C4 的 read-pair factor 無本文長讀共現證據可直接測，應先留在合成實驗。C5 評估 clade 切法敏感性；C6 同時報樹的 edge support、CCF uncertainty 與 CN/SV conflicts。

最小 benchmark：選 2–3 個病人，保留 scDNA 參考樹及 cell assignments，將 tumor cells 按已知比例 pseudobulk，加入正常細胞時另記 cellular fraction 與 ploidy 加權 DNA fraction。比較 bulk VAF baseline、CN-aware C2、C2+C3；以細胞 carrier fraction 的誤差、mutation ancestral-pair precision/recall 與 clone recovery 評估。將建樹 CN features 與 held-out SNV/SV 分開，避免用同一標記建答案又評估。無 matched long reads 時，此資料驗的是 CN/CCF 模組，不能聲稱驗證 long-read topology 的增益。
