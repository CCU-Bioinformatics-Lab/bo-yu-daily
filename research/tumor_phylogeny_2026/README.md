# 腫瘤演化樹文獻調查：single cell × long read × haplotype

調查截止：2026-10-15，文件語言：繁體中文。近期範圍採 **2021–2026**；online publication 與卷期年份不同時並列，preprint 與正式版不重複計數。

> **2026-10-16 補充**：本調查的選文標準是「論文裡有樹」，13 篇中多數是建樹只是手段的應用研究，真正的 phylogeny 方法論文只有 MEDICC2。以「推論 topology 為主要貢獻」重新搜尋的方法調查見 [methods_survey/README.md](methods_survey/README.md)（46 個方法）。

## 先看結論與閱讀路線

本調查整理 **13 篇不同論文**：A 類 5 篇病人 single-cell 遺傳演化樹；B 類主選 5 篇 long-read／linked-read／haplotype 特徵參與演化推理的研究，另附 3 篇重要比較與延伸文獻。每篇有獨立目錄、PDF、全文文字與閱讀筆記。

**B 類主選的技術並不全是實測 long reads**：B01、B04、B06 使用 ONT；B02 是 10x linked short reads；B07 是從短讀 scRNA-seq 做 population-based haplotype phasing。B04 提供局部突變順序與候選 topology 排除，B06 是 sample tree；均不冒充完整 deconvolved clone tree。若把第二類限縮為「5 篇均以實測 ONT/PacBio 直接重建完整 clone tree」，目前選集不符合這個更嚴條件。

最接近使用者優先交集的是 [B04 肺癌 phasing](papers/B04_lung_longread_phasing_2022/README.md)：同一研究有真實病人 long reads、mutation-pair timing、single-cell DNA 驗證。**直接利用 long reads 選線性／分支樹的 S14，並不是做 scDNA 的 S8/S20**，所以仍未取得「同一病人、獨立 scDNA 完整參考樹、long-read 全樹推理」的完整閉環。

建議先讀 B04 → B01 → A04 → A01 → B07，再看 [本 repo 改進方案](REPO_IMPROVEMENTS.md)。

## A：真實病人 single-cell 支持的演化樹，5 篇

此類不要求使用 long reads。這裡的「答案」是資料與模型支持的 **reference phylogeny**，不是觀察每次細胞分裂得到的唯一歷史。

| ID／年份 | 論文與筆記 | 實際材料與樹 | 與本 repo 最相關 |
|---|---|---|---|
| A01／2025 | [Tracking clonal evolution during treatment in ovarian cancer using cell-free DNA](papers/A01_ovarian_cfDNA_2025/README.md) | 24 位病人；DLP+ scWGS、allele-specific CN、MEDICC2；cfDNA 追蹤 | CN／VAF／CCF 對應；clone fraction 與 CCF 分母；longitudinal 驗證 |
| A02／online 2024、卷期 2025 | [SPRINTER](papers/A02_sprinter_2025/README.md) | 真實 NSCLC 病人多部位 scWGS；SNV topology 與其上的 CNA 歷史 | cell cycle／WGD／CN 誤差；固定 topology 的 CNA 不能當獨立驗證 |
| A03／2023 | [Application of high-throughput single-nucleus DNA sequencing in pancreatic cancer](papers/A03_pancreatic_snDNA_2023/README.md) | 16 位病人、34 樣本；snDNA CNV 與 SNV；轉移 phylogeny | 病人多部位 clone 參考；混合與 sampling bias |
| A04／2024 | [Single-cell multiomics analysis reveals dynamic clonal evolution and targetable phenotypes in AML with complex karyotype](papers/A04_aml_strandseq_2024/README.md) | 病人 Strand-seq/scTRIP、SV/CN/LOH；另含 PDX，分開標示 | allele-specific CN/LOH 與 SV 約束；Strand-seq 是短讀技術 |
| A05／2024 | [Multiomic single cell sequencing identifies stemlike nature of mixed phenotype acute leukemia](papers/A05_mpal_multiome_2024/README.md) | 真實 MPAL 病人 scDNA；SCITE genetic tree 與 phenotype 對照 | SNV lineage benchmark；genotype 與 transcriptomic state 分離 |

詳見 [A 類綜整、資料 accession 與 PDF 校驗](A_SUMMARY.md)。

## B：long-read／long-range／haplotype 特徵參與演化推理，主選 5 篇

| ID／年份 | 論文與筆記 | 特徵如何進入推理 | 關鍵邊界 |
|---|---|---|---|
| B01／2026 | [Long-read sequencing of single cell-derived melanoma sublines reveals divergent and parallel genomic and epigenomic evolutionary trajectories](papers/B01_melanoma_longread_2026/README.md) | ONT SNV 建 ScisTree；SV/CNA/DMR 由 TreeHarmonizer 放到樹上 | 小鼠細胞株的 23 個 single-cell-derived cultures；不是病人、不是直接 scDNA-seq；TreeHarmonizer 不重新推 topology |
| B02／2021 | [Co-evolution of tumor and immune cells during progression of multiple myeloma](papers/B02_myeloma_linkedread_2021/README.md) | linked-read somatic haplotypes 對 clone 共存／分支提供限制；另有 scRNA | linked reads 並非 ONT/PacBio；沒有獨立 scDNA 完整真樹 |
| B04／2022 | [Phasing analysis of lung cancer genomes using a long read sequencer](papers/B04_lung_longread_phasing_2022/README.md) | ONT 同 read mutation pairs 決定局部先後；S14 排除一個候選 topology | 有病人 scDNA 驗證，但不同病例與 coverage 限制阻止完整真樹宣稱 |
| B06／2025 | [Multisite long-read sequencing reveals the early contributions of somatic structural variations to HBV-related hepatocellular carcinoma tumorigenesis](papers/B06_hcc_multisite_longread_2025/README.md) | ONT SV breakpoint presence matrix → neighbor-joining sample phylogeny；另估 SV CCF | 5 病人 42 樣本，無 single-cell；sample tree 不等於 clone tree |
| B07／online 2022、卷期 2023 | [Numbat: Haplotype-aware analysis of somatic copy number variations from single-cell transcriptomes](papers/B07_numbat_2022/README.md) | population phased haplotype + allele counts + expression → CNV → iterative clonal phylogeny | 可移植的 haplotype 特徵；原研究是短讀 scRNA，不是實測 long reads；RNA 等位偏差不能照搬 DNA likelihood |

主選同時覆蓋「真正 long reads 直接提供的遺傳訊號」、「長分子 linked-read 約束」與「haplotype-specific CN/LOH 如何入樹」。三者分層計數，不能合寫成 5 篇 ONT clone-tree 方法。

## 補充的 3 篇與近似命中

| ID | 論文 | 納入原因／不計入 B 主選的原因 |
|---|---|---|
| B03／2022 | [Single-cell genomic variation induced by mutational processes in cancer](papers/B03_singlecell_mutational_processes_2022/README.md) | single-cell haplotype-specific parallel CN evolution；nanopore 主要作 SV 驗證，不能說 long-read linkage 重建該樹 |
| B05／2022 | [MEDICC2](papers/B05_medicc2_2022/README.md) | allele-specific CN/LOH/WGD event-based phylogeny，支撐 A01/A02；本身不是 long-read 專用方法 |
| B08／2023 | [Intratumoral Heterogeneity and Clonal Evolution Induced by HPV Integration](papers/B08_hpv_integration_2023/README.md) | ONT/PacBio 推局部SV molecular history；無法判斷同cell／不同clone，不能當完整clone tree |

[交集查核](INTERSECTION_SUMMARY.md) 記錄是否同一病人、同一樣本、同一資料層；[搜尋與排除紀錄](SEARCH_LOG.md) 保留 LongSom、HATCHet2、ALPACA、Wakhan、Severus 以及 2026 AACR mutation-pair phasing 摘要等線索，說明為何未用它們湊滿完整 clone-tree 論文數量。各篇是否公開程式碼及 GitHub 星星數見 [程式碼與 GitHub 星星數](CODE_AVAILABILITY.md)。

## 基準參考（不在 2021–2026 窗口，不計入篇數）

| ID | 論文 | 用途 |
|---|---|---|
| R01／2016 | [McPherson et al., HGSOC clonal spread](references/R01_mcpherson_hgsoc_2016/README.md) | PhyClone HGSOC 病人 2/3/9 真值樹的來源：single-nucleus targeted PCR＋SCG＋stochastic Dollo。主文 closed access，只讀 supplement 與 tables |

## 關鍵詞入口

| 關鍵詞 | 優先論文 | 對本 repo 的意義 |
|---|---|---|
| single cell／single nucleus | A01–A05、B03、B07 | 逐細胞 genotype/CN 作參考；區分 scDNA、scRNA、培養衍生株 |
| long read／ONT／linked read | B01、B02、B04、B06 | read-level cis/trans、SV breakpoint、候選樹排除 |
| purity／VAF／CCF | A01、B04、B06、B05 | purity 定義、copy-number 校正、clone fraction 與 descendant-inclusive CCF |
| haplotype／phasing／phase set | A04、B02、B04、B07 | PS 內一致性、orientation、phasing uncertainty；HP1 不是全基因組的 clone ID |
| CNV／LOH／copy number／WGD | A01、A02、A04、B03、B05、B07 | multiplicity、平行演化、mutation loss、haplotype-specific CN |

## 檔案、驗證與證據分級

每篇 `papers/<ID>/` 存放 `paper.pdf`、`paper.txt`、`README.md`；B04/B06另附已讀的 `supplement.pdf` 與文字版。頁碼以實體 PDF 頁序為準。B07的主要閱讀PDF是bioRxiv v1，另對照正式全文；B08是作者機構保存的accepted manuscript，其他主要PDF為正式版或修正版。不同版本頁碼不可互換。

`catalog.json` 是選文與分類資料；`manifest.tsv`／`manifest.json` 是本地實檔的 SHA-256、byte size、pdfinfo 頁數、閱讀筆記路徑。可從本目錄執行 `python3 tools/validate_bundle.py --write-manifest` 重新驗證。此檢查只驗證交付檔與連結，不代表重跑論文的科學分析。

研究建議屬 `inferred`；目前程式行為屬 `current`，在 [REPO_IMPROVEMENTS.md](REPO_IMPROVEMENTS.md) 附實作檔定位。lab 術語查核屬 `lab-canonical`。既有 HCC1395 參考樹整理是 `historical` 導覽，不能提升為病人 ground truth。歷史資料庫 `/bip8_disk/boyu114/bip8_disk_boyu_database` 此次不存在，已記錄為 `not-found`。
