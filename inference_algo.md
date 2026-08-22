# HCC1395 Tumor Tree Inference Algorithm

更新日期：2026-08-21

> [!NOTE]
> 本文件只定義「如何從 active model 的 posterior 目標產生推理結果」。模型變數、觀測 likelihood、ASCAT purity、HP counts 與 CN-constrained latent multiplicity 見 [`model.md`](model.md)；canonical input 與 provenance 見 [`data.md`](data.md)；正式實驗矩陣、holdout 與 gate 見 [`experiment_workflow.md`](experiment_workflow.md)。

```yaml
document_id: inference_algo
document_type: inference_algorithm_specification
inference_family: Bayesian posterior inference
algorithm_id: phylowgs_inspired_tssb_mcmc
active_algorithm: phylowgs_inspired_finite_k_compound_mcmc
model_contract: model.md
data_contract: data.md
workflow_contract: experiment_workflow.md
implementation: inference/
```

## 1. 推理演算法的模組邊界

`Inference algorithm` 是上位概念，不限定必須使用 MCMC。它的責任是：

1. 讀取已通過 schema／QA 的 canonical model table。
2. 以 [`model.md`](model.md) 定義的 posterior target 為目標。
3. 對模型中的未知量或 latent state 做抽樣、最佳化或近似推理。
4. 輸出可供 workflow 做 convergence、posterior summary 與 predictive evaluation 的 artifact。

它不負責：

- 從 BAM、VCF 或 ASCAT 原始檔重建 canonical table。
- 自行重新估計 `rho_ASCAT` 或 major/minor CN；C++ loader 依 CN 建立 multiplicity candidate support，並由 observation emission 自動計算其 posterior responsibility。
- 把 PS block 加入 downstream likelihood、clone-assignment prior 或 topology constraint。
- 修改 model 的 observation likelihood 或偷偷使用 legacy `tumor_dna_fraction`、`multiplicity_posteriors`。

因此整體模組關係是：

```text
raw data / provenance
        ↓
canonical model table  ← data.md
        ↓
model posterior target ← model.md
        ↓
inference algorithm    ← this file
        ↓
posterior / summary artifacts
        ↓
workflow diagnostics and gates
```

## 2. 通用 inference contract

目前 active model 的 latent state 是：

```text
x = (T, eta, z)
T   = finite-K tree parents
eta = K 個 clone local masses，sum(eta)=1
phi = eta + descendants 的 local masses（由 T、eta 結構性推導）
z   = 每個 SNV 的 clone assignment
M_i = 每個 SNV 的 latent multiplicity；在 likelihood 中解析邊際化，並輸出 posterior responsibility
```

任何替代 inference algorithm 都必須清楚宣告：

- 使用哪一個 model posterior target。
- 需要哪些 canonical input columns 與固定 config。
- 哪些量是 sampled、optimized、integrated out 或 deterministic derived。
- 輸出是 posterior draws、MAP estimate、variational approximation 或其他結果型態。
- 如何保存 input hash、model version、algorithm name 與 config，讓結果可追溯。

目前 workflow 的 formal diagnostics 假設 active algorithm 能產生 posterior sample stream；若日後改用 MAP 或 Variational Inference，必須另定義對應的 uncertainty、convergence 與 holdout evaluation contract，不能直接把非 MCMC 輸出偽裝成 chain draws。

## 3. 目前 active algorithm

目前 C++ active sampler 使用有限 K 的 TSSB-shaped compound MCMC，並在每個 site emission 內採用 PhyloWGS-style 的 latent multiplicity marginalization。完整名稱是：

> **finite-K compound Metropolis-within-Gibbs MCMC with CN-constrained latent multiplicity inference**

它保留 PhyloWGS 的核心分工：用樹狀 local mass 產生 descendant-sum prevalence，讓 assignment／樹結構探索與 continuous mass 更新分開。這不是完整的無限 TSSB 實作；目前 K 仍由 workflow 的 `K=4/6/8` sensitivity 固定。

MCMC 在這裡是 posterior inference 的具體演算法類別；`compound` 表示每次 iteration 由多個不同 kernel 組成，而不是只使用一種 proposal。

### 3.1 Compound sweep

每次 iteration 執行一個 compound sweep：

1. **All-SNV assignment Gibbs sweep**：固定目前 `T, eta, phi`，對每個 SNV 直接從
   `P(z_i=v) ∝ eta_v × P_obs(D_i,H_i | phi_v,C_i,rho_ASCAT)`
   的 categorical distribution 抽樣。這取代原本「隨機換一個 clone 再 MH」的單點 assignment move。
2. **Local-mass independence Metropolis-Hastings update**：依目前 tree 的 depth/width TSSB-shaped Dirichlet prior，加上各 clone 的 assignment counts 產生 `eta` proposal；emission 改變仍以 MH posterior ratio 校正。`eta` 是 local clone mass，不是 purity、normal fraction 或額外的 assignment `pi`。
3. **Conditional subtree prune-and-regraft Gibbs update**：選一個 clone node，保留其 descendants 的 subtree，列舉所有不會形成 cycle 的合法 parent，依完整 posterior score 抽樣。這是 finite-K 的 topology conditional update，與舊版 uniform parent-reassignment MH 不同。

這三個 kernel 合在一起，形成目前的 compound Metropolis-within-Gibbs 結構：Gibbs kernel 更新 discrete latent assignment／topology，MH kernel 更新 continuous local mass。

### 3.2 `eta` independence-MH implementation audit

設計上，`eta` proposal 是固定 `T` 與 assignment occupancy 後的 TSSB-shaped Dirichlet independence proposal。對非對稱的 independence proposal，完整的 MH acceptance ratio 應包含：

```text
log α = log π(eta_new) - log π(eta_old)
        + log q(eta_old) - log q(eta_new)
```

目前 C++ implementation (`inference/src/algorithm.cpp`) 的實際接受判斷使用 `eta_result.score - current_score`，source 中尚未看到明確的 `log q(eta_old) - log q(eta_new)` 項。因為 Dirichlet proposal 一般不是對稱 proposal，這是目前 inference correctness audit 的 blocker：

- 結構上仍可描述為 compound MCMC，因為每輪確實執行 assignment、`eta` 與 topology 三個 state update。
- 在 Hastings ratio 補齊或完成數學驗證前，不應把目前 formal output 宣稱為已驗證的 exact posterior MCMC 結果。
- 這不是 canonical input 的問題，也不是 `rho_ASCAT`、PS 或 multiplicity input 的問題；它是 `eta` proposal kernel 的 inference implementation 問題。

目前文件保留 algorithm identity 與實際 source 行為分開記錄，待修正或驗證後再將 audit note 關閉。

### 3.3 一條 chain 的輸入

`inference/` 的 C++ backend 只讀 validated `canonical likelihood_input.tsv.gz` 與一份 `ChainConfig`：

| 輸入 | 內容 |
|---|---|
| canonical table | 每列一個 eligible SNV：site key、bulk counts、四個 HP counts、ASCAT major/minor/total CN、`rho_ASCAT`、eligibility flags；loader 再由 major/minor CN 內部建立 multiplicity support／weights |
| `ChainConfig` | `seed`、finite `num_nodes`、`iterations`、`burnin`、`thin`、程式設定欄位 `purity`（對應模型的 `rho_ASCAT`）與 `checkpoint_every` |
| workflow control | 可選 `exclude_ids`（holdout）；這不是新的 biological model parameter。C++ backend 對未完成 chain 的 `resume` 目前 fail-closed |

PS 不需再作為 downstream table 欄位傳入 sampler。它已在上游 LongPhase-S tagging 中協助產生一致的 HP labels，對 sampler 的可見效果只透過 canonical table 的 `H_i` counts 傳遞。

### 3.4 一條 chain 的輸出

- `samples.jsonl.gz`：burn-in 後每個 retained draw 的 `log_posterior`、`parents`、`eta`、`phi`、`occupancy`；assignment 以 posterior summary 與 representative tree 彙整。
- `checkpoint.json.gz`：iteration、目前 `(T, eta, z)`、random-generator state、retained draws、canonical table hash 與 ChainConfig 的 audit/state snapshot；目前不宣稱可由 C++ restore。
- `multiplicity_posterior.tsv.gz`：每個 SNV 的 candidate multiplicity、CN prior 與 retained draws 平均 posterior responsibility；這是模型輸出，不是 canonical input。
- `diagnostics.json`：input/schema/hash、chain config、proposal counters、acceptance rates、posterior sample 摘要、multiplicity posterior artifact 與 PS 的 upstream/holdout role。
- `representative_tree.json`：由 retained draws 選出的代表 tree、best sample 及每個 SNV 的 assignment aggregate/MAP node。
- `chain_complete.json`：完成狀態與已發布 artifact 清單；只有 chain 完整寫出後才存在。

### 3.5 單條 chain 與外層 convergence

單條 chain sampler 只產生一個 posterior sample stream，不自行宣稱收斂。workflow 另外用相同 canonical table/config 啟動多條不同 seed 的獨立 compound-MCMC chains，再由外層 diagnostics 計算 R-hat、bulk/tail ESS、label-invariant assignment agreement、edge support 與 holdout predictive metrics。

這些 convergence checks 是 workflow 層，不是 MCMC kernel 的輸入或內部更新。PS-grouped、chromosome-grouped 與 ASCAT-segment-grouped holdout 也是 workflow evaluation design，不是 topology likelihood constraint。

## 4. 可替換的 algorithm backend

`inference/` 以 `Algorithm` interface 與 `AlgorithmRegistry` 保留替換點：

```text
CanonicalTable loader  ->  AlgorithmRegistry  ->  Algorithm::run
        |                         |
        +-- immutable sites       +-- phylowgs_inspired_tssb_mcmc
                                  +-- future algorithms
```

目前 implementation 的並行化邊界是：

- 每條 chain 擁有獨立的 random generator、latent state、output directory 與 counters；不同 seed 的 chains 可平行執行。
- likelihood scorer 對 independent SNV rows 做 site-level parallel scoring。
- 最終 state score 按 site order reduction，確保相同 chain config 下 `--threads 1` 與 `--threads 2` 可重現。
- topology、assignment 與 `eta` 更新仍由單條 chain 的狀態轉移順序定義，不能把同一 chain 的有依賴 iteration 任意平行化。

若未來改成 Variational Inference、MAP optimization、Sequential Monte Carlo 或其他 Bayesian inference method，仍可稱為 `inference algorithm`；但必須另外實作其 state、update／optimization rule、uncertainty artifact 與 diagnostics contract。

## 5. 實驗設定的責任分配

- `model.md`：定義 posterior target、觀測 likelihood、latent quantities 與 structural derivation。
- `data.md`：定義 raw source、canonical table、欄位與 provenance。
- 本文件：定義 inference algorithm、state transition、chain input/output 與 backend abstraction。
- `experiment_workflow.md`：定義 smoke、pilot、formal、K／purity sensitivity、holdout、convergence gates、run records 與 fail-closed 行為。

目前正式長鏈與 gate 數值以 workflow 為準，不在本文件複製另一份可漂移的設定。

## 6. 與原始 PhyloWGS 的關係與限制

本版採用 PhyloWGS 的核心思想：CN 約束的 latent mutation-copy state 不由外部表格指定，而是在 clone prevalence、CN 與 read-count emission 下被自動評估，再對候選 state 邊際化。原始 PhyloWGS 另外使用 CNV cellular prevalence、CNV event/tree placement、SNV-CNV timing 與更完整的 TSSB slice／stick 更新；目前 canonical schema 沒有那些欄位，因此本版不會假裝已取得這些未提供的資訊。

目前限制：

1. finite `K` 是模型容量，不是真實 clone 數；由 workflow 比較 `K=4,6,8`。
2. 單條 chain 的 acceptance／change rate 只描述 kernel 更新行為，不是 convergence proof。
3. 多條 chain 的 R-hat、ESS、assignment agreement、edge support 與 predictive metrics 是外層 workflow evidence，不是單條 sampler 自動保證的性質。
4. C++ backend 目前對失敗／中斷 chain 不支援原地 restore；正式流程須建立新的 output directory。
5. `multiplicity_posterior.tsv.gz` 是在每個 retained tree／assignment state 下計算的 emission responsibility 平均值；它不是 ASCAT 直接量測的 SNV-level truth，也不會回寫 canonical input。
