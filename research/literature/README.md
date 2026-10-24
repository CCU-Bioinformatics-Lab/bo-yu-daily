# 文獻目錄

所有文獻筆記集中在本目錄。找論文先看 [分類索引](PAPER_CATEGORIES.md)。

## 結構

| 路徑 | 內容 |
|---|---|
| [`papers/`](papers/) | 逐篇筆記，一篇一個目錄（README、`paper.txt`、PDF）。ID 前綴代表收錄來源：A／B = 2026 文獻調查，M = 方法調查，R = 真值樹來源 |
| [`PAPER_CATEGORIES.md`](PAPER_CATEGORIES.md) | 分類索引：定序平台 × single-cell 真值（C1、C2、C3a、C3b） |
| [`paper_categories.tsv`](paper_categories.tsv) | 分類總表，唯一來源 |
| [`papers_by_category/`](papers_by_category/) | 依分類的 symlink 目錄，由腳本產生，不要手改 |
| [`SYNTHESIS_phyclone_longphase.md`](SYNTHESIS_phyclone_longphase.md) | 跨論文去重與 PhyClone × longphase-s 整合地圖 |
| [`surveys/patient_sc_longread_2026/`](surveys/patient_sc_longread_2026/README.md) | 病人 single-cell 與 long-read／haplotype 特徵調查（A／B 類摘要、資料與程式可得性、改進方案） |
| [`surveys/methods_survey/`](surveys/methods_survey/README.md) | 腫瘤演化樹重建方法調查（2019–2026）；`workers/` 是分工檢索的原始紀錄 |
| [`surveys/longread_tree_search_2026-10-19/`](surveys/longread_tree_search_2026-10-19/README.md) | long-read 建樹文獻補搜；`raw/` 是原始搜尋結果 |
| `tools/` | `sync_paper_categories.py`：由 TSV 同步 front-matter、symlink 與分類表 |

HCC1395 golden tree（H01）的筆記不在本目錄，見 [`../hcc1395_golden_tree_research/`](../hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md)。

## 規則

- 新論文放 `papers/<ID>_<短名>_<年>/`，不要放進 `surveys/`。
- 新增或改分類：只改 `paper_categories.tsv`，再執行：

```bash
python3 research/literature/tools/sync_paper_categories.py
python3 research/literature/tools/sync_paper_categories.py --check
```

- 改 2026 文獻調查的 PDF 後，重產 manifest：

```bash
python3 research/literature/surveys/patient_sc_longread_2026/tools/validate_bundle.py --write-manifest
```
