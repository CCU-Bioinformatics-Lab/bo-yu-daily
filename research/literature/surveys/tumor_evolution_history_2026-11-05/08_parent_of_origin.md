# 雙倍體的父系與母系來源（parent-of-origin）在腫瘤演化中的角色

## 結論

- **核心問題有直接量測，但只有一篇 preprint。** PCAWG pan-cancer 腫瘤中（原文未列年齡；PCAWG 以成人為主是我的推論），體細胞 SNV 總量在父系與母系基因組間沒有可偵測的不對稱（E8-01：PCAWG 21 位 admixed 病人，cohort 上限 5.7%）。這篇還沒有同儕審查，只測基因組總量，也沒有分癌別。在本次搜尋範圍內沒找到第二篇獨立量測，也沒找到反駁。
- **共識（單一基因座）：** 部分 CNA／LOH 有父母偏差，且集中在 imprinted 區與特定癌別。14q aUPD 偏父系（21/22，E8-16）。11p15 cnLOH 依癌別不同（E8-12、E8-13）。
- **有爭議：** neuroblastoma 1p 的母系流失（E8-06 的 13/15，E8-07 的 6/10）。RB1 第一個體細胞突變的父系偏差（osteosarcoma 12/13，retinoblastoma 沒有）。這些研究樣本都很小，且來自 1987–1993 年。
- **沒有證據：** 在本次搜尋範圍內，沒找到 long read 全基因組定出腫瘤 SNV 或 CNA 父母來源的研究。沒找到 gain、deletion 的全基因組父母偏差統計。沒找到 Xi 的父母來源和腫瘤結果之間的量測。
- **不要混淆：** germline de novo 突變的父系偏差（E8-G1：55.4 比 14.2）是生殖細胞的事件。它不能外推到體細胞。E8-01 的結果也和這種外推不一致。
- **對模擬器〔推論〕：** 在單點突變階段，現有證據沒有要求真值層加父／母標籤才能產生 SNV 分布。到 CNA 階段，父／母標籤才有生物意義，但前提是模擬器有基因組座標。

## 問題 A–F 的直接回答

| 問題 | 回答 | 證據 |
|---|---|---|
| A. 單點突變有偏差嗎？ | 全基因組：沒偵測到（上限約 5%）。單一基因座：RB1 有衝突的舊資料。 | E8-01；E8-02、E8-03 |
| A. LOH 有偏差嗎？ | 依基因座和癌別而定。沒有全基因組統計。 | E8-05、E8-06、E8-07、E8-12、E8-13、E8-16 |
| A. gain 有偏差嗎？ | 少數案例：N-myc 擴增偏父系（12/13）。hyperdiploid ALL 的多數 trisomy 沒偏差。 | E8-07、E8-14 |
| A. deletion／monosomy 有偏差嗎？ | near-haploid ALL 多數染色體沒偏差。1p 有衝突。 | E8-13、E8-06、E8-07 |
| B. 機制 | imprinting 是主要假說。BRCA 的 second hit 由「哪條帶 germline 突變」決定，不是由父／母決定。JAK2 是 germline haplotype 的 cis 效應。粒線體不屬於本題，只在 E8-01 當母系標記。 | E8-16、E8-08、E8-17、E8-01 |
| C. germline 偏差能外推嗎？ | 不能。 | E8-G1、E8-03、E8-01 |
| D. long read 能定來源嗎？ | 可以，正常細胞中整條染色體都行（5 個 trio），但要 Strand-seq 等長距離資訊。腫瘤中未驗證。 | E8-09、E8-12、E8-15 |
| E. 「SNV 隨機落在父／母」 | 量過一次（preprint），未被反駁，範圍窄。 | E8-01 |
| F. 模擬器要記父／母嗎？ | SNV 階段沒有證據要求；CNA 階段才有差距。 | 〔推論〕，見差距表 |

### E 題和主題 04 的分別

- 單一腫瘤的 HP1 vs HP2 偏差，可能來自 selection、區域效應或 lesion segregation。它不能單獨說明父／母來源的效果。〔推論〕
- HP1／HP2 對父母來源是隨機指派的（E8-09）。所以就算存在父系偏差，跨病人平均 HP1 比例仍會接近 0.5，方向訊息會消失。〔推論〕
- 要看來源本身的效果，必須先定出父／母，再比較跨病人的方向。E8-01 的 10 人方向性檢定就是這種設計。

## 搜尋範圍

- **日期：** 2026-11-05。
- **來源：** WebSearch（15 組查詢）、PMC 頁面、bioRxiv、Nature 期刊頁、OpenAlex。
- **關鍵字：** parent-of-origin、parental origin、somatic mutation、maternal／paternal haplotype、LOH、uniparental disomy、imprinting、Strand-seq、nanopore、mosaic chromosomal alterations、JAK2 46/1、TP53 codon 72、BRCA parental origin。
- **期間：** 不限；實際論文為 1987–2026。
- **重要限制：** 當天 NCBI E-utilities、PubMed MCP 與 Europe PMC 的查詢都失敗（HTTP 500／503、API error）。所以**沒有做過系統性 PubMed 檢索**。文中「沒找到」都只指 WebSearch 這幾組查詢的範圍。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| H1：SNV 總量在父母基因組間對稱 | 父／母比例接近 1:1，clonal、subclonal 都一樣 | E8-01 | 在本次範圍內沒找到 | PCAWG 癌別混合；只含 admixed 病人的部分基因組；不含 imprinted 區 | 證據不足（單篇 preprint，目前無反證） |
| H2：imprinting 使 LOH／aUPD 偏向特定親源 | imprinted 基因座的流失方向不隨機 | E8-16（14q）、E8-05（Wilms 11p）、E8-12（colon 11p15）、E8-13（回顧 adrenocortical） | E8-16（22q 沒偏差）、E8-12（乳癌、肺癌 11p15 各半）、E8-13（回顧 AML） | 特定基因座、特定癌別 | 共識（局部）；不能推廣到全基因組 |
| H3：neuroblastoma 1p36 母系流失 | 流失的 1p 多為母系 | E8-06 | E8-07 | 兒童 neuroblastoma | 爭議 |
| H4：RB1 第一個體細胞突變偏父系 | 散發腫瘤留下的突變等位基因多為父系 | E8-02（osteosarcoma） | E8-03、E8-04（retinoblastoma） | 兒童、青少年腫瘤 | 爭議 |
| H5：全染色體增減受 imprinting 影響 | trisomy／monosomy 親源有偏差 | E8-14（+8、+14 未達顯著）、E8-13（chr11，未校正） | E8-14、E8-13 的多數染色體 | 兒童 ALL | 多數染色體沒偏差；個別未定 |
| H6：BRCA second hit 落在野生型 | LOH 流失野生型，和父／母無直接關係 | E8-08 | E8-08（BRCA2 乳癌 46% 保留野生型） | 帶因者的乳癌、卵巢癌 | LOH 方向為共識；父母來源的影響未測 |
| H7：germline haplotype 影響 cis 上的體細胞事件 | 突變集中在特定 haplotype | E8-17 | 機制未定（作者保留兩種可能） | MPN 的 JAK2 | 關聯為共識；不等於父母效應 |
| H8：Xi 比 Xa 累積更多突變 | 女性 Xi 突變密度較高 | E8-11、E8-01 | E8-11（CLL、大腸癌等不一定有） | 依癌別不同；屬 Xi／Xa，不是父／母 | 共識（Xi 效應）；Xi 的父母來源未測 |

## 論文卡片

### E8-01 Lefèbvre 2026, bioRxiv preprint — 10.64898/2026.09.02.748867
- **資料：** PCAWG 2,645 人篩出 21 位 admixed 病人，癌別混合（作者未逐癌別列出，只舉 chromophobe RCC 例子）。bulk WGS。**short read**（paired-end 100 bp，約 55X）。單區域。真值來源：無 trio；用 local ancestry 當親源代理，用 mtDNA、chrX、chrY 判定父母。
- **讀取層級：** 全文；Supplementary Table 1–3（bioRxiv media-1～3.tsv，2026-11-09 讀）。未經同儕審查。
- **21 人的癌別與 purity（2026-11-09 補）：** 癌別取自 S1 的 project 欄，再用本機 PCAWG `icgc_sample_annotations_summary_table.txt` 以 tumour aliquot ID 對上 histology_abbreviation（21／21 對上）。Breast-AdenoCA 6、Uterus-AdenoCA 3、Kidney-ChRCC 2、Panc-AdenoCA 2、Skin-Melanoma 2，Prost-AdenoCA、Eso-AdenoCA、ColoRect-AdenoCA、SoftTissue-Leiomyo、Liver-HCC、Ovary-AdenoCA 各 1。論文和補充表都沒有 purity 欄；PCAWG consensus purity 是 0.38–0.98（中位數 0.78），4 人 < 0.5，8 人 WGD。論文沒寫用哪一版 purity〔論文〕〔repo〕`/big8_disk/boyu114/benchmark_data/PCAWG/icgc25k_open/`。S3 中有 1 人（0bfd1043，Prost-AdenoCA，淋巴結轉移）haplotype A 比例 0.41、p ≈ 0，偏離 50%〔論文〕。
- **用了建樹工具：** 無。
- **觀點：** 作者認為結果「validating a key assumption of cancer evolutionary analyses」，並稱這是首次活體量化。
- **演化假設：** 兩條親代基因組累積體細胞突變的速率相同。作者指出多數癌症基因體分析隱含這個假設，gain timing 尤其依賴它。
- **真實結論：**
  - balanced 區 21 人全部落在對稱的預期範圍（Results「Stable global mutation burden」第 1 段）。
  - 不對稱上限：最佳病人 4%；全 cohort 5.7%（12,839 SNV，p = 0.329）。對 5% 以上有 90% power。
  - 方向性檢定只有 10 人：−0.03%，95% CI −7.25% 到 2.22%，p = 0.34。
  - clonal／subclonal 沒有顯著差異；(C>T)pG 沒有偏差。
  - 陽性對照：11 位女性中 8 位 Xi 突變較多，4 位顯著。
- **限制與反證：**
  - 摘要寫 4-5%，Results 寫 5.7%；方向性 CI 下限 −7.25% 也超過 5%。實際可排除的範圍比摘要標題窄。
  - 平均只用 30.25% 基因組，平均 32.77% SNV 可定相；每人 SNV 中位數 5,882。
  - imprinted 區只有 2 個可定相突變，所以**沒有測到最可能有偏差的區域**。
  - 個別病人的個別區域有顯著差異，作者視為孤立觀察。
  - 只測總量。這不證明單一基因座或 driver 沒有偏差，也不證明每個 SNV 彼此獨立。〔推論〕
  - admixed 病人不一定能代表所有人；作者自己指出遠緣 ancestry 會加大局部突變率差異。
  - 定相方法：親代 ancestry 分類 chrX 98–100%、chrY 94–98%；SNV 定相一致率 95.93%。
  - 我沒有找到獨立團隊的重複研究或評論。
- **支持哪一層（N3）：** 觀測特徵（突變數分布），部分支持演化路徑（clonal vs subclonal）。不支持克隆結構。
- **對 diplosim 的意義〔推論〕：** 對應 `src/hp.rs:30` 的 Bernoulli(0.5)。它支持「總量上沒有明顯父母偏差」，但不支持「獨立」這一半；獨立性屬主題 04。屬真值層。short read 數字不能當 diplosim 校正目標。

### E8-02 Toguchida 1989, Nature — 10.1038/338156a0
- **資料：** 13 個散發 osteosarcoma。親子標記比對。bulk。非定序時代（讀長不適用）。
- **讀取層級：** 只有摘要（付費牆）。不能當主要證據。
- **用了建樹工具：** 無。
- **觀點：** 作者認為牽涉 germinal imprinting。
- **演化假設：** 兩條 RB1 拷貝對第一次突變的易感性依親源不同。
- **真實結論：** 12 of 13 的第一個突變在父系（摘要）。
- **限制與反證：** 樣本小。E8-03、E8-04 在 retinoblastoma 看不到。「第一個突變」是推論順序，不是直接測到。
- **支持哪一層（N3）：** 演化路徑（單一基因座的事件順序），證據弱。
- **對 diplosim 的意義〔推論〕：** diplosim 沒有基因，無法表達這種基因座偏差。

### E8-03 Dryja 1989, Nature — 10.1038/339556a0
- **資料：** retinoblastoma 病人（摘要頁未給出總數）。親子標記比對。
- **讀取層級：** 只有摘要（付費牆）。
- **用了建樹工具：** 無。
- **觀點：** 新生 germline 突變主要來自精子生成。
- **演化假設：** Toguchida 的父系偏好是否也存在於 retinoblastoma。
- **真實結論：** 第一個體細胞突變沒有偏好；新生 germline 突變來自父親。
- **限制與反證：** E8-12 引本文來支持「散發 RB 的 maternal chr13 優先流失」，和本文摘要不合。引用這點時要回原文，不能只看 E8-12。
- **支持哪一層（N3）：** 演化路徑（單一基因座）。
- **對 diplosim 的意義〔推論〕：** 它把「germline 父系偏差」和「體細胞偏差」分開，正是 C 題要的對照。

### E8-04 Zhu 1989, Nature — 10.1038/340312a0
- **資料：** 8 位非家族病人，9 個 retinoblastoma。親子標記比對。
- **讀取層級：** 只有摘要（付費牆）。
- **用了建樹工具：** 無。
- **觀點：** 雙側病例的偏差來自精子生成或早期胚胎 imprinting，兩者未分開。
- **演化假設：** 腫瘤留下的 RB1 等位基因是否偏父系。
- **真實結論：** 6 留父系、3 留母系；單側 3 個只有 1 個留父系；雙側 5 位中 4 位留父系。
- **限制與反證：** 樣本極小，無統計力。
- **支持哪一層（N3）：** 演化路徑（單一基因座）。
- **對 diplosim 的意義〔推論〕：** 同 E8-03。

### E8-05 Schroeder 1987, Am J Hum Genet — PMC1684136
- **資料：** 5 位 Wilms 病人和父母。chr11 探針。非定序時代。
- **讀取層級：** 只有摘要（PMC 為掃描檔，無文字）。
- **用了建樹工具：** 無。
- **觀點：** 流失的 chr11 親源不隨機。
- **演化假設：** chr11 的流失依親源而定（後來連到 11p15 imprinting）。
- **真實結論：** 5 位病人中流失的都是母系。
- **限制與反證：** n = 5。全球 Wilms 的現代統計本次沒讀到。
- **支持哪一層（N3）：** 克隆內單一事件的方向，不涉及樹。
- **對 diplosim 的意義〔推論〕：** LOH 方向屬 CNA 階段；要先有座標才能表達。

### E8-06、E8-07 Caron 1993／Cheng 1993, Nat Genet — 10.1038/ng0693-187；10.1038/ng0693-191
- **資料：** 同期兩篇。Caron：53 個 neuroblastoma，15 個有 1p36 LOH。Cheng：22 個 N-myc 擴增腫瘤，用病人和父母 DNA。
- **讀取層級：** 兩篇都只有摘要（付費牆）。
- **用了建樹工具：** 無。
- **觀點：** Caron 認為是 1p imprinting 的第一個證據。Cheng 認為 imprinting 影響 N-myc 擴增，但不影響 1p。
- **演化假設：** 癌症特異的重排依親源而定。
- **真實結論：** Caron：13/15 流失母系。Cheng：N-myc 擴增偏父系 12/13（P = 0.002）；1p 流失 10 例中 6 例父系，符合隨機（P > 0.2）。
- **限制與反證：** 兩篇在 1p 上直接衝突。兩者選的病例不同（Cheng 只收 N-myc 擴增），這可能是原因之一。〔推論〕
- **支持哪一層（N3）：** 單一事件方向。
- **對 diplosim 的意義〔推論〕：** gain／amplification 屬 CNA 階段。現階段只記為差距。

### E8-08 Maxwell 2017, Nat Commun — 10.1038/s41467-017-00388-9
- **資料：** 160 個 germline BRCA1/2 乳癌、卵巢癌（TCGA 100、Penn 60）。WES。**short read**。單區域。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 沒有 locus-specific LOH 可能是抗藥的生物標記。
- **演化假設：** 帶因者的腫瘤都靠 LOH 失去野生型。
- **真實結論：** 保留野生型比例：BRCA1 卵巢 7%、BRCA2 卵巢 16%、BRCA1 乳癌 10%、BRCA2 乳癌 46%。
- **限制與反證：** **本文沒有分析父／母來源。** 它只說 second hit 由「哪條帶 germline 突變」決定。WES 看 LOH 有偵測限制。
- **支持哪一層（N3）：** 單一事件方向（LOH 流失哪條）。
- **對 diplosim 的意義〔推論〕：** 回答 B 題：germline 背景決定 LOH 落點時，看的是有沒有帶突變，不是父／母標籤。diplosim 沒有 germline driver 概念。

### E8-09 Akbari 2023, Cell Genomics — 10.1016/j.xgen.2022.100233
- **資料：** 5 個正常人 trio（NA12878、HG002、HG005、HG00733、NA19240）。**long read**（nanopore 24–38×）＋ Strand-seq 42–220 libraries。真值：trio 定相。**沒有腫瘤樣本。**
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者預期可改善遺傳疾病的診斷。
- **演化假設：** 無（方法論文）。假設 iDMR 在個體和組織間穩定。
- **真實結論：**
  - 220 條同源染色體全部判對；mismatch 平均 SNV 0.31%、indel 1.89%。
  - 用 192 個 iDMR（144 母系、48 父系），只占體染色體約 0.014%。每條染色體平均 5.7 個（1–29）；信心分數 95.7%（57.5–100%）。
  - 只靠 nanopore 的 phase block N50 為 4.85 Mb，不跨全染色體，也不一定含 iDMR。這是為什麼要 Strand-seq。
  - X 染色體未納入。
  - HP1／HP2 指派對父母來源是隨機的。
- **限制與反證：** 輸入是全血或可培養的活細胞。作者承認其他組織的 iDMR 可能不同。腫瘤有 iDMR 改變、CNA、switch error（見 E8-12），這些都未測。〔推論〕
- **支持哪一層（N3）：** 觀測層能力，不是演化證據。
- **對 diplosim 的意義〔推論〕：** 觀測層。真實 long read bulk 沒有 Strand-seq 時，只有含 iDMR 的 phase block 才可能指派父母。真值層標籤和這個能力是兩件事（N1）。

### E8-11 Jäger 2013, Cell — 10.1016/j.cell.2013.09.042
- **資料：** 402 個腫瘤 WGS，含兒童與成人腫瘤。**short read**。read pair 定相只有少數樣本（MB101、淋巴瘤 4120193）。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** Xi 超突變來自異常增殖細胞的 replication stress，是早期事件。
- **演化假設：** Xi 較晚複製，因此累積更多突變。
- **真實結論：** Xi 平均 2 倍、最高 4 倍。定相：MB101 為 46 Xi、12 Xa；淋巴瘤 389/444 在 Xi。放寬定義後 83/191（43%）女性受影響。正常 HSPC 和 MDS 沒有。
- **限制與反證：** 本文**沒有分析 Xi 是父系還是母系**（全文只有一句提到「a maternal and a paternal copy」）。E8-01 也只分 Xa／Xi。所以 Xi 的親源隨機性和腫瘤結果的關係，在這兩篇內沒有量測。
- **支持哪一層（N3）：** 觀測特徵（突變密度）。
- **對 diplosim 的意義〔推論〕：** 兩條 HP 間的真實不對稱確實存在，但來源是 Xa／Xi 狀態，不是父／母。diplosim 沒有 X 染色體概念。

### E8-12 Martin-Trujillo 2017, Nat Commun — 10.1038/s41467-017-00639-9
- **資料：** 超過 280 個 cancer cell line，並和 TCGA 原發腫瘤比對。HM450k 甲基化陣列加 CNA。非定序為主。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** imprinted DMR 的異常主要是 CNA 造成，不是 epigenetic 錯誤。
- **演化假設：** 「imprinting 異常在腫瘤中很常見」。作者認為多數只是 CNA 的結果。
- **真實結論：** 280 中 258 個至少一段 cnLOH 碰到 imprinted locus。11p15.5 cnLOH：乳癌、肺癌 cell line 父母各半，大腸癌 cell line 全父系。7/7 肺癌 cell line 有 RB1 DMR 高甲基化。帶同型突變時，突變的影響大於父母來源。
- **限制與反證：** cell line 不等於原發腫瘤，有培養選擇。引 Dryja 1989 的句子和原文摘要不合（見 E8-03）。
- **支持哪一層（N3）：** 觀測特徵（甲基化與 CN 關係）。
- **對 diplosim 的意義〔推論〕：** 對 D 題重要。腫瘤中甲基化比例會被 CN 改變，所以用 iDMR 判父母時，CN 和親源是混在一起的。屬觀測層。

### E8-13 Lundin-Ström 2020, Blood Cancer J — 10.1038/s41408-020-0317-2
- **資料：** 7 位 near-haploid ALL 病人＋ 2 個 cell line。imprinted 基因座的甲基化分析。非定序。
- **讀取層級：** 全文（letter）。
- **用了建樹工具：** 無。
- **觀點：** 父母同源染色體在此病隨機流失；chr11 可能例外。作者指出看 cnLOH 親源的研究只有少數。
- **演化假設：** 留下哪條 monosomy 會受 imprinting 影響。
- **真實結論：** chr 6、7、14、15 沒偏差。chr 11 有 8/9 留母系（P = 0.039，未校正）。作者回顧：adrenocortical 11p15 cnLOH 絕大多數重複父系；AML 與 leiomyosarcoma 沒偏差。
- **限制與反證：** n = 9，校正後不顯著。回顧句是二手資料，原文未讀。
- **支持哪一層（N3）：** 單一事件方向。
- **對 diplosim 的意義〔推論〕：** 全染色體流失多為隨機，只有基因座例外。屬 CNA 階段。

### E8-14 Paulsson 2003, Blood — 10.1182/blood-2003-05-1444
- **資料：** 10 位兒童 hyperdiploid ALL，38 個 microsatellite。非定序。
- **讀取層級：** 只有摘要。
- **用了建樹工具：** 無。
- **觀點：** imprinting 在此病不重要，+8、+14 可能例外。
- **演化假設：** trisomy 的親源受 imprinting 影響。
- **真實結論：** X、4、6、9、10、17、18、21 沒偏差。+8 為 4/4 父系（P = .125）；+14 為 7/8 母系（P = .0703）。
- **限制與反證：** 樣本小；兩個例外未達顯著。
- **支持哪一層（N3）：** 單一事件方向。
- **對 diplosim 的意義〔推論〕：** gain 的親源多數沒偏差。屬 CNA 階段。

### E8-15 Stacey 2025, JCI Insight — 10.1172/jci.insight.188216
- **資料：** 16 位 germline RB1 病人（家族 7、新生 9）。**血液** DNA，**long read**（ONT adaptive sampling，targeted）。不是腫瘤 DNA。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 父母來源是預後標記。
- **演化假設：** RB1 的 germline 變異效應依親源不同。
- **真實結論：** RB1 intron 2 的 DMR 母系甲基化；變異和 DMR 相距最多 154 kb 仍可定相。15 位分析：母系 6、父系 9。父系較晚就診（8.5 vs 2.6 月，P = 0.03），較晚分期 8/18 眼 vs 2/12 眼，化療失敗較多（P = 0.02）。
- **限制與反證：** 小樣本；分期的 Fisher 檢定無顯著差異。這是 germline 變異的親源，不是體細胞。
- **支持哪一層（N3）：** 觀測層能力；臨床表型關聯。
- **對 diplosim 的意義〔推論〕：** 示範局部定親源可在沒有 Strand-seq 時做到，但只限 DMR 附近的 phase block。屬觀測層。

### E8-16 Chase 2015, Leukemia — 10.1038/leu.2015.130
- **資料：** 29 例 aUPD14q，骨髓系腫瘤和老年族群。甲基化特異 PCR；7 例 exome（**short read**）。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** aUPD14q 目標是 imprinted locus，可能足以驅動 clonal hematopoiesis。
- **演化假設：** 父系同型提供生長優勢。
- **真實結論：** 22 例中 21 例父系（P<0.0001）。aUPD22q 母系 2、父系 3，作者判定沒有偏差。
- **限制與反證：** 血液疾病，不能外推到實體瘤。22q 只有 5 例。
- **支持哪一層（N3）：** 克隆選擇的方向；部分支持演化路徑（有些例子是早期事件）。
- **對 diplosim 的意義〔推論〕：** 這是本次讀到最強的父母偏差案例，但作者的解讀是 selection，且限 14q 與骨髓系。屬 CNA 階段的差距。

### E8-17 Jones 2009, Nat Genet — 10.1038/ng.334
- **資料：** MPN：PV 192、ET 78、MF 41，加對照。genotyping 和 allele-specific PCR。非全基因組定序。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 種系因子可提高特定體細胞突變的風險。
- **演化假設：** 突變可能優先發生或被選擇在特定 germline haplotype。
- **真實結論：** 142 個帶 V617F 的等位基因中 109 個（77%）是 46/1；46/1 族群頻率 0.24；OR 3.7（3.1–4.3）。
- **限制與反證：** 作者未分開 hypermutability 和選擇。本文看的是 haplotype，不是親源；46/1 可來自父或母。
- **支持哪一層（N3）：** 單一基因座的觀測關聯。
- **對 diplosim 的意義〔推論〕：** 這類 cis 效應和父／母標籤無關，應記到 germline haplotype，不是親源。

### 對照與背景（不當主要證據）

- **E8-G1 Kong 2012, Nature — 10.1038/nature11396（germline，非腫瘤）：** 78 個冰島 trio 全基因組（short read，全文）。每年約多 2 個 de novo 突變。5 個可定親源的 trio 中，父系 55.4、母系 14.2。**這是生殖細胞的 de novo 突變。** 〔推論〕它不能外推：這些突變在受精前就已存在於親代生殖系，而腫瘤體細胞突變發生在受精後的體細胞。兩者的機制和時間都不同。E8-03 和 E8-01 也支持這個區分。
- **E8-10 Zink 2018, Nat Genet — 10.1038/s41588-018-0232-7（只讀摘要）：** 285 個甲基化體、11,617 個轉錄體，周邊血，正常人。imprinted 甲基化是連續特徵，不是二元。〔推論〕這也讓腫瘤中的 iDMR 判定更不確定。

## 對 diplosim 的差距（照優先順序）

| 真實腫瘤的現象 | diplosim 現況 | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| 父／母基因組的 SNV 總量大致對稱 | 每個 SNV 獨立 Bernoulli(`prop_snv_on_b`)（`src/hp.rs:30`）；對 A／B 而非父／母 | 總量層級沒有發現矛盾。「獨立」這一半未被本題證據支持或反駁（見主題 04） | 中低（單篇 preprint） | 單點突變 |
| 每條 haplotype 有父／母身分（生物事實） | 只有 allele A／B；`diplosim/src`、`DECISIONS.md` 用 maternal、paternal、parent of、imprint 搜尋都沒有結果 | 真值層沒有這個標籤。單點突變階段，現有證據沒有顯示 SNV 分布會因此改變 | 高（事實本身）；用途不確定 | 單點突變（標籤）／CNA 後（用途） |
| imprinted 基因座的 LOH／aUPD 偏向特定親源，依癌別不同 | CN 每個 position 獨立（`docs/conipher_steps.md` S4–S6），SNV 沒有座標 | 沒有基因組座標，無法表達基因座層級的方向性 | 中 | CNA 後 |
| Xi 突變較多（女性、部分癌別） | 沒有 X 染色體，沒有座標 | 無法表達 | 高（E8-11、E8-01）；但屬 Xa／Xi，不屬父／母 | 單點突變或之後，待決定 |
| germline haplotype 的 cis 效應（JAK2） | 沒有 germline 變異和基因的概念 | 無法表達；和父／母無關 | 中（單一基因） | 超出目前範圍〔推論〕 |
| 真實資料中，父／母只能從 iDMR 和長距離定相得知 | 觀測層只有 HP1／HP2／HP0 | 目前不需要模擬親源觀測。要測試方法時才需要 | 中（正常細胞）；腫瘤未驗證 | 觀測層 |

**F 題整理〔推論〕：**

- 樹重建工具看到的是 HP1／HP2，不是父／母。在沒有親源偏差的前提下，把 A／B 改名成父／母，不會改變樹重建的輸入。
- 所以就「測試 HP 能否改善樹重建」這個目標而言，父／母標籤在單點突變階段沒有已知用途。
- 它可能有用的情況：(1) CNA 階段要表達 imprinted 偏差；(2) 之後要測試親源推斷本身。
- E8-01 的上限只有約 5%，不是 0。而且它沒測 imprinted 區。所以這是「沒有證據要求」，不是「已證明不需要」。

## 未解問題

1. 長讀且有親源資訊的腫瘤研究：在本次查詢範圍內，沒找到用 long read 為腫瘤全基因組指派父母的研究，E8-01 只把它列為未來方向。
2. E8-01 尚未同儕審查，也沒有獨立重複。上限的單位（比例差或相對差）在 Results 和 Extended Data 寫法不完全相同，未核對 Supplementary Table 3。
3. driver 與 imprinted 區的 SNV 親源：E8-01 測不到。
4. gain、deletion 的全基因組親源統計：在本次查詢範圍內沒找到。
5. Xi 的父母來源對腫瘤有沒有影響：E8-11、E8-01 都沒測。
6. **看到但沒讀到，不算證據的線索：** Feinberg 2006（Nat Rev Genet）；Goldmann（germline）；Loh 2020（Nature，mCA 與遺傳變異）；Hensen 2004（SDHD 與 chr11 母系流失）；Pal 1990（Oncogene，Wilms 母系）；2002 Ann Neurol 的 oligodendroglioma 19q 標題；BRCA 親源與乳癌風險的世代研究（只看到搜尋摘要）；TP53 codon 72 的 cis 偏差（搜尋摘要顯示結果不一致）。要用時須回原文。
7. 工具失敗：PubMed 結構化檢索當天不可用。這些查詢值得在服務恢復後重跑一次，以確認沒有遺漏。
