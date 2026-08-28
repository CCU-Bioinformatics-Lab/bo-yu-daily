# Model outputs

更新日期：2026-08-28

## 0. VAF target output contract

本 repo 的 VAF 定義目標已改為 PhyClone-compatible `xi`，並固定：

```text
vaf_formula = phyclone_xi_v1
error_rate = 0.001
error_rate_status = configured
vaf_implementation_status = synced
```

`xi` 是由 tumour content、clone CCF、各 genotype candidate 的 copy number 與
ALT-copy fraction 做 DNA-copy-weighted mixture 後得到的 expected ALT probability；
candidate 不確定時再依 `P_G(g)` 邊際化。完整公式見 [`model.md`](model.md)。

C++ 與 Python runtime 已同步這個最小 emission，並在 diagnostics/contract tests
保存上述 metadata；既有 artifact schema 不變。runtime 目前尚未逐 site 輸出
`predicted_xi`，因此正式 predictive validation 仍需另外完成。

## 1. Clone topology

```text
normal cells
|
└── tumor_root
    |
    └── C1
        ├── C2
        └── C3
```


## 2. CCF output (PhyloWGS-style node labels)

```text
normal cells
|
+-- tumor_root
    |
    +-- C1  [CCF = phi_C1 = 1.00 (100%)]
        +-- C2  [CCF = phi_C2 = 0.60 (60%)]
        `-- C3  [CCF = phi_C3 = 0.25 (25%)]
```

The **clone-specific local fraction** ($\eta_v$) is the tumor-cell fraction
assigned to clone $v$ itself, excluding descendants. The **CCF** ($\phi_v$) is
the cumulative tumor-cell fraction for clone $v$ plus all of its descendants;
it is not the clone-specific local fraction alone.

The percentages are illustrative. The actual run supplies the values in the
$\phi$ vector.

| clone | CCF summary |
|---|---|
| C1 | posterior median + 95% credible interval |
| C2 | posterior median + 95% credible interval |
| C3 | posterior median + 95% credible interval |

實際數值由 `posterior_summary.tsv.gz` 提供；上圖數字只是示意。


## 3. SNV-to-clone assignment

```text
SNV_A, SNV_B ──▶ C1
SNV_C  ──▶ C2
SNV_D, SNV_E ──▶ C3
```


## 4. Model-derived parameters → output

模型不是把輸入表格直接複製成結果。target model 會使用 bulk counts、ASCAT copy
number、`rho_ASCAT` 對應的 tumour content、genotype candidates 與
`error_rate=0.001`，再由 inference algorithm 探索模型內部的未知狀態；C++/Python
runtime 已同步最小版 `xi` target。

```text
canonical input
     │
     ▼
model likelihood
     │
     ▼
inference explores latent states
     │
     ▼
output summaries
```

### 模型內部自動推導的狀態

| 內部狀態 | 白話意義 | 最後如何整理成輸出 |
|---|---|---|
| `T` | clone 之間誰是誰的 parent、誰是 descendant | 形成 tumor evolutionary tree topology |
| `z_i` | 第 `i` 個 SNV 被分到哪個 clone | 形成 SNV-to-clone assignment |
| $\eta_v$ | clone `v` 自己獨有的細胞比例 | 與樹的 descendants 一起推導 $\phi_v$ |
| $\phi_v$ / CCF | clone `v` 加上 descendants 的累積 tumor-cell fraction | 形成每個 clone 的 CCF summary |
| `G_i` / `M_i` | 第 `i` 個 SNV 的 genotype candidate 與 mutated-copy state | active runtime 彙整成 genotype／multiplicity posterior |

這些不是輸入表格中已經固定好的答案。`T`、`z_i`、$\eta_v$ 與 `M_i` 是模型在
每個候選狀態中評估的 latent quantities；inference algorithm 負責探索多個候選
狀態，最後再把它們彙整成 topology、CCF、SNV assignment 與 multiplicity
posterior。

`rho_ASCAT`、major/minor/total CN 與 read counts 則是模型輸入，不是模型從本次
tumor-tree inference 自動猜出的參數。$\phi_v$／CCF 也不是直接把 observed VAF
換算而來，而是由樹 `T` 與 clone-specific local fraction vector $\eta$ 結構性推導，再由 purity、CN、latent
multiplicity、`xi` 與 bulk likelihood 共同受到資料約束。這段已是 active runtime
的語意；完整 predictive／formal gates 仍需後續驗證。

目前相關輸出包括：

- `posterior_summary.tsv.gz`：每個 clone 的 `phi`／CCF posterior summary。
- `topology_summary.tsv`：候選樹的 parent-child edge support。
- `multiplicity_posterior.tsv.gz`：每個 SNV 各種 multiplicity 的 posterior support。
- `predicted_xi`（future artifact）：每個候選腫瘤演化樹／SNV 的 PhyClone expected
  ALT probability；若加入此欄位，必須附帶 `vaf_formula=phyclone_xi_v1` 與
  `error_rate=0.001`。
- SNV-to-clone assignment：每個 SNV 所屬 clone 與其不確定性。

目前這些仍屬 diagnostic candidate output；在 inference correctness、canonical
input 重建與 predictive checks 完成前，不代表唯一真實的腫瘤演化歷史。
