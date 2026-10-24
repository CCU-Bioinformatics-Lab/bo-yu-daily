# Tumor Cell-line Alignment Sample Inventory

更新日期：2026-10-20

本文件整理目前 `/big8_disk/data/` 下六種主要 ONT 腫瘤細胞株的 alignment 檔路徑與
`subsample` 純度設計。盤點只看檔案、資料夾名稱與 CRAM header，沒有讀取 read 內容。
文末另列 PhyClone 論文的 benchmarking 資料集（`/big8_disk/boyu114/phyclone_dataset/`），
以及 SMC-Het DREAM Challenge 資料集（`/big8_disk/boyu114/smchet_dataset/`）。

## 格式更新：BAM → CRAM（依 `.crai` mtime 推斷約在 2026-09-23～24）

- 所有 subsample，以及所有原始 tumor／normal 檔，都已轉成 **CRAM**（`.cram` + `.cram.crai`）。原本的 `.bam` 已刪除。
- CRAM reference：`/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`（header 的 `UR:`；`chr1` 的 `M5:6aef897c…`）。讀取時要用 `-T`／`--reference` 指定這個 fasta，或者確認 header 的 UR 路徑可以存取。
- **以下 symlink 已失效**（目標 BAM 已轉成 CRAM 並刪除），不要再使用：
  - `HCC1395/ONT_Dorado/HCC1395{,BL}.bam{,.bai}`
  - `H1437/ONT/H1437{,BL}.bam{,.bai}`、`H2009/ONT/H2009{,BL}.bam{,.bai}`
  - `HCC1937/ONT/HCC1937{,BL}.bam{,.bai}`、`HCC1954/ONT/HCC1954{,BL}.bam{,.bai}`
  - `COLO829/ONT_PAO/subsample/t33_n00/COLO829_t33_n00.bam{,.bai}`（指向 `../../PAO29420.bam`，該檔已不存在）
- 上面這些失效檔案，對應的 CRAM 在 `/big8_disk/Google_somatic_data/bams/<line>/<line>_{Tumor,Normal}_ONT.GRCh38.sorted.cram`。只有 COLO829 PAO t33_n00 的對應檔在 `/big8_disk/data/COLO829/ONT_PAO/PAO29420.cram`。

## 資料來源（2026-10-17 核對）

- HCC1395、H1437、H2009、HCC1937、HCC1954 的 ONT CRAM 來自 [CASTLE panel](https://github.com/CASTLE-Panel/castle) Release 1（SRA BioProject PRJNA1086849）。
  - 下載來源是 Google mirror `brain-genomics-public/publications/park2024_deepsomatic`，見 `/big8_disk/Google_somatic_data/urls.txt`。
  - H1437／H2009 的 header 顯示是 R10.4.1、Guppy sup；tumor run 日期是 2023-01-17。它們對應 SRR28305180 和 SRR28305173。
  - 本機沒有 CASTLE Release 2 的 semi-UL E821 資料。
- COLO829 不屬於 CASTLE。本機的 ONT_R10 和 ONT_PAO 的來源尚未核對。

## 純度標籤口徑

`tX_nY` 表示 tumor/normal 的 target-depth components；下表的百分比是
**nominal/design tumor fraction**：

```text
nominal fraction = X / (X + Y)
```

這不是從 alignment 實際量測出的 realized tumor DNA fraction，也不是 cellular
purity ground truth。`t00_n25` 是純 normal baseline，不是腫瘤樣本。

## 六種細胞株

subsample 檔案命名規則：`<subsample path>/<purity label>/<line>_<purity label>.cram`（index 是 `.cram.crai`）。唯一例外是 COLO829 ONT_PAO 的 `t33_n00`，見下方說明。

### HCC1395

- 癌症類型：乳腺癌（ductal carcinoma）
- 原始 tumor／normal CRAM：
  - ONT：`/big8_disk/data/HCC1395/ONT/HCC1395.cram`、`HCC1395BL.cram`
  - ONT_Dorado：`/big8_disk/Google_somatic_data/bams/HCC1395/HCC1395_Tumor_ONT.GRCh38.sorted.cram`、`HCC1395_Normal_ONT.GRCh38.sorted.cram`。`ONT_Dorado/` 底下的 `.bam` symlink 已失效。同一目錄另有 `HCC1395_Tumor_ONT.50x.GRCh38.sorted.cram`。
  - ONT_5khz_simplex_5mCG_5hmCG：`/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.cram`、`HCC1395BL.cram`
- `subsample` 路徑：
  - `/big8_disk/data/HCC1395/ONT/subsample/`
  - `/big8_disk/data/HCC1395/ONT_Dorado/subsample/`
- 純度種類：
  - ONT：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
  - ONT_Dorado：`t00_n25`（0%）、`t7_n29`（19.4%）、`t19_n29`（39.6%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）

### COLO829

- 癌症類型：黑色素瘤（melanoma）
- 原始 tumor／normal CRAM：
  - ONT_R10：`/big8_disk/data/COLO829/ONT_R10/COLO829.cram`、`COLO829BL.cram`
  - ONT_PAO：`/big8_disk/data/COLO829/ONT_PAO/PAO29420.cram`（tumor），以及 `PAO33946.cram`（normal COLO829BL，依 `info.txt`）
- `subsample` 路徑：
  - `/big8_disk/data/COLO829/ONT_R10/subsample/`
  - `/big8_disk/data/COLO829/ONT_PAO/subsample/`
- 純度種類：
  - ONT_R10：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
  - ONT_PAO：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t33_n8`（80.5%）、`t33_n00`（100%）
- 注意：ONT_PAO 的 `t33_n00` 沒有 CRAM，只有一個失效的 BAM symlink（原本指向完整的 `PAO29420.bam`）。100% 樣本要改用 `/big8_disk/data/COLO829/ONT_PAO/PAO29420.cram`。

### H1437

- 癌症類型：肺腺癌（lung adenocarcinoma）
- 原始 tumor／normal CRAM：`/big8_disk/Google_somatic_data/bams/H1437/H1437_{Tumor,Normal}_ONT.GRCh38.sorted.cram`。`/big8_disk/data/H1437/ONT/H1437.bam` 已失效。
- `subsample` 路徑：`/big8_disk/data/H1437/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）

### H2009

- 癌症類型：肺腺癌（lung adenocarcinoma）
- 原始 tumor／normal CRAM：`/big8_disk/Google_somatic_data/bams/H2009/H2009_{Tumor,Normal}_ONT.GRCh38.sorted.cram`。`/big8_disk/data/H2009/ONT/H2009.bam` 已失效。
- `subsample` 路徑：`/big8_disk/data/H2009/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t8_n30`（21.1%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）

### HCC1937

- 癌症類型：乳腺癌（BRCA1-mutant label；特定 provenance 仍需外部確認）
- 原始 tumor／normal CRAM：`/big8_disk/Google_somatic_data/bams/HCC1937/HCC1937_{Tumor,Normal}_ONT.GRCh38.sorted.cram`。`/big8_disk/data/HCC1937/ONT/HCC1937.bam` 已失效。
- `subsample` 路徑：`/big8_disk/data/HCC1937/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t6_n26`（18.8%）、`t17_n26`（39.5%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）

### HCC1954

- 癌症類型：乳腺癌
- 原始 tumor／normal CRAM：`/big8_disk/Google_somatic_data/bams/HCC1954/HCC1954_{Tumor,Normal}_ONT.GRCh38.sorted.cram`。`/big8_disk/data/HCC1954/ONT/HCC1954.bam` 已失效。
- `subsample` 路徑：`/big8_disk/data/HCC1954/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）

## 來源與範圍

- Current inventory：2026-10-15 重新盤點 `/big8_disk/data/` 與 `/big8_disk/Google_somatic_data/bams/` 的目錄、檔名和 symlink 狀態；CRAM reference 取自 `samtools view -H`。
- 癌症類型與六樣本範圍：`/big8_disk/liaoyoyo2001/Knowledge/02_samples/cancer-samples.md`。
- 純度標籤定義：`/big8_disk/liaoyoyo2001/Knowledge/02_samples/subsample-purity.md`。
- `/big8_disk/data/colo829_nygc/` 的 COLO829 NYGC 資料是額外的 Illumina 外部驗證資料，不另列為第七種細胞株。

## PhyClone Benchmarking 資料集

- 根目錄：`/big8_disk/boyu114/phyclone_dataset/`
- 內容：PhyClone 論文 benchmarking 用的模擬資料與 HGSOC 真實資料，包含 ground truth、各方法輸入檔與輸出結果。官方說明見該目錄的 `README.md`。
- 完整性：每個 `.tar.gz` 都已解壓到同名目錄；2026-10-15 執行 `md5sum -c md5.txt`，9 個檔案全部 `OK`。
- 執行狀態：2532 個 trial 的 `program_outputs/phyclone_outliers/exit.status` 全部是 `PASS`。

### 目錄結構

```text
<Dataset>/data_archive/<Trial>/
├── ground_truth/       # tree.json 必定存在，其他 truth 檔依資料集不同
├── program_inputs/     # 各方法的輸入，例如 phyclone_outliers/data.tsv、clusters.tsv.gz
└── program_outputs/    # 各方法的輸出，包含 exit.status（Pass/Fail）與 tree.json
```

- 比較的方法：`phyclone_outliers`、`pairtree`、`orchard`、`fastBE`、`conipher`、`pyclone-vi`。`TSSB_Low` 另外有 `phylowgs`。`FS-CRP_Loss` 只有 `phyclone_naive` 與 `phyclone_outliers`。
- PhyClone 輸入 `data.tsv` 的欄位：`mutation_id, sample_id, ref_counts, alt_counts, major_cn, minor_cn, normal_cn, tumour_content, chrom`（HGSOC 另外有 `coord, cluster_id`）。cluster 輸入檔是 `clusters.tsv.gz`，HGSOC 的對應檔案是 `results.tsv`。
- PhyClone 輸出：`results.tsv`、`topology_report.tsv`、`tree.nwk`、`tree.json`。

### 資料集一覽

| 資料集 | Trials | 解壓大小 | 參數設計（從 trial 名稱解析） | Ground truth 檔案 |
|---|---:|---:|---|---|
| `FS-CRP_Loss` | 300 | 444M | `loss_prop_{0.0,0.1,0.2}_run{0..99}`，每個 loss proportion 100 runs | `data.tsv`、`loss_dict.json`、`loss_tree.pdf`、`tree.json` |
| `TSSB_High` | 400 | 15G | `S{2,4,8,16}_D1000_M10000_run{0..99}` | `down_sampled_data.tsv`、`tree.json` |
| `TSSB_Low` | 500 | 3.2G | `S{2,4,8,16,128}_D1000_M100_run{0..99}` | `down_sampled_data.tsv`、`tree.json` |
| `Pairtree` | 576 | 14G | `sim_K{3,10,30,100}_S*_T{50,200,1000}_M*_run{1..4}`，共 144 個設定 × 4 runs | `*.truth.pickle`、`truth.pdf`、`tree.json` |
| `CONIPHER_Noise` | 150 | 525M | `LTXSIM001`–`LTXSIM150` | `*_treeedges.tsv`、`*_full_truth_with_mut_id.tsv`、`tree.json` |
| `CONIPHER_No-Noise` | 150 | 507M | `LTXSIM001`–`LTXSIM150` | 同上 |
| `Copy_Number_Error` | 450 | 1.8G | `LTXSIM{001..150}_error_{0.0,0.1,0.2}` | `*_perturbed.tsv`、`*.tsv`、`*_treeedges.tsv`、`tree.png`、`tree.json` |
| `HGSOC` | 6 | ~76M | `p{2,3,9}_wgs`（WGS）與 `p{2,3,9}_wgs_t`（WGS + targeted） | `data.tsv`、`results.tsv`、`ground_truth_coloured.png`、`tree.json` |

參數縮寫只依目錄名稱判讀，正式定義要以 PhyClone 論文為準：`S` 是 sample 數，`K` 是 clone／subclone 數，`T` 是 read depth，`M` 是 mutation 數，`D` 依 TSSB 命名推測是 depth。Pairtree 的 `S` 範圍會隨 K 改變：K3／K10 用 {1,3,10,30,100}，K30／K100 用 {10,30,100}。M 則依 K 取 3 個值，例如 K10 用 {100,200,1000}。

### HGSOC 樣本

| Patient | Samples（sites） | Mutations |
|---|---|---:|
| p2 | `omentum_site_1/2`、`right_ovary_site_1/2`（4） | 5060 |
| p3 | `adnexa_site_1`、`omentum_site_1`、`right_ovary_site_1/2`（4） | 2882 |
| p9 | `left_ovary_site_1/2`、`omentum_site_1/2`、`right_ovary_site_1`（5） | 2014 |

`_wgs` 與 `_wgs_t` 的 mutation 和 sample 集合相同，但 `data.tsv` 內容不同。推測 `_wgs_t` 的 read counts 來自 targeted deep sequencing，這點尚未逐欄比對確認。

#### HGSOC `ground_truth/` 的來源（已確認）

結論：這棵樹是**單細胞資料加 bulk 資料推論出來的 reference tree**。PhyClone 論文把它當真值用，但它不是觀測到的細胞譜系。來源是 McPherson 2016（PhyClone 主文 §2.4.1.5、Fig.6），只涵蓋病人 2、3、9。細節見 `research/literature/papers/R01_mcpherson_hgsoc_2016/README.md`。

**Single-nucleus targeted PCR 做了什麼**

- 用 FACS 把細胞核一顆一顆分到不同孔，不做全基因組擴增。
- 每顆細胞核只對 48–96 個事先挑好的位點做 PCR，再用 MiSeq 定序。位點包含：
  - 區分 clone 的 SNV：從 bulk 推出的 PyClone cluster 中抽。
  - ancestral SNV：標示腫瘤細胞。
  - germline 異型合子 SNP：標示正常細胞。
  - breakpoint：人工挑選。
- 它提供的資訊：**每顆細胞核在這幾十個位點上，有沒有帶突變**。SCG 依這些 genotype 把細胞核分成 clone。

**為什麼不能說「真值樹來自單細胞定序」**

1. **位點少，而且是用 bulk 挑的。** 單細胞只測了 47–95 個可用位點，大部分 truth SNV 從沒在單細胞中測過。位點挑選條件是「bulk 推論為 informative 的 cluster」，所以樹天生偏向 bulk 已經看得到的結構。
2. **樹是模型推出來的，不是直接讀出來的。**
   - SCG 先分群。
   - 再把 SNV 併回 bulk 的 PyClone cluster，二值化成 cluster 層級的有無。
   - 用 WGS 的 bulk SNV 數加權 stochastic Dollo likelihood，選出最佳樹。
   - 最後人工標註 germline SNP 與 breakpoint。
3. **truth SNV 的節點歸屬由 bulk 決定。** 每個 SNV 掛在哪個節點，由 bulk deep-seq 的 PyClone cluster 加上單細胞的 cluster-level genotype 共同決定。PhyClone 對 HGSOC 又使用同源的 cluster 當輸入，所以評估不完全獨立。
4. **只看得到大 clone。** 只有 ≥10 顆細胞核的 clone 進入建樹，rare clone 看不到。單細胞 PCR 的 allelic dropout 由 SCG 的模型吸收，沒有獨立量化。

正確說法：「樹由單細胞定序加 bulk 資料推論，論文拿來當真值用。」

## SMC-Het（DREAM）資料集

- 根目錄：`/big8_disk/boyu114/smchet_dataset/`（解壓後共約 25G）
- 來源：Synapse 專案 `syn2813581`，2026-10-18 下載。對應論文見 `research/literature/papers/M07_smchet_benchmark_2024/`。
- 內容：SMC-Het DREAM Challenge 的模擬腫瘤。每個腫瘤是 **單一 bulk short-read sample**，附 SNV VCF、Battenberg CN、purity／ploidy 與 truth files。
- 完整性：2026-10-20 執行 `md5sum -c md5.txt`，13 個檔案全部 `OK`。`md5.txt` 的值取自 Synapse 的檔案 metadata。
- 解壓：2026-10-20 完成。每個 `.tar.gz` 都已解壓，規則如下：
  - 壓縮檔內已有頂層目錄（`Tumour1–7`）：直接解壓在根目錄。
  - 壓縮檔內沒有頂層目錄：解壓到同名目錄。例外是 `battenberg_files.tar.gz`，它在 2026-10-18 解壓到 `battenberg/`。
- 本機沒有 BAM。metadata 的 `EGA_FileName` 欄指向 EGA 受控存取資料。

### 目錄結構

```text
smchet_dataset/
├── truthFiles/<Tumour>-noXY/          # 51 個 scored 腫瘤，每個 11 個檔
├── truthfilesDownsampled/single_caller/  # T2–T6 downsampled × caller 的 truth
├── downsampled_vcfs/                  # T2–T6 downsampled 的 caller VCF（125 個）
├── downsampled_battenberg/            # T2–T6 downsampled 的 Battenberg refit
├── battenberg/                        # 51 個腫瘤的 Battenberg 與 cellularity_ploidy
├── Tumour{1,2,3,4,6,7}/               # training 腫瘤（沒有 Tumour5、Tumour8）
├── Tumour_metadata_final.tsv          # 57 列 metadata
├── signatures.txt、input_trinucleotide_signatures.txt
└── md5.txt、*.tar.gz                  # 原始壓縮檔保留
```

### 每個腫瘤的檔案（`truthFiles/<T>-noXY/` 與 `Tumour*/` 格式相同）

| 檔案 | 內容 |
|---|---|
| `*.mutect.vcf` | 輸入 SNV（MuTect call） |
| `*.battenberg.txt` | Battenberg CN segment。subclonal segment 有第二組 `nMaj2_A/nMin2_A/frac2_A` |
| `*.cellularity_ploidy.txt` | purity（cellularity）與 ploidy |
| `*.truth.1A.txt` | 真實 purity |
| `*.truth.1B.txt` | 真實 cluster 數 |
| `*.truth.1C.txt` | 每個 cluster 一列：`cluster_id`、SNV 數、cellular prevalence |
| `*.truth.2A.txt` | 每個 SNV 的 cluster 指派（一行一個 SNV） |
| `*.truth.2B.gz` | SNV × SNV co-clustering 矩陣 |
| `*.truth.3A.txt` | 樹：每列 `cluster_id parent_id`，`0` 是 root |
| `*.truth.3B.gz` | SNV × SNV ancestor-descendant 矩陣 |
| `*.truth.scoring_vcf.vcf` | 評分用 VCF |

以 `Tumour1` 為例：1A = 0.70，cellularity 檔 = 0.7107，1B = 4。1C 第一列 cluster 1 的 CP 等於 purity（0.70），所以 1C 的 CP 是 **含 purity 的 cellular prevalence，不是 CCF**。1C 另有一列 CP = 0 的 cluster 5（509 個 SNV），但 2A 沒有指派到 cluster 5。推測 cluster 5 是 false-positive SNV，尚未對照官方評分程式確認。

### 腫瘤清單

| 類別 | 腫瘤 | 數量 | 說明 |
|---|---|---:|---|
| PCAWG-based | `P1`–`P25` | 25 | PCAWG 腫瘤的模擬 |
| 已發表腫瘤 | `T0`–`T16` | 17 | 模擬自已發表研究（Nik-Zainal、Gundem、Bolli 等） |
| 特殊案例 | `S2`–`S10` | 9 | 例如兩群難分（85:15）、overdispersed、caller 漏掉 rare subclone |
| Training | `Tumour1–4,6,7` | 6 | 不屬於 51 個 scored 腫瘤 |

- 51 個 scored 腫瘤的 truth 數量和論文一致。所有來源都找不到 `S1`。
- `Tumour_metadata_final.tsv` 有 49 列 scored 腫瘤。它缺 `T7` 和 `S9`，但這兩個都有 truth 與 Battenberg 檔。
- 51 個 scored 腫瘤的真實 cluster 數（1B）：2 個 cluster 有 3 例，3 個有 21 例，4 個有 18 例，5 個有 9 例。

### Downsampled 子集

- 腫瘤：`T2`–`T6`。深度：8X、16X、32X、64X、128X。另有 `full_depth` 的 Battenberg（只在 `downsampled_battenberg/`）。
- `downsampled_vcfs/`：5 種 caller（`mutect`、`Strelka`、`somaticsniper`、`mutationseq`、`perfect`）× 5 腫瘤 × 5 深度 = 125 個 VCF。
- `downsampled_battenberg/`：每個腫瘤 × 深度一組 `refit_cellularity_ploidy` 與 `refit_subclones_noXY`。T5、T6 沒有 128X。
- `truthfilesDownsampled/single_caller/`：`MuTect`、`Strelka`、`somaticsniper`、`mutationseq` 各 25 組，加上 `T6_128_perfect` 1 組。
  - `mutationseq_T5.T.8X` 只有 1A–2B，缺 3A、3B、scoring_vcf。
  - `gmon.out` 是 profiler 殘檔，不是資料。

### 和本研究的關係

- 這是單一樣本 bulk 資料。它可以測 PhyClone 在 single-sample 下的表現，也可以測 subclonal CN 對 PhyClone 的影響。
- 它沒有 long read，也沒有 haplotype／phasing 資訊。
- PhyClone 每個 SNV 只接受一組 `major_cn/minor_cn`。轉換 Battenberg 時，要決定 subclonal segment（`frac1_A < 1`）的處理方式。
