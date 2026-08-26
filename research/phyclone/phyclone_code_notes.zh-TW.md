# 官方 PhyClone 程式碼筆記

## 1. 版本與 repository 身分

本地保存的是作者/實驗室的官方 repository，而不是 fork：

- repository：`Roth-Lab/PhyClone`
- tag/version：`0.8.0`
- commit：`27383246c1aff7b1d62c02662017bd61bfdfbc33`
- package entry point：`phyclone = phyclone.cli:main`
- Python：`>=3.12`
- license：GPL-3.0-or-later

論文 benchmark 的 archival code 是 **v0.7.0**，保存在 [Zenodo 15062185](https://zenodo.org/records/15062185)。因此「現在 GitHub 的 v0.8.0」與「論文當時用來 benchmark 的 v0.7.0」必須分開記錄；要重現 paper 結果，應優先使用 archival snapshot 與 paper settings。

## 2. Source tree 對照

```text
phyclone/
├── cli.py                    # run/map/consensus/topology-report commands
├── run.py                    # chain、burn-in、main sampler、HDF5 trace
├── data/
│   ├── pyclone.py            # input table、CN genotype prior、likelihood grid
│   ├── base.py               # DataPoint container
│   └── validator/            # JSON schemas + validation
├── tree/                     # FS-CRP tree and joint distribution
├── smc/                      # bootstrap/fully-adapted/semi-adapted kernels
├── mcmc/
│   ├── particle_gibbs.py     # PG tree/subtree updates
│   └── gibbs_mh.py           # data reassignment / prune-regraph moves
├── process_trace/            # MAP、consensus、topology report/archive
├── utils/                    # HDF5 save/load、math/cache utilities
└── tests/                    # unit/integration correctness tests
```

這個 tree 與論文 supplementary implementation description 一致：先把 emission 變成 CCF grid，接著以 tree likelihood 建構與採樣；但 repository 的具體 serialization 與 default options 會隨 release 改變。

## 3. Code-level input contract

### 3.1 Main schema

[`data/validator/PhyClone_schema.json`](PhyClone/phyclone/data/validator/PhyClone_schema.json) 定義：

- required: `mutation_id`, `sample_id`, `ref_counts`, `alt_counts`, `major_cn`, `minor_cn`, `normal_cn`；
- optional: `tumour_content`, `error_rate`, `chrom`；
- counts/CN/error-rate/purity 類欄位不可為負值；
- mutation/sample identity 可為 string 或 integer。

### 3.2 Cluster schema

[`data/validator/cluster_file_schema.json`](PhyClone/phyclone/data/validator/cluster_file_schema.json) 要求 `mutation_id`、`cluster_id`；可選 `sample_id`、`cellular_prevalence`、`outlier_prob`、`chrom`。若啟用 data-informed loss prior，程式碼會額外檢查 `sample_id`、`chrom`、`cellular_prevalence` 是否可用。

### 3.3 Loader 的實際順序

[`data/pyclone.py`](PhyClone/phyclone/data/pyclone.py) 的 `load_pyclone_data` / `load_data` 會：

1. 讀取並驗證 delimiter、schema、column types；
2. 去除 duplicated rows；
3. 移除 `major_cn == 0`；
4. 移除沒有完整涵蓋全部 sample 的 mutation；
5. 補 `error_rate = 1e-3`、`tumour_content = 1.0`；
6. 依 mutation group rows，建立每個 sample 的 `SampleDataPoint`；
7. 由 major/minor/normal CN 與 error rate 建立 genotype candidates/`log_pi`；
8. 將每個 data point 轉成 Binomial 或 Beta-Binomial CCF likelihood grid。

這是結構性輸入清理，不等於 raw sequencing QC。官方 PhyClone 沒有 BAM read counting、somatic variant calling、CN segmentation 或 purity estimation pipeline；這些都在它的輸入邊界之外。

## 4. Command entry points

### 4.1 `phyclone run`

主要參數：

| option | 功能 |
|---|---|
| `-i/--in-file` | main tidy TSV |
| `-c/--cluster-file` | optional cluster TSV |
| `-o/--out-file` | HDF5 trace output |
| `-b/--burnin` | unconditional SMC burn-in |
| `-n/--num-iters` | main MCMC iterations |
| `--num-chains` | independent parallel chains |
| `--num-particles` | PG-SMC particle count |
| `-d/--density` | `binomial` 或 `beta-binomial` |
| `--precision` | Beta-Binomial precision |
| `--grid-size` | CCF discretisation grid |
| `-p/--proposal` | `bootstrap`、`fully-adapted`、`semi-adapted` |
| `--seed` | reproducibility |
| `-l/--outlier-prob` | global outlier prior |
| `--assign-loss-prob` | 從 cluster data 推定 loss prior |
| `--user-provided-loss-prob` | 使用 cluster file 的 `outlier_prob` |
| `--high-loss-prob` | data-informed loss prior 的 high level |
| `--subtree-update-prob` | subtree PG update 機率 |

目前 v0.8.0 CLI defaults 與 paper benchmark settings 不完全相同。至少要把 version、CLI options、input hash、seed、chain count、burn-in、iteration、particle count、density、grid size 與 outlier settings 一起保存，才有可重現性。

### 4.2 `phyclone map`

輸入 HDF5 trace，依 `joint-likelihood` 或 topology `frequency` 選一個代表 tree。輸出：

- Newick tree；
- mutation/clone table；
- sample prevalence table。

程式碼在 [`process_trace/process_trace.py`](PhyClone/phyclone/process_trace/process_trace.py) 的 `write_map_results`、`get_clone_table`。

### 4.3 `phyclone consensus`

從 sampled tree clade frequency 建 consensus tree。可選：

- `--consensus-threshold`；
- `--weight-type counts`；
- `--weight-type joint-likelihood`。

輸出格式與 MAP 相同，但 topology 是 sampled clades 的 thresholded consensus。

### 4.4 `phyclone topology-report`

輸出 unique topology table；若給 `--topologies-archive`，每個 topology 會包含：

```text
{topology_id}_results_table.tsv
{topology_id}.nwk
{topology_id}_sample_prevs_table.tsv
```

這個 command 是保留 posterior topology diversity 的主要出口，不應只看 MAP tree 就丟掉其他 topology。

## 5. Trace HDF5 contract

[`utils/save_hdf5.py`](PhyClone/phyclone/utils/save_hdf5.py) 寫入：

```text
samples
run_info/rng_seed
clusters/{cluster_id,mutation_id}             # optional
data/datapoints/datapoint_i/{value,attrs...}
trace/chains/chain_i/trace_data/{iter,time,alpha,log_p,tree_hash,
                                  num_nodes,num_outliers,num_roots}
trace/chains/chain_i/trees/tree_iter/...     # graph/node data references
```

同一個 sampled tree 可以透過 `tree_hash` / HDF5 reference 重用 storage。`load_hdf5.py` 再把 trace 還原為 DataPoint、Tree 與 chain dataframe，交給 MAP/consensus/topology postprocessor。

## 6. Official companion workflow

`Roth-Lab/PhyClone-Workflow` 是官方 Snakemake companion，不是 core PhyClone library。它的主要流程是：

```text
input_file
  ↓ correct_input
cleaned_input.tsv.gz + removed_variants.tsv.gz
  ↓ PyClone-VI
clusters.tsv.gz + PyClone-VI trace.h5
  ↓ PhyClone run
trace.h5
  ├── MAP / Consensus tree + SVG
  ├── mutation result table
  ├── sample prevalence table
  └── topology report / optional archive
```

workflow 的 config 會把 `pyclone-vi` 與 `phyclone` options 分開管理，並保存 program version、logs、benchmarks、cleaned input 與 removed variants。這個 workflow 仍假設 `input_file` 已經是 PyClone-VI/PhyClone-compatible tidy table；它不是 BAM-to-tree pipeline。

## 7. 與目前 tumor-tree repo 的邊界

這個研究 bundle 只是 reference，不修改 active backend。概念上有相似處：

- 都把 raw BAM/VCF/CN/purity processing 放在 upstream builder；
- 都把 purity/CN/allele counts 帶入 observation model；
- 都保留 posterior/diagnostics，而不是只輸出一棵樹。

但不能宣稱目前 backend 是 PhyClone reproduction：目前 repo 是 finite-K、Rao–Blackwellized annealed SMC；它不等同於 PhyClone 的 FS-CRP + auxiliary-order Particle Gibbs，也沒有直接複製 PhyClone 的 outlier/loss model、pre-clustering 或 HDF5 trace schema。

另外，PhyClone 的 `error_rate` 是 input column（缺省 `0.001`）；目前 repo 的 active runtime 尚未同步此欄位，文件 target 固定記錄 `0.001`。在 config 或結果解讀上，必須把文件 target 與尚未同步的 runtime 分開標記。
