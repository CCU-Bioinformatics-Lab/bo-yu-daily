# HCC1395 LongPhase-Clone 模型設計

更新日期：2026-08-20

> [!WARNING]
> 本文件定義 active model；輸入與 provenance以 [`data.md`](data.md) 為準，正式執行契約以 [`experiment_workflow.md`](experiment_workflow.md) 為準。舊 M3／Stage 6 artifact只可作歷史比較。

```yaml
document_id: model
document_type: model_specification
model_name: LongPhase-Clone finite-K candidate tree
sample: HCC1395
implementation: tumor_tree_pipeline
links:
  - relation: uses_data_from
    target: data.md
  - relation: inferred_by
    target: inference_algo.md
  - relation: executed_by
    target: experiment_workflow.md
```

## 1. 一頁結論

目前模型以每個 SNV 的 bulk REF/ALT、HP1-1/HP2-1、ASCAT major/minor/total CN、CN-only multiplicity prior與 ASCAT purity，推導 finite-K candidate clone-tree posterior。

五條核心邊界：

1. bulk counts只在 allele-count likelihood 使用一次。
2. `multiplicity_prior` 只由 ASCAT major/minor CN 建立，不讀 VAF、bulk counts或 purity。
3. `rho_ASCAT=0.99` 是固定的 purity input，只在 emission 中使用，並在 manifest 中留存 provenance。
4. PS block 是建立 HP1-1/HP2-1 labels/counts 的上游 phase 資訊；因此會透過 `H_i` 間接影響 likelihood，但 PS 本身不作為 downstream likelihood 欄位、inference state 或 topology edge constraint。它也可供 grouped holdout 與 provenance 使用。
5. `eta` 只保存 finite-K clone 的 local mass；`phi` 由樹上的 descendant sum 推導，結構性 `tumor_root` 的頻率固定為 1。normal contamination 只由 purity 處理。

輸出是 candidate tumor-tree posterior，不是 single-cell lineage truth，也不是 HCC1395 唯一真實演化樹。

## 2. Active posterior

```text
P(T, z, eta | D, H, C, P_M, rho_ASCAT)
  proportional to
P_TSSB^K(T) * P(eta | T) * product_i eta_{z_i}
     * product_i sum_m P_M,i(m)
         P_obs(D_i, H_i | phi_z(i), C_i, m, rho_ASCAT)
```

PS 不出現在 downstream likelihood 的條件集合；它在上游 phase/tagging 階段影響 `H_i` 的產生。`P_M,i(m)` 是 CN-only `multiplicity_prior`，不是用同一組 `D_i` 先算出的 posterior。`product_i eta_{z_i}` 是 TSSB-inspired local-node mass assignment，不另建立一個獨立的 `pi` state。

| 符號 | 定義 |
|---|---|
| `T` | rooted parent-child clone tree |
| `z_i` | mutation `i` 的 clone assignment |
| `eta_v` | clone `v` 的 local／exclusive tumor mass；全體 clone `eta` 為 simplex |
| `phi_v` | clone `v` 與 descendants 的 cumulative prevalence／CCF |
| `D_i` | bulk REF/ALT counts |
| `H_i` | HP1-1/HP2-1 conditional allocation counts |
| `C_i` | `major_cn`, `minor_cn`, `total_cn` context |
| `M_i` | mutated-copy multiplicity；由固定 `multiplicity_prior` 邊際化 |
| `P_M,i(m)` | CN-only multiplicity prior |
| `rho_ASCAT` | 外部固定 ASCAT tumor purity；主分析為 `0.99` |

### 2.1 Tree fraction 與 root

```text
phi_v = eta_v + sum(eta_w for w in descendants(v))
```

`eta_v` 是 clone `v` 的 local mass，所有 K 個 clone 的 `eta` 組成 simplex；`phi_v` 是該節點加上 descendants 的總 mass。結構性 `tumor_root` 不承載 SNV assignment，頻率概念上為 1；`1-rho_ASCAT` 是 normal contamination，不放進 `eta` simplex，只出現在 observation emission。

### 2.2 Purity-aware allele emission

位點 `i` 分配到 clone `z_i` 且 multiplicity為 `m` 時：

```text
q_i = rho_ASCAT * phi_z(i) * m
      / ((1-rho_ASCAT)*2 + rho_ASCAT*C_i,total)
```

若納入 sequencing error `e_i`：

```text
r_i = e_i + (1-2*e_i)*q_i
ALT_i ~ Binomial(bulk_depth_i, r_i)
```

`rho_ASCAT` 不用來建立 multiplicity prior，也不由 inference algorithm 重新估計。LongPhase-S DNA fraction `0.958936` 只留在歷史 provenance。

### 2.3 HP observation

`HP:Z:1-1` 與 `HP:Z:2-1` 提供 mutation side的 read allocation evidence。目前實作把 HP counts視為給定 bulk REF/ALT totals的條件式 allocation：tagged fraction由觀測 counts決定，HP1與HP2各配置 tagged mass的一半；候選 mutated side使用bulk ALT probability，另一側使用error probability，再對兩個side等權邊際化。這些是固定 observation assumptions，不是自動估計參數。等價記帳可寫成六類互斥 categories：

```text
HP1-1_REF, HP1-1_ALT,
HP2-1_REF, HP2-1_ALT,
untagged_REF, untagged_ALT
```

不能把 bulk counts與其子集合 HP counts當成兩批獨立 reads重複相乘。`HP:Z:1-2/2-2`、germline-only `HP:Z:1/2` 與 RR/RA/AR/AA不是目前 likelihood輸入。

PS block 先讓同一 phase block 內的 `HP1-1`／`HP2-1` labels 維持一致；跨不同 PS block 的 HP label 不假設具有全球一致方向。PS 不直接決定 mutation side、不建立 downstream 的 PS-wide orientation variable，也不形成 clone 或 edge。

## 3. CN-only multiplicity prior

`M_i` 是一個 tumor cell中攜帶 ALT的 copy數，不是 clone數或 CCF。可行 support由 extant ASCAT sides決定：

```text
major side: m in {1, ..., major_cn}
minor side: m in {1, ..., minor_cn}
```

ASCAT major/minor只表示 copy數較多／較少的一側，不能直接命名為 HP1/HP2。

### 3.1 階層式 neutral prior

1. 所有 `CN>0` 的 extant side先等權。
2. 在每一 side內，對 `m=1..side_CN` 均分。
3. 相同 `m` 的 side contributions相加。

公式：

```text
P_M,i(m) = sum_s P(side=s) * P(m | side=s)
```

`major_cn=3, minor_cn=1` 時：

```text
P(M=1) = 1/2 + 1/6 = 2/3
P(M=2) = 1/6
P(M=3) = 1/6
```

Canonical table保存：

```text
multiplicity_candidates = 1;2;3
multiplicity_prior      = 1=0.666667;2=0.166667;3=0.166667
```

若 `minor_cn=0`，major side取得全部 prior mass。若沒有可靠 CN segment、`total_cn=0`、support非法或 prior不和為1，該列不得進 likelihood；不能補成 diploid或單點 `m=1`。

這個 prior不使用 `D_i`，所以 bulk counts只在第2.2節 likelihood出現一次。未來若要jointly sample multiplicity，必須另開模型版本與校準，不可悄悄改變本契約。

## 4. 模型實際讀取表

Canonical schema：

```text
mutation_id
chrom pos ref alt
bulk_ref bulk_alt bulk_depth
hp1_1_ref hp1_1_alt hp2_1_ref hp2_1_alt
major_cn minor_cn total_cn
rho_ASCAT
multiplicity_candidates multiplicity_prior
model_include model_status
```

每列是一個 SNV。只有 `model_include=yes`、`model_status=eligible` 的列進 likelihood；CN=0、unmapped、zero-depth或其他排除列留在表與 manifest中供 audit。

PS欄位不屬於 active likelihood schema。PS block 可在上游 artifact 中用來產生 HP counts，也可在 grouped holdout／audit artifact 中保存；canonical likelihood table 的 inference loader 不把 PS 當成模型參數或 state。

Loader必須 fail closed：

- integrated table不存在就停止，不讀 legacy default。
- 必要欄位缺失、purity不一致、CN非法或 prior錯誤就停止。
- 不使用 `CN=2`、point multiplicity或舊欄位 fallback。

## 5. 固定輸入與模型狀態

### 固定輸入

| 項目 | 角色 |
|---|---|
| bulk REF/ALT | allele-count likelihood |
| HP1-1/HP2-1 counts | conditional HP allocation likelihood |
| major/minor/total CN | VAF denominator與 multiplicity support |
| `multiplicity_prior` | 固定 marginalization weights |
| `rho_ASCAT` | 固定 purity-aware emission參數 |

### 模型未知量與結構性推導量

| 項目 | 意義 |
|---|---|
| `T` | clone tree topology；由 inference algorithm 估計或抽樣 |
| `z_i` | mutation-to-clone assignment；由 inference algorithm 估計或抽樣 |
| `eta_v` | exclusive/local clone mass；由 inference algorithm 估計或抽樣 |
| `phi_v`／CCF | 由 `T` 與 `eta` 結構性推導的 cumulative prevalence |

具體使用哪一種抽樣、最佳化或近似推理方法，見 [`inference_algo.md`](inference_algo.md)。模型本身不規定 MCMC，也不會從這批資料自動推導 ASCAT purity、major/minor CN、跨PS的全球 HP identity或唯一真實clone數。

## 6. 推理演算法文件

本模型文件只定義 posterior target、觀測 likelihood、prior、latent quantities
與資料邊界，不規定要用 MCMC、MAP、Variational Inference 或其他 inference
algorithm。當前 active algorithm、chain input/output、平行化邊界與 algorithm
backend abstraction 見 [`inference_algo.md`](inference_algo.md)。

正式執行入口、K／purity sensitivity、chain 數、holdout、convergence metrics
與 fail-closed gates 見 [`experiment_workflow.md`](experiment_workflow.md)；這些是 workflow contract，不在 model spec 內重複定義。

## 7. 已知限制

1. finite `K` 是模型容量，不是真實clone數；必須比較 `K=4,6,8`。
2. major/minor CN不能轉稱HP1/HP2 CN；retained-allele orientation仍未識別。
3. site-level CN summary尚未建模完整CN event ordering或segment graph。
4. single bulk sample對部分tree topology不可辨識；topology recovery應單獨報告。
5. HP1-1/HP2-1是read evidence，不是clone label或lineage truth。

## 8. 歷史結果與不相容介面

2026-08-15 的歷史 integrated table使用 `multiplicity_posteriors`：它由同一組bulk counts形成權重，之後舊sampler又使用bulk likelihood。該artifact可能重複使用觀測，不能作為本模型輸入。

歷史I6 baseline為最大label-invariant R-hat `24.983`、最低ESS/chain `3.1`。這些數字只證明舊run未收斂，**不是ASCAT 0.99新版流程的結果**。

歷史PS-wide orientation、Beta-Binomial table、Stage 6 production-like output與experiment-loop pass都不代表目前模型。新版正式輸入只接受 `multiplicity_prior` 與 `rho_ASCAT`，並由 `tumor_tree_pipeline` wrapper驗收。

## 9. 維護規則

1. canonical input變更：同步更新 `data.md`、schema與fixture。
2. likelihood、latent state或proposal變更：同步更新本文件與contract tests。
3. gate或實驗矩陣變更：同步更新workflow、wrapper config與HTML。
4. 大型資料留在Git外；Git保存程式、tests、configs、fixture、manifest與小型診斷摘要。
