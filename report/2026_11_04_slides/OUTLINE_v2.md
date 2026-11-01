# 2026-11-04 報告大綱（v2，2026-11-01）

v1 → v2：照使用者 2026-11-01 指示改主軸（見 `BRIEF.md` B-1）。不講 purity holdout 的模擬結果（① 到 ⑥ 的改動與通過數）。v1 審查意見中仍適用的部分已併入（見文末「v1 審查意見處理」）。

## 主問題（C-2）

**diplosim 比 CONIPHER 多輸出哪些 long read 資訊？要怎麼檢查這些資訊接近真實的 long read bulk？**

- 使用者原話（2026-11-01）：「先不要說明 diplosim 後面 purity 的結果，大致說到 conipher 和 diplosim 相比新增甚麼參數，並同時比喻為兩台機器輸出 bulk 定序模擬資料，並比較資訊量多寡，測試部分為了逼近真實癌腫的真實 bulk 定序資料，先拿 hcc1395 各不同 purity 來觀察各項數值，檢查是否能接近模擬出真實 long read 的資訊」。
- 對照會議 2026-10-28：決議 1「說清楚相對原流程增加了什麼」→ 第一段；待辦「探討驗證方法、釐清 HCC 能支持什麼」→ 第二段。
- 結構照 `CLAUDE.md`「交付」1–5；第 6 項只寫在 `BRIEF.md`。

## 頁序

### 交付 1：接回上次會議

**p1 大綱頁（W-4＝L-1 開場）**
- 標題：diplosim 比 CONIPHER 多輸出哪些 long read 資訊？怎麼檢查它接近真實資料？
- 研究目的：模擬帶 HP1／HP2 的 long read bulk 資料，用來測試 PhyClone 的 HP 擴充。
- 上次（10-28）的方向與現況：
  1. 說清楚改了哪裡 → **可行**：本週第一段。
  2. 列 2–3 個驗證方法 → **選定一個先做**：和真實 HCC1395 long read 比數值；HG008 single cell 樹 **未定**；TRACERx 統計 **排除**（short read）。
  3. 用流程圖呈現 → 每段都有圖。
  4. 同一條 read 上的 SNV 共現 → **延後**（不是排除）。
- 本週兩段，各一句：
  - 第一段：把 CONIPHER 與 diplosim 想成兩台機器，比較輸入的參數與輸出的資訊量。
  - 第二段：用 HCC1395 不同 purity 的真實 long read，定出要檢查哪些數值。

### 交付 2＋3：任務 1——兩台機器比什麼（候選方案與選擇理由）

**p2 兩台機器頁（比喻＋資訊量）**
- 標題：兩台機器吃相同的腫瘤設定，diplosim 把每個 SNV 的 read 計數從 2 個拆成 6 個（依 HP），並多一欄真值
- 圖：左右兩台機器（CONIPHER、diplosim），上方同一組輸入卡（clone 數、SNV 數、purity、coverage、CN gain／loss、WGD），下方各吐出一張「每個 SNV 一列」的輸出表，用同一個 SNV 當例子（E-1，用實際輸出的一列，標「實際結果」）：
  - CONIPHER：ref read 數、alt read 數（2 個計數）。
  - diplosim：同樣的 ref、alt，再拆成 HP1、HP2、HP0（unphased）各自的 ref／alt（6 個計數，加總等於左邊），加上「SNV 在哪條 allele」的真值欄。
- 資訊量比較：每個 SNV 從 2 個 read 計數變成 6 個；真值多一欄 allele。共用欄位不變（CONIPHER 24 欄，diplosim 31 欄＝24＋7）。〔程式，`conversion.py:31`、`diplosim.tsv` 表頭〕
- 頁底一列：多出的 HP 計數讓 PhyClone 能用什麼（例如同一 clone 的 SNV 分在同一條 HP）。

**p3 新增參數頁**
- 標題：diplosim 沿用 CONIPHER 的參數，另外新增 8 個參數，分別控制 HP 分配、HP 標記、read 錯誤、depth 與 CN
- 圖：機器的「旋鈕盤」，每組旋鈕旁畫它影響的輸出（F-9、C-18 參數頁做法：只寫控制什麼與預設／例子值，不寫範圍，不排先後）：
  - SNV 放在哪條 allele：`prop_snv_on_b`（預設 0.5；設 0 時和 CONIPHER 相同）。
  - HP 標記：`prop_tagged`（有 HP tag 的 read 比例）、`tag_concentration`（各位點的 tag 比例不同）。
  - read 錯誤：`base_error`（ref、alt 讀錯）、`mistag_rate`、`mistag_concentration`（HP 標錯，集中在少數位點）。
  - depth：`depth_dispersion`（同 CN 下 depth 也會有額外變異）。
  - CN：`prop_pos_second_cna`（同一位置第二個 CN 事件，例如先 LOH 再 gain）。
- 拿掉的：多 sample 相關參數（`n_samples` 等），因為研究只用一個 bulk sample；改名：`n_nodes`→`n_clones`、`n_positions`→`n_snv`。
- 新參數多數預設為「關閉」；預設不是關閉的有 `prop_snv_on_b`（0.5）與 `prop_tagged`（0.8）。設 `prop_snv_on_b` 0、`prop_tagged` 1、其他新參數關閉時，模型和 CONIPHER 相同（亂數不同，輸出分布一致，不是逐位元相同）。〔程式，`diplosim/DECISIONS.md`〕

**p4 候選方案頁：read 計數怎麼拆成 HP1／HP2**
- 標題：HP 計數拆分選方案 ②：沿用 CONIPHER 的 depth 與 alt，再依 allele 份數拆 ref，最後一部分 read 變成 unphased
- 三個候選，各一張卡、一張示意圖、優點／風險：① 計數後拆分、② ①＋unphased、③ 逐條 read 產生。
- 選 ② 的理由：HP1＋HP2＋HP0 等於 CONIPHER 的 depth、alt，有 CN 事件也能用。
- 限制（講稿）：沒有逐條 read，產生不了同 read 共現 → 延後。
- 圖：`diplosim/docs/figs/hp_split_compare.png`、`hp_split_option_2.png`。

### 交付 2＋3：任務 2——怎麼檢查輸出接近真實 long read

**p5 驗證方法頁（需求分兩組）**
- 標題：要驗兩件事；「資料像不像」先用真實 HCC1395 long read，「樹能否重建」要等 HG008
- 需求拆兩組（L-2）：
  - 驗資料：只用 long read、能讀出 HP1／HP2 → HCC1395 ONT ✓。
  - 驗樹：要有真值 clone 樹 → HCC1395 ✗（沒有已知 clone 樹）；HG008 single cell 樹 → 未定（資料已刪，single cell 讀長待查）。
  - TRACERx cohort 統計 → ✗（short read）。
- benchmark 第一句（L-3）：真值來源＝無 clone 樹，只比數值；讀長＝ONT long read；輸入＝ClairS somatic SNV＋HP pileup；公開真實資料（SEQC2），無生成程式。

**p6 HCC1395 不同 purity 設計頁**
- 標題：同一株細胞的 5 個 long read 樣本，tumor read 比例從 100% 降到 20%，用來看各項數值怎麼隨 purity 改變
- 圖：5 條混合比例條（t50…t10），每條寫 nominal（tumor reads 比例：100%、80%、60%、40%、20%）與換算的細胞 purity（0.97、0.70、0.48、0.29、0.14，寫明換算時用 ploidy 3.06，〔推論，公式〕）。
- 做法流程（F-9）：真實樣本 → ClairS 叫 somatic SNV → 用 HP tag 拆 read → 算數值；模擬端：同樣的 purity、coverage 餵給 diplosim → 算同樣的數值 → 比較。
- 只講設計，不放模擬結果（使用者 2026-11-01 指示）。

**p7 要檢查的數值頁（一個數值對一個旋鈕）**
- 標題：檢查 6 類 long read 數值，每一類對應 diplosim 的一個旋鈕
- 圖：每類一張小卡，畫 read 示意圖說明這個數值在量什麼（一次解釋 HP0、mistag 等詞，T-5），旁邊標對應旋鈕：
  1. HP0 比例（沒有 HP tag 的 read）→ `prop_tagged`。
  2. 位點間 tag 比例的差異 → `tag_concentration`。
  3. alt 分在兩條 HP 的 SNV → `base_error`、`mistag_rate`。
  4. minor HP depth < 0.1 的位點（LOH）→ CN 事件、`prop_pos_second_cna`。
  5. depth 變異÷平均 → `depth_dispersion`＋CN。
  6. VAF 分位 → purity、CN、clone 比例。

### 交付 4：結果（含做到哪一步）

**p8 實際產出頁**
- 標題：真實 HCC1395 的 HP 類數值幾乎不隨 purity 改變，LOH 與 VAF 類數值隨 purity 下降
- 左：diplosim 實際輸出的前 2 列（標「實際結果」），對照 p2 的欄位。
- 右：真實 HCC1395 5 個 purity 的數值（只放真實端，標「實際結果」）〔實測，`lab_report/2026-11-01_diplosim_detection_curve/*/tables/ppc_stats.tsv` 的 real 欄〕：

  | 數值 | t50 | t40 | t30 | t20 | t10 |
  |---|---:|---:|---:|---:|---:|
  | HP0 比例 | 0.138 | 0.138 | 0.139 | 0.137 | 0.134 |
  | 位點 tag 比例 SD | 0.254 | 0.251 | 0.248 | 0.244 | 0.241 |
  | alt 分在兩條 HP | 0.027 | 0.027 | 0.030 | 0.036 | 0.047 |
  | minor HP depth < 0.1 | 0.482 | 0.181 | 0.020 | 0.003 | 0.003 |
  | depth 變異÷平均 | 9.41 | 6.59 | 4.18 | 2.57 | 1.68 |
  | VAF 中位數 | 0.44 | 0.36 | 0.29 | 0.23 | 0.17 |

- 意義：HP 標記類數值是定序與 phasing 的性質，不隨 purity 變；LOH、depth、VAF 類數值隨 purity 變，正好可以測 diplosim 的 CN 與 purity 機制〔推論〕。
- 做到哪一步（L-9）：模擬端已經跑過 5 個 purity；比較結果與改動，下次報告。

### 交付 5：懂／不懂

**p9 懂／不懂**
- 標題：已確認的與還不確定的
- 已確認：diplosim 新增的 8 個參數各控制什麼〔程式〕；HP 計數加總等於 CONIPHER 的計數〔程式〕；真實 HCC1395 哪些數值隨 purity 改變〔實測〕。
- 還不確定：HCC1395 只能驗資料、不能驗樹；HG008 能不能補上樹的驗證；新參數的預設值目前只是暫定或從 HCC1395 看出來的，不能當通用預設。
- 使用者自己的懂／不懂：**待使用者補**。

## 保留在計畫，不上投影片

- purity holdout 的模擬比較與 6 步改動（`lab_report/2026-11-01_diplosim_purity_summary/`），下次報告。
- φ 從 normal 量測、ClairS 規則與偵測曲線、配對 normal。

## v1 審查意見處理

- 主結論太滿（兩位）：v2 不講模擬結果，不再下「差距來自量測端」的結論。
- purity 寫法混用（兩位）：p6 一律寫 nominal 與換算值，並寫 ploidy 來源。
- 14／13 項不一（兩位）：v2 不放通過數。
- 黑話（兩位）：p7 用 read 示意圖一次解釋。
- 需求表不完整、L-3 寫錯（邏輯）：p5 已改。
- PPC 用詞（教授）：v2 不用「PPC」，改說「和真實資料比數值」。
- 負對照（教授）：v2 不談結果，列為之後要做（BRIEF）。

## 待確認

1. p8 放「真實 HCC1395 的數值」是否符合「先拿 hcc1395 各不同 purity 來觀察各項數值」的意思？或 p8 只放 diplosim 的實際輸出？
2. p4（HP 計數拆分的候選方案）要保留嗎？它是交付 3「方案與選擇理由」的例子，但可能讓第一段變長。
