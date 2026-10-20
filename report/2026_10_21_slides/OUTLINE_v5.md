# 2026-10-21 簡報大綱 v5 草案（使用者已確認方向；審查中）

v4.2（`OUTLINE.md`）偏離使用者指定的主題。本版只保留兩大段，見 `report_rule.md`「各簡報主軸」。
本版尚未做兩方審查（`report_rule.md` 製作流程第 1 條）。

## 主問題

要驗證 long-read 特徵能不能讓演化樹更準，需要「有真值樹、又有 long read」的資料。
這種資料存在嗎？不存在的話，前人的驗證資料怎麼做，我們可以照著做？

- 第一大段回答：存在嗎？
- 第二大段回答：前人怎麼做？

## 判準（第一大段使用）

| 軸 | 判「有」的條件 | 來源 |
|---|---|---|
| single-cell 真值樹 | 用 single-cell 定序排出樹，並拿它驗證建樹結果。以 PhyClone 用的 single-nucleus 真值樹為標準（`report_rule.md` 文字與表格第 4 條） | 規則檔 |
| long read | bulk 長讀資料進入建樹流程（不只做 variant calling 或 SV 驗證） | `paper_categories.tsv` 的 `long_read_role` |
| haplotype（HP） | 突變被指派到 HP1／HP2 | `long_read_features` |
| phase set（PS） | 用到 phase block 的邊界（HP 只在同一個 block 內有意義） | `long_read_features` |

## 第一大段：有沒有研究同時用 single-cell 真值樹與 long-read 特徵？

### P1 封面
- 標題草案：「有真值樹又有 long read 的建樹資料存在嗎？」

### P2 主問題
- 一個主問題，下面兩張卡片：存在嗎？／前人怎麼做資料？

### P3 標題：「22 篇裡，只有 1 篇同時有長讀與 single-cell 驗證」
- 圖：2×2 篇數表（列：短讀／長讀；欄：single-cell 真值 無／有）。短讀無 6、長讀無 4、短讀有 11、長讀有 1。長讀有那格加框。
- 圖旁小圖：什麼叫 single-cell 真值樹（一顆一顆細胞定序 → 排樹 → 當答案）。
- 講稿：篇數是我們自己分類的（分析推論）。說明搜尋範圍與判準。

### P4 標題：「用到 HP 與 phase block 的研究，都沒有完整的真值樹」
- 圖：特徵矩陣。列是論文，欄是「single-cell 真值樹／long read 進建樹／HP／PS／BAM 可下載」。格子只寫「有」「無」。
- 只列有任一 long-read 或 phasing 特徵的篇（使用者 2026-10-19 決定）。候選列（待逐篇查核）：
  - 肺癌 ONT（B04）：長讀有、HP 有、PS 有、single-cell 只有局部佐證（2 位病人、可對照的突變對只有 2 與 13 對）。
  - 小鼠單細胞衍生子株（B01）：長讀有、HP 無（近親品系沒有異型合子 SNP）、樹是推得的參考，不是真值。
  - SIGNALS（B03）：single-cell 樹有、ONT 只做 SV 驗證。
  - PhyClone（M01）：single-cell 真值樹有、長讀無。
  - TreeClone（M02）：短讀 read-pair 共現有、無真值。
- 結論：沒有一篇同時滿足「完整真值樹」與「HP／PS 進入建樹」。
- 講稿：B04 的長讀只用來在兩棵候選樹中挑一棵，不在建樹模型內。

## 第二大段：各論文的模擬資料與真實資料怎麼產生？

### P5 標題：「多數模擬只產生 read 數，沒有產生 read」
- 圖：兩條生成路線對照。
  - 左「計數層級」：設計樹 → 每個 clone 的 CCF → 依二項分布抽有／沒突變的 read 數。代表：PhyClone 的 TSSB、FS-CRP、Pairtree、CONIPHER 模擬；TreeClone（從自己的 prior 生成）；TUSV-ext；PhylEx（bulk＋scRNA 計數）；Pharming（low-pass scDNA 細胞）。
  - 右「read 層級」：真實 read 依 haplotype 切開 → 調深度模擬拷貝數 → 植入突變 → 合併成腫瘤 BAM。代表：SMC-Het。
- 結論：計數層級沒有 read，所以沒有 HP、PS、同 read 共現。
- 講稿：PhyClone 模擬多數 purity＝1、拷貝數簡單。TreeClone 資料由自己的 prior 生成，對自己有利。

### P6 標題：「SMC-Het 把突變放在特定 haplotype 上，可改成長讀版」
- 圖：SMC-Het 五步流程。HG002 300× 短讀 → 依 haplotype × 染色體切 read pool → 依 clone 比例與拷貝數調深度 → 植入 SNV／SV（子 clone 帶父 clone 的突變）→ 合併並呼叫變異。
- 圖下：同一流程換成 HG002 ONT 長讀時，哪一步要改（標「分析推論」）。
- 講稿：真值裡已有「突變在哪個 haplotype」。參賽者只拿到 VCF 與拷貝數結果，看不到 read。

### P7 標題：「真實資料的真值樹，都來自另一批 single-cell 定序」
- 圖：三種真值來源。
  - single-nucleus 標靶定序：McPherson 2016 卵巢癌（R01）→ PhyClone 真實資料的真值。
  - DLP+ 全基因體 single-cell：卵巢癌病人與細胞株（A01、A02、B03、M06）。
  - Tapestri 標靶 panel、Strand-seq：胰臟癌、白血病（A03、A04、A05）。
- 每格標：病人或細胞株、細胞數、短讀。
- 講稿：這些都是短讀。single-cell 樹多半是拷貝數樹或標靶 panel 樹，和 SNV 樹不完全相同（待逐篇查核）。

### P8 標題：「真實長讀資料都沒有真值樹」
- 圖：長讀真實資料表（樣本／平台／真值）。
  - 肺癌病人 20 位（B04）：ONT＋2 位病人 10x scDNA；受控存取。
  - 小鼠 melanoma 23 株單細胞衍生子株（B01）：每株 ONT；樹由同一批突變推得。
  - HCC1395 社群參考資料（H01）：PacBio 只做 call set 驗證；10x 單細胞 CNV 只有局部佐證。
- 講稿：子株資料可以混合成「已知組成」的半真實樣本（分析推論，原論文沒做）。

### P9 總結
- 存在嗎：不存在。最接近的 B04 只有局部 single-cell 佐證，長讀只用來事後挑樹。
- 前人怎麼做：模擬多停在計數層級；只有 SMC-Het 做到 read 層級並保留 haplotype。真實資料的真值都來自短讀 single-cell。
- 對我們的參考（分析推論）：
  1. 照 SMC-Het 流程，改用長讀做 read 層級模擬。
  2. 用單細胞衍生子株混合，做半真實資料。

## 待查核（製作前要補）

- 22 篇中有沒有長讀層級的模擬。目前讀到的筆記都沒有。
- A01–A05 的 single-cell 樹是 SNV 樹還是拷貝數樹，以及細胞數。
- 每篇「BAM 可下載」欄。可從 `research/tumor_phylogeny_2026/ONT_DATA_AVAILABILITY.md` 與各篇資料段補。
- PhyClone 各模擬器的生成細節：查 `research/phyclone_research/notes/`。

## 來源

- `research/paper_categories.tsv`（分類與篇數）。
- 各篇 README：M01、M02、M04、M05、M06、M07、B01、B03、B04、R01、H01。
