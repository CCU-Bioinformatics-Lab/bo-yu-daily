# C4 read 共現 topology 因子：壓力測試樹（2026-10-25）

問題：加入 read 共現的 pairwise 項（`plan.md` C4，設計文件的 B 層）後，單一樣本的三個失敗（`research/phyclone_research/HP_EXTENSION_DESIGN.md` §1）能不能解決？

- P1：C1 與 C2 被合併。
- P2：直線樹（C3 在 C4 之下）與分岔樹約 4:6，分不開。
- P3：cnLOH 遺失的 s10 被併進 C3。

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論。

## 1. 結論

- **C4 完全解決 P2，連實測 SNV 密度也一樣。** 錯誤直線樹的 posterior 比例，從 0.39–0.48 降到 0.000–0.002。12 個 C4 run 全部如此，包括只有 16 個合格 pair 的 ×1 密度。〔實測〕
- **少量 pair 就足夠，是因為每條矛盾的 read 代價很高。** 分支關係的 pair 每出現一條「只有一個 ALT」的 read，在祖孫假設下就要付出 log ε ≈ −4.6。×1 下，能分辨 P2 的 pair 合計給出 7.4–21.3 的 log 證據。base 兩種拓樸之間只差約 0.4。〔實測＋推論〕
- **這個強度也是風險。** 模擬沒有 phasing 誤差和定序誤差，而 ε = 0.01 是假設值。真實資料中，錯標 HP 的 read 會產生假的矛盾，可能讓 C4 很有信心地選錯樹。〔推論〕在用到真實資料之前，必須先測 ε 與 phasing 誤差的敏感度。
- **P1 只部分改善。** ×10 下，`c1c2_merged` 在 3 個 seed 中有 2 個降到接近 0。但 base＋C4 是改成 C2 與 C4 合併，clone 數仍是 3。只有 A2＋C4 的 seed 1 推出完整的 4 clone 真值樹（posterior 0.996）。〔實測〕
- **C2／C4 分不開是設計上的限制。** C2 的 SNV（s4）全在 HP2，C4 的 SNV（s5、s8）全在 HP1。不同 HP 的 SNV 不會在同一條 read 上，所以沒有任何 read 能區分這兩個 clone。〔推論〕
- **P3 要靠 A2，不是 C4。** s10 被併進 C3 的比例，base／base＋C4 約 1.0，A2／A2＋C4 約 0.01–0.04。〔實測〕所以 A2 和 C4 是互補的：A2 處理突變遺失，C4 處理拓樸。

## 2. 結果

### 2.1 posterior 比例（3 個資料 seed）

| 密度 | 方法 | 直線樹 `c3_under_c4`（真值 0） | C1／C2 合併（真值 0） | 完整 4 clone 正確（真值 1） | s10 在 C3（真值 0） |
|---|---|---|---|---|---|
| ×1 | base | 0.41／0.40／0.44 | 0.90／1.00／0.99 | 0／0／0 | 1.00／1.00／1.00 |
| ×1 | base＋C4 | **0.002／0.001／0.000** | 0.91／1.00／0.98 | 0／0／0 | 1.00／1.00／1.00 |
| ×1 | A2 | 0.44／0.44／0.43 | 0.48／1.00／0.95 | 0／0／0 | 0.00／0.01／0.01 |
| ×1 | A2＋C4 | **0.001／0.002／0.000** | 0.49／0.99／0.92 | 0／0／0 | 0.00／0.02／0.02 |
| ×10 | base | 0.39／0.43／0.42 | 1.00／0.96／1.00 | 0／0／0 | 1.00／0.99／1.00 |
| ×10 | base＋C4 | **0／0／0** | 0.01／0.12／1.00 | 0／0／0 | 1.00／1.00／1.00 |
| ×10 | A2 | 0.44／0.45／0.48 | 1.00／0.80／1.00 | 0／0／0 | 0.01／0.00／0.01 |
| ×10 | A2＋C4 | **0／0／0** | 0.00／0.00／0.74 | **1.00**／0／0.26 | 0.04／0.00／0.02 |

完整表：`topology_summary.tsv`。MAP 樹：`map_trees.tsv`。

### 2.2 合格 pair 數（seed 1）

| 密度 | pair 列數 | 合格 pair | s4×s6 | s5×s7 |
|---|---|---|---|---|
| ×1 | 105 | 16 | 3 | 6 |
| ×10 | 1,094 | 157 | 23 | 28 |

s4（C2）×s6（C3）與 s5（C4）×s7（C3）都是分支關係。直線樹把 C3 放在 C4 之下，會讓它們變成祖孫關係，所以這兩組 pair 能分辨 P2。

## 3. 資料

- 樹：手寫壓力測試樹（`longbulksim/specs/stress.yaml`）。purity 0.40，200×，100 個 SNV，單一樣本。
- 密度：×1 是 HCC1395 實測的 12.9 SNV／Mb；×10 是 `plan.md` §5.8.5 的高密度分層（segment 長度除以 10）。spec 在 `specs/`。
- 模擬：`longbulksim` v0.1，資料 seed 1–3。HP tag 比例 0.859，沒有 phasing 誤差。

## 4. 做法

```bash
bash lab_report/2026-10-25_c4_pair_term_stress/run_all.sh
```

- 四種方法用同一份模擬資料，PhyClone 設定相同：`-d binomial -b 100 -n 1000 --num-chains 4 --seed 1`，outlier 關閉。
- C4：`tools/phyclone_pairs.py`，經 `tools/phyclone_hp.py --pairs` 開啟，ε = 0.01。
- 拓樸彙總：`tools/summarize_hp_truth_topologies.py`（指標定義見該檔）。

### 4.1 C4 的實作

- **pair score。** 四種關係的公式照 `plan.md` §4.5.3。n00 不建模；允許格子之間的未知比例用 Beta(1,1) 積分。
- **合格 pair。** 只用觀測資料（`plan.md` §4.5.1）：
  - 兩個 SNV 的觀測 `snv_hp` 相同，且等於 read 的 HP。
  - 兩者在同一個 segment。
  - 該 HP 在 segment 的兩種 CN 狀態都正好 1 copy（`segments.tsv` 的 a／b 狀態，不用 phi）。
- **接法。** pairwise 項加進 `TreeJointDistribution` 的 `log_p`、`log_p_one`、`compute_log_p_and_log_p_one`。SMC、PG、Gibbs-MH 和 trace 的 `log_p` 都經過這三個方法，所以 MAP 也會反映它。proposal 不知道 pairwise 項。
- **沒有改 submodule。** 採用可逆的外部 monkeypatch。是否改進 submodule，仍是未決問題（`HP_EXTENSION_DESIGN.md` §8 第 3 項）。
- **速度。** 157 個合格 pair 時，比 base 慢約 23%。
- **測試。** `tools/test_phyclone_pairs.py`，6 個。

### 4.2 第一輪失效與修正

- 第一輪 12 個 C4 run 的結果，與沒有 C4 的 run 逐位相同。
- 原因：PhyClone 在 `get_context("spawn")` 的子 process 裡跑 chain（`phyclone/run.py` L117）。子 process 重新 import 原版的 `TreeJointDistribution`，所以只在主 process 做的 patch 沒有生效。
- 修正：`install_everywhere()` 替換 `phyclone.run.ProcessPoolExecutor`，加上 initializer，在每個子 process 重新安裝 pairwise 項。
- 回歸測試：`SpawnedChainWorkers` 確認 spawn 出來的子 process 看得到 patch。拿掉 initializer 時，子 process 看到的是原版，所以這個測試有鑑別力。
- A1／A2 不受影響。資料在主 process 載入後才 pickle 給子 process，所以 `lab_report/2026-10-25_random_tree_phyclone_baseline/` 的結果仍然有效。

## 5. 限制

- **沒有 phasing 誤差，ε 是假設值。** 這是 C4 結論最大的弱點，見第 1 節。
- **只有一棵手寫樹。** 隨機真實樹（`lab_report/2026-10-25_random_tree_phyclone_baseline/`）上還沒跑 C4。
- **每個資料 seed 只有一個 MCMC seed。**
- **A2 用真值 phi。**
- **proposal 不知道 pairwise 項。** 目標分布是對的，但 C1／C2 這種需要大幅改樹的移動，可能抽樣效率不足。×10 seed 3 沒有分開 C1／C2，原因未查明。
- **trace.h5 沒有 commit**（`.gitignore`）。
