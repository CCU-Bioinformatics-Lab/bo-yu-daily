# B06 官方 PDF 來源與驗證

取得日期：2026-10-15。來源為 **NIH/NLM/NCBI PubMed Central 官方 PMC Article Datasets on AWS**；未使用非授權 mirror，未解人機驗證或繞過登入。

## 保存的版本

- DOI：[10.1101/gr.279617.124](https://doi.org/10.1101/gr.279617.124)。正式版 *Genome Research* 35(4):671–685 (2025)。
- PMCID/version：`PMC12047258.1`。官方 [JSON metadata](https://pmc-oa-opendata.s3.amazonaws.com/PMC12047258.1/PMC12047258.1.json) 已存為 [oa_metadata.json](oa_metadata.json)。其中 `is_manuscript=false`、`is_retracted=false`、`license_code=CC BY-NC`。
- [主文 PDF 官方直鏈](https://pmc-oa-opendata.s3.amazonaws.com/PMC12047258.1/PMC12047258.1.pdf) → [paper.pdf](paper.pdf)：15 個實體頁、1,768,901 bytes，PDF 1.3，title metadata `GR279617Zen 671..685`。
- [補充 PDF 官方直鏈](https://pmc-oa-opendata.s3.amazonaws.com/PMC12047258.1/Supplemental_Figures.pdf) → [supplement.pdf](supplement.pdf)：23 個實體頁、4,046,463 bytes，PDF 1.6。
- [paper.txt](paper.txt)、[supplement.txt](supplement.txt) 均由相應 PDF 以 `pdftotext -layout` 成功抽出。

## 校驗

`file` 確認兩檔為 PDF，`pdfinfo` 可解析 page tree 與 metadata；不是以 `.pdf` 命名的 HTML。MD5 與官方 JSON 中各物件的 MD5 完全一致。

| 檔案 | 官方 MD5＝本機 MD5 | 本機 SHA-256 |
|---|---|---|
| paper.pdf | `d21afe1c62144979f06e890928edd39b` | `5e69c92f8dfa6db09d8a0911b8e8d7ed58242017feefeb6f1f9eaa8b815d513a` |
| supplement.pdf | `aeaf185870f532d5d4c3a76efd549fb4` | `923c7a6752579c1dc3fdf4cfc1a39d57d28122983068fac562800ca48e17132b` |

## 為何改用 AWS

PMC 的舊 `oa.fcgi` API 與 FTP `oa_package` 在本次均回 404。這是分發服務退役，不能據此判定論文沒有開放 PDF。NCBI 官方 [Cloud Service](https://pmc.ncbi.nlm.nih.gov/tools/cloud/) 與 [Accessing PMC Article Datasets Using Amazon Web Services](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/) 說明：legacy FTP/API/cloud files 已於 2026 年 8 月移除，新版使用 `pmc-oa-opendata` bucket，以 PMCID.version prefix 組織。依此官方說明列出本 PMCID 的公開 objects，再取得上述 PDF。

Publisher download 回 403，PMC viewer download 回傳「Preparing to download」HTML 的先前結果，保留為 `paper.download_challenge.html` 和 `supplement.download_challenge.html` 供稽核；已不把它們當 PDF。EPMC render 亦未成功。本次成功來源為官方 AWS，與這些失敗路徑無關。

資料來源致謝：NIH NLM NCBI PubMed Central (PMC) Article Datasets — Full-Text Biomedical and Life Sciences Journal Articles on AWS，accessed 2026-10-15，資料集入口 [AWS Open Data Registry](https://registry.opendata.aws/ncbi-pmc)。論文內容授權仍以原作者/期刊 CC BY-NC 條款為準；沒有暗示 NIH/NLM 認可本研究報告。
