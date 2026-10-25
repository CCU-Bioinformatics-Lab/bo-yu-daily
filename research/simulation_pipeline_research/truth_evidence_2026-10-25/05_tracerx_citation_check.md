# 05 TRACERx 相關引用核對（2026-10-25）

核對對象：`04_event_evidence_real_tumors.md` 中所有和 TRACERx 有關的數字、DOI 與程式參數。
做法：逐篇打開原文全文或資料檔，逐字比對。本檔只新增，不改 04。

## 1. 結論

- 共核對 **19 條**主張：✅ 14 條、⚠️ 5 條（#6、#7、#8、#16、#19）、❌ 0 條、❓ 0 條。
- 論文數字本身都對得上原文。問題集中在三處：
  1. **出處標錯**：「TRACERx WES 中位 413×」是 TRACERx 421（Frankell 2023）。TRACERx 100（Jamal-Hanjani 2017）是 **426×**。
  2. **CONIPHER 參數混用**：coverage 400、purity 0.7–0.9 只是函式預設值。作者 150 份 benchmark 模擬實際從 cohort 表抽值。實測 purity 是 **0.21–0.90**，每份模擬的 depth 中位是 **142–718×**。
  3. **分母不同，不能直接比**：TRACERx 的 13% 是「subclonal 突變」中的比例。CONIPHER 的 `prop_mut_lost` 和使用者設計的 20／100 是「全部 SNV」中的比例。所以「在範圍內，偏高端」要改成「高於 TRACERx 中位，接近 CONIPHER 上限」。
- 「Frankell 2023 有 150 份模擬」在 Frankell 正文與 Methods 找不到。150 份來自 CONIPHER 的 Zenodo 資料。
- 04 沒有引用 Martínez-Ruiz 2023、Bailey 2023、TRACERx Renal，所以這三篇不在核對範圍。

## 2. 取得原文的方式

| 論文 | 取得方式 | 狀態 |
|---|---|---|
| Jamal-Hanjani 2017 NEJM | Glasgow eprints 全文 PDF（eprints.gla.ac.uk/219104，NEJM 排版版），pdftotext 後逐字搜尋 | 全文 |
| Watkins 2020 Nature | PubMed Central PMC7611706 全文 | 全文（PMC 去掉了部分上標與基因名） |
| Frankell 2023 Nature | PubMed Central PMC10115649 全文（含 Methods） | 全文 |
| Grigoriadis 2024 Nat Protoc（CONIPHER） | nature.com 頁面；正文付費，只取得摘要、Data availability、Code availability | 部分 |
| CONIPHER benchmark 資料 | Zenodo 10.5281/zenodo.10048165（`dataset1.zip` 用 HTTP range 只讀 150 個 `_info.tsv`；`dataset2.zip` 36 MB 整包下載到 scratchpad） | 實測 |
| TRACERx_simulation_tool | 本 repo `upstream/TRACERx_simulation_tool/`（commit `facd2d7`） | 程式 |

DOI 解析：四個 DOI 都用 PubMed metadata 確認，題名、期刊、卷頁都正確。

## 3. 核對表

判定符號：✅ 正確；⚠️ 部分正確；❌ 錯誤；❓ 無法取得原文。

### 3.1 Jamal-Hanjani 2017（TRACERx 100）

| # | 04 原句（位置） | 原文證據（逐字，位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 1 | 「多區域 WES，100 例 NSCLC」（§2.2） | "we performed multiregion whole-exome sequencing on 100 early-stage NSCLC tumors … We sequenced and analyzed 327 tumor regions"（Abstract, Methods） | ✅ | 可補「327 個 region」。 |
| 2 | 「92 例有 CN 資料，其中 62% 有 mirrored subclonal allelic imbalance」（§2.2） | "This phenomenon was observed in 62% of 92 tumors with copy-number data on multiregion whole-exome sequencing (found in 30 adenocarcinomas, 23 squamous-cell carcinomas, and 4 other samples)."（Results，p.2115） | ✅ | 可補絕對數：57／92 例。 |
| 3 | 「MSAI，不同 subclone 的不同 parental allele 各自 gain／loss」（§2.2） | "if the maternal allele is gained or lost in a subclone in one region, yet the paternal allele is gained or lost in a different subclone in another region, it will result in a mirrored subclonal allelic imbalance profile"（Results；Fig. 3A 圖說） | ✅ | 要註明：MSAI 是**多 region** 才看得到的現象。 |
| 4 | 「共 375 個 MSAI 事件，佔受影響基因組 1–43%」（§2.2） | "In total, we detected 375 mirrored subclonal allelic imbalance events that varied in size from focal to whole chromosome and involved 1 to 43% of affected tumor genomes"（Results，p.2115） | ✅ | 無。 |
| 5 | 「每個樣本的 subclonal 突變中，中位 13%（範圍 0–56%）可能是 CN loss 造成的『看似 subclonal』」（§2.3） | "Overall, a median of 13% of subclonal mutations (range, 0 to 56) per sample are probably subclonal as a result of loss events associated with copy-number alterations"（Results，p.2115） | ✅ | 無。 |
| 6 | §3 表「subclonal HP1 gain」列：「TRACERx：62% 有 MSAI」用來支持設計 | 同 #2、#3 | ⚠️ | 數字對，但用途不完全對應。設計的 seg A 是**單一 allele、單一 subclone** 的 gain，不是 mirrored 事件。MSAI 需要兩個 subclone 動到不同 allele。建議改用 Watkins 的「中位 18% 基因組有 subclonal SCNA」當主證據；MSAI 只當「haplotype-specific subclonal CN 常見」的旁證。〔推論〕 |
| 7 | §3 表「突變遺失比例」列：「s2＋s10 共 20／100 個 SNV 受影響；TRACERx：subclonal 突變中位 13%（0–56%）來自 loss……**在範圍內，偏高端**」 | 同 #5；另有 "a median of 30% (range, 0.5 to 93) of somatic mutations identified as subclonal"（Results，p.2111） | ⚠️ | 分母不同。13% 的分母是 subclonal 突變；20／100 的分母是全部 SNV。粗估換算：13% × 30% ≈ 4% 的全部突變〔推論；兩個中位數相乘只是量級估計〕。設計值 20% 約是 TRACERx 中位的 5 倍，只落在 0–56% 的上段，也接近 CONIPHER 上限 0.25。建議改為「高於 TRACERx 典型值，屬壓力測試」。 |

### 3.2 TRACERx depth

| # | 04 原句（位置） | 原文證據 | 判定 | 修正建議 |
|---|---|---|---|---|
| 8 | 「TRACERx WES 中位 413×」（§3 depth 列，沒有標出處） | Frankell 2023："These tumour samples were subjected to whole-exome sequencing (WES) at a median depth of 413× (interquartile range (IQR) = 367–474)"（Results 第一段）。Jamal-Hanjani 2017："to a median depth of 426× (Table S3 in Supplementary Appendix 1)"（Results） | ⚠️ | 413× 正確，但屬 **TRACERx 421**（1,644 個 tumour region）。要標出處為 Frankell 2023。TRACERx 100 是 426×。另外要註明是 **WES**，不能和 WGS 的 depth 直接比。 |

### 3.3 Watkins 2020

| # | 04 原句（位置） | 原文證據（PMC7611706） | 判定 | 修正建議 |
|---|---|---|---|---|
| 9 | 「394 個腫瘤、1,421 個樣本、22 種癌，多樣本 phasing」（§2.2） | "We applied a multi-sample phasing SCNA analysis method … to 1,421 cancer samples from 394 patients across 22 tumour subtypes (median 3 samples per tumour; range 2–16 samples per tumour)" | ✅ | 可註明：這是泛癌 cohort，只有一部分來自 TRACERx 100（原文："A subset of the WES cohort … comes from the first 100 patients prospectively analysed by the lung TRACERx study"）。 |
| 10 | 「基因組中位 18% 有 subclonal SCNA（clonal 是 26%）」（§2.2；§3 也引用） | "A median of 26% of the genome was subject to clonal SCNAs and 18% to subclonal SCNAs." | ✅ | 無。 |
| 11 | 「45% 腫瘤有 > 20% 基因組是 subclonal SCNA」（§2.2） | "In 45% of tumours, more than 20% of the genome was subject to subclonal SCNAs" | ✅ | 無。 |
| 12 | 「37% 腫瘤有 parallel 事件」（§2.2） | "Parallel evolution of SCNA events … was observed in 146 out of 394 (37%) tumours" | ✅ | 可補絕對數 146／394。 |
| 13 | DOI 10.1038/s41586-020-2698-6；*Nature* 587:126–132 | PubMed PMID 32879494：題名、卷 587、頁 126–132 相符 | ✅ | 無。 |

### 3.4 CONIPHER（Grigoriadis 2024）與 TRACERx_simulation_tool

| # | 04 原句（位置） | 證據 | 判定 | 修正建議 |
|---|---|---|---|---|
| 14 | 「150 份模擬，依樣本數分組」（§4） | Zenodo `dataset1.zip` 與 `dataset2.zip` 各有 150 個 `_info.tsv`〔實測〕。程式 `make_tx_simulations(n_sims_per_sample_group=50, sample_group_boundaries=(3,7))` 產生 3 組 × 50 份（`src/make_simulation.py:9`）。Frankell Methods："{8, …, 16}, {12, … 24} and {22, …, 30} for the low (2–3 samples), medium (4–7 samples) and high (>7 samples) sample size groups" | ✅ | Nat Protoc 正文付費，沒有讀到正文對「150」的描述。Data availability 只寫 "The three simulated datasets used in the benchmarking analyses are available at https://zenodo.org/doi/10.5281/zenodo.10048164"。建議出處寫「Zenodo 資料實測＋程式」。 |
| 15 | 「生成器有 mutation loss、WGD、noise」（§4） | Frankell Methods："our framework models … truncal and subclonal SCNAs (including gains, losses, copy-neutral LOHs, among others) as well as truncal and subclonal WGDs" 與 "we simulated the presence of noisy and artefactual mutations"。程式有 `prop_mutloss_positions`、`clonal_wgd`／`subclonal_wgd`、`fract_noise` | ✅ | 可補：生成器也模擬 copy-neutral LOH（程式標記 `cnloh_A`）。 |
| 16 | 「預設 coverage 400、purity 0.7–0.9」（§4） | `src/simulate.py:35–37`：`coverage=400, min_tumour_purity=0.7, max_tumour_purity=0.9`（只是 `tx_simulation()` 的函式預設）。benchmark 用的 `make_tx_simulations()` 改從 cohort 表抽：`'Purity': purity, 'Coverage': coverage`（`src/make_simulation.py:32,69–71`）。Zenodo dataset1 實測：`min_tumour_purity` 0.21–0.87，`max_tumour_purity` 0.26–0.90〔實測〕。dataset2 每份模擬的 DEPTH 中位是 142–718×，中間值 455×〔實測〕 | ⚠️ | 改寫為：「函式預設 coverage 400、purity U(0.7, 0.9)；作者 benchmark 實際從 TRACERx 421 摘要表抽 purity（>0.2）與 coverage，實測 purity 0.21–0.90」。另外要註明：repo 附的 `data/TRACERx_data.tsv` 是隨機產生的替代表（README："Currently, the data provided … is a randomly simulated dataset of patient summary genomic information"），不是真實 TRACERx 數值。 |
| 17 | 「CONIPHER 生成器 `prop_mut_lost` 0.02–0.25」（§3 突變遺失列） | Zenodo dataset1（有 noise）150 份：`prop_mut_lost` 最小 0.02、中位 0.16、最大 0.25，沒有任何一份是 0〔實測〕。dataset2（無 noise）150 份全部是 0.0〔實測〕。程式的輸入值是 `np.arange(0.1, 0.26, 0.01)`（`src/make_simulation.py:39`）；輸出的 `prop_mut_lost` 是實現值，分母是**全部 SNV 位點**（`src/evolution.py:208`） | ✅ | 數字正確。要補兩點：(1) 只有 noise 組有 loss；(2) 分母是全部 SNV，不是 subclonal SNV，所以不能和 TRACERx 的 13% 直接比（見 #7）。 |
| 18 | DOI 10.1038/s41596-023-00913-9；*Nat Protoc* 19:159–183 (2024) | PubMed PMID 38017136：題名、卷 19、期 1、頁 159–183 相符 | ✅ | 無。 |

### 3.5 Frankell 2023（04 第 182 行查核備註）

| # | 04 原句 | 原文證據（PMC10115649） | 判定 | 修正建議 |
|---|---|---|---|---|
| 19 | 「WGD 77%、subclonal WGD 19%、150 份模擬」 | "we observed at least 1 WGD event in 307 out of 401 (77%) of tumours" 與 "78 out of 401 (19%) of tumours had at least 1 subclonal WGD event"（Results）。全文與 Methods 搜尋不到「150 份模擬」；Methods 只提到 ParallelGDDetect 用了 "500 simulated tumours" | ⚠️ | WGD 77% 與 subclonal WGD 19% 正確（分母 401 個可建樹的腫瘤）。「150 份模擬」要改標出處為 CONIPHER Zenodo 資料（見 #14），不要掛在 Frankell 名下。DOI 10.1038/s41586-023-05783-5 與 *Nature* 616:525–533 正確（PMID 37046096）。 |

另外核對 Jamal-Hanjani 2017 書目：DOI 10.1056/NEJMoa1616288 解析到 PMID 28445112，*NEJM* 376(22):2109–2121，正確（併入 #1–#5 的 ✅，不另計）。

## 4. 補充：04 沒有用、但更有力的 TRACERx 數字

依主題排列。全部是原文逐字引用。

### 4.1 clone 數與樹形

| 數字 | 原文（位置） | 對本研究的意義〔推論〕 |
|---|---|---|
| TRACERx 100 共 525 個 mutation cluster，每個腫瘤中位 5 個（2–15） | "We identified 525 mutation clusters, with a median of 5 per tumor (range, 2 to 15)."（Jamal-Hanjani 2017，Results） | 設計的 4 個 clone 接近中位 5，比 PCAWG 或 Minussi 的數字更直接支持「4 個 clone 合理」。 |
| 86% 的 region 只帶單一 branch 的 subclone | "Most tumor regions (86%) were found to carry subclones from only a single branch of the phylogenetic tree"（同上） | 單一 bulk sample 通常只看到一條 branch。設計中 C3 與 C2／C4 同時出現在一個樣本，屬較少見但可能的情況。符合「單一 sample」主軸的限制說明。 |
| 沒有多 region 時，76% 的 subclonal 突變會看似 clonal；65% 的 branched subclone cluster 會看似 clonal | "Without multiregion whole-exome sequencing, 76% of subclonal mutations could have appeared to be clonal" 與 "65% of branched subclone clusters could have erroneously appeared to be clonal"（同上） | 單一樣本推理的上限問題。可用來說明為什麼要靠 HP／read 共現補資訊。 |
| 模擬用的 clone 數 8–30；每個 bulk sample 3–8 個 clone | "among the range {8, …, 30} … of clones observed in the TRACERx 421 cohort"；"chosen uniformly at random from the range {3, … 8} of tumour clones typically observed within the same tumour sample"（Frankell 2023，Methods） | 一個樣本 3–8 個 clone。設計的 4 個 clone 在範圍下段。 |

### 4.2 subclonal 比例與 SCNA

| 數字 | 原文（位置） | 意義〔推論〕 |
|---|---|---|
| 中位 30%（0.5–93）突變是 subclonal；中位 48%（0.3–88）CNA 是 subclonal | "a median of 30% (range, 0.5 to 93) of somatic mutations identified as subclonal and a median of 48% (range, 0.3 to 88) of copy-number alterations as subclonal"（Jamal-Hanjani 2017，Results） | #7 換算分母要用這個數字。 |
| 99% 腫瘤至少有一個 subclonal SCNA | "99% of tumours (390 out of 394) had at least one subclonal SCNA"（Watkins 2020） | subclonal HP1 gain 的存在性證據，比 MSAI 更直接。 |
| HLA 區 subclonal LOH 影響 22% 的 cohort | "The HLA locus (chromosome 6p21.3) represented a clear peak of subclonal LOH in WGD samples, which affected 22% of the cohort"（Watkins 2020） | subclonal LOH 常見的例子。注意：原文是 LOH，不一定是 copy-neutral LOH；Watkins 全文沒有 "copy-neutral" 一詞。 |
| clonal WGD 49%（Watkins 泛癌）；TRACERx 421 WGD 77%、subclonal WGD 19%、多個平行 subclonal WGD 10% | Watkins："whole-genome doubling, that was found as a clonal event in 49% of tumours"。Frankell："39 out of 401 (10%) of tumours had multiple subclonal WGD events, each occurring on parallel phylogenetic branches" | 若之後加 WGD 情境，可用這組數字。 |

### 4.3 突變遺失與低 CCF subclone

| 數字 | 原文（位置） | 意義〔推論〕 |
|---|---|---|
| 26% 腫瘤至少有一個「recent」subclonal expansion（終端 node） | "in 26% of tumours, we observed at least one 'recent' subclonal expansion, whereby a terminal node o[f the tree …]"（Frankell 2023，Results） | 和低 CCF 終端 clone（C3）的情境有關，但原文是大 expansion，不是低 CCF。只能當旁證。 |
| CONIPHER 第二步移除 cluster 時，平均移除 2% 突變（中位 0%） | "a mean of 2% of all mutations were removed (median = 0%) across 401 TRACERx phylogenies"（Frankell 2023，Methods） | 真實資料中被判為不合理的 cluster 很少。 |
| 模擬只取 purity > 20%、SNV > 150、truncal 比例 < 90% | "tumour purity >20%; number of somatic SNVs >150; and proportion of truncal mutations <90%"（Frankell 2023，Methods） | 使用者設計 purity 0.40、SNV 100 個。SNV 數低於 CONIPHER 模擬下限 150。 |

本次沒有在 TRACERx 原文找到「低 CCF subclone（例如 CCF < 0.1）頻率」的直接數字。〔未查到〕

## 5. 參考文獻

1. Jamal-Hanjani M et al. Tracking the evolution of non-small-cell lung cancer. *N Engl J Med* 376(22):2109–2121 (2017). [10.1056/NEJMoa1616288](https://doi.org/10.1056/NEJMoa1616288)（PMID 28445112；全文取自 eprints.gla.ac.uk/219104）
2. Watkins TBK et al. Pervasive chromosomal instability and karyotype order in tumour evolution. *Nature* 587(7832):126–132 (2020). [10.1038/s41586-020-2698-6](https://doi.org/10.1038/s41586-020-2698-6)（PMID 32879494；PMC7611706）
3. Frankell AM et al. The evolution of lung cancer and impact of subclonal selection in TRACERx. *Nature* 616(7957):525–533 (2023). [10.1038/s41586-023-05783-5](https://doi.org/10.1038/s41586-023-05783-5)（PMID 37046096；PMC10115649）
4. Grigoriadis K et al. CONIPHER: a computational framework for scalable phylogenetic reconstruction with error correction. *Nat Protoc* 19(1):159–183 (2024). [10.1038/s41596-023-00913-9](https://doi.org/10.1038/s41596-023-00913-9)（PMID 38017136；正文付費，只讀摘要與 availability 段）
5. CONIPHER benchmarking 資料。Zenodo [10.5281/zenodo.10048165](https://doi.org/10.5281/zenodo.10048165)（concept DOI 10.5281/zenodo.10048164）
6. TRACERx_simulation_tool，https://github.com/zaccaria-lab/TRACERx_simulation_tool；本地 `research/simulation_pipeline_research/upstream/TRACERx_simulation_tool/`（commit `facd2d7`）

文獻來源：PubMed／PubMed Central（metadata 與 PMC 全文）。
