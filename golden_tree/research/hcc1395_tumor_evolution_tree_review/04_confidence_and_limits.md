# 04. 高可信度的真正含義與限制

## 1. 為什麼這篇論文的證據強

論文的強項在於不同誤差來源被分開處理：

| 可能問題 | 論文的處理 |
|---|---|
| 單一 caller 的 false positive | 六個 caller 並行，配合 SomaticSeq/NeuSomatic |
| 單一 aligner artifact | BWA-MEM、Bowtie2、NovoAlign 交叉比較 |
| 單一 center/replicate 偶然訊號 | 21 replicates、多中心、多 platform |
| 低 VAF 被一般深度漏掉 | 350×、400×、1,500× rescue |
| 短讀長 mapping/complexity 問題 | PacBio long-read discordance filter |
| 不可判讀的 genomic region | GATK CallableLoci、consensus callable regions、LowConf/Unclassified exclusion |
| purity/VAF 不合理 | tumor-normal titration 與 VAF fitting score |
| diploid 假設不成立 | karyotype、CytoScan、ASCAT、subHMM、single-cell CNV |
| 單一 bulk clonality 分析偏差 | PhyloWGS 與 SuperFreq 的結果交叉支持 |

所以更精確的說法是：high-confidence candidate branching tree topology 是由高品質 mutation evidence 與多種 copy-number/heterogeneity evidence 支撐的高可信度候選演化樹。

## 2. 哪些內容有直接數字驗證

有直接 validation rate 的主要是：

- HighConf/MedConf somatic SNV/indel 是否被 AmpliSeq、Ion Torrent WES、HiSeq WES 確認。
- PacBio 是否有支持以及 discordance 是否需要降級。
- VAF 是否在 tumor-normal titration 中按照 purity 改變。
- callable region 與 low-quality region 的排除效果。

這些數字可稱為 mutation call-set confidence；不能直接改名成 tree topology confidence。

## 3. 哪些內容是交叉一致性，而不是獨立 truth

以下內容是支持 tree 的重要證據，但不是逐邊 ground truth：

- PhyloWGS 產生的 S1–S10 topology。
- SuperFreq 從 bulk WES 得到相似的 clonality / subclone pattern。
- subHMM 與 ASCAT 得到的 clonal/subclonal CNA。
- 10x single-cell CNV heatmap 顯示 subclonal CNAs。
- driver mutations 位於 MRCA 或 branch 的生物學解讀。

其中 SuperFreq 與 PhyloWGS 都依賴 bulk sequencing evidence，不能簡單視為完全獨立的實驗；single-cell 只量 CNV，不是同一套單細胞 SNV genotype。故「多工具同意」增加可信度，但不等於有一份完全獨立的 lineage truth。

## 4. 不能誇大的結論

不應寫成：

- 「作者用 single-cell sequencing 直接驗證了每個 SNV 的 clone assignment。」
- 「S1–S10 是 HCC1395 唯一真實演化樹。」
- 「所有 tree edges 都有獨立的 posterior probability 或 validation rate。」
- 「PacBio long-read 已用 read-level phase blocks 重建這棵樹。」
- 「論文已公開完整 PhyloWGS input 與 command，可無歧義重跑 high-confidence candidate branching tree topology。」

較準確的寫法是：

> 論文使用 copy-number-aware bulk clonality inference 產生 high-confidence candidate branching tree topology，並以 SuperFreq、CNA、karyotype 與 single-cell CNV 結果確認其整體生物學一致性；mutation call 的真實性則由多平台正交定序與 tumor-normal titration 高度支持。

## 5. 細胞株本身的外推限制

HCC1395 是可持續培養的癌細胞株，不等同於一個 primary tumor。作者也明確提醒它不代表所有 TNBC genome；cell culture expansion 可能造成 genetic drift，且細胞株的 branching event 可能發生於體內或培養期間。這使它非常適合作為 benchmark material，卻不適合當作所有病人腫瘤演化的普遍模板。

## 6. 論文內部的 metadata caveat

review PDF 時有幾個數字或引用需保留原文脈絡，不宜自行挑一個版本當成唯一真值：

- Results 段落提到 seven sequencing centers，但 Fig. 1 caption 寫 six；Table 1 將 HiSeq 的 six centers 與 NovaSeq 的 one center 分開列出。
- HiSeq WES 的 library/repeat 數在 Table 1、Fig. 2 caption 與 supplementary methods 的描述不完全一致。
- Fig. 2 與 supplementary table 的 HighConf SNV count 有 100 個差異。
- AmpliSeq 的約 2,000× 是 validation rule 所用的概略 depth；Table 1 的 tumor/normal depth 另列為約 2,900×/3,300×，不應直接當成同一欄位。
- Extended Data Fig. 9b 的 caption 將 subHMM 引用標為 `38`，但 bibliography 中真正對應 subHMM 的 reference 是 `55`；這看起來是論文 caption 的引用編號問題。

這些 caveat 不會推翻「多平台、多 replicate、多方法交叉支持」的主結論，但會降低對某個單一 exact metadata 數字或完整重跑設定的信心。
