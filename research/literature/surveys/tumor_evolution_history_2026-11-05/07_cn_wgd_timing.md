# CNA、LOH、WGD 與 SNV 的先後關係

依 N4，這些機制排在單點突變**之後**。本筆記是預備知識，不是目前的工作項目。下面的數字幾乎都來自 short read，只當生物假說的證據，不是 diplosim 的驗證目標或校正值。

## 結論

- **共識：** CN 事件以 segment 或染色體臂為單位發生，同段的 SNV 一起被複製。gain 前的 SNV 會變多份，gain 後的不會。多個大型隊列都用這個原理定時（E7-01、E7-03、E7-09）。細胞株實驗也支持它（E7-03）。
- **共識：** WGD 常見，比例依癌別差很多。WGD 多半在 TP53 突變或其他 driver 之後（E7-02、E7-01）。WGD 之後常接大量 loss（E7-02）。
- **有爭議：** WGD 是否「早」，以及 WGD 後每條染色體的 CIN 是否變高。E7-02 認為 WGD 早發生；E7-01 的時序排名把 WGD 放在中段。E7-07 在細胞株看不到每條染色體的 CIN 上升；E7-09 在腫瘤推論 late WGD 後 gain 速率上升，early WGD 後反而下降。
- **有爭議：** parsimony 假設。E7-09 推論 WGD 腫瘤有近三成後驗機率落在非 parsimony 路徑，但作者也說單一切片可能高估這點。
- **證據不足：** 突變因 deletion 流失的隊列級比例。本次只讀到小規模 single-cell 結果（E7-10）。在下列搜尋範圍內，也沒找到直接用 long read 量 gain 或 WGD 時間的研究。
- **HP 偏向只見於 driver：** 帶 oncogene 突變的 allele 在 loss 時幾乎總被保留，中性 germline allele 則沒有偏向（E7-08）。

## 搜尋範圍

- **日期：** 2026-11-05。
- **來源：** PMC、Europe PMC、PubMed（NCBI eutils 當天多次 HTTP 500，部分全文改由 Europe PMC 的 fullTextXML 取得，文字檔第一行有 PMCID）；WebSearch。
- **關鍵字：** long-read tumor phased copy number timing WGD multiplicity nanopore；molecular time critique punctuated gradual；preferential amplification mutant allele imbalance；GRITIC；Oxford Nanopore haplotype-resolved allele-specific copy number somatic SNV clonal evolution。
- **期間：** 不限年份，實際讀到 2014–2024。
- **WebSearch 的摘要不算證據。** 我只把它當線索，再回原文核對。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| Multiplicity 可定時：gain 前的 SNV 變多份 | gain 區有兩群 VAF；早 gain 幾乎沒有多份 SNV | E7-01、E7-03（細胞株）、E7-09（多樣本內部檢查）| E7-09：複雜狀態路徑模糊。觀測到的時間不是實際時間 | clonal gain；每段要有足夠 SNV | 共識（原理）；複雜狀態有爭議 |
| WGD 是單一事件，全基因組同時 | 各 gain 段時間聚在同一點 | E7-01 範例；E7-09 把它當推論約束 | 多重 WGD 無法定時（E7-09）；subclonal WGD 存在（E7-03）| WGD 腫瘤 | 共識（單次事件）；次數與 clonal 比例未定 |
| WGD 早於多數 CN 事件 | 多數 loss 在 WGD 後；driver 在 WGD 前 | E7-02、E7-09 | E7-01：排名居中；E7-04、E7-09：常見 LOH 事件在 WGD 前 | 依癌別不同 | 爭議 |
| WGD 提高 CIN | WGD 後事件速率上升 | E7-09（late WGD）、E7-04（WGD 腫瘤 MSAI 較多）、E7-07（異常累積）| E7-07：每條染色體速率不升。E7-09：early WGD 後下降 | 細胞株與腫瘤結論不同 | 爭議 |
| WGD 緩衝 LOH 區的有害變異 | WGD 前的 LOH 區有 purifying selection，WGD 後沒有 | E7-03 | E7-03 自己：essential gene 的 nonsense 不夠解釋選擇；全 exome 中性 | NSCLC 為主，部分其他癌別 | 爭議 |
| Parallel／mirrored 事件常見 | 不同 subclone 影響同區或不同 allele | E7-04；B03、B05（既有）| 多區域取樣才看得到；purity 干擾 clonality | 多區域資料；單一 bulk 多半看不到〔推論〕 | 共識（存在）；頻率依方法 |
| 同段 SNV 共享 CN 歷史 | 同段 SNV 的 multiplicity 由同一組事件決定 | E7-01、E7-09、E7-06 | 在本次讀到的論文沒有反證；E7-10 顯示小規模流失可能不伴隨大段 deletion | 大片段事件 | 共識（大片段）|
| 帶 driver 的 allele 被偏向保留 | 中性 allele 沒有偏向，driver allele 有 | E7-08、E7-03（TSG 的 LOH 選擇）| 不適用 passenger | 少數 oncogene、TSG | 共識（driver）|
| 突變會因 CN loss 流失 | subclonal 訊號部分來自流失 | E7-10、R01 | E7-10 的五例沒有大段 deletion；targeted 資料難排除 CN〔推論〕 | single-cell 為主 | 證據不足（頻率）|

## 論文卡片

### E7-01 Gerstung 2020, Nature — 10.1038/s41586-019-1907-7
- **資料：** PCAWG 2,658 例 WGS；2,116 個樣本可定時；bulk；**short read**；單樣本為主；沒有獨立真值。
- **讀取層級：** 全文。
- **用了建樹工具：** 無完整樹；用 MutationTimeR 定時。
- **觀點：** 作者解讀：同步 gain 指向 punctuated bursts；arm-level gain 來自 anaphase 單份 mis-segregation。
- **演化假設：** gain 前的突變在兩份上，gain 後的不會。
- **真實結論：**
  - gain 的 molecular time 中位 0.60，IQR 0.10–0.87（Timing patterns 段）。
  - 2,583 個樣本的 4,700 萬點突變：22% early clonal、7% late clonal、53% unspecified clonal、17% subclonal。
  - driver 點突變：29%、5%、56%、8%。
  - near-diploid 腫瘤有 57%（468／815）同步 gain；共同 gain 的 segment 只有 6% 有直接的染色體間 SV 連結。
  - arm-level gain 有 80–90% 只讓 allele-specific CN 加 1。同 allele 兩次 gain 的 segment 約 85% 第二次明顯延遲。
  - glioblastoma 90% 有 7、19 或 20 號單份 gain，落在前 10% molecular time；trisomy 7 通常不到 3／600 SNV 先於 gain。
- **限制與反證：** 53% clonal 突變無法定時，所以 22:7 不是所有 clonal 突變的比例。WGD 的實際年代依突變率情境推估，例如卵巢腺癌中位 latency 超過 10 年。diagnosis 前的絕對時間不是量測。
- **支持哪一層（N3）：** 演化路徑（單一時間點的推論），不支持克隆結構。
- **對 diplosim 的意義〔推論〕：** 真值層。diplosim 每個 position 獨立洗牌（`src/evolution.rs:369`），同段 SNV 沒有共享 gain 時間，也沒有 molecular time。

### E7-02 Bielski 2018, Nat Genet — 10.1038/s41588-018-0165-1
- **資料：** MSK-IMPACT 9,692 例 advanced cancer（targeted panel，**short read**）；TCGA 6,184 例 WES 對照；bulk；單樣本。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。CN 用 FACETS。
- **觀點：** 作者模型：WGD 早發生，但在 driver 之後。
- **演化假設：** 用最簡解釋定時；同位點獨立相同突變不考慮。TCN=3 且模糊的 clonal 突變排除。
- **真實結論：**
  - WGD 比例 28.2%；TCGA 31%。germ cell 58%，部分癌別 5% 以下。
  - 可定時病例中 97.3%（1142／1174）WGD 在功能性 TP53 突變之後。其他 oncogenic driver 81.1% 先於 WGD，非 hotspot 未知意義突變 57.8%。
  - 46% 的 WGD 在 TP53 野生型腫瘤。
  - 73,545 個 arm／染色體長度 loss 約 70% 在 WGD 之後。中位 ploidy：WGD 3.3，無 WGD 2.1。
- **限制與反證：** panel 只有幾百個基因，定時靠少數突變。Parsimony 假設被 E7-09 挑戰。隊列是 advanced cancer，不代表早期腫瘤〔推論〕。
- **支持哪一層（N3）：** 演化路徑（群體層級），觀測特徵（WGD 比例）。
- **對 diplosim 的意義〔推論〕：** 真值層。`clonal_wgd`（`src/params.rs:40`）是開關，WGD 沒有和 driver、loss 順序綁定。
- **親源：** 原文字樣是「maternal and parental alleles」，只是 allele-specific CN 的稱呼，沒有測親源。這是觀測層標籤。

### E7-03 López 2020, Nat Genet — 10.1038/s41588-020-0584-7
- **資料：** TRACERx（多區域 WES）與 TCGA LUAD、LUSC，再擴到 33 癌別；HCT-116 isogenic 細胞株 exome；**short read**；含模擬。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** WGD 可作為 Muller's ratchet 的緩衝。
- **演化假設：** WGD 被選擇，以減輕 LOH 區有害變異累積。預測：WGD 前的 LOH 區必要基因有 purifying selection，WGD 後沒有。
- **真實結論：**
  - WGD：LUAD 64.45%、LUSC 66.12%；subclonal 僅 1.63%、6.25%。
  - haploid 基因組：WGD 平均 1.32%，非 WGD 9.55%。clonal LOH 平均 25.85%，subclonal 5.96%。
  - 定時驗證（細胞株）：WGD 前突變 90.19% 正確，tetraploid 專屬突變 94.70% 正確。作者指出此前這個假設沒有實驗驗證。
  - NSCLC 大部分可偵測的 clonal 突變在 WGD 之前累積。
- **限制與反證：** 全 exome 層級沒有偏離中性。作者自己說 WGD 不能只靠緩衝必要基因的 nonsense 突變被選擇。緩衝機制來自模擬，不是量測。
- **支持哪一層（N3）：** 演化路徑；細胞株實驗支持定時方法。
- **對 diplosim 的意義〔推論〕：** 真值層。diplosim 沒有選擇，也沒有「LOH 在 WGD 前」的順序傾向。WGD 與 CNA 洗牌（`src/evolution.rs:369`）。

### E7-04 Watkins 2020, Nature — 10.1038/s41586-020-2698-6
- **資料：** 22 癌別 394 腫瘤、1,421 樣本（中位每腫瘤 3 個樣本，範圍 2–16）；多區域 bulk；WES 與 SNP array（**short read／array**）；沒有獨立真值。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（MEDICC，用來估 MRCA 的 CN）。
- **觀點：** CIN 持續提供選擇材料，事件有序且常平行。
- **演化假設：** 二倍體時 loss 造成完全 LOH，所以 clonal LOH 應早於 WGD。
- **真實結論：**
  - 99%（390／394）至少一個 subclonal SCNA。中位 26% 基因組 clonal、18% subclonal。45% 腫瘤超過 20% 基因組 subclonal。
  - Clonal WGD 49%。
  - Parallel 事件 37%（146／394）；定義是發生在不同 subclone 的事件。allele-specific expression 追蹤來自不同 haplotype 的 parallel 事件（ρ = 0.89）。
  - WGD 腫瘤的 MSAI 較多。本次未在主文看到 MSAI 的全隊列百分比。
  - 與 clonal loss peak 重疊的事件 94% 是 LOH。TP53 LOH 在 92% WGD 腫瘤為 clonal。CCNE1 擴增在 9／20 clonal WGD 腫瘤為 subclonal。
  - HLA 位點 subclonal LOH 影響 22% 隊列。parallel gain 比非 parallel subclonal gain 更 focal。
- **限制與反證：** 作者說 subclonal 比例被低估，因為只定序一小部分腫瘤；purity 可能干擾 clonality。需要多樣本 phasing，所以單一 bulk 很難重現〔推論〕。「parental alleles」來自 allelic imbalance phasing，不是真實親源。
- **支持哪一層（N3）：** 克隆結構（異質性）、演化路徑（相對 WGD 的順序）。
- **對 diplosim 的意義〔推論〕：** 真值層。diplosim 的 subclonal 事件以 position 為單位（`src/evolution.rs:421`），沒有「同段、不同 subclone、不同 HP」的結構。HP 觀測能否看到 mirrored 事件，要分開討論。

### E7-06 Mitchell 2018, Cell — 10.1016/j.cell.2018.02.020
- **資料：** TRACERx Renal，33 位病人 34 個腫瘤；WGS 與多區域 panel（**short read**）；bulk；ccRCC。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（phylogenetic tree，本次沒有確認工具名）。
- **觀點：** 3p loss 是早期事件的 driver，所以 t(3;5) 早發生。
- **演化假設：** 用 5q 上兩份與一份突變的比例和突變率推實際年齡。
- **真實結論：**
  - 3p loss 超過 90% 病人。3p loss 與 5q gain 同時發生於 36% 病人，常經 chromothripsis。
  - 已知 3p LOH 斷點的 30 個腫瘤有 13 個（43%）是 3p–5q 重排，通常一次事件同時失去 3p、獲得 5q。
  - 多數病人 t(3;5) 在兒童或青少年，約診斷前 30–50 年。不連 3p 的 5q gain 年齡範圍更廣。
  - chromothripsis 的重排定相到單一 haplotype。
- **限制與反證：** 只限 ccRCC。實際年齡依恆定突變率假設，作者有測試替代模型。
- **支持哪一層（N3）：** 演化路徑（單癌別）。
- **對 diplosim 的意義〔推論〕：** 真值層。一次事件可同時影響多個區域且落在同一 HP。diplosim 的事件沒有跨 position 或跨染色體的連結（`src/evolution.rs:342`）。

### E7-07 Dewhurst 2014, Cancer Discov — 10.1158/2159-8290.CD-13-0285
- **資料：** HCT-116 isogenic 2N／4N 長期培養；TCGA CRC 404 例 SNP6；**非定序為主（FISH、array）**。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** WGD 的 tolerance 讓 CIN 異常累積，不是每條染色體出錯變多。
- **演化假設：** Tetraploid 的異常來自耐受與加倍的總量。
- **真實結論：**
  - Tetraploid 細胞每條染色體的 structural 或 numerical CIN 頻率沒有升高（摘要）。
  - 克隆形成效率：2N 63%，4N 6%。
  - 群落內細胞間變異：passage 5 為 7% 對 28%；passage 50 為 13% 對 33%。
  - polyploid 腫瘤 wGII 較高。
- **限制與反證：** 單一 MIN 細胞株模型，不代表 CIN 腫瘤。和 E7-09 的 late WGD 後 gain 速率上升不直接衝突：E7-07 量每條染色體，E7-09 量全基因組且未校正 genomic content〔推論〕。
- **支持哪一層（N3）：** 機制（實驗），不是腫瘤演化路徑。
- **對 diplosim 的意義〔推論〕：** 真值層。diplosim 沒有 CIN 速率的概念，只有比例參數（`src/params.rs:18-20`）。

### E7-08 Bielski 2018, Cancer Cell — 10.1016/j.ccell.2018.10.003
- **資料：** 13,448 例 advanced solid cancer、53 癌別；69 個 oncogene 的 1,229 個 driver 與 17,352 個 passenger；targeted panel，中位約 650×（**short read**）；bulk。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。CN 用 FACETS。
- **觀點：** 多數 oncogene 突變伴隨約單份的劑量 gain，選擇偏向突變 allele。
- **演化假設：** 若 WGD 後的 loss 中性，四份 allele 被丟的機率應相等。germline 多型當中性對照。
- **真實結論：**
  - 55% driver heterozygous，45% 有 allelic imbalance；41% 腫瘤有 mutant allele imbalance。
  - 機制：focal amplification 12%；WT allele 的 LOH／CN-LOH 33%；hitchhiking 4%。TSG 84% 來自 WT allele 流失。
  - 36 位病人的檢定：germline 多型的兩個 allele 保留或流失頻率相等；oncogene loss 幾乎總保留 gain-of-function allele。
- **限制與反證：** 只看已知 driver，不適用全基因組 passenger。panel 不能告訴我們 HP 的全基因組分布。
- **支持哪一層（N3）：** 演化路徑（選擇），群體層級。
- **對 diplosim 的意義〔推論〕：** 真值層。`gain_events`、`loss_events` 等機率挑（`src/params.rs:30-31,97-98`），`src/*.rs` 中用 `driver` 關鍵字沒找到相關程式。passenger 中性有支持，所以 HP 偏向屬於 driver 議題；這和主題 04 交接。

### E7-09 Baker 2024, Cancer Discov（GRITIC）— 10.1158/2159-8290.CD-23-1249
- **資料：** PCAWG 與 Hartwig 共 6,091 例單樣本 bulk WGS（**short read**）；164,062 個 clonal gain 區域；用模擬評估方法，不是腫瘤真值。
- **讀取層級：** 全文。
- **用了建樹工具：** 無完整樹。用 DPClust 分 SNV 群。
- **觀點：** WGD 主要影響 loss 景觀，對 gain 影響小。把 SNV 定相到 haplotype 或特定 copy 可減少模糊。
- **演化假設：** 每個鹼基最多突變一次；WGD 同時作用於全基因組，當推論約束。
- **真實結論：**
  - WGD 腫瘤 gain 段有 29.8% 後驗在非 parsimony 路徑，5.6% 在多兩個以上事件的路徑。
  - 未加懲罰時，全 parsimony 模擬中也有 56.2% 後驗落在非 parsimony，作者把懲罰校到約 5%。所以 29.8% 依賴這個校正〔推論〕。
  - complex 狀態佔 gain 基因組 27.8%。WGD：轉移 55.3%、原發 31.2%。
  - late WGD 後 gain 速率上升；early WGD 前速率高，之後下降。
  - 98.5% WGD 腫瘤有 post-WGD gain，非 WGD 對照 78.0%。
  - Punctuated：16.9% 非 WGD 樣本、33.3% WGD 腫瘤；WGD 腫瘤的 burst 有 88.7% 在 WGD 之後。
  - 多樣本內部檢查：共有 gain 較早，78.9%（142／180）。
  - ccRCC 有 52／54 WGD 腫瘤帶 3p LOH。
- **限制與反證：** 每段至少 20 個 SNV、最多 500 條路徑。multiple WGD（估 5.8%）無法定時。clonal loss 無法定量定時，且 loss 可能讓先前的 gain 看不到。突變時間軸不是實際時間的線性映射。單切片的非 parsimony 可能在全腫瘤其實是 parsimonious。各段分開推論，不連結 segment。
- **支持哪一層（N3）：** 演化路徑（模型推論），不是直接量測。
- **對 diplosim 的意義〔推論〕：** 真值層。`extra_truncal_cnas`（`src/evolution.rs:318`）能做同位點多次 CNA，但沒有段與 WGD 的時間點。這篇也點出 long read phasing 的潛在價值，只是作者的觀點，沒有 long read 實測。

### E7-10 Kuipers 2017, Genome Res — 10.1101/gr.220707.117
- **資料：** 12 個已發表 single-cell 資料集（3 個 exome、9 個 targeted）；**short read**；真值來自模型比較，不是獨立資料。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（SCITE 延伸）。
- **觀點：** infinite sites 不再普遍成立。
- **演化假設：** Finite sites 模型比 infinite sites 模型更適合資料。
- **真實結論：** 11／12 資料集有同位點多次事件的證據。7 例是突變流失，其中 5 例位點沒有大段 deletion。模擬下 specificity 90%–95%（BF cutoff 1）。作者也把 LOH 當 back mutation 的替代解釋來檢驗。
- **限制與反證：** 少量細胞與少量位點，不是頻率估計。targeted 資料很難排除小 deletion 或 cnLOH〔推論〕。allele dropout 可能影響判斷〔推論〕。
- **支持哪一層（N3）：** 克隆結構（單細胞樹模型）。
- **對 diplosim 的意義〔推論〕：** 真值層。`prop_mutloss_positions`（`src/params.rs:34`）直接設比例，和 deletion 事件沒有段的連結。

### E7-11 O'Neill 2024, Cell Genomics — 10.1016/j.xgen.2024.100674
- **資料：** Long-Read POG，181 位病人 189 個腫瘤；43 個樣本（41 位病人）有 matched normal；**long read（ONT PromethION）**，read N50 中位 31.3 kb；中位 tumor 26×、normal 17.5×；bulk；每位病人多為單一樣本〔推論，由 189 樣本／181 病人〕；76% 樣本來自轉移位點。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** long read phasing 能解析 TSG 的 biallelic 機制。
- **演化假設：** 無演化時間模型。
- **真實結論：**
  - 基因完全定相比例中位 85%（IQR 79.1%–89.1%）。
  - 30 例在至少一個 TSG 有雙 somatic 變異；17 對在 trans，2 對在 cis。
  - 一例 PTEN 雙突變在 somatic deletion 的對面 allele。
  - ASE 基因與 LOH 區重疊。
- **限制與反證：** 不定 gain／WGD 時間。沒有隊列層級的 SNV vs CN 順序。phase block 依 read 長而異。
- **支持哪一層（N3）：** 觀測特徵（可定相性），局部支持 SNV 與 deletion 在哪條 haplotype。
- **對 diplosim 的意義〔推論〕：** 這是本筆記唯一的 long read 第一手研究。它不能當時間模型的證據，但顯示 SNV 和 deletion 的 HP 關係在 long read 可觀測。屬觀測層與真值的連結。

### 既有 ID（未重抓）
- **B03**（`research/literature/papers/B03_singlecell_mutational_processes_2022/summary.md`）：scDNA 的 haplotype-specific CN 與 parallel 事件。ONT 只用來驗證特定 SV，樹來自 total CN。
- **B05**（`.../B05_medicc2_2022/summary.md`）：haplotype CN、WGD、MSAI 影響 topology。它的 phasing 是模型估計方向，不是實測父源／母源。
- **R01**（`.../R01_mcpherson_hgsoc_2016/summary.md`）：infinite sites with loss 模型，用 CN 佐證 loss。摘要寫明 CN-naive 時，「祖先 SNV 流失」和「SNV 起源於兄弟節點」不可區分。

## 回答任務中的問題

1. **Multiplicity 定時與 clonal 比例：** 原理見 E7-01、E7-09。PCAWG 22% early clonal、7% late clonal，但 53% clonal 無法定時，所以這不是全部 clonal 的前後比例。
2. **WGD 頻率與時機：** 比例依癌別與隊列不同（E7-02、E7-03、E7-04、E7-09）。Multiple WGD 估 5.8%（E7-09）。WGD 前後的 CIN 變化有爭議（E7-07 對 E7-09）。
3. **MSAI 與 parallel：** Parallel 37%（E7-04），但多區域才看得到。MSAI 的全隊列百分比本次沒有核對到原文（見未解問題）。
4. **LOH 與 mutation loss：** 隊列頻率本次沒有核對到（E7-10 是小樣本）。共享 segment 的證據很強（E7-01、E7-06、E7-09），和 diplosim 的 position 獨立假設不同。
5. **HP 偏向：** 只見於 driver（E7-08），passenger 的 germline allele 沒有偏向。
6. **Long read：** 只有 E7-11 與 B03 的局部驗證。

## 親源（父系／母系）紀錄（交給主題 08）

本次讀到的論文都沒有測親源。E7-02、E7-04、E7-09 的 maternal／paternal／parental allele 都是 allele-specific CN 或 phasing 的稱呼。兩條 allele 的身分是模型標籤，對應到 diplosim 的 allele A／B（HP1／HP2），也是觀測層標籤。真實親源需要 trio、imprinting 甲基化或 Strand-seq 等額外資訊。E7-08 的中性對照顯示，germline 多型的兩個 allele 被丟的頻率相等，但它比的是 ref／non-ref，不是父／母。

## 對 diplosim 的差距（照優先順序）

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| CN 事件以 segment／染色體臂為單位，同段 SNV 共享歷史（E7-01、E7-06、E7-09）| 每個 position 獨立抽事件（`src/evolution.rs:421`），洗牌順序（`src/evolution.rs:369`）| 沒有 segment，也沒有基因組座標 | 強（short read 原理與細胞株）| CNA 後 |
| WGD 是單一時間點，SNV 分成前後（E7-01、E7-03、E7-09）| `wgd_assignment`（`src/evolution.rs:297`）給節點，WGD 事件和其他事件逐 position 洗牌（`docs/conipher_steps.md` S5）| 同節點不同 position 的 WGD 時間點不同 | 強 | CNA 後 |
| Gain、loss、WGD 有傾向順序（E7-02、E7-04、E7-09）| 等機率、無時序傾向（`src/params.rs:30-31`）| 沒有順序結構；是否要模擬待決 | 中，癌別差異大 | CNA 後 |
| Mutation loss 伴隨 deletion 同段發生（E7-10、R01）| `prop_mutloss_positions`（`src/params.rs:34`）直接設比例 | 流失和 segment 沒有連結；頻率證據也不足 | 弱到中 | CNA 後 |
| 不同 subclone 的不同 allele 同區事件（E7-04、B03、B05）| subclonal 事件以 position 抽（`src/evolution.rs:421`），事件可含 gain_A／gain_B | 有 position 層級的 A／B，但沒有 segment 層級的 mirrored 結構 | 中（多區域）；單 bulk 少見證據 | CNA 後 |
| 帶 driver 的 allele 被偏向保留（E7-08）| 沒有 driver 概念；gain／loss 從清單等機率挑（`src/params.rs:97-98`）| 缺 driver 層；passenger 中性有支持 | 強（僅 driver）| CNA 後 |
| Multiple WGD、subclonal WGD（E7-03、E7-09）| `clonal_wgd`、`subclonal_wgd`、`n_subclonal_wgd`（`src/params.rs:40-44`）；沒有 multiple clonal WGD | 部分有；時間機制待決（`DECISIONS.md` 2026-10-30）| 中 | CNA 後 |
| 真實親源（E7-02 等用語，未實測）| 只有 allele A／B（`src/hp.rs:30`）| 真值層沒有父／母標籤；證據見主題 08 | 本主題無直接證據 | CNA 後 |

## 未解問題

- **Jamal-Hanjani 2017（10.1056/NEJMoa1616288）的 MSAI 百分比與 mutation loss 比例：** NEJM 全文沒進 PMC，期刊頁回 403，PubMed 摘要沒有這些數字。repo 的 `simulation_pipeline_research/truth_evidence_2026-10-25/04_event_evidence_real_tumors.md` §2.2、§2.3 有相關數字，但本次沒有回原文核對，所以不引用。
- **Frankell 2023（TRACERx 421）與 McGranahan 2017（HLA LOH）：** 本次沒有讀到全文。
- **隊列級 mutation loss 比例：** 在本次讀到的 10 篇全文中，沒有直接的全基因組頻率。
- **Long read 時間研究：** 在 2026-11-05 的 WebSearch（long-read tumor phased copy number gain timing WGD multiplicity nanopore；ONT haplotype-resolved copy number somatic SNV clonal evolution）中，沒找到用 long read 定 gain／WGD 時間的第一手研究。結果裡的工具論文（Wakhan 等）與 Nature Communications 的 s41467-024-46414-5 我沒有讀，只是線索。
- **未搜尋的反證：** 我沒有專門搜尋 MutationTimeR 的 reanalysis；E7-09 是目前讀到最接近的挑戰。
- **單一 bulk 能看到多少：** E7-04 的 parallel 事件靠多區域。單一 bulk long read 的 HP 訊號能否看到 mirrored 事件，本次沒有找到直接證據。
