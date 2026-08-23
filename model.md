# HCC1395 腫瘤演化樹建立

更新日期：2026-08-23

> [!WARNING]
> 本文件定義 active model；輸入與 provenance以 [`data.md`](data.md) 為準，正式執行契約以 [`experiment_workflow.md`](experiment_workflow.md) 為準。舊 M3／Stage 6 artifact只可作歷史比較。

```yaml
document_id: model
document_type: model_specification
model_name: tumor_evolutionary_tree_construction
sample: HCC1395
implementation: tumor_tree_pipeline
primary_model: bulk_cn_purity_multiplicity_baseline
experimental_extension: hp_long_read_likelihood
formal_status: diagnostic_only_until_model_and_inference_gates_pass
links:
  - relation: uses_data_from
    target: data.md
  - relation: inferred_by
    target: inference_algo.md
  - relation: executed_by
    target: experiment_workflow.md
```

## 1. 一頁結論

目前模型先以每個 SNV 的 bulk REF/ALT、ASCAT major/minor/total CN、ASCAT purity 與模型內部的 latent multiplicity，推導 finite-K candidate clone-tree posterior。HP1-1/HP2-1 counts 仍保留在 canonical data 與 audit 中，但暫時不進入正式 primary topology likelihood；它們會在後續的 Model B 作為 long-read likelihood 擴充。multiplicity 不由外部工具提供；C++ loader 先依每列的 major/minor CN 建立可行 support 與初始權重，再由 primary bulk emission、purity、CN 與 clone fraction 共同計算每個候選 multiplicity 的 posterior responsibility。

七條核心邊界：

1. bulk counts只在 allele-count likelihood 使用一次。
2. multiplicity candidate support 與 CN working prior 由 C++ loader 依 ASCAT major/minor CN 建立，不是 canonical table 欄位；primary bulk counts、purity 與 clone fraction 會在 emission 中更新其 posterior responsibility。
3. `rho_ASCAT=0.99` 是固定的 purity input，只在 emission 中使用，並在 manifest 中留存 provenance。
4. Model A 是正式 primary baseline：HP counts 不進入 primary topology likelihood。HP counts、PS block 與 LongPhase-S tag provenance 仍保留供 QC、Model B、grouped holdout 與結果解讀。
5. tumor tree 必須只有一個 tumor founder：structural root 只能有一個直接 tumor child，所有其他 clone 都是該 founder 的 descendants；founder 的 `phi` 為 1。
6. `eta` 只保存 finite-K clone 的 local mass；`phi` 由樹上的 descendant sum 推導。normal contamination 只由 purity 處理。
7. primary emission 先使用固定 sequencing error `e=0.005` 的 Binomial baseline；是否升級 Beta-Binomial 由 prior/posterior predictive checks 決定。

輸出是 diagnostic candidate tumor-tree posterior，以及每個 SNV 的 `multiplicity_posterior.tsv.gz`；在 inference correctness、canonical input 重建與 predictive checks 完成前，不得稱為正式 posterior tumor tree。它不是 single-cell lineage truth，也不是 HCC1395 唯一真實演化樹。

## 2. Active posterior

```text
P_A(T, z, eta | D, C, rho_ASCAT)
  proportional to
P_K(T) * Dirichlet(eta | alpha(T)) * product_i eta_{z_i}
     * product_i sum_m P_M,i(m | C_i)
         P_bulk(D_i | phi_z(i), C_i, m, rho_ASCAT, e)
```

Model A 是目前應先驗證的 primary posterior。`P_K(T)` 與 `Dirichlet(eta | alpha(T))` 是 finite-K、TSSB-shaped working prior，不是完整的無限 TSSB。`P_M,i(m | C_i)` 是 C++ loader 依 CN 建立的 candidate prior，之後同一個 bulk emission 會用 `D_i`、purity 與 clone prevalence 形成 multiplicity posterior；不會先產生外部 multiplicity table 再重複使用 counts。`product_i eta_{z_i}` 是 local-node mass assignment，不另建立一個獨立的 `pi` state。

目前文件採用的實際 finite-K working prior 是：

```text
P_K(T) ∝ exp(
    -0.35 * sum_v depth(v)
    -0.12 * sum_v children(v)^2
) * I(T has exactly one tumor founder)

alpha_v(T) = 0.25
              + 0.75 * exp(-0.65 * (depth(v)-1))
                / (1 + children(v))

eta | T ~ Dirichlet(alpha(T))
```

這些常數是目前 finite-K implementation 的 working prior，不是從 HCC1395 資料估計出的生物常數；必須透過 prior predictive tree-depth、branch-count 與 clone-mass 檢查，並在 sensitivity analysis 中記錄其影響。

Model B 才會加入 HP/long-read likelihood：

```text
P_B(T, z, eta | D, H, C, rho_ASCAT)
  proportional to P_A(T, z, eta | D, C, rho_ASCAT)
                 * product_i P_HP(H_i | D_i, z_i, phi_z(i), C_i, PS_i)
```

Model B 必須先定義 mutated-side latent state、HP tag 的分類錯誤/未標記機率，以及 PS block 內的 orientation 或 read-level linkage；在這些項目與 predictive checks 完成前，`P_HP` 不得併入 Model A 的正式 topology posterior。

| 符號 | 定義 |
|---|---|
| `T` | rooted parent-child clone tree |
| `z_i` | mutation `i` 的 clone assignment |
| `eta_v` | clone `v` 的 local／exclusive tumor mass；全體 clone `eta` 為 simplex |
| `phi_v` | clone `v` 與 descendants 的 cumulative prevalence／CCF |
| `D_i` | bulk REF/ALT counts |
| `H_i` | HP1-1/HP2-1 supplementary counts；保留供 Model B，不是 Model A 的 primary likelihood input |
| `C_i` | `major_cn`, `minor_cn`, `total_cn` context |
| `M_i` | mutated-copy multiplicity；由模型在每個 SNV 的 emission 中自動評估的 latent state |
| `P_M,i(m | C_i)` | 由 C++ loader 依 major/minor CN 建立的 CN working prior；Model A 的 bulk counts/CN/purity/clone fraction 會形成 posterior responsibility |
| `rho_ASCAT` | 外部固定 ASCAT tumor purity；主分析為 `0.99` |

### 2.1 Tree fraction 與 root

```text
phi_v = eta_v + sum(eta_w for w in descendants(v))
```

`eta_v` 是 clone `v` 的 local mass，所有 K 個 clone 的 `eta` 組成 simplex；`phi_v` 是該節點加上 descendants 的總 mass。structural root 只能連接一個 tumor founder `f`，且所有 clone 都在 `f` 的 subtree 中，因此 `phi_f=1`。structural root 不承載 SNV assignment；`1-rho_ASCAT` 是 normal contamination，不放進 `eta` simplex，只出現在 observation emission。

```text
exactly one v has parent(v) = structural_root
all other clones are descendants of v
phi_v = 1 for that founder
```

### 2.2 Purity-aware allele emission

位點 `i` 分配到 clone `z_i` 且 multiplicity為 `m` 時：

```text
q_i = rho_ASCAT * phi_z(i) * m
      / ((1-rho_ASCAT)*2 + rho_ASCAT*C_i,total)
```

目前 primary baseline 使用固定全域 sequencing error `e=0.005`，不是每個位點一個未定義的 `e_i`：

```text
r_i = e + (1-2*e)*q_i,  e=0.005
ALT_i ~ Binomial(total_reads_i, r_i)
```

這是第一版 baseline，不代表已證明所有位點都符合等變異 Binomial。正式使用前要做 prior predictive 與 posterior predictive checks；若 ALT-count dispersion、coverage 或 holdout log score 顯示 Binomial 不足，才另立 Beta-Binomial extension。

### VAF–CCF 備註

在簡化的 bulk sequencing 模型中，CCF 通常可由 VAF、tumor purity、local copy number 與 mutation multiplicity 共同換算估計。忽略 sequencing error，將上式反解可得：

```text
CCF_i ≈ VAF_i * ((1-rho_ASCAT)*2 + rho_ASCAT*CN_i,total)
        / (rho_ASCAT*m_i)
```

在 purity、local CN 與 `m_i` 已知，且位點為 CN-stable、正常細胞不帶 ALT、技術偏差可忽略時，這個反解可作為 CCF 的近似估計。若是 diploid、`m_i=1` 且無 sequencing error，則簡化為：

```text
CCF_i ≈ 2 * VAF_i / rho_ASCAT
```

但 VAF 不是 CCF 的直接觀測值，CCF 也不是任意情況下都能由 VAF 唯一換算。未知 multiplicity、CNV/LOH、purity 語意差異、測序誤差與 read/mapping bias 都會使同一個 VAF 對應多個可能的 CCF。`rho_ASCAT` 也不能與 tumor DNA fraction 未經轉換地混用。

本模型的 `phi_v`／CCF 是 clone `v`（含 descendants）在 tumor compartment 中的累積細胞比例，由樹結構 `T` 與 local mass `eta` 推導；它不是把 observed VAF 直接轉換而來。Model A 使用 bulk REF/ALT counts、`rho_ASCAT`、local CN、latent multiplicity 與固定 sequencing error 共同進入 observation likelihood。HP counts 目前不在 Model A 中，因此不會把尚未驗證的 long-read heuristic 混入 CCF posterior。

`rho_ASCAT` 不用來建立 candidate support，但會參與 multiplicity posterior 所依賴的 observation emission，也不由 inference algorithm 重新估計。LongPhase-S DNA fraction `0.958936` 只留在歷史 provenance。

### 2.3 HP observation（Model B，暫不屬於 primary likelihood）

LongPhase-S 的 `HP:Z:1-1` 與 `HP:Z:2-1` 是 somatic ALT-supporting read tags，可提供 long-read haplotype evidence，但它們不是獨立於 ALT call 的新一批 reads。Model B 必須明確描述 tagged-read 的產生與錯誤機率，才能讓 HP counts 正確改變 posterior。

目前 active C++ primary scorer 不包含 HP heuristic，也不會把 tagged fraction 或 HP1/HP2 side 假設乘進 Model A。HP counts 只做 schema／conservation validation；若要讓 HP 改變 posterior，必須另行完成 Model B 的 generative definition、tag/error model 與 predictive validation。

不能把 bulk counts 與其子集合 HP counts 當成兩批獨立 reads 重複相乘。等價記帳可寫成六類互斥 categories：

```text
HP1-1_REF, HP1-1_ALT,
HP2-1_REF, HP2-1_ALT,
untagged_REF, untagged_ALT
```

PS block 先讓同一 phase block 內的 `HP1-1`／`HP2-1` labels 維持一致；跨不同 PS block 的 HP label 不假設具有全球一致方向。PS 不直接決定 mutation side、不建立 downstream 的 PS-wide orientation variable，也不形成 clone 或 edge。

Model B 的最低驗證要求是：保留 read/PS provenance、明確處理未標記與 ambiguous tags、檢查同一 PS block 的 label consistency，並比較加入 HP 前後的 grouped holdout、posterior predictive coverage、assignment stability 與 edge support。若 HP 只改善訓練 likelihood、卻沒有改善 holdout 或造成 topology 過度集中，不能宣稱它提供有效 long-read 增益。

## 3. CN-constrained latent multiplicity inference

`M_i` 是一個 tumor cell中攜帶 ALT的 copy數，不是 clone數或 CCF。可行 support由 extant ASCAT sides決定：

```text
major side: m in {1, ..., major_cn}
minor side: m in {1, ..., minor_cn}
```

ASCAT major/minor只表示 copy數較多／較少的一側，不能直接命名為 HP1/HP2。

### 3.1 Candidate support 與初始 CN prior

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

canonical table 不保存 multiplicity 欄位。C++ loader 讀到 `major_cn=3`、`minor_cn=1` 後，在記憶體內得到：

```text
m support = {1, 2, 3}
P_M(1), P_M(2), P_M(3) = 0.666667, 0.166667, 0.166667
```

若 `minor_cn=0`，major side取得全部 weight。若沒有可靠 CN segment、`total_cn=0` 或 loader 無法建立有限且正規化的 support，該列不得進 likelihood；不能補成 diploid或單點 `m=1`。

這個 CN prior 只負責提供候選狀態的初始權重，不是最終答案。它是 ASCAT static-CN working model，不等同完整 PhyloWGS CNV model；目前沒有 CNV cellular prevalence、CNV node placement 或 SNV-CNV timing，因此不能從本模型輸出 CNA event 的演化順序。每次 tree／clone state 提供 `phi_z(i)` 後，Model A 計算：

```text
log w_i(m)
  = log P_M,i(m | C_i)
    + log P_bulk(D_i | phi_z(i), C_i, m, rho_ASCAT, e)

P(M_i=m | D_i, C_i, phi_z(i), rho_ASCAT)
  = softmax_m(log w_i(m))
```

MCMC 不需要把每個 `m` 另放成一個高維 state；它在每個 retained tree／clone state 中被解析邊際化，並將 conditional responsibility 累積成 `multiplicity_posterior.tsv.gz`。因此 bulk counts 在 Model A 的 bulk emission 中使用一次，observed VAF 也不被覆寫。HP counts 若在 Model B 啟用，必須使用條件式或 read-level joint likelihood，不能未經證明地再獨立乘上一個 HP likelihood。

### 3.2 Multiplicity posterior output

正式 chain 會輸出：

```text
mutation_id  multiplicity  prior  posterior_mean
```

`posterior_mean` 是所有 retained posterior draws 中，依當次 SNV clone assignment 與 `phi` 計算的 conditional responsibility 平均值。它表示模型對 latent multiplicity 的支持程度，不表示 ASCAT 直接量測到該 SNV 的 mutated-copy 數。每個 SNV 的 posterior probabilities 應加總為 1。

另外輸出：

- `posterior_summary.tsv.gz`：每個 candidate clone 的 `phi`／CCF posterior median、2.5% 與 97.5% quantile。
- `topology_summary.tsv`：對 retained trees 做 clone-label canonicalization 後的 parent-child edge support；跨 chain/K 的比較由 workflow 負責。

## 4. 模型實際讀取表

Canonical schema：

```text
mutation_id
chrom pos ref alt
ref_reads alt_reads total_reads
hp1_1_ref hp1_1_alt hp2_1_ref hp2_1_alt
major_cn minor_cn total_cn
rho_ASCAT
model_include model_status
```

每列是一個 SNV。只有 `model_include=yes`、`model_status=eligible` 的列進 likelihood；CN=0、unmapped、zero-depth或其他排除列留在表與 manifest中供 audit。

PS欄位不屬於 active likelihood schema。PS block 可在上游 artifact 中用來產生 HP counts，也可在 grouped holdout／audit artifact 中保存；canonical likelihood table 的 inference loader 不把 PS 當成模型參數或 state。

Loader必須 fail closed：

- integrated table不存在就停止，不讀 legacy default。
- 必要欄位缺失、purity不一致、CN非法或 loader 無法建立內部 multiplicity distribution 就停止。
- 不使用 `CN=2`、point multiplicity或舊欄位 fallback。

## 5. 固定輸入與模型狀態

### 固定輸入

| 項目 | 角色 |
|---|---|
| bulk REF/ALT | allele-count likelihood |
| HP1-1/HP2-1 counts | supplementary long-read evidence；Model B、QC 與 holdout 使用，暫不屬於 Model A primary likelihood |
| major/minor/total CN | VAF denominator，也是 C++ loader 建立 multiplicity support 的來源 |
| CN-constrained multiplicity candidates | C++ loader 內部建立的 marginalization support／初始 weights，不是 table input |
| multiplicity posterior | 由每個 retained clone/tree state 的 emission responsibility 累積後輸出的 `multiplicity_posterior.tsv.gz` |
| `rho_ASCAT` | 固定 purity-aware emission參數 |

### 模型未知量與結構性推導量

| 項目 | 意義 |
|---|---|
| `T` | clone tree topology；由 inference algorithm 估計或抽樣 |
| `z_i` | mutation-to-clone assignment；由 inference algorithm 估計或抽樣 |
| `eta_v` | exclusive/local clone mass；由 inference algorithm 估計或抽樣 |
| `phi_v`／CCF | 由 `T` 與 `eta` 結構性推導的 cumulative prevalence |

具體使用哪一種抽樣、最佳化或近似推理方法，見 [`inference_algo.md`](inference_algo.md)。模型本身不規定 MCMC，也不會從這批資料自動推導 ASCAT purity、major/minor CN、跨PS的全球 HP identity、CNV event timing 或唯一真實clone數。

## 6. 推理演算法文件

本模型文件只定義 posterior target、觀測 likelihood、prior、latent quantities
與資料邊界，不規定要用 MCMC、MAP、Variational Inference 或其他 inference
algorithm。當前 active algorithm、chain input/output、平行化邊界與 algorithm
backend abstraction 見 [`inference_algo.md`](inference_algo.md)。

正式執行入口、K／purity sensitivity、chain 數、holdout、convergence metrics
與 fail-closed gates 見 [`experiment_workflow.md`](experiment_workflow.md)；這些是 workflow contract，不在 model spec 內重複定義。

## 7. 已知限制

1. finite `K` 是模型容量，不是真實clone數；必須比較 `K=4,6,8`。
2. primary model 假設單一 tumor founder；若資料支持多重 founder，必須另立模型，不能默默放寬此約束。
3. major/minor CN不能轉稱HP1/HP2 CN；retained-allele orientation仍未識別。
4. static-CN model 尚未建模 CNV cellular prevalence、CNV event ordering、CNV node placement 或 segment graph。
5. single bulk sample對部分tree topology不可辨識；topology recovery應單獨報告。
6. HP1-1/HP2-1是 read-level somatic evidence，不是 clone label或lineage truth；Model B 尚未通過 generative 與 predictive validation。
7. 固定 Binomial 是 baseline assumption；若 predictive checks 顯示 overdispersion，必須另立 Beta-Binomial model。

## 8. 歷史結果與不相容介面

2026-08-15 的歷史 integrated table使用 `multiplicity_posteriors`：它由同一組bulk counts形成權重，之後舊sampler又使用bulk likelihood。該 artifact 不能作為本模型輸入；Model A 的目標是由單一 bulk likelihood 評估流程邊際化並輸出 posterior，避免把 posterior 欄位回填到 canonical input。

歷史I6 baseline為最大label-invariant R-hat `24.983`、最低ESS/chain `3.1`。這些數字只證明舊run未收斂，**不是ASCAT 0.99新版流程的結果**。

歷史PS-wide orientation、Beta-Binomial table、Stage 6 production-like output與experiment-loop pass都不代表目前模型。新版正式輸入只接受 canonical CN／counts／HP／purity 欄位；C++ loader 由 CN 內部建立 multiplicity candidates，Model A likelihood 解析邊際化並輸出 per-SNV posterior。舊的 multiplicity table 欄位不再是輸入，並由 loader／contract 拒絕。現有舊 formal artifact 若仍使用 `bulk_ref`、`bulk_alt`、`bulk_depth` 或 multiplicity table 欄位，必須重建 canonical input 後才能進入正式流程。

### 8.1 Formal status gate

在下列條件全部完成前，本文件定義的輸出只能標記為 `diagnostic candidate output`：

1. C++ topology state enforce exactly one tumor founder。
2. `eta` independence-MH 補上正確的 forward/reverse proposal-density correction，或改成已證明正確的 update。
3. 以新版 canonical schema 重建 input bundle，並確認 loader 不讀 legacy table。
4. Model A 完成 prior predictive、posterior predictive、multi-chain convergence 與 holdout checks。
5. HP Model B 若要進入 primary likelihood，另完成 mutated-side、tag error、PS/read linkage 與增益驗證；在此之前 HP 只作 supplementary evidence。

## 9. 維護規則

1. canonical input變更：同步更新 `data.md`、schema與fixture。
2. likelihood、latent state或proposal變更：同步更新本文件與contract tests。
3. gate或實驗矩陣變更：同步更新workflow、wrapper config與HTML。
4. 大型資料留在Git外；Git保存程式、tests、configs、fixture、manifest與小型診斷摘要。
