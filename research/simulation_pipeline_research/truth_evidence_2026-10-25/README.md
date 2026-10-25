# HP-aware 真值樹的真實資料證據（2026-10-25）

目標：證明 `figures/hp_truth_tree.png` 中的事件在真實資料中存在。這樣模擬的 bulk 資料才可信。

> **目前主線（2026-10-25 起）：** 先證明這棵樹合理、符合真實腫瘤演化，再開發 long read bulk 模擬軟體。
> 所有觀察與實驗都先驗證「樹的事件與參數是否真實」（第 1 層）。
> phasing 雜訊校準（switch error、PS block、longphase 準確度）屬第 2 層，等模擬器加入 phasing 層時再做。
方法：4 個 subagent 平行搜尋一手來源。本目錄只整理證據，沒有下載大檔。

| 檔案 | 主題 |
|---|---|
| [`01_T2T_Q100_HG002.md`](01_T2T_Q100_HG002.md) | T2T-Q100 HG002 diploid assembly、GIAB v5.0q、HG002 ONT、phasing 評估 |
| [`02_GIAB_HG008_somatic.md`](02_GIAB_HG008_somatic.md) | GIAB 癌症樣本 HG008、mosaic 基準、stratifications、評估工具 |
| [`03_SEQC2_COLO829_celllines.md`](03_SEQC2_COLO829_celllines.md) | SEQC2 HCC1395、SPP titration、COLO829、CASTLE／Wakhan |
| [`04_event_evidence_real_tumors.md`](04_event_evidence_real_tumors.md) | 7 類事件在真實腫瘤的證據、參數範圍、模擬可信度標準（第 1、3 節已依 05／06 與實測修正） |
| [`05_tracerx_citation_check.md`](05_tracerx_citation_check.md) | TRACERx 相關數字逐篇核對：19 條，14 ✅、5 ⚠️ |
| [`06_pcawg_other_citation_check.md`](06_pcawg_other_citation_check.md) | PCAWG 與其他文獻逐篇核對：50 條，38 ✅、12 ⚠️ |

實驗（`lab_report/`）：`2026-10-25_hg008_truth_tree_plausibility`、`2026-10-25_seqc2_hcc1395_measured_purity`、`2026-10-25_tracerx_event_stats`、`2026-10-25_pcawg_event_stats`。

## 總判定（2026-10-25，文獻核對＋4 組資料實測後）

**一句話：7 類事件在真實腫瘤中都存在；但這棵樹把它們集中在 100 個 SNV 裡，遺失比例與事件密度高於典型腫瘤，應定位為「由真實事件組成的壓力測試樹」。**

| 事件／參數 | 設計值 | 最強真實證據 | 判定 |
|---|---|---|---|
| ① purity | 0.40 | PCAWG 中位 0.66（17% ≤ 0.40）；TRACERx 421 中位 0.39；本機 HCC1395 實測 0.15–0.74 | ✅ 典型 |
| ② subclonal HP gain | seg A +1 copy（C2） | TRACERx 421：91% tumour 有 haplotype-specific subclonal gain，91% 只差 1 copy；HG008 clonal 2+1 | ✅ 典型 |
| ③ 突變遺失 | 20% SNV | TRACERx 421 每 tumour 中位 0%、最高 11.7%；TRACERx 100 換算約 4% | ⚠️ 偏高（壓力測試） |
| ④ 低 CCF clone | C3 CCF 0.10 | TRACERx 421 單區域 8.4% subclone CCF ≤ 0.15；200× 下邊緣可偵測 | ✅ 存在，屬少數 |
| ⑤ HP 拆分 | 兩條 HP 都有 SNV | HG008 平衡區 hap1:hap2 = 2,208:2,385 | ✅ 典型 |
| ⑥ subclonal cnLOH | seg D（C2） | TRACERx 421：72% tumour 有 ≥ 1 Mb subclonal cnLOH，中位 7.2 Mb | ✅ 典型 |
| ⑦ CN timing | gain 區 early 0.5；cnLOH 區 1.0 | PCAWG 中位 0.28／0.56；HG008 兩種 timing 都有 | ⚠️ gain 區 early 偏高；cnLOH 在範圍內 |
| clone 數與形狀 | 4 clone，分岔 | PCAWG 2.3% 有 ≥ 3 subclone；TRACERx 421 單區域 20% 剛好 4 clone、73% 為直線 | ⚠️ 上尾；分岔屬少數 |
| depth | 200× | PCAWG 中位 48.5×；NRPCC 40 只有 0.4% 樣本達到 | ⚠️ 偏高 |

**建議：** 保留現有樹作為壓力測試，另外做一棵「典型樹」對照：突變遺失約 1–4%、2–3 個 clone、直線形、gain 區 early 比例約 0.3、depth 40–60×。

## 結論

- **沒有任何一套公開基準能單獨證明整棵樹。** 公開資料沒有「ONT bulk + 完整 clone tree 真值」。要分層證明：每類事件各找真實證據。〔04、03〕
- **T2T-Q100 只能證明 germline phasing 層。** 它給出 MAT/PAT 真值、het SNP 密度、PS block 長度、switch error。它不能證明 somatic 事件。〔01〕
- **HG008 是最強的 somatic + haplotype 證據。** 它的 CNV 有 `CN_HAP1/CN_HAP2`，SNV 有 haplotype 與 multiplicity。gain 前後的 SNV 都有實例。benchmark 仍是 draft（V0.4／V0.6）。〔02〕
- **SEQC2 HCC1395 能證明低 purity 和 cnLOH。** SPP 是真實 gDNA 混合。實測 purity 和 nominal 不同（nominal 20% → 實測 0.24）。CNV benchmark 有 320 個 LOH 區。〔03〕
- **你的 5 株 ONT 細胞株屬於 CASTLE Release 1。** Wakhan 為它們的 normal 建了 diploid assembly，也有 haplotype-specific CNA。這是最接近你資料的參考，但不是 curated 真值。〔03〕
- **3 個參數比真實資料樂觀。** depth 200×（PCAWG 中位約 46×）、C3 CCF 0.10、每對 SNV 80 條跨越 read。設計樹應標為「壓力測試」，再加一組 40–60× 的典型設定。〔04〕

## 7 類事件 × 證據來源

| 事件 | T2T-Q100 | GIAB HG008 | SEQC2／COLO829 | 真實腫瘤文獻 | 狀態 |
|---|---|---|---|---|---|
| ① 低 purity | — | 不能（細胞株約 100%） | **可以**（SPP 濕實驗混合） | TCGA 平均 0.62±0.20 | 有直接證據 |
| ② subclonal HP gain | — | 部分（haplotype CN，clonal 為主） | 部分（scDNA 只有 total CN） | TRACERx 62% 有 subclonal allelic imbalance | 文獻證據；無 HP 真值 |
| ③ 突變遺失 | — | 部分（passage 間 deletion 遺失） | 不能 | TRACERx subclonal 突變中位 13% 可能由 CN loss 造成 | 文獻 + HG008 實例 |
| ④ 低 CCF clone | — | 不能（mosaic 只有 85 SNV） | 部分（VAF 峰 0.15、0.08，無 label） | PCAWG 只保證 CCF ≥ 0.30 可偵測 | 證據弱；參數偏樂觀 |
| ⑤ HP 拆分 | **germline 真值** | **somatic SNV 有 haplotype 標記** | Wakhan assembly | long-read phylogeny 文獻 | germline 有真值；somatic 只有 HG008 |
| ⑥ cnLOH | — | 有（3 個大事件，位置未查到） | **可以**（320 個 LOH 區） | TCGA 約 47% 有 arm-level cnLOH | 有直接證據 |
| ⑦ CN timing | — | **可以**（TAC/TCN multiplicity） | 間接（COLO829 BFB→WGD） | PCAWG gain 80–90% 只多 1 copy | 有直接證據 |

## 建議做法（依優先順序）

1. **用真實 read 當背景，再植入設計樹。** 這是業界標準（SMC-Het 用 BAMSurgeon）。把 ONT 細胞株 read 依 HP 分組，再依設計樹植入 SNV。germline phasing 層就自動真實。〔04〕
2. **用 HG002 ONT CRAM + v5.0q 校準 phasing 參數。** 量 PS block 長度、switch error、unphased 比例，再寫進模擬器。〔01〕
3. **用 SEQC2 clonal SNV 量 `tX_nY` 的實測 purity。** 這能把 nominal purity 換成實測值。流程見 `03` 第 9 節。〔03〕
4. **用 HG008 的 `CN_HAP` 與 multiplicity 分佈校準 ②⑦ 的參數。**〔02〕
5. **在報告中把每類事件標上證據等級**（直接真值／文獻實測／推論），用上表即可。

## 待核實

- ~~v5.0q VCF 的 GT 順序可能是 `PAT|MAT`。~~ **已驗證（2026-10-25）：GT = `PAT|MAT`。** 三條證據〔實測〕：
  1. dipcall VCF 的 chrX 非 PAR 有 136,087 個 `.|1`，表示 hap2 帶 X，也就是 MAT。HG002 是男性。另有 21 個 `1|0`，全部在 PAR2 邊界前 600 bp 內（chrX:155,700,797–155,701,379）。
  2. chrY 2–26 Mb 的變異都是 `1|.`，表示 hap1 帶 Y，也就是 PAT。`.|1` 只集中在 11 Mb 和 56 Mb 兩個重複區。
  3. dipcall 的 hap1 BAM 開頭 read 名稱是 `chr*_PATERNAL`，hap2 是 `chr*_MATERNAL`。
  - v5.0q smvar 和 dipcall 在 chr1、chr20 共有 293,779 個 het 位點，GT 完全相同，沒有翻轉。所以 v5.0q 沿用 dipcall 的 `PAT|MAT`。
  - 限制：v5.0q 在 chrX/Y 非 PAR 寫成單倍體 GT（`1`），這兩區要看 dipcall VCF。
- 下列 DOI 沒有逐一打開核對：Wagner 2022（Cell Genomics，見 02），以及 Kuipers、SCARLET、CHISEL、Alleloscope、Nik-Zainal、Marass（見 04）。
- COLO829 的一手 purity／ploidy 沒有查到。本機 NYGC SNV truth 的上游論文出處沒有核實。〔03〕
- 用 Q100 評估 longphase 的 switch error 數字沒有查到。〔01〕

## 下載

**小檔已下載（2026-10-25）**：`/big8_disk/boyu114/benchmark_data/`，共 1.2 GB，361 個檔案，md5／gzip 檢查通過。清單見該目錄 `README.md`；腳本是 `tools/download_benchmark_small.sh`。
已下載的小檔：SEQC2 v1.2.1 VCF 與 high-confidence BED、SEQC2 CNV/LOH benchmark、GIAB v5.0q GRCh38 small variant VCF/BED、HG008 V0.4 VCF 與 V0.6 CNV、GIAB v3.6 stratification BED。
大檔（各 90–113 GB）：HG002 ONT haplotagged CRAM、HG008-T ONT BAM。要做真實 read 植入時再下載。
