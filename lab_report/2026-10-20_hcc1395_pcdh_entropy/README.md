# HCC1395 PCDH methylation barcode entropy 檢查（2026-10-20）

## 結論

HCC1395 tumor 的 PCDH 區幾乎整區高甲基化，10-CpG barcode 多樣性大多消失。兩批 basecalling 不同的 ONT 資料（Dorado、5khz simplex）結果一致，所以不是平台造成的。PCDH barcode 不適合當 HCC1395 的主要建樹特徵。只有少數中間甲基化的 window 可以當輔助驗證。

## 問題

B09（Hackett … Blundell 2026）用 PCDH 區的 per-read CpG pattern 當 lineage barcode。B09 README 列了一個未驗證風險：癌細胞可能讓 PCDH 整區高甲基化。本實驗用本地 ONT 資料檢查 HCC1395 的 PCDH barcode 是否仍有多樣性。

## 資料

| 標籤 | CRAM | 說明 |
|---|---|---|
| `t50_n00` | `/big8_disk/data/HCC1395/ONT_Dorado/subsample/t50_n00/HCC1395_t50_n00.cram` | nominal 100% tumor（design fraction，不是實測 purity） |
| `t00_n25` | `/big8_disk/data/HCC1395/ONT_Dorado/subsample/t00_n25/HCC1395_t00_n25.cram` | 純 normal baseline（HCC1395BL） |

- reference：`/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`
- 區域：`chr5:140,780,000-141,520,000`（PCDHA1 到 PCDHGC5，GRCh38 約略座標，沒有跑 liftOver 驗證），共 13,104 個 CpG。

## 做法

腳本：`tools/pcdh_entropy.py`。

```bash
python3 tools/pcdh_entropy.py <CRAM> <LABEL> <OUT_TSV>
```

1. 只取 primary、MAPQ ≥ 20 的 read。
2. 用 pysam 讀 MM/ML tag（5mC，`C+m?`）。沒有列出 call 的 CpG 算缺值。minus strand 的 call 對回 CpG 的 C 位置。
3. call 判定：機率 ≥ 0.8 算甲基化（1），≤ 0.2 算未甲基化（0），中間算缺值。
4. 把 CpG 依序切成不重疊的 10-CpG window。每條 read 必須 10 個 CpG 都有 call，才算一個 barcode。
5. window 至少要有 20 條完整 read。每次隨機抽 20 條算 Shannon entropy（bits，上限 10），重複 20 次取平均。這樣可以消除兩檔深度不同的影響。
6. 另外記錄 window 平均甲基化，以及最常見 barcode 的比例。

沒有 modkit 與 longphase，所以沒有分 haplotype。

## 結果

| 指標 | t50_n00 tumor | t00_n25 normal |
|---|---|---|
| 可用 read 數 | 4,839 | 2,267 |
| 可用 window 數 | 1,197 | 239 |
| window 平均甲基化（中位數） | 0.98 | 0.66 |
| entropy 中位數（IQR），bits | 0.57（0.23–1.43） | 2.57（1.99–3.10） |
| entropy ≤ 1 bit 的 window | 757（63%） | 8（3%） |
| entropy ≥ 3 bits 的 window | 54（5%） | 72（30%） |

兩檔共有 238 個 window：
- entropy 中位數：tumor 0.44，normal 2.57 bits。
- tumor 比 normal 低的 window：229 / 238。差值中位數 −1.97 bits。
- 平均甲基化中位數：tumor 0.99，normal 0.66。

tumor 依 window 平均甲基化分組：

| 平均甲基化 | window 數 | entropy 中位數（bits） |
|---|---|---|
| 0.0–0.2 | 50 | 0.50 |
| 0.2–0.4 | 7 | 1.93 |
| 0.4–0.6 | 24 | 3.10 |
| 0.6–0.8 | 60 | 2.97 |
| 0.8–1.0 | 942 | 0.61 |

## 解讀（分析推論）

- tumor 大部分 window 接近全甲基化，entropy 接近 0。主要現象是高甲基化。
- cell line 本來就是 clonal。所以 entropy 降低一部分來自 clonality，不全是高甲基化。本實驗分不出兩者各占多少。
- tumor 約有 84 個 window 的平均甲基化在 0.4–0.8，entropy 約 3 bits。它們是候選的可用 window，但有兩個混淆因素：
  - 沒分 haplotype。HP1 與 HP2 的 barcode 不同時，會多出約 1 bit。
  - call 錯誤會提高 entropy。全甲基化 window 仍有約 0.6 bits，大致代表錯誤造成的基線。

## 定序平台與 call 校準檢查

問題：tumor 與 normal 的定序或 methylation calling 不同時，甲基化差異可能來自平台，不是生物。

header 比對（`@PG`；兩檔都沒有 `@RG`）：

| 項目 | t50_n00 tumor | t00_n25 normal |
|---|---|---|
| 來源 | `Google_somatic_data/.../HCC1395_Tumor_ONT.GRCh38.sorted.cram` | `.../HCC1395_Normal_ONT.GRCh38.sorted.cram` |
| flowcell | PAK70131（2023-03-17）、PAO34127、PAO32353（2023-03-23） | PAK63384（2023-03-17） |
| alignment | minimap2 2.26，`-ax map-ont -k 17 -y --eqx` | 相同 |
| read tag | `MM`（`C+m?`）、`ML` 與其他 tag 相同 | 相同 |
| basecaller／modification model | 沒有記錄 | 沒有記錄 |

call 分布對照（腳本 `tools/meth_call_control.py`；ML ≥ 204 算甲基化，≤ 50 算未甲基化）：

| 區域 | tumor 甲基化比例 | normal 甲基化比例 | tumor 中間 call（51–203） | normal 中間 call |
|---|---|---|---|---|
| PCDH | 0.891 | 0.501 | 1.7% | 1.9% |
| GAPDH promoter（`chr12:6,533,500-6,535,000`） | 0.003 | 0.003 | 1.2% | 1.1% |
| ACTB promoter（`chr7:5,529,000-5,531,000`） | 0.021 | 0.004 | 0.7% | 0.6% |

解讀：
- 兩個 housekeeping promoter 在兩檔都接近 0。中間 call 的比例也相近。沒有看到整體校準偏移。
- 所以 PCDH 的差異（0.89 對 0.50）不太可能來自平台。
- 這不能完全排除平台差異：basecaller 版本不明；tumor 多了 2 個較晚的 PAO flowcell；只檢查了 2 個 promoter。

## 跨批次重現：ONT_5khz_simplex_5mCG_5hmCG

目的：用 basecalling 不同的另一批資料重跑，排除平台因素。

資料：`/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.cram`（tumor）、`HCC1395BL.cram`（normal）。全深度，沒有 subsample。每個 CpG 同時有 5mC（`C+m?`）與 5hmC（`C+h?`）機率。

跑兩種設定：
- `m`：只用 5mC，和 Dorado 批相同。
- `m,h`：5mC 加 5hmC 機率。EM-seq 與 bisulfite 分不出兩者，所以這個設定較接近 B09 的讀法。

```bash
python3 tools/pcdh_entropy.py <CRAM> <LABEL> <OUT_TSV> m      # 或 m,h
python3 tools/meth_call_control.py <CRAM>
```

| 資料 | window 數 | 平均甲基化中位數 | entropy 中位數（IQR），bits | ≤ 1 bit | ≥ 3 bits |
|---|---|---|---|---|---|
| Dorado tumor（t50_n00） | 1,197 | 0.98 | 0.57（0.23–1.43） | 63% | 5% |
| Dorado normal（t00_n25） | 239 | 0.66 | 2.57（1.99–3.10） | 3% | 30% |
| 5khz tumor，`m` | 1,004 | 0.96 | 1.11（0.62–1.80） | 46% | 5% |
| 5khz normal，`m` | 607 | 0.45 | 2.52（1.94–2.92） | 6% | 18% |
| 5khz tumor，`m,h` | 1,190 | 0.99 | 0.39（0.11–1.32） | 69% | 2% |
| 5khz normal，`m,h` | 570 | 0.75 | 2.23（1.65–2.69） | 10% | 10% |

同批 tumor 對 normal（共有 window）：

| 設定 | 共有 window | tumor 較低 | entropy 差中位數 |
|---|---|---|---|
| 5khz `m` | 521 | 417（80%） | −1.25 bits |
| 5khz `m,h` | 559 | 502（90%） | −1.56 bits |

兩批之間（逐 window Pearson r）：

| 比對 | 共有 window | r（平均甲基化） | r（entropy） |
|---|---|---|---|
| Dorado tumor 對 5khz tumor `m` | 971 | 0.99 | 0.86 |
| Dorado normal 對 5khz normal `m` | 140 | 0.98 | 0.76 |

tumor 中間甲基化 window（0.4–0.8）：Dorado 84 個，5khz `m` 91 個，重疊 68 個。

call 校準（`5khz_*.call_control.txt`）：
- housekeeping promoter 的甲基化比例：GAPDH tumor 0.002、normal 0.005；ACTB tumor 0.017、normal 0.002。和 Dorado 批相近。
- 5khz 批的 ML 51–101 call 比 Dorado 批多（promoter 約 10–17%，Dorado 約 0.5%）。這是兩批的校準差異。它增加缺值，但 tumor 與 normal 受到相同影響。

解讀（分析推論）：
- 換一批 basecalling，tumor 仍是高甲基化、低 entropy。逐 window 的甲基化在兩批幾乎一致（r = 0.99）。所以主結論不是平台造成的。
- 5khz tumor 只用 `m` 時 entropy 較高（1.11）。加上 `h` 後降到 0.39。推論：這個 model 把部分甲基化 CpG 分給 5hmC，使只看 `m` 的 barcode 多出假變化。
- 中間甲基化 window 在兩批有 68 個重疊。這些 window 較可能是真實訊號，可以列為後續分 haplotype 的候選。

## 限制

- Dorado 批的 basecaller 與 modification model 版本沒有記錄。5khz 批也沒有 `@RG`。
- 沒有 HP tag，沒有分 haplotype。
- normal 只有 239 個 window 通過門檻。比較只限 238 個共有 window，可能有選擇偏差。
- PCDH 的 GRCh38 範圍是約略值。
- normal 是 lymphoblastoid cell line，本身可能是寡克隆。它的 entropy 不能當 polyclonal 組織的上限。
- 只做 HCC1395 一株。

## 下一步

1. 對 H1437 等其他 cell line 跑同一支腳本，看高甲基化是不是 HCC1395 才有。
2. 安裝 longphase 後做 haplotag，對 84 個中間甲基化 window 分 HP 重算 entropy。

## 檔案

| 檔案 | 內容 |
|---|---|
| `HCC1395_t50_n00.pcdh_windows.tsv` | tumor 逐 window 結果 |
| `HCC1395_t00_n25.pcdh_windows.tsv` | normal 逐 window 結果 |
| `5khz_HCC1395{,BL}.{m,mh}.pcdh_windows.tsv` | 5khz 批 tumor／normal，`m` 與 `m,h` 兩種設定 |
| `5khz_HCC1395{,BL}.call_control.txt` | 5khz 批 call 校準對照 |

欄位：`label`、`win_start`／`win_end`（window 第一個與最後一個 CpG 的 0-based 座標）、`n_reads`（完整 read 數）、`mean_meth`、`entropy_sub20`、`n_distinct_sub20`（抽 20 條時的不同 barcode 數）、`top_barcode_frac`。
