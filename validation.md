# Tumor-tree Validation Module Handoff

更新日期：2026-08-28
狀態：MVP 規格 / Codex handoff  
適用架構：`data input → model ↔ inference_algo → output`，其中 `validation` 為 cross-cutting read-only module

VAF target specification：PhyClone `xi` observation model，`error_rate=0.001`。目前
Python／C++ emission 已同步；但 validation 仍需檢查 deterministic prediction output、
正式資料 predictive check 與其他 gates，不能把公式同步誤當成 validation PASS。

---

## 1. 目的

這份文件定義 tumor-tree research repo 第一版 `validation` 模組。

第一版的目標不是一次建立完整的「腫瘤演化樹高可信度認證系統」，而是先建立一個穩定、可擴充、**不侵入目前 model 與 SMC inference 實作**的 validation scaffold，作為之後修改：

- canonical observation and model-input artifacts
- purity / CNV / LOH compatibility artifacts
- SMC inference
- likelihood
- tree topology representation

時的共同安全網。

目前 active inference algorithm 是 **SMC（Sequential Monte Carlo）**，因此第一版 validation **不使用 R-hat、MCMC chain ESS 或 MCMC convergence gate**。

本模組第一階段只回答四個核心問題：

1. **SMC 計算本身是否健康？**
2. **posterior particles 對 clone ancestry 關係到底支持什麼？**
3. **在有 synthetic ground truth 時，cluster 與 ancestry 是否重建正確？**
4. **推理結果是否至少能重現觀察到的 ALT/VAF 訊號？**

第一版刻意不回答：

> 「這位病人的整棵腫瘤演化樹已經被生物學證明為 high-confidence。」

這需要後續 robustness、CN/purity uncertainty propagation、posterior calibration、orthogonal validation 等模組。

---

# 2. 在 research architecture 中的位置

目前核心 architecture：

```text
data input
    │
    ▼
  model ◄────────► inference_algo
    │
    ▼
  output
```

新增兩個 cross-cutting module：

```text
Core research modules
────────────────────────

data input
model
inference_algo
output


Cross-cutting modules
────────────────────────

validation
experiment_workflow
```

其中：

- `experiment_workflow.md`：負責「這次實驗怎麼執行、使用什麼設定、留下什麼 provenance」。
- `validation.md`：負責「這次推理結果有什麼證據支持、有哪些診斷訊號」。

`validation` 必須是 **read-only observer**：

```text
data artifacts ───────┐
model artifacts ──────┤
SMC artifacts ────────┼──► validation ───► validation report
output artifacts ─────┤
ground truth(optional)┘
```

validation：

- 可以讀取既有 artifacts。
- 不可以修改 model parameters。
- 不可以重新定義 posterior。
- 不可以偷偷 rerun inference。
- 不可以為了讓 validation PASS 而自動調整 SMC 設定。
- 不可以修改 output tree。

如果 validation 發現問題，只能回報 diagnostic / failure receipt。

---

# 3. 為什麼先實作 validation scaffold

未來若要改動上游資料準備或 genome-state model，必須另開設計階段；這些上游輸入框架目前不屬於 `validation.md`。

目前 validation 只建立 output-level baseline，檢查問題來源是否可能來自：

- canonical observation artifact
- purity/CN/LOH compatibility artifact
- mutation multiplicity
- likelihood
- SMC proposal
- particle degeneracy
- tree model
- output conversion

第一版 validation 的角色就是建立這個 output-level baseline。

---

# 4. 資料來源

本節刻意分成兩種「資料來源」：

1. validation runtime 真正讀取的 repo artifacts。
2. validation design 所參考的 benchmark / literature。

兩者不可混淆。

---

## 4.1 Runtime data sources

### A. Observed mutation data

來源：

- 現有 `data input`
- 或 model 已經使用的 observation artifact

最低需求：

```text
mutation_id
sample_id
ref_reads
alt_reads
total_reads
major_cn
minor_cn
total_cn
normal_cn
tumour_content
```

`normal_cn`、`tumour_content` 與 CN timing 是 PhyClone `xi` 所需的 observation
context；目前 v4 canonical table 不新增這些欄位，而 runtime 使用固定 normal CN=2、
`rho_ASCAT` 作 tumour-content mapping，以及 major-CN pre/post candidates。因此在
缺少 deterministic per-site `predicted_xi` output 或正式 predictive receipt 時，這個
gate 仍保持 `BLOCKED`，不能用 legacy q baseline 代替。

其中：

$$
n_{is}=ALT_{is}+REF_{is}
$$

以及：

$$
VAF_{is}^{obs}
=
\frac{ALT_{is}}{ALT_{is}+REF_{is}}
$$

第一版 validation 不重新產生 observation counts；它只讀取已經存在的 canonical observation artifact，再與 posterior 和 diagnostics 對照。

```text
canonical observation artifact
              ↓
       model / inference output
              ↓
          validation
```

上游資料準備與 observation extraction 不在本模組內重複實作。

---

### B. SMC diagnostic artifact

`inference_algo` 必須提供每一步至少：

```text
step
particle_count
ess
max_normalized_weight
resampled
```

如果目前 SMC 使用 annealing / tempering，再提供：

```text
beta
```

如果目前還沒有這些欄位，應由 inference layer 增加 diagnostic emission，但不要改變 inference target。

---

### C. Posterior particle artifact

每個 final particle 至少需要：

```text
particle_id
normalized_weight
tree
clone_assignment
```

如果 output/model 已能提供 PhyClone `xi` expected ALT probability，再提供：

```text
predicted_xi[mutation_id, sample_id]
```

若沿用 `predicted_vaf` 作相容 alias，必須同時標註它實際來自
`phyclone_xi_v1`，不能把 observed VAF 當成 prediction。

或提供一個可由 validation 呼叫的純函式：

```text
predict_vaf(particle, mutation, sample)
```

不要要求 validation 重複實作 model likelihood。

---

### D. Optional synthetic ground truth

只有 benchmark / synthetic dataset 才需要：

```text
truth_tree
truth_clone_assignment
```

真實病人資料沒有 truth 時：

```text
ground_truth = NOT_AVAILABLE
```

不得把 inferred MAP tree 當作 ground truth。

---

### E. Run metadata

至少：

```text
run_id
dataset_id
model_version
inference_version
random_seed
particle_count
timestamp
```

如果可以，再保留：

```text
git_commit
config_hash
input_provenance
```

這些 metadata 由 `experiment_workflow` 管理；validation 只讀取。

### F. VAF model metadata and prediction interface

當 VAF predictive check 被啟用時，runtime 必須提供下列 metadata；validation 不得從
舊的 `q` 公式自行重建另一套 likelihood：

```text
vaf_formula = phyclone_xi_v1
error_rate = 0.001
error_rate_status = configured | not_configured
vaf_implementation_status = synced | documentation_only
cn_timing_model = explicit
```

每個 particle／mutation／sample 必須能取得 deterministic `predicted_xi`，或由不改變
model state 的 deterministic prediction API 計算。若 runtime 仍只提供舊 baseline
`q_repo`、沒有 `error_rate`，或無法回報公式 metadata，VAF check 必須輸出
`NOT_APPLICABLE`／`BLOCKED`，不能輸出 `PASS`。

---

# 4.2 Research / benchmark sources

第一版 implementation 的設計主要參考以下工作。

## PhyClone

**PhyClone: accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing**  
Bioinformatics, 2025.

重點：

- 使用 SMC 同時探索 tree topology 與 mutation clustering。
- validation 使用 V-measure 評估 clustering。
- 使用 ancestor–descendant F-score 評估 ancestry reconstruction。
- 更完整版本也使用 LPR 與 RRE，但這兩項不列入本次 MVP。

來源：

- https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563

### 目標 VAF observation contract

PhyClone 的 target emission 以 DNA-copy-weighted population mixture 定義 expected
ALT probability。令 `e=error_rate=0.001`：

```text
w_N = 1 - t
w_R = t * (1 - CCF)
w_V = t * CCF

mu_g = clamp(mutant_copies_g / total_copies_g, e, 1-e)

xi = (w_N*c_N*mu_N + w_R*c_R*mu_R + w_V*c_V*mu_V)
     / (w_N*c_N + w_R*c_R + w_V*c_V)

ALT_reads ~ Binomial(total_reads, xi)
```

其中 `t` 是 tumour content、`CCF` 是帶 mutation 的 tumour-cell fraction、`c_*`
是各 population 的 total copy number，`mu_*` 是該 genotype 產生 ALT read 的機率。
若 genotype candidate 不確定，應依 candidate prior 邊際化：

```text
P(reads | CCF) = sum_g P(g) * P(reads | xi_g)
```

因此 `q_repo = rho_ASCAT * phi * multiplicity /
((1-rho_ASCAT)*2 + rho_ASCAT*total_cn)` 不再是本 validation 的 VAF oracle；它
只能作為歷史 baseline 的比較欄位。這個 target 仍不是所有真實腫瘤的 ground truth，
尤其不能忽略 CN timing、subclonal CNV、normal genotype、mapping bias 或
overdispersion。

**Implementation caveat：** C++/Python active emission 已套用 `phyclone_xi_v1` 與
`error_rate=0.001`，並由 unit/contract tests 保護；但目前 artifact 尚未逐 site 輸出
deterministic `predicted_xi`，所以 predictive gate 仍不能直接標為 PASS。任何使用舊 q
的歷史 artifact 都必須標示 `vaf_formula_status=documentation_only`。

---

## Pairtree

**Reconstructing Complex Cancer Evolutionary Histories from Multiple Bulk DNA Samples Using Pairtree**

重點：

- 使用 pairwise evolutionary relationships 描述 tree uncertainty。
- 在 576 simulated datasets 上 benchmark。
- 提出 Relationship Reconstruction Error（RRE）。
- 使用 VAF reconstruction loss 評估 inferred frequencies 對 observation 的解釋能力。
- 把 algorithm failure / timeout 也視為 benchmark 的重要資訊。

來源：

- https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/

相關 simulation / experiment resources：

- https://github.com/morrislab/pairtree-experiments
- https://github.com/morrislab/pearsim

第一版只借用「relationship-based validation」思想，不實作完整 RRE。

---

## DREAM SMC-Het

**Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction**  
Nature Biotechnology, 2024.

重點：

- 31 個 subclonal reconstruction algorithms。
- 51 個 simulated tumors。
- 從原始定序層級建立 realistic simulation。
- 將 purity、subclone number、cellular prevalence、mutation clustering、phylogeny 分開評估。
- clustering / phylogeny 同時區分 hard 與 probabilistic output。

來源：

- https://www.nature.com/articles/s41587-024-02250-y

相關 scoring framework：

- https://github.com/asalcedo31/SMC-Het_Scoring

第一版不直接重做 DREAM 全套 scoring，只採納「不同 reconstruction problem 分開驗證」的原則。

---

## SMC-Het evaluation standards

**A community effort to create standards for evaluating tumor subclonal reconstruction**  
Nature Biotechnology, 2020.

重點：

- realistic raw-sequencing-level tumor simulation。
- mutation / copy-number error 對 downstream reconstruction accuracy 的影響。
- 提供 scoring harness 等基礎資源。

來源：

- https://www.nature.com/articles/s41587-019-0364-z
本資料主要保留給未來 raw-sequencing / CNV / purity benchmark，MVP 不依賴它。

---

# 5. MVP 範圍

第一版只實作四個 validation component：

```text
V1  SMC Adequacy
V2  Relationship Posterior
V3  Synthetic Ground-truth Accuracy
V4  Basic Predictive Check
```

架構：

```text
                       validation
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  SMC adequacy       tree posterior      observed data
        │                  │                  │
        ▼                  ▼                  ▼
 diagnostics       relationship matrix   predictive residual
                           │
                           ▼
                  synthetic truth(optional)
                           │
                           ▼
                    V-measure / AD-F1
```

第一版**不要**加入：

- bootstrap stability
- CN perturbation
- purity perturbation
- multiplicity perturbation
- independent-region validation
- posterior predictive intervals
- LPR
- RRE
- single-cell validation
- deep-targeted validation
- overall 0–100 confidence score

這些全部保留到 Phase 2+。

---

# 6. V1 — SMC Adequacy

## 6.1 目的

回答：

> 目前這次 SMC 執行是否產生有效且沒有明顯 particle-weight degeneracy 的 posterior approximation？

它不回答：

> tree 是否為真。

---

## 6.2 Normalized particle weights

對某一步的 particle weights：

$$
\tilde w_p
=
\frac{w_p}
{\sum_{j=1}^{P}w_j}
$$

必須滿足：

$$
\tilde w_p \ge 0
$$

以及：

$$
\sum_p\tilde w_p\approx 1
$$

### Hard failure

以下任何情況直接：

```text
SMC_VALIDITY = FAIL
```

- NaN weight
- Inf weight
- negative normalized weight
- total weight = 0
- particle count = 0
- tree artifact 無法解析

---

## 6.3 Weight ESS

定義：

$$
ESS_w
=
\frac{1}
{\sum_{p=1}^{P}\tilde w_p^2}
$$

並輸出 normalized ESS：

$$
ESS_{frac}
=
\frac{ESS_w}{P}
$$

範圍：

$$
\frac{1}{P}\le ESS_{frac}\le1
$$

第一版只需要記錄：

```text
min_ess_fraction
median_ess_fraction
final_ess_fraction
ess_trajectory
```

### 注意

如果某一步剛完成 resampling：

```text
weights = uniform
```

那一步的 ESS 會人工回到接近 `P`。

因此 report 必須保留完整 ESS trajectory 與 `resampled` flag，不能只看 final ESS。

---

## 6.4 Maximum normalized weight

每一步：

$$
w_{max}
=
\max_p \tilde w_p
$$

輸出：

```text
max_weight_trajectory
global_max_weight
```

它可以快速顯示是否曾出現：

```text
one particle dominates population
```

---

## 6.5 Resampling count

輸出：

```text
num_resampling_events
resampling_steps
```

MVP 不對「resampling 次數多少才算好」設定 hard threshold。

因為 resampling frequency 會受：

- proposal
- tempering schedule
- particle count
- likelihood sharpness

影響。

第一版只紀錄，不直接判定 model correctness。

---

## 6.6 Unique final topologies

對 final particles 建立 canonical topology representation。

例如不要直接比較 Newick child order：

```text
(A,(B,C))
```

與：

```text
((C,B),A)
```

如果實際 rooted topology 等價，就必須 canonicalize 成同一 topology。

輸出：

```text
unique_topology_count
top_topologies
```

其中：

```text
top_topologies:
    topology_hash
    posterior_mass
```

### 注意

`unique_topology_count = 1` **不等於失敗**。

如果資料真的強烈支持單一 topology，posterior concentrated 是合理結果。

因此這一項第一版只做 descriptive diagnostic。

---

## 6.7 MVP SMC output

例如：

```json
{
  "smc_validity": "PASS",
  "particle_count": 1000,
  "min_ess_fraction": 0.42,
  "median_ess_fraction": 0.77,
  "final_ess_fraction": 0.68,
  "global_max_weight": 0.031,
  "num_resampling_events": 7,
  "unique_topology_count": 14
}
```

MVP **不要**根據任意 ESS 門檻產生「HIGH-CONFIDENCE TREE」。

---

# 7. V2 — Relationship Posterior

這是第一版最重要的 tree uncertainty output。

## 7.1 為什麼不要只輸出 MAP tree

假設 posterior：

```text
Tree A    0.42
Tree B    0.38
Tree C    0.20
```

只輸出 Tree A 會隱藏大量 uncertainty。

真正應該問的是：

> clone A 與 clone B 的 evolutionary relation，在整個 posterior 中有多少支持？

---

## 7.2 Clone-pair relation

對兩個不同 clone：

$$
(i,j)
$$

第一版採用 Pairtree-compatible 3-state：

$$
R_{ij}
\in
\{
i\prec j,\;
j\prec i,\;
i\parallel j
\}
$$

其中：

- $i\prec j$：`i` is ancestor of `j`
- $j\prec i$：`j` is ancestor of `i`
- $i\parallel j$：兩者位於不同 branch，彼此沒有 ancestry

第一版 clone-level relation **不加入 same-clone state**。

如果未來把 clustering uncertainty 直接提升到 mutation-pair relation，再擴充 4-state representation。

---

## 7.3 Weighted relationship posterior

非常重要：

SMC particles 有權重，所以不能：

```text
count particles / particle_count
```

必須：

$$
P(R_{ij}=r\mid D)
=
\sum_{p=1}^{P}
\tilde w_p
I(R^{(p)}_{ij}=r)
$$

其中：

$$
\sum_r P(R_{ij}=r\mid D)=1
$$

---

## 7.4 Output table

產生：

`relationship_posterior.tsv`

例如：

```text
clone_a clone_b p_a_ancestor_b p_b_ancestor_a p_branch max_relation max_probability
A       B       0.982          0.003          0.015    A->B         0.982
A       C       0.501          0.004          0.495    A->C         0.501
B       C       0.021          0.006          0.973    branch       0.973
```

---

## 7.5 Descriptive classification

第一版可以提供簡單 label，但必須標註這是 **TPCF provisional engineering label**，不是領域共識。

```text
max probability >= 0.95    STRONG
0.80 - 0.95                MODERATE
0.60 - 0.80                WEAK
< 0.60                     UNRESOLVED
```

例如：

```text
A → B     STRONG
A ? C     UNRESOLVED
B || C    STRONG
```

### 重要限制

`STRONG` 只代表：

```text
strong posterior support within this model/inference run
```

不能直接翻譯成：

```text
biologically proven
```

---

# 8. V3 — Synthetic Ground-truth Accuracy

只有存在 ground truth 時執行。

```text
if ground_truth is None:
    benchmark_metrics = NOT_APPLICABLE
```

第一版只做：

```text
V-measure
AD-F1
```

---

# 9. V-measure

## 9.1 目的

回答：

> mutation 是否被放進正確的 clone？

這是 clustering accuracy。

它不回答 tree topology 是否正確。

令：

- `C` = truth clustering
- `K` = inferred clustering

Homogeneity：

$$
h
=
1-\frac{H(C|K)}{H(C)}
$$

Completeness：

$$
c
=
1-\frac{H(K|C)}{H(K)}
$$

V-measure：

$$
V
=
2\frac{hc}{h+c}
$$

範圍：

$$
0\le V\le1
$$

---

## 9.2 Predicted clustering

MVP benchmark 使用：

```text
MAP / highest posterior mass clustering
```

但 report 必須明確記錄：

```text
clustering_estimator = MAP
```

不要假裝 V-measure 已經評估完整 clustering posterior。

---

# 10. Ancestor–Descendant F1

## 10.1 目的

這是第一版 **primary tree accuracy metric**。

回答：

> 推理出的 mutation ancestor–descendant relationships 是否符合 ground truth？

PhyClone 也使用 ancestor–descendant F-score 進行 tree reconstruction accuracy benchmark。

---

## 10.2 Ground-truth ancestor pair set

由 truth tree 建立：

$$
\mathcal A^*
=
\{
(m_i,m_j):
m_i\text{ is a strict ancestor of }m_j
\}
$$

prediction：

$$
\hat{\mathcal A}
$$

---

## 10.3 Score

$$
TP
=
|\hat{\mathcal A}\cap\mathcal A^*|
$$

$$
FP
=
|\hat{\mathcal A}\setminus\mathcal A^*|
$$

$$
FN
=
|\mathcal A^*\setminus\hat{\mathcal A}|
$$

Precision：

$$
P
=
\frac{TP}{TP+FP}
$$

Recall：

$$
R
=
\frac{TP}{TP+FN}
$$

最後：

$$
AD\text{-}F1
=
2\frac{PR}{P+R}
$$

---

## 10.4 Same-clone mutations

同一 clone 內的 mutations 不應當視為 strict ancestor relation。

例如：

```text
Clone A: m1, m2
Clone B: m3
A → B
```

positive ancestor pairs：

```text
m1 → m3
m2 → m3
```

但：

```text
m1 → m2
```

不是 strict ancestor pair。

---

## 10.5 V-measure 與 AD-F1 必須同時保留

例如：

```text
V-measure = 0.97
AD-F1     = 0.51
```

代表：

> mutations clustering 幾乎正確，但 clone evolution ordering 錯誤。

因此不得把兩者平均成：

```text
accuracy = 0.74
```

---

# 11. V4 — Basic Predictive Check

第一版不要直接做完整 posterior predictive calibration。

先回答最基本的問題：

> posterior particles 所代表的 model prediction，是否至少能大致重現實際 ALT/VAF？

---

## 11.1 Observed VAF

$$
y_{is}
=
\frac{ALT_{is}}
{ALT_{is}+REF_{is}}
$$

---

## 11.2 Posterior predictive mean VAF

target runtime 應由 PhyClone xi 計算每個 particle 的 expected ALT probability：

$$
\xi_{is}^{(p)}
=
E[ALT\ probability_{is}\mid X^{(p)},\ phyclone\_xi\_v1,\ e=0.001]
$$

則：

$$
\hat \xi_{is}
=
\sum_p
\tilde w_p
\xi_{is}^{(p)}
$$

若輸出仍稱為 predicted_vaf，其值也必須明確標記為由 xi 產生，而不是把 observed
VAF 直接當成 prediction。

---

## 11.3 Residual

$$
r_{is}
=
y_{is}-\hat\xi_{is}
$$

輸出：

```text
mean_absolute_vaf_residual
median_absolute_vaf_residual
max_absolute_vaf_residual
top_predictive_outliers
```

以及：

`predictive_residuals.tsv`

```text
mutation_id
sample_id
observed_vaf
predicted_vaf
predicted_xi
residual
depth
vaf_formula
error_rate
```

---

## 11.4 MVP 不設定 universal PASS threshold

這項資料同時被拿去 fit model，因此：

```text
training-data fit
```

不是：

```text
independent predictive accuracy
```

所以第一版：

```text
status = DESCRIPTIVE
```

不要規定：

```text
MAE < 0.05 => PASS
```

後續建立 synthetic calibration / held-out prediction 後再加入 threshold。

---

# 12. 第一版 ValidationReport

建議主要輸出：

```text
validation_report.json
relationship_posterior.tsv
predictive_residuals.tsv
benchmark_metrics.json        # only when truth exists
```

---

## 12.1 `validation_report.json`

建議結構：

```json
{
  "schema_version": "validation.v1",
  "run_id": "run-001",

  "smc": {
    "validity": "PASS",
    "particle_count": 1000,
    "min_ess_fraction": 0.42,
    "median_ess_fraction": 0.77,
    "global_max_weight": 0.031,
    "resampling_events": 7,
    "unique_topology_count": 14
  },

  "relationships": {
    "num_clone_pairs": 10,
    "strong": 6,
    "moderate": 1,
    "weak": 1,
    "unresolved": 2
  },

  "predictive": {
    "mean_absolute_vaf_residual": 0.031,
    "median_absolute_vaf_residual": 0.019,
    "max_absolute_vaf_residual": 0.181
  },

  "benchmark": {
    "available": true,
    "v_measure": 0.91,
    "ad_f1": 0.87
  }
}
```

---

# 13. MVP 不產生 overall confidence score

第一版禁止：

```text
tree_confidence = 87/100
```

也禁止：

```text
HIGH CONFIDENCE TUMOR TREE
```

原因：

目前 MVP 尚未驗證：

- input uncertainty
- purity robustness
- CN robustness
- multiplicity robustness
- bootstrap stability
- independent SMC reproducibility
- posterior calibration
- external biological evidence

所以第一版 report 最多可以說：

```text
SMC diagnostics available
posterior relationships summarized
synthetic reconstruction accuracy available
basic observation fit available
```

---

# 14. Suggested module layout

具體語言與 package naming 請遵循 repo 既有 style；以下只定責任，不強制目錄語言。

```text
validation/
│
├── schema/
│   ├── validation_input
│   └── validation_report
│
├── smc/
│   ├── weights
│   ├── ess
│   └── topology_summary
│
├── relationships/
│   ├── canonical_tree
│   └── posterior
│
├── benchmark/
│   ├── v_measure
│   └── ancestor_descendant_f1
│
├── predictive/
│   └── vaf_residual
│
└── report/
    └── writer
```

不要在第一版建立：

```text
bootstrap/
robustness/
orthogonal/
cn_validation/
rre/
lpr/
```

等空架構。

需要時再新增。

---

# 15. Input contract

Codex 實作前，先在既有資料結構上建立 adapter。

概念 contract：

```text
ValidationInput
├── run_metadata
├── observed_mutations
├── smc_steps
├── posterior_particles
└── ground_truth?       optional
```

---

## 15.1 `observed_mutations`

至少：

```text
mutation_id
sample_id
ref_reads
alt_reads
total_reads
```

normal_cn、tumour_content 與 CN timing 是 PhyClone xi 的 observation context；
若 canonical artifact 尚未提供這些欄位，不能把 legacy q_repo 的結果宣稱為
phyclone_xi_v1 prediction。

---

## 15.2 `smc_steps`

至少：

```text
step
particle_count
ess
max_normalized_weight
resampled
beta?                   optional
```

---

## 15.3 `posterior_particles`

至少：

```text
particle_id
normalized_weight
tree
clone_assignment
predicted_xi?           optional
predicted_vaf?          optional alias; must identify xi source
vaf_formula?            required when prediction exists
error_rate?             required when prediction exists
```

如果 `predicted_vaf` 不儲存：

validation 可以透過 model 的 deterministic prediction API 計算，但該 API 必須：

- 不修改 model state
- 不重新 infer
- 同一輸入必須 deterministic

---

# 16. Canonical tree requirement

validation 必須定義 canonical tree representation。

最低要求：

1. rooted tree。
2. 每個 clone 有 stable ID。
3. sibling ordering 不影響 topology identity。
4. topology hash 對等價 sibling ordering 必須一致。

例如：

```text
A
├── B
└── C
```

與：

```text
A
├── C
└── B
```

必須是同一 topology。

---

# 17. Error receipt

validation 遇到資料不完整時不要 silent skip。

例如：

```json
{
  "component": "predictive",
  "status": "NOT_APPLICABLE",
  "reason": "posterior particle does not expose predicted VAF"
}
```

其他 reason 例如：

```text
GROUND_TRUTH_NOT_AVAILABLE
INVALID_PARTICLE_WEIGHT
TREE_PARSE_ERROR
MISSING_CLONE_ASSIGNMENT
MISSING_OBSERVED_COUNTS
PREDICTED_VAF_NOT_AVAILABLE
```

---

# 18. Implementation order

Codex 第一輪依序執行。

## Step 0 — Freeze current baseline

在修改任何 model/input 前：

- 記錄目前可正常執行的 dataset。
- 記錄 current SMC config。
- 記錄 current model version / commit。
- 保存 current tree / CCF / assignment output。

如果 repo 有 tag 機制，建立 baseline tag。

建議語意：

```text
baseline-pre-validation
```

---

## Step 1 — 建立 schema 與 report writer

先完成：

```text
ValidationInput
ValidationReport
```

以及 JSON/TSV writer。

此步不做 metric。

Acceptance：

- 可以讀目前一個 inference result。
- 可以輸出合法空 validation report。
- 不改變既有 inference output。

---

## Step 2 — 實作 SMC adequacy

完成：

- weight validation
- ESS summary
- max weight summary
- resampling summary
- canonical topology count

Acceptance：

已知 toy particle population 的 ESS 必須符合人工計算。

例如：

```text
weights = [0.25, 0.25, 0.25, 0.25]
ESS = 4
ESS_fraction = 1
```

以及：

```text
weights = [1, 0, 0, 0]
ESS = 1
ESS_fraction = 0.25
```

---

## Step 3 — 實作 relationship posterior

完成：

```text
clone-pair 3-state posterior
```

必須使用 particle weights。

Acceptance：

建立 toy particles：

```text
particle 1  weight .6   A→B
particle 2  weight .3   branch
particle 3  weight .1   B→A
```

輸出必須：

```text
P(A→B)   = .6
P(B→A)   = .1
P(branch)= .3
```

---

## Step 4 — 實作 synthetic benchmark

完成：

```text
V-measure
AD-F1
```

Acceptance：

perfect reconstruction：

```text
V-measure = 1
AD-F1     = 1
```

clustering perfect but topology wrong 的 toy case：

```text
V-measure = 1
AD-F1 < 1
```

此測試必須存在，防止未來把 clustering accuracy 誤當 tree accuracy。

---

## Step 5 — 實作 basic predictive check

只有在 runtime 已同步 phyclone_xi_v1 與 error_rate=0.001，並能提供 deterministic
prediction API／receipt 時，才加入：

```text
observed VAF
predicted xi
residual
vaf_formula = phyclone_xi_v1
error_rate = 0.001
```

如果目前沒有上述 API、公式 metadata 或 error-rate receipt：

**不要為了 validation 強改 model。**

先輸出：

```text
predictive = BLOCKED
vaf_formula_status = DOCUMENTATION_ONLY
```

把 runtime migration、formula oracle 與 deterministic prediction API 留給後續 PR。

---

# 19. MVP acceptance criteria

第一版 validation 模組完成的最低條件：

- [ ] 不修改現有 posterior 定義。
- [ ] 不修改現有 SMC inference behavior。
- [ ] 可以讀取至少一個目前 repo inference run。
- [ ] 可以偵測 invalid particle weights。
- [ ] 可以輸出 SMC ESS summary。
- [ ] 可以 canonicalize tree topology。
- [ ] 可以產生 weighted clone relationship posterior。
- [ ] synthetic truth 存在時可計算 V-measure。
- [ ] synthetic truth 存在時可計算 AD-F1。
- [ ] truth 不存在時 benchmark metrics 正確輸出 `NOT_APPLICABLE`。
- [ ] 不產生 overall confidence score。
- [ ] 所有 validation artifact 帶 `run_id` 與 schema version。
- [ ] toy tests 能驗證 weighted posterior 與 AD-F1 邏輯。
- [ ] runtime 明確回報 vaf_formula=phyclone_xi_v1 與 error_rate=0.001。
- [ ] 有獨立數值 oracle test 覆蓋 normal／reference／variant population 的 copy-number
      weighted xi，並覆蓋 genotype candidate marginalization。
- [ ] 在上述 runtime sync 與 oracle test 完成前，VAF predictive gate 保持
      BLOCKED／NOT_APPLICABLE，不得標記 PASS。

---

# 20. 第一版明確不做的事情

以下全部 deferred：

## Phase 2 — SMC reproducibility

- independent SMC runs
- relationship-posterior JSD
- particle-count scaling
- log-normalizing-constant stability
- ancestor/path degeneracy

---

## Phase 3 — Robustness

- mutation / genomic-block bootstrap
- read downsampling
- purity perturbation
- CN posterior perturbation
- multiplicity perturbation
- leave-one-region-out

---

## Phase 4 — Posterior benchmark

- full posterior predictive calibration
- predictive intervals
- LPR / VAF reconstruction loss
- RRE
- relationship entropy
- calibrated threshold profiles

---

## Phase 5 — Orthogonal validation

- single-cell DNA evidence
- targeted ultra-deep sequencing
- phasing support / contradiction
- longitudinal validation
- independent multi-region validation

---

## Phase 6 — Genome-state validation

當未來的 genome-state posterior artifact 與 uncertainty interface 穩定後，再新增：

```text
purity accuracy / calibration
major-minor CN accuracy
LOH accuracy
ploidy ambiguity
CN posterior calibration
genome-state → tree uncertainty propagation
```

**這些目前不要放進 MVP。**

---

# 21. 未來與 Genome-State Framework 的關係

後續新的 model 可能變成：

$$
G=
(\rho,\psi,C^{maj},C^{min},LOH)
$$

$$
E=
(T,z,\phi,M)
$$

推理：

$$
p(G,E\mid D)
$$

但 validation API 不應因此被推翻。

理想上：

```text
old pipeline
external CN/purity
      ↓
posterior particles
      ↓
validation


new upstream genome-state module
      ↓
genome-state posterior artifact
      ↓
posterior particles
      ↓
validation
```

也就是 validation 應盡量依賴：

```text
observations
+
posterior artifacts
+
optional truth
```

而不是綁死 upstream tool。

---

# 22. 未來 benchmark strategy

完整 benchmark 之後再加入以下 datasets / regimes：

```text
native synthetic
TSSB-like
Pairtree simulation
CONIPHER-like CN/mutation-loss simulation
DREAM raw-sequencing-level simulation
```

但第一版只需要：

```text
repo already has synthetic truth
```

如果 repo 目前沒有 synthetic dataset：

第一個 benchmark fixture 只建立極小 toy truth：

```text
Root
└── A
    ├── B
    └── C
```

足夠測：

- clustering
- ancestry
- relationship posterior
- weighted particles

不要在 validation PR 同時開發大型 tumor simulator。

---

# 23. Validation philosophy

後續所有 validation 開發都遵守：

```text
convergence / particle adequacy
        !=
tree accuracy
        !=
robustness
        !=
biological truth
```

以及：

```text
high posterior probability
        !=
high biological confidence
```

第一版最重要的成果不是產生更多指標，而是讓 repo 從現在開始具備：

```text
change model/input/inference
          │
          ▼
run the same validation
          │
          ▼
compare against baseline
```

的能力。

---

# 24. Definition of Done

當以下流程可以穩定執行時，MVP 完成：

```text
existing inference run
        │
        ▼
ValidationInput
        │
        ├── SMC adequacy
        ├── relationship posterior
        ├── V-measure / AD-F1 (if truth)
        └── VAF residual (if prediction available)
        │
        ▼
validation_report.json
relationship_posterior.tsv
benchmark_metrics.json (optional)
predictive_residuals.tsv (optional)
```

完成後：

**先停止擴充 validation metrics。**

下一個 major architecture task 才會另行定義 upstream genome-state data contract；目前不在 `validation.md` 描述其原始輸入框架。

並用本 validation scaffold 作為 baseline safety net。

---

# 25. Bulk-only Output Support and Claim Ceiling

本章整合原 `support.md` 的 output support evaluator 規格。`validation.md` 是
目前唯一的 validation 文件；不再維護獨立的 `support.md`。這一層位於 output
之後，只讀取 model、inference 與 output artifacts，不重新推理，也不把外部證據
塞回 likelihood。

## 25.1 驗證對象與最高語意

目前 output 只驗證三類結果：

1. `normal cells → tumor_root → clone` 的 rooted topology。
2. clone-specific local fraction ($\eta_v$) 與 CCF ($\phi_v$)。
3. 每個 eligible SNV 的 clone assignment 及其不確定性。

樹圖的語意固定為：

```text
normal cells
      │
      ▼
tumor_root
      │
      C1
    ┌─┴─┐
   C2  C3
```

- `normal cells` 是 presentation-level external root，不是目前 C++ sampler 的
  posterior node。
- `tumor_root` 是所有 tumor clones 的共同祖先，不承載普通 SNV assignment。
- `clone_1` 等 artifact node 可在展示層映射成 `C1`、`C2`；validation 必須保留
  兩者的 mapping，並以 label-invariant topology 比較結果。
- clone-specific local fraction ($\eta_v$) 是只分配給 clone $v$ 本身、排除
  descendants 的 tumor-cell fraction；CCF ($\phi_v$) 是該 clone 加上 descendants
  的 cumulative tumor-cell fraction。

目前最高可使用的名稱是：

> **high-confidence candidate branching tree topology**

它只表示 bulk evidence 支持的候選 branching topology，不表示 single-cell
lineage truth、唯一真實腫瘤歷史，或直接觀察到的 clone ancestry。

若 `output.md` 仍是 `output_status=illustrative`，只能標記
`NOT_APPLICABLE`；illustration 不可產生 formal PASS，也不可升級 claim grade。

## 25.2 證據分層與狀態詞彙

每個 evidence record 必須保存 `evidence_layer`：

| layer | 意義 |
|---|---|
| `method_capability` | 方法理論上能支援的分析能力，例如 PhyloWGS 可將 CNV 表成 pseudo-SSM 並納入 joint inference。 |
| `published_evidence` | HCC1395 論文或其他外部研究已報告的證據。 |
| `current_implementation` | 本 repo 程式與目前 run artifact 實際產生的結果。 |
| `external_orthogonal` | 未被本次 likelihood 使用、可獨立支持同一 claim 的外部資料。 |

每個來源另保存 `artifact_status`：

| status | 意義 |
|---|---|
| `reported` | 外部論文或文件明確報告。 |
| `reproduced` | 本 repo 已成功重建且可檢查。 |
| `inferred` | 從資料或模型結果推導，不是直接觀測。 |
| `not_reported` | 文獻或文件沒有提供。 |
| `missing` | 目前應存在但不存在。 |

run-level gate 只使用 `PASS`、`FAIL`、`UNKNOWN`、`NOT_APPLICABLE`。後兩者都
不可當作 PASS；`not_reported` 與 `missing` 是來源狀態，不是 gate 通過狀態。

## 25.3 證據獨立性與 PS 邊界

每筆 evidence 必須附上：

```text
evidence_origin = in_likelihood | held_out | external_orthogonal
used_in_likelihood = true | false
```

ASCAT CN、ASCAT purity、CN-derived multiplicity 與目前 Model A 讀取的 bulk
counts 已進入 likelihood；它們可以支持 model fit 或 bulk compatibility，但不
能再次被描述成獨立 branch validation。真正的獨立支持必須標為
`external_orthogonal`。

PS phase block 只可用於 phase provenance、局部 QC 與 grouped holdout。PS 不直接
決定 clone assignment、$\eta_v$、$\phi_v$、topology 或 ancestry edge；HP counts 目前也
只是 supplementary evidence，不是 Model A primary likelihood。沒有 joint
single-cell SNV+CN matrix 時，不宣稱 single-cell SNV lineage validation。

## 25.4 Output support 的 gate 對應

本章的 support 檢查沿用前面 Gate 0–12，不另建第二套結果判定：

| support 問題 | 對應 gate | 可以支持的語意 |
|---|---|---|
| run 是否完整且可追溯 | Gate 0 | artifact identity / reproducibility |
| canonical table 是否正確 | Gate 1 | observed-data contract |
| SMC particle population 是否健康 | Gate 2 | inference reliability |
| topology 是否為合法 rooted tree | Gate 3 | structural validity |
| $\eta_v$ / $\phi_v$ 是否滿足 CCF constraints | Gate 4 | numerical consistency |
| SNV assignment 是否完整且相容 | Gate 5 | assignment support |
| bulk counts 是否被 posterior predictive 解釋 | Gate 6 | model fit / holdout fit |
| ASCAT purity、CN、LOH、ploidy 是否相容 | Gate 7 | bulk compatibility |
| CNV event 是否放到 node | Gate 8 | optional event-placement claim |
| driver 是否有獨立 annotation 與 node join | Gate 9 | optional interpretation claim |
| topology 是否跨 repeat、K、purity 穩定 | Gate 10 | topology stability |
| alternatives 與 interval 是否被保留 | Gate 11 | uncertainty / alternatives |
| 是否足以發布候選樹名稱 | Gate 12 | final claim ceiling |

任何 core hard `FAIL` 都停止該層級 claim；`UNKNOWN` 必須保留為未知，不能補寫
成通過。

## 25.5 Bulk compatibility 不等於 branch-level proof

目前 ASCAT / CNV / LOH / ploidy / purity 可以檢查：

```text
rho_ASCAT、major_cn、minor_cn、total_cn
segment boundary、BAF / allelic balance、LOH state
CN-zero / unmapped exclusion、caller / version / source hash
```

這些資料可讓候選 tree 與 bulk genome-state pattern **相容**，但若只有
site-level CN，就不能宣稱已完成：

```text
CNA event → candidate node
SNV-CNA timing
SNV-CNA ancestor relationship
```

PhyloWGS 的方法能力可以作為 `method_capability` 證據：外部 CNV 可被轉成
pseudo-SSM/CNV event，與 SSM joint inference，並由 model 推定 event 對應的
clone/tree node。但這不代表 HCC1395 論文公開了完整 event-to-node table，也不
代表目前 repo 已產生該 table。

因此目前的 claim 是：

> candidate topology 與 segment-level CN/LOH pattern 相容。

不是：

> 已證明某個 CNA event 發生在某一個 clone branch。

## 25.6 Optional evidence tables

以下是 validation 可產生或未來補上的 evidence tables；它們不是目前 model 的
輸入欄位。

### CNV / LOH compatibility table

```text
segment_id, chrom, start, end
major_cn, minor_cn, total_cn, loh_state
cnv_status, cnv_caller, purity_source, ploidy
compatibility_status, evidence_layer, artifact_status, notes
```

### CNV event-to-node table（目前 UNKNOWN）

```text
cnv_event_id, segment_id, cnv_type, chrom, start, end
candidate_node, assignment_posterior, event_prevalence, ccf_interval
affected_snv_ids, multiplicity_context, snv_cnv_timing
phase_or_allele_context, prevalence_convention, cell_universe
tumor_cell_fraction, all_cell_fraction, purity_conversion
independent_support, claim_status
```

### Driver annotation table

```text
event_id, variant_key, gene, transcript, consequence
annotation_database, database_version, driver_tier
candidate_node, assignment_posterior, ccf_interval
local_cn, multiplicity, cnv_context, loh_context
independent_source, claim_status
```

driver annotation 是獨立 interpretation layer。高 CCF、ALT count、tumor-root
位置、multiplicity、depth 或論文圖上的 edge label，都不能單獨產生 driver
truth。沒有完整公開的 driver → node mapping table 時，狀態只能是
`annotation_only`、`figure_annotation_only`、`ambiguous` 或 `unknown`。

## 25.7 Topology class 與 claim grading

比較 topology 時，先 canonicalize 每個 draw 的 node labels，再依預先登錄規則
比較 `linear`、`branching`、`polytomy` 的 posterior mass、edge support 與
predictive metrics。跨 K 只比較共同 rooted clade/partition，不能直接比較
node index。

只有在 primary `K=6, rho_ASCAT=0.99`、K/purity sensitivity、SMC repeat stability、
bulk predictive gate 與 alternatives 檢查都通過，且 branching 與 runner-up 的
差值超過事前登錄的 `topology_selection_margin`，才能標記：

```text
topology_status = branching_candidate
```

目前若 margin、class scoring 或 inference correctness audit 尚未完成，狀態是
`UNKNOWN`，不可機械化授予 Grade A。

| grade | 語意 |
|---|---|
| A | bulk-supported candidate topology；可使用 high-confidence candidate branching tree topology，但仍不是真實唯一 lineage。 |
| B | 部分 local edges 穩定，完整 topology 尚有 alternatives。 |
| C | 合法 candidate hypothesis，但 inference、holdout 或 sensitivity 尚未完整。 |
| D | core gate FAIL、run failed、posterior 缺失或 topology 高度敏感；不發布 evolutionary claim。 |

目前已知的 claim ceiling：沒有成功 formal posterior、沒有完成所有 inference
correctness/robustness audit 時，不能發布 Grade A；目前最多是 method-development
或 candidate hypothesis。CNV event-to-node 與 driver mapping 的 `UNKNOWN` 只會
阻擋相應 optional claim，不自動把 bulk compatibility 改寫成 branch proof。

## 25.8 Validation report 中的 evidence matrix

所有 output support 結果最後寫入同一份 `validation_report.json` 的 evidence
matrix：

```text
claim_id, claim, evidence_layer, artifact_status, status
source, supporting_fields, contradicting_fields, missing_fields
claim_ceiling, reviewer_note
```

最低範例：

| claim | layer | status | claim ceiling |
|---|---|---|---|
| topology is structurally valid | current_implementation | PASS | structural validity |
| CCF obeys descendant constraints | current_implementation | PASS | numerical consistency |
| CNV event maps to clone node | current_implementation | UNKNOWN | no CNV-to-node claim |
| candidate tree is compatible with bulk CN/LOH | current_implementation | PASS/UNKNOWN | bulk compatibility only |
| SNV lineage is validated by single-cell data | published_evidence | UNKNOWN | no single-cell lineage claim |
| final topology is high-confidence | current_implementation | UNKNOWN | blocked by run / inference status |

## 25.9 Wayfinder route

```text
run completeness / provenance
          ↓
canonical input → SMC adequacy
          ↓
tree structure → clone-specific local fraction / CCF → SNV assignment
          ↓
repeat / K / purity stability
          ↓
bulk predictive holdout
          ↓
ASCAT / CN / LOH compatibility
          ↓
optional CNV event-to-node + driver interpretation
          ↓
uncertainty + alternatives
          ↓
claim grade
```

這個順序是 validation 的 decision route，不是新的 inference pipeline。它只讀取
既有 artifacts，發現問題時輸出 diagnostic 或 failure receipt，不修改 model、
SMC 設定或 output tree。

## 25.10 整合決策紀錄

本次 `grill-with-docs` review 後，研究架構固定如下：

1. `validation.md` 是唯一的 output support / evidence evaluator 規格。
2. validation 是 `output` 後的獨立、read-only 評估模組。
3. `support.md` 不再作為獨立模組或文件入口。
4. bulk CN/LOH/purity 只能在 evidence matrix 中標示 compatibility，不能自動升級成 branch-level proof。
5. CNV event-to-node、driver annotation 與 single-cell lineage 都是 optional / future evidence layer；缺少時明確標示 `UNKNOWN`。
6. active inference backend 是 Rao–Blackwellized annealed SMC；所有 adequacy wording 使用 particle、repeat、ESS、resampling 與 rejuvenation，不使用 MCMC chain convergence 作為 active gate。
