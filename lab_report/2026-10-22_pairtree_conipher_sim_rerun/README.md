# 重跑 Pairtree 與 CONIPHER 的模擬資料生成程式

日期：2026-10-22。問題：用公開的生成程式重跑，能不能得到和 PhyClone benchmark 一模一樣的資料？

## 結論

| 資料 | 生成器輸出 | PhyClone 格式檔 | 能逐筆重現嗎 |
|---|---|---|---|
| Pairtree（576 份） | 格式、參數、生成規則都相同；數值**不同**（0／576） | 轉換規則已找出：`tree.json` 576／576 逐 byte 相同 | **否**：作者的種子沒有生效 |
| CONIPHER No-Noise（150 份） | 6 個檔 **150／150 逐 byte 相同** | 內容 150／150 相同；只有列的順序不同 | **是** |
| CONIPHER Noise（150 份） | 讀數相關的 4 個檔 150／150 逐 byte 相同；`_cloneprops.tsv` 3 份差在最後一位小數 | 內容 150／150 相同；只有列的順序不同 | **是**（讀數完全相同） |

- **Pairtree**：腳本能跑完，576 份全部產生。但作者執行時沒給 `--seed`，程式呼叫 `np.random.seed(None)`。pickle 裡記錄的種子實際沒有被使用。所以只能重現「同一個分布」，不能重現同一份資料。〔程式＋實測〕
- **CONIPHER**：用 Zenodo `_info.tsv` 記錄的參數與種子，加上兩個沒記錄、但可以搜尋出來的輸入，就能逐 byte 重現作者的生成器輸出。〔實測〕
- **PhyClone 作者自己的轉換步驟**（生成器輸出 → PhyClone 的 `tree.json`、`data.tsv`）沒有公開。本實驗從檔案反推出規則，見下方「PhyClone 轉換規則」。〔實測〕

## 資料

- 作者資料：`/big8_disk/boyu114/phyclone_dataset/{Pairtree,CONIPHER_No-Noise,CONIPHER_Noise}/data_archive/`
- CONIPHER 原始生成器輸出：Zenodo [10.5281/zenodo.10048165](https://zenodo.org/records/10048165)
  - `dataset2.zip`：No-Noise，150 份，完整下載。
  - `dataset1.zip`：Noise，1.3 GB。只用 HTTP Range 取出 150 份 `sim/` 底下的 6 個表格檔（約 25 MB），不含 png。
- 生成程式（submodule，見 `research/simulation_pipeline_research/upstream/SOURCE.md`）：
  - Pairtree：`pairtree/simulator/make_simulated_data.sh`（未修改）＋ `pearsim` commit **`0b9b249`**（2019-11-13）
  - CONIPHER：`TRACERx_simulation_tool` commit **`8c8d173`**（2023-08-30）

### 為什麼用這兩個舊版

- **pearsim `0b9b249`**：作者 pickle 的欄位只符合 2021-04 加入 garbage 功能之前的版本：
  - 頂層有 `seed`、`args`，沒有 `simparams`。
  - `args` 沒有 garbage 參數。
  - variant 沒有 `omega_v_true`。

  另外，作者 eta 的最小值剛好停在 1e-30。這表示作者的版本已經有 2019-11-13 加入的 `eta_min`。新舊兩版的 sample 都會碰到這個下限：作者 124／576 份，重跑 114／576 份。〔實測〕
- **TRACERx tool `8c8d173`**：Zenodo 的檔案日期是 2022-06-16。在那之前最後一個 commit 是 `0711a85`（2022-04-30）。`0711a85` 到 `8c8d173` 之間，`src/` 只多了一個沒有被呼叫的函式，模擬路徑相同。〔程式〕

## 做法

### 環境

- Pairtree：`~/venvs/phyclone`（Python 3.10、numpy 2.2.6）。`0b9b249` 只依賴 numpy，用的是舊版 `np.random.*`，亂數序列在各 numpy 版本間保持不變。
- CONIPHER：新建 `~/venvs/txsim`，裝 2022 年的版本：numpy 1.22.4、pandas 1.4.2、scipy 1.8.1、graphviz 0.20、ipython。README 指定 Python 3.9.5，本機只有 3.10。

### Pairtree

1. 原樣執行 `make_simulated_data.sh`。腳本寫死 `~/work/pearsim`、`~/work/pairtree/scratch/...` 和 `module load`，所以：
   - 設 `HOME=/big8_disk/boyu114/phyclone_dataset/Pairtree_rerun/home`。這個目錄下的 `work/pearsim` 放 `0b9b249`。
   - 在 `PATH` 最前面放兩個替身：什麼都不做的 `module`，以及轉呼叫 venv 的 `python3`。
2. 種子測試：用作者 pickle 記錄的 `seed` 加 `--seed` 重跑 2 份。
3. 比較生成器輸出：`tools/pairtree_sim_check.py`。
4. 反推 PhyClone 轉換：`tools/pairtree_sim_to_phyclone.py --check-author`。再用同一支程式把 576 份重跑資料轉成 PhyClone 格式。
5. PhyClone 讀取測試：`sim_K10_S3_T200_M200_run1`，真值分群當 cluster 檔，`-b 100 -n 500 --num-chains 1 --seed 1`。

```bash
R=/big8_disk/boyu114/phyclone_dataset/Pairtree_rerun
HOME=$R/home PATH=$R/shim:$PATH bash $R/make_simulated_data.sh
~/venvs/phyclone/bin/python tools/pairtree_sim_check.py $R/home/work/pairtree/scratch/inputs/sims.smallalpha.pairtree --out $R/compare_vs_author.tsv
~/venvs/phyclone/bin/python tools/pairtree_sim_to_phyclone.py --check-author
~/venvs/phyclone/bin/python tools/pairtree_sim_to_phyclone.py $R/home/work/pairtree/scratch/inputs/sims.smallalpha.pairtree $R/data_archive
```

### CONIPHER

1. 對每份模擬，用 `_info.tsv` 的參數與 `random_seed` 呼叫 `tx_simulation()`。`_info.tsv` 沒記錄的參數，用 notebook `make_tx_simulations.ipynb` 的固定值。
2. 有兩個輸入沒有記錄，要搜尋：
   - `prop_mutloss_positions`：`_info.tsv` 只記錄實際的比例，而且四捨五入到 2 位。先試記錄值，再試 notebook 的候選值 `np.arange(0.1, 0.26, 0.01)`。保留第一個讓 `_info.tsv`、`_treeedges.tsv`、`_cloneprops.tsv` 都相符的值。
   - `coverage`：從作者的平均 DEPTH 四捨五入開始，往兩邊試整數。保留第一個讓 DEPTH 與 VAR_COUNT 完全相同的值。
3. 逐 byte 比較 6 個輸出檔和 Zenodo 的檔案：`tools/conipher_sim_rerun.py`。
4. 比較 PhyClone 格式檔：`tools/conipher_sim_check.py`。

```bash
C=/big8_disk/boyu114/phyclone_dataset/CONIPHER_rerun
~/venvs/phyclone/bin/python tools/remote_zip_extract.py 'https://zenodo.org/records/10048165/files/dataset1.zip?download=1' $C/zenodo 'dataset1/LTXSIM\d+/sim/LTXSIM\d+(_info|_TX|_cloneprops|_treeedges|_events)?\.tsv$'
~/venvs/txsim/bin/python tools/conipher_sim_rerun.py $C/tool_8c8d173/src $C/zenodo/dataset2 $C/No-Noise_sim
~/venvs/txsim/bin/python tools/conipher_sim_rerun.py $C/tool_8c8d173/src $C/zenodo/dataset1 $C/Noise_sim
~/venvs/phyclone/bin/python tools/conipher_sim_check.py $C/No-Noise_sim /big8_disk/boyu114/phyclone_dataset/CONIPHER_No-Noise/data_archive
~/venvs/phyclone/bin/python tools/conipher_sim_check.py $C/Noise_sim /big8_disk/boyu114/phyclone_dataset/CONIPHER_Noise/data_archive
```

實際執行時，把 150 份分成 10 組平行跑（`--names`），再合併 `compare.tsv`。

## 結果：Pairtree

### 腳本能不能跑

- 576 份全部產生，0 個錯誤，用時 14 秒（40 個平行工作）。〔實測〕
- 每份都有 `.truth.pickle`、`.truth.npz`、`.params.json`、`.ssm`，檔名和作者相同（去掉 `_G0` 後 576／576 對上）。

### 種子測試

| 資料 | 作者記錄的 seed | 重跑的 `structure` | 作者的 `structure` |
|---|---|---|---|
| `sim_K3_S1_T50_M30_run1` | 1188003544 | `[0 1 2]` | `[0 1 0]` |
| `sim_K10_S3_T200_M200_run1` | 1445480472 | `[0 1 2 3 4 1 6 3 8 9]` | `[0 1 2 2 3 5 0 7 8 9]` |

記錄的 seed 不能重現資料。576 份作者資料的 `args.seed` 都是 `None`。〔實測〕

### 生成器輸出比較（576 份）

| 項目 | 結果 |
|---|---|
| pickle 欄位、variant 欄位、`args`（路徑與 seed 除外） | 576／576 相同 |
| 模擬內容逐項相同 | **0／576** |
| 11 條生成規則（例如 phi = Z·eta、root phi = 1、每群至少 1 個 SNV、total reads = T、omega = 0.5、沒有 CNA） | 重跑 576／576，作者 576／576 |

10 個統計量的分布（兩樣本 KS 檢定，576 對 576）：

| 統計量 | 重跑平均 | 作者平均 | KS p |
|---|---|---|---|
| root 的 child 數 | 1.54 | 1.62 | 0.84 |
| 「延伸目前分支」的比例 | 0.833 | 0.827 | 0.60 |
| 樹深 ÷ K | 0.652 | 0.640 | 0.80 |
| 每個 sample 最大的 eta | 0.577 | 0.587 | 0.46 |
| root 的 eta | 0.116 | 0.113 | 0.84 |
| 群大小變異係數 | 0.822 | 0.815 | 1.00 |
| VAF 平均 | 0.163 | 0.159 | 0.91 |
| var reads = 0 的比例 | 0.298 | 0.302 | 0.88 |
| binomial z 平均 | 0.0004 | 0.0037 | 0.30 |
| binomial z² 平均 | 0.924 | 0.944 | 0.70 |

依 K 分層的 40 個檢定中，只有 1 個 p < 0.05（K=30 的樹深，p = 0.015）。40 個檢定裡出現 1 個，和隨機誤差相符。〔推論〕完整表：`pairtree_compare_vs_author.tsv`。

### PhyClone 讀取測試

`phyclone run` 與 `map` 都正常結束，用時 37 秒。真值 10 群被併成 6 個 clone，例如 cluster 6／7／8 的 CCF 幾乎相同（約 0.42／0.75／0.88）。alpha = 0.1 時常有這種情形。這只是一次短鏈，不代表準確度。

## 結果：CONIPHER

### 生成器輸出：逐 byte 比較（重跑 vs Zenodo）

| 檔案 | No-Noise | Noise |
|---|---|---|
| `_info.tsv`（參數、種子、警告） | 150／150 | 150／150 |
| `.tsv`（每個 SNV × sample 的讀數與真值） | 150／150 | 150／150 |
| `_TX.tsv`（CONIPHER 輸入格式） | 150／150 | 150／150 |
| `_treeedges.tsv`（樹的邊與事件數） | 150／150 | 150／150 |
| `_events.tsv`（每個位置在每條邊上的事件） | 150／150 | 150／150 |
| `_cloneprops.tsv`（每個 sample 的 clone 比例） | 150／150 | **147／150** |

- Noise 的 3 份（LTXSIM066、086、100）只差在 clone 比例的最後一位，例如 `0.06245211874344086` 對 `0.062452118743440845`。差異約 1e-17，來自函式庫版本的浮點運算差異。`.tsv` 的值四捨五入到 2 位，所以完全相同。〔實測〕
- 搜尋到的輸入：
  - coverage：No-Noise 120／150、Noise 113／150 在第一次就對中，就是平均 DEPTH 的四捨五入值；其餘的差 ±1 或 ±2。
  - mutation loss：No-Noise 全是 0。Noise 有 130／150 和記錄值相同。其餘 20 份的實際輸入比記錄值大，被程式上限截掉；這時 `_info.tsv` 會多一條「capped」警告，靠這條警告才能分辨。
- Noise 的 `_info.tsv` 也受 coverage 影響：noise 步驟在讀數之後才抽亂數。所以 LTXSIM034 要先找到 coverage，`_info.tsv` 才相符。

完整表：`conipher_no-noise_vs_zenodo.tsv`、`conipher_noise_vs_zenodo.tsv`。

### PhyClone 格式檔（重跑 vs PhyClone benchmark）

| 檢查 | No-Noise | Noise |
|---|---|---|
| `_treeedges.tsv` 逐 byte 相同 | 150／150 | 150／150 |
| `full_truth_with_mut_id.tsv`：排序後內容相同 | 150／150 | 150／150 |
| `full_truth_with_mut_id.tsv`：列的順序相同 | **0／150** | **0／150** |
| `data.tsv`：排序後內容相同（依下方規則轉換） | 150／150 | 150／150 |
| `tree.json` 的邊 | 150／150 | 150／150 |
| `tree.json` 的節點與 SNV | 150／150 | 150／150 |
| `tree.json` 的 `id -1` 節點 = noise SNV | 150／150 | 150／150 |

列的順序沒有重現：它不是依任何一欄排序，各 sample 之間的順序也不同。轉換程式沒有公開，所以無法得知規則。〔實測〕完整表：`conipher_no-noise_vs_phyclone.tsv`、`conipher_noise_vs_phyclone.tsv`。

## PhyClone 轉換規則（從檔案反推）

PhyClone 作者把生成器輸出轉成 benchmark 格式的程式沒有公開。下面的規則在全部資料上成立。〔實測〕

**Pairtree**（pickle → PhyClone）

- `tree.json`：節點 0..K。`clonal_prev` = eta，`cellular_prev` = phi。SNV 名稱是 `S_<編號>`。邊依 `structure` 建立。用 `tools/pairtree_sim_to_phyclone.py` 重建，576／576 逐 byte 相同。
- `data.tsv`：ref／alt 來自 pickle。`major_cn` = `minor_cn` = 1，`normal_cn` = 2，`tumour_content` = 1.0。除了 `chrom` 之外，576／576 相同。
- `chrom`：每個 mutation 一個 1–22 的隨機值，無法重現。它不影響 PhyClone 的計算。

**CONIPHER**（Zenodo `sim/` → PhyClone）

- `full_truth_with_mut_id.tsv` = `<name>.tsv` 加一欄 `mutation_id = s<VAR_POS>`，列重新排序。
- `data.tsv`：
  - ref／alt = REF_COUNT／VAR_COUNT，`tumour_content` = PURITY，`chrom` = CHR，`normal_cn` = 2。
  - `major_cn` = round(max(CN_A, CN_B))，`minor_cn` = round(min(CN_A, CN_B))。CN_A、CN_B 是 sample 內各腫瘤 clone 依比例加權的平均值，可以不是整數，例如 2.93。
- `tree.json`：
  - 用 `_treeedges.tsv` 的邊，但去掉「正常細胞 root → 第一個腫瘤 clone」那條邊。
  - 沒有剩下任何非 noise SNV 的 clone 會被刪掉，它的 child 接到最近一個還有 SNV 的祖先。這種情形出現在 13／150 份 Noise 資料。
  - 多一個 `id -1` 節點，放所有 noise SNV。No-Noise 資料的這個節點是空的。FS-CRP 的 `tree.json` 也有這個空節點。

## 輸出位置

| 目錄 | 內容 |
|---|---|
| `/big8_disk/boyu114/phyclone_dataset/Pairtree_rerun/` | `make_simulated_data.sh`（原檔複本）、`shim/`、`home/work/pearsim/`（`0b9b249`）、生成器輸出（`home/work/pairtree/scratch/inputs/sims.smallalpha.pairtree/`）、`data_archive/`（576 份 PhyClone 格式）、`seed_test/`、`compare_vs_author.tsv`。共 4.7 GB。 |
| `/big8_disk/boyu114/phyclone_dataset/CONIPHER_rerun/` | `tool_8c8d173/`、`zenodo/`（dataset2 全部、dataset1 的表格檔）、`No-Noise_sim/`、`Noise_sim/`（各含 `compare.tsv`）、兩個 `*_vs_phyclone.tsv`。共 676 MB。 |

## 限制

- Python 版本：Pairtree 與 CONIPHER 都在 Python 3.10 上跑。README 指定的是 3.9.5。CONIPHER 的結果已經逐 byte 相同，所以版本差異沒有影響讀數。
- Pairtree 的重跑資料不能取代作者資料。兩者分布相同，但具體的樹和讀數都不同。
- CONIPHER 的 `coverage` 與 `prop_mutloss_positions` 是搜尋出來的，不是記錄的。它們讓 6 個檔逐 byte 相同，但不能證明作者當時輸入的就是這個值。例如 mutation loss 被截掉時，任何大於上限的輸入都會得到相同結果。
- 沒有重跑 Copy_Number_Error。它是 PhyClone 作者對 CONIPHER No-Noise 做的拷貝數擾動，擾動程式沒有公開。
- CONIPHER 只在 Noise 的 13 份上驗證了「刪除空 clone」規則。No-Noise 沒有空 clone。
