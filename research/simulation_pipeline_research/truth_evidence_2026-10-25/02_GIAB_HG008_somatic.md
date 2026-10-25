# GIAB（HG008 somatic、mosaic、stratifications、phasing）作為 HP-aware 模擬的真實基準

> 調查日期：2026-10-25。來源以 NIST 官網、GIAB FTP 目錄與 README、論文為主。
> 證據等級：〔官方文件〕＝NIST 網頁／FTP README／目錄清單；〔論文〕＝期刊或 preprint；〔推論〕＝本文根據前兩者的推論。
> 本文只列下載清單，沒有下載大檔。表中檔案大小取自 FTP 目錄清單，或用 HTTP HEAD 取得。
> 唯一例外是 HG008 small variant `tumorvariants.vcf.gz`（279 KB），本文用 streaming 讀它，統計 TAC/TCN 分布（見 §1.5）。

---

## 0. 結論

1. **HG008 是目前唯一公開、broad consent 的 GIAB tumor–normal 組。** HG008-T 是 PDAC 細胞株，HG008-N-D／HG008-N-P 是十二指腸與胰臟正常組織。資料論文已刊於 Sci Data 2025（DOI 10.1038/s41597-025-05438-2）。assembly 與 benchmark 的論文是 2026-05 bioRxiv preprint（DOI 10.64898/2026.05.01.722316）。〔論文〕〔官方文件〕
2. **benchmark 全部仍是 draft，沒有 v1.0。** 最新版是 small variant **V0.4**（2026-10-06）與 SV+CNV **V0.6**（2026-10-06）。兩者都以 clonal／truncal 變異為主。〔官方文件〕
3. **HG008 有 haplotype-resolved 真值。** HG008-N v6.3 有 44 條 T2T scaffold。HG008-T（tumor MRCA）v3.x 的 35 條染色體都有 T2T scaffold。HG008 沒有父母資料，所以 haplotype 是 hap1／hap2，**不是 MAT／PAT**。〔論文〕〔推論〕
4. **CNV benchmark 有 haplotype-specific CN。** GRCh38 版給 `CN_HAP1`/`CN_HAP2`。native 版給每個 haplotype 的 `CN_this_hap`。small variant 的每個 SNV 帶 `TAC/TCN`，也就是 assembly 推得的 multiplicity／total CN。這是「HP 拆分」與「CN timing」最直接的真實證據。〔官方文件〕〔推論〕
5. **HG008-T 確實有 subclone 與 passage 差異。** 證據包括 WGD 比例隨 passage 上升（p21 9/40、p53 28/40、p101 20/20），以及 dGH 看到 1–4 個細胞的 subclonal 變異。preprint 也說，subclonal SV 在後代 passage 消失，主因是大片 deletion。但 GIAB **沒有發布 subclone 樹或 CCF 真值**。〔論文〕
6. **低 purity 與低 CCF clone 沒有 GIAB 真值。** HG008-T 是細胞株，接近 100% tumor，也沒有官方 purity titration（未查到）。HG002 mosaic benchmark 只有 85 個 SNV，VAF 約 5–30%，而且很可能來自細胞培養，**不是 clone tree**。〔官方文件〕〔推論〕
7. **評估工具已有共識，但 somatic 的部分還不足。** small variant 用 hap.py＋vcfeval（GA4GH，Krusche 2019），HG008 README 推薦 aardvark。SV 用 truvari ≥ v5，參數 `--sizemax -1 --passonly --pick multi`。GA4GH 沒有 somatic 專用的規範（未查到）。README 也說明：CNV 比對 best practice「尚未建立」，現有工具「不考慮 VAF」。〔官方文件〕〔論文〕
8. **模擬時要套用 GIAB v3.6 stratifications。** 用 `GRCh38_notinalldifficultregions.bed.gz` 限定事件位置。用 `GRCh38_alllowmapandsegdupregions.bed.gz` 標註或排除困難區。〔官方文件〕

---

## 1. 資源總表

| 資源 | 版本／狀態 | 內容重點 | URL | 大小 | 等級 |
|---|---|---|---|---|---|
| HG008 data paper | Sci Data 12:1195（2025-07-16），有 correction 12:1385 | 17 種技術，含 coverage | https://doi.org/10.1038/s41597-025-05438-2 | – | 〔論文〕 |
| HG008 assembly/benchmark preprint | bioRxiv 2026-05 | "A complete human pancreatic cancer genome" | https://doi.org/10.64898/2026.05.01.722316 | – | 〔論文〕 |
| HG008 FTP 根目錄 | 持續更新 | Liss_lab（0823p23 batch）、NIST（bulk passages、clones） | https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG008/ | – | 〔官方文件〕 |
| small variant benchmark | **V0.4 draft**（2026-10-06） | 18,871 個 truncal SNV/indel（GRCh38），phased，帶 TAC/TCN | …/Liss_lab/analysis/NIST_HG008-T_somatic-smvar_DraftBenchmark_V0.4-20261006/ | GRCh38 VCF 279 KB；BED 885 KB | 〔官方文件〕 |
| SV+CNV benchmark | **V0.6 draft**（2026-10-06） | 211 個 PASS SV（GRCh38），含 subclonal flag；CNV 帶 CN_HAP1/2 | …/Liss_lab/analysis/NIST_HG008-T_somatic-stvar-CNV_DraftBenchmark_V0.6-20261006/ | 每檔 < 220 KB | 〔官方文件〕 |
| HG008-N assembly | v6.3 | 正常 diploid，hap1/hap2 | https://nist-giab.s3.us-east-1.amazonaws.com/giab_tumor-normal/analysis/HG008/NIST_asm_dev/HG008N_v6.3/HG008N_v6.3.fasta.gz | 1.50 GB（HEAD） | 〔官方文件〕 |
| HG008-T assembly | v3.2 公開；V0.4 用 v3.4 | tumor MRCA，hap1/hap2 | https://nist-giab.s3.us-east-1.amazonaws.com/giab_tumor-normal/analysis/HG008/NIST_asm_dev/HG008T_v3.2/HG008T_v3.2.fasta.gz | 1.25 GB（HEAD）；v3.4 同格式路徑回 403（未查到公開位置） | 〔官方文件〕 |
| HG002 mosaic SNV | v1.1（mosaic_v1.10） | 85 個 SNV，VAF > 5%；BED 2.45 Gb | https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/mosaic_v1.10/GRCh38/SNV/ | VCF 16 KB；BED 20 MB | 〔官方文件〕〔論文〕 |
| HG002 Q100 benchmark | v5.0q draft | 以 T2T-HG002 Q100 v1.1 assembly 為基礎；GT phased | https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/v5.0q/ | smvar VCF 40 MB；stvar VCF 46 MB | 〔官方文件〕 |
| HG002 v4.2.1 | 對 HG002 已被 v5.0q 取代 | mapping-based；GT 多數 unphased | …/HG002_NA24385_son/NISTv4.2.1/GRCh38/ | VCF 149 MB | 〔官方文件〕 |
| Stratifications | **v3.6**（2025-04） | difficult、segdup、low mappability 等 | https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/genome-stratifications/v3.6/ | GRCh38 tar.gz 1.3 GB；單檔數 KB–34 MB | 〔官方文件〕〔論文〕 |

---

## 2. 各問題詳細

### Q1. HG008 癌症／somatic 計畫

#### 1.1 發表狀態
- **資料論文**：McDaniel J.H., Patel V., …, Zook J.M.《Development and extensive sequencing of a broadly-consented Genome in a Bottle matched tumor-normal pair》，*Sci Data* 12:1195（2025-07-16），DOI 10.1038/s41597-025-05438-2。correction 是 *Sci Data* 12:1385（2025-08-08）。preprint DOI 是 10.1101/2024.09.18.613544。〔論文〕
- **assembly／benchmark 論文**：Wagner J., Keskus A.G., Oshima K.K., Ranallo-Benavidez T.R., …, Zook J.M.《A complete human pancreatic cancer genome》，bioRxiv 2026-05，DOI 10.64898/2026.05.01.722316。狀態是 preprint，尚未經同儕審查。〔論文〕
- **NIST 官網**（2026-10 更新）說 V0.6 SV/CNV 與 V0.4 small variant 都是 draft，並徵求回饋。下一個樣本是 HG009（PDAC 肝轉移，normal 是 CD4+ T cell）。〔官方文件〕https://www.nist.gov/programs-projects/cancer-genome-bottle

#### 1.2 樣本與 passage
- 患者是 61 歲女性（XX），PDAC，ypT2 N1。〔論文〕
- HG008-T 被描述為「mixed population with shared and subpopulation-specific somatic variants」。〔官方文件〕README_HG008.md
- 主要 batch 是 **0823p23**（passage 23）。NIST 另有 bulk passage p18、p21、p41、p53、p100、p101、p103。single-cell clone 放在 `NIST/HG008-T_clones/`，例如 `20240718p14/2D6/p15plus6`。官網說「8 cell lines derived from single-cell clones of HG008-T」已有資料。〔官方文件〕
- README 警告：**不要把 2022 年的資料和 0823p23 混用**，因為不同 passage 之間有 genomic change。`Liss_lab/other_passages/` 有 p2、p13 的 ILMN／ONT，專門用來研究 passage 間的變化。〔官方文件〕

#### 1.3 資料種類與 coverage（Sci Data Table 3/4）〔論文〕

| 技術 | HG008-T | HG008-N-D | HG008-N-P |
|---|---|---|---|
| Illumina PCR-free | 140x／141x／118x | 169x、115x | 150x |
| Element AVITI short／long insert | 76x／22x | 77x／26x | 76x／19x |
| PacBio Onso | 100x | 48x | – |
| Ultima UG100／ppmSeq | 212x／110x | 232x／160x | – |
| PacBio Revio HiFi | 79x、72x | 68x | 35x |
| ONT standard R10.4.1（E8.2） | 45x | 94x | 41x |
| ONT Ultra-Long R10.4.1 | 39x、38x | – | – |
| Hi-C（Phase Genomics、Arima、Dovetail） | 有 | Arima 有 | Dovetail LinkPrep（FTP） |
| single-cell WGS（BioSkryb ResolveDNA → ILMN／Ultima） | 120 cells（98 個通過 QC） | – | – |
| Bionano、G-banding karyotype、dGH（KROMASURE） | 有 | – | – |

- Strand-seq：Sci Data 正文**未查到**。
- FTP 實際檔案（GRCh38 BAM）〔官方文件〕：
  - HG008-T ONT-UL：`Liss_lab/UCSC_ONT-UL_20231207/HG008-T_GRCh38_GIABv3_ONT-UL-R10.4.1-dorado0.4.3_sup4.2.0_5mCG_5hmCG_54x_UCSC_20231031.bam`，**113 GB**，含 5mC/5hmC tag。
  - HG008-T ONT-std：`Liss_lab/UCSC_ONT_20231003/HG008-T_GRCh38_GIABv3_ONT-R10.4.1-doradov0.3.4-5mCG-5hmC_63x_UCSC_20230905.bam`，**131 GB**。
  - HG008-N-D ONT-std：`Liss_lab/Northeastern_ONT-std_20240422/` 下有 GRCh38-GIABv3 94x（**420 GB**）和 13x_gt25kb（55 GB）。
  - HG008-N-P ONT-std：同一目錄下有 41x（173 GB）和 20x_gt25kb（73 GB）。
- raw data 在 SRA SRP047086／BioProject PRJNA200694。〔論文〕

#### 1.4 HG008-N 的 diploid assembly
- preprint 說作者建立了「near-complete, donor-specific, haplotype-resolved assemblies」，對象是 tumor MRCA 與 matched normal。normal 有 **44 條 T2T scaffold**。tumor 的 35 條染色體都有 T2T scaffold，共 9 個 gap，其中 8 個是 rDNA。〔論文〕
- 檔案：HG008N_v6.3（1.50 GB），HG008T_v3.2（1.25 GB）。small variant V0.4 已改用 HG008-T **v3.4**（有 14,370 個 polishing edit），但 v3.4 FASTA 的公開路徑**未查到**。〔官方文件〕
- **沒有 MAT/PAT 標記。** HG008 沒有父母樣本，所以 contig 命名是 `chr*_hap1/_hap2`。這是 phased，但沒有 parent-of-origin。〔推論〕依據是 SV/CNV V0.6 README 的 contig 命名。

#### 1.5 somatic benchmark 現狀

**Small variant V0.4（2026-10-06）**〔官方文件〕README
- 推薦 VCF：`HG008-T_somatic_smvar_benchmark_v0.4_GRCh38_tumorvariants.vcf.gz`，含 18,871 筆（9,574 個 SNV、9,297 個 INDEL）。
- 推薦 BED：`..._GRCh38_all.bed`（2.793 Gb）。另有 `nogermlineinterference.bed` 與 `nogermlinewithin50bp.bed`。
- 範圍只含 **clonal／truncal** 變異。兩個 likely-subclonal BED（VAF < 100%）已整段排除。README 建議 query 先濾掉 VAF < 5–10% 的 call。
- **phasing**：GT 對 HG008-N v6.3 與 HG008-T v3.4 分 haplotype（`GTHAP1/GTHAP2`）。INFO 標記 somatic 變異來自 hap1 或 hap2。
- **`VAF = TAC/TCN`**：TAC 是帶 ALT 的 tumor assembly 拷貝數，TCN 是 tumor total CN。這不是觀測的 read fraction，而是假設 100% clonal 時的期望 VAF。
- 本文用 streaming 讀取這個 279 KB VCF，統計 TAC/TCN 分布：

  | TAC/TCN | 筆數 | 解讀〔推論〕 |
  |---|---|---|
  | 1/2 | 11,864 | 正常 CN=2，multiplicity 1 |
  | 1/1 | 5,890 | 單拷貝區（LOH／hemizygous），SNV 在保留的 haplotype 上 |
  | 2/2 | 677 | 突變先發生，該 haplotype 後來被複製，可能是 cnLOH 或 duplication，multiplicity 2 |
  | 1/3 | 249 | CN=3，multiplicity 1：gain 之後發生，或位在未複製的 haplotype |
  | 2/3 | 148 | CN=3，multiplicity 2：gain 之前發生在被複製的 haplotype |
  | 3/3、1/4、2/4、4/5 等 | 24 | 高 CN 區 |
  | 多等位（1,1/2,2） | 19 | – |

  → 這是**真實腫瘤中「gain 前後 multiplicity 不同」的 SNV 實例**，而且有 assembly 等級的真值。〔推論〕
- V0.4 已知限制：centromere、segdup 被排除。germline-to-ref reversion 在線性 reference 上無法呈現。部分 subclonal indel 仍然漏掉。

**SV＋CNV V0.6（2026-10-06）**〔官方文件〕README
- GRCh38：211 個 PASS SV，ALL 共 245 個。類型有 DEL、DUP、INS（含 L1）、CNV:TR、BND，inversion 拆成 BND。
- **subclonal**：VAF ≥ 5% 的 subclonal SV 屬於 PASS，並帶 `SUBCLONAL=y`。這類 SV 只放在 `clonal_and_subclonal.bed`，不在 `clonal.bed`。VAF < 5% 的 9 個 SV 標 `VAFlt5percent`。
- **CNV**：`GRCh38_..._somatic-CNV_PASS.draftbenchmark.calls.bed` 給 total CN 與 **`CN_HAP1/CN_HAP2`**（phased 到 normal haplotype）。native 版另有 `..._CNV_samehap...bed`。
- CN 值以**沒有 WGD 的細胞**為準，雖然有一部分細胞已經 WGD。
- **沒有獨立的 cnLOH call 檔。** native 版用某 haplotype CN=0 表示 loss。
- truvari 用法：v5.0 以上，`--sizemax -1 --passonly --pick multi --includebed`。先跑 `decomposeINV_and_filterlt50bp.py`。README 明說「CNV comparison best practices have not been developed yet」。
- native 版的 CN 門檻仍屬 exploratory：47 個 DUP 中只有 22 個在 depth 上看得到 gain。

舊版歷程：stvar V0.1（2024-12）→ V0.2 → V0.3 → stvar-CNV V0.4（2025-07）→ V0.5（2026-03）→ V0.6。smvar V0.3（2026-04）→ V0.4。〔官方文件〕Liss_lab/analysis 目錄清單

#### 1.6 subclone、aneuploidy、cnLOH、HP-specific CN、passage 差異〔論文〕
- **Aneuploidy**：hypodiploid。NIST p18 有 17/20 個 spread 是 34–36 條染色體，3/20 個 spread 是 WGD（68–70 條）。MGH p31 的 spread 在 29–71 條之間。chr4 在大多數細胞是單拷貝。有大量造成 LOH 的大片 deletion（1p、3p、6p、6q、8p、18q 等），型態類似 TCGA 的 chromosomal-scale LOH。（Sci Data、preprint）
- **cnLOH**：preprint 說「Translocations caused only three large duplications or CNLOH events」（Supp Fig 7）。具體染色體**未查到**。
- **haplotype-specific CN**：chr6 兩臂在**相反 haplotype** 上丟失，造成 MHC 少一份。chr19 有 nested foldback，CN 在 1–5 之間，最後 8 Mb 來自另一個 haplotype。（preprint）
- **driver**：KRAS G12V 的突變拷貝可能被複製；CDKN2A 一個 haplotype 有 20 kb deletion，另一個整段丟失；TP53 K132T 位在剩下的拷貝；SMAD4 有 frameshift。（Sci Data）
  - KRAS 的例子是「先突變、後 gain」的 CN timing 實例。〔推論〕
- **subclone／passage**：
  - WGD 比例：p21 是 9/40，p53 是 28/40，p101 是 20/20。
  - dGH 看了 p21 與 p53 共 80 個細胞，大多數事件是共有的。subclonal 變異只出現在 1–4 個細胞。
  - preprint 說「a subset are subclonal due to loss in descendent passages, mostly due to large deletions」。
  - preprint 只處理 truncal 變異，subclonal 分析留給未來。
- **purity／normal contamination**：兩篇都**未查到**數值。

### Q2. GIAB mosaic／low VAF 基準
- **HG002 Mosaic SNV v1.1**（目錄 `mosaic_v1.10`）〔官方文件〕README；〔論文〕Daniels C.A. et al., bioRxiv 2024，DOI 10.1101/2024.12.02.625685
  - 內容是 85 個 mosaic SNV，沒有 indel。VAF 有把握 > 5%，大多數 > 7%，上限約 30%。
  - BED 是 2.45 Gb（891,240 個區段）。這些區段裡可以確認沒有其他 VAF > 2% 的 mosaic 變異，所以適合拿來估 FP。
  - 資料來源是 Illumina 300x trio，HG003＋HG004 當 normal。驗證平台有 BGI、Element、HiFi。
  - 建議使用 NIST RM8391 DNA，因為 Coriell GM24385 的 VAF 不同。
  - 變異**可能來自 B cell mosaicism 或細胞株培養**。一篇 2026 medRxiv（DRAGEN）也指出許多 HG002「mosaic」變異是培養產生的。
  - README 說 hap.py、vcfeval「do not consider VAF」，需要新的 VAF-aware 工具。
- 對「低 CCF clone」的用處〔推論〕：
  - **能證明**：真實 WGS 中 5–30% VAF 的單一 SNV 群體確實存在，也能被多平台驗證。也可以用它的 2% 偵測下限，當作 caller sensitivity 的參考。
  - **不能證明**：85 個 SNV 之間沒有 clone 成員或 tree 關係。它們的 CN 是正常的，沒有 CNV。它們也不是腫瘤。所以它**不能當成低 CCF clone 的 clustering 或 tree 真值**。

### Q3. Stratifications（v3.6）
- 論文：Dwarshuis N. et al.《The GIAB genomic stratifications resource for human reference genomes》，*Nat Commun* 15:9029（2024），DOI 10.1038/s41467-024-53260-y。〔論文〕
- 目錄：https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/genome-stratifications/v3.6/GRCh38@all/ 。另有 CHM13、GRCh37、HG002.mat、HG002.pat 版本。〔官方文件〕
- 類別有 Union、Mappability、SegmentalDuplications、LowComplexity、GCcontent、OtherDifficult（MHC、KIR、VDJ、gap）、XY、Functional、Ancestry 等。
- 模擬時建議用的檔案〔官方文件〕清單與大小；用途是〔推論〕：

| 用途 | 檔案（GRCh38@all/…） | 大小 |
|---|---|---|
| 只在容易區放事件 | `Union/GRCh38_notinalldifficultregions.bed.gz` | 31 MB |
| 標註困難區 | `Union/GRCh38_alldifficultregions.bed.gz` | 30 MB |
| 排除 low-map＋segdup | `Union/GRCh38_alllowmapandsegdupregions.bed.gz` | 3.4 MB |
| low mappability | `Mappability/GRCh38_lowmappabilityall.bed.gz` | 4.3 MB |
| segdup | `SegmentalDuplications/GRCh38_segdups.bed.gz`、`_segdups_gt10kb.bed.gz` | 64 KB／17 KB |
| hap.py 分層 TSV | `GRCh38-all-stratifications.tsv` | 17 KB |

- 對 HP 特徵的特別提醒〔推論〕：
  - segdup 與 low-map 區的 phasing 和 allele-specific depth 都不可靠。HP-aware 模擬應排除這些區，或另外分層報告。
  - MHC 在 HG008 是真實的 haplotype-specific loss 區。但它也是 OtherDifficult，判讀時要小心。

### Q4. 評估流程與工具
- **GA4GH 定義**〔論文〕Krusche P. et al., *Nat Biotechnol* 37:555–560（2019），DOI 10.1038/s41587-019-0054-x；GitHub https://github.com/ga4gh/benchmarking-tools
  - benchmark region（confident region）是 benchmark 宣告「區內所有變異都已知」的區域。只有區內的 call 會被計分。
  - TP 是 query 與 truth 在 allele 或 genotype 層級相符，比對時容許不同表示法。FN 是 truth 有、query 沒有。FP 是 query 有、truth 沒有，而且位在 benchmark region 內。
  - 結果要依 stratification 分層報告。
  - 這份規範**只涵蓋 germline small variant**。
- **工具**
  - hap.py＋vcfeval engine（https://github.com/Illumina/hap.py ，https://github.com/RealTimeGenomics/rtg-tools ）：HG002 v5.0q README 推薦用於 small variant。〔官方文件〕
  - som.py 包在 hap.py 裡，是 somatic 用的位置比對。mosaic README 說它「less robust」，可能漏掉等價的不同表示法。〔官方文件〕
  - aardvark（PacBio）：HG008 small variant V0.4 README 推薦的工具。README 也說 vcfeval 與 hap.py 可能無法處理「改寫 germline 的 somatic 變異」。〔官方文件〕
  - truvari：用於 SV，v5 以上。〔論文〕English A.C. et al., *Genome Biol* 23:271（2022），DOI 10.1186/s13059-022-02840-6。參數見 §1.5。
- **somatic 評估是否有 GA4GH 建議**：**未查到**正式的 GA4GH somatic benchmarking 規範。
  - 目前 GIAB 的做法是三件事：用 clonal／truncal benchmark、要求 query 先濾掉低 VAF、標記 subclonal 但不計分。〔官方文件〕
  - VAF-aware 比較與 CNV 比較都還沒有標準。〔官方文件〕
  - → 使用者的 clone-tree 評估（CCF、clone assignment、topology）**需要自己定義 metric**。GIAB 只能提供 variant 層級的 TP/FP/FN。〔推論〕

### Q5. 與 long read phasing 相關的 GIAB benchmark
- **HG002 v5.0q**（draft）：以 T2T-HG002 Q100 v1.1 diploid assembly 為基礎，覆蓋 GRCh37、GRCh38、CHM13v2。〔官方文件〕
  - 本文讀了 GRCh38 smvar VCF 的開頭片段，GT 已 phased（`0|1`、`1|0`、`1|1`）。〔官方文件〕+〔推論〕
  - 引用 T2T Q100 preprint，DOI 10.1101/2025.09.21.677443。這部分由同事負責。
- **HG002 v4.2.1**：mapping-based，對 HG002 已被 v5.0q 取代。本文讀了 GRCh38 VCF 的開頭片段，GT 多數是 unphased（`0/1`），雖然 header 有 PS 欄位。〔官方文件〕+〔推論〕
  - 論文是 Wagner J. et al., *Cell Genomics* 2022，DOI 10.1016/j.xgen.2022.100128。〔論文〕（DOI 憑記憶，本次沒有逐字驗證）
- **CMRG v1.00**：273 個醫學相關困難基因，以 hifiasm diploid assembly 建立，phased。〔論文〕Wagner et al., *Nat Biotechnol* 2022，DOI 10.1038/s41587-021-01158-1。
- **HG001–HG007**：HG002–HG004 是 AJ trio，HG005–HG007 是漢人 trio，各有 v4.2.1 small variant benchmark（目錄見 `release/`）。parent-of-origin phasing 只有 HG002 的 Q100 assembly 與 stratifications（`HG002.mat@all`、`HG002.pat@all`）有完整的 MAT/PAT 層。〔官方文件〕目錄清單；細節未逐一查證
- **HG008**：small variant V0.4 的 somatic 與 germline 都 phased 到 hap1/hap2，而且有 native-assembly 座標版。這是 GIAB 中**唯一同時有 somatic 與 haplotype 資訊**的資源。〔官方文件〕
- 使用者的 germline phasing 層可以兩種方式驗證〔推論〕：
  - 用 HG002 v5.0q 驗證 longphase 的 germline phasing 準確度（switch／flip error）。
  - 用 HG008-N v6.3 驗證 tumor 背景下的 HP 指派。

### Q6. GIAB 能證明與不能證明的事件
見 §3。補充一點：使用者的 HCC1395 有 SEQC2 somatic reference（Fang L.T. et al., *Nat Biotechnol* 39:1151（2021），DOI 10.1038/s41587-021-00993-6），還有 tumor／normal 稀釋系列。這不屬於 GIAB，但對「低 purity」最有用。建議另立一份文件查證。〔論文〕〔推論〕

---

## 3. 「可以證明／不能證明」對照表

| 事件類 | GIAB 能證明的部分 | GIAB 不能證明的部分 | 主要證據 |
|---|---|---|---|
| **低 purity** | 間接：HG008-T＋HG008-N-D／N-P 有同一個體的 tumor 與 normal 高深度 ONT／HiFi，可以在真實 read 上做 in silico 混合，真值不變。〔推論〕 | GIAB **沒有官方 purity titration** 或 purity 真值（未查到）。HG008-T 是細胞株，接近 100% tumor。 | Sci Data Table 3/4；搜尋未查到 HG008 mixture |
| **subclonal CN** | 有限：V0.6 有 `SUBCLONAL=y` 的 SV（VAF ≥ 5%）。WGD 比例隨 passage 改變。dGH 看到 1–4 個細胞的 subclonal SV。〔論文〕〔官方文件〕 | CNV 真值以「非 WGD 細胞」為準，屬於 clonal。**沒有 subclonal CN 的 CCF 或 haplotype 真值。** | V0.6 README；preprint |
| **deletion 造成突變遺失** | 有：preprint 說 subclonal 變異在後代 passage 消失，主因是大片 deletion。5,890 個 SNV 是 TAC/TCN=1/1，位在單拷貝區，表示另一個 haplotype 已經丟失。〔論文〕〔推論〕 | 沒有逐一列出「被 deletion 刪掉的 SNV」清單。passage 間 SNV 遺失的真值也還沒發布。 | preprint；V0.4 VCF 統計 |
| **低 CCF clone** | 弱：HG002 mosaic 證明 5–30% VAF 的變異真實存在，也能被偵測。HG008 subclonal SV 的 VAF 可以 < 5%。〔官方文件〕 | mosaic 變異沒有 clone 結構，很可能來自培養。HG008 的 small variant benchmark 排除了 subclonal 變異。**沒有低 CCF clone 的 tree 真值。** | mosaic v1.1 README；V0.4 README |
| **HP 拆分（haplotype-specific CN、SNV 在哪個 HP）** | **強**：HG008 有 tumor 與 normal 的 haplotype-resolved T2T-like assembly，以及 `CN_HAP1/CN_HAP2`、`GTHAP1/GTHAP2` 與 somatic 來源 haplotype。例子：chr6 兩臂丟在相反 haplotype；chr19 CN 1–5。〔官方文件〕〔論文〕 | 只有 hap1/hap2，**沒有 MAT/PAT**。只限 clonal 事件。 | V0.4／V0.6 README；preprint |
| **cnLOH** | 有，但數量少：preprint 指出 translocation 造成 3 個 large duplication 或 CNLOH 事件。TAC/TCN=2/2 的 677 個 SNV 符合「LOH 後複製」或 duplication 的型態。〔論文〕〔推論〕 | 沒有獨立的 cnLOH call 檔。具體區段要看 Supp Fig 7（未查到）。 | preprint |
| **CN timing（gain 前後 multiplicity）** | **強**：V0.4 每個 SNV 都有 assembly 推得的 TAC/TCN。CN=3 區有 2/3（148 個，pre-gain）和 1/3（249 個），CN=2 區有 2/2（677 個）。KRAS G12V 的突變拷貝被複製。〔官方文件〕〔推論〕 | 這只是 truncal（MRCA）的拷貝數，沒有 subclonal timing。TAC/TCN 是 assembly 期望值，不是 read 觀測值。WGD 細胞不適用。 | V0.4 VCF header 與統計；Sci Data |
| （附）germline phasing 層 | 強：HG002 v5.0q 已 phased，有 Q100 assembly 與 MAT/PAT stratifications。HG008-N v6.3 有 hap1/hap2。 | HG002 不是腫瘤。 | v5.0q README |

---

## 4. 建議下載清單（存到 `/big8_disk/boyu114/benchmark_data/GIAB/`；**只列，未下載**）

`FTP=https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab`

| 優先 | 本地子目錄 | URL | 大小 |
|---|---|---|---|
| P0 | `HG008/smvar_V0.4/` | `$FTP/data_somatic/HG008/Liss_lab/analysis/NIST_HG008-T_somatic-smvar_DraftBenchmark_V0.4-20261006/`（README.md 37 KB、checksums.md5、`GRCh38/` 全部，除了 `nogermlinewithin50bp.bed`〔77 MB〕可以略過；`HG008Nv6.3/`） | GRCh38 小於 30 MB（不含 77 MB BED） |
| P0 | `HG008/stvar-CNV_V0.6/` | `$FTP/data_somatic/HG008/Liss_lab/analysis/NIST_HG008-T_somatic-stvar-CNV_DraftBenchmark_V0.6-20261006/`（README 79 KB、`GRCh38/` 11 個檔、`HG008Nv6.3/`） | 小於 1 MB |
| P0 | `stratifications_v3.6/GRCh38/` | `$FTP/release/genome-stratifications/v3.6/GRCh38@all/Union/`、`Mappability/`、`SegmentalDuplications/`、`GRCh38-all-stratifications.tsv` | 約 80 MB |
| P1 | `HG008/assembly/` | https://nist-giab.s3.us-east-1.amazonaws.com/giab_tumor-normal/analysis/HG008/NIST_asm_dev/HG008N_v6.3/HG008N_v6.3.fasta.gz | 1.50 GB |
| P1 | `HG008/assembly/` | https://nist-giab.s3.us-east-1.amazonaws.com/giab_tumor-normal/analysis/HG008/NIST_asm_dev/HG008T_v3.2/HG008T_v3.2.fasta.gz（v3.4 位置未查到） | 1.25 GB |
| P1 | `HG002/mosaic_v1.1/` | `$FTP/release/AshkenazimTrio/HG002_NA24385_son/mosaic_v1.10/GRCh38/SNV/`（VCF、BED、README；`_GermlineV4.2.1.vcf.gz` 143 MB 視需要再下載） | 約 20 MB（不含 143 MB） |
| P1 | `HG002/v5.0q/` | `$FTP/release/AshkenazimTrio/HG002_NA24385_son/v5.0q/HG002_GRCh38_v5.0q_smvar.{vcf.gz,vcf.gz.tbi,benchmark.bed}`＋README | 約 42 MB |
| P2 | `HG008/bam/` | `$FTP/data_somatic/HG008/Liss_lab/UCSC_ONT-UL_20231207/HG008-T_GRCh38_GIABv3_ONT-UL-R10.4.1-dorado0.4.3_sup4.2.0_5mCG_5hmCG_54x_UCSC_20231031.bam`（＋.bai） | 113 GB |
| P2 | `HG008/bam/` | `$FTP/data_somatic/HG008/Liss_lab/Northeastern_ONT-std_20240422/` 的 HG008-N-P GRCh38-GIABv3 41x BAM（N-D 94x 是 420 GB，不建議） | 173 GB |
| P3 | – | `$FTP/data_somatic/HG008/Liss_lab/other_passages/`（p2、p13 ONT／ILMN）、`NIST/HG008-T_clones/`（single-cell clone）：等 subclone 真值發布後再評估 | 未查（目錄沒有列大小） |

注意事項：
- GIAB GRCh38 BAM 用的是 `GRCh38_GIABv3` reference。使用者的 CRAM reference 是 `GRCh38_no_alt_analysis_set`。兩者 chr1–22、X 的座標相同，但 decoy 與 contig 集合不同，實際使用前要核對 header。〔推論〕
- 建議 P2 只用 region（`samtools view URL region`）串流取片段，不要下載整檔。〔推論〕

---

## 5. 參考文獻

1. McDaniel J.H., Patel V., … Zook J.M. Development and extensive sequencing of a broadly-consented Genome in a Bottle matched tumor-normal pair. *Sci Data* 12:1195 (2025). https://doi.org/10.1038/s41597-025-05438-2 ；PMC12267650；code：https://github.com/usnistgov/giab-HG008-data-paper
2. Wagner J., Keskus A.G., Oshima K.K., Ranallo-Benavidez T.R., … Zook J.M. A complete human pancreatic cancer genome. bioRxiv (2026). https://doi.org/10.64898/2026.05.01.722316
3. NIST. Cancer Genome in a Bottle（2026-10 更新）. https://www.nist.gov/programs-projects/cancer-genome-bottle
4. GIAB FTP README_HG008.md. https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG008/README_HG008.md
5. HG008-T small variant draft benchmark V0.4 README. https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG008/Liss_lab/analysis/NIST_HG008-T_somatic-smvar_DraftBenchmark_V0.4-20261006/README.md
6. HG008-T SV/CNV draft benchmark V0.6 README. https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG008/Liss_lab/analysis/NIST_HG008-T_somatic-stvar-CNV_DraftBenchmark_V0.6-20261006/README.md
7. Daniels C.A., … Olson N.D., Zook J.M. A robust benchmark for detecting low-frequency variants in the HG002 GIAB NIST reference material. bioRxiv (2024). https://doi.org/10.1101/2024.12.02.625685 ；README：https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/mosaic_v1.10/GRCh38/SNV/README.md
8. Dwarshuis N., … Zook J.M. The GIAB genomic stratifications resource for human reference genomes. *Nat Commun* 15:9029 (2024). https://doi.org/10.1038/s41467-024-53260-y
9. Krusche P., … GA4GH Benchmarking Team. Best practices for benchmarking germline small-variant calls in human genomes. *Nat Biotechnol* 37:555–560 (2019). https://doi.org/10.1038/s41587-019-0054-x
10. English A.C., … Sedlazeck F.J. Truvari: refined structural variant comparison preserves allelic diversity. *Genome Biol* 23:271 (2022). https://doi.org/10.1186/s13059-022-02840-6
11. NIST HG002 v5.0q README. https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/v5.0q/NIST_HG002_v5.0q_variant-benchmarksets_README.md ；T2T Q100 preprint：https://doi.org/10.1101/2025.09.21.677443
12. Wagner J., … Zook J.M. Curated variation benchmarks for challenging medically relevant autosomal genes. *Nat Biotechnol* 40:672–680 (2022). https://doi.org/10.1038/s41587-021-01158-1
13. Wagner J., … Zook J.M. Benchmarking challenging small variants with linked and long reads. *Cell Genomics* 2:100128 (2022). https://doi.org/10.1016/j.xgen.2022.100128（DOI 憑記憶，本次沒有逐字驗證）
14. Fang L.T., … Xiao W. Establishing community reference samples, data and call sets for benchmarking cancer mutation detection using whole-genome sequencing. *Nat Biotechnol* 39:1151–1160 (2021). https://doi.org/10.1038/s41587-021-00993-6（SEQC2 HCC1395；非 GIAB，本次沒有展開查證）
