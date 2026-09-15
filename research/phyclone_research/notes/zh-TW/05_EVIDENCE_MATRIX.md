# 證據矩陣

`—` 表示該來源並非適合此主張的證據類型，不一定代表該主張為假。除非明確標示為 0.7.0，對版本敏感的實作欄位均指目前簽出版本 的 0.8.0。

| 主張 | 論文正文 | 補充資料 | XLSX | 程式碼 | 類型 | 信心程度 |
|---|---|---|---|---|---|---|
| 僅靠整體腫瘤樣本只能部分辨識克隆祖先關係；後驗不確定性具有科學意義 | Introduction pp.1–2 | Figs.S5–S7 pp.16–18 說明排序／樹狀結構的歧義 | — | trace 保留多個狀態 | [明示 STATED] | HIGH（高） |
| FS-CRP 聯合建立未知突變分割及有根森林／樹的模型 | §2.1 pp.2–3 | S1.3 pp.2–3 | — | `tree/distributions.py:43-65` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| 樹內突變的 CCF，是以該節點為根的整個子樹（包含該節點本身）中，各克隆專有盛行率的總和 | §2.2 p.3 | S1.3 p.3 | — | `tree/tree_node.py:59-69`；`process_trace/map.py:127-157` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| 等位基因概似透過 PyClone 基因型混合模型納入讀序數、CN 與純度 | §2.2 p.3 | S1.1–S1.2 pp.1–2 | — | `utils/math_utils.py:179-244`；`data/pyclone.py:299-403` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| CN 與純度為固定輸入，不由模型推論 | 由 §2/Fig.1 暗示 | S1.1 pp.1–2 | — | schemas 與 `data/pyclone.py` | [實作 IMPLEMENTED]/[推論 INFERRED] | HIGH（高） |
| 預先分群的叢集不可拆分，但可彼此合併 | §2.2.2 p.3 | — | §2.4.2 說明共同的前處理 | `data/pyclone.py:82-115` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| 將盛行率邊際化，可從樹狀結構抽樣中移除連續變數 | §2.2.1 p.3；Discussion p.8 | S1.4–S1.5 pp.4–5 | 後驗指標使用邊際化分數 | `tree/utils.py`；`tree/distributions.py:151-163` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| DP 的詳細成本為 `O(V(NL+CSL^2))`，一般不能只寫成 `O(V^2)` | §2.2.1 p.3 的簡略寫法 | S1.5 p.5 | — | `tree/utils.py:28-68` 中逐樣本的網格卷積 | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高）；已解決措辭衝突 |
| 最終分數強烈偏好單一次根節點（`C=1000`） | 未詳述 | S1.3.1 pp.3–4 | — | `tree/distributions.py:12-14,67-121` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| 輔助排序 PG 內部的 semi-adapted 由下而上 SMC，是核心抽樣器 | §2.3–§2.3.1 pp.3–4 | S1.6–S1.6.3 pp.6–7 | 有說明 基準測試設定，但非原始資料 | `smc/kernels/semi_adapted.py`；`mcmc/particle_gibbs.py` | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高） |
| 離群值狀態可容納違反繼承限制的情形，但不會推論發生流失的邊 | §2.2.3 p.3 | S1.7 pp.7–8 | 流失消融實驗 S4/S19；HGSOC S10/S11 | bucket `-1`，無 loss-edge 變數 | [明示 STATED] + [推論 INFERRED] 邊界 | HIGH（高） |
| 論文發表的離群值積分等同於目前程式碼 | §2.2.3 中的一重積分 | S1.7 中的一重積分 | — | 兩個版本的 `data/base.py:29-34` 均為三角形雙重加總 | [推論 INFERRED]—REJECTED（駁回） | 「等同性缺乏支持」的判斷為 HIGH（高）；不一致尚未解決 |
| 資料導向的 缺失先驗 使用染色體集中情形、10,000 次抽樣，以及 0.0001/0.4 的先驗 | benchmark 選項 §2.4.2 p.5 | S1.7.1 p.8 | — | `cluster_outlier_probabilities.py:24-151`，另有額外篩選條件 | [明示 STATED]/[實作 IMPLEMENTED] | HIGH（高）；細節為 APPROXIMATE（近似） |
| 啟用離群值的 PhyClone 可抵抗模擬流失 | §3.1/Fig.2 p.6 | — | S4 `A2:M601`；S19 `A2:F5` | 功能存在；缺少實驗 pipeline | [明示 STATED] | 在帶偏差的消融實驗範圍內為 HIGH（高） |
| TSSB-Low：PhyClone 在 AD 指標上優於所有方法，且 PhyloWGS 慢得多 | §3.2/Fig.3 pp.6–7 | Figs.S10–S11 pp.21–22 | S2/S15/S16 | 缺少 基準測試流程 | [明示 STATED] | HIGH（高） |
| 在 TSSB-High/Pairtree/CONIPHER-NN 的 AD 指標中，沒有任何方法顯著優於 PhyClone | §3.3/Fig.4 pp.7–8 | Fig.S10/S12–13 | S18/S21/S23 | — | [明示 STATED] | HIGH（高）；S23 有一項原始資料方向衝突，但不影響決策 |
| CONIPHER 在 TSSB-High 的 V-measure 指標上顯著優於 PhyClone | §3.3 p.7 | — | S18 row 15：`p=2.90e-8` | — | [明示 STATED] | HIGH（高） |
| CONIPHER-noise 的 AD 頂尖群組為 PhyClone/CONIPHER/fastBE | §3.4/Fig.5 pp.7–8 | — | S7/S25 | — | [明示 STATED] | HIGH（高） |
| 在 CN-error 合併排名中，AD 指標偏向 PhyClone；論文報告指出不同擾動程度的影響極小，但由於 S14 缺少錯誤程度標記，無法獨立重建並驗證各擾動條件下影響近乎不變的模式 | §3.4 p.7 | Fig.S14 p.25 | S14/S27 支持合併排名，但缺少錯誤程度 | — | 合併結果為 [明示 STATED]；趨勢為 [推論 INFERRED]/UNRESOLVED（未釐清） | MEDIUM（中） |
| PhyClone 最能重建 HGSOC 病人 3，並排除兩個已流失的叢集 | §3.5/Fig.6 pp.8–9 | Table S1 p.27 | S10/S11 精確指標 | 僅有離群值結構；無實驗資料 | [明示 STATED] | 對此個案為 HIGH（高），對泛化則為 LOW（低） |
| 目前匯出的盛行率是後驗平均值／區間 | 正文 §2 p.2 指出可透過 MAP 或抽樣（sampling） 還原 | — | — | `process_trace/map.py` 僅有 max-product 網格回溯 | [推論 INFERRED]—REJECTED（駁回） | HIGH（高） |
| 目前 0.8.0 的 bootstrap＋離群值提議具有內部一致性 | — | S1.6.2 中的一般 bootstrap 說明 | — | 抽樣機率為 0.1/0.35/0.55，記錄的機率則為 0.1/0.45/0.45 | [推論 INFERRED]—REJECTED（駁回） | HIGH（高）；目前版本的迴歸問題 |
| 子樹 PG 的形式正確性已獲驗證 | — | S1.6.4 p.7 宣稱有校正 | — | 0.7.0/0.8.0 均有 TODO | [推論 INFERRED]—REJECTED（駁回） | MEDIUM-HIGH（中高）；UNRESOLVED（未釐清） |
| 目前實際操作的預設值等同於論文基準測試 設定 | benchmark 0.7.0 §2.4.2 p.5 | — | — | 0.8.0 CLI/API 不同 | [推論 INFERRED]—REJECTED（駁回） | HIGH（高） |
| PhyClone 在所有情況下都較優越，且計算成本低廉 | 沒有這種範圍明確的主張 | — | 準確度的例外情形與資源成本 | 執行時間結構／成本 | [推論 INFERRED]—REJECTED（駁回） | HIGH（高） |

## 衝突登錄表

### 已解決

1. **虛擬根節點維度：** 加入根節點後，補充資料的 `|b|=|V|` 與正文的 `|b|+1=|V|` 衝突；程式碼包含根節點質量。判定為補充資料的符號錯誤。
2. **複雜度：** 採用補充資料的 `O(V(NL+CSL²))`；正文的 `O(V²)` 是不完整的簡略寫法。
3. **Bootstrap regression 的來源：** 0.8.0 的抽樣／log probabilities 不一致；0.7.0 則一致，而論文基準測試 使用 semi-adapted。判定為目前版本的迴歸問題，而非論文結果背後的機制。
4. **「顯著」門檻：** 所有 worksheet flags 均與正文明確指定的 `p<0.01` 一致；不需要未明示的多重比較校正。
5. **Pairtree 數量：** 576 可由省略 `K=30/100` 且 `M=1/3` 的組合解釋；論文並未說明這項排除規則。

### 尚未解決

1. **離群值邊際化：** 論文為單一均勻積分，但兩個版本的程式碼皆為三角形雙重加總；很可能是實作不一致。
2. **子樹 PG：** 原始碼 TODO 質疑選取機率項（selection-probability term）；此路徑預設關閉。
3. **CONIPHER-NN 中 fastBE 相較於 PhyClone 的 AD：** 原始平均值的方向與 S23 row 8 衝突，但 `p=0.94951`，因此不顯著的結論維持不變。
4. **Friedman 精確 p-values：** 部分數值無法由可見的活頁簿儲存格精確重現；決策仍完全相同。
5. **CN-error 趨勢：** S14 缺少錯誤程度標記。
6. **Timeout／統計流程：** 儲存庫內不存在，因此懲罰方式是以代數推導，而非直接由程式碼讀取。
