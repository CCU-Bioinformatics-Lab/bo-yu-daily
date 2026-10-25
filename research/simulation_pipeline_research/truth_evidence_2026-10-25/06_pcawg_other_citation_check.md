# 04 檔 PCAWG 與其他非 TRACERx 主張的原文核對（2026-10-25）

對象：`04_event_evidence_real_tumors.md`（以下稱「04」）。
範圍：PCAWG（Gerstung 2020、Dentro 2021）、TCGA purity（Aran 2015、TCGA PDAC 2017）、Sivakumar 2021、Ciani 2022、SMC-Het（Salcedo 2020／2025）、AML31（Griffith 2015）、BAMSurgeon（Ewing 2015）、Farahani 2017、Salehi 2021、Minussi 2021，以及 04 末列「DOI 未逐一確認」的 6 篇（Kuipers、SCARLET、CHISEL、Alleloscope、Nik-Zainal、Marass）。
不核對：TRACERx 100／421、Watkins 2020、CONIPHER（另一位同事負責）。Funnell、Sakamoto、Keskus、LongPhase-S、McPherson、Pairtree、Tarabichi、Lai 不在本次範圍。
做法：用 PubMed 把 DOI 轉成 PMID／PMCID，確認標題與期刊。再從 Europe PMC／NCBI PMC 取全文，搜尋數字所在段落。Sivakumar 2021 的 PMC 沒有正文，改讀 OUP 期刊頁。Marass 2016 不在 PubMed，改讀 arXiv 1604.01715（ar5iv HTML）。查詢日期 2026-10-25。
引文為英文原句節錄（≤ 2 句）。

## 1. 結論

- **共核對 50 條主張：✅ 38 條、⚠️ 12 條、❌ 0 條、❓ 0 條。** ⚠️ 中有 3 條（#29、#49、#50）是 04 第 3 節的用法問題，原數字本身正確。
- **所有 DOI 都能解析到正確論文。** 20 篇用 PubMed ID converter 確認。Marass 2016 的 DOI 302 轉到 Project Euclid 的同名論文頁。
- **使用者點名的 6 個重點數字都正確：**
  - Gerstung：arm-level gain 80–90% 只加 1 copy ✅。
  - Aran：ABSOLUTE 62.3% ± 19.9% ✅。PDAC：中位 33% ✅。
  - Sivakumar：5,222／11,074 ≈ 47% 有 arm-level cnLOH ✅。但它不分 clonal／subclonal（⚠️ 用法）。
  - Dentro：中位約 46× ✅。CCF ≥ 30% 的門檻成立，前提是 nrpcc ≥ 10 ✅。
  - Griffith：約 850× 才找回 6 個 cluster ✅。但 850× 是 down-sampling 的 variant 深度，不是 WGS 深度（⚠️）。
  - SMC-Het：51 棵樹中 25 棵來自 PCAWG ✅。
- **最重要的修正（影響 04 第 3 節的判定）：** PCAWG「只保證 CCF ≥ 0.30」是 nrpcc = 10 時的值。門檻規則是「期望 ≥ 3 條 variant read」。我們的設計 nrpcc ≈ 40，用同一規則推得的最低 CCF ≈ 0.075。所以 C3（CCF 0.10）在 200× 時剛好高過 PCAWG 的理論門檻，不是「低於」。〔原文規則＋推論〕
- **其他 ⚠️ 都是描述細節的問題，不改變結論：** 樣本數、時間點、資料平台、引用來源張冠李戴。逐條見第 2 節。

## 2. 核對表

判定：✅ 正確／⚠️ 部分正確／❌ 錯誤／❓ 無法取得原文。

### 2.1 Aran 2015, Nat Commun（TCGA purity）

DOI [10.1038/ncomms9971](https://doi.org/10.1038/ncomms9971) → PMID 26634437、PMC4671203 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 1 | ABSOLUTE purity 平均 62.3% ± 19.9%（11 種癌） | "An exception was ABSOLUTE, with an average estimate of 62.3±19.9%." 另："ABSOLUTE … (estimations were available for only 11 cancer types)"（Results 第 1 段） | ✅ | — |
| 2 | consensus（CPE）平均 75.3% ± 18.9% | "CPE is the median purity level after normalizing levels from all methods to give them equal means and s.d.'s (75.3±18.9%)."（Results） | ✅ | 可補一句：75.3 ± 18.9 是正規化後的共同 mean／SD |
| 3 | LUAD、LUSC、HNSC 等 purity < 70% | "low purity (<70%) in cancers resulting from chronic mutagenic exposures, such as lung adenocarcinoma (LUAD), squamous cell carcinoma and head and neck squamous cell carcinoma"（Results、Fig. 1b） | ✅ | 這是 CPE 的值，不是 ABSOLUTE |
| 4 | SKCM 以 ABSOLUTE 計有 40.3% 樣本 < 60% | "While only 1.9% of the samples had purity levels lower than the TGCA's minimum of 60% by IHC, 40.3, 8.9 and 18.5% had low purity according to ABSOLUTE, ESTIMATE and LUMP, respectively."（Results，SKCM 段） | ✅ | — |
| 5 | TCGA 收案門檻原本 80%，後來降到 60% | "at least 80% tumour nuclei … However, this threshold was later reduced to 60%."（Introduction） | ✅ | — |

### 2.2 TCGA PDAC 2017, Cancer Cell

DOI [10.1016/j.ccell.2017.07.007](https://doi.org/10.1016/j.ccell.2017.07.007) → PMID 28810144、PMC5964983 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 6 | ABSOLUTE purity 範圍 9–89%，中位 33%，第一四分位 20% | "ranged from 9–89% (first quartile 20%; median 33%) ( Table S1 )"（Results，Samples 段） | ✅ | — |
| 7 | 74／150 例 purity < 33% | "a 'low-purity' set of 74 samples that had ABSOLUTE purity < 33%"（Results，clustering 段） | ✅ | — |
| 8 | 「不設門檻的 PDAC 中位只有 0.33」 | 原文說刻意收入低 cellularity 樣本："including samples with characteristic low neoplastic cellularity"（Summary）。但 central pathology review < 1% 的 9 例被排除："The 9 samples that were found to have < 1% neoplastic cellularity … were held out" | ⚠️ | 改成「刻意收入低 cellularity 樣本的 PDAC cohort」。不要說「不設門檻」。病理估計的中位更低，只有 18%（"ranged from 0–53% (median 18%)"） |

### 2.3 Dentro 2021, Cell（PCAWG-11）

DOI [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) → PMID 33831375、PMC8054914 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 9 | consensus purity 與 TCGA purity 相關 R = 0.76 | "our consensus has a high correlation with the one reported by them (R = 0.76) ( Figure S1 )"；"them" 指 Aran et al. (2015)（STAR Methods，purity 段） | ⚠️ | 改成「與 Aran 2015 的 TCGA consensus purity（CPE）相關 R = 0.76」 |
| 10 | WGS 中位 depth 約 46× | "based on single-sample reconstruction and a median ∼46× read coverage, provide a conservative lower bound"（Results，Figure 3 段） | ✅ | 收案門檻是 tumor ≥ 30×、normal ≥ 25×（STAR Methods），可一起引用 |
| 11 | arm-level CNA 的 subclonal 比例 13.3%（chRCC）到 53.8%（前列腺癌） | "lowest in chromophobe renal cell cancers (13.3% ± 16.8%) and highest in prostate adenocarcinoma (53.8% ± 32.0%) ( Figure 3 E)"；圖說："arm-level CNAs (E) that were classified as subclonal" | ✅ | 補上：這是各癌別的 mean ± SD。只計 ≥ 5 個事件的樣本 |
| 12 | 1,705 例 nrpcc ≥ 10，只保證 CCF ≥ 30% 的 subclone 可偵測 | "focused on 1,705 genomes where our approach is powered to detect subclones encompassing more than 30% of tumor cells"；推導："Given that a mutation can be detected when it is supported by at least three variant reads, we are theoretically able, in a sample with nrpcc of at least 10, to detect mutations in 30% of tumor cells or more."（STAR Methods） | ✅ | 數字正確。但 30% 是 nrpcc = 10 時的值，不是 PCAWG 的通用下限（見 #49） |
| 13 | 95.1%（1,621／1,705）至少有 1 個 subclone | "One or more subclonal expansions were evident in 1,621 tumors (95.1%)" | ✅ | — |
| 14 | CCF < 30% 的 subclone 約 21% SNV 被漏掉 | "In subclones with a CCF of less than 30%, an average 21% of SNVs are missed. These values reflect SNVs missed in detected subclones, not in subclones that remain undetected" | ✅ | 補上：這是「已偵測 subclone」內的漏失。全部可觀察 subclone 平均漏 14% |
| 15 | 單一樣本約 26% subclonal 突變被誤判為 clonal | "Analysis of five distinct multi-region sequenced primary prostate tumors in PCAWG suggests that, on average, in our single-sample analysis, 44% of variants are missed, and 26% of subclonal mutations appear to be clonal"（Figure S3 段） | ⚠️ | 補上來源限制：只來自 5 個多區域定序的前列腺腫瘤，不是全 cohort。同一分析也報 44% variant 被漏掉 |
| 16 | 1,537 例中 245 例有 cis pair，其中 95.1%（233）符合 clone→subclone | "Of 1,537 tumors with sufficient power and at least one phaseable pair in the correct context, 245 show discordant in cis SNVs pairs … the vast majority of these samples (233, 95.1%) show pairs corroborating the expected clone-subclone relationship." | ✅ | — |
| 17 | 995 例中 51 例有 trans pair | "Of 995 powered tumors, 51 carry discordant in trans SNVs pairs" | ✅ | — |
| 18 | sibling 是 parent-child 的 3.11 倍（95% CI 1.71–7.50） | "two subclones are 3.11-fold more likely to have sibling than parent-child relationships (bootstrapped 95% confidence interval [1.71; 7.50]; Figure 4 D)" | ✅ | 補上：只在 linear 與 branching 偵測力相近的子集計算 |
| 19 | PhylogicSim500：500 個樣本，CN 從 PCAWG 抽；SimClone1000：965 個樣本、網格設計 | "PhylogicSim500, contained 500 samples, where the copy number profiles were sampled from the PCAWG samples"；"SimClone1000, contained 965 samples and used a grid design to cover the collection of scenarios encountered in the PCAWG samples" | ✅ | — |
| 20 | 全文沒有討論 mutation loss 頻率（未查到） | 全文只用模擬估 infinite sites violation 的下限，用來控制 phasing 分析："We opted for a simulation approach to establish a lower bound estimate of the expected number of such violations in any given sample."（STAR Methods）。沒有報 loss 頻率 | ✅ | 可改成「只估 parallel mutation 的下限，沒有報 loss 頻率」 |

### 2.4 Gerstung 2020, Nature（PCAWG，MutationTimeR）

DOI [10.1038/s41586-019-1907-7](https://doi.org/10.1038/s41586-019-1907-7) → PMID 32025013、PMC7054212 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 21 | 2,116 例有可定時的 gain；molecular time 中位 0.60（IQR 0.10–0.87） | "we applied this analysis to the 2,116 samples with copy number gains suitable for timing … (median molecular time 0.60, interquartile range (IQR) 0.10–0.87)"（Timing patterns of copy number gains 段） | ✅ | — |
| 22 | arm-level gain 有 80–90% 只讓 allele-specific CN 加 1 | "Because most arm-level gains increment the allele-specific copy number by 1 (80–90%; Fig. 1g ), it seems that these gains arise through mis-segregation of single copies during anaphase." | ✅ | — |
| 23 | 57%（468／815）near-diploid 腫瘤的 gain 同步發生 | "occurring in 57% (468 out of 815) of informative near-diploid tumours, 61% more frequently than expected by chance" | ✅ | — |
| 24 | 4,700 萬點突變中 22% early clonal（multiplicity > 1）、7% late clonal、53% 無法定時、17% subclonal | "Out of the 47 million point mutations in 2,583 unique samples, 22% were early clonal, 7% late clonal, 53% unspecified clonal and 17% subclonal (Fig. 2a )." | ⚠️ | 「53% 無法定時」改成「53% clonal 但無法區分 early／late（unspecified clonal）」。分母是 2,583 個樣本。「multiplicity > 1」是 early clonal 在 gain 區段的操作意義，原文這句沒有寫，要標〔推論〕 |

### 2.5 Sivakumar 2021, Genetics

DOI [10.1093/genetics/iyaa021](https://doi.org/10.1093/genetics/iyaa021) → PMID 33683368、PMC8045738 ✅（PMC 無正文，讀 OUP 期刊頁）。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 25 | TCGA 11,074 對腫瘤-正常，33 種癌 | "we analyzed 11,074 tumor–normal pairs across 33 tumor sites in the TCGA cohort" | ✅ | — |
| 26 | 94% 腫瘤有 allelic imbalance，基因組中位負擔 32% | "Our method identified at least one AI event in 10,411 cases (94%)"；"with a median genomic AI burden … of 32%" | ✅ | — |
| 27 | 5,222 例（約 47%）共有 20,454 個 arm-level cnLOH | "Our methods identified 20,454 cnLOH arm-level events across 5,222 cases in TCGA (Supplementary Table S1)." | ✅ | 47% 是自算的（5,222／11,074 = 47.2%），要標〔計算〕。arm-level 定義是 "spanning more than 70% of the chromosome arm" |
| 28 | 17p cnLOH：LGG 21.6%、ESCA 22%、LUSC 20.1%、OV 18.5% | "LGG tumors showed a pronounced presence of cnLOH on 17p (21.6% of tumors"；"prevalent in ESCA (22%), LUSC (20.1%), OV (18.5%), and HNSC tumors (17.8%)" | ✅ | — |
| 29 | 第 3 節：「cnLOH 在 C2 是 subclonal → 約 47% TCGA 腫瘤有 arm-level cnLOH → 在範圍內」 | 原文沒有區分 clonal 與 subclonal。只在 Discussion 說目標是 "identifying large SCNAs of low mutant cell fractions" | ⚠️ | 47% 只能支持「cnLOH 常見」。要支持「subclonal cnLOH」，改引 Alleloscope SU008（#43） |

### 2.6 Ciani 2022, Cell Systems

DOI [10.1016/j.cels.2021.10.001](https://doi.org/10.1016/j.cels.2021.10.001) → PMID 34731645、PMC8856743 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 30 | TCGA 4,950 例、27 種癌；CN-LOH 負擔中位 2%（IQR 0–9%）；9.2% 看似 wild-type 的基因其實是 CN-LOH | "an overall pan-cancer median CN-LOH burden per sample of 2% (IQR [0%, 9%])"；"9.2% of wild-type gene calls according to conventional methods … are CN-LOH (2-0)" | ✅ | 補上：4,950 例是從 8,183 例中挑出的高 purity 樣本（"pan-cancer median of 69%, interquartile range [IQR] [54% and 82%]"） |

### 2.7 Griffith 2015, Cell Systems（AML31）

DOI [10.1016/j.cels.2015.08.015](https://doi.org/10.1016/j.cels.2015.08.015) → PMID 26645048、PMC4669575 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 31 | primary WGS 312× | "using multiple independent libraries to 312× and 121× coverage, respectively" | ✅ | — |
| 32 | 30× 只找到 4／6 個 cluster；第 5 個要約 200× 才穩定出現 | "At 30× depth, SciClone detected only four clusters … we did not reliably detect the fifth cluster until 200× coverage" | ✅ | — |
| 33 | 6 個全部要約 850× | "To resolve all six clusters, ~850× coverage depth in the primary tumor, and ~310× depth in the relapse was required."；同段："we downsampled all variants from the platinum list to values between 10× and the maximum coverage available (1,640× for primary …). VAFs were calculated for all sites, independently of whether a site could conceivably be called" | ⚠️ | 850× 是對已驗證的 platinum variant 做 down-sampling 的深度（WGS＋capture 合併，上限 1,640×），不是 WGS 深度。VAF 也不經 caller。這個 primary 的 purity 是 90.7%（"tumor cell purity of primary and relapse tumors as 90.7% and 36.2%"）。純度這麼高仍需 850×，用來支持「低 CCF 難偵測」反而更強 |
| 34 | TP53 在 primary VAF 約 0.01%，復發時升到 17.65% | "only 0.01% VAF at day 0, its proportion increased post-chemotherapy, with a VAF of 6.84% by day 187 and 17.65% by day 334"；復發是 day 505："collected at days 0 (primary tumor), 14, 34, 69, 187, 334, and 505 (relapse)" | ⚠️ | 改成「化療後 day 334 升到 17.65%」。這是 targeted amplicon 的時間序列，不是復發樣本 |
| 35 | 作者建議 subclonal 推論用 500–1,000×；第 3 節「Griffith 建議 200–300×」 | "Plan for 500–1,000× coverage or more if detailed inference of subclonal populations is important."；"A suitable intermediate-term compromise may be to increase the standard depth of tumor WGS to at least 200–300×" | ✅ | 200–300× 是「折衷」，目的是找 sub-10% VAF 的 variant，不是 subclonal 推論的建議值 |

### 2.8 SMC-Het：Salcedo 2025、Salcedo 2020、BAMSurgeon

Salcedo 2025：DOI [10.1038/s41587-024-02250-y](https://doi.org/10.1038/s41587-024-02250-y) → PMID 38862616、PMC11994449 ✅。PubMed 出版日 2024-06-11（online），04 寫的卷期 43:581–592（2025）是印刷版。兩種年份都對，報告中擇一並寫 DOI。
Salcedo 2020：DOI [10.1038/s41587-019-0364-z](https://doi.org/10.1038/s41587-019-0364-z) → PMID 31919445、PMC6956735 ✅。
Ewing 2015：DOI [10.1038/nmeth.3407](https://doi.org/10.1038/nmeth.3407) → PMID 25984700、PMC4856034 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 36 | 51 棵樹：25 棵來自 PCAWG，16 棵來自文獻，10 棵是 PD4120 邊界案例；titration 8×–128× | "25 of these phylogenies were based on manually curated tumors from the … (PCAWG) study, while 16 were based on non-PCAWG tumors … The remaining ten were designed as variations of a single breast tumor"；"10 were special theoretical cases based on the highly curated PD4120"；"a five-tumor titration series at 8×, 16×, 32×, 64× and 128× coverage" | ✅ | — |
| 37 | NRPCC 解釋 sc2A 19.8% 變異；建議 NRPCC ≥ 32；subclonal gain 25／48 被 Battenberg 漏掉 | "NRPCC … explained 19.8% of the variance across tumors"；"a clear benefit to tumor sequencing to an NRPCC of at least 32"；"7 of 68 subclonal losses and 25 of 48 subclonal gains were entirely missed and six more were misestimated" | ✅ | 可一起引用 subclonal loss 7／68 |
| 38 | 「BAMSurgeon（Ewing 2015）；SMC-Het：用 GIAB HG002 300× 真實 read，先定相……除了 deletion 以外，子 clone 帶有父 clone 的突變」 | Salcedo 2025 Methods："aligning a high-depth (300×) Illumina paired-end publicly available BAM file (Genome in a Bottle GM24385)"；"thus, except for deletion events, a child subclone would contain its parent's mutations"。Ewing 2015 的示範資料是另一株："we took the sequence of the HCC1143 BL cell line and created two separate synthetic tumor-normal pairs" | ⚠️ | HG002（GM24385）300× 是 SMC-Het（Salcedo 2025）的設定，不是 Ewing 2015。Ewing 2015 用 HCC1143 BL。「SMC-Het 也模擬了 deletion 造成的遺失」是從括號句推得，要標〔推論〕 |
| 39 | Salcedo 2020：跑 580 個重建，改變 depth、癌別與 caller | "We benchmark 580 tumor reconstructions, varying tumor read-depth, tumour type, and somatic variant detection."（Abstract） | ✅ | 580 是「腫瘤×depth×CNA×SNV caller×重建演算法」的組合數，不是 580 個獨立腫瘤 |

### 2.9 04 末列 6 篇「DOI 未確認」

Kuipers：[10.1101/gr.220707.117](https://doi.org/10.1101/gr.220707.117) → PMID 29030470、PMC5668945 ✅。
SCARLET：[10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001) → PMID 32864481、PMC7451135 ✅。
CHISEL：[10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6) → PMID 32879467、PMC9876616 ✅（39(2):207–214）。
Alleloscope：[10.1038/s41587-021-00911-w](https://doi.org/10.1038/s41587-021-00911-w) → PMID 34017141、PMC9127226 ✅。
Nik-Zainal：[10.1016/j.cell.2012.04.023](https://doi.org/10.1016/j.cell.2012.04.023) → PMID 22608083、PMC3428864 ✅。
Marass：[10.1214/16-AOAS986](https://doi.org/10.1214/16-AOAS986) → 302 轉到 Project Euclid "A phylogenetic latent feature model for clonal deconvolution"（AoAS 10(4)）✅。不在 PubMed。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 40 | Kuipers：12 個資料集中 11 個有同位點重複突變；7 例有突變遺失，其中 5 個位點沒有大段 deletion | "for 11 of 12 single-cell sequencing data sets … Seven cases involved the loss of earlier mutations, five of which occurred at sites unaffected by large-scale genomic deletions."（Abstract） | ✅ | 補上：多數是 targeted panel 單細胞資料 |
| 41 | SCARLET：轉移性大腸癌（141 primary＋45 metastasis）；FHIT、LRP1B、LINGO2 三個 loss，各有 read depth 下降支持 | "targeted sequencing of 1000 genes in 141 cells from a primary colon tumor and 45 cells from a matched liver metastasis"；"three mutation losses: in genes FHIT, LRP1B, and LINGO2. Each of these losses is supported by a significant decrease in read depth" | ✅ | 補上：只有 1 位病人（CRC2），36 個 SNV |
| 42 | CHISEL：2 位乳癌病人、約 2,000 個細胞；找到 total CN 看不到的 cnLOH、mirrored-subclonal CNA，涉及 TP53、BRCA2、PTEN | "10 single-cell datasets from 2 breast cancer patients, each dataset containing ≈ 2 000 cells"；cnLOH 基因："PTEN on chromosome 10q, BRCA2 and RB1 on chromosome 13, and MAP2K4 on chromosome 17p"；"CHISEL identified most of these copy-neutral LOHs to be clonal" | ⚠️ | 細胞數改成「10 個資料集，每個約 2,000 個細胞」（合計約 2 萬）。這些 cnLOH 大多是 clonal，不能當 subclonal cnLOH 的證據。TP53 是「17p LOH 早於 WGD」的 timing 論述，不是 cnLOH 基因清單 |
| 43 | Alleloscope：P5931 chr7 MMm／Mmm；P6198 chr9 7 種組合；sensitivity 0.86–0.97、specificity 0.97–1.00；SU008 chr4 cnLOH 只在 clone-2；P6198 cnLOH 全部以 linked-read 驗證 | "The chromosome 7 amplification exhibits two mirrored subclones with allelic configurations MMm and Mmm."；"the region on chromosome 9 of P6198 … reveals 7 subclones"；Table 1 linked-read：sensitivity 0.8638–0.9671、specificity 0.9666–0.9986；"a subclone in SU008 marked by a copy-neutral LOH event on chr4a"；"All copy neutral LOH events identified by Alleloscope in this sample (chr5, chr11, chr16) are validated by matched linked-read WGS" | ✅ | 小修：P6198 的 7 群包含 1 群 normal cell；SU008 是 chr4a，不是整條 chr4 |
| 44 | Nik-Zainal：21 例乳癌 WGS，multiplicity 定時法的早期示範 | "we can estimate the timing of the duplication event by comparing the proportion of mutations at ploidy 1 and ploidy 2"；"Among the 20 breast genomes sequenced to 30- to 40-fold depth, 16 had informative genomes for timing chromosomal gains" | ✅ | 可補：PD4120a 定序到 188×，是 SMC-Het 10 棵邊界樹的來源 |
| 45 | Marass 2016：「受控生物資料」（單細胞稀釋的癌細胞株與正常株混合）；平台 exome | arXiv 版：4 株 Horizon 癌細胞株（HD124、HD212、HD249、HD659）先單細胞稀釋，再與 1 株正常株（HG00131）依已知比例混成 14 個 mixture。exome 只用來取得 genotype；allele fraction 用 targeted sequencing 量測，最終 82 個突變、中位 17,260×。樹是用不相關細胞株的 heterozygous variant 人工組成 | ⚠️ | 平台改成「exome 選位點＋deep targeted sequencing（中位 17,260×）」。真值是「人工 phylogeny」，不是真實演化樹。來源是 arXiv 1604.01715 的 ar5iv 摘錄，期刊版正文未直接讀到 |

### 2.10 其他實體資料與 single-cell 主張

Farahani：[10.1038/s41598-017-13338-8](https://doi.org/10.1038/s41598-017-13338-8) → PMID 29044127、PMC5647443 ✅。
Salehi：[10.1038/s41586-021-03648-3](https://doi.org/10.1038/s41586-021-03648-3) → PMID 34163070、PMC8396073 ✅。
Minussi：[10.1038/s41586-021-03357-x](https://doi.org/10.1038/s41586-021-03357-x) → PMID 33762732、PMC8049101 ✅。

| # | 04 原句 | 原文證據（位置） | 判定 | 修正建議 |
|---|---|---|---|---|
| 46 | Farahani：比例 0.9／0.1 到 0.1／0.9，每組 14 個樣本；184-hTERT-L2＋HCT116、DAH55＋DAH56；PDX SA494；MiSeq amplicon 中位 5,488× 與 11,754×；ENA PRJEB18801 | Table 2 每個比例（0/1、0.1/0.9、0.25、0.5、0.75、0.9、1/0）各 2 個 mixture ID，共 14 個；"a median coverage of 5488 and 11754 reads for Experiments 1 and 2"；"The cell lines TOV3133D and TOV3133G will be referred to as DAH55 and DAH56"；"available at ENA … under accession PRJEB18801" | ✅ | 補上：14 個樣本含純株（0/1、1/0）。只測 144 個 target SNV 位點 |
| 47 | Salehi：DLP+ 時間序列 42,000 個細胞基因組；TNBC PDX 做實驗強制的 clone 競爭；EGA 受控 | "we generated 42,000 genomes from multi-year time series single cell whole genome sequencing (scWGS) of breast epithelium and primary triple negative breast cancer (TNBC) patient derived xenografts"；"inferred fitness coefficients … accurately forecast experimentally enforced clonal competition dynamics"；"European Genome-Phenome archive … EGAS00001004448" | ✅ | 補上：42,000 個基因組也包含乳腺上皮細胞株，每個細胞約 0.022× |
| 48 | Minussi：16,178 個細胞，8 例 TNBC＋4 株細胞株；每個腫瘤 7–22 個 subclone，歸成 3–5 個 superclone | "copy number analysis of 16,178 single cells from 8 triple-negative breast cancers (TNBCs) and 4 cell lines … a large milieu of subclones (7–22) that are organized into a few (3–5) major superclones" | ✅ | 數字正確，但用法見 #50 |

### 2.11 04 第 3 節由上述數字推得的判定

| # | 04 原句 | 原文依據 | 判定 | 修正建議 |
|---|---|---|---|---|
| 49 | 「C3 CCF 0.10……PCAWG 只保證 CCF ≥ 0.30……生物上存在，但在 200× 低於可靠偵測下限」 | Dentro 的規則是 "at least three variant reads"，nrpcc 公式為 nrpcc = ρ·cov／(ρψ_t＋(1−ρ)ψ_n)。30% 是 nrpcc = 10 時的值 | ⚠️ | 我們的 nrpcc ≈ 40（04 已算），C3 期望 alt read ≈ 40 × 0.10 = 4 條，高於 3 條規則。依 PCAWG 規則，最低可偵測 CCF ≈ 3／40 = 0.075。所以應改成「剛好高於 PCAWG 理論門檻，但在 SMC-Het（NRPCC ≥ 32 才有好表現）與 AML31（850×）標準下屬邊緣」。Poisson(4) 下 ≥ 3 條的機率約 0.76，約 1／4 的 C3 SNV 仍會漏掉〔推論〕 |
| 50 | 「clone 數與形狀：4 個 clone……Minussi 7–22 個 subclone → 在範圍內」 | Minussi 的 subclone 是 single-cell CN 分群。PCAWG bulk 的數字："only 11% of subclones (265 of 2,329) were annotated with a driver"，分母 2,329 個 subclone 分布在 1,621 個有 subclone 的樣本 | ⚠️ | Minussi 不能直接比 bulk SNV clone 數。單一 bulk 樣本的 PCAWG 平均每個有 subclone 的腫瘤約 1.4 個 subclone（2,329／1,621，〔計算〕）。我們的設計有 3 個 subclone，偏多。要寫成「真實存在，但高於 PCAWG 單樣本可偵測的平均」 |

註：⚠️ 共 12 條：#8、#9、#15、#24、#29、#33、#34、#38、#42、#45、#49、#50。

## 3. 補充：對 4 個主題更有力的數字

### 3.1 突變遺失頻率

- **SCARLET（CRC2）：36 個 SNV 中有 3 個 loss（約 8%）。** "The authors identified 36 single-nucleotide variants (SNVs)"；"The SCARLET tree contains three mutation losses"。3／36 是〔計算〕。只有 1 位病人、targeted panel。
- **Kuipers（Gawad ALL 6 位病人）：5 位有 lost mutation，都不在 bulk 偵測到的 LOH 區。** "For all samples apart from patient 5, the recurrent mutation is a lost mutation."；"None of the five lost mutations we identified appeared in any of the LOH regions of the respective patient"。這支持「小段 deletion 也會造成 loss」。
- **SMC-Het 設計本身就讓 deletion 移除父 clone 突變。** 引文見 #38。這可以回應「模擬加入 loss 不合理」的質疑：業界 benchmark 也這樣做〔推論〕。
- **SMC-Het：subclonal deletion 會讓演算法低估 SNV 的 CP。** "subclonal losses on the mutation-bearing DNA copy reduced VAF, causing many algorithms to underestimate the CP of these SNVs"（Salcedo 2025）。

### 3.2 subclonal cnLOH

- **最直接的證據是 Alleloscope SU008。** chr4a cnLOH 只在 clone-2（#43）。
- **CHISEL 的 cnLOH 大多是 clonal**（#42），不要拿來支持 subclonal。
- **Sivakumar、Ciani 的 TCGA 數字都不分 clonal／subclonal。** 只能支持「cnLOH 常見」。Ciani：高 allele-specific ploidy 腫瘤的 CN-LOH 負擔中位 14%（IQR 8–22%），30% 這類樣本有 ≥ 20% 基因組是 CN-LOH："30% of the high asP samples have at least 20% of the genome with CN-LOH signal"。
- 本次沒有找到 PCAWG 對 subclonal cnLOH 比例的正文數字（未查到）。

### 3.3 低 CCF subclone 偵測下限

- **PCAWG 的門檻規則是「≥ 3 條 variant read」。** 最低可偵測 CCF ≈ 3／nrpcc（引文見 #12、#49）。這比「CCF ≥ 0.30」更通用。可直接套到任何 depth／purity 設定〔原文規則＋推論〕。
- **SMC-Het：subclonal gain 有一半以上（25／48）被 CN caller 完全漏掉，subclonal loss 7／68。** 偵測率受 NRPCC 強烈影響："The accuracy of subclonal CNA detection was strongly influenced by tumor NRPCC"。
- **AML31：purity 90.7% 的樣本仍需約 850× 的 variant 深度才分出全部 6 個 cluster**（#33）。
- **AML31：一般 WGS 深度對低 VAF variant 幾乎無效。** "At 50× coverage, 95% of SNVs with a VAF of 15% or higher could be consistently detected, but only 10% of SNVs with less than 15% VAF could be consistently found."
- **PCAWG：黑色素瘤只有一半樣本偵測到 subclone。** "except cutaneous melanoma, where subclones were detectable by our approach in only 31 of 62 samples"。

### 3.4 purity 分佈

- **PCAWG 作者自述的典型值：depth 50、purity 80%。** "for an average read depth of 50 and a purity of 80%, which are typical values seen in PCAWG datasets"（Dentro 2021 Methods，PhyloWGS 段）。這是方法段的說法，不是分佈統計。
- **Ciani 篩選後的 TCGA WES：purity 中位 69%（IQR 54–82%）。** 引文見 #30。
- **PDAC 病理估計中位只有 18%（0–53%）。** 比 ABSOLUTE 的 33% 更低（#8）。
- **AML31 的 relapse purity 是 36.2%。** 可當「單一病人不同時間點 purity 差很大」的例子。

## 4. 參考文獻

查核來源：PubMed（ID converter 與 metadata）、Europe PMC／NCBI PMC 全文、OUP 期刊頁、arXiv。

1. Aran D, Sirota M, Butte AJ. Systematic pan-cancer analysis of tumour purity. *Nat Commun* 6:8971 (2015). [10.1038/ncomms9971](https://doi.org/10.1038/ncomms9971)．PMID 26634437．PMC4671203
2. Cancer Genome Atlas Research Network. Integrated genomic characterization of pancreatic ductal adenocarcinoma. *Cancer Cell* 32:185–203 (2017). [10.1016/j.ccell.2017.07.007](https://doi.org/10.1016/j.ccell.2017.07.007)．PMID 28810144．PMC5964983
3. Dentro SC et al. Characterizing genetic intra-tumor heterogeneity across 2,658 human cancer genomes. *Cell* 184:2239–2254 (2021). [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009)．PMID 33831375．PMC8054914
4. Gerstung M et al. The evolutionary history of 2,658 cancers. *Nature* 578:122–128 (2020). [10.1038/s41586-019-1907-7](https://doi.org/10.1038/s41586-019-1907-7)．PMID 32025013．PMC7054212
5. Sivakumar S et al. Pan cancer patterns of allelic imbalance from chromosomal alterations in 33 tumor types. *Genetics* 217:iyaa021 (2021). [10.1093/genetics/iyaa021](https://doi.org/10.1093/genetics/iyaa021)．PMID 33683368．PMC8045738
6. Ciani Y et al. Allele-specific genomic data elucidate the role of somatic gain and copy-number neutral loss of heterozygosity in cancer. *Cell Syst* 13:183–193 (2022). [10.1016/j.cels.2021.10.001](https://doi.org/10.1016/j.cels.2021.10.001)．PMID 34731645．PMC8856743
7. Griffith M et al. Optimizing cancer genome sequencing and analysis. *Cell Syst* 1:210–223 (2015). [10.1016/j.cels.2015.08.015](https://doi.org/10.1016/j.cels.2015.08.015)．PMID 26645048．PMC4669575
8. Salcedo A et al. Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction. *Nat Biotechnol* 43:581–592 (2025; online 2024-06-11). [10.1038/s41587-024-02250-y](https://doi.org/10.1038/s41587-024-02250-y)．PMID 38862616．PMC11994449
9. Salcedo A et al. A community effort to create standards for evaluating tumor subclonal reconstruction. *Nat Biotechnol* 38:97–107 (2020). [10.1038/s41587-019-0364-z](https://doi.org/10.1038/s41587-019-0364-z)．PMID 31919445．PMC6956735
10. Ewing AD et al. Combining tumor genome simulation with crowdsourcing to benchmark somatic single-nucleotide-variant detection. *Nat Methods* 12:623–630 (2015). [10.1038/nmeth.3407](https://doi.org/10.1038/nmeth.3407)．PMID 25984700．PMC4856034
11. Kuipers J, Jahn K, Raphael BJ, Beerenwinkel N. Single-cell sequencing data reveal widespread recurrence and loss of mutational hits in the life histories of tumors. *Genome Res* 27:1885–1894 (2017). [10.1101/gr.220707.117](https://doi.org/10.1101/gr.220707.117)．PMID 29030470．PMC5668945
12. Satas G, Zaccaria S, Mon G, Raphael BJ. SCARLET: single-cell tumor phylogeny inference with copy-number constrained mutation losses. *Cell Syst* 10:323–332 (2020). [10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001)．PMID 32864481．PMC7451135
13. Zaccaria S, Raphael BJ. Characterizing allele- and haplotype-specific copy numbers in single cells with CHISEL. *Nat Biotechnol* 39:207–214 (2021). [10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6)．PMID 32879467．PMC9876616
14. Wu CY et al. Integrative single-cell analysis of allele-specific copy number alterations and chromatin accessibility in cancer. *Nat Biotechnol* 39:1259–1269 (2021). [10.1038/s41587-021-00911-w](https://doi.org/10.1038/s41587-021-00911-w)．PMID 34017141．PMC9127226
15. Nik-Zainal S et al. The life history of 21 breast cancers. *Cell* 149:994–1007 (2012). [10.1016/j.cell.2012.04.023](https://doi.org/10.1016/j.cell.2012.04.023)．PMID 22608083．PMC3428864
16. Marass F, Mouliere F, Yuan K, Rosenfeld N, Markowetz F. A phylogenetic latent feature model for clonal deconvolution. *Ann Appl Stat* 10:2377–2404 (2016). [10.1214/16-AOAS986](https://doi.org/10.1214/16-AOAS986)．arXiv [1604.01715](https://arxiv.org/abs/1604.01715)
17. Farahani H et al. Engineered in-vitro cell line mixtures and robust evaluation of computational methods for clonal decomposition and longitudinal dynamics in cancer. *Sci Rep* 7:13467 (2017). [10.1038/s41598-017-13338-8](https://doi.org/10.1038/s41598-017-13338-8)．PMID 29044127．PMC5647443
18. Salehi S et al. Clonal fitness inferred from time-series modelling of single-cell cancer genomes. *Nature* 595:585–590 (2021). [10.1038/s41586-021-03648-3](https://doi.org/10.1038/s41586-021-03648-3)．PMID 34163070．PMC8396073
19. Minussi DC et al. Breast tumours maintain a reservoir of subclonal diversity during expansion. *Nature* 592:302–308 (2021). [10.1038/s41586-021-03357-x](https://doi.org/10.1038/s41586-021-03357-x)．PMID 33762732．PMC8049101
