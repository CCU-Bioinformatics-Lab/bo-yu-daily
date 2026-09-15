# 獨立翻譯校對 C：術語、語意與結構審查

## 審查範圍與結論

- 逐段英中對照：`03_EXPERIMENTS_RESULTS.md`、`06_ASSUMPTIONS_LIMITATIONS.md`、`07_PRESENTATION_BRIEF.md`。
- 橫向檢查：batch_a、batch_b、batch_c 的八份正式譯稿。
- 結論：三份逐段對照稿沒有漏段、漏表、數值改寫或 locator 遺失；否定、顯著／不顯著、限制與證據上限的語氣大致忠實。Markdown 的標題、表格、清單及 code fence 結構亦完整。正式整合前仍需修正下列局部語意問題，並統一跨文件術語。

## Findings

### 1. HIGH — clone 與 cluster 的譯名跨文件不一致，可能使兩個不同實體混為一談

- **檔案／段落：** `01_PAPER_BIG_PICTURE.md` 全文使用「克隆／叢集」；`02_METHODS_DEEP_DIVE.md`、`05_EVIDENCE_MATRIX.md` 使用「複製株／群集」；`03_EXPERIMENTS_RESULTS.md`、`06_ASSUMPTIONS_LIMITATIONS.md`、`07_PRESENTATION_BRIEF.md` 使用「複製群／群集」。
- **問題：** clone 是生物學細胞族群，cluster 是演算法上的突變群集。現在三套 clone 譯名與兩套 cluster 譯名並存；「複製群」尤其容易和「群集」混淆。
- **精確建議譯文／全域詞彙表：**
  - `clone` →「克隆」；首次出現可寫「克隆（細胞族群）」；
  - `clonal` →「克隆性」；`subclonal` →「亞克隆」；
  - `clone mass` →「克隆質量」；`clonal prevalence` →「克隆盛行率」；
  - `cellular prevalence` →「細胞盛行率」；
  - `mutation cluster`／`pre-cluster` →「突變群集」／「預分群群集」。
- **代表性修正：** `07_PRESENTATION_BRIEF.md` 一句話版本改為「……聯合推論突變群集與克隆祖先關係……」；`06_ASSUMPTIONS_LIMITATIONS.md` 第 5 行改為「其 CCF 等於後代子樹中克隆質量的總和」。

### 2. MEDIUM — `bulk` 被譯為「群體」，容易誤解成 population sequencing

- **檔案／段落：** `07_PRESENTATION_BRIEF.md` 一句話版、30 秒版、三分鐘版第 1 點、投影片 1；`05_EVIDENCE_MATRIX.md` 第 7 行仍保留英文 `bulk`；`01_PAPER_BIG_PICTURE.md` 則使用「整體樣本／整體定序」。
- **問題：** 此處 `bulk tumour/specimen/sequencing` 指未做單細胞分離的整體腫瘤檢體，不是族群層級研究。「群體定序／群體檢體」有語意漂移。
- **精確建議譯文：** 統一為「整體腫瘤定序」、「整體腫瘤檢體」與「整體樣本」。例如 30 秒版首句改為：「整體腫瘤定序混合了多個克隆，因此只依盛行率將突變分群，無法揭示祖先關係，且往往會留下多棵都與資料相容的樹。」

### 3. MEDIUM — `clinical efficacy` 譯成「臨床療效」會誤指治療效果

- **檔案／段落：** `03_EXPERIMENTS_RESULTS.md`，最終可支持的實驗主張，第 161 行。
- **問題：** 原文否定的是由此重建研究推論族群層級臨床效用／有效性的能力，不是在評估藥物療效。「療效」會把研究問題改成治療成效。
- **精確建議譯文：** 句尾改為「……或族群層級的臨床有效性。」若要更保守，可寫「……或推廣至病人族群的臨床效用。」

### 4. MEDIUM — mutation `recurrence` 譯成「復發事件」，易被理解成癌症復發

- **檔案／段落：** `06_ASSUMPTIONS_LIMITATIONS.md`，生物學假設第 5 點，第 9 行。
- **問題：** 此處 recurrence 是同一突變在系譜中獨立重複發生，不是疾病復發。
- **精確建議譯文：** 「同一狀態可以吸收缺失、CN 錯誤、比對／計數錯誤或其他不相容情況；模型不會推論發生缺失的分支，也不會推論突變重複發生事件。」

### 5. MEDIUM — `a favourable internal ablation` 的修飾對象不清楚

- **檔案／段落：** `07_PRESENTATION_BRIEF.md`，投影片 7 口頭說明，第 70 行。
- **問題：** 「有利於內部方法的消融實驗」不自然，也沒有明確指出實驗設定有利於 PhyClone。原文的 `internal` 指方法內部消融，`favourable` 指生成設定偏向本方法。
- **精確建議譯文：** 「這是設定上有利於 PhyClone 的方法內部消融實驗，且不能定位突變流失發生在哪一條邊。」

### 6. MEDIUM — likelihood、topology、collapsed 與 convolution 的術語未依台灣學術慣例統一

- **檔案／段落：** batch_a 使用「似然、拓樸、摺疊式、摺積」；batch_b/c 多用「概似、拓撲、折疊式、卷積」，其中 `02_METHODS_DEEP_DIVE.md` 內亦同時出現「拓樸」與「卷積」。
- **問題：** 同一套正式成果不宜混用；此外 collapsed integration 和 mathematical convolution 是兩個不同運算，不能都用「摺」字處理。
- **精確建議譯文／全域詞彙表：**
  - `likelihood` →「概似」；`likelihood-weighted` →「以概似加權」；
  - `topology` →「拓樸」（台灣常用字形）；
  - `collapsed likelihood/integration` →「邊際化概似／邊際化積分」，避免「摺疊式」的歧義；
  - `convolution` →「卷積」。
- **代表性修正：** `01_PAPER_BIG_PICTURE.md` 一句話摘要的「摺疊式盛行率似然」改為「盛行率邊際化概似」；`04_CODE_MAPPING.md` 的「子節點似然摺積」改為「子節點概似卷積」。

### 7. LOW — `optional` 不宜譯為「選用式」

- **檔案／段落：** `07_PRESENTATION_BRIEF.md`，投影片 3 核心訊息，第 39 行；另見其他文件的「選用的」。
- **問題：** 「選用式預分群」不像台灣自然用法，可能被誤認為一種特定方法類型。
- **精確建議譯文：** 「定序讀數／CN／純度 → 可選的預分群 → 貝氏樹後驗 → MAP／共識／拓樸。」

### 8. LOW — `mutation deleted on a descendant branch` 的被動句不自然

- **檔案／段落：** `07_PRESENTATION_BRIEF.md`，投影片 7 建議圖示，第 69 行。
- **問題：** 「一個突變……被缺失」不是自然中文，也模糊 deletion 與 mutation loss 的關係。
- **精確建議譯文：** 「畫出一個突變因後代分支上的缺失事件而消失，接著被送入離群值容器 `-1`。」

### 9. LOW — 一處 evidence marker 的中英文順序和其餘 117 處不同

- **檔案／段落：** `03_EXPERIMENTS_RESULTS.md`，E3 資料段，第 77 行。
- **問題：** 唯一使用 `[RESOLVED 已釐清]`；其餘證據標記一律採中文在前，例如 `[明示 STATED]`。此外 `UNRESOLVED（未解決）` 與 `UNRESOLVED（未釐清）` 也跨文件混用。
- **精確建議譯文：** 第 77 行改為 `[已釐清 RESOLVED]`；全域統一採 `UNRESOLVED（未釐清）`、`REJECTED（駁回）`、`CONFLICT（衝突）`。

### 10. LOW — 少數英文普通詞仍可中文化，但技術識別碼應保留

- **檔案／段落：** `06_ASSUMPTIONS_LIMITATIONS.md` 失敗情境矩陣第 82 行的 `outliers`；`03_EXPERIMENTS_RESULTS.md` 第 136 行的 `targeted-count`；八份稿中的 `Main`／`Supplement` locator 呈現方式不一。
- **問題：** `outliers` 與 `targeted-count` 在敘事句中不是不可翻譯的識別碼；來源 locator 則有「主文／補充資料」和 `Main`／`Supplement` 兩種風格。
- **精確建議譯文：** 「0.8.0 的 bootstrap＋離群值」、「WGS＋標靶計數輸入」。Locator 建議全域保留原始格式 `Main`／`Supplement` 以方便搜尋，或全域改為「主文」／「補充資料」，但不可混用；sheet 名稱、程式符號、路徑、CLI flag 與方法名稱保持原文。

### 11. LOW — `tumour content` 與 purity 的關係應在首次出現時固定

- **檔案／段落：** `01_PAPER_BIG_PICTURE.md` 使用「腫瘤含量」；`02_METHODS_DEEP_DIVE.md` 使用「腫瘤含量／純度」；batch_c 多只寫「純度」。
- **問題：** 兩者在本資料模型中指惡性細胞比例，但讀者可能以為是兩個輸入欄位。
- **精確建議譯文：** 首次出現寫「腫瘤含量（tumour content；即腫瘤純度）」，後文統一簡稱「純度」；程式欄位 `tumour_content` 保留不翻。

## 數值、否定與限制語氣核對

- `03_EXPERIMENTS_RESULTS.md`：所有表格數值、p 值、正負號、成功／缺失次數、cell range 與 S-sheet locator 均與英文原稿相同。`not significant`、`does not establish`、`UNRESOLVED` 與 pooled-test 限制均有保留。
- `06_ASSUMPTIONS_LIMITATIONS.md`：六組假設／限制及 14 列失敗情境均完整；版本 0.7.0/0.8.0、`C=1000`、`2^R`、`O(V(NL+CSL²))`、預設值與程式 locator 無異動。
- `07_PRESENTATION_BRIEF.md`：一句話、30 秒、三分鐘、10 張投影片、4 張備用投影片與 7 個教授問答均完整；所有數值、版本與複雜度式均相同。

## Markdown 結構檢查

八份英文／中文稿的標題數、表格列數、code fence 數、項目符號數與編號清單數逐檔相同。batch_a/b 中的 `00_SOURCE_MAP.md`、`01_PAPER_BIG_PICTURE.md`、`02_METHODS_DEEP_DIVE.md` 各比英文稿少一行，差異是空白／檔尾換行，不是內容遺失。未發現表格欄位錯位、code fence 未閉合或清單層級破壞。

## 建議整合順序

1. 先套用 Findings 1、2、6、11 的全域詞彙表。
2. 再修正 Findings 3–5 的局部語意問題。
3. 最後統一 evidence marker、locator 與殘留普通英文，並重新做一次數值／backtick token 比對。
