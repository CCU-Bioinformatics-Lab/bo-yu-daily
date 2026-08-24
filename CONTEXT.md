# Tumor-tree research vocabulary

## Core modules

- **data input**：把原始資料整理成 model 可以讀取的資料介面。
- **model**：定義觀測資料、latent state、likelihood 與輸出參數的語意。
- **inference_algo**：根據 model 推理未知參數的方法；目前使用 SMC。
- **output**：呈現 topology、CCF/phi 與 SNV-to-clone assignment。
- **validation**：只讀取 output 與相關證據，檢查結果可靠性及 claim ceiling。

## Validation terms

- **bulk compatibility**：候選 topology 與 bulk counts、ASCAT purity、CN、LOH 或 ploidy pattern 相容；不等於 branch-level proof。
- **external orthogonal evidence**：沒有被目前 likelihood 使用、可獨立支持同一 claim 的外部證據。
- **claim ceiling**：目前 evidence 允許使用的最高研究敘述，不能超過證據強度。
- **candidate branching topology**：模型與驗證支持的候選分支樹；不是唯一真實腫瘤歷史，也不是 single-cell lineage truth。
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
