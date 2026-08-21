# bo-yu-daily

目前 repo 的研究輸入、模型、推理與輸出文件：

- [data.md](data.md)：canonical data/provenance
- [model.md](model.md)：model specification（posterior、likelihood、prior 與 latent quantities）
- [inference_algo.md](inference_algo.md)：inference algorithm specification；說明如何以目前 finite-K compound MCMC 從 model posterior 推理 `T`、`eta` 與 SNV assignment `z`，以及可替換 backend 的 input/output contract
- [output.md](output.md)：模型輸出解讀；集中說明 clone topology、由 `phi` 表示的 CCF，以及每個 SNV 被分配到哪個 clone，並提供三-clone ASCII 示意圖
- [ascat_purity_experiment_workflow.md](ascat_purity_experiment_workflow.md)：ASCAT purity=0.99 的新輸入重跑流程
- [tumor_tree_pipeline/](tumor_tree_pipeline/)：正式、可版本控制的建表、Python workflow 與 gate wrapper
- [inference/](inference/)：active C++17 finite-K compound MCMC backend，提供 AlgorithmRegistry、chain/site 平行化與五個 inference artifacts
- `daily/`：每天產生的 HTML的相關資料和每日總結。

文件閱讀順序是 `data.md` → `model.md` → `inference_algo.md` → `output.md`：
先確認資料表，再確認 posterior model，接著確認推理演算法，最後解讀模型輸出。
