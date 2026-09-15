# Batch A 翻譯狀態

COMPLETE

## 完成檔案

| 檔案 | 譯文行數 | 狀態 |
|---|---:|---|
| `00_SOURCE_MAP.md` | 116 | 完整翻譯 |
| `01_PAPER_BIG_PICTURE.md` | 83 | 完整翻譯 |
| `04_CODE_MAPPING.md` | 64 | 完整翻譯 |

## 自檢結果

- 三份譯文的 Markdown 標題數量與層級均與原文相同。
- 三份譯文的表格列數、每列欄位數、編號項目數與程式碼區塊數均與原文相同。
- 排除依規格翻譯的證據標記後，所有行內程式碼、路徑、函式名稱與參數字串均與原文逐項一致，且出現次數相同。
- 所有阿拉伯數字 token（包括版本、數值、頁碼、XLSX sheet/cell ranges、commit 與 SHA-256 內的數字部分）均逐檔比對，數量與原文相同，無遺漏或新增。
- 證據標記已統一為 `[明示 STATED]`、`[實作 IMPLEMENTED]`、`[推論 INFERRED]`；組合標記保留 XLSX 等原始限定詞。
- `EXACT`、`POSSIBLE_MISMATCH`、`APPROXIMATE`、`PAPER_ONLY`、`ADDITIONAL_IMPLEMENTATION_DETAIL` 與 `UNRESOLVED` 等分類均保留英文，並於首次需要處提供中文說明。
- 已逐段檢查語意方向、否定語氣、比較關係、統計顯著性與版本界線；未發現語意反轉或內容省略。
- 採用台灣學術書寫習慣，使用「資料、程式碼、儲存庫、相依套件、整體定序、標靶定序、拷貝數、純度」等用語，未使用中國大陸慣用語法。
