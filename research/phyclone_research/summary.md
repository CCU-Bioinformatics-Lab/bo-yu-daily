# PhyClone 原版分析與 HP 擴充設計：摘要

這個目錄只當背景。HP 擴充的實作在 haploclone：`/bip8_disk/boyu114/haploclone/rust/`。

## 結論

- PhyClone 用 FS-CRP 樹先驗、CN／purity 校正的 allele likelihood、prevalence 邊際化和 Particle-Gibbs SMC，從 bulk 資料聯合推 mutation cluster 和 clone 祖先關係。〔repo〕`notes/zh-TW/07_PRESENTATION_BRIEF.md`
- 它的 outlier 狀態可以容納 mutation loss，但不會推論 loss 邊。CN 和 purity 是固定輸入，預分群也不能再拆。〔repo〕`notes/zh-TW/07_PRESENTATION_BRIEF.md`
- 論文實驗用 0.7.0，筆記讀的程式是 0.8.0（commit `2738324`）。版本敏感的發現不能回推到論文結果。〔repo〕`notes/zh-TW/00_SOURCE_MAP.md`
- HP 設計分 3 層：A1 HP 拆分計數＋haplotype CN、A2 subclonal haplotype CN 的 loss-aware emission、B read 層級共現。文件記載 A1、A2 已實作並測試，B 沒有實作。〔repo〕`HP_EXTENSION_DESIGN.md` §1
- 失效模式 2（C1／C2 合併）由 FSCRP prior 的 node 大小項主導。prior 的 Rust 實作已完成，實驗還沒跑。〔實測〕〔repo〕`FSCRP_PRIOR_PLAN.md`

## 使用限制

- 同 read 共現（B 層）在 2026-11-04 已決定先不列為需求（`CLAUDE.md`）。
- HP 設計的日期是 2026-10-25。haploclone 的現況以 `rust/docs/PORTING.md` 為準。
- 本機 `PhyClone/` submodule 已在 2026-11-05 刪除。筆記裡的 `PhyClone/` 路徑要對照上游 commit，或看 `/bip8_disk/boyu114/phyclone/`（同一個 commit）。

## 全文層

| 檔案 | 內容 |
|---|---|
| `notes/zh-TW/00_SOURCE_MAP.md` | 來源對照與證據詞彙 |
| `notes/zh-TW/01_PAPER_BIG_PICTURE.md` | 論文全貌 |
| `notes/zh-TW/02_METHODS_DEEP_DIVE.md` | 方法細節 |
| `notes/zh-TW/03_EXPERIMENTS_RESULTS.md` | 實驗與結果 |
| `notes/zh-TW/04_CODE_MAPPING.md` | 論文和程式對照 |
| `notes/zh-TW/05_EVIDENCE_MATRIX.md` | 證據矩陣 |
| `notes/zh-TW/06_ASSUMPTIONS_LIMITATIONS.md` | 假設與限制 |
| `notes/zh-TW/07_PRESENTATION_BRIEF.md` | 簡報大綱 |
| `HP_EXTENSION_DESIGN.md` | HP 擴充設計 |
| `FSCRP_PRIOR_PLAN.md` | FSCRP prior 修改計畫 |

第一手資料見 `source.md`。
