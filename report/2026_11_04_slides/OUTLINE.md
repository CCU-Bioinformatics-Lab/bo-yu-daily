# 2026-11-04 報告大綱（v4，2026-11-01，使用者確認）

v2 → v3：依第 2 輪審查（`REVIEW_v2.md`）修正事實與標題。主軸不變（`BRIEF.md` B-1）：不講 purity holdout 的模擬結果。
v3 → v4（使用者 2026-11-01）：HG008 全部不提（還沒考慮）；p8 畫成 6 條小折線；其餘照 v3。P-2 通過。

## 主問題（C-2）

**diplosim 比 CONIPHER 多輸出哪些 long read 資訊？要怎麼檢查這些資訊接近真實的 long read bulk？**

- 使用者原話與會議對照：見 `BRIEF.md` B-1；會議 2026-10-28 決議 1 → 第一段，待辦「探討驗證方法」→ 第二段。
- 結構照 `CLAUDE.md`「交付」1–5；第 6 項只寫在 `BRIEF.md`。

## 頁序

### 交付 1：接回上次會議

**p1 大綱頁（W-4＝L-1 開場）**
- 標題：diplosim 比 CONIPHER 多輸出哪些 long read 資訊？怎麼檢查它接近真實資料？
- 研究目的：模擬帶 HP1／HP2 的 long read bulk 資料，用來測試 PhyClone 的 HP 擴充。
- 上次（10-28）的方向與現況：
  1. 說清楚改了哪裡 → **可行**：本週第一段。
  2. 列 2–3 個驗證方法 → **先做一個**：和真實 HCC1395 long read 比數值；TRACERx 統計 **排除**（short read）。
  3. 用流程圖呈現 → 每段都有圖。
  4. 同一條 read 上的 SNV 共現 → **延後**（不是排除）。
- 本週兩段，各一句：
  - 第一段：把 CONIPHER 與 diplosim 想成兩台機器，比較輸入的參數與輸出的資訊。
  - 第二段：用 HCC1395 不同 purity 的真實 long read，定出 diplosim 要對上的數值。

### 交付 2＋3：任務 1——兩台機器

**p2 兩台機器頁（比喻＋資訊量）**
- 標題：兩台機器吃相同的腫瘤設定，diplosim 另外把每個 SNV 的 read 依 HP1／HP2／unphased 拆開，並記下 SNV 在哪條 allele
- 圖：左右兩台機器（CONIPHER、diplosim），上方同一組輸入卡（clone 數、SNV 數、purity、coverage、CN gain／loss、WGD），下方各吐出「每個 SNV 一列」的輸出表，用同一個 SNV 當例子（E-1，用實際輸出的一列，標「實際結果」）：
  - 兩台都有：ref read 數、alt read 數、每條 allele 的 copy number（CN_A、CN_B）、clone、CCF。〔程式，`conversion.py:31`〕
  - 只有 diplosim：ref／alt 再拆成 HP1、HP2、unphased（HP0）各自的 ref／alt（6 個計數，加總等於 diplosim 自己的 ref、alt）；真值欄「SNV 在哪條 allele」。
- 新增的資訊是「read 層級的 phase」，不是欄位數（CONIPHER 本來就有 allele 的 copy number）。
- 和真實資料的差別（頁面一個小標籤，細節放講稿）：真實 long read 的 HP1／HP2 標號只在同一個 phase block 內一致；diplosim 全基因組 HP1＝allele A，沒有 phase block。〔程式，`diplosim/src/hp.rs`〕
- 頁底一列：多出的 HP 計數之後可讓 PhyClone 用什麼（例如同一 clone 的 SNV 落在同一條 HP）〔推論，擴充尚未做〕。

**p3 新增參數頁（機器的旋鈕）**
- 標題：diplosim 沿用 CONIPHER 的參數，另外新增 8 個旋鈕，控制 SNV 落在哪條 allele、HP 標記、read 錯誤、depth 與 CN
- 圖：旋鈕盤，每組旋鈕旁畫它影響的輸出（F-9、C-18：只寫控制什麼與預設值，不寫範圍，不排先後）。頁面用中文名稱，程式參數名放小字：
  - SNV 落在 allele B 的機率（`prop_snv_on_b`，預設 0.5；0 時和 CONIPHER 相同）。
  - 有 HP 標記的 read 比例（`prop_tagged`，預設 0.8）、各位點標記比例的差異（`tag_concentration`，預設關閉）。
  - 鹼基讀錯（`base_error`）、HP 標錯（`mistag_rate`）、HP 標錯集中在少數位點（`mistag_concentration`），預設都關閉。
  - depth 的額外變異（`depth_dispersion`，預設關閉＝CONIPHER 的 Poisson）。
  - 同一位置的第二個 CN 事件，例如先 LOH 再 gain（`prop_pos_second_cna`，預設 0＝CONIPHER）。
- 拿掉：多 sample 相關參數（研究只用一個 bulk sample）。改名：`n_nodes`→clone 數 `n_clones`、`n_positions`→SNV 數 `n_snv`。
- 講稿：設 `prop_snv_on_b` 0、`prop_tagged` 1、其他新旋鈕關閉時，模型和 CONIPHER 相同；這是依程式推得，輸出分布的一致性還沒有實測〔程式，未實測〕。

**p4 候選方案頁：read 計數怎麼拆成 HP1／HP2**
- 標題：HP 計數拆分選方案 ②：沿用 CONIPHER 的 depth 與 alt，再依 allele 份數拆 ref，最後一部分 read 變成 unphased
- 三個候選，各一張卡、一張示意圖、優點／風險：① 計數後拆分、② ①＋unphased、③ 逐條 read 產生。
- 選 ② 的理由：HP1＋HP2＋HP0 等於 depth、alt；有 CN 事件也能用。
- 講稿限制：沒有逐條 read，產生不了同 read 共現 → 延後。
- 圖：`diplosim/docs/figs/hp_split_compare.png`、`hp_split_option_2.png`。

### 交付 2＋3：任務 2——怎麼檢查輸出接近真實 long read

**p5 驗證方法頁（需求分兩組）**
- 標題：要驗兩件事；「資料像不像」先用真實 HCC1395 long read，「樹能否重建」要另外的資料
- 需求拆兩組（L-2）：
  - 驗資料：只用 long read、能讀出 HP1／HP2 → HCC1395 ONT ✓。
  - 驗樹：要有真值 clone 樹 → HCC1395 ✗（沒有已知 clone 樹）；驗樹用什麼資料，還沒決定。
  - TRACERx cohort 統計 → ✗（short read）。
- 講稿：「樹能否重建」也可以用 diplosim 自己的真值樹測（模擬內部），那是測 PhyClone，不是證明模擬合理（10-28 議題三）。
- benchmark 第一句（L-3）：真值來源＝無 clone 樹，只比數值；讀長＝ONT long read；輸入＝ClairS somatic SNV＋HP pileup；公開真實資料（SEQC2），無生成程式。

**p6 HCC1395 不同 purity 設計頁**
- 標題：HCC1395 tumor 與 normal 的 long read 依 5 種比例混合，tumor read 從 100% 降到 20%，用來看各項數值怎麼隨 purity 改變
- 圖：5 條混合比例條（t50…t10），每條寫：
  - nominal：tumor reads 比例 100%、80%、60%、40%、20%（tumor 來自 HCC1395，normal 來自配對的 HCC1395BL）。
  - 換算的 tumor 細胞比例：0.97、0.70、0.48、0.29、0.14。換算用兩個 ASCAT 值：t50 本身的 purity 0.97、ploidy 3.06〔推論，公式〕。
- 講稿：ploidy 換用 2.73 時換算值約高 10%；更精細的換算（normal 帶少量 tumor DNA）下次再講。
- 做法流程（F-9）：真實樣本 → ClairS 叫 somatic SNV → 用 HP tag 拆 read → 算數值；模擬端：同樣的 purity、coverage 餵給 diplosim → 算同樣的數值 → 比較。
- 只講設計，不放模擬結果。

**p7 要檢查的數值頁**
- 標題：從 13 項數值中挑 6 類代表，每類寫出主要對應的旋鈕，以及也會影響它的因素
- 圖：每類一張小卡，畫 read 示意圖說明在量什麼（一次解釋 HP0、HP 標錯等詞，T-5）：
  1. unphased read 比例 → 主要：`prop_tagged`。
  2. 位點間 HP 標記比例的差異 → 主要：`tag_concentration`。
  3. alt 分在兩條 HP 的 SNV → 主要：鹼基讀錯、HP 標錯；也受 purity 影響。
  4. minor HP depth < 0.1 的位點（LOH）→ 主要：loss 比例、loss 事件種類、第二個 CN 事件；也受 purity 影響（normal 細胞補上 minor HP）。
  5. depth 變異÷平均 → 主要：depth 額外變異；也受 CN 與 purity 影響。
  6. VAF 分位 → purity、CN、clone 比例；真實端還經過 ClairS 篩選。
- 講稿：為什麼挑這 6 類——各代表一組旋鈕；其餘 7 項是同一類的不同切法。

### 交付 4：結果（含做到哪一步）

**p8 真實目標值頁**
- 標題：這些是 diplosim 要對上的目標值：unphased 比例幾乎不隨 purity 變，alt 分在兩條 HP、LOH、depth、VAF 都隨 purity 改變
- 圖：真實 HCC1395 5 個 purity 的數值（只放真實端，標「實際結果」）〔實測，`lab_report/2026-11-01_diplosim_detection_curve/*/tables/ppc_stats.tsv` real 欄〕，畫成 6 張小折線圖（x＝換算 purity，y＝數值，每張一個數值；使用者 2026-11-01 指定）。資料：

  | 數值 | t50 | t40 | t30 | t20 | t10 |
  |---|---:|---:|---:|---:|---:|
  | unphased read 比例 | 0.138 | 0.138 | 0.139 | 0.137 | 0.134 |
  | 位點 HP 標記比例 SD | 0.254 | 0.251 | 0.248 | 0.244 | 0.241 |
  | alt 分在兩條 HP | 0.027 | 0.027 | 0.030 | 0.036 | 0.047 |
  | minor HP depth < 0.1 | 0.482 | 0.181 | 0.020 | 0.003 | 0.003 |
  | depth 變異÷平均 | 9.41 | 6.59 | 4.18 | 2.57 | 1.68 |
  | VAF 中位數 | 0.44 | 0.36 | 0.29 | 0.23 | 0.17 |

- 講稿：
  - minor HP < 0.1 在 purity 約 0.7 以下幾乎歸零，是因為 normal 細胞補上 minor HP，超過固定門檻 0.1〔推論〕；它在高 purity 才是 LOH 的好指標。
  - 每個 purity 叫出的 SNV 集合不同（ClairS 在低 purity 叫出較少），趨勢有一部分來自 caller 篩選〔推論〕。
- 做到哪一步（L-9）：模擬端已經跑過 5 個 purity；比較結果下次報告。

### 交付 5：懂／不懂

**p9 懂／不懂**
- 標題：8 個旋鈕與它們影響的數值已確認；HCC1395 只能驗資料，驗樹與 phase block 還沒處理
- 已確認：8 個新旋鈕各控制什麼〔程式〕；HP 計數加總等於 diplosim 的 ref、alt〔程式〕；真實 HCC1395 哪些數值隨 purity 改變〔實測〕。
- 還不確定：驗樹要用什麼資料；diplosim 沒有 phase block，和真實資料怎麼對齊；新旋鈕的預設值只是暫定或從 HCC1395 看出來的。
- 使用者自己的懂／不懂：**待使用者補**。

## 保留在計畫，不上投影片

- purity holdout 的模擬比較與 6 步改動（`lab_report/2026-11-01_diplosim_purity_summary/`），下次報告。
- φ 從 normal 量測、ClairS 規則與偵測曲線、配對 normal、purity 換算加入 normal 的 tumor 比例。
- 沿用 CONIPHER 的規則（LOH 丟沒突變的 allele、gain 複製帶突變那份）對 multiplicity 的偏差（教授追問）。

## 使用者確認（2026-11-01）

- HG008 先不提（還沒考慮）。
- p8 畫成 6 條小折線。
- 其餘內容與順序照 v3。
