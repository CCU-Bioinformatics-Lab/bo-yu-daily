# 研究索引

跨研究共用名詞先查 [研究共用術語](CONTEXT.md)；統一寫法、ASD-STE100 風格與來源範圍見 [術語使用指南](TERMINOLOGY.md)。

| 主題 | 入口 | 內容 |
|---|---|---|
| **論文分類（平台 × single-cell 真值）** | [分類索引](literature/PAPER_CATEGORIES.md) | 19 篇分 C1 短讀／未說平台、C2 long-read 特徵、C3a／C3b single-cell 真值 × 平台；每篇 README 有可 grep 的 front-matter；`literature/papers_by_category/` 依類瀏覽 |
| 腫瘤演化樹重建**方法**（2019–2026） | [方法調查](literature/surveys/methods_survey/README.md) | 45 個推論 topology 的方法，分 bulk／single-cell／CN／多模態／read-level 連鎖；novelty 邊界與評估指標 |
| 腫瘤演化樹：病人 single-cell 與 long-read／haplotype 特徵 | [2026 文獻調查](literature/surveys/patient_sc_longread_2026/README.md) | A 類 5 篇、B 類主選 4 篇、補充 2 篇；逐篇 PDF／閱讀筆記、證據分級、資料取得與本 repo 改進方案 |
| 文獻去重與 PhyClone × longphase-s 整合地圖 | [整合地圖](literature/SYNTHESIS_phyclone_longphase.md) | 檔案層級重複、12 條跨論文收斂約束（對應 C0–C6）、每篇唯一貢獻、過時內容 |
| PhyClone HGSOC 真值樹來源 | [McPherson 2016 dossier](literature/papers/R01_mcpherson_hgsoc_2016/README.md) | 單核 targeted PCR＋SCG＋stochastic Dollo 如何建樹；與 benchmark `tree.json` 的對應及 p2 loss 被剝除的觀察 |
| PhyClone 模型與實作 | [中文版來源地圖](phyclone_research/notes/zh-TW/00_SOURCE_MAP.md) | 模型、推理、實驗、code mapping、假設與限制 |
| HP 特徵接進 PhyClone（設計） | [HP_EXTENSION_DESIGN.md](phyclone_research/HP_EXTENSION_DESIGN.md) | 單一 bulk 樣本；A1 HP 拆分 emission、A2 loss-aware emission、B read 共現 pairwise 項 |
| PhyClone 模擬資料生成流程 | [模擬流程研究](simulation_pipeline_research/README.md) | 論文的 generative model 與 benchmark 生成方式、`fscrp.py`／`sim_data_on_tree.py` 實際行為（樹形偏向、CN 逐 sample 獨立抽）、benchmark 真值格式、加入 HP 特徵的缺口；其他真值樹＋SNV 模擬器總調查（`simulator_survey_2026-10-24/`） |
| HCC1395 參考演化樹 | [既有文獻分析](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md) | bulk 推理與 single-cell CNV 驗證的證據邊界；不能視為病人 lineage ground truth |

| 會議紀錄 | [2026-10-21 會議整理](meeting_record/2026_10_21_meeting_summary.md) | 會議原始紀錄（語音辨識整理）與會後整理、未決事項 |

文獻目錄結構見 [literature/README.md](literature/README.md)。新增調查保留既有研究內容；實際輸入與開發設計仍分別以 repo 的 `data_input.md`、`plan.md` 為準。
