# Tumor Cell-line Alignment Sample Inventory

更新日期：2026-10-15

本文件整理目前 `/big8_disk/data/` 下六種主要 ONT 腫瘤細胞株的 alignment 檔路徑與
`subsample` 純度設計。盤點只看檔案、資料夾名稱與 CRAM header，沒有讀取 read 內容。
文末另列 PhyClone 論文的 benchmarking 資料集（`/big8_disk/boyu114/phyclone_dataset/`）。

## 格式更新：BAM → CRAM（依 `.crai` mtime 推斷約在 2026-09-23～24）

- 所有 subsample，以及所有原始 tumor／normal 檔，都已轉成 **CRAM**（`.cram` + `.cram.crai`）。原本的 `.bam` 已刪除。
- CRAM reference：`/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`（header 的 `UR:`；`chr1` 的 `M5:6aef897c…`）。讀取時要用 `-T`／`--reference` 指定這個 fasta，或者確認 header 的 UR 路徑可以存取。
- **以下 symlink 已失效**（目標 BAM 已轉成 CRAM 並刪除），不要再使用：
  - `HCC1395/ONT_Dorado/HCC1395{,BL}.bam{,.bai}`
  - `H1437/ONT/H1437{,BL}.bam{,.bai}`、`H2009/ONT/H2009{,BL}.bam{,.bai}`
  - `HCC1937/ONT/HCC1937{,BL}.bam{,.bai}`、`HCC1954/ONT/HCC1954{,BL}.bam{,.bai}`
  - `COLO829/ONT_PAO/subsample/t33_n00/COLO829_t33_n00.bam{,.bai}`（指向 `../../PAO29420.bam`，該檔已不存在）
- 上面這些失效檔案，對應的 CRAM 在 `/big8_disk/Google_somatic_data/bams/<line>/<line>_{Tumor,Normal}_ONT.GRCh38.sorted.cram`。只有 COLO829 PAO t33_n00 的對應檔在 `/big8_disk/data/COLO829/ONT_PAO/PAO29420.cram`。

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

`_wgs` 與 `_wgs_t` 的 mutation 和 sample 集合相同，但 `data.tsv` 內容不同。推測 `_wgs_t` 的 read counts 來自 targeted deep sequencing，這點尚未逐欄比對確認。真實腫瘤資料沒有真正的演化樹，所以 `ground_truth/` 裡的樹應該是論文採用的 reference tree，來源要再回論文確認。
