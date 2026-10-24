# W1：bulk SNV（可含 CN）clone tree／mutation tree 重建方法

面向：bulk sequencing（single-sample、multi-region 或 longitudinal）以 SNV 為主、可含 CN 的 clone tree／mutation tree 推論方法，也就是 PhyClone 的直接同類與競品。
查詢日：2026-10-16。DOI 都經 Crossref API（`api.crossref.org/works/<DOI>`）或出版頁／PMC／bioRxiv 頁核對過標題、第一作者、年份與期刊。GitHub stars 用 GitHub API 查（查詢日 2026-10-16）。
內容描述以摘要／方法段為依據；我自己的推論標「推論」。

## 搜尋紀錄

- `PhyClone accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing Bioinformatics`
- `"PhyClone" Roth 2025 Bioinformatics doi cancer phylogenies bulk sequencing forest structured Chinese restaurant process`
- `Orchard building large cancer phylogenies stochastic combinatorial search Kulman`
- `Pairtree Wintersinger reconstructing complex cancer evolutionary histories Blood Cancer Discovery doi`
- `CONIPHER Grigoriadis Nature Protocols 2024 tree building multi-region`
- `CALDER Myers longitudinal cancer phylogeny Cell Systems 2019 doi`
- `PICTograph Zheng Bayesian tumor phylogeny copy number multi-sample doi`
- `PICTograph karchinlab clone trees multi-region published Bioinformatics Advances 2023`
- `"PICTograph" Karchin cancer cell fractions clone trees uncertainty journal publication`
- `PICTograph Bioinformatics Advances "Lai" OR "Zheng" Karchin multi-region clone tree uncertainty Bayesian 2022`
- `Sapling inferring and summarizing tumor phylogenies bulk data backbone trees`
- `"Inferring and summarizing tumor phylogenies from bulk DNA data" Algorithms for Molecular Biology 2025 Qi El-Kebir`
- `tumor clone tree reconstruction bulk sequencing copy number aware multiplicity new method 2025`（extended）
- `bulk multi-sample tumor phylogeny inference method bioRxiv 2025 2026 clone tree new algorithm SNV`（extended）
- `RECOMB 2025 OR ISMB 2025 tumor phylogeny bulk DNA sequencing clone tree inference copy number loss Dollo`（extended）
- `Bayesian clone tree inference bulk WGS whole-genome doubling mutation multiplicity phylogeny method 2024 2025 2026`（extended）
- `TuELiP tumor evolution lineage integer programming bulk sequencing clone tree`
- `DEVOLUTION phylogenetic reconstruction multi-region bulk Andersson Bioinformatics 2021`
- `PACTION parsimonious clone tree reconciliation SNV copy number Sashittal`
- `longitudinal tumor samples clone tree inference method 2023 2024 bulk sequencing temporal constraints`
- `longitudinal ctDNA clonal evolution tree reconstruction method serial samples phylogeny 2024 2025 Bioinformatics`
- `CITUP2 mixed-integer quadratic program tree topology clone prevalences 2026`
- `TUSV-ext clonal lineage trees SNV CNA SV Bioinformatics 2022 btac253 Fu Xu`
- `DeCiFer simultaneous inference of mutation clustering descendant cell fraction copy number Satas Cell Systems 2021`
- `BAMSE Bayesian model selection tumor phylogeny bulk Toosi Bioinformatics`
- `TRaIT Ramazzotti learning mutational graphs of individual tumour evolution bulk single-cell 2019`
- `SubMARine Sundermann PLOS Computational Biology 2021 subclonal reconstruction copy number lineage relationships`
- `MIPUP minimum perfect unmixed phylogenies Husić Bioinformatics 2019 doi`
- `PhylEx clonal phylogeny bulk DNA single-cell RNA Jun Bouchard-Côté Bioinformatics 2023`
- `Canopy2 tumor phylogeny inference bulk DNA single-cell RNA published journal 2025`
- `MyClone BMC Bioinformatics 2025 clonal population structures tree inference`
- `clone tree inference bulk sequencing mutation loss k-Dollo variant allele frequency method 2023 2024`
- `deep learning OR reinforcement learning OR transformer tumor clone tree reconstruction bulk variant allele frequency 2024 2025`
- PubMed：`tumor phylogeny bulk sequencing clone tree method`（2023–2026 filter）；`PICTograph`
- Crossref：`query.bibliographic=Parsimonious Clone Tree Integration in cancer Sashittal`；`query.bibliographic=PICTograph clone trees Zheng Karchin Scharpf`
- WebFetch：PhyClone 的 OUP 頁與 bioRxiv 頁、Orchard／fastBE／PhylEx 的 PMC 頁、PICTograph 的 OUP 頁、Arborist／PICTographPlus／Enumerating clonal trees 的 bioRxiv 頁、Sapling 的 Crossref 紀錄

## 主選候選

| 方法名 | 論文標題 | 第一作者 et al. | 年份 | 期刊/preprint | DOI(連結) | 輸入資料 | 輸出樹類型 | 模型與推論 | 是否處理 CN／multiplicity／WGD | 程式碼(URL, stars) | 驗證狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PhyClone | PhyClone: accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing | Hurtado et al.（Bouchard-Côté, Roth） | 2025 | Bioinformatics 41(7):btaf344；preprint bioRxiv 10.1101/2024.08.14.607069 | [10.1093/bioinformatics/btaf344](https://doi.org/10.1093/bioinformatics/btaf344) | bulk；SNV allele counts + CN + tumour content；single 或 multi-sample | clone tree（clone 數由模型推論；node 上掛 SNV 集合） | Bayesian nonparametric（forest-structured CRP prior）+ Particle Gibbs（內嵌 SMC）+ SPR／SNV 重新指派 moves；clonal prevalence 以 DP 積分掉 | 是：沿用 PyClone 的 CN／purity 校正 likelihood；有 outlier 機率來吸收 mutation loss；**不處理 subclonal CN**（論文自述限制）；WGD 沒有獨立模型（推論） | [Roth-Lab/PhyClone](https://github.com/Roth-Lab/PhyClone)，9★ | verified |
| Pairtree | Reconstructing Complex Cancer Evolutionary Histories from Multiple Bulk DNA Samples Using Pairtree | Wintersinger et al.（Morris） | 2022 | Blood Cancer Discovery 3(3):208–219；preprint bioRxiv 10.1101/2020.11.06.372219 | [10.1158/2643-3230.BCD-21-0092](https://doi.org/10.1158/2643-3230.BCD-21-0092) | bulk；SNV VAF（含 variant read probability）；multi-sample（可達 100 samples） | clone tree（posterior 樣本） | 先算 pairwise relation tensor（Pairs Tensor），再用 MCMC 抽 clone tree；ISA | 部分：用每個 SNV 每個 sample 的 variant read probability 做 CN 校正（需外部給定）；不推論 multiplicity／WGD | [morrislab/pairtree](https://github.com/morrislab/pairtree)，44★ | verified |
| Orchard | Orchard: Building large cancer phylogenies using stochastic combinatorial search | Kulman et al.（Kuang, Morris） | 2024 | PLOS Comput Biol 20(12):e1012653；preprint arXiv 2311.12917 | [10.1371/journal.pcbi.1012653](https://doi.org/10.1371/journal.pcbi.1012653) | bulk；SNV VAF；multi-sample | mutation tree／clone tree（mixed sample perfect phylogeny） | 對 tree posterior 的 factorized 近似做 stochastic beam search，以 Gumbel 技巧無放回抽樣；一次加一個 mutation；ISA | 部分：variant read probability 可依 sample 變動以吸收 CNA；建議 CN 不可靠時剔除受 CNA 影響的 mutation | [morrislab/orchard](https://github.com/morrislab/orchard)，6★ | verified |
| CONIPHER | CONIPHER: a computational framework for scalable phylogenetic reconstruction with error correction | Grigoriadis et al.（McGranahan, Swanton, Zaccaria） | 2023（online）／2024（卷期 19:159–183） | Nature Protocols | [10.1038/s41596-023-00913-9](https://doi.org/10.1038/s41596-023-00913-9) | bulk；SNV + CN（clone-level CCF）；multi-region（TRACERx421 WES） | clone tree（含多個 alternative trees） | combinatorial：clustering → 列舉合理 ancestral relation → 建樹；剔除造成 cycle、違反 pigeonhole 和 crossing rule 的 clone | 是：明確處理 CNA 與 mutation error（以 CN 校正 CCF）；WGD 經 CCF 前處理間接處理（推論） | [McGranahanLab/CONIPHER](https://github.com/McGranahanLab/CONIPHER)，27★ | verified |
| CALDER | CALDER: Inferring Phylogenetic Trees from Longitudinal Tumor Samples | Myers et al.（Satas, Raphael） | 2019 | Cell Systems 8(6):514–522；preprint bioRxiv 10.1101/526814 | [10.1016/j.cels.2019.05.010](https://doi.org/10.1016/j.cels.2019.05.010) | bulk；SNV frequency；longitudinal multi-sample | clone tree（加上 longitudinal 約束） | 組合最佳化（MILP），在 sum condition 外加入取樣時間順序約束；ISA | 主要假設 copy-neutral SNV，不推論 multiplicity（推論，摘要沒有提到 CN 模型） | [raphael-group/calder](https://github.com/raphael-group/calder)，15★ | verified |
| PICTograph | Estimation of cancer cell fractions and clone trees from multi-region sequencing of tumors | Zheng et al.（Niknafs, Wood, Karchin, Scharpf） | 2022 | Bioinformatics 38(15):3677–3683；preprint bioRxiv 10.1101/2021.06.12.448194 | [10.1093/bioinformatics/btac367](https://doi.org/10.1093/bioinformatics/btac367) | bulk；SNV + 外部給定的 CN、multiplicity、purity；multi-region | clone tree ensemble（多個同分 tree 合成邊權重圖） | Bayesian hierarchical model（JAGS MCMC）估 CCF 與 cluster，依 sample presence 分組；Gabow–Myers 列舉 spanning tree；用 sum condition 過濾；SCHISM fitness 打分 | 部分：multiplicity、CN、purity 都是**輸入**，誤差不會傳進 posterior | [KarchinLab/pictograph](https://github.com/KarchinLab/pictograph)，5★ | verified |
| fastBE | A regression based approach to phylogenetic reconstruction from multi-sample bulk DNA sequencing of tumors | Schmidt et al.（Raphael） | 2024 | PLOS Comput Biol 20(12):e1012631 | [10.1371/journal.pcbi.1012631](https://doi.org/10.1371/journal.pcbi.1012631) | bulk；SNV frequency；multi-sample（可到數百 samples、約 1000 clones） | clone tree | 固定 tree 時解 structured regression（O(mnd)，比 LP 快）+ tree space 搜尋；perfect phylogeny／ISA；附 phylogeny-constrained clustering | 否：只用 copy-neutral 區域的 SNV；CN 列為 future work | [raphael-group/fastBE](https://github.com/raphael-group/fastBE)，6★ | verified |
| Sapling | Inferring and summarizing tumor phylogenies from bulk DNA data | Qi et al.（Schmidt, El-Kebir） | 2026 | Algorithms for Molecular Biology 21:5；conference 版 WABI 2024（LIPIcs 312, 10.4230/LIPIcs.WABI.2024.7）；preprint bioRxiv 10.1101/2024.04.10.588891 | [10.1186/s13015-025-00295-5](https://doi.org/10.1186/s13015-025-00295-5) | bulk；SNV read counts；multi-sample | 少量 backbone trees（mutation 子集）+ 擴展成 full clone tree | combinatorial heuristic（Backbone Tree Inference/Expansion from Reads，兩者都證明 NP-hard）+ greedy expansion；ISA | 否：作者承認 copy-number loss 會違反 ISA；靠 clustering 前處理 | elkebir-group/Sapling（0★；repo 名稱是我依 lab 命名推測後用 API 查到的，論文正文中的 URL 未逐字核對） | verified（論文）；code URL 部分驗證 |
| TUSV-ext | Reconstructing tumor clonal lineage trees incorporating single-nucleotide variants, copy number alterations and structural variations | Fu et al.（Schwartz） | 2022 | Bioinformatics 38(Suppl 1):i125–i133（ISMB 2022） | [10.1093/bioinformatics/btac253](https://doi.org/10.1093/bioinformatics/btac253) | bulk；SNV + allele-specific CNA + SV breakpoints；multi-sample | clonal lineage tree（含 CN profile） | deconvolution 與 Dollo-type parsimony phylogeny（ILP／coordinate descent 是依原版 TUSV 框架的推論，正文未逐字核對） | 是：allele-specific CN 與 SNV、SV 一起放進樹；SNV 可以因 CN loss 而消失（Dollo 型） | [CMUSchwartzLab/TUSV-ext](https://github.com/CMUSchwartzLab/TUSV-ext)，21★ | verified |
| DEVOLUTION | DEVOLUTION—A method for phylogenetic reconstruction of aneuploid cancers based on multiregional genotyping data | Andersson et al. | 2021 | Communications Biology 4:1103 | [10.1038/s42003-021-02637-6](https://doi.org/10.1038/s42003-021-02637-6) | bulk；SNV + CNA（需先有每個事件的 mutated clone fraction）；multi-region | event／clone phylogeny | 先做 subclonal deconvolution，再做 phylogeny（parsimony 類；細節以正文為準） | 是：專門針對 aneuploid、CNA 多但 SNV 少的腫瘤；可只用 CN | [NatalieKAndersson/DEVOLUTION](https://github.com/NatalieKAndersson/DEVOLUTION)，6★ | verified |
| SubMARine | Reconstructing tumor evolutionary histories and clone trees in polynomial-time with SubMARine | Sundermann et al.（Morris 等） | 2021 | PLOS Comput Biol 17(1):e1008400；preprint bioRxiv 10.1101/2020.06.11.146100 | [10.1371/journal.pcbi.1008400](https://doi.org/10.1371/journal.pcbi.1008400) | bulk；已 cluster 的 subclone frequencies；可加 subclonal CNA；multi-sample | partial clone tree／MAR（Maximally-Constrained Ancestral Reconstruction），可再列舉 clone trees | polynomial-time 組合演算法（ISA、sum rule 等 lineage constraints） | 是：延伸版用 equivalence constraints 處理 subclonal CNA | [morrislab/submarine](https://github.com/morrislab/submarine)，8★ | verified |
| BAMSE | BAMSE: Bayesian model selection for tumor phylogeny inference among multiple samples | Toosi et al.（Hajirasouliha） | 2019 | BMC Bioinformatics 20(Suppl 11):282 | [10.1186/s12859-019-2824-3](https://doi.org/10.1186/s12859-019-2824-3) | bulk；SNV read counts；multi-sample | clone tree（ranked） | Bayesian model selection：先為 clustering 打分，再為每個 clustering 生成 lineage trees，用 posterior 排序；ISA | 否（摘要沒有 CN 模型；推論） | [HoseinT/BAMSE](https://github.com/HoseinT/BAMSE)，1★ | verified |
| TRaIT | Learning mutational graphs of individual tumour evolution from single-cell and multi-region sequencing data | Ramazzotti et al.（Caravagna） | 2019 | BMC Bioinformatics 20:210；preprint arXiv 1709.01076 | [10.1186/s12859-019-2795-4](https://doi.org/10.1186/s12859-019-2795-4) | bulk multi-region 或 single-cell；binary mutation presence（可含多種 alteration） | mutational graph／mutation tree（可以是 DAG 或 forest） | Suppes probabilistic causation + 最大似然／information-theoretic 結構學習（TRONCO 框架） | 否：用 binarized presence，不模型 CN 或 multiplicity | 位於 [BIMIB-DISCo/TRONCO](https://github.com/BIMIB-DISCo/TRONCO)，30★（另有 BIMIB-DISCo/TRaIT 1★） | verified |

### 各篇重點

**PhyClone（2025）**
- 核心創新：用 FS-CRP prior 把 SNV clustering 和 tree topology 放進同一個模型；clonal prevalence 被積分掉，所以推論只需在 tree space 上走。用 Particle Gibbs 搭配 SMC 由下而上建樹，再加 outlier 機制吸收 mutation loss。
- 主要假設：ISA（outlier 機制是一種軟性放寬）；CN 為外部給定、clonal、每個 SNV 一組 CN；不處理 subclonal CN。
- 和本研究的關聯：本研究的基線。long-read phasing 最直接的切入點是 PyClone 式 emission 中的 multiplicity／CN 狀態設定（推論），以及把「同一 read 上兩個 SNV 共現」當成 pairwise ancestry 證據加進 SMC proposal 或 likelihood（推論）。

**Pairtree（2022）**
- 核心創新：用 pairwise relation（ancestor、descendant、branched、cocluster、garbage）的 posterior 張量約束 tree MCMC，能擴展到約 30 個以上 subclone、100 個 sample。
- 主要假設：ISA；CN 透過 variant read probability 外部給定。
- 和 long-read 的關聯：pairwise relation 是 phasing 證據最自然的接口。同一 read 上兩個 SNV 的共現或互斥，可以直接改寫 pairwise posterior（推論）。

**Orchard（2024）**
- 核心創新：把 tree posterior 分解成「逐一加入 mutation」的條件分布，用 stochastic beam search 無放回抽樣，能處理最多 1000 個 mutation。這是 PhyClone 之外另一個逐步建樹（sequential construction）的路線。
- 主要假設：ISA、mixed sample perfect phylogeny；CN 由 variant read probability 吸收。
- 和 PhyClone 的關聯：兩者都是 sequential、一次加一個節點的 tree 建構。比較 Orchard 的 beam／Gumbel 抽樣與 PhyClone 的 SMC，可以找出 proposal 改進方向（推論）。

**CONIPHER（2023/2024）**
- 核心創新：TRACERx 實務流程的公開版，把 clustering、錯誤 cluster 修正（cycle、pigeonhole、crossing rule）與建樹整合在一起，能擴展到大量 sample 和 clone。
- 主要假設：ISA 搭配規則式錯誤修正；CCF 經 CN 校正。
- 關聯：是 ALPACA（Nature 2025）的上游，代表臨床 multi-region WES 的標準做法；其 pigeonhole／crossing rule 可以當 PhyClone 結果的 sanity check（推論）。

**CALDER（2019）**
- 核心創新：首次把 longitudinal 取樣順序寫成 tree 約束（clone 出現的時間不能早於祖先），可以減少 bulk 解空間的歧義。
- 主要假設：ISA、sum condition。
- 關聯：本研究的 `tX_nY` 是 purity 梯度而不是時間序列，不能直接套用；但「外部順序資訊 → 約束 topology」這個框架和「phasing 推出的 SNV/CN timing → 約束 topology」是同一類想法（推論）。

**PICTograph（2022）**
- 核心創新：以 sample presence 分組後才做 clustering，並把同分的多棵樹畫成 ensemble，表示 topology 的不確定性。
- 主要假設：ISA、sum condition（有容許誤差）；multiplicity／CN／purity 都視為已知。
- 關聯：把 multiplicity 當外部輸入，正好凸顯 multiplicity 誤差無法傳遞的問題。phasing 可以讓 multiplicity 輸入更可靠（推論）。2026 年 Karchin lab 推出後續 PICTographPlus（見近似與排除）。

**fastBE（2024）**
- 核心創新：固定 tree 時的 frequency regression 有 O(mnd) 演算法，並能在 tree 變動後快速更新，所以可擴展到數百個 sample、上千個 clone。
- 主要假設：perfect phylogeny；只用 copy-neutral SNV。
- 關聯：是 bulk 方法的 scalability 上限參考；CN-aware 擴展留給 future work，這正是本研究可以補的缺口（推論）。

**Sapling（WABI 2024 → AMB 2026）**
- 核心創新：bulk 解空間通常很大，因此改推一小組 backbone trees 來摘要整個解空間，再擴展成 full tree。
- 主要假設：ISA；作者承認 CN loss 會違反 ISA。
- 關聯：和 PhyClone 的 consensus／topology-report 是同一類問題（如何摘要 posterior）。phasing 若能縮小解空間，可以用 backbone 數量下降來量化效益（推論）。

**TUSV-ext（2022）**
- 核心創新：在同一個 deconvolution + phylogeny 框架中放進 SNV、allele-specific CNA 和 SV。
- 主要假設：Dollo 型 parsimony（允許 loss），使用 ILP。
- 關聯：是少數在 bulk 端同時建模 allele-specific CN 與 SNV 的建樹方法。haplotype-specific CN（例如 longphase 加上 HP 分離的 depth）可直接成為它的輸入型態（推論）。

**DEVOLUTION（2021）**
- 核心創新：針對 CNA 多、SNV 少的 aneuploid（例如兒童）腫瘤，把 CN 事件和 SNV 一起當 phylogenetic marker。
- 主要假設：每個事件的 clone fraction 已知；parsimony 類建樹。
- 關聯：提醒我們在 SNV 稀少的情況下，CN 事件本身就是 topology 的主要訊號；細胞株（例如 HCC1395）CN 複雜，可以參考（推論）。

**SubMARine（2021）**
- 核心創新：不給單一 tree，而是給所有 equally-good tree 共有的 partial ancestry（MAR），並延伸到 subclonal CNA。
- 主要假設：ISA、sum rule、CN equivalence constraints。
- 關聯：可以拿 PhyClone posterior 中確定的關係和 SubMARine 的 subMAR 做比較；phasing 證據也可表示成額外的 partial ancestry constraint（推論）。

**BAMSE（2019）**
- 核心創新：先為 clustering 打分、再為 lineage tree 打分的兩段式 Bayesian model selection，把 subclone 數的 prior 和演化過程放進 posterior。
- 主要假設：ISA；沒有 CN 模型。
- 關聯：方法較輕量，可以當小規模 benchmark 的競品。

**TRaIT（2019）**
- 核心創新：同一個統計框架同時處理 multi-region bulk 和 single-cell，輸出 mutational graph。
- 主要假設：binary presence、probabilistic causation；不用 VAF 做 deconvolution。
- 關聯：和 PhyClone 的 VAF-based 路線差異大，偏低解析度的基線（推論）。

## 經典基線（不計主選）

| 方法 | 論文 | 年份／期刊 | DOI | 要點 |
|---|---|---|---|---|
| PhyloWGS | Deshwar et al., PhyloWGS: Reconstructing subclonal composition and evolution from whole-genome sequencing of tumors | 2015, Genome Biology | [10.1186/s13059-015-0602-8](https://doi.org/10.1186/s13059-015-0602-8) | TSSB + MCMC；SNV + CN；[morrislab/phylowgs](https://github.com/morrislab/phylowgs) 113★ |
| Canopy | Jiang et al., Assessing intratumor heterogeneity and tracking longitudinal and spatial clonal evolutionary history by NGS | 2016, PNAS | [10.1073/pnas.1522203113](https://doi.org/10.1073/pnas.1522203113) | 同時用 SNV 與 allele-specific CNA 建 tree，MCMC；[yuchaojiang/Canopy](https://github.com/yuchaojiang/Canopy) 71★ |
| LICHeE | Popic et al., Fast and scalable inference of multi-sample cancer lineages | 2015, Genome Biology | [10.1186/s13059-015-0647-8](https://doi.org/10.1186/s13059-015-0647-8) | evolutionary constraint network + spanning tree；[viq854/lichee](https://github.com/viq854/lichee) 35★ |
| CITUP | Malikic et al., Clonality inference in multiple tumor samples using phylogeny | 2015, Bioinformatics | [10.1093/bioinformatics/btv003](https://doi.org/10.1093/bioinformatics/btv003) | 列舉 tree topology + quadratic integer programming |
| AncesTree | El-Kebir et al., Reconstruction of clonal trees and tumor composition from multi-sample sequencing data | 2015, Bioinformatics | [10.1093/bioinformatics/btv261](https://doi.org/10.1093/bioinformatics/btv261) | VAF factorization、ILP、perfect phylogeny mixture |
| SPRUCE | El-Kebir et al., Inferring the Mutational History of a Tumor Using Multi-state Perfect Phylogeny Mixtures | 2016, Cell Systems | [10.1016/j.cels.2016.07.004](https://doi.org/10.1016/j.cels.2016.07.004) | 把 SNV 和 CN 視為 multi-state character，CN-aware 的 perfect phylogeny |
| Treeomics | Reiter et al., Reconstructing metastatic seeding patterns of human cancers | 2017, Nature Communications | [10.1038/ncomms14114](https://doi.org/10.1038/ncomms14114) | Bayesian presence/absence + ILP 建 multi-region phylogeny |
| ClonEvol | Dang et al., ClonEvol: clonal ordering and visualization in cancer sequencing | 2017, Annals of Oncology | [10.1093/annonc/mdx517](https://doi.org/10.1093/annonc/mdx517) | 給定 clustering，再列舉 consistent tree |
| MIPUP | Husić et al., MIPUP: minimum perfect unmixed phylogenies for multi-sampled tumors via branchings and ILP | 2018 online／2019 卷期, Bioinformatics 35(5) | [10.1093/bioinformatics/bty683](https://doi.org/10.1093/bioinformatics/bty683) | min perfect phylogeny via branchings + ILP；online 日期是 2018，所以放在基線 |

## 近似與排除

| 方法 | DOI | 排除／降級原因 |
|---|---|---|
| ALPACA（Pawlik et al., Nature 2025） | [10.1038/s41586-025-09398-w](https://doi.org/10.1038/s41586-025-09398-w) | 給定 SNV tree（CONIPHER）後推 clone-level allele-specific CN，不推 topology。 |
| DeCiFer（Satas et al., Cell Systems 2021） | [10.1016/j.cels.2021.07.006](https://doi.org/10.1016/j.cels.2021.07.006) | 提出 descendant cell fraction，同時選 multiplicity 並做 clustering，但輸出是 cluster，不輸出 topology。對 CN-aware multiplicity 非常相關，**建議協調者當方法參考**。 |
| PACTION（Sashittal et al., AMB 2022；WABI 2021） | [10.1186/s13015-022-00209-9](https://doi.org/10.1186/s13015-022-00209-9) | 輸入是已推得的 SNV clone 與 CNA clone（及其 tree），用 MILP 整合成一棵 tree。屬於 tree integration／reconciliation，不是從 read 重建；列為近似。 |
| Arborist（Weber et al., bioRxiv 2026） | [10.64898/2026.02.26.707773](https://doi.org/10.64898/2026.02.26.707773) | 只用 low-pass scDNA 為 bulk 推得的候選 tree 排序（variational lower bound），不從頭建 topology。 |
| TuELiP（Guang et al., Bioinformatics 2023） | 經 PMC10311318 查到（PMC 頁顯示為 btad230）；DOI 未經 Crossref 逐一核對 → unverified | consensus tree（weighted ILP），輸入是多棵已推得的 tree。 |
| PICTographPlus（Lai et al., bioRxiv 2026） | [10.64898/2026.01.15.699695](https://doi.org/10.64898/2026.01.15.699695) | 主要貢獻是把 DNA clone tree 和 bulk RNA-seq 結合、解出 clone-specific expression；建樹部分延續 PICTograph（GitHub 寫的是 1-Dollo、SSM + CNA）。不計主選，但值得注意它把 CNA 也放進樹。 |
| CITUP2（AACR 2026 abstract 6905） | 無 DOI → unverified | 只有會議摘要（MIQP 同時解 topology 與 prevalence，用 DCF 當輸入），沒有正式論文或程式碼。 |
| MyClone（BMC Bioinformatics 2025） | [10.1186/s12859-025-06252-8](https://doi.org/10.1186/s12859-025-06252-8) | clonal composition／clustering（CN-corrected CCF），不推 tree。 |
| PyClone-VI | — | 只做 clustering（依 common.md 規則排除）。 |
| PhylEx（Jun et al., Nat Commun 2023） | [10.1038/s41467-023-36202-y](https://doi.org/10.1038/s41467-023-36202-y) | 確實會推 topology（TSSB + slice sampling，bulk SNV + major/minor CN + scRNA），但核心是 bulk + scRNA 整合，屬多模態面向；建議交給 bulk+sc 的 worker。和 Roth lab 有作者重疊。 |
| Canopy2（Weideman et al., Stat Biosci 2025） | [10.1007/s12561-024-09466-1](https://doi.org/10.1007/s12561-024-09466-1) | bulk DNA + scRNA 的 Bayesian MCMC tree，同屬多模態面向。 |
| TUSV-int（PMC12571511, 2025） | DOI 未核對 → unverified | bulk DNA + scRNA 的 ILP 版 TUSV，同屬多模態面向。 |
| Mase-phi（ctDNA marker selection, PMC12002908） | DOI 未核對 | 用 tree posterior 挑 ctDNA marker，主要貢獻不是建樹。 |
| Enumerating and Exploring the Space of Clonal Trees（Bernstein et al., bioRxiv 2025） | [10.1101/2025.07.18.664776](https://doi.org/10.1101/2025.07.18.664776) | tree space 列舉與 simulation 方法學，不是推論方法；可以當 benchmark 設計參考。 |
| CloMu（Genome Research 2023, RL） | 未核對 → unverified | 跨病人學 mutation 演化傾向，用來從候選 tree 中挑選，不是單一腫瘤的建樹方法。 |
| MEDICC2、CNT-MD 等 CN-only phylogeny | — | 屬 CN／event phylogeny 面向，不在本 worker 範圍。 |
| HATCHet2、PyClone-VI、BnpC | — | CN calling 或只做 clustering，依規則排除。 |

## 給協調者的建議

最該精讀的 5 篇：

1. **PhyClone（btaf344）**：基線本身。要精讀 emission（CN、purity、multiplicity 的處理方式）、outlier／loss 機制，以及論文自述「不處理 subclonal CN」的限制。這些是 long-read phasing 最直接的切入點。
2. **Pairtree（Blood Cancer Discov 2022）**：它的 pairwise relation tensor 是把「同一 read 上 SNV 共現」這類 phasing 證據接進 tree 推論最自然的接口，也是 PhyClone 論文的主要 benchmark 對手。
3. **Orchard（PLOS CB 2024）**：和 PhyClone 一樣是 sequential、逐一加 mutation 的建構路線，但用 beam／Gumbel 抽樣，可擴展到 1000 個 mutation。可借鏡它改進 PhyClone SMC 的 proposal 和 scalability。
4. **DeCiFer（Cell Systems 2021；雖然排除為主選）＋ TUSV-ext（Bioinformatics 2022）**：bulk 端在 CN-aware multiplicity 和 mutation loss（DCF）、allele-specific CN 和 SNV 共同建樹上最完整的兩個模型。要設計「phasing 約束 multiplicity／CNV timing」時，這兩篇是必讀參照。
5. **Sapling（AMB 2026）或 SubMARine（PLOS CB 2021）**：都在處理 bulk 解空間不唯一的問題。要量化「加入 phasing 後解空間縮小多少」時，可以用它們的 backbone／MAR 指標當評估框架。

### 不確定之處

- Sapling 的 code repo 是 `elkebir-group/Sapling`（GitHub API 回傳存在、0★），但我沒有逐字比對論文中寫的 URL。
- CALDER、BAMSE 的 CN 處理是依摘要推論，沒有讀正文。DEVOLUTION 的建樹演算法細節（parsimony 類）沒有讀正文確認。
- CONIPHER 的 Crossref 年份是 2023（online），卷期是 2024；UCL Discovery 頁回 403，正文細節來自搜尋摘要。
- TuELiP、TUSV-int、CloMu、Mase-phi 的 DOI 沒有用 Crossref 核對（它們都在排除清單，不影響主選）。
- 2025–2026 年新的**純 bulk SNV 建樹**方法搜到的不多（主要是 PhyClone、Sapling 期刊版、fastBE、Orchard），沒有搜到 RECOMB／ISMB 2025–2026 的新純 bulk clone tree 方法；可能是搜尋涵蓋不足，建議協調者用 proceedings 目錄再補查一次。
- 沒有找到任何一個 bulk 方法使用 long-read haplotype／read-level SNV 共現來建 clone tree，這個缺口和本研究方向一致。
