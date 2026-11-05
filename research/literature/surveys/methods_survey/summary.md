# 腫瘤演化樹重建方法調查：摘要

查核日：2026-10-16。全文：[`fulltext.md`](fulltext.md)。

## 結論

- 這份調查只收「主要貢獻是推論 topology」的方法。去重後有 45 個：bulk SNV＋CN 13、single-cell SNV 10、single-cell SNV＋CN 6、CN／event phylogeny 11、多模態 5、read-level 連鎖 0。〔repo〕全文「總覽」
- PhyClone 屬 bulk SNV＋CN＋purity 類。主要競品是 Pairtree、Orchard、CONIPHER、PICTograph。〔repo〕全文「總覽」
- 同 read 共現推樹不算新穎點：BitPhylogeny 和 B04 已做過。〔推論〕全文「Novelty 邊界」
- 在這次搜尋範圍內（至 2026-10-16），沒找到同時做到這 4 點的方法：bulk SNV＋CN＋purity likelihood、同 read 共現 likelihood、HP 配 haplotype CN 約束 multiplicity、SMC／PG 推 topology。〔推論〕全文「Novelty 邊界」
- 主指標建議用不依賴 clone 編號的 pairwise 祖先關係：SMC-Het ADM、Pairtree 的關係重建誤差。〔repo〕全文「Benchmark 與評估指標」

## 使用限制

- 同 read 共現在 2026-11-04 已決定先不列為需求（`CLAUDE.md`），新穎點要照這個前提重看。
- 只有 M01、M04–M06、M08 讀過全文並建 dossier；其他方法沒有下載 PDF。〔repo〕全文「待核與已知缺口」
- 5 個 subagent 的原始報告已在 2026-10-29 刪除，要查用 git 歷史。全文提到的 `evaluation_v1.md` 現在不存在。

## 要查細節時

全文的章節：收錄判準、主選總表（A–F）、邊界方法、Novelty 邊界、Benchmark 與指標、精讀順序、待核缺口、逐篇 dossier。
