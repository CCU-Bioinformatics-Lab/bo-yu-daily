# P03｜long read 四代家族：postzygotic SNV 沒有顯著父源偏向（1.38:1，P = 0.09）；germline DNM 81.4% 父源

## 論文與結論

Porubsky D, Dashnow H, Sasani TA, et al. **Human de novo mutation rates from a four-generation pedigree reference.** *Nature* 643, 427–436 (2025). DOI：[10.1038/s41586-025-08922-2](https://doi.org/10.1038/s41586-025-08922-2)。PMID 40269156；PMC12240836。同儕審查。讀取層級：全文（PMC 文字與 PMC XML；Supplementary Note 與補充表沒讀）。查核日期：2026-11-08。

**結論：** postzygotic SNV（PZM）在父源與母源之間沒有顯著差異。比例是 1.38:1（paternal:maternal），Wilcoxon signed-rank P = 0.09。germline 小型 DNM 則有 81.4% 在父源 haplotype（4.38:1）。1.38:1 換算約 58% 父源〔推論〕；方向偏父源，但不顯著，而且只有 10 個人。

| 查核軸 | 結果 |
|---|---|
| 樣本與組織 | 一個四代 28 人家族 CEPH 1463；DNM 只在 G2（2 人）與 G3（8 人）找；DNA 來自 blood（UL-ONT 與 Strand-seq 用細胞株） |
| 定序資料 | long read 加 short read：PacBio HiFi、ONT、Illumina、Element，加 Strand-seq |
| 親代資料 | 有。80 kb 視窗內的 informative SNP，把每條 HiFi／ONT read 指派到父源或母源 haplotype |
| 突變類型 | germline DNM（Fig. 2b：germline SNV n = 626）與 postzygotic SNV（n = 119），共 745 個 de novo SNV |
| 對本問題的方向 | (b) 大致各半（不顯著；點估計偏父源） |
| 證據類型 | 直接定相到 haplotype；正文只給比例，沒給 PZM 的父源與母源計數 |

## 實際讀到的證據

- **PZM 沒有親代偏向：** "By contrast, PZMs show no significant difference with respect to parental origin (1.38:1 paternal:maternal ratio, Wilcoxon signed-rank test, P = 0.09) and no parental age effects (Fig. 2c)."（Results，"De novo SNVs and small indels"）〔論文〕
- **germline DNM 對照：** "In total, 81.4% of germline small DNMs originate on paternal haplotypes (4.38:1 paternal:maternal ratio, Wilcoxon signed-rank test, P < 2 × 10−16)"（同段；指數由 PMC XML 核對）〔論文〕
- **PZM 數量：** "We classify 16% of de novo SNVs as postzygotic in origin (n = 119 PZMs/745 de novo SNVs)."（Discussion）。其中 122 個因 incomplete linkage、7 個因無法定相且 allele balance 顯著小於 0.5 被判為 PZM；10 個未通過 haplotype 驗證，最後 119 個。（Results）〔論文〕
- **高 allele balance 的 PZM 也不偏：** "Such events would previously have been classified as germline but, consistent with PZM expectations, we find no paternal bias associated with these DNMs (Fig. 2c)."（Discussion）〔論文〕
- **定義方法：** "We determined that a DNM was germline in origin if it was present on every read from a given parent's haplotype. Conversely, if a DNM was present on only a fraction of reads from a parental haplotype, we determined that it was postzygotic in origin."（Methods，"DNM phasing and postzygotic assignment"）〔論文〕
- **年齡效應：** Fig. 2c 圖說：germline +1.55 DNMs／年（P = 0.013），PZM P = 0.72；母親年齡 DNM P = 0.54，PZM P = 0.74。〔論文〕
- **傳遞：** 有子女的 4 人中，62 個 PZM 有 40 個（64.5%）傳給下一代；germline SNV 為 242/249（97.2%）。（Results）〔論文〕
- **未核對：** 119 個 PZM 中父源與母源各幾個，正文沒寫；可能在補充表（未讀）。用 1.38:1 推得約 58% 父源〔推論〕；7 個未定相的 PZM 是否計入比例，未核對。摘要的 "no paternal bias"，在正文的實際數字是 1.38:1、P = 0.09。

## 限制

- 作者寫：所有定序資料來自 blood，不能證明每個 PZM 存在於多個組織；用傳遞到下一代當替代證據。（Discussion）〔論文〕
- 作者寫：樣本小，不足以偵測 de novo 與 postzygotic 突變譜的差異。（Results）〔論文〕
- 只有一個家族、10 個人。Wilcoxon 是配對檢定，檢定力低；P = 0.09 不能解讀成「確定各半」，只能說沒偵測到偏向。配對單位（每個人）是本檔推測，未核對。〔推論〕
- 只涵蓋早期胚胎突變，不涵蓋成人組織累積的體突變，也不涵蓋腫瘤。〔推論〕
- **和 P01 重疊：** "Previous Illumina-based analysis of this family<sup>14</sup> identified 605 de novo SNVs ..."，ref 14 是 Sasani 2019（P01）（由 PMC XML 核對，見 `fulltext.md` 檔尾補註）。所以 CEPH 1463 也在 P01 的 33 個家族裡。G2 的 PZM 可能和 P01 的 gonosomal 集合部分重疊；P03 新增 72 個 G3 PZM。兩篇不能當作兩個獨立樣本。〔論文〕〔推論〕

## 對本研究的意義〔推論〕

- 和 P01 一致：早期胚胎的 somatic SNV 沒有明顯偏向父源或母源。這支持 diplosim 用 50% 當 HP 指派的零假設。但點估計約 58% 偏父源、n 很小，所以 50% 仍是暫定值。
- 這篇用 long read 直接把每條 read 定相到親代 haplotype，方法和 diplosim 模擬的資料類型（HP1／HP2）最接近。
- 支持的 N3 層：只有觀測特徵（SNV 在親代 haplotype 的分布）。不支持克隆結構或演化路徑；也不能直接外推到腫瘤。
