# HCC1395 腫瘤演化樹：experiment workflow

更新日期：2026-08-23

狀態：**目前可執行的流程是 finite-K compound MCMC；所有結果在完整 gates 通過前都只能視為 diagnostic-only candidate output。**

本文件是 `arch.md` 四個可替換模組之上的編排與稽核契約。它定義資料如何交給模型、如何呼叫推理 backend、何時建立 holdout、哪些檢查算通過，以及失敗時要留下什麼紀錄。它不重新定義 `data.md`、`model.md`、`inference_algo.md` 或 `output.md` 的數學與欄位內容。

> Repo 中實際存在的推理文件名稱是 [`inference_algo.md`](inference_algo.md)；本文件不另建立 `inference.md`。

```yaml
workflow_id: hcc1395_tumor_tree_experiment
schema_version: hcc1395_tumor_tree_input/v4
active_backend_id: phylowgs_inspired_tssb_mcmc
active_backend_name: finite-K compound MCMC
candidate_backend_id: rao_blackwellized_annealed_smc
candidate_backend_status: specification_only_not_implemented_not_promoted
primary_purity: 0.99
```

## 1. 研究目的與固定邊界

研究目標是用 bulk SNV counts、ASCAT allele-specific CN 與 ASCAT tumor purity，重建 HCC1395 的 **candidate tumor evolutionary tree posterior**，並輸出 clone topology、CCF/`phi` 與 SNV-to-clone assignment。輸出不是 single-cell lineage truth，也不是已被獨立資料證明的唯一真樹。

目前固定設定：

| 項目 | 目前設定 | workflow 意義 |
|---|---|---|
| primary model | Model A bulk/CN/purity baseline | HP counts 暫不進 primary topology likelihood |
| executable backend | `phylowgs_inspired_tssb_mcmc` | 人類閱讀名稱為 finite-K compound MCMC |
| clone capacity | 主分析 `K=6`；敏感度 `K=4/8` | K 是模型容量，不是真實 clone 數 |
| ASCAT purity | `rho_ASCAT=0.99` | 主分析唯一正式 purity input |
| purity sensitivity | `0.97`、`0.95` | 固定 purity perturbation，不是新的 ASCAT 量測值 |
| candidate SMC | Rao–Blackwellized annealed SMC | 只有規格，現在不執行、不產生正式結果 |

主模型的 tree/root、no-loss inheritance、CN-constrained latent multiplicity 與 observation likelihood 以 [`model.md`](model.md) 為準；active MCMC 的 state transition 與輸出以 [`inference_algo.md`](inference_algo.md) 為準。

## 2. 四個模組如何交接

| 模組 | 輸入 | 交給下一層的內容 | 本模組不負責 |
|---|---|---|---|
| `data.md` | BAM、VCF、ASCAT 與 provenance | canonical input bundle、QA、manifest | 不建立 tree、不做 posterior inference |
| `model.md` | canonical SNV-level table | posterior target、likelihood、latent state 定義 | 不執行 MCMC、不管理 run |
| `inference_algo.md` | model posterior target、ChainConfig、holdout exclusions | posterior samples、tree/CCF/assignment/multiplicity artifacts | 不直接讀 raw BAM/VCF、不修改 model |
| `output.md` | inference summary | 人類可讀的 topology、CCF、SNV assignment 表示 | 不補造 CNA event、不宣稱 biological truth |
| `experiment_workflow.md` | 上述模組的契約 | stage 順序、holdout、diagnostics、gates、provenance | 不取代任何模組的定義 |

```text
raw sources
    ↓
derived builder artifacts
    ↓
canonical input bundle
    ↓
Model A posterior target
    ↓
active finite-K compound MCMC
    ↓
posterior artifacts
    ↓
workflow diagnostics / gates / publication
```

`experiment_workflow` 是跨模組的 orchestrator，不是第五個 likelihood module。

## 3. 原始資料到 canonical input bundle

### 3.1 上游來源

`data.md` 定義的來源包括：

- tumor BAM 與 somatic SNV VCF：建立 bulk REF/ALT counts。
- phase-tagged tumor BAM：提供 HP/PS provenance 與 HP-tagged read counts。
- ASCAT segment output：提供每個 SNV 所在位置的 `major_cn`、`minor_cn`、`total_cn`。
- ASCAT purity output：提供主分析 `rho_ASCAT=0.99`。
- reference FASTA、normal BAM、phased germline VCF：保存座標、germline 與 CN 分析背景。

目前指定的 phase-tagged tumor BAM 是：

```text
/bip8_disk/boyu114/longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam
/bip8_disk/boyu114/longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam.bai
```

不使用 `hcc1395_new_split_tagging.bam`。只要 tagged BAM 或其他 source 改變，就必須重建 derived counts；不能只修改 manifest 的路徑。

LongPhase-S DNA fraction `0.958936` 只保留在歷史 provenance，不是目前模型輸入。

### 3.2 建置順序

```text
upstream BAM / VCF / ASCAT
          ↓
snv_bulk_counts.tsv.gz
snv_hp_counts.tsv.gz
snv_hp_qc.tsv.gz
site_cnv_qc.tsv.gz
          ↓
likelihood_input.tsv.gz
          ↓
input_qa.json + manifest.json
```

`likelihood_input.tsv.gz` 是 model 與 inference backend 之間的固定資料介面。每列是一個 SNV，schema 是 `hcc1395_tumor_tree_input/v4`。canonical bundle 不包含 `multiplicity_candidates`、`multiplicity_prior` 或 `multiplicity_posteriors`。

## 4. Canonical input QA

這一階段只回答一件事：**這份資料能不能安全交給 Model A 與 C++ active backend？**

### 4.1 欄位分層

| 類別 | 欄位／資料 | 目前用途 |
|---|---|---|
| Model A likelihood-active | `ref_reads`、`alt_reads`、`total_reads`、`major_cn`、`minor_cn`、`total_cn`、`rho_ASCAT` | bulk emission 與 purity/CN context |
| Schema-required supplementary | `hp1_1_ref`、`hp1_1_alt`、`hp2_1_ref`、`hp2_1_alt` | schema、count QC、provenance、holdout 與未來 Model B；目前不進 Model A scorer |
| Eligibility | `model_include`、`model_status` | fail-closed site selection |
| Workflow metadata | PS audit、holdout metadata、simulation manifest | 前置條件與 predictive evaluation；不是 model parameter |
| Model-owned latent | multiplicity、`T`、`z`、`eta`、`phi`/CCF | 由 model/inference 內部處理或推導，不是 table 欄位 |

HP 欄位是 canonical schema 的 required columns，但「存在於表格」不代表「進入 Model A likelihood」。builder 先對完整 HP domain 做 conservation；C++ loader 驗證表內四個 HP 欄位格式與不超過 bulk counts；Model A scorer 不把 HP counts 當成第二批獨立 reads。

### 4.2 必須通過的檢查

- required columns 完整、`mutation_id` 唯一、座標與 REF/ALT 可追溯。
- `total_reads = ref_reads + alt_reads`。
- builder 的完整 HP categories conservation 通過；四個 canonical HP fields 是 bulk counts 的子集合。
- `major_cn >= minor_cn >= 0`，且 `total_cn = major_cn + minor_cn`。
- table 與 ASCAT purity source 的 `rho_ASCAT` 一致；primary table 為 `0.99`。
- 只有 `model_include=yes` 且 `model_status=eligible` 的 rows 進入該次 fitted Site collection。
- eligible site 的 `total_cn > 0`，且 C++ loader 能由 major/minor CN 建立有限、非空、正規化的 multiplicity support。
- 不接受舊 purity/multiplicity 介面：`tumor_dna_fraction`、`multiplicity_candidates`、`multiplicity_prior`、`multiplicity_posteriors`。
- 舊的 `bulk_ref`、`bulk_alt`、`bulk_depth` 不符合 v4 required schema；必須使用 `ref_reads`、`alt_reads`、`total_reads`。

Multiplicity 在這一步只確認「CN 是否足以讓 loader 建立候選 support」。真正的 posterior responsibility 在每個 tree/clone state 的 Model A emission 中計算，規則詳見 [`model.md`](model.md)。

QA 失敗時，workflow 必須停止，不得 fallback 到舊 table、`CN=2` 或固定 `multiplicity=1`。

## 5. PS、前置條件與 grouped holdout

PS 的作用是上游 phase provenance：同一 PS block 內協助維持 HP label 一致，進而產生 HP counts。PS 不是 clone label、topology edge、MCMC state，也不直接進 Model A likelihood。跨 PS block 不假設 HP1/HP2 方向全球一致。

正式 holdout 只由 workflow metadata 分組，不由 HP count 欄位分組：

| holdout | 分組規則 | 用途 |
|---|---|---|
| `ps` | 同一 chromosome + PS block；缺少 PS 時使用該 SNV 的 singleton block | 保留 phase block 的完整性 |
| `chromosome` | chromosome | 檢查跨染色體泛化 |
| `ascat_segment` | ASCAT segment identity | 檢查 CN context 的泛化 |

holdout metadata 必須包含 `mutation_id`、`chrom`、`ps`，以及 `ascat_segment_id` 或 segment start/end；其 mutation IDs 必須與 canonical eligible IDs 完全一致。被該 chain holdout 的 site 不進 fitted Site collection，只用於 predictive evaluation，不要求該 chain 產生 clone assignment 或 multiplicity posterior。

正式 prerequisites 的輸出與責任：

```text
prerequisites.json
holdouts/{ps,chromosome,ascat_segment}/
  holdout_site_ids.txt
  train_site_ids.txt
  manifest.json
```

PS audit manifest 必須已通過且 `discordance_fraction <= 0.01`。目前 workflow 驗證 manifest 的 pass 狀態、discordance 與 manifest hash；原始 BAM/VCF lineage hash 由上游 audit/provenance 保存，不由這個 validation 函式重新讀 BAM。

正式模式也要求 synthetic-recovery manifest 宣告 `passed=true`。目前 workflow 驗證這個外部 receipt，不會在此步驟重新執行完整 simulation recovery。

## 6. 目前可執行的 inference backend

### 6.1 Backend identity

目前 CLI、registry 與 C++ adapter 接受的 executable machine ID 是：

```text
phylowgs_inspired_tssb_mcmc
```

人類閱讀名稱是 **finite-K compound MCMC**。它的 compound sweep、`T`/`z`/`eta` state、topology/root 規則、CN-constrained latent multiplicity marginalization 與輸出見 [`inference_algo.md`](inference_algo.md)。多條 chain 是 workflow 的 convergence wrapper，不是另一種 model。

`inference_algo.md` 的 YAML 同時保存 inference family 與人類閱讀用的 active label；設定檔與 run manifest 必須使用上面的 executable ID，不得把 descriptive label 當成另一個 backend。

Model A scorer 使用 bulk counts、ASCAT CN、固定 purity 與內部 multiplicity；HP/PS 不乘入 primary topology likelihood。assignment 的 site score 必須使用已對 multiplicity 邊際化的 site emission，不能只使用未加總的單一 `m` likelihood。

### 6.2 Chain input

每條 C++ chain 讀取：

- validated `likelihood_input.tsv.gz`。
- `ChainConfig`：seed、K、iterations、burn-in、thin、`rho_ASCAT`、checkpoint interval。
- 該 holdout 的 exclusion IDs。

正式 active backend 不直接讀 BAM、VCF、ASCAT raw output 或 PS 欄位。

### 6.3 Chain output

每條 chain 的必要 output 是：

```text
samples.jsonl.gz
multiplicity_posterior.tsv.gz
posterior_summary.tsv.gz
topology_summary.tsv
diagnostics.json
representative_tree.json
checkpoint.json.gz
chain_complete.json
```

其中：

- `samples.jsonl.gz` 是 retained MCMC draws。
- `multiplicity_posterior.tsv.gz` 是模型輸出的 per-SNV multiplicity posterior，不是 input。
- `posterior_summary.tsv.gz` 是 clone CCF/`phi` median 與 95% credible interval。
- `topology_summary.tsv` 是 clone-label canonicalization 後的 topology/edge support。
- `representative_tree.json` 是該 chain 的代表 topology 與 assignment summary。
- `diagnostics.json`、`checkpoint.json.gz`、`chain_complete.json` 是計算與稽核 artifacts。

`output.md` 的 normal cells → tumor founder → C1/C2/C3 圖示是輸出格式示意；實際值必須以通過 gates 的 run artifacts 為準。

目前 wrapper 沒有建立「通過 holdout 後的 full-data final fit」，也沒有建立跨 holdout/chain 的 run-level aggregate tree。因而：

- 每個 `representative_tree.json` 只代表一個 cell、holdout 與 chain。
- 目前沒有一個可被 workflow 自動指定為唯一正式研究樹的檔案。
- holdout 結果是 predictive evaluation artifacts，不應直接當成 full-data tumor tree。
- 未來若要發布單一 candidate tree，必須另加 full-data fit、跨 chain aggregation 與明確的 selection receipt；在此之前，`output.md` 只能作格式說明。

## 7. Staged experiment matrix

執行採 dependency-ordered 與 early-stop：前一階段失敗，就不啟動後續昂貴階段。

### 7.1 Smoke

```text
fixture: hcc1395_tp20_v1
sites: 20
eligible: 16
excluded: 2 CN-zero + 2 unmapped-segment
K: 6
rho_ASCAT: 0.99
chains: 2
iterations: 20
burnin: 5
```

Smoke 只驗證 loader、schema、CN/multiplicity 建立、短鏈 I/O、artifact completeness 與錯誤回報；不判定 convergence、topology recovery 或 HCC1395 生物學結果。

### 7.2 Pilot

```text
K: 4, 6, 8
rho_ASCAT: 0.99
independent chains per K: 4
iterations: 300
burnin: 100
```

Pilot 用來估計執行成本、觀察 proposal behavior、確認不同 chain 能產生可比較的 summaries。`R-hat <= 1.10` 只是 pilot report signal，不是 formal pass。

### 7.3 Formal main

主分析先固定：

```text
K: 6
rho_ASCAT: 0.99
independent chains: 4
iterations: 1500
burnin: 1000
thin: 1
retained draws: at least 500 per chain
```

每個正式 cell 執行 `ps`、`chromosome`、`ascat_segment` 三種 strict grouped holdout。任何一種 holdout gate 失敗，該 cell 失敗，後續 sensitivity 不執行。

### 7.4 Formal sensitivity

只有 formal main 所有 gates 通過後，才執行：

```text
K sensitivity: 4, 8 at rho_ASCAT=0.99
fixed-purity sensitivity perturbation: 0.97, 0.95 at K=6
```

`0.97`、`0.95` 是固定情境的 robustness test。每個 purity 情境會建立自己的 `input_sensitivity/rho_*` table、manifest、hash 與 output cell；不能把它們寫回主分析的 ASCAT purity，也不能稱為新的 ASCAT output。

### 7.5 ESS 不足與 resume

目前 C++ checkpoint 是 audit/state snapshot，`--resume` 會 fail closed；尚未支援 sampler state restore。因而：

- 已完成 chain/cell 的 workflow resume 只能重新讀取完整且 hash/config 相符的 artifacts。
- 未完成 chain 不能從 checkpoint 接續。
- ESS 不足時，不能只修改 checkpoint 的 iterations；必須用更高 iterations 建立新的 immutable run/output directory。
- candidate SMC 的 checkpoint/resume round-trip 是未來 promotion gate，不適用於目前 MCMC。

## 8. Gates 與結果狀態

### 8.1 Gate 分層

| Gate 層 | 目前檢查內容 | 由誰執行 |
|---|---|---|
| input gate | schema、site key、counts、HP conservation、CN、purity、eligibility、forbidden columns | builder/QA + C++ loader |
| prerequisite gate | PS audit、simulation manifest、holdout metadata 與 hash | Python workflow；部分 receipt 由外部流程產生 |
| runtime gate | binary、chain artifacts、`chain_complete.json`、diagnostics 可讀 | C++ adapter + workflow |
| convergence gate | rank-normalized R-hat、bulk ESS、tail ESS | workflow；只對 label-invariant CCF/`phi` ranks |
| stability gate | assignment agreement、canonical edge-support difference | workflow diagnostics |
| predictive gate | holdout coverage、minimum predictive log score | workflow diagnostics |
| publication gate | 所有 requested cells 通過、manifest/inventory 可寫出 | workflow |

目前 formal gate 的數值下限是：

```text
max rank-normalized R-hat < 1.01
bulk ESS total >= 400
tail ESS total >= 400
assignment agreement >= 0.90
max edge-support difference <= 0.10
holdout coverage in [0.85, 0.95]
minimum predictive log score >= config threshold
```

R-hat/ESS 不直接證明離散 topology 已收斂；topology 由 canonical edge support，SNV assignment 由 assignment agreement，holdout 由 predictive metrics 分別評估。

### 8.2 尚未接入目前 workflow 的檢查

下列項目在 model/inference 文件中是必要的研究檢查，但目前不能假設已由 wrapper 自動完成：

- 完整 prior predictive tree check。
- 完整 posterior predictive simulation 與 model/config/hash 對照。
- synthetic manifest 之外的 simulation recovery 重算。
- C++ MCMC checkpoint restore round-trip。
- Candidate SMC 的 particle diversity、annealing、rejuvenation 與 weighted-particle diagnostics。
- CNV event → tree node、SNV-CNV timing 或 single-cell lineage validation。

若只有外部 manifest 宣告通過，workflow 只能記錄該 receipt；不能描述成 wrapper 重新驗證過全部數值。

### 8.3 `_SUCCESS`、`_FAILED` 與 diagnostic-only

- `_SUCCESS`：本次 workflow 的程式執行、已接入的 gates 與 artifacts 發布成功；不代表 biological truth。
- `_FAILED`：輸入、前置條件、chain、holdout gate 或 publication 失敗；該 run 不得當成正式研究結果。
- `diagnostic-only`：目前 model/inference/input/gates 尚未全部完成時，所有 output 的研究解讀狀態。
- `candidate-not-converged`：推理有產物，但正式 convergence/stability/predictive gate 未通過。
- `candidate-passing-gates`：已接入的 computational gates 通過，仍只能稱 candidate tree posterior，不能稱 single-cell truth。

目前 `status.json` 的機器狀態仍以 `running`、`success`、`failed` 為主；上述 result interpretation 是研究判讀層，不應與執行成功混為一談。

## 9. Stage artifacts 與錯誤定位

### 9.1 Stage 對照表

| stage | 主要輸出 | 失敗時看哪裡 |
|---|---|---|
| `initialization` | `command.json`、`status.json`、`execution_trace.jsonl`、`run.lock` | command/config、Git state |
| `input_build` | `input/` 下的 canonical table、manifest、QA | builder log、source path/hash |
| `input_resolution` | 外部指定的 table 與 validation manifest 記錄 | table/manifest path 與 hash |
| `input_validation` | `input_validation.json`、`input_sensitivity/rho_*` | schema、counts、CN、purity |
| `prerequisites` | `prerequisites.json`、`holdouts/*` | PS audit、simulation receipt、metadata |
| `smoke` / `pilot` / `formal_*` | cell `summary.json`、每個 holdout 的 `diagnostics.json`、每條 chain artifacts | chain log、diagnostics、gate checks |
| `publication` | experiment `manifest.json`、`artifact_inventory.json`、`_SUCCESS` | manifest/inventory/atomic publish |

每個 run 至少保存：

```text
command.json 或 resume_command.NNN.json
command_ledger.json
execution_trace.jsonl
status.json
logs/workflow_error.log（失敗時）
input_validation.json
prerequisites.json
```

`execution_trace.jsonl` 至少記錄：

```text
workflow_started
stage_started / stage_completed
cell_started / cell_completed
holdout_started / holdout_completed
chain_started / chain_completed / chain_failed
holdout_failed
workflow_failed / workflow_completed
```

chain event 必須包含 `stage`、`cell`、`K`、`rho_ASCAT`、`holdout`、`chain`、`seed` 與 `iterations`。因此可區分：

| 錯誤類型 | 定位方式 |
|---|---|
| source/path/build | `input_build` 或 `input_resolution` |
| schema/count/CN/purity | `input_validation.json` |
| PS/simulation/holdout | `prerequisites.json` 與對應 manifest |
| C++/memory/output artifact | `chain_failed`、chain `diagnostics.json`、`workflow_error.log` |
| R-hat/ESS/assignment/edge/predictive | 該 holdout 的 workflow `diagnostics.json` gate checks |
| publication | `status.json.failed_stage=publication` 與 traceback |

目前失敗路徑一定保存 `status.json`、`execution_trace.jsonl`、`logs/workflow_error.log` 與 `_FAILED`；`artifact_inventory.json` 目前是在成功 publication 階段建立，不能假設每個失敗 run 都有完整 inventory。

### 9.2 最小診斷順序

```bash
RUN=output/tumor_tree_pipeline/<run_id>
for FILE in \
  "$RUN/status.json" \
  "$RUN/execution_trace.jsonl" \
  "$RUN/logs/workflow_error.log" \
  "$RUN/input_validation.json" \
  "$RUN/prerequisites.json"; do
  if test -f "$FILE"; then
    echo "--- $FILE"
    if test "$FILE" = "$RUN/execution_trace.jsonl"; then tail -n 20 "$FILE"; else sed -n '1,120p' "$FILE"; fi
  else
    echo "--- $FILE (not created before the failure stage)"
  fi
done
```

先用 `status.json.failed_stage` 與 `failed_scope` 定位，再查看該 stage 的最後一個失敗事件。不要把 `_FAILED` 當成可發表的 tree，也不要只看最後一個 `log_posterior` 就判定模型成功。

## 10. Run directory 與 provenance

目前 wrapper 的 run layout 大致為：

```text
output/tumor_tree_pipeline/<run_id>/
├── command.json
├── command_ledger.json
├── execution_trace.jsonl
├── status.json
├── manifest.json                 # publication success 時
├── input_validation.json
├── prerequisites.json
├── input/
├── input_sensitivity/rho_*/
├── holdouts/{ps,chromosome,ascat_segment}/
│   ├── holdout_site_ids.txt
│   ├── train_site_ids.txt
│   └── manifest.json
├── runs/<cell_id>/
│   ├── summary.json
│   └── {none,ps,chromosome,ascat_segment}/
│       ├── diagnostics.json
│       └── chain_01/
│           ├── samples.jsonl.gz
│           ├── multiplicity_posterior.tsv.gz
│           ├── posterior_summary.tsv.gz
│           ├── topology_summary.tsv
│           ├── diagnostics.json
│           ├── representative_tree.json
│           ├── checkpoint.json.gz
│           └── chain_complete.json
├── logs/workflow_error.log       # failure 時
├── artifact_inventory.json       # success publication 時
└── _SUCCESS 或 _FAILED
```

每個 run 必須能追溯：

- exact command、cwd、Git SHA 與 worktree state。
- workflow config、schema version、model/inference algorithm identity。
- 所有 input path、source metadata/hash、canonical table hash。
- K、purity、seed、holdout IDs、iterations、burn-in、thin。
- external PS/simulation receipt 的 path/hash。

Git 保存程式、tests、configs、small fixtures、manifest 與小型 diagnostics；大型 BAM、完整 samples 與可重建的大型 intermediate table 不放入 Git。

## 11. 正式執行命令

`formal.example.json` 是 template config，內部的 `/absolute/path/to/...` 必須先替換成真實 canonical table、validation manifest、holdout metadata、PS audit manifest 與 synthetic-recovery manifest；它不是拿來直接執行的現成設定。

先檢查 dependency-ordered matrix：

```bash
python3 -m tumor_tree_pipeline plan \
  --config tumor_tree_pipeline/configs/formal.example.json
```

再執行 immutable、fail-closed workflow：

```bash
python3 -m tumor_tree_pipeline run \
  --config tumor_tree_pipeline/configs/formal.example.json
```

正式 `formal`/`all` 模式要求 clean Git worktree、外部 prerequisites、明確的 predictive log-score threshold，以及至少四條獨立 chains。任何 failure 都回傳 non-zero exit，不建立 `_SUCCESS`。

## 12. Candidate SMC 的位置

`inference_algo.md` 定義的：

```text
Rao–Blackwellized annealed Sequential Monte Carlo
algorithm_id: rao_blackwellized_annealed_smc
status: specification_only_not_implemented_not_promoted
```

目前它：

- 不在 registry、CLI 或 Python workflow 的可選 backend 中。
- 不在 smoke、pilot、formal 或 sensitivity matrix 中。
- 不共用目前 MCMC 的 chain R-hat/ESS 判讀。
- 不得把 weighted particle output 改名成 MCMC chain draws。

未來要加入 workflow，至少要先完成獨立 backend、adapter、particle/annealing diagnostics、checkpoint round-trip、synthetic recovery、holdout predictive checks，以及與 active MCMC 的比較 gate。完成前，本文件只把 SMC 當作可替換的候選演算法規格。

## 13. 完成定義

一次可解釋的 formal candidate run 必須同時具備：

1. v4 canonical input table、QA、manifest 與 source provenance。
2. 主分析 `rho_ASCAT=0.99`，且沒有舊 purity/multiplicity interface。
3. active MCMC backend identity、K、seed、chain 與 holdout 可追溯。
4. 每條 chain 的必要 output artifacts 與 `chain_complete.json`。
5. workflow 的 convergence、assignment、edge、holdout predictive 與 log-score gate receipt。
6. run-level status、execution trace、command ledger 與成功/失敗 marker。
7. 清楚區分 holdout evaluation artifacts 與 full-data final fit；目前後者尚未由 wrapper 產生。
8. 結果標記為 candidate posterior；不宣稱 single-cell lineage truth 或 CNV event branch proof。

若任何一項缺少，該 run 只能作 diagnostic/provenance。即使 computational gates 通過，在 full-data aggregation contract 完成前，也不能指定單一檔案代表目前研究的正式候選腫瘤演化樹。

## 14. 相關文件

- 資料輸入與 canonical schema：[`data.md`](data.md)
- Model A posterior、CCF/`phi` 與 latent multiplicity：[`model.md`](model.md)
- Active MCMC 與 candidate SMC specification：[`inference_algo.md`](inference_algo.md)
- 人類可讀的 topology、CCF 與 SNV assignment：[`output.md`](output.md)
- 四模組整體連接：[`arch.md`](arch.md)
