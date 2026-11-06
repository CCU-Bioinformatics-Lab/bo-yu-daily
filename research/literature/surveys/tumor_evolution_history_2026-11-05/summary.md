# 腫瘤演化歷史文獻調查：摘要

日期：2026-11-05。用到的會議：2026-11-04（N1–N5）。範圍：8 個主題、97 篇不重複的論文。論文清單與讀取層級：[`source.md`](source.md)。

標記：〔論文〕論文量到或主張；〔程式〕讀 `diplosim` 程式；〔推論〕本檔的推論。E／B 編號的卡片在下面的主題筆記。

## 結論

1. **`diplosim` 現在模擬的是「一棵隨機樹加上隨機放置的 SNV」，不是演化過程。** 它沒有時間、族群動態、選擇，SNV 也沒有基因組座標。〔程式〕`src/topology.rs:57-109`、`src/evolution.rs:273`、`src/hp.rs:30`
2. **「每個 SNV 獨立以 50% 落在某條 HP」要拆成兩個主張。**
   - **比例約 50%：** 是合理的零假設，有初步支持，但沒有被證實。直接證據只有一篇未經同儕審查的 preprint：PCAWG 2,645 人中有 21 人可用，short read，不對稱上限 4–5%（cohort 合併 5.7%），imprinted 區無法分析。〔論文〕E4-26
   - **互相獨立：** 局部已被反駁，整體沒有人檢驗。Kataegis 的突變在同一條親代染色體上（E4-02）。B04 用 long read 找到有突變偏向一條 HP 的區域（下面「限制」有說明）。但全部 substitution 只有 3.7% 屬 clustered（E4-20）。〔論文〕
3. **爸爸和媽媽：在單點突變階段，現有證據沒有要求加父／母標籤。** 上述 preprint 沒有偵測到父母基因組之間的 SNV 總量差異。父母偏差的證據集中在特定基因座和癌別的 CN／LOH，例如 14q aUPD 有 21/22 例是父系（E8-16）。〔論文〕HP1／HP2 只是任意標籤，不等於父或母（E6-11、E8-09）。這是「沒有證據要求」，不是「證明不需要」。〔推論〕
4. **直接支持 long read 的證據很少。** 8 個主題中，只有主題 06 專收 long read。在本次範圍內沒找到用 long read 量全基因組 HP 間突變比例、邊長或 truncal 比例的研究。 2026-11-06 用 COLO829 和 HG008 的公開資料自行算出兩個細胞株的比例（lab_report），體染色體都接近各半。再用 PRCGAP 的公開結果逐段比較 8 個細胞株：兩條拷貝數相同的 229 個 20 Mb 區段，有 7 個校正後顯著，7 株的段間差異比純隨機大，原因沒有查。這些都不是論文結論。其他主題的數字幾乎都來自 short read，只能當生物假說，不能當 `diplosim` 的驗證目標或預設值。

## 流程對照（真實腫瘤 vs `diplosim`）

```text
真實腫瘤（文獻描述的過程）                     diplosim 現況
─────────────────────────                      ─────────────
正常細胞隨年齡累積突變 ───────────────────────► 無時間（只有 trunk 比例）
   │  E3-08：近線性累積                          prop_truncal_snvs = 0.5
   ▼
起始：driver 出現，約 4 個 coding driver ─────► 無 driver、無選擇
   │  E2-01；約 99% coding 突變接近中性           （和 passenger 中性相容）
   ▼
突變落在基因組上 ─────────────────────────────► 無座標；每個 SNV 獨立
   │  區域差異 > 5 倍（E4-05）                    Bernoulli(0.5) 選 HP
   │  kataegis 同一條 in cis（E4-02）
   ▼
族群擴張、clone 競爭 ─────────────────────────► 隨機二分＋剪葉
   │  樹形依癌別不同（E1-14、E1-05）              邊長和時間無關
   │  clone 內有低頻尾巴（E1-09）                 無 clone 內突變
   ▼
clone 消失、大小偏斜 ─────────────────────────► 全部 clone 留著，Dirichlet(1)
   │  E5-02、E5-03、E5-05（實驗系統）
   ▼
一次 bulk 取樣與定序 ─────────────────────────► 真值保留全部 clone（符合 N1）
      約 46× 只測得到 CCF > 30%（E1-10）          觀測層的偵測極限另外處理
```

CNA、LOH、WGD 依 N4 排在單點突變之後，放在[主題 07](07_cn_wgd_timing.md)，上圖不列。

## 假設與真實結論

### 共識（有直接資料，但多為 short read）

| 真實結論 | 數字 | 來源 | 支持的層（N3） |
|---|---|---|---|
| 多數腫瘤測得到 subclone | 1,705 個有功效的腫瘤中 95.1%；只測得到 CCF > 30% | E1-10 | 觀測特徵 |
| coding 突變幾乎都接近中性 | 約 99%；每腫瘤約 4 個 driver（癌別間 1–10） | E2-01 | 觀測特徵 |
| 樹形依癌別而異 | AML 123 人中 55% linear、45% branching；ccRCC clone 數中位 4（1–23） | E1-14、E1-05 | 克隆結構 |
| infinite sites 不是完全成立 | 12 個單細胞資料集中 11 個有同位點多次受影響 | E5-06 | 克隆結構 |
| 區域突變率差很多，但兩條 HP 多半一起變〔後半是推論〕 | 差異 > 5 倍；88% 基因組兩條同時複製 | E4-05、E4-14 | 機制 |
| Xi 比 Xa 突變多 | 一例校正 CN 後 3.5 倍；不是所有癌別都有 | E4-04 | 機制 |
| TSG 雙突變多在 trans，oncogene 多在 cis | oncogene 91% cis（243/268）；TP53 例外 43% cis（70/163）；long read 的 TSG 17 對 trans、2 對 cis | E4-12、E6-02 | 機制（只限 driver） |
| passenger 接近隨機保留，driver 有偏向 | gain／loss 時 mutant 與 WT passenger 接近等頻 | E4-17 | 機制 |

### 爭議（兩邊都有資料）

| 問題 | 一方 | 另一方 | 目前能說的 |
|---|---|---|---|
| 腫瘤是中性演化嗎？ | E1-01：部分腫瘤符合 1/f | E1-02：非中性模擬 53.5% 被誤判，AUC 0.42 | 1/f 不能單獨證明中性；受選腫瘤也有尾巴（E1-04） |
| subclone 由選擇推動嗎？ | E2-03（和 E1-10 同一篇）：subclonal dN/dS > 1 | E1-09：298 個二倍體案例只有 9 個（3%）有持續選擇 | 同資料、不同模型，沒有獨立真值可以裁決。大腸癌 27 個中 7 個有強選擇證據，15 個最佳模型是中性（E5-11） |
| 腫瘤內突變率固定嗎？ | E3-04：ccRCC 相容 | E3-03、E3-18：速率上升；E3-14：POLE 爆發 | 依癌別而定 |
| 突變來自分裂還是時間？ | 模型常假設來自分裂 | E3-07：neuron 不分裂也累積（只讀摘要） | 邊長不能直接換算成分裂次數 |
| long read phasing 受 CN 影響多大？ | E6-02：相對小 | 主題 06 的 smrest、LongPhase-S、Wakhan | 依 purity、LOH 比例而變 |

### 證據不足（不要寫成事實）

- **clone 比例的分布：** 在本次範圍內，沒找到未治療實體腫瘤的直接量測。實驗系統顯示 clone 大小偏斜（E5-03：植入約 2,150 個 clone，約 100 個長起來；E5-02：轉移部位 80–90% 細胞來自單一 clone）。所以現有證據不足以判定 Dirichlet(1) 對或錯。
- **sweep 頻率、實體瘤的 linear／branching 比例、樹深：** 沒找到直接量測。
- **扣掉 cluster 之後，相鄰 SNV 的 HP 是否獨立：** 沒找到直接檢驗。這是 `diplosim` 假設中最沒被測試的部分。
- **germline cis 效應、allele-specific TCR 造成的 HP 間差異：** 沒找到直接量測。
- **長讀定親源用在腫瘤：** E8-09 在 5 個 trio 的正常細胞驗證，要 Strand-seq 等長距離資訊；腫瘤未驗證。

## 對 `diplosim` 的差距（單點突變階段）

順序是〔推論〕，依「其他差距是否依賴它」與證據強度排列。這張表只列差距，不是實作方案（N2、M1：動手前要再列方案，由使用者選）。

| 順序 | 差距 | 屬於 | 證據 | 註 |
|---|---|---|---|---|
| 1 | SNV 沒有基因組座標 | 真值 | 強 | cluster、區域差異、phase block、同位點重複都依賴它 |
| 2 | HP 放置完全獨立，沒有 in cis 聚集 | 真值 | 中（E4-02、B04） | clustered 比例小（E4-20），影響可能有限 |
| 3 | 沒有時間與速率，邊長和 clone 比例無關 | 真值 | 中 | 生成模型的選擇仍有爭議 |
| 4 | 沒有 clone 內低頻尾巴 | 真值 | 中（模型為主） | 會影響 outlier 與低頻訊號 |
| 5 | 沒有 clone 消失，比例分布沒有依據 | 真值 | 弱到中（實驗系統） | 不足以判定要換成哪種分布 |
| 6 | 突變流失預設關閉，也沒有同位點重複 | 真值 | 中（E5-06、R01） | `prop_mutloss_positions` 已有（`src/params.rs:34`，預設 0），但比例直接設定，和座標無關 |
| 7 | 沒有 phase block；HP0 和 VAF 無關 | 觀測 | 強（主題 06） | 只影響觀測層，不能動到真值（N1） |

**目前沒有發現矛盾、不需要因文獻而改的部分：** `prop_snv_on_b` 的 50% 比例；passenger 不受選擇；真值保留全部 clone。`prop_truncal_snvs` = 0.5 沒有對錯可言：文獻的 subclonal 比例（E3-13：肺鱗癌 6.1% 到 pilocytic astrocytoma 61.3%）是偵測後的觀測值，不等於真值參數。

## 限制

- **搜尋不是系統性回顧。** 當天 NCBI E-utilities 和 PubMed connector 一直失敗，Europe PMC 時好時壞。子代理主要靠 WebSearch。主 agent 事後用 Europe PMC 補跑 7 組查詢（`gap_search_europepmc.txt`），從標題看，沒有找到推翻結論的論文，但只看每組前 12 筆的標題。所有「沒找到」都只限這個範圍。
- **多數論文只讀相關段落。** 用關鍵字定位後閱讀，補充資料與圖都沒讀。
- **引文核對不等於解讀正確。** 1,014 段引文都出現在原文（`claims/`），另有 1 段來自網頁，無法機器核對。主 agent 另外逐條抽查了本檔引用的關鍵數字。其餘 claim 沒有逐條核對中文解讀。
- **B04 的 190 個區域不能當成全基因組比例。** 這是 15 例、834 個「突變富集」區域中再挑出來的，有選擇偏差，也沒有校準過的 null，且可能受 CN 影響〔推論〕。
- **E5-02、E5-03、E5-05 是小鼠、xenograft、PDX 或細胞株，不能直接套到病人原發腫瘤。**
- **E5-04 的 16% 是 100% 減 84% 算出來的**，指不完全符合最佳樹的 SNV，主文沒有拆解原因，可能含偵測雜訊。
- **主題 04、08 共用同一篇 preprint**，主題 01、02、03 也共用 PCAWG 的 E1-10。不能當多份獨立證據。
- **取得方式有問題：** 部分子代理用偽裝瀏覽器的 User-Agent 抓網頁，詳見 [`source.md`](source.md)。

## 最值得補讀

1. **E6-12 已補讀並自行計算：** 論文正文沒有報告 hap1 對 hap2 的全基因組比例。用作者公開的 VCF 算，原始比例 61:39，主要因一條流失；扣掉無突變片段後 9.34 比 9.31 個／Mb（比值 1.004，95% CI 0.985–1.023）。只有一個細胞株，不知親源。獨立 ONT 資料的 2:1 區 read 定相是 1,639 比 1,425，分早晚後 1 份那條仍比對稱預測少約 10%，原因未定；不同批 COLO829 的 chr1p 拷貝數也不同。見 `lab_report/2026-11-06_colo829_hap_snv_ratio/`、`lab_report/2026-11-06_colo829_loss_events/`。
2. **Roerink 2018、Lee-Six 2019：** 單細胞衍生 colony 的直接觀察，Europe PMC 標為非開放取用，要另找來源。
3. **B04 的 Methods 與 Supplementary Fig. S13：** 判斷 190 個區域有多少是偶然。

## 搜尋方法

8 個子代理各負責一個主題，再由主 agent 驗收。排除清單沿用 repo 規則：`Excluded papers`（M02、M03、B02、B06、B08、B09）；模擬器 clonesim、VISOR、PSiTE、ProCESS、SCOUT 不在範圍內。HCC1395 依 11-04 決定暫停，本調查沒有提議新的 HCC1395 實驗或參數。

這批論文不符合 `research/index.md`「論文」表的收錄條件（2026-10-19：要用到建樹工具），而且多數只讀相關段落，所以放在主題層，不逐篇開 `papers/` 目錄。

## 學習網站

`site/index.html` 是給使用者補基礎知識的白話入門網站：39 張原創示意圖加 1 張真實資料圖（圖 7.7，COLO829；圖 7.8 整理 COLO829、HG008 的整體差別、8 個細胞株的逐段比較與區域差別），照「腫瘤的一生」的順序排列，不放模擬器決策。圖的構圖參考外部網路圖片（`來源` 頁列出），沒有複製。圖下「真實資料」的數字來自本調查。重建：在 `site/` 執行 `python3 build_site.py`；圖的來源是 `ch_a.py`、`ch_b.py`。

## 全文層

| 筆記 | 主題 | 階段 |
|---|---|---|
| [`09_core_hypotheses.md`](09_core_hypotheses.md) | 核心假說分級（ISA、克隆演化、時序）：哪些能當主要論證 | 單點突變 |
| [`04_haplotype_distribution.md`](04_haplotype_distribution.md) | 突變在兩條 HP 的分布（最優先，回答 11-04 未決問題） | 單點突變 |
| [`08_parent_of_origin.md`](08_parent_of_origin.md) | 爸爸和媽媽（parent-of-origin） | 單點突變；CNA 後 |
| [`01_evolution_modes.md`](01_evolution_modes.md) | 演化模式與樹形（linear、branching、中性、big bang） | 單點突變 |
| [`02_selection_clone_dynamics.md`](02_selection_clone_dynamics.md) | 選擇、driver／passenger、clone 動態 | 單點突變 |
| [`03_mutation_rate_timing.md`](03_mutation_rate_timing.md) | 突變率、signature、時間 | 單點突變 |
| [`05_clone_level_truth.md`](05_clone_level_truth.md) | 克隆層級的獨立證據（單細胞、lineage tracing） | 單點突變 |
| [`06_longread_evidence.md`](06_longread_evidence.md) | long read 腫瘤研究與 phasing 能力 | 單點突變（觀測層） |
| [`07_cn_wgd_timing.md`](07_cn_wgd_timing.md) | CNA、LOH、WGD 與 SNV 時序（預備知識） | CNA 後 |
