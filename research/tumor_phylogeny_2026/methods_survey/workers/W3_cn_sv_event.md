# W3：以 CN／SV event 為主要訊號的 tumor phylogeny 重建方法

> 面向：以 copy number（含 allele-specific／haplotype-specific CN、LOH、WGD）或 SV 為主要 phylogenetic marker 的推樹方法（bulk 與 single-cell 都算）。
> 查詢日：2026-10-16。GitHub star 數是 2026-10-16 透過 GitHub API 查到的。
> 標記規則：「摘要／方法」是論文本身的描述；「推論」是本 worker 的判斷，尚未逐行核對原始碼。

## 搜尋紀錄

WebSearch（standard／extended）：
- `Lazac copy number phylogeny Schmidt Raphael`
- `DICE distance-based reconstruction single-cell copy number phylogenies Bansal`
- `NestedBD Bayesian inference phylogenetic trees single-cell copy number birth-death`
- `CNETML maximum likelihood phylogeny copy number alterations multiple samples low-pass`
- `SCICoNE single-cell copy number calling event history reconstruction Kuipers`
- `CONET copy number event tree model single-cell Bioinformatics Markowska`
- `MEDALT single-cell copy number lineage tracing Genome Biology`
- `sitka cancer phylogenetic tree inference at scale from 1000s of single cell genomes`
- `TUSV-ext reconstructing tumor clonal lineage trees SNV copy number structural variations`
- `MEDICC2 whole-genome doubling aware copy number phylogenies Kaufmann Genome Biology`
- `copy number weighted aberrations Zeira Raphael Bioinformatics 2020 CNT`
- `haplotype-specific copy number phylogeny single-cell 2024 2025 method allele-specific tree inference`
- `bioRxiv 2025 copy number aberration phylogeny single-cell new method tree reconstruction breakpoints`
- `structural variant based tumor phylogeny reconstruction long-read sequencing method`
- `Sc-TUSV-ext single-cell clonal lineage inference SNV CNA SV published`
- `Sc-TUSV-Ext Journal of Computational Biology 2025 Bristy Fu Schwartz 10.1089/cmb.2024.0613`
- `Paction parsimonious clone tree integration cancer Sashittal Algorithms for Molecular Biology`
- `ALPACA allele-specific copy number given phylogenetic tree TRACERx Grigoriadis`
- `CNRein evolution-aware deep reinforcement learning single-cell copy number calling published`
- `whole-genome doubling single-cell copy number phylogeny 2025 method tree inference WGD timing`
- `NestedBD-Long longitudinal single-cell copy number phylogeny Liu Nakhleh published`
- `Henri Schmidt Raphael 2025 copy number phylogeny bioRxiv`
- `Meltos multi-sample tumor phylogeny structural variants Ricketts Bioinformatics DOI`
- `SVclone inferring structural variant cancer cell fraction Cmero Nature Communications`
- `"copy number" tumor phylogeny 2026 method haplotype-specific OR allele-specific bulk multi-sample`
- `DEVOLUTION phylogenetic reconstruction aneuploid cancers multiregional genotyping`
- `CalicoST allele-specific copy number aberrations tumor phylogeography spatial transcriptomics Nature Methods`
- `SCARLET single-cell tumor phylogeny copy-number constrained mutation losses Cell Systems Satas`
- `COMPASS joint copy number and SNV tumor phylogeny targeted single-cell Sollier Nature Communications`
- `linear-time algorithm copy number transformation problem Zeira Zehavi Shamir Journal of Computational Biology`
- `TUSV deconvolution phylogeny inference structural variations tumor Eaton Bioinformatics 2018`
- `benchmark copy number phylogeny methods single-cell MEDICC2 MEDALT sitka Lazac comparison 2024 2025`
- `tumor phylogeny copy number "long-read" OR "haplotype-resolved" phasing clone tree inference 2025 2026 bioRxiv`
- `phylogeny from structural variants single-cell OR bulk tumor "breakpoint" lineage tree inference method 2023 2024 2025 ...`
- `allele-specific copy number single-cell phylogeny maximum likelihood 2024 2025 new tool ...`
- `Schwarz 2014 "Phylogenetic quantification of intra-tumour heterogeneity" MEDICC ...`
- `"Phylogenetic copy-number factorization of multiple tumor samples" Zaccaria ...`

WebFetch 核對過的官方頁面：PMC10662746（Lazac）、PMC9236577（TUSV-ext）、PMC12571511（TUSV-int）、PMC7355291（WCND）、PMC8919608（PACTION）、PMC9185904（CONET）、PMC10283241（CNETML）、PMC7901082（MEDALT）、PMC6022719（TUSV）、PMC7451135（SCARLET）、academic.oup.com btaf072（SCICoNE）、peercommunityjournal.org pcjournal.292（sitka）、life-science-alliance.org e202402923（DICE）、bioRxiv 2025.09.16.676596（LoPhy）、bioRxiv 2025.03.17.643834（NestedBD-Long）。
GitHub star 數：`api.github.com/repos/<repo>` 與 `gh api`。

## 主選候選

| 方法名 | 論文標題 | 第一作者 et al. | 年份 | 期刊/preprint | DOI(連結) | 輸入資料 | 輸出樹類型 | 模型與推論 | 是否處理 CN／multiplicity／WGD | 程式碼(URL, stars) | 驗證狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MEDICC2（舊調查已收，這裡為完整性再列） | MEDICC2: whole-genome doubling aware copy-number phylogenies for cancer evolution | Kaufmann et al. | 2022 | Genome Biology 23:241（preprint bioRxiv 2021.02.28.433227） | [10.1186/s13059-022-02794-9](https://doi.org/10.1186/s13059-022-02794-9) | bulk multi-sample 或 single-cell；haplotype-specific CN | sample／cell 的 phylogeny（含 ancestral genome） | combinatorial：minimum-event distance（FST，含 WGD，linear time）+ distance-based 建樹 | CN：是（haplotype-specific、LOH）；WGD：是（clonal 與 subclonal）；SNV multiplicity：否 | [schwarzlab-ccb/medicc2](https://github.com/schwarzlab-ccb/medicc2)（GitHub 上 10 stars；主 repo 可能另在 Bitbucket，未核對） | verified |
| WCND（CNT distance 家族） | Copy number evolution with weighted aberrations in cancer | Zeira et al. | 2020 | Bioinformatics 36(Suppl 1):i344（ISMB 2020） | [10.1093/bioinformatics/btaa470](https://doi.org/10.1093/bioinformatics/btaa470) | bulk 或 single-cell；total 或 allele-specific CN（實例用 CHISEL 的 A／B allele） | clone／cell phylogeny | combinatorial：weighted CND（constraint matrix 為 totally unimodular，可用 LP 解）+ minimum spanning arborescence 或 NJ | CN：是（事件依長度、位置、類型加權）；WGD：否（推論）；multiplicity：否 | [raphael-group/WCND](https://github.com/raphael-group/WCND)（4） | verified |
| MEDALT | MEDALT: single-cell copy number lineage tracing enabling gene discovery | Wang F. et al. | 2021 | Genome Biology 22:70 | [10.1186/s13059-021-02291-5](https://doi.org/10.1186/s13059-021-02291-5) | single-cell DNA，或由 scRNA 推得的 CN（inferCNV）；integer CN，論文沒寫明是 total 還是 allele-specific | cell lineage tree（rooted arborescence；cell 是節點，沒有未觀測到的 ancestor） | combinatorial：Minimal Event Distance + Edmonds arborescence；另有 lineage speciation analysis | CN：是（0 copy 不可恢復）；WGD：否；multiplicity：否 | [KChen-lab/MEDALT](https://github.com/KChen-lab/MEDALT)（21） | verified |
| CONET | CONET: copy number event tree model of evolutionary tumor history for single-cell data | Markowska et al. | 2022 | Genome Biology 23:128（preprint bioRxiv 2021.04.23.441204） | [10.1186/s13059-022-02693-z](https://doi.org/10.1186/s13059-022-02693-z) | single-cell WGS（per-bin、per-breakpoint 訊號）；total CN | CN event tree（節點是 breakpoint pair） | Bayesian + regularized MCMC；cell 事後以 ML 掛到節點 | CN：只建模事件的有／無，刻意不建模確切 CN 變化，CN 事後才 call；finite sites；WGD：否 | [szczurek-lab/CONET](https://github.com/szczurek-lab/CONET)（2） | verified |
| SCICoNE | Single-cell copy number calling and event history reconstruction | Kuipers et al. | 2025 | Bioinformatics 41(3):btaf072（preprint bioRxiv 2020.04.28.065755） | [10.1093/bioinformatics/btaf072](https://doi.org/10.1093/bioinformatics/btaf072) | single-cell 淺層 WGS read count matrix；CN 推論上是 total（論文沒寫明） | CN event tree（節點帶 segment amp／del event） | Bayesian + MCMC（同時抽 tree 與 event vector），同時做 CN calling | CN：是（允許重疊、巢狀、recurrent event）；可設 root ploidy（例如 tetraploid）來表示 WGD；multiplicity：否 | [cbg-ethz/SCICoNE](https://github.com/cbg-ethz/SCICoNE)（29） | verified |
| NestedBD（含 NestedBD-Long） | NestedBD: Bayesian inference of phylogenetic trees from single-cell copy number profiles under a birth-death model | Liu Y. et al. | 2024 | Algorithms for Molecular Biology（2024 年 4 月；preprint bioRxiv 2022.01.16.476510） | [10.1186/s13015-024-00264-4](https://doi.org/10.1186/s13015-024-00264-4) | single-cell CN profile；推論為 total CN | 有 branch length 的 cell phylogeny，含 ancestral CN | Bayesian + MCMC（BEAST 2 package），CN 採 nested birth-death model | CN：是（bin 之間獨立）；WGD：未見；multiplicity：否 | [Androstane/NestedBD](https://github.com/Androstane/NestedBD)（6） | verified（NestedBD-Long 是 bioRxiv [10.1101/2025.03.17.643834](https://doi.org/10.1101/2025.03.17.643834)，Liu & Nakhleh；Springer 章節 10.1007/978-3-031-94928-9_2 推測是 RECOMB-CG 2025，標為 partially verified） |
| Lazac（ZCNT） | A zero-agnostic model for copy number evolution in cancer | Schmidt et al. | 2023 | PLoS Comput Biol 19(11):e1011590（preprint bioRxiv 2023.04.10.536302） | [10.1371/journal.pcbi.1011590](https://doi.org/10.1371/journal.pcbi.1011590) | single-cell 或 bulk 的 integer CN profile（total） | cell／clone phylogeny（large parsimony） | combinatorial：ZCNT distance 是 metric，small parsimony 可在 polynomial time 解，再做 tree search | CN：是（允許 0 copy 被改變，作者承認這不符合生物現實）；WGD：否；multiplicity：否 | [raphael-group/lazac-copy-number](https://github.com/raphael-group/lazac-copy-number)（6） | verified |
| DICE | DICE: fast and accurate distance-based reconstruction of single-cell copy number phylogenies | Weiner et al. | 2024 | Life Science Alliance 8(3):e202402923（preprint bioRxiv 2024.06.03.597037） | [10.26508/lsa.202402923](https://doi.org/10.26508/lsa.202402923) | single-cell CN（benchmark 中有 allele-specific 就給 allele-specific） | cell phylogeny | distance-based：breakpoint 或 standard root distance + balanced minimum evolution | CN：是；WGD：否；multiplicity：否 | [samsonweiner/DICE](https://github.com/samsonweiner/DICE)（2） | verified |
| CNETML | CNETML: maximum likelihood inference of phylogeny from copy number profiles of multiple samples | Lu B. et al. | 2023 | Genome Biology 24:144（preprint bioRxiv 2022.03.18.484889） | [10.1186/s13059-023-02983-0](https://doi.org/10.1186/s13059-023-02983-0) | bulk multi-sample（含 longitudinal）low-pass WGS；total 或 haplotype-specific CN | 有時間尺度的 sample phylogeny（node age、mutation rate） | ML：per-site 的 haplotype-specific CN 用 continuous-time Markov chain，Felsenstein pruning + IQ-TREE 式 tree search | CN：是（輸入 total CN 時，haplotype 狀態當 latent 邊際化）；WGD：未見；multiplicity：否 | [ucl-cssb/cneta](https://github.com/ucl-cssb/cneta)（5） | verified |
| sitka | Cancer phylogenetic tree inference at scale from 1000s of single cell genomes | Salehi et al. | 2023 | Peer Community Journal 3:e63（preprint bioRxiv 2020.05.06.058180） | [10.24072/pcjournal.292](https://doi.org/10.24072/pcjournal.292) | single-cell WGS（DLP+）CN；SNV 在建樹後 call | cell phylogeny（可擴展到上萬個 cell） | Bayesian + MCMC；sitka transformation 把 CN 編成 changepoint binary marker | CN：是（以 changepoint 間接編碼）；WGD：否；multiplicity：否 | [UBC-Stat-ML/sitkatree](https://github.com/UBC-Stat-ML/sitkatree)（3） | verified |
| TUSV-ext（含 Sc-TUSV-ext、TUSV-int） | Reconstructing tumor clonal lineage trees incorporating single-nucleotide variants, copy number alterations and structural variations | Fu X. et al. | 2022 | Bioinformatics 38(Suppl 1):i125（ISMB 2022） | [10.1093/bioinformatics/btac253](https://doi.org/10.1093/bioinformatics/btac253) | bulk multi-sample WGS；SNV + allele-specific segmental CN + SV breakpoint | clone tree（binary，root 是 normal）+ clone 比例 | ILP，以 coordinate descent 交替解 U（frequency）與 C（clone CN）；L1 fit + CN evolution 懲罰項 | CN：是（allele-specific，並把 breakpoint／SNV phase 到 allele）；SNV／SV 採 Dollo 式約束，只能經由 allele loss 消失；variant 可隨 segment 一起 duplicate，是一種 multiplicity；WGD：未見 | [CMUSchwartzLab/TUSV-ext](https://github.com/CMUSchwartzLab/TUSV-ext)（21） | verified（家族：Sc-TUSV-ext，J Comput Biol 32(8):723（2025），DOI 10.1089/cmb.2024.0613，DOI 由 SAGE 頁面與 DBLP 交叉核對，[repo](https://github.com/CMUSchwartzLab/Sc-TUSV-ext) 3；TUSV-int，Bioinformatics Advances 5(1):vbaf234（2025），[10.1093/bioadv/vbaf234](https://doi.org/10.1093/bioadv/vbaf234)，[repo](https://github.com/CMUSchwartzLab/TUSV-INT) 3） |
| DEVOLUTION | DEVOLUTION—A method for phylogenetic reconstruction of aneuploid cancers based on multiregional genotyping data | Andersson N. et al. | 2021 | Communications Biology 4:1103 | [10.1038/s42003-021-02637-6](https://doi.org/10.1038/s42003-021-02637-6) | bulk multi-region；CN event + SNV（需要已知 clone fraction） | subclone phylogeny | combinatorial：先做 subclonal deconvolution，再以 event matrix 建 parsimony 樹 | CN：是（為 aneuploid、SNV 少的腫瘤設計）；WGD：未見；multiplicity：否 | 未查到 GitHub（unverified） | verified |
| COMPASS | COMPASS: joint copy number and mutation phylogeny reconstruction from amplicon single-cell sequencing data | Sollier et al. | 2023 | Nature Communications（preprint bioRxiv 2022.01.06.475205） | [10.1038/s41467-023-40378-8](https://doi.org/10.1038/s41467-023-40378-8) | targeted single-cell（Tapestri amplicon）；SNV + CNA（含 CNLOH） | 同時含 SNV 與 CNA 事件的 event tree | Bayesian + MCMC（SCITE 系的 tree move） | CN：是（CNA 事件與 CNLOH）；SNV 可因 CNLOH／deletion 而 loss；WGD：否 | [cbg-ethz/COMPASS](https://github.com/cbg-ethz/COMPASS)（26） | verified |
| CalicoST | Inferring allele-specific copy number aberrations and tumor phylogeography from spatially resolved transcriptomics | Ma C. et al. | 2024 | Nature Methods 21:2239（preprint bioRxiv 2024.03.09.584244） | [10.1038/s41592-024-02438-9](https://doi.org/10.1038/s41592-024-02438-9) | spatial transcriptomics（Visium），以 phased SNP 的 BAF 加上 RDR | clone phylogeny + spatial phylogeography | HMRF/HMM 推 allele-specific CN clone，再以 CNA／LOH 為 marker 建樹 | CN：是（allele-specific，能偵測 copy-neutral LOH 與 mirrored subclonal CNA）；WGD：未見 | [raphael-group/CalicoST](https://github.com/raphael-group/CalicoST)（51） | verified |

### 逐篇重點

**MEDICC2**
- 核心創新：把 minimum-event distance 擴充到 WGD，並能在 linear time 內計算。可以重建 ancestral genome、找出 parallel event，也能為 WGD 做相對 timing。
- 假設：不採用 infinite sites（允許 homoplasy），也不把相鄰 locus 當成獨立。輸入必須是 haplotype-specific CN；作者用 multi-sample phasing 揭露 mirrored subclonal allelic imbalance（MSAI）。
- 與本研究的關聯（推論）：在所有方法中，它最直接需要「haplotype-consistent 的 phasing」。longphase 的 HP1／HP2 phase set 可以取代 statistical phasing，減少 MSAI 被誤判成 parallel event 的機會。不過它不吃 SNV，也沒有 multiplicity；用在 PhyClone 時比較適合當成 CN 事件層的外部參考樹，或拿來借用它的 WGD-aware event 距離。

**WCND（CNT 家族）**
- 核心創新：CNT／CND 是把一個 CN profile 經由 segmental amp／del 轉成另一個所需的最少事件數。WCND 讓不同事件有不同權重（機率），並且利用 total unimodularity 讓計算維持 tractable。
- 假設：segmental 事件彼此獨立地加權；建樹靠 distance + arborescence 或 NJ，不是完整的 likelihood 模型。
- 關聯：可以吃 allele-specific CN，所以 long-read 的 haplotype-specific segment 可以直接放進去（推論）。

**MEDALT**
- 核心創新：用 cell 當節點建 MED-based rooted arborescence，並以 lineage speciation analysis 找出和 fitness 有關的 CNA。
- 假設：沒有 unobserved ancestor；把 0 copy 當成 absorbing state；屬於 combinatorial、非機率模型。
- 關聯：不適合 bulk 單樣本；DICE 的 benchmark 顯示它在 noisy data 下表現差（normalized RF 0.861）。對 PhyClone 的參考價值低（推論）。

**CONET**
- 核心創新：tree 的節點直接是 breakpoint pair（CN event），per-breakpoint 與 per-bin 兩種訊號一起放進 likelihood。
- 假設：finite sites；只建模事件「有／無」，不建模 CN 數值。
- 關聯：「節點就是 breakpoint event」這個設計，可以借用到 long-read 的 phased breakpoint：每個 breakpoint 帶 HP 標記，同一 read 跨過兩端時會更可信（推論）。

**SCICoNE**
- 核心創新：先偵測 breakpoint 切出 segment，再用 MCMC 同時推 CN event tree 與每個 cell 的 CN，以演化關係對低深度 cell 去雜訊。
- 假設：事件可以重疊、巢狀、重複發生；root ploidy 可以設定。
- 關聯：做法上和 PhyClone 的 SMC／PG 同屬 tree-space sampler，event-vector 的設計可以參考（推論）。只支援 single-cell。

**NestedBD／NestedBD-Long**
- 核心創新：在 BEAST 2 框架下為 CN 建立 birth-death 模型，同時推 topology、branch length 與 branch-specific rate。NestedBD-Long 加進 longitudinal sampling time，作者指出時間資訊能顯著提升準確度。
- 假設：bin 獨立、cells 在單一時間點取樣（Long 版放寬了這一點）。
- 關聯：bulk ONT 的 purity series 不是時間序列，所以 Long 版的時間資訊用不上（推論）。

**Lazac（ZCNT）**
- 核心創新：放寬 CNT 對 0 copy 的限制，得到一個 metric 距離；small parsimony 因此有 polynomial 解，large parsimony 據作者表示比 sitka、MEDICC2 快 100 倍以上。
- 假設：0 copy 可以被 amp，作者承認這不符合生物現實；只用 total CN。
- 關聯：只吃 total CN，沒有使用 haplotype 資訊；適合當 fast baseline（推論）。

**DICE**
- 核心創新：在 breakpoint 或 CN profile 上用 root distance，再以 balanced minimum evolution 建樹。在作者的 noisy benchmark 裡，DICE-star 的 normalized RF 是 0.353，MEDICC2 是 0.584、Lazac 0.763、sitka 0.808（作者自評，有利益衝突）。
- 假設：純 distance-based，不推 ancestral state 的機率。
- 關聯：概念簡單，可以拿來檢查 long-read CN 樹的穩定性；但它不處理 bulk 的 clonal mixture（推論）。

**CNETML**
- 核心創新：第一個從 total CN（low-pass WGS）同時以 ML 推出 topology、node age 與 mutation rate 的方法。底層是 haplotype-specific CN 的 Markov 模型；輸入 total CN 時，haplotype 被邊際化。
- 假設：site 獨立、global clock。作者指出 copy-neutral 事件（cnLOH、MSAI）超過約 10% 時，只用 total CN 會不準。
- 關聯：這個 Markov 模型可以直接改寫成 PhyClone 中 CN 狀態沿 tree 的轉移 prior。long-read 的 haplotype-specific CN 正好解決它自己指出的 copy-neutral 弱點（推論）。

**sitka**
- 核心創新：sitka transformation 把 CN 的位點相依性改寫成 changepoint marker，讓 MCMC 可以擴展到 10^4 個 cell；建樹之後再用樹做 SNV calling。
- 假設：只把 changepoint 的有／無當作 marker，直接的 CN 數值資訊被簡化掉。
- 關聯：作者群包含 Andrew Roth（PhyClone 的作者），和 PhyClone 屬於同一個生態系。它只支援 single-cell，所以對 bulk ONT 的直接用途有限（推論）。

**TUSV-ext（家族）**
- 核心創新：把 SNV、allele-specific CNA、SV breakpoint 放進同一個 ILP clone tree。breakpoint 會被 phase 到 allele，一個 SV 的兩個 breakpoint 必須落在同一條 edge 上，SNV 只能隨 segment 被 duplicate 或 loss。
- 假設：SNV 與 SV 都用 Dollo 式約束；tree 是 binary；超過約 9 個 clone 時 runtime 會失控；SNV 和 breakpoint 太多時要先 subsample。
- 關聯：**這是唯一原生把 breakpoint 和 SNV phase 到 allele 的推樹方法**。longphase 的 HP tag 加上 phased SV breakpoint（例如 Severus 的 HP 輸出）可以把「phase 到哪個 allele」從 latent 變成 observed，大幅縮小 ILP 的搜尋空間（推論）。缺點是它需要 multi-sample deconvolution；我們的 purity series 本質上只是同一組 clone 和 normal 的不同混合比例，資訊增量有限（推論）。

**DEVOLUTION**
- 核心創新：專門處理 aneuploid、SNV 少的腫瘤（兒童腫瘤），在 multi-region bulk 裡把 CN 事件和 SNV 一起拿來做 deconvolution 並建樹。
- 假設：需要事先知道每個事件的 clone fraction，屬於 parsimony 類方法。
- 關聯：以 CN event 補足 SNV 稀少的問題，在概念上和「用 haplotype CN 約束 clone」相近（推論）。

**COMPASS**
- 核心創新：同時建 SNV 與 CNA（含 CNLOH）event tree，CNLOH 可以解釋 SNV 為什麼不見。
- 假設：只適用 targeted panel 的 single-cell（Tapestri）；CNA 數量少。
- 關聯：「CNLOH 造成 SNV loss」這個建模方式，和 PhyClone 想用 haplotype 判斷 multiplicity 與 loss 是同一類問題（推論）。

**CalicoST**
- 核心創新：從 spatial transcriptomics 推出 allele-specific CN，並以 LOH 和 mirrored CNA 當 marker 建 clone phylogeny，再結合空間位置。
- 假設：phasing 來自 reference panel 的 population phasing，加上空間平滑。
- 關聯：作者明確指出只用 total CN 會把 clone 和 phylogeny 推錯。這是「haplotype 資訊會改變 topology」的直接證據；long-read 的 read-based phasing 可以取代 population phasing（推論）。

## 經典基線（不計主選）

| 方法 | 論文 | 年份／期刊 | DOI | 備註 |
|---|---|---|---|---|
| MEDICC | Phylogenetic Quantification of Intra-tumour Heterogeneity（Schwarz et al.） | 2014, PLoS Comput Biol 10(4):e1003535 | [10.1371/journal.pcbi.1003535](https://doi.org/10.1371/journal.pcbi.1003535) | 最早的 allele-specific CN minimum-event distance（FST），會順便推 major/minor allele 的 phasing |
| CNT（linear-time） | A Linear-Time Algorithm for the Copy Number Transformation Problem（Shamir, Zehavi, Zeira） | 2016, CPM（LIPIcs 54） | [10.4230/LIPIcs.CPM.2016.16](https://doi.org/10.4230/LIPIcs.CPM.2016.16) | 給出 CNT distance 的 linear-time 算法；沒查到 JCB 期刊版（unverified） |
| CNT-MD | The copy-number tree mixture deconvolution problem…（Zaccaria et al.）；期刊版為 Phylogenetic copy-number factorization of multiple tumor samples | 2017 RECOMB；2018 J Comput Biol 25(7):689 | RECOMB 版 [10.1007/978-3-319-56970-3_20](https://doi.org/10.1007/978-3-319-56970-3_20)；JCB 版 DOI unverified | 從 multi-sample bulk 同時做 deconvolution 與 CN tree |
| TUSV | Deconvolution and phylogeny inference of structural variations in tumor genomic samples（Eaton et al.） | 2018, Bioinformatics 34(13):i357 | [10.1093/bioinformatics/bty270](https://doi.org/10.1093/bioinformatics/bty270) | 第一個以 SV + CNA 推 bulk tumor phylogeny 的方法，對 breakpoint 採 perfect phylogeny；[jaebird123/tusv](https://github.com/jaebird123/tusv)（9） |

## 近似與排除

| 方法 | DOI | 排除原因 |
|---|---|---|
| ALPACA（Pawlik, Grigoriadis et al., Nature 2025, "Clone copy number diversity is linked to survival in lung cancer"） | [10.1038/s41586-025-09398-w](https://doi.org/10.1038/s41586-025-09398-w) | **給定 topology 推事件**：以 SNV 建出的 tree 為輸入，推 clone-specific、allele-specific CN，不推 topology。可作為「SNV tree + haplotype CN」的下游對照。[McGranahanLab/ALPACA-model](https://github.com/McGranahanLab/ALPACA-model)（14） |
| PACTION（Sashittal, Zaccaria, El-Kebir, AMB 2022） | [10.1186/s13015-022-00209-9](https://doi.org/10.1186/s13015-022-00209-9) | **整合兩棵已給定的 tree**（SNV clone tree + CNA clone tree）。輸出的是 refine 過的整合 tree，不是從資料直接推 topology，因此屬於近似，不計主選 |
| Meltos（Ricketts et al., Bioinformatics 2020） | [10.1093/bioinformatics/btz737](https://doi.org/10.1093/bioinformatics/btz737) | 以 SNV tree 作 guide，把 SV call 放到既有 tree 上，主要是 SV 放置與 VAF 估計 |
| SVclone（Cmero et al., Nat Commun 2020） | [10.1038/s41467-020-14351-8](https://doi.org/10.1038/s41467-020-14351-8) | 只估 SV breakpoint 的 CCF 並做 clustering，不推 tree |
| HATCHet（Zaccaria & Raphael, Nat Commun 2020）／HATCHet2 | [10.1038/s41467-020-17967-y](https://doi.org/10.1038/s41467-020-17967-y)（HATCHet2 DOI 未查） | 只做 allele-specific、clone-specific CN calling 與 WGD 偵測，不推樹 |
| CHISEL／SIGNALS／Wakhan／Severus | 未逐一核對 DOI（依規則屬純 calling，unverified） | 只做 haplotype-specific CN 或 SV calling。SIGNALS 的論文另外用 MEDICC2 或 sitka 建樹，樹不是它自己的貢獻 |
| CNRein（Ivanovic & El-Kebir, Genome Biol 2025） | [10.1186/s13059-025-03553-2](https://doi.org/10.1186/s13059-025-03553-2) | evolution-aware 的 haplotype-specific CN calling（RL + CNN）。演化模型只當 calling 的正則化，主要輸出是 CN，不是 tree（邊界） |
| Numbat（Gao et al., Nat Biotechnol 2023） | [10.1038/s41587-022-01468-y](https://doi.org/10.1038/s41587-022-01468-y) | 用 scRNA 做 haplotype-aware CNV calling；clone phylogeny 是迭代過程的副產物，主要貢獻是 calling（邊界） |
| SCARLET（Satas et al., Cell Syst 2020）／ConDoR | [10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001)（ConDoR 未核對） | 以 SNV 為 marker、用 CN 約束 SNV loss，主訊號是 SNV，應歸 SNV／single-cell worker；這裡只是 cross-ref |
| LoPhy（scaOrchard；Kulman, Morris, Kuang, bioRxiv 2025） | [10.1101/2025.09.16.676596](https://doi.org/10.1101/2025.09.16.676596) | 對 longitudinal targeted scDNA 同時建 SNV + CNA tree，有推 topology，但目前只是 preprint、SNV 與 CN 並重，所以列邊界。[ethanumn/LoPhy](https://github.com/ethanumn/LoPhy)（0） |
| doubleTime（Ongoing genome doubling…, Nature 2025） | 論文頁 [s41586-025-09240-3](https://www.nature.com/articles/s41586-025-09240-3) | 在既有 single-cell tree 上為 WGD 定時，屬應用研究，不推 topology |
| Refphase | PMC10621967（DOI 未抄錄） | multi-sample phasing，產生 haplotype-specific CN，不推樹 |
| 長讀 melanoma sublines（Nat Commun 2026） | 論文頁 [s41467-026-75172-9](https://www.nature.com/articles/s41467-026-75172-9) | 應用論文：用 ScisTree 建 SNV tree，Wakhan 的 CNA 只做 harmonize，沒有方法學貢獻。不過這是**ONT 長讀加推樹**少見的實例，值得當 pipeline 參考 |

## 給協調者的建議

1. **TUSV-ext（加上 Sc-TUSV-ext／TUSV-int）**：唯一在推樹時把 SNV、allele-specific CN 與 SV breakpoint 一起 phase 到 allele 的方法，也有 multiplicity 式約束（variant 隨 segment duplicate 或 loss）。它和「longphase HP + phased SV」的對接最直接。精讀時重點看 ILP 中 phasing 的 latent 變數能不能直接以 long-read 的觀測值取代。
2. **MEDICC2**：haplotype-specific CN 與 WGD 的事實標準，作者也明確展示 phasing 品質會改變推出的 event 和 tree（MSAI）。可以拿它的 event model 當 PhyClone CN 層的 prior，或當外部 CN tree 的對照。
3. **CNETML**：底層是 haplotype-specific CN 的 Markov 模型加上 Felsenstein likelihood，作者也量化了 total CN 在 copy-neutral 事件下會失準。這是把「CN 沿 tree 轉移的機率」放進 PhyClone likelihood 時最好借用的機率模型。
4. **SCICoNE／CONET（擇一精讀，建議 SCICoNE）**：以 MCMC 抽樣 CN event tree，breakpoint／event 本身就是節點，和 PhyClone 的 tree-space sampler 架構最接近，可參考它的 event 表示法與 tree move。
5. **ALPACA（雖然排除，仍建議對照讀）**：它是「給定 SNV tree 推 allele-specific CN」的代表，正好界定我們要超越的範圍：我們想讓 haplotype CN 回過頭影響 topology，而不只是下游標註。

---

### 不確定處（給協調者）
- MEDICC2 主程式碼 repo 的位置（GitHub `schwarzlab-ccb/medicc2` 只有 10 stars，可能是 mirror；Bitbucket 未查證）。
- NestedBD-Long 正式出版的 venue（Springer 章節 10.1007/978-3-031-94928-9_2，推測是 RECOMB-CG 2025，頁面因 redirect 無法讀取）。
- SCICoNE、NestedBD 吃的是 total 還是 allele-specific CN，論文頁沒有寫明，表中標為「推論 total」。
- DEVOLUTION 的程式碼 URL 沒查到。
- CNT-MD 的 JCB DOI、ConDoR、HATCHet2、SIGNALS、Wakhan、Severus 的 DOI 都沒有逐一核對（因為它們屬於排除或經典類）。
- 2025–2026 沒有找到「長讀 phased breakpoint 或 haplotype CN 直接用來推 tumor topology」的專門方法論文。這可能是空白，也可能是搜尋漏掉。
