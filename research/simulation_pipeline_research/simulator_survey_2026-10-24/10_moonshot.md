# 「Moonshot」線索調查

調查日期：2026-10-24。問題：「Moonshot」模擬器是什麼？它能不能同時產生真值 clone tree 與模擬 SNV 資料？

證據標記：〔論文〕論文或 README 的描述；〔程式〕讀過原始碼（只讀，沒有執行）；〔推論〕分析推論，沒有實測。程式 clone 在 `/tmp/claude-1024/-bip8-disk-boyu114-main-work/18fc1cc2-ffb5-4afb-8a48-a15890b40de5/scratchpad/clones2/`（暫存，會消失）。

## 結論

1. **「Moonshot」不是一個腫瘤模擬器。** GitHub 與網路搜尋都沒有找到叫 Moonshot 的腫瘤演化或 SNV 模擬工具。名稱含 moonshot 的 repo 是 NCI Cancer Moonshot Biobank 的資料工具、專利視覺化、太空模擬遊戲等，都和建樹無關。〔推論〕
2. **NCI「Somatic Mutation Working Group」是 FDA 主導的 SEQC2 工作組。** 它的產出是 HCC1395／HCC1395BL 的**真實資料真值集**，不是生成器。它**沒有** clone tree 真值檔。〔論文〕〔程式〕
3. **SEQC2 有兩種「合成」資料，但都不符合需求。**
   - `SPP`：HCC1395 與 HCC1395BL 的**實體 DNA 混合**（100%、75%、50%、20%、10%、5%、0% tumor），Illumina 定序。這是真實 purity 梯度，不是模擬。
   - `DeepLearning_bams`：用 BAMSurgeon 在 normal BAM 裡 spike-in 的 `synthetic_tumor_*.bam` 加 `synthetic_truth_*.vcf.gz`。只有 SNV／indel 真值，沒有樹，沒有 CN。
4. **搜尋時意外找到一個重要的新候選：SCOUT。** 它是 Caravagna lab 用 ProCESS 產生的合成 WGS cohort（bioRxiv 2026-06）。7 個 tumour model，216 個 tumour FASTQ 加 7 個 normal FASTQ，purity 0.3／0.6／0.9，有 multi-region、有 allele-specific CN 真值。它是**已生成的資料集**；生成程式在 `process_reproducibility`。它和 Moonshot 無關。〔論文〕〔程式〕
5. **ClonalSim（Bioconductor）是 VAF 層的小型生成器。** 它沒有 CN，也沒有明確的樹檔，價值低。〔程式〕
6. **SEQC2 有 HCC1395 的 ONT 與 PacBio 資料，但只用來做 SV call set。** 沒有 clone 或 haplotype 真值。〔論文〕

| 候選 | 類型 | clone tree 真值 | 資料層級 | CN | purity<1 | long read | 符合需求？ |
|---|---|---|---|---|---|---|---|
| 名為 Moonshot 的模擬器 | 不存在 | — | — | — | — | — | 否（沒有這個工具） |
| SEQC2 SNV／indel 真值集（v1.2.1） | 真實資料真值集 | 否 | VCF＋BED（真實 Illumina BAM） | 另有 CNV 真值集（Genome Biol 2024） | 否 | PacBio 只做驗證 | 否，只能當 HCC1395 的 SNV 真值 |
| SEQC2 `SPP` 實體 titration | 真實 DNA 混合 | 否 | Illumina BAM／FASTQ | 真實 | **是**（7 個比例） | 否 | 否；但可當「真實 purity 梯度」對照 |
| SEQC2 `DeepLearning_bams`（BAMSurgeon spike-in） | 合成 BAM（已生成） | 否 | BAM＋truth VCF | 無 | 部分（依 VAF 設定，未核對） | 否 | 否 |
| SEQC2 long read（Talsania 2022） | 真實資料 | 否 | ONT／PacBio 真實 read | — | 否 | **是** | 否；只有 SV 真值 |
| **SCOUT**（ProCESS cohort） | 合成資料集＋生成腳本 | 有 cell-level phylogeny（`.sff` forest）；是否公開待核對 | Illumina PE FASTQ；sarek BAM／VCF 結果 | allele-specific CN | **是**（0.3／0.6／0.9） | 否（NovaSeq 模型） | **部分**：bulk short read 有；HP／long read 沒有 |
| ClonalSim | 生成器（R） | 否（只有 clone 群組） | VAF／read count | 無 | 是（clone 比例和 <1） | 否 | 否 |

## 1. 名為「Moonshot」的工具

- GitHub repo 搜尋 `moonshot tumor`、`moonshot genomics`、`moonshot somatic`、`moonshot phylogeny` 都是 0 筆。〔程式〕
- `moonshot cancer` 有 10 筆。最接近的是 `CBIIT/cmbiobank-tools`（Cancer Moonshot Biobank 資料工具），不是模擬器。〔程式〕 https://github.com/CBIIT/cmbiobank-tools
- `moonshot sim` 的 11 筆都是遊戲、金融或 LLM 專案。〔程式〕
- 網路搜尋「Moonshot」＋tumor phylogeny／subclonal reconstruction 沒有找到任何 benchmark。〔推論〕
- 推測：這個線索可能是把「Cancer Moonshot」「SEQC2 Somatic Mutation Working Group」「DREAM SMC-Het」混在一起記。DREAM SMC-Het 已在 [02](02_read_level_simulators.md) 處理（Salcedo 2020，doi:10.1038/s41587-019-0364-z，PubMed 已核對）。〔推論〕

## 2. SEQC2 Somatic Mutation Working Group（HCC1395／HCC1395BL）

本專案已在 `research/hcc1395_golden_tree_research/` 整理 Fang 2021 的 PhyloWGS 候選樹。這裡只補「它是不是生成器」與資料清單。

- **它是真實資料真值集，不是生成器。** 產出是高可信度 somatic SNV／indel 集與 callable region。〔論文〕
  - Fang 2021，Nat Biotechnol 39:1151，doi:10.1038/s41587-021-00993-6（PubMed 已核對）。
  - Xiao 2021，Nat Biotechnol 39:1141，doi:10.1038/s41587-021-00994-5（PubMed 已核對）。它研究 purity、input 量、library、caller 對 calling 的影響。
- **真值檔位置**：`https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/seqc/Somatic_Mutation_WG/release/latest/`，有 `sSNV.MSDUKT.superSet.v1.2.vcf.gz`、`sINDEL.MDKT.superSet.v1.2.vcf.gz`、`High-Confidence_Regions_v1.2.bed`。release 目錄有 v1.0、v1.1、v1.2、v1.2.1。〔程式〕
- **沒有 clone tree 真值檔。** FTP 上找不到樹檔。論文的樹是 PhyloWGS 推論結果，不是真值。〔程式〕〔論文〕
- **CN 真值**：另一篇建立 HCC1395 的高可信度 CNV call set。Genome Biol 2024 25:163，doi:10.1186/s13059-024-03294-8（PubMed 已核對）。〔論文〕
- **SEQC2 有 HCC1395BL 的 de novo assembly**：`assembly/HCC1395BL_v1.0/`（PacBio＋Illumina＋10x＋HiC）。它可作為 normal 的 haplotype-aware reference，但 README 沒有說它是 phased 的。〔程式〕
- 授權：美國政府公開資料，沒有 software license。〔推論〕

### 2a. `SPP` 實體 tumor／normal titration

- 位置：`Somatic_Mutation_WG/data/SPP/`。檔名 `SPP_GT_<tumor>-<normal>_<rep>`，比例有 1-0、3-1、1-1、1-4、1-9、1-19、0-1。〔程式〕
- 推得 tumor fraction 是 100%、75%、50%、20%、10%、5%、0%，每個比例 3 個 replicate。另有 10X 到 300X 的降採樣子目錄。〔推論〕
- SRA 清單把它們標成 `DNA mix`，儀器是 Illumina HiSeq 4000（SRP162370）。〔程式〕
- **這是實體 DNA 混合，不是模擬。** 它沒有 clone 真值，但它是「已知 nominal purity 的真實資料」。和我們 `tX_nY` 的 subsample 設計概念相同，可當對照。〔推論〕
- SRA run 清單裡沒有 ONT 或 PacBio run。〔程式〕

### 2b. `DeepLearning_bams`（BAMSurgeon 合成 tumor）

- 位置：`Somatic_Mutation_WG/data/DeepLearning_bams/`，有 `synthetic_tumor_{FD2N,FD3N,IL1N,IL2N,NS1N,NS2N}.dedup.bam` 與 `truth_vcf/synthetic_truth_*.vcf.gz`。〔程式〕
- 來源論文：Sahraeian 2022，Genome Biol 23:12，doi:10.1186/s13059-021-02592-9（PubMed 已核對）。它用 spike-in 突變與真實突變一起訓練 NeuSomatic。〔論文〕
- Fang 2021 也用 BAMSurgeon 在 normal replicate 中 spike-in 約 10 萬個 SNV 訓練 SomaticSeq（見 `hcc1395_tumor_evolution_tree_review/01_data_and_callset.md`）。〔論文〕
- **只有 SNV／indel 位置與 VAF 真值，沒有樹，沒有 CN，沒有 clone 結構。** 生成器本身是 BAMSurgeon，已在 [02](02_read_level_simulators.md) 處理。〔推論〕

### 2c. SEQC2 long read

- Talsania 2022，Genome Biol 23:255，doi:10.1186/s13059-022-02816-6（PubMed 已核對）。HCC1395 有 Illumina、10x linked read、PacBio、ONT、Hi-C 資料，產出 1,788 個 somatic SV 的 consensus 集。〔論文〕
- 另一篇用 HCC1395 的 ONT／PacBio 資料與**模擬資料**評估 long read somatic SV calling（Genom Proteom Bioinform 2025，doi:10.1093/gpbjnl/qzaf139，PubMed 已核對）。模擬的是 SV，不是 SNV clone 結構；生成器沒有核對。〔論文〕
- **沒有 clone 或 haplotype 真值。** 這些 read 是真實資料。〔推論〕
- 對本專案的意義：HCC1395 是我們的細胞株。SEQC2 SNV 真值集可以檢查我們 ONT 資料上的 SNV calling。但它不能提供樹的真值。〔推論〕

## 3. SCOUT（ProCESS 合成 WGS cohort）— 新候選

- **論文**：Valeriani … Casagrande, Caravagna，"SCOUT"，bioRxiv 2026-06-11，doi:10.64898/2026.06.09.731105（bioRxiv 頁面讀過；未經同行審查）。reproducibility repo 的 README 寫的論文標題是 "Ground-truth benchmarking of tumour evolution inference from whole-genome sequencing"。〔論文〕
- **生成器是 ProCESS（v1.1.0）**。這也補上 [04](04_evolutionary_simulators.md) 裡 ProCESS「沒找到論文」的缺口。〔論文〕
- **資料規模**：7 個 tumour model（SPN01–SPN07），30 個 clone，24 個 biopsy，216 個 tumour FASTQ 加 7 個 normal FASTQ，GRCh38。〔論文〕
- **purity 與 depth**：論文寫 purity 0.3／0.6／0.9、coverage 50×／100×／150×。`build_cohort/README.md` 寫 coverage 有 50／100／150／200X，normal 30X。兩者不一致，以實際下載為準。〔論文〕〔程式〕
- **seed**：200X 拆成 40 個 5X lot，第 i 個 lot 的 sequencing seed 是 i。〔程式〕`process_reproducibility/build_cohort/README.md`
- **真值**：`SCOUT/R/getters_ground_truth.R` 提供 `get_mutations()`（每個 purity×coverage 的 mutation RDS），`read_sheets.R` 提供 `get_ground_truth_cna()`、`get_ground_truth_drivers()`、`get_ground_truth_exposures()`、`get_sampling_information()`。〔程式〕
- **clone tree 真值**：生成時用的是 ProCESS 的 phylogenetic forest `.sff` 檔（cell-level）。SCOUT R 套件裡**沒有** tree getter。forest 檔有沒有公開，沒有核對。〔程式〕〔推論，未驗證〕
- **read 平台**：Illumina NovaSeq 6000 PE 模型。沒有 long read。〔論文〕
- **haplotype**：ProCESS 的 read 帶 phased germline SNP（見 04），所以 FASTQ 裡 somatic SNV 與 germline SNP 的共現是真的。但 SCOUT 沒有釋出 per-read HP 真值。〔推論〕
- **資料位置**：ENA（論文寫 `PRJEB97253`，fetch 結果帶一個尾字元 `T`，未核對），Zenodo（DOI 在補充表 T10，未核對），網站 https://caravagnalab.github.io/SCOUT-website/。〔論文〕
- **repo**：
  - https://github.com/caravagnalab/SCOUT（資料存取 R 套件），`6fddbff`，2026-07-31，LICENSE 檔是 R 的 `YEAR/COPYRIGHT HOLDER` 格式（GitHub 判為 NOASSERTION）。
  - https://github.com/caravagnalab/process_reproducibility（生成與分析腳本，需要 SLURM），`c0928a0`，2026-06-08，沒有 license。
- **對本專案**：SCOUT 是現成的「真值＋bulk short read FASTQ＋多 purity＋多 region」資料。它可以直接當 PhyClone 的 short read baseline，不用自己跑生成器。它不能測 long read HP 特徵。〔推論〕

## 4. ClonalSim（Bioconductor）

- repo：https://github.com/gbucci/ClonalSim，`d27becd`，2026-04-23，MIT。Bioconductor 套件版本 0.99.8 到 1.1.0。〔程式〕
- 生成器：`R/simulateTumor.R` 的 `simulateTumor()`。輸入是 clone 頻率、每個 clone 的 private 突變數、founder 突變數、shared 群組（例如 `"2 3 4"=15`）。〔程式〕
- **沒有明確的樹。** shared 群組由使用者給。群組可以互相交錯（預設 `"1 2"` 與 `"2 3 4"`），所以不保證是一棵樹。〔程式〕〔推論〕
- **沒有 CN。** VAF 由 clone 頻率決定，加 Beta 雜訊、negative binomial depth、binomial read。〔程式〕`R/noise_model.R`
- 單一樣本；purity 是 clone 頻率總和。seed 要使用者自己 `set.seed()`。有 `toPyClone()`、`toSciClone()`、`toVCF()`。〔程式〕
- 沒有找到論文。〔推論〕

## 5. 順帶找到的 meta 資源

- Lai, Liu, Scharpf, Karchin，"Evaluation of simulation methods for tumor subclonal reconstruction"，arXiv 2402.09599（2024）。網路摘要說它評估 51 個模擬方法，其中 9 個是通用工具。可用來補本調查的漏網工具。全文沒有讀。〔論文，未驗證〕

## 搜尋範圍（2026-10-24）

- GitHub repo search（`gh api search/repositories`）：`moonshot tumor`、`moonshot cancer`、`moonshot genomics`、`moonshot somatic`、`moonshot phylogeny`、`moonshot sim`、`seqc2 somatic`。
- `gh api repos/...`：caravagnalab/SCOUT、caravagnalab/process_reproducibility、caravagnalab/SCOUT-website、gbucci/ClonalSim。
- WebSearch：moonshot＋tumor simulation；SEQC2 titration／BAMSurgeon；HCC1395 ONT／PacBio；Cancer Moonshot synthetic tumor benchmark；Moonshot＋subclonal reconstruction。
- WebFetch：SCOUT bioRxiv 全文（前 100k 字元）、Area Science Park 摘要頁、arXiv 2402.09599、SEQC2 FTP 目錄（`data/`、`data/SPP/`、`data/DeepLearning_bams/`、`release/latest/`、`assembly/`、`data/reads/SRA_run_accession_list`）。
- PubMed：Fang 2021、Xiao 2021、Talsania 2022、Salcedo 2020、Sahraeian 2022、HCC1395 相關 5 篇。
- 沒有查：HTAN、CPTAC、ICGC-ARGO 的模擬資源（搜尋沒有出現相關結果，未深入）。SCOUT 的 Zenodo 檔案清單與 `.sff` 是否公開。
