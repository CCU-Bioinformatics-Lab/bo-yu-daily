# 2026-10-21 簡報 v5.3：共用規格（給每頁 subagent）

Repo 根目錄：`/bip8_disk/boyu114/main_work`。Deck 原始檔根目錄 `ROOT=/bip8_disk/boyu114/main_work/report/2026_10_21_slides`。
每頁寫成 `ROOT/project/slides/<id>.html`。先讀 `report/report_rule.md`，遵守它。
逐頁規格唯一來源：`ROOT/OUTLINE_v5.3.md`（已通過兩方兩輪審查，使用者已確認）。審查紀錄：`ROOT/REVIEW_v5.md`。
v4 舊頁與舊 BRIEF 備份在 `ROOT/old_v4_slides/`，只作版面參考，內容不能沿用。

## A. 內容規則

- 語言：繁體中文。技術名詞保留英文（SNV、CCF、clone、purity、haplotype、HP、phase block、read、BAM、SV）。
- 文字用 ASD-STE100 風格：一句一件事、短句、主動語態、先結論再原因。一個詞只用一個意思。
- 一頁一個重點。每頁正文最多約 4 個短句；頁面文字照大綱「頁面文字」那行，不要另加。
- 每個重點文字都要有對應的示意圖。頁面文字只描述當頁圖上畫出的事實。補充、限制、但書、推論放講稿。
- 圖先查 `report/VISUAL_SPEC.md`；照本檔 F 節草圖構圖。
- 有／無欄位只寫「有」或「無」，不加修飾小字。判準見 `OUTLINE_v5.3.md`「判準」。
- 區分論文描述／分析推論（見 H 節）。推論在講稿用口語說「這是我們的推論」。
- 不要編造數字。只用 `OUTLINE_v5.3.md` 與 E 節來源裡的數字。
- 講稿：`<aside>` 純文字，中文約 200–250 字。口語、能直接念。先講結論，再沿著圖講原因。引導觀眾看圖時用位置、顏色、上面的字指路。段落之間照大綱的橋接句。同一個但書全冊只講一次。
- 用詞與首次出現頁照 `OUTLINE_v5.3.md`「用詞首次出現頁」。術語第一次出現時用一句白話解釋。
- **代號禁用（頁面與講稿都禁止）**：論文代號 A01–A05、B03–B05、B07、M01、M02、M04–M07、R01、H01；病人代號 S8／S14／S20、PA04；C1／C2／C3a／C3b；EGA、MTA、Synapse、accession 編號；工具名 BAMSurgeon、PhaseTools、MuTect、Battenberg、TSSB、FS-CRP、Pairtree、CONIPHER、WhatsHap、Long Ranger、ScisTree。一律改用大綱的白話名稱（例如「肺癌長讀研究」「建樹競賽」「PhyClone 的四種模擬器」）。HG002 可以寫成「公開的標準正常人樣本」，講稿可提一次 HG002。
- 整份不出現小鼠子株研究，也不出現我們自己的 6 株細胞株。例外：第 7、8 頁可點名 HCC1395（CASTLE 公開 ONT，使用者 2026-10-20 同意）。

## B. 視覺系統（全 deck 一致，不要改）

字體：
- 標題：`font-family:'Noto Serif TC', Georgia, serif; font-weight:700`
- 內文：`font-family:'Noto Sans TC', Arial, sans-serif`（寫在 section 上讓它繼承）
- 程式碼／欄位名：`font-family:'JetBrains Mono', 'Courier New', monospace`

字級（只用這五級）：96（封面標題）、64（頁標題 h2）、40（卡片標題 h3／大數字說明）、30（內文）、24（標籤、表格小字、頁尾）。大數字可用 96。

顏色：
- 深色字 `#1F2A37`；次要字 `#4A5568`；淡字（頁尾）`#6B7480`
- 背景 A（主要）`#F7F6F2`；背景 B（交替用，例如資料頁）`#EEF2F6`；卡片底 `#FFFFFF` 改用 `#FDFDFB`；卡片框線 `#D9DDE3`
- 強調 1（藍）`#2F6DB5`；強調 2（橘）`#C96A1B`；壞／警告 `#B4442F`；好／通過 `#2E7D4F`
- 深色宣告頁背景 `#1F2A37`，上面字用 `#F7F6F2`，次要字 `#BFD0E0`
- Haplotype 固定配色（與舊 PPT 圖一致）：HP1 `#2C5F9E`、HP1-1 `#8FB3E0`、HP2 `#D9772B`、HP2-1 `#F2B880`、SNV 標記 `#D23A2E`、unphased `#9AA3AE`
- 顏色不能單獨表達意思：旁邊一定要有文字。

版面骨架（每張內容頁都一樣，位置不可跳動）：

```html
<section id="ID" style="background:#F7F6F2;color:#1F2A37;font-family:'Noto Sans TC', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:700;color:#2F6DB5;letter-spacing:2px">1 · 這種資料存在嗎</p>
<h2 style="font-family:'Noto Serif TC', Georgia, serif;font-size:64px;font-weight:700;line-height:1.15;color:#1F2A37">頁標題（一句結論）</h2>
<div style="flex:1;display:flex;gap:40px"> …內容… </div>
<div style="position:absolute;left:128px;right:128px;bottom:64px;display:flex;justify-content:space-between">
<p style="font-size:24px;color:#6B7480">2026-10-21 腫瘤演化樹研究進度</p>
<p style="font-size:24px;color:#6B7480">NN / 10</p>
</div>
<aside>講者備註</aside>
</section>
```

- eyebrow（第一行小字）依段落：P3–P4 寫 `1 · 這種資料存在嗎`；P5–P8 寫 `2 · 前人怎麼做資料`。封面、主問題、總結不放 eyebrow。
- 頁標題寫成一句結論，不要只寫名詞。標題最多兩行。
- 卡片：`background:#FDFDFB;border:1px solid #D9DDE3;border-radius:16px;padding:32px`，不要設固定 height。
- 表格：`<table style="font-size:26px;color:#1F2A37">`，第一列 `<th>`，每格 `width:N%` 寫在第一列；表頭列 `<tr style="background:#E3E8EF">`。
- 圖片：`<img src="/_blob/..." alt="…" style="width:…px;height:…px;object-fit:contain">`，放在 `background:#FFFFFF` 的圓角框裡。圖片下加 24px 出處說明。
- 可視區：1664×824（扣頁尾後實際內容高度約 800px，從 y=128 到 y=920）。估算高度：行高約 字級×1.4；表格列約 2.1×字級。放不下就刪字，不要縮字到 24 以下。
- 文字寬度：中文每字約 1×字級寬。卡片寬度要容得下最長的英文單字（0.6×字級／字元）。

## C. 格式子集（違反會被丟掉）

- 只能有一個 `<section id="ID" …>`，id 等於檔名，前後不能有任何東西。不能有 `<html> <head> <style> <link> <script> class`。
- 所有樣式 inline。禁止：`margin`、`z-index`、`em`、`rem`、`%` 字級、`var()`、`float`、`grid-area`、`colspan/rowspan`、巢狀清單。
- 可用元素：`h1 h2 h3 p ul ol li br b i u span(只能設 color) a div img table tr th td svg hr x-shape x-icon x-connector aside`。
- `<x-shape kind="rect|rounded|ellipse|diamond|arrow-right|arrow-left|arrow-up|arrow-down|line" style="background;border;width;height">`；箭頭長寬比接近 2:1。
- `<x-connector x1 y1 x2 y2 head="end|both|none" route="straight|hv|vh|elbow" style="color:#…;border-width:3px">` 以 slide 座標（px）定位，或放在 `position:relative` 的 div 裡以 div 座標定位；它是 pinned 圖層，不能設 left/top/width/height。
- `<x-icon name>` 只能用：Activity Book Chart Chat Check CheckCircle Clock Cloud Code Database Globe GraduationCap Home Key Lightbulb Lightning Link Lock PaperPlane Play Search Settings Star ThumbsUp Tool Trust Users Verified Warning Wrench。
- `<svg aria-label="…" width height viewBox>`：只能畫圖形，不要用 `<text>`（字型不會載入）。文字標籤用 pinned `<p>` 疊上去。svg ≤52KB。
- `position:absolute` 的子元素要給 width。一個 div 內最多 24 個 pinned 子元素。每頁最多 200 個元素，div 最多 15 層。
- 勾叉符號不要用 ✓✗，用 `<x-icon name="Check">` 或文字「有／無」。
- 標點：中文用全形標點。

## D. 舊圖

不用舊圖。所有圖都用 div／x-shape／x-connector／svg 重新畫。

## E. 主要事實來源（需要細節時讀這些檔；路徑相對於 repo 根目錄）

- `research/literature/paper_categories.tsv`（分類、篇數；扣除 B01 後 21 篇）。
- 各篇 README：路徑在 TSV 的 `readme` 欄（相對於 `research/`）。
- `report/2026_10_21_slides/REVIEW_v5.md`（兩輪審查查得的事實：樹種類、細胞數、資料取得）。
- `research/literature/surveys/patient_sc_longread_2026/ONT_DATA_AVAILABILITY.md`（資料取得；只涵蓋有 sc 樹的 9 篇）。
- `research/phyclone_research/notes/zh-TW/03_EXPERIMENTS*`（PhyClone 模擬器）。

## F. 逐頁規格與草圖

總頁數 10（P4 拆頁後）。頁碼＝`project/deck.json` 的 order 位置（cover＝1）。內容照 `OUTLINE_v5.3.md` 同頁。

| 頁 | id | eyebrow | 製作 subagent |
|---|---|---|---|
| P1 | `cover` | — | 甲 |
| P2 | `agenda` | — | 甲 |
| P3 | `s1-count` | 1 · 這種資料存在嗎 | 乙 |
| P4 | `s1-terms` | 1 · 這種資料存在嗎 | 乙（後加） |
| P5 | `s1-features` | 1 · 這種資料存在嗎 | 乙 |
| P5c–e | `s1-feat-lung`、`s1-feat-methyl`、`s1-feat-pair` | 1 · 這種資料存在嗎 | 主 agent（2026-10-20 追加，頁尾 7–9 / 10） |
| ~~P5b~~ | ~~`s1-read-features`~~（2026-10-20 使用者刪除，不要復原） | 1 · 這種資料存在嗎 | 主 agent（2026-10-20 追加，頁尾 6 / 10） |
| P6 | `s2-sim-layers` | 2 · 前人怎麼做資料 | 丙 |
| P7 | `s2-smchet` | 2 · 前人怎麼做資料 | 丙 |
| P8 | `s2-sc-trees` | 2 · 前人怎麼做資料 | 丁 |
| P9 | `s2-longread` | 2 · 前人怎麼做資料 | 丁 |
| P10 | `summary` | — | 甲 |

草圖：

```
P1 cover（深色宣告頁）
  大標：有真值樹又有 long read 的建樹資料存在嗎？
  小字：2026-10-21 實驗室會議

P2 agenda
  主問題一句（大字）
  [卡片 藍] 存在嗎？        [卡片 橘] 前人怎麼做資料？
  每張卡一行白話說明＋一個小圖示（放大鏡／流程箭頭）。卡片不標段落編號。

P3 s1-count
  上：細胞團 → 一顆顆細胞 → 細胞樹 ⇄「評分」⇄ bulk 樹（VISUAL_SPEC §8 簡化）
  下：篇數表
              驗證用真值  局部佐證  只有參考樹  無
     短讀        2          2         7        6   (17)
     長讀       [0]         1         0        3   (4)
  結論：長讀 × 驗證用真值＝0（橘框）

P4 s1-features
  左小圖（VISUAL_SPEC §3 簡化）：HP1／HP2 兩條、reads 上色、兩段 phase block 括號、
        一條長 read 跨兩個紅點＝同 read 共現
  右矩陣：6 列＋PhyClone 對照列（灰底分隔）× 6 欄，格子只寫「有」「無」；
        「真值樹」欄全部「無」用橘框強調；PhyClone 列「有」
  結論：同時有 HP 與 PS 的只有肺癌長讀研究，它的真值樹欄是「無」

P5b s1-read-features（2026-10-20 使用者確認）
  標題：三篇都用同一條 read 上的多個位點，用在不同步驟
  三欄卡片（肺癌長讀研究｜甲基化條碼研究｜配對 read 建樹方法），每欄一張小圖：
   左：HP1 長條＋跨兩個紅點的長讀 → 2 棵候選樹，虛線挑 1 棵（人工）
   中：HP1 長讀上一串甲基化 ●○ → read 的樹
   右：短讀 pair 兩端各蓋一個突變 → 組合計數 → 機率模型 → 樹
  下方三列：長讀 有/有/無；HP 分相 有/有/無；用在哪一步 事後挑樹/直接建樹/放進機率模型

P5c–e 三篇各一頁拆解（2026-10-20 使用者要求「每個特徵單獨一頁、配圖、數字先不放」）
  共同版面：三張步驟卡 ① 資料 → ② 訊號 → ③ 建樹，每卡一張示意圖＋圖例＋兩行圖說；底部「用在哪一步」標籤（同總覽頁配色）。
  s1-feat-lung：①HP1/HP2 長條，長讀跨兩個紅點 ②●●、●○、○○ 三種 read，「○●」打叉 → 左早於右 ③短讀給分支／線性兩棵候選，虛線從長讀指向線性樹（人工挑選）
  s1-feat-methyl：①細胞譜系，每顆細胞下方 5 格條碼，橘框＝新改變 ②混合 read 依 HP 分成兩堆 ③HP1 read×位點矩陣 → 樹，深色大群≈主要 clone
  s1-feat-pair：①短讀 pair 兩端各蓋一點，虛線＝同一對，單端 read 也保留 ②兩個 clone 各一張 2×2 小表 → 預測柱≈觀測柱 ③三棵候選樹＋機率柱，循環箭頭＝反覆抽樣
  clone 顏色：clone 1 #4A5568、clone 2 #2A9D8F、clone 3 #7B5EA7（沿用封面）；甲基化：實心 #1F2A37＝有、空心＝無。

P5 s2-sim-layers
  三欄由左到右（越接近真實定序）：
   事件層：樹 → 拷貝數 profile（階梯線）     代表 1 篇
   計數層：樹 → clone 比例 → 數字表(ref/alt)  代表 5 篇
   read 層：read 條 → 植入紅點 → BAM          代表 1 篇
  下方一條橫軸：「有 read 序列？」無／無／有；「長讀？」無／無／無
  標題數字 7／1／0 要能在圖上數到

P6 s2-smchet
  六步橫向流程（方塊＋箭頭）：正常人短讀 → 定相分兩份 → 切 read 池(haplotype×染色體)
   → 調深度(clone 比例、拷貝數) → 植入 SNV/SV(子帶父) → 合併 BAM、呼叫變異
  read 池畫成兩色條（HP1 藍、HP2 橘），紅點只植入其中一色
  右端：參賽者只拿到「變異清單」（read 圖示打斜線底＝看不到）

P7 s2-sc-trees
  兩欄：標靶 panel（3 格）｜淺層全基因體（5 格）
  每格：癌別、細胞數、樹種類標籤（SNV 樹／拷貝數樹）、✓/✗ 圖示＋文字「評分」「未評分」
  ✓ 兩格（卵巢癌單細胞研究、卵巢癌細胞株）加藍框

P8 s2-longread
  表：樣本｜平台｜樹的來源｜驗證用真值樹｜BAM 可下載
   4 列進入分析 + 最下 1 列「只做驗證」（灰底）
  「驗證用真值樹」欄全部「無」；「BAM 可下載」只有肺癌細胞株「有」（藍框）

P9 summary
  兩張回答卡：存在嗎 → 不存在（一句）；前人怎麼做 → 7／1／0、真值 2 篇都短讀
  下方一條「對我們的參考（推論）」：長讀版 read 層模擬 → 驗證樹形
```

## G. 來源記錄（講稿不放路徑，來源寫在這裡）

| 頁 | 來源 |
|---|---|
| s1-count | `research/literature/paper_categories.tsv` 的 `sc_truth_strength` 與 `platform_class`（扣 B01）；R01 README:34（選文期間外） |
| s1-features | TSV `long_read_role`／`long_read_features`／`cross_tags`；B04、M02、B09 README；資料取得見 REVIEW_v5.md。B09 的「甲基化」欄指建樹用到 per-read 5mC pattern；PS 欄填無，因論文沒寫用 phase block（2026-10-20 加入） |
| s1-read-features | B04 README（supplement p.19–20 Fig. S9c–d：ClonEvol 候選中依長讀選 linear）；B09 README（LongPhase haplotag、modkit per-read 5mC、Hamming＋UPGMA）；M02 paper.txt p.8–12（8 類 read multinomial、Z 與 T 聯合 MCMC）、README |
| s1-feat-lung | B04 paper.txt:336–361（EGFR 只有雙突變、mutation pair 排序、NKAIN4–BIRC7 例）；supplement.txt:1080–1098（S14 依長讀選 linear） |
| s1-feat-methyl | B09 paper.txt L.16（擴張後條碼收縮成兩組＝兩條 haplotype）、L.31–33、L.52、L.80–82 |
| s1-feat-pair | M02 paper.txt p.8–12（8 類 read、A(s,z)、tree prior、MCMC）、p.17–19（Sim 2） |
| s2-sim-layers | M01（03_EXPERIMENTS:28、73–75）、M02 README:44–50、107、M04 README:135–150、M05 README:141–157、M06 README:141–160、M07 README:51–66、B05 README:48 |
| s2-smchet | M07 README:51–66（論文 Methods p.13）；長讀版難點為第一輪教授審查推論（REVIEW_v5.md「應改」） |
| s2-sim-plan 困難情境 | 兄弟 clone CCF 接近：`report/VISUAL_SPEC.md` §7、M02 README（Sim 2）、`sources/s5908_text.md:170-177`；subclonal CN：`VISUAL_SPEC.md` §4、PhyClone notes 02 §S1.2、M07 README:134；低 purity／低深度：PhyClone notes `zh-TW/06_ASSUMPTIONS_LIMITATIONS.md:76`、M07 README:116-125（NRPCC）。三個情境的挑選屬分析推論 |
| s2-sc-trees | REVIEW_v5.md 待查核答案 2；A01–A05、B03、R01、M06 README；M06 paper.txt:234–241、266–269 |
| s2-longread | B04、B09、B03、H01 README（B09：PD6646 MPN 病人，ONT R9.4.1，真值是 Williams 2022 colony WGS 樹；論文沒有 data／code 連結） |
| summary | 前述各頁 |

## H. 證據類型與假想值

- 2026-10-20：篇數改為 18 篇（加入 B09 Hackett 2026）。長讀 × 驗證用真值 由 0 改為 1。B09 只用目視比對與 clade fraction，這個但書只在 s1-count 講稿講一次。
- 2026-10-20：使用者刪除 s1-read-features（總覽頁），指示不要復原。以下為刪除前紀錄。
- 2026-10-20：加 s1-read-features。「用在哪一步」屬論文描述；「右邊做法最值得借用」屬分析推論，講稿口語標明。三張小圖的 read 與 ●○ pattern 是示意，不是實測。
- 2026-10-20：P5c–e 的 read、條碼、柱高與樹形都是示意，不是實測。頁面不放數字（使用者指定）。
- 2026-10-20：頁尾改為真實頁數（目前 order 共 5 頁：cover、s1-features 2/5、s1-feat-lung 3/5、s1-feat-methyl 4/5、s1-feat-pair 5/5）。F 節的「NN / 10」與頁碼欄已過時，以 deck.json order 為準。
- 2026-10-20：使用者要求全冊刪除 TreeClone（配對 read 建樹方法），因為它是短讀，怕被誤會成長讀方法。s1-features 刪掉該列，標題改「2 篇」；s1-feat-pair 從 deck 移除（本地檔保留，不要再發布）。頁尾改為 2/4、3/4、4/4。
- 2026-10-20：使用者指定在 s1-feat-lung 步驟 ③ 標出候選樹來自 PyClone-VI + ClonEvol（B04 paper.txt:1689–1697；論文 Methods 誤植為 PyClone-IV）。工具名禁用規則對這兩個名稱例外。
- 2026-10-20：新增 s2-sim-plan（第 5 頁，新段落「2 · 我們怎麼驗證」）。內容取自對話中「模擬資料的用途」兩段說明。①計數層模擬的四根長柱是示意，不是結果；整頁是分析推論（研究計畫），講稿已口語標明「這頁是計畫，還沒有結果」。甲基化頁講稿結尾改為橋接到本頁；頁尾改為 /5。
- 2026-10-20：使用者要求刪除 s2-sim-plan 的 read 層模擬（認為做法怪怪的，是否輸出比對檔未定）。本頁只保留計數層模擬，底部情境改為「模擬要製造的困難情境」。
- 2026-10-20：s2-sim-plan 依使用者留言補上中間步驟，流程改為五格：設計的樹 → 直接產生計數 → 新軟體（吃進模擬計數、加入 long read 訊號）→ 新軟體輸出的樹 → 和設計的樹比對：樹的準確度（示意）。（線上版由留言自動處理完成，本地已同步。）
- 2026-10-20：s2-sim-plan 第 2 格依使用者留言改為 IGV 風格 read 堆疊圖（紅＝alt、白＝ref，四組 read 數 3／2／0／3 為示意）。
- 2026-10-20：s2-sim-plan 第 1 格改為 HP1／HP2 兩棵並排的設計樹：HP1 上 SNV1 在主幹（root→clone 1）、SNV2 在 clone 1→clone 2；HP2 上 SNV3 在 clone 1→clone 3。與 IGV 格一致：帶 SNV2 的 read 一定帶 SNV1，所以「只有右 alt」為 0。
- 2026-10-20：s2-sim-plan 第 2 格 IGV 圖改為依 HP 分區，並補上 SNV3 欄。示意 read 數：HP1 區 SNV1+SNV2 alt 2、只有 SNV1 2、只有 SNV2 0、全 ref 2；HP2 區 SNV3 alt 2、全 ref 1（取代先前的 3／2／0／3）。
- 2026-10-20：依使用者留言，s2-sim-plan IGV 圖右側的 read 數字已移除，只保留 read 堆疊（組內 read 條數仍為示意）。
- 2026-10-20：依使用者留言，s2-sim-plan 先刪除所有 pair 相關內容：準確度圖只剩 PhyClone 與 +HP 兩根柱，圖例刪 +HP+pair 與打亂 pair，圖說刪「打亂 pair 後增益消失」，講稿同步刪除。
- 2026-10-20：依使用者留言新增第 6 頁 s2-sim-check（迴歸對照：PhyClone 原始短讀資料集同時跑 PhyClone 與新軟體，兩棵樹差距要小；計畫，無結果）。新增時第 5 頁被退回含 pair 的舊版，已重新刪除 pair。頁尾改為 /6；第 5 頁講稿結尾橋接到第 6 頁。本地 deck.json 已與線上同步。
- 2026-10-20：使用者把 s2-sim-check 移到第 5 頁、s2-sim-plan 移到第 6 頁，並把第 6 頁標題改為「產生有 long read 特徵的模擬資料來驗證」。已依新順序修正頁尾（5/6、6/6）、段落 s4 起點（s2-sim-check）與三頁講稿的前後銜接。
- 2026-10-20：s2-sim-plan 第 4 格「新軟體輸出的樹」改為 HP1／HP2 兩棵並排、標 SNV1–3，格式與設計樹相同；比對得分格縮為 240px 以容納。
- 2026-10-20：s2-sim-check 比對標準沿用 PhyClone 論文的 AD F-score（祖先—後代關係）與 V-measure（突變分群），來源 phyclone_research/notes/03_EXPERIMENTS_RESULTS.md:13–14（Main §2.4.3）。講稿已用白話解釋兩個分數。
- 2026-10-20：s2-sim-check 比對方塊加上兩個指標示意圖：AD F-score 用灰（PhyClone）藍（新軟體）兩圈重疊表示祖孫關係重疊；V-measure 用上下兩排色點表示分群一致度，一點不一致。皆為示意。
- 2026-10-20：s2-sim-plan 最右格的準確度長柱改為沿用 s2-sim-check 的 AD F-score（重疊圓）與 V-measure（兩排色點）示意圖；此頁灰＝設計的樹、藍＝新軟體輸出的樹。講稿已同步。
- 2026-10-20：新增第 7 頁 s2-real-ref、第 8 頁 s2-real-consistency（同段「2 · 我們怎麼驗證」，真實資料驗證）。大綱 `OUTLINE_real_data.md`（兩方審查後 v2，使用者確認）。使用者決定：可點名 HCC1395（CASTLE 公開 ONT）；第 8 頁右欄「同一條 read 上兩個 SNV」檢查保留，只當驗證，不進入建樹，不寫 pair。本段因此為 4 頁，超過每段 2 頁的預設，屬使用者選擇。頁尾全部改 /8；第 6 頁講稿結尾橋接到第 7 頁。
- 2026-10-20：第 7 頁參考樹來源：SEQC2（Fang et al. 2021 Nat Biotech）Fig. 4a，`research/hcc1395_golden_tree_research/hcc1395_golden_tree.pdf` p.7，已目視確認 driver 所在邊。參考樹是多平台 bulk 資料加 PhyloWGS 推出的候選樹，不是真值；PhyloWGS 輸入未公開，不能算 SNV 層級 AD F-score。S、CCF% 屬論文描述。
- 2026-10-20：第 7、8 頁的得分、柱高、一致度都是示意，不是結果；整段屬分析推論（計畫）。nominal purity 20%–100% 是混合設計比例，不是實測 purity。
- 2026-10-20：依使用者留言，s1-feat-lung 步驟 ③ 兩棵樹節點補上 CCF：C-1 100%（黑 #1F2A37，原為灰）、C-2 40%（綠）、C-3 30%（紫）；SNV 標籤移到邊上；C-1／C-2／C-3 顏色圖例改成「節點旁 %＝CCF」，避免頁面變高。數值由使用者指定，尚未對照論文確認是否為實測值。
- 2026-10-20：依使用者指示，s2-sim-plan 底部三個困難情境各加一張原因示意圖：①真樹（分叉）與直線樹都符合同樣的 VAF；②40% 細胞多一份 HP1，HP1 上 SNV 的 VAF 偏高；③深度低時兩群 VAF 分布變寬重疊。圖上的 100%、40%、60%、柱高與分布形狀都是示意。講稿同步補上原因。
- 2026-10-20：依使用者指示，s2-sim-plan 的 subclonal CN 格改為三排對照（2 → 3 的例子）：控制組＝五顆細胞都是 1:1（✓ 一組 CN 就夠）；對照組＝五顆都是 2:1（✓）；subclonal＝三顆 1:1、兩顆 2:1，代表 60%／40%（✗ 一組 CN 不夠）。依使用者要求不放 CCF 數值；原本的「VAF 偏高」柱圖已移除。細胞顆數是示意。
- 2026-10-20：使用者澄清要比的是 main clone CN 與 subclone CN 的差異。s2-sim-plan 的 subclonal CN 格改為：main clone 三顆 1:1 細胞（CN 2）→ subclone 兩顆 2:1 細胞（CN 3，HP1 多一份），下方「✗ PhyClone 只收一組 CN」。取代前一版的控制組／對照組三排。細胞顆數是示意。
- 2026-10-20：使用者在線上把 s2-sim-plan 第一格標題改為「多 clone CCF 接近」；那次存檔基於舊版，蓋掉了 main clone／subclone 圖，已在保留該標題的前提下重新合併發布。
- 2026-10-20：依使用者指示，s2-sim-plan 的「低 purity／低深度」格改為兩個偏低的量表：purity → VAF 變小、depth → VAF 估不準（原寫「雜訊變大」，再改「VAF 不穩」，依使用者指示定為「估不準」），兩條箭頭匯合指向「CCF 不準」。取代原本的兩排 VAF 分布圖。量表填滿程度是示意。機制出處：M07 README:116-125（NRPCC）、PhyClone notes 06:76。
- 2026-10-20：刪除第 8 頁 s2-real-consistency。兩種一致性檢查（purity 稀釋一致性、long read 留出檢查）保留在驗證計畫，內容與原講稿移到 `OUTLINE_real_data.md`，原頁檔移到 `removed_slides/`。頁尾全部改 /7；第 7 頁講稿結尾補一句收尾；段落 s4 描述改為不含一致性檢查。
- 第 1–6 頁沒有假想數值（第 5、6 頁示意圖除外）。所有數字都來自論文或 TSV 計數。
- 分析推論（講稿要口語標明）：篇數分類本身；「長讀版建樹競賽流程可行」與其難點；「真值檔可能保留 haplotype」。
- 論文描述：各篇平台、細胞數、樹種類、模擬流程、資料取得方式。
- 本冊不涉及 purity 實測值；P8 講稿若提 purity，只用白話「腫瘤細胞比例」，不給數字。

## I. 收錄與排除清單（由 `report_rule.md` 搬來，2026-10-20）

主軸（2026-10-19 指定）：只分兩大段。
1. 文獻調查：有沒有研究同時用 single-cell 定序建立真值樹來驗證，並用長讀、haplotype、phase set 等特徵重建演化樹。
2. 各論文的模擬資料與真實資料怎麼產生，作為我們做驗證資料的參考。

收錄標準：論文至少要用一個建樹工具（現成軟體或自己的演算法）。只做 VAF 分群、畫圖（例如 Fishplot）或人工整理的樹不算。用現成工具也算，例如 ScisTree、ClonEvol。

排除清單（整份不放）：

| 論文 | 原因 |
|---|---|
| 小鼠子株長讀研究（Liu 2026） | 使用者指定 |
| HPV 整合長讀研究（Akagi 2023） | 不符收錄標準 |
| 骨髓瘤 linked-read 研究（Liu 2021） | 不符收錄標準 |
| 肝癌多點長讀研究（Zeng 2025） | 有 neighbor-joining 樣本樹，但使用者決定不收 |
| 肺癌細胞株長讀摘要（Donmez 2026，AACR 摘要） | 使用者指定 |

追加收錄：PCDH 甲基化條碼研究（Hackett 2026，2026-10-20 指定）。它用同一位病人的單細胞來源樹比對自己建的樹，所以「真值樹」填「有」。「只有目視比對、沒有量化分數」的但書只在 s1-count 講稿講一次。

篇數：扣除排除清單後 18 篇（加入 Hackett 2026 前是 17 篇）。

資料範圍：不放我們自己的 6 株 ONT 細胞株。已發表論文的細胞株資料（HCC1395 社群資料）可以列。

用語：全冊用「long read」，不用「長讀」（2026-10-20 使用者改指定；封面標題也是）。「短讀」維持中文，使用者未指定。

## J. 第 8 頁 s2-smchet-split（2026-10-21 加入）

- 使用者要求：第 8 頁新增 SMC-Het 對建樹問題的拆解，並列出 SMC-Het benchmark 的資料。使用者點名 SMC-Het，所以頁面標出這個名稱（「文字與表格」第 5 條例外）。
- 來源：`research/literature/papers/M07_smchet_benchmark_2024/README.md`；`pmc_fulltext.txt`（Results 第 1–2 段、Fig. 1 圖說）。
- 論文描述：7 個子題（1A purity、1B clone 數、1C CCF、2A／2B 分群確定版／機率版、3A／3B 樹確定版／機率版）；51 棵設計樹＝25 PCAWG＋16 文獻＋10 特殊情境；titration 5 個腫瘤 × 8×／16×／32×／64×／128×；HG002 300× Illumina 植入突變；參賽者只拿 SNV VCF、Battenberg CN segment 與 purity；BAM 在 EGA、calls 與真值在 Synapse；PhyClone 不在受測方法中。
- 分析推論（講稿口語標明）：「前一步錯，後一步通常跟著錯」；「可以補上 PhyClone 基線」。
- 示意：三張卡的柱高、點數、樹形，以及深度柱高（log 等距）都是示意。
- 頁尾全部改 /8；第 7 頁講稿結尾補橋接句。

## K. 第 4 頁 s1-feat-methyl 改版（2026-10-21）

- 使用者要求：寫明樹是由 PCDH 區的甲基化重建，並顯示 single-cell 真值樹。
- 步驟 ③ 改成兩棵樹並排：左＝一段 PCDHα（exon 2–4）window、HP1 read 的 UPGMA 樹；右＝PD6646 colony WGS 真值樹（Williams 2022）。
- 來源：B09 `paper.pdf` p.6 Fig. 4a（真值樹與 clade fraction 表：non-cancer 0.16、DNMT3A 0.84、JAK2:DNMT3A 0.65、CBL:DNMT3A 0.12、other:DNMT3A 0.07）與 Fig. 4c（haploid A／B dendrogram 形狀），已目視確認。論文的 haploid A 在頁面寫成 HP1。
- 配色：真值樹顏色改用本冊 clone 配色（DNMT3A／其他 #4A5568、JAK2 #2A9D8F、CBL #7B5EA7、非癌 #8E99A8），不用論文原色。
- 示意：左邊 read 樹的色條長度大致依真值比例畫，樹的細節是簡化示意，不是逐 read 重畫。
- 論文描述：「closely resembled」是目視比對；分支長度不符（L.33）。
- 真值樹的百分比是論文值，屬論文描述；這是「細節數字先不放」規則的例外，因為比對的就是 clone 大小。
- 2026-10-21：依使用者指示，在 ② 與真值對照之間補上「③ 甲基化矩陣 → UPGMA 建樹」，真值對照改為 ④。內容取自 B09 paper.txt L.80–82：每個 HP 一個 read × CpG 矩陣，缺值用 Hamming 距離 kNN（k=3）補，再用 Hamming 距離＋average linkage（UPGMA）分群。卡上 8 列 × 10 欄矩陣、缺值位置與樹形都是示意。四張卡寬度改為 290／290／324／640。
