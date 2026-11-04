# CLAUDE.md

## 研究目標

列方案或動手前，先對照這一節。前提錯了，所有方案都會偏。（N5）

- **目的：** 模擬帶 HP1／HP2 的 long read bulk 腫瘤定序資料，附已知的真值演化樹，用來測試把 HP 資訊加進樹重建（haploclone）能不能改善結果。模擬器是 `diplosim/`。〔repo〕`report/2026_11_04_slides/OUTLINE.md`「研究目的」
- **真值和觀測分開：** 模擬器知道每個 SNV、每條 read（或每個計數）來自哪條 HP、哪個 clone、哪個位置，這些都要留在真值裡。HP0／unphased、mistag、caller 漏抓只屬於觀測層，不能讓真值跟著遺失。（N1）
- **需求表：** 只用 long read（輸入與驗證參考都是）；要有真值樹。只優化一個 bulk sample，多 sample 只當上限參考。（同 read 共現：2026-11-04 使用者決定先不列為需求）〔會議〕10-21；〔repo〕`diplosim/DECISIONS.md` 2026-10-29、10-30
- **目前暫停：HCC1395 的觀察與驗證**（PPC、purity holdout、為了對上 HCC1395 統計量的調參）。不要提議新的 HCC1395 實驗或參數；既有結果只當歷史參考。現在的方向是先查單點突變的生物假說（N2、N4）。〔repo〕`diplosim/DECISIONS.md` 2026-11-04
- **最新會議優先：** 本檔的規則來自各次會議（L1–L7：10-21，M1–M3：10-28，N1–N5：11-04）。一律以 `meeting_record/index.md` 裡日期最新的一次為準；本檔和最新會議衝突時，照最新會議做，並告訴使用者要更新本檔。

## 去哪裡找

先看 `research/INDEX.md`（研究總入口）。

| 要找 | 先看 |
|---|---|
| 資料路徑（BAM、CRAM、VCF、HG008） | `docs/index.md` |
| 實驗結論與狀態 | `lab_report/INDEX.md` |
| 腳本與主流程指令 | `tools/README.md` |
| 會議需求、決議、待辦 | `meeting_record/index.md` → 最新一次 `_summary.md` |
| 論文 | `research/literature/README.md`（分類只改 `paper_categories.tsv`，再跑 `python3 research/literature/tools/sync_paper_categories.py`，`--check` 查 drift） |
| 模擬器（現行） | `diplosim/DECISIONS.md`；CONIPHER 步驟對照 `diplosim/docs/conipher_steps.md`、`porting_map.md`；測試 `cd diplosim && cargo test` |
| 樹重建（HP 擴充） | haploclone：`/bip8_disk/boyu114/haploclone/rust/`（branch `rust-port`）。現況 `rust/docs/PORTING.md`、`decisions.tsv`；HP 設計 `rust/docs/plan.md`（10-21 後未更新，先看檔頭「現況」）。改 haploclone 時，預設路徑的輸出要和原版 bit-identical |

其他目錄：
- `research/phyclone_research/`：PhyClone 原版的論文與程式分析，只當背景。HP 擴充的改動在 haploclone 做，不改 `PhyClone/` submodule。
- `research/simulation_pipeline_research/`：模擬流程研究；`upstream/` 是 Pairtree、CONIPHER 的 submodule。`research/hcc1395_golden_tree_research/`：HCC1395 參考樹文獻。
- `report/`：投影片。`daily/`：工作日誌，只作導覽，不能當事實來源。

## 工作慣例

- **【強制】使用者看得到的文字一律用繁體中文**，包含進度句、通知回覆、compaction 後第一句。技術名詞（SNV、CCF、multiplicity、purity 等）保留英文。
- 寫作採 ASD-STE100 風格，約做到 80%：先寫結論，一句一件事，句子短，主動語態，一詞一義。
- 使用者問「是不是／是什麼」或說「簡單說」：先用 2–4 句白話回答，不用標題與表格。
- **大型資料先找共用副本，不要重複下載。** 先查 `docs/index.md`，或問使用者實驗室成員是否已下載；有就引用路徑，只讀不寫。（使用者 2026-11-04：多人重複下載會把 server 硬碟用完）
- **repo 是公開的**（GitHub `CCU-Bioinformatics-Lab/bo-yu-daily`）。不要 commit 論文 PDF、論文補充表格、金鑰或個人資料；`.gitignore` 已擋 `research/**/*.pdf`、`*.xlsx` 與 `lab_report` 的大型輸出。只在使用者要求時 commit 或 push。
- 投影片：原始檔放 `report/<簡報名稱>/`。動手前先把新指令併入 `report/report_rule.md`「個人風格」，再讀並遵守該檔。報告講什麼、照什麼順序，以本檔「交付」為準；`report_rule.md` 只管投影片怎麼做。

## 決策點：先列方案，停下來讓使用者選（M1，最優先）

- 遇到設計或驗證問題（模擬器怎麼改、怎麼驗證、選哪個資料或方法），不直接動手改。先確認前提（研究目標、相關生物假說），再列 2–3 個候選方案，每個寫：核心想法、改哪裡、優點、風險、怎麼驗證。然後停下來，等使用者選。（M1、N5）
- 使用者選定前，不寫實作。只有一個合理方案時，也要寫出排除其他方案的理由，再請使用者確認。
- 實作細節（命名、重構、測試、格式、bug 修正）可以自己決定，不必停。
- 動手後，用白話列出「改了哪裡、為什麼」，讓使用者能不看程式就向老師說明。
- 控制速度：一次只做一個步驟或一組改動，做完停下來，等使用者確認看懂了，才做下一步。（來源：2026-10-29 前一版模擬器 4 天改了 CONIPHER 11 步裡的 10 步，使用者跟不上）

## 開工前

- 讀最新一次會議的 `_summary.md`：需求、決議、待辦。不在這些項目上的工作，先提議，等同意再做。回覆中寫明用了哪幾次會議。
- 評估任何資料、benchmark 或方法，先逐條對「研究目標」的需求表。不符合的寫出違反哪一條，然後排除，不再展開。（L4）

## 做研究時

**證據**
- 程式存在不等於程式適用。評估現成工具或模擬器時，先讀程式，寫出它產生什麼、缺什麼，附 `檔案:行號`。（L1）
- 每個 claim 標來源：〔論文〕〔程式〕〔實測〕〔會議〕〔推論〕。AI 的回答（包括 subagent 的摘要）不算證據，要回到原文或程式核對。區分 nominal 與實測 purity、論文主張與程式行為。（L3）
- 說「沒有／不存在」時，改寫成「在 X 來源、Y 關鍵字、Z 期間內沒找到」。（L5）
- 提到 benchmark，第一句先寫：真值來源（模擬或 single cell）、讀長、輸入、是否公開生成程式。（L7）

**改模擬器**
- 改機制或加參數前，先查相關的癌症演化假說、支持證據與適用範圍，寫成短的知識文件（每個 claim 標來源），再列方案。不要只在既有程式上加隨機參數，也不要讓「既有程式好改」決定研究方向。（N2）
- 一次只加一個機制：先單點突變，再 CNA、LOH、多倍體。（N4）
- 說明流程時，照順序寫出步驟；講到改造現有程式，每步標「沿用（附函式）」或「新寫」。（L2）

**驗證模擬**
- 先列出全部驗證路徑（模擬內部檢查、真實 bulk 統計、single cell／克隆分群），再收斂並寫出選擇理由。（L6）
- 每個驗證寫出它支持哪一層：觀測特徵像真實資料、克隆結構對、演化路徑對。最終特徵相似（例如 BAM 統計量）不能證明演化樹或過程正確；「和真實資料一樣」要先定義。（N3）

**呈現**
- 解釋逐步發生的過程（演化事件、模擬步驟、候選改法）時，先畫流程圖或示意圖，再補文字。圖要能直接放進報告。不是每個回答都要畫圖。（M3）
- 新增實驗時，在 `lab_report/INDEX.md` 加一列；取代舊實驗時改它的狀態。新寫腳本時，在 `tools/README.md` 加一列。

## 交付（照報告順序）

1. 接回上次會議：研究目的、上次定的方向、各方向現在是可行、不可行還是未定。（M2）
2. 本週 1–3 個任務：不必等全部完成才報告。（M2）
3. 方案與選擇理由：每個任務寫候選方案、選了哪個、為什麼。（M2）
4. 結果（含失敗）：實際輸出檔、前幾行、一張圖，放 `lab_report/`。寫出預期與實際結果，失敗也要放；沒有結果，就寫卡在哪一步。
5. 自我檢查：完成前逐條檢查最新一次會議 summary §2.2 的清單（它沿用前幾次的清單）。做投影片時，再跑 `tools/check_slides.py` 與 `report_rule.md` 的交付前檢查表。把未通過的項目告訴使用者。
6. AI 環境改善（1–2 頁，和研究進度分開）：這週調整了哪些專案知識或工作規則、哪些有效、哪些無效。（N5）

## 新會議紀錄進來時

原始紀錄存成 `meeting_record/YYYY_MM_DD_meeting_record.md`，整理成 `_summary.md`，在 `meeting_record/index.md` 最上面加一列，再把新問題併入本檔對應的段落（標上新編號）。
