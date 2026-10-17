# 資料輸入盤點：tagged BAM 與 SNV 定序資訊

> 盤點日期：2026-10-15。範圍：`/bip8_disk/boyu114/` 內，可給 `plan.md`（PhyClone + longphase-s HP 特徵）使用的 tagged BAM，以及已萃取出來的 SNV 計數表。
> 以下路徑若沒有特別寫，都是相對於 `/bip8_disk/boyu114/`。
> 證據來源：BAM 的 `@PG` header、`samtools view` 抽查、各目錄的 `RECORD.md` / `run_metadata.json` / 腳本原始碼。

---

## 1. Tagged BAM（longphase-s `somatic_haplotag` 輸出）

共同點：

- tumor 輸入都是**完整的 HCC1395**：`/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam`。這個 `.bam` 現在已經不存在，同目錄只剩 `HCC1395.cram` / `HCC1395BL.cram`。
- **不是 `tX_nY` subsample**，所以只有單一 sample。`tX_nY` 都還沒有做過 somatic_haplotag。
- phased normal VCF：`/big8_disk/liaoyoyo2001/data/vcf/HCC1395BL_methyl_phase.vcf.gz`（chr16 A/B 測試例外，見下表）。
- 參數：`-q 20 --tagSupplementary`，reference 為 `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`。
- 抽查 chr1:20,000,000–20,050,000 的前 3,000 條 read（old tagging 全基因組版），有 `HP:Z:1`（522）、`HP:Z:1-1`（12）、`HP:Z:2`（7）以及 `PS:i:`（541）。**確認 read 上有 `PS` tag**，可以用來做 `plan.md` §4.5.3 的 read 層級 PS 篩選。

| 路徑 | 範圍 | tagging 版本 | `--tumor-snv-file` | 大小 | 索引 |
|---|---|---|---|---|---|
| `longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam` | 全基因組 | old | ClairS PASS：`/big8_disk/liaoyoyo2001/data/vcf/ClairS_ss/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/pileup/HCC1395_methyl_PASS.vcf`（203,611 筆） | 283 GB | `.bai` |
| `longphase-s-boyu/output/hcc1395_new_split_tagging_bundle/hcc1395_new_split_tagging.bam` | 全基因組 | new，`--enable-two-site-split` | `/bip8_disk/boyu114/intersubmod/output/annotated_with_PS.vcf.gz` | 292 GB | `.bai` |
| `longphase-s-boyu/.worktrees/longphase-s-origin-new-split/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam` | 全基因組 | old（worktree 重跑） | ClairS PASS | 292 GB | `.bai` |
| `longphase-s-boyu/.worktrees/longphase-s-origin-new-split/output/hcc1395_chr1_split_enabled/hcc1395_chr1_split_enabled.bam` | chr1 | new split | ClairS PASS | 25 GB | **沒有 `.bai`** |
| `longphase-s-boyu/.worktrees/longphase-s-origin-new-split/output/hcc1395_new_split_tagging_annotated_ps_chr1/hcc1395_new_split_tagging_annotated_ps_chr1.bam` | chr1 | new split | `longphase-s-boyu/output/tumor_phase_experiment_origin/annotated_with_PS.chr1.vcf.gz` | 25 GB | `.bai` |
| `longphase-s-boyu/output/chr16_34600401_phase_cleanup_ab/haplotag_on/chr16_34600401_cleanup_on.bam` | chr16:34,550,000–34,850,000 | phase cleanup on | ClairS PASS；normal VCF 用 `phase_on/HCC1395BL_chr16_cleanup_on.vcf.gz`，`--disableFilter` | 79 MB | `.bai` |
| `longphase-s-boyu/output/chr16_34600401_phase_cleanup_ab/haplotag_off/chr16_34600401_cleanup_off.bam` | 同上 | phase cleanup off | 同上（`phase_off/`） | 79 MB | `.bai` |

每個目錄都有一份 `*_purity.out`（longphase-s purity 估計），可以和 ASCAT purity 比較。

**決定（2026-10-15）：C0 前處理用 old tagging**，檔案是 `longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam`（第一列）。worktree 裡同指令重跑的版本大小不同（292 GB vs 283 GB），不使用。第 3 節的 co-read 計數表也是用這個 BAM 產生的，兩者可以互相對照。longphase-s purity 估計為 0.992164（`hcc1395_old_tagging_purity.out`）。

### 相關 VCF

| 路徑 | 內容 |
|---|---|
| `/big8_disk/liaoyoyo2001/data/vcf/HCC1395BL_methyl_phase.vcf.gz` | phased normal SNP VCF（含 PS），上述 BAM 共用 |
| `longphase-s-boyu/output/whole_bam_phase_rerun_ssrs/HCC1395BL_ssrs_rerun.vcf.gz` | normal 全基因組 phasing 重跑版（76 MB） |
| `/big8_disk/liaoyoyo2001/InterSubMod/data/vcf/HCC1395/pileup/filtered_snv_tp.vcf.gz` | ClairS PASS ∩ SEQC2 truth 的 TP，30,490 個 SNV（chr1–22） |
| `/bip8_disk/boyu114/intersubmod/output/annotated_with_PS.vcf.gz` | new-split tagging 用的 somatic SNV（附 PS） |
| `longphase-s-boyu/output/tumor_phase_experiment_origin/` | chr1 的 tumor phasing 實驗 VCF |

---

## 2. PhyClone 輸入（沒有 HP 欄位，即 baseline）：`phyclone/hcc1395_input/`

製作紀錄：`phyclone/hcc1395_input/RECORD.md`（2026-10-07）。

| 檔案 | 內容 |
|---|---|
| `output/hcc1395_phyclone_input.tsv` | PhyClone 主輸入，30,368 個 SNV × 1 sample（`HCC1395`）。`ref/alt` 從 CRAM 重新 pileup（`bcftools mpileup -q 20 -Q 10`）；`major/minor` 來自 ASCAT；`normal_cn=2`；`tumour_content=0.99`（ASCAT 文獻值） |
| `output/hcc1395_phyclone_input_noCN.tsv` | 同上但沒有 CN，30,490 個 SNV |
| `output/hcc1395_site_counts_qc.tsv` | tumor / normal 的 ref、alt、other 計數與 VAF |
| `output/hcc1395_dropped_sites.tsv` | 被移除的 122 個位點及原因（不在 ASCAT segment 內、`major_cn=0`） |
| `pyclone_vi/hcc1395_clusters.tsv` | PyClone-VI 原始 5 群 |
| `pyclone_vi/hcc1395_clusters_merged.tsv` / `_merged4.tsv` | 合併後 3 群 / 4 群 |
| `phyclone_run5/` | 5 群：MAP = consensus，線性 `0→1→2→4→3` |
| `phyclone_run3/` | 3 群：兩種 topology 各約 50% |
| `phyclone_run4/` | 4 群：MAP `(((2,3)1)0)root`，`num_outliers=0` |
| `cn_subset/major1`、`cn_subset/cn21_22` | 只取特定 CN 狀態位點的重新分群結果 |
| `scripts/01–06` | pileup → 建表 → 加 ASCAT CN → 合併 cluster → CN 子集 |

注意：

- 這些 run 都沒有加 `--outlier-prob`，符合 `plan.md` §0.1「不使用 outlier」的設定，可以直接當 ablation 的 baseline。
- 單一 sample，所以樹形大多由 PyClone-VI 的 cluster CCF 和 sum rule 決定（見 `RECORD.md`「PhyClone 正式跑」各節）。

---

## 3. SNV pair co-read 計數：`longphase-s-boyu/output/hcc1395_cnv_multisomatic_altref_observation/`

設定（`run_metadata.json`）：tumor BAM 為 `longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam`；SNV 為 `filtered_snv_tp.vcf.gz`（30,490 個）；PS 來自 `annotated_with_PS.vcf.gz`；CNV 區域為 `/big8_disk/data/HCC1395/SEQC2/CNV/ngs_benchmark_cnv_{gain,loss}_cn.bed`；`min_mapq=20`、`min_baseq=10`。產生腳本：`longphase-s-boyu/tools/run_cnv_ps_multisomatic_tree_statistics.py`。

| 檔案 | 列數 | 內容 |
|---|---|---|
| `site_pair_coread_counts.tsv` | 20,470 對 | `interval_id, cnv_type, chrom, PS, site_a, site_b, ALT_ALT, ALT_REF, REF_ALT, REF_REF, callable_pair_reads` |
| `read_multisomatic_alleles.tsv` | 約 201 萬 | 每條 read 在每個位點的 allele、base quality、MAPQ |
| `read_multisomatic_patterns.tsv` | 約 27 萬 | 每條 read 跨多個位點的 allele pattern |
| `cnv_tp_somatic_sites.tsv` | 21,371 | CNV 區域內的 TP 位點及所屬 PS |
| `cnv_ps_block_tree_states.tsv`、`cnv_ps_pattern_support.tsv`、`cnv_ps_tree_state_summary.tsv` 等 | — | 每個 CNV-PS block 推出的 topology 狀態 |

**和 `plan.md` §4.5 F5 的差異（不能直接拿來用）：**

1. **只涵蓋 CNV 區域**：20,294 對在 gain（CN 3–5），169 對在 loss，7 對在 gain;loss。這是 plan 第一版排除的 `C_h ≥ 2` 情況；plan 需要的 `C_h = 1` 區域沒有算。
2. **沒有依 read 的 HP / PS tag 篩選**：腳本用 VCF 的 PS 把位點分組，再用 `samtools view -M -L` 取出 read，沒有檢查 read 上的 `HP` 或 `PS` tag，兩條 haplotype 的 read 混在一起。例如第一列 `ALT_ALT=0, ALT_REF=23, REF_ALT=13`，比較像兩個 SNV 分別在不同的 haplotype 上。
3. 沒有限制只用 primary alignment（`plan.md` §4.5.3 條件 2）。

可沿用的部分：read 取法與 allele 判定可以當作 C0 F5 計數程式的起點，再補上 HP / PS 篩選、primary alignment 和 `C_h = 1` 條件。

---

## 4. 其他（和 plan 關係較小）

- `InterSubMod/output/`、`longphase-s-boyu/output/cnv_single_site_intersubmod_*`、`hp3_*`：以單一 PS 或單一位點為單位的 read label、methylation、heatmap 結果，主要是 tagging 驗證與 methylation 分析。
- `longphase-s-boyu/output/hp3_germline_support_comparison_old_tagging/read_level.tsv`、`hp3_conflict_vs_strict_stats_old_tagging/hp3_rescue_failure_read_level.tsv`：HP3 read 的 read-level 統計，可以用來評估 `plan.md` §6 第 5 點（HP3 比例）。

---

## 5. 對 `plan.md` 的影響與下一步

- C0 前處理的輸入：old tagging BAM（第 1 節第一列）+ `phyclone/hcc1395_input/output/hcc1395_phyclone_input.tsv` 的位點 + ASCAT CN。
- F5 要重新計數；第 3 節的表只能當參考。
- 多 purity sample 的評估目前做不了，需要先對 `tX_nY` subsample 跑 somatic_haplotag。
