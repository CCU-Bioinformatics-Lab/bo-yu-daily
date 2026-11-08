# P08｜JAK2 V617F 多半發生在帶 rs10974944 G allele 的那條 haplotype 上（45 例中 38 例）

## 論文與結論

Kilpivaara O, Mukherjee S, Schram AM, et al. **A germline JAK2 SNP is associated with predisposition to the development of JAK2V617F-positive myeloproliferative neoplasms.** *Nature Genetics* 41, 455–459 (2009)。DOI：[10.1038/ng.342](https://doi.org/10.1038/ng.342)。PMID 19287384，PMC3676425。

- 同儕審查：是（Nat Genet；本機為 NIHMS author manuscript）。
- 讀取層級：全文（主文、Methods、圖說、Table 1–3）。Supplementary Fig. 2、3 與 Supplementary Table 未讀。
- 查核日期：2026-11-08。

**答案：在 JAK2 這一個基因座，somatic V617F 不是平均落在兩條 haplotype。** 45 個 rs10974944 germline 異型合子、V617F 異型合子的病人中，38 例的 V617F 和 G allele 在同一條（cis）。作者沒有分開「這條較容易突變」和「突變在這條較有生長優勢」，兩種機制都列為可能。這是單一基因座、MPN 的結果，不能推到全基因組。

| 查核軸 | 結果 |
|---|---|
| 樣本 | MPN（PV、ET、PMF）病人。SNP array：granulocyte DNA 217 例（含 PV 113、ET 68）；germline 關聯 324 例 MPN vs WTCCC 對照；cis 分析 45 例 |
| 資料與方法 | Affymetrix 250K StyI array、TaqMan genotyping、allele-specific long-range PCR（3 kb）後定序 V617F 位點；11 例另做 TOPO 選殖驗證 |
| 親代資料／定相方法 | 沒有親代資料。用分子定相：同一個 3-kb PCR 產物同時含 rs10974944 與 exon 14，所以是物理上的 cis 判定，不是統計定相 |
| 突變類型 | V617F 是 somatic；rs10974944 是 germline |
| 對本問題的方向 | (c) 只在特定情境：單一基因座偏向帶 G allele 的那條 haplotype |
| 證據類型 | 病例對照關聯＋單分子（PCR 產物）cis 判定 |
| 突變率 vs 天擇是否分開 | 否。作者列兩種解釋，未檢驗 |

## 實際讀到的證據

- **cis 判定（主文「Analysis of the haplotype structure」段）〔論文〕：** "Using allele-specific PCR on 45 subjects heterozygous for rs10974944 in their germline and hetero-zygous for JAK2V617F in their granulocyte DNA, we found that in 38 cases JAK2V617F was acquired in cis with the G allele at rs10974944 (P = 2.8 × 10–14) (Fig. 2b)."
  - 38／45 = 84%（本檔計算）。若兩條各半，期望值約 22.5 例。〔推論〕
  - P 值用哪種檢定，正文沒寫；Methods 只列 Pearson χ2、Fisher's exact、ANOVA。未核對是哪一個。
- **同一段的另一組〔論文〕：** "We investigated 42 subjects heterozygous for rs10974944 in their germline and a somatic homozygous JAK2V617F mutant clone (JAK2V617F allele burden > 50%) and found in 38 of 42 cases somatic conversion to a homozygous GG genotype at rs10974944." 這是 LOH（isodisomy）後留下 G 那條，和上面的 45 例是不同的一組。
- **距離（Fig. 2a 圖說）〔論文〕：** "rs10974944 and exon 14 of JAK2 are in a shared haplotype approximately 3 kb apart."
- **圖說措辭（Fig. 2）〔論文〕：** "The G allele was found to be in cis with the mutant T allele in 38 of 45 ... suggesting that JAK2V617F is almost always acquired in cis with the risk allele at rs10974944."
- **germline 關聯〔論文〕：** GG/CG vs CC，MPN vs WTCCC：OR = 3.1，P = 4.1 × 10–20（Table 2a）。V617F 陽性 MPN：OR = 4.0，P = 7.7 × 10–22；V617F 陰性：OR = 1.6，P = 0.06（主文、Table 3）。
- **機制（Discussion）〔論文〕：** "These data suggest that rs10974944 favors the acquisition of JAK2 mutations in cis by an unidentified mechanism. There may be haplotype-specific variation in a regulatory motif or genotype-specific splicing that increases the selective advantage of the JAK2V617F allele when it is acquired on the predisposition haplotype. Alternatively, it is possible that genotype-specific genomic variation in the JAK2 haplotype block increases the somatic mutation rate at this locus, as has been observed for germline variants in the APC gene ..."（後者引用 P10 Laken 1997）
- **沒找到功能差異〔論文〕：** "We did not observe genotype-specific differences in JAK2 expression ..., nor did we observe genotype-specific nonsynonymous sequence alterations or alterations in the 3′ UTR."
- **家系〔論文〕：** 25 個 MPN 家族中，rs10974944 genotype 和 MPN 沒有關聯（作者註明 unpublished data）。

## 限制

- 〔論文〕作者自己說：SNP 資料來自病變組織；strand-ambiguous SNP 造成基因組覆蓋不完整；樣本數相對小。
- 〔論文〕機制未定：選擇優勢與突變率兩種解釋並列。
- 〔推論〕只有一個基因座，而且是特定 driver（V617F）。偏向可能來自 driver 的選擇，不代表 passenger SNV 也偏。
- 〔推論〕只看到「有 V617F 而被診斷的人」。V617F 落在 C 那條但沒有擴增的細胞看不到，所以無法分開發生率和選擇。
- 〔推論〕MPN 是血液腫瘤，不是實體腫瘤。
- 〔推論〕G allele 來自父或母沒有測。這是 germline haplotype 效應，不是 parent-of-origin 效應（同 `08_parent_of_origin.md` E8-17 Jones 2009 的判讀）。

## 對本研究的意義〔推論〕

- 不推翻全基因組「SNV 在兩條 HP 各約 50%」的暫定 null。它只說明：在特定基因座，一條 germline haplotype 可以帶較多 somatic driver。
- 若 diplosim 日後要納入這種效應，應做成「特定基因座、依 germline allele 的局部偏向」，記在 haplotype 上，不是記在父／母上。SNV-only 第一階段不需要。
- N3 層級：單一基因座的觀測關聯，只支持「觀測特徵」層；不提供克隆結構或演化路徑的證據。
