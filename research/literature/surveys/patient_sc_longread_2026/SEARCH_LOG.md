# 搜尋、收錄與排除紀錄

查核日：2026-10-15。此檔記錄本次範圍、查詢與選文判準，不宣稱完成系統性回顧或窮盡所有資料庫。

## 研究問題與分工

問題 A：有沒有真實病人 single-cell sequencing 支持的 genetic/clonal evolution reference tree？不要求 long read。

問題 B：long reads、linked reads 或 haplotype/phasing 等特徵是否真正參與 tree／ancestral relationship／局部事件順序推理？允許 simulation、cell line、single-cell-derived cultures，但分別標示。僅提供上游 CN/SV/phasing measurement 的方法不自動等於重建演化樹。

優先交集：同一病人、最好相同取樣的 scDNA reference tree，加上 long-read 特徵推理。檢查不只停在 cohort 層級；B04 的 S14 與 S8/S20 就必須拆開。

依使用者要求使用 3 個平行 subagents：病人 scDNA 文獻與 lab 術語查核、long-read／haplotype 方法與 repo source 查核、交集與近似命中獨立搜尋。協調者另行檢索 primary sources、核對源碼、整合與驗證。中途模型 usage limit 中斷後保留已下載檔案，在使用者要求繼續後接續處理，沒有把未完成筆記算作已閱讀。

## 本地證據 preflight

| 層次 | 結果 | 搜尋與使用範圍 |
|---|---|---|
| lab | available | `/big8_disk/liaoyoyo2001/Knowledge`；先查 `tumor/tumour evolution/phylogeny`、`single.cell`、`haplotype`、`phase set`、`purity`。術語採 glossary；sample metadata 採 cancer-samples/hcc1395 |
| current repo | available | `/bip8_disk/boyu114/main_work`；CLAUDE.md、plan.md、data_input.md、tumor_sample.md、PhyClone notes 與 data/math/tree source |
| historical KB | missing | `/bip8_disk/boyu114/bip8_disk_boyu_database`；記為 `not-found`，不冒稱已完成歷史資料庫深搜 |
| 已有研究文件 | available | `research/phyclone_research`、`research/hcc1395_golden_tree_research` 作導覽；歷史 pilot 數字不當本次新驗證 |

目前 repo 沒有頂層 README/arch/data/model 導覽，依實際存在的 CLAUDE.md 與研究 notes 導覽。當前程式事實回到 source 核對；沒有因為計畫文件畫出模組就認為功能已實作。

## 搜尋詞與交叉追查

查詢反覆組合以下 aliases，並以論文參考文獻、作者工具 repository 與 data availability 追查：

```text
tumor/tumour phylogeny, clonal evolution, clone tree, lineage reconstruction
single cell, single-cell DNA, scDNA-seq, scWGS, single nucleus, DLP+, Strand-seq
long read, long-read, nanopore, ONT, PacBio, linked-read, long-range haplotype
purity, tumor DNA fraction, VAF, CCF, multiplicity
haplotype, phasing, phase set, HP, PS, cis, trans, mutation pairs
copy number, CNV, CNA, LOH, copy-neutral LOH, WGD, parallel evolution
```

實際查詢例（各 worker 完整候選脈絡另見 A/B/INTERSECTION summaries）：

```text
tumor phylogeny long reads single cell haplotype reconstruction 2024 2025
"single-cell" "phylogeny" "long-read" cancer
"tumour" "phylogenetic" "Strand-seq"
"long-read" "tumor phylogeny" reconstruction
"long-read" "clonal" "haplotype" phylogeny cancer method
"linked-read" "tumor" "phylogeny" reconstruction
"haplotype" "phylogeny" "2025" cancer single cell
"long-read sequencing" "clonal tree"
"LongSom" "phylogenetic" tree
"SomaticHaplotype" phylogeny
```

primary-source 優先順序：正式出版全文／PDF與補充圖 → 作者機構保存版／正式 PMC 全文 → 原始作者 preprint（顯著標版本）→ 原作者 repository／資料封存。搜尋引擎、OpenAlex 等只供發現 DOI／合法來源，不當科學結論的最終依據。技術與資料取用的年份資訊以查核日可讀來源為準。

## 收錄判準

A 類必須確有 primary patient genomic single-cell 或 single-nucleus evidence，且產出 genetic tree／clonal ancestry；單純 expression cluster、UMAP、normal-cell receptor lineage 不算。PDX 與 primary tissue 分開；16 人 cohort 若只有 PA04 完整樹，就不能寫成有 16 棵可驗證病人樹。

B 主選採三篇涵蓋研究路徑：B01/B04 是 native ONT，B07 是 population phased haplotype/CN 的實際 topology 方法。**native long reads 不等於必然使用 haplotype-specific 特徵**：B01 鼠株 inbred 缺乏可用 germline phasing，就是重要反例。B05與B03列延伸；沒有為了數量把 validation-only、fixed-tree event placement 或會議摘要寫成 full clone-tree algorithm。

同一研究的 preprint、正式版與 correction 只計一次。

## 近似命中與排除原因

除已在 `papers/` 建 dossier 者，下表為 primary-source 初篩，**未全部下載／精讀 PDF，不計入主選配額**。

| 研究與來源 | 與問題的關係 | 未列為完整 long-read clone-tree 論文的原因 |
|---|---|---|
| [LongSom, 2025](https://doi.org/10.1101/gr.279281.124) | 卵巢癌 LR-scRNA、matched scWGS、de novo SNV/fusion/CNA；非常接近資料交集 | 正文方法使用 BnpC 做 subclone clustering，沒有因此提供完整有向 phylogeny。可借鑑 variant/normal contamination QC；RNA VAF 不同於 DNA VAF |
| [HATCHet2, 2024](https://doi.org/10.1186/s13059-024-03267-x) | clone-與haplotype-specific CN inference；適合 C0/C2 上游 | clone/CN deconvolution 本身不是 de novo clone-tree reconstruction；不能因輸出 haplotype 就充樹論文 |
| [ALPACA, 2025](https://doi.org/10.1038/s41586-025-09398-w) | clone-specific CN evolution、LOH persistence、multiple samples | 以既定 SNV clone tree 作輸入，主要解 CN evolution；不是從 long-read pairs 新推 topology |
| [Severus, 2025](https://doi.org/10.1038/s41587-025-02618-8) | long-read haplotype-specific SV 與複雜 rearrangements | SV detector/graph 不是 clonal phylogeny；適合擴充 C0 的事件層 |
| [Wakhan, 2025 preprint](https://www.medrxiv.org/content/10.64898/2025.12.11.25342098v1) | long-read chromosome-scale phased CN、SV-aware phase connection | CN reconstruction 不等於 clone-tree inference；可作 C_h／phase provenance 的候選上游 |
| [Refphase, 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10621967/) | 多樣本 haplotype-specific CN phasing、MEDICC2 介面 | long-range reference phasing 不代表使用 native long reads，仍需另外推樹 |
| [Meltos, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC8215921/) | 將 SV 放進既有 SNV evolutionary tree，另有 linked-read 支持 | 年份較早；linked reads 在該研究主要用於 assessment，不能改寫為主 likelihood |
| [TreeClone, 2019](https://arxiv.org/abs/1703.03853) | proximal SNV pairs、Bayesian tree prior；同分子共現的早期先例 | 使用 short reads，超出近期主選，但對 C4 novelty 判斷有用；不可聲稱 co-read pair idea 始於本 repo |
| [SomaticHaplotype, 2024 preprint](https://doi.org/10.1101/2024.08.09.607342) | somatic/germline phasing、linked-read clone constraints | preprint、局部結構與完整樹需分開，不另當獨立病人驗證 |
| [ecSingle, 2026](https://doi.org/10.1186/s13059-026-03933-2) | patient scRNA allelic imbalance、ONT RNA/WGS、ecDNA subclonal dynamics | ecDNA 分群與縱向擴張不自動等於完整 genetic phylogeny；另須考慮 ecDNA 非樹狀遺傳 |
| [Esophageal amplicons, 2024](https://doi.org/10.1038/s41467-024-47619-4) | long-read assembly＋DLP+ 追 organoid clonal shifts | organoid passage selection、amplicon architecture 與病人原位 lineage truth 不同；不能只因同有 scDNA/longread就當完整交集 |

## PDF、閱讀與版本控管

每個主選 dossier 均須有有效 PDF、抽出全文與 Methods/Fig 定位，才算交付。`curl` 成功不代表 PDF 有效：有的站點回傳 subscription HTML 或「Preparing to download」頁，會由 `%PDF-` 與 `pdfinfo` 檢查攔下。

B07 的正式 publisher PDF 未取得；保存的是合法 bioRxiv v1 PDF，並另外保存正式 PMC HTML、核對新增實驗與 accession 更正。因此不能宣稱所有本地 PDFs 都是正式期刊版。補充資料只有實際下載與讀過才寫成已閱讀，沒有取得的 supplementary tables/figures僅作後續入口。

資料 accession 與下載權限詳見逐篇 README。本次沒有使用作者聯絡、私人帳號憑證、付費存取繞過，也未下載受控／TB級 patient raw data。這不影響閱讀公開論文與提出可 review 的實驗設計，但不能稱為已重跑各篇 benchmark。
