# W8：tumor phylogeny benchmark 補查（2026-10-18）

> 查詢日 2026-10-18。目的：檢查 W5（2026-10-16）與 W7 之後，是否有更新的 tree 推論 benchmark。
> 方法：WebSearch（extended）6 次；Europe PMC REST 關鍵字查詢（2025-06-01 到 2026-10-18，851 筆，逐筆看標題）；重點文章讀全文或摘要。
> 標記：「論文描述」＝原文明寫；「推論」＝我的分析。

## 結論

1. **沒有新的中立 tree 推論 benchmark。** 2025-06 之後沒有期刊或 preprint 以「比較 clone tree／mutation tree 推論方法」為主題。最新的大型 benchmark 仍是 SMC-Het 2024（[M07](../papers/M07_smchet_benchmark_2024/README.md)），它沒有測 PhyClone。
2. **唯一同時比較 PhyClone、Pairtree、CONIPHER 的新項目是一份會議 poster**（EMulSI-Phy）。它沒有 preprint、沒有程式碼，也是作者自家方法。
3. **對本研究最有用的新資源是 Liu et al. 2026（Kolmogorov 組）的 ONT 黑色素瘤 subline 資料**。它是公開的 long-read 資料，並且有 phylogeny 約束的 variant truth set。它可以混成 pseudo-bulk，當作「已知樹的 bulk ONT」測資（推論）。
4. 其他新項目是 simulator 或方法論文自帶的比較，不是中立 benchmark。

## 新項目

| 項目 | 類型 | DOI／來源 | 與 tree benchmark 的關係 |
|---|---|---|---|
| **Liu, Goretsky, …, Sahinalp, Day, Kolmogorov 2026** | 期刊（Nat Commun，2026-07-16） | [10.1038/s41467-026-75172-9](https://doi.org/10.1038/s41467-026-75172-9)；PMC13493970 | 見下節。long-read、有樹、資料公開 |
| EMulSI-Phy（Winata，UCLA） | 會議 poster abstract（Festival of Genomics Boston 2026） | [poster 頁](https://festivalofgenomics.com/boston/poster-abstract-benchmarking-subclonal-reconstruction-algorithms-scalable-multi-sample-cancer-phylogeny-inference) | 比較 DPClust、PyClone、PyClone-VI、CONIPHER、Pairtree、PhyClone；504 組模擬＋400 例 TRACERx NSCLC。只報 task completion（clustering 100%、phylogeny 98.4%）、compute cost、silhouette、sum rule 違反。摘要沒有 tree 正確率數字。頁面日期與頁尾（2027）不一致 |
| SCOUT（Valeriani, …, Caravagna） | bioRxiv 2026-06 | [10.64898/2026.06.09.731105](https://doi.org/10.64898/2026.06.09.731105) | W7 已列。本次讀全文確認：只測 MOBSTER、VIBER、PyClone-VI 與 tumourevo；**沒有測 PhyClone／Pairtree／CONIPHER，沒有 topology 指標**。short-read Illumina；ProCESS 有 ground-truth phylogeny，Zenodo 有 truth 資料，但是否輸出 per-mutation clone label 與 multiplicity 未寫明 |
| SRNJ／DLCA-NJ（Lagergren 組） | bioRxiv 2026-07 | [10.64898/2026.07.30.739152](https://doi.org/10.64898/2026.07.30.739152) | W1 已列為方法。附 sc CN tree 的模擬比較（triplet、root-split distance、clade-F1）。是方法論文自帶比較 |
| SISTEM | Bioinformatics 2025 | [10.1093/bioinformatics/btaf634](https://doi.org/10.1093/bioinformatics/btaf634) | simulator：tumor 演化、轉移、DNA-seq reads，帶 lineage truth。不是 benchmark |
| MOV&RSim | BMC Bioinf 2025 | [10.1186/s12859-025-06292-0](https://doi.org/10.1186/s12859-025-06292-0) | simulator：cancer variant 與 read 特性。不是 benchmark |
| cancerSimCraft | bioRxiv 2024-12 | [10.1101/2024.12.11.627708](https://doi.org/10.1101/2024.12.11.627708) | simulator：記錄 clone 身分與 phylogeny truth。出版狀態未查 |
| NestedBD-Long | bioRxiv 2025-03（RECOMB-CG 2025） | [10.1101/2025.03.17.643834](https://doi.org/10.1101/2025.03.17.643834) | W3 已列。方法論文自帶比較 |
| SCITE-RNA | Genome Biol 2026 | [10.1186/s13059-026-04123-w](https://doi.org/10.1186/s13059-026-04123-w) | scRNA 推樹方法，自帶比較（DENDRO、PhylinSic、Canopy2、PhylEx 等）|

查過但無關：scRNA CNV caller benchmark（Nat Commun 2025、bioRxiv 2026-04）、somatic mutation calling benchmark（SMaHT 2025）、long-read scRNA 工具 benchmark（bioRxiv 2025.07.21.665920）。它們不評估樹。

## Liu et al. 2026：ONT 黑色素瘤 subline 資料（論文描述）

- **樣本**：小鼠 B2905 皮膚黑色素瘤細胞株的 23 個 single-cell-derived subline，加 1 個 spleen normal。
- **定序**：每個 subline 一個 ONT R10.4 PromethION flow cell，平均 69.77 Gbp，read N50 29.1 kb。
- **對齊與 phasing**：minimap2 對 **GRCm38（mm10）**；margin＋WhatsHap 以 normal 做 phasing 與 haplotag。
- **建樹**：DeepVariant 各 subline 叫 somatic SNV，再用 **ScisTree** 建 cell lineage tree（FP／FN 做 grid search）。之後用 **TreeHarmonizer** 把 SNV、SV（Severus）、CNA 放到樹枝上，並標出與樹衝突的 variant。
- **benchmark 用法**：混合 subline reads 做 5 個 pseudo-bulk（全部 23 個；4 個主要 clade 各一）。用它比較 Clair3、ClairS、DeepVariant、DeepSomatic 的 precision／recall。**只測 variant caller，沒有測 tree 推論。**
- **資料**：ONT reads 在 SRA PRJNA1307171；variant calls 與 source data 在 Zenodo [10.5281/zenodo.20072601](https://doi.org/10.5281/zenodo.20072601)。

### 對本研究的意義（推論）

- 它是目前唯一找到的「公開 ONT＋已知 subline 樹」資料。按比例混合 subline reads，可以造出 clone 比例已知、樹已知的 bulk ONT。這比 `tX_nY` 的 nominal purity 更接近 ground truth。
- 可以直接測 PhyClone 與 HP-PhyClone 的 topology、clone assignment 與 multiplicity。reads 已 haplotag，但仍需改用 longphase 重新 phasing，才和本研究流程一致。
- 限制：
  - 是小鼠（mm10），不是本研究的 GRCh38 人類細胞株。
  - truth 樹本身是推論結果（ScisTree＋TreeHarmonizer），不是 lineage tracing。
  - subline 是單細胞衍生，混合後沒有「祖先 clone 本身存在於樣本中」的情況，和真實腫瘤不同。
- 作者群含 Kolmogorov，與 [M03](../papers/M03_donmez_aacr2026/README.md) 的 Donmez AACR 2026 同組。他們很可能用這份資料驗證 read-phasing 建樹，這增加了競爭風險。

## 對 `evaluation_v1.md` 的建議（推論）

1. 主指標維持不變：ADM 類 pairwise 祖先關係（SMC-Het）與 Pairtree relationship error。新文獻沒有提出取代方案。
2. 新增一條驗證路線：Liu 2026 subline 混合 pseudo-bulk。它補上「long-read＋已知樹」的缺口。
3. SCOUT 與 SISTEM 可作為 short-read 模擬對照，但要先確認 truth 是否含 per-mutation clone 與 multiplicity。
4. EMulSI-Phy 出 preprint 後再評估。它是唯一把 PhyClone 放進第三方比較的項目。

## 附：方法論文補查（2026-10-18）

方法：WebSearch（extended）4 次；Europe PMC 標題查詢 2025-01 到 2026-10，並與 survey 內 298 個 DOI 自動比對；RECOMB 2026 錄取名單重看；10 個追蹤中的 preprint 以 Crossref `is-preprint-of` 查正式版。

**結論：沒有找到符合主選判準、而且 survey 還沒收的新方法。** bulk SNV＋CN 推樹、read-level 連鎖推樹兩類都沒有新方法。

| 項目 | DOI | 判斷 |
|---|---|---|
| scRevol（He et al., Genome Med 2026-04） | [10.1186/s13073-026-01648-4](https://doi.org/10.1186/s13073-026-01648-4) | **新的邊界方法**。用 scRNA 推得的 CNV，以 reinforcement learning 做 clone 分群並重建演化軌跡。性質近 MEDALT（D 類）；摘要沒有寫輸出是否為有向 clone tree，需讀全文才能決定是否列主選 |
| Metient 正式版 | [10.1038/s41592-025-02924-8](https://doi.org/10.1038/s41592-025-02924-8)（Nat Methods 2025-12） | W5 只引 preprint，正式版已出。仍屬排除：給定 clone tree 推轉移史 |
| GIFT（Blattman et al., bioRxiv 2026-04） | [10.64898/2026.04.11.717967](https://doi.org/10.64898/2026.04.11.717967) | 實驗 assay（固定 transcriptome 上的 genotyping），不是推樹方法 |
| Zilber et al. homoplasy score（bioRxiv 2025-07） | [10.1101/2025.07.27.667007](https://doi.org/10.1101/2025.07.27.667007) | CRISPR lineage tracing 的樹可信度評分，排除。不可逆突變的想法可參考 |
| ecSingle（Hendriksen et al., Genome Biol 2026-01） | [10.1186/s13059-026-03933-2](https://doi.org/10.1186/s13059-026-03933-2) | scRNA 推 ecDNA clone，不推 topology，排除 |
| Long-read allelic configuration（medRxiv 2026-05，PMC13174754） | [10.64898/2026.05.05.26351600](https://doi.org/10.64898/2026.05.05.26351600) | ONT phasing 判 cis／trans 雙擊，不推樹。可作為 phasing 臨床價值的引用 |

**preprint 正式版狀態**：Phyllochron、ScisTreeCNA、PhyloSOLID、scLongTree、SRNJ、CTBF、SCOPE、Arborist、PICTographPlus 在 Crossref 都還沒有 `is-preprint-of` 紀錄。
