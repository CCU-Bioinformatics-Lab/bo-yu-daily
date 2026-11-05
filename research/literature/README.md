# 文獻目錄

所有文獻筆記集中在本目錄。找論文先查 [`research/index.md`](../index.md)，再讀該篇的 `summary.md`。

## 結構

| 路徑 | 內容 |
|---|---|
| [`papers/`](papers/) | 逐篇資料，一篇一個目錄：`summary.md`、`fulltext.md`、`source.md`、本機 PDF。ID 前綴代表收錄來源：A／B = 2026 文獻調查，M = 方法調查，R = 真值樹來源 |
| [`SYNTHESIS_phyclone_longphase.md`](SYNTHESIS_phyclone_longphase.md) | 跨論文去重與 PhyClone × longphase-s 整合地圖 |
| [`surveys/patient_sc_longread_2026/`](surveys/patient_sc_longread_2026/summary.md) | 病人 single-cell 與 long-read／haplotype 特徵調查（A／B 類摘要、資料與程式可得性、改進方案） |
| [`surveys/methods_survey/`](surveys/methods_survey/summary.md) | 腫瘤演化樹重建方法調查（2019–2026） |
| [`surveys/longread_tree_search_2026-10-19/`](surveys/longread_tree_search_2026-10-19/summary.md) | long-read 建樹文獻補搜 |
| [`surveys/sc_longread_datasets_2026-10-26/`](surveys/sc_longread_datasets_2026-10-26/summary.md) | bulk long read＋single-cell 公開資料調查 |

HCC1395 golden tree（H01）的筆記不在本目錄，見 [`../hcc1395_golden_tree_research/`](../hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/summary.md)。

## 規則

- 新論文放 `papers/<ID>_<短名>_<年>/`，不要放進 `surveys/`。
- 新增論文：目錄內放 `summary.md`、`fulltext.md`、`source.md`，再到 `research/index.md`「論文」加一列（路徑、一句話、關鍵字）。

- 改 2026 文獻調查的 PDF 後，重產 manifest：

```bash
python3 research/literature/surveys/patient_sc_longread_2026/tools/validate_bundle.py --write-manifest
```
