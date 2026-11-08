# P04｜biallelic 突變證明兩條親代同源染色體會在同一位點各自突變；本文沒有比較兩條親代的突變量

## 論文與結論

Demeulemeester J, et al. **Biallelic mutations in cancer genomes reveal local mutational determinants.** *Nature Genetics* 54, 128–133 (2022). DOI：[10.1038/s41588-021-01005-8](https://doi.org/10.1038/s41588-021-01005-8)。PMID 35145300；PMC8837546。

- 同儕審查：是（正式出版）。
- 讀取層級：全文（PMC XML 轉文字；Extended Data 只讀圖說；Supplementary Tables 未讀）。
- 查核日期：2026-11-08。

**本文不回答「突變偏向哪一條親代」。** 它只數「同一鹼基在兩條親代拷貝上各自突變」的事件。作者的 uniform permutation 模擬把突變均勻放在兩條 diploid 拷貝上，但這個模型低估 biallelic 數；準確預測的是另一個 neighbor resampling 模型。所以「均勻放在兩條拷貝」不是本文驗證過的假設〔論文〕〔推論〕。

| 查核軸 | 結果 |
|---|---|
| 樣本 | PCAWG 2,658 個腫瘤 WGS；biallelic 突變出現在 559 個（21%）樣本 |
| 定序資料 | short read（PCAWG bulk WGS，read pair） |
| 親代資料與定相方法 | 沒有親代資料。用 700 bp 內的 germline het SNP 與同一 read pair 定相；另用 Battenberg 的 phased BAF 比較 VAF |
| 突變類型 | SNV（parallel、divergent）、dinucleotide；MSI 腫瘤另有 indel 模擬 |
| 對本問題的方向 | (d) 沒量：沒有比較 HP1 與 HP2，也沒有比較父與母 |
| 證據類型 | 直接計數（biallelic 事件）；對親代比例只是間接 |

## 實際讀到的證據

- 〔論文〕摘要："Here we identify 18,295 biallelic mutations, where the same base is mutated independently on both parental copies, in 559 (21%) bulk sequencing samples from the Pan-Cancer Analysis of Whole Genomes study."
- 〔論文〕Results："In total, we identified 5,330 divergent mutations, 12,937 parallel SNVs and 14 dinucleotide variants in 559 (21%) PCAWG samples"。三者相加是 18,281，和摘要的 18,295 差 14。原因未核對。
- 〔論文〕Methods（uniform permutation model）："mutations at trinucleotides taken uniformly along the two (diploid) copies of the callable parts of chromosome i." 每樣本模擬 1,000 次。
- 〔論文〕Results（Fig. 4c、Extended Data Fig. 6）："While the uniform permutation model underestimates, neighbor resampling accurately predicts the number of biallelic mutations"。**注意：** 準確預測的是 neighbor resampling（每次保留原腫瘤 50% 突變，另 50% 從同癌別、相近 signature 的腫瘤重抽），不是「均勻放在兩條拷貝」的 uniform 模型。
- 〔論文〕Results：uniform 模型給出下界 "at least 1, typically parallel, violation in 147 tumors (5.5%; Fig. 2a)"。
- 〔論文〕Methods（phasing）："Phasing information was obtained for all heterozygous SNP–SNV pairs that were within 700 bp of one another." parallel 判定："≥2 Ref/Alt and ≥2 Alt/Alt reads"，且兩類 read 各占 >10% phased reads。
- 〔論文〕Fig. 3 圖說：DO220906 有 "373 parallel mutations (74 supported by phasing) and 8 divergent mutations"。
- 〔論文〕Results：biallelic 數 "proportional to the square of the mutation burden (n2; Fig. 4d)"。
- 〔論文〕Discussion："only 2.8% of biallelic hits fall within or near exons"；有 8 個候選 biallelic driver 事件。

## 限制

- 〔論文〕兩種偵測方法 "are blind in regions with loss of heterozygosity"；男性只看 X 的 pseudoautosomal 區。
- 〔論文〕模擬把輸入突變當作單一事件，作者說 "this may have underestimated the true number of violations"。
- 〔推論〕biallelic 事件按定義兩條親代各有一個，所以無法顯示親代偏向。
- 〔推論〕uniform 模型低估，表示位點之間突變率不均勻（作者稱 "effective genome size" 較小）。這是位點層級的不均勻，不是親代之間的不均勻。
- 〔推論〕short read 定相只到 700 bp，看不到長區段的 HP 分布。

## 對本研究的意義〔推論〕

- 對 diplosim 的 50% null：本文不直接支持，也不反對。它只說明兩條同源拷貝都會被打到，而且同一位點可以兩條都突變。
- diplosim 若採 infinite sites，真值會缺少 biallelic 事件。21% 樣本至少有 1 個，但占總突變很少。這是另一個機制；照 N4，先不加。
- N3 層級：觀測特徵（位點層級的突變計數）。不支持克隆結構或演化路徑。
