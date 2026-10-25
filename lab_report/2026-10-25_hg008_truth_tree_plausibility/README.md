# HG008 真實腫瘤統計：檢查 HP-aware 真值樹的事件是否真實（2026-10-25）

目的：用 GIAB HG008-T（胰臟癌 PDAC 細胞株）的 haplotype-resolved 真值，檢查 [`hp_truth_tree.png`](../../research/simulation_pipeline_research/figures/hp_truth_tree.png) 的事件在真實腫瘤中是否存在。
這是「先證明真值樹合理」主線的第一個實驗（見 `research/simulation_pipeline_research/truth_evidence_2026-10-25/README.md`）。

## 結論

- **haplotype-specific gain 與 CN timing 都有真實實例。** 在 2+1 gain 區，gained haplotype 上的 SNV 有 76 個 multiplicity 2（gain 前發生），65 個 multiplicity 1（gain 後發生）。這對應真值樹的 s1（gain 前）和 s8（gain 後）。〔實測〕
- **cnLOH 存在，而且兩種 timing 都有。** 2+0 區佔基因組 3.1%（77.7 Mb），germline het 100% 消失。區內 SNV 有 89 個 multiplicity 2（cnLOH 前），54 個 multiplicity 1（cnLOH 後）。這對應真值樹的 s9（cnLOH 前、multiplicity 2）。〔實測〕
- **somatic SNV 分佈在兩條 haplotype 上，比例接近 1:1。** 平衡區（1+1）的 SNV 有 2,208 個在 hap1、2,385 個在 hap2。這支持真值樹「每個 SNV 有 HP 歸屬，兩條 HP 都會有 SNV」的設定。〔實測〕
- **haplotype-specific 的 subclonal 事件存在，但規模比真值樹小。** 31 個 SV／CNV 被標為可能 subclonal。其中 8 個是單一 haplotype 的 deletion（≤ 20 kb），1 個是 4.6 Mb 的 2+1 gain（chrX，VAF 0.24）。〔實測〕
- **低 VAF 的 subclone 存在。** 27 個有 VAF 的 subclonal SV 中，15 個 VAF < 0.1（最低 0.021）。這表示細胞株內有小比例的 subclone。這間接支持 C3（CCF 0.10）這類低 CCF clone。〔實測 VAF；CCF 換算是推論〕
- **HG008 不能證明 3 件事：** 低 purity（細胞株接近 100% tumor）、subclonal cnLOH（沒有 2+0 被標為 subclonal）、SNV 層級的突變遺失（benchmark 只收 clonal SNV）。這 3 項要靠 SEQC2 和 TRACERx／PCAWG 文獻。〔實測〕
- **整體上，HG008 的 LOH 比例遠高於真值樹。** 51.6% 的基因組是 1+0 的 LOH-deletion。真值樹只有 seg B 一段 deletion。這是 PDAC 細胞株的特性，不代表真值樹不合理。〔實測＋推論〕

## 真值樹事件對照

| 真值樹事件 | 樹中的例子 | HG008 證據 | 判定 |
|---|---|---|---|
| ① 低 purity | purity 0.40 | 細胞株，不適用 | 不能證明 |
| ② subclonal HP gain | seg A HP1 gain 在 C2 | clonal 2+1 gain 48.4 Mb；subclonal 2+1 gain 1 個（chrX 4.6 Mb，VAF 0.24） | **支持** |
| ③ 突變遺失 | s2 隨 HP2 deletion 在 C4 消失 | 有 8 個 haplotype-specific subclonal deletion（≤ 20 kb）；SNV 層級遺失無法觀察 | 部分支持（只有機制） |
| ④ 低 CCF clone | C3 CCF 0.10 | 15 個 subclonal SV 的 VAF < 0.1 | 間接支持 |
| ⑤ HP 拆分 | 每個 SNV 屬 HP1 或 HP2 | 平衡區 SNV hap1:hap2 = 2,208:2,385 | **支持** |
| ⑥ cnLOH | seg D cnLOH 在 C2 | clonal 2+0 佔 77.7 Mb，germline het 100% 消失；沒有 subclonal cnLOH | **支持（clonal）** |
| ⑦ CN timing | s1 mult 2、s8 mult 1、s9 mult 2 | gain 區 mult 2:1 = 76:65；cnLOH 區 = 89:54 | **支持** |

## 資料

- GIAB HG008-T somatic small variant draft benchmark V0.4（GRCh38）：`somatic_tumornormal.vcf.gz`、`full_tumornormal.vcf.gz`、`all.bed`。
- GIAB HG008-T somatic SV＋CNV draft benchmark V0.6（GRCh38）：`CNV_PASS.calls.bed`（CN_total、CN_HAP1、CN_HAP2）、`CNV_ALL.calls.bedpe`（`possibly_subclonal`、`SVVIZ_VAF_ALL`）。
- 位置：`/big8_disk/boyu114/benchmark_data/GIAB/HG008/`。兩者都是 draft，不是正式版。
- SV VAF 來自 svviz2 在 HG008-T passage 23（MGH0823p23）資料上的計算。

## 做法

```bash
python3 -I tools/hg008_truth_tree_stats.py /big8_disk/boyu114/benchmark_data/GIAB/HG008 \
  lab_report/2026-10-25_hg008_truth_tree_plausibility/tables
```

1. 把 CNV PASS 區段依 `(CN_HAP1, CN_HAP2)` 分類：balanced 1+1、LOH-deletion 1+0、cnLOH 2+0、hap-specific gain（例如 2+1）。
2. 每個 somatic SNV 對到所在 CN 區段。讀 tumor GT（哪條 haplotype 帶突變、哪條被刪除）與 `TAC/TCN`。
3. multiplicity 定義：gained haplotype 或 cnLOH 區上的 SNV，`TAC=2` 視為 gain／cnLOH 之前發生，`TAC=1` 視為之後發生。
4. 用 germline het SNP 是否保留，檢查 CN 狀態是否正確。
5. 讀 bedpe 的 `possibly_subclonal=y` 事件與 VAF。

## 結果

表格在 [`tables/`](tables/)：

| 檔案 | 內容 |
|---|---|
| `cn_class_genome.tsv` | 各 CN 類別佔基因組與 benchmark 區的比例 |
| `cn_state_genome.tsv` | 每個 `CN_HAP1/CN_HAP2` 狀態的長度 |
| `germline_het_by_cn.tsv` | 各 CN 狀態的 germline het 保留比例 |
| `snv_by_cn_gt_tac.tsv` | somatic SNV × CN 狀態 × tumor GT × TAC/TCN |
| `hap_label_consistency.tsv` | CNV 刪除的 haplotype 與 SNV GT 是否一致 |
| `sv_cnv_subclonal_flag.tsv`、`subclonal_events.tsv` | subclonal SV／CNV 清單與 VAF |

### CN 狀態（GRCh38，PASS CNV）

| 類別 | 長度 | 佔比 | germline het 保留 |
|---|---:|---:|---:|
| LOH-deletion 1+0 | 1,289.4 Mb | 51.6% | 0.5–2.5% |
| balanced 1+1 | 1,084.6 Mb | 43.4% | 90.4% |
| cnLOH 2+0 | 77.7 Mb | 3.1% | 0% |
| hap-specific gain（2+1、1+3 等） | 48.4 Mb | 1.9% | 45–53% |

### 檢查：標籤一致性

- **CNV 的 haplotype 標籤和 SNV 的 GT 一致。** CNV 標為刪除的 haplotype，和 SNV GT 中的 `.` 有 7,886 個位點吻合，只有 4 個相反。〔實測〕
- **CN 狀態和 germline het 一致。** LOH 區的 het 幾乎全部消失，1+1 區保留 90.4%。〔實測〕
- **hap-specific gain 區的 het 只保留約 50%。** 這表示這些 CNV 區段內混有 LOH 小片段。這一類的 multiplicity 統計只算 GT 與 CN 一致的 SNV。〔推論〕

## 限制

- **benchmark 只收 clonal SNV。** likely-subclonal 的區域整段排除。所以 SNV 層級的 subclone 與突變遺失都看不到。
- **`TCN` 是 assembly contig 數，不是真實 CN。** 完全相同的多個 copy 會被算成一個，multiplicity 可能低估。
- **`tumorvariants.vcf.gz` 的 `.` 語意和 README 不一致。** 它把「沒有突變」也寫成 `.`。本實驗改用 `somatic_tumornormal.vcf.gz` 的 HG008-T 欄位，那裡 `.` 才只代表刪除。
- **HG008 是單一細胞株，而且是 PDAC。** 它的 LOH 比例特別高，不能當成一般腫瘤的參數分佈。
- **subclonal 事件只有 SV／CNV 層級，而且都偏小。** 真值樹的 subclonal 事件是整段 segment 等級。大型 subclonal 事件的頻率要看 TRACERx／PCAWG。
- **VAF → CCF 的換算假設 het 且 CN 已知**，所以「低 CCF clone」只是間接證據。
