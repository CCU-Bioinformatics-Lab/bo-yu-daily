# CONIPHER 模擬步驟

日期：2026-10-29。目的：diplosim 要照 CONIPHER 的步驟一步一步重寫。動手前，先把 CONIPHER 每一步做什麼寫清楚。

來源：
- CONIPHER：`research/simulation_pipeline_research/upstream/TRACERx_simulation_tool/src/`，commit `facd2d7`。下文寫 `topology.py:64` 這類行號，都指這個目錄。

標記：〔程式〕讀程式碼得到；〔推論〕分析推論，沒有執行驗證。

## 1. 結論

- **CONIPHER 已經分 allele A／B。** 每個 position 的狀態是 `[cnA, cnB, 帶突變的 copy 數]`（`evolution.py:115`）。〔程式〕
- **但 CONIPHER 的 SNV 一律放在 A。** `snv` 事件只在 cnA ≠ 0 時加一個突變 copy（`evolution.py:167,172`）。`gain_A` 和 `loss_A` 一定作用在帶突變的那份 copy（`evolution.py:166,169,176`）。所以 B 永遠不帶 SNV，A 等於「帶突變的那條 haplotype」。〔程式〕
- **CONIPHER 沒有 segment。** 每個 SNV position 是一個獨立的 locus，自己抽 CN 事件、自己決定事件順序（`evolution.py:91-105`）。〔程式〕
- **CONIPHER 沒有 read。** 它直接用 Poisson 抽 depth、Binomial 抽 alt 數（`sequencing.py:95-104`）。〔程式〕

## 2. 流程圖

```text
CONIPHER（tx_simulation）
─────────────────────────
S1 參數（多 sample）
S2 建樹：隨機二元樹 → 剪葉
S3 SNV 分到各邊（每個 position 獨立）
S4 CNA：每個 position 抽事件
S5 WGD：每個 position 一個 wgd 事件
S6 事件順序：每個 position 隨機洗牌
S7 混合：每 sample 抽 clone、Dirichlet(1)
S8 期望 VAF
S9 Poisson depth + Binomial alt
S10 假 cluster 雜訊
S11 輸出 CONIPHER 格式
```

## 3. 逐步對照（輸入 → 步驟 → 輸出 → 假設）

### S1 參數

| | 內容 |
|---|---|
| 輸入 | 使用者參數：`n_nodes`、`n_positions`、`n_samples`、每個 sample 的 clone 數範圍、`prop_truncal_snvs`、`prop_pos_gained`／`lost`、truncal 比例、`clonal_wgd`／`subclonal_wgd`、`prop_mutloss_positions`、`coverage`、purity 範圍、`fract_noise`（`simulate.py:13-46`） |
| 步驟 | `tx_simulation` 收參數，交給 `make_a_simulation`（`simulate.py:64-68`） |
| 輸出 | 參數表 `_info.tsv`（`simulate.py:82-87`） |
| 假設 | 多 sample；參數由使用者給，沒有預設的 cohort 值 |

**diplosim 已決定（2026-10-29）：** 固定一個 bulk sample。理由：病人定序成本高，不能隔時間重複定序，也不能分別定序多個區域。〔使用者〕見 `../DECISIONS.md`。

**連帶影響，待決：** 只有一個 sample 時，CONIPHER 的 `all_leaf_observed = True` 會把所有葉子都放進這個 sample，`max_clones_per_sample` 就失效（`sequencing.py:20-34`）。`all_leaf_observed = False` 則可能產生沒有任何資料的 clone。這兩個參數怎麼處理，還沒決定。〔程式〕〔推論〕

### S2 建樹

| | 內容 |
|---|---|
| 輸入 | `n_nodes` |
| 步驟 | 1. 葉子 1..n 遞迴隨機二分，建出二元樹（`topology.py:9-43`）。2. 加一個 root（diploid normal），接到 trunk `initial_cc`（`topology.py:24-26`）。3. 隨機刪葉子，直到剩 `n_nodes + 1` 個節點（`topology.py:46-61`）。 |
| 輸出 | nodes、edges、root、`initial_cc` |
| 假設 | 樹形是二元樹剪葉後的結果，沒有控制 linear 或 branched 的比例 |

### S3 SNV 放到邊上

| | 內容 |
|---|---|
| 輸入 | edges、`n_positions`、`prop_truncal_snvs` |
| 步驟 | 按比例抽出 truncal SNV，放在 root → trunk 這條邊。其餘 SNV 切成連續區段，分給其他邊，每條邊至少 1 個（`evolution.py:35-61`）。 |
| 輸出 | 每條邊的 SNV position 清單 |
| 假設 | 每個 position 是獨立 locus；SNV 一律在 allele A（見 S6） |

### S4 CNA

| | 內容 |
|---|---|
| 輸入 | positions、`prop_pos_gained`／`lost`、truncal 比例、`prop_mutloss_positions`、`constant_multiplicity` |
| 步驟 | 1. 算各類事件數：truncal／subclonal × gain／loss（`evolution.py:213-246`）。2. gain 類：`gain_A`、`gain_B`、`gain_both`；loss 類：`loss_B`、`cnloh_B`（`evolution.py:191-194`）。3. mutation loss 只用 `loss_A`、`cnloh_A`，放在 SNV 所在邊的下游 subclone（`evolution.py:249-291`）。4. `constant_multiplicity` 為真時，subclonal CNA 不放在 SNV 所在邊的下游，帶突變的 clone 裡 multiplicity 不變（`evolution.py:350-355`）。 |
| 輸出 | 每個節點、每個 position 的 CN 事件 |
| 假設 | CN 事件以 position 為單位；mutation loss 的比例直接設定 |

### S5 WGD

| | 內容 |
|---|---|
| 輸入 | `clonal_wgd`、`subclonal_wgd`、`n_subclonal_wgd` |
| 步驟 | clonal WGD：trunk 的每個 position 加一個 `wgd` 事件。subclonal WGD：隨機挑 subclone 做同樣的事（`evolution.py:75-88`）。 |
| 輸出 | wgd 事件，和 S4 的事件併在一起 |
| 假設 | wgd 和其他事件一起洗牌（S6），所以每個 position 的 WGD 時間點不同〔程式〕 |

**補充（2026-10-29，待決，不是最終決定）**

- **CONIPHER 沒有 WGD 時間。** 有 clonal WGD 時，truncal SNV 的 multiplicity 2 與 1 各約一半（3 個 seed：0.500、0.490、0.477）。真值只記錄 WGD 有或沒有。〔實測〕`lab_report/2026-10-29_conipher_wgd_timing/`（2026-11-04 刪除，未進 git，無法取回）
- **改成單一時間點的 WGD 時，要考慮三件事：**

| 考量 | 真實情況 | 來源 |
|---|---|---|
| WGD 後突變變快 | copy 數加倍，同樣時間累積約 2 倍 SNV。SNV 時間若在 trunk 上均勻抽，會忽略這點。例：WGD 在 t = 0.5 時，均勻抽給 0.5，速率修正後約 0.33 | 〔推論〕；MutationTimeR 有校正這點〔論文〕 |
| subclonal WGD | TRACERx 421 有 19% 的腫瘤有 subclonal WGD | `research/.../05_tracerx_citation_check.md:75`〔論文〕 |
| WGD 時間的分布 | 未查 | 〔推論〕，待查文獻 |

- **S5 的候選做法（還沒選）：**
  1. 照搬 CONIPHER：逐 position 洗牌。沒有時間，不建議用在 multiplicity。
  2. 單一時間點，SNV 時間均勻。
  3. 單一時間點，SNV 速率和 copy 數成正比；可再加 subclonal WGD。
- 「WGD 是一次性事件」目前沒有附文獻出處，放進報告前要補引用。

### S6 事件順序與套用

| | 內容 |
|---|---|
| 輸入 | S3–S5 的事件 |
| 步驟 | 每個節點、每個 position 的事件隨機洗牌（`evolution.py:101-103`）。從 trunk 往下，把事件套在 `[cnA, cnB, mut]` 上（`evolution.py:114-132`）。事件定義在 `evolution.py:164-181`。 |
| 輸出 | 每個 clone、每個 position 的 `[cnA, cnB, mut]` |
| 假設 | SNV 在 A；`gain_A` 若有突變 copy，就多一份突變 copy（被複製的一定是帶突變的那份）；`loss_A` 若有突變 copy，就失去一份（`evolution.py:166-176`） |

### S7 clone 混合

| | 內容 |
|---|---|
| 輸入 | clone 清單、葉子、sample 數、purity 範圍 |
| 步驟 | 每個 sample 的 purity ~ U(min, max)，clone 數隨機，並確保每片葉子至少出現在一個 sample（`sequencing.py:51-63`）。clone 比例 = Dirichlet(1,…,1) × purity；normal = 1 − purity（`sequencing.py:35-37`）。 |
| 輸出 | 每個 sample 的 clone 比例 |
| 假設 | 比例平均接近（Dirichlet α = 1）；不限制 clone 之間的 CCF 差距 |

### S8 期望 VAF

| | 內容 |
|---|---|
| 輸入 | S6 的 profile、S7 的比例 |
| 步驟 | VAF = Σ 比例 × 突變 copy 數 ÷ Σ 比例 × (cnA + cnB)（`sequencing.py:66-92`） |
| 輸出 | 每個 SNV、每個 sample 的真值 VAF |
| 假設 | 定序沒有偏差 |

### S9 read 計數

| | 內容 |
|---|---|
| 輸入 | S8 的 VAF、`coverage` |
| 步驟 | depth ~ Poisson(coverage × 該位點 CN 份量 ÷ 平均 CN 份量)（`sequencing.py:95-99`）；alt ~ Binomial(depth, VAF)（`sequencing.py:102-104`） |
| 輸出 | 每個 SNV 的 ref／alt 數 |
| 假設 | SNV 之間獨立；沒有 read，也沒有 haplotype 資訊 |

### S10 雜訊

| | 內容 |
|---|---|
| 輸入 | `fract_noise`、`n_noise_clones` |
| 步驟 | 抽一部分 SNV 改屬假 cluster，給它隨機 CCF，再重抽 alt 數（`noise.py:5-24`） |
| 輸出 | 帶 `Noise` 標記的 variant 表 |
| 假設 | 雜訊是 cluster 層級的錯誤 |

### S11 輸出

| | 內容 |
|---|---|
| 輸入 | variant 表 |
| 步驟 | 依染色體長度比例隨機給 CHR／POS（`conversion.py:35-44`），REF／ALT 隨機，CN_A／CN_B 以 sample 平均的小數表示（`conversion.py:4-33`） |
| 輸出 | `_TX.tsv`（建樹輸入）、`_treeedges.tsv`、`_cloneprops.tsv`、`_events.tsv` 等（`simulate.py:89-95`） |
| 假設 | 座標只是標籤，不影響計數 |

## 4. 給 diplosim 的整理

依 10-28 會議議題二（雙套體與單倍型演化），從 CONIPHER 改成雙套體 long read 模擬時，改動可以分成四組：

| 組 | 步驟 | 和「雙套體」的關係 |
|---|---|---|
| 核心：雙套體 | S3（SNV 選 HP 與 copy）、S6（事件作用在 copy 上） | 直接相關。CONIPHER 的 SNV 只在 A，這裡要改成兩條 HP 都可能 |
| 結構：segment 與 WGD | S4（segment 為單位）、S5（單一時間點的 WGD） | 間接相關。要有 segment，同一條 read 上的 SNV 才會共享 CN 歷史 |
| 觀測：long read | S9（read、HP tag、共現、錯誤）、S10、S11 | 產生 long read 特徵，和演化模型無關 |
| 校正：cohort 參數 | S1、S2、S7（TRACERx 預設、樹形比例、min_gap） | 和雙套體無關，是讓模擬更像真實資料 |

diplosim 要從哪一步開始、每一組怎麼改，還沒有決定。

已決定（2026-10-29）：不加入 `het_map`、`depth_map`、`caller`、`allelic_precision`。這四個只用單一資料集校正。見 `../DECISIONS.md`。

已決定（2026-10-29）：不加入 `--preset`、`--phased`。連帶影響待決：HP tag 要怎麼決定。
