# long-read 特徵建樹文獻補搜：摘要

日期：2026-10-19。全文：[`fulltext.md`](fulltext.md)。

## 結論

- 在這次搜尋範圍內（4 個 subagent，至 2026-10-19），沒找到把 long-read HP／PS 或同 read 共現放進 tree likelihood 或 prior 的已發表腫瘤 clone tree 方法。〔repo〕全文 §1
- 現有工具只做到「產生 phased feature」或「把變異放到給定的樹上」，沒有用 phasing 約束 topology。〔repo〕全文 §1、§4
- long read 有實際角色的已收錄研究：B04（同 read pair order 選 linear model，只在 S14）、B01（ONT SNV 建樹，phased SV 和 CN 事後放上樹）。M08 只提供可移植的模型。〔repo〕全文 §2
- 可接的輸入：longphase-s 的 somatic haplotag、Wakhan 的 subclonal hp1／hp2 CN。〔推論〕全文 §1

## 使用限制

- 結論來自 subagent 搜尋，原始報告已刪除。引用前要回論文核對。
- §5 的新穎點提案是分析推論，也沒有實作。同 read 共現在 2026-11-04 已決定先不列為需求（`CLAUDE.md`）。
- §6 列出沒抓到的來源。B09 已在 2026-11-05 從 repo 刪除。

## 要查細節時

全文：§2 有建樹步驟的研究、§3 不納入的研究與原因、§4 phased feature 工具、§5 新穎點提案、§6 未驗證項目。
