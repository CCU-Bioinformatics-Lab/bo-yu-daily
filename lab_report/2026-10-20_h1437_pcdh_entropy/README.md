# H1437 PCDH methylation barcode entropy 檢查（2026-10-20）

## 結論

H1437 tumor 的 PCDH 區沒有高甲基化，和 HCC1395 相反。tumor 的甲基化反而比 normal 低，barcode entropy 也比 normal 高。所以高甲基化不是所有 cancer cell line 的共同現象，要逐株檢查。

H1437 的 barcode 仍有多樣性，但這些多樣性能不能反映 clone 結構，還沒有驗證（見「解讀」）。

## 問題

HCC1395（乳癌）的 PCDH 區幾乎整區高甲基化，barcode 多樣性大多消失（見 `lab_report/2026-10-20_hcc1395_pcdh_entropy/`）。本實驗檢查 H1437（肺腺癌）是否也一樣。

## 資料

| 標籤 | CRAM | 說明 |
|---|---|---|
| `t50_n00` | `/big8_disk/data/H1437/ONT/subsample/t50_n00/H1437_t50_n00.cram` | nominal 100% tumor（design fraction，不是實測 purity） |
| `t00_n25` | `/big8_disk/data/H1437/ONT/subsample/t00_n25/H1437_t00_n25.cram` | 純 normal baseline |

- 兩檔都從 Google somatic data 的 H1437 tumor／normal CRAM subsample 產生。
- MM tag 只有 5mC（`C+m?`），沒有 5hmC。
- 區域、reference 和 HCC1395 實驗相同：`chr5:140,780,000-141,520,000`，13,104 個 CpG。

## 做法

和 HCC1395 實驗相同。只用 5mC（`m` 設定）。和 B09 原論文做法的差異，見 `lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md`「做法」一節。

```bash
python3 tools/pcdh_entropy.py <CRAM> <LABEL> <OUT_TSV>
python3 tools/meth_call_control.py <CRAM>
```

## 結果

| 指標 | t50_n00 tumor | t00_n25 normal |
|---|---|---|
| 可用 read 數 | 1,558 | 688 |
| 可用 window 數 | 966 | 257 |
| window 平均甲基化（中位數） | 0.52 | 0.85 |
| entropy 中位數（IQR），bits | 2.96（2.17–3.49） | 2.51（1.69–3.17） |
| entropy ≤ 1 bit 的 window | 7% | 11% |
| entropy ≥ 3 bits 的 window | 49% | 33% |
| 最常見 barcode 比例（中位數） | 0.29 | 0.38 |

兩檔共有 228 個 window：
- entropy 中位數：tumor 2.97，normal 2.57 bits，差值中位數 +0.27 bits。
- tumor 較低的 window 只有 88 / 228。
- 平均甲基化中位數：tumor 0.64，normal 0.85。

tumor window 的平均甲基化從 0 到 1 分布很廣：0.0–0.2 有 204 個、0.4–0.6 有 181 個、0.8–1.0 有 215 個。中間甲基化（0.4–0.8）共 375 個，entropy 中位數 3.49 bits。

依 PCDH 次區塊（座標為約略值）：

| 次區塊 | tumor 甲基化／entropy | normal 甲基化／entropy |
|---|---|---|
| alpha（140.78–141.02 Mb） | 0.75／2.69 | 0.83／2.53 |
| beta（141.05–141.25 Mb） | 0.40／3.02 | 0.64／3.14 |
| gamma（141.33–141.52 Mb） | 0.46／3.16 | 0.88／2.22 |

call 校準：

| 區域 | tumor 甲基化比例 | normal 甲基化比例 |
|---|---|---|
| PCDH | 0.475 | 0.600 |
| GAPDH promoter | 0.004 | 0.005 |
| ACTB promoter | 0.005 | 0.002 |

兩檔的 ML 中間 call（51–203）都約 1–2%，和 HCC1395 Dorado 批相近。

## 和 HCC1395 對照

| 項目 | HCC1395（乳癌，Dorado 批） | H1437（肺腺癌） |
|---|---|---|
| tumor 甲基化中位數 | 0.98 | 0.52 |
| tumor entropy 中位數 | 0.57 bits | 2.96 bits |
| normal entropy 中位數 | 2.57 bits | 2.51 bits |
| tumor 對 normal | 低很多 | 略高 |

兩株的 normal 很接近，差異集中在 tumor。

## 解讀（分析推論）

- H1437 沒有 HCC1395 那種整區高甲基化。gamma 次區塊的甲基化下降最多（0.88 → 0.46）。
- cell line 是 clonal，照理 entropy 應該比 normal 低。H1437 tumor 反而較高，可能的原因：
  1. 沒分 haplotype。H1437 的 HP1 與 HP2 barcode 若差很多，會多出約 1 bit。
  2. 這一區有 copy number 增加或 subclone，會讓 barcode 種類變多。
  3. 長期培養中 epimutation 持續累積。若速度太快，barcode 會飽和，反而失去 lineage 資訊。
  4. call 錯誤。GAPDH 與 ACTB 的錯誤率約 0.5%，10 個 CpG 約只會帶來 0.3 bit 左右，不足以解釋全部差異。
- 所以「entropy 高」只代表 barcode 還沒消失。它是 clone 結構、haplotype 差異還是飽和，要分 haplotype 才分得出來。

## 限制

- 沒有 HP tag，沒有分 haplotype。
- normal 只有 688 條 read、257 個 window，比較只限 228 個共有 window。
- 只有一批資料，沒有跨 basecalling 批重現。
- 沒有檢查 H1437 在 chr5q31 的 copy number。
- PCDH 次區塊與整區的 GRCh38 座標都是約略值。

## 下一步

1. 做 longphase haplotag，分 HP 重算 entropy。看 HP 內是否仍有多於 1 群的 barcode。
2. 查 H1437 在 chr5q31 的 CN 與 LOH。
3. 對 H2009、HCC1937、HCC1954 跑同一套檢查，看高甲基化的株有幾株。

## 檔案

| 檔案 | 內容 |
|---|---|
| `H1437_t50_n00.pcdh_windows.tsv` | tumor 逐 window 結果 |
| `H1437_t00_n25.pcdh_windows.tsv` | normal 逐 window 結果 |
| `H1437_{t50_n00,t00_n25}.call_control.txt` | call 校準對照 |

欄位定義同 `lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md`。
