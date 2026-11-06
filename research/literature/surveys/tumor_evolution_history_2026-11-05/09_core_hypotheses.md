# 腫瘤演化核心假說：哪些能當主要論證（2026-11-06）

依 N2 整理：假說、證據、適用範圍。本檔不談模擬器怎麼改。用到的會議：2026-11-04。

標記：〔論文〕原文；〔程式〕讀程式；〔推論〕本檔判斷。核對欄的「親核」是 2026-11-06 用 Europe PMC 或 PubMed 全文抓到原句；「代理」只有 subagent 回報，用前要再核對。

## 結論

- **ISA 不是「被證實」的事實。** 嚴格版已有反例；可以主張的是「做 SNV 分群時，它是可用的近似」，而且 UV、MSI、高突變負荷的腫瘤要特別小心。〔論文〕〔推論〕
- **實證最強的假說有六個：** 克隆演化、多數 coding 突變是 passenger、subclone 普遍存在、TSG 雙擊機制、正常組織有 driver clone、突變隨年齡累積。〔推論〕
- **有一條對我們不利，要正面回應：** Tarabichi 2021 認為建樹一般應限於多樣本研究。我們的目標是單一 bulk。〔論文〕

## 分級總表

分級是本檔的判斷〔推論〕。除非標 long read，數字都來自 short read、單細胞或 colony，只當生物假說，不能當 `diplosim` 的驗證目標。

| 假說 | 等級 | 可當主要論證嗎 | N3 層 |
|---|---|---|---|
| 克隆演化：突變依序累積、逐步分化 | 大量直接實證 | 可以，限一般形式 | 演化路徑 |
| 多數 coding 突變是 passenger | 比例：大量直接實證 | 可以，限 coding | 演化路徑（群體） |
| Subclone 普遍存在 | 存在：大量實證；數量：有條件 | 可以，不要引用數量 | 克隆結構 |
| TSG 雙擊 | 機制：大量直接實證 | 可以，限 TSG | 演化路徑 |
| 正常組織有 driver clone | 大量直接實證 | 可以 | 克隆結構 |
| 突變隨年齡累積（分子時鐘） | 正常組織：大量直接實證 | 可以，腫瘤定年除外 | 觀測特徵 |
| 突變率依基因組區域不均 | 大量直接實證 | 可以，這不是分 HP 的結果 | 觀測特徵 |
| ISA 作為分群近似 | 有實證但有條件 | 可以，限近似版 | 克隆結構 |
| 用 CN、multiplicity 定相對時序 | 有條件 | 只當原理 | 演化路徑 |
| 單株起源 | 有條件：癌前有反例 | 不要寫成「一律」 | 克隆結構 |
| Perfect phylogeny | 有條件：只有細胞株、PDX 的比例 | 輔助 | 克隆結構 |
| 體染色體突變約各半 | 有條件：證據很少 | 只當暫定假設 | 觀測特徵 |
| Inactive X 突變較多 | 有條件：依癌別 | 輔助 | 觀測特徵 |
| Sum、crossing rule | 主要是建模假設 | 不能單獨用 | 克隆結構 |
| 同 CCF 等於同 clone | 有爭議 | 不可以 | 克隆結構 |
| 中性腫瘤比例、Big Bang 泛化、sweep 頻率 | 有爭議，或沒找到直接量測 | 不可以 | 只到觀測特徵 |
| 腫瘤內突變率固定、WGD 多早、chromothripsis 一次發生 | 有爭議 | 不可以 | 演化路徑 |

## ISA 與建樹規則

### ISA：同一位點一生只突變一次

| 重點 | 原句 | 來源 | 核對 |
|---|---|---|---|
| 反例：單細胞 | "for 11 of 12 single-cell sequencing data sets"；"Seven cases involved the loss of earlier mutations, five of which occurred at sites unaffected by large-scale genomic deletions"；"Four cases exhibited a parallel mutation" | Kuipers 2017，[10.1101/gr.220707.117](https://doi.org/10.1101/gr.220707.117) | 親核 |
| 反例：全基因組 bulk | "18,495 biallelic mutations ... in 559 (21%) bulk sequencing samples" | Demeulemeester 2022，PCAWG，[10.1038/s41588-021-01005-8](https://doi.org/10.1038/s41588-021-01005-8) | 親核 |
| 支持近似 | 分群方法 "are otherwise expected to remain robust at the levels identified here" | 同上 | 親核 |
| 支持近似 | "occur rarely enough that they are not expected to impact clustering based on hundreds to thousands of SNVs" | Tarabichi 2021，[10.1038/s41592-020-01013-2](https://doi.org/10.1038/s41592-020-01013-2) | 親核 |
| 對 phasing 的例外 | 黑色素瘤的 SNV pair "a median 67% ... reflect phylogenetically uninformative biallelic parallel mutations" | Demeulemeester 2022 | 親核 |
| 正常組織 | 11,429 個基因組中，最終 "328 MAVs and 490 PVVs"，來自持續的 DNA lesion（非腫瘤） | Spencer Chapman 2025，[10.1038/s41586-024-08423-8](https://doi.org/10.1038/s41586-024-08423-8) | 親核 |

可以這樣寫〔推論〕：「ISA 在腫瘤中並非嚴格成立，但在分群層級是常用且有條件的近似。」

### 突變丟失（Dollo）

- 丟失確實存在（Kuipers 2017）。〔論文〕
- **「LOH 是最常見的反例」不能當定論。** 單細胞樹上常見的是 loss，鹼基層級的模擬多是 parallel，而且 Kuipers 的 7 例中有 5 例不在大片段缺失的位置。各研究的分母也不同。〔論文〕〔推論〕
- TRACERx 100 報告 "a median of 13% of subclonal mutations" 被丟失（[10.1056/NEJMoa1616288](https://doi.org/10.1056/NEJMoa1616288)）。〔論文〕代理，來自 repo 舊紀錄。

### 樹的規則

- **Perfect phylogeny：** Laks 2019（細胞株、PDX 單細胞）有 14,068 個 SNV，"84% fit perfectly with the inferred phylogenetic tree"；breakpoint 是 88%。其餘 16% 的原因沒有拆解。[10.1016/j.cell.2019.10.026](https://doi.org/10.1016/j.cell.2019.10.026) 〔論文〕親核
- **Sum、crossing rule：** 由 ISA 加上「不丟失」推得。在 Europe PMC 用 "pigeonhole"、"sum rule"、"crossing rule" 查前列結果，沒找到真實破壞率的直接量測。〔推論〕代理
- **單一 bulk 的挑戰：** "We believe tree inference should generally be restricted to multi-sample studies: while subclones can be identified in single samples, they are only weakly informative of the underlying tree"（Tarabichi 2021）。〔論文〕親核
- **CCF 分群：** 模型會 "detect several clusters within the neutral tail that are erroneously identified as subclones"；"for the majority of PCAWG cases, the data resolution was too low"（Caravagna 2020，[10.1038/s41588-020-0675-5](https://doi.org/10.1038/s41588-020-0675-5)）。〔論文〕親核

### 工具依賴什麼（只陳述現況，subagent 回報，未重驗）

- haploclone：同節點共用一個 CCF（`src/tree.rs:5`）；outlier 預設 0（`src/main.rs:202-204`）。〔程式〕
- Pairtree：丟棄 garbage 突變（`pairtree/README.md:224,499`）。〔程式〕
- `diplosim`：位置不放回抽樣，所以不重複（`src/evolution.rs:273-276`）；loss 預設 0（`src/params.rs:99`）。〔程式〕

## 克隆起源與選擇

| 假說 | 重點 | 來源 | 核對 |
|---|---|---|---|
| Passenger | "nearly all coding substitutions (∼99%) appear to accumulate neutrally"。同文也承認正負選擇相抵的 "formal possibility" | Martincorena 2017，7,664 例，[10.1016/j.cell.2017.09.042](https://doi.org/10.1016/j.cell.2017.09.042) | 親核 |
| Subclone | "1,621 tumors (95.1%)"，只測 CCF > 30%，"a conservative lower bound"。這是分群模型的輸出，不是獨立驗證 | Dentro 2021，[10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) | 親核 |
| 樹形 | 兩個 subclone 為手足的機率是親子的 3.11 倍（CI 1.71–7.50） | Dentro 2021 | 親核 |
| 雙擊（long read） | 可定相的 TSG 雙突變，"The majority (n = 17) of pairs were found to occur in trans, while two were found to occur in cis" | O'Neill 2024，[10.1016/j.xgen.2024.100674](https://doi.org/10.1016/j.xgen.2024.100674) | 親核 |
| 雙擊的例外 | Haploinsufficiency，"a questionable dogma"，指所有 TSG 都守雙擊 | Berger 2011，[10.1038/nature10275](https://doi.org/10.1038/nature10275) | 代理 |
| 依序累積 | 2,658 例，22% 早 clonal、17% subclonal | Gerstung 2020，[10.1038/s41586-019-1907-7](https://doi.org/10.1038/s41586-019-1907-7) | 代理 |
| 單株起源的反例 | 小鼠 lineage tracing，有色腫瘤 40% heterotypic | Sadien 2024，[10.1038/s41586-024-08053-0](https://doi.org/10.1038/s41586-024-08053-0) | 代理 |
| 中性爭議 | 323／904 符合 power law；Tarabichi 2018 指 "53.5% false positive" | Williams 2016，[10.1038/ng.3489](https://doi.org/10.1038/ng.3489)；[10.1038/s41588-018-0258-x](https://doi.org/10.1038/s41588-018-0258-x) | 代理 |
| 正常組織 | 皮膚 18–32% 細胞帶受選突變（4 人）；食道 NOTCH1 正常組織 30–80%、癌約 10% | Martincorena 2015，[10.1126/science.aaa6806](https://doi.org/10.1126/science.aaa6806)；2018，[10.1126/science.aau3879](https://doi.org/10.1126/science.aau3879) | 代理 |

**注意：** Dentro、Gerstung、Caravagna 都用 PCAWG，不是獨立證據。同一批資料，Dentro 寫 "widespread selection"，Caravagna 在 298 例中只找到 9 例。〔論文〕代理

## 突變時序與過程

| 假說 | 重點 | 來源 | 核對 |
|---|---|---|---|
| 分子時鐘 | 正常血液幹細胞的突變 "increases linearly with age" | Lee-Six 2018，[10.1038/s41586-018-0497-0](https://doi.org/10.1038/s41586-018-0497-0) | 親核 |
| 時鐘的限制 | 只有 signature 1、5 和年齡相關，合計占 23% | Alexandrov 2015，[10.1038/ng.3441](https://doi.org/10.1038/ng.3441) | 代理 |
| Multiplicity 定序 | 此前 "has not been subject to experimental validation"；細胞株驗證 "90.19% of pre-genome doubled mutations were correctly timed" | López 2020，[10.1038/s41588-020-0584-7](https://doi.org/10.1038/s41588-020-0584-7) | 親核 |
| 定序的限制 | 高度擴增區無法定時；53% clonal 無法定時 | Purdom 2013；Gerstung 2020 | 代理 |
| 區域不均 | 突變率差異超過 5 倍；染色質解釋度高 | Lawrence 2013，[10.1038/nature12213](https://doi.org/10.1038/nature12213)；Polak 2015，[10.1038/nature14221](https://doi.org/10.1038/nature14221) | 代理 |
| 局部聚集 | "only 3.7% of all substitutions ... are clustered events" | Bergstrom 2022，[10.1038/s41586-022-04398-6](https://doi.org/10.1038/s41586-022-04398-6) | 親核 |
| WGD 頻率 | 37%；28.2%（panel） | Zack 2013，[10.1038/ng.2760](https://doi.org/10.1038/ng.2760)；Bielski 2018，[10.1038/s41588-018-0165-1](https://doi.org/10.1038/s41588-018-0165-1) | 代理 |
| Chromothripsis 爭議 | Stephens 2011 稱 "apparently one-off"；Umbreit 2020 認為 "accumulates through a cascade" | [10.1016/j.cell.2010.11.055](https://doi.org/10.1016/j.cell.2010.11.055)；[10.1126/science.aba0712](https://doi.org/10.1126/science.aba0712) | 代理 |
| 兩條的比例 | 只有 Lefèbvre 2026（21 人，short read，預印本）；另有本 repo 的 COLO829、HG008 細胞株計算 | [10.64898/2026.09.02.748867](https://doi.org/10.64898/2026.09.02.748867)；`lab_report/2026-11-06_*_hap_snv_ratio/` | 代理；repo |

## 限制

- 這不是系統性回顧。全文多用關鍵字定位句子，補充資料沒讀。部分 PubMed 查詢被限流或回 0 筆，所以「沒找到」的效力很弱。
- 「大量實證」是本檔的判斷，沒有正式共識聲明。唯一直接提到共識的句子，是 Sadien 2024 作者對單株起源的描述（代理）。
- 查到的 long read 直接證據很少；本檔只有 O'Neill 2024 的雙擊結果來自 long read。ISA 在 long read 腫瘤資料中的直接量測，在 Europe PMC "long-read" 加 "infinite sites" 的前 8 筆內沒找到（代理）。
- subagent 回報的 Kuipers「兩例大腸癌各約 8,000 個平行突變」，我在全文找不到這個數字，所以沒有收錄。
- Knudson 1971、Jäger 2013 的本機快取標 `WEB:`，可能來自舊的偽裝 User-Agent 抓取（`source.md`），這裡不引用其快取內容。Knudson 的雙擊本身以 O'Neill 2024 等為證據。
