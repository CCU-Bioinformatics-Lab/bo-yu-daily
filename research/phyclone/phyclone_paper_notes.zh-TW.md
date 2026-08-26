# PhyClone 論文重點：從 bulk reads 到 clone phylogeny

## 1. 論文識別

- **標題**：*PhyClone: accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing*
- **作者**：Emilia Hurtado、Alexandre Bouchard-Côté、Andrew Roth
- **期刊**：Bioinformatics 41(7), btaf344，2025-06-13
- **核心問題**：bulk sequencing 看見的是多個 clone 混在一起的 allele counts；單靠一個 sample 的 prevalence 常常無法唯一決定 clone 間是 sibling 還是 ancestor/descendant，也無法自然處理 mutation loss。
- **核心方法**：以 FS-CRP（forest structured Chinese restaurant process）建立 tree-structured clustering prior；把 clone prevalence 邊際化，讓 inference 主要在 tree topology/cluster assignment 上進行；再用 Particle Gibbs + sequential Monte Carlo（PG-SMC）探索 posterior。

來源：`paper-oup`、`paper-pmc`、`paper-supp`，詳見 [SOURCES.md](SOURCES.md)。

## 2. 論文要解決的直覺問題

把一個腫瘤想成一棵家族樹：祖先 clone 先得到一組 mutation，後代 clone 繼承祖先 mutation，再增加自己的 mutation。可是 bulk sample 會把所有細胞的 DNA 混成一鍋，因此觀察到的 VAF/allele counts 只是混合後的結果。

PhyClone 不只輸出一棵「看起來最像」的樹，而是先保留可能的 tree posterior；最後才依需求輸出 MAP tree、consensus tree 或 sampled topology report。這個 Bayesian framing 是為了表達 bulk data 對 topology 的不確定性，而不是假裝每個 branching 都能被唯一識別。

論文特別指出兩個困難：

1. **ISA/additivity ambiguity**：較高 cellular prevalence 的 mutation 不必然能唯一指向較早的 clone；multi-sample 交叉 prevalence 關係可以增加可識別性，但仍可能有多棵相容樹。
2. **Mutation loss**：copy-number alteration、deletion 或 allele-count/CN 錯誤會讓 mutation 不再沿著所有 descendant 傳遞。若模型強迫 perfect propagation，會把 loss 誤解成錯誤的 tree。

## 3. 資料輸入定義

### 3.1 Main input：每列是一個 mutation-sample observation

官方 schema 是 tab-delimited tidy table。必要欄位如下：

| 欄位 | 型別/限制 | 模型用途 |
|---|---|---|
| `mutation_id` | string 或 integer；不可空 | 連結同一 mutation 在不同 sample 的 rows |
| `sample_id` | string 或 integer；不可空 | sample/region 維度 |
| `ref_counts` | non-negative integer | reference allele reads |
| `alt_counts` | non-negative integer | alternate allele reads |
| `major_cn` | non-negative integer | mutation 所在 segment 的 major allele copy number |
| `minor_cn` | non-negative integer | mutation 所在 segment 的 minor allele copy number |
| `normal_cn` | integer，至少 1 | normal tissue 的 total copy number；常染色體通常 2 |

官方 schema 也允許以下 optional columns：

| 欄位 | 缺省值/用途 |
|---|---|
| `tumour_content` | 缺少時 loader 設為 `1.0`；代表 sample 中 malignant cell fraction |
| `error_rate` | 缺少時 loader 設為 `0.001`；進入 PyClone emission 的 sequencing-error floor |
| `chrom` | 染色體位置；主要供 cluster-aware loss/outlier prior 使用 |

直接證據：`PhyClone/phyclone/data/validator/PhyClone_schema.json`、`PhyClone/phyclone/data/pyclone.py::_process_required_cols_on_df`、論文 Methods S1.1。

### 3.2 Cluster input：可選的預分群資訊

cluster file 至少需要：

- `mutation_id`
- `cluster_id`

可選欄位：`sample_id`、`chrom`、`cellular_prevalence`、`outlier_prob`。

預分群不是硬性必要，但論文與 README 都指出：WGS 大規模資料若完全不先 cluster，計算複雜度會大幅增加。PhyClone 會保留同一個輸入 cluster 的 mutation 在同一 node，但可以把原本不同 clusters merge 到同一個 node，因此它不是盲目接受 pre-clustering，而是用 tree constraint 進一步修正 clustering。

### 3.3 Input preprocessing / filtering

官方程式碼在 inference 前做以下處理：

1. 讀入並依 schema 驗證欄位、型別與 non-negative constraints。
2. 移除 duplicate rows。
3. 移除 `major_cn == 0` 的 mutation；這類 loci 沒有可用 major copy。
4. 移除沒有在所有 provided samples 出現的 mutation；每個 mutation 必須在每個 sample 有一列觀察。
5. 若沒有 `error_rate`，補 `1e-3`；若沒有 `tumour_content`，補 `1.0`。
6. 若 `major_cn < minor_cn`，`get_major_cn_prior` 會拒絕該 row。
7. 將每個 mutation 的 sample rows 組成 `PyCloneDataPoint`，在 CCF grid 上先計算 likelihood。

官方 workflow 另外將 input cleaning 寫成 `cleaned_input.tsv.gz`，並把 removed variants 保存到 `removed_variants.tsv.gz`，使 filtering 有 provenance 可追蹤。

## 4. Observation model：從 counts 估計某個 CCF 的可信度

### 4.1 PyClone emission

對每個 mutation/sample，觀察 `x = alt_counts`、`d = ref_counts + alt_counts`。給定 genotype、tumour content `t`、cellular prevalence `\bar{\rho}` 與 sequencing error `\epsilon`，先計算讀到 variant allele 的機率 `\xi`，再用：

```text
x | d, genotype, CCF, tumour_content ~ Binomial(d, xi)
```

若資料 variance 比 Binomial 能解釋的更大，可以改用 Beta-Binomial。官方 CLI 的 default density 是 `beta-binomial`，default precision 是 `400`；也可明確選 `binomial`。

### 4.2 Mutational genotype prior

reference/variant cell populations 的 genotype 通常未知，因此 PhyClone 根據 `major_cn`、`minor_cn`、`normal_cn` 列出合理的 genotype candidates：

- mutation 發生在 copy-number event 前：variant side 可有最多 `major_cn` 個 variant-bearing copies。
- mutation 發生在 copy-number event 後：以 event 後的 total CN 與 1 個 variant copy 建構 candidate。
- candidate prior weight 先設為等權重。

因此 copy-number input 不是只拿來做 QC；它直接影響 emission 中每個 candidate genotype 的 prior/mutational fraction。

### 4.3 CCF grid 與 likelihood cache

程式碼把 CCF 離散到 `grid_size` 個點，default `101`，再對每個 mutation/sample 預先計算 emission likelihood。這讓後面的 tree scorer 可以重用 arrays/cache，但也意味著 marginalisation 是離散近似，grid 越細通常越準、成本也越高。

## 5. FS-CRP tree model

### 5.1 Generative process

論文的無 outlier 版本可用下列順序理解：

1. 用 CRP(`alpha`) 將 SNVs partition 成 mutation clusters。
2. 在 cluster 數量相同的 rooted forests 中抽一個 topology。
3. 加一個 dummy root，把 forest 的所有 roots 接到同一個 structural root。
4. 對每個 sample，從 Dirichlet(`kappa`) 抽各 tree node 的 **clonal prevalence** `rho`；這些 local masses 加總為 1。
5. 對 node `v`，把自己與所有 descendants 的 local masses 相加，得到 **cellular prevalence / CCF** `bar_rho_v`。
6. 每個 mutation 使用其所屬 node 的 CCF 進入 PyClone emission。

用一句話說：`rho` 是「直接出生在這個 node 的細胞比例」，`bar_rho` 是「這個 node 加上所有後代所涵蓋的細胞比例」。

### 5.2 Tree prior 的 implementation detail

Supplementary Methods 描述：forest topology 依 cluster 數使用 uniform forest prior；最終 tree 對多個 sub-roots 加入 adjustment，讓 single-rooted topology 比 two-root topology 高約 1000 倍的 prior weight（再依 node 數正規化）。這是 sampler 的 structural prior，不是輸入 table 欄位。

### 5.3 Collapsed prevalence marginalisation

若直接把每個 node 的 prevalence 都放進 sampler，state dimension 會隨 clone 數量與 sample 數量膨脹。PhyClone 改為計算：

```text
p(X, clusters, tree) = ∫ p(X, clusters, tree, rho) d rho
```

做法是把 node prevalence 轉成 descendant-sum/CCF parameterization，在 CCF grid 上用 tree-aware dynamic programming 計算 subtree likelihood，最後把 `rho` 邊際化掉。論文主文指出其 marginalised likelihood 可用 `O(|V|^2)` 的 tree-dependent dynamic programming 計算；實際 runtime 仍會受到 grid size、mutation/cluster 數與 children convolution 影響。

## 6. Outlier / mutation-loss model

若一個 mutation 不符合 descendant additivity，它可以被標記為 outlier：

- mutation `n` 有 outlier prior `nu_n`。
- 非 outlier：進入 tree node，使用 tree-derived CCF `bar_rho_vn`。
- outlier：不被迫掛在 tree 的 propagation path 上，對 CCF 使用 Uniform prior 並做 numerical integration。
- outlier modelling active 時，官方 output 將該 mutation 分配到 clone id `-1`。

有兩種 outlier prior 來源：

1. 全域 `--outlier-prob`。
2. 從 clustered data 推定：以跨 sample prevalence 最高的 cluster 找 truncal background，再以 10,000 次 chromosome draws 判斷某 cluster 是否有異常的 genomic locality；低於 p-value `0.01` 時提高 loss/outlier prior。default low/high prior 為 `0.0001`/`0.4`，但都可由 CLI/config 改變。

這個 outlier state 是 PhyClone 與單純 perfect-phylogeny tree builder 的關鍵差異：它允許「某些 mutation loss」而不必把整棵 tree 判成不合法。

## 7. Inference：PG-SMC 如何探索 tree posterior

### 7.1 Bottom-up SMC

SMC particle 從一個 rooted forest 開始，依 mutation ordering `sigma` 逐一加入資料點。新 mutation 可以：

- 加到現有 node；或
- 建立新 node，並從目前 root nodes 選一部分 child 接到新 node。

每一步都對 particle reweight，最後得到近似 posterior。官方提供三種 proposal：

- `bootstrap`：便宜但 proposal quality 較弱；
- `fully-adapted`：列舉更多可能 state，單 iteration 較好但成本最高；
- `semi-adapted`：現有 node attachment 用 likelihood，new-node child subset 用抽樣，是實務折衷且 default。

### 7.2 為什麼需要 Particle Gibbs

固定 `sigma` 會造成可達性偏差：若 mutation `x` 先於 `y` 加入，某些 `x` ancestor of `y` 的 topology 可能永遠到不了。PhyClone 將 `sigma` 當成 auxiliary variable：

1. 固定 `sigma`，用 conditional SMC 更新 tree/clusters。
2. 固定目前 tree，依能產生該 tree 的 permutation set `Sigma(T)` 重新抽 `sigma`。
3. 交替進行，讓 sampler 能探索原本被 ordering 擋住的 tree。

對長序列，還提供 subtree Particle-Gibbs update：抽一個 mutation，選其 parent 作 subtree root，只更新該 subtree，以降低 particle genealogy degeneracy。

### 7.3 其他 mixing moves

每次 tree update 外，官方程式碼還能做：

- subtree prune-regraft（挑 subtree，重新 Gibbs sample attachment）；
- 固定 topology、重新把 data point 分配到另一個等構型 node；
- concentration parameter `alpha` 的更新；
- 多 chain 平行執行，並用 seed 追蹤 reproducibility。

## 8. 產出定義

### 8.1 Sampling trace

`phyclone run` 將 sampling 結果寫入 HDF5 `TRACE.h5`，主要保存：

- `samples`：sample identifiers；
- `run_info/rng_seed`：seed provenance；
- `clusters/cluster_id`、`clusters/mutation_id`：若有 pre-clustering；
- `data/datapoints/`：每個 datapoint 的 likelihood grid、name、outlier priors；
- `trace/chains/chain_*`：每個 chain 的 iterations、time、alpha、log posterior、tree hash、node/outlier/root counts，以及可去重重用的 tree graph/node data。

### 8.2 MAP tree

`phyclone map` 從 trace 選：

- `map-type=joint-likelihood`：最高 sampled joint likelihood 的 tree；或
- `map-type=frequency`：最常出現的 topology。

寫出：

- `TREE.nwk`：clone tree topology；
- `TABLE.tsv`：mutation → clone assignment，若有 clustering 也保留 `cluster_id`，並附 `ccf`、`clonal_prev`；
- `SAMPLE_PREVALENCE_TABLE.tsv`：每個 sample/clone 的 CCF 與 local clonal prevalence。

### 8.3 Consensus tree

`phyclone consensus` 對 sampled trees 的 clades 算出現比例，保留達到 consensus threshold 的 clades，再產生 consensus tree。weight 可選 raw counts 或 joint-likelihood。程式碼的 `key_above_threshold` 實際使用嚴格 `>` threshold，這是閱讀 output 時要注意的 implementation detail。

### 8.4 Topology report/archive

`phyclone topology-report` 產生每個 unique topology 的：

- topology identifier；
- sampled count；
- representative/best sampled log-likelihood 與 chain/iteration context。

若指定 archive，還會為每個 topology 保存 Newick、mutation result table、sample prevalence table。這使 output 不必壓縮成單一 point estimate，可以保留 posterior topology diversity。

## 9. 論文宣稱的端到端流程

```text
SNV caller + BAM/allele counts
        + segment-level major/minor/normal CN
        + tumour content per related sample
        + optional PyClone-VI clusters
        ↓
schema validation + duplicate/partial/CN-zero filtering
        ↓
PyClone genotype prior + Binomial/Beta-Binomial likelihood grid
        ↓
FS-CRP cluster/tree prior + Dirichlet node masses
        ↓
tree-aware CCF marginalisation (dynamic programming)
        ↓
PG-SMC: particles, resampling, proposals, ordering updates, MCMC moves
        ↓
posterior trace.h5
        ├── MAP tree + mutation/CCF tables
        ├── consensus tree + prevalence tables
        └── topology report + optional sampled-tree archive
        ↓
code correctness + synthetic benchmark + real HGSOC ground-truth validation
```

## 10. 研究解讀與 claim ceiling

論文結果支持的強度是：「在作者選定的 synthetic datasets、比較方法、設定與 HGSOC real datasets 中，PhyClone 的 topology/assignment performance 與 scalability 表現通常強，且可處理部分 mutation loss。」

不能直接延伸成：

- 每個 real tumour 的 tree 都是唯一真實歷史；
- CCF uncertainty 已完全解決；
- sub-clonal CNV 已被完整建模；
- 只用單一 sample 就能可靠辨識任意數量的 clones；
- current GitHub `main` 與 paper benchmark archival snapshot 逐 byte 相同。

論文明確指出的主要 limitation 是 PyClone genotype correction 不能處理 sub-clonal copy-number variation；這也是把 PhyClone 概念移植到其他 CN model 時最重要的風險邊界。
