# longbulksim 隨機樹生成器：與 cohort 實測比對（2026-10-25）

對象：`longbulksim/longbulksim/random_tree.py`。每個 spec 取一棵 TRACERx 421 的單區域真實樹，再配上同一個 tumour 的 allele-specific CN profile。

標記：〔實測〕＝本次生成 1,000 個 spec 後計算；〔推論〕＝本檔推論。

## 1. 結論

- **從藍圖直接取的量都吻合。** 直線樹 72.9%（TRACERx 73%），purity 中位 0.41（0.41）。〔實測〕
- **CCF 投影不改變分布。** 不 merge 時，subclone CCF 中位 0.59、clone 數中位 5，TRACERx 原始值是 0.58、5。〔實測〕
- **merge 讓 clone 數變少、CCF 變低，這是刻意的。** CCF 與 parent 相差 < 0.05 的 clone 併入 parent，65% 的 spec 有 merge。之後 clone 數中位 3，subclone CCF 中位 0.45。〔實測〕在單一區域裡，這些 clone 都接近 clonal，一個 bulk 樣本分不開。〔推論〕
- **CN timing 沒有調參數，自然落在 PCAWG 的 IQR 內。** clonal 2:1 區 early 比例 0.24（PCAWG 中位 0.28，IQR 0.18–0.40）。2:0 區 0.42（0.56，IQR 0.37–0.80）。〔實測〕
- **subclonal CN 的量吻合。** subclonal CN 區的 SNV 佔比中位 6.4%，PCAWG subclonal CN 佔基因組中位 7.6%。〔實測〕
- **突變遺失高於 TRACERx 的嚴格下限，但低於論文估計。** 中位 0.5%、Q90 3.1%、最大 13.5%。TRACERx 嚴格下限是 0／1.4%／11.7%。〔實測〕Jamal-Hanjani 2017 估計 subclonal 突變中位 13% 可能因 CN 遺失。所以生成值在兩者之間，判定為可接受。〔推論〕
- **遺失機制現在偏 deletion 型。** deletion 型 91%，TRACERx 是 75%。CN 目錄改版前是 36%。〔實測〕

## 2. 對照表

| 指標 | cohort 來源 | cohort | 生成 | 判定 |
|---|---|---|---|---|
| clone 數中位 | TRACERx 單區域（merge 前） | 5 | 3（merge 前 5） | 由 merge 造成，刻意 |
| 直線樹比例 | TRACERx 單區域 | 0.73 | 0.729 | ✅ |
| purity 中位 | TRACERx 區域 ACF | 0.41 | 0.41 | ✅ |
| subclone CCF 中位 | TRACERx 單區域 | 0.58 | 0.45（merge 前 0.59） | 由 merge 造成，刻意 |
| 遺失比例中位 | TRACERx 每 tumour（嚴格下限） | 0 | 0.005 | ⚠️ 高於下限 |
| 遺失比例 Q90 | 同上 | 0.014 | 0.031 | ⚠️ 高於下限 |
| 遺失比例最大 | 同上 | 0.117 | 0.135 | ✅ |
| 遺失中 deletion 型 | TRACERx 遺失突變 | 0.75 | 0.91 | ⚠️ 偏高 |
| clonal 2:1 early 比例 | PCAWG | 0.28 | 0.24 | ✅ 在 IQR 內 |
| clonal 2:0 early 比例 | PCAWG | 0.56 | 0.42 | ✅ 在 IQR 內 |
| subclonal CN 區 SNV 佔比 | PCAWG（佔基因組） | 0.076 | 0.064 | ✅ |

其他〔實測〕：
- 56% 的 spec 至少有 1 個遺失（TRACERx 47% 的 tumour）。
- 前 20 個 spec 跑完整模擬，20／20 都寫出全部輸出。

## 3. 迭代紀錄

驗證工具先跑出來，再修生成器。每一輪都用同一個工具、同一個 seed。v1–v3 用舊 CN 目錄（4 類 ≥ 1 Mb 事件）。v4 換成每個 segment 的 trunk 狀態加 subclonal 改變。

| 版本 | 遺失中位 | 遺失 Q90 | deletion 型 | 問題 | 修正 |
|---|---|---|---|---|---|
| v1 | 0.025 | 0.085 | 0.26 | truncal SNV 排在 clonal cnLOH 之後，在所有 clone 都消失，等於觀測不到，卻被算成遺失 | 移除沒有任何 clone 帶的 SNV |
| v2 | 0.015 | 0.066 | 0.37 | tumour 的所有多區域 subclonal 事件都放進一個區域的樹，事件太多 | 事件先指派給整個 tumour 樹的一個 clone，該 clone 在區域內才保留 |
| v3 | 0 | 0.020 | 0.36 | 事件目錄沒有非 LOH 的 deletion 和 clonal gain | 改用 `scna_region` 重建每個 segment 的 trunk 與 subclonal 狀態 |
| v4 | 0.005 | 0.031 | 0.91 | 見第 1 節 | 不調參數，照實記錄 |

### v4 的假設檢查

假設：trunk 方向用「多數狀態」判斷（佔 subclonal segment 的 65%）時，會把 gain 誤判成 loss，造成多餘的 deletion 型遺失。

檢查：在 500 個 spec 中，比較兩種規則的 segment 上 SNV 的遺失率。

| trunk 判斷規則 | SNV 數 | 遺失 | 遺失率 |
|---|---|---|---|
| majority | 22,681 | 622 | 2.7% |
| ploidy | 13,075 | 412 | 3.2% |
| 沒有 subclonal 改變 | 58,970 | 0 | 0 |

結果：兩種規則的遺失率相近，假設被推翻。〔實測〕所以不改方向判斷規則。

## 4. 資料

- 藍圖：`longbulksim/longbulksim/data/tracerx421_region_trees.tsv`（1,426 棵區域樹、401 個 tumour）和 `tracerx421_cn_segments.tsv`（60,067 個 segment，32,383 個有 subclonal 改變）。由 `tools/tracerx_blueprints.py` 從 `/big8_disk/boyu114/benchmark_data/TRACERx/Frankell2023_zenodo7822002/derived_tsv` 產生。
- CN segment 的規則：
  - allele 的 raw CN 在區域間的範圍 ≥ 0.8 才算改變。這和 `tools/tracerx_event_stats.py` 的 strict 規則相同。
  - 有兩種區域狀態時，標成 `neutral`（相對 ploidy）的那個當 trunk。兩個都不是或都是時，用比較常見的狀態（`rule` 欄）。
- cohort 數字：`lab_report/2026-10-25_tracerx_event_stats/`、`lab_report/2026-10-25_pcawg_event_stats/`。

## 5. 做法

```bash
python3 tools/tracerx_blueprints.py \
  /big8_disk/boyu114/benchmark_data/TRACERx/Frankell2023_zenodo7822002/derived_tsv \
  longbulksim/longbulksim/data                                    # 約 1 分鐘
python3 tools/random_tree_validation.py lab_report/2026-10-25_random_tree_generator --n 1000 --run 20
```

驗證約 2 分鐘。輸出：`cohort_vs_generated.tsv`、`per_spec.tsv`、`summary.json`。

## 6. 限制

- **只有 NSCLC。** TRACERx 421 是肺癌，WES 約 400×。偵測下限會影響低 CCF clone 的頻率。
- **subclonal 改變的方向只是推論。** 65% 的 subclonal segment 用多數狀態決定 trunk。第 3 節顯示它不影響遺失率，但個別 segment 的方向可能是反的。
- **WGD 以多個獨立 gain 表示。** 同一 segment 的兩條 HP 各自在 root 邊上的隨機時間 gain，不是同時發生。
- **每個 segment 最多一個 subclonal 改變。** 有三種以上區域狀態時，只取最常見的兩種。
- **遺失機制偏 deletion 型。** 原因未查明。可能和 cnLOH 需要兩條 allele 同時達到 0.8 的門檻有關。〔推論〕
- **SNV 數固定成 200 左右。** 藍圖只提供各 clone 的相對比例。「觀測不到」的 SNV 會被移除，所以實際數量略少。
