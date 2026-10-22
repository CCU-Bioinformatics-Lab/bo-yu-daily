# 其他 benchmark 的模擬資料生成程式

下載日期：2026-10-22。三個目錄都是 **git submodule**，內容未修改，只供閱讀與對照。調查經過見 [`../notes/05_OTHER_SIMULATORS.md`](../notes/05_OTHER_SIMULATORS.md)。

用 submodule 而不是複製檔案，原因是 `pearsim` 沒有授權檔。我們的 repo 只記錄連結與 commit，不散布它的程式碼。

| 目錄 | 上游 | commit | 授權 | 對應的 PhyClone benchmark 資料 |
|---|---|---|---|---|
| `pearsim/` | https://github.com/morrislab/pearsim | `f22db48`（2021-04-28，最新） | 無 | Pairtree（576 份） |
| `pairtree/` | https://github.com/morrislab/pairtree | `13e33dd`（2024-04-18，最新） | MIT | Pairtree：提供 `pearsim` 依賴的 `lib/`，以及產生 576 份的驅動腳本 |
| `TRACERx_simulation_tool/` | https://github.com/zaccaria-lab/TRACERx_simulation_tool | `facd2d7`（2025-04-03，最新） | BSD-3 | CONIPHER Noise／No-Noise（各 150 份） |

## Pairtree：要看哪些檔

| 檔案 | 角色 |
|---|---|
| `pairtree/simulator/make_simulated_data.sh` | **產生 576 份的那一支。** 參數網格與 `--alpha 0.1` 和本機資料一致。 |
| `pearsim/make_simulated_data.py` | CLI：讀參數、呼叫 simulator、寫 truth pickle、`params.json`、`.ssm` |
| `pearsim/simulator.py` | 生成樹、clone 比例、read 數 |
| `pearsim/garbage.py` | 產生 garbage mutation（576 份用 `G_frac 0`，沒有用到） |
| `pearsim/make_simulated_data.sh` | **不是** 576 份用的腳本。它跑 `G_frac` 0／0.01／0.1／1 各 1 份，用來測 garbage。 |

**作者用的 pearsim 是舊版。** 作者 pickle 的欄位只符合 commit `0b9b249`（2019-11-13）：頂層有 `seed`、`args`，沒有 `simparams`，也沒有 garbage 參數。依程式碼，最新版 `f22db48` 的輸出格式不同（多一層 `simparams`）。〔程式〕依程式碼判斷，最新版加 `--write-numpy` 時會因為 `simdata` 沒有 `seed` 而出錯；這點沒有實際執行。〔程式〕要重現，用 `git -C pearsim archive 0b9b249`。`0b9b249` 只依賴 numpy，不需要 Pairtree 的 `lib/`。〔實測〕

注意：最新版 `pearsim` 用 `sys.path` 載入 `~/work/pairtree/lib`。要執行時，需要改這個路徑，或建立對應的 symlink。

## CONIPHER：要看哪些檔

| 檔案 | 角色 |
|---|---|
| `TRACERx_simulation_tool/scripts/make_tx_simulations.ipynb` | 產生 TRACERx 風格模擬資料的主 notebook |
| `TRACERx_simulation_tool/src/simulate.py` | 單份模擬：樹、拷貝數、mutation loss、noise、read 數；`np.random.seed(rs)` |
| `TRACERx_simulation_tool/src/{topology,evolution,sequencing,noise,conversion}.py` | 各步驟的實作 |
| `TRACERx_simulation_tool/data/` | 抽參數用的病人摘要資料 |

### 版本與 Zenodo 資料的關係

- Zenodo 紀錄發布日是 2023-10-27，但 zip 裡檔案的日期是 **2022-06-16**。在那之前最後一個 commit 是 `0711a85`（2022-04-30）。〔實測〕
- `0711a85` 到 `8c8d173`（2023-08-30）之間，`src/` 只多了一個沒被呼叫的函式 `simulate_evolution()`，模擬路徑相同。〔程式〕
- `8c8d173` 到最新版之間，`src/` 和 `scripts/` 改了 5 個檔，其中 `src/simulate.py` 改 38 行。〔實測〕
- 用 `8c8d173` 加上 `_info.tsv` 的種子，No-Noise 與 Noise 共 300 份的讀數都和 Zenodo 逐 byte 相同（見 `lab_report/2026-10-22_pairtree_conipher_sim_rerun/`）。〔實測〕
- 要重現，切到 `8c8d173`，不要用最新版：

  ```bash
  git -C research/simulation_pipeline_research/upstream/TRACERx_simulation_tool checkout 8c8d173
  ```

  這只改 submodule 的工作目錄。要回到記錄的版本，跑 `git submodule update`。
- `8c8d173` 的病人摘要資料是 `data/simulated_TRACERx_data.tsv`，README 說它是隨機產生的假資料。〔程式〕
