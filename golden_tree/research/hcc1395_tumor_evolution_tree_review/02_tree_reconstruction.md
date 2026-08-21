# 02. 腫瘤演化樹如何重建

## 1. high-confidence candidate branching tree topology 是什麼

high-confidence candidate branching tree topology 是一棵 rooted tumor phylogenetic tree（原論文第 4a 圖）：

```text
Normal cells
    │
 S1: MRCA ── PIK3CA ── S2: 60% ── S4: 51% ──┬─ S7: 29%
    │                                         └─ S5: 14%
    └─ S8: 34% ── S9: 27% ── S10: 25%
```

圖中：

- `S1` 是所有 tumor cells 的 most recent common ancestor（MRCA）。
- `S2`–`S10` 是不同 cancer cell fraction 的 subclones；`S3`、`S6` 因低於 10% 沒有畫出。
- 邊旁的 `TP53; PTEN; GATA3; NF1; MAP3K1`、`PIK3CA`、`KRAS`、`CASP8; SF3B1` 是作者標示的 driver-gene mutations。
- `S2:60%`、`S4:51%`、`S8:34%` 等是 cancer cell fraction 標籤，不是單一 SNV 的 VAF。
- 樹表達的是 branching evolution：從 S1 分成以 S2 與 S8 開始的兩個主要分支。

來源：PDF p. 7（printed p. 1157）、Fig. 4 caption。

## 2. PhyloWGS 在這篇文章的角色

論文正文只明確寫出：

論文指出，PhyloWGS 產生的原論文第 4a 圖候選樹呈現 branching evolution；本研究將這個結果命名為 **high-confidence candidate branching tree topology**。

也就是說，PhyloWGS 負責把 bulk somatic mutation/CNA 的 clonal prevalence evidence 整合成一個樹狀模型。論文引用的原始方法是 Deshwar et al., *PhyloWGS: reconstructing subclonal composition and evolution from whole-genome sequencing of tumors*（本文 reference 48）。

原文沒有在 HCC1395 這篇 resource paper 中列出：

- high-confidence candidate branching tree topology 實際使用的完整 SSM/CNV input file；
- 每個 SNV 的 exact VAF、local CN、multiplicity 或 purity table；
- PhyloWGS 的 command line、random seed、chain 數、burn-in、posterior sample 數；
- 每個 SNV 對應到 S1–S10 的完整 assignment table；
- tree posterior probability、edge support 或 topology bootstrap。

因此可以說「作者用 PhyloWGS 推導 high-confidence candidate branching tree topology」，但不能把它重述成一個文章內已完整公開且可逐步重現的 inference artifact。

## 3. Copy-number-aware clonality

同一研究的 SuperFreq 分析提供了較清楚的計算語意。Methods 說明：

1. 使用 capture WES 的 HCC1395/HCC1395BL mapped、mark-duplicate BAM。
2. 使用其他 HCC1395BL replicate 作 background filtering。
3. 以 SuperFreq default parameters 進行 somatic SNV 與 CNA analysis。
4. 每個 somatic SNV 的 clonality 由 VAF 計算，並 accounting for local copy number。
5. SNV 與 CNA 依 clonality 以及跨 replicate 的 uncertainty 做 hierarchical clustering。

這代表樹上的 CCF 不能從 `ALT / (REF + ALT)` 直接讀出。至少要把 local CN 與 VAF 的關係納入，否則同一 VAF 在不同 copy-number state 可能代表不同的 cell fraction。

論文還用 subHMM 從 Illumina WGS 的 log OR、log R 出發，先做 library-size 與 GC normalization，再以 HMM 同時做 segmentation、genotype mixture modeling，估計 clonal/subclonal CNA genotype 與 clonal proportion。subHMM 允許不同 subclonal region 有不同 proportion，因此不同區域的 CNA pattern 可支持不同 subclone。

來源：PDF p. 7、Methods PDF p. 13 的 `Cell line clonality analysis` 與 `CNV analysis with WGS`。

## 4. SuperFreq、PhyloWGS 與 single-cell CNV 的分工

| 模塊 | 主要輸入 | 主要輸出／作用 | 是否直接產生完整 SNV tree |
|---|---|---|---|
| PhyloWGS | bulk WGS/WES 的 somatic evolution evidence | high-confidence candidate branching tree topology 與 subclone CCF | 是，依論文描述 |
| SuperFreq | capture WES tumor-normal BAM、local CN、replicates | SNV/CNA clonality、hierarchical clustering、river plot | 否；是獨立的 bulk clonality 支持 |
| subHMM | Illumina WGS 的 log OR/log R | clonal/subclonal CNA segments、genotype、proportion | 否；提供 CNA 演化支持 |
| 10x single-cell CNV | 單細胞 DNA libraries | 每個 cell 的 integer-scaled CNA profile 與 clusters | 否；驗證 CNA 異質性，不是 SNV lineage tree |

## 5. 為什麼可以得到 high-confidence candidate branching tree topology

合理的證據鏈是：

```text
bulk VAF + local CN
        ↓
SNV clonality / cancer cell fraction
        +
clonal/subclonal CNA pattern
        ↓
PhyloWGS / SuperFreq 的 clone structure
        ↓
S1 MRCA → S2 branch and S8 branch → descendant subclones
        ↓
single-cell CNV、karyotype、ASCAT、subHMM 做異質性與基因組背景確認
```

這是「資料與模型相互一致」的 branching hypothesis。它不是從 single-cell SNV genotype 逐個 cell 直接追蹤出來的樹。
