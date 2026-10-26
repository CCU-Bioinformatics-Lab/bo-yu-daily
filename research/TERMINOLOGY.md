# 研究術語使用指南

整理日期：2026-10-15。適用範圍：本 repo 的 `research/`。

> **2026-10-21 更新**：結構化資料 `research/terminology/`（`terms.tsv`、`evidence.tsv`、`corpus.tsv`）已刪除。詞條定義仍以 [CONTEXT.md](CONTEXT.md) 為準。下文的數量與欄位名稱描述 2026-10-15 掃描的結果。需要原始資料時，用 `git show 6bc87ca:research/terminology/<檔名>` 取回。

統一定義請讀 [研究共用術語](CONTEXT.md)。每個詞條都有英文名稱、繁體中文名稱、別名對照、簡短定義與使用界線。後續撰寫研究比較時，使用詞條中的名稱。引用論文原句、工具名稱、程式參數與欄位名稱時，保留原字串。

## 本次如何判定「共用」

本次掃描三個研究目錄的正式筆記及既有論文文字。研究單位共 13 個：PhyClone、PhyloWGS、HCC1395 參考樹研究，以及 2026 文獻調查的 10 篇論文。PhyloWGS review 位於 HCC1395 目錄，但作為獨立方法研究計數。

「共用詞」表示該概念在至少兩個研究單位的文字中出現。它不表示全部 13 個研究都使用該方法，也不表示原作者都量測了該特徵。筆記中對某方法的限制、否定或改進建議，也可能提到該詞。若要確認某篇論文實際使用了什麼，須回讀方法與結果。

詞條分為三種：

| 類別 | 判定方式 | 使用目的 |
|---|---|---|
| 共用詞 `shared` | 至少兩個研究單位有經限定的詞形命中 | 統一跨研究的討論語言 |
| 支援詞 `supporting` | 僅一個研究單位出現，或只見於綜整文件 | 補足對照所需的概念，例如樣本樹、名目混合比例 |
| 方法補充 `method-extension` | 特定方法的術語，或為處理多義詞而補充的概念 | 保留必要差異，例如兩種 ESS、兩種 multiplicity |

共用詞不加標記。其餘詞條在標題標示類別。詞條 ID 是固定定位碼；同一類別的後補詞條可能不連號。

## 本次交集與數量

本次掃描 **52 份文字檔**，整理 **193 個詞條**：164 個共用詞、19 個支援詞、10 個方法補充詞。這些分類互不重疊。

| 交集範圍 | 詞數 | 原 `terms.tsv` 的篩選條件 |
|---|---:|---|
| 全部 13 個研究單位的文本都出現 | 14 | `study_count=13`；見下表 |
| 三個研究目錄的文本都出現 | 53 | `family_count=3` |
| 至少兩個研究單位出現的共用詞 | 164 | `scope=shared` |

以上三種交集有重疊，不可相加。它們描述文字中的共用語言，不宣稱所有研究使用相同模型或量測。

全部 13 個研究文本的嚴格詞形交集如下。定義與界線統一以 [詞彙表](CONTEXT.md) 為準。

| 詞條 ID | 統一中文 | 英文／縮寫 |
|---|---|---|
| T002 | 克隆 | clone |
| T003 | 亞克隆 | subclone |
| T016 | 祖先與後代關係 | ancestor–descendant relationship |
| T029 | 拷貝數 | copy number / CN |
| T043 | 等位基因 | allele |
| T056 | 變異等位基因比例 | variant allele fraction / VAF |
| T057 | 癌細胞比例 | cancer cell fraction / CCF |
| T059 | 腫瘤細胞純度 | cellular tumor purity |
| T063 | 定序深度 | sequencing depth |
| T068 | 讀段 | sequencing read |
| T088 | 概似 | likelihood |
| T146 | 樣本 | sample |
| T172 | 變異 | variant |
| T173 | 突變 | mutation |

別名欄列出供讀文對照的名稱，不表示每種寫法都在本次語料出現。實際命中詞形與位置記錄在已刪除的 `evidence.tsv`（取回方式見文首）。多義名稱另由「用詞界線」限定。

## ASD-STE100 風格如何用在本文件

ASD-STE100 是英文技術文件的受控語言標準。本次採用其短句、單一主題與清楚指涉的寫作原則，撰寫繁體中文說明；這是風格應用，未宣稱中文文件通過 STE 合規檢查。[官方說明](https://www.asd-ste100.org/STE_faq.html)

本 repo 採用以下編寫規則：

1. 同一概念使用同一名稱。不要為了變換句型而改用近義詞。
2. 每個定義只說一個概念。必要的限制另列在「用詞界線」。
3. 先寫對象與範圍。再寫觀測、估計或推論的結果。
4. 比例必須寫出分子與分母。樹必須寫出節點代表的單位。
5. 區分實測值、模型估計值與設計值。不要只寫「真值」或「信心很高」。
6. 保留必要的專業名詞。第一次使用時，寫出中文、英文與縮寫。

以上是本 repo 的編寫規則，不是標準條文的逐字翻譯。正式英文 STE 文件另有字典與寫作限制。[ASD-STE100 官方網站](https://www.asd-ste100.org/)

## 統一寫法

| 原有寫法 | 後續採用的名稱 | 說明 |
|---|---|---|
| 拓樸、拓撲、topology | 樹拓樸（tree topology） | 保留 repo 既有主要寫法 |
| 叢集、群集、cluster | 群集 | 描述群集形成的動作時使用「分群」 |
| 盛行率、prevalence | 明寫 CCF 或克隆專有比例 | 不用同一個「盛行率」涵蓋兩種量 |
| variant allele frequency/fraction | 變異等位基因比例（VAF） | 本文的 fraction 指樣本內支持比例，與族群 allele frequency 分開 |
| 相位分析、分相、phasing | 定相（phasing） | 狀態與範圍仍稱相位、相位區塊 |
| 讀序、read | 讀段（read） | 指一次序列讀取的物件 |
| read length、讀長 | 讀長（read length） | 指長度；若舊筆記把「讀長」當作物件，按上下文修正 |
| LOH、雜合性缺失、雜合性丟失 | 雜合性喪失（LOH） | 不預設一定由物理刪除造成 |
| nominal purity、design tumor fraction | 名目混合比例 | 保留原標籤，另寫明設計分母 |
| truth tree、golden tree、答案樹 | 先判證據，再命名 | 推論結果通常稱參考樹或候選樹；有明確生成或追蹤依據才稱指定範圍的真值 |

這些是本 repo 的命名決策，狀態為 `inferred`。它們不是原作者或實驗室的官方譯名。原始論文、既有研究筆記與上游程式碼保留原文，可由別名欄對照。

## 不可合併的概念

| 概念 | 必須保留的差異 | 研究定位 |
|---|---|---|
| VAF、CCF、克隆專有比例、腫瘤細胞純度、腫瘤 DNA 比例 | 分母不同；包含後代的規則也不同 | [PhyClone 方法 §2、§5](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)；[綜整 §3](literature/surveys/patient_sc_longread_2026/REPO_IMPROVEMENTS.md) |
| clone、mutation cluster、node | 群集是統計分組；節點的生物意義依模型而定 | [PhyClone 方法 §1、§4](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md) |
| clone tree、cell tree、sample tree、mutation tree | 節點或葉節點代表不同單位 | [A 類比較](literature/surveys/patient_sc_longread_2026/A_SUMMARY.md)；[A05](literature/papers/A05_mpal_multiome_2024/README.md) |
| CN、CNA、CNV、SV | CN 是量或狀態；事件分類與原文用法另記 | [MEDICC2](literature/papers/B05_medicc2_2022/README.md)；[Strand-seq 研究](literature/papers/A04_aml_strandseq_2024/README.md) |
| major/minor CN、HP1/HP2 CN | 前者按數量排序；後者需要單倍型身份與方向 | [MEDICC2](literature/papers/B05_medicc2_2022/README.md)；[平行 CN 演化](literature/papers/B03_singlecell_mutational_processes_2022/README.md) |
| long reads、linked reads、long-range phasing | 直接長讀段、條碼連接短讀段、跨長距離定相，是不同技術層次 | [A04](literature/papers/A04_aml_strandseq_2024/README.md)；[Numbat](literature/papers/B07_numbat_2022/README.md) |
| same molecule、same cell、same clone | 同分子共現、同細胞共存與共同克隆身份，是不同主張 | [B04](literature/papers/B04_lung_longread_phasing_2022/README.md) |
| scDNA、scRNA、single-cell-derived culture | DNA 量測、RNA 量測與培養擴增材料，不可互換 | [A05](literature/papers/A05_mpal_multiome_2024/README.md)；[B01](literature/papers/B01_melanoma_longread_2026/README.md) |
| outlier、mutation loss | 前者是模型指派；後者是生物事件 | [PhyClone 限制 §1、§3](phyclone_research/notes/zh-TW/06_ASSUMPTIONS_LIMITATIONS.md) |
| mutation multiplicity、tree-representation multiplicity | 前者計算突變拷貝；後者計算等價樹表示 | [PhyClone 方法 §3、§4](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md) |
| particle ESS、MCMC ESS | 前者由粒子權重計算；後者依指定統計量的鏈自相關估計 | [PhyClone `Swarm.ess`、`relative_ess`](phyclone_research/PhyClone/phyclone/smc/swarm/swarm.py)；[Stan 官方文件](https://mc-stan.org/docs/2_40/reference-manual/analysis.html) |
| MAP、MLE、consensus tree | 後驗最佳狀態、概似最佳狀態與多樹摘要，採用不同目標 | [PhyClone 方法 §9](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)；[Numbat](literature/papers/B07_numbat_2022/README.md) |
| credible interval、confidence interval | 後驗機率區間與重複抽樣涵蓋率區間，解釋不同 | [A05](literature/papers/A05_mpal_multiome_2024/README.md)；[B07 全文](literature/papers/B07_numbat_2022/paper.txt) |
| cis/trans 相位、cis/trans 表現效應 | Numbat 此處指 CNV 區域內外的表現效應，與相同／不同單倍型的相位用法分開 | [Numbat 全文 L383、L392–400](literature/papers/B07_numbat_2022/paper.txt) |
| call-set validation、tree validation | 變異存在的驗證率，不等於樹邊或祖先關係的正確率 | [HCC1395 驗證 §1、§6](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md) |

特別注意 PhyClone 的介面字串 `joint-likelihood`：目前研究筆記與源碼顯示，該選樹分數包含先驗。敘述其行為時，使用「依後驗分數選樹」；原始介面字串仍保留。[方法 §9](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)；[`log_p_one`](phyclone_research/PhyClone/phyclone/tree/distributions.py)

## 用短句說清楚的例子

| 原寫法 | 統一後的寫法 |
|---|---|
| 這個 clone 的 prevalence 是 30%。 | 這個節點的 CCF 是 30%。分母是樣本中的全部癌細胞。此值包含後代克隆。 |
| HP1 就是 major clone。 | 這些讀段在此相位區塊標為 HP1。HP1 是單倍型標籤。克隆身份須另外推論。 |
| long read 證明這兩個 mutation 同時發生。 | 同一讀段同時帶有兩個突變。此觀測支持同分子共現。事件先後仍需其他觀測與假設。 |
| single cell 驗證了 golden tree。 | 單細胞 CNV 資料支持細胞群具有拷貝數差異。完整 SNV 祖先關係尚未逐邊驗證。 |
| purity 是 80%，所以 CCF 是 80%。 | 腫瘤細胞純度是 80%。這個數值未直接指定任何突變的 CCF。 |

比例可用兩個簡例確認。下列是定義與簡化模型的推算，狀態為 `inferred`，不是本次實驗量測。

第一例：節點 CCF 為 0.70。兩個直接子節點的 CCF 分別為 0.20 與 0.30。依無流失的樹繼承模型，該節點的克隆專有比例為 `0.70 − 0.20 − 0.30 = 0.20`。[PhyClone 方法 §5](phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md)

第二例：樣本的腫瘤細胞純度為 0.80。某突變的 CCF 為 0.50。假設正常與所有癌細胞在該位點均有兩個拷貝，攜帶細胞均有一個 ALT 拷貝，且忽略觀測偏差，預期 VAF 為 `0.80 × 0.50 / 2 = 0.20`。因此三個比例分別是 80%、50% 與 20%。[簡化觀測式與條件](literature/surveys/patient_sc_longread_2026/REPO_IMPROVEMENTS.md)

## 來源與查核方式

| 檔案 | 狀態 | 內容 |
|---|---|---|
| [CONTEXT.md](CONTEXT.md) | 現行 | 人讀詞彙表；定義與用詞界線 |
| `terminology/terms.tsv` | 2026-10-21 刪除 | 詞條的結構化資料；含別名、比對模式、分類與出現研究 |
| `terminology/evidence.tsv` | 2026-10-21 刪除 | 每個詞條在各研究單位的一個文字定位；含路徑、行號與命中片段 |
| `terminology/corpus.tsv` | 2026-10-21 刪除 | 掃描的來源清單、行數與 SHA-256 |

三個 TSV 的最後版本在 commit `6bc87ca`，用 `git show 6bc87ca:research/terminology/<檔名>` 取回。

`terms.tsv` 的 `study_count` 只計不同研究單位。英文與繁中版本不重複計數。跨研究綜整文件使用 `SYN`，不計入 `study_count`。`family_count` 則按三個原始研究目錄計算。這兩個欄位是不同層級。

`evidence.tsv` 的 `role=lexical-occurrence` 表示限定詞形的文字出現。它是導覽定位，不是「此處正式定義術語」的宣告。已排除明顯多義命中，例如一般動詞 map、random forest、complete-linkage clustering，以及 precision 參數。詞彙表的簡短定義是核對來源後的整合說明；不把每個命中片段當作完整定義的證據。

研究代碼如下：

| 代碼 | 研究與入口 |
|---|---|
| PC | [PhyClone](phyclone_research/notes/zh-TW/00_SOURCE_MAP.md) |
| PW | [PhyloWGS model review](hcc1395_golden_tree_research/phylowgs_model_review.md) |
| HCC | [HCC1395 參考演化樹](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md) |
| A01–A05 | [病人單細胞研究索引](literature/surveys/patient_sc_longread_2026/A_SUMMARY.md) |
| B01、B03–B05、B07 | [長讀段／長距離／單倍型研究索引](literature/surveys/patient_sc_longread_2026/B_SUMMARY.md) |
| SYN | [2026 文獻綜整](literature/surveys/patient_sc_longread_2026/README.md)與改進建議；不當成額外論文 |

原始 PDF、XLSX、HTML 視覺化、程式碼與中間 agent 產物，不作本次詞形統計的語料。前兩類研究以已整理的正式筆記為入口。2026 文獻調查另外掃描既有 `paper.txt` 與 `supplement.txt`。關鍵比例、ESS 與選樹分數另對照上游程式碼。這次沒有重新分析原始定序資料，也沒有全面改寫各篇研究筆記。

三層來源查核結果如下：

| status | source | locator／用途 |
|---|---|---|
| `current` | 本 repo 的研究筆記與論文文字 | 原 `corpus.tsv` 與 `evidence.tsv`（已刪除，見 commit `6bc87ca`）；含當時簽出中未追蹤的文獻調查，不能據此宣稱已實驗驗證 |
| `lab-canonical` | `/big8_disk/liaoyoyo2001/Knowledge/08_references/glossary.md` | L67–85：LOH、定相、HP、細胞純度、DNA 比例與名目比例；L90–91：體細胞變異 |
| `lab-canonical` | `/big8_disk/liaoyoyo2001/Knowledge/README.md` | L109–111：真值集適用範圍、定相標籤與 LOH 判讀界線 |
| `lab-canonical` | `/big8_disk/liaoyoyo2001/Knowledge/00_background/benchmark-methodology.md` | L30–42：precision、recall、F1 與固定評估範圍 |
| `inferred` | 本詞彙表與本指南 | 中文統一名稱、整合定義、分類與示範推算，屬本次編輯決策 |
| `not-found` | `/bip8_disk/boyu114/bip8_disk_boyu_database` | 2026-10-15 查核時目錄不存在；沒有採用未讀取的歷史內容 |

lab KB 未提供 CCF、克隆專有比例與 mutation multiplicity 的完整定義。這些條目依本 repo 的方法筆記與源碼核對。KB 中未明確規定 CNA/CNV 的嚴格分界；本詞彙表保留文獻用法，另提出寫作慣例。

MCMC ESS 與順式／反式相位屬區分多義詞所需的補充，不宣稱在本次研究語料已有獨立使用實例。順式／反式的分義另核對[原始研究](https://pubmed.ncbi.nlm.nih.gov/11380938/)。資料洩漏與 ARI 等詞若只見於綜整設計，歸為支援詞。工具專名如 PhyClone、PhyloWGS、PyClone、MEDICC2、Numbat、SCITE、ScisTree、SPRINTER、SIGNALS、Strand-seq、ONT、PacBio，保留官方拼法；它們不當作一般概念的同義詞。

BAM、CRAM、VCF 與 BED 的格式界線另核對 [HTS 官方規格索引](https://samtools.github.io/hts-specs/)。BED 的座標說明核對 [UCSC 格式文件](https://genome.ucsc.edu/FAQ/FAQformat#format1)。這些外部來源用於補充定義，不計為本地研究的新增命中。

定義、別名或來源更新時，直接更新 [CONTEXT.md](CONTEXT.md)。`terminology/` 已刪除，不再維護 TSV。要重做詞形統計時，先從 commit `6bc87ca` 取回三個 TSV，再重新掃描。
