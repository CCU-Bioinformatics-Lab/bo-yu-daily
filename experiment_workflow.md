# HCC1395 tumor-tree experiment workflow

本文件是目前 `arch.md` 四模組架構下的可執行實驗流程：

```text
data input → model → output
                   ↓
            inference_algo
                   │
                   └──→ model
```

目前正式 inference backend 固定為：

```yaml
inference_algorithm: rao_blackwellized_annealed_smc
backend: C++17
primary_rho_ASCAT: 0.99
primary_K: 6
K_sensitivity: [4, 8]
purity_sensitivity: [0.97, 0.95]
```

## 1. 每個模組的責任

| 模組 | 讀取 | 產生 |
|---|---|---|
| `data.md` / data builder | BAM、VCF、ASCAT CN/purity、phase-derived counts | validated `likelihood_input.tsv.gz` |
| `model.md` | canonical SNV-level table | tree、eta、phi/CCF 與 site likelihood target |
| `inference_algo.md` | model target + canonical table | SMC particles、topology、CCF、assignment、multiplicity posterior |
| `output.md` | inference artifacts | topology tree 與 CCF summary 的閱讀定義 |

## 2. Active input

正式流程使用：

```text
/bip8_disk/boyu114/main_work/output/tumor_tree_pipeline/input_20260823_old_tagging_v4/likelihood_input.tsv.gz
```

這張表必須是 `hcc1395_tumor_tree_input/v4`、`rho_ASCAT=0.99`、QA pass，且每列
代表一個 SNV。正式 inference 不直接讀取 BAM/VCF。

若由 raw data 重新建立 table，使用 `BuildInputs` 指定：

- canonical bulk / HP count directory；
- site-CNV QC table；
- ASCAT purity source，固定 primary value `0.99`。

builder 會產生 table、validation manifest 與 hash；workflow 會在 sampler 啟動前
再次檢查 schema、hash、purity、eligible IDs 與禁止舊欄位。

## 3. 執行階段

### Smoke

目的：確認 executable、schema、輸出 artifact、tree/root 規則、multiplicity
posterior 與 checkpoint 形式都能工作。它不代表正式結果通過。

```bash
python3 -m tumor_tree_pipeline.cli run \
  --config tumor_tree_pipeline/configs/smoke.example.json
```

### Pilot

使用 `K=4,6,8` 與較小 particle budget，確認執行成本、beta schedule、ESS、
resampling 與 rejuvenation 行為。Pilot 是診斷階段，不取代 formal gates。

```bash
python3 -m tumor_tree_pipeline.cli run \
  --config tumor_tree_pipeline/configs/pilot.example.json
```

### Formal

執行順序固定為：

```text
K=6, rho=0.99
   ↓ pass
K=4, rho=0.99 → K=8, rho=0.99
   ↓ pass
K=6, rho=0.97 → K=6, rho=0.95
```

每個 cell 使用多個獨立 SMC repeats；每個 repeat 使用不同 deterministic seed，
並產生自己的 particle artifacts。formal holdout 分成：

- PS grouped；
- chromosome grouped；
- ASCAT segment grouped。

```bash
python3 -m tumor_tree_pipeline.cli run \
  --config tumor_tree_pipeline/configs/formal.example.json
```

## 4. C++ SMC 介面

Python workflow 透過 `tumor_tree_pipeline/cpp_backend.py` 呼叫：

```bash
tumor_tree_inference run \
  --algorithm rao_blackwellized_annealed_smc \
  --input likelihood_input.tsv.gz \
  --outdir OUTPUT_DIR \
  --seed SEED \
  --num-nodes 6 \
  --annealing-stages 64 \
  --particles 1024 \
  --ess-threshold 0.5 \
  --purity 0.99 \
  --repeats 1 \
  --threads 1
```

`annealing-stages` 是 beta schedule 的最大階段數；`particles` 是每個 repeat 的
particle 數；`repeats` 是彼此獨立的 SMC population。這些名稱不代表保留 chain
draw 或 burn-in。

## 5. 一個 repeat 的輸出

每個 repeat 完成後必須存在：

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

`smc_complete.json` 是完成標記；缺少任何 artifact 時 workflow 會 fail closed。
`samples.jsonl.gz` 的每列必須標記 `sample_kind=smc_particle`，不能被解讀成時間
序列式 sample。

## 6. Gate 與錯誤處理

### Input gate

- schema 與 table hash 正確；
- `rho_ASCAT` 與 experiment cell 一致；
- `model_include=yes` 且 `model_status=eligible` 的 SNV IDs 與 holdout metadata
  完全一致；
- 不接受 `tumor_dna_fraction`、外部 multiplicity 欄位等舊 schema。

### SMC gate

- beta 到達 1；
- conditional / weighted particle ESS 不低於門檻；
- particle 與 ancestor diversity 足夠；
- CCF stability、SNV assignment agreement、edge support 差異通過；
- grouped holdout predictive coverage / score 通過。

### Fail-closed

任何 repeat、holdout 或 formal cell 失敗：

1. 寫入錯誤與 execution trace；
2. 建立 `_FAILED`，不建立 `_SUCCESS`；
3. formal matrix 停在第一個失敗 cell；
4. 不把 partial output 當成 tumor evolutionary tree 結果。

成功則先寫 artifact inventory、summary 與 provenance，最後才原子建立 `_SUCCESS`。
完成的 experiment directory 不可覆寫。

## 7. 目前可驗證的輸出

SMC 輸出可以回答：

- candidate tumor tree 的 root / clone edge topology；
- 每個 clone 的 CCF/phi summary；
- 每個 SNV 的 representative clone assignment；
- 模型內部 CN-aware multiplicity posterior；
- particle / repeat / holdout diagnostics。

它不會自動聲稱取得 ASCAT 未提供的 CNV cellular prevalence、CNV timing、唯一
真實 clone 數，或 single-cell level validation。

## 8. 可重跑條件與紀錄

每次 run 必須記錄：

- Git SHA 與 worktree 狀態；
- canonical table 與 manifest hash；
- SMC algorithm ID、K、purity、particles、annealing stages、seed；
- holdout kind、excluded IDs 與 hash；
- 每個 repeat 的 artifact manifest、diagnostics、failure trace。

只有在上面紀錄完整且所有 gate 通過後，才可把輸出交給 [`output.md`](output.md)
作為 candidate tree summary。
