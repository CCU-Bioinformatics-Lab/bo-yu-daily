# W6：正文核對（methods_survey README 的「待核」項目）

- 核對日期：2026-10-17
- 範圍：README 與 W1–W5 中標「待核」或「推論／記憶」的推論演算法、CN 處理、程式碼位置與 venue。
- 讀取方式：主要讀 PMC OA 全文（以 Europe PMC／NCBI efetch 取得 JATS XML，暫存在 `/tmp`，沒有放進 repo）。PICTograph 的全文改用 OUP 網頁讀取，COMPASS 的 MCMC moves 讀 Supplementary Note 2（Springer ESM PDF）。NestedBD-Long 的 venue 用 Crossref metadata 核對，程式碼位置則對照論文的 Code／Data availability 段落並實際打開網址。
- 狀態定義：
  - **confirmed**：原描述與正文一致，只補細節。
  - **corrected**：原描述有錯，或簡化到會誤導。
  - **still-unverified**：正文沒有寫，或無法取得正文。
- 證據 URL 一律附 PMC 頁面（`https://pmc.ncbi.nlm.nih.gov/articles/PMCxxxx/`），段落名稱照原文。

---

## 1. COMPASS（Sollier et al., Nat Commun 2023，10.1038/s41467-023-40378-8）

| 項目 | 內容 |
|---|---|
| 原描述 | README C 類：「Tapestri；CNA／CNLOH 事件與 SNV 同樹；**MCMC**」。W3：「Bayesian + MCMC（SCITE 系的 tree move）」。W2：「Bayesian＋MCMC；每個 variant 各自的 ADO rate…建模 per-variant ADO 與 doublet」 |
| 核對後描述 | **推論**：搜尋目標是 MAP tree。作法是 **simulated annealing**，不是用來做 posterior sampling 的 MCMC。它沿用 MCMC 的 proposal 與 Metropolis 式接受規則，接受率是 `min(1, exp(log(P(T)P(D|T))/T))`，溫度 T 逐步下降。初始樹是隨機的 Prüfer 序列樹，節點數 3–10，一開始沒有 CNA。分兩階段：(1) 先跑不含 CNA 的 SA，接在 root 的 cell 視為 normal，用它們估每個 region 的權重 ρk，並篩出深度有偏移的候選 region；(2) 再跑含 CNA 的 SA，CNA 只能加在候選 region。cell attachment 以 SCITE 的方式邊際化掉，但 node 權重 πn 是學出來的，不是 uniform。πn 與 per-variant dropout rate μi 在**每一步 MCMC 內用 EM 求 MAP**，沒有被 sample。<br>**Tree moves**（Suppl. Note 2）：prune & reattach、swap node labels、move event（SNV 或 CNA，可移到新節點或既有節點）、split／merge node、add／remove CNA event、exchange loss↔CNLOH、change alleles affected by a CNA、merge／duplicate CNA。<br>**CNA 建模**：CNA 分三種，gain、loss、CNLOH。region 以 gene 為單位，也就是同一 gene 的 amplicon 合併成一個 region。region 內有 variant 時，CNA 是 **allele-specific**，會指定影響哪一個 allele，而且該 allele 必須已存在於該節點。同一 region 可以在不同 lineage 發生多次 CNA，但**每條 lineage 最多一次**。SNV 只能獲得一次，但可以在多條 lineage 中失去（Dollo 型）。read depth 用 negative binomial 建模。allelic read count 用 beta-binomial 建模，並對 dropout 組合求和。prior 會懲罰節點數與 CNA 數，導致 LOH 的 CNA 罰得更重，相鄰 region 的 CNA 算成一個事件。germline SNP 可以一起放進模型，用來輔助偵測 CNA。<br>**ADO**：每個 variant 有自己的 dropout rate μi，用 beta prior（以 0.05 為中心）配 EM 估計。ref 與 alt 各 copy 都可能獨立 drop out。<br>**Doublet**：可選。作法是 ∞SCITE 式的 singlet／doublet 混合，doublet 機率為 δ。doublet 的 genotype 定義為：allele copy 相加，region copy number 取平均。<br>程式碼：C++，GPL3，https://github.com/cbg-ethz/COMPASS |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC10427627/ — Results「Probabilistic model for joint SNV and CNA single-cell tumour phylogenies」：“When variants are present in a region, the CNA calls are allele-specific”、“at most once per lineage”。Methods「Simulated annealing」：“we use a simulated annealing (SA) approach… The MCMC moves are described in the Supplementary Note 2”。Methods「Estimation of the node probabilities and dropout rates」：“we use the parameters which maximise the posterior probability… EM algorithm… inside each MCMC step”。Methods「Doublets」：“Doublets can optionally be modelled… as is done in ∞SCITE”。Supplementary Information（41467_2023_40378_MOESM1_ESM.pdf）Supplementary Note 2「MCMC moves for exploring the tree space」2.1–2.8。Code availability 段落 |
| 狀態 | **corrected**：「MCMC」應改成「simulated annealing（以 MCMC moves 搜 MAP tree）」。CNA allele-specific、ADO、doublet 的描述 confirmed |

## 2. ConDoR（Sashittal et al., Genome Biol 2023，10.1186/s13059-023-03106-5）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「constrained k-Dollo；CN cluster 約束 loss」。W2：「MILP（以 ILP 求 ML，推論／記憶）；CN 只以 cluster 形式使用」。W5：「combinatorial（MILP，待核）」 |
| 核對後描述 | **確實是 MILP**：Python 3 實作，用 Gurobi 9.0.3 精確求解。問題名稱是 CkDP-RC：輸入 variant／total read count 矩陣 Q、R，copy-number clustering σ 與整數 k，在 constrained k-Dollo phylogeny 的約束下最大化 beta-binomial likelihood `Pr(Q|R,A)`。<br>**CN 如何約束**：只需要每個 cell 的 **copy-number clustering**，也就是 CN clone label。**不需要 CN tree，也不需要整數 CN profile**。約束有兩條：(1) mutation j 在邊 (v,w) 上 loss 時，必須 σ(v)≠σ(w)，也就是 loss 只能發生在 CN cluster 改變的邊上；(2) 同一個 CN cluster 的節點在樹上形成 connected subtree，代表每種 CN profile 只出現一次。此外，每個 mutation 最多 gain 一次、最多 loss k 次。SNV 和 germline SNP 都可放入，SNP 的 root 狀態為 1。p=1 時退化成 infinite sites；p=n 時退化成 k-Dollo。<br>論文還特別和 SCARLET 對照：SCARLET 需要 CN profile 與 CN tree，ConDoR 不需要。在 Tapestri 資料上，CN clustering 是從 amplicon 的 total read 做 clustering 得到。<br>程式碼：https://github.com/raphael-group/ConDoR（MIT） |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC10688497/ — Results「Constrained k-Dollo model」與「Definition 1」：“we only allow such losses between cells that belong to distinct copy-number clusters”、“cells belonging to the same cluster form a connected subtree”。「Problem 1」之後：“an efficient mixed linear integer program (MILP)… using Gurobi [43] (version 9.0.3)”。Methods「ConDoR algorithm for constrained k-Dollo model」：“We formulate a mixed integer linear program (MILP) to solve Problem 1 exactly”。Evaluation：“SCARLET is given… the precise copy-number profile of each cell and the true copy-number tree as input”。Conclusions：“ConDoR currently takes the read count matrices… and the copy-number clustering as input”。Methods「Copy-number clustering」 |
| 狀態 | **confirmed**（MILP，用 CN cluster 約束 loss）。補充：不需要 CN tree |

## 3. CalicoST（Ma et al., Nat Methods 2024，10.1038/s41592-024-02438-9）

| 項目 | 內容 |
|---|---|
| 原描述 | README D 類：「spatial transcriptomics；是（allele-specific）；germline SNP phasing 的 BAF」。W3：「HMRF/HMM 推 allele-specific CN clone，再以 CNA／LOH 為 m[arker]…」 |
| 核對後描述 | 流程分兩段。<br>**CN／clone 推論**：在固定 clone 數 M 下，用 block coordinate ascent 交替做兩件事：給定 clone label ℓ 時，以 HMM 解 copy number state Z 與 RDR／BAF 參數；給定 Z 時，以 HMRF（空間 Markov random field）解 ℓ。最後再從 RDR／BAF 換算 integer 的 allele-specific copy number A、B。<br>**建樹**：**只用高信度的 LOH events 當 phylogenetic character**，依 LOH 不可逆的假設，用 **Startle** 建樹。Startle 是 Sashittal et al. 為 CRISPR-Cas9 lineage tracing 設計的 star homoplasy 方法。過濾門檻：LOH 至少 3 個 bin，且該 clone 的 SNP-covering UMI 至少 100（皆為預設值）。<br>gain／loss 等非 LOH 的 CNA **不進入建樹**。<br>**Phylogeography**：把葉節點放在 clone 的空間中心，祖先位置用 Gaussian diffusion 推（變異數與邊上 mutation 數成正比），以 maximum likelihood 估計。<br>程式碼：https://github.com/raphael-group/CalicoST（BSD-3） |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11621028/ — Methods「CNAs and clone inference problem」：“combines the HMM of copy number states with the HMRF of cancer clones… block coordinate ascent”。Methods「Reconstructing tumor phylogeography」：“builds a phylogeny between the cancer clones using the LOH events as phylogenetic markers… We construct a phylogenetic tree for highly confident LOH events under the irreversibility assumption using Startle33”。Ref 33：“Startle: a star homoplasy approach for CRISPR-Cas9 lineage tracing. Cell Syst”。Code availability 段落 |
| 狀態 | **corrected**：「以 CNA／LOH 為 marker」要改成「只以 LOH events 為不可逆 character，用 Startle（star homoplasy）建樹」。allele-specific confirmed |

## 4. DEVOLUTION（Andersson et al., Commun Biol 2021，10.1038/s42003-021-02637-6）

| 項目 | 內容 |
|---|---|
| 原描述 | README B 類：「SNV＋CNA event；multi-region｜**deconvolution＋parsimony**｜有（為 aneuploid 腫瘤設計）」。W1：「parsimony 類；細節以正文為準」 |
| 核對後描述 | 流程依序是：<br>(1) 輸入每個 alteration（SNV、gain、loss、cnni 等）在每個 biopsy 的 **mutated clone fraction（MCF）**。MCF 要由外部工具先算好，例如 PyClone、SciClone、DeCiFer、SVclone，或由 log2 ratio／VAF 換算。<br>(2) 用 DBSCAN 把在各 biopsy 中 MCF 相近的 alteration 聚類。<br>(3) 以「空間分配」演算法做 subclonal deconvolution。目標是盡量減少 parallel evolution 與 back mutation，有多種解時採用 largest-available-space 規則。<br>(4) 得到二元的 event matrix（subclone × alteration）。<br>(5) **兩種建樹都做**，都用 R 套件 **phangorn**：<br>　• **ML**：先以 Hamming distance 做 neighbor joining 得到起始樹，再用 `pml` 與 `optim.pml` 優化（Jukes–Cantor，`optEdge=TRUE`）。<br>　• **Maximum parsimony**：用 `pratchet`（parsimony ratchet，Fitch），branch length 用 `acctran`。<br>兩者都 root 在不帶任何 alteration 的 normal cell。<br>**CN 處理**：CNA 被當成二元 event，與 SNV 地位相同。start／end 位置差在 1 Mbp 以內（預設）且類型相同時，視為同一事件。沒有 copy number state 或 multiplicity 模型，CN 只透過外部給定的 MCF 進入。<br>程式碼：R（≥4.0.2），https://github.com/NatalieKAndersson/DEVOLUTION |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8452746/ — Methods「The software」：“Usage of a mathematical model to reconstruct the phylogenetic trees, in this case maximum likelihood and maximum parsimony”。Methods「Reconstruction of phylogenetic trees」：“The maximum likelihood trees were reconstructed using the pml algorithm in the package phangorn… initial tree given by the neighbor joining method… optim.pml… Jukes Cantor model”、“The maximum parsimony trees were constructed using the parsimony ratchet algorithm (pratchet) in the R package phangorn with the Fitch algorithm”。Methods「Preprocessing of the data」（MCF 為輸入、1 Mbp cutoff）。「Clustering of genetic alterations…」（DBSCAN）。Code availability 段落 |
| 狀態 | **corrected**：「deconvolution＋parsimony」要改成「MCF 輸入 → DBSCAN 聚類 → subclonal deconvolution → event matrix，再用 phangorn 建 ML（pml/optim.pml，JC）與 MP（pratchet/Fitch）兩種樹」。CN「有」需加註：CNA 只是二元 event，MCF 外給 |

## 5. SiCloneFit（Zafar et al., Genome Res 2019，10.1101/gr.243121.118）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「DP clustering＋finite-sites tree；doublet」。W2：「Bayesian nonparametric（DP clustering…）」，推論細節標「推論／記憶」 |
| 核對後描述 | **模型**：輸入是 cell × site 的 **genotype 矩陣**（binary {0,1,X} 或 ternary {0,1,2,X}），不是 read count。cell 先用 **tree-structured Chinese restaurant process**（延伸 Meeds et al. 2008）分到 clone。clone 位於 **rooted binary clonal phylogeny 的葉節點**；樹的 prior 是 topology uniform、branch length 指數分布。clonal genotype 沿樹的演化用 SiFit 的 **finite-site CTMC**：0→1 是 point mutation；1→0 與 1→2 代表 deletion／LOH。速率參數有兩個，λr（recurrent mutation）與 λl（mutation loss），genotype 的 prior 用 Felsenstein pruning 計算。觀測誤差用 FP rate α 與 FN rate β 建模。<br>**Doublet 模型**：每個 cell 有一個 Bernoulli 變數 Yj 表示是否為 doublet，doublet 率 δ 服從 Beta 分布。每個 cell 另有第二個 cluster indicator cj2；doublet 的 genotype 用 ⊕ 或 logical OR 合成。<br>**推論**：Gibbs sampler（仿 Neal 2000），步驟如下：<br>　• cluster indicator 用 partial Gibbs／partial MH 更新；新增 cluster 或刪除 singleton 時改變維度，屬於 partial reversible-jump。<br>　• tree 與演化參數用 MH 更新。<br>　• clonal genotype 從 conditional posterior 抽樣。<br>　• α、β 用 rejection sampling。<br>　• CRP concentration α0 用 Escobar & West 方法。<br>程式碼：Java，https://bitbucket.org/hamimzafar/siclonefit（MIT） |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6836738/ — Results「Overview of SiCloneFit」：“phylogeny-based Chinese restaurant process (clusters reside at the leaves of a phylogeny)… Gibbs sampling algorithm comprised of partial reversible-jump and partial Metropolis-Hastings updates”。Methods「Model of evolution and error model」：“Point mutations can result in the genotype transition 0 → 1, whereas LOH and deletion can result in… 1 → 0 or 1 → 2”。Methods「Doublet-aware model description」。Methods「Inference」。「Software availability」 |
| 狀態 | **confirmed**，需精確化：「DP clustering」改寫為「tree-structured CRP（clone 在 binary clonal tree 的葉節點）」，並註明輸入是 genotype 矩陣、推論為 Gibbs＋partial RJ-MCMC＋MH |

## 6. CellPhy（Kozlov et al., Genome Biol 2022，10.1186/s13059-021-02583-w）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「GT16 ML phylogenetics（RAxML-NG）」，年份 2022。W2 依記憶撰寫 |
| 核對後描述 | **模型**：有兩種 finite-site、time-reversible 的 genotype 模型：**GT16**（16 個 phased diploid 狀態）與 **GT10**（10 個 unphased 狀態，約快一倍）。<br>**Error model**：兩個參數，ADO rate δ 與 amplification／sequencing error ε，最多考慮一次 error。輸入有兩種模式：**CellPhy-ML** 讀 GT（genotype matrix 或 VCF 的 GT 欄）；**CellPhy-GL** 讀 VCF 的 PL 欄（genotype likelihood）。<br>**推論**：在 RAxML-NG 裡做 ML tree search。預設 20 棵起始樹，10 棵由 randomized stepwise addition parsimony 產生，10 棵 random。之後以 SPR moves 爬山，交替優化參數與 topology：替換率與頻率用 L-BFGS-B，δ 與 ε 用 Brent。<br>**附加功能**：branch support 可用 standard bootstrap 或 transfer bootstrap；也能做 ancestral state reconstruction，把 mutation map 到 branch 上。<br>**CN**：不建模 CN。<br>程式碼：https://github.com/amkozlov/cellphy。出版：Genome Biol 23:37，2022-01-26 |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8790911/ — Methods「Model of nucleotide substitution for phased/unphased diploid genotypes」（GT16／GT10）。「Single-cell genotype error model」。Methods「Phylogenetic tree search」：“starts by default with 20 different trees, ten obtained using a maximum parsimony-based randomized stepwise addition order routine and ten with a completely random topology… SPR”。「Model parameter optimization」：“L-BFGS-B… Brent’s method”。「Branch support」。「Input data」（CellPhy-ML／CellPhy-GL） |
| 狀態 | **confirmed**（補 GT10、GL 模式、搜尋細節） |

## 7. DelSIEVE（Kang et al., Genome Biol 2025，10.1186/s13059-025-03738-9）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「finite sites＋單點 deletion」。W2：「推論細節（…BEAST 2）依記憶撰寫」 |
| 核對後描述 | **輸入**：每個候選位點、每個 cell 的 raw read count，包括三個 alternative nucleotide 的計數（遞減排序）與 total coverage。可另外輸入 background site，用來做 acquisition bias correction。<br>**Genotype 狀態**：7 個，0/0、0/1、1/1、1/1′、0/-、1/-、-。可分辨 28 種 genotype transition，歸成 17 類 mutation event，比 SIEVE 多 8 類。<br>**演化模型**：CTMC 是 **time non-reversible、reducible** 的。mutation rate 設為 1，back mutation 相對速率為 1/3，deletion 相對速率為 d，並加上 discrete Gamma（4 類）描述 among-site rate variation。<br>**樹**：rooted binary cell tree，root 是 normal cell，root 與 MRCA 之間有一段 trunk。branch length 的單位是每個位點的 expected somatic mutation 數。<br>**Read count 模型**：nucleotide read count 用 Dirichlet-multinomial，coverage 用 negative binomial。dropout 有兩種模式，ADO 與 LDO（locus dropout）。<br>**推論**：d、T、β、η 以 **MCMC** 估計 posterior。之後在給定的樹上，用 **maximum likelihood** 推每個節點的 genotype。<br>**實作**：Java。正文沒有寫 BEAST 2，但官方 GitHub README 寫明 “available as a package of BEAST 2”，目前相容 BEAST 2.6。<br>**CN**：只建模 deletion（單點的 allele loss），不建模 gain 或一般 CNA。論文模擬顯示中等程度的 CNA 對結果影響小，CNA 太多時 branch 會被拉長。<br>程式碼：https://github.com/szczurek-lab/DelSIEVE（GPL-3） |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12376439/ — Results「Overview of the DelSIEVE model」（7 個 genotype、28 transitions／17 events）。Methods「Statistical phylogenetic model behind DelSIEVE」：“time non-reversible and reducible… Hidden random variables d,T,β,η are estimated using MCMC”。Methods「Model of raw read counts」：“Dirichlet-Multinomial… negative binomial”。Results「DelSIEVE is robust to occurrence of doublets and moderate copy number aberrations (CNAs)」。BEAST 2：https://github.com/szczurek-lab/DelSIEVE README |
| 狀態 | **confirmed**（BEAST 2 由官方 repo README 確認，正文本身沒有寫） |

## 8. PICTograph（Zheng et al., Bioinformatics 2022，10.1093/bioinformatics/btac367）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「SNV＋外給 CN／multiplicity／purity｜JAGS MCMC＋spanning tree 列舉｜CN 有（外給）」 |
| 核對後描述 | **CN 處理**：CN 是**條件化的固定輸入**。模型 “conditional on the multiplicity m_is, tumor purity p_s and copy number of the tumor c_is”，這些值由其他方法事先估好，不會被推論。Discussion 承認這些值被當成沒有誤差，其不確定性**不會**傳到 CCF posterior 或 cluster membership。正文沒有指定用哪個 CN 工具；模擬資料假設 diploid background。<br>**推論**：CCF 與 clustering 用 JAGS（4.3.0）跑 MCMC，cluster 數 K 在 1–15 之間用 BIC 選。建樹時只用 **MAP 的 CCF 與 cluster**：先以 sample presence 與 lineage precedence 篩候選邊，再用修改過的 Gabow–Myers 列舉 spanning tree，刪掉違反 sum condition 的樹，剩下的樹用 SCHISM 的 fitness 打分，同分的 top trees 合成 ensemble tree。<br>程式碼：https://github.com/KarchinLab/pictograph |
| 證據 | https://academic.oup.com/bioinformatics/article/38/15/3677/6595188（PMC9344857；Europe PMC 全文 API 回 500，改讀 OUP 網頁）— Sec. 2.1：“conditional on the multiplicity… tumor purity… and copy number”、JAGS／BIC／Gabow–Myers／SCHISM fitness。Sec. 2.2：模擬假設 diploid。Discussion：輸入假設無誤差 |
| 狀態 | **confirmed**（補充：建樹只用 MAP CCF，CN 不確定性不傳遞） |

## 9. CALDER（Myers et al., Cell Syst 2019，10.1016/j.cels.2019.05.010）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「SNV；longitudinal｜MILP＋時間順序約束｜CN 否」。W1：「主要假設 copy-neutral」。W5：「ILP（longitudinal constraint，待核）」 |
| 核對後描述 | **推論**：問題是 LVAFFP-U。輸入 F 的上下界（由 read count 算 confidence interval），求 F̂=UB；B 是 perfect phylogeny 矩陣。約束包括 sum condition、permanent extinction condition、lineage continuity condition，加上 ut,v=0 或 ≥h。目標是最小化 ‖U‖0。整個問題寫成 **MILP** 求解。正文另外描述一個 Gabow–Myers 的 spanning tree 列舉版本，用於列舉所有解。clustering 用 absence-aware clustering。<br>**CN**：**不建模**。Discussion 明說 “we focused our analysis on SNVs in diploid regions, ignoring copy number aberrations (CNAs)”。前處理時，若某 mutation 的 VAF 下界 >0.5，就視為 CN 異常並丟棄。<br>程式碼：https://github.com/raphael-group/calder |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC7263382/ — Results「Longitudinal Variant Allele Frequency Factorization Problem with Uncertainty (LVAFFP-U)」：“CALDER… formulates and solves this problem as a mixed integer linear program (MILP)”。STAR Methods「Enumerating spanning trees」。Discussion：“ignoring copy number aberrations”。「Data processing」：“lower bound frequency… >.5… considered to have abnormal copy number and was discarded”。「Data and Software Availability」 |
| 狀態 | **confirmed** |

## 10. BAMSE（Toosi et al., BMC Bioinf 2019，10.1186/s12859-019-2824-3）

| 項目 | 內容 |
|---|---|
| 原描述 | README：「SNV counts；multi-sample｜Bayesian model selection｜CN 否」 |
| 核對後描述 | **框架**：只要求每個 mutation 有 `Pr(D_n | f_n)`。論文說 “BAMSE can take copy number variations (CNVs) into account by incorporating copy number information in the frequency probability distribution”。<br>**實作**：用的是 **diploid、無 CNV** 的 binomial likelihood（含 sequencing error）。在這個前提下，likelihood 是 log-concave，才能用 CVXPY 做 convex optimization；候選 clustering 用 K-means 產生；樹用 Algorithm 1 列舉「ISA violation 小於門檻」的樹。作者把 CNV 支援列為 future work，並寫明 “we did not involve copy number variations for the sake of a fast approximate algorithm”。<br>**結論**：實務上不處理 CN。<br>程式碼：https://github.com/HoseinT/BAMSE |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6551234/ — Implementation「The Bayesian Model」（Eq. 4 diploid formula、CVXPY）。「Searching for good models」：“When there is no copy number variants (CNVs)… K-means”。Discussion：“we did not involve copy number variations for the sake of a fast approximate algorithm… MCMC based inference can be indeed used” |
| 狀態 | **confirmed**（「否」正確；可加註：框架上可以接 CN，但實作沒有） |

## 11. SCICoNE（Kuipers et al., Bioinformatics 2025，10.1093/bioinformatics/btaf072）

| 項目 | 內容 |
|---|---|
| 原描述 | README D 類：「淺層 scWGS｜推論為 total」。W3：「論文沒寫明」 |
| 核對後描述 | **確定是 total CN**。輸入只有校正過 GC 與 mappability 的 per-bin read count，沒有 BAF 或 allele 資訊。event 是 segment 的 amplification／deletion（+S／−S），clone 的 profile 是一串整數 total copy number，例如 (4,3,2,2,2)。read 落在 segment 的機率正比於 ckj·sk。Conclusions 把 allele-specific 列為未來方向，提到 “for considering allele-specific events where methods currently look at the phasing…”。<br>**推論**：先用 dynamic programming 跨 cell 偵測 breakpoint。再用 MCMC 在 CNA tree 與 event vector 空間 sample，moves 包括 prune-reattach、label swap、add／remove events、add／remove node、condense／split、genotype-preserving prune-reattach。最後做 maximal search：先在 PhenoGraph cluster 上跑，初始樹用 Ward 階層聚類，跑 10 條 chain，再回到全資料。<br>程式碼：C++，https://github.com/cbg-ethz/SCICoNE |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11897432/ — 「2.1 Model overview」：“corrected counts can be assumed to be proportional to the underlying copy number”，以及 Fig. 1 圖說 “copy number profile of Clone 4 is (4,3,2,2,2)”。「2.4 CNA trees」Eq. 3。「2.7 MCMC scheme」。「2.8 Maximal search」。「4 Conclusions」。Code availability |
| 狀態 | **confirmed**（「推論為 total」可升級為「total（正文確認）」） |

## 12. NestedBD（Liu et al., AMB 2024，10.1186/s13015-024-00264-4）與 NestedBD-Long

| 項目 | 內容 |
|---|---|
| 原描述 | README D 類：「NestedBD（含 -Long）｜2024 AMB｜sc CN｜推論為 total」。待核清單：「NestedBD-Long 的正式 venue 未完全確認」 |
| 核對後描述 | **CN 類型**：**total CN**。每個 bin 的 CN 狀態空間是 {0,1,2,…}（likelihood 計算時上限 k，預設 9），沒有 allele 維度。注意：模擬器在產生資料時會隨機選 paternal 或 maternal allele 放 CNA，但推論吃的是 total CN profile。<br>**輸入**：已估好的 single-cell CN profile，不是 read count。用 N(ct, σ²) 描述 CN 估計誤差。<br>**模型**：每個 copy 都有 linear birth-death 過程（amplification λ、deletion μ），bin 之間假設獨立。樹的 prior 是 birth-death branching process。<br>**推論**：BEAST 2 package 的 MCMC，可得到有時間意義的 branch length。<br>程式碼：https://github.com/Androstane/NestedBD<br>**NestedBD-Long 的 venue**：Liu & Nakhleh，“Inferring Phylogenetic Trees of Cancer Evolution from Longitudinal Single-Cell Copy Number Profiles”，收錄於 *Comparative Genomics*（RECOMB-CG 2025，Seoul，會議開始日 2025-04-24），LNCS，Springer，pp. 9–23，first online 2025-09-01，DOI 10.1007/978-3-031-94928-9_2。preprint：bioRxiv 10.1101/2025.03.17.643834 |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11059640/ — Methods 開頭：“The copy number profile of a cell at each bin is an element of {0,1,2,…}”。「A birth-death evolutionary model of CNAs」。「Accounting for error in copy number profile estimates」。Conclusion：“implemented as a BEAST 2 package”。「Availability of data and materials」。Venue：Crossref `https://api.crossref.org/works/10.1007/978-3-031-94928-9_2`（container-title “Comparative Genomics”／LNCS；conference_acronym “RECOMB-CG”，conference_year 2025，first_online 2025-09-01，page 9-23） |
| 狀態 | **confirmed**（total CN；NestedBD-Long venue 確定為 RECOMB-CG 2025，LNCS） |

## 13. MEDICC2 官方程式碼位置（Kaufmann et al., Genome Biol 2022，10.1186/s13059-022-02794-9）

| 項目 | 內容 |
|---|---|
| 原描述 | README 待核：「MEDICC2 的官方 repo 位置不確定」。W3：「GitHub `schwarzlab-ccb/medicc2` 只有 10 stars，可能是 mirror；Bitbucket 未查證」 |
| 核對後描述 | 論文 Availability 段寫的官方位置是 **Bitbucket：https://bitbucket.org/schwarzlab/medicc2**（GPLv3），同時發布在 Bioconda，並有 Zenodo 存檔。PyPI（medicc2 1.1.2）的 homepage 也指向 Bitbucket。<br>GitHub 的 `schwarzlab-ccb/medicc2` 仍在維護（最近 push 為 2026-10-14），README 是官方內容，CI badge 指向 `ICCB-Cologne/medicc2`，而 GitHub API 對這個名稱回 “Moved Permanently”，應是組織改名後的轉址。結論：**論文指定的官方 repo 是 Bitbucket**；GitHub `schwarzlab-ccb/medicc2` 是同一團隊的現行 repo，不是第三方 mirror。這一點是分析推論，依據是 README 內容與 CI 轉址。<br>實作：Python 3＋OpenFST（核心 C++，Cython）。 |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9661799/ —「Availability of data and materials」：“MEDICC2 is implemented in Python 3 and freely available under GPLv3 on Bitbucket (https://bitbucket.org/schwarzlab/medicc2) [74] and in the Bioconda repository”。PyPI `https://pypi.org/pypi/medicc2/json`（Homepage＝Bitbucket）。`https://api.github.com/repos/schwarzlab-ccb/medicc2` |
| 狀態 | **corrected**（從「不確定」改為「Bitbucket schwarzlab/medicc2，GitHub schwarzlab-ccb/medicc2 為同團隊現行 repo」） |

## 14. PACTION 與 Canopy2 的官方程式碼

| 項目 | 內容 |
|---|---|
| 原描述 | README 待核：「Canopy2、PACTION 沒有找到 repo」。W5：「PACTION 未查到 repo（raphael-group/paction 回 404）」 |
| 核對後描述 | **PACTION**：官方程式碼在 **https://github.com/elkebir-group/paction**（El-Kebir lab，不是 Raphael lab），HTTP 200。方法本身用 MILP，整合「現有方法已推出的」SNV clone 與 CNA clone 及其 proportion；也可以把 ancestral 關係一起放進來。正文 Conclusion：“integrating SNV and CNA clones inferred using existing methods”。這符合 README 把它歸為「邊界」的理由。<br>**Canopy2**：官方 R package 在 **https://github.com/annweideman/canopy2**，HTTP 200；推論是 MCMC，資料是 bulk DNA＋scRNA 的 SNV。 |
| 證據 | PACTION：https://pmc.ncbi.nlm.nih.gov/articles/PMC8919608/ —「Availability of data and materials」：“PACTION is available at https://github.com/elkebir-group/paction”；Abstract Results：“mixed integer linear programming formulation”。Canopy2：https://pmc.ncbi.nlm.nih.gov/articles/PMC12904911/ —「Data and Code Availability」→「R Package」：“The Canopy2 package is an open source R package available at https://github.com/annweideman/canopy2” |
| 狀態 | **corrected**（兩者都有官方 repo） |

## 15. Dentro et al. 2021 Cell（PCAWG ITH，10.1016/j.cell.2021.03.009）

| 項目 | 內容 |
|---|---|
| 原描述 | W5：「多個 subclonal reconstruction 方法的 ensemble 與 consensus（方法數約 11 個，待核）｜沿用 SMC-Het 類的 metric 在模擬上驗證 consensus（待核）」。README 正文沒有收這篇 |
| 核對後描述 | **方法數**：**11 個 subclonal reconstruction 方法**：BayClone-C、Ccube、CliP、cloneHD、CTPsingle、DPClust、PhylogicNDT、PhyloWGS、PyClone、Sclust、SVclone。另有 **6 個 CN caller**（ABSOLUTE、ACEseq、Battenberg、cloneHD、JaBbA、Sclust）做 consensus CN 與 purity。consensus 方法有 3 個：Caesar（CSR）、Chic（CICC）、WeMe（WM，weighted median）。另外設計了 3 個 random baseline：stick breaking、informed、single cluster。<br>**評估指標**：**不是**照搬 SMC-Het 的 metric。作者說 rand index、mutual information 等 assignment-based 指標在這裡不實用，因此**自行設計 3 個指標**：<br>　(1) CFC：relative clonal fraction change<br>　(2) NCD：relative number of clusters difference（刻意偏好低估）<br>　(3) 以 purity 正規化的 CP RMSE<br>三者都 rescale 到 0–1，再用 normalized rank 合成總分。真實 PCAWG 資料沒有 ground truth，改用方法間的 pairwise similarity（normalized difference over average）。驗證用兩套獨立模擬資料。<br>**範圍**：這些指標只評估 clustering／subclonal architecture，也就是 cluster 數、各 cluster 的 SNV 數與 CP，**不評估 tree topology**。 |
| 證據 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8054914/ — Summary：“builds consensus CNAs from 6 methods and subclonal reconstruction from 11 methods”。STAR Methods「Subclonal architecture Methods」的 11 個子段落。「Consensus approaches」（Caesar／Chic／Weme）。「Three random methods」。「Evaluation metrics」→「Performance on simulated data」：“we designed three metrics specifically for this study… Relative clonal fraction change… Relative Number of clusters difference… Root mean square error”。「Similarity in real data」 |
| 狀態 | **corrected**：方法數 11 confirmed；metric 從「沿用 SMC-Het 類」改為「自訂 CFC／NCD／RMSE＋normalized rank，不評 topology」 |

---

## 附：其他順手核到的點

- **COMPASS 的 CN 輸入**：CN 從 Tapestri 的 amplicon read depth 加 allelic imbalance 一起推，不需要外部 CN。region 以 gene 為單位，CN 解析度很粗。
- **ConDoR 與 SCARLET 的差異**（README 第 216 行把兩者並列為「CN 約束 SNV loss」）：SCARLET 需要 CN profile 與 CN tree；ConDoR 只需要 CN clustering。把它們升級成 haplotype 層級約束時，兩者的輸入需求不同。
- **CalicoST 的 phasing**：CalicoST 的建樹訊號只有 LOH，與「haplotype-specific CN 推樹」並不完全一樣。README「haplotype-specific CN 推樹已有」那段把 CalicoST 和 MEDICC2、CNETML 並列，需加註：CalicoST 的 tree 只用 LOH 的有無（二元、不可逆），不使用 CN 數值。
