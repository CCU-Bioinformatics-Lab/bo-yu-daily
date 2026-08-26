# PhyClone research bundle

這個目錄保存 PhyClone 論文、supplementary material、官方程式碼，以及根據 primary sources 整理的研究筆記。

## 入口

- [SOURCES.md](SOURCES.md)：來源、下載日期、local artifact 與 commit/hash provenance。
- [phyclone_paper_notes.zh-TW.md](phyclone_paper_notes.zh-TW.md)：論文的問題定義、資料輸入、模型、推理、輸出與整體流程。
- [phyclone_code_notes.zh-TW.md](phyclone_code_notes.zh-TW.md)：官方 GitHub 程式碼與 workflow 的檔案級對照。
- [phyclone_validation_notes.zh-TW.md](phyclone_validation_notes.zh-TW.md)：code correctness、synthetic/real benchmark、metrics、統計檢定與 limitations。
- [phyclone_q_formula_comparison.zh-TW.md](phyclone_q_formula_comparison.zh-TW.md)：PhyClone `xi` 與目前 repo `q`／VAF emission 的公式、程式與數值比較。
- [phyclone_long_read_usage.zh-TW.md](phyclone_long_read_usage.zh-TW.md)：PhyClone 是否直接使用 ONT／PacBio long-read、BAM、phase 或 read-level 資訊的輸入與 source code 核對。
- [phyclone_eli5_flow.spec.json](phyclone_eli5_flow.spec.json)：Fireworks Open ELI5 的可驗證流程規格。
- [phyclone_eli5_flow.html](phyclone_eli5_flow.html)：離線互動式繁體中文視覺解說。

## 已保存的原始材料

- `PhyClone_paper.pdf`：Bioinformatics 正式論文。
- `PhyClone_paper.xml`：Europe PMC 結構化全文，方便追溯 section、figure、data/code availability。
- `paper_supplement/content/supp.pdf`：Supplementary Methods、implementation details、correctness tests 與 supplementary figures/tables 說明。
- `paper_supplement/content/*.xlsx`：supplementary benchmark metrics 與 Friedman–Nemenyi 結果表。
- `PhyClone/`：官方 PhyClone GitHub repository 的 shallow clone。
- `PhyClone-Workflow/`：官方 PyClone-VI → PhyClone Snakemake workflow 的 shallow clone。

## 一句話總結

PhyClone 把多個 bulk tumour sample 的 SNV allele counts、copy-number context 與 tumour content，放進 PyClone emission + FS-CRP tree prior，透過 collapsed prevalence marginalisation 與 Particle-Gibbs SMC 探索 clone tree posterior，再以 MAP、consensus、topology report 與 benchmark/correctness tests 交付結果。

## 閱讀注意

這份 bundle 分開標示：

1. 論文直接宣稱的內容；
2. 官方 source code 實際執行的內容；
3. 根據兩者對照得到的 inference 或研究建議。

不要把 PhyClone 的 `error_rate`、`tumour_content`、Beta-Binomial precision、outlier prior 或 cluster file 當成目前 repo 的 v4 canonical input contract；本 bundle 是方法研究資料，不會自動修改主 repo 的 inference backend。
