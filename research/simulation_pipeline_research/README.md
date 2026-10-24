# 模擬資料生成流程研究

本目錄整理 PhyClone 的模擬資料生成流程。目的是設計帶 long read 特徵（HP1／HP2 phasing、read 共現）的模擬資料，用來驗證 HP-aware PhyClone。

驗證計畫本身以 repo 根目錄的 `plan.md`（§5.7 L0、§5.8 L2、§5.9 L1-B）為準。本目錄只負責「模擬資料怎麼產生」。

## 結論摘要

1. **PhyClone 的模擬器是計數層。** 它只輸出每個 SNV 每個 sample 的 ref／alt 計數，不產生 read，也沒有 haplotype。〔程式〕
2. **上游 repo 只有 FS-CRP 的生成程式。** TSSB、mutation loss、CN 擾動的生成程式都不在 repo 內。Pairtree 與 CONIPHER 資料是借用已發表的模擬資料。〔論文 p.4–5；程式〕
3. **FS-CRP 樹的形狀有偏向。** SNV 數最多的 cluster 一定是 root，parent 的 SNV 數一定 ≥ child。這和論文寫的 Uniform forest prior 不一致。本機 `FS-CRP_Loss` 的 100 棵真值樹全部符合這個偏向。〔程式＋實測〕
4. **CN 對每個 SNV、每個 sample 獨立抽。** CN 沒有 segment 結構，也不跟著 clone 走。同一個 SNV 在 8 個 sample 中的 CN 可以全部不同。〔程式＋本機資料〕
5. **因此要自己寫 HP-aware 生成器。** PhyClone 的程式可以沿用「樹 → prevalence → 計數」的骨架，但 CN、haplotype、read 共現都要重新設計。缺口見 [04](notes/04_GAPS_FOR_LONGREAD.md)。

標記：〔論文〕＝論文或補充文件的描述；〔程式〕＝讀程式碼得到的行為；〔實測〕＝本目錄實際執行的結果；〔本機資料〕＝讀 `/big8_disk/boyu114/phyclone_dataset/` 得到；〔推論〕＝分析推論，尚未直接證實。

## 目錄

| 路徑 | 內容 |
|---|---|
| [notes/01_PAPER_SIMULATION_DESIGN.md](notes/01_PAPER_SIMULATION_DESIGN.md) | 論文描述：generative model、emission、各 benchmark 資料集怎麼生成 |
| [notes/02_CODE_PIPELINE.md](notes/02_CODE_PIPELINE.md) | 程式實作：`fscrp.py` → `sim_data_on_tree.py` → likelihood grid；參數、已驗證行為、論文與程式的差異 |
| [notes/03_BENCHMARK_DATASET_FORMAT.md](notes/03_BENCHMARK_DATASET_FORMAT.md) | 本機 benchmark 資料集的真值格式，以及從資料反推的生成參數 |
| [notes/04_GAPS_FOR_LONGREAD.md](notes/04_GAPS_FOR_LONGREAD.md) | 要產生 long read 特徵還缺什麼；對應 `plan.md` 的 L1-B／L2 |
| [simulator_survey_2026-10-24/](simulator_survey_2026-10-24/README.md) | 其他「真值樹＋模擬 SNV 資料」生成器總調查（約 90 個工具，6 個方向）與總表 `ALL_SIMULATORS.tsv` |
| [phyclone_sim_code/](phyclone_sim_code/SOURCE.md) | PhyClone 模擬與驗證程式的快照（上游 commit `2738324`），來源對照見 `SOURCE.md` |
| `references/` | 指向論文、補充文件、XLSX、benchmark 資料集 README 的 symlink |

## 相關文件（不複製，直接連結）

- PhyClone 模型與實驗整體分析：[`../phyclone_research/notes/zh-TW/`](../phyclone_research/notes/zh-TW/00_SOURCE_MAP.md)，特別是 `03_EXPERIMENTS_RESULTS.md`。
- benchmark 資料集與 SMC-Het 資料集盤點：repo 根目錄 `tumor_sample.md`。
- 前人模擬方式分層（事件層／計數層／read 層）：`report/2026_10_21_slides/project/slides/s2-sim-layers.html`。
- HP-aware 驗證計畫：repo 根目錄 `plan.md`。

## 維護規則

- `phyclone_sim_code/` 是唯讀快照。要改上游行為，在 submodule `../phyclone_research/PhyClone/` 內改並另外 commit。
- 新寫的生成器放 repo 根目錄 `tools/`，實驗結果放 `lab_report/YYYY-MM-DD_<主題>/`。本目錄只放分析文件。
