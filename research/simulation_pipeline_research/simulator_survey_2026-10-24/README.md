# 真值樹＋模擬 SNV 資料生成器總調查

調查日期：2026-10-24。問題：除了 Pairtree（`pearsim`）與 CONIPHER（`TRACERx_simulation_tool`），還有沒有其他公開程式，能同時產生「真值演化樹」與「給建樹工具用的模擬 SNV 定序資料」？

做法：6 個 subagent 並行調查 6 個方向，共讀約 90 個 repo（只讀程式碼，沒有執行任何生成器）。之後再用 4 個 subagent 補查第一輪沒查完的 4 個名字（07–10）。Pairtree、CONIPHER、PhyClone 自己的 FS-CRP／TSSB 已在 [`../notes/05_OTHER_SIMULATORS.md`](../notes/05_OTHER_SIMULATORS.md) 處理，本調查不重做。

證據標記：〔論文〕論文或 README 的描述；〔程式〕讀過原始碼；〔推論〕分析推論，沒有實測。

## 結論

1. **有，而且不少。** 約 90 個工具中，同時輸出真值樹與 SNV 計數或 read 的超過 30 個。〔程式〕
2. **沒有任何一個工具做完整條我們要的流程。** 完整流程是：clone tree → 樹邊上的 haplotype-specific SNV 與 CN → long read BAM → 每條 read 的 clone／HP 真值。每個工具只做其中一段。〔推論〕
3. **沒有任何工具輸出「somatic SNV 在同一條 long read 上的共現」真值。** 這一層要我們自己做。〔程式〕
4. **最值得用的 5 個工具：**

| 角色 | 工具 | 為什麼 | 主要缺點 |
|---|---|---|---|
| 真值骨架（樹＋allele-specific CN＋SNV 所在 allele） | **clonesim**（`elkebir-group/clonesim`，Pharming 用） | 每個 segment 一棵 allele-specific CNA tree，掛在 clone tree 的邊上。`xbar`／`ybar` 是 SNV 在兩個 allele 上的突變拷貝數，等於 haplotype-specific multiplicity 真值。`-s` seed 會生效（`src/simulatemain.cpp:67`，本次核對） | 沒有 license；bulk 只寫真值，read count 要自己抽 |
| 直接給 PhyClone 的 bulk 輸入 | **SISTEM**（`samsonweiner/sistem`，GPL-3.0，Bioinformatics 2025） | Newick 真值樹、`SNV_events.tsv` 的 `Allele` 欄、haplotype-specific CN、多 site 的 bulk ref／alt（`gen_readcounts_bulk`，`sistem/data/reads.py:223`，本次核對）、含 normal 細胞（purity<1） | 沒有 seed 參數；read 層只有 short read |
| read 層 haplotype 真值（short read） | **PSiTE**（`hchyang/PSiTE`，GPL-3.0） | SNV 與 allele-specific CN 沿樹放，每個 SNV 指定 parental haplotype。read 名稱前綴 `{tipnode}_prt{parental}`，所以每條 read 有 clone 與 haplotype 來源（`psite/fa2wgs.py:286`，本次核對） | 寫死 ART；2021 後沒更新 |
| read 層＋germline phased SNP | **ProCESS**（`caravagnalab/ProCESS`，前身 rRACES） | 依「細胞 → allele」產生 read，read 上帶 1000G phased germline SNP，所以 somatic SNV 與 germline SNP 的共現是真的。有 allele-specific CN、WGD、purity、multi-region、seed | 真值是 cell-level forest，要自己收斂成 clone tree；SAM 沒有 HP tag；sequencer 模型偏 Illumina，long read 長度未測；沒找到論文 |
| long read BAM＋`HP`／`CL` tag | **VISOR**（HACk＋LASeR，LGPL-3.0） | 唯一原生輸出 ONT／PacBio 並逐 read 標 `CL`（clone）、`HP` 的工具 | 沒有樹；呼叫 Badread 時沒有傳 seed（`LASeR.py:153`，本次核對）；purity<1 時用沒有 germline het SNP 的 reference read 補；同一 haplotype 上重疊的變異會被跳過 |

5. **建議路線〔推論，未實測〕：**
   1. 用 clonesim 或自寫產生器，產生樹、segment CN、SNV 所在 haplotype。
   2. 把每個 clone × haplotype 寫成 FASTA（PSiTE、HeteroGenesis、SISTEM 的做法可參考）。
   3. 用 Badread 或 PBSIM3（兩者都有 `--seed`）產生 ONT read。每個 copy 的 depth 依 clone 比例與 CN 分配。
   4. minimap2 對位，加真值 tag，merge；另做 normal BAM。
   5. 跑 longphase，依 HP 計數，產生 PhyClone 輸入。
   - 參考 VISOR LASeR 的 tag 與 merge 做法，但不要直接用它，因為它沒有 seed，purity 補法也會破壞 phasing。
6. **補查結果（07–10）不改變上面的排名。** 新增值得注意的是 cancerSimCraft（haplotype CN＋SNV haplotype，但只有 short read）與 SCOUT（ProCESS 的現成合成 cohort，可省去自己跑 ProCESS）。〔程式＋論文〕
7. **快速 baseline**：先用 SISTEM 產生 bulk 計數加真值樹。這樣不用寫 read 層，就能先測 PhyClone 在 allele-specific CN 下的表現。〔推論〕

## 各方向的結論

| 報告 | 範圍 | 一句話結論 |
|---|---|---|
| [01](01_bulk_method_simulators.md) | 建樹方法論文附的模擬器（MACHINA、CALDER、Orchard、PhylEx、PhylogicSim…） | clonesim 最符合模型需求；MASCoTE 有 haplotype FASTA 與 BAM 但沒有 somatic SNV；mutsim（Orchard）有 SNV phase 但沿用 pearsim 的 seed bug。其他多數沒有 CN。 |
| [02](02_read_level_simulators.md) | read 層（BAMSurgeon、SMC-Het、HeteroGenesis、tHapMix…） | PSiTE 有逐 read 的 clone＋haplotype 真值。tHapMix 對每條 read、每個 SNV 各自獨立抽，所以同一條 read 上的 SNV 共現**不符合** clone 結構。SMC-Het 管線有隱含真值，但只有 short read，資料受控。 |
| [03](03_longread_haplotype_simulators.md) | long read 與 haplotype（VISOR、NanoSim、PBSIM3、Badread…） | 沒有現成的整條流程。VISOR 最接近，但有 4 個缺口。LongPhase-S、ClairS 的 purity 資料是真實 read 混合，不是模擬。 |
| [04](04_evolutionary_simulators.md) | 演化／agent-based（ProCESS、SISTEM、CHESS、TEMULATOR…） | ProCESS 最適合測 HP 特徵；SISTEM 最接近 PhyClone 格式。其餘多數沒有 CN 或 purity。 |
| [05](05_singlecell_simulators.md) | single-cell 與 bulk＋sc（CellCoal、SimSCSnTree、CNAsim…） | SISTEM、SimSCSnTree、PSiTE 記錄 SNV 所在 haplotype。CellCoal 有真 haplotype 但沒有 CNA。 |
| [06](06_cn_aware_bulk_simulators.md) | CN-aware bulk（DeCiFer、PyClone-VI、MOBSTER、PhylogicSim…） | clonesim 是唯一把 allele-specific segment CN 放在樹邊上的工具。DeCiFer、SPRINTER、Tarabichi 2021 都沒有公開模擬程式。 |
| [07](07_oncosim.md) | 補查：OncoSim | 沒有符合的工具。`ciarajudge/OncoSim`（R／Shiny）有 mat/pat allele 與 allele-specific CN，但樹不寫檔、沒有 seed，且有變數拼錯的 bug。其他同名工具是人口 microsimulation 或治療模擬。 |
| [08](08_cancersim.md) | 補查：CancerSim | 沒有符合的同名工具。附帶找到 3 個：**cancerSimCraft**（樹邊上的 maternal／paternal CN、SNV 帶 `haplotype` 欄、ART short read、沒有 seed）；`cbg-ethz/WES_Cancer_Sim`（tree＋CNV＋normal 稀釋→BAM，一次性管線）；GeRnika（tree＋多 sample VAF，沒有 CN，未讀碼）。 |
| [09](09_tumorsim.md) | 補查：TumorSim | 沒有符合的工具。Waclaw 2015 TumourSimulator 有 genotype 親子表與 seed，但沒有 read、CN、purity；官方 ZIP 已 404，只讀到非官方鏡像。 |
| [10](10_moonshot.md) | 補查：Moonshot | 沒有叫 Moonshot 的模擬器。SEQC2（HCC1395）是真實資料的 SNV／indel 真值集，**不是生成器，也沒有 clone tree 真值**。附帶找到 **SCOUT**：用 ProCESS 產生的合成 WGS cohort（bioRxiv 2026，doi:10.64898/2026.06.09.731105，本次確認 DOI 可解析），purity 0.3／0.6／0.9、multi-region、allele-specific CN 真值，只有 Illumina。 |

機器可讀總表：[`ALL_SIMULATORS.tsv`](ALL_SIMULATORS.tsv)（129 列，19 欄）。第一欄是來源報告。同一個工具若被兩組調查到，會出現兩列（clonesim、SISTEM、PSiTE、VISOR、HeteroGenesis、MASCoTE 等 10 個）。要看單一方向，讀 `0N_*.tsv`。

## 本次交叉核對

兩組結果不一致或很關鍵時，我回頭讀了程式碼：

| 說法 | 結果 | 證據 |
|---|---|---|
| SISTEM 沒有 bulk 資料（04）vs 有 bulk read 數（05） | 不矛盾。有 bulk read count（`readcounts.tsv`），沒有 bulk FASTQ | `sistem/data/reads.py:223` |
| VISOR 沒有 seed | 確認。LASeR 組 Badread 指令時沒有 `--seed` | `VISOR/LASeR/LASeR.py:153` |
| clonesim seed 會生效 | 確認。`-s` 預設 0，`g_rng.seed(seed)` | `src/simulatemain.cpp:44,67` |
| PSiTE read 名稱帶 clone 與 haplotype | 確認 | `psite/fa2wgs.py:286` |

其他沒有核對的不一致：MASCoTE 的 license（01 寫 NOASSERTION，04 寫 Princeton BSD-like `LICENSE.txt`）與 seed（01 寫有 `-s`，04 寫 unknown）。

## 限制

- 所有生成器都沒有實際執行。「能用」都是讀程式碼的判斷。〔推論〕
- 02 組的 GitHub code search 碰到 rate limit。OncoSim、CancerSim、TumorSim、Moonshot 已由 07–10 補查完成。
- 07–10 沒有查 GitLab、Zenodo、PyPI、CRAN 的全文。SCOUT 的 tree 真值檔是否公開，沒有核對。
- 部分論文出處憑記憶填寫，TSV 已標 `unverified`。
- 程式碼 clone 在 session scratchpad，會消失。要重讀時，依 TSV 的 `repo_url` 與 `last_commit` 重新 clone。
- 沒有加 submodule。要長期對照的工具（例如 clonesim、SISTEM、PSiTE），再依 `../upstream/SOURCE.md` 的規則加入。
