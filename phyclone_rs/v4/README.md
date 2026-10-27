# V4：PhyClone 論文 benchmark 子集上的 Rust vs Python 比較（M8b，2026-10-27）

問題：在論文 benchmark 的子集上，Rust 版（haploclone）的 V-measure 與 AD F-score 是否系統性地比 Python PhyClone 0.8.0、論文的 0.7.0 輸出差？（`PORTING.md` 第 3 節 V4、第 4 節）

## 結論

- **判定：V 與 AD 都是 PASS。** 全部 67 個 trial 的 Rust − Python 成對差：V 中位數 +0.0000（Wilcoxon p = 0.70），AD 中位數 +0.0000（p = 0.58）。〔實測，`summary.tsv`〕
- 沒有任何 trial 的 Rust 比 Python 差 > 0.05。〔實測〕
- 和論文 0.7.0 比，Rust 與 Python 一樣：中位數差都是 0。FS-CRP_Loss 有 3 個 trial 的 AD 比論文低 0.07–0.17，Python 0.8.0 與 Rust 完全相同，所以不是 port 的問題。〔實測〕
- 速度：同樣 14 slot × 4 chain，Python 牆鐘 1,170 秒，Rust 242 秒。逐 trial 的 run 時間中位數比 8.1×。〔實測，一次 run，見第 4 節〕

## 1. 指令

```bash
PY=~/venvs/phyclone/bin/python
$PY phyclone_rs/v4/run_v4.py progress                       # 進度（兩個 impl 各幾個完成／執行中／失敗）
cat /big8_disk/boyu114/phyclone_v4/python080/progress.tsv   # 每個完成的 job 一行
cat /big8_disk/boyu114/phyclone_v4/rust/progress.tsv
$PY phyclone_rs/v4/run_v4.py run --impl python080 --slots 14 --launch-deadline 7200
$PY phyclone_rs/v4/run_v4.py run --impl rust --slots 14 --launch-deadline 7200
$PY phyclone_rs/v4/run_v4.py score                          # 寫 results.tsv、summary.tsv，印出判定
```

- 有 `status.json` 的 job 不會重跑，所以 `run` 中斷後再跑會接著做。失敗的 job 只有加 `--retry-failed` 才重跑。
- 這次的實際啟動方式：一個 `nohup` 依序跑 Python 再跑 Rust，log 在 `/big8_disk/boyu114/phyclone_v4/driver.log`。

## 2. 設定（使用者決定）

- 子集：`lab_report/2026-10-27_v4_evaluator/proposed_subset.tsv`，67 個 job（trial × program）。
- `run`：`--num-chains 4 -b 100 -n 5000 --num-particles 100 -d beta-binomial -p semi-adapted --seed 1 -c <cluster file>`。
  - `PhyClone` 列加 `--assign-loss-prob`（low／high loss prob 用預設值，不傳 `-l`、`--high-loss-prob`）。輸入在 `program_inputs/phyclone_outliers/`。
  - `PhyClone-N` 列不加 loss 選項，outlier 關閉。輸入在 `program_inputs/phyclone_naive/`。
  - cluster file 是 `program_inputs/<dir>/` 中唯一存在的那個：`results.tsv.gz`（TSSB、FS-CRP）、`results.tsv`（HGSOC）、`clusters.tsv.gz`（Pairtree、CONIPHER、Copy_Number_Error）。
- 後處理：`map`（預設 joint-likelihood）與 `topology-report -t topologies.tar.gz`（保留 archive，之後可算 RRE）。
- Python：upstream 0.8.0（`research/phyclone_research/PhyClone`，commit 27383246），不是 `tools/phyclone_hp.py`。Rust：`haploclone` branch rust-port，commit 8326226 的 release binary。
- CPU：最多 14 個 job 同時跑 × 4 chain = 56 core（機器的一半）。兩個 impl 都設 `OMP/MKL/OPENBLAS/NUMBA_NUM_THREADS=1`。依論文的牆鐘時間由長到短排程。開始 2 小時後不再啟動新 job。
- 原始輸出（不在 repo）：`/big8_disk/boyu114/phyclone_v4/<impl>/<job key>/`，impl = `python080`、`rust`。每個目錄有 `command.txt`、`run.log`、`map.log`、`topo.log`、trace、`map_table.tsv`、`map_tree.nwk`、`map_prev.tsv`、`topology_report.tsv`、`topologies.tar.gz`、`status.json`（每步的 exit code 與牆鐘秒數）。

## 3. 評估

- 指標用 `tools/eval_phyclone_dataset.py` 的 `score`（從 `map_table.tsv` + `map_tree.nwk` 讀）。論文 0.7.0 的值用 `lab_report/2026-10-27_v4_evaluator/validation_paper_outputs.tsv` 的 xlsx 欄位。
- HGSOC p3 的 AD：真值和論文不同（見 evaluator README），所以 p3 的 AD 不放進「和論文比」的差值；Rust vs Python 仍然比。
- 每個 trial 只有一個 seed。所以差值的分布反映 trial 之間的雜訊加上 seed 雜訊，不能把單一 trial 的差當成 Rust 的偏差。

### 判定規則（跑之前寫下）

對每個指標（V、AD），用全部 67 個 trial 的成對差 Rust − Python：

- **PASS**（沒有系統性變差）：中位數在 ±0.01 內，**而且** two-sided Wilcoxon signed-rank p ≥ 0.01（差為 0 的 trial 不列入）。
- **WORSE**：中位數 < −0.01，或 p < 0.01 且平均差為負。
- **DIFFERENT（Rust 較好）**：其他情況（顯著但方向是 Rust 較好）。

輔助資訊（不改變判定）：每個 dataset 的平均、中位數、sign test；Rust − 論文與 Python − 論文的對照；Rust 比 Python 差 > 0.05 的 trial 數。每個差 > 0.05 的 trial 都要個別看（MAP outlier 數、clone 數）。

## 4. 結果

67 個 job，兩個 impl 都 0 失敗（`run`、`map`、`topology-report` exit 0）。Rust trace 每個 run 有 20,000 列 iteration（4 chain × 5,000）。

### 4.1 指標（每組 trial 的平均；差值是成對差）

+/− 是差不為 0 的 trial 中 Rust 較好／較差的個數。HGSOC 的論文 AD 平均不含 p3（4 個 trial），其他欄含 6 個，所以這一格不能直接比。

| 組 | n | 指標 | 論文 0.7.0 | Python 0.8.0 | Rust | Rust−Py 平均／中位數 | +/− | Wilcoxon p | Rust−論文 中位數 (p) | Py−論文 中位數 (p) |
|---|---|---|---|---|---|---|---|---|---|---|
| CONIPHER_No-Noise | 5 | V | 0.8411 | 0.8411 | 0.8411 | +0.0000／+0.0000 | 0/0 | 1 | +0.0000 (0.5) | +0.0000 (0.5) |
| CONIPHER_No-Noise | 5 | AD | 0.9332 | 0.9387 | 0.9345 | -0.0042／+0.0000 | 2/2 | 0.625 | +0.0009 (0.375) | +0.0045 (0.312) |
| CONIPHER_Noise | 5 | V | 0.7172 | 0.7172 | 0.7172 | +0.0000／+0.0000 | 2/1 | 1 | -0.0000 (0.688) | -0.0000 (0.5) |
| CONIPHER_Noise | 5 | AD | 0.7852 | 0.7921 | 0.7947 | +0.0027／+0.0000 | 2/2 | 0.875 | +0.0094 (0.0625) | +0.0041 (0.125) |
| Copy_Number_Error | 9 | V | 0.7800 | 0.7800 | 0.7800 | +0.0000／+0.0000 | 1/0 | 1 | +0.0000 (0.641) | +0.0000 (0.641) |
| Copy_Number_Error | 9 | AD | 0.9020 | 0.9017 | 0.9000 | -0.0017／-0.0022 | 1/6 | 0.219 | -0.0022 (0.203) | +0.0000 (1) |
| FS-CRP_Loss | 9 | V | 0.9969 | 0.9972 | 0.9973 | +0.0000／+0.0000 | 1/0 | 1 | +0.0001 (0.297) | +0.0001 (0.375) |
| FS-CRP_Loss | 9 | AD | 0.9795 | 0.9640 | 0.9640 | -0.0000／+0.0000 | 0/2 | 0.5 | +0.0000 (0.945) | +0.0000 (0.945) |
| FS-CRP_Loss/N | 9 | V | 0.9895 | 0.9897 | 0.9895 | -0.0002／+0.0000 | 0/2 | 0.5 | +0.0000 (0.812) | +0.0000 (0.156) |
| FS-CRP_Loss/N | 9 | AD | 0.8887 | 0.8886 | 0.8881 | -0.0005／+0.0000 | 0/2 | 0.5 | +0.0000 (0.812) | +0.0000 (0.625) |
| HGSOC | 6 | V | 0.9221 | 0.9221 | 0.9221 | +0.0000／+0.0000 | 0/0 | 1 | +0.0000 (1) | +0.0000 (1) |
| HGSOC | 6 | AD | 0.9590 | 0.9195 | 0.9195 | +0.0000／+0.0000 | 0/0 | 1 | +0.0000 (1) | +0.0000 (1) |
| Pairtree | 8 | V | 0.8550 | 0.8568 | 0.8568 | +0.0000／+0.0000 | 0/0 | 1 | +0.0000 (0.375) | +0.0000 (0.375) |
| Pairtree | 8 | AD | 0.7774 | 0.7776 | 0.7952 | +0.0175／+0.0000 | 1/0 | 1 | +0.0000 (1) | +0.0000 (1) |
| TSSB_High | 6 | V | 0.9977 | 0.9977 | 0.9977 | +0.0000／+0.0000 | 0/0 | 1 | +0.0000 (0.75) | +0.0000 (0.75) |
| TSSB_High | 6 | AD | 0.9943 | 0.9944 | 0.9943 | -0.0001／+0.0000 | 0/2 | 0.5 | -0.0000 (0.375) | +0.0000 (1) |
| TSSB_Low | 10 | V | 0.9747 | 0.9747 | 0.9747 | +0.0000／+0.0000 | 0/0 | 1 | +0.0000 (1) | +0.0000 (1) |
| TSSB_Low | 10 | AD | 0.9665 | 0.9655 | 0.9701 | +0.0046／+0.0000 | 2/1 | 0.75 | +0.0000 (0.875) | +0.0000 (1) |
| ALL | 67 | V | 0.9074 | 0.9077 | 0.9077 | -0.0000／+0.0000 | 4/3 | 0.703 | +0.0000 (0.2) | +0.0000 (0.0765) |
| ALL | 67 | AD | 0.9109 | 0.9075 | 0.9099 | +0.0024／+0.0000 | 8/17 | 0.578 | +0.0000 (0.807) | +0.0000 (0.186) |

### 4.2 值得看的 trial

| trial | 指標 | 論文 | Python | Rust | 說明 |
|---|---|---|---|---|---|
| FS-CRP loss_prop_0.1_run0（PhyClone） | AD | 0.9998（28 outlier） | 0.9285（0） | 0.9285（0） | 兩個 impl 都把相同 cluster（0、9）設 0.4 loss prior，MAP 都沒有 outlier |
| FS-CRP loss_prop_0.2_run0 | AD | 0.9999（58） | 0.8252（0） | 0.8252（0） | 同上（cluster 9） |
| FS-CRP loss_prop_0.1_run2 | AD | 1.0000（29） | 0.9231（0） | 0.9231（0） | 同上（cluster 9） |
| FS-CRP loss_prop_0.2_run1 | AD | 0.8246（154） | 0.9995（109） | 0.9995（109） | 這次反過來，0.8.0／Rust 較好 |
| Pairtree sim_K10_S3_T1000_M1000_run2 | AD | 0.7811 | 0.7828 | 0.9231 | Rust 較好 +0.14；clone 數相同（6） |
| TSSB_Low S2_D1000_M100_run0 | AD | 0.9523 | 0.9523 | 1.0000 | Rust 較好 +0.05 |
| CONIPHER_No-Noise LTXSIM004 | AD | 0.9441 | 0.9643 | 0.9449 | Rust 較差 −0.019（最大的 Rust 劣勢） |

- 〔推論〕FS-CRP 的 3 個落差來自設定或版本（論文沒寫 outlier prior；`--assign-loss-prob` 預設值下 MAP 選了沒有 outlier 的樹），不是 port。證據：Python 與 Rust 的 log 標出相同的 lost cluster，MAP 指標完全相同。
- 〔實測〕Rust 與 Python 的 MAP 在多數 trial 完全相同：V 只有 7 個 trial 不同，AD 25 個不同。AD 不同的 25 個中 Rust 較差 17 個、較好 8 個（sign test p = 0.11），但平均差 +0.0024（Rust 略好），差都很小。Copy_Number_Error 的 AD 是 1/6，平均 −0.0017，未達顯著（p = 0.22）。
- 每個 trial 只有一個 seed，這些差反映 seed 加 trial 的雜訊。

### 4.3 速度（V5 預覽）

| 組 | n | Python run 合計 h | Rust run 合計 h | Python/Rust 中位數 | Python/論文 中位數 |
|---|---|---|---|---|---|
| CONIPHER_No-Noise | 5 | 0.184 | 0.020 | 10.4× | 0.32 |
| CONIPHER_Noise | 5 | 0.291 | 0.029 | 9.1× | 0.34 |
| Copy_Number_Error | 9 | 0.434 | 0.046 | 10.3× | 0.30 |
| FS-CRP_Loss | 9 | 1.262 | 0.346 | 3.7× | 0.45 |
| FS-CRP_Loss/N | 9 | 1.235 | 0.332 | 4.1× | 0.43 |
| HGSOC | 6 | 0.132 | 0.018 | 9.0× | 0.69 |
| Pairtree | 8 | 0.213 | 0.037 | 8.0× | 0.31 |
| TSSB_High | 6 | 0.254 | 0.031 | 8.6× | 0.39 |
| TSSB_Low | 10 | 0.172 | 0.015 | 12.7× | 0.29 |
| ALL | 67 | 4.176 | 0.874 | 8.1× | 0.34 |

- 牆鐘：Python 1,170 秒，Rust 242 秒（兩個 phase 都是 14 slot、由長到短）。core-hour（run 牆鐘 × 4 chain）：Python 16.7，Rust 3.5。〔實測〕
- 〔實測〕FS-CRP（8 樣本、有 outlier）只快 3.7–4.1×，其他 dataset 8–13×。限制因素沒有 profile，不知道。〔猜測〕FS-CRP 的 trace 長（每 chain 5,000 iter、600 SNV），可能在 outlier 相關的步驟較慢。
- 〔實測〕Python 0.8.0 的時間約是論文 0.7.0 xlsx 時間的 0.34 倍（中位數）。機器與負載都不同（本機跑時 load 約 43–57），所以這不是 0.8.0 vs 0.7.0 的速度比較。
- 一次 run、沒有重複，所以沒有 spread；V5 要用重複 run 和 profile 才能下結論。

### 4.4 Evaluator 的問題（回報，沒有修改）

- `tools/eval_hp_truth_phyclone.py` 的 `newick_parents` 不去掉空白。論文 HGSOC p3_wgs_t 的 `tree.nwk` 是 `((((4)3, 2)1,5)0)root;`，node `" 2"` 失去 parent。所以用 table 讀時 AD = 0.7931，用 tree.json 讀時是 0.8932（xlsx 0.9294）。
- 只有論文的這個 Newick 有空格。0.8.0 與 Rust 的 `map_tree.nwk` 沒有空格；`run_v4.py score` 會 assert 這件事。論文的 V、AD 直接用 xlsx 的值。

## 5. 檔案

- `run_v4.py`：runner、進度、評分。
- `results.tsv`：每個 trial × impl（paper070、python080、rust）一列：V、AD、n_pred、n_true、MAP clone 數、MAP outlier 數、run 牆鐘秒數。
- `summary.tsv`：每組與 ALL 的平均、成對差、Wilcoxon、sign test、差 > 0.05 的個數，以及速度列（`metric = run_wall_s`）。
