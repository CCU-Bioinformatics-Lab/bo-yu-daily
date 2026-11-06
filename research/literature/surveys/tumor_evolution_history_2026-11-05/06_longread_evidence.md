# Long read 腫瘤研究：突變在兩條 HP 的分布、演化事件與 phasing 能力

## 結論

- **「每個 SNV 獨立 50%」在全基因體尺度還沒被直接檢驗。** 在讀到的論文中，只有 B04 問過突變是否隨機分布。B04 只檢驗「突變富集」的區域。〔論文〕
- **局部反證明確。** B04 在 20 例 NSCLC 中，15 例有 834 個突變富集且偏向一條 HP 的區域；其中 190 個區域有 >80% 的突變在同一條 HP。這個偏向依癌別而異：典型肺腺癌傾向集中，其他 NSCLC 隨機分布。〔論文〕
- **共識：** 複雜重排和 chromothripsis 多半只落在一條 HP。B04、Severus、Wakhan、Ijaz 都看到這個方向。但這些研究的突變和 SV 都是挑選過的，而且多數來自細胞株或 organoid。〔論文〕
- **爭議：** 腫瘤中 phasing 受 CN 影響多大。POG 認為影響小；smrest、LongPhase-S、Wakhan 認為二倍體假設會出錯。〔論文〕
- **沒有證據：** 在本次來源中，沒找到用 long read 報告「全基因體 HP1／HP2 突變比例」的研究。沒找到以 long read 資料獨立驗證完整 clone tree 的研究；最接近的是 B04（局部）。〔論文〕〔推論〕
- **HP 不等於父母。** Wakhan 明寫真正的 parental state 未知。B04 把 HP 稱為 maternal/paternal，但沒有 parent-of-origin 資訊。〔論文〕

## 搜尋範圍

- **日期：** 2026-11-05。
- **成功的來源：** WebSearch（約 15 個查詢）；Europe PMC 的 5 個關鍵字查詢（伺服器恢復後才成功，見未解問題 6）；期刊與預印本全文；本 repo B01、B04 的 PDF 文字。
- **失敗的來源：** PubMed MCP 回 API error。NCBI E-utilities 的 13 個關鍵字查詢沒有回傳結果（伺服器 500）。Europe PMC 另有 3 個關鍵字查詢（甲基化、HiFi、biallelic）沒有重跑。所以**本主題沒有完成系統性資料庫搜尋**。下文所有「沒找到」的強度都受這點限制。
- **關鍵字：** long-read／nanopore／HiFi × somatic × phasing／haplotype × tumor；chromothripsis haplotype；allele-specific methylation tumor；switch error tumor；maternal paternal somatic；HG008；COLO829；Severus；SAVANA；Wakhan；LongPhase-S。
- **期間：** 2019–2026。
- **排除：** 只收 long read 腫瘤研究；E6-04 是唯一的非腫瘤論文，只當 phasing 能力的二倍體基準。
- **既有文件：** 已讀 `surveys/longread_tree_search_2026-10-19/`、`surveys/sc_longread_datasets_2026-10-26/`，本筆記不重複其工具與資料清單。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| H1：SNV 獨立以 50% 落在兩條 HP | 每個 phase block 內兩條 HP 的突變數符合 binomial | B04：非典型肺腺癌的 NSCLC，富集區隨機分布。E6-13：一名 HCC 的 SV allele 6,472 對 6,779（是 SV，不是 SNV；總數接近不代表局部獨立） | B04：190 個區域 >80% 在一條 HP | 只測過 NSCLC 的富集區；全基因體未測 | 證據不足；局部已有反例 |
| H2：局部 hypermutation 只影響一條 HP | 富集區單一 signature，且全在同一 HP | B04 S2（14/14 在 HP1，APOBEC）、S20（3.75 Mb 內全在 HP1） | B04：其他癌別沒有這個型態 | EGFR 陽性肺腺癌最明顯；其他癌別未知 | 少數案例支持 |
| H3：複雜重排是單一 HP 的一次事件 | 重排 cluster 的 phased SV 為 cis | Severus 75–85% cis；Wakhan 複雜擴增多半一條 HP；B04 S20；E6-14 | 尚未讀到反例；Severus、Wakhan 以細胞株為主，E6-14 依此條件挑樣本 | 複雜 SV，非點突變 | 方向一致；時間順序未驗證 |
| H4：同基因雙突變是 in trans（biallelic） | 兩個 TSG 變異多在不同 HP | POG 17/19 in trans | POG 2/19 in cis；B04 S21 EGFR 在同一 HP（oncogene） | TSG，有選擇壓力；不適用 passenger | TSG 內多數支持 |
| H5：腫瘤的 long read phasing 和二倍體一樣準 | LOH、aneuploidy 不降低準確度 | POG：影響「relatively small」 | smrest、LongPhase-S、Wakhan | 依 purity、LOH 比例而變 | 爭議 |
| H6：HP 標籤等於父母來源 | 不需額外資料就能知道父系 | 無 | Wakhan：標籤起初任意，A／B | 全部 | 被否定（觀測層事實） |
| H7：long read 能獨立驗證演化樹 | 同 read 順序或 phased 事件和獨立真值一致 | B04 局部（scDNA 少量 pair）；B01 用 subline 建樹 | B01 樹是推論，不是真值；HG008、COLO829 論文沒有樹 | 局部 partial order | 證據不足 |

## 論文卡片

### B04 Sakamoto 2022, Nat Commun — 10.1038/s41467-022-31133-6（既有 ID）
- **資料：** 20 例 NSCLC；bulk；ONT PromethION 加 Illumina（germline SNP 來自短讀）；單區域；2 例有 scDNA，局部真值。
- **讀取層級：** 全文（repo 的 PDF）。
- **用了建樹工具：** 有（PyClone-VI、ClonEvol；long read 只篩候選）。
- **觀點：** 作者認為兩條 haplotype 的條件不同，這造成不同的突變事件；S20 可能是一次染色體層級的破碎事件，不是逐步累積。
- **演化假設：** 檢驗「突變是否在兩條 haplotype 真的隨機分布」。
- **真實結論：**
  - 可 phase 比例：43% 的 point mutation 指派到 HP1 或 HP2（每例平均 38%）。4 例低於 15%。VAF ≥ 0.2 時升到 71%（平均 50%）（Results "Characterization of cancerous mutations"）。
  - 分布：15 例有 834 個富集且偏向的區域，5 例沒有；和 TMB 相關 r = 0.78；190 個區域（每例 1–75）> 80% 在一條 HP；比例依癌別而異（Results，Fig. 5a–b）。
  - 案例：S2 的 14 個可解析 SNV 全在 HP1（2.8 Mb），APOBEC cosine 0.946。S20 的 chr5 3.75 Mb block 內所有 SV 和 SNV 都在 HP1。至少 5 例有 chromothripsis 痕跡，其中 4 例是 EGFR 陽性肺腺癌（Results，Fig. 5–7）。
  - 相位：block N50 834 kb，一致率 > 99%；20 例中位 N50 normal 665,168 bp、tumor 1,002,105 bp；平均 78% 基因體落在 block；S21 tumor／normal 不一致率 0.59%。
- **限制與反證：** 區域是先挑「富集」再挑「顯著偏向」，所以 190／834 不是全基因體比例。作者把偏向歸因於類 chromothripsis，但沒有分開 CN 的影響。低 VAF 突變不易指派，已指派的集合偏向高 CCF。超過 read 長的突變關係沒有分析。
- **支持哪一層（N3）：** 觀測特徵（HP 分布）；演化路徑只有局部（類 chromothripsis 是解讀）。
- **對 diplosim 的意義〔推論〕：** 直接對應 `src/hp.rs:30` 的獨立 Bernoulli。模擬器缺少「局部區域偏向一條 HP」這類現象，也沒有座標可以放這種區域。屬真值層。B04 是目前唯一對 N2 問題提供量測的 long read 論文。

### E6-02 O'Neill 2024, Cell Genomics — 10.1016/j.xgen.2024.100674
- **資料：** 189 個病人腫瘤、41 個 matched normal，多癌別；bulk；ONT PromethION，另有短讀；單樣本為主；無真值樹。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 SV 和 LOH 對 phasing 的影響不大，可能因為 biopsy 的非腫瘤細胞保留兩條 haplotype。
- **演化假設：** 短讀常假設同一 TSG 的兩個小突變 in trans；作者用 long read 檢驗。
- **真實結論：**
  - Read N50 中位 31.3 kb；tumor 中位 26×。Phase block 和 read 長相關 rho 0.72。每例中位 85% 基因可完整 phase（Results "Long-range phasing"）。
  - 30 例有 TSG 雙 somatic 變異；33 對中 19 對（18 例）可 phase；17 對 in trans，2 對 in cis（Table 1）。
  - 84% CpG 可 phase；446 萬個 aDMR，腫瘤約為 normal 的 5 倍；79% 落在雜合 CNV 或 LOH 區。
  - 每例平均 26.5% phased 基因有 ASE；ASE 和 CNA allelic ratio 相關 r = 0.63。
  - **parent-of-origin 線索：** DUSP22 在 122/135 例有 ASE。作者推測 imprinting 重新活化參與腫瘤發生。這是推測，沒有 trio。
- **限制與反證：** 樣本入選條件包含 SV 負荷或 HRD，不是隨機樣本。雙突變對來自臨床報告回顧，只含 TSG。論文沒有報告全基因體 somatic SNV 的 HP 比例。
- **支持哪一層（N3）：** 觀測特徵；in trans 支持 biallelic 選擇（克隆結構以外的機制層）。
- **對 diplosim 的意義〔推論〕：** 差距有兩個。真值層：TSG 上的選擇使 in trans 多於隨機；diplosim 沒有基因與選擇。觀測層：phased 能力依 read 長和 SNP 密度變化；diplosim 的 HP0 與 mistag 逐 site 獨立（`src/hp.rs:79-81`）。

### E6-01 Keskus 2025, Nat Biotechnol（Severus）— 10.1038/s41587-025-02618-8
- **資料：** 癌症細胞株面板（多技術）；3 例兒童白血病或淋巴瘤；bulk；ONT 與 PacBio；真值是 COLO829 benchmark 與集成 benchmark。
- **讀取層級：** 全文（journal 版，author manuscript）。
- **用了建樹工具：** 無。
- **觀點：** 作者明講 phasing 只分兩條 germline haplotype，每條可能含多個 tumor allele 和 clone。
- **演化假設：** 用 phased breakpoint graph 把 SV 分群成複雜事件。
- **真實結論：** 相鄰 phased SV 中 75–85% 為 cis。多數細胞株 SV 的 VAF 在 0–0.5 平均分布。COLO829 benchmark 可能漏掉真實 subclonal 事件。F1 0.77–0.83。H1437 最大 cluster 是 chr9 的 chromothripsis-like 事件。
- **限制與反證：** 細胞株為主；COLO829 評估只算 VAF ≥ 10%。75–85% 是 SV，不是 SNV。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 「germline HP 內仍有多個 clone」和 N1 的分層一致。差距在 CNA 階段：diplosim 的 CN 事件沒有 segment，也沒有 SV。

### E6-03 Espejo Valle-Inclan 2022, Cell Genomics（COLO829）— 10.1016/j.xgen.2022.100139
- **資料：** COLO829 黑色素瘤細胞株與配對 lymphoblastoid；bulk；ILL、ONT、PacBio、10X、Bionano；真值是實驗驗證的 SV。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 truth set 可供校正 SV 工具，也可用於 SV phasing 開發。
- **演化假設：** 無。
- **真實結論：** 68 個驗證過的 somatic SV；50 個（74%）同時以 capture 和 PCR 驗證；頻率 < 5% 的 subclonal 事件可能漏掉。
- **限制與反證：** 真值是 SV 是否存在，不是 clone 或樹。Severus 指出它可能漏 subclonal 事件。truth set 建構含短讀。
- **支持哪一層（N3）：** 觀測特徵。不支持克隆結構或演化路徑。
- **對 diplosim 的意義〔推論〕：** 不提供 HP 分布或樹的驗證參考。

### E6-HG008 McDaniel 2025, Sci Data（HG008）— 10.1038/s41597-025-05438-2
- **資料：** PDAC 細胞株與 matched normal；17 種量測技術，含 ONT、PacBio、single cell；無真值樹。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者提醒，部分變異可能是建株期間新增，不代表原發腫瘤。
- **演化假設：** 大 deletion 之後 WGD 符合 TP53 缺失腫瘤的已知進程（作者解讀）。
- **真實結論：** 許多大 deletion 造成 LOH。一部分細胞有 WGD：NIST p18 有 17/20 spread 為 34–36 條，3/20 為 68–70 條。Germline phasing 用 PacBio 加 Hi-C。資料公開。
- **限制與反證：** 論文只描述資料，沒有報告 somatic SNV 的 HP 分布。large LOH 會讓一大片基因體只有一條 HP 可觀測〔推論〕。
- **支持哪一層（N3）：** 觀測特徵；WGD subpopulation 支持克隆結構（karyotype 層）。
- **對 diplosim 的意義〔推論〕：** 可當未來回答「HP 分布」的候選資料，見下方資料表。差距屬 CNA 後階段。

### E6-11 Ahmad 2025, medRxiv（Wakhan）— 10.64898/2025.12.11.25342098
- **資料：** tumor／normal 細胞株面板、8 株乳癌細胞株、3 例兒童腫瘤（PacBio）；bulk；ONT 與 PacBio。未同儕審查。
- **讀取層級：** 全文（預印本 HTML）。
- **用了建樹工具：** 無。
- **觀點：** 作者提出部分 phase switch 可能是腫瘤早期 homologous recombination，尚待查證。
- **演化假設：** 複雜擴增只影響一條染色體 haplotype，表示它們在一次 burst 中產生。
- **真實結論：** Haplotype 標 A／B，因為 parental state 未知；CNA segment 的父母指派一開始是任意的。到染色體尺度需要 Hi-C、PoreC 或 pedigree。延伸後 N50 增加一個數量級，switch、hamming error 相近或更低。Assembly 參考平均每基因體 2 個大尺度 switch。不建模 clone 混合。Normal 細胞株的 LOH 可能在建株後才發生。
- **限制與反證：** 真值來自 coverage 一致性，不是 curated CN 真值。細胞株為主。
- **支持哪一層（N3）：** 觀測特徵；"single burst" 是解讀，屬演化路徑的間接線索。
- **對 diplosim 的意義〔推論〕：** 明確支持 N1：HP1／HP2 是觀測標籤，父母來源是真值層另一件事。diplosim 目前只有 allele A／B。

### E6-10 Ho 2025, bioRxiv（LongPhase-S）— 10.1101/2025.11.20.689492
- **資料：** 8 組公開 ONT tumor-normal，6 株細胞株；模擬混合；bulk；真值是混合比例與已知 somatic 變異。未同儕審查。
- **讀取層級：** 全文（預印本 HTML）。
- **用了建樹工具：** 無。
- **觀點：** 作者認為二倍體假設不適合腫瘤；細胞株可能低估原發腫瘤的複雜度。
- **演化假設：** 真突變落在一條 parental haplotype，錯誤隨機跨兩條（單一位點層級，不是全基因體比例）。
- **真實結論：** 傳統 germline phasing 在 LOH 區會誤指派 somatic read。HP1-1／HP2-1 tagging F1 在 6/8 資料 ≥ 0.98。無 germline 錨定的 HP3 較差：同一資料 F1 0.746 對 0.929，recall 0.596 對 0.871。
- **限制與反證：** 作者承認 subclonal CNA、LOH、aneuploidy 造成的 allelic skew 可能類似 purity 效果。這些是 read 層級標記準確度，不是突變 HP 比例。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 觀測層的差距：tag 準確度依「有沒有 germline 錨定」而不同；diplosim 的 mistag 不區分這點（`src/params.rs:74`）。

### E6-08 Simpson 2024, bioRxiv（smrest）— 10.1101/2024.02.26.582089
- **資料：** COLO829 與 mixture；模擬；bulk；ONT、PacBio；真值是外部 call set。未同儕審查。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 phasing 把 somatic calling 變成「在單一 HP 內找混合」。
- **演化假設：** 無。
- **真實結論：** LOH 時，失去 allele 的證據只來自正常細胞，取決於 purity。WhatsHap 不是為 allele-specific CN 設計。smrest 不推論 subclonal 的 CCF 分布。評估排除 VAF < 10%。
- **限制與反證：** 主要在 COLO829 開發。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 觀測層：LOH 區的 phasing 依 purity 而變。屬 CNA 後階段。

### E6-07 Elrick 2025, Nat Methods（SAVANA）— 10.1038/s41592-025-02708-0
- **資料：** 99 對 tumor-normal（57 軟組織肉瘤、28 骨肉瘤、14 GBM），QC 後 92 個腫瘤；bulk；ONT 與 Illumina；真值是 PCR 驗證與定序 replicate。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 somatic SV 的支持 read 應 phase 到單一 haplotype。
- **演化假設：** 真 somatic SV 只在一條 parental allele；假訊號常跨兩條。
- **真實結論：** ONT 中位深度 tumor 51×、normal 34×；read N50 中位 tumor 15 kbp、normal 21 kbp。和短讀 PURPLE 比，purity r = 0.97、ploidy r = 0.9（short read 比較，不當 diplosim 目標）。
- **限制與反證：** 單一 HP 一致性被當成過濾依據，所以它不是獨立生物結論。作者沒有報告 SNV 的 HP 分布。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 真實病人 read N50 差很多（15 kbp 對 POG 31.3 kb）。read 長影響 phased 能力，但 diplosim 是計數層，沒有 read 長（`src/hp.rs:2`）。

### E6-05 Fujimoto 2021, Genome Med — 10.1186/s13073-021-00883-1
- **資料：** 11 對日本肝癌與 normal；bulk；ONT MinION，另有 ICGC 短讀。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 clustered SV 可能涉及多種修復機制。
- **演化假設：** 用斷點序列推 SV 機制。
- **真實結論：** 919 個 somatic SV。long read 找回短讀 SV 的 68.4%。VAF ≥ 0.4 的 SV 有 80% 被偵測。含 ≥ 2 個斷點的 read 只有 21 條。
- **限制與反證：** 深度低。沒有 somatic SNV phasing 結果。
- **支持哪一層（N3）：** 觀測特徵；機制推論屬間接。
- **對 diplosim 的意義〔推論〕：** 主要是偵測極限：低 VAF 事件在 long read bulk 中常漏。

### E6-14 Ijaz 2024, Cell Genomics — 10.1016/j.xgen.2023.100484
- **資料：** 5 個食道腺癌 organoid（其中 2 個來自同一病人，化療前與復發後）；PacBio CCS、Hi-C、轉錄體與表觀；haplotype-resolved 組裝。無演化樹真值。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者敘述 chromothripsis 通常只影響兩條親本染色體中的一條，並把未受影響的一條當內部對照。
- **演化假設：** Chromothripsis 驅動並常起始癌症演化（作者前提，本論文未檢驗）。
- **真實結論：** 樣本的 chromothripsis 完全 clonal 且只影響單一親本 copy。重排達 900 個仍可組裝。組裝只代表 dominant clone；subclonal 區常被壓成 dominant clone。CN 不對稱時方法最有效。
- **限制與反證：** 「單一親本 copy」部分來自選樣條件，不能當發生率。"maternal／paternal" 只是兩條 haplotype 的稱呼，沒有 trio。
- **支持哪一層（N3）：** 克隆結構（clonal 事件）；觀測特徵。
- **對 diplosim 的意義〔推論〕：** 支持真值層「事件綁定一條親本 copy」。屬 CNA 後階段。

### E6-13 Lin 2026, Adv Sci — 10.1002/advs.76856
- **資料：** 1 名 HCC 男性病人；tumor 與 normal；PacBio HiFi、超長 ONT、Hi-C；單區域；無真值樹。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者明寫這是單一病人的 proof-of-concept，只能產生假說。
- **演化假設：** 無。
- **真實結論：** Tumor SV allele 分配到 haplotype 1、2 為 6,472 和 6,779。
- **限制與反證：** n = 1。組裝比對的 SV 可能含組裝差異〔推論〕。沒有報告 somatic SNV 的逐 haplotype 分布（全文關鍵字查核）。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 只是全基因體總數接近的單一案例，不足以支持或否定獨立 50%。

### E6-12 Sohn 2026, Cell — 10.1016/j.cell.2026.09.033
- **資料：** 1 名捐贈者的黑色素瘤；near-T2T diploid 組裝；short 和 long read 深度定序。
- **讀取層級：** **只有摘要**（全文抓取失敗）。不當主要證據。
- **用了建樹工具：** 摘要未提。
- **觀點：** 作者認為 T2T 分析揭露了過去看不到的 somatic 變異。
- **演化假設：** 無明列。
- **真實結論：** 16% somatic 變異落在 GRCh38 沒有的序列；satellite repeat 是 UV 相關突變熱點；haplotype-resolved chromatin map 顯示廣泛 somatic epimutation。
- **限制與反證：** n = 1。摘要沒有逐 haplotype 的突變數。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 全文可能有逐 haplotype 資料，值得優先補讀。對應現況「SNV 沒有座標、沒有區域差異」。

### B01 Liu 2026, Nat Commun — 10.1038/s41467-026-75172-9（既有 ID）
- **資料：** 23 個單細胞衍生小鼠黑色素瘤 sublines；每 subline bulk ONT；真值：無（ScisTree 推論樹）。
- **讀取層級：** 全文（repo 的 PDF，另讀 `summary.md`）。
- **用了建樹工具：** 有（ScisTree）。
- **觀點：** 作者把重複的 CNA 解讀為平行演化。
- **演化假設：** 用 SNV 建樹時假設 infinite sites，並排除 deletion 區。
- **真實結論：** 10,862 個 SNV 建樹，得到 4 個主要 clade。小鼠株高度近交，germline phasing 無用；Wakhan 以 unphased 模式執行。
- **限制與反證：** 小鼠、無 HP。不能回答兩條 HP 的分布。
- **支持哪一層（N3）：** 克隆結構（推論樹）。
- **對 diplosim 的意義〔推論〕：** 缺 HP 資訊，不適合當 HP 分布參考。

### E6-04 Kolmogorov 2023, Nat Methods — 10.1038/s41592-023-01993-x（非腫瘤基準）
- **資料：** 17 個人類基因體（14 腦組織、3 細胞株）；ONT；真值是 HPRC assembly。**不是腫瘤。**
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為考慮 SV 能改善 phasing。
- **演化假設：** 無。
- **真實結論：** Switch error 0.04–0.09%；只用 small variant 時 0.17–0.21%。Hamming error 2.1–2.6%。SV 邊界 100 bp 內 switch error 1–1.26%。腦組織 phase block NG50 平均 1.08 Mb。
- **限制與反證：** 二倍體基準，不代表腫瘤。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 只作觀測層的下界參考，不是預設值。

## 問題一：somatic SNV 的 phasing 量到什麼

| 指標 | B04（NSCLC） | E6-02 POG（多癌別） | 其他 |
|---|---|---|---|
| 可 phase 的 somatic SNV 比例 | 43%（每例平均 38%）；VAF ≥ 0.2 時 71%；4 例 < 15% | 只報 TSG 雙變異對：19/33 | 在本次來源中，沒找到全基因體比例的其他報告 |
| HP1／HP2 比例 | 未報全基因體；190 區 > 80% 在一條 | 未報 | Block 標籤任意，全基因體比例需要染色體尺度 phasing〔推論〕 |
| in cis／in trans | S21 EGFR 在同一 HP | 17 in trans、2 in cis（TSG） | Severus：SV 75–85% cis |
| phase block | N50 834 kb；中位 1.0 Mb（tumor） | 和 read 長相關 rho 0.72 | 二倍體基準 NG50 1.08 Mb（E6-04） |
| 基因或區域覆蓋 | 78% 基因體 | 中位 85% 基因 | — |

## 問題二：short read 看不到的事件

| 事件 | 量測 | 論文 |
|---|---|---|
| 單一 HP 的局部 hypermutation | S2 14/14 在 HP1 | B04 |
| chromothripsis 的 allele | S20 全在 HP1；至少 5 例有痕跡 | B04 |
| 複雜 SV 的相位 | 75–85% cis | Severus |
| 單一 HP 的複雜擴增 | 多半一條 | Wakhan |
| Chromothripsis 染色體的 haplotype 組裝 | 5 個 organoid，重排達 900 個 | E6-14 |
| GRCh38 缺少的區域內的 somatic 變異 | 16%（只讀摘要） | E6-12 |
| allele-specific 甲基化 | 446 萬 aDMR，79% 在 CNV／LOH 區 | POG |
| TSG double hit 的相位 | 17 in trans、2 in cis | POG |
| 同 read 突變排序 | 12 條 read 覆蓋 EGFR 兩突變；順序仍不唯一 | B04 |

## 問題三：對樹、clone、CCF 的獨立驗證

- **B04：** 局部 partial order，scDNA 只驗少量 pair（見 B04 `summary.md`）。
- **B01：** subline 建樹，但樹本身是推論。
- **COLO829、HG008：** 論文提供資料和 SV truth，沒有演化樹。
- **結論〔推論〕：** 上述論文都不能單獨驗證完整 clone tree。依 N3，SV truth set 只支持觀測層。

## 問題四：能回答「突變在兩條 HP 的分布」的公開資料（只列論文說明，不下載）

| 資料 | 癌別 | Long read | 存取 | 評估〔推論〕 |
|---|---|---|---|---|
| HG008（E6-HG008） | PDAC 細胞株 | ONT、PacBio；另有 Hi-C | 公開（GIAB FTP） | 最接近可用：有 matched normal 與 Hi-C。限制：大片 LOH、細胞株 |
| COLO829（E6-03） | 黑色素瘤細胞株 | ONT、PacBio | 公開 | SV truth 完整，SNV 由其他 truth set 提供 |
| 6 株細胞株 8 組 ONT（E6-10） | 乳癌、黑色素瘤、肺癌 | ONT | 論文稱公開 | 細胞株偏差；其中 HCC1395 目前暫停，不列入新實驗 |
| POG（E6-02） | 多癌別病人 | ONT，tumor 中位 26× | EGA（受控程度未在本次確認） | 唯一大型病人資料；只有 41 例有 long read normal |
| SAVANA 100,000 Genomes（E6-07） | 肉瘤、GBM | ONT，tumor 51× | 需申請 Genomics England | 病人資料，存取受限 |
| B04 | NSCLC | ONT | JGA 受控（見 `summary.md`） | 已有結果，但原始資料受控 |
| B01 | 小鼠 | ONT | 公開 | 排除：違反「HP」需求（無 germline 雜合） |

## 問題五：觀測層（和真值層分開，N1）

| 觀測偏差 | 證據 | 依賴 |
|---|---|---|
| 低 VAF 突變較難指派 HP | B04：VAF ≥ 0.2 時從 43% 升到 71% | purity、CCF、深度 |
| LOH 區的相位依賴正常細胞 | smrest；LongPhase-S 的 LOH 誤指派 | purity、LOH |
| SV 附近 switch error 較高 | E6-04：1–1.26%（非腫瘤） | SV 密度 |
| 大尺度 switch | Wakhan：平均每基因體 2 個 | 參考組裝 |
| Block 標籤任意；跨 block 無共同意義 | Wakhan、B04 | Block 長度 |
| Tag 準確度依 germline 錨定而變 | LongPhase-S：HP3 明顯較差 | SNP 密度 |
| 可 phase 區依 SNP 密度和重複序列而變 | POG：BRCA1、NF1、RB1 只有約一半腫瘤可完整 phase | 基因座 |

**父母來源（parent-of-origin）：** 真值層是生物事實；觀測層的 HP 是任意標籤。本主題讀到的論文都沒有用 trio 確認腫瘤突變的父母來源。POG 的 DUSP22 imprinting 只是推測。主題 08 專責此方向。

## 對 diplosim 的差距（照優先順序）

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| 部分區域的突變集中在一條 HP | 獨立 Bernoulli（`src/hp.rs:30`） | 沒有區域相關性，也沒有座標 | 中（B04 單一研究，20 例，選過的區域） | 單點突變 |
| 偏向依癌別、機制而異 | 全部 SNV 同一個 `prop_snv_on_b` | 沒有癌別或 signature 的差異 | 弱至中 | 單點突變 |
| TSG 雙突變多為 in trans | SNV 無基因註解 | 沒有選擇 | 中（POG 19 對，只含 TSG） | 單點突變 |
| Phase block 與跨 block 標籤任意 | HP0、mistag 逐 site（`src/hp.rs:79-81`）；`src/*.rs` 內未找到 PS 或 phase block | 觀測層沒有 block 結構 | 強（多篇一致） | 單點突變（觀測層） |
| 低 VAF 難 phase | HP0 比例不依 VAF（tag rate 逐 count） | 觀測偏差和 CCF 無關 | 中（B04） | 單點突變（觀測層） |
| 單一 HP 的複雜事件和 LOH | CN 逐 position 獨立（`docs/conipher_steps.md` S4–S6） | 沒有 segment、SV | 中 | CNA 後 |
| HP 的父母來源 | 只有 allele A／B | 真值層沒有父系／母系標籤 | 事實明確；對單點突變的影響未知 | 待主題 08 |

## 未解問題

1. 全基因體尺度，突變在兩條 HP 上是否偏離 binomial？在本次來源中沒找到答案。B04 只測富集區。
2. B04 的偏向有多少來自 CN？HP 的 copy 較多時，能觀測到的突變也可能較多〔推論〕。論文沒有逐區分開。
3. 其他癌別是否重現 B04 的結果？POG、SAVANA 的資料可能回答，但論文沒有報告。
4. **讀不到的線索：** Valle-Inclan 2025 Cell（`10.1016/j.cell.2024.12.005`，骨肉瘤 ongoing chromothripsis）和 Rausch 2023 Cell Genomics（`10.1016/j.xgen.2023.100281`，medulloblastoma）沒抓到全文，未收錄。E6-12 的全文也沒抓到。Atanda 2026 預印本（`10.64898/2026.10.08.757715`）和 Chen 2026 預印本（`10.64898/2026.09.14.751225`）在搜尋中出現，未讀。
5. **找不到的種子：** Paez-Moscoso、van Belzen 相關 cohort、Sakamoto 2020，以及 HG008 的 somatic benchmark 論文（Sanchez 或 Zook 署名），在本次 WebSearch 中沒有確認，也沒有讀。
6. 系統性搜尋未完成：NCBI 和 Europe PMC 的部分查詢沒有結果，資料庫穩定後應重跑。
7. **E6-12 已補讀全文（2026-11-05）：** COLO829 near-T2T（Sohn 2026, Cell）。44,795 個 sSNV 都在二倍體 assembly 的單倍型座標上，FDR 約 0.1%，但論文全文沒有報告 hap1 對 hap2 的全基因組 sSNV 比例，也沒有指認父母（全文以 maternal、paternal、parent-of-origin 檢索，0 筆）。補充表未讀。它不能直接回答比例問題：只有一個細胞株、78.05% 基因組有 sCNV、經歷多次 WGD。
8. **E6-12 的 VCF 已自行計算（2026-11-06）：** 原始 hap1:hap2 為 61.2:38.8。hap2 有 844 Mb 的 contig 完全沒有 SNV。扣掉超過 5 Mb 的無 SNV 片段後，9.34 比 9.31 個／Mb。11 對同源配對中 9 對差距不到 4.4 個百分點，chr14、chr16 偏離較大。這是本 repo 的計算，不是論文結論。見 `lab_report/2026-11-06_colo829_hap_snv_ratio/`。
9. **COLO829 事件驗證（2026-11-06）：** 實驗室 ONT 資料顯示約 765 Mb 只剩一條單倍型，多為多份；2:1 區用同 read 定相是 1,639 比 1,425；chr1p 的拷貝數在三批細胞中不同（約 0、0.3、1）。這是本 repo 的計算。見 `lab_report/2026-11-06_colo829_loss_events/`。
