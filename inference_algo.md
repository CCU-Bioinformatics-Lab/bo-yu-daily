# HCC1395 Tumor Tree Inference Algorithm

更新日期：2026-08-23

> [!NOTE]
> 本文件只定義「如何從 active model 的 posterior 目標產生推理結果」。模型變數、觀測 likelihood、ASCAT purity、HP counts 與 CN-constrained latent multiplicity 見 [`model.md`](model.md)；canonical input 與 provenance 見 [`data.md`](data.md)；正式實驗矩陣、holdout 與 gate 見 [`experiment_workflow.md`](experiment_workflow.md)。

```yaml
document_id: inference_algo
document_type: inference_algorithm_specification
inference_family: Bayesian posterior inference
algorithm_id: phylowgs_inspired_tssb_mcmc
active_algorithm: phylowgs_inspired_finite_k_compound_mcmc
candidate_algorithm: rao_blackwellized_annealed_smc
candidate_status: specification_only_not_implemented_not_promoted
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

目前 workflow 的 formal diagnostics 假設 active algorithm 能產生 posterior sample stream；若日後改用 MAP、Variational Inference 或粒子方法，必須另定義對應的 uncertainty、convergence 與 holdout evaluation contract，不能把非 MCMC 輸出偽裝成 chain draws。

## 3. 目前 active algorithm

目前 C++ active sampler 使用固定 K 的 TSSB-shaped compound MCMC，並在每個 site emission 內採用 PhyloWGS-style 的 latent multiplicity marginalization。Model A primary emission 只使用 bulk counts、ASCAT static CN、固定 `rho_ASCAT=0.99` 與內部 multiplicity；HP counts 不進 active likelihood。完整名稱是：

> **finite-K compound Metropolis-within-Gibbs MCMC with CN-constrained latent multiplicity inference**

它保留 PhyloWGS 的核心分工：用樹狀 local mass 產生 descendant-sum prevalence，讓 assignment／樹結構探索與 continuous mass 更新分開。這不是完整的無限 TSSB 實作；目前 K 是固定的 candidate clone node 數，由 workflow 以 `K=6` 作主分析、`K=4/8` 作 sensitivity。structural root 恰有一個 tumor founder，所有其他 clone 都是 founder descendants；SNV 採 no-loss／infinite-sites inheritance，ASCAT CN 在 Model A 中是跨 clone 固定的 static-CN context。

MCMC 在這裡是 posterior inference 的具體演算法類別；`compound` 表示每次 iteration 由多個不同 kernel 組成，而不是只使用一種 proposal。

### 3.1 Compound sweep

每次 iteration 執行一個 compound sweep：

1. **All-SNV assignment Gibbs sweep**：固定目前 `T, eta, phi`，對每個 SNV 直接從
   `P(z_i=v) ∝ eta_v × P_bulk(D_i | phi_v,C_i,rho_ASCAT,e=0.005)`
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

目前 C++ implementation (`inference/src/algorithm.cpp`) 明確計算
`log q(eta_old) - log q(eta_new)`，並將它與 posterior score difference 一起放入接受判斷。這是 independence-MH 的完整 Hastings ratio；由於 proposal 在固定 tree 與 occupancy 下使用同一組 Dirichlet parameters，兩個 proposal density 在數學上相同時會抵消，但 source 仍保留正向／反向項，避免把 MH 更新誤寫成未校正的 Gibbs replacement。

### 3.3 一條 chain 的輸入

`inference/` 的 C++ backend 只讀 validated `canonical likelihood_input.tsv.gz` 與一份 `ChainConfig`：

| 輸入 | 內容 |
|---|---|
| canonical table | 每列一個 eligible SNV：site key、bulk counts、四個 schema-required HP counts、ASCAT major/minor/total CN、`rho_ASCAT`、eligibility flags；HP counts 由 loader 驗證但 Model A scorer 不讀取；loader 再由 major/minor CN 內部建立 multiplicity support／weights |
| `ChainConfig` | `seed`、finite `num_nodes`、`iterations`、`burnin`、`thin`、程式設定欄位 `purity`（對應模型的 `rho_ASCAT`）與 `checkpoint_every` |
| workflow control | 可選 `exclude_ids`（holdout）；這不是新的 biological model parameter。C++ backend 對未完成 chain 的 `resume` 目前 fail-closed |

PS 不需作為 downstream table 欄位傳入 sampler。它在上游 LongPhase-S tagging 中協助產生 supplementary HP labels/counts；Model A scorer 不使用這些 counts。只有未來 Model B 定義並驗證 HP generative likelihood 後，HP/PS 才能影響 posterior。

### 3.4 一條 chain 的輸出

- `samples.jsonl.gz`：burn-in 後每個 retained draw 的 `log_posterior`、`parents`、`eta`、`phi`、`occupancy`；assignment 以 posterior summary 與 representative tree 彙整。
- `checkpoint.json.gz`：iteration、目前 `(T, eta, z)`、random-generator state、retained draws、canonical table hash 與 ChainConfig 的 audit/state snapshot；目前不宣稱可由 C++ restore。
- `multiplicity_posterior.tsv.gz`：每個 SNV 的 candidate multiplicity、CN prior 與 retained draws 平均 posterior responsibility；這是模型輸出，不是 canonical input。
- `posterior_summary.tsv.gz`：每個 candidate clone 的 CCF/`phi` posterior median、2.5% quantile 與 97.5% quantile。
- `topology_summary.tsv`：每個 retained tree 先做 clone-label canonicalization 後的 parent-child edge support；跨 chain/K 的比較由 workflow 彙整。
- `diagnostics.json`：input/schema/hash、chain config、proposal counters、acceptance rates、posterior sample 摘要、multiplicity posterior artifact 與 PS 的 upstream/holdout role。
- `representative_tree.json`：由 retained draws 選出的代表 tree、best sample 及每個 SNV 的 assignment aggregate/MAP node。
- `chain_complete.json`：完成狀態與已發布 artifact 清單；只有 chain 完整寫出後才存在。

### 3.5 單條 chain 與外層 convergence

單條 chain sampler 只產生一個 posterior sample stream，不自行宣稱收斂。workflow 另外用相同 canonical table/config 啟動多條不同 seed 的獨立 compound-MCMC chains，再由外層 diagnostics 計算 R-hat、bulk/tail ESS、label-invariant assignment agreement、edge support、CCF median/95% interval 與 holdout predictive metrics；並先做 prior predictive tree checks、再做 Model A posterior predictive checks。edge/topology summary 必須對 clone labels 做 canonicalization。

這些 convergence checks 是 workflow 層，不是 MCMC kernel 的輸入或內部更新。PS-grouped、chromosome-grouped 與 ASCAT-segment-grouped holdout 也是 workflow evaluation design，不是 topology likelihood constraint。

## 4. Candidate algorithm：Rao–Blackwellized annealed SMC

下一個候選 backend 定義為：

> **Rao–Blackwellized annealed Sequential Monte Carlo with topology and clone-mass rejuvenation**

algorithm ID 是 `rao_blackwellized_annealed_smc`。它目前只有規格，尚未實作、尚未通過測試，也尚未取代第 3 節的 active compound MCMC。這個候選演算法不改變 [`data.md`](data.md) 的 canonical input，也不改變 [`model.md`](model.md) 的 posterior target；它只改變如何計算同一個 posterior。

選擇 SMC 的原因是目前 posterior 同時包含離散 tree topology 與連續 clone mass，而且 single-bulk tree posterior 可能具有彼此分離的 topology modes。純 NUTS 不能直接更新離散樹；mean-field ADVI 也不適合拿來代表多峰 topology uncertainty。Annealed SMC 以一群可平行化 particles 從 prior 逐步走到完整 posterior，並在每個溫度階段以合法的 MCMC kernel 恢復粒子多樣性。

### 4.1 Particle state 與精確邊際化

每個 particle 只保存：

```text
x = (T, eta)
T   = fixed-K、single-founder clone tree
eta = K 個 clone 的 positive local masses，sum(eta)=1
phi = 由 T 與 eta 做 descendant sum 的 deterministic CCF
```

`z_i` 與 `M_i` 仍是 [`model.md`](model.md) 定義的 latent quantities，但 candidate SMC 不把它們放進 particle state。對每個 SNV `i`、clone `v` 與 multiplicity `m`，先定義：

```text
L_i(v,m | T,eta)
  = eta_v
    * P_M,i(m | C_i)
    * P_bulk(D_i | phi_v, C_i, m, rho_ASCAT, e=0.005)
```

site likelihood 精確加總所有候選 clone 與 multiplicity：

```text
L_i(T,eta) = sum_v sum_m L_i(v,m | T,eta)
```

因此 SMC 的 marginal posterior target 是：

```text
P(T,eta | D,C,rho_ASCAT)
  proportional to
P_K(T) * Dirichlet(eta | alpha(T)) * product_i L_i(T,eta)
```

每個保留 particle 同時計算 joint responsibility：

```text
R_i(v,m)
  = L_i(v,m | T,eta) / L_i(T,eta)
```

最後依 particle posterior weights 加權平均：

```text
P(z_i=v | data) = sum_m E_particles[R_i(v,m)]
P(M_i=m | data) = sum_v E_particles[R_i(v,m)]
```

這是 Rao–Blackwellization：不逐一抽樣數萬個 `z_i`，也不抽樣 `M_i`，但仍輸出完整的 SNV assignment posterior 與 multiplicity posterior。bulk counts 仍只在同一個 joint site likelihood 使用一次。

### 4.2 Adaptive likelihood annealing

SMC 使用 likelihood tempering path：

```text
pi_beta(T,eta)
  proportional to
P_K(T) * Dirichlet(eta | alpha(T))
  * product_i L_i(T,eta)^beta

beta = 0  -> prior
beta = 1  -> full posterior
```

只 temper likelihood，不 temper tree prior 或 `eta` prior。下一個 `beta` 由目前粒子的 log-likelihood 自動求得，使 conditional ESS 目標維持在 `0.8 * particle_count` 左右；當 weighted particle ESS 低於 `0.5 * particle_count` 時使用 systematic resampling。所有 `beta`、ESS、incremental log weights、resampling decisions 與 normalizing-constant estimates 都必須寫入 diagnostics。

預定的 staged particle budget 是：

| 階段 | 粒子設定 | 用途 |
|---|---:|---|
| smoke | 64 | 20-site fixture、I/O 與 checkpoint contract |
| pilot | 256 | 校準執行時間、proposal 與 SMC gate |
| formal | 1,024 × 4 independent repeats | 主設定 `K=6`, `rho_ASCAT=0.99` |

只有主設定通過後，才執行 `K=4/8` 與 purity sensitivity。正式粒子數與 gate 必須在 formal run 前鎖定，不能看過 formal 結果後再修改及格線。

### 4.3 Clone-mass rejuvenation

`eta` 不使用目前忽略 likelihood geometry 的 Dirichlet independence proposal，也不把 NUTS 直接塞進 production C++。每個 annealing stage 先把 simplex 轉成 additive-log-ratio coordinates：

```text
y_j = log(eta_j / eta_K),  j=1,...,K-1
```

由該 stage 的 weighted particles 估計 regularized covariance，接著在 stage 內固定 covariance，使用 adaptive Gaussian random-walk MH：

```text
y_new = y_old + Normal(0, scale^2 * Sigma_stage)
```

MH target 必須包含從 `y` 轉回 simplex `eta` 的 Jacobian；proposal covariance 與 scale 一旦進入該 stage 的 rejuvenation 就固定，不能在單次接受判斷中依 proposal 結果改變。acceptance、scale、covariance regularization 與每個 ALR coordinate 的移動幅度都寫入 diagnostics。

PyMC 只作小型 reference implementation：固定 topology、synthetic fixture 與少量 SNV 下，對照 C++ 的 log target、joint responsibilities 與 posterior summaries。PyMC 不作 HCC1395 production backend，也不成為正式 workflow 的 runtime dependency。

### 4.4 Topology rejuvenation

Topology kernel 是兩種合法 proposal 的 mixture，pilot 起始設定為：

```text
80% local conditional subtree prune-and-regraft
20% global legal single-founder tree proposal
```

- local kernel：選一個 node，保留其 descendants，列舉不形成 cycle 且符合 exactly-one-founder 的 parent support，再依 tempered target 做 conditional draw。
- global kernel：由合法 single-founder tree prior 提出較大 topology jump，使用完整 forward/reverse proposal density 做 MH correction。

兩種比例都屬於 algorithm config，必須保存於 run manifest。不能把 topology change rate 稱為 acceptance proof；正式判讀仍依 particle diversity、跨 repeat edge support 與 predictive evaluation。

### 4.5 Adaptive rejuvenation stop

每個 annealing stage 在 resampling 後至少執行 3 個 compound rejuvenation sweeps，最多 20 個。每個 sweep 包含 clone-mass update 與 topology update。是否提早停止由以下資訊共同決定：

- resampling 前後／rejuvenation 前後的 ALR-`eta` particle correlation；
- topology change rate 與 unique canonical topology count；
- `eta` proposal acceptance；
- duplicated-particle ancestry 是否已被有效打散。

確切 decorrelation 門檻先由 synthetic recovery 與 256-particle pilot 校準，並在 formal run 前寫入 immutable config。diagnostics 必須記錄每個 stage 的 sweep 數與停止原因，不能只輸出最後平均 acceptance。

### 4.6 Output contract 與 representative tree

核心輸出檔名維持不變：

- `samples.jsonl.gz`：最終經等權重 resampling 的 posterior particles；每列明確標記 `sample_kind=smc_particle`，不得描述成 MCMC chain draw。
- `multiplicity_posterior.tsv.gz`：對 joint responsibilities 先加總 clone、再對 particles 平均所得的 multiplicity posterior。
- `posterior_summary.tsv.gz`：particle-weighted CCF median、2.5% 與 97.5% quantile。
- `topology_summary.tsv`：canonical topology／edge 的 particle-weighted posterior support。
- `representative_tree.json`：posterior weight 總和最高的 canonical topology class；在該 class 中選擇最接近 weighted CCF median 的 particle 作代表，不使用單一最高 log-posterior particle。
- `diagnostics.json`：algorithm ID、particle count、independent repeat、annealing、ESS、resampling、rejuvenation、predictive 與 input hash。
- `checkpoint.json.gz`、`chain_complete.json`：名稱暫時為相容既有 workflow 而保留，但內容必須標示 SMC stage／particle semantics。

新增的 supplementary audit artifact：

- `particle_history.jsonl.gz`：保存 annealing stage、particle weight、ancestor index、canonical topology、rejuvenation counters 與 RNG/checkpoint lineage；它不屬於生物模型輸出。

fixed K 的所有節點都保留在 raw posterior，不因 local mass 小或 assignment 少而從 particle 中刪除。summary 另外輸出 `expected_assigned_snv`、`local_mass_posterior` 與 `supported_clone`；人看的圖可以淡化低支持節點，但核心 tree artifact 不得事後剪枝。

### 4.7 Checkpoint 與 resume

每完成一個完整 annealing stage，就原子保存：

- particles `(T,eta)`；
- normalized／unnormalized weights 與 ancestor indices；
- 目前 `beta`、累積 normalizing-constant estimate；
- adaptive proposal state、run config、input hash；
- 每個 worker／repeat 的 RNG state。

resume 只可從最後一個完整、hash 與 config 完全一致的 stage 開始。checkpoint round-trip test 必須證明 uninterrupted run 與 interrupted/resumed run 產生相同 final artifacts；通過前不得執行昂貴 formal run。

### 4.8 SMC diagnostics 與 promotion gate

SMC 不使用 MCMC R-hat 或 chain ESS 作主要 gate。它必須報告：

- 每個 stage 的 conditional ESS、weighted particle ESS 與 particle diversity；
- `beta` progression、resampling 次數與 ancestor diversity；
- `eta`／topology rejuvenation acceptance、change 與 decorrelation；
- 四次 independent repeats 的 assignment、CCF 與 edge-support stability；
- posterior predictive、strict holdout coverage 與 predictive log score。

既有 assignment agreement `>=0.90`、max edge-support difference `<=0.10`、predictive coverage `0.85–0.95` 與 holdout score contract 先保留。新增的 particle-diversity、temperature、decorrelation 與 CCF-stability 門檻由 synthetic recovery 和 pilot 校準，再於 formal run 前預先登錄。

candidate backend 只有在以下條件全部通過後才能升為 active：

1. C++ 與 PyMC 小型 reference 的 log target、joint responsibilities 與 posterior summary 在預設 tolerance 內一致。
2. Synthetic topology、CCF、assignment 與 multiplicity recovery 通過。
3. 四次 independent pilot 的 assignment、edge support 與 CCF 穩定。
4. Posterior predictive 與 holdout gates 通過。
5. Checkpoint/resume round-trip 完全通過。
6. 新 SMC 的 predictive score 至少不差於舊 compound-MCMC diagnostic baseline。

在 promotion 前，第 3 節的 `phylowgs_inspired_finite_k_compound_mcmc` 仍是 active algorithm；candidate SMC 的任何輸出一律標記 `diagnostic-only`。

### 4.9 方法依據

- [PyMC sampler API](https://www.pymc.io/projects/docs/en/latest/api/samplers.html)：NUTS／HMC 用於連續 state；離散與連續 state 需要分開處理或組合 step methods。
- [PyMC Sequential Monte Carlo API](https://www.pymc.io/projects/docs/en/stable/api/smc.html)：SMC 與其 MH／IMH rejuvenation kernel 的官方介面背景。
- [Hoffman and Gelman, The No-U-Turn Sampler](https://arxiv.org/abs/1111.4246)：NUTS 避免 random-walk behavior 的方法背景；本 repo 僅用它作小型連續-state reference，不直接處理 topology。
- [Kelly et al., Adaptive Rao-Blackwellisation in Gibbs Sampling](https://proceedings.mlr.press/v89/kelly19a.html)：解析加總 latent variables 可降低 sampling variance 的方法背景。
- [`golden_tree/research/phylowgs_model_review.md`](golden_tree/research/phylowgs_model_review.md)：原始 PhyloWGS assignment、TSSB 與 continuous-mass 更新和本 repo 的差異。

## 5. 可替換的 algorithm backend

`inference/` 以 `Algorithm` interface 與 `AlgorithmRegistry` 保留替換點：

```text
CanonicalTable loader  ->  AlgorithmRegistry  ->  Algorithm::run
        |                         |
        +-- immutable sites       +-- phylowgs_inspired_tssb_mcmc
                                  +-- rao_blackwellized_annealed_smc (candidate)
                                  +-- future algorithms
```

目前 implementation 的並行化邊界是：

- 每條 chain 擁有獨立的 random generator、latent state、output directory 與 counters；不同 seed 的 chains 可平行執行。
- likelihood scorer 對 independent SNV rows 做 site-level parallel scoring。
- 最終 state score 按 site order reduction，確保相同 chain config 下 `--threads 1` 與 `--threads 2` 可重現。
- topology、assignment 與 `eta` 更新仍由單條 chain 的狀態轉移順序定義，不能把同一 chain 的有依賴 iteration 任意平行化。

若未來改成 Variational Inference、MAP optimization 或其他 Bayesian inference method，仍可稱為 `inference algorithm`；但必須另外實作其 state、update／optimization rule、uncertainty artifact 與 diagnostics contract。第 4 節的 SMC candidate 已先定義這些契約，但目前 registry 與 workflow 尚未實作。

## 6. 實驗設定的責任分配

- `model.md`：定義 posterior target、觀測 likelihood、latent quantities 與 structural derivation。
- `data.md`：定義 raw source、canonical table、欄位與 provenance。
- 本文件：定義 inference algorithm、state transition、chain input/output 與 backend abstraction。
- `experiment_workflow.md`：定義 smoke、pilot、formal、K／purity sensitivity、holdout、convergence gates、run records 與 fail-closed 行為。

目前正式長鏈與 gate 數值以 workflow 為準，不在本文件複製另一份可漂移的設定。

## 7. 與原始 PhyloWGS 的關係與限制

本版採用 PhyloWGS 的核心思想：CN 約束的 latent mutation-copy state 不由外部表格指定，而是在 clone prevalence、CN 與 read-count emission 下被自動評估，再對候選 state 邊際化。原始 PhyloWGS 另外使用 CNV cellular prevalence、CNV event/tree placement、SNV-CNV timing 與更完整的 TSSB slice／stick 更新；目前 canonical schema 沒有那些欄位，因此本版不會假裝已取得這些未提供的資訊。

目前限制：

1. finite `K` 是模型容量，不是真實 clone 數；由 workflow 比較 `K=4,6,8`。
2. 單條 chain 的 acceptance／change rate 只描述 kernel 更新行為，不是 convergence proof。
3. 多條 chain 的 R-hat、ESS、assignment agreement、edge support 與 predictive metrics 是外層 workflow evidence，不是單條 sampler 自動保證的性質。
4. C++ backend 目前對失敗／中斷 chain 不支援原地 restore；正式流程須建立新的 output directory。
5. `multiplicity_posterior.tsv.gz` 是在每個 retained tree／assignment state 下，以 Model A bulk/CN/purity emission 計算的 responsibility 平均值；它不是 ASCAT 直接量測的 SNV-level truth，也不會回寫 canonical input。
6. 在 C++ implementation、canonical input、tests 與 workflow gates 同步並通過前，所有結果都是 `diagnostic-only`；舊 schema artifact 不得進入 active backend。
