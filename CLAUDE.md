# CLAUDE.md

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
- `meeting_record/`：每週會議紀錄（`YYYY_MM_DD_meeting_record.md` 原始紀錄、`_summary.md` 整理）。

## 工作慣例

- **【強制】所有使用者看得到的文字一律用繁體中文**，包含進度句、通知回覆、compaction 後第一句。技術名詞（SNV、CCF、multiplicity、purity 等）保留英文。
- 寫作採 ASD-STE100 風格，約做到 80%：先寫結論，一句一件事，句子短，主動語態，一詞一義。
- 使用者問「是不是／是什麼」或說「簡單說」：先用 2–4 句白話回答，不用標題與表格。
- 投影片：原始檔放 `report/<簡報名稱>/`。動手前先把新指令併入 `report/report_rule.md`「個人風格」，再讀並遵守該檔。

## 研究與報告流程

來源：`meeting_record/2026_10_21_meeting_summary.md` §2（老師指出的邏輯問題 L1–L7）、`meeting_record/2026_10_28_meeting_record.md` 議題四至六（M1–M3）。新會議若指出新問題，整理時一併更新本節。

**決策點：先列方案，停下來讓使用者選（M1，最優先）**

- 遇到設計或驗證問題（模擬器怎麼改、怎麼驗證、選哪個資料或方法），不直接動手改。先列 2–3 個候選方案，每個寫：核心想法、改哪裡、優點、風險、怎麼驗證。然後停下來，等使用者選。
- 使用者選定前，不寫實作。只有一個合理方案時，也要寫出排除其他方案的理由，再請使用者確認。
- 實作細節（命名、重構、測試、格式、bug 修正）可以自己決定，不必停。判斷標準：這個決定會不會被老師問「為什麼這樣改」。會，就停。
- 動手後，用白話列出「改了哪裡、為什麼」，讓使用者能不看程式就向老師說明。

**開工前**

- 先讀 `meeting_record/` 最新一次會議紀錄（有 `_summary.md` 就先讀它）的需求、決議與待辦。不在這些項目上的工作，先提議，等同意再做。
- 評估任何資料、benchmark 或方法，先逐條對需求表（只用 long read、要有真值樹、要能產生 HP1/HP2 與同 read 共現）。不符合的寫出違反哪一條，然後排除，不再展開。（L4）
- 驗證路徑先列全部（模擬、single cell），再收斂，並寫出選擇理由。（L6）

**做研究時**

- 程式存在不等於程式適用。評估現成工具或模擬器時，先讀程式，寫出它產生什麼、缺什麼，附 `檔案:行號`。（L1）
- 每個 claim 標來源：〔論文〕〔程式〕〔實測〕〔會議〕〔推論〕。AI 的回答（包括 subagent 的摘要）不算證據，要回到原文或程式核對。區分 nominal 與實測 purity、論文主張與程式行為。（L3）
- 說「沒有／不存在」時，改寫成「在 X 來源、Y 關鍵字、Z 期間內沒找到」。（L5）
- 提到 benchmark，第一句先寫：真值來源（模擬或 single cell）、讀長、輸入、是否公開生成程式。（L7）
- 說明流程（例如模擬資料怎麼產生）一律用「輸入 → 步驟 → 輸出 → 假設」四欄，每步標「沿用（附函式）」或「新寫」。（L2）
- 解釋逐步發生的過程（演化事件、模擬步驟、候選改法）時，先畫流程圖或示意圖，再補文字。圖要能直接放進報告。不是每個回答都要畫圖。（M3）

**交付**

- 報告開頭先接回上次會議：研究目的、上次定的方向、各方向現在是可行、不可行還是未定，然後才講本週做了什麼。（M2）
- 不必等全部完成才報告。挑 1–3 個代表性嘗試，各寫：候選方案、選了哪個與理由、已懂與未懂、預期與實際結果（失敗也要放）。（M2）
- 先有可執行的小結果，再做報告：實際輸出檔、前幾行、一張圖，放 `lab_report/`。沒有結果的週，報告要明寫卡在哪一步。
- 報告或投影片完成前，逐條檢查 summary §2.2 的自我檢查清單，並把未通過的項目告訴使用者。
- 每個結論附一句「這對研究目標有什麼用」。
