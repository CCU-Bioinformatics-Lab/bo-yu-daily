# 同一腫瘤同時有 bulk long read 與 single-cell DNA 的公開資料（2026-10-26）

問題：要用 single-cell 真值樹驗證「只從 bulk long read 推出的樹」，需要同一個腫瘤（或同一批細胞）同時有 bulk ONT／PacBio 和 single-cell DNA。有哪些公開資料？

範圍：以「資料集」為主。前一次調查（`../patient_sc_longread_2026/`，2026-10-15～16）以論文為主，結論是只有 B04（JGA 受控）與 B03（MTA）同時有 ONT 與 single-cell，而且都沒有可評分的完整真值樹。本次補查細胞株與 2026 年的新資料。

標記：〔repo〕＝repository 頁面實際看到；〔論文〕；〔推論〕。沒有下載任何資料檔。

## 1. 結論

- **最好的候選是 GIAB HG008（胰臟癌細胞株，公開）。** 〔repo〕
  - **本機共用副本（2026-11-04 核對）：** `/big8_disk/yungjen114/data/HG008/`，只有 bulk long read（ONT、ONT-UL、PacBio）與 NIST benchmark；單細胞和 8 株 clone 沒下載。直接引用，不要重複下載。細節見 `docs/tumor_sample.md`「HG008」。
  - bulk：ONT standard 與 ultra-long（UCSC、Northeastern）、PacBio Revio（約 80×）、多種短讀。
  - single-cell：119 個 BioSkryb ResolveDNA（PTA 擴增）單細胞，用 UG100 重新定序到每細胞 coverage 中位 23×（12–48×），每個細胞都有 CRAM 與 VCF。所以是 **SNV 層級**的單細胞資料，不只是 CNV。
  - 單細胞和主要 bulk 資料來自**同一個 passage p23 批次**（Batch ID 0823p23）。
  - 120 個細胞的低深度 CNV 分析（Ginkgo）初步看到「8 個可重複的 CNV 型態」。
  - NIST 另外有 8 株從 HG008-T 單細胞衍生的 clonal line，位置在 `NIST/HG008-T_clones/`，每株有 PacBio Revio 與現成的 somatic 分析（見第 4 節）。
- **第二候選是 GIAB HG009（胰臟癌肝轉移細胞株，公開，2026 年才上傳）。** 〔repo〕
  - 10 株單細胞衍生的 clone（`HG009-T_clones/20250918p14/`：1C3、1D5、1E4、2B5、2E7、3C4、3C9、3F2、4F10、4G9）。抽查 3C9：有 PacBio Revio、NovaSeq X、karyotyping。
  - bulk（p16）有 PacBio Revio 與 NovaSeq X。本次沒看到 ONT。
  - clone 本身就是單細胞的後代，所以 clone 之間的關係可以當作 lineage 參考，類似 B01 的小鼠黑色素瘤 subline 設計。〔推論〕
- **COLO829 有公開的單細胞 CNV，但沒有樹，也不是同一批細胞。** 10x scCNV，1,475 個細胞，至少 4 個 subclone（A 653、B 117、C 43、D 560 個細胞），GEO GSE151409。論文只有 CN heatmap 和示意模型，沒有正式的 phylogeny。ONT bulk 是其他實驗室的培養批次（本機也有 `ONT_R10`、`ONT_PAO`）。〔論文〕
- **沒有找到公開的「病人腫瘤 + bulk long read + single-cell DNA」資料。** 已知的 B04 是 JGA 受控存取，B03 要走 MTA。SPLONGGET（B-ALL 單細胞 nanopore 全基因組）只有 London Calling 2025 的初步報告，沒有公開資料。〔repo＋論文〕

## 2. 候選比較

| 資料 | 腫瘤 | bulk long read | single-cell／clone | 同一批細胞 | 存取 | 樹 |
|---|---|---|---|---|---|---|
| **HG008** | PDAC 細胞株 | ONT std＋UL、PacBio Revio 80× | 119 個 PTA 單細胞，中位 23×，CRAM＋VCF；8 株 clonal line（短讀，位置待查） | ✅ p23 | 公開（NIST data use terms） | 無；有 8 個 CNV 型態 |
| **HG009** | PDAC 肝轉移細胞株 | PacBio Revio（bulk p16） | 10 株單細胞衍生 clone，至少 3C9 有 Revio＋NovaSeq X | 待確認 passage 對應 | 公開 | 無（clone 關係可自建） |
| COLO829 | 黑色素瘤細胞株 | ONT（其他批次） | 10x scCNV 1,475 個細胞，4 個 subclone | ❌ | 公開（GEO GSE151409） | 無 |
| B04 Sakamoto 2022 | 肺癌病人 | ONT WGS | 10x scDNA，2 例 | ✅ 同病人 | JGA 受控 | 無（bulk 推的樹） |
| B03 Funnell 2022 | PDX | ONT（5 個 genome） | DLP+ scWGS | ✅ | MTA | DLP+ CN 樹 |
| B01 小鼠黑色素瘤 | 小鼠細胞株 | ONT（每個 subline） | 23 株單細胞衍生 subline | ✅ | 公開 | ScisTree 推論樹 |
| SPLONGGET | B-ALL 病人 | 單細胞 nanopore | 同上 | ✅ | 未公開 | 初步報告 |

## 3. HG008 的用法建議〔推論〕

1. 用 119 個單細胞的 VCF 和 CRAM 建單細胞參考樹。可以用 SNV（例如 SCITE、ScisTree），也可以用 CNV。要處理 PTA 的擴增錯誤與 allele dropout。
2. 用 bulk ONT（UCSC／Northeastern，同一個 p23 批次）跑 longphase 與 PhyClone + HP 特徵，只從 bulk 推樹。
3. 把兩棵樹轉成共同 SNV 的關係（same／ancestor／descendant／branch）再比較。單細胞和 bulk 的節點不同，不能直接算 tree edit distance。
4. 8 株 clonal line 上傳後，可以當作第二個獨立參考。

要先確認的事：
- 每個 ONT／PacBio 資料夾的 passage 與 batch（README 或 Cancer GIAB Data Manifest）。
- 單細胞 CRAM／VCF 的 S3 位置（`giab-aws_HG008-bioskryb-ultima_data_manifest.tsv`）。
- 細胞株在培養中的異質性夠不夠：8 個 CNV 型態是正面訊號，但 subclone 的 SNV 差異可能很少。

## 4. HG008 確認結果（同日，只讀目錄與 README，沒有下載大檔）

### 4.1 bulk long read 的 passage 與批次〔repo〕

| 資料夾 | 技術 | 樣本 | batch／passage | coverage |
|---|---|---|---|---|
| `Liss_lab/UCSC_ONT_20231003/` | ONT std R10.4.1，dorado 0.3.4 sup4.2.0，5mC／5hmC | HG008-T | **0823p23** | 63× |
| `Liss_lab/UCSC_ONT-UL_20231207/` | ONT ultra-long R10.4.1，dorado 0.4.3 | HG008-T | **0823p23** | 54× |
| `Liss_lab/Northeastern-ONT-UL-20241216/` | ONT ultra-long R10.4.1，dorado 0.8.1 | HG008-T | **0823p23** | 54× |
| `Liss_lab/Northeastern_ONT-std_20240422/` | ONT std，dorado 0.5.3 | **normal**（十二指腸、胰臟） | — | — |
| `Liss_lab/PacBio_Revio_20240125/` | PacBio HiFi Revio | HG008-T | **0823p23** | 116× |
| `Liss_lab/BCM_Revio_20240313/` | PacBio HiFi Revio | HG008-T | **0823p23** | 106× |
| `Liss_lab/other_passages/BCM_ONT-std_HG008T-p2_20260313/` | ONT std，dorado sup v4.3.0；已附 longphase haplotag CRAM | HG008-T | **passage 2**（早期） | 檔名標示 |

- 主要的 tumor ONT（3 份）和 PacBio（2 份）都是 0823p23，和 119 個單細胞同一批。
- 有 matched normal 的 ONT（Northeastern），可以做 germline phasing。
- 另外有 passage 2 的 ONT，可以看早期與晚期 passage 的差異。

### 4.2 單細胞 CRAM／VCF 的位置與大小〔repo〕

manifest：`Liss_lab/HG008-T_bioskryb-libraries-UG100/giab-aws_HG008-bioskryb-ultima_data_manifest.tsv`。

| 類型 | 檔案數 | 總大小 | 平均 |
|---|---:|---:|---:|
| CRAM（alignment） | 119 | 4,798 GB | 40.3 GB |
| VCF（variants） | 119 | 64.3 GB | 0.54 GB |

- 位置：`s3://giab-aws/WGS/Bioskryb/2024/HG008-T_bioskryb-libraries-UG100/`，manifest 也有 https URL。
- **只用 VCF 就能先建單細胞 SNV 矩陣（64 GB）**，不必先下載 4.8 TB 的 CRAM。CRAM 留到需要逐細胞查特定位點時再取部分區域。〔推論〕

### 4.3 8 株 clonal line 的位置〔repo〕

位置：`NIST/HG008-T_clones/`。clone 在 passage 14 或 19 時由單細胞分離，再擴增數代後定序。

| 分離批次 | clone | 定序 |
|---|---|---|
| `20240718p14/` | 2D6、2E6、3E4 | Illumina、PacBio Revio、karyotype；3E4 另有 PacBio CiFi |
| `20240805p19/` | SC14、SC24、SC28、SC6、SC9 | Illumina、PacBio Revio、karyotype；SC14、SC24 另有 PacBio CiFi |

- 抽查 SC14：PacBio HiFi 59×（median diploid），已用 HiPhase phasing。
- **每株都有現成的 tumor vs normal 分析**（`analysis/GRCh38/…/HG008-T-<clone>_vs_HG008-N-P/`）：DeepSomatic somatic SNV、PURPLE CN segment 與 purity、CNVkit、Severus somatic SV、甲基化。
- 所以只要下載 8 個 DeepSomatic VCF 和 PURPLE segment，就能用 clone 之間共有／私有的 SNV 建 clone 關係樹。〔推論〕
- clone 在 p14／p19 分離，bulk 是 p23。clone 代表的是 p14–p19 時培養中存在的細胞群；clone 擴增期間新增的突變，只會出現在該 clone，不會出現在 bulk。比對時要扣除這些「擴增後」突變。〔推論〕

### 4.4 對驗證設計的意義〔推論〕

可以建出兩個彼此獨立的參考：

1. **clone 參考樹：** 8 株 clone 的 somatic SNV／CN，資料小、已處理好，最容易先做。
2. **單細胞參考樹：** 119 個 PTA 單細胞的 VCF，和 bulk 同一批，但要處理擴增錯誤與 allele dropout。

再用 p23 的 bulk ONT（UCSC 63×）跑 longphase + PhyClone（加或不加 HP 特徵），比較推出的 clone 結構與兩個參考是否一致。

## 5. 來源

- HG008 目錄：https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG008/Liss_lab/
  - `Bioskryb_ResolveDNA_20230914/README_Bioskryb.md`（120 cells、Batch 0823p23、p23、Ginkgo CNV、「8 pretty well defined」CNV 型態）
  - `HG008-T_bioskryb-libraries-UG100/README_Bioskryb-Ultima.md`（119/120 通過、CRAM＋VCF 在 giab-aws S3）、`NIST_Bioskryb_QC_measures.csv`（mean coverage 12.11–47.61，中位 23.11）
- HG009 目錄：https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG009/NIST/
- NIST GIAB cancer 頁面：https://www.nist.gov/node/1828591（「8 cell lines derived from single cell clones of the NIST HG008-T cell line」）
- COLO829 scCNV：https://pmc.ncbi.nlm.nih.gov/articles/PMC7316972/（GSE151409）
- Arborist（排除：只用短讀 MPNST 病人資料）：https://www.biorxiv.org/content/10.64898/2026.02.26.707773v1.full
- SPLONGGET：https://nanoporetech.com/zh/resource-centre/case-study-unravelling-tumour-biology-with-single-cell-oxford-nanopore-sequencing
- 前一次調查：`../patient_sc_longread_2026/INTERSECTION_SUMMARY.md`、`ONT_DATA_AVAILABILITY.md`
