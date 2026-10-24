# W2：single-cell DNA 以 SNV 為主的 mutation tree／cell lineage tree 重建方法

查詢日：2026-10-16。書目資訊（標題、第一作者、年份、期刊、DOI）都經 Crossref REST API（`api.crossref.org/works`）逐筆核對，DOI 皆由 Crossref 回傳，沒有自行拼湊。GitHub stars 透過 GitHub API／`gh api` 在 2026-10-16 查詢。
模型描述的依據：有標「摘要」的，來自 Crossref 收錄的摘要或 bioRxiv 摘要；Pharming 另讀了 bioRxiv 全文的方法段（WebFetch）。標「推論／記憶」的內容是我依過去對該論文的了解，本次沒有逐字核對全文，需要精讀確認。

## 搜尋紀錄

Crossref `query.bibliographic`：
- `SPhyR single-cell phylogeny loss`
- `PhISCS combinatorial single-cell bulk tumor phylogeny Malikic`
- `PhISCS-BnB branch and bound perfect phylogeny single-cell`
- `SCARLET copy number loss supported single-cell phylogeny Satas`
- `COMPASS joint copy number single-nucleotide variant targeted single-cell Sollier`
- `BiTSC2 Bayesian inference of tumor clonal tree single-cell SNV CNA`
- `CellPhy accurate fast probabilistic inference single-cell phylogenies`
- `ScisTree2 single cell phylogeny`、`ScisTree2 scalable cell lineage tree`
- `ScisTree maximum likelihood perfect phylogeny noisy single cell Wu`
- `ConDoR copy-number constrained mutation loss tumor phylogeny`
- `SiCloneFit Bayesian inference population structure genotype phylogeny tumor single-cell`
- `SCIPhIN single-cell mutation calling tree loss recurrence`
- `SCIPhI single-cell mutation identification phylogenetic inference Singer`
- `Phertilizer clonal trees ultra-low coverage single-cell DNA`
- `SIEVE joint inference single-cell phylogeny variant calling`、`DelSIEVE deletion single-cell phylogeny`
- `SASC Dollo-k simulated annealing single-cell cancer progression`
- `gpps ILP mutation losses single cell`
- `Phylovar phylogeny-aware variant calling single-cell`
- `PHALCON phylogeny-aware variant calling single-cell panel`
- `SCITE-RNA cell lineage tree single-cell RNA`、`SCITE Tree inference for single-cell data Jahn`
- `infSCITE recurrence loss mutational hits life histories tumors`
- `SiFit inferring tumor trees single-cell finite-sites`
- `SCsnvcna integrating SNVs CNAs phylogenetic tree single-cell`
- `Sc-TUSV-ext single-cell clonal lineage SNV CNA SV`
- `Pharming joint clonal tree SNV CNA single-cell`
- `Phyllochron longitudinal tumor phylogenies single-cell sequencing`
- `Exploring the space of tumor phylogenies consistent with single-cell whole-genome sequencing Khan`
- `doublet aware tumor phylogeny single-cell perfect phylogeny`、`SCITE doublets single-cell mutation history`
- `single-cell tumor phylogeny inference deep learning mutation matrix 2024`
- `cell lineage tree inference single-cell DNA mutation 2025 scalable`
- `Scelestial Steiner tree single-cell lineage tree inference`
- `doubletD doublet detection single-cell DNA Weber El-Kebir`
- `tumor phylogeny single-cell bulk integration 2024 perfect phylogeny`

WebSearch：
- `Tapestri single-cell DNA tumor phylogeny inference method 2024 2025 mutation tree allelic dropout`（extended）
- `new method 2025 2026 single-cell DNA sequencing tumor mutation tree reconstruction bioRxiv false negatives doublets loss`（extended）
- `SASC Ciccolella "Inferring cancer progression from Single-cell Sequencing while allowing mutation losses" Bioinformatics`
- `PHALCON phylogeny-aware variant calling single-cell panel Zafar published 2025 journal`
- `Phyllochron longitudinal perfect phylogeny Jakatdar Sashittal Raphael 2026`
- `SiCloneFit bitbucket hamimzafar siclonefit source code`

GitHub：`gh search repos` 查詢 `SiCloneFit`、`SCsnvcna`、`PHALCON`、`phylogeny-aware variant calling`、`SCOPE tumor phylogeny scWGS`、`Tapestri phylogeny`。

## 主選候選

| 方法名 | 論文標題 | 第一作者 et al. | 年份 | 期刊/preprint | DOI(連結) | 輸入資料 | 輸出樹類型 | 模型與推論 | 是否處理 CN／multiplicity／WGD | 程式碼(URL, stars) | 驗證狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PhISCS | PhISCS: a combinatorial approach for subperfect tumor phylogeny reconstruction via integrative use of single-cell and bulk sequencing data | Malikic et al. | 2019 | Genome Research 29(11)（preprint 10.1101/376996） | [10.1101/gr.234435.118](https://doi.org/10.1101/gr.234435.118) | single-cell SNV 二元矩陣（含 FP/FN/missing），可選 bulk VAF；multi-sample bulk | mutation tree（加修正後的 cell genotype matrix） | combinatorial：ILP 與 weighted Max-SAT（CSP） | 否（只允許少數 infinite-sites 違反，「sub-perfect」） | [sfu-compbio/PhISCS](https://github.com/sfu-compbio/PhISCS), 11 | verified |
| SiCloneFit | SiCloneFit: Bayesian inference of population structure, genotype, and phylogeny of tumor clones from single-cell genome sequencing data | Zafar et al. | 2019 | Genome Research 29(11)（preprint 10.1101/394262） | [10.1101/gr.243121.118](https://doi.org/10.1101/gr.243121.118) | single-cell SNV genotype（binary/ternary，含 FP/FN/missing、doublet） | clone tree（clone 的 genotype 與 cell assignment） | Bayesian nonparametric（DP clustering）＋finite-sites tree；MCMC（推論／記憶） | CN 否；允許 loss／recurrence（finite sites） | [bitbucket.org/hamimzafar/siclonefit](https://bitbucket.org/hamimzafar/siclonefit)（Bitbucket，回應 HTTP 200；無 stars） | verified |
| SCARLET | SCARLET: Single-Cell Tumor Phylogeny Inference with Copy-Number Constrained Mutation Losses | Satas et al. | 2020 | Cell Systems（preprint 10.1101/840355；RECOMB 2020 LNCS） | [10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001) | 同一批 cell 的 SNV read counts＋CN（copy-number tree／profile） | cell/clone phylogeny（loss-supported） | loss-supported model（介於 infinite sites 和 Dollo 之間）＋sequencing error 與 ADO 的機率模型 | 有：SNV loss 只能出現在 CN 下降的 locus；沒有 multiplicity 或 WGD | [raphael-group/scarlet](https://github.com/raphael-group/scarlet), 8 | verified |
| SASC | Inferring cancer progression from Single-Cell Sequencing while allowing mutation losses | Ciccolella et al. | 2021（線上 2020） | Bioinformatics 37(3):326–333（preprint 10.1101/268243） | [10.1093/bioinformatics/btaa722](https://doi.org/10.1093/bioinformatics/btaa722) | single-cell SNV 二元矩陣（FP/FN/missing） | mutation tree（含 loss 節點） | Dollo-k model＋simulated annealing（ML） | 不處理 CN；loss 不受 CN 約束 | [sciccolella/sasc](https://github.com/sciccolella/sasc), 3 | verified |
| CellPhy | CellPhy: accurate and fast probabilistic inference of single-cell phylogenies from scDNA-seq data | Kozlov et al. | 2022 | Genome Biology 23（preprint 10.1101/2020.07.31.230292） | [10.1186/s13059-021-02583-w](https://doi.org/10.1186/s13059-021-02583-w) | scDNA SNV（16-state diploid genotype 或 genotype likelihood） | cell lineage tree（有 branch length 與 bootstrap support） | ML phylogenetics（以 RAxML-NG 實作；含 ADO 與 error 的 finite-sites GT16 model）（推論／記憶） | 否（只有 diploid unphased genotype） | [amkozlov/cellphy](https://github.com/amkozlov/cellphy), 23 | verified |
| SCIPhIN | Single-cell mutation calling and phylogenetic tree reconstruction with loss and recurrence | Kuipers et al. | 2022 | Bioinformatics（preprint 10.1101/2022.01.28.478229） | [10.1093/bioinformatics/btac577](https://doi.org/10.1093/bioinformatics/btac577) | scDNA raw read counts | cell lineage tree（標出 mutation loss 與 recurrence 位置） | Bayesian（MCMC），同時做 mutation calling 與建樹（摘要） | CN 不明確建模；允許 loss／recurrence | [cbg-ethz/SCIPhIN](https://github.com/cbg-ethz/SCIPhIN), 5 | verified |
| BiTSC2 | BiTSC2: Bayesian inference of tumor clonal tree by joint analysis of single-cell SNV and CNA data | Chen et al. | 2022 | Briefings in Bioinformatics（preprint 10.1101/2020.11.30.380949） | [10.1093/bib/bbac092](https://doi.org/10.1093/bib/bbac092) | scDNA raw reads：SNV＋CNA（read depth） | clone tree（subclonal SNV/CNA genotype 與 cell assignment） | Bayesian＋MCMC，含 sequencing error 與 dropout（摘要） | CN 有（subclonal scCNA matrix）；multiplicity 部分處理（推論）；WGD 否 | [ucasdp/BiTSC2](https://github.com/ucasdp/BiTSC2), 6 | verified |
| COMPASS | COMPASS: joint copy number and mutation phylogeny reconstruction from amplicon single-cell sequencing data | Sollier et al. | 2023 | Nature Communications（preprint 10.1101/2022.01.06.475205） | [10.1038/s41467-023-40378-8](https://doi.org/10.1038/s41467-023-40378-8) | targeted amplicon scDNA（Tapestri）：SNV read counts＋region depth | tree of clones（節點上有 SNV 與 CNA/CNLOH 事件） | Bayesian＋MCMC；每個 variant 各自的 ADO rate（以 EM 估計）、doublet 模型 | CN 有（region 層級 gain/loss、CNLOH）；allele-specific 有限；WGD 否 | [cbg-ethz/COMPASS](https://github.com/cbg-ethz/COMPASS), 26 | verified |
| ConDoR | ConDoR: tumor phylogeny inference with a copy-number constrained mutation loss model | Sashittal et al. | 2023 | Genome Biology（preprint 10.1101/2023.01.05.522408） | [10.1186/s13059-023-03106-5](https://doi.org/10.1186/s13059-023-03106-5) | Tapestri SNV read counts＋cell 的 CN clustering | mutation/clone tree（constrained k-Dollo phylogeny） | constrained k-Dollo model；MILP（以 ILP 求 ML，推論／記憶） | CN 只以 cluster 形式使用，用來約束 loss 的位置；沒有 multiplicity 或 WGD | [raphael-group/ConDoR](https://github.com/raphael-group/ConDoR), 9 | verified |
| Phertilizer | Phertilizer: Growing a clonal tree from ultra-low coverage single-cell DNA sequencing of tumors | Weber et al. | 2023 | PLOS Computational Biology（preprint 10.1101/2022.04.18.488655） | [10.1371/journal.pcbi.1011544](https://doi.org/10.1371/journal.pcbi.1011544) | ultra-low coverage scWGS（DLP+/ACT）：SNV read counts＋binned read depth | clonal tree（加上 cell 與 SNV 的放置） | 機率模型＋遞迴切分（recursive partitioning）heuristic | 只把 CN signal 當成 clustering 的依據；SNV 採 infinite sites | [elkebir-group/phertilizer](https://github.com/elkebir-group/phertilizer), 4 | verified |
| ScisTree2 | ScisTree2 enables large-scale inference of cell lineage trees and genotype calling using efficient local search | Zhang et al. | 2025 | Genome Research（前身 ScisTree：Bioinformatics 2020, [10.1093/bioinformatics/btz676](https://doi.org/10.1093/bioinformatics/btz676)） | [10.1101/gr.280542.125](https://doi.org/10.1101/gr.280542.125) | scDNA genotype probability | cell lineage tree＋genotype calls | ML under infinite sites；local search，可處理上萬個 cell（摘要） | 否 | [yufengwudcs/ScisTree2](https://github.com/yufengwudcs/ScisTree2), 9 | verified |
| DelSIEVE（含 SIEVE） | DelSIEVE: cell phylogeny modeling of single nucleotide variants and deletions from single-cell DNA sequencing data | Kang et al. | 2025 | Genome Biology（preprint 10.1101/2023.09.09.556903；前身 SIEVE：Genome Biol 2022, [10.1186/s13059-022-02813-9](https://doi.org/10.1186/s13059-022-02813-9)） | [10.1186/s13059-025-03738-9](https://doi.org/10.1186/s13059-025-03738-9) | scDNA raw read counts（候選位點上所有 nucleotide） | cell phylogeny（有 branch length）＋SNV／deletion genotype | 統計 phylogenetics，finite sites；Bayesian MCMC（以 BEAST 2 實作，推論／記憶） | 單點 deletion（以 coverage 區分 deletion 與 artifact）；可辨識 double mutant；沒有 segment CN 或 WGD | [szczurek-lab/DelSIEVE](https://github.com/szczurek-lab/DelSIEVE), 1；[szczurek-lab/SIEVE](https://github.com/szczurek-lab/SIEVE), 4 | verified |
| Sc-TUSV-ext | Sc-TUSV-Ext: Single-Cell Clonal Lineage Inference from Single Nucleotide Variants, Copy Number Alterations, and Structural Variants | Bristy et al. | 2025 | J. Computational Biology 32:723–737（preprint 10.1101/2023.12.07.570724） | [10.1089/cmb.2024.0613](https://doi.org/10.1089/cmb.2024.0613) | scDNA：SNV＋CNA＋SV | clonal lineage tree | ILP（摘要） | CN 有，SV 有；WGD 不明 | [CMUSchwartzLab/Sc-TUSV-ext](https://github.com/CMUSchwartzLab/Sc-TUSV-ext), 3 | verified |
| Pharming | Pharming: Joint Clonal Tree Reconstruction of Single-Nucleotide Variant and Copy Number Aberration Evolution from Single-Cell DNA Sequencing of Tumors | Weber et al. | 2026（線上 2025） | J. Computational Biology（preprint 10.1101/2024.11.17.623950；RECOMB 2025 LNCS 10.1007/978-3-031-90252-9_25） | [10.1177/15578666251374694](https://doi.org/10.1177/15578666251374694) | low-pass scWGS：SNV read counts＋**allele-specific CN（以兩條 germline haplotype 為基準）**＋SNV 所在 segment | joint SNV＋CNA clonal tree | 定義 JCTI（NP-hard）問題；divide-and-conquer heuristic，包括 SNV cluster tree 列舉、各 segment 的 CNA tree 列舉，以及 genotype 與 cell assignment 的 coordinate descent（全文方法段） | **有**：genotype 為 (x,y,w,z)，即兩個 haplotype 的 CN 加上各自的 mutated copies，也就是 haplotype-specific multiplicity；SNV 採 Dollo，CNA 採 infinite alleles；WGD 未見 | [elkebir-group/Pharming](https://github.com/elkebir-group/Pharming), 2 | verified |
| Phyllochron | Deriving longitudinal tumor phylogenies from single-cell sequencing data | Jakatdar et al.（Sashittal, Raphael） | 2025 | bioRxiv preprint | [10.1101/2025.08.06.668977](https://doi.org/10.1101/2025.08.06.668977) | 多時間點 targeted scDNA（Tapestri AML）的 SNV read counts | longitudinal phylogeny（clone tree 加上時間點的 clone 比例約束） | longitudinal perfect phylogeny；ILP（依 Princeton talk 頁）＋統計檢定（摘要） | 否 | [raphael-group/Phyllochron](https://github.com/raphael-group/Phyllochron), 2 | verified（preprint） |

各方法重點：

**PhISCS**
- 核心創新：把 single-cell 的雜訊矩陣和 bulk VAF 的 sum condition 放在同一個 ILP／Max-SAT 中聯合求解，並允許少數 mutation 被排除（sub-perfect）。
- 主要假設：infinite sites（perfect phylogeny）。
- 與本研究的關聯：bulk 的 VAF 約束正好可以和 PhyClone 的 CCF 比較。後續的 PhISCS-BnB（見備選）用 branch and bound 加速。

**SiCloneFit**
- 核心創新：在同一個 MCMC 中同時做 clone clustering、genotype 修正和 finite-sites tree 推論，並明確建模 doublet。
- 主要假設：finite sites，允許 recurrence 與 loss。
- 與本研究的關聯：「clone clustering 與 tree 聯合抽樣」這一點和 PhyClone 的 outlier／clone 結構相似。

**SCARLET**
- 核心創新：提出 loss-supported model，只有在 CN 證據顯示該 locus 拷貝數下降時才允許 SNV loss，比 Dollo 更嚴格。
- 主要假設：除了有 CN 支持的 loss 之外，其餘遵守 infinite sites。
- 輸入（推論／記憶，待精讀確認）：需要 copy-number tree 或 CN profile 作為輸入，再加以 refine。
- 與 long-read 的關聯：如果 longphase 能指出 deletion 落在哪個 haplotype，就能把「loss 是否被 CN 支持」加強成「loss 發生在帶有 SNV 的那個 haplotype」。

**SASC**
- 核心創新：Dollo-k model，每個 mutation 最多被 loss k 次；以 simulated annealing 搜尋 tree。
- 主要假設：Dollo-k，ADO 視為 FN。
- 與本研究的關聯：屬於「放寬 infinite sites」的代表方法，但它的 loss 不受 CN 約束，可能過於寬鬆，SCARLET 和 ConDoR 正是針對這點改進。

**CellPhy**
- 核心創新：把 phylogenetics 標準的 ML 框架（RAxML-NG）配上 16-state diploid genotype 和 error／ADO model，並提供 bootstrap support。
- 主要假設：finite sites，各位點獨立。
- 與 PhyClone 的關聯：輸出的是 cell 層級、帶 branch length 的樹，不是 clone tree，和 PhyClone 的輸出形式不同。

**SCIPhIN**
- 核心創新：延伸 SCIPhI，在一個 Bayesian 框架中同時做 mutation calling 和建樹，並明確允許 mutation loss 與 recurrence，還能量化不確定性。
- 與本研究的關聯：屬於「從 raw read counts 直接建樹」的路線，和 PhyClone 直接使用 read counts 的設計一致。

**BiTSC2**
- 核心創新：以 raw reads 為輸入，同時推論 subclonal SNV genotype、CNA genotype、cell assignment 和 tree（MCMC）。
- 主要假設：clone tree，SNV 與 CNA 共用同一棵樹。
- 與 PhyClone 的關聯：SNV 的觀測模型會受 CN 調整，這和 PhyClone 用 CN 與 multiplicity 計算 VAF likelihood 的思路相近。

**COMPASS**
- 核心創新：針對 Tapestri amplicon 資料，在同一棵 clone tree 上同時放置 SNV 和 region 層級的 CNA（含 CNLOH）。ADO rate 依 variant 個別估計，並建模 doublet。
- 規模：在 123 位 AML 病人上驗證。
- 與 long-read 的關聯：CNLOH 和 allele-specific 事件是 haplotype 資訊最能約束的地方。

**ConDoR**
- 核心創新：constrained k-Dollo model。Tapestri 的 CN 不準，所以只用 CN clustering 來限制 SNV loss 只能發生在哪些 cell cluster。
- 主要假設：除 loss 外遵守 perfect phylogeny。
- 後續應用：Phyllochron 和一篇胰臟癌 Tapestri 研究的 fast-ConDoR（unverified）都延續這條路線。

**Phertilizer**
- 核心創新：在每個 cell 平均只有約 0.01–0.05× 覆蓋的 scWGS 上，利用 CN signal 協助判斷 SNV clone 結構，以遞迴切分的方式「長出」clonal tree。
- 主要假設：SNV 採 infinite sites（這是 Pharming 論文中的說法）。
- 與本研究的關聯：證明了 SNV 稀疏時，CN 資訊可以補足 SNV 的不足。

**ScisTree2**
- 核心創新：用 local search 取代窮舉，讓 infinite-sites 下的 ML cell tree 推論能處理上萬個 cell，同時輸出 genotype calls。
- 主要假設：infinite sites，不處理 CN。
- 與本研究的關聯：屬於 scalability 方向的參考。

**DelSIEVE（含 SIEVE）**
- 核心創新：SIEVE 在 finite sites 下，以候選位點全部 nucleotide 的 read counts 同時推論 SNV 與 cell phylogeny，並校正 acquisition bias。DelSIEVE 再加入 deletion 狀態，用來把「真正的 loss」和 ADO 或 artifact 分開。
- 與 long-read 的關聯：「deletion 對比 ADO」的分辨正是 haplotype-aware coverage 能夠幫上忙的地方。

**Sc-TUSV-ext**
- 核心創新：第一個在 single-cell 層級把 SNV、CNA、SV 同時放進 clonal lineage ILP 的方法。
- 與 long-read 的關聯：SV 是 long-read 的強項，可作為「事件種類擴充」的參考；但這是 single-cell 方法，不能直接搬到 bulk ONT 資料（推論）。

**Pharming**
- 核心創新：利用 scWGS CN 推論相對準確、且 SNV 常和 CNA 落在同一 segment 的性質，分 segment 列舉 CNA tree 再整合成 joint tree。genotype 明確區分 SNV 位於哪個 haplotype 的哪幾個 copy。
- 主要假設：SNV 採 Dollo；CNA 採 infinite alleles。
- 與本研究的關聯：**與本研究最接近。** 它的 (x,y,w,z) 表示法和 longphase 的 HP1/HP2 加上 haplotype-specific multiplicity 幾乎一一對應，可以直接借用來約束 PhyClone 的 multiplicity（推論）。

**Phyllochron**
- 核心創新：longitudinal perfect phylogeny，要求 clone 出現的順序和時間點一致（避免已消失的 clone 再出現），並附統計檢定判斷縱向約束是否有資料支持。
- 與 PhyClone 的關聯：PhyClone 支援 multi-sample，這類時間約束可以作為延伸（推論）。

## 經典基線（不計主選）

| 方法 | DOI | 年份／期刊 | 一句話 |
|---|---|---|---|
| OncoNEM | [10.1186/s13059-016-0929-9](https://doi.org/10.1186/s13059-016-0929-9) | 2016 Genome Biol | 以 nested effects model 推論 cell 的 clonal lineage，處理 FP/FN |
| SCITE | [10.1186/s13059-016-0936-x](https://doi.org/10.1186/s13059-016-0936-x) | 2016 Genome Biol | infinite-sites mutation tree＋FP/FN 模型，以 MCMC 推論（[cbg-ethz/SCITE](https://github.com/cbg-ethz/SCITE), 24） |
| infSCITE | [10.1101/gr.220707.117](https://doi.org/10.1101/gr.220707.117) | 2017 Genome Res | SCITE 擴充 doublet、recurrence、loss，並以模型選擇檢驗 infinite sites（[cbg-ethz/infSCITE](https://github.com/cbg-ethz/infSCITE), 9） |
| SiFit | [10.1186/s13059-017-1311-2](https://doi.org/10.1186/s13059-017-1311-2) | 2017 Genome Biol | finite-sites ML／heuristic search 的 cell tree，對 doublet 較穩健（[KChen-lab/SiFit](https://github.com/KChen-lab/SiFit), 6） |
| SCIPhI | [10.1038/s41467-018-07627-7](https://doi.org/10.1038/s41467-018-07627-7) | 2018 Nat Commun | 從 raw reads 同時做 mutation calling 與建樹（[cbg-ethz/SCIPhI](https://github.com/cbg-ethz/SCIPhI), 25） |
| SPhyR | [10.1093/bioinformatics/bty589](https://doi.org/10.1093/bioinformatics/bty589) | 2018 Bioinformatics | k-Dollo＋FP/FN 的 combinatorial 方法（clustering 與 ILP 交替） |

## 近似與排除

### 備選（符合判準、會推論 topology，但因與主選重疊、屬變體或證據較弱而不計主選）

- **B-SCITE**（Malikic et al., Nat Commun 2019, [10.1038/s41467-019-10737-5](https://doi.org/10.1038/s41467-019-10737-5)）：SCITE 加上 bulk VAF 的 MCMC。和 PhISCS 屬同一團隊、同一條路線，所以不重複列。
- **PhISCS-BnB**（Sadeqi Azer et al., Bioinformatics 2020, [10.1093/bioinformatics/btaa464](https://doi.org/10.1093/bioinformatics/btaa464)；[algo-cancer/PhISCS-BnB](https://github.com/algo-cancer/PhISCS-BnB), 10）：PhISCS 的 perfect phylogeny 加速版，屬於變體。
- **gpps**（Ciccolella et al., BMC Bioinformatics 2020, [10.1186/s12859-020-03736-7](https://doi.org/10.1186/s12859-020-03736-7)）：Dollo-k 的 ILP 版本，和 SASC 同一團隊，屬於變體。
- **Scelestial**（Foroughmand-Araabi et al., PLoS Comput Biol 2022, [10.1371/journal.pcbi.1009100](https://doi.org/10.1371/journal.pcbi.1009100)）：Steiner tree 近似演算法建 cell tree。沒有 error model，對 ADO 的處理較弱。
- **Phylovar**（Edrisi et al., Bioinformatics 2022, [10.1093/bioinformatics/btac254](https://doi.org/10.1093/bioinformatics/btac254)；[NakhlehLab/Phylovar](https://github.com/NakhlehLab/Phylovar), 2）：phylogeny-aware SNV calling，同時推論樹。主要貢獻偏向 variant calling。
- **PHALCON**（Priya et al., bioRxiv 2024, [10.1101/2024.12.26.630385](https://doi.org/10.1101/2024.12.26.630385)；Research Square 版 [10.21203/rs.3.rs-6155560/v1](https://doi.org/10.21203/rs.3.rs-6155560/v1)；文件頁 https://phalcon-phylogeny-aware-variant-calling-for-panel-seq-data.readthedocs.io/ ，沒找到 GitHub）：針對大規模 Tapestri panel，在 clonal phylogeny 上以 finite-sites 做 variant calling。主要貢獻是 variant calling，且尚未正式出版。
- **SCOPE**（Khan & Sashittal, bioRxiv 2026, [10.64898/2026.01.21.700922](https://doi.org/10.64898/2026.01.21.700922)；[sashittal-group/SCOPE](https://github.com/sashittal-group/SCOPE), 1）：在 copy-number constrained perfect phylogeny 下，刻劃 scWGS 資料所支持的「所有一致 tree 的解空間」。概念上很有價值（tree uncertainty），但只是 preprint，不計主選。
- **SCITE-RNA**（Zimmermann et al., Genome Biol 2026, [10.1186/s13059-026-04123-w](https://doi.org/10.1186/s13059-026-04123-w)；[cbg-ethz/SCITE-RNA](https://github.com/cbg-ethz/SCITE-RNA), 6）：從 scRNA-seq 的 SNV 推論 mutation／cell tree。會推論 topology，但資料是 scRNA，不在本面向（scDNA）範圍。

### 排除

- **SCsnvcna**（Zhang et al., Genome Res 2023, [10.1101/gr.277249.122](https://doi.org/10.1101/gr.277249.122)；[compbio-mallory/SCsnvcna](https://github.com/compbio-mallory/SCsnvcna), 1）：把 SNV 放到**既有的 CNA tree** 上，屬於給定 tree 的下游工作，不自行推論 topology。
- **doubletD**（Weber et al., Bioinformatics 2021, [10.1093/bioinformatics/btab266](https://doi.org/10.1093/bioinformatics/btab266)）：只做 scDNA doublet detection，不建樹。
- **SECEDO**（Rozhoňová et al., preprint [10.1101/2021.11.08.467510](https://doi.org/10.1101/2021.11.08.467510)）、SCClone、RobustClone、BnpC：只做 clustering，不推論 topology（或只事後畫 MST）。
- **Canopy2**（Weideman et al., preprint [10.1101/2024.03.18.585595](https://doi.org/10.1101/2024.03.18.585595)）：bulk DNA 加 scRNA，屬於 bulk 或 multi-omics 面向，交給其他 worker。
- **純 CN 的 single-cell 方法**（例如 DICE、MEDALT、CNETML、SCICoNE、Lazac、SPRINTER）：交給 CN worker，不在這裡展開。
- **Tapestri-CN／fast-ConDoR**（WebSearch 結果中的胰臟癌單細胞研究，PMC12900634）：這是應用研究，方法學貢獻是 CN caller 加上 ConDoR 的加速版。這次沒有查到 DOI 或 fast-ConDoR 的獨立方法論文，標 **unverified**。

## 給協調者的建議

最該精讀的幾篇：

1. **Pharming（JCB 2026）**：唯一一個在 genotype 中明確寫出「haplotype-specific CN 加上各 haplotype 上的 mutated copies」的 joint SNV＋CNA 建樹方法。它的 (x,y,w,z) 狀態和 longphase 的 HP1/HP2 phasing、PhyClone 的 multiplicity 最直接對應；以 segment 為單位列舉 CNA tree 的做法，也可以借來處理 CNV timing。
2. **SCARLET（2020）與 ConDoR（2023）**：兩者都屬於「CN 約束 SNV loss」的路線。這是把 Dollo 從過度寬鬆收斂回可辨識模型的關鍵想法。long-read phasing 可以把「CN 下降」進一步升級成「帶有 SNV 的那個 haplotype 被 delete」，約束更強。
3. **COMPASS（Nat Commun 2023）**：Tapestri 上的 SNV、CNA、CNLOH 聯合 MCMC，並建模 per-variant ADO 與 doublet。它的 CNLOH 與 allele-specific 事件建模，以及 MCMC 的 tree move 設計，可以和 PhyClone 的 PG/SMC 比較。
4. **DelSIEVE（Genome Biol 2025）**：用 raw read counts 區分 deletion、ADO 與 double mutant，是 finite-sites 統計模型的代表。它可作為「同一位點多次事件」觀測模型的參考。
5. **Phertilizer 與 SCOPE（選讀）**：Phertilizer 示範在 SNV 極稀疏時如何用 CN signal 協助推論 clone 結構。SCOPE 則刻劃「整個一致 tree 空間」，可呼應 PhyClone 想量化的 topology uncertainty。

## 不確定之處

- SCARLET 是否需要預先給定的 CN tree（記憶中需要），本次沒有讀到全文（Cell Systems 頁面回應 403）。
- SiCloneFit、CellPhy、DelSIEVE 的推論細節（MCMC、RAxML-NG、BEAST 2）依記憶撰寫，已標「推論／記憶」。
- Sc-TUSV-ext 是否處理 WGD，摘要中沒有寫。
- PHALCON 和 Phyllochron 截至查詢日沒有找到正式出版版本。
