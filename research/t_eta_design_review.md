# `T` + `eta` candidate-tree design review

## 短結論

沒有任何一篇已核對的腫瘤演化樹論文完整地說：「先把樹拓樸 `T` 和
clone-specific local fraction `eta` 固定好，再依序猜 `phi`、`z`、`m`。」目前
repo 的做法是把幾個已有方法的想法組合起來：

1. **最接近 `eta -> phi` 的原始先例是 PhyloWGS 的 PhyloSub-model。** 它明確
   引入每個樹節點的輔助變數 `eta_v`，要求它們加總為 1，再用節點與 descendants
   的 `eta` 加總得到 SSM population frequency `phi_v`。這直接支持本 repo 的
   `clone-specific local fraction eta_v` 與 CCF/`phi_v` descendant sum 語意。
   來源：PhyloWGS, *Materials and methods / PhyloSub model*, HTML lines 343–350，
   [原始論文](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)。

2. **但是目前 repo 的整套設計不是 PhyloWGS 的複製品。** TSSB 提供的是
   tree-structured prior；Pairtree 使用 population frequency 與 tree-constrained
   subclonal frequency；PhyClone 則選擇把 node prevalence 邊際化，並在
   topology/clustering 空間做 Particle Gibbs + SMC。它們支持不同部分，沒有任何
   一篇同時指定本 repo 的固定 `K`、單一 founder、Dirichlet `eta`、以及目前的
   `z/m` likelihood marginalization。

3. **「預設」要分成兩種意思。** 如果是「先由 prior 產生／提出候選值」，這是
   Bayesian sampling 的正常流程；如果是「人為固定 `T` 和 `eta`，後面才估計其他量」，
   則不是目前 C++ 的實際流程。候選樹的 `T` 和 `eta` 會被反覆提出、評分、重抽樣和
   rejuvenate；`phi` 在給定 `T`、`eta` 後是直接算出的，不是另一個獨立待猜的量。
   `z` 和 `m` 則在每個候選樹的 likelihood 評分中被加總，不先存成 state。

4. **因此，最準確的描述是：**

   > 演算法持續探索許多組候選的 `T` 與 `eta`。每組候選值都直接產生一組
   > `phi`/CCF；評分時再把 SNV 屬於哪個 clone（`z`）以及 multiplicity（`m`）
   > 的可能性整合進 likelihood。這是本 repo 的 finite-K、Rao–Blackwellized
   > working design，不是某一篇論文原封不動的演算法。

## 目前 repo 的精確對照

### 目前 active C++ 做什麼

以下是 `main_work` 的 current implementation evidence；source status 為
`current`，而非只依賴研究日誌：

| repo 行為 | 證據與 locator |
|---|---|
| 每個候選狀態保存 parent topology 與 `eta` 向量 | [`Particle` 的 `parents`/`eta`](../inference/src/algorithm.cpp#L32-L36)；status: `current` |
| `phi` 由 topology 指定的 descendants 加總 `eta` 得到 | [`cumulative_phi` 與 `visit_phi`](../inference/src/algorithm.cpp#L69-L92)；status: `current` |
| tree prior 與 `eta` Dirichlet prior 進入 state target | [`particle_log_target`](../inference/src/algorithm.cpp#L494-L499)、[`tssb_tree_log_prior`](../inference/src/algorithm.cpp#L112-L121)、[`dirichlet_logpdf`](../inference/src/algorithm.cpp#L144-L152)；status: `current` |
| 初始時抽 topology，再依 tree-shaped alpha 抽 `eta` | [`run` 的初始化](../inference/src/algorithm.cpp#L904-L911)；status: `current` |
| topology 與 `eta` 之後仍會被提出、接受或拒絕 | [`rejuvenate` 的 topology/eta proposals](../inference/src/algorithm.cpp#L925-L991)；status: `current` |
| clone assignment 不作為 `Particle` 的持續 state；site score 以 `sum_v eta_v L_i(phi_v)` 形式對 clone index 加總 | [`site_mixture_log_likelihood`](../inference/src/algorithm.cpp#L180-L193)；status: `current` |
| multiplicity 不作為 `Particle` 的持續 state；site likelihood 對 loader-derived candidates 做 log-sum-exp | [`site_log_likelihood`](../inference/src/model.cpp#L255-L274)；status: `current` |
| `z` 的 MAP assignment 只在輸出整理時產生，不等於 inference state | [`rb_map_assignments`](../inference/src/algorithm.cpp#L501-L518) 與輸出整理 [`algorithm.cpp`](../inference/src/algorithm.cpp#L1068-L1095)；status: `current` |
| artifact metadata 明確把 `topology`/`eta` 列為 state，把 `assignment`/`multiplicity` 列為 Rao–Blackwellized variables | [`diagnostics` state metadata](../inference/src/algorithm.cpp#L1160-L1167)；status: `current` |

因此，current C++ 的 site-level 結構可寫成：

$$
L_i(T,\eta)
=
\sum_v \eta_v
\left[
  \sum_m \pi_i(m)\,
  \operatorname{Binomial}\left(A_i\mid N_i,q_i(\phi_v,m)\right)
\right],
\qquad
\phi_v=\eta_v+
\sum_{w\in\operatorname{descendants}_T(v)}\eta_w.
$$

這個式子是從目前 C++ 的 `site_mixture_log_likelihood` 與
`site_log_likelihood` 抽象出來的 interpretation；數值細節仍以 source code 為準。
其中 `z` 對應外層的 clone mixture index `v`，`m` 對應內層的 multiplicity
candidate。這是對 current code 的 `inferred` reading，而不是宣稱 source 中存在
名為 `z` 的變數。

### 文件 target/spec 與 current runtime 的邊界

[`inference_algo.md`](../inference_algo.md#L11-L43) 將 state 說成 topology + eta，並
描述 assignment/multiplicity 在 candidate-marginalized likelihood 中處理；這與目前
C++ 的結構一致，status: `current`/`documented-current`。

但 [`model.md`](../model.md#L45-L55) 的 `P_A(T,z,eta | ...)` 是較完整的
PhyClone-compatible target/spec，文件自己也標示現有 runtime 尚未同步。它不應被讀成
目前 C++ 已經有一個顯式的 `z` vector 或完整 genotype candidate engine，status:
`target-spec-only`。

## Primary-source crosswalk

### PhyloSub：支持樹、lineage assignment 與 descendant frequency，但不是完整的 repo state 定義

PhyloSub 的原始論文把每個 node 視為一個 subclonal lineage，node 有「只在該
lineage 出現、且不含 descendant 新 SNV」的 population frequency；一個 SNV 的
population frequency 則是它出現的 lineage 加上 descendants 的 frequencies。這正是
「local quantity → cumulative quantity」的生物語意來源。來源：PhyloSub original
paper 的 model description, §“The PhyloSub algorithm”, HTML lines 43–57，
[Jiao et al. 2014 / arXiv full text](https://arxiv.org/abs/1210.3384)。

PhyloSub 同時把 phylogeny 視為 latent structure，使用 Bayesian inference/MCMC 來
保留多個可解釋觀測 SNV frequency 的 phylogenies，而不是只輸出一個必然正確的 tree。
來源：同一原始論文，abstract lines 3–6、background lines 15–17、conclusion
lines 139–147，[同一來源](https://arxiv.org/abs/1210.3384)。

**與本 repo 的關係：**

- 支持 `T` 決定 ancestor/descendant，local fraction 經 descendant sum 形成 CCF/`phi`。
- 支持保留多個 posterior candidate，而不是只保留一棵 MAP tree。
- 沒有證據顯示 PhyloSub 原始論文使用本 repo 的固定 finite `K`、單一 structural
  founder、或目前 C++ 的每-site multiplicity sum。

**優點：** 能把讀數誤差與 tree ambiguity 一起放進 posterior；multiple samples
能進一步限制候選 phylogenies。來源：[PhyloSub conclusion, lines 137–147](https://arxiv.org/abs/1210.3384)。

**缺點：** lineage 若由很少 SNV 定義、頻率低、read depth 不足或 CN 不確定，會很難
重建；作者也明確指出 MCMC 可能長時間卡在 local minima。來源：[PhyloSub conclusion,
lines 143–147](https://arxiv.org/abs/1210.3384)。

### PhyloWGS：`eta_v` 與 `phi_v` descendant sum 的最直接先例

PhyloWGS 的 Materials and methods 先以 TSSB 建立 rooted tree，再為每個 node 引入
滿足 `sum_v eta_v = 1` 的輔助變數；接著明確定義：

$$
\phi_v
=
\eta_v+
\sum_{w\in\mathcal D(v)}\eta_w
=
\eta_v+
\sum_{w\in\mathcal C(v)}\phi_w.
$$

來源：[PhyloWGS, §“PhyloSub model”](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)，HTML lines 329–350，尤其 lines 343–350、equation (2)。這是本 repo 使用
`clone-specific local fraction eta_v` 再由 descendants 推導 CCF/`phi_v` 的最強
primary-source precedent。

PhyloWGS 以 TSSB 作 tree prior，使用 posterior samples 而非只假定 single tree；它
也同時整合 SSM、CNV 與 copy-number-aware allele-count model。來源：[PhyloWGS
overview and conclusions](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)，HTML lines 322–326、338–342。

它對 CNV/SSM 關係的處理也說明為什麼 `m` 或 genotype/CN timing 不能總是先固定：
SSM 可能在 CNV 前、CNV 後，或位於不同 branch；expected allele frequency 會依
演化關係與 maternal/paternal copy breakdown 改變。來源：[PhyloWGS CNV/SSM
cases](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)，HTML lines 163–203、372–412。

**與本 repo 的關係：**

- `eta -> phi`：高度相符。
- `T`、$η$ 作為 inference 中持續變動的 quantity：概念相符，但 PhyloWGS 用的是
  TSSB/MCMC 與它自己的 auxiliary-variable construction。
- `z/m`：PhyloWGS 有 latent tree/lineage、CNV timing 與 allele-copy possibilities，
  但這不等於目前 repo 的每-site `sum_v sum_m` 實作；這裡只能標為 `inferred`
  correspondence，不能說是同一個 algorithm。

**優點：** `eta` simplex 讓 tree-compatible frequencies 自動成立；CNV 與 SSM 一起
提供比單純 VAF 更強的 phylogenetic constraints；作者報告相較 PhyloSub 更快且能處理
WGS-scale data。來源：[PhyloWGS abstract/conclusion](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)，HTML lines 322–327。

**缺點：** 需要 CNV preprocessing；對 amplification，通常需要 maternal/paternal
copy decomposition，否則要限制到較簡單的 CN regions。來源：[PhyloWGS discussion](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)，HTML lines 312–315。
此外，`eta` 的 posterior sampling 與 tree sampling 仍依賴 MCMC；來源：[PhyloWGS
MCMC settings](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)，HTML lines 342–350、416–420。

### TSSB：提供 tree-structured prior，不提供 tumor-specific `eta` 語意

原始 TSSB 論文在 tree node 上使用 `pi_epsilon` 表示 partition mass，並由
`nu_epsilon` 的 stop/pass break 與 `psi_epsilon` 的 child-branching break 建構；
paper 的 equation (2) 與其後的解釋明確使用 `pi`、`nu`、`psi`，不是 tumor-tree
語境下的 `eta` local fraction。來源：[Adams, Ghahramani & Jordan, TSSB original
paper](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf)，PDF page 1, HTML lines 73–105。

TSSB 的 inference state 以資料被分配到哪條 node path 的 assignment strings 為核心，
並用 slice sampling 與 MCMC 探索 tree、sticks、parameters 和 assignments。來源：[TSSB
inference section](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf)，PDF pages 3–4, HTML lines 213–225、265–284。

**與本 repo 的關係：**

- 本 repo 的 `P_K(T)` 名稱是 `TSSB-shaped` working prior；這表示形狀受到 TSSB
  啟發，不表示實作了原始無限 TSSB。
- 原始 TSSB 的 `eta` 在另一個 generalized Gaussian diffusion example 中是
  parent-to-child shrinkage coefficient，不是 node mass。來源：[TSSB hierarchical
  priors](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf)，PDF page 3, HTML lines 174–197。

**優點：** 可以表達無限寬度／深度的 tree-structured partition，且資料可以停在
internal node。來源：[TSSB construction and urn view](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf)，PDF pages 1–2, HTML lines 73–105、144–165。

**缺點：** 原始模型是通用 hierarchical data prior，不是 CN-aware tumor
likelihood；無限 tree/assignment space 也使 inference 需要 slice/retrospective
machinery。來源：[TSSB inference](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf)，PDF pages 3–4, HTML lines 213–284。把它直接改成
本 repo 的 finite-K tumor model 是額外的 modeling decision，status: `inferred`。

### Pairtree：相近的 `eta`/`phi` 輸出語意，但搜尋與頻率 fitting 架構不同

Pairtree paper 把 subpopulation frequency 與 tree-constrained subclonal frequency
分開：subclone 的 cumulative frequency 是該 subpopulation 與所有 descendants 的
population frequencies 加總；tree likelihood 再評估這些 tree-constrained frequencies
對 VAF data 的 fit。來源：[Pairtree original paper, Pairtree Algorithm](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/)，HTML lines 161–169、278–280。

Pairtree 的官方 output contract 直接命名 `eta` 為 population frequencies、`phi` 為
tree-constrained subclonal frequencies，並同時輸出 tree posterior probability、
parents 與 sampled tree information。來源：[official Pairtree README, Pairtree
outputs](https://github.com/morrislab/pairtree#pairtree-outputs)，README section
“Pairtree outputs”, source locator: `phi`/`eta`/`prob`/`parents` entries；status:
`primary-source-code`。

Pairtree 使用 MCMC proposal 搜尋 clone trees，並用 data-guided Pairs Tensor 引導
subclone move；它也明確承認同一資料可能支持多個 tree。來源：[Pairtree tree
search](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/)，HTML lines 242–251、272–287。

**與本 repo 的關係：**

- `eta` 是 local/exclusive population frequency、`phi` 是 cumulative tree-constrained
  frequency：語意相容。
- Pairtree 的 frequency fitting 是對每一棵 tree 做 MAP/optimization；本 repo 則把
  `eta` 直接當成 finite-K candidate-tree state 的 continuous component，再以 SMC
  jointly explore topology + eta。這是架構差異，不能寫成「本 repo 就是 Pairtree」。
- Pairtree 的主要 likelihood 對象是 VAF/read counts 與 tree-constrained frequencies；
  它不是本 repo 的 CN-derived multiplicity candidate marginalization。status:
  `inferred`/`not-equivalent`。

**優點：** 對多 sample、多 subclone 能擴展，並保留多個 tree 的 posterior uncertainty；
官方 paper 也指出 data-guided soft constraints 可避免硬 constraint 排除真實 tree。
來源：[Pairtree abstract and discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/)，HTML lines 131–134、240–251。

**缺點：** low-VAF subclones 的 parent 關係可能無法辨識；遺漏的 genome mutations
也讓 tree 只是 incomplete view；對很大的 tree，搜尋空間與 frequency optimization
仍會變難。來源：[Pairtree uncertainty and scaling discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/)，HTML lines 242–249、251–254。

### PhyClone：它支持 marginalization，但選的是另一種 state split

PhyClone 的 paper 明確說，關鍵好處之一是把 tree nodes 的 clonal prevalence
parameters 邊際化，讓 posterior inference 可以在較低維的 topology space 進行；
來源：[PhyClone original paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)，HTML lines 159–165。

它的符號也不同：$ρ_v$ 是 node 的 clonal prevalence，$̅ρ_v$ 是 node 加 descendants 的
cellular prevalence；$̅ρ_v$ 的 descendant recursion 與本 repo 的 `eta -> phi`
數學形狀相似，但 symbol 和 inference state 不同。來源：PhyClone §2.1–2.2，HTML
lines 173–213，[原始論文](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)。

PhyClone 同時對 topology 與 mutation clustering 做 SMC；為了解決固定 mutation
ordering 的可達性問題，再把 SMC 放進 Particle Gibbs；另外使用 SPR 與 node-assignment
moves 改善 mixing。來源：PhyClone §2.3，HTML lines 236–276，[原始論文](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)。

**與本 repo 的關係：**

- 相同的部分：都認為 bulk data 只部分辨識 tree，因此應保留 posterior uncertainty；
  都使用 sequential/particle-style inference ideas。
- 不同的部分：PhyClone 把 prevalence `rho` 邊際化；目前 repo 把 `eta` 保留在
  candidate-tree state，而把 clone assignment/multiplicity 在 site likelihood 中
  邊際化。
- 因此不能說「PhyClone 告訴我們要把 `T` 與 `eta` 放在 state」；PhyClone 更直接
  支持的是「可以選擇把 node prevalence collapse 掉」，但它本身選了相反的
  prevalence treatment。

**優點：** collapsed prevalence 可降低 topology inference 維度；Particle Gibbs
可解除固定 data-order 對可達 tree 的限制；作者也提供 MAP、consensus 與全 sampled
topology summary。來源：[PhyClone model/inference](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)，HTML lines 159–165、221–275；[official output documentation](https://github.com/Roth-Lab/PhyClone#phyclone-output)，README lines 351–418。

**缺點：** WGS-sized data 通常建議先做 pre-clustering，因為不 pre-cluster 會顯著增加
computational complexity；固定 ordering 的 SMC 也會漏掉部分 tree，需要 Particle
Gibbs correction。來源：[PhyClone pre-clustering and inference](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)，HTML lines 221–228、246–270。

## 「T、eta state；phi、z、m 不在 state」的優缺點

以下分成有文獻直接支持的優點，和由本 repo source 推導的設計取捨。後者標成
`inferred`，不冒充某篇 paper 的原句。

### 優點

1. **不容易產生不符合樹的 CCF。** `eta` 是 simplex，`T` 提供 descendants；
   因而 `phi` 自動是 descendant sum，不需要另外對每個 `phi_v` 加上 parent ≥ child
   等一大組限制。這是 PhyloWGS 明確使用 auxiliary `eta` construction 的核心好處，
   status: `primary-source-supported`。[PhyloWGS lines 343–350](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)。

2. **state 維度較低。** 不把每顆 SNV 的 `z`、每個 SNV 的 `m` 都存進每個候選狀態，
   可以避免 state 維度隨 SNV 數量一起膨脹；`z/m` 的不確定性仍可進 likelihood
   和 posterior responsibility。對「把 node parameters 邊際化以降低 inference
   維度」這個 general strategy，PhyClone 有直接論述；把它延伸到本 repo 的 `z/m`
   是依 current source 做的 `inferred` interpretation。[PhyClone lines 159–165](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)；repo source: [`site_mixture_log_likelihood`](../inference/src/algorithm.cpp#L180-L193)、[`site_log_likelihood`](../inference/src/model.cpp#L255-L274)。

3. **可以保留 tree uncertainty。** `T` 不是只選一棵 tree，而是由 SMC 保留多個
   candidate trees；這符合 PhyloSub、PhyloWGS、Pairtree 與 PhyClone 都強調的 posterior
   uncertainty。[PhyloWGS lines 135–137](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)、[Pairtree lines 169、242–246](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/)、[PhyClone lines 159–165](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)。

4. **`phi` 的定義不會被 observed VAF 直接反解綁死。** tree + eta 先產生
   tree-consistent CCF，再讓 purity、CN、read counts 與 multiplicity likelihood
   共同評分；這保留 CN/VAF ambiguity，而不是把一個 observed VAF 強行轉成唯一 CCF。
   PhyloWGS 對 CNV timing 與 allele-copy relationship 的處理直接支持這個必要性，
   status: `primary-source-supported`。[PhyloWGS lines 149–203](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)。

### 缺點與風險

1. **`eta` 必須被正確解釋。** TSSB 的 node mass 是 `pi`，PhyClone 使用 `rho`/
   `bar rho`；只有 PhyloWGS 的這個 auxiliary construction 直接使用 `eta`/`phi`。
   因此文件必須說「本 repo 採用與 PhyloWGS 相容的 notation」，不能說 `eta` 是所有
   tumor-tree papers 的通用符號。來源：[TSSB lines 81–105、191–197](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf)、[PhyClone lines 178–213](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)。

2. **fixed-K 會把未知的 clone number 變成外加假設。** 本 repo 主分析 `K=6`，
   `K=4/8` 做 sensitivity；這不是 PhyloSub/PhyloWGS/PhyClone 的 nonparametric
   unknown-node treatment。若 K 選錯，可能製造不必要的 clone、把真實 clone 合併，
   或令 posterior 依 K 改變。這是由 current config/documentation 推導的 `inferred`
   risk：[`InferenceConfig::num_nodes=6`](../inference/include/tumor_tree_inference/algorithm.hpp#L13-L25)、[`inference_algo.md`](../inference_algo.md#L19-L31)。

3. **不把 `z` 放進 state，會犧牲持續的 SNV clustering 結構。** 目前 C++ 的 site
   mixture 能對每顆 SNV 算 clone responsibility，並在輸出時產生 assignment summary；
   但 `z_i` 不是會跨 iteration 保留的 joint variable。這表示 current baseline 不能
   自動表達「一群 SNV 必須共同屬於同一個 node」這種額外 clustering structure，除非
   另加 model term。這是從 [`Particle`](../inference/src/algorithm.cpp#L32-L36)、
   [`site_mixture_log_likelihood`](../inference/src/algorithm.cpp#L180-L193) 與
   [`rb_map_assignments`](../inference/src/algorithm.cpp#L501-L518) 推導的 `inferred`
   limitation；不能用 current output 的 MAP assignment 反過來宣稱 `z` 是 sampled state。

4. **不把 `m` 放進 state，會讓 multiplicity prior/model 成為 site-local assumption。**
   目前 loader 由 `major_cn`/`minor_cn` 產生有限 multiplicity candidates，再以目前的
   static-CN q likelihood 加總；這不是完整的 PhyloWGS maternal/paternal/CNV timing
   genotype model，也不是文件 target/spec 的完整 PhyClone `xi`。來源：[`derive_multiplicity_distribution`](../inference/src/model.cpp#L128-L175)、[`expected_alt_probability`](../inference/src/model.cpp#L206-L212)、[`model.md` target boundary](../model.md#L27-L41)。

5. **topology 與 eta 的 posterior 可能有多個 mode，SMC 不會自動解決 identifiability。**
   Tree space 大、低頻 clone 的關係可能資料無法辨識；PhyloSub 提到 MCMC mixing/local
   minima，Pairtree 也指出低 VAF 與大型 tree 的 uncertainty/complexity。來源：[PhyloSub lines 143–147](https://arxiv.org/abs/1210.3384)、[Pairtree lines 242–249](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/)。

6. **finite-K prior 常數是 repo working choice，不是生物學定律。** depth penalty、
   child-count penalty、Dirichlet alpha shape 會影響哪些 tree/eta 被偏好；因此需要
   prior predictive 與 K/prior sensitivity，而不能把它包裝成 PhyloWGS/TSSB 原始 prior。
   來源：[`model.md` finite-K prior specification](../model.md#L57-L72) 與實作
   [`tssb_tree_log_prior`](../inference/src/algorithm.cpp#L112-L121)、[`tssb_mass_prior_alpha`](../inference/src/algorithm.cpp#L95-L109)；status: `current` + `inferred-risk`。

## 哪些是本 repo 自己的 finite-K 設計

下列項目沒有被找到一篇論文完整指定；它們應在文件中標成 repo working design：

| finite-K 設計 | current evidence | 判定 |
|---|---|---|
| 固定 `K=6`，以 `K=4/8` 做 sensitivity | [`InferenceConfig`](../inference/include/tumor_tree_inference/algorithm.hpp#L13-L25)、[`inference_algo.md`](../inference_algo.md#L19-L31) | `current repo design` |
| `parents` 必須形成單一 connected tumor tree，只有一個 `-1` structural-root child | [`valid_tree`](../inference/src/algorithm.cpp#L40-L59) | `current repo design` |
| structural root 不承載 SNV，founder 的 descendant sum 為 1 | [`cumulative_phi`](../inference/src/algorithm.cpp#L77-L92)、[`model.md`](../model.md#L94-L105) | `current repo design` |
| topology prior 使用 `-0.35 * depth - 0.12 * children^2` | [`tssb_tree_log_prior`](../inference/src/algorithm.cpp#L112-L121)、[`model.md`](../model.md#L57-L72) | `repo-specific working prior` |
| `eta | T` 使用由 depth/children 產生的 Dirichlet alpha，且 eta 全部為正、總和為 1 | [`tssb_mass_prior_alpha`/`dirichlet_sample`](../inference/src/algorithm.cpp#L95-L109)、[`algorithm.cpp`](../inference/src/algorithm.cpp#L144-L167) | `repo-specific finite-K parameterization` |
| 用 annealed SMC、systematic resampling、local/global topology moves 與 eta rejuvenation | [`inference_algo.md`](../inference_algo.md#L45-L73)、[`algorithm.cpp`](../inference/src/algorithm.cpp#L925-L991) | `repo-specific inference composition` |
| `z` 不存成 particle state，site-level 以 clone mixture marginalization 評分；MAP assignment 只在 output 整理 | [`site_mixture_log_likelihood`](../inference/src/algorithm.cpp#L180-L193)、[`rb_map_assignments`](../inference/src/algorithm.cpp#L501-L518) | `current C++ design` |
| `m` 不存成 particle state，由 major/minor CN 派生 candidates，再於 site likelihood 中 marginalize | [`derive_multiplicity_distribution`](../inference/src/model.cpp#L128-L175)、[`site_log_likelihood`](../inference/src/model.cpp#L255-L274) | `current C++ design; simplified CN working model` |
| `xi`/`error_rate=0.001` 的完整 PhyClone target/spec 尚未同步到 C++ | [`model.md` warning/boundary](../model.md#L1-L41)、[`inference_algo.md`](../inference_algo.md#L16-L25) | `documentation target only` |

## 建議對外／對文件的準確說法

建議寫成：

> 本 repo 的每個候選腫瘤演化樹會攜帶一個有限節點的 topology `T` 與一組
> clone-specific local fractions `eta`。`phi`/CCF 不是另外猜的一組數，而是依照
> `T` 的 descendants 對 `eta` 做 descendant sum 後得到。對每個 SNV，current C++
> baseline 不把 clone assignment 或 CN-derived multiplicity 存進候選樹 state；它們
> 在 site likelihood 中以 mixture／candidate marginalization 一起評分，之後再整理
> assignment/multiplicity posterior summary。

這句話應附帶兩個限制：

- `eta -> phi` 的數學構造有 PhyloWGS/PhyloSub-model precedent，但 `eta` 不是所有
  tumor-tree paper 的 universal symbol；TSSB 用 `pi`，PhyClone 用 `rho`/`bar rho`。
- current C++ 的 multiplicity model 是由 major/minor CN 派生的 simplified finite
  candidate model；文件中的完整 PhyClone `xi`/genotype-aware target 仍是
  `target-spec-only`，不能說已在 runtime 實作。

## Evidence packet

```text
worker: research-note coordinator (capacity fallback)
scope: primary-source review of T + eta state, phi/CCF descendant derivation,
       z/m likelihood marginalization, and finite-K repo-specific additions
queries: PhyloSub eta phi; PhyloWGS eta phi; TSSB node mass pi eta;
         Pairtree eta phi population frequencies; PhyClone clonal prevalence;
         current repo Particle cumulative_phi site_log_likelihood

source layers:
  current repository: available
  lab knowledge base: available; lab-first preflight had no direct focused entries
  historical KB: available; scanned navigation and the relevant multi-evol-tree summary
  external primary sources: available

findings:
  - claim: PhyloWGS explicitly uses simplex eta_v and derives phi_v by descendant sum
    status: primary-source
    source: https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8
    locator: Materials and methods, “PhyloSub model”, HTML lines 343-350; equation (2)
  - claim: PhyloSub models latent phylogeny and reports posterior uncertainty over trees
    status: primary-source
    source: https://arxiv.org/abs/1210.3384
    locator: abstract lines 3-6; background lines 15-17; conclusion lines 139-147
  - claim: original TSSB uses pi/nu/psi for node mass and stick-breaking, not tumor eta
    status: primary-source
    source: https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf
    locator: PDF page 1, HTML lines 73-105; Gaussian example page 3, lines 191-197
  - claim: Pairtree separates population frequencies eta from tree-constrained phi in its official output
    status: primary-source-code
    source: https://github.com/morrislab/pairtree#pairtree-outputs
    locator: “Pairtree outputs” section, phi/eta/prob/parents entries
  - claim: Pairtree samples candidate trees and reports posterior uncertainty; MAP frequency fitting is an approximation
    status: primary-source
    source: https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/
    locator: HTML lines 169, 242-251, 272-287
  - claim: PhyClone marginalizes node prevalence and uses topology/clustering SMC plus Particle Gibbs
    status: primary-source
    source: https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563
    locator: HTML lines 159-165, 173-213, 221-275
  - claim: current C++ stores topology/eta, derives phi, and marginalizes clone/multiplicity at site scoring
    status: current
    source: ../inference/src/algorithm.cpp and ../inference/src/model.cpp
    locator: algorithm.cpp lines 32-36, 69-92, 180-193, 494-518, 904-991;
             model.cpp lines 128-175 and 255-274
  - claim: fixed K, single founder, working prior constants, and current simplified CN multiplicity are repo-specific
    status: current + inferred
    source: ../inference/include/tumor_tree_inference/algorithm.hpp;
            ../inference/src/algorithm.cpp; ../inference/src/model.cpp; ../model.md
    locator: algorithm.hpp lines 13-25; algorithm.cpp lines 40-59, 95-121;
             model.cpp lines 128-175; model.md lines 57-72

gaps:
  - The main investigation used four parallel read-only subagents covering the
    lab knowledge base, current repository, primary literature, and note synthesis.
    The coordinator independently rechecked the repository claims and integrated
    the evidence here.
  - PhyloClone PMC access returned a reCAPTCHA page; the publisher's open article text
    was used as the primary source instead.
  - “z” is not a universal symbol across these papers. Where current code has no literal
    z variable, the mapping to clone-mixture index is marked inferred.
```
