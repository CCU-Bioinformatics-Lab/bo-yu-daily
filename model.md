# HCC1395 腫瘤演化樹建立

更新日期：2026-08-28

> [!WARNING]
> 本文件定義 active model；PhyClone/PyClone-VI-style `xi`、`error_rate=0.001` 與 CN timing candidates 已同步到 C++/Python emission 與 smoke/contract tests。`error_rate` 與正常 CN=2 是目前 model-side fixed assumptions，尚未成為 canonical input 欄位。輸入與 provenance 以 [`data.md`](data.md) 為準，正式執行契約以 [`experiment_workflow.md`](experiment_workflow.md) 為準。舊 M3／Stage 6 artifact 只可作歷史比較。

```yaml
document_id: model
document_type: model_specification
model_name: tumor_evolutionary_tree_construction
sample: HCC1395
implementation: tumor_tree_pipeline
primary_model: phyclone_compatible_genotype_aware_expected_vaf
formal_status: diagnostic_only_until_model_and_inference_gates_pass
documentation_status: xi_emission_synced_cpp_python;_full_posterior_gates_pending
error_rate: 0.001
links:
  - relation: uses_data_from
    target: data.md
  - relation: inferred_by
    target: inference_algo.md
  - relation: executed_by
    target: experiment_workflow.md
```

## 1. 一頁結論

本文件本輪改以 PhyClone-compatible、genotype-aware expected VAF 作為 primary likelihood 的 target/spec。對每個 SNV，模型應由 bulk REF/ALT、ASCAT major/minor/total CN、暫以 `rho_ASCAT` 對應的 tumour content `t`、clone 的 CCF/`phi`，以及 genotype candidate（包含 CN timing 與 mutated-copy multiplicity）計算 DNA-copy-weighted expected ALT probability `xi`，再評估 allele-count likelihood。`error_rate=0.001` 是本 target/spec 的模型參數。

HP1-1/HP2-1 counts 仍保留在 canonical data 與 audit 中，但不進入 active primary likelihood。multiplicity 與其他 genotype candidate 不由外部工具提供，而是在 emission 中以 candidate prior marginalization 處理。**目前 C++ 與 Python emission 已套用此 `xi` 計算；完整 posterior／predictive／formal gates 仍未因此自動通過。**

七條核心邊界：

1. bulk counts只在 allele-count likelihood 使用一次。
2. genotype candidate support 與 CN working prior 由 ASCAT major/minor/total CN 定義，不是 canonical table 欄位；candidate prior 會在 genotype-aware emission 中邊際化。當前 v4 runtime 使用正常 CN=2，建立 mutation-before-CN 的 `m=1..major_cn` candidates，並在 total CN 非 2 時加入 mutation-after-CN 的 `m=1` candidate。
3. `rho_ASCAT=0.99` 是固定的 purity input，只在 emission 中使用，並在 manifest 中留存 provenance。
4. Model A 是正式 primary baseline：HP counts 不進入 active primary likelihood，僅保留在 input/audit 中供資料檢查。
5. tumor tree 必須只有一個 tumor founder：structural root 只能有一個直接 tumor child，所有其他 clone 都是該 founder 的 descendants；founder 的 `phi` 為 1。
6. clone-specific local fraction $\eta_v$ 表示 finite-K clone 的專屬 tumor-cell fraction；每個 clone 的 $\phi_v$ 由 tree topology `T` 與 $\eta$ 的 descendant sum 推導。normal contamination 只由 purity 處理。
7. target/spec 的 primary emission 使用 `ALT_i ~ Binomial(total_reads_i, xi_i)`；是否升級 Beta-Binomial 由 prior/posterior predictive checks 決定。`error_rate=0.001` 透過 genotype 的 `mu` 定義進入 `xi`。

輸出是 diagnostic candidate tumor-tree posterior，以及每個 SNV 的 `multiplicity_posterior.tsv.gz`；在 inference correctness、canonical input 重建與 predictive checks 完成前，不得稱為正式 posterior tumor tree。它不是 single-cell lineage truth，也不是 HCC1395 唯一真實演化樹。

## 2. Active posterior

```text
P_A(T, z, eta | D, C, rho_ASCAT)
  proportional to
P_K(T) * Dirichlet(eta | alpha(T)) * product_i eta_{z_i}
     * product_i sum_{g in G_i} P_G,i(g | C_i)
         P_bulk(D_i | phi_z(i), C_i, g, rho_ASCAT, error_rate)
```

Model A 是目前應先驗證的 primary posterior。`P_K(T)` 與 `Dirichlet(eta | alpha(T))` 是 finite-K、TSSB-shaped working prior，不是完整的無限 TSSB。`G_i` 是 SNV `i` 的 genotype candidate set，可包含 CN timing、`c_N/c_R/c_V` 與 mutated-copy multiplicity；`P_G,i(g | C_i)` 是 normalized candidate prior。每個 candidate 都先計算 `xi_i(g)`，再以同一組 bulk counts 做 emission，最後對 `g` 邊際化；不會先產生外部 multiplicity table 再重複使用 counts。`product_i eta_{z_i}` 是 assigned clone 的 clone-specific local fraction weighting，不另建立一個獨立的 `pi` state。這套最小 candidate emission 已同步到目前 C++/Python runtime；完整 clone-specific CNV event model 仍是未來範圍。

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

這些常數是目前 finite-K implementation 的 working prior，不是從 HCC1395 資料估計出的生物常數；必須透過 prior predictive tree-depth、branch-count 與 clone-specific local fraction 檢查，並在 sensitivity analysis 中記錄其影響。

| 符號 | 定義 |
|---|---|
| `T` | rooted parent-child clone tree |
| `z_i` | mutation `i` 的 clone assignment |
| $\eta_v$ | clone-specific local fraction；表示只屬於 clone `v`、不包含 descendants 的 tumor-cell fraction；全體 clone 的 $\eta$ 為 simplex |
| $\phi_v$ | clone `v` 加上 descendants 的 cumulative tumor-cell fraction／CCF |
| `D_i` | bulk REF/ALT counts |
| `C_i` | `major_cn`, `minor_cn`, `total_cn` context |
| `M_i` | mutated-copy multiplicity；由模型在每個 SNV 的 emission 中自動評估的 latent state |
| `G_i` | SNV `i` 的 genotype candidate set；包含 CN timing、各 population CN 與 mutated-copy state |
| `P_G,i(g | C_i)` | genotype candidate prior；在 primary likelihood 中對 `g` 做 marginalization |
| `P_M,i(m | C_i)` | `P_G,i` 中的 multiplicity marginal；由 runtime 對不同 CN timing candidates 聚合輸出 |
| `rho_ASCAT` | 外部固定 ASCAT tumor purity；主分析為 `0.99` |
| `t` | tumour content；目前以 `rho_ASCAT` 作 model-side mapping，仍不宣稱兩者在所有 CN 狀態下完全等價 |
| `CCF` / $\phi_v$ | tumor compartment 中帶有該 clone mutation 的 fraction；repo 以 clone `v` 加上 descendants 的 cumulative tumor-cell fraction 表示 |
| `c_N,c_R,c_V` | normal、未帶 mutation 的 tumor reference、帶 mutation 的 tumor variant population 的 total copy number |
| `mu_N,mu_R,mu_V` | 各 population 內 ALT-bearing copies 的比例，並受 `error_rate` 下限與上限約束 |
| `xi` | DNA-copy-weighted expected ALT probability；runtime 與文件的 expected VAF |
| `error_rate` | genotype `mu` 的觀測錯誤下限／上限參數；runtime 固定為 `0.001`，不加入 canonical input |

### 2.1 Tree fraction 與 root

```text
phi_v = eta_v + sum(eta_w for w in descendants(v))
```

$\eta_v$ 是 clone-specific local fraction，表示只屬於 clone `v`、不包含 descendants 的 tumor-cell fraction；所有 K 個 clone 的 $\eta$ 組成 simplex；$\phi_v$ 是該節點加上 descendants 的 cumulative tumor-cell fraction。structural root 只能連接一個 tumor founder `f`，且所有 clone 都在 `f` 的 subtree 中，因此 `phi_f=1`。structural root 不承載 SNV assignment；`1-rho_ASCAT` 是 normal contamination，不放進 $\eta$ simplex，只出現在 observation emission。

```text
exactly one v has parent(v) = structural_root
all other clones are descendants of v
phi_v = 1 for that founder
```

### 2.2 PhyClone-compatible genotype-aware expected VAF

對位點 `i`，令 `CCF_i = phi_z(i)`，並以
`t = rho_ASCAT` 對應 tumour content。三個 DNA population 的權重為：

```text
w_N = 1 - t                 # normal population
w_R = t * (1 - CCF_i)       # tumour cells without the mutation
w_V = t * CCF_i             # tumour cells carrying the mutation
```

每個 genotype candidate `g` 定義三個 population 的 total copy number 與 ALT-copy
fraction：`c_N, c_R, c_V` 以及 `mu_N, mu_R, mu_V`。DNA-copy-weighted
expected ALT probability（expected VAF）為：

```text
xi_i(g) =
    w_N*c_N*mu_N + w_R*c_R*mu_R + w_V*c_V*mu_V
    -----------------------------------------------
              w_N*c_N + w_R*c_R + w_V*c_V
```

`error_rate=0.001` 是 runtime 的 genotype observation floor。若 `a_g` 是該
population 的 ALT-bearing copy 數，則：

```text
mu_g = clamp(a_g / c_g, error_rate, 1 - error_rate)
```

對 normal 與 reference population，`a_N=a_R=0`，所以 target/spec 使用
`mu_N=mu_R=error_rate`；variant population 則由 genotype candidate 的 mutated-copy
state 決定 `a_V`。在 `c_g=0` 的 candidate 中，該 population 的 copy-weighted
contribution 必須為零，且 candidate 必須通過 normalization 檢查。

最小的 PhyClone-compatible candidate 例子是：

```text
pre-CN candidate:
  c_N = normal_cn, c_R = normal_cn, c_V = total_cn
  a_V = m, where m is an allowed mutated-copy multiplicity

post-CN candidate:
  c_N = normal_cn, c_R = total_cn, c_V = total_cn
  a_V = 1
```

其中 `normal_cn`、CN timing、`m` 與其他 genotype state 組成 `G_i`。對每個
candidate 先計算 `xi_i(g)`，再使用：

```text
ALT_i ~ Binomial(total_reads_i, xi_i(g))
```

真正進入 site-level posterior 的 emission 是 candidate prior marginalization：

```text
P_bulk(D_i | phi_z(i), C_i, rho_ASCAT, error_rate)
  = sum_{g in G_i}
      P_G,i(g | C_i) * Binomial(ALT_i | total_reads_i, xi_i(g))
```

這裡的 `P_G,i(g | C_i)` 必須是合法、非負且總和為 1 的 genotype candidate prior；
它可以包含 CN timing、multiplicity 與 allele-specific CN uncertainty。這是本輪
文件的 active emission；**目前 C++/Python 已同步計算 `xi` 與 `error_rate=0.001`**。
正常 CN=2 是 model-side fixed assumption，canonical input 不新增欄位。primary baseline 仍先指定 Binomial；若 posterior predictive
check 顯示 overdispersion，再另立 Beta-Binomial extension。

### VAF–CCF 備註

`xi` 是 expected VAF，不是先驗輸入，也不是把 observed VAF 直接反解成 CCF 的公式。
CCF/`phi` 由 tree topology `T` 與 clone-specific local fraction vector $\eta$ 結構性推導，再透過 candidate-marginalized allele-count
likelihood 受到 reads、purity、CN 與 genotype state 共同約束。因此同一個 observed
VAF 可能由不同的 CCF、CN timing 或 multiplicity 組合產生，不能在一般情況下唯一
反推出 CCF。

`rho_ASCAT` 目前作為 `t` 的 model-side mapping，但 ASCAT purity 與 PhyClone
tumour content 並不宣稱在所有 CN 狀態下語意完全等價。HP counts 不屬於 active
primary likelihood。LongPhase-S DNA fraction `0.958936` 只留在歷史 provenance。

## 3. CN-constrained genotype candidate marginalization

`G_i` 是一個 genotype candidate，不是 clone 數或 CCF。它可以包含 `M_i`（tumor
cell 中攜帶 ALT 的 copy 數）、CN timing、`c_N/c_R/c_V` 與 allele-specific CN
state。可行 support 由 ASCAT major/minor/total CN 限制；目前 runtime 使用正常
CN=2，並已同步建立 candidate construction 與 emission：

```text
major side: m in {1, ..., major_cn}, where allowed by candidate g
minor side: m in {1, ..., minor_cn}, where allowed by candidate g
```

ASCAT major/minor只表示 copy數較多／較少的一側，不能直接命名為 HP1/HP2。

### 3.1 Candidate support 與初始 CN prior

目前 runtime 的 candidate prior 遵循：

1. 建立所有符合 `C_i` 與 CN timing 的 genotype candidate `g`。
2. 每個 candidate 明確記錄 `c_N/c_R/c_V`、`a_N/a_R/a_V`、`mu_N/mu_R/mu_V`。
3. 以 `mu_g = clamp(a_g/c_g, error_rate, 1-error_rate)` 計算 `xi_i(g)`。
4. 對所有合法 candidate 使用 normalized `P_G,i(g | C_i)` 做 marginalization。

公式：

```text
P_G,i(g | C_i) >= 0
sum_g P_G,i(g | C_i) = 1

P_bulk(D_i | phi_z(i), C_i, rho_ASCAT, error_rate)
  = sum_g P_G,i(g | C_i)
        * Binomial(ALT_i | total_reads_i, xi_i(g))
```

genotype candidate prior 可以把同一 CN context 下的 multiplicity 與 CN timing
uncertainty 一起表示；不應把其中一個 multiplicity 先固定成 observed VAF 的函式。
目前 runtime 對 `major_cn=3, minor_cn=1, total_cn=4` 的 candidate prior 示例為：

```text
pre-CN:  m=1,2,3, with prior 1/4 each
post-CN: m=1, with prior 1/4

因此輸出依 multiplicity 聚合後，`m=1` 會合併兩個 timing candidates。
```

以 `major_cn=3, minor_cn=1, total_cn=4` 為例，runtime 建立三個 pre-CN candidates
（`m=1,2,3`）與一個 post-CN candidate（`m=1`），每個 candidate 的 prior 為
`1/4`；輸出層再將兩個 `m=1` 的 posterior responsibility 聚合。canonical table
不保存 `G_i` 或 multiplicity 欄位，candidate set 由 model side 建立。

```text
G_i = {g_1, g_2, ..., g_J}
P_G,i(g_j | C_i) is normalized over the valid candidates
```

若 `minor_cn=0`，只有 nonzero side 可產生 candidate。若沒有可靠 CN segment、
`total_cn=0` 或 candidate set 無法建立有限且正規化的 support，該列不得進
likelihood；不能補成 diploid 或單點 `m=1`。

這個 candidate prior 只負責提供 genotype state 的初始權重，不是最終答案。即使
採用 static-CN input，也必須明確保留 pre-CN/post-CN 等可能性；若 CNV 是
subclonal，單一 bulk segment 仍可能不足以識別真實 genotype。每次 tree／clone
state 提供 `phi_z(i)` 後，runtime 計算：

```text
log w_i(g)
  = log P_G,i(g | C_i)
    + log Binomial(ALT_i | total_reads_i, xi_i(g))

P(G_i=g | D_i, C_i, phi_z(i), rho_ASCAT, error_rate)
  = softmax_g(log w_i(g))
```

SMC 不需要把每個 `g` 另放成一個高維 particle state；target/spec 應在每個
particle 的 tree／clone state 中解析邊際化，並將 conditional responsibility 累積
成 genotype／multiplicity posterior。bulk counts 在 Model A 的 bulk emission 中
使用一次，observed VAF 也不被覆寫。HP counts 不進入本模型的 primary likelihood。

### 3.2 Genotype 與 multiplicity posterior output

目前正式 artifact 仍輸出：

```text
mutation_id  multiplicity  prior  posterior_mean
```

`posterior_mean` 是所有 retained posterior draws 中，依當次 SNV clone assignment、
`phi` 與 `xi` candidate likelihood 計算的 conditional responsibility，並依相同
multiplicity 聚合後的平均值。它表示模型對 multiplicity 的支持程度，不表示 ASCAT
直接量測到該 SNV 的 mutated-copy 數；不同 CN timing candidates 的責任會先合併到
同一個 `m`。每個 SNV 的 multiplicity posterior probabilities 應加總為 1。

這個 output layout 維持既有 artifact schema；目前 runtime 已包含最小
PhyClone/PyClone-VI-style genotype/timing marginalization，但不把 candidate timing
細節另列為 output 欄位。

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
| HP1-1/HP2-1 counts | supplementary evidence；不屬於 active primary likelihood |
| major/minor/total CN | `xi` 的 DNA-copy denominator context，也是 target/spec 建立 genotype candidate support 的來源 |
| CN-constrained genotype candidates | runtime 依 major/minor/total CN 內部建立的 marginalization support／初始 weights，不是 table input |
| multiplicity posterior | 由每個 retained clone/tree state 的 emission responsibility 累積後輸出的 `multiplicity_posterior.tsv.gz` |
| `rho_ASCAT` | 固定 purity-aware emission參數 |

### 模型未知量與結構性推導量

| 項目 | 意義 |
|---|---|
| `T` | clone tree topology；由 inference algorithm 估計或抽樣 |
| `z_i` | mutation-to-clone assignment；由 inference algorithm 估計或抽樣 |
| $\eta_v$ | clone-specific local fraction；由 inference algorithm 估計或抽樣 |
| $\phi_v$／CCF | 由 `T` 與 $\eta$ 結構性推導的 clone plus descendants cumulative tumor-cell fraction |

具體使用哪一種抽樣、最佳化或近似推理方法，見 [`inference_algo.md`](inference_algo.md)。模型本身不規定推理後端，也不會從這批資料自動推導 ASCAT purity、major/minor CN、跨PS的全球 HP identity、CNV event timing 或唯一真實clone數。

## 6. 推理演算法文件

本模型文件只定義 posterior target、觀測 likelihood、prior、latent quantities
與資料邊界，不規定要用 SMC、MAP、Variational Inference 或其他 inference
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
6. HP1-1/HP2-1 是 supplementary read-level evidence，不是 clone label 或 lineage truth。
7. 固定 Binomial 是 baseline assumption；若 predictive checks 顯示 overdispersion，必須另立 Beta-Binomial model。

## 8. 歷史結果與不相容介面

2026-08-15 的歷史 integrated table使用 `multiplicity_posteriors`：它由同一組bulk counts形成權重，之後舊sampler又使用bulk likelihood。該 artifact 不能作為本模型輸入；Model A 的目標是由單一 bulk likelihood 評估流程邊際化並輸出 posterior，避免把 posterior 欄位回填到 canonical input。

歷史I6 baseline為最大label-invariant R-hat `24.983`、最低ESS/chain `3.1`。這些數字只證明舊run未收斂，**不是ASCAT 0.99新版流程的結果**。

歷史PS-wide orientation、Beta-Binomial table、Stage 6 production-like output與experiment-loop pass都不代表目前模型。新版正式輸入只接受 canonical CN／counts／HP／purity 欄位；runtime 由 CN 內部建立 genotype candidates，並以 `xi` 做 candidate marginalization。舊的 multiplicity table 欄位不再是輸入，並由 loader／contract 拒絕。現有舊 formal artifact 若仍使用 `bulk_ref`、`bulk_alt`、`bulk_depth` 或 multiplicity table 欄位，必須重建 canonical input 後才能進入正式流程。

### 8.1 Formal status gate

在下列條件全部完成前，本文件定義的輸出只能標記為 `diagnostic candidate output`：

1. C++ topology state enforce exactly one tumor founder。
2. `eta` independence-MH 補上正確的 forward/reverse proposal-density correction，或改成已證明正確的 update。
3. 以新版 canonical schema 重建 input bundle，並確認 loader 不讀 legacy table。
4. Model A 完成 prior predictive、posterior predictive、multi-chain convergence 與 holdout checks。

## 9. 維護規則

1. canonical input變更：同步更新 `data.md`、schema與fixture。
2. likelihood、latent state或proposal變更：同步更新本文件與contract tests。
3. gate或實驗矩陣變更：同步更新workflow、wrapper config與HTML。
4. 大型資料留在Git外；Git保存程式、tests、configs、fixture、manifest與小型診斷摘要。
