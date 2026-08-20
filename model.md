# HCC1395 LongPhase-Clone 模型設計

更新日期：2026-08-19

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
3. `rho_ASCAT=0.99` 只在 emission 與 provenance 生效。
4. PS 不進 likelihood或 MCMC state，只作 read audit、grouped holdout與 provenance。
5. `eta[0]` 是未由任何建模 clone 解釋的 residual tumor mass，不是可承載 SNV 的 founding clone；normal contamination只由 purity處理。

輸出是 candidate tumor-tree posterior，不是 single-cell lineage truth，也不是 HCC1395 唯一真實演化樹。

## 2. Active posterior

```text
P(T, z, eta, pi | D, H, C, P_M, rho_ASCAT)
  proportional to
P(T) * P(eta | T) * P(pi) * P(z | pi)
     * product_i sum_m P_M,i(m)
         P_obs(D_i, H_i | phi_z(i), C_i, m, rho_ASCAT)
```

PS 不出現在條件集合。`P_M,i(m)` 是 CN-only `multiplicity_prior`，不是用同一組 `D_i` 先算出的 posterior。

| 符號 | 定義 |
|---|---|
| `T` | rooted parent-child clone tree |
| `z_i` | mutation `i` 的 clone assignment |
| `eta_v` | clone `v` 的 exclusive tumor fraction |
| `phi_v` | clone `v` 與 descendants 的 cumulative prevalence／CCF |
| `pi_v` | mutation assignment mixture weight |
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

PS不決定 mutation side，不建立 PS-wide orientation variable，也不形成 clone或 edge。

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

PS欄位不屬於 active likelihood schema。若為 grouped holdout攜帶 PS metadata，必須存於獨立 split/audit artifact，不能讓 sampler loader把它當模型參數。

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
| `pi_v` | chain內部更新的 assignment mixture weight；目前不逐draw保存 |
| topology draws | retained samples保存 `parents`、`eta`、`phi`、`occupancy` |
| assignment summary | 每個 SNV的posterior aggregate與MAP node；不保存逐draw `z_i` |

模型不會從這批資料自動推導 ASCAT purity、major/minor CN、跨PS的全球 HP identity或唯一真實clone數。

## 6. 推理演算法

目前使用 compound Metropolis-within-Gibbs：

- **Gibbs sampling**：在其餘 state固定時更新 `z_i` 與 assignment mixture。
- **Metropolis–Hastings**：更新 `eta` 與離散 topology；非對稱 proposal必須加入完整 Hastings correction。
- **Independent eta bridge**：從固定 reference proposal提出較遠的 `eta` 候選，並加入 reverse/forward proposal-density ratio。

目前 sampler 沒有 restricted split–merge kernel；split–merge 只是可供未來改善跨 mode移動的 MH block-move背景。現有更新共享第2節 posterior target。acceptance rate只反映 proposal行為，不證明收斂。

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
4 overdispersed chains
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
- PS-grouped、chromosome-grouped與ASCAT-segment-grouped holdout分別報告。
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
