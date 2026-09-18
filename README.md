# bo-yu-daily

目前 repo 的研究輸入、模型、推理與輸出文件：

- [ARCHITECTURE.md](ARCHITECTURE.md)：整體研究架構；說明 `data input`、`model`、`inference_algo`、`output` 與 `validation` 的文件引用與資料流向
- [data.md](data.md)：canonical data/provenance
- [model.md](model.md)：model specification（posterior、likelihood、prior 與 latent quantities）
- [inference_algo.md](inference_algo.md)：目前 Rao–Blackwellized annealed SMC 的推理流程、PhyClone-inspired local SPR/global tree moves、particle state、ESS/resampling、rejuvenation 與 backend input/output contract
- [output.md](output.md)：模型輸出解讀；集中說明 clone topology、clone-specific local fraction ($\eta_v$)，以及由 $\phi_v$ 表示的 CCF（clone 加上 descendants 的 cumulative tumor-cell fraction），並提供三-clone ASCII 示意圖
- [validation.md](validation.md)：output 後的獨立、read-only validation；整合 SMC adequacy、PhyClone `xi`／VAF predictive check、topology/CCF/SNV assignment、bulk CN/LOH compatibility、optional CNV/driver evidence 與 claim ceiling
- [daily/](daily/)：每天產生的 HTML的相關資料和每日總結。
