# Pairtree 與 CONIPHER 的模擬資料生成程式

調查日期：2026-10-21。問題：PhyClone benchmark 用到的 Pairtree 與 CONIPHER 資料，有沒有公開、完整的生成程式？

## 結論

| 資料 | 生成程式 | 完整嗎 | 能逐筆重現作者資料嗎 |
|---|---|---|---|
| Pairtree（576 份） | `morrislab/pearsim` + `morrislab/pairtree/simulator/make_simulated_data.sh` | 是：從參數產生樹、read 數，並寫檔 | 否：記錄的種子沒有真的被使用。重跑 576 份，分布相同、數值不同〔實測〕 |
| CONIPHER Noise／No-Noise（各 150 份） | `zaccaria-lab/TRACERx_simulation_tool` | 是：產生樹、拷貝數、mutation loss、noise、read 數，並寫檔 | **是**：用 commit `8c8d173` 與記錄的種子，300／300 份的讀數逐 byte 相同〔實測〕 |
| Copy_Number_Error（450 份） | PhyClone 作者對 CONIPHER No-Noise 做的拷貝數擾動 | 否：擾動程式沒有公開 | 否 |
| FS-CRP、TSSB | PhyClone 作者 | 否（見 `../../../lab_report/2026-10-21_phyclone_sim_rerun/README.md` 與 01 §7） | 否 |

其他生成器（約 90 個工具）的總調查見 [`../simulator_survey_2026-10-24/README.md`](../simulator_survey_2026-10-24/README.md)。

本機副本：三個生成器 repo 已加為 submodule，放在 `../upstream/`，版本與要看的檔案見 [`../upstream/SOURCE.md`](../upstream/SOURCE.md)。

另外，三組資料轉成 PhyClone benchmark 的 `tree.json`、`data.tsv` 的轉換程式，在 PhyClone repo 裡都沒找到。Pairtree 與 CONIPHER 的轉換規則已從檔案反推出來。

重跑結果（2026-10-22）見 [`../../../lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md`](../../../lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md)。

## Pairtree

證據：

- PhyClone 論文 §2.4.1.3：「We used previously published data from Wintersinger et al. (2022)」，576 份。〔論文〕
- `morrislab/pairtree` 的 `simulator/make_simulated_data.sh`（repo 最新 commit `13e33dd`，2024-04-18）：參數網格 K {3,10,30,100} × S {1,3,10,30,100}（K≥30 時跳過 S<10）× T {50,200,1000} × 每群 SNV 數 {10,20,100} × 4 份，正好 576 份；`--alpha 0.1`。〔程式〕
- 該腳本呼叫 `~/work/pearsim/make_simulated_data.py`。`morrislab/pearsim` 是公開 repo，最後 push 是 2021-04-28，沒有授權檔。〔程式〕
- `pearsim/make_simulated_data.py` 有完整 CLI，會寫出 truth pickle、`params.json`、`.ssm` 輸入檔，以及選用的 `.npz`。〔程式〕
- 本機 576 份的檔名與 pickle 裡的 `args` 都和腳本一致，例如 `sim_K100_S100_T1000_M10000_G0_run1`，以及作者機器上的路徑 `/home/q/qmorris/jawinter/work/pairtree/scratch/inputs/sims.smallalpha.pairtree/`。〔實測〕

缺點：

- **種子沒有生效。** 程式沒收到 `--seed` 時，會產生一個種子存進輸出（例如 `seed = 1503064755`），但實際呼叫的是 `np.random.seed(args.seed)`，也就是 `np.random.seed(None)`。本機抽查 60 份，`args.seed` 都是 `None`。所以記錄的種子不能重現資料。〔程式＋實測〕
- 依賴 Pairtree 的 `lib/`，路徑寫死成 `~/work/pairtree/lib`。〔程式〕
- 沒有授權檔：可以讀，但不能直接複製進我們的 repo。

## CONIPHER

證據：

- PhyClone 論文 §2.4.1.4：「We used previously published data from Grigoriadis et al.」，用 dataset 1（noise）與 dataset 2（no-noise），各 150 份。〔論文〕
- 資料在 Zenodo `10.5281/zenodo.10048165`（2023-10-27）。`scripts.zip` 只有 4 個畫補充圖的 R 檔，讀 TRACERx421 的真實樹，不是模擬程式。dataset2 每份有 `sim/` 底下 7 個檔：`.tsv`、`_TX.tsv`、`_cloneprops.tsv`、`_treeedges.tsv`、`_events.tsv`、`_tree.png`、`_info.tsv`。〔實測〕
- `McGranahanLab/CONIPHER` 與 `CONIPHER-wrapper` 都只有建樹程式，沒有模擬程式。〔程式〕
- 生成器是 `zaccaria-lab/TRACERx_simulation_tool`（BSD-3，2022-04 建立，最後 push 2025-04-03）。用 GitHub 程式碼搜尋 `LTXSIM` 找到。Simone Zaccaria 是 CONIPHER 論文的共同作者。〔程式〕
  - README 的輸出檔名和 Zenodo 資料完全對得上。README 也寫明預設值就是用來 benchmark TRACERx 建樹工具的設定：每組 50 份，以 (3, 7) 分成三組 sample 數。〔程式〕
  - 程式有 mutation loss、noise、WGD、拷貝數 gain／loss，並把每份的參數與 `random_seed` 寫進 `_info.tsv`。例如 Zenodo 的 `LTXSIM001_info.tsv` 是 `random_seed 602`、`n_nodes 13`、`n_samples 3`。`simulate.py` 用 `np.random.seed(rs)`，種子會生效。〔程式＋實測〕

缺點：

- **輸入的病人摘要資料不一定是當時那份。** README 寫：附的資料是「randomly simulated dataset of patient summary genomic information」，等 TRACERx 資料公開才會換掉。`data/TRACERx_data.tsv` 在 2024-01-08 才加入。但 `_info.tsv` 已經記錄了每份抽出來的參數，所以重現時可以跳過這一步。〔程式〕
- **程式在資料產生後改過**：2023-11-07 Fix display output、2024-04-09 tx_conversion_fix 等。Zenodo 檔案的日期是 2022-06-16。用 `8c8d173`（模擬路徑和 2022-04-30 版相同）加上記錄的種子，300／300 份的讀數逐 byte 相同。沒有測最新版。〔實測〕
- **兩個輸入沒有記錄**：`coverage` 與 `prop_mutloss_positions`。兩者都能用搜尋找回，見重跑報告。〔實測〕
- 主要程式碼放在 Jupyter notebook（`scripts/make_tx_simulations.ipynb`）；README 指定 Python 3.9.5。

## 輸入與輸出比較（2026-10-24）

比較的版本是實際產生 PhyClone benchmark 資料的版本：Pairtree 是 `pearsim@0b9b249`，CONIPHER 是 `TRACERx_simulation_tool@8c8d173`。

一句話：Pairtree 只要幾個手動設定的數字，輸出 read 數；CONIPHER 從病人摘要表抽參數，輸出 read 數與 allele-specific CN。〔程式〕

兩者的流程相同：先抽真值樹，再從樹與 clone 比例算期望 VAF，最後抽 read 數。真值與定序資料在同一次執行中寫出。〔程式〕

### 輸入

| | Pairtree（`pearsim`） | CONIPHER（`TRACERx_simulation_tool`） |
|---|---|---|
| 給參數的方式 | CLI，用 `make_simulated_data.sh` 的網格 | `make_tx_simulations()` 從病人摘要表抽，再加上固定範圍 |
| 樹的大小 | `-K` clone 數 | `n_nodes`（Zenodo 實際是 8–29）〔實測〕 |
| sample 數 | `-S` | `n_samples`（從表抽） |
| SNV 數 | `-M` | `n_positions`（從表抽，>150） |
| depth | `-T`，每個位點相同 | `coverage`；DEPTH 用 Poisson 抽，和 CN 成比例 |
| clone 比例 | `--alpha`（Dirichlet，576 份用 0.1） | Dirichlet(1)，每個 sample 3–8 個 clone |
| purity | 沒有這個參數，隱含在 normal 的 eta 裡（1−eta_root） | `min/max_tumour_purity`，每個 sample 從 U(min, max) 抽 |
| CN | `-C`（576 份是 0；`omega_v` 固定 0.5，CN 不影響 read 數） | gain／loss 比例、truncal 比例、clonal／subclonal WGD |
| mutation loss | 沒有 | `prop_mutloss_positions`（loss_A／cnloh_A） |
| noise | `-G` garbage（576 份是 0） | `fract_noise`：一個假 cluster，CCF 隨機 |
| 種子 | `--seed`（作者沒有給，見上文） | `rs`（會生效，記錄在 `_info.tsv`） |

Zenodo 兩組 CONIPHER 資料（各 150 份 `_info.tsv`）的實際差別：Noise 的 `fract_noise` 是 0.05–0.10，`prop_mut_lost` 是 0.02–0.25；No-Noise 的這兩個參數全部是 0。所以 No-Noise 也沒有 mutation loss。〔實測〕

### 輸出

| | Pairtree | CONIPHER |
|---|---|---|
| 真值樹 | `.truth.pickle`／`.truth.npz`：`structure`（parent 向量）、`phi`、`eta` | `_treeedges.tsv`：Parent、Child、每條 edge 的 CNA／SNV／WGD 數 |
| 真值分群 | `.params.json`：`clusters` | `.tsv`：CLUSTER、TRUE_CCF、TRUE_DCF、MUT_CN、CN_A／CN_B |
| 真值 clone 比例 | pickle 的 `eta` | `_cloneprops.tsv`（含 normal） |
| 每個位點的事件 | 沒有 | `_events.tsv` |
| 給建樹工具的資料 | `.ssm`：var_reads、total_reads、var_read_prob（固定 0.5） | `_TX.tsv`：REF/VAR_COUNT、DEPTH、CLUSTER、COPY_NUMBER_A／B、ACF（purity）、PLOIDY、CHR/POS |
| 參數紀錄 | pickle 的 `args` | `_info.tsv`、`_tree.png` |

注意：`_TX.tsv` 的 COPY_NUMBER_A／B 是真值，沒有誤差。它是 tumour cell 的平均 fractional CN，所以會出現非整數值。`CLUSTER` 也是真值 cluster。〔程式〕

### 重點差異

- **CN 的影響**：Pairtree 的 VAF 只由 phi 決定（0.5·phi）。CONIPHER 的 VAF 受 allele-specific CN、WGD 與 mutation loss 影響。〔程式〕
- **樹形**：Pairtree 的 node 有 0.75 的機率接在前一個 node 下，樹偏線性。CONIPHER 先建隨機 binary tree，再隨機剪 leaf。〔程式〕
- **重現性**：CONIPHER 能逐 byte 重現作者資料，Pairtree 不能。〔實測〕
- **共同限制**：兩者都只輸出 count 層的資料，沒有 read、HP phasing，也沒有同 read 共現。〔程式〕

## CONIPHER 生成器的病人摘要表（2026-10-24）

### 摘要表不是必要輸入

`tx_simulation()`（`src/simulate.py`）直接收參數，不讀任何表。只有外層的 `make_tx_simulations()`（`src/make_simulation.py`）讀摘要表，路徑寫死成 `../data/simulated_TRACERx_data.tsv`。〔程式〕

| 函式 | 要摘要表嗎 | 用途 |
|---|---|---|
| `make_tx_simulations()` | 要 | 批次產生：從表抽參數，再呼叫 `tx_simulation()` |
| `tx_simulation()` | 不要 | 產生一份模擬 |

`tx_simulation()` 有 6 個必填參數：`patient_name`、`n_nodes`、`n_positions`、`n_samples`、`min_clones_per_sample`、`max_clones_per_sample`。其他參數都有預設值，例如 `coverage=400`、purity 0.7–0.9、`fract_noise=0`。〔程式〕

我們的重跑（`tools/conipher_sim_rerun.py`）用 `_info.tsv` 的參數直接呼叫 `tx_simulation()`，沒有讀摘要表，300 份照樣逐 byte 重現。〔實測〕

所以要產生我們自己的模擬，例如照 ONT 細胞株的 purity 與 depth 設定，直接給參數就可以。〔推論〕

最小呼叫範例：

```python
import sys; sys.path.append('src')
from simulate import tx_simulation

tx_simulation('MYSIM001', n_nodes=10, n_positions=500, n_samples=3,
              min_clones_per_sample=3, max_clones_per_sample=8,
              coverage=100, min_tumour_purity=0.4, max_tumour_purity=0.6,
              rs=1, output_directory='out')
```

### 摘要表的用途

README 說明它的目的是讓模擬接近真實病人：「uses genomic summary data for TRACERx patients to create realistic evolutionary simulations」。這套工具的預設值就是 benchmark CONIPHER 時用的設定。〔程式，README〕

摘要表在程式裡有兩個用途：〔程式〕

1. **抽參數**：coverage、purity 上下限、SNV 數、truncal 比例、gain／loss 比例、WGD 狀態都從表裡抽。
   - `prop_pos_gained` 與 `prop_pos_lost` 從同一個病人成對抽，所以兩者的相關性會保留。
   - 其他參數各自獨立抽，可能來自不同病人，所以彼此的相關性沒有保留。
2. **依 sample 數分組**：病人依 NSamples 以 (3, 7) 分成 3 組，每組 50 份。三組的 `n_nodes` 範圍分別是 [8,16)、[12,24)、[22,30)，所以 sample 越多，樹越大。

限制：

- repo 附的 `simulated_TRACERx_data.tsv`，依 README 是隨機產生的假資料。用 `8c8d173` 重跑時，「接近真實」只是設計意圖，沒有真正做到。〔程式〕
- 作者產生 Zenodo 資料時用的是哪一張表，沒有證據可以確認。不過 `_info.tsv` 已記錄每份抽到的參數，所以重現時不需要這張表。〔實測〕

## PhyClone 的 CONIPHER 資料怎麼來（2026-10-24）

結論：PhyClone 作者沒有自己跑生成器。他們拿 CONIPHER 論文（Grigoriadis 等人）發布在 Zenodo 的模擬結果，用一支沒有公開的程式轉成 PhyClone 格式。〔論文＋實測〕

```
病人摘要表 + 固定範圍
   │ make_tx_simulations() 抽參數
   ▼
tx_simulation()（Grigoriadis 等人執行）
   ▼
Zenodo 10048165：<name>/sim/ 的 7 個檔        ← 公開，可重現
   │ PhyClone 作者的轉換程式（沒有公開，規則由檔案反推）
   ▼
PhyClone benchmark：data_archive/<name>/{ground_truth, program_inputs, program_outputs}
```

| PhyClone 檔案 | 來源 | 轉換 |
|---|---|---|
| `ground_truth/<name>_treeedges.tsv` | `_treeedges.tsv` | 直接複製，逐 byte 相同 |
| `ground_truth/<name>_full_truth_with_mut_id.tsv` | `<name>.tsv` | 加一欄 `mutation_id = s<VAR_POS>`，列的順序被打亂 |
| `ground_truth/tree.json` | `_treeedges.tsv`、`<name>.tsv` | 去掉 normal root 的邊；刪掉沒有非 noise SNV 的 clone；加一個 `id -1` noise 節點 |
| `program_inputs/phyclone_outliers/data.tsv` | `<name>.tsv`（不是 `_TX.tsv`） | `major_cn`／`minor_cn` = round(max／min(CN_A, CN_B))；`tumour_content` = PURITY |
| `program_inputs/conipher/<name>_TX.tsv` | `_TX.tsv` | 給 CONIPHER 用 |

完整規則與驗證見 `../../../lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md` 的「PhyClone 轉換規則」。

轉換後要注意三點：

- **CN 被四捨五入**：fractional CN（例如 1.91、2.93）變成整數，subclonal CN 的資訊不見了。〔實測〕
- **purity 用真值**：`tumour_content` 是生成器的 purity 真值，不是估計值。〔實測〕
- **cluster 輸入不是真值**：`phyclone_outliers/clusters.tsv.gz` 和 `program_outputs/pyclone-vi/clusters.tsv.gz` 內容相同，No-Noise 與 Noise 都是 150／150。所以 PhyClone 吃的 cluster 是 PyClone-VI 的分群，不是生成器的真值 CLUSTER。例如 LTXSIM001（No-Noise）的真值樹有 13 個 node，PyClone-VI 只分出 8 群。〔實測，2026-10-24〕

Copy_Number_Error（450 份）不在這條路徑上。它是 PhyClone 作者自己在 No-Noise 資料上擾動 CN 做出來的，擾動程式沒有公開。

## 對我們的意義

- 三組公開生成器都只產生計數或 VAF 層的資料。都沒有 read、HP，也沒有同 read 共現。CONIPHER 的生成器有 allele-specific 拷貝數、真實位置與 purity 小於 1，最接近我們 long read 生成器需要的設計。〔推論〕
- 「在 X 範圍內沒找到」的範圍：PhyClone repo `2738324`、`morrislab/pairtree`、`morrislab/pearsim`、`McGranahanLab/CONIPHER`、`CONIPHER-wrapper`、Zenodo `10048165`、GitHub 程式碼搜尋 `LTXSIM`（2026-10-21）。CONIPHER 論文全文有付費牆，沒有讀到它的 Methods。

## TSSB（2026-10-22 調查，三個 subagent 加交叉核對）

**結論：PhyClone 的 TSSB 生成程式沒有公開，找不到「確定用過」的程式。**

證據：

- 論文與 bioRxiv 預印本（10.1101/2024.08.14.607069）只引用 Ghahramani et al. 2010，沒有程式連結，也沒有超參數。Data availability 只把 TSSB 資料指向作者自己的 Zenodo（10.5281/zenodo.13240566 → 14238235）。所以資料是作者自己產生的。〔論文＋推論〕
- Zenodo 只有 tar.gz 與 README，沒有腳本。〔程式〕
- Roth-Lab 30 個 repo、aroth85、elhurtado（第一作者 Emilia Hurtado）都沒有 TSSB 或 benchmark 生成 repo。PhyClone 4 個 branch 的 commit 也查不到 tssb、simulate、benchmark。〔程式〕
- 第三方 repo `GiulioSP/CPSC536project1` 的 README（第 64 行）寫：原論文的 benchmarking scripts「were not published」，是第一作者私下提供的。該 repo 只有評估程式，沒有生成程式。〔程式〕

本機資料鑑識（900 份）〔實測〕：

- 計數層和 `sim_data_on_tree.py::simulate_counts` 相同：depth 固定 1000、error 0.001、`mu = 0.5·ccf + 0.001·(1−ccf)` 900／900 成立、binomial 變異數約 1。但 CN 固定 1/1、genotype 全是 AA/AA/AB。
- 樹層不符合 FS-CRP：root 是最大群只有約 62–76%，parent ≥ child 只有 79–92%。node id 是 DFS 前序，兄弟中 id 小的群較大，符合 TSSB 依 stick 順序走訪。
- 94／900 棵樹的 clonal_prev 加總小於 1：沒拿到 SNV 的 node 被刪掉，但祖先的 prevalence 沒有重算。每棵樹至少 3 個 node，可能有「≥3 群」的過濾。〔推論〕
- Low 與 High 是同一套流程，但各自獨立抽樹；Low 不是 High 的子集。
- 腳本：scratchpad `tssb_forensics/`（未進 repo）。

候選（都只是 plausible，沒有直接證據）：

| 候選 | 能從 prior 抽樹 | 和本機資料的衝突 | 判斷 |
|---|---|---|---|
| `morrislab/phylowgs` `tssb.py`（GPL-3.0） | 可以（`find_node` 懶惰 break sticks） | 不產生計數；需要外加 `simulate_counts` | 樹層最可能的來源之一〔推論〕 |
| `junseonghwan/PhylEx` `simulation/`（C++，無授權檔；作者群含 Bouchard-Côté、Roth） | 可以（`SampleFromTssbPrior`） | depth 是 Poisson（`simul_data.cpp` 第 172 行），本機 depth 固定 1000 | 不是完整生成器；至多借用樹層〔程式＋推論〕 |
| `sharadmv/trees`（MIT） | 可以 | 和 Roth lab 無關聯 | 低 |
| Roth-Lab `pgfa_experiments`、`pgsm`、PyClone-VI `simulate_data.py` | 否（不是 TSSB） | — | 排除 |

最可能的情況：作者用某個 TSSB 實作抽樹與 SNV 分配，再接上 PhyClone 測試程式那套計數程式（CN 固定 1/1）。〔推論〕要取得原程式，只能向 Emilia Hurtado 或 Andrew Roth 索取。

## CONIPHER 真值 clone 過細（2026-10-24）

問題：CONIPHER 的真值樹常把 CCF 相近的 clone 分開，clone 數很多。這是模擬造成的嗎？

**結論：是，主要原因在模擬設計。** 真值樹的 clone 數（中位數 19）遠多於 bulk 資料能分出的群數。PhyClone 實際收到的 PyClone-VI 群數中位數只有 8。〔程式＋實測〕

### 原因

1. **樹的大小和 SNV 數無關。** `n_nodes`（8–29）先決定，SNV 再隨機分到各邊，`minimum_branch_length` 預設 1。所以有 33% 的 clone 只新增 ≤ 5 個 SNV，太少，無法形成可辨識的 cluster。〔程式 `evolution.py`＋實測〕
2. **每個 sample 只抽 3–8 個 clone 給比例。** 其他 clone 在該 sample 的比例是 0（`src/sequencing.py` L28–62，`np.random.choice` 加 `dirichlet.rvs`）。〔程式〕
   - 16% 的 clone 在所有 sample 的比例都是 0，只是中間 node。〔實測〕
   - 這種 node 若只有一個 child，它在每個 sample 的 CCF 都和 child 相同。9% 的 clone 和 parent 的 CCF 完全相同；容許差 0.1 時是 18%。〔實測〕
3. **單一 sample 看起來更像。** 例如 LTXSIM114 的 C42→C43→C44→C45→C46 在 S1 的 CCF 都是 0.21。它們在其他 sample 的 CCF 不完全相同，所以理論上可分。但它們各只帶 2、3、1、7、1 個 SNV。〔實測，見 `lab_report/2026-10-24_sim_truth_tree_comparison/tree_CONIPHER.png`〕

### 影響

- 只把 CCF 相同的 clone 合併，群數只從 19 降到 16。所以「分不開」主要不是 CCF 完全重疊，而是 SNV 太少的 clone 太多。〔實測〕
- PhyClone benchmark 的 `tree.json` 只刪掉「沒有非 noise SNV」的 clone。1 個 SNV 的 clone 仍留在真值裡。〔實測，見上文「PhyClone 的 CONIPHER 資料怎麼來」〕
- PhyClone 用 PyClone-VI 的群（中位數 8）當輸入，不可能重建出 19 個 clone。所以這組 benchmark 的 topology 分數有上限，而且這個上限來自真值定義，不是建樹方法本身。〔推論〕

### 建議〔推論〕

- 評估時另外報告「可辨識真值」：先合併 CCF 向量相同的 clone，再把新增 SNV 少於門檻（例如 5）的 clone 併入 parent，然後才算分數。
- 我們自己的生成器要設定每個 clone 的最少 SNV 數，並讓每個非 root clone 至少在一個 sample 有不同的 CCF。

重現：`python3 tools/conipher_clone_resolvability.py`。
