# HCC1395 30,490-site 腫瘤演化樹：ASCAT purity 重跑流程

更新日期：2026-08-20
狀態：**正式契約已固定；新版 pipeline、fixture 與 wrapper 完成驗證前，不啟動完整 MCMC**

本流程以 ASCAT tumor purity `rho_ASCAT=0.99` 重建 HCC1395 finite-K 候選腫瘤演化樹。LongPhase-S 報告的 DNA fraction `0.958936` 只保留為歷史 provenance，不是模型輸入。

正式、可版本控制的執行來源是 [`tumor_tree_pipeline/`](tumor_tree_pipeline/)。`/bip8_disk/boyu114/multi_evol_tree/tools/` 內的舊 builder、experiment loop 與 production runner只供歷史比對，不再是正式入口。

## 1. 研究邊界

- site universe：HCC1395 的 30,490 個 PASS biallelic TP SNV。
- observation：bulk REF/ALT、`HP:Z:1-1/2-1` counts、ASCAT allele-specific CN 與 ASCAT purity。
- inference：有限節點 clone tree、mutation assignment 與 clone prevalence posterior。
- output：只能稱為 **candidate tumor-tree posterior**；不能稱為 single-cell lineage truth。
- `eta`：K 個 clone local masses 的 simplex；`phi` 由 descendants sum 推導。structural tumor root 不承載 SNV，normal contamination 只由 `rho_ASCAT` 處理。

## 2. 正式模型輸入

每列是一個 SNV，key 為 `chrom + pos + ref + alt`。只有 `model_include=yes` 且 `model_status=eligible` 的列進 likelihood；排除列仍保留供 QA。

| 欄位 | 角色 |
|---|---|
| `bulk_ref`, `bulk_alt`, `bulk_depth` | 該 SNV 的 bulk allele counts；`depth=ref+alt` |
| `hp1_1_ref`, `hp1_1_alt` | `HP:Z:1-1` 的條件式 read allocation evidence |
| `hp2_1_ref`, `hp2_1_alt` | `HP:Z:2-1` 的條件式 read allocation evidence |
| `major_cn`, `minor_cn`, `total_cn` | ASCAT 投影到 SNV 的 allele-specific CN；`total=major+minor` |
| `multiplicity_candidates` | 由 extant major/minor side 決定的可行 mutated-copy 數 |
| `multiplicity_prior` | **只由 CN 建立**的固定先驗；sampler 對 `m` 邊際化 |
| `rho_ASCAT` | 全域固定 ASCAT purity；主分析為 `0.99` |
| `model_include`, `model_status` | fail-closed eligibility gate |

### 2.1 CN-only multiplicity prior

這個 prior 不讀 VAF、bulk ALT/depth 或 purity，避免同一組 bulk counts 先決定 multiplicity、又進一次 bulk likelihood。

1. extant major/minor side 各先取得 `0.5`；CN=0 的 side 不分配權重，另一側取得全部權重。
2. 每一側再於 `m=1..side_CN` 均分。
3. 兩側產生相同 `m` 時，將機率相加。

例如 `major_cn=3, minor_cn=1`：

```text
major side: m=1,2,3，各 1/6
minor side: m=1，1/2

multiplicity_prior = 1=0.666667;2=0.166667;3=0.166667
```

這是 major/minor orientation 未知時的中性階層 prior，不把 ASCAT major/minor 誤認為 HP1/HP2，也不宣稱 mutation timing 已知。

### 2.2 Purity 的唯一作用

`rho_ASCAT` 只在 provenance 驗證與 emission 中生效。SNV `i` 在 clone `z_i`、multiplicity `m`、total CN `C_i` 下的期望 ALT fraction為：

```text
q_i = rho_ASCAT * phi_z(i) * m
      / ((1-rho_ASCAT)*2 + rho_ASCAT*C_i)
```

`rho_ASCAT` 不參與 `multiplicity_prior`，也不由 sampler 重新估計。

### 2.3 PS 的邊界

PS block 是 LongPhase-S 建立 HP labels 的上游 phase 資訊。先在同一 PS block 內維持 `HP1-1`／`HP2-1` label 的一致性，再把 reads 彙整成 `hp1_1_ref`、`hp1_1_alt`、`hp2_1_ref`、`hp2_1_alt`；因此 PS 對 downstream likelihood 的 `H_i` 有間接影響。

但 PS **不是 downstream likelihood 的直接欄位，也不是 MCMC state、clone label 或 topology edge constraint**。跨不同 PS block 不假設 `HP1`／`HP2` 具有全球一致方向。PS 只另用於：

- 外部 audit 步驟用 canonical tagged BAM 重建 `ps_read_audit.tsv.gz` 與 manifest；wrapper 只驗證 manifest、hash 與 discordance fraction `<=0.01`，不直接讀 BAM。
- PS-grouped strict holdout，避免同一 phase block 被拆到 train 與 holdout。
- provenance 與局部一致性 QC。

另做 chromosome-grouped 與 ASCAT-segment-grouped holdout，作為切分方式的 sensitivity analysis；它們不取代 PS audit。

## 3. 原始資料如何變成模型表

```text
30,490-site TP VCF ─┐
canonical tagged BAM ├─> LongPhase-S PS blocks ─> HP1-1/HP2-1 counts ─┐
ASCAT segments ──────┼─> site-level major/minor CN ────────────────────┼─> likelihood_input.tsv.gz
ASCAT purity file ───┘                                                  └─> manifest + QA
```

### 3.1 可重用與必須重建

- 重用已通過 row count、site key、count conservation 與 BAM quickcheck 的 30,490-site counts；不為 purity 改變重掃 273 GB BAM。
- 正式 manifest 補齊 VCF、counts、ASCAT、程式與輸出的 SHA-256；大型 BAM 記錄 path、size、mtime、header、quickcheck，並背景補算內容 hash。
- 重新由 ASCAT segments 建立 `site_cnv_qc.tsv.gz`，保留 `mapped_nonzero_cn`、`cn_zero`、`unmapped_segment`、`segment_overlap` 四種狀態。
- 在wrapper外重新執行PS read audit並保存artifact；先前摘要可作對照，不能取代新manifest。
- builder 只建立 `multiplicity_candidates` 與 CN-only `multiplicity_prior`。

### 3.2 Canonical table 格式

```csv
mutation_id,chrom,pos,ref,alt,bulk_ref,bulk_alt,bulk_depth,hp1_1_ref,hp1_1_alt,hp2_1_ref,hp2_1_alt,major_cn,minor_cn,total_cn,rho_ASCAT,multiplicity_candidates,multiplicity_prior,model_include,model_status
chr1:100:A:G,chr1,100,A,G,34,11,45,8,6,10,2,3,1,4,0.99,"1;2;3","1=0.666667;2=0.166667;3=0.166667",yes,eligible
```

正式 loader 必須 fail closed：缺欄、非法 CN、purity 不一致、prior support／sum 錯誤或 input path 不存在都直接停止；不得 fallback 到 legacy table、假 `CN=2` 或單點 multiplicity。

## 4. QA 與實驗 gate

### 4.1 Input gate

- site key 唯一，reference build、contig、1-based VCF position 與 REF/ALT 一致。
- builder/QA驗證 `bulk_depth=bulk_ref+bulk_alt` 與原始完整 HP categories的count conservation；sampler loader只讀HP1-1/HP2-1並檢查其子集合不超過bulk，剩餘counts視為untagged。
- `major_cn>=minor_cn>=0`、`total_cn=major_cn+minor_cn`；eligible rows 必須 `total_cn>0`。
- `multiplicity_prior` 的 support 合法、非負且總和為 1。
- table 與 manifest 的 `rho_ASCAT=0.99`、sample、ASCAT source/hash 一致。
- PS read audit通過 `discordance_fraction<=0.01`；PS 不得出現在 downstream likelihood schema，但其上游產生的 HP counts 必須在 canonical table 中。
- 任一 gate fail：停止、回傳非零 exit、建立 `_FAILED`，不得建立 `_SUCCESS`。

### 4.2 Deterministic 20-site fixture

smoke fixture固定為：

- 16 個 eligible sites。
- 2 個 `CN=0`、2 個 `unmapped_segment` exclusion cases。
- 涵蓋 diploid、CN gain、CN=1、LOH-like、HP1、HP2 與 missing HP。
- selection seed：`hcc1395_tp20_v1`；以 `SHA256(seed|mutation_id)` 決定 strata 內順序。
- `fixture_manifest.json` 保存來源 hash、20 個 mutation IDs、strata 與預期 gate 結果。

Smoke 只驗證 schema、排除規則、prior 與短鏈 I/O，不判斷收斂或生物學 recovery。

## 5. 推理演算法與 root 定義

### 5.1 Inference algorithm contract

每條 chain 由 `inference/` 的 C++17 finite-K PhyloWGS-inspired compound MCMC
backend 執行。其 algorithm identity、state transition、`ChainConfig`、輸出
artifact 與目前 `eta` proposal correctness audit，統一記錄在
[`inference_algo.md`](inference_algo.md)。本 workflow 只負責把已驗證的 canonical
table、holdout control 與 workflow config 交給 backend，不在此重複定義 sampler
kernel。

模型 posterior target、`T/z/eta/phi` 的意義、ASCAT purity、HP observation 與
CN-only multiplicity prior 見 [`model.md`](model.md)。PS 仍只透過上游產生的 HP
counts 間接影響 downstream observation；PS block 不直接進 sampler state 或
topology edge constraint。

### 5.2 單條 chain 的輸出

每條 chain 完成後產生四個主要資料 artifact，另有一個完成狀態檔：

- `samples.jsonl.gz`：burn-in 後 retained draws 的 `iteration`、`log_posterior`、`parents`、`eta`、`phi`、`occupancy`。
- `checkpoint.json.gz`：目前 `(T, eta, z)`、RNG state、iteration、retained draws、canonical table hash、ChainConfig 與 holdout IDs，作為 audit/state snapshot 與未來 versioned restore 的基礎；目前不接受 C++ resume。
- `diagnostics.json`：schema/input hash、ChainConfig、proposal counters、acceptance rates、posterior sample摘要與輸入角色。
- `representative_tree.json`：由 retained draws 選出的代表 tree、best sample，以及每個 SNV 的 assignment aggregate/MAP node。
- `chain_complete.json`：chain 完成狀態與已發布 artifact 清單。

PS 不會以欄位直接傳入這個 downstream sampler。它在 LongPhase-S 上游 phase/tagging 階段協助產生 `H_i`，所以影響會經由 canonical table 的 HP counts 傳遞；PS block 本身不進 state，也不限制 tree edge。

### 5.3 單條 chain 與外層 convergence check

單條 chain 只產生一條 posterior sample stream。外層 workflow 才用相同 canonical table/config、不同 seed 啟動多條獨立 compound-MCMC chains，並計算 rank-normalized R-hat、bulk/tail ESS、label-invariant assignment agreement、edge support 與 holdout predictive metrics。多條 chain 是 convergence check 的執行包裝，不是把單條 sampler 改成另一種推理演算法。

## 6. 唯一正式 wrapper

正式入口是 `python3 -m tumor_tree_pipeline`；舊 `run_m3_experiment_loop.py`、`run_stage6_production.py` 與舊 sampler command只作歷史除錯／比較，不得產生正式 `_SUCCESS`。

```bash
# example JSON內的/absolute/path/to/...必須先替換成新表、manifest與audit實體路徑。
# 先驗證設定並顯示dependency-ordered matrix
python3 -m tumor_tree_pipeline plan \
  --config tumor_tree_pipeline/configs/formal.example.json

# 正式執行immutable、fail-closed workflow
python3 -m tumor_tree_pipeline run \
  --config tumor_tree_pipeline/configs/formal.example.json
```

wrapper contract：

- 成功run不可覆寫；C++ backend 對失敗／中斷 chain 不支援原地接續，必須建立新 output directory。已完成 chain 可在 workflow resume 時被重新讀取，但不代表 sampler restore。
- `flock` 保護 run directory；寫入 temporary file 後 atomic rename。
- 每條chain定期原子寫入 checkpoint；若未來啟用 versioned restore，必須先核對 table hash、chain config 與 holdout IDs。目前 `--resume` 會明確拒絕未完成 C++ checkpoint。
- formal/all拒絕dirty worktree；啟動時保存exact command、schema version、Git commit/state與input hashes。
- 任一 input、simulation、holdout 或 convergence gate fail 時回傳非零 exit並建立 `_FAILED`。
- 只有所有正式gate通過後，最後原子建立`artifact_inventory.json`與`_SUCCESS`。
- directory mode `2775`、一般 artifact `664`；group 使用實際存在的研究群組。

```text
output/tumor_tree_pipeline/<run_id>/
├── command.json
├── command_ledger.json
├── status.json
├── manifest.json
├── input_validation.json
├── prerequisites.json
├── run.lock
├── logs/
├── input/                         # wrapper建表時建立
├── input_sensitivity/rho_*/
├── holdouts/{ps,chromosome,ascat_segment}/
├── runs/<stage_run_id>/<holdout>/
│   ├── chain_01/
│   │   ├── samples.jsonl.gz
│   │   ├── checkpoint.json.gz
│   │   ├── diagnostics.json
│   │   └── representative_tree.json
│   └── ...
└── _SUCCESS | _FAILED
```

## 7. Staged experiment matrix

依 early-stop 執行，不一次展開所有昂貴組合。

1. **Smoke**：20-site fixture，僅驗證 I/O 與契約。
2. **Synthetic prerequisite**：外部 simulation流程先產生並通過manifest；本wrapper只驗證manifest與hash，不會自行模擬資料。
3. **HCC pilot**：`K=4,6,8`，各 4 條獨立 compound-MCMC chains；pilot R-hat `<=1.10` 只用來決定是否延長，不是正式通過。
4. **Full K=6**：先跑主設定；通過後才追加 `K=4,8` sensitivity。
5. **Purity sensitivity**：主分析 `0.99` 通過後，再跑 `0.97`、`0.95`；各設定分別報告 occupied clones、CCF、assignment、edge support 與 predictive score。

正式長鏈的起始下限：

```text
independent chains = 4
iterations = 1500
burnin = 1000
thin = 1
retained draws >= 500 per chain
```

ESS 不足時延長至每鏈至少 1,000 retained draws；不能因固定 iterations 跑完就宣稱通過。

## 8. 正式判讀標準

- rank-normalized split/folded R-hat `<1.01`。
- bulk ESS total `>=400`、tail ESS total `>=400`。
- label-invariant assignment agreement `>=0.90`。
- 每個K內跨chain的max edge-support difference `<=0.10`；K=4/6/8另列sensitivity，目前不宣稱已有cross-K gate。
- strict holdout 90% predictive coverage在 `0.85–0.95`，並報告 predictive log score。
- simulation recovery 與最差 replicate 必須通過預先登錄門檻；topology recovery個別報告，不得把一般 computational pass改稱「tumor-tree truth recovered」。

任一正式標準未通過，結果標記為 `candidate—not converged`，wrapper回傳非零 exit。

歷史 baseline（不是 ASCAT 0.99 新流程結果）：最大 label-invariant R-hat `24.983`、最低 ESS/chain `3.1`。這兩個數字只能用來說明舊 run 未收斂。

## 9. Git 與 artifact 保存

Git 保存：

- `tumor_tree_pipeline/` 的 modules、CLI、tests、configs與20-site fixture。
- workflow、exact command、schema、manifest、QA／diagnostic summary、代表樹與小型可讀表。
- 大型來源檔的 path、metadata與 hash。

Git 不保存大型 BAM、完整 MCMC samples或可重建的大型中間表。正式 manifest／summary不可被 `output/.gitignore` 一併隱藏；大型 artifact則由 manifest指向外部 immutable storage。

## 10. 歷史相容性聲明

2026-08-15 的舊 integrated table曾保存 `multiplicity_posteriors`，而且該欄位使用相同 bulk counts形成權重；舊 sampler之後又用這批 counts計算 likelihood。這個設計可能重複使用觀測，**不得作為新版正式輸入**。

歷史 Stage 6、production-like與experiment-loop輸出可留作 provenance，但不代表本流程的 posterior。新版正式表只能含 CN-only `multiplicity_prior`，且只能由 `tumor_tree_pipeline` wrapper產生與驗收。
