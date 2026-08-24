# bo-yu-daily

目前 repo 的研究輸入、模型、推理與輸出文件：

- [arch.md](arch.md)：整體研究架構；說明 `data input`、`model`、`inference_algo`、`output` 與 `validation` 的文件引用與資料流向
- [data.md](data.md)：canonical data/provenance
- [model.md](model.md)：model specification（posterior、likelihood、prior 與 latent quantities）
- [inference_algo.md](inference_algo.md)：目前 Rao–Blackwellized annealed SMC 的推理流程、particle state、ESS/resampling、rejuvenation 與 backend input/output contract
- [output.md](output.md)：模型輸出解讀；集中說明 clone topology、由 `phi` 表示的 CCF，以及每個 SNV 被分配到哪個 clone，並提供三-clone ASCII 示意圖
- [validation.md](validation.md)：output 後的獨立、read-only validation；整合 SMC adequacy、topology/CCF/SNV assignment、bulk CN/LOH compatibility、optional CNV/driver evidence 與 claim ceiling
- [experiment_workflow.md](experiment_workflow.md)：整合 `arch.md` 核心模塊的實驗執行、QA、分階段 gate 與錯誤追蹤紀錄流程
- [tumor_tree_pipeline/](tumor_tree_pipeline/)：正式、可版本控制的建表、Python workflow 與 gate wrapper
- [inference/](inference/)：active C++17 finite-K annealed SMC backend，提供 AlgorithmRegistry、repeat/site 平行化與 particle artifacts（包含每個 SNV 的 multiplicity posterior）
- `daily/`：每天產生的 HTML的相關資料和每日總結。

建議文件閱讀順序是 `arch.md` → `data.md` → `model.md` → `inference_algo.md` → `output.md` → `validation.md`：
先從 `arch.md` 掌握模塊分工與連線，再確認資料表、posterior model、推理演算法與模型輸出，最後用 `validation.md` 驗證輸出能支持到哪一層研究 claim。
