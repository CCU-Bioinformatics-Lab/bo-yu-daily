# Long-read 特徵第一版評估規格

採用日期：2026-10-15。範圍：`plan.md` 的 C2（multiplicity prior）、C3（haplotype-specific likelihood）、C4（同 read 共現 topology factor）。

**狀態：已採用的評估設計，尚未實作評分程式或產生實驗結果。** 下列新增規格屬 `inferred`；AD F-score、V-measure 沿用 PhyClone 論文定義，其餘是本 repo 的評估選擇，不宣稱皆為引用論文原本使用的指標。

2026-10-15 修訂：依使用者決定，取消 multiplicity 正確率，也不要求逐 SNV multiplicity 真值或 MAP multiplicity 輸出。保留 PhyClone 將不同 multiplicity／genotype 情況納入 likelihood 並邊際化的機制；C2／C3 的效果透過 CCF 與祖先關係等其餘指標評估。

## 1. 第一版採用的指標

| 輸出 | 指標 | 評估單位／分母 | 真值需求 |
|---|---|---|---|
| 祖先關係 | AD F-score | 共同可評估 SNV 的有向祖先—後代配對 | 完整已知樹與 SNV assignment，或明確限定的獨立參考關係 |
| 突變分群 | V-measure | 共同可評估 SNV；比較 mutation-to-node partition | SNV 的真實群集；不比較任意 clone ID 數字 |
| CCF | MAE | 已知真值且有預測的 SNV × sample | 含所有後代的 mutation-carrier CCF；不是 exclusive clone fraction 或 VAF |
| 局部關係 | 四類 confusion matrix | 每 sample 的固定合格 SNV pair，一對只計一次 | 由獨立真樹／assignment 得到 same、ancestor、descendant、branch |
| 資訊可用範圍 | 合格／informative pair 數與比例 | 同一份固定候選 pair 清單，並列各階段排除數 | 不需要樹真值；是可用性統計，不是正確率 |

第一版先不要求 RRE、LPR、RF／GRF、posterior calibration、CCF interval coverage 或 held-out predictive log score。這些列為後續擴充；目前 MAP CCF 輸出沒有區間，不能據此計算 interval coverage。

2026-10-18 新增：**SMC-Het 相容分數**（sc1A–sc3B，§2.7）列為附加驗證。它用來和 SMC-Het DREAM Challenge 的 31 個方法放在同一尺度比較，不取代上表的主要指標。

## 2. 共同評分母體與計算方式

### 2.1 評分母體

每個 trial 在比較方法前凍結 `evaluation_mutations`、`evaluation_samples`、候選／合格 pair 清單與 truth 版本。先依真值與共同 QC 決定母體，不依某方法成功輸出的項目重新挑選。

先核對 mutation ID、sample ID、reference build。以 SNV ID 對齊 assignment／CCF，不需把推估 clone 編號硬對到真實 clone 編號。所有方法使用相同母體；缺少預測另列 `missing_prediction`，不能只刪掉失敗項再宣稱表現提升。

### 2.2 AD F-score 與 V-measure

AD 的真值配對集合與預測配對集合都包含跨多層的祖先關係，不包含同 node，也不是只計直接親子邊：

```text
AD_F1 = 2 * TP / (2 * TP + FP + FN)
```

AD F-score 使用選定的單棵最高分樹。若缺少任一評分 SNV 的有效 assignment，主要完整母體 AD／V 記為 `NA: incomplete_prediction`；可另外提供清楚標示的共同子集診斷，但不能取代主要結果。若 AD 的分母為 0，記為 `NA: no_ancestral_pairs`，不填 0 或 1。

V-measure 使用同一批 SNV 的 partition，沿用 PhyClone 論文的 homogeneity／completeness 定義。空集合為 `NA`；非空、兩邊皆只有一群時為 1。不同 clone ID 名稱不影響分數。

另分層報告 AD：全部配對、具有合格 linkage 的配對、其餘配對。後兩組各以固定的無向 SNV pair 清單選取兩個有向關係，不依預測拓樸改變分組；每組同報 pair 數與 TP／FP／FN。

樹的 AD 分層使用各 sample 合格 pair 的聯集，同一 SNV pair 不因多 sample 重複計分。pair QC 與四類矩陣則保留 sample 維度，與各 sample 的分子觀測對應；兩種分母分開標示。固定預分群時 V-measure 可能不變，應如實報告。

### 2.3 CCF MAE

```text
CCF_MAE = sum(abs(predicted_ccf - true_ccf)) / n_scored_mutation_samples
```

CCF 範圍為 0–1，以腫瘤細胞為分母，包含攜帶該突變的所有後代。每個 SNV × sample 等權，會使含較多 SNV 的 clone 權重較大，結果中需註明此定義。不以純度、total VAF 或 nominal `tX_nY` 代替 CCF 真值。

每個方法同報 `n_truth_available`、`n_scored`、`n_missing_prediction`、`n_invalid_prediction`。超出 0–1 的預測列為 invalid，不自行截斷；只有所有有真值項目都有有效預測時，才能標記為完整母體 MAE。分母為 0 時為 `NA`。

### 2.4 Multiplicity 在 likelihood 中的角色（不計分）

```text
L_i(f) = sum_g pi_i(g) * P(reads_i | f, g, CN, purity, phase)
```

`g` 包含 multiplicity 與 SNV／CNA 時序等 genotype 假設，`pi_i(g)` 為其權重，`f` 為 CCF；phase 為新增特徵啟用時的條件資訊。實作用 logsumexp 計算各假設的加權總和，沿用 PhyClone 的 genotype 邊際化。

C2 可以利用 HP／allele-specific CN 調整候選 genotype 與權重，C3 以這些假設計算 phased／unphased 觀測的 likelihood。無 HP 資訊時保留原本的候選與 likelihood 行為；不能因取消評估指標而固定所有 SNV 的 multiplicity 為 1，或刪去此潛在變數。

第一版不計算 multiplicity accuracy／error／calibration，也不要求回推每個 SNV 的 MAP multiplicity。候選集合與權重可作選用模型診斷，不列為評估完成條件；對模型效果的比較使用本文件其餘指標。

### 2.5 四類關係 confusion matrix

每對以固定 mutation ID 排序成 `(i, j)`，方向定義如下：

| 類別 | 定義 |
|---|---|
| same | i、j 指派到同一 node |
| ancestor | i 所在 node 是 j 所在 node 的祖先，包含跨多層關係 |
| descendant | j 所在 node 是 i 所在 node 的祖先 |
| branch | 兩者不同 node，且互不為祖先 |

矩陣 row 為 truth，column 為 prediction，順序固定為 `same, ancestor, descendant, branch`。輸出原始計數與每個 truth 類別的 support；row-normalized 矩陣只作附加顯示，support 為 0 的 row 記為 `NA`。

缺少／無法判定的預測另外列數，不自動算 branch；缺少獨立 relation truth 的 pair 不能進入正確率矩陣。矩陣另外標示完整性，避免只呈現成功預測的配對。第一版保留整張矩陣，不以一個總 accuracy 掩蓋特定類別的錯誤。

### 2.6 Pair 可用比例

在方法比較前，從固定 SNV set、sample 與預先宣告的距離窗建立候選 pair 清單；距離窗、read／base filters 與最小共覆蓋門檻寫入評估設定，所有方法共用。pair key 為 `(sample, chrom, mutation_i, mutation_j)`；多條 read 或多種觀測型態都不能把同一對重複計數。

合格 pair 須符合 `plan.md` §4.5：同 PS、同 HP、clonal CN 且該 HP 的 `C_h=1`、無跨 CN breakpoint，以及符合 primary alignment 與 base-call 篩選的共同覆蓋 reads。以相同上游觀測與 QC 決定 eligibility，不使用某方法推得的 relation 選 pair。模擬另以真實 CN 分層檢查 QC 誤納情形。

```text
eligible_pair_fraction = n_eligible_pairs / n_candidate_pairs
informative_pair_fraction = n_informative_pairs / n_candidate_pairs
informative_given_eligible = n_informative_pairs / n_eligible_pairs
```

`informative` 在此只表示合格 pair 有至少一條帶 ALT 的共同覆蓋 read，即 `n11+n10+n01 > 0`；不表示已能唯一決定關係。另報這三格的有效深度分布，只有 `11` 或沒有 `11` 都不能直接變成確定的 relation truth。

每項比例同報 numerator／denominator；分母為 0 時為 `NA`。排除流程固定順序並逐階計數，將無 phase、HP 不確定、CN 不合格、跨 breakpoint、coverage 不足等原因保留下來。

### 2.7 SMC-Het 相容分數（附加驗證）

**目的。** 用 SMC-Het 的官方定義計分，讓 PhyClone 和本 repo 的新增特徵能和 SMC-Het 的受測方法直接比較（[M07 筆記](research/tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/README.md)）。PhyClone 不在 SMC-Het 的受測方法中。本節是附加驗證；§2.2–2.6 仍是主要結果。

**依據。** 公式依官方評分程式 [uclahs-cds/tool-SMCHet-scoring](https://github.com/uclahs-cds/tool-SMCHet-scoring)（commit `fa67302`，2025-07-14，Apache-2.0，Python 2）的 `smc_het_eval/SMCScoring.py`。論文 Methods 只有摘要；兩者不一致時以程式為準，並在下表註明。

#### 2.7.1 七項分數與 PhyClone 輸出的對應

| 項目 | 評估什麼 | 分數（官方程式） | PhyClone 要提供的輸出 |
|---|---|---|---|
| sc1A | purity | `1 − |truth − pred|`（`calculate1A`） | **PhyClone 不推論 purity**，只把它當輸入。記為 `NA: purity_not_inferred`。若改報上游 purity 估計器的分數，`method` 欄寫該估計器，不寫 PhyClone |
| sc1B | clone 數 | `(L + 1 − min(L + 1, |pred − L|)) / (L + 1)`（`calculate1B`） | MAP 樹的非空 node 數。計數規則（是否含 clonal node）以官方 truth 檔的定義對齊後固定 |
| sc1C | CP 分布 | 依 SNV 數展開兩邊的 CP 後排序比對，取 `1 − mean|Δ|`；原始版與縮放版取較大值（`calculate1C`）。論文稱為 `1 − EMD` | 每個 node 一列：`cluster_id, n_snv, CP`。官方 validator 最多接受 10 列 |
| sc2A | 硬分群 | normalized JS divergence 和 normalized AUPR 的平均，加 pseudo count（`om_calculate2A`、`calculate2`） | MAP 樹的 SNV→node 指派，cluster ID 從 1 連續編號 |
| sc2B | 軟分群 | 同 sc2A，但輸入是 co-clustering 機率矩陣 | posterior trace 中 burn-in 之後，i、j 同 node 的樣本比例 |
| sc3A | 硬 phylogeny | 見 §2.7.2 | MAP 樹的 `node, parent` 表；root 寫 0 |
| sc3B | 軟 phylogeny | 見 §2.7.2 | 同 sc2B 的 co-clustering 矩陣，加上 AD 機率矩陣：i 所在 node 是 j 所在 node 祖先的樣本比例 |

**sc1C 的 CP 尺度。** CP 是 CCF，還是 purity×CCF，要先用官方 truth 檔確認，確認後寫進 manifest。未確認前，sc1C 記為 `NA: cp_scale_unverified`。不可用 VAF 代替。

**sc1C 超過 10 群。** 官方 validator 會拒收。記為 `invalid: too_many_clusters`，不自行合併 node。本 repo 的重新實作可以另算不設上限的版本，但要標成 `non_official`，不能和 SMC-Het 排名混在一起。

**多 sample。** SMC-Het 是 single-sample 設計。sc1A、sc1C 依 sample 分開計分。sc1B、sc2、sc3 只看 SNV 指派和樹，不依 sample 重複計分。

**forest。** PhyClone 可能輸出多個 root。每個 root 的 parent 都寫 0。

#### 2.7.2 sc3 的計算

每一對 SNV `(i, j)` 建四個 N×N 矩陣：

```text
CCM[i,j] = 1  若 i、j 在同一 node
AD[i,j]  = 1  若 i 所在 node 是 j 所在 node 的祖先（含跨多層）
ADᵀ      = AD 的轉置
C        = 1 − CCM − AD − ADᵀ          # cousin：不同 node 且互不為祖先
M        = [CCM | AD | ADᵀ | C]        # 橫向串接成 N × 4N
```

軟版本（sc3B）用 posterior 機率代替 0/1。官方 validator 要求 `CCM` 對角線為 1、`AD` 對角線為 0、`AD + ADᵀ + CCM ≤ 1`。

```text
raw   = Pearson(M_pred, M_truth)
worst = min(Pearson(M_truth, M_one), Pearson(M_truth, M_n))
        # M_one：所有 SNV 同一群（CCM=1, AD=0）
        # M_n：每個 SNV 自成一群、互為 cousin（CCM=I, AD=0）
score = max(0, ((raw − worst) / (1 − worst) + 1) / 2)
```

**解讀。**
- 完美預測的 score=1。
- 兩個極端解中**較差的那一個** score 正好是 0.5，另一個 ≥0.5。所以 score 的有效下限約 0.5，不是 0。比 0.5 低表示比最差的極端解還差。
- **sc3 對 topology 錯誤不敏感。** 在 10 個 SNV、三個 node 的手算例子中，真樹是 A→B、A→C（branching）。預測成 A→B→C（linear）時，score 仍有 0.875；單一 cluster 解是 0.542（2026-10-18 以臨時腳本依上式重算，不是官方程式輸出；腳本未存入 repo）。原因是 same 和多數 ancestor 配對仍然正確，只有 B、C 之間的配對錯。
- 因此 branching 和 linear 的區分不能只看 sc3，必須同時看 §2.2 的 AD F-score 和 §2.5 的 branch 列。論文表中的分數又做了跨方法 min–max 正規化（每個 {tumor, subchallenge} 內，最差的方法為 0、最好的方法為 1）。本 repo 主要報上式的原始 score；只有和一組固定方法同時比較時，才另報 min–max 版本，並列出參與正規化的方法清單。

**與 §2.5 的關係。** `CCM`、`AD`、`ADᵀ`、`C` 分別對應 same、ancestor、descendant、branch。差別有兩點：
- sc3 用**全部** SNV pair，並把結果壓成一個相關係數。
- §2.5 只用合格 pair，並保留四乘四的計數。

兩者分開報告，不互相替代。

#### 2.7.3 評分母體：採用 SMC-Het 的 FN／FP 規則

本節是 §2.1「缺少預測記為 NA」的明確例外，目的是和 SMC-Het 的結果可比：
- **false negative**：truth 有、預測沒有的 SNV，加進一個額外 cluster，`CP=0`，parent 為 0（官方規則）。PhyClone 會移除 `major_cn=0` 的 SNV，以及沒有出現在所有 sample 的 SNV，這些都屬於此類。
- **outlier**：PhyClone 判為 outlier 的 SNV 不在樹上，也用同一個額外 cluster 處理。
- **false positive**：預測有、truth 沒有的 SNV，在計分前排除。

每個 trial 同報 `n_fn_added`、`n_outlier_added`、`n_fp_removed`。主要母體（§2.1）的 AD／V 結果仍依原規則記 NA，不因本節而改變。

#### 2.7.4 規模與數值

- N 個 SNV 的 `M` 有 4N² 個元素。N=10,000 時，單一 float64 矩陣約 3.2 GB。
- N 太大時，使用官方的 `--approx <fraction> <iterations>` 子抽樣，並把 fraction、iteration 數和 `--approx_seed` 寫進 manifest。子抽樣的分數標成 `approx`。
- hard 版本的矩陣在 cluster 區塊內是常數，可以用區塊計數精確算出 Pearson，不必展開 N×N（推論）。若本 repo 自行實作這個算法，必須先通過 §5 的一致性驗收。

#### 2.7.5 適用資料

| 資料 | 能否計分 | 說明 |
|---|---|---|
| SMC-Het 公開資料（Synapse syn2813581） | 可以 | 用官方 truth 檔和官方程式。參考基因組是 hs37d5（GRCh37） |
| 本 repo 自建模擬 | 可以 | truth 由生成器輸出，轉成官方格式。計分可以用官方程式或通過驗收的重新實作 |
| HCC1395 等真實資料 | 不可以 | 沒有完整 SNV assignment 真值，記為 `NA: truth_unavailable` |

## 3. 第一版比較實驗

主要設定：`baseline`、`+C2`、`+C3`、`+C4`、`+C2+C3+C4`。另外保留既有計畫的 `+C2+C3`，以接續 C4 的增量比較。

固定 mutations、clusters、CN、實測 purity、read partitions、seeds、chain 數與推理預算；全部使用第一版 no-outlier 設定。各方法都要提供可對齊的 CCF 預測；multiplicity 保留於 likelihood 內部，不要求額外點估計。

各新增特徵組共用 C0／C1 的萃取與輸入支援；`+C3` 等名稱表示只啟用該模型改動，不代表省略其必要前處理。baseline 使用相同原始觀測的 total counts，評估器仍保留同一份 pair QC 清單。

必要對照：打亂 pair 對應或注入 PS 內 phase switch，以及 coverage／callability／錯誤率相同的 short-span 對照。保持一整個 PS 內 HP1／HP2 及其相關 CN 一起對調只是等價改名，應作不變性檢查，不能當作破壞 phase 的負對照。

模擬至少分層：正確 CN、minor CN ±1、不同 tagging recall／allele bias、低 pair coverage、phase switch。第一版 C4 主結果限 `C_h=1`；amplified／subclonal CN、mutation loss 列為模型範圍外 stress test，不混入主要平均。

獨立模擬資料集／生物樣本是比較單位，seeds 是同一資料集的推理重複。先保留逐 trial／seed 結果，再報每個資料集的 seed 彙整與相對 baseline 差值；不把 reads、pairs 或 seeds 當成獨立病人數。失敗 trial 同報失敗率，不將 `NA` 填成完美分數或靜默刪除。

## 4. 真值與獨立性

模擬的生成樹、assignment、CCF 與方法輸入分開保存，評分時才讀取。生成器若需指定 multiplicity，該值僅作生成設定與 provenance 保存，不列為本版的評估答案或評分輸入。長讀觀測可以參與建樹，但不能再把同一批觀測當獨立 relation truth。

HCC1395 golden tree 缺少完整 SNV assignment，且不是獨立完整真樹。現有 HCC1395 pilot 先報 pair 可用性與候選樹相容性；缺少相應真值的 AD／V、CCF MAE、relation confusion matrix 記為 `NA: truth_unavailable`，不補造答案。Multiplicity 正確率已取消，不輸出該評分欄位。

若另報獨立 read consistency，須在 tagging／feature extraction 前切分 molecules／位點，必要時 retag 或遮罩 held-out somatic variants。某條 read 衍生的所有位點與 pairs 必須留在同一側；存在共享 molecules 的位點／PS 須整組處理，不能只切最後的 pair 表。

## 5. 預定輸出與完成條件

以下是後續評分程式的輸出規格，目前尚未產生這些檔案：

| 檔名 | 必要內容 |
|---|---|
| `evaluation_manifest.json` | 規格版本、trial／資料生成 seed、推理 seed、方法版本、truth／輸入 checksum、固定評分母體、QC／pair 門檻、CN／purity／outlier 設定 |
| `metrics.tsv` | trial、seed、方法、分層、metric、value、numerator／denominator（適用時）、評分／缺失／invalid 數、完整性與 NA 原因 |
| `relation_confusion.tsv` | trial、seed、方法、分層、truth_relation、predicted_relation、count；即使 count=0 仍輸出四乘四格 |
| `pair_qc.tsv` | sample、候選／合格／informative pair 數、各階段排除數、三項比例與有效深度分布 |
| `smchet_scores.tsv` | trial、seed、方法、sample（sc1A／sc1C）、subchallenge、raw score、min–max score（有時）、`official`／`non_official`／`approx` 標記、評分程式 commit、`n_fn_added`、`n_outlier_added`、`n_fp_removed`、NA／invalid 原因 |

完成條件：各方法能以相同母體產出上述四類評估；完整預測且與已知真值一致時，AD／V 為 1（AD 有有效分母時）、CCF MAE 為 0、confusion matrix 僅有對角線計數；空母體與缺失真值依規格回報 `NA`。Multiplicity 的候選情況仍參與 likelihood，沒有 HP 欄位時須保留原本行為。這些是未來實作的驗收條件，不是已通過的測試。

SMC-Het 相容分數（§2.7）另有三項驗收條件：
- 完美預測的 sc1A／sc1B／sc1C／sc2A／sc3A 都是 1。
- 單一 cluster 解和 N-cluster 解中，較差的那一個 sc3A 是 0.5，另一個 ≥0.5。
- 若本 repo 重新實作評分，對同一組 SMC-Het 預測檔的分數必須和官方程式一致，差異在 1e-6 以內。

一致性驗收要用官方程式的測試資料（`smc_het_eval/test_SMCScoring.py`）和至少一個 SMC-Het 公開腫瘤。

## 6. 來源

- [實作與實驗計畫](plan.md)：§4.0、§4.5、§4.7、§5。
- [PhyClone 評估指標](research/phyclone_research/notes/zh-TW/03_EXPERIMENTS_RESULTS.md)：§「指標與統計方法」，AD／V 的原文依據。
- [文獻對本 repo 的改進方案](research/tumor_phylogeny_2026/REPO_IMPROVEMENTS.md)：§4–6，分層評估、ablation 與資訊洩漏。
- [B04 肺癌 long-read phasing](research/tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md)：局部 mutation partial order 的研究動機，不提供本規格全部指標的既有實作。
- [M07 SMC-Het benchmark](research/tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/README.md)：§2.7 的論文依據（Salcedo et al., *Nat Biotechnol* 2024，Methods「Scoring metrics」「Scoring and ranking」）。
- [SMC-Het 官方評分程式](https://github.com/uclahs-cds/tool-SMCHet-scoring)：commit `fa67302`；`SMCScoring.py` 的 `calculate1A`、`calculate1B`、`calculate1C`、`calculate2`、`calculate3Final`、`validate3A`、`validate3B`，以及 `scoring_harness_optimized.py` 的 `om_calculate2A`。
- [實驗室依輸出類型驗證規範](/big8_disk/liaoyoyo2001/Knowledge/06_workflows/validation-by-output-type.md)：L30–46、L86–96、L138–154，分母、HP 語意與獨立驗證；`status: lab-canonical`。
