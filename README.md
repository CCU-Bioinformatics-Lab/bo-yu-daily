# bo-yu-daily

目前 repo 的研究輸入與模型文件：

- [data.md](data.md)：canonical data/provenance
- [model.md](model.md) model specification
- [ascat_purity_experiment_workflow.md](ascat_purity_experiment_workflow.md)：ASCAT purity=0.99 的新輸入重跑流程
- [tumor_tree_pipeline/](tumor_tree_pipeline/)：正式、可版本控制的建表、Python workflow 與 gate wrapper
- [inference/](inference/)：active C++17 plain-MH backend，提供 AlgorithmRegistry、chain/site 平行化與五個 inference artifacts
- `daily/`：每天產生的 HTML的相關資料和每日總結。

## 目前推理基線

目前先使用最簡單的 plain finite-K Metropolis-Hastings baseline。每條 chain
只從 canonical SNV table 讀取觀測資料，對有限 K 的樹、SNV clone assignment
與 prevalence `eta` 做單一 MH proposal kernel；state update 由 `inference/` C++17
backend 執行，Python 只做 workflow orchestration 與 diagnostics。

```text
canonical SNV table + ChainConfig
        │  bulk / HP / ASCAT CN / multiplicity prior / rho_ASCAT=0.99
        ▼
latent state: topology T + assignment z + prevalence eta
        │  plain finite-K MH accept/reject
        ▼
posterior samples + diagnostics + representative tree + checkpoint
```

PS 是 LongPhase-S 的上游 phasing metadata：它協助形成一致的 HP labels/counts，
因此會間接影響每個 SNV 的 `H_i`。建表完成後，PS 不直接作 downstream
likelihood 欄位、clone-assignment prior 或 topology edge constraint；它仍可用於
read-level provenance、audit 與 grouped holdout。
