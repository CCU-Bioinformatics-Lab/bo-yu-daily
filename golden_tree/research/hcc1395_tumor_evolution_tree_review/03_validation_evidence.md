# 03. 論文如何驗證高可信度

## 1. 先區分兩種 validation

這篇論文有兩個不同層次的驗證：

1. **Mutation call validation**：確認某個 somatic SNV/indel 是否真的存在，並確認 VAF 在不同 assay 中是否一致。
2. **Evolutionary-model support**：確認 HCC1395 的 clonal/subclonal CNA、ploidy、LOH 與 single-cell heterogeneity 是否支持 high-confidence candidate branching tree topology 所描繪的 branching evolution。

第一層有明確 validation rate；第二層主要是多種資料的一致性支持，沒有逐 edge 的 tree truth rate。

## 2. 三種正交 somatic mutation validation

### AmpliSeq deep sequencing

研究從不同 confidence tier、不同 VAF 與不同 chromosome 抽樣 2,477 個 somatic/germline variants；因為 HCC1395 的 chr6、chr16、chrX 變異過度代表，抽樣時對這些 chromosome downweight。設計成功並完成 coverage 的是 1,368 個 300-bp amplicon regions。

AmpliSeq tumor/normal depth 約 2,000×。判定使用 MQ ≥ 40、BQ ≥ 30，典型規則包括：tumor/normal depth ≥ 600×、tumor variant depth ≥ 100、normal variant depth < 10 時確認；若深度不足或規則無法判定，標為 uninterpretable 或交給 IGV 人工檢查。

HighConf SNV 的可判讀 validation rate 是 244/245 = 99.6%；MedConf 是 18/18 = 100%。

### Ion Torrent WES

Ion Torrent WES 約 34× tumor、47× normal。相同的 MQ/BQ 門檻下，判定會比較依賴 tumor variant depth、tumor VAF 與 normal VAF；例如 tumor variant depth > 2 且 tumor VAF > 10 倍 normal VAF 可確認。

HighConf SNV 的可判讀 validation rate 是 630/636 = 99.1%；MedConf 是 27/27 = 100%。

### HiSeq WES

HiSeq WES 約 2,500×，HighConf SNV 的可判讀 validation rate 是 1,088/1,088 = 100%；MedConf 是 75/75 = 100%。

三種平台合併後，HighConf + MedConf 的 unique SNV 是 1,428 個，其中 1,418 個可判讀，1,417 個確認，得到 99.93% 的可判讀 validation rate。

來源：PDF p. 5、Table 2、Methods 的 AmpliSeq 與 WES validation rules。

## 3. Tumor-normal titration：檢查 VAF 是否隨 tumor fraction 合理變化

研究把 HCC1395 tumor gDNA 與 HCC1395BL normal gDNA 混合，建立 100%、75%、50%、20%、10%、5%、0% tumor purity 的 titration series，並以約 350× WGS 測量。

對 copy-number-neutral region 的真實 somatic mutation，觀察到的 VAF 應隨 tumor fraction 近似線性下降；作者以每個 VAF group 的 linear mixed model 與 MRSE 建立 tumor purity fitting score。HighConf 與 MedConf 的 fit 明顯優於 LowConf 與 Unclassified。

這個實驗的價值是檢查「VAF 對 purity 的反應是否像真 somatic mutation」，不是直接推導 high-confidence candidate branching tree topology。

## 4. PacBio long-read：補足短讀長盲點與 discordance filter

PacBio 約 40× WGS 被當作 orthogonal evidence：

- 用來確認 HighConf/MedConf calls，尤其是短讀長難以 mapping 的區域。
- 對 high-VAF 但 low-mapping/low-complexity 的 calls，若 PacBio 沒有支持且差異達指定統計門檻，降級為 LowConf。
- 論文報告 PacBio 確認 HighConf SNV 約 99.3%、indel 約 98.5%；另有 33 SNVs 與 11 indels 因 PacBio discordance 被移出 reference call set。

這裡的 long-read 用法是 call-set validation 與 filter，不是用 read-level haplotype/PS 直接重建 high-confidence candidate branching tree topology 的 mutation lineage。

## 5. CNA、ploidy 與 LOH 的獨立背景確認

研究用多個層次確認 HCC1395 確實具有適合做 clonality benchmark 的 genomic complexity：

- karyotype 與 cytogenetic analysis：確認 chromosome gains/losses 與 chr6p、chr16q、chrX loss。
- Affymetrix CytoScan HD microarray：提供 genome-wide copy-number background。
- ASCATNgs：從 WGS 估計大量 chromosome gains、losses 與 LOH；CNA-based purity 約 99%。
- subHMM：從 WGS 推導 clonal/subclonal CNA profiles、genotype 與 proportions。

Methods 另記載 ASCATNgs 4.2.1 的 paired tumor-normal WGS 設定：BWA-MEM BAM、hg38 reference、ASCAT SNP panel、`-protocol WGS` 與 default parameters。論文列出的 command 是：

```text
ascat.pl -tumour tumor.bam -norm normal.bam \
  -reference hg38.fa -snp_gc Snp_panel -protocol WGS
```

這些結果不是用來逐一證明每個 SNV assignment，而是確認 tree inference 不能假設一個簡單 diploid、完全 homogeneous genome。

來源：PDF p. 6–7、Extended Data Figs. 5–9、Methods 的 karyotype、ASCAT、subHMM 段落。

## 6. 10x single-cell CNV：檢查細胞層級異質性

10x Genomics Single Cell CNV Solution 產生 Illumina 2 × 150-bp single-cell DNA libraries，Cell Ranger DNA 1.1 做 CNV analysis；作者移除 noisy cells 與 S-phase cells，再以 complete-linkage hierarchical clustering 將 CNV 相似的 cells 聚在一起。

Fig. 4b 是 638 個 HCC1395BL cells，Fig. 4c 是 1,270 個 HCC1395 cells。結果顯示 HCC1395 有 substantial subclonal CNAs，而 HCC1395BL 作為 normal 對照提供不同背景。

這是很重要但需要正確命名的驗證：它直接支持「存在細胞層級 CNV 異質性」，間接支持 bulk clonality tree 的生物學合理性；它不是直接把每一個 SNV 分配到 S1–S10。
