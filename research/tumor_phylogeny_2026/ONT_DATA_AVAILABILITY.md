# 有 single-cell 樹的論文：ONT 資料可得性查核

查核日期：2026-10-16。範圍：`papers/` 中有 single-cell 樹的 9 篇（A01–A05、B03、B04、B05、B07）。方法：先讀本機 `paper.txt`／supplement 的 Data availability，再查 repository metadata（EGA metadata API、ENA filereport、GEO、NBDC/DDBJ Search）。**未下載任何資料檔，也未打開檔案驗證格式**；以下「格式」以 repository 頁面所列為準。

證據層級標記：**[論文]** 論文本身寫的；**[repo]** repository 頁面實際看到的；**[推論]** 分析推論。

## 結論

目錄中沒有任何一篇提供可直接公開下載的 ONT BAM／CRAM。實際做過 ONT 的只有 B04 與 B03，兩者都需要申請：

- **B04**：ONT WGS 加同病人 10x scDNA，資料寄存於 JGA，為 controlled access，repository 只列 FASTQ。這是唯一可同時取得 ONT 與 scDNA 的候選，**但它沒有 single-cell ground-truth 樹**（見下方 B04 段落），只能做局部、定性的驗證，不能像 PhyClone 的 HGSOC 那樣拿來替樹打分數。
- **B03**：PDX 有 PromethION 定序，但未寄存任何公開或受控 repository，只能透過 MTA 向作者索取。

## 總表

| 論文 | 有 ONT？ | 格式 | accession | 存取 | 與 single-cell 樹重疊的樣本 |
|---|---|---|---|---|---|
| **B04** 肺癌 long-read phasing | **有** | 只列 FASTQ [repo] | JGAS000349 → JGAD000463（NBDC hum0068）；舊資料 JGAS000065 → JGAD000252/253 | controlled（NBDC DAC Type I，JGAP000001） | scDNA「2 cases」，應為 S8、S20 [推論]；metadata 無樣本 ID |
| **B03** SIGNALS | **有做，未寄存** | — | EGA／Zenodo／dbGaP 皆無 ONT [repo] | 經 MTA 向 Shah lab 索取 [論文] | PDX：SA1096、SA530、SA1184（或 SA1181），皆有 DLP+ 樹 |
| A01 ovarian cfDNA | 無 | — | dbGaP phs002857.v3.p1；Synapse syn66399325 | controlled | — |
| A02 SPRINTER | 無 | — | SRA PRJNA1158752；EGA EGAD00001015411；Zenodo 6998936/7718917；SRA PRJNA770772 | 混合 | — |
| A03 pancreatic snDNA | 無 | — | EGAS00001006024 → EGAD00001009735 | controlled | — |
| A04 CK-AML Strand-seq | 無 | — | EGAS00001007436；ArrayExpress E-MTAB-14420 | controlled | — |
| A05 MPAL DAb-seq | 無 | — | GEO GSE232074（PRJNA970740） | open | — |
| B05 MEDICC2 | 無 | — | 引用 Minussi 2021 TNBC（PRJNA629885，全為 Illumina） | — | — |
| B07 Numbat | 無 | — | PRJNA694128、PRJNA625321、PRJNA498809、GSE148673、GSE142750 | 混合 | — |

## 逐篇說明

### B04 — Sakamoto 2022（肺癌）
- [論文] p16 Data availability 列 JGAS000349 與 JGAS000065，註明 restricted access。supplement 提到分析時使用 fast5 與 mapped BAM，但這不代表這些檔案有寄存。
- [repo] JGAD000463（2021-12-01 釋出，2.3 TB）包含 PromethION WGS（SQK-LSK109）、PromethION 與 NovaSeq RNA-seq、10x scDNA-seq（2 cases、2 個 tumor samples）。JGAD000252（4.3 TB）、JGAD000253（3.0 TB）包含 NovaSeq 與 PromethION WGS。NBDC 頁面的 File format 只列 FASTQ。
  - https://humandbs.dbcls.jp/en/hum0068
  - https://humandbs.dbcls.jp/en/dataset/JGAD000463
- [repo] hum0068 的 controlled-access users 名單中有美國機構（University of Hawaii、Icahn School of Medicine at Mount Sinai）。
- [推論]
  - 海外研究者可以申請，但需要核准的研究計畫，並符合 NBDC security guideline。
  - 拿到 FASTQ 後要自己 align 才有 BAM。若 FASTQ 沒有保留 MM/ML tags，可能無法做 methylation 分析。
  - 公開 metadata 無法逐筆確認 S8、S14、S20 各自有哪些 ONT 檔案。

**scDNA 的實際用途：沒有建出 single-cell 演化樹**（2026-10-16 依本機全文補查）
- [論文] 樹由 bulk 推得：先用 bulk short-read WGS 的 VAF 跑 PyClone-VI，再用 ClonEvol 排出 clonal ordering（paper.txt:1697）。S8、S20 的 PyClone 只有 2 個 cluster，C-1 為 "Major"、C-2 為 "Minor"，因此 topology 只有 C-1 → C-2 一條邊（supplement Fig. S10b–d）。
- [論文] scDNA 為 10x Chromium 單細胞 CNV。用 Cell Ranger DNA 取得 20-kb CN profile 後，以 Manhattan 距離加 complete linkage 做階層式分群並畫成 heatmap（paper.txt:1700–1708）。這是 CN 相似度的 dendrogram，不是用演化模型推出的 phylogeny。
- [論文] 以 mpileup 檢查每顆細胞的 BAM 是否帶有突變，藉此佐證 "Minor" 突變只出現在部分細胞。long-read 能直接判定先後順序的 mutation pair 中，S8 只有 2 對、S20 只有 13 對在單細胞資料中有覆蓋；論文展示了 2 個例子（supplement Fig. S10e–f 與 Note）。
- [論文] 作者自述的限制：單細胞 coverage 低，又有 allele drop-out，"Minor" 突變常偵測不到，需要合併多顆細胞分析；scDNA 只做了 2 例（paper.txt:1391；supplement p.26 Note）。
- [論文] 過濾 noisy cells 後的細胞數，Table S7 為 S8 138、S20 376；Fig. S10a 圖說寫成「138 and 376 cells in S20 and S8」，兩者順序相反。以 Table S7 為準。
- [推論] 與 PhyClone 的 HGSOC 不同。PhyClone 論文的病人 2、3、9 有由 single-cell／targeted 驗證得到、topology 明確的 ground-truth 樹，可以計算 V-measure 與 AD F-score（`../phyclone_research/notes/03_EXPERIMENTS_RESULTS.md` E6）。B04 沒有這類可評分的樹，只能用來驗證 mutation pair 的先後順序與 CN 子群。
- [推論] 若取得 JGA 資料，可以自行用 MEDICC2 等工具重新分析這 2 例的 10x scCNV 並建 CN tree。但這樣得到的仍是推論出來的樹，只有 2 例，SNV 層級的訊號也很稀疏。論文本身沒有做這一步。

### B03 — Funnell 2022（SIGNALS）
- [論文] Methods（paper.txt 約 1984–2004 行）的流程：HMW DNA 上 PromethION 定序，Guppy v3 basecalling，minimap2 比對到 hg19+mm10 以去除小鼠 reads，再用 PEPPER-Margin-DeepVariant／WhatsHap 做 phasing。
- [論文] Extended Data Fig.1 寫明「Long read sequencing, 5 genomes」。內文點名 SA1096（chr3–6 translocation）、SA530（CCNE1）、SA1184（MYC、5q）。ED Fig.9c 的 5q 圖標為 SA1181，與內文不一致；第 5 個 genome 是哪個樣本未寫明。
- [論文] Data availability 沒有提到 ONT；原始資料可經 MTA 向 shahs3@mskcc.org 索取。
- [repo] 以下 repository 都查不到 nanopore／PromethION dataset：
  - EGAS00001006343（361 個 dataset）、EGAS00001004448（275 個）、EGAS00001003190（63 個）：全為 Illumina／BGISEQ。
  - Zenodo 6998936：只有 processed data。
  - dbGaP phs003036／phs003038：頁面未顯示定序平台。
- 簡短搜尋沒有找到 Shah lab 在這批 PDX 上另外釋出的 ONT 資料。

### 其他 7 篇（無 ONT）
- **A01**：資料只有 DLP+ scWGS、bulk WGS 與 cfDNA duplex panel。dbGaP 頁面沒有提到任何 long-read。
- **A02**：PRJNA1158752 的 10 個 run 全是 NovaSeq WGS（HCT116）。EGAD00001015411 是 1 名病人的 DLP+ scWGS（12 個 BAM、1.0 TB），由 PEACE DAC 管理。
- **A03**：EGAD00001009735 的平台只有 Tapestri、HiSeq 4000、NovaSeq 6000，共 187 個檔案。有 bulk 資料的樣本：PR01–PR05 有 WES，PA04 有 WGS。
- **A04**：Reporting summary 寫明只用 Illumina 與 Bionano Saphyr（OGM，不是 sequencing reads）。4 個 EGA dataset 全為 Illumina。相關但不同 cohort 的研究：Klever 2023 在另一個 CK-AML cohort 做了 ONT＋Hi-C，未證實與 A04 是同一批病人。
- **A05**：平台只有 GPL24676（NovaSeq 6000）。ENA 的 31 個 run 都是 PIP-seq cDNA；DAb-seq 是否在 SRA 有 raw reads 未逐一核實。
- **B05**：真實 single-cell 資料只用 Minussi 2021 的 TN1／TN2。PRJNA629885 有 16,492 個 WGS run 加 16 個 AMPLICON run，全為 Illumina。這個 accession 不是 B05 論文列出的，而是查核時憑記憶查到的，內容規模與 Minussi 研究相符。
- **B07**：PRJNA625321（13 個 run）與 PRJNA498809（9 個 run）全為 Illumina。PRJNA694128 在公開索引中查不到 run，可能是受控或尚未公開，未確認。Numbat 的 phasing 是 population-based（Eagle2），不是 read-based。

## 相關資料（不屬於本目錄論文）

- **PRJDB7926**（DRA DRP005565）：B04 作者群公開的 5 株 lung cancer cell line ONT WGS（MinION/PromethION），細胞株包括 LC2/ad、A549、RERF-LC-KJ、RERF-LC-MS 等，為 public access。這批**沒有 single-cell 樹**，也與本 server 上的細胞株都不同。檔案格式未逐一確認。

## 待辦

1. 評估是否申請 B04 的 JGAD000463 與 JGAD000252/253。這是唯一能做「ONT bulk 推樹 vs. 同病人 scDNA 子群」**局部**驗證的資料。它沒有 ground-truth 樹，不能當作 topology benchmark；申請前要先確認這種局部驗證值不值得花時間走流程。
2. 若要追 B03，需要聯絡 Shah lab 走 MTA，並先確認第 5 個 ONT 樣本是哪一個。
