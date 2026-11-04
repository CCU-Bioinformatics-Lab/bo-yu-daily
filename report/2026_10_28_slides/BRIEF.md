# 2026-10-28 簡報：共用規格（給每個段落 subagent）

Repo 根目錄：`/bip8_disk/boyu114/main_work`。Deck 根目錄 `ROOT=/bip8_disk/boyu114/main_work/report/2026_10_28_slides`。
每頁寫成 `ROOT/project/slides/<id>.html`。先讀 `report/report_rule.md`，遵守它。
逐頁內容唯一來源：`ROOT/OUTLINE.md`（v5.4，兩輪 P-1 審查，使用者 2026-10-22 確認可以製作）。審查紀錄：`ROOT/REVIEW_v5.md`。
大綱文末「保留在計畫，不上投影片」的內容（Noise 組、long read 版）**一律不上頁面、不進講稿**。
線上版：https://claude.ai/artifact/VD3N6zKfSawc7HCgoUZx6q（2026-10-23 用目前帳號重建；舊版 CLPQBjSsU2hnkBRM44Rvgw 屬原帳號。Slides artifact type；使用者 2026-10-22 同意直接覆蓋，不備份）。

## 主軸（B-1，2026-10-22 使用者指定）

- 主問題：CONIPHER benchmark 的生成器，怎麼一步步產生建樹的驗證資料？
- 兩段：0 上次的問題（P1–P2）；1 生成流程（P3–P7）。
- 使用者決定：只講一個 sample；只講一般版本（No-Noise 組），不講 Noise 組；先不談 long read；保留「隨機亂數產生」。
- L-2【必要】需求清單：因使用者「long read先不要想」，本冊不放需求清單（2026-10-22 使用者確認「可直接開始製作」）。

## A. 內容規則

- 語言：繁體中文。技術名詞保留英文（SNV、clone、truncal、subclonal、allele、copy number、multiplicity、gain、loss、cnLOH、WGD、purity、coverage、depth、alt read、VAF、read count、Poisson、Dirichlet、leaf、normal）。
- 文字用 ASD-STE100 風格：一句一件事、短句、主動語態、先結論再原因。
- 一頁一個重點。頁面文字只用大綱「圖」那段寫的短語，不要另加。每個重點文字都要有對應的圖（T-6）。
- 圖上文字只放名詞或短語（T-9）。補充、限制、推論放講稿（T-7）。
- **數字只用 `OUTLINE.md` 裡的數字**，不要自己算新數字。示意值標「示意」；LTXSIM001 的值標「實際結果」（E-3）。
- 不用「抽」（T-13，寫「隨機亂數產生」）、不用「雜訊」（T-10）、不寫「每個 sample」「多 sample」（T-12）。
- 頁面與講稿不出現：檔案路徑、檔名、函式名、commit 編號、程式欄位名（`CLUSTER`、`CCF_PHYLO`、`get_descendants` 等）、內部代號（C3b、P-1 等）。用白話名稱：「SNV 所屬 clone 欄」「CCF 欄」。
- 講稿：`<aside>` 純文字，中文約 200–250 字（S-2）。口語、能直接念。先講結論，再沿著圖講原因（S-1）。用位置、顏色、上面的字指路（S-6）。大綱的講稿要點都要講到；橋接句照大綱（S-7）。推論在講稿用口語標明：「這是我們的推論」（S-8）。一步講完再講下一步（S-10）。

## B. 視覺系統（全 deck 一致，不要改）

字體（已在 `deck.json` faces）：
- 標題：`font-family:'Noto Serif TC', Georgia, serif; font-weight:700`
- 內文：`font-family:'Noto Sans TC', Arial, sans-serif`（寫在 section 上讓它繼承）
- 數字、公式、座標：`font-family:'JetBrains Mono', 'Courier New', monospace`

字級（只用這四級）：64（頁標題 h2）、40（卡片標題 h3）、30（內文）、24（標籤、表格小字、頁尾）。

顏色：
- 深色字 `#1F2A37`；次要字 `#4A5568`；淡字（頁尾）`#6B7480`
- 背景 A `#F7F6F2`（內容頁）；卡片底 `#FDFDFB`；卡片框線 `#D9DDE3`；表頭列 `#E3E8EF`
- 步驟色（P3 五格與 P7 縮圖，全冊同一套）：產生真值的第 0–2 步（定參數、建樹、放事件）藍 `#2F6DB5`；產生 read count 的第 3–4 步（混合 clone、產生 read count）橘 `#C96A1B`。
- clone 固定色（樹節點、細胞組成長條，全冊相同）：normal `#9AA3AE`、c1 `#3B5B7A`、c2 `#7B5EA7`、c3 `#2E8B8B`、c4 `#B07D2B`。
- allele 份數條（細胞示意）：A 沒帶 SNV `#5B6B7F`；B `#C3CAD3`；帶 SNV 的 A 份數 `#D23A2E`（somatic SNV 紅，F-4）。不要用 HP1／HP2 的顏色，本冊沒有 HP。
- 好／通過 `#2E7D4F`；壞 `#B4442F`。
- 顏色不能單獨表達意思：旁邊一定要有文字。

固定圖示（全冊同一概念同一圖示，F-4）：
- 演化樹：圓形節點，節點內寫 clone 名（normal、c1、c2、c3、c4），root（normal）在上。枝旁寫 SNV 名稱（SNV1–5 等）。P4、P5、P7 用同一棵樹、同樣位置比例。
- 細胞示意：圓角方框，裡面一條條短橫條＝每一份 allele，A 在上、B 在下；帶 SNV 的份數為紅色並標「SNV」。
- 三數組 (A, B, SNV 份數)：用 JetBrains Mono，例如 `(2,1,2)`。

版面骨架（每張內容頁都一樣，位置不可跳動）：

```html
<section id="ID" style="background:#F7F6F2;color:#1F2A37;font-family:'Noto Sans TC', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:700;color:#2F6DB5;letter-spacing:2px">1 · 生成流程</p>
<h2 style="font-family:'Noto Serif TC', Georgia, serif;font-size:64px;font-weight:700;line-height:1.15;color:#1F2A37">頁標題（照大綱）</h2>
<div style="flex:1;display:flex;gap:40px"> …內容… </div>
<div style="position:absolute;left:128px;right:128px;bottom:64px;width:1664px;display:flex;justify-content:space-between">
<p style="font-size:24px;color:#6B7480">2026-10-28 CONIPHER 模擬資料生成流程</p>
<p style="font-size:24px;color:#6B7480">NN / 7</p>
</div>
<aside>講者備註</aside>
</section>
```

- eyebrow：P1 寫 `這週大綱`；P2 寫 `0 · 上次的問題`；P3–P8 寫 `1 · 生成流程`。
- 頁標題照大綱，最多兩行（64px 時一行約 25 個中文字）。
- 卡片：`background:#FDFDFB;border:1px solid #D9DDE3;border-radius:16px;padding:32px`，不設固定 height。
- 表格：`<table style="font-size:26px;color:#1F2A37">`，第一列 `<th>`；表頭列 `<tr style="background:#E3E8EF">`。
- 可視區 1664×824（內容約 y=128 到 y=920）。行高約 字級×1.4；表格列約 2.1×字級。放不下就刪字，不要縮字到 24 以下（T-8）。
- 中文每字約 1×字級寬；英文約 0.6×字級／字元。
- 「示意」標籤：右上角小膠囊 `font-size:24px;color:#4A5568;border:1px solid #D9DDE3;border-radius:999px;padding:4px 16px`。「實際結果」標籤同樣式，字色 `#2E7D4F`。

## C. 格式子集（違反會被丟掉）

- 只能有一個 `<section id="ID" …>`，id 等於檔名，前後不能有任何東西。不能有 `<html> <head> <style> <link> <script> class`。
- 所有樣式 inline。禁止：`margin`、`z-index`、`em`、`rem`、`%` 字級、`var()`、`float`、`grid-area`、colspan/rowspan、巢狀清單。
- 可用元素：`h1 h2 h3 p ul ol li br b i u span(只能設 color) a div img table tr th td svg hr x-shape x-icon x-connector aside`。
- `<x-shape kind="rect|rounded|ellipse|diamond|arrow-right|arrow-left|arrow-up|arrow-down|line" style="background;border;width;height">`；箭頭長寬比接近 2:1。
- `<x-connector x1 y1 x2 y2 head="end|both|none" route="straight|hv|vh|elbow" style="color:#…;border-width:3px">`：放在 `position:relative` 的 div 裡以 div 座標定位。不能設 left/top/width/height。
- `<x-icon name>` 只能用：Activity Book Chart Chat Check CheckCircle Clock Cloud Code Database Globe GraduationCap Home Key Lightbulb Lightning Link Lock PaperPlane Play Search Settings Star ThumbsUp Tool Trust Users Verified Warning Wrench。
- `<svg aria-label width height viewBox>`：只畫圖形，不用 `<text>`。文字標籤用 pinned `<p>` 疊上去。svg ≤52KB。
- `position:absolute` 的子元素要給 width。一個 div 內最多 24 個 pinned 子元素。每頁最多 200 個元素，div 最多 15 層。
- 勾叉用 `<x-icon name="Check">` 或文字「有／無」。中文用全形標點。
- 斜線底（F-5，基準那側沒有的東西）：`background:repeating-linear-gradient(45deg,#EEF0F3,#EEF0F3 10px,#FDFDFB 10px,#FDFDFB 20px)`。

## D. 頁面分配

頁碼＝`project/deck.json` 的 order 位置（outline＝1；2026-10-23 依 W-4 拿掉封面，舊頁移到 `removed_slides/cover.html`），總頁數 8（2026-10-22 新增 `s1-params`）。

| 頁 | id | eyebrow | 製作 |
|---|---|---|---|
| P1 | `outline` | 這週大綱 | 主 agent（2026-10-23 取代封面） |
| P2 | `s0-answer` | 0 · 上次的問題 | subagent 甲 |
| P3 | `s1-overview` | 1 · 生成流程 | subagent 乙 |
| P4 | `s1-params` | 1 · 生成流程 | 主 agent（2026-10-22 補頁） |
| P5 | `s1-tree` | 1 · 生成流程 | subagent 乙 |
| P6 | `s1-cn` | 1 · 生成流程 | subagent 乙 |
| P7 | `s1-counts` | 1 · 生成流程 | subagent 乙 |
| P8 | `s1-output` | 1 · 生成流程 | subagent 乙 |

## E. 草圖（F-1）

```
P1  大綱頁（W-4，只有文字）：標題寫主問題；三列 [上次的問題｜用公開、能重現的生成器回答｜第 2 頁]
                                      [生成流程｜五步｜第 3–7 頁] [輸出｜read count＋真值｜第 8 頁]
P2  上：左右兩欄卡片 [PhyClone 作者的 benchmark｜生成程式：沒找到（斜線底）｜範圍：repo＋論文補充]
                      [CONIPHER 的 benchmark｜生成程式：公開｜重跑 150／150 份輸出相同（實際結果標籤）]
    下：三格徽章 [真值來源：模擬] [讀長：short read，只有 read count] [生成程式：公開]
P3  五格橫向卡＋箭頭（2026-10-23 改成示意圖，F-9）；每卡：步驟名（藍/橘頂條）＋ 示意圖 ＋ 一個短語圖說
    [五個參數條] → [小樹] → [小樹＋枝上紅短線＋c2 旁 SNV/SNV/媽] → [直立比例條＋purity 括號] → [SNV1 上 6 條 read，紅點 alt、白點 ref]
    下方：藍括號「產生真值」（第 1–3 步）、橘括號「產生觀察到的資料」（第 4–5 步）
P4' s1-params（2026-10-23 改成示意圖）：上排五張參數卡 [名稱＋範圍｜例子值｜小圖｜→ 第 N 步]；
    下排 WGD 細節：三棵小樹（無／clonal／subclonal，加倍的 clone 黑框）｜表（順序×爸媽份數×multiplicity×VAF）＋subclonal、depth 兩行
（以下 P4–P7 是 2026-10-22 補頁前的頁碼，現在是 P5–P8；數值以 OUTLINE 的改版記錄為準）
P4  左卡「第 1 步 建樹」：(a) 隨機二分大樹縮圖 → (b) 剪 leaf 後 normal→c1→{c2, c3→c4}
    右卡「第 2 步 放 SNV」：同樹，normal→c1 枝旁「SNV1–5 truncal」，c1→c2「SNV6–7」，c1→c3「SNV8–9」，c3→c4「SNV10」，後三者標 subclonal
P5  頂規則列；左右兩欄細胞示意：SNV2 (1,1,0)→(1,1,1)→(2,1,2) multiplicity 2；SNV3 (1,1,0)→(2,1,0)→(2,1,1) multiplicity 1
    底列：小樹，SNV8 在 c1→c3 枝；c3、c2 綠勾「可放」；c4 紅叉「不放」
P6  左：細胞組成橫條 normal 20｜c2 30｜c3 20｜c4 30（%）＋規則列
    中：期望 VAF 四列表 SNV1 0.40／SNV2 0.57／SNV3 0.29／SNV8 0.25＋公式列
    右：SNV1 depth 長條 397，alt 159 段紅色＋規則列
P7  左卡「給建樹工具的輸入」：4 列 read count 表；右卡「藏起來的真值」：同一棵樹＋SNV→clone＋clone 比例
    下列「實際結果：LTXSIM001」：樹縮圖說明、第 1 列 chr11:79841933 105／691 purity 0.42、972 個 SNV
    最下：五步縮圖（藍藍藍橘橘）
```

P6 中欄「期望 VAF：SNV6」改版草圖（2026-10-23，E-5；先上方案 A，同日使用者改選方案 B 彈珠，已上頁）：

```
方案 A 層蛋糕（寬＝比例，層＝份數，紅層＝帶 SNV）
                              ┌────────┐
                              │▓▓▓▓▓▓▓▓│ 爸（gain 複製）
 ┌────────────────────┬──────┼────────┼──────┬────────┐
 │                    │      │▓▓▓▓▓▓▓▓│      │        │ 爸
 ├────────────────────┼──────┼────────┼──────┼────────┤
 │                    │      │        │      │        │ 媽
 └────────────────────┴──────┴────────┴──────┴────────┘
   normal 41%          c1 12% c2 17%   c3 13% c4 17%
 VAF＝紅色面積 ÷ 整塊蛋糕 ＝ 0.34 ÷ 2.17 ≈ 0.16

方案 B 一袋彈珠（100 個細胞的 DNA 份數全倒進袋子）
 normal ○○ ×41 ┐
 c1     ○○ ×12 │
 c2    ●●○ ×17 ├─→ 袋子 217 顆，紅 ● 34 顆 → 抽到紅的機率 34/217 ≈ 0.16
 c3     ○○ ×13 │
 c4     ○○ ×17 ┘
```

P7 的示意 read count 表：位置欄用「SNV1」等名稱，不寫座標；alt／depth 只寫 SNV1 的 159／397，其他三列 alt／depth 寫「—」，只放 A 份數、B 份數、purity（SNV1 1／1、SNV2 2／1、SNV3 2／1、SNV8 1／1；purity 0.8）。不要自己編新的 read 數。

## F. 來源代號表（C-10）

| 代號 | 來源 |
|---|---|
| 程式 | `zaccaria-lab/TRACERx_simulation_tool` commit `8c8d173`，`/big8_disk/boyu114/phyclone_dataset/CONIPHER_rerun/tool_8c8d173/src/`（本地 submodule `facd2d7` 模擬函式相同） |
| 重跑 | `lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md` |
| 實際結果 | `/big8_disk/boyu114/phyclone_dataset/CONIPHER_rerun/No-Noise_sim/LTXSIM001/sim/`（2026-10-22 讀取） |
| PhyClone 搜尋範圍 | PhyClone repo commit `2738324` 與論文補充文件；`lab_report/2026-10-21_phyclone_sim_rerun/` |

程式位置（L-4、C-18）：參數 `make_simulation.py`；建樹 `topology.py` `make_tree`、`prune_tree`；SNV `evolution.py` `snv_assignment`；CNA `cna_assignment`、`assign_cnas`、`prevent_subclonal_cnas`；事件 `generate_events`；先後隨機 `concat_all_events`；混合與 read count `sequencing.py` `simulate_sample_leaves`、`all_samples`、`calculate_vaf`、`get_total_reads`、`get_variant_reads`；座標 `conversion.py` `assign_chr_pos_correct`。

## G. 示意與量測（C-10）

- 示意：5 節點樹、10 個 SNV、SNV2／SNV3 的事件先後、clone 比例、purity 0.8、coverage 400、SNV1 depth 397 與 alt 159。全是假想例子，用程式公式手算。
- 實際結果：LTXSIM001（一般版本）13 個腫瘤 clone＋normal、972 個 SNV、truncal 枝 535、clonal WGD、prop_truncal 0.55；第一個 sample purity 0.42、第 1 列 chr11:79841933 alt 105／depth 691。
- 但書（不上頁面）：LTXSIM001 有 3 個 sample，頁面只取第一個；該 sample 不含全部 leaf。一般版本不是 `make_tx_simulations` 預設產生（預設一律開 mutation loss 與假 SNV），重跑用每份記錄的參數（推論＋實測）。
- 論文／程式／推論：頁面流程全依程式行為；CONIPHER 論文 Methods 沒讀到。推論只有一處，在講稿：P5「每個位置各自決定 copy number 是簡化」。

## H. 術語表（B-7）

| 術語 | 全冊寫法 | 第一次解釋的頁 |
|---|---|---|
| 腫瘤細胞群 | clone | P3 |
| 第一個腫瘤 clone | truncal clone（c1） | P4 |
| 所有腫瘤細胞都有的 SNV | truncal SNV | P4 |
| 只有一支有的 SNV | subclonal SNV | P4 |
| 正常細胞 | normal | P4 |
| 兩個版本的染色體 | allele；頁面寫「爸爸的 copy number／媽媽的 copy number」，圖上簡寫「爸」「媽」，表頭「爸份數／媽份數」（2026-10-22 使用者留言指定；程式裡叫 A、B，P5 講稿說明） | P3 講稿一句、P5 詳細 |
| 份數 | copy number | P5 |
| 帶 SNV 的份數 | multiplicity | P5 |
| 份數不變的 LOH | cnLOH | P5 |
| 全基因組加倍 | WGD | P3 |
| 腫瘤細胞比例 | purity | P3 |
| 平均讀到幾次 | coverage | P3 |
| 某位點讀到幾次 | depth | P6 |
| 帶 SNV 的 read 比例 | VAF | P6 |
| read 的計數 | read count | P3 |
| 隨機步驟 | 隨機亂數產生 | — |

## 規則檢查（2026-10-22；2026-10-23 更新 P1）

`python3 tools/check_slides.py report/2026_10_28_slides/ --titles`：8 頁，0 個錯誤，結束碼 0（2026-10-23 封面改大綱頁後重跑）。

標題串讀（W-3）：
1. 這週回答：CONIPHER 的模擬資料怎麼一步步產生？
2. 上次問模擬資料怎麼產生：用公開、能重現的 CONIPHER 生成器逐步回答
3. CONIPHER 生成器分五步：定參數、建樹、放事件、混合 clone、產生 read count
4. 第 1 步：先隨機產生五個參數，每個參數控制後面一步
5. 建樹與放 SNV：一部分 SNV 放在 truncal 枝，其餘分到各 subclone 枝
6. SNV 和 copy number gain 的先後，決定 SNV 的 multiplicity
7. 產生 read count：clone 依比例混合，每個位點各自隨機亂數產生 depth 與 alt read
8. 輸出：每個 SNV 一列 read count，加上真值樹與每個 SNV 所屬的 clone

| 代號 | 結果 | 說明 |
|---|---|---|
| W-3 | ✓ | 標題串讀如上，P-6 檢查者確認能講完故事 |
| W-4 | ✓ | 沒有封面；P1 是大綱文字頁，標題寫主問題，三段各一列並標頁碼 |
| P-1、P-2 | ✓ | 兩輪兩方審查（`REVIEW_v5.md`）；使用者 2026-10-22 確認「可直接開始製作」 |
| P-11 | 不適用 | 使用者 2026-10-22 指示「直接覆蓋沒差，不用備份舊版」 |
| C-1、C-2 | ✓ | 段落與標題照 v5.4；主問題對照使用者原話與會議整理 |
| C-7 | ✓ | 流程依程式行為，P3 講稿說明論文 Methods 沒讀到；推論只有 P5 一處，講稿標明 |
| L-1 | ✓ | P2 回答上次問題；P7 收尾回到老師的問題 |
| L-2、L-3 | 部分 | L-3 ✓（P2 三格徽章）；L-2 需求清單依使用者「long read先不要想」不放 |
| L-5、L-6 | ✓ | 重跑結果附實測；PhyClone 寫「沒找到」並附範圍 |
| E-1、E-3 | ✓ | 全冊同一棵 5 節點樹；示意與實際結果膠囊都有 |
| F-9 | ✓ | P3、P4 每步或每個參數一張示意圖，文字只留名稱與短語圖說（2026-10-23） |
| C-18 | ✓ | P4 每個參數標出控制第幾步；WGD 細節對照 `wgd_assignment`、`generate_events`、`calculate_vaf`、`get_total_reads` 核對（2026-10-23） |
| F-4 | ✓ | clone 固定色全冊一致；P7 縮圖 truncal 枝改用 c1 色，不用 SNV 紅 |
| T-5、S-4 | ✓ | 術語第一次出現都有一句解釋（P-6 檢查後補 depth、CCF、cnLOH 順序） |
| T-6、T-7 | ✓ | 頁面文字都有對應圖；但書在講稿 |
| S-7 | ✓ | 段落間有橋接句 |

排版：沒有渲染器，reviewer 依 B 節估算法逐頁估算，修正 P3、P5、P6 的溢出與 P7 標籤寬度。上線後建議看一次實際畫面。

## 2026-10-27 追加第 8 頁 `s2-truth-evidence`（使用者指示，C-19）

- 使用者原話：在最後一頁加上 longbulksim 模擬真值樹上事件的資料來源視覺化，顯示 clone 可細分 HP1／HP2 的 SNV 與其他事件，且有真實資料支持。
- 底稿：線上版 1793077491-4f26（使用者在編輯器改過 s1-output 等頁）。改前的本地版備份在 `local_backup_2026-10-27/`。
- 改動：新增 P8；全部頁尾改成 n / 8；大綱頁加第三列「模擬真值樹｜第 8 頁」與講稿一句；P7 講稿結尾加橋接句（S-7）。
- 樹：`longbulksim/specs/stress.yaml`（＝`research/simulation_pipeline_research/figures/hp_truth_tree.png`）。頁面把 s1–s10 寫成 SNV1–SNV10（E-4）。這棵樹和第 2–7 頁的 CONIPHER 示意樹是不同的樹，講稿有說明。
- 草圖（F-1）：
  ```
  左卡 壓力測試樹（設計值）              右卡 每個事件的真實資料（資料實測）
   ① purity 0.40  (normal)                表：事件｜資料｜觀察到什麼，①–⑦ 各一列
        │  ⑤ [HP1：SNV1、3、9][HP2：SNV2、10]
       c1
   [HP2：SNV4]  ╱   ╲  [HP1：SNV7][HP2：SNV6]
   ② HP1 gain  c2    c3  ④ CCF 0.10
   ⑥ cnLOH      │
   ③ SNV10 遺失 │ [HP1：SNV5] ⑦ SNV8 在 gain 後 ③ HP2 deletion → SNV2 遺失
               c4
  ```
- 數字來源（全部是資料實測，已對照原文）：
  | 事件 | 數字 | 來源 |
  |---|---|---|
  | ① purity | TRACERx 421 tumour 中位 0.39 | `lab_report/2026-10-25_tracerx_event_stats/README.md` |
  | ② subclonal HP gain | 91% tumour（嚴格版 haplotype-specific subclonal gain） | 同上 |
  | ③ 突變遺失 | 47% tumour ≥ 1 個（區域間，嚴格下限） | 同上 |
  | ④ 低 CCF | 8.4% subclone CCF ≤ 0.15（單區域） | 同上 |
  | ⑤ HP 拆分 | HCC1395 ONT 92.2%（≥ 3 alt read 的 SNV，≥ 90% tagged alt 在同一 HP）；HG008 平衡區 2,208：2,385 | `lab_report/2026-10-25_hcc1395_hp_split/`、`lab_report/2026-10-25_hg008_truth_tree_plausibility/` |
  | ⑥ cnLOH | TRACERx 421 72% tumour ≥ 1 Mb；HCC1395 ONT 2:0 區 97.5% 位點 minor HP 比例 < 0.1 | 同上兩份 |
  | ⑦ CN timing | HG008 gain 區 multiplicity 2：1＝76：65 | `lab_report/2026-10-25_hg008_truth_tree_plausibility/` |
- 但書（只在講稿）：事件都存在，但突變遺失 20% 遠高於中位 0%、分岔樹屬少數，所以定位為壓力測試（`truth_evidence_2026-10-25/SUMMARY.md`）。
- 規則檢查：`check_slides.py` 8 頁，新頁 0 錯誤。剩 3 個 T-13（「抽」）在 s1-counts、s1-output，是使用者線上版既有的彈珠比喻文字，這次沒動。排版沒有渲染器，依座標估算。
- 標題串讀第 8 條：模擬真值樹的每個事件，都在真實資料中觀察到。
- 未做：P-1 兩方審查與 P-2 大綱確認（使用者直接指定內容）。

## 2026-10-27 追加第 9 頁 `s2-hg008-clones`（使用者指示，C-19 新子條）

- 使用者原話：在第八頁新增 GIAB HG008 能提供什麼資料，證明設計的真值演化樹事件符合生物驗證，且 long read haplotype 特徵真的出現在腫瘤演化樹中。
- 第 8 頁已放滿七列表格，所以接在第 8 頁後面另開一頁；第 8 頁只在講稿結尾加橋接句（S-7）。
- 底稿：線上版 1793084478-4d06（先把線上全部頁檔同步回本地 `project/`）。發布後版本 1793084950-6702。
- 改動：新增 P9；全部頁尾改成 n / 9；大綱頁第三列改「第 8–9 頁」並補一句；`deck.json` s2 description 補 HG008。
- 草圖（F-1）：
  ```
  頂列：HG008 提供 [8 株單細胞衍生 clone（PacBio） → 樹形、事件在哪條枝] [bulk ONT 63× → SNV 對到 HP、bulk CCF] [normal assembly → HP1／HP2 方向]
  左卡 HG008 clone 樹（資料實測）           右卡 對到真值樹的事件（資料實測）
          normal                            ② {2D6,2E6} chr2 1+1→2+1，32 Mb
          truncal                           ⑦ {2D6,2E6} multiplicity 2：1＝56：46，兩群各在一條 HP
   紫{2D6,2E6} 青{SC14,SC28} SC6 另3株      ⑥ SC6 chr1q 1+1→2+0，100 Mb
   2D6 2E6     SC14 SC28   ⑥③               ③ SC6 cnLOH 205、chrX deletion 161 個遺失
   ②⑦          ⑤HP1 24 HP2 27 ④CCF 0.14     ④ {SC14,SC28} bulk CCF 約 0.14
                                            ⑤ {SC14,SC28} HP1：HP2＝24：27
  ```
  紫＝c2 色、青＝c3 色（C-17：對應 clone 同色）。
- 數字來源：全部取自 `lab_report/2026-10-27_hg008_clone_tree_hp/README.md` 第 1 節與 4.x 節。CCF 0.14 是推論（假設 1+1、purity 約 1），講稿標明。CN 是 PURPLE 推論〔工具〕。① purity 不適用（細胞株 purity 約 1），只在講稿說明。
- 和第 8 頁的差異：第 8 頁 HG008 ⑦ 76：65 是 2026-10-25 全基因組 gain 區 bulk 統計；第 9 頁 56：46 只算 {2D6,2E6} chr2 subclonal gain 區，講稿有說明。
- 規則檢查：`check_slides.py` 9 頁，新頁 0 錯誤；剩 3 個 T-13（s1-counts、s1-output 使用者既有彈珠文字，未動），結束碼 1。排版沒有渲染器，依座標估算（標題約 1,560 px 一行；右表約 362 px，可用 408 px）。
- 標題串讀第 9 條：HG008 真實 clone 樹上，也看得到真值樹的事件與 HP 拆分。
- 未做：P-1 兩方審查與 P-2 大綱確認（使用者直接指定內容）。
- 2026-10-27 使用者指定：頁首與講稿改稱「單細胞衍生 clone」，講稿說明是單一細胞培養後用 PacBio 整群定序，不是單細胞定序。術語表加一列：單細胞衍生 clone｜單一細胞培養成群後整群定序的 clone 株｜P9。

## 2026-10-27 第 2 段改成一頁一個事件（使用者指示，C-19 改寫）

- 使用者原話：第八、九頁都太複雜，先拆分。左邊放 GIAB HG008 的樹證明該頁的事，右邊放我設計的模擬真值樹；第八頁先做「clone 內的 SNV 可細分 HP1、HP2」，所以可以生成 long read 模擬 bulk 資料。
- 底稿：線上版 1793085547-b325。舊第 8 頁（事件總表）與第 9 頁（HG008 clone 樹）的線上版移到 `removed_slides/s2-truth-evidence_2026-10-27.html`、`removed_slides/s2-hg008-clones_2026-10-27.html`，並從線上刪除。發布後版本 1793086375-b3d5。
- 新 P8 `s2-hp-split`：總頁數 8，全部頁尾改成 n / 8；大綱頁第三列改「第 8 頁」與新說法。
- 草圖（F-1）：
  ```
  左卡 GIAB HG008 真實 clone 樹（資料實測）   →照著設計→   右卡 我們的模擬真值樹（設計值）
     normal                                                  normal
     truncal  [HP1 2,208][HP2 2,385]                         c1 [HP1 SNV1、3、9][HP2 SNV2、10]
   其他6株  青{SC14,SC28} [HP1 24][HP2 27]           [HP2 SNV4] c2      c3 [HP1 SNV7][HP2 SNV6]
             SC14  SC28                                         c4 [HP1 SNV5、8]
  下列：→ 生成 long read bulk 資料 ｜ read 示意（HP1／HP2 read，SNV 只在自己那條 HP 的 read 上）｜ 4 色圖例（F-4）
  ```
  truncal＝c1 色、{SC14,SC28}＝c3 色（C-17）。
- 數字來源：truncal 2,208／2,385 是 GIAB V0.4 clonal SNV 在 1+1 區的 hap1／hap2（`lab_report/2026-10-25_hg008_truth_tree_plausibility/`）；{SC14,SC28} 24／27（另 42 判不出）是 bulk ONT 判讀（`lab_report/2026-10-27_hg008_clone_tree_hp/tables/branch_bulk_hp.tsv`）。模擬樹 HP 依 `longbulksim/specs/stress.yaml`。
- 拆分計畫（之後各一頁，同一版面；保留在計畫，未上頁面）：② HP gain＋⑦ gain 前後的 SNV（{2D6,2E6} ↔ c2）；⑥ cnLOH＋③ 突變遺失（SC6 ↔ c2／c4）；④ 低 CCF clone（{SC14,SC28} ↔ c3）。① purity HG008 不適用，需另找資料。舊總表的 TRACERx／HCC1395 數字可放講稿。
- 規則檢查：`check_slides.py` 8 頁，新頁 0 錯誤；剩 3 個 T-13（s1-counts、s1-output 既有），結束碼 1。排版依座標估算（標題約 1,460 px 一行；樹區 376 px，卡內可用約 384 px）。
- 標題串讀第 8 條：真實 clone 樹的 SNV 分在 HP1、HP2，模擬樹照著設計。
- 未做：P-1 兩方審查與 P-2 大綱確認（使用者直接指定內容）。

## 2026-10-27 第 8 頁左樹換成單細胞修正版（使用者指示）

- 底稿：線上版 1793086544-582d（使用者已在編輯器刪掉底部「生成 long read bulk 資料」列）。發布後 1793088560-47dc。
- 左樹改成：normal → truncal → {3E4（灰）, 7 株共同枝} → {{2D6,2E6}、SC6（灰）, {SC9,SC14,SC24,SC28}} → {{SC14,SC28}, SC9、SC24（灰）} → SC14、SC28。HP 膠囊移到節點左側。綠字＝帶該枝的單細胞數（119／119、111／119、48／119、16／119），來源 `lab_report/2026-10-27_hg008_sc_tree_check/`。
- 講稿：補單細胞檢查一句與「bulk 0.14 對 16／119」；刪掉提到底列的句子（P-10），改成一句不指圖的說法。
- check_slides：8 頁，新頁 0 錯誤（剩既有 3 個 T-13）。

## 2026-10-27 第 8 頁使用者留言（頁面編輯器已套用，線上版 1793089162-4825）

- 刪掉綠字（單細胞數）與圖例，只留 clone 與 HP1／HP2。單細胞數只在講稿口頭補充。
- clone 改成 1–8 編號：1＝3E4、2＝2D6、3＝2E6、4＝SC6、5＝SC9、6＝SC24、7＝SC14、8＝SC28。節點：7 株共同枝、{2, 3}、4、{5, 6, 7, 8}、{7, 8}、5、6、7、8。對照表也寫在講稿。本地檔已同步成線上版。

## 2026-10-27 第 8 頁左樹改成和模擬樹同一畫法（使用者選「只改畫法，保留真實分枝」）

- 底稿 1793089162-4825，發布後 1793089394-80d7。
- 圓形節點：h1＝truncal、h2＝7 株（1 號以外）共同祖先、h3＝5–8 號共同祖先、h4＝7、8 號共同祖先；樣本 7、8 小圓；灰色「其他：1」「其他：2、3、4」「其他：5、6」。右上角 4 行圖例說明 h1–h4。HP 膠囊：h1 2,208／2,385、h4 24／27。
- 講稿：補 h1–h4 定義，{7, 8} 全部改成 h4，c1 對 h1、c3 對 h4。
- 規則：C-19 新增畫法子條。check_slides：新頁 0 錯誤。

## 2026-10-27 第 8 頁左樹全部改成 h1–h9（使用者：不用分「其他」與共同祖先）

- 發布後 1793089588-960d。圖例與「其他」節點刪除。
- 對照（只在講稿）：h1＝truncal；h2＝1 號以外 7 株共同枝；h3＝1 號（3E4）；h4＝2、3、4 號（2D6、2E6、SC6，合併）；h5＝5–8 號共同枝；h6＝7、8 號共同枝（對應 c3，HP1 24／HP2 27）；h7＝5、6 號（SC9、SC24，合併）；h8＝7 號（SC14）；h9＝8 號（SC28）。
- 顏色：h1 深藍（對 c1）、h6 青（對 c3），其他 h 深灰。

## 2026-10-27 第 8 頁加 h2、h5 的 HP（使用者指示）

- 發布後 1793089830-2a69。h2：HP1 54、HP2 68（7 株共同枝真分枝 303 個 SNV 的 1+1 區；`lab_report/2026-10-27_hg008_sc_tree_check/README.md` 第 6 節）。h5：HP1 7、HP2 9（`branch_bulk_hp.tsv` SC14,SC24,SC28,SC9 列）。講稿補一句。

## 2026-10-27 第 8 頁九個節點都填 HP（clone 定相，使用者指示）

- 來源改為每株 clone 自己的 PacBio 定相，依 V0.4 HG008-N assembly 統一方向（`lab_report/2026-10-27_hg008_clone_tree_hp/README.md` 第 7 節；`tools/hg008_clone_hp_orient.py`）。只算該 clone 1+1 區。與 bulk ONT 一致 99.7%，跨 clone 一致 97.8%。
- 數字（HP1：HP2）：h1 2,404：2,490；h2 52：66（真分枝 303 個）；h3 194：277；h4 462：478（2D6、2E6、SC6 private＋{2D6,2E6} 加總）；h5 7：10；h6 34：55；h7 184：190（SC9、SC24 private 加總）；h8 89：99；h9 130：153。
- 版面：節點旁一對色塊只寫數字，右上角 HP1／HP2 圖例；樹區高 500。講稿改寫 HP 段落。

## 2026-10-27 新增第 8 頁 `s2-hg008-data`（使用者指示；原 HP 頁變第 9 頁）

- 底稿 1793090263-7741，發布後 1793092588-4475。全部頁尾改 n / 9；大綱頁第三列「第 8–9 頁」；`deck.json` s2 start 改成新頁。
- 草圖（F-1）：
  ```
  左 2/3：8 張資料卡（2 欄 × 4 列），綠框＝已使用、灰框＝尚未使用
    已使用：8 株單細胞衍生 clone｜bulk 腫瘤 ONT｜119 顆單細胞｜normal 組裝序列｜GIAB 突變 benchmark
    尚未使用：Tapestri 單細胞｜ResolveOME 單細胞｜多代 bulk
  右 1/3：→ [Claude agent 星芒圖示｜寫分析程式、交叉核對] ↓ [HG008 真實 clone 樹縮圖｜9 個 clone｜每個都有 HP1、HP2｜資料實測]
          ⇣ 虛線「當作參考」 [模擬真值樹縮圖 c1–c4｜設計值]
  ```
- 資料清單來源：GIAB FTP 2026-10-27 目錄（scratchpad `giab/listing.tsv`）與各資料 README。星芒圖示是自畫的通用符號，不是官方 logo。
- L-5：講稿寫明分析由 Claude agent 協助寫程式，並以資料交叉核對（HP 兩種方法 99.7% 一致、單細胞重現主要分枝）。
- check_slides：9 頁，新頁 0 錯誤（剩既有 3 個 T-13）。標題串讀第 8 條：HG008 公開資料推論出參考用的真實 clone 樹。

## 2026-10-27 新增第 10 頁 `s2-hp-gain`（使用者指示，C-19 左右對照）

- 底稿 1793092588-4475，發布後 1793093076-c91c。全部頁尾改 n / 10；大綱頁「第 8–10 頁」；第 9 頁講稿結尾加橋接句。
- 草圖（F-1）：
  ```
  左（資料實測）：同第 9 頁 h1–h9 樹，h4 紫色＋「HP2 gain」膠囊
     份數條：HP2 ■■（A●●）(B● 只在一條)  HP2 ■■  HP1 ■（C●）
     A 52 個：gain 前，2 份｜B 1 個：gain 後，1 份｜C 37 個：在 HP1，1 份
  右（設計值）：c1–c4，c2 紫色＋「HP1 gain」
     份數條：HP1 ×2（A＝SNV1 兩條都有，B＝SNV8 一條）、HP2 ×1
  ```
- 數字：`lab_report/2026-10-27_hg008_clone_tree_hp/README.md` 第 8 節（chr2:28–62 Mb，2D6、2E6 2+1；multiplicity＝round(VAF×3)；HP 用 clone 定相）。「約 32 Mb」沿用第 1 節寫法。B＝1 個證據弱，講稿明說。
- h4 在第 9、10 頁都用紫色（對應 c2，C-17；第 9 頁 2026-10-27 依使用者改色）。
- check_slides：10 頁，新頁 0 錯誤（剩既有 3 個 T-13）。標題串讀第 10 條：被 gain 的 HP 上 SNV 變兩份，模擬樹照著設計。
- 2026-10-27 使用者留言「HP1、HP2 旁加 copy gain 事件與突變份數」：頁面編輯器已套用（線上 1793093978-bf30）：列標「HP2 原本／HP2 ＋gain」、gain 那份虛線框、右側「突變 2 份／1 份」。本地已同步。另做的「gain 前 → 箭頭 → gain 後」版本未發布，草稿在 scratchpad `s2-hp-gain_timeline_draft.html`。
- 2026-10-27 使用者指出份數條畫反（「HP2 原本」上同時有 A、B，讀起來像 B 在 gain 前就存在卻沒被複製）。改成時間順序：gain 前（HP2：A；HP1：C）→ 箭頭「HP2 copy gain」→ gain 後（HP2 兩份都有 A，B 只在一份；HP1：C），底下一行寫突變份數。右卡同法（SNV1、SNV8）。講稿補「另一份不是失去 B，而是複製時 B 還不存在」。發布後 1793094361-3a89。
- 2026-10-27 第 10 頁排版亂掉：編輯器（1793094484-6357）把左面板一個「HP1」標籤移出定位圖層，成為面板下的一般段落，撐高卡片。修正（1793094556-9ce6）：刪除該段落；刪除 gain 後三條份數條左側 HP 標籤（兩面板共 5 個，顏色與「HP2 2 份／HP1 1 份」已標示）；圖例縮成一行「突變份數：A 2 份・52 個｜B 1 份・1 個｜C 1 份・37 個」。教訓：一個定位容器內的元素盡量少於 20 個。

## 2026-10-27 新增第 8 頁 `s2-architecture` 架構圖（使用者指出方向偏了）

- 使用者原話：講完第七頁的輸入輸出，應該要說明整體的最精簡生成模擬程式，方便借鑑 CONIPHER 模擬程式來生成 long read 版本，在第八頁新增架構圖。
- 底稿 1793095369-1391（使用者編輯器版），發布後 1793097848-fea6。總頁數 11；HG008 資料頁、HP 拆分、HP gain 依序變第 9–11 頁。
- 草圖（F-1）：
  ```
            定參數   建樹    放事件       混合 clone  產生 read        輸出
  CONIPHER  [參數條] [小樹]  [枝上紅點]   [比例條]    [alt/ref 長條]   [表]
            ↓修改    ↓修改   ↓新寫        ↓沿用       ↓新寫            ↓擴充
  longbulk  [參數條] [小樹]  [HP1/HP2 點 [比例條]    [HP1/HP2 read，  [表＋HP 欄
            TRACERx  直線／  ＋HP gain]               一條帶多個 SNV]   ＋共現欄]
  ```
- 對應程式（L-4）：CONIPHER 見第 F 節；longbulksim `param_tree.py`（Params、draw_tree、draw_spec）、`model.py`（replay：事件順序 → multiplicity、遺失）、`sample.py`（place_mutations、sample_segment：逐條 read）、`simulate.py`（run、counts、pair_rows、輸出 data.tsv／data_hp.tsv／pairs.tsv／truth）。測試：`ReadCooccurrenceFollowsTree`、`CountsMatchExpectedVAF`（longbulksim README「已驗證」）。
- 第 7 頁講稿結尾改成橋接到架構圖；架構圖講稿結尾橋接到 HG008 資料頁。大綱頁第三列改「long read 版｜沿用五步骨架改成 long read 版，再用 HG008 佐證新事件｜第 8–11 頁」。
- 規則：L-10 新增子條（基線輸入輸出之後先放架構圖）。check_slides：11 頁，新頁 0 錯誤。
- 2026-10-27 第 8 頁 CONIPHER「定參數」格：使用者留言改成「範圍內隨機值」，編輯器已套用（1793099145-0a78），本地已同步。

## 2026-10-27 第 8 頁 longbulksim 定參數格改成「範圍內隨機值」（使用者指示）

- 使用者原話：幫我也把第八頁longbulksim的輸入也改成範圍內隨機值，其他細節部分先隱藏。使用者選「只改頁面」：程式不動。
- 頁面：longbulksim 定參數格由「TRACERx 中位數＋read 長度」改成「範圍內隨機值」，和 CONIPHER 列同一句。參數來源與 read 長度等細節不上頁面。
- 講稿：定參數句改寫，刪掉 TRACERx／PCAWG 中位數、read 長度、HP tag 比例；加一句「目前程式還是用固定值，改成範圍內隨機值是接下來要做的」（C-7：頁面是計畫，程式是固定值；`longbulksim/longbulksim/param_tree.py` docstring）。
- 「↓ 修改」標籤沒動。
- 規則：L-10 新增子條（架構圖每格只放做法短語，細節隱藏；和程式不同時講稿寫明）。
- 規則檢查（P-8 局部修改）：check_slides 第 8 頁 0 錯誤；全冊 3 個錯誤是第 6、7 頁既有的「抽」，本次未動。W-3 標題串未變 ✓；E-1 不受影響 ✓；C-7 講稿已標明程式實際行為 ✓。
- 發布：線上版 1793099145-0a78（和本地 sha256 相同）→ 1793102122-9e20。

## 2026-10-27 第 8 頁定參數格列出共同參數（使用者指出只寫「範圍內隨機值」看不出定了什麼）

- 兩列定參數格都改成：clone 數、SNV 數／purity、coverage／gain／loss、WGD／**範圍內隨機值**。名稱照第 3 頁 CONIPHER 參數頁；longbulksim 六個參數都有對應（`n_clones`、`n_snv`、`purity`、`depth`、`prop_gain`／`prop_loss`、`wgd`）。
- 參數條示意圖縮成 48 px 高；兩列卡片高度 190→240、220→250 px，讓四行字放得下。
- 講稿定參數句改成列出同一組六個參數。
- 規則：L-10 再加一條子條（定參數格列出共同參數名稱）。
- 發布：1793102295-fafc。發布前線上有一次頁面儲存 1793102197-9b65，本檔覆蓋了該版的第 8 頁；其他頁保留。

## 2026-10-27 第 8 頁定參數欄標籤改成「↓ 擴充」（使用者留言）

- 使用者在定參數欄的「↓ 修改」留言「擴充」。線上版 1793106973-aae5 已套用：標籤改「↓ 擴充」，講稿改「灰色是擴充或修改」。本地已同步成該版。
