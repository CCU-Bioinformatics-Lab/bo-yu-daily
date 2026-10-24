# 演化／agent-based／spatial 腫瘤模擬器調查

調查日期：2026-10-24。範圍：用族群遺傳、agent-based 或 spatial 模型模擬腫瘤演化，並輸出「真值 lineage／clone tree」加上「模擬 SNV 定序資料」的公開程式。Pairtree（`pearsim`）與 CONIPHER（`TRACERx_simulation_tool`）已在 [`../notes/05_OTHER_SIMULATORS.md`](../notes/05_OTHER_SIMULATORS.md) 涵蓋，這裡不重做。

機器可讀總表：[`04_evolutionary_simulators.tsv`](04_evolutionary_simulators.tsv)。

證據標記：〔論文〕論文或文件描述；〔程式〕讀過 repo 原始碼（只讀，沒執行）；〔推論〕我們的判斷。程式碼都以 shallow clone 讀取，commit 列在各節。

## 結論

一句話：**ProCESS 是唯一同時給出 haplotype-aware reads、allele-specific CN、purity、multi-region 與 seed 的演化模擬器。SISTEM 最接近 PhyClone 輸入格式。** 其他工具大多缺 CN、缺 purity 或缺 read 層。

| 排名 | 工具 | 真值樹 | SNV 資料層 | CN | multi-sample | purity<1 | haplotype／read 層 | 轉成 PhyClone 的工作量 |
|---|---|---|---|---|---|---|---|---|
| 1 | **ProCESS**（前身 rRACES）＋ CLONES | cell-level forest | VAF 表＋SAM reads | allele-specific＋WGD | 是 | 是 | **有**：reads 依 allele 產生，帶 germline SNP | 高：要把 cell forest 收斂成 clone tree |
| 2 | **SISTEM** | clone tree（Newick） | bulk ref/alt 計數 | allele-specific＋WGD | 是（多個 site） | 是（normal 細胞） | 部分：只有 single-cell reads 分 allele | 低到中 |
| 3 | iscc | lineage＋clone | 計數矩陣＋reads | total CN（homolog 部分記錄） | 是 | 未驗證 | 部分 | 中；工具很新，需先驗證 |
| 4 | CHESS | cell genealogy | 多個 punch 的 alt/depth | 無 | 是 | 否 | 無 | 中：要自建 clone tree，CN 全設 2 |
| 5 | TEMULATOR | clone 標籤 | 單一樣本 alt/depth | 無 | 否 | 是 | 無 | 低，但只能做單樣本、無 CN |
| 6 | CancerSeqSim.jl | subclone 頻率 | VAF＋depth | 無 | 部分 | 是 | 無 | 中；Julia 版本老舊 |
| 7 | MASCoTE | clone tree | **沒有 somatic SNV** | allele-specific＋WGD | 是 | 是 | **有**：germline SNP 分兩條 haplotype | 不適用 SNV tree；只適合 CN／haplotype 部分 |
| 8 | J-SPACE | cell Newick | single-cell reads（ART） | 無 | 否 | 未提 | 無 | 高 |
| 9–13 | demon、tumopp、SITH、CINner、OncoSimulR、SCIMET | genealogy／genotype tree | 無 read 計數或只有 VAF | 多數無（CINner 例外） | 不一 | 多數無 | 無 | 高：要自己補 read 層 |

給我們的建議〔推論〕：

1. 想測 **HP1/HP2 特徵**：先看 ProCESS。它從 1000G 的 phased germline 產生每個細胞、每個 allele 的 reads，所以 SAM 裡天然有 SNV 與 germline SNP 的共現。缺點是 sequencer 模型偏 Illumina，`read_size` 能否設成 long read 長度未測。
2. 想快速得到 **PhyClone 可用的 bulk 資料加 clone tree**：用 SISTEM。它的輸出最接近 PhyClone 的 8 個欄位。
3. 其餘工具只適合當 genealogy 來源，再接我們自己的 read／CN 層。

## 各工具

### 1. ProCESS（前身 rRACES）＋ CLONES 核心

- Repo：`caravagnalab/ProCESS`（GPL-3.0，default branch commit `796a3d1`，2026-05-21；GitHub `pushed_at` 2026-10-05）。`caravagnalab/rRACES` 現在轉址到 ProCESS。C++ 核心是 `albertocasagrande/CLONES`（MIT，`0111bee`，2026-10-05），由 `configure` 在安裝時 `git clone`。〔程式〕
- 真值：`PhylogeneticForest` 是取樣細胞的 cell-level forest。`get_sampled_cell_mutations()` 給每個細胞的 SNV／indel，`get_sampled_cell_CNAs()` 給 CNA。CNA 與 driver 表有 `allele`、`src_allele` 欄（`src/phylogenetic_forest.cpp` L321–325）。`get_bulk_allelic_fragmentation(sample)` 給每個樣本每段的 allelic type。〔程式〕
- 定序資料：`simulate_seq()` 回傳表格，每個樣本有 `<sample> occurrences`、`<sample> coverage`、`<sample> VAF` 三欄。`write_SAM=TRUE` 會寫 SAM。〔程式：`vignettes/sequencing.Rmd` L60–92、L139–179〕
- purity：`simulate_seq(purity=0.7, with_normal_sample=TRUE)`。〔程式：`vignettes/sequencing.Rmd` L182–207；`src/seq_simulation.cpp` L516–569〕
- **haplotype 資訊**：CLONES 依「細胞 → allele → fragment」逐段產生 reads，並把該 allele 的 germline 變異一起放進 read（`include/read_simulator.hpp` L1588–1618）。germline 來自 1000 Genomes 的 IGSR VCF（`include/germline.hpp` L134–144）。SAM tag 只有 `RG`（樣本）、`NM`、`CB`（細胞 ID）；**沒有 HP 或 allele tag**（L1458–1464）。〔程式〕
  - 推論：同一 read 上 somatic SNV 與 germline het SNP 的共現是真的。allele 真值可從 cell mutation 表的 `allele` 欄取得。要 HP tag，需要自己用 germline phase 標註或跑 longphase。〔推論〕
  - read 模型有 `read_size`、`insert_size_mean`、error rate 與 quality score（`src/seq_simulation.cpp` L423–462、L512–550）。看不到 ONT 專用錯誤模型。〔程式〕
- multi-sample：tissue 上可取多個樣本與多個時間點。〔程式：`vignettes/sampling.Rmd`、`time_series.Rmd`〕
- seed：`simulate_seq(seed=)`，種子寫進回傳的 `parameters`。〔程式：`src/seq_simulation.cpp` L542、L589〕
- 已有資料：`caravagnalab/ProCESS-examples` 的 SCOUT cohort，7 個合成病人（SPN01–SPN07），每個有 12 種 coverage × purity 組合，共約 30 TB。流程接 nf-core/sarek 與 nf-core/tumourevo，並用 ASCAT 對 `get_bulk_allelic_fragmentation` 驗證。〔程式：`vignettes/SCOUT.Rmd` L39–115；ProCESS-examples README〕
- 論文：本次搜尋沒找到 ProCESS 的正式論文。〔未驗證〕
- 轉成 PhyClone 的工作〔推論〕：
  - `alt_counts` = occurrences；`ref_counts` = coverage − occurrences；`tumour_content` = 設定的 purity。
  - `major_cn`／`minor_cn`：從 allelic fragmentation 取 SNV 所在段。subclonal CN 會出現多種 allelic type，需要決定規則。
  - clone tree：要把 cell forest 依 mutant（driver 物種）或 clade 收斂。passenger SNV 指派到 clone，需用 `get_first_occurrences()` 找出現的細胞再對應到 clone。工作量高。

### 2. SISTEM

- Repo：`samsonweiner/sistem`（GPL-3.0，`627f888`，2026-05-30；PyPI `sistem`）。論文：Weiner & Bansal, *Bioinformatics* 2025（PMC12701798）。〔論文〕〔程式〕
- 真值：`simulate_clonal_lineage` 產生 clone tree，leaf 是觀察到的 clone，帶細胞數；內部節點是祖先。`Tree.save()` 寫 Newick。另有 migration graph。〔程式：`sistem/lineage/tree.py` L156–232；`sistem/anatomy/utils.py` L113–123〕
- CN：`observed_CNPs.tsv`、`ancestral_CNPs.tsv`，每個 region 分 allele 0／1 計數，是 allele-specific CN。支援 focal、arm、chromosome 事件與 WGD。〔程式：`sistem/data/utils.py` L182–194；`sistem/data/profiles.py` L14–40〕
- SNV 資料：`gen_readcounts_bulk()` 寫 `readcounts.tsv`，欄位是 `Chrom Pos` 加每個 site 的 `ref,alt`。期望 VAF 由 clone 比例與每個 clone 的 alt／total 拷貝數計算。〔程式：`sistem/data/reads.py` L223–300；`profiles.py` L192–200〕
- purity：`ncells_normal` 加入 diploid 細胞；metastatic site 依原發灶比例補 normal。〔程式：`parameters.py` L59、L120；`reads.py` 中 `diploid` 處理〕
- haplotype：single-cell reads 對 allele 0 用 `ref`、allele 1 用 `alt_ref` 各跑一次 dwgsim，再合併 FASTQ。bulk 沒有 reads。〔程式：`reads.py` L51–106；`parameters.py` L22〕
- seed：沒有 seed 參數。程式全用 `np.random` 全域 RNG，所以外部 `np.random.seed()` 應可重現計數；dwgsim 不受控。〔程式＋推論〕
- 轉成 PhyClone〔推論〕：工作量低到中。每個 site 是一個 sample；`major_cn`／`minor_cn` 從 clone CNP 取，但 bulk 混合多 clone 時要選規則（例如取主要 clone）。`tumour_content` = 1 − normal 細胞比例。clone tree 直接用 Newick。

### 3. iscc（in silico cancer center）

- Repo：`pedrofale/iscc`（MIT，`003132f`，2026-09-21；PyPI `insilico-cancer-center` 0.3.0）。沒找到論文。〔程式〕
- README：模擬單一腫瘤的生長、治療、取樣，再產生 single-cell 與 bulk DNA、RNA、spatial 資料，直到 reads。〔程式：`README.md` L10–14〕
- DNA 層輸出 coverage、alt count、VAF 矩陣，加上真值 CN 與 alt fraction。reads 由 DWGSIM 或 ART 產生，寫法註明「SISTEM-faithful」。〔程式：`src/iscc/data/dna.py` L1–23；`src/iscc/data/reads/dna.py` L1–30〕
- truncal SNV 記錄 `seeded_truncal_homolog`；germline 有 het site。〔程式：`src/iscc/tumor/germline.py` L83–315〕
- `cell_cnv` 是 total CN；是否有完整 allele-specific CN 未驗證。預設是合成基因組。〔程式＋未驗證〕
- 有 `integrations/multiregion.py` 與 `clones_from_clades()`。〔程式〕
- 推論：功能面很廣，但非常新、沒論文。要用前先跑小例子驗證。

### 4. CHESS（CHESS.cpp）

- Repo：`kchkhaidze/CHESS.cpp`（`6af3a0a`，2019-05-04）。**沒有授權檔**，R DESCRIPTION 也沒有 License 行。論文：Chkhaidze et al., *PLoS Comput Biol* 2019。〔程式〕〔論文〕
- 2D／3D spatial 生長。`SimulateTumourSample()` 輸出 punch／needle biopsy 的 VAF 檔，欄位 clone、alt、depth、id；`SimulateTumourTree()` 輸出 single-cell 樹。〔程式：`README.md` L126–140〕
- depth 模型：Poisson、beta-binomial（overdispersion 0.08）、固定。〔程式：`src/CellSample.cpp` L31–37；README L90–98〕
- 沒有 purity、沒有 CN。有 `--seed`。〔程式：README L82–83；grep 無 purity〕
- 推論：可做 spatial multi-region 但 CN 全設 2、purity 全設 1。沒有授權，不能複製程式碼。

### 5. TEMULATOR

- Repo：`T-Heide/TEMULATOR`（DESCRIPTION 寫 GPL-3，`273fbe1`，2022-06-30）。MOBSTER（Caravagna et al. 2020）的 150 份模擬資料出自它，已附在 `data/`。〔程式：`R/data.R`〕
- `sample(min_vaf, purity, depth, depth_model)` 回傳每個 mutation 的 clone、alt、depth、VAF、CCF。〔程式：`R/RcppExports.R` L10–17；`src/Universe.cpp` L330–333〕
- 單一 well-mixed 樣本，沒有 CN。clone 結構是使用者指定的 subclone 插入。〔程式〕
- seed 有效，有測試。〔程式：`tests/testthat/test-simulations.R` L72–101〕

### 6. CancerSeqSim.jl

- Repo：`marcjwilliams1/CancerSeqSim.jl`（MIT，`867aab9`，2019-05-07）。Williams et al. 的 neutral evolution 系列。〔程式〕
- `simulate()` 有 `read_depth`、`cellularity`、`ploidy`、`nclones`、`μ` 等參數，輸出 VAF 與 depth。〔程式：`src/samplesim.jl` L220–319〕
- 有 `multiplesamples.jl`，細節未驗證。沒有 CN 事件，`ploidy` 只是常數。〔程式〕
- `simulate()` 沒有 seed 參數。Julia 套件格式是 1.0 前的 `REQUIRE`。〔程式〕

### 7. MASCoTE

- Repo：`raphael-group/mascote`（Princeton 自訂 BSD 類授權，`dd93162`，2020-12-03）。HATCHet 論文的模擬框架。〔程式〕〔論文〕
- 先在兩條 haplotype 上放 germline SNP，再依隨機 clone tree 施加 CNA 與 WGD，用 ART＋BWA 產生每個 clone 的 reads，再依 clone 比例混成多個樣本 BAM。〔程式：`README.md` L3–89〕
- grep `somatic`／`SNV` 沒有命中。**沒有 somatic SNV**。〔程式〕
- 推論：不能直接做 SNV clone tree。可借用它的 haplotype-aware CN read 生成方式。

### 8. J-SPACE

- Repo：`BIMIB-DISCo/J-Space.jl`（論文寫 BSD；GitHub 偵測 NOASSERTION；最後 commit `87f02a3`，2024-03-06）。論文：Angaroni et al., *BMC Bioinformatics* 2022。〔論文〕
- 輸出取樣細胞的 Newick、driver tree、每細胞 FASTA、ART 產生的 single-cell reads。沒有 CN，未提 purity，只有單一時間點單一腫瘤。〔論文：PMC9270769，經 WebFetch 讀取〕
- 程式碼未 clone。〔未驗證〕

### 9. demon（＋ Warlock）

- Repo：`robjohnnoble/demon_model`（GPL-3.0，`0989187`，2025-01-28）。〔程式〕
- deme-based spatial 模型。輸出 `phylo.dat`、`driver_phylo.dat`（genotype phylogeny）與 `output_allele_counts.dat` 等。沒有 depth 或 read 抽樣。`normal_birth_rate` 可加入 normal 細胞。有 `seed`。〔程式：`README.md` L40–80；`src/demon.cpp` 輸出檔名〕
- Warlock（Bak et al., arXiv 2301.07808）是包 demon 的 workflow。GitHub 上沒找到 repo。〔論文；repo 未找到〕

### 10. tumopp

- Repo：`heavywatal/tumopp`（MIT，`fcfa4e2`，2026-06-22）；R 介面 `heavywatal/rtumopp`（MIT，`6e00c30`，2026-08-25）。Iwasaki & Innan, *PLoS One* 2017。〔程式〕
- C++ 寫 `population.tsv.gz`（每個細胞的 id、ancestor、birth、death、座標），是完整 cell genealogy。〔程式：`src/simulation.cpp` L232–258〕
- R 端在 genealogy 上用 Poisson 放 mutation 並算樣本 VAF；沒有 read depth、CN、purity。〔程式：`rtumopp/R/ms.R` L36、L58〕

### 11. 其他（簡述）

- **SITH**（`phillipnicol/SITH`，GPL≥2，`ac69cfb`，2024-04-02）：Waclaw 類 3D 模型。bulk VAF 用 `rpois` depth 加 `rbinom` alt。無 CN。〔程式：`R/sequencing.R` L191–194〕
- **CINner**（`dinhngockhanh/CINner`，GitHub MIT／DESCRIPTION GPL≥2，`8c98f83`，2026-06-16）：CIN 為主，有 cell 與 clone phylogeny、allele-specific CN、CN-LOH、WGD。SNV 只有 driver。〔程式：`README.md` L6–25〕
- **OncoSimulR**（`rdiaz02/OncoSimul`，GPL≥3，`26d96c7`，2026-04-16）：fitness landscape 模擬，輸出 genotype 頻率與 clone genealogy，沒有 read 層。〔程式：DESCRIPTION〕〔推論：輸出內容依既有知識，未逐行驗證〕
- **SCIMET**（`cancersysbio/SCIMET`，無授權，`427a9bc`，2019-05-28）：metastasis timing 的 ABC 腳本，輸出 deme tree Newick。不是 benchmark 生成器。〔程式：`ABC_simulation/deme_tree_generator_met.py` L7–49〕

### 範圍外但相關（不列入排名）

- **HeteroGenesis**（`GeorgetteTanner/HeteroGenesis`，GPL-3.0，2024-03-14）：clone tree 由使用者給定，不是演化模擬。〔程式：repo 描述〕
- **SimClone1000**（`galder-max/SimClone1000`，GPL-3.0，2018-08-31）：參數式 grid 設計，依賴 `sdentro/simclone`，該 repo 現在 404。〔程式〕
- **ClonalSim**（Bioconductor，MIT）：參數式 founder／shared／private mutation，不是演化模型。〔程式：r-universe 描述〕
- **cancerSimCraft**（`haijingjin/cancerSimCraft`，2025-03-07）與 **CNAsim**（`samsonweiner/CNAsim`，GPL-3.0，2026-09-09）：以 single-cell CN 為主，屬其他調查範圍。〔程式：repo 描述〕

## 沒找到程式的工具

- **TumorSimulator（Waclaw 2015）**：不在 GitHub。只在 Edinburgh 個人頁提供 v1.2.3 ZIP（https://www2.ph.ed.ac.uk/~bwaclaw/cancer-code）。沒有下載檢查。
- **Warlock**：只有 arXiv 2301.07808；GitHub 搜尋沒有結果。
- **CHESS 的 Python 或其他版本**：只找到 `CHESS.cpp`。
- **TumorEvolver、TumourSims、CloneSim、SLiM 腫瘤模型、PhyloSim（腫瘤用途）**：GitHub repo 搜尋與網路搜尋都沒有對應的腫瘤演化＋定序模擬程式。
- **OG-SPACE**：有論文（arXiv 2110.06588），GitHub 搜尋沒找到 repo。

## 搜尋範圍

- 日期：2026-10-24。
- GitHub：`gh api repos/...` 檢查候選 repo；`gh search repos` 查 SISTEM、warlock、TumorSimulator、SimClone1000、MASCoTE、SCIMET、TumourSims、HeteroGenesis、CloneSim、tumor evolver、J-SPACE、OG-SPACE、cancerSimCraft、iscc。
- 網路：WebSearch 查 SISTEM、Waclaw TumourSimulator、Warlock、2025 agent-based 模擬器、ProCESS 論文；WebFetch 讀 J-SPACE 論文（PMC9270769）；PyPI JSON 查 iscc；r-universe 查 ClonalSim。
- 讀碼：shallow clone 到 scratchpad，只讀不執行。clone 的 repo：ProCESS、CLONES、sistem、iscc、TEMULATOR、CancerSeqSim.jl、CHESS.cpp、demon_model、tumopp、rtumopp、CINner、mascote、SimClone1000、SITH、SCIMET。
- 沒做：沒有執行任何模擬器；沒有下載 SCOUT 資料；ProCESS 的 long `read_size` 行為未測。
