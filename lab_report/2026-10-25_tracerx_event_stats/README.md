# TRACERx 421 事件頻率 vs HP-aware 真值樹（2026-10-25）

對象：`lab_report/2026-10-24_hp_truth_tree_phyclone/` 的手動真值樹（purity 0.40、200×、100 個 SNV、4 個 clone：C1→C2→C4、C1→C3）。
資料：TRACERx 421 公開處理後資料（Frankell 2023，Zenodo 7822002），401 個多區域 NSCLC tumour，1,426 個區域。
標記：〔論文主張〕＝論文文字；〔本次資料實測〕＝本次用公開資料算出；〔推論〕＝本檔的推論。

## 1. 結論

- **突變遺失 20% 偏高。** 本次實測的嚴格下限：每 tumour 中位 0%，pooled 0.7%，最高 11.7%。沒有任何 tumour 達 20%。CONIPHER 因 CN loss 移除的 cluster 只佔 0.5% 的突變。〔本次資料實測〕論文主張是 subclonal 突變的中位 13% 可能來自 CN loss（Jamal-Hanjani 2017）。所以 20%（佔全部 SNV）高於兩者。〔推論〕
- **低 CCF clone（C3 = 0.10）存在，但在尾端。** 單一區域視角下，8.4% 的 subclone CCF ≤ 0.15。24% 的區域至少有 1 個這種 subclone。cell prevalence ≤ 0.04（C3 的設計值）只有 1.7%。〔本次資料實測〕這是約 400× WES 的偵測結果，所以真實頻率可能更高。〔推論〕
- **subclonal cnLOH 常見，大小合理。** 72% 的多區域 tumour 至少有 1 個 ≥ 1 Mb 的區域間 subclonal cnLOH。每 tumour 中位 2 個事件，長度中位 7.2 Mb（IQR 2.7–23.4 Mb）。〔本次資料實測〕
- **單一 haplotype 的 subclonal gain 常見，而且多是 +1。** TRACERx 的 MSAI 標記出現在 71% 的 tumour。嚴格版的 haplotype-specific subclonal gain 出現在 91% 的 tumour。這些 gain 的長度中有 91%（每 tumour 平均）只差 1 個 copy。〔本次資料實測〕seg A 的 HP1 +1 gain 在範圍內。
- **4 個 clone 和分岔形狀：單區域視角下合理，但分岔屬於少數。** 單區域子樹的 clone 數中位 5（IQR 3–6），20% 剛好 4 個。73% 的單區域子樹是直線。4-clone 的單區域子樹中，83% 是直線，11% 和真值樹同形。〔本次資料實測〕全腫瘤樹（多區域合併）中位 9 個 clone，94% 分岔。
- **purity 0.40 在中位附近。** tumour 層級 purity 中位 0.39（IQR 0.27–0.55），48% 的 tumour ≤ 0.40。〔本次資料實測〕
- **depth 200× 低於 TRACERx WES，但這不是同一種資料。** TRACERx 每區域在突變位點的 depth 中位 396×。〔本次資料實測〕ONT WGS 通常更低。這一點已在 `04_*.md` 討論，本檔不改判定。

## 2. 對照表

判定標準：「在範圍內」＝設計值落在 TRACERx 的 IQR 或常見範圍；「偏高／偏低」＝在 IQR 外或超出觀察到的最大值；「尾端」＝存在但少於 10–25%。

| 事件 | 真值樹參數 | TRACERx 實測（本次） | 判定 |
|---|---|---|---|
| purity | 0.40 | tumour 中位 0.39（IQR 0.27–0.55）；區域 ACF 中位 0.41（IQR 0.26–0.60）；48% tumour ≤ 0.40 | **在範圍內** |
| 突變遺失比例（a） | 20／100 SNV（20%） | 嚴格下限：每 tumour 中位 0%，Q75 0.5%，Q90 1.4%，最大 11.7%；pooled 0.7%；47% tumour 至少 1 個；0 個 tumour ≥ 20%。佔 subclonal 突變：中位 0%，Q90 2.7%。cpn_removed cluster：pooled 0.5%，23% tumour 有 | **偏高**（高於實測最大值；論文主張的 13% 是另一個分母與較寬的定義） |
| 遺失機制（a） | deletion（s2）10 個、cnLOH（s10）10 個，各半 | 2,191 個遺失突變中，75% deletion 型（total CN 降）、25% copy-neutral 型 | **cnLOH 型略偏高**，但兩種都存在 |
| 低 CCF subclone（b） | C3 CCF 0.10（cell prevalence 0.04） | 單區域：subclone CCF 中位 0.58，Q10 0.17；8.4% ≤ 0.15；24% 區域至少 1 個；cell prevalence ≤ 0.04 佔 1.7% | **尾端**（存在，但少；偵測下限影響此數） |
| 中高 CCF subclone（b） | C2 0.80、C4 0.45 | 單區域 subclone CCF IQR 0.29–0.92 | **在範圍內** |
| subclonal cnLOH（c） | seg D，在 C2（CCF 0.80） | 72% 多區域 tumour ≥ 1 個（≥ 1 Mb）；每 tumour 中位 2（IQR 0–5）；長度中位 7.2 Mb（Q10 1.5、Q90 54 Mb）；佔基因組中位 1.0% | **在範圍內**（真值樹沒有指定 seg D 長度） |
| clonal cnLOH（參考） | 無 | 85% tumour 有；長度中位 8.9 Mb | — |
| subclonal HP-specific +1 gain（d） | seg A HP1 +1，在 C2 | MSAI 71% tumour；嚴格 haplotype gain 91% tumour、每 tumour 中位 14 個事件、基因組中位 12%；gain 中 +1 佔 91%（平均） | **在範圍內** |
| clone 數（d） | 4 | 單區域：中位 5（IQR 3–6），20% = 4。全樹：中位 9（IQR 6–13），7.5% = 4 | **單區域在範圍內；全樹偏低** |
| 分岔 vs 直線（d） | 分岔（C1→{C2, C3}） | 單區域：27% 分岔、73% 直線。全樹：94% 分岔 | **單區域屬少數**；全樹常見 |
| 4-clone 形狀（d） | `((())())`＝root 有 2 個子，其中 1 個再有 1 個子 | 單區域 4-clone 子樹 286 個：直線 237（83%）、同形 31（11%）、root→A→{B, C} 18（6%）。全樹 4-clone 30 棵：同形 20（67%） | **單區域屬少數**（11%） |
| depth | 200× | 每區域突變位點 depth 中位 396×（IQR 354–448×，WES） | 低於 TRACERx（不同平台，不直接比） |
| SNV 數 | 100 | exome TMB 中位 593（IQR 366–987） | 刻意縮小（壓力測試設計） |

## 3. 資料

- 來源與下載紀錄：`/big8_disk/boyu114/benchmark_data/TRACERx/README.md`。
- Frankell 2023（Zenodo 7822002，`figurecode.zip`，178 MB）：mutation table、每區域 SCNA（含跨區域 phased 的 nAraw／nBraw、MSAI、ACF）、401 棵 CONIPHER 樹、evolutionary metrics。
- Al Bakir 2023（Zenodo 7649257，`metsFigures.zip`，313 MB）：只用 `20220808_purityandploidy.txt` 交叉檢查 purity。502 個共同區域中，ACF 與此檔 purity 最大差 0.04。
- 下載量：zip 共 491 MB；解壓與衍生 TSV 後全目錄約 1.4 GB。兩筆都是 Zenodo open access（學術、非商業使用）。沒有使用 EGA 資料。
- TRACERx 100 沒有另外下載。原因：TRACERx 421 已重新處理並包含這 100 例。

## 4. 做法

### 4.1 可重跑指令

```bash
B=/big8_disk/boyu114/benchmark_data/TRACERx
# 1. fst/rds 轉 TSV（需要 R 套件 fst，裝在 ~/Rlib）
Rscript --vanilla tools/tracerx_export.R \
  $B/Frankell2023_zenodo7822002/extracted/figurecode/data \
  $B/Frankell2023_zenodo7822002/derived_tsv
# 2. 統計（約 40 秒）
python3 -I tools/tracerx_event_stats.py \
  --derived $B/Frankell2023_zenodo7822002/derived_tsv \
  --metrics $B/Frankell2023_zenodo7822002/extracted/figurecode/data/20221110_TRACERx421_evolutionary_metrics.tsv \
  --purity  $B/AlBakir2023_zenodo7649257/extracted/metsFigures/data/20220808_purityandploidy.txt \
  --out lab_report/2026-10-25_tracerx_event_stats/tables
```

`python3 -I` 會關掉 user site。腳本只把 `~/.local` 的 site-packages 加回 `sys.path`，不加 cwd 或資料目錄。

### 4.2 定義

**(a) 突變遺失（區域間、mutation 層級，嚴格下限）**
- 突變 m 在區域 R1 是 clonal：PhyloCCF ≥ 0.8 且 alt read ≥ 5。
- m 在區域 R2 缺席：alt read = 0 且 depth ≥ 50。
- 缺席可由 allele 遺失解釋：某一個 phased allele（A 或 B）在 R1 的 raw CN ≥ 0.5，在 R2 < 0.25。
- 機制：R1 到 R2 的 total raw CN 降 ≥ 0.5 記為 deletion 型；否則記為 copy-neutral（cnLOH）型。
- 分母：該 tumour 在樹表內的突變數（clean cluster）。另算以 subclonal 突變（`PyCloneClonal_SC == "S"`）為分母的版本。
- 補充指標：落在 CONIPHER `cpn_removed_clusters` 的突變比例（分母：有 PyClone cluster 的突變）。這些 cluster 被 CONIPHER 判定為 CN 造成，不放進樹。

**(b) subclone CCF**
- 單區域視角：每區域取樹上 CCF > 0 的 cluster，排除 trunk。CCF 用 `nested_pyclone$ccf_cluster_table`（PhyClone 意義的 CCF，以 tumour 細胞為分母）。cell prevalence = CCF × 該區域 ACF。
- tumour 平均視角：每個 subclone 在所有區域的 CCF 平均（缺席區域算 0）。

**(c) subclonal cnLOH（區域間）**
- 每區域 cnLOH：`nMinor == 0`、`nMajor ≥ 2`、`cpn_event_vs_ploidy == "neutral"`。
- subclonal：同一 segment 在 ≥ 1 區域是 cnLOH，且在 ≥ 1 區域 `nMinor ≥ 1`。
- 同一染色體相鄰的 subclonal segment 合併成一個事件，只留 ≥ 1 Mb。
- TRACERx 的 segmentation 是同一 tumour 各區域共用，所以可以逐 segment 比較。

**(d) 樹形與 haplotype-specific gain**
- 全樹：`graph_pyclone$Corrected_tree` 的 edge。只有 trunk 的 tumour 用 self-edge 表示，算成 1 個 clone。
- 單區域子樹：保留該區域 CCF > 0 的 cluster 和它們的祖先。
- 形狀用 canonical 括號字串比較。真值樹是 `((())())`。
- MSAI：直接用 TRACERx scna table 的 `MSAI` 欄位（任一區域 TRUE 即算）。
- haplotype-specific subclonal gain（寬鬆）：某 allele 的 round(raw CN) 在區域間不同，而且最小值 ≥ 1。
- 嚴格版：另外要求 integer total CN 在區域間不同、該 allele raw 差 ≥ 0.8、另一 allele raw 變動 < 0.5。
- +1 比例：寬鬆版事件中，max − min = 1 的長度比例。

## 5. 結果

完整數字：`tables/summary.json`。

| 檔案 | 內容 |
|---|---|
| `tables/summary.json` | 所有摘要統計與門檻 |
| `tables/mutation_loss_per_tumour.tsv` | (a) 每 tumour 的遺失突變數、機制、cpn_removed 比例 |
| `tables/subclone_ccf_per_region.tsv` | (b) 每區域每 subclone 的 CCF、purity |
| `tables/subclone_ccf_tumour_mean.tsv` | (b) 每 subclone 的跨區域平均 CCF |
| `tables/cn_per_tumour.tsv` | (c)(d) 每 tumour 的 cnLOH／LOH／MSAI／haplotype gain 事件數與基因組比例 |
| `tables/cn_events.tsv` | (c)(d) 合併後的每個 CN 事件（chr、start、end、長度） |
| `tables/tree_per_tumour.tsv` | (d) 全樹 clone 數、分岔、形狀、histology |
| `tables/tree_per_region.tsv` | (d) 單區域子樹 clone 數、分岔、形狀、purity |

補充觀察〔本次資料實測〕：
- (a) 11.5%（每 tumour 平均）的突變在某區域 clonal、在另一區域缺席。其中只有約 3% 能用 allele 遺失解釋。其餘大多是 branch-specific 的正常 phylogeny。
- (a) 遺失比例隨區域數上升：2–3 區域的 tumour 中位 0%，6 區域以上中位 0.5%。
- (b) tumour 平均視角下 48% 的 subclone 平均 CCF ≤ 0.15。原因是 region-private subclone 在其他區域算 0。這個數字不代表單一樣本會看到的 CCF。
- (c) subclonal cnLOH 的偵測率隨區域數上升：2 區域 51%、3 區域 73%、4–5 區域 86%、6 區域以上 96%。
- (c) 43% 的 subclonal cnLOH 事件 ≥ 10 Mb。54% 的 tumour 至少有 1 個 ≥ 10 Mb 的事件。
- (d) 全樹的分岔比例在 LUAD 95%、LUSC 91%。
- (d) 單區域子樹的 clone 數與分岔比例在不同 purity 間差不多（purity ≤ 0.3：中位 4、75% 直線；> 0.5：中位 5、73% 直線）。

## 6. 限制

- **TRACERx 是 NSCLC 多區域 WES，不是單一 bulk ONT WGS。** 結果代表肺癌；其他癌別的頻率可能不同。〔推論〕
- **(a) 是嚴格下限。** 只抓到「整個區域都遺失」的 clonal 突變。單一區域內的 subclonal 遺失（例如真值樹的 s2、s10 在 C2／C4 內遺失，CCF 降而不是歸零）用這份資料看不到。資料不支援單區域內 SNV 遺失的頻率。
- **(a) 和論文主張的 13% 不能直接比較。** Jamal-Hanjani 2017 的 13% 以 subclonal 突變為分母，而且定義是「可能」由 CN loss 解釋。本次是嚴格的區域間缺席＋allele 遺失。
- **mutation 的 haplotype 不知道。** WES 沒有 read-level phasing，所以 (a) 只要求「某一個 allele」掉到 ~0。若遺失的 allele 不是帶突變的那個，會高估；若 raw CN 估錯，會低估。
- **(b) 受偵測下限影響。** 約 400× WES 和 PyClone 的 cluster 合併會漏掉更小的 clone。單區域 CCF 由多區域聯合 clustering 得到，比真正的單樣本推論更精準。
- **(c)(d) 只看區域間的 subclonal 事件。** 單一區域內的 subclonal CN（raw CN 非整數）沒有計入。所以 subclonal cnLOH 的頻率是低估。
- **haplotype gain 的寬鬆版可能高估。** raw CN 四捨五入有雜訊。嚴格版較保守。TRACERx 自己的 MSAI 欄位最可靠。
- **單區域子樹不是單樣本重建的樹。** 它是多區域樹的投影；真正單樣本推論會因 CCF 相近而合併 clone，分岔更難辨識。
- **樹的不確定性：** 80% 的 tumour 有多於 1 棵 alt tree。本次只用 `Corrected_tree`（default tree）。
- **cnLOH 的定義依賴 `cpn_event_vs_ploidy == "neutral"`。** WGD tumour 的 cnLOH 可能被歸為 gain 或 loss。
