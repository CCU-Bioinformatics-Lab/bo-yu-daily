# 獨立語意校對 B：02 與 05

## 結論

校對結果：**PASS WITH MINOR CORRECTIONS**。

逐段比對英文原稿與繁體中文稿後，未發現漏譯、公式變動、數值錯置、路徑／locator 遺失、否定句翻轉，或證據強度被提高的情形。`STATED`、`IMPLEMENTED`、`INFERRED`、`REJECTED`、`RESOLVED`、`UNRESOLVED`、`CONFLICT`、`PAPER_ONLY` 與 `APPROXIMATE` 的判定均有保留。這兩份英文原稿未使用 `EXACT` 或 `POSSIBLE_MISMATCH` 標籤，因此中文稿沒有漏掉這兩類標籤。

公式與參數亦逐項一致，包括 `rho_bar_v` 的子樹加總、`O(V(NL+CSL^2))`、離群值的三角形雙重加總、`(L+1)/(2L)`、bootstrap 機率組合、p 值與所有 CLI/API 預設值。

下列問題都屬局部語意精度或台灣技術書寫的改善，不會改變研究結論。

## Findings

### B-01 — MEDIUM

- 檔案／段落：`05_EVIDENCE_MATRIX.md`，證據矩陣第 3 項主張（中文稿第 9 行）
- 英文原意：`In-tree mutation CCF is descendant-subtree sum of clone-exclusive prevalences.` 依 02 的公式，總和涵蓋以該節點為根的整個子樹，**包含該節點本身**。
- 問題：現譯「在後代子樹中的總和」在中文裡容易被理解為只加總後代、不含突變所在節點，會與 `rho_bar_v = rho_v + ...` 的定義產生歧義。
- 精確建議譯文：`樹內突變的 CCF，是以該節點為根的整個子樹（包含該節點本身）中，各複製株專有盛行率的總和。`

### B-02 — LOW

- 檔案／段落：`02_METHODS_DEEP_DIVE.md`，§2 變數表 `rho_v`（中文稿第 19 行）
- 英文原意：`malignant-cell fraction originating at that clone only`，重點是 clone-exclusive mass，不包含後代複製株的質量。
- 問題：現譯「僅起源於該複製株的惡性細胞比例」可能讓讀者以為後代複製株也源自此株而應計入；「only」修飾的是該節點專有的質量。
- 精確建議譯文：`僅屬於該複製株、不含其後代複製株的惡性細胞比例。`

### B-03 — MEDIUM

- 檔案／段落：`02_METHODS_DEEP_DIVE.md`，§8 Published model（中文稿第 187 行）
- 英文原意：`Outliers ... get an independent uniform-CCF PyClone likelihood.` 結合緊接其前的公式，是將離群突變的 CCF 以獨立的 Uniform(0,1) 分布積分，而不是說 PyClone likelihood 本身是均勻分布。
- 問題：現譯「取得獨立、服從均勻 CCF 的 PyClone 概似」語法上可能被讀成「概似服從均勻分布」，模糊了均勻分布作用於 CCF 的層級。
- 精確建議譯文：`離群值會排除在受繼承限制的樹之外，其 PyClone 概似則在一個獨立且服從 Uniform(0,1) 的 CCF 上積分。`

### B-04 — LOW

- 檔案／段落：`02_METHODS_DEEP_DIVE.md`，§8 Data-informed prior（中文稿第 191 行）
- 英文原意：`assigns low/high prior 0.0001/0.4 at p<0.01`，也就是以 `p<0.01` 作為選擇低／高離群先驗的判定門檻。
- 問題：現譯「並在 `p<0.01` 時分別指定低／高先驗」可能被理解為只有在 `p<0.01` 時同時指定兩個值，條件與二擇一關係不夠清楚。
- 精確建議譯文：`並以 p<0.01 為判定門檻，將離群先驗設為低值 0.0001 或高值 0.4。`

### B-05 — LOW

- 檔案／段落：`05_EVIDENCE_MATRIX.md`，CN-error 主張（中文稿第 25 行）
- 英文原意：`condition-specific flatness is not independently reconstructible ... because error-level labels are absent`，指無法分條件驗證「擾動程度改變時，結果幾乎不變」的模式。
- 問題：現譯「各條件下的平坦趨勢」是直譯，在台灣技術中文中指涉較不自然，也可能被誤認為曲線斜率的嚴格陳述。
- 精確建議譯文：`但由於 S14 缺少錯誤程度標記，無法獨立重建並驗證各擾動條件下影響近乎不變的模式。`

## 完整性核對

- `02_METHODS_DEEP_DIVE.md`：11 個主節、所有次節、公式、條列與衝突表均有翻譯，無漏段。
- `05_EVIDENCE_MATRIX.md`：說明段、25 項矩陣主張、5 項已解決衝突與 6 項未解決衝突均有翻譯，無漏項。
- 兩份稿件的 inline-code token 數量與內容逐項一致：02 為 134 個、05 為 32 個。
- 所有 claim ceiling 均維持：個案結果沒有泛化、相關性沒有改寫為普遍優越、`UNRESOLVED` 沒有被改寫成已證實，遭 `REJECTED` 的主張也沒有被翻成肯定句。

