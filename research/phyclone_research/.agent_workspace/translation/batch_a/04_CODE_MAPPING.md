# 論文至程式碼對照

受檢查的實作：PhyClone **0.8.0**，commit `27383246c1aff7b1d62c02662017bd61bfdfbc33`。論文實驗：**0.7.0**。`EXACT`（精確相符）容許論文明載的數值網格近似；若無充分理由判定等效，則保留 `POSSIBLE_MISMATCH`（可能不相符）。

| 論文概念 | 論文位置 | 原始碼檔案／函式 | 執行期行為 | 相符程度 |
|---|---|---|---|---|
| 主要整齊格式輸入 | 主文 §2／圖 1 第 2 頁 | `data/validator/PhyClone_schema.json`; `data/pyclone.py:197-280` | 驗證資料列；捨棄主要 CN 為零及資料不完整的突變；提供純度／錯誤率預設值 | EXACT + ADDITIONAL_IMPLEMENTATION_DETAIL（額外實作細節） |
| PyClone CN／純度 VAF | 補充資料 S1.1 第 1–2 頁 | `utils/math_utils.py:179-244`, `log_pyclone_*`; `data/pyclone.py:299-403` | 在 CCF 網格上使用三族群、CN 加權的基因型混合模型 | EXACT |
| 主要 CN 基因型先驗 | 補充資料 S1.2 第 2 頁 | `data/pyclone.py:324-352`, `get_major_cn_prior` | CNA 前／後候選使用相等權重 | EXACT |
| 預分群原子 | 主文 §2.2.2 第 3 頁 | `data/pyclone.py:82-115,184-194` | 將成員的對數網格相加；原子可以合併，但絕不拆分 | EXACT |
| CRP 分割先驗 | 主文 §2.1–2.2 第 2–3 頁；補充資料 S1.3 | `tree/distributions.py:56-65` | `alpha^K prod (size-1)!`，省略與狀態無關的正規化常數 | EXACT |
| 虛擬根節點森林 | 主文 §2.1 第 2 頁；補充資料 S1.3 | `tree/tree.py:19-43`; `tree/distributions.py:43-54` | 明確的根節點；多個根節點子節點用來編碼森林；Cayley 項 | EXACT |
| 最終單一根節點偏好 | 補充資料 S1.3.1 第 3–4 頁 | `tree/distributions.py:12-14,67-121`; `tree/base.py:93-100` | `C=1000` 根節點懲罰與表示法重數修正 | EXACT + 額外細節 |
| Dirichlet 盛行率 | 主文 §2.1–2.2；補充資料 S1.3–S1.5 | `tree/base.py:27-35`; `tree/utils.py:7-25` | 均勻網格與累積積分實作 `kappa=1`；不支援任意 kappa | kappa=1 時為 EXACT；一般 kappa 為 PAPER_ONLY（僅見於論文） |
| 後代加總 CCF | 主文 §2.2 第 3 頁 | `tree/tree_node.py:35-69`; `tree/utils.py:39-57` | 子節點似然摺積施加父節點 ≥ 子節點總和的限制 | EXACT |
| 摺疊式似然 | 主文 §2.2.1 第 3 頁；補充資料 S1.4–S1.5 | `tree/tree_node.py:43-69`; `tree/utils.py:7-68`; `tree/distributions.py:151-163` | 有限網格的後序動態規劃；根節點完整質量固定為 1 | 如文中所述為 APPROXIMATE（近似相符） |
| 多樣本模型 | 主文 §2.2 第 3 頁；補充圖 S2 | `data/pyclone.py:375-403`; `tree/utils.py:39-57` | 共用樹／分割，各樣本的網格運算彼此獨立 | EXACT |
| SMC 目標／成長狀態 | 主文 §2.3 第 3–4 頁；補充資料 S1.6 第 6 頁 | `tree/tree_shell_node_adder.py`; `smc/kernels/base.py:46-75` | 加入既有根節點、在某個子集合上方建立新根節點，或指派為離群值 | EXACT |
| 半調適式 proposal | 補充資料 S1.6.2 第 6 頁 | `smc/kernels/semi_adapted.py:31-130` | 評分既有指派，並抽樣新根節點的子節點子集合 | EXACT；基準測試／預設路徑 |
| 完全調適式 proposal | 補充資料 S1.6.2 第 6 頁 | `smc/kernels/fully_adapted.py` | 列舉所有 `2^R` 個子集合 | EXACT |
| Bootstrap proposal | 補充資料 S1.6.2 第 6 頁 | `smc/kernels/bootstrap.py` | 類似先驗的隨機 proposal | 未使用離群值時為 EXACT；0.8.0 搭配離群值時為 POSSIBLE_MISMATCH |
| ESS／重抽樣 | 補充資料 S1.6／圖 S4 | `smc/swarm/swarm.py:21-61`; `smc/samplers/standard.py:22-44` | 穩定的正規化權重；在相對 ESS 門檻進行多項式重抽樣 | ADDITIONAL_IMPLEMENTATION_DETAIL |
| 容許順序 | 主文 §2.3.1 第 4 頁；補充資料 S1.6.3 第 7 頁 | `smc/utils.py:19-135` | 後代在父節點之前，並進行節點內洗牌與橋接洗牌（bridge shuffle） | EXACT |
| 整棵樹 Particle Gibbs | 主文 §2.3.1 第 4 頁 | `mcmc/particle_gibbs.py:8-49`; `smc/samplers/conditional.py` | 條件路徑，加上最後的加權粒子 | EXACT |
| 子樹 Particle Gibbs | 補充資料 S1.6.4 第 7 頁 | `mcmc/particle_gibbs.py:52-110` | 依突變加權選取根節點，並進行整棵樹修正 | POSSIBLE_MISMATCH：原始碼有 TODO；預設關閉 |
| 重新指派移動 | 主文 §2.3.2 第 4 頁 | `mcmc/gibbs_mh.py:7-66` | 將非單元素資料移至既有節點／離群值；節點數固定 | 行為為 EXACT；正確性有 TODO |
| 剪枝再嫁接 | 主文 §2.3.2 第 4 頁 | `mcmc/gibbs_mh.py:69-129` | 列舉新的連接位置，包含虛擬根節點 | EXACT |
| 二元離群值狀態 | 主文 §2.2.3 第 3 頁；補充資料 S1.7 | `tree/distributions.py:124-204`; tree outlier bucket `-1` | 將離群原子排除於樹之外，並套用先驗／獨立評分 | 結構上為 EXACT |
| 均勻離群值積分 | 同上 | `data/base.py:29-34` | 累積後再計算第二次網格平均，而非單一矩形積分 | 0.7.0 與 0.8.0 均為 POSSIBLE_MISMATCH |
| 資料導向的缺失先驗 | 補充資料 S1.7.1 第 8 頁 | `data/cluster_outlier_probabilities.py:24-151` | 幹系染色體虛無模型；最小叢集為 4，並加入 ratio>1 條件 | APPROXIMATE + 額外細節 |
| Alpha 重抽樣 | 補充資料 S2.2 第 9 頁 | `mcmc/concentration.py:11-60`; `run.py:292-313,382-392` | 選用的 Gamma 先驗輔助更新 | ADDITIONAL_IMPLEMENTATION_DETAIL |
| 快取／TreeHolder | 補充資料 S2.1–S2.2 第 9–10 頁 | `utils/cache.py`, `hashing_utils.py`, `tree_shell_node_adder.py`, kernels | 有界的摺積／樹／proposal 快取 | EXACT／額外細節 |
| 軌跡 | 主文輸出概覽第 2 頁 | `utils/save_hdf5.py` | HDF5 狀態、時間資訊、alpha、節點／離群值／根節點數 | ADDITIONAL_IMPLEMENTATION_DETAIL |
| MAP 樹 | 主文 §2.4.2 第 5 頁 | `process_trace/process_trace.py:27-58` | 儘管名稱為「joint-likelihood」，實際最大化納入先驗的 `log_p_one` | EXACT 意圖；命名注意事項 |
| 共識 | 主文的一般輸出主張 | `process_trace/consensus.py:81-111` | 相容演化支；預設效果相當於計數 × 最佳評分 | ADDITIONAL_IMPLEMENTATION_DETAIL |
| 盛行率復原 | 主文 §2 第 2 頁 | `process_trace/map.py:6-157` | 僅進行條件網格的最大乘積回溯 | MAP 為 EXACT；後驗抽樣為 PAPER_ONLY |
| 基準測試指標／統計 | 主文 §2.4.3 | 缺少 | 簽出版本中沒有 V/AD/RRE/LPR/Friedman/Nemenyi 流程 | PAPER_ONLY |

## 操作預設值

| 設定 | 已發表的基準測試 0.7.0 | 目前 0.8.0 CLI | 目前 0.8.0 直接呼叫 `run()` |
|---|---:|---:|---:|
| 鏈數 | 4 | 1 | 1 |
| 暖機期 | 100 | 1000 | 100 |
| 迭代次數 | 5000 | 10000 | 5000 |
| 粒子數 | 100 | 100 | 100 |
| 密度 | beta-binomial | beta-binomial | beta-binomial |
| 精度 | 未另行說明；0.7 CLI 為 400 | 400 | 1.0 |
| proposal | semi-adapted | semi-adapted | semi-adapted |
| 網格點數 | 0.7 預設為 101 | 101 | 101 |
| 全域離群值先驗 | 啟用缺失指派時，低／高為 0.0001/0.4 | 除非啟用，否則為 0 | 0 |
| 子樹 PG | 0.7 預設為 0 | 0 | 0 |

## 測試與驗證限制

[明示 STATED] 補充資料 S2.3 說明了三種 PG 核心函式（kernel）的精確小型後驗測試，以及對至少十棵樹使用 1,000,000 次 Dirichlet 重要性抽樣器（importance sampler）抽樣進行的邊際化比較（第 10–11 頁）。[實作 IMPLEMENTED] 相對應的測試模組確實存在。在此工作區中，`test_root_term` 的八項測試全數通過。其他選定模組無法在現有 Python 3.10 環境中完成收集，因為缺少必要套件（`numba`、`networkx`、`xxhash`）；儲存庫宣告需要 Python ≥3.12。任何匯入失敗都不會被視為演算法失敗。

## 目前使用時的警告

1. 在 0.8.0 搭配啟用的離群值使用 `bootstrap` 時，應先修正／測試抽樣機率 0.1/0.35/0.55 與所記錄機率 0.1/0.45/0.45 的不一致，再行使用。論文基準測試採用 semi-adapted，因此不受牽連。
2. 除非其 selection-probability TODO 已解決，否則應維持關閉子樹 PG。
3. 由於實作的離群值邊際量不符合論文發表的單一積分，應審慎解讀離群值後驗勝算。
4. 請明確指定 CLI／API 特有的預設值；最好傳入所有關鍵數值。
5. 執行前請驗證叢集／主要突變的一致性及純度／CN 欄位；程式碼有可能遺漏格式不正確資料或使其對位錯誤的邊界情況。
