# 2026-09-01 主題地圖

## 當日主線

先把「誰提出候選、誰計算與評分」講準，再把這個邊界落成可回查的 SVG 素材與 `module_format` 消費端畫面；最後留下兩個仍需人工確認的視覺／語意關卡。

| 主題 | 主題 summary | 包含的 task | 為何屬於同一主題 | 代表證據 | 未完成事項 |
|---|---|---|---|---|---|
| 01. 執行環境清理 | 移除失效 skill，清掉今日最早的 loader warning。 | 移除失效 `daily-work-html` skill | 共同成果是恢復技能載入環境；不涉及研究模型或 repo 交付物。 | `codex:01a05c01-e93b-7d12-8ff9-64360f629776`，08:07–08:10 UTC | 無；刪除位置在工作區外，後續需重載／新 session 才能觀察 warning 是否消失。 |
| 02. Model／inference contract | 把候選 state、派生 CCF、CN/multiplicity candidates 與 read likelihood 分層，避免流程圖把 latent assignment 誤畫成 particle state。 | model／inference 語意查核 | 共同回答同一個高階問題：「SMC 實際探索什麼，model 如何用資料評分？」文件、C++、worker evidence 是同一條定義與驗證鏈。 | `φ_v = η_v + Σdesc η`；particle=`T+η`；`z_i/g_i` marginalize；`major_cn=3, minor_cn=1, total_cn=4` 的 candidate 例 | `minor_cn` 的文字描述與現行 candidate enumeration 還有落差；`model_process.svg` 底部 joint posterior 是否保留 `z` 仍需最後定義。 |
| 03. 可重用 SVG 素材治理 | 將固定 K=3 topology、η/φ、reads 與六階段 scoring 圖拆成可回查的既有素材與組合元件。 | 素材與術語對照；K=3 clone tree；REF／ALT read 元件；六階段 composite | 共同交付是 visual primitive／composite library，素材都有路徑、preview、spec 或 QA 可追溯。 | `fixed_k3_clone_tree.svg`、`ref_read.svg`／`alt_read.svg`、`model_process_composite.svg`；`model_process_composite` 已組合 78 個元素 | composite 與 standalone read 元件尚未完成使用者的人工視覺核准；K=3 仍是 illustrative asset，不代表 primary workflow K=3。 |
| 04. `module_format` 消費端交付 | 將定義與素材選擇同步落入 Markdown、HTML 生成器與投影片 slide 3–5，讓使用者可直接看到更新後流程。 | `module_format` slides 3–5 同步；model-process rollback／移除 z 並嵌回 slide-5 | 兩者都修改同一份 module 的來源、生成器與使用者可見輸出；後者是前者的最後視覺校正。 | slide-3 `Data input目的`、slide-4 四大類別＋`read_pileup.svg`、slide-5 `model_process.svg`；`PASS: 16 rendered slide checks` | 最後一輪 slide-5 的實際瀏覽器人工驗收受 Firefox sandbox 限制；需確認新版嵌入圖在讀者尺寸下仍清楚。 |

## Coverage checklist

| task | coverage |
|---|---|
| 移除失效 `daily-work-html` skill | 納入主題 01 |
| model／inference 語意查核 | 納入主題 02 |
| 素材與術語對照表 | 納入主題 03，並支援主題 04 |
| K=3 topology-only clone tree | 納入主題 03 |
| REF／ALT read 元件擷取 | 納入主題 03；slide-4 後續選擇 `read_pileup.svg` 已在主題 04 記錄 |
| 六階段 model-process composite | 納入主題 03 |
| `module_format` slides 3–5 同步 | 納入主題 04 |
| rollback、移除 z、嵌回 slide-5 | 納入主題 04；其語意理由回扣主題 02 |

## 日期 × 主題檢查

本報告為單日來源（2026-09-01）；四個主題均有當日 session 代表證據，無跨日期素材需要排除。
