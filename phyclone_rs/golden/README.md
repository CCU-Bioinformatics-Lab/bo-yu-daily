# PhyClone 原版的凍結輸入與輸出（golden，2026-10-26）

目的：在用 Rust 重寫 PhyClone 之前，凍結原版（Python PhyClone ＋ `tools/` 的 A1／A2／C4 擴充）的輸入與輸出。Rust 版必須在這些 fixture 上對齊，才算正確。

版本：PhyClone submodule `27383246`；`tools/phyclone_hp.py`、`tools/phyclone_pairs.py` 取自 repo commit `3b91b17`；Python 3.10.12、numpy 2.2.6、scipy 1.15.3、pandas 2.3.3、rustworkx 0.18.1、numba 0.68.0、h5py 3.16.0。完整清單與每個檔案的 sha256：`MANIFEST.json`。

## 1. 已驗證〔實測〕

| 檢查 | 結果 |
|---|---|
| fixture 可重現：`freeze.py --check` 重產後逐 byte 比對 | 53 個 fixture 完全相同 |
| fixture 描述的就是 sampler 的模型：用 fixture 重建 7 個參考 run 的 MAP 樹，在該 run 的 alpha 下重算 `log_p_one`（含 pair term），和 trace 存的值比較 | 7／7 一致，\|差\| ≤ 9.1e-13 |
| 原版端到端可重現：用相同 seed 重跑 `upstream_clusters`、`e0_base_bin` | topology report 逐 byte 相同 |

所以：**Python 原版在固定 seed 下是 deterministic 的**。之後改 Python 端（例如 FSCRP prior）時，可以拿 `runs/` 做逐位回歸測試。Rust 版的 RNG 不可能和 numpy 逐位一致，所以端到端只能做統計比較（第 4 節）。

## 2. 內容

```
golden/
  cases.tsv              5 個案例與來源
  runs.tsv               7 個參考 run 的參數
  run_reference.sh       複製輸入、跑參考 run（L1、L6）
  freeze.py              從輸入與參考 trace 產生 fixtures/（L2–L5）
  verify_against_traces.py
  MANIFEST.json
  cases/<case>/input/    輸入原樣複製；壓力樹與隨機樹另有 truth/（truth.tsv、truth_tree.tsv）
  runs/<run>/            command.txt、run.log、run_seconds.txt、trace.h5、map_*、consensus_*、
                         topology_report.tsv、topologies.tar.gz
  fixtures/              datapoints/、pairs/、trees/、scores/、SHA256SUMS
```

### 2.1 案例

| case | 來源 | 為什麼選它 |
|---|---|---|
| `stress_e0_s1` | `lab_report/2026-10-25_c4_robustness/sims/x10_e0_s1` | 壓力樹，無觀測誤差 |
| `stress_real_s1` | 同上 `x10_real_s1` | 校正後的 ONT 誤差；低 VAF 的 s7_07 HP 被判錯 |
| `stress_b03_s1` | 同上 `x10_b03_s1` | 3% base error（失效模式 1） |
| `random_spec_0000` | `lab_report/2026-10-25_random_tree_phyclone_baseline/sims/spec_0000` | TRACERx 隨機樹，186 個 SNV，94 個 CN segment，depth 50 |
| `upstream_mixing_small` | `research/phyclone_research/PhyClone/examples/data` | upstream 範例：4 個樣本、beta-binomial、cluster 檔 |

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

樹的來源：每個參考 trace 取 MAP 加上 25 個平均間隔的 iteration；真值樹；每個案例再加 15 棵固定 seed 的隨機樹（1–8 個 node，可以有多個 root）。重複的樹只留一棵，其他 id 記在 `aliases`。

| case | 樹數 | node 數 | root 數 |
|---|---|---|---|
| stress_e0_s1 | 42 | 1–8 | 1–3 |
| stress_real_s1 | 41 | 2–8 | 1–2 |
| stress_b03_s1 | 67 | 1–8 | 1–4 |
| random_spec_0000 | 16 | 1–8 | 1–4 |
| upstream_mixing_small | 13 | 1–7 | 1–5 |

## 3. 重產

```bash
bash phyclone_rs/golden/run_reference.sh                       # 約 5 分鐘（7 個 run 平行）
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
$PY phyclone_rs/golden/freeze.py                               # 約 15 秒
$PY phyclone_rs/golden/freeze.py --check                       # 應印出 identical
$PY phyclone_rs/golden/verify_against_traces.py                # 應印出 OK
```

**不要隨意重產。** golden 的意義是「凍結」。只有在刻意改變原版行為、而且記錄原因之後，才重產並更新 `MANIFEST.json`。

## 4. Rust 版的對齊標準（提案）

| 層 | 標準 |
|---|---|
| L2 datapoints | 每個元素 \|差\| ≤ 1e-10，或相對差 ≤ 1e-12 |
| L3 prior 各項、multiplicity | ≤ 1e-10（只有對數階乘與加總） |
| L3 data_log_likelihood、log_p、log_p_one | ≤ 1e-6。原版用 FFT 做 convolution，換成不同的 FFT 或直接 convolution，會有 ~1e-9 量級的差 |
| L4 pair scores、pair term | ≤ 1e-8（midpoint grid 積分；grid 大小必須一樣是 400） |
| L5 clone table | node 對應後 ccf ≤ 1e-6；結構完全相同 |
| L6 端到端 | 不能逐位比較。用相同設定跑多個 seed，比較 posterior 摘要（clone 數分布、topology 類別比例、`c3_under_c4` 等）與 `lab_report/` 的長 run 結果是否在 seed 間的變異範圍內 |

## 5. 時間基準（要加速的對象）

| 項目 | 時間 |
|---|---|
| 參考短 run（1 chain、220 iteration） | 106–282 秒；C4 約讓時間變成 1.6–2 倍 |
| 壓力樹長 run（4 chain、1100 iteration），24 個平行 | 一組 24 個 run 43–44 分鐘；36 個 run 61 分鐘 |
| 隨機樹長 run（4 chain、1100 iteration），120 個 | 中位數 1534 秒，範圍 581–3864 秒 |

## 6. 觀察到的原版行為（照實凍結，沒有修改）

- **隨機樹的短 run 卡在一棵樹上。** `random_a1_bin`、`random_base_betabin` 在 220 個 iteration 中都只有 1 個 node，alpha 一直是 1.0。長 run（4 chain、1100 iteration）最多推出 3 個 clone（`2026-10-25_random_tree_phyclone_baseline`）。〔實測〕
- **upstream 範例的 alpha 很高**：MAP 樣本的 alpha 是 280.6。〔實測〕原因沒有查。
- C4 的 pair term 是本研究在 `tools/` 加的擴充，不屬於 upstream PhyClone。Rust 版如果要涵蓋它，要把 `tools/phyclone_pairs.py` 的語意一起移植。

## 7. 沒有凍結的功能

- outlier 模型（`--outlier-prob` > 0）、`--assign-loss-prob`、`--user-provided-loss-prob`、`--high-loss-prob`
- `--proposal` 的 `semi-adapted` 以外選項、`--subtree-update-prob` > 0、`--num-particles` ≠ 100、`--thin` ≠ 1、`--max-time`
- consensus 的 `--weight-type` 非預設值、`--consensus-threshold` 非預設值
- 多 chain 合併的後處理（參考 run 只有 1 chain）

Rust 版若要支援這些功能，要先補凍結。
