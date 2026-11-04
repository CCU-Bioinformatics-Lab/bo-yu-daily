# v5 大綱審查摘要（P-1，2026-10-22）

兩位審查者結論都是「需修改後再審」。主 agent 核對了教授提出的程式事實（commit 版本、摘要表檔名、LTXSIM001 數值），都成立。

## 已改進 v5.1

| 來源 | 頁 | 問題 | 改法 |
|---|---|---|---|
| 邏輯 | P9 | 寫「沿用 0–3 步」，講稿卻改第 2 步 | 改成沿用 0、1、3；改寫 2、4；新增 germline SNP 與 phasing 錯誤 |
| 邏輯 | P9 | 結尾沒有回答 long read 版怎麼產生 | 結尾改成「沿用三步、改寫兩步、新增 germline SNP 與 HP」 |
| 邏輯 | P1、P9 | 會議 P0-2 的 HP 小型產出沒交代 | 封面講稿與 P9 進度列說明尚未實作 |
| 邏輯 | P8 | 假 SNV 的 VAF 0.24 撞到 SNV9 的 0.25 | CCF 改成 0.85，VAF 0.34，和各 clone 的 CCF 都不同 |
| 邏輯＋教授 | P5 | 放置規則和 P6 矛盾，也不精確 | 改成「嚴格後代不放；本身、祖先、旁支可放」，並註明 mutation loss 例外 |
| 邏輯 | P7、P8 | 違反 T-12（三個 sample） | 只放一個 sample |
| 邏輯 | P8、P9 | 觀眾可能以為用 short read 資料當輸入 | 標「重跑核對用，不當輸入」；P9 寫明只沿用程式設計 |
| 邏輯 | P3 | Noise／No-Noise 未定義；「五步」與第六張卡不一致 | P3 定義兩組；標題改成「五步＋Noise 組多兩步」 |
| 邏輯 | P2 | 「沒有」缺搜尋範圍；缺需求；缺 single cell 路徑 | 加範圍、需求列、single cell 一句 |
| 邏輯＋教授 | P4 | 「一半」不是程式規則 | 標題改「一部分」，講稿補上限 0.9、實際 0.85 |
| 邏輯 | P7 | c1 沒被選的原因；術語未定義 | 補選 clone 規則；定義 CCF、VAF、Dirichlet、WGD、cnLOH |
| 教授 | P8 | 假 SNV 是改標既有位置，不是額外加 | 改寫例子與講稿：保留 depth 與 copy number，只重新產生 alt |
| 教授 | P8 | 假 SNV 的 VAF 分母不是固定 2 | 例子註明前提：2 份、multiplicity 1 |
| 教授 | P8 | LTXSIM001 數值 | 改成 1070 個位置（61 個假 SNV）、truncal 群 854、purity 0.28 |
| 教授 | P6 | truncal SNV 也會被選；WGD 時不一定消失；10–25% 會被截 | 標題改「變少或消失」，講稿補三點 |
| 教授 | P3 | 「參數分布照真實病人」不對 | 改成「範圍取自摘要表（目前附的是模擬版）」 |
| 教授 | P5 | 事件種類不完整 | 講稿列出 loss 只有 loss B 與 cnLOH；A 的 loss 只用於 mutation loss |
| 教授 | P9 | A＝HP 的推論太快；缺 germline SNP | 改寫推論，germline SNP 列為新增需求 |
| 教授 | P2 | 重跑缺但書 | 補 coverage 與 mutation loss 比例是搜尋值 |
| 教授 | P7 | 「低估 CCF」不精確 | 改成「CCF 和 c3 這群不符，可能被分錯群」 |
| 教授 | 來源 | 路徑與版本 | 改成 `tool_8c8d173/src/`，註明本地 `facd2d7` 模擬函式相同 |

## 沒照改

- 「隨機亂數產生」→「隨機抽樣」：T-13 禁用「抽」。保留原寫法。
- 「假 SNV」→「noise SNV」：T-10 禁用「雜訊」。保留「假 SNV」，資料組名保留「Noise 組」。

## 待使用者決定

- T-12：只講一個 sample，不提 sample 分組。
- 頁數 9 頁。

# 第二輪審查（v5.2 → v5.3，2026-10-22）

使用者先決定：只講一個 sample；不講 Noise 組；保留「隨機亂數產生」。兩位審查者結論都是「需修改後再審」，問題都是局部的。主 agent 核對了文獻篇數（`research/literature/paper_categories.tsv` 共 19 份、C3b 2 篇）。

| 來源 | 頁 | 問題 | 改法 |
|---|---|---|---|
| 邏輯 | P2 | 「21 篇沒找到 long read 真值樹」和分類表不符 | 改成 19 份；2 篇有 long read＋single cell，但沒有用完整 sc 真值樹量化評估 SNV clone tree |
| 邏輯＋教授 | P8 | 第 0 步標「沿用」不成立；標題與結尾步數不一致 | 第 0 步改「改寫」（ONT coverage、read 長度）；標題加「參數」；結尾改「沿用兩步、改寫三步」 |
| 邏輯 | P5 | 「一般版本不會…」暗示另一版本 | 改成「程式不會丟掉帶 SNV 的 A」 |
| 邏輯＋教授 | P5 | c1 不能放 subclonal CNA（`evolution.py:198` 排除 initial_cc） | 小圖只列 c3 本身與 c2 旁支；講稿補 truncal 事件放 c1 |
| 邏輯 | P3 | A／B、Poisson、二項分布先用後解釋 | P3 講稿各補一句 |
| 邏輯 | 例子 | CCF 數值是 Noise 殘留 | 刪掉 |
| 教授 | 全冊 | 「真實座標」誤導（隨機撒點、hg18、REF／ALT 隨機） | 改成隨機座標；P8 新增「座標與 REF 對到 GRCh38」 |
| 教授 | P7 | 輸出表含真值 CLUSTER 與 CCF | 講稿補「給工具前要拿掉這兩欄」 |
| 教授 | P7 | 13 個 clone | 改成 13 個腫瘤 clone＋normal |
| 教授 | P6 | 選 clone 規則 | 改成「先放全部 leaf，再補到 3–8 個」 |
| 教授 | P5 | WGD、cnLOH 先後也影響 multiplicity；一個位置最多一個 CNA | 講稿補上 |
| 教授 | 例子 | 8–30 個節點 | 改成 8–29 個腫瘤 clone |
| 教授 | 來源 | 一般版本不是 `make_tx_simulations` 預設產生 | BRIEF 來源補推論；重跑用 `_info.tsv` 參數 |

不上頁面、只記 BRIEF：LTXSIM001 有 3 個 sample，R1 不含全部 leaf（T-12，使用者決定只講一個 sample）。
