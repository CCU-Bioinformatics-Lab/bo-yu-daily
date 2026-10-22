# Pairtree 與 CONIPHER 的模擬資料生成程式

調查日期：2026-10-21。問題：PhyClone benchmark 用到的 Pairtree 與 CONIPHER 資料，有沒有公開、完整的生成程式？

## 結論

| 資料 | 生成程式 | 完整嗎 | 能逐筆重現作者資料嗎 |
|---|---|---|---|
| Pairtree（576 份） | `morrislab/pearsim` + `morrislab/pairtree/simulator/make_simulated_data.sh` | 是：從參數產生樹、read 數，並寫檔 | 否：記錄的種子沒有真的被使用。重跑 576 份，分布相同、數值不同〔實測〕 |
| CONIPHER Noise／No-Noise（各 150 份） | `zaccaria-lab/TRACERx_simulation_tool` | 是：產生樹、拷貝數、mutation loss、noise、read 數，並寫檔 | **是**：用 commit `8c8d173` 與記錄的種子，300／300 份的讀數逐 byte 相同〔實測〕 |
| Copy_Number_Error（450 份） | PhyClone 作者對 CONIPHER No-Noise 做的拷貝數擾動 | 否：擾動程式沒有公開 | 否 |
| FS-CRP、TSSB | PhyClone 作者 | 否（見 `../../../lab_report/2026-10-21_phyclone_sim_rerun/README.md` 與 01 §7） | 否 |

本機副本：三個生成器 repo 已加為 submodule，放在 `../upstream/`，版本與要看的檔案見 [`../upstream/SOURCE.md`](../upstream/SOURCE.md)。

另外，三組資料轉成 PhyClone benchmark 的 `tree.json`、`data.tsv` 的轉換程式，在 PhyClone repo 裡都沒找到。Pairtree 與 CONIPHER 的轉換規則已從檔案反推出來。

重跑結果（2026-10-22）見 [`../../../lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md`](../../../lab_report/2026-10-22_pairtree_conipher_sim_rerun/README.md)。

## Pairtree

證據：

- PhyClone 論文 §2.4.1.3：「We used previously published data from Wintersinger et al. (2022)」，576 份。〔論文〕
- `morrislab/pairtree` 的 `simulator/make_simulated_data.sh`（repo 最新 commit `13e33dd`，2024-04-18）：參數網格 K {3,10,30,100} × S {1,3,10,30,100}（K≥30 時跳過 S<10）× T {50,200,1000} × 每群 SNV 數 {10,20,100} × 4 份，正好 576 份；`--alpha 0.1`。〔程式〕
- 該腳本呼叫 `~/work/pearsim/make_simulated_data.py`。`morrislab/pearsim` 是公開 repo，最後 push 是 2021-04-28，沒有授權檔。〔程式〕
- `pearsim/make_simulated_data.py` 有完整 CLI，會寫出 truth pickle、`params.json`、`.ssm` 輸入檔，以及選用的 `.npz`。〔程式〕
- 本機 576 份的檔名與 pickle 裡的 `args` 都和腳本一致，例如 `sim_K100_S100_T1000_M10000_G0_run1`，以及作者機器上的路徑 `/home/q/qmorris/jawinter/work/pairtree/scratch/inputs/sims.smallalpha.pairtree/`。〔實測〕

缺點：

- **種子沒有生效。** 程式沒收到 `--seed` 時，會產生一個種子存進輸出（例如 `seed = 1503064755`），但實際呼叫的是 `np.random.seed(args.seed)`，也就是 `np.random.seed(None)`。本機抽查 60 份，`args.seed` 都是 `None`。所以記錄的種子不能重現資料。〔程式＋實測〕
- 依賴 Pairtree 的 `lib/`，路徑寫死成 `~/work/pairtree/lib`。〔程式〕
- 沒有授權檔：可以讀，但不能直接複製進我們的 repo。

## CONIPHER

證據：

- PhyClone 論文 §2.4.1.4：「We used previously published data from Grigoriadis et al.」，用 dataset 1（noise）與 dataset 2（no-noise），各 150 份。〔論文〕
- 資料在 Zenodo `10.5281/zenodo.10048165`（2023-10-27）。`scripts.zip` 只有 4 個畫補充圖的 R 檔，讀 TRACERx421 的真實樹，不是模擬程式。dataset2 每份有 `sim/` 底下 7 個檔：`.tsv`、`_TX.tsv`、`_cloneprops.tsv`、`_treeedges.tsv`、`_events.tsv`、`_tree.png`、`_info.tsv`。〔實測〕
- `McGranahanLab/CONIPHER` 與 `CONIPHER-wrapper` 都只有建樹程式，沒有模擬程式。〔程式〕
- 生成器是 `zaccaria-lab/TRACERx_simulation_tool`（BSD-3，2022-04 建立，最後 push 2025-04-03）。用 GitHub 程式碼搜尋 `LTXSIM` 找到。Simone Zaccaria 是 CONIPHER 論文的共同作者。〔程式〕
  - README 的輸出檔名和 Zenodo 資料完全對得上。README 也寫明預設值就是用來 benchmark TRACERx 建樹工具的設定：每組 50 份，以 (3, 7) 分成三組 sample 數。〔程式〕
  - 程式有 mutation loss、noise、WGD、拷貝數 gain／loss，並把每份的參數與 `random_seed` 寫進 `_info.tsv`。例如 Zenodo 的 `LTXSIM001_info.tsv` 是 `random_seed 602`、`n_nodes 13`、`n_samples 3`。`simulate.py` 用 `np.random.seed(rs)`，種子會生效。〔程式＋實測〕

缺點：

- **輸入的病人摘要資料不一定是當時那份。** README 寫：附的資料是「randomly simulated dataset of patient summary genomic information」，等 TRACERx 資料公開才會換掉。`data/TRACERx_data.tsv` 在 2024-01-08 才加入。但 `_info.tsv` 已經記錄了每份抽出來的參數，所以重現時可以跳過這一步。〔程式〕
- **程式在資料產生後改過**：2023-11-07 Fix display output、2024-04-09 tx_conversion_fix 等。Zenodo 檔案的日期是 2022-06-16。用 `8c8d173`（模擬路徑和 2022-04-30 版相同）加上記錄的種子，300／300 份的讀數逐 byte 相同。沒有測最新版。〔實測〕
- **兩個輸入沒有記錄**：`coverage` 與 `prop_mutloss_positions`。兩者都能用搜尋找回，見重跑報告。〔實測〕
- 主要程式碼放在 Jupyter notebook（`scripts/make_tx_simulations.ipynb`）；README 指定 Python 3.9.5。

## 對我們的意義

- 三組公開生成器都只產生計數或 VAF 層的資料。都沒有 read、HP，也沒有同 read 共現。CONIPHER 的生成器有 allele-specific 拷貝數、真實位置與 purity 小於 1，最接近我們 long read 生成器需要的設計。〔推論〕
- 「在 X 範圍內沒找到」的範圍：PhyClone repo `2738324`、`morrislab/pairtree`、`morrislab/pearsim`、`McGranahanLab/CONIPHER`、`CONIPHER-wrapper`、Zenodo `10048165`、GitHub 程式碼搜尋 `LTXSIM`（2026-10-21）。CONIPHER 論文全文有付費牆，沒有讀到它的 Methods。
