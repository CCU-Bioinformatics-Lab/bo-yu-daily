# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 研究目標

這是專門研究**腫瘤演化樹（tumor phylogeny / clonal evolution tree）重建**的研究目錄。主軸是：

1. 以 **PhyClone**（Roth-Lab，bulk SNV + CN 的 clone tree 推理，Particle Gibbs/SMC）為基線，分析並改善其模型與推理。
2. 加入 **long read 才有的特徵**，特別是 **longphase-s 產生的 haplotype（HP1/HP2 phasing）** 資訊，例如 phased reads 上 SNV 與 haplotype／allele-specific CN 的對應、同一 read 上多個 SNV 的共現關係，用來約束 multiplicity、CNV timing、clone assignment 與 topology。

資料是 ONT 腫瘤細胞株（HCC1395、COLO829、H1437、H2009、HCC1937、HCC1954）的 alignment，已由 BAM 轉成 **CRAM**（reference：`/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`）。每株有多個 nominal purity 的 subsample（`tX_nY`），詳見 `tumor_sample.md`。注意：`tX_nY` 的百分比是 design tumor fraction，**不是**實測 purity ground truth；`t00_n25` 是純 normal baseline。


## 目錄結構

- `research/literature/`：**找論文先看這裡**。所有文獻集中在這裡，結構見 `research/literature/README.md`。
  - `papers/`：19 篇逐篇筆記（A01–A05、B01、B03–B05、B07、B09、M01、M02、M04–M08、R01），一篇一個目錄。第 20 篇 HCC1395 golden tree（H01）仍放在 `research/hcc1395_golden_tree_research/`。
  - `PAPER_CATEGORIES.md`：分類索引。20 篇依「定序平台 × single-cell 真值」分成 C1（短讀／未說平台）、C2（long-read 特徵輔助建樹）、C3a／C3b（single-cell 真值樹 × 短讀／long read）。總表是 `paper_categories.tsv`（唯一來源）；每篇 README 頂端有單行 YAML front-matter，可直接 `grep -rl '^category: "C2"' --include=README.md research/`；`papers_by_category/` 是依類的 symlink 目錄。改分類時只改 TSV，再跑 `python3 research/literature/tools/sync_paper_categories.py`（`--check` 檢查 drift）。
  - `surveys/`：各次文獻調查的摘要與搜尋紀錄（`patient_sc_longread_2026/`、`methods_survey/`、`longread_tree_search_2026-10-19/`）。論文本體一律放 `papers/`，調查只放摘要。
  - `SYNTHESIS_phyclone_longphase.md`：跨論文整合地圖。
- `research/meeting_record/`：會議紀錄與會後整理。
- `tumor_sample.md`：樣本／CRAM 路徑盤點（`/big8_disk/data/<cell line>/ONT*/subsample/<purity label>/<line>_<purity label>.cram`；部分舊 `.bam` symlink 已失效，以該檔為準），以及 PhyClone benchmarking 資料集（`/big8_disk/boyu114/phyclone_dataset/`）。
- `research/phyclone_research/`：PhyClone 論文分析。
  - `PhyClone/`：上游 PhyClone 原始碼，是 **git submodule**（`https://github.com/Roth-Lab/PhyClone.git`），改動要在 submodule 內另外 commit。
  - `notes/`（`zh-TW/` 是中文版）：`00_SOURCE_MAP` 到 `07_PRESENTATION_BRIEF`，涵蓋論文全貌、方法、實驗、code mapping、evidence matrix、假設與限制。要了解 PhyClone 時優先讀這裡，再回頭查原始碼。
  - `RESEARCH_PLAN.md`：分析規範。分析 PhyClone 時，讀取範圍限制在 `research/phyclone_research/` 內，並區分「論文描述」「程式實作」「分析推論」。
  - `.agent_workspace/`：多 agent 分析的中間產物，已在 2026-10-17 刪除，內容已被 `notes/` 吸收。需要原件時，用 `git show 2a48b80:research/phyclone_research/.agent_workspace/<path>` 取回。
- `research/simulation_pipeline_research/`：模擬資料生成流程研究。`notes/` 分析 PhyClone 模擬的論文設計、程式行為、benchmark 真值格式，以及加入 long read（HP）特徵的缺口；`phyclone_sim_code/` 是上游模擬與驗證程式的唯讀快照（來源見 `SOURCE.md`）。`upstream/` 是 Pairtree（`pearsim`、`pairtree`）與 CONIPHER（`TRACERx_simulation_tool`）模擬生成器的 git submodule（見 `upstream/SOURCE.md`）。驗證層級定義仍以根目錄 `plan.md` 為準。
- `research/hcc1395_golden_tree_research/`：HCC1395 golden tree 文獻整理，以及 PhyloWGS model review，可作為 HCC1395 的驗證參考。
- `daily/`：每日工作日誌 HTML（由 `daily-log` skill 產生；`.data/`、`.worklog_scan/` 是它的掃描產物）。日誌只作導覽，不能當成事實來源。
- `report/`：PPT／投影片的輸出目錄（見工作慣例）。
- `tools/`：視覺化元件產生腳本（`build_visual_components.py` 會呼叫 `~/.codex/skills/svg-component-builder`），以及資料分析腳本（例如 `pcdh_entropy.py`）。
- `lab_report/`：實驗結果，一個實驗一個目錄（`YYYY-MM-DD_<主題>/`），內含 `README.md`（結論、資料、做法、結果、限制）與結果檔。產生結果的腳本放 `tools/`。

## PhyClone 常用指令

PhyClone 的程式碼位於 `research/phyclone_research/PhyClone/phyclone/`。`smc/` 是 SMC kernels／samplers，`mcmc/` 是 Particle Gibbs、Gibbs-MH 與 concentration，`tree/` 是 tree 結構與分布，`process_trace/` 負責 MAP、consensus 與 topology report。

```bash
# 推理與摘要（需先建立 conda 環境：conda create -n phyclone -c bioconda phyclone，或在 submodule 內 pip install -e .）
phyclone run -i INPUT.tsv -c CLUSTERS.tsv -o TRACE.h5 --num-chains 4
phyclone map -i TRACE.h5 -t TREE.nwk -o TABLE.tsv -s SAMPLE_PREVALENCE_TABLE.tsv
phyclone consensus -i TRACE.h5 -t TREE.nwk -o TABLE.tsv -s SAMPLE_PREVALENCE_TABLE.tsv
phyclone topology-report -i TRACE.h5 -o TOPOLOGY_TABLE.tsv -t SAMPLED_TOPOLOGIES.tar.gz

# 測試（unittest；在 submodule 根目錄執行）
cd research/phyclone_research/PhyClone
python -m unittest discover -s phyclone/tests/unit_tests
python -m unittest phyclone.tests.unit_tests.test_tree            # 單一測試檔
python -m unittest phyclone.tests.unit_tests.test_tree.<Class>.<method>
```

## 工作慣例

- **【強制】所有回答一律使用繁體中文**，包括對話回覆、摘要與說明；技術名詞依下一條保留英文。不論前文或工具輸出是什麼語言，都不可改用英文回答。
- 文件以**繁體中文**撰寫，技術名詞（SNV、CCF、multiplicity、topology、purity、ESS 等）保留英文。
- 製作 PPT／投影片時，原始檔一律輸出到 `report/<簡報名稱>/`（例如 `report/sc_groundtruth_slides/`），不要放在 `research/` 或暫存目錄。
- 收到任何製作或修改 PPT／投影片報告的指令時，先把該指令併入 `report/report_rule.md` 的「個人風格」對應區塊，再動手。製作前先讀這份規則檔並遵守。
- 做研究 claim 時，要區分 nominal purity 與實測 purity，也要區分論文主張與程式實際行為，並標明證據來源。
- 回答時採用 **ASD-STE100（Simplified Technical English）** 風格：一句只說一件事、句子短（說明句約 25 字詞內、指令句約 20 字詞內）、用主動語態、一個詞只用一個意思、指令用祈使句、先寫結論或動作再寫原因。中文回答也套用相同原則；技術名詞照上方規則保留英文。
