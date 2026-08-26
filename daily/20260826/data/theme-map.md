# 2026-08-26 主題地圖

## 當日主線

今天把兩件事往前推：先把 PhyClone 的 CNV／SNV 輸入與 VAF likelihood 寫成可核對的 target 規格，再把 repo 的模組邊界、歷史演進與 HTML 報告的誤讀風險整理清楚。共同的收斂點是：文件可以先定義方向，但目前 runtime、獨立 validation runner 與 formal biological claim 都不能被提前宣稱完成。

| 主題 | 主題 summary | 包含的 task | 為何屬於同一主題 | 代表證據 | 未完成事項 |
|---|---|---|---|---|---|
| PhyClone 輸入與模型契約 | 把「一筆 SNV 如何帶著 reads、CN、normal baseline、purity 與 error floor 進入 likelihood」說清楚，並把新公式和舊 runtime 的邊界寫明。 | PhyClone CNV／SNV 輸入與 VAF 公式文件化 | 共同推進同一個 PhyClone-compatible model contract，欄位、`normal_cn`、CN timing、`xi` 與 Binomial likelihood 互相依賴。 | `model.md:120`、`data.md:66`、`research/phyclone/phyclone_q_formula_comparison.zh-TW.md:1`；原文 9–353、2218–2562。 | `error_rate=0.001`、`normal_cn`、`tumour_content`、`xi` 尚未進入 C++／Python scoring；predictive validation 維持 BLOCKED。 |
| 架構說明與報告可信度 | 將研究生產線從資料、模型、SMC、輸出到驗證的責任說白話，並用唯讀審查校正「核心模組、diagnostic candidate、validation、pilot」的語意。 | `arch.md` 模組與 daily 時間線整理；`arch_eli5_report.html` 品質與語意審查 | 兩項任務共同服務同一份架構說明交付物；審查結果直接約束報告如何呈現模組邊界與證據強度。 | `arch.md:7`–`arch.md:15`、`arch.md:57`、`experiment_workflow.md:26`、`arch_eli5_report.html:1`；原文 2013–2212、2655–2770。 | 若要再修 HTML，需補明確的 `output → validation`、workflow gate、`_SUCCESS` 不等於 biological truth；standard HTML validator 仍未可用。 |

## Coverage checklist

- [x] PhyClone CNV／SNV 輸入、`normal_cn` 與 `xi` 文件任務 → 「PhyClone 輸入與模型契約」。
- [x] `arch.md` 核心模組責任與 daily 時間線 → 「架構說明與報告可信度」。
- [x] `arch_eli5_report.html` 結構、accessibility、ELI5 語意審查 → 「架構說明與報告可信度」。
- [x] 追問、平行 subagent 產物、收斂回覆均已合併，不另算任務。
- [x] 本日來源範圍只有 2026-08-26；沒有其他日期素材被誤混入本日 task 表。
