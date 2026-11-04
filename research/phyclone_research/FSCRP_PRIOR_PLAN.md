# FSCRP prior 修改：計畫（2026-10-26，只記錄，尚未實作）

狀態：**Rust 實作完成（haploclone `403eee0`、`f05b615`，2026-10-27），實驗尚未執行。** 原本：只記錄，尚未實作。 先等 PhyClone 的 Rust 重寫完成（原 `phyclone_rs/`，現在是 haploclone：`/bip8_disk/boyu114/haploclone/rust/`），再用它跑實驗。理由：每組 24 個 run 要 43–61 分鐘，prior 的比較需要很多組。

## 1. 問題與證據

**現象：失效模式 2（C1／C2 合併，C3 變成第二個 root）由 FSCRP prior 主導。** 〔實測，`lab_report/2026-10-26_c4_truth_vs_map/`〕

- 5 個模式 2 的失敗 run 中，4 個的 pair term 偏好真值（+0.3 到 +7.0），data 也大致中立；MAP 勝出靠的是 prior（MAP 高 2.1–14.9）。
- prior 的來源是 CRP 的 node 大小項 Σ log(n_k − 1)!，它偏好「一個很大的 node 加一個很小的 node」：

| run | 樹 | node 大小 | Σ log(n−1)! | prior |
|---|---|---|---|---|
| real s2，ε 0.01 | MAP | 42, 28, 26, 4 | 238.39 | 231.29 |
| | 真值拓樸（SNV 位置最佳化） | 33, 30, 30, 7 | 230.65 | 229.19 |
| sw5 s1，ε 0.03 | MAP | 40, 30, 28, 2 | 242.45 | 236.07 |
| | 真值拓樸 | 30, 30, 26, 14 | 223.07 | 221.64 |

- **削弱 pair 證據的三次嘗試都因為這個 prior 失敗。** 〔實測〕composite weight（`2026-10-26_c4_composite_weight`（2026-11-04 刪除，未進 git，無法取回））、高估錯誤率（`2026-10-26_c4_error_model`）、HP 不確定性（`2026-10-26_c4_hp_uncertain`）都讓 C1／C2 更容易合併，模式 2 惡化。C1／C2 能分開，靠的是 pair 證據強到能壓過 prior。〔推論〕
- MAP 樣本的 alpha：0.82–4.82，中位數 1.94（177 個 run）。〔實測〕

## 2. 目前的 prior（程式實作，`phyclone/tree/distributions.py`）

`FSCRPDistribution.log_p_one(tree)`：

```
K log α + Σ_k log (n_k − 1)!              CRP（node 大小）
− Σ_roots (m_r − 1) log m_r                每個 root 子樹的標記樹數（m_r = 子樹 node 數）
+ r_term(#roots, K)                        多 root 懲罰，c_const = 1000 → 每多一個 root 約 −6.91
− Σ_nodes log (out_degree)!                multiplicity
```

- alpha 用 Gamma prior 做 Gibbs 更新（`mcmc/concentration.py`；CLI `--concentration-update`、`--concentration-value`）。
- CRP 的 rich-get-richer 是 Dirichlet process 的性質：partition 的 prior ∝ α^K Π (n_k − 1)!。〔程式實作；和論文描述是否一致，這裡沒有核對〕

## 3. 候選修改

| 編號 | 修改 | 預期效果 | 風險 |
|---|---|---|---|
| P1 | **調溫**：CRP 的 node 大小項乘上 τ ∈ (0, 1]（τ = 1 是原版） | 直接削弱「大＋小」的偏好 | τ 太小會鼓勵很多小 clone（過度拆分） |
| P2 | **Pitman–Yor**：Π (1 − d)_(n_k − 1)，discount d ∈ [0, 1) | 大 node 的相對優勢變小，是有理論依據的 CRP 推廣 | 多一個參數；文獻在 clone tree 上的使用要查 |
| P3 | **固定 alpha**（`--no-concentration-update`）並掃描數值 | 檢查 alpha 的更新是否把 prior 推向少而大的 node | 只改 K log α，不影響 node 大小的不平衡 |
| P4 | **均勻 partition**：給定 K 時，所有 partition 機率相同（去掉 Σ log (n_k − 1)!） | 完全去掉大小偏好 | 失去 DP 的稀疏性，clone 數可能失控 |
| P5 | **最小 node 大小**：小於 n_min 個 SNV 的 node 加懲罰 | 針對「大＋很小（1–4 個 SNV）」的 MAP | ad hoc；n_min 依資料而定 |

推薦順序：P3（只改 CLI 參數，最便宜）→ P1 → P2。P4、P5 只當對照。

## 4. 實驗設計

1. **先不跑 MCMC。** 用 `tools/c4_truth_vs_map.py` 的分數拆解，在現有的 177 個 run 上，換成各候選 prior 重算 MAP 與最佳相容樹的分數。看模式 2 的 run 是否翻成偏好真值，以及原本 `ok` 的 run 是否被翻壞。這一步需要在工具裡加上 prior 的選項。
2. **MCMC。** 選出 1–2 個候選，跑 12 個壓力測試 sim（e0／real／sw5／b03）× 誤差模型校正組合。
3. **過度拆分的檢查。** 必須在 40 棵 TRACERx 隨機樹（`lab_report/2026-10-25_random_tree_phyclone_baseline/`（2026-11-04 刪除；取回：`git show efb15e9:lab_report/2026-10-25_random_tree_phyclone_baseline/README.md`））上確認 clone 數沒有變得太多。壓力測試樹只有 4 個 clone，看不出過度拆分。
4. **判定（提案）：** 模式 2 的 run（real s2、sw5 s1）錯誤樹 < 0.5；C1／C2 分開的 run 數 ≥ 誤差模型校正組合（10／12）；隨機樹的 clone 數錯誤沒有變差（配對 bootstrap CI）。

## 5. 和 Rust 重寫的關係

- Rust 版要讓 prior 可以替換：至少支援 τ（P1）、Pitman–Yor discount（P2）、固定或更新 alpha（P3）。
- τ = 1、d = 0 時，必須和 golden fixtures（haploclone `rust/golden/`）的 prior 數值逐位一致。

## 6. 未決問題

- 〔已處理，haploclone `9254ad5`：PY 的 α 改放在 (−d, ∞)，α + d ~ Gamma(0.01, 0.01)；K ≥ 2 時不再塌陷，K = 1 時仍堆在 −d，可用 `--prior-alpha-shape 1`–`2` 避免，這是新的未決選擇〕 原始紀錄：**PY 配 Gamma(0.01, 0.01) 的 α prior 時，α 塌到下限 1e-10**〔實測：smoke run 的 α 中位數 1e-10；quadrature 在 K=3、N=50、d=0.3 時約 84% 的 posterior 在 α < 1e-8〕。原因：PY 的 α likelihood Π_{k=1}^{K−1}(α+kd)/(α+1)_{N−1} 在 α → 0 仍大於 0，Gamma(0.01) 在 0 的尖峰主導。可選：PY 配固定 α（P3）、換 α prior、或在 α ∈ (−d, ∞) 放 prior。〔推論〕CRP 在 K = 1 時 likelihood 也是 1/(α+1)_{N−1}，同樣會塌，這可能就是隨機樹短 run alpha 停在 1e-10 的原因。
- **有 cluster 檔時 n_k 是 cluster 數**；每個 node 只有 1 個 cluster 時，τ 與 PY 的 node 大小項都是 0。§4 的實驗要用 mutation 層級的輸入。
- τ、uniform、min-node 下的 α 更新沿用 CRP 的條件分布，是近似。

- τ、d 要固定，還是當成參數一起抽樣？
- 改 prior 算不算偏離 PhyClone 的「論文模型」？報告時要清楚區分論文、原版程式和本研究的修改。
- 判定門檻需要老闆同意。
