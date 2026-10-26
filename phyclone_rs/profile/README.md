# M1：Python 參考 run 的時間分布（2026-10-26）

結論：

- base run 沒有單一熱點。tree 結構與 node 更新、SMC proposal、convolution 三塊合計 86%，都是 Python 物件與直譯器的開銷。移植成 Rust 後應該全面變快〔推論，V5 才實測〕。
- 開 C4 時，pair term 佔 31%，是最大的單一模組。它讓 run 時間約變成 1.9 倍。M4 移植 pair term 時要先處理它。

## 方法

- 兩個參考 run，參數和 `golden/run_reference.sh` 相同（`-b 20 -n 200 --num-chains 1 --seed 1`）：
  - `e0_base_bin`：base emission，沒有 C4。
  - `b03_base_err003_hpu`：C4 誤差模型 e = 0.03，加 HP 不確定性。
- `profile_run.py` 在同一個 process 內跑 chain，用 cProfile 量。原版用 spawn 的 process pool 跑 chain，從 parent 量會量不到 chain 的工作。
- `analyze.py` 把每個函式的 tottime 分到 `PORTING.md` 第 2 節的 Rust 模組。numpy、scipy、builtin 的時間依呼叫邊分給最近的 phyclone 或 tools frame。
- 驗證方式：
  - profile 版的 trace 和 `golden/runs/<run>/trace.h5` 完全相同（`compare_trace.py`：兩個 run 都是 1,908 個 dataset，0 個不同）。所以量到的是同一條 chain。
  - profiled 區段的時間等於整支 script 的 wall time（差 < 0.01 秒），所以 chain 的工作都在 profile 範圍內。
- 機器：AMD EPYC 7453，量測時 load 約 1.2–2.2。兩個 run 依序執行。

## wall time

| run | 沒有 profile（`profile_run.py --no-profile`） | 有 profile | 倍數 |
|---|---:|---:|---:|
| e0_base_bin | 141.2 s | 218.4 s | 1.55 |
| b03_base_err003_hpu | 272.3 s | 444.7 s | 1.63 |

下面的百分比是 profile 下的值。cProfile 對呼叫次數多的小函式加的開銷比較大，所以比例只能看相對大小。

## 各 Rust 模組的時間比例

| Rust 模組 | e0_base_bin | b03_base_err003_hpu |
|---|---:|---:|
| pairs（C4） | — | 31.1% |
| tree：結構、copy、node 更新 | 42.5% | 30.1% |
| tree：convolution（compute_log_S/D 與 cache） | 19.6% | 15.4% |
| smc | 23.9% | 14.1% |
| prior/joint | 8.4% | 6.2% |
| 啟動（import、numba JIT） | 2.4% | 1.2% |
| math | 1.7% | 1.1% |
| data、mcmc、trace、其他 | 1.5% | 0.8% |

## 最貴的函式（e0_base_bin，依 tottime）

| 函式 | 呼叫次數 | tottime | cumtime |
|---|---:|---:|---:|
| `tree/utils.py` `compute_log_D` | 649,583 | 8.6 s | 26.9 s |
| `smc/kernels/semi_adapted.py` `_propose_new_node` | 1,079,022 | 7.9 s | 73.7 s |
| numpy ufunc `reduce` | 1,608,091 | 6.1 s | 6.1 s |
| rustworkx `digraph_dfs_search` | 687,491 | 5.2 s | 21.8 s |
| `tree/tree_node.py` `add_data_point_list` | 290,185 | 4.3 s | 4.8 s |

## C4 run 的 pair term

- `tools/phyclone_pairs.py` 的 `term` 被呼叫 779,656 次，tottime 90.8 s（20.4%）。
- 它呼叫 4.46 億次 `dict.get`，再佔 27.8 s（6.2%）。
- 原因：每評估一棵樹，`term` 就把所有合格 pair 掃一遍，並用 dict 查每個 mutation 的 node。
- 給 M4 的方向：先把 mutation → node 改成陣列查表。增量更新（只重算有變動的 node 的 pair）會改變計算方式，要先用 fixture 證明數值相同才採用。

## 檔案

- `profile_run.py`：有或沒有 cProfile 的單一 run。
- `time_run.py`：不用 cProfile，只計時 convolution、`tree_assignment`、`PairTable.term` 三個入口。M1 agent 寫了它，但沒有找到它的輸出，這裡的數字都不是它產生的。
- `analyze.py`：產生上面的表。執行方式：`python3 phyclone_rs/profile/analyze.py e0_base_bin b03_base_err003_hpu`。
- `compare_trace.py`：比對兩個 trace.h5。
- `<run>.pstats`、`<run>.json`、`<run>.plain.json`、`log_*.txt`：原始量測。
- `*.trace.h5` 不進 git（每個 2.9 MB），可以用 `profile_run.py` 重產。
