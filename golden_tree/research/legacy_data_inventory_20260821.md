# Repo 舊資料與舊結果索引

更新日期：2026-08-21

## 目的與使用規則

本文件只做分類與狀態紀錄；不因索引本身自動刪除、搬移或覆寫檔案。目的是避免把歷史模型、舊輸入或失敗輸出誤當成目前 active pipeline 的上下文。已由使用者明確指定刪除的項目，會保留在本文件作為歷史紀錄並標示為「已刪除」。

目前 active baseline 以 `inference/` 的 C++17 `phylowgs_inspired_tssb_mcmc`、`tumor_tree_pipeline/` workflow、ASCAT `rho_ASCAT=0.99` 與 `hcc1395_tumor_tree_input/v2` canonical table 為準。

## 現況快照

- **目前程式與規格**：`inference/`、`tumor_tree_pipeline/`、`model.md`、`inference_algo.md`、`data.md` 與 `ascat_purity_experiment_workflow.md`。
- **目前可用輸入 receipt**：`output/tumor_tree_pipeline/input_20260820/`；schema v2，30,490 個 observed sites，其中 30,006 個 eligible，ASCAT `rho_ASCAT=0.99`。
- **目前 PS receipt**：`output/tumor_tree_pipeline/prerequisites_20260820/formal_ps_audit_manifest.json`，PS audit 通過；PS 只作 provenance、QC 與 grouped holdout，不是 likelihood 欄位。
- **目前 formal 結果**：只剩 `20260820T122332Z_afce5dea2c6e_...` 這個失敗診斷 run；沒有成功的 tumor-tree posterior 可引用。
- **本次清理**：三個舊／失敗 run、兩個重複 preflight 目錄、六個舊 blocker receipt，以及三個可重建快取已刪除；以下仍保留其歷史分類。

## A. 目前 active、不要歸入舊資料

| 路徑 | 身分 | 判定依據 |
|---|---|---|
| [`inference/`](../inference/) | active C++17 inference backend | AlgorithmRegistry、compound MCMC、canonical loader 與 contract tests |
| [`tumor_tree_pipeline/`](../tumor_tree_pipeline/) | active 建表與 workflow | 目前正式入口 `python3 -m tumor_tree_pipeline` |
| [`model.md`](../model.md) | active model specification | 定義 `T,z,eta`、ASCAT purity、HP counts、CN-only multiplicity prior |
| [`inference_algo.md`](../inference_algo.md) | active inference algorithm specification | 定義 `phylowgs_inspired_tssb_mcmc`、compound kernels、chain I/O、backend abstraction 與目前 `eta` correctness audit |
| [`data.md`](../data.md) | active data/provenance 文件，含歷史章節 | canonical input contract 與來源 hash；歷史段落需按章節閱讀 |
| [`ascat_purity_experiment_workflow.md`](../ascat_purity_experiment_workflow.md) | active formal workflow | 定義 smoke、pilot、formal、holdout 與 fail-closed 規則 |
| [`inference/README.md`](../inference/README.md) | active backend 說明 | 明確描述 assignment Gibbs、eta MH、subtree prune-and-regraft Gibbs |
| [`research/phylowgs_model_review.md`](phylowgs_model_review.md) | 方法背景 | PhyloWGS 參考與本 repo 有限 K 近似，不是舊實驗結果 |
| `output/tumor_tree_pipeline/input_20260820/manifest.json` | active generated input receipt | schema v2、30,490 observed sites、30,006 eligible、`rho_ASCAT=0.99`；明確禁止 `tumor_dna_fraction` 與 `multiplicity_posteriors` |
| `output/tumor_tree_pipeline/metadata_20260820/metadata_manifest.json` | active holdout metadata receipt | 30,006 rows；只供 grouped holdout，PS 不進 likelihood |
| `output/tumor_tree_pipeline/prerequisites_20260820/formal_ps_audit_manifest.json` | active PS provenance/QC receipt | 30,490 selected sites，audit `passed=true`；只描述 PS read audit，不是模型 likelihood |

## B. 高風險：舊內容仍在 repo，容易污染目前上下文

### B1. 根目錄 README（已同步更新）

[`README.md`](../README.md) 已改為連結分離後的 `model.md` 與 `inference_algo.md`，並將 active backend 標示為 finite-K compound MCMC；目前不再是 plain-MH stale blocker。

結論：它仍是 repo 入口文件；推理演算法的權威來源改為 [`inference_algo.md`](../inference_algo.md)，README 只作導覽。

### B2. 舊 Python plain-MH sampler

[`tumor_tree_pipeline/sampler.py`](../tumor_tree_pipeline/sampler.py) 開頭已標明是 legacy Python reference implementation，並且仍輸出 `single_chain_plain_metropolis_hastings`。目前 workflow 的正式 chain runner 不是它，而是 [`cpp_backend.py`](../tumor_tree_pipeline/cpp_backend.py)。

用途仍可保留：contract test、數值對照、歷史 baseline。使用模型或實驗上下文時，不可把它當成 active inference implementation。

### B3. 2026-08-19 舊 HTML

以下 HTML 仍描述 plain MH baseline：

- [`daily/20260819/20260819_hcc1395_inference_background.html`](../daily/20260819/20260819_hcc1395_inference_background.html)
- [`daily/20260819/20260819_hcc1395_tumor_tree_model_map.html`](../daily/20260819/20260819_hcc1395_tumor_tree_model_map.html)

它們是歷史視覺化／當日紀錄，不是目前模型說明。最新 daily 內容應以 [`daily/20260820/index.html`](../daily/20260820/index.html) 為準，但其中的實驗結果仍要以 formal output 的 `status.json` 與 `diagnostics.json` 為準。

### B4. 舊輸入欄位與舊 integrated table

`data.md`、`model.md` 與 workflow 文件仍保留對下列歷史內容的說明：

- `multiplicity_posteriors`
- `tumor_dna_fraction`
- 舊 `stage_06_likelihood_20260815_binomial/likelihood_input.tsv.gz`
- `output/longphase_clone/...`
- 舊 `multi_evol_tree/tools/` builder、validation、experiment loop、Stage 6 runner

目前本 repo 中 `tools/`、`output/longphase_clone/`、`longphase-clone.md`、`convergence_cleanup_20260816.md` 與 `cnv_tool_and_data.md` 都不存在；它們在本 repo 內是文件中的歷史路徑／交接引用，不是可直接執行或可直接載入的 active input。需要注意的是，現行 `input_20260820/manifest.json` 的 provenance 仍記錄 `/bip8_disk/boyu114/multi_evol_tree/output/longphase_clone/canonical_counts_20260814/` 下的 canonical bulk/HP counts；這是外部來源資料的 lineage，不等於本 repo 內仍存在舊的 `longphase_clone` 實驗結果。

目前 active input receipt 已確認：`rho_ASCAT` 是固定全域 likelihood input；multiplicity 使用 CN-derived `multiplicity_prior`；PS 不在模型 likelihood。`tumor_dna_fraction`、`multiplicity_posteriors` 與以 VAF 反推 multiplicity 的舊介面只屬歷史或禁止欄位，不可重新當成目前輸入。

舊 integrated table 曾使用 bulk counts 形成 multiplicity 權重，再把同一批 counts 用於 likelihood，可能重複使用觀測。因此只能作 schema／row-count 對照，不可作目前模型輸入。

## C. 舊結果與 generated artifacts

### C1. Formal run 時間線

以下表格記錄 `output/` 下的 formal run；其中第一至第三個目錄已刪除，只保留歷史索引，第四個仍存在並保留作 audit。它們都不是可直接引用的成功 tumor-tree result。

| run | Git SHA | algorithm | 狀態 | 可作什麼 |
|---|---|---|---|---|
| `20260820T065834Z_f4894377aea3_rho0p99-0p97-0p95_K6-4-8_seed20260820` | `f4894377aea3` | command 未記錄 algorithm 欄位 | **已刪除（2026-08-21）**；原先 `running`，沒有 `_SUCCESS`／`_FAILED` | 未完成／中斷的歷史 run；目前只保留本索引紀錄，不可引用 |
| `20260820T110728Z_fb4f01792d18_rho0p99-0p97-0p95_K6-4-8_seed20260820` | `fb4f01792d18` | `plain_metropolis_hastings` | **已刪除（2026-08-21）**；原先 `_FAILED` | 舊 plain-MH baseline；目前只保留本索引紀錄，不可引用 |
| `20260820T121546Z_9d103df6e932_rho0p99-0p97-0p95_K6-4-8_seed20260820` | `9d103df6e932` | `phylowgs_inspired_tssb_mcmc` | **已刪除（2026-08-21）**；原先 `phi_values` 浮點邊界錯誤 | 新 sampler 初次 pre-clamp 失敗記錄；目前只保留本索引紀錄 |
| `20260820T122332Z_afce5dea2c6e_rho0p99-0p97-0p95_K6-4-8_seed20260820` | `afce5dea2c6e` | `phylowgs_inspired_tssb_mcmc` | `_FAILED`，formal gate failed | 目前唯一保留的 formal diagnostic artifact；不是成功結果 |

最新 run 的 chain artifacts 已完成，但 convergence、ESS、assignment agreement、edge support 與 predictive gates 均未通過。不能把它的 representative tree 解讀成真實腫瘤演化樹。

### C2. 當日生成的 preflight／simulation，不是 tumor-tree posterior

以下是目前仍存在、在 2026-08-20 產生或被 formal workflow 引用的 preflight／simulation artifact；仍要和目前 v2 canonical input 及真實 formal posterior 分開。它們的日期較新，不代表內容就是目前 active model result：

- `output/tumor_tree_pipeline/prerequisites_20260820/`
- `output/tumor_tree_pipeline/metadata_20260820/`
- `output/tumor_tree_pipeline/simulation_20260820/`

以下兩個重複／舊 preflight 目錄已於 2026-08-21 刪除，不再是目前可載入資料：

- `output/tumor_tree_pipeline/prerequisites_ps_1000_20260820/`
- `output/tumor_tree_pipeline/prerequisites_ps_smoke_20260820/`

其中：

- `simulation_20260820/synthetic_recovery_gate.json` 是 synthetic identifiability gate，通過不代表 HCC1395 真實樹恢復。
- `simulation_20260820/raw/m3_assignments.tsv.gz` 與 `m3_latent_cn_site_posterior.tsv.gz` 是 simulator 的舊命名／測試欄位，不能當成正式 `likelihood_input.tsv.gz`。
- `prerequisites_20260820/` 中的 `stage_06_model_gate.json` 與 `stage_07_m3_gate.json` 已於 2026-08-21 刪除；`prerequisites_ps_1000_20260820/` 與 `prerequisites_ps_smoke_20260820/` 內相同命名的 receipt 也隨舊目錄一併刪除。這些檔案原本是舊 stage／M3 contract 的 blocker receipts，不是目前 v2 model gate 通過，也不是成功結果。
- `output/tumor_tree_pipeline/input_20260820/manifest.json` 與 `input_qa.json` 是目前 canonical table 的小型 provenance/QA receipt；大型 `likelihood_input.tsv.gz` 仍是 ignored generated input。
- `output/tumor_tree_pipeline/metadata_20260820/metadata_manifest.json` 是目前 grouped-holdout metadata 的 receipt，不是 likelihood input；它明確記錄 PS 只用於 grouped holdout。

### C3. Build 與 cache 生成物

以下三個已指定的可重建生成物已於 2026-08-21 刪除：

- `inference/build/`
- `tumor_tree_pipeline/__pycache__/`
- `tumor_tree_pipeline/tests/__pycache__/`

前三個目錄不是研究資料，也不是歷史模型結果；之後編譯或執行測試時可以重新產生。其他 ignored checkpoint、samples、logs、temporary lock 與 compiled artifacts 仍不應進入研究上下文，也不應作為來源檔。

## D. 簡化後的上下文載入順序

之後若要理解目前 repo，建議只先載入：

1. [`README.md`](../README.md)（但要注意 B1 的 plain-MH stale block）。
2. [`model.md`](../model.md) 的 active sections。
3. [`data.md`](../data.md) 的 active model-table contract 與 ASCAT purity sections。
4. [`ascat_purity_experiment_workflow.md`](../ascat_purity_experiment_workflow.md)。
5. [`tumor_tree_pipeline/README.md`](../tumor_tree_pipeline/README.md)。
6. [`inference/README.md`](../inference/README.md) 與 `inference/src/`。
7. 最新 formal run 的 `status.json`／aggregate `diagnostics.json`，只作 failed diagnostic evidence。

預設不要載入：`daily/20260819/`、`tumor_tree_pipeline/sampler.py` 的 plain-MH implementation、`output/tumor_tree_pipeline/` 的全部 generated tree、`m3_*` simulation table、已刪除 run 的任何重新推測，以及文件中已不存在的 `tools/`／本 repo 內的 `output/longphase_clone/` 路徑。若需理解目前 inference algorithm，優先讀 [`inference_algo.md`](../inference_algo.md)；若需追溯 input provenance，才讀 manifest 中指向外部 `multi_evol_tree` 的 canonical source path。

## E. 本次盤點紀錄

- 盤點日期：2026-08-21。
- 使用 read-only `git ls-files`、`rg`、`find`、`jq` 與 output status/manifest inspection。
- 已使用多個 subagent 分工掃描 active architecture、historical paths/names、output provenance。
- 本次更新前已依使用者指定，刪除 3 個舊／失敗 formal run、2 個重複 preflight 目錄、6 個舊 blocker receipt，以及 `inference/build/`、兩個 `__pycache__/`；這些都是 ignored、未被 Git 追蹤的 generated artifacts。
- 本次新增 [`inference_algo.md`](../inference_algo.md)，並將 inference algorithm 核心內容從 `model.md` 移出；`model.md` 現在只保留 model specification。
- `README.md`、`tumor_tree_pipeline/README.md` 與 workflow 的演算法導覽已改為指向 `inference_algo.md`，避免把 algorithm contract 分散成多份權威描述。
- 最新 formal failure `20260820T122332Z_afce5dea2c6e_...`、`prerequisites_20260820/` 的其餘現行 audit 檔案、`metadata_20260820/`、`simulation_20260820/` 與 `input_20260820/` 均保留。
- 本次只更新本索引的分類與狀態描述，沒有修改 active source code、canonical input 或研究結果。
- lab knowledge-base 對照：`/big8_disk/liaoyoyo2001/Knowledge/README.md`、`07_script_docs/run-benchmark-sh.md`、`00_background/field-primer.md`。
- repo-local knowledge-base 對照：`/bip8_disk/boyu114/bip8_disk_boyu_database/multi-evol-tree/INDEX.md`、`MANIFEST.tsv`、`SUMMARY.md`。該 knowledge base 的 historical canonical topology 結果與本 repo 2026-08-20 finite-K MCMC output 不可混為同一套結果。
