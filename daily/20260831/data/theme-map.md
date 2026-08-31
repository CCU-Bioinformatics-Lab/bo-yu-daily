# 2026-08-31 主題地圖

主線：先把 inference 的責任、狀態與驗證邊界說準，再把這套語意轉成可重用的 topology／fraction 視覺元件，最後接到 `module_format` 的 slide 7 並留下可回溯的版本邊界。

| 主題 | 主題 summary | 包含的 task | 為何屬於同一主題 | 代表證據 | 未完成事項 |
|---|---|---|---|---|---|
| Inference contract 與 claim boundary | 完成 inference「在固定 model 規則內探索候選狀態」的白話邊界，定義可摘要的候選輸出與正確的 VAF predictive check；正式逐 SNV predictive gate 尚未關閉。 | Inference 演算法目的與責任邊界；`module_format.md` 文件衝突整理；後驗結果摘要語意定案；預測 VAF 與真實 VAF 的比較方法 | 四者共同回答 inference 到底做什麼、輸出能說到哪裡、資料驗證如何對接；文件修正與 predictive check 是同一條語意／驗證生命週期。 | `T + η` 探索邊界（`transcript_full.txt:179–438`）；`alt_reads / total_reads` 對 `Σ weight × xi`（`1241–1360`）。 | 要決定 assignment schema／founder 限制等文件—實作落差是否修正；一般 runtime 尚需逐 SNV deterministic `predicted_xi` 才能開正式 gate。 |
| Reusable model-rules visuals | 把 model rules 從純文字改成可數、可組裝、可重用的 topology／fraction 元件，並修正透明背景與標籤碰線等可讀性問題。 | Canonical SNV row SVG 化；Model rules 可重用視覺元件 | 都產生可重用 SVG 素材或其組裝規則，服務同一個「用圖呈現 model／inference state」的元件層。 | `candidate_tree_state_a/b/c.svg` 的不同拓樸＋`Ση=1.00`（`1739–2100`）；standalone K=6 與 `C3/C5/C6` 避線（`3239–3370`）。 | 中間 composite `model_inference_loop.svg` 已依使用者要求刪除；若未來要恢復完整 loop，需重新決定新的 component source，不可把舊版當現行成品。 |
| `module_format` 消費端交付 | 將 inference visual 接到 7-slide HTML／Markdown 對照，移除會誤導 active backend 的互動 teaching case，並保存一個未 push 的版本基線。 | `module_format` slide 7 最終接入；視覺更新版本保存 | 前者是消費端呈現與來源回寫，後者是同一批呈現變更的 provenance 保存；兩者共同形成使用者看得到的交付。 | `slide-7-inference-module`、`assets/png_to_svg/inference_module.svg` 與 Markdown slot（`3429–3574`）；`ae8f794`（`3432–3470`）。 | slide 7 最終 image-only revision、`module_format.md`／generator diff 與新 SVG wrapper 尚未另行 commit；branch 也尚未 push。 |

## Coverage checklist

- `T1` Inference 演算法目的與責任邊界 → **Inference contract 與 claim boundary**。
- `T2` `module_format.md` 文件衝突整理 → **Inference contract 與 claim boundary**。
- `T3` 後驗結果摘要語意定案 → **Inference contract 與 claim boundary**。
- `T4` 預測 VAF 與真實 VAF 的比較方法 → **Inference contract 與 claim boundary**。
- `T5` Canonical SNV row SVG 化 → **Reusable model-rules visuals**。
- `T6` Model rules 可重用視覺元件 → **Reusable model-rules visuals**。
- `T7` `module_format` slide 7 最終接入 → **`module_format` 消費端交付**。
- `T8` 視覺更新版本保存 → **`module_format` 消費端交付**。
- `codex:01a05829-4e7a-7541-a03d-933d2ed27e34` → 排除：本次日報整理／抽取流程本身，不是被回顧的研究交付任務。

## 日期 × 主題檢查

本報告為單日來源（2026-08-31）；三個主題均有當日代表證據，沒有跨日素材需要排除。
