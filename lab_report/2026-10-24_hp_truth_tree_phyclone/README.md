# HP-aware 設計真值樹：PhyClone 基線測試（2026-10-24）

真值樹與示意圖：[`research/simulation_pipeline_research/figures/hp_truth_tree.png`](../../research/simulation_pipeline_research/figures/hp_truth_tree.png)。

> **研究範圍備註（2026-10-25）：** 老闆指出，實務上通常拿不到病人的多樣本資料。所以研究主軸是「只有一個 bulk 定序樣本時，如何精確重建演化樹」。兩個 sample 的結果只當作上限參考，不是要提出的解法。要解決的是單一 sample 的三個問題：C1／C2 合併、直線與分岔拓樸約 4:6 無法分辨、s10 被併進 C3。這些都要靠 long read／HP 特徵（HP 拆分計數、read 層級 SNV 共現、haplotype CN）補足。

## 結論

### 兩個 sample（2026-10-25；上限參考，非研究主軸）

- **加入第二個 sample 後，4 個真 clone 和它們的關係全部正確。** C1／C2 不再合併，C4 在 C2 之下，直線樹消失。posterior 比例 99.8–100%，10 次 run 的 MAP 都相同。〔實測〕
- **s2 回到 C1。** 它在 S2 的實際帶突變比例是 0.90，接近 1，所以被正確歸進 truncal。〔實測〕
- **s10 變成一個假 clone，插在 C1 和 C3 之間。** 它的 CCF（S1／S2 = 0.12／0.67）在兩個 sample 都大於 C3（0.09／0.38），所以 PhyClone 把它當成 C3 的祖先。posterior 比例 100%，outlier 模式也一樣。〔實測〕
- **outlier 機制仍然抓不到遺失。** s2、s10 進 outlier 的比例只有 0.15–0.36%，和正常 SNV 相同。〔實測〕
- **多 sample 解決了拓樸的不可辨識性，但解決不了突變遺失。** 遺失的 SNV 在每個 sample 都有一致的 CCF 組合，看起來就像一個真的 clone。HP 資訊（seg D 的 HP2 depth 下降、HP1 上升）可以指出它是 cnLOH 造成的遺失。〔推論〕

### 一個 sample

- **PhyClone 只推出 3 個 clone，真值有 4 個。** C1（CCF 1.00）和 C2（0.80）被合併成一個 clone，CCF 0.89。兩種模式都一樣。〔實測〕
- **cnLOH 遺失的 s10 被當成 C3 的突變。** 10 個中有 9 個進了 C3 的 clone（CCF 0.10）。這和圖中 ④ 的預測相同。〔實測〕
- **deletion 遺失的 s2 被拆到兩個 clone。** 它的 CCF 約 0.55，沒有一個 clone 能對上。〔實測〕
- **outlier 機制抓不到遺失。** 開啟 `-l 0.05` 後，s2、s10 被放進 outlier 的比例只有 0.1–0.4%，和正常的 s6、s7、s8 相同。seed 1 的 MAP 沒有任何 outlier。〔實測，5 個 seed〕
- **MAP 樹和 posterior 不一致。** 10 次 run 中有 9 次的 MAP 是直線樹（C3 在 C4 之下）。但 posterior 中直線樹只佔 36–42%，58–63% 是「C3 接在 truncal 下」的分岔樹。扣掉 C1／C2 合併，分岔樹和真值的形狀一致。只看 MAP 會選到錯的拓樸。〔實測，5 個 seed × 2 種模式〕
- **兩種拓樸無法用 bulk 資料分開。** 只有一個 sample 時，兩者都滿足 CCF 加總規則。posterior 在 5 個 seed 間很穩定（約 4:6），這表示這是資料本身的不可辨識性，不是 MCMC 沒收斂。read 共現（帶 s6 的 read 從不帶 s4）可以排除直線樹。〔推論〕

## 資料

- 真值：手動設計的 4-clone 樹（`tools/draw_hp_truth_tree.py` 的 `PROP`、`GENOME`、`SNV`）。不是任何模擬器的輸出。
- purity 0.40（實際值），一個 sample，平均 depth 200×。
- 10 種 SNV 角色，每種 10 個，共 100 個 SNV。同一角色在同一 segment，CN 歷史相同。
- major／minor：細胞數最多的 tumour 狀態。只給 PhyClone 的 8 個欄位，**沒有 HP 資訊**。

| 角色 | 真值 clone | 設計目的 |
|---|---|---|
| s1 | C1 | seg A 的 HP1 gain 在它之後（subclonal CN，multiplicity 2） |
| s2 | C1 | seg B 的 HP2 deletion，在 C4 遺失 |
| s3 | C1 | 對照組 |
| s4 | C2 | 對照組 |
| s5、s8 | C4 | s8 在 gain 之後（multiplicity 1） |
| s6、s7 | C3 | 低 CCF clone（0.10） |
| s9 | C1 | seg D cnLOH，在 C2／C4 的 multiplicity 變 2 |
| s10 | C1 | seg D cnLOH，在 C2／C4 遺失 |

## 做法

```bash
D=lab_report/2026-10-24_hp_truth_tree_phyclone
python3 tools/hp_truth_tree_to_phyclone.py $D/input --per-role 10 --depth 200 --seed 1

PH='env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python -c "from phyclone.cli import main; main()"'
# 模式一：outlier 關閉（預設）
eval "$PH run -i $D/input/data.tsv -o $D/run_no_outlier/trace.h5 -d binomial -b 100 -n 1000 --num-chains 4 --seed 1"
eval "$PH map -i $D/run_no_outlier/trace.h5 -t $D/run_no_outlier/map_tree.nwk -o $D/run_no_outlier/map_table.tsv"
# 模式二：outlier prob 0.05
eval "$PH run -i $D/input/data.tsv -o $D/run_outlier05/trace.h5 -d binomial -b 100 -n 1000 --num-chains 4 --seed 1 -l 0.05"
eval "$PH map -i $D/run_outlier05/trace.h5 -t $D/run_outlier05/map_tree.nwk -o $D/run_outlier05/map_table.tsv"

python3 tools/eval_hp_truth_phyclone.py $D/input $D/run_no_outlier
python3 tools/eval_hp_truth_phyclone.py $D/input $D/run_outlier05
```

- 沒有 cluster 檔，分群與建樹都由 PhyClone 自己做。
- 用 binomial density，因為資料就是用 binomial 抽樣產生的。
- 每種模式約 15 分鐘（4 條 chain 平行）。

## 結果

### 每個角色被分到哪裡

「預測 CCF」= 用 PhyClone 的 likelihood 對無雜訊計數逐 SNV 求 MLE（圖中 ④ 的「估計：期望」）。

| 角色 | 真值 | 實際帶突變 | 預測 CCF | `-l 0`：clone（個數）／CCF | `-l 0.05`：clone（個數）／CCF |
|---|---|---|---|---|---|
| s1 | C1，1.00 | 1.00 | 0.92 | 0（10）／0.89 | 0（10）／0.89 |
| s2 | C1，1.00 | 0.55 | 0.60 | 1（5）、0（5）／0.43、0.89 | 1（6）、0（4）／0.44、0.89 |
| s3 | C1，1.00 | 1.00 | 1.00 | 0（10）／0.89 | 0（10）／0.89 |
| s4 | C2，0.80 | 0.80 | 0.80 | 0（10）／0.89 | 0（10）／0.89 |
| s5 | C4，0.45 | 0.45 | 0.45 | 1（10）／0.43 | 1（10）／0.44 |
| s6 | C3，0.10 | 0.10 | 0.10 | 2（10）／0.10 | 2（10）／0.10 |
| s7 | C3，0.10 | 0.10 | 0.10 | 2（10）／0.10 | 2（10）／0.10 |
| s8 | C4，0.45 | 0.45 | 0.44 | 1（8）、2（2） | 1（6）、2（3）、0（1） |
| s9 | C1，1.00 | 1.00 | 0.90 | 0（10）／0.89 | 0（10）／0.89 |
| s10 | C1，1.00 | 0.20 | 0.12 | 2（9）、1（1）／0.10、0.43 | 2（9）、1（1）／0.10、0.44 |

### 推出的樹

| 模式 | MAP 樹 | clone 0 | clone 1 | clone 2 | outlier |
|---|---|---|---|---|---|
| `-l 0` | `(((2)1)0)root`：直線 | C1＋C2，0.89 | C4，0.43 | C3＋s10，0.10，parent = clone 1 | 不適用 |
| `-l 0.05` | `((1,2)0)root`：分岔 | C1＋C2，0.89 | C4，0.44 | C3＋s10，0.10，parent = clone 0 | 0 個 |

真值：C1 → {C2, C3}，C2 → C4。因為 C1 和 C2 被合併，`-l 0.05` 的分岔樹在合併後與真值一致；`-l 0` 的直線樹把 C3 錯放到 C4 之下。

### 對照圖中 ④ 的預測

| 預測 | 結果 |
|---|---|
| s10 被併進 C3 | 符合（9／10，兩種模式都一樣） |
| s2 不像任何 clone | 符合：被拆到 clone 0 和 clone 1 |
| s1、s9 的 CCF 被低估 | 沒有被拆出來，但 truncal clone 的 CCF 被拉到 0.89 |
| s4、s5、s8 正確 | s5 正確；s8 大多正確；s4 被併進 truncal |

## 多 seed 與 posterior 拓樸

同一份資料，MCMC seed 1–5，兩種模式各 5 次。每次 4 條 chain × 1000 次迭代，共 4000 個 posterior sample。

```bash
bash lab_report/2026-10-24_hp_truth_tree_phyclone/run_seeds.sh 1 2 3 4 5      # run + map + topology-report
python3 tools/summarize_hp_truth_topologies.py $D/input $D/run_no_outlier $D/seeds/no_outlier_s{2,3,4,5} \
    $D/run_outlier05 $D/seeds/outlier05_s{2,3,4,5} > $D/topology_posterior_summary.tsv
```

- `topology-report` 依 `tree_hash` 分組。4000 個 sample 有 3241–3505 種，因為 hash 也包含每個 SNV 的分群。所以要把每棵樹化約成要問的問題，再依 `count` 加權（`tools/summarize_hp_truth_topologies.py`）。

### MAP 樹

| 模式 | seed 1 | seed 2 | seed 3 | seed 4 | seed 5 |
|---|---|---|---|---|---|
| `-l 0` | 直線 | 直線 | 直線 | 直線 | 直線 |
| `-l 0.05` | 分岔 | 直線 | 直線 | 直線 | 直線 |

直線 = `(((2)1)0)`，C3 在 C4 之下。分岔 = `((1,2)0)`，C3 接在 truncal 下。

### posterior 比例（`topology_posterior_summary.tsv`）

| 指標 | `-l 0`（5 個 seed 範圍） | `-l 0.05`（5 個 seed 範圍） | 真值 |
|---|---|---|---|
| clone 數 = 3 | 0.96–0.98 | 0.95–0.97 | 4 |
| C1、C2 合併 | 1.000 | 1.000 | 否 |
| C3 在 C4 之下（直線） | 0.377–0.398 | 0.357–0.415 | 否 |
| C3 的 parent = truncal clone（分岔） | 0.594–0.616 | 0.573–0.634 | 是（合併後） |
| s10 多數和 C3 同 clone | 0.998–0.999 | 0.997–0.999 | 否 |
| s2 被拆到多個 clone | 1.000 | 1.000 | — |
| 每個 sample 中 s2＋s10 進 outlier 的個數（共 20 個） | 0 | 0.027–0.060 | 20 |
| 有任何 outlier 的 sample 比例 | 0 | 0.141–0.184 | — |

### outlier 落在哪些角色（`-l 0.05`，每個 SNV 進 outlier 的 posterior 比例）

| 角色 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | s10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 範圍 | ≤0.05% | 0.15–0.23% | ≤0.03% | ≤0.05% | 0.13–0.30% | 0.22–0.33% | 0.22–0.40% | 0.19–0.49% | ≤0.03% | 0.13–0.44% |

遺失的 s2、s10 沒有比正常的 s5–s8 更常進 outlier。outlier 比較像是分給 CCF 較低、計數較少的 SNV，而不是分給「不符合樹」的 SNV。〔實測＋推論〕

## 兩個 sample（2026-10-25；上限參考，非研究主軸）

### 設計

樹、CN、SNV 的 HP 都不變，只改第二個 sample 的細胞組成。S1 就是原本的 sample。

| sample | purity | C1 | C2 | C3 | C4 | CCF：C2／C3／C4 |
|---|---|---|---|---|---|---|
| S1 | 0.40 | 0.10 | 0.35 | 0.10 | 0.45 | 0.80／0.10／0.45 |
| S2 | 0.60 | 0.30 | 0.20 | 0.40 | 0.10 | 0.30／0.40／0.10 |

- S2 中 C3（0.40）> C4（0.10），所以「C3 在 C4 之下」違反 CCF 加總規則。
- major／minor 依各 sample 的多數細胞狀態決定。所以 seg A 在 S1 是 (2,1)，在 S2 是 (1,1)；seg D 在 S1 是 (2,0)，在 S2 是 (1,1)。
- 遺失 SNV 在 S2 的實際帶突變比例：s2 = 0.90，s10 = 0.70。
- 單一 sample 的輸入重新產生後和原本逐 byte 相同（`cmp`），所以前面的結果不受轉換程式修改影響。

```bash
B=lab_report/2026-10-24_hp_truth_tree_phyclone; D=$B/two_sample
python3 tools/hp_truth_tree_to_phyclone.py $D/input --per-role 10 --depth 200 --seed 1 --two-sample
IN=$D/input OUT=$D/runs bash $B/run_seeds.sh 1 2 3 4 5          # 跑完 map + topology-report 後自動刪 trace
python3 tools/summarize_hp_truth_topologies.py $D/input $D/runs/no_outlier_s{1..5} $D/runs/outlier05_s{1..5} \
    > $D/topology_posterior_summary.tsv
python3 tools/eval_hp_truth_phyclone.py $D/input $D/runs/no_outlier_s1
```

### MAP 樹

10 次 run（5 個 seed × 2 種模式）的 MAP 都是 `(((2)1,(4)3)0)root`。

| clone | parent | CCF（S1／S2） | 包含的角色 | 對應真值 |
|---|---|---|---|---|
| 0 | root | 0.88／1.00 | s1、s2、s3、s9 各 10 個 | C1 ✓ |
| 3 | 0 | 0.76／0.25 | s4×10 | C2 ✓ |
| 4 | 3 | 0.40／0.10 | s5×10、s8×10 | C4 ✓ |
| 1 | 0 | 0.12／0.67 | s10×10 | **假 clone**（s10 遺失造成） |
| 2 | 1 | 0.09／0.38 | s6×10、s7×10 | C3，但 parent 錯成假 clone |

真值：C1 → {C2, C3}，C2 → C4。唯一的錯誤是 s10 變成 C3 的假祖先。

### posterior 比例（`two_sample/topology_posterior_summary.tsv`）

| 指標 | 一個 sample（10 次 run 範圍） | 兩個 sample（10 次 run 範圍） |
|---|---|---|
| clone 數 | 3：0.95–0.98 | 5：0.99–1.00 |
| C1、C2 合併 | 1.000 | 0.000 |
| C3 在 C4 之下（直線） | 0.357–0.415 | 0.000 |
| C2 接 truncal、C4 接 C2 | 0.000 | 0.998–1.000 |
| s10 自成 clone，且是 C3 的 parent | 0.000–0.001 | 1.000 |
| s10 多數和 C3 同 clone | 0.997–0.999 | 0.000 |
| s2 被拆到多個 clone | 1.000 | 0.002–0.039 |
| 每個 sample 中 s2＋s10 進 outlier 的個數（共 20 個；`-l 0.05`） | 0.027–0.060 | 0.035–0.061 |
| unique `tree_hash` 數（共 4000 個 sample） | 3241–3505 | 895–1287 |

### outlier 落在哪些角色（兩個 sample，`-l 0.05`）

| 角色 | s2 | s4 | s5 | s6 | s7 | s8 | s10 | 其他 |
|---|---|---|---|---|---|---|---|---|
| 範圍 | 0.17–0.36% | 0.02–0.24% | 0.07–0.48% | 0.10–0.44% | 0.03–0.14% | 0.09–0.49% | 0.15–0.26% | 0 |

## 解讀

- **C1／C2 合併。** 兩者的 CCF 差 0.20，又被 s1、s9 的低估（約 0.90）填在中間。單一 sample、200× 的資料不足以分開它們。〔推論〕
- **outlier 機制抓不到遺失。** PhyClone 把 outlier 定義為「不符合樹的突變」。s10 遺失後的 CCF（0.12）剛好接近 C3（0.10），所以它被當成 C3 的突變，而不是 outlier。HP 資訊可以分辨這個情況：s10 在 HP2，而同一段 seg D 的 HP2 depth 下降、HP1 上升。這是 cnLOH 的特徵，不是一個新的 clone。〔推論〕
- **拓樸差異來自單一 sample 的不可辨識性。** 兩棵 MAP 樹都滿足加總規則（0.89 ≥ 0.43＋0.10）。兩種模式只差在 outlier 參數，但 MAP 樹不同。這表示 posterior 在兩種拓樸之間搖擺。〔推論〕應該看 `topology-report`，不能只看 MAP。

## 限制

- 只有一份資料（資料 seed 1）。5 個 seed 只改 MCMC，沒有重抽資料。
- 一個 sample 的拓樸本來就難以辨識。兩個 sample 的組成是刻意設計成可辨識的（S2 中 C3 > C4），不代表真實多區域取樣的情況。
- 每種角色 10 個 SNV，數量很少。
- 這次只有基線。PhyClone 沒有欄位能接收 HP 資訊，所以 HP 的效果還沒有測。
- 沒有測 `--assign-loss-prob`。它需要 cluster 檔與 `chrom` 欄（`data/cluster_outlier_probabilities.py`）。

## 檔案

| 檔案 | 內容 |
|---|---|
| `input/data.tsv` | PhyClone 輸入（100 個 SNV） |
| `input/truth.tsv` | 每個 SNV 的角色、真值 clone、HP、segment、預測 CCF |
| `input/clusters_truth.tsv` | 真值分群（這次沒有使用） |
| `input/truth_tree.tsv` | 真值樹與 CCF |
| `run_*/map_tree.nwk`、`run_*/map_table.tsv` | PhyClone MAP 結果 |
| `run_*/eval_by_role.tsv`、`run_*/eval_clones.tsv` | 評估表 |
| `run_*/run.log` | 執行紀錄（seed 1） |
| `seeds/{no_outlier,outlier05}_s{2..5}/` | seed 2–5 的 MAP、`topology_report.tsv`、`topologies.tar.gz` |
| `run_*/topology_report.tsv`、`run_*/topologies.tar.gz`、`run_*/post.log` | seed 1 的 topology-report（另記在 `post.log`） |
| `topology_posterior_summary.tsv` | 10 次 run 的 posterior 摘要 |
| `run_seeds.sh` | 多 seed 執行腳本（`IN`、`OUT` 可換輸入與輸出目錄） |
| `two_sample/input/` | 兩個 sample 的輸入與真值（`truth.tsv` 的 S2 欄位加 `_S2` 後綴） |
| `two_sample/runs/{no_outlier,outlier05}_s{1..5}/` | 兩個 sample 的 MAP、`topology_report.tsv`、`topologies.tar.gz` |
| `two_sample/topology_posterior_summary.tsv` | 兩個 sample 的 posterior 摘要 |

所有 `trace.h5` 已在 2026-10-25 刪除（每個約 40 MB）。要重做 posterior 分析，請用 `run_seeds.sh` 重跑。

腳本：`tools/hp_truth_tree_to_phyclone.py`（轉換）、`tools/eval_hp_truth_phyclone.py`（評估）、`tools/summarize_hp_truth_topologies.py`（posterior 摘要）、`tools/draw_hp_truth_tree.py`（真值與圖）。
