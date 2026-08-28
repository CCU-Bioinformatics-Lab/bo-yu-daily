# Inference algorithm：Rao–Blackwellized annealed SMC

更新日期：2026-08-28

本文件描述目前真的會執行的推理後端；其 site emission 已同步採用
PhyClone/PyClone-VI-style `xi` target。
它和 [`model.md`](model.md) 分開：`model.md` 定義 posterior target 與觀測
likelihood；本文件定義如何從這個 target 找到腫瘤演化樹、clone-specific local fractions 與 CCF。

## 1. 目前固定設定

```yaml
algorithm_id: rao_blackwellized_annealed_smc
backend: C++17
input: validated hcc1395_tumor_tree_input/v4 canonical table
primary_purity: rho_ASCAT = 0.99
expected_vaf_model: phyclone_compatible_genotype_aware_xi
error_rate: 0.001
implementation_status: phyclone_xi_v1_synced_cpp_python
state: topology + eta
parallel_unit: independent SMC repeat / particle
```

目前 C++ 與 Python runtime 已執行以下 `xi`、`error_rate=0.001` 與 genotype
candidate marginalization；error rate 與正常 CN=2 是 model-side fixed assumptions，
不新增 canonical input 欄位。完整 posterior／predictive／formal gates 仍須另外通過。

`T` 是固定 K 個 clone 的樹拓樸；clone-specific local fraction 是只屬於該 clone、
不包含 descendants 的 tumor fraction，本文件以 $\eta_v$ 表示。由樹把各 clone
的 $\eta_v$ 加總後得到 $\phi_v$，也就是包含 descendants 的累積細胞比例
(CCF)。`K=6` 是主分析，
`K=4/8` 是 workflow 的敏感度設定。

每個 particle 只保存：

- 合法的單一 tumor founder tree topology；
- 一個正值且總和為 1 的 clone-specific local fraction simplex（各分量為
  $\eta_v$）。

SNV assignment 與 genotype candidate（包含 multiplicity）不另外塞進 particle state。
它們在每個 site 的 candidate-marginalized likelihood 中以 Rao–Blackwellization
邊際化，並在輸出時累積 posterior responsibility。
因此 model input 不需要 multiplicity 欄位，模型仍會產生
`multiplicity_posterior.tsv.gz`。

## 2. 為什麼選 SMC

目前 posterior 同時包含離散的樹拓樸與連續的 clone-specific local fractions，而且不同樹形可能形成
分開的 posterior mode。SMC 讓很多 particles 從簡單的 prior 一起出發，逐步增加
真實資料的影響；粒子可以平行計算，也能在有效粒子數下降時重抽樣，保留多個候選
拓樸，而不是只困在單一初始樹附近。

## 3. 實際推理流程

```text
canonical table
      │
      ▼
建立多個合法 tree + eta particles
      │
      ▼
beta: 0 ──逐步增加資料評分力量──▶ beta: 1
      │             │
      │             ├─ conditional ESS 決定下一個 beta
      │             ├─ weighted ESS 太低 → systematic resampling
      │             └─ topology / eta rejuvenation 恢復粒子多樣性
      ▼
等權重 posterior particles
      │
      ├─ CCF / phi
      ├─ topology edge support
      ├─ SNV clone assignment
      └─ multiplicity posterior
```

### 3.1 Annealing

`beta=0` 時，particle 只反映 prior；`beta=1` 時，完整使用 model likelihood。
每一階段都用 conditional ESS 選擇下一個 beta，避免一次加入太多資料而令權重
集中在少數 particles。

### 3.2 重抽樣與 rejuvenation

當 weighted ESS 低於設定比例，使用 systematic resampling 把高權重 particle
複製成新的 population，並記錄 ancestor diversity。

接著對每個 particle 做固定的 rejuvenation sweep：

- topology：在合法單一 founder tree 的候選 parent 中依條件 posterior 選擇；
- eta：以 prior-shaped Dirichlet proposal 更新 clone-specific local fractions
  （$\eta_v$），並以完整 target
  的 forward/reverse proposal ratio 判斷是否接受。

這些步驟是 SMC 的 particle rejuvenation kernel，不是另一個獨立的推理後端。

### 3.3 PhyClone-inspired 拓樸探索設定

本 repo 沒有直接複製 PhyClone 的 Particle Gibbs、forest construction 或 mutation
ordering；目前後端仍是 annealed SMC。吸收的是它對「拓樸容易卡在單一 mode」的實際
處理方式：每個 rejuvenation sweep 同時使用兩種合法樹提案。

- **local conditional SPR**：剪下某個非 founder clone 的整個子樹，依目前 target
  在可行 parent 中重新接回；這保留固定 K 與單一 tumor founder。
- **global legal-tree MH**：另外隨機產生一棵合法 fixed-K tree，以完整 posterior
  target 做 Metropolis–Hastings 接受判斷，讓 particle 有機會跨越局部拓樸 mode。

目前 C++ 預設每個 sweep 做 `global_topology_moves=1`，可用 CLI
`--global-topology-moves N` 調整。這是改善拓樸探索的可替換設定，不代表已經得到
PhyClone 的完整 Particle Gibbs 演算法，也不會自動讓低 ESS 變成通過。SNV assignment
與 multiplicity 仍維持 Rao–Blackwellization，不新增 data schema 欄位。

### 3.4 Rao–Blackwellization

對每個 SNV，target/spec 同時評估所有 clone-specific local fractions 與 CN 允許的 genotype candidates。
令 `CCF_i=phi_z(i)`、`t=rho_ASCAT` 暫作 tumour-content mapping，三個 population
weights 為：

```text
w_N = 1-t
w_R = t*(1-CCF_i)
w_V = t*CCF_i
```

candidate `g` 具有 `c_N/c_R/c_V` 與 `mu_N/mu_R/mu_V`，其 expected VAF 為：

```text
xi_i(g) =
  [w_N*c_N*mu_N + w_R*c_R*mu_R + w_V*c_V*mu_V]
  / [w_N*c_N + w_R*c_R + w_V*c_V]
```

`mu_g=clamp(a_g/c_g, error_rate, 1-error_rate)`，target/spec 固定
`error_rate=0.001`，且：

```text
ALT_i ~ Binomial(total_reads_i, xi_i(g))
P(D_i | C_i, phi_i) =
  sum_g P_G,i(g | C_i) * Binomial(ALT_i | total_reads_i, xi_i(g))
```

這些看不見的 assignment / genotype candidates 不會被硬抽成單一答案，而是直接把
可能性加總；最後輸出每個 SNV 的 assignment 與 genotype/multiplicity posterior。

## 4. 輸入介面

後端只接受已通過 QA 的 `likelihood_input.tsv.gz`，不直接讀 BAM、VCF 或 ASCAT
原始輸出。主要欄位由 [`data.md`](data.md) 定義：bulk ref/alt reads、ASCAT
major/minor/total CN、`rho_ASCAT`、HP supplementary counts，以及 eligibility
欄位。`error_rate=0.001` 是 model-side fixed parameter，本輪不新增 canonical
column；正常 CN=2 亦同樣是目前 v4 runtime 的固定假設。

PS 不會成為 particle state 或 topology constraint；它只在上游協助形成 HP counts，
並保留在 provenance / grouped holdout metadata。

## 5. 輸出介面

每個 SMC repeat 應產生：

| Artifact | 用途 |
|---|---|
| `samples.jsonl.gz` | 最終等權重 posterior particles；`sample_kind=smc_particle` |
| `particle_history.jsonl.gz` | 每個 annealing stage 的 particle、weight 與 ancestor 紀錄 |
| `posterior_summary.tsv.gz` | 每個 clone 的 CCF/phi median 與區間 |
| `topology_summary.tsv` | canonical edge support |
| `representative_tree.json` | 代表性 topology 與 SNV assignment summary |
| `multiplicity_posterior.tsv.gz` | 模型內部 CN-aware multiplicity 的 posterior |
| `diagnostics.json` | beta、ESS、resampling、diversity、rejuvenation 與輸入 provenance |
| `checkpoint.json.gz` | SMC stage particle state、weights、ancestor 與 RNG audit |
| `smc_complete.json` | 完成標記與 artifact manifest |

`smc_complete.json` 出現前，該 repeat 不得被 workflow 當成完成結果。

## 6. Workflow 層的判定

單個 repeat 只表示它完成了 SMC。formal workflow 會以不同 seed 執行多個獨立
repeats，再檢查：

- conditional ESS 與 weighted particle ESS；
- particle diversity 與 ancestor diversity；
- CCF stability、SNV assignment agreement、edge support difference；
- PS、chromosome、ASCAT segment grouped holdout 的 predictive coverage / score。

這些是 workflow 的 evidence gates，不是 model input，也不會把 PS 直接塞進
likelihood。

## 7. 平行化設計

- C++ 以 `repeats` 作為獨立工作單位；不同 repeat 使用不同 deterministic seed。
- `--threads` 控制 repeat 平行度；多 repeat 時每個 repeat 的 site scorer 使用一條
  thread，避免 oversubscription。
- 同一 repeat 內 particle 與 site likelihood 可再由 C++ scorer 平行化。
- Python 只負責 workflow、holdout、provenance、gate 與測試 fixture；正式 sampler
  由 `tumor_tree_pipeline/cpp_backend.py` 呼叫 C++ executable。

## 8. 測試與限制

目前已涵蓋：

- C++ Debug build 與 smoke test；
- Python SMC artifact fixture、workflow gate 與 immutable-run tests；
- black-box CLI schema、HP supplementary invariance、thread policy、independent
  repeat seed、fail-closed output tests。

上述測試已加入 genotype-candidate、`mu` clipping、`xi` 數值與 candidate-prior
marginalization 的 C++/Python contract coverage；它們仍不取代正式資料的
posterior predictive 與 convergence gates。

目前 `--resume` 只允許讀取已完成且 artifact 完整的 immutable repeat；尚未宣稱能
從中途 checkpoint 接續計算。正式 HCC1395 全量 run 仍須先通過 smoke、pilot、
formal gates，未通過時只能稱為 diagnostic candidate output。

## 9. 與 PhyloWGS 的關係

本文件 target/spec 採用相同的大方向：CN-aware genotype candidates 不由外部表格
指定，而是在 CCF、copy number、`error_rate` 與 read-count likelihood
中被自動評估並邊際化。拓樸
探索則採用受限的 local SPR + global legal-tree MH，這是從 PhyClone 的拓樸 mode
探索得到的實作借鑑；它不是完整複製 PhyClone 的 Particle Gibbs、pre-clustering、
outlier/loss model 或 auxiliary ordering。資料仍只使用 canonical table 中明確存在
的 ASCAT static CN 與 purity；目前 C++/Python runtime 已同步本文件的最小
PhyClone-compatible `xi` emission，但尚未建模 clone-specific CNV event history。
