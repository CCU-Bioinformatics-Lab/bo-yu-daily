# HCC1395 ONT：真實 somatic SNV 的 HP 拆分訊號（2026-10-25）

目的：在本機真實 ONT 資料上量測 HP（haplotype）特徵，檢查 HP-aware 真值樹與模擬器的假設是否真實。
要回答的是：PhyClone 加上 long read 特徵分出真值樹時，要依靠的 HP 訊號在真實資料中有多強。

## 結論

- **大多數 somatic SNV 可以明確分到 HP1 或 HP2。** 在至少有 3 條 alt read 的 30,965 個 SNV 中，92.2% 的 tagged alt read 有 ≥ 90% 落在同一條 HP。只有 2.4% 分散在兩條 HP。〔實測〕
- **alt read 有 HP tag 的比例是 85.9%。** 這和模擬器的假設（`--phased 0.85`）幾乎相同。〔實測〕
- **兩條 HP 上的 SNV 數相近。** 已指派的 SNV 中，HP1:HP2 = 14,443:14,120。這支持真值樹事件 ⑤（HP 拆分）。HG008 的結果也一樣。〔實測〕
- **HP 深度能直接反映 haplotype-specific CN。** minor HP 的深度比例和 ASCAT 的預期值一致：LOH 區（minor = 0）有 95–100% 的位點 minor HP < 0.1；3+1 區預期 0.333、實測 0.357；6+2 區預期 0.333、實測 0.333。這表示真值樹事件 ②（HP gain）和 ⑥（cnLOH）在真實 ONT 資料中看得到。〔實測〕
- **read 共現取決於 SNV 間距。** 在約 50× 下，間距 < 5 kb 的 SNV pair 有約 44–52 條跨越 read（幾乎是全部 depth）。5–20 kb 中位 21 條，20–50 kb 中位 2 條，50–100 kb 幾乎沒有。〔實測〕
- **共現的 pair 不多。** 37,305 對相鄰 SNV pair 中，只有 7,111 對（19%）有至少 1 條 read 同時帶兩個 ALT。HCC1395 有 37,330 個 somatic SNV，突變負荷偏高。突變少的腫瘤，近距離 pair 會更少。〔實測＋推論〕
- **對模擬器的意義：** phasing 比例和 HP 深度的假設都符合真實資料。read 共現不能對每對 SNV 都設定固定的 80 條，應該依 SNV 間距和 depth 抽樣。〔推論〕

## 結果

### A. HP 指派（37,327 個 SEQC2 SNV 有 pileup）

| 類別 | SNV 數 | 佔比 | 說明 |
|---|---:|---:|---|
| 指派到單一 HP | 28,563 | 76.5% | tagged alt read ≥ 3，而且 ≥ 90% 在同一條 HP |
| alt read 總數 < 3 | 6,362 | 17.0% | 低 VAF 或低 depth，不是 phasing 問題 |
| alt ≥ 3，但 tagged alt < 3 | 1,647 | 4.4% | read 上沒有已 phase 的 het SNP |
| 分散在兩條 HP | 755 | 2.0% | 可能是 phase block 切換錯誤，或 SEQC2 位點本身有問題 |

- alt read 有 HP tag 的比例（合併）：85.9%。
- 位點平均 depth：54.9×。

### B. minor HP 深度比例 × ASCAT CN

只用兩條 HP 合計 ≥ 10 條 tagged read 的位點。HP 方向在每個 phase block 內是任意的，所以只看 minor 比例。

| tumor CN（total, minor） | SNV 數 | 預期 minor 比例 | 實測中位 | minor < 0.1 的位點比例 |
|---|---:|---:|---:|---:|
| 1, 0 | 371 | 0 | 0.000 | 94.6% |
| 2, 0（cnLOH） | 8,384 | 0 | 0.000 | 97.5% |
| 2, 1 | 1,025 | 0.500 | 0.394 | 2.9% |
| 3, 0 | 4,346 | 0 | 0.000 | 98.0% |
| 3, 1 | 6,663 | 0.333 | 0.357 | 0.8% |
| 4, 0 | 1,412 | 0 | 0.000 | 98.6% |
| 4, 1 | 757 | 0.250 | 0.371 | 0.8% |
| 4, 2 | 4,330 | 0.500 | 0.442 | 0.3% |
| 5, 1 | 1,914 | 0.200 | 0.206 | 1.8% |
| 6, 1 | 285 | 0.167 | 0.176 | 2.1% |
| 6, 2 | 549 | 0.333 | 0.333 | 0.7% |
| 7, 1 | 140 | 0.143 | 0.149 | 5.7% |

- 大部分狀態吻合到 ±0.03 以內。
- **(2,1) 和 (4,1) 偏離較多**（0.394 對 0.5；0.371 對 0.25）。可能是 ASCAT 在這些區段的 CN 不準，或是 subclonal CN。這兩類只佔 4.8% 的位點。〔推論〕
- 位點上的 depth 包含 alt read。alt read 都落在帶突變的 HP，所以 minor 比例會有小偏差。〔推論〕

### C. 相鄰 SNV pair 的跨越 read

| 間距 | pair 數 | 跨越 read 中位數 | ≥ 1 條 | ≥ 10 條 |
|---|---:|---:|---:|---:|
| 0–1 kb | 1,394 | 52 | 100% | 99.9% |
| 1–5 kb | 2,516 | 44 | 100% | 99.8% |
| 5–20 kb | 7,209 | 21 | 100% | 85.9% |
| 20–50 kb | 9,581 | 2 | 73.8% | 5.2% |
| 50–100 kb | 8,244 | 0 | 5.7% | 0% |

- 全基因組 37,305 對相鄰 pair，其中 28,944 對間距 < 100 kb。
- 7,111 對有 read 同時帶兩個 ALT。13,973 對有 read 只帶其中一個 ALT。後者對拓樸有資訊：它表示兩個 SNV 不一定在同一群細胞。
- 這是 100% tumor（`t50_n00`）。在 purity 0.4 的樣本中，帶 ALT 的 read 會少約 60%。〔推論〕

## 對照模擬器與真值樹的假設

| 假設 | 模擬器／真值樹 | HCC1395 實測 | 判定 |
|---|---|---|---|
| read 有 HP tag 的比例 | 0.85 | alt read 0.859 | ✅ 一致 |
| somatic SNV 可分到單一 HP | 每個 SNV 都有 HP | 有足夠 alt read 時 92.2% | ✅ 大致成立；約 8% 無法指派或分散 |
| HP 深度反映 haplotype CN | 依 copy 數抽 read | 多數 CN 狀態吻合到 ±0.03 | ✅ 成立 |
| 兩條 HP 都有 SNV | 是 | HP1:HP2 ≈ 1:1 | ✅ 成立 |
| 指定 SNV pair 的跨越 read | 每對 80 條（200×） | 依間距而定：< 5 kb 接近全部 depth，> 50 kb 幾乎為 0 | ⚠️ 要改成依間距抽樣 |

## 資料

- tumor read：ONT（香港大學，SRR25005626）系列的 `t50_n00` subsample，約 50×，100% tumor。
- phasing：SEQC2 HCC1395BL germline 真值中的 het SNP（1,816,766 個，Illumina），在 ONT normal `HCC1395BL.cram` 上 phase。
- somatic SNV：SEQC2 v1.2.1 HighConf（37,330 個）。
- CN：SEQC2 21 份 WGS ASCAT 的共識（同 `lab_report/2026-10-25_seqc2_hcc1395_measured_purity/`）。
- 大型中間檔：`/big8_disk/boyu114/hcc1395_hp_split/`（tagged CRAM 82 GB）。

## 做法

```bash
bash tools/hcc1395_hp_split_prepare.sh /big8_disk/boyu114/hcc1395_hp_split
python3 -I tools/hcc1395_hp_split.py /big8_disk/boyu114/hcc1395_hp_split/tagged_t50_n00.cram \
  lab_report/2026-10-25_hcc1395_hp_split
```

1. `longphase-s phase --ont`：只用 normal read 做 phasing，避免 tumor LOH 干擾。
2. `longphase-s haplotag`（germline 模式）：標記 tumor read。
3. `samtools mpileup --output-extra QNAME,HP`（`-q 20 -Q 7 -B`，排除 supplementary）：取得每個 SNV 位點上每條 read 的 allele 和 HP。

`longphase-s haplotag` 需要兩個 VCF 修正，否則會以 `stoi` 錯誤中止：`##contig` 行要有 `length=`；未 phase 的位點（PS 為 `.`）要移除。前處理腳本已處理。

## 結果檔

`tables/`：`summary.txt`、`per_snv_hp.tsv`（每個 SNV 的 HP 計數與 CN）、`hp_depth_by_cn.tsv`、`snv_pairs.tsv`、`pair_spanning_by_distance.tsv`。

## 限制

- **只用 germline `haplotag`。** longphase-s 的 `somatic_haplotag` 可能標到更多 read，所以本實驗的 tag 比例是下限。要模仿哪一種，尚未決定。
- **只用 100% tumor 的 subsample。** 低 purity 下，帶 ALT 的 read 會等比例減少。
- **只有一株細胞株，一個資料集。** HCC1395 的 LOH 比例高，突變負荷也高，近距離 SNV pair 比一般腫瘤多。
- **「分散在兩條 HP」的原因還沒有拆開分析。** 可能來自 phase 切換錯誤、SEQC2 假陽性，或重複區段。
