# HP 特徵接進 PhyClone：設計說明（草案）

日期：2026-10-25。狀態：A1、A2 已實作並測試（見 §9）；B 還沒有實作。
前提：每個腫瘤只有**一個 bulk 樣本**（老闆 2026-10-25 指示；多樣本只當上限參考）。
基線結果：[`lab_report/2026-10-24_hp_truth_tree_phyclone/`](../../lab_report/2026-10-24_hp_truth_tree_phyclone/README.md)。
程式行號以 submodule 目前的 commit 為準，路徑相對於 `PhyClone/phyclone/`。

證據標記：〔程式〕＝讀過程式碼；〔實測〕＝基線 run 的結果；〔設計〕＝本文提出的做法；〔推論〕＝分析推論，尚未驗證。

## 1. 結論

- **要解決的是單一樣本的三個失敗。**〔實測〕
  - P1：C1 和 C2 被合併（CCF 1.00 與 0.80 → 一個 0.89 的 clone）。
  - P2：直線樹與分岔樹在 posterior 中約 4:6，無法分辨。
  - P3：cnLOH 遺失的 s10 被併進 C3。deletion 遺失的 s2 被拆到兩個 clone。outlier 機制抓不到。
- **分三層接入，依改動大小排序。**〔設計〕

| 層 | HP 特徵 | 接在哪裡 | 主要解決 | 改動大小 |
|---|---|---|---|---|
| A1 | HP 拆分計數＋haplotype CN | 每個 SNV 的 emission（CCF grid） | P1 的一部分 | 小：只換 emission |
| A2 | segment 的 subclonal haplotype CN 比例 φ | 每個 SNV 的 emission（CCF grid） | P3、P1 | 中：emission 變成多情境混合 |
| B | read 層級 SNV 共現 | 樹層級的 pairwise 項 | P2、P1 | 大：加進 tree log_p 與 sampler |

- **A1、A2 不改樹的推理。** 它們只改每個 SNV 的 likelihood 表，PhyClone 的 convolution、SMC、PG 都可以原樣使用。所以先做 A1＋A2。〔推論〕
- **B 需要改 sampler 的權重計算**，放在第二階段。

## 2. PhyClone 現在怎麼算 likelihood

〔程式〕

1. 每個 SNV 先算成一張表：`DataPoint.value`，形狀是 (sample 數, grid 數)，預設 grid = 101。每格是「node 的 CCF = 該格值」時的 log-likelihood。（`data/base.py`；`data/pyclone.py` L40–48 呼叫 `to_likelihood_grid`）
2. 表裡每格的值來自 `log_pyclone_binomial_pdf`／`log_pyclone_beta_binomial_pdf`（`utils/math_utils.py` L180–244）。它把細胞分成三群：normal（1−t）、不帶突變的 tumour（t(1−f)）、帶突變的 tumour（t·f），再對 `get_major_cn_prior` 列出的 genotype 取 logsumexp（`data/pyclone.py` L325–345）。
3. node 的 `log_p` = 該 node 所有 SNV 表的和（`tree/tree_node.py` L35–50）。
4. node 的 `log_r` = `log_p` 加上 children 的 convolution（`compute_log_S`，`tree/utils.py`）。這一步實現「children 的 CCF 和 ≤ parent」。
5. 整棵樹的分數 = FSCRP prior＋outlier prior＋root 的 `log_r` 取 logsumexp（`tree/distributions.py` L137–149，`TreeJointDistribution.log_p`）。`log_p_one` 是 root CCF 固定為 1 的版本（L151–161）。
6. SMC kernel 與 Gibbs-MH 都用這兩個函數算權重（`smc/kernels/base.py` L73–79；`smc/swarm/tree_holder.py` L74；`mcmc/gibbs_mh.py` L60、L90）。

**關鍵限制**：步驟 1–2 只看「這個 SNV 自己的 CCF f」。所以只要新特徵能寫成「f 的函數」，就可以放進 grid，不用動樹的推理。

## 3. A1：HP 拆分計數＋haplotype CN

### 3.1 輸入

`data.tsv` 新增欄位（每個 SNV × sample 一列）：

| 欄位 | 意思 |
|---|---|
| `snv_hp` | SNV 在 HP1 或 HP2。由 alt read 的 HP tag 多數決定 |
| `ps_block` | SNV 所在的 phase block。HP1／HP2 的方向只在 block 內有意義 |
| `cn_hp1`、`cn_hp2` | 該 segment 在 tumour 中 HP1、HP2 的整數 CN（同一個 PS block 的方向） |
| `ref_hp1`、`alt_hp1`、`ref_hp2`、`alt_hp2` | phased read 的計數 |
| `ref_unphased`、`alt_unphased` | 沒有 HP tag 的 read |

舊欄位 `major_cn`、`minor_cn` 保留，用來相容。

### 3.2 emission

〔設計〕設 SNV 在 HP h，另一側是 h'。三群細胞與 PhyClone 相同，但 CN 分 HP 計算：

- normal：HP h 有 1 份，HP h' 有 1 份。
- 不帶突變的 tumour：HP h 有 `cn_h` 份，突變 0 份。
- 帶突變的 tumour：HP h 有 `cn_h` 份，其中 m 份帶突變，m ∈ {1, …, cn_h}。

HP h 上的期望 VAF：

```
VAF_h(f, m) = t·f·m / [ (1−t)·1 + t·cn_h ]
```

likelihood（m 取 logsumexp，prior 均等）：

```
L(f) = Σ_m π(m) · Bin(alt_h | ref_h+alt_h, VAF_h(f,m))      # 帶突變的那一側
            · Bin(alt_h' = 0 | ref_h'+alt_h', ε)             # 另一側只有定序錯誤
            · Bin(alt_u | ref_u+alt_u, VAF_total(f,m))       # unphased read 用原本的公式
```

### 3.3 和現在的差別

- **multiplicity 的上限從 major 變成 cn_h。** 例如 s1 在 HP1、`cn_hp1`=2 時 m ∈ {1,2}。若 SNV 在 HP2、`cn_hp2`=1，m 只能是 1。現在的 PhyClone 不知道 SNV 在哪一側，所以兩種情況都要列入（`pyclone.py` L332–343）。〔程式＋推論〕
- **分母只用該 HP 的 depth**，不受另一側 CN 影響。

### 3.4 限制

- A1 仍然假設所有 tumour cell 的 CN 相同，所以**解決不了 subclonal CN 與遺失**。那是 A2 的工作。
- 預期效果：只能減少 genotype 的模糊。對 P1 有幫助，但不足以單獨解決。〔推論〕

## 4. A2：subclonal haplotype CN 與 loss-aware emission

### 4.1 想法

單一樣本雖然不能直接看到 clone，但**看得到每個 segment 每條 HP 的 depth**。從 HP depth 可以算出「有多少比例的細胞改變了這條 HP 的 CN」。

例：seg D（cnLOH）在 S1 的期望 HP depth 比例：〔推論，由真值計算〕

- HP1 copies 的加權和 = 0.6＋0.04＋0.14×2＋0.04＋0.18×2 = 1.32
- HP2 copies 的加權和 = 0.6＋0.04＋0＋0.04＋0 = 0.68
- 所以 HP2 在 tumour 中被取代的細胞比例 φ = (1 − 0.68) ／ 0.40 = 0.80，正好等於 C2＋C4 的 CCF。

### 4.2 輸入

新增 `segments.tsv`（每個 segment × sample 一列）：

| 欄位 | 意思 |
|---|---|
| `segment_id`、`ps_block` | segment 與它所在的 phase block |
| `state_a_hp1`、`state_a_hp2` | 狀態 A 的 HP CN（通常是祖先狀態） |
| `state_b_hp1`、`state_b_hp2` | 狀態 B 的 HP CN |
| `phi` | tumour 中處於狀態 B 的細胞比例（0–1） |

`data.tsv` 新增 `segment_id`。

`phi` 的來源：模擬時用真值或加雜訊的真值。真實資料需要一個「HP-aware 的 subclonal CN caller」，目前還沒有決定用哪個工具，可能要自己寫（輸入 longphase 的 phased depth）。〔設計〕

### 4.3 emission

〔設計〕設 SNV 的 CCF 是 f，處於狀態 B 的細胞比例是 φ（已知）。兩群細胞的關係只有四種可能：

| 情境 | 關係 | 例子 |
|---|---|---|
| E1 | 狀態 B 的細胞 ⊂ 帶突變的細胞（CN 在 SNV 之後） | s1：gain 在 s1 之後；s9、s10：cnLOH 在 s9、s10 之後 |
| E2 | 帶突變的細胞 ⊂ 狀態 B 的細胞（SNV 在 CN 之後） | s8：gain 之後才出現 |
| E3 | 兩群不重疊（不同分支） | 一個分支的 SNV，另一個分支的 CN |
| E4 | 狀態 B 不影響這個 SNV 的 HP | SNV 在沒有改變的那一側 |

每個情境都有一個期望 VAF。它是 f、φ、`cn`、multiplicity 的函數。E1 的子情況要包含**遺失**：如果狀態 B 刪除了 SNV 所在的 copy，那麼 φ 那部分細胞不再帶突變，帶突變的比例變成 f − φ。

```
L(f) = logsumexp over 情境 e、multiplicity m:  log π(e) + log π(m|e) + log Bin(計數 | VAF_e,m(f, φ))
```

情境不可能成立時，該項為 −∞。例如 E1 需要 φ ≤ f，E2 需要 f ≤ φ。

### 4.4 為什麼能解決 P3

- **s10**（HP2，seg D，φ = 0.80）：E1 的遺失子情況給出「f = 1，帶突變的比例 = 1 − 0.80 = 0.20」。這和觀察到的 VAF 相符。所以 s10 的 likelihood 峰值會回到 f ≈ 1，被歸到 C1，不再進 C3。〔推論〕
- **s2**（HP2，seg B 在 C4 被刪除，φ = 0.45）：同理，f ≈ 1。〔推論〕
- **s1、s9**：E1 的「multiplicity 只在 φ 部分變 2」，期望 VAF 符合觀察值，CCF 不再被低估。truncal clone 的 CCF 回到約 1.0。它和 C2 的 0.80 拉開距離，所以 **P1 也可能改善**。〔推論〕

### 4.5 限制與風險

- **情境之間的一致性沒有被強制。** E1 表示「狀態 B 發生在這個 SNV 的子樹內」。同一個 segment 的所有 SNV 應該共用同一個 CN 事件位置，但 A2 讓每個 SNV 各自選情境。這是局部放寬。完整版要把 CN 事件放到樹的 node 上，見 §6。〔設計〕
- **φ 只能分辨一個 subclonal 狀態。** 一個 segment 有三種以上狀態時，要擴充成多個 φ。
- **假陽性遺失**：如果 φ 估錯，低 CCF 的真 SNV 可能被解釋成「f=1 加遺失」。π(遺失) 要給得小，並用模擬測試敏感度。

## 5. B：read 層級 SNV 共現

### 5.1 輸入

新增 `pairs.tsv`：同一個 PS block、同一條 HP、距離小於 read 長度的 SNV 對。

| 欄位 | 意思 |
|---|---|
| `mut_i`、`mut_j` | 兩個 SNV |
| `n11`、`n10`、`n01`、`n00` | 同時覆蓋兩個位置的 read 中，兩者都有／只有 i／只有 j／都沒有的數目 |

只收同一條 HP 的 SNV 對。不同 HP 的 SNV 本來就不會在同一條 read 上，沒有資訊。

### 5.2 關係與禁止格

| 樹上的關係 | 應該接近 0 的格 |
|---|---|
| i 和 j 在同一個 node | `n10`、`n01` |
| i 是 j 的祖先 | `n01`（有 j 必有 i） |
| j 是 i 的祖先 | `n10` |
| 不同分支 | `n11` |

### 5.3 接法

〔設計〕給每對 SNV 一個 pairwise 項：

```
log L_ij(rel) = Σ_{禁止格 k} log Bin(n_k | n_total, ε)  +  Σ_{允許格} 0
```

ε 是定序錯誤、phasing 錯誤、遺失造成的雜訊率。它可以設成參數，或從資料估計。

整棵樹的分數加上 `Σ_{pairs} log L_ij(rel(node_i, node_j))`。

### 5.4 要改的程式

〔程式＋設計〕

- `tree/distributions.py`：`TreeJointDistribution.log_p` 和 `log_p_one`（L137–161）都要加上 pairwise 項。
- `tree/tree.py`：需要一個「兩個 node 的祖先關係」查詢，並 cache 起來。
- `smc/swarm/tree_holder.py` L74：權重透過 `compute_log_p_and_log_p_one` 計算，會自動吃到新項。
- **proposal 不知道 pairwise 項。** SMC 的 proposal（`smc/kernels/`）只看 grid likelihood。只改 log_p 時，目標分布仍然正確，但效率會變差，可能要更多 particle。第二步再把 pairwise 項放進 proposal。〔推論〕
- 計算量：pairs 的數目大約和「每個 PS block 內同 HP、在 read 長度內的 SNV 數」的平方成正比。真實資料的 somatic SNV 密度低，預期 pairs 不多。要用 HCC1395 等實際資料確認。〔推論〕

### 5.5 為什麼能解決 P2、P1

- **P2**：s4（C2）和 s6（C3）同在 HP2、seg C。帶 s6 的 read 從不帶 s4（`n11` = 0，`n01` > 0）。所以 s6 不能在 s4 的子樹內，直線樹（C3 在 C4 之下，C4 帶 s4）被排除。〔推論〕
- **P1**：如果一對 C1 SNV 和 C2 SNV 同在一條 HP，`n10` > 0、`n01` = 0 表示它們是祖先關係，不是同一個 node，所以會阻止合併。〔推論〕
- **低 CCF 的弱點**：在 200× 的基線資料中，s6 的 alt read 只有個位數（設計圖 ② 中是 3 條）。證據的強度取決於 depth 和 SNV 密度，要測試它的下限。〔實測＋推論〕

## 6. 之後的完整版（不在第一階段）

- **CN 事件放到樹上。** 每個 segment 的 HP CN 變化指定給某一條邊，所有 SNV 的情境（E1–E4）由樹決定，不再各自選。這樣才能保證 §4.5 的一致性。這需要改 node 的狀態與 convolution，改動很大。〔設計〕
- **把 φ 一起推論**，不當作固定輸入。

## 7. 實驗計畫

### 7.1 模擬資料要先補的東西

`tools/hp_truth_tree_to_phyclone.py` 目前只輸出 PhyClone 的 8 個欄位。要新增：

1. HP 拆分計數、`snv_hp`、`cn_hp1`、`cn_hp2`、`ps_block`。（`draw_hp_truth_tree.py` 的 `simulate` 已經有這些計數的邏輯）
2. `segments.tsv`：真值 φ，以及加雜訊的 φ。
3. `pairs.tsv`：依 read 長度與 SNV 間距產生共現計數。真值設計要加入跨 clone、同 HP 的 SNV 對（例如一個 C1 SNV 和一個 C2 SNV 放在同一段、同一條 HP），才能測 P1。
4. phasing 雜訊：unphased 比例、switch error、block 方向翻轉。第一輪先用理想 phasing。

### 7.2 比較

同一份單一樣本資料，多個資料 seed（不只 MCMC seed）：

| 版本 | 內容 |
|---|---|
| base | 現在的 PhyClone（已有結果） |
| +A1 | HP 拆分 emission |
| +A1+A2 | 加 loss-aware emission |
| +B | 只加共現 |
| 全部 | A1＋A2＋B |

指標沿用 `tools/summarize_hp_truth_topologies.py`：clone 數、C1／C2 是否合併、直線樹比例、C2／C4 是否正確、s10／s2 的位置、outlier。

### 7.3 成功標準

- P1：C1／C2 合併的 posterior 比例 < 0.2。
- P2：直線樹的 posterior 比例 < 0.1。
- P3：s10、s2 多數歸到 C1，而且沒有假 clone。
- 對照組（s3–s8）不能變差。

上面的門檻是暫定的，要和老闆討論。

## 8. 待決定的問題

1. 真實資料的 φ 要怎麼來：找現成的 HP-aware subclonal CN 工具，還是自己寫？
2. PS block 很短時，一個 segment 會跨好幾個 block。block 之間的 HP 方向不一致，A1／A2 要怎麼合併？
3. 實作要改 submodule（另開 branch），還是在外面寫 wrapper，只替換 `to_likelihood_grid`？後者比較不會和上游衝突，但 B 一定要改 submodule。
4. ε（B 的雜訊率）與 π(遺失)（A2）的預設值。

## 9. 實作狀態與第一輪結果（2026-10-25）

實驗：[`lab_report/2026-10-25_hp_a1a2_vs_base/`](../../lab_report/2026-10-25_hp_a1a2_vs_base/README.md)。程式：`tools/phyclone_hp.py`（submodule 外的 wrapper）。

| 問題 | base | A1 | A2 |
|---|---|---|---|
| P1：C1／C2 合併 | 1.00 | 1.00 | 1.00（沒有改善） |
| P2：直線樹比例 | 0.38–0.44 | 0.34–0.45 | 0.43–0.47（沒有改善，符合預期） |
| P3：s10 在 C3 | 0.92–1.00 | 0.00–0.67，但出現假 clone（0.14–0.45） | **0.00–0.01** |
| P3：s10／s2 回到 truncal | 0／0.37–0.47 | 0／0.40–0.59 | **0.80–0.86／0.72–0.78** |

和設計不同、實作時才發現的事：

- **E2 的 multiplicity 必須固定為 1**（§4.3 原本寫成 1…`b_h`）。新的 SNV 只在一份 copy 上。〔實測：s8 的峰值從 0.25 回到約 0.45〕
- **不可行的 CCF 不能是 −inf。** PhyClone 的 Gibbs-MH 會產生 NaN。現在改成「最差可行值 − 10」。
- **遺失的 SNV 在 A2 下有兩個一樣高的峰**：E1（f≈1，遺失）與 E3（f≈1−φ，不同分支）。單一 SNV 無法分辨，要靠樹的結構。§4.4 原本預測「峰值會回到 f≈1」，這個說法要修正為「多出一個 f≈1 的峰」。
- **A1 不應單獨使用。** cnLOH 讓 dominant state 的 SNV 那一側 CN = 0，A1 會產生假 clone。
- **A2 沒有改善 P1。** §4.4 預測「P1 也可能改善」，但沒有成立。原因待查（FSCRP prior 與 likelihood 差的比較）。

下一步：加雜訊的 φ；不同的真值設計（含 CCF ≈ 1−φ 的真 clone，測 A2 的誤判風險）；實作 B 處理 P2 與 P1。

### 9.1 B 層（C4）第一輪結果（2026-10-25）

實驗：[`lab_report/2026-10-25_c4_pair_term_stress/`](../../lab_report/2026-10-25_c4_pair_term_stress/README.md)。程式：`tools/phyclone_pairs.py`，經 `tools/phyclone_hp.py --pairs` 開啟（submodule 外的 monkeypatch）。

- **P2 解決。** 直線樹比例從 0.39–0.48 降到 0.000–0.002，連實測密度（16 個合格 pair）也一樣。〔實測〕
- **P1 只部分改善。** ×10 密度下 C1／C2 不再合併（3 個 seed 中 2 個），但 base＋C4 改成 C2／C4 合併。只有 A2＋C4 的一個 seed 推出完整 4 clone 樹。C2 與 C4 的 SNV 在不同 HP，沒有 read 能區分它們。〔實測＋推論〕
- **§5.4 的預測修正。** 只改 `log_p` 不夠：chain 在 spawn 的子 process 裡跑，patch 要用 pool initializer 送進每個 worker。
- **§5.5 的「低 CCF 的弱點」沒有出現。** 少量 pair 就足以排除直線樹。但這是在沒有 phasing 誤差、ε = 0.01 的條件下。〔實測＋推論〕

下一步：ε 與 phasing 誤差的敏感度；在 40 個隨機真實樹上跑 C4。
