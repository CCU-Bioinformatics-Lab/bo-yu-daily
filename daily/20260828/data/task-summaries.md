# 2026-08-28 任務摘要

## 蒐集範圍

- 日期：2026-08-28（Asia/Taipei）。
- 來源：`session-manifest.json` 對應的 31 個 Codex rollout entries；依 root session 去重後為 3 個工作串。
- 摘要以完整 transcript 為主；UTC 紀錄轉為台北時間。日誌產生、建置與檢查本身不列為研究任務。
- 下列是依實質產出與決策去重後的任務，不是逐輪對話清單。

## 去重後任務

| ID | 任務 | 產出／決策 | 狀態 | 主要證據 |
| --- | --- | --- | --- | --- |
| T1 | 模型文件迭代與精簡 | 將 `module_format.md` 的數學表達改成 VS Code 可渲染的 LaTeX；依後續需求移除完整 likelihood／prior／posterior 詳解與單一 SNV 範例，保留模組邊界及簡短 Model purpose。 | 完成 | `module_format.md`；`codex:01a046eb-1aa6-7691-89d1-479ca9491de5` |
| T2 | `eta`、CCF／`phi` 與 `clonal prevalence` 語意同步 | 專案採用 `clone-specific local fraction (eta_v)`；`eta_v` 只代表 clone 自身，CCF／`phi_v` 維持含後代的累積比例；不把 `clonal prevalence` 當作專案 canonical term。 | 定案 | `CONTEXT.md`、`model.md`、`inference_algo.md` 等 13 個 active Markdown；3 個 root session |
| T3 | `eta` 符號文獻查核 | 整理 PhyloSub／PhyloWGS、TSSB、PhyClone 與 Pairtree 的符號與語意；結論是 `eta` 有先例但不是跨方法的 universal notation。 | 完成 | `research/eta_symbol_literature.md`; `codex:01a046eb-1aa6-7691-89d1-479ca9491de5` |
| T4 | 候選腫瘤演化樹 state 與 `T + eta -> phi` 設計 | 以「可能答案卡」說明候選樹 `T` 與 local mass `eta`，再由樹的後代關係決定 `phi`；確認此結構是多篇方法的交集與本 repo 的 hybrid design，沒有單一論文逐字規定完整實作。 | 釐清 | `research/t_eta_design_review.md`; `algorithm.cpp`、`inference_algo.md` |
| T5 | multiplicity latent variable 與 CNV timing 決策 | 決定 multiplicity 留在 likelihood 內 marginalize，不作持久 candidate-tree state；區分 mutation-before-CNV／mutation-after-CNV；輸出每個 SNV 的全域 multiplicity posterior；CCF／`phi` 定義保留，疑似 mutation-loss 先標為 outlier（精確規則尚未實作）。 | 定案 | `research/multiplicity_latent_variable_review.md`; `docs/adr/0001-multiplicity-emission-and-cnv-timing.md` |
| T6 | PhyClone／PyClone-VI `xi` emission 查核 | 確認 PyClone-VI 是完整的 genotype-aware CCF inference，不是單純 VAF→CCF 轉換；採用其 copy-number／purity／multiplicity-aware expected ALT probability `xi` 作為 active target，保留 `q_repo` 作 baseline。 | 定案 | `research/phyclone_pyclone_vi_q4_review.md` |
| T7 | 套用 copy-number-aware、PhyClone/PyClone-VI-style VAF 計算 | C++ 與 Python 同步加入 genotype candidate、mutation timing、expected ALT probability 與 multiplicity posterior；diagnostics 標註 `phyclone_xi_v1`、`synced`，multiplicity 以 Rao–Blackwellized responsibility 處理。 | 完成 | commit `4138d59`; `inference/src/model.cpp`; `tumor_tree_pipeline/model.py` |
| T8 | tumor-evolution model definitions crosswalk 與 prediction 邊界 | 整理 13 個方法，區分 generative/posterior、constraint/optimization、clustering/emission；釐清 repo 的 model 負責用 canonical SNV evidence 評分候選 configuration，prediction rule 已有 xi／Binomial，但正式 predictive artifact／gate 仍未完成。使用者決定精簡 HTML 先不展開 prediction rule。 | 定案 | `research/tumor_evolution_model_definitions_review.md`; `validation.md`; `codex:01a047b9-ba56-7362-bab0-fc89810a558c` |
| T9 | 變更收斂與 provenance commit | 將當日模型、文件、research notes、測試與 ADR 變更收斂成 `4138d59 feat: synchronize copy-number-aware tumor-tree model`；未 push。 | 完成 | `git show --stat 4138d59`; `codex:01a046eb-1aa6-7691-89d1-479ca9491de5` |

## 驗證摘要

- C++ debug smoke、C++ black-box contract、Release build／smoke／contract：PASS。
- Python workflow tests：48/48 PASS。
- `git diff --check`：PASS。
- 仍不能把上述測試等同於正式 predictive validation；目前缺少 per-SNV `predicted_xi` artifact 與完整 predictive gate。
