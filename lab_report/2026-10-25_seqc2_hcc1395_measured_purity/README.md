# HCC1395 ONT subsample 的實測 purity（SEQC2 真值，2026-10-25）

目的：用 SEQC2 的 HCC1395 somatic SNV 真值，量測本機 `tX_nY` subsample 的實測細胞 purity。
這是「先證明真值樹合理」主線的一部分：它檢查事件 ①（低 purity）的參數範圍，也把 nominal 標籤換成實測值。

## 結論

- **nominal 標籤是 tumor DNA 比例，不是細胞 purity。** 實測細胞 purity 都比 nominal 低。例如 `t20_n30`（nominal 40%）的實測細胞 purity 是 0.32。〔實測〕
- **兩者的差距可以用 ploidy 完全解釋。** 用 ploidy 2.85 把細胞 purity 換回 DNA 比例，結果和 nominal 的差距在 0.006 以內。nominal 反推出的 ploidy 是 2.75–2.91，和 SEQC2 論文的 2.85 一致。〔實測＋推論〕
- **估計很穩定。** 在 tumor CN 1 到 7 的位點各自估計，同一個 subsample 的結果最多差約 0.03。bootstrap 95% CI 寬度約 0.004。〔實測〕
- **兩個系列的結果幾乎相同。** ONT 和 ONT_Dorado 在對應的 nominal 下（例如 40% 對 39.6%），實測 purity 差 0.003–0.006。〔實測〕
- **`t00_n25` 有約 0.4–0.7% 的背景訊號。** 這可能是 ONT 定序錯誤剛好等於 ALT 鹼基，也可能是極少量的 tumor 混入。目前無法分辨。〔實測；原因是推論〕
- **真值樹的 purity 0.40 落在本機實際資料的範圍內。** 它介於 `t20_n30`（0.32）和 `t30_n20`（0.51）之間。〔實測〕
- **給 PhyClone 的 `tumour_content` 要用實測細胞 purity，不能用 nominal。** PhyClone 的模型假設 tumour_content 是細胞比例。〔推論；PhyClone 模型見 `research/phyclone_research/notes/`〕

## 結果

細胞 purity 用 CN = 2 位點估計（約 10,000 個）。DNA 比例用 ploidy ψ 換算。

| 系列 | 標籤 | nominal | 實測細胞 purity（95% CI） | DNA 比例（ψ=2.85） | DNA 比例（ψ=3.09） | median depth |
|---|---|---:|---:|---:|---:|---:|
| ONT | t00_n25 | 0.000 | 0.007（0.007–0.008） | 0.010 | 0.011 | 26 |
| ONT | t10_n40 | 0.200 | **0.153**（0.151–0.154） | 0.205 | 0.218 | 52 |
| ONT | t20_n30 | 0.400 | **0.321**（0.319–0.323） | 0.402 | 0.422 | 53 |
| ONT | t30_n20 | 0.600 | **0.513**（0.511–0.515） | 0.600 | 0.620 | 52 |
| ONT | t40_n10 | 0.800 | **0.737**（0.735–0.739） | 0.800 | 0.813 | 52 |
| ONT | t50_n00 | 1.000 | 1.000（定義） | 1.000 | 1.000 | 53 |
| ONT_Dorado | t00_n25 | 0.000 | 0.004（0.003–0.004） | 0.005 | 0.006 | 26 |
| ONT_Dorado | t7_n29 | 0.194 | **0.149**（0.147–0.151） | 0.200 | 0.213 | 38 |
| ONT_Dorado | t19_n29 | 0.396 | **0.315**（0.313–0.317） | 0.396 | 0.416 | 51 |
| ONT_Dorado | t30_n20 | 0.600 | **0.508**（0.505–0.510） | 0.595 | 0.615 | 52 |
| ONT_Dorado | t40_n10 | 0.800 | **0.734**（0.732–0.736） | 0.797 | 0.810 | 52 |
| ONT_Dorado | t50_n00 | 1.000 | 1.000（定義） | 1.000 | 1.000 | 52 |

完整表格在 [`tables/`](tables/)：

| 檔案 | 內容 |
|---|---|
| `measured_purity.tsv` | 上表 |
| `purity_by_cn.tsv` | 每個 tumor CN 層各自估出的 purity（一致性檢查） |
| `site_cn_summary.tsv` | 位點數、ASCAT 共識位點數、各 CN 層位點數、ASCAT ploidy |

### 一致性檢查：各 CN 層的估計

以 ONT `t20_n30` 為例。VAF 比值隨 CN 上升，但換算後的 purity 一致：

| tumor CN | 位點數 | VAF 比值 | 換算 purity |
|---:|---:|---:|---:|
| 1 | 430 | 0.190 | 0.320 |
| 2 | 10,039 | 0.321 | 0.321 |
| 3 | 11,625 | 0.402 | 0.309 |
| 4 | 6,838 | 0.472 | 0.309 |
| 5 | 2,810 | 0.528 | 0.309 |
| 7 | 294 | 0.601 | 0.301 |

CN ≥ 3 的估計略低約 0.01。可能原因是 ASCAT 的 CN 在部分位點偏高。這不影響結論。〔推論〕

## 資料

- SNV 真值：SEQC2 v1.2.1 `high-confidence_sSNV_in_HC_regions_v1.2.1.vcf.gz`，只取 HighConf（37,330 個）。
- tumor CN：SEQC2 21 份 WGS ASCAT 結果（`analysis/CNVs/WGS/ascat/`）。只收 ≥ 18 份一致的位點（33,230 個）。21 份的 autosome ploidy 中位數是 3.09。
- ONT subsample：`/big8_disk/data/HCC1395/{ONT,ONT_Dorado}/subsample/<label>/HCC1395_<label>.cram`。兩個系列的來源不同，見 `tumor_sample.md`。
- 位置：`/big8_disk/boyu114/benchmark_data/SEQC2/`。

## 做法

```bash
python3 -I tools/seqc2_hcc1395_purity.py lab_report/2026-10-25_seqc2_hcc1395_measured_purity
```

1. 在每個 CRAM 上用 `bcftools mpileup -R`（`-q 20 -Q 7 -B`）計算 SEQC2 位點的 REF／ALT read 數。只算 SEQC2 指定的 ALT 鹼基。
2. 只用兩邊都有足夠 depth 的位點（`t50_n00` ≥ 10、subsample ≥ 5）。
3. 在 tumor CN = k 的位點，合併 VAF 比值 r = subsample 合併 VAF ÷ `t50_n00` 合併 VAF。
4. 換算細胞 purity：p = 2r / (k(1 − r) + 2r)。k = 2 時 p = r。
5. 換算 tumor DNA 比例：d = pψ / (pψ + 2(1 − p))。
6. bootstrap：對 CN = 2 位點重抽 500 次，取 2.5% 與 97.5% 分位。

這個方法對 subclonal SNV 也成立。原因是 subsample 和 `t50_n00` 來自同一批 tumor read，subclone 比例相同。〔推論〕

## 限制

- **`t50_n00` 被當成 100% tumor。** SEQC2 報告 HCC1395 的 purity 約 99%。如果 `t50_n00` 本身不是 100%，所有實測值都要再乘上它的 purity。
- **CN 來自 Illumina ASCAT，不是 ONT 資料本身。** 兩者是不同批次的細胞。CN 一致性檢查顯示影響小於 0.03。
- **ploidy 有兩個來源，數值不同。** ASCAT 是 3.09，SEQC2 論文是 2.85。nominal 反推的值（2.75–2.91）支持 2.85，所以表中 ψ = 2.85 的 DNA 比例較可信。
- **這只量測 HCC1395。** 其他 5 株沒有 SEQC2 等級的 SNV 真值。
