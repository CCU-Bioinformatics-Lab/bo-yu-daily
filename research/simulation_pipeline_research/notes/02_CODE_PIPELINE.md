# 02 程式實作的模擬流程

本檔記錄**程式的實際行為**〔程式〕。程式快照在 [`../phyclone_sim_code/`](../phyclone_sim_code/SOURCE.md)，版本是上游 commit `2738324`。行號指快照檔案。

## 1. 流程總覽

```text
fscrp.simulate_fscrp_tree(rng, alpha, dim, num_data_points)
 ├─ simulate_labels      CRP 分群：SNV m0..m{N-1} → cluster label
 ├─ simulate_tree        cluster → 節點，接成一棵樹（單一 root）
 ├─ add_clonal_prev      每個 sample 抽 Dirichlet(1,…,1) → clonal_prev
 └─ add_cellular_prev    post-order 累加 → cellular_prev（CCF）
                    │  nx.DiGraph；節點屬性 snvs、clonal_prev、cellular_prev
                    ▼
sim_data_on_tree.simulate_data(tree, rng, num_samples, depth, ...)
 每個節點 × 每個 SNV × 每個 sample：
 ├─ get_parental_copy_number   抽 total CN，再拆成 major／minor
 ├─ get_reference_genotype     g_r ∈ {g_n="AA", "A"×total}
 ├─ get_variant_genotypes      依 g_r 決定 g_v 候選，再隨機選一個
 ├─ simulate_counts            算 ξ，抽 alt ~ Binomial(depth, ξ)
 └─ get_major_cn_prior         推理端的 genotype prior（cn、mu、log_pi）
 → SampleDataPoint → PyCloneDataPoint.to_likelihood_grid(dist, grid_size, precision)
 → 節點內所有 SNV 的 grid 相加 → DataPoint（節點層級）
                    ▼
寫回 tree 的節點屬性：converted_sample_dp（每個 sample 每個 SNV 的計數物件）、datapoint
```

`simulate_data` **不寫檔**。它只把結果寫進 networkx graph 的節點屬性。

## 2. 參數與預設值

| 函式 | 參數 | 預設 | 說明 |
|---|---|---|---|
| `simulate_fscrp_tree` | `alpha` | 1.0 | CRP concentration |
| | `dim` | 1 | sample 數 |
| | `num_data_points` | 20 | SNV 數 |
| | `forest` | False | 見 §4.6 |
| `simulate_data` | `depth` | 100 | 每個 SNV 每個 sample 的固定深度 |
| | `error_rate` | 1e-3 | 定序錯誤率 ε |
| | `min_cn`／`max_cn` | 1／6 | total CN 的均勻抽樣範圍 |
| | `min_minor_cn` | 0 | minor CN 下限 |
| | `tumour_content` | 1.0 | purity，所有 sample 相同 |
| | `dist` | `"beta-binomial"` | **只用在 likelihood grid**，不用在計數生成 |
| | `grid_size`／`precision` | 101／400 | CCF grid 點數；Beta-Binomial precision |

## 3. 各步驟細節

### 3.1 分群：`simulate_labels`（`fscrp.py:69`）

- 標準 CRP。第 i 個 SNV 依現有 cluster 大小或 α 決定加入哪一群。
- SNV 名稱是 `m{i}`。

### 3.2 建樹：`simulate_tree`（`fscrp.py:104`）

1. cluster 依 SNV 數**由小到大**排序。
2. 先放最小的 cluster。
3. 之後每加一個 cluster，就從目前的 root 中隨機選 0 到全部個，當它的 children。
4. 最後一個 cluster（最大的）收下所有剩下的 root，所以樹只有一個 root。

### 3.3 Prevalence：`add_clonal_prev`／`add_cellular_prev`（`fscrp.py:7`、`fscrp.py:14`）

- 每個 sample 獨立抽 `Dirichlet(1, …, 1)`，維度是節點數。
- cellular prevalence 用 post-order 累加。root 的 cellular prevalence 在每個 sample 都是 1。
- 沒有 dummy root。真實的 root 節點本身帶 SNV（clonal SNV）。

### 3.4 CN 與 genotype（`sim_data_on_tree.py:86` 起）

- `get_parental_copy_number`：total CN 從 `[min_cn, max_cn]` 均勻抽；再抽 `x ∈ [0, total)`，`minor = max(min_minor_cn, min(total−x, x))`，`major = total − minor`。
- normal genotype 固定為 `"AA"`（normal CN = 2）。
- `g_r` 從 `{"AA", "A"×total}` 中等機率選：
  - `g_r == "AA"`（突變在 CN 事件前）：`g_v` 的突變 allele 數是 `major` 或 `minor`（minor > 0 時）。
  - `g_r` 全 ref（突變在 CN 事件後）：`g_v` 只有 1 個突變 allele。
- 生成用的 genotype 是推理端 prior 支撐集的子集。推理端 `get_major_cn_prior` 允許 1 到 major 個突變 allele。

### 3.5 計數：`simulate_counts`（`sim_data_on_tree.py:121`）

- 依 S1.1 的公式算 ξ，`alt ~ Binomial(depth, ξ)`，`ref = depth − alt`。
- 深度固定，沒有變異。
- 計數用 **Binomial** 抽，但測試用 **Beta-Binomial**（precision 400）算 likelihood。

### 3.6 玩具資料：`simulate.py`

- `simulate_binomial_data(idx, n, p, rng)`：每個 sample 抽 `x ~ Binomial(n, p)`。
- likelihood 是 `Binomial(x | n, grid)`。`p` 直接當成 alt 機率，沒有 CN、purity、genotype。
- 只用在 exact enumeration 等小型測試。

## 4. 已驗證的行為與論文差異

### 4.1 樹形偏向：root 一定是最大的 cluster〔程式＋實測〕

- 由 §3.2 的建樹順序推得：parent 一定比 child 晚加入，所以 parent 的 SNV 數 ≥ child；最大的 cluster 一定是 root。
- 實測：`seed=1`、`alpha=1`、`dim=2`、`num_data_points=100`，2000 次中有 1867 棵樹的節點數 ≥ 3，**全部** root 是最大 cluster。
- 本機 `FS-CRP_Loss` 的 `loss_prop_0.0` 100 棵真值樹：100 棵 root 是最大 cluster；741 條邊全部 parent SNV 數 ≥ child。這支持 benchmark 資料用同一套建樹程式產生。〔本機資料〕
- 論文 S1.3 寫的是 Uniform forest prior。程式的生成分布和它不同。〔推論〕這會讓模擬資料偏向「clonal cluster 最大」的樹，可能高估方法在 root 判定上的表現。

### 4.2 CN 對每個 SNV、每個 sample 獨立抽〔程式＋本機資料〕

- `get_parental_copy_number` 在 sample 迴圈內呼叫。CN 沒有 segment，沒有 clone 特異性，也不在 sample 間共用。
- 本機 `FS-CRP_Loss/loss_prop_0.0_run0`：600 個 SNV **全部**在 8 個 sample 中出現 ≥ 2 種 major/minor 組合。
- 生物上，同一個 SNV 在同一 clone 的 multiplicity 不該隨 sample 改變。這是模擬簡化，不是真實腫瘤行為。〔推論〕

### 4.3 生成與推理的 emission 不完全一致〔程式〕

- 生成用 Binomial；測試的 likelihood 用 Beta-Binomial（precision 400）。
- 生成 genotype 只取 `{major, minor}` 個突變 allele；推理 prior 均勻分給 `1..major` 加「CN 後」一種。

### 4.4 沒有 dummy root〔程式〕

- 論文 S1.3 用 dummy root 連接 forest 的所有 root。程式直接產生單一 root 的樹，root 帶 SNV。

### 4.5 邊界條件：`min_cn=1` 且 `min_minor_cn=1` 會出錯〔程式；未執行〕

- total CN = 1 時，`minor = 1`、`major = 0`。`get_major_cn_prior` 遇到 `major < minor` 會丟 `MajorCopyNumberError`。

### 4.6 `forest=True` 不可用〔程式；未執行〕

- `forest=True` 時最後一步不強制收下所有 root，但函式結尾仍 `assert len(roots) == 1`。多 root 時會 assertion error。

### 4.7 repo 內沒有的生成程式〔程式〕

- mutation loss 步驟（FS-CRP Loss）。
- TSSB 樹生成。
- CN 擾動（Copy Number Error）。
- 把模擬結果寫成 PhyClone 輸入 TSV 的程式。本機 `FS-CRP_Loss` 的 `data.tsv` 有 `g_n`、`g_r`、`g_v`、`mu`、`ccf`、`error_rate` 欄，和 `simulate_data` 的內部變數同名。推測作者用的是本程式的擴充版，未公開。〔推論〕

## 5. 用模擬資料做的正確性測試

### 5.1 Marginalisation test：`tests/test_marginalisation.py`（補充 S2.3.2）

1. `simulate_fscrp_tree` 產生樹，`simulate_data` 產生計數。
2. 把 networkx 樹轉成 PhyClone `Tree`，算 grid 邊際化的 log p（含 tree prior）。
3. `run_importance_sampler` 用 Dirichlet 提案估同一棵樹的 likelihood，1,000,000 iterations。
4. 10 個 trial 的兩組 likelihood 做 permutation t-test，要求 p > 0.01。

測試設定：depth 1000、CN 固定 1/1（`min_cn=max_cn=2`、`min_minor_cn=1`）、tumour content 1.0、50 或 100 SNV、1 或 2 samples、Beta-Binomial precision 400、grid 101、固定 seed。

### 5.2 Exact enumeration test：`tests/test_pg_posterior.py`（補充 S2.3.1）

- 用 `simulate_binomial_data` 產生 1–3 個 data point。
- `exact_posterior.get_exact_posterior` 窮舉所有分群與樹，算真 posterior。
- 和 Particle Gibbs sampler 的樣本頻率比對。三種 kernel 各跑一次。

## 6. 最小使用範例

在已安裝 PhyClone 的環境中、submodule 根目錄執行：

```python
import numpy as np
from phyclone.tests.utilities.fscrp import simulate_fscrp_tree
from phyclone.tests.utilities.sim_data_on_tree import simulate_data

rng = np.random.default_rng(0)
tree = simulate_fscrp_tree(rng, alpha=1.0, dim=8, num_data_points=600)
simulate_data(tree, rng, num_samples=8, depth=1000, max_cn=6, min_cn=2, min_minor_cn=1, tumour_content=1.0)

for node in tree.nodes:
    for s, snv_dps in tree.nodes[node]["converted_sample_dp"].items():
        for snv, dp in snv_dps.items():
            ...  # dp 是 SampleDataPoint；計數在 dp.a（ref）、dp.b（alt）
```

上面的參數是從本機 `FS-CRP_Loss` 反推的值，見 [03 §2](03_BENCHMARK_DATASET_FORMAT.md)。
