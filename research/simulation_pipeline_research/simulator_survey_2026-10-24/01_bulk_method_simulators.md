# Bulk 建樹方法論文附帶的模擬生成器

調查日期：2026-10-24。範圍：bulk 定序 clone tree 建樹方法論文附帶的模擬程式。Pairtree 的 `pearsim`、CONIPHER 的 `TRACERx_simulation_tool`、PhyClone 的 FS-CRP／TSSB 已在 [`../notes/05_OTHER_SIMULATORS.md`](../notes/05_OTHER_SIMULATORS.md) 處理，本文不重複。

證據標籤：〔論文〕論文或 README 的主張；〔程式〕讀過原始碼（只讀、沒執行）；〔推論〕由程式推出、未實測。本文沒有執行任何生成器。

## 結論

- **沒有一個生成器同時給出「somatic SNV + 樹上的 allele-specific CN + read 層級的 haplotype 資訊」。** 最接近的組合是 clonesim（SNV 在哪個 allele 的真值）加 MASCoTE（haplotype 分開的 clone 基因體與 BAM）。
- **clonesim 最符合我們的模型需求。** 它在樹的邊上放 allele-specific CNA，並記錄每個 SNV 落在哪個 allele 上（`xbar`／`ybar`）。缺點：bulk 只輸出真值，不輸出 read count。
- **MASCoTE 是唯一輸出真正 read（BAM）的工具。** 它給每個 clone 產生 maternal／paternal 兩份 FASTA，CNA 與 WGD 放在樹的邊上。缺點：沒有 somatic SNV，read 模擬器是 Illumina 的 ART。
- `mutsim`（Orchard 用的 pearsim fork）有 SNV phase 與 CNA phase，但種子 bug 與 pearsim 相同。
- 其餘生成器（MACHINA、CALDER、fastBE、ClonEvol 等）沒有 CN，或 CN 不連到樹，只適合測 topology。

| 排名 | 工具 | 生成器位置 | 資料層級 | CN 模型 | purity<1 | 多樣本 | haplotype／read | 種子可重現 |
|---|---|---|---|---|---|---|---|---|
| 1 | clonesim（Pharming） | `elkebir-group/clonesim` `simulate`、`generatesinglecells` | bulk 只有真值；single-cell 有 read count | allele-specific，樹邊上的 segment CNA | 是 | 是 | **SNV 所在 allele 真值** | 是 |
| 2 | MASCoTE（HATCHet） | `raphael-group/mascote` `src/mascotte.py`、`MixBAMs.py` | **BAM read** | allele-specific + WGD，樹邊上 | 是 | 是 | **haplotype FASTA、phased germline SNP**；無 somatic SNV | 是（`-s`） |
| 3 | mutsim（Orchard） | `ethanumn/mutsim` `make_simulated_data.py` | count | allele-specific CNA event，帶 phase | 否（純腫瘤） | 是 | SNV phase 與 CNA timing | 否（同 pearsim bug） |
| 4 | PhylEx simulator | `junseonghwan/PhylEx` `simulation/` | bulk count + scRNA 每細胞 count | 每個 SNV 的 ref／var copy 沿樹演化 | 未確認 | 是（multi-region） | 每細胞 read，不是每 read | 是 |
| 5 | PhylogicSim | `broadinstitute/PhylogicNDT` `PhylogicSim/SimEngine.py` | count（beta-binomial） | 從 seg 檔讀 allele-specific CN，不連到樹 | 是 | 是 | 無 | 否 |
| 6 | MACHINA `simulate` | `raphael-group/machina` `src/simulation/` | count | 無 | 是（`-P`） | 是 | 無 | 是 |
| 7 | CALDER branchsim | `raphael-group/calder` `branching-sim/branchsim.py` | count | 無 | 否 | 是（縱向） | 無 | 是 |
| 8 | fastBE `simulation.py` | `raphael-group/fastBE` `scripts/simulation.py` | count | 無 | 否 | 是 | 無 | 是 |
| 9 | ClonEvol `sim.r` | `hdng/clonevol` `simulations/sim.r` | count | 只擾動 VAF（`cn.rate`） | 否 | 是 | 無 | 是 |
| 10 | AncesTree `makeSimData.py` | `raphael-group/AncesTree` `src/python/makeSimData.py` | count | 無 | 否 | 是 | 無 | 否；缺模組 |
| 11 | CITUP `generatingInput` | `sfu-compbio/citup` `src/generatingInput.cpp` | frequency | 無 | 否 | 是 | 無 | 預設否 |
| 12 | PICTograph `simulation.R` | `KarchinLab/pictograph` `R/simulation.R` | count | 整數 CN + multiplicity，不連到樹 | 隱含 | 是 | 無 | 寫死種子 |
| 13 | TUSV `sim.py` | `jaebird123/tusv` `sim/sim.py` | CN／SV 矩陣 | 總 CN + SV | 未確認 | 是 | 無；也沒有 SNV | 否 |

## 每個工具

### 1. clonesim（El-Kebir lab；Pharming 用）

- Repo：https://github.com/elkebir-group/clonesim ，commit `f148511`（2025-06-12），沒有授權檔。〔程式〕
- README 說明它是「Simulating clonal trees with segmental CNAs and SNVs」。流程是先 `generatecnatrees` 列出 allele-specific CN state tree，再用 `simulate -S cnatrees.txt` 產生 clone tree。〔程式〕README
- `simulate` 有 `-purity`（預設 0.8）、`-m` 樣本數、`-k` segment 數、`-kk` truncal segment 數、`-l` cluster 數、`-n` SNV 數、`-s` 種子。〔程式〕README
- 輸出 `tree.tsv`（父子邊）、`node.tsv`、`proportions.tsv`（每個 node 在每個樣本的比例）。〔程式〕`src/phylogeny.cpp` L356–358
- `node.tsv` 欄位是 `node segment x y m xbar ybar clusterIDofMutation`。`Genotype(x, y, xbar, ybar)` 裡 `x`、`y` 是兩個 allele 的 CN，`xbar`、`ybar` 是帶突變的 copy 數。〔程式〕`src/genotypetree.h` L38
- 所以每個 SNV 在每個 clone 中「在哪個 allele、有幾份」都有真值。這可以當 HP1／HP2 phasing 的真值。〔推論〕
- bulk 部分沒有 binomial／read count 輸出。read count 只在 `generatesinglecells`（single-cell、稀疏）裡產生。〔程式〕README、`src/singlecellgeneration.cpp`
- segment 是抽象 index，不是真實座標。〔推論〕
- 用途：直接接 Pharming。要給 PhyClone，需要自己用 `proportions.tsv` 與 `node.tsv` 算 VAF 再抽 binomial read count。〔推論〕

### 2. MASCoTE（HATCHet 論文的模擬框架）

- Repo：https://github.com/raphael-group/mascote ，commit `dd93162`（2020-12-03），授權 NOASSERTION（Princeton copyright）。Python 2.7。〔程式〕
- README：模擬二倍體人類基因體（兩條 haplotype 上放 germline SNP），產生系統樹，在每條邊上放 CNA 與 WGD，再從每個 clone 的基因體模擬 read，最後依 clone 比例混合 BAM。〔論文〕README
- 輸出：每個 clone 的 `cloneX_maternal.fa`、`cloneX_paternal.fa`，`copynumbers.csv`（每個 clone 每段 `A|B`），`tumor.dot`（樹與事件）。〔程式〕`doc/doc_mascote.md`
- CN 事件都是 haplotype-specific：arm、整條染色體 loss、focal 擴增／刪除、clonal 與 subclonal WGD。〔程式〕`doc/doc_mascote.md`、`src/Mutation.py`
- `MixBAMs` 用 `U:U_0:...:U_N` 指定每個樣本的 normal 比例與 clone 比例，所以 purity<1 與多樣本都支援。〔程式〕`doc/doc_mixbams.md`
- read 用 ART（`art_illumina`）產生，再用 BWA 比對。〔程式〕README
- **沒有 somatic SNV。** `src/` 中找不到 SNV 或 somatic 相關程式。〔程式〕
- `-s/--rndseed` 可重現 genome 與樹。ART 的隨機性要另外設定。〔程式〕〔推論〕
- 真實座標：用使用者給的 reference 與 dbSNP 位置。〔程式〕
- 對我們的意義：這是唯一在 read 層級帶 haplotype 的生成器。若在 haplotype FASTA 上插入 somatic SNV，並把 ART 換成 ONT read 模擬器，就能得到帶 HP 的長讀資料。這需要自己寫。〔推論〕
- 相關：`raphael-group/hatchet2-simulations`（BSD-3，commit `48c7dd6`，2024-04-02）是 Snakemake 流程，讀 MASCoTE 的 `copynumbers.csv` 再改 CN。它也沒有 SNV。〔程式〕README

### 3. mutsim（Orchard）

- Orchard README 寫「Install libraries for simulating mutation trees (optional)」，指向 `git clone https://github.com/ethanumn/mutsim.git`。〔程式〕`morrislab/orchard` README L103–106，commit `5d19f32`
- mutsim README：「Fork of morrislab/pearsim」。commit `9d9ea41`（2024-05-04），沒有授權檔。〔程式〕
- 比 pearsim 多 `--tree-type monoprimary/polyprimary`；參數網格 K 到 300、S 到 100。〔程式〕`make_simulated_data.py` L57、`make_simulated_data.sh`
- 有 CNA：`-C` CN event 數、`-H` segment 數。每個 SNV 有 `ssm_phases` 與 `ssm_timing`；CNA 也有 phase。程式用這些算「SNV 是否受 CNA 影響」。〔程式〕`simulator.py` L224–255
- 種子 bug 與 pearsim 相同：產生 `seed` 但呼叫 `np.random.seed(args.seed)`。〔程式〕`make_simulated_data.py` L79–83
- 沒有 normal 汙染參數。〔推論〕

### 4. PhylEx simulator

- Repo：https://github.com/junseonghwan/PhylEx ，commit `83f4654`（2023-11-26），沒有授權檔。C++（GSL）。〔程式〕
- `simulation/` 是獨立 CMake 專案。設定有 `seed`、`n_regions`、`bulk_mean_depth`、`seq_err`、`n_cells`、`dropout_rate` 等。〔程式〕`simulation/simul_config.hpp`
- CN 沿樹演化：每個 node 有 `(ref_cn, var_cn)`，SNV 發生時從 ref copy 中抽 `var_cn`，之後再 birth-death。〔程式〕`simulation/simul_data.cpp` L211–259
- 輸出：`simul_ssm.txt`、`genotype_ssm.txt`、`cts_cn_profile.txt`、`cluster_labels.txt`，以及 single-cell 資料。〔程式〕`simulation/main.cpp` L229–277
- single-cell 是 scRNA 每細胞每 SNV 的 read count，不是同一條 read 上的 SNV 共現。〔程式〕〔推論〕
- 沒找到明確的 purity 參數。〔程式〕
- 這裡的 CN 是「每個 SNV 位點的 ref／var copy」，不是 segment 層級的 allele-specific CN。〔推論〕

### 5. PhylogicSim（PhylogicNDT）

- Repo：https://github.com/broadinstitute/PhylogicNDT ，commit `e47fb07`（2025-04-17），授權 NOASSERTION。Python 2。CLI：`PhylogicNDT.py PhylogicSim`。〔程式〕
- 參數：`-p` purity、`-a` artifact 比例、`-nm` SNV 數、`-ns` 樣本數、`-nodes` 節點數、`-cov` 深度分布檔、`-seg` CN 檔。〔程式〕`PhylogicNDT.py` L331–367
- 從 seg 檔抽 contig 與位置，取該段的 total CN 與 allele CN，再抽 multiplicity。所以座標可以是真實座標。〔程式〕`SimEngine.py` L283–330
- CN 是每段固定的 clonal 值，不在樹的邊上變動。〔推論〕
- read count 用 beta-binomial。〔程式〕`SimEngine.py` L177
- 樹的邊只寫進 `*.simulation_paramters.tsv` 的 `edges` 一行（Python list 字串）。〔程式〕`SimEngine.py` L700–737
- 種子：函式有 `seed=157` 參數，但檔案內沒有呼叫 `np.random.seed` 或 `random.seed`。不能重現。〔程式〕

### 6. MACHINA `simulate`（另有 OncoLib 版本）

- Repo：https://github.com/raphael-group/machina ，commit `ac71282`（2021-03-05），BSD-3。`simulate` 在 CMake 中是 `EXCLUDE_FROM_ALL`，要單獨 build。〔程式〕`CMakeLists.txt` L547
- agent-based 腫瘤生長與轉移。參數：`-C` coverage、`-P` purity、`-E` 定序錯誤、`-s` 種子（`std::mt19937`）。〔程式〕`src/simulation/simulationmain.cpp`
- 輸出 `T_seed*.tree`、`*.labeling`、`G_seed*.tree`、`reads_seed*.tsv`。depth 用 Poisson，variant read 用 binomial。〔程式〕`simulation.cpp` L127–218
- 沒有 CN。〔程式〕（`copy number` 0 筆）
- `data/sims/` 也附 PASTRI 格式輸入（`reads_seed*.pastri`）。〔程式〕
- `elkebir-group/OncoLib`（BSD-3，commit `1707709`，2019-10-20）有相同的 `simulate`，另外有 `mix`、`sequence`、`downsample`。〔程式〕

### 7. CALDER branchsim

- `raphael-group/calder`，commit `41d6c83`（2023-07-11），BSD-3。`branching-sim/branchsim.py` 加上 `Branching simulation data.zip`。〔程式〕
- 族群模擬加 driver，多時間點取樣，`np.random.binomial(depth, freq)` 產生 read。`random.seed` 與 `np.random.seed` 都有設。〔程式〕L54–55、L302
- 沒有 CN、沒有 purity。沒有 CLI，入口是 `run_sim_exome(seed)` 這類函式。〔程式〕

### 8. fastBE `simulation.py`

- `raphael-group/fastBE`，commit `c4613f0`（2026-02-18），沒有授權檔。〔程式〕
- CLI：`--mutations --clones --samples --coverage --seed --output`；`np.random.seed(args.seed)`。〔程式〕L199–210
- 輸出 `sim_tree.txt`、`sim_usage_matrix.txt`、`sim_variant_matrix.txt`、`sim_total_matrix.txt` 等。〔程式〕`examples/`
- `scripts/processing/` 有轉成 Pairtree、CALDER、CITUP、PyClone-VI 輸入的腳本。〔程式〕
- 沒有 CN、沒有 purity。〔程式〕

### 9. ClonEvol `simulations/sim.r`

- `hdng/clonevol`，commit `7aff737`（2018-11-17），GPL-3.0。〔程式〕
- 參數：truth 檔、depth、樹數、replicate、error rate、`cn.rate`、`rand.seed`。`set.seed(rand.seed)`。〔程式〕L3、L316
- read 由隨機抽樣產生。`cn.rate` 只是讓一部分 variant 的 VAF 偏移，沒有 CN 模型。〔程式〕L38–39

### 10. AncesTree `makeSimData.py`

- `raphael-group/AncesTree`，commit `df376c6`（2018-04-01）。〔程式〕
- 有 `-m -n -c -s` 與種子（預設 47）。但只呼叫 `random.seed`；read count 用 `np.random.binomial`，沒設種子。〔程式〕L120、L375
- import 的 `convertData` 不在 repo 內。現況無法直接跑。〔程式〕

### 11. CITUP `generatingInput`

- `sfu-compbio/citup`，commit `deadbdf`（2015-05-08），沒有授權檔。〔程式〕
- 輸出 frequency 並加 Gaussian noise，不產生 read count。種子預設 `time(0)`。〔程式〕`generatingInput.cpp` L31、`generatingFrequencies.cpp` L219

### 12. PICTograph `R/simulation.R`

- `KarchinLab/pictograph`，commit `3463726`（2025-10-25），沒有授權檔。〔程式〕
- 有整數 CN（`icn`）、multiplicity（`m`）、SNV 與 CNA 重疊；read 用 `rbinom`。〔程式〕L16–76
- 檔案中沒有樹或邊的生成（`tree|edge` 0 筆）。只給 cluster 的 MCF。〔程式〕
- `simulation_type*_jags` 忽略 `seed` 參數，寫死 `set.seed(12345)` 或 `set.seed(123)`。〔程式〕L2、L128

### 13. TUSV `sim/sim.py`

- `jaebird123/tusv`，commit `ed6abf1`（2018-03-14），MIT。〔程式〕
- 只模擬 SV 與 CN（`amp`、`rem`、`inv`），沒有 SNV，沒有種子參數。〔程式〕L64、L717–722
- `CMUSchwartzLab/TUSV-ext`（MIT）附了含 SNV 的模擬資料（`B_SNV.tsv`、`T.dot`），但 repo 中沒有生成程式。〔程式〕

### 其他：SPRUCE `randomtree`

- `raphael-group/spruce`，commit `e5ffc88`（2018-06-06）。`randomtree` 依 `maxXY`、`maxCopyEvents` 抽 CN state tree 與 clone tree，輸出到 stdout。〔程式〕`src/randomtree.cpp`
- `data/sims/` 的 `.data` 是怎麼由樹轉成 read count，未確認。〔未查證〕

## 沒找到生成程式的工具

| 工具 | 狀況 |
|---|---|
| PhyloWGS | `morrislab/phylowgs` 只有 `phylowgs_sims/*.ssm.txt` 資料，沒有生成程式。〔程式〕 |
| CNT-MD | `data/sim/` 只有資料；`utils/make_input.py` 只是轉檔。〔程式〕 |
| DeCiFer | `decifer/src/decifer/generator.py` 是 beta-binomial 擬合，不是模擬器。`decifer-data` README 寫「Simulated data will be available soon...」。〔程式〕 |
| PhyDOSE | `data/simulations/*.tar.gz` 只有資料。〔程式〕 |
| Canopy | 只有 `canopy.simrun.diagnostic.R`（診斷用），沒找到生成器。〔程式〕 |
| LICHeE、TreeOmics（`reiterlab/treeomics`）、SCHISM、PASTRI | repo 中沒有模擬相關檔案。PASTRI 用 MACHINA 的模擬資料。〔程式〕 |
| BitPhylogeny | 原 repo `KeYuan/BitPhylogeny` 回 404；`keyuan/bitphyloR` 與 `kritdass/bitphylogeny` 沒有模擬檔。〔程式〕 |
| CloneFinder | `gstecher/CloneFinderAPI` 沒有生成器。〔程式〕 |
| Sapling、Cloe、CONETT | 沒找到對應 repo，或沒有模擬檔。〔未查證〕 |
| TreeMHN | 模擬 mutation tree 與 single-cell 資料，不在 bulk read count 範圍內。〔推論〕 |

## 搜尋範圍

- 日期：2026-10-24。
- 方法：`gh api repos/...` 取授權與 push 日期；`gh api .../git/trees` 列出檔名含 `sim|generat|synth` 的檔案；必要時 shallow clone 到 scratchpad 只讀程式。
- 列過的組織：`raphael-group`、`elkebir-group` 全部 repo。
- 讀過程式的 repo：machina、OncoLib、PhylogicNDT、PhylEx、calder、pictograph、decifer、AncesTree、citup、clonevol、tusv、TUSV-ext、orchard、mutsim、spruce、clonesim、mascote、hatchet2-simulations、fastBE。
- 只看檔名的 repo：phylowgs、Canopy、lichee、SCHISM、treeomics、CNT-MD、TreeMHN、PhyDOSE、CloneFinderAPI、PASTRI、bitphyloR、CONETT、SVclone、UniPPM、PBDRJB、meltos。
- 沒做：沒有執行任何生成器；沒有讀論文 PDF 核對模擬設定。
