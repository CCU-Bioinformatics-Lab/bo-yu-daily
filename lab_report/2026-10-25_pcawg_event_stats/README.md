# PCAWG 事件統計：對照 HP-aware 真值樹參數（2026-10-25）

對象：`lab_report/2026-10-24_hp_truth_tree_phyclone/` 的手動真值樹（purity 0.40、200×、4 個 clone、C3 CCF 0.10）。
文獻整理見 `research/simulation_pipeline_research/truth_evidence_2026-10-25/04_event_evidence_real_tumors.md`（本次沒有修改）。
標記：〔本次資料實測〕＝用 PCAWG open 檔自己算；〔論文主張〕＝論文的數字；〔推論〕＝本檔的推論。

## 結論

- **purity 0.40 在範圍內。** PCAWG 2,658 例中位 0.66（IQR 0.47–0.82），17.0% 的樣本 ≤ 0.40。肺腺癌 26%、前列腺癌 30% 的樣本 ≤ 0.40。〔本次資料實測〕
- **200× 遠高於 PCAWG。** tumour coverage 中位 48.5×。NRPCC 中位 13.1。真值樹的 NRPCC 是 40，PCAWG 只有 0.4% 的樣本達到。〔本次資料實測〕
- **「purity 0.40＋CCF 0.10」在 PCAWG 的深度下偵測不到。** 在 48× 時，CCF 0.10 的 SNV 期望只有約 1 條 alt read，P(alt ≥ 3) = 7.5%。在 200× 時期望 4 條，P(alt ≥ 3) = 76%。〔本次資料實測（深度）＋推論（Poisson 模型）〕
- **CCF ≤ 0.15 的 subclone 在 PCAWG 幾乎不存在，而且是偵測下限造成的。** CliPP 找到 3,001 個 subclone，只有 0.5% 的 CCF ≤ 0.15。NRPCC < 10 的樣本是 0%，NRPCC ≥ 20 的樣本升到 2.4%。〔本次資料實測（CliPP 結果）＋推論〕
- **4 個 clone 屬於 PCAWG 的上尾。** PCAWG-11 consensus：23% 有 0 個 subclone，53% 有 1 個，21% 有 2 個，只有 2.3% 有 ≥ 3 個（也就是 ≥ 4 個 clone）。CliPP 是 4.8%。這反映 40× 的偵測力，不代表腫瘤真的簡單。〔本次資料實測＋推論〕
- **單拷貝 gain 在範圍內。** 被 gain 的 bp 中，71% 只多 1 copy（per-sample 中位 80%）。〔本次資料實測〕
- **subclonal CN 和 subclonal LOH 很常見，但真值樹的密度偏高。** PCAWG 中位 7.6% 基因組是 subclonal CN，24.5% 的樣本超過 20%。真值樹 4 個 segment 中 3 個有 subclonal CN；PCAWG 只有 0.9% 的樣本 ≥ 75%。92.5% 的樣本有 subclonal LOH，55% 有 ≥ 10 Mb 的 subclonal LOH 段。〔本次資料實測〕
- **subclonal cnLOH：資料不支援。** Battenberg 的兩個狀態只差一個 allele 的一個 copy，所以 (1,1)/(2,0) 這種 subclonal cnLOH 無法表示，計數恆為 0。clonal cnLOH 有 67.6% 的樣本出現，38.6% 有 ≥ 10 Mb 的段。〔本次資料實測〕
- **突變遺失頻率：資料不直接支援。** open 檔沒有每個 SNV 的 clone 歸屬。代理值：subclonal deletion 佔基因組中位 3.7%（q75 12.8%），16% 的樣本 ≥ 20%。真值樹的 20% SNV 受影響屬於上尾。〔本次資料實測（代理）＋推論〕
- **CN timing：2:1 gain 區 early（multiplicity 2）比例中位 0.28（IQR 0.18–0.40）。** 真值樹的 seg A 是 0.5，只有 4.5% 的樣本 ≥ 0.5，偏高。cnLOH（2:0）區 early 比例中位 0.56；真值樹 seg D 是 1.0，18% 的樣本 ≥ 0.9，在範圍內但偏高端。本次估計的 molecular time 中位 0.66，接近 Gerstung 2020 的 0.60，表示方法合理。〔本次資料實測＋論文主張〕

## 對照表

判定：在範圍內＝落在 PCAWG IQR 或常見範圍；偏高／偏低＝落在 PCAWG 上／下尾（約 < 10% 樣本）；資料不支援＝open 檔無法量測。

| 事件 | 真值樹參數 | PCAWG 實測（本次） | 判定 |
|---|---|---|---|
| (d) purity | 0.40 | 中位 0.66（IQR 0.47–0.82）；17.0% ≤ 0.40；8.3% ≤ 0.30。breast 中位 0.56（17% ≤ 0.40）；lung adeno 0.49（26%）；lung SCC 0.57（13%） | 在範圍內（偏低側） |
| depth | 200× | tumour coverage 中位 48.5× | 偏高（約 4 倍） |
| NRPCC | 40 | 中位 13.1；71.5% ≥ 10；0.4% ≥ 40 | 偏高 |
| (d) clone 數 | 4（3 個 subclone） | PCAWG-11 consensus：0／1／2／≥3 個 subclone = 23.3%／53.2%／21.3%／2.3%。CliPP cluster 1／2／3／≥4 = 15.4%／63.4%／16.4%／4.8% | 偏高（上尾；受偵測力限制） |
| (b) 低 CCF subclone | C3 CCF 0.10 | CliPP subclone CCF 中位 0.40（IQR 0.31–0.49）；≤ 0.15 只佔 0.5%；< 0.30 佔 21%。0.6% 的樣本有 CCF ≤ 0.15 的 subclone | 偏低（PCAWG 幾乎看不到；偵測受限） |
| (b) 可偵測性 | 200×、purity 0.40、CCF 0.10 → 每 SNV 期望 4 條 alt read | 同參數在 48× → 0.97 條；P(alt ≥ 3) 7.5%。PCAWG 每樣本在 CCF 0.10 期望 alt 中位 1.3 條；CCF 0.30 才到 3.9 條 | 在 PCAWG 深度下不可偵測 |
| subclonal CN 範圍 | 4 個 segment 中 3 個（seg A、B、D） | subclonal CN 佔基因組中位 7.6%（q75 20.6%）；24.5% 樣本 > 20%；5.2% ≥ 50% | 偏高（壓力測試密度） |
| HP-specific 單拷貝 gain | seg A HP1 +1 copy，subclonal（C2，CCF 0.80） | 71% 的 gain bp 只 +1 copy。subclonal 單拷貝 gain 段 derived 狀態佔 tumour 中位 0.41（IQR 0.22–0.62） | 在範圍內（CCF 0.80 偏高端） |
| (c) subclonal cnLOH | seg D，C2（CCF 0.80） | Battenberg 無法表示，計數 0。改看 subclonal LOH：92.5% 樣本有；55% 有 ≥ 10 Mb 段；LOH 狀態佔 tumour 中位 0.30（IQR 0.14–0.61）；段長中位 0.8 Mb | subclonal cnLOH：資料不支援；subclonal LOH：在範圍內 |
| clonal cnLOH（參考） | 無 | 67.6% 樣本有；38.6% 有 ≥ 10 Mb；段長中位 0.5 Mb | — |
| (a) 突變遺失 | 20／100 個 SNV（s2 deletion、s10 cnLOH） | 資料不直接支援。代理：subclonal deletion 佔基因組中位 3.7%，q75 12.8%，16.2% 樣本 ≥ 20%，4.3% ≥ 40% | 偏高（代理值；推論） |
| (e) 2:1 gain 區 multiplicity | seg A：s1 m=2（10 個）、s8 m=1（10 個）→ early 0.5 | early／clonal 中位 0.28（IQR 0.18–0.40），pooled 0.32；4.5% 樣本 ≥ 0.5 | 偏高 |
| (e) cnLOH 區 multiplicity | seg D：保留的 s9 全部 m=2 → early 1.0 | early／clonal 中位 0.56（IQR 0.37–0.80）；18% 樣本 ≥ 0.9 | 在範圍內（偏高端） |

## 資料

全部是 open access，不需申請。下載紀錄與 URL：`/big8_disk/boyu114/benchmark_data/PCAWG/README.md`。共 1.2 GB。

| 來源 | 檔案 | 用在 |
|---|---|---|
| ICGC 25K open bucket（`s3://icgc25k-open/PCAWG/`） | `icgc_sample_annotations_summary_table.txt`（2,778 aliquot；取 `is_preferred` 的 2,658 例） | purity、depth、NRPCC、num_subclones、clonal／subclonal SNV 數 |
| 同上 | `consensus.20170119.somatic.cna.annotated.tar.gz`（2,778 例） | consensus major／minor CN、star；Battenberg 兩狀態 |
| 同上 | `final_consensus_passonly.snv_mnv_indel.icgc.public.maf.gz`（883 MB，只有 ICGC 樣本） | SNV 的 alt／ref read 數，做 multiplicity |
| CliPP（MD Anderson，第三方） | 39 個 project 的 `subclonal_structure`（2,658 例 match） | 每個 subclone 的 CCF |

沒有用到的 controlled 檔：PCAWG-11 consensus subclonal reconstruction（cluster CCF、mutation assignment）、MutationTimeR 的 `allSegmentsTime*`、`driversTiming*`、TCGA 的 SNV MAF。所以 multiplicity 只用 ICGC 樣本，subclone CCF 改用 CliPP。

## 做法

```bash
cd /bip8_disk/boyu114/main_work
D=lab_report/2026-10-25_pcawg_event_stats
# (b)(c)(d)(e)：樣本層級、CN、multiplicity（要讀 883 MB 的 MAF，需數分鐘）
python3 -I tools/pcawg_event_stats.py /big8_disk/boyu114/benchmark_data/PCAWG $D
#   只重算非 MAF 的部分：加 --skip-maf（約 10 秒）
# (b)：CliPP subclone CCF
python3 -I tools/pcawg_clipp_ccf.py /big8_disk/boyu114/benchmark_data/PCAWG $D
```

- **樣本**：只取 `is_preferred == TRUE`（每位 donor 一個樣本，2,658 例）。
- **NRPCC** = cov × p／(p × ploidy＋2(1−p))（Dentro 2021 定義）。真值樹：0.4 × 200／(0.8＋1.2) = 40。
- **可偵測性**：heterozygous、multiplicity 1 的 SNV，期望 alt read = NRPCC × CCF。P(alt ≥ 3) 用 Poisson。沒有模擬 caller、sequencing error 或 clustering。
- **CliPP CCF**：`cellular_prevalence` 是佔全部細胞的比例。CCF = CP／consensus purity。最大 CP 的 cluster 當 clonal；clonal CCF 中位 0.997，確認換算正確。
- **subclonal CN**：Battenberg `frac1_A < 0.999` 且有第二狀態，即為 subclonal 段。只算 autosome。分母是有 Battenberg 呼叫的 bp。
  - subclonal LOH：只有一個狀態的 minor = 0。LOH 不能回復，所以 LOH 狀態必為 derived，用它的 fraction 當 CCF。
  - subclonal deletion：一個狀態的 total CN 低於基準（非 WGD 為 2，WGD 為 4）。這是突變遺失的代理值。
  - subclonal cnLOH：Battenberg 只允許相鄰狀態，無法表示，不輸出。
- **clonal cnLOH**：consensus minor = 0 且 total = 基準。
- **單拷貝 gain**：consensus total = 基準＋1 的 bp ÷ total > 基準的 bp。
- **multiplicity（e）**：只用非 WGD、NRPCC ≥ 10 的 ICGC 樣本。SNV 落在 consensus 2:1 或 2:0、star ≥ 2、Battenberg clonal 的段。每個樣本 × 段型做 EM，成分是 {m=2 clonal、m=1 clonal、subclonal（m=1，CCF 0.10–0.85 均勻格點）}，binomial likelihood。至少 30 個 SNV 才報。early 比例 = w(m=2)／(w(m=1)＋w(m=2))。molecular time 用 2:1 時 t = 3n₂／(2n₂＋n₁)，2:0 時 t = 2n₂／(2n₂＋n₁)（MutationTimeR 的簡化，沒有 bootstrap）。
- **分層**：breast、lung adeno、lung SCC、prostate、liver、pancreas、melanoma、ovary、colorectal、GBM、clear-cell RCC。

## 結果

表格在 `tables/`：

| 檔案 | 內容 |
|---|---|
| `d_purity_depth_subclones.tsv` | purity、coverage、NRPCC、subclone 數、subclonal SNV 比例（全體＋分層） |
| `d_purity_histogram.tsv` | purity 分佈（0.1 間隔） |
| `b_detectability.tsv` | 真值樹參數在不同 depth 的 NRPCC、期望 alt read、P(alt ≥ 3) |
| `b_clipp_subclone_ccf_summary.tsv`、`b_clipp_subclone_ccf_histogram.tsv`、`b_clipp_ccf_by_nrpcc.tsv`、`b_clipp_per_sample.tsv` | CliPP cluster 數、subclone CCF 分佈、依 NRPCC 分層 |
| `c_copy_number_events.tsv`、`c_copy_number_per_sample.tsv`、`c_event_segment_lengths.tsv` | subclonal CN、subclonal LOH／deletion、clonal cnLOH、單拷貝 gain；段長與 CCF |
| `e_gain_multiplicity_summary.tsv`、`e_gain_multiplicity_per_sample.tsv` | 2:1 與 2:0 段的 multiplicity 權重、early 比例、molecular time |

### (d) purity、depth、clone 數〔本次資料實測〕

| 群組 | n | purity 中位 | ≤ 0.40 | coverage 中位 | NRPCC 中位 | 0／1／2／≥3 subclone |
|---|---|---|---|---|---|---|
| 全體 | 2,658 | 0.66 | 17.0% | 48.5× | 13.1 | 23%／53%／21%／2.3% |
| Breast-AdenoCA | 198 | 0.56 | 17.2% | 48.1× | 11.0 | 27%／57%／15%／2.0% |
| Lung-AdenoCA | 38 | 0.49 | 26.3% | 37.3× | 7.2 | 53%／39%／8%／0% |
| Lung-SCC | 48 | 0.57 | 12.5% | 54.5× | 12.9 | 27%／65%／8%／0% |
| Prost-AdenoCA | 210 | 0.50 | 30.5% | 58.6× | 13.9 | 20%／57%／22%／1.0% |
| Panc-AdenoCA | 239 | 0.56 | 22.6% | 62.7× | 15.6 | 17%／49%／31%／2.9% |
| Ovary-AdenoCA | 113 | 0.79 | 3.5% | 50.8× | 15.0 | 11%／54%／28%／7.1% |

肺腺癌 NRPCC 中位只有 7.2，一半樣本沒有 subclone。這比較像偵測力不足，不是腫瘤沒有 subclone。〔推論〕

### (b) 低 CCF subclone 與可偵測性

| 情境 | NRPCC | CCF 0.10 期望 alt read | P(alt ≥ 3) |
|---|---|---|---|
| 真值樹：purity 0.40，200× | 40 | 4.0 | 0.76 |
| purity 0.40，60× | 12 | 1.2 | 0.12 |
| purity 0.40，48.5×（PCAWG 中位） | 9.7 | 0.97 | 0.075 |
| purity 0.40，40× | 8 | 0.8 | 0.047 |

〔推論：Poisson 模型，不含 error〕

CliPP subclone CCF 依 NRPCC 分層〔本次資料實測〕：

| NRPCC | 樣本數 | subclone CCF 中位 | CCF ≤ 0.15 的 subclone 比例 | 有 CCF ≤ 0.15 subclone 的樣本比例 |
|---|---|---|---|---|
| < 10 | 757 | 0.46 | 0% | 0% |
| 10–20 | 1,438 | 0.39 | 0.2% | 0.3% |
| ≥ 20 | 463 | 0.33 | 1.7% | 2.4% |

NRPCC 越高，找到的 subclone CCF 越低。這表示 PCAWG 的 CCF 分佈被偵測下限截斷。〔推論〕Dentro 2021 也說 NRPCC ≥ 10 時只保證 CCF ≥ 0.30 可偵測。〔論文主張〕

### (c) subclonal CN、LOH〔本次資料實測〕

| 群組 | subclonal CN 基因組比例中位 | > 20% 的樣本 | 有 subclonal LOH ≥ 10 Mb | 有 clonal cnLOH ≥ 10 Mb | subclonal deletion 中位 |
|---|---|---|---|---|---|
| 全體 | 7.6% | 24.5% | 54.9% | 38.6% | 3.7% |
| Breast-AdenoCA | 11.9% | 34.3% | 59.1% | 52.5% | 6.7% |
| Lung-AdenoCA | 20.9% | 47.4% | 81.6% | 47.4% | 14.5% |
| Lung-SCC | 20.3% | 50.0% | 70.8% | 77.1% | 13.8% |
| Prost-AdenoCA | 3.5% | 11.0% | 59.5% | 9.5% | 2.4% |
| Kidney-RCC.clearcell | 1.1% | 6.3% | 34.2% | 18.9% | 0.2% |

段長（全體）：subclonal LOH 中位 0.8 Mb（17% ≥ 10 Mb）；subclonal 單拷貝 gain 中位 0.4 Mb；clonal cnLOH 中位 0.5 Mb（15% ≥ 10 Mb）。小段很多，可能部分是 segmentation 雜訊。〔推論〕

肺癌的 subclonal CN 比例約是全體的 3 倍，和 TRACERx 的高 CIN 一致。〔本次資料實測＋推論〕

### (e) CN timing〔本次資料實測〕

| 段型 | 樣本數 | SNV 數 | early 比例中位（IQR） | molecular time 中位 | ≥ 0.5 的樣本 |
|---|---|---|---|---|---|
| 2:1（單拷貝 gain） | 506 | 597,678 | 0.28（0.18–0.40） | 0.66 | 4.5% |
| 2:0（cnLOH） | 245 | 131,875 | 0.56（0.37–0.80） | 0.72 | 58.8% |

Gerstung 2020 報 gain 的 molecular time 中位 0.60（IQR 0.10–0.87）。〔論文主張〕本次 0.66 接近，但本次只用 ICGC、非 WGD、NRPCC ≥ 10 的樣本。breast 2:1 early 比例中位 0.24（37 例）。

## 限制

- **subclone CCF 不是 PCAWG-11 consensus。** consensus 的 cluster CCF 是 controlled。CliPP 是 consensus 的 11 個方法之一，但它的 cluster 數比 consensus 多（≥ 4 cluster：4.8% vs 2.3%）。
- **突變遺失沒有直接量測。** subclonal deletion 的基因組比例只是候選區的大小。真正遺失的 SNV 還要在被刪的 allele 上，而且要早於 deletion，所以實際比例應該更低。〔推論〕
- **subclonal cnLOH 無法量測。** 這是 Battenberg 模型限制，不代表事件不存在。04 檔引用的 Alleloscope、CHISEL 等 single-cell 研究直接觀察到 subclonal cnLOH。〔論文主張〕
- **Battenberg 狀態的方向是假設。** gain／deletion 的 derived 狀態用「高／低 CN 者」判定；只有 LOH 能確定方向。
- **multiplicity 是簡化版 MutationTimeR。** 沒有 bootstrap、沒有 clonal／subclonal 的 cluster 位置先驗；subclonal 成分用均勻 CCF 格點。只用 ICGC 樣本（TCGA MAF 是 controlled），且只用非 WGD 樣本。
- **真值樹參數的對應不完全相等。** 真值樹的 seg A gain 是 subclonal，而 s8 是 gain 後的 subclonal SNV；PCAWG 的 early 比例只算 clonal 2:1 段的 clonal SNV。〔推論〕
- **可偵測性模型沒有 caller 與 error。** ONT error 接近 VAF 0.02，實際可偵測性比 Poisson 估計更差。〔推論〕
- **短讀 WGS 的 PCAWG，不等於 ONT。** depth、purity 分佈可以借用；read 層級的 phasing 與共現本次沒有量測。
- **PCAWG 的 purity 偏高。** 收案有 purity 門檻，所以低 purity 的比例被低估（見 04 的 TCGA PDAC 例子）。〔論文主張〕
- **座標是 GRCh37。** 本次只用比例與長度，沒有和 GRCh38 資料合併。
