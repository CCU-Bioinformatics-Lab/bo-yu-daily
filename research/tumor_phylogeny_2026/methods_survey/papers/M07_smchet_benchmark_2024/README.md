---
paper_id: M07
category: "C1"
category_label: "短讀或未說平台（無 single-cell 真值）"
subtype: "c1_bulk_short_read"
sc_truth_strength: "none"
title: "SMC-Het DREAM: Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction"
year: 2024
doc_type: "benchmark"
material: "simulated"
platform_class: "short_or_unspecified"
platform_detail: ["simulated Illumina WGS (BAMSurgeon on GM24385)"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "simulated_only"
single_cell_tech: []
input_is_single_cell: false
tree_type: ["clone_tree"]
cross_tags: ["simulated_benchmark", "evaluation_metrics"]
keywords_en: ["smc-het", "dream challenge", "bamsurgeon", "battenberg", "mutect", "single-sample bulk", "subclonal reconstruction", "nrpcc", "phylowgs", "dpclust", "simulated tumors", "co-clustering", "ancestor-descendant matrix"]
keywords_zh: ["社群基準測試", "模擬腫瘤", "單樣本", "次克隆重建", "拷貝數"]
summary_zh: "短讀模擬的單樣本 benchmark，比較 31 個方法。"
category_index: "../../../../PAPER_CATEGORIES.md"
---

# M07 SMC-Het DREAM Challenge（Salcedo, Tarabichi et al., Nat Biotechnol 2024/2025）閱讀筆記

閱讀日：2026-10-18。標記：「論文描述」＝主文、Methods 或 supplement 明寫；「推論」＝我的分析。本篇沒有讀參賽方法的程式碼。

## 書目、版本與檔案

- Salcedo A, Tarabichi M, Buchanan A, …, Ellrott K, Van Loo P, Boutros PC. **Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction.** *Nature Biotechnology* 43(4):581–592。DOI [10.1038/s41587-024-02250-y](https://doi.org/10.1038/s41587-024-02250-y)。PMID 38862616，PMCID PMC11994449。
- 日期：Received 2022-04-11；Accepted 2024-04-17；online 2024-06-11；卷期 2025。授權 CC BY 4.0。
- Preprint：bioRxiv [10.1101/2022.06.14.495937](https://doi.org/10.1101/2022.06.14.495937)（沒有下載，沒有比對）。

| 本地檔 | 內容 | 來源 |
|---|---|---|
| `paper.pdf` | **出版社正式版**，27 頁（含 Extended Data） | PMC OA S3 `PMC11994449.1.pdf`（md5 `0ce31079c2304943fdd7ec92103155ec`，與 PMC metadata 一致） |
| `supplement.pdf` | Supplementary Notes 1–3、Supp. Fig. 1–6、Table 4–5，21 頁 | 同上 `41587_2024_2250_MOESM1_ESM.pdf` |
| `supplementary_tables.xlsx` | Supp. Table 1（全部分數）、2（tumor features）、3（entry features） | 同上 `MOESM3_ESM.xlsx`（本次沒有打開） |
| `reporting_summary.pdf` | Nature Reporting Summary | 同上 `MOESM2_ESM.pdf` |
| `paper.txt`、`supplement.txt` | `pdftotext -layout` | — |
| `pmc_fulltext.txt` | PMC 的純文字版正文；圖文混排比 `paper.txt` 乾淨，閱讀主要用它 | PMC OA S3 `PMC11994449.1.txt` |

頁碼：`[p.N]` 指 `paper.pdf` 實體頁；`[S p.N]` 指 `supplement.pdf` 實體頁。

## 一句話定位

這是 **single-sample bulk subclonal reconstruction** 的社群 benchmark：31 個方法、51 個模擬腫瘤、7 個 subchallenge，共 12,061 次執行 [p.1]。它提供三樣可直接借用的東西：**模擬框架、評分程式、帶真值的資料**。PhyClone（2024 才發表）**不在**受測方法中。

## Benchmark 設計（論文描述）

### 模擬腫瘤 [p.3；Methods p.13]

- 51 棵設計樹：25 棵來自 PCAWG 人工建樹、16 棵來自文獻、10 棵是 PD4120 乳癌的 special case（測試演算法假設的邊界）。另有 5 個腫瘤的 titration series（8×、16×、32×、64×、128×）。
- PCAWG 建樹用 DPClust＋Battenberg，以 pigeonhole principle 和 **mutation-to-mutation phasing** 限制可能的 topology；有多個可能時隨機選一棵，並平衡 branching 與 linear [Methods；S p.4]。
- 每個 node 帶：CP、整條染色體的 CN 事件、SNV／SV 數、trinucleotide context。

### BAM 模擬流程 [Methods p.13]

1. 以 GIAB **GM24385（HG002）** 300× Illumina PE BAM 為底，對 hs37d5 比對。
2. 用 PhaseTools 把 reads 定相，phased contig 中位長度約 85 kb。
3. 依「phase × chromosome」切成 sub-BAM，依 CP 與 fractional copy 調整每個 read pool 的深度，以模擬 CNA。
4. 用 BAMSurgeon 在各 read pool spike-in SNV／SV／indel，保留演化順序（除 deletion 外，子 clone 帶有父 clone 的突變）。
5. 合併回 tumor BAM；用 MuTect 呼叫 SNV、Battenberg 呼叫 CNA 與 purity。

**重點（推論）**：模擬時每個突變都放在**特定 haplotype** 的 read pool 上。所以真值裡有「SNV 在哪條 haplotype」的資訊。但 reads 是 short read，參賽者拿到的只有 VCF 和 Battenberg 輸出。

### 參賽者拿到的輸入 [p.3；Methods p.13]

- MuTect SNV VCF（ref／alt counts）。
- Battenberg 輸出：allele-specific CN segment（最多兩個 CN 狀態的混合，也就是 subclonal CN）和 purity／ploidy。
- 排除 X、Y 染色體。
- 參賽者看不到其他任何設計細節。

### 七個 subchallenge 與評分 [p.3；Methods p.13]

| subchallenge | 評估什麼 | 分數 |
|---|---|---|
| sc1A | purity | `1 − |ρ − c|` |
| sc1B | subclone 數 | `(L − d + 1)/(L + 1)`，d＝預測與真值的差（上限 L+1） |
| sc1C | SNV CP 分布 | `1 − EMD`（normalized earth mover's distance） |
| sc2A／sc2B | SNV 分群（hard／soft） | AUPR 與 AJSD 的平均，以「全部一群」和「每個 SNV 一群」兩個極端方法正規化 |
| sc3A／sc3B | phylogeny（hard／soft） | 預測與真值的 **co-clustering、cousin、ancestor–descendant、轉置 ancestor–descendant 四個矩陣**的 Pearson correlation |

- 評分以「完美 SNV call」的真值為準。false negative 被加成一個 CP=0、來自 normal 的 cluster；false positive 在評分前排除 [Methods p.13]。
- 分數在每個 {tumor, subchallenge} 內做 min–max 正規化 [Methods p.13]。**所以分數是相對排名，不是絕對正確率**（推論）。
- 缺少輸出不扣分 [Methods p.13]。

### 執行限制 [p.3]

- 每次執行上限 21 天、≥24 CPU、200 GB RAM。
- 失敗 2,189 次，多數集中在兩個 >100,000 SNV 的腫瘤。
- 主辦方加了 5 個參考方法：random、PCAWG informed brute-force、單一 cluster（VAF mode），以及 SOTA 的 **DPClust 和 PhyloWGS**。

## 主要結果（論文描述）

### 整體排名 [p.3，Table 1]

- **沒有一個方法在所有 subchallenge 都最好。**
- 各項的 top performer：sc1A 是 Object integration、GISL；sc1B 是 GISL、CCube；sc1C 是 PhylogicNDT、GISL；sc2A 是 PhylogicNDT、GISL、FastClone；sc2B 是 PhylogicNDT；sc3A 是 GISL、FastClone；sc3B 是 FastClone。
- sc1A 第一名**只用 CN** 推 purity。

### Phylogeny（sc3）[p.3；S p.10–11 Supp. Fig. 2]

- 只有 **7 個方法**提交了 phylogeny 任務。
- 方法之間辨認 branching 的能力不同，傾向合併或拆分 node 的程度也不同。
- 越靠近 normal 的 node（clonal node 和它的子 node），SNV 的 parent 越容易推對。
- 推錯 parent 時，多半錯到相近的 node。
- 作者結論：single-sample phylogeny 只有 clonal 變異和它的直接後代可靠；更深的結構在不同腫瘤和方法間差異很大。

### 什麼決定準確度 [p.4–5]

- **方法選擇的影響大於腫瘤特徵。** algorithm ID 解釋 19–35% 的分數變異；tumor ID 約 15%；沒有單一腫瘤特徵超過 10%。
- **雜訊模型**：Gaussian 雜訊模型在 sc2A 明顯比 binomial／beta-binomial 差 [p.5]。
- **NRPCC**（number of reads per chromosome copy）是最重要的可控因素：

  ```text
  NRPCC = ρ·d / (ρ·ψ + 2(1 − ρ))      # d=depth，ρ=purity，ψ=tumor ploidy
  ```

  - sc2A 中，NRPCC 解釋 19.8% 的變異。
  - 作者建議 single-sample 至少 **NRPCC ≥ 32**，超過後分數趨於飽和，差異主要來自方法本身。
  - NRPCC 低時，purity 會被高估（低頻 SNV 偵測不到，形成截尾分布）[p.5]。
  - NRPCC 越高，推出的 subclone 數越多；樹越深、真實 subclone 越多，越容易低估 subclone 數。
- WGD 時，方法較容易低估 subclone 數。

### CN 對 CP 估計的影響 [p.7]

- subclonal CNA 區的 SNV clonality 準確度顯著低於 clonal CNA 區。
- **clonal SNV＋subclonal loss**：準確度最差。帶突變的 copy 被刪後 VAF 下降，多數方法**低估** CP。
- **subclonal SNV＋subclonal gain**：多數方法**高估** CP。
- 對 CNA 越穩健的方法，sc1C 和 sc2A 越好。
- **Battenberg 本身的 subclonal CN 偵測**：clonal CNA 幾乎全對；但 68 個 subclonal loss 漏掉 7 個，**48 個 subclonal gain 漏掉 25 個**，另有 6 個估錯。準確度受 NRPCC 影響很大；低 CP subclone 和 SNP 稀少區最容易錯。
- 幾乎所有方法都會高估 subclonal SNV 的 CP，CP 越低、NRPCC 越低越嚴重。

### 其他 [p.7–9]

- **neutral tail**：影響小，主要在 >64× 時增加假的低 VAF subclone；MOBSTER 過濾有幫助。
- **ensemble**：median、WeMe、CICC 等 ensemble 只在 sc1B 勝過最好的單一方法。

### 作者在 Discussion 明寫的缺口 [p.10]

- 需要**系統性的 subclonal CNA benchmark**。
- 「As read lengths increase」：**mutation-to-mutation 和 mutation-to-SNP phasing** 可用來解決不明確的 phylogeny，尤其在高 SNV burden 的腫瘤。
- 沒有評估 balanced SV；受測方法也都沒用 SV。
- 建議用 single-cell WGS 的 pseudo-bulk 當補充真值。

## 資料與程式可取得性 [p.15]

| 項目 | 位置 | 備註 |
|---|---|---|
| 模擬 tumor／normal BAM | EGA **EGAS00001002092** | 本次沒有查存取條件 |
| SNV／SV／CNA／indel calls 與**真值檔** | Synapse [syn2813581](https://www.synapse.org/#!Synapse:syn2813581/files/) | 需要 Synapse 帳號（推論，沒有實際登入確認） |
| spike-in 後的 normal BAM | ENA PRJEB52520 | — |
| 參賽 Docker container | Synapse syn2813581 docker | — |
| Galaxy workflows | [github.com/smc-het-challenge](https://github.com/smc-het-challenge/) | — |
| 評分程式 | [uclahs-cds/tool-SMCHet-scoring](https://github.com/uclahs-cds/tool-SMCHet-scoring)（Python 2.7） | — |
| BAMSurgeon | [adamewing/bamsurgeon](https://github.com/adamewing/bamsurgeon) v1.2 | — |
| PhaseTools | [mateidavid/phase-tools](https://github.com/mateidavid/phase-tools) | — |
| 分數與預測樹的互動頁面 | [mtarabichi.shinyapps.io/smchet_results](https://mtarabichi.shinyapps.io/smchet_results/) | — |

reference 是 **hs37d5（GRCh37）**。本 repo 的 CRAM 是 GRCh38，兩者不能直接混用（推論）。

## 對 PhyClone＋longphase-s 的用途

以下全部為「推論」。C0–C6 名稱依 `plan.md`。

### 1. 評分：sc3 和本 repo 的評估規格幾乎同構

- `evaluation_v1.md` 的「四類 confusion matrix」（same、ancestor、descendant、branch）對應 sc3 的四個矩陣（co-clustering、ancestor–descendant、轉置 ancestor–descendant、cousin）。
- 差別：
  - sc3 用 Pearson correlation 匯總成一個數；本 repo 分開報四類和 AD F-score。
  - sc3B 接受 soft assignment（posterior 機率矩陣）。PhyClone 有 posterior trace，可以算 soft 版本；目前 `evaluation_v1.md` 只評 MAP 樹。
- 建議：在本 repo 的評分程式裡**加一個 sc3A／sc3B 相容輸出**。這樣 PhyClone 的結果可以直接放進 SMC-Het 的排名裡比較，不必重新定義指標。
- 注意 min–max 正規化：SMC-Het 分數是相對值，要和 SMC-Het 排名比，必須用原始分數或同一批方法一起正規化。

### 2. 基線：PhyClone 從沒在這套資料上被測過

- 最便宜的第一個實驗：用 Synapse 的 VCF＋Battenberg 輸出，轉成 PhyClone 的 TSV（`ref_counts, alt_counts, major_cn, minor_cn, normal_cn, tumour_content`），跑原版 PhyClone，用官方評分程式計 sc1A–sc3B。
- 這可以回答「PhyClone 在 single-sample 下的表現」。M01 筆記指出這正是 PhyClone 論文證據最薄的部分。
- 轉換時的難點：Battenberg 給的 subclonal CN 是兩個狀態加比例，PhyClone 只吃一組 major/minor。這正好重現上一輪討論的 subclonal CNA 問題；可以把「SNV 位在 subclonal CN 區」當成分層變數。

### 3. Long-read 版 benchmark：可以照這個模擬框架重做

- SMC-Het 的模擬本來就是「依 haplotype 分 read pool → 依 CP 和 CN 調深度 → 依樹 spike-in」。
- 換成 long read 的做法：
  - GM24385 就是 **HG002**，GIAB 有公開的 ONT 資料（推論；需要另外確認版本與深度）。
  - 用 longphase 對 HG002 ONT 定相，按 HP／PS 切 read pool，沿用 SMC-Het 的 51 棵設計樹與 CP／CN 參數，用 BAMSurgeon 或其他 long-read spike-in 工具重做 tumor BAM。
- 好處：
  - **真值完全已知**：樹、SNV→node、SNV 在哪條 haplotype、CN 事件在哪條 haplotype。
  - 可以直接量化 C2（HP-aware genotype prior）、C3（HP 拆分 likelihood）、C4（同 read 共現 factor）的增益。
  - 可以和 SMC-Het 的 short-read 結果比較：同一棵設計樹，short read 對 long read。
- 風險：
  - BAMSurgeon 對 ONT long read 的 spike-in 支援程度不明，需要先確認或改用其他工具。
  - 模擬資料的錯誤型態不等於真實 ONT 錯誤。
  - 這只是「方法在已知設定下的表現」，不能取代真實腫瘤的驗證。

### 4. 論文結果給本 repo 的設計限制

- **NRPCC**：本 repo 每個 `tX_nY` subsample 要先算 NRPCC 再解讀結果。例如 d=60×、ρ=0.5、ψ=3 時，NRPCC＝30/(1.5+1)＝12，低於建議的 32。purity 和 ploidy 要用估計值，不能用 nominal 百分比。
- **subclonal gain 漏偵測率高（25/48）**：bulk short-read 的 CN caller 對 subclonal gain 很弱。HP-specific depth 可能有幫助，這可以列為 C0／C1 的一個獨立評估項目：HP-aware CN 對 subclonal gain 的偵測率。
- **clonal SNV＋subclonal loss 最難**：這正是 HP 資訊最可能有用的位置。若 SNV 在 HP1、而 HP1 在某 subclone 被刪除，HP 拆分的 VAF 會直接顯示出來。可以設計成 C3 的分層評估。
- **single-sample 樹的深層結構不可靠**：推錯 parent 多半錯到相近 node。C4 的 read pair 證據應該**專門評估在非 clonal、深層的 SNV pair 上**的增益，因為那裡 baseline 最弱。
- **雜訊模型**：Gaussian 明顯比 binomial／beta-binomial 差。PhyClone 已用 beta-binomial；新增的 HP 拆分 likelihood 也應維持 count-based 模型。

## 核心判斷

1. 這是目前最完整的 single-sample bulk subclonal reconstruction benchmark，但只有 short read、只有模擬資料，而且 PhyClone 不在受測方法中。
2. sc3 的四矩陣評分和本 repo `evaluation_v1.md` 的四類關係矩陣幾乎同構，可以直接接軌；soft 版本（sc3B）能用到 PhyClone 的 posterior。
3. 最便宜的下一步是：在 Synapse 資料上跑原版 PhyClone，用官方評分程式取得 single-sample 基線。
4. 作者在 Discussion 明確把 long read 的 mutation-to-mutation／mutation-to-SNP phasing 列為未來方向，這直接支持本研究的動機；但論文本身沒有任何 long-read 實驗。
5. 它的模擬框架是「依 haplotype 分 read pool」，所以可以改成 long-read 版，做出 HP 真值完全已知的 benchmark。這是評估 C2–C4 最乾淨的途徑，代價是需要確認 long-read spike-in 工具。
