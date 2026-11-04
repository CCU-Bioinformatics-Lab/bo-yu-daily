# C4 pair score 加入 SNV 的 HP 不確定性（2026-10-26）

> **2026-11-04 註記：** 文中引用的 `2026-10-25_c4_robustness` 已刪除，可用 `git show efb15e9:lab_report/2026-10-25_c4_robustness/README.md` 取回。

問題：real s1 的錯誤樹，來自低 VAF 的 s7_07 被鹼基錯誤判到錯的 HP（`lab_report/2026-10-26_c4_error_model/` 第 2.4 節）。如果 pair score 不再假設 SNV 一定在 snv_hp 上，而是依 HP1／HP2 的 alt 計數給一個後驗機率，能不能修好這類失敗，又不傷到其他 run？

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論。

## 1. 結論

- **修好了目標問題。** 〔實測〕real s1（e 0.004）：
  - C3 不再被拆開：MAP 從 4 個 node 變成 3 個，clone 數眾數 4 → 3（posterior 0.98）。
  - pair term 不再偏好錯誤的樹：最佳相容樹 − MAP 的 pair 差，從 −14.5 變成 0.0。
- **但 real s1 仍然判為錯誤，原因和 C4 無關。** 〔實測〕剩下的錯誤樹是「C2／C4 合併，s8 放到 C3」（0.62）。s8 在 segment A，那裡沒有合格 pair。分數拆解：prior −4.4、data +2.1、pair 0.0。eps 0.01 的 run 也有同一類錯誤（0.35）；e0 seed 1 有類似的 segment A s8 放錯（0.40，`2026-10-25_c4_robustness` 第 3 節）。所以 real s1 的「錯誤樹 > 0.5」是 base 模型在 segment A 的問題，C4 只是讓它多了 C3 被拆開這一層。
- **整體沒有改善。** 〔實測〕校正組合（b03 e 0.03，其餘 0.004）：

| | 誤差模型 | ＋HP 不確定性 |
|---|---|---|
| 錯誤樹 > 0.5 | **1** | 2 |
| C1／C2 分開 | **10** | 9 |
| 完整 4 clone 樹 > 0.5 | **3** | 2 |
| segment C 相容比例平均 | **0.943** | 0.936 |

- **副作用：正確的分支證據也被削弱。** 〔實測〕
  - e0 s3 的 C1／C2 合併：0.504 → 0.958；sw5 s3：0.164 → 0.578。
  - e = 0.03 時，P2 開始失守：直線樹最高 0.18（e0 s3 0.147）。沒有 HP 不確定性時是 0.001。
  - 模式 2 增加：sw5 s1 0.994、sw5 s3 0.960（e 0.03）。
  - 原因〔推論〕：q < 1 時，每個 pair 的反證都有上限，正確的分支證據（例如 s4 × s6）也一樣。錯誤率越高，q 越不確定，上限越低。這和 composite weight 失敗的原因相同：任何「一律削弱 pair 證據」的修法，都會削弱 C4 對抗 FSCRP prior、分開 C1／C2 的力量。
- **合格 pair 增加 28–105 個。** 〔實測〕HP 不確定的 SNV 現在也會進入計算，只是權重較低。
- **建議：** 不把 HP 不確定性設為預設，保留成選項（`--pair-hp-uncertain`）。三次「削弱 pair 證據」的嘗試（composite weight、高估 e、HP 不確定性）結果都一樣，所以下一步應該處理 FSCRP prior（模式 2 的主因，`2026-10-26_c4_truth_vs_map`），而不是繼續調整 pair 證據的強度。

## 2. 模型

`tools/phyclone_pairs.py`：`hp_posterior`、`hp_uncertain_scores`；`tools/phyclone_hp.py --pair-hp-uncertain`（需要 `--pair-error`）。

- q_i(h)：SNV i 在 HP h 上的後驗機率。在 h 上時，alt 比例 ~ Beta(1,1)；在另一條 HP 上時，alt read 全部是錯誤（錯誤率 e）。prior 各 1/2。mistag 沒有建模。
- pair 在 HP h 上的分數 = log Σ 四種情況：兩個都在 h（誤差模型的 relation 分數，權重 q_i q_j）、只有 i 在、只有 j 在、都不在。後三種和 relation 無關。
- 合格條件：q_i(h)、q_j(h) 都 ≥ 0.05（原本是 snv_hp = h）。
- q = 1 時和誤差模型完全相同（測試，誤差 < 1e-9）。
- 測試：`tools/test_phyclone_pairs.py`，23 個全部通過。包括 q = 1 時等價、HP 有疑慮時反證有上限（s6_04 × s7_07：6.93 → 1.70）、強的分支證據保得住、spawn 子 process 看得到新設定。

## 3. 結果

壓力測試樹，×10 密度，base＋C4，資料 seed 1／2／3，PhyClone 設定同前。完整表：`topology_summary.tsv`；彙總：`results_by_arm.tsv`。

### 3.1 依 arm（12 個 run／arm）

| arm | 錯誤樹 > 0.5 | `c3_under_c4` 最大 | C1／C2 分開 | 完整 4 clone 樹 > 0.5 | `segC_compat` 平均 |
|---|---|---|---|---|---|
| eps 0.01 | 0 | 0.001 | 9 | 2 | 0.728 |
| err 0.004 | 1 | 0.000 | 11 | 4 | 0.856 |
| err 0.004＋HP | 1 | 0.000 | 10 | 3 | 0.850 |
| err 0.03 | 3 | 0.001 | 6 | 0 | 0.790 |
| err 0.03＋HP | 5 | **0.180** | 4 | 0 | 0.729 |
| 校正組合 | 1 | 0.000 | 10 | 3 | 0.943 |
| 校正組合＋HP | 2 | 0.001 | 9 | 2 | 0.936 |

### 3.2 主要變化（seed 1／2／3）

| 條件 | arm | `c1c2_merged` | `max_wrong` | clone 數眾數 |
|---|---|---|---|---|
| real | err 0.004 | 0.000／0.073／0.000 | 0.513／0.169／0.007 | 4／4／3 |
| real | err 0.004＋HP | 0.000／0.155／0.000 | 0.622／0.149／0.008 | **3**／4／3 |
| e0 | err 0.004 | 0.003／0.000／0.504 | 0.411／0.003／0.113 | 3／3／4 |
| e0 | err 0.004＋HP | 0.011／0.234／**0.958** | 0.412／0.003／0.009 | 3／3／3 |
| sw5 | err 0.004 | 0.220／0.204／0.164 | 0.239／0.188／0.237 | 4／4／4 |
| sw5 | err 0.004＋HP | 0.257／0.293／**0.578** | 0.180／0.167／0.111 | 4／4／4 |
| b03 | err 0.03 | 0.237／0.000／0.639 | 0.309／0.326／0.306 | 3／3／3 |
| b03 | err 0.03＋HP | 0.191／0.000／**0.944** | 0.321／0.307／**0.582** | 3／3／3 |

### 3.3 失敗 run 的分數拆解（最佳相容 − MAP；> 0 表示偏好真值）

| run | verdict | 總差 | prior | data | pair | posterior 錯誤樹 |
|---|---|---|---|---|---|---|
| real s1，err 0.004＋HP | model | −2.3 | **−4.4** | +2.1 | 0.0 | 0.62 |
| b03 s2，err 0.004＋HP | model | −23.4 | +28.8 | +7.0 | **−59.2** | 0.33 |
| b03 s3，err 0.004＋HP | model | −22.2 | +21.2 | −8.5 | **−35.0** | 0.18 |
| sw5 s1，err 0.03＋HP | model | −8.6 | **−21.6** | +7.6 | +5.4 | 0.99 |
| sw5 s3，err 0.03＋HP | model | −11.7 | +1.2 | **−10.9** | −1.9 | 0.96 |
| real s1，err 0.03＋HP | model | −4.0 | **−6.5** | +4.7 | −2.2 | 0.63 |

- real s1：pair 差是 0，剩下的錯誤是 prior 主導，和 C4 無關。
- b03 用 e 0.004（低估）：仍然是 pair 主導，屬於模式 1 的殘留和 read 重複計算。HP 不確定性對它沒有幫助。
- sw5 s1：模式 2，prior 主導，和前幾輪相同。

### 3.4 不跑 MCMC 的檢查（real s1）

用新的分數重算誤差模型 run 的 MAP 樹和最佳相容樹：總差 −5.10 → +1.76，pair 差 −14.5 → −7.6。剩下的 7.6 來自 s6_08 的錯誤 read 被重複計算，HP 不確定性解決不了這部分。MCMC 的結果比這個好（pair 差 0），因為新的 MAP 已經不再把 C3 拆開。〔實測〕

## 4. 做法

```bash
L=lab_report/2026-10-26_c4_hp_uncertain
bash $L/run_all.sh $L/jobs_step1.txt          # 24 run，約 44 分鐘
bash $L/summarize.sh > $L/topology_summary.tsv
bash lab_report/2026-10-26_c4_truth_vs_map/run_all.sh > lab_report/2026-10-26_c4_truth_vs_map/scores.tsv
```

## 5. 限制

- 只有一棵手寫樹、×10 密度、一個 MCMC seed。
- q 沒有考慮 mistag：被錯標的 alt read 會被當成錯誤，讓 q 稍微低估。
- q 的 alt 比例 prior 是 Beta(1,1)。對低 VAF 的 SNV 來說太寬，可能讓 q 偏向「只有少數 alt read」的那條 HP。
- 合格門檻 Q_MIN = 0.05 是自訂的。

## 6. 下一步

1. **處理 FSCRP prior。** 三次削弱 pair 證據的嘗試都失敗了，原因都是 C1／C2 分開依賴 pair term 壓過 prior。直接處理 prior，才能同時降低對 pair 證據強度的依賴。
2. **segment A 的 s8 放錯**（real s1、e0 s1）是 base 模型的問題，和 C4 無關。A2 是否能修正它，要另外看。
3. **以 read 為單位的 likelihood**：處理 b03 和 s6_08 的重複計算。
