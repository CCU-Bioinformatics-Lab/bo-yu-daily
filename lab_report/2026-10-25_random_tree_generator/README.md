# longbulksim 隨機樹生成器：與 cohort 實測比對（2026-10-25）

對象：`longbulksim/longbulksim/random_tree.py`。每個 spec 取一棵 TRACERx 421 的單區域真實樹，再配上同一個 tumour 的 CN 事件。

標記：〔實測〕＝本次生成 1,000 個 spec 後計算；〔推論〕＝本檔推論。

## 1. 結論

- **從藍圖直接取的量都吻合。** 直線樹 73.7%（TRACERx 73%），purity 中位 0.42（0.41）。〔實測〕
- **CCF 投影不改變分布。** 不 merge 時，subclone CCF 中位 0.59、clone 數中位 5，TRACERx 原始值是 0.58、5。〔實測〕
- **merge 讓 clone 數變少、CCF 變低，這是刻意的。** merge 把 CCF 與 parent 相差 < 0.05 的 clone 併入 parent。67% 的 spec 有 merge。之後 clone 數中位 3，subclone CCF 中位 0.45。在單一區域裡，這些 clone 都接近 clonal，一個 bulk 樣本分不開。〔實測＋推論〕
- **突變遺失沒有調參數，自然吻合。** 遺失比例中位 0（TRACERx 0），Q90 2.0%（1.4%），最大 10%（11.7%）。41% 的 spec 至少有 1 個遺失（TRACERx 47% 的 tumour）。TRACERx 數字是嚴格下限，所以略高是合理的。〔實測〕
- **clonal gain 的 early 比例吻合。** 0.20，PCAWG 2:1 clonal 區是 0.28。〔實測〕
- **遺失機制偏 copy-neutral。** deletion 型只佔 36%，TRACERx 是 75%。原因是事件目錄只收 LOH 型 deletion，沒有收「多個 copy 少掉一個」的 deletion（例如 3+1 → 2+1）。這是已知缺口。〔推論〕

## 2. 對照表

| 指標 | cohort 來源 | cohort | 生成 | 判定 |
|---|---|---|---|---|
| clone 數中位 | TRACERx 單區域（merge 前） | 5 | 3（merge 前 5） | 由 merge 造成，刻意 |
| 直線樹比例 | TRACERx 單區域 | 0.73 | 0.737 | ✅ |
| purity 中位 | TRACERx 區域 ACF | 0.41 | 0.42 | ✅ |
| subclone CCF 中位 | TRACERx 單區域 | 0.58 | 0.45（merge 前 0.59） | 由 merge 造成，刻意 |
| 遺失比例中位 | TRACERx 每 tumour（嚴格下限） | 0 | 0 | ✅ 自然產生 |
| 遺失比例 Q90 | 同上 | 0.014 | 0.020 | ✅ 自然產生 |
| 遺失比例最大 | 同上 | 0.117 | 0.100 | ✅ 自然產生 |
| 遺失中 deletion 型 | TRACERx 遺失突變 | 0.75 | 0.36 | ⚠️ 事件目錄缺口 |
| clonal gain early 比例 | PCAWG 2:1 clonal 區 | 0.28 | 0.20 | ✅ 自然產生 |

其他〔實測〕：
- subclonal CN 區的 SNV 佔比中位 4.0%（PCAWG subclonal CN 佔基因組中位 7.6%）。
- subclonal gain 的 early 比例中位 0.50。這一項沒有 cohort 對照。
- clone 數分布（1 到 10 個）：52／222／279／201／123／78／33／10／1／1。
- 前 20 個 spec 跑完整模擬，20／20 都寫出全部輸出。

## 3. 迭代紀錄

驗證工具先跑出來，再修生成器。每一輪都是同一個工具、同一個 seed。

| 版本 | 遺失中位 | 遺失 Q90 | deletion 型 | 問題 | 修正 |
|---|---|---|---|---|---|
| v1 | 0.025 | 0.085 | 0.26 | truncal SNV 排在 clonal cnLOH 之後，在所有 clone 都消失，等於觀測不到，卻被算成遺失 | 移除沒有任何 clone 帶的 SNV |
| v2 | 0.015 | 0.066 | 0.37 | tumour 的所有多區域 subclonal 事件都放進一個區域的樹，事件太多 | 事件先指派給整個 tumour 樹的一個 clone，該 clone 在區域內才保留 |
| v3 | 0 | 0.020 | 0.36 | early 比例逐事件取中位，小 segment 不穩 | 照 PCAWG 做法，每個 spec 合併計算 |

v1、v2 的錯都在前提，不在參數。修正後沒有調任何數值參數。

## 4. 資料

- 藍圖：`longbulksim/longbulksim/data/tracerx421_region_trees.tsv`（1,426 棵區域樹、401 個 tumour）和 `tracerx421_cn_events.tsv`（12,514 個 ≥ 1 Mb 事件）。由 `tools/tracerx_blueprints.py` 從 `/big8_disk/boyu114/benchmark_data/TRACERx/Frankell2023_zenodo7822002/derived_tsv` 與 `lab_report/2026-10-25_tracerx_event_stats/tables/cn_events.tsv` 產生。
- cohort 數字：`lab_report/2026-10-25_tracerx_event_stats/`、`lab_report/2026-10-25_pcawg_event_stats/`。

## 5. 做法

```bash
python3 tools/tracerx_blueprints.py \
  /big8_disk/boyu114/benchmark_data/TRACERx/Frankell2023_zenodo7822002/derived_tsv \
  lab_report/2026-10-25_tracerx_event_stats/tables/cn_events.tsv longbulksim/longbulksim/data
python3 tools/random_tree_validation.py lab_report/2026-10-25_random_tree_generator --n 1000 --run 20
```

約 2 分鐘。輸出：`cohort_vs_generated.tsv`、`per_spec.tsv`、`summary.json`。

## 6. 限制

- **只有 NSCLC。** TRACERx 421 是肺癌，WES 約 400×。偵測下限會影響低 CCF clone 的頻率。
- **CN 事件是多區域層級的呼叫。** 「subclonal」的意思是區域之間不同。在單一區域中，這類事件是 subclonal 還是 clonal，由它被指派到的 clone 決定。這是近似。
- **事件目錄缺少非 LOH 的 deletion 和 clonal gain。** clonal gain 只來自「subclonal 事件剛好落在併入 trunk 的 clone」。WGD 沒有模擬。
- **每個 segment 最多一個事件。** 真實腫瘤有重疊事件。
- **SNV 數固定成 200 左右。** 藍圖只提供各 clone 的相對比例。被移除的「觀測不到」SNV 會讓實際數量略少（每個 spec 中位 1 個，Q90 6 個，最多 26 個；200 個中）。
