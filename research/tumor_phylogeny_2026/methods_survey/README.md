# 腫瘤演化樹重建方法調查（2019–2026）

查核日：2026-10-16。文件語言：繁體中文，技術名詞保留英文。

> **2026-10-18**：`papers/` 下 M01、M02、M04–M08 已納入 [論文分類索引](../../PAPER_CATEGORIES.md)（平台 × single-cell 真值）。46 個方法的總表仍以本檔為準，未逐一分類。

## 為什麼重做

上一輪 [13 篇調查](../README.md) 的選文標準是「論文裡有樹」，不是「建樹是主要貢獻」。依建樹在論文中的角色重分：

- 只有 MEDICC2（B05）是 phylogeny 方法論文。
- B01、B04、A04 以演化推理為主軸，但是應用研究。
- 其餘多半是 cfDNA 追蹤、cell cycle、phenotype、CN calling 等研究，樹只是手段。

這一輪改成只收「**主要貢獻是推論 tumor phylogeny topology 的方法**」。13 篇仍可作為參考樹資料來源或特徵證據，不刪除。

## 收錄判準與流程

**收錄**：方法會推論 clone tree、mutation tree、cell lineage tree 或 CN／event phylogeny 的 topology。主選期間 2019–2026；更早的奠基方法列為經典基線。preprint 與正式版只算一篇。

**排除**：
- 給定 tree 只做下游：ALPACA、Meltos、TreeHarmonizer。
- 只做 clustering：PyClone-VI、BnpC、DeCiFer。
- 只做 CN 或 SV calling：HATCHet2、SIGNALS、CHISEL、Wakhan、Severus。

**流程**：5 個平行 subagent 各查一個面向，原始報告在 `workers/`：

| Worker | 面向 | 檔案 |
|---|---|---|
| W1 | bulk SNV（＋CN）clone tree | [W1_bulk_snv_cn.md](workers/W1_bulk_snv_cn.md) |
| W2 | single-cell DNA 的 SNV（＋CN）tree | [W2_single_cell_snv.md](workers/W2_single_cell_snv.md) |
| W3 | CN／allele-specific CN／WGD／SV event phylogeny | [W3_cn_sv_event.md](workers/W3_cn_sv_event.md) |
| W4 | read／molecule 層級連鎖、long-read、haplotype | [W4_read_phasing_longread.md](workers/W4_read_phasing_longread.md) |
| W5 | 多資料整合方法、benchmark 與 review | [W5_integrative_benchmark.md](workers/W5_integrative_benchmark.md) |
| W6 | 「待核」推論細節的正文核對 | [W6_verification.md](workers/W6_verification.md) |
| W7 | 2025–2026 會議論文集與 2026 bioRxiv 補查 | [W7_proceedings_2025_2026.md](workers/W7_proceedings_2025_2026.md) |

**協調者核對**：
- 主選表 50 個不重複 DOI，全部以 Crossref API 解析成功，標題與第一作者相符（2026-10-16）。
- SCARLET 的輸入從官方 README 確認：需要給定 copy-number tree，在其上推 mutation tree。

**證據層級**：
- 輸入、輸出、模型三欄多數依摘要與方法段整理。
- worker 標「待核」或「推論／記憶」的細節，在各 worker 檔中保留標記，本表不升級為已核。
- GitHub stars 為 2026-10-16 查詢值，見各 worker 檔。

## 總覽

去重後主選 **46 個方法**，另列 2 個邊界方法：

| 類別 | 數量 |
|---|---|
| A. bulk SNV（＋CN） | 13 |
| B. single-cell SNV | 10 |
| C. single-cell SNV＋CN | 6 |
| D. CN／event phylogeny | 11 |
| E. 多模態整合 | 5 |
| F. read-level 連鎖 | 1 |

跨 worker 重複收錄的已合併：PhISCS、COMPASS、SCARLET、ConDoR、BiTSC2、Pharming、TUSV-ext 家族、CALDER、CalicoST、MEDICC2、DEVOLUTION。

**PhyClone 的位置**：屬 A 類，是 bulk SNV＋CN＋purity 的 Bayesian nonparametric 方法，以 Particle Gibbs／SMC 推論。同類主要競品如下：

| 方法 | 推論方式 |
|---|---|
| Pairtree | pairwise relation tensor＋MCMC |
| Orchard | stochastic beam search |
| CONIPHER | combinatorial |
| PICTograph | MCMC＋spanning tree 列舉 |

PhyClone 已有正式版：Bioinformatics 2025，[10.1093/bioinformatics/btaf344](https://doi.org/10.1093/bioinformatics/btaf344)。

## 主選總表

欄位精簡版；完整欄位、程式碼連結與 stars 見對應 worker 檔。

### A. bulk SNV（＋CN）clone tree

| 方法 | 年份／期刊 | DOI | 輸入 | 推論 | CN 處理 |
|---|---|---|---|---|---|
| **PhyClone** | 2025 Bioinformatics | [btaf344](https://doi.org/10.1093/bioinformatics/btaf344) | SNV counts＋CN＋purity；single／multi-sample | forest CRP prior＋Particle Gibbs（SMC）；outlier model 預設開啟，prior 依 chromosome clustering 指派 | clonal major/minor CN 外給；multiplicity 在 1..major（CN 變化前）加 1 個「CN 變化後」genotype 上均勻邊際化，不輸出 multiplicity／timing；不處理 subclonal CN（論文自述）。見 [M01](papers/M01_phyclone_2025/README.md) |
| Pairtree | 2022 Blood Cancer Discov | [BCD-21-0092](https://doi.org/10.1158/2643-3230.BCD-21-0092) | SNV VAF；多到 100 samples | pairwise tensor＋MCMC；ISA | 部分（外給 variant read probability） |
| Orchard | 2024 PLoS CB | [e1012653](https://doi.org/10.1371/journal.pcbi.1012653) | SNV VAF；multi-sample | stochastic beam search | 部分 |
| CONIPHER | 2023/24 Nat Protoc | [s41596-023-00913-9](https://doi.org/10.1038/s41596-023-00913-9) | SNV＋CN（CCF）；multi-region | combinatorial；pigeonhole／crossing rule 剔除 | 有 |
| CALDER | 2019 Cell Syst | [cels.2019.05.010](https://doi.org/10.1016/j.cels.2019.05.010) | SNV；longitudinal | MILP＋時間順序約束 | 否 |
| PICTograph | 2022 Bioinformatics | [btac367](https://doi.org/10.1093/bioinformatics/btac367) | SNV＋外給 CN／multiplicity／purity | JAGS MCMC＋spanning tree 列舉 | 有（外給） |
| fastBE | 2024 PLoS CB | [e1012631](https://doi.org/10.1371/journal.pcbi.1012631) | SNV；數百 samples | regression＋tree search；ISA | 否 |
| Sapling | 2026 AMB（WABI 2024） | [s13015-025-00295-5](https://doi.org/10.1186/s13015-025-00295-5) | SNV counts；multi-sample | backbone tree 推論＋擴展 | 否 |
| SubMARine | 2021 PLoS CB | [pcbi.1008400](https://doi.org/10.1371/journal.pcbi.1008400) | subclone frequency＋subclonal CNA | polynomial-time 約束推理 | 有（equivalence constraints） |
| BAMSE | 2019 BMC Bioinf | [s12859-019-2824-3](https://doi.org/10.1186/s12859-019-2824-3) | SNV counts；multi-sample | Bayesian model selection | 否 |
| TRaIT | 2019 BMC Bioinf | [s12859-019-2795-4](https://doi.org/10.1186/s12859-019-2795-4) | binary presence（bulk 或 sc） | Suppes causation＋結構學習 | 否 |
| DEVOLUTION | 2021 Commun Biol | [s42003-021-02637-6](https://doi.org/10.1038/s42003-021-02637-6) | SNV＋CNA event；multi-region | MCF 輸入 → DBSCAN → subclonal deconvolution → 二元 event matrix → phangorn ML（JC，NJ 起始）與 MP（pratchet） | CNA 只當二元 event；MCF 需外部先算，沒有 CN state 模型 |
| TUSV-ext | 2022 Bioinformatics（ISMB） | [btac253](https://doi.org/10.1093/bioinformatics/btac253) | SNV 平均 copy number（非 read count）＋allele-specific CN＋SV breakpoint | ILP＋coordinate descent；L1 目標式，無 likelihood；SNV／SV 皆 Dollo | 有；SNV／SV phase 到 allele（latent）。「allele」是 major／minor 排序，不是 germline haplotype，mirrored allelic imbalance 會混淆；purity 即 root normal clone 頻率；規模約 120 variant、9 clone。見 [M05](papers/M05_tusv_ext_2022/README.md) |

經典基線（不計主選）：PhyloWGS、Canopy、LICHeE、CITUP、AncesTree、SPRUCE、Treeomics、MIPUP（W1）。

### B. single-cell DNA：SNV 為主

| 方法 | 年份／期刊 | DOI | 重點 |
|---|---|---|---|
| SiCloneFit | 2019 Genome Res | [gr.243121.118](https://doi.org/10.1101/gr.243121.118) | tree-structured CRP（clone 在 binary clonal tree 葉節點）＋finite-sites；Gibbs＋partial reversible-jump／MH；輸入是 genotype 矩陣；doublet |
| SASC | 2021 Bioinformatics | [btaa722](https://doi.org/10.1093/bioinformatics/btaa722) | Dollo-k＋simulated annealing |
| CellPhy | 2022 Genome Biol | [s13059-021-02583-w](https://doi.org/10.1186/s13059-021-02583-w) | GT16 ML phylogenetics（RAxML-NG） |
| SCIPhIN | 2022 Bioinformatics | [btac577](https://doi.org/10.1093/bioinformatics/btac577) | calling＋建樹聯合；loss／recurrence |
| ScisTree2 | 2025 Genome Res | [gr.280542.125](https://doi.org/10.1101/gr.280542.125) | 上萬 cell 的 ML local search |
| DelSIEVE（含 SIEVE） | 2025 Genome Biol | [s13059-025-03738-9](https://doi.org/10.1186/s13059-025-03738-9) | finite sites＋單點 deletion |
| Phertilizer | 2023 PLoS CB | [pcbi.1011544](https://doi.org/10.1371/journal.pcbi.1011544) | ultra-low coverage scWGS；遞迴切分 |
| Phyllochron | 2025 bioRxiv | [2025.08.06.668977](https://doi.org/10.1101/2025.08.06.668977) | longitudinal Tapestri；preprint |
| Dolphyin | 2026 AMB（WABI 2025） | [s13015-026-00303-2](https://doi.org/10.1186/s13015-026-00303-2) | 1-Dollo phylogeny 的 combinatorial 演算法（El-Kebir 組） |
| Luque et al.（faster-tphyl） | 2026 WABI | [LIPIcs.WABI.2026.10](https://doi.org/10.4230/LIPIcs.WABI.2026.10) | branch-and-bound 精確推論，新 pruning；接續 PhISCS-BnB |

2025–2026 preprint 候選（W7 補查，DOI 已核；不計主選，正式發表後再評估）：

| 方法 | DOI | 建議分類 | 重點 |
|---|---|---|---|
| ScisTreeCNA | [10.1101/2025.11.21.689819](https://doi.org/10.1101/2025.11.21.689819) | C | ScisTree 延伸，SNV＋CNA 聯合 probabilistic model |
| PhyloSOLID | [10.64898/2026.02.04.703905](https://doi.org/10.64898/2026.02.04.703905) | B | 對 single-cell 誤差 robust 的建樹 |
| scLongTree | [10.1101/2023.11.11.566680](https://doi.org/10.1101/2023.11.11.566680) | B | longitudinal scDNA；2026 年出 v2 |
| SRNJ／DLCA-NJ | [10.64898/2026.07.30.739152](https://doi.org/10.64898/2026.07.30.739152) | D | 大規模 sc CN 建樹（Lagergren 組） |
| CTBF | [10.64898/2026.10.14.759162](https://doi.org/10.64898/2026.10.14.759162) | D | biopsy-aware longitudinal sc CN 建樹 |

經典基線：SCITE、OncoNEM、SiFit、SCIPhI、SPhyR 等（W2）。不計主選但符合判準：B-SCITE（放 E 類）、PhISCS-BnB、gpps、Scelestial、Phylovar、PHALCON、SCOPE、SCITE-RNA（理由見 W2）。

### C. single-cell DNA：SNV＋CN 聯合

| 方法 | 年份／期刊 | DOI | CN 如何進模型 |
|---|---|---|---|
| SCARLET | 2020 Cell Syst | [cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001) | 需給定 CN tree；SNV loss 只允許發生在 CN 下降處 |
| BiTSC2 | 2022 Brief Bioinf | [bbac092](https://doi.org/10.1093/bib/bbac092) | 同時估 scCNA 與 scSNV genotype；MCMC |
| COMPASS | 2023 Nat Commun | [s41467-023-40378-8](https://doi.org/10.1038/s41467-023-40378-8) | Tapestri；gain／loss／CNLOH 與 SNV 同樹，region 內有 variant 時為 allele-specific，同一 region 每條 lineage 最多一次；simulated annealing 搜 MAP tree（MCMC 式 moves，node 權重與 dropout rate 每步用 EM） |
| ConDoR | 2023 Genome Biol | [s13059-023-03106-5](https://doi.org/10.1186/s13059-023-03106-5) | constrained k-Dollo；CN cluster 約束 loss |
| Sc-TUSV-ext | 2025 J Comput Biol 32(8) | [cmb.2024.0613](https://doi.org/10.1089/cmb.2024.0613) | SNV＋CNA＋SV；先以 MEDICC2 距離把 cell 聚成 clone，再解 ILP（無 VAF 一致性項） |
| **Pharming** | 2026 J Comput Biol（online 約 2025-09；RECOMB 2025） | [15578666251374694](https://doi.org/10.1177/15578666251374694) | genotype＝(x,y,w,z)：兩條 germline haplotype 的 CN＋各自帶 mutation 的 copy 數；但 likelihood 只用 (w+z)/(x+y)，SNV 在哪條 haplotype 是 latent。只讀到 bioRxiv v1，見 [M04](papers/M04_pharming_2026/README.md) |

### D. CN／event phylogeny

| 方法 | 年份／期刊 | DOI | 資料 | 是否 allele／haplotype-specific |
|---|---|---|---|---|
| MEDICC2 | 2022 Genome Biol | [s13059-022-02794-9](https://doi.org/10.1186/s13059-022-02794-9) | bulk 或 sc | 是；含 WGD |
| WCND | 2020 Bioinformatics | [btaa470](https://doi.org/10.1093/bioinformatics/btaa470) | bulk 或 sc | 可 |
| MEDALT | 2021 Genome Biol | [s13059-021-02291-5](https://doi.org/10.1186/s13059-021-02291-5) | sc（可吃 scRNA 推的 CN） | 未寫明 |
| CONET | 2022 Genome Biol | [s13059-022-02693-z](https://doi.org/10.1186/s13059-022-02693-z) | scWGS | 否（只看事件有無） |
| SCICoNE | 2025 Bioinformatics | [btaf072](https://doi.org/10.1093/bioinformatics/btaf072) | 淺層 scWGS（只吃 read depth） | total（正文確認） |
| NestedBD（含 -Long：RECOMB-CG 2025，[10.1007/978-3-031-94928-9_2](https://doi.org/10.1007/978-3-031-94928-9_2)） | 2024 AMB | [s13015-024-00264-4](https://doi.org/10.1186/s13015-024-00264-4) | 已估好的 sc CN profile；BEAST 2 MCMC | total（正文確認） |
| Lazac（ZCNT） | 2023 PLoS CB | [pcbi.1011590](https://doi.org/10.1371/journal.pcbi.1011590) | sc 或 bulk | total |
| DICE | 2024 Life Sci Alliance | [lsa.202402923](https://doi.org/10.26508/lsa.202402923) | sc CN | 可 |
| CNETML | 2023 Genome Biol | [s13059-023-02983-0](https://doi.org/10.1186/s13059-023-02983-0) | bulk multi-sample | 是；CTMC＋Felsenstein pruning |
| sitka | 2023 Peer Community J | [pcjournal.292](https://doi.org/10.24072/pcjournal.292) | scWGS（DLP+） | 否（changepoint marker） |
| CalicoST | 2024 Nat Methods | [s41592-024-02438-9](https://doi.org/10.1038/s41592-024-02438-9) | spatial transcriptomics | CN 推論是 allele-specific（germline SNP phasing 的 BAF）；**建樹只用高信度 LOH 有無**（Startle），gain／loss 不進樹 |

經典基線：MEDICC（2014）、CNT（2016）、CNT-MD、TUSV（2018）。

### E. 多模態整合

| 方法 | 年份／期刊 | DOI | 整合方式 |
|---|---|---|---|
| B-SCITE | 2019 Nat Commun | [s41467-019-10737-5](https://doi.org/10.1038/s41467-019-10737-5) | SCITE likelihood 加上 bulk VAF |
| PhISCS | 2019 Genome Res | [gr.234435.118](https://doi.org/10.1101/gr.234435.118) | sc 二元矩陣＋可選 bulk；ILP／Max-SAT |
| PhylEx | 2023 Nat Commun | [s41467-023-36202-y](https://doi.org/10.1038/s41467-023-36202-y) | bulk DNA likelihood × scRNA cell 指派的邊際化（同一 cell 的 locus 共用同一 node，沒有獨立 pairwise 項）；TSSB＋slice sampler／MH；bulk 無 purity 參數，major／minor CN 外給。Lagergren 組主導、Roth 為共同通訊作者。見 [M06](papers/M06_phylex_2023/README.md) |
| Canopy2 | 2025 Stat Biosci | [s12561-024-09466-1](https://doi.org/10.1007/s12561-024-09466-1) | bulk DNA＋scRNA；MCMC |
| TUSV-int | 2025 Bioinf Adv | [vbaf234](https://doi.org/10.1093/bioadv/vbaf234) | bulk DNA＋scRNA；SNV＋CNA＋SV；ILP。scRNA 只透過 Numbat 的 RNA clone allele-specific CN 進模型，不用 scRNA 上的 SNV 共現 |

W5 也查了 deep learning／generative 型方法（2023–2026），沒有找到能列主選的：CloMu 從候選樹中挑樹，CPhyT-GNN 是 tree embedding，VICTree 只用 CN，PhyloGFN 不是腫瘤專用。

### F. read／molecule 層級連鎖直接進推樹

| 方法 | 年份／期刊 | DOI | 重點與限制 |
|---|---|---|---|
| **TreeClone** | 2019 Ann Appl Stat | [18-AOAS1224](https://doi.org/10.1214/18-AOAS1224) | short-read 相鄰 SNV pair 的 4 類 haplotype read count 進 Bayesian tree likelihood（8 類 read multinomial，含 partially missing reads；pair 間未互相 phase，genotype 以鏡像對稱縮為 10 類）；CN=2 寫死在 likelihood 的「0.5×兩條 allele」項；沒有 multiplicity；程式碼目前連不上。只讀到 arXiv v2，見 [M02](papers/M02_treeclone_2019/README.md) |

| **BitPhylogeny** | 2015 Genome Biol | [s13059-015-0592-6](https://doi.org/10.1186/s13059-015-0592-6) | 每條 read（或每個 cell）的多位點 0/1 pattern 整筆來自同一個 clone，TSSB prior＋Gibbs（加 swap move）同時推 clone 數、clone 參數與樹；clone 可在內部節點。資料是 454 bisulfite methylation 與 single-cell exome；沒有 CN、purity、read count 模型；真實資料無真值樹。Bitbucket code 已失效，GitHub `keyuan/bitphyloR`（2016）。見 [M08](papers/M08_bitphylogeny_2015/README.md) |

這一類共 2 篇。TreeClone 用顯式 pair 計數；BitPhylogeny 用「整條 read 共用一個 clone」隱式約束。2026-10-19 依使用者決定加入 M08。

## 邊界與近似（不計主選）

| 方法 | 原因 |
|---|---|
| PACTION（2022 AMB，[s13015-022-00209-9](https://doi.org/10.1186/s13015-022-00209-9)） | 把已推出的 SNV tree 與 CNA tree 整合，不直接從資料推 topology（W5 列主選，W1／W3 列排除；本表列邊界） |
| Numbat（2022 Nat Biotech） | 主要是 scRNA CN calling，phylogeny 只是迭代流程中的模組；haplotype-aware CN 的做法值得借用 |
| ALPACA（2025 Nature） | 給定 SNV tree 推 clone-specific allele-specific CN |
| Meltos、TreeHarmonizer、Goretsky AACR 2026 #4134 | 把 SV 放到既有樹上，或給定樹之後做 SV timing |
| DeCiFer | descendant cell fraction clustering，不出樹；但 multiplicity 處理與 PhyClone 高度相關 |
| LongPhase-TO（2026-09 bioRxiv） | longphase 家族的 somatic haplotype 重建，不推樹；要持續追蹤 |
| OncoPhase、Demeulemeester 2022 | 用 phasing 估 prevalence 或檢驗 ISA，不推樹 |
| LongSom、SomaticHaplotype、Baker 2026 | clustering 或局部 haplotype，沒有完整有向 phylogeny |
| cfClone（Roth lab，2026） | 用 haplotype-specific 訊號追蹤 cfDNA 中的 clone，但 clone 結構是給定的，不推 topology（W7） |
| fastppm（ISMB 2025，[btaf235](https://doi.org/10.1093/bioinformatics/btaf235)） | 只對固定 topology 做 regression 計分；可考慮借來加速 PhyClone 的 tree 計分（推論） |

完整排除清單見各 worker 檔的「近似與排除」。

## Novelty 邊界（分析推論）

依 W1、W3、W4 的交叉結果，截至 2026-10-16：

1. **「在 tree likelihood 中使用同一 read 上 SNV 共現」不是 novelty**：TreeClone（2019）已經做過，限 short-read 與 CN=2。
2. **haplotype-specific CN 推樹已有**：MEDICC2、CNETML、Numbat 都這樣做（CalicoST 的 CN 是 allele-specific，但樹只用 LOH 有無），SNV 不在它們的 likelihood 裡，或只是外加。
3. **TUSV-ext 把 SNV、SV phase 到 allele**，但 phase 是 latent 變數，而且 allele 是 major／minor 排序，不是 germline haplotype。longphase 的 HP 可以把它變成觀測值，並修正 mirrored allelic imbalance 的身分混淆。
4. **Pharming 的 (x,y,w,z) genotype** 在狀態空間上與「HP1/HP2 CN＋multiplicity」幾乎一一對應，但：likelihood 只用 (w+z)/(x+y)，read 不分 haplotype；SNV 落在哪條 haplotype 只靠 CN 演化約束間接推出；評估指標都是 modulo multiplicity and allele specificity，等於沒驗證這兩者；擴展到 bulk 只在 Discussion 提一句，沒有實作。HP 拆開計數後 w、z 才能分別識別，這正是它缺的一塊（推論）。
5. **沒有找到任何方法同時做到這四點**：
   - PhyClone 式 bulk SNV＋CN＋purity likelihood；
   - long-read 上 SNV pair 的共現 likelihood；
   - SNV 經 phase set 指派到 HP1/HP2，再配合 haplotype-specific CN，約束 multiplicity 與 CN timing；
   - 以 SMC／PG 推 topology。

可主張的是這幾項的**聯合模型**，不能單獨主張「首次用 read phasing 推腫瘤樹」。

## Benchmark 與評估指標（供 `evaluation_v1.md`）

W5 整理了 11 篇 benchmark／review，完整表格見 W5 檔。對本 repo 最有用的有三點：

- **主指標**：不依賴 clone 編號的 pairwise 祖先關係。
  - SMC-Het 的 ADM Pearson correlation（Salcedo 2020 Nat Biotech，[10.1038/s41587-019-0364-z](https://doi.org/10.1038/s41587-019-0364-z)）。
  - Pairtree 的 relationship reconstruction error（四類關係的 JSD）。
  - 兩者跟 `evaluation_v1.md` 的四類關係矩陣一致。
- **輔助指標**：
  - VAF reconstruction loss：沒有 truth 時，比較加入 long-read 特徵前後的 fit。
  - MLTED、CASet、DISC：與 HCC1395 參考樹比較。
  - MP3：引入 haplotype-specific loss 之後使用。
  - linear 與 branching topology 分層報告（Tomlinson 2019）。
- **新的評估論點**：Satas et al.（WABI 2026）證明 single-cell 常用的 min-flip 目標函數在統計上不一致；SCOUT 是合成 WGS benchmark（W7）。
- **缺口**：沒有找到中立的 single-cell tree 或 CN phylogeny benchmark，現有比較都寫在方法論文自己的章節裡。
- **2026-10-18 補查**（[W8](workers/W8_benchmark_update_2026-10-18.md)）：2025-06 後沒有新的中立 tree benchmark。新資源是 Liu et al. 2026 Nat Commun（Kolmogorov 組）的 ONT 小鼠黑色素瘤 23 subline，有已知樹，可混成 long-read pseudo-bulk 測資。EMulSI-Phy poster 比較了 PhyClone，但只有摘要。

`tX_nY` 的 nominal purity 只能當 sanity check，不是 ground truth。

## 建議精讀順序

1. **PhyClone**：基線，已有正式版。
2. **TreeClone**：read pair 共現 likelihood 的直接起點與差異界定。
3. **Pharming**：haplotype CN＋multiplicity 的 genotype 表示法。
4. **TUSV-ext**：phased SNV／SV／CN 的 ILP，可對接 longphase 的 HP。
5. **PhylEx**：在 bulk likelihood 上加單細胞共現資訊的範式（Lagergren 組，Roth 共同通訊）；換成 read 層級共現需要改的四項見 M06。
6. **Pairtree／Orchard**：主要 bulk 競品與 benchmark 指標來源。
7. **MEDICC2／CNETML**：haplotype CN 沿樹轉移的模型，可作為 CN-only baseline。
8. **SCARLET／ConDoR**：CN 約束 SNV loss 的作法，可升級成 haplotype 層級的約束。
9. **Salcedo 2020**：評估指標。

## 待核與已知缺口

- **推論細節核對**：Pharming、TUSV-ext、PhylEx 已在 M04–M06 讀正文確認。COMPASS、ConDoR、CalicoST、DEVOLUTION、SiCloneFit、CellPhy、DelSIEVE、PICTograph、CALDER、BAMSE、SCICoNE、NestedBD 已讀正文核對，結果見 [W6_verification.md](workers/W6_verification.md)；表中已依此更正。W2／W3／W5 原檔保留原描述，衝突處以本表與 W6 為準（例如 CALDER 是 MILP、CalicoST 只用 LOH 建樹）。
- **會議論文補查（W7）**：RECOMB 2025、ISMB 2025／2026、ECCB 2026、WABI 2025／2026、RECOMB-CG 2025／2026 已逐篇看過目錄；RECOMB 2026 與 RECOMB-CCB 只部分覆蓋；bioRxiv 2025-06 到 2026-10 的 6 個 category 已用關鍵字與 lab 作者掃過；medRxiv 沒掃。bulk 端沒有找到新的 SNV＋CN 推樹方法。
- **其他不確定處**：
  - 程式碼位置已查明：MEDICC2 論文寫 bitbucket.org/schwarzlab/medicc2，GitHub schwarzlab-ccb/medicc2 是同團隊目前維護的 repo（由轉址推斷）；PACTION 在 github.com/elkebir-group/paction（W5 寫的 raphael-group 是錯的 org）；Canopy2 在 github.com/annweideman/canopy2。
  - PHALCON、Phyllochron 還沒有正式版。
- **逐篇 dossier**：精讀清單前 5 篇已建立，見下節。其餘方法沒有下載 PDF。
- **版本限制**：TreeClone 只讀 arXiv v2（期刊 PDF 被擋）；Pharming 只讀 bioRxiv v1（JCB 正式版付費）；Sc-TUSV-ext 只讀 bioRxiv v1 與 JCB 摘要；TUSV-ext 的完整 ILP（補充材料 S1）未讀。

## 逐篇 dossier

每篇目錄有 PDF（或摘要）、`paper.txt` 與閱讀筆記；頁碼指本地 PDF 實體頁。

| ID | 方法 | 本地版本 | 重點 |
|---|---|---|---|
| [M01](papers/M01_phyclone_2025/README.md) | PhyClone | 出版社正式版 10 頁＋補充 28 頁；另存 bioRxiv v1 對照 | 正式版與 preprint 差異、multiplicity 邊際化、outlier model、PG／SMC |
| [M02](papers/M02_treeclone_2019/README.md) | TreeClone | arXiv v2 30 頁（期刊版未取得） | mutation-pair read likelihood、CN=2 寫死之處、推廣到 long read 的方式 |
| [M04](papers/M04_pharming_2026/README.md) | Pharming | bioRxiv v1 29 頁 | (x,y,w,z) 狀態空間、JCTI、與 HP＋multiplicity 的接點 |
| [M05](papers/M05_tusv_ext_2022/README.md) | TUSV-ext（附 Sc-TUSV-ext、TUSV-int） | 出版社正式版 9 頁 | ILP、latent allele phasing、改用觀測 HP 的簡化 |
| [M06](papers/M06_phylex_2023/README.md) | PhylEx | 出版社正式版 16 頁＋補充 19 頁 | bulk × scRNA likelihood 合成、改成 read 層級共現要改的項 |
| [M08](papers/M08_bitphylogeny_2015/README.md) | BitPhylogeny | Europe PMC 全文 XML（PDF 被擋，補充檔未讀） | read pattern 當抽樣單位、TSSB 聯合推 clone 與樹、搬到 ONT＋HP 的 5 個問題 |

