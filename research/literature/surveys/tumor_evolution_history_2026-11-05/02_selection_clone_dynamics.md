# 選擇壓力、driver／passenger 與 clone 動態

> 所有數字的引文定位在機器核對表 [`claims/02.tsv`](claims/02.tsv)。下面每個數字都對得到該表一列。
> 本筆記的論文全是 short read 或 short read 為底的 single-cell。它們只當生物假說與機制的證據，不是 diplosim 的驗證目標或校正數字。

## 結論

- **共識：** 在 coding SNV 層級，passenger 佔絕大多數，全基因 dN/dS 接近 1。平均每個腫瘤約 4 個 coding driver，癌別間 1–10（E2-01）。常見 driver 偏早、偏 clonal；晚期與 subclonal driver 的基因更分散（E2-04、E2-06）。
- **爭議一：負選擇有多少。** E2-01 估計不到 1 個 coding 突變被移除。E2-27、E2-09 主張訊號被低估或被混合抵消。E2-17 主張表面的 neoantigen depletion 大多可由 mutational signature 解釋。
- **爭議二：subclone 是選擇還是中性。** 同一批 PCAWG 資料得到相反解讀：E2-03 認為選擇普遍，E1-09 只在 3% 高功效二倍體案例找到持續 subclonal 選擇。兩者的差距與深度、clone 定義直接相關。
- **證據不足：** clonal sweep 的頻率在實體腫瘤沒有直接量測，目前只有模型預測（E2-25）和間接推論（E1-05）。clone 比例的分布也沒有找到直接量測：本批論文報 clone 數，不報每個 clone 比例的分布，所以無法判定 Dirichlet(1) 對或錯。
- **直接的 clone 消失證據** 來自 PDX 時間序列（E2-26）與血液腫瘤治療前後（E2-15）。這些是機制證據，不是未治療實體腫瘤的觀察。
- **與主軸的關係〔推論〕：** SNV 接近中性，不等於 clone 結構是隨機的。diplosim 不對 passenger 施加選擇，這點和資料相容。差距在 clone 結構層：沒有 clone 內的中性尾巴，所有 clone 都留在樣本裡，邊長和時間無關。

## 搜尋範圍

- **來源：** PubMed／PMC（`fetch_paper.py`）、WebSearch、任務書種子清單。
- **關鍵字：** clonal sweep frequency、subclone proportion distribution、detection limit、critique／reanalysis dN/dS、not neutral、clone size single-cell、longitudinal clone extinction、negative frequency dependent、clonal interference。
- **期間：** 2010–2026。搜尋日期：2026-11-05。
- **讀取方式：** 15 篇都是 PMC 全文，但我用關鍵字定位後讀相關段落，沒有逐字讀完。補充表格和多數圖沒有讀（硬碟限制與格式）。E2-13 全文很短，已讀完。
- **種子沒讀到：** Bailey 2018、Bozic 2010、Vogelstein 2013、Rosenthal 2019、Salichos 2020、Weghorn & Sunyaev 2017。NCBI 回應 HTTP 500，Europe PMC 回應 503。這些論文的內容本筆記不引用。
- **備用工具：** Europe PMC 備用腳本全部失敗，沒有產生任何本筆記使用的檔案。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| H1 多數 coding 突變是中性 passenger | 全基因 dN/dS ≈ 1 | E2-01；E2-27 的全基因值也接近 1 | E2-27、E2-09 認為負選擇被低估 | 泛癌、cohort 層級；只含 coding SNV | 共識（非 coding 未驗證） |
| H2 負選擇在癌症中很弱 | 很少基因 dN/dS < 1 | E2-01；E2-17 | E2-27（25 個負選擇基因）；E2-09；E2-08 的部分群體 | 依免疫狀態、CN 狀態、基因必需性而變 | 爭議 |
| H3 driver 先早後晚，晚期更分散 | clonal driver 基因集中，subclonal 分散 | E2-04、E2-06、E2-03 | 例外：KIRC（E2-06）；部分基因依癌別而變（E2-03） | 泛癌；單樣本 clonal 判定有「假 clonal」 | 共識（趨勢），個案差異大 |
| H4 subclonal 擴張由選擇推動 | subclonal dN/dS > 1；subclone 帶 driver | E2-03 的 dN/dS；E2-14；E2-26 | 只有 11% subclone 帶已知 driver（E2-03）；E1-09 的 3% | 癌別差異大；深度決定結論 | 爭議 |
| H5 中性演化（Williams 2016）：選擇在生長前結束 | VAF 呈 1/f power law | E2-12；E1-09 的 neutral tail | E2-13：R² 門檻判別力接近隨機；判為中性者仍有 subclonal dN/dS > 1 | 只能當 VAF 形狀的描述 | 方法已被反駁，「部分腫瘤有效中性」仍爭議 |
| H6 負選擇使 SFS 看起來更中性 | 強免疫選擇下 VAF 仍呈 1/f | E2-08（模型） | 資料難以直接驗證：單腫瘤 VAF 無足夠功效 | 免疫原性高的癌別 | 證據不足（模型為主） |
| H7 sweep 只在早期發生 | 晚期 driver 局部增多但不固定 | E2-25（模型）；E2-03 的不完全 sweep 敘述 | E2-15（血液腫瘤轉化期有 sweep）；E1-05 的多 clonal driver 亞型 | 實體腫瘤、空間擴張；模型給上限 | 證據不足 |
| H8 分支比線性常見 | sibling 多於 parent-child | E2-03 同 read 定相；TRACERx odds（引自 E2-03） | 功效有限，只限 haploid 區且 SNV 對少 | 泛癌單樣本、多區域 | 大致共識（少量資料） |
| H9 治療反轉 fitness 排序 | 抗藥 clone 來自未治療時的低 fitness 譜系 | E2-26（PDX）；E2-15（FLT3 抑制劑，3 人） | 停藥回復不一定持續（E2-26 不同時間點） | 治療後；TNBC PDX、AML | 機制有直接證據，泛化性未定 |

## 論文卡片

### E2-01 Martincorena 2017, Cell — 10.1016/j.cell.2017.09.042
- **資料：** 7,664 腫瘤、29 癌別（TCGA）；bulk exome；short read；單區域；無真值。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** 整體接近中性；正選擇多於負選擇。兩套以上拷貝可能緩衝了負選擇。
- **演化假設：** 用 192 參數的突變模型後，dN/dS 能當選擇的量尺。
- **真實結論：** 全基因 dN/dS 接近但略高於 1（Results「Universal」段）。每腫瘤約損失 0.55 個 coding 突變（CI 0.31–1.16）。約 2.2% 基因 dN/dS ≥ 1.5，約 0.14% 基因 dN/dS ≤ 0.75。driver 以外約 99% coding 突變中性累積。平均約 4 個 coding driver，癌別間 1–10，約一半在未知基因。分析限 <500 coding 突變的樣本（佔 92%）。頭頸癌只有 5.0% 非同義突變是 driver。CN=1 區的必需基因 nonsense dN/dS = 0.66。
- **限制與反證：** 個別病人可能遠離癌別平均。cohort 平均會把不同腫瘤混在一起（反證見 E2-09）。基因層級功效有限；作者只說負選擇弱於偵測極限。只含 coding。
- **支持哪一層（N3）：** 演化路徑（選擇強度），cohort 層級。不支持單一腫瘤的克隆結構。
- **對 diplosim 的意義〔推論〕：** diplosim 不模擬選擇。對 passenger 來說，這和 H1 相容。屬真值層。缺的不是 passenger 上的選擇，而是 driver 與 clone 擴張的連結。

### E2-27 Zapata 2018, Genome Biology — 10.1186/s13059-018-1434-0
- **資料：** 7546 exome、26 癌別（TCGA）；bulk；short read；單區域。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** 負選擇存在但被低估。
- **演化假設：** 校正 somatic 取代偏差後，dN/dS 可以找到負選擇基因。
- **真實結論：** 39 個顯著基因：14 個正選擇、25 個負選擇（Results 首段）。全基因 dN/dS 在每個癌別仍接近 1。
- **限制與反證：** 「被低估」來自作者自己的模擬，不是直接量測。它和 E2-01 用同類資料得到不同解讀。
- **支持哪一層（N3）：** 演化路徑（基因層級的選擇）。
- **對 diplosim 的意義〔推論〕：** SNV 沒有基因組座標，所以無法表達「必需基因區較少突變」。效應在全基因層級很小。屬真值層，優先度低。

### E2-17 Van den Eynden 2019, Nat Genet — 10.1038/s41588-019-0532-6
- **資料：** 8,683 樣本、32 癌別（TCGA）；bulk；short read。真值來源：依 trinucleotide signature 的中性模擬。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** neoantigen depletion 訊號偵測不到，可能是功效不足或早期免疫逃脫。
- **演化假設：** 免疫負選擇會造成 HLA 結合區的突變減少。
- **真實結論：** 12/19 癌別表面上有 HBMR < 1。只保留 signature 的模擬也出現類似訊號（HBMR = 0.83）。考慮 signature 後訊號可忽略（摘要）。
- **限制與反證：** 沒測到不等於不存在，作者自己保留此點。E2-09 用 ON／OFF 比值與個體 HLA，在部分群體測到負選擇訊號。
- **支持哪一層（N3）：** 觀測特徵（方法學：signature 會造出假選擇訊號）。
- **對 diplosim 的意義〔推論〕：** 不直接對應現況。它提醒：突變 signature 和選擇訊號會混淆，真值層若加入其中之一，要能分開檢查。

### E2-08 Lakatos 2020, Nat Genet — 10.1038/s41588-020-0687-1
- **資料：** 模型（branching process）＋879 個 colon、stomach、endometrial 癌（exome、RNA）；另有多區域 CRC；short read。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** 這些癌別在嚴格免疫壓力下演化，逃脫常在生長初期就被選出。
- **演化假設：** 沒有免疫逃脫時，neoantigen 不是 clonal 就是低頻。負選擇越強，整體 VAF 分布越像中性。
- **真實結論：** 57% 腫瘤至少有一種逃脫機制（MMR 71%、POLE 98%）。中度 T 細胞且無逃脫的群體有 neoantigen depletion。多區域 CRC 中 HLA LOH 見於 5/10 癌、1/6 腺瘤，其中 4/6 為 subclonal。
- **限制與反證：** 單一腫瘤的 neoantigen VAF 功效很低，要合併群體。整體 neoantigen 比例在不同組別沒有差異；作者說這符合文獻中的無 depletion 報告。
- **支持哪一層（N3）：** 模型部分支持演化路徑的機制；資料部分支持觀測特徵與 cohort 趨勢。
- **對 diplosim 的意義〔推論〕：** VAF 形狀不能區分「中性」與「強負選擇」。這直接支持 N3：單靠 VAF／BAM 相似不能證明過程。HLA LOH 是作用在單一 haplotype 上的選擇，屬 CNA 階段，現在不處理。

### E2-09 Zapata 2023, Nat Genet — 10.1038/s41588-023-01313-1
- **資料：** >10,000 原發、356 個 ICI 治療轉移；另有 6,858 TCGA 個體分析；48 人 ICI 前後縱向；bulk；short read。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** dN/dS 能分辨 immune edited 與 immune escaped，並有助預測治療反應。
- **演化假設：** 混合 edited 與 escaped 腫瘤會讓 cohort dN/dS 趨近 1。
- **真實結論：** escaped− 無反應者 immune dN/dS 中位 0.69（P = 0.0012）。縱向隊列中 nivolumab 只在非 edited 病人移除 neoantigen。
- **限制與反證：** 分類依預選的 escape 基因，未涵蓋的逃脫機制可能被誤分〔推論〕。這個混合假設若成立，會削弱 E2-01 的 cohort 平均解讀；但本筆記未量化抵消幅度。
- **支持哪一層（N3）：** 演化路徑（個體層級的免疫選擇），治療資料支持機制。
- **對 diplosim 的意義〔推論〕：** 群體平均的 dN/dS 不能推到單一腫瘤。diplosim 只模擬一個 bulk，所以不能把 cohort 平均當作每個模擬腫瘤都成立的事實。

### E2-03 Dentro 2021, Cell — 10.1016/j.cell.2021.03.009
- **資料：** 2,658 癌、38 癌別（PCAWG）；bulk WGS；short read；主要單區域；另有 5 個多區域前列腺癌。方法用模擬驗證。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 有（11 種 subclonal reconstruction 的共識）；分支判斷另用同 read pair 定相。
- **觀點：** subclone 普遍，選擇普遍。作者保留：不排除部分腫瘤是弱選擇或無選擇。
- **演化假設：** 同一 expansion 的突變有相同 CCF，所以聚類能得到 subclone。
- **真實結論：** 1,705 個有功效的腫瘤中 1,621（95.1%）有 subclone。功效門檻是 nrpcc ≥ 10，只測到 CCF 超過 30% 的 subclone。subclone 內平均 14% SNV 低於偵測極限；CCF < 30% 時平均漏 21%。多區域對照：單樣本漏 44% 變異，26% subclonal 看似 clonal。3,933 個 driver SNV／indel 中 357（9.0%）subclonal。85% 有 subclone 的樣本沒有已知 subclonal driver。只有 11% subclone（265／2,329）帶已知 driver。76% 樣本有 clonal driver。subclonal dN/dS > 1。兩 subclone 為手足的機率是親子的 3.11 倍（CI 1.71–7.50）；TRACERx 為 2.86。subclonal SNV 比例：肺鱗癌 6.1%、pilocytic astrocytoma 61.3%。黑色素瘤只有 31/62 測得 subclone。signature 在 clone 與 subclone 間大致穩定，但 34.5%–54.7% 邊界與變化點重合。
- **限制與反證：** 95.1% 只代表 CCF > 30% 且用聚類定義。E1-09 認為這種深度（中位約 46×）無法可靠區分 subclone 與 neutral tail。dN/dS > 1 是 cohort 訊號，不代表每個 subclone 都被選擇。低 CCF 會高估 CCF、低估突變數。
- **支持哪一層（N3）：** 克隆結構（聚類結果）；手足比例屬演化路徑，證據量小。
- **對 diplosim 的意義〔推論〕：** 對應 `prop_truncal_snvs` 和 topology。真實 subclonal 比例依癌別差很大，單一預設只代表一種情境（這裡不建議數值）。樹形比例目前不受控制。偵測門檻屬觀測層，不能寫進真值（N1）。

### E2-04 Gerstung 2020, Nature — 10.1038/s41586-019-1907-7
- **資料：** 2,658 癌（PCAWG）；bulk WGS（腫瘤 ≥30×）；short read；單區域。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無傳統建樹；用 copy number gain 上的 SNV 倍數定時，並跨樣本排序。
- **觀點：** 早期 driver 來自有限基因集，晚期更多樣。
- **演化假設：** 突變累積近似時鐘，gain 前的 SNV 有多拷貝。
- **真實結論：** 全體點突變：22% 早 clonal、7% 晚 clonal、53% 未定 clonal、17% subclonal。5,913 個 driver 點突變：29%、5%、56%、8%。TP53、KRAS 早期富集 12 與 8 倍。早期 driver 的 50% 集中在 9 個基因；晚期與 subclonal 各約 35 個基因。常見 driver 先於罕見 driver。CRC 排序符合 APC→KRAS→TP53。
- **限制與反證：** 分子時間會受突變率變化影響。排序是跨樣本的機率性排序，不是單一腫瘤的真實順序。subclonal 比例受偵測極限影響，是下限。
- **支持哪一層（N3）：** 演化路徑（群體層級順序）。單腫瘤的樹不受此證明。
- **對 diplosim 的意義〔推論〕：** diplosim 沒有時間和 driver 順序。對只測 HP 建樹的目標，driver 身分可能不是必要，但邊長和時間的關係缺失。屬真值層。定時依賴 multiplicity，屬 CNA 階段。

### E2-06 McGranahan 2015, Sci Transl Med — 10.1126/scitranslmed.aaa1408
- **資料：** 2694 腫瘤、九癌別（TCGA）；bulk exome；short read；單區域。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無；用 CCF 與 mutation copy number 分類。
- **觀點：** subclonal driver 影響標靶治療策略。
- **演化假設：** clonal 突變早於最近一次 clonal expansion，subclonal 較晚。
- **真實結論：** 除 KIRC 外，各癌別 driver 突變都富集於 clonal。PI3K-AKT-mTOR 超過 15% subclonal；GBM 的 IDH1 超過 20% subclonal。TP53 超過 90% 在基因組加倍前發生。超過 30 例有平行 subclonal 事件。APOBEC 在 clonal driver 佔 21%，在 subclonal driver 超過 45%（僅 APOBEC 相關癌別）。深度 70 時，VAF 0.1 偵測機率 0.98，VAF 0.05 只有 0.69。
- **限制與反證：** 單區域且未校正空間差異。低頻 subclonal 突變被低估。
- **支持哪一層（N3）：** 演化路徑（順序趨勢）與克隆結構（CCF 推論）。
- **對 diplosim 的意義〔推論〕：** 平行演化代表同一基因可在不同 clone 獨立突變。SNV 沒有基因身分，無法表達此現象。APOBEC 變化屬主題 04。偵測機率屬觀測層。

### E2-12 Williams 2016, Nat Genet — 10.1038/ng.3489
- **資料：** 904 癌、14 癌別；bulk WGS／WES；short read。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** 被判為中性的腫瘤，選擇發生在生長開始之前。
- **演化假設：** 中性生長使 VAF 累積分布呈 1/f power law。
- **真實結論：** 323/904 符合 power law（門檻 R² ≥ 0.98）；colon 為 38/108。這是模型擬合結果，不是中性的直接量測。
- **限制與反證：** 見 E2-13。分析窗只含部分 VAF。
- **支持哪一層（N3）：** 觀測特徵（VAF 形狀）。
- **對 diplosim 的意義〔推論〕：** 見差距表「neutral tail」。

### E2-13 PCAWG Evolution and Heterogeneity Working Group 2018, Nat Genet（Crossref 的第一作者欄；常稱 Tarabichi 等，此名來自記憶）— 10.1038/s41588-018-0258-x
- **資料：** 再分析 TCGA exome＋模擬（branching process）；short read；真值來自模擬。
- **讀取層級：** 全文（短文，讀完）。
- **用了建樹工具：** 無。
- **觀點：** VAF 分布沒有足夠資訊排除選擇。
- **演化假設：** 被判為中性的腫瘤，不應有 subclonal 選擇訊號。
- **真實結論：** 分析窗 VAF 0.12–0.24；37% 腫瘤有 WGD，會造成假性偏離。模擬中只有約 11% 正確拒絕中性。非中性腫瘤 53.5% 被判為中性，AUC 0.42。判為中性的腫瘤 subclonal dN/dS 仍顯著 > 1。
- **限制與反證：** 這是方法批評，不證明腫瘤沒有中性動態。E2-14 是 Williams 團隊後續的貝氏方法，作者認為只能測到大差異。
- **支持哪一層（N3）：** 否定「VAF 形狀→演化路徑」的推論，支持 N3 的原則。
- **對 diplosim 的意義〔推論〕：** VAF 相似不能當演化過程的驗證，HP 版本也一樣。

### E2-14 Williams 2018, Nat Genet — 10.1038/s41588-018-0128-6
- **資料：** 高深度的 breast、gastric、blood、colon、lung 與 MET500；bulk；short read；部分多區域；方法用模擬驗證。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 有（自建貝氏 branching process 模型）。
- **觀點：** 能偵測到的 subclone，都是早期出現且優勢大。
- **演化假設：** subclone 的平均 VAF 代表大小，突變數代表年齡；兩者可推 fitness 與出現時間。
- **真實結論：** 需要 >100X；深度不足時模型偏向中性，即使中性是錯的。gastric 29%（5/17）、colon 21%（15/70）、MET500 51%（58/113）有被選擇 subclone。優勢 >20%，且出現很早（AML 與乳癌在前 15 次族群倍增內）。篩選條件為 purity >40%、subclonal 突變 ≥25。
- **限制與反證：** 「早且強」很可能部分是偵測偏差〔推論〕：晚出現或弱優勢的 subclone 達不到可偵測頻率。模型假設良好混合與指數生長。E1-09、E2-13 都批評只憑 VAF 判中性。
- **支持哪一層（N3）：** 演化路徑（模型推論）。不是直接觀察。
- **對 diplosim 的意義〔推論〕：** 把 clone 的大小和年齡連起來，正是 diplosim 缺的關係（比例和邊長獨立抽）。屬真值層。

### E2-15 Miles 2020, Nature — 10.1038/s41586-020-2864-x
- **資料：** 146 樣本、123 病人（CH、MPN、AML）；740,529 細胞；targeted amplicon scDNA（31 基因）；真值為 single-cell 基因型。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無傳統工具；用基因型定 clone，再用 Markov 決策過程推路徑。
- **觀點：** 髓系腫瘤是隨時間演化的 clone 生態系。
- **演化假設：** 突變組合的合作決定 clone 優勢。
- **真實結論：** AML 由少數 clone 主導。signaling 基因突變常在不同 subclone 重複出現。單細胞找到 bulk 沒有的稀有突變。4/6 例 MPN→AML 轉化有 clonal sweep。gilteritinib 治療下 3/3 FLT3 clone 下降。clone 定義為至少 10 細胞，所以仍有偵測下限。
- **限制與反證：** 只看 31 個基因，clone 是 driver 定義的，不含 passenger。多為復發／難治樣本。血液腫瘤無空間結構，不能推到實體腫瘤。
- **支持哪一層（N3）：** 克隆結構（直接）；演化路徑（縱向個案）。
- **對 diplosim 的意義〔推論〕：** 「少數 clone 主導」與等權重的期望不同，但沒有量到分布參數。屬真值層，要在血液腫瘤範圍內解讀。

### E2-16 Minussi 2021, Nature — 10.1038/s41586-021-03357-x
- **資料：** 16,178 細胞、8 TNBC、4 細胞株；single-cell DNA（ACT，short read）；真值為 single-cell CN。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 有（balanced minimum evolution，用 subclone 的 CN 共識）。
- **觀點：** TNBC 在原發生長時持續產生 CN 多樣性。
- **演化假設：** clonal TP53、LOH、WGD 之後，有短暫不穩定期，接著持續 CN 演化。
- **真實結論：** 7–22 個 subclone，組成 3–5 個 superclone。體外每 4 次分裂約 1 個新 CNA。
- **限制與反證：** subclone 數量取決於定序細胞數，所以可能低估。只有 TNBC（高度非整倍體）。clone 定義是 CN 相似度。
- **支持哪一層（N3）：** 克隆結構（直接）。
- **對 diplosim 的意義〔推論〕：** clone 數比 bulk 估計多，且有兩層階層。這是 CNA 階段的證據。「parental-allele」在此由 major allele 定相，不代表父母來源。

### E2-25 Stein 2026, Nat Commun — 10.1038/s41467-026-69363-7
- **資料：** 數學模型＋agent-based 模擬；參數化到人類腫瘤；無新定序資料。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 無。
- **觀點：** 多個 clonal driver 用多階段停滯模型解釋較合理。
- **演化假設：** 空間擴張下，clonal interference 本身就會阻止 sweep。
- **真實結論（模型預測，不是量測）：** sweep 除早期外罕見。機率與突變率無關。晚期 driver 局部變多但不易固定。最後生長期超過兩次 sweep 極不可能。
- **限制與反證：** 作者說模型給上限，未納入微環境與免疫。對照 E2-15：血液腫瘤有 sweep，但非空間系統，不是直接反證。
- **支持哪一層（N3）：** 演化路徑（理論）。
- **對 diplosim 的意義〔推論〕：** 「clone 共存到取樣時」和模型相容，所以「所有 clone 留在 sample」不一定錯；但模型也預測祖先層級會被 sweep 清掉。

### E2-26 Salehi 2021, Nature — 10.1038/s41586-021-03648-3
- **資料：** 42,000 基因組；多年時間序列 scWGS；乳腺上皮細胞株與 PDX（TNBC、HER2+）；short read；真值為時間序列觀察。
- **讀取層級：** 全文（相關段落）。
- **用了建樹工具：** 有（sitka；fitClone 估 fitness）。
- **觀點：** CNA 定義的 clone 有可量測的 fitness，抗藥有代價。
- **演化假設：** Wright-Fisher 模型能從 clone 比例軌跡推選擇係數。
- **真實結論：** TNBC-SA1035 有 Clone A 從 20% 到測不到；Clone E 由少數擴張到 69%（1+s = 1.06）。fitness 係數能預測實驗混合競爭。cisplatin 下抗藥 clone 來自未治療時的低 fitness 譜系，高 fitness clone 被消滅。停藥後動態反轉，但不一定持續：X5 回到 Clone B 90%，X6、X7 維持 >99% Clone A。HER2+SA532 與 TNBC 不同，TNBC 才有明確動態。
- **限制與反證：** PDX 不是病人體內。實驗用 NRG 小鼠，所以推測沒有完整免疫壓力〔推論〕。clone 由 CNA 定義，SNV 的貢獻未分開。
- **支持哪一層（N3）：** 演化路徑（直接時間序列，克隆層級）。這是本筆記最接近「直接看到 clone 消失」的證據。
- **對 diplosim 的意義〔推論〕：** 真實過程有 clone 消失；diplosim 所有 clone 都留著，沒有滅絕的 clone。屬真值層。主軸是單一 bulk，這只當機制證據。

### 跨主題引用（卡片在主題 01，這裡只記本主題用到的數字）

- **E1-05 Turajlic 2018, Cell（10.1016/j.cell.2018.03.043）：** 101 病人、1,206 區域；short read；多區域；全文。每腫瘤最多 30 個 driver 事件，clone 中位 4 個（範圍 1–23），約 10 cm 後高原化。只有 VHL 時 MRCA 到診斷中位 28 年，多一個 clonal driver 時為 5 年。BAP1、SETD2、PTEN 有平行演化。作者把多 clonal driver 亞型解讀成 clonal sweep，這是解讀，不是直接觀察。支持克隆結構與演化路徑。
- **E1-09 Caravagna 2020, Nat Genet（10.1038/s41588-020-0675-5）：** PCAWG 重分析，short read；全文。深度低於 90–100x 且低 purity 時無法可靠重建；PCAWG 中位 45x、purity 65%，作者認為不足。低深度時 neutral tail 可能被誤認成 subclone。AML 320x 重分析移除一個假低頻 subclone。298 個二倍體案例只有 9（3%）有持續 subclonal 選擇（敏感度 2.7%–3.7%）。902 例：tail 突變 dN/dS 約 1，非 tail >1。限制：作者也說 dN/dS 在生長中的腫瘤有詮釋問題；篩選條件只留高功效案例。支持觀測特徵與克隆結構。

## 回答任務問題（短版）

1. **多少是 passenger？** cohort 層級約 99% coding 突變中性（E2-01），爭議在負選擇（E2-27、E2-09、E2-17）。
2. **driver 時序？** 常見 driver 偏早、基因集中；晚期分散（E2-04）。subclonal driver 是否推動擴張：只有 11% subclone 帶已知 driver（E2-03），只有 PDX 時間序列直接支持 clone 擴張與 CNA 的連結（E2-26）。
3. **sweep 與比例？** sweep 頻率沒有直接量測；E2-25 只是模型。比例：本批論文只報 clone 數（E1-05、E2-16）與定性描述（E2-15），沒有和 Dirichlet 比較。偵測下限依方法而異：CCF 30%（E2-03）、VAF 0.05 的機率下降（E2-06）、至少 10 細胞（E2-15）。
4. **clone 交互作用與滅絕？** 直接證據在 PDX（E2-26）與 AML 治療（E2-15）。WebSearch 關鍵字 negative frequency dependent、clonal interference 未找到人體縱向的直接實驗；該次搜尋只看結果摘要。
5. **治療與免疫？** 治療反轉 fitness（E2-26）。免疫選擇有訊號但量值爭議（E2-08、E2-09、E2-17）。這些只當機制證據。

## 雙倍體的爸爸和媽媽（本主題碰到的部分）

- **真值層：** 在下列檔案用 `paternal|maternal|parent-of-origin|parental (allele|haplotype|chromosome)|imprint` 搜尋（E2-01、03、04、06、08、12–17、25、26、27、E1-05、E1-09；E2-09 另用 `paternal|maternal|parent-of-origin|imprint` 查），沒有找到選擇強度和父母來源相關的量測。
- **觀測層：** E2-03 的「Parental alleles」只是兩條 allele 的著色；E2-16 的 parental-allele 由 major allele 定相。兩者都沒有指明父或母。這和任務書說的「HP1／HP2 是任意標籤」一致〔推論〕。
- **間接相關〔推論〕：** HLA LOH（E2-08）是作用在某一 haplotype 的選擇，但論文沒有報告它和父母來源的關係。

## 對 diplosim 的差距（照優先順序）

下表只列差距，不提實作。讀長一律 short read，不當驗證目標。

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| clone 內有 neutral tail：突變不只分布在 clone 共有層級（E1-09、E2-12） | SNV 只放在樹的邊上，clone 內所有細胞共有（`src/evolution.rs:273`） | 真值中沒有 clone 內低頻突變。此處屬真值，不是觀測。 | 中（理論與高深度資料一致；量值依方法而變） | 單點突變 |
| clone 大小、年齡、fitness 相關（E2-14、E2-26） | 比例來自 Dirichlet(1)（`src/sequencing.rs:63`），邊長隨機切段（`src/evolution.rs:273`），兩者獨立 | 沒有時間，也沒有大小和突變數的關聯 | 中（模型為主；PDX 直接觀察） | 單點突變 |
| clone 比例分布（E2-15 少數 clone 主導；E2-03 測到的 CCF 有偏差） | Dirichlet(1)（`src/sequencing.rs:59-63`、`docs/conipher_steps.md:117-119`），等於比例在單純形上均勻〔推論〕 | 未知。本批論文沒有分布量測，不能判定 Dirichlet(1) 是否合理 | 弱 | 單點突變 |
| clone 消失（E2-26、E2-15） | 所有 clone 留在 sample（`src/sequencing.rs:59`） | 沒有滅絕 clone，真值樹等於存活樹 | 中（治療／PDX 的機制證據；未治療腫瘤不足） | 單點突變 |
| 手足多於親子（E2-03 的 3.11） | 隨機二分＋剪葉，不控制 linear／branching（`src/topology.rs:57-109`） | 樹形比例未量過，也未控制 | 中低（SNV 對少） | 單點突變 |
| clonal／subclonal 比例依癌別差很大（E2-03：6.1%–61.3%） | `prop_truncal_snvs` 預設 0.5（`src/evolution.rs:273`） | 單一值只代表一種情境。不代表 0.5 錯，也不建議改值。 | 中 | 單點突變 |
| driver 與 passenger 的區別（E2-01、E2-04） | `src/*.rs` 用 `driver|selection|passenger|fitness|time` 搜尋沒有結果〔實測〕 | 無 driver 概念。若目標只是測 HP 建樹，可能不是必要，要先和使用者確認 | 強（生物事實），對目標的必要性未定 | 單點突變 |
| 平行演化（E2-06、E1-05、E2-15） | 每個 SNV 是獨立 locus，無基因身分 | 無法表達同基因獨立突變。diplosim 用無限位點式放置。 | 中 | 單點突變 |
| 選擇和 CN 交互作用（E2-01 的 CN=1；E2-08 的 HLA LOH） | CN 每 position 獨立（`docs/conipher_steps.md` S4–S6） | 無法表達 haplotype 特異的選擇 | 中 | CNA 後 |
| 偵測極限（E2-03、E2-06、E2-14、E1-09） | 真值保留所有 clone（屬正確做法，N1） | 不是真值差距。觀測層的漏抓要和真值分開評估 | 強 | 觀測層 |

## 未解問題

1. **passenger 在兩條 HP 上的比例：** 在本批 15 篇用 `haplotype` 搜尋，只有 E2-03、E2-08、E2-09 有結果。E2-03 指同 read pair 的突變／野生型組合，E2-08 與 E2-09 指 HLA。沒有論文量 passenger 在兩條 HP 的比例，所以本主題不能回答 N2 的 50% 問題。這要由主題 04 或 08 回答。
2. **clone 比例分布：** 需要 single-cell 且大量細胞、每個 clone 比例的原始表格。補充表格本次未讀，所以「沒有」只限主文段落。E1-05、E2-16 的補充資料可能有。
3. **sweep 頻率：** 實體腫瘤直接量測，在上述來源、關鍵字、期間內沒找到。
4. **未讀的種子：** Bailey 2018（driver 基因）、Bozic 2010（driver／passenger 模型）、Rosenthal 2019（肺癌 neoantigen）、Weghorn & Sunyaev 2017（負選擇）、Salichos 2020（單樣本生長模式）、Vogelstein 2013（review）。另有 Frankell 2023（TRACERx 的 subclonal selection）也沒讀；它已列在 `research/simulation_pipeline_research/truth_evidence_2026-10-25/04_event_evidence_real_tumors.md` 的參考文獻。
5. **long read 上的證據：** 本批論文都不是 long read。同 read 定相在 long read 可能增加分支判斷的功效〔推論〕，但本批沒有資料支持。
6. **E2-03 與 E1-09 的矛盾：** 同資料、不同模型。沒有獨立真值（single-cell）可以裁決。PCAWG 沒有配對 single-cell。
