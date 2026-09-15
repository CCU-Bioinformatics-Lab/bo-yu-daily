# Tumor Cell-line BAM Sample Inventory

更新日期：2026-09-03

本文件整理目前 `/big8_disk/data/` 下六種主要 ONT 腫瘤細胞株的 BAM 路徑與
`subsample` 純度設計。盤點只使用檔案與資料夾名稱，沒有讀取 BAM 內容。

## 純度標籤口徑

`tX_nY` 表示 tumor/normal 的 target-depth components；下表的百分比是
**nominal/design tumor fraction**：

```text
nominal fraction = X / (X + Y)
```

這不是從 BAM 實際量測出的 realized tumor DNA fraction，也不是 cellular
purity ground truth。`t00_n25` 是純 normal baseline，不是腫瘤樣本。

## 六種細胞株

### HCC1395

- 癌症類型：乳腺癌（ductal carcinoma）
- 原始 tumor BAM：
  - `/big8_disk/data/HCC1395/ONT/HCC1395.bam`
  - `/big8_disk/data/HCC1395/ONT_Dorado/HCC1395.bam`
  - `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam`
- `subsample` 路徑：
  - `/big8_disk/data/HCC1395/ONT/subsample/`
  - `/big8_disk/data/HCC1395/ONT_Dorado/subsample/`
- 純度種類：
  - ONT：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
  - ONT_Dorado：`t00_n25`（0%）、`t7_n29`（19.4%）、`t19_n29`（39.6%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
- BAM 命名規則：`<subsample path>/<purity label>/HCC1395_<purity label>.bam`

### COLO829

- 癌症類型：黑色素瘤（melanoma）
- 原始 tumor BAM：
  - `/big8_disk/data/COLO829/ONT_R10/COLO829.bam`
  - `/big8_disk/data/COLO829/ONT_PAO/PAO29420.bam`
- `subsample` 路徑：
  - `/big8_disk/data/COLO829/ONT_R10/subsample/`
  - `/big8_disk/data/COLO829/ONT_PAO/subsample/`
- 純度種類：
  - ONT_R10：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
  - ONT_PAO：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t33_n8`（80.5%）、`t33_n00`（100%）
- BAM 命名規則：`<subsample path>/<purity label>/COLO829_<purity label>.bam`

### H1437

- 癌症類型：肺腺癌（lung adenocarcinoma）
- 原始 tumor BAM：`/big8_disk/data/H1437/ONT/H1437.bam`
- `subsample` 路徑：`/big8_disk/data/H1437/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
- BAM 命名規則：`/big8_disk/data/H1437/ONT/subsample/<purity label>/H1437_<purity label>.bam`

### H2009

- 癌症類型：肺腺癌（lung adenocarcinoma）
- 原始 tumor BAM：`/big8_disk/data/H2009/ONT/H2009.bam`
- `subsample` 路徑：`/big8_disk/data/H2009/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t8_n30`（21.1%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
- BAM 命名規則：`/big8_disk/data/H2009/ONT/subsample/<purity label>/H2009_<purity label>.bam`

### HCC1937

- 癌症類型：乳腺癌（BRCA1-mutant label；特定 provenance 仍需外部確認）
- 原始 tumor BAM：`/big8_disk/data/HCC1937/ONT/HCC1937.bam`
- `subsample` 路徑：`/big8_disk/data/HCC1937/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t6_n26`（18.8%）、`t17_n26`（39.5%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
- BAM 命名規則：`/big8_disk/data/HCC1937/ONT/subsample/<purity label>/HCC1937_<purity label>.bam`

### HCC1954

- 癌症類型：乳腺癌
- 原始 tumor BAM：`/big8_disk/data/HCC1954/ONT/HCC1954.bam`
- `subsample` 路徑：`/big8_disk/data/HCC1954/ONT/subsample/`
- 純度種類：`t00_n25`（0%）、`t10_n40`（20%）、`t20_n30`（40%）、`t30_n20`（60%）、`t40_n10`（80%）、`t50_n00`（100%）
- BAM 命名規則：`/big8_disk/data/HCC1954/ONT/subsample/<purity label>/HCC1954_<purity label>.bam`

## 來源與範圍

- Current inventory：`/big8_disk/data/` 的目錄與檔名盤點，狀態為 `current`。
- 癌症類型與六樣本範圍：`/big8_disk/liaoyoyo2001/Knowledge/02_samples/cancer-samples.md`。
- 純度標籤定義：`/big8_disk/liaoyoyo2001/Knowledge/02_samples/subsample-purity.md`。
- `/big8_disk/data/colo829_nygc/` 的 COLO829 NYGC BAM 是額外的 Illumina 外部驗證資料，不另列為第七種細胞株。
