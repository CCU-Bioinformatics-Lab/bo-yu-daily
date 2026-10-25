# SEQC2、COLO829 與 CASTLE 細胞株：真實基準能證明哪些模擬事件

調查日期：2026-10-25。範圍：SEQC2（HCC1395/HCC1395BL）、COLO829/COLO829BL，以及 H1437、H2009、HCC1937、HCC1954 的公開真值。
證據等級：〔官方文件〕＝FTP、Zenodo、GitHub 原檔或 README；〔論文〕＝同儕審查或 preprint 正文；〔推論〕＝本文由原檔計算或推理得出。
本地先讀過的整理：`research/hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/`（01、03 章）、`tumor_sample.md`。本文不重複那裡已寫的 Fang 2021 細節，只補新資訊。

---

## 0. 結論（先讀這段）

1. **低 purity 有真實濕實驗證據。** SEQC2 SPP 是真的 gDNA 混合（100/75/50/20/10/5/0%），350× WGS。官方也放了 HATCHet、FACETS、ascatNgs 在每個混合比例上的 CNV 結果。〔官方文件〕〔論文〕
2. **nominal 不等於實測。** 從官方 HATCHet 檔讀出的 tumor fraction 是：nominal 20% → 0.24、50% → 0.43、75% → 0.68、100% → 0.995。5% 與 10% 擬合失敗。〔推論，由官方檔計算〕
3. **LOH／cnLOH 有高可信度真值。** SEQC2 CNV benchmark 有 320 個 high-confidence LOH call，共 1,490.4 Mb（定義為 CN=2 的 LOH，等於 cnLOH）。HCC1395 另有 clonal 17q NLOH。〔論文〕
4. **subclonal CN 存在，但沒有 haplotype-specific 的 subclonal 真值。** HCC1395 與 COLO829 都有 10x scDNA 證據顯示 subclonal CNA（只有 total CN）。沒有任何資料集逐段標出「哪個 haplotype 在哪個 subclone 增加」。〔論文〕
5. **低 CCF clone 的存在有證據，但沒有逐 SNV 的 clone label。** Fang 2021 報告 VAF 峰值在 0.15 與 0.08，樹上 S3、S6 的 CCF < 10%。v1.2.1 有 5,146 個 SNV 的 TVAF < 0.1。〔論文〕〔推論〕
6. **deletion 造成突變遺失、CN timing（multiplicity）、somatic HP 拆分：沒有直接真值。** 只能用間接證據或自行在 ONT 上建立 silver standard。〔推論〕
7. **最大新發現：CASTLE + Wakhan。** 使用者的 HCC1395、H1437、H2009、HCC1937、HCC1954 ONT 都屬於 CASTLE panel。Wakhan（medRxiv 2025-12）為其中 5 個 normal 建了 chromosome-scale diploid assembly，並發布 haplotype-specific CNA 輸出與 mutation timing 腳本（Zenodo 21611881）。這是 HP-aware 驗證最接近的公開「參考 coverage」。〔論文〕〔官方文件〕
8. **可行流程：** 用 SEQC2 v1.2.1 SNV 當 HCC1395 的 SNV 真值。用自己的 ONT subsample 量測實測 purity。再用 Wakhan／SEQC2 LOH 檢查 HP 層級的 cnLOH 與 allele imbalance。見第 8 節。

---

## 1. 資源總表

| 資源 | 細胞株 | 內容 | 版本／日期 | 真值強度 | 來源 |
|---|---|---|---|---|---|
| SEQC2 somatic SNV/indel reference call set | HCC1395 | 39,447 SNV、1,625 indel（v1.2.1，HC region 內） | v1.0 (2018)、v1.1 (2019)、v1.2 (2020-05)、v1.2.1 (2022-10) | 高（多中心、多 caller、AmpliSeq/WES/PacBio 驗證） | 〔官方文件〕FTP `release/` |
| SEQC2 High-Confidence Regions | HCC1395 | BED，16 MB | v1.2 | 高 | 〔官方文件〕 |
| SEQC2 SPP titration | HCC1395 + BL | 真實 gDNA 混合 7 個比例，3 replicate，另有 10×–300× downsample | 2021 | 高（濕實驗） | 〔官方文件〕〔論文〕 |
| SEQC2 CNV benchmark | HCC1395 | 346 gain（1,525.6 Mb）、33 loss（87.9 Mb）、320 LOH（1,490.4 Mb） | Genome Biol 2024 | 中高（只保證 GAIN/LOSS/LOH 類別，不保證整數 CN） | 〔論文〕 |
| SEQC2 SV consensus | HCC1395 | 1,788 SV（Illumina、10x、PacBio、ONT、Hi-C） | Genome Biol 2022 | 中高；包含小族群 SV | 〔論文〕 |
| SEQC2 HCC1395 ONT/PacBio BAM | HCC1395 + BL | `tumor.ont.bam` 70G、`normal.ont.bam` 46G、PacBio NGMLR/PBMM2 | 2022-01 | 原始資料 | 〔官方文件〕 |
| SEQC2 HCC1395BL assembly | HCC1395BL | 10 kb+ scaffold，PacBio+Illumina+10x+Hi-C；GenBank JAEOAY000000000 | v1.0 | 未標明 haplotype-resolved | 〔官方文件〕 |
| HCC1395 10x scCNV | HCC1395 + BL | 1,270 tumor／638 normal cells（QC 後） | Fang 2021 | 支持 subclonal CNA（total CN） | 〔論文〕 |
| COLO829 SV truth set | COLO829 | 68 somatic SV（134 BND 記錄）＋ CN 檔 | Zenodo 3988185（2020-08） | 高 | 〔官方文件〕〔論文〕 |
| COLO829 in silico purity 混合 | COLO829 + BL | ILL/ONT/PB 各 10/20/25/50/75% | ENA PRJEB27698 | 中（讀段隨機混合，不是濕實驗） | 〔官方文件〕〔論文〕 |
| COLO829 NYGC SNV truth（本機已有） | COLO829 | 42,993 PASS（41,427 SNV、1,566 MNV；38,517 HighConfidence） | NYGC pipeline v6 | 中高；來源論文待核 | 〔推論，由本機檔讀出〕 |
| COLO829 scDNA | COLO829 | 1,475 cells，至少 4 個 subclone | Commun Biol 2020 | 支持 subclonal CNA | 〔論文〕 |
| CASTLE panel | HCC1395、H1437、H2009、HCC1937、HCC1954、Hs578T（+COLO829 額外資料） | Illumina、HiFi、ONT R10；SNV benchmark；SV confident ensemble | Release 1–4（2024-03 至 2026-09） | SNV：orthogonal benchmark；SV：非 ground truth | 〔官方文件〕 |
| Wakhan 補充資料 | 上述 5 株 CASTLE（不含 Hs578T） | diploid normal assembly、haplotype-specific CNA、timing 腳本、HCC1954/H1437 purity 混合 | Zenodo 21611881 v2.0（2026-07） | 中（haplotype coverage 參考；無 curated CNA 真值） | 〔論文〕〔官方文件〕 |
| Severus 補充資料 | CASTLE 細胞株 | SV truthset VCF、Minda 評估 | Zenodo 14541057（2024-12） | 中 | 〔官方文件〕 |

---

## 2. Q1：SEQC2 HCC1395 somatic SNV/indel reference call set

### 2.1 版本與檔案

- FTP 根目錄：`https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/seqc/Somatic_Mutation_WG/release/`，有 `v1.0/`、`v1.1/`、`v1.2/`、`v1.2.1/`、`latest/`。〔官方文件〕
- `latest/` 等於 v1.2.1。〔官方文件〕
- **用 v1.2.1。** README 說明：v1.2 VCF 只用 consensus callable region 過濾。v1.2.1 再用 `High-Confidence_Regions_v1.2.bed` 交集。差異是 113 SNV 與 297 indel。〔官方文件〕`release/latest/README.md`
- v1.0 另有 `HCC1395BL_highConfident_germline_variants.txt.gz`（34M），可當 germline 真值。〔官方文件〕

### 2.2 本文由 v1.2.1 讀出的統計〔推論，由官方檔計算〕

- SNV：39,447（HighConf 37,330、MedConf 2,117）。indel：1,625。
- VCF 有 `TVAF`（三 aligner 合併 tumor VAF）、`TVAF95`、`NVAF`、`bwaDP` 欄位。可直接拿來比對 ONT VAF。
- **chrX 沒有任何 call。** 6p、16q 被排除（germline LOH 區）。這些區域不能用來驗證 HP 事件。〔論文〕Fang 2021 Methods
- TVAF 分佈：

| TVAF | SNV 數 |
|---|---:|
| 0.0–0.1 | 5,146 |
| 0.1–0.2 | 6,271 |
| 0.2–0.3 | 5,868 |
| 0.3–0.4 | 5,526 |
| 0.4–0.5 | 5,219 |
| 0.5–0.6 | 3,219 |
| 0.6–0.7 | 2,042 |
| 0.7–0.8 | 408 |
| 0.8–0.9 | 216 |
| 0.9–1.0 | 5,532 |

- VAF > 0.9 有 5,532 個。這代表 mutation 落在 LOH 區，或 mutation 在 LOH／gain 之前發生（multiplicity = total CN）。這是 CN timing 的間接訊號。〔推論〕

### 2.3 purity、ploidy、CNV、LOH

- 實測 purity：subHMM 估計約 **99%**。〔論文〕Fang 2021 p.6
- 實測 ploidy：**2.85**。Genome Biol 2024 CNV 論文引用此值，並用它重新置中 CNVkit。〔論文〕DOI 10.1186/s13059-024-03294-8
- 注意：DepMap CCLE ABSOLUTE 2018 檔把 HCC1395 ploidy 列成 1.48。DepMap 論壇已有人指出它和 SEQC2 karyotype（hypertetraploid）不符。**不要用 CCLE ABSOLUTE 的 HCC1395 ploidy。**〔官方文件〕https://forum.depmap.org/t/hcc1395-implausible-ploidy-estimate/458
- 6p、16q、chrX 在 HCC1395 是整段 loss。〔論文〕Genome Biol 2024 Methods
- clonal 17q copy-neutral LOH（NLOH）。〔論文〕Fang 2021 p.6
- CNV benchmark：346 gain、33 loss、320 LOH。LOH 定義為 CN = 2，所以這些就是 cnLOH。〔論文〕Genome Biol 2024
- 限制：作者明說整數 CN 中位數「不應當 gold standard」，breakpoint 也不精確。〔論文〕Genome Biol 2024 Discussion

### 2.4 有沒有 subclonal 突變

- 有。Fang 2021 觀察到 VAF 峰值在 0.15 與 0.08，判讀為 subclone。〔論文〕Fang 2021 p.6、Extended Data Fig. 8
- PhyloWGS 樹有 S1–S10。S3、S6 的 CCF < 10%，未畫出。〔論文〕Fang 2021 Fig. 4a
- **VCF 沒有 clone label。** 樹的輸入表沒有公開（見本地 01 章）。〔官方文件〕〔論文〕

---

## 3. Q2：SEQC2 tumor-normal titration（SPP）

### 3.1 設計

- 混合比例：100%、75%、50%、20%、10%、5%、0% tumor。真實 gDNA 混合，WGS 約 350×。〔論文〕Fang 2021 p.3
- 檔名對照（T:N）：`1-0`=100%、`3-1`=75%、`1-1`=50%、`1-4`=20%、`1-9`=10%、`1-19`=5%、`0-1`=0%。〔推論，由檔名與百分比對應〕
- 每個比例 3 個 replicate（`SPP_GT_<ratio>_{1,2,3}.bwa.dedup.bam`，各約 160 GB）。〔官方文件〕`data/SPP/`
- 另有 10X/30X/50X/80X/200X/300X downsample 子目錄。300X 是三 replicate 合併，每檔約 480–496 GB。〔官方文件〕

### 3.2 實測 tumor fraction（由官方 HATCHet 檔讀出）〔推論，由官方檔計算〕

檔案：`analysis/CNVs/SPP/hatchet/SPP_300X_<pct>.hatchet.txt`。讀第一列的 clone proportion。

| nominal tumor | HATCHet normal | HATCHet tumor 合計 | 判讀 |
|---:|---:|---:|---|
| 100% | 0.005 | 0.995 | 一致 |
| 75% | 0.318 | 0.682 | 略低 |
| 50% | 0.571 | 0.429 | 略低 |
| 20% | 0.758 | 0.242 | 略高 |
| 10% | — | — | 擬合失敗（6 個 1\|1 component） |
| 5% | — | — | 擬合失敗（3 個 1\|1 component） |

- 這只是一個 caller 的估計。HATCHet 在 SEQC2 replicate 間一致性最差。〔論文〕Genome Biol 2024
- 意義：DNA 混合比例和 cellular purity 不同。HCC1395 ploidy 2.85 > 2，所以 cellular purity 會低於 DNA fraction。Wakhan 也指出 60%／80% DNA 混合約等於 30%／50% cellular purity（HCC1954、H1437）。〔論文〕Wakhan preprint
- 使用者的 `tX_nY` 是 depth 比例，更接近 DNA fraction。實測 cellular purity 會更低。〔推論〕

### 3.3 能不能當證據

- **能**證明「低 purity」與「VAF 隨 purity 線性下降」。Fang 2021 用 linear mixed model 擬合，HighConf/MedConf 的 fitting score 明顯高於 LowConf。〔論文〕
- 限制：線性關係只在 copy-number-neutral 區成立。〔論文〕
- Genome Biol 2024：purity ≤ 20% 時 ascatNgs、DRAGEN 的 gain/loss 準確度大幅下降。< 20% 時 ascatNgs、CNVkit、Control-FREEC、HATCHet 都叫不出 loss。〔論文〕這是「低 purity 讓 CN 推論失敗」的真實證據。
- SPP 是 Illumina。**SEQC2 沒有 ONT 的 titration。**〔官方文件〕

---

## 4. Q3：SEQC2 SV 基準與 HCC1395 long read

- Talsania 2022：1,788 個 consensus SV（717 DEL、230 DUP、551 INS、133 INV、146 TRA、11 BND）。平台：Illumina、10x、PacBio、ONT、Hi-C。驗證：PCR、Affymetrix、Bionano、RNA-seq fusion。〔論文〕DOI 10.1186/s13059-022-02816-6
- Genome Biol 2024 說明：SV set 收進「小細胞族群」的事件，CNV set 只收整體族群事件。兩者應分開使用。〔論文〕這可間接支持 subclonal SV 存在。
- FTP `analysis/SVs/VCFs/` 只有各平台、各 caller 的原始 VCF。**未查到** consensus 1,788 VCF 在 FTP。它應在論文 Additional file。〔官方文件〕〔推論〕
- long-read BAM：`analysis/SVs/BAMs/tumor.ont.bam`（70G）、`normal.ont.bam`（46G）、`tumor.pacbio.{NGMLR,PBMM2}.bam`（75G/61G）。〔官方文件〕
- 另有 CNV long-read 結果：`analysis/CNVs/orthogonal_technologies/long_reads/result_BED/{PacBio,10x_Genomics,BioNano_Andy}/`（> 30 kb DEL/DUP BED，KB 級）。〔官方文件〕
- **haplotype-resolved assembly：** SEQC2 只有 `HCC1395BL_10kplus_v1.0.fa`（2.7G）。README 沒說是 diploid/phased。〔官方文件〕Wakhan 用 ONT + Hi-C + hifiasm 另建了 BL1395 assembly（N50 19 Mb，達 chromosome-level phasing，但有 8 處疑似 phase switch）。〔論文〕Wakhan preprint
- **未查到** SEQC2 官方的 HCC1395 haplotype-resolved somatic 分析。

---

## 5. Q4：HCC1395 single-cell／clonal 結構證據

- 10x Single Cell CNV：1,270 HCC1395 cells、638 HCC1395BL cells（QC 後）。結果顯示大量 subclonal CNA。〔論文〕Fang 2021 Fig. 4c
- subHMM 推出 clonal 與 subclonal CNA。〔論文〕
- 官方 HATCHet（WGS_NS_1）給出 2 個 tumor clone：0.21 與 0.77，normal 0.019。兩 clone 的 allele-specific CN 在 27.2% 基因組不同；其中 15.8% 只差一個 haplotype。〔推論，由官方檔計算〕
  - 警告：HATCHet 在 replicate 間不穩定，haplotype 標籤也只在 block 內有意義。不要把這些當成真值。〔論文〕Genome Biol 2024
- **沒有** scDNA 層級的 SNV 真值樹。PhyloWGS 樹的 topology 沒有逐邊驗證。〔論文〕本地 03 章
- 批次差異：使用者的 HCC1395 ONT 來自 CASTLE（2023 起），SEQC2 細胞在約 2017 年培養。subclone 比例可能已漂移。〔推論〕

---

## 6. Q5：COLO829／COLO829BL

### 6.1 SV truth set（Valle-Inclan 2022）

- 68 個 somatic SV。平台：Illumina HiSeq X、ONT、PacBio、10x、Bionano；外加實驗驗證。〔論文〕DOI 10.1016/j.xgen.2022.100139
- 下載：Zenodo 3988185。`truthset_somaticSVs_COLO829.vcf`（22 KB，134 BND 記錄）、`COLO829_somaticSV_copynumber.zip`（15 KB，含 bicseq CNA 與跨平台 `mergedCNA.tsv`）。〔官方文件〕
- 細胞來自 ATCC 一個 vial 擴增的大批次。〔論文〕
- chr3 的 CN profile 可用 4 輪 BFB + 一次 whole-genome doubling 解釋。這是**論文中的 CN timing 重建**。〔論文〕
- 有 germline 異合 CNA 後再 somatic LOH 的例子。〔論文〕
- 作者明說：subclonal 頻率 < 5% 的事件可能漏掉；細胞株有一定異質性，不同批次要另行驗證。〔論文〕
- 後續四實驗室 replicate 研究提出 54 個穩定 SV 的 consensus。〔論文〕Genome Res 2025, DOI 10.1101/gr.279352.124（此數字取自檢索摘要，未讀全文）

### 6.2 purity 混合

- 10/20/25/50/75% 的混合是**讀段隨機混合（in silico）**，不是 DNA 混合。〔論文〕
- ENA PRJEB27698 有這些混合檔。ONT 每個混合約 160–200 GB fastq，PacBio 約 44 GB，Illumina 約 30–48 GB。〔官方文件〕ENA filereport
- 用途：可證明「低 purity 降低 SV recall」。ONT 在 < 50% 時 recall < 22%（當年工具）。〔論文〕

### 6.3 SNV truth、purity、ploidy

- SNV/CNA truth 早期來源：Pleasance 2010、Craig 2016（Sci Rep, DOI 10.1038/srep24607）、Arora 2019。〔論文〕Valle-Inclan 2022 引用
- 本機已有 `/big8_disk/data/colo829_nygc/colo829_truth.vcf.gz`。header 指向 NYGC pipeline（Strelka2 等多 caller，`HighConfidence` flag），由 HKU ClairS/longphase-s 鏡像下載。〔推論，由本機檔讀出〕
  - 42,993 PASS；38,517 HighConfidence。VAF 0.4–0.6 最多（17k）；VAF > 0.9 有 7,762；VAF < 0.1 有 3,616。
  - 上游論文出處未核實。使用前要確認版本。
- 實測 purity／ploidy 的一手數值：**未查到**。論文只確認 WGD 與 BFB。scDNA 論文說 COLO829 呈 monosomic/trisomic 模式並有 endoreduplication。〔論文〕DOI 10.1038/s42003-020-1044-8

### 6.4 COLO829 single-cell

- 1,475 cells 淺層 scDNA，至少 4 個主要 subclone，並以 bulk 與 spectral karyotyping 驗證 hallmark 事件。〔論文〕Velazquez-Villarreal 2020
- Valle-Inclan 2022 比對：bulk 與 scDNA 主 cluster 很像；subclonal cluster B–D 有 bulk 看不到的 CNA。〔論文〕

### 6.5 SMaHT

- SMaHT 用 COLO829BL 建了 donor-specific assembly（COLO829BL_DSA），偵測到 1.8 倍的人工驗證 sSV。〔論文〕bioRxiv 2026, DOI 10.64898/2026.02.20.707061
- SMaHT 的 1:49 細胞株混合（Cell Genomics 2026）是 mosaic 基準。摘要沒說用 COLO829。〔論文〕DOI 10.1016/j.xgen.2026.101390
- **未查到** SMaHT 發布的 COLO829 tumor-in-normal 混合樣本一手文件。

### 6.6 long-read 與 haplotype-resolved CN

- ONT R9 與 PacBio（ENA PRJEB27698）、ONT R10（EPI2ME `https://labs.epi2me.io/colo-2024.03/`）。〔官方文件〕CASTLE README
- **未查到** COLO829 的 haplotype-resolved CN 真值。Wakhan 的 assembly 不含 COLO829BL。〔論文〕

---

## 7. Q6：H1437、H2009、HCC1937、HCC1954

| 細胞株 | somatic SNV benchmark | SV | diploid normal assembly | haplotype-specific CN | purity 混合 |
|---|---|---|---|---|---|
| H1437 | CASTLE orthogonal-technology／orthogonal-tools benchmark | CASTLE confident ensemble（≥2/3 技術、≥4/11 caller） | Verkko（PoreC + UL ONT），N50 > 130 Mb | Wakhan 輸出 | Wakhan in silico：100/80/60% DNA，60–20× |
| H2009 | 同上 | 同上 | Verkko | Wakhan 輸出 | 無 |
| HCC1937 | 同上 | 同上 | Verkko | Wakhan：除 3 條外每條染色體都有部分 LOH；full-chromosome LOH 有一半在此株 | 無 |
| HCC1954 | 同上 | 同上 | hifiasm（Hi-C），N50 89 Mb | Wakhan 輸出 | Wakhan in silico：同 H1437 |
| HCC1395 | SEQC2 + CASTLE | SEQC2 + CASTLE | hifiasm，N50 19 Mb | Wakhan 輸出 | SEQC2 SPP（濕實驗） |

來源：CASTLE GitHub README〔官方文件〕；Wakhan preprint〔論文〕；Zenodo 21611881〔官方文件〕。

重點：
- CASTLE SNV benchmark 是「留一技術」的 orthogonal 設計，不是多中心 consensus。強度低於 SEQC2。〔官方文件〕
- CASTLE README 明說 SV **沒有 ground truth**，只有 confident ensemble。〔官方文件〕
- Wakhan 沒有 curated CNA 真值。它用 diploid assembly 算 haplotype「reference coverage」，再評分各工具。〔論文〕
- Wakhan 不建模 clone mixture，只標記 subclonal segment。〔論文〕
- Wakhan Zenodo 有 `timing_scripts.tar.gz`（mutation timing 分析腳本）。正文未讀到 timing 結果。〔官方文件〕
- 使用者本機的 ONT CRAM 就是 CASTLE Release 1（`tumor_sample.md`）。所以 CASTLE/Wakhan 結果和使用者資料是同一批讀段。〔官方文件〕〔推論〕
- CCLE ABSOLUTE（2018-12-27 檔）有這些株的 purity/ploidy，但 DepMap 已停用 ABSOLUTE，HCC1395 值明顯錯誤。只能參考，不能當真值。〔官方文件〕DepMap 論壇
- **未查到** H1437、H2009、HCC1937、HCC1954 的 single-cell DNA 資料。

---

## 8. Q7：7 類事件「可以證明／不能證明」對照表

| # | 模擬事件 | 能證明？ | 最強真實證據 | 不能證明的部分 |
|---|---|---|---|---|
| 1 | 低 purity | **可以** | SEQC2 SPP 濕實驗混合；HATCHet 實測 0.24/0.43/0.68；VAF 線性下降〔論文〕〔推論〕 | ONT 沒有濕實驗 titration；COLO829、Wakhan 混合是 in silico |
| 2 | subclonal haplotype-specific CN gain | **部分** | HCC1395、COLO829 scDNA subclonal CNA〔論文〕；HATCHet 2-clone allele-specific CN〔推論〕；Wakhan subclonal flag〔論文〕 | 沒有逐段「哪個 HP、哪個 clone」真值；scDNA 只有 total CN |
| 3 | deletion 造成突變遺失 | **不能直接證明** | subclonal loss 存在（scDNA）〔論文〕；COLO829「germline 異合 → somatic LOH」例子〔論文〕 | 沒有資料標出「被刪掉的 SNV」 |
| 4 | cnLOH | **可以** | SEQC2 320 個 LOH（CN=2）、1,490 Mb；HCC1395 17q clonal NLOH〔論文〕；Wakhan HCC1937 廣泛 LOH〔論文〕 | SEQC2 只保證類別，breakpoint 不精確 |
| 5 | CN timing（multiplicity） | **間接** | COLO829 chr3 BFB→WGD 重建〔論文〕；SEQC2 5,532 個 VAF > 0.9 SNV〔推論〕；Wakhan timing 腳本〔官方文件〕 | 沒有逐 SNV multiplicity 真值 |
| 6 | 低 CCF clone | **部分** | VAF 峰值 0.15、0.08；S3、S6 CCF < 10%〔論文〕；5,146 SNV TVAF < 0.1〔推論〕 | 沒有 SNV→clone label；樹輸入未公開 |
| 7 | HP 拆分 | **只能驗 germline phasing** | Wakhan diploid assembly（5 株）、SEQC2 BL assembly、BL germline set〔論文〕〔官方文件〕 | 沒有 somatic SNV 的 HP 真值；chrX/6p/16q 無 SNV 真值 |

---

## 9. 用自己的 ONT 細胞株 + SEQC2 真值做驗證（可行流程）

所有步驟只用小檔或本機 CRAM。〔推論〕

1. **座標對齊。** SEQC2 VCF 用 `GRCh38.d1.vd1`。本機 CRAM 用 `GRCh38_no_alt_analysis_set`。主染色體名稱相同，可直接交集。先用 `bcftools view -R High-Confidence_Regions_v1.2.bed` 限縮。
2. **建 HCC1395 SNV 真值子集。** 取 v1.2.1 PASS SNV。排除 chrX、6p、16q。依 SEQC2 CNV benchmark 標記每個 SNV 所在的 gain／loss／LOH。
3. **量測實測 purity。** 在每個 `tX_nY` subsample 上做 pileup。只取 CN-neutral、非 LOH 區的 clonal SNV（TVAF 約 0.4–0.6 的峰）。回歸 ONT VAF 對 SEQC2 TVAF，斜率就是相對 purity。再和 nominal 比較。
4. **對照 SPP。** 用 HATCHet／FACETS 的 SPP 結果（KB–MB 級小檔）當 Illumina 端的參考曲線。檢查 ONT subsample 的曲線是否同形。
5. **驗 cnLOH 與 allele imbalance。** 用 longphase-s 對本機 normal phasing。在 SEQC2 LOH 區檢查 tumor 的 HP1/HP2 coverage 是否只剩一邊。再和 Wakhan 的 haplotype CNA 輸出比較（`castle_benchmarks.tar.gz` 中的 HCC1395 部分）。
6. **驗 HP 拆分的 germline 層。** 用 Wakhan BL1395 assembly 或 SEQC2 BL germline set，算 longphase-s 的 switch error。這是 somatic HP 指派的上限。
7. **低 CCF 與 timing 的 silver standard。** 在 phased reads 上找 VAF < 0.1 的 SEQC2 SNV。檢查它們是否只在一個 HP 上。VAF > 0.9 的 SNV 檢查是否落在 LOH／gain 區。這只能產生一致性證據，不是真值。
8. **跨株推廣。** H1437（低複雜度）與 HCC1954（高複雜度）用 Wakhan 的 CNA 與 in silico 混合結果。注意它們沒有 SEQC2 等級的 SNV 真值。

限制：
- 細胞批次不同。SEQC2 的 subclone 比例不一定適用於 CASTLE 讀段。〔推論〕
- PhyClone 不直接吃 HP；這套流程只驗證模擬事件的真實性，不驗證樹。〔推論〕

---

## 10. 建議下載清單（只列，不下載）

建議存放：`/big8_disk/boyu114/benchmark_data/SEQC2/`、`.../COLO829/`、`.../CASTLE/`。大小取自 FTP index 或 Zenodo API。

SEQC2 FTP 前綴：`https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/seqc/Somatic_Mutation_WG/`

| 優先 | 檔案（相對 SEQC2 前綴，或完整 URL） | 大小 | 用途 | 存放 |
|---|---|---:|---|---|
| A | `release/latest/high-confidence_sSNV_in_HC_regions_v1.2.1.vcf.gz` | 4.6M | SNV 真值 | SEQC2/ |
| A | `release/latest/high-confidence_sINDEL_in_HC_regions_v1.2.1.vcf.gz` | 263K | indel 真值 | SEQC2/ |
| A | `release/latest/High-Confidence_Regions_v1.2.bed` | 16M | HC region | SEQC2/ |
| A | `release/latest/README.md` | 1K | 版本說明 | SEQC2/ |
| A | `analysis/CNVs/SPP/{hatchet,facets,ascat}/` 全部 | 每檔 < 2M | SPP 實測 purity／CN | SEQC2/SPP_cnv/ |
| A | `analysis/CNVs/WGS/{hatchet,facets,ascat,dragen}/` | 每檔 < 1M | HCC1395 allele-specific CN | SEQC2/WGS_cnv/ |
| A | Genome Biol 2024 Additional file 5（CNV benchmark VCF） | 未查大小 | LOH／gain／loss 真值 | SEQC2/ |
| B | `release/v1.0/HCC1395BL_highConfident_germline_variants.txt.gz` | 34M | germline 真值 | SEQC2/ |
| B | `analysis/CNVs/SEQC_CNV_raw_data.zip` | 45M | CNV 原始整合資料 | SEQC2/ |
| B | `analysis/CNVs/orthogonal_technologies/affy_array/HCC1395.segments.txt` | 803K | array CN | SEQC2/ |
| B | Talsania 2022 Additional file（1,788 SV consensus） | 未查大小 | SV 真值 | SEQC2/ |
| C | `release/latest/sSNV.MSDUKT.superSet.v1.2.vcf.gz` | 359M | 含 LowConf 的全集 | SEQC2/ |
| C | `assembly/HCC1395BL_v1.0/HCC1395BL_10kplus_v1.0.fa` | 2.7G | BL assembly | SEQC2/ |
| C | `analysis/SNVs/cancer_reference_samples_supporting_files/data_to_recreate_call_set_v1-2.tar.gz` | 3.8G | 重建 call set | SEQC2/ |
| 不建議 | `data/SPP/*.bam`、`analysis/SVs/BAMs/*.bam` | 46–496G/檔 | 原始 BAM | — |
| A | https://zenodo.org/api/records/3988185/files/truthset_somaticSVs_COLO829.vcf/content | 22K | COLO829 SV 真值 | COLO829/ |
| A | https://zenodo.org/api/records/3988185/files/COLO829_somaticSV_copynumber.zip/content | 15K | COLO829 CN | COLO829/ |
| B | https://zenodo.org/api/records/3988185/files/COLO829_somaticSV_rawSVcalling.zip/content | 203M | 各平台 raw SV | COLO829/ |
| A | https://zenodo.org/api/records/21611881/files/tools_cmd.tar.gz/content | 9K | Wakhan 指令 | CASTLE/wakhan/ |
| A | https://zenodo.org/api/records/21611881/files/timing_scripts.tar.gz/content | 42K | mutation timing 腳本 | CASTLE/wakhan/ |
| A | https://zenodo.org/api/records/21611881/files/cna_profiles_visualization_castle.tar.gz/content | 6.9M | CNA 視覺化 | CASTLE/wakhan/ |
| B | https://zenodo.org/api/records/21611881/files/benchmarking.tar.gz/content | 184M | CNA profile 與評分腳本 | CASTLE/wakhan/ |
| C | https://zenodo.org/api/records/21611881/files/castle_benchmarks.tar.gz/content | 6.7G | 各工具在 CASTLE 的輸出 | CASTLE/wakhan/ |
| C | https://zenodo.org/api/records/21611881/files/castle_normal_assemblies.tar.gz/content | 8.4G | 5 株 diploid normal assembly | CASTLE/wakhan/ |
| C | https://zenodo.org/api/records/21611881/files/downsampled_{HCC1954,H1437}.tar.gz/content | 各 14.3G | in silico purity 混合結果 | CASTLE/wakhan/ |
| B | https://zenodo.org/api/records/16595168/files/variant_calls_and_benchmarks.tar.gz/content | 1.74G | CASTLE SNV benchmark（DeepSomatic v1） | CASTLE/deepsomatic/ |
| C | https://zenodo.org/api/records/14541057/files/variant_calls_and_benchmarks.tar.gz/content | 15.0G | Severus SV truthset 與評估 | CASTLE/severus/ |

已在本機：`/big8_disk/data/colo829_nygc/colo829_truth.vcf.gz`（COLO829 NYGC SNV truth，1.9M）。

---

## 11. 參考文獻

- Fang LT et al. Establishing community reference samples, data and call sets for benchmarking cancer mutation detection using whole-genome sequencing. *Nat Biotechnol* 39, 1151–1160 (2021). https://doi.org/10.1038/s41587-021-00993-6 （本地 PDF：`research/hcc1395_golden_tree_research/hcc1395_golden_tree.pdf`）
- Talsania K et al. Structural variant analysis of a cancer reference cell line sample using multiple sequencing technologies. *Genome Biol* 23, 255 (2022). https://doi.org/10.1186/s13059-022-02816-6
- Evaluation of somatic copy number variation detection by NGS technologies and bioinformatics tools on a hyper-diploid cancer genome. *Genome Biol* (2024). https://doi.org/10.1186/s13059-024-03294-8
- Espejo Valle-Inclan J et al. A multi-platform reference for somatic structural variation detection. *Cell Genomics* 2, 100139 (2022). https://doi.org/10.1016/j.xgen.2022.100139
- Velazquez-Villarreal EI et al. Single-cell sequencing of genomic DNA resolves sub-clonal heterogeneity in a melanoma cell line. *Commun Biol* 3, 318 (2020). https://doi.org/10.1038/s42003-020-1044-8
- Craig DW et al. A somatic reference standard for cancer genome sequencing. *Sci Rep* 6, 24607 (2016). https://doi.org/10.1038/srep24607
- Park J et al. Accurate somatic small variant discovery for multiple sequencing technologies with DeepSomatic. *Nat Biotechnol* 44, 1569–1578 (2025). https://doi.org/10.1038/s41587-025-02839-x
- Keskus A et al. Severus: accurate detection and characterization of somatic structural variation in tumor genomes using long reads. medRxiv (2024). https://doi.org/10.1101/2024.03.22.24304756
- Ahmad T, Keskus AG et al. Wakhan: reconstruction of chromosome-scale copy number profiles of tumor genomes with long-read sequencing. medRxiv (2025-12-15). https://doi.org/10.64898/2025.12.11.25342098
- Closing the gaps, and improving somatic structural variant analysis and benchmarking using CHM13-T2T. *Genome Res* 35 (2025). https://doi.org/10.1101/gr.279352.124
- SMaHT：Donor-specific assemblies enhance somatic structural variant detection in complex genomic regions. bioRxiv (2026). https://doi.org/10.64898/2026.02.20.707061
- SMaHT：Detecting low-allele-fraction mosaic mutations: a multi-institution benchmarking with cell-line mixtures. *Cell Genomics* (2026). https://doi.org/10.1016/j.xgen.2026.101390
- ClairS：a deep-learning method for long-read tumor-normal pair somatic small variant calling. *Nat Methods* (2026). https://doi.org/10.1038/s41592-026-03152-4
- 官方資源：SEQC2 FTP https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/seqc/Somatic_Mutation_WG/ ；CASTLE https://github.com/CASTLE-Panel/castle ；SRA PRJNA1086849、PRJNA489865；ENA PRJEB27698；Zenodo 3988185、21611881、16595168、14541057；DepMap 論壇 https://forum.depmap.org/t/hcc1395-implausible-ploidy-estimate/458
- PubMed 用於檢索上述論文的 metadata 與 PMC 全文（PMC9903816、PMC11188507）。
