# docs 索引：資料路徑與盤點

本目錄放**資料在哪裡、長什麼樣**的盤點。設計文件不在這裡：HP 特徵設計在 `/bip8_disk/boyu114/haploclone/rust/docs/plan.md`，研究入口在 `research/INDEX.md`。

盤點有日期。路徑與檔案可能已經改變，用之前先 `ls` 確認。

**大型公開資料先查這裡有沒有共用副本，有就直接引用，不要自己下載**，避免多人重複下載把 server 硬碟用完。

## 檔案

| 檔案 | 內容 | 盤點日期 |
|---|---|---|
| [tumor_sample.md](tumor_sample.md) | 六株 ONT 細胞株的原始與 subsample CRAM 路徑、`tX_nY` 純度標籤、HCC1395 實測 purity；HG008 共用副本；PhyClone benchmark、SMC-Het 的結構（本機已刪） | 2026-10-15 盤點，10-25、11-04 更新 |
| [data_input.md](data_input.md) | HCC1395 tagged BAM／CRAM（longphase-s `somatic_haplotag`）、相關 VCF、baseline 樹重建輸入表、SNV pair co-read 計數表 | 2026-10-15 盤點，11-02、11-03 更新刪除與轉檔 |

## 快速查詢

| 要找什麼 | 去哪裡 | 一句話答案 |
|---|---|---|
| HCC1395 tumor／normal CRAM | `tumor_sample.md`「HCC1395」 | 三組：`ONT/`（香港大學）、`ONT_Dorado`（CASTLE）、`ONT_5khz_simplex_5mCG_5hmCG/`。前兩組是不同實驗室的細胞培養，不要混用 |
| subsample 路徑與檔名規則 | `tumor_sample.md`「六種細胞株」 | `<subsample path>/<tX_nY>/<line>_<tX_nY>.cram`；COLO829 PAO `t33_n00` 例外 |
| `tX_nY` 的百分比是什麼 | `tumor_sample.md`「純度標籤口徑」 | nominal tumor DNA 比例 X／(X+Y)，不是 cellular purity；`t00_n25` 是純 normal |
| HCC1395 實測 cellular purity | `tumor_sample.md`「HCC1395」實測表 | `ONT/`：t10 0.153、t20 0.321、t30 0.513、t40 0.737、t50 1.000（定義） |
| 讀 CRAM 要用的 reference | `tumor_sample.md`「格式更新」 | `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`，用 `-T` 指定 |
| 哪些 `.bam` symlink 已失效 | `tumor_sample.md`「格式更新」 | 所有原始 `.bam` 已轉 CRAM 並刪除；對應 CRAM 在 `/big8_disk/Google_somatic_data/bams/<line>/` |
| 資料來源（CASTLE、SRA 編號） | `tumor_sample.md`「資料來源」 | H1437、H2009、HCC1937、HCC1954、HCC1395 `ONT_Dorado` 來自 CASTLE Release 1；HCC1395 `ONT/` 是 SRR25005626 |
| HCC1395 HP-tagged 全基因組檔 | `data_input.md` §1 | 決定用 old tagging：`longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam`（283 GB） |
| new split tagged BAM | `data_input.md` §1「已刪除」 | 2026-11-02 全部刪除；要重做須從 `HCC1395.cram` 重跑 `somatic_haplotag` |
| phased normal VCF、somatic SNV VCF | `data_input.md` §1「相關 VCF」 | normal：`HCC1395BL_methyl_phase.vcf.gz`；TP SNV：`filtered_snv_tp.vcf.gz`（30,490 個） |
| baseline 樹重建輸入表（無 HP） | `data_input.md` §2 | `/bip8_disk/boyu114/phyclone/hcc1395_input/output/hcc1395_phyclone_input.tsv`，30,368 SNV × 1 sample |
| SNV pair co-read 計數 | `data_input.md` §3 | 有 20,470 對，但只涵蓋 CNV 區域、沒依 read 的 HP／PS 篩選，不能直接用 |
| `tX_nY` subsample 有沒有 HP tag | `data_input.md` §1、§5 | 沒有。subsample 都還沒跑 `somatic_haplotag` |
| HG008 在哪、有什麼 | `tumor_sample.md`「HG008」 | `/big8_disk/yungjen114/data/HG008/`（共用，只讀）：ONT、ONT-UL、PacBio 的 tumor 與兩個 normal，NIST somatic SNV 與 SV／CNV draft benchmark，ONT purity 系列 subsample 加 ClairS-TO 結果 |
| HG008 有沒有單細胞 | `tumor_sample.md`「HG008」 | 沒有。PTA 單細胞與 8 株 clone 沒下載；需要時先和 yungjen114 確認 |
| 讀 HG008 BAM 用的 reference | `tumor_sample.md`「HG008」 | 用它自帶的 `reference/GRCh38-GIABv3/`，不能換成實驗室常用的 GRCh38 no-alt |
| PhyClone benchmark、SMC-Het | `tumor_sample.md` 最後兩節 | 本機已刪除；都是 short read，依 2026-10-21 會議不當輸入或真值；只留結構說明 |

## 不在本目錄的資料說明

- 小檔 benchmark（SEQC2 HCC1395 真值與 CNV、GIAB HG002、T2T Q100、COLO829、CASTLE Wakhan）：`/big8_disk/boyu114/benchmark_data/README.md`。同目錄另有 `PCAWG/`、`TRACERx/`，README 表內沒有列。
- GIAB HG008 的文獻與資料集調查（含公開的 119 個 PTA 單細胞）：`research/literature/surveys/sc_longread_datasets_2026-10-26/README.md`。本機副本見上表「HG008」。
- HCC1395 ASCAT CN：`lab_report/2026-10-30_ascat_hcc1395_5khz/`。
