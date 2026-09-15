# 翻譯狀態

COMPLETE

| 檔案 | 輸出行數 | 狀態 |
|---|---:|---|
| `02_METHODS_DEEP_DIVE.md` | 237 | 完成 |
| `05_EVIDENCE_MATRIX.md` | 50 | 完成 |

## 自檢結果

- 完整性：通過。逐節、逐段及逐表列翻譯，未摘要或省略；`02_METHODS_DEEP_DIVE.md` 的 29 個標題、24 個表格列、26 個程式碼圍欄與 11 個項目符號均與來源一致；`05_EVIDENCE_MATRIX.md` 的 4 個標題及 27 個表格列均與來源一致。`02` 與來源的行數差 1，僅因來源檔案末尾多一個空白行。
- 技術忠實度：通過。公式、數值、版本、程式符號、路徑、XLSX sheet/cell ranges、引用 locator 均保留；所有公式逐項核對，未改變值或索引。
- 證據標記：通過。統一使用 `[明示 STATED]`、`[實作 IMPLEMENTED]`、`[推論 INFERRED]`；組合標記及 `REJECTED`、`RESOLVED`、`UNRESOLVED`、`APPROXIMATE`、`PAPER_ONLY` 等分類均忠實保留。
- 語意：通過。特別核對 clonal prevalence 與 cellular prevalence、邊際化概似、FS-CRP、SMC/PG、離群值積分不一致、版本與介面預設值等容易產生語意漂移的段落。
- 語體：通過。採用台灣學術寫作的繁體中文與自然語序；必要的演算法、統計及程式介面術語保留英文，避免誤譯。
