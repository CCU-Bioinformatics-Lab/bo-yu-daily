# 腫瘤演化歷史文獻調查：第一手資料

日期：2026-11-05。不重複的論文 97 篇（以 DOI 計）：全文 87 篇、只有摘要 9 篇、只有網頁片段 1 篇。摘要與片段不當主要證據。

「全文」表示取得全文，不表示逐字讀完。多數論文用關鍵字定位後讀相關段落，補充資料都沒讀。同一篇在不同主題有多個 ID 時，列在同一列，算一份證據。

## 重建與核對

- `fulltext_cache/`：抓下來的論文文字，只留本機（`.gitignore` 已擋）。新 clone 的 repo 沒有；用下表的 DOI 和 `tools/lit_fetch_paper.py` 重抓。
- `claims/NN.tsv`：每個主題的引文表（每段 ≤ 30 字的英文原文）。核對：`python3 -I tools/lit_check_quotes.py research/literature/surveys/tumor_evolution_history_2026-11-05/claims/*.tsv`。
- `gap_search_europepmc.txt`：主 agent 補搜的查詢與結果清單。
- 引文核對只證明這段文字出現在原文，不證明中文 claim 的解讀正確。

## 取得方式的已知問題

- 主題 04、06、08 的子代理曾用偽裝瀏覽器的 User-Agent（`curl -A "Mozilla/5.0"`、`urllib`）抓 bioRxiv、PMC、PubMed 頁面；主題 01 的同樣嘗試被權限檢查擋下。任務書只允許 `fetch_paper.py` 與 WebFetch，這不是授權的做法。第一行標 `WEB:` 的 `fulltext_cache` 檔案可能來自這類抓取。
- 核心 preprint（E4-26／E8-01）的關鍵數字已另用 WebFetch 重新確認（見 `summary.md`）。其他 `WEB:` 檔案沒有逐一重抓。這些檔案只留本機，不進 git。

## 論文

| ID | 論文 | 讀取層級 | 連結 |
|---|---|---|---|
| B04、E4-B04 | Sakamoto 2022, Nat Commun | 全文 | https://doi.org/10.1038/s41467-022-31133-6 |
| E1-01、E2-12、E3-17 | Williams 2016, Nat Genet | 全文 | https://doi.org/10.1038/ng.3489 |
| E1-02、E2-13、E3-20 | Tarabichi 2018, Nat Genet | 全文 | https://doi.org/10.1038/s41588-018-0258-x |
| E1-03 | Sottoriva 2015, Nat Genet | 全文 | https://doi.org/10.1038/ng.3214 |
| E1-04、E2-14 | Williams 2018, Nat Genet | 全文 | https://doi.org/10.1038/s41588-018-0128-6 |
| E1-05 | Turajlic 2018, Cell | 全文 | https://doi.org/10.1016/j.cell.2018.03.043 |
| E1-06 | Waclaw 2015, Nature | 全文 | https://doi.org/10.1038/nature14971 |
| E1-07 | Noble 2022, Nat Ecol Evol | 全文 | https://doi.org/10.1038/s41559-021-01615-9 |
| E1-08 | Chkhaidze 2019, PLoS Comput Biol | 全文 | https://doi.org/10.1371/journal.pcbi.1007243 |
| E1-09 | Caravagna 2020, Nat Genet | 全文 | https://doi.org/10.1038/s41588-020-0675-5 |
| E1-10、E2-03、E3-13 | Dentro 2021, Cell | 全文 | https://doi.org/10.1016/j.cell.2021.03.009 |
| E1-11 | Gao 2016, Nat Genet | 全文 | https://doi.org/10.1038/ng.3641 |
| E1-12、E2-16 | Minussi 2021, Nature | 全文 | https://doi.org/10.1038/s41586-021-03357-x |
| E1-13 | Sun 2017, Nat Genet | 全文 | https://doi.org/10.1038/ng.3891 |
| E1-14 | Morita 2020, Nat Commun | 全文 | https://doi.org/10.1038/s41467-020-19119-8 |
| E1-17 | Heide 2018（bioRxiv 回覆） | 網頁片段 | https://doi.org/10.1101/274142 |
| E1-23 | Tung & Durrett 2021, PLoS Comput Biol | 全文 | https://doi.org/10.1371/journal.pcbi.1008701 |
| E2-01 | Martincorena 2017, Cell | 全文 | https://doi.org/10.1016/j.cell.2017.09.042 |
| E2-04、E3-03、E7-01 | Gerstung 2020, Nature | 全文 | https://doi.org/10.1038/s41586-019-1907-7 |
| E2-06、E3-12 | McGranahan 2015, Sci Transl Med | 全文 | https://doi.org/10.1126/scitranslmed.aaa1408 |
| E2-08 | Lakatos 2020, Nat Genet | 全文 | https://doi.org/10.1038/s41588-020-0687-1 |
| E2-09 | Zapata 2023, Nat Genet | 全文 | https://doi.org/10.1038/s41588-023-01313-1 |
| E2-15 | Miles 2020, Nature | 全文 | https://doi.org/10.1038/s41586-020-2864-x |
| E2-17 | Van den Eynden 2019, Nat Genet | 全文 | https://doi.org/10.1038/s41588-019-0532-6 |
| E2-25 | Stein 2026, Nat Commun | 全文 | https://doi.org/10.1038/s41467-026-69363-7 |
| E2-26、E5-05 | Salehi 2021, Nature | 全文 | https://doi.org/10.1038/s41586-021-03648-3 |
| E2-27 | Zapata 2018, Genome Biology | 全文 | https://doi.org/10.1186/s13059-018-1434-0 |
| E3-01 | Alexandrov 2015, Nat Genet | 全文 | https://doi.org/10.1038/ng.3441 |
| E3-04、E7-06 | Mitchell 2018, Cell | 全文 | https://doi.org/10.1016/j.cell.2018.02.020 |
| E3-05 | Lee-Six 2018, Nature | 全文 | https://doi.org/10.1038/s41586-018-0497-0 |
| E3-07 | Abascal 2021, Nature | 摘要 | https://doi.org/10.1038/s41586-021-03477-4 |
| E3-08 | Cagan 2022, Nature | 全文 | https://doi.org/10.1038/s41586-022-04618-z |
| E3-11 | Frankell 2023, Nature（TRACERx421）— 10.1038/s41586-023-05783-5 | 全文 | https://doi.org/10.1038/s41586-023-05783-5 |
| E3-14 | Campbell 2017, Cell | 全文 | https://doi.org/10.1016/j.cell.2017.09.048 |
| E3-16 | Liu 2024, Nature（HiDEF-seq）— 10.1038/s41586-024-07532-8 | 全文 | https://doi.org/10.1038/s41586-024-07532-8 |
| E3-18 | Werner 2020, Nat Commun | 全文 | https://doi.org/10.1038/s41467-020-14844-6 |
| E3-21 | Blokzijl 2016, Nature | 全文 | https://doi.org/10.1038/nature19768 |
| E4-01 | Aitken 2020, Nature | 全文 | https://doi.org/10.1038/s41586-020-2435-1 |
| E4-02 | Nik-Zainal 2012, Cell | 全文 | https://doi.org/10.1016/j.cell.2012.04.024 |
| E4-03 | Mas-Ponte & Supek 2020, Nat Genet | 全文 | https://doi.org/10.1038/s41588-020-0674-6 |
| E4-04、E8-11 | Jäger 2013, Cell | 全文 | https://doi.org/10.1016/j.cell.2013.09.042 |
| E4-05 | Lawrence 2013, Nature | 全文 | https://doi.org/10.1038/nature12213 |
| E4-08 | Polak 2015, Nature | 全文 | https://doi.org/10.1038/nature14221 |
| E4-09 | Haradhvala 2016, Cell | 全文 | https://doi.org/10.1016/j.cell.2015.12.050 |
| E4-10 | Knudson 1971, PNAS | 全文 | https://doi.org/10.1073/pnas.68.4.820 |
| E4-12 | Gorelick 2020, Nature | 全文 | https://doi.org/10.1038/s41586-020-2315-8 |
| E4-13 | Vasan 2019, Science | 全文 | https://doi.org/10.1126/science.aaw9032 |
| E4-14 | Mukhopadhyay 2014, PLoS Genet | 全文 | https://doi.org/10.1371/journal.pgen.1004319 |
| E4-15 | Koren 2014, Cell | 全文 | https://doi.org/10.1016/j.cell.2014.10.025 |
| E4-17、E7-08 | Bielski 2018, Cancer Cell | 全文 | https://doi.org/10.1016/j.ccell.2018.10.003 |
| E4-18 | Park 2018, Nat Commun | 全文 | https://doi.org/10.1038/s41467-018-04900-7 |
| E4-20 | Bergstrom 2022, Nature | 全文 | https://doi.org/10.1038/s41586-022-04398-6 |
| E4-26、E8-01 | Lefèbvre 2026, bioRxiv preprint | 全文 | https://doi.org/10.64898/2026.09.02.748867 |
| E5-01 | Yang 2022, Cell | 全文 | https://doi.org/10.1016/j.cell.2022.04.015 |
| E5-02 | Simeonov 2021, Cancer Cell | 全文 | https://doi.org/10.1016/j.ccell.2021.05.005 |
| E5-03 | Quinn 2021, Science | 全文 | https://doi.org/10.1126/science.abc1944 |
| E5-04 | Laks 2019, Cell | 全文 | https://doi.org/10.1016/j.cell.2019.10.026 |
| E5-06、E7-10 | Kuipers 2017, Genome Research | 全文 | https://doi.org/10.1101/gr.220707.117 |
| E5-09 | Ben-David 2018, Nature | 全文 | https://doi.org/10.1038/s41586-018-0409-3 |
| E5-10 | Cross 2018, Nature Ecology & Evolution | 全文 | https://doi.org/10.1038/s41559-018-0642-z |
| E5-11 | Househam 2022, Nature | 全文 | https://doi.org/10.1038/s41586-022-05311-x |
| E5-13 | McPherson 2025, Nature | 全文 | https://doi.org/10.1038/s41586-025-09240-3 |
| E6-01 | Keskus 2025, Nat Biotechnol（Severus）— 10.1038/s41587-025-02618-8 | 全文 | https://doi.org/10.1038/s41587-025-02618-8 |
| E6-02、E7-11 | O'Neill 2024, Cell Genomics | 全文 | https://doi.org/10.1016/j.xgen.2024.100674 |
| E6-03 | Espejo Valle-Inclan 2022, Cell Genomics（COLO829）— 10.1016/j.xgen.2022.100139 | 全文 | https://doi.org/10.1016/j.xgen.2022.100139 |
| E6-04 | Kolmogorov 2023, Nat Methods | 全文 | https://doi.org/10.1038/s41592-023-01993-x |
| E6-05 | Fujimoto 2021, Genome Med | 全文 | https://doi.org/10.1186/s13073-021-00883-1 |
| E6-07 | Elrick 2025, Nat Methods（SAVANA）— 10.1038/s41592-025-02708-0 | 全文 | https://doi.org/10.1038/s41592-025-02708-0 |
| E6-08 | Simpson 2024, bioRxiv（smrest）— 10.1101/2024.02.26.582089 | 全文 | https://doi.org/10.1101/2024.02.26.582089 |
| E6-10 | Ho 2025, bioRxiv（LongPhase-S）— 10.1101/2025.11.20.689492 | 全文 | https://doi.org/10.1101/2025.11.20.689492 |
| E6-11 | Ahmad 2025, medRxiv（Wakhan）— 10.64898/2025.12.11.25342098 | 全文 | https://doi.org/10.64898/2025.12.11.25342098 |
| E6-12 | Sohn 2026, Cell | 全文 | https://doi.org/10.1016/j.cell.2026.09.033 |
| E6-13 | Lin 2026, Adv Sci | 全文 | https://doi.org/10.1002/advs.76856 |
| E6-14 | Ijaz 2024, Cell Genomics | 全文 | https://doi.org/10.1016/j.xgen.2023.100484 |
| E6-B01 | Liu 2026, Nat Commun（既有 B01） | 全文 | https://doi.org/10.1038/s41467-026-75172-9 |
| E6-HG008 | McDaniel 2025, Sci Data（HG008）— 10.1038/s41597-025-05438-2 | 全文 | https://doi.org/10.1038/s41597-025-05438-2 |
| E9-01 | Demeulemeester 2022, Nat Genet | 全文 | https://doi.org/10.1038/s41588-021-01005-8 |
| E9-02 | Tarabichi 2021, Nat Methods | 全文 | https://doi.org/10.1038/s41592-020-01013-2 |
| E6-15 | A complete human pancreatic cancer genome, bioRxiv 2026 preprint（HG008）— 10.64898/2026.05.01.722316 | 全文 | https://doi.org/10.64898/2026.05.01.722316 |
| E6-16 | Sakamoto 2026, bioRxiv preprint（PRCGAP）— 10.64898/2026.05.28.728591 | 全文 | https://doi.org/10.64898/2026.05.28.728591 |
| E7-02 | Bielski 2018, Nat Genet | 全文 | https://doi.org/10.1038/s41588-018-0165-1 |
| E7-03 | López 2020, Nat Genet | 全文 | https://doi.org/10.1038/s41588-020-0584-7 |
| E7-04 | Watkins 2020, Nature | 全文 | https://doi.org/10.1038/s41586-020-2698-6 |
| E7-07 | Dewhurst 2014, Cancer Discov | 全文 | https://doi.org/10.1158/2159-8290.CD-13-0285 |
| E7-09 | Baker 2024, Cancer Discov（GRITIC）— 10.1158/2159-8290.CD-23-1249 | 全文 | https://doi.org/10.1158/2159-8290.CD-23-1249 |
| E8-02 | Toguchida 1989, Nature | 摘要 | https://doi.org/10.1038/338156a0 |
| E8-03 | Dryja 1989, Nature | 摘要 | https://doi.org/10.1038/339556a0 |
| E8-04 | Zhu 1989, Nature | 摘要 | https://doi.org/10.1038/340312a0 |
| E8-05 | Schroeder 1987, Am J Hum Genet | 摘要 | PMC1684136 |
| E8-06 | Caron 1993／Cheng 1993, Nat Genet | 摘要 | https://doi.org/10.1038/ng0693-187 |
| E8-07 | Cheng 1993, Nat Genet | 摘要 | https://doi.org/10.1038/ng0693-191 |
| E8-08 | Maxwell 2017, Nat Commun | 全文 | https://doi.org/10.1038/s41467-017-00388-9 |
| E8-09 | Akbari 2023, Cell Genomics | 全文 | https://doi.org/10.1016/j.xgen.2022.100233 |
| E8-10 | Zink 2018, Nat Genet | 摘要 | https://doi.org/10.1038/s41588-018-0232-7 |
| E8-12 | Martin-Trujillo 2017, Nat Commun | 全文 | https://doi.org/10.1038/s41467-017-00639-9 |
| E8-13 | Lundin-Ström 2020, Blood Cancer J | 全文 | https://doi.org/10.1038/s41408-020-0317-2 |
| E8-14 | Paulsson 2003, Blood | 摘要 | https://doi.org/10.1182/blood-2003-05-1444 |
| E8-15 | Stacey 2025, JCI Insight | 全文 | https://doi.org/10.1172/jci.insight.188216 |
| E8-16 | Chase 2015, Leukemia | 全文 | https://doi.org/10.1038/leu.2015.130 |
| E8-17 | Jones 2009, Nat Genet | 全文 | https://doi.org/10.1038/ng.334 |
| E8-G1 | Kong 2012, Nature（germline 對照） | 全文 | https://doi.org/10.1038/nature11396 |
