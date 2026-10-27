# V3：Rust 版與 Python 版的統計比較（2026-10-26）

目的：Rust sampler 的 RNG 不可能和 numpy 逐位一致，所以端到端驗證（`PORTING.md` 第 3 節 V3）只能做統計比較。本目錄提供：

1. 一個 reader，把 Python `trace.h5` 和 Rust TSV trace（`PORTING.md` 第 5 節）讀成同一種形式。
2. 每個 run 的 posterior 摘要。
3. 每個摘要的判定規則（PASS／FAIL／INCONCLUSIVE），並用 Python 自己校正。
4. Python baseline：golden 的 7 個參考設定，各 15 個 seed，另有一個 4-chain 設定。
5. 一個指令：給 Rust 的 trace 根目錄，印出逐設定、逐摘要的判定表。

標記：〔實測〕＝本目錄計算；〔推論〕＝本檔推論。

## 1. 一個指令

```bash
PY="env PYTHONPATH=research/phyclone_research/PhyClone $HOME/venvs/phyclone/bin/python"
$PY phyclone_rs/v3/compare.py RUST_ROOT [--out verdicts.tsv]
```

- `RUST_ROOT/<config>/<seed dir>/`：每個 seed 一個目錄，內容是 TSV trace（有 `meta.json`）或 `trace.h5`。
- `<config>` 是 `golden/runs.tsv` 的 run 名稱（例如 `e0_base_bin`）。4-chain 設定叫 `e0_base_bin.chains4`。
- 每個 seed 必須用 golden 的 argv，加上 `-b 20 -n 200 --num-chains 1`（chains4 用 `--num-chains 4`）。seed 不必和 Python 相同。
- 建議每個設定跑 10 個 Rust seed。少於 4 個 seed 時，規則無法給出 FAIL，只會給 INCONCLUSIVE。
- Python 端讀 `baseline/summaries/<config>.json.gz`，不需要 trace.h5。
- 輸出欄位：`python`／`candidate`（純量時是平均與範圍）、`effect`（觀測距離 ÷ permutation 距離的中位數，null 下約為 1）、`p`、`verdict`。最後一行是整體判定。有 FAIL 時 exit 1。

在 Rust 版完成前，可以用 Python 的 trace 試跑：

```bash
$PY phyclone_rs/v3/compare.py phyclone_rs/v3/baseline/runs/fresh    # 5 個新 seed，應為 PASS
$PY phyclone_rs/v3/compare.py phyclone_rs/v3/baseline/runs/noc4     # 拿掉 C4，應為 FAIL
$PY phyclone_rs/v3/trace_io.py IN/trace.h5 OUT_DIR [--permute-seed N]   # h5 → TSV trace
```

## 2. 檔案

| 檔案 | 內容 |
|---|---|
| `trace_io.py` | 共同形式 `Trace`／`Tree`；`read_h5`、`read_tsv_dir`、`read_trace`；`write_tsv_dir`（h5 → TSV，可打亂 mutation 標籤） |
| `summaries.py` | 每個 run 的摘要（`run_summaries`）、真值指標、JSON 快取 |
| `compare.py` | 判定規則與上面的指令 |
| `run_baseline.py`、`variants.tsv` | 跑 Python baseline 與破壞版本（可中斷後續跑：有 `run_seconds.txt` 的 job 會跳過） |
| `summarize_baseline.py` | 把 `baseline/runs/` 轉成 `baseline/summaries/*.json.gz` 與 `per_seed.tsv` |
| `calibrate.py` | 校正：Python 對 Python 的誤判率、破壞版本的檢出力 |
| `check_seed1.py` | seed 1 是否和 golden 的 trace 完全相同 |
| `tests/test_v3.py`、`tests/fixture_trace/` | reader、摘要、規則的單元測試；手寫的 TSV fixture |
| `baseline/summaries/` | 每個設定、每個 seed 的摘要（gzip JSON，共 1.4 MB）；`per_seed.tsv` 是純量摘要的總表 |
| `baseline/calibration/` | `false_fail*.tsv`、`power.tsv`、`verdicts_*.tsv` |
| `baseline/calibration_m7/` | M7 設定單獨成一張表的校正（第 10 節） |
| `baseline/runs/` | trace.h5 等（580 MB，`.gitignore` 排除） |

測試：`cd phyclone_rs/v3 && $PY -m unittest discover -s tests`（11 個，約 40 秒）。

## 3. Trace 的共同形式

每個 posterior 樣本：`chain`、`iter`、`alpha`、`log_p_one`、`num_nodes`、`num_roots`，以及一棵樹。樹是 mutation 層級：

- `node_of[m]`：mutation m 所在的 node；outlier 是 −1。
- `parent[n]`：node n 的 parent；掛在 PhyClone 虛擬 root 下的 node 是 −1。

node 編號依「node 內第一個 mutation」重新排序（canonical）。所以兩個 sampler 抽到同一棵樹時，`Tree` 值相同，和 node 名稱無關。

- **cluster 檔的 run 展開到 mutation。** h5 用 `clusters` 群組，TSV 用 `clusters.tsv`；TSV 的 `assignments.tsv` 寫 cluster id 或 mutation id 都可以。
- **TSV reader 的容忍度**：多的欄位忽略；`meta.json` 的 `columns` 可以改欄名（`{"iterations.tsv": {"log_p_one": "<檔內名稱>"}}`）；`outlier_node` 指定 outlier 的 node 編號；`iterations.tsv` 若有 `phase` 欄，只留 `sample` 列（Python trace 不存 burn-in，兩邊才可比）。缺必要欄位時報錯。
- **驗證**〔實測〕：
  - h5 reader 重算的 node 數、root 數，和 trace 存的 `num_nodes`／`num_roots` 逐樣本相同。
  - 6 個參考 run 的 MAP 樹，和 golden `fixtures/trees` 的 `<run>:map` 相同。`upstream_clusters` 跳過，因為 fixture 存的是 cluster 層級。
  - h5 → TSV → reader 的摘要，和直接讀 h5 的摘要逐位相同。
  - 5 個 fresh seed 轉成 TSV 再比較，判定表和直接讀 h5 的判定表相同（第 6.3 節）。

Rust writer 還不存在，所以 TSV 格式只用手寫 fixture 和本目錄的 writer 測過。Rust writer 完成後，要先跑一次 `trace_io.py` 讀它的輸出。

## 4. Posterior 摘要

一個 run（一個 seed，多 chain 時合併）的所有樣本都用。Python trace 只存 burn-in 之後的 200 個 iteration。

| 摘要 | 形式 | 為什麼選它 |
|---|---|---|
| `num_nodes` | clone 數分布（0–16） | 最直接的 posterior 結構量；PG／prune-regraph 或 FSCRP prior 的 bug 會改變它 |
| `num_roots` | root 數分布 | 多 root 的 prior 項（FSCRP 的 r 項）錯了會改變它 |
| `log_alpha_q` | log alpha 的 10／50／90 百分位 | 測 concentration 更新與 FSCRP prior。用 log 是因為 alpha 從 1e-10 到 280 都有 |
| `log_p_one_q` | log_p_one 的 10／50／90 百分位 | 整個 joint（prior＋data＋C4 pair term）的大小；漏一項或算錯一項會整體位移 |
| `map_log_p_one` | 最大的 log_p_one | MAP 的分數；sampler 找不到好樹，或分數算錯，都會改變它 |
| `step_change` | 相鄰兩個樣本間，co-clustering 改變的 mutation pair 比例 | 混合速度。Gibbs 重新指派、prune-regraph 的 bug 會改變每步的移動量 |
| `coclust` | 每對 mutation 在同一 node 的比例 | 和 node 編號無關的 clustering posterior；指派記錯會改變它 |
| `ancestor` | 每對 (i, j) 中 i 的 node 是 j 的祖先的比例 | 和 node 編號無關的 topology posterior |
| `post_ari`、`map_ari` | 和真值 origin clone 的 ARI（posterior 平均、MAP 樹） | 專案既有指標（`tools/eval_random_tree_phyclone.py`）。有真值的 6 個設定 |
| `post_compat`、`map_compat` | role 層級的真值相容（posterior 比例、MAP 樹） | 專案既有指標（`tools/summarize_c4_robustness.py`；遺失角色 s2、s10 用來源 sim 的 `genome.json` 排除）。4 個壓力樹設定 |
| `post_c3_under_c4` | 直線樹（C3 在 C4 下）的 posterior | 專案既有指標（`tools/summarize_hp_truth_topologies.py`），C4 是否起作用的主要量。4 個壓力樹設定 |

- 所有摘要四捨五入到 1e-6，在同一處（`run_summaries`）做，快取與新算的值才會完全一致。
- 沒有用「topology 類別比例」當獨立摘要。在 -n 200 下，壓力樹每個樣本幾乎都是不同的 mutation 層級樹（200 個樣本 199–200 棵）。類別分布太稀疏，所以改用 `coclust`、`ancestor`，以及 role 層級的 `post_compat`、`post_c3_under_c4`。

## 5. 判定規則

每個設定、每個摘要：把 N 個 Python run 和 M 個 Rust run 合併，做 permutation test。

- 統計量 T：兩組平均摘要向量的加權 L1 距離。`dist` 用 total variation；`quant` 每個分量除以合併後的 seed 間 SD；`scalar` 用平均差；`matrix` 用每對的平均絕對差。權重只取決於合併資料，所以 test 在「兩邊的 run 可交換」的 null 下是精確的。
- p：C(N+M, M) ≤ 10,000 時完整列舉；否則抽 10,000 個分組（固定 RNG，結果可重現）。
- 判定：

| verdict | 條件 |
|---|---|
| FAIL | p < 0.001 |
| INCONCLUSIVE | 0.001 ≤ p < 0.01；或 seed 數讓 p 不可能 < 0.001；或某一邊沒有這個摘要 |
| PASS | p ≥ 0.01 |

- 整體判定：任一格 FAIL → FAIL；INCONCLUSIVE 的格數 ≥ 3 → INCONCLUSIVE；否則 PASS。
- 為什麼這樣定：
  - 表有約 85 格。每格的誤判率就是門檻本身，所以 0.001 讓整張表的誤判率約 5%（第 6.1 節實測 4.9%）。用 0.05 的話，幾乎每次都會有假的 FAIL。
  - permutation test 直接回答「Rust 是否落在 Python 的 seed 間變異內」。它用的是 seed 間的實際變異，不需要假設常態，也不需要長 run。
  - 數值相同的格（例如隨機樹的 run 都卡在 1 個 node）：距離小於 1e-9 × 資料尺度時當作 0，判 PASS。否則 float 的捨入誤差會被當成差異（實測發生過，已修正）。

## 6. 校正〔實測〕

### 6.1 Python 對 Python（誤判率）

每個設定有 15 個 Python seed。分成 10 個參考＋5 個候選，共 C(15, 5) = 3,003 種分法，每種都套用規則。

- **每一格**：FAIL 率在 0.0001–0.0010，INCONCLUSIVE 率在 0.001–0.009（依摘要）。這是 permutation test 的性質，不是巧合：每格的誤判率 ≤ 門檻是保證的。這項校正主要確認實作沒有錯（例如 tie 的處理）。
- **每個設定與整張表**（摘要之間有相關，這不是保證的）：

| 範圍 | 至少一格 FAIL | 至少一格不是 PASS |
|---|---|---|
| 單一設定 | 0.10%–1.00% | 1.0%–10.0% |
| 整張表（8 個設定、約 85 格，同一種分法套用到每個設定） | **4.9%** | 37.2% |

- 整張表中「不是 PASS」的格數：≥ 1 格 37.2%，≥ 2 格 13.5%，≥ 3 格 4.9%，≥ 4 格 1.5%。所以整體判定用「≥ 3 格 INCONCLUSIVE」，對應約 5% 的誤判。
- 5 個新的 Python seed（201–205，`fresh`）經由 `compare.py` 對 15 個 baseline seed：**80 格全部 PASS**（`baseline/calibration/verdicts_fresh.tsv`）。

`false_fail.tsv`、`false_fail_by_config.tsv`、`false_fail_table_count.tsv`。chains4 也有 15 個 seed，一起校正。

### 6.2 檢出力（破壞版本）

Python seed 1–10 對 5 個破壞版本的 seed（和 6.1 一樣是 10 對 5）。`power.tsv`。

| 破壞版本 | 模擬的 bug | 有 FAIL 的設定 | 偵測到的摘要 |
|---|---|---|---|
| `alphafixed`（`--no-concentration-update`） | alpha 不更新（prior／alpha move 錯） | **7／7** | `log_alpha_q` 7／7；`log_p_one_q` 4／7；`map_log_p_one` 1／7。樹的摘要都沒變 |
| `noc4`（拿掉 `--pairs`） | 漏掉 C4 pair term | **3／3** | `num_nodes`、`log_*`、`map_log_p_one`、`ancestor`、`post_c3_under_c4` 3／3；`coclust`、`post_ari`、`post_compat`、`step_change` 2／3 |
| `permuted`（seed 11–15 的 trace 打亂 mutation 標籤，經 TSV writer／reader） | 指派記錯 | **5／7** | `coclust`、`ancestor` 5／7；`post_ari`、`map_ari` 4／6；`post_compat` 3／4。數值類摘要都沒變（應該如此） |
| `np20`（`--num-particles 20`） | sampler 變弱，但目標分布相同 | **0／7** | 沒有任何一格 FAIL（最小 p = 0.043） |

- `permuted` 的 2 個漏網設定是兩個隨機樹設定。它們每個 seed 都只有 1 個 node，打亂標籤後樹不變，所以本來就無法偵測。
- 經由 `compare.py` 對 15 個 baseline seed 重跑：`noc4` 28 格 FAIL，`alphafixed` 12 格，fresh seed 打亂後的 TSV 22 格，`np20` 0 格（`verdicts_*.tsv`）。

## 7. seed 1 重現〔實測〕

`check_seed1.py`：7 個設定的 `baseline/runs/ref/<run>/seed01/trace.h5`，和 `golden/runs/<run>/trace.h5` 比較每個樣本的 alpha、log_p_one、num_nodes、num_roots（逐位）與樹（canonical）。**7／7 完全相同。**

baseline 用絕對路徑的輸入，並設 `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1`；這些都沒有改變結果。

## 8. Python baseline

- 設定：`golden/runs.tsv` 的 argv＋`-b 20 -n 200 --num-chains 1 --seed S`，outlier 關閉。`variants.tsv` 列出全部版本。

| 版本 | seed | 設定 | run 數 | 單一 run 時間（秒） | 合計（run-秒） |
|---|---|---|---|---|---|
| `ref` | 1–15 | 7 個 | 105 | 8–350 | 17,982 |
| `chains4` | 1–15 | e0_base_bin，4 chain | 15 | 183–227 | 3,083（× 4 chain） |
| `fresh` | 201–205 | 7 個 | 35 | 8–306 | 5,934 |
| `alphafixed` | 101–105 | 7 個 | 35 | 8–320 | 6,581 |
| `np20` | 101–105 | 7 個 | 35 | 6–136 | 2,908 |
| `noc4` | 101–105 | 3 個 C4 設定 | 15 | 70–145 | 1,409 |

- 合計約 13.1 core-hour（4-chain 算 4 core）。牆鐘時間約 27 分鐘：三批，最多約 70 個 process 同時跑。
- 平行時單一 run 比 golden 慢（例如 e0_base_bin 平均 186 秒，golden 143 秒）。
- 各設定 15 個 seed 的純量摘要：`baseline/summaries/per_seed.tsv`。

## 9. 限制與未決問題

- **-n 200 下，部分摘要沒有資訊。**
  - 隨機樹設定幾乎都卡在 1 個 node。`random_base_betabin` 15／15 個 seed 只有 1 個 node；`random_a1_bin` 12／15 個 seed 只有 1 個 node，另外 3 個（seed 04、06、11）短暫到 2 個 node。所以樹的摘要（`coclust`、`ancestor`、`post_ari`、`step_change`）幾乎沒有變異，只能確認 Rust 也卡住。這兩個設定實際上只測 alpha 與 log_p_one。
  - `upstream_clusters` 在每個 seed 都只有 1 棵樹（7 個 cluster 各自一個 node）；只有 alpha 會變。
  - `num_roots` 幾乎都是 1，在任何破壞版本都沒有偵測到差異。
  - `step_change` 在隨機樹與 upstream 設定幾乎都是 0；在壓力樹設定只偵測到 `noc4`（2／3）。
  - `map_compat` 是每個 seed 一個 0／1，seed 間變異很大（real_a2_err004 是 0 到 1），沒有偵測到任何破壞版本。
  - `post_compat` 在 real_a2_err004 也是雙峰（seed 間 0 到 1）。這表示 -n 200 的 chain 沒有混合好，不是 bug。
- **這個 harness 測不出「目標分布相同、只是 sampler 變弱」的差異**（`np20` 0／7）。它能抓出改變 posterior 的 bug（prior、漏掉的項、指派記錯），但抓不到效率變差。效率要在 V5 用時間與 ESS 另外比較。〔推論〕若要更敏感，需要更長的 run 或更多 seed。
- **誤判率是在 10 對 5 下校正的。** 實際使用是 15 個 Python 對約 10 個 Rust。每格的誤判率由 permutation test 保證，不受 seed 數影響；整張表的誤判率取決於摘要間的相關，〔推論〕應該接近 5%，但沒有實測。
- **建議 Rust 也照 Python 的方式存 trace**：只存 burn-in 之後的 iteration，`log_p_one` 包含 C4 pair term（Python trace 的 `log_p` 欄存的就是這個）。否則 `log_p_one_q`、`map_log_p_one` 會因定義不同而 FAIL。
- **`PORTING.md` 第 8 節提到的 child 順序差異**（log_p_one 最多差 0.0124）遠小於多數設定的 seed 間變異（`map_log_p_one` 的 seed 間範圍是 3–15 個 log 單位），不會影響這些設定的判定。〔推論〕
- **例外：`random_base_betabin` 的 `map_log_p_one` 在 15 個 seed 完全相同（121.22732）。** 1 個 node 的樹沒有 child，所以上面的順序差異不適用。但 Rust 的值只要和 Python 差超過捨入（1e-6），這一格就會 FAIL。這等於要求 V1 的 log_p_one 精度在這個設定也成立。若 Rust 在這裡 FAIL 而其他格都 PASS，先查 V1，不是 sampler。
- **golden README 第 6 節的描述和實測不同。** 它說隨機樹短 run 的「alpha 一直是 1.0」。實測 golden 的 `random_a1_bin` trace 有 170／200 個樣本的 alpha 是 1e-10（下限）；第一個樣本是 1.0，其餘 29 個在兩者之間。baseline 的兩個隨機樹設定，30 個 seed 的 alpha 中位數都是 1e-10。node 數在 golden trace 確實一直是 1。本目錄沒有修改 golden。
- **outlier 沒有測過**：所有設定都關閉 outlier。reader 把 outlier 當成「不和任何 mutation 同 node、也不是祖先」。TSV 的 outlier node 編號仍要在 `meta.json` 的 `outlier_node` 指定（`PORTING.md` 第 5 節還沒定義）。

## Rust 版的判定（M5，2026-10-26）

```bash
python3 phyclone_rs/v3/run_rust.py OUT --seeds 1-10 --jobs 24      # 80 個 run，約 19 秒牆鐘
env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \
  phyclone_rs/v3/compare.py OUT --out OUT/verdicts.tsv
```

- `run_rust.py` 用 `golden/runs.tsv` 的 argv 加上 `-b 20 -n 200`，跑 haploclone（預設 `/bip8_disk/boyu114/haploclone/rust/target/release/haploclone`）。每個 golden 設定 10 個 seed，加上 `e0_base_bin.chains4`。
- 結果（haploclone `3ecf7e7`）：**93 格全部 PASS，0 格 INCONCLUSIVE，0 格 FAIL**。表在 `rust_m5/compare.txt`、`rust_m5/verdicts.tsv`。
- 讀 Rust trace 時修了一處：Rust 的 `meta.json` `columns` 是「欄名 → 說明」，reader 原本把它當成改名。現在只有值是該檔的欄名時才當成改名（`trace_io.py` `_read_tsv`）。

## 10. M7 設定的 baseline（2026-10-27）〔實測〕

`golden/runs.tsv` 第 9–24 列是 M7 的參考 run。其中 13 個只能做統計比較，加進 `variants.tsv` 的第二個 `ref` 列（seed 1–15）。另加兩種破壞版本（seed 101–105）：`noout`（`-l 0`，等於移植時完全沒用 outlier node）與 `noloss`（關掉 loss prior，每個 cluster 都用全域 1e-4）。舊的 variant 列原本寫 `all`，現在改成明列原有的 7 個 run，意義不變；否則新的 golden run 會被拉進 np20、alphafixed、fresh。

不做 V3 的 M7 run 與原因：`e0_thin5`、`e0_maxtime0`、`e0_chains4` 用確定性質檢查（`golden/check_m7_runs.py`）；4-chain 已有 `e0_base_bin.chains4`。

```bash
~/venvs/phyclone/bin/python phyclone_rs/v3/run_baseline.py --jobs 48 --variant ref noout noloss   # 既有的 run 會跳過
$PY phyclone_rs/v3/summarize_baseline.py --configs <M7 設定與破壞版本>     # 只寫這些設定；per_seed.tsv 其他列不動
$PY phyclone_rs/v3/calibrate.py --configs <13 個 M7 設定> --out phyclone_rs/v3/baseline/calibration_m7
```

### 10.1 成本

220 個 run，牆鐘 1,208 秒（48 個平行，機器上同時有其他使用者約 31 個 core）。合計 37,660 run-秒 = **10.5 core-hour**。最貴的是 `e0_out001_fully`（每個 714–795 秒，合計 3.1 core-hour）。每個設定的時間：`baseline/summaries/per_seed.tsv` 的 `run_seconds`。

### 10.2 誤判率（Python 對 Python，10 對 5，3,003 種分法）

| 範圍 | 至少一格 FAIL | 至少一格不是 PASS |
|---|---|---|
| 單一設定 | 0.20%–1.07% | 2.0%–10.0% |
| M7 整張表（13 個設定） | **8.7%** | 59.4% |

- 「不是 PASS」的格數：≥ 3 格 12.5%，≥ 4 格 5.5%，≥ 5 格 2.5%（`false_fail_table_count.tsv`）。
- **M7 表的誤判率比原有表（4.9%）高**，因為格數變多。建議：M7 設定和原有 8 個設定分開跑 `compare.py --configs`；M7 表出現單一 FAIL 時，先用新的 Rust seed 重跑那個設定再下結論；INCONCLUSIVE 的整體門檻在 M7 表用 ≥ 5 格才約等於 5%〔推論：由上面的分布〕。

### 10.3 檢出力

| 破壞版本 | 設定 | FAIL 的格 |
|---|---|---|
| `noout` | `real_a2_err004_out001` | 6 格（`log_alpha_q`、`log_p_one_q`、`map_log_p_one`、`step_change`、`coclust`、`ancestor`；另 3 格 INCONCLUSIVE） |
| `noout` | `fscrp_out` | 1 格（`log_p_one_q`） |
| `noout` | `e0_out001` | **0 格**：`-l 0.01` 在這個資料幾乎不用 outlier（golden run 200 個樣本中 2 個有 outlier），開或關的 posterior 分不出來 |
| `noloss` | `fscrp_assign_loss`、`fscrp_user_loss` | 各 2 格（`log_p_one_q`、`map_log_p_one`） |
| `permuted` | 13／13 個設定 | 58 格 |

所以 outlier 的移植主要靠 `real_a2_err004_out001` 檢查。fscrp 的 3 個設定在每個 seed 都卡在同一棵樹（golden 第 6.1 節第 14 項），只能測 `log_p_one` 與 alpha。

### 10.4 sampler 選項本身改變了什麼（Python 設定互比）

拿某個設定的 seed 1–10 當候選，和另一個設定的 15 個 baseline seed 比（`compare.py`）。這回答「這個選項在 -n 200 下有沒有改變 posterior 摘要」，也就是 V3 能不能看出 Rust 把它做錯成另一個選項。

| 候選 | 對照 | 結果 |
|---|---|---|
| `e0_out001_boot` | `e0_out001` | 13 格 PASS |
| `e0_boot` | `e0_base_bin` | 13 格 PASS |
| `e0_subtree05` | `e0_base_bin` | 13 格 PASS |
| `e0_np20_rt08` | `e0_base_bin` | 12 格 PASS、1 格 INCONCLUSIVE |
| `e0_out001_fully` | `e0_out001` | 3 格 FAIL（`ancestor`、`post_compat`、`post_c3_under_c4`） |
| `e0_moves` | `e0_base_bin` | 3 格 FAIL（`log_p_one_q`、`ancestor`、`post_c3_under_c4`；`post_c3_under_c4` 從 0.44 變 0） |

- **V3 看不出 bootstrap 和 semi-adapted 的差別，也看不出 bootstrap＋outlier 的 0.8.0 回歸**（`e0_out001` 很少用到 outlier）。所以 Rust 照原版移植 bootstrap 回歸、或不小心修好它，V3 都會 PASS。這部分只能靠程式對照與單元測試（golden 第 6.1 節第 2 項的機率）。
- subtree PG 同樣看不出來；Rust 刻意修正的重新加權（`decisions.tsv` M5）因此不會造成 V3 FAIL，但 V3 也驗證不了它。
- fully-adapted 與 `--num-samples-prune-regraph 0` 看得出來：做錯成 semi-adapted、或 prune-regraph 沒有關掉，會 FAIL。

