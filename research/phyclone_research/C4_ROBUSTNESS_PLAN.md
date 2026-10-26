# C4 穩健性測試：交接計畫（2026-10-25）

新 session 從這裡開始。先讀本檔，再讀第 2 節列出的檔案。

> **狀態（2026-10-25 晚）：** 第 3 節（longbulksim v0.2）與第 4 節第 1、2 階段已完成，結果見 `lab_report/2026-10-25_c4_robustness/README.md`。P2 穩健；依第 1 節判定整體不穩健（`real` seed 2 的錯誤樹 0.98）。第 3.2 節「mistag 讓分支 pair 的 n11 > 0」的預期不成立（整條 read 錯標只產生 n00）。第 4 節第 3 階段未做。下一步待決，見該報告第 6 節。

## 1. 目標與判定

**問題：** C4（read 共現 topology 因子）在壓力測試樹上完全排除了錯誤的直線樹。但那是在「HP tag 全對、沒有定序錯誤、ε = 0.01」的條件下。真實 ONT 資料有錯標 HP、phase switch 和鹼基錯誤。C4 對每條矛盾的 read 罰 log ε ≈ −4.6，所以少量錯誤就可能讓它很有信心地選錯樹。

**要回答：**
1. 錯誤率多高時，C4 開始選錯樹？
2. ε 該怎麼設，才能在真實錯誤率下保有 P2 的改善，又不過度自信？

**判定（提案，可改）：**
- **穩健：** 在真實錯誤率下（第 4.1 節），直線樹 `c3_under_c4` < 0.1，而且沒有任何錯誤拓樸的 posterior > 0.5。
- **不穩健：** 任一真實錯誤率條件下，錯誤拓樸的 posterior > 0.5。這時要改 ε 或 pair score 模型，再重測。

## 2. 現況（已 commit 到 main）

| commit | 內容 |
|---|---|
| `8e6fdca` | `longbulksim` v0.1：molecule 層 read 模擬器 |
| `2d47cf6`、`b9dd860` | TRACERx 藍圖的隨機樹生成器 |
| `a1be32c` | 40 個隨機樹上的 base／A1／A2，以及 `phyclone_hp.py` 對 `snv_hp = .` 的修正 |
| `ed7a136` | C4 實作與壓力測試樹實驗 |

要讀的檔案：
- `lab_report/2026-10-25_c4_pair_term_stress/README.md`：C4 的結果、實作與限制。
- `tools/phyclone_pairs.py`：pair score、合格 pair 篩選、patch 安裝。
- `longbulksim/README.md`、`longbulksim/DECISIONS.md`：模擬器的輸出與設計決策。
- `longbulksim/longbulksim/sample.py`：read 抽樣。HP tag 在第 99 行，目前一律等於真實 HP。
- `longbulksim/longbulksim/simulate.py`：`observe()`、`counts()`、`pair_rows()`，HP 與 allele 的觀測都在這裡。
- `research/phyclone_research/HP_EXTENSION_DESIGN.md` §9.1。

已驗證（細節見各報告）：
- 壓力測試樹上，C4 把直線樹 posterior 從 0.39–0.48 降到 0.000–0.002，×1 與 ×10 密度都一樣。
- P1 只部分改善，P3 要靠 A2。
- 測試：`longbulksim` 18 個、`tools/test_phyclone_pairs.py` 6 個，全過。

## 3. 要做的程式改動（longbulksim v0.2）

依序做，每一步都要先通過測試再做下一步。

### 3.1 錯誤模型

在 spec 加三個欄位，CLI 也要能覆寫：

| 欄位 | 意思 | 實作位置 |
|---|---|---|
| `mistag_rate` | tagged read 被標成另一條 HP 的機率。以整條 read 為單位，read 上所有 SNV 一起錯 | `sample.py`：新增 `obs_hp` 陣列 |
| `switch_rate_per_mb` | 每個 segment 內的 phase switch 點（Poisson）。read 中點在奇數個 switch 之後時，`obs_hp` 反轉 | `sample.py` |
| `base_error` | 每條 read 在每個 SNV 位點，allele 被讀反的機率 | `simulate.py:observe()` |

要點：
- `counts()` 與 `pair_rows()` 都改用 `obs_hp`，不再用 molecule 的真實 HP。
- 鹼基錯誤要在 `observe()` 裡套用。`counts()` 與 `pair_rows()` 都讀同一份 `obs`，所以兩者會一致。
- 錯誤率為 0 時，不要多抽亂數。這樣舊 seed 的輸出才會逐位相同。
- `truth/reads.tsv.gz` 加 `obs_hp` 欄。

### 3.2 測試

- 錯誤率全為 0 時，`stress.yaml` seed 7 的 `input/` 檔案和 v0.1 逐位相同（先存一份 v0.1 的輸出當基準）。
- 量到的錯標率、鹼基錯誤率，在設定值的統計誤差內。
- 有 `mistag_rate` 時，分支 pair 的 n11 > 0。這表示錯誤真的會流到 `pairs.tsv`。

### 3.3 PhyClone 端

C4 本身不用改。`tools/phyclone_hp.py` 已經有 `--pair-eps`。

## 4. 實驗設計

結果放在 `lab_report/2026-10-2X_c4_robustness/`。照 `lab_report/2026-10-25_c4_pair_term_stress/run_all.sh` 的寫法，並沿用 `tools/summarize_hp_truth_topologies.py`。

### 4.1 錯誤率要先校正

| 參數 | 來源 | 狀態 |
|---|---|---|
| `mistag_rate` | `lab_report/2026-10-25_hcc1395_hp_split/`：有 ≥ 3 條 alt read 的 SNV 中，2.4% 分散在兩條 HP | 這是上限代理值，要重新解讀 |
| `switch_rate_per_mb` | `research/simulation_pipeline_research/truth_evidence_2026-10-25/01_T2T_Q100_HG002.md`，或 longphase 論文 | **未查**，不要編數字 |
| `base_error` | ONT Dorado 在 SNV 位點的鹼基錯誤率 | **未查** |

### 4.2 三階段

1. **單因子掃描（約 21 run）。** 壓力測試樹，×10 密度，base＋C4，ε = 0.01，資料 seed 1–3。一次只改一種錯誤：
   - `mistag_rate` 0.01／0.025／0.05
   - `base_error` 0.01／0.03
   - `switch_rate_per_mb` 兩個值，依 4.1 的校正結果決定
2. **ε 掃描。** 在第 1 階段開始失效的條件下，掃 ε = 0.001／0.03／0.1。另外試「ε 照錯誤率設定」，例如 ε ≈ mistag + 2 × base_error。
3. **擴大。** ×1 密度、A2＋C4，以及 `lab_report/2026-10-25_random_tree_phyclone_baseline/` 的 40 個隨機樹（模擬資料已在 `sims/`，可用 `--phased` 等選項重生）。

每個 run 約 17 分鐘（4 chain）。平行數 ≤ 25，機器是 112 核。

### 4.3 指標

- `c3_under_c4`、`c1c2_merged`、`c2_c4_correct`（`summarize_hp_truth_topologies.py`）。
- 新增：MAP 拓樸是否正確，以及錯誤拓樸的最大 posterior。

## 5. 已知陷阱

- **PhyClone 的 chain 跑在 spawn 的子 process。** 任何 monkeypatch 都要經過 `phyclone_pairs.install_everywhere()` 的 pool initializer，否則子 process 看不到。檢查方法：結果和沒有 C4 的 run 逐位相同，就是沒有生效。
- **不要用 `pgrep -f <字串>` 等另一個腳本。** 等待迴圈自己的命令列也含那段字串，會永遠等下去。改成在同一個命令裡依序執行。
- **PhyClone 的 `-n` 必須大於 thin。** smoke test 用 `-b 1 -n 2`。
- **兩個 Python。** `longbulksim` 用系統 `python3`（有 pyyaml、pysam）。PhyClone 用 `env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python`（沒有 pyyaml）。
- **`summarize_hp_truth_topologies.py` 的第一個參數**是 `sims/<name>/truth`，不是 `input`。
- **`trace.h5` 不 commit**（`.gitignore` 已有 `lab_report/**/trace.h5`）。
- **`snv_hp = .`**（沒有 tagged alt read）的 SNV 不會進入 C4。A1／A2 會對兩條 HP 取平均。

## 6. 未決問題（不要自行決定）

- **改 submodule 還是外部 wrapper？**（`HP_EXTENSION_DESIGN.md` §8 第 3 項）目前是 wrapper。
- **模擬的 HP 標籤要模仿 germline `haplotag` 還是 `somatic_haplotag`？**（§8 第 5 項）會影響 `mistag_rate` 的校正。
- **成功門檻需要老闆同意。** 第 1 節的判定是 Claude 的提案。
- **A2 的 phi 在真實資料從哪來？**（§8 第 1 項）

## 7. 工作慣例（使用者的偏好）

- 回答用繁體中文，ASD-STE100 風格。
- commit 直接到 `main`，只放該次的檔案，排除 `trace.h5`。commit 前先問使用者。
- 每個實驗一個 `lab_report/<日期>_<主題>/`，含 `README.md`（結論、資料、做法、結果、限制）。
- 數字要附證據等級（〔實測〕／〔推論〕）。報告前要逐條核對數字。
