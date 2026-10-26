# 真值樹＋模擬 SNV 資料生成器總調查

調查日期：2026-10-24。問題：除了 Pairtree（`pearsim`）與 CONIPHER（`TRACERx_simulation_tool`），還有沒有其他公開程式，能同時產生「真值演化樹」與「給建樹工具用的模擬 SNV 定序資料」？

做法：6 個 subagent 並行調查 6 個方向，共讀約 90 個 repo（只讀程式碼，沒有執行任何生成器）。之後再用 4 個 subagent 補查第一輪沒查完的 4 個名字（07–10）。Pairtree、CONIPHER、PhyClone 自己的 FS-CRP／TSSB 已在 [`../notes/05_OTHER_SIMULATORS.md`](../notes/05_OTHER_SIMULATORS.md) 處理，本調查不重做。

證據標記：〔論文〕論文或 README 的描述；〔程式〕讀過原始碼；〔推論〕分析推論，沒有實測。

## 結論

1. **有，而且不少。** 約 90 個工具中，同時輸出真值樹與 SNV 計數或 read 的超過 30 個。〔程式〕
2. **沒有任何一個工具做完整條我們要的流程。** 完整流程是：clone tree → 樹邊上的 haplotype-specific SNV 與 CN → long read BAM → 每條 read 的 clone／HP 真值。每個工具只做其中一段。〔推論〕
3. **沒有任何工具輸出「somatic SNV 在同一條 long read 上的共現」真值。** 這一層要我們自己做。〔程式〕
4. **符合篩選標準、最值得用的新工具只有 1 個**（篩選標準見「範圍更正」；另外兩個是已有的 Pairtree、CONIPHER，見 [`../notes/08_SIMULATOR_COMPARISON.md`](../notes/08_SIMULATOR_COMPARISON.md)）：

| 角色 | 工具 | 為什麼 | 主要缺點 |
|---|---|---|---|
| 真值骨架＋bulk 輸入 | **SISTEM**（`samsonweiner/sistem`，GPL-3.0，Bioinformatics 2025） | Newick 真值樹、`SNV_events.tsv` 的 `Allele` 欄、全基因組一致的 haplotype-specific CN、多 site 的 bulk ref／alt（`gen_readcounts_bulk`，`sistem/data/reads.py:223`，本次核對）、含 normal 細胞（purity<1） | 沒有 seed 參數（外部設 `np.random.seed` 可重現）；bulk 計數沒有 binomial 抽樣、VAF 沒有 CN 加權（`reads.py` L296–302，見 [07](../notes/07_SISTEM.md)），要重抽；read 層只有 short read |

5. **建議路線〔推論，未實測〕：**
   1. 用 SISTEM 的真值或自寫產生器，產生樹、segment CN、SNV 所在 haplotype。
   2. 把每個 clone × haplotype 寫成 FASTA（HeteroGenesis、SISTEM 的做法可參考）。
   3. 用 Badread 或 PBSIM3（兩者都有 `--seed`）產生 ONT read。每個 copy 的 depth 依 clone 比例與 CN 分配。
   4. minimap2 對位，加真值 tag，merge；另做 normal BAM。
   5. 跑 longphase，依 HP 計數，產生 PhyClone 輸入。
6. **補查結果（07–10）沒有找到符合標準的新工具。** cancerSimCraft 有 haplotype CN 與 SNV haplotype，但和 PSiTE 一樣只輸出 short read FASTQ。〔程式〕
7. **快速 baseline**：先用 CONIPHER 的現成資料。要測 allele-specific CN 情境時，用 SISTEM 的真值樹與 CN，再依 CN 加權公式重抽 bulk 計數（`tools/sistem_to_phyclone.py` 的 `truth_snv.tsv` 有期望值）。不要直接用 SISTEM 的 `readcounts.tsv`。〔推論〕

## 範圍更正（2026-10-24）

**clonesim（`elkebir-group/clonesim`）移出 bulk 範圍。** 01 與 06 原本把它歸在 bulk 類，這不精確：〔程式〕

- 它的 `simulate` 只寫真值（樹、每個 node × segment 的 CN、SNV 所在 allele、clone 比例），不產生 bulk read count。
- 它的 read 層是 `generatesinglecells`，產生每個 cell 的 var／total 與帶誤差的 CN，輸入對象是 Pharming、Phertilizer、SCITE 等 single-cell 建樹軟體（Pharming `simulation_study/Snakefile`）。
- Pharming 給 DeCiFer 的 bulk 輸入，是把所有 cell 的 read 加總成一個 pseudo-bulk sample（`Pharming/src/prep_decifer.py`），不是 bulk 模擬。

所以它不是給 PhyClone、Pairtree、CONIPHER 這類 bulk 建樹軟體的資料生成程式。01、06 的 clonesim 一節與 TSV 已加註；程式層級紀錄保留在 [`../notes/06_CLONESIM.md`](../notes/06_CLONESIM.md)。

SISTEM 的主要目標也是 single-cell，但它原生為每個 site 寫出 bulk read count，所以保留在 bulk 範圍。

**篩選標準（2026-10-24）：** 生成器的輸出最終要能當 PhyClone 這類 bulk 建樹軟體的輸入，而且真值要能直接對應 clone tree。真值只有 cell-level 譜系、要自己收斂成 clone tree 才能比對的演化模擬器，不列入本調查。

**VISOR 與 PSiTE 也移出（2026-10-24）。** 兩者都不是「輸出能直接給 PhyClone」的生成器：〔程式〕

- VISOR（HACk＋LASeR）沒有樹。clone 基因體與比例都要使用者自己給，它只負責產生 read。它只能當 read 模擬的零件。
- PSiTE 有樹，但只輸出 FASTA／FASTQ（寫死 ART short read）。要自己做 alignment、variant calling 與 CN calling，才能得到 PhyClone 的輸入。

02、03、05 的這兩節與 TSV 已加註；推薦表與建議路線已刪除它們。

## 各方向的結論

| 報告 | 範圍 | 一句話結論 |
|---|---|---|
| [01](01_bulk_method_simulators.md) | 建樹方法論文附的模擬器（MACHINA、CALDER、Orchard、PhylEx、PhylogicSim…） | clonesim 最符合模型需求，但它的 read 層只有 single-cell，已移出 bulk 範圍；MASCoTE 有 haplotype FASTA 與 BAM 但沒有 somatic SNV；mutsim（Orchard）有 SNV phase 但沿用 pearsim 的 seed bug。其他多數沒有 CN。 |
| [02](02_read_level_simulators.md) | read 層（BAMSurgeon、SMC-Het、HeteroGenesis、tHapMix…） | PSiTE 有逐 read 的 clone＋haplotype 真值，但只輸出 FASTQ，已移出。tHapMix 對每條 read、每個 SNV 各自獨立抽，所以同一條 read 上的 SNV 共現**不符合** clone 結構。SMC-Het 管線有隱含真值，但只有 short read，資料受控。 |
| [03](03_longread_haplotype_simulators.md) | long read 與 haplotype（VISOR、NanoSim、PBSIM3、Badread…） | 沒有現成的整條流程。VISOR 最接近，但沒有樹，已移出。LongPhase-S、ClairS 的 purity 資料是真實 read 混合，不是模擬。 |
| [04](04_evolutionary_simulators.md) | 演化／agent-based（SISTEM、CHESS、TEMULATOR…） | SISTEM 最接近 PhyClone 格式。其餘多數沒有 CN 或 purity。 |
| [05](05_singlecell_simulators.md) | single-cell 與 bulk＋sc（CellCoal、SimSCSnTree、CNAsim…） | SISTEM、SimSCSnTree、PSiTE 記錄 SNV 所在 haplotype（PSiTE 已移出）。CellCoal 有真 haplotype 但沒有 CNA。 |
| [06](06_cn_aware_bulk_simulators.md) | CN-aware bulk（DeCiFer、PyClone-VI、MOBSTER、PhylogicSim…） | clonesim 是唯一把 allele-specific segment CN 放在樹邊上的工具，但它是 single-cell 生成器，已移出 bulk 範圍。DeCiFer、SPRINTER、Tarabichi 2021 都沒有公開模擬程式。 |
| [07](07_oncosim.md) | 補查：OncoSim | 沒有符合的工具。`ciarajudge/OncoSim`（R／Shiny）有 mat/pat allele 與 allele-specific CN，但樹不寫檔、沒有 seed，且有變數拼錯的 bug。其他同名工具是人口 microsimulation 或治療模擬。 |
| [08](08_cancersim.md) | 補查：CancerSim | 沒有符合的同名工具。附帶找到 3 個：**cancerSimCraft**（樹邊上的 maternal／paternal CN、SNV 帶 `haplotype` 欄、ART short read、沒有 seed）；`cbg-ethz/WES_Cancer_Sim`（tree＋CNV＋normal 稀釋→BAM，一次性管線）；GeRnika（tree＋多 sample VAF，沒有 CN，未讀碼）。 |
| [09](09_tumorsim.md) | 補查：TumorSim | 沒有符合的工具。Waclaw 2015 TumourSimulator 有 genotype 親子表與 seed，但沒有 read、CN、purity；官方 ZIP 已 404，只讀到非官方鏡像。 |
| [10](10_moonshot.md) | 補查：Moonshot | 沒有叫 Moonshot 的模擬器。SEQC2（HCC1395）是真實資料的 SNV／indel 真值集，**不是生成器，也沒有 clone tree 真值**。 |

機器可讀總表：[`ALL_SIMULATORS.tsv`](ALL_SIMULATORS.tsv)（127 列，19 欄；clonesim 兩列的 category 已改為 `single_cell`）。第一欄是來源報告。同一個工具若被兩組調查到，會出現兩列（clonesim、SISTEM、PSiTE、VISOR、HeteroGenesis、MASCoTE 等 10 個）。要看單一方向，讀 `0N_*.tsv`。

## 本次交叉核對

兩組結果不一致或很關鍵時，我回頭讀了程式碼：

| 說法 | 結果 | 證據 |
|---|---|---|
| SISTEM 沒有 bulk 資料（04）vs 有 bulk read 數（05） | 不矛盾。有 bulk read count（`readcounts.tsv`），沒有 bulk FASTQ | `sistem/data/reads.py:223` |
| VISOR 沒有 seed | 確認。LASeR 組 Badread 指令時沒有 `--seed` | `VISOR/LASeR/LASeR.py:153` |
| clonesim seed 會生效 | 確認。`-s` 預設 0，`g_rng.seed(seed)` | `src/simulatemain.cpp:44,67` |
| PSiTE read 名稱帶 clone 與 haplotype | 確認 | `psite/fa2wgs.py:286` |
| MASCoTE 的 license（01：NOASSERTION；04：BSD 類） | 兩者都不精確。是 Princeton 自訂授權，**只限非商業研究使用** | `mascote/LICENSE.txt` |
| MASCoTE 的 seed（01：有；04：unknown） | 01 對。`--rndseed` 設定 `random`；`MixBAMs.py -rs` 預設 12 | `src/mascotte.py` L24–25、`src/MixBAMs.py` L31 |
| SISTEM 的 bulk 計數能直接給 PhyClone（04、05、07 初版） | 不能。alt＝round(DP×fraction)，沒有抽樣；VAF 沒有 CN 加權。三份報告已加註 | `sistem/data/reads.py` L296–302 |
| clonesim 是 bulk 生成器（01、06 初版） | 不是。read 層只有 single-cell，已移出 bulk 範圍 | 見「範圍更正」 |

## 限制

- 所有生成器都沒有實際執行。「能用」都是讀程式碼的判斷。〔推論〕
- 02 組的 GitHub code search 碰到 rate limit。OncoSim、CancerSim、TumorSim、Moonshot 已由 07–10 補查完成。
- 07–10 沒有查 GitLab、Zenodo、PyPI、CRAN 的全文。
- 部分論文出處憑記憶填寫，TSV 已標 `unverified`。
- 程式碼 clone 在 session scratchpad，會消失。要重讀時，依 TSV 的 `repo_url` 與 `last_commit` 重新 clone。
- 沒有加 submodule。要長期對照的工具（例如 SISTEM），再依 `../upstream/SOURCE.md` 的規則加入。
