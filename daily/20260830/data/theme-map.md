# 2026-08-30 主題地圖

主線：把 `module_format` 從「以文字模擬素材」轉成由可追溯 SVG 元件、保留強度與視覺槽位驅動的可重生說明。

| 主題 | 主題 summary | 包含 task | 為何屬於同一主題 | 代表證據 | 未完成事項 |
|---|---|---|---|---|---|
| 視覺生成治理 | 將素材採用、來源區段、保留強度、槽位數量與渲染驗收變成明確契約。 | 規則重構、Chromium 驗證、視覺槽位契約。 | 都是在限制 HTML 重生如何消費既有 Markdown 與素材。 | slide 6 從一個合併紀錄拆成四個 anchored 槽位；12 張 render checks 通過。 | 之後新頁仍需在 Markdown 明示需要鎖定或可替換的素材。 |
| Canonical SNV 視覺元件 | 以四個獨立、可組裝 SVG 說明 identity、read count、CN 與 purity。 | CN、read pileup、Identity 元件。 | 同屬 slide 3 的 canonical SNV row，且元件互補、不互相取代。 | `major_cn=3 + minor_cn=1 = total_cn=4`；`REF=3, ALT=2, total=5`。 | 元件預覽與正式 SVG 必須持續分層，避免把 QA PNG 當正式素材。 |
| 開發環境維護 | 清理不需要的擴充、釐清啟動警告，並完成本批 repo 版本保存。 | skill/plugin 清理、MCP 診斷、Git 提交、skill 翻譯。 | 都服務於後續可用的 Codex 與可讀的元件建構流程。 | `9fbfe3c` 已提交且未 push。 | data-analytics 的安裝狀態仍可能讓 MCP warning 重現，尚未根治。 |

## Coverage checklist

- 清理 plugin／MCP 診斷／提交：納入「開發環境維護」。
- spec-paged-html 與 visual-slot 修改：納入「視覺生成治理」。
- Copy number、read pileup、Identity：納入「Canonical SNV 視覺元件」。
- svg-component-builder 繁中化：納入「開發環境維護」。
