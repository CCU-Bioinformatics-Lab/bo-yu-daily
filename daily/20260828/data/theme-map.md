# 2026-08-28 主題對照

## 主題

| 主題 | 核心問題 | 對應任務 | 代表產出 |
| --- | --- | --- | --- |
| 1. 文件與讀者語言 | Model 要說到什麼程度，才能可讀又不超出目前實作？ | T1、T8 | `module_format.md`、model definitions crosswalk |
| 2. `eta` 與 clone fraction 語意 | local fraction、CCF／`phi`、`clonal prevalence` 是否混用？ | T2、T3 | terminology sync、`eta_symbol_literature.md` |
| 3. 候選樹 state 設計 | `T`、`eta`、`phi`、`z`、`m` 各自留在哪一層？ | T4 | `t_eta_design_review.md` |
| 4. CNV／multiplicity-aware emission | 如何讓 VAF／read-count likelihood 和 copy number、purity、timing 對齊？ | T5、T6、T7 | ADR、`phyclone_xi_v1` implementation |
| 5. 可驗證交付與邊界 | 已完成的 code／測試和尚未完成的 predictive gate 如何分開？ | T7、T8、T9 | 48/48 tests、commit `4138d59`、pending list |

## 覆蓋檢查

- T1–T9 全部被至少一個頁面引用。
- 主題 1–5 全部在 `01-today-map.html` 出現，並在後續頁面展開。
- 最後一頁只放未完成、待決與下一步，不把規格文件或 smoke test 包裝成正式 validation。
