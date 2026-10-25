# 典型 HP-aware 真值樹：壓力測試樹的對照組（2026-10-25）

目的：設計一棵「每個參數都落在真實腫瘤典型範圍」的 HP-aware 真值樹，當作 [`hp_truth_tree.png`](../../research/simulation_pipeline_research/figures/hp_truth_tree.png)（壓力測試樹）的對照。
依據：`research/simulation_pipeline_research/truth_evidence_2026-10-25/README.md` 的總判定，以及 TRACERx 421、PCAWG、HG008 的實測（`lab_report/2026-10-25_{tracerx,pcawg}_event_stats/`、`2026-10-25_hg008_truth_tree_plausibility/`）。

## 結論

- **典型樹的每個參數都取自真實 cohort 的實測中位數或常見值。** 依據見「參數與證據」表。〔資料實測〕
- **和壓力測試樹相比，主要差在 5 處：** clone 數 4 → 3、分岔 → 直線、突變遺失 20% → 1.5%、gain 區 early 比例 0.50 → 0.30、沒有 CCF ≤ 0.15 的 clone。〔設計〕
- **7 類事件中保留 6 類。** 低 purity、subclonal HP gain、突變遺失、HP 拆分、subclonal cnLOH、CN timing 都在，只是比例和密度降到典型值。低 CCF clone 刻意拿掉，因為它在單區域只佔 8.4%。〔設計〕
- **兩棵樹的用途不同。** 壓力測試樹檢查方法在極端情況下的表現，典型樹代表一般腫瘤。報告中兩棵要一起呈現。〔推論〕
- **本實驗只做設計，沒有跑 PhyClone。** 方法評估要等真值樹被接受、模擬器完成後再做。

## 設計

定義在 `tools/typical_truth_tree.py`。資料模型和壓力測試樹相同（`tools/draw_hp_truth_tree.py`）。

```text
C1 truncal（CCF 1.00，70% SNV）
 └─ C2（CCF 0.58）：seg A HP1 +1 gain
     └─ C3（CCF 0.29）：seg D cnLOH（HP2 被 HP1 拷貝取代）→ t6 遺失
```

| SNV 角色 | 個數 | 起源 | HP | segment | 設計目的 |
|---|---:|---|---|---|---|
| t1 | 3 | C1 | HP1 | A | gain 前 → C2／C3 中 multiplicity 2 |
| t2 | 7 | C1 | HP2 | A | 未 gain 的 HP，multiplicity 1 |
| t3、t4 | 62＋62 | C1 | HP1／HP2 | C | 對照（CN 中性） |
| t5 | 3 | C1 | HP1 | D | cnLOH 前 → C3 中 multiplicity 2 |
| t6 | 3 | C1 | HP2 | D | 在 C3 被 cnLOH 帶走（突變遺失） |
| t7 | 2 | C2 | HP1 | A | gain 後 → multiplicity 1 |
| t8、t9 | 17＋17 | C2 | HP1／HP2 | C | 對照 |
| t10 | 2 | C3 | HP1 | D | cnLOH 後 → multiplicity 1 |
| t11、t12 | 11＋11 | C3 | HP1／HP2 | C | 對照 |

共 200 個 SNV：C1 140（70%）、C2 36、C3 24。

## 參數與證據

| 參數 | 壓力測試樹 | **典型樹** | 依據（實測） |
|---|---|---|---|
| purity | 0.40 | **0.40** | TRACERx 421 tumour 中位 0.39；PCAWG 17% ≤ 0.40 |
| clone 數 | 4（3 個 subclone） | **3（2 個 subclone）** | PCAWG-11：21% 有 2 個 subclone；TRACERx 421 單區域 q25 為 3 個 clone |
| 樹形 | 分岔 | **直線** | TRACERx 421 單區域 73% 為直線 |
| subclone CCF | 0.80、0.45、0.10 | **0.58、0.29** | TRACERx 421 單區域 subclone CCF 中位 0.58、q25 0.29 |
| clonal SNV 比例 | 50% | **70%** | TRACERx 100 中位 30% subclonal |
| 突變遺失 | 20% | **1.5%**（3／200） | TRACERx 421 區域間：47% tumour ≥ 1 個、Q90 1.4%、最高 11.7%；TRACERx 100 換算約 4% |
| 遺失機制 | deletion＋cnLOH | **cnLOH** | TRACERx 421：75% deletion 型、25% cnLOH 型（本樹只放一種，以減少事件密度） |
| subclonal HP gain | seg A，+1 copy | **seg A，+1 copy** | TRACERx 421：91% tumour 有，91% 只差 1 copy |
| gain 區 early 比例 | 0.50 | **0.30**（3／10） | PCAWG 2:1 區中位 0.28（IQR 0.18–0.40） |
| subclonal cnLOH | seg D，CCF 0.80 | **seg D，CCF 0.29** | TRACERx 421：72% tumour 有，中位 7.2 Mb |
| subclonal CN 佔 SNV 比例 | 3／4 段 | **約 10%**（seg A 6%＋seg D 4%） | PCAWG subclonal CN 中位 7.6% 基因組；Watkins 中位 18% |
| depth | 200× | **50× 與 200×** | PCAWG 中位 48.5×；ONT 腫瘤 WGS 多在 30–60× |
| 低 CCF clone（≤ 0.15） | C3 0.10 | **無** | TRACERx 421 單區域只有 8.4% subclone CCF ≤ 0.15 |

**刻意保留的限制：**
- 只有一個 bulk 樣本。這是研究主軸（單樣本）。
- 每個 segment 只有兩種 tumour CN 狀態，沿用壓力測試樹的資料模型。
- SNV 數只有 200。真實腫瘤有數千個。SNV 越多，clone 的 CCF 越容易分開，所以這裡偏保守。

## 資料

- 真值與輸入：`input_200x/`、`input_50x/`（`data.tsv`、`truth.tsv`、`truth_tree.tsv`、`segments.tsv`、`data_hp.tsv`）。

## 做法

```bash
D=lab_report/2026-10-25_typical_truth_tree
for dp in 200 50; do
  python3 tools/hp_truth_tree_to_phyclone.py $D/input_${dp}x --tree typical --depth $dp --seed 1
done
```

`input_*/` 只是把設計轉成 PhyClone 輸入格式，方便之後使用。

## 結果：真值檢查

`input_200x/truth.tsv` 的無雜訊期望值（每個角色一列）：

| 角色 | 起源 CCF | 實際帶突變比例 | 期望 VAF |
|---|---:|---:|---:|
| t1（gain 前） | 1.00 | 1.00 | 0.283 |
| t2（未 gain HP） | 1.00 | 1.00 | 0.179 |
| t3、t4 | 1.00 | 1.00 | 0.200 |
| t5（cnLOH 前） | 1.00 | 1.00 | 0.258 |
| t6（被 cnLOH 帶走） | 1.00 | **0.71** | 0.142 |
| t7–t9（C2） | 0.58 | 0.58 | 0.104–0.116 |
| t10–t12（C3） | 0.29 | 0.29 | 0.058 |

segment 狀態：A 在 58% 的 tumour 細胞是 2+1；D 在 29% 的 tumour 細胞是 2+0；C 全部 1+1。和設計一致。

## 限制

- 典型樹的參數取自 cohort 的中位數或常見值。單一真實腫瘤不會每個參數都剛好在中位數。
- TRACERx 421 的 clone 數與 CCF 來自多區域重建，再取單區域子樹。單一樣本實際偵測得到的 clone 可能更少（PCAWG 中位 1 個 subclone）。
- 輸入只給 PhyClone 標準 8 欄，沒有 HP 資訊。HP 欄位在 `data_hp.tsv`，之後給 HP-aware 版本使用。
