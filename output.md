# Model outputs

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

`phi_v` is the cumulative cancer-cell fraction for clone `v` and all of its
descendants; it is not the local mass `eta_v`.

The percentages are illustrative. The actual run supplies the values in the
`phi` vector.

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

模型不是把輸入表格直接複製成結果。它會先使用 bulk counts、ASCAT copy number
與 `rho_ASCAT`，再由 inference algorithm 探索模型內部的未知狀態。

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
| `eta_v` | clone `v` 自己獨有的細胞比例 | 與樹的 descendants 一起推導 `phi_v` |
| `phi_v` / CCF | clone `v` 加上 descendants 的累積細胞比例 | 形成每個 clone 的 CCF summary |
| `M_i` | 第 `i` 個 SNV 在 tumor cells 中可能佔幾份 copy | 彙整成 `multiplicity_posterior.tsv.gz` |

這些不是輸入表格中已經固定好的答案。`T`、`z_i`、`eta_v` 與 `M_i` 是模型在
每個候選狀態中評估的 latent quantities；inference algorithm 負責探索多個候選
狀態，最後再把它們彙整成 topology、CCF、SNV assignment 與 multiplicity
posterior。

`rho_ASCAT`、major/minor/total CN 與 read counts 則是模型輸入，不是模型從本次
tumor-tree inference 自動猜出的參數。`phi_v`／CCF 也不是直接把 observed VAF
換算而來，而是由樹 `T` 與 local mass `eta` 結構性推導，再由 purity、CN、latent
multiplicity 與 bulk likelihood 共同受到資料約束。

目前相關輸出包括：

- `posterior_summary.tsv.gz`：每個 clone 的 `phi`／CCF posterior summary。
- `topology_summary.tsv`：候選樹的 parent-child edge support。
- `multiplicity_posterior.tsv.gz`：每個 SNV 各種 multiplicity 的 posterior support。
- SNV-to-clone assignment：每個 SNV 所屬 clone 與其不確定性。

目前這些仍屬 diagnostic candidate output；在 inference correctness、canonical
input 重建與 predictive checks 完成前，不代表唯一真實的腫瘤演化歷史。
