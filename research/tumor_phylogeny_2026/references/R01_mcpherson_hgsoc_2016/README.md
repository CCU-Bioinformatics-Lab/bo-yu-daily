---
paper_id: R01
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_patient_sc_reference"
sc_truth_strength: "reference_tree"
title: "McPherson 2016: Divergent modes of clonal spread and intraperitoneal mixing in high-grade serous ovarian cancer"
year: 2016
doc_type: "reference_truth_source"
material: "human_patient"
platform_class: "short_or_unspecified"
platform_detail: ["Illumina HiSeq WGS", "targeted amplicon MiSeq", "single-nucleus targeted PCR"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "patient_scdna_reference_tree"
single_cell_tech: ["single-nucleus targeted PCR (Fluidigm Access Array, MiSeq)", "SCG genotyper"]
input_is_single_cell: true
tree_type: ["clone_tree", "sample_tree"]
cross_tags: ["phyclone_truth_source", "mutation_loss", "multi_region", "roth_lab"]
keywords_en: ["high-grade serous ovarian cancer", "single-nucleus sequencing", "targeted deep sequencing", "scg", "pyclone", "stochastic dollo", "infinite sites with loss", "multi-region wgs", "clone tree", "phyclone truth tree", "intraperitoneal spread"]
keywords_zh: ["卵巢癌", "單核定序", "真值樹", "多區域取樣", "突變流失"]
summary_zh: "病人單核 PCR 建樹；是 PhyClone HGSOC 真值樹來源。"
category_index: "../../../PAPER_CATEGORIES.md"
---

# R01 — McPherson 2016 HGSOC：PhyClone 真實資料真值樹的來源

McPherson, A. et al. **Divergent modes of clonal spread and intraperitoneal mixing in high-grade serous ovarian cancer.** *Nature Genetics* **48**, 758–767 (2016). DOI: [10.1038/ng.3573](https://doi.org/10.1038/ng.3573)。PMID 27182968。

[官方正文](https://www.nature.com/articles/ng.3573) · [官方 Supplementary Note PDF](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fng.3573/MediaObjects/41588_2016_BFng3573_MOESM152_ESM.pdf) · [官方 Supplementary Tables](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fng.3573/MediaObjects/41588_2016_BFng3573_MOESM153_ESM.xlsx) · [本機 supplement](supplement.pdf) · [supplement 全文文字](supplement.txt) · [本機 tables](supplementary_tables.xlsx)

## 收錄定位

這篇是 **PhyClone 論文 HGSOC 實驗（病人 2、3、9）的真值樹來源**（PhyClone 主文 §2.4.1.5、§3.5、Fig.6；Supp. Fig. S15–S16）。它不屬於本調查 2021–2026 的選文窗口，也不計入 A／B 類篇數，所以放在 `references/`，不寫進 `catalog.json`。

**證據範圍。** 主文是 closed access（Unpaywall `oa_status: closed`；Europe PMC 無全文），本次**沒有讀主文**。以下內容全部來自：

- 官方 Supplementary Note PDF：87 頁，SHA-256 `7915b4e3772878a1ddb568abd574e6b868ac7fd130cab497de7be3e9deec6844`。UBC 作者頁的 [sup-2016Divergent.pdf](https://www.stat.ubc.ca/~bouchard/pub/sup-2016Divergent.pdf) 與它 byte 完全相同。
- 官方 Supplementary Tables S1–S19：xlsx，SHA-256 `166bf71ae2c8f686fa11e97784de1619ef1b6339becc65a647c2a66fc78bdbd6`。
- 本機 PhyClone benchmark 資料 `/big8_disk/boyu114/phyclone_dataset/HGSOC/`（說明見 `tumor_sample.md`）。

supplement 的 PDF 實體頁與頁尾印刷頁碼相同。p.41 Supp. Fig.16 已渲染核對。

## 研究設計

- **病人與樣本**：10 名 HGSOC 病人送定序。病人 5、6 因 tumour cellularity 太低排除，病人 8 因 dbSNP 污染排除，剩 7 名（1、2、3、4、7、9、10），共 68 個樣本（§1.2 p.9；Table S3）。
- **兩類樣本**：
  - discovery：冷凍組織，做 WGS。
  - archival：FFPE，只做 targeted bulk deep sequencing。
- **WGS**：Illumina HiSeq2000，PE100，平均約 30x，對齊 hg19。
  - SNV 用 Strelka 和 MutationSeq 呼叫；high quality 定義為兩者都有呼叫且 mappability = 1.0（§2.1–2.2 p.9–10）。
  - breakpoint 用 deStruct（§2.4）。
  - allele-specific CN 用 DeMix（§2.5 p.10，隨 deStruct 0.1.2 提供）。Supp. Fig.7–13 的圖名寫 ReMixT，與 §2.5 不一致，本筆記以 §2.5 為準。

## 四步建樹流程

### 1. Bulk WGS sample tree（§2.6 p.13；§6 p.20–26）

- **模型**：自建的 **infinite sites with loss** 模型，是 stochastic Dollo 的簡化版。每個 mutation 只出現一次，但可以在多個分支上流失；loss 由全域 loss rate `π_l` 控制。
- **觀測模型**：binomial likelihood，考慮 allele-specific CN、tumour cellularity 和定序錯誤。
- **樹搜尋**：只用 high-confidence SNV，對所有 rooted full binary trees **窮舉**（8 個樣本時有 135,135 棵）。prior 是 uniform，以 MAP 取得 `T_opt`（§6.3.3 p.24）。
- **loss 的檢定**：用 likelihood ratio test（χ²，df=1）檢查 loss 是否顯著改善擬合。Table S3 列出各病人的 `snvs_loss_model_p_value`。
- **CN 佐證**：用 maximum parsimony 重建祖先 allele-specific CN，檢查被判為 lost 的 SNV 是否有 deletion 支持（§6.4 p.25–26）。
- **作者明說的不可識別性**：在 CN-naive 模型下，「祖先 SNV 在直接後代中流失」和「SNV 起源於兄弟節點」產生的證據完全相同（p.13–14）。

### 2. Targeted bulk deep sequencing 與 PyClone（§4.1–4.7 p.15–17）

- **定序**：31 個 tumour 樣本加 7 個 normal 樣本，做 TruSeq/Nextera amplicon 和 MiSeq 定序。每個 allele 是否存在用 binomial exact test 判定，p < 10⁻⁶。
- **分群**：PyClone 0.12.7，跑 4 條 MCMC chain，每條 100,000 iterations、burn-in 50,000；用 mpear 做硬分群。
- **輸出**：每個病人的 SNV cluster 列在 Table S16。這些 cluster 是後面所有 clone genotype 的基本單位。

### 3. Clone phylogeny：兩種策略（§4.8 p.17）

- **病人 1、4、7、10（沒有 single-cell）**：假設每個 discovery sample 只含單一 lineage，直接把 sample tree 當 clone tree。
  - 每個 PyClone cluster 在某個樣本中的 dominance 機率，取其 prevalence > 0.5 的 posterior 機率。
  - 這個機率作為 stochastic Dollo 模型的 presence 機率，再用 ML 重建內部節點的 genotype。
- **病人 2、3、9**：多項證據顯示至少一個樣本混了分歧 lineage，所以改做 single-nucleus sequencing（見第 4 步）。
- 兩種策略最後都會合併 genotype 相同的 clone。

### 4. Single-nucleus targeted sequencing 與 clone tree（§5 p.18–20）

**挑標記（§5.1）**：

| 標記類型 | 怎麼挑 | 用途 |
|---|---|---|
| phylogeny SNV | 從「起源於或流失於後代 lineage」的高信心 PyClone cluster 中**隨機**抽 | 區分 clone |
| ancestral SNV | 取自 prevalence 最高的 cluster | 標示 tumour 細胞 |
| germline 異型合 SNP | 位在全樣本都 LOH 的區段 | 標示 normal 細胞：有雙 allele 表示是 normal |
| breakpoint | 依 DeMix 結果**人工**挑選 | 區分 clone |

**實驗（§5.2–5.5）**：

- 冷凍切片做均質化，取出 nuclei，PI 染色後用 FACS 每孔分一顆單核。
- **不做全基因組擴增**：每顆單核直接做 48-plex PCR，再用 Fluidigm 48×48 Access Array 做 singleplex PCR，加 Nextera barcode 後用 MiSeq 定序。
- 控制組：每塊板都有 gDNA 10 ng／1 ng（positive）、beads 孔與空孔（negative）。

**Genotyping（§5.6 p.19–20）**：

- 每個 allele 用 binomial exact test 判定，p < 10⁻⁶。SNV 位點少於 50 reads 視為 missing；breakpoint 要 ≥5 reads 才算存在。
- 接著用 **SCG（Single Cell Genotyper）v0.3.0** 同時分群並推 genotype：
  - SNV 是 A/AB/B 三態，breakpoint 是有／無兩態。
  - 模型包含 position-specific error rate、sample-specific clone prevalence 和 doublet。
  - 初始 40 個 cluster、1,000 次 random restart，取 lower bound 最好的一次；空 cluster 丟掉。
  - 先驗：SNV error prior 的對角線為 99；breakpoint error prior 為 9:1；doublet Beta prior 為 (99, 1)。

**Clone tree（§5.7 p.20）**：

1. 只保留 ≥10 nuclei 的 SCG clone，並刪掉 80% 細胞都 missing 的 SNV。
2. **不能直接把 SCG 結果丟進 Dollo 模型**。挑出來的 SNV 不是全基因組的無偏樣本，直接建樹會推出 bulk 和 CN 都不支持的假 loss。
3. 所以先把 SNV 併回 PyClone cluster：
   - 每個 SNV 的 presence = P(AB) + P(B)。> 0.9 算存在，< 0.1 算不存在，其餘當 missing。
   - cluster 內只要有任一 SNV 存在，這個 cluster 就算存在於該 clone genotype。
4. **校正取樣偏差**：把 WGS 的所有 SNV 用 PyClone likelihood 指派到這些 cluster，再用各 cluster 的 SNV 數加權 stochastic Dollo likelihood。效果是小 cluster 流失比大 cluster 流失更容易被接受。
5. germline SNP 和 breakpoint 的狀態最後**人工**標到樹上。

## 三位 single-nucleus 病人的實際數字

以下數字取自 Table S3、S17、S18（xlsx），用本機 stdlib 讀取 xlsx 後統計。

| 病人 | 單核定序的樣本（每樣本 nuclei 數） | nuclei 定序／用於分析 | primer 目標（S17） | 可用 SNV／breakpoint 目標（S3） |
|---|---|---:|---:|---:|
| 2 | omentum ×2（各 126）、right ovary ×2（84、252） | 588／491 | 48 | 42／5 |
| 3 | adnexa、omentum、right ovary ×2（各 168） | 672／636 | 96 | 83／12 |
| 9 | left ovary ×2、omentum ×2、right ovary（各 84） | 420／402 | 48 | 43／5 |

S18 每個樣本的 nucleus 孔數加總，恰好等於 S3 的定序數（588／672／420）。

**資料內 conflict**：§4.8 p.17 寫「48 loci for patients 2 and 96 loci for patient 9」。但 S17 primer 表是病人 2 = 48、**病人 3 = 96**、病人 9 = 48，S3 的可用目標數也和 S17 一致。本筆記採表格數字，原文句子應是筆誤。

**Clone genotype（Table S8；p.41 Supp. Fig.16 已渲染核對一致）**：每個 clone 列出含有的 PyClone cluster ID。粗體的 cluster 是祖先有、但該 clone 流失的。

| 病人 | clone genotype | 流失 |
|---|---|---|
| 2 | A{5,8,11}；B{5,8,9,11}；C{1,5,8,11}；D{1,8,11}；E{1,4,5,8,11}；F{1,4,5,8} | D 流失 **5**；F 流失 **11** |
| 3 | A{7,10,16}；B{7,8,10,16}；C{7,10,16,17}；D{10,16,17}；E{6,10,16,17}；F{1,10,16,17}；G{1,4,16,17} | D 流失 **7**；G 流失 **10** |
| 9 | A{1}；B{1,6}；C{1,4} | 無 |

## 與 PhyClone benchmark 真值的對應（本機資料核對）

`/big8_disk/boyu114/phyclone_dataset/HGSOC/p{2,3,9}_{wgs,wgs_t}/data_archive/p*/ground_truth/tree.json` 的節點 ID 就是上表的 clone 字母。邊如下：

- p2：A→B、A→C、C→D、C→E、E→F
- p3：A→B、A→C、C→D、D→E、D→F、F→G
- p9：A→B、A→C

這些和 S8 的 genotype 包含關係一致。

| 病人 | truth SNV／PhyClone 輸入 mutation | truth SNV 在 S16（targeted deep seq）中 | 其中屬於 single-nucleus 目標的 |
|---|---:|---:|---:|
| 2 | 43／5,060 | 43／43 | 15 |
| 3 | 149／2,882 | 149／149 | 35 |
| 9 | 112／2,014 | 112／112 | 12 |

`status: inferred`，依據是上表的本機核對：

1. **truth SNV 不只是單核定序過的位點**。所有 truth SNV 都來自 Table S16 的 targeted bulk deep-seq PyClone cluster，大部分 SNV 從沒在單細胞中測過。它們的節點歸屬，是由 **bulk deep-seq PyClone cluster 加上 single-nucleus 的 cluster-level genotype** 共同決定的。PhyClone 主文說真值「只由選入 single-cell targeted deep sequencing 的子集定義」，應理解為 targeted deep-seq 子集，而不是單核位點。
2. **p2 的真值把流失訊號剝掉了**。S8 裡的 cluster 5 和 11 並沒有出現在 PhyClone 的 p2 truth 中，即使這兩群 SNV 有 3 個和 14 個在輸入 `data.tsv` 裡。因此 D、F 在 truth 中是空節點，`lost_snvs` 也是空的。PhyClone 論文沒有說明 truth SNV 的納入規則；為何排除這兩群目前是 `UNRESOLVED`。p3 的 truth 則保留了 E、F、G 的 `lost_snvs`。
3. **分群不是獨立的**。PhyClone 對 HGSOC「使用原始研究提供的 clusters」，和建真值用的 PyClone cluster 同源。因此 HGSOC 的 V-measure 主要反映 outlier／loss 處理，不是獨立的分群能力。

## 真值強度與限制

- **真值等級**：模型推論的 reference tree，不是觀測到的 lineage。它依序經過 SCG 分群、cluster 層級的二值化，再用 bulk SNV 數加權的 stochastic Dollo ML 建樹，並有人工標註。
- **病人與位點太少**：只有 3 名病人，每人 48–96 個 PCR 目標，可用的只有 47–95 個。只有 ≥10 nuclei 的 clone 會進入建樹，rare clone 看不到。
- **偏差來源**：
  - 抽 SNV 的條件是「依 bulk 推論為 informative 的 cluster」，所以真值天生偏向 bulk 已經看得到的結構。
  - 單核 PCR 的 allelic dropout，由 SCG 的 error 和 doublet 模型吸收，沒有獨立量化。
- **與 bulk 的獨立性**：真值樹的 cluster 定義和權重都來自 bulk，所以拿同源的 bulk 輸入評估，不是完全獨立的驗證。這正是 `REPO_IMPROVEMENTS.md` §6「參考樹與驗證資料不獨立」的又一個例子。
- **作者做的額外驗證**：
  - 病人 2 的 CCNE1 分歧：最佳 SNV 樹和 breakpoint 樹的 log odds 分別為 3680 和 297。CCNE1 擴增區的 28 個 breakpoint，起源於祖先分支的後驗機率都 < 0.001。break end 的有無和 CN 落差顯著相關（Mann–Whitney p = 2.8×10⁻⁷），並做了 FISH（§7 p.27；Table S12）。
  - 病人 9 的 ERBB2 做了 FISH 和 IHC（§3 p.14）。
  - 這些驗證支持特定事件，不是逐條 edge 的真值。
- **技術背景**：全為 short-read，參考基因組是 hg19。沒有 haplotype phasing，也沒有 HP/PS。

## 可取得資料

- PhyClone 整理過的 HGSOC 輸入與 truth：`/big8_disk/boyu114/phyclone_dataset/HGSOC/`，含 `data.tsv`、`results.tsv`、`tree.json`、`ground_truth_coloured.png`，以及各方法的輸入與輸出。
- 原始單核 read count、primer、clone genotype 與 prevalence：本目錄的 `supplementary_tables.xlsx`（S8、S9、S16–S19）。
- 原始 WGS 的 accession 不在 supplement 裡，主文未讀，所以這裡沒有列 raw data 位置。

## 對本 repo 的用處（尚未實作）

- **C2／C3 的 loss 測試**：p3 是 PhyClone 唯一有明確 loss 真值的真實病人（E、F、G 帶 `lost_snvs`）。若要比較 multiplicity 或 CN-aware loss 模型，p3 適合當 regression case。p2 的 truth 已剝掉 loss，不適合這個用途。
- **評估方法**：沿用 PhyClone 的做法，把預測樹修剪到只剩 truth SNV，再折疊變空的節點。但要另外報告「truth SNV 占輸入的比例」：p2 只有 0.85%，p3、p9 約 5%。這樣避免把子集上的分數當成整樹準確率。
- **作為 C4／long-read 驗證的定位**：這組資料沒有 long reads，不能驗證 HP 或 co-read 特徵的增益。它的價值是作為「單核 genotype → clone tree」的方法範式，可以和 A03（同樣用 SCG）、B04（scDNA 局部驗證）對照。

實讀定位：
- §1–2 p.9–14：樣本、WGS 與 sample tree
- §4 p.15–18：targeted bulk 與 clone phylogeny
- §5 p.18–20：single nuclei
- §6 p.20–26：infinite sites with loss
- §7 p.27：CCNE1 驗證
- Supp. Fig.16 p.41；Supp. Fig.17 p.42
- Table S3 p.69（欄位說明；數值在 xlsx）
