# W4：在推樹時使用 read-level／molecule-level 連鎖資訊的方法

面向：同一 read／read pair／linked-read molecule 上的 SNV 共現（mutation-pair phasing）、germline SNP phasing、haplotype／phase set、long-read（ONT／PacBio）特徵直接進入 tree likelihood 或 topology 約束。
查詢日：2026-10-16。GitHub stars 以 `gh api` 在查詢日取得。

> 總結先講：**真正把「同一 read 上 SNV 共現」放進推樹的方法極少**。查到的只有 TreeClone（2019，short-read mutation pair，限 CN=2）、PairClone（同組，沒有樹）、BitPhylogeny（2015，read pattern 當作 haplotype 樣本）以及 AACR 2026 Abstract 6912（Donmez & Kolmogorov，long-read pairwise timing，只有摘要）。其他「haplotype-aware」的推樹方法（Numbat、MEDICC2、CalicoST）用的是 **germline SNP phasing 得到的 haplotype-specific CN**，不是 somatic SNV 在 read 上的連鎖。主選因此只收 6 篇，寧缺勿濫。

## 搜尋紀錄

- `tumor phylogeny reconstruction long-read phasing mutation co-occurrence same read clone tree method`
- `"long-read" tumor clonal evolution phylogeny haplotype-aware subclone inference nanopore 2025 bioRxiv`
- `read-backed phasing somatic mutations resolve clonal ordering pigeonhole principle tumor phylogeny`
- `"mutation pairs" OR "pairs of mutations" phased reads subclonal reconstruction method bulk sequencing tree inference`
- `linked-read 10x Genomics tumor phylogeny reconstruction method haplotype subclone tree`
- `PairClone Bayesian subclone caller mutation pairs Zhou Müller Sengupta Ji`
- `single-cell DNA phylogeny germline SNP read phasing somatic mutation haplotype-aware tree inference method`
- `Conbase unsupervised discovery clonal somatic mutations single cells read phasing Genome Biology`
- `single-cell long-read whole genome sequencing nanopore PacBio phylogeny somatic SNV haplotype lineage tree SMOOTH-seq`
- `Strand-seq single-cell haplotype-resolved structural variation subclone phylogeny tumor scTRIP`
- `tumor clonal haplotype reconstruction from bulk sequencing reads subclone haplotypes phylogeny method ...`
- `"Phasing tumor clones" AACR 2026 abstract mutation pair long-read`
- `bulk tumor phylogeny joint SNV haplotype-specific copy number phased germline SNP B-allele clone tree inference method 2024 2025`
- `Donmez Kolmogorov point mutation timing long reads tumor clones phylogeny bioRxiv`
- `"long reads" "phylogeny" somatic SNV "same read" co-occurrence clonal tree inference "ultra-long" OR "PacBio HiFi" cancer method preprint 2025 2026`
- `long-read subclonal reconstruction haplotype-resolved clonal deconvolution bulk tumor nanopore method cellular prevalence phased reads`
- `haplotype-specific copy number single-cell phylogeny inference method 2024 2025 allele-specific tree WGD`
- `"phasing" somatic SNVs "infinite sites" violation detection tumor phylogeny reads cis trans parallel mutation`
- `OncoPhase cellular prevalence somatic mutation phase information germline SNP`
- `PhylEx clonal tree bulk DNA single-cell RNA mutation co-occurrence ...`
- `Numbat haplotype-aware copy number single-cell transcriptomes ...`
- `Bayesian tumor subclone phylogeny "mutation pairs" OR "phased reads" OR "haplotype reads" 2020–2023 extension TreeClone`
- `BitPhylogeny ... Genome Biology 2015`
- `CalicoST allele-specific copy number aberrations tumor phylogeography ...`
- `TUSV-ext reconstructing tumor clonal lineage trees ...`
- `"Biallelic mutations in cancer genomes reveal local mutational determinants" ...`
- `SMOOTH-seq single-cell genome sequencing third-generation platform ...`
- `single-cell nanopore DNA sequencing tumor subclone phylogeny haplotype copy number 2024 2025 ...`
- `clone tree inference constraint "two mutations" observed together on same reads ancestral relationship bulk sequencing ILP OR combinatorial phasing constraints`
- `long-read sequencing tumor structural variant phylogeny reconstruction method haplotype phased subclonal SV tree 2025 2026 bioRxiv`
- `"Somatic mutation phasing and haplotype extension using linked-reads in multiple myeloma" journal published`
- `MEDICC2 whole-genome doubling aware copy-number phylogenies ...`
- `single-cell mutation tree inference using read-level phasing with germline heterozygous SNPs to resolve allelic dropout lineage tree method`
- `LiRA linked-read analysis single-cell somatic SNV calling read-backed phasing ...`
- 另外 WebFetch：synapsesocial AACR 2026 abstract 6912、4134 頁面；bioRxiv LongPhase-TO 頁；PMC13493970（melanoma sublines 正式版）；PMC12991090（Baker 2026）；ideas.repec（PairClone）；UMD talk 3571。

## 主選候選

分兩類：(A) somatic SNV 在 read 上的共現直接進入推樹；(B) haplotype（germline phasing 得到的 haplotype-specific CN）進入推樹。(A) 是本研究 novelty 的直接對手，(B) 是 haplotype-specific CN 那一半的對手。

| 方法名 | 論文標題 | 第一作者 et al. | 年份 | 期刊/preprint | DOI(連結) | 輸入資料 | 輸出樹類型 | 模型與推論 | 是否處理 CN／multiplicity／WGD | 程式碼(URL, stars) | 驗證狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TreeClone（A；已知線索） | TreeClone: Reconstruction of tumor subclone phylogeny based on mutation pairs using next generation sequencing data | Tianjian Zhou et al.（Zhou, Sengupta, Müller, Ji） | 2019 | Ann. Appl. Stat. 13(2):874–899（arXiv 1703.03853） | [10.1214/18-AOAS1224](https://doi.org/10.1214/18-AOAS1224) | bulk short-read paired-end；相鄰 SNV pair 的 4 種 haplotype read count（含只蓋一端的 partially missing reads）；single 或 multi-sample | clone tree（subclone 以 mutation-pair haplotype 定義） | Bayesian latent feature allocation + phylogenetic tree prior；MCMC | 否：作者明言只用 copy-neutral（CN=2）區域的 mutation pair；無 multiplicity／WGD | 論文列 compgenome.org／ccte.uchicago.edu/treeclone；無官方 GitHub | verified（Project Euclid 頁） |
| Phasing tumor clones（A；已知線索 AACR 6912） | Phasing tumor clones by timing point mutations using bulk long-read sequencing | Ataberk Donmez et al.（…, Mikhail Kolmogorov） | 2026 | AACR Annual Meeting 2026, Cancer Res 86(7 Suppl) Abstract 6912（會議摘要） | DOI 推測為 10.1158/1538-7445.AM2026-6912，**未直接查證** | bulk ONT（含 ultra-long >100 kb）；somatic SNV／indel；同時蓋到兩個 PM 的 reads 的 ref/alt 組合；single-sample（H2009、H1437 cell line） | point-mutation phylogeny；node＝可能的 clonal haplotype | 推論：combinatorial／graph-based。每對 PM 判為 sequential／co-occurring／divergent，形成多種 edge type 的 graph，用 transitivity 串接沒有共同 read 的 pair，以 connected component 為單位 phasing | 摘要未提 CN／multiplicity／WGD | 未公開 | verified（摘要頁 synapsesocial；標題、作者、Abstract 號已核） |
| PhylEx（A'：cell-level 共現） | Reconstructing clonal tree for phylo-phenotypic characterization of cancer using single-cell transcriptomics | Seong-Hwan Jun et al.（…, Andrew Roth, Jens Lagergren） | 2023 | Nat. Commun. 14:982（bioRxiv 2021.02.16.431009） | [10.1038/s41467-023-36202-y](https://doi.org/10.1038/s41467-023-36202-y) | bulk DNA（SNV read count＋CN）＋ scRNA-seq 上 SNV 的 per-cell co-occurrence；multi-sample bulk 可 | clone tree＋cell-to-clone assignment | Bayesian；tree-structured stick-breaking（TSSB）prior＋MCMC（推論：沿用 PhyloWGS 系 TSSB） | bulk 部分沿用 CN 輸入；WGD 未見 | [junseonghwan/PhylEx](https://github.com/junseonghwan/PhylEx)（3★） | verified（Nat Commun／PMC） |
| Numbat（B） | Haplotype-aware analysis of somatic copy number variations from single-cell transcriptomes | Teng Gao et al.（…, Po-Ru Loh, Peter Kharchenko） | 2023（online 2022-09） | Nat. Biotechnol. 41(3) | [10.1038/s41587-022-01468-y](https://doi.org/10.1038/s41587-022-01468-y) | scRNA-seq；germline het SNP 經 population-based phasing 得到 haplotype，allele＋expression 訊號；single-sample | subclone phylogeny（CNV 事件放在 branch）＋single-cell CN | HMM（haplotype-aware）＋ iterative 交替推 CN 與 phylogeny（推論：phylogeny 部分用 ML／distance 型方法） | 有 allele-specific CN（含 CN-LOH）；無 SNV multiplicity；WGD 未見 | [kharchenkolab/numbat](https://github.com/kharchenkolab/numbat)（232★） | verified（PubMed 36163550） |
| MEDICC2（B） | MEDICC2: whole-genome doubling aware copy-number phylogenies for cancer evolution | Tom L. Kaufmann et al.（…, Roland F. Schwarz） | 2022 | Genome Biol. 23:241（bioRxiv 2021.02.28.433227） | [10.1186/s13059-022-02794-9](https://doi.org/10.1186/s13059-022-02794-9) | **haplotype-specific** CN profile（single-cell 或 multi-sample bulk）；SNV 不用 | CN event phylogeny（sample／cell tree） | minimum-event distance（FST）＋tree building；不假設 infinite sites，容許 overlapping events | 是：haplotype-specific CN、clonal／subclonal WGD | GitHub 搜到 [schwarzlab-ccb/medicc2](https://github.com/schwarzlab-ccb/medicc2)（10★；官方來源請以論文 code availability 為準） | verified（Genome Biol／DOAJ） |
| CalicoST（B） | Inferring allele-specific copy number aberrations and tumor phylogeography from spatially resolved transcriptomics | Cong Ma et al.（…, Benjamin J. Raphael） | 2024 | Nat. Methods 21(12):2239–2247（bioRxiv 2024.03.09.584244） | [10.1038/s41592-024-02438-9](https://doi.org/10.1038/s41592-024-02438-9) | spatial transcriptomics（Visium）；germline SNP phasing 的 haplotype B-allele＋expression；multi-slice | clone phylogeny＋空間 phylogeography | HMM＋HMRF（空間）推 allele-specific CNA；之後由 clone CN 推 phylogeny | 有 allele-specific CN（mirrored subclonal CNA、CN-LOH）；無 SNV | [raphael-group/CalicoST](https://github.com/raphael-group/CalicoST)（51★） | verified（Nat Methods／PMC11621028） |

重點：

- **TreeClone**：唯一一個正式發表、把「同一 read pair 上兩個 SNV 的 haplotype count」當作 likelihood 主體並推 clone tree 的 bulk 方法。核心創新是 tree prior 讓只有可被樹解釋的 subclone genotype 拿到非零機率，並示範 marginal VAF 相同時 phasing 可區分 linear 與 branching。主要假設：infinite sites（樹上的 genotype 單調）、CN=2、只用 short-read 可同時覆蓋的近距 pair（約數百 bp 內）。和本研究的關係：它就是「read 共現進 clone-tree likelihood」的先例；但它沒有 multiplicity／CN，也沒把 pair likelihood 和 PhyClone 式 marginal SNV＋CN likelihood 合成同一模型，long-read 長距 pair 與 germline phase set 都沒用到。
- **Donmez & Kolmogorov AACR 2026**：目前看到唯一明確「bulk long-read＋read 上 PM 共現→phylogeny」的工作，而且用的正是我們研究清單裡的 H2009、H1437（CASTLE collection）。從摘要看是 combinatorial pairwise relation graph，不是機率 likelihood，也沒提 CN、purity、multiplicity 或 cellular prevalence。只有摘要，細節（是否處理 sequencing error、LOH、germline phase）未知。**它是最需要追蹤的直接競爭者**，作者說下一步要延伸到 SV timing。
- **PhylEx**：Roth lab 的 bulk＋single-cell 方法。它的「co-occurrence」是 **cell-level**（同一細胞的 scRNA reads），不是 molecule-level，但它示範了在 bulk clone-tree likelihood 上「加一項 co-occurrence likelihood」的作法，在 likelihood 結構上最接近我們要做的（推論）。和 PhyClone 同一個 lab，code 風格與 tree 表示可能可以互通（推論）。
- **Numbat／MEDICC2／CalicoST**：三者都把 phasing 得到的 haplotype-specific CN 放進推樹，處理 mirrored CNA、CN-LOH（MEDICC2 還處理 WGD）。但都**不用 SNV 的 read-level 連鎖**，phasing 也來自 population／germline，不是 somatic read。和本研究的關係：它們證明 haplotype-specific CN 對推樹有用；我們要做的「把 SNV 掛到 HP1/HP2 並和 haplotype-specific CN 一起約束 multiplicity／timing」仍不在它們的範圍內。

## 經典基線（不計主選）

| 方法 | 年份／期刊 | DOI | 與本面向的關係 |
|---|---|---|---|
| BitPhylogeny（Yuan, Sakoparnig, Markowetz, Beerenwinkel） | 2015, Genome Biol. 16:36 | [10.1186/s13059-015-0592-6](https://doi.org/10.1186/s13059-015-0592-6) | 最早把 **read-level pattern**（methylation pattern 或 single-cell genotype）當作 haplotype 樣本，以 tree-structured stick-breaking（TSSB）＋MCMC 同時推 clone 數、clone 組成與樹。作者提到 read 變長後可在同一 read 看到多個 SNV。無 CN。Code：[keyuan/bitphyloR](https://github.com/keyuan/bitphyloR)（3★）。 |
| PhyloWGS（Deshwar et al.） | 2015, Genome Biol. | （其他 worker 已涵蓋） | TSSB 推樹的基線；利用 pigeonhole 推論，但沒有 read 連鎖。 |
| LICHeE／Canopy／CITUP／SCITE | 2014–2016 | （其他 worker 涵蓋） | 都只用 marginal VAF 或 cell genotype，沒有 read 連鎖；列出來讓對照完整。 |

## 近似與排除

這一節決定 novelty 邊界，所以寫得比較詳細。

### A. 用了 read／molecule 連鎖，但不推 topology（或不是方法論文）

| 方法／論文 | DOI | 用了什麼連鎖 | 排除原因 |
|---|---|---|---|
| PairClone（Zhou, Müller, Sengupta, Ji），JRSS-C 68(3):705–725, 2019 | [10.1111/rssc.12328](https://doi.org/10.1111/rssc.12328) | short-read mutation pair 的 haplotype count | TreeClone 的前身，用 categorical IBP 推 subclone 數、genotype 與比例，**明確假設 subclone 彼此獨立、不推樹**。只做 clustering／deconvolution。CN=2。 |
| SomaticHaplotype（Foltz, …, Li Ding；已知線索） | bioRxiv [10.1101/2024.08.09.607342](https://doi.org/10.1101/2024.08.09.607342)（PMC11326269） | 10x linked-read；phased 79.4% 的 somatic mutation，multi-sample 延長 phase block | 查詢日沒有找到正式期刊版。只做 somatic mutation phasing，用 phased pair 去**手動 refine** clonal model（例如同一 haplotype 上兩個 NRAS hotspot 在不同 subclone 獨立發生），沒有推樹演算法。 |
| Meltos（已知線索） | 未重新查證（Bioinformatics 2020，Ricketts et al.） | 不是 read 連鎖 | 給定 SNV tree 之後放 SV，屬下游。 |
| LongSom（已知線索） | 未重新查證 | long-read scRNA 上的 somatic SNV／CNA／fusion | 只做 clonal heterogeneity，不推樹（搜尋結果也說「does not build phylogenetic trees」）。 |
| Wakhan、Severus（已知線索） | 未重新查證 | long-read haplotype-specific CN／SV | 只做 CN／SV calling，排除。 |
| Sakamoto 2022 lung phasing（已知線索） | 未重新查證 | long-read phasing＋timing | 應用研究，不是推樹方法。 |
| Liu, Goretsky et al.，Long-read sequencing of single cell-derived melanoma sublines…，Nat. Commun. 17:8740, 2026（bioRxiv 2025.08.28.672865） | [10.1038/s41467-026-75172-9](https://doi.org/10.1038/s41467-026-75172-9) | ONT＋margin／WhatsHap haplotag | 樹用既有的 **ScisTree**，以 23 個 subline 的 SNV presence/absence 推出；**read 共現沒有用來建樹或約束樹**。新工具 TreeHarmonizer 只把 SNV／SV／CNA 放到固定的樹上（下游）。這是 Kolmogorov／Sahinalp 團隊，和 Donmez 摘要同一個生態系。 |
| Goretsky et al.，AACR 2026 Abstract 4134 | [10.1158/1538-7445.am2026-4134](https://doi.org/10.1158/1538-7445.am2026-4134) | long-read SV breakpoint | 「phylogeny-constrained」SV calling 與 timing；從摘要看樹是給定的，屬下游。 |
| Day et al.，AACR 2026 Abstract 704 | DOI 未查證 | ONT melanoma subline | 同一套 melanoma 資料的應用摘要。 |
| LongPhase-TO（Zhen-Yu Chen, …, Ruibang Luo, …, Yao-Ting Huang），bioRxiv 2026-09 | [10.64898/2026.09.14.751225](https://doi.org/10.64898/2026.09.14.751225) | 同一 graph 內 co-phase germline 與 somatic allele；從 heterozygosity depletion 推 LOH 與 tumor DNA fraction | tumor-only 的 somatic haplotype reconstruction／variant recalibration，**不推 subclone、不推樹**。和本研究使用的 longphase 是同一個工具家族（Huang 組），可以直接當作上游輸入（推論）。 |
| Baker et al.，Genome-wide classification of tumor-derived reads from bulk long-read sequencing，bioRxiv 2026-03 | [10.64898/2026.03.03.709085](https://doi.org/10.64898/2026.03.03.709085) | HiPhase germline phasing＋methylation 把 read 分成 tumor/normal | 分類 read；subclonal 部分用 DPClust（VAF＋CN），沒有 read 共現，也不推樹。 |
| OncoPhase（Chedom-Fotso, Ahmed, Yau），bioRxiv 2016 | [10.1101/046631](https://doi.org/10.1101/046631) | somatic SNV 與鄰近 phased germline SNP 的 read 連鎖 | 用 phase 資訊估計單一 mutation 的 cellular prevalence，**很接近我們想用 phase 約束 multiplicity／CCF 的想法**，但不推樹，也沒找到正式版。 |
| Demeulemeester, Dentro, Gerstung, Van Loo，Biallelic mutations in cancer genomes…，Nat. Genet. 2022 | [10.1038/s41588-021-01005-8](https://doi.org/10.1038/s41588-021-01005-8) | read-level phasing 判 cis／trans | 在 PCAWG 用 phasing 偵測 infinite-sites violation（parallel／divergent mutation），是**用 phasing 檢驗 ISA** 的重要證據，但不是推樹方法。 |
| Conbase（Hård et al.），Genome Biol. 2019 | [10.1186/s13059-019-1673-8](https://doi.org/10.1186/s13059-019-1673-8) | single-cell 中 somatic SNV 與 germline SNV 的 read phasing | 只做 single-cell sSNV calling（處理 allelic dropout），不推樹。 |
| LiRA（Bohrson et al.），Nat. Genet. 51:749–754, 2019 | [10.1038/s41588-019-0366-2](https://doi.org/10.1038/s41588-019-0366-2) | single-cell read-backed phasing（candidate sSNV 與 germline het SNP） | 只做 single-cell 的 calling／artifact 過濾，不推樹。 |
| Hård et al.，Long-read whole-genome analysis of human single cells，Nat. Commun. 2023 | [10.1038/s41467-023-40898-3](https://doi.org/10.1038/s41467-023-40898-3) | single-cell PacBio HiFi（MDA）上 phased SNV／SV | 實驗技術＋calling，不推樹。 |
| SMOOTH-seq（Fan et al.），Genome Biol. 22:195, 2021（任務提示寫的 Genome Research 有誤） | [10.1186/s13059-021-02406-y](https://doi.org/10.1186/s13059-021-02406-y) | single-cell PacBio long-read WGS | 實驗技術，作者自承 SNV／CNV 準確度有限；不推樹。 |
| scTRIP（Sanders et al.），Nat. Biotechnol. 2020 | [10.1038/s41587-019-0366-x](https://doi.org/10.1038/s41587-019-0366-x) | Strand-seq 的 chromosome-length haplotype＋strand＋depth | single-cell haplotype-resolved SV discovery 與 subclone 描述；沒有找到推樹的演算法。 |

### B. 用 haplotype／phasing，但推樹以外或不屬 read-level

| 方法 | DOI | 排除或降級原因 |
|---|---|---|
| CHISEL（Zaccaria & Raphael），Nat. Biotechnol. 2021 | [10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6) | single-cell 的 allele／haplotype-specific CN calling 與 clone 推論，樹只在應用中描述；主要貢獻是 CN calling，依判準排除。Code [raphael-group/chisel](https://github.com/raphael-group/chisel)（44★）。 |
| HATCHet2 | （其他 worker 涵蓋） | bulk haplotype-specific CN calling，不推樹。 |
| TUSV-ext（Fu, Lei, Tao, Schwartz），Bioinformatics 38(Suppl 1):i125, 2022 | [10.1093/bioinformatics/btac253](https://doi.org/10.1093/bioinformatics/btac253) | **會**推 SNV＋CNA＋SV clone tree，也有 allele-specific CN 與 breakpoint phasing，但 phasing 是模型內推出的，**不是 read-level 觀測**。應屬 W3（CN/SV）的主選；此處只列為近似。Code [CMUSchwartzLab/TUSV-ext](https://github.com/CMUSchwartzLab/TUSV-ext)（21★）。 |
| Pairtree | DOI 未在本次查證 | pairwise ancestry relation 只從 VAF 推，概念上和「read 共現判 pairwise relation」對應，可以借用它的 pairwise-relation 表示法（推論）。 |

## Novelty 邊界

問題：「把 phased read 上的 SNV 共現與 haplotype-specific CN 放進 PhyClone 類 bulk clone-tree likelihood」是否已經有人做過？做到什麼程度？

1. **read 共現進 clone-tree likelihood：有先例，但很窄。**
   - TreeClone（2019）是唯一正式發表、把 mutation-pair 的 4 類 haplotype read count 放進 Bayesian 推樹 likelihood 的方法。限制：short-read 近距 pair、**只用 CN=2 區域**、沒有 multiplicity、purity 與 CN 沒有和 marginal SNV likelihood 聯合，而且 subclone 以 mutation pair 為單位，不是 PhyClone 那種 SNV cluster＋CN 的 node（論文描述）。
   - BitPhylogeny（2015）把 read pattern 當作 haplotype 樣本推樹，沒有 CN（論文描述）。
   - 因此「在 tree likelihood 中使用 read 共現」**本身不能宣稱為 novelty**；要宣稱的是下面 3 到 5 點的組合。
2. **long-read 共現→phylogeny：已有一個同時期的競爭者，只發表到摘要層級。** Donmez & Kolmogorov（AACR 2026 #6912）用 bulk ONT ultra-long read，以 pairwise sequential／co-occurring／divergent 關係加上 transitivity 建 PM phylogeny，資料正是 H2009／H1437。從摘要看：combinatorial、沒有 CN／multiplicity／purity／prevalence likelihood，也沒有 multi-sample。**風險**：正式 preprint 可能在 2026–2027 出現，並可能補上 CN。建議定期追蹤 Kolmogorov 組（NCI）的 bioRxiv。
3. **haplotype-specific CN 進推樹：已有，但沒有和 SNV read 連鎖結合。** MEDICC2、Numbat、CalicoST 都用 phased haplotype-specific CN 推 CN-event phylogeny（MEDICC2 含 WGD），SNV 卻不在它們的 likelihood 裡，或只是外加。TUSV-ext 有 allele-specific CN 加 SNV 加 SV，但 phasing 是推出來的，不是 read 觀測。
4. **用 phase 約束 SNV multiplicity／CCF：只有不推樹的先例。** OncoPhase（2016 preprint）用 germline phase 估 prevalence；Wakhan、Sakamoto 一類工作用 long-read phasing 做 CN 與 timing；Demeulemeester 2022 用 phasing 檢驗 ISA。**沒有找到**任何方法把「SNV→HP1/HP2（phase set）指派」與「haplotype-specific CN」一起放進 clone-tree likelihood，去約束 multiplicity、CNV timing（SNV 在 CN gain 之前或之後）與 topology。
5. **cell-level 共現加 bulk likelihood 的組合範式已存在**（PhylEx，Roth lab）。可以把它當作 likelihood 合成方式的參照：bulk 項 × co-occurrence 項。我們的差別在於共現來自 molecule（read）而非 cell，同時要處理 read 長度與覆蓋造成的 pair 選擇偏差，以及 germline phase set 的橋接。

**結論（分析推論）**：截至 2026-10-16 的搜尋結果，**沒有找到**任何方法同時做到以下四點：
- (i) PhyClone 式 bulk SNV＋CN＋purity 的 marginal likelihood；
- (ii) long-read 上 somatic SNV pair 的共現 likelihood（含 sequential、co-occurring、mutually exclusive 三種關係）；
- (iii) 透過 germline phase set 把 SNV 指派到 HP1/HP2，並和 haplotype-specific CN 聯合，約束 multiplicity 與 CN timing；
- (iv) 以 SMC／PG 推論 topology。

最接近的部分重疊是 TreeClone（只有 ii 的 short-read 版，限 CN=2）、Donmez AACR 2026（ii 加樹，無 CN）和 MEDICC2／Numbat（只有 iii 的 CN 部分）。可宣稱的 novelty 是 (i)+(ii)+(iii) 的**聯合模型**，以及 long-read 長距 linkage 讓 pair 數量大增後的計算處理。單獨宣稱「首次用 read phasing 推腫瘤樹」**不成立**。

不確定處：Donmez 摘要的完整方法未知；查詢日可能已有未被搜尋引擎索引的 preprint。SomaticHaplotype 正式版未找到。Meltos、LongSom 等已知線索本次沒有重新核對 DOI。

## 給協調者的建議

1. **TreeClone（AOAS 2019）**：唯一正式發表的「read pair 共現 × tree prior」likelihood。精讀它對 4 類 haplotype count 的建模與 partially-missing read 的處理，可以直接借來當作我們 pair likelihood 的起點，同時用它 CN=2 的限制界定差異。
2. **Donmez & Kolmogorov AACR 2026 #6912**：最直接的同期競爭者，而且用同樣的 cell line。精讀摘要並追蹤後續 preprint，必要時聯絡作者確認範圍。
3. **PhylEx（Nat Commun 2023）**：Roth lab 在 bulk clone-tree likelihood 上加 co-occurrence 項的範式，和 PhyClone 同 lab，最適合拿來參考 likelihood 合成與推論實作。
4. **MEDICC2（Genome Biol 2022）**：haplotype-specific CN 加 WGD 的推樹標竿。我們做 haplotype-specific CN 約束時，需要和它的 event model 對照，也可以當作 CN-only baseline。
5. （次選）**OncoPhase preprint＋Demeulemeester 2022**：前者是「phase→prevalence／multiplicity」的最早想法；後者提供 phasing 偵測 ISA violation 的實證，可支撐我們用 read 共現檢驗或放寬 infinite sites 的動機。
