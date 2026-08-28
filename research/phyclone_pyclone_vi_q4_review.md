# PhyClone / PyClone-VI：Q4 evidence review

> Scope: 釐清 PyClone-VI 是否是 VAF→CCF 的前置作業、它是否使用
> tumour content（purity/cellularity）、copy number 與 mutated-copy
> multiplicity、PhyClone 如何接收它，以及 Q4 的候選正式模型。
>
> Decision boundary: 本 note originally recorded the evidence without selecting
> Q4. On 2026-08-28 the user confirmed Candidate B and asked for it to be
> applied; the implementation status is now recorded below.
> Q5=C 已確認：保留原本 CCF/`phi` 語意，將疑似 mutation loss 的位點標記為
> outlier，而不是現在就改成 DCF。這個使用者決定與本 repo 的 ADR 記錄在
> [`docs/adr/0001-multiplicity-emission-and-cnv-timing.md:77`](/bip8_disk/boyu114/main_work/docs/adr/0001-multiplicity-emission-and-cnv-timing.md:77)。

## 1. Short answer

### 1.1 PyClone-VI 是不是 VAF→CCF 的前置作業？

答案要分成兩層：

1. **Workflow 層：是。** PhyClone 官方 README 建議先用 PyClone-VI 做
   mutation pre-clustering，並說 PyClone-VI 的輸出可以直接作為 PhyClone
   的 cluster file。PyClone-VI 的輸出包含 `cellular_prevalence`、
   `cellular_prevalence_std` 與 `cluster_assignment_prob`；其中
   `cellular_prevalence` 被 README 定義為 CCF。[PhyClone README 的 cluster
   input 說明](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L271-L291)、
   [PhyClone README 的 PyClone-VI workflow](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L421-L432)、
   [PyClone-VI README 的 output format](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L106-L122)

2. **Statistical model 層：不是一個單純的 VAF→CCF 點轉換器。**
   PyClone-VI 保留 `ref_counts`／`alt_counts`，對一組 CCF grid 中的每個
   候選值計算 read-count likelihood，再用 variational inference 推斷
   CCF 分布與 cluster assignment。原始論文將這個模型寫成 CCF 的離散
   候選集合與 allele-count emission，而不是一條先把 observed VAF 直接
   反解成 CCF 的公式。[PyClone-VI 原始論文，模型與 inference](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/#Sec8)

因此最準確的說法是：

> PyClone-VI 是 PhyClone 可選的 **copy-number-aware CCF inference / mutation
> pre-clustering stage**，不是獨立的 deterministic `VAF -> CCF` correction。

這個區分很重要，因為 PhyClone 之後仍會讀取原始 allele counts、copy number
與 tumour content，並重新建立自己的 PyClone likelihood；它不是只把
PyClone-VI 輸出的 CCF 當作固定觀測值。[PhyClone `run.py` 的 `load_data`
呼叫](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/run.py#L12-L80)、
[PhyClone `data/pyclone.py` 的 likelihood-grid 建立](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L277-L326)

### 1.2 PyClone-VI 有沒有使用 purity、CN、multiplicity？

| 項目 | 證據與精確說法 |
|---|---|
| purity | 有使用相同概念的 `tumour_content`／cellularity；官方輸入欄位不是命名為 `purity`。缺欄位時程式預設 `tumour_content=1.0`。[official README](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L97-L105)、[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L101-L108) |
| copy number | 有；輸入 `major_cn`、`minor_cn`、`normal_cn`，並由程式建立每個 SNV 的 CN context。[official README](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L84-L105)、[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L81-L98) |
| multiplicity | 有等價的 mutated-copy/genotype candidates，但官方程式沒有把它命名成獨立變數 `m`。`get_major_cn_prior` 會列出 `x=1,...,major_cn` 的 variant-allele fractions `x/total_cn`，並在 total CN 與 normal CN 不同時加入 mutation-after-CN candidate。[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L148-L171) |
| sequencing error | 有；`error_rate` 會進入 normal/reference 與 variant genotype 的 `mu`，缺欄位時預設 `0.001`。[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L81-L96)、[official README](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L97-L105) |
| observed VAF | 不會先覆寫或修改 observed VAF；程式使用 ref/alt counts 建立 binomial 或 beta-binomial emission。[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L239-L301) |

## 2. PyClone-VI 的實際 emission：不是先做一張固定轉換表

### 2.1 Input 與 latent CCF

PyClone-VI 接收每個 mutation/sample 的：


\[
(
\mathrm{ref\_counts},
\mathrm{alt\_counts},
\mathrm{major\_cn},
\mathrm{minor\_cn},
\mathrm{normal\_cn},
\mathrm{tumour\_content}
)
\]

官方 README 明列了這些 input 欄位；輸出則將 `cellular_prevalence` 定義為
malignant cells 中帶有該 mutation 的比例，也就是文獻中常稱的 CCF。[PyClone-VI
official README input](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L70-L105)、
[PyClone-VI official README output](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L106-L122)

原始論文的 PyClone-VI model 將 CCF 限制在有限集合

\[
\mathbf{\Phi}
=
\left\{
0,\frac{1}{F},\ldots,\frac{F-1}{F},1
\right\},
\]

並對每個 cluster/sample 的 CCF 分布做 variational inference。[PyClone-VI
原始論文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/#Sec9)

### 2.2 CN/genotype candidate 如何進入 expected VAF

在 official `data.py` 中，對固定 CCF `f` 與某個 genotype candidate `c`，
先建立三種細胞群的比例：

\[
w_N=1-t,
\qquad
w_R=t(1-f),
\qquad
w_V=tf,
\]

其中 `t` 是 `tumour_content`，`f` 是候選 CCF。這三群分別對應正常細胞、
腫瘤細胞中不帶 mutation 的部分，以及腫瘤細胞中帶 mutation 的部分。
這些權重直接對應 official code 中的 `population_prior`。[official
`data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L239-L247)

對 candidate `c`，程式再以該 candidate 的 copy number `cn[c,i]` 與
variant-allele fraction `mu[c,i]` 計算 expected ALT fraction：

\[
\xi_c(f)
=
\frac{
\sum_{i\in\{N,R,V\}}w_i\,c_{c,i}\,\mu_{c,i}
}{
\sum_{i\in\{N,R,V\}}w_i\,c_{c,i}
}.
\]

這個公式是將 official code 的 `e_cn`、`e_vaf` 與 `norm_const` 改寫成數學
表示；程式在 `data.py` 的 lines 251–263（beta-binomial）與 lines 286–297
（binomial）逐項做同樣的計算。[official `data.py` beta-binomial](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L239-L270)、
[official `data.py` binomial](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L273-L301)

### 2.3 Multiplicity 在哪裡？

`get_major_cn_prior` 的核心行為是：

```text
candidate 1: variant fraction = 1 / total_cn
candidate 2: variant fraction = 2 / total_cn
...
candidate major_cn: variant fraction = major_cn / total_cn
```

這些 candidate 是由 `major_cn` 與 `minor_cn` 所限制的 mutated-copy/genotype
可能性；若 total CN 改變，程式另加一個 mutation-after-CN candidate，其
variant fraction 為 `1/total_cn`。每個 candidate 都保存 `cn`、`mu` 和
`log_pi`，之後進入 emission。[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L148-L171)

因此可用下列對照理解：

\[
m \quad\text{（本 repo 的名稱）}
\Longleftrightarrow
\text{PyClone-VI candidate 中的 mutated-copy count / genotype state}
\]

但不能說 PyClone-VI 的 source 有一個名為 `m` 的 persistent variable；它是
candidate array 中的 genotype/mutated-copy information。[official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L207-L224)

固定 CCF `f` 後，PyClone-VI 對所有 candidate 產生 likelihood，再做
`log_sum_exp`：

\[
\log p(D\mid f)
=
\log\sum_{c\in\mathcal C_i}
\exp\left[
\log \pi_{i,c}
+
\log p(D_i\mid \xi_{i,c}(f))
\right].
\]

這就是 multiplicity/genotype candidate 的 likelihood marginalization；它
不會先產生一個固定的 `VAF_corrected` 欄位再交給 CCF clustering。[official
`data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L239-L301)

### 2.4 CCF 是怎麼輸出的？

PyClone-VI 將每個 cluster/sample 的 CCF posterior 近似放在 `theta` 的 CCF
grid 上，再用 grid 的期望值與變異計算 `cellular_prevalence` 和
`cellular_prevalence_std`；mutation 的 cluster label 與 assignment probability
則由 variational `z` 取最大值。[official `post_process.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/post_process.py#L14-L33)、
[official `post_process.py` 的 CCF summary](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/post_process.py#L36-L75)

所以流程不是：

\[
\mathrm{observed\ VAF}
\xrightarrow{\text{one fixed formula}}
\mathrm{CCF}
\xrightarrow{}
\mathrm{PhyClone}.
\]

比較準確的是：

```text
REF/ALT counts + CN + tumour content
        ↓
建立 genotype/mutated-copy candidates
        ↓
對 CCF grid 的每個 f 計算 expected ALT probability 與 read likelihood
        ↓
PyClone-VI 以 VI 推斷 CCF 分布與 mutation clusters
        ↓  optional pre-clustering input
PhyClone 用 cluster IDs 協助樹搜尋，並對原始 counts 重新計算自己的 emission
```

上圖的前半段由 PyClone-VI official `data.py` 與 `post_process.py` 實作；後半段
由 PhyClone 的 workflow README、`run.py` 和 `data/pyclone.py` 實作。[PyClone-VI
official data code](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L40-L98)、
[PhyClone workflow README](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L271-L291)、
[PhyClone `run.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/run.py#L12-L80)

## 3. PhyClone 如何使用 PyClone-VI？

### 3.1 是外部兩階段 workflow，不是 PhyClone 內部直接 import PyClone-VI

PhyClone 官方 README 將分析分為：

1. 準備 main input：原始 ref/alt counts、major/minor/normal CN、tumour content。
2. 可選地準備 cluster file；README 建議這個 cluster file 由 PyClone-VI
   產生，且格式可以直接餵給 PhyClone。[PhyClone README main/cluster input](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L222-L291)
3. 執行 `phyclone run -i INPUT.tsv -c CLUSTERS.tsv ...`。[PhyClone README
   run command](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L298-L326)

PhyClone 的 `run.py` import 的是自己的 `phyclone.data.pyclone.load_data`，
不是 `pyclone_vi`；它將 main input 送進自己的 `load_data`。[PhyClone
`run.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/run.py#L6-L24)、
[PhyClone `run.py` load call](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/run.py#L69-L80)

### 3.2 PhyClone 不把 PyClone-VI 的 CCF 當成固定 CCF observation

PhyClone paper 說明 pre-clustering 的作用是計算效率：一起被 pre-cluster 的
mutations 會被保持在一起，但原本不同的 clusters 仍可在 PhyClone 中合併；
PhyClone 也可以不做 pre-clustering，只是 WGS 的計算量會增加。[PhyClone
原始論文 §2.2.2](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec5)

這代表 PyClone-VI 的 cluster ID 是一種樹搜尋的 grouping constraint/starting
information，不是把每個 mutation 的 CCF 以點估計鎖死。PhyClone 的 data loader
會從 main input 建立 `PyCloneDataPoint`，對 CCF grid 呼叫自己的
`to_likelihood_grid`；若有 cluster file，程式只將 cluster assignments 與
PyClone data 合併成 clustered data point，仍然使用原始 counts 與 CN。[official
PhyClone `data/pyclone.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L14-L65)、
[official PhyClone clustered data construction](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L75-L105)

### 3.3 PhyClone 自己的 tree-layer 與 emission-layer

PhyClone paper 在 tree layer 定義 clonal prevalence `rho`，並以 tree descendant
sum 得到 cellular prevalence `bar rho`：

\[
\bar\rho_v
=
\sum_{u\in V_v}\rho_u.
\]

這一層是樹上的 clone/cell fraction 關係；paper 接著明確說 allele-count
likelihood `f(x_n | bar rho_v)` 是由 copy number 與 tumour content 修正的
PyClone likelihood。[PhyClone 原始論文 §2.1–2.2](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)

PhyClone official code 中，這個 emission 的 candidate loop 仍然存在：它以
`population_prior = [1-t, t*(1-f), t*f]` 建立三類細胞比例，利用 `cn` 與 `mu`
計算 `e_vaf`，再對 candidate likelihood 做 `log_sum_exp`。[official
PhyClone `math_utils.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/utils/math_utils.py#L919-L995)

因此：

> PhyClone 的 descendant-sum 不需要 multiplicity；但它用來解釋 read counts
> 的 PyClone emission 仍使用 CN/genotype candidate marginalization。

這也解釋為什麼只看 PhyClone 主文的 `rho -> bar rho` 方程式或最終輸出表格，
會誤以為 PhyClone 完全沒有 multiplicity。它沒有把 candidate state 以
`multiplicity` 欄位呈現在主要 tree output；candidate 是 emission 內部計算。[PhyClone
paper §2.2](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)、
[official PhyClone `data/pyclone.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L301-L326)

## 4. 和目前 repo 的差異

### 4.1 Current repo：有 multiplicity，但 emission 比 PyClone-VI/PhyClone 簡化

目前 repo 的 C++ loader 從 `major_cn` 與 `minor_cn` 建立 multiplicity candidates
與 prior；例如每個 side 內均勻分配，再將 major/minor sides 的 mass 合併。[current
repo `model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:128)

目前 production emission 是：

\[
q_{\mathrm{repo}}(\phi,m)
=
\operatorname{clip}
\left(
\frac{
\rho_{\mathrm{ASCAT}}\phi m
}{
2(1-\rho_{\mathrm{ASCAT}})
+
\rho_{\mathrm{ASCAT}}\,CN_i
},
10^{-12},1-10^{-12}
\right).
\]

並對 multiplicity candidate 做：

\[
L_i(\phi)
=
\sum_{m\in M_i}
\pi_i(m)
P(D_i\mid q_{\mathrm{repo}}(\phi,m)).
\]

這兩個行為分別在 [`model.cpp:206`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:206)
與 [`model.cpp:255`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:255)。

### 4.2 PyClone-VI/PhyClone-style candidate emission 的差異

| 層次 | 目前 repo | PyClone-VI / PhyClone-style emission |
|---|---|---|
| CCF input | `phi` 由 tree/eta 推導 | PyClone-VI 對 CCF grid 做 inference；PhyClone 對 tree-derived cellular prevalence 做 inference |
| tumour content | `rho_ASCAT` 進入簡化 denominator | `tumour_content=t` 形成 normal/non-mutant/mutant 三群權重 |
| CN | 使用 normal/reference/variant 三群的 copy-number-weighted denominator；major/minor 建立候選的 `cn` | 使用 major/minor/normal CN 建立 candidate-specific `cn` |
| multiplicity | 以候選 genotype 的 mutated-copy count 表示，對 candidate likelihood 做 log-sum-exp | 以 `mu`、genotype/copy-number candidate 表示，對 candidate likelihood 做 log-sum-exp |
| mutation timing | 目前最小 candidate set 包含 mutation-before/after-CN 的 emission possibilities；更完整 timing/phase 仍需更豐富 event model | PyClone-VI 的 candidate support 至少包含 mutation-before/after-CN 的 emission possibilities |
| sequencing error | 使用 model-side `error_rate=0.001` 產生 candidate-specific `mu` | `error_rate` 進入 candidate `mu`，預設為 `0.001` |
| output | 另輸出 `multiplicity_posterior.tsv.gz` | PyClone-VI standard output 主要是 cluster/CCF/assignment probability；PhyClone standard output 主要是 tree、assignment、CCF/clonal prevalence |

表中 current repo 的 claim 可由 [`model.hpp:32-48`](/bip8_disk/boyu114/main_work/inference/include/tumor_tree_inference/model.hpp:32)
與 [`algorithm.cpp:1158-1164`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:1158)
核對；PyClone-VI/PhyClone 的 claim 可由上列 official source locators 核對。

目前 repo 的 `m` 確實是 latent emission variable，且 active runtime 已同步
最小版的 candidate-specific `c_N/c_R/c_V`、`mu` 與 mutation-before/after-CN
candidate 計算；它仍不等同於 PhyClone/DeCiFer 那種完整的 clone-specific
genotype/event history。[current
repo `model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:239)、
[official PyClone-VI `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L148-L171)

## 5. Q4 的候選正式模型與已確認決定

### 5.0 Coordinator 的 evidence-based recommendation

若 Q4 問的是「正式 likelihood 應採用哪一種 VAF/CCF emission」，本次查核的
推薦是 **Candidate B：integrated PhyClone-compatible `xi` emission**。理由是
它保留目前候選腫瘤演化樹的 `T`、`eta` 與由 descendants 推導的 `phi`，但把
purity/tumour content、CN、mutated-copy/genotype candidates、sequencing error
與 read counts 放進同一個 emission；它也最接近 PhyClone/PyClone-VI 官方程式碼的
實際計算方向。

Candidate C（先跑 PyClone-VI 做 pre-clustering）可以是之後的**工作流程加速選項**，
但不應取代 Candidate B 的正式 emission。換句話說，PyClone-VI 的 CCF summary
不是固定真值，也不是把 observed VAF 先改寫成一欄 CCF 後再交給樹模型。

使用者已於 2026-08-28 確認採用 **Candidate B**；目前 C++/Python 都已同步
實作並有 deterministic candidate/xi contract tests。`q_repo` 保留在研究紀錄
中作為歷史 baseline，不再是 active scorer。完整 predictive、posterior
calibration 與正式 gate 仍待完成。

以下仍列出四個可以明確分開的候選，方便追溯為何選 B；A 是 baseline，C 是
未來可選的 pre-clustering workflow，D 是更完整但尚未實作的事件模型。

### Candidate A — current static-CN `q_repo(phi,m)` baseline

\[
q_{\mathrm{repo}}(\phi,m)
=
\frac{\rho_{\mathrm{ASCAT}}\phi m}
{2(1-\rho_{\mathrm{ASCAT}})+\rho_{\mathrm{ASCAT}}CN_i},
\qquad
L_i(\phi)=\sum_m\pi_i(m)P(D_i\mid q_{\mathrm{repo}}).
\]

**What it means:** 保留目前可執行的 static-CN、per-SNV multiplicity
baseline；`T`/`eta` 的 tree state 不變，`m` 只在 read likelihood 中邊際化。[current
repo `model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:206)、
[current repo likelihood marginalization](/bip8_disk/boyu114/main_work/inference/src/model.cpp:255)

**Advantages:** state 維度較小、程式變更較少、可以保留 amplified/LOH 位點的
基本 CN effect；這些是由目前公式直接推得的 model-engineering consequences，
不是文獻保證。[current repo `model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:128)

**Limitations:** 它沒有 PyClone-VI/PhyClone emission 的三群 DNA-copy weighting、
candidate-specific `mu`、error-rate 與明確 mutation-before/after-CNV candidate；
這是對兩套 source code 的直接比較。[current repo `model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:206)、
[PyClone-VI candidate construction](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L148-L171)、
[PhyClone candidate construction](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L301-L326)

### Candidate B — integrated PhyClone-compatible `xi` emission

把 current `q_repo` 改成 candidate-aware expected ALT probability：

\[
\xi_i(g,\phi)
=
\frac{
\sum_{r\in\{N,R,V\}}
w_{ir}(\phi)
c_{ir}(g)\mu_{ir}(g)
}{
\sum_{r\in\{N,R,V\}}
w_{ir}(\phi)c_{ir}(g)
},
\]

\[
L_i(\phi)
=
\sum_{g\in\mathcal G_i}
P(g\mid C_i)
P(D_i\mid \xi_i(g,\phi),e_i).
\]

這個 candidate 的來源是 PhyClone paper 對 copy-number/tumour-content-corrected
PyClone likelihood 的定義，以及 official PhyClone/PyClone-VI code 中的
`population_prior`、`cn`、`mu` 與 candidate log-sum-exp。[PhyClone paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)、
[official PhyClone emission](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/utils/math_utils.py#L919-L995)、
[official PyClone-VI emission](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L239-L301)

**What it does not mean:** 不代表要先執行 PyClone-VI，再把 PyClone-VI 的
`cellular_prevalence` 當固定 CCF 填入 tree likelihood。PhyClone 的正式流程是
可選地使用 PyClone-VI 做 pre-clustering，但仍以原始 counts/CN/tumour content
建立自己的 emission。[PhyClone README](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L271-L291)、
[official PhyClone clustered data construction](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L75-L105)

**Advantages:** 可以把 CCF、tumour content、CN、genotype/multiplicity candidate
與 read likelihood 放在同一個 emission 層；候選不確定性能傳遞到 CCF 與樹的
評分。這是由 joint likelihood 結構推得的 advantage，不是宣稱一定改善所有
資料集。[PhyClone paper §2.2](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)

**Costs:** 需要明確定義 `G_i` candidate support、candidate prior、`mu` clipping、
error model 與 output responsibility。這些最小規則目前已在 C++/Python 同步；
尚未完成的是 clone-specific CNV event history 與正式 predictive validation。
[current model target/spec](/bip8_disk/boyu114/main_work/model.md:108)、
[current runtime `xi`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:239)

### Candidate C — two-stage PyClone-VI pre-clustering + integrated tree emission

這是 workflow choice，不是把 PyClone-VI CCF 當成 final truth：

```text
PyClone-VI:
  raw counts + CN + tumour content
  -> CCF posterior/grid + mutation clusters

PhyClone-like tree model:
  same raw counts + CN + tumour content
  + optional PyClone-VI cluster IDs
  -> tree topology + tree-constrained CCF + candidate-aware emission
```

PhyClone 官方 README 明確推薦 PyClone-VI 作為 WGS pre-clustering；paper 同時
說明 clustered-together mutations 會被保持在一起，但不同 pre-clusters 可以
被 PhyClone 合併。[PhyClone README](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L271-L291)、
[PhyClone paper §2.2.2](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec5)

**Advantages:** 用 PyClone-VI 將 mutation 數量壓成 clusters，降低後續 tree
搜尋成本；保留 PhyClone 對原始 counts 的 copy-number-aware emission，而不是
只把 precomputed CCF 當作輸入。PhyClone paper 將 pre-clustering 的主要動機
列為 computational efficiency。[PhyClone paper §2.2.2](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec5)

**Costs:** pre-cluster 中被綁在一起的 mutation 不能在 PhyClone 中拆開；如果
PyClone-VI 的 clustering 錯誤，這個 constraint 可能把錯誤帶進 tree layer。
另外 PyClone-VI paper 說 VI 是 posterior approximation，且可能低估 posterior
variance；其 CCF 也使用有限 grid。[PyClone-VI paper limitation discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/#Sec10)、
[PhyClone pre-clustering behavior](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec5)

### Candidate D — richer CNV timing/phase event model

若 Q2=B 的要求是「正式推論 mutation 發生在 CNV 之前或之後」，可以將
`g` 擴充為含 allele-specific copy number、phase 與 CNV timing 的 event candidate，
而不是只用一個 scalar `m_i`。PhyloWGS 將 SSM/CNV timing、maternal/paternal
copy state 與 expected allele frequency 放在同一個 evolutionary model 中；
DeCiFer 也將 genotype/multiplicity 與 cancer cell fraction 的解釋聯結起來。[PhyloWGS
原始論文](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8#Sec6)、
[DeCiFer 原始論文](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)

**Advantages:** 能表示比 scalar `m_i` 更細緻的 CNV timing、allele phase 與
mutation loss/DCF 類解釋。[PhyloWGS 原始論文](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8#Sec6)、
[DeCiFer 原始論文](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)

**Costs:** candidate state、prior、tree/event coupling 和 identifiability
都更複雜；不能只把 current `m` 欄位改名，就宣稱已完成此 model。這是由
Candidate D 比 Candidate A/B 多出的 latent structure 推得的 implementation
consequence。[current repo `model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:128)、
[PhyloWGS 原始論文](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8#Sec6)

## 6. 即使 Q4 已確認，仍不能混淆的三個東西

### 6.1 Observed VAF

\[
\mathrm{VAF}_{\mathrm{obs},i}
=
\frac{\mathrm{ALT\ reads}_i}
{\mathrm{REF\ reads}_i+\mathrm{ALT\ reads}_i}.
\]

這是 read-count summary；PyClone-VI 與 PhyClone 的 official code 使用原始
counts 計算 emission，而不是把 observed VAF 欄位改寫成 CCF。[PyClone-VI
official `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L81-L98)、
[PhyClone official `data/pyclone.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L277-L326)

### 6.2 Expected ALT probability

\[
\xi_i(g,\phi)
\]

是「假設 CCF=`phi` 且 genotype candidate=`g` 時，模型預期看到的 ALT read
比例」。它不是 observed VAF，也不是 final CCF。這個定義直接由
PhyClone/PyClone-VI emission code 的 `e_vaf`／`xi` 類計算得出。[official
PyClone-VI emission](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L239-L301)、
[PhyClone paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)

### 6.3 Inferred CCF

CCF 是 likelihood 對 CCF 候選值的 posterior 結果；PyClone-VI 用 CCF grid 的
posterior mean 作為 `cellular_prevalence` output，而 PhyClone 將 tree-derived
cellular prevalence 放進其 PyClone emission。[PyClone-VI official `post_process.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/post_process.py#L36-L75)、
[PhyClone paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)

## 7. Q5=C：已確認的邊界

Q5=C 的語意是：

> 保留 CCF/`phi` 的既有定義；對不符合 additivity、且可能由 mutation loss
> 造成的位點，先標記為 outlier，不立即把整個模型改成 DCF。

這是使用者已確認的設計決定，不是本 note 替使用者推導的選項。其文獻／官方
實作 precedent 是 PhyClone 的 outlier/loss modelling：paper 將 mutation loss
描述為會破壞 additivity，並以 outlier variable 與 outlier likelihood 允許
這些位點不加入一般 tree-node likelihood；官方 README 也說明 outlier/lost
mutations 最後可被標為 clone `-1`。[PhyClone paper mutation-loss discussion](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec1)、
[PhyClone paper outlier model](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec5)、
[PhyClone official README outlier modelling](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L328-L348)

Q5=C 不等於已經完成 mutation-loss inference；目前仍需另外定義：

- 哪些 evidence 觸發 outlier flag；
- outlier probability 的 prior 與 threshold；
- outlier 是否只排除於 descendant-sum，或也要進入 CN/timing candidate；
- 未來是否需要 DCF-like output。

這些項目在 current ADR 中仍被列為未指定的 implementation/model details。[current
ADR](/bip8_disk/boyu114/main_work/docs/adr/0001-multiplicity-emission-and-cnv-timing.md:77)

## 8. Evidence-based conclusion

1. **PyClone-VI 有做 copy-number／tumour-content-aware CCF inference，且是
   PhyClone 建議的 pre-clustering stage。** [PhyClone README](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L271-L291)、
   [PyClone-VI paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/#Sec8)

2. **PyClone-VI 有 multiplicity-equivalent genotype candidates。** 它們在
   `get_major_cn_prior` 建立，並在 expected ALT probability 與 candidate
   likelihood 中被整合；只是 source 沒有把它命名成 repo 式的 `m`，也沒有
   standard multiplicity output table。[official PyClone-VI `data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L148-L171)、
   [official PyClone-VI output code](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/post_process.py#L14-L33)

3. **PhyClone 不只是接收 PyClone-VI 產生的 CCF。** 它接收 optional cluster
   IDs 來降低 tree search complexity，然後以 original input 的 counts/CN/
   tumour content 重新計算 PhyClone/PyClone emission。[PhyClone `run.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/run.py#L69-L80)、
   [official clustered data construction](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L75-L105)

4. **Q4 的正式模型已確認為 Candidate B：integrated PhyClone-compatible
   `xi`。** A 保留作 baseline，C 是 optional pre-clustering workflow，D
   是未來的 richer CNV event model。[current repo runtime `xi`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:239)、
   [PhyClone paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563#Sec4)

## 9. Source list

### Primary papers

- [Gillis & Roth (2020), PyClone-VI: scalable inference of clonal population structures using whole genome data](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/)
- [Hurtado, Bouchard-Côté & Roth (2025), PhyClone: accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)
- [Deshwar et al. (2015), PhyloWGS](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)
- [Satas et al. (2021), DeCiFer](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)

### Official repositories and locators

- [Roth-Lab/pyclone-vi](https://github.com/Roth-Lab/pyclone-vi)
  - [`pyclone_vi/data.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/data.py#L148-L301)
  - [`pyclone_vi/post_process.py`](https://github.com/Roth-Lab/pyclone-vi/blob/master/pyclone_vi/post_process.py#L14-L97)
  - [README input/output](https://github.com/Roth-Lab/pyclone-vi/blob/master/README.md#L70-L122)
- [Roth-Lab/PhyClone](https://github.com/Roth-Lab/PhyClone)
  - [`phyclone/data/pyclone.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/data/pyclone.py#L277-L326)
  - [`phyclone/utils/math_utils.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/utils/math_utils.py#L919-L995)
  - [`phyclone/run.py`](https://github.com/Roth-Lab/PhyClone/blob/main/phyclone/run.py#L6-L80)
  - [README cluster/pre-clustering workflow](https://github.com/Roth-Lab/PhyClone/blob/main/README.md#L271-L291)
- Current repo:
  - [`/bip8_disk/boyu114/main_work/inference/src/model.cpp:128`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:128)
  - [`/bip8_disk/boyu114/main_work/inference/src/model.cpp:206`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:206)
  - [`/bip8_disk/boyu114/main_work/inference/src/model.cpp:255`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:255)
  - [`/bip8_disk/boyu114/main_work/docs/adr/0001-multiplicity-emission-and-cnv-timing.md:77`](/bip8_disk/boyu114/main_work/docs/adr/0001-multiplicity-emission-and-cnv-timing.md:77)
