# bulk long read＋single-cell 公開資料調查：摘要

日期：2026-10-26。只讀目錄與 README，沒有下載資料。全文：[`fulltext.md`](fulltext.md)。

## 結論

- 最好的候選是 GIAB HG008（胰臟癌細胞株）。bulk ONT 和 PacBio 與 119 個 PTA 單細胞都來自 p23 批次（0823p23）。〔repo〕全文 §1、§4.1
- 本機共用副本在 `/big8_disk/yungjen114/data/HG008/`，只有 bulk long read 和 NIST benchmark，沒有單細胞和 8 株 clone。不要重複下載。〔repo〕全文 §1
- 第二候選是 GIAB HG009：10 株單細胞衍生 clone，bulk 有 PacBio Revio；本次沒看到 ONT。〔repo〕全文 §1
- COLO829 有 10x scCNV（4 個 subclone），但沒有樹，也不是同一批細胞。〔論文〕全文 §1
- 在這次查的來源中，沒找到公開的「病人腫瘤＋bulk long read＋single-cell DNA」資料。B04 是 JGA 受控，B03 要 MTA。〔repo〕全文 §1

## 使用限制

- HG008 的單細胞是 UG100 定序，不是 long read；8 株 clone 有 PacBio Revio。拿來當驗證參考前，要先對 `CLAUDE.md` 的需求表（輸入與驗證參考都只用 long read）。〔推論〕
- §3、§4.4 的用法建議是推論，不是實測。

## 要查細節時

全文：§2 候選比較表、§3 HG008 用法、§4.1 各批次 passage 與 coverage、§4.2 單細胞檔案位置與大小、§4.3 clone 位置、§5 來源。
