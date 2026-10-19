# 研究共用術語

本詞彙表統一 `research/` 的腫瘤演化、變異、定相與推論用語。各項定義適用於本 repo；引用個別研究時，仍須保留原文的測量範圍與假設。

命名規則、研究範圍與來源索引見 [術語使用指南](TERMINOLOGY.md)。說明採短句繁體中文，依 ASD-STE100 原則改寫。

## Language

### 演化與樹

**T001 腫瘤演化樹（tumor phylogeny）**

描述腫瘤細胞群之祖先關係的樹狀模型。它由資料與假設推得。

_別名與對照_：tumour phylogeny; tumor evolutionary tree; clone phylogeny。
_用詞界線_：敘述特定結果時，另寫明節點代表細胞、克隆、突變或樣本。
_原文定位_：[HCC L1](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T002 克隆（clone）**

本研究解析度下，共享特定遺傳歷史的細胞群。

_別名與對照_：clonal population; 克隆群。
_用詞界線_：不要把統計群集或單倍型直接稱為克隆。
_原文定位_：[HCC L37](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T003 亞克隆（subclone）**

腫瘤內可由遺傳差異區分的克隆群。

_別名與對照_：subclonal population。
_用詞界線_：指出相對的祖先或比較範圍；低 VAF 本身不能證明亞克隆。
_原文定位_：[HCC L8](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L44](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)。

**T004 克隆演化（clonal evolution）**

細胞群隨時間累積遺傳改變，形成不同克隆的過程。

_別名與對照_：clonal evolutionary history。
_用詞界線_：克隆比例變動不一定代表新增遺傳事件。
_原文定位_：[HCC L53](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A01 L3](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T005 腫瘤內異質性（intratumor heterogeneity；ITH）**

同一腫瘤內，細胞或細胞群之間存在的差異。

_別名與對照_：intratumoral heterogeneity; intra-tumour heterogeneity。
_用詞界線_：標明差異屬於基因型、拷貝數、表觀遺傳或表型。
_原文定位_：[HCC L15](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md)；[A03 L21](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T006 克隆樹（clone tree）**

以克隆為節點，表示克隆祖先關係的樹。

_別名與對照_：clonal tree; clone phylogeny。
_用詞界線_：不要與樣本樹、細胞樹或突變樹互換。
_原文定位_：[A02 L11](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)；[A03 L9](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T007 細胞樹（cell tree）**

以個別細胞為觀測末端，表示推定親緣關係的樹。

_別名與對照_：cell phylogeny; single-cell phylogeny。
_用詞界線_：細胞的相似度分群圖不會自動成為細胞演化樹。
_原文定位_：[A01 L15](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L1](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T008 樣本樹（sample tree）**〔支援詞〕

以樣本為觀測末端，表示樣本間關係的樹。

_別名與對照_：sample phylogeny。
_用詞界線_：同一樣本可能含多個克隆；樣本樹不直接給出克隆樹。
_原文定位_：[B06 L1](tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/README.md)。

**T009 突變樹（mutation tree）**

以突變事件為節點，表示事件先後或祖先關係的樹。

_別名與對照_：event tree。
_用詞界線_：部分方法將共同發生的突變置於同一節點，須另行說明。
_原文定位_：[A05 L1](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)；[B05 L1337](tumor_phylogeny_2026/papers/B05_medicc2_2022/paper.txt)。

**T010 樹拓樸（tree topology）**

樹的節點連接方式與祖先關係。

_別名與對照_：topology; tree structure; 拓撲。
_用詞界線_：統一寫「拓樸」；拓樸本身不包含分支長度或細胞比例。
_原文定位_：[HCC L1](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L13](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)。

**T011 節點（node）**

樹中代表指定生物單位或事件的元素。

_別名與對照_：vertex。
_用詞界線_：先寫明節點代表什麼；虛擬根節點不一定代表真實細胞。
_原文定位_：[HCC L18](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T012 邊（edge）**

連接兩個節點的關係。

_別名與對照_：tree edge。
_用詞界線_：有根演化樹的邊有祖先方向；邊的存在不表示已有直接實驗驗證。
_原文定位_：[HCC L10](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L17](phyclone_research/notes/05_EVIDENCE_MATRIX.md)。

**T013 根節點（root node）**

指定有根樹之祖先方向的起點。

_別名與對照_：root。
_用詞界線_：區分正常細胞根、腫瘤祖先根與計算用虛擬根。
_原文定位_：[PC L12](phyclone_research/notes/zh-TW/04_CODE_MAPPING.md)；[B01 L193](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T014 子樹（subtree）**

由一個節點及其所含後代構成的樹。

_別名與對照_：descendant subtree。
_用詞界線_：計算 CCF 時，說明是否包含子樹內的所有後代。
_原文定位_：[PC L5](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)；[B01 L742](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T015 最近共同祖先（most recent common ancestor；MRCA）**

指定細胞群或節點共同擁有的最近祖先。

_別名與對照_：共同祖先。
_用詞界線_：寫明比較範圍；MRCA 不等於已觀測到的單一細胞。
_原文定位_：[HCC L9](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[A01 L23](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T016 祖先與後代關係（ancestor–descendant relationship）**

一個節點位於另一節點的祖先路徑上的關係。

_別名與對照_：ancestry; ancestor-descendant relation。
_用詞界線_：區分直接親子關係與跨多層的祖先關係。
_原文定位_：[HCC L17](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T017 線性演化（linear evolution）**

指定演化範圍內，主要克隆依序沿單一路徑出現的模型。

_別名與對照_：linear topology; linear tree。
_用詞界線_：只描述指定範圍；局部線性順序不代表全樹只有一條路徑。
_原文定位_：[HCC L55](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[A04 L19](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)。

**T018 分支演化（branching evolution）**

一個祖先群產生兩個或更多後代分支的演化模型。

_別名與對照_：branched evolution; branching topology; branching tree。
_用詞界線_：分支的可識別程度取決於資料與模型。
_原文定位_：[HCC L1](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[B04 L1008](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/supplement.txt)。

**T019 平行演化（parallel evolution）**

不同分支獨立出現相同或相似遺傳改變的過程。

_別名與對照_：parallel genomic evolution。
_用詞界線_：相同 total CN 不足以證明相同事件；不要直接等同共同祖先繼承。
_原文定位_：[B01 L5](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)；[A04 L427](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/paper.txt)。

**T020 突變指派（mutation assignment）**

把觀測突變分配到指定節點或克隆的推論結果。

_別名與對照_：mutation-to-clone assignment; SNV-to-node assignment。
_用詞界線_：clone assignment 也可指細胞到克隆的指派，不能無條件視為同義詞。
_原文定位_：[HCC L32](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T021 突變群集（mutation cluster）**

依指定觀測特徵或模型，歸在同一組的突變集合。

_別名與對照_：cluster; 叢集; 突變分群。
_用詞界線_：統一寫「群集」；多個群集可能屬於同一克隆。
_原文定位_：[HCC L45](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T124 趨同演化（convergent evolution）**

不同演化分支透過各自的改變，形成相似功能或狀態的過程。

_別名與對照_：convergent inactivation。
_用詞界線_：與平行演化的區分須依原文；相似結果不等於相同事件。
_原文定位_：[A03 L17](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[B01 L305](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T125 克隆組成（clonal composition）**

指定樣本內的克隆種類及各克隆的相對含量。

_別名與對照_：clone mixture; mixture composition。
_用詞界線_：克隆結構 clonal architecture 也可包含祖先關係，不直接當成同義詞。
_原文定位_：[HCC L31](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[A04 L23](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)。

**T126 克隆擴張（clonal expansion）**

指定克隆的細胞數或群體占比隨時間增加的過程。

_別名與對照_：clone expansion。
_用詞界線_：說明是絕對數量增加或相對比例增加。
_原文定位_：[B02 L27](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/README.md)；[B01 L1053](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T127 葉節點（leaf node）**

在指定樹中，沒有子節點的末端節點。

_別名與對照_：leaf; tip。
_用詞界線_：葉節點可能代表細胞、克隆或樣本，須按樹類型說明。
_原文定位_：[PC L9](phyclone_research/notes/07_PRESENTATION_BRIEF.md)；[B03 L19](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T128 演化支（clade）**

指定祖先節點與其全部後代形成的群組。

_別名與對照_：monophyletic group。
_用詞界線_：演化支是樹內群組，不是任意相似度群集。
_原文定位_：[HCC L65](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L35](phyclone_research/notes/04_CODE_MAPPING.md)。

**T129 事件定位（event placement）**

把推定事件配置到指定樹之節點或邊的結果。

_別名與對照_：mutation placement; phylogenetic placement。
_用詞界線_：在固定樹上配置事件，不代表重新推論拓樸。
_原文定位_：[PC L5](phyclone_research/notes/zh-TW/07_PRESENTATION_BRIEF.md)；[B01 L17](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)。

**T130 祖先狀態重建（ancestral-state reconstruction）**

由已觀測後代與模型，推定未觀測祖先狀態的分析。

_別名與對照_：ancestral CN reconstruction。
_用詞界線_：推定的祖先 CN 不是直接測量值。
_原文定位_：[PC L9](phyclone_research/notes/zh-TW/07_PRESENTATION_BRIEF.md)；[A01 L19](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T186 預先分群（pre-clustering）**

在樹推論之前，先依指定資料或模型建立突變群集的程序。

_別名與對照_：preclustering; preclustering step。
_用詞界線_：明示群集是否固定不可拆分，避免把分群改善誤認為拓樸改善。
_原文定位_：[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)；[B04 L45](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)。

**T191 克隆指派（clone assignment）**

把指定細胞或其他觀測單位歸入某個克隆的結果。

_別名與對照_：cell-to-clone assignment。
_用詞界線_：每次明示被指派的單位；不可單由此名稱推定是突變或細胞。
_原文定位_：[HCC L48](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/04_confidence_and_limits.md)；[A01 L11](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T192 克隆結構（clonal architecture）**

由克隆種類、含量或祖先關係描述的腫瘤組織方式。

_別名與對照_：clonal structure。
_用詞界線_：原文 architecture 的範圍可能不同，引用時說明實際包含哪些項目。
_原文定位_：[A03 L17](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A01 L227](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

### 變異與拷貝數

**T022 體細胞變異（somatic variant）**

受精後在某個細胞或細胞群獲得的序列變異。

_別名與對照_：somatic mutation; 體細胞突變。
_用詞界線_：不要求只在腫瘤出現，也不要求所有腫瘤細胞都帶有該變異。
_原文定位_：[HCC L12](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A05 L15](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)。

**T023 生殖系變異（germline variant）**

源自生殖系、構成個體遺傳背景的變異。

_別名與對照_：germline mutation; 生殖細胞變異。
_用詞界線_：統一寫「生殖系」；constitutional variant 的範圍須按原文說明。
_原文定位_：[HCC L16](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A03 L15](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T024 單核苷酸變異（single-nucleotide variant；SNV）**

指定位置的一個核苷酸與比較序列不同的變異。

_別名與對照_：single nucleotide variation。
_用詞界線_：SNV 可屬於體細胞或生殖系；SNV 不等於 SNP。
_原文定位_：[HCC L7](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T025 單核苷酸多型性（single-nucleotide polymorphism；SNP）**

族群中具有多型性的單核苷酸變異。

_別名與對照_：single nucleotide polymorphism。
_用詞界線_：不要把任何單一鹼基變異都稱為 SNP。
_原文定位_：[HCC L63](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A03 L23](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T026 短插入與缺失（small insertion or deletion；indel）**

短序列的插入或缺失變異。

_別名與對照_：insertion/deletion; 小片段插入缺失。
_用詞界線_：長度分類門檻須依 caller 或 benchmark 規格註明。
_原文定位_：[HCC L7](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A01 L1461](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T027 結構變異（structural variant；SV）**

改變較大片段 DNA 位置、方向、連接或拷貝配置的變異。

_別名與對照_：structural variation。
_用詞界線_：標明方法的分類與長度門檻；SV 不一定改變拷貝數。
_原文定位_：[A01 L11](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L803](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T028 斷點（breakpoint）**

序列連接或基因組狀態發生改變的位置。

_別名與對照_：SV breakpoint; CN breakpoint。
_用詞界線_：標明是 SV 連接斷點或 CN 分段邊界，並記錄定位不確定性。
_原文定位_：[A01 L17](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L159](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T029 拷貝數（copy number；CN）**

在指定細胞與基因組區段中，該區段的 DNA 拷貝數量。

_別名與對照_：copy-number state。
_用詞界線_：區分單細胞整數狀態、克隆狀態與混合樣本的平均估計值。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T030 拷貝數改變（copy-number alteration；CNA）**

相對指定基準，DNA 區段拷貝數增加或減少的改變。

_別名與對照_：copy-number aberration。
_用詞界線_：癌症獲得性改變優先寫 CNA；需區分事件與觀測狀態。
_原文定位_：[HCC L8](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L9](phyclone_research/notes/04_CODE_MAPPING.md)。

**T031 拷貝數變異（copy-number variation；CNV）**

基因組區段拷貝數的差異。

_別名與對照_：copy-number variant。
_用詞界線_：文獻常與 CNA 交用；保留工具原名，不以 CNV 推定生殖系來源。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[PC L44](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)。

**T032 總拷貝數（total copy number）**

指定區段所有等位拷貝的總數。

_別名與對照_：total CN; C_total。
_用詞界線_：在二等位表示法中，total CN 為 major CN 加 minor CN。
_原文定位_：[PC L34](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)；[PW L65](hcc1395_golden_tree_research/phylowgs_model_review.md)。

**T033 等位基因特異性拷貝數（allele-specific copy number）**

分別表示兩個等位背景之 DNA 拷貝數的狀態。

_別名與對照_：allele-specific CN; ASCN。
_用詞界線_：major/minor 是數量排序；haplotype-specific CN 另外保留已定相的身份。
_原文定位_：[HCC L98](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T034 主要與次要等位拷貝數（major and minor copy number）**

將兩個等位背景按拷貝數排序後，分別得到的較大值與較小值。

_別名與對照_：major/minor CN; major_cn/minor_cn。
_用詞界線_：major 不固定對應 HP1；不同區段的排序可能交換。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L7](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T035 單倍型特異性拷貝數（haplotype-specific copy number）**

保留單倍型身份後，分別表示每個單倍型的拷貝數。

_別名與對照_：haplotype-specific CN; homolog-specific CN。
_用詞界線_：使用前須確認定相方向；不能只把 major/minor 改名為 HP1/HP2。
_原文定位_：[A01 L15](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A04 L13](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)。

**T036 倍體數（ploidy）**

細胞的染色體組套數，或模型所估計的平均基因組拷貝水準。

_別名與對照_：ploidy estimate。
_用詞界線_：報告時說明是細胞學倍體或模型平均值。
_原文定位_：[HCC L8](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L48](phyclone_research/notes/zh-TW/03_EXPERIMENTS_RESULTS.md)。

**T037 雜合性喪失（loss of heterozygosity；LOH）**

原本雜合的位點或區域，失去其中一個等位背景的狀態。

_別名與對照_：雜合性缺失; 雜合性丟失。
_用詞界線_：統一寫「喪失」；LOH 可由刪除或拷貝數中性機制造成。
_原文定位_：[HCC L8](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A01 L21](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T038 拷貝數中性雜合性喪失（copy-neutral loss of heterozygosity；cnLOH）**

總拷貝數未改變，但已發生雜合性喪失的狀態。

_別名與對照_：copy-neutral LOH; CN-LOH。
_用詞界線_：總 CN 為 2 不足以排除 LOH。
_原文定位_：[HCC L88](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[A01 L21](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T039 全基因組加倍（whole-genome doubling；WGD）**

整套基因組拷貝加倍的演化事件。

_別名與對照_：whole genome duplication。
_用詞界線_：WGD 後可再有增減；當前倍體值不能單獨證明事件歷史。
_原文定位_：[A01 L25](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L1368](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T040 突變等位基因拷貝數（mutation multiplicity）**

一個攜帶細胞在指定位點具有的突變等位拷貝數。

_別名與對照_：mutant-copy number; multiplicity。
_用詞界線_：不可與樹表示重數混用；須指定細胞或克隆的 CN 狀態。
_原文定位_：[HCC L15](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L40](phyclone_research/notes/05_EVIDENCE_MATRIX.md)。

**T041 突變流失（mutation loss）**

後代因刪除或其他基因組事件，不再保留祖先突變的情形。

_別名與對照_：mutation deletion; 突變丟失。
_用詞界線_：缺少支持讀段不等於已發生突變流失。
_原文定位_：[PC L5](phyclone_research/notes/07_PRESENTATION_BRIEF.md)；[A03 L33](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T042 事件時序（event timing）**

兩個或多個演化事件的相對先後，或事件發生時間的估計。

_別名與對照_：mutation timing; CNV timing。
_用詞界線_：區分相對順序、分子時間與日曆時間。
_原文定位_：[HCC L295](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L68](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T131 拷貝數區段（copy-number segment）**

在指定分段方法下，具有共同拷貝數狀態的連續基因組區域。

_別名與對照_：CN segment; segmentation result。
_用詞界線_：量測分箱 bin 與推定區段 segment 須分開。
_原文定位_：[HCC L55](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[A01 L35](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T132 拷貝數增加（copy-number gain）**

相對指定基準，基因組區段的拷貝數較高的改變。

_別名與對照_：CN gain; copy gain。
_用詞界線_：須寫明正常、克隆或倍體基準。
_原文定位_：[HCC L58](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L56](phyclone_research/notes/04_CODE_MAPPING.md)。

**T133 擴增（amplification）**

指定區段產生額外 DNA 拷貝的現象。

_別名與對照_：gene amplification; focal amplification。
_用詞界線_：高階擴增與一般 gain 的區分，依研究門檻說明。
_原文定位_：[PC L44](phyclone_research/notes/zh-TW/03_EXPERIMENTS_RESULTS.md)；[PW L78](hcc1395_golden_tree_research/phylowgs_model_review.md)。

**T134 DNA 缺失（DNA deletion）**

相對指定基準，某段 DNA 序列流失的變異事件。

_別名與對照_：deletion; sequence deletion。
_用詞界線_：與資料缺失及廣義 CN loss 分開；低覆蓋本身不能證明 DNA 缺失。
_原文定位_：[PC L9](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)；[A03 L15](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T135 等位基因不平衡（allelic imbalance）**

指定位置或區段中，兩個等位背景的觀測量不相等的情形。

_別名與對照_：allele imbalance; BAF shift。
_用詞界線_：可能來自 CN、細胞混合、表現偏差或技術偏差；不直接等同 LOH。
_原文定位_：[B05 L13](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md)；[A01 L1562](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T136 鏡像亞克隆等位基因不平衡（mirrored subclonal allelic imbalance；MSAI）**

不同亞克隆對相反等位背景呈現不平衡的情形。

_別名與對照_：mirrored allelic imbalance; mirrored haplotype amplification。
_用詞界線_：合併樣本可能互相抵消；total CN 相同仍可能有不同演化歷史。
_原文定位_：[B05 L13](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md)；[B07 L21](tumor_phylogeny_2026/papers/B07_numbat_2022/README.md)。

**T137 接合點（junction）**

在變異結構中，原先分離的 DNA 區段相接的位置。

_別名與對照_：SV junction; virus–host junction。
_用詞界線_：與各片段在參考基因組上的斷點分開描述。
_原文定位_：[B04 L26](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)；[A01 L968](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T138 染色體重排（chromosomal rearrangement）**

染色體 DNA 片段的位置、方向或連接方式改變的事件。

_別名與對照_：genomic rearrangement。
_用詞界線_：平衡重排可以沒有總 CN 改變。
_原文定位_：[HCC L31](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md)；[A01 L17](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T139 染色體碎裂重組（chromothripsis）**

染色體發生大量相關碎裂與錯誤重接，形成複雜重排的現象。

_別名與對照_：chromothriptic rearrangement。
_用詞界線_：單憑斷點密集不足以確認，須保留研究判定準則。
_原文定位_：[A01 L27](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A04 L19](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)。

**T140 斷裂融合橋循環（breakage–fusion–bridge cycle；BFB）**

染色體末端融合、形成橋並再次斷裂，可反覆發生的過程。

_別名與對照_：breakage-fusion-bridge。
_用詞界線_：BFB 可產生擴增與重排；單一擴增狀態不能唯一決定此歷史。
_原文定位_：[A04 L19](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)；[A01 L656](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T172 變異（variant）**

相對指定比較背景，序列或基因組結構不同的狀態。

_別名與對照_：genomic variant; sequence variant。
_用詞界線_：先指定參考背景；變異判定是觀測結果，不直接給出演化事件時間。
_原文定位_：[HCC L16](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L8](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)。

**T173 突變（mutation）**

細胞的遺傳材料發生改變的事件。

_別名與對照_：mutational event。
_用詞界線_：事件稱突變；觀測差異稱變異；引用文獻時保留原作者用詞。
_原文定位_：[HCC L5](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T174 雜合（heterozygosity）**

指定位置具有不同等位形式的狀態。

_別名與對照_：heterozygous; HET。
_用詞界線_：在複雜 CN 背景中說明等位拷貝組成；未觀測到其中一種不直接證明純合。
_原文定位_：[PC L48](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)；[PW L33](hcc1395_golden_tree_research/phylowgs_model_review.md)。

**T175 純合（homozygosity）**

指定位置的同源等位拷貝具有相同形式的狀態。

_別名與對照_：homozygous; HOM。
_用詞界線_：單一剩餘拷貝是半合子，不因只有一種觀測就直接判為純合。
_原文定位_：[A03 L15](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A01 L1455](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T193 拷貝數減少（copy-number loss）**

相對指定基準，某區段或染色體的拷貝數較少的改變。

_別名與對照_：CN loss; copy-number decrease。
_用詞界線_：DNA 缺失或整條染色體流失都可能使 CN 減少；CN loss 不單指片段刪除。
_原文定位_：[HCC L58](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L28](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

### 單倍型與分子證據

**T043 等位基因（allele）**

指定位點或區域的一種序列形式。

_別名與對照_：等位型。
_用詞界線_：等位基因不同不代表位於不同細胞或不同克隆。
_原文定位_：[HCC L53](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T044 基因型（genotype）**

指定細胞、克隆或樣本在指定位置具有的等位組成。

_別名與對照_：genotypic state。
_用詞界線_：基因型可包含拷貝數；與基因表現狀態分開。
_原文定位_：[HCC L23](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L8](phyclone_research/notes/04_CODE_MAPPING.md)。

**T045 單倍型（haplotype）**

同一染色體拷貝上一起存在的一組等位基因。

_別名與對照_：haplotype background。
_用詞界線_：同一單倍型背景可存在於多個克隆。
_原文定位_：[HCC L52](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A01 L15](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T046 定相（phasing）**

把變異分配到各染色體拷貝或單倍型區塊的過程。

_別名與對照_：haplotype phasing; 相位分析; 分相。
_用詞界線_：統一寫「定相」；不得只因工具名稱含 Haplotype 就宣稱已定相。
_原文定位_：[HCC L295](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[A03 L23](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T047 相位區塊（phase block）**

在指定範圍內，變異相對單倍型配置可一致解讀的區段。

_別名與對照_：phasing block; haplotype block; phase set。
_用詞界線_：區塊外的 HP1/HP2 不保證方向一致。
_原文定位_：[HCC L19](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A01 L25](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T048 相位集合識別碼（phase-set identifier；PS）**

識別一組已定相關係的標籤值。

_別名與對照_：PS tag; phase set ID。
_用詞界線_：連同 sample 與 contig 解讀；PS 數值相同不證明跨樣本是同一區塊。
_原文定位_：[HCC L19](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A01 L25](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T049 單倍型標籤（haplotype tag；HP）**

記錄讀段所屬單倍型類別的標籤。

_別名與對照_：HP1/HP2; HP tag。
_用詞界線_：依工具與標籤型別解讀；HP1/HP2 不等於父母來源或 clone ID。
_原文定位_：[HCC L3](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A01 L25](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T050 讀段單倍型標記（haplotagging）**

把讀段標記到推定單倍型的過程。

_別名與對照_：haplotag; read phasing。
_用詞界線_：與變異定相分開；沒有 HP 的讀段不等於沒有變異。
_原文定位_：[A03 L23](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[B01 L574](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T051 單倍型方向對齊（haplotype orientation）**〔支援詞〕

把相位區塊的單倍型標籤對應到共同等位背景的關係。

_別名與對照_：phase orientation; HP orientation。
_用詞界線_：方向對齊需要額外證據；不可預設 HP1 固定為 major 或父源。
_原文定位_：[A04 L17](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)。

**T052 相位切換錯誤（switch error）**

推定的兩個單倍型在某一位置後錯誤交換身份的定相錯誤。

_別名與對照_：phasing switch error; phase switch。
_用詞界線_：計算 switch error rate 時，寫明可評估的相鄰位點對。
_原文定位_：[B05 L43](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md)；[B04 L183](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/paper.txt)。

**T053 分子連鎖（molecular linkage）**

變異由同一分子來源的觀測連接起來的證據。

_別名與對照_：read-level linkage; long-range linkage。
_用詞界線_：區分實測同一長讀段與條碼重建的長分子來源。
_原文定位_：[PW L145](hcc1395_golden_tree_research/phylowgs_model_review.md)；[B06 L43](tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/README.md)。

**T054 同一分子共現（same-molecule co-occurrence）**

兩個變異在同一來源 DNA 分子上被共同觀測到的情形。

_別名與對照_：co-read; same-read co-occurrence; mutation-pair co-occurrence。
_用詞界線_：同一分子共現不直接給出變異先後或完整克隆身份。
_原文定位_：[HCC L270](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[A01 L35](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T055 同一細胞共存（same-cell co-occurrence）**

兩個特徵在同一可辨識細胞內被共同觀測到的情形。

_別名與對照_：cell-level co-occurrence。
_用詞界線_：兩個特徵可在不同染色體上；不可直接換成同一分子的 pair counts。
_原文定位_：[A03 L17](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A02 L61](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T141 同源染色體（homologous chromosome）**

二倍體背景中，一對帶有對應基因座的染色體之一。

_別名與對照_：homolog; homologue。
_用詞界線_：未經來源定向，不將 H1/H2 指定為父源／母源。
_原文定位_：[A01 L25](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L853](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T142 觀測互斥（observed mutual exclusivity）**

在指定觀測單位與有效資料內，兩個特徵未共同出現的情形。

_別名與對照_：mutually exclusive; negative co-occurrence。
_用詞界線_：寫明是分子、細胞或樣本互斥；未見共現不直接證明不同克隆。
_原文定位_：[HCC L226](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[A03 L11](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T143 局部先後關係（partial order）**〔支援詞〕

只限制部分事件先後，而未指定所有事件完整順序的關係。

_別名與對照_：local event order; local ancestry。
_用詞界線_：局部先後關係可以排除候選樹，但不一定決定唯一全樹。
_原文定位_：[B04 L1](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)。

**T176 參考等位基因（reference allele；REF）**

變異紀錄中，與指定參考序列對應的等位形式。

_別名與對照_：reference base; ref allele。
_用詞界線_：REF 不表示正常細胞來源，也不保證是演化祖先狀態。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L34](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T177 替代等位基因（alternate allele；ALT）**

變異紀錄中，相對 REF 所記錄的另一等位形式。

_別名與對照_：alternative allele; alt allele。
_用詞界線_：ALT 不自動表示體細胞來源；多等位位置可有多個 ALT。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)。

### 比例與觀測

**T056 變異等位基因比例（variant allele fraction；VAF）**

在指定計數規則下，ALT 支持數占 REF 與 ALT 支持總數的比例。

_別名與對照_：variant allele frequency; 變異等位基因頻率。
_用詞界線_：統一寫 fraction／比例；多等位位點與缺失值須另定分母。
_原文定位_：[HCC L7](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[PC L8](phyclone_research/notes/04_CODE_MAPPING.md)。

**T057 癌細胞比例（cancer cell fraction；CCF）**

全部癌細胞中，攜帶指定突變或事件的細胞比例。

_別名與對照_：cellular prevalence (PhyClone); 細胞盛行率（須核對分母）。
_用詞界線_：在無流失的繼承模型中，節點 CCF 包含該節點及其後代；其他文獻的 prevalence 須另核對分母。
_原文定位_：[HCC L18](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L5](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)。

**T058 克隆專有比例（exclusive clone fraction）**

全部癌細胞中，僅屬於指定克隆而不屬於其後代克隆的細胞比例。

_別名與對照_：clonal prevalence (PhyClone); clone-exclusive fraction; 克隆盛行率。
_用詞界線_：文獻的 clonal prevalence 或 clone fraction 可能另有定義，引用前先核對分母。
_原文定位_：[HCC L31](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L9](phyclone_research/notes/05_EVIDENCE_MATRIX.md)。

**T059 腫瘤細胞純度（cellular tumor purity）**

樣本全部細胞中，腫瘤細胞所占的比例。

_別名與對照_：tumour content (PhyClone); cellular purity; tumor purity。
_用詞界線_：purity 未定義時先釐清；不要直接用腫瘤 DNA 比例代入。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T060 腫瘤 DNA 比例（tumor DNA fraction）**

總 DNA 中，來自腫瘤細胞的 DNA 所占比例。

_別名與對照_：tumour DNA fraction。
_用詞界線_：與腫瘤細胞純度的換算取決於每細胞 DNA 量。
_原文定位_：[A01 L37](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A03 L21](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T061 名目混合比例（nominal mixture fraction）**〔支援詞〕

實驗設計指定的腫瘤與正常來源混合比例。

_別名與對照_：nominal purity; design tumor fraction; target-depth mixture。
_用詞界線_：tX_nY 是設計標籤；不是實測細胞純度或 DNA 比例。同一細胞株的各 tX_nY 只是同一腫瘤 DNA 的稀釋，CCF 相同；不要當成多部位樣本。
_原文定位_：[HCC L103](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)。

**T062 參考與替代等位支持數（reference and alternate allele counts）**

依指定過濾與計數單位，分別支持 REF 與 ALT 的觀測數。

_別名與對照_：REF/ALT counts; ref_counts/alt_counts。
_用詞界線_：寫明計數單位是讀段、分子或 UMI；避免重複計數。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)。

**T063 定序深度（sequencing depth）**

在指定位點或指定範圍內，符合規則的讀段覆蓋量。

_別名與對照_：read depth; coverage depth; coverage。
_用詞界線_：區分平均深度與位點深度；coverage 也可能指覆蓋廣度。
_原文定位_：[HCC L13](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L28](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

**T064 共同覆蓋深度（joint coverage）**〔支援詞〕

同時覆蓋指定兩個位置，且在兩處均可判讀的觀測數。

_別名與對照_：pair coverage; spanning-read count。
_用詞界線_：n11 為零的意義取決於共同覆蓋深度與錯誤模型。
_原文定位_：[B04 L22](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)。

**T065 缺失觀測（missing observation）**

在指定位置沒有可採用判定的資料狀態。

_別名與對照_：missingness; no-call; missing genotype。
_用詞界線_：缺失觀測不等於 REF，也不等於突變不存在。
_原文定位_：[PC L29](phyclone_research/notes/zh-TW/06_ASSUMPTIONS_LIMITATIONS.md)；[A03 L33](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T066 比對品質（mapping quality；MAPQ）**

描述讀段定位可信程度的品質值。

_別名與對照_：MQ; mapping confidence。
_用詞界線_：與鹼基品質分開；數值的校準依比對器而異。
_原文定位_：[HCC L18](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[B03 L21](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T067 鹼基品質（base quality；BQ）**

描述指定鹼基判讀可信程度的品質值。

_別名與對照_：base-call quality。
_用詞界線_：與讀段比對品質分開。
_原文定位_：[HCC L18](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[A03 L1282](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/paper.txt)。

### 資料與定序

**T068 讀段（sequencing read）**

定序儀對核酸序列產生的一筆讀取結果。

_別名與對照_：read; 讀序。
_用詞界線_：「讀段」指物件；「讀長」指長度。
_原文定位_：[HCC L3](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T069 長讀長定序（long-read sequencing）**

直接讀取較長連續核酸片段的定序技術。

_別名與對照_：long-read; long read; 長讀序定序。
_用詞界線_：ONT 與 PacBio 屬此類；不要把所有長距離定相都稱為長讀長定序。
_原文定位_：[HCC L3](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A01 L9](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T070 連鎖短讀段（linked reads）**

以共同條碼把來自同一長分子的短讀段連接起來的資料。

_別名與對照_：linked-read sequencing; linked short reads。
_用詞界線_：10x linked reads 不等於實測的 ONT／PacBio 長讀段。
_原文定位_：[A01 L9](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L9](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T071 長距離定相（long-range phasing）**〔支援詞〕

在較長基因組範圍內建立變異單倍型關係的方法。

_別名與對照_：long-range haplotyping; chromosome-length phasing。
_用詞界線_：可由長讀段、條碼、Strand-seq 或統計方法取得，須寫明來源。
_原文定位_：[A04 L1](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)。

**T072 混合樣本定序（bulk sequencing）**

將多個細胞的核酸混合後量測的定序方式。

_別名與對照_：bulk WGS/WES; bulk data。
_用詞界線_：bulk 的等位比例是混合訊號，不直接提供單細胞基因型。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T073 單細胞 DNA 定序（single-cell DNA sequencing；scDNA-seq）**

在可辨識的單細胞單位量測 DNA 的定序方式。

_別名與對照_：scDNA; single-cell DNA。
_用詞界線_：依測量區分 targeted DNA 與全基因組 DNA；不等於 scRNA-seq。
_原文定位_：[HCC L66](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[A01 L1](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T074 單核 DNA 定序（single-nucleus DNA sequencing；snDNA-seq）**〔支援詞〕

以可辨識的單一細胞核為單位量測 DNA 的定序方式。

_別名與對照_：snDNA; single-nucleus DNA。
_用詞界線_：記錄核的分離方法；不把細胞核數直接等同原始組織細胞比例。
_原文定位_：[A03 L3](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T075 單細胞 RNA 定序（single-cell RNA sequencing；scRNA-seq）**

在可辨識的單細胞單位量測 RNA 的定序方式。

_別名與對照_：scRNA; single-cell transcriptome。
_用詞界線_：由 RNA 推定的 CNV 須標明是模型估計。
_原文定位_：[A03 L9](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A01 L31](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T076 單細胞全基因組定序（single-cell whole-genome sequencing；scWGS）**

以單細胞為單位，在全基因組範圍量測 DNA 的定序方式。

_別名與對照_：single-cell WGS。
_用詞界線_：低深度 scWGS 不代表每個位置都有可用的 SNV 判定。
_原文定位_：[A01 L9](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L9](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T077 全基因組定序（whole-genome sequencing；WGS）**

在全基因組範圍取得序列的定序方式。

_別名與對照_：whole genome sequencing。
_用詞界線_：WGS 不代表每個位置皆可判讀；另寫明深度與有效區域。
_原文定位_：[HCC L5](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[PC L18](phyclone_research/notes/07_PRESENTATION_BRIEF.md)。

**T078 全外顯子定序（whole-exome sequencing；WES）**

以富集外顯子區域為目標的定序方式。

_別名與對照_：exome sequencing。
_用詞界線_：與 WGS 的可判讀範圍及 CN 解析度分開。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[A03 L9](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)。

**T079 單細胞衍生培養株（single-cell-derived culture）**〔支援詞〕

由一個起始細胞培養擴增得到的細胞群。

_別名與對照_：single-cell-derived subline; clonal subline。
_用詞界線_：其 bulk 定序不是直接單細胞定序；培養期間可能新增變異。
_原文定位_：[B01 L1](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)。

**T080 偽混合樣本（pseudobulk）**

依指定細胞或克隆分組，將單細胞觀測合併得到的資料。

_別名與對照_：pseudo-bulk。
_用詞界線_：記錄組成與合併方式；不得當成額外獨立樣本。
_原文定位_：[A01 L23](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L17](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T081 無細胞 DNA（cell-free DNA；cfDNA）**〔支援詞〕

存在於細胞外的 DNA。

_別名與對照_：circulating cell-free DNA。
_用詞界線_：cfDNA 可來自正常或腫瘤細胞；不等於 ctDNA。
_原文定位_：[A01 L1](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T082 細胞株（cell line）**

可在培養條件下持續維持與擴增的細胞群。

_別名與對照_：cultured cell line。
_用詞界線_：細胞株的參考結果不自動代表病人原位腫瘤的完整歷史。
_原文定位_：[HCC L5](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[A01 L9](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T083 配對正常樣本（matched normal sample）**

來自同一個體，用於比較腫瘤變異的正常來源樣本。

_別名與對照_：matched normal; tumor–normal pair。
_用詞界線_：配對正常仍可能有嵌合變異或培養改變，須按實驗設計解讀。
_原文定位_：[HCC L8](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[B04 L20](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)。

**T084 DNA 甲基化（DNA methylation）**

DNA 上的甲基化修飾狀態。

_別名與對照_：methylation; 甲基化。
_用詞界線_：甲基化差異不是序列變異，也不單獨證明克隆祖先關係。
_原文定位_：[A05 L25](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)；[A02 L1297](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T085 差異甲基化區域（differentially methylated region；DMR）**

依指定比較群組與統計規則，判定甲基化程度不同的基因組區段。

_別名與對照_：differential methylation region。
_用詞界線_：記錄區段定義與判定規則；甲基化群集不直接等於遺傳克隆。
_原文定位_：[B01 L13](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)；[B04 L113](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/supplement.txt)。

**T086 表型（phenotype）**

細胞或樣本可觀測的功能、形態或其他特徵。

_別名與對照_：cell phenotype; phenotypic feature。
_用詞界線_：表型群集不等於遺傳克隆。
_原文定位_：[A02 L11](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)；[A01 L31](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T144 DNA 分子（DNA molecule）**

實際承載 DNA 序列的分子單位。

_別名與對照_：native DNA molecule; source molecule。
_用詞界線_：一個分子可產生多筆讀段；讀段數不一定等於獨立分子數。
_原文定位_：[A02 L23](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)；[A01 L99](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T145 來源條碼（source barcode）**

用來識別觀測來源的序列標籤。

_別名與對照_：cell barcode; molecule barcode。
_用詞界線_：細胞條碼、分子條碼與 UMI 各有用途，須明示標籤層級。
_原文定位_：[A03 L27](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A04 L2439](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/paper.txt)。

**T146 樣本（sample）**

一次採樣或指定實驗製備得到的材料單位。

_別名與對照_：specimen。
_用詞界線_：樣本可含多種細胞與多個克隆；不等於一個克隆。
_原文定位_：[HCC L5](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T147 多部位取樣（multisite sampling）**

從同一來源的不同解剖位置或區域取得樣本的設計。

_別名與對照_：multiregion sampling; spatial sampling。
_用詞界線_：區分同病人多部位與不同病人的樣本。
_原文定位_：[A03 L9](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[B01 L521](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T148 縱向取樣（longitudinal sampling）**

從同一來源在不同時間取得樣本的設計。

_別名與對照_：serial sampling; time-series sampling。
_用詞界線_：時間標籤提供採樣順序，不直接給出每次突變的時間。
_原文定位_：[A01 L9](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)；[A02 L29](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T149 目標區域定序（targeted sequencing）**

以預先選定的基因組區域為量測目標的定序方式。

_別名與對照_：targeted panel; targeted DNA sequencing。
_用詞界線_：目標區域內的基因型一致，不代表全基因組一致。
_原文定位_：[A01 L1441](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)；[A03 L70](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/paper.txt)。

**T150 病人衍生異種移植（patient-derived xenograft；PDX）**

將病人材料移植至另一物種宿主形成的實驗模型。

_別名與對照_：patient derived xenograft。
_用詞界線_：移植與擴增可能改變克隆組成，須與原始病人樣本分開。
_原文定位_：[A04 L9](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md)；[A01 L1252](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T151 基因表現（gene expression）**

指定細胞或樣本中，基因產物的表現量。

_別名與對照_：transcript abundance。
_用詞界線_：RNA 表現量不同不直接表示 DNA 拷貝數或基因型不同。
_原文定位_：[B02 L21](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/README.md)；[A01 L1617](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T152 表觀遺傳狀態（epigenetic state）**

以 DNA 或染色質修飾等特徵描述的細胞狀態。

_別名與對照_：epigenomic state。
_用詞界線_：明示量測特徵；表觀遺傳相似度不直接等於遺傳祖先關係。
_原文定位_：[B01 L5](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)；[A02 L1315](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T178 讀長（read length）**

一筆讀段所包含的序列長度。

_別名與對照_：sequence read length。
_用詞界線_：明示原始讀長、裁切後讀長或有效比對跨度。
_原文定位_：[HCC L13](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/04_confidence_and_limits.md)；[B04 L34](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/supplement.txt)。

**T179 循環腫瘤 DNA（circulating tumor DNA；ctDNA）**

循環無細胞 DNA 中，來自腫瘤細胞的部分。

_別名與對照_：circulating tumour DNA。
_用詞界線_：ctDNA 是 cfDNA 的子集合；其含量受釋放與清除過程影響。
_原文定位_：[A02 L19](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)；[A01 L47](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T180 BAM 比對格式（Binary Alignment/Map format；BAM）**

以二進位儲存序列比對紀錄的格式。

_別名與對照_：BAM file; BAM alignment。
_用詞界線_：讀段標籤的意義依格式規格與產生工具解讀。
_原文定位_：[HCC L37](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[PC L26](phyclone_research/notes/00_SOURCE_MAP.md)。

**T181 CRAM 比對格式（CRAM format；CRAM）**〔支援詞〕

以壓縮方式儲存序列比對紀錄的格式。

_別名與對照_：CRAM file。
_用詞界線_：依壓縮模式可能需要相符的參考序列解碼，須保留參考版本。
_原文定位_：[SYN L3](tumor_phylogeny_2026/REPO_IMPROVEMENTS.md)。

**T182 VCF 變異格式（Variant Call Format；VCF）**

以標頭與資料列記錄變異及其註解的格式。

_別名與對照_：VCF file; variant-call file。
_用詞界線_：FORMAT 的 AF 等欄位依標頭定義解讀，不預設等於 CCF 或族群頻率。
_原文定位_：[HCC L84](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[PC L26](phyclone_research/notes/00_SOURCE_MAP.md)。

**T183 BED 區間格式（Browser Extensible Data format；BED）**〔支援詞〕

以基因組區間為核心記錄資料的文字格式。

_別名與對照_：BED file。
_用詞界線_：標準 BED 使用從零起算、右端不包含的區間，轉換座標時須核對。
_原文定位_：[B05 L963](tumor_phylogeny_2026/papers/B05_medicc2_2022/paper.txt)。

**T184 FASTQ 序列格式（FASTQ format；FASTQ）**

同時儲存讀段序列與逐鹼基品質值的文字格式。

_別名與對照_：FASTQ file。
_用詞界線_：FASTQ 不是比對結果；座標須經比對流程取得。
_原文定位_：[A03 L27](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A01 L1457](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T185 唯一分子識別碼（unique molecular identifier；UMI）**

用來辨識來源分子並協助處理擴增重複的序列標籤。

_別名與對照_：molecular identifier。
_用詞界線_：UMI 不等於細胞條碼；錯誤與碰撞的處理依分析流程而定。
_原文定位_：[A05 L602](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/paper.txt)；[B02 L1020](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/paper.txt)。

**T187 細胞狀態（cell state）**

在指定時點，以功能、表現或分化特徵描述的細胞狀態。

_別名與對照_：transcriptional state; differentiation state。
_用詞界線_：相同克隆可有不同細胞狀態；狀態改變不直接表示新增遺傳事件。
_原文定位_：[A01 L32](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)；[A05 L294](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/paper.txt)。

### 模型與推論

**T087 觀測模型（observation model）**

描述潛在生物狀態如何產生觀測資料的機率模型。

_別名與對照_：emission model; 發射分布。
_用詞界線_：指定計數單位、錯誤模型與條件變數。
_原文定位_：[HCC L19](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L16](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)。

**T088 概似（likelihood）**

將已觀測資料視為固定後，用來比較不同參數或模型的資料機率函數。

_別名與對照_：似然; likelihood function。
_用詞界線_：統一寫「概似」；概似值不是模型為真的機率。
_原文定位_：[HCC L15](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T089 先驗分布（prior distribution）**

納入本次資料前，模型對未知量指定的機率分布。

_別名與對照_：prior; 先驗。
_用詞界線_：先驗可包含偏好與限制，不等於已證實的生物事實。
_原文定位_：[HCC L297](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T090 後驗分布（posterior distribution）**

在模型與先驗下，納入觀測資料後得到的未知量機率分布。

_別名與對照_：posterior; 後驗。
_用詞界線_：報告時交代模型、先驗與近似推論方式。
_原文定位_：[HCC L29](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md)；[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T091 邊際化（marginalization）**

對未直接報告的未知量加總或積分，得到其餘未知量的分布或概似。

_別名與對照_：integrating out; 積分消去。
_用詞界線_：邊際化不是把未知量設為固定最佳值。
_原文定位_：[PC L5](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)；[B03 L36](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T092 二項觀測模型（binomial observation model）**

在固定試驗次數與成功機率下，描述成功計數的模型。

_別名與對照_：Binomial; 二項分布。
_用詞界線_：讀段存在依賴或額外變異時，須檢查此模型是否適用。
_原文定位_：[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)；[PW L29](hcc1395_golden_tree_research/phylowgs_model_review.md)。

**T093 貝他二項觀測模型（beta-binomial observation model）**

讓成功機率依貝他分布變動，再描述計數的模型。

_別名與對照_：Beta-Binomial; beta binomial。
_用詞界線_：可表示相對二項分布的過度離散；參數化方式須明示。
_原文定位_：[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)；[B03 L17](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T094 馬可夫鏈蒙地卡羅（Markov chain Monte Carlo；MCMC）**

利用馬可夫鏈抽樣來近似目標分布的方法。

_別名與對照_：MCMC sampling。
_用詞界線_：須檢查混合與收斂；抽樣次數多不直接證明結果可靠。
_原文定位_：[HCC L43](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

**T095 序列蒙地卡羅（sequential Monte Carlo；SMC）**〔支援詞〕

以帶權重粒子序列近似一連串目標分布的方法。

_別名與對照_：SMC sampling; SMC sampler。
_用詞界線_：說明粒子數與重抽樣規則；SMC 步驟不一定是生物時間，粒子濾波是其應用之一。
_原文定位_：[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T096 最大後驗估計（maximum a posteriori estimate；MAP）**

選取指定後驗目標中，機率或密度最高的狀態作為摘要。

_別名與對照_：MAP tree; maximum a posteriori。
_用詞界線_：區分最高分聯合狀態與對其他狀態加總後的最高機率拓樸。
_原文定位_：[PC L27](phyclone_research/notes/05_EVIDENCE_MATRIX.md)；[B03 L39](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T097 共識樹（consensus tree）**

依指定支持度與相容性規則，彙整多棵樹得到的摘要樹。

_別名與對照_：consensus phylogeny。
_用詞界線_：寫明共識規則；它不一定等於任一抽到的樹或 MAP 樹。
_原文定位_：[PC L35](phyclone_research/notes/04_CODE_MAPPING.md)；[B03 L19](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T098 離群模型（outlier model）**

以額外成分表示不符合主要模型之資料的模型。

_別名與對照_：outlier mixture; 離群值模型。
_用詞界線_：離群標籤不直接判定資料是技術錯誤或真實突變流失。
_原文定位_：[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)；[A02 L1271](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T099 無限位點假設（infinite-sites assumption；ISA）**

在指定演化範圍內，每個位點最多發生一次突變且不再逆轉的假設。

_別名與對照_：infinite sites; infinite-sites model。
_用詞界線_：PhyClone 的樹內繼承另要求後代保留突變；允許 CNA 造成流失時，須說明模型處理方式。
_原文定位_：[PC L5](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)；[PW L145](hcc1395_golden_tree_research/phylowgs_model_review.md)。

**T100 可識別性（identifiability）**

在指定觀測與模型下，不同未知狀態能否被區分的性質。

_別名與對照_：identifiable topology; 可辨識性。
_用詞界線_：不確定區間小不直接證明模型可識別或假設正確。
_原文定位_：[PC L89](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)；[A02 L35](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T101 事件最簡原則（event parsimony）**

以較少或較低成本的事件解釋觀測差異的選模原則。

_別名與對照_：maximum parsimony; minimum-event reconstruction。
_用詞界線_：事件成本與允許事件不同，得到的歷史可能不同。
_原文定位_：[B03 L27](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)；[A01 L127](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。

**T153 最大概似估計（maximum likelihood estimate；MLE）**

選取使觀測資料概似最大的參數或模型狀態。

_別名與對照_：maximum-likelihood inference; ML estimate。
_用詞界線_：與包含先驗分布的 MAP 分開。
_原文定位_：[B07 L23](tumor_phylogeny_2026/papers/B07_numbat_2022/README.md)；[B01 L650](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T154 邊際概似（marginal likelihood）**

對指定未知量依其分布加總或積分後，得到的資料概似。

_別名與對照_：collapsed likelihood; integrated likelihood。
_用詞界線_：寫明消去了哪些未知量；不同邊際化範圍可能不是同一分數。
_原文定位_：[HCC L318](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L16](phyclone_research/notes/04_CODE_MAPPING.md)。

**T155 後驗不確定性（posterior uncertainty）**

在指定模型與資料下，後驗分布仍支持多種狀態的程度。

_別名與對照_：topology uncertainty; assignment uncertainty。
_用詞界線_：分別說明拓樸、事件位置與比例的不確定性。
_原文定位_：[PC L7](phyclone_research/notes/05_EVIDENCE_MATRIX.md)；[B01 L34](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)。

**T156 貝氏可信區間（credible interval）**〔支援詞〕

在指定後驗分布下，包含給定機率質量的區間。

_別名與對照_：Bayesian credible interval; 後驗區間。
_用詞界線_：與頻率學派信賴區間分開，並標明區間機率與計算方式。
_原文定位_：[A05 L19](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)。

**T157 信賴區間（confidence interval）**

由抽樣程序構造，並以重複抽樣涵蓋率定義的參數區間。

_別名與對照_：frequentist confidence interval。
_用詞界線_：例如 95% 指程序的長期涵蓋率，不直接表示固定參數有 95% 機率在該區間內。
_原文定位_：[A05 L19](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)；[A02 L555](tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt)。

**T158 隱藏式馬可夫模型（hidden Markov model；HMM）**

以滿足馬可夫性質的隱藏狀態序列，產生對應觀測序列的機率模型。

_別名與對照_：Hidden Markov Model。
_用詞界線_：用於 CN 分段時，隱藏狀態可代表 CN；其序列位置不等於演化時間。
_原文定位_：[HCC L55](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[B03 L17](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md)。

**T159 鄰接法（neighbor joining；NJ）**

由成對距離逐步連接節點來建立樹的方法。

_別名與對照_：neighbour joining; neighbor-joining。
_用詞界線_：通常先得到無根樹；生物祖先方向須另有定根依據。
_原文定位_：[B05 L13](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md)；[A03 L53](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/paper.txt)。

**T160 提議分布（proposal distribution）**

抽樣演算法用來產生下一個候選狀態的機率分布。

_別名與對照_：proposal kernel。
_用詞界線_：提議分布不是目標後驗分布。
_原文定位_：[HCC L297](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

**T161 暖機期（burn-in）**

正式保留抽樣結果前，依指定規則捨棄或調整狀態的階段。

_別名與對照_：warm-up; burn in。
_用詞界線_：說明實際演算法；PhyClone 的啟發式 SMC 暖機不當作後驗證據。
_原文定位_：[HCC L37](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

**T162 鏈混合（chain mixing）**

抽樣鏈在目標分布支持的狀態之間移動的效率。

_別名與對照_：MCMC mixing; sampler mixing。
_用詞界線_：接受率高不一定表示能在不同拓樸間充分移動。
_原文定位_：[PC L25](phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md)；[PW L127](hcc1395_golden_tree_research/phylowgs_model_review.md)。

**T188 鏈收斂（chain convergence）**

抽樣鏈的分布接近指定目標分布的情形。

_別名與對照_：MCMC convergence。
_用詞界線_：有限診斷只能提供收斂證據；不能單憑鏈長或單一接受率宣稱已收斂。
_原文定位_：[HCC L62](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[B03 L1796](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/paper.txt)。

### 驗證與證據

**T102 參考基因組（reference genome）**

提供序列比對與基因組座標的參考序列。

_別名與對照_：reference assembly; genome build。
_用詞界線_：記錄版本與 contig 命名；不可簡稱為樣本真值。
_原文定位_：[HCC L63](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)；[B05 L28](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md)。

**T103 變異判定集合（variant call set）**

依指定流程判定為變異的一組紀錄。

_別名與對照_：callset; call set; 變異呼叫集合。
_用詞界線_：與經驗證且有適用範圍的評估真值集分開。
_原文定位_：[HCC L1](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[A03 L1395](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/paper.txt)。

**T104 可判讀區域（callable region）**〔支援詞〕

在指定資料與品質規則下，可以進行變異判定的基因組區域。

_別名與對照_：evaluable region; callable genome。
_用詞界線_：區域外沒有 call 不表示沒有變異；與高可信度評估區域分開記錄。
_原文定位_：[HCC L14](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/04_confidence_and_limits.md)。

**T105 參考演化樹（reference phylogeny）**

供比較或評估使用，且具有明確來源與限制的演化樹。

_別名與對照_：reference tree; candidate reference tree。
_用詞界線_：由資料推斷的參考樹不直接等於完整歷史真值。
_原文定位_：[HCC L1](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L5](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)。

**T106 評估真值（ground truth）**

在指定評估範圍內，用作正確答案的資料或事件紀錄。

_別名與對照_：truth set; 評估真值集; golden truth。
_用詞界線_：寫明來源、版本與適用單位；變異真值不能升格為整棵樹的真值。
_原文定位_：[HCC L7](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md)；[PC L16](phyclone_research/notes/zh-TW/03_EXPERIMENTS_RESULTS.md)。

**T107 正交驗證（orthogonal validation）**

用測量機制不同的資料，檢查指定結果的驗證方式。

_別名與對照_：orthogonal assay; independent validation。
_用詞界線_：說明共享的樣本、前處理與模型；多工具同意不一定是獨立驗證。
_原文定位_：[HCC L11](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A02 L19](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T108 邊支持度（edge support）**

在指定重抽樣或後驗樹集合中，某條邊被保留或出現的程度。

_別名與對照_：branch support; edge posterior support。
_用詞界線_：先指定邊、演化支或祖先關係等評估對象；後驗機率、bootstrap 比例與正確率不可互換。
_原文定位_：[HCC L18](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md)；[A01 L35](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T109 留出驗證（holdout validation）**

以建模時未使用的觀測，評估模型預測或一致性的方法。

_別名與對照_：held-out validation; hold-out test。
_用詞界線_：若特徵產生已看過留出資料，仍可能存在資料洩漏。
_原文定位_：[HCC L34](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)；[A01 L37](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T110 資料洩漏（data leakage）**〔支援詞〕

評估資料的資訊進入建模或特徵建立流程，導致評估偏高的情形。

_別名與對照_：tagging leakage; information leakage。
_用詞界線_：留出切分需涵蓋定相、標記與特徵建立的資訊來源。
_原文定位_：[SYN L113](tumor_phylogeny_2026/REPO_IMPROVEMENTS.md)。

**T111 抽樣偏差（sampling bias）**〔支援詞〕

採樣或保留規則使觀測組成偏離目標群體的情形。

_別名與對照_：selection bias; ascertainment bias。
_用詞界線_：區分組織採樣、細胞篩選、比對與標記造成的偏差。
_原文定位_：[A05 L33](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)。

**T112 等位基因脫落（allelic dropout；ADO）**

細胞具有某個等位基因，但該等位基因未被成功觀測的現象。

_別名與對照_：allele dropout。
_用詞界線_：未觀測到 ALT 不足以判定野生型或突變流失。
_原文定位_：[A03 L11](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[A05 L23](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)。

**T113 雙細胞混入（doublet）**

兩個細胞被當成一個單細胞觀測單位的情形。

_別名與對照_：cell doublet。
_用詞界線_：可能產生假的共存訊號；與真實單細胞多突變分開。
_原文定位_：[A03 L23](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md)；[B03 L2225](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/paper.txt)。

**T114 偽陽性（false positive；FP）**

依指定評估真值，本來不屬於陽性卻被判為陽性的結果。

_別名與對照_：false-positive call。
_用詞界線_：須先固定可評估區域、比對規則與判定單位。
_原文定位_：[HCC L9](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/04_confidence_and_limits.md)；[A05 L17](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)。

**T163 受控模擬（controlled simulation）**

依指定生成機制產生資料，以檢查推論結果的分析。

_別名與對照_：synthetic data; simulated benchmark。
_用詞界線_：生成樹可作模擬真值；不等於已知病人的完整歷史。
_原文定位_：[PC L5](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)；[A02 L37](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md)。

**T164 消融比較（ablation study）**

固定其他條件，加入或移除指定資訊以比較結果的設計。

_別名與對照_：ablation; feature ablation。
_用詞界線_：同時改變深度、分群與模型時，難以單獨歸因效益。
_原文定位_：[PC L17](phyclone_research/notes/05_EVIDENCE_MATRIX.md)；[B01 L27](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)。

**T165 重抽樣（resampling）**

依指定單位與規則，再次抽取觀測或模型狀態的程序。

_別名與對照_：resampling step; 重新抽樣。
_用詞界線_：bootstrap 與粒子重抽樣是不同設計；須指定分子、細胞、區段或粒子單位。
_原文定位_：[HCC L39](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)；[PC L21](phyclone_research/notes/04_CODE_MAPPING.md)。

**T166 精確率（precision）**

在判定為陽性的結果中，依指定真值屬於真陽性的比例。

_別名與對照_：positive predictive value; PPV。
_用詞界線_：精確率為 TP/(TP+FP)；不要與整體正確率 accuracy 混用。
_原文定位_：[HCC L48](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[A01 L37](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md)。

**T167 召回率（recall）**

在依指定真值屬於陽性的結果中，被成功判為陽性的比例。

_別名與對照_：sensitivity; true positive rate。
_用詞界線_：召回率為 TP/(TP+FN)；須固定評估範圍。
_原文定位_：[HCC L48](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)；[PC L18](phyclone_research/notes/zh-TW/06_ASSUMPTIONS_LIMITATIONS.md)。

**T168 F1 分數（F1 score；F1）**

精確率與召回率的調和平均數。

_別名與對照_：F-score (F1)。
_用詞界線_：F1 為 2PR/(P+R)；說明評估的是變異、指派或祖先關係。
_原文定位_：[PC L14](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)；[B01 L602](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。

**T169 調整蘭德指數（adjusted Rand index；ARI）**〔支援詞〕

比較兩份分群指派，並校正隨機一致性的指標。

_別名與對照_：adjusted Rand score。
_用詞界線_：分群相同不代表祖先關係或拓樸相同。
_原文定位_：[SYN L88](tumor_phylogeny_2026/REPO_IMPROVEMENTS.md)。

**T170 V-measure（V-measure）**〔支援詞〕

以同質性與完整性的調和平均，評估兩份分群指派的一致程度。

_別名與對照_：V measure。
_用詞界線_：它評估分群；不能單獨當作演化樹正確率。
_原文定位_：[PC L13](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

**T171 樹距離（tree distance）**

依指定規則，比較兩棵樹結構差異的數值。

_別名與對照_：Robinson–Foulds distance; RF distance; tree edit distance。
_用詞界線_：比較前須確認節點單位、標籤、定根方式及未解析節點的處理相容。
_原文定位_：[B04 L48](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)；[B05 L218](tumor_phylogeny_2026/papers/B05_medicc2_2022/paper.txt)。

**T189 偽陰性（false negative；FN）**

依指定評估真值，本來屬於陽性卻未被判為陽性的結果。

_別名與對照_：false-negative call。
_用詞界線_：未量測或不可評估的資料，不自動視為偽陰性。
_原文定位_：[A05 L17](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md)；[B01 L15](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md)。

### 方法補充

**T115 粒子 Gibbs 抽樣（Particle Gibbs；PG）**〔方法補充〕

以條件式 SMC 更新粒子路徑的 MCMC 方法。

_別名與對照_：particle Gibbs sampling。
_用詞界線_：與單次無條件 SMC 分開；PhyClone 的暖機程序另有目的。
_原文定位_：[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T116 粒子權重有效樣本數（particle-weight effective sample size；particle ESS）**〔方法補充〕

依正規化粒子權重的不均勻程度，估計有效粒子數的指標。

_別名與對照_：SMC ESS; weight-based ESS。
_用詞界線_：ESS 為 1/Σw²；與 relative ESS 及 MCMC ESS 分開。
_原文定位_：[PC L22](phyclone_research/notes/04_CODE_MAPPING.md)。

**T117 MCMC 有效樣本數（MCMC effective sample size；MCMC ESS）**〔方法補充〕

依鏈的自相關，估計某個統計量相當於多少獨立抽樣的指標。

_別名與對照_：chain ESS; autocorrelation-based ESS。
_用詞界線_：須指定統計量；與粒子權重 ESS 使用不同定義。
_原文定位_：[Stan 官方定義](https://mc-stan.org/docs/2_40/reference-manual/analysis.html)；本次語料未找到獨立使用實例。

**T118 樹表示重數（tree-representation multiplicity）**〔方法補充〕

同一樹狀結構在指定表示法下，具有的等價排列數。

_別名與對照_：topology multiplicity; ordering multiplicity。
_用詞界線_：此處 multiplicity 是組合計數，不是突變等位基因拷貝數。
_原文定位_：[PC L89](phyclone_research/notes/02_METHODS_DEEP_DIVE.md)。

**T119 有根森林（rooted forest）**〔方法補充〕

由一棵或多棵互不相連的有根樹構成的結構。

_別名與對照_：rooted forest structure。
_用詞界線_：PhyClone 可加入虛擬根連接各棵樹；虛擬根不代表生物共同祖先。
_原文定位_：[PC L8](phyclone_research/notes/05_EVIDENCE_MATRIX.md)。

**T120 樹結構折棒過程（tree-structured stick-breaking process；TSSB）**〔方法補充〕

以階層式折棒權重表示樹上分配的隨機過程。

_別名與對照_：tree structured stick breaking。
_用詞界線_：保留 TSSB，避免與 PhyClone 的森林結構 CRP 先驗互換。
_原文定位_：[HCC L194](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)；[PC L7](phyclone_research/notes/03_EXPERIMENTS_RESULTS.md)。

**T121 森林結構 CRP 先驗（forest-structured Chinese restaurant process prior；FS-CRP）**〔方法補充〕

結合突變分割與有根森林結構的先驗模型。

_別名與對照_：FSCRP; forest-structured CRP。
_用詞界線_：與 PhyloWGS 的 TSSB 是不同先驗模型。
_原文定位_：[PC L5](phyclone_research/notes/01_PAPER_BIG_PICTURE.md)。

**T122 順式與反式相位（cis and trans phase）**〔方法補充〕

在同一細胞或指定基因組中，順式指兩變異位於同一染色體拷貝；反式指分處對應同源拷貝。

_別名與對照_：cis/trans phasing。
_用詞界線_：相同 HP 標籤不足以確認順式；此用法與 Numbat 的 cis/trans 表現效應分開。
_原文定位_：[原始研究的 cis/trans 定義](https://pubmed.ncbi.nlm.nih.gov/11380938/)；本次語料未找到此相位用法。

**T123 區域內與區域外表現效應（cis and trans expression effects）**〔方法補充〕

本批 Numbat 文獻中，分別指 CNV 區域內與區域外的基因表現效應。

_別名與對照_：cis/trans effects (Numbat)。
_用詞界線_：這是該文的效應分類；不表示突變位於相同或不同單倍型。
_原文定位_：[B07 L383](tumor_phylogeny_2026/papers/B07_numbat_2022/paper.txt)。

**T190 相對粒子有效樣本數（relative particle effective sample size；relative ESS）**〔方法補充〕

粒子權重 ESS 除以粒子總數得到的比例。

_別名與對照_：relative ESS; normalized particle ESS。
_用詞界線_：其範圍通常為 1/N 到 1；與未正規化的粒子 ESS 分開。
_原文定位_：[PC L22](phyclone_research/notes/04_CODE_MAPPING.md)。
