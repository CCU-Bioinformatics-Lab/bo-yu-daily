# C4 composite likelihood 加權：交接計畫（2026-10-26）

新 session 從這裡開始。先讀本檔，再讀第 2 節列出的檔案。

## 1. 目標與判定

**問題：** C4 的 pair term 太重。〔實測，`lab_report/2026-10-25_c4_robustness/` 第 8 節〕
- pair term 的變動是 base log_p 的 6.8–33 倍（中位數 11.6）。
- 一條 read 平均被計入 2.4–4.0 個 pair，最多 105 個。C4 把每個 pair 當成獨立證據，所以訊號和錯誤都被重複計算。
- 一個鹼基錯誤可以罰到約 41 log 單位。這是失效模式 1（clone 被拆開）的主要來源。

**做法（composite likelihood 加權）：** pair term 整體乘上權重 w。

  log p(tree) = base log_p + w × Σ_pairs score(pair, relation)

- 理論依據：pairwise composite likelihood 的 pair 不獨立。常用的修正是除以每個觀測被重複使用的次數。〔推論；文獻依據未查〕
- w 的參考值：1／（每條 read 平均出現在幾個 pair）。12 個 sim 中是 0.25–0.42。

**要回答：**
1. w < 1 能不能減少兩種失效，同時保住 P2（直線樹排除）？
2. 從資料估的 w（`auto`）和固定 w 哪個比較好？

**判定（提案，可改）：** 和 w = 1（已有結果）比較。
- 改善：錯誤樹 > 0.5 的 run 數減少，clone 數眾數更接近收縮後的真值（3–4），而且 `c3_under_c4` 全部 < 0.1。
- 沒有改善：上述任一項變差，或 `c3_under_c4` ≥ 0.1。

## 2. 現況（commit 見 `git log`）

| 內容 | 位置 |
|---|---|
| C4 實作 | `tools/phyclone_pairs.py`（`relation_scores`、`PairTable`、`install`、`install_everywhere`） |
| CLI | `tools/phyclone_hp.py`：`--pairs`、`--hp-data`、`--segments`、`--pair-eps` |
| 穩健性實驗、w = 1 的結果 | `lab_report/2026-10-25_c4_robustness/README.md`（第 1–8 節）、`topology_summary.tsv` |
| 事後挑樹（不建議當主方法） | 同上第 7 節、`tools/c4_posthoc.py` |
| 權重診斷 | `tools/c4_pair_weight_diagnostics.py`、`pair_weight_diagnostics.tsv` |
| 模擬器 | `longbulksim` v0.2（`--mistag`、`--switch-rate`、`--base-error`） |

w = 1 的參考數字（×10，ε 0.01，seed 1／2／3）〔實測〕：

| 條件 | 方法 | `c3_under_c4` | 錯誤樹最大 posterior | clone 數眾數 |
|---|---|---|---|---|
| e0 | base＋C4 | 0／0／0 | 0.40／0.00／0.01 | 3／3／3 |
| real | base＋C4 | 0／0／0 | 0.35／0.39／0.01 | 4／4／3 |
| sw5 | base＋C4 | 0／0／0 | 0.30／0.14／0.05 | 4／4／4 |
| b03 | base＋C4 | 0／0.001／0 | 0.14／0.16／0.15 | 4／7／5 |
| real | A2＋C4 | 0／0／0 | 0.38／0.53／0.00 | 4／4／3 |
| b03 | A2＋C4 | 0／0／0 | 0.29／0.30／0.14 | 5／7／5 |

完整數字：`topology_summary.tsv` 的 `run_base_c4_e0.01`、`run_a2_c4_e0.01`。

## 3. 程式改動

依序做，每一步都要先通過測試再做下一步。

### 3.1 `tools/phyclone_pairs.py`

- `PairTable.from_files(..., eps, weight=1.0)`：把 `relation_scores(...)` 的結果乘上 weight。這樣 `term()` 不用改。
- `_init_worker` 與 `install_everywhere` 的 `initargs` 加上 weight。**這是必要的：** chain 跑在 spawn 的子 process，沒有傳 weight，子 process 會用 w = 1。
- `weight="auto"`：w = 1／（合格 pair 的 read 次數 ÷ 不同 read 數）。
  - **問題：** `pairs.tsv` 沒有 read ID，所以算不出不同 read 數。`truth/reads.tsv.gz` 有 read 位置，但它在 `truth/`，方法不得讀取（`plan.md` §5.8.2 規則 7）。
  - **作法（要使用者確認）：** longbulksim 在 `input/` 多輸出一個檔，例如 `pair_read_stats.tsv`（每個 segment × HP：合格 pair 的 read 次數、不同 read 數）。真實資料可從 BAM 的 read ID 算出同樣的數字。
  - 或者第一輪只用固定 w，`auto` 留到第二輪。

### 3.2 `tools/phyclone_hp.py`

- 加 `--pair-weight`（float，預設 1.0）。啟動訊息加上 weight，例如「C4 pair term on, N eligible pairs, eps = 0.01, weight = 0.3」。

### 3.3 測試（`tools/test_phyclone_pairs.py`）

- weight = 1 時，分數與現在逐位相同。
- `term()` 隨 weight 線性縮放。
- `SpawnedChainWorkers` 擴充：子 process 看到的 weight 等於設定值，不是 1。
- 執行：`env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python -m unittest tools/test_phyclone_pairs.py`

### 3.4 診斷工具

- `tools/c4_pair_evidence.py` 加 `--weight`，先不跑 MCMC，看 w 對 `truth_minus_linear` 和 `same_vs_split` 的影響。
  - w 會同樣縮放這兩個量，所以它們的正負號不會變。真正的差別在和 base log_p 相比時的大小。

## 4. 實驗設計

結果放在新目錄 `lab_report/2026-10-2X_c4_composite_weight/`。sims 直接用 `lab_report/2026-10-25_c4_robustness/sims/`（不要重生；可用 symlink 或在腳本中指向它）。

1. **固定 w 掃描。** e0、real、sw5、b03 × seed 1–3 × base＋C4，ε 0.01，w = 0.5／0.3／0.2。共 36 run，分兩批（每批 ≤ 25）。w = 1 已有結果。
2. **A2＋C4。** 取第 1 步最好的 w，跑同樣 12 個 sim。
3. **（選做）`auto`。** 3.1 決定後再做。
4. **ε 與 w 的交互。** 如果 w 能修模式 1，再看 ε 0.03 是否還需要。

每個 run 約 17–25 分鐘（4 chain）。平行數 ≤ 25，機器 112 核。

**指標：** 沿用 `lab_report/2026-10-25_c4_robustness/summarize.sh`（`c3_under_c4`、`c1c2_merged`、`c2_c4_correct`、`segC_*`、`max_wrong`、`n_clones`）。

## 5. 已知陷阱

- **spawn 子 process：** patch 要經過 `install_everywhere()` 的 initializer。檢查方法：結果和 w = 1 逐位相同，就是 weight 沒有生效。
- **不要用 `pgrep -f <字串>` 等待。** 等待迴圈自己的命令列也含那段字串。改成等 log 裡 `time` 印出的 `real` 行：`until grep -q "^real" LOG; do sleep 20; done`。
- **`topology_report.tsv` 比 `topologies.tar.gz` 先寫完。** 用「`topology_report.tsv` 存在」判斷完成會太早。要等整批的 log 出現 `real`。
- **bash 的 `local a=$1 b=${a...}`** 會在指派前先展開所有字，`b` 會是空的。分成兩行寫。
- **兩個 Python：** longbulksim 用系統 `python3`；PhyClone 與 `phyclone_pairs` 用 `env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python`。
- **`trace.h5` 不 commit**（`.gitignore` 已有）。

## 6. 未決問題（不要自行決定）

- `auto` 需要的 read 統計要不要加進 longbulksim 的 `input/`（3.1）。
- 成功門檻（第 1 節）是 Claude 的提案，需要老闆同意。
- 長期方向：以 read 為單位的 likelihood（每條 read 只算一次，逐位點建模鹼基錯誤），或對每條 read 的矛盾設懲罰上限。composite 加權只修重複計數的平均效果，不處理少數被算 100 次的 read。
- 失效模式 2（C3 變成第二個 root）是結構衝突，加權預期只能減輕它（第 8.1 節）。
- 上一份計畫的未決問題仍有效：`research/phyclone_research/C4_ROBUSTNESS_PLAN.md` 第 6 節。

## 7. 工作慣例

- 回答用繁體中文，ASD-STE100 風格。
- commit 直接到 `main`，只放該次的檔案，排除 `trace.h5`。commit 前先問使用者。
- 每個實驗一個 `lab_report/<日期>_<主題>/`，含 `README.md`（結論、資料、做法、結果、限制）。
- 數字要附證據等級（〔實測〕／〔推論〕）。報告前要逐條核對數字。
