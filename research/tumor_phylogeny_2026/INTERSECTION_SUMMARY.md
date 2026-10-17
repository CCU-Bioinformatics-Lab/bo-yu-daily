# 真實病人 single-cell × long-read 演化樹：交集查核

查核日期：2026-10-15。此文件只整合本次交集 worker 實讀的四篇 PDF，補充全研究總索引；不是聲稱所有相關文獻已窮盡。每篇獨立論文的詳細方法、data accessions、C0–C6 建議與 ablation 見其 README。

後續另補 [B08 HPV integration 2023](papers/B08_hpv_integration_2023/README.md)：5 primary cancers＋4 cell lines，以真正 ONT／PacBio 推局部 molecular SV history；沒有 sc-seq，作者明示不能判斷 structures 在同 cell 或不同 subclones。此為 CNV timing／SV-loss／ecDNA 的方法延伸，並不填補完整 clinical scDNA truth-tree 缺口，也不取代主研究的核心配額。

## 結論與「答案」的強度

這次找到真正的 clinical／single-cell／long-molecule 交集，但**尚未找到一個能誠實稱為「同一真實病人的完整獨立 scDNA truth tree，並用 long-read haplotype／co-read features 重建且全面驗證整棵樹」的本批研究**。這是本批查核範圍內的結果，不是不存在這類論文的證明。

最接近的是 **Sakamoto 2022 肺癌**：20 位真實病人做 ONT＋short-read WGS，其中 S8／S20 另做 scDNA；實際 long-read partial order 甚至被拿來從 S14 的 linear／branched 候選中選 linear。但 S14 不是 scDNA 驗證病例；S8／S20 的單細胞只覆蓋少量可排序 pairs，沒有完整獨立的全樹 truth。此處應使用「局部 ancestry evidence／候選 topology 篩選＋同病例 scDNA 佐證」，避免把 `scDNA validation` 升級成全樹 ground truth。

| 論文 | 病人／模型與 single cell | long feature 的實際角色 | 完整獨立 scDNA truth tree？ | 分類建議 |
|---|---|---|---|---|
| [B04 Lung 2022](papers/B04_lung_longread_phasing_2022/README.md) | 真實 NSCLC；2 病例 10x scDNA | ONT 跨 SNV reads 直接提供 partial order，S14 用以挑選 bulk tree 候選 | 否；scDNA 病例與最清楚 topology selection 病例不同 | 最優先交集，需限制語氣 |
| [B02 Myeloma 2021](papers/B02_myeloma_linkedread_2021/README.md) | 真實 MM，14 病人 longitudinal；scRNA | 10x linked-read germline haplotype＋molecule co-occurrence，限制 NRAS 分支解釋 | 否；scRNA 不是 scDNA，fishplot 不是獨立 truth | long-range 交集／第二類擴充，不能稱 native long reads |
| [B01 Melanoma 2026](papers/B01_melanoma_longread_2026/README.md) | 小鼠 cell line；23 single-cell-derived cultures，bulk ONT | long-read SNV genotypes 建 ScisTree；SV／CNA／DMR 下游放置 | 否；非人類、非直接 scDNA，樹仍為 inferred reference | 第二類核心，公開方法開發資料 |
| [B03 Funnell 2022](papers/B03_singlecell_mutational_processes_2022/README.md) | 真實／PDX scDNA＋isogenic cell lines | SIGNALS haplotype CN 映到 total-CN tree；ONT 驗證部分 complex SV | 否；PDX／tissue 混合，total CN inferred tree | 第一類／橋接；不能計作 direct long-read topology paper |

長分子產生 `11`／`10`／`01` 等 mutation pattern，對祖先／分支關係的證據比只看 marginal VAF 多；但這種證據仍受 haplotype copy number、mutation loss、coverage、mapping／tag errors 及 sample mixture 限制。germline HP1／HP2 是 homolog 身分，**不是 clone 身分**；PS block 也不是 somatic clone。這是四篇對本 repo 最一致的提醒。

## 最有用的具體證據與資料內衝突

1. **B04 supplement p19–20 Fig. S9：** S14 的 C2→C3 long-read evidence 排除 branched alternative；同份 p26 Note：S8／S20 有 scDNA coverage 的 order pairs 各僅 2／13 對。故可作 relationship benchmark，不可直接報全樹 edit distance truth。
2. **B04 supplement p21 圖與 p48 Table S7：** S8 QC 後 138 cells，S20 376。p25 Fig. S10a caption 把病人對應寫反；圖與表一致，本筆記採前者。狀態標為 `conflict`，並保留原始 PDF 可回查。
3. **B01 p3、p12–14：** TreeHarmonizer 假定並固定 input topology；SNV tree 由 ScisTree 先建。且 inbred mouse 缺乏可用 germline heterozygosity，Wakhan unphased；不能說這篇證明 PS／HP-specific likelihood 的效果。
4. **B02 p11 Fig. 6：** 同 HP2 的兩個 NRAS mutations 沒有在覆蓋雙位點的 linked evidence 共現，作者據 n=4 偏好不同 subclones。陰性共現需以有效 molecule coverage 衡量，不能硬判。
5. **B03 p6／p8 Fig. 5：** tree 是 total CN breakpoints；HSCN 揭露平行 CN／LOH 使 bulk VAF／CCF 失真。ONT 的直接證據在 p6、Extended Data Fig. 9 p26–27，角色是 SV validation。

## 擴展搜尋與近似命中：不混入核心配額

以下僅為 primary-source 網頁初篩，**本文件未替這些項目下載與完整實讀 PDF**，因此不能算作已完成的十篇論文配額。總索引中如其他 worker 已另行讀完，應以其獨立 dossier 為準。

| 候選與 primary source | 命中原因 | 本輪保留／排除理由 |
|---|---|---|
| [LongSom 2025](https://doi.org/10.1101/gr.279281.124) | native long-read scRNA、卵巢癌 somatic SNV／fusion／CNA、subclone inference | subgroup／heterogeneity 不自動等於 genetic phylogeny；本輪未確認完整 tree，因此不以「long-read tree」計數 |
| [Grimes et al. 2023, NAR Cancer](https://doi.org/10.1093/narcan/zcad034) | adaptive ONT single-cell cDNA、真實病人 targeted somatic variants | 主目的 mutation-to-cell mapping／genotyping；未見已完成 full tumor phylogeny 的證據 |
| [RAGE-Seq 2019](https://pubmed.ncbi.nlm.nih.gov/31311926/) | 7,138 cells 來自乳癌病人的腫瘤／淋巴結，long-read BCR／TCR，B-cell lineage trees | 這是免疫細胞 receptor clonal evolution，不能直接代替 malignant tumor genome tree；若研究 lymphoma 需另議 |
| [scTRIP 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC7612647/) | Strand-seq depth／strand／haplotype 三通道、病人 leukemia SV subclones | Strand-seq 是 long-range strand linkage 而非 native long-read sequencing；本輪未確認完整 cell phylogeny，不能因有 haplotype 就誤列 |
| [scNOVA 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC10264249/) | Strand-seq、CLL／T-ALL、SV 與 phenotype 整合 | 功能／subclone characterization 並不保證 full genetic tree；需和真正 single-cell phylogeny study 區別 |
| [Refphase 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10621967/) | long-range haplotype-specific CN，可餵 MEDICC2 | long-range 是跨樣本 reference phasing，適用 short-read／array／exome；不是使用 ONT／PacBio 的證明 |
| [SAVANA 2025](https://www.nature.com/articles/s41592-025-02708-0) | long-read SV／SCNA、single-haplotype、purity／ploidy | 上游 measurement 方法，未見直接演化樹輸出；適合 C0／CN input pipeline，不當作 tree reconstruction |
| [POG long-read cohort 2024](https://pubmed.ncbi.nlm.nih.gov/39406235/) | 189 病人 tumors、ONT、phasing／methylation／SV | 臨床資源強，但並非 single-cell-derived truth／tree inference paper |
| [Lung progression 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10724178/) | 真實病人、多時期病理、ONT haplotype blocks、CN／mutation history | 不同病人 AIS→advanced 病理分期不能自動當同一病人 lineage；本輪未確認完整 phylogeny |
| [Meltos 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC8215921/) | SV tree integration、10x linked-read orthogonal data | 文中把 GROC-SVs linked reads 用於 assessment／validation；不能宣稱其為核心 long-read feature likelihood |
| [RCK 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7545144/) | clone／haplotype-specific karyotypes、long-range adjacencies | karyotype reconstruction 有 evolutionary constraints，不等於重建完整 clone tree；年份也較早 |
| [AACR 2026 abstract 6912](https://www.aacr.org/wp-content/uploads/2026/04/AACR2026_Proceedings_Part-1.pdf) | bulk long-read phasing tumor clones；H2009／H1437 與本 repo 細胞株相同 | 會議摘要，非完整已實讀 paper；僅兩 cell lines、沒有真實病人 scDNA truth。後續追蹤全文很值得 |

搜尋 aliases 含：`cancer phylogeny long read single cell haplotype patient`、`Strand-seq scTRIP clonal evolution phylogenetic`、`tumor phylogeny linked reads`、`PacBio tumor phylogenetic phasing`、`nanopore phylogenetic tree cancer`、`long-read somatic mutation timing`。文獻選取以能核對 Methods／Fig／data source 為準，不以搜索引擎摘要中的 `clonal evolution` 單一詞組作入選條件。

## 對 repo 的落地順序：分析推論，尚未修改模型

`status: current`；`source: /bip8_disk/boyu114/main_work/plan.md`；`locator: §4.1–4.7，C0–C6 表與 §5 ablation`。目前計畫 C0 提取 HP／PS／allele counts、C2 限制 multiplicity、C3 分開 phased likelihood、C4 加 co-read topology factor、C5 cluster integration、C6 posterior／conflicts。這是計畫，不是此研究任務已完成的模型實作。

`status: inferred`：建議先用 B04 的 **read-pair constraints** 檢驗 C4 語義；用 B03 的 **相同 total CN、相反 HSCN** 壓力測試 C2／C3；再用 B01 的 **公開 clonal genomes** 建 controlled mixtures。B02 則提供低 molecule coverage 的實際反例，用來防止「沒看到共現就硬分支」。四者分別驗證不同層，不應混成同一種 truth。

最小共同報告項：可用 pairs／全 pairs、coverage、PS compatibility、`C_h=1` eligibility、mutation loss／LOH flags、purity 來源、pair-held-out ancestor calibration、topology posterior uncertainty。沒有 clinical raw-data access 時，先用公開 processed constraints 建可核對的 specification fixtures，清楚標為 published-evidence reproduction。

## 下載驗真清單

所有下列資料均在各自 paper directory，論文檔案已以 `file`／`pdfinfo` 驗為 PDF，並產生 `pdftotext -layout` 的 `.txt`。已渲染 B01 Fig. 2、B02 Fig. 6、B03 Fig. 5、B04 Fig. S9／S10，避免只依文字摘要判斷。

| 檔案 | 官方來源 | PDF physical pages | SHA256 |
|---|---|---:|---|
| B01/paper.pdf | [Nature](https://www.nature.com/articles/s41467-026-75172-9.pdf) | 21 | `8811bc50ebff622b1b3663f9b25e9a749e818488a7510fb67a49187557ceb475` |
| B02/paper.pdf | [Nature](https://www.nature.com/articles/s41467-021-22804-x.pdf) | 18 | `861c823952ffade2130699caee9505351d2558a43c6829ead9a491f3b1b781e6` |
| B03/paper.pdf | [Nature](https://www.nature.com/articles/s41586-022-05249-0.pdf) | 30 | `eb6086d36613473f256502e2fdfc6655525620f5601e03cf72cce79bf0f1d6bb` |
| B04/paper.pdf | [Nature](https://www.nature.com/articles/s41467-022-31133-6.pdf) | 17 | `e13aa7957455432171cf39edd4fee9c09ad257d4f53328d9b48e58fddcd12e21` |
| B04/supplement.pdf | [MOESM1](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-022-31133-6/MediaObjects/41467_2022_31133_MOESM1_ESM.pdf) | 58 | `d30f94ed901c5f886dd89d50ea264866c5b221498610c43effa51dc807e053de` |
| B08/paper.pdf | [CSHL accepted manuscript](https://repository.cshl.edu/40840/1/2023-Goodwin-Intratumoral-heterogeneity-and-clonal-evolution-induced-by-HPV-integration.pdf) | 46 | `f5aeab2885a2244c4d458346b822855eb81690b53fa92e5148c85b41ed8e4a1f` |

`B01` 等在此表為可讀簡稱，實際相對路徑見上方各篇 README 連結。B03 `file` 的表面提示頁數為 23，而 `pdfinfo` 的 page tree 為 30；閱讀定位採後者。未保存的初篩候選不出現在本表，也不冒稱已讀 PDF。
