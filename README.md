# bo-yu-daily

目前 repo 的研究輸入與模型文件：

- [data.md](data.md)：canonical data/provenance
- [model.md](model.md) model specification
- [ascat_purity_experiment_workflow.md](ascat_purity_experiment_workflow.md)：ASCAT purity=0.99 的新輸入重跑流程
- [tumor_tree_pipeline/](tumor_tree_pipeline/)：正式、可版本控制的建表、Python workflow 與 gate wrapper
- [inference/](inference/)：active C++17 plain-MH backend，提供 AlgorithmRegistry、chain/site 平行化與五個 inference artifacts
- `daily/`：每天產生的 HTML的相關資料和每日總結。
