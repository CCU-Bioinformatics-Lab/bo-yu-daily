# PhyClone 原版的凍結輸入與輸出（golden，2026-10-26；M7 補凍結 2026-10-27）

目的：在用 Rust 重寫 PhyClone 之前，凍結原版（Python PhyClone ＋ `tools/` 的 A1／A2／C4 擴充）的輸入與輸出。Rust 版必須在這些 fixture 上對齊，才算正確。

版本：PhyClone submodule `27383246`；`tools/phyclone_hp.py`、`tools/phyclone_pairs.py` 取自 repo commit `3b91b17`；Python 3.10.12、numpy 2.2.6、scipy 1.15.3、pandas 2.3.3、rustworkx 0.18.1、numba 0.68.0、h5py 3.16.0。完整清單與每個檔案的 sha256：`MANIFEST.json`。

## 1. 已驗證〔實測〕

| 檢查 | 結果 |
|---|---|
| fixture 可重現：`freeze.py --check` 重產後逐 byte 比對 | 75 個 fixture 完全相同（原有 53 個＋M7 的 22 個） |
| M7 沒有動到原有 fixture：原有 53 個檔案的 sha256 和 commit `2797c5c` 的 `SHA256SUMS` 相同 | 53／53 相同；`SHA256SUMS` 只多了 22 行 |
| M7 沒有動到原有輸入與 run：`manifest.py --check --against 2797c5c` | 117／117 個檔案相同 |
| fixture 描述的就是 sampler 的模型：用 fixture 重建參考 run 的 MAP 樹，在該 run 的 alpha 下重算 `log_p_one`（含 pair term；M7 run 開 outlier 模型），和 trace 存的值比較 | 15／15 一致（原有 7 個＋M7 的 8 個），\|差\| ≤ 9.1e-13 |
| 原版端到端可重現：用相同 seed 重跑 `upstream_clusters`、`e0_base_bin` | topology report 逐 byte 相同 |
| M7 的 16 個 run 端到端可重現：`check_rerun.py` 用 `command.txt` 重跑，比對 trace.h5 的所有 dataset 與 attribute（`time` 欄除外）、map／consensus／topology report 輸出 | 16／16 完全相同（含 4-chain run；`real_a2_err004_out001` 的 consensus 兩次都同樣失敗，見第 6 節）。`upstream_clusters` 也用同一支檢查重跑過，相同 |
| M7 run 的確定性質：`check_m7_runs.py` | `e0_thin5` 正好是 `e0_base_bin` 的第 0、5、10…個樣本；`e0_alpha25_fixed` 每個樣本 alpha = 2.5；`e0_maxtime0` 只有 1 個樣本（iter 0）；`e0_chains4` 4 個 chain 各 200 個樣本，逐樣本等於 V3 baseline 的 `chains4` seed 1 |

所以：**Python 原版在固定 seed 下是 deterministic 的**。之後改 Python 端（例如 FSCRP prior）時，可以拿 `runs/` 做逐位回歸測試。Rust 版的 RNG 不可能和 numpy 逐位一致，所以端到端只能做統計比較（第 4 節）。

## 2. 內容

```
golden/
  cases.tsv              6 個案例與來源
  runs.tsv               23 個參考 run 的參數（第 2–8 列原有，第 9–24 列 M7）
  run_reference.sh       複製輸入、跑參考 run（L1、L6）；可只跑指定的 run
  freeze.py              從輸入與參考 trace 產生 fixtures/（L2–L5），最後呼叫 freeze_m7.py
  freeze_m7.py           M7 的 fixtures（outlier、loss prior、precision、grid ≥ 1000）
  verify_against_traces.py
  check_rerun.py         重跑 run，檢查 trace 與後處理輸出完全相同
  check_m7_runs.py       M7 run 的確定性質（thin、alpha 固定、max-time 0、多 chain）
  manifest.py            寫入／檢查 MANIFEST.json 的 sha256 表
  probes/                重現第 6 節原版怪癖的小程式
  MANIFEST.json
  cases/<case>/input/    輸入原樣複製；壓力樹與隨機樹另有 truth/（truth.tsv、truth_tree.tsv）；
                         FS-CRP 案例另有 ground_truth/ 與 paper_output/（論文 0.7.0 的輸出）
  runs/<run>/            command.txt、run.log、run_seconds.txt、trace.h5、map_*、consensus_*、
                         topology_report.tsv、topologies.tar.gz
  fixtures/              datapoints/、pairs/、trees/、scores/、outlier/、SHA256SUMS
```

### 2.1 案例

| case | 來源 | 為什麼選它 |
|---|---|---|
| `stress_e0_s1` | `lab_report/2026-10-25_c4_robustness/sims/x10_e0_s1` | 壓力樹，無觀測誤差 |
| `stress_real_s1` | 同上 `x10_real_s1` | 校正後的 ONT 誤差；低 VAF 的 s7_07 HP 被判錯 |
| `stress_b03_s1` | 同上 `x10_b03_s1` | 3% base error（失效模式 1） |
| `random_spec_0000` | `lab_report/2026-10-25_random_tree_phyclone_baseline/sims/spec_0000` | TRACERx 隨機樹，186 個 SNV，94 個 CN segment，depth 50 |
| `upstream_mixing_small` | `research/phyclone_research/PhyClone/examples/data` | upstream 範例：4 個樣本、beta-binomial、cluster 檔 |
| `fscrp_loss_0.2_run0` | `/big8_disk/boyu114/phyclone_dataset/FS-CRP_Loss/data_archive/loss_prop_0.2_run0` | PhyClone 論文的 FS-CRP_Loss trial（M7、之後 V4 的起點）：8 個樣本、600 個 SNV、10 個 PyClone-VI cluster，cluster 檔是 gzip（`results.tsv.gz`）。用 rng seed 1 時 `--assign-loss-prob` 正好判出 1 個 lost cluster（9），所以 loss prior 的高、低兩支都會跑到。`results_user_loss.tsv` 是 `run_reference.sh` 從 `results.tsv.gz` 產生的：多一欄 `outlier_prob` = 0.001 ×（cluster + 1），cluster 3 改成 0、cluster 9 改成 0.4（測 p = 0 的分支與高值） |

FS-CRP 案例的資料檔都一樣大（600 個 SNV、8 個樣本），所以挑第一個 loss 比例 0.2 的 trial。〔實測〕

### 2.2 參考 run（L6，`runs.tsv`）

共同設定：`-b 20 -n 200 --num-chains 1 --seed 1`，outlier 關閉（PhyClone 預設），grid 101，precision 400。

| run | case | emission | density | C4 | 時間（秒） |
|---|---|---|---|---|---|
| `e0_base_bin` | stress_e0_s1 | base | binomial | — | 143 |
| `real_a2_err004` | stress_real_s1 | A2 | binomial | 誤差模型 e 0.004 | 282 |
| `b03_base_eps001` | stress_b03_s1 | base | binomial | eps 0.01 | 225 |
| `b03_base_err003_hpu` | stress_b03_s1 | base | binomial | 誤差模型 e 0.03＋HP 不確定性 | 275 |
| `random_a1_bin` | random_spec_0000 | A1 | binomial | — | 120 |
| `random_base_betabin` | random_spec_0000 | base | beta-binomial | — | 106 |
| `upstream_clusters` | upstream_mixing_small | base | beta-binomial | —（cluster 檔） | 8 |

7 個 run 同時跑；時間是單一 run 的牆鐘時間。

M7 run（`runs.tsv` 第 9–24 列）。共同設定相同；run 的 argv 有某個共同選項時，用 argv 的值（只有 `e0_chains4` 的 `--num-chains 4`）。全部經由 `tools/phyclone_hp.py --hp-mode base`（`real_a2_err004_out001` 用 A2），和原有 run 一樣。

| run | case | 測的功能 | 時間（秒） |
|---|---|---|---|
| `e0_out001` | stress_e0_s1 | outlier 模型 `-l 0.01`，semi-adapted | 178 |
| `e0_out001_boot` | stress_e0_s1 | outlier＋`-p bootstrap`（0.8.0 已知回歸，照實凍結） | 240 |
| `e0_boot` | stress_e0_s1 | `-p bootstrap`，outlier 關閉 | 229 |
| `e0_out001_fully` | stress_e0_s1 | outlier＋`-p fully-adapted` | 716 |
| `real_a2_err004_out001` | stress_real_s1 | A2＋C4（e 0.004）＋outlier `-l 0.01` | 180 |
| `fscrp_out` | fscrp_loss_0.2_run0 | cluster 檔（gzip）＋outlier `-l 0.01`，beta-binomial | 21 |
| `fscrp_assign_loss` | fscrp_loss_0.2_run0 | `--assign-loss-prob`（`-l` 預設 0，CLI 改成 1e-4；`--high-loss-prob` 0.4） | 22 |
| `fscrp_user_loss` | fscrp_loss_0.2_run0 | `--user-provided-loss-prob`，`results_user_loss.tsv`（`-l` 同上改成 1e-4） | 20 |
| `e0_chains4` | stress_e0_s1 | `--num-chains 4`（多 chain 的 trace 與後處理） | 161 |
| `e0_subtree05` | stress_e0_s1 | `-s 0.5` | 141 |
| `e0_np20_rt08` | stress_e0_s1 | `--num-particles 20 --resample-threshold 0.8` | 44 |
| `e0_moves` | stress_e0_s1 | `--num-samples-data-point 3 --num-samples-prune-regraph 0` | 198 |
| `e0_alpha25_fixed` | stress_e0_s1 | `--concentration-value 2.5 --no-concentration-update` | 200 |
| `e0_thin5` | stress_e0_s1 | `--thin 5` | 148 |
| `e0_maxtime0` | stress_e0_s1 | `--max-time 0`（唯一確定的 max-time 值） | 6 |
| `upstream_grid1000` | upstream_mixing_small | `--grid-size 1000`（convolution 改走 FFT） | 10 |

16 個 run 同時跑（`e0_maxtime0` 先單獨跑過）。合計約 2,500 run-秒；4-chain 算 4 core，約 0.8 core-hour。

### 2.3 Fixtures（L2–L5，`freeze.py`）

所有檔案都是 JSON，浮點數用 round-trip 十進位。`inf`／`nan` 寫成字串。

| 層 | 檔案 | 內容 |
|---|---|---|
| L2 | `datapoints/<case>__<loader>.json` | 每個 SNV（或 cluster）的 `value`（樣本 × grid 的 log-likelihood）、`idx`、`name`。loader：`base_binomial`、`base_betabin`、`a1_binomial`、`a2_binomial`、`upstream_clusters` |
| L3 | `trees/<case>.json` | 每棵樹的結構（`nodes`：node → parent、mutations）；在 α = 0.5／1／2.5 下的 FSCRP prior 各項（`crp`、Σ log(n−1)!、`r_term`、`multiplicity`、`prior_log_p`、`prior_log_p_one`、node 數、root 數）；各 pair model 的 C4 pair term |
| L3 | `scores/<case>__<loader>.json` | 每棵樹的 `data_log_likelihood`（樣本 × grid），以及 `TreeJointDistribution` 在各 α 下的 `log_p`、`log_p_one`（不含 pair term，outlier 關閉） |
| L4 | `pairs/<case>__<pair model>.json` | 合格 pair 與 4 個 relation 分數（same、ancestor、descendant、branch）。pair model：`eps0.01`、`eps0.01_w0.3`、`err0.004`、`err0.03`、`err0.004_hpu`、`err0.03_hpu` |
| L5 | `scores/...` 的 `clone_table` | MAP 樹與真值樹的 clone table（`get_clone_table`：clone_id、ccf、clonal_prev 等） |
| L5 | `runs/<run>/map_*`、`consensus_*`、`topology_report.tsv` | 給定 trace 的後處理輸出 |

M7 的 fixtures（`freeze_m7.py`，格式同上）：

| 層 | 檔案 | 內容 |
|---|---|---|
| L2 | `outlier/terms.json` | `compute_outlier_prob(p, size)`：p ∈ {0, 1e-300, 1e-4, 0.01, 0.4, 0.999, 1} × size ∈ {1, 2, 58}；常數 likelihood（全為 0）的 `outlier_marginal_prob` 與 closed form，grid 11／101／1000（論文的積分在這裡是 0） |
| L2 | `datapoints/<case>__<M7 loader>.json` | 原有欄位，加上每個點的 `outlier_prob`、`outlier_prob_not`、`outlier_marginal_prob`；`settings`（loader 的全部參數）。cluster loader 另有 `clusters`（每個 cluster 的大小與原始機率 p）。`clusters_assign_loss` 另有 `loss_assignment`：truncal cluster、truncal 的 chromosome 陣列、每個 cluster 的 Monte Carlo 結果（`samples_fewer`、`num_unique_sum`、`pvalue`、`estimate`、是否 `resized`）與 lost cluster |
| L3 | `trees/<case>__m7.json`、`trees/fscrp_loss_0.2_run0.json` | 樹的結構多一欄 `outliers`（在 outlier node 上的點）、`num_outliers`；prior 各項、C4 pair term（壓力樹案例，6 個 pair model） |
| L3 | `scores/<case>__<M7 loader>.json` | `outlier_modelling_active`（= outlier_prob > 0）、`grid_size`；每棵樹：`data_log_likelihood`、各項單獨的值（`outlier_prior`、`outlier_marginal`、`data_log_p`、`data_log_p_one`），以及各 α 下的 `log_p`、`log_p_one`；MAP 樹的 `clone_table`。grid 1000 另有 `log_p@1.0_direct_conv`、`log_p_one@1.0_direct_conv`（改用 `np.convolve` 算的值）與 `fft_noise_dominated` |

M7 loader：

| loader | case | 設定 |
|---|---|---|
| `base_binomial_out0.01` | stress_e0_s1 | PhyClone `load_data`，`-l 0.01` |
| `base_binomial_grid1000` | stress_e0_s1 | grid 1000，outlier 關閉 |
| `a2_binomial_out0.01` | stress_real_s1 | `tools/` A2 loader，`-l 0.01` |
| `clusters_out0.01` | fscrp_loss_0.2_run0 | cluster 檔，`-l 0.01` |
| `clusters_assign_loss` | fscrp_loss_0.2_run0 | `--assign-loss-prob`，`-l 1e-4`，high 0.4，rng = `default_rng(1)` |
| `clusters_user_loss` | fscrp_loss_0.2_run0 | `--user-provided-loss-prob`，`results_user_loss.tsv`，`-l 1e-4` |
| `clusters_user_loss_nocol` | fscrp_loss_0.2_run0 | `--user-provided-loss-prob`，但 cluster 檔沒有 `outlier_prob` 欄（退回全域 1e-4） |
| `upstream_clusters_grid1000` | upstream_mixing_small | grid 1000（FFT），outlier 關閉 |
| `upstream_clusters_prec100` | upstream_mixing_small | `--precision 100`（只有 datapoints） |

樹的來源：每個參考 trace 取 MAP 加上 25 個平均間隔的 iteration；真值樹；每個案例再加 15 棵固定 seed 的隨機樹（1–8 個 node，可以有多個 root）。重複的樹只留一棵，其他 id 記在 `aliases`。

| case | 樹數 | node 數 | root 數 |
|---|---|---|---|
| stress_e0_s1 | 42 | 1–8 | 1–3 |
| stress_real_s1 | 41 | 2–8 | 1–2 |
| stress_b03_s1 | 67 | 1–8 | 1–4 |
| random_spec_0000 | 16 | 1–8 | 1–4 |
| upstream_mixing_small | 13 | 1–7 | 1–5 |

M7 的樹：每個 M7 參考 trace 取 MAP 加上 25 個 iteration；3 棵固定的樹（全部是 outlier、1 個 node、1 個 node＋1 個 outlier）；15 棵固定 seed 的隨機樹，每棵有 1 到 ⌊n/3⌋ 個 outlier，其餘分到 1–8 個 node。

| trees 檔 | 樹數 | node 數 | outlier 數 | trace 樹中有 outlier 的 |
|---|---|---|---|---|
| stress_e0_s1__m7 | 95 | 0–8 | 0–100 | 5 |
| stress_real_s1__m7 | 44 | 0–8 | 0–100 | 26 |
| fscrp_loss_0.2_run0 | 19 | 0–9 | 0–10 | 0（3 個 run 的 200 個樣本都是同一棵樹） |
| upstream_mixing_small__m7 | 19 | 0–7 | 0–7 | 0 |

## 3. 重產

```bash
bash phyclone_rs/golden/run_reference.sh [RUN ...]             # 全部約 12 分鐘（最慢的是 e0_out001_fully）
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
$PY phyclone_rs/golden/freeze.py                               # 約 35–50 秒
$PY phyclone_rs/golden/freeze.py --check                       # 應印出 identical
$PY phyclone_rs/golden/verify_against_traces.py                # 應印出 OK
$PY phyclone_rs/golden/check_rerun.py RUN ...                  # 每個 run 應印出 identical
$PY phyclone_rs/golden/check_m7_runs.py                        # 每行應為 OK
python3 phyclone_rs/golden/manifest.py [--check [--against REV]]
```

**不要隨意重產。** golden 的意義是「凍結」。只有在刻意改變原版行為、而且記錄原因之後，才重產並更新 `MANIFEST.json`。

## 4. Rust 版的對齊標準（提案）

| 層 | 標準 |
|---|---|
| L2 datapoints | 每個元素 \|差\| ≤ 1e-10，或相對差 ≤ 1e-12 |
| L3 prior 各項、multiplicity | ≤ 1e-10（只有對數階乘與加總） |
| L3 data_log_likelihood、log_p、log_p_one | ≤ 1e-6。grid < 1000 時原版用 `np.convolve`（OpenBLAS `cblas_ddot`），不是 FFT（2026-10-26 M3 實測更正）；Rust 版照 OpenBLAS 的加總順序實作，fixture 上逐位相同 |
| L4 pair scores、pair term | ≤ 1e-8（midpoint grid 積分；grid 大小必須一樣是 400） |
| L5 clone table | node 對應後 ccf ≤ 1e-6；結構完全相同 |
| L6 端到端 | 不能逐位比較。用相同設定跑多個 seed，比較 posterior 摘要（clone 數分布、topology 類別比例、`c3_under_c4` 等）與 `lab_report/` 的長 run 結果是否在 seed 間的變異範圍內 |
| M7 outlier 各項（`outlier/terms.json`、datapoints 的 outlier 欄位） | ≤ 1e-12（只有 log 與 logaddexp 累加）；p = 0 或 1 的值是 log(2.2250738585072014e-308) × size，要逐位相同 |
| M7 `loss_assignment` | lost cluster 集合必須相同。Rust 的 RNG 不同，所以 `pvalue`、`estimate` 只能在 Monte Carlo 誤差內相同：10,000 次抽樣的標準誤 ≤ 0.005。這個案例離門檻最近的是 cluster 0（pvalue 0.0328，門檻 0.01），差約 12 個標準誤，所以集合穩定〔推論〕 |
| M7 grid 1000 的 scores | `fft_noise_dominated` 為 false 的樹：≤ 1e-6。為 true 的樹（都是隨機樹）：結果由 FFT 的捨入雜訊決定，只要求 Rust 的值 ≥ `*_direct_conv` 的值減 1e-6，不要求等於 fixture（見第 6 節） |
| M7 run 的確定性質 | Rust 自己的 trace 也要滿足 `check_m7_runs.py` 的 thin、alpha、max-time 0、chain 數性質（和 seed 無關） |

## 5. 時間基準（要加速的對象）

| 項目 | 時間 |
|---|---|
| 參考短 run（1 chain、220 iteration） | 106–282 秒；C4 約讓時間變成 1.6–2 倍 |
| 壓力樹長 run（4 chain、1100 iteration），24 個平行 | 一組 24 個 run 43–44 分鐘；36 個 run 61 分鐘 |
| 隨機樹長 run（4 chain、1100 iteration），120 個 | 中位數 1534 秒，範圍 581–3864 秒 |

## 6. 觀察到的原版行為（照實凍結，沒有修改）

- **隨機樹的短 run 卡在一棵樹上。** `random_a1_bin`、`random_base_betabin` 在 220 個 iteration 中都只有 1 個 node。alpha 只有 iter 0 是 1.0，之後塌到下限約 1e-10（`random_a1_bin` 有 170／200 個樣本是 1e-10；2026-10-26 M5／V3 實測更正）。長 run（4 chain、1100 iteration）最多推出 3 個 clone（`2026-10-25_random_tree_phyclone_baseline`）。〔實測〕
- **upstream 範例的 alpha 很高**：MAP 樣本的 alpha 是 280.6。〔實測〕原因沒有查。
- C4 的 pair term 是本研究在 `tools/` 加的擴充，不屬於 upstream PhyClone。Rust 版如果要涵蓋它，要把 `tools/phyclone_pairs.py` 的語意一起移植。

### 6.1 M7 找到的原版怪癖（照實凍結，沒有修改）

upstream 路徑都相對於 `research/phyclone_research/PhyClone/phyclone/`。

1. **outlier marginal 是三角形的雙重和，不是論文的單一積分**（筆記 `06` 實作第 1 項）。`data/base.py:29-34`：先對 grid 做 `logaddexp.accumulate`（累加到 j），再 `logsumexp`，兩次都乘 1/G。likelihood 是常數 1 時，論文的值是 0，程式的值是每個樣本 log((G+1)/(2G))：G = 101 時 −0.683，G = 1000 時 −0.692。`outlier/terms.json` 凍結了這組值。〔實測〕
2. **bootstrap＋outlier 的 proposal 質量不一致**（筆記 `06` 實作第 3 項，0.8.0 回歸）。`smc/kernels/bootstrap.py:44-45, 99-104` 抽樣時 outlier／既有 node／新 node 是 0.1／0.35／0.55，`log_p`（同檔 59-86）記的是 0.1／0.45／0.45。另外找到第二個不一致：parent particle 存在但沒有 root（前面的點都是 outlier）時，`sample` 用 `parent_is_empty_tree`，抽到新 node 的機率是 0.9，但 `log_p` 只看 `parent_particle is None`，記成 0.45。`probes/bootstrap_mass.py` 抽 40,000 次：0.097／0.35／0.554 對 0.1／0.45／0.45；沒有 root 時 0.897 對 0.45。semi-adapted 兩種情況都一致。`e0_out001_boot` 照實凍結。〔實測〕
3. **outlier node 上只有一個點時，Gibbs move 動不了它。** `mcmc/gibbs_mh.py:30` 只重新指派「所在 node 有 > 1 個點」的點；outlier node 也套用這條。所以唯一的 outlier 只能靠 PG 離開。〔程式閱讀〕
4. **consensus 在沒有任何 clade 超過門檻時直接失敗。** `real_a2_err004_out001`：top tree 有 29 個 outlier；每個樣本的 outlier 集合不同，clade（mutation 集合）跟著不同，最大的 clade 支持度只有 0.405（`--consensus-threshold` 0.5，`process_trace/consensus.py:111` 用嚴格的 `>`）。consensus graph 是空的，`get_tree_from_consensus_graph`（`process_trace/process_trace.py:221`）沒有加入 root，networkx 報 `The node root is not in the digraph.`。這個 run 沒有 `consensus_*` 檔，錯誤在 `post.log`，重跑時同樣失敗。〔實測〕
5. **grid ≥ 1000 時 FFT 的捨入雜訊決定不合理樹的 likelihood。** `tree/utils.py:61-67` 改用 `scipy.signal.fftconvolve`；雜訊約為 children 最大值乘積的 1e-16，比真正的 convolution 大很多，`log_d <= 0` 的位置再被設成 1e-100（同檔 51 行）。和 `np.convolve` 比，grid 1000 的 score fixture 中 `log_p_one` 差超過 1e-6 的樹全是隨機樹：upstream 19 棵中 10 棵，最多高出 934 個 log 單位；壓力樹 95 棵中 11 棵，最多 338。trace 樹與 MAP 樹都差 0（另用 scratch 程式算壓力樹兩個 trees 檔的 103 棵 trace 樹，也都差 0）。fixture 用 `fft_noise_dominated` 標出這些樹。〔實測〕
6. **`--user-provided-loss-prob` 的 `fillna` 永遠不會執行。** `data/pyclone.py:140` 用全域值補 NaN，但 cluster 檔的 validator 先拒絕有 NaN 的 `outlier_prob` 欄（`Column contains missing or NaN values`）。這行在 pandas 2.3 另外會發 chained-assignment 的 FutureWarning。〔實測〕
7. **cluster 檔同一個 mutation 有兩個不同的 `outlier_prob` 時，這個 mutation 算兩次。** `_setup_cluster_df` 以（mutation、cluster、outlier_prob）去重複（`data/pyclone.py:144`），合併後這個 mutation 有兩列：likelihood 加兩次、cluster 大小多 1，cluster 的機率取第一列（同檔 89 行）。`probes/cluster_outlier_prob_rows.py`：cluster 8 的 outlier_prob 從 log(0.009) 變成 2 × log(0.5)，likelihood 剛好變兩倍。〔實測〕
8. **`--assign-loss-prob` 在 chain 開始前就用掉主 RNG。** `data/cluster_outlier_probabilities.py:51` 每個受測 cluster 抽 10,000 次，用的是 `run.py` 的 `rng_main`，所以 1-chain run 的 sampler 亂數序列和沒開這個選項時不同。cluster 比 truncal cluster 大時，`np.resize`（同檔 40 行）把 truncal 陣列循環補長，`replace=False` 抽出全部元素，所以 unique 數固定、測試沒有隨機性；本案例 truncal cluster（1，233 個 SNV）最大，沒有跑到這一支。〔程式閱讀；本案例 `resized` 全為 false 是實測〕
9. **outlier_prob = 0 不會關掉 outlier。** loss prior 的 CLI 選項開著、`-l` 是 0 時，CLI 把 `-l` 改成 1e-4（`cli.py:202-221`）。cluster 自己的機率是 0 時（`results_user_loss.tsv` 的 cluster 3），`compute_outlier_prob` 用最小的正規化 double：log P = −708.4 × size，不是 −inf。〔實測〕
10. **max-time 的兩個迴圈條件不同。** burn-in 用 `>`（`run.py:359`），主迴圈用 `>=`，而且在存入 trace 之後、更新 alpha 之前判斷（`run.py:286-293`）。兩段共用一個 timer。所以 `--max-time 0` 跑 1 個 burn-in iteration、存 1 個樣本；log 的 burn-in 結束行仍印 `iter: 20`。〔實測〕
11. **C4 pair term 跳過含 outlier 的 pair**（本研究的 `tools/`，不是 upstream）。`tools/phyclone_pairs.py:173-175`：任一端是 outlier 時這個 pair 貢獻 0。所以 outlier 可以避開 pair 的懲罰；`real_a2_err004_out001` 的 200 個樣本都有 outlier，最多 32／100 個 SNV。〔實測〕
12. **outlier 關閉時，outlier node 上的點完全不算分。** `TreeJointDistribution(outlier_modelling_active=False)` 不加 outlier prior、也不加 outlier marginal（`tree/distributions.py:186-204`）。grid 1000 的 score 檔用 outlier 關閉的設定為有 outlier 的樹評分，看得到這個行為。〔實測〕
13. **multi-chain 的 trace.h5 只在樣本層級相同。** `e0_chains4` 和 V3 baseline 的 `chains4` seed 1 命令相同（baseline 用絕對路徑、1 個 BLAS thread）。800 個樣本的 alpha、log_p_one、node 數與 canonical 樹逐位相同，但 chain 1–3 的 h5 有 242 個 item 不同（node 編號與樹的儲存）。同一個命令重跑 `e0_chains4` 則 h5 完全相同。原因沒有查。〔實測〕
14. **論文的 0.7.0 輸出把 lost cluster 9 判成 outlier，0.8.0 的短 run 沒有。** `paper_output/results.tsv` 中 cluster 9（58 個 SNV，`ground_truth/loss_dict.json` 的 lost clone）的 clone_id 是 −1。`fscrp_out`、`fscrp_assign_loss`、`fscrp_user_loss` 的 200 個樣本都是同一棵樹，cluster 9 在樹上。在 `clusters_assign_loss` 下，把 MAP 樹的 cluster 9 移到 outlier（children 接到它的 parent）會讓 `log_p_one` 低 40.8，所以 0.8.0 的模型在這棵樹附近也不偏好 outlier。論文用的 `-l` 與 loss 選項不知道。這是 V4 的問題，不是移植的問題。〔實測〕

## 7. 沒有凍結的功能

- `--max-time` > 0：結果取決於機器速度，不能凍結。只凍結了 `--max-time 0`。
- consensus 的 `--weight-type` 非預設值、`--consensus-threshold` 非預設值：golden 沒有凍結；M6 已直接和 upstream 比過（`decisions.tsv` M6 V2 gate）。
- `--assign-loss-prob` 中 cluster 比 truncal cluster 大的分支（第 6.1 節第 8 項）：本案例沒有跑到。
- `--high-loss-prob` 只用了預設 0.4；`--outlier-prob` 與 `--high-loss-prob` 的 CLI 驗證只看程式，沒有凍結（`cli.py:202-229`；`-l` ≥ high 時是否報錯，取決於 click 處理兩個選項的順序）。
- outlier 模型＋A1、beta-binomial 的 SNV 層級 loader：outlier 欄位的公式和 loader 無關，所以只凍結了 base、A2 與 cluster loader。
- 多 chain 只有 `e0_chains4` 一個 golden run（V3 另有 `e0_base_bin.chains4` 15 個 seed）。

## 8. M7：哪些功能用 V1 fixture，哪些只能用 V3

V1 是確定性的逐值比較；V3 是 `phyclone_rs/v3/` 的多 seed 統計比較。sampler 的路徑由 RNG 決定，所以只改 sampler 行為的選項只能用 V3。

| 功能 | V1（確定） | V3（統計） | 為什麼 |
|---|---|---|---|
| outlier 的 prior、marginal、joint | `outlier/terms.json`、M7 datapoints、M7 trees／scores | `e0_out001`、`real_a2_err004_out001`、`fscrp_out`；破壞版本 `noout`（只有 `real_a2_err004_out001` 與 `fscrp_out` 偵測得到） | 各項是確定的函數；SMC／Gibbs 指派 outlier 的部分要看 posterior |
| bootstrap、fully-adapted proposal | — | `e0_boot`、`e0_out001_boot`、`e0_out001_fully` | proposal 只改變 RNG 路徑。bootstrap＋outlier 的回歸會改變 SMC 的權重，Rust 照原版移植。但實測 V3 分不出 bootstrap 與 semi-adapted，也分不出這個回歸（`v3/README.md` 10.4 節），所以回歸要靠單元測試對第 6.1 節第 2 項的機率；fully-adapted 則分得出來 |
| loss prior（assign、user、沒有欄位時退回） | M7 datapoints（每個 cluster 的機率、`loss_assignment` 的每一步）、scores | `fscrp_assign_loss`、`fscrp_user_loss`；破壞版本 `noloss` | 機率的指派是確定的（assign 的 Monte Carlo 除外，見第 4 節）；之後的 sampler 看 V3 |
| `--subtree-update-prob` | — | `e0_subtree05` | 只改 sampler。注意：Rust 刻意修正了 PG subtree 重新加權的 bug（`decisions.tsv` M5），baseline 是原版行為，所以這一格 FAIL 時先查這個差異 |
| `--num-particles`、`--resample-threshold` | — | `e0_np20_rt08` | 只改 sampler；V3 對「目標分布相同、sampler 變弱」的檢出力是 0（`v3/README.md` 6.2 節 np20），所以這一格只能抓到明顯的錯 |
| `--num-samples-data-point`、`--num-samples-prune-regraph` | — | `e0_moves` | 只改 sampler |
| `--concentration-value`、`--no-concentration-update` | alpha 恆為 2.5（`check_m7_runs.py`） | `e0_alpha25_fixed` | alpha 是確定的；樹仍由 RNG 決定 |
| `--grid-size` ≥ 1000（FFT） | M7 datapoints／scores（grid 1000），附 `np.convolve` 的對照值 | `upstream_grid1000` | convolution 是確定的，但 FFT 的雜訊區不能逐位相同 |
| `--precision` | `upstream_clusters_prec100` datapoints | — | 只影響 beta-binomial 的 likelihood |
| `--thin` | thin 5 = thin 1 的每 5 個樣本（`check_m7_runs.py`） | — | thin 不抽亂數，Rust 對自己的 trace 檢查同一性質，比統計比較更強 |
| `--max-time` | `--max-time 0` → 1 個樣本 | — | 其他值和機器速度有關 |
| `--num-chains` | `e0_chains4` 每 chain 200 個樣本 | 既有的 `e0_base_bin.chains4` | 已有 15 個 seed 的 baseline，不再重跑 |
| 壓縮的 cluster 檔 | `fscrp_loss_0.2_run0` 的 `results.tsv.gz` | 同 V3 的 fscrp 設定 | **Rust 還不能讀 .gz**（`PORTING.md` 第 8 節），M7b 要加上 |

V3 baseline 的結果見 `phyclone_rs/v3/README.md` 第 10 節。
