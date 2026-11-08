# P05｜LCL 中 Xi 的突變率是 Xa 的 1.78 倍；Xa 和體染色體沒有顯著差異；文字沒有報告體染色體父母差異

## 論文與結論

Caballero M, Koren A. **The landscape of somatic mutations in lymphoblastoid cell lines.** *Cell Genomics* 3, 100305 (2023). DOI：[10.1016/j.xgen.2023.100305](https://doi.org/10.1016/j.xgen.2023.100305)。PMID 37388907；PMC10300552。

- 同儕審查：是（正式出版）。
- 讀取層級：全文（PMC XML 轉文字；圖只讀圖說；Figure S3、Table S1 未讀）。
- 查核日期：2026-11-08。

**偏向只出現在 X：** 女性 LCL 的 Xi 突變率比 Xa 高 1.78 倍，主要來自 SBS9（polymerase η）。Xa 和體染色體沒有顯著差異。Xi 是父或母幾乎各半（293 父、249 母）。所以偏向跟「是不是 Xi」有關，不跟「父或母」有關〔論文〕〔推論〕。體染色體父母同源之間的比較只在 Fig. 5F 圖中，文字沒有給數字〔論文〕。

| 查核軸 | 結果 |
|---|---|
| 樣本 | 1,662 個 LCL（EBV 轉化的 B 細胞，非腫瘤）；另 151 個 CLL 腫瘤作比較 |
| 定序資料 | short read（Illumina HiSeq X／NovaSeq／HiSeq 2000，2×100 或 2×150，約 15–50×） |
| 親代資料與定相方法 | 有 trio（parent-offspring）。用同一 read 或 mate pair 上的 inherited phaseable variant 把突變指到父或母；Xi 定為 read depth 較低的親代同源 |
| 突變類型 | SNV（885,655 個體染色體、42,061 個 X 突變） |
| 對本問題的方向 | X：(a) 偏向 Xi；體染色體：(d) 文字沒量（Fig. 5F 數值未核對） |
| 證據類型 | 直接計數（phased 突變，依 phaseable variant 數正規化） |

## 實際讀到的證據

- 〔論文〕Highlights："Analysis of 885,655 mutations from 1,662 lymphoblastoid cell lines (LCLs)"。
- 〔論文〕Results："we identified the Xi in 542 of 746 female offspring (72.65%), of which 293 were paternally X inactivated, and 249 were maternally X inactivated (Figure 5D; Table S1)."
- 〔論文〕Results："Among 542 females with an identifiable Xi, we phased 6,005 (19.75%) X chromosome mutations, of which 3,844 (64.01%) were assigned to Xi (Figure 5E)."
- 〔論文〕Results："We confirmed that the mutation rate of Xi was 1.78-fold higher (p < 1 × 10−5) than that of Xa and significantly higher than any autosome (p < 1 × 10−6) (Figure 5F; Figure S3E); the mutation rate of Xa was not significantly different than autosomes (Figure 5F)."
- 〔論文〕Fig. 5F 圖說："Xa and Xi mutation rate compared with maternal and paternal homologous autosomes with the most similar number of inherited phaseable variants to chromosome X. Mutation rate was calculated as the number of phased mutations normalized by the number of inherited phaseable variants on each chromosome homolog pair. p values were calculated from a two-tailed t test." **文字沒有寫體染色體父 vs 母的差異或 p 值；圖中數值未核對。**
- 〔論文〕Results（Fig. 5G）：Xa 與體染色體的 SBS9 占 34.36% ± 2.49%、clock-like 占 65.64% ± 5.94%；Xi 則 72.84% ± 2.27% 是 SBS9，只有 27.16% ± 2.38% 是 clock-like。"The elevated mutation rate on Xi can thus be predominantly attributed to SBS9."
- 〔論文〕Methods：Xi 判定以 chr14 的親代 read depth 差異第 95 百分位為門檻；"The parental identity of Xi was assigned to the parental homolog with the lower mean sequencing read depth." 17 個重複定序樣本的判定一致。
- 〔論文〕Methods：只有 mutation allele 的 read 全部對到一位親代時才定相；對到兩位親代算 ambiguous。

## 限制

- 〔論文〕parent-offspring calling "cannot distinguish somatic from germline mutations"；由 MZ twin 推估體染色體假突變 1.85%–27.2%（median 9.66%）。
- 〔論文〕作者說缺少 donor age、培養歷史、passage 資訊。
- 〔推論〕LCL 不是腫瘤。突變大多來自 B 細胞的 SHM／polymerase η（SBS9），機制和多數實體腫瘤不同。
- 〔推論〕只有 19.75% 的 X 突變能定相；short read 定相只限 read 或 mate pair 範圍。
- 〔推論〕Xi 判定靠 read depth 較低的一側。若 Xi 拷貝較少，突變偵測也可能受影響；作者已正規化到 phaseable variant 數，但這個影響本檔未核對。

## 對本研究的意義〔推論〕

- 支持 diplosim 對體染色體用 50% null：Xa 和體染色體沒有顯著差異。但體染色體父母比較本身沒有文字數據，只能算間接支持。
- Xi 是明確例外（1.78 倍）。偏向跟 X 失活有關，而 X 失活的親代約各半，所以「父或母」本身不是偏向來源。diplosim 目前只模擬 chr1–22，這個例外暫時不影響；若加入 chrX，要另外處理。
- N3 層級：觀測特徵（突變在同源染色體上的分布）。不支持克隆結構或演化路徑。
