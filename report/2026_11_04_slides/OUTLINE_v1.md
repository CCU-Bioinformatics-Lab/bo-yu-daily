# 2026-11-04 報告大綱（v1，2026-11-01 擬）

## 主問題（C-2）

**改造後的模擬器（diplosim）比原版 CONIPHER 多做了什麼？它產生的資料，像不像真實的 long read bulk？**

- 使用者原話（2026-11-01）：「幫我製作 11_4 的報告，先完全按照 claude.md 裡面的指示，看看是否報告有比較順暢好懂」。
- 對照會議：`meeting_record/2026_10_28_meeting_record.md`（最新一次；沒有 `_summary.md`）。決議 1「說清楚相對原流程增加了什麼」、決議 2「關鍵設計與驗證問題先比較 2–3 個候選方案」、決議 3「用流程圖呈現中間思考」；待辦「探討 2–3 種驗證方法，釐清 HG008／HCC 能支持什麼」。
- 用到的會議：2026-10-28（主）、2026-10-21 summary（L1–L7 與 §2.2 自我檢查清單）。
- 結構完全照 `CLAUDE.md`「交付」1–5；第 6 項（自我檢查）只寫在 `BRIEF.md`，不上投影片。

## 頁序（照 CLAUDE.md 交付 1–5）

### 交付 1：接回上次會議（1 頁）

**p1 大綱頁（W-4，同時是 L-1 開場）**
- 標題：diplosim 比 CONIPHER 多了什麼？產生的資料像不像真實 long read bulk？
- 研究目的：模擬帶 HP1／HP2 的 long read bulk 資料，用來測試 PhyClone 的 HP 擴充。
- 上次（10-28）定的 3 個方向與現況：
  1. 說清楚改了哪裡 → **可行**：diplosim 照 CONIPHER 一步一步移植，每個改動有紀錄。
  2. 先列 2–3 個驗證方法 → **選定一個**：和真實 HCC1395 long read 比較；HG008 single cell 樹 **未定**；TRACERx 統計 **排除**（short read）。
  3. 用流程圖呈現 → 每個任務都附流程圖。
- 本週 3 個任務（下面 3 段），每段一句。

### 交付 2＋3：本週任務、候選方案與選擇理由（每個任務 1–2 頁）

**任務 1：diplosim 相對 CONIPHER 改了哪幾步？**

p2 架構對照頁（L-10 架構圖做法）
- 標題：diplosim 沿用 CONIPHER 的 5 步，只在「放 SNV」與「產生 read 計數」兩步加上 HP1／HP2
- 左欄 CONIPHER、右欄 diplosim，同一列同一步：定參數 → 建樹 → 放 SNV 與 CN 事件 → 混合 clone（purity）→ 產生 read 計數。每格標「沿用／修改／新寫」，配小示意圖。
- 新寫項目（只列已進程式、預設值和 CONIPHER 不同或新增的）：SNV 落在 HP2 的機率 0.5（對稱改名）；read 計數拆成 HP1／HP2／HP0；同位置第二個 CN 事件；read 錯誤（base error、mistag）；位點 tag 比例不同；depth 變異（φ）。
- 來源：`diplosim/DECISIONS.md`〔程式〕。

p3 候選方案頁：read 計數怎麼拆成 HP1／HP2
- 標題：HP 計數拆分選方案 ②：照 CONIPHER 抽 depth 與 alt，再依 allele 份數拆 ref，最後一部分 read 變成 unphased
- 三個候選 ①計數後拆分、②①＋unphased、③逐條 read 產生；每個畫示意圖，寫優點／風險；選 ②，理由：HP1＋HP2＋HP0 等於 CONIPHER 的 depth、alt，CN 開著也能用。限制：沒有逐條 read，產生不了同 read 共現（延後，不是排除）。
- 圖：`diplosim/docs/figs/hp_split_compare.png`、`hp_split_option_2.png`。

**任務 2：怎麼驗證模擬資料像真實資料？**

p4 驗證方案頁
- 標題：三種驗證方法中，選「和真實 HCC1395 long read 比統計量」，因為它是唯一只用 long read、而且現在就能做的
- 先列需求（L-2）：只用 long read、能產生 HP1／HP2。
- ① TRACERx cohort 統計：short read → 排除。② 真實 HCC1395 ONT bulk 比統計量（PPC）：選定，但 HCC1395 沒有已知的 clone 樹，只能驗資料、不能驗樹。③ HG008 single cell 樹＋bulk ONT：能驗樹，未定。
- benchmark 第一句（L-3）：真值來源＝無（HCC1395 沒有 clone 樹，只比統計量）；讀長＝ONT long read；輸入＝ClairS somatic SNV＋HP pileup；生成程式＝diplosim（自己的）。
- 圖：`diplosim/docs/figs/validation_option_2.png`、`validation_option_3.png`。

**任務 3：只在一個 purity 上調好的設定，換到其他 purity 還成立嗎？**

p5 holdout 設計頁
- 標題：只在 purity 0.97 的樣本上調參數，再拿 4 個較低 purity 的同一株細胞樣本檢查
- 圖：5 個 subsample（t50…t10）的 tumor／normal 混合比例條，標 nominal 與換算 purity；t50 標「調參數」，其他 4 個標「檢查」；13 項統計量的示意（VAF、depth、HP0、tag、split alt、minor HP）。
- C-7：nominal（tumor reads 比例）和換算的細胞 purity 分開寫。

p6 候選方案與選擇頁（流程圖）
- 標題：低 purity 對不上的主因在 ClairS 與 purity 換算，不在 diplosim 怎麼產生資料
- 6 步流程（`lab_report/2026-11-01_diplosim_purity_summary/pipeline.png` 的結構）：每一步寫「發現的問題 → 候選 → 選了什麼」。
  ② 逐位點 mistag；③ 旋鈕範圍抽樣；④ 配對 normal＋ClairS 規則；⑤ purity 換算加入 normal 的 tumor 比例；⑥ ClairS 偵測曲線。
- 只放已做的步驟；φ 量測（沒選估計式）放講稿或 BRIEF。

### 交付 4：結果（含失敗）（2 頁）

p7 t50 起點結果
- 標題：用預設參數時，14 項統計量只有 5 項落在模擬範圍；調整後在 t50 上 12／13 項落在範圍內
- 圖：`lab_report/2026-10-30_diplosim_ppc_hcc1395/`（2026-11-04 刪除，未進 git，無法取回） 的圖（真實 vs 模擬分布），標「實際結果」。
- 預期 vs 實際：預期預設參數就接近，實際 HP tag、錯誤、LOH 三類對不上。

p8 5 個 purity 的結果
- 標題：6 步改動後，t20 從 3／13 升到 11／13，t10 從 1／13 升到 8／13
- 圖：`lab_report/2026-11-01_diplosim_purity_summary/progress.png`（左：通過項數；右：平均相對差距）。
- 失敗也列：t10 的 VAF 兩端分位、接近 0 的統計量、split alt 隨 purity 偏高、高 purity 的 call 數偏少、normal 的 alt 集中在少數位點、c 兩個估計不一致。
- 讀圖注意：③ 起改成範圍抽樣，區間變寬，項數上升有一部分來自這點；要和右圖一起看。

### 交付 5：懂／不懂（1 頁）

p9 懂／不懂
- 標題：已確認的 4 件事與還不知道的 4 件事
- 左「已確認（有證據）」：低 purity 差距主要來自量測端；ClairS 的 normal 規則（程式）；ClairS 用的 normal 和 t00_n25 同一批 read；t50 上 CN 分布對得上。
- 右「還不知道」：normal alt 為何集中；c 兩個估計為何不同；split alt 低 purity 偏高的原因；能否推廣到別的細胞株或 caller。
- 使用者自己的懂／不懂：**待使用者補**（BRIEF 也記）。

## 保留在計畫，不上投影片
- φ 從 normal 量測（估計式差 4 倍，沒選）：細節在 `lab_report/2026-11-01_diplosim_phi_from_normal/`。
- 同 read 共現延後的理由。
- 交付 6 自我檢查：寫在 `BRIEF.md`。

## 待確認
1. 3 個任務是否都要講？或只講任務 3（purity holdout），任務 1、2 縮成一頁背景？
2. p7 是否保留（t50 起點），或直接併入 p8？
