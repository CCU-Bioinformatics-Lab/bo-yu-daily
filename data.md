# HCC1395 演化樹資料清單

更新日期：2026-08-19  
判定基準：[from_variants_to_tumor_evolution_tree.md](from_variants_to_tumor_evolution_tree.md)

> [!WARNING]
> **文件依賴警告：請勿單獨刪除或改名本文件、[`model.md`](model.md)、[`longphase-clone.md`](longphase-clone.md) 或 [`convergence_cleanup_20260816.md`](convergence_cleanup_20260816.md)。**
> 本文件是模型輸入與 provenance 的唯一清單；模型公式見 `model.md`，研究／實作進度見 `longphase-clone.md`，輸出保留／待刪除政策見 `convergence_cleanup_20260816.md`。若搬移任一文件，請同步更新三者連結。

```yaml
document_id: data_manifest
document_type: data_provenance
links:
  - relation: provides_inputs_to
    target: model.md
  - relation: supports_experiments_in
    target: longphase-clone.md
  - relation: output_retention_policy
    target: convergence_cleanup_20260816.md
```

這份文件只回答三件事：

1. 正式重建演化樹需要哪些輸入。
2. 目前實際有哪些檔案、還缺哪些檔案。
3. 哪些資料不是模型輸入，但值得保留作驗證或未來擴充。

## 1. 一頁結論

### 1.1 正式流程必要輸入

| 資料 | 目前狀態 | 主要用途 |
|---|---|---|
| Reference FASTA | 已有 | 固定 GRCh38 座標與 REF allele |
| Raw tumor BAM + index | 已有 | 腫瘤 REF/ALT、depth、LongPhase-S 上游輸入 |
| Raw normal BAM + index | 已有 | matched-normal baseline、germline/CN 校正 |
| 最新同分支 ClairS `tp.vcf` | 已找到；ClairS v0.4.1、29,860 SNV，但尚非 model-ready | 最新 benchmark TP 來源候選 |
| 歷史流程的 indexed TP SNV VCF | 已有；ClairS v0.4.1、30,490 SNV | 既有 PS annotation 流程的實際基礎輸入 |
| BAM-derived PS TP VCF + index | 已重建；30,490 SNV，30,123 個有 PS | 依 tagged BAM read 的 PS 眾數為 TP SNV 補上 phase set |
| 歷史 `annotated_with_PS.vcf.gz` | **原路徑目前遺失** | 舊流程曾使用的 PS-annotated 衍生檔 |
| Phased germline VCF + index | 已有 | normal heterozygous phase backbone |
| LongPhase-S tagged tumor BAM + index | 已有 | 提供 read-level HP/PS 與 haplotype evidence |
| 正式 allele-specific CNV/LOH segment 檔 | **ASCAT canonical 5kHz 結果已取得；正式 purity input 固定為 `0.99`；segment schema/QA 仍標記 review** | 提供每個區段的 total/major/minor CN 與 LOH |
| ASCAT tumor purity | 已取得；HCC1395_5khz `purity=0.99` | 作為正式模型的 purity input，將 VAF、CN、multiplicity 投影到 CCF likelihood |

舊 M3 中間表已移除。新的正式流程固定為七個 gate（第 10 節有可直接重跑的命令與輸出契約）：

1. 明確選定 30,490-site TP benchmark mode，或另提供有 header/index 的完整 ClairS PASS VCF；目前完整 PASS site set 尚未提供，因此 canonical default 是 30,490。
2. 用同一份 canonical tagged BAM 做 VCF PS 的 read-level audit，不能把另一份 BAM 的 PS 沿用過來。
3. 將 ASCAT segments 正規化成共同的 `chr/start/end/major_cn/minor_cn/total_cn/loh_state` schema。
4. 對無 segment 對位與 `total_cn=0` 的 SNV 分別保留明確 QC 狀態，不刪除、不補值。
5. 從 canonical tagged BAM 重建 bulk 與 HP count tables，並檢查 counts 守恆與 site key 唯一。
6. 只有整合表具備固定 `multiplicity_posteriors`、major/minor CN、ASCAT purity=`0.99` 與普通 Binomial likelihood 所需欄位後，才允許更新模型；不再要求或產生 Beta-Binomial concentration，也不再把 LongPhase-S tumor DNA fraction 當作模型輸入。
7. 最後才做 M3 convergence、simulation recovery 與嚴格 held-out calibration。

第 9 節保留歷史優先順序；第 10 節是目前唯一的正式驗證入口。

## 2. 必要原始資料與路徑

### 2.1 Reference

```text
/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta
/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta.fai
```

狀態：已存在。BAM、VCF 與 CNV segments 都必須使用相同 GRCh38 contig 命名與座標系。

### 2.2 Tumor BAM

Raw tumor BAM：

```text
/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam
/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam.bai
```

用途：正式上游來源，可重建 REF/ALT counts、LongPhase-S tagged BAM，以及未來 CNV caller 所需訊號。原始 BAM 不含可供模型直接使用的 somatic HP tag。

LongPhase-S tagged tumor BAM：

```text
/bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam
/bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam.bai
```

用途：目前 haplotype channel 的主檔，含 read-level `HP`/`PS`。目前的單位點 REF/ALT 與 HP counts 都由這個版本建立。

模型使用邊界（2026-08-13 修正）：此 BAM 來自包含 `somatic-two-site-split` 實驗標籤的工作流程；正式 clone-tree likelihood 只讀取 `HP:Z:1-1` 與 `HP:Z:2-1`。`HP:Z:1-2/2-2` 暫時排除，`HP:Z:1/2` 只代表 germline side，不作 somatic ALT evidence。

### 2.3 Normal BAM

```text
/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395BL.bam
/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395BL.bam.bai
```

用途：matched-normal baseline、germline allele、tumor/normal CNV calling。正式流程需要 normal BAM，但目前 M3 MCMC 不會直接讀 BAM，而是讀上游整理後的表格。

### 2.4 Somatic VCF

#### 最新 ClairS `tp.vcf`（已找到，尚非 model-ready）

與目前 HCC1395 ONT 分支對應、檔名確實為 `tp.vcf` 的最新本地 ClairS 結果是：

```text
/big8_disk/data/HCC1395/ONT/ClairS_v0_4_1/benchmark_result/tp.vcf
```

實體位置：

```text
/big8_disk/mingen112/test_data/HCC1395/ONT/orig_bam/tumor/clairS/v0_4_1/ont_r10_dorado_sup_5khz_ssrs/benchmark_result/tp.vcf
```

狀態與 QA（2026-08-12 實查）：

- ClairS 版本：v0.4.1；
- 29,860 筆 records，全部是 SNV；
- 檔案大小：5,815,266 bytes，mtime：2025-05-25 11:15:31 +08:00；
- 是 benchmark 的 TP subset，不是完整 caller output；
- 檔案沒有 VCF header、沒有 index、沒有 `FORMAT/PS`，目前不能直接交給 `bcftools` 或模型；
- 同一 ClairS run 的 `output.vcf.gz` header 記錄輸入 BAM 為
  `/big8_disk/data/HCC1395/ONT/HCC1395.bam` 與
  `/big8_disk/data/HCC1395/ONT/HCC1395BL.bam`；這兩個檔案與本文件第 2.2、2.3 節的 5kHz methylation BAM 並非同一 inode/大小，因此正式使用前仍需做 read/reference provenance 對齊確認。

因此先把它記錄為「最新 ClairS TP 來源候選」，尚不直接指定為模型 canonical VCF。

#### 歷史 PS 流程使用的 indexed ClairS TP VCF

過去產生 30,490-site PS VCF 時實際使用的基礎輸入是：

```text
/big8_disk/liaoyoyo2001/InterSubMod/data/vcf/HCC1395/pileup/filtered_snv_tp.vcf.gz
/big8_disk/liaoyoyo2001/InterSubMod/data/vcf/HCC1395/pileup/filtered_snv_tp.vcf.gz.tbi
```

狀態與 QA（2026-08-12 實查）：

- VCF header：`source=ClairS`、`clairs_version=0.4.1`；
- 30,490 筆 records，全部是 biallelic SNV；
- sample column：`SAMPLE`；
- 檔案大小：1,150,924 bytes；index 大小：272,915 bytes；
- 此檔也是與 truth set 比對後保留的 `TP`（true positive）集合，不是 ClairS 的完整、未經 truth 篩選 caller output；
- 適合本次 HCC1395 benchmark-mode 演化樹分析，但不應當成未知樣本中可直接取得的無偏 somatic call set；
- VCF 本身沒有 `FORMAT/PS`，因此還不能直接提供 phase-set likelihood。

歷史來源關係：

```text
ClairS v0.4.1 calls / benchmark split
        + SEQC2 truth comparison
        -> filtered_snv_tp.vcf.gz (30,490 SNV; no PS)
        + LongPhase-S / phased-germline PS annotation
        -> annotated_with_PS.vcf.gz (historical derived file; currently missing)
```

此選擇與歷史流程一致：`run_vcf_all_snv.sh` 使用這份
`filtered_snv_tp.vcf.gz` 產生後續的 `annotated_with_PS.vcf.gz`。

注意：29,860-site `benchmark_result/tp.vcf` 與 30,490-site
`filtered_snv_tp.vcf.gz` 筆數不同，不可視為單純壓縮前後的同一檔。正式重跑前要先選定 canonical site set；若目標是重現既有 574 個 two-SNV PS 結果，應沿用 30,490-site 歷史集合。

#### 新重建的 BAM-derived PS TP VCF（目前可用）

```text
/bip8_disk/boyu114/multi_evol_tree/data/hcc1395_clairs_v041_tp_with_bam_ps.vcf
/bip8_disk/boyu114/multi_evol_tree/data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz
/bip8_disk/boyu114/multi_evol_tree/data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz.tbi
```

每個 PS 的 TP 位點統計：

```text
/bip8_disk/boyu114/multi_evol_tree/data/hcc1395_clairs_v041_tp_count_per_ps.csv
```

產生方式與結果（2026-08-12 實際執行）：

- 輸入 TP VCF：30,490-site ClairS v0.4.1 `filtered_snv_tp.vcf.gz`；
- PS 來源 BAM：`/big8_disk/liaoyoyo2001/InterSubMod/data/bam/HCC1395/tumor.bam`；
- 對每個 TP 座標抓取重疊 reads，取 read-level `PS` 的眾數寫入 `FORMAT/PS`；
- 沒有執行 `bcftools annotate`，也沒有用 phased germline VCF 補值；
- 30,123 個 TP SNV 有 PS，367 個沒有 PS；
- 共 4,079 個 PS，其中 574 個 PS 剛好含 2 個 TP SNV；
- 壓縮 VCF 已建立 tabix index，`bcftools index -n` 驗證為 30,490 records。

#### 歷史 PS-annotated 衍生檔（路徑失效，但已有替代檔）

歷史鎖定路徑：

```text
/bip8_disk/boyu114/intersubmod/output/annotated_with_PS.vcf.gz
/bip8_disk/boyu114/intersubmod/output/annotated_with_PS.vcf.gz.tbi
```

這個 target 目前不存在；`/bip8_disk/boyu114/InterSubMod/output/` 下只剩指向它的失效 symlink。

歷史 QA 記錄顯示該衍生 VCF 曾包含：

- 30,490 個 PASS biallelic SNV；
- 30,123 個有 `FORMAT/PS`；
- 367 個沒有 PS；
- sample column 為 `SAMPLE`；
- VCF 沒有 `FORMAT/HP`，HP 來自 tagged BAM。

歷史路徑本身仍然失效，但已由本 repo 的
`data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz` 與 `.tbi` 取代；若只需要依 BAM-derived PS 統計每個 phase set 的 TP 位點數，現在已可完整重跑。兩者不可因為統計數字相同就視為 byte-identical 檔案，因為新檔刻意沒有加入 phased germline VCF 的額外補值步驟。

### 2.5 Phased germline VCF

```text
/big8_disk/liaoyoyo2001/data/vcf/HCC1395BL_methyl_phase.vcf.gz
/big8_disk/liaoyoyo2001/data/vcf/HCC1395BL_methyl_phase.vcf.gz.tbi
```

用途：normal heterozygous variants、phase backbone、germline anchors，以及 HP orientation 的局部參照。

## 3. 正式 CNV/LOH 輸入：ASCAT canonical 5kHz 結果已取得

正式模型需要的是 segment-level allele-specific CNV/LOH，不需要把多套自製 observation TSV 全部塞進模型。本次已用 `data.md` 鎖定的 canonical 5kHz tumor/normal BAM 完成 ASCAT，因而已有符合核心需求的 segment-level allele-specific CN 資料。

### 3.1 Canonical ASCAT 輸出（目前可用）

執行腳本：

```text
tools/cnv_callers/hcc1395_5khz/run_ascat_hcc1395_5khz.sh
tools/cnv_callers/hcc1395_5khz/run_ascat_hcc1395_5khz.R
```

實際執行設定：

```text
tumor  = /big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam
normal = /big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395BL.bam
threads = 4
genome = hg38
min_base_qual = 10
additional_allelecounter_flags = -f 0
```

結果目錄：

```text
output/cnv_callers/ascat_hcc1395_5khz_t4/
```

主要檔案：

```text
output/cnv_callers/ascat_hcc1395_5khz_t4/HCC1395_5khz.segments.txt
output/cnv_callers/ascat_hcc1395_5khz_t4/HCC1395_5khz.segments_raw.txt
output/cnv_callers/ascat_hcc1395_5khz_t4/purity_ploidy.txt
output/cnv_callers/ascat_hcc1395_5khz_t4/ASCAT_objects.Rdata
output/cnv_callers/ascat_hcc1395_5khz_t4/run.log
```

結果 QA：

```text
segment records = 650
chromosomes     = 1–22, X（輸出原始欄位沒有 `chr` 前綴；投影到 VCF 前需統一命名）
purity          = 0.99
ploidy          = 2.89591670005995
goodnessOfFit   = 92.5999403270063
```

這次執行已成功完成並產生 segments、purity/ploidy、LogR/BAF 與 QC 圖。`run.log` 有兩個 `NAs introduced by coercion` 警告，但 R process exit code 為 0；因此先標記為「可用候選結果」，在 M3 正式使用前仍要完成欄位正規化與警告來源釐清。

### 3.1.1 ASCAT coercion warning 釐清（2026-08-14）

這兩個 warning 不是兩個 CNV segment 或兩個位點的數值錯誤，而是 ASCAT 3.2.0 內部同一個索引轉換表達式被呼叫兩次：

```r
SNPpos[as.numeric(names(bafsegmented)), ]
```

本次 `bafsegmented` 的 row names 是 `chr_position` locus ID（例如 `1_995371`、`X_343200`），不是 ASCAT 這段程式預期的數字列索引。因此 `as.numeric("1_995371")` 會得到 `NA`，R 才顯示 `NAs introduced by coercion`。輸入本身可由 `SNPpos` 的 row names 完整對回；549,261 個 segmented BAF loci 全部是這種可解析的 `chr_position` 格式，其中只有 76 個是 X chromosome loci。

已用同一份 `ASCAT_objects.Rdata` 做診斷性重跑，將內部 locus names 暫時改成正確的數字列索引：

```text
原始 names：warning 2 次；purity=0.99、ASCAT psi=2.8、GOF=92.5999403、650 segments
修正 names：無 coercion warning；purity=0.99、ASCAT psi=2.8、GOF=92.6038069、650 segments
```

兩次輸出的 650×4 segment index/CN 矩陣完全相同（`identical = TRUE`），因此這次 warning 對目前 HCC1395 5-kHz 的 segment、major/minor CN 與投影結果沒有觀察到實質影響。它仍保留為 `review`，因為這是 caller 相容性問題，不能把 warning 靜默丟掉；正式流程應在 wrapper 中保留 `chr_position → SNPpos row index` 的明確轉換，再產生無 warning 的 canonical ASCAT provenance。

完整診斷記錄曾位於 `input_validation_20260814/stage_03_ascat_warning_diagnosis.md`，該歷史目錄已於 2026-08-16 刪除；ASCAT warning 結論保留於本文件與 `convergence_cleanup_20260816.md`。

### 3.2 ASCAT 欄位與模型共同格式

ASCAT 原始 segment 檔欄位是：

```text
sample  chr  startpos  endpos  nMajor  nMinor
```

映射到模型共同格式：

```text
chrom    = chr
start    = startpos
end      = endpos
major_cn = nMajor
minor_cn = nMinor
total_cn = nMajor + nMinor
loh_state = 由 minor_cn 與 total_cn 的明確規則推導
```

目前可採用的初始 `loh_state` 規則：

```text
minor_cn = 0 且 total_cn > 0  -> LOH-like
total_cn = 0                  -> homozygous deletion
minor_cn > 0                  -> non-LOH
```

這表示 ASCAT 已提供 `chrom/start/end/major_cn/minor_cn`，而 `total_cn` 與 `loh_state` 是可重現的衍生欄位；尚未直接產生 `P(retained_HP1)`、`P(retained_HP2)`、retained-allele direction 或每個 segment 的 confidence。`nMajor/nMinor` 是 copy-number 大小排序，不等同 LongPhase-S 的 HP1/HP2。

Caller 的輸入相容性、已找到的 ASCAT 程式／reference／腳本、HCC1395 歷史結果路徑與 provenance 限制，統一記錄於 [cnv_tool_and_data.md](cnv_tool_and_data.md)。

建議統一格式：

```text
sample  chrom  start  end  total_cn  major_cn  minor_cn  loh_state  caller  confidence
```

最少必要欄位：

```text
chrom
start
end
total_cn
major_cn
minor_cn
loh_state
```

可由 ASCAT、FACETS、PURPLE 或其他正式 allele-specific CNV caller 轉換成這個共同格式。每個 SNV 再依座標投影到對應 segment。

`major_cn/minor_cn` 只表示多、少兩側的 copy number，不直接表示 retained HP1 或 retained HP2。HP direction 應由 phased germline variants、tagged reads與 PS-local orientation 另外估計。

## 4. M3 中間表狀態：舊表已移除；Stage 6 canonical 整合表已重建

2026-08-13 確認先前的 M3 中間表來自舊資料流程，因此下列檔案已刪除，不再是模型輸入：

```text
output/longphase_clone/snv_bulk_counts.tsv.gz
output/longphase_clone/snv_hp_counts.tsv.gz
output/longphase_clone/m3_latent_cn_site_posterior.tsv.gz
output/longphase_clone/m3_bam_sensitivity_site_ccf_proxy.tsv.gz
output/longphase_clone/m3_bam_sensitivity_candidate_tree.json
```

2026-08-15 已由本文件確認的 canonical VCF、tagged tumor BAM count tables 與 site-level ASCAT schema 重建的模型實際讀取表：

```text
output/longphase_clone/stage_06_likelihood_20260815_binomial/likelihood_input.tsv.gz
```

它保留 30,490 個 TP SNV；其中 30,006 個為 `eligible`，399 個 `excluded_cn_zero` 與 85 個 `excluded_unmapped_segment` 保留為明確 QC 狀態，沒有用假 CN 或假 multiplicity 補值。每個 eligible site 含 bulk/HP counts、major/minor/total CN，以及固定輸入的 multiplicity candidates/posteriors；不含 Beta-Binomial concentration。完整 QA 與 provenance 分別見 [`stage_06_likelihood_input_qa.json`](output/longphase_clone/stage_06_likelihood_20260815_binomial/stage_06_likelihood_input_qa.json) 和 [`stage_06_likelihood_manifest.json`](output/longphase_clone/stage_06_likelihood_20260815_binomial/stage_06_likelihood_manifest.json)。

這是 **已核准的 Stage 6 資料輸入表**。2026-08-15 已以普通 Binomial raw-count likelihood、固定 `multiplicity_posteriors` 與 dynamic CN support 重建並通過 schema/QA；舊的 2026-08-14 Beta-Binomial table 僅保留作歷史比較。這只是資料介面驗證，不是 production posterior；長鏈仍須在新 likelihood 下重跑。

M3 主程式的歷史版本讀取 TSV，而不會在每次 MCMC iteration 重掃 BAM：

```text
tools/run_longphase_clone_m3_tssb_mcmc.py
```

## 5. 非必要，但建議預備與保留

### 5.1 Tagged normal BAM

```text
/big8_disk/liaoyoyo2001/data/bam/HCC1395BL_ONT_5khz_simplex_5mCG_5hmCG_tagged.bam
/big8_disk/liaoyoyo2001/data/bam/HCC1395BL_ONT_5khz_simplex_5mCG_5hmCG_tagged.bam.bai
```

不是目前 M3 必要輸入。可保留作 normal HP/PS QC、germline haplotype 分層與未來 retained-allele orientation 分析。

### 5.2 SEQC2 somatic truth set

```text
/big8_disk/data/HCC1395/SEQC2/high-confidence_sSNV_in_HC_regions_v1.2.1.vcf.gz
/big8_disk/data/HCC1395/SEQC2/High-Confidence_Regions_v1.2.bed
```

用途：held-out validation、callability 與 sensitivity QC。不能把 truth VCF 當成未知 somatic mutation 的模型輸入，否則會造成資料洩漏。

### 5.3 SEQC2 CNV/LOH benchmark

來源目錄：

```text
/big8_disk/data/HCC1395/SEQC2/CNV/
```

主要檔案：

```text
Additional_file_5_cnv_benchmark_calls.vcf
ngs_benchmark_cnv_gain_cn.bed
ngs_benchmark_cnv_loss_cn.bed
ngs_benchmark_cnvs_gain_loss_loh.bed
Additional_file_3_cnv_gain_cn_median.txt
Additional_file_4_cnv_loss_cn_median.txt
exclusion.bed
```

這些是外部 benchmark，可用於驗證新 CNV caller 的 gain/loss/LOH overlap 與排除區域；不再當成正式演化樹 likelihood 的主要 CNV 輸入。其 site-level 衍生表：

```text
output/longphase_clone/m3_cnv_loh_reference.tsv.gz
```

同樣只保留作 benchmark overlay 與歷史比較。

### 5.4 LongPhase-S tumor DNA fraction report（reference-only，不是模型輸入）

```text
/bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging_purity.out
```

報告值：

```text
tumor DNA fraction = 0.958936
```

這是 LongPhase-S 的資料估計值，**不再作為目前模型的 input**，也不再用來取代 ASCAT purity。它只保留作 provenance、歷史比較與 sensitivity reference。正式 M3 模型固定使用 ASCAT `purity=0.99`；若未來要把 purity uncertainty 納入模型，必須另開版本並明確記錄 uncertainty model。

## 6. 不再使用或刻意排除

以下已刪除，不是未來正式 CNV 輸入：

```text
# The old BAM-derived allele-specific CN table was deleted; its summary/audit
# is historical and not a current model input.
/bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_cnv_multisomatic_altref_observation/cnv_intervals.tsv
/bip8_disk/boyu114/longphase-s-boyu/output/cnv_loh_adjacency/interval_adjacency.tsv
/bip8_disk/boyu114/longphase-s-boyu/output/strict_cnv_adjacent_loh_phased_snp_audit_gain_and_loss/site_summary.tsv
```

目前也刻意不把下列項目當成模型必要輸入：

```text
RR/RA/AR/AA joint-read summaries
只限 exactly-two-SNV PS 的資料
跨 PS 強制對齊的 HP1/HP2 label
WGD event、timing 或 mode
SEQC2 truth calls 作為訓練/建樹答案
```

## 7. 參數來源與目前設定

| 參數 | 數值 | 性質 |
|---|---:|---|
| ASCAT tumor purity (`rho_ASCAT`) | 0.99 | 正式模型 input，來自 `purity_ploidy.txt` |
| LongPhase-S tumor DNA fraction | 0.958936 | reference-only；不進目前 likelihood |
| HCC1395 ploidy | 2.85 | SEQC2/HCC1395 外部背景值；未來優先使用正式 CNV caller 結果 |
| MAPQ threshold | 20 | 人工 QC 設定 |
| baseQ threshold | 10 | 人工 QC 設定 |
| fallback sequencing error | 0.005 | 模型假設，尚未完成 site-specific calibration |
| finite node count K | 2–8 | 模型容量；程式預設 8，目前 strict 工作設定 6 |

`MAPQ`、`baseQ`、error rate 與 `K` 都不是從 HCC1395 自動推導出的生物學真值。

## 8. 簡化資料流

```text
Reference + raw tumor/normal BAM
        + somatic VCF with PS
        + phased germline VCF
                    │
                    ▼
       LongPhase-S tagged tumor BAM
                    │
                    ▼
          REF/ALT counts + HP/PS counts

Formal allele-specific CNV/LOH segments
                    │
                    ▼
       每個 SNV 的 total/major/minor CN

counts + CN/LOH + ASCAT tumor purity (`rho_ASCAT=0.99`)
                    │
                    ▼
       clone assignment + tree posterior

SEQC2 truth/CNV benchmark ──► 只作外部驗證
```

## 9. 下一個資料準備優先順序

目前原則是：**先確保所有資料來自同一組 canonical inputs，再建立衍生表；不能拿舊 M3 proxy 補缺值。**

| 優先級 | 要做的事 | 完成條件 |
|---:|---|---|
| **P0** | 鎖定 canonical input bundle | 固定 reference、raw tumor/normal BAM、LongPhase-S tagged tumor BAM、phased germline VCF、ASCAT `purity_ploidy.txt`（`rho_ASCAT=0.99`）與 30,490-site somatic site set；記錄實體路徑、版本、檔案大小與 checksum |
| **P1** | 驗證並固定 somatic VCF 的 PS | 逐位點核對 `data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz` 與 canonical tagged tumor BAM 的 read-level PS；若不一致，必須由該 tagged BAM 重新回填 PS，不能沿用另一份 BAM 的 PS |
| **P2** | 重建單位點 observation tables | 從 canonical somatic VCF＋tagged tumor BAM 重算 REF/ALT、depth、VAF、PS、`HP:Z:1-1` 與 `HP:Z:2-1` counts；排除 `1-2/2-2`，並記錄 MAPQ/baseQ、excluded flags、零深度與缺 PS 位點 |
| **P3** | 固定正式 allele-specific CNV/LOH segments | ASCAT canonical 5kHz run 已完成；將 `HCC1395_5khz.segments.txt` 轉為共同 schema，明確寫入 `total_cn/loh_state/caller/confidence`，並完成兩個非致命 warning 的 QC 說明 |
| **P4** | 建立每個 SNV 的整合輸入 | 將 SNV 投影到 CNV/LOH segment，建立 CN、LOH、multiplicity 候選及 HP-side evidence；retained HP 方向不足時標成 `unknown`，不可硬補 HP1 或 HP2 |
| **P5** | 建立 provenance manifest 並驗收 | 每張中間表附產生腳本、完整命令、input checksum、row/site count、schema、filter、建立日期；確認 site key 唯一、座標/contig 一致、REF 符合 reference、bulk 與 HP counts 守恆 |
| **P6** | 重新啟動模型 | 只有 P0–P5 全部通過後，才進行 M3 smoke test、多鏈 posterior、simulation 與 held-out validation |

### 9.1 目前立即要做的三件事

```text
第一：PS VCF ↔ canonical tagged BAM 一致性稽核
第二：用通過稽核的資料重建 REF/ALT 與 HP1-1/HP2-1 counts
第三：產生正式 allele-specific CNV/LOH segment 檔
```

### 9.2 暫時不要做

- 不使用已刪除的舊 M3 intermediate/proxy tables。
- 不為了讓 sampler 能跑而用 SEQC2 benchmark 補成正式 CNV likelihood；SEQC2 只作外部驗證。
- 不把 `HP:Z:1-2/2-2`、exactly-two-SNV PS 或 RR/RA/AR/AA 當成目前必要輸入。
- 在 provenance manifest 與 QA 未通過前，不重新產生或解讀新的 M3 tree。

舊的 `input_manifest.json` 與 `input_qa_report.md` 是 2026-08-06 的歷史快照，已於 2026-08-16 刪除；目前資料狀態以本文件與新版 Stage 6 manifest 為準。

## 10. 2026-08-14 七階段可重現驗證管線

本節把「資料準備完成」定義成可執行的 gate，而不是只在文件中宣稱完成。入口程式是：

```text
tools/validate_hcc1395_m3_pipeline.py
```

它只讀取輸入 BAM/VCF/ASCAT/reference，將 audit 表與 JSON manifest 寫到指定 output directory；不會修改原始 BAM、VCF 或 ASCAT 檔案。每次執行都會記錄完整命令、輸入大小／mtime，對小檔案寫入 SHA256；273 GB BAM 與 3.1 GB reference 若要做內容 checksum，需明確加 `--hash-large-files`。

### 10.1 Canonical site-set decision

目前正式 reproducibility mode 是：

```text
site VCF = data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz
site label = hcc1395_tp_30490
records = 30,490 PASS biallelic SNVs
PS-present = 30,123
PS-missing = 367
```

這是為了保留既有 574 two-SNV PS 結果的可重現性。`/big8_disk/data/HCC1395/ONT/ClairS_v0_4_1/benchmark_result/tp.vcf` 只有 29,860 筆 TP、沒有 header/index/PS，不能冒充完整 ClairS PASS set；若日後要改用 complete PASS，必須提供有 header、index、reference build 與 provenance 的 VCF，並用 `--site-mode complete_clairs_pass` 另建一個 output directory，不能覆蓋本模式結果。

Gate 1 pass 條件：所有選定 records 都是 PASS、biallelic SNV；30,490 mode 另外必須得到 `30,490 / 30,123 / 367` 三個 snapshot 數字。site key digest 也會寫入 `stage_01_site_universe.json`。

### 10.2 PS VCF ↔ canonical tagged BAM audit

canonical read-level source 是：

```text
/bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam
```

每個 SNV 以 `MAPQ >= 20`、`baseQ >= 10`、排除 unmapped/secondary/QC-failed/duplicate/supplementary reads 的規則，將 callable REF/ALT reads 的 BAM `PS` 與 VCF `FORMAT/PS` 比較。相同 query name 在同一 locus 的重複 pileup observation 只算一條 read，但會列入 `duplicate_query_name` QC 欄位；因此這是 read-level audit，不是 pileup row-level audit。

輸出：

```text
ps_read_audit.tsv.gz
stage_02_ps_audit.json
```

主要狀態：

| 狀態 | 意義 |
|---|---|
| `match_alt` | VCF PS 至少出現在一條 callable ALT read 上 |
| `discordant_alt` | ALT read 有 PS，但沒有 VCF 指定的 PS |
| `match_ref_only` | 只有 REF read 支持 VCF PS，沒有 callable ALT read |
| `bam_ps_missing` | 有 allele reads，但 BAM 沒有 PS tag |
| `no_callable_reads` | 目前 filter 下沒有可用 REF/ALT read |
| `vcf_ps_missing` | VCF 本身沒有 PS；不能假裝成 audit pass |
| `bam_contig_missing` | VCF contig 不在 BAM header |

正式 gate 使用 `--max-discordance-fraction 0.01`；`--max-sites` 只可作 smoke test，結果會標成 `smoke_only`，不算正式通過。

### 10.3 ASCAT normalization

ASCAT 原始檔：

```text
output/cnv_callers/ascat_hcc1395_5khz_t4/HCC1395_5khz.segments.txt
```

正規化輸出：

```text
ascat_segments.normalized.tsv.gz
stage_03_ascat_summary.json
```

共同 schema：

```text
segment_id  sample  chr  start  end  major_cn  minor_cn  total_cn  loh_state  caller  confidence
```

座標為 1-based inclusive；`total_cn = major_cn + minor_cn`。目前 650 段、23 個 chromosome、沒有 segment overlap。`loh_state` 只做可重現的分類：`total_cn=0 → homozygous_deletion`、`minor_cn=0 且 total_cn>0 → loh_like`、其餘 → `non_loh`。`confidence=global_fit_only` 不代表每一個 segment 都有獨立可信度；retained HP1/HP2 direction 仍不能由 ASCAT 的 major/minor 自動推出。

### 10.4 SNV 對 CN/LOH 的 QC projection

輸出：

```text
site_cnv_qc.tsv.gz
stage_04_site_cnv_qc.json
```

每一個 site 都保留一列，狀態不可互相混淆：

```text
mapped_nonzero_cn  = 有一段覆蓋且 total_cn > 0
cn_zero            = 有一段覆蓋但 total_cn == 0（保留，不能靜默刪掉）
unmapped_segment   = 沒有 ASCAT segment 覆蓋（目前預期 85）
segment_overlap    = 超過一段覆蓋，需回頭檢查 caller/schema
```

對 30,490-site snapshot，正式 gate 會檢查 `unmapped_segment=85` 與 `cn_zero=399`。這兩個數字是 QC 分層，不是把 484 個位點直接餵給模型的 CN=0 或隨意補成 diploid。

### 10.5 Canonical bulk/HP counts

先用明確路徑重建，不依賴已刪除的舊 default：

```bash
python3 tools/build_hcc1395_longphase_clone_site_counts.py \
  --vcf data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz \
  --bam /bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam \
  --outdir output/longphase_clone/canonical_counts_20260814 \
  --workers 4 --min-mapq 20 --min-baseq 10 \
  --sample-label HCC1395
```

輸出契約：

```text
snv_bulk_counts.tsv.gz
snv_hp_counts.tsv.gz
snv_hp_qc.tsv.gz
site_counts_manifest.json
```

bulk table 是單位點 `REF/ALT/depth/VAF`；HP table 保留完整 observed HP domain，但模型目前只把 `1-1` 與 `2-1` 作 somatic ALT haplotype evidence，`1-2/2-2` 不進 likelihood。每個 site 必須有固定 10 個 HP rows；bulk REF/ALT 必須等於 HP rows 加總；site key 必須唯一；manifest 必須標示 `single_site_only=true`、canonical tagged BAM、filters 與 `deduplicate_query_names=true`。這個 count builder 不產生 RR/RA/AR/AA，也不把 exactly-two-SNV PS 當成模型限制。

完成後用既有 validator：

```bash
python3 tools/validate_hcc1395_longphase_clone_counts.py \
  --outdir output/longphase_clone/canonical_counts_20260814
```

再把 counts directory 傳給本節 pipeline 的 `--counts-dir`，讓 `stage_05_counts_qa.json` 以相同 site universe 檢查 row 數與 manifest。

### 10.6 新 likelihood 的輸入契約（Stage 6 Binomial 資料表已完成）

第 6 gate 不是「欄位存在就算完成」，而是要求整合表至少明確提供：

```text
major_cn
minor_cn
total_cn
multiplicity_posteriors
```

其中 `multiplicity_posteriors` 必須依該 site 的 major/minor CN 動態產生，不能固定塞 `1..2`。Beta-Binomial concentration 不再是輸入欄位，也不由模型推估。

2026-08-15 的 Stage 6 builder 已滿足這個資料契約，並寫出 [`stage_06_model_gate.json`](output/longphase_clone/input_validation_20260815_binomial/stage_06_model_gate.json) 的 `pass`。`multiplicity_posteriors` 以 major/minor side 邊際化的中性先驗與普通 Binomial observation 形成，並在 sampler 中作固定輸入的邊際化；不能誤讀為 sampler 重新估計的 multiplicity posterior。

### 10.7 M3 convergence、simulation、held-out calibration gate

第 7 gate 必須同時有：

```text
label-invariant R-hat / ESS diagnostics
simulation truth-recovery summary
strict held-out calibration summary
```

輸入資料變更、likelihood 變更或 site universe 變更後，舊的 M3 tree PNG 不算新結果。只有 `stage_06_model_gate.json=pass`，且新的 M3 output 明確包含 R-hat、ESS、simulation recovery、held-out calibration 四類 artifact，`stage_07_m3_gate.json` 才可能是 `pass`。否則總 manifest 必須是 `blocked`。

### 10.8 一條可重跑的正式命令

先做 smoke（只驗證介面，不宣稱資料完成）：

```bash
python3 tools/validate_hcc1395_m3_pipeline.py \
  --site-vcf data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz \
  --tagged-bam /bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam \
  --ascat-segments output/cnv_callers/ascat_hcc1395_5khz_t4/HCC1395_5khz.segments.txt \
  --reference /big8_disk/ref/GRCh38_no_alt_analysis_set.fasta \
  --site-mode tp30490 --site-label hcc1395_tp_30490 \
  --outdir output/longphase_clone/input_validation_20260814_smoke \
  --max-sites 10 --audit-workers 2
```

正式資料 gate 使用同一命令但移除 `--max-sites`，並可加入 `--counts-dir`、`--integrated-table`、`--m3-dir`。以下是
2026-08-14 的歷史 full-gate 命令；其中產生的舊 Stage 6 表格與 Beta-Binomial M3
結果只保留作 provenance/比較，不是目前模型輸入：

```bash
python3 tools/validate_hcc1395_m3_pipeline.py \
  --site-vcf data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz \
  --tagged-bam /bip8_disk/boyu114/longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam \
  --ascat-segments output/cnv_callers/ascat_hcc1395_5khz_t4/HCC1395_5khz.segments.txt \
  --reference /big8_disk/ref/GRCh38_no_alt_analysis_set.fasta \
  --site-mode tp30490 --site-label hcc1395_tp_30490 \
  --max-discordance-fraction 0.01 --audit-workers 4 --audit-window-size 50000000 \
  --counts-dir output/longphase_clone/canonical_counts_20260814 \
  --outdir output/longphase_clone/input_validation_20260814
```

這條歷史 full-gate 命令的主要輸出是：

```text
validation_manifest.json
stage_01_site_universe.json
stage_02_ps_audit.json
stage_03_ascat_summary.json
stage_04_site_cnv_qc.json
stage_05_counts_qa.json
stage_06_model_gate.json
stage_07_m3_gate.json
site_universe.tsv.gz
ps_read_audit.tsv.gz
ascat_segments.normalized.tsv.gz
site_cnv_qc.tsv.gz
```

目前 2026-08-15 Binomial likelihood 的 Stage 6-only refresh 使用下列命令；它重用
前一輪已完成的 Stage 1--5 raw-data audit，只重新驗證現行 Stage 6 schema 與
`multiplicity_posteriors`。若未來重建 Stage 1--5，應另開新的日期版本目錄，不要覆寫
這份 provenance：

```bash
python3 tools/validate_hcc1395_m3_pipeline.py \
  --stage6-only \
  --integrated-table output/longphase_clone/stage_06_likelihood_20260815_binomial/likelihood_input.tsv.gz \
  --outdir output/longphase_clone/input_validation_20260815_binomial
```

目前版 Stage 6 gate 的必要模型欄位只有 `major_cn`、`minor_cn`、`total_cn` 與
`multiplicity_posteriors`；沒有 `beta_binomial_concentration` 或任何等價的 Beta
overdispersion 欄位。

若 MCMC 命令列仍出現 `eta_concentration` 或 `assignment_concentration`，那是
proposal／assignment prior 的數值設定，並不代表恢復了 Beta-Binomial concentration。

### 10.9 已執行與尚未執行

| 項目 | 目前狀態 | 證據 |
|---|---|---|
| Script compile | 已執行 | `python3 -m py_compile ...` |
| Validation contract tests | 已執行；3 個通過 | `tests/test_hcc1395_m3_pipeline_validation.py`（環境沒有 pytest，使用直接函式執行）；既有 M3 latent tests 3 個通過 |
| 10-site PS smoke | 已執行；10/10 `match_alt`、0 discordance | `/tmp/hcc1395_validation_batch10/stage_02_ps_audit.json` |
| ASCAT normalization smoke | 已執行；650 段、0 overlap；原 ASCAT `run.log` 有 2 次 `NAs introduced by coercion`，因此 gate 為 `review` | `/tmp/hcc1395_validation_batch10/stage_03_ascat_summary.json`；正式 warning 亦保留在 `output/.../stage_03_ascat_summary.json` |
| Full site/CNV preparation | 已執行；30,490 site、650 segments、`unmapped=85`、`CN=0=399` | 歷史 `input_validation_20260814` 已刪除；摘要與新版 QA 保留於 `input_validation_20260815_binomial/` |
| 30,490-site PS audit | 已完成；29,976 match_alt、20 discordant、14 bam_ps_missing、113 match_ref_only、367 vcf_ps_missing；discordance fraction=0.000667 | 歷史 audit JSON 已刪除；結果摘要保留於本文件 |
| canonical count rebuild | 已完成；30,490 bulk rows、304,900 HP rows、30,490 QC rows | canonical counts 目錄仍保留；舊 validation QA 已刪除 |
| 模型 likelihood input（Binomial counts、固定 multiplicity、major/minor CN） | **資料表已完成；Gate pass** | [likelihood_input.tsv.gz](output/longphase_clone/stage_06_likelihood_20260815_binomial/likelihood_input.tsv.gz)：30,490 rows、30,006 eligible、0 posterior-sum errors |
| M3 Binomial + fixed multiplicity + major/minor CN likelihood | **資料 adapter 已更新；I6 production-like rerun 已完成，但尚未收斂** | [`input_validation_20260815_binomial`](output/longphase_clone/input_validation_20260815_binomial/) 與 [`i6_automation_tmp/run_20260816_002_longchain_eta1`](output/longphase_clone/i6_automation_tmp/run_20260816_002_longchain_eta1/)；舊 Beta-Binomial M3 output 不代表目前模型 |
| M3 convergence/simulation/held-out | **已完成 I6 diagnostics；未通過 gate** | [`convergence.md`](convergence.md)；目前最大 label-invariant R-hat=24.983、最低 ESS/chain=3.1，Stage 7 為 `review` |

因此目前的資料流程結論是：**Stage 6 的 canonical likelihood data 已可重跑且通過 schema/QA；新的 joint sampler、convergence、simulation 與 held-out calibration 已完成一輪，但 R-hat/ESS 與 simulation gate 未通過，仍未達到重新解讀 M3 演化樹的條件。**

### 10.11 Stage 6 production-like posterior run（2026-08-14）

可重跑 runner：[`tools/run_stage6_production.py`](tools/run_stage6_production.py)。本輪使用新的 `likelihood_input.tsv.gz`、K=6、3 條獨立 chain、每條 8 iterations（burn-in 2），並在 MCMC 前以 `(chrom, PS)` block 分割 6,009 個 strict holdout sites。

結果摘要：

- R-hat：各 prevalence-rank 因短鏈／鏈內變異不足而出現 `NaN`；不能視為收斂。
- minimum ESS：2.7，遠低於 100。
- label-invariant assignment agreement：0.546–0.559；topology 每條 chain 有 2–3 個 retained topologies。
- strict held-out：3 條 chain 均完成，6,009/6,009 sites 可評估；平均 predictive log score `-54.1815 ± 0.0428`，90% coverage `83.31%`。
- simulation recovery：assignment fraction of oracle `0.500`、prevalence RMSE `0.2302`、topology F1 `0.4954`，未通過 recovery gate。

因此 Stage 7 現在不是「沒有執行」，而是 **artifact 已齊全但 convergence/recovery gate 為 review**。2026-08-14 的歷史 production raw outputs 已刪除；目前完整結果以 [`convergence.md`](convergence.md) 與 [`i6_automation_tmp/run_20260816_002_longchain_eta1`](output/longphase_clone/i6_automation_tmp/run_20260816_002_longchain_eta1) 為準。

### 10.12 收斂導向的輸出保留

目前正式保留的不是所有歷史 output，而是能重建 canonical input、I5 PASS、I6 FAIL 與
下一輪 CN/LOH 修正的最小集合。保留／刪除逐項執行清單見
[`convergence_cleanup_20260816.md`](convergence_cleanup_20260816.md)；截至 2026-08-16
已刪除 179 個舊 pilot、重複 seed、舊 candidate tree 與早期描述性圖表，避免誤把歷史結果
當成目前模型輸入。

### 10.10 Heavy-I/O detached runner

為避免 273 GB tagged BAM 的長時間讀取綁在 agent session，已新增：

```text
tools/run_hcc1395_m3_input_validation.sh
```

預設使用 8 個 worker、50 Mb batched pileup window，並把 stdout/stderr、PID、參數、stage status 寫入：

```text
output/longphase_clone/input_validation_20260814/run_hcc1395_m3_input_validation.log
output/longphase_clone/input_validation_20260814/run_status.tsv
output/longphase_clone/input_validation_20260814/run_parameters.tsv
```

從 repo root 啟動 detached 全流程：

```bash
tools/run_hcc1395_m3_input_validation.sh \
  --mode all --threads 8 --audit-window-size 50000000 --detach
```

可重複使用的模式：

```bash
tools/run_hcc1395_m3_input_validation.sh --mode counts --threads 8 --detach
tools/run_hcc1395_m3_input_validation.sh --mode audit --threads 8 --detach
tools/run_hcc1395_m3_input_validation.sh --mode all --threads 8 --rebuild-counts --detach
```

`--detach` 優先使用持久 `tmux` session `hcc1395_input_validation`，因此不依賴 agent session；若沒有 tmux 才 fallback 到 `nohup`。同一 output directory 使用 `flock` 防止兩個重 I/O job 同時寫檔。若 count tables 已存在且未指定 `--rebuild-counts`，會先驗證並重用；runner 負責 Gate 1–5 的重 I/O 產物，不會自動重跑 MCMC。模型輸入表請以 `tools/build_hcc1395_likelihood_input.py` 從已驗證的 counts/CN tables 建立；Stage 7 則須等 sampler 與 calibration artifact 都完成才可通過。
