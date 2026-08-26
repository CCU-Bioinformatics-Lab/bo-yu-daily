# HCC1395 腫瘤演化樹建立

更新日期：2026-08-25

> [!WARNING]
> 本文件定義 active model 的目標規格；本輪新增的 PhyClone `xi`／`error_rate=0.001` 尚未同步到 Python、C++、tests 或 config。輸入與 provenance 以 [`data.md`](data.md) 為準，正式執行契約以 [`experiment_workflow.md`](experiment_workflow.md) 為準。舊 M3／Stage 6 artifact 只可作歷史比較。

```yaml
document_id: model
document_type: model_specification
model_name: tumor_evolutionary_tree_construction
sample: HCC1395
implementation: tumor_tree_pipeline
primary_model: phyclone_compatible_genotype_aware_expected_vaf
experimental_extension: hp_long_read_likelihood
formal_status: diagnostic_only_until_model_and_inference_gates_pass
documentation_status: target_spec_only_cpp_not_synchronized
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

HP1-1/HP2-1 counts 仍保留在 canonical data 與 audit 中，但暫時不進入正式 primary topology likelihood；它們會在後續的 Model B 作為 long-read likelihood 擴充。multiplicity 與其他 genotype candidate 不由外部工具提供，而是在 target/spec 中以 candidate prior marginalization 處理。**本輪只修改文件；C++、Python、tests 與 config 尚未同步，因此下文的 `xi` 規格不可宣稱現有 runtime 已實作。**

七條核心邊界：

1. bulk counts只在 allele-count likelihood 使用一次。
2. target/spec 的 genotype candidate support 與 CN working prior 由 ASCAT major/minor/total CN 定義，不是 canonical table 欄位；candidate prior 會在 genotype-aware emission 中邊際化。現有 C++ loader 尚未同步此規格。
3. `rho_ASCAT=0.99` 是固定的 purity input，只在 emission 中使用，並在 manifest 中留存 provenance。
4. Model A 是正式 primary baseline：HP counts 不進入 primary topology likelihood。HP counts、PS block 與 LongPhase-S tag provenance 仍保留供 QC、Model B、grouped holdout 與結果解讀。
5. tumor tree 必須只有一個 tumor founder：structural root 只能有一個直接 tumor child，所有其他 clone 都是該 founder 的 descendants；founder 的 `phi` 為 1。
6. `eta` 只保存 finite-K clone 的 local mass；`phi` 由樹上的 descendant sum 推導。normal contamination 只由 purity 處理。
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

Model A 是目前應先驗證的 primary posterior。`P_K(T)` 與 `Dirichlet(eta | alpha(T))` 是 finite-K、TSSB-shaped working prior，不是完整的無限 TSSB。`G_i` 是 SNV `i` 的 genotype candidate set，可包含 CN timing、`c_N/c_R/c_V` 與 mutated-copy multiplicity；`P_G,i(g | C_i)` 是 normalized candidate prior。每個 candidate 都先計算 `xi_i(g)`，再以同一組 bulk counts 做 emission，最後對 `g` 邊際化；不會先產生外部 multiplicity table 再重複使用 counts。`product_i eta_{z_i}` 是 local-node mass assignment，不另建立一個獨立的 `pi` state。這段是 target/spec；現有 runtime 尚未同步。

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
| `G_i` | SNV `i` 的 genotype candidate set；包含 CN timing、各 population CN 與 mutated-copy state |
| `P_G,i(g | C_i)` | genotype candidate prior；在 primary likelihood 中對 `g` 做 marginalization |
| `P_M,i(m | C_i)` | `P_G,i` 中的 multiplicity marginal；本輪保留作為 target/spec 子狀態，現有 C++ loader 尚未同步 |
| `rho_ASCAT` | 外部固定 ASCAT tumor purity；主分析為 `0.99` |
| `t` | tumour content；本 target/spec 暫以 `rho_ASCAT` 對應，不代表語意已由 runtime 驗證 |
| `CCF` / `phi_v` | tumor compartment 中帶有該 clone mutation 的 cellular prevalence；repo 以 clone `v` 的 cumulative prevalence 表示 |
| `c_N,c_R,c_V` | normal、未帶 mutation 的 tumor reference、帶 mutation 的 tumor variant population 的 total copy number |
| `mu_N,mu_R,mu_V` | 各 population 內 ALT-bearing copies 的比例，並受 `error_rate` 下限與上限約束 |
| `xi` | DNA-copy-weighted expected ALT probability；target/spec 的 expected VAF |
| `error_rate` | genotype `mu` 的觀測錯誤下限／上限參數；target/spec 固定為 `0.001`，尚未加入 canonical input |

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

### 2.2 PhyClone-compatible genotype-aware expected VAF

對位點 `i`，令 `CCF_i = phi_z(i)`，並在本 target/spec 暫以
`t = rho_ASCAT` 對應 tumour content。三個 DNA population 的權重為：

```text
w_N = 1 - t                 # normal population
w_R = t * (1 - CCF_i)       # tumour cells without the mutation
w_V = t * CCF_i             # tumour cells carrying the mutation
```

每個 genotype candidate `g` 定義三個 population 的 total copy number 與 ALT-copy
fraction：`c_N, c_R, c_V` 以及 `mu_N, mu_R, mu_V`。target/spec 的 DNA-copy-weighted
expected ALT probability（expected VAF）為：

```text
xi_i(g) =
    w_N*c_N*mu_N + w_R*c_R*mu_R + w_V*c_V*mu_V
    -----------------------------------------------
              w_N*c_N + w_R*c_R + w_V*c_V
```

`error_rate=0.001` 是 target/spec 的 genotype observation floor。若 `a_g` 是該
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
文件的 target/spec，**現有 C++/Python 尚未同步，不代表 runtime 已計算 `xi` 或
`error_rate=0.001`**。primary baseline 仍先指定 Binomial；若 posterior predictive
check 顯示 overdispersion，再另立 Beta-Binomial extension。

### VAF–CCF 備註

`xi` 是 expected VAF，不是先驗輸入，也不是把 observed VAF 直接反解成 CCF 的公式。
CCF/`phi` 由 tree 與 `eta` 結構性推導，再透過 candidate-marginalized allele-count
likelihood 受到 reads、purity、CN 與 genotype state 共同約束。因此同一個 observed
VAF 可能由不同的 CCF、CN timing 或 multiplicity 組合產生，不能在一般情況下唯一
反推出 CCF。

`rho_ASCAT` 在本 target/spec 暫作 `t` 的對應值，但 ASCAT purity 與 PhyClone
tumour content 的語意仍需在實作與資料驗證階段確認。HP counts 目前不在 Model A
中，因此不會把尚未驗證的 long-read heuristic 混入 CCF posterior。LongPhase-S
DNA fraction `0.958936` 只留在歷史 provenance。

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

## 3. CN-constrained genotype candidate marginalization

`G_i` 是一個 genotype candidate，不是 clone 數或 CCF。它可以包含 `M_i`（tumor
cell 中攜帶 ALT 的 copy 數）、CN timing、`c_N/c_R/c_V` 與 allele-specific CN
state。可行 support 由 ASCAT major/minor/total CN 限制，但 candidate construction
與 emission synchronization 尚未在本輪修改的 runtime 中完成：

```text
major side: m in {1, ..., major_cn}, where allowed by candidate g
minor side: m in {1, ..., minor_cn}, where allowed by candidate g
```

ASCAT major/minor只表示 copy數較多／較少的一側，不能直接命名為 HP1/HP2。

### 3.1 Candidate support 與初始 CN prior

target/spec 的 candidate prior 應遵循：

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

target/spec 的 genotype candidate prior 可以把同一 CN context 下的 multiplicity
與 CN timing uncertainty 一起表示；不應把其中一個 multiplicity 先固定成 observed
VAF 的函式。若沿用 current static-CN working prior 的 side contributions，則
`major_cn=3, minor_cn=1` 可作為 candidate prior 的示例：

```text
P(M=1) = 1/2 + 1/6 = 2/3
P(M=2) = 1/6
P(M=3) = 1/6
```

這只是 prior construction example，不代表所有 CN timing candidate 都只有這三個
state。canonical table 不保存 `G_i` 或 multiplicity 欄位；target/spec 應由 model
side 建立 candidate set。**本輪沒有修改 C++ loader，因此不能宣稱上述 candidate
construction 已在現有 runtime 執行。**

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
state 提供 `phi_z(i)` 後，target/spec 計算：

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
使用一次，observed VAF 也不被覆寫。HP counts 若在 Model B 啟用，必須使用條件式
或 read-level joint likelihood，不能未經證明地再獨立乘上一個 HP likelihood。

### 3.2 Genotype 與 multiplicity posterior output

正式 chain 會輸出：

```text
mutation_id  genotype_candidate  multiplicity  prior  posterior_mean
```

`posterior_mean` 是所有 retained posterior draws 中，依當次 SNV clone assignment、
`phi` 與 `xi` candidate likelihood 計算的 conditional responsibility 平均值。它
表示模型對 genotype/multiplicity state 的支持程度，不表示 ASCAT 直接量測到該 SNV
的 mutated-copy 數。每個 SNV 的 candidate posterior probabilities 應加總為 1。

這個 output layout 是 target/spec；目前 runtime 的既有 artifact schema 尚未因本輪
文件修改而改變。實作同步前，不得把現有 `multiplicity_posterior.tsv.gz` 宣稱為
已經包含完整 PhyClone genotype marginalization 的結果。

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
| major/minor/total CN | `xi` 的 DNA-copy denominator context，也是 target/spec 建立 genotype candidate support 的來源 |
| CN-constrained genotype candidates | target/spec 內部建立的 marginalization support／初始 weights，不是 table input；runtime 尚未同步 |
| multiplicity posterior | 由每個 retained clone/tree state 的 emission responsibility 累積後輸出的 `multiplicity_posterior.tsv.gz` |
| `rho_ASCAT` | 固定 purity-aware emission參數 |

### 模型未知量與結構性推導量

| 項目 | 意義 |
|---|---|
| `T` | clone tree topology；由 inference algorithm 估計或抽樣 |
| `z_i` | mutation-to-clone assignment；由 inference algorithm 估計或抽樣 |
| `eta_v` | exclusive/local clone mass；由 inference algorithm 估計或抽樣 |
| `phi_v`／CCF | 由 `T` 與 `eta` 結構性推導的 cumulative prevalence |

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
6. HP1-1/HP2-1是 read-level somatic evidence，不是 clone label或lineage truth；Model B 尚未通過 generative 與 predictive validation。
7. 固定 Binomial 是 baseline assumption；若 predictive checks 顯示 overdispersion，必須另立 Beta-Binomial model。

## 8. 歷史結果與不相容介面

2026-08-15 的歷史 integrated table使用 `multiplicity_posteriors`：它由同一組bulk counts形成權重，之後舊sampler又使用bulk likelihood。該 artifact 不能作為本模型輸入；Model A 的目標是由單一 bulk likelihood 評估流程邊際化並輸出 posterior，避免把 posterior 欄位回填到 canonical input。

歷史I6 baseline為最大label-invariant R-hat `24.983`、最低ESS/chain `3.1`。這些數字只證明舊run未收斂，**不是ASCAT 0.99新版流程的結果**。

歷史PS-wide orientation、Beta-Binomial table、Stage 6 production-like output與experiment-loop pass都不代表目前模型。新版正式輸入只接受 canonical CN／counts／HP／purity 欄位；本文件 target/spec 要求由 CN 內部建立 genotype candidates，並以 `xi` 做 candidate marginalization，但 C++ loader 與 scorer 尚未同步。舊的 multiplicity table 欄位不再是輸入，並由 loader／contract 拒絕。現有舊 formal artifact 若仍使用 `bulk_ref`、`bulk_alt`、`bulk_depth` 或 multiplicity table 欄位，必須重建 canonical input 後才能進入正式流程。

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
