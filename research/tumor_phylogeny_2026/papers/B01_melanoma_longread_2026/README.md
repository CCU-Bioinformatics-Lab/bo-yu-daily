# B01｜23 個單細胞衍生小鼠 melanoma sublines 的 ONT 演化樹

## 論文與定位

Liu Y, Goretsky A, Keskus AG, et al. **Long-read sequencing of single cell-derived melanoma sublines reveals divergent and parallel genomic and epigenomic evolutionary trajectories.** *Nature Communications* 17, 8740 (2026). DOI：[10.1038/s41467-026-75172-9](https://doi.org/10.1038/s41467-026-75172-9)，2026-07-16 發表。保存正式出版 PDF，21 頁；查核日期 2026-10-15。

**第二類核心：真實 long-read 資料建樹，但不是人類病人，也不是直接對單細胞做 long-read scDNA-seq。** 23 個 B2905 小鼠 melanoma sublines 各由單一細胞培養擴增，再對每個 subline 做 bulk ONT WGS。既有 scRNA、WES 是表型或正交對照；它們不會把這個實驗變成人類病人的單細胞 truth tree。主文 p18 明確說沒有使用 human sample。

本研究很適合作 **long-read-derived clone genomes 與演化分析的 benchmark resource**，但其樹仍是 inferred reference。尤其不能稱「TreeHarmonizer 以 SV／methylation 共同重建 topology」：先用 long-read SNV 建樹，其他事件之後放上固定的樹。

## 從 reads 到樹的確切流程

主文 p2–4 Fig. 1／2：每 subline 一張 ONT R10.4 PromethION flow cell，平均 69.77 Gbp，read N50 約 29.1 kb；matching-normal 為相應遺傳背景的鼠 spleen。DeepVariant 呼叫 SNV，去掉 normal 與 FVB strain variants；Severus 多樣本呼叫 SV；Wakhan 依 coverage、SV breakpoints 估 CN；ONT 原生 5mC 給 BSmooth 做 DMR。23 個 sublines 產生有 4 大 clades 的樹，Fig. 2a（p4）把 SNV、SV、CN summary、DMR 與表型放在同一 lineage framework。

主文 p12–13：只保留 phylogenetically informative SNV；排除任一 subline 有 deletion 的區域，避免 infinite-sites violation，並排除 private／全體共有變異、低 coverage、不可靠 VAF 與背景 alt support。從 277,818 個 informative SNVs 得到 **10,862 個建樹位點**。ScisTree 對 8 組 FP、7 組 FN、100 個 cell-order permutations 搜尋，共 5,600 棵候選，選最高 likelihood。每位點 coverage≤10 標為 missing，平均／中位 coverage<20 再篩掉。這是 error-aware SNV tree，並沒有以 multi-read co-occurrence likelihood 直接優化 topology。

**TreeHarmonizer 是 downstream placement（p3、p13–14）。** 輸入既定 tree＋per-subline SNV／SV／CNA；尋找 carriers 的 MRCA，考慮 FN、附近 deletion，再決定 placed／unplaced。作者明說它假設 input topology 最佳，既不評估也不修改樹。SNV 與 SV 各約 96.71%、95.49% 能放置；CNAs 主要報每個 branch 影響的 genome percentage，不是對每個重疊 CN event 完成唯一時序分解。DMR 是在 tree-defined bipartitions 做比較，不能拿其與樹一致性當作獨立建樹驗證。

## haplotype、CNV／LOH、purity／VAF／CCF 的重點

這篇標題很符合 long-read evolution，但 **HP1／HP2 訊號並不是主貢獻**。p12 雖描述 margin／WhatsHap 的準備，隨後明確說鼠株高度 inbred、缺乏 germline heterozygosity，因此無法做有用的 germline phasing；Wakhan 使用 **unphased mode**。不能把這批資料當作測試本 repo PS block／HP-specific CN 的首選。

每個 subline 已培養近 clone，heterozygous clonal／subclonal placed variants 在 subline 的 VAF 大多近 0.5；這與混合 bulk 腫瘤的 CCF inference 問題不同。資料能測 variant loss、CN／SV placement，但不自然涵蓋 normal contamination、low purity 與多 clone deconvolution。初始樹排除大多 deletion-impacted SNV，使其對高 CN complexity 問題的答案帶有位點選擇條件。

TreeHarmonizer 後續用 deletion 解釋 ancestral SNV 為何在後代缺失，值得本 repo 參考；但 p14 也說 copy-neutral LOH、重疊 gain/loss 且沒有 informative breakpoints 等仍未完整處理。若把「未見 SNV」一律當作未繼承，會產生假 branching。本文的 high placement rate 亦是對自己推得 tree 的一致性，不等於實驗觀察到歷史的絕對正確率。

## 接到本 repo：建議與最小 ablation

以下為**分析推論**，C0–C6 名稱依據 `plan.md` §4：

- **C0／C1**：可重用公開 ONT＋variant calls 建 clone-genome mixtures，記錄 subline／read／variant provenance，並以 coverage eligibility 控制 missing。
- **C2／C3**：這篇不適合驗證 HP／PS likelihood，因 germline phasing不足。若人工混入 normal、不同 sublines，可評估 CN／VAF／purity 對 CCF 的影響，但那是新增的 simulation，不是原論文的實測 truth。
- **C4／C5**：樹由讀出的 SNV genotype 建立，不能將同一 SNV set 的 read pairs 再視作獨立 truth。建議按 genomic blocks 留出：一部分建立 reference，另一部分量化 co-read constraints 對 ambiguity 的改善。
- **C6**：借鏡 placed／unplaced report，將 deletion-rescued、low-coverage、CN-ambiguous、與 reference topology 衝突分開。需要同時輸出 topology uncertainty，因本研究只有選定最佳 tree 與 variant placement。

最小 ablation：以已建的四大 clades 為 reference，固定 mixture composition 與 input SNVs，做 baseline、`+CN-loss-aware masking`、`+C4`；跨部位留出並報 ancestor relation、variant assignment 與 unplaced fraction。另以 unchanged topology 的 placement-only 分析當 downstream control，避免把 placement 改善錯算 topology 改善。此資料適合方法開發；臨床外推仍需病人 scDNA cohort。

## 資料與定位

Data availability（p18）：原始 ONT **PRJNA1307171**；既有 bWES **PRJNA891351**、scRNA **PRJNA891349**、bWTS **PRJNA891350**。processed source data／variant calls：[Zenodo 20072601](https://doi.org/10.5281/zenodo.20072601)。PDF 中 DOI 後緊接 reference 128，文字抽取會看似 `20072601128`，正確 DOI 由 Fig. 2 hyperlink 與 Code availability 相互核對為 `20072601`。程式：[TreeHarmonizer](https://github.com/KolmogorovLab/TreeHarmonizer)。

證據定位：p2 實驗、p3 明確固定 topology、p4 Fig. 2、p11–13 calling／filtering／tree inference、p13–14 deletion 與 CN limitation、p18 data。已實際渲染讀取 p4 Fig. 2；頁數均為 PDF physical page。

- [paper.pdf](paper.pdf)：[官方下載](https://www.nature.com/articles/s41467-026-75172-9.pdf)，21 頁，`file`／`pdfinfo` 已驗真。
- SHA256：`8811bc50ebff622b1b3663f9b25e9a749e818488a7510fb67a49187557ceb475`。
- [paper.txt](paper.txt)：`pdftotext -layout`，保留 page breaks。
