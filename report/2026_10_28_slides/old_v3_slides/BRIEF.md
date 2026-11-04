# 2026-10-28 簡報：共用規格（給每個段落 subagent）

Repo 根目錄：`/bip8_disk/boyu114/main_work`。Deck 根目錄 `ROOT=/bip8_disk/boyu114/main_work/report/2026_10_28_slides`。
每頁寫成 `ROOT/project/slides/<id>.html`。先讀 `report/report_rule.md`，遵守它。
逐頁內容唯一來源：`ROOT/OUTLINE.md`（v3，已通過三輪審查，使用者 2026-10-21 確認）。審查紀錄：`ROOT/REVIEW_v1.md`、`ROOT/REVIEW_v2.md`。
上一份簡報 `report/2026_10_21_slides/project/slides/` 可以參考版面，內容不能沿用。

## A. 內容規則

- 語言：繁體中文。技術名詞保留英文（SNV、CCF、clone、purity、HP、read、sample、root、LOH、germline SNP）。
- 文字用 ASD-STE100 風格：一句一件事、短句、主動語態、先結論再原因。
- 一頁一個重點。頁面文字照大綱「頁面文字」那行，不要另加。每個重點文字都要有對應的圖。
- 圖上文字只放名詞或短語。補充、限制、推論放講稿。
- **數字只用 `OUTLINE.md` 裡的數字。** 那些數字都已對過作者真實資料，不要改，不要自己算新數字。示意用的圖（例如 P6 左邊的建樹規則）要標「示意」。
- **全冊示意例子（2026-10-21 使用者指定，取代作者真實資料的例子）：** 頁面上一律用同一個 10 個 SNV 的假想例子，標「示意」。作者真實數字（600 個 SNV、9 群、root 291 等）只放講稿。
  - 分群：10 個 SNV → 4 群，c1 4 個、c2 3 個、c3 2 個、c4 1 個（前 3 個 SNV 照 P5 三段：開第 1 桌、進第 1 桌、開第 2 桌）。
  - 樹拓樸：c4 放入 → c3 加入 k＝1 接 c4 → c2 加入 k＝0 → c1 最後全接成 root。結果 c1→c3→c4、c1→c2。
  - clone 比例（Dirichlet 隨機，示意值）：c1 0.40、c2 0.25、c3 0.20、c4 0.15。CCF：c4 0.15、c3 0.35、c2 0.25、c1 1.00。
- 例外（2026-10-21 使用者指定）：第 2 頁（`s1-overview`）的兩個程式方框左上角寫程式檔名 `fscrp.py`、`sim_data_on_tree.py`，講稿可以唸出這兩個檔名。
- 黑話規則：頁面與講稿都不出現程式欄位名與函式名（`g_r`、`g_v`、`major_cn`、`tumour_content`、`simulate_tree`、`fscrp.py` 等）、檔案路徑、commit 編號、審查代號。用大綱的白話名稱：「較多那邊／較少那邊」、「帶突變的份數」、「突變在拷貝數改變之前／之後」。
  - 可以出現：中國餐廳過程（CRP）、二項分布、purity、CCF、LOH、germline SNP。第一次出現時照大綱「用詞首次出現頁」用一句白話解釋。
- 講稿：`<aside>` 純文字，中文約 200–300 字。口語、能直接念。先講結論，再沿著圖講原因。用位置、顏色、上面的字指路。大綱的講稿要點都要講到；橋接句照大綱。同一個但書全冊只講一次。
- 推論在講稿用口語標明：「這是我們的推論」。

## B. 視覺系統（全 deck 一致，不要改）

字體：
- 標題：`font-family:'Noto Serif TC', Georgia, serif; font-weight:700`
- 內文：`font-family:'Noto Sans TC', Arial, sans-serif`（寫在 section 上讓它繼承）
- 數字、公式：`font-family:'JetBrains Mono', 'Courier New', monospace`

字級（只用這五級）：96（封面標題）、64（頁標題 h2）、40（卡片標題 h3／大數字說明）、30（內文）、24（標籤、表格小字、頁尾）。

顏色：
- 深色字 `#1F2A37`；次要字 `#4A5568`；淡字（頁尾）`#6B7480`
- 背景 A（主要）`#F7F6F2`；背景 B（第二大段用）`#EEF2F6`；卡片底 `#FDFDFB`；卡片框線 `#D9DDE3`
- 強調 1（藍）`#2F6DB5`：「產生樹」的步驟（第一到三步）
- 強調 2（橘）`#C96A1B`：「產生 read 數」的步驟（第四、五步）
- 壞／警告 `#B4442F`；好／通過 `#2E7D4F`
- 深色宣告頁背景 `#1F2A37`，上面字 `#F7F6F2`，次要字 `#BFD0E0`
- 帶突變的染色體份數、突變標記：`#D23A2E`；沒帶突變的份數：`#9AA3AE`
- HP 固定配色：HP1 `#2C5F9E`、HP2 `#D9772B`、unphased `#9AA3AE`
- P2／P14／P15 標籤固定配色：沿用 `#2E7D4F`、修改 `#7B5EA7`、重寫 `#B4442F`、新增 `#4A5568`。標籤上一定寫字。藍、橘只代表「產生樹／產生 read 數」，不能再拿來當標籤色。（2026-10-21 依全冊邏輯檢查修改）
- 顏色不能單獨表達意思：旁邊一定要有文字。

貫穿全冊的固定圖示（同一概念全冊同圖）：
- 真實樹（P6、P7）：圓形節點，節點內寫 SNV 數；root 在上。不標任何 SNV 編號（2026-10-21 使用者要求刪除 m392 案例）。
- 細胞示意（P8、P9）：圓角方框代表一群細胞，裡面畫短橫條代表染色體份數，帶突變的份數為紅色，沒帶突變的為灰色。
- 五步流程（P4、P14）：五格（P14 為六格）橫向方塊加箭頭，第一到三格藍框，第四、五格橘框。

版面骨架（每張內容頁都一樣，位置不可跳動）：

```html
<section id="ID" style="background:#F7F6F2;color:#1F2A37;font-family:'Noto Sans TC', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:700;color:#2F6DB5;letter-spacing:2px">1 · 程式怎麼產生資料</p>
<h2 style="font-family:'Noto Serif TC', Georgia, serif;font-size:64px;font-weight:700;line-height:1.15;color:#1F2A37">頁標題（照大綱）</h2>
<div style="flex:1;display:flex;gap:40px"> …內容… </div>
<div style="position:absolute;left:128px;right:128px;bottom:64px;display:flex;justify-content:space-between">
<p style="font-size:24px;color:#6B7480">2026-10-28 PhyClone 模擬資料生成流程</p>
<p style="font-size:24px;color:#6B7480">NN / 15</p>
</div>
<aside>講者備註</aside>
</section>
```

- eyebrow：P2–P3 寫 `0 · 上次的問題`；P4–P10 寫 `1 · 程式怎麼產生資料`；P11–P14 寫 `2 · 能不能直接用`。封面、總結不放 eyebrow。
- 背景：P1 封面用深色 `#1F2A37`；P2–P10 用 `#F7F6F2`；P11–P14 用 `#EEF2F6`；P15 總結用深色 `#1F2A37`。
- 頁標題照大綱，最多兩行（64px 時一行約 25 個中文字）。
- 卡片：`background:#FDFDFB;border:1px solid #D9DDE3;border-radius:16px;padding:32px`，不設固定 height。
- 表格：`<table style="font-size:26px;color:#1F2A37">`，第一列 `<th>`，每格 `width:N%` 寫在第一列；表頭列 `<tr style="background:#E3E8EF">`。
- 可視區 1664×824（扣頁尾後內容約 y=128 到 y=920）。行高約 字級×1.4；表格列約 2.1×字級。放不下就刪字，不要縮字到 24 以下。
- 中文每字約 1×字級寬；英文約 0.6×字級／字元。卡片寬要容得下最長的英文字。

## C. 格式子集（違反會被丟掉）

- 只能有一個 `<section id="ID" …>`，id 等於檔名，前後不能有任何東西。不能有 `<html> <head> <style> <link> <script> class`。
- 所有樣式 inline。禁止：`margin`、`z-index`、`em`、`rem`、`%` 字級、`var()`、`float`、`grid-area`、colspan/rowspan、巢狀清單。
- 可用元素：`h1 h2 h3 p ul ol li br b i u span(只能設 color) a div img table tr th td svg hr x-shape x-icon x-connector aside`。
- `<x-shape kind="rect|rounded|ellipse|diamond|arrow-right|arrow-left|arrow-up|arrow-down|line" style="background;border;width;height">`；箭頭長寬比接近 2:1。
- `<x-connector x1 y1 x2 y2 head="end|both|none" route="straight|hv|vh|elbow" style="color:#…;border-width:3px">`：放在 `position:relative` 的 div 裡以 div 座標定位，或以 slide 座標定位。不能設 left/top/width/height。
- `<x-icon name>` 只能用：Activity Book Chart Chat Check CheckCircle Clock Cloud Code Database Globe GraduationCap Home Key Lightbulb Lightning Link Lock PaperPlane Play Search Settings Star ThumbsUp Tool Trust Users Verified Warning Wrench。
- `<svg aria-label width height viewBox>`：只畫圖形，不用 `<text>`。文字標籤用 pinned `<p>` 疊上去。svg ≤52KB。
- `position:absolute` 的子元素要給 width。一個 div 內最多 24 個 pinned 子元素。每頁最多 200 個元素，div 最多 15 層。
- 勾叉不用 ✓✗，用 `<x-icon name="Check">` 或文字「有／無」。
- 標點：中文用全形標點。

## D. 圖

不用舊圖。所有圖都用 div／x-shape／x-connector／svg 重新畫。
畫演化樹前讀 `report/VISUAL_SPEC.md` §1 與 `report/BIO_DRAWING_RULES.md` C 節；畫拷貝數前讀 `VISUAL_SPEC.md` §4 與 `BIO_DRAWING_RULES.md` D 節；P3、P13 的 HP 小圖讀 `VISUAL_SPEC.md` §3。

## E. 事實來源（給 BRIEF 追溯；頁面不出現）

- 程式：`research/simulation_pipeline_research/phyclone_sim_code/utilities/fscrp.py`（分群 L69–L101、建樹 L104–L155、比例 L7–L23）；`sim_data_on_tree.py`（拷貝數 L86–L95、時機 L42、帶突變份數 L104–L118、抽 read L121–L146）。上游 commit `2738324`。
- 論文：`research/simulation_pipeline_research/notes/01_PAPER_SIMULATION_DESIGN.md`。
- 真實資料：`/big8_disk/boyu114/phyclone_dataset/FS-CRP_Loss/data_archive/loss_prop_0.0_run0/ground_truth/{tree.json,data.tsv}`（2026-10-21 讀取）。
- 樹形統計：`loss_prop_0.0_run*` 共 100 棵（2026-10-21 重算，教授獨立重算一致）。
- 量測方式：m392 的期望比例用程式公式手算（s0：0.0161；s3：0.0753），和資料檔 `mu` 欄相同。
- 推論：「作者 benchmark 由這套程式產生」「樹形偏向讓方法看起來比較準」。講稿要標明是推論。
- 示意：P6 整頁（10 個 SNV、4 群的建樹過程）、P5 三段 SNV 入座案例與其結果、P13／P14 的流程圖是示意，不是資料。

## F. 頁面分配

頁碼＝`project/deck.json` 的 order 位置（cover＝1），總頁數 15。

| 頁 | id | eyebrow | 製作 |
|---|---|---|---|
| P1 | `cover` | — | 主 agent |
| P2 | `s0-answers` | 0 · 上次的問題 | subagent 甲 |
| P3 | `s0-needs` | 0 · 上次的問題 | subagent 甲 |
| P4 | `s1-overview` | 1 · 程式怎麼產生資料 | subagent 乙 |
| P5 | `s1-crp` | 1 · 程式怎麼產生資料 | subagent 乙 |
| P6 | `s1-tree` | 1 · 程式怎麼產生資料 | subagent 乙 |
| P7 | `s1-prev` | 1 · 程式怎麼產生資料 | subagent 乙 |
| P8 | `s1-cn` | 1 · 程式怎麼產生資料 | subagent 丙 |
| P9 | `s1-counts` | 1 · 程式怎麼產生資料 | subagent 丙 |
| P10 | `s1-output` | 1 · 程式怎麼產生資料 | subagent 丙 |
| P11 | `s2-paper-code` | 2 · 能不能直接用 | subagent 丁 |
| P12 | `s2-needs-check` | 2 · 能不能直接用 | subagent 丁 |
| P13 | `s2-paths` | 2 · 能不能直接用 | subagent 丁 |
| P14 | `s2-reuse` | 2 · 能不能直接用 | subagent 丁 |
| P15 | `summary` | — | subagent 甲 |

第一大段 7 頁超過「每段 1–2 頁」上限：依「結構與內容」第 13、25 條逐步拆解，使用者 2026-10-21 同意。
第一大段由乙、丙兩個 subagent 分做，因為 7 頁太多；乙、丙要共用同一套樹與細胞圖示（見 B 節）。

## G. 草圖要點（細節照 OUTLINE.md）

```
P2  三列橫條：[問題卡（淡底）] → [答案卡（白底，答案用粗體）]
P3  五張小卡一列：圖示＋短語；頁面文字放下方一行
P4  頂部一行例子身分；五格流程（每格：步驟名／輸入→輸出／假設），1–3 藍框，4–5 橘框
P5  （2026-10-21 使用者改版）頂部一行機率規則＋「α＝1，程式預設」「示意」；上中下三段＝第 1、2、3 個 SNV：入座前狀態 → 選項機率（1；1/2、1/2；2/3、1/3）→ 本例結果（開第 1 桌；進第 1 桌；開第 2 桌）。最下面第四段「全部跑完」：4 根長條＝c1 4、c2 3、c3 2、c4 1 個 SNV（示意結果；作者 600 個 SNV、9 群只放講稿）
P6  （2026-10-21 使用者改版：整頁太複雜，改用 10 個 SNV 示意）頂部規則一行；「示意」＋ 4 群排隊（c4 1、c3 2、c2 3、c1 4 個 SNV）；四格（卡片只寫標題＋一句結果，不寫 k 的細節；第 2、3 格放上下式分數「機率 1/2」，標分子（產生 k＝1 或 0）與分母（k 可為 0 或 1），再寫結果「→ 接 c4」「→ 都不接」，第 1、4 格結果固定不放）：先放入 c4 → c3 把 c4 接到底下 → c2 都不接 → c1 全接成 root；底部結論＋圖例。假想例子，非作者資料。程式 fscrp.py L104–L155
P7  （2026-10-21 改用示意例子）左：4 段比例直條 c1 0.40／c2 0.25／c3 0.20／c4 0.15（示意）；右：c1→c2、c1→c3→c4 縮排樹，每節點寫「自己 ｜ CCF」與加總式
P8  上：四格規則；下：s0、s3 兩組細胞示意（沒帶突變的腫瘤細胞／帶突變的腫瘤細胞），紅色份數
P9  左：s0 的三段細胞組成長條（正常 0／0.939／0.061）＋份數；右：兩行計算＋1000 條 read 的結果
P10 左：一列輸入表＋「沒有的資訊」三項（灰色斜線底）；右：答案檔三項
P11 左右對照表 4 列；下方「沒有公開的程式」四個斜線底小卡
P12 需求表 5 列 × 有／無 × 原因
P13 A／B／C 三張卡＋下方五項對照表；底部箭頭 C → B
P14 六格流程，每格頂部彩色標籤（新增／沿用／修改／沿用／重寫／重寫）；下方一行進度
P15 深色：三個答案＋下一步＋請老師決定
```
