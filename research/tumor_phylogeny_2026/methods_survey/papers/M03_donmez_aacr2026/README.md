---
paper_id: M03
category: "C2"
category_label: "long-read 特徵輔助建樹（無 single-cell 真值）"
subtype: "c2_local_order"
sc_truth_strength: "none"
title: "Phasing tumor clones by timing point mutations using bulk long-read sequencing (AACR 2026 Abstract 6912)"
year: 2026
doc_type: "abstract"
material: "cell_line"
platform_class: "long_read_feature"
platform_detail: ["ONT R10 regular + ultra-long (CASTLE H2009, H1437)"]
long_read_role: "local_order"
long_read_features: ["same-read SNV co-occurrence", "haplotag HP (code only)"]
single_cell_truth: "none"
single_cell_tech: []
input_is_single_cell: false
tree_type: ["mutation_tree", "local_order"]
cross_tags: ["read_cooccurrence_model", "direct_competitor", "castle_ont_same_data", "longphase"]
keywords_en: ["long-read", "oxford nanopore", "ultra-long reads", "somatic snv phasing", "read co-occurrence", "sequential co-occurring divergent", "mutation graph", "transitivity", "castle panel", "h2009", "h1437", "lung cancer cell line", "kolmogorov"]
keywords_zh: ["長讀定序", "體細胞突變定相", "同 read 共現", "突變時序", "細胞株"]
summary_zh: "ONT 同 read 共現判定突變先後與分歧；沒有真值。"
category_index: "../../../../PAPER_CATEGORIES.md"
---

# M03 Donmez & Kolmogorov（AACR 2026 Abstract 6912）

閱讀日：2026-10-17。只有會議摘要，沒有全文。標記：「摘要描述」＝摘要原文寫的；「推論」＝我的分析。

## 書目、版本與檔案

- Donmez A, Kolmogorov M. **Phasing tumor clones by timing point mutations using bulk long-read sequencing** [abstract]. In: Proceedings of the AACR Annual Meeting 2026; Part 1 (Regular Abstracts); 2026 Apr 17–22; San Diego, CA. *Cancer Res* 2026;86(7_Suppl):Abstract nr 6912. DOI [10.1158/1538-7445.AM2026-6912](https://doi.org/10.1158/1538-7445.AM2026-6912)。Crossref issued 2026-04-03。
- **作者只有兩位**：Crossref 作者欄與摘要附的 Citation Format 都只列 Ataberk Donmez、Mikhail Kolmogorov。任務描述的「Donmez A, …, Kolmogorov M」應更正為兩位作者。
- 本地檔：`abstract.txt`，摘要全文取自 Crossref API 的 JATS abstract 欄（逐字，只去掉標籤），檔頭註明來源 URL。AACR 出版頁 `https://aacrjournals.org/cancerres/article/86/7_Supplement/6912/778053/...` 沒有抓取。沒有 PDF，因此不放 `paper.pdf`。

## 搜尋：是否已有 preprint、程式或對應工具（2026-10-17）

| 管道 | 結果 |
|---|---|
| Europe PMC：`AUTH:"Donmez A"` 加 long read／tumor | 只找到 Severus（Nat Biotech 2025，Donmez 為共同作者），沒有對應本摘要的 preprint |
| Europe PMC：`AUTH:"Kolmogorov M"`，2025–2026 | 有 Wakhan preprint（medRxiv/bioRxiv `10.64898/2025.12.11.25342098`，Donmez 為共同作者）、melanoma sublines（Nat Commun 2026）、DeepSomatic、GIAB tumor-normal 等；**沒有**對應本摘要的 preprint |
| Web 搜尋（標題、作者＋co-occurring/divergent） | 只有摘要鏡像（synapsesocial）；沒有 bioRxiv／arXiv 版本 |
| GitHub `KolmogorovLab`（10 個 repo） | Severus、Wakhan、hapcorrect、hapdup、hapdiff、strainy、minda、Padfoot、TreeHarmonizer、**Lumos**；沒有任何 repo 描述 point-mutation timing 或 phasing clone。Lumos（無授權、2026-08-17 更新）是 ONT somatic pipeline：minimap2 → Clair3 → **longphase** → Severus → Wakhan → DeepSomatic → modkit |
| GitHub 使用者 `AtaberkDonmez` | 4 個 repo 都與本題無關（可能不是同一人，無法確認） |
| UMD PhD proposal（2026-06-22） | 是 Anton Goretsky 的 proposal，內容是 TreeHarmonizer 等，沒有提 read 共現 timing |

結論：截至查詢日，**沒有找到本摘要的 preprint 或公開程式**。同組相關工具：Severus（SV）、Wakhan（haplotype-specific CN）、TreeHarmonizer（把變異放到既有樹上）、Lumos（流程，內含 longphase）。

## 問題與模型（只依摘要）

摘要描述：
- 把 clone 重建視為「multi-allelic phasing problem」；先建立 somatic point mutation（PM）的 phylogeny，其節點對應「可能的 clonal haplotype」。
- 對兩個 PM，取同時覆蓋兩個位點的 reads，依 reads 上 ref/alt 組合判定三種關係之一：**sequential**（同一分支上先後發生）、**co-occurring**（一起出現）、**divergent**（不同分支）。
- 宣稱 PM pair 的 timing 有遞移性，因此可串接沒有共同 read 的 PM pair，得到更長的鏈。
- 以 graph 表示：PM 為節點，三種關係是三種 edge；以 connected component 為單位分析。

未在摘要中出現（也就是不知道）：判定三種關係的規則或統計模型（閾值、機率、錯誤率）、如何處理定序錯誤與 mapping 錯誤、矛盾關係怎麼解、是否用 germline phase、如何從 graph 得到 tree、是否有 likelihood 或 posterior。

推論：用詞是「deduce」與 graph／transitivity，較像組合式規則，而不是機率 likelihood；但摘要資訊不足，不能確定。

## CN、multiplicity、purity、haplotype 怎麼處理

逐字檢查摘要（摘要描述）：

| 項目 | 是否提到 |
|---|---|
| CN | **沒有直接提到 copy number**。唯一相關句是「phasing somatic mutations can also distinguish duplicated chromosome copies」，表示他們把區分重複的染色體拷貝當成附帶用途 |
| multiplicity | 沒有 |
| purity | 沒有（cell line，也沒提 normal contamination） |
| multi-sample | 沒有；兩株 cell line 各自分析 |
| haplotype | 有，但指的是「clonal haplotype」（somatic PM 組合），沒有提 germline het SNP 或 phase block 是否被使用；只在動機段提到 long reads 能把 germline variant 定相成 megabase 級 phase block |
| SV | 未來工作：「extend our approach to include timing of structural variations」 |

## 實驗與可支持的結論

摘要描述：
- 資料：CASTLE collection 的 **H2009、H1437**，regular 與 ultra-long（100 kb+）ONT reads。
- somatic SNP 數：H1437 87,999、H2009 162,334（摘要用「somatic SNPs」一詞）。
- connected component 跨距中位數 102 kb／55 kb（最大 9.5 Mb／6.4 Mb）。
- 每個 component 的 haplotype 數中位數 2（最大 56／80）；其中由多個 SNP 組成的 haplotype 中位數 1（最大 23／46）。
- 作者自承這些 cell line 的異質性低於真實腫瘤。

可支持的範圍（推論）：
- 只有描述統計，**沒有準確度評估**、沒有 ground truth、沒有和任何方法比較，也沒有全基因體尺度的樹。
- 「component 中位數 2 個 haplotype、多 SNP haplotype 中位數 1」顯示大多數 component 很小，可能大部分只是一對 SNV 的局部關係；結果離完整 clone tree 還很遠。
- 數字對應的是 cell line，somatic SNV 數量很大（數萬到十多萬），其中多少是真正的 subclonal 訊號不清楚。

## 程式碼與可取得性

- 沒有 preprint（見上方搜尋表）。
- **程式：[atabeerk/cancer_phasing](https://github.com/atabeerk/cancer_phasing)**（使用者於 2026-10-17 提供，已核對）。
  - 判定為作者 repo 的依據：
    - README 標題是「Phasing Tumor Clones By Timing Somatic Mutations In Bulk Long-Read Sequencing」，幾乎和摘要標題相同 [repo]。
    - 帳號 bio 是「CS PhD student @ UMD」，並 fork 了 Kolmogorov 的 Flye [repo]。
    - 帳號不在 KolmogorovLab org 名下 [repo]。
  - 狀態：建立於 2024-12-19，最後 push 是 2026-10-16。沒有 license，README 寫明「actively developed」[repo]。
  - **輸入**：somatic-only VCF，加上 haplotagged tumor BAM。HP tag 用來標註每個 SNV 的 HP1/HP2 alt reads [repo]。
  - **pair 計數**：同時覆蓋兩個 SNV 的 read，依兩點的 ref/alt 分成 ALT_ALT、ALT_REF、REF_ALT、REF_REF 四格（`evo/snv_analysis.cpp` 的 `compareSNVs`）[repo]。
  - **關係判定**（`evo/process_snv_output.cpp`）[repo]：
    - 關係類型有 7 種：`snp1_before_snp2`、`snp2_before_snp1`、`cooccurring`、`divergent`，以及 timing 和 cooccurring 的 `_loss` 版本。
    - 每種關係都規定「必須出現」和「禁止出現」的格子，例如 divergent 必須有 A/R 和 R/A，禁止 R/R 和 A/A。
    - 必須出現的格子要達到 `minReads`。分數 = 觀測比例 ÷ VAF 推出的期望比例，取最小值，再扣掉禁止格的 penalty。
  - **建圖**（`evo/graph_ops/builder.py`）[repo]：
    - cooccurring 邊用 union–find 合併成 cluster。
    - 加入 timing 或 divergent 邊之前，先檢查和既有 cluster 關係的遞移一致性；有衝突就拒收並記錄。
  - **輸出**：每 10 Mb 一張 mutation graph（JSON，可用 Cytoscape 看），以及 genome 層級的 component 摘要 [repo]。
  - **和本 repo 的差異** [推論]：
    - 它沒有 CN 或 multiplicity 模型，也沒有 purity 校正。期望比例直接由 VAF 推得。
    - 它不產出 clone tree 或 CCF，也沒有接 PhyClone。
    - 它的 pair 規則可以當 C4 的 rule-based baseline 和實作對照。
- 先前在 KolmogorovLab org 和同名帳號 `atadn` 都沒找到程式。原因是 repo 放在作者個人帳號 `atabeerk`。
- 資料來源是公開的 CASTLE panel（[CASTLE-Panel/castle](https://github.com/CASTLE-Panel/castle)：HCC1954、HCC1937、H1437、H2009、Hs578T、HCC1395 六對 tumor/normal，含 ONT R10 與 H1437／H2009／HCC1937 的「semi-UL」E821 資料）。

## 與本研究的重疊與差異

**重疊**（摘要描述＋推論）：
- 相同資料（2026-10-17 核對）：本 repo 的 H1437、H2009 ONT CRAM 是 CASTLE Release 1 的標準 ONT R10 資料。
  - 本機 CRAM 下載自 `brain-genomics-public/publications/park2024_deepsomatic`（`/big8_disk/Google_somatic_data/urls.txt`）。CASTLE README 寫明這個 bucket 是它的 Google mirror [repo]。
  - header 的來源檔是 `01_17_23_R1041_CancerProject_H1437_{1,2,3}_Guppy_6.3.9_prom_sup` 和 `..._H2009_{1,2}_...`，即 R10.4.1、Guppy 6.3.9 sup。對應 SRA 的 SRR28305180（H1437）和 SRR28305173（H2009），library 名為 `*_ONT` [repo]。
  - `/big8_disk/data/<line>/ONT/subsample/` 的 header 也帶相同來源檔 [repo]。
  - **本機沒有** Release 2 的 semi-UL E821 資料（SRR31537476、SRR31537473，library `*_ONT_UL`）。M03 同時用 regular 和 ultra-long reads，所以只有 regular 部分和本機相同 [推論]。
  - 讀取數和鹼基數沒有逐一比對。
- 相同核心訊號：同一 long read 上兩個 somatic SNV 的 ref/alt 共現，用來判定 sequential／co-occurring／divergent，等同本研究「read pair → ancestor/descendant/sibling」的想法。
- 同一生態系：Kolmogorov 組的 Lumos 流程使用 longphase 做 phasing，Wakhan 產出 haplotype-specific CN；他們若把這些接起來，就會走到本研究的方向。

**差異**（推論，受限於摘要資訊）：
- 本研究以 PhyClone 的 **bulk VAF＋CN＋purity likelihood** 為主體，read 共現是附加約束；摘要沒有 VAF／CCF、CN、purity 的模型。
- 本研究要把 SNV 經 phase set 指派到 HP1/HP2，再配合 haplotype-specific CN 約束 **multiplicity 與 CN timing**；摘要完全沒提 multiplicity 或 CN timing。
- 本研究有機率模型與 posterior（PG-SMC）；摘要看起來是 graph／規則式推導。
- 本研究可用多個 nominal purity subsample（雖然它們是同一 DNA 的稀釋）；摘要是 single-sample。
- 摘要的節點是「clonal haplotype」（偏局部 phasing），本研究的節點是 PhyClone 的 SNV cluster＋clone prevalence。

**風險**（推論）：
- 這是最直接的同期競爭者，用同樣的 cell line。完整論文很可能補上 Wakhan 的 haplotype CN 與 SV timing（摘要已說要做 SV）。
- 若他們的完整版加入 CN 與 prevalence，本研究的差異化就只剩 PhyClone 式 Bayesian 聯合模型與 multiplicity／timing 約束，需要盡早定位並以 benchmark 證明。
- 建議：每月查一次 bioRxiv（作者 Donmez、Kolmogorov）與 KolmogorovLab GitHub；必要時直接聯絡作者確認範圍。

**可借用的點**：
- 三分類（sequential／co-occurring／divergent）可以直接當本研究 read-pair 證據的離散摘要，與 PhyClone 樹上的 ancestor／same-node／sibling 關係一一對應，方便做 consistency 檢查。
- component span 與 haplotype 數的統計方式，可作為本研究在 H2009／H1437 上的描述性基準，先複製這些數字，確認我們的 pair 抽取流程與他們的量級一致。

## 核心判斷

- 摘要只確認「用 bulk ONT 上 PM pair 的 read 共現判定 sequential／co-occurring／divergent，再以遞移性串成 graph」，資料是 H2009、H1437。
- 摘要沒有提到 CN、multiplicity、purity 或 multi-sample；只附帶提到可區分重複的染色體拷貝。
- 截至 2026-10-17 沒有 preprint 或程式；同組已有 Wakhan（haplotype CN）與含 longphase 的 Lumos 流程，補上 CN 的門檻不高。
- 本研究的差異應定位在 PhyClone 式 VAF＋CN＋purity 的機率模型，加上 HP-aware 的 multiplicity／CN timing 約束，而不是 read 共現本身。
