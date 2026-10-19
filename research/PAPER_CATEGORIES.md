---
doc_role: paper_classification_index
source_of_truth: paper_categories.tsv
regenerate: python3 research/tools/sync_paper_categories.py
keywords_en: [paper classification, short read, long read, single-cell truth tree, platform, category index]
keywords_zh: [論文分類, 短讀, 長讀, 單細胞真值樹, 定序平台, 分類索引]
---

# 論文分類索引：定序平台 × single-cell 真值

分類日：2026-10-18。共 22 份文獻：`tumor_phylogeny_2026/` 的 A01–A05、B01–B08、M01–M07、R01，以及 HCC1395 golden tree（H01）。`phyclone_research/` 與 M01 是同一篇論文。

每篇先由 5 個平行 subagent 讀 README 與全文，再由協調者統一判定邊界案例。這是**分析推論**，證據行號寫在各篇 README。

## 先看結論

| 類別 | 篇數 | 論文 |
|---|---|---|
| **C1** 短讀或未說平台（無 sc 真值） | 6 | B02、B07、M02、M04、M05、M07 |
| **C2** long-read 特徵輔助建樹（無 sc 真值） | 4 | M03、B06、B08、B01（弱） |
| **C3a** single-cell 真值樹 × 短讀 | 11 | A01–A05、B03、R01、M01、M06、B05、H01 |
| **C3b** single-cell 真值樹 × long-read 特徵 | 1 | B04 |

- 只有 **B04** 同時具備 long-read 特徵與 single-cell 驗證。它的 scDNA 只做局部驗證，且與 long-read topology 篩選不在同一病人。
- 目前**沒有任何一篇**用 long-read 特徵重建完整 clone tree，再以完整 single-cell 真值樹評估。這是本 repo 的空缺。
- 與本 repo 最直接競爭的是 **M03**。它用同一批 CASTLE ONT 資料，但只有摘要。

## 分類判準

### 軸 1：建樹資料的平台（每篇必屬一類）

| 值 | 判準 |
|---|---|
| `short_or_unspecified` | Illumina 短讀、10x linked-read、Strand-seq、短讀 scDNA／scRNA、targeted PCR、模擬資料，或論文沒寫平台 |
| `long_read_feature` | 用 ONT／PacBio 原生 read，**而且** long read 獨有的特徵進入建樹、約束、排序或篩選 topology。例：同 read SNV 共現、read-based phasing／haplotag、read 跨越的 SV breakpoint |
| `long_read_data_only` | 用 ONT 資料建樹，但只用 SNV genotype，沒有 long-read 獨有特徵約束 topology（只有 B01）。歸入 C2 的弱子類 |

**規則**：long read 只用來驗證或 call variant、從不進入建樹時，平台軸仍算短讀。欄位 `long_read_role` 記為 `validation_only`（B03、H01）。

### 軸 2：single-cell 真值樹（像 PhyClone 的 HGSOC 真值）

| `sc_truth_strength` | 判準 | 論文 |
|---|---|---|
| `reference_tree` | 從病人 single-cell／single-nucleus DNA 建出參考演化樹 | A01–A05、B03、R01 |
| `benchmark_truth` | 用 single-cell 來源的樹當答案，評估方法 | M01、M06 |
| `partial` | single-cell DNA 只佐證樹的一部分 | B05、H01、B04 |
| `none` | 沒有 sc 真值：只有模擬真值、只有 scRNA、或沒有真值 | C1、C2 全部 |

**規則**：方法的輸入是 single-cell，但只用模擬評估時，不算 C3。這類論文標 `input_is_single_cell: true`（B07、M04）。

### 重疊細分

軸 2 有 sc 真值時，一定會與軸 1 重疊。所以 C3 依平台拆成 C3a（短讀）與 C3b（long read）。每類再依 `subtype` 細分：

| 類別 | subtype | 意思 | 論文 |
|---|---|---|---|
| C1 | `c1_bulk_short_read` | bulk 短讀或模擬 benchmark | M05、M07 |
| C1 | `c1_read_cooccurrence_short` | 用 read／分子共現，但資料是短讀；模型可移植到 long read | M02、B02 |
| C1 | `c1_single_cell_input_no_truth` | 輸入是 single-cell，沒有 sc 真值樹 | B07、M04 |
| C2 | `c2_local_order` | 同 read 共現排出局部突變先後 | M03 |
| C2 | `c2_sample_tree_sv` | long-read SV breakpoint 建 sample tree | B06 |
| C2 | `c2_molecular_history` | long read 排出局部 SV 分子史 | B08 |
| C2 | `c2_long_read_data_only` | ONT 資料建樹，沒有 long-read 獨有特徵（弱） | B01 |
| C3a | `c3a_patient_sc_reference` | 病人 scDNA 參考樹 | A01–A05、B03、R01 |
| C3a | `c3a_sc_benchmark_truth` | sc 來源真值當 benchmark | M01、M06 |
| C3a | `c3a_sc_partial` | sc 只部分佐證 | B05、H01 |
| C3b | `c3b_topology_constraint_sc_partial` | long read 篩選 topology，scDNA 局部驗證 | B04 |

## 邊界案例的判定

| ID | 判定 | 原因 | 另一種判法 |
|---|---|---|---|
| B01 | C2 弱子類 | ONT SNV 建樹；SV／甲基化只事後放上固定樹 | 嚴格看「long-read 特徵」時改屬 C1 |
| B02 | C1 | linked read 是短讀加分子 barcode | 把 long-range 分子資訊當 long-read 特徵時改屬 C2 |
| B03 | C3a | ONT 只做 SV 正交驗證，不進入建樹 | — |
| B05 | C3a partial | 從病人 scDNA 建樹，只與原研究 clone 結構比對 | 也可標 `reference_tree` |
| B07 | C1 | scRNA 加族群 phasing；scDNA 只佐證 CN | 接受 CN 佐證時改屬 C3a partial |
| M02 | C1 | 同 read 共現模型，但只用短 PE reads | — |
| M04 | C1 | 病人 scDNA 推樹，但準確度只來自模擬 | 把推論的 scDNA 樹當參考時改屬 C3a |
| M06 | C3a benchmark | DLP 樹來自細胞株，不是病人 | — |
| H01 | C3a partial（最弱） | scCNV 只支持 CNA 異質性，沒有逐邊 SNV 真值 | 不接受部分驗證時改屬 C1 |

## 快速檢索

每篇 README 頂端有 YAML front-matter。每個欄位在同一行，可以直接 grep。

```bash
cd research
# 依類別列出 README
grep -rl '^category: "C2"' --include=README.md .
# 依 long-read 角色、cross tag 或關鍵詞找
grep -rl '^long_read_role: "topology_constraint"' --include=README.md .
grep -rl '^cross_tags:.*read_cooccurrence_model' --include=README.md .
grep -rli '^keywords_en:.*haplotype' --include=README.md .
# 用總表篩選（欄位見表頭）
awk -F'\t' '$2=="C3a" {print $1, $3, $4}' paper_categories.tsv
# 依分類瀏覽目錄（symlink，不搬原檔）
ls -R papers_by_category
```

**front-matter 欄位**：`paper_id`、`category`、`category_label`、`subtype`、`sc_truth_strength`、`title`、`year`、`doc_type`、`material`、`platform_class`、`platform_detail`、`long_read_role`、`long_read_features`、`single_cell_truth`、`single_cell_tech`、`input_is_single_cell`、`tree_type`、`cross_tags`、`keywords_en`、`keywords_zh`、`summary_zh`、`category_index`。

**常用 cross tag**：

| tag | 論文 |
|---|---|
| `read_cooccurrence_model` | M02、B02、M03、B04 |
| `haplotype_specific_cn` | A01、A04、B03、B05、B07、M04 |
| `long_read_validation_only` | B03、H01 |
| `phyclone_truth_source` | R01、M01 |
| `single_cell_input` | B07、M04、M06、B05 |
| `structural_variant` | A01、A04、B01、B06、B08、M05 |
| `castle_ont_same_data`、`direct_competitor` | M03 |

## 維護

1. 只改 `paper_categories.tsv`。列表欄位以 `; ` 分隔。
2. 執行 `python3 research/tools/sync_paper_categories.py`。它會重寫 front-matter、`papers_by_category/` 與下方表格。
3. 執行 `python3 research/tools/sync_paper_categories.py --check`，確認沒有 drift。

新增論文時，在 TSV 加一列，填 `dir` 與 `readme`，再執行同步。

## 分類總表（自動產生，不要手改）

<!-- BEGIN GENERATED: paper table -->

### C1｜短讀或未說平台（無 single-cell 真值）（6 篇）

| ID | 子類 | 年 | 論文 | 平台（建樹資料） | long-read 角色 | sc 真值 | 一句話 |
|---|---|---|---|---|---|---|---|
| [M05](tumor_phylogeny_2026/methods_survey/papers/M05_tusv_ext_2022/README.md) | `c1_bulk_short_read` | 2022 | TUSV-ext: Reconstructing tumor clonal lineage trees incorporating SNVs, CNAs and SVs | multi-region bulk short-read WGS; simulated (no platform) | `none` | `simulated_only`（none） | ILP 聯合 SNV/SV/CNA 建樹；phasing 是潛變數。 |
| [M07](tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/README.md) | `c1_bulk_short_read` | 2024 | SMC-Het DREAM: Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction | simulated Illumina WGS (BAMSurgeon on GM24385) | `none` | `simulated_only`（none） | 短讀模擬的單樣本 benchmark，比較 31 個方法。 |
| [B02](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/README.md) | `c1_read_cooccurrence_short` | 2021 | Co-evolution of tumor and immune cells during progression of multiple myeloma | 10x linked-read WGS (Illumina); bulk WGS/WES; 10x scRNA-seq | `none` | `scrna_only`（none） | linked-read 分子判定 NRAS 雙突變屬獨立分支。 |
| [M02](tumor_phylogeny_2026/methods_survey/papers/M02_treeclone_2019/README.md) | `c1_read_cooccurrence_short` | 2019 | TreeClone: Reconstruction of tumor subclone phylogeny based on mutation pairs using next generation sequencing data | Illumina HiSeq PE100 WES; simulated | `none` | `simulated_only`（none） | 用同 read 上的 SNV pair 推 clone tree；只用 short read。 |
| [B07](tumor_phylogeny_2026/papers/B07_numbat_2022/README.md) | `c1_single_cell_input_no_truth` | 2022 | Haplotype-aware analysis of somatic copy number variations from single-cell transcriptomes (Numbat) | 10x scRNA-seq (short read); Eagle2 population phasing reference | `none` | `scrna_only`（none） | scRNA 加族群 phasing 推 CNV 細胞樹；不是 long read。 |
| [M04](tumor_phylogeny_2026/methods_survey/papers/M04_pharming_2026/README.md) | `c1_single_cell_input_no_truth` | 2026 | Pharming: Joint Clonal Tree Reconstruction of SNV and Copy Number Aberration Evolution from Single-Cell DNA Sequencing of Tumors | low-pass scDNA (ACT, DLP+); simulated | `none` | `simulated_only`（none） | 單細胞 SNV+CNA 聯合 clone tree；只有模擬真值。 |

### C2｜long-read 特徵輔助建樹（無 single-cell 真值）（4 篇）

| ID | 子類 | 年 | 論文 | 平台（建樹資料） | long-read 角色 | sc 真值 | 一句話 |
|---|---|---|---|---|---|---|---|
| [M03](tumor_phylogeny_2026/methods_survey/papers/M03_donmez_aacr2026/README.md) | `c2_local_order` | 2026 | Phasing tumor clones by timing point mutations using bulk long-read sequencing (AACR 2026 Abstract 6912) | ONT R10 regular + ultra-long (CASTLE H2009, H1437) | `local_order` | `none`（none） | ONT 同 read 共現判定突變先後與分歧；沒有真值。 |
| [B01](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md) | `c2_long_read_data_only` | 2026 | Long-read sequencing of single cell-derived melanoma sublines reveals divergent and parallel genomic and epigenomic evolutionary trajectories | ONT R10.4 PromethION bulk WGS per subline | `tree_input` | `single_cell_derived_lines`（none） | ONT SNV 建樹；SV／甲基化只事後放上固定樹。 |
| [B08](tumor_phylogeny_2026/papers/B08_hpv_integration_2023/README.md) | `c2_molecular_history` | 2023 | Intratumoral Heterogeneity and Clonal Evolution Induced by HPV Integration | ONT WGS (>=20 kb reads); PacBio HiFi; Illumina WGS | `molecular_history` | `none`（none） | long read 排出 HPV 局部 SV 分子史；不是完整 clone tree。 |
| [B06](tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/README.md) | `c2_sample_tree_sv` | 2025 | Multisite long-read sequencing reveals the early contributions of somatic structural variations to HBV-related hepatocellular carcinoma tumorigenesis | ONT WGS ~37x; Illumina WGS | `sample_tree` | `none`（none） | ONT SV 建多區域 sample tree；沒有 single-cell 真值。 |

### C3a｜single-cell 真值樹 × 短讀或未說平台（11 篇）

| ID | 子類 | 年 | 論文 | 平台（建樹資料） | long-read 角色 | sc 真值 | 一句話 |
|---|---|---|---|---|---|---|---|
| [A01](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md) | `c3a_patient_sc_reference` | 2025 | Tracking clonal evolution during treatment in ovarian cancer using cell-free DNA | DLP+ scWGS (Illumina) | `none` | `patient_scdna_reference_tree`（reference_tree） | 病人 scWGS 建 MEDICC2 樹；cfDNA 追蹤抗藥 clone。 |
| [A02](tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md) | `c3a_patient_sc_reference` | 2025 | Characterizing the evolutionary dynamics of cancer proliferation in single-cell clones with SPRINTER | DLP+ scWGS (Illumina) | `none` | `patient_scdna_reference_tree`（reference_tree） | SPRINTER 校正 S 期 CN；病人 scDNA 樹連結增殖與轉移。 |
| [A03](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md) | `c3a_patient_sc_reference` | 2023 | Application of high-throughput single-nucleus DNA sequencing in pancreatic cancer | Tapestri snDNA amplicon panel (Illumina) | `none` | `patient_scdna_reference_tree`（reference_tree） | Tapestri snDNA 建 PA04 的 SNV+SMAD4 刪除 clone 樹。 |
| [A04](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md) | `c3a_patient_sc_reference` | 2024 | Single-cell multiomics analysis reveals dynamic clonal evolution and targetable phenotypes in acute myeloid leukemia with complex karyotype | Strand-seq scTRIP (Illumina NextSeq); OGM validation | `none` | `patient_scdna_reference_tree`（reference_tree） | Strand-seq 單細胞 SV+單倍型建 CK-AML 人工 clone 樹。 |
| [A05](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md) | `c3a_patient_sc_reference` | 2024 | Multiomic single cell sequencing identifies stemlike nature of mixed phenotype acute leukemia | DAb-seq (Tapestri) amplicon; Illumina NovaSeq | `none` | `patient_scdna_reference_tree`（reference_tree） | DAb-seq 單細胞 DNA 以 SCITE 建 MPAL 突變樹。 |
| [B03](tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md) | `c3a_patient_sc_reference` | 2022 | Single-cell genomic variation induced by mutational processes in cancer | DLP+ scDNA-seq (Illumina); ONT PromethION for SV validation only | `validation_only` | `patient_scdna_reference_tree`（reference_tree） | scDNA total-CN 建細胞樹；ONT 只驗證 SV。 |
| [R01](tumor_phylogeny_2026/references/R01_mcpherson_hgsoc_2016/README.md) | `c3a_patient_sc_reference` | 2016 | McPherson 2016: Divergent modes of clonal spread and intraperitoneal mixing in high-grade serous ovarian cancer | Illumina HiSeq WGS; targeted amplicon MiSeq; single-nucleus targeted PCR | `none` | `patient_scdna_reference_tree`（reference_tree） | 病人單核 PCR 建樹；是 PhyClone HGSOC 真值樹來源。 |
| [M01](tumor_phylogeny_2026/methods_survey/papers/M01_phyclone_2025/README.md) | `c3a_sc_benchmark_truth` | 2025 | PhyClone: accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing | bulk WGS; targeted deep sequencing; simulated (platform not named) | `none` | `sc_derived_benchmark_truth`（benchmark_truth） | bulk SNV+CN 的貝氏 clone tree；HGSOC 真值樹來自單細胞。 |
| [M06](tumor_phylogeny_2026/methods_survey/papers/M06_phylex_2023/README.md) | `c3a_sc_benchmark_truth` | 2023 | PhylEx: Reconstructing clonal tree for phylo-phenotypic characterization of cancer using single-cell transcriptomics | bulk WGS/WES; Smart-seq3 and 10x scRNA; DLP pseudobulk | `none` | `sc_derived_benchmark_truth`（benchmark_truth） | bulk+scRNA 共現建樹；以 DLP scDNA 樹為真值。 |
| [B05](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md) | `c3a_sc_partial` | 2022 | MEDICC2: whole-genome doubling aware copy-number phylogenies for cancer evolution | bulk Illumina WGS (PCAWG); short-read scDNA (Minussi TNBC); simulated | `none` | `sc_partial_validation`（partial） | haplotype CN+WGD 改變 topology；單細胞樹仍是推論。 |
| [H01](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md) | `c3a_sc_partial` | 2021 | Fang 2021: HCC1395 community reference samples and call sets (high-confidence candidate branching tree) | Illumina bulk WGS/WES; PacBio ~40x for call-set validation only | `validation_only` | `sc_partial_validation`（partial） | bulk PhyloWGS 建樹；單細胞 CNV 只部分佐證。 |

### C3b｜single-cell 真值樹 × long-read 特徵（1 篇）

| ID | 子類 | 年 | 論文 | 平台（建樹資料） | long-read 角色 | sc 真值 | 一句話 |
|---|---|---|---|---|---|---|---|
| [B04](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md) | `c3b_topology_constraint_sc_partial` | 2022 | Phasing analysis of lung cancer genomes using a long read sequencer | ONT PromethION bulk WGS (pair order); Illumina WGS (VAF, FACETS -> PyClone-VI -> ClonEvol) | `topology_constraint` | `sc_partial_validation`（partial） | long read 同 read 排序選出 S14 線性樹；scDNA 局部驗證。 |

<!-- END GENERATED: paper table -->
