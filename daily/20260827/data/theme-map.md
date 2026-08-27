# 2026-08-27 主題地圖

> 來源範圍：2026-08-27 的 2 個 Codex root sessions；本日報涵蓋 module／bioinformatics skill／Model A 文件／assets／Git 與 daily 壓縮工作。

| 主題 | 主題 summary | 包含的 task | 為何屬於同一主題 | 代表證據 | 未完成事項 |
|---|---|---|---|---|---|
| 1. 模組解說與視覺語言 | 把 `arch.md` 的五模組 contract 轉成一般讀者可理解、可製圖的敘事骨架。 | T1、T5 | 共同產出 `module.md` 與同一條 data → model → inference → output → validation 敘事。 | `module.md`；transcript L16–L48、L1056–L1135 | F0–F15 尚未完整製作；IGV-like pileup、CN projection、likelihood 與 validation visuals 仍待補。 |
| 2. 可核驗的 bioinformatics 檢索流程 | 讓專案相關知識查詢有固定的來源分層、平行搜尋與衝突核對流程。 | T2、T3 | T2 找到入口，T3 將入口改成可執行的 evidence workflow；兩者共同形成 skill 能力。 | `/home/boyu114/.codex/skills/bioinformatics-knowledge/SKILL.md`；`Skill is valid!` | 後續查詢仍需依新流程驗證實際使用效果；skill 外部路徑不屬本 repo 版本。 |
| 3. Model A 與 current runtime 邊界 | 將文件從複雜 target/spec 收斂到目前 Model A baseline，釐清 phi、CCF、eta、multiplicity 與 HP 的責任。 | T6、T7、T8 | 都直接改變 model 文件的 active／supplementary／future 邊界，並以 C++ 實作為核對依據。 | `model.md`、`module_format.md`、`inference/src/model.cpp`；transcript L1501–L1560、L2388–L2971 | PhyClone-compatible `xi` target 與完整 validation 仍不是 current runtime；需避免文件與實作再次漂移。 |
| 4. 素材盤點與未來 HTML 準備 | 確認目前 assets 能當參考素材，但不足以直接支撐完整教學圖。 | T4 | 兩輪盤點都回答同一個交付問題：哪些圖已有、哪些圖必須重畫、HTML 未來如何接入。 | `assets/`、`module.md` F0–F15 清單；transcript 約 L976–L1055、L2080–L2200、L2977–L3049 | 尚缺可直接貼入 HTML 的 SVG；需優先補 P0 圖並接入 BAM／SNV／REF-ALT 說明。 |
| 5. 文件版本與研究 provenance | 把文件變更獨立提交，並將 08/19–08/26 daily 壓縮成可持續維護的單一週摘要。 | T9、T10 | 都是研究工作產物的版本與回查治理，承接前四個主題但不改變 C++／Python 行為。 | Git `8f58e9e`；`daily/20260819_20260826_week/index.html` | 本日報尚未 commit；其他既有工作樹變更仍需另行判斷，不應混入本日報 commit。 |

## Coverage checklist

| task | 納入主題／排除理由 |
|---|---|
| T1 | 主題 1：模組 contract 與視覺規格。 |
| T2 | 主題 2：skill 入口與路徑核對。 |
| T3 | 主題 2：skill workflow 與 validator 結果。 |
| T4 | 主題 4：assets 與 F0–F15 覆蓋率。 |
| T5 | 主題 1：module 主線簡化；與 Model 邊界重疊但交付物是解說文件。 |
| T6 | 主題 3：移除 Model B／HP likelihood 細節。 |
| T7 | 主題 3：phi、CCF、eta、multiplicity 定義。 |
| T8 | 主題 3：current C++ baseline 公式。 |
| T9 | 主題 5：scoped docs commit。 |
| T10 | 主題 5：跨日 daily 壓縮與日期目錄整理。 |

## 日期 coverage

- 2026-08-27：有 2 個 root Codex session；內容由 T1–T10 完整涵蓋。
- 平行 rollout：已合併到其 root session 的 task，不另計日期或主題。
