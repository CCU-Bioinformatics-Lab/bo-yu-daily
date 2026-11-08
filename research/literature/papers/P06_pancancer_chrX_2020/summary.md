# P06｜女性腫瘤的 X 突變負荷較高，作者歸因於 Xi；沒有定相，Xi 偏向是間接推論

## 論文與結論

Akdemir KC, et al. **Somatic mutation distributions in cancer genomes vary with three-dimensional chromatin structure.** *Nature Genetics* 52, 1178 (2020)（終頁未核對）。DOI：[10.1038/s41588-020-0708-0](https://doi.org/10.1038/s41588-020-0708-0)。PMID 33020667；PMC8350746（author manuscript）。

- 同儕審查：是（正式出版；本地讀的是 author manuscript）。
- 讀取層級：全文（PMC author manuscript XML 轉文字；Extended Data 只讀圖說；Supplementary 未讀）。
- 查核日期：2026-11-08。

**本文主題是 3D 染色質結構與突變分布，不是 X 專文。** X 的部分比較女性和男性腫瘤的 X 突變負荷與分布，並推論 Xi 突變較多。它沒有把突變定相到 Xi 或 Xa，也沒有比較體染色體的兩條親代〔論文〕。所以它只能間接支持「Xi 是例外」〔推論〕。

| 查核軸 | 結果 |
|---|---|
| 樣本 | 約 3,000 對 tumor-normal WGS，42 種癌別（PCAWG 等） |
| 定序資料 | short read bulk WGS |
| 親代資料與定相方法 | 沒有親代資料，沒有定相（全文搜尋 "phas" 0 筆）；比較女性與男性，並用 allele-specific X Hi-C 圖說明 Xi 結構 |
| 突變類型 | somatic SNV（mutation load、clonal／subclonal） |
| 對本問題的方向 | (c) 只在特定情境：女性 X（推論為 Xi）；體染色體 (d) 沒量 |
| 證據類型 | 間接（性別比較、分布形狀、XIST 相關） |

## 實際讀到的證據

- 〔論文〕摘要："we studied 3,000 tumor-normal pair whole-genome datasets from 42 different human cancer types."
- 〔論文〕Results（Fig. 2c）：R1（active）與 R2（inactive）500 kb 區之間，"The mutational load change is 74.3% in male samples between these two regions whereas the change is only 30.7% in female samples"。作者解讀為 Xi 沒有 TAD 結構。
- 〔論文〕Results："subclonal mutations on the X-chromosome exhibit a more invariant distribution between R1 and R2 when compared to clonal mutations, a phenomenon implying that Xi acquires more mutations during tumor evolution than Xa (Fig. 2c, Extended Data Fig. 5b–c)." 體染色體（chr7）沒有這個差異。
- 〔論文〕Results（Fig. 2d）：CLL 的性別差異最大；"Female X-mutation load is significantly higher even when compared to copy-number-corrected male samples (P value < 10−6; Fig. 2d)."
- 〔論文〕Results（Fig. 2e）：有 X 多倍體的男性腫瘤沒有顯著增加，"implying the observed increase is predominantly due to an inactive X-chromosome"。
- 〔論文〕Discussion："The subclonal mutation rate on Xi is higher when compared to that of the active X-chromosome in female tumors"。
- 〔論文〕Discussion："the repressed gene regions in Xi potentially acquire 2-fold higher mutation load compared to the same regions in Xa." 這句在討論免疫治療時出現，原文用 "potentially"，本檔沒有找到直接計算這個 2 倍的 Results 段落（關鍵字 "2-fold"、"twofold"）。

## 限制

- 〔論文〕X 分析排除強烈性別偏向的癌別（breast、prostate、ovarian、uterine adenocarcinoma）。
- 〔推論〕沒有定相：「Xi 突變較多」是由女性 vs 男性、分布形狀、XIST 相關推得，不是直接數 Xi 與 Xa 上的突變。
- 〔推論〕"2-fold" 是 Discussion 的推測語氣，不能當量測值引用。
- 〔推論〕clonal／subclonal 分類來自 PCAWG 的 VAF 與 CN 模型，不是單細胞。

## 對本研究的意義〔推論〕

- 和 P05 一致：Xi 是同源染色體之間突變量不對稱的例外；但本文是間接證據，強度低於 P05 與 Jäger 2013 的定相計數。
- 本文沒有提供體染色體父母比例，對 diplosim 的 50% null 沒有直接資訊。
- N3 層級：觀測特徵（X 突變負荷與分布）；clonal／subclonal 差異間接涉及演化時序，但不支持克隆結構。
