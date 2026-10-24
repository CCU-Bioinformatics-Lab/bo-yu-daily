# Single-cell 與 bulk＋single-cell 聯合模擬器調查

調查日期：2026-10-24。範圍：能同時產生「真值 clone／cell tree」與「模擬 SNV 定序資料」的 single-cell DNA 模擬器，以及 bulk＋single-cell 聯合模擬器。

標記：〔論文〕論文或文件描述；〔程式〕讀過原始碼或 README；〔推論〕我們的判斷；〔未驗證〕沒有讀到原文或程式。所有程式只讀、沒有執行。

## 結論

一句話：**SISTEM 最接近我們的需求。** 它輸出真值樹、每個 SNV 所在的 haplotype（`Allele` 欄）、haplotype-specific CN，以及 bulk SNV 的 read 數。SimSCSnTree 與 PSiTE 也記錄 SNV 所在的 haplotype，但只產生 FASTQ。沒有任何工具產生 long read，也沒有工具輸出 read 層級的 SNV 共現。

| 排名 | 工具 | 真值樹 | 資料層級 | CN | SNV 所在 haplotype | bulk／pseudo-bulk | 主要缺點 |
|---|---|---|---|---|---|---|---|
| 1 | SISTEM | 有（cell 或 clone，Newick） | per-cell 等位 read 數（bin）；per-site bulk SNV read 數；FASTQ | haplotype-specific，focal／arm／整條 | **有**：`SNV_events.tsv` 的 `Allele` | 有，含 diploid 細胞（purity<1）、多 site | 沒有 seed 參數；short read |
| 2 | SimSCSnTree | 有（`.npy`，可轉 Newick） | FASTQ（每個 allele 一個檔）；bulk FASTQ | allele-specific CNA、WGD | **有**：`read_tree.py -n` 輸出 allele 0／1 | 有 bulk FASTQ，但沒有 normal 混合 | 沒有授權檔；沒有 seed；要自己 align＋call |
| 3 | PSiTE | 有（輸入 Newick） | 每個 cell／sector 的 FASTA→ART read | 有 CNV | **有**：`hap` 欄 | 有，sector purity | 2021 後沒更新；要自己 call |
| 4 | CellCoal | 有（`-6` 輸出樹） | VCF read 數＋genotype likelihood | **沒有 CNA**；只有 cnLOH、點 deletion | **有**：`-9` 輸出真 maternal／paternal haplotype | 沒有 | 沒有 CN；沒有 bulk |
| 5 | COMPASS 生成器 | 有（`_treeTRUE.gv`） | Tapestri 型 AD／DP 矩陣＋region read 數 | allele 相對於 SNV（REF/ALT）的 CNA、cnLOH | 部分：CNA 打在 REF 或 ALT | 沒有 | 只有 panel 尺度 |
| 6 | scsim（haotianzh） | 輸入 Newick | per-cell genotype＋read 數 | 隨機 allele 複製或刪除 | 沒有 | 沒有 | 沒有授權檔 |
| 7 | CNAsim | 有 | CN profile、FASTQ | haplotype CN | 沒有 SNV 真值 | 沒有 | 只有 CNA |
| 8 | HCDSIM | 有（Newick） | CN、FASTQ、BAM | haplotype-specific CN | 只有 germline SNP phase | 沒有 | 沒有 somatic SNV |
| 9 | flahertylab SCSIM | **沒有**樹 | bulk＋single-cell FASTQ | 沒有 | 沒有 | 有 | 階層抽樣，不是 phylogeny |
| 10 | SCsnvcna、SPhyR、trisicell、SBMClone 的 sim | 有 | 二元矩陣（含 FP／FN／missing） | 無或只有 CNA overlap | 沒有 | 沒有 | 沒有 read 數 |
| — | SCSsim、SCSilicon | 沒有 | FASTQ | 有 CNV | 沒有 | 沒有 | 只模擬 read，不模擬演化樹 |

對我們的意義〔推論〕：

- 要測「haplotype 約束 multiplicity」，可用 SISTEM 的 `SNV_events.tsv`（allele）＋`observed_CNPs.tsv`（haplotype CN）當真值。bulk read 數可直接轉成 PhyClone 輸入。
- 要測「同一 read 上 SNV 共現」，現有工具都不夠。SimSCSnTree、PSiTE、SISTEM、HCDSIM 都會寫出每個 haplotype 的 FASTA。可以把這些 FASTA 接到 long-read 模擬器（例如 PBSIM／Badread），自己產生帶 HP 標記的 read。這一步要自己寫。
- CellCoal 有 per-allele ADO 與真 haplotype，但沒有 CN，不適合測 CN 相關的 multiplicity。

## 各工具證據

### SISTEM（samsonweiner/sistem）

- README：「simulate ground truth cell or clonal lineages … generating CNA profiles, SNV profiles, bulk-seq read counts, single-cell read counts, and allele-specific scDNA-seq reads」。〔程式〕
- `sistem/data/profiles.py::log_mutations` 寫 `SNV_events.tsv`，欄位 `Cell/Clone, Driver, Chrom, Allele, Region Index, Ref Region Index, Position, BP`。`Allele` 就是 SNV 所在的 haplotype（0／1）。〔程式〕
- `docs/source/output_formats.rst`：`observed_CNPs.tsv` 有 `Hap CN`（x_a, x_b）與 `Total CN`；`ancestral_CNPs.tsv` 有祖先節點。〔程式〕
- `SNV_profiles.tsv` 輸出每個 cell 的 `A/B` genotype，按 haplotype 分開。〔程式〕
- `sistem/data/reads.py::gen_readcounts_bulk`：對每個 site 的每個 SNV 抽 total／variant read 數。期望 VAF 用各 clone 的 x_alt/(x_ref+x_alt) 加權，所以含 CN 效應。若樹中有 `diploid` 節點，會加入 normal 細胞，等於 purity<1。多個轉移 site 是多個 sample。〔程式〕
- `gen_readcounts_singlecell`：per-cell、per-bin 的 `Acount`、`Bcount`（haplotype 層級 read 數），覆蓋不均用 Lorenz 曲線。〔程式〕
- 沒有找到 `seed` 參數（`grep seed` 只找到 metastasis seeding）。使用者可能可在外部設 `np.random.seed`，〔未驗證〕。
- 沒有 ADO 或 doublet 模型（在 `reads.py` 沒看到）。〔程式〕
- GPL-3.0；最後 commit `627f888`（2026-05-30）。https://github.com/samsonweiner/sistem

### SimSCSnTree（compbiofan/SimSCSnTree）

- 兩步：step 1 產生樹，樹的邊上加 CNA 與 SNV；step 2 用 wgsim 從每個節點的基因組抽 read。〔程式：README〕
- `read_tree.py -n -f *.tree.npy` 輸出真值 SNV：「chromosome, position, reference nucleotide, variant nucleotide, the allele the variant is on (0 or 1), and the ID of the cell」。〔程式：README〕
- CNA 一次只打一個 allele（`gen_tree_overlappingCNA.py` 註解「the copy number change happens on only one allele」）；有整條染色體 WGD 選項。〔程式〕
- `main.par.overlapping.py` 對每個 allele 分別產生 FASTQ，檔名 `level*_node*_allele1.fq`／`allele2.fq`。bulk 模式（`-U`、`-V`）把同一層所有節點、兩個 allele 的 FASTQ `cat` 成 `level*_bulk.fq`。〔程式〕
- 推論：合併前的 per-allele FASTQ 可以當 haplotype 標記的來源。合併後的 bulk FASTQ 失去標記。〔推論〕
- bulk 只取腫瘤節點，沒看到 normal 混合參數。〔程式〕
- 沒有 seed 參數（`grep seed` 無結果）。沒有授權檔。最後 commit `08747dc`（2023-04-10）。可 `conda install simscsntree`。https://github.com/compbiofan/SimSCSnTree

### PSiTE（hchyang/PSiTE）

- 模組：`vcf2fa`（germline）→ `phylovar`（沿輸入 Newick 樹加 somatic 變異）→ `chain2fa`（產生每個 cell／clone 的基因組）→ `fa2wgs`／`fa2wes`（用 ART 抽 read）。〔程式：README〕
- 變異檔有 `hap` 欄：「The haplotype copy of the chromosome on which the somatic variant resides on」。〔程式：README〕
- sector 設定有 `purity`；輸出 `frequency`、alt／total read 數「taking into account tumor purity」。〔程式：README〕
- GPL-3.0；最後 commit `b752cd1`（2021-04-25）。single-cell 讀 read 的路徑沒有細讀。〔未驗證〕https://github.com/hchyang/PSiTE

### CellCoal（dapogon/cellcoal）

- coalescent 樹；SNV、點 deletion、cnLOH；手冊明寫「CellCoal does not simulate copy number alterations or structural variants」。〔程式：手冊 v1.1〕
- 技術誤差：ADO、allelic imbalance、amplification error、sequencing error、doublet（`-B`）。〔程式：手冊〕
- read 數：每個 site 的 read 以 Poisson／NB 抽，再依 allelic imbalance 隨機分到 maternal 或 paternal。輸出 VCF（read 數＋genotype likelihood），另有選項可輸出 CATG 格式。〔程式：手冊〕
- haplotype：`-9` 輸出「true maternal and paternal haplotypes at all sites」；`-2`／`-4` 輸出觀察／ML haplotype；`-6` 輸出樹。所以 SNV 所在 haplotype 可以從 `true_hap` 讀出。〔程式：手冊〕
- read 層級的 haplotype 歸屬只在內部使用，不輸出到 VCF。〔推論，未逐行驗證〕
- `-#` 設 seed。〔程式〕
- 沒有 bulk 或 pseudo-bulk 輸出；但每個 cell 的 VCF read 數可以自己加總。〔推論〕
- GPL（`src/cellcoal.c` 檔頭）；最後 commit `f628037`（2025-02-10）。https://github.com/dapogon/cellcoal

### COMPASS 合成資料生成器（cbg-ethz/COMPASS）

- `Experiments/simulations/generate_synthetic_data.py`：Prüfer 隨機樹；SNV 指派到 region；CNA 指派到節點。〔程式〕
- CNA 記成 `(region, type, alleles)`，`alleles` 對每個 SNV 指定 gain／loss 打在 REF 或 ALT。這是相對於 SNV 的 phase，不是全域 haplotype。〔程式〕
- 輸出 `_variants.csv`、`_regions.csv`、`_DP.csv`、`_AD.csv`、`_genotypes.csv`、`_treeTRUE.gv`、`_cellAssignmentsTRUE.tsv`。〔程式〕
- 參數：`--dropoutrate`、`--doubletrate`、`--allow_cnloh`、`--seed`（`np.random.seed(seed)`）。〔程式〕
- 設計對象是 Tapestri（Mission Bio）panel。GPL-3.0；最後 commit `8238988`（2025-08-24）。https://github.com/cbg-ethz/COMPASS

### scsim（haotianzh/scsim，ScisTree 作者）

- C++；輸入帶 branch length 的 Newick；SNV 依 infinite sites；CNM「Randomly select an allele and either duplicate or delete it」。〔程式：README〕
- 參數：`dropout-rate`、`doublet`、`rnd-seed`、beta-binomial read 數。輸出 genotype 與 read 數。〔程式：README〕
- genotype 記為 (wild, mutant) 數量，沒有 haplotype 標記。〔程式：README〕
- PyPI `scsim` 1.0.0（GPL3 宣告）；GitHub repo 沒有授權檔；最後 commit `ecc4bab`（2025-11-24）。https://github.com/haotianzh/scsim
- ScisTree2 README 說論文資料與腳本放在 Zenodo。〔程式〕

### CNAsim（samsonweiner/CNAsim）

- 產生 cell lineage 樹、CNA、CN profile 或 dwgsim read；可給兩個 haplotype reference（`-r1`、`-r2`）。〔程式：README〕
- 有 normal／pseudonormal 細胞比例（`-n1`、`-n2`）。〔程式：README〕
- 沒有 SNV 真值。〔程式：README＋`grep snv`〕
- seed：`tree.py` 用 `np.random.randint` 產生 ms 的 seed；`reads.py` 呼叫 `np.random.seed()`（無參數）。所以不能重現。〔程式〕
- GPL-3.0；最後 commit `f034398`（2026-09-09）。https://github.com/samsonweiner/CNAsim

### HCDSIM（BioThinkLab/HCDSIM）

- 輸出 clone 與 cell 的 haplotype-specific CN（`maternal|paternal`）、`clone_changes.csv`（含 `Haplotype` 欄）、`snp_phases.csv`、`tree.newick`；有 FASTQ、BAM。〔程式：docs/tutorials.md〕
- 有 `--random_seed`。〔程式：docs/man〕
- 沒有找到 somatic SNV 模擬。〔程式：`grep snv` 無結果〕
- MIT；最後 commit `3851dc0`（2026-10-16）。https://github.com/BioThinkLab/HCDSIM

### flahertylab SCSIM

- 「jointly simulating correlated single-cell and bulk next-generation sequencing data」；用階層抽樣，不是 phylogeny。〔程式：README〕
- `src/gen-scref.py` 預設 `seed = 10696`；`mix.py` 用 `rng_seed`。〔程式〕
- MIT；最後 commit `a8771a4`（2020-02-03）。https://github.com/flahertylab/scsim

### 二元矩陣類（只給 0／1／missing，沒有 read 數）

- **SCsnvcna**（compbio-mallory/SCsnvcna）：`code/simulation_code/gen_tree.py` 產生樹；`sim_par.py` 加 FP（alpha）、FN（beta）、missing、mutation loss、SNV-CNA overlap。沒看到 seed。沒有授權檔。`3824bf4`（2023-11-29）。〔程式〕
- **SPhyR**（elkebir-group/SPhyR）：`simulate` 從 perfect phylogeny 產生 k-Dollo 樹；`perturb` 加 FP／FN；`-s` 設 seed。BSD-3。`a3b0ebe`（2022-12-09）。〔程式：README〕
- **trisicell**（faridrashidi/trisicell）：`trisicell/datasets/_simulate.py` 的 `simulate()` 與 `add_doublets()`。BSD-3。`0c3ec56`（2023-12-23）。〔程式〕
- **SBMClone**（raphael-group/SBMClone）：`src/simulation.py` 產生稀疏區塊矩陣，有 `seed`。BSD-3。`6e962f1`（2021-10-13）。〔程式〕

### 只模擬 read、不模擬樹

- **SCSsim**（qasimyu/scssim）：`simuvars` 插入使用者指定的 SNV／CNV；`genreads` 模擬擴增與 read。沒有樹。BSD-3。〔程式：README〕
- **SCSilicon**（BioThinkLab/SCSilicon）：自動產生 SNV、CNV 與 subclone 標籤，依賴 SCSsim。MIT。沒看到 lineage tree。〔論文摘要〕

## 沒找到模擬程式的工具

- **PhISCS**（sfu-compbio/PhISCS）：只有 `PhISCS-I/helperFunctions.py::simulateMutantReferenceCounts`（從 VAF 抽 bulk read 數），沒有樹生成器。〔程式〕
- **PhISCS-BnB**（algo-cancer/PhISCS-BnB）：沒有模擬程式。〔程式〕
- **B-SCITE**（smalikic/B-SCITE）：README 提到模擬資料，但 repo 沒有生成器。〔程式〕
- **BiTSC2**（ucasdp/BiTSC2）：repo 只有推論程式（`code_function/tree_samp_fun.R`）。〔程式〕
- **SiFit**（KChen-lab/SiFit）：只有 `SiFit.jar`，可輸入真值樹做比較。〔程式〕
- **SiCloneFit**：沒找到 GitHub repo（試過 KChen-lab、hzi-bifo、hamimzafar）。程式可能在 bitbucket。〔未驗證〕
- **OncoNEM**：沒找到 repo；論文圖說列出模擬參數。scphylo-tools 有基於 OncoNEM 的 `simulate`。〔未驗證〕
- **SCARLET**、**Phylovar**：只有已產生的資料（`data/simulations`、`data/`），沒有生成器。〔程式〕
- **SCITE**、**infSCITE**、**SCIPhI**、**BnpC**：沒有找到獨立生成器。〔程式：repo 清單〕
- **HUNTRESS**、**ROVER**：GitHub 搜尋無結果（2 次）。〔未驗證〕
- **cancerSimCraft**（bioRxiv 2024.12.11.627708）：沒找到 repo。〔未驗證〕
- **long-read single-cell**：沒有找到專用模擬器。VISOR 可模擬 haplotype 標記的 long read，但不模擬 SNV 演化樹。〔論文摘要〕
- **DREAM single-cell lineage challenge**：是 CRISPR lineage barcode，不是腫瘤 SNV，排除。〔推論〕

## 搜尋範圍（2026-10-24）

- `gh api repos/...` 查 45 個候選 repo；`gh search repos` 查 16 個關鍵字（後半因 rate limit 中斷）。
- WebSearch：SCSilicon／single-cell DNA simulator、OncoNEM／SiCloneFit、cancerSimCraft、SCSilicon2、long-read single-cell simulator。
- 淺層 clone 到 scratchpad 讀碼：cellcoal、SimSCSnTree、CNAsim、scssim、PhISCS、PhISCS-BnB、B-SCITE、BiTSC2、SCsnvcna、COMPASS、SBMClone、trisicell、ScisTree2、scarlet、Phylovar、sistem、PSiTE、haotianzh/scsim、flahertylab/scsim、HCDSIM、SCSilicon、SiFit、BnpC、SPhyR。全部沒有執行。
