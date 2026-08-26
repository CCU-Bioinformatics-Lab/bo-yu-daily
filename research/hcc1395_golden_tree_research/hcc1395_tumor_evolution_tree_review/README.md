# HCC1395 high-confidence candidate branching tree topology：論文分析索引

本目錄分析：

> Fang et al., *Establishing community reference samples, data and call sets for benchmarking cancer mutation detection using whole-genome sequencing*, Nature Biotechnology 39, 1151–1160 (2021).

主要問題是：論文如何把多來源資料與多層驗證，組合成 HCC1395 的 **high-confidence candidate branching tree topology**（原論文第 4a 圖）。論文 PDF 位於 [`golden_tree/hcc1395_golden_tree.pdf`](../../hcc1395_golden_tree.pdf)。

## 先看結論

這棵樹的可信度不是來自單一演算法或單一 truth label，而是四層證據疊加：

1. 以多中心、多 replicate、多 aligner、多 caller 建立高可信度 somatic mutation call set。
2. 用 bulk WGS/WES 的 VAF 與 local copy number 做 clonality analysis，再以 PhyloWGS 推出 high-confidence candidate branching tree topology；SuperFreq 提供另一個 bulk clonality 分析支持。
3. 用 ASCAT、subHMM、karyotype/CytoScan 與 10x single-cell CNV 檢查 HCC1395 的 ploidy、LOH 與 subclonal CNA 是否符合異質性模型。
4. 用 AmpliSeq、Ion Torrent WES、HiSeq WES、PacBio long-read 與 tumor-normal titration 驗證 mutation call 的真實性與 VAF 行為。

但要保留一個重要界線：論文直接高強度驗證的是 mutation call set 與 CNA/異質性證據；high-confidence candidate branching tree topology 的完整 SNV branch topology 沒有一份獨立的 single-cell SNV truth tree 可逐邊驗證。因此它是高可信度的整合性演化模型，不是唯一且已被逐節點證明的 lineage ground truth。

## 分章閱讀

- [`01_data_and_callset.md`](01_data_and_callset.md)：樣本、定序資料、variant callers、call-set 與 callable region。
- [`02_tree_reconstruction.md`](02_tree_reconstruction.md)：PhyloWGS、SuperFreq、VAF/local-CN 與 high-confidence candidate branching tree topology 的讀法。
- [`03_validation_evidence.md`](03_validation_evidence.md)：正交定序、titration、CNA、karyotype 與 single-cell CNV 驗證。
- [`04_confidence_and_limits.md`](04_confidence_and_limits.md)：什麼可以稱為高可信度、什麼不能誇大，以及證據之間的獨立性。
- [`05_lessons_for_current_repo.md`](05_lessons_for_current_repo.md)：對目前 ASCAT + long-read/HP-count tumor-tree repo 的可移植啟示。
- [`06_evolutionary_model_support_framework.md`](06_evolutionary_model_support_framework.md)：逐層檢查 high-confidence candidate branching tree topology 與 CNA、ploidy、LOH、single-cell CNV 的相容性。

## 論文定位

論文的研究目標是建立可供社群 benchmark 的 HCC1395/HCC1395BL reference sample 與 call set，不是建立一個可套用到所有病人腫瘤的通用 lineage truth。HCC1395 是高度異倍體、含大量 CNA 與複雜 rearrangement 的癌細胞株；這使它適合測試 somatic-calling 與 clonality 方法，也使其演化樹必須在 copy-number-aware 的前提下解讀。
