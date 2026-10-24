# 2026-10-21 簡報：共用規格（給每頁 subagent）

Repo 根目錄：`/bip8_disk/boyu114/main_work`。Deck 原始檔根目錄 `ROOT=/bip8_disk/boyu114/main_work/report/2026_10_21_slides`。
每頁寫成 `ROOT/project/slides/<id>.html`。先讀 `report/report_rule.md`，遵守它。

## A. 內容規則

- 語言：繁體中文。技術名詞保留英文（SNV、CCF、clone、topology、purity、haplotype、HP、PS、multiplicity、VAF、CN）。
- 文字用 ASD-STE100 風格：一句一件事、短句、主動語態、先結論再原因。一個詞只用一個意思。
- 一頁一個重點。內容簡單，只講重點。每頁正文最多約 4 個短句。
- 每個重點文字旁邊都要有對應的手畫生物示意圖（染色體、haplotype、read、SNV、clone tree 等）。構圖照 `VISUALS.md` 的描述畫，不要憑印象。
- 不要用 D 節的舊圖。舊圖只作參考，所有圖都用 x-shape／div／x-connector／svg 重新畫。
- 有／無欄位只寫「有」或「無」，不加修飾小字。平台只寫「長讀」或「短讀」。
- 區分「論文描述」「程式實作」「分析推論」。推論要標「推論」。nominal purity 不是實測 purity。
- 不要編造數字。只用本檔與指定來源檔裡的事實。拿不準就不寫。
- 講稿：`<aside>` 純文字，中文約 200–250 字（約一分鐘）。口語、能直接念（可用「我們」「大家看這裡」）。先講這頁結論，再沿著圖講原因。不用黑話；術語第一次出現時用一句白話解釋（照 `OUTLINE.md` 用詞表）。**不放 repo 路徑、章節編號、內部代號**；來源記錄寫在本檔 G 節。
- 頁面文字只描述當頁圖上畫出的事實。補充、限制、但書、推論細節放講稿。頁面上不放「註：…」「出處：…」小字。
- 黑話禁用清單（頁面與講稿都禁止）：C1／C2／C3a／C3b、B04、K1–K12、F1–F5、C0–C6、Phase 0、L0–L3、PS、CP、AD、sc3、1A–3B、Battenberg、MuTect、ASCAT、PyClone-VI、ClonEvol、tumour_content、major_cn、minor_cn、ref_counts、alt_counts、normal_cn、S14 等病人代號。改說白話（「肺癌論文」「會議摘要」「樹分數」「祖先關係分數」「拷貝數工具」「分群程式」「選樹程式」）。

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
<p style="font-size:24px;font-weight:700;color:#2F6DB5;letter-spacing:2px">1 · 現象</p>
<h2 style="font-family:'Noto Serif TC', Georgia, serif;font-size:64px;font-weight:700;line-height:1.15;color:#1F2A37">頁標題（一句結論）</h2>
<div style="flex:1;display:flex;gap:40px"> …內容… </div>
<div style="position:absolute;left:128px;right:128px;bottom:64px;display:flex;justify-content:space-between">
<p style="font-size:24px;color:#6B7480">2026-10-21 腫瘤演化樹研究進度</p>
<p style="font-size:24px;color:#6B7480">NN / 10</p>
</div>
<aside>講者備註</aside>
</section>
```

- eyebrow（第一行小字）依段落：`1 · 現象`、`2 · 原因`、`3 · 空缺`、`4 · 解法`、`5 · 驗證`。補充頁在 eyebrow 後加 `　補充頁`（例：`2 · 原因　補充頁`），表示這頁是為了補邏輯缺口新增。
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

## D. 舊圖（只作參考，不要放進投影片）

| 檔 | src | 內容 |
|---|---|---|
| image1 | `/_blob/68daaa3d0374b57c56a408cf18917eea` | 文氏圖：短讀建樹、長讀建樹、單細胞演化樹；短讀樹有單細胞驗證；長讀樹與單細胞樹無交集（2720×2080） |
| image2 | `/_blob/357e58020dc958c4c6d9d61c62ec5967` | 模擬資料 vs 真實資料示意圖（2200×990） |
| image3 | `/_blob/8b2078968e7270e46719fc5fa064fa13` | HCC1395 clonality 魚形圖（SuperFreq 類輸出，487×245） |
| image4 | `/_blob/81fa5248182368288f29519639c5bbf7` | HCC1395 Fang 2021 分支樹 S1–S10（PhyloWGS，411×337） |
| image5 | `/_blob/58dd9314740a410cd6c2d48eebe8e69e` | 由 clonality 畫出的線性樹 正常→A→B→C→D→E（229×484） |
| image6 | `/_blob/5fac6b5906db01d8034f4d875f716e0e` | PhyClone 論文 Fig.6：HGSOC p3 ground truth vs PhyClone/CONIPHER/Pairtree/fastBE/Orchard（2129×1056） |
| image7 | `/_blob/dd722553b6da12f3665bd4633ed6bac9` | B04 肺癌論文流程圖：SNP calling、long read phasing、突變加 haplotype（1446×440） |
| image8 | `/_blob/d8faebe8b48f5322c100f12644e0fe52` | B04 S14-T：branched vs linear 模型，long read 雙突變 reads 支持 linear（877×554） |

## E. 主要事實來源（需要細節時讀這些檔）

- `research/literature/PAPER_CATEGORIES.md`：22 篇分類 C1/C2/C3a/C3b。
- `research/literature/SYNTHESIS_phyclone_longphase.md`：跨論文設計約束 K1–K12。
- `research/literature/surveys/methods_survey/workers/W8_benchmark_update_2026-10-18.md`：新 benchmark 調查、Liu 2026。
- `research/literature/papers/M07_smchet_benchmark_2024/README.md`：SMC-Het。
- `research/literature/papers/B04_lung_longread_phasing_2022/README.md`：B04。
- `plan.md`（§0 驗證層 L0–L3、§2 架構 C0–C6、§3 特徵 F1–F5、§4.5 pair 條件）。
- `data_input.md`：HCC1395 tagged BAM、PhyClone baseline run。
- `evaluation_v1.md`：評估指標（§2.2–2.7）。
- `tumor_sample.md`：細胞株 CRAM、PhyClone 資料集。
- `/tmp/claude-1024/-bip8-disk-boyu114-main-work/23ba803e-44e2-4cf9-8ce6-3e6e92e46d5c/scratchpad/s5908_text.md`：輸入輸出調查、clone 定義、subclonal CNA、SMC-Het 摘要（2026-10-18 session 紀錄）。

## F. 逐頁規格

以 `OUTLINE.md`（v4.2，方案 B，已通過兩方三輪審查）為唯一逐頁規格與用詞表。總頁數 10，頁碼＝`project/deck.json` 的 order 位置（cover＝1）。v3.2（13 頁）規格作廢，備份在 `OUTLINE_v3.2.md`；舊頁備份在 `old_v3_slides/`。

| 頁 | id | 段落 eyebrow | 舊頁可參考 |
|---|---|---|---|
| P1 | `cover` | — | cover |
| P2 | `agenda` | — | agenda |
| P3 | `s1-hcc1395` | 1 · 現象 | s2-hcc1395、s1-gap 左側概念圖 |
| P4 | `s2-phyclone-io` | 2 · 原因 | s3-phyclone-io |
| P5 | `s2-pitfalls` | 2 · 原因 | s3-pitfalls（陷阱 2 例子要整個換掉） |
| P6 | `s3-gap` | 3 · 空缺 | s1-gap 右側矩陣＋s1-lung |
| P7 | `s4-hp` | 4 · 解法 | s4-hp（右下小圖換成 P5 新例子） |
| P8 | `s4-pair` | 4 · 解法 | s4-pair |
| P9 | `s5-validate` | 5 · 驗證 | s2-data＋s5-score 右半 |
| P10 | `summary` | — | summary |

## G. 來源記錄（講稿不放路徑，來源寫在這裡）

| 頁 | 來源 |
|---|---|
| s1-hcc1395 | `data_input.md` §2；`/bip8_disk/boyu114/phyclone/hcc1395_input/RECORD.md`（30,368 SNV、purity 0.99 文獻值、5 群線性、3 群 MAP 分支、0.65＋0.26＝0.91 ≤ 0.98、抽樣線性 19,953／分支 20,047） |
| s2-phyclone-io | `research/phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md`（輸入 schema、輸出、單一 CN 假設）、`01_PAPER_BIG_PICTURE.md` |
| s2-pitfalls | `VISUALS.md` §4、§7；`research/phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md`:66–68（multiplicity 列舉後積分）；陷阱 2 數字為本 repo 推算（60%/40%、VAF 0.333、CCF 0.8／0.4） |
| s3-gap | `research/literature/PAPER_CATEGORIES.md`、`research/literature/paper_categories.tsv`（分類為本 repo 分析推論）；Sakamoto 2022 *Nat Commun* 13:3464 Supp. Fig. S9c–d；B04 README；M02 TreeClone README（短讀共現、只用拷貝數正常區） |
| s4-hp | `plan.md` §3.1–3.2；`research/literature/SYNTHESIS_phyclone_longphase.md` K1；`VISUALS.md` §3；HP 層級 VAF 0.8／0.571 為本 repo 推算 |
| s4-pair | `plan.md` §4.5.1–4.5.4；SYNTHESIS K2–K3；`VISUALS.md` §5；突變密度 3.1 Gb ÷ 30,368 ≈ 102 kb |
| s5-validate | `tumor_sample.md`；`research/literature/surveys/methods_survey/workers/W8_benchmark_update_2026-10-18.md`；M07 README；`evaluation_v1.md` §2.2、§2.7；`data_input.md` §3（20,470 對 co-read 計數） |
| summary | 前述各頁 |
