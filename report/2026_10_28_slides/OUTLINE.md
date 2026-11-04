# 2026-10-28 簡報大綱 v5.5：CONIPHER 的模擬資料怎麼一步步產生

狀態：v5 經 P-1 兩方審查（`REVIEW_v5.md`）→ v5.1。2026-10-22 使用者決定三點 → v5.2。第二輪審查 → v5.3（`REVIEW_v5.md` 第二輪）。使用者要求先不談 long read → v5.4（已製作）。2026-10-22 使用者指出第 0 步沒有展開頁 → v5.5 新增 P4「定參數」，全冊 8 頁。
v4.1（PhyClone 測試工具版）備份為 `OUTLINE_v4.md`；製作前依 P-11 備份本地 `project/` 與線上版。
規則：`report/report_rule.md`。主軸來源：`research/meeting_record/2026_10_21_meeting_summary.md`。

## 使用者決定（2026-10-22，B-1）

1. 只講一個 sample（T-12）。不提 sample 分組。
2. 先不講 Noise 組，只講一般版本（No-Noise 組）。mutation loss 與假 SNV 移到文末「保留在計畫，不上投影片」（C-18）。
3. 用語：保留「隨機亂數產生」（T-13）。
4. 先不談 long read，只把 CONIPHER 的生成流程講好（使用者原話：「long read先不要想，先好好把conipher的生成流程講好再說」）。原 P8（long read 版）與 P2 的需求列移到「保留在計畫，不上投影片」。

## 主問題

一個公開、能重現的模擬器（CONIPHER benchmark 的生成器），怎麼一步步產生建樹的驗證資料？

- 使用者原話（2026-10-22）：「把這簡單生成流程例子，重新製作 2026_10_28_slides 的報告，作為下周的主要大綱，但其中白話可以恢復成生物術語的，並用簡單例子來表示整體模擬資料生成過程」。
- 會議整理第 1 節：老師要「能具體說明怎麼產生的」驗證資料。本次只回答「怎麼產生」；long read 版留到下次（使用者決定 4）。

## 為什麼換成 CONIPHER 生成器（和 v4 的差別）

- v4 講 PhyClone repo 的測試工具。重跑發現它不是作者產生 benchmark 的程式。在 PhyClone repo（commit `2738324`）與論文補充文件內，沒找到作者的生成程式〔實測：`lab_report/2026-10-21_phyclone_sim_rerun/`〕。
- CONIPHER benchmark 的生成器 `zaccaria-lab/TRACERx_simulation_tool` 完整公開。一般版本用記錄的種子重跑，150／150 份的 6 個輸出檔逐 byte 相同。但書：coverage 沒有記錄，是搜尋出來的值〔實測：`lab_report/2026-10-22_pairtree_conipher_sim_rerun/`〕。
- 它有 allele-specific copy number、SNV 與 CNA 的先後、purity 小於 1〔程式〕。座標與 REF／ALT 是隨機產生的，不對應參考序列（`conversion.py`，長度表是 hg18）。

## 全冊示意例子（E-1、E-2）

頁面一律用這個例子，標「示意」。程式實際產生 8–29 個腫瘤 clone 的樹，5 個節點只為了好講。真實產出 LTXSIM001（一般版本）只放 P7 的「實際結果」列與講稿。

- 樹（5 個節點）：normal → c1（truncal clone）；c1 → c2、c3；c3 → c4。leaf 是 c2、c4。
- SNV（10 個）：
  - normal→c1 枝（truncal）：SNV1–SNV5。
  - c1→c2：SNV6、SNV7。c1→c3：SNV8、SNV9。c3→c4：SNV10。
- copy number 事件（2026-10-22 使用者在編輯器改成 subclonal 例子，放在 SNV 出生的 clone）：
  - SNV6（c2）：先 SNV、後爸爸 gain → multiplicity 2。
  - SNV8（c3，c4 繼承）：先爸爸 gain、後 SNV → multiplicity 1。
- 一個 sample：purity 0.8。clone 比例 c2 0.30、c3 0.20、c4 0.30、normal 0.20。c1 沒被選進這個 sample（程式從 normal 以外的全部 clone 隨機選，內部節點也可能被選）。
- 期望 VAF（手算，示意）：
  - SNV1：0.8×1 ÷ 2 = 0.40。
  - SNV6：0.30×2 ÷ 2.3 = 0.26（2.3＝0.2×2＋0.3×3＋0.2×2＋0.3×2）。
  - SNV8：0.50×1 ÷ 2.5 = 0.20（2.5＝0.2×2＋0.3×2＋0.2×3＋0.3×3）。
  - 輸入表的爸份數是腫瘤細胞平均：SNV6 (0.3×2＋0.5×1)÷0.8＝1.38；SNV8 (0.3×1＋0.5×2)÷0.8＝1.63。
  - SNV10：0.30 ÷ 2 = 0.15。
- 定序（示意）：coverage 400。SNV1 depth 397、alt read 159。

## 標題串讀（W-3）

1. CONIPHER 的模擬資料怎麼一步步產生？
2. 上次問模擬資料怎麼產生：用公開、能重現的 CONIPHER 生成器逐步回答
3. CONIPHER 生成器分五步：定參數、建樹、放事件、混合 clone、產生 read count
4. 定參數：clone 數在固定範圍內隨機產生，其他參數從病人摘要表隨機選
5. 建樹與放 SNV：一部分 SNV 放在 truncal 枝，其餘分到各 subclone 枝
6. SNV 和 copy number gain 的先後，決定 SNV 的 multiplicity
7. 產生 read count：clone 依比例混合，每個位點各自隨機亂數產生 depth 與 alt read
8. 輸出：每個 SNV 一列 read count，加上真值樹與每個 SNV 所屬的 clone

## 證據層級（C-7，全冊適用）

- 〔程式〕`TRACERx_simulation_tool` commit `8c8d173`（重跑用的版本）。本地 submodule 是 `facd2d7`，模擬函式和 `8c8d173` 相同，只差輸出路徑。行號見文末「來源」。
- 〔實測〕重跑報告：一般版本 150／150 份 6 個檔相同。
- 〔論文〕CONIPHER 論文 Methods 有付費牆，沒有讀到。頁面的流程依據程式行為。
- 〔推論〕標在講稿。

## P1 這週大綱（2026-10-23 依 W-4 取代封面）

- eyebrow：這週大綱
- 標題：「這週回答：CONIPHER 的模擬資料怎麼一步步產生？」
- 內文（只有文字）：三列，依頁序：
  - 上次的問題：模擬資料怎麼產生：用公開、能重現的 CONIPHER 生成器回答（第 2 頁）
  - 生成流程：五步：定參數、建樹、放事件、混合 clone、產生 read count（第 3–7 頁）
  - 輸出：每個 SNV 一列 read count，加上真值樹與 SNV 所屬的 clone（第 8 頁）
- 講稿（L-1、L-5）：這週要回答的問題與三段大綱；步驟是自己讀生成程式整理的；全篇例子 SIM004、5 個節點的小樹，標「示意」。

## P2 標題：「上次問模擬資料怎麼產生：用公開、能重現的 CONIPHER 生成器逐步回答」

- eyebrow：0 · 上次的問題
- 圖：
  - 中間左右兩欄（F-5）：
    - 左「PhyClone 作者的 benchmark」：生成程式「沒找到」（斜線底）；範圍：PhyClone repo 與論文補充文件。
    - 右「CONIPHER 的 benchmark」：生成程式「公開」；重跑 150／150 份輸出相同（實際結果）。
  - 下方三格徽章（L-3）：真值來源＝模擬；讀長＝short read，只有 read count；生成程式＝公開。
- 講稿：
  - 第一句（L-3）：CONIPHER benchmark 的真值來自模擬，是 short read 的 read count，沒有 read。生成程式公開，所以可以一步步拆開來看。
  - PhyClone 作者的生成程式，在 PhyClone repo 和論文補充文件裡沒找到（L-6）。
  - 「重跑相同」：同一個程式、同一個種子，150 份的輸出一個 byte 都不差。coverage 沒有記錄，是我們搜尋出來的值。
  - 橋接：「它怎麼產生資料？先看全貌」。

## P3 標題：「CONIPHER 生成器分五步：定參數、建樹、放事件、混合 clone、產生 read count」

- eyebrow：1 · 生成流程
- 圖（F-9、C-18，2026-10-23 重新設計）：五張卡橫排加箭頭。每張卡：步驟名稱＋一張示意圖（畫出這一步的輸出）＋一個短語圖說。標「示意」，數字用 SIM004。
  - 第 1 步：五個參數條（clone 數 4、SNV 數 1405、purity 0.59、coverage 625、WGD 無）→「一組參數」
  - 第 2 步：小樹 normal→c1→{c2, c3→c4} →「真值樹」
  - 第 3 步：同一棵樹，每條枝一條紅色短線（SNV）；c2 左邊一疊 [SNV][SNV][媽]（同 P6 的 SNV6）→「每個 clone 的 copy number 與 SNV」
  - 第 4 步：直立比例條 normal 41%、c2 22%、c3 15%、c4 22%，右側括號標 purity 0.59 →「一個 sample 的細胞組成」
  - 第 5 步：SNV1 位點上 6 條 read（2 紅點 alt、4 白點 ref），標 depth 618、alt 181 →「read count 表」
  - 下方分組括號：前三步藍色「產生真值」；後兩步橘色「產生觀察到的資料：read count」。
  - 下表四欄（L-8）不上頁面，放講稿與本大綱。

  | 步 | 輸入 | 做什麼 | 輸出 | 假設 |
  |---|---|---|---|---|
  | 0 定參數 | 病人摘要表 | 隨機亂數產生 clone 數、SNV 數、purity、coverage、WGD | 一組參數 | 範圍取自摘要表（目前附的是模擬版） |
  | 1 建樹 | clone 數 | 隨機二分，再剪 leaf | 真值樹 | 樹形隨機 |
  | 2 放事件 | 樹＋SNV 數 | 把 SNV 與 copy number 事件放到枝上 | 每個 clone 每個位置的 A 份數、B 份數、SNV 份數 | 後代繼承祖先事件 |
  | 3 混合 clone | 樹＋purity | 隨機亂數產生 clone 比例 | 一個 sample 的細胞組成 | 每個 leaf 都被看到 |
  | 4 產生 read count | 細胞組成＋coverage | Poisson 產生 depth；二項分布產生 alt read | read count 表 | 位點之間各自獨立 |

- 講稿：
  - 結論，再從左到右一步講完再講下一步（S-10）。
  - clone：帶同一組突變的一群腫瘤細胞。purity：sample 裡腫瘤細胞的比例。coverage：每個位點平均被讀到幾次。WGD：整個基因組加倍。
  - A、B 是同一段染色體的兩個 allele，下一頁詳細講。Poisson：產生「平均是某個值」的隨機整數。二項分布：每條 read 以固定機率帶 alt，數總共幾條。
  - 第 0 步的參數範圍來自 TRACERx 肺癌病人的摘要表。程式附的摘要表是隨機模擬的版本，不是真實病人。每份資料都記錄了實際用的參數，重跑就是用這些記錄的參數。
  - 橋接：「從第 1 步開始，用一棵 5 個節點的小樹走一遍」。

## P4 標題：「第 1 步：先隨機產生五個參數，每個參數控制後面一步」（2026-10-22 新增；2026-10-23 改成示意圖）

- eyebrow：1 · 生成流程；標「示意」。
- 圖（F-9、C-18）：
  - 上排五張參數卡，每張：名稱＋範圍｜例子值（SIM004）｜一張小圖｜「→ 第 N 步：控制什麼」。
    | 參數 | 範圍 | 例子 | 小圖 | 控制 |
    |---|---|---|---|---|
    | clone 數 | 8–29 | 4 | c1–c4 四個節點 | 第 2 步：樹的大小 |
    | SNV 數 | 175–1793 | 1405 | 基因組線上 10 條紅線 | 第 3 步：SNV 有幾個 |
    | purity | 0.21–0.81 | 0.59 | normal 41%｜腫瘤 59% 比例條 | 第 4 步：腫瘤細胞比例 |
    | coverage | 319–662 | 625 | 一個位點上疊的 read | 第 5 步：平均 depth |
    | WGD | 三選一 | 無 | 無／clonal／subclonal 三顆膠囊，「無」反白 | 第 3 步：基因組加倍 |
  - 下排「WGD 細節：放在哪個 clone、影響什麼」：
    - 左：三棵小樹（同全冊的 normal→c1→{c2, c3→c4}），加倍的 clone 加黑框，WGD 膠囊放在 WGD 發生的 clone 旁。
      - 無（50 位中 9 位）：每個位置 2 份。
      - clonal（17 位）：WGD 在 c1，c1–c4 全部加倍。
      - subclonal（24 位）：隨機選 1 個 subclone（不含 c1），例子選 c3，c3、c4 加倍，c2 不變。
    - 右：表「順序（clonal）｜爸、媽份數｜multiplicity｜VAF」（purity 0.59）：
      - 沒有 WGD：SNV／媽，1，0.30
      - SNV → WGD：SNV／SNV／媽／媽，2，0.37
      - WGD → SNV：SNV／爸／媽／媽，1，0.19
      - 下兩行：subclonal 時 WGD 前的 SNV 在 c3、c4 有 2 份、在 c2 只有 1 份；depth 平均不變。
- 講稿：clone 數依病人資料分三組（8–15、12–23、22–29）；其他四個參數各自從摘要表隨機選，不一定來自同一位病人；SNV 數只選大於 150；purity 上下限在第 4 步才產生單一值；truncal 比例與 gain／loss 比例也從表裡選。WGD 細節照上面的圖講。橋接：「參數定好了，接著第 2 步建樹」。
- 程式（2026-10-23 核對）：
  - 參數：`make_simulation.py` `make_tx_simulations`（clone 數範圍、分組）與檔尾 `nmutations`、`purity`、`coverage`、`wgd`、`muttruncal`、`cna`；每個參數各自呼叫 `np.random.choice`。purity 的單一值在 `sequencing.py` `all_samples`。範圍與 WGD 次數：`simulated_TRACERx_data.tsv`（50 位病人：subclonal 24、clonal 17、False 9）。
  - WGD 放置：`evolution.py` `wgd_assignment`。clonal：`wgd[initial_cc]` 放在每個位置；subclonal：`np.random.choice(subclone_nodes, n_subclonal_wgd)`，`n_subclonal_wgd = subclonal*1 = 1`；`subclone_nodes` 不含 root 與 initial_cc（`cna_assignment`）。
  - WGD 作用：`generate_events` 的 `wgd = x * 2`，爸、媽、SNV 份數全部 ×2。`concat_all_events` 把同一 clone、同一位置的事件隨機排序；`set_profiles` 把 clone 的事件套到它和全部後代。
  - VAF：`calculate_vaf`，VAF＝Σ 比例×SNV 份數 ÷ Σ 比例×總份數（含 normal 2 份）。0.59×2／(0.59×4＋0.41×2)＝0.37；0.59／3.18＝0.19；沒有 WGD 0.59／2＝0.30（主 agent 手算）。
  - depth：`get_total_reads`，Poisson 平均＝各位置的份數 × coverage ÷ 全部位置份數的平均，所以平均 depth＝coverage，WGD 讓全部位置一起加倍時不改變 depth。

## P5 標題：「建樹與放 SNV：一部分 SNV 放在 truncal 枝，其餘分到各 subclone 枝」

- eyebrow：1 · 生成流程
- 圖：左右兩欄，標「示意」。
  - 左「第 1 步 建樹」：兩張小圖。(a) 隨機二分出的大樹；(b) 剪掉多的 leaf 後剩 normal → c1 → c2、c3 → c4。
  - 右「第 2 步 放 SNV」：同一棵樹，枝旁寫 SNV 名稱。normal→c1 枝寫 SNV1–5，標「truncal」；其他枝寫 SNV6–7、SNV8–9、SNV10，標「subclonal」。
- 講稿：
  - 結論：樹的形狀完全隨機；SNV 依 truncal 比例分兩堆。
  - 最上面的 normal 是正常細胞，混樣時代表正常細胞混入。c1 是第一個腫瘤 clone。
  - truncal SNV：所有腫瘤細胞都有。subclonal SNV：只有某一支和它的後代有。
  - 程式把 subclonal SNV 隨機切段，每條枝至少 1 個。
  - truncal 比例依摘要表隨機亂數產生，上限 0.9。例子用一半；實際資料 LTXSIM001 是 0.55。
  - 橋接：「SNV 放好了，接著放 copy number」。

## P6 標題：「SNV 和 copy number gain 的先後，決定 SNV 的 multiplicity」

- eyebrow：1 · 生成流程
- 圖：上方一行規則：「每個位置記三個數：A 份數、B 份數、帶 SNV 的份數；SNV 一律放在 A 上」。
  - 中間左右兩欄（F-5），細胞示意（BIO_DRAWING_RULES D 節）：
    - 左「SNV6：先 SNV，後爸爸 gain」→ multiplicity 2。
    - 中「SNV8：先爸爸 gain，後 SNV」→ multiplicity 1。
    - 右：樹上 c2、c3 旁放兩張卡的最後狀態；後代 c4 不放（2026-10-22 使用者留言改版；三數組已依使用者要求刪除）。
  - 最下一列小圖：SNV8 位置上的 copy number 事件可放在哪些 clone。c3 本身、c2 這類旁支可以放；c4 這類後代不放 → 帶 SNV8 的細胞 multiplicity 都一樣。
- 講稿：
  - 結論：同一種 gain，先後不同，帶 SNV 的份數就不同，VAF 也不同。
  - allele：同一段染色體的兩個版本，一份來自父親、一份來自母親。copy number：這段有幾份。multiplicity：幾份帶 SNV。
  - 同一個 clone、同一個位置的事件，程式隨機排序，所以先後是隨機的。WGD 和 cnLOH 也一樣：發生在 SNV 之後，帶 SNV 的份數會跟著增加。
  - 一個位置最多只有一個 copy number 事件，WGD 另計。truncal 事件放在 c1；subclonal 事件放在 c1 以下的 clone。
  - 事件種類：gain A、gain B、兩邊都 gain、loss B、cnLOH（copy-neutral LOH：丟掉 B、A 多一份，總份數不變）、WGD。程式不會丟掉帶 SNV 的 A，所以 SNV 一旦出現，後代都保留。
  - 這是程式行為。真實腫瘤的 copy number 是一整段染色體一起變；這個程式每個位置各自決定，這是簡化（推論）。
  - 橋接：「每個 clone 的狀態都定好了，下一步把 clone 混成一個 sample」。

## P7 標題：「產生 read count：clone 依比例混合，每個位點各自隨機亂數產生 depth 與 alt read」

- eyebrow：1 · 生成流程
- 圖：三段，由左到右，標「示意」。
  1. 細胞組成長條：normal 20%｜c2 30%｜c3 20%｜c4 30%。規則列：「腫瘤 clone 比例＝Dirichlet × purity；normal＝1 − purity」。
  2. 期望 VAF 表（四列）：SNV1 0.40、SNV6 0.26、SNV8 0.20、SNV10 0.15。上方一行公式：「VAF＝Σ 比例×SNV 份數 ÷ Σ 比例×總份數」。
  3. read count：SNV1 的一條 depth 長條，397 條 read，其中 159 條 alt。規則列：「depth ~ Poisson；alt ~ 二項分布」。
- 講稿：
  - 結論：VAF 由細胞組成、copy number 和 multiplicity 一起決定；read count 只是在 VAF 上加隨機性。
  - VAF：帶 SNV 的 read 佔全部 read 的比例。Dirichlet：把總和固定的比例隨機切成幾份。
  - 程式先放入全部 leaf，再從其他 clone 隨機補到 3–8 個，內部節點也可能被選。例子補了 c3，沒選到 c1。
  - SNV6 只在 c2 但有 2 份帶 SNV → 0.26；SNV8 在 c3＋c4 但只有 1 份、總份數 3 → 0.20。
  - SNV8 在 c3 和 c4 裡都有，所以比例加起來是 0.50。
  - depth 依該位置的總份數調整，份數多的位置 read 多。
  - 程式只產生 read count，不產生 read 序列。
  - 橋接：「最後，程式交出哪些檔？」

## P8 標題：「輸出：每個 SNV 一列 read count，加上真值樹與每個 SNV 所屬的 clone」

- eyebrow：1 · 生成流程
- 圖：左右兩欄（F-13 的「題目／答案」對照）。
  - 左「給建樹工具的輸入」（示意）：read count 表 4 列（SNV1、SNV6、SNV8、SNV10），欄：位置、alt、depth、爸份數、媽份數、purity（SNV6、SNV8 的爸份數 1.38、1.63）。
  - 右「藏起來的真值」（示意）：例子的樹；每個 SNV 屬於哪個 clone；clone 比例。
  - 下方「實際結果」列（L-9），標「重跑核對用，不當輸入」：LTXSIM001 的兩個檔。
    - 真值樹縮圖：13 個腫瘤 clone＋normal，有 WGD；truncal 枝 535 個 SNV。
    - read count 表第 1 列：chr11:79841933，alt／depth＝105／691，purity 0.42。
    - 參數：972 個 SNV。
  - 最下一行：五步縮圖（沿用 P3 的五格），收尾回到主問題。
- 講稿：
  - 結論：建樹工具只該拿到左邊的 read count 與 copy number；右邊的樹和 SNV 歸屬是評分用的答案。
  - 程式輸出的表其實把 SNV 所屬 clone 和 CCF 也寫在同一個檔裡。給建樹工具前，要先拿掉這兩欄。
  - 實際的檔裡，每個 SNV 都有座標、REF／ALT、A 和 B 的份數、purity。座標依染色體長度隨機撒在 chr1–22，REF／ALT 也是隨機選的，不對應參考序列。
  - 這份資料只拿來核對重跑。
  - 收尾（回到 L-1）：回到老師的問題，模擬資料就是這五步產生的：定參數、建樹、放事件、混合 clone、產生 read count。每一步的程式位置我都核對過，也重跑出一樣的結果。

## 保留在計畫，不上投影片（2026-10-22 使用者決定）

Noise 組（150 份）比一般版本多兩個步驟。使用者要求時再加頁。內容已核對程式與重跑結果（v5.1 審查）：

- **mutation loss**（第 2 步內）：程式在 SNV 所在枝的嚴格後代 clone 上放 loss A 或 cnLOH A，拿掉一份帶 SNV 的 A。2 份的位置 SNV 會消失；有 WGD 時只會變少。leaf 枝上的 SNV 不會被選；`mutloss_truncal` 為 True 時優先選 truncal SNV。目標比例 0.10–0.25，會被 `get_npos_cnas` 上限截掉（重跑 20／150 份）。違反 infinite sites。示意：c4 在 SNV8 的位置 loss A → SNV8 的 VAF 從 0.25 變 0.12。
- **假 SNV**（第 4 步之後）：程式先模擬 n_positions＋n_noise 個位置，再隨機挑 n_noise 個改標成假 clone。depth 與 copy number 保留；每個 sample 的 CCF 在 0.01–0.99 隨機；VAF＝max(multiplicity,1)×CCF×purity ÷ 該位置總份數；只重新產生 alt read。比例 0.05–0.10。示意：SNV11（truncal）改標，CCF 0.85 → VAF 0.34。
- Noise 組實際結果 LTXSIM001：1009＋61 個位置、truncal 群 854、purity 0.28、mutation loss 0.20。

## 保留在計畫，不上投影片：long read 版（2026-10-22 使用者決定 4）

使用者要求先講好 CONIPHER 生成流程。以下原 P8 與 P2 需求列內容已經兩輪審查，之後要談 long read 時再用。

- 原 P2 需求列：「我們要的驗證資料：long read、有真值樹、有 HP、有同 read 共現」；「只當範本：學它怎麼產生，不用它的資料」。
- 原 P2 講稿（L-7）：在 19 份文獻內，有 2 篇同時用 long read 和 single cell，但沒找到用 long read 重建 SNV clone tree、再用完整 single-cell 真值樹量化評估的研究。

### 原 P8 標題：「我們的 long read 版：沿用建樹與 clone 混合，改寫參數、事件與 read 產生，新增 germline SNP 與 HP」

- eyebrow：2 · long read 版
- 圖：上段需求表（L-2），下段沿用 P3 的五步表加一欄「沿用／改寫／新增」（L-8）。
  - 需求表，✓／✗ 加文字（F-5）：

    | 需求 | CONIPHER 生成器 |
    |---|---|
    | 真值樹 | 有 |
    | allele-specific copy number | 有 |
    | long read 序列 | 無 |
    | germline SNP（phasing 用） | 無 |
    | HP1／HP2 | 無 |
    | 同 read 上的 SNV 共現 | 無 |
    | 座標與 REF 對到 GRCh38 | 無 |

  - 五步表加欄：

    | 步 | 標籤 | 做什麼 |
    |---|---|---|
    | 0 定參數 | 改寫 | coverage 與 read 長度改成 ONT 的範圍 |
    | 1 建樹 | 沿用 | 同原程式 |
    | 2 放事件 | 改寫 | copy number 一整段一起變；SNV 可放在 A 或 B |
    | 3 混合 clone | 沿用 | 同原程式 |
    | 4 產生 read | 改寫 | 產生跨多個位點的 read，帶 HP 與共現 |
    | 新 | 新增 | 座標與 REF 對到 GRCh38；放 germline SNP；加入 phasing 錯誤 |

  - 最下一行（L-9）：「目前進度：CONIPHER 流程已讀懂並重跑；long read 版尚未實作。下一步：用一棵小樹產生帶 HP 的模擬資料。」
- 講稿：
  - 結論：建樹和 clone 混合照搬；參數範圍、事件和 read 產生要改寫；germline SNP 與 HP 要新增。
  - 參數：原 coverage 取自 short read 的摘要表，是數百 x；ONT 要改成我們資料的深度，並加上 read 長度。
  - 只沿用程式設計，不用 CONIPHER 的資料或真值樹。
  - 程式有輸出 A 和 B 的份數，但每個位置的 A、B 各自獨立，位置之間沒有連起來。所以 A 不等於某一個 HP。要先讓 copy number 一整段一起變，A、B 才能對到 HP1、HP2（推論）。
  - germline SNP：正常細胞就有、父親和母親版本不同的位點。longphase 靠它把 read 分到 HP1 或 HP2，原程式沒有產生。
  - read 產生改成：從細胞組成選一個細胞、選一份 allele，再切出一條跨多個位點的 read。這樣 read 就自帶 HP 與共現（推論）。
  - phasing 錯誤：phasing 區塊的邊界，以及區塊內 HP1、HP2 對調。
  - 座標要對到 GRCh38，read 才能和真實 reference 比對。
  - 請老師決定：先只產生 read count 層的 HP 與共現，還是直接產生 read 序列？
  - 回到老師的問題：模擬資料就是這五步產生的；我們的 long read 版沿用其中兩步，改寫三步，再新增 germline SNP 與 HP。


## 來源（記入 BRIEF）

- 程式（`TRACERx_simulation_tool` commit `8c8d173`，`/big8_disk/boyu114/phyclone_dataset/CONIPHER_rerun/tool_8c8d173/src/`；本地 submodule `facd2d7` 的模擬函式相同）：
  - 參數：`make_simulation.py`（讀 `simulated_TRACERx_data.tsv`；節點範圍；truncal 比例小於 0.9）。
  - 建樹：`topology.py` `make_tree`、`prune_tree`。
  - SNV：`evolution.py` `snv_assignment`；CNA：`cna_assignment`、`assign_cnas`、`prevent_subclonal_cnas`（嚴格後代除外，`get_descendants(...)[1:]`）；事件：`generate_events`（loss 事件預設只有 loss_B、cnloh_B）；先後隨機：`concat_all_events`。
  - 混合與 read count：`sequencing.py` `simulate_sample_leaves`、`all_samples`、`calculate_vaf`、`get_total_reads`、`get_variant_reads`。
  - 座標：`conversion.py` `assign_chr_pos_correct`。
- 一般版本的產生方式：`make_tx_simulations` 預設一律開 mutation loss（≥0.1）與假 SNV（≥0.05），所以一般版本是關掉這兩項後產生的（推論）。重跑用 `_info.tsv` 記錄的參數直接呼叫 `tx_simulation`。
- 實際結果的但書（不上頁面，T-12）：LTXSIM001 有 3 個 sample，頁面只取 R1。R1 只含 clone 1、15、16，不含全部 leaf；單一 sample 時程式才會放入全部 leaf。
- 實測：`lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md`；一般版本 LTXSIM001：`/big8_disk/boyu114/phyclone_dataset/CONIPHER_rerun/No-Noise_sim/LTXSIM001/sim/`（2026-10-22 讀取：13 個 clone、972 個 SNV、truncal 枝 535、clonal WGD、prop_truncal 0.55、第一個 sample purity 0.42、第 1 列 chr11:79841933 alt 105／depth 691）。

## 2026-10-22 使用者在編輯器與留言的後續改版（以線上版為準）

- 全篇例子統一用病人 SIM004（摘要表模擬版）：SNV 數 1405、purity 0.59、coverage 625、WGD 無；clone 數例子 4；圖只畫 10 個 SNV。
- clone 比例（purity 0.59）：normal 41%、c2 22%、c3 15%、c4 22%。期望 VAF：SNV1 0.30、SNV6 0.20、SNV8 0.16、SNV10 0.11；SNV1 depth 618、alt 181；P8 爸份數 SNV6 1.38、SNV8 1.63（主 agent 驗算）。
- 第 4 頁簡化為「第 1 步：先隨機產生五個參數」（五張卡：範圍＋例子），拿掉病人表格。全冊步驟編號改為 1–5：1 定參數、2 建樹、3 放事件、4 混合 clone、5 產生 read count。
- 選 SIM004 的理由：WGD 無。選 clonal WGD 的病人會讓所有位置份數加倍、truncal SNV 的先後也加入 WGD，第 6–8 頁要重畫。

## 2026-10-23 拿掉封面（W-4）

- 使用者新增規則：不做封面，第 1 頁直接寫這週的大綱文字。P1 改成 `outline` 大綱頁，舊封面移到 `removed_slides/cover.html`。總頁數仍是 8。

## 2026-10-23 第 3 頁改成示意圖（F-9）

- 使用者要求：描述流程時搭配示意圖，比文字好懂。P3 由四行文字卡改成每步一張示意圖。舊版移到 `removed_slides/s1-overview_text_2026-10-23.html`。

## 2026-10-23 第 4 頁改成示意圖，加 WGD 細節（F-9、C-18）

- 使用者要求：第 4 頁也改成示意圖；WGD 要說明參數會影響什麼。上排五張參數卡各配小圖與「控制第幾步」；下排 WGD 細節（三種選項的放置位置、出現次數，以及對 copy number、multiplicity、VAF、depth 的影響）。標題改成「第 1 步：先隨機產生五個參數，每個參數控制後面一步」。舊版移到 `removed_slides/s1-params_text_2026-10-23.html`。

## 2026-10-23 線上版換帳號重建

- 原線上版（https://claude.ai/artifact/CLPQBjSsU2hnkBRM44Rvgw）屬於原帳號，目前登入的帳號打不開。用目前帳號另建新版：https://claude.ai/artifact/VD3N6zKfSawc7HCgoUZx6q（8 頁，內容＝本地 `project/`）。之後的修改發布到新版。

## 2026-10-23 第 4 頁刪「範圍」與 WGD 樹（C-18）

- 調查結果：程式只有 clone 數是寫死範圍（依 sample 數分三組 8–15、12–23、22–29）。其他參數各自從摘要表隨機選真實值，只有篩選門檻（purity>0.2、SNV 數>150、truncal 比例<0.9）。purity＝選兩個值當上下限，再 uniform。150 份實際資料超出附表（SNV 數最多 3437、purity 上限最大 0.92、clonal WGD 101／150），作者用的是另一份表（推論）。
- 使用者要求：刪掉全部參數「範圍」（第 2 頁「搜尋範圍」是 L-6 的搜尋範圍，保留）；WGD 只留「事件順序 × 爸媽 copy number × multiplicity × VAF」表，刪三棵樹、黑框圖例、subclonal 與 depth 兩行。WGD 標題改成「WGD：SNV 和 WGD 誰先發生，決定帶 SNV 的份數」。講稿改寫成沒有固定上下限的說法，並刪掉 50 位病人的 WGD 次數。

## 2026-10-23 WGD 改畫放置位置；使用者刪第 2 頁

- WGD 區塊重畫：無（不放）｜clonal（WGD ×2 在 normal→c1 枝上，c1 與全部後代灰底）｜subclonal（WGD ×2 在 c1→c3 枝上，隨機選 1 個 subclone，c3、c4 灰底），右側保留事件順序表，表上加「同一個 clone 裡，WGD 和 SNV 隨機排先後」。
- 使用者在編輯器刪掉 `s0-answer`（上次的問題）。舊頁移到 `removed_slides/s0-answer_2026-10-23.html`，全冊頁尾改成 n / 7，大綱頁刪「上次的問題」列，頁碼改成第 2–6 頁、第 7 頁。

## 2026-10-23 WGD 移到第 5 頁（s1-cn），加骰子

- 使用者選擇把 WGD 細節從定參數頁移到第 3 步放事件頁。第 3 頁只留五張參數卡。
- 第 5 頁新標題「copy number 事件的先後決定 multiplicity」。上：規則列（骰子＋「同一個 clone 裡，copy number 事件和 SNV 隨機排先後」）；中：SNV6、SNV8 兩張先後卡＋gain 放置小樹（SNV6、SNV8 最後狀態在 c2、c3 旁）；下：WGD「放在 c1，或從 subclone 中只挑 1 個」——無｜clonal（c1 起灰底，不畫骰子）｜subclonal（c2、c3、c4 虛線候選，挑中 c3 加 WGD 膠囊＋骰子，c3、c4 灰底）＋事件順序表。
- 程式核對：`n_subclonal_wgd = subclonal*1 = 1`；`np.random.choice(subclone_nodes, 1)`；22 份 subclonal 資料每份剛好 1 條 WGD 枝（中間節點 12、leaf 10）。舊版第 5 頁移到 `removed_slides/s1-cn_before_wgd_2026-10-23.html`。

## 2026-10-23 第 3 頁拿掉步驟編號（留言）

- 使用者留言：參數卡的「→ 第 N 步」會讓人誤會參數有順序。線上版已改：卡片只寫「→ 控制什麼」，標題改成「先隨機產生五個參數，每個參數各控制流程的一部分」，講稿加「五個參數之間沒有先後順序」。本地已同步（`build_s1_params.py` 產生的版本已過時，之後以本地檔為準）。

## 2026-10-23 第 3 頁改成六個參數

- 新增「gain／loss 比例」卡（SIM004：%PosGained 0.29、%PosLost 0.32、%GainTruncal 0.81、%LossTruncal 0.06；→ 單點 gain、loss、LOH）。WGD 卡改成「在 main clone 或一個 subclone 放 copy number gain（全部位置 ×2）」（以使用者編輯器的寫法為底）。六張卡排兩列，標題改成「先隨機產生六個參數…」。第 2 頁第 1 步卡加 gain／loss 一列，講稿改成六個參數。

## 2026-10-23 第 5 頁刪「gain 放在 SNV 出生的 clone」區塊（留言）

- 使用者留言要求刪除；線上版已刪掉該小樹與講稿中解釋它的句子（P-10），本地已同步。
