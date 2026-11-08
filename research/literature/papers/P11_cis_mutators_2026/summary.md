# P11｜1,662 個 LCL 中找到 35 個 mutQTL；其中 2 個被稱為 cis-mutator，但摘要沒說是否證明多出的突變在同一條 haplotype（只讀摘要）

## 論文與結論

Caballero M, Koren A. **Genetic control of local mutation rates.** *PNAS* 123(35), e2625619123 (2026)。DOI：[10.1073/pnas.2625619123](https://doi.org/10.1073/pnas.2625619123)。PMID 42658760，PMC13534546。

- 同儕審查：是（PNAS；Edited by Marcus W. Feldman；received 2026-07-22，accepted 2026-08-03）。
- 讀取層級：摘要（含 Significance）。全文無法取得：PMC 在 embargo，XML 不提供全文，網頁 HTTP 403。
- 查核日期：2026-11-08。

**答案：這篇說明 germline 多型可以和其附近的 somatic 突變率相關，而且相關位點遍布全基因組多處（35 個）。** 這是跨個體的關聯（genotype vs 局部突變率），不是同一個人兩條 haplotype 的比較。摘要說 2 個 mutQTL「functioned as cis-mutators」，但沒寫是否用定相證明多出的突變落在帶該 allele 的那條。這點未核對。

| 查核軸 | 結果 |
|---|---|
| 樣本 | 1,662 個個體的 cell lines（LCL）；另有 CLL 與 germline 變異的比較 |
| 資料與方法 | somatic 突變的染色體分布；控制 DNA replication timing 與 trans-acting 的全域突變率；與 genotype 做關聯（mutQTL） |
| 親代資料／定相方法 | 摘要未提；未核對 |
| 突變類型 | 主要是 somatic（LCL、CLL）；另比較 germline 變異 |
| 對本問題的方向 | (d) 沒量（摘要層級）：沒有直接比較同一個體兩條 haplotype；若 cis-mutator 有定相證據，則屬 (c) |
| 證據類型 | 群體關聯（QTL mapping） |
| 突變率 vs 天擇是否分開 | 作者把它定為突變率（mutation rate）；LCL 突變主要是培養中累積，選擇角色未核對 |

## 實際讀到的證據

全部出自 PubMed／PMC 摘要〔論文〕：

- "we analyzed the chromosomal distribution of somatic mutations in cell lines from 1,662 individuals, controlling for the confounding effects of DNA replication timing on local mutation rates and of trans-acting modulators on global mutation rates."
- "We describe substantial interindividual variation in mutation rates across the human genome."
- "By comparing mutation-rate variation to individuals' genotypes, we identified 35 instances in which polymorphic alleles in the population associate with somatic mutation rates in their vicinity. We call these mutation quantitative trait loci (mutQTLs)."
- "mutQTLs associated with somatic mutations in lymphoblastoid cell lines and in chronic lymphocytic leukemia, and with germline genetic variants."
- "Two of the four mutQTLs inferred to be associated with germline mutation-rate variation were located within large clusters of zinc-finger genes and transposable elements, where they functioned as cis-mutators conferring an increased rate of mutation in their vicinity."
- Significance："In at least some of these cases, the underlying cause of these differences in local mutation rates could be mapped to genetic differences among individuals."

未核對：
- "cis-mutator" 的操作定義（是「附近」還是「同一條 haplotype」）。
- 是否做 phasing，以及多出的 somatic 突變是否落在帶 risk allele 的那條。
- 35 個 mutQTL 的顯著門檻、視窗大小、效應量、在 CLL 的重現數目。
- LCL 突變的來源（培養 vs 活體）。

## 限制

- 〔論文〕摘要用 "associate"，35 個是關聯。
- 〔論文〕cis-mutator 只有 2 個，而且是在 4 個和 germline 突變率變化相關的 mutQTL 之中。
- 〔推論〕"cis" 在 QTL 文獻常指「位置靠近」，不一定指「同一條染色體」。沒有全文，不能把它讀成 haplotype 層級的偏向。
- 〔推論〕LCL 是 EBV 轉化的細胞株，不是腫瘤；CLL 是血液腫瘤。都不是實體腫瘤。
- 〔推論〕跨個體設計：同一個體內兩條 HP 的平衡沒有被直接測。

## 對本研究的意義〔推論〕

- 不推翻全基因組 50% null，但提醒：局部突變率可能隨 germline genotype 改變。若這種效應是 cis（同一條），異型合子位點附近會出現小幅 HP 偏向。
- 要判斷對 diplosim 有無影響，需要全文的效應量與定相結果。現在只能列為「可能的局部偏向來源」，不作為改模擬器的依據。
- N3 層級：觀測特徵層（突變分布），不涉及克隆結構或演化路徑。
