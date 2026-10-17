# B03｜SIGNALS：真實／PDX scDNA 的 haplotype-specific CN 演化，ONT 為正交驗證

## 論文與分類

Funnell T, O'Flanagan CH, Williams MJ, et al. **Single-cell genomic variation induced by mutational processes in cancer.** *Nature* 612, 106–115 (2022). DOI：[10.1038/s41586-022-05249-0](https://doi.org/10.1038/s41586-022-05249-0)，2022-10-26 online。正式 PDF 共 30 physical pages（含 Methods、Extended Data 與後附頁）；查核日期 2026-10-15。

**這是高價值的第一類／橋接研究，不是「long-read features 直接建立樹」的第二類核心。** 它有大量 real scDNA、patient tissues、PDX、haplotype-specific CN、single-cell trees，以及同樣本 nanopore sequencing；但主文 p6 清楚說樹來自 **total CN breakpoints**，long reads 用來驗證特定 complex rearrangements。不能用標題含 single cell、Methods 有 ONT，就推稱 ONT phase 特徵決定 topology。

## 實驗設計與樣本要分開

研究先在 184-hTERT mammary epithelial isogenic cell lines 比較 WT、TP53 knockout、TP53＋BRCA1／BRCA2 knockout，合計 **13,818 genomes**（p1–2）。這是控制實驗，不是病人。

臨床 meta-cohort 為 **309 病人**（170 HGSC、139 TNBC）的 bulk WGS。由中選 **23 cases：16 HGSC、7 TNBC**，產生／利用 PDX 並結合 primary patient tissues，得到 **22,057 scDNA genomes**（p4）。所以 309 不是 scDNA 病人數，22,057 也不能全叫原位病人單細胞。單細胞 DLP+ median coverage 約 0.05×，正是需要 haplotype blocks／跨細胞整合的原因。每張 Fig／sample 的 tissue-versus-PDX 需查原始 metadata，不能以 cohort 全部混稱 human patient ground truth。

## 從 single-cell reads 到 haplotype CN 與樹

p2、p14 Methods：DLP+ 取得真實單細胞 genome；HMMCopy 提供 total CN。**SIGNALS** 使用單細胞中 genotyped haplotype blocks，配 Beta-Binomial likelihood 的 HMM 估 haplotype-specific CN（HSCN）。這能區分 total CN 相同但分別保留 A／B allele 的 cells；total CN 的 1 不足以判定究竟失去哪條 homolog。

**tree 先後順序不可寫錯。** p6 的 Haplotype-specific parallel evolution 明講，用全 genome **total-CN-inferred breakpoints** 建 phylogeny；p14 由 sitka posterior 取 consensus tree，之後把 HSCN 狀態映射在 tips，檢視同一或不同 clades 是否發生 alternate-haplotype gains／losses。Fig. 5（p8）展示 SA1049 chr1q、SA1053 chr10q、SA1093 chr8，總 CN 與 HSCN 並列；沒有聲稱 long-read phase evidence 在 sitka tree likelihood 中。

long-read Methods 在 p12：PromethION、Guppy、Minimap2；PDX reads 先對 hg19＋mm10 分離 mouse contamination；MAPQ<60 排除，PEPPER-Margin-DeepVariant phasing＋WhatsHap tag，Sniffles／cuteSV 呼叫 SV，再 SURVIVOR merge。**p6、Extended Data Fig. 9 p26–27** 說 nanopore 單分子讀段驗證 SA1096 chr3／6 rearrangement，以及 MYC／5q 等 complex amplifications。這是 orthogonal SV support，不是用 ONT 推完整 clonal tree。

## 直接關係到本 repo 的科學風險

Fig. 5d–e（p8）非常值得先讀：在不同細胞分別是 `2|1`／`1|2` 或 `1|0`／`0|1` 的情況，同一 clonal SNV 的 VAF 會隨保留哪條 allele 而改變；把 cells 混成 bulk 後，VAF 不再唯一對應 single CN state。作者明確說這使 CCF inference 困難。這是本 repo `C_h` 固定為 clonal 的假設需要壓力測試的實證，不是 HP tag 足夠準就會消失的問題。

parallel CN gains／losses、cnLOH、WGD 可讓相同 total CN 在不同 branches 出現。若將這些 SNV 的 absence 全當 dropout 或 sequencing error，可能把 mutation loss 誤判 branching；反過來同 total CN 的 cells 也可能有相反 parental origin。p14–15 的 ancestral-state event rate 使用 parsimony、unit cost，且作者明示 no-cell-death 假設使速率是 effective rate，不應當作實際每分裂 mutation rate truth。

purity 在 single-cell genomes 與混合 bulk 的語義不同；本研究沒有提供 full bulk ONT purity／CCF posterior benchmark。也不能將 A／B allele labels 無條件翻成 repo across-PS 的全域 HP1／HP2。

## 接到 C0–C6 與最小實驗

下列為**分析推論**，非已完成的 repo 改動：

- **C0／C1**：加入 segment 的 subclonal CN ambiguity、WGD、LOH flags；每個 HP-specific count 保留 PS與 sample provenance。
- **C2／C3**：優先測同 total CN、相反 `C_h` 的 mixtures，而非只在一個固定 `major/minor` 下調 allele count。固定 CN 假設被破壞時應 fallback 或 marginalize，不能將高信心 HP 當高信心 multiplicity。
- **C4**：嚴守 `C_h=1` 且無 subclonal CN／breakpoint；若缺少這種條件，molecule genotype 與 cell genotype 的簡單映射無法保證。
- **C5**：檢查同 CCF cluster 是否混合了不同 CN backgrounds，並比較先分 CN-state 再 clustering 的結果。
- **C6**：借鏡 Fig. 5，將 inferred tree、total CN、HSCN、pair conflicts 並列；標出模型不適用／資料不足，不能只給單一 MAP tree。

最小 ablation：以公開 processed HSCN 選出 total CN 相同、A／B 不同的 cell groups，形成有已知 mixing proportion 的 pseudo-bulk；比較 baseline、C2、C2＋C3，在 fixed versus subclonal CN 兩條件量化 CCF calibration。這個比例來自人工混合而非病人完整歷史 truth。另用 ONT-supported SV 作獨立 validation layer，避免以同一種 CN data 建 reference 又評估自己。

## 資料、閱讀定位與檔案

p15–16 Data availability：[processed Zenodo 6998936](https://zenodo.org/records/6998936)；raw scDNA／scRNA **EGAS00001006343**，既有 scDNA **EGAS00001004448、EGAS00001003190**；bulk data 另有 **phs003038.v1.p1、phs003036.v1.p1、EGAD00001003268**，部分受控或需 MTA。程式 [SIGNALS](https://github.com/shahcompbio/signals)，版本 0.7.2：[Zenodo 6642342](https://doi.org/10.5281/zenodo.6642342)。本文不是所有資料均可免申請下載 raw reads。

實讀定位：p1–2 isogenic design／HSCN；p4 23-case cohort；p6 total-CN tree 與 nanopore validation；p8 Fig. 5（已渲染核對）；p12 long-read Methods；p14 sitka／HSCN／parsimony；p15–16 data；p26–27 Extended Data Fig. 9 validation。

- [paper.pdf](paper.pdf)：[官方 PDF](https://www.nature.com/articles/s41586-022-05249-0.pdf)，`pdfinfo` 確認 30 頁；`file` 的 23-page 提示與總頁數不同，採 pdfinfo page tree。
- SHA256：`eb6086d36613473f256502e2fdfc6655525620f5601e03cf72cce79bf0f1d6bb`。
- [paper.txt](paper.txt)：以 `pdftotext -layout` 產生，保留 physical-page breaks。
