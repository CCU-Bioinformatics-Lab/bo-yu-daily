# Bulk-only Output Support Evaluator

> 目的：驗證 output.md 定義的模型輸出，並把結果整理成可追溯的 bulk-only 證據評估。
>
> 最高可用語意：**high-confidence candidate branching tree topology**。
>
> 本文件不宣稱 single-cell lineage truth，也不宣稱唯一真實腫瘤演化樹。

## Destination

建立一個獨立於模型 likelihood 的 support evaluator，檢查三項輸出：

1. normal cells → tumor_root → clone topology
2. CCF / phi
3. SNV → clone assignment

評估結果分成三層：

- model fit：模型是否能解釋 observed bulk counts。
- inference reliability：推理實作與 posterior samples 是否可信。
- biological / evolutionary compatibility：候選樹是否與外部 bulk CNA、LOH、ploidy、purity 與文獻證據相容。

support evaluator 是 output 後的獨立評估層，不重新推理模型，也不把外部證據偷偷塞入 likelihood。

## Notes

### output.md 的三項輸出語意

~~~
normal cells
      │
      ▼
tumor_root
      │
      C1
    ┌─┴─┐
   C2  C3
~~~

- normal cells：外部正常細胞根，不是 tumor clone。
- tumor_root：所有 tumor clones 的共同祖先，不承載普通 SNV assignment。
- `normal cells` 是 presentation-level external root；目前 sampler artifact 的 root 是 `tumor_root`，不是一個 normal-cell JSON node。
- `C1/C2/C3` 是 `output.md` 的展示名稱；實際 C++ artifact 的 node ID 可能是 `clone_1/clone_2/...`，support evaluator 必須保存兩者的 mapping。
- parents：clone 的 parent-child topology。
- eta：node 的 local / exclusive cancer-cell mass。
- phi：該 node 加上所有 descendants 的 cumulative cancer-cell fraction。
- SNV → clone assignment：每個 eligible SNV 的 candidate node 與其不確定性。

output.md 的樹圖與數值目前是 `output_status=illustrative` 的說明用 illustration，不能當作已完成的 formal posterior run，也不能從它產生 PASS。

### 證據與狀態詞彙

每項 claim 都要記錄 evidence_layer：

| evidence_layer | 意義 |
|---|---|
| method_capability | 方法理論上能否支援這種輸出或判斷。 |
| published_evidence | HCC1395 論文或其他外部研究已報告的證據。 |
| current_implementation | 本 repo 程式與 artifact 實際產生的結果。 |

每項來源都要記錄 artifact_status：

| artifact_status | 意義 |
|---|---|
| reported | 外部論文或文件明確報告。 |
| reproduced | 本 repo 已成功重建且可檢查。 |
| inferred | 從現有資料或模型結果推導，並非直接觀測。 |
| not_reported | 文獻或文件沒有提供。 |
| missing | 目前應存在但不存在。 |

每個 gate 使用：

| status | 意義 |
|---|---|
| PASS | 證據與預先定義條件全部符合。 |
| FAIL | 明確違反資料、模型或統計條件。 |
| UNKNOWN | 必要資料、artifact 或不確定性不足。 |
| NOT_APPLICABLE | 該檢查不適用於目前 artifact，例如 illustration 沒有 posterior。 |

UNKNOWN 與 NOT_APPLICABLE 都不可當作 PASS。`not_reported` 與 `missing` 是來源 artifact_status，不是目前 run 的 gate status。

### 證據是否獨立

每個 evidence record 另外保存：

~~~
evidence_origin = in_likelihood | held_out | external_orthogonal
used_in_likelihood = true | false
~~~

已進入 likelihood 的 ASCAT CN、purity、multiplicity 與 HP counts 可以支持 model fit 或 compatibility，但不能被再次描述成獨立 branch validation；真正的獨立支持必須標為 `external_orthogonal`。

### PS 的位置

PS phase block 可用於 phase provenance、局部 QC 與 grouped holdout。PS 不直接決定 clone assignment、eta、phi、topology 或 ancestry edge。PS 產生的 HP counts 會間接影響 observation likelihood，但 PS block 本身不進 downstream sampler state。

## Decisions

目前採用以下決策：

1. support evaluator 與模型 likelihood 分離。
2. 正式 purity input 是 rho_ASCAT = 0.99，不再使用舊 tumor DNA fraction 介面。
3. topology、CCF、SNV assignment 分開驗證。
4. CNV、LOH、ploidy 與 purity 先作 bulk compatibility evidence。
5. PhyloWGS 方法層級可將外部 CNV 轉為 pseudo-SSM，與 SSM joint inference，並把 CNV event 放到 clone/tree node。
6. 只有 site-level CN 時，不能宣稱已完成 CNA event → node 推理。
7. driver annotation 與 node assignment 分開記錄；高 CCF 或 figure edge label 不能自動變成 driver truth。
8. single-cell CNV 只作細胞異質性 compatibility evidence；沒有 joint single-cell SNV+CN matrix，不能驗證 SNV lineage。
9. inference_algo.md 記錄的 eta independence-MH proposal cancellation 尚未完成數學 audit；目前不能稱已驗證的 exact posterior MCMC。
10. formal run failed 時，不得發布 Grade A topology claim。
11. CNV-to-node 與 driver annotation 是 optional evidence / interpretation layers，不是 output.md 三項核心輸出；缺失時降低對應 claim ceiling，但不自動抹除核心 topology 的結構驗證。

## Not yet specified

正式實驗前仍要定義：

- topology class scoring、`topology_selection_margin` 與 K=4,6,8 的預先登錄選擇設定。
- 多棵近似等支持 topology 的保留格式。
- node label 是否固定為 C1, C2...。
- 是否把 CNV event 加入模型 latent state。
- CNA event → candidate node 的輸出格式與門檻。
- driver annotation database、release、tier 與 node posterior threshold。
- topology support 最低門檻與 alternative topology set 格式。
- formal run 成功後的 reproducibility manifest。
- support evaluator 的程式位置與命令列介面。

未定義前，結果只能是 candidate topology support，不可解釋為唯一真實演化樹。

## Out of scope

- 從 bulk data 證明唯一真實的腫瘤演化歷史。
- 將 PS block 或 HP1/HP2 label 直接轉成 ancestry edge 或 clone label。
- 用 single-cell CNV 推導每個 SNV 的 lineage。
- 沒有 joint single-cell SNV+CN matrix 時宣稱 single-cell SNV validation。
- 從 site-level CN 直接推導 CNA event timing 或 ordering。
- 僅依高 CCF、ALT count、read depth、multiplicity 或 tumor-root 位置判定 driver。
- 把 HCC1395 圖上的 driver label 當成完整公開的 driver → node table。
- 把 output.md illustration 當成 formal posterior。
- 把 acceptance rate 當作 convergence 證據。

# Ordered Validation Route

依序執行下列 gate。任何 core hard FAIL 都停止該層級 claim；UNKNOWN 不得被補寫成通過。CNV-to-node 與 driver 是 optional evidence gate，缺失時要降低相應 claim ceiling。

### Current repository ceiling

依目前文件與已記錄的 run 狀態：

- `output.md` 只是 illustration，因此不能產生 formal PASS。
- 最新 formal run 為 failed，沒有可發布的成功 posterior tree。
- eta independence-MH proposal cancellation 尚未完成數學 audit。
- 因此目前只能保留為 candidate / method-development status，不能宣稱 exact posterior MCMC、Grade A 或 high-confidence candidate branching tree topology。

## Gate 0：Run completeness and provenance

### Artifact identity precheck

先判斷輸出類型：

| output_status | 動作 |
|---|---|
| `illustrative` | `NOT_APPLICABLE`；只檢查文件語意，不做 posterior PASS。 |
| `formal_posterior` | 繼續本流程。 |
| `failed` 或 `incomplete` | `FAIL`；不得進行 final claim grading。 |

### 檢查

對 `formal_posterior` 確認輸出來自可追溯、完成且可重現的 run：

~~~
sample_id, reference_build, input paths/hashes
model version, inference version, config hash
K, rho_ASCAT, seed, chain count, burnin, thin
holdout scheme, software/compiler version, run status
~~~

每條 chain 與 run 應有：

~~~
chain_complete.json
diagnostics.json
checkpoint.json.gz
posterior samples
representative_tree.json
input/config manifest
~~~

### 判定

| 條件 | 狀態 |
|---|---|
| run 完成、manifest 完整、hash 可追溯 | PASS |
| run 中斷、沒有 completion marker 或沒有 posterior | FAIL |
| manifest 或部分 provenance 缺失 | UNKNOWN |

若 FAIL，不得進行 final claim grading。

## Gate 1：Canonical input contract

### 目前 active likelihood table 的必要欄位

以下是目前 model.md 定義、由 sampler 實際讀取的 site-level 欄位；canonical table 每列是一個 SNV，只有 eligible rows 進入 sampler：

~~~
mutation_id, chrom, pos, ref, alt
bulk_ref, bulk_alt, bulk_depth
hp1_1_ref, hp1_1_alt, hp2_1_ref, hp2_1_alt
major_cn, minor_cn, total_cn
rho_ASCAT
multiplicity_candidates, multiplicity_prior
model_include, model_status
~~~

segment_id、loh_state、BAF、segment boundary 與 caller metadata 不是目前 C++ sampler 的 active likelihood 必要欄位；builder 可以把 segment_id、loh_state 等作為 optional audit columns 保留在 canonical table，也可以由獨立 CN/LOH compatibility artifact 保存。它們不因此成為 active likelihood input。

### 必須驗證

~~~
bulk_depth = bulk_ref + bulk_alt
total_cn = major_cn + minor_cn
major_cn >= minor_cn >= 0
total_cn >= 0
multiplicity_prior >= 0
sum(multiplicity_prior) = 1
mutation_id 唯一
hp1_1_ref + hp1_1_alt + hp2_1_ref + hp2_1_alt <= bulk_depth
~~~

另外確認：

- reference build、sample、ASCAT purity source 與 hash 一致。
- model_include=yes 且 model_status=eligible 才能進 likelihood。
- excluded site 有明確原因，不能被 fallback 成 CN=2 或 m=1。
- CN-zero、unmapped segment、zero-depth 等排除狀態與 `model_include/model_status` 一致。
- PS 不出現在 downstream likelihood schema；其上游產生的 HP counts 必須可追溯。

### Callset evidence subcheck

對 HCC1395 published/canonical callset，另保存 `call_confidence_tier`、caller/replicate support、callable-region status 與 orthogonal validation status（例如 PacBio、AmpliSeq 或 WES）。這些欄位不是 C++ likelihood 必要輸入；缺少它們時是 callset-evidence `UNKNOWN`，不能冒充 callset 已被獨立驗證。

此 gate 只驗證模型吃到的資料是否正確，不代表 topology 已正確。

## Gate 2：Inference correctness

### 目前演算法

目前 active sampler 是有限 K 的 PhyloWGS-inspired compound Metropolis-within-Gibbs MCMC：

- assignment Gibbs
- local-mass independence Metropolis-Hastings
- conditional subtree prune-and-regraft topology update
- 多條 independent chains 作外層診斷

inference_algo.md 與 C++ source 都記錄了 eta 的非對稱 Dirichlet independence proposal；source 的設計註解認為 proposal 不依賴 current eta，因此 forward/reverse density 可抵消。但這個抵消條件與實際 target/proposal 定義仍需數學 audit。一般 independence proposal 的完整比例是：

~~~
log α = log π(eta_new) - log π(eta_old)
        + log q(eta_old) - log q(eta_new)
~~~

### 必須檢查

- Gibbs conditional、MH forward/reverse proposal density 與 normalization 正確。
- topology move 的 forward/reverse probability 正確。
- state 不形成 cycle，root semantics 一致。
- log posterior 無 NaN/Inf，參數邊界不產生非法 state。
- checkpoint、RNG state 與 config hash 可追溯；目前 C++ 未宣稱可直接 restore。

| 情況 | 狀態與 claim ceiling |
|---|---|
| transition 與 reverse proposal term 完成 audit | PASS，仍須通過後續 diagnostics |
| 明確存在錯誤 | FAIL，不得作 posterior claim |
| 尚未完成 audit | UNKNOWN，不可稱已驗證的 exact posterior MCMC 或 Grade A |

## Gate 3：Tree structure

### 主要輸出

~~~
parents
selected_edges
best_sample
node_id, parent_id, root_id
~~~

### 必須檢查

- normal cells、tumor_root、ordinary clone node 的語意分開。
- parents 無 cycle；除 tumor root 外每個 node 只有一個 parent。
- 所有 node 從 tumor_root 可達。
- selected_edges 與 parents 一致。
- best_sample 確實存在於 retained samples。
- topology comparison 使用 label-invariant node matching。
- root 不被錯誤當成普通 SNV clone。

結構合法只代表輸出是一棵合法樹，不代表它是生物學唯一正確的樹。

## Gate 4：eta / phi CCF constraints

對每一個 posterior draw 驗證：

~~~
eta_v >= 0
sum_v eta_v = 1
phi_v = eta_v + sum(eta_u for all descendants u)
0 <= phi_v <= 1
phi_parent >= phi_child
phi_parent >= sum(phi_immediate_children)
phi_tumor_root = 1
~~~

`sum(eta)=1` 是對全部 latent finite-K clone nodes（包括 occupancy 為 0 的 node）；輸出時可另報 occupied nodes。若 normal cells 也納入完整 cellular mixture，必須另寫 mixture convention；不可把 tumor-only phi 與 normal fraction 混用。建議 node schema 明確保存 `node_type = normal_root | tumor_root_wrapper | clone` 與 `mixture_convention = tumor_only | full_sample`。

常見錯誤：把 eta 當 CCF、把 phi 當 local mass、把 purity 當 node phi、或把 ALT/depth 直接當 CCF。此 gate 通過只表示數學一致，不表示 purity、CNV、multiplicity 已被正確解釋。

## Gate 5：SNV-to-clone assignment

### 必須保留

~~~
mutation_id, assigned_node, assignment_posterior, assignment_status
ccf_median, ccf_lower, ccf_upper, local_cn, multiplicity
model_include, model_status
~~~

### 必須檢查

- input 與 output 的 mutation ID 一一對應。
- 所有 fitted eligible SNV 有 assignment；excluded site 與該 chain 的 holdout site 不得被報成已 assignment。
- assignment node 存在於 parents。
- assignment posterior 不可使用不存在的 node。
- assignment 與 phi / CCF interval 相容。
- 本 gate 只驗證單一 chain/run 的 assignment 完整性；跨 chain 的 label-invariant assignment agreement 延後到 Gate 10。

對 holdout chain，fitted eligible sites 是 `eligible sites − 該 chain 的 holdout IDs`；holdout sites 不要求 assignment，應在 Gate 6 以 predictive output 驗證。

建議狀態：assigned、ambiguous、unassigned、excluded、unknown。

目前 samples.jsonl.gz 主要保存 log_posterior、parents、eta、phi、occupancy；逐 SNV posterior 若只存在 checkpoint 或 representative artifact，必須明確標記其來源。缺少逐 SNV posterior 時，不得把單一 assignment 宣稱為穩定 clone truth。

## Gate 6：Bulk likelihood and predictive holdout

### 檢查

以模型 predictive distribution，而不是只有 ALT / depth，檢查：

~~~
bulk REF/ALT counts, depth, rho_ASCAT
local CN, multiplicity, CCF/phi
posterior predictive ALT count/VAF
site holdout, PS-grouped holdout
chromosome/ASCAT-segment grouped sensitivity
predictive log score, central credible interval coverage
~~~

VAF 的預測受 purity、total/major/minor CN、multiplicity 與 clone CCF 共同影響。PS grouped holdout 可測試 phase block 的泛化，但不代表 PS 進入 ancestry likelihood。

目前 implementation 產生 aggregate predictive coverage 與 log score；尚未自動產生 CN、depth、CCF、driver strata 或獨立 per-site ALT-count predictive artifact。workflow 的正式 predictive gate 是 central 90% coverage 0.85–0.95；stratified/per-site 表是應補的 artifact，不得描述成目前已產生的結果。若 formal run failed 或缺少完整 predictive artifact，此 gate 為 FAIL 或 UNKNOWN。

## Gate 7：ASCAT purity、ploidy、CN 與 LOH compatibility

### 外部 bulk evidence

~~~
rho_ASCAT, purity source/hash, global ploidy
segment_id, chr/start/end
major_cn, minor_cn, total_cn
BAF/allelic counts, LOH state, CNV caller/version
~~~

檢查該 run 的 purity 與 manifest/model input 一致；primary run 是 rho_ASCAT=0.99，0.97/0.95 是 sensitivity runs。purity 是 mixture calibration，不是 topology edge 的直接證據，也不是 per-node phi。

檢查：

~~~
total_cn = major_cn + minor_cn
major_cn >= minor_cn >= 0
~~~

並檢查 segment boundary、ploidy 與全基因組 CN profile 是否相容，以及 CN-zero/unmapped exclusion 是否有記錄。LOH 需綜合 normal heterozygous anchor、tumor allele balance、major/minor CN、BAF/allelic counts、deletion LOH 與 copy-neutral LOH、segment boundary、caller/version；高 VAF、HP label、HP3 或單一 imbalance flag 不能單獨證明 LOH。

此 gate 是 bulk compatibility 檢查，不直接證明某 branch 發生某個 CNA event。由於 CN/purity/multiplicity 多數已進 likelihood，這裡的結果標為 `in_likelihood` compatibility；不能當作獨立 branch validation。

## Gate 8：CNV event → candidate node

### 方法能力

在 `method_capability` 層級，PhyloWGS 可接收外部 CNV preprocessing，將 CNV 表成 pseudo-SSM/CNV event，與 SSM joint inference，並依 overlap、timing 與 allele-copy mass 將 event 放到 clone/tree node。這不等於 HCC1395 論文已公開實際 CNV input 或完整 node assignment；其 evidence record 應拆寫為 `evidence_layer=published_evidence`、`artifact_status=not_reported`。

### 目前 claim ceiling

目前本 repo 的 major_cn、minor_cn、total_cn 與（若在 compatibility artifact 中存在的）segment_id、loh_state 是 site/segment CN context，不等於完整 CNV latent event。若沒有以下輸出，必須標記：

~~~
CNV event → node placement = UNKNOWN
CNV event timing = UNKNOWN
CNV event order = UNKNOWN
~~~

未來若真的加入 CNV latent state，至少保存：

~~~
cnv_event_id, segment_id, cnv_type, chrom, start, end
major_cn, minor_cn, total_cn, event_prevalence
candidate_node, assignment_posterior, ccf_interval
affected_snv_ids, multiplicity_context
snv_cnv_timing, phase_or_allele_context
prevalence_convention, cell_universe
tumor_cell_fraction, all_cell_fraction, purity_conversion
independent_support, claim_status
~~~

目前最多只能寫：「候選 topology 與 segment-level CN/LOH pattern 相容」，不能寫「已證明 CNA event 發生在某 clone branch」。

## Gate 9：Driver annotation 與 node mapping

driver annotation 是獨立的 interpretation layer，不是目前 model/inference 的自動輸出。至少保存：

~~~
event_id, variant_key, chrom, pos, ref, alt
gene, transcript, consequence
annotation_database, database_version, driver_tier
candidate_node, assignment_posterior
ccf_interval, local_cn, multiplicity
cnv_context, loh_context, independent_source, claim_status
~~~

claim_status 可用 annotation_only、figure_annotation_only、posterior_supported_candidate、independently_supported、ambiguous、unknown。

不可由高 CCF、ALT count、tumor-root 位置、figure edge label、高 multiplicity 或高 depth 單獨產生 driver truth。HCC1395 論文的 driver labels 可作 published evidence，但沒有完整公開 driver → node mapping table 時，不能直接轉成目前模型的真實 clone assignment。

## Gate 10：Topology stability

確認 topology 不是單一 chain、seed 或設定造成：

- 至少 4 條 independent chains。
- 比較 K=4,6,8。
- 比較 rho_ASCAT sensitivity、CN source/caller sensitivity。
- 做 holdout scheme sensitivity；site/read/segment bootstrap 是 recommended future robustness analysis，不是目前 formal hard gate。
- 保存 topology frequency、edge posterior support、node occupancy、CCF interval overlap、SNV assignment agreement 與 alternative topology posterior mass。

workflow/recommended gates：

~~~
R-hat < 1.01
bulk ESS >= 400
tail ESS >= 400
label-invariant assignment agreement >= 0.90
max cross-chain edge-support difference <= 0.10
~~~

這些是 workflow gate，不是目前結果。Acceptance rate 只描述 proposal 被接受比例，不是 convergence、posterior 穩定或 assignment 正確的證明。

### Branching / linear / polytomy selection

不能用 CCF peaks 或單一 best sample 直接把 topology 命名為 branching。support evaluator 必須依下列可重現路線執行：

1. 將每個 draw 的 node labels canonicalize，保存 rooted clade/edge topology key；比較時不使用 `C1` 或 `clone_1` 這類 label。
2. 在 primary `K=6, rho_ASCAT=0.99` 下，按預先登錄的 topology class（linear、branching、polytomy）彙總 posterior mass、edge support 與 predictive metrics。
3. 用同一套規則比較 `K=4/8` 與 rho sensitivity；跨 K 只比較共同 rooted clade/partition，不能直接比較 node index。
4. 只有當 branching class 在 primary 與 sensitivity 中勝出、core predictive gate 通過，且與 runner-up 的差值大於 run manifest 事先保存的 `topology_selection_margin`，才令 `topology_status=branching_candidate`。
5. 若 `topology_selection_margin` 尚未登錄、候選支持接近、或不同設定選出不同 class，令 `topology_status=ambiguous`，不得使用 high-confidence branching 名稱。

因此，現在「選擇規則尚未具體化」本身就是 Gate 10 的 `UNKNOWN`；在 margin、class scoring 與 canonicalization 實作完成前，不能機械化授予 Grade A。

## Gate 11：Uncertainty and alternatives

必須保留：

~~~
node/edge: node_id, parent_id, edge_support, occupancy, topology_frequency
CCF: eta_median, eta_interval, phi_median, phi_interval
SNV: mutation_id, candidate_node, assignment_posterior, uncertainty summary
CN/LOH: segment_id, compatibility_status, evidence status
alternative: topology_id, parents, posterior_mass, edge_set, selection_status
~~~

若多棵 topology 支持接近，輸出 topology_status=ambiguous，不能任意挑一棵標成唯一真實樹。

## Gate 12：Final claim grading

### Grade A — bulk-supported candidate topology

run provenance、input、inference correctness、tree structure、CCF、assignment、bulk predictive、purity/CN/LOH compatibility、uncertainty、multi-chain/K/purity/CN sensitivity 與 alternatives 全部通過，才能使用：

> **high-confidence candidate branching tree topology**

仍不可稱 single-cell lineage truth 或唯一真實演化樹。

### Grade B — supported local edges / partial topology

部分 edge 在多 chain 穩定，CCF 與 bulk CN 相容，但完整 topology 有 alternatives 或部分 assignment 不穩定。

### Grade C — candidate hypothesis

模型可產生合法樹，且有部分 bulk evidence，但 inference reliability、holdout 或 sensitivity 尚未完整通過；CNV-to-node 或 driver mapping 仍可能是 UNKNOWN。

### Grade D — no evolutionary claim

任何 core hard gate FAIL、formal run failed、posterior artifact 缺失、inference correctness 未完成且影響 posterior validity，或 topology 對 chain/K/purity 高度敏感時，只能報告：

> no supported evolutionary claim from the current run

目前已知阻擋 Grade A 的項目：eta MH proposal cancellation 尚未 audit；最新 formal run failed；core topology/CCF/assignment/stability/predictive gate 未通過。只有 site-level CN 時，CNV event→node 是 optional UNKNOWN，會阻擋 CNV-to-node claim，但不單獨阻擋 bulk-compatibility topology Grade A。沒有 joint single-cell SNV+CN 時不能宣稱 single-cell lineage validation。

# Support Artifacts: Current vs Future

以下要區分三種東西：

- `current artifact`：目前 C++/workflow 已能產生，必須先核對內容。
- `derived evaluator artifact`：support evaluator 需要由 current artifact 與 input join/summary 產生；缺少時對應 status 是 `UNKNOWN`。
- `optional future evidence`：目前模型沒有產生，只有未來加入 CNV latent event 或獨立 annotation layer 後才建立。

## 1. Run manifest

~~~
run_id, sample_id, reference_build, input_manifest_hash
model_version, inference_version, config_hash
seed, chain_count, burnin, thin, K, rho_ASCAT
holdout_scheme, software_version, compiler_version, run_status
schema_version, algorithm_id, git_commit, exact_command
canonical_table_hash, holdout_manifest_hash, evaluator_version, output_status
~~~

## 2. Topology summary

~~~
topology_id, node_id, parent_id, node_type
eta_median, eta_interval, phi_median, phi_interval
occupancy, edge_support, topology_frequency, selected_status
~~~

## 3. Per-chain posterior artifacts（目前 current artifact）

來源：samples.jsonl.gz、checkpoint.json.gz、chain-level diagnostics.json。per-chain sample record 目前以 iteration 識別；chain_id 由目錄與 chain-level manifest/diagnostics 提供，不假設它存在每一筆 JSON record。

~~~
iteration, log_posterior, parents, eta, phi, occupancy
checkpoint: parents, eta, z, RNG state, retained samples, input/config hashes
chain diagnostics: input hash, seed, proposal counters, acceptance rates, finite summaries
~~~

acceptance_rate 只能作 proposal diagnostics。

## 4. Fit-level diagnostics（目前 current artifact）

R-hat、bulk/tail ESS、label-invariant assignment agreement、edge support difference 與 aggregate holdout coverage/log score 是 fit-level/outer-chain diagnostics；不能從單條 chain diagnostics 推導。

## 5. Site assignment table（derived evaluator artifact）

~~~
mutation_id, chrom, pos, ref, alt
assigned_node, assignment_posterior, assignment_status
ccf_median, ccf_lower, ccf_upper, local_cn, multiplicity
model_include, model_status
~~~

目前 representative_tree 直接提供 assignment node、assignment probability 與 best-sample assignment；`ccf_*`、`local_cn`、`multiplicity`、`assignment_status` 若沒有由 evaluator 正確 join/derive，就標記 `UNKNOWN`，不能只因欄位名稱存在就宣稱已輸出 posterior assignment。

對每一列另保存 `chain_id`、`draw_count`、`assignment_support`、`assignment_entropy` 與 `source_artifact`，以區分跨 draw/跨 chain summary 和單一 best sample。

## 6. Predictive site table（derived evaluator artifact）

若要驗證 per-site holdout，至少保存：

~~~
mutation_id, holdout_group, is_held_out
observed_ref, observed_alt, predictive_mean
predictive_lower, predictive_upper, interval_level, log_score
evidence_origin
~~~

目前 workflow 主要產生 aggregate coverage/log score；缺少此表時，per-site predictive claim 為 `UNKNOWN`。

## 7. CNV / LOH compatibility table（optional evidence layer）

~~~
segment_id, chrom, start, end
major_cn, minor_cn, total_cn, loh_state
cnv_status, cnv_caller, purity_source, ploidy
compatibility_status, evidence_layer, artifact_status, notes
~~~

沒有 cnv_event_id 與 candidate_node 時，這只表示 compatibility context，不表示 event placement。

## 8. CNV event-to-node table（optional future evidence；目前為 UNKNOWN）

~~~
cnv_event_id, segment_id, cnv_type, chrom, start, end
candidate_node, assignment_posterior, event_prevalence, ccf_interval
affected_snv_ids, multiplicity_context, snv_cnv_timing
phase_or_allele_context, prevalence_convention, cell_universe
tumor_cell_fraction, all_cell_fraction, purity_conversion
independent_support, claim_status
~~~

## 9. Driver annotation table（optional interpretation layer）

~~~
event_id, variant_key, gene, transcript, consequence
annotation_database, database_version, driver_tier
candidate_node, assignment_posterior, ccf_interval
local_cn, multiplicity, cnv_context, loh_context
independent_source, claim_status
~~~

## 10. Evidence matrix

~~~
claim_id, claim, evidence_layer, artifact_status, status
source, supporting_fields, contradicting_fields, missing_fields
claim_ceiling, reviewer_note
~~~

範例：

| claim | layer | status | claim ceiling |
|---|---|---|---|
| topology is structurally valid | current_implementation | PASS | structural validity |
| CCF obeys descendant constraints | current_implementation | PASS | numerical consistency |
| CNV event maps to clone node | current_implementation | UNKNOWN | no CNV-to-node claim |
| cell-level CNA heterogeneity exists | published_evidence | PASS | cell-level heterogeneity |
| branching topology is branch-validated by HCC1395 CNA | published_evidence | UNKNOWN | no branch-level validation claim |
| PhyloWGS method supports CNV event → node | method_capability | PASS | method capability only |
| HCC1395 run used a published CNV event → node table | published_evidence | UNKNOWN | no published event-to-node claim |
| SNV lineage is validated by single-cell data | published_evidence | UNKNOWN | no single-cell lineage claim |
| final topology is high-confidence | current_implementation | UNKNOWN | blocked by inference/run status |

# Wayfinder Decision Route

這份文件同時作為目前 support evaluator 的本地 destination map。依賴關係如下：

~~~
run completeness/provenance
          ↓
canonical input contract
          ↓
inference correctness
          ↓
tree structure → eta/phi → SNV assignment
          ↓
chain/K/purity stability
          ↓
bulk predictive holdout
          ↓
ASCAT/CN/LOH compatibility
          ↓
optional CNV event-to-node + driver interpretation
          ↓
uncertainty + alternatives
          ↓
claim grade
~~~

目前的 decision tickets：

1. **Inference correctness**：完成 eta MH reverse proposal audit。
2. **Formal reproducibility**：修正 blocker 後重跑正式 chains 與 grouped holdouts。
3. **Topology comparison**：比較 linear、branching、polytomy 及 label-invariant edge support。
4. **Bulk compatibility**：檢查 CCF nesting、ASCAT CN/LOH/ploidy/purity 與 predictive residual 是否一致。
5. **CNV event placement**：只有模型輸出 event-to-node table 才能把 compatibility 升級成 placement claim。
6. **Driver layer**：完成獨立 annotation 與 variant-to-node posterior join，否則保留 annotation_only 或 unknown。
7. **Final confidence**：依 hard gates、missing artifacts、alternative topologies 與 claim ceiling 給 A/B/C/D。

# Source Map

- [output.md](output.md)：定義 topology、CCF/phi 與 SNV-to-clone assignment 的展示輸出。
- [model.md](model.md)：定義 bulk counts、ASCAT CN、purity、multiplicity、CCF 與 likelihood 邊界。
- [inference_algo.md](inference_algo.md)：定義 latent state、MCMC kernels、chain artifacts 與 eta MH blocker。
- [ascat_purity_experiment_workflow.md](ascat_purity_experiment_workflow.md)：定義 purity、canonical table、holdout、chain 設定與 workflow gates。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/README.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/README.md)：HCC1395 review 總覽。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/01_data_and_callset.md)：樣本、bulk callset、CNA、LOH、ploidy 與資料來源。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md)：HCC1395 tree reconstruction、PhyloWGS 與 driver label 邊界。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/03_validation_evidence.md)：bulk CNA、LOH、ploidy、purity 與 single-cell CNV 的外部證據。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/04_confidence_and_limits.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/04_confidence_and_limits.md)：candidate branching topology 的信心邊界。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/05_lessons_for_current_repo.md)：HCC1395 經驗對目前 bulk-only repo 的可轉移內容。
- [golden_tree/research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md](golden_tree/research/hcc1395_tumor_evolution_tree_review/06_evolutionary_model_support_framework.md)：model fit、inference reliability、biological compatibility 分層框架。
- [golden_tree/research/phylowgs_model_review.md](golden_tree/research/phylowgs_model_review.md)：PhyloWGS SSM/CNV joint inference、pseudo-SSM 與 CNV-to-node 方法能力。

# Final Interpretation Rule

只有在必要 artifact 存在、core hard gates 全部通過、posterior inference 完成 correctness audit，且 topology 在 chains、K、purity 與 workflow CN/source sensitivity 下穩定時，才能標記：

~~~
high-confidence candidate branching tree topology
~~~

這個名稱仍然只表示：

~~~
bulk-supported candidate branching topology
~~~

不表示：

~~~
single-cell lineage truth
unique true tumor history
directly observed clone ancestry
~~~
