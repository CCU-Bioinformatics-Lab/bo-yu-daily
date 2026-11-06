# 突變率、mutational signature 與時間

## 結論

- **共識：** 正常細胞的體細胞替換隨年齡近線性累積（E3-08、E3-21、E3-16）。
- **共識：** SBS1 和 SBS5 與診斷年齡相關，而且速率依癌別差很大（E3-01）。
- **共識：** 「clonal」和「subclonal」的比例隨癌別差很大，並受偵測力影響（E3-13）。
- **爭議：** 腫瘤內突變率是否固定。ccRCC 的資料和固定速率相容（E3-04）。其他研究估計速率上升（E3-03、E3-18）。POLE 腫瘤有爆發（E3-14）。
- **爭議：** SBS1 或總突變量能否當「分裂時鐘」。不分裂的 neuron 也以固定速率累積突變（E3-07，只讀摘要）。
- **爭議：** signature 的時間變化有多大。同一批 PCAWG 資料，E3-03 說 40% 樣本改變，E3-13 說活性 remarkably stable。兩篇的指標不同，所以不能直接比。
- **證據不足：** 在本次搜尋中，沒找到用 long read 直接量腫瘤 clone 邊長或 truncal 比例的研究。

**給 diplosim 的一句話〔推論〕：** 它現在的邊長只是 SNV 的隨機分配，沒有速率、時間、分裂次數，也沒有 signature。文獻的 subclonal 比例是偵測後的觀測值，不等於 `prop_truncal_snvs` 這個真值參數。本筆記的數字幾乎都來自 short read，只作生物假說的證據，不是校正目標。

## 搜尋範圍

- **來源：** PubMed E-utilities 與 PMC 全文、Europe PMC（摘要）、WebSearch。
- **關鍵字：** somatic mutation rate、clock-like signature、clonal subclonal signature、mutation rate per cell division、neutral evolution critique、hypermutation POLE MMR、HiFi duplex long-read somatic mutation。
- **期間：** 主要看 2013–2024；WebSearch 含到 2025 年的 preprint。
- **日期：** 2026-11-05。
- **取得限制：** NCBI 當天多次回 429／500。部分論文只取到摘要（見「未解問題」）。PubMed 的關鍵字查詢有 2 次回 API error，所以反證搜尋主要靠 WebSearch，涵蓋不完整。

**Long read 標記：** 只有 E3-16（HiDEF-seq，PacBio）是 long read 平台，但中位分子只有 1.7 kb，用途是單分子準確度，不是長距離 phasing。E3-07 的 NanoSeq 不是 long read。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| H1 正常組織突變隨年齡線性累積 | 突變量對年齡呈直線，截距接近 0 | E3-08、E3-21、E3-16 | 本次搜尋（上述關鍵字與期間）內沒找到直接反證 | 已測的正常組織；E3-21 只測腸與肝 | 共識 |
| H2 SBS1、SBS5 是 clock-like | 計數與年齡相關，其他 signature 不相關 | E3-01 | E3-01 自己：相關強度低（0.34、0.13），部分癌別 SBS5 多但無相關 | 26／36 癌別有相關；不是全部 | 共識，但「時鐘」只是近似 |
| H3 SBS1 記錄分裂次數 | 高增殖組織速率高；不分裂細胞沒有 | E3-01（解讀）、E3-21（解讀） | E3-07 只說整體突變，未細分 SBS1（摘要層級） | 主要是高 turnover 上皮 | 爭議 |
| H4 突變主要來自分裂 | 分裂多的細胞突變多 | 模型常假設（E3-18、E3-17） | E3-07：分化血球分裂更多，突變量卻相似；neuron 不分裂也累積 | 正常組織；腫瘤內未測 | 爭議 |
| H5 腫瘤內突變率固定 | 同腫瘤 subclone 的突變量相近；年齡項不需加速 | E3-04（ccRCC） | E3-03（CpG>TpG 上升 1–10 倍）；E3-18（4–100 倍）；E3-14（POLE 爆發） | ccRCC 可能適用；hypermutator 不適用 | 爭議 |
| H6 Signature 隨演化改變 | 外源 signature 早多，APOBEC／MMR 晚多 | E3-03、E3-12 | E3-13（活性整體穩定） | 吸菸、UV、APOBEC 的方向重複被觀測 | 方向是共識；幅度有爭議 |
| H7 Subclonal 突變近中性累積（1/f） | 累積突變數對 1/f 線性 | E3-17 | E3-20：方法會誤判，真拒絕只約 11% | Bulk VAF 法不足以判定 | 爭議 |

## 論文卡片

### E3-01 Alexandrov 2015, Nat Genet — 10.1038/ng.3441
- **資料：** 10,250 癌基因組，36 癌別；bulk；short read，來源混合；單樣本為主。真值：無。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** Signature 1 可能是記錄有絲分裂次數的時鐘（作者用條件句）。細胞增殖可能不是 signature 5 的主要因素。
- **演化假設：** 某些 process 以固定速率運作，所以突變數和年齡成正比。
- **真實結論：**
  - 33 個 signature 中，只有 signature 1、5 與診斷年齡相關（Spearman 0.34、0.13）。
  - 26／36 癌別個別有相關：signature 1 在 17 癌別，signature 5 在 12 癌別。
  - Signature 1 速率：胃 23.7、大腸 23.4，到 pilocytic astrocytoma 0.65（每 Gb 每年）。
  - Signature 5 速率：kidney papillary 31.8，到 AML 2.8（每 Gb 每年）。
  - 兩者速率跨癌別不相關（−0.08）。
- **限制與反證：** 用癌症樣本回推正常細胞；頭頸、大腸、肺鱗 signature 5 多，但與年齡不相關。訊號歸因依賴 NMF，會互相污染。
- **支持哪一層（N3）：** 觀測特徵（計數與年齡的相關），間接支持演化路徑。
- **對 diplosim 的意義〔推論〕：** diplosim 沒有 signature，也沒有年齡或時間。缺的是真值層的「每個 SNV 由哪個 process 產生」。

### E3-03 Gerstung 2020, Nature — 10.1038/s41586-019-1907-7
- **資料：** PCAWG，2,778 樣本，2,658 捐贈者，38 癌別；bulk WGS，short read，腫瘤最低平均 30×；單樣本。真值：無。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（MutationTimeR、共識 subclonal 重建）。
- **觀點：** 作者自述 molecular timing 受突變率改變影響。
- **演化假設：** 速率固定時，實足時間等於 molecular time 乘診斷年齡。速率改變時關係是非線性的。作者選典型加速 5 倍（腦癌 2.5 倍、卵巢癌 7.5 倍），跨度為診斷前 15 年。Subclone 分攤 subclonal 突變，假設 branching。
- **真實結論：**
  - 點突變：22% early clonal、7% late clonal、53% unspecified clonal、17% subclonal。
  - Driver：29%、5%、56%、8%。
  - 突變譜改變：early→late 29%（530／1,852）；clonal→subclonal 30%（729／2,387）；合計 40%（1,069／2,688）。
  - 下降：SBS4 中位 fold 0.43，SBS7 中位 fold 0.16。上升：APOBEC 2.0，MMR 相關 1.8。
  - CpG>TpG 在癌症中上升 1–10 倍，增加 20–40% 突變。
  - **模型推估（不是量測）：** WGD 在部分癌別早於診斷數年到十年以上；卵巢癌中位 latency 超過 10 年；MRCA 到最後可測 subclone 通常數月到數年。
- **限制與反證：** 實足時間依賴 CpG>TpG 速率情境，加速倍數是選定值。Unspecified clonal 占 53%，時序未知。單樣本看不到低頻 clone。
- **支持哪一層（N3）：** 突變比例屬觀測特徵；時間軸屬演化路徑，但有模型依賴。
- **對 diplosim 的意義〔推論〕：** diplosim 的邊沒有時間單位。這篇提示 clone 間速率不一定固定。比例屬觀測層，不能直接對應 `prop_truncal_snvs`。

### E3-04 Mitchell 2018, Cell — 10.1016/j.cell.2018.02.020
- **資料：** ccRCC，33 病人 95 biopsy；bulk WGS，short read（HiSeq X Ten，腫瘤平均 67x）；多區域。真值：無。
- **讀取層級：** 全文。
- **用了建樹工具：** 有 subclone 層級的 burden；本次全文 grep 常見工具名（PyClone、DPClust、CONIPHER 等）沒有命中，工具名未確認。
- **觀點：** 各 subclone 自分歧後以相同穩定速率累積。
- **演化假設：** 一生固定突變率。t(3;5) 的時間用 5q 上二拷貝與一拷貝突變的比例估。
- **真實結論：**
  - 突變量與年齡線性，87 突變／年（CI 80–94），病人間標準差 17 突變／年。
  - 同腫瘤不同 subclone 的突變量大致相同。
  - 加入年齡平方項沒有顯著改善擬合。
  - **模型推估：** t(3;5) 在診斷前 30–50 年；雙等位 VHL 失活到診斷 15–30 年。
- **限制與反證：** 只有 ccRCC。擬合是跨病人的相關，不是個別腫瘤直接量到的速率時間序列。
- **支持哪一層（N3）：** 克隆結構（subclone 突變量）與演化路徑（時間軸，依賴固定速率假設）。
- **對 diplosim 的意義〔推論〕：** 這是「邊長約和時間成正比」最直接的證據之一，但只適用 ccRCC。diplosim 的隨機切段不產生這種相關。

### E3-05 Lee-Six 2018, Nature — 10.1038/s41586-018-0497-0
- **資料：** 正常血液，59 歲男性，140 個單細胞 colony；WGS short read。真值來源：colony 系譜樹（單細胞解析度）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（作者自建系譜樹；非腫瘤工具）。
- **觀點：** 引文獻說血液幹細胞突變隨年齡線性，暗示準確時鐘。
- **演化假設：** 成年造血是中性模型（模型推估 HSC 數與分裂間隔）。
- **真實結論：**
  - 平均 1023 個替換（815–1210）。
  - 胚胎期 1–2 個突變／分裂。
  - **模型推估：** HSC 對稱分裂間隔 2–20 個月；活躍 HSC 44,000–215,000。
- **限制與反證：** 單一個體，正常組織。
- **支持哪一層（N3）：** 克隆結構與演化路徑（單細胞系譜），但非腫瘤。
- **對 diplosim 的意義〔推論〕：** 分裂與邊長的關係只在「每分裂突變數已知」時才能換算。diplosim 沒有分裂次數。

### E3-07 Abascal 2021, Nature — 10.1038/s41586-021-03477-4
- **資料：** 正常組織，NanoSeq duplex；**不是 long read**；錯誤率每十億鹼基低於 5。
- **讀取層級：** 只有摘要（不當主要證據）。
- **用了建樹工具：** 無。
- **觀點：** 獨立於分裂的 process 是體細胞突變的重要來源。
- **演化假設：** 檢驗「突變依賴分裂」。
- **真實結論：** 血液與結腸的分化細胞，突變量和 signature 都和幹細胞相似，雖然成熟血球分裂更多。Neuron 不分裂，也以固定速率累積。
- **限制與反證：** 只讀摘要，細部數字未核對。正常組織，不是腫瘤。
- **支持哪一層（N3）：** 演化路徑（機制）。
- **對 diplosim 的意義〔推論〕：** 「邊長=分裂次數」不能當預設前提。時間和分裂兩種解釋要分開。

### E3-08 Cagan 2022, Nature — 10.1038/s41586-022-04618-z
- **資料：** 16 物種 56 個體 208 個 crypt；WGS short read；clonal 單位。真值：crypt 克隆性。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** SBS1 被認為來自 5-甲基胞嘧啶脫胺。
- **演化假設：** 突變率和壽命成反比，所以壽命終點的突變負擔相近。
- **真實結論：** 五個物種線性累積且截距不顯著。人類 47 替換／年，小鼠 796。人類 crypt 2% 有 APOBEC。
- **限制與反證：** 只有腸；跨物種比較，不是腫瘤。
- **支持哪一層（N3）：** 觀測特徵（正常組織速率）。
- **對 diplosim 的意義〔推論〕：** 提供 trunk 中「腫瘤前」的突變背景概念。diplosim 的 trunk 不區分腫瘤前與腫瘤後。

### E3-11 Frankell 2023, Nature（TRACERx421）— 10.1038/s41586-023-05783-5
- **資料：** NSCLC，421 病人 1,644 區域；bulk 多區域 whole-exome，short read。真值：無。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（CONIPHER、PyClone）。
- **觀點：** 造成 illusion of clonality 的 subclone 可能帶正選擇訊號。
- **演化假設：** Truncal 代表早期，subclonal 代表晚期；subclonal expansion 會在部分區域造成 illusion of clonality。
- **真實結論：**
  - LUAD 的 truncal SBS4 比例隨 pack-years 上升（r=0.31）；LUSC 不顯著（r=−0.14）。
  - 曾吸菸 LUAD：75% 有吸菸 signature，8% 沒有證據。
  - Illusion of clonality 有 89% 屬 ancestral；26% 腫瘤至少一個 recent subclonal expansion。
  - 多數基因 truncal 選擇訊號強於 subclonal。
- **限制與反證：** WES 只看 exome，邊長是 exome 上的突變數。本次在全文中未抓到全基因組 truncal 比例的單一數字。
- **支持哪一層（N3）：** 克隆結構（多區域）；signature 時序屬演化路徑的間接證據。
- **對 diplosim 的意義〔推論〕：** 同一突變在單區域可能看似 clonal。真值的 trunk 和觀測的 clonal 要分開記。

### E3-12 McGranahan 2015, Sci Transl Med — 10.1126/scitranslmed.aaa1408
- **資料：** TCGA 九癌別 2694 腫瘤；bulk，short read；單樣本。真值：無。
- **讀取層級：** 全文。
- **用了建樹工具：** 無（用 CCF 分類 clonal／subclonal）。
- **觀點：** 無單獨列。
- **演化假設：** Clonal 等於早期，subclonal 等於晚期。
- **真實結論：**
  - 10 個 robust signature，多數隨發展改變盛行度。
  - Signature 4（LUAD）、7（SKCM）早期多。Signature 2 隨時間增加；signature 13 在 BLCA 反而早期多。
  - 肺與頭頸 APOBEC 樣本：clonal driver 平均 21% 屬 APOBEC context，subclonal 超過 45%。
- **限制與反證：** 單樣本把 illusion of clonality 算成 clonal。Clonal 和早期不完全等價。
- **支持哪一層（N3）：** 觀測特徵，間接支持演化路徑。
- **對 diplosim 的意義〔推論〕：** trunk 與 subclonal 邊的 signature 組成可能不同；diplosim 沒有這層資訊。

### E3-13 Dentro 2021, Cell — 10.1016/j.cell.2021.03.009
- **資料：** PCAWG；1,705 個 powered 樣本（中位約 46×）；bulk，short read；單樣本。驗證：模擬、read phasing。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（11 個方法的共識，含 DPClust、PhylogicNDT、PyClone）。
- **觀點：** 單樣本估計是保守下限。
- **演化假設：** 突變的 CCF 分群反映 subclone。
- **真實結論：**
  - 95.1% 至少一個 subclonal expansion（1,621 例）。
  - Subclonal SNV 比例（校正後）：肺鱗 6.1%±6.7%、頭頸 9.7%±11.9%、子宮頸 20.6%±19.6%；高端 chromophobe 45.2%、PanNET 46%、pilocytic astrocytoma 61.3%。
  - 偵測：可測 subclone 內平均漏 14% SNV；CCF 低於 30% 時漏 21%。偵測力依 purity、ploidy、深度。
  - 5 個前列腺腫瘤：單樣本漏 44% 變異，26% subclonal 突變看似 clonal。
  - Signature 活性在 clone 與 subclone 間穩定；SBS12 在肝癌（198／326 活躍）是最常變動的。
  - 兩個 subclone 是手足關係的機率是親子的 3.11 倍。
  - Linear／branching 和 mutation burden 無顯著差異（p=0.594）。
- **限制與反證：** 只能偵測 CCF 超過 30% 的 subclone。前列腺的修正只有 5 例。
- **支持哪一層（N3）：** 克隆結構；比例本身屬觀測特徵。
- **對 diplosim 的意義〔推論〕：** 這篇直接回答 `prop_truncal_snvs` 的問題：觀測值的跨癌別範圍很大，而且受深度影響。真值層比例在這批資料中沒有直接量到。

### E3-14 Campbell 2017, Cell — 10.1016/j.cell.2017.09.048
- **資料：** 78,452 成人癌、2,885 兒童癌；targeted panel，short read；單樣本。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者用「模型」描述三種累積型態，有部分是推斷。
- **演化假設：** Signature 組成可反推 mutator 事件的先後。
- **真實結論：**
  - Hypermutation 定義為 10 Mut/Mb。成人 17%、ultra-hypermutation 0.6%。
  - 兒童癌範圍 0–864 Mut/Mb。
  - 第一型：吸菸、UV、MMR 緩慢穩定累積。第二型：POLE 腫瘤中段爆發。第三型：晚期爆發。
- **限制與反證：** Panel 只有 1.1–3.25 Mb；時序是從 signature 推論，不是直接時間序列。臨床 cohort 有選樣偏差。
- **支持哪一層（N3）：** 觀測特徵（burden）；時序屬演化路徑的推論。
- **對 diplosim 的意義〔推論〕：** Mutator 讓一條邊長暴增。diplosim 沒有 clone 特異的速率。

### E3-16 Liu 2024, Nature（HiDEF-seq）— 10.1038/s41586-024-07532-8
- **資料：** 精子、血液、肝、腎、皮質 neuron、癌症易感症候群；**PacBio single-molecule（long read 平台）**，中位 32 passes，中位分子 1.7 kb；另有 Illumina 配對。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** PacBio 單 pass 替換準確度可能比先前估計高。
- **演化假設：** ssDNA mismatch 是 dsDNA 突變的前驅。
- **真實結論：**
  - 精子 dsDNA burden 和 de novo 研究、NanoSeq 一致。
  - 肝、腎、血、neuron 的 dsDNA burden 隨年齡線性。
  - POLE PPAP 的 ssDNA call 增 2.6 倍，CMMRD 增 1.6 倍。
- **限制與反證：** 1.7 kb 分子不提供長距離 phasing。不是腫瘤 clone 層級的量測。
- **parent-of-origin：** 文中和**父系定相的 de novo** 比較，這屬生殖細胞、不是腫瘤。父／母的資訊來自 trio，不是來自 read。
- **支持哪一層（N3）：** 觀測特徵。
- **對 diplosim 的意義〔推論〕：** 唯一符合「long read 平台」的速率研究，但測的是正常與易感組織。不能當腫瘤 clone 邊長的參考。

### E3-17 Williams 2016, Nat Genet — 10.1038/ng.3489
- **資料：** 14 癌別 904 癌；bulk，short read；單樣本。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 中性癌中，所有 clonal selection 都發生在癌生長前。
- **演化假設：** 中性生長時，累積突變數對 1/f 線性。
- **真實結論：** 模型對 323／904 癌擬合很好。MSI 組有效突變率比 CIN 高超過 15 倍。有效突變率被未知的 β 縮放。非中性病例無法估計。
- **限制與反證：** E3-20 直接質疑。
- **支持哪一層（N3）：** 觀測特徵（VAF 分布）；中性的解讀未被證實。
- **對 diplosim 的意義〔推論〕：** 分布形狀由邊長與 clone 比例決定。diplosim 所有 clone 都在 sample 裡，沒有低頻長尾。

### E3-18 Werner 2020, Nat Commun — 10.1038/s41467-020-14844-6
- **資料：** 血液（Lee-Six 資料）、胎兒 neuron、16 腫瘤 131 biopsy（1 adenoma、7 colon、5 ccRCC、2 肺鱗）；WGS／WES，short read；多樣本。
- **讀取層級：** 全文。
- **用了建樹工具：** 無（用突變距離分布）。
- **觀點：** 無單獨列。
- **演化假設：** 固定突變率，無爆發事件；每次分裂突變數 Poisson。
- **真實結論：**
  - 單一 lineage 的突變量無法分開每分裂突變率和存活率。
  - 正常：1.14 與 1.37 突變／基因組／分裂（3.9×10⁻¹⁰、4.6×10⁻¹⁰ bp/分裂）。
  - 腫瘤：每分裂突變率高 4–100 倍（2.91×10⁻⁹ 到 53×10⁻⁹ bp/分裂）。
  - 病人間差異顯著，同病人的染色體間沒有。
- **限制與反證：** 模型本身假設固定速率，和它要回答的問題有張力。腫瘤解析度比正常組織低。比較基準是模型的健康值。
- **支持哪一層（N3）：** 克隆結構（距離分布）；每分裂速率依賴模型。
- **對 diplosim 的意義〔推論〕：** 邊長不等於分裂次數，因為存活率也影響。這是 diplosim 真值層缺的兩個獨立量。

### E3-20 Tarabichi 2018, Nat Genet — 10.1038/s41588-018-0258-x
- **資料：** 評論與模擬；真值來源：模擬。
- **讀取層級：** 全文（短評）。
- **用了建樹工具：** 無。
- **觀點：** Williams 法常把非中性判成中性，也會反過來。
- **演化假設：** 指出 Williams 模型假設同步分裂與固定死亡、突變、分裂率。
- **真實結論：** 含 selected subclone 的模擬中，真實拒絕中性只約 11%。
- **限制與反證：** 這是對方法的批評，不是證明腫瘤是選擇性的。
- **支持哪一層（N3）：** 方法層；說明觀測特徵不足以判演化路徑。
- **對 diplosim 的意義〔推論〕：** 呼應 N3：VAF 形狀相似不能證明真值過程對。

### E3-21 Blokzijl 2016, Nature — 10.1038/nature19768
- **資料：** 小腸、結腸、肝的成體幹細胞，捐贈者 3–87 歲；clonal organoid WGS，short read。真值：clonal 培養。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 腸的突變主要是增殖相關的 CpG 脫胺加上另一 process。
- **演化假設：** 檢驗突變累積速率是否和癌症風險相關。
- **真實結論：** 約每年 40 個新突變。癌症發生率不同的器官，累積速率相似。肝的突變譜和腸不同。
- **限制與反證：** 只有三個器官。和 E3-01 的「組織差很大」範圍不同：E3-01 用癌症資料、分 signature 算速率。
- **支持哪一層（N3）：** 觀測特徵（正常組織速率）。
- **對 diplosim 的意義〔推論〕：** 組織差異可能在 signature 組成，而不一定在總速率。

## 對 diplosim 的差距（照優先順序）

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| 真值 trunk 與觀測 clonal 不同：單樣本會把 subclonal 看成 clonal（E3-13、E3-11） | `prop_truncal_snvs` 預設 0.5（`src/params.rs:91`），放到 trunk（`src/evolution.rs:273`） | 文獻比例是偵測後的值，不能直接比。兩者要分層記錄 | 強（方向），弱（修正幅度只有 5 例） | 單點突變 |
| Subclonal 比例依癌別差很大（E3-13） | 單一參數，沒有癌別概念 | 參數的生物意義未定 | 強 | 單點突變 |
| 邊長和時間在部分癌別有相關（E3-04） | 其餘 SNV 隨機切段分給各邊（`src/evolution.rs:279`），無時間 | 沒有速率也沒有時間 | 中（只有 ccRCC） | 單點突變 |
| 邊長不等於分裂次數（E3-18、E3-07） | 無分裂次數、無存活率 | 邊長只有一個自由度 | 中（依賴模型） | 單點突變 |
| Clone 間速率可能改變；POLE／MMR 爆發（E3-14、E3-03、E3-18） | 各邊沒有 clone 特異速率 | 無 mutator 機制 | 強（存在），中（頻率） | 單點突變 |
| Signature 隨時間改變（E3-03、E3-12） | SNV 沒有座標與 context | 無 signature 真值 | 強（方向） | 單點突變；要先有座標 |
| VAF 低頻長尾（E3-17，爭議） | 所有 clone 都留在 sample（`docs/conipher_steps.md` S7） | 無未取樣的低頻 clone | 弱（解讀有爭議，E3-20） | 單點突變 |
| 用 CN 上的 multiplicity 定時序（E3-03、E3-04） | 每個 position 獨立抽 CNA（`docs/conipher_steps.md` S4–S6） | 無 segment，所以沒有共享的 early／late 訊號 | 強 | CNA 後 |

**真值與觀測（N1）：** 速率、時間、分裂次數、signature 來源都屬真值層。Clonal／subclonal 判定、CCF、偵測漏失都屬觀測層。

**Parent-of-origin：** 本主題的論文都沒有把腫瘤體細胞突變率按父系／母系分開。只有 E3-16 用到父系定相的 de novo 突變，而且是生殖細胞、來自 trio。詳細證據歸主題 08。

## 未解問題

- **腫瘤 long read 的邊長或 truncal 比例：** 在 PubMed、WebSearch，用「HiFi／long-read／duplex／somatic mutation rate」等關鍵字，到 2025 年內沒找到第一手研究。SMaHT 的 duplex 比較 preprint（WEB: https://www.biorxiv.org/content/10.64898/2025.12.12.692823.full.pdf）只看到搜尋摘要，未讀，不當證據。
- **同一腫瘤的直接速率量測：** 現有速率多來自跨病人相關或模型。本次沒讀到以連續取樣直接量同一 clone 速率的研究。
- **SBS1 與 SBS5 的機制分離：** Spisak 2024 PLoS Biol（WebSearch 線索，未讀全文）主張兩者來源不同，待查。
- **只讀到摘要、未列卡片的種子論文：** Jamal-Hanjani 2017、Lee-Six 2019、Martincorena 2018、Tomasetti 2013（E3-10、E3-06、E3-09、E3-19 檔案只有摘要）。其中 Tomasetti 2013 的「半數以上突變在腫瘤起始前」還沒讀全文，對 trunk 的組成很重要。
- **未讀全文的 Abascal 2021：** 只有摘要，需要全文才能引用各組織速率。
- **未查的範圍：** Blokzijl 與 Alexandrov 的組織差異差在哪裡，本次沒有系統比較。
