# H1437 PCDH barcode entropy 分 HP 重算（2026-10-20）

## 結論

分 haplotype 後，H1437 tumor 的 PCDH barcode entropy 只降約 0.1–0.2 bits，同一條 haplotype 內仍保留高多樣性。所以先前「tumor entropy 比 normal 高」主要不是 HP1、HP2 混在一起造成的。

另外有兩個新發現：

- tumor 的 HP1 與 HP2 read 數約 1.9：1，normal 約 1：1。tumor 在 PCDH 區有 allelic imbalance。
- PCDH 低甲基化主要在 HP1：tumor HP1 0.54，normal HP1 0.81。HP2 只從 0.86 降到 0.77。

這些多樣性是否帶有 clone 結構，本實驗還不能判斷（見「解讀」）。

## 問題

H1437 是 5 株中保留 PCDH barcode 多樣性的一株（`lab_report/2026-10-20_pcdh_entropy_panel/`）。之前沒有分 haplotype，HP1 與 HP2 的 barcode 混在一起計算。本實驗分 HP 重算，看多樣性是否只來自 haplotype 混合。

## 資料

| 用途 | 檔案 |
|---|---|
| germline het SNP 來源 | `/big8_disk/data/H1437/ONT/subsample/t50_n00/ClairS_TO_v0_3_0/snv.vcf` |
| phasing 用 read | `/big8_disk/data/H1437/ONT/subsample/t50_n00/H1437_t50_n00.cram` |
| haplotag 與 entropy（主結果，全深度） | `/big8_disk/Google_somatic_data/bams/H1437/H1437_{Tumor,Normal}_ONT.GRCh38.sorted.cram` |
| haplotag 與 entropy（第一次試跑） | `/big8_disk/data/H1437/ONT/subsample/{t50_n00,t00_n25}/*.cram` |

`t50_n00` 是 nominal 100% tumor（design fraction，不是實測 purity）。

## 做法

### 1. phasing 與 haplotag

```bash
tools/pcdh_haplotag.sh <ClairS-TO snv.vcf> <PHASE_CRAM> <OUT_DIR> \
  <TUMOR_CRAM>:full_tumor <NORMAL_CRAM>:full_normal
```

1. 從 ClairS-TO `snv.vcf` 取 `NonSomatic`、AF 0.2–0.8 的位點，GT 改成 `0/1`。範圍是 `chr5:139.5–142.8 Mb`，加 flank 是為了讓 phasing 連成一整段。
   - ClairS-TO 的 GT 不可靠。例如 AF 0.98 的位點被標成 `0/1`，所以改用 AF 判斷。
2. `longphase-s phase --ont`（`/bip8_disk/boyu114/longphase-s-origin`，v1.0.0）。
3. `longphase-s haplotag -q 20 --region chr5:140780000-141520000`，對 tumor 與 normal 用同一份 phased VCF。這樣 tumor 與 normal 的 HP1 指的是同一條 haplotype。

### 2. 分 HP 算 entropy

```bash
python3 tools/pcdh_entropy.py <TAGGED_BAM> <LABEL> <OUT_TSV> m --by-hp
python3 tools/pcdh_hp_compare.py <TSV ...> <TUMOR_LABEL> <NORMAL_LABEL>
```

- `--by-hp` 依 HP tag 分組。沒有 HP tag 的 read 不計入。
- 其餘設定和之前相同：10-CpG window，每個 window 抽 20 條完整 read，只用 5mC。
- 這是借自 B09 短讀做法的 10-mer 指標，不是 B09 的 long-read 做法。差異見 `lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md`「做法」一節。long-read 做法見 `lab_report/2026-10-21_h1437_pcdh_longread_matrix/`。
- 不加 `--by-hp` 時，新版腳本的輸出和舊版完全相同（已用 H1437 `t00_n25` 驗證）。
- tagged BAM 不分 HP 的結果，也和原 CRAM 的結果完全相同。

## 結果

### phasing 品質

| 項目 | 數值 |
|---|---|
| het SNP（含 flank） | 1,875 |
| phased SNP | 1,858 |
| PCDH 區內 phased SNP | 577 |
| PCDH 區的 PS block | 1 個（PS 140729939，覆蓋整區） |

PCDH 區 `NonSomatic` 位點的 AF：0.2–0.8 有 581 個，≥ 0.9 有 246 個。AF 0.2–0.8 的位點分布在整區，所以沒有看到 LOH。AF 峰值在 0.6–0.7。

### HP read 數

| 資料 | HP1 | HP2 | 沒有 HP | HP1：HP2 |
|---|---|---|---|---|
| tumor 全深度 | 1,355 | 708 | 431 | 1.9：1 |
| normal 全深度 | 623 | 572 | 225 | 1.1：1 |
| tumor `t50_n00` | 859 | 474 | 269 | 1.8：1 |
| normal `t00_n25` | 295 | 293 | 118 | 1.0：1 |

### 全深度 entropy

| 組別 | window 數 | 甲基化中位數 | entropy 中位數（IQR），bits | ≤ 1 bit | ≥ 3 bits |
|---|---|---|---|---|---|
| tumor 不分 HP | 1,204 | 0.49 | 2.95（2.16–3.46） | 7% | 48% |
| tumor HP1 | 1,007 | 0.54 | 2.74（1.98–3.33） | 9% | 40% |
| tumor HP2 | 205 | 0.72 | 2.35（1.65–2.96） | 11% | 23% |
| normal 不分 HP | 1,044 | 0.69 | 2.80（2.09–3.38） | 6% | 41% |
| normal HP1 | 231 | 0.81 | 2.12（1.29–2.84） | 18% | 19% |
| normal HP2 | 290 | 0.83 | 2.31（1.39–2.94） | 15% | 24% |

共有 window 的比較（entropy 中位數；差值是逐 window 差的中位數）：

| 比較 | 共有 window | entropy | 差值 | 甲基化 |
|---|---|---|---|---|
| tumor HP1 對 tumor 不分 HP | 1,007 | 2.74 對 2.92 | −0.09 | 0.54 對 0.52 |
| tumor HP2 對 tumor 不分 HP | 205 | 2.35 對 2.68 | −0.19 | 0.72 對 0.74 |
| normal HP1 對 normal 不分 HP | 231 | 2.12 對 2.48 | −0.25 | 0.81 對 0.81 |
| normal HP2 對 normal 不分 HP | 290 | 2.31 對 2.62 | −0.26 | 0.83 對 0.82 |
| HP1：tumor 對 normal | 212 | 2.73 對 2.16 | +0.46 | 0.54 對 0.81 |
| HP2：tumor 對 normal | 84 | 2.11 對 2.02 | +0.10 | 0.77 對 0.86 |

HP 內中間甲基化 window（0.4–0.8）：tumor HP1 379 個（entropy 3.29），tumor HP2 63 個（2.97），normal HP1 66 個（3.11），normal HP2 89 個（3.13）。

### subsample 試跑

`t50_n00`／`t00_n25` 的 read 太少。tumor HP2 只有 5 個 window，normal HP1 0 個、HP2 1 個，達到 20 條完整 read 的門檻。所以主結果改用全深度。試跑結果仍保存在 `H1437_{t50_n00,t00_n25}.byhp.pcdh_windows.tsv`。

## 解讀（分析推論）

- **haplotype 混合只解釋一小部分。** 分 HP 後，tumor entropy 只降約 0.1–0.2 bits，比預期的約 1 bit 少很多。normal 降約 0.25 bits。
- **tumor 多樣性集中在 HP1。** HP1 tumor 比 normal 高 0.46 bits，HP2 只高 0.10 bits。HP1 也是低甲基化較多、read 較多的一條。
- **HP1 read 多可能來自 copy number 增加。** HP1：HP2 約 1.9：1，AF 峰值也在 0.6–0.7，可能是 HP1 有 2 份、HP2 有 1 份（未驗證）。若成立，有一個重要混淆：同一個細胞內的兩份 HP1，甲基化可能各自漂移。這會讓 HP1 entropy 變高，但不代表有 subclone。
- **還不能說多樣性帶有 clone 結構。** 高 entropy 有 3 種可能：(1) subclone；(2) 同一細胞內多份 HP1 的差異；(3) 培養中 epimutation 隨機累積。要分辨，需要檢查同一條 read 在相鄰 window 的 barcode 是否一致分群。clone 結構會跨 window 保持一致，隨機 epimutation 不會。

## 限制

- 全深度的 tumor HP2 與 normal 各 HP，只有約 200–300 個 window，比較只限共有 window。
- het SNP 來自 tumor-only 的 ClairS-TO，沒有用 normal 的 germline caller。
- 沒有實測 PCDH 區的 copy number。1.9：1 只來自 read 數與 AF。
- 單一 PS block 是在 phasing 輸出中確認的。沒有用其他工具（例如 WhatsHap）交叉驗證 phasing。
- tagged BAM 沒有存進 repo，存在 repo 外（見「檔案」）。也可以用上方指令約 1 分鐘重建。

## 下一步

1. 做跨 window 一致性檢查：同一條 read 在相鄰 window 的分群是否一致。
2. 查 H1437 在 chr5q31 的 haplotype-specific CN，確認 HP1 是否有 2 份。
3. 對 HCC1954 做同樣的分 HP 檢查。

## 檔案

| 檔案 | 內容 |
|---|---|
| `H1437_pcdh_phased.vcf.gz` | longphase-s phased VCF（含 flank） |
| `H1437_{tumor,normal}_full.pcdh_windows.tsv` | 全深度、不分 HP |
| `H1437_{tumor,normal}_full.byhp.pcdh_windows.tsv` | 全深度、分 HP（label 結尾 `_HP1`／`_HP2`） |
| `H1437_{t50_n00,t00_n25}.byhp.pcdh_windows.tsv` | subsample 試跑，分 HP |
| `hp_compare.txt` | `tools/pcdh_hp_compare.py` 輸出 |

欄位定義同 `lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md`。

repo 外的檔案（`/big8_disk/boyu114/bam_save/h1437_pcdh_haplotag_2026-10-20/`，2026-10-21 存放）：

| 檔案 | 內容 |
|---|---|
| `H1437_tumor_full.PCDH.haplotag.bam`（55 MB） | 全深度 tumor，PCDH 區，有 HP／PS tag 與 MM／ML |
| `H1437_normal_full.PCDH.haplotag.bam`（36 MB） | 全深度 normal，同上 |
| `H1437_t50_n00.PCDH.haplotag.bam`（36 MB） | subsample 試跑 tumor |
| `H1437_t00_n25.PCDH.haplotag.bam`（18 MB） | subsample 試跑 normal |
| `H1437_pcdh_het_input.vcf` | 給 `phase` 的 het SNP（AF 0.2–0.8，GT 改成 `0/1`） |
| `H1437_pcdh_phased.vcf` | phased VCF（未壓縮，內容同 repo 內的 `.vcf.gz`） |

每個 BAM 旁邊都有 `.bai`。

## 相關實驗

- `lab_report/2026-10-20_h1437_pcdh_entropy/`：H1437 不分 HP 的初次檢查。
- `lab_report/2026-10-20_pcdh_entropy_panel/`：5 株比較。
