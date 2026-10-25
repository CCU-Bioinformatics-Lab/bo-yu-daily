# 隨機真實樹上的 PhyClone baseline 與 HP-aware emission（A1／A2）（2026-10-25）

問題：在「像真實腫瘤」的單一 bulk 樣本上，原版 PhyClone 表現如何？加入 HP 拆分計數（A1、A2）後，有沒有改善？

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論。

## 1. 結論

- **原版 PhyClone 系統性低估 clone 數。** 32 個有 ≥ 2 個可偵測 clone 的 sim 中，27 個推出的 clone 數少於可偵測數。它最多只推出 3 個 clone。〔實測〕
- **原版的拓樸關係很差。** balanced relation accuracy 中位 0.44。四類（same／ancestor／descendant／branch）隨機猜約 0.25，全對是 1。〔實測〕
- **A1、A2 都有小而確定的改善。** 和 base 配對比較，ARI 平均 +0.053（A1）／+0.063（A2），95% CI 都不含 0。V-measure、relation accuracy、CCF 誤差也一樣。〔實測〕
- **改善不是來自 clone 數。** A1、A2 都沒有減少 clone 數的錯誤（CI 含 0）。改善來自同一批 clone 裡 SNV 分得比較對，CCF 比較準。〔實測〕
- **A2 只比 A1 好一點。** A2 用的是真值 phi，所以 A2 − A1 的差（約 +0.01 ARI）是「phi 已知」能帶來的上限。〔實測＋推論〕
- **增益和 purity 有關，和 CN 複雜度無關。** 增益與 purity 的 Spearman 為 0.31。與「非 1:1 SNV 比例」為 −0.08。〔實測〕這符合理論：HP 拆分讓另一條 HP 的 read 不必進入 binomial，每條 read 的資訊比例約為 (1−p)／(1−p_h)。p_h 隨 purity 上升，所以 purity 越高增益越大。〔推論〕
- **拓樸問題要靠 read 共現（C4），不是 emission。** A1／A2 只改單一 SNV 的 likelihood，不會改變 tree prior，所以 clone 合併與拓樸錯誤大多還在。〔推論〕

## 2. 結果

### 2.1 配對比較（40 個 sim）

diff = 方法 − base，平均值與 95% bootstrap CI（10,000 次）。`ccf_mae` 與 `clone_count_err` 越低越好，其他越高越好。

| 指標 | base 中位 | A1 中位 | A2 中位 | A1 − base | A2 − base |
|---|---|---|---|---|---|
| ARI | 0.218 | 0.357 | 0.441 | +0.053 [+0.027, +0.085] | +0.063 [+0.033, +0.100] |
| V-measure | 0.203 | 0.264 | 0.349 | +0.047 [+0.026, +0.070] | +0.056 [+0.032, +0.084] |
| balanced relation acc | 0.440 | 0.483 | 0.504 | +0.033 [+0.015, +0.056] | +0.038 [+0.017, +0.064] |
| CCF MAE | 0.068 | 0.052 | 0.054 | −0.013 [−0.020, −0.007] | −0.016 [−0.025, −0.008] |
| clone 數錯誤 | 1.0 | 1.0 | 1.0 | −0.075 [−0.175, 0.000] | 0.000 [−0.125, +0.125] |

分層：
- 可偵測 clone 數 = 1（8 個 sim）：三種方法完全相同。這時只有一個 clone 可分，沒有改善空間。
- 可偵測 clone 數 ≥ 2（32 個 sim）：ARI 增益為 +0.066（A1）、+0.078（A2），CI 都不含 0。

逐 sim（ARI 差 > 0.01 算變好）：A1 有 22 個變好、17 個相同、1 個變差。A2 有 21 個變好、17 個相同、2 個變差。

完整表：`method_comparison.tsv`。逐 sim 分數：`per_sim.tsv`、`per_sim_a1.tsv`、`per_sim_a2.tsv`。

### 2.2 clone 數：可偵測數 vs 推出數

| 可偵測 | base 推出 1／2／3 | A1 推出 1／2／3 | A2 推出 1／2／3 |
|---|---|---|---|
| 0 | 1／0／0 | 1／0／0 | 1／0／0 |
| 1 | 7／0／0 | 7／0／0 | 7／0／0 |
| 2 | 3／5／0 | 2／6／0 | 2／6／0 |
| 3 | 6／9／0 | 4／11／0 | 7／8／0 |
| 4 | 0／7／0 | 0／7／0 | 0／7／0 |
| 5 | 0／1／1 | 0／1／1 | 0／1／1 |

「可偵測」＝該 clone 的 SNV，期望 alt read 數的中位 ≥ 3。在 50× 下，40 個 sim 共 141 個真 clone，其中 106 個可偵測。〔實測〕

## 3. 資料

- 樹：`longbulksim.random_tree` 從 TRACERx 421 單區域樹抽 40 個 spec（seed 2026），見 `specs/`。藍圖與 cohort 比對見 `lab_report/2026-10-25_random_tree_generator/`。
- 模擬：`longbulksim` v0.1，每個 spec 約 200 個 SNV，depth 50×（PCAWG 中位 48.5×），單一樣本，HP tag 比例 0.859，沒有 phasing 誤差。seed 1。
- clone 數：真值中位 3（1 到 7）。purity：TRACERx 區域 ACF。

## 4. 做法

```bash
bash lab_report/2026-10-25_random_tree_phyclone_baseline/run_all.sh 40 25   # 生成、模擬、base
bash lab_report/2026-10-25_random_tree_phyclone_baseline/run_hp.sh 40      # A1、A2
python3 tools/summarize_random_tree_methods.py lab_report/2026-10-25_random_tree_phyclone_baseline
```

- 三種方法用同一份模擬資料，PhyClone 設定相同：`-d binomial -b 100 -n 1000 --num-chains 4 --seed 1`，outlier 關閉，`tumour_content` 給真值 purity。
- base 讀 `input/data.tsv`。A1、A2 用 `tools/phyclone_hp.py` 讀 `input/data_hp.tsv`。A2 另外讀 `input/segments.tsv`。
- 評分：`tools/eval_random_tree_phyclone.py`（ARI、V-measure 自行實作，已用已知值核對）。
- 時間：base 每個 run 平均 17 分鐘。A1 平均 34 分鐘、A2 平均 25 分鐘，因為 40 個 run 同時跑，CPU 超載。

### 4.1 本次修正的 `phyclone_hp.py` bug

- 症狀：A2 在 40 個 sim 中有 8 個 SNV 讓程式崩潰（`need at least one array to concatenate`）。
- 原因：這 8 個 SNV 的 `snv_hp` 都是 `.`，也就是沒有任何 tagged alt read。wrapper 把 `.` 一律當成 HP2。這些 segment 的 HP2 在兩種狀態都是 0 copy，所以沒有任何可行的 scenario。
- 修正：HP 未知時，對兩條 HP 的 likelihood 取平均，不可行的那條跳過。真實資料也會有沒有 tagged alt read 的 SNV，所以這個修正對真實資料同樣有用。
- 影響：全部 SNV 中有 1.7%（131／7,489）是 `.`，其中 92 個 alt = 0。

## 5. 限制

- **A2 用真值 phi。** 真實資料的 phi 從哪來，還沒決定（`HP_EXTENSION_DESIGN.md` §8 第 1 項）。
- **purity 給真值。** 真實資料要用實測值，誤差會影響三種方法。
- **只有一種 depth（50×）與一個 MCMC seed。** posterior 的不確定性沒有估計。
- **沒有 phasing 誤差。** HP tag 一律正確，所以 A1／A2 的增益是 phasing 完美時的值。
- **樹只來自 NSCLC。** 而且 TRACERx 腫瘤的 aneuploidy 很高（中位 92% 的 SNV 不在 1:1 區）。
- **SNV 密度 12.9／Mb、約 200 個 SNV。** pair 共現資訊很少，本實驗也沒有使用。
- **評分用 MAP 樹。** 沒有看 posterior 的 topology 分布。
