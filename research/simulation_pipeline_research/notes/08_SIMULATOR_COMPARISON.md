# 08 bulk 生成器比較：Pairtree、CONIPHER、SISTEM

調查日期：2026-10-24。來源：
- Pairtree（`pearsim@0b9b249`）與 CONIPHER（`TRACERx_simulation_tool@8c8d173`）：[05](05_OTHER_SIMULATORS.md)「輸入與輸出比較」。
- SISTEM（`627f888`／PyPI 1.0.5）：[07](07_SISTEM.md)。
- 試跑：`lab_report/2026-10-24_clonesim_sistem_trial/sistem/`（2026-11-04 刪除，已排除的路線；未進 git，無法取回）。

標記：〔程式〕讀原始碼；〔實測〕本機執行；〔論文〕；〔推論〕。

**範圍：只比較會直接產生 bulk 輸入（每個 sample 的 ref／alt read count）的生成器。** clonesim（Pharming）已在 2026-10-24 移出：它的 read 層只產生 single-cell 資料，是給 single-cell 建樹軟體（Pharming、Phertilizer、SCITE）用的。Pharming 給 DeCiFer 的 bulk 輸入，是把所有 cell 的 read 加總成單一 pseudo-bulk（`Pharming/src/prep_decifer.py`），不是 bulk 模擬。程式層級的紀錄（原 `06_CLONESIM.md`）已在 2026-10-29 刪除。〔程式〕

SISTEM 的主要目標也是 single-cell（論文只評估 single-cell CNA 建樹），但它原生有 `gen_readcounts_bulk`，會為每個 site 寫出 bulk read count，所以保留。〔程式＋論文〕

## 1. 結論

- **三個工具各自缺不同的東西，沒有一個能直接產生 HP-aware 的 PhyClone 輸入。**〔推論〕
- **只有 SISTEM 有「全基因組一致的 haplotype 標籤」。** 它能直接推出 SNV 在 allele 0 或 1。CONIPHER 的 A／B 只在單一位點內有意義，Pairtree 沒有 allele。〔程式〕
- **只有 Pairtree 與 CONIPHER 輸出可以直接用的 read count。** SISTEM 有 read count，但 alt 是取整算出來的，沒有抽樣，VAF 也沒有用 CN 加權。〔程式＋實測〕
- **只有 CONIPHER 與 SISTEM 有基因組座標。** CONIPHER 用真實的 CHR／POS，SISTEM 用 hg38 的染色體長度。Pairtree 只有序號。〔程式〕
- **三個都沒有 read 共現、germline het SNP、PS block 或 phasing 誤差。** 這一層一定要自己寫。〔程式〕
- **seed 的狀況：** CONIPHER 的 seed 會生效。SISTEM 在外部設 `np.random.seed` 就能重現。Pairtree 記錄的 seed 沒有生效。〔實測〕

**建議〔推論〕：**
- 第一個 PhyClone baseline 用 **CONIPHER**。它有現成資料、能逐 byte 重現，也已經有 PhyClone 的轉換規則。
- HP 生成器的真值骨架，現成工具中只有 **SISTEM** 有全基因組一致的 haplotype 標籤。它的 bulk 計數要用 `truth_snv.tsv` 的期望值重抽，不要直接用。
- 另一條路是在 CONIPHER 的骨架上自己補 haplotype：把每個位點的 A 隨機指定到 HP1 或 HP2，並讓同一 segment 內的位點方向一致。

## 2. 輸入

| | Pairtree | CONIPHER | SISTEM |
|---|---|---|---|
| 介面 | CLI | Python 函式（`tx_simulation`） | Python API／YAML |
| 樹的大小 | `-K`，直接指定 | `n_nodes`，直接指定 | 間接：由生長、取樣與 `min_mut_fraction` 決定 |
| sample 數 | `-S` | `n_samples` | `nsites`（一個 site 是一個 sample） |
| SNV 數 | `-M` | `n_positions` | 間接：每條邊 ~ Binomial(代數, `SNV_pass_rate`) |
| depth | `-T`，每個位點相同 | `coverage`，Poisson，和 CN 成比例 | `coverage`，Poisson × 不加權平均 CN／2 |
| clone 比例 | Dirichlet(`alpha`) | 每個 sample 3–8 個 clone，Dirichlet(1) | 不能指定，由生長決定 |
| purity | 沒有參數（隱含在 1−eta_root） | 每個 sample U(min, max) | `ncells_normal`；**各 site 幾乎相同** |
| CN | 沒有（576 份 CN 不影響 read） | 依位點：gain／loss 比例、truncal 比例、WGD | focal／arm／整條染色體／WGD，各有速率 |
| mutation loss | 沒有 | `prop_mutloss_positions` | 沒有參數；deletion 時自然發生 |
| noise | garbage `-G` | `fract_noise`（假 cluster） | 沒有 |
| seed | `--seed`，**沒有生效** | `rs`，會生效 | 沒有參數；外部 `np.random.seed` 可重現 |

## 3. 輸出

| | Pairtree | CONIPHER | SISTEM |
|---|---|---|---|
| 真值樹 | pickle 的 `structure`（parent 向量） | `_treeedges.tsv`（含每條邊的事件數） | `clone_tree.nwk`；clone 比例只在 pickle 裡 |
| 真值分群 | `params.json` 的 `clusters` | `.tsv` 的 CLUSTER | SNV 的起源 node；空 node 要併掉 |
| 真值 clone 比例 | `eta` | `_cloneprops.tsv` | 只在 pickle（leaf cell 數）；internal node 一律 0 |
| 每個位點的 CN 真值 | 沒有 | CN_A／CN_B、MUT_CN | `observed_CNPs.tsv`、`ancestral_CNPs.tsv`（allele 0, allele 1） |
| 給建樹工具的資料 | `.ssm`（var、total、var_read_prob＝0.5） | `_TX.tsv`（REF/VAR、DEPTH、CN A/B、purity、CHR/POS） | `readcounts.tsv`（total,alt） |
| 參數紀錄 | pickle 的 `args` | `_info.tsv` | 沒有（`sim.log` 只是生長紀錄） |

## 4. 模型差異

### 4.1 樹形

| | 怎麼長 | 偏向 |
|---|---|---|
| Pairtree | node 有 0.75 的機率接在前一個 node 下 | 偏線性 |
| CONIPHER | 隨機 binary tree，再隨機剪 leaf | 有分岔 |
| SISTEM | agent 生長加 selection，回溯 lineage，再用 coalescent 解多分岔 | 只有 leaf 有 prevalence；有空 internal node |

〔程式，見 05、07〕

### 4.2 CN 與 haplotype

| | CN 的單位 | CN 放在哪 | SNV 在哪個 allele | allele 標籤跨位點一致嗎 |
|---|---|---|---|---|
| Pairtree | 沒有 | — | 沒有 | — |
| CONIPHER | **每個位點獨立** | 樹的 node／edge（`_treeedges` 有事件數） | 一律在 A（`snv`、`gain_A`、`loss_A` 都更新突變 copy） | **否**：A 只代表該位點帶突變的 allele〔程式 `evolution.py` L163–180＋推論〕 |
| SISTEM | 5 Mb region＋focal 長度 | 樹的邊（child 複製 parent 再套事件） | `Allele` 欄 0／1 | **是**：新 copy 繼承來源 allele〔程式〕 |

所以要做 HP 真值，現成工具只能用 SISTEM。CONIPHER 只能說「SNV 和 A 同側」，不能說兩個 SNV 是否在同一條 haplotype。〔推論〕

### 4.3 multiplicity 與 CN timing

| | SNV 在 CN 前 | SNV 在 CN 後 | 已知問題 |
|---|---|---|---|
| Pairtree | 不適用 | 不適用 | — |
| CONIPHER | `gain_A` 會讓突變 copy 加 1 | 突變 copy 不變 | `constant_multiplicity` 預設 True，會限制 subclonal CNA 數 |
| SISTEM | copy 跟著複製（實測 multiplicity 2、4） | 只在一份 copy 上 | 沒發現 |

### 4.4 VAF 與 read count

| | 期望 VAF | 抽樣 |
|---|---|---|
| Pairtree | 0.5·phi | Binomial |
| CONIPHER | 依 CN、multiplicity、purity | DEPTH 用 Poisson，VAR 用 Binomial〔程式 `src/sequencing.py` L98、L103〕 |
| SISTEM | Σp_c·(alt_c／tot_c)：**沒有用 CN 加權** | DP 用 Poisson；**alt＝round(DP×fraction)，沒有抽樣**〔程式 `reads.py` L296–302〕 |

## 5. 對照 04 缺口表

| 04 的缺口 | Pairtree | CONIPHER | SISTEM |
|---|---|---|---|
| SNV 落在哪條 haplotype | 否 | 部分（只有位點內 A） | **是** |
| allele-specific CN 跟著 haplotype | 否 | 部分 | **是** |
| CN segment 結構 | 否 | 否（每個位點獨立） | **是** |
| CN 跟著 clone、sample 間一致 | 否 | **是** | **是** |
| CN timing | 否 | **是** | **是** |
| subclonal CN | 否 | **是** | **是** |
| purity < 1 | 隱含 | **是**（每個 sample 不同） | 部分（各 site 相同） |
| read 共現 | 否 | 否 | 否 |
| phasing 誤差 | 否 | 否 | 否 |
| 真實座標、PS block | 否 | 座標有，PS 沒有 | 座標像 hg38，PS 沒有 |
| 可用的 read count | **是** | **是** | 有，但模型不對 |
| seed 可重現 | 否 | **是** | 外部設定可重現 |
| 授權 | 無 | BSD-3 | GPL-3.0 |

## 6. 要做 HP-aware PhyClone 輸入，各要補什麼

| | 要補的東西 | 工作量〔推論〕 |
|---|---|---|
| Pairtree | CN、haplotype、purity、座標、read 層，等於全部重寫 | 高 |
| CONIPHER | 全基因組的 haplotype 標籤、segment、座標上的 PS block、read 層 | 中到高 |
| SISTEM | 重抽 read count（用 CN 加權）、germline het SNP、PS block、read 層；每個 site 的 purity 要能不同；併空 node | 中 |

轉換程式（試跑時寫的）：`tools/sistem_to_phyclone.py`（2026-11-04 刪除，已排除的路線；未進 git，無法取回）：SISTEM → PhyClone `data.tsv`＋真值樹＋`truth_snv.tsv`（含 HP 拆分期望值）。〔實測〕

## 7. 三棵真值樹的共同點（2026-10-24）

比較圖：`lab_report/2026-10-24_sim_truth_tree_comparison/`（2026-11-04 刪除，已排除的路線；未進 git，無法取回）。Pairtree（576 份）與 CONIPHER（150 份）用全部資料統計；SISTEM 只有兩棵試跑樹，所以靠程式判斷。

### 三個都有的共同點

| 共同點 | 證據 |
|---|---|
| 有根樹，root 是 normal（沒有 SNV） | 三個工具的真值檔都有，SISTEM 是 `P0`／`diploid`〔程式＋實測〕 |
| 每個 SNV 只出現在一個 node（infinite sites／Dollo），沒有 parallel mutation | 三個工具的 SNV→node 都是一對一〔程式〕 |
| prevalence 滿足 sum rule：parent 的 cellular prevalence ≥ 所有 children 的總和 | 三個工具都由 clonal prevalence 沿子樹加總〔程式〕 |
| 樹的大小在 10–30 個 clone 左右，以二分岔為主 | 比較圖；CONIPHER 149／150 棵的最大分岔數是 2〔實測〕 |
| clone 是「一群同時出現的 SNV」，SNV 數和時間或突變率無關 | 三個工具都直接抽 cluster 大小或每邊 SNV 數〔程式〕 |

### 看起來共同、其實不共同的點

| 特徵 | CONIPHER | SISTEM | Pairtree |
|---|---|---|---|
| root 下只有一個 truncal clone | 150／150〔實測〕 | 是（單一 founder）〔程式〕 | **只有 322／576（56%）**〔實測〕 |
| truncal 是 SNV 最多的 node | 144／150；中位數占 61% 的 SNV〔實測〕 | 試跑 seed 1：41 個，最多〔實測〕 | **只有 61／576**；中位數占 10%〔實測〕 |
| 每個 sample 只含部分 clone | 是（每個 sample 3–8 個） | 是（依 site） | **否**：每個 clone 在每個 sample 都有比例 |
| CN 事件放在樹上 | 是 | 是 | 沒有 CN |
| purity < 1 | 是 | 是（各 site 相同） | 隱含 |
| 線性樹 | 1／150 | 少 | **153／576（27%）最大分岔是 1** |

所以 Pairtree 是例外。它允許多個 clone 直接從 normal 長出來，常常是全線性的樹，truncal 也不大。CONIPHER 與 SISTEM 都是「一個大 trunk，下面分岔」的形狀。

### 對我們生成器的建議〔推論〕

- **保留三個工具都有的規則**：normal root、infinite sites、sum rule、10–30 個 clone、以二分岔為主。這些是目前 bulk 建樹工具 benchmark 的共同預設，偏離時要說明原因。
- **採用 CONIPHER 與 SISTEM 的共同形狀**：單一 truncal clone，而且 truncal SNV 占多數（CONIPHER 中位數 61%）、sample 間 clone 組成不同、CN 事件綁在樹上、purity < 1。
- **三個工具都沒有、要自己補**：read 層、HP phasing、germline het SNP、phasing 誤差。
- **每個 clone 要有最少 SNV 數**：CONIPHER 有 33% 的 clone 只帶 ≤ 5 個 SNV，bulk 資料分不出來（見 05「CONIPHER 真值 clone 過細」）。
- **不要把這些共同點當成生物學證據。** 它們是建模慣例，沒有一個工具拿模擬樹和真實腫瘤樹比過分布。

## 8. 哪個工具提供的真值資訊最多（2026-10-24）

計分：有＝1、部分＝0.5、沒有＝0。「有」是指輸出檔可以直接讀到，或用讀檔就能算出來（不必改程式或讀 pickle）。證據見 05、07 與 `lab_report/2026-10-24_sim_truth_tree_comparison/`。

| 資訊 | Pairtree | CONIPHER | SISTEM |
|---|---|---|---|
| 真值樹 | 1 | 1 | 1 |
| clone 比例與 purity 寫成檔 | 0.5（eta；purity 隱含） | 1（`_cloneprops`，含 normal） | 0（只在 pickle） |
| allele-specific CN | 0 | 1（每個位點 A／B） | 1（每個 region allele 0／1） |
| allele 標籤全基因組一致（可對應 HP） | 0 | 0 | 1 |
| multiplicity／CN timing | 0 | 1（`MUT_CN`） | 0.5（要讀 pickle 才能算） |
| 逐 clone 的事件紀錄 | 0 | 1（`_events.tsv`：每個位點 × 每條邊） | 1（`CNA_events`、`SNV_events`，含類型與 allele） |
| mutation loss | 0 | 1（參數＋事件） | 0.5（會發生，但要讀 pickle） |
| WGD | 0 | 1 | 1 |
| 基因組座標 | 0 | 1（真實 CHR／POS） | 0.5（hg38 長度，位置隨機） |
| 可直接用的 bulk read count | 1 | 1 | 0.5（沒有抽樣、沒有 CN 加權） |
| 參數紀錄＋seed 可重現 | 0 | 1（`_info.tsv`、`rs`） | 0.5（外部設 seed，沒有參數紀錄） |
| read／haplotype FASTA 層 | 0 | 0 | 1（每個 haplotype 的 FASTA、single-cell read） |
| **合計（滿分 12）** | **2.5** | **10** | **8.5** |

結論〔推論〕：

- **輸出檔裡的真值最完整：CONIPHER（10 分）。** 每個 SNV 都有 cluster、CCF、DCF、MUT_CN、CN_A／CN_B、purity、真實座標，每條邊每個位點的事件也都寫出來，參數與 seed 也有紀錄。它唯一缺的是全基因組一致的 haplotype。
- **模型最廣：SISTEM（8.5 分）。** 它有演化動態、metastasis、arm／chromosome／WGD、haplotype FASTA。但重要真值（clone 比例、purity、mutation loss）只在 pickle 裡，bulk 計數模型也有問題。
- **最少：Pairtree（2.5 分）。** 它只有樹、cluster、prevalence 與 read count。

## 9. 限制

- SISTEM 只跑了小設定，兩個 seed，沒有統計樹形分布。
- SISTEM 的轉換結果沒有實際丟給 PhyClone 跑。
- CONIPHER 的「A 不是全基因組 haplotype」來自程式結構（每個位點獨立模擬），沒有另外實測。
- 授權：SISTEM 是 GPL-3.0，把它的程式碼複製進 repo 會受 GPL 約束。
