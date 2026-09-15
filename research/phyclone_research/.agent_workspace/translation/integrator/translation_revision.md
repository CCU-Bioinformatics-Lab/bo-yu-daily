# 繁體中文翻譯整合修訂紀錄

## 整合範圍

- 英文正式稿：`notes/00_SOURCE_MAP.md` 至 `notes/07_PRESENTATION_BRIEF.md`。
- 初稿：`batch_a/`、`batch_b/`、`batch_c/` 共八份。
- 獨立校對：`semantic_a/review.md`、`semantic_b/review.md`、`style_structure/review.md`。
- 正式成果：`notes/zh-TW/00_SOURCE_MAP.md` 至 `notes/zh-TW/07_PRESENTATION_BRIEF.md`。
- 英文正式稿、批次初稿、校對報告與研究來源均未修改。

## 統一術語表

| 英文 | 正式譯法 |
|---|---|
| clone | 克隆；必要時首次說明為細胞族群 |
| clonal / subclonal | 克隆性／亞克隆 |
| cluster / pre-cluster | 叢集／預分群叢集 |
| clonal prevalence | 克隆盛行率 |
| cellular prevalence | 細胞盛行率 |
| clone-exclusive mass/prevalence | 克隆專有質量／盛行率 |
| bulk sequencing/specimen | 整體腫瘤定序／整體腫瘤檢體 |
| likelihood | 概似 |
| collapsed likelihood/integration | 邊際化概似／邊際化積分 |
| convolution | 卷積 |
| topology | 拓樸 |
| outlier | 離群值；作模型狀態時為離群值狀態 |
| proposal | 提議分布 |
| multinomial resampling | 多項分布重抽樣 |
| tumour content | 腫瘤含量（即腫瘤純度）；後文簡稱純度 |

`evidence` 一律譯為「證據」而非「證明」。`not significant` 一律保留為「未達顯著／無顯著差異」，不改寫成「相同」或「等效」。

## Semantic A findings disposition

| Finding | 嚴重度 | 處置 |
|---|---:|---|
| A-01 | HIGH | 採納；`multinomial resampling` 改為「多項分布重抽樣」。 |
| A-02 | HIGH | 採納；「證明該系統」改為「提供證據顯示」，維持證據強度。 |
| A-03 | MEDIUM | 採納；改為「PG 取樣核心（kernel）」與「Dirichlet 重要性抽樣」。 |
| A-04 | MEDIUM | 採納；改為「非單例叢集中的資料點」，明確保留 singleton 限制。 |
| A-05 | MEDIUM | 採納；明列 PhyClone 253 秒、PhyloWGS 37,563 秒，消除配對歧義。 |
| A-06 | LOW | 採納並依橫向審查調整；使用「彼此相關的整體腫瘤樣本／整體腫瘤定序」。 |
| A-07 | LOW | 採納；`optional` 統一為「可選的」，external pre-clustering 為「外部預分群」。 |
| A-08 | LOW | 採納；改為「完整的數學推導」。 |
| A-09 | LOW | 採納；改為「每個留存的條件組合」。 |
| A-10 | LOW | 採納；改為「根節點的總質量固定為 1」。 |
| A-11 | LOW | 採納；敘事中的 proposal、subtree PG 與 selection probability 均加上中文技術主詞，識別碼及設定值保留英文。 |

## Semantic B findings disposition

| Finding | 嚴重度 | 處置 |
|---|---:|---|
| B-01 | MEDIUM | 採納；明寫整個子樹包含節點本身。 |
| B-02 | LOW | 採納；`rho_v` 改為僅屬該克隆且不含後代克隆的比例。 |
| B-03 | MEDIUM | 採納；明確說明是在獨立且服從 `Uniform(0,1)` 的 CCF 上積分概似。 |
| B-04 | LOW | 採納；明確寫成以 `p<0.01` 為門檻，在低值 0.0001 與高值 0.4 間設定先驗。 |
| B-05 | LOW | 採納；以「各擾動條件下影響近乎不變的模式」取代平坦趨勢直譯。 |

## Style/structure findings disposition

| Finding | 嚴重度 | 處置 |
|---|---:|---|
| C-01 | HIGH | 採納；全域統一 clone＝克隆、cluster＝叢集。 |
| C-02 | MEDIUM | 採納；依腫瘤定序語境使用「整體腫瘤定序／檢體」，避免誤解為 population sequencing。 |
| C-03 | MEDIUM | 採納；`clinical efficacy` 改為「推廣至病人族群的臨床效用」。 |
| C-04 | MEDIUM | 採納；`recurrence` 改為「突變重複發生事件」，避免誤讀為癌症復發。 |
| C-05 | MEDIUM | 採納；改為「設定上有利於 PhyClone 的方法內部消融實驗」。 |
| C-06 | MEDIUM | 採納；統一概似、拓樸、邊際化與卷積。 |
| C-07 | LOW | 採納；`optional` 使用「可選的」。 |
| C-08 | LOW | 採納；改寫為突變因後代分支上的缺失事件而消失。 |
| C-09 | LOW | 採納；統一 `[已釐清 RESOLVED]`，並以 `UNRESOLVED（未釐清）` 表示未決問題。 |
| C-10 | LOW | 採納；敘事中的 `outliers` 與 `targeted-count` 已中文化；程式符號、路徑、方法名及原始 locator 保留。 |
| C-11 | LOW | 採納；首次說明 tumour content 即腫瘤純度，後文依欄位或語境使用腫瘤含量／純度。 |

## 完整性與忠實度檢查

| 檔案 | 標題 | 表格列 | code fence | inline-code 數量 | 結果 |
|---|---:|---:|---:|---:|---|
| `00_SOURCE_MAP.md` | 12/12 | 43/43 | 2/2 | 66/66 | PASS |
| `01_PAPER_BIG_PICTURE.md` | 11/11 | 8/8 | 2/2 | 2/2 | PASS |
| `02_METHODS_DEEP_DIVE.md` | 29/29 | 24/24 | 26/26 | 134/134 | PASS |
| `03_EXPERIMENTS_RESULTS.md` | 15/15 | 43/43 | 0/0 | 37/37 | PASS |
| `04_CODE_MAPPING.md` | 4/4 | 45/45 | 0/0 | 62/62 | PASS |
| `05_EVIDENCE_MATRIX.md` | 4/4 | 27/27 | 0/0 | 32/32 | PASS |
| `06_ASSUMPTIONS_LIMITATIONS.md` | 10/10 | 16/16 | 0/0 | 16/16 | PASS |
| `07_PRESENTATION_BRIEF.md` | 17/17 | 0/0 | 0/0 | 12/12 | PASS |

表中數字依序為英文稿／正式中文稿。前三份中文稿少一個空白或檔尾換行，內容區塊沒有缺漏。除 `00_SOURCE_MAP.md` 將三個 evidence marker 的 code-span 內容翻成雙語標籤外，其餘七份 inline-code token 多重集合均與英文稿相同；00 的 token 數量仍一致。公式、p 值、版本、SHA、路徑、cell range、locator 與證據類別均已抽查並保留。

## Root QA 補充修訂

- 將 `01_PAPER_BIG_PICTURE.md`、`06_ASSUMPTIONS_LIMITATIONS.md` 與 `07_PRESENTATION_BRIEF.md` 內四處可能被誤讀為「只含後代」的「後代子樹」改寫為：以該節點為根，且包含節點本身及所有後代的整個子樹。此修訂只消除圖論範圍歧義，不改變模型或證據強度。
- `02_METHODS_DEEP_DIVE.md` 相較英文稿唯一增加的數值 token 是 `Uniform(0,1)` 中的 `0,1`；這是 semantic B 的 B-03 所核准之語意澄清，明確指出均勻分布作用於 CCF，而非作用於概似。公式、實驗數值、版本與 locator 均未更動。
- 最終結構 QA 移除 `06_ASSUMPTIONS_LIMITATIONS.md` 澄清句中兩個重複新增的 inline-code `v` 標記，但完整保留「以該節點為根，包含節點本身及所有後代」的定義。八份文件的 Markdown 結構與 inline-code 數量均與英文稿一致：8/8 PASS。

## 最終判定

八份文件均為完整繁體中文譯本；所有 HIGH、MEDIUM、LOW findings 與 Root QA 補充修訂均已採納，沒有駁回項目。證據上限、否定、未顯著、衝突與未解事項的語氣均未提高或翻轉。
