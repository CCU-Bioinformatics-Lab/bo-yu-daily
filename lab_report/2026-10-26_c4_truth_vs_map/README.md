# 真值樹 vs MAP 樹的分數比較（2026-10-26）

> **2026-11-04 註記：** 本實驗用到的 `2026-10-25_c4_robustness`、`2026-10-26_c4_composite_weight` 已刪除。文中引用保留原文；第 89–90 行的重跑指令已無法執行。`c4_robustness` 可用 `git show db9fa20:lab_report/2026-10-25_c4_robustness/README.md` 取回，`c4_composite_weight` 未進 git，無法取回。

問題：改良版 PhyClone 選錯樹時，是**抽樣**沒找到真值樹，還是**模型**本身偏好錯誤的樹？如果是模型，是哪一項（FSCRP prior、SNV data likelihood、C4 pair term）造成的？

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論。

## 1. 結論

- **幾乎沒有抽樣問題。** 〔實測〕129 個 run 中，只有 3 個判為 `sampling`。它們的最佳相容樹只比 MAP 高 2.2–3.5 log 單位，剛好超過 tie 區間。MCMC 找到的 MAP，分數通常不低於我們能找到的任何相容樹。
- **base 和 A2（沒有 C4）的錯誤幾乎都是 tie。** 〔實測〕24 個 run 中有 17 個 tie：MAP 和最佳相容樹差 ≤ 2 log 單位（多半 < 1）。單一 bulk 樣本真的分不出直線樹和分岔樹（P2）。這是可辨識性的限制，不是 bug。
- **失效模式 1（拆 clone）是 pair term 造成的模型問題。** 〔實測〕b03（3% base error）的 base＋C4（ε 0.01）3 個 run，MAP 有 4–8 個 node，比最佳相容樹多。分數拆解：pair term 偏好 MAP 20–107 log 單位，prior 偏好真值 16–29。eps 模型把鹼基錯誤當成拆開 clone 的證據，和 `2026-10-25_c4_robustness` 第 8 節的診斷一致。
- **失效模式 2（C3 變成第二個 root）主要不是 pair term 造成的。** 〔實測〕real seed 2、sw5 seed 1 的 5 個失敗 run 裡，MAP 只比最佳相容樹高 2.0–6.0 log 單位。其中 4 個 run 的 pair term 其實**偏好真值**（+0.3 到 +7.0），讓 MAP 勝出的是 FSCRP prior（MAP 高 2.1–14.9）。例外是 sw5 s1 的 w 0.3：prior 偏好真值，MAP 靠 data likelihood 勝出（−8.0）。
  - prior 的來源是 CRP 的 node 大小項 Σ log(n−1)!。它偏好「一個很大的 node 加一個很小的 node」（MAP 的 node 大小，例如 [42, 28, 26, 4]），勝過大小平均的真值（[33, 30, 30, 7]）。差 8–19 log 單位，大於多一個 root 的懲罰（−6.9）。
  - 這修正了上一份報告「模式 2 是 pair 和 bulk 的結構衝突」的說法：bulk 和 pair 都不反對真值，是 prior 把接近平手的情況推向 C1／C2 合併。〔推論〕
  - posterior 可以高到 0.98，但 MAP 只贏 5.6，原因是 posterior 是對 SNV 位置積分，不是只比最大值。e^5.6 ≈ 270 倍的勝算已經足以得到 0.99 以上。〔推論〕
- **這個檢查不能排除模擬器的問題。** 「模型在這份資料上偏好錯誤的樹」可能是模型錯，也可能是資料不像真實資料。要分開這兩者，要做模擬器的解析期望檢查（下一步）。

## 2. 判定方法

工具：`tools/c4_truth_vs_map.py`（單一 run）、`tools/summarize_truth_vs_map.py`（彙總）。

1. 從 `trace.h5` 讀 datapoints 和 MAP 樹。datapoints 是 MCMC 實際用的 likelihood（base 或 A2）。
2. 依 run 目錄名稱套用相同的 C4 設定（eps、weight 或 error）。**檢查：** 重算的 MAP `log_p_one` 減掉 trace 存的值，129 個 run 都在 ±2.3e-13 以內。〔實測〕
3. 建出所有和真值相容的樹：真值樹，以及所有邊收縮的組合（壓力測試樹有 3 條邊，共 8 種）。
4. 對每棵相容樹做 `_opt`：拓樸固定，SNV 用 coordinate ascent 移到分數最高的 node。不允許清空 clone，也不允許移動後變成不相容（role 層，定義同 `summarize_c4_robustness.py`，遺失的 s2、s10 不計）。
   - 為什麼要 `_opt`：真值把遺失的 SNV 放在 origin clone，base model 無法表達遺失，所以直接比較真值會低估約 200 log 單位。
   - `_opt` 是局部搜尋，所以它是最佳相容分數的**下界**。
5. 所有分數都用 MAP 樣本的 alpha，拆成 prior、data likelihood、pair term。
6. 判定（只看 MAP 不相容的 run；MAP 的相容判定和 topology summary 129／129 一致）：

| verdict | 條件 | 意思 |
|---|---|---|
| `tie` | \|最佳相容 − MAP\| ≤ 2 | 模型幾乎沒有偏好（勝算 ≤ e² ≈ 7） |
| `sampling` | 最佳相容 > MAP + 2 | 模型偏好相容樹，但 run 沒找到 |
| `model` | 最佳相容 < MAP − 2 | 找不到能贏過 MAP 的相容樹 |

## 3. 結果

範圍：`2026-10-25_c4_robustness` 的 93 個 run，加上 `2026-10-26_c4_composite_weight` 的 36 個 run，共 129 個。完整表：`scores.tsv`（每棵樹一列）、`verdicts.tsv`（每個 run 一列）。

### 3.1 依方法（e0／real／sw5／b03 × 3 seed）

| run | ok | tie | sampling | model |
|---|---|---|---|---|
| base | 4 | 7 | 0 | 1 |
| A2 | 2 | 10 | 0 | 0 |
| base＋C4，ε 0.01 | 6 | 2 | 0 | 4 |
| A2＋C4，ε 0.01 | 9 | 0 | 0 | 3 |
| base＋C4，ε 0.03 | 2 | 2 | 1 | 4 |
| base＋C4，ε 0.01，w 0.3 | 7 | 0 | 2 | 3 |

### 3.2 失敗 run 的分數拆解（最佳相容 − MAP；> 0 表示該項偏好真值）

| run | verdict | 總差 | prior | data | pair | MAP node 數 |
|---|---|---|---|---|---|---|
| b03 s1，base＋C4 ε 0.01 | model | −6.2 | +15.8 | −1.8 | **−20.2** | 4 |
| b03 s3，base＋C4 ε 0.01 | model | −50.7 | +28.6 | −8.8 | **−70.6** | 5 |
| b03 s3，A2＋C4 ε 0.01 | model | −46.3 | +11.0 | +5.4 | **−62.8** | 5 |
| real s1，base＋C4 ε 0.01 | model | −15.6 | +6.1 | +1.5 | **−23.2** | 4 |
| real s2，base＋C4 ε 0.01 | model | −2.0 | −2.1 | −0.2 | +0.3 | 4 |
| real s2，base＋C4 ε 0.03 | model | −5.6 | **−14.9** | +4.0 | +5.3 | 4 |
| sw5 s1，base＋C4 ε 0.03 | model | −2.7 | **−14.4** | +4.7 | +7.0 | 4 |
| real s2，base＋C4 w 0.3 | model | −6.0 | **−11.3** | +1.8 | +3.6 | 3 |
| sw5 s1，base＋C4 w 0.3 | model | −4.5 | +4.9 | −8.0 | −1.4 | 3 |

- 上半部（b03、real s1）：pair term 是主因，對應模式 1，以及 real s1 的 C2／C4 合併與 s8 放錯。
- 下半部（real s2、sw5 s1）：對應模式 2。前 4 列 pair term 偏好真值，prior 是主因；最後一列（sw5 s1，w 0.3）是 data likelihood。
- real s1 的 pair term 也偏好 MAP（−23.2）。這個 seed 有 0.4% 的 base error 和 phase switch，所以不完全是 prior 的問題。〔實測〕

### 3.3 模式 2 的 prior 拆解

| run | 樹 | node 大小 | root 數 | Σ log(n−1)! | 子樹項 | root 懲罰 | prior |
|---|---|---|---|---|---|---|---|
| real s2，ε 0.01 | MAP | 42, 28, 26, 4 | 2 | 238.39 | −2.20 | −6.91 | 231.29 |
| | truth_opt | 33, 30, 30, 7 | 1 | 230.65 | −4.16 | 0 | 229.19 |
| real s2，ε 0.03 | MAP | 39, 31, 29, 1 | 1 | 245.52 | −4.16 | 0 | 243.62 |
| | truth_opt | 33, 30, 30, 7 | 1 | 230.65 | −4.16 | 0 | 228.75 |
| sw5 s1，ε 0.03 | MAP | 40, 30, 28, 2 | 2 | 242.45 | −2.20 | −6.91 | 236.07 |
| | truth_opt | 30, 30, 26, 14 | 1 | 223.07 | −4.16 | 0 | 221.64 |

用暫存腳本計算（各項定義見 `phyclone/tree/distributions.py` 的 `FSCRPDistribution`）。

## 4. 做法

```bash
L=lab_report/2026-10-26_c4_truth_vs_map
bash $L/run_all.sh > $L/scores.tsv          # 129 run，8 平行，約 3 分鐘
python3 tools/summarize_truth_vs_map.py $L/scores.tsv \
  lab_report/2026-10-25_c4_robustness/topology_summary.tsv \
  lab_report/2026-10-26_c4_composite_weight/topology_summary.tsv > $L/verdicts.tsv
```

## 5. 限制

- **`_opt` 是局部搜尋。** `model` 的意思是「找不到贏過 MAP 的相容樹」，不是證明沒有。差距小的 `model`（−2 到 −6）有可能是搜尋不足。
- **只比最大值。** posterior 是對 SNV 位置積分，所以分數差不能直接換算成 posterior。
- **alpha 固定在 MAP 樣本的值。** CRP 的 node 數項在兩棵樹 node 數不同時會受 alpha 影響。
- **tie 門檻 2 log 單位是自訂的。**
- **只有壓力測試樹。** 誤差模型的 24 個 run 還沒有跑完，沒有納入；跑完後重新執行 `run_all.sh`，它會自動略過還沒完成的 run。
- 不能排除模擬器的問題（第 1 節最後一點）。

## 6. 下一步

1. **模擬器的解析期望檢查：** VAF 和 pair 計數對照真值的期望值，再從 `truth/reads.tsv.gz` 獨立重算 `pairs.tsv`。這可以回答「資料本身對不對」。
2. **模式 2 要處理 prior，不是 pair term。** 例如檢查 FSCRP 的 rich-get-richer 是否不適合「少數大 clone」的單樣本情境，或者看 concentration 的更新是否把 alpha 推得太低。〔推論，未測〕
3. 誤差模型的 run 跑完後，用同一個工具檢查模式 1 是否消失。
