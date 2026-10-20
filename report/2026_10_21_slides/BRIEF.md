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
- 整份不出現小鼠子株研究，也不出現我們自己的 6 株細胞株。

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

- `research/paper_categories.tsv`（分類、篇數；扣除 B01 後 21 篇）。
- 各篇 README：路徑在 TSV 的 `readme` 欄（相對於 `research/`）。
- `report/2026_10_21_slides/REVIEW_v5.md`（兩輪審查查得的事實：樹種類、細胞數、資料取得）。
- `research/tumor_phylogeny_2026/ONT_DATA_AVAILABILITY.md`（資料取得；只涵蓋有 sc 樹的 9 篇）。
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
| s1-count | `research/paper_categories.tsv` 的 `sc_truth_strength` 與 `platform_class`（扣 B01）；R01 README:34（選文期間外） |
| s1-features | TSV `long_read_role`／`long_read_features`／`cross_tags`；B04、M02 README；資料取得見 REVIEW_v5.md |
| s2-sim-layers | M01（03_EXPERIMENTS:28、73–75）、M02 README:44–50、107、M04 README:135–150、M05 README:141–157、M06 README:141–160、M07 README:51–66、B05 README:48 |
| s2-smchet | M07 README:51–66（論文 Methods p.13）；長讀版難點為第一輪教授審查推論（REVIEW_v5.md「應改」） |
| s2-sc-trees | REVIEW_v5.md 待查核答案 2；A01–A05、B03、R01、M06 README；M06 paper.txt:234–241、266–269 |
| s2-longread | B04、B03、H01 README |
| summary | 前述各頁 |

## H. 證據類型與假想值

- 全冊沒有假想數值。所有數字都來自論文或 TSV 計數。
- 分析推論（講稿要口語標明）：篇數分類本身；「長讀版建樹競賽流程可行」與其難點；「真值檔可能保留 haplotype」。
- 論文描述：各篇平台、細胞數、樹種類、模擬流程、資料取得方式。
- 本冊不涉及 purity 實測值；P8 講稿若提 purity，只用白話「腫瘤細胞比例」，不給數字。
