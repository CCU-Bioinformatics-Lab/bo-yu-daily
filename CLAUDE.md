# CLAUDE.md

## 研究目標

重建**腫瘤演化樹（tumor phylogeny / clone tree）**，並加入 long read 才有的特徵：**longphase-s 的 HP1/HP2 phasing**、SNV 與 allele-specific CN 的對應、同一 read 上 SNV 的共現。用這些特徵約束 multiplicity、CNV timing、clone assignment 與 topology。

資料：ONT 腫瘤細胞株（HCC1395、COLO829、H1437、H2009、HCC1937、HCC1954）的 CRAM，reference 是 `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`。路徑見 `tumor_sample.md`。`tX_nY` 是 design tumor fraction，**不是**實測 purity；`t00_n25` 是純 normal。

## 目錄

先看 `research/INDEX.md`（研究總入口）。術語以 `research/CONTEXT.md` 為準。

- `plan.md`：HP 特徵接進 PhyClone 的設計與驗證層級。`data_input.md`：tagged BAM 與 SNV 計數表盤點。
- `research/literature/`：**找論文先看這裡**（見其 `README.md`）。分類只改 `paper_categories.tsv`，再跑 `python3 research/literature/tools/sync_paper_categories.py`（`--check` 查 drift）。
- `research/phyclone_research/`：PhyClone 分析。先讀 `notes/zh-TW/`，再查原始碼。`PhyClone/` 是 git submodule，改動要在 submodule 內 commit。
- `research/simulation_pipeline_research/`：模擬生成流程研究。`upstream/` 是 Pairtree、CONIPHER 模擬器的 submodule。
- `research/hcc1395_golden_tree_research/`：HCC1395 參考樹文獻，可作驗證參考。
- `longbulksim/`：long read bulk 模擬器，輸出 PhyClone 輸入、HP 計數、SNV pair 共現與獨立的 `truth/`。說明見 `README.md`、`DECISIONS.md`。測試：`cd longbulksim && python3 -m unittest discover -s tests`。
- `phyclone_rs/`：PhyClone 的 Rust 移植（haploclone）計畫、golden 與 V1–V5 驗證。程式在 `/bip8_disk/boyu114/haploclone/rust/`（branch `rust-port`）。現況與決策見 `PORTING.md`、`decisions.tsv`。改 haploclone 時，預設路徑的輸出要和原版保持 bit-identical。
- `tools/`：分析與繪圖腳本。`lab_report/`：一個實驗一個目錄（`YYYY-MM-DD_<主題>/README.md`：結論、資料、做法、結果、限制），腳本放 `tools/`。
- `report/`：投影片輸出。`daily/`：工作日誌，只作導覽，不能當事實來源。

## 工作慣例

- **【強制】所有使用者看得到的文字一律用繁體中文**，包含進度句、通知回覆、compaction 後第一句。技術名詞（SNV、CCF、multiplicity、purity 等）保留英文。
- 寫作採 ASD-STE100 風格，約做到 80%：先寫結論，一句一件事，句子短，主動語態，一詞一義。
- 使用者問「是不是／是什麼」或說「簡單說」：先用 2–4 句白話回答，不用標題與表格。專案代號（A1/A2、C4、PPC 等）每次回答第一次出現時附一句白話定義。
- 研究 claim 要標證據來源，並區分 nominal 與實測 purity、論文主張與程式行為。
- 投影片：原始檔放 `report/<簡報名稱>/`。動手前先把新指令併入 `report/report_rule.md`「個人風格」，再讀並遵守該檔。
- 耗時運算（PhyClone 批次、下載、新量測）前，先寫出：回答的問題與目標、資料與版本、預估時間與 CPU（先看 `uptime`，runs × chains 不超過空閒核心）、查進度的指令。不在目前目標上的工作，先提議，等同意再做。
