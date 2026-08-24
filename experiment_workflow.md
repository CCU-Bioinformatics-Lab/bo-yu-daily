# HCC1395 tumor-tree agent experiment workflow

更新日期：2026-08-24

本文件把 [`arch.md`](arch.md) 的五個可替換模組接成一條可執行、可追蹤且
fail-closed 的實驗流程。正式推理 backend 是 C++17
`rao_blackwellized_annealed_smc`；Python 負責建表、編排、驗收與留下紀錄。

```text
data input → model ↔ inference_algo → output → validation
```

## 1. 目前模組實作

| 模組 | 規格文件 | 目前實作或資料 | 2026-08-24 狀態 |
|---|---|---|---|
| data input | [`data.md`](data.md) | `tumor_tree_pipeline/input_table.py`、`contracts.py`、目前 v4 input bundle | **可用**；input QA PASS |
| model | [`model.md`](model.md) | `tumor_tree_pipeline/model.py`、`inference/src/model.cpp` | **可用**；目前 working tree 的 Python/C++ tests PASS |
| inference_algo | [`inference_algo.md`](inference_algo.md) | `inference/src/algorithm.cpp`、`cpp_backend.py` | **可用**；目前 working tree 的 C++ annealed SMC smoke PASS |
| output | [`output.md`](output.md) | C++ repeat artifacts、workflow summary/inventory | **可產生**；目前只有 fixture smoke，不是 HCC1395 正式結果 |
| validation | [`validation.md`](validation.md) | 尚無獨立 runner；目前 output 已提供 diagnostics 供未來讀取 | **尚未實作** |

`experiment_workflow.md` 是上述模組外的 agent 編排層，不改寫 model，也不把
validation 混入 likelihood。

## 2. 已準備的資料

### HCC1395 active input sources

```text
prepared counts
output/tumor_tree_pipeline/derived_counts_20260823_old_tagging_v4/

site-CNV table
output/tumor_tree_pipeline/prerequisites_20260823_old_tagging/site_cnv_qc.tsv.gz

current readable input bundle
output/tumor_tree_pipeline/input_20260823_old_tagging_v4/
```

目前 bundle contract：

- schema：`hcc1395_tumor_tree_input/v4`；
- `rho_ASCAT=0.99`；
- 30,490 列，其中 30,006 個 eligible SNV、399 個 CN-zero、85 個 unmapped；
- `input_qa.json` 為 PASS；
- inference 不直接讀 BAM、VCF 或 ASCAT 原始檔。

既有 bundle 的內容可讀，但 `contracts.py` 已更新，舊 manifest 所記錄的 contract
hash 不再是最新值。因此 agent 執行 pilot 時必須透過 `build_inputs` 從 prepared
counts 重建當次 run 的 input bundle，不能直接宣稱舊 manifest 已鎖定最新程式。

限制：prepared counts 的來源 lineage 有記錄，但「raw BAM/VCF → v4 counts」仍缺少
一份完整 command receipt；這不阻擋 fixture smoke，但會限制正式 HCC1395 run 的
raw-data reproducibility claim。

## 3. 已準備的執行設定

| 設定檔 | 用途 | 資料 | 可否執行 |
|---|---|---|---|
| `configs/smoke.active.json` | 快速檢查整條介面 | checked-in 20-site fixture | **可以** |
| `configs/pilot.active.json` | HCC1395 K=4/6/8 小型診斷 | active prepared counts，run-time 重建 v4 bundle | **可以，但尚未執行** |
| `configs/formal_20260820.json` | 既有 formal matrix | HCC1395 v4 bundle + grouped holdout | **阻擋** |

Formal 被阻擋的原因不是 C++ 無法執行，而是目前
`simulation_20260820/synthetic_recovery_gate.json` 驗證的是退役的 input v2。workflow
現在會要求 synthetic gate 同時符合：

```text
schema = synthetic_recovery_gate/v1
input_schema = hcc1395_tumor_tree_input/v4
inference_algorithm = rao_blackwellized_annealed_smc
passed = true
```

在補上新的 synthetic-data generator／runner，並產生 v4 + C++ SMC recovery gate
前，agent 不得啟動 formal。目前 repo 尚無可直接產生這個新 gate 的正式命令。
此外 formal 禁止 dirty worktree；上述 gate 完成後仍須先 commit，使 provenance
可被 Git SHA 鎖定。

## 4. Agent 自動化主流程

### A. 每次開始先盤點

```bash
git status --short
python3 -m tumor_tree_pipeline plan \
  --config tumor_tree_pipeline/configs/smoke.active.json
python3 -m tumor_tree_pipeline plan \
  --config tumor_tree_pipeline/configs/pilot.active.json
```

Agent 必須記錄 Git SHA、dirty worktree、設定檔、input path、schema、purity、K、seed
與預計輸出目錄。`plan` 只展開 matrix，不代表實驗成功。

### B. 建置與 contract tests

```bash
cmake --build inference/build --parallel 4
ctest --test-dir inference/build --output-on-failure
inference/tests/run_contract_tests.sh inference/build/tumor_tree_inference
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tumor_tree_pipeline/tests -p 'test_*.py'
```

任一測試失敗就停止，不得執行 pilot 或 formal。

### C. Fixture smoke

```bash
TUMOR_TREE_INFERENCE_THREADS=4 PYTHONDONTWRITEBYTECODE=1 \
python3 -m tumor_tree_pipeline run \
  --config tumor_tree_pipeline/configs/smoke.active.json
```

Agent 只在以下條件全部成立時標記 smoke 成功：

- run root 有 `_SUCCESS` 且沒有 `_FAILED`；
- `artifact_inventory.json` 與 manifest 完整；
- 每個 repeat 有 `smc_complete.json`；
- diagnostics 的 algorithm、particle semantics、`final_beta=1` 與 tree contract 正確。

2026-08-24 已通過的 smoke receipt：

```text
output/tumor_tree_pipeline/
20260824T075036Z_b35aa42d6d5a_rho0p99_K6_seed20260824/
```

這次 run 使用包含未提交修正的 working tree；它證明當下 20-site fixture 的端到端
介面可運作，但不是由單一 Git commit 完整鎖定的 release receipt，也不是 HCC1395
tumor tree 結果。程式 commit 後應再跑一次，才有 immutable SHA receipt。

### D. HCC1395 pilot

```bash
TUMOR_TREE_INFERENCE_THREADS=4 PYTHONDONTWRITEBYTECODE=1 \
python3 -m tumor_tree_pipeline run \
  --config tumor_tree_pipeline/configs/pilot.active.json
```

Pilot 會先從 active prepared counts 重建 input，再依序跑 `K=4,6,8`。Agent 應檢查：

- 建表 QA 與 schema/hash/purity；
- beta 是否到 1；
- conditional ESS、weighted particle ESS、resampling；
- particle/ancestor diversity；
- eta 與 topology change；
- repeats 的 CCF、assignment 與 edge support 是否穩定；
- 完整 artifact inventory；若要量測 elapsed time／peak memory，需另以資源監測工具
  包住命令，目前 workflow 尚未把這兩項寫進正式 artifact。

Pilot 失敗時保留 `_FAILED`、`workflow_error.log`、`execution_trace.jsonl` 和已完成的
repeat；先診斷，不把 partial output 當正式候選樹。

### E. Formal 解鎖後才執行

先建立並驗收當前 v4 + C++ SMC synthetic recovery gate，再確認 Git clean，之後才
允許 formal matrix：

```text
K=6, rho=0.99
K=4, rho=0.99
K=8, rho=0.99
K=6, rho=0.97
K=6, rho=0.95
```

既有 formal 設定是 5 cells × 3 grouped holdouts × 4 repeats，共 60 次 C++ SMC
repeat。這是長時間實驗，agent 必須先根據 pilot 另行量測並估算時間與記憶體。
`formal_20260820.json` 目前只能用於 `plan`；新 gate 產生後必須建立更新的 active
formal config，通過 preflight 才可執行 `run`。

## 5. Model 與 inference 如何交接

Data builder 交付每個 SNV 一列的 v4 table。Model 使用 REF/ALT read counts、ASCAT
copy number 與 purity 評分候選 tree state。C++ SMC particle 明確保存：

- tree topology；
- `eta`（clone-local mass）。

`phi/CCF` 由 topology 與 eta 推導；SNV clone assignment 與 multiplicity 在 model
內邊際化，不是 data table 的外部欄位。HP counts 目前只載入並做守恆檢查，尚未
進入主要 likelihood。

## 6. 有效的 inference 參數

目前真正傳入 C++ 的主要參數是：

| 參數 | 意義 |
|---|---|
| `num_nodes` | 固定 K |
| `particles` | 每個獨立 SMC population 的 particle 數 |
| `max_annealing_stages` | beta 逐步加入資料評分的最大階段數 |
| `conditional_ess_target` | 選擇下一個 beta 的 particle 穩定度目標 |
| `resample_ess_threshold` | 何時 resample |
| `min_rejuvenation_sweeps` | 每個 stage 固定執行的 rejuvenation sweeps |
| `seed` / repeats | 可重現的獨立 population |
| `main_purity` | ASCAT purity；primary 為 0.99 |
| `TUMOR_TREE_INFERENCE_THREADS` | 傳給 C++ 的 thread 設定；目前 active path 尚未實際平行化 |

目前 Python workflow 依序執行 repeats，C++ active likelihood 也仍是逐 site 評分；
所以目前 threads 不會帶來已驗證的 repeat-level 或 site-level 加速。舊 config 裡的
`eta_rw_scale`、`topology_global_probability`、
`max_rejuvenation_sweeps` 與週期性 `checkpoint_every` 並未控制目前 C++ kernel，
agent 不得拿它們解釋實驗結果。

## 7. 每個 SMC repeat 的必要輸出

```text
samples.jsonl.gz
particle_history.jsonl.gz
multiplicity_posterior.tsv.gz
posterior_summary.tsv.gz
topology_summary.tsv
representative_tree.json
diagnostics.json
checkpoint.json.gz
smc_complete.json
```

`samples.jsonl.gz` 是 terminal resampling 後的等權重 SMC particles，不是 MCMC
chain draws；annealing 過程的非等權重狀態記錄在 diagnostics/history。workflow 會
產生 run-level summary、artifact inventory、manifest、command ledger 與 execution
trace。指定既有 `run_id` 並使用 `--resume` 時可重用已完成 repeat；目前 checkpoint
只保存終點，不能從中途 stage 恢復。

## 8. Validation 的實作邊界

目前下列項目屬於 inference/workflow diagnostics，不是獨立 validation 模組：

- input contract 與 provenance；
- beta、ESS、particle/ancestor diversity 與 rejuvenation；
- repeat stability；
- grouped holdout coverage/log score；
- artifacts 是否完整。

以下仍是 [`validation.md`](validation.md) 的規格，尚無完整 runner：

- `validation_report.json`；
- `relationship_posterior.tsv`；
- `predictive_residuals.tsv`；
- 獨立 V-measure、ancestor-descendant F1；
- CNV/LOH/driver evidence mapping 與 claim grading。

因此 `_SUCCESS` 只代表該 mode 自己的 workflow 條件完成：smoke 是介面完成，pilot
是診斷執行完成，只有 formal 才會套用 formal gates。它不等於獨立 validation PASS，
也不能單靠它聲稱 high-confidence candidate branching tree topology。

## 9. Fail-closed、權限與停止條件

任何建表、repeat、holdout 或 gate 失敗時：

1. 寫入錯誤、command ledger 與 execution trace；
2. 建立 `_FAILED`，不建立 `_SUCCESS`；
3. formal matrix 停在第一個失敗 cell；
4. 保留 partial artifacts 供診斷。

成功時先完成 inventory、summary 與 provenance，再原子建立 `_SUCCESS` publication
marker；其後 execution trace 仍可追加完成事件。
workflow 建立的目錄權限為 `2775`、一般檔案為 `664`；C++ executable 為 `775`。

目前 agent 的停止條件：

- smoke：已完成；
- pilot：設定與資料已準備，尚未執行；
- formal：缺少當前 v4 + SMC synthetic recovery gate，必須停止；
- validated HCC1395 result：尚不存在，不得引用舊 run 或 fixture smoke 代替。
