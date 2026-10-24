# 2026-10-21 開會整理與下週報告準備

原始紀錄：[`2026_10_21_meeting_record.md`](2026_10_21_meeting_record.md)（語音辨識整理，不是逐字稿）。
本檔整理原始紀錄，並用 repo 既有證據回答部分未決事項。

標記規則：

- 〔會議〕：會議中的說法，未查證。
- 〔程式〕：讀程式碼得到的行為。
- 〔repo〕：repo 內既有分析文件的結論，附路徑。
- 〔推論〕：本檔的推論，尚未證實。

---

## 1. 一句話結論

老師要的是「能具體說明怎麼產生的長讀驗證資料」。
本週報告的是「這種資料存不存在」。兩者不是同一個問題。
下週要拿出模擬資料的生成流程，最好附一份小型可執行結果。

**資料範圍：我們只要 long read 的模擬資料集。short read 資料集都不用了**，包括 PhyClone benchmark 與 SMC-Het 的資料。

---

## 2. 本週被指出的邏輯問題

### 2.1 問題清單

| # | 發生了什麼 | 邏輯缺口 | 下週的改法 |
|---|---|---|---|
| L1 | 說「已有模擬程式，可交給 AI 處理」 | 把「程式存在」當成「程式適用」 | 先讀程式，再逐項說明它產生什麼、缺什麼 |
| L2 | 說不清模擬流程 | 心裡有流程，但沒有寫成可檢查的步驟 | 用「輸入 → 步驟 → 輸出 → 假設」四欄說明 |
| L3 | 依 AI 的回答判斷可行 | 證據來源是 AI 口述，不是程式或論文原文 | 每個 claim 標來源：論文、程式、實測、推論 |
| L4 | 推薦短讀 benchmark（SMC-Het） | 沒先對照需求：研究需要長讀 | 先寫需求清單，再拿候選資料逐條比對 |
| L5 | 回答「確定沒有長讀 single-cell benchmark」 | 把「我沒找到」說成「不存在」 | 說「在 X 範圍、Y 關鍵字內沒找到」 |
| L6 | 可能把 single cell 當成唯一驗證路徑 | 沒列出全部驗證路徑就收斂 | 先列模擬與 single cell 兩條，再說明選擇理由 |
| L7 | 談 benchmark 時沒說答案從哪來 | 真值來源不清，結論範圍就不清 | 每次提 benchmark，第一句先說真值來源 |

### 2.2 下週報告的自我檢查（報告前逐條打勾）

- [ ] 每一頁的第一句，都回答「這頁對研究目標有什麼用」。
- [ ] 每個「可以」「沒有」「已驗證」都附證據來源。
- [ ] 每個 benchmark 都寫出：真值來源、讀長、輸入、是否公開生成程式。
- [ ] 「沒找到」都附搜尋範圍。
- [ ] AI 產生的結論，都標明我自己核對過哪一部分。
- [ ] 能不看投影片，口頭說完模擬資料的生成步驟。

---

## 3. 研究需求（判斷任何資料或方法前，先對這張表）

| 需求 | 來源 |
|---|---|
| **只用 long read 的模擬資料集** | 〔會議〕老師明確說不用短讀資料集 |
| **short read 資料集都不用**：PhyClone benchmark、SMC-Het 都不當輸入，也不借它們的真值樹 | 〔會議〕同上。PhyClone benchmark 只有計數、沒有 read（〔repo〕`simulation_pipeline_research/README.md` 結論 1）；SMC-Het 是短讀 |
| 必須有已知答案的樹（真值） | 〔會議〕驗證需要 |
| 真值來源：模擬或 single cell，任一可用，最好兩者都有 | 〔會議〕老師澄清 |
| 若沒有適用的 single-cell benchmark，先把模擬做好 | 〔會議〕決議 |
| 模擬假設要符合目前對癌細胞演化的理解 | 〔會議〕 |
| 模擬要能產生 HP1／HP2 與同 read 共現資訊 | 研究目標（`CLAUDE.md`） |

---

## 4. 未決事項：repo 已有的答案

以下問題在會議中列為未決。repo 已有部分證據，下週可以直接回答。

| 會議問題 | 目前答案 | 證據 |
|---|---|---|
| 既有模擬有沒有考慮 HP1／HP2？ | **沒有。** PhyClone 模擬器只輸出每個 SNV 的 ref／alt 計數，沒有 haplotype，也不產生 read | 〔程式〕`phyclone_sim_code/utilities/*.py` 搜尋 haplo／phase 為零筆（2026-10-21）；〔repo〕`research/simulation_pipeline_research/README.md` 結論 1 |
| 「PyClone 的模擬程式」是哪個？ | 很可能指 **PhyClone**。PhyClone repo 只有 FS-CRP 生成程式，在 `phyclone/tests/utilities/` | 〔推論〕名稱；〔repo〕`simulation_pipeline_research/README.md` 結論 2 |
| 哪些可沿用、哪些要新寫？ | 沿用「樹 → prevalence → 計數」骨架。CN segment、haplotype、read 共現、phasing 誤差要新寫 | 〔repo〕`simulation_pipeline_research/notes/04_GAPS_FOR_LONGREAD.md` §1–§2 |
| 既有模擬的假設有沒有問題？ | 有兩個：(1) root 一定是 SNV 最多的 cluster；(2) CN 對每個 SNV 每個 sample 獨立抽，沒有 segment | 〔程式＋實測〕同上 README 結論 3–4 |
| 「S NC HET」是什麼？ | **SMC-Het DREAM Challenge**（Salcedo et al., *Nat Biotechnol* 2024） | 〔repo〕`methods_survey/papers/M07_smchet_benchmark_2024/README.md` |
| SMC-Het 的真值來源？ | **模擬。** 短讀 HG002 依 haplotype 切 read pool，再植入突變。reference 是 GRCh37 | 同上 |
| SMC-Het 有沒有公開模擬程式？ | 部分公開：BAMSurgeon、PhaseTools、Galaxy workflows、評分程式。**完整的逐腫瘤生成腳本是否公開，仍待查** | 同上「資料與程式可取得性」 |
| SMC-Het 的三類問題？ | sc1：purity、clone 數、clone 比例；sc2：SNV 歸屬與共聚；sc3：樹拓撲 | 同上 |
| 文獻是「特徵進建樹」還是「特徵篩樹」？ | 肺癌長讀研究（B04）屬於後者：長讀只用來在兩棵候選樹中事後挑一棵 | 〔repo〕`report/2026_10_21_slides/OUTLINE_v5.3.md` P4 講稿 |
| 「農綠」是什麼？ | 很可能是「長讀」 | 〔推論〕與短讀對比 |
| White clone／Fi Clone／PCBA | 可能是 PhyClone、PhyClone、PCAWG | 〔推論〕僅依發音，需再確認 |

---

## 5. 優先事項

排序原則：老師明確要求、且下週一定會被問的放前面。

### P0：下週必須完成

**P0-1　寫出模擬資料生成流程（一頁可口頭說明的版本）**

- 用「輸入 → 步驟 → 輸出 → 假設」四欄寫。
- 至少涵蓋：樹怎麼產生、clone 比例、CN segment 與 HP、SNV 放在哪條 HP、read 怎麼跨多個 SNV、phasing 誤差。
- 每個步驟標明：沿用 PhyClone 哪個函式，或需要新寫。
- 基礎：`notes/04_GAPS_FOR_LONGREAD.md` 與 `plan.md` §5.2、§5.8、§5.9。
- 完成標準：不看 AI、不看稿，能在 3 分鐘內講完。

**P0-2　產出一份小型模擬資料（計數層 L1）**

- 老師原預期本週看到資料成果〔會議〕。下週要有實際檔案。
- 範圍：1 棵小樹、幾十個 SNV、帶 HP 計數與 SNV pair 共現。
- 程式放 `tools/`，結果放 `lab_report/2026-10-2x_hp_sim_demo/`。
- 完成標準：能展示真值樹、輸出檔前幾行、一張 HP 分布圖。

**P0-3　核對既有模擬程式（親自讀，不只靠 AI）**

- 讀 `phyclone_sim_code/utilities/fscrp.py` 與 `sim_data_on_tree.py`。
- 準備在會議上指出：哪一行產生計數、哪裡沒有 haplotype。
- 完成標準：能回答「為什麼不能直接用」並指出程式位置。

### P1：下週應完成

**P1-1　SMC-Het 模擬程式的公開程度（只看流程，不用資料）**

- 查 `github.com/smc-het-challenge` 的 Galaxy workflows，確認有沒有完整生成腳本。
- 目的：參考它「依 haplotype 切 read pool → 植入突變」的做法，改寫成 long read 版生成流程（L2）。
- SMC-Het 的資料與真值檔是短讀，不用。

**P1-2　長讀 single-cell benchmark 的搜尋範圍說明**

- 寫清楚：搜過哪些來源、關鍵字、時間範圍、篇數（目前 21 篇）。
- 改用 1–2 個其他 AI model 補搜〔會議建議〕，結果回原文核對。
- 結論句改成「在上述範圍內沒找到」。

**P1-3　驗證路徑總表**

- 一張表列出 long read 的驗證層：L1、L2、L3（定義見 `plan.md`）。
- **移除 L0 與 L1-B。** 這兩層的輸入是 PhyClone 短讀 benchmark，short read 資料集都不用了。
- `plan.md` 的 L0 與 L1-B 已於 2026-10-21 刪除。
- 每列寫：真值來源、讀長、能支持什麼結論、目前進度。

### P2：可以排在後面

- **P2-1** 釐清 P1／P2 與 HP1／HP2 是否同義。下週會議直接問老師。
- **P2-2** 文獻建樹邏輯比對：每篇標「特徵進模型」或「特徵事後篩樹」。
- **P2-3** 每週開會後，把紀錄放 `research/meeting_record/`，開工前先讀上週紀錄。本目錄已建立。

---

## 6. 下週報告建議結構

照第 2 節的改法排序：先回答老師上次的問題，再報進度。

1. **上次的問題與回答**（1 頁）：列第 4 節的表，只放最重要的 4–5 列。
2. **研究需求**（1 頁）：第 3 節的表。後面每頁都回頭對照它。
3. **模擬資料怎麼產生**（2–3 頁）：P0-1 的四欄流程。每步標「沿用／新寫」。
4. **小型模擬結果**（1–2 頁）：P0-2 的真值樹與輸出。
5. **既有程式為什麼不夠**（1 頁）：P0-3，附程式位置。
6. **SMC-Het 的定位**（1 頁）：真值來自模擬、短讀、GRCh37。它的資料不用；只參考它的生成流程，改寫成 long read 版。
7. **下一步與要老師決定的事**（1 頁）：例如 P1／P2 定義、樹形 prior 要不要修正。

---

## 7. 待辦對照表（原紀錄 → 本檔優先級）

| 原紀錄待辦 | 本檔 |
|---|---|
| 說明模擬資料如何產生，列出流程與假設 | P0-1、P0-2 |
| 核對既有模擬是否支援 HP1／HP2 | 已有答案（第 4 節）；P0-3 準備展示 |
| 釐清目標讀長需求，核對 single-cell benchmark | 第 3 節；P1-2 |
| 找並讀 PyClone、S NC HET 的模擬程式 | P0-3、P1-1 |
| 釐清 benchmark 的答案來源與讀長是否相符 | 第 4 節；P1-3 |
| 擴大文獻搜尋，核對建樹邏輯差異 | P1-2、P2-2 |
| 建立會議紀錄子目錄 | P2-3（已建立） |
