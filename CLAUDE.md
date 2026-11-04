# CLAUDE.md

## 目錄

先看 `research/INDEX.md`（研究總入口）。術語以 `research/CONTEXT.md` 為準。

- HP 特徵設計與驗證層級（原 `plan.md`）：2026-11-04 搬到 `/bip8_disk/boyu114/haploclone/rust/docs/plan.md`（10-21 後未更新，先看檔頭「現況」）。
- `docs/`：**找資料路徑先看 `docs/index.md`**（問題 → 檔案章節 → 一句話答案）。`docs/data_input.md`：HCC1395 tagged BAM、VCF、SNV 計數表盤點。`docs/tumor_sample.md`：六株 ONT 細胞株的 CRAM 路徑、subsample 純度與實測 purity。
- `research/literature/`：**找論文先看這裡**（見其 `README.md`）。分類只改 `paper_categories.tsv`，再跑 `python3 research/literature/tools/sync_paper_categories.py`（`--check` 查 drift）。
- `research/phyclone_research/`：PhyClone 分析。先讀 `notes/zh-TW/`，再查原始碼。`PhyClone/` 是 git submodule，改動要在 submodule 內 commit。
- `research/simulation_pipeline_research/`：模擬生成流程研究。`upstream/` 是 Pairtree、CONIPHER 模擬器的 submodule。
- `research/hcc1395_golden_tree_research/`：HCC1395 參考樹文獻，可作驗證參考。
- `diplosim/`：**現行模擬器**，用 Rust 寫的雙套體 long read bulk 模擬器（2026-10-29 建立）。照 CONIPHER 模擬步驟逐步移植，每一步都要能說明「沿用哪個函式」或「新寫什麼、為什麼」。決策與現況先看 `DECISIONS.md`；CONIPHER 步驟對照見 `docs/conipher_steps.md`、`docs/porting_map.md`。測試：`cd diplosim && cargo test`。
- haploclone（PhyClone 的 Rust 移植）：程式、golden、移植文件都在 `/bip8_disk/boyu114/haploclone/rust/`（branch `rust-port`）。現況與決策見 `rust/docs/PORTING.md`、`rust/docs/decisions.tsv`。改 haploclone 時，預設路徑的輸出要和原版保持 bit-identical。
- `tools/`：分析與繪圖腳本。`lab_report/`：一個實驗一個目錄（`YYYY-MM-DD_<主題>/README.md`：結論、資料、做法、結果、限制），腳本放 `tools/`。
- `report/`：投影片輸出。`daily/`：工作日誌，只作導覽，不能當事實來源。
- `meeting_record/`：每週會議紀錄（`YYYY_MM_DD_meeting_record.md` 原始紀錄、`_summary.md` 整理）。**找會議先看 `meeting_record/index.md`**（日期、會議目的、關鍵字、主要決議）。

## 研究目標

列方案或動手前，先對照這一節。前提錯了，所有方案都會偏（11-04 會議 N5）。

- **目的：** 模擬帶 HP1／HP2 的 long read bulk 腫瘤定序資料，附已知的真值演化樹，用來測試把 HP 資訊加進樹重建（haploclone）能不能改善結果。模擬器是 `diplosim/`。〔repo〕`report/2026_11_04_slides/OUTLINE.md`「研究目的」
- **真值和觀測分開（N1）：** 模擬器知道每個 SNV、每條 read（或每個計數）來自哪條 HP、哪個 clone、哪個位置，這些都要留在真值裡。HP0／unphased、mistag、caller 漏抓只屬於觀測層，不能讓真值跟著遺失。
- **一個 bulk sample：** 只優化單一 bulk 樣本，多 sample 只當上限參考。〔repo〕`diplosim/DECISIONS.md` 2026-10-29
- **只用 long read：** 輸入與驗證參考都只用 long read 資料。〔會議〕10-21；〔repo〕`diplosim/DECISIONS.md` 2026-10-30
- **合理性要分層說（N3）：** 觀測特徵像真實資料，不等於克隆結構對，也不等於演化路徑對。每個驗證要寫出它支持哪一層。

## 工作慣例

- **【強制】所有使用者看得到的文字一律用繁體中文**，包含進度句、通知回覆、compaction 後第一句。技術名詞（SNV、CCF、multiplicity、purity 等）保留英文。
- **大型資料先找共用副本，不要重複下載。** 要用公開資料前，先查 `docs/index.md`，或問使用者實驗室成員是否已下載。有就直接引用路徑，並只讀不寫。例：HG008 在 `/big8_disk/yungjen114/data/HG008/`。（使用者 2026-11-04：多人重複下載會把 server 硬碟用完）
- 寫作採 ASD-STE100 風格，約做到 80%：先寫結論，一句一件事，句子短，主動語態，一詞一義。
- 使用者問「是不是／是什麼」或說「簡單說」：先用 2–4 句白話回答，不用標題與表格。
- 投影片：原始檔放 `report/<簡報名稱>/`。動手前先把新指令併入 `report/report_rule.md`「個人風格」，再讀並遵守該檔。分工：報告講什麼、照什麼順序，以本檔「交付」與「開工前／做研究時」為準；`report_rule.md` 只管投影片怎麼做（頁面、圖、講稿）。

## 研究與報告流程

來源：`meeting_record/index.md` 列出的各次會議 summary §2。目前有 L1–L7（10-21）、M1–M3（10-28）、N1–N5（11-04）。**一律以 `meeting_record/index.md` 裡日期最新的一次會議為準**；本節和最新會議衝突時，照最新會議做，並告訴使用者要更新本節。有新的會議紀錄時：整理成 `_summary.md`、更新 `index.md`，再把新問題併入本節。回覆中寫明用了哪幾次會議。

**決策點：先列方案，停下來讓使用者選（M1，最優先）**

- 遇到設計或驗證問題（模擬器怎麼改、怎麼驗證、選哪個資料或方法），不直接動手改。先列 2–3 個候選方案，每個寫：核心想法、改哪裡、優點、風險、怎麼驗證。然後停下來，等使用者選。
- 使用者選定前，不寫實作。只有一個合理方案時，也要寫出排除其他方案的理由，再請使用者確認。
- 列方案前，先確認前提：研究目標（見「研究目標」）和相關的生物假說。前提不清楚，先查清楚再列方案。（N5）
- 實作細節（命名、重構、測試、格式、bug 修正）可以自己決定，不必停。
- 動手後，用白話列出「改了哪裡、為什麼」，讓使用者能不看程式就向老師說明。
- 控制速度：一次只做一個步驟或一組改動。做完後停下來，等使用者確認看懂了，才做下一步。不要一次連做多步或多個版本。（來源：2026-10-29 前一版模擬器 4 天改了 CONIPHER 11 步裡的 10 步，使用者跟不上，因此改寫成 diplosim）

**開工前**

- 先讀 `meeting_record/index.md` 裡日期最新的一次會議（有 `_summary.md` 就先讀它）的需求、決議與待辦。不在這些項目上的工作，先提議，等同意再做。
- 評估任何資料、benchmark 或方法，先逐條對需求表（只用 long read、要有真值樹、要能產生 HP1/HP2 與同 read 共現）。不符合的寫出違反哪一條，然後排除，不再展開。（L4）
- 驗證路徑先列全部（模擬、single cell），再收斂，並寫出選擇理由。（L6）

**做研究時**

- 程式存在不等於程式適用。評估現成工具或模擬器時，先讀程式，寫出它產生什麼、缺什麼，附 `檔案:行號`。（L1）
- 每個 claim 標來源：〔論文〕〔程式〕〔實測〕〔會議〕〔推論〕。AI 的回答（包括 subagent 的摘要）不算證據，要回到原文或程式核對。區分 nominal 與實測 purity、論文主張與程式行為。（L3）
- 說「沒有／不存在」時，改寫成「在 X 來源、Y 關鍵字、Z 期間內沒找到」。（L5）
- 提到 benchmark，第一句先寫：真值來源（模擬或 single cell）、讀長、輸入、是否公開生成程式。（L7）
- 說明流程（例如模擬資料怎麼產生）時，照順序寫出步驟。格式依問題決定，不用固定欄位。講到改造現有程式時，每步標「沿用（附函式）」或「新寫」。（L2）
- 解釋逐步發生的過程（演化事件、模擬步驟、候選改法）時，先畫流程圖或示意圖，再補文字。圖要能直接放進報告。不是每個回答都要畫圖。（M3）
- 改模擬機制或加參數前，先查相關的癌症演化假說、支持證據與適用範圍，寫成短的知識文件（每個 claim 標來源），再列方案。不要只在既有程式上加隨機參數，也不要讓「既有程式好改」決定研究方向。（N2）
- 模擬器一次只加一個機制，先單點突變，再 CNA、LOH、多倍體。每一階段先補生物機制、既有模擬方法與驗證資訊。（N4）
- 驗證模擬時，最終特徵相似（例如 BAM 統計量）只算一個指標，不能證明演化樹或演化過程正確。「和真實資料一樣」要先定義。另找獨立證據，例如克隆分群、單細胞。（N3）

**交付（照報告順序）**

1. 接回上次會議：研究目的、上次定的方向、各方向現在是可行、不可行還是未定。（M2）
2. 本週 1–3 個任務：不必等全部完成才報告。挑 1–3 個任務實際嘗試解決。（M2）
3. 方案與選擇理由：每個任務寫候選方案、選了哪個、為什麼。（M2）
4. 結果（含失敗）：實際輸出檔、前幾行、一張圖，放 `lab_report/`。寫出預期與實際結果，失敗也要放。沒有結果，就寫卡在哪一步。
5. 交出前自我檢查：報告或投影片完成前，逐條檢查最新一次會議 summary §2.2 的自我檢查清單（它會沿用前幾次的清單）。做投影片時，再跑 `report_rule.md` 的 `check_slides.py` 與交付前檢查表。把未通過的項目告訴使用者。
6. AI 環境改善（1–2 頁，和研究進度分開）：這週調整了哪些專案知識或工作規則、哪些有效、哪些無效。（N5）
