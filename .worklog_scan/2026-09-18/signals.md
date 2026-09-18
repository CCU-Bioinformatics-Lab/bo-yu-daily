# 選材信號原料 — 2026-09-18

> 這份只把**可數的東西數出來**。哪個候選對應哪些訊息與檔案要你讀 transcript 判斷。
> 權重：**參與度 > 落地 > 跨日延續**。
> ⚠️ 分數與信號**不進日誌 JSON**，只用來排候選表——它是啟發式，不是量測值。

---

## 1. 參與度：使用者訊息 17 則（不含重疊區）

拍板句用 **★** 標出來。一條線只要有拍板句，它就不是 agent 自己在跑。

⚠️ 本區間有 **2 個 session**（01a0b300、01a0b320）。平行做不同任務時，同一條線的訊息會散落在時間序上——**先照 session 分組再對應到候選**。

- 　 `01a0b300 09-18 13:33` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 13:33` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 13:33` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 13:33` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 13:57` 幫我把data.md,model.md,inference_algo.md,output.md,validation.md都先清空所有內容，因為想要重新設計，並都補上未來待補
- 　 `01a0b300 09-18 14:00` 先幫我使用多subagent分類git commmit，並也使用subagent reviewer去檢查classes agent
- 　 `01a0b300 09-18 14:00` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 14:00` 幫我把data.md,model.md,inference_algo.md,output.md,validation.md都先清空所有內容，因為想要重新設計，並都補上未來待補
- 　 `01a0b300 09-18 14:00` 先幫我使用多subagent分類git commmit，並也使用subagent reviewer去檢查classes agent
- 　 `01a0b300 09-18 14:00` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 14:00` 幫我把data.md,model.md,inference_algo.md,output.md,validation.md都先清空所有內容，因為想要重新設計，並都補上未來待補
- 　 `01a0b300 09-18 14:00` 先幫我使用多subagent分類git commmit，並也使用subagent reviewer去檢查classes agent
- 　 `01a0b300 09-18 14:01` 幫我調查本repo的檔案目錄架構，使用多subagent分頭搜索，最終由manager agent來顯示成果
- 　 `01a0b300 09-18 14:01` 幫我把data.md,model.md,inference_algo.md,output.md,validation.md都先清空所有內容，因為想要重新設計，並都補上未來待補
- 　 `01a0b300 09-18 14:01` 先幫我使用多subagent分類git commmit，並也使用subagent reviewer去檢查classes agent
- 　 `01a0b300 09-18 14:04` 都幫我分別git add並個別git commit
- 　 `01a0b320 09-18 14:09` 幫我使用daily-log plugin，輸出到/bip8_disk/boyu114/main_work/daily/

## 2. 落地：寫入型工具呼叫 0 次

（無）

> ⚠️ **上面這份（工具呼叫）才是可以歸屬到 session 的落地證據。**
> 下面的 git commit 與檔案 mtime 是**全域**的，平行開多個 session 時
> 分不出哪個檔是哪條線改的。**填候選的 `files` 信號要用工具呼叫這份**，
> 用 mtime 那份會把 A 的檔案數算到 B 頭上。

### 2b. git commit（29 筆）

- 324184e 14:06 docs: reset validation design placeholder
- 5d267c8 14:06 docs: reset output design placeholder
- 6dbfbca 14:06 docs: remove module format specification
- 7c15d63 14:06 docs: remove module format page
- 327c9a5 14:06 docs: reset model design placeholder
- c0540e2 14:06 docs: remove legacy data reference
- 0420e3c 14:06 docs: reset inference algorithm design placeholder
- 052fb26 14:06 test: remove inference smoke test
- ef18684 14:06 test: remove inference contract test runner
- 1b2c667 14:06 test: remove inference contract tests
- 7abb0e1 14:06 test: remove inference smoke fixture
- 82c2a21 14:06 test: remove inference test guide
- 17d8ea8 14:06 refactor: remove inference algorithm registry implementation
- b223e23 14:06 refactor: remove inference model implementation
- 4c9173e 14:06 refactor: remove inference CLI entry point
- 5e41247 14:06 refactor: remove inference JSON interface
- 7c14969 14:06 refactor: remove inference JSON implementation
- 3aa837b 14:06 refactor: remove inference hash interface
- 447dbc7 14:06 refactor: remove inference hash implementation
- f0021cb 14:06 refactor: remove inference algorithm implementation
- f2ad106 14:06 refactor: remove inference algorithm registry interface
- f01b065 14:06 refactor: remove inference model interface
- de22d33 14:06 refactor: remove inference algorithm interface
- 403692c 14:06 docs: remove inference backend guide
- d0d4e4b 14:06 build: remove inference CMake configuration
- baa0fbd 14:06 chore: remove inference ignore rules
- d56a0a5 14:06 docs: remove experiment workflow specification
- 4bc0381 14:06 docs: reset data design placeholder
- 9457f3f 14:06 docs: update repository README

### 2c. 動過的檔案（19 個；mtime 0＋只有 git 看得到的 19）

> ⚠️ mtime 只記得最後一次改動 —— 補寫舊日期時，那天改過、之後又被改過的檔（專案現況、決策紀錄這類最活躍的檔最常見）在 mtime 上已經消失。標 **[git]** 的就是靠 commit 記錄補回來的。

- `inference/.gitignore`  **[git]**
- `inference/CMakeLists.txt`  **[git]**
- `inference/README.md`  **[git]**
- `inference/include/tumor_tree_inference/algorithm.hpp`  **[git]**
- `inference/include/tumor_tree_inference/model.hpp`  **[git]**
- `inference/include/tumor_tree_inference/registry.hpp`  **[git]**
- `inference/src/algorithm.cpp`  **[git]**
- `inference/src/hash.cpp`  **[git]**
- `inference/src/hash.hpp`  **[git]**
- `inference/src/json.cpp`  **[git]**
- `inference/src/json.hpp`  **[git]**
- `inference/src/main.cpp`  **[git]**
- `inference/src/model.cpp`  **[git]**
- `inference/src/registry.cpp`  **[git]**
- `inference/tests/README.md`  **[git]**
- `inference/tests/canonical_smoke.tsv`  **[git]**
- `inference/tests/contract_test.py`  **[git]**
- `inference/tests/run_contract_tests.sh`  **[git]**
- `inference/tests/smoke.cpp`  **[git]**

### 2d. subagent 報告提到的檔案（0 個）

> subagent 的內部工具呼叫不進 transcript，主對話只留結案報告。這些檔在 2 與 2c 都可能是隱形的，**別漏掉它們代表的工作項**。

（無）

## 3. 跨日延續：前 7 天的日誌標題（0 筆）

候選項若與下列任一條是同一件事，標為「續」。

（無先前日誌）

---

## 保底規則

**有 commit 的事一律留在候選表上**，不論參與度多低。
否則「叫 agent 背景跑一件重要的事、整天沒再管它」會被三個信號全判低。

