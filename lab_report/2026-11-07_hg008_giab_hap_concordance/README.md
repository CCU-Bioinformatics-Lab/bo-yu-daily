# HG008：PRCGAP 和 GIAB benchmark 的單倍型對照（2026-11-07）

問題：HG008 的 SNV 落在哪條單倍型，PRCGAP 和 GIAB 的判定一致嗎？

真值來源：沒有絕對真值，GIAB 是 draft benchmark，單倍型同樣來自組裝。讀長：兩邊都以 long read 組裝為主，GIAB 另用多種定序資料確認突變。輸入：PRCGAP 的 HG008 突變表、GIAB small variant benchmark v0.4（GRCh38）。生成方法：本實驗程式已列於下方。

用到的會議：2026-11-04（未決事項 2）。標記：〔實測〕本實驗計算；〔repo〕GIAB v0.4 README；〔推論〕本檔推論。

## 1. 結論

- **兩邊高度一致。** 容許每條染色體整條對調後，6,302 個 SNV 有 6,139 個一致（97.41%）。〔實測〕
- **編號不能跨染色體使用。** 23 條染色體有 14 條編號相反，9 條相同。〔實測〕
- **這是兩份組裝互相吻合，不是和絕對真值比對。** 也不回答親源：GIAB v0.4 README 搜尋不到 maternal、paternal、mother、father、trio。〔repo〕

這重現 2026-11-06 的 97.4%。當時只跑在暫存腳本，現在存成 `tools/hg008_giab_hap_concordance.py`。

支持的層（N3）：觀測特徵（單倍型判定的一致性）。不支持克隆結構或演化路徑。

## 2. 怎麼對照

1. **PRCGAP：** 依論文可重建的條件過濾，再加 `point_mutation_other` = True，並要有 GRCh38 座標，得到 6,821 個 SNV。
2. **GIAB：** GRCh38 `tumorvariants` VCF 的 9,574 個 SNV。單倍型取自 `HG008Nv63SOMATICVARIANT` 註記，例如 `chr1_hap1:783363-G-A`。
3. **找同一個突變：** 同染色體、同鹼基變化，位置容許 +0 或 +1，兩條股都試。找到 6,306 個，其中 4 個的 GIAB 單倍型不明，扣除後剩 6,302 個。
4. **比編號：** 每條染色體分別算編號相同和相反的數量，取較多的一邊當一致。

結果在 `summary.tsv`、`per_chromosome.tsv`。

## 3. GIAB 怎麼做出 benchmark〔repo〕

- **候選：** 腫瘤組裝 HG008-T v3.4 用 dipcall 比到正常組裝 HG008-N v6.3。
- **確認：** PacBio HiFi、ONT、Illumina／Element 的比對結果，用 repun 確認或否決每個候選突變。
- **檢查：** 和 10 份社群 callset 比較；另外人工抽查 34 個重複出現的 FP／FN 位點，其中 29 個判定 benchmark 正確。不是逐一人工檢查所有突變。

## 4. 預期和實際

| | 預期 | 實際 |
|---|---|---|
| 一致率 | 重現 97.4% | 97.41% |
| 編號相反的染色體 | 之前寫「約一半」 | 14／23，已更正相關文字 |

## 5. 限制

- **只含 truncal SNV。** GIAB 排除可能的 subclonal 突變，所以低 VAF 突變沒有比到。
- **比例略為偏高。** 每條染色體取較多的方向當一致。各條都幾乎一面倒，影響應該很小。〔推論〕
- **163 個不一致的原因沒有查。** 可能是真的錯誤，也可能是座標或表示法不同。
- **獨立性沒有核對。** 兩邊是不同團隊和組裝，但是否用到相同定序資料沒有核對。
- **只有 HG008。** 不能外推到其他細胞株。

## 6. 重跑

```bash
python3 -I tools/hg008_giab_hap_concordance.py /big8_disk/boyu114/benchmark_data/prcgap_sakamoto2026/extracted lab_report/2026-11-07_hg008_giab_hap_concordance
```
