# Search D：long-read 特徵建樹的 repo／preprint／abstract／thesis

搜尋日期：2026-10-19。工具：`gh search repos/code/issues`、`gh repo list`、`gh api`（README）、WebSearch、WebFetch。
每一項都附上實際抓取的 URL。星數與 push 日期取自 `gh api`，時間為 2026-10-19。

## 結論

- 沒有找到「用 HP／PS 或 same-read SNV co-occurrence 當 tree input 或 topology constraint」的公開 repo 或 preprint。
- 有建樹或排序步驟的新項目只有兩個。兩者都屬於已知的 mouse melanoma ONT sublines 研究（Liu & Goretsky, Kolmogorov／Sahinalp lab）：
  - TreeHarmonizer（repo）：把 SNV／SV／CNA 放到已知樹上。
  - Yuelin Liu 2025 UMD 博士論文與 NCM 2023 talk：用 phased CpG methylation 建 phylogeny。
- LongPhase-S 與 LongPhase-TO 用 lineage 式命名（HP1 → HP1-1）。這是最接近「haplotype 階層」的東西。但兩篇都明說沒有 subclone tree，並把聯合 subclonality 模型列為未來工作。這是 PhyClone + longphase-s 延伸的空白點。

---

## A. 主清單（存在建樹或 mutation-ordering 步驟）

### A1. TreeHarmonizer
- type：repo；year：2025（created 2025-06-25，last push 2026-03-10），stars = 1
- URL：https://github.com/KolmogorovLab/TreeHarmonizer
- lab：Kolmogorov lab（NCI）。對應論文是 Liu & Goretsky et al.（melanoma sublines）→ **論文本身 already_known**，repo 是新發現。
- platform：ONT
- long-read 特徵：Severus SV（只支援 Severus VCF）、Wakhan CNA（haplotype-specific CN 輸出）、SNV
- role：timing（把事件放到樹的分支上）；樹本身來自外部（論文用 ScisTree 對 sublines 的 SNV 建樹）
- algorithm：輸入 Newick 樹和每個 sample 的 SNV／CNA／SV，把每個 variant 指派到樹上能解釋其出現模式的分支，並視覺化 variant trajectory。
- maturity：有 code、conda env、example_data、notebook；README 說在 Python 3.6／3.12 測過。沒有 unit test 目錄。用途偏向論文重現。
- evidence（README，經 `gh api repos/KolmogorovLab/TreeHarmonizer/readme` 抓取）：
  > "TreeHarmonizer is a utility for placing called variants onto a pre-existing phylogenetic tree … It supports single nucleotide variants (SNVs), structural variants (SVs), and copy number alterations (CNAs)"
  > "`--sv-path` … **Only Severus files are currently supported.**"
- 與 PhyClone + longphase-s 的關係：輸入是 single-cell-derived sublines（每個 leaf 是一個 clone），**不是** bulk mixture deconvolution。可參考的做法是「建樹後再放 Wakhan HP1/HP2 CN 與 Severus SV」。它不用 HP 約束 topology。

### A2. Yuelin Liu，"Studying Tumor Evolution with Emerging Sequencing Technologies"（博士論文）+ NCM 2023 Houston talk
- type：thesis（UMD 2025，advisors：S. Cenk Sahinalp、Mihai Pop）+ conference talk（ONT NCM 2023，頁面日期 2023-12-06）
- URL：https://drum.lib.umd.edu/items/4490d113-fb04-4023-96a6-0548f8633718 ；https://nanoporetech.com/resource-centre/ncm-2023-houston-analysis-melanoma-evolution-using-nanopore-long-read-sequencing
- platform：ONT PromethION R10（mouse melanoma sublines）
- long-read 特徵：**phased CpG methylation**、SNV、SV、CNA
- role：tree_input（methylation-based phylogeny）+ validation（與 bulk exome／transcriptome 樹比對）
- algorithm：NCM 頁面說用 sublines 的 phased CpG methylation profile 建 tumor phylogeny，結果與既有 bulk 樹一致。論文另含一個 distance-based 方法，用 single-cell methylation 建 phylogeny（論文頁面原文說是 single-cell methylation 資料，不是 long read）。
- maturity：thesis 與 talk 摘要；沒找到獨立的 methylation-tree code（TreeHarmonizer 是同一計畫的 repo）。
- evidence：
  - NCM 頁面："the tumor phylogeny constructed using phased CpG methylation profiles"（WebFetch 取得）
  - DRUM 頁面："a novel framework to study both the genomic and epigenomic changes during tumor evolution"
  - DRUM 頁面**沒有**提到 phasing（WebFetch 結果）。
- 與本研究的關係：屬於 already_known melanoma 研究的延伸材料。可借鏡的是 haplotype-resolved methylation 當獨立 lineage 證據，但前提是 clonal sublines，不是 bulk。

### A3.（already_known）Long-read sequencing of single cell-derived melanoma subclones/sublines
- bioRxiv 10.1101/2025.08.28.672865 → Nat Commun 2026（s41467-026-75172-9）。用 ScisTree 對 SNV 建樹，再放 SV／methylation。只列出以利交叉比對，**不算新發現**。

### 接近但不符納入條件
- **SVCFit**（Liu … Karchin，bioRxiv 10.1101/2025.02.01.636056；code：https://github.com/KarchinLab/SVCFit）。它從 SV CCF 建 clonal tree（DPGMM 聚類 + Gabow–Myers 列舉 + SCHISM fitness）。但它用**短讀**（Manta／Delly／GRIDSS）。long read 只在 Discussion 出現："with long-read sequencing providing additional breakpoint resolution where available"。→ 不列主清單。
- **Meltos**（https://github.com/ih-lab/Meltos，8 stars，last update 2025-01-25）：multi-sample SV tumor phylogeny，短讀，2018 年代工具。

---

## B. Feature tools（caller／phaser／CN；沒有建樹步驟）

| 名稱 | type | URL | stars／last push | 特徵 | 與 PhyClone + HP 的關係 |
|---|---|---|---|---|---|
| LongPhase-S（Ho, Zheng, Luo, Chiang, Huang；bioRxiv 2025-11） | preprint + repo | https://www.biorxiv.org/content/10.1101/2025.11.20.689492v1 ；https://github.com/CCU-Bioinformatics-Lab/longphase-s | 12／2026-08-05 | somatic haplotag（HP1-1／HP2-1，HP3 = unresolved）、purity estimation | 本研究的 HP 來源。原文："HP1-1 and HP2-1 represent the somatically altered descendants of HP1 and HP2"。也寫："a fully joint model of purity, ploidy, and subclonality would further reduce ambiguity"。這表示 subclone 模型是未來工作。**沒有建樹**。 |
| LongPhase-TO（Chen, Zheng, Luo, Fu, Yang, Huang；bioRxiv 2026-09） | preprint + repo | https://www.biorxiv.org/content/10.64898/2026.09.14.751225v1 ；https://github.com/CCU-Bioinformatics-Lab/longphase-to | 17／2026-10-19 | tumor-only 的 germline + somatic 聯合 phasing、LOH、tumor DNA fraction、可選 5mC XGBoost | "This lineage-aware traversal preserves clonal ancestry (e.g., HP1-1 from HP1)"。只有一層 descendant，沒有多層 subclone 階層。 |
| LongPhase（germline） | repo | https://github.com/twolinin/longphase | 133／2026-10-16 | SNV／indel／SV／5mC co-phasing | 上游 phaser。另有 manuscript repo `ythuang0522/longphase-2-paper`（0 stars）。 |
| Wakhan（Kolmogorov lab；medRxiv 2025-12；AACR 2025 Abstract 5049） | preprint + repo | https://www.medrxiv.org/content/10.64898/2025.12.11.25342098v1.full.pdf ；https://github.com/KolmogorovLab/Wakhan | 91／2026-10-15 | haplotype-specific CNA、phase-switch 校正、purity／ploidy、**subclonal／fractional CN 輸出** | README："`subclonal_profile.bed` … for subclonal/fractional copy numbers (`--copynumbers-subclonal-enable`)"。可當 PhyClone 的 allele-specific major/minor CN 輸入，並保留 hp1/hp2 對應。AACR 5049 頁面回 403，摘要內容（H1437 第 6、21 號染色體的 subclonal event）只來自搜尋 snippet，**未驗證**。 |
| Severus（Kolmogorov lab） | repo | https://github.com/KolmogorovLab/Severus | 181／2026-06-08 | somatic SV、haplotype-specific SV、breakpoint graph | 提供 phased SV breakpoint 給 Wakhan。沒有建樹。 |
| Padfoot（Kolmogorov lab） | repo | https://github.com/KolmogorovLab/Padfoot | 2／2026-03-12 | Severus／Wakhan 結果註解，README 標註 "under development" | feature_only |
| SAVANA（Cortes-Ciriano lab；Nat Methods 2025） | repo | https://github.com/cortes-ciriano-lab/savana | 93／2026-06-30 | somatic SV + allele-specific SCNA + purity／ploidy | feature_only。journal 論文，已為人熟知。 |
| PRCGAP（Sakamoto … Shiraishi；bioRxiv 10.64898/2026.05.28.728591） | preprint + repo | https://github.com/yos-sk/PRCGAP | — | personalized diploid reference；把 SNV、SV、CN、methylation 指派到 haplotype | 原文："revealed their co-occurrence with copy-number changes and SV breakpoints on the same haplotype"。資料集含 **HCC1954**，與本研究重疊。沒有建樹或 timing（Methods 只讀到前 100k 字元）。 |
| Long-Read Haplotype Phasing Resolves Allelic Configuration（medRxiv 10.64898/2026.05.05.26351600） | preprint | https://www.medrxiv.org/content/10.64898/2026.05.05.26351600v2.full | — | cis／trans 判定 | 臨床 cis/trans，沒有 clone tree（只看搜尋摘要）。 |
| ONT ASHG 2023 poster "Haplotype-resolved, multi-modal, tumour-normal analysis…" | poster | https://nanoporetech.com/resource-centre/haplotype-resolved-multi-modal-tumour-normal-analysis-cancer-genomes-using-nanopore | — | "long nanopore reads enable haplotype and clone specific CNV calling" | 沒列作者與工具。沒有建樹。 |
| shahcompbio：nfhaplotag、nfphasing、wakcna、nanogenome | repo（pipeline） | https://github.com/shahcompbio/nfhaplotag 等 | 0–1 stars | WhatsHap／longphase haplotag、Wakhan CN 的 Nextflow 包裝 | 表示 Shah lab 正在建 long-read CN pipeline。沒有找到 long-read tree 工具。 |
| Spectre（Sedlazeck lab） | repo | https://github.com/fritzsedlazeck/Spectre | 72／2026-10-02 | long-read CNV caller | feature_only |
| elkebir-group/prolyG-phasing | repo | https://github.com/elkebir-group/prolyG-phasing | 0／2026-09-28 | polyG locus 的 read family 用 flanking SNV 標 haplotype；可用 matched normal 的 haplotype 為腫瘤 read 投票（ref-phase） | 是 read pair 資料，**不是** long read。只有 phasing 想法相近，沒有建樹。 |

---

## C. 各 lab 檢查結果

| Lab | 方法 | 結果 |
|---|---|---|
| Roth-Lab（PhyClone、PyClone-VI） | `gh repo list Roth-Lab`、issue 搜尋 | **沒有 long-read 計畫**。新 repo：`hapclone-cnasim-experiments`（2026-04 建立，0 stars）把 "hapclone" 跟 CHISEL、SIGNALS、HMMcopy 比較。我推論它是 scWGS 的 haplotype-specific CN clone 方法，code 尚未公開。`cfclone`：用 scWGS clone CN 對 cfDNA 做反卷積（輸入包含 haplotype count），屬短讀。PhyClone／pyclone-vi issue 中沒有 long read 討論。 |
| Raphael lab（HATCHet） | `gh repo list raphael-group` | **沒有找到** long-read phylogeny。相關的有 CalicoST、CHISEL（haplotype-specific CN，非 long read），以及 `multibreak-sv`（舊的 long-read SV caller）。 |
| El-Kebir lab（Pharming、SPRUCE、DeCiFer） | repo list + publications 頁面 | **沒有找到**。publications 頁面 2023–2026 標題沒有 long read／nanopore／haplotype／phasing。只找到 prolyG-phasing（非 long read）。 |
| Schwarz lab（MEDICC2） | `gh repo list schwarzlab` 無結果（MEDICC2 在 Bitbucket） | **沒有找到** long-read 計畫（只查了 GitHub 與網路搜尋）。 |
| Kolmogorov lab（Wakhan、Severus） | repo list + README | Wakhan、Severus、Padfoot、**TreeHarmonizer**（A1）。後者是唯一有樹的 repo，但樹由外部提供。 |
| Sedlazeck lab | repo list + 搜尋 | **沒有找到** tumor phylogeny 計畫。只有 Spectre、SURVIVOR 等 caller。 |
| Kuo／Huang lab（longphase、longphase-s、longphase-to） | repo list + 兩篇 preprint 全文 | LongPhase-S 與 LongPhase-TO 都只有一層 lineage label（HP1 → HP1-1），**沒有建樹**。org 中有私有性質的 `knowledge` repo，沒看內容。 |
| Cortes-Ciriano lab | repo list | SAVANA，feature_only。 |

---

## D. 總表

| # | 名稱 | type | year | 平台 | long-read 特徵 | role | code | 狀態 |
|---|---|---|---|---|---|---|---|---|
| A1 | TreeHarmonizer | repo | 2025 | ONT | Severus SV、Wakhan HP CN、SNV | timing（放到既有樹上） | 有（1 star） | 新（論文 already_known） |
| A2 | Y. Liu UMD thesis + NCM 2023 | thesis／talk | 2023–2025 | ONT | phased CpG methylation | tree_input／validation | 沒找到 | 新（同一計畫） |
| A3 | Melanoma sublines | preprint／journal | 2025–2026 | ONT | SNV、SV、methylation | tree_input（ScisTree） | Zenodo | already_known |
| — | SVCFit | preprint + repo | 2025 | 短讀 | 無（只在 Discussion 提及） | tree_input | 有 | 不符納入條件 |
| B | LongPhase-S／LongPhase-TO／LongPhase | preprint + repo | 2025–2026 | ONT | HP／PS、somatic haplotag、5mC | feature_only | 有 | 新的 feature 來源 |
| B | Wakhan／Severus／Padfoot | preprint + repo | 2024–2026 | ONT | HP-specific CN、phased SV、subclonal CN | feature_only | 有 | feature |
| B | SAVANA、PRCGAP、Spectre、Shah pipelines | repo／preprint | 2023–2026 | ONT | SV、allele-specific CN、haplotype 指派 | feature_only | 有 | feature |

---

## E. 失敗或無結果的搜尋

- `gh search repos`，以下關鍵字 **0 筆**："phylogeny long-read cancer"、"clonal nanopore"、"subclonal haplotype"、"phase set clone"、"haplotype clonal tumor"、"co-occurrence phylogeny"、"long read tumor evolution"、"long-read subclonal"、"clone tree nanopore"、"phased copy number tumor long read"、"nanopore cancer clone"、"ONT tumor phylogeny"、"clonal deconvolution long reads"、"read-level phylogeny"、"allele-specific copy number nanopore"、"subclone phasing"、"single molecule clonal"、"mutation co-occurrence reads"。
- `gh search code` 搜 `"phase set" clone tree tumor`、`haplotag subclone`、`pyclone haplotype long read`、`phylogeny "longphase"`、`clonal "whatshap" tumor tree`：0 筆。`"HP:i" clonal tree` 只回傳無關的 ontology 檔案。
- 「clone tree／tumor phylogeny／subclonal reconstruction」的 repo，用 long／haplo／phas／nanopore 過濾後，沒有 long-read 工具。
- 在 PhyClone、pyclone-vi、HATCHet、Pharming、longphase-s 的 issue 搜 "long read" 或 "phylogeny／clone"：0 筆。
- Web：RECOMB／ISMB 2025–2026 沒有 long-read clone tree 論文。RECOMB 2025 的 devider 是 mixture haplotyping，與腫瘤無關，沒有深入看。arXiv 2024–2025 沒有 same-read mutation-pair 的 long-read 方法。AACR 2025 沒有 phasing + clonal evolution 的 abstract（只有 Wakhan 5049，頁面 403）。PacBio HiFi 沒有 tumor phylogeny 研究。
- 已查但不納入：SPLONGGET（bioRxiv 10.1101/2025.09.08.674950，ONT single-cell 多體學，B-ALL）。摘要提到 "clonal dynamics"，但沒說有建樹或 phasing。屬於未驗證的可能線索，值得讀全文。
- 依指示排除：Donmez & Kolmogorov AACR 2026 #6912、Zeng 2025 HBV HCC、Akagi/Goodwin 2023 HPV、Liu 2021 myeloma。這些都沒列出。
