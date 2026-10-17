# B02｜真實 multiple myeloma：scRNA 加 linked reads 限制 clonal relationship

## 論文與定位

Liu R, Gao Q, Foltz SM, et al. **Co-evolution of tumor and immune cells during progression of multiple myeloma.** *Nature Communications* 12, 2559 (2021). DOI：[10.1038/s41467-021-22804-x](https://doi.org/10.1038/s41467-021-22804-x)，2021-05-07。正式出版 PDF，18 頁；查核日期 2026-10-15。

**真實病人＋single cell＋long-range molecule information 的重要交集，但 single cell 是 scRNA，long-range 是 10x linked-read WGS。** 它有直接的 NRAS mutation 關係約束，仍不是 direct long-read scDNA，也沒有獨立 single-cell DNA truth tree。不可因同時出現 10xWGS、scRNA 就稱為 single-cell long-read genome sequencing；兩種 library 的 cell barcode／molecule barcode 語義不同。

14 位病人、29 個 longitudinal samples；所有病人至少有一個時間點同時具 scRNA 與 10x linked-read WGS，9 位具兩個以上時間點（p2）。研究包含 SMM、primary、remission、relapse，並有 bulk RNA／WGS／WES、FISH 與額外 CyTOF 作整合。17,267 plasma cells、57,719 immune cells 是論文摘要所列細胞數；不同段落的 retained-total 有細微不一致，不另行拼出更精確的 unique-cell count。

## long-range feature 是否真的影響演化判斷

**是，作用在特定 pair 的 clonality model。** p11 Fig. 6d–e 是關鍵：patient 27522 有 NRAS G13（chr1:114716124 C>G）與 Q61（chr1:114713909 A>T）。bulk VAF trajectory 本身可容許「Q61 是 G13 子 clone」或「兩者獨立」等解釋；作者用相鄰 germline variants 指派 linked-read molecules 到 haplotype，再看同 molecule 是否帶雙突變。

兩個 NRAS mutation 均在 haplotype 2，但覆蓋兩位置的 linked-read evidence 沒有雙突變；主文報 n=4，據此偏好它們屬於 independent subclones。Fig. 6 的 fishplot 因此畫成兩個分支。這恰好說明 **同 germline HP 不代表同 clone**；只有含兩個位置的實際 molecule observation 才直接約束兩 mutation 關係。另一方面，n=4 的陰性共現證據很弱，不能一般化為「零個 double mutant ⇒ 絕對 branching」。linked-read barcode 亦不是唯一 cell ID，需控制 barcode collision 與 molecule reconstruction。

Methods p14：Long Ranger 2.2.2 處理 linked-read WGS，GATK 呼叫 variants；利用相同 linked reads 周圍 germline variation 做 somatic haplotype assignment。p16 Subclonal analysis 說 bulk clonal architecture 由 **SciClone** 定義，tumor phylogeny 用 **Fishplot** 呈現；Fishplot 本身是呈現工具，不是獨立的 tree inference 或 truth 產生器。這篇的價值是 mechanistic constraint＋longitudinal clinical interpretation，不是新發明的 posterior topology sampler。

## single-cell 證據到底回答什麼

scRNA 用 gene expression、inferCNV、已知 somatic variant 的單細胞 mapping，把 longitudinal plasma subpopulations 接上 genomic events（p3、p9–11 Fig. 5）。例如 relapse-2 的 mutations 主要出現在 RL2.1，搭配 t(4;14)、chromosome 13／16 loss 幫助辨識不同 plasma-cell populations。文中也觀察同一細胞多個已知 variants。

但 scRNA coverage 稀疏、有 allele-specific expression、RNA dropout，CNV 為表達推估；沒有 mutant RNA 的 cell 不能當作 DNA wild type。因此 scRNA 是 clone-to-phenotype mapping 的佐證，不能把 t-SNE distance／expression cluster 直接當 genetic lineage tree。NRAS 分支結論的直接 molecule evidence 來自 bulk 10xWGS，而非對 scRNA 完整突變矩陣重建後的獨立 DNA tree。

## purity、VAF、CCF、CN／LOH、HP／PS 的限制

Fig. 6a／c 以 VAF clustering 為主，p11 mutation frequencies 的變化可以反映 clone expansion，也會受 plasma-cell fraction、CN、採樣與 treatment 影響；不能把 VAF 直接乘二當普遍 CCF。這個 cohort 的 del(13q)、hyperdiploidy、translocations 本來就需要與 SNV 層共同解讀。本文沒有提供可直接移植的 PhyClone haplotype-specific multiplicity likelihood，也沒有用 long-read-derived allele-specific CN 聯合推 purity／CCF。

它的 NRAS 例子與本 repo C4 方向契合，但在 amplified HP 上多個 copies 可存在於同一 cell、不同 molecule，absence of `11` 未必表示分支。germline block 的 HP 標號也要保留 PS 範圍；不能用「都是 HP2」跨 chromosome／phase block 建 lineage constraints。

## 對本 repo 與最小 ablation

以下為**本筆記分析推論**，依 `plan.md` 的 C0–C6：

- **C0／C1**：將 evidence unit 與 library type 寫入 provenance：ONT 是 read／native molecule，10x linked read 則先重建 molecule，不能逐條 short read 當獨立長分子。保存 `PS/HP` 與 pair denominator。
- **C2／C3**：不應以這篇宣稱改善 allele-specific CN／CCF；可用其臨床 CN／fraction 變化設計 sensitivity cases。
- **C4**：用 NRAS 的同 HP、互斥 mutation pair 作 branch-versus-ancestor 的 worked example；對零 co-occurrence 使用 coverage-aware soft factor，避免硬排除。
- **C5**：檢查 VAF 相近 variants 的 cluster 是否被 molecule constraint 拆分；固定 cluster 的 ablation 需另報有多少 pairs 只落同 cluster。
- **C6**：把 clonal genetic relationship 與 scRNA cell-state labels 分列，輸出 posterior relationship 和實際 molecule counts；不能以 embedding 顏色代替 lineage uncertainty。

最小 ablation：先以公開 NRAS pair 重建 published constraint，再固定 SNV／CN／purity 比較 baseline、真 pair factor、打亂 pair factor，將 molecule coverage downsample 至 2／4／8／更高，量化 branching posterior 對低 coverage 的敏感度。評估單一 relationship 是否被支持即可，不把本文 fishplot 當完整高信心 truth。

## 資料與閱讀定位

全部 sequencing data（10xWGS、WGS、WES、bulk RNA、scRNA）在 **PRJNA694128**；CyTOF **FR-FCM-Z3EP**；另用 CoMMpass ancestry resource **phs000748**（p16 Data availability）。NCBI 登錄號不等於本筆記已下載 raw reads；本次下載並讀的是論文 PDF。

實讀定位：p2 cohort／sample pairing、p3 somatic-to-scRNA mapping、p9–10 Fig. 5、**p11 Fig. 6** linked-read constraint、p14 Long Ranger、p16 SciClone／Fishplot 與 Data availability。已渲染核對 Fig. 6。

- [paper.pdf](paper.pdf)：[官方 PDF](https://www.nature.com/articles/s41467-021-22804-x.pdf)，18 頁；`file`／`pdfinfo` 已驗真。
- SHA256：`861c823952ffade2130699caee9505351d2558a43c6829ead9a491f3b1b781e6`。
- [paper.txt](paper.txt)：`pdftotext -layout`，頁碼以 PDF physical page 為準。
