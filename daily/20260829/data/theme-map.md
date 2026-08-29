# 2026-08-29 主題地圖

## 主題摘要

| 主題 | 主題 summary | 包含的 task | 為何屬於同一主題 | 代表證據 | 未完成事項 |
|---|---|---|---|---|---|
| 規格 → 可讀的 HTML | 把 Markdown 的模組邊界轉成可翻頁、可追溯且能看見既有素材的 HTML。 | T1、T2 | 同一個消費端交付物；T2 是 T1 的素材忠實度修正。 | `module_format.html` 6→7 頁、asset-derived SVG、`full_arch.svg`；L9-L100、L421-L467 | Firefox 截圖驗證受 snap／環境問題限制。 |
| 可重用規格與素材管線 | 將 Markdown→HTML 與 PNG/JPEG→SVG 的規則整理成可再次呼叫的技能與 wrapper 管線。 | T3、T4 | 兩者共同提供後續視覺化的輸入契約、來源追溯與格式統一。 | `spec-paged-html` 泛化／全域安裝；23→41 個 SVG wrapper；L103-L140、L187-L250、L252-L420、L3479-L3530 | wrapper 仍是內嵌 raster，不是 path-level vector。 |
| 語意導向的 SVG 元件 | 從「缺少關係圖」與原子元素開始，修正載入／排版，再以數量契約重建九張 component。 | T5、T6、T7 | 都在同一條 component 生命週期：需求審查 → 組裝除錯 → 語意與 QA 重製。 | P0/P1 roadmap；九張 component、99:1 purity、REF=3/ALT=2、major=3/minor=1；L2303-L2333、L3592-L3800、L3888-L4092 | 九張目前是 machine-validated，仍待使用者做最終視覺接受。 |
| 可回溯的程式交付 | 把文件、素材與 component 產物分組提交，讓後續能獨立回溯。 | T8 | 這是前述三個主題的版本控制交付，不改變圖像語意。 | `26a7b84`、`b132639`、`3ff9083`；L4105-L4153 | branch ahead 3；尚未 push。 |

## Coverage checklist

| Task | 納入主題 | 覆蓋判定 |
|---|---|---|
| T1 Markdown 規格轉分頁 HTML | 規格 → 可讀的 HTML | 已納入；形成初始 HTML 與導覽。 |
| T2 HTML 素材忠實度與版面修正 | 規格 → 可讀的 HTML | 已納入；是同一 HTML 交付物的後續修正。 |
| T3 `spec-paged-html` 泛化、改名與安裝 | 可重用規格與素材管線 | 已納入；提供多文件與全域選用能力。 |
| T4 Raster assets SVG wrapper | 可重用規格與素材管線 | 已納入；提供 PNG/JPEG 對應 SVG 格式。 |
| T5 新繪資訊缺口與原子元素契約 | 語意導向的 SVG 元件 | 已納入；決定先做關係圖與最小元素。 |
| T6 第一版 component 組裝與載入／版面修正 | 語意導向的 SVG 元件 | 已納入；屬於可重建 component 的除錯階段。 |
| T7 語意契約與 `svg-component-builder` 重製 | 語意導向的 SVG 元件 | 已納入；以數量、比例與 bounds QA 收斂最終產物。 |
| T8 分類提交視覺化與資產變更 | 可回溯的程式交付 | 已納入；三個 commit 完成且未 push。 |

## 當日主線

先把 `module_format.md` 做成可閱讀的素材驅動 HTML，再把「不能硬放」的問題拆成原子元素與語意契約，最後以可驗證的 SVG component 與分組 commit 交付。機器驗證已完成；人的最後視覺判定與 HTML 截圖限制仍明確保留。
