# HCC1395 LongPhase-Clone 模型設計

更新日期：2026-08-20

> [!WARNING]
> 本文件定義 active model；輸入與 provenance以 [`data.md`](data.md) 為準，正式執行契約以 [`ascat_purity_experiment_workflow.md`](ascat_purity_experiment_workflow.md) 為準。舊 M3／Stage 6 artifact只可作歷史比較。

```yaml
document_id: model
document_type: model_specification
model_name: LongPhase-Clone finite-K candidate tree
sample: HCC1395
implementation: tumor_tree_pipeline
links:
  - relation: uses_data_from
    target: data.md
  - relation: executed_by
    target: ascat_purity_experiment_workflow.md
```

## 1. 一頁結論

目前模型以每個 SNV 的 bulk REF/ALT、HP1-1/HP2-1、ASCAT major/minor/total CN、CN-only multiplicity prior與 ASCAT purity，推導 finite-K candidate clone-tree posterior。

五條核心邊界：

1. bulk counts只在 allele-count likelihood 使用一次。
2. `multiplicity_prior` 只由 ASCAT major/minor CN 建立，不讀 VAF、bulk counts或 purity。
3. `rho_ASCAT=0.99` 是固定的 purity input，只在 emission 中使用，並在 manifest 中留存 provenance。
4. PS block 是建立 HP1-1/HP2-1 labels/counts 的上游 phase 資訊；因此會透過 `H_i` 間接影響 likelihood，但 PS 本身不作為 downstream likelihood 欄位、MCMC state 或 topology edge constraint。它也可供 grouped holdout 與 provenance 使用。
5. `eta[0]` 是未由任何建模 clone 解釋的 residual tumor mass，不是可承載 SNV 的 founding clone；normal contamination只由 purity處理。

輸出是 candidate tumor-tree posterior，不是 single-cell lineage truth，也不是 HCC1395 唯一真實演化樹。

## 2. Active posterior

```text
P(T, z, eta | D, H, C, P_M, rho_ASCAT)
  proportional to
P(T) * P(eta | T) * P(z | T)
     * product_i sum_m P_M,i(m)
         P_obs(D_i, H_i | phi_z(i), C_i, m, rho_ASCAT)
```

PS 不出現在 downstream likelihood 的條件集合；它在上游 phase/tagging 階段影響 `H_i` 的產生。`P_M,i(m)` 是 CN-only `multiplicity_prior`，不是用同一組 `D_i` 先算出的 posterior。`P(z | T)` 是固定的 assignment prior，不是另外抽樣的 `pi` 參數。

| 符號 | 定義 |
|---|---|
| `T` | rooted parent-child clone tree |
| `z_i` | mutation `i` 的 clone assignment |
| `eta_v` | clone `v` 的 exclusive tumor fraction |
| `phi_v` | clone `v` 與 descendants 的 cumulative prevalence／CCF |
| `D_i` | bulk REF/ALT counts |
| `H_i` | HP1-1/HP2-1 conditional allocation counts |
| `C_i` | `major_cn`, `minor_cn`, `total_cn` context |
| `M_i` | mutated-copy multiplicity；sampler以固定 prior邊際化 |
| `P_M,i(m)` | CN-only multiplicity prior |
| `rho_ASCAT` | 外部固定 ASCAT tumor purity；主分析為 `0.99` |

### 2.1 Tree fraction 與 root

```text
phi_v = eta_v + sum(eta_w for w in descendants(v))
```

`eta[0]` 是 tumor population內未由任何建模 clone解釋的 residual mass；它不承載 SNV，也不加入任何 clone的 `phi_v`，因此不能稱為 founding clone。`1-rho_ASCAT` 是 normal contamination，不放進 `eta` simplex，只出現在 observation emission。

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

`rho_ASCAT` 不用來建立 multiplicity prior，也不由 sampler重新估計。LongPhase-S DNA fraction `0.958936` 只留在歷史 provenance。

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

PS欄位不屬於 active likelihood schema。PS block 可在上游 artifact 中用來產生 HP counts，也可在 grouped holdout／audit artifact 中保存；canonical likelihood table 的 sampler loader 不把 PS 當成模型參數或 state。

Loader必須 fail closed：

- integrated table不存在就停止，不讀 legacy default。
- 必要欄位缺失、purity不一致、CN非法或 prior錯誤就停止。
- 不使用 `CN=2`、point multiplicity或舊欄位 fallback。

## 5. 固定輸入與自動推導

### 固定輸入

| 項目 | 角色 |
|---|---|
| bulk REF/ALT | allele-count likelihood |
| HP1-1/HP2-1 counts | conditional HP allocation likelihood |
| major/minor/total CN | VAF denominator與 multiplicity support |
| `multiplicity_prior` | 固定 marginalization weights |
| `rho_ASCAT` | 固定 purity-aware emission參數 |

### sampler自動推導

| 項目 | 意義 |
|---|---|
| `T` | clone tree topology |
| `z_i` | mutation-to-clone assignment |
| `eta_v` | exclusive tumor fraction |
| `phi_v`／CCF | cumulative prevalence |
| topology draws | retained samples保存 `parents`、`eta`、`phi`、`occupancy` |
| assignment summary | 每個 SNV的posterior aggregate與MAP node；不保存逐draw `z_i` |

模型不會從這批資料自動推導 ASCAT purity、major/minor CN、跨PS的全球 HP identity或唯一真實clone數。

## 6. 推理演算法：plain Metropolis–Hastings

目前的 baseline 是一條 chain 使用單一 plain Metropolis–Hastings (MH) kernel。它直接在下列 latent state 上提出整體新 state，再以同一個 posterior target 接受或拒絕：

```text
x = (T, eta, z)
T   = finite-K tree parents
eta = clone exclusive fractions（含 residual eta[0]）
z   = 每個 SNV 的 clone assignment
```

每次 iteration 只提出一個候選 move；move type 可以是固定比例的三種 proposal，但都屬於同一個 MH transition：

1. **SNV assignment move**：選一個 SNV，將 `z_i` 提議到另一個 clone。對稱 proposal 直接比較 target ratio。
2. **`eta` move**：在 simplex 上提出 Dirichlet random-walk；若 proposal 不對稱，接受率包含 reverse/forward proposal-density ratio。
3. **Topology move**：在有限合法 parent support 中提出一個 parent 變更；接受率包含正確的 reverse/forward support ratio。

這個 baseline 不另外抽樣 assignment mixture 或 multiplicity。`z` 的 assignment prior 是固定部分；`m` 則在每個 site likelihood 內用 `multiplicity_prior` 邊際化。每條 chain 的 acceptance rate只描述 proposal行為，不是 convergence proof。

### 6.1 一條 chain 的輸入

`inference/` 的 C++ sampler 只讀 validated `canonical likelihood_input.tsv.gz` 與一份 `ChainConfig`：

| 輸入 | 內容 |
|---|---|
| canonical table | 每列一個 eligible SNV：site key、bulk counts、四個 HP counts、ASCAT major/minor/total CN、`rho_ASCAT`、`multiplicity_candidates`、`multiplicity_prior`、eligibility flags |
| `ChainConfig` | `seed`、finite `num_nodes`、`iterations`、`burnin`、`thin`、固定 `ascat_purity`／`rho_ASCAT` 與 `checkpoint_every` |
| workflow control | 可選 `exclude_ids`（holdout）；這不是新的 biological model parameter。C++ backend 對未完成 chain 的 `resume` 目前 fail-closed |

PS 不需再作為 downstream table 欄位傳入 sampler。它已在上游 LongPhase-S tagging 中協助產生一致的 HP labels，對 sampler 的可見效果只透過 canonical table 的 `H_i` counts 傳遞。

### 6.2 一條 chain 的輸出

- `samples.jsonl.gz`：burn-in 後每個 retained draw 的 `log_posterior`、`parents`、`eta`、`phi`、`occupancy`；assignment 以 posterior summary 與 representative tree 彙整。
- `checkpoint.json.gz`：iteration、目前 `(T, eta, z)`、random-generator state、retained draws、canonical table hash 與 ChainConfig 的 audit/state snapshot；目前不宣稱可由 C++ restore。
- `diagnostics.json`：input/schema/hash、chain config、proposal counters、acceptance rates、posterior sample摘要與 PS 的 upstream/holdout role。
- `representative_tree.json`：由 retained draws 選出的代表 tree、best sample及每個 SNV 的 assignment aggregate/MAP node。
- `chain_complete.json`：完成狀態與已發布 artifact 清單；只有 chain 完整寫出後才存在。

### 6.3 單條 chain 與外層 convergence check

單條 chain sampler 只產生一個 posterior sample stream，不自行宣稱收斂。workflow 另外用相同 canonical table/config 啟動多條不同 seed 的獨立 MH chains，再由外層 diagnostics 計算 R-hat、bulk/tail ESS、label-invariant assignment agreement、edge support 與 holdout predictive metrics。這些 convergence checks 是 workflow 層，不是 MH kernel 的輸入或內部更新。

## 7. 正式實驗設定與 gate

唯一正式執行來源是 [`tumor_tree_pipeline/`](tumor_tree_pipeline/) wrapper。其tree prior是自訂finite-K depth/branching penalty，不是TSSB stick-breaking。舊 `multi_evol_tree/tools/` runner只留作歷史比對。

### 7.1 Staged design

- deterministic 20-site fixture先驗證 schema與 I/O。
- synthetic baseline、topology ambiguity與 CN/LOH+HP missingness情境先過 recovery gate。
- HCC pilot比較 `K=4,6,8`。
- full analysis先跑 `K=6`；通過後追加 `K=4,8`。
- 主 purity為 `0.99`；主分析通過後，再以 `0.97`、`0.95` 做 sensitivity。

正式長鏈起始下限：

```text
4 independent MH chains
1500 iterations
1000 burn-in
thin = 1
>=500 retained draws per chain
```

ESS不足時延長至每鏈至少1,000 retained draws。

### 7.2 Formal gates

- rank-normalized split/folded R-hat `<1.01`。
- bulk與tail ESS total各 `>=400`。
- label-invariant assignment agreement `>=0.90`。
- max edge-support difference `<=0.10`。
- strict holdout 90% predictive coverage `0.85–0.95`，並報告 predictive log score。
- PS-grouped、chromosome-grouped與ASCAT-segment-grouped holdout分別報告；PS-grouped split 以 phase block 為群組，不把 PS 當 likelihood covariate。
- 任一正式gate失敗即回傳非零exit、建立 `_FAILED`，不建立 `_SUCCESS`。

Pilot R-hat `<=1.10` 只用來決定是否繼續，不是正式收斂標準。

## 8. 已知限制

1. finite `K` 是模型容量，不是真實clone數；必須比較 `K=4,6,8`。
2. major/minor CN不能轉稱HP1/HP2 CN；retained-allele orientation仍未識別。
3. site-level CN summary尚未建模完整CN event ordering或segment graph。
4. single bulk sample對部分tree topology不可辨識；topology recovery應單獨報告。
5. HP1-1/HP2-1是read evidence，不是clone label或lineage truth。

## 9. 歷史結果與不相容介面

2026-08-15 的歷史 integrated table使用 `multiplicity_posteriors`：它由同一組bulk counts形成權重，之後舊sampler又使用bulk likelihood。該artifact可能重複使用觀測，不能作為本模型輸入。

歷史I6 baseline為最大label-invariant R-hat `24.983`、最低ESS/chain `3.1`。這些數字只證明舊run未收斂，**不是ASCAT 0.99新版流程的結果**。

歷史PS-wide orientation、Beta-Binomial table、Stage 6 production-like output與experiment-loop pass都不代表目前模型。新版正式輸入只接受 `multiplicity_prior` 與 `rho_ASCAT`，並由 `tumor_tree_pipeline` wrapper驗收。

## 10. 維護規則

1. canonical input變更：同步更新 `data.md`、schema與fixture。
2. likelihood、latent state或proposal變更：同步更新本文件與contract tests。
3. gate或實驗矩陣變更：同步更新workflow、wrapper config與HTML。
4. 大型資料留在Git外；Git保存程式、tests、configs、fixture、manifest與小型診斷摘要。
