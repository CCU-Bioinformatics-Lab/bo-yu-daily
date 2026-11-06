# 05 克隆層級的獨立證據（演化路徑與克隆結構）

引文表：[`claims/05.tsv`](claims/05.tsv)（99 列，全部通過引文核對）。

## 結論

能直接觀察演化過程的只有三類資料：CRISPR lineage tracing（小鼠或 xenograft，條碼是真值）、時序單細胞 WGS（細胞株與 PDX，實際看到 clone 比例隨時間變化）、病人單細胞 WGS（樹仍是推論的）。三類都指向同一件事：clone 大小極度偏斜，少數 clone 佔多數細胞，大量 clone 很小或完全失敗，而且 clone 會消失。〔論文〕這和 diplosim 的 Dirichlet(1) 加「所有 clone 都留在 sample」不符。建樹的基本假設 infinite sites 已被單細胞資料直接否證：12 個資料集有 11 個出現同位點重複突變或突變流失，多數流失不落在 LOH 區。〔論文〕bulk deconvolution 對上單細胞 clone 時，clone 數、比例、CN 結構都估不準。〔論文〕爭議點是選擇的普遍性：小鼠 lineage tracing 看到明確的 subclonal 擴張，而人類大腸癌的空間模型在 27 個腫瘤中只有 7 個支持 subclonal selection。證據最弱的是「這些比例能否套到人類病人」：所有 clone 大小與瓶頸的數字都來自小鼠或細胞株。

## 回答主題的五個問題（摘要）

1. **哪些實驗能直接觀察演化過程：** CRISPR lineage tracing（E5-01 小鼠自發腫瘤、E5-02 小鼠原位注射、E5-03 人類細胞株 xenograft）；時序單細胞 WGS 加實體混合驗證（E5-05）；病人單細胞 WGS（E5-04、E5-13、R01）；單一腺體／顯微解剖等級的空間取樣（E5-11）。在本次來源與關鍵字內，沒找到以 single-cell-derived colony 全基因組建腫瘤樹的論文全文（嘗試抓 Roerink 2018、Lee-Six 2019 失敗，見「未解問題」）。
2. **直接觀察到的樹長什麼樣：** 深（細胞層級深度 10–20）、幾乎每個細胞都是唯一 lineage 狀態、少數 clade 擴張、大量私有低頻 lineage；clone 大小跨好幾個數量級；fitness 呈連續分布而非兩群（E5-01、E5-03、E5-05）。
3. **單細胞／真值揭露了哪些 bulk 的錯誤：** infinite sites 違反（E5-06）；bulk CN deconvolution 在 clone 數與比例上失準（E5-04）；bulk 把相似頻率的 subclone 併成一個節點，所以小 clone 消失（E5-04、E5-06 的論述）；同一 clonal SNV 在不同 allele-specific CN 的細胞中 VAF 不同（B03）。
4. **基本假設被違反多少：** infinite sites：12 個資料集中 11 個違反（E5-06）。perfect phylogeny：單細胞 clone 的 SNV 有 16% 不完全符合最佳樹（E5-04）。clone 數：bulk 會低估（E5-04）。sum rule 在本次來源中沒找到直接量測的論文。
5. **哪些結論不能套到病人：** E5-01、E5-02（小鼠）、E5-03（人類細胞株 xenograft）、E5-05（細胞株與 PDX）的所有 clone 大小、瓶頸比例、fitness 係數都是實驗系統的；E5-04 的 bulk 對照是 in-silico 混合，不是真實 bulk。只有 E5-11、E5-13、E5-10、R01 是病人資料。

## 搜尋範圍

- 來源：PubMed／PMC（`fetch_paper.py` 走 E-utilities）、WebSearch。期間 2016–2026。日期 2026-11-05。
- 關鍵字：lineage tracing tumor evolution、CRISPR barcode phylogeny、single-cell DNA clone tree、infinite sites assumption violation、bulk deconvolution versus single-cell ground truth、clone size distribution xenograft、neutral evolution critique。
- 已收錄不重抓：R01（McPherson 2016 HGSOC 單核真值樹）、B03（Funnell 2022 SIGNALS）、M01（PhyClone）。本篇引用它們既有 ID 與 `summary.md`。
- 排除清單內的論文沒有收（清單見 `summary.md`「搜尋方法」）。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| Infinite sites：每個位點一生只突變一次，且不會流失 | 任何 clone 的 SNV 集合滿足 perfect phylogeny | — | E5-06（12 個單細胞資料集中 11 個違反；7 例流失、4 例平行突變） | 人類多癌別單細胞 panel／exome | 爭議（原假設被否證，但量級依癌別與偵測力而定） |
| 突變流失主要來自 LOH／大片段缺失 | 流失位點應落在缺失區 | R01（HGSOC 真值樹用 infinite sites with loss，並用 CN 佐證） | E5-06（5 個流失位點都不在該病人 LOH 區） | 白血病 panel、卵巢癌 panel | 爭議 |
| 腫瘤由少數擴張 subclone 主導（selection） | 樹上有少數大 clade、其餘為小的私有 lineage | E5-01（腫瘤通常 1–2 個擴張 subclone）、E5-02（轉移部位 80–90% 細胞來自單一 clone） | E5-01 本身也看到部分腫瘤無正選擇證據 | 小鼠 KP 肺腺癌、小鼠 PDAC、A549 xenograft | 爭議（體內模型內部就不一致） |
| clone 大小近似對稱分布（如 Dirichlet(1)） | 各 clone 比例同數量級 | 在本次來源與關鍵字內沒找到支持 | E5-02、E5-03（極度偏斜，多數 clone 很小或失敗） | 實驗性模型 | 證據不足／反向 |
| clone 是穩定的離散單位 | 同一 clone 的組成隨時間不變 | — | E5-05（clone 從 20% 歸零、另一個漲到 69%）、E5-09（單細胞衍生 clone 數月後 13% SNV 不共有） | 細胞株、PDX | 反向（體外與 PDX 證據） |
| clone 的 ploidy 在腫瘤內一致 | 一個腫瘤一個 ploidy | — | E5-13（41 名病人中 40 名共存多種 WGD 倍數） | HGSOC 病人 | 共識偏反對（屬 CNA 階段） |
| 樹的邊長與時間（突變數）成正比 | 可用分子鐘定事件時序 | E5-13（以 CpG C>T 當分子鐘定 WGD 時序）、E5-10（molecular clock 定 CNA 時序） | — | HGSOC、大腸癌 | 共識（方法層） |
| bulk deconvolution 能回復真實 clone 結構 | clone 數與比例接近單細胞真值 | — | E5-04（in-silico 混合中 bulk 在 clone 比例、clone 數、CN 結構都差） | 卵巢癌細胞株 CN clone | 共識偏反對（限 CN 層） |
| 轉移源自原發腫瘤內的擴張 subclone（晚期播種） | 轉移與特定擴張 clade 在樹上最近 | E5-01、E5-02、E5-03 | 人類病人的早期播種文獻（本篇未收） | 小鼠與 xenograft | 爭議（模型證據一致，人類未驗） |

## 論文卡片

### E5-01 Yang 2022, Cell — 10.1016/j.cell.2022.04.015

- **資料：** 小鼠 Kras;Trp53（KP）肺腺癌，29 個原發腫瘤（分析用 21 個）；CRISPR lineage tracing + scRNA-seq；short read（10x）；多區域（部分腫瘤含轉移家族）；真值來源：合成 Cas9 indel 條碼（lineage 真值，非基因體突變）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（Cassiopeia；以 Neighbor Joining 交叉驗證）。
- **觀點：** 作者認為腫瘤演化是階層式的，由罕見但高 fitness 的 subclone 推動；可塑性先升高，之後出現 clonal sweep。
- **演化假設：** 用「中性模型下的 subclone 預期大小」當虛無假設來偵測選擇；fitness 推論假設小效應突變累積。
- **真實結論：** 代表性腫瘤 772 個細胞，樹中位深度 12、最大 15。29 個原發腫瘤取 21 個高品質者分析。同一批腫瘤中既有看似中性者，也有明確正選擇者。腫瘤通常只有 1 或 2 個擴張 subclone，擴張細胞比例分布很寬。換 Neighbor Joining 得到一致的擴張比例（相關 0.87）。21 個腫瘤中 20 個的 subclonal CNV 關係與 Cas9 樹顯著相似。轉移一致源自擴張 subclone。（Results「Rare subclones expand…」節、Discussion 第 1–2 段）
- **限制與反證：** 小鼠 GEMM 的突變負荷低，所以必須用合成條碼，不能用天然 SNV 當 lineage marker；這表示它的樹不是 SNV 樹，拿來校正 SNV 模型要小心。作者自承無法定出狀態轉換方向，也無法排除未觀察到的中間態。fitness 模型假設小效應突變。
- **支持哪一層（N3）：** 演化路徑（最強）、克隆結構。
- **對 diplosim 的意義〔推論〕：** 對應 `src/topology.rs:57-109`（隨機二分 + 隨機剪葉）與 clone 比例 Dirichlet(1)。真實（小鼠）腫瘤的樹深可達 12–15 層，且只有少數 clade 擴張；diplosim 沒有「擴張 clone」這個概念，也沒有時間。屬真值層的差距。

### E5-02 Simeonov 2021, Cancer Cell — 10.1016/j.ccell.2021.05.005

- **資料：** 小鼠 KPCY 胰腺癌（PDAC）細胞株、原位注射 2 隻小鼠；macsGESTALT CRISPR 條碼 + scRNA-seq；short read；多部位（原發 + 轉移）；真值來源：靜態條碼（clone 身分）+ 可編輯條碼（subclone）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（自建 macsGESTALT pipeline 的階層分群與 phylogeny 重建）。
- **觀點：** 轉移能力集中在罕見的 late-hybrid EMT 狀態，並受到強烈選擇。
- **演化假設：** clone 的轉移成敗由可遺傳的轉錄狀態決定，而非新的驅動突變。
- **真實結論：** 回收約 380,000 個 target site、約 28,000 個細胞。兩隻小鼠共 95 個 clone。注入的 clone 不到 1% 成功移植。原發腫瘤中 >50% 細胞來自少數 clone（M1 兩個、M2 六個）。轉移部位 80%–90% 細胞通常來自單一 clone。48/95（51%）clone 完全沒有轉移。同批細胞在體外幾乎都能長成群落。（Results「Aggressive clones are rare…」節）
- **限制與反證：** 細胞株注入模型，不是自發腫瘤；只有 2 隻小鼠；條碼在 scRNA-seq 的回收率 77%–89%，未回收者可能偏向低表現細胞。體內外差異說明這些比例是模型與環境特有的，不能當人類病人參數。
- **支持哪一層（N3）：** 克隆結構（clone 大小分布）、演化路徑（轉移）。
- **對 diplosim 的意義〔推論〕：** 直接對應「clone 比例 Dirichlet(1)、所有 clone 都留在 sample」（`docs/conipher_steps.md` S7）。真實觀察是極度偏斜加上大量失敗 clone。差距在真值層的 clone 比例模型。

### E5-03 Quinn 2021, Science — 10.1126/science.abc1944

- **資料：** 人類 A549 肺腺癌細胞株、原位 xenograft，4 隻小鼠（主分析 M5k）；Cas9 lineage tracer + scRNA-seq；short read；多組織（6 個部位）；真值來源：intBC 靜態條碼 + 演化中的 indel。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（Cassiopeia；Neighbor Joining 對照）。
- **觀點：** 轉移能力有可遺傳、植入前就存在的異質性，不需要新突變。
- **演化假設：** 用 Fitch-Hartigan 最大簡約推祖先組織位置，把轉移當樹上的狀態轉換。
- **真實結論：** 植入 5,000 個細胞估計含 2,150 個可分辨 clone，但只有約 100 個成功移植並增生；97.7% 細胞可指派到這 100 個 clonal population。植入前與犧牲後的 clone 大小幾乎不相關。代表性 clone 5,616 個細胞、99.0% 細胞 lineage 狀態唯一，平均樹深 10.0、最大 20。17 個 clone（7.3% 細胞）記錄品質不足被排除。clone 的轉移率涵蓋從不轉移到高度轉移的連續分布。（Results 第 2–5 段）
- **限制與反證：** 作者自承只用單一轉移模型；A549 是長期培養的細胞株，核型與病人腫瘤不同；排除低品質 clone 會偏向記錄效率高者。
- **支持哪一層（N3）：** 克隆結構、演化路徑。
- **對 diplosim 的意義〔推論〕：** 兩點。一、clone 的「存活瓶頸」是真實現象（2,150 → 100），diplosim 的隨機剪葉沒有族群動態的意義。二、真實樹幾乎每個細胞都是唯一 lineage 狀態，而 bulk 模型只處理少數 clone，兩者是不同解析度；這支持「bulk 的 clone 數是觀測層的產物」。

### E5-04 Laks 2019, Cell — 10.1016/j.cell.2019.10.026

- **資料：** 細胞株、乳癌 PDX、卵巢癌細胞株（同一病人的 1 個原發 + 2 個復發）、follicular lymphoma、乳癌 FNA；DLP+ 單細胞 WGS，共 51,926 個基因體；short read；真值來源：單細胞 CN clone 與 clone 專屬 SNV／breakpoint。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（CN 分群 + 最大似然 SNV 樹、階層分群、breakpoint 樹；對照 ReMixT、THetA2、CloneHD）。
- **觀點：** 單細胞可取代繁瑣且易錯的 bulk deconvolution。
- **演化假設：** 共享 CN profile 的細胞可當同一 clone；clone 層級的 SNV 與 breakpoint 應符合同一棵樹。
- **真實結論：** 卵巢癌 9 個 clone，每 clone 62–145 個細胞，中位覆蓋 15x。14,068 個 SNV 中 84% 完全符合推得的樹；28% 祖先、9% clone 專屬、63% clade 專屬。538 個 breakpoint 中 88% 完全符合，且 breakpoint 樹與 SNV 樹拓樸完全相同。in-silico 混合測試中 bulk deconvolution 在 clone 比例、clone 數、CN 結構三項都差。由 germline 多型位點推 haplotype block，92%–94% 的 bin 有高品質 allele 量測。未轉型二倍體細胞中 <5% 帶整條染色體分離錯誤。（Results「Ascertainment of Clone Specific…」節）
- **限制與反證：** 「真值」是細胞株與 PDX，不是病人原位組織；bulk 對照是 in-silico 混合，不是真實 bulk 定序，所以是方法上限而非實際臨床比較。16% 的 SNV 不符合樹，作者沒有拆解原因（可能是 dropout、ISA 違反或分群誤差）。
- **支持哪一層（N3）：** 克隆結構（最強）；對 bulk 方法的誤差只支持 CN 層。
- **對 diplosim 的意義〔推論〕：** 兩件事。一、這批細胞株與 PDX 的 clone 有 84% SNV 完全符合最佳樹，其餘 16%（100% − 84%，主文沒有拆解原因，可能含偵測雜訊）不完全符合。diplosim 預設的真值沒有不符合的 SNV：每邊 ≥1 個 SNV（`src/evolution.rs:273`），`prop_mutloss_positions` 預設 0（`src/params.rs:99`），也沒有同位點重複。所以預設模擬的資料比真實資料「乾淨」。（2026-11-05 主 agent 核對程式後修正：原文寫「無流失」，實際是預設關閉。）二、haplotype block 的 allele A／B 是 phasing 標籤，不是父母來源（父母方向只能靠 germline 與參考 panel），屬觀測層，不屬真值層。

### E5-06 Kuipers 2017, Genome Research — 10.1101/gr.220707.117

- **資料：** 重新分析 12 個已發表的單細胞腫瘤資料集（3 個 exome、9 個 targeted panel），涵蓋 MPN、腎細胞癌、ER+ 乳癌、6 名兒童 ALL、3 個卵巢癌樣本；single-cell；short read；真值來源：無（以 Bayes factor 做模型比較）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（自建 infinite sites／finite sites 突變樹模型，含 doublet 與 dropout）。
- **觀點：** infinite sites 不能當通用假設，需要更複雜的模型。
- **演化假設：** 比較「每位點最多一次事件」與「允許一次重複事件」兩個模型。
- **真實結論：** 12 個資料集中 11 個有強證據支持同位點被多次影響。7 例是早期突變流失，其中 5 例位點沒有大片段缺失。4 例是 parallel mutation。白血病 panel 的 BF 在 10^5–10^15（一例 330）。三名病人流失的突變正是樹中最早發生的那一個。16 個 bulk LOH 事件有 13 個是祖先、出現在所有 clone；5 個流失突變都不落在 LOH 區。卵巢癌 panel 為 43 或 84 個突變、420–672 個細胞。檢定特異度 90%–95%；每突變 2–3 個細胞時靈敏度只有 50%–60%。（Results 全節、Discussion 第 1–3 段）
- **限制與反證：** 只是模型比較，沒有獨立真值；doublet 在某些平台高達 40%，作者以模型吸收但未獨立驗證；小規模 deletion 無法與真正的 back mutation 區分；panel 位點是依 bulk 選的，有取樣偏差。先驗機率的估計假設突變均勻分布、無選擇、全部被觀察到。
- **支持哪一層（N3）：** 克隆結構與演化路徑（針對建樹假設本身）。
- **對 diplosim 的意義〔推論〕：** diplosim 預設沒有突變流失（`prop_mutloss_positions` 預設 0，`src/params.rs:99`；可手動開啟，但比例直接設定，和 segment 無關），也沒有同位點重複；SNV 也沒有基因組座標，所以連「同位點」這個概念都不存在。若要測 HP 資訊對建樹的幫助，而真實資料有流失與平行突變，模擬器就少了這個難度來源。屬真值層。

### E5-05 Salehi 2021, Nature — 10.1038/s41586-021-03648-3

- **資料：** 184-hTERT 乳腺上皮細胞株（p53 野生與兩條 isogenic p53 缺失分支）、1 個 HER2+ 與 3 個 TNBC 病人衍生 xenograft（PDX）系列；時序單細胞 WGS（DLP+），分析保留 42,000 個基因體、113 個 library；short read；真值來源：時序上實際觀察到的 clone 比例變化，以及實體混合再移植的驗證實驗。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（sitka 單細胞 phylogeny；fitClone 的 Wright-Fisher diffusion fitness 模型）。
- **觀點：** 以 CNA genotype 定義的 clone，其 fitness 可量化並預測後續擴張。
- **演化假設：** clone 的 CNA genotype（或與其連動的遺傳因子）決定 fitness；族群依 Wright-Fisher 擴散演化。
- **真實結論：** 四個 PDX 系列分別追蹤 927、619、381、353 天。TNBC-SA1035 偵測到 11 個 clone；參考 Clone A 起始佔 20%，最後時間點已偵測不到；Clone E 從極低比例擴張到 X8 代的 69%。p53 缺失的 aneuploid clone 擴張顯著較快，二倍體細胞快速消失。每細胞 CN breakpoint 數隨 fitness 升高，但點突變率相對穩定。停藥實驗中 clone 組成可回復為前驅 Clone B 佔 90%。（Results 各節）
- **限制與反證：** PDX 與細胞株，不是病人原位腫瘤；clone 以 CNA 定義，SNV 只是附帶；作者自承 SNV、SV、罕見 CNA 會另外影響 fitness 但未納入模型；覆蓋只有 0.022x，單細胞層級看不到 SNV。
- **支持哪一層（N3）：** 演化路徑（時序 clone 動態，證據等級最高的一類）、克隆結構。
- **對 diplosim 的意義〔推論〕：** 最直接的一點是「clone 會消失」。真實時序中一個起始佔 20% 的 clone 可以歸零，另一個可以從極低比例漲到 69%。diplosim 的 Dirichlet(1) 是一次抽樣，沒有時間軸，也不會讓 clone 消失。屬真值層。

### E5-10 Cross 2018, Nature Ecology & Evolution — 10.1038/s41559-018-0642-z

- **資料：** 24 個大腸腺瘤與癌（含 MSS、MSI）；多區域 bulk WGS／WES；short read；多區域；真值來源：無（多區域推論）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（多區域系統發生樹、molecular clock、CNA 時序分析）。
- **觀點：** 腺瘤佔較寬的 fitness peak，癌則接近單一最佳解（近三倍體）。
- **演化假設：** 腺瘤到癌是 selective sweep 加遺傳瓶頸；CNA 的累積不是均勻的。
- **真實結論：** 腺瘤的 SNA 有中位 56% 是 sub-clonal，MSS 癌顯著較低（45%，p=0.04）。所有癌中生理距離與系統發生距離強相關（R²=0.81–0.93）。每個腫瘤的每個區域都至少帶一個 CNA（含 cnLOH）。MSS 癌的樹幹比分支長，腺瘤相反。癌的 sub-clonal CNA 比共有 CNA 小（p<0.001）；腺瘤無此差異。三個癌的 CNA 時序集中在 MRCA 之前，呈 punctuated 模式。（Results 各節）
- **限制與反證：** bulk 多區域，不是單細胞；「sub-clonal」的定義是「不是所有取樣區域都偵測到」，所以完全受取樣與偵測極限影響；24 個腫瘤、每個區域數不多。
- **支持哪一層（N3）：** 克隆結構（trunk／branch 比例），部分支持演化路徑。
- **對 diplosim 的意義〔推論〕：** diplosim 的 `prop_truncal_snvs` 預設 0.5。這篇是真實腫瘤裡 trunk 比例有量測的少數來源之一（癌 55%、腺瘤 44% 的 SNA 屬 trunk，依其 sub-clonal 比例換算），而且癌與腺瘤明顯不同。但它是 short read bulk，依研究規則 只能當生物假說，不能當 diplosim 的預設值來源。
- **parent-of-origin 相關：** 無。本篇用 total CN 與 cnLOH，不分父母來源。

### E5-11 Househam 2022, Nature — 10.1038/s41586-022-05311-x

- **資料：** 27 個原發大腸癌、297 個 single-gland／crypt 樣本（每腫瘤平均 11 個，範圍 1–38）；單一腺體的 deep WGS（中位 35x）＋ low-pass WGS ＋ RNA-seq ＋ ATAC-seq；short read；空間取樣（等同顯微解剖層級的小 clonal unit）；真值來源：無（以 ABC 模型選擇）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（多樣本系統發生樹；空間 agent-based 模型 + ABC-SMC 做模型選擇）。
- **觀點：** CRC 的表型異質性大多不是遺傳造成的；subclonal selection 只在少數腫瘤中可偵測。
- **演化假設：** 比較「中性 subclonal 生長」與「有選擇的 subclone」兩類空間模型，用 AIC 選擇。
- **真實結論：** 27 個腫瘤中 7 個有 subclonal selection 的強證據（ΔAIC > 4），其中 4 個在被選 clade 內找到有表現的 driver；其餘 15 個最佳模型是中性。被選 subclone 的生長速率推估最高是背景 clone 的 20 倍，且多半在腫瘤還小於 50,000 個細胞時就出現。分支長度相近的平衡樹常見。38 個 subclonal driver 候選中有 14 個（37%）是良性或未表現。3,705 個可測 subclonal 突變只有 2.4% 影響 cis 表現。（Results「evolutionary dynamics」與「spatial modelling」節）
- **限制與反證：** 模型選擇不是真值；每腫瘤樣本數差異很大（1–38）；only CRC；選擇訊號依賴空間模型的假設（推擠寬度、突變率等）。作者自己也說 dN/dS 在被判中性的腫瘤中約為 1，這是內部一致性而非外部驗證。
- **支持哪一層（N3）：** 演化路徑（選擇的有無與強度）、克隆結構（樹形平衡度）。
- **對 diplosim 的意義〔推論〕：** 三點。一、真實 CRC 多數呈「有效中性」，所以 diplosim 不加選擇未必錯，但它的樹形分布是演算法產物，不是中性模型的結果，兩者不同。二、有選擇時，選擇強度大（最高 20 倍）且發生得早（< 50,000 細胞），對應到樹上就是「一個大 clade 很早分出來」。三、single-gland 取樣是把 bulk 的混合度降到最低的做法，提醒我們 clone 比例同時取決於空間取樣，diplosim 現在沒有空間。屬真值層。

### E5-13 McPherson 2025, Nature — 10.1038/s41586-025-09240-3

- **資料：** 41 名未治療 HGSOC 病人、70 個多部位樣本；單細胞 WGS（DLP+），共 100,054 個單細胞基因體（30,260 個腫瘤基因體），中位覆蓋深度 0.060；另有 scRNA-seq 與多重免疫螢光；short read；真值來源：單細胞 CN 與 clone 專屬 SNV（以 doubleTime 推時序）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（doubleTime：用 SNV 推 clone 分歧與 WGD 時序；單細胞 phylogeny）。
- **觀點：** WGD 不是一次性事件，而是持續進行的過程，會提高 CIN 並抑制 interferon 訊號。
- **演化假設：** 以年齡相關的 CpG C>T 突變當分子鐘，分支長度等於突變數；WGD 可在不同 clone 中重複發生。
- **真實結論：** 41 名病人中 40 名體內同時存在不同 WGD 倍數的細胞；比主族群多一次 WGD 的細胞在 37/41 名病人中被偵測到；全 cohort 有 4% 的腫瘤細胞屬於這類。WGD 多半早發生，但有晚期事件的長尾。truncal WGD clone 的改變顯著多於 subclonal WGD clone，整染色體與臂的流失多三倍。細胞間 CN 距離隨 WGD 倍數上升。（Results「Ongoing WGD」至「Evolvability of WGD clones」）
- **限制與反證：** 覆蓋極低（0.060），單細胞層級無法直接看 SNV，SNV 是 clone 層級聚合後才算；只有 HGSOC；clone 定義以 CN 為主。
- **支持哪一層（N3）：** 克隆結構、演化路徑（WGD 時序）。
- **對 diplosim 的意義〔推論〕：** 兩點。一、真值裡「同一腫瘤共存多種 ploidy」是常態（40/41），不是例外；這屬於 N4 的 CNA／多倍體階段，現在不做，但要記錄。二、它的分支長度是突變數，與時間掛鉤；diplosim 的邊長與時間無關（`src/evolution.rs:273` 隨機切段），這是真值層的結構差距。
- **parent-of-origin 相關：** 有 cnLOH 與 allele 層級分析，但不區分父系／母系；本篇沒有 trio 或 imprinting 資訊。

### E5-09 Ben-David 2018, Nature — 10.1038/s41586-018-0409-3

- **資料：** 106 個細胞株的 WES 跨實驗室比較；27 個 MCF7「strain」的完整基因體刻畫；3 個野生型與 5 個帶中性修飾的單細胞衍生 clone；條碼實驗（五種培養條件、各五重複）；26,465 個細胞的 scRNA-seq；short read；真值來源：單細胞衍生 clone 的已知起點與時序取樣。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（階層分群建 strain 樹；PyClone 做 subclonal 重建）。
- **觀點：** 細胞株不是 clonal 也不是穩定的；培養中的 clonal 動態會改變藥物反應。
- **演化假設：** 若 clonal 動態是隨機的，獨立重複會長出不同條碼族群；若是既存 subclone 被選擇，重複之間會一致。
- **真實結論：** 106 個細胞株有廣泛 clonal 多樣性。27 個 MCF7 strain 兩兩比較中，10 條染色體臂（基因體 25%）有增減差異。95 個編碼區 SNV／indel 只有 35% 為所有 strain 共有，29% 只出現在單一 strain。27 個 strain 都帶同一 PIK3CA 突變，但 AF 從 0.21 到 0.70。45% 的突變被判為 subclonal。同一母族群衍生的單細胞 clone 之間突變圖譜就不同；培養 8–14 個月後，中位 13%（8%–16%）的非沉默 SNV 在時間點間不共有。（Results 各節）
- **限制與反證：** 全是體外細胞株，與病人腫瘤的選擇壓力不同；「subclonal」的判定依賴 AF 與 CN，受 purity 與 CN 誤差影響；MCF7 是單一細胞株。
- **支持哪一層（N3）：** 克隆結構（單細胞衍生 clone 的再分化速度）、演化路徑（體外選擇）。
- **對 diplosim 的意義〔推論〕：** 它給出「從單一細胞出發，多久會再長出可測的 subclonal 結構」的量級（數月、約 13% 的 SNV 不共有）。這支持「clone 不是離散穩定單位」。但它是體外系統，依研究規則的規則不能當 diplosim 的預設值。

## 已收錄論文的交叉引用

- **R01（McPherson 2016, Nat Genet）**：病人層級單核定序建的 clone tree，是 PhyClone HGSOC 真值樹來源。它的模型是 infinite sites **with loss**，而且明確寫出「祖先 SNV 在後代流失」與「SNV 起源於兄弟節點」在 CN-naive 模型下無法區分。真值只有 3 名病人、每人 47–95 個可用位點，且位點是依 bulk 推論挑的，所以真值天生偏向 bulk 看得到的結構。〔repo〕`research/literature/papers/R01_mcpherson_hgsoc_2016/summary.md`
- **B03（Funnell 2022, Nature）**：scDNA + haplotype-specific CN。樹來自 total-CN breakpoints，long read（ONT）只驗證特定 SV。它示範同一 clonal SNV 在 `2|1` 與 `1|2` 細胞中的 VAF 不同，混成 bulk 後 VAF 不再唯一對應 CN 狀態。〔repo〕`research/literature/papers/B03_singlecell_mutational_processes_2022/summary.md`
- **M01（PhyClone 2025）**：mutation loss 用 outlier 吸收，不在樹上明確建模；HGSOC patient 3 示範可移除兩個 lost cluster。這說明現行 bulk 方法處理 ISA 違反的方式是「丟掉」，不是「建模」。〔repo〕`research/literature/papers/M01_phyclone_2025/summary.md`

## 對 diplosim 的差距（照優先順序）

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| clone 大小極度偏斜；多數 clone 很小或根本沒長起來 | clone 比例 Dirichlet(1)，所有 clone 都留在 sample（`docs/conipher_steps.md` S7） | 沒有族群瓶頸、沒有失敗 clone、沒有大小偏斜 | 強（E5-02、E5-03，但都是模型系統） | 單點突變 |
| SNV 會流失、同位點會重複突變，真值不滿足 perfect phylogeny | 每邊 ≥1 個 SNV（`src/evolution.rs:273`）；流失預設關閉（`src/params.rs:99`）；無重複 | 預設真值過於乾淨，建樹難度可能被低估 | 強（E5-06；R01 的 loss 真值） | 單點突變 |
| 真值樹有深層 lineage（深度 10–15）與少數擴張 clade | 隨機遞迴二分 + 隨機剪葉（`src/topology.rs:57-109`） | 沒有時間、沒有擴張／選擇，拓樸分布無生物依據 | 中（E5-01、E5-03，皆為小鼠／xenograft） | 單點突變 |
| SNV 有基因組座標，才談得上同位點重複、LOH 交互作用 | 每個 SNV 是獨立 locus，無座標 | 無法表示 ISA 違反與 LOH 的關係 | 強（E5-06） | CNA 後 |
| haplotype 的 allele A／B 只是 phasing 標籤，不是父母來源 | `src/hp.rs:30` 的 Bernoulli(0.5) 只給 A／B | 真值層缺 parent-of-origin 標籤；觀測層不應假設 HP1 = 父 | 中（E5-04 的 haplotype block 由 germline panel 推） | 單點突變 |

## 讀長與證據等級一覽

| ID | 系統 | 讀長 | 真值強度 |
|---|---|---|---|
| E5-01 | 小鼠 KP 肺腺癌（自發） | short read | 合成條碼真值（lineage 真值，非 SNV） |
| E5-02 | 小鼠 PDAC 原位注射 | short read | 合成條碼真值 |
| E5-03 | 人類 A549 xenograft | short read | 合成條碼真值 |
| E5-04 | 細胞株、PDX、病人樣本 | short read（ONT 無） | 單細胞 CN clone；bulk 對照是 in-silico 混合 |
| E5-05 | 細胞株、TNBC PDX 時序 | short read | 時序觀測 + 實體混合再移植驗證 |
| E5-06 | 12 個已發表單細胞資料集 | short read | 無真值（Bayes factor 模型比較） |
| E5-09 | MCF7 細胞株與單細胞衍生 clone | short read | 已知起點 + 時序取樣 |
| E5-10 | 24 個大腸腫瘤多區域 bulk | short read | 無真值 |
| E5-11 | 27 個大腸癌 single-gland | short read | 無真值（ABC 模型選擇） |
| E5-13 | 41 名 HGSOC 病人 scWGS | short read | 單細胞 CN clone + SNV 時序 |

全部為 short read。依研究規則（輸入與驗證參考只用 long read），這些只能當生物假說與機制證據，不能當 diplosim 的驗證目標或預設參數。

## parent-of-origin（雙倍體的爸爸和媽媽）

本主題碰到的相關證據只有兩處，都屬觀測層：

- E5-04：allele-specific CN 用 germline 多型位點推 haplotype block，再配 1000 Genomes 參考 panel。所以 allele A／B 是統計 phasing 的結果，不是父母來源。〔論文〕
- B03（已收錄）：haplotype-specific CN 能區分保留哪一條 homolog，但標籤仍是 A／B。〔repo〕

在本次來源與關鍵字內，沒找到用 trio、imprinting 甲基化或 Strand-seq 把腫瘤 clone 的 haplotype 標成父系／母系的論文。這個方向屬主題 08。

## 未解問題

1. 在本次來源（PubMed／PMC、WebSearch，2026-11-05）與上列關鍵字內，沒找到「同一位病人同時做 bulk 與單細胞，並量化 bulk 重建漏掉多少 clone」的獨立 cohort 研究。找到的都是方法論文自己的比較，或 in-silico 混合（E5-04）。
2. CRISPR lineage tracing 的 clone 大小分布能否外推到人類病人，沒有證據。所有數字都來自小鼠或 xenograft。
3. 突變流失中「真正 back mutation」與「小片段 deletion」的比例未知。E5-06 只能排除大片段 LOH。
4. sum rule（子 clone 的 CCF 之和不超過親 clone）在真實資料中被違反多少，本次沒找到直接量測的論文。
5. 未取得全文的線索（NCBI E-utilities 在 2026-11-05 多次回 500／搜尋無結果）：Roerink 2018 Nature（大腸癌單細胞衍生 organoid）、Lee-Six 2019 Nature（正常大腸上皮 crypt）。Europe PMC 標為非開放取用（2026-11-05 查詢），本筆記不引用它們的數字。
6. 主 agent 2026-11-05 補查：Minussi 2021 已在主題 01（E1-12）、主題 02（E2-16）讀過全文，不是缺口。Heide 2022（`10.1038/s41586-022-05202-1`，PMC9684080）已抓全文，內容是大腸癌基因組與染色質的共同演化，對單點突變階段不是核心，未列卡片。
