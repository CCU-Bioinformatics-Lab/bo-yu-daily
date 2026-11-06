# 突變在兩條 haplotype 上的分布：獨立 50% 成立嗎？

## 結論

「獨立 50%」要拆成兩個主張。

- **主張 1（比例約 50%）：** 體染色體、全基因組、親代之間，有一篇直接測量：E4-26 量到不對稱上限約 4–5%（cohort 合併 5.7%）。它是未經同儕審查的 preprint，只有 21 位病人，用 short read，只有部分 SNV 可用。所以 50% 是合理的零假設，有初步支持，**還不能說已被證實**。
- **主張 2（每個 SNV 互相獨立）：** 局部被直接反駁。kataegis 的突變在同一條親代染色體上（E4-02）。long read 在肺腺癌找到 >80% 突變集中在一條 HP 的區域（B04）。但全部 substitution 只有 3.7% 是 clustered（E4-20），所以這是少數突變的現象。
- **明確的例外：** Xi 相對 Xa 有強偏差（E4-04：一例校正 CN 後 3.5 倍）。driver 受選擇：oncogene 雙 missense 多在 cis，TSG 多在 trans（E4-12），driver allele 被偏向保留（E4-17）；passenger 與 germline SNP 則接近隨機（E4-17）。
- **區域差異很大，但多半同時影響兩條 HP：** 區域差異超過 5 倍（E4-05），而兩條同源染色體約 88% 基因組同時複製（E4-14）。「同時影響兩條」是我的推論，沒有論文直接量過突變率。
- **證據不足：** germline 變異在 cis 改變同一條 HP 突變率，以及 allele-specific 表達（TCR）造成的 HP 間突變差異，我都沒找到直接量測。範圍見「搜尋範圍」。

## 搜尋範圍

- **日期：** 2026-11-05。
- **來源：** WebSearch；種子論文的 PMC 頁面與 bioRxiv 全文。
- **關鍵字（節錄）：** somatic mutations phased long-read haplotype imbalance；somatic mutation rate maternal paternal haplotypes phased；germline variants in cis somatic mutation rate allele-specific chromatin；lesion segregation human cancer strand asymmetry；allele-specific expression TCR somatic mutation between alleles；long-read phased clusters kataegis；critique reanalysis inactive X lesion segregation asymmetry。
- **期間：** 沒有設下限；PubMed 嘗試過的查詢限 2014 年後或 2019 年後。
- **工具限制：** PubMed 查詢當天回 API 錯誤或 0 筆；NCBI E-utilities 回 500，Europe PMC 回 503。所以**這不是系統性的 PubMed 回顧**，沒找到不等於不存在。全文改由 PMC 網頁抓取，並核對頁面上的 DOI。
- **反證搜尋：** 上述 critique／reanalysis 查詢只跑過一次。在這次結果裡，沒找到質疑 Xi hypermutation 的再分析。
- **讀取深度：** E4-26 讀完 Introduction、Results、Discussion 與部分 Methods。其他論文用關鍵字定位後讀相關段落，不是逐字讀完。補充資料都沒讀。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| H1 兩條親代基因組的全基因組突變負擔相同 | 親代比例接近 50% | E4-26 | 目前沒找到全基因組反例；E4-26 方向性 CI 偏寬（−7.25% 到 2.22%） | 體染色體；PCAWG；混血病人；short read | **初步支持，證據不足以稱共識** |
| H2 每個 SNV 獨立落在一條 HP | 相鄰 SNV 的 HP 無相關 | 沒有直接檢驗 | E4-02、B04、E4-20（clustered 占 3.7%） | clustered 以外的多數 SNV 未被檢驗 | **局部被反駁，整體未檢驗** |
| H3 Xi 突變多於 Xa | Xi 占多數；逃逸區沒有 | E4-04、E4-26 | E4-26 有 3/11 的 Xi 沒有較多；健康 HSPC、MDS 沒有（E4-04） | 女性、chrX、腫瘤期 | **共識**（程度與機制仍有變異） |
| H4 lesion segregation 讓整條 chromatid 的 strand 不對稱 | 區段性 strand bias；負荷不變 | E4-01 | 人類腫瘤只有少數可測，作者推論多次暴露會遮蔽 | 外源 mutagen；小鼠 DEN、人類 iPSC、馬兜鈴酸相關腫瘤 | **機制共識；人類腫瘤的普遍程度未定** |
| H5 Lesion segregation 造成 HP 負荷偏差 | 一條 HP 突變較多 | 沒找到 | E4-01：突變負荷大致均勻 | — | **證據不足，現有資料不支持**〔推論〕 |
| H6 兩次打擊把 hit 放在 trans | TSG 雙突變多為 trans | E4-12、E4-10、E4-18 | TP53 有 43% 是 cis（E4-12） | TSG；driver | **共識，有例外** |
| H7 Oncogene 雙突變放在 cis | 同一 allele | E4-12、E4-13 | MDA-MB-361 為 trans（E4-13）；short read 高估 cis（E4-12） | oncogene driver | **共識，有例外** |
| H8 帶 driver 的 HP 被選擇性 gain／保留 | 突變 allele 拷貝多於 WT | E4-17 | passenger 接近隨機（E4-17，界定適用範圍） | driver；advanced 腫瘤 | **共識（driver）** |
| H9 Allele-specific 複製時序造成 HP 間突變差異 | 晚複製 HP 突變多 | Xi 是極端例子（E4-04） | 88% 基因組兩條同時複製（E4-14）；沒找到自體染色體的突變率量測 | 體染色體未知 | **證據不足** |
| H10 Germline cis 變異改變同一 HP 突變率 | HP 依 germline 不同而差 | 只有 E4-15 的 cis 複製時序與 E4-26 轉述 | 在本次搜尋中沒找到直接測突變率的論文 | — | **證據不足** |

## 論文卡片

### E4-26 Lefèbvre 2026, bioRxiv preprint — 10.64898/2026.09.02.748867

- **資料：** PCAWG 2,645 位中可用 21 位（只有一位是 F1）；多癌別；bulk WGS；**short read**（paired-end 100 bp，約 55X）；單區域。真值：親代來源由 local ancestry 推得，不是 trio。
- **讀取層級：** 全文（WEB，已存本地文字）。**未經同儕審查**。
- **用了建樹工具：** 無。
- **觀點：** 作者寫 "validating a key assumption"。這是作者的解讀。我認為 21 位 preprint 不足以稱驗證〔推論〕。
- **演化假設：** 兩條親代基因組突變累積相同。作者寫這個假設 "has never been tested"。
- **真實結論：**
  - 不對稱上限：最高檢定力病人 4%；cohort 合併 5.7%（12,839 個 SNV，p = 0.329）；有 90% 檢定力偵測 ≥5%（Results，"Stable global mutation burden" 節）。
  - 方向性（10 位）：−0.03%，95% CI −7.25% 到 2.22%。
  - clonal／subclonal 與 C>TpG 都沒有顯著差異（"Stable mutation burdens" 節）。
  - 每例平均 32.77% SNV 可 phasing；20 位的可用區段平均只占 30.25% 基因組。
  - 正對照 Xi：11 位女性中 8 位 Xi 較多，4 位顯著。
  - imprinted 區域只有 2 個可 phasing 突變，**無法回答 imprinting 問題**。
- **限制與反證：**
  - 摘要的 4–5% 比合併的 5.7% 和方向性下界 −7.25% 都窄，不要只引摘要〔推論〕。
  - 文字 "42 of 1,298" 的單位與上限 4% 的關係，我沒有弄清楚；4% 是偏離 50% 的百分點還是相對差，也要看 Methods 與補充表。
  - 分析限於與雜合 SNP 同 read 的 SNV。混血病人的遺傳距離可能掩蓋細微訊號（作者自述）。CN 校正有 1–7% 殘差。X 的 11 位是挑過的（高 SNV、X 不平衡），不是隨機樣本。
  - 只測「全基因組總量」。**不測 SNV 之間是否獨立，也不測單一區段。**
- **支持哪一層（N3）：** 觀測特徵（突變的等位分布）。不支持克隆結構或演化路徑。
- **對 diplosim 的意義〔推論〕：** 對應 `src/hp.rs:30`。它支持全基因組比例，只限體染色體、非選擇性突變。屬真值層。

### E4-04 Jäger 2013, Cell — 10.1016/j.cell.2013.09.042

- **資料：** 402 個腫瘤全基因組，兒童與成人；bulk；short read；單區域。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為這是早期且常見的特徵，來自 DNA replication stress。機制是解讀，不是直接量測。
- **演化假設：** Xi 晚複製，所以累積更多突變。
- **真實結論：**
  - Xi 每 Mb 平均 2 倍、最高 4 倍於體染色體（摘要）。
  - MB56 為 3.6 倍；medulloblastoma 女性 20/25（80%）有 hypermutation。
  - 直接 phasing：MB101 的 58 個 SNV 中 46 在 Xi、12 在 Xa；校正 CN 後 46 vs 24，p = 0.006。lymphoma 4120193：389/444 在 Xi，校正後 3.5 倍。
  - 逃逸 X 失活區沒有 hypermutation。健康 HSPC 和 MDS 沒有。
- **限制與反證：** phasing 只靠 read pair，只有兩個高突變樣本。hypermutation 定義用「X vs 體染色體 ≥2 倍」，門檻是作者設的。
- **支持哪一層（N3）：** 觀測特徵；「健康與 MDS 沒有」間接支持時序（演化路徑）。
- **對 diplosim 的意義〔推論〕：** diplosim 沒有 chrX 的概念（`src/` 只在 `output.rs:14` 提到 chromosomes 1–22）。這是目前最強的 HP 偏差，但只限女性 chrX。

### E4-01 Aitken 2020, Nature — 10.1038/s41586-020-2435-1

- **資料：** 104 隻 C3H 小鼠 371 個 DEN 肝腫瘤 WGS；另分析人類 iPSC 暴露資料與 18,965 個人類癌症；bulk；short read；單區域。真值：單次 DEN 暴露的實驗設計。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者推論 lesion segregation "has likely shaped all genomes"，並挑戰 infinite sites 假設。推論範圍超過人類腫瘤的實測。
- **演化假設：** 未修復的 lesion 分離到子細胞。每條染色體的 strand 保留是「兩個獨立 1:1 Bernoulli」。預測 50% 體染色體與 100% 單倍 X 不對稱（資料支持）。
- **真實結論：**
  - 不對稱區段中位數 55 Mb；偏好突變有 23 倍（中位數）超額；3.5% 腫瘤是離群值。
  - **突變負荷大致均勻**。不對稱是 strand 層級，不是負荷層級。
  - Braf driver：94%（144/153）落在預期 strand。
  - 人類 iPSC：陽光、BPDE、temozolomide 都測到。
  - 人類腫瘤：可檢出者多為腎、肝、膽，符合馬兜鈴酸暴露。皮膚癌預期測不到（作者推論）。
- **限制與反證：** 主要是小鼠、單次暴露。人類腫瘤檢出多數是高突變、單一 mutagen 者。沒讀到人類腫瘤的檢出比例。
- **支持哪一層（N3）：** 觀測特徵與演化路徑（可用來追蹤事件）。
- **對 diplosim 的意義〔推論〕：** 「strand」和「HP」是兩個不同的軸。它不支持 HP 負荷偏差。差距在於 multi-allelic 與同 chromatid 的 strand 相關；diplosim 沒有 spectrum 與 strand。屬真值層。

### B04 Sakamoto 2022, Nat Commun — 10.1038/s41467-022-31133-6（已收錄，詳見 `research/literature/papers/B04_lung_longread_phasing_2022/summary.md`）

- **資料：** 20 位日本 NSCLC；bulk；**long read（ONT）加 short read**；單區域。phased block N50 834 kb，一致率 >99%。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 有（PyClone-VI、ClonEvol，見 B04 summary）。
- **觀點：** 作者解讀：不同染色體背景造成 haplotype 特異的後續變異。
- **演化假設：** 作者直接問突變是否真的隨機分布在兩條 haplotype。
- **真實結論：**
  - 100 kb 視窗；15 例共 834 個 mutation-enriched region；5 例沒有。
  - 190 個區域（每例 1–75）有 >80% 突變在一條 HP。
  - LUAD 集中於單條；其他 NSCLC 隨機分布於兩條。
  - S2：14 個 SNV 全在 HP1（2.8 Mb），符合 APOBEC SBS2（cos = 0.946）。S20：3.7 Mb block 內 SV 與 SNV 都在 HP1，伴隨類 chromothripsis。
- **限制與反證：**
  - 作者先選 enriched，再選統計上偏向一條的區域，所以 190 是**挑選後的計數，不是偏差率**〔推論〕。
  - 我沒讀到它報告全基因組 HP1：HP2 比例。
  - HP 標籤跨 block 是任意的，所以「全基因組 HP1 比 HP2」在這種資料上沒有定義〔推論〕。
  - 只有 20 例，且 enriched block 數與 TMB 相關（r = 0.78）。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 這是最接近 diplosim 情境的 long read 證據。它反對「所有 SNV 獨立」，但只限局部。

### E4-02 Nik-Zainal 2012, Cell — 10.1016/j.cell.2012.04.024

- **資料：** 21 個乳癌；bulk WGS；short read；單區域。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者提出 AID/APOBEC 家族可能相關。當時是假說。
- **演化假設：** 突變可能同時或連續產生在一條 strand 上。
- **真實結論：** 13/21 有 kataegis。PD4107a 在 14 Mb 區域高突變；microcluster 內多數突變 in cis，在同一親代染色體上。14 Mb 內有 17 個重排，其餘 157 Mb 只有 7 個。
- **限制與反證：** in cis 只靠單條 read，所以只看得到近距離。沒有給全體的 cis 比例。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 一次事件可在一條 HP 上放多個 SNV，且這些 SNV 落在同一分支。diplosim 每個 SNV 各抽一次（`src/hp.rs:30`）。

### E4-03 Mas-Ponte & Supek 2020, Nat Genet — 10.1038/s41588-020-0674-6

- **資料：** 22 種腫瘤 WGS；另有獨立 WGS 驗證；bulk；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 MMR 相關的 omikli 是 APOBEC 突變的主要來源，這依賴迴歸估計。
- **演化假設：** MMR 的 ssDNA 中介讓 A3 產生短 clustered 突變。
- **真實結論：** 699 個腫瘤 108,401 個 clustered 突變，45% 在 A3 context。A3 omikli 在早複製區富集 2.0／2.5 倍，未 clustered TCW 為 0.54／0.72 倍。IMD 峰 355 nt。估計 omikli 過程貢獻 66.4% A3 context 突變。
- **限制與反證：** 66.4% 是迴歸估計，不是直接計數。E4-20 發現只有 16.2% omikli 符合 APOBEC3 模式，定義範圍不同。沒有直接 phasing 短 cluster。IMD 峰 355 nt 落在 long read 內，但本文沒有 long read 驗證〔推論〕。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 同一 read 上可能看到 omikli pair。diplosim 沒有座標，產生不了這種訊號。

### E4-20 Bergstrom 2022, Nature — 10.1038/s41586-022-04398-6

- **資料：** 2,583 個 PCAWG WGS；bulk；short read；單區域。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為 ecDNA 上有 APOBEC3 突變聚集。
- **演化假設：** clustered 事件可依距離、VAF 與 sequence context 分類，反映不同機制。
- **真實結論：** 1,686,013 個 clustered SBS；**全部 substitution 只有 3.7% clustered**，但貢獻 8.4% 的 substitution driver。clustered 組成：DBS 45.7%、MBS 0.7%、omikli 37.2%、kataegis 7.0%。bone leiomyosarcoma 11.5%；黑色素瘤 clustered 中 74.2% 是 UV doublet。36.2% kataegis 事件在斷點 10 kb 內。
- **限制與反證：** 用 VAF 一致性代替 phasing，沒有直接證明同一 haplotype。低 VAF cluster 看不到〔推論〕。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 提供差距的尺度：不獨立的 SNV 占少數，但在 driver 中較多。short read 數字不能當 diplosim 的校正值。

### E4-12 Gorelick 2020, Nature — 10.1038/s41586-020-2315-8

- **資料：** 31,359 位病人；臨床 panel；bulk；short read；advanced／metastatic。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** cis composite 可能有 biallelic 失活以外的功能。
- **演化假設：** composite 突變受選擇；phase 依基因類別不同。
- **真實結論：** 22.7% 腫瘤有 composite，比隨機多 56%。可評估者 67% cis、19% trans、14% 不確定。TSG 71% trans（79/111）；oncogene 雙 missense 91% cis（243/268）。EGFR、TERT、PIK3CA cis 88–97%。TP53 43% cis（70/163）。
- **限制與反證：** 作者寫 short read 對 trans 敏感度較低，可能高估 cis。panel 只看癌症基因，不能外推到 passenger。advanced 腫瘤有選擇偏差。
- **支持哪一層（N3）：** 演化路徑（選擇的結果）；不支持克隆樹。
- **對 diplosim 的意義〔推論〕：** driver 的 HP 不是隨機。diplosim 沒有選擇也沒有 driver。

### E4-13 Vasan 2019, Science — 10.1126/science.aaw9032

- **資料：** 70,754 位病人（cBioPortal）；6 個新鮮腫瘤樣本用 **SMRT long read** 定 phase。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** cis 雙突變增加致癌性與藥物敏感性。
- **演化假設：** 雙 PIK3CA 突變在 cis 比單一或 trans 更有選擇優勢。
- **真實結論：** 12–15% 有多個 PIK3CA 突變，95% 為雙突變。4526 例中 576 例（13%）。6 個樣本全部 cis。細胞株 MDA-MB-361 是 trans。
- **限制與反證：** long read 樣本只有 6 個，只能取到 metastatic 新鮮檢體。
- **支持哪一層（N3）：** 演化路徑。
- **對 diplosim 的意義〔推論〕：** 同一基因的 cis 共現，是 long read 能看到的。同 read 共現目前不是研究需求（CLAUDE.md 2026-11-04），這裡只記差距。

### E4-17 Bielski 2018, Cancer Cell — 10.1016/j.ccell.2018.10.003

- **資料：** 13,448 個 advanced 腫瘤，53 癌別，69 個 oncogene；臨床 panel；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 等位不平衡是普遍的演化創新。
- **演化假設：** 中性時，突變 allele 與 WT 的額外 copy 應等頻。
- **真實結論：** driver 55% 雜合、45% 不平衡；41% 腫瘤有 driver 不平衡；LOH／CN-LOH 占 33%。**passenger 與 germline SNP 接近隨機、接近等頻**；已知 driver 強烈偏向突變 allele。
- **限制與反證：** advanced 腫瘤；基因 panel 不含大部分基因組。CN 由 allele-specific 定序推得，沒有 long read phasing。
- **支持哪一層（N3）：** 演化路徑（選擇）。
- **對 diplosim 的意義〔推論〕：** 這個階段屬「CNA 後」。它提示 CNA 事件選哪條 HP 時，passenger 接近隨機，driver 不是。一次一個機制，先記差距（N4）。

### E4-18 Park 2018, Nat Commun — 10.1038/s41467-018-04900-7（背景：E4-10 Knudson 1971，10.1073/pnas.68.4.820，**只有摘要**）

- **資料：** 10,043 個 TCGA exome，30 癌別；short read。Knudson：48 例視網膜母細胞瘤。
- **讀取層級：** Park 全文；Knudson 只有摘要（PMC 是掃描檔）。
- **用了建樹工具：** 無。
- **觀點：** rare germline 變異對癌症風險貢獻很大。
- **演化假設：** Knudson 的兩次打擊。germline hit 加上另一條 HP 的 somatic LOH。
- **真實結論：** 已知易感基因在有 allelic imbalance 的樣本中富集 rare damaging germline 變異。估計約貢獻 14% 卵巢癌。
- **限制與反證：** AI 是 LOH 的代理；exome；Knudson 的統計是推論模型，不是分子量測。14% 是估計值，定義要看原文。
- **支持哪一層（N3）：** 演化路徑。
- **對 diplosim 的意義〔推論〕：** 把第二次 hit 放在另一條 HP，是 TSG driver 的規則，不適用於 passenger。

### E4-14 Mukhopadhyay 2014, PLoS Genet — 10.1371/journal.pgen.1004319

- **資料：** 人類初代 erythroblast；兩位個體；family quartet phasing；short read。非腫瘤。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 結構變異與 imprinting 是不同步的兩個原因。
- **演化假設：** 同源染色體複製程式有多一致。
- **真實結論：** 約 88% 基因組兩條同時複製，差異 <S 期 10%（<48 分鐘）。其餘 12% 最多 2–3 小時。約 600 個 Mb 級不同步區。maternal／paternal 時序 r² = 0.95。最長區富集 imprinted 基因。作者推測 Xa／Xi 差異更大。
- **限制與反證：** 非腫瘤，只有兩人。腫瘤裡的不同步沒有在這裡量。沒有量突變。
- **支持哪一層（N3）：** 機制背景，不屬於三層中的任何一層。
- **對 diplosim 的意義〔推論〕：** 支持「區域差異同時影響兩條 HP」的前提。parent-of-origin：imprinting 相關的不同步只記在這裡，由主題 08 專責。

### E4-15 Koren 2014, Cell — 10.1016/j.cell.2014.10.025

- **資料：** 161 人 LCL，1000 Genomes；short read。非腫瘤。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 複製時序受遺傳多型影響。
- **演化假設：** germline 多型在 cis 影響 Mb 級複製時序。
- **真實結論：** 16 個 rtQTL，有 allele-specific 效應；replication variant 覆蓋超過 10% 基因組。
- **限制與反證：** 沒有量 somatic 突變，所以「germline cis → 複製時序 → HP 突變差異」這條路徑**沒有被驗證**〔推論〕。
- **支持哪一層（N3）：** 機制背景。
- **對 diplosim 的意義〔推論〕：** 這是 H10 的可能路徑，目前只是假說。

### E4-05 Lawrence 2013, Nature — 10.1038/nature12213

- **資料：** 3,083 對，27 癌別；其中 126 對 WGS，10 癌別；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 不校正異質性會造成假陽性癌症基因。
- **演化假設：** 突變率隨表達與複製時序變化。
- **真實結論：** 區域差異超過 5 倍。低表達基因突變率約高 2.9 倍。
- **限制與反證：** 區域差異不區分 HP。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** diplosim 沒有區域差異（SNV 沒有基因組座標，見 `src/hp.rs:37`）。

### E4-08 Polak 2015, Nature — 10.1038/nature14221

- **資料：** 多癌別 WGS；ENCODE 等表觀資料；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 突變圖譜可用來推測 cell of origin。
- **演化假設：** 細胞來源的染色質決定突變分布。
- **真實結論：** 區域差異最多約 5 倍；表觀標記加複製時序解釋七種癌 74–86% 變異。
- **限制與反證：** 用 pooled 資料解釋變異，不是因果；不區分 allele。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 同 E4-05。

### E4-09 Haradhvala 2016, Cell — 10.1016/j.cell.2015.12.050

- **資料：** 590 個腫瘤，14 癌別；WGS；short read。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** 不對稱可用來解析 DNA damage 機制。
- **演化假設：** 轉錄與複製方向造成 strand 不對稱。
- **真實結論：** T-class 主導 UV、抽菸、肝癌相關突變；R-class 主導 POLE、APOBEC、MSI 相關突變。
- **限制與反證：** strand 的方向由基因組位置決定，不區分 HP。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** strand asymmetry 不等於 HP asymmetry。

## 對 diplosim 的差距（照優先順序）

差距只描述現象，不代表要加入。階段依 N4 排序。

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| 體染色體全基因組比例接近 50% | `src/hp.rs:30`，`prop_snv_on_b` 預設 0.5 | 沒有已知矛盾；前提只有一篇 preprint 支持 | 中低（E4-26） | 單點突變 |
| 一次事件在同一 HP 放多個 SNV（kataegis、omikli、局部偏差） | `src/hp.rs:30` 每 position 獨立；`src/hp.rs:37` 每 SNV 有自己的 position | 沒有 cluster，也沒有座標 | 中（E4-02、B04、E4-20；多為 short read，只有 B04 是 long read） | 單點突變 |
| 區域突變率差異超過 5 倍，且可能同時影響兩條 HP | 沒有座標（`src/hp.rs:37`） | 沒有區域差異 | 高（E4-05、E4-08），但「兩條 HP 同時」是推論 | 單點突變 |
| 女性 Xi 明顯偏多 | 沒有性別與 chrX（`src/output.rs:14` 只列 1–22） | 模擬範圍不含 chrX；若要包含就是差距 | 高（E4-04、E4-26） | 單點突變 |
| Driver 的 cis／trans 結構 | 沒有 driver、選擇（`src/topology.rs:57-109` 無選擇） | 所有 SNV 地位相同 | 高（E4-12、E4-13、E4-18） | 單點突變；需先有選擇機制 |
| Driver 所在 HP 被選擇性 gain／保留 | CNA 每 position 獨立（`docs/conipher_steps.md` S4–S6） | CN 與 driver 無關；passenger 隨機部分與現況相容 | 高（E4-17） | CNA 後 |
| Lesion segregation（strand、multi-allelic） | 沒有 strand 與 spectrum | 不影響 HP 比例，只影響 strand 與重複突變 | 中（E4-01，人類腫瘤證據少） | 單點突變，低優先 |
| 真值的親代來源標籤 | 只有 allele A／B（`src/hp.rs`） | 主題 08 專責 | E4-26 附帶 | 單點突變 |

**真值與觀測（N1）〔推論〕：** E4-26 量的是父母，B04 量的是 HP1／HP2。跨 phase block 的 HP 標籤是任意的，所以在觀測層，「全基因組 HP1 比 HP2」沒有定義；有意義的觀測量是同一 block 內的分布。真值層可以知道每條染色體的來源。

## 未解問題

1. **長讀版的 E4-26：** 在 X（本次 WebSearch）範圍內，用 Y（somatic mutation、phased long-read、haplotype imbalance、mutation burden、HP1 HP2）關鍵字，沒有找到用 long read 測全基因組 HP 間比例的研究。作者也把 long read 列為未來方向。
2. **SNV 之間的 HP 相關性：** 沒找到扣掉已知 cluster 之後，直接檢驗「相鄰 SNV 的 HP 是否獨立」的研究（同一次搜尋範圍）。這是 diplosim 假設中最沒有被測試的部分。
3. **B04 的 190 個區域有多少是偶然：** 我沒讀到校準過的 null。需要補讀 Methods 與 Supplementary Fig. S13。
4. **Germline cis 影響 somatic 突變率：** 在 WebSearch 關鍵字 "germline variants in cis ... somatic mutation rate ... allele-specific" 中，只找到 germline 與 somatic 的整體關聯，沒找到同一 HP 上的量測。
5. **Allele-specific 表達與 TCR：** 在 "expressed allele vs silent allele somatic mutation" 關鍵字中沒找到兩條 allele 的直接比較。E4-04 的逃逸區是最接近的間接證據。
6. **沒讀到的種子：** Schuster-Böckler 2012（PMC 無全文）；Saito 2020（我用的 DOI 無法在 PMC 確認，改用 E4-12、E4-13）；Dietzen 2024 與 Supek 2015（已列入但工具失敗，未讀）。Stamatoyannopoulos 2009 有讀，但它量的是物種間差異與 germline SNP，沒有放進卡片。Cortés-Ciriano 2020（chromothripsis）未讀；chromothripsis 附近的證據只來自 E4-02、B04。
7. **Parent-of-origin：** 本文只記碰到的證據。E4-26 測親代方向沒有偏差；imprinted 區域無法分析；E4-14 記錄 imprinting 與複製不同步。其餘交主題 08。
8. **Short read 數字：** 除 B04 與 E4-13 的 long read 部分，本文的數字都來自 short read，只能當機制證據，不能當 diplosim 的校正值。

## 補記（2026-11-05）：B04 細讀

使用者指出，HP1／HP2 在同一 phase block 內就是兩條親代染色體，只是不知道哪條是爸爸。這是對的。所以 B04 的區域偏向，確實是「其中一位親代較多」的局部證據，但沒有固定方向。Fig. 5d 顯示這些富集且偏向的突變，只占全部突變約 0.35–0.41%。細節見 `papers/B04_lung_longread_phasing_2022/summary.md`。
