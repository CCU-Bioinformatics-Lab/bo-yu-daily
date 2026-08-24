# Inference algorithm：Rao–Blackwellized annealed SMC

本文件只描述目前真的會執行的推理後端。它和 [`model.md`](model.md) 分開：
`model.md` 定義 posterior target 與觀測 likelihood；本文件定義如何從這個
target 找到腫瘤演化樹、clone mass 與 CCF。

## 1. 目前固定設定

```yaml
algorithm_id: rao_blackwellized_annealed_smc
backend: C++17
input: validated hcc1395_tumor_tree_input/v4 canonical table
primary_purity: rho_ASCAT = 0.99
state: topology + eta
parallel_unit: independent SMC repeat / particle
```

`T` 是固定 K 個 clone 的樹拓樸；`eta` 是每個 clone 的 local mass。由樹把
descendant mass 加總後得到 `phi`，也就是每個 clone 的 CCF。`K=6` 是主分析，
`K=4/8` 是 workflow 的敏感度設定。

每個 particle 只保存：

- 合法的單一 tumor founder tree topology；
- 一個正值且總和為 1 的 `eta` simplex。

SNV assignment 與 multiplicity 不另外塞進 particle state。它們在每個 site 的
likelihood 中以 Rao–Blackwellization 邊際化，並在輸出時累積 posterior responsibility。
因此 model input 不需要 multiplicity 欄位，模型仍會產生
`multiplicity_posterior.tsv.gz`。

## 2. 為什麼選 SMC

目前 posterior 同時包含離散的樹拓樸與連續的 clone mass，而且不同樹形可能形成
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
- eta：以 prior-shaped Dirichlet proposal 更新 local clone mass，並以完整 target
  的 forward/reverse proposal ratio 判斷是否接受。

這些步驟是 SMC 的 particle rejuvenation kernel，不是另一個獨立的推理後端。

### 3.3 Rao–Blackwellization

對每個 SNV，模型同時評估所有 clone mass 與 CN 允許的 multiplicity 候選。這些
看不見的 assignment / multiplicity 不會被硬抽成單一答案，而是直接把可能性加總；
最後輸出每個 SNV 的 assignment summary 和 multiplicity posterior。

## 4. 輸入介面

後端只接受已通過 QA 的 `likelihood_input.tsv.gz`，不直接讀 BAM、VCF 或 ASCAT
原始輸出。主要欄位由 [`data.md`](data.md) 定義：bulk ref/alt reads、ASCAT
major/minor/total CN、`rho_ASCAT`、HP supplementary counts，以及 eligibility
欄位。

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

目前 `--resume` 只允許讀取已完成且 artifact 完整的 immutable repeat；尚未宣稱能
從中途 checkpoint 接續計算。正式 HCC1395 全量 run 仍須先通過 smoke、pilot、
formal gates，未通過時只能稱為 diagnostic candidate output。

## 9. 與 PhyloWGS 的關係

本後端採用相同的大方向：CN-aware latent multiplicity 不由外部表格指定，而是在
clone prevalence、copy number 與 read-count likelihood 中被自動評估並邊際化。它
不是完整複製原始 PhyloWGS 的所有 CNV event、timing 或 CNV cellular prevalence
輸入；目前本 repo 仍只使用 canonical table 中明確存在的 ASCAT static CN 與 purity。
