# CN-aware bulk 次克隆重建模擬器與 clustering／CCF 工具模擬器

調查日期：2026-10-24。範圍：CN-aware bulk subclonal reconstruction 模擬器、clustering／CCF 工具附帶的模擬程式、通用 clone tree 模擬套件。Read 層級（BAMSurgeon、SMC-Het reads）由其他調查負責。

證據標記：〔論文〕論文描述；〔程式〕讀過原始碼；〔推論〕分析推論；〔未驗證〕沒有直接證據。所有程式只讀，沒有執行。

## 結論

最有用的是 `elkebir-group/clonesim`。它是唯一把 allele-specific segment CN 放在 clone tree 邊上的工具。它也輸出每個 SNV 在兩個 allele 上的突變拷貝數（`xbar`、`ybar`）。這等於 haplotype-specific multiplicity 真值。它不產生 bulk read count，需要自己補一層 binomial 抽樣。

DeCiFer、SPRINTER、Tarabichi 2021 guide 都沒有公開模擬程式。

| 排名 | 工具 | 產生 tree 真值 | 產生 SNV read count | CN 綁在 tree 邊上 | allele／haplotype 資訊 | 對我們的用處 |
|---|---|---|---|---|---|---|
| 1 | clonesim（El-Kebir lab） | 是 | 否（只有 single-cell reads） | 是，每個 segment 一棵 allele-specific CNA tree | 有：segment `x`/`y` 與 SNV `xbar`/`ybar` | 高：可直接當 haplotype-aware 真值骨架 |
| 2 | PhylEx simulation | 是 | 是（bulk 多 region + scRNA） | 是，CN 沿 tree 用 birth-death 演化 | 有 `major_cn`/`minor_cn` 與變異拷貝數；沒有 segment | 中高：唯一同時把 multiplicity 與 CN 綁在 tree 上並出 bulk read 的 |
| 3 | PhylogicSim（PhylogicNDT） | 是（只寫在參數檔） | 是（多 sample、purity） | 否：CN 是 clonal，multiplicity 隨機抽 | 有 allele CN；沒有相位 | 中：格式簡單；seed 沒生效；Python 2 |
| 4 | QuantumCat（QuantumClone） | 內部產生，不輸出 | 是（多 sample、contamination） | 部分：可設 subclonal CNA fraction | 有 `AB` genotype 字串 | 低中：tree 真值拿不到 |
| 5 | SimClone1000（PCAWG-11） | 是（grid 設計） | 是 | 有 subclonal CN 參數 | 未驗證 | 低：依賴的 `simclone` R 套件找不到 |
| 6 | ccube vignette／clonesig SimLoader／mobster `random_dataset`／CNAqc sampler | 否 | 是（單 sample） | 否 | ccube、clonesig、CNAqc 有 major/minor | 低：沒有 tree |
| 7 | hatchet2-simulations | CN clone 結構 | 否（只有 CN） | 否 | allele-specific CN | 低：沒有 SNV |
| 8 | ClonePhyTester（Miura） | 是（附資料） | 是（附資料，含 `G7cna`） | 未驗證 | 未驗證 | 低：只確定有資料，生成器未確認 |

## 各工具

### 1. clonesim（El-Kebir lab）

- Repo：https://github.com/elkebir-group/clonesim ，commit `f148511`（2025-06-12）。GitHub 沒有 license 欄位，repo 內也沒有 LICENSE 檔。〔程式〕
- 生成器：`src/simulatemain.cpp`（執行檔 `simulate`），CNA tree 由 `generatecnatrees` 先列舉。README 描述為「Simulating clonal trees with segmental CNAs and SNVs」。〔程式〕
- CN 模型：每個 segment 抽一棵 allele-specific CNA tree（`CnaGraph::sampleCnaTree()`），再合併成一棵 clone tree（`phylo.addSegment(T, T.truncal())`）。`-kk` 控制 truncal segment 數。`lossProb = 0.05` 控制 allele loss。另有選項可違反 infinite alleles。〔程式〕
- SNV：`phylo.sampleMutations(n, l, ...)` 把 SNV 分到 `l` 個 cluster。〔程式〕
- 真值輸出（`-f -output_file_dir`）：`tree.tsv`、`node.tsv`、`proportions.tsv`、DOT 圖。`node.tsv` 欄位是 `node segment x y m xbar ybar clusterIDofMutation`。`x`/`y` 是兩個 allele 的 CN；`xbar`/`ybar` 是 SNV 在兩個 allele 上的突變拷貝數。〔程式：`src/phylogeny.cpp` L355–440〕
- 多 sample：`-m`（預設 2）。Purity：`-purity`（預設 0.8）。Seed：`-s`（預設 0）。〔程式〕
- Read 層級：`simulate` 不抽 bulk read count。`generatesinglecells` 只產生 single-cell 的 binomial reads。〔程式：`src/singlecellgeneration.cpp` L409〕
- 下游：Pharming（https://github.com/elkebir-group/Pharming ，BSD-3）用它當 scDNA 模擬基底。〔程式〕
- 推論：`xbar`/`ybar` 可直接對應 HP1/HP2 上的 SNV multiplicity。加上 purity 與 `proportions.tsv`，就能算出每個 sample 的 expected VAF 與 haplotype-specific VAF。只要補 binomial 抽樣，就能產生 PhyClone 輸入。〔推論〕

### 2. PhylEx simulation

- Repo：https://github.com/junseonghwan/PhylEx ，commit `83f4654`（2023-11-26）。沒有 license。〔程式〕
- 生成器：`simulation/main.cpp`、`simulation/simul_data.cpp`，編譯成 `simul`。設定檔 key 有 `seed`、`n_regions`、`n_sites`、`bulk_mean_depth`、`birth_rate`、`death_rate`、`max_cn`、`var_cp_prob`、`n_cells` 等。〔程式〕
- CN 模型：開啟 birth-death 模式時（`birth_rate>0` 且 `max_cn>2`），每個 SNV locus 的 `ref_cn` 沿 tree 用 rate matrix 演化。SNV 出現的 node 上，用 `var_cn = Binomial(var_cp_prob, ref_cn-1)+1` 決定變異拷貝數。CN 與 multiplicity 都綁在 tree 邊上，但是以 locus 為單位，不是 segment。〔程式：`simul_data.cpp` L209–250〕
- Read：depth `~ Poisson(bulk_mean_depth * total_cn/2)`，VAF 用 `phi * var_cn / total_cn`。〔程式：`simul_data.cpp` L163–178〕
- 真值輸出：`simul_ssm.txt`、`genotype_ssm.txt`（欄位含 `major_cn`、`minor_cn`）、`cts_cn_profile.txt`、`cluster_labels.txt`、`ancestral_matrix.csv`、`cellular_prev.csv`、`clone_freq.csv`、single-cell 資料與 cell-to-node 對應。〔程式〕
- Purity：程式內找不到 purity 參數。〔程式；是否以 root 的 prevalence 代替，未驗證〕
- 論文：Jun et al., PhylEx（scRNA + bulk）。〔論文；未逐頁核對〕
- 推論：這是唯一同時「CN 沿邊演化 + multiplicity 由 tree 決定 + bulk 多 region read count」的生成器。缺 segment 與 haplotype 相位。〔推論〕

### 3. PhylogicSim（PhylogicNDT）

- Repo：https://github.com/broadinstitute/PhylogicNDT ，commit `e47fb07`（2025-04-17）。Broad 自訂 license（GitHub 顯示 NOASSERTION）。〔程式〕
- 生成器：`PhylogicSim/SimEngine.py`，入口 `./PhylogicNDT.py PhylogicSim`。程式是 Python 2 語法（`print 'Using provided...'`）。〔程式〕
- Tree：`nx.generators.directed.gn_graph` 產生隨機樹，限制每個 node 子代 <4。CCF 由 parent 剩餘量往下切。〔程式：L190–236〕
- CN：從 seg 檔（或內建 hg19 profile）取每條 contig 的 allelic CN。CN 是 clonal，沒有綁在 tree 邊上。Multiplicity 從 `1..allele CN` 隨機抽，偏向 1。〔程式：L295–330〕
- Read：beta-binomial coverage（`-ap 2 -b 18 -nb 1000`）或 coverage 檔；alt ~ Binomial。過濾 alt<3。多 sample（`-ns`），per-sample purity（`-p` 或 `-pfile`），artifact 比例（`-a`）。〔程式〕
- 輸出：每 sample 一個 MAF-like `.txt`（含 `t_ref_count`、`t_alt_count` 與 CCF 直方圖）、`.sif`、`.truth.txt`（`cluster_id totalCN multiplicity ccf_*`）、`.simulation_paramters.tsv`（含 tree `edges`）。〔程式：L628–727〕
- Seed：函式有 `seed=157` 參數，但程式從沒呼叫 `np.random.seed` 或 `random.seed`。結果不可重現。〔程式〕

### 4. QuantumCat（QuantumClone）

- Repo：https://github.com/DeveauP/QuantumClone ，commit `45b595b`（2021-10-27）。`DESCRIPTION` 寫 GPL-2；GitHub 沒偵測到 license。〔程式〕
- 生成器：`R/QuantumCat.R` 的 `QuantumCat()`，內部呼叫 `R/Tree_generation.R` 的 `phylo_tree_generation()`。〔程式〕
- CN：`ploidy` 可設 `"disomic"`、指定 genotype 字串（如 `AAB`），或用 Poisson 抽 A/B 拷貝數。可設 `Subclonal.CNA.fraction`。〔程式〕
- Read：depth ~ NegBinomial(size 4.33, mu=depth)，alt ~ Binomial。多 sample；`contamination` 給 normal 比例。〔程式〕
- 輸出：每 sample 一個 data.frame（`Chr Start Genotype Cellularit number_of_copies Frequency Depth Alt`）。Tree 物件沒有回傳。沒有 seed 參數。〔程式〕

### 5. SimClone1000（PCAWG-11，Tarabichi）

- Repo：https://github.com/galder-max/SimClone1000 ，commit `909395c`（2018-08-31），GPL-3。〔程式〕
- 內容：`Step1.deriveGrid.R` 從 PCAWG 實際 purity、ploidy、coverage、cluster 結果建 grid；`simulateSample.R` 每個 grid 點產生一個 tumour。`set.seed(12345)`。〔程式〕
- `simulate_dataset()` 參數有 `no.subsamples`、`cellularity`、`sample.subcl.cn.frac`、`cluster_ccfs`、`archive_copynumber_index`。〔程式〕
- 缺點：依賴 `library(simclone)`（README 指向 `github.com/sdentro/simclone`）。這個 repo 回 404，GitHub code search 也找不到。〔程式〕
- 推論：這組資料是 PCAWG-11 模擬的來源。Tarabichi 2021 Nat Methods guide 是否用同一套，未驗證。〔推論〕

### 6. 只有 VAF／CCF、沒有 tree 的單 sample 模擬器

- **ccube**（https://github.com/keyuan/ccube ，`2345c3a`，2022-12-20，GPL-3）：`R/util.R` 匯出 `GenerateCopyNumberProfile()` 與 `GenerateSubClonalCNProfile()`（major/minor、2 個 subclone 的 subclonal CN）。vignette 用 `rbinom`／`rpois` 抽 read，multiplicity 從 `1..major_cn` 隨機抽。〔程式〕
- **clonesig**（https://github.com/judithabk6/clonesig ，`ec9d0fc`，2023-01-30，MIT）：`clonesig/data_loader.py` 的 `SimLoader` 產生 purity、depth、`C_tumor_tot`、`C_tumor_minor`、`C_tumor_mut` 與 signature。沒有 tree。分析程式在 https://github.com/judithabk6/Clonesig_analysis （CC-BY-4.0）。〔程式〕
- **mobster**（https://github.com/caravagnalab/mobster ，`85c898f`，2025-08-21，GPL-3）：`R/random_dataset.R` 產生 Beta 混合 + Pareto tail 的 VAF。沒有 CN，沒有 tree。有 `seed` 參數。〔程式〕
- **CNAqc**（https://github.com/caravagnalab/CNAqc ，`4b7cea4`，2026-08-31，GPL-3）：`nobuild/sampler.R` 有 `sample_CNA_segments()`（clonal allele-specific segment）與 `sample_clonal_mutations_from_CNA()`。在 `nobuild/`，沒有匯出。只有 clonal。〔程式〕
- **PyClone-VI**（https://github.com/Roth-Lab/pyclone-vi ，`0730683`，GPL-3）：只有 `pyclone_vi/tests/simulate.py` 的 binomial 測試 helper。沒有 tree、沒有 CN。〔程式〕

### 7. hatchet2-simulations（HATCHet）

- Repo：https://github.com/raphael-group/hatchet2-simulations ，`48c7dd6`（2024-04-02），BSD-3。〔程式〕
- Snakemake 流程。`scripts/simulate_genome.py` 在 MASCoTE 的 clone CN 表上加事件（含 mirrored）。CN only，沒有 SNV tree。〔程式〕
- 舊資料在 https://github.com/raphael-group/hatchet-paper `simulation/`。〔程式〕

### 8. ClonePhyTester（Miura et al.）

- Repo：https://github.com/SayakaMiura/ClonePhyTester ，最後 push 2021-08-13，README 寫類 BSD-2 license。〔程式〕
- 內容：打包了 benchmark 用的模擬資料集（`G7`、`G7cna`、`G12`、`MA`、`MA50`、`P10`、`TGconst`、`TGlinear`、`TGstep`）與七個方法的結果。〔程式〕
- 生成器是否在 repo 內，未驗證。`G7cna` 的 CN 模型未讀。〔未驗證〕

## 沒找到模擬程式的工具

- **DeCiFer**：主 repo https://github.com/raphael-group/decifer （`1b6f6d8`，BSD-3）只有推論程式與 test 資料。`raphael-group/decifer-data` README 寫「Simulated data will be available soon...」，最後 push 2021-04-07。〔程式〕
- **SPRINTER**：https://github.com/zaccaria-lab/SPRINTER （`f75e87d`）沒有模擬目錄。〔程式〕
- **Tarabichi 2021 guide**（Nat Methods 18:144, doi:10.1038/s41592-020-01013-2）：網路搜尋沒找到程式 repo。〔未驗證〕
- **simclone（sdentro）**：404。〔程式〕
- **PyClone（舊版）、DPClust、cloneHD、CliPP、SVclone**：repo 內沒有 SNV + tree 的生成器。CliPP 只附 `sample/` 範例資料。SVclone 的 SV 模擬在 `mcmero/sv_simu_pipe`，不屬 SNV。〔程式〕
- **tumourevo**（caravagnalab）：分析 pipeline，不是模擬器。caravagnalab 的模擬器是 ProCESS（https://github.com/caravagnalab/ProCESS ），屬 read 層級空間模擬，由其他調查負責。〔程式〕
- **MEDICC2、CHISEL、Alleloscope**：CN-only 或 scDNA，沒有 SNV tree 真值，本次不深入。〔推論〕
- **Sclust、CTPsingle、SciClone、Battenberg**：沒找到公開模擬程式（CTPsingle GitHub repo 未找到；其餘沒有搜尋到 sim 腳本）。〔未驗證〕
- **`tumor-tree-sim`、`cloneTreeSim`**：GitHub repo 搜尋沒有結果。〔程式〕

## 搜尋範圍

- 日期：2026-10-24。
- 方法：`gh api repos/...` 查 metadata；淺 clone 到 scratchpad 讀碼（不執行）；`gh search repos`；WebSearch（Tarabichi guide、DeCiFer simulation）。
- 本機 clone 路徑：`/tmp/claude-1024/-bip8-disk-boyu114-main-work/18fc1cc2-ffb5-4afb-8a48-a15890b40de5/scratchpad/clones/`。
