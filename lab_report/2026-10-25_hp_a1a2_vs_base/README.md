# HP emission A1／A2 與 PhyClone 基線比較（2026-10-25）

設計：[`research/phyclone_research/HP_EXTENSION_DESIGN.md`](../../research/phyclone_research/HP_EXTENSION_DESIGN.md) §3–§4。
基線與真值樹：[`lab_report/2026-10-24_hp_truth_tree_phyclone/`](../2026-10-24_hp_truth_tree_phyclone/README.md)。
範圍：**只有一個 bulk 樣本**（老闆 2026-10-25 指示）。

## 結論

- **A2 解決了 P3（突變遺失）。** 〔實測，3 份資料 × 3 個 MCMC seed〕
  - s10 被併進 C3 的 posterior 比例：base 0.92–1.00 → A2 0.000–0.007。
  - s10 回到 truncal clone 的比例：base 0 → A2 0.80–0.86。
  - s2 回到 truncal clone 的比例：base 0.37–0.47 → A2 0.72–0.78。
  - truncal clone 的 MAP CCF：base 0.87–0.90 → A2 0.97–1.00（真值 1.00）。
  - A2 沒有產生假 clone。
- **A1 單獨使用會變差。** 它讓 s10 離開 C3，但 s10 改成一個假 clone，插在 C3 上面（posterior 0.14–0.45）。原因是 dominant state 的 `cn_hp2` = 0，只能用 1 代替，所以 VAF 被錯誤解讀。A1 不應該單獨使用。〔實測＋推論〕
- **P1（C1／C2 合併）沒有改善。** 三種方法的合併比例都是 1.000。truncal clone 的 CCF 雖然回到約 1.0，但 s4（C2，CCF 0.80）仍然被併進去。〔實測〕
- **P2（直線與分岔拓樸）沒有改善。** 直線樹的比例：base 0.38–0.44，A2 0.43–0.47。這符合設計：A1／A2 只改單一 SNV 的 likelihood，不帶任何拓樸資訊。P2 要靠 B（read 共現）。〔實測＋推論〕

## 資料

- 真值：與 2026-10-24 相同的 4-clone 設計樹。一個 sample，purity 0.40，depth 200×，100 個 SNV（10 種角色 × 10 個）。
- 資料 seed 1、2、3。資料 seed 1 的 `data.tsv` 和 2026-10-24 的輸入逐 byte 相同（`cmp`）。
- 新增的 HP 輸入（`tools/hp_truth_tree_to_phyclone.py`）：
  - `data_hp.tsv`：原本 8 欄＋`snv_hp`、`segment_id`、`cn_hp1`、`cn_hp2`（dominant state）、HP1／HP2／unphased 的 ref／alt。phased 比例 0.85。HP 拆分用另一個 RNG，所以 `data.tsv` 不變。
  - `segments.tsv`：每個 segment 的祖先狀態 A（= C1）、另一個狀態 B、φ（tumour 中處於 B 的比例）。**這次用的是真值 φ，沒有加雜訊。**

| segment | A（HP1, HP2） | B | φ | 影響的角色 |
|---|---|---|---|---|
| A | (1,1) | (2,1) | 0.80 | s1（gain 之前）、s8（gain 之後） |
| B | (1,1) | (1,0) | 0.45 | s2（遺失） |
| C | (1,1) | — | 0 | s3–s7 |
| D | (1,1) | (2,0) | 0.80 | s9（cnLOH，multiplicity 2）、s10（cnLOH，遺失） |

## 做法

- `tools/phyclone_hp.py`：在 submodule 外替換 `phyclone.run.load_data`，再呼叫原本的 CLI。樹、SMC／PG、trace、map、topology-report 都沒有改。（實作位置是 §8 第 3 題的暫定預設，見下方「暫定決定」。）
- A1：所有 tumour cell 都用 dominant state 的 HP CN，multiplicity 1…`cn_h`。
- A2：三種情境的混合（E1：CN 在 SNV 之後，含遺失；E2：SNV 在 CN 之後；E3：不同分支）。
- 實作時修正的兩點：
  1. **E2 的 multiplicity 只能是 1。** 新出現的 SNV 只在一份 copy 上。第一版允許 1…`b_h`，s8 的峰值錯落在 0.25（真值 0.45）。修正後回到約 0.45。
  2. **不可能的 CCF 不能給 −inf。** s10、s2 在 1−φ < f < φ 時沒有任何情境成立。−inf 會讓 PhyClone 的 Gibbs-MH 產生 NaN，所以改成「該 SNV 最差可行值 − 10」。
- 每次 run：`-d binomial -b 100 -n 1000 --num-chains 4`，outlier 關閉，再跑 map 與 topology-report，最後刪除 trace。

```bash
bash lab_report/2026-10-25_hp_a1a2_vs_base/run_all.sh "1 2 3" "1 2 3"     # 27 次 run，約 25 分鐘
D=lab_report/2026-10-25_hp_a1a2_vs_base
for ds in 1 2 3; do
  python3 tools/summarize_hp_truth_topologies.py $D/data_s$ds \
    $(for m in base a1 a2; do for s in 1 2 3; do echo $D/runs/data_s$ds/${m}_m$s; done; done) | sed "s/^/d$ds\t/"
done | awk 'NR==1||$2!="run"' > $D/summary_raw.tsv
# summary_by_method.tsv = summary_raw.tsv 依 (方法, 資料 seed) 平均，加上 map_table.tsv 中 s3 所在 clone 的 CCF
```

## 結果

### 依方法與資料 seed（3 個 MCMC seed 的平均；`summary_by_method.tsv`）

| 方法 | 資料 | C1／C2 合併 | 直線樹 | s10 在 C3 | s10 在 truncal | s2 在 truncal | s10 假 clone 在 C3 上 | MAP truncal CCF |
|---|---|---|---|---|---|---|---|---|
| base | d1 | 1.00 | 0.39 | 1.00 | 0.00 | 0.47 | 0.00 | 0.88 |
| base | d2 | 1.00 | 0.43 | 0.93 | 0.00 | 0.38 | 0.04 | 0.90 |
| base | d3 | 1.00 | 0.39 | 1.00 | 0.00 | 0.46 | 0.00 | 0.88 |
| A1 | d1 | 1.00 | 0.36 | 0.65 | 0.00 | 0.52 | 0.15 | 0.93 |
| A1 | d2 | 1.00 | 0.43 | 0.00 | 0.01 | 0.40 | 0.43 | 0.93 |
| A1 | d3 | 1.00 | 0.37 | 0.15 | 0.00 | 0.59 | 0.34 | 0.91 |
| **A2** | d1 | 1.00 | 0.43 | **0.01** | **0.80** | **0.75** | 0.00 | **0.97** |
| **A2** | d2 | 1.00 | 0.45 | **0.00** | **0.85** | **0.72** | 0.00 | **1.00** |
| **A2** | d3 | 1.00 | 0.44 | **0.00** | **0.81** | **0.77** | 0.00 | **0.98** |

真值：合併 0、直線樹 0、s10 在 C3 0、s10／s2 在 truncal 1、假 clone 0、truncal CCF 1.00。
「s10 在 truncal」和「s2 在 truncal」是 10 個複本中進 truncal clone 的平均比例。其他欄位是 posterior 中符合條件的比例。

### MAP 例子（資料 seed 1，MCMC seed 1）

| 方法 | clone 0（truncal） | clone 1 | clone 2 |
|---|---|---|---|
| base | 0.89：s1、s2×5、s3、s4、s9 | 0.43：s2×5、s5、s8×8、s10×1 | 0.10：s6、s7、s8×2、s10×9 |
| A1 | 0.93：s1、s2×5、s3、s4、s9 | 0.41：s2×5、s5、s8、s10×6 | 0.10：s6、s7、s10×4 |
| A2 | 0.97：s1、s2×8、s3、s4、s9、**s10×10** | 0.43：s2×2、s5、s8 | 0.09：s6、s7 |

三種方法的 MAP 都是直線樹 `(((2)1)0)`，而且 s4（C2）都被併進 truncal。

### 單一 SNV 的 likelihood 峰值（A2，資料 seed 1 的 10 個複本）

| 角色 | 峰值 | 說明 |
|---|---|---|
| s1 | 0.83–1.00 | base 是 0.80 左右 |
| s8 | 0.20–0.61，中心約 0.45 | 修正 E2 之後 |
| s9 | 0.80–1.00 | |
| s10 | 0.12–0.20 或 0.91–0.98 | **兩個峰一樣高**：E1 遺失（f≈1）與 E3 不同分支（f≈1−φ=0.2） |
| s2 | 0.37–0.55 | 另一個峰在 f≈0.91（E1 遺失），高度相同 |

s10、s2 的兩個峰在單一 SNV 層級無法分辨。是樹的結構（已經有 CCF≈1 的 truncal clone，但沒有 CCF 0.2 的 clone）讓它們回到 truncal。〔實測＋推論〕

## 解讀

- **A2 的作用是「多給一個正確的解釋」，不是直接指出答案。** 遺失的 SNV 在 A2 下同時符合「truncal＋遺失」和「另一個分支的小 clone」。在這棵樹中，後者沒有對應的 clone，所以 posterior 選前者。如果剛好有一個 CCF ≈ 1−φ 的真 clone，A2 可能把遺失的 SNV 錯放進去。要用不同的真值設計測試這個風險。〔推論〕
- **P1 沒有改善的可能原因。** truncal CCF 回到 1.0 後，s4 的 0.80 和它的距離反而變大，但 PhyClone 仍然把它們合併。可能是 FSCRP prior 對多一個 node 的懲罰，大於 10 個 s4 SNV 在 0.80 和 1.0 之間的 likelihood 差。這還沒有驗證。〔推論〕
- **A1 的問題來自 dominant state 的假設。** cnLOH 讓 dominant state 的 SNV 那一側 CN 為 0，A1 無法表達這件事，只能硬設為 1。所以 A1 的價值只在沒有 subclonal CN 的 segment。〔推論〕

## 限制

- **φ 用真值。** 真實資料的 φ 要從 HP depth 估計，來源還沒有決定（設計 §8 第 1 題）。下一步要測試加雜訊的 φ（`--phi-noise`）。
- **phasing 是理想的。** 沒有 switch error，也沒有 PS block 方向翻轉（§8 第 2 題）。
- A2 假設每個 segment 只有兩種 tumour 狀態，而且狀態 A 是祖先狀態。
- 真值樹只有一種設計，每種角色只有 10 個 SNV。
- 只用 binomial density；wrapper 還不支援 beta-binomial 和 cluster 檔。

## 暫定決定（設計 §8 尚未回答）

- 實作位置：暫時用 submodule 外的 wrapper（§8 第 3 題）。改用 submodule 時，只要把 `snv_grid` 移進 `to_likelihood_grid`。
- 成功標準（§8 第 4 題）：P3 已經達到草案門檻，P1、P2 還沒有。門檻本身仍待老闆確認。

## 檔案

| 檔案 | 內容 |
|---|---|
| `run_all.sh` | 產生資料並執行 27 次 run |
| `data_s{1,2,3}/` | 每份資料的 `data.tsv`、`data_hp.tsv`、`segments.tsv`、`truth.tsv`、真值樹 |
| `runs/data_s*/{base,a1,a2}_m{1,2,3}/` | MAP、`topology_report.tsv`、`topologies.tar.gz`、`run.log`（trace 已刪除） |
| `summary_raw.tsv` | 27 次 run 的 posterior 指標 |
| `summary_by_method.tsv` | 依方法與資料 seed 的平均 |

腳本：`tools/phyclone_hp.py`（A1／A2 wrapper）、`tools/hp_truth_tree_to_phyclone.py`（模擬器，新增 HP 輸出）、`tools/summarize_hp_truth_topologies.py`（新增 `s10_in_trunk`、`s2_in_trunk`）。
