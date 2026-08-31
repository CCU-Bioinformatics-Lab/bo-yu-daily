# Tumor-tree research vocabulary

## Core modules

- **data input**：把原始資料整理成 model 可以讀取的資料介面。
- **model**：定義 model features、candidate latent state、likelihood，以及 topology、CCF/phi 和 SNV-to-clone assignment 的語意；不負責搜尋整個 tree space。
- **inference_algo**：根據 model 推理未知參數的方法；目前使用 SMC。
- **output**：呈現 topology、CCF/phi 與 SNV-to-clone assignment。
- **validation**：只讀取 output 與相關證據，檢查結果可靠性及 claim ceiling。

## Validation terms

- **bulk compatibility**：候選 topology 與 bulk counts、ASCAT purity、CN、LOH 或 ploidy pattern 相容；不等於 branch-level proof。
- **external orthogonal evidence**：沒有被目前 likelihood 使用、可獨立支持同一 claim 的外部證據。
- **claim ceiling**：目前 evidence 允許使用的最高研究敘述，不能超過證據強度。
- **candidate branching topology**：模型與驗證支持的候選分支樹；不是唯一真實腫瘤歷史，也不是 single-cell lineage truth。
- **candidate tumor-evolution hypothesis**：在固定 model assumptions 下，由 tree topology `T` 與 clone-specific local fraction `eta` 組成的一個候選 latent state；inference 比較這些候選狀態，不會在同一次推理中自行修改 model assumptions。
- **optional evidence layer**：CNV event-to-node、driver annotation、single-cell lineage 等非目前核心 output 的補充證據。

## Architecture decisions

1. `validation.md` 是唯一的 output support / evidence evaluator 規格；不再維護獨立的 `support.md`。
2. validation 位於 output 之後，是 read-only 評估模組，不回寫 model、inference 或 output。
3. bulk CN/LOH/purity 可支持 compatibility，但不能自動升級成 branch-level proof。
4. 缺少 CNV event-to-node、driver mapping 或 joint single-cell SNV+CN evidence 時，對應 claim 保持 `UNKNOWN`。

## Experiment lifecycle terms

- **interrupted run**：實驗被外部中止，尚未完成所有 requested stages；它不是成功結果，也不是 sampler biological failure。
- **stale run**：紀錄顯示仍在執行，但 heartbeat 已過期且原 process 不存在的未完成實驗。
- **quick pilot**：用較小的 K、particle 數、annealing stages 與 repeat 數，先確認完整資料流程能跑通；不取代完整 pilot 或 formal result。

## Data and model terms

**SNV evidence row**：每顆 SNV 一列，合併 read evidence、purity、copy-number context 和 eligibility，供 model 使用。
_Avoid_: raw BAM row, clone assignment

**read evidence**：同一顆 SNV 的 REF/ALT read counts；`total_reads` 是兩者的和。
_Avoid_: observed lineage

**copy-number context**：SNV 所在位置的 major/minor/total CN 與 LOH state。它描述 bulk compatibility context，不直接代表 evolutionary branch event。
_Avoid_: CNA event, clone branch

**purity / `rho_ASCAT`**：整個樣本的 tumor fraction。它不是某個 clone 的 CCF。
_Avoid_: clone purity, CCF

**CCF / `phi`**：在 candidate branching topology 中，一個 clone 加上 descendants 的累積 tumor-cell fraction。
_Avoid_: purity, observed VAF

**SNV-to-clone assignment**：一顆 SNV 對 candidate clone 的模型支持關係，通常保留不確定性；它不是直接觀察到的 lineage proof。
_Avoid_: confirmed lineage

**multiplicity**：在 copy-number context 下，帶有某個 SNV 的 mutated-copy 數量候選；它不是 total copy number、CCF、canonical input，也不是 ASCAT 直接量測值。它可以在模型中作為固定輸入、latent state，或在 allele-count emission 中被邊際化；它本身不等於 tree topology。
_Avoid_: ASCAT multiplicity

## Statistical model terms

**Observation**：一顆 SNV 實際觀察到的 REF/ALT read counts，以及該 SNV 的 copy-number 與 purity context。

**Likelihood**：在一個指定的 tree、clone-specific local fraction、clone assignment 與 multiplicity 解釋下，觀察到目前 read counts 的機率。

**Prior**：在尚未使用目前 SNV read counts 前，對 tree、clone-specific local fraction、assignment 或 multiplicity 的機率／權重假設。

**Posterior**：將 observation 的 likelihood 與 prior 結合後，對候選 tree、clone-specific local fraction 及其 latent interpretation 更新出的不確定性分布。

**Tree topology**：candidate tumor clones 之間的 rooted parent-child ancestry 關係。

**clone-specific local fraction ($\eta_v$)**：只屬於某個 clone、且不包含 descendants 的 tumor-cell fraction；所有 clone-specific local fractions 為正並加總為 1。

本 repo 使用 $\eta_v$ 這個命名有 PhyloSub／PhyloWGS 的先例，但這是 project notation，不是所有 tumor-tree model 的 universal symbol。

**Cumulative tumor-cell fraction (`phi`／CCF)**：某 clone 的 clone-specific local fraction 加上所有 descendants 的 clone-specific local fractions 總和；每個 $\phi_v$ 都由 tree topology `T` 與 clone-specific local fraction vector $\eta$ 推導，不是獨立觀察值。

**Clone assignment (`z`)**：把一顆 SNV 對應到某個 candidate clone 的 latent state。

**Multiplicity prior (`pi_i(m)`)**：由第 `i` 顆 SNV 的 major/minor CN 建立、且在該 SNV candidate support 上正規化的 multiplicity 初始權重。

**Working prior**：為了 finite-K inference 而指定的可檢驗先驗；它是模型假設，不是從 HCC1395 直接量測出的 biological truth。

**Rao–Blackwellized marginalization**：不把 assignment 或 multiplicity 當作 particle 維度，而是在 likelihood 中對它們的可能值加權求和，並從 conditional responsibility 產生 posterior summary。
