# 03 本機 benchmark 資料集：真值格式與反推的生成參數

資料根目錄：`/big8_disk/boyu114/phyclone_dataset/`。整體盤點（trial 數、大小、md5、HGSOC 真值來源）見 repo 根目錄 `tumor_sample.md`。各資料集可用真值的欄位對照見 `plan.md` §5.9.2。本檔只補「和生成流程有關」的觀察。〔本機資料〕

檢查日期：2026-10-21。只檢查下列 trial，其他 trial 未逐一核對。

## 1. 共同格式

- 每個 trial：`data_archive/<trial>/{ground_truth, program_inputs, program_outputs}`。
- `ground_truth/tree.json` 是 networkx node-link 格式：
  - `nodes[]`：`id`、`snvs`（SNV ID 列表）、`clonal_prev`、`cellular_prev`（長度 = sample 數）。
  - `edges[]`：`{"parent": …, "child": …}`。
- `tree.json` 的節點屬性名稱和 `fscrp.py` 的節點屬性相同（`snvs`、`clonal_prev`、`cellular_prev`）。

## 2. FS-CRP_Loss

檢查 trial：`loss_prop_0.0_run0`、`loss_prop_0.1_run5`、`loss_prop_0.2_run0`，以及 `loss_prop_0.0_run*` 共 100 棵樹的 `tree.json`。

### 2.1 檔案

| 檔案 | 內容 |
|---|---|
| `ground_truth/data.tsv` | `mutation_id, sample_id, ref_counts, alt_counts, major_cn, minor_cn, normal_cn, tumour_content, error_rate, g_n, g_r, g_v, ccf, mu, cluster, coord, chrom` |
| `ground_truth/loss_dict.json` | 每個 loss 事件：`lost_at`（loss-node ID）、`snvs`、`num_missing`、`num_remaining`、`chrom` |
| `ground_truth/loss_tree.pdf` | loss 標註後的樹圖 |
| `program_inputs/phyclone_outliers/data.tsv` | 和 `ground_truth/data.tsv` **欄位相同**，含 `g_v`、`ccf`、`mu` 等真值欄 |

PhyClone 只讀它需要的欄位，所以真值欄留在輸入檔不影響結果。〔程式：`phyclone/data/pyclone.py::create_sample_data_point` 只讀計數、CN、`normal_cn`、`tumour_content`、`error_rate`〕自己重做 benchmark 時，輸入檔應移除真值欄。

### 2.2 反推的生成參數

| 項目 | 觀察值 | 對應 `simulate_data` 參數 |
|---|---|---|
| SNV 數 | 600 | `num_data_points=600` |
| sample 數 | 8 | `dim=num_samples=8` |
| depth | 每筆都是 1000 | `depth=1000` |
| tumour content | 1.0 | `tumour_content=1.0` |
| total CN | 2–6；`loss_prop_0.2_run0` 中每個 total 約 900–1000 筆（共 4800），近似均勻 | `min_cn=2`、`max_cn=6` |
| minor CN 最小值 | 1 | `min_minor_cn=1` |
| `error_rate` 欄 | 0.001 | `error_rate=1e-3` |
| `coord` | 等於 mutation ID 的序號（`m392` → 392） | 不是基因組位置 |
| `chrom` | 1–22 | 生成程式未公開 |

結論：參數和 `simulate_data` 的介面完全對得上。〔推論〕

### 2.3 樹形

- 100 棵 `loss_prop_0.0` 真值樹：root 都是 SNV 最多的節點；741 條邊都滿足 parent SNV 數 ≥ child。和 `fscrp.simulate_tree` 的偏向一致（見 [02 §4.1](02_CODE_PIPELINE.md)）。
- 節點數依 trial 改變（例：run0 有 10 個節點，`loss_prop_0.1_run5` 有 6 個）。

### 2.4 CN 在 sample 間不一致

- `loss_prop_0.0_run0`：600 個 SNV 全部在 8 個 sample 中有 ≥ 2 種 major/minor 組合。
- 例（`loss_prop_0.2_run0`）：`m392` 在 s0 是 2/1、`g_v=AAB`；在 s1 是 5/1、`g_v=AAAAAB`；在 s2 是 3/2、`g_v=AAABB`。
- 例（`loss_prop_0.0_run0`）：`m392` 在 s0 是 3/1、`g_v=AAAB`；在 s1 是 2/1、`g_v=AAB`；在 s3 是 4/1、`g_v=ABBBB`。（2026-10-21 核對）

### 2.5 Loss 事件

- `loss_prop_0.2_run0` 只有 1 個 loss 事件：loss-node 是 5，58 個 SNV，`num_remaining=233`，全部在 chr19。
- lost SNV 在 `data.tsv` 的 `chrom` 欄也全是 19，符合論文「同一條染色體」的描述。
- `ccf` 欄是 loss 前還是 loss 後的值，尚未確認。

## 3. TSSB_Low／TSSB_High

檢查 trial：`TSSB_High/S2_D1000_M10000_run0`、`TSSB_Low/S2_D1000_M100_run0`、`TSSB_Low/S128_D1000_M100_run0`。

- 真值計數檔：`ground_truth/down_sampled_data.tsv`。欄位比 FS-CRP 多 `mut_cn`、`total_cn`。
- depth 每筆都是 1000。檔名的 `D1000` 是 depth。
- CN 全部是 1/1，tumour content 1.0。符合論文「diploid heterozygous」。
- 檔名有 `down_sampled`，但 depth 全是 1000。降採樣的對象可能是 SNV 數，尚未確認。

## 4. CONIPHER 系列與 Copy_Number_Error

檢查 trial：`Copy_Number_Error/LTXSIM001_error_0.2`。

- 真值檔：`LTXSIM001.tsv`（原始）、`LTXSIM001_perturbed.tsv`（CN 擾動後）、`LTXSIM001_treeedges.tsv`、`tree.json`、`tree.png`。
- 欄位：`PATIENT, SAMPLE, VAR_POS, CHR, POS, REF, ALT, REF_COUNT, VAR_COUNT, DEPTH, TRUE_VAF, VAF_OBS, TRUE_CCF, TRUE_DCF, CCF_OBS, MUT_CN, CN_A, CN_B, TOTAL_CN, CN_PREVALENCE, PURITY, PLOIDY, CLUSTER, NOISE, mutation_id`。
- 有真實座標、allele-specific CN（`CN_A`／`CN_B`）、`MUT_CN`、purity < 1。這是本機唯一同時有 allele-specific CN、multiplicity 與 purity < 1 的模擬真值。
- 沒有 SNV 所在的 haplotype（`CN_A` 與 `CN_B` 哪一條帶突變未標）。

## 5. Pairtree

- 真值：`*.truth.pickle`、`truth.pdf`、`tree.json`。pickle 的欄位尚未讀取。
- 依論文與 `plan.md` §5.9.2：CN 全部 1:1，只有 `chrom`，沒有位置與 haplotype。
