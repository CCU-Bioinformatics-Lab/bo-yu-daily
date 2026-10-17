# W5：整合多種資料的推樹方法 ＋ Benchmark／Review

> Worker W5，查詢日 2026-10-16。範圍是整合型（bulk+single-cell、多樣本／時序／空間、SNV+CN+SV、deep learning／generative）的 tumor tree 推論方法，以及 2019–2026 的 benchmark、評估與 review。
> 驗證方式：每篇的 DOI、標題、第一作者、年份、期刊都用 Crossref API（`api.crossref.org/works/<DOI>`）核對過，部分再用 Europe PMC、PMC 或出版頁交叉確認。GitHub stars 是用已登入的 `gh api repos/<repo>` 在 2026-10-16 查的。
> 內容描述以摘要為主。標「推論」的是我的推斷；標「待核」的是我憑印象補充、摘要沒有寫到的細節，還要讀全文確認。

---

## 搜尋紀錄

**Crossref `query.bibliographic`（腳本是暫存的 `cr.py`／`ab.py`）**
- `SCARLET single-cell tumor phylogeny copy-number constrained mutation losses`
- `TUSV-ext reconstructing tumor evolutionary histories SNV CNA SV`、`TUSV-ext structural variants tumor clonal lineage`、`Sc-TUSV-ext single-cell clonal lineage SNV CNA SV`
- `PICTograph multi-sample tumor evolution copy number`、`PICTograph resolving uncertainty clonal evolution multi-sample tumor sequencing`、`Estimation of cancer cell fractions and clone trees from multi-region sequencing of tumors`
- `CALDER longitudinal tumor phylogeny`、`CALDER inferring phylogenetic trees from longitudinal tumor samples`
- `ConDoR constrained Dollo tumor phylogeny copy number single-cell`
- `Pharming joint clonal tree SNV CNA single-cell`
- `Phertilizer low-coverage single-cell tumor phylogeny`
- `BiTSC2 Bayesian tumor clonal tree single-cell SNV CNA`
- `CalicoST allele-specific copy number spatial transcriptomics phylogeography`
- `Tumoroscope spatial clones bulk`、`Tumoroscope probabilistic model mapping cancer clones tumor tissues`
- `CONIPHER tumor phylogeny reconstruction protocol`
- `generative flow network tumor phylogeny`、`deep learning tumor phylogeny inference neural network clone tree`、`variational inference tumor clonal tree single-cell copy number VICTree`
- `Canopy2 tumor phylogeny inference bulk DNA single-cell RNA`
- `Deriving longitudinal tumor phylogenies from single-cell sequencing data`、`LACE longitudinal analysis cancer evolution single-cell`、`Inferring phylogenetic trees of cancer evolution from longitudinal single-cell copy number profiles`
- `CloMu modeling predicting cancer clonal evolution reinforcement learning`
- `PhylEx clonal tree single-cell transcriptomics bulk`
- `PACTION parsimonious clone tree integration SNV CNA`
- `Metient metastasis polyclonal seeding`
- `Evaluation of simulation methods for tumor subclonal reconstruction`
- `benchmarking single-cell tumor phylogeny inference methods`、`systematic benchmark of single-cell mutation tree inference methods`、`benchmark copy number phylogeny methods single-cell simulation comparison MEDICC2 Lazac`、`simulation framework benchmarking tumor phylogeny inference methods`
- `Power and pitfalls of computational methods for inferring clone phylogenies and mutation orders from bulk sequencing`
- `Distance measures for tumor evolutionary trees`、`Triplet-based similarity score for fully multilabeled trees with poly-occurring labels`
- `Parameter, noise, and tree topology effects in tumor phylogeny inference`
- `Characterizing genetic intra-tumor heterogeneity across 2,658 human cancer genomes`
- `Computational strategies in tumor phylogenetics evaluating multimodal integration`
- 經典基線：Canopy、SPRUCE、MACHINA、TUSV、ddClone

**WebSearch**
- `deep learning OR transformer OR reinforcement learning tumor phylogeny clone tree inference 2024 2025`
- `"tumor" phylogeny "generative" OR "GFlowNet" OR "diffusion" OR "neural" mutation tree single-cell bioRxiv 2025 2026 inference topology`
- `"clonal tree" OR "tumor phylogeny" "neural network" OR "variational autoencoder" OR "graph neural network" OR "language model" inference single-cell bulk bioRxiv 2025`
- `spatial transcriptomics tumor clone phylogeny inference method copy number tree topology 2024 2025 (CalicoST OR SpaceTree OR Clonalscope OR "phylogeography")`
- `method infer tumor phylogeny incorporating spatial location of samples multi-region "spatial" clone tree algorithm migration`
- `benchmark single-cell tumor phylogeny inference methods comparison SCITE SiFit SPhyR SCIPhI evaluation 2022 2023 2024`
- `independent benchmarking study cell lineage tree inference single-cell DNA tumor methods SCITE SiFit SCIPhIN infSCITE CellPhy accuracy comparison`
- `review "tumor phylogenetics" OR "cancer phylogenetics" methods 2022 2023 2024 Annual Review OR Nature Reviews Genetics ...`
- `PICTograph tumor evolution multi-sample Bayesian copy number Bioinformatics Advances Zheng Scharpf`
- `Metient metastasis migration histories clone tree Koyyalagunta Nature Cancer 2025 doi`

**WebFetch／Europe PMC（讀摘要或方法段）**
- PMC12596152（Jiang 2025 review＋benchmark）、PMC11764021（Lu 2024 CN phylogeny review）
- PMC6956735（Salcedo 2020 SMC-Het metrics）、PMC7044161（Miura 2020）、PMC9780082（Pairtree benchmark）
- Europe PMC REST：Salcedo 2020、Miura 2020、Wintersinger 2022、Dentro 2021 的摘要

---

## 主選候選

主選 15 篇，依整合類型分組排列。

| 方法名 | 論文標題 | 第一作者 et al. | 年份 | 期刊/preprint | DOI(連結) | 輸入資料 | 輸出樹類型 | 模型與推論 | 是否處理 CN／multiplicity／WGD | 程式碼(URL, stars) | 驗證狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **B-SCITE** | Integrative inference of subclonal tumour evolution from single-cell and bulk sequencing data | Malikic et al. | 2019 | Nature Communications | [10.1038/s41467-019-10737-5](https://doi.org/10.1038/s41467-019-10737-5) | bulk＋scDNA；SNV；bulk 可以是 multi-sample（待核） | mutation tree（cell attach 到樹上） | Bayesian＋MCMC（從 SCITE 擴充，likelihood 再加上 bulk VAF） | 不顯式建模 CN；摘要說 bulk VAF 受 CN 影響時結果仍穩健 | [smalikic/B-SCITE](https://github.com/smalikic/B-SCITE)，10★ | verified |
| **PhISCS** | PhISCS: a combinatorial approach for subperfect tumor phylogeny reconstruction via integrative use of single-cell and bulk sequencing data | Malikic et al. | 2019 | Genome Research | [10.1101/gr.234435.118](https://doi.org/10.1101/gr.234435.118) | scDNA＋（可選）bulk；SNV | mutation tree／sub-perfect phylogeny | combinatorial：ILP 與 Boolean CSP | 不建模 CN；可以「刪除」違反 ISA 的 mutation（摘要把原因歸到 LOH、deletion 或 CN 估錯） | [sfu-compbio/PhISCS](https://github.com/sfu-compbio/PhISCS)，11★ | verified |
| **PhylEx** | Reconstructing clonal tree for phylo-phenotypic characterization of cancer using single-cell transcriptomics | Jun et al. | 2023 | Nature Communications（preprint 10.1101/2021.02.16.431009） | [10.1038/s41467-023-36202-y](https://doi.org/10.1038/s41467-023-36202-y) | bulk DNA＋scRNA；SNV（scRNA 上 mutation 的共現） | clone tree | Bayesian（推論：TSSB 類 nonparametric＋MCMC，待核） | bulk 部分應該會讀 CN 輸入（推論，待核） | [junseonghwan/PhylEx](https://github.com/junseonghwan/PhylEx)，3★ | verified |
| **Canopy2** | Canopy2: Tumor Phylogeny Inference by Bulk DNA and Single-Cell RNA Sequencing | Weideman et al. | 2025（線上 2025-01） | Statistics in Biosciences（preprint 10.1101/2024.03.18.585595） | [10.1007/s12561-024-09466-1](https://doi.org/10.1007/s12561-024-09466-1) | bulk DNA＋scRNA；SNV | clone tree＋cell assignment | Bayesian＋MCMC（binomial／beta-binomial mixture；把 scRNA 的 0 分成三種來源） | 摘要沒有提 CN | 未找到官方 repo | verified |
| **TUSV-int** | Deconvolution and phylogeny inference of diverse variant types integrating bulk DNA-seq with single-cell RNA-seq | Bristy et al. | 2025 | Bioinformatics Advances 5(1):vbaf234（preprint 10.1101/2025.01.24.634791） | [10.1093/bioadv/vbaf234](https://doi.org/10.1093/bioadv/vbaf234) | bulk DNA＋scRNA；SNV＋CNA＋SV | clonal lineage tree | ILP（deconvolution 與 phylogeny 一起解） | 有，處理 CNA | [CMUSchwartzLab/TUSV-int](https://github.com/CMUSchwartzLab/TUSV-int)，3★ | verified |
| **TUSV-ext** | Reconstructing tumor clonal lineage trees incorporating single-nucleotide variants, copy number alterations and structural variations | Fu et al. | 2022 | Bioinformatics（ISMB） | [10.1093/bioinformatics/btac253](https://doi.org/10.1093/bioinformatics/btac253) | bulk；multi-sample；SNV＋CNA＋SV | clonal lineage tree | ILP＋coordinate descent（從 TUSV 延伸，待核） | 有，CNA 是 tree 上的事件 | [CMUSchwartzLab/TUSV-ext](https://github.com/CMUSchwartzLab/TUSV-ext)，21★ | verified |
| **Sc-TUSV-ext** | Sc-TUSV-Ext: Single-Cell Clonal Lineage Inference from Single Nucleotide Variants, Copy Number Alterations, and Structural Variants | Bristy et al. | 2025 | J. Comput. Biol.（preprint 10.1101/2023.12.07.570724） | [10.1089/cmb.2024.0613](https://doi.org/10.1089/cmb.2024.0613) | scDNA；SNV＋CNA＋SV | clonal lineage tree | ILP | 有 | [CMUSchwartzLab/Sc-TUSV-ext](https://github.com/CMUSchwartzLab/Sc-TUSV-ext)，3★ | verified |
| **PACTION** | Parsimonious Clone Tree Integration in cancer | Sashittal et al. | 2022 | Algorithms for Molecular Biology | [10.1186/s13015-022-00209-9](https://doi.org/10.1186/s13015-022-00209-9) | bulk multi-sample；先各自推出的 SNV clone tree 與 CNA clone tree，加上兩邊的 proportion | 整合後的 joint SNV＋CNA clone tree | MILP | 有，CNA clone 是輸入 | 未查到 repo（raphael-group/paction 回 404） | verified |
| **SCARLET** | SCARLET: Single-Cell Tumor Phylogeny Inference with Copy-Number Constrained Mutation Losses | Satas et al. | 2020 | Cell Systems（RECOMB 2020；preprint 10.1101/840355） | [10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001) | scDNA；SNV read counts＋CN clone 資訊 | cell/mutation tree | loss-supported model（ISA 與 Dollo 的推廣）＋probabilistic error/ADO model；演算法是 combinatorial（待核） | 有：只有 CN 下降的位點才允許 mutation loss | [raphael-group/scarlet](https://github.com/raphael-group/scarlet)，8★ | verified |
| **ConDoR** | ConDoR: tumor phylogeny inference with a copy-number constrained mutation loss model | Sashittal et al. | 2023 | Genome Biology（preprint 10.1101/2023.01.05.522408） | [10.1186/s13059-023-03106-5](https://doi.org/10.1186/s13059-023-03106-5) | targeted scDNA；SNV＋cell cluster（CN） | constrained k-Dollo phylogeny | combinatorial（MILP，待核） | 有：SNV loss 受 cell cluster 約束 | [raphael-group/ConDoR](https://github.com/raphael-group/ConDoR)，9★ | verified |
| **COMPASS** | COMPASS: joint copy number and mutation phylogeny reconstruction from amplicon single-cell sequencing data | Sollier et al. | 2023 | Nature Communications | [10.1038/s41467-023-40378-8](https://doi.org/10.1038/s41467-023-40378-8) | targeted (amplicon) scDNA；SNV＋CNA（含 CNLOH，待核） | joint SNV＋CNA tree | Bayesian＋MCMC（待核） | 有 | [cbg-ethz/COMPASS](https://github.com/cbg-ethz/COMPASS)，26★ | verified |
| **BiTSC²** | BiTSC2: Bayesian inference of tumor clonal tree by joint analysis of single-cell SNV and CNA data | Chen et al. | 2022 | Briefings in Bioinformatics | [10.1093/bib/bbac092](https://doi.org/10.1093/bib/bbac092) | scDNA raw reads；SNV＋CNA | subclonal tree＋cell assignment | Bayesian＋MCMC | 有：同時估 scCNA 與 scSNV genotype，處理兩者重疊 | [ucasdp/BiTSC2](https://github.com/ucasdp/BiTSC2)，6★ | verified |
| **Pharming** | Pharming: Joint Clonal Tree Reconstruction of SNV and CNA Evolution from Single-Cell DNA Sequencing of Tumors | Weber et al. | 2025 | RECOMB 2025，LNCS（preprint 10.1101/2024.11.17.623950） | [10.1007/978-3-031-90252-9_25](https://doi.org/10.1007/978-3-031-90252-9_25) | low-pass scWGS；SNV＋CNA | joint SNV＋CNA clonal tree | combinatorial／likelihood search（細節待核） | 有，核心是 SNV 與 CNA 在同區域共現 | [elkebir-group/pharming](https://github.com/elkebir-group/pharming)，2★ | verified |
| **CALDER** | CALDER: Inferring Phylogenetic Trees from Longitudinal Tumor Samples | Myers et al. | 2019 | Cell Systems（preprint 10.1101/526814） | [10.1016/j.cels.2019.05.010](https://doi.org/10.1016/j.cels.2019.05.010) | bulk；longitudinal multi-sample；SNV | clone tree（longitudinal phylogeny） | ILP（longitudinal constraint，待核） | 不建模 CN | [raphael-group/calder](https://github.com/raphael-group/calder)，15★ | verified |
| **CalicoST** | Inferring allele-specific copy number aberrations and tumor phylogeography from spatially resolved transcriptomics | Ma et al. | 2024 | Nature Methods（preprint 10.1101/2024.03.09.584244） | [10.1038/s41592-024-02438-9](https://doi.org/10.1038/s41592-024-02438-9) | spatial transcriptomics（Visium）；allele-specific CNA（以 germline SNP 的 BAF 為基礎）；多 slice | clone phylogeny＋phylogeography（2D 或 3D 空間） | HMM（沿 genome）＋HMRF（跨 spot），之後重建 clone tree（建樹演算法待核） | 有：allele-specific CN，包含 CN-LOH 與 mirrored subclonal CNA | [raphael-group/CalicoST](https://github.com/raphael-group/CalicoST)，51★ | verified |

### 各篇重點

**B-SCITE（2019）**
- 創新：這是第一個用 single-cell 加 bulk 推 tumor tree 的方法。SCITE 的 cell genotype likelihood 和 bulk VAF 的 likelihood 在同一個 MCMC 裡合併。
- 假設：infinite sites（ISA）、perfect phylogeny。
- 與本研究的關聯（推論）：B-SCITE 的作法是兩種資料各自給一份 likelihood，再加總後做 MCMC。PhyClone 若要加入「long-read 上多 SNV 共現」這類新的 likelihood 項，可以照這個寫法。long read 上 SNV 的共現可視為「極局部的 single-cell 觀測」：同一條 read 來自同一個細胞的同一個 haplotype。

**PhISCS（2019）**
- 創新：提出 sub-perfect phylogeny，可以明確刪除少數違反 ISA 的 mutation。bulk VAF 被寫成 lineage constraint（sum condition）。
- 假設：ISA，但允許有限度違反。
- 關聯（推論）：PhISCS 把 bulk VAF 寫成硬性的 sum/lineage constraint。phasing 得到的 pairwise SNV 關係（例如同一 read 上 co-occur 就代表 ancestral 或同 clone，cis 上互斥就代表 branching）也可以用同樣方式表達。
- 後續的 PhISCS-BnB 只吃 single-cell，列在「近似與排除」。

**PhylEx（2023）**
- 創新：bulk DNA 決定 clone 結構，scRNA 上 mutation 的共現提供 branching 資訊，結果可以把 clone 對應到 expression phenotype。
- 假設：推論是 ISA 加上 nonparametric tree prior。
- 關聯：PhylEx 用 scRNA 的 read 共現資訊補 bulk，long-read 共現的角色跟它非常接近。這篇最值得拿來做 likelihood 設計的對照。

**Canopy2（2025）**
- 創新：明確區分 scRNA 的三種 0：細胞沒有 mutation、bursting 造成的 stochastic 0、技術上漏測。
- 假設：clone tree 加上 ISA（推論）。
- 關聯：long read 上「沒看到 alt」也有好幾種原因：在另一個 haplotype、coverage 不夠、或真的不存在。這種「區分 0 的來源」的建模方式可以借用（推論）。

**TUSV-int（2025）**
- 創新：在同一個 ILP 裡用 bulk DNA 和 scRNA 做 deconvolution 並建樹，同時納入 SNV、CNA、SV。
- 假設：mutation 在樹上的出現有 parsimony 式的限制（待核）。
- 關聯：這是目前看到整合型態最多的一個，可當作「多變異型態加多資料源」的上限參考。

**TUSV-ext（2022）**
- 創新：在 bulk multi-sample 框架裡把 SNV、CNA、SV 一起放到 clonal lineage tree 上。
- 假設：每個 SNV 和 SV breakpoint 只出現一次（推論，屬 ISA 類）。CN 透過 tree 上的事件解釋。
- 關聯：PhyClone 也處理 bulk SNV 加 CN，TUSV-ext 是最直接的 ILP 對照。long-read 本來就擅長 SV 偵測（例如 Severus），未來加 SV 時可以參考它的 SV-breakpoint 與 CN 的 coupling 方式（推論）。

**Sc-TUSV-ext（2025）**
- 創新：把 TUSV-ext 的 SNV、CNA、SV 聯合模型搬到 scDNA。
- 假設：與 TUSV-ext 類似（推論）。
- 關聯：與本研究只有間接關係，主要用來確認「SV 進入 tree」在 single-cell 上也走得通。

**PACTION（2022）**
- 創新：先分別推出 SNV clone tree 和 CNA clone tree，再用 MILP 合併成一棵 joint tree，並考慮兩邊 proportion 的不確定性。
- 假設：parsimony（clone 數最少）。
- 關聯（推論）：這篇對本研究很重要。我們可以先用 longphase 加 haplotype-specific CN 得到 allele-specific CNA 的 clone 結構，再和 PhyClone 的 SNV tree 用 PACTION 的方式整合，作為「不改 PhyClone 內部」的 baseline。

**SCARLET（2020）**
- 創新：提出 loss-supported model，只有 CN 有下降證據的位點才允許 SNV loss。這比 Dollo 或 finite-sites 更受限、也更合理。
- 假設：ISA 的推廣。
- 關聯（推論）：這個概念可以直接搬到 long read。HP-specific CN 能指出到底是哪一條 haplotype 掉了，所以 loss 可以進一步限制在「SNV 所在的同一條 haplotype」。這對 PhyClone 的 multiplicity 與 genotype 設定是很強的先驗。

**ConDoR（2023）**
- 創新：提出 constrained k-Dollo，SNV 的 loss 只能發生在 CN cluster 的邊界上。
- 假設：k-Dollo。
- 關聯：與 SCARLET 是同一條路線，可以看作 SCARLET 的離散化版本。

**COMPASS（2023）**
- 創新：針對 targeted scDNA（例如 Tapestri）同時推 SNV 與 CNA 的 phylogeny，並在 123 位 AML 病人上應用。
- 假設：推論是 SNV 遵守 ISA，同時允許 CNA 事件或 LOH。
- 關聯：它用 allelic imbalance 偵測 CNLOH，這和 haplotype-aware CN 有關，可參考它的 tree-level 事件建模。

**BiTSC²（2022）**
- 創新：直接吃 scDNA raw reads，聯合估計 scCNA genotype、scSNV genotype、clone 與 tree。
- 假設：推論是 tree 上的 SNV 遵守 ISA。
- 關聯：這是 SNV 與 CN 重疊處 likelihood 的 single-cell 版本，可以跟 PhyClone 的 genotype prior 對照。

**Pharming（2025）**
- 創新：先用比較準的 low-pass scWGS CNA tree 當骨架，再利用「SNV 與 CNA 在同一區段共現」把 SNV 放上去，同時得到兩種事件的順序。
- 關聯（推論）：這篇在概念上最接近本研究的主軸。長 read 可以直接觀察到 SNV 與 haplotype、CN 事件的關係，例如「SNV 在被放大的那條 haplotype 上」，因此能幫 CNV timing 與 multiplicity 定錨。值得精讀。

**CALDER（2019）**
- 創新：把「樣本的時間順序」寫成 longitudinal phylogeny 的 constraint，例如 clone 在第一次出現前不可能存在。結果顯示這能大幅減少 multi-sample bulk 的歧義。
- 假設：ISA、perfect phylogeny mixture。
- 關聯：PhyClone 支援 multi-sample，但不使用時間資訊。如果本研究的不同 purity 或時間點樣本能提供順序約束，可以參考 CALDER。我們的 `tX_nY` 是 subsample dilution，**不是時序**，所以不能直接套用。

**CalicoST（2024）**
- 創新：從 spatial transcriptomics 推 allele-specific CNA，包括 total CN 看不到的 CN-LOH 與 mirrored subclonal CNA，再重建空間上的 clone phylogeny。
- 假設：clone 的邊界具空間連續性（HMRF）。
- 關聯（推論）：它的核心是用 germline SNP 的 phasing 加上 BAF 找出 mirrored subclonal CNA。這和 longphase HP1/HP2 加 allele-specific CN 是同一種訊號。它對 phasing 和 BAF 的處理可以借用，用來偵測 haplotype 層級的 subclonal CNA。

---

### Deep learning／generative 型 tumor tree 推論（2023–2026）：沒有可列入主選的論文

我查了 GNN、VAE、GFlowNet、diffusion、transformer、RL 等關鍵字，**沒有找到任何以 neural/generative model 直接推論單一病人 tumor tree topology、並已正式發表的方法**。找到的相關工作都放在「近似與排除」，原因分別寫在各列：
- Sadeqi Azer 2020 iScience：把 topology 分成 linear 或 branching 的分類器，而且是 2020 年。
- CloMu 2023 Genome Research：跨病人的 evolution model，用來在候選樹中挑選。
- CPhyT-GNN 2026 Bioinformatics Advances：tree embedding。
- VICTree 2024 preprint：variational inference，但只用 scDNA CN，應由 CN worker 負責。
- PhyloGFN：通用 phylogenetics，不是 tumor 專用。

結論（推論）：在 2023–2026 年，「deep learning tumor tree inference」大多停留在 downstream 分析、表示學習或通用 phylogenetics，還沒有成熟的 topology 推論方法。

---

## 經典基線（不計主選）

| 方法 | 標題（簡） | 第一作者 | 年份 | 期刊 | DOI | 整合類型 |
|---|---|---|---|---|---|---|
| Canopy | Assessing intratumor heterogeneity and tracking longitudinal and spatial clonal evolutionary history by NGS | Jiang | 2016 | PNAS | [10.1073/pnas.1522203113](https://doi.org/10.1073/pnas.1522203113) | bulk SNV＋allele-specific CNA、multi-sample、Bayesian MCMC |
| SPRUCE | Inferring the Mutational History of a Tumor Using Multi-state Perfect Phylogeny Mixtures | El-Kebir | 2016 | Cell Systems | [10.1016/j.cels.2016.07.004](https://doi.org/10.1016/j.cels.2016.07.004) | bulk SNV＋CNA，multi-state perfect phylogeny |
| MACHINA | Inferring parsimonious migration histories for metastatic cancers | El-Kebir | 2018 | Nature Genetics | [10.1038/s41588-018-0106-z](https://doi.org/10.1038/s41588-018-0106-z) | 多部位樣本，同時推 clone tree 與 migration（PMH-TI） |
| TUSV | Deconvolution and phylogeny inference of structural variations in tumor genomic samples | Eaton | 2018 | Bioinformatics | [10.1093/bioinformatics/bty270](https://doi.org/10.1093/bioinformatics/bty270) | bulk SV＋CNA，ILP |
| ddClone | Joint statistical inference of clonal populations from single cell and bulk tumour sequencing data | Salehi | 2017 | Genome Biology | [10.1186/s13059-017-1169-3](https://doi.org/10.1186/s13059-017-1169-3) | bulk＋sc，偏 clonal population／genotype 推論，不輸出 topology（推論） |

---

## 近似與排除

| 方法 | DOI | 排除或降級原因 |
|---|---|---|
| PhISCS-BnB（Sadeqi Azer 2020, Bioinformatics） | [10.1093/bioinformatics/btaa464](https://doi.org/10.1093/bioinformatics/btaa464) | 能推 topology，但只用 single-cell，不屬於「整合」，交給 scDNA worker（W2）。程式碼在 [algo-cancer/PhISCS-BnB](https://github.com/algo-cancer/PhISCS-BnB)，10★。 |
| Conifer（Baghaarabani 2021, BMC Bioinformatics） | [10.1186/s12859-021-04338-7](https://doi.org/10.1186/s12859-021-04338-7) | 是 bulk＋sc 整合、也推 topology，但概念與 B-SCITE、PhISCS 重疊，影響力較低。為了「寧缺勿濫」降為備選。程式碼在 [LeilaBagha/Conifer](https://github.com/LeilaBagha/Conifer)，3★。 |
| Phyllochron（Jakatdar 2025, bioRxiv） | [10.1101/2025.08.06.668977](https://doi.org/10.1101/2025.08.06.668977) | 用 longitudinal perfect phylogeny 加上 MILP，從多時點 scDNA 推 topology。它符合時序整合，但還是 preprint，而且只用 single-cell，所以列為備選。程式碼在 [raphael-group/phyllochron](https://github.com/raphael-group/phyllochron)，2★。 |
| PICTograph（Zheng 2022, Bioinformatics） | [10.1093/bioinformatics/btac367](https://doi.org/10.1093/bioinformatics/btac367) | multi-region bulk SNV，Bayesian CCF 加上 Gabow-Myers 枚舉樹，會推 topology。它屬於純 bulk SNV multi-sample，交給 W1。程式碼在 [KarchinLab/pictograph](https://github.com/KarchinLab/pictograph)，5★。 |
| CONIPHER（Grigoriadis 2023, Nature Protocols） | [10.1038/s41596-023-00913-9](https://doi.org/10.1038/s41596-023-00913-9) | multi-region bulk SNV 加上 CN-aware clustering 與 error correction，屬於 bulk 主線，交給 W1。程式碼在 [McGranahanLab/CONIPHER](https://github.com/McGranahanLab/CONIPHER)，27★。 |
| Metient（Koyyalagunta et al., preprint 2024；正式版期刊未能確認） | [10.1101/2024.07.09.602790](https://doi.org/10.1101/2024.07.09.602790) | 輸入是**未標記的 clone tree**，在給定的樹上推 migration history，不推 tumor topology。程式碼在 [morrislab/metient](https://github.com/morrislab/metient)，13★。 |
| Tumoroscope（Shafighi, bioRxiv 2022） | [10.1101/2022.09.22.508914](https://doi.org/10.1101/2022.09.22.508914) | 把既有的 clone 對應到空間 spot 上，只做 deconvolution 與 mapping，不推 topology。正式版期刊沒有在 Crossref 查到。 |
| STARCH（bioRxiv 2020） | [10.1101/2020.07.13.188813](https://doi.org/10.1101/2020.07.13.188813) | 從 spatial transcriptomics 推 CN 與 clone，只做 clone 推論，不推 tree。 |
| CloMu（Ivanovic & El-Kebir 2023, Genome Research） | [10.1101/gr.277672.123](https://doi.org/10.1101/gr.277672.123) | 用 RL 訓練的 neural network 做跨病人的 tree generative model，用途是預測 trajectory 與 **tree selection**（從候選樹中挑選），不從原始資料推 topology。程式碼在 [elkebir-group/CloMu](https://github.com/elkebir-group/CloMu)，7★。 |
| Tumor Phylogeny Topology Inference via Deep Learning（Sadeqi Azer 2020, iScience） | [10.1016/j.isci.2020.101655](https://doi.org/10.1016/j.isci.2020.101655) | 用 deep learning 分類 topology（linear 或 branching），不輸出完整的樹，而且不在 2023–2026 範圍內。 |
| CPhyT-GNN（Bioinformatics Advances 2026, vbag016） | DOI 沒有用 Crossref 核對，`unverified`（出版頁：academic.oup.com/bioinformaticsadvances/article/6/1/vbag016） | 對已有的 tumor tree 做 GNN embedding，屬於 downstream。 |
| VICTree（Melin, bioRxiv 2024） | [10.1101/2024.02.14.580312](https://doi.org/10.1101/2024.02.14.580312) | 用 variational inference 推 clonal tree，但只吃 scDNA CN，屬於 CN worker（W3）的範圍。 |
| Inferring Phylogenetic Trees … Longitudinal Single-Cell Copy Number Profiles（Liu 2025, LNCS） | [10.1007/978-3-031-94928-9_2](https://doi.org/10.1007/978-3-031-94928-9_2) | 時序整合，但只用 CN，交給 W3。 |
| LACE（Ramazzotti 2022, J. Comput. Sci.） | [10.1016/j.jocs.2021.101523](https://doi.org/10.1016/j.jocs.2021.101523) | 多時點 sc 的 longitudinal 模型，只用 single-cell SNV，交給 W2。我沒有細看它是否輸出 topology。 |
| Exploring the Space of Tumor Phylogenies Consistent with scWGS（Khan 2026, bioRxiv） | [10.64898/2026.01.21.700922](https://doi.org/10.64898/2026.01.21.700922) | 只看過標題，屬於 sc 範圍，交給 W2 或 W3。 |

---

## Benchmark 與 Review

| 標題 | 作者 | 年份 | 期刊 | DOI | 比較的方法 | 評估指標 | 主要結論 |
|---|---|---|---|---|---|---|---|
| A community effort to create standards for evaluating tumor subclonal reconstruction（**SMC-Het／DREAM 的 metric 框架**） | Salcedo, Tarabichi, … Boutros | 2020 | Nature Biotechnology | [10.1038/s41587-019-0364-z](https://doi.org/10.1038/s41587-019-0364-z) | 共 580 個 reconstruction 組合：PhyloWGS、DPClust 搭配多種 SNV caller（MuTect、SomaticSniper、Strelka、MutationSeq、perfect calls），CN 用 Battenberg，深度 8–128×；另外做了 4,250 組 CNA 錯誤注入 | **SC1A** purity：1−\|ρ−c\|。**SC1B** clone 數：[L−d+1]/(L+1)。**SC1C** CCF 與每個 lineage 的 mutation 數：earth-mover 類分數。**SC2A/2B** SNV 分群：co-clustering matrix 的 AUPR 與 AJSD 平均。**SC3A/3B** 祖先關係：把 CCM、**ADM（ancestor-descendant matrix）**、ADMᵀ、CM 疊起來算 Pearson correlation。基礎 metric 有 MCC、PCC、AUPR、AJSD | 精確度隨有效深度上升，約 60× 以後趨平。SNV caller 的 sensitivity 影響最大。PhyloWGS 在 SC2B 較好、對 CNA 錯誤較穩健，DPClust 的 purity 估計較好。單一 metric 與專家判斷的一致性很低（約 0.12–0.14），所以要組合多個 metric |
| Characterizing genetic intra-tumor heterogeneity across 2,658 human cancer genomes（PCAWG ITH） | Dentro, Leshchiner, … | 2021 | Cell | [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) | 多個 subclonal reconstruction 方法的 ensemble 與 consensus（方法數約 11 個，待核） | 沿用 SMC-Het 類的 metric 在模擬上驗證 consensus（待核） | 95.1% 的 informative 樣本有 subclonal expansion，且 branching 很常見。主要價值是 consensus pipeline 與泛癌資源 |
| A practical guide to cancer subclonal reconstruction from DNA sequencing | Tarabichi et al. | 2021 | Nature Methods | [10.1038/s41592-020-01013-2](https://doi.org/10.1038/s41592-020-01013-2) | 實務指引型 review，沒有新的 benchmark（待核） | 整理 purity、CN、clustering、tree 各步驟的 QC 與常見錯誤（待核） | 可作為「從 CN 到 subclone 到 tree」標準流程的檢查清單 |
| Power and pitfalls of computational methods for inferring clone phylogenies and mutation orders from bulk sequencing data | Miura, … Kumar | 2020 | Scientific Reports | [10.1038/s41598-020-59006-2](https://doi.org/10.1038/s41598-020-59006-2) | CloneFinder、MACHINA、Treeomics、LICHeE、MixPhy、PhyloWGS、Cloe（multi-region bulk） | **MLTED**（multi-labeled tree edit distance）、**mutation ordering error rate**、**TreeVec**、**Robinson–Foulds** | 各方法差異很大，而且都難以找出樣本中真實存在的祖先 clone。CNA、多次 seeding、樣本間細胞混雜都會讓所有方法變差。整體以 CloneFinder、MACHINA、LICHeE 最好，但沒有一個方法在所有情境都好 |
| Parameter, noise, and tree topology effects in tumor phylogeny inference | Tomlinson, Oesper et al. | 2019 | BMC Medical Genomics | [10.1186/s12920-019-0626-0](https://doi.org/10.1186/s12920-019-0626-0) | 在 ISA 下枚舉所有一致的 phylogeny，比較多種枚舉或重建策略（multi-sample bulk SNV） | 重建 tree 與真實 tree 的一致性，以及 ISA 違反率（細節待核） | 有 noise 時 ISA 常常被違反，低 coverage 加高 noise 更難重建。**branching topology 比 linear 容易重建**。放寬 ISA 後仍能得到好的 phylogeny |
| Reconstructing Complex Cancer Evolutionary Histories from Multiple Bulk DNA Samples Using **Pairtree** | Wintersinger, … Morris | 2022 | Blood Cancer Discovery | [10.1158/2643-3230.BCD-21-0092](https://doi.org/10.1158/2643-3230.BCD-21-0092) | Pairtree、CALDER、PASTRI、CITUP、LICHeE、PhyloWGS；576 組模擬（3–100 subclones、1–100 samples）加上 14 例 B-ALL | **VAF reconstruction loss**：相對於 truth 或 expert tree，每個 mutation 平均 log-likelihood 的下降。**Relationship reconstruction error**：每對 subclone 的真實與推論 pairwise 關係（ancestor、descendant、branched、同 clone）之間的平均 JSD，範圍 0–1 bit。另有 success rate | 只有 Pairtree 跑完全部 576 組。樣本越多它越準，其他方法沒有這個趨勢。≤30 subclones 時表現最好。在真實資料上它的 fit 不輸 expert tree |
| Distance measures for tumor evolutionary trees（**CASet／DISC**） | DiNardo, … Oesper | 2020（online 2019-11） | Bioinformatics | [10.1093/bioinformatics/btz869](https://doi.org/10.1093/bioinformatics/btz869) | 方法論文：比較 CASet、DISC 與既有的 tree distance（parent-child、ancestor-descendant、MLTED 等） | **CASet**（Common Ancestor Set distance）、**DISC**（Distinctly Inherited Set Comparison） | 這兩個距離比既有 metric 更能分辨 subclonal inheritance pattern 的差異（stereodist 實作） |
| Triplet-based similarity score for fully multilabeled trees with poly-occurring labels（**MP3**） | Ciccolella, … Della Vedova | 2021（online 2020-07） | Bioinformatics | [10.1093/bioinformatics/btaa676](https://doi.org/10.1093/bioinformatics/btaa676) | 方法論文：MP3 與其他 tree similarity measure 比較 | **MP3**（triplet-based similarity），支援一個 node 有多個 mutation，也支援同一 mutation 多次出現（非 ISA） | 第一個能處理 poly-occurring label 的相似度。若樹允許 loss 或 recurrence（例如 SCARLET、ConDoR 類），應改用 MP3（[AlgoLab/mp3treesim](https://github.com/AlgoLab/mp3treesim)） |
| Computational strategies in tumor phylogenetics: evaluating multimodal integration and methodological trade-offs across study designs | Jiang, … Liang, Tao | 2025 | Bioinformatics Advances 5(1):vbaf242 | [10.1093/bioadv/vbaf242](https://doi.org/10.1093/bioadv/vbaf242) | 回顧 20 多種工具（cross-sectional、regional bulk、single-cell、lineage tracing）；benchmark 7 個：RETCHER、SciClone、PyClone、CITUP、ClonEvol、LICHeE、PICTograph（只用模擬資料：3、6、9 個 sample 乘 5、7、9 個 cluster，每組 20 份，200×，purity 0.9） | 正確 cluster 數比例、**正確 branch 比例**（正確推出的 branch 除以總 branch）、5 小時內完成的比例 | RETCHER（作者自家方法，有利益衝突）最好。複雜度提高時多數方法準確度下降。PICTograph 在 6 和 9 個 sample 時崩潰。multi-omics 整合有幫助，但 mutation ordering 與 polyclonal detection 仍是難點。**未納入 PhyClone、Pairtree** |
| Cancer phylogenetic inference using copy number alterations detected from DNA sequencing data | Lu (Bingxin) | 2025（online 2024-04） | Cancer Pathogenesis and Therapy 3(1):16–29 | [10.1016/j.cpt.2024.04.003](https://doi.org/10.1016/j.cpt.2024.04.003) | 系統性 review。CN-only：MEDICC2、CNT-ILP、Lazac、MEDALT、CNETML、NestedBD、Sitka、CONET、SCICoNE 等。CN+SNV：SCARLET、PhyloWGS、Canopy、Pairtree、CONIPHER、SPRUCE、BiTSC2、PACTION、COMPASS 等。CN+SV：TUSV、TUSV-ext、Sc-TUSV-ext 等 | 沒有自己的 benchmark | CN phylogeny 缺乏完整 benchmark。CN calling 的雜訊、ISA 違反、NP-hard 是主要挑戰。建議用多個方法交叉驗證 robustness |
| Assessing the merits: an opinion on the effectiveness of simulation techniques in tumor subclonal reconstruction | Lai et al. | 2024 | Bioinformatics Advances | [10.1093/bioadv/vbae094](https://doi.org/10.1093/bioadv/vbae094) | 評論 tumor 模擬工具，不是方法 benchmark | 無 | 沒有公認的 simulator 標準，是 benchmark 進展的主要障礙 |

**關於 single-cell tree 與 CN phylogeny 的獨立 benchmark**：我查了多次，**沒有找到中立的第三方 benchmark**。現有的比較幾乎都寫在方法論文自己的 benchmark 裡，例如 SCARLET、CellPhy、ScisTree2 的比較章節，因此有利益衝突。Lu 2024 的 review 也明說「comprehensive benchmark studies are still needed」。如果協調者需要，我可以再補 ScisTree2（Genome Research 2025）等方法論文裡的比較設定，但它們不算獨立 benchmark。

### 可供 `evaluation_v1.md` 參考的指標整理（推論）

| 層級 | 指標 | 出處 | 適用情境 |
|---|---|---|---|
| purity／clone 數 | SC1A：1−\|ρ−c\|；SC1B：clone 數分數 | Salcedo 2020 | nominal purity 和 PhyClone 推估 purity 的比較只能當 sanity check，因為 `tX_nY` 不是 ground truth |
| CCF | SC1C（earth-mover 類）；CCF 的 L1／RMSE | Salcedo 2020 | 跨 dilution 系列檢查 CCF 是否隨 nominal purity 的比例縮放 |
| mutation 分群 | co-clustering matrix 的 AUPR、AJSD、MCC | Salcedo 2020 | 與 golden cluster 比較 |
| 祖先關係 | **ADM 的 PCC**（SC3）；**Pairtree relationship error**（pairwise 四類關係的 JSD） | Salcedo 2020；Wintersinger 2022 | **最適合當主指標**，不依賴 clone 的編號，還可以用 long-read phasing 得到的 pairwise 證據做部分驗證（推論） |
| 資料 fit | VAF reconstruction loss | Wintersinger 2022 | 沒有 truth 時，比較「加 long-read 特徵前後」的 fit |
| tree 距離 | MLTED、CASet、DISC、RF、TreeVec | Miura 2020；DiNardo 2020 | 與 HCC1395 golden tree 比較 |
| 允許 loss 或 recurrence 的樹 | MP3 | Ciccolella 2021 | 引入 haplotype-specific loss 之後 |
| topology 類型 | linear 與 branching 的分層報告 | Tomlinson 2019 | linear tree 本來就比較難，要分開報告 |

---

## 給協調者的建議

最該精讀的 5 篇：

1. **Pharming（Weber 2025, RECOMB）**：它用「SNV 與 CNA 在同一區段共現」聯合推斷兩種事件的順序，與本研究「用 long-read 同 read 共現與 haplotype 定錨 multiplicity 和 CNV timing」最接近。它的 likelihood 與搜尋設計可以直接對照。
2. **SCARLET（Satas 2020）與 ConDoR（2023）**：兩篇都只允許「有 CN 下降證據」的 SNV loss。換成 long read 後，可以升級成只允許發生在同一條 haplotype 上的 loss。這是改 PhyClone genotype 與 multiplicity 先驗最直接的範本。
3. **PACTION（Sashittal 2022）**：它把獨立推出的 SNV tree 和 CNA tree 合併。我們可以用它做一個「PhyClone SNV tree 加上 longphase allele-specific CN tree」的整合 baseline，不必改 PhyClone 內部，成本最低。
4. **CalicoST（Ma 2024）**：它用 phased germline SNP 的 BAF 找出 mirrored subclonal CNA 與 CN-LOH，和 longphase 的 HP1/HP2 加 allele-specific CN 是同一種訊號，前處理與模型都可以借用。
5. **Benchmark 層面請精讀 Salcedo 2020 與 Wintersinger 2022（Pairtree）**：這兩篇定義了 ADM-PCC 和 pairwise relationship error。這類「不依賴 clone 編號的 pairwise 祖先關係」指標應該當成 `evaluation_v1.md` 的主指標，而且可以用 long-read phasing 的 pairwise 證據做部分驗證。

### 不確定之處
- PhylEx、COMPASS、ConDoR、Pharming、CalicoST 的推論演算法細節（MCMC、MILP、搜尋方式），以及 Dentro 2021 的方法數與 metric，都是憑印象補充、標了「待核」，摘要沒有寫。
- Bioinformatics Advances 第 5 卷（TUSV-int、Jiang review）在 Crossref 的 issued 日期顯示 2024-12-26，這是卷的起始日，實際刊出在 2025。我的表格寫 2025。
- Metient 的正式期刊版沒有核對到（PMC 有 2025 年的紀錄），所以只引用 bioRxiv DOI。CPhyT-GNN 的 DOI 沒有用 Crossref 核對，標 `unverified`。
- Canopy2 與 PACTION 沒有找到官方 GitHub repo。
- 沒有找到 2023–2026 年真正用 deep learning 或 generative model 推單一病人 tumor topology 的論文。這是我搜尋後的負面結論，不排除有漏掉的 preprint。
