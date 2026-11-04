# V4 評估程式：重現 PhyClone 論文的 V-measure 與 AD F-score（2026-10-27）

## 結論

- `tools/eval_phyclone_dataset.py` 重現論文 xlsx 的 PhyClone／PhyClone-N 點估計指標：**2,832 列中 2,830 列完全相同**（誤差 ≤ 4e-14）。〔實測，`validation_summary.tsv`〕
- 從 `tree.json` 讀，或從 `results.tsv` + `tree.nwk` 讀，結果都一樣。所以 0.8.0 `map` 的 `map_table.tsv` + `map_tree.nwk` 也能用同一個 loader 讀。〔實測〕
- 唯一不符的是 HGSOC p3（S10、S11）的 AD F-score。所有方法（含 CONIPHER、Pairtree 等）都差同一組 408 個真值 pair。論文的 p3 真值和公開的 `tree.json` 不同。〔實測＋推論，見「HGSOC p3」〕
- RRE、LPR 不能用現有檔案算。原因見「限制」。
- 建議的 V4 子集：67 個 run，論文時間合計 38,656 秒。估計 Python 約 43 core-hour，Rust 約 1.7 core-hour。〔估計〕還沒跑。

## 資料

- Dataset：`/big8_disk/boyu114/phyclone_dataset/<Dataset>/data_archive/<Trial>/`。真值 `ground_truth/tree.json`；論文的 PhyClone 0.7.0 輸出 `program_outputs/phyclone_{outliers,naive}/`。
- 論文每個 trial 的指標：`research/phyclone_research/btaf344_supplementary_data/Experiment_Performance_Metrics.xlsx`（S2–S14）。
- 0.8.0 輸出：`phyclone_rs/golden/runs/fscrp_out/`（FS-CRP_Loss `loss_prop_0.2_run0`，1 chain、-b 20、-n 200、`-l 0.01`）。

### xlsx 欄位與 trial 目錄的對應

所有 sheet 都有 `program`、`v_measure`、`num_mutations_pred`、`num_mutations_true`、`ancestor_descendant_f_score`、`Success`、`memory`、`time`。`time` 是秒（4 chain 平行的牆鐘）；`memory` 單位沒寫，數值像 MB。

| Sheet | Dataset | 其他欄 | Trial 目錄 |
|---|---|---|---|
| S2／S3 | TSSB_Low／TSSB_High | depth, num_mutations, num_samples, run | `S{num_samples}_D{depth}_M{num_mutations}_run{run}` |
| S4 | FS-CRP_Loss | …, mut_loss_prop, run | `loss_prop_{p:.1f}_run{run}`；`PhyClone`→`phyclone_outliers`，`PhyClone-N`→`phyclone_naive` |
| S5 | Pairtree | depth, num_clusters, num_mutations, num_samples, run | `sim_K{num_clusters}_S{num_samples}_T{depth}_M{num_mutations}_run{run}` |
| S6／S7 | CONIPHER_No-Noise／Noise | sim_name, num_samples | `{sim_name}` |
| S14 | Copy_Number_Error | sim_name, num_samples（**沒有 error 欄**） | 同一個 sim 的第 k 列（k=0,1,2）= `{sim_name}_error_{0.1k}` |
| S8–S13 | HGSOC | run（p2／p3／p9） | S8 p2_wgs、S9 p2_wgs_t、S10 p3_wgs、S11 p3_wgs_t、S12 p9_wgs、S13 p9_wgs_t；`HGSOC/<版本>/data_archive/<run>` |

S14 的順序規則：444／450 列只符合一個 error 目錄，另外 6 列同時符合多個；依出現順序對應時 450 列全對。〔實測〕

## 做法

### 指標定義（程式實際行為，能重現 xlsx）

論文主張：V-measure 評估分群，AD F-score 評估所選樹中 SNV pair 的祖先—後代關係（Main §2.4.3；Supplement Fig. S9 p.20：只要 M_D 在 M_A 的子孫中就算對，不限直接 child）。論文沒有說明 outlier、遺失 SNV、多 root 怎麼處理，也沒有公開程式。下面是反推出來、能重現數值的規則：

- **SNV 集合。** 真值 SNV = `tree.json` 所有 node 的 SNV（含 FS-CRP 的 `-1` node，即遺失的 SNV）。預測 SNV = 預測樹中的 SNV；0.7.0／0.8.0 表格中 `clone_id = -1` 的 outlier 不算預測樹的一部分（論文的預測 `tree.json` 本身也沒有 outlier）。
- **V-measure。** sklearn 式（自然對數、beta=1）。只用「同時在預測樹與真值」的 SNV。真值的 `-1` node 是一個普通的 label。
- **AD F-score。** 真值 pair 集合 T = {(a, d)：真值中 a 的 node 是 d 的 node 的嚴格祖先}；預測 pair 集合 P 同理，只看真值 SNV。F = 2|T∩P| / (|T| + |P|)。
  - 同 node 的 pair 不算。
  - 真值 `-1` node 沒有 edge，所以它的 SNV 不在任何 pair。
  - 預測 outlier 和不在預測樹的 SNV 不在 P，但它們的真值 pair 仍在 T（降低 recall）。
  - 多個 root（PhyClone `root` 底下的 forest）之間沒有 pair。Newick 的 `root` 不是 clone。
- `num_mutations_pred` = |預測 SNV ∩ 真值 SNV|；`num_mutations_true` = |真值 SNV|。HGSOC 的預測樹含所有 WGS SNV（2,014–5,060 個），只有真值的 43–149 個參與評估。

試過但不符的規則（FS-CRP，600 列）〔實測，scratch `proto/p1.py`〕：

| 規則 | 完全相同的列數 |
|---|---|
| V 用全部真值 SNV，預測 outlier 當 label `-1` | 485／600 |
| V 用全部真值 SNV，預測 outlier 各自成一群 | 392／600 |
| V 再排除真值 `-1` 的 SNV | 428／600 |
| AD 的 T 也只看預測樹中的 SNV | 550／600 |
| AD 的 T、P 都排除真值 `-1` 和預測 outlier | 338／600 |
| **採用的規則** | **600／600** |

### 驗證指令

```bash
~/venvs/phyclone/bin/python tools/eval_phyclone_dataset.py validate /big8_disk/boyu114/phyclone_dataset \
  research/phyclone_research/btaf344_supplementary_data/Experiment_Performance_Metrics.xlsx \
  lab_report/2026-10-27_v4_evaluator/validation_paper_outputs.tsv     # 本機約 10–20 分鐘（沒有精確計時）
~/venvs/phyclone/bin/python tools/eval_phyclone_dataset.py score TRIAL_DIR OUT_DIR   # 單一 trial
~/venvs/phyclone/bin/python -m unittest tools/test_eval_phyclone_dataset.py           # 3 個測試
```

xlsx 用標準函式庫的 zip／XML 解析（不需要 openpyxl）。AD 用 node 層級的計數矩陣計算，10,000 SNV 的 trial 也不用列舉 pair。

## 結果

### 與論文 xlsx 的一致性〔實測，`validation_summary.tsv`〕

| Sheet | 方法 | 列數 | tree.json 相同 | results.tsv+nwk 相同 | max abs ΔV | max abs ΔAD |
|---|---|---|---|---|---|---|
| S2 TSSB-Low | PhyClone | 500 | 500 | 500 | 1.6e-15 | 3.3e-16 |
| S3 TSSB-High | PhyClone | 400 | 400 | 400 | 3.9e-14 | 2.2e-16 |
| S4 FS-CRP Loss | PhyClone | 300 | 300 | 300 | 4.4e-16 | 2.2e-16 |
| S4 FS-CRP Loss | PhyClone-N | 300 | 300 | 300 | 4.4e-16 | 2.2e-16 |
| S5 Pairtree | PhyClone | 576 | 576 | 576 | 2.0e-15 | 2.2e-16 |
| S6 CONIPHER No-Noise | PhyClone | 150 | 150 | 150 | 1.6e-15 | 2.2e-16 |
| S7 CONIPHER Noise | PhyClone | 150 | 150 | 150 | 8.9e-16 | 1.7e-16 |
| S14 Copy Number Error | PhyClone | 450 | 450 | 450 | 1.4e-15 | 2.2e-16 |
| S8／S9 HGSOC p2 | PhyClone | 1＋1 | 2 | 2 | 0 | 0 |
| S12／S13 HGSOC p9 | PhyClone | 1＋1 | 2 | 2 | 2.2e-16 | 1.1e-16 |
| S10 HGSOC WGS p3 | PhyClone | 1 | 0 | 0 | 0 | 0.0312 |
| S11 HGSOC WGS+T p3 | PhyClone | 1 | 0 | 0 | 0 | 0.0362 |

HGSOC 也對 CONIPHER、fastBE、Pairtree、Orchard 的列檢查過（scratch）：p2、p9 全對，p3 都不符。

### HGSOC p3

- 我們的真值 pair |T| = 5,803。用 8 列（fastBE、Orchard、Pairtree、PhyClone × WGS／WGS+T）反推，論文的 |T| 都是 5,395，而且 |T∩P| 不變。CONIPHER 的 2 列反推時，|T∩P| 少 40。〔實測〕
- 從 T 移除下面 408 個 pair 後，10 列（5 方法 × 2 版本）全部完全相同〔實測〕：
  - node A 中 cluster 10 的 16 個 SNV × node G 的 17 個 SNV（272）。
  - node A 中 cluster 7 的 4 個 SNV（`18_8008075_rC_aT`、`19_46281423_rC_aA`、`1_85759592_rG_aA`、`2_179785060_rA_aG`）× node F、G、E（136）。
- 〔推論〕論文的 p3 真值可能把這些 SNV 當成在子孫中遺失。證據：cluster 10 在 adnexa 的 prevalence 約 0.01，但 G 在 adnexa 約 0.42；這違反「祖先 ≥ 子孫」。公開的 `tree.json` 沒有記錄這件事。
- 評估程式不加特例。V4 比較 0.7.0、0.8.0、Rust 時都用同一個真值，所以不影響版本間的比較；只是 p3 的 AD 不能直接和論文的數字比。

### 0.8.0 輸出的檢查〔實測〕

- 用 upstream 0.8.0（`research/phyclone_research/PhyClone`，`version = "0.8.0"`）對 golden `fscrp_out/trace.h5` 重跑 `map`。輸出和 golden 的 `map_table.tsv`、`map_tree.nwk` 逐位元相同。
- 評估結果：V = 0.998402130725652、AD F = 0.825224071702945（precision 0.7025、recall 0.9999），`num_mutations_pred` = 600。
- 這兩個數字和論文 **PhyClone-N** 在同一 trial 的值完全相同。〔推論〕這個短 run（`-l 0.01`）的 MAP 沒有 outlier，得到和論文 naive run 相同的分群與樹。論文 PhyClone（outlier 開啟，prior 設定不明）把 58 個遺失 SNV 標成 outlier，AD F = 0.99993。

### 執行時間與規模（論文 PhyClone 列，`time` 秒）〔xlsx〕

| Dataset | trial 數 | SNV | 樣本 | 輸入 cluster | 中位數 | 範圍 | 合計（小時） |
|---|---|---|---|---|---|---|---|
| TSSB_Low | 500 | 100 | 2–128 | 3–9 | 198 | 79–1,774 | 35.2 |
| TSSB_High | 400 | 10,000 | 2–16 | 2–14 | 424 | 89–4,100 | 60.0 |
| FS-CRP_Loss（兩種方法） | 600 | 600 | 8 | 2–20 | 454 | 53–5,328 | 126.1 |
| Pairtree | 576 | 30–10,000 | 1–100 | 1–19 | 412 | 42–27,071 | 261.5 |
| CONIPHER_No-Noise | 150 | 162–3,437 | 2–11 | 4–21 | 630 | 148–4,640 | 34.1 |
| CONIPHER_Noise | 150 | 172–4,439 | 2–13 | 5–16 | 831 | 275–6,244 | 40.3 |
| Copy_Number_Error | 450 | 162–3,437 | 2–11 | 4–18 | 885 | 215–4,527 | 140.4 |
| HGSOC（6 個） | 6 | 2,014–5,060 | 4–5 | 3–8 | 52–208 | — | 0.2 |

全部合計約 698 小時牆鐘（×4 chain ≈ 2,800 core-hour）。Pairtree 的時間主要看 K 與樣本數：K100 S100 中位數 8,378 秒，K3 S1 中位數 80 秒。

### 建議的 V4 子集（還沒跑）

清單：`proposed_subset.tsv`（67 列）。規則：

| Dataset | 選法 | run 數 | 論文時間合計（秒） |
|---|---|---|---|
| TSSB_Low | S2、S4，run0–4 | 10 | 2,054 |
| TSSB_High | S2、S4，run0–2 | 6 | 2,240 |
| FS-CRP_Loss | loss 0.0／0.1／0.2，run0–2；outlier 開與關各一次 | 9＋9 | 21,202 |
| Pairtree | K3 S3／S10 T1000 M300、K10 S3／S10 T1000 M1000，run1–2 | 8 | 2,434 |
| CONIPHER_No-Noise／Noise | LTXSIM001–005 | 5＋5 | 4,813 |
| Copy_Number_Error | LTXSIM001–003 × error 0.0／0.1／0.2 | 9 | 5,211 |
| HGSOC | 全部 6 個 | 6 | 703 |
| 合計 | | 67 | 38,656 |

成本估計（論文設定：4 chain、burn-in 100、5,000 iteration、100 particle、beta-binomial、semi-adapted、outlier 開啟）：

- **Python 0.8.0：約 43 core-hour**。〔估計〕算法是論文牆鐘 × 4 chain。假設 0.8.0 和 0.7.0 一樣快、機器和論文相近；兩者都沒有實測。FS-CRP 佔一半（23 core-hour），因為它有兩種方法、8 個樣本。
- **Rust：約 1.7 core-hour**。〔估計〕用 Python ÷ 25。25 倍來自 M7 V3 run 集：Rust 360 個 run 合計 2,246 run-秒（`phyclone_rs/v3/rust_m7/run_rust.log`）；同一批設定中有 Python 時間的 315 個 run 估計 56,480 秒（`phyclone_rs/v3/baseline/summaries/per_seed.tsv` 的平均 × seed 數）。那是 -b 20 -n 200、1 chain 的設定，機器同時有其他負載，所以只是粗估。
- 論文的確切 flag〔論文，`notes/zh-TW/03_EXPERIMENTS_RESULTS.md`，Main §2.4.2〕沒有寫 outlier prior 的值，dataset 也沒有附每個 trial 的指令。輸入 cluster 檔沒有 `outlier_prob` 欄〔實測，FS-CRP、Pairtree〕，所以 0.8.0 只有兩個選擇：全域 `-l／--outlier-prob`，或 `--assign-loss-prob`（由 cluster 資料指派 low／high prior，Supplement S1.7.1：預設 0.0001／0.4）。0.8.0 的 `-d` 預設 beta-binomial、`-p` 預設 semi-adapted〔程式，`phyclone/cli.py`〕。跑之前要先決定 outlier flag。

## 限制

- **RRE、LPR 不能用 dataset 的檔案算。** RRE 要每個不重複解的 SNV 指派；dataset 只有 `topology_report.tsv`（clone id 的 Newick，沒有 SNV 指派），沒有 `SAMPLED_TOPOLOGIES.tar.gz`。LPR 要用 PhyClone 的邊際化重新計算真值的分數，也沒有公開程式。V4 新跑的 run 要保留 `topology-report -t SAMPLED_TOPOLOGIES.tar.gz`，之後才能補 RRE。
- 指標定義是反推的（論文沒有公開評估程式）。證據是 2,830／2,832 列完全相同，不是原始碼。
- HGSOC p3 的解釋是用數值湊出來的 408 個 pair，再用 prevalence 佐證。它能重現 10 列，但不是唯一可能的解釋。
- 子集的成本是用論文的時間推的，沒有在本機實測。Rust 25 倍是不同設定下的粗估。
- `memory` 欄的單位沒寫。
