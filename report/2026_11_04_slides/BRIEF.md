# 2026-11-04 簡報 BRIEF

## B-1 主軸（使用者指定，2026-11-01）

- 原話：「先不要說明 diplosim 後面 purity 的結果，大致說到 conipher 和 diplosim 相比新增甚麼參數，並同時比喻為兩台機器輸出 bulk 定序模擬資料，並比較資訊量多寡，測試部分為了逼近真實癌腫的真實 bulk 定序資料，先拿 hcc1395 各不同 purity 來觀察各項數值，檢查是否能接近模擬出真實 long read 的資訊」。
- 分兩段：
  1. CONIPHER 與 diplosim 比喻成兩台輸出 bulk 定序模擬資料的機器：新增哪些參數、輸出的資訊量差多少。
  2. 測試：用 HCC1395 不同 purity 的真實 long read 觀察各項數值，作為檢查 diplosim 是否接近真實 long read 的依據。
- 不講：purity holdout 的模擬結果與之後的 6 步改動。
- 報告結構照 `CLAUDE.md`「交付」1–5（使用者 2026-11-01：「先完全按照 claude.md 裡面的指示」）。

## 線上版

https://claude.ai/artifact/2NCt1kGAEfbCKGcVxeXb8C（2026-11-01 建立，Slides artifact type）

## 版面（沿用 2026-10-28 簡報）

- 背景 `#f7f6f2`；主文字 `#1f2a37`；次要文字 `#6b7480`；強調藍 `#2f6db5`；強調橘 `#c96a1b`；卡片白 `#ffffff`，邊框 `#e3e1da`。
- HP 固定配色（F-4）：HP1 `#2C5F9E`、HP1 帶 SNV `#8FB3E0`、HP2 `#D9772B`、HP2 帶 SNV `#F2B880`、somatic SNV `#D23A2E`、unphased（HP0）`#9AA3AE`。
- section：`display:flex; flex-direction:column; gap:32px; padding:128px 128px 160px; background:#f7f6f2`。
- 段落標籤：`<p>` Noto Sans TC 24px 700 `letter-spacing:2px` `#2f6db5`，例如「1 · 兩台機器」。
- 標題：`<h2>` Noto Serif TC 64px 700 `line-height:1.15` `#1f2a37`（W-2：一句結論）。
- 內文：Noto Sans TC，最小 24px。程式參數名用 JetBrains Mono 24px 次要色。
- 頁尾（P-7）：`<div style="position:absolute; right:128px; bottom:64px; left:128px; display:flex; flex-direction:row; justify-content:space-between">`，左 `2026-11-04 diplosim：兩台機器與真實 long read`，右 `n / 9`，都是 Noto Sans TC 24px `#6b7480`。
- 圖用 inline `<svg aria-label>`（≤ 52 KB）或 div 卡片；不用外部圖片。

## 貫穿例子（E-1，實際結果）

diplosim 預設參數（`--n-clones 3 --n-snv 450 --seed 1 --coverage 53 --min/max-tumour-purity 0.9`）輸出的一列（`report/2026_11_04_slides/data/diplosim_default_seed1/diplosim.tsv`）：
chr7:21,792,655 G>A；ref 36、alt 21、depth 57；CN_A 1、CN_B 1；SNV 在 allele A（HP1）；HP1 ref 0／alt 19、HP2 ref 27／alt 0、HP0 ref 9／alt 2。
CONIPHER 格式只會有 ref 36、alt 21（同一列的共用欄位）。頁面寫成「SNV1」（E-4），座標只放 BRIEF。

## 來源代號表

| 代號 | 來源 |
|---|---|
| R1 | `diplosim/DECISIONS.md`（參數決策與預設值） |
| R2 | `diplosim/src/params.rs`（參數列表）、`diplosim/src/hp.rs`（HP 拆分與錯誤） |
| R3 | CONIPHER 模擬器 `src/conversion.py:31`（24 欄輸出）、`src/simulate.py:186-205`（參數） |
| R4 | `lab_report/2026-10-31_diplosim_purity_holdout_plan/`（purity 換算：ASCAT purity 0.97、ploidy 3.06） |
| R5 | `lab_report/2026-11-01_diplosim_detection_curve/*/tables/ppc_stats.tsv` real 欄（真實 HCC1395 數值）。p14 r-targets 自 2026-11-03 起改用 `lab_report/2026-11-03_diplosim_mask_ig_loci/*/tables/ppc_stats.tsv`（真實端排除 IGH、IGK、IGL，模擬端不變） |
| R6 | `lab_report/2026-10-30_diplosim_ppc_hcc1395/`（2026-11-04 刪除，未進 git，無法取回）；真實資料表的副本在 `lab_report/2026-10-31_diplosim_ppc_hcc1395_lost045/tables/`（真實資料處理：ClairS PASS ∩ HC、longphase haplotag） |

## 規則檢查

### 腳本（2026-11-01）

`python3 tools/check_slides.py report/2026_11_04_slides/ --titles`：9 頁，0 個錯誤。

### W-3 標題串讀

1. diplosim 比 CONIPHER 多輸出哪些 long read 資訊？怎麼檢查它接近真實資料？
2. 兩台機器吃相同設定，diplosim 多把 read 拆成 HP1／HP2／unphased，並記下 SNV 在哪條 allele
3. diplosim 沿用 CONIPHER 參數，新增 8 個旋鈕：SNV 在哪條 allele、HP 標記、read 錯誤、depth、CN
4. HP 計數拆分選方案 ②：depth、alt 沿用 CONIPHER，ref 依 allele 份數拆，再讓部分 read 變 unphased
5. 要驗兩件事；「資料像不像」先用真實 HCC1395 long read，「樹能否重建」要另外的資料
6. HCC1395 tumor 與 normal 的 long read 依 5 種比例混合，看各項數值怎麼隨 purity 改變
7. 把 13 項數值分成 6 類，每類寫出主要對應的旋鈕，以及也會影響它的因素
8. diplosim 的目標值：HP 標記的 2 個數值幾乎不隨 purity 變，其餘 4 個隨 purity 改變
9. 8 個旋鈕各控制什麼已確認；HCC1395 只能驗資料，驗樹與 phase block 還沒處理

### 人工檢查表（2026-11-01）

| 代號 | 結果 | 說明 |
|---|---|---|
| W-3 | ✓ | 標題串讀見上；P-6 檢查後改了 p7、p8、p9 標題 |
| P-1、P-2 | ✓ | 兩輪兩方審查（REVIEW_v1、REVIEW_v2）；使用者 2026-11-01 確認 v4 |
| P-11 | 不適用 | 新簡報，不是重新設計 |
| C-1、C-2 | ✓ | 段落與使用者 B-1 主軸一致；沒有模擬比較結果、沒有 HG008 |
| C-7 | ✓ | p6 分開寫 nominal tumor read 比例與換算 purity；p2 寫「purity 設定 0.9」；推論標〔推論〕 |
| L（→ CLAUDE.md） | ✓ | 頁序照交付 1–5；交付 6 寫在本檔 |
| E-1、E-3 | ✓ | p2、p4 用同一個 SNV1（實際結果）；示意值標「示意」 |
| F-4 | ✓ | HP 色照固定表；P-6 後統一 ✗ 色（#B3362B），p5 樹節點改成非固定表的單一深藍 |
| T-5、S-4 | ✓ | P-6 後 p2 講稿補 unphased、phase block，p3 講稿補 LOH；CCF、trunk 只在圖上小字出現，未另解釋 |
| T-6、T-7 | ✓ | 但書放講稿 |
| S-7 | ✓ | p4→p5、p7→p8、p8→p9 有橋接句 |
| 版面 | 未檢查 | 這台機器沒有瀏覽器，無法看渲染縮圖（P-5）；p2、p4、p8 標題可能三行，需使用者在線上版確認 |

P-6 全冊邏輯檢查（subagent）：修正 p7 標題（分成 6 類，不是挑 6 類）、p8 標題與講稿（補位點標記差異、橋接句、刪 t50 → t10）、p9 標題（不說數值對應已確認）、p2 purity 標成設定值、配色統一。審查者說 p8 minor HP 圖名少了「< 0.1 的位點比例」，核對後圖名已有，不改。

## 交付 6 自我檢查（2026-10-21 summary §2.2）

- [x] 每一頁的第一句回答「這頁對研究目標有什麼用」：講稿第一句是該頁結論。
- [x] 「可以」「沒有」「已驗證」附證據來源：見來源代號表與 sketches/。
- [x] benchmark 寫出真值來源、讀長、輸入、生成程式：p5。
- [x] 「沒找到」附搜尋範圍：本簡報沒有「沒找到」類結論。
- [ ] AI 結論標明自己核對過哪部分：待使用者補。

## 之後要做（不上投影片）

- 負對照：證明「和真實資料比數值」抓得出錯的模擬器（v1 審查，教授）。


## 圖文比例量測與改版提案（2026-11-01，F-2）

量法：去掉講稿、標題、頁尾後，數圖外的字數；圖面積只算 inline SVG 的寬×高（用 div 畫的色條沒算進去，所以 p2、p4、p7 的圖面積略被低估）。

| 頁 | id | 圖外字數 | 圖佔內容區 | 判斷 |
|---|---|---:|---:|---|
| 1 | outline | 282 | 0% | 大綱頁例外 |
| 2 | t1-machines | 387 | 17% | 文字多 |
| 3 | t1-knobs | 484 | 8% | 最需要改 |
| 4 | t1-hpsplit | 321 | 14% | 文字多 |
| 5 | t2-validation | 271 | 2% | 最需要改 |
| 6 | t2-purity | 408 | 5% | 最需要改 |
| 7 | t2-stats | 411 | 16% | 文字多 |
| 8 | r-targets | 199 | 34% | 接近標準 |
| 9 | u-known | 198 | 4% | 需要改 |

### 提案（每頁一張主圖，文字改成圖上標籤）

p3 旋鈕盤：機器面板上 5 個旋鈕，每個旋鈕拉一條箭頭，指到 p2 那一列輸出中它改動的欄位。
```
        ┌──── diplosim 面板 ────┐
        │ (◎)   (◎◎)  (◎◎◎)  (◎)  (◎) │   ← 5 組旋鈕，旋鈕下只寫中文名＋預設值
        └──┬────┬─────┬─────┬────┬──┘
           ▼    ▼     ▼     ▼    ▼
輸出一列：[allele][HP0 計數][另一條 HP 的 alt][depth][CN_A,CN_B]
```

p5 驗證需求：改成打勾矩陣。欄＝兩件要驗的事（read 圖示、樹圖示），列＝候選資料，格子只放 ✓／✗ 大圖示。
```
              [read 圖示] 驗資料    [樹圖示] 驗樹
HCC1395 ONT        ✓                  ✗
TRACERx 統計       ✗（short read）     —
diplosim 真值樹    —                  ✓（只測 PhyClone）
真實樹資料         —                  ？（還沒決定）
```

p6 purity：5 條 read 比例條放大成主圖，每條右側用箭頭接到一條 0–1 數線上的點（細胞 purity）；換算卡改成細胞圖示（tumor 細胞 3 條 DNA、normal 細胞 2 條）。下方流程改成 4 個圖示＋箭頭。
```
read 比例                         細胞 purity
[■■■■■■■■■■]  ──────────────►  ●0.97
[■■■■■■■■□□]  ──────────────►  ●0.70
...                               0 ──────────── 1
[tumor 細胞 ≡≡≡] [normal 細胞 ==]
```

p2、p4、p7：保留結構，只把文字條列改成圖上的 ✓／✗、色條與箭頭；p2 左欄三行「無…」改成一塊斜線底。
p9：每一項一個小圖示（旋鈕、read、樹＋問號、phase block 色段）＋一個短語。

### 改版後量測（2026-11-01，p1、p3、p5、p6 依 F-2 圖示化）

| 頁 | 圖外字數 | 圖內字數（約） | 圖佔內容區 |
|---|---:|---:|---:|
| 1 outline | 4 | 213 | 65% |
| 3 t1-knobs | 6 | 309 | 66% |
| 5 t2-validation | 76 | — | 56% |
| 6 t2-purity | 10 | — | 66% |

- 舊版備份：`old_v1_slides/`。
- p3 標題改成「diplosim 沿用 CONIPHER 參數，新增 8 個旋鈕，分 5 組各改輸出的一部分」（原句在截圖中排成 3 行，壓縮主圖）。
- p3 刪掉：8 個參數名小字、每組「影響：…」文字（改用箭頭）、舊參數名、設回 CONIPHER 的具體值、講稿的 LOH 解說（p7 有解釋 LOH）。
- p1、p3 的文字有一部分搬進圖內；總字數比舊版少約 25–35%。
- p2、p4、p7、p9 還沒改版。

## 2026-11-03 新增 p3「CONIPHER 參數」（c-params）

- 使用者要求：在原第 3 頁前加 CONIPHER 參數頁，只放影響 ref、alt、VAF、copy number 的參數。
- 頁面參數與例子值取自貫穿例子的 run（`data/diplosim_default_seed1/diplosim_info.tsv`，新旋鈕關閉時等於 CONIPHER 參數）：clone 數 3、trunk SNV 比例 0.5、purity 0.9、gain／loss 比例 0.5／0.3、WGD 無、coverage 53。
- 參數 → 欄位對照（〔程式〕CONIPHER 模擬器）：
  - clone 數、trunk SNV 比例 → SNV 在哪個 clone、CCF：`src/simulate.py:162`（simulate_topology）、`src/evolution.py:48`（snv_assignment）。
  - gain／loss 比例、WGD → CN_A、CN_B：`src/evolution.py:184-233`（cna_assignment）、`:75-88`（wgd_assignment）。
  - purity → 期望 VAF：`src/sequencing.py:54`（purity 隨機）、`:66-92`（VAF＝帶 SNV 的份數 ÷ 總份數，normal 佔 1−purity）。
  - coverage → depth：`src/sequencing.py:95-99`（Poisson，平均 ∝ coverage × 該位點總 copy number）。
  - 期望 VAF → alt：`src/sequencing.py:102-104`（Binomial(depth, VAF)）；ref＝depth − alt：`src/conversion.py:13`。
- SNV1 實際結果：CN 1、1，CCF 1.0，TRUE_VAF 0.45（0.9 × 1 ÷ 2），depth 57，alt 21，ref 36，VAF_OBS 0.37。
- 插頁後頁碼：t1-knobs 起各頁 +1；同時修正 r-targets、u-known 原本寫成「/ 12」的頁尾；大綱頁段落頁碼改為 p3–p9、p10–p11、p12–p13。
- 腳本檢查（2026-11-03）：13 頁，0 個錯誤。未渲染縮圖確認排版。

## 2026-11-03 新增 p9「depth 旋鈕」（k-depth）

- 使用者留言：t1-knobs 的 depth 旋鈕沒有展開頁，要求照 k-allele 版型補一頁。排在 k-cn 之後（面板由右到左展開的最後一組）。
- 編輯器端先放了一版，左下用「全部 SNV 的 depth 變異÷平均」（9.41…1.68）。這個值大部分來自 CN 之間的差異（總變異 7.0 + 2.4，見 R7），不能支持這個旋鈕，所以改成只看 CN 相同的位點。
- 左下〔實測〕：`lab_report/2026-10-31_diplosim_ppc_hcc1395_depthdisp0.03/README.md` §2（ASCAT CN 分組；CN 2＋0 1.83、CN 5＋2 3.06，6 組 1.83–3.06）。purity 是 ASCAT 估計 0.97。
- 旋鈕〔程式〕：`diplosim/src/sequencing.rs:141-160`（每位點 Poisson 平均乘 Gamma(1/φ, φ)）；`diplosim/DECISIONS.md` 2026-10-31 列。預設不設＝Poisson。
- 右邊 SNV1〔實測〕：貫穿例子參數加 `--depth-dispersion 0.03`（`data/diplosim_seed1_depthdisp003/`）。tree、CN、VAF、allele 與預設 run 相同（第 3 個 SNV）；座標因亂數順序不同而不同，頁面不顯示。depth 57→50，ref 27、alt 23，HP1 4／17、HP2 18／0、unphased 5／6。
- 中間「本例 CN 1＋1 的 90 個位點變異÷平均 0.85 → 2.54」〔實測〕：同兩個 run 中 CN_A＝CN_B＝1 的位點。
- 插頁後頁碼：k-depth 9；t1-machines 起 +1，總頁數 14；大綱卡「p8–9 CN 事件、depth」。腳本檢查：14 頁，0 個錯誤。

## 2026-11-03 新增 p5「前提說明」（k-premise）

- 使用者要求：在 t1-knobs 與 k-allele 之間加一頁前提，說明接下來每個新參數都是先觀察到 HCC1395 真實資料的現象，再加參數來模擬。
- 版面：上排三步（看 HCC1395 現象 → 加新參數 → diplosim 輸出也出現），下排 5 列「現象 → 新參數」對應 p6–p10。
- 5 個現象的數字取自各頁標題（p6 49.2%、p7 13.8%、p8 約一成、p9 20.7%、p10 1.8–3.1 倍），沒有新數字。
- 插頁後總頁數 15；大綱卡改為 p3–5、p6、p7、p8、p9–10、p11；段落 p3–p11、p12–p13、p14–p15。腳本檢查：15 頁，0 個錯誤。
- 注意：本地 `project/slides/` 中 k-allele、k-tag、k-error、k-cn、t1-knobs、t2-stats、r-targets、u-known 在本次之前就和線上版不同（使用者在編輯器改過），只同步了頁碼。以線上版為準。

## 2026-11-03 修改 p14「真實 HCC1395 對 diplosim」（r-targets）：真實端排除抗體基因區

- 原因：LOH 比例在 purity 0.48、0.29、0.14 落在區間外。t10 的 22 個低 minor HP 位點中，19 個在 IGL 基因座；normal（B 淋巴母細胞株）在這段的 depth 只有兩側的一半〔實測〕。推論是 V(D)J 刪除，所以 normal 補不回 minor HP〔推論〕。詳見 `lab_report/2026-11-03_diplosim_mask_ig_loci/`。
- 使用者 2026-11-03 選方案 1：真實端排除 IGH、IGK、IGL（81–114 個 SNV），模擬端沿用原本的 sim 統計量。
- 頁面改動：標題改成「6 個數值中 5 個在 5 個 purity 都落在模擬區間內，depth 高低程度只在 purity 0.97 略偏」；LOH 小圖變成 5/5；加一行「真實端排除抗體基因區（normal 細胞在此少一條 HP）：81–114 個 SNV」；講稿改寫 LOH 那段，並標出推論（S-8）。
- `gen_p11.py` 同時對齊線上版編輯器裡的改動：骰子那一行、刪掉橘色「SNV 偏少」那行、講稿開頭的骰子句。
- 規則檢查（P-8 局部修改）：`check_slides.py --titles` 15 頁 0 錯誤；W-3 標題串讀 p13 → p14 → p15 仍接得上；E-1 不受影響；C-7：刪除原因標為推論；S-5：講稿最後一句的「lab_report 2026-11-01_diplosim_detection_curve」是線上版原有的路徑，腳本沒抓到，未改動。

