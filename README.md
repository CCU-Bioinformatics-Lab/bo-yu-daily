# bo-yu-daily

目前 repo 的研究輸入、模型、推理與輸出文件：

- [arch.md](arch.md)：整體研究架構；說明 `data input`、`model`、`inference_algo` 與 `output` 四個可替換模塊，以及它們之間的文件引用與資料流向
- [data.md](data.md)：canonical data/provenance
- [model.md](model.md)：model specification（posterior、likelihood、prior 與 latent quantities）
- [inference_algo.md](inference_algo.md)：inference algorithm specification；說明如何以目前 finite-K compound MCMC 從 model posterior 推理 `T`、`eta` 與 SNV assignment `z`，以及可替換 backend 的 input/output contract
- [output.md](output.md)：模型輸出解讀；集中說明 clone topology、由 `phi` 表示的 CCF，以及每個 SNV 被分配到哪個 clone，並提供三-clone ASCII 示意圖
- [support.md](support.md)：output 後的獨立 support evaluator 規格；依序驗證 topology、CCF/`phi` 與 SNV→clone assignment，並檢查推理可靠性、ASCAT/CN/LOH compatibility、holdout、topology stability 與最終 claim grade。CNV event→node 與 driver annotation 在此列為 optional evidence，不會直接加入模型 likelihood
- [experiment_workflow.md](experiment_workflow.md)：整合 `arch.md` 四個模塊的實驗執行、QA、分階段 gate 與錯誤追蹤紀錄流程
- [tumor_tree_pipeline/](tumor_tree_pipeline/)：正式、可版本控制的建表、Python workflow 與 gate wrapper
- [inference/](inference/)：active C++17 finite-K compound MCMC backend，提供 AlgorithmRegistry、chain/site 平行化與六個 inference artifacts（包含每個 SNV 的 multiplicity posterior）
- `daily/`：每天產生的 HTML的相關資料和每日總結。

建議文件閱讀順序是 `arch.md` → `data.md` → `model.md` → `inference_algo.md` → `output.md` → `support.md`：
先從 `arch.md` 掌握四個模塊的分工與連線，再確認資料表、posterior model、推理演算法與模型輸出，最後用 `support.md` 驗證輸出能支持到哪一層研究 claim。
