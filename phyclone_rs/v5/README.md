# V5：Rust（haploclone）vs Python PhyClone 0.8.0 的速度（M9b，2026-10-27）

問題：Rust 比 Python 快多少、spread 多大？為什麼 FS-CRP 只快約 4×、`upstream_grid1000` 只快 1.7×？哪些可以修？（`PORTING.md` 第 3 節 V5）

## 結論

- **修正後，10 個 config 的 Python/Rust 牆鐘比中位數約 28×（範圍 5.2–48×）；修正前約 18×（1.6–49×）。** 每格是 3 次 run 的中位數。〔實測，`summary.tsv`〕
- **慢的原因是 Python 有 memo，Rust 沒有。** PhyClone 用 `list_of_np_cache` 快取 `compute_log_S`，也用 `two_np_arr_cache` 快取 `_convolve_two_children`。cluster 輸入的節點少，同樣的 child grid 一再出現，所以 Python 大多直接命中快取。Rust 每次都重算。〔程式：`tree/utils.py:7,60`；實測：`periter.tsv`〕
  - `upstream_grid1000`：修正前 Python 每 iteration 18.7 ms，Rust 21.8 ms，Rust 反而比較慢。修正後 Rust 6.6 ms。
  - FS-CRP golden：Python 61.9 ms、Rust 27.3 → 16.9 ms。
- **修正後 FS-CRP 仍只快約 5×，原因是「Python 本來就快」。** 8 個樣本 × 101 格的 convolution 與 log 空間累加，在兩邊都是編譯過的數值運算（Python 走 numpy／OpenBLAS）。Rust 的時間有 82–91% 在 `log_s` 的 cache miss 上，其中 convolution 約 30–37%，`exp`／`log1p`／`log` 約 30%。〔實測，callgrind〕
- **四項修正都不改任何浮點結果。** 7 個 golden config 的 seed-1 trace 與 `v3/rust_m7` 逐位元相同；`cargo test --release` 118 pass、1 ignored（含 V1、`tests/post.rs` V2）。
- 單樣本 SNV 輸入（e0、b03、A2）本來就 28–49×，修正後不變（差 < 1%）。
- `loss.rs` 的 O(n²) `unique()` 已修。20,000 SNV 時 `assign()` 的指令數從 3.20e9 降到 1.33e9；剩下的是 Monte Carlo 抽樣（語意本身）。

## 1. 速度表

Python = run1；Rust 修正前（f05b615）與修正後（a08fb40）= run3。每格是 3 次 run 的中位數［最小–最大］，單位秒。比值範圍 = 最慢 Python ÷ 最快 Rust 到最快 Python ÷ 最慢 Rust。

| config | chain | Python | Rust 前 | Rust 後 | 比值 前 | 比值 後 |
|---|---|---|---|---|---|---|
| e0_base_bin | 1 | 143.0 [142.2–153.2] | 5.12 [5.11–5.13] | 5.10 [5.08–5.19] | 27.9× [27.7–30.0] | 28.0× [27.4–30.2] |
| b03_base_err003_hpu（C4） | 1 | 282.1 [277.5–304.3] | 8.53 [8.51–8.55] | 8.48 [8.45–8.48] | 33.1× [32.5–35.8] | 33.3× [32.7–36.0] |
| real_a2_err004（A2） | 1 | 283.0 [279.5–296.5] | 5.81 [5.80–5.84] | 5.85 [5.84–5.93] | 48.7× [47.9–51.1] | 48.3× [47.1–50.8] |
| e0_out001（outlier） | 1 | 181.6 [175.4–198.4] | 6.14 [6.09–6.18] | 5.80 [5.71–6.16] | 29.6× [28.4–32.6] | 31.3× [28.5–34.7] |
| e0_out001_fully | 1 | 701.9 [688.6–721.5] | 27.44 [27.44–27.93] | 25.21 [24.79–25.22] | 25.6× [24.7–26.3] | 27.8× [27.3–29.1] |
| upstream_grid1000 | 1 | 8.87 [8.82–9.40] | 5.47 [5.46–5.62] | 1.08 [1.08–1.09] | 1.6× [1.6–1.7] | 8.2× [8.1–8.7] |
| fscrp_assign_loss | 1 | 21.27 [21.14–21.59] | 6.44 [6.43–7.00] | 4.11 [4.10–4.24] | 3.3× [3.0–3.4] | 5.2× [5.0–5.3] |
| V4 FS-CRP loss_prop_0.2_run2（outlier） | 4 | 264.6 [263.7–266.1] | 77.56 [77.42–77.83] | 46.49 [41.76–46.52] | 3.4× [3.4–3.4] | 5.7× [5.7–6.4] |
| V4 Pairtree K10_S10_M1000_run1 | 4 | 97.2 [96.5–97.7] | 23.59 [23.43–23.62] | 4.54 [4.53–4.56] | 4.1× [4.1–4.2] | 21.4× [21.1–21.6] |
| V4 CONIPHER_No-Noise LTXSIM002 | 4 | 74.9 [73.3–75.0] | 7.24 [7.22–7.33] | 1.84 [1.84–1.91] | 10.3× [10.0–10.4] | 40.7× [38.3–40.8] |

- golden config 用 `-b 20 -n 200`，1 chain。V4 trial 用論文設定（4 chain、`-b 100 -n 5000`、100 particle、beta-binomial、semi-adapted，`PhyClone` 列加 `--assign-loss-prob`）。指令同 `v4/run_v4.py`。
- 只計 `run` 的牆鐘，不含 `map`／`topology-report`。
- golden 的 Python 時間含 4–7 s 的固定成本（import、numba JIT）。Rust 的固定成本是 0.1–0.36 s（`periter.tsv`）。所以短 run 的比值有一部分來自 Python 的啟動。

### 每 iteration 成本（`periter.tsv`）

`-b 0`，`-n 2` 與 `-n 202` 各 3 次；per_iter = (t202 − t2) / 200。Python 只在這裡跑了 9 次。

| config | Python 固定 s | Python ms/iter | Rust 前 ms/iter | Rust 後 ms/iter |
|---|---|---|---|---|
| e0_base_bin | 6.32 | 645.8 | 19.20 | 19.16 |
| fscrp_assign_loss | 6.65 | 61.9 | 27.27 | 16.89 |
| upstream_grid1000 | 4.33 | 18.7 | 21.84 | 6.58 |

V4 FS-CRP（100 particle，每 chain 5,100 iteration）：Python 51.9 ms/iter，Rust 15.2 → 9.1 ms/iter（由上表牆鐘換算）。〔推論〕

## 2. 做法

- 量測腳本：`bench.py`（全部 run）、`periter.py`（每 iteration 成本）、`summarize.py`（中位數、範圍、比值）、`check_identity.py`（seed-1 逐位元比對）、`make_loss_input.py`（`unique()` 的大輸入）。
- 每次 run 都在 `timings.tsv`（共 240 列：run1 = Python + Rust 4 個 build，run2／run3 = Rust）。原始輸出在 `/big8_disk/boyu114/phyclone_v5/<run>/<impl>/<config>/rep<r>/`，binary 在 `/big8_disk/boyu114/phyclone_v5/bin/`。
- 公平性：
  - 所有 impl 的 job 用固定 seed 打亂後交錯執行，同時最多 16 core（一個 chain 一個 core）。所以兩邊看到相同的背景負載。
  - 每次啟動前讀 1 分鐘 load；別人的 load 一直 < 60（實測最高約 40）。
  - 兩邊都設 `OMP/MKL/OPENBLAS/NUMBA_NUM_THREADS=1`。Rust 是 release build（`target-cpu=x86-64-v3`）。
  - Python 與 Rust 修正前在同一個 run（run1）也量過，Rust f05b615 在 run1 與 run3 的中位數差 ≤ 2.3%，所以 run3 的 Rust 可以和 run1 的 Python 比。
- 「工作有沒有真的做」：每個 job 檢查 exit 0；Rust 的 `iterations.tsv` 要有 chain × n 列，Python 要有 `trace.h5`。240 個 job 全部完整。
- Profile：`perf` 不能用（`perf_event_paranoid` 4），用 valgrind callgrind，`--toggle-collect=*run_chain*` 只計 chain。原始檔在 session scratchpad `m9b/cg_*.out`。

## 3. 修正（branch `perf-m9b`，haploclone）

| commit | 內容 | 效果（實測） |
|---|---|---|
| e14e417 | `loss.rs` 的 `unique()` 改用 `HashSet`，保留首次出現順序 | 20k SNV：`assign()` 3.20e9 → 1.33e9 Ir；10k／20k／40k SNV 的 trace 與修正前相同 |
| 1561e39 | `log_s` 的 per-thread memo：一棵以「依序的 child grid」為鍵的 trie。每個 prefix 存 scaled row 的 convolution，每個完整序列存 `log_s` | grid1000 5.5 → 1.4 s，V4 Pairtree 23.6 → 5.8 s，V4 FS-CRP 77 → 51 s |
| a6f870a | 一輪內命中率 < 25% 時，下一輪 memo 只留 1,024 個 prefix（預設 4,096，同 PhyClone） | 單樣本 e0 在 15 個 run 並行時，從 +8% 變 +1.6%（相對 f05b615）；cluster 輸入不變 |
| 118deef | 每個 child grid 的 scaled row（除以最大值後取 exp）也放進 memo | fscrp_assign_loss 5.09 → 4.52 s |
| a08fb40 | grid 的 hash 只取 64 個等距元素（multiply 鏈受延遲限制）；查表仍比對全部位元 | grid1000 1.36 → 1.08 s，V4 Pairtree 5.55 → 4.47 s，V4 FS-CRP 45.9 → 43.2 s |

逐位元相同的理由：memo 的鍵是 child grid 的**完整位元、依順序**。命中時回傳的值，就是同樣的輸入、同樣的計算順序算出的值。PhyClone 的鍵把 child 的 hash 排序（不看順序），Rust 沒有這樣做，因為 convolution 的捨入取決於順序。

驗證：每個 commit 都跑 `check_identity.py`（7 個 golden config 的 seed-1 trace 與 `v3/rust_m7` 逐位元相同；`meta.json` 忽略 `settings.prior`）與 `cargo test --release`（118 pass、1 ignored）。

memo 的記憶體上限：每個 thread 最多 16M float（128 MiB）或 4,096 個 prefix，超過就清空重來。

## 4. 沒有採用的選項（會改變浮點結果）

| 選項 | 預期效果 | 依據 |
|---|---|---|
| 和 PhyClone 一樣，memo 鍵不看 child 順序（先依 hash 排序） | FS-CRP golden −21%、V4 FS-CRP −7%；Pairtree、CONIPHER、grid1000 反而慢 10–15%（排序成本） | 實驗 build `rust_unordered_expt`，相對 1561e39，`summary_run1.tsv` |
| 向量化的 `exp`／`log`／`log1p`（SIMD libm） | libm 佔 chain 指令數約 30–35%（FS-CRP、e0）；若快 4 倍，整體約快 20–25% 〔推論〕 | callgrind exclusive |
| FFT 改用其他 plan／pocketfft | grid1000 的 `log_s` 命中率 0.95，FFT 已不是瓶頸；預期 < 5% 〔推論〕 | memo 命中率統計 |

## 5. 限制

- 每格 3 次 run，不是 benchmark-checklist 建議的 5 次。比值的範圍不重疊（除了單樣本 config 的前後比較，那裡的差 < 2%，判定為沒有可量測的差異）。
- `periter.tsv` 的 Rust a08fb40 先量到一次受背景負載影響的結果（grid1000 8.58 ms），在 load < 7 時重量並取代。
- 每 iteration 成本與軌跡有關：`-b 0` 的軌跡和 `-b 20` 不同，命中率也不同。
- 預設 build 的 memo 使用額外記憶體：cluster 輸入每個 chain 最多 128 MiB。
- Python core-hour：run1 2.82，`periter.py` 與探測約 0.15，共約 3.0。
