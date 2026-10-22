# 04 要產生 long read 特徵，還缺什麼

本檔比對「PhyClone 模擬器能給什麼」與「HP-aware 驗證需要什麼」。驗證層級（L0／L1／L1-B／L2）的定義與判定規則以 `plan.md` 為準，本檔不重寫。

## 1. 缺口總表

| 需要的生成能力 | PhyClone 模擬器現況 | 證據 | 要怎麼補 |
|---|---|---|---|
| SNV 落在哪條 haplotype（HP1／HP2） | 沒有 | 〔程式〕genotype 只用 A／B 字串，沒有 allele 身分 | 生成時先指定 SNV 的 haplotype，再決定 multiplicity |
| allele-specific CN 跟著 haplotype | 沒有。major／minor 不對應任何 haplotype | 〔程式〕 | CN 事件指定 clone、haplotype、segment |
| CN segment 結構 | 沒有。每個 SNV 獨立抽 CN | 〔程式＋本機資料〕[02 §4.2](02_CODE_PIPELINE.md) | 先產生 segment，再把 SNV 放進 segment |
| CN 跟著 clone 走、sample 間一致 | 沒有。每個 sample 重抽 CN | 同上 | CN 事件綁在樹的邊上，sample 只改 prevalence |
| CN timing（突變在 CN 前或後） | 有，但每個 sample 獨立隨機選 | 〔程式〕`g_r` 每次重抽 | timing 由樹上 SNV 與 CN 事件的先後決定 |
| subclonal CN | 沒有 | 〔程式〕CN 只套在 R、V 兩群，不分 clone | CN 事件放在非 root 的邊上 |
| purity < 1 | 有參數，但 benchmark 都用 1.0 | 〔論文 p.4–5；本機資料〕 | 掃 purity 格點 |
| read 共現（同一 read 跨多個 SNV） | 沒有。每個位點獨立抽 Binomial | 〔程式〕 | 依 `plan.md` §5.8.2 規則 4–6：每個 molecule 抽一個 lineage 與 haplotype |
| phasing 誤差（unphased、HP 錯標、phase switch） | 沒有 | 〔程式〕 | 依 `plan.md` §5.9.4 加 `r`、`a`、switch rate |
| 真實基因組座標、PS block | 沒有。`coord` 是序號 | 〔本機資料〕[03 §2.2](03_BENCHMARK_DATASET_FORMAT.md) | 依 `plan.md` §5.9.3 從 I02／I05 補 |
| 無偏的樹形 prior | 有偏：root 一定是最大 cluster | 〔程式＋實測〕[02 §4.1](02_CODE_PIPELINE.md) | 改成真正的 uniform forest，或把偏向當成一個情境明確標示 |
| 輸出 TSV 與真值檔 | 沒有寫檔程式 | 〔程式〕 | 輸出格式沿用 `FS-CRP_Loss` 的 `data.tsv`＋`tree.json`，另加 HP 與 pair 檔 |

## 2. 可以直接沿用的部分

- `fscrp.simulate_labels`：CRP 分群。
- `fscrp.add_clonal_prev`／`add_cellular_prev`：Dirichlet prevalence 與子樹累加。
- `sim_data_on_tree.simulate_counts`：三群混合的 ξ 公式。HP 版要把它拆成「每條 haplotype 的 copy 數 × lineage 比例」。
- `tree.json` 格式：沿用後，可以直接重用既有的 AD F-score／V-measure 評分程式（若之後取得）。
- `test_marginalisation.py` 的驗證思路：固定真樹，比對新 likelihood 與 importance sampler。HP likelihood 也可以用同樣方法驗證正確性。

## 3. 三種生成路線與本目錄的關係

| 路線 | 樹從哪來 | 計數從哪來 | 本目錄提供 |
|---|---|---|---|
| L1（計數層，自訂樹） | 自己的生成器（可沿用 `fscrp.py` 骨架） | 參數式生成 HP 計數與 pair | §1 缺口、§2 可沿用部分 |
| L1-B（計數層，借真值樹） | benchmark 的 `tree.json` | 保留原計數，補 HP 與 pair | [03](03_BENCHMARK_DATASET_FORMAT.md) 的真值格式與限制 |
| L2（read 層） | 自訂或 scDNA 參考樹 | spike-in 或 read simulator | 只提供 prevalence 與 CN 設計的參考 |

## 4. 待決定事項

- 樹形 prior：修正 `simulate_tree` 的偏向，或保留它以便和 `FS-CRP_Loss` 對照。建議兩種都產生，分開報告。〔推論〕
- 不同 HP 上的兩個 SNV 算不算祖孫關係：評分前要先定規則（`report/2026_10_21_slides/project/slides/s2-sim-plan.html` 也列為未決）。
- 生成器的語言與位置：建議 Python，放 `tools/`，沿用 PhyClone 的 numpy `Generator` 介面，方便重現 seed。
