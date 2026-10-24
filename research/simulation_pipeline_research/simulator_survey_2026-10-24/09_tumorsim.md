# TumorSim／tumor-sim／TumourSim 同名工具調查

調查日期：2026-10-24。目的：補完 02 組因 GitHub rate limit 沒查完的「TumorSim」。需求是同時產生真值 clone tree 與模擬 SNV 定序資料（count、VAF、read）的公開程式。

證據標記：〔論文〕論文或 README 的描述；〔程式〕讀過原始碼（只讀，沒有執行或編譯）；〔推論〕分析推論，沒有實測。程式 clone 在 `/tmp/claude-1024/-bip8-disk-boyu114-main-work/18fc1cc2-ffb5-4afb-8a48-a15890b40de5/scratchpad/clones2/`（暫存，會消失）。

## 結論

- **沒有一個叫 TumorSim 的工具符合需求。** 沒有任何同名工具同時輸出真值 clone tree 與 SNV read count／VAF／read。〔程式〕
- **沒有找到「TumorSim」這個名字的定序 read 模擬器論文。** 學術上正式叫 TumorSim 的是 MRI 腦腫瘤影像模擬器（Prastawa 2009）。〔論文〕
- 最接近的是 Waclaw 2015 的 **TumourSimulator**。它輸出 genotype 親子表（等於 clone tree）與每個突變的真實 cell 比例，有 seed。但它沒有 read count、沒有 CN、沒有 purity。要自己加 binomial 抽樣。〔程式〕
- 順帶發現：`hcoggan/Agent-based-simulations-of-lung-tumour-evolution` 有 clone 親子表加 binomial alt read。它不是 TumorSim 同名工具，只讀了一部分。〔程式〕
- 對我們：這個方向可以結案。不需要加入建議路線。〔推論〕

| 候選 | repo | 類型 | 真值樹 | SNV 資料 | 符合需求？ |
|---|---|---|---|---|---|
| NCBI-Hackathons Tumor_sim | `NCBI-Hackathons/Tumor_sim` | 單一腫瘤基因體 FASTA（SV 為主） | 否 | 只有 FASTA＋BED，無 read | 否 |
| TumorSim.jl（Fontaneda & Diaz-Uriarte） | `TumorSim/TumorSim` | 空間 agent-based、adaptive therapy | 每個細胞有 `phylogeny` 突變順序 | 無（只有少數 gene 的 genotype 計數） | 否 |
| bmannakee/tumorsim | `bmannakee/tumorsim` | 未完成的 Rcpp 骨架 | 否 | 否 | 否 |
| TumourSimulator（Waclaw 2015） | Edinburgh ZIP（已 404）；GitHub 鏡像 `Durwella/TumourSimulator` v1.2.2 | 3D 空間 agent-based | 是（genotype 親子表） | 只有真實突變 cell 比例，無 read | 部分（缺 read、CN、purity） |
| st-cnv-simulator（`SpatialCNV_TumorSimulator`） | `jintong-shi/SpatialCNV_TumorSimulator` | spatial transcriptomics＋allele-specific CNV | 細胞 lineage | 無 somatic SNV；只有 germline SNP 的 AD/DP | 否 |
| TumorSim（MRI，Prastawa 2009） | NITRC `projects/tumorsim` | 腦腫瘤 MR 影像 | 無關 | 無關 | 排除 |
| 其他同名小 repo | 見「搜尋範圍」 | 生長模擬、課堂作業、醫學影像 | 否 | 否 | 否 |
| （順帶）hcoggan lung ABM | `hcoggan/Agent-based-simulations-of-lung-tumour-evolution` | 3D deme ABM | 是（`subclone_parentage`） | binomial alt read（depth 160） | 部分（無 CN，purity 未核對） |

## 各候選

### NCBI-Hackathons／Tumor_sim

- repo：<https://github.com/NCBI-Hackathons/Tumor_sim>，commit `10d0f1f`（2017-12-15），MIT。沒有論文；README 說是 2017 NYGC-NCBI Hackathon 產物。〔程式〕
- 入口是 `lib/simulate_endToEnd.py`。它先加 germline SNV 與 indel，產生 normal FASTA；再加 SV（deletion、translocation、duplication、inversion、insertion），產生一個 tumor FASTA 與 BED。〔程式〕`lib/simulate_endToEnd.py` L69–95；`lib/mutation_orchestrator.py`
- 只有一個 tumor 基因體。沒有 clone、沒有 tree、沒有 purity、沒有 read。〔程式〕
- 用 `np.random` 但沒有設 seed 的參數。〔程式〕`lib/mutation_orchestrator.py` L29、L39
- 對我們：不符合。最多當 SV FASTA 產生器。〔推論〕

### TumorSim.jl（Fontaneda & Diaz-Uriarte）

- repo：<https://github.com/TumorSim/TumorSim>（README 舊網址 `YM162/TumorSim`），commit `4663270`（2023-05-24），GPL-3.0。〔程式〕
- 論文：Fontaneda & Diaz-Uriarte, bioRxiv 2023.05.18.541330, doi:10.1101/2023.05.18.541330（取自 README，沒有開論文頁核對）。〔論文〕
- Julia 空間 agent-based 模型。使用者給 fitness landscape（genotype bit 向量 → mitosis 機率）與治療設定。〔程式〕README；`src/Fitness/Fitness.jl`
- 每個細胞記 `genotype::BitArray` 與 `phylogeny::Array{Int}`（突變 gene 的順序）。〔程式〕`src/TumorModel/TumorModel.jl` L18–19、L147
- seed：`model_init(;seed=...)` 用 `MersenneTwister(seed)`。〔程式〕`src/TumorModel/TumorModel.jl` L24、L46
- 沒有 SNV 位置、沒有 read、沒有 CN、沒有 purity。突變只是少數 driver gene 的 0/1。〔程式〕grep `read`、`vaf` 無結果
- 對我們：不符合。它是治療策略模擬器。〔推論〕

### bmannakee／tumorsim

- repo：<https://github.com/bmannakee/tumorsim>，commit `aa39756`（2018-07-11），沒有 license（`DESCRIPTION` 仍是範本文字）。〔程式〕
- 只有 RStudio 範本 `hello.R` 與兩個 C++ 骨架（`src/cell-class.cpp` 91 行、`src/tree-class.cpp` 48 行），內有 TODO。〔程式〕
- 對我們：未完成，不能用。〔推論〕

### TumourSimulator（Waclaw et al. 2015）

- 論文：Waclaw et al. 2015, *Nature* 525:261–264, doi:10.1038/nature14971（README 與官方頁都引用）。〔論文〕
- 官方頁 <https://www2.ph.ed.ac.uk/~bwaclaw/cancer-code/> 現在回 404（2026-10-24 測試）。Wayback 快照 2022-01-24 有頁面，但 `version_1.2.3.zip` 沒有被存檔（下載回 HTML）。所以 v1.2.3 沒有讀到。〔程式〕
- 改讀 GitHub 鏡像 <https://github.com/Durwella/TumourSimulator>，commit `0c56cf2`（2015-09-29），GPL-3.0，README 標 v1.2.2。不是官方 repo。〔程式〕
- 執行：`cancer.exe [name] [number of samples] [seed]`；`_srand48(RAND)`，所以 seed 可重現。參數寫死在 `params.h`，要重新編譯才能改。〔程式〕`main.cpp` L191–198；官方頁快照
- 真值輸出：
  - `genotypes_<size>.dat`：每個 genotype 一列，含 `prev_gen`（親代 genotype）、driver 數、細胞數。這就是 clone tree。〔程式〕`main.cpp` L146–150、L265
  - `all_PMs_<seed>_<sample>.dat`：每個 passenger mutation 的真實 cell 比例（`n[i]/total`）。〔程式〕`functions.cpp` L36–55；`main.cpp` L248
  - `cells_<size>.dat`：細胞 3D 位置。〔程式〕`main.cpp` L264
- 沒有 read count、沒有 VAF 抽樣、沒有 CN、沒有 normal 細胞（purity=1）、突變沒有基因體座標。〔程式〕grep `binom`、`depth` 無結果
- multi-sample：`[number of samples]` 是獨立重跑，不是同一腫瘤的多區 biopsy。〔程式〕`main.cpp` L203
- 對我們：可當空間 clone tree 產生器。要自己加 diploid VAF、binomial read、CN、purity。SITH（04 組）已在 R 做了類似的 Waclaw 模型加 `rbinom`，比這個好用。〔推論〕

### st-cnv-simulator（repo 名 SpatialCNV_TumorSimulator）

- repo：<https://github.com/jintong-shi/SpatialCNV_TumorSimulator>，commit `0b92e2e`（2026-07-29），MIT；`CITATION.cff` 指向 `jintongshi/st-cnv-simulator` v0.1.0。沒有論文。〔程式〕
- 2-D lattice ABM，每次分裂可從 CNV catalogue 抽 allele-specific CNV。輸出 single-cell 表達、Visium spot、germline SNP 的 AD/DP（可給 Numbat）、`lineage.tsv`。〔程式〕README；`src/st_cnv_simulator/pipeline.py` L135、L294–312、L332–343
- 有 `--seed`，README 說 byte-identical。〔論文〕README「Reproducibility」
- 沒有 somatic SNV（grep `somatic`、`snv` 無結果）。資料是 RNA，不是 DNA 定序。〔程式〕
- 對我們：不符合。〔推論〕

### TumorSim（MRI，排除）

- Prastawa, Bullitt & Gerig 2009, *Medical Image Analysis* 13(2):297–311。NITRC <https://www.nitrc.org/projects/tumorsim/>，RRID:SCR_002604。〔論文〕
- 它模擬腦腫瘤 MR 影像，不是基因體。排除。〔推論〕

### 順帶發現：hcoggan lung ABM（不是 TumorSim 同名）

- repo：<https://github.com/hcoggan/Agent-based-simulations-of-lung-tumour-evolution>，commit `ab499ac`（2026-06-17），MIT。論文 README 說「upcoming」，沒有 DOI。〔程式〕
- `construct_tree` 用 `subclone_parentage` 建 clone tree。`sequence()` 對每個突變做 `np.random.binomial(read_depth, prev*(1-error))`，預設 depth 160。〔程式〕`model_1.py` L429、L517–523
- 沒有 CN。`prev` 是否已除以 2（diploid VAF）、有沒有 normal 汙染、seed 是否固定，都沒有核對。〔未驗證〕
- 對我們：功能和 SITH 類似，不是優先。〔推論〕

## 搜尋範圍（2026-10-24）

- GitHub `gh search repos`：`tumorsim`、`tumor-sim`、`tumoursim`、`TumorSimulator`、`tumour-sim`。前 10–15 筆都看過描述。〔程式〕
  - clone 並讀程式：`NCBI-Hackathons/Tumor_sim`、`TumorSim/TumorSim`、`bmannakee/tumorsim`、`Durwella/TumourSimulator`、`jintong-shi/SpatialCNV_TumorSimulator`、`hcoggan/Agent-based-simulations-of-lung-tumour-evolution`。
  - 只看描述就排除：`qurit/tumorsim`（細胞生長）、`denniswong1313/tumorSim`（cellular automaton）、`EETEEHAN/TumorSim`、`SalifVrt/TumorSim2`（PhysiCell 輔助）、`bd517/TumourSim`、`arthur-drozdov/TumourSim`、`Calum1888/tumourSim`（PFS 統計）、`ding-yt/TumorSimulation_BDsingleCell`、`yuadamding/tumorSimulation`、`Vmbundu/TumorSimulation`、各種 tumor growth／腦腫瘤影像 repo。沒有說明或描述與定序無關。〔推論，未讀程式〕
- Waclaw 官方頁：直接 curl 回 404；Wayback 頁面可讀，但 ZIP 兩種 URL 都只拿到 HTML。〔程式〕
- WebSearch：「TumorSim simulator tumor genome sequencing reads clonal heterogeneity」、「"TumorSim" OR "Tumorsim" software paper」、Waclaw cancer-code ZIP。結果只有 MRI TumorSim；定序模擬器的評測（PMC10896360）列出的 9 個工具也沒有 TumorSim。〔論文〕
- 沒查：PyPI、CRAN、Bioconductor 上同名套件；Google Scholar 全文。
