# PhyClone → Rust 移植計畫（haploclone）

狀態（2026-10-27）：M0–M7 完成並驗證（V1 數值層、V2 後處理、V3 統計層）；下一步 M8。進度與決策紀錄在 `decisions.tsv`（一列一個決策）。V3 harness 在 `v3/`（`v3/README.md`）。

## 1. 目標

1. **加速。** 現在一組實驗（24 個 run × 4 chain × 1100 iteration）要 43–61 分鐘；40 棵隨機樹的長 run 中位數 1534 秒。prior、pair score 的比較要跑很多組，所以速度是主要瓶頸。〔實測，`golden/README.md` 第 5 節〕
2. **模型語意和原版相同。** 包含 upstream PhyClone 0.8.0，以及本研究在 `tools/` 的擴充：
   - emission：base（PhyClone `load_data`，binomial／beta-binomial）、A1、A2（`tools/phyclone_hp.py`）
   - C4 pair term：eps、誤差模型、HP 不確定性、composite weight（`tools/phyclone_pairs.py`）
3. **prior 可以替換。** 預留 `research/phyclone_research/FSCRP_PRIOR_PLAN.md` 的候選：固定或更新 alpha、調溫 τ、Pitman–Yor discount。τ = 1、d = 0 時要和原版一致。
4. **trace 改成 TSV**（2026-10-26 決定，見第 5 節）。
5. **固定 seed 時可重現。** Rust 的 RNG 不會和 numpy 逐位一致，但同一個 Rust 版本、同一個 seed，結果必須相同。

非目標：GPU、分散式執行、改變模型。模型的修改（例如 FSCRP prior）在移植完成、對齊驗證之後才做。

## 2. 程式碼對照

| 位置 | 內容 |
|---|---|
| `/bip8_disk/boyu114/haploclone/` | 原版 PhyClone 的 git clone，checkout 在 `27383246`（= tag `0.8.0`，detached HEAD）。**Rust 版也放在這裡**（第 7 節）。upstream 的 Python 程式只當對照，不要修改 |
| `research/phyclone_research/PhyClone/` | 同一個 commit 的 submodule（本 repo） |
| `tools/phyclone_hp.py`、`tools/phyclone_pairs.py` | A1／A2／C4 擴充（repo commit `3b91b17`） |
| `phyclone_rs/golden/` | 凍結的輸入／輸出（commit `0194713`），見該目錄 README |
| `research/phyclone_research/notes/04_CODE_MAPPING.md` | 論文 ↔ 程式對照 |

- 論文用的是 **0.7.0**（tag 存在），和 0.8.0 之間有 205 個 commit。筆記記錄的差異包括 outlier 的積分方式（`notes/06_ASSUMPTIONS_LIMITATIONS.md` 第 61、63 項）。
- 原版非測試程式約 6,700 行。主要模組：

| Python | 行數 | Rust 模組（暫定） |
|---|---|---|
| `data/pyclone.py`、`data/cluster_outlier_probabilities.py`、`data/validator/` | 424＋175＋203 | `data`：讀 TSV、CN prior、likelihood grid、cluster、outlier 機率 |
| `tools/phyclone_hp.py` | 226 | `data::hp`：A1、A2 |
| `utils/math_utils.py` | 254 | `math`：log-sum-exp、binomial／beta-binomial、FFT convolution |
| `tree/tree.py`、`tree/base.py`、`tree/tree_node.py`、`tree/tree_shell_node_adder.py`、`tree/visitors.py` | 443＋100＋82＋469＋136 | `tree`：結構、子樹 likelihood 的增量更新 |
| `tree/distributions.py` | 204 | `prior`、`joint`：FSCRP（可替換）、TreeJointDistribution、outlier |
| `tools/phyclone_pairs.py` | 251 | `pairs`：pair table、四種 score |
| `smc/kernels/*`、`smc/samplers/*`、`smc/utils.py` | ~1,090 | `smc`：semi-adapted（必要）、bootstrap（選做） |
| `mcmc/particle_gibbs.py`、`mcmc/gibbs_mh.py`、`mcmc/concentration.py` | ~300 | `mcmc`：PG、prune-regraph、outlier Gibbs、alpha 更新 |
| `run.py` | 436 | `run`：chain、burn-in、多 chain 平行 |
| `process_trace/*`、`utils/save_hdf5.py`、`utils/load_hdf5.py` | ~1,070 | `trace`（TSV）、`post`：map、consensus、topology report |
| `cli.py` | 465 | `cli`：子命令與選項，名稱盡量和原版相同 |

## 3. 驗證

由內而外，每一層通過才做下一層。

| 層 | 資料 | 判準 |
|---|---|---|
| V1 數值對齊 | `phyclone_rs/golden/fixtures/`：datapoints、FSCRP prior 各項、data log-likelihood、log_p／log_p_one、pair table／pair term、clone table | `golden/README.md` 第 4 節的容許誤差（datapoints ≤ 1e-10；likelihood ≤ 1e-6；pair ≤ 1e-8） |
| V2 後處理 | `golden/runs/*/`：把原版 trace 轉成 TSV，跑 Rust 的 map／consensus／topology-report | 和 golden 的輸出一致 |
| V3 端到端（統計） | golden 的 7 個參考 run＋`lab_report/` 的長 run（壓力樹 12 個 sim、40 棵隨機樹） | 多個 seed 的 posterior 摘要（clone 數分布、topology 類別比例、`c3_under_c4` 等）落在 Python 版 seed 間的變異範圍內 |
| V4 PhyClone benchmark | `/big8_disk/boyu114/phyclone_dataset/`（見第 4 節） | 和真值的評估指標，與論文輸出、Python 0.8.0 輸出比較，沒有系統性變差 |
| V5 速度 | 同一批 run，Rust vs Python | 回報加速倍數；目標另訂 |

V1–V2 是確定性的比較。V3–V4 只能做統計比較，因為 RNG 不同。

## 4. 用 PhyClone 論文 dataset 驗證（V4）

- 位置：`/big8_disk/boyu114/phyclone_dataset/`（46 GB）。說明見 `tumor_sample.md` 的「PhyClone Benchmarking 資料集」。
- 每個 trial：`<Dataset>/data_archive/<Trial>/{ground_truth,program_inputs,program_outputs}/`
  - PhyClone 輸入：`program_inputs/phyclone_outliers/data.tsv`（9 欄）、`results.tsv.gz`（PyClone-VI 分群，當 cluster 檔）
  - 論文的 PhyClone 輸出：`program_outputs/phyclone_outliers/{results.tsv,topology_report.tsv,tree.nwk,tree.json,exit.status}`
  - 真值：`ground_truth/tree.json`
- 規模：TSSB_Low 500、TSSB_High 400、Pairtree 576、CONIPHER_Noise／No-Noise 各 150、Copy_Number_Error 450、FS-CRP_Loss 300、HGSOC 6 個 trial。
- 論文的 PhyClone 設定〔論文，`notes/03_EXPERIMENTS_RESULTS.md`〕：**PhyClone 0.7.0**、4 chain、burn-in 100、5,000 iteration、100 particle、beta-binomial、semi-adapted proposal、**outlier 開啟**；點估計取 joint score 最大的樹。
- 比較方式：
  1. 先挑小的子集，例如每個 dataset 各 5–10 個 trial、只用小的設定（TSSB_Low S2／S4、CONIPHER、FS-CRP_Loss），控制時間。
  2. 在同一子集上跑：Python 0.8.0（haploclone）、Rust 版。論文的 0.7.0 輸出已經在 dataset 裡。
  3. 用相同的評估指標比較三者和真值的差距（論文用 ancestor-descendant F-score 等；評估程式要確認可用）。
- **限制：**
  - 論文輸出是 0.7.0，和 0.8.0 不同，只能看統計趨勢，不能逐檔比較。
  - **dataset 的設定需要 outlier 模型，但 golden 沒有凍結 outlier。** 開始 V4 之前，要先在 golden 加上 outlier 開啟的 case（例如一個 FS-CRP_Loss trial），補凍結後再對齊。
  - beta-binomial、cluster 檔、多樣本已經在 golden 的 `upstream_mixing_small` 涵蓋。

## 5. Trace 格式：TSV（已決定）

實測（同一份 trace，樹去重複）：長 run 從 h5 的 38.7 MB 降到 TSV 4.67 MB、TSV＋xz 0.55 MB、TSV＋zstd 0.75 MB；Parquet 0.56 MB，但不能直接看。〔實測，2026-10-26，轉換腳本在 session 暫存目錄，沒有保留〕

```
trace/
  meta.json             版本、指令、全部設定、seed、樣本名、grid size
  iterations.tsv[.zst]  chain  iter  alpha  log_p  log_p_one  num_nodes  num_outliers  num_roots  tree_id
  trees.tsv[.zst]       tree_id  node  parent   log_prior      （相同的樹只存一次；parent = -1 表示 root）
  assignments.tsv[.zst] tree_id  mutation  node                （node −1 = outlier；meta.json 有 `"outlier_node": -1`）
  datapoints.tsv[.zst]  mutation  sample  outlier_prob  outlier_prob_not  g0 … g{grid-1}
  clusters.tsv[.zst]    cluster_id  mutation_id                （有 cluster 檔時）
```

- 浮點數用 round-trip 精度（`%.17g`）。
- **不壓縮**（2026-10-26 決定）。之後若要壓縮，再加選項。
- 轉換器（M6 完成）：`haploclone/rust/tools/trace_h5.py`，子命令 `h5-to-trace`、`trace-to-h5`。用 Python 寫，Rust binary 不依賴 HDF5；`trace-to-h5` 直接呼叫原版的 `save_trace_to_h5df`。原版後處理和現有工具（`tools/c4_truth_vs_map.py`、`golden/verify_against_traces.py`）可以透過它讀 Rust trace。
- M6 加的格式規則（後處理的輸出順序依賴它們）：
  - `meta.json` 的 `dtypes` 記錄每個 id 欄是 int 還是 str。
  - `datapoints.tsv` 多一欄 `outlier_marginal_prob`。
  - `assignments.tsv` 的 node −1 是 outlier node。
  - node id 等於它的入邊在儲存的 edge list 裡的位置，所以同一 parent 的 children 依 id 遞增就是儲存順序。node 內 `assignments.tsv` 的列順序就是 log_p 加總資料點的順序。
  - iteration 依 h5 的 chain 名稱順序讀（`chain_10` 在 `chain_2` 前）。
  - `iterations.tsv` 可以有 `tree_hash` 欄（`h5-to-trace` 寫入原版存的 `trace_data/tree_hash`）。後處理照原版 `create_topology_dataframe` 用它分組；沒有這欄時（Rust 寫的 trace）用樹本身的 hash，`trace-to-h5` 也寫入同一個值。存的值和樹的 hash 不同時，`map`、`consensus`、`topology-report` 會警告。
  - `trees.tsv` 的 node：同一 parent 的 children 依 id 遞增就是儲存的 edge 順序，也就是 `Tree.from_dict` 之後的 rustworkx edge index，也是 map.py 的 networkx 列出 children 的順序。

## 6. 里程碑（暫定）

| 步驟 | 內容 | 通過條件 |
|---|---|---|
| M0 | 安裝 Rust toolchain（2026-10-26 已用 rustup 裝到家目錄）；在 haploclone 建立 crate | `cargo test` 可跑 |
| M1 | 用 cProfile 量 Python 參考 run 的時間分布 | 知道熱點，確認移植優先順序 |
| M2 | data：讀 TSV、likelihood grid（base、A1、A2、cluster） | V1 datapoints |
| M3 | tree＋prior＋joint：convolution、FSCRP、log_p／log_p_one | V1 trees／scores |
| M4 | pairs：四種 pair model | V1 pairs、pair term |
| M5 | SMC（semi-adapted）＋PG＋prune-regraph＋alpha 更新；多 chain | V3 |
| M6 | trace TSV、map／consensus／topology-report、h5 轉換器 | V2 |
| M7 | outlier、bootstrap proposal、loss prior 選項（`--assign-loss-prob` 等）、其餘 CLI 選項；golden 補凍結這些功能 | V1（新 case） |
| M8 | dataset 驗證 | V4 |
| M9 | 速度比較；prior 可替換（τ、Pitman–Yor） | V5；τ = 1、d = 0 時 V1 仍然通過 |

## 7. 決定（2026-10-26）與未決問題

已決定：

1. **完整移植。** 資料讀取、SMC／Particle Gibbs、trace、後處理全部用 Rust，不透過 PyO3 呼叫 Python。
2. **程式放在 `/bip8_disk/boyu114/haploclone/`。** 建議做法（實作時確認）：在這個 clone 從 tag `0.8.0` 開一個新 branch，Rust crate 放在子目錄（例如 `haploclone/rust/`）。upstream 的 Python 程式留在原位當對照，這樣 `git diff 0.8.0` 只會看到新增的 Rust 程式。
3. **trace 用 TSV，不壓縮。**
4. **Rust toolchain**：用 rustup 安裝到家目錄（M0）。
5. **全部功能都支援。** 包括 outlier、bootstrap proposal（0.8.0 有已知回歸，筆記 `06` 第 63 項：Rust 版先照原版行為移植，並在文件標明；修正另外做）、`--assign-loss-prob`／`--user-provided-loss-prob`／`--high-loss-prob`、`--subtree-update-prob`、`--thin`、`--max-time`、consensus 的各種 `--weight-type` 等。golden 目前沒有凍結的功能，要先補凍結再移植（M7）。

實作時決定（2026-10-26）：

6. **branch 與目錄**：採用第 2 項的建議。haploclone 的 branch `rust-port` 從 tag `0.8.0` 開出，crate 名稱 `haploclone`，放在 `haploclone/rust/`。M0 commit `8941bf3`。
7. **RNG**：`rand_chacha` 的 ChaCha8。用 `seed_from_u64(seed)` 起始；stream 0 給主 RNG（資料讀取等），chain i 用 stream i+1。這對應原版 `rng_main.spawn(num_chains)`（`run.py` 第 115 行）的角色，但數值不同。
8. **golden 路徑**：Rust 測試用環境變數 `HAPLOCLONE_GOLDEN` 找 `phyclone_rs/golden/`，預設是本 repo 的絕對路徑。

仍未決定：

- **dataset 評估程式**：論文的指標（AD F-score 等）用哪一支程式算，是否已經在 `tools/` 或 `lab_report/2026-10-22_pairtree_conipher_sim_rerun/` 裡。

## 8. 已知注意事項

- **lgamma 綁定 C libm。** numba 把 `math.lgamma` 編成 glibc 的 `lgamma`。Rust 版用 FFI 呼叫 `lgamma_r`，才能逐位相同（M2 實測：85,000 個值全同；`libm` crate 有 1,724 個不同）。
- **convolution 的逐位對齊條件**（M3 實測）：
  - grid < 1000 時原版走 `np.convolve` → OpenBLAS `cblas_ddot`（Haswell／Zen kernel）。Rust 版照它的加總順序（16 個 FMA accumulator）實作，fixture 上 0 差。換成 AVX-512 機器，OpenBLAS 會換 kernel，Python 自己的結果也會變〔推論〕。
  - crate 設 `target-cpu=x86-64-v3`（`rust/.cargo/config.toml`）。沒有硬體 FMA 時 `mul_add` 變成軟體呼叫，kernel 慢 9 倍；結果不受影響。
  - child 的走訪順序會改變 1e-100 clip 的位置，進而改變 tail 與 `log_p_one`（實例差 0.0124）。Rust 版用 newest-first（同 rustworkx successors）。Python 的 `compute_log_S` cache 不看 child 順序，所以一般樹的順序取決於歷史，無法完全重現；這只影響 V3 以後的統計比較，不影響 V1。
  - grid ≥ 1000 走 FFT（M7）：用 `realfft`（純 Rust），長度照 scipy 的 `next_fast_len`。和 pocketfft 不逐位相同。V1 只比 row 峰值以下 25 log 單位以內的 grid 格（`tests/trees.rs` `FFT_FLOOR`）；不是 `fft_noise_dominated` 的樹，log_p／log_p_one 全部比，誤差 ≤1.4e-13。
- **M4 找到的 pair term 怪癖**（Rust 照原版）：`pairs.tsv` 的 `sample_id` 沒有用到，eligibility 與 HP posterior 只看 `data_hp.tsv`／`segments.tsv` 每個 mutation／segment 的第一列；HP 不確定性模式只用 q ≥ Q_MIN 判斷，不看 `snv_hp`；用 cluster 檔時 pair 會對到 cluster id（`dp.name`），base mode 不會拒絕這種輸入。
- **平台綁定（審查補記）**：V1 的逐位相同依賴 glibc `lgamma_r`（musl／macOS 會失去逐位一致）、OpenBLAS ddot 的加總順序，以及 `x86-64-v3`。沒有 AVX2／FMA 的 CPU 會直接 SIGILL，目前沒有 runtime 偵測。軟體 `fma` 與硬體 FMA 都是正確捨入，所以數值相同；慢 9 倍的只是速度。
- **壓縮輸入**：gzip 已支援（M7）。bz2、xz、zip 仍回傳 `Error::Unported`。
- **M2 找到的原版怪癖**（Rust 版照原版行為實作）：
  - base loader 先把 `sample_id` 轉成字串再排序（"20" 在 "3" 前）；A1/A2 loader 保留整數排序。整數 mutation id 兩者都用數值排序。
  - major_cn = 0 的過濾在建立 sample 清單之前，所以全為 0 的 sample 會消失。
  - data 裡不在 cluster 檔的 mutation 會被靜默丟掉；同一個 mutation 在兩個 cluster 時兩邊都算。
  - A1/A2 loader 沒有 validator、去重複與 major_cn 過濾。
  - scipy 1.15 的 `logsumexp` 和 numpy 依 axis 不同的加總順序都會影響末位；Rust 版照原版順序。

- 原版 trace 的 `log_p` 欄存的是 `log_p_one`；MAP 取它的最大值（`process_trace.py` `write_map_results`）。
- PhyClone 在 `ProcessPoolExecutor(mp_context=spawn)` 裡跑 chain；C4 的 monkeypatch 必須在子 process 重裝（`tools/phyclone_pairs.py` `install_everywhere`）。Rust 版沒有這個問題，但要確認 pair term 在 SMC、PG、Gibbs-MH 都有算到。
- C4 pair term 只加在 `log_p`、`log_p_one`、`compute_log_p_and_log_p_one`。**更正（M5 實測）**：semi-adapted proposal 的 existing-node q 用 `x.log_p`（`smc/kernels/base.py:176-177`），它來自被 patch 的 `compute_log_p_and_log_p_one`（`smc/swarm/tree_holder.py:74`），所以這部分**有**看到 pair term（eps0.01 時 log_q 最多變 157 nat）。只有 new-node 的子節點選法不看 pair term。Rust 版照原版。
- 隨機樹的短 run 可能卡在 1 個 node（`golden/README.md` 第 6 節）。**更正（M5）**：alpha 只有 iter 0 是 1.0，之後塌到約 1e-10；Python 與 Rust 中位數都是 1e-10。這是原版行為，Rust 版重現它不算 bug。
- **M5 刻意的偏差（2026-10-27 決定保留修正）**：PG 子樹的 `_correct_weights`（`mcmc/particle_gibbs.py:89-105`）在同一個 particle 被 resample 成多份時，第二份會把其餘部分再 graft 一次，資料點重複。Rust 每份各自重新加權（`rust/src/mcmc.rs:37,71`）。只在 `--subtree-update-prob` > 0 時有影響（預設 0）。這是目前唯一和 0.8.0 語意不同的地方；`--subtree-update-prob` > 0 時，Rust 和 Python 的結果不能直接比。
- **M5 其他小差異**：`--max-time` 在 M7 改回原版語意（共用一個 timer；burn-in 用 `>`，存 trace 後用 `>=`；`--max-time 0` 跑 2 個 burn-in iteration，golden README 6.1 第 10 項寫 1 個，原版程式實際是 2 個）；單一 chain 也用 stream 1（原版用 rng_main）；TSV trace 相對第 5 節的偏差寫在每個 trace 的 `meta.json`（沒有 time 欄、`log_p` = `log_p_one`、node 依最小資料點 index 編號、tree_id 跨 chain 去重複）。
- **M6 找到的後處理怪癖**（Rust 照原版，全部沒改）：
  1. map.py 的 `compute_log_D` 第一個 child 從 0 向量開始，不是從 0 的點質量開始；`>=`／`>` 的 tie 規則照原樣。
  2. consensus 的輸出依賴 Python set 的走訪順序（改用排序會讓 7 個 golden run 中 4 個不同）。Rust 在 `rust/src/python.rs` 重現 CPython 3.10 的 int／frozenset／tuple hash 與 setobject.c 的順序。
  3. 門檻用嚴格的 `>`。joint-likelihood 權重下 clade 的比例可能因捨入略大於 1，所以 `--consensus-threshold 1` 在部分 run 仍保留 clade；沒有任何 clade 通過時，原版丟 NetworkXError "The node root is not in the digraph"。
  4. 有 2 個 root 的樹（real_a2_err004）在 `-w counts` 與門檻 0.9 時也因此 crash。
  5. 門檻 0 在 4 個 run 丟 "Inconsistent set of clades"，是否發生取決於 set 順序。
  6. `convert_dtypes` 會把全為整數值的浮點欄印成整數（隨機樹 run 的 alpha 印成 `1`）。
  7. trace 依 Python `hash((clades, outliers))` 分組，依 hash 遞增排列。
- **M6 的偏差**：
  - 不同 topology 的 log_p 完全相同時，原版用 pandas → numpy quicksort argsort 排序；這台 AVX2 機器上 numpy 2.2 走不穩定的 SIMD sort，結果依 CPU 而定。Rust 不模仿，保留 hash 分組順序並在 stderr 警告。golden 沒有這種 tie。
  - topologies 的 tar header 不同（原版寫入暫存檔的 mtime／uid，Rust 寫 mtime 0）；member 名稱、順序、內容相同。
  - 不輸出原版 click 的進度訊息。
  - consensus 裡兩個 clade 重新標號後相同時，Rust 回傳錯誤；原版會建出不是樹的圖。
  - `-i` 吃 TSV trace 目錄，不吃 h5。
- **M6 審查（sonnet）找到、尚未處理的風險**：
  - ~~consensus 樹的 child 順序~~：已修（haploclone `5c887a1`）。見下面「consensus 的 child 順序」。
  - ~~用重算的 hash 分組~~：已修（haploclone `2c5cdc8`），改用存的 `tree_hash`。
  - consensus 權重逐位相同依賴 numpy 2.2 的 pairwise sum 與 glibc `exp`；`--consensus-threshold 1` 在 3 個 run 能通過就是靠這個捨入。
  - 測試資料的缺口：golden 都是 1 chain、只有 1 個 run 有多樣本、沒有 int 型 id、沒有 log_p tie。
- **consensus 的 child 順序（map.py）**：`build_phyclone_tree_from_nx` 先把每個 node 接在 dummy root 下，再用 `insert_node_on_in_edges_multiple` 搬 children。這個呼叫先加新邊再刪舊邊，rustworkx 會重用最後釋放的 edge slot。networkx 依 edge index 列 children，所以 CCF convolution 看到的是加邊順序的一個 rotation；兄弟節點資料相同時，它決定誰拿哪個 CCF。Rust 重播 slot 配置（`phyclone_edge_indices`）。rustworkx 自己的 child 順序（label、newick、clade）仍是 newest edge first。測試：`child_order.json`（45 棵 consensus 樹，舊順序有 14 棵不同）、`tied_siblings.py`（舊 binary 的 `consensus_table`／`sample_prev` 和原版不同，我自己重跑確認）。
- **M7 的決定與偏差**：
  - outlier、loss prior、fully-adapted、bootstrap、outlier Gibbs、subtree＋outlier 都照原版移植，golden README 6.1 的 14 項怪癖都重現。bootstrap 的兩個 proposal 質量不一致也照抄（第 7 節決定 5）。
  - assign-loss 的 Monte Carlo 用 ChaCha8 stream 0，只能和原版在 Monte Carlo 誤差內一致（lost 集合相同，p 值差 ≤1.9 SE）；resize 分支不抽樣，直接算，和原版逐位相同。Rust 的 chain 一律用 stream i+1，所以 loss 檢定不會像原版那樣移動 chain 的 RNG。
  - V3 看不到 bootstrap 的回歸和 subtree 的修正（M7a 量過）；這兩項靠 `tests/moves_m7.rs` 對照原版的 move 層級值（1212 個 log q／log p，相對差 ≤7e-15）。
  - V3 的 M7 表：13 個設定、各 15 個 seed，149/149 PASS（`v3/rust_m7/compare.txt`）。
- 誤差模型的 pair score 用 400 點的 midpoint grid 積分；HP 不確定性的門檻 Q_MIN = 0.05。
