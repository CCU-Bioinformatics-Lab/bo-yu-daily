# 01. 資料來源與高可信度 somatic call set

## 1. 研究材料

研究使用同一 donor 的配對細胞株：

- `HCC1395`：triple-negative breast cancer cell line，作為 tumor。
- `HCC1395BL`：匹配的 B-lymphoblastoid normal cell line。
- gDNA 從 fresh cultured cells 萃取，分送到不同測序中心；不是從一份臨床腫瘤切片直接建立。

研究設計包含 bulk WGS、bulk WES、targeted deep sequencing、PacBio long-read、microarray、karyotype 與 single-cell CNV。Table 1 的主要數字如下：

| 用途 | 技術 | 論文列出的資料量 |
|---|---|---|
| discovery WGS | Illumina HiSeq | 6 centers、12 libraries；tumor/normal 各約 21 billion reads、約 750× |
| discovery WGS | Illumina NovaSeq | 1 center、9 libraries；tumor/normal 各約 13 billion reads、約 400× |
| high-depth rescue | HiSeq tumor-content | 1 center、3 libraries；約 350× |
| high-depth rescue | pooled NovaSeq | 9 個 NovaSeq replicates 合併約 400× |
| pooled short-read | 全部短讀長資料 | tumor-normal 各約 1,500× |
| orthogonal WGS | PacBio | 約 40× |
| WES | HiSeq | 6 centers、12 libraries；約 2,500× |
| WES | Ion Torrent | 約 34× tumor、47× normal |
| targeted validation | MiSeq AmpliSeq | 約 2,900× tumor、3,300× normal |
| single-cell CNV | 10x Genomics | Table 1 列出 1,465 tumor 與 983 normal cells；Fig. 4 以 QC 後 1,270 tumor 與 638 normal cells 作圖 |

論文正文有一個需保留的計數差異：研究設計段落提到 seven sequencing centers，而 Fig. 1 caption 寫 six sequencing centers；Table 1 則把 HiSeq 的 six centers 與 NovaSeq 的 one center 分開列出。這不影響「跨中心、多 replicate」的設計結論，但不應在新文件中把中心數當成沒有歧義的唯一 metadata。

來源：論文 PDF p. 2（Table 1 與 Study design）、PDF p. 3（Fig. 1）。

## 2. 從 21 個 WGS replicate 到 378 個 call sets

原始 somatic call set 的主要架構是：

```text
21 tumor-normal WGS replicates
        × 3 aligners
        = 63 tumor-normal BAM pairs
        × 6 somatic callers
        = 378 caller/alignment call sets
        ↓
SomaticSeq + NeuSomatic + cross-replicate/center/aligner evidence
        ↓
HighConf / MedConf / LowConf / Unclassified
```

三個 aligner 是 BWA-MEM、Bowtie2 與 NovoAlign；六個 somatic callers 是 MuTect2、SomaticSniper、VarDict、MuSE、Strelka2 與 TNscope。

SomaticSeq 的 classifier 不是直接把一個 caller 的結果當 truth：研究用 BAMSurgeon 在 normal replicate 中 spike-in 約 100,000 SNVs 與 20,000 indels，建立兩組 training data，再交換 training/test data 做 cross-validation。論文報告 SNV 的 sensitivity、specificity、PPV、NPV 分別為 98.39%、99.23%、99.52%、99.86%；indel 對應數字為 96.96%、98.03%、98.08%、99.67%。

這一步的用意是讓 classifier 學到不同 sequencing center、aligner 與 caller 的 artifact，而不是只複製某一份 BAM 的判斷。

來源：PDF p. 2–3、Methods 的 `Building center- and aligner-specific SomaticSeq classifiers`。

## 3. 低 VAF rescue 與 conservative confidence labeling

論文沒有只用 21 個一般深度 replicate：

1. 以 350× HiSeq 與 400× pooled NovaSeq 資料 rescue 低 VAF calls。
2. 合併全部短讀長資料成 1,500×，用 NeuSomatic 再找低 VAF calls。
3. 若 HighConf/MedConf call 在 PacBio 不支持，且位於 low-mapping 或 low-complexity region，則降級為 LowConf。
4. 最後把 HighConf 與 MedConf 合併成 somatic reference call set；LowConf 與 Unclassified 不納入高可信度區域。

因此「高可信度」不是單純由 VAF 高低決定，而是由 reproducibility、classifier evidence、深度 rescue、long-read consistency 與可比對區域共同決定。

在 consensus callable region 的建立上，研究對 126 個 BAM（63 tumor + 63 normal）使用 GATK CallableLoci，排除低 coverage、超高 coverage、低 MQ、低 BQ 等區域；再以多數 replicate、data group 與 aligner 的規則取得 consensus regions，並移除 LowConf/Unclassified 周圍 20 bp 以及 chr6p、chr16q、chrX 的 germline LOH 區域。

來源：PDF p. 3–5、Methods 的 `Determine high-confidence genomic regions and somatic mutation reference call set`。

## 4. 最終 call-set 的驗證量級

三個 orthogonal validation experiment 的 unique-count 彙總是：

| 類別 | HighConf + MedConf | 可判讀數 | 已確認 | 可判讀 validation rate |
|---|---:|---:|---:|---:|
| SNV | 1,428 | 1,418 | 1,417 | 99.93% |
| indel | 82 | 80 | 78 | 97.50% |

若把不可判讀位置也算成未確認，SNV 與 indel 的總 validation rate 分別是 99.2% 與 95.1%。這些是 call-set 的 validation rate，不是 high-confidence candidate branching tree topology 每一條演化樹 edge 的 validation rate。

來源：PDF p. 5、Table 2。

## 5. 這些資料如何供樹使用

論文在 HCC1395 heterogeneity 段落同時分析 bulk WGS/WES 的 clonality 與 10x single-cell CNV；其中 bulk evidence 用於 bulk clonality/PhyloWGS 的 high-confidence candidate branching tree topology 推理，10x single-cell CNV 用於檢查 cell-level CNA heterogeneity。正文與 Methods 沒有公開該 topology 的完整 input table、VCF 版本、每個 mutation 的參數轉換或 command line。因此可以確認「輸入證據層級」，不能從這篇文章反推出一份完整可重跑的 PhyloWGS preprocessing contract。
