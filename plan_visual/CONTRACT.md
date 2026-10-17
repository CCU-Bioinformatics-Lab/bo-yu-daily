# 視覺化 plan.html 共用設計規格（所有 subagent 必須遵守）

內容來源：`/bip8_disk/boyu114/main_work/plan.md`（唯一事實來源，不可新增它沒有的技術主張；可以畫示意資料，但要標示「示意」）。
語言：繁體中文，技術名詞保留英文（SNV、CCF、multiplicity、PS、HP、read、topology…）。

## 產出格式

每個 subagent 只產出一個 **HTML 片段檔**（不要 `<html>/<head>/<body>/<style>` 標籤，不要 `<script>` 除非規格允許），放在
`/bip8_disk/boyu114/main_work/plan_visual/parts/<名稱>.html`。
片段最外層是 `<section id="<錨點>" class="sec">`，內含：
```html
<section id="xxx" class="sec">
  <header class="sec-head"><p class="eyebrow">章節標籤</p><h2>標題</h2><p class="lede">一兩句導言</p></header>
  ... 內容 ...
</section>
```

## 可用的 CSS class（由組裝者提供樣式，不要自己寫 <style>）

- 文字：`.lede` 導言、`.note` 小字註解、`.tag-impl` [程式實作]、`.tag-doc` [longphase-s 文件]、`.tag-infer` [分析推論]（行內 `<span>`）
- `code` 行內程式碼；`<pre class="code">` 程式碼區塊
- `.fig` 圖容器：`<figure class="fig"><div class="fig-scroll"> <svg ...> </div><figcaption>說明</figcaption></figure>`（`.fig-scroll` 會 overflow-x:auto）
- `.grid2` 兩欄（窄螢幕自動一欄）、`.grid3` 三欄
- `.card` 有框卡片（少用）；`.callout` 強調框；`.callout.warn` 警示框
- 表格：`<div class="tbl"><table>...</table></div>`
- `.chip` 小標籤，可加 `.hp1 .hp2 .hp11 .hp21 .hp3 .un .mod` 上色
- `.mono` 等寬字

## SVG 規則（重要）

1. **只用 CSS 變數上色**，不准寫死顏色。用 `fill="var(--x)"` 或 `style="fill:var(--x)"` 或 class。所有可用 token：
   - 介面：`--bg` 頁底、`--surface` 面板、`--surface2` 次面板、`--fg` 主文字、`--muted` 次文字、`--line` 線條/格線、`--accent` 主強調色（藍綠）、`--accent-soft` 淡強調底
   - **HP 語意色（全頁一致）**：
     - `--hp1` haplotype 1（germline，ref read）
     - `--hp2` haplotype 2（germline，ref read）
     - `--hp11` HP:1-1（hap1 上帶 somatic alt 的 read）
     - `--hp21` HP:2-1（hap2 上帶 somatic alt 的 read）
     - `--hp3` HP:3（somatic 但無法歸 haplotype）
     - `--un` 未 tag read
     - `--alt` somatic alt 鹼基標記（IGV mismatch 色塊）
     - `--snp` germline het SNP 標記
     - `--bad` 被禁止／衝突、`--good` 允許／一致
   - 文字字型用 `font-family="var(--mono)"` 或 `var(--sans)`
2. SVG 一律 `viewBox` + `width="100%"`、不設固定 height（或用 `style="max-width:…"`），並加 `role="img"` 與 `<title>`。
3. viewBox 留邊界，標籤不可被切掉；文字大小 11–14（viewBox 單位，預期 viewBox 寬約 900–1000）。
4. 不要用漸層、陰影、emoji。
5. **IGV 風格**（read pileup 圖）：
   - 最上方：座標尺（chr + 位置刻度，用真實感座標如 `chr1:1,212,600–1,213,400`，標「示意」）
   - coverage track：灰色長條（`--un` 或 `--line`），SNV 位點的長條依 allele 分色（ref 部分 `--muted`、alt 部分 `--alt`）
   - read track：每條 read 是細長圓角矩形（高 8–10，間距 3–4），**依 HP 分組**，每組左側有組標籤（如 `HP:1`、`HP:1-1`），read 填色用對應 HP token 的淡化版（用 `fill-opacity="0.35"` + 同色描邊即可）
   - read 上的 mismatch：在位點畫小方塊 `--alt`（somatic）或 `--snp`（germline het SNP）
   - 位點用垂直虛線貫穿所有 track，上方標 SNV 名稱
   - PS block：在座標尺下方畫一條帶，標 `PS:1,198,442`
6. 若要互動（例如切換情境），可用 **純 CSS**（radio + :checked）或極少量 inline `<script>`，script 必須包在 IIFE 內、只操作自己 section 內的元素（用 `document.getElementById('<你的section id>')` 起始查詢），不可依賴外部函式庫。優先用靜態圖。

## 頁面整體結構（組裝者負責，供你了解上下文）

0. 頂部摘要（組裝者寫）
1. `#arch` PhyClone 架構流程 M1–M7（subagent A）
2. `#hp` longphase-s HP 標籤與 F1–F5 特徵（subagent B，IGV 圖）
3. `#c2c3` C2/C3：phase-aware multiplicity 與 haplotype-specific VAF（subagent C，IGV 圖＋數值例）
4. `#c4` C4：read co-occurrence topology 因子（subagent D，IGV 圖＋小樹）
5. 對照表 C0–C6、階段、風險（組裝者寫）
