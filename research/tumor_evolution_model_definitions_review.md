# 腫瘤演化樹文獻中的 model 定義 crosswalk

更新日期：2026-08-28

## 1. 研究問題與證據範圍

問題：代表性的腫瘤演化／克隆樹論文，通常如何定義自己的 `model`？這些
`model` 是否都等於 likelihood、tree search 或輸出結果？

本次由 5 個唯讀 subagent 分工查找：

- literature-A：PhyloSub、PhyloWGS、Canopy、PyClone、PyClone-VI。
- literature-B：CITUP、LICHeE、AncesTree、Treeomics、MACHINA，並以 PhyloWGS 作 probabilistic 對照。
- repo-search：核對目前 `main_work` 的 model/inference/output contract。
- lab-search：核對 lab Knowledge 的術語邊界。
- history-search：核對歷史 tumor-tree 方法與研究脈絡。

論文證據只採 primary sources：原始論文的 PMC、期刊全文、作者／官方程式
與官方 README。`daily/`、lab Knowledge 與歷史資料庫只用於語意定位，不能取代
論文原文。

## 2. 先講結論

文獻裡的 `model` 沒有單一固定意思，但成熟的方法通常會交代以下幾件事：

1. **observed data**：read counts、VAF／cellular frequency、CNA/CNV、sample composition。
2. **latent quantities**：clone/tree、clone proportion、mutation assignment、genotype、CN state、mutation order。
3. **evolutionary assumptions／constraints**：infinite-sites、persistent inheritance、parent-child frequency／sum condition、CN timing。
4. **observation model 或 objective**：Binomial／Beta-Binomial／Normal likelihood，或 SSE、BIC、ILP、parsimony、migration cost。
5. **inference procedure**：MCMC、SMC、variational inference、QIP、ILP、QP 或 graph search。
6. **output uncertainty**：posterior trees、valid-tree set、best-scoring tree、clone proportions 或 CCF distributions。

因此，論文中的 `model` 通常不是單一公式，也不一定是 Bayesian posterior。它是
「資料如何由候選克隆結構解釋」的完整規格；不同論文只是用 likelihood、constraint
或 optimization 來實現這個規格。

## 3. 跨論文總覽

| 方法 | model 類型 | 主要 latent／候選結構 | 資料如何約束 | 主要結果 |
|---|---|---|---|---|
| **PhyloSub** | Bayesian generative tree model | lineage tree、SNV-to-lineage、lineage frequency、genotype | read-count likelihood、tree prior、infinite-sites／frequency constraints | posterior trees、lineage frequencies、partial-order uncertainty |
| **PhyloWGS** | CNV-aware Bayesian generative tree model | TSSB tree、SSM/CNV placement、subclone frequencies、phase/order | Binomial allele-count model、CNV/SSM evolutionary relationship、tree prior | posterior trees、SSM/CNV grouping、genotypes、frequencies |
| **Canopy** | joint SNA/CNA Bayesian matrix-and-tree model | clone number、bifurcating tree、mutation matrix、major/minor CN、mixture、phase/order | SNA Binomial + CNA Normal likelihood、parsimony／tree constraints | tree histories、clone profiles、CN states、mixture、phase/order |
| **Pairtree** | probabilistic tree search with CNA-corrected frequencies | subclone tree、exclusive population frequency、tree-constrained frequency | read/VAF likelihood 與 tree-compatible frequency fitting | 多個 plausible trees、tree weights、frequency summaries |
| **PhyClone** | tree-structured clustering／Bayesian SMC model | tree、clonal prevalence `rho`、cellular prevalence `bar-rho`、mutation clusters | PyClone copy-number／tumour-content corrected likelihood | tree posterior／summary、cluster assignment、prevalence |
| **CITUP** | combinatorial optimization／QIP | rooted clone tree、mutation assignment、sample-specific clone proportion | frequency residual、Gaussian-style score、BIC | best or ranked trees、assignment、clone proportions |
| **LICHeE** | constraint graph + optimization | VAF clusters、constraint DAG、spanning trees | perfect-phylogeny／VAF ordering、QP residual | valid／ranked lineage trees、sample composition |
| **AncesTree** | probabilistic measurement layer + ILP | ancestry graph、spanning arborescence、usage matrix | Beta/binomial uncertainty、ancestry／sum condition | clonal tree、sample usage、possible graph structures |
| **Treeomics** | Bayesian presence layer + weighted MILP | mutation patterns、compatible pattern set、phylogeny | binomial presence probability、perfect/persistent compatibility | compatible patterns、phylogeny、artifact／seeding interpretation |
| **MACHINA** | constrained multi-objective optimization | labeled clone tree、migration graph、migration history | frequency intervals、tree constraints、allowed migration patterns | parsimonious migration histories |
| **PyClone** | Bayesian clonal clustering；不是 tree model | mutation CCF、genotype、DP cluster | allele-count likelihood、genotype prior、DP mixture | CCF posterior、mutation clusters、similarity matrix |
| **PyClone-VI** | finite mixture + variational inference；不是 tree model | finite CCF grid、mixture component、mutation assignment | Binomial／Beta-Binomial emission、finite mixture | CCF variational distribution、clusters；不推論 ancestry tree |
| **DeCiFer** | multiplicity-aware clonal frequency model | mutation multiplicity、DCF、clusters | CN／multiplicity-aware evolutionary model | DCF、multiplicity-related cluster estimates；不等於本 repo 的 `phi` |

## 4. 各方法怎麼定義 model

### 4.1 PhyloSub：用 generative model 解釋未觀測的 phylogeny

PhyloSub 將腫瘤中的 subclonal lineage 表示為樹節點。每個節點有自身新出現的
SNV 與 local lineage mass；SNV 的 population frequency 則由出現該 SNV 的節點
及其 descendants 的 mass 累積而來。

其 model 包含：

- observed：每顆 SNV 的 reference／variant read counts、depth，以及 copy-number／zygosity context；
- latent：tree、SNV-to-lineage assignment、lineage frequency、genotype；
- assumption：infinite-sites／single-origin，並要求 parent frequency 能容納 descendants；
- likelihood：由 lineage frequency 與 genotype 推出的 allele frequency，再連接到 read-count likelihood；
- prior：tree-structured Bayesian nonparametric prior；
- inference：MCMC 同時探索 tree、assignment 與 frequency；
- output：posterior tree samples、lineage frequencies、mutational profiles 與 partial-order uncertainty。

所以 PhyloSub 的 `model` 是一個「由 read counts 生成／解釋 SNV frequency 與
latent tree」的 Bayesian model，不只是 VAF clustering。

Primary source：[Jiao et al., PhyloSub (2014)](https://doi.org/10.1186/1471-2105-15-35) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3922638/)

### 4.2 PhyloWGS：在 PhyloSub 的 tree model 上加入 CNV／SSM 關係

PhyloWGS 明確把自己建立在 tree-structured stick-breaking process 與 allele-frequency
generative model 上。相較只使用 SNV frequency 的模型，它把 SSM、CNV、copy number、
maternal／paternal phase 與 SSM-CNV temporal order 放進同一個解釋架構。

它的 model 重點是：

- tree 是 Bayesian prior 下的 latent variable，而非事先固定的 topology；
- clone／node frequency 由 tree-compatible local masses 產生；
- CNV 與 SSM 的先後及所在 copy 會改變 expected allele probability；
- read counts 以 Binomial observation model 評分；
- MCMC 同時探索 tree、event placement、frequency、phase／order。

因此，PhyloWGS 的 model 可以濃縮成：

```text
tree prior
  + subclone frequencies
  + SSM/CNV placement and timing
  + copy-number-aware read likelihood
  → posterior over tumor trees and subclone composition
```

Primary source：[Deshwar et al., PhyloWGS (2015)](https://doi.org/10.1186/s13059-015-0602-8) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4359439/)

### 4.3 Canopy：把 SNA、CNA、mixture、phase 與 tree 放在聯合模型

Canopy 將 tumor evolution 表示為一個具有 clone number `K` 的 bifurcating tree，
並以矩陣共同表示：

- `Z`：clone 的 SNA presence／genotype；
- major/minor copy-number matrices；
- `P`：sample-by-clone mixture proportions；
- `H`：overlapping SNA/CNA 的 phase；
- `Q`：SNA-CNA temporal order；
- `tau_K`：clonal tree。

它的 likelihood 同時包含 allele-count Binomial 與 CNA copy-ratio Normal terms，
而 `K`、tree、mutation state、copy number、phase/order 都是需要推論的 unknowns。
這是典型的 joint model：不是先獨立得到 SNA cluster，再把結果貼到一棵樹上。

Primary source：[Jiang et al., Canopy (2016)](https://doi.org/10.1073/pnas.1522203113) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5027458/)

### 4.4 Pairtree 與 PhyClone：同樣區分 tree、frequency 與 emission，但符號不同

Pairtree 把 subpopulation 的 exclusive／local frequency 與 tree-constrained cumulative
frequency 分開，並以 tree search 加上 frequency fitting 來保留多個 plausible trees。
它支持「同一 bulk data 可對應多個 tree」這個不確定性觀念。

PhyClone 則使用：

- `rho_v`：node-level clonal prevalence；
- `bar-rho_v`：node 加 descendants 的 cellular prevalence；
- mutation cluster 對應 tree node；
- PyClone-derived copy-number／tumour-content corrected allele-count likelihood；
- SMC 探索 topology 與 clustering。

這兩個方法都說明一件事：

> tree structure、clone proportion／prevalence、mutation assignment 與 read-count
> emission 可以是同一個 joint inference 的不同層次，不必全部變成同一種 persistent state。

Primary sources：[Pairtree paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/) · [Pairtree official outputs](https://github.com/morrislab/pairtree#pairtree-outputs) · [PhyClone paper](https://doi.org/10.1093/bioinformatics/btaf344)

### 4.5 CITUP：把 model 表示為可最佳化的 tree-compatible objective

CITUP 不以完整 posterior over trees 為主要輸出，而是把多樣本 mutation frequency、
mutation assignment、clone proportion 與 shared rooted tree 寫成 combinatorial
optimization problem。

其 model 可概括為：

```text
observed mutation frequencies
  + rooted tree constraints
  + mutation-to-node assignment
  + sample-specific clone proportions
  → frequency residual / Gaussian-style score
  → BIC-penalized optimum
```

所以 CITUP 的 `model` 仍包含 biological／frequency assumptions 與 scoring function，
但主要 inference result 是 QIP／BIC 的最佳解，不是由 MCMC 抽出的 posterior tree。

Primary source：[Malikic et al., CITUP (2015)](https://doi.org/10.1093/bioinformatics/btv003) · [Oxford Academic full text](https://academic.oup.com/bioinformatics/article/31/9/1349/200674)

### 4.6 LICHeE：model 是 constraint network 與 tree feasibility

LICHeE 先使用多樣本 SSNV 的 presence pattern 與 VAF，把 SNV 分組／cluster；再建立
evolutionary constraint network。candidate trees 是 DAG 的 spanning trees，必須通過
perfect-phylogeny 型 ordering、parent/child VAF 以及 child-sum constraints。

其中 GMM／EM 用於 VAF clustering，但整體 tree model 的核心是：

```text
candidate tree ∈ trees satisfying evolutionary constraints
```

多棵合法 tree 會再依 VAF correction／SSE ranking。因此 LICHeE 不是完整
read-count generative posterior，而是 constraint/search model，帶有 probabilistic
clustering component。

Primary source：[Popic et al., LICHeE (2015)](https://doi.org/10.1186/s13059-015-0647-8) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4501097/)

### 4.7 AncesTree：measurement uncertainty 加上 ancestry ILP

AncesTree 先以 noisy VAF／read counts 建立 ancestry probability 或 approximate ancestry
graph，再使用 Sum Condition 與 ILP 選擇 spanning arborescence。其 model 因此是 hybrid：

- probabilistic layer：Beta/binomial measurement uncertainty；
- structural layer：ancestry graph、parent-child constraint、Sum Condition；
- optimization layer：ILP 選擇符合條件的 ancestry structure。

這提醒我們：有 Bayesian／Beta-binomial component，不代表最後就是完整 Bayesian
posterior over topology。

Primary source：[El-Kebir et al., AncesTree (2015)](https://doi.org/10.1093/bioinformatics/btv261) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4542783/)

### 4.8 Treeomics：presence probability 與 compatible pattern optimization

Treeomics 的 Bayesian model 主要估計 mutation 在各 sample 中存在／不存在的可靠度，
再把跨 sample 的 binary mutation patterns 放進 conflict graph。結構層以 weighted
MILP／minimum-weight vertex cover 移除不相容 pattern，最後從剩餘 patterns 建立 phylogeny。

所以它的 `model` 不是一個直接對所有 topology 抽 posterior 的 model，而是：

```text
read counts
  → mutation presence reliability
  → compatible mutation-pattern set
  → phylogeny / seeding interpretation
```

Primary source：[Reiter et al., Treeomics (2017)](https://doi.org/10.1038/ncomms14114) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5290319/)

### 4.9 MACHINA：model 的中心是 migration history，不是單純 mutation tree

MACHINA 接受 clone tree 與 anatomical labels，將 tree edge 的 site label 變化轉成
migration graph。它的主要目標是 lexicographically 最小化 migration number，再最小化
comigration number；PMH-TI 則另外把 frequency confidence intervals 與 tree inference
納入可行域。

因此 MACHINA 的 model 主要是 labeled-tree／migration constraint model。migration
cost 是 parsimony objective，不是 biological probability，也不是 read-count likelihood。

Primary source：[El-Kebir et al., MACHINA (2018)](https://doi.org/10.1038/s41588-018-0106-z) · [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6103651/)

### 4.10 PyClone 與 PyClone-VI：重要的「不是 tree model」對照

PyClone 是 hierarchical Bayesian clustering model。它推論 mutation 的 cellular
prevalence／CCF、genotype 與 mutation clusters，但本身不定義 rooted tree、parent-child
edge 或 ancestry topology。PyClone-VI 將 DP mixture 改為 overcomplete finite mixture，
把 continuous CCF 改成 finite grid，並以 mean-field variational inference 換取 WGS-scale
可擴展性；它仍不推論 tumor phylogenetic tree。

這些方法可以提供下游 tree-building 的 cluster 或 CCF information，但：

```text
clonal cluster ≠ lineage node
cellular prevalence ≠ ancestry topology
```

Primary sources：[PyClone (2014)](https://doi.org/10.1038/nmeth.2883) · [PyClone-VI (2020)](https://doi.org/10.1186/s12859-020-03919-2)

## 5. 跨論文抽出的共同模型骨架

### 5.1 Generative／posterior model

代表：PhyloSub、PhyloWGS、Canopy、PhyClone；Pairtree 也保留 probabilistic tree
uncertainty。

一般形狀是：

```text
p(tree, clone quantities, assignments | observed data)
  ∝
p(observed data | tree, clone quantities, assignments)
  ×
p(tree, clone quantities, assignments)
```

這類方法通常明確列出 prior、likelihood、latent state 與 posterior sampling／summary。

### 5.2 Constraint／optimization model

代表：CITUP、LICHeE、MACHINA；AncesTree 與 Treeomics 的結構層也接近此類。

一般形狀是：

```text
find tree / assignment / composition
  subject to evolutionary constraints
  minimizing error, BIC, migration cost, or incompatibility weight
```

這類方法的 uncertainty 常表達成 valid-tree set、ranked solutions、confidence
interval feasible set 或 tied optima，不一定是 posterior distribution。

### 5.3 Clustering／emission-only model

代表：PyClone、PyClone-VI；DeCiFer 則更靠近 multiplicity-aware clonal-frequency
model。

這類方法可以有很完整的 read-count likelihood、genotype prior 與 CCF posterior，
但沒有把 parent-child topology 定義為 latent state。因此不能把 cluster 直接稱為
演化樹上的 lineage node。

## 6. 對目前 repo 的直接意義

### 6.1 Current repo 的 model 定義

目前 repo 的 current contract 是：

- `model.md` 定義 posterior target、likelihood、prior 與 latent quantities；
- `inference_algo.md` 定義如何探索 model target，目前是 Rao–Blackwellized annealed SMC；
- persistent particle state 主要是 topology `T` 與 local mass `eta`；
- `phi` 由 tree 與 `eta` 的 descendants sum 推導；
- clone assignment、genotype／multiplicity candidates 在 scoring/emission 中 marginalize，並可在 output 層彙整；
- current output 是 diagnostic candidate samples／summaries，尚不能宣稱 unique tree 或 single-cell truth。

證據：[arch.md](/bip8_disk/boyu114/main_work/arch.md:9-15)、[model.md](/bip8_disk/boyu114/main_work/model.md:27-55)、[inference_algo.md](/bip8_disk/boyu114/main_work/inference_algo.md:5-8)、[output.md](/bip8_disk/boyu114/main_work/output.md:75-127)。

### 6.2 與文獻的準確對接方式

可以說：

> 本 repo 採用 PhyloSub／PhyloWGS 所代表的「tree-compatible clone fractions +
> read-count likelihood」大方向，並參考 PhyClone／PyClone 的 CN-aware emission；
> 但 finite `K`、one-founder、Dirichlet `eta`、candidate construction 與 SMC
> proposal 是本 repo 的 working design，不是任何單一論文的完整複製。

不應說：

- 「所有 tumor-tree papers 都把 model 定義成 Bayesian posterior。」
- 「所有方法都把 multiplicity 作為 tree state。」
- 「PyClone／PyClone-VI 直接產生 tumor evolutionary tree。」
- 「VAF 先經一條固定公式就等於 CCF。」
- 「PhyClone 的 `rho` 與本 repo 的 `eta` 是同一個原始符號。」

### 6.3 對 `module_format.md` 的建議簡化文字

若 `module_format.md` 只保留模組邊界與資料流，不需要放論文級公式，建議將
Model 段落寫成：

```text
Model 定義如何用 canonical SNV evidence 評分候選的 clone/tree configuration。
它指定觀測資料、候選狀態、演化相容性假設，以及把資料轉成 score 或 likelihood
的規則；inference 再依這個定義探索多個候選 configuration，最後由 output
整理 topology、CCF/phi、assignment 與其他 summary。
```

如果要再短一點：

```text
model：定義哪些 clone/tree configuration 與觀測資料相容，以及如何評分；
inference：探索這些候選 configuration 並整理不確定性。
```

這個版本保留文獻共同核心，也不會把「是否保存於候選樹項目」這類 implementation
detail 放進 module boundary 文件。

## 7. Evidence-layer notes

### current repo

- [arch.md](/bip8_disk/boyu114/main_work/arch.md:9-15)：module responsibilities。
- [model.md](/bip8_disk/boyu114/main_work/model.md:45-55)：current posterior target。
- [inference_algo.md](/bip8_disk/boyu114/main_work/inference_algo.md:5-8)：model 與 inference 的分工。
- [output.md](/bip8_disk/boyu114/main_work/output.md:75-127)：latent quantity 與 output semantics。

### historical project context

- [multi-evol-tree/SUMMARY.md](/bip8_disk/boyu114/bip8_disk_boyu_database/multi-evol-tree/SUMMARY.md:19-23)：目前歷史研究主要輸出 local/regional candidate trees，不是 single-cell lineage truth。
- [multi-evol-tree/SUMMARY.md](/bip8_disk/boyu114/bip8_disk_boyu_database/multi-evol-tree/SUMMARY.md:42-61)：related-work 分類與 candidate-set／fail-closed 原則。
- [multi-evol-tree/SUMMARY.md](/bip8_disk/boyu114/bip8_disk_boyu_database/multi-evol-tree/SUMMARY.md:138-154)：HP、PS、methylation 與 VAF/CCF 的證據上限。

### lab-canonical boundary

- [`intersubmod.md`](/big8_disk/liaoyoyo2001/Knowledge/05_tools/intersubmod.md:191-199)：InterSubMod 的 tree 是 read-level methylation distance dendrogram，不能直接稱為 tumor clonal phylogeny。
- lab Knowledge 對 PhyloWGS、CITUP、Canopy、Treeomics、MACHINA 等沒有完整專門索引，故本 report 的方法定義以各自 primary papers 為準。

## 8. Limitations and status labels

- 跨方法的「generative／hybrid／optimization」分類是依論文模型與推論流程整理出的 **inferred synthesis**；論文未必使用完全相同的 taxonomy。
- `eta`、`phi`、`rho`、`bar-rho`、cellular prevalence、clonal prevalence 等命名不是 universal standard；符號必須連同方法一起引用。
- 不同論文對 purity、CCF、cellular frequency、CNV prevalence 的 population denominator 可能不同，不能只因公式外觀相似就直接替換。
- current repo 的 target/spec、runtime source、tests 與 generated receipts 仍需以 current source/test contract 分層核對；本 report 不把論文結果當成 runtime 已通過 validation 的證據。
