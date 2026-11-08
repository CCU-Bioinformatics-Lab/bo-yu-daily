# P07｜HG008 的 chrX_hap2（大致是 Xi）SNV 與 indel 較多；體染色體 hap1／hap2 只有密度圖，沒有比例檢定

## 論文與結論

Wagner J, Keskus AG, Oshima KK, …, Kolmogorov M, Zook JM. **A complete human pancreatic cancer genome.** *bioRxiv* 2026.05.01.722316（v1）. DOI：[10.64898/2026.05.01.722316](https://doi.org/10.64898/2026.05.01.722316)。作者共 78 位（依 citation_author meta 計數）。

- 同儕審查：否（bioRxiv preprint）。
- 讀取層級：全文（bioRxiv v1 HTML 轉文字）；補充資料未下載，Supplementary Fig 44 沒看到。
- 查核日期：2026-11-08。

**這是本研究用的同一個 HG008 樣本。** 作者把 tumor 與 normal 各組成 haplotype-resolved 組裝，直接比對得到 truncal somatic 變異。主文只寫 chrX_hap2（大部分轉錄沉默的那條 X）SNV 與 indel 較多。體染色體只有 Fig. 1b–c 的 hap1／hap2 密度圖，沒有計數比較或檢定〔論文〕。hap1／hap2 是組裝的 haplotype 編號，不是父母標籤〔論文〕〔推論〕。

| 查核軸 | 結果 |
|---|---|
| 樣本 | HG008：一位女性（germline XX）PDAC 病人的 hypodiploid 腫瘤細胞株與正常胰臟、十二指腸組織；單一個體 |
| 定序資料 | long read 為主（PacBio HiFi、ONT ultralong，加 Hi-C）組裝；short read（Element、Onso、Illumina 等）用於 polishing 與評估 |
| 親代資料與定相方法 | 沒有親代資料（全文搜尋 parent／maternal／paternal 0 筆相關）。Verkko 組裝定相，Hi-C 與 haplotype-specific marker 驗證；tumor 與 normal 的 hap 編號人工對齊 |
| 突變類型 | truncal somatic SNV、indel、SV、CNV、L1 insertion |
| 對本問題的方向 | X：(a) 偏向 hap2（Xi）；體染色體：(d) 沒量 |
| 證據類型 | 直接計數（組裝直接比對），但 X 的結果在補充圖，主文沒有數字 |

## 實際讀到的證據

- 〔論文〕Results："Besides kataegis and omikli, the inactive chrX_hap2 has more SNVs and indels across most of the chromosome, consistent with previous studies showing hypermutation of inactive X is common in cancer (Supplementary Fig 44)." 主文沒有給計數或檢定。
- 〔論文〕Results："a balanced chr18_hap2/chrX_hap2 translocation on the copy of chrX that is mostly transcriptomically silenced (Supplementary Fig 8)."
- 〔論文〕Fig. 1 圖說："(b-c) Overview of haplotype-specific somatic SNVs (density plot with default 10 Mbp window) and SVs from HG008T-hap1 (b) and HG008T-hap2 (c)." 這是體染色體唯一的 hap1／hap2 SNV 呈現，只是密度圖。
- 〔論文〕Results：同一 haplotype 上的真 cluster 有 "68 kataegis events containing 480 variants and 1,509 omikli events containing 3,169 variants"；另有 "395 false omikli from variants on opposite haplotypes"。
- 〔論文〕Results：dGH 看 80 個細胞，"the mutations characterized here are all truncal"。
- 〔論文〕Methods：大段 duplication 中未被組裝器定相的變異，"randomly selecting which path in each bubble comes first"；"Variants were similarly assigned randomly on the very large 83 and 64 Mbp duplications of chr17 and chr20 if they were not phased by the assembler." 作者說 "these smaller somatic variants may be on the wrong copy of the duplication"。
- 〔論文〕Methods：tumor 與 normal 的 haplotype 人工對齊；"This matching of haplotypes was possible for all truncal events in HG008 except the true haplotype switch on chr19." subclonal 的 chr2_hap2–chrX_hap1 translocation 會破壞這個對齊。
- 〔論文〕Methods：Hi-C 在同一 haplotype 染色體內的連結 93.5%（normal）、94.2%（tumor）。

## 限制

- 〔論文〕預印本，未經同儕審查。
- 〔論文〕chr17、chr20 大段 duplication 與 3 個 >1 Mbp tandem duplication 中，部分變異的拷貝是隨機指定的。
- 〔推論〕hap1／hap2 不是父母標籤：沒有親代資料，編號只表示組裝的兩條 haplotype。跨染色體不能把 hap1 加總成「父」或「母」。
- 〔推論〕chrX_hap2 是 Xi，是依「大部分轉錄沉默」判斷；Supplementary Fig 44 的數值未核對。
- 〔推論〕單一細胞株、單一病人；細胞株培養可能加入體外突變。只分析 truncal 變異。

## 對本研究的意義〔推論〕

- 對 diplosim 的 50% null：HG008 主文沒有體染色體 hap1 vs hap2 的數字，不能拿來檢驗 50%。若要檢驗，要從 GIAB 的 phased benchmark VCF 自己數，並且分染色體、排除 chr17／chr20 隨機指派的 duplication 區。這是提議，不是已做的實驗。
- Xi 例外在同一樣本也看得到，與 P05、P06、Jäger 2013 方向一致。diplosim 目前只模擬 chr1–22，暫不影響。
- N3 層級：觀測特徵（真實 truncal 變異的 haplotype 分布）。truncal 判定有 dGH 支持，但不涉及克隆結構。
