# 「CancerSim」同名工具調查

調查日期：2026-10-24。目標：釐清「CancerSim」指哪個工具，並判斷它能不能同時產生真值 clone tree 與模擬 SNV 定序資料。這份補 02 組因 GitHub rate limit 沒查完的項目。

證據標記：〔論文〕論文或 README 的描述；〔程式〕讀過原始碼（shallow clone，只讀，沒有執行）；〔推論〕分析推論，沒有實測。程式 clone 在 `/tmp/claude-1024/-bip8-disk-boyu114-main-work/18fc1cc2-ffb5-4afb-8a48-a15890b40de5/scratchpad/clones2/`（暫存，會消失）。

## 結論

- **「CancerSim」這個名字沒有對應到符合需求的工具。** 同名的工具不是沒有基因體資料，就是只輸出 VAF，而且沒有 CN。〔程式〕
- **最常被引用的「CancerSim」是 MPI 的 `mpievolbio-scicomp/cancer_sim`**（JOSS 2020）。它是 2D 空間腫瘤生長模型。它輸出 mutation genealogy（pickle）與加上 binomial 雜訊的 VAF。它沒有 CN，沒有 normal 細胞，也沒有 read。它只適合當教學或 VAF 層的 baseline。〔程式〕
- **名字相近、而且真正有用的是 cancerSimCraft**（`haijingjin/cancerSimCraft`）。它有 clone tree、maternal／paternal CN 事件放在樹邊上、SNV 指定 haplotype、phased germline SNP、每個 clone × haplotype 的 FASTA，再用 ART 產生 short read。它的定位是 single-cell，但 bulk read 函式也有。缺點：沒有 seed、只接 ART、沒有正式期刊論文。〔程式〕
- **本次新發現、前 6 份報告沒收錄的兩個近似工具：**
  - `cbg-ethz/WES_Cancer_Sim`（Hofmann 2017）：二元 subclone tree、真實 SNV 放到樹上、CNV 隨機放到樹節點並指定 zygosity、Wessim 產生 WES BAM、加 normal 稀釋。這是一次性的 benchmark 管線，不是通用工具。〔程式〕
  - GeRnika（CRAN）：clone tree（`B` 矩陣）＋多 sample 的真值與雜訊 VAF。沒有 CN，沒有 purity。〔論文：CRAN manual〕
- **建議：** 不要用 MPI CancerSim。要 haplotype-resolved FASTA 時，cancerSimCraft 可和 PSiTE 並列當參考，把 ART 換成 Badread／PBSIM3。〔推論，未實測〕

| 候選 | repo | 真值樹 | 資料層 | CN | purity<1 | haplotype | 符合需求？ |
|---|---|---|---|---|---|---|---|
| CancerSim（MPI，Opasic 2020） | `mpievolbio-scicomp/cancer_sim` | mutation genealogy（`mut_container.p`） | VAF（Poisson depth＋binomial） | 無（ploidy 固定 2） | 否 | 否 | 否：無 CN，無 count |
| CancerSim（Abbott／Forrest／Pienta 2006） | 沒找到公開 repo | 無 | 無基因體資料 | 無 | 無 | 無 | 否：hallmark agent-based 模型 |
| SchriderLab/CancerSim | `SchriderLab/CancerSim` | 無 | 無（SLiM 族群模擬） | 無 | 無 | 無 | 否 |
| cancerSimCraft | `haijingjin/cancerSimCraft` | 是（clone tree，igraph） | haplotype FASTA → FASTQ（ART） | allele-specific，事件在樹邊 | 未見明確參數 | 是：SNV 有 `haplotype` 欄 | 部分：short read、無 seed |
| WES_Cancer_Sim（近似名） | `cbg-ethz/WES_Cancer_Sim` | 是（寫死的二元 tree） | WES BAM（Wessim） | 有 zygosity 的 gain／loss | 是 | 部分（het CNV 指定 copy） | 部分：一次性管線 |
| GeRnika（近似用途） | CRAN `GeRnika`（`cran/GeRnika` mirror） | 是（`B` 矩陣） | VAF | 無 | 未提到 | 否 | 否：無 CN |
| r-forge `cancersim` | `r-forge/cancersim`（空 mirror） | 未知 | 未知 | 未知 | 未知 | 未知 | 無法判斷 |

## 1. CancerSim（MPI Evolutionary Biology，`cancer_sim`）

- Repo：`https://github.com/mpievolbio-scicomp/cancer_sim`。MIT。最後 commit `d46fa78`，2020-09-24。版本 v2.0.1。未封存。〔程式〕
- 論文：Opasic L, Scott JG, Traulsen A, Fortmann-Grote C. "CancerSim: A Cancer Simulation Package for Python 3." JOSS 2020。DOI `10.21105/joss.02436`（README badge 與 JOSS PDF 一致）。〔論文〕
- 生成器：`casim/casim.py`（1205 行）。CLI：`python casim/casim.py -p params.py -s SEED -o OUTDIR`（argparse，`-p`／`-s`／`-o`）。〔程式〕
- 模型：2D 格點上的細胞分裂與死亡。每次分裂產生新的 mutation event。可在第 N 代放一個 advantageous mutation。可選「single」或「double」腫瘤。〔程式〕
- 真值樹：`mut_container.p` 是 `(parent_mutation_id, mutation_id)` 的 list（`casim.py:1026`、`1047`）。這是 mutation event 的 genealogy，可轉成樹。docstring（`casim.py:525`）說第一個元素是「cell number」，但程式實際存的是 parent mutation id。〔程式〕
- 每個 mutation event 之後依 Poisson 倍數展開成多個 SNV（`increase_mut_number`，`casim.py:761`）。展開後的 SNV 共用同一個 event，所以真值是 event 層的 clone，不是個別 SNV。〔程式〕
- 資料層：`sample_out_XXX_YYY.txt` 與 `mtx_VAF.txt`，欄位是 `mutation_id`、`additional_mut_id`、`frequency`。〔程式〕
- 雜訊：depth ~ Poisson(`read_depth`)，alt ~ Binomial(depth, AF)，只寫出 VAF（`simulate_seq_depth`，`casim.py:743`）。VAF=0 的 SNV 被刪掉。depth 與 alt count 沒有寫檔。〔程式〕
- CN：`__ploidy=2` 固定（`casim.py:338`）。頻率除以 ploidy 得到 VAF（`casim.py:737`）。沒有 CN 事件。〔程式〕
- purity：頻率以「所有 cancer cell 都有的 mutation 1」當分母（`casim.py:736`）。沒有 normal 細胞。所以 purity 等於 1。〔推論〕
- multi-sample：`sampling_positions` 可給多個座標，每個座標輸出一個 sample。〔程式〕
- seed：`-s` 同時設 `random` 與 `numpy.random`（`casim.py:537-538`）。輸出目錄以 seed 命名。〔程式〕
- haplotype、read、long read：全部沒有。〔程式〕

## 2. CancerSim（Abbott、Forrest、Pienta，hallmarks of cancer）

- 論文：Abbott RG, Forrest S, Pienta KJ. "Simulating the Hallmarks of Cancer." Artificial Life 2006。前身是 Abbott 2002 碩士論文「CancerSim」。〔論文：Forrest 個人頁與 UNM PDF；DOI 未核對〕
- 模型：agent-based，模擬 Hanahan–Weinberg hallmark 的出現順序。沒有基因體序列，沒有 SNV 資料。〔論文〕
- 後續：ASU 有「CancerSim2」3D agent-based 專案頁（2024）。沒找到公開 repo。〔論文：專案頁〕
- 與需求無關。〔推論〕

## 3. SchriderLab/CancerSim

- Repo：`https://github.com/SchriderLab/CancerSim`。沒有 license。最後 commit `51464c7`，2021-05-04。README 只有標題。〔程式〕
- 內容：一個 SLiM nonWF 腳本（`NonWFCancer4.slim`，82 行）與參數掃描腳本。輸出 `sim.outputFixedMutations()`，以及 R 畫圖。〔程式〕
- 沒有 clone tree 真值，沒有 VAF／read，沒有 CN。沒有找到論文。〔程式〕

## 4. cancerSimCraft（名稱近似）

- Repo：`https://github.com/haijingjin/cancerSimCraft`。R 套件 v0.2.0。DESCRIPTION 寫 `MIT + file LICENSE`；GitHub API 判為 NOASSERTION。最後 commit `dd11441`，2025-03-05（API `pushed_at` 2025-03-07）。〔程式〕
- 論文：Jin H, Navin N, Chen K. bioRxiv `10.1101/2024.12.11.627708`（2024-12）。沒找到期刊版。〔論文：README＋bioRxiv 頁〕
- 本調查 04 組只記 repo 描述；05 組寫「沒找到 repo」。這裡補程式細節。〔程式〕
- 真值樹：clone tree 是 igraph 物件。可自訂，或用 `generate_random_tree`（`R/tree_relevant_functions.R:3`）。也有 single-cell 層的 lineage（`get_sc_ancestors`）。〔程式〕
- CN：事件表有 `haplotype`（maternal／paternal）、`parent`、`child`、`CN_change`、`copy_index`（`create_event`，`R/event_relevant_functions.R:111`）。CN 事件放在樹邊上，而且 allele-specific。也支援 WGD。〔程式〕
- SNV：`sim_clonal_mutation_pos`（`R/snv_relevant_functions.R:772`）在每條邊上放 SNV，並隨機選一個 haplotype，寫入 `haplotype` 欄。這等於 SNV 所在 haplotype 的真值。〔程式〕
- germline：`insert_snps_to_genome`（`R/snp_relevant_functions.R:182`）把 phased VCF 的 `1|0`、`0|1` SNP 插入 maternal／paternal 基因體。所以 read 上 germline SNP 與 somatic SNV 的共現有真實結構。〔程式〕
- read：`simulate_read_bulk`（`R/read_sim.R:2`）對每個 FASTA 呼叫 `art_illumina`。只有 short read。`merge_fasta_files`（`R/read_sim.R:134`）會把 paternal 與 maternal FASTA 合併，合併後 read 名稱不帶 haplotype。若不合併、逐 haplotype 跑，就能從檔名追 clone 與 haplotype。〔程式〕〔推論〕
- purity、multi-sample：沒看到明確的 normal 稀釋或多 sample 參數。可以自己依 clone 比例調 depth 來混。〔推論〕
- seed：套件函式沒有 seed 參數。ART 呼叫沒有傳 `-rs`，所以 read 層不可重現。〔程式〕〔推論：ART 預設用時間當 seed〕
- 不是 CLI，要在 R 裡組流程。〔程式〕

## 5. WES_Cancer_Sim（cbg-ethz，名稱近似，本次新收錄）

- Repo：`https://github.com/cbg-ethz/WES_Cancer_Sim`。Apache-2.0。最後 commit `563d211`，2017-10-03。〔程式〕
- 論文：Hofmann AL, Behr J, Singer J, Kuipers J, Beisel C, Schraml P, Moch H, Beerenwinkel N. BMC Bioinformatics 2017;18:8。DOI `10.1186/s12859-016-1417-7`（PMC5209852）。〔論文〕
- 流程：從真實腎腫瘤與 normal BAM 用 freebayes 找變異，再放到寫死的二元 subclone tree 上（`create_cancer_vcfs.py`），每個 clone 建一份 reference（`create_ref_from_vcf.cpp`），再用 Wessim 產生 exome read 並比對（`run_wessim_all.sh`）。〔程式〕
- CN：`distribute_cnvs_on_tree.py` 把 Control-FREEC 呼叫的 CNV 隨機放到 tree 的某一層、某個節點，並隨機決定 het／hom 與哪一個 copy。子節點繼承。`random.seed(44)` 寫死。〔程式〕
- purity：`process_true_alignments.sh:113` 註明「simulate normal contamination」，以不同百分比合併 normal BAM。〔程式〕
- 限制：路徑與節點名寫死（例如 `nodeInTree=10_0_TU`）。只有 short read WES。沒有 per-read clone tag。這是重現論文用的管線。〔程式〕〔推論〕

## 6. GeRnika（CRAN，用途近似，本次新收錄）

- CRAN 套件 v1.2.0，GPL (>=3)。作者 Sánchez-Ferrera、Tellaetxe-Abete、Calvo。原始碼 mirror：`https://github.com/cran/GeRnika`。〔論文：CRAN manual〕
- `create_instance(n, m, k, selection, noisy, depth, seed)` 回傳 `B`（tree 的 topology 矩陣）、`U`（各 sample 的 clone 比例）、`F_true`、雜訊 `F`。〔論文：CRAN manual〕
- 雜訊：depth 用 negative binomial，alt 與 mismatch 用 binomial。只輸出 VAF 矩陣，不輸出 count。〔論文：CRAN manual〕
- 有 multi-sample 與 `seed`。沒有 CN，沒有 purity。程式沒有 clone 細讀。〔論文〕〔未驗證：未讀原始碼〕

## 7. 其他同名但無關的 repo

- `r-forge/cancersim`：GitHub mirror 是空的（size 0）。R-Forge 專案頁回 HTTP 503。無法判斷內容。〔程式〕
- 以下 repo 只依 GitHub 描述判斷，都是教學、細胞層或族群動態模擬，沒有基因體資料：`alexalemi/cancersim`（2014）、`sterlesser/cancersim`（2014）、`taylormjs/CancerSim`（2017）、`pumaman/cancersim2`（BioDynaMo，2020）、`verne91/cancerSimulator`（2017）、`hackersforpeace/cancersimulator`、`mesako/CancerSimulationR`、`ocbe-uio/Cancer_simulator`。〔程式：repo 描述，未讀碼〕
- `rhea-mal/cancersimulator_extensions`、`rhea-mal/cancersimulator_copynumber`：拿某個「cancer simulator」的 CN 輸出和 PCAWG 比對的分析筆記本。repo 內沒有生成器，也沒寫明是哪個 simulator。〔程式〕
- `marcjwilliams1/CancerSeqSim.jl`：已在 [04](04_evolutionary_simulators.md) 收錄，這裡不重做。
- 「CanSim」：GitHub 搜尋結果全是 Statistics Canada 資料包裝或 CAN bus 模擬器，與腫瘤無關。〔程式：repo 描述〕
- 沒有找到「Lucas Laboratory CancerSim」或 `mrc-ide` 名下的 cancer simulator（`gh search repos cancer --owner mrc-ide` 無結果）。〔未驗證〕

## 搜尋範圍（2026-10-24）

- `gh search repos`：`cancersim`、`"cancer simulator"`、`cansim`、`cancer-sim`、`cancer_sim`、`cancer --owner mrc-ide`。組合查詢 `cancersim OR cancer-sim OR cansim` 回空結果。
- `gh api repos/...`：`mpievolbio-scicomp/cancer_sim`、`haijingjin/cancerSimCraft`、`SchriderLab/CancerSim`、`r-forge/cancersim`、`cbg-ethz/WES_Cancer_Sim`、`marcjwilliams1/CancerSeqSim.jl`。
- Shallow clone 並讀碼：`cancer_sim`、`SchriderLab/CancerSim`、`cancerSimCraft`、`r-forge/cancersim`、`rhea-mal/cancersimulator_extensions`、`WES_Cancer_Sim`、`CancerSeqSim.jl`（只確認已收錄）。
- WebSearch：「CancerSim tumor simulator github」、「CancerSim Abbott Forrest Pienta hallmarks」、「cancerSimCraft Jin Navin Chen published journal」、「CanSim／CancerSimulator／cancer_sim tumour phylogeny VAF」、Hofmann 2017 論文 DOI。
- WebFetch：GeRnika CRAN manual；R-Forge `cancersim` 專案頁（HTTP 503）。
- 沒有執行任何生成器。
