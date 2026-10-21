# 5 株 cell line 的 PCDH methylation barcode entropy 比較（2026-10-20）

## 結論

5 株中有 3 株的 PCDH 區整區高甲基化，barcode 多樣性大多消失：HCC1395、H2009、HCC1937。另外 2 株保留多樣性：H1437、HCC1954。

- 分組和癌種無關。兩組都同時有乳癌與肺腺癌。
- 可以繼續評估 PCDH barcode 的只有 H1437 與 HCC1954。
- COLO829 沒有檢查，因為它的 ONT_R10 subsample 沒有 MM tag（見 B09 README 的本地查核）。

## 問題

HCC1395 的 PCDH 區高甲基化，H1437 沒有（見下方「相關實驗」）。本實驗補齊另外 3 株，看高甲基化有多普遍。

## 資料

每株用 `/big8_disk/data/<line>/ONT/subsample/` 的兩檔：

- `t50_n00`：nominal 100% tumor（design fraction，不是實測 purity）。
- `t00_n25`：純 normal baseline。

HCC1395 用 `ONT_Dorado/subsample/`。全部 MM tag 都是 5mC（`C+m?`）。HCC1937 `t50_n00` 約 25% 的 read 沒有 MM tag（抽查 77 條中有 19 條），腳本會略過這些 read。

| 株 | 癌種（`tumor_sample.md`） |
|---|---|
| HCC1395 | 乳癌 |
| H1437 | 肺腺癌 |
| H2009 | 肺腺癌 |
| HCC1937 | 乳癌（BRCA1-mutant label，provenance 待外部確認） |
| HCC1954 | 乳癌 |

## 做法

和 HCC1395、H1437 實驗相同，只用 5mC（`m` 設定）。和 B09 原論文做法的差異，見 `lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md`「做法」一節。

```bash
python3 tools/pcdh_entropy.py <CRAM> <LABEL> <OUT_TSV>
python3 tools/meth_call_control.py <CRAM>
python3 tools/pcdh_entropy_summary.py LINE:TUMOR_TSV:NORMAL_TSV [...] > panel_summary.tsv
```

## 結果

完整數字見 `panel_summary.tsv`。

| 株 | tumor 甲基化 | normal 甲基化 | tumor entropy（IQR），bits | normal entropy | tumor ≤ 1 bit | tumor 中間甲基化 window | 共有 window 中 tumor 較低 | entropy 差中位數 |
|---|---|---|---|---|---|---|---|---|
| HCC1395 | 0.98 | 0.66 | 0.57（0.23–1.43） | 2.57 | 63% | 84 | 229 / 238 | −1.97 |
| H2009 | 0.95 | 0.55 | 0.94（0.46–1.62） | 2.88 | 53% | 129 | 181 / 186 | −2.07 |
| HCC1937 | 0.98 | 0.76 | 0.57（0.26–1.28） | 2.56 | 69% | 54 | 183 / 197 | −1.84 |
| H1437 | 0.52 | 0.85 | 2.96（2.17–3.49） | 2.51 | 7% | 375 | 88 / 228 | +0.27 |
| HCC1954 | 0.76 | 0.59 | 2.77（1.77–3.44） | 2.97 | 9% | 386 | 100 / 185 | −0.10 |

甲基化與 entropy 都是 window 的中位數。中間甲基化指 window 平均甲基化 0.4–0.8。

tumor 依 PCDH 次區塊的甲基化中位數（alpha／beta／gamma，座標約略）：

| 株 | tumor | normal |
|---|---|---|
| HCC1395 | 0.96／0.98／0.99 | 0.77／0.53／0.70 |
| H2009 | 0.95／0.94／0.96 | 0.74／0.41／0.50 |
| HCC1937 | 0.98／0.98／0.99 | 0.91／0.74／0.72 |
| H1437 | 0.75／0.40／0.46 | 0.83／0.64／0.88 |
| HCC1954 | 0.78／0.62／0.85 | 0.47／0.49／0.76 |

call 校準（ML ≥ 204 的甲基化比例；`*.call_control.txt`）：

| 株 | GAPDH tumor／normal | ACTB tumor／normal |
|---|---|---|
| H2009 | 0.004／0.007 | 0.005／0.003 |
| HCC1937 | 0.003／0.002 | 0.035／0.004 |
| HCC1954 | 0.005／0.003 | 0.004／0.003 |

HCC1395 與 H1437 的校準結果見各自的實驗目錄。全部 promoter 都接近 0，沒有整體校準偏移。HCC1937 tumor 的 ACTB 是 0.035，略高，但仍很低。

## 解讀（分析推論）

- **高甲基化組（HCC1395、H2009、HCC1937）**：三個次區塊都約 0.95 以上，tumor 的 entropy 比 normal 低約 2 bits。這一組在 PCDH 上幾乎沒有可用的 barcode。
- **保留多樣性組（H1437、HCC1954）**：tumor 的 entropy 和 normal 相近，中間甲基化的 window 約 380 個。
- H1437 的甲基化比 normal 低。HCC1954 比 normal 高，但沒有到飽和。兩株的機制可能不同。
- 「entropy 高」只代表 barcode 還沒消失。它反映的是 clone 結構、haplotype 差異還是 epimutation 飽和，要分 haplotype 才能判斷（見 H1437 實驗的「解讀」）。
- 5 株的 normal entropy 都在 2.5–3.0 bits。差異集中在 tumor。

## 限制

- 沒有 HP tag，沒有分 haplotype。
- 每株的 normal 只有約 200 個 window 通過門檻，比較只限共有 window。
- 只有 HCC1395 做過跨 basecalling 批的重現。其餘 4 株只有一批。
- 沒有檢查各株在 chr5q31 的 copy number 與 LOH。
- 樣本只有 5 株，不足以推論癌種或分子亞型和高甲基化的關係。

## 下一步

1. 對 H1437、HCC1954 做 longphase haplotag，分 HP 重算 entropy。
2. 查這兩株在 chr5q31 的 CN 與 LOH。
3. 有分 HP 的結果後，再評估 PCDH dendrogram 能不能當 PhyClone MAP 樹的事後驗證。

## 相關實驗

- `lab_report/2026-10-20_hcc1395_pcdh_entropy/`：HCC1395，含跨批次重現與 5hmC 設定。
- `lab_report/2026-10-20_h1437_pcdh_entropy/`：H1437。

## 檔案

| 檔案 | 內容 |
|---|---|
| `panel_summary.tsv` | 5 株的摘要（`tools/pcdh_entropy_summary.py` 產生） |
| `{H2009,HCC1937,HCC1954}_{t50_n00,t00_n25}.pcdh_windows.tsv` | 3 株逐 window 結果 |
| `{H2009,HCC1937,HCC1954}_{t50_n00,t00_n25}.call_control.txt` | 3 株 call 校準 |

HCC1395 與 H1437 的逐 window 結果放在各自的實驗目錄，不重複存放。欄位定義同 `lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md`。
