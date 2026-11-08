# P01｜早期胚胎的 postzygotic SNV 大致各半落在父源與母源 haplotype；germline DNM 約 80% 來自父親

## 論文與結論

Sasani TA, Pedersen BS, Gao Z, et al. **Large, three-generation human families reveal post-zygotic mosaicism and variability in germline mutation accumulation.** *eLife* 8, e46922 (2019). DOI：[10.7554/eLife.46922](https://doi.org/10.7554/eLife.46922)。PMID 31549960；PMC6759356。同儕審查。讀取層級：全文（PMC 文字；補充資料沒讀）。查核日期：2026-11-08。

**結論：** postzygotic（gonosomal）SNV 沒有明顯偏向一條親代 haplotype。475 個 gonosomal DNM 中，249 個（52%）在父源 haplotype。對照組是單一配子的 germline DNM，79.8% 來自父親。作者沒有對 249/475 報檢定值；本檔用雙尾 exact binomial 算出 p ≈ 0.31〔推論〕。

| 查核軸 | 結果 |
|---|---|
| 樣本與組織 | 33 個三代 CEPH/Utah 家族，603 人（QC 移除 10 人）；blood-derived DNA；正常人，不是腫瘤 |
| 定序資料 | short read：Illumina HiSeqX，2 × 150 bp，median ~30X |
| 親代資料 | 有。用三代 haplotype sharing 與 read tracing（±200 kb informative sites、500 bp 內 read-backed）定相到祖父母 haplotype |
| 突變類型 | germline DNM（第二代 4,671 個）；gonosomal postzygotic DNM（第二代 475 個）；post-PGCS germline mosaic（第三代 720 個、303 個位點） |
| 對本問題的方向 | (b) 大致各半（postzygotic SNV） |
| 證據類型 | 直接計數（249/475）；沒有報檢定 |

## 實際讀到的證據

- **gonosomal DNM 各半：** "In total, we identified 475 putative autosomal gonosomal DNMs ... gonosomal mutations appeared to be sex-balanced with respect to the parental haplotype on which they occurred; 52% (249/475) of all gonosomal DNMs occurred on a paternal haplotype, as compared to ~80% of germline DNMs observed in the second generation."（Results，gonosomal 段）〔論文〕
- **突變類型也不偏：** "no significant enrichment of particular gonosomal mutation types was observed on either parental haplotype at a false discovery rate of 0.05"。但 T > A 在 gonosomal 比 germline DNM 多（p = 2.32e-3）。（同段）〔論文〕
- **沒有親代年齡效應：** "there were no significant effects of parental age on gonosomal DNM counts (maternal age, p=0.132; paternal age, p=0.225)"（同段）〔論文〕
- **比例：** "over 9% (475/5,017) of all candidate autosomal germline mutations observed in the second generation were, in fact, post-zygotic"；allele balance ≥ 0.2 的有 303/5,017（約 6%）。（同段）〔論文〕
- **germline DNM 對照：** 第二代 "The ratio of paternal to maternal DNMs was 3.96:1, and 79.8% of DNMs were paternal in origin"；第二代每人 median 98.5% 可定相（範圍 90.3–100%）。第三代 5,336 個可定相的 DNM 中 4,201 個（78.7%）來自父親。（Results，"Parent-of-origin and parental age effects" 段與第三代段）〔論文〕
- **post-PGCS germline mosaic：** "Of the phased shared germline mosaic mutations, 124/260 (47.7%) were paternal in origin; thus, the mutations that occurred following PGCS likely occurred irrespective of any parental sex biases"（Results，germline mosaicism 段）。這裡的 "paternal" 指突變發生在哪一位親代的 germline（父或母的生殖腺），不是同一人體內兩條 haplotype 的分配〔推論〕。雙尾 exact binomial p ≈ 0.50〔推論〕。
- **gonosomal 的定義與偵測：** 第二代為 heterozygous，但對附近 informative alleles 呈 "incomplete linkage"（Results 與 Materials and methods）〔論文〕。所以 475 個都已定相〔推論〕。

## 限制

- 作者寫：要求第二代是 heterozygous，會漏掉 blood 中頻率很低的 postzygotic 突變，所以 gonosomal 數量可能低估。（Results）〔論文〕
- 作者寫：只測 blood，不能排除 "germline-only" mosaic 其實也在其他沒取樣的體細胞中。（Results）〔論文〕
- 作者寫：可能低估 maternal age effect 的檢定力；pipeline 可能錯分 gonosomal 與 shared germline mosaic。〔論文〕
- 只涵蓋早期胚胎（PGCS 前）的突變。不涵蓋成人組織累積的體突變，也不涵蓋腫瘤。〔推論〕
- short read 定相只能用 read 長度內或家族傳遞的 informative sites。偵測依賴 incomplete linkage，可能有篩選偏差；偏差方向未核對。〔推論〕
- 249/475 是全部家族合併。各家族或各人的分布，本檔沒核對（補充表未讀）。〔推論〕
- **和 P03 重疊：** P03 寫 "Previous Illumina-based analysis of this family<sup>14</sup>"，ref 14 就是本文（P03 `fulltext.md` 檔尾補註，PMC XML 核對）。所以 CEPH 1463 是本文 33 個家族之一，P01 與 P03 不是完全獨立的樣本。本文本機 `fulltext.md` 用關鍵字 "1463" 搜不到家族編號。〔論文〕〔推論〕

## 對本研究的意義〔推論〕

- 支持 diplosim 把 somatic SNV 以 50% 機率分到 HP1 或 HP2 當零假設。但證據來自正常人早期胚胎與 blood，不是腫瘤。腫瘤中仍可能有局部偏向（例如 kataegis、B04 的富集區）。
- 支持的 N3 層：只有觀測特徵（SNV 在兩條親代 haplotype 的分布）。不支持克隆結構或演化路徑。
- germline DNM 的 ~80% 父源偏向來自配子生成，和腫瘤的 somatic SNV 是不同機制。不要把 80% 套到模擬器的 somatic SNV。
