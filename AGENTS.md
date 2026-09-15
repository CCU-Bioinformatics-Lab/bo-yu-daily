# 關鍵字搜尋路徑

依任務中的關鍵字選擇一個分支，只讀該列的「入口」。入口不足以回答或需要驗證目前行為時，才讀「深入」；任務明確跨分支時才開啟多列。每項必要主張都有對應來源後即停止擴大讀取範圍。

| 關鍵字或問題 | 入口 | 入口不足時才深入 |
|---|---|---|
| 儲存庫導覽、功能位置 | `README.md` | 對應模組的 README 或原始碼 |
| 跨模組架構、資料流、模組邊界 | `ARCHITECTURE.md` | `CONTEXT.md` |
| 領域詞彙、核心實體、既有決策 | `CONTEXT.md` | `docs/adr/` 中與問題相符的 ADR |
| 輸入、schema、v4、reads、CNV、purity、PS | `data.md` | `inference/src/model.cpp`、`inference/tests/` |
| 樣本、BAM、purity label、資料 inventory | `tumor_sample.md` | 該文件指向的 manifest 或外部路徑 |
| model、multiplicity、topology、CCF、likelihood | `model.md` | `inference/include/tumor_tree_inference/model.hpp`、`inference/src/model.cpp`、相關 ADR/tests |
| SMC、annealing、ESS、resampling、rejuvenation | `inference_algo.md` | `inference/README.md`、`inference/src/algorithm.cpp`、相關 tests |
| C++ backend、CLI、API、contract | `inference/README.md` | `inference/include/`、`inference/src/`、`inference/tests/` |
| smoke、pilot、formal、gate、停止條件 | `experiment_workflow.md` | `validation.md`、使用者指定的 config、script 或 receipt |
| 驗證指標、穩定性、claim ceiling | `validation.md` | `inference/tests/` 與使用者指定的 diagnostics 或 receipt |
| artifact、manifest、receipt、provenance、`_SUCCESS`／`_FAILED` | `output.md` | 使用者指定的 artifact 或 manifest；若含 `git_sha`，再對照該版本原始碼 |
| legacy 欄位、淘汰介面 | `legacy_data.md` | `inference/tests/` 與相關 Git history |
| 文獻、方法比較、歷史研究 | `research/` 中與主題相符的 README 或 Markdown | 該文件直接引用的論文或資料 |
| 近期決策、實驗歷程 | `daily/` 中與日期或關鍵字相符的 HTML | 原始碼、tests、manifest 與 receipts；每日紀錄只作導覽 |
| HTML、SVG、元件、視覺化 | `module_format.md` | `module_format.html`、`assets/`、`tools/` 中與元件相符的檔案 |

入口提到的路徑若不存在，以目前 `rg --files` 的結果為準，不沿用文件中的舊路徑。
