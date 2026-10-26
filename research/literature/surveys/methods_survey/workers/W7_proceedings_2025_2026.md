# W7：2025–2026 會議論文集與 2026 preprint 補查

查核日：2026-10-17。範圍：補查 README 所列「沒有逐篇翻查」的 2025–2026 proceedings，以及 2025-06 到 2026-10 的 bioRxiv preprint。

收錄判準與 README 相同：論文的主要貢獻必須是推論 tumor phylogeny topology。以下幾類列入排除：
- 只做 clustering 或 CN calling；
- 給定樹之後做下游分析，例如 migration、trajectory、tree comparison；
- 不以腫瘤體細胞突變為對象的 CRISPR lineage tracing。

DOI 的核對方式：
- Crossref DOI：用 `https://api.crossref.org/works/<doi>` 核對標題與第一作者。
- LIPIcs（WABI）的 DOI 由 DataCite 註冊，Crossref 回 404，所以改用 `https://api.datacite.org/dois/<doi>` 核對，並在表中註明。

## 查過的來源

| 來源 | 是否成功瀏覽完整目錄 | 方法與查詢字串 | 腫瘤演化樹相關命中 |
|---|---|---|---|
| RECOMB 2025（LNCS 15647，ISBN 978-3-031-90252-9） | **是**。官方 accepted papers 頁列 55 篇；Crossref `filter=isbn:9783031902529,type:book-chapter` 也回 55 章，兩者一致 | 逐篇看標題 | Pharming、ScisTree2（已在 44 中）；MACH2、Partition Function（Mehrabadi）、Tree Labeling Polytope（排除）；另有 CRISPR lineage tracing 3 篇（排除） |
| RECOMB 2026（Thessaloniki） | **部分**。官方頁 `recomb.org/recomb2026/accepted_papers` 已逐篇看完（約 66 篇）；**LNCS 冊在 Crossref 查不到**（以書名與 2026 年份查詢都沒有結果） | 逐篇看標題 | Arborist（W1 已排除）、omlta（tree alignment，排除）、POTTR（下游，排除）、LineageMap（lineage tracing，排除）、DecoDiPhy（metagenomics，排除） |
| ISMB 2025（Bioinformatics 41, Supplement_1） | **是**。OUP 目錄 71 篇，Crossref 依 volume＋issue 過濾也得 71 篇 | 標題關鍵字 `tumou?r\|cancer\|clon\|phylog\|lineage\|copy.number\|haplotyp\|long.read\|metasta\|subclon\|evolution\|single.cell\|mutation`，再人工看過 | fastppm（`btaf235`，給定 tree 的 regression 子程序，列近似） |
| ISMB 2026（Bioinformatics 42, Supplement_1） | **是**。OUP 目錄 69 篇；Crossref 合計 124 篇，含 Supplement_2 | 同上 | LAML-Pro（CRISPR lineage tracing，排除）、BFBArchitect（BFB 重建，不推樹）。**沒有 tumor phylogeny 方法** |
| ECCB 2026（Bioinformatics 42, Supplement_2） | **是**。OUP 目錄 54 篇＋editorial | 同上 | 無 |
| WABI 2025（LIPIcs 344） | **是**。DataCite 逐號列出 `10.4230/LIPIcs.WABI.2025.0–23` | 逐篇看標題 | **Dolphyin**（新增）。正式版已轉投 AMB 2026 |
| WABI 2026（LIPIcs 390） | **是**。DataCite 逐號列出 `10.4230/LIPIcs.WABI.2026.0–31` | 逐篇看標題 | **Luque et al. branch-and-bound**（新增）；Satas et al. 的 statistical inconsistency 是理論文，排除 |
| RECOMB-CCB 2025 | **部分**。`accepted.html` 是沿用 2024 的模板（Orchard、Refphase 等），不是 2025 名單；改看 `program.html` | 人工看議程 | Phyllochron（W2 已收）、Arborist（已排除）；Rivaroli 的 subclonal deconvolution、Cocomello 的 amplification timing、BiLinT（lineage tracing）都排除 |
| RECOMB-CCB 2026 | **部分**。accepted 頁寫「TBA」，內容同樣是舊模板；改看 `program.html`，有完整議程 | 人工看議程 | SMiTH（＝Kuzmin 2025 Nat Commun，給定 phylogeny 推 migration，排除）、Conquer（clustering consensus，排除）、Jiang／Wang 的 penalized likelihood（CliPP 系，clustering，排除）、LeafRank（下游，排除）、Cwikla et al.（LBR，只有標題，unverified） |
| RECOMB-CG 2025（LNCS 15666，ISBN 978-3-031-94927-2） | **是**。官方站 `recomb.org/recomb-cg2025` 回 404，改用 Crossref ISBN 過濾，列出 21 章 | 逐篇看標題 | Liu & Nakhleh「Inferring Phylogenetic Trees of Cancer Evolution from Longitudinal Single-Cell Copy Number Profiles」＝**NestedBD-Long**，已含在 44 個中的 NestedBD |
| RECOMB-CG 2026（LNCS，ISBN 978-3-032-26891-4） | **是**。Crossref ISBN 過濾，列出 19 章 | 逐篇看標題 | 無腫瘤相關論文 |
| bioRxiv 2025-06-01 到 2026-10-17 | **是（限 6 個 category）**。用 `api.biorxiv.org/details` 全量下載 bioinformatics、cancer biology、genomics、genetics、evolutionary biology、systems biology，去重後共 21,286 個 DOI | 下方三種方式 | 見「新增候選」與「近似與排除」 |
| Crossref posted-content（`from-posted-date:2025-06-01`） | 是（相關性排序，每個查詢取前 40 筆） | `tumor phylogeny`、`clone tree cancer`、`cancer phylogenetic reconstruction`、`long-read phylogeny tumor`、`clonal evolution tree inference single-cell`、`copy number phylogeny`、`subclonal reconstruction tree`、`haplotype phasing tumor clone`、`bulk long-read sequencing tumor clones somatic mutation co-occurrence reads`、`nanopore tumor subclonal phylogeny`、`long reads clonal phylogeny cancer cell line`、`mutation pairs reads phylogeny tumor` | 補到 Ahmed et al. 2026（bin size）。其他命中與 bioRxiv 全量掃描重疊 |
| WebSearch（輔助） | — | `RECOMB 2026 accepted papers tumor phylogeny`、`RECOMB-CG 2025 accepted papers`、`bioRxiv 2026 long-read tumor phylogeny haplotype phasing clone tree`、`El-Kebir 2026 bioRxiv tumor phylogeny method`、`Zaccaria lab 2026 …`、`Roth lab Bouchard-Côté 2026 …`、`Russell Schwartz 2026 …` | 沒有新增方法 |

bioRxiv 全量掃描用了三種方式：
- **(a) 方法導向**：title＋abstract 同時含腫瘤詞與樹詞，abstract 含 `we present/introduce/develop/propose|algorithm|framework|tool`。
- **(b) 標題寬鬆比對**：標題含 `phylog|clonal tree|clone tree|mutation tree|lineage tree|clonal evolution|subclon|perfect phylogeny|dollo|copy-number evolution` 等。
- **(c) 作者比對**：Kolmogorov、Raphael、El-Kebir、Morris Q、Roth A、Schwartz R、Zaccaria、Sashittal、Bouchard-Côté、Beerenwinkel、Sahinalp、Oesper、McPherson、Satas。
- 另外用 long-read 詞（`long-read|nanopore|ONT|PacBio|HiFi`）配上樹詞或 subclone 詞，再做一次掃描。

覆蓋限制：
- 沒有掃 medRxiv。也沒有掃 bioRxiv 其他 category，例如 cell biology、molecular biology。
- RECOMB 2026 的 LNCS 章節 DOI 目前查不到，所以 RECOMB 2026 的論文都以 bioRxiv DOI 記錄。

## 新增候選

以下都**不在現有 44 個主選中**，也不在 W1–W5 的備選或排除清單裡；已用 grep 核對過 workers 目錄。

**驗證狀態**：
- 表中 DOI 都已核對標題與第一作者，Crossref 或 DataCite 解析成功。
- 輸入、輸出、推論、CN 處理四欄只依 abstract 整理（ScisTreeCNA 另看了 GitHub README），沒有讀全文。

| 方法 | 標題 | 第一作者 | 年份 | venue | DOI | 輸入 | 輸出樹 | 推論 | CN 處理 | 程式碼 | 是否已在 44 中 | 建議分類 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ScisTreeCNA** | Accurate Probabilistic Reconstruction of Cell Lineage Trees from SNVs and CNAs with ScisTreeCNA | Haotian Zhang（Yufeng Wu 組） | 2025 | bioRxiv preprint | [10.1101/2025.11.21.689819](https://doi.org/10.1101/2025.11.21.689819)（Crossref 已核） | scDNA 上的 SNV 與 CNA | cell lineage tree | 以 SNV＋CNA 聯合演化的新 probabilistic model 做 likelihood 推論，GPU 加速（ScisTree2 的延伸） | 有，CNA 直接進 likelihood。是否區分 allele／haplotype **未核** | [haotianzh/ScisTreeCNA](https://github.com/haotianzh/ScisTreeCNA)，2★ | 否 | **C** |
| **Dolphyin** | Dolphyin: A Combinatorial Algorithm for Identifying 1-Dollo Phylogenies in Cancer | Daniel W. Feng（El-Kebir） | 2025（WABI）；2026（AMB） | WABI 2025，LIPIcs 344:9；正式版 Algorithms Mol Biol 2026 | [10.4230/LIPIcs.WABI.2025.9](https://doi.org/10.4230/LIPIcs.WABI.2025.9)（DataCite 已核）；[10.1186/s13015-026-00303-2](https://doi.org/10.1186/s13015-026-00303-2)（Crossref 標題、作者已核） | binary mutation matrix（sc 為主） | 1-Dollo phylogeny（persistent perfect phylogeny） | 證明 1-Dollo linear phylogeny 等價於 C1P，再把 tree 遞迴分解成多條 linear phylogeny；指數時間的 combinatorial 演算法 | 否（只允許 loss，不建模 CN） | [elkebir-group/Dolphyin](https://github.com/elkebir-group/Dolphyin)，1★ | 否 | **B** |
| （未命名；faster-tphyl） | Exact and Efficient Inference of Tumor Phylogenies via Novel Pruning Techniques | Juan Luque（Sahinalp） | 2026 | WABI 2026，LIPIcs 390:10 | [10.4230/LIPIcs.WABI.2026.10](https://doi.org/10.4230/LIPIcs.WABI.2026.10)（DataCite 已核；Crossref 不適用） | scDNA 帶雜訊的 binary genotype matrix | 最可能的 tumor phylogeny（perfect phylogeny 型，推論） | branch-and-bound，以 Vertex Cover 2-approximation 做 bound，有最佳性保證；宣稱比前一代（PhISCS-BnB 類）快 100 倍 | 否 | [jdluque/faster-tphyl-reconstruction](https://github.com/jdluque/faster-tphyl-reconstruction)，1★ | 否（PhISCS-BnB 只在 W2 備選） | **B**（也可視為 PhISCS-BnB 的後繼，列備選） |
| **PhyloSOLID** | PhyloSOLID: Robust phylogeny reconstruction from single-cell data despite inherent error and sparsity | Qing Yang（Yanmei Dou，Westlake） | 2026 | bioRxiv preprint | [10.64898/2026.02.04.703905](https://doi.org/10.64898/2026.02.04.703905)（Crossref 已核） | scDNA 或 scRNA 上的 somatic SNV | cell phylogeny | 先用可靠 mutation 建 graph-based backbone tree，再用懲罰 phylogenetic inconsistency 的 Bayesian model 逐步併入其餘資料 | 否（abstract 未提） | abstract 提到 web interface；repo 未核 | 否 | **B** |
| **scLongTree** | scLongTree: an accurate computational tool to infer the longitudinal tree for single-cell DNA sequencing data | Rituparna Khan（Xian Mallory，FSU） | 2023 首版；2026-04 出 v2 | bioRxiv preprint | [10.1101/2023.11.11.566680](https://doi.org/10.1101/2023.11.11.566680)（Crossref 已核） | longitudinal scDNA（SNV） | subclonal longitudinal tree | 專為多時點設計的推樹演算法；與 LACE、SCITE、SiCloneFit 比較（細節未核） | 否（abstract 未提） | `compbio-mallory/sc_longitudinal_infer`（GitHub 回 301，已搬移，未核） | 否 | **B**（與 Phyllochron、LACE 同一條 longitudinal 路線） |
| **SRNJ／DLCA-NJ** | Scalable and robust phylogenetic tree reconstruction from copy-number data with Sparse Rooted Neighbor Joining | Vittorio Zampinetti（Jens Lagergren，KTH） | 2026 | bioRxiv preprint | [10.64898/2026.07.30.739152](https://doi.org/10.64898/2026.07.30.739152)（Crossref 已核） | scDNA CN profile 之間的 pairwise distance | rooted cell tree（diploid root） | 把 Deepest-LCA NJ 用在 CN 樹，利用已知的 diploid root；再提出 sparse 版 SRNJ 以處理大量 cell | 是（total CN distance；不是 allele-specific，推論） | 未核 | 否（同組的 VICTree 在 W5 排除） | **D** |
| **CTBF**（Cancer Tree Biopsy Framework） | Biopsy-aware phylogenetic reconstruction from longitudinal single-cell copy number profiles | Jarosław Paszek（Univ. Warsaw） | 2026（2026-10-16 才上線） | bioRxiv preprint | [10.64898/2026.10.14.759162](https://doi.org/10.64898/2026.10.14.759162)（Crossref 已核） | longitudinal scDNA integer CN profile；多次 biopsy | partial tree 或 closed-state tree；允許 sampled ancestor | biopsy-guided 重建：依採樣順序連接 profile，延後處理模糊的 parent assignment；與 NJ、MEDICC2、NestedBD-Long 比較 | 是（integer CN；allele-specific 未提） | 未核 | 否 | **D** |

**協調者注意**：
- 7 個新增候選中，**正式發表的只有 Dolphyin（AMB 2026）與 Luque et al.（WABI 2026 proceedings）**，其餘 5 個都是 preprint。
- 依 README「preprint 與正式版只算一篇」的慣例，Phyllochron 這類 preprint 也曾列主選，所以這 5 個是否列主選，交由協調者決定。

### 在 proceedings 中命中、但已涵蓋者（不重複計）

| 方法 | 出現的 venue | 現有位置 |
|---|---|---|
| Pharming | RECOMB 2025，[10.1007/978-3-031-90252-9_25](https://doi.org/10.1007/978-3-031-90252-9_25) | C 類主選（JCB 2026 正式版） |
| ScisTree2 | RECOMB 2025，[10.1007/978-3-031-90252-9_21](https://doi.org/10.1007/978-3-031-90252-9_21) | B 類主選（Genome Res 2025） |
| NestedBD-Long | RECOMB-CG 2025，[10.1007/978-3-031-94928-9_2](https://doi.org/10.1007/978-3-031-94928-9_2)（Crossref 已核，Yushu Liu） | D 類主選 NestedBD 的「含 -Long」。**建議在 README 補上這個 LNCS DOI，作為 -Long 的正式出處** |
| Phyllochron | RECOMB-CCB 2025 short talk | B 類主選 |
| SCOPE（Khan & Sashittal） | bioRxiv 2026 | W2 備選 |
| LoPhy | bioRxiv 2025，2026-04 出 v3 | W3、W5 排除或近似 |
| Arborist | RECOMB 2026；RECOMB-CCB 2025 | W1 排除（只為候選樹排序） |
| SCITE-RNA（Zimmermann／Beerenwinkel） | bioRxiv [10.1101/2025.09.04.674140](https://doi.org/10.1101/2025.09.04.674140) | W2 備選 |
| Enumerating clonal trees（Bernstein／Oesper） | bioRxiv 2025 | W1 排除 |
| PICTographPlus | bioRxiv 2026 | W1 排除 |

## 近似與排除

| 方法／論文 | 來源 | DOI | 排除理由 |
|---|---|---|---|
| fastppm（Schmidt, Qi, Raphael, El-Kebir） | ISMB 2025 | [10.1093/bioinformatics/btaf235](https://doi.org/10.1093/bioinformatics/btaf235) | 解的是「**給定 topology** 的 perfect phylogeny regression」，屬於 tree search 的內層子程序。它本身不搜尋 topology，但嵌進 fastBE、Orchard 類方法後可加速 50–450 倍。**對本研究有工程價值**：PhyClone 的 SMC／PG 每一步都要對固定 tree 計分，概念相同（推論） |
| MACH2（Roddur et al.） | RECOMB 2025 | [10.1007/978-3-031-90252-9_34](https://doi.org/10.1007/978-3-031-90252-9_34) | 給定 clone tree，推 migration history |
| Tree Labeling Polytope（Schmidt & Raphael） | RECOMB 2025 | [10.1007/978-3-031-90252-9_20](https://doi.org/10.1007/978-3-031-90252-9_20) | 給定 tree 的 ancestral labeling 與 migration |
| Partition Function Algorithm（Rashidi Mehrabadi et al.） | RECOMB 2025 | [10.1007/978-3-031-90252-9_50](https://doi.org/10.1007/978-3-031-90252-9_50) | 評估已推出的 subclonal 結構有多可靠，不做推樹 |
| omlta（Gilbert, Wu, …, Sahinalp） | RECOMB 2026；AACR 2026 #6898 | [10.64898/2026.02.25.708046](https://doi.org/10.64898/2026.02.25.708046)；[10.1158/1538-7445.am2026-6898](https://doi.org/10.1158/1538-7445.am2026-6898) | 兩棵 clonal tree 的最佳 alignment，屬比較工具。可作為評估指標的參考 |
| POTTR（Käufler, …, Raphael） | RECOMB 2026 | [10.64898/2026.02.25.707960](https://doi.org/10.64898/2026.02.25.707960) | 從多棵已推出的 tree 找跨病人重複出現的 trajectory |
| Inferring Multi-Stage Pathway Progression Models from Tumor Phylogenies（Sashittal 組） | bioRxiv 2026 | [10.64898/2026.05.25.727519](https://doi.org/10.64898/2026.05.25.727519) | 以 tree 當輸入的下游分析（只看標題與 abstract 的分類，未逐字核） |
| SMiTH／graph homomorphism（Kuzmin, …, Raphael, Skums） | RECOMB-CCB 2026 highlight | [10.1038/s41467-025-63411-4](https://doi.org/10.1038/s41467-025-63411-4) | 抽樣出與「給定 phylogeny」一致的 migration／transmission tree，不推 phylogeny topology |
| Statistical Inconsistency of Error-Correction Objectives for Perfect Phylogenies（Satas, Myers, Shah） | WABI 2026 | [10.4230/LIPIcs.WABI.2026.23](https://doi.org/10.4230/LIPIcs.WABI.2026.23) | 理論文：證明 min-flip 目標函數在統計上不一致。**對評估有參考價值**：sc 錯誤率下，error-correction 目標偏好不平衡的深樹 |
| Discrete diffusion models for tumor phylogenies（Sabata & Schwartz） | bioRxiv 2026 | [10.64898/2026.03.23.713822](https://doi.org/10.64898/2026.03.23.713822) | 學習 tree 的生成分布（unconditional generation），不從病人資料推樹 |
| Optimizing CN profiles for tumor phylogeny（Ahmed, …, Bansal） | bioRxiv 2026 | [10.64898/2026.10.05.756871](https://doi.org/10.64898/2026.10.05.756871) | 只處理 CN calling 前的 bin size 選擇，屬前處理 |
| SVCFit（Liu, …, Karchin） | bioRxiv（2026-08 v4） | [10.1101/2025.02.01.636056](https://doi.org/10.1101/2025.02.01.636056) | 主要貢獻是 SV cellular fraction 估計；建樹部分 abstract 未說明，推測沿用 PICTograph 系 |
| cfClone（Kabeer, …, Bouchard-Côté, Roth） | bioRxiv 2026 | [10.64898/2026.07.29.741620](https://doi.org/10.64898/2026.07.29.741620) | **Roth lab 新作**。用 scWGS 得到的**既有 clonal structure**，在 cfDNA 上估 clone prevalence。模型含 haplotype-specific signal 與 MCMC，但不推 topology |
| PHYFUM（Bousquets-Muñoz, …, Mallo） | bioRxiv 2026 | [10.64898/2026.05.05.722981](https://doi.org/10.64898/2026.05.05.722981) | 會推 topology，但對象是正常與癌前組織的 gland／stem cell，用 fluctuating methylation，不是 tumor clone tree。列為邊界 |
| mt-SCITE（Seidel, …, Beerenwinkel） | bioRxiv（2026-08 v2） | [10.1101/2025.02.28.640740](https://doi.org/10.1101/2025.02.28.640740) | 用 mitochondrial mutation 推 cell lineage；應用在 T cell，不是腫瘤 |
| LAML-Pro（Chu, …, Raphael） | ISMB 2026 | [10.1093/bioinformatics/btag219](https://doi.org/10.1093/bioinformatics/btag219) | CRISPR lineage tracing 的 cell lineage tree |
| Dai & Molloy DP；Prillo NJ guarantees；Sashittal differentiation maps；LineageMap | RECOMB 2025、2026 | 見 RECOMB LNCS 目錄 | 都是 CRISPR lineage tracing |
| VINE（Siepel 組） | bioRxiv 2026 | [10.64898/2025.12.24.696405](https://doi.org/10.64898/2025.12.24.696405) | 通用 phylogenetic VI，適用物種樹與 CRISPR lineage，不是腫瘤 somatic 專用 |
| CNVeil（Yuan, …, X. M. Zhou） | bioRxiv 2026 | [10.64898/2026.07.20.739667](https://doi.org/10.64898/2026.07.20.739667) | sc haplotype-specific CN calling，不推樹 |
| BFBArchitect（Li et al.） | ISMB 2026 | [10.1093/bioinformatics/btag225](https://doi.org/10.1093/bioinformatics/btag225) | long-read BFB 結構重建，不推 clone tree |
| Conquer（Li, Weber, Van Loo）；CliPP 系 penalized likelihood（Jiang, …, W. Wang）；Rivaroli et al. | RECOMB-CCB 2025、2026 | 無 DOI（議程）→ unverified | subclonal clustering 或 consensus，不出 topology |
| LeafRank（Wu, Wang, Sun） | RECOMB-CCB 2026 LBR；bioRxiv | [10.64898/2026.07.06.736651](https://doi.org/10.64898/2026.07.06.736651) | 給定 sc phylogeny 推 fitness，屬下游 |
| Cwikla et al.，Tracking the co-evolution of genome and transcriptome through treatment | RECOMB-CCB 2026 LBR | 無 DOI → **unverified** | 只有議程標題，無法判斷是否推樹；建議追蹤 Schwarz 組的後續 preprint |
| Lefèbvre et al.，Parent-of-origin phasing of somatic mutations | bioRxiv 2026 | [10.64898/2026.09.02.748867](https://doi.org/10.64898/2026.09.02.748867) | 把 somatic mutation phase 到親源 haplotype，用於 mutation burden 分析，不推樹 |
| DecoDiPhy（Arasti, …, El-Kebir, Mirarab） | RECOMB 2026 | [10.64898/2026.01.18.700179](https://doi.org/10.64898/2026.01.18.700179) | metagenomics 的 distance deconvolution，不是腫瘤 |

## 對 novelty 邊界的影響

**結論：沒有改變。** 截至 2026-10-17，在上述 proceedings 與 bioRxiv 掃描範圍內，仍然沒有找到任何方法同時做到以下四點：
- bulk SNV＋CN likelihood；
- long-read 上 SNV pair 的共現；
- 透過 phase set 把 SNV 指派到 HP1／HP2；
- 以 SMC／PG 推論 topology。

細節如下：

1. **read-level 共現**：新增的 7 個候選沒有一個用到 read／molecule 層級的 SNV 連鎖。bioRxiv 的 long-read 掃描只命中下列幾類，都不推樹：
   - calling 或 phasing 工具：LongPhase-S、LongPhase-TO、Baker 2026、Lefèbvre 2026、LRSomatic；
   - 應用論文：melanoma sublines（已在 W3、W4）。
   F 類在主選期間仍沒有方法。
2. **haplotype 方向**：新出現的 haplotype-aware 工作有兩個，都不推 topology：
   - cfClone（Roth lab）：在給定 clone 結構下估 prevalence；
   - CNVeil：sc haplotype-specific CN calling。
   HP 指派加上 haplotype-specific CN 約束 multiplicity 這一點，最接近的仍是 Pharming（sc）與 TUSV-ext（latent phase）。
3. **SNV＋CN 聯合推樹**：新增的 ScisTreeCNA 與 LoPhy、Pharming、COMPASS 同屬 single-cell。bulk 端沒有新的 SNV＋CN 推樹方法。PhyClone 在 A 類的競品清單不變。
4. **推論引擎**：新方法用的推論方式如下，沒有新的 SMC／Particle Gibbs 腫瘤推樹方法：
   - combinatorial：Dolphyin、branch-and-bound、CTBF；
   - distance-based：SRNJ；
   - Bayesian 精修或 likelihood search：PhyloSOLID、ScisTreeCNA。
   - fastppm 屬固定 tree 的計分加速，不搜尋 topology，可以考慮借用到 PhyClone 的 tree 計分（推論）。
5. **對評估有用的副產品**：
   - Satas et al.（WABI 2026）：min-flip 目標偏好不平衡的深樹。
   - omlta：clonal tree alignment，可作為另一種 tree 距離。

**待追蹤**：
- Cwikla／Schwarz 的 RECOMB-CCB 2026 LBR；
- RECOMB 2026 的 LNCS 章節 DOI；
- 本次沒有掃的 medRxiv 與 bioRxiv 其他 category。
