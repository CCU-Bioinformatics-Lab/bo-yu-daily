# PhyClone 測試程式重跑 FS-CRP 模擬資料

日期：2026-10-21。

## 結論

- **能正確輸出。** `fscrp.py` 與 `sim_data_on_tree.py` 照 FS-CRP_Loss 的設定重跑，產生的資料通過 6 項規則檢查（100／100 份）。PhyClone 能讀入這份資料並輸出樹。
- **但兩個程式本身不寫檔。** 要得到資料集，需要一支外包腳本把記憶體裡的結果寫成作者的檔案格式（`tools/phyclone_sim_rerun.py`）。
- **作者的生成程式和公開的測試程式不是同一版。** 有兩點不同：
  1. 拷貝數拆分點的範圍：作者資料符合「0 到總拷貝數，含兩端」；公開程式是「0 到總拷貝數減 1」。〔實測〕
  2. 中國餐廳過程的 α：作者平均 8.41 群，α＝1 只有 6.8 群。用 α 約 1.25–1.27 才吻合。〔推論，α 沒有記錄〕
- 把這兩點改掉後，所有比較的統計量都和作者資料吻合。這支持「作者用的是相近但未公開的版本」。〔推論〕

## 資料

- 作者資料：`/big8_disk/boyu114/phyclone_dataset/FS-CRP_Loss/data_archive/loss_prop_0.0_run{0..99}/ground_truth/`。只用 `loss_prop_0.0`，因為測試程式沒有「突變丟失」這一步。
- 程式：PhyClone submodule commit `2738324` 的 `phyclone/tests/utilities/fscrp.py` 與 `sim_data_on_tree.py`，未修改。
- 輸出：`/big8_disk/boyu114/phyclone_dataset/PhyClone_testcode_rerun/`

| 子目錄 | 內容 |
|---|---|
| `single/run0/` | 1 份重跑資料，另含 `phyclone_naive/`，是 PhyClone 的輸入、trace 與 map 樹 |
| `reps_alpha1/run{0..99}/` | 公開程式原樣，α＝1，100 份 |
| `hypothesis_alpha1.25_cnx_inclusive/run{0..99}/` | 假說版本：α＝1.25，加上拷貝數拆分點含兩端，100 份 |

每份資料有三個檔：

- `ground_truth/data.tsv`：欄位和作者相同，17 欄。
- `ground_truth/tree.json`：格式和作者相同。
- `phyclone_input.tsv`：只有 PhyClone 讀的 9 欄，不含答案欄。

## 做法

1. **環境**：本機只有 Python 3.10。PhyClone 要求 3.12 以上，以及 `networkx>=3.6.1`。
   - 用 `~/venvs/phyclone`，裝 networkx 3.4.2、numpy 2.2.6。
   - 用 `PYTHONPATH` 直接載入 submodule，不安裝 PhyClone。
2. **反推作者設定**（從 100 份作者資料）：600 個 SNV、8 個 sample、深度 1000、purity 1.0、總拷貝數 2–6、較少那邊至少 1 份。
3. **重跑**：

   ```
   PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python tools/phyclone_sim_rerun.py OUT --reps 100 [--alpha 1.25 --cn-x-inclusive]
   ```

   外包腳本只記錄中間值，不改程式行為。亂數呼叫順序和原程式相同，並逐筆核對記錄值和程式物件裡的 read 數。
4. **規則檢查與分布比較**：

   ```
   ~/venvs/phyclone/bin/python tools/phyclone_sim_check.py OUT --out OUT/compare_vs_author.tsv
   ```

5. **PhyClone 讀取測試**：在 `single/run0` 上照作者的 `phyclone_naive` 設定跑一次（真值分群當 cluster 檔，`-b 100 -n 500 --num-chains 1 --seed 1`），再跑 `map`。

## 結果

### 規則檢查（通過份數 / 份數）

| 規則 | 公開程式 α＝1 | 假說版本 | 作者資料 |
|---|---|---|---|
| read 總數固定（深度） | 100/100 | 100/100 | 100/100 |
| 用公式重算的 mu 和記錄值相同 | 100/100 | 100/100 | 100/100 |
| genotype 符合「突變在拷貝數改變前或後」的規則 | 100/100 | 100/100 | 100/100 |
| ccf 欄等於該群的 cellular_prev | 100/100 | 100/100 | 100/100 |
| 一個 root、CCF＝自己＋後代、root CCF＝1 | 100/100 | 100/100 | 100/100 |
| parent 的 SNV 數不少於 child | 100/100 | 100/100 | 100/100 |

### 分布比較（100 份的平均，括號是 5%–95%）

| 統計量 | 公開程式 α＝1 | 假說版本 | 作者資料 |
|---|---|---|---|
| 群數 | 6.80 [3, 11] | 7.94 [4, 13] | 8.41 [4, 14] |
| root 是最大群 | 1.00 | 1.00 | 1.00 |
| root 的 child 數 | 1.87 | 2.00 | 1.88 |
| 突變在拷貝數改變之前的比例 | 0.600 | 0.601 | 0.601 |
| 較少那邊是 1 份的比例 | **0.771** | 0.807 | 0.807 |
| 平均總拷貝數 | 4.00 | 4.00 | 4.00 |
| VAF 中位數 | 0.278 | 0.259 | 0.259 |

完整表：`compare_published_code_alpha1.tsv`、`compare_hypothesis_alpha1.25_cnx_inclusive.tsv`。

### 拷貝數拆分點：作者資料對兩種規則

| 總拷貝數 | 作者資料（較少那邊 1／2／3 份） | 含兩端的規則 | 公開程式 |
|---|---|---|---|
| 4 | 0.800／0.200 | 4/5、1/5 | 3/4、1/4 |
| 5 | 0.664／0.336 | 4/6、2/6 | 3/5、2/5 |
| 6 | 0.572／0.286／0.143 | 4/7、2/7、1/7 | 3/6、2/6、1/6 |

`sim_data_on_tree.py` 的 `x = rng.integers(0, total_cn)` 從 2024-11-26 進 repo（commit `d31071d`）後沒有改過。

### PhyClone 讀取測試

- `phyclone run` 與 `phyclone map` 都正常結束，用時 24 秒。
- map 樹對了 8 條真值邊中的 7 條。錯的是只有 3 個 SNV 的 cluster 8：真值 parent 是 cluster 7，推出來是 cluster 1。這只是一次短鏈，不代表 PhyClone 的準確度。

### 格式差異

作者每棵 `tree.json` 都多一個 `id = -1` 的節點。它沒有 SNV、沒有比例，也沒有連到任何邊。重跑資料沒有這個節點。它可能是 PhyClone 的 outlier 佔位節點。〔推論〕

## 限制

- 執行環境不是 PhyClone 要求的版本：Python 3.10、networkx 3.4.2。程式全部跑完，規則也全部通過，但沒有在 3.12 上對照。
- α 只用群數平均反推，沒有唯一解。群數的差異（7.94 對 8.41）在 100 份的抽樣變異內，但沒有做檢定。
- 測試程式沒有「突變丟失」，所以只能比 `loss_prop_0.0`。
- 作者資料無法逐筆重現：種子不明，版本也不同。
