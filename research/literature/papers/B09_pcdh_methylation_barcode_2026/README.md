---
paper_id: B09
category: "C3b"
category_label: "single-cell 真值樹 × long-read 特徵"
subtype: "c3b_methylation_barcode_tree_sc_truth"
sc_truth_strength: "benchmark_truth"
title: "In vivo lineage tracing across human tissues using methylation barcodes in the protocadherin gene cluster"
year: 2026
doc_type: "method"
material: "human_patient"
platform_class: "long_read_feature"
platform_detail: ["ONT PromethION R9.4.1 bulk WGS with 5mC calls (PD6646, ~280X, mean read 10.3 kb)", "ONT R10.4.1 (KX004 control)", "targeted EM-seq short reads for 10-CpG barcodes"]
long_read_role: "tree_input"
long_read_features: ["per-read 5mC CpG pattern across PCDH (epiallele barcode)", "LongPhase/WhatsHap haplotag (HP)"]
single_cell_truth: "sc_derived_benchmark_truth"
single_cell_tech: ["WGS of single-cell-derived colonies (Williams 2022, PD6646)"]
input_is_single_cell: false
tree_type: ["read_dendrogram"]
cross_tags: ["methylation", "haplotag", "read_cooccurrence_model", "transferable_to_long_read", "purity_lower_bound", "no_copy_number", "priority_intersection"]
keywords_en: ["protocadherin", "pcdh", "methylation barcode", "epiallele", "epimutation", "fluctuating cpg", "lineage tracing", "oxford nanopore", "longphase", "whatshap", "haplotag", "modkit", "hamming knn imputation", "upgma", "barcode fraction", "clonal hematopoiesis", "mpn", "aml", "purity lower bound"]
keywords_zh: ["原鈣黏蛋白", "甲基化條碼", "表觀等位基因", "表觀突變", "譜系追蹤", "長讀定序", "單倍型定相", "克隆造血", "純度下界"]
summary_zh: "HP 分相的 ONT read 上 PCDH CpG pattern 建 UPGMA 樹；對照同病人 colony WGS 樹。"
category_index: "../../PAPER_CATEGORIES.md"
---

# B09｜PCDH methylation barcode：用 HP-phased ONT read 的 CpG pattern 建 lineage 樹（Hackett … Blundell；bioRxiv 2026）

閱讀日：2026-10-20。標記：「論文描述」＝正文明寫；「推論」＝我的分析；「本地查核」＝我在本機資料上實際檢查的結果。`[L.N]` 指本地 `paper.txt` 的行號；`[S.N]` 指 `supplement.txt` 的行號。

## 先看結論

- **相關度：高。** 但它的用途是「long-read 特徵」與「正交驗證」，不是可直接套用的 clone tree 方法。
- 它是目前收錄論文中，唯一用 **longphase／WhatsHap 的 HP tag 把 ONT read 分 haplotype，再用每條 read 的多位點 pattern 建樹**，並和同一病人的 single-cell-derived colony WGS 樹比對的研究 [L.31, L.52]。
- 它補上 M08 的缺口：somatic SNV 在一條 read 上太稀疏，但 PCDH 區每條 read 平均有 220 個 CpG [L.80]。
- 本地查核：Google Dorado 版 CRAM 帶 5mC 的 `MM/ML` tag。舊版 HCC1395 ONT CRAM 沒有。CRAM 都沒有 HP tag，要先跑 longphase haplotag。
- 限制：只有 1 位 MPN 病人；樹是 read 的 UPGMA dendrogram，不是 SNV clone tree；比對只有目視 topology 與 clade fraction；branch length 不符；沒有公開 code [L.33, L.79]。

## 書目、版本與檔案

- Hackett SF\*, Boniface CT\*, Fonseca AVA, Ramos-Yamasaki AD, Watson C, Bazin HML, Tan AB, Lee Yu H, Hanssen LLP, Dev H, Apostolidou S, Gentry-Maharaj A, Esener S, Menon U, **Blundell JR**. **In vivo lineage tracing across human tissues using methylation barcodes in the protocadherin gene cluster.** *bioRxiv* 2026-02-23, v1。DOI [10.64898/2026.02.23.707349](https://doi.org/10.64898/2026.02.23.707349)。CC BY-NC-ND 4.0。
- bioRxiv 從 2025-12 起改用 `10.64898` 前綴，所以 DOI 格式正確（見 `longread_tree_search_2026-10-19/README.md`）。
- 尚未正式發表（bioRxiv API `published: NA`，2026-10-20 查詢）。

| 本地檔 | 內容 | 來源 |
|---|---|---|
| `paper.pdf` | 正文 PDF，13 頁 | `biorxiv.org/content/10.64898/2026.02.23.707349v1.full.pdf` |
| `paper.xml` | JATS XML 全文 | `biorxiv.org/content/early/2026/02/23/2026.02.23.707349.source.xml` |
| `paper.txt` | 由 XML 轉出的純文字，每段一行。MathML 公式沒有轉出 | 本地轉檔 |
| `supplement.pdf` | Supplementary Notes 1–19、Fig. S1–S19、Table S1，19 頁 | bioRxiv `DC1/embed/media-1.pdf` |
| `supplement.txt` | `pdftotext` 轉出。Table S1 與多數圖是影像，沒有文字 | 本地轉檔 |

**程式碼**：正文只寫「custom workflow and scripts」[L.51, L.79]。正文與補充資料都沒有 code 或 data accession 連結。

## 論文在做什麼

### 核心主張（論文描述）

- PCDH gene cluster 的 CpG 會隨機（去）甲基化。這些 pattern 可以遺傳，所以可以當成天然 lineage barcode [L.4]。
- 單一細胞擴張成 clone 時，barcode 多樣性會崩縮成兩組。兩組分別對應 founder cell 的母源與父源 haplotype [L.16]。
- clone 擴張後，barcode 仍持續 epimutation。甲基化約 10⁻²／年，去甲基化約 10⁻³／年 [L.24]。所以 subclone 會帶著從 founder 衍生、差 1–2 個位點的 barcode [L.25–26]。

### 資料（論文描述）

| 資料 | 平台 | 用途 |
|---|---|---|
| UKCTOCS 50 pre-AML + 50 control，每年抽血，最長 10 年 | targeted EM-seq，PE，約 1000X；另有 duplex panel 當 clone size 真值 [L.49] | 10-CpG barcode、barcode fraction（BF）、epimutation rate |
| UKCTOCS 單時間點 112 pre-AML + 111 control | targeted EM-seq | BF 預測 AML 風險 [L.22] |
| **PD6646**（MPN 病人，顆粒球） | **ONT R9.4.1，約 280X，平均 read 10.3 kb** [L.31, L.76] | **long-read 建樹**。真值是 Williams 2022 的 colony WGS 樹 |
| KX004（健康人 PBMC，約 15% 早期擴張） | ONT R10.4.1，約 150X，平均 read 3.8 kb [L.76, L.80] | polyclonal 負對照 |
| ccRCC、oncocytoma、前列腺、膀胱、肺 | 公開 methylation 資料 | 跨組織 BF；BF 是 purity 下界 [L.36, S.1503] |

### Long-read 建樹流程（論文描述）

1. Dorado 做 basecalling 與 5mCG call，對齊 GRCh38 [L.76]。
2. Clair3 內建的 WhatsHap，加上 **LongPhase v1.7**，給每條 read 一個 haplotype tag [L.52]。
3. `modkit extract calls` 取出每條 read 的 CpG 狀態 [L.78]。
4. 以約 3 個 exon 為一個 window（平均 29.5 kb、646 個 CpG），用 greedy 法建「read × CpG」矩陣。每個 haplotype 一個矩陣 [L.80]。
   - 每條 read 的 CpG dropout ≤20%，連續 dropout ≤5 個。
   - PD6646 的矩陣平均 66 條 read × 152 個 CpG（每個 haplotype）。
5. 用 Hamming 距離 kNN（k=3）補缺失的 CpG [L.82]。
6. 用 Hamming 距離 + average linkage（UPGMA）做階層分群 [L.82]。
7. 取最上層兩群的 read 比例當作「cancer vs. 正常」比例，再以 5 群切分看 subclade [L.82]。

### 結果（論文描述）

- 單一 window（PCDHα exon 2–4）的 dendrogram 和真值樹「closely resembled」[L.31]。這是目視比較，沒有樹距離數字。
- 兩個 haplotype 的 dendrogram 彼此一致 [L.31]。
- 37 個 window 的 clade fraction 分布，和真值的遺傳 clone size（DNMT3A clone 約 84%）一致 [L.32]。
- KX004 負對照得到不同的 clade size [L.31]。
- branch length 無法重現。作者歸因於 CpG dropout 與 call error [L.33]。
- 補充：kmeans（k=2，不補值）估 DNMT3A clone fraction 比 hclust 略好 [S.1035]。

### 模擬（論文描述）

- agent-based Wright–Fisher 模擬，N=10,000，每個 haplotype 500 個 CpG，epimutation 0.01／代 [L.84]。
- 加 10% call error、20% dropout 後，barcode 要 >20–25 個 CpG 才能分出 founder／subclone [L.30, S.912]。
- clone fraction 約 20% 時，kNN 補值準確度只有 60–65% [L.86]。

## 和本研究的關聯（推論）

### 1. 它用的就是本研究的工具鏈

- ONT bulk WGS、LongPhase 的 HP tag、每條 read 的多位點 pattern。這三者正是本研究要接進 PhyClone 的特徵。
- 差別在位點類型：它用 CpG 5mC，本研究目前用 somatic SNV。

### 2. CpG 解決 M08 指出的「每條 read 位點太少」問題

- M08 README 的第 1 個移植問題是：多數 ONT read 只蓋到 0–1 個 somatic SNV。
- PCDH 區每條 read 平均蓋到 220 個 CpG（PD6646）[L.80]。
- 所以 per-read epiallele 可以當成 BitPhylogeny 式「整條 read 共用一個 clone 來源」的資料，而且資訊量遠高於 SNV。

### 3. 可以當 cell line 的正交驗證

- 本研究的 6 株 cell line 沒有 single-cell 真值樹（見 `PAPER_CATEGORIES.md` 的空缺）。
- PCDH barcode 和 SNV 是獨立的 lineage marker。若 PhyClone 推出 subclone，PCDH dendrogram 應該在對應 haplotype 上出現相同比例的分群。
- 這不能取代 single-cell 真值，但能當「不依賴 SNV」的佐證。

### 4. barcode fraction 可以估 tumor read fraction

- 作者說 BF 是 tumor purity 的下界 [S.1503]。
- 本研究的 `tX_nY` 是 tumor 與 matched normal 依設計比例混合。tumor 與 normal 的 founding barcode 不同，所以可以在 PCDH 上分開計數。
- 這可以給出和 nominal purity 無關的實測估計。要注意 3 點：
  - read fraction 不等於 cell fraction。tumor 在 PCDH 區的 haplotype-specific CN 會改變比例，要用 CN 校正。
  - HCC1395BL 等 normal 是 lymphoblastoid cell line，本身可能是寡克隆，barcode 也會崩縮。先用 `t00_n25` 定出 normal 的 barcode。
  - 這只是單一 locus 的估計，需要和 SNV／CN 為基礎的 purity 比對。

### 5. 不能直接搬來用的地方

- **沒有 CN、沒有 purity、沒有機率模型。** UPGMA 只是距離分群。
- **cell line 的 epimutation rate 未知。** 論文的 rate 來自數十年的體內血液。cell line 長期培養的 rate 可能不同（未驗證）。
- **癌細胞可能讓 PCDH 整區高甲基化。** 那樣 barcode 多樣性會消失。這要用本地資料檢查（未驗證）。
- **單一病人、目視比較。** 證據強度不足以支持「long-read 特徵可重建完整 clone tree」。
- **R9.4.1 錯誤率較高。** 本研究的 Dorado R10 資料 call error 可能較低，但沒有查核。

### 6. 和 PhyClone 的接法（推論，尚未實作）

- 與 M08 README 的提案相同：保留 PhyClone 的 SNV cluster likelihood，再乘上一項 per-read pattern likelihood。
- 每條 HP-tagged PCDH read 的 CpG pattern，對來源 clone 邊際化：`P(pattern | tree, prevalence, C_h) = Σ_clone w_clone(h) · P(pattern | clone 的 barcode, error)`。
- clone 的 barcode 本身是潛變數，沿樹以 epimutation rate 轉移。這比 SNV 的 infinite-sites 模型更接近 M08 的 rate-matrix 轉移核。
- 較低成本的第一步：先不改模型，只把 PCDH dendrogram 當成 PhyClone MAP 樹的事後驗證。

## 本地查核：資料是否可用

2026-10-20 檢查。每個檔只看 `chr5:141,000,000-141,010,000` 的前 200 條 read，所以只能證明 tag 存在，不能證明全檔一致。這段位於 GRCh38 的 PCDH 區內（論文 hg19 座標 `chr5:140,150,000-140,895,000` [L.56]；GRCh38 約 `chr5:140.78–141.52 Mb`，沒有跑 liftOver 驗證）。

| CRAM | `MM` tag | 修飾類型 | `HP` tag |
|---|---|---|---|
| `Google_somatic_data/bams/{HCC1395,HCC1937,HCC1954,H1437,H2009}/*_Tumor_ONT.GRCh38.sorted.cram` | 有（HCC1937：151/200，其餘全部） | `C+m`（5mC） | 無 |
| `data/HCC1395/ONT_Dorado/subsample/t50_n00/*.cram` | 有 | `C+m` | 無 |
| `data/H1437/ONT/subsample/t50_n00/*.cram` | 有 | `C+m` | 無 |
| `data/HCC1395/ONT/HCC1395.cram`（舊版） | 無 | — | 無 |
| `data/COLO829/ONT_R10/subsample/t50_n00/*.cram` | 無 | — | 無 |
| `data/COLO829/ONT_PAO/PAO29420.cram` | 有 | `C+h`（5hmC），`C+m` 未檢查 | 無 |

**下一步建議**：

1. 在 HCC1395 Dorado 的 tumor 與 normal CRAM 上跑 longphase haplotag。
2. 用 `modkit extract calls` 取 PCDH 區的 per-read CpG。
3. 計算 10-mer entropy，比對 tumor、normal 與 `t00_n25`。先確認 cell line 的 PCDH barcode 是否仍有多樣性。

## 真值樹的來源（2026-10-20 查核 Williams 2022 原文）

PD6646 的真值樹來自 Williams et al. 2022（*Nature* 602:162，DOI [10.1038/s41586-021-04312-6](https://doi.org/10.1038/s41586-021-04312-6)）。全文從公開 PDF 讀取，沒有存進 repo。

| 項目 | Williams 2022 的做法（論文描述） |
|---|---|
| 細胞來源 | PBMC 在 MethoCult 培養 14 天，挑出單一 BFU-E colony。每個 colony 來自一顆細胞 |
| 定序 | 每個 colony 各自做 Illumina WGS（150 bp PE，low-input 建庫）。全研究 12 位病人、1,013 個 colony |
| 單一細胞來源的檢查 | colony 的 somatic VAF 約 0.5（Extended Data Fig. 1b） |
| 建樹 | 只用 SNV 的 binary genotype 矩陣，用 MPBoot（maximum parsimony）建 topology |
| bulk 的角色 | 對 bulk 周邊血顆粒球做 targeted recapture（300–400×）。只用來**驗證** clade fraction（ACF = 2 × mean VAF），不參與建樹 |

**和 PhyClone HGSOC 真值樹（R01，McPherson 2016）的差別（推論）**：

- HGSOC 是 bulk 與 single-cell 混合：SNV 集合與 cluster 來自 bulk WGS、targeted deep seq 和 PyClone。single-nucleus 只對挑選的標記做 targeted PCR，再用 SCG 分群。建 Dollo 樹時還要用 bulk WGS 的 SNV 數加權。
- PD6646 的 topology 只來自 single-cell-derived colony 的全基因體 SNV。bulk 只做事後驗證。
- 所以 PD6646 真值樹的 single-cell 成分比 HGSOC 更純。代價是 colony 要先體外擴增，不是直接定序單顆細胞。

**未確認**：
- Hackett Fig. 4d 的「ground-truth genetic clone sizes」來自 colony 比例，還是 bulk recapture，論文沒寫。
- ONT 樣本（顆粒球）和 colony（PBMC 培養）的採樣時間是否相同，論文沒寫。

## 分類判定

- **C3b**，subtype `c3b_methylation_barcode_tree_sc_truth`（新子類）。
- 平台：ONT 原生 read；HP tag 與 per-read 5mC pattern 直接進入建樹。所以 `long_read_role` 是 `tree_input`。
- sc 真值：PD6646 的真值樹來自同一病人 single-cell-derived colony 的 WGS（Williams 2022），被用來評估本方法，所以標 `benchmark_truth`。
- 邊界：評估只是目視 topology 與 clade fraction，沒有量化樹距離，branch length 不符。若要求量化評估，改標 `partial`。
- 和 B04 的差別：B04 的 long read 只篩選 SNV clone tree 的候選 topology，scDNA 和 long read 不在同一病人。B09 的 long read 是建樹的唯一輸入，真值在同一病人，但樹不是 SNV clone tree。
- 它在 2026-10-19 的 long-read 搜尋中已被標為 include（`longread_tree_search_2026-10-19/README.md` 第 2 節）。當時沒有讀全文。
