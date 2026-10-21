# 2026-10-20 痕跡

- 模式：接續游標 2026-10-19T23:59:59
- 掃描區間：2026-10-19T22:59:59 ~ 2026-10-20T23:00:09
- 其中重疊區（已讀過，只供補脈絡）：2026-10-19T22:59:59 ~ 2026-10-19T23:59:59
- ⚠️ 日期標籤 2026-10-20 只是檔名，不等於內容的涵蓋範圍（見上）

## git commits

- 9ce1932 22:00 docs(lab_report): add PCDH entropy checks for 5 cell lines
- 396bd62 22:00 feat(tools): add PCDH methylation barcode entropy scripts
- 74a95ff 21:36 docs(report): add read-feature, simulation and real-data validation slides to 10-21 deck
- fc60d0a 21:36 docs(report): split dated bio-drawing rules into BIO_DRAWING_RULES.md with keyword index
- 7df7942 21:36 docs(research): add B09 PCDH methylation barcode paper (C3b)
- 6e51ec4 21:36 docs(claude): require Traditional Chinese in all replies
- 33ec56f 14:50 docs(data): add SMC-Het dataset inventory to tumor_sample.md
- ad3a634 11:19 chore(daily): backfill 2026-10-19 work log
- 9ac5274 11:19 docs(report): refocus 10-21 deck on validation data availability
- ba51b72 11:19 docs(research): add long-read phasing tree-method search and M08
- 6bc87ca 11:19 docs(research): drop papers without a tree-building step

## commit 改動的檔案

### 9ce1932 docs(lab_report): add PCDH entropy checks for 5 cell lines
```
 .../H1437_t00_n25.call_control.txt                 |    3 +
 .../H1437_t00_n25.pcdh_windows.tsv                 |  258 +++++
 .../H1437_t50_n00.call_control.txt                 |    3 +
 .../H1437_t50_n00.pcdh_windows.tsv                 |  967 ++++++++++++++++
 lab_report/2026-10-20_h1437_pcdh_entropy/README.md |  113 ++
 .../5khz_HCC1395.call_control.txt                  |    3 +
 .../5khz_HCC1395.m.pcdh_windows.tsv                | 1005 ++++++++++++++++
 .../5khz_HCC1395.mh.pcdh_windows.tsv               | 1191 +++++++++++++++++++
 .../5khz_HCC1395BL.call_control.txt                |    3 +
 .../5khz_HCC1395BL.m.pcdh_windows.tsv              |  608 ++++++++++
 .../5khz_HCC1395BL.mh.pcdh_windows.tsv             |  571 ++++++++++
 .../HCC1395_t00_n25.pcdh_windows.tsv               |  240 ++++
 .../HCC1395_t50_n00.pcdh_windows.tsv               | 1198 ++++++++++++++++++++
 .../2026-10-20_hcc1395_pcdh_entropy/README.md      |  171 +++
 .../H2009_t00_n25.call_control.txt                 |    3 +
 .../H2009_t00_n25.pcdh_windows.tsv                 |  196 ++++
 .../H2009_t50_n00.call_control.txt                 |    3 +
 .../H2009_t50_n00.pcdh_windows.tsv                 | 1168 +++++++++++++++++++
 .../HCC1937_t00_n25.call_control.txt               |    3 +
 .../HCC1937_t00_n25.pcdh_windows.tsv               |  202 ++++
 .../HCC1937_t50_n00.call_control.txt               |    3 +
 .../HCC1937_t50_n00.pcdh_windows.tsv               | 1170 +++++++++++++++++++
 .../HCC1954_t00_n25.call_control.txt               |    3 +
 .../HCC1954_t00_n25.pcdh_windows.tsv               |  197 ++++
 .../HCC1954_t50_n00.call_control.txt               |    3 +
 .../HCC1954_t50_n00.pcdh_windows.tsv               | 1107 ++++++++++++++++++
 lab_report/2026-10-20_pcdh_entropy_panel/README.md |  111 ++
 .../panel_summary.tsv                              |    6 +
 28 files changed, 10509 insertions(+)
```
### 396bd62 feat(tools): add PCDH methylation barcode entropy scripts
```
 tools/meth_call_control.py    | 28 ++++++++++++++
 tools/pcdh_entropy.py         | 89 +++++++++++++++++++++++++++++++++++++++++++
 tools/pcdh_entropy_summary.py | 52 +++++++++++++++++++++++++
 3 files changed, 169 insertions(+)
```
### 74a95ff docs(report): add read-feature, simulation and real-data validation slides to 10-21 deck
```
 report/2026_10_21_slides/BRIEF.md                  |  87 ++++++++++++-
 report/2026_10_21_slides/OUTLINE_real_data.md      |  42 ++++++
 report/2026_10_21_slides/project/deck.json         |  33 +++--
 report/2026_10_21_slides/project/slides/cover.html |  72 ++++++++++-
 .../2026_10_21_slides/project/slides/s1-count.html |  82 ++++--------
 .../project/slides/s1-feat-lung.html               |  91 +++++++++++++
 .../project/slides/s1-feat-methyl.html             |  78 +++++++++++
 .../project/slides/s1-feat-pair.html               |  43 ++++++
 .../project/slides/s1-features.html                | 132 +++++++++++++++++--
 .../project/slides/s1-read-features.html           | 107 +++++++++++++++
 .../project/slides/s2-longread.html                |   5 +-
 .../project/slides/s2-real-ref.html                | 122 +++++++++++++++++
 .../project/slides/s2-sc-trees.html                |   4 +-
 .../project/slides/s2-sim-check.html               |  71 ++++++++++
 .../project/slides/s2-sim-plan.html                |  92 +++++++++++++
 .../2026_10_21_slides/project/slides/summary.html  |  14 +-
 .../removed_slides/s2-real-consistency.html        | 144 +++++++++++++++++++++
 17 files changed, 1115 insertions(+), 104 deletions(-)
```
### fc60d0a docs(report): split dated bio-drawing rules into BIO_DRAWING_RULES.md with keyword index
```
 report/BIO_DRAWING_RULES.md | 42 ++++++++++++++++++++++++++++
 report/report_rule.md       | 67 ++++++++++++++++++++++++++++++++++++---------
 2 files changed, 96 insertions(+), 13 deletions(-)
```
### 7df7942 docs(research): add B09 PCDH methylation barcode paper (C3b)
```
 research/PAPER_CATEGORIES.md                       |   21 +-
 research/paper_categories.tsv                      |    1 +
 .../c3b_methylation_barcode_tree_sc_truth/B09      |    1 +
 research/tumor_phylogeny_2026/catalog.json         |    9 +
 .../longread_tree_search_2026-10-19/README.md      |    4 +-
 research/tumor_phylogeny_2026/manifest.json        |   30 +-
 research/tumor_phylogeny_2026/manifest.tsv         |    2 +
 .../B09_pcdh_methylation_barcode_2026/README.md    |  190 ++
 .../B09_pcdh_methylation_barcode_2026/paper.txt    |  154 ++
 .../B09_pcdh_methylation_barcode_2026/paper.xml    |   57 +
 .../supplement.txt                                 | 1930 ++++++++++++++++++++
 11 files changed, 2386 insertions(+), 13 deletions(-)
```
### 6e51ec4 docs(claude): require Traditional Chinese in all replies
```
 CLAUDE.md | 1 +
 1 file changed, 1 insertion(+)
```
### 33ec56f docs(data): add SMC-Het dataset inventory to tumor_sample.md
```
 tumor_sample.md | 77 +++++++++++++++++++++++++++++++++++++++++++++++++++++++--
 1 file changed, 75 insertions(+), 2 deletions(-)
```
### ad3a634 chore(daily): backfill 2026-10-19 work log
```
 .worklog_scan/2026-10-19/candidates.json          |   39 +-
 .worklog_scan/2026-10-19/layered.json             |  178 +-
 .worklog_scan/2026-10-19/session-manifest.json    |   80 +-
 .worklog_scan/2026-10-19/signals.md               |  210 +-
 .worklog_scan/2026-10-19/traces.md                |  817 +-
 .worklog_scan/2026-10-19/transcript.txt           | 9507 ++++++++++++++++++++-
 .worklog_scan/2026-10-19/transcript_user_only.txt |  939 ++
 daily/.data/2026-10-19.json                       |  414 +-
 daily/.data/_cursor.json                          |    4 +-
 daily/2026-10-19.html                             |   57 +-
 daily/README.md                                   |    2 +-
 daily/index.html                                  |    2 +-
 12 files changed, 12050 insertions(+), 199 deletions(-)
```
### 9ac5274 docs(report): refocus 10-21 deck on validation data availability
```
 report/2026_10_21_slides/BRIEF.md                  | 173 +++++++++++++--------
 report/2026_10_21_slides/OUTLINE_v3.2.md           |   2 +-
 report/2026_10_21_slides/OUTLINE_v5.1.md           | 126 +++++++++++++++
 report/2026_10_21_slides/OUTLINE_v5.2.md           | 152 ++++++++++++++++++
 report/2026_10_21_slides/OUTLINE_v5.3.md           | 158 +++++++++++++++++++
 report/2026_10_21_slides/OUTLINE_v5.md             |  93 +++++++++++
 report/2026_10_21_slides/REVIEW_v5.md              |  52 +++++++
 report/2026_10_21_slides/VISUALS.md                |   4 +-
 .../old_27p_slides/s1-benchmark-scan.html          |   3 +-
 .../old_27p_slides/s1-categories.html              |  12 +-
 .../old_27p_slides/s3-papers-io.html               |   4 +-
 .../old_27p_slides/s4-novelty.html                 |  18 +--
 report/2026_10_21_slides/old_v4_slides/BRIEF_v4.md | 127 +++++++++++++++
 report/2026_10_21_slides/old_v4_slides/agenda.html |  41 +++++
 report/2026_10_21_slides/old_v4_slides/cover.html  |  11 ++
 report/2026_10_21_slides/old_v4_slides/deck.json   |   1 +
 .../old_v4_slides/live_backup/project/deck.json    |  67 ++++++++
 .../live_backup/project/slides/agenda.html         |  41 +++++
 .../live_backup/project/slides/cover.html          |  11 ++
 .../live_backup/project/slides/s1-hcc1395.html     | 135 ++++++++++++++++
 .../live_backup/project/slides/s2-pitfalls.html    | 111 +++++++++++++
 .../live_backup/project/slides/s3-gap.html         | 116 ++++++++++++++
 .../live_backup}/project/slides/s4-hp.html         |   0
 .../live_backup}/project/slides/s4-pair.html       |   0
 .../live_backup}/project/slides/s5-validate.html   |   0
 .../live_backup/project/slides/summary.html        |  47 ++++++
 .../slides => old_v4_slides}/s1-hcc1395.html       |   0
 .../slides => old_v4_slides}/s2-phyclone-io.html   |   0
 .../slides => old_v4_slides}/s2-pitfalls.html      |   0
 .../{project/slides => old_v4_slides}/s3-gap.html  |   0
 report/2026_10_21_slides/old_v4_slides/s4-hp.html  | 110 +++++++++++++
 .../2026_10_21_slides/old_v4_slides/s4-pair.html   |  40 +++++
 .../old_v4_slides/s5-validate.html                 |  80 ++++++++++
 .../2026_10_21_slides/old_v4_slides/summary.html   |  47 ++++++
 report/2026_10_21_slides/project/deck.json         |  56 ++++++-
 .../2026_10_21_slides/project/slides/agenda.html   |  47 +++---
 report/2026_10_21_slides/project/slides/cover.html |  13 +-
 .../2026_10_21_slides/project/slides/s1-count.html | 118 ++++++++++++++
 .../project/slides/s1-features.html                |  12 ++
 .../2026_10_21_slides/project/slides/s1-terms.html |  58 +++++++
 .../project/slides/s2-longread.html                |  17 ++
 .../project/slides/s2-sc-trees.html                |  75 +++++++++
 .../project/slides/s2-sim-layers.html              | 128 +++++++++++++++
 .../project/slides/s2-smchet.html                  | 121 ++++++++++++++
 .../2026_10_21_slides/project/slides/summary.html  |  87 ++++++-----
 report/2026_10_21_slides/sources/s5908_text.md     |  13 +-
 report/VISUAL_SPEC.md                              |  49 +++++-
 report/report_rule.md                              |  19 ++-
 48 files changed, 2413 insertions(+), 182 deletions(-)
```
### ba51b72 docs(research): add long-read phasing tree-method search and M08
```
 research/PAPER_CATEGORIES.md                       |  14 +-
 research/paper_categories.tsv                      |   1 +
 .../c1_read_cooccurrence_short/M08                 |   1 +
 .../longread_tree_search_2026-10-19/README.md      |  88 ++++++++
 .../raw/search_A_cooccurrence.md                   | 123 +++++++++++
 .../raw/search_B_haplotype_cn.md                   | 132 ++++++++++++
 .../raw/search_C_singlecell_methyl_sv.md           | 129 ++++++++++++
 .../raw/search_D_repos_preprints.md                | 112 ++++++++++
 .../tumor_phylogeny_2026/methods_survey/README.md  |   6 +-
 .../papers/M08_bitphylogeny_2015/README.md         | 169 +++++++++++++++
 .../papers/M08_bitphylogeny_2015/paper.txt         | 228 +++++++++++++++++++++
 .../papers/M08_bitphylogeny_2015/paper.xml         |  25 +++
 12 files changed, 1020 insertions(+), 8 deletions(-)
```
### 6bc87ca docs(research): drop papers without a tree-building step
```
 research/CONTEXT.md                                |   12 +-
 research/PAPER_CATEGORIES.md                       |   26 +-
 research/SYNTHESIS_phyclone_longphase.md           |   26 +-
 research/TERMINOLOGY.md                            |   21 +-
 research/paper_categories.tsv                      |    6 +-
 .../c1_read_cooccurrence_short/B02                 |    1 -
 .../C2_long_read_feature/c2_local_order/M03        |    1 -
 .../C2_long_read_feature/c2_molecular_history/B08  |    1 -
 .../C2_long_read_feature/c2_sample_tree_sv/B06     |    1 -
 research/terminology/corpus.tsv                    |    7 -
 research/terminology/evidence.tsv                  |  239 --
 research/terminology/terms.tsv                     |  218 +-
 research/tumor_phylogeny_2026/B_SUMMARY.md         |   18 +-
 research/tumor_phylogeny_2026/CODE_AVAILABILITY.md |    3 -
 .../tumor_phylogeny_2026/INTERSECTION_SUMMARY.md   |   10 +-
 research/tumor_phylogeny_2026/README.md            |   15 +-
 research/tumor_phylogeny_2026/REPO_IMPROVEMENTS.md |    6 +-
 research/tumor_phylogeny_2026/SEARCH_LOG.md        |   11 +-
 research/tumor_phylogeny_2026/catalog.json         |   28 -
 research/tumor_phylogeny_2026/manifest.json        |   52 +-
 research/tumor_phylogeny_2026/manifest.tsv         |    4 -
 .../tumor_phylogeny_2026/methods_survey/README.md  |   26 +-
 .../papers/M03_donmez_aacr2026/README.md           |  147 -
 .../papers/M03_donmez_aacr2026/abstract.txt        |   14 -
 .../workers/W4_read_phasing_longread.md            |   30 +-
 .../workers/W7_proceedings_2025_2026.md            |   15 +-
 .../workers/W8_benchmark_update_2026-10-18.md      |    1 -
 .../papers/B02_myeloma_linkedread_2021/README.md   |   76 -
 .../papers/B02_myeloma_linkedread_2021/paper.txt   | 1312 ---------
 .../PDF_PROVENANCE.md                              |   28 -
 .../B06_hcc_multisite_longread_2025/README.md      |   84 -
 .../oa_metadata.json                               |    1 -
 .../B06_hcc_multisite_longread_2025/paper.txt      |  865 ------
 .../B06_hcc_multisite_longread_2025/supplement.txt |  328 ---
 .../papers/B07_numbat_2022/README.md               |    2 -
 .../papers/B08_hpv_integration_2023/README.md      |   66 -
 .../papers/B08_hpv_integration_2023/paper.txt      | 2859 --------------------
 37 files changed, 201 insertions(+), 6359 deletions(-)
```

## 未提交的變動

```
 M CLAUDE.md
 M tools/pcdh_entropy.py
?? .worklog_scan/2026-10-20/
?? lab_report/2026-10-20_h1437_pcdh_hp_entropy/
?? tools/pcdh_haplotag.sh
?? tools/pcdh_hp_compare.py
```

## 當天新增或修改的檔案（排除 .git / 掃描暫存 / 大型二進位）

```
CLAUDE.md
daily/2026-10-19.html
daily/.data/2026-10-19.json
daily/.data/_cursor.json
daily/.data/_private/2026-10-19.evidence.json
daily/index.html
daily/README.md
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t00_n25.call_control.txt
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t50_n00.call_control.txt
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_entropy/README.md
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_normal_full.byhp.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_normal_full.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_pcdh_phased.vcf.gz
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_t00_n25.byhp.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_t50_n00.byhp.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_tumor_full.byhp.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_tumor_full.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_hp_entropy/hp_compare.txt
lab_report/2026-10-20_h1437_pcdh_hp_entropy/README.md
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.call_control.txt
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.mh.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.m.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.call_control.txt
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.mh.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.m.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/HCC1395_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/HCC1395_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t00_n25.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t50_n00.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t00_n25.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t50_n00.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t00_n25.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t50_n00.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/panel_summary.tsv
lab_report/2026-10-20_pcdh_entropy_panel/README.md
report/2026_10_21_slides/BRIEF.md
report/2026_10_21_slides/OUTLINE_real_data.md
report/2026_10_21_slides/project/deck.json
report/2026_10_21_slides/project/slides/agenda.html
report/2026_10_21_slides/project/slides/cover.html
report/2026_10_21_slides/project/slides/s1-count.html
report/2026_10_21_slides/project/slides/s1-feat-lung.html
report/2026_10_21_slides/project/slides/s1-feat-methyl.html
report/2026_10_21_slides/project/slides/s1-feat-pair.html
report/2026_10_21_slides/project/slides/s1-features.html
report/2026_10_21_slides/project/slides/s1-read-features.html
report/2026_10_21_slides/project/slides/s1-terms.html
report/2026_10_21_slides/project/slides/s2-longread.html
report/2026_10_21_slides/project/slides/s2-real-ref.html
report/2026_10_21_slides/project/slides/s2-sc-trees.html
report/2026_10_21_slides/project/slides/s2-sim-check.html
report/2026_10_21_slides/project/slides/s2-sim-plan.html
report/2026_10_21_slides/project/slides/summary.html
report/2026_10_21_slides/removed_slides/s2-real-consistency.html
report/BIO_DRAWING_RULES.md
report/report_rule.md
research/hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md
research/PAPER_CATEGORIES.md
research/paper_categories.tsv
research/phyclone_research/notes/zh-TW/00_SOURCE_MAP.md
research/tumor_phylogeny_2026/catalog.json
research/tumor_phylogeny_2026/longread_tree_search_2026-10-19/README.md
research/tumor_phylogeny_2026/manifest.json
research/tumor_phylogeny_2026/manifest.tsv
research/tumor_phylogeny_2026/methods_survey/papers/M01_phyclone_2025/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M02_treeclone_2019/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M04_pharming_2026/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M05_tusv_ext_2022/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M06_phylex_2023/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M08_bitphylogeny_2015/README.md
research/tumor_phylogeny_2026/methods_survey/README.md
research/tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md
research/tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md
research/tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md
research/tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md
research/tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md
research/tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md
research/tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md
research/tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/README.md
research/tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md
research/tumor_phylogeny_2026/papers/B07_numbat_2022/README.md
research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/paper.pdf
research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/paper.txt
research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/paper.xml
research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/README.md
research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/supplement.pdf
research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/supplement.txt
research/tumor_phylogeny_2026/references/R01_mcpherson_hgsoc_2016/README.md
tools/meth_call_control.py
tools/pcdh_entropy.py
```

## commit 動過的檔案（git 記錄，不受 mtime 覆蓋）

```
CLAUDE.md
daily/2026-10-19.html
daily/.data/2026-10-19.json
daily/.data/_cursor.json
daily/index.html
daily/README.md
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t00_n25.call_control.txt
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t50_n00.call_control.txt
lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_h1437_pcdh_entropy/README.md
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.call_control.txt
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.mh.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.m.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.call_control.txt
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.mh.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.m.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/HCC1395_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/HCC1395_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_hcc1395_pcdh_entropy/README.md
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t00_n25.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t50_n00.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/H2009_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t00_n25.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t50_n00.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1937_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t00_n25.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t00_n25.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t50_n00.call_control.txt
lab_report/2026-10-20_pcdh_entropy_panel/HCC1954_t50_n00.pcdh_windows.tsv
lab_report/2026-10-20_pcdh_entropy_panel/panel_summary.tsv
lab_report/2026-10-20_pcdh_entropy_panel/README.md
report/2026_10_21_slides/BRIEF.md
report/2026_10_21_slides/old_27p_slides/s1-benchmark-scan.html
report/2026_10_21_slides/old_27p_slides/s1-categories.html
report/2026_10_21_slides/old_27p_slides/s3-papers-io.html
report/2026_10_21_slides/old_27p_slides/s4-novelty.html
report/2026_10_21_slides/old_v4_slides/agenda.html
report/2026_10_21_slides/old_v4_slides/BRIEF_v4.md
report/2026_10_21_slides/old_v4_slides/cover.html
report/2026_10_21_slides/old_v4_slides/deck.json
report/2026_10_21_slides/old_v4_slides/live_backup/project/deck.json
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/agenda.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/cover.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/s1-hcc1395.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/s2-pitfalls.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/s3-gap.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/s4-hp.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/s4-pair.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/s5-validate.html
report/2026_10_21_slides/old_v4_slides/live_backup/project/slides/summary.html
report/2026_10_21_slides/old_v4_slides/s1-hcc1395.html
report/2026_10_21_slides/old_v4_slides/s2-phyclone-io.html
report/2026_10_21_slides/old_v4_slides/s2-pitfalls.html
report/2026_10_21_slides/old_v4_slides/s3-gap.html
report/2026_10_21_slides/old_v4_slides/s4-hp.html
report/2026_10_21_slides/old_v4_slides/s4-pair.html
report/2026_10_21_slides/old_v4_slides/s5-validate.html
report/2026_10_21_slides/old_v4_slides/summary.html
report/2026_10_21_slides/OUTLINE_real_data.md
report/2026_10_21_slides/OUTLINE_v3.2.md
report/2026_10_21_slides/OUTLINE_v5.1.md
report/2026_10_21_slides/OUTLINE_v5.2.md
report/2026_10_21_slides/OUTLINE_v5.3.md
report/2026_10_21_slides/OUTLINE_v5.md
report/2026_10_21_slides/project/deck.json
report/2026_10_21_slides/project/slides/agenda.html
report/2026_10_21_slides/project/slides/cover.html
report/2026_10_21_slides/project/slides/s1-count.html
report/2026_10_21_slides/project/slides/s1-feat-lung.html
report/2026_10_21_slides/project/slides/s1-feat-methyl.html
report/2026_10_21_slides/project/slides/s1-feat-pair.html
report/2026_10_21_slides/project/slides/s1-features.html
report/2026_10_21_slides/project/slides/s1-read-features.html
report/2026_10_21_slides/project/slides/s1-terms.html
report/2026_10_21_slides/project/slides/s2-longread.html
report/2026_10_21_slides/project/slides/s2-real-ref.html
report/2026_10_21_slides/project/slides/s2-sc-trees.html
report/2026_10_21_slides/project/slides/s2-sim-check.html
report/2026_10_21_slides/project/slides/s2-sim-layers.html
report/2026_10_21_slides/project/slides/s2-sim-plan.html
report/2026_10_21_slides/project/slides/s2-smchet.html
report/2026_10_21_slides/project/slides/summary.html
report/2026_10_21_slides/removed_slides/s2-real-consistency.html
report/2026_10_21_slides/REVIEW_v5.md
report/2026_10_21_slides/sources/s5908_text.md
report/2026_10_21_slides/VISUALS.md
report/BIO_DRAWING_RULES.md
report/report_rule.md
report/VISUAL_SPEC.md
research/CONTEXT.md
research/PAPER_CATEGORIES.md
research/paper_categories.tsv
research/papers_by_category/C1_short_read_or_unspecified/c1_read_cooccurrence_short/B02
research/papers_by_category/C1_short_read_or_unspecified/c1_read_cooccurrence_short/M08
research/papers_by_category/C2_long_read_feature/c2_local_order/M03
research/papers_by_category/C2_long_read_feature/c2_molecular_history/B08
research/papers_by_category/C2_long_read_feature/c2_sample_tree_sv/B06
```

## 當天新增的圖

- research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/paper.pdf
- research/tumor_phylogeny_2026/papers/B09_pcdh_methylation_barcode_2026/supplement.pdf

## 當天的 .meta.json（含指令列、seed、參數）


## 當天新增或改動的結果表（前 15 行）

### lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t00_n25.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_t00_n25	140786982	140787275	21	0.695	3.051	10.00	0.286
H1437_t00_n25	140787341	140787522	23	0.630	4.037	17.15	0.087
H1437_t00_n25	140787695	140787750	24	0.996	0.243	1.85	0.958
H1437_t00_n25	140788158	140788251	22	0.932	1.934	5.75	0.545
H1437_t00_n25	140789223	140789513	23	0.243	3.230	11.80	0.261
H1437_t00_n25	140792650	140794284	20	0.160	2.639	8.00	0.350
H1437_t00_n25	140796441	140796489	22	0.968	1.413	5.55	0.727
H1437_t00_n25	140796582	140796648	24	0.892	2.507	7.50	0.333
H1437_t00_n25	140796948	140797023	20	0.800	2.346	8.00	0.400
H1437_t00_n25	140797038	140797147	24	0.667	2.765	8.30	0.250
H1437_t00_n25	140797155	140797263	20	0.530	2.628	8.00	0.300
H1437_t00_n25	140797309	140798008	20	0.675	3.646	14.00	0.150
H1437_t00_n25	140800636	140801060	21	0.467	3.526	13.60	0.238
H1437_t00_n25	140801105	140801340	22	0.477	3.223	12.20	0.318
```
### lab_report/2026-10-20_h1437_pcdh_entropy/H1437_t50_n00.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_t50_n00	140783399	140785368	22	0.132	1.851	5.00	0.500
H1437_t50_n00	140786373	140786482	29	0.500	3.597	13.70	0.138
H1437_t50_n00	140786489	140786627	27	0.770	2.989	9.90	0.222
H1437_t50_n00	140786670	140786948	37	0.422	2.869	9.55	0.243
H1437_t50_n00	140786982	140787275	37	0.359	3.650	14.05	0.135
H1437_t50_n00	140787341	140787522	41	0.580	4.037	17.25	0.073
H1437_t50_n00	140787532	140787602	30	0.830	1.961	5.20	0.367
H1437_t50_n00	140787615	140787678	35	0.794	3.650	14.40	0.200
H1437_t50_n00	140787695	140787750	45	0.978	0.100	1.35	0.978
H1437_t50_n00	140787752	140787810	33	0.739	3.762	15.00	0.121
H1437_t50_n00	140787822	140787912	42	0.724	3.136	10.90	0.214
H1437_t50_n00	140787917	140787980	28	0.825	2.908	10.35	0.357
H1437_t50_n00	140787989	140788086	35	0.831	1.949	5.95	0.543
H1437_t50_n00	140788091	140788156	42	0.924	1.877	5.25	0.476
```
### lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_normal_full.byhp.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_normal_full_HP1	140786982	140787275	20	0.785	2.741	8.00	0.250
H1437_normal_full_HP1	140787341	140787522	24	0.658	3.704	14.35	0.167
H1437_normal_full_HP1	140787615	140787678	22	0.891	2.634	8.60	0.318
H1437_normal_full_HP1	140787695	140787750	24	1.000	0.000	1.00	1.000
H1437_normal_full_HP1	140787752	140787810	27	0.915	1.769	4.70	0.519
H1437_normal_full_HP1	140787822	140787912	21	0.824	2.277	6.75	0.381
H1437_normal_full_HP1	140787989	140788086	20	0.940	1.839	6.00	0.550
H1437_normal_full_HP1	140788091	140788156	22	0.995	0.258	1.90	0.955
H1437_normal_full_HP1	140788158	140788251	24	0.946	1.459	4.35	0.583
H1437_normal_full_HP1	140788259	140788337	21	0.867	2.618	7.95	0.286
H1437_normal_full_HP1	140789223	140789513	25	0.152	2.234	7.10	0.480
H1437_normal_full_HP1	140792650	140794284	24	0.129	1.822	5.70	0.583
H1437_normal_full_HP1	140794404	140795003	24	0.312	2.780	9.30	0.333
H1437_normal_full_HP1	140795013	140795107	21	0.300	3.464	13.30	0.190
```
### lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_normal_full.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_normal_full	140783399	140785368	24	0.179	2.914	8.50	0.208
H1437_normal_full	140786373	140786482	23	0.670	3.872	15.50	0.087
H1437_normal_full	140786489	140786627	27	0.904	2.028	4.75	0.333
H1437_normal_full	140786670	140786948	28	0.796	3.100	10.80	0.250
H1437_normal_full	140786982	140787275	39	0.703	2.960	9.55	0.282
H1437_normal_full	140787341	140787522	41	0.651	3.900	15.95	0.098
H1437_normal_full	140787532	140787602	31	0.865	2.061	4.60	0.323
H1437_normal_full	140787615	140787678	35	0.886	2.871	9.20	0.257
H1437_normal_full	140787695	140787750	46	0.993	0.257	1.90	0.957
H1437_normal_full	140787752	140787810	37	0.908	1.986	6.00	0.486
H1437_normal_full	140787822	140787912	38	0.858	1.500	4.95	0.658
H1437_normal_full	140787917	140787980	33	0.912	2.392	8.80	0.515
H1437_normal_full	140787989	140788086	34	0.894	2.514	8.05	0.382
H1437_normal_full	140788091	140788156	39	0.990	0.384	2.35	0.923
```
### lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_t00_n25.byhp.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_t00_n25_HP2	140862745	140862829	20	0.935	1.188	3.00	0.600
```
### lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_t50_n00.byhp.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_t50_n00_HP1	140786373	140786482	21	0.462	3.072	9.90	0.190
H1437_t50_n00_HP1	140786670	140786948	25	0.440	2.535	8.60	0.360
H1437_t50_n00_HP1	140786982	140787275	27	0.348	3.882	15.85	0.148
H1437_t50_n00_HP1	140787341	140787522	25	0.540	3.996	16.95	0.120
H1437_t50_n00_HP1	140787532	140787602	22	0.841	1.617	3.95	0.500
H1437_t50_n00_HP1	140787615	140787678	27	0.848	3.268	12.05	0.259
H1437_t50_n00_HP1	140787695	140787750	31	0.968	0.186	1.65	0.968
H1437_t50_n00_HP1	140787752	140787810	22	0.682	3.754	14.85	0.136
H1437_t50_n00_HP1	140787822	140787912	26	0.665	3.294	11.45	0.192
H1437_t50_n00_HP1	140787917	140787980	22	0.868	2.665	8.45	0.364
H1437_t50_n00_HP1	140787989	140788086	24	0.821	2.160	6.70	0.500
H1437_t50_n00_HP1	140788091	140788156	26	0.896	2.032	5.45	0.423
H1437_t50_n00_HP1	140788158	140788251	22	0.555	3.479	13.10	0.182
H1437_t50_n00_HP1	140788259	140788337	20	0.515	2.695	10.00	0.450
```
### lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_tumor_full.byhp.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_tumor_full_HP1	140783399	140785368	24	0.096	1.671	3.85	0.417
H1437_tumor_full_HP1	140786373	140786482	33	0.442	3.287	11.45	0.182
H1437_tumor_full_HP1	140786489	140786627	26	0.731	3.305	11.35	0.154
H1437_tumor_full_HP1	140786670	140786948	35	0.434	2.297	7.75	0.343
H1437_tumor_full_HP1	140786982	140787275	41	0.329	3.454	12.60	0.146
H1437_tumor_full_HP1	140787341	140787522	38	0.545	4.041	17.45	0.105
H1437_tumor_full_HP1	140787532	140787602	35	0.851	1.732	4.35	0.457
H1437_tumor_full_HP1	140787615	140787678	37	0.854	3.206	11.60	0.270
H1437_tumor_full_HP1	140787695	140787750	45	0.978	0.129	1.45	0.978
H1437_tumor_full_HP1	140787752	140787810	31	0.694	3.775	14.90	0.129
H1437_tumor_full_HP1	140787822	140787912	38	0.666	2.928	9.50	0.263
H1437_tumor_full_HP1	140787917	140787980	35	0.883	2.569	9.25	0.457
H1437_tumor_full_HP1	140787989	140788086	32	0.806	2.310	7.45	0.469
H1437_tumor_full_HP1	140788091	140788156	40	0.890	2.161	6.20	0.400
```
### lab_report/2026-10-20_h1437_pcdh_hp_entropy/H1437_tumor_full.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
H1437_tumor_full	140783399	140785368	35	0.120	1.729	4.20	0.457
H1437_tumor_full	140786373	140786482	44	0.484	3.644	13.95	0.136
H1437_tumor_full	140786489	140786627	40	0.755	2.906	9.45	0.250
H1437_tumor_full	140786670	140786948	51	0.427	2.834	9.45	0.235
H1437_tumor_full	140786982	140787275	55	0.345	3.487	12.80	0.127
H1437_tumor_full	140787341	140787522	60	0.585	4.061	17.50	0.100
H1437_tumor_full	140787532	140787602	48	0.833	1.949	4.80	0.333
H1437_tumor_full	140787615	140787678	47	0.811	3.384	12.85	0.234
H1437_tumor_full	140787695	140787750	67	0.985	0.100	1.35	0.985
H1437_tumor_full	140787752	140787810	46	0.739	3.788	15.10	0.130
H1437_tumor_full	140787822	140787912	59	0.719	2.861	9.25	0.203
H1437_tumor_full	140787917	140787980	47	0.830	3.021	11.50	0.383
H1437_tumor_full	140787989	140788086	45	0.820	2.103	6.85	0.511
H1437_tumor_full	140788091	140788156	62	0.919	1.958	5.85	0.452
```
### lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.mh.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
5khz_N_mh	140787752	140787810	24	0.942	1.874	4.95	0.500
5khz_N_mh	140788347	140788448	20	0.610	2.846	8.00	0.300
5khz_N_mh	140792650	140794284	20	0.140	2.171	5.00	0.300
5khz_N_mh	140795414	140795788	22	0.573	3.412	10.90	0.091
5khz_N_mh	140796352	140796426	36	0.894	1.802	5.30	0.500
5khz_N_mh	140796441	140796489	34	0.882	2.776	8.20	0.294
5khz_N_mh	140796496	140796575	34	0.953	1.466	3.75	0.588
5khz_N_mh	140796582	140796648	24	0.725	2.436	6.80	0.333
5khz_N_mh	140796651	140796748	38	0.900	2.180	5.85	0.368
5khz_N_mh	140796757	140796832	26	0.954	1.579	3.85	0.538
5khz_N_mh	140797038	140797147	32	0.719	2.230	5.80	0.375
5khz_N_mh	140797309	140798008	20	0.500	2.646	7.00	0.300
5khz_N_mh	140798012	140800618	24	0.275	2.197	5.95	0.417
5khz_N_mh	140800636	140801060	22	0.327	3.048	8.90	0.182
```
### lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395BL.m.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
5khz_N_m	140782524	140783383	20	0.240	2.922	8.00	0.200
5khz_N_m	140787341	140787522	20	0.890	2.322	6.00	0.400
5khz_N_m	140788347	140788448	22	0.564	2.693	7.95	0.364
5khz_N_m	140788634	140789214	20	0.360	2.922	8.00	0.200
5khz_N_m	140789223	140789513	24	0.217	2.459	6.85	0.333
5khz_N_m	140794404	140795003	26	0.269	2.549	6.95	0.308
5khz_N_m	140796441	140796489	24	0.867	2.947	8.75	0.250
5khz_N_m	140796496	140796575	26	0.946	1.679	4.00	0.538
5khz_N_m	140796582	140796648	22	0.718	2.731	8.00	0.364
5khz_N_m	140796651	140796748	20	0.830	2.646	7.00	0.300
5khz_N_m	140796846	140796936	20	0.670	3.122	9.00	0.200
5khz_N_m	140798012	140800618	28	0.229	2.409	6.70	0.357
5khz_N_m	140800636	140801060	22	0.327	3.231	9.95	0.182
5khz_N_m	140801484	140801632	22	0.527	2.532	6.90	0.364
```
### lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.mh.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
5khz_T_mh	140783399	140785368	40	0.588	3.149	10.60	0.225
5khz_T_mh	140786489	140786627	46	0.813	1.692	4.50	0.543
5khz_T_mh	140786670	140786948	67	0.924	1.246	3.15	0.582
5khz_T_mh	140786982	140787275	79	0.967	0.971	4.15	0.797
5khz_T_mh	140787341	140787522	94	0.995	0.190	1.60	0.947
5khz_T_mh	140787532	140787602	67	0.997	0.228	1.70	0.970
5khz_T_mh	140787615	140787678	94	0.994	0.383	2.25	0.936
5khz_T_mh	140787695	140787750	85	1.000	0.000	1.00	1.000
5khz_T_mh	140787752	140787810	83	0.995	0.291	1.90	0.952
5khz_T_mh	140787822	140787912	73	0.992	0.306	1.90	0.918
5khz_T_mh	140787917	140787980	81	0.972	1.215	3.50	0.716
5khz_T_mh	140787989	140788086	65	0.988	0.484	1.90	0.877
5khz_T_mh	140788091	140788156	84	0.998	0.138	1.45	0.976
5khz_T_mh	140788158	140788251	89	0.983	0.394	2.20	0.933
```
### lab_report/2026-10-20_hcc1395_pcdh_entropy/5khz_HCC1395.m.pcdh_windows.tsv
```
label	win_start	win_end	n_reads	mean_meth	entropy_sub20	n_distinct_sub20	top_barcode_frac
5khz_T_m	140783399	140785368	41	0.568	3.118	10.60	0.220
5khz_T_m	140786373	140786482	50	0.196	2.754	9.05	0.300
5khz_T_m	140786489	140786627	46	0.524	2.132	5.85	0.326
5khz_T_m	140786670	140786948	45	0.927	1.605	4.55	0.578
5khz_T_m	140786982	140787275	43	0.947	1.696	5.90	0.674
5khz_T_m	140787341	140787522	56	0.979	0.632	3.20	0.857
5khz_T_m	140787532	140787602	30	0.973	1.235	4.35	0.767
5khz_T_m	140787695	140787750	26	0.977	0.837	3.55	0.846
5khz_T_m	140787752	140787810	38	0.995	0.255	1.70	0.947
5khz_T_m	140787822	140787912	27	0.952	1.777	6.10	0.630
5khz_T_m	140787917	140787980	33	0.945	1.801	4.80	0.515
5khz_T_m	140787989	140788086	25	0.916	1.852	4.70	0.440
5khz_T_m	140788091	140788156	37	0.978	0.608	2.95	0.892
5khz_T_m	140788158	140788251	40	0.943	1.085	4.50	0.800
```

## 追蹤清單當天的改動（CLAUDE.md evaluation_v1.md research/INDEX.md research/CONTEXT.md research/phyclone_research/RESEARCH_PLAN.md research/phyclone_research/notes/ report/report_rule.md）

```diff
commit fc60d0ab98817ad6c1fe48d23b94c170bbc92250
Author: paulboul1013 <paulboul1013@gmail.com>
Date:   Tue Oct 20 21:36:25 2026 +0800

    docs(report): split dated bio-drawing rules into BIO_DRAWING_RULES.md with keyword index
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/report/report_rule.md b/report/report_rule.md
index baa4e46..f8a29e5 100644
--- a/report/report_rule.md
+++ b/report/report_rule.md
@@ -37,5 +37,6 @@
    - 假想的例子與數值沒有被讀成實測。
    依檢查結果修改後，才算完成。
-7. 修改既有報告的範圍：
+7. **【必要】頁尾頁碼一定要照真實頁數顯示**，寫成「目前頁 / 總頁數」。目前頁＝該頁在 `deck.json` `order` 中的位置（封面算第 1 頁）。總頁數＝`order` 的長度。新增、刪除或移動頁面後，同一次修改就要更新全部頁尾。不要沿用大綱預計的頁數。（2026-10-20 加入）
+8. 修改既有報告的範圍：
    - 一般修改只動被指到的頁，不重跑整個流程。
    - 要求「嚴格重新修改」時，從第 1 步重跑完整流程。逐頁對照本規則檢查，違反的地方全部改掉，不要只修局部。
@@ -63,19 +64,44 @@
 
 11. 主軸以使用者指定的主題為準。擬大綱前，先用一句話寫出主問題，對照使用者的原話。大綱內容偏離該主題時，刪掉偏離的段落，不要保留。
+12. 介紹論文用哪些特徵建樹時，每篇都標明特徵進入建樹的哪一步：
+    - 事後挑樹（先由別的工具產生候選樹，再用特徵挑一棵）。
+    - 直接當建樹的輸入（例如距離分群）。
+    - 放進機率模型（likelihood）。
+    - 只做驗證，不參與建樹。
+
+    不要把「事後挑樹」寫成「用特徵建樹」。（2026-10-20 加入）
+13. 總覽頁講得太淺時，每個特徵各用一頁拆解。每頁用同一套三步驟版面：
+    1. 資料長怎樣（read 上看到什麼）。
+    2. 讀出什麼訊號（為什麼能推出先後或親緣）。
+    3. 怎麼進入建樹（接到哪個工具或模型）。
+
+    每一步都要有一張示意圖，文字只當圖說。細節數字先不放在頁面上。限制放講稿。這種拆解頁可以讓該段超過「結構與內容」第 2 條的 2 頁上限。（2026-10-20 加入）
+14. 介紹長讀特徵的頁只放真的用長讀資料的論文。短讀方法即使概念可以移植到長讀，也不要放進這類頁，以免觀眾誤會它用了長讀。（2026-10-20 加入）
+15. 把對話中的說明做成頁時，保留原說明的結構（例如兩種做法各一欄）。每個重點畫成一張流程示意圖，頁面只放短語，完整說明放講稿。示意的數值或柱高要標「示意」。（2026-10-20 加入）
+16. 研究計畫頁只放做法已經想清楚的部分。使用者覺得做法有疑義或「怪怪的」時，直接從頁面刪除，不要保留半套說明。（2026-10-20 加入）
+17. 畫驗證流程時，每一步都要畫出來，不能跳步。至少要有：輸入資料 → 軟體 → 軟體輸出的結果 → 和真值比對 → 得分。（2026-10-20 加入）
+18. 使用者要求先刪掉某個特徵或做法時（例如 pair），同一頁的圖、圖例、圖說與講稿要一起刪，不留下孤立的提及。（2026-10-20 加入）
+19. 評估指標（例如 AD F-score、V-measure）要配示意圖說明它在比什麼，不要只寫指標名稱。（2026-10-20 加入）
+20. 驗證計畫分「模擬資料」與「真實資料」兩部分時，真實資料頁沿用模擬頁的流程版面（第 17 條），並在圖上標明比對對象是什麼：single-cell 真值樹、別的工具推出的參考樹，或沒有真值的一致性檢查。不要把參考樹寫成真值。（2026-10-20 加入）
+21. 使用者要刪掉某頁、但保留其中做法到計畫時：從 `deck.json` `order` 移除該頁，同一次更新全部頁尾頁碼（「製作流程」第 7 條）。把該頁的做法、預期、限制與講稿原文搬進該簡報的大綱檔，標成「保留在計畫，不上投影片」，並註明刪除日期。原頁檔移到簡報目錄的 `removed_slides/`，不要直接丟掉。（2026-10-20 加入）
 
 ### 各簡報主軸
 
-- **2026-10-21 報告**（2026-10-19 指定）：只分兩大段。
-  1. 文獻調查：有沒有研究同時用 single-cell 定序建立真值樹來驗證，並用 long read、haplotype、phase set 等特徵重建演化樹。
-  2. 各論文的模擬資料與真實資料怎麼產生，作為我們做驗證資料的參考。
-  - 整份不放小鼠子株長讀研究（Liu 2026）。
-  - 收錄標準：論文至少要用一個建樹工具（現成軟體或自己的演算法）。只做 VAF 分群、畫圖（例如 Fishplot）或人工整理的樹不算。用現成工具也算，例如 ScisTree、ClonEvol。
-  - 依上述標準，整份不放：HPV 整合長讀研究（Akagi 2023）、骨髓瘤 linked-read 研究（Liu 2021）。
-  - 整份不放肝癌多點長讀研究（Zeng 2025）。它用 neighbor-joining 建樣本樹，但使用者決定不收。
-  - 整份不放肺癌細胞株長讀摘要（Donmez 2026，AACR 摘要）。
-  - 篇數以去掉上述論文之後的 17 篇計算。
-  - 不放我們自己的 6 株 ONT 細胞株。
-  - 已發表論文的細胞株資料（HCC1395 社群資料）可以列，因為它們是論文資料，不是我們的對照。
-  - 全冊用「長讀」，不用「long read」（封面標題也是）。
+每份簡報的主軸、收錄清單與篇數，記在該簡報的 `BRIEF.md`，不寫在本檔。本檔只放通用規則。
+
+1. **主軸**：使用者指定主軸時，記下指定日期、分幾段、每段回答什麼問題。之後的大綱都以它為準（見「結構與內容」第 11 條）。
+2. **收錄標準**：用「論文做了什麼」定義，不用論文名稱定義。例如「至少用一個建樹工具」：
+   - 現成軟體或自己的演算法都算。
+   - 只做 VAF 分群、畫圖或人工整理的樹不算。
+3. **排除與追加**：使用者點名排除或加入的論文，寫進 `BRIEF.md` 的清單，並附原因。符合標準但使用者不收的論文，也照樣記錄。
+4. **篇數**：以「符合標準的論文，扣掉排除清單」計算。篇數只記在 `BRIEF.md`。
+5. **加入或移除論文時**：
+   - 引用篇數、計數或結論的頁都要一起改，不要留下前後矛盾。
+   - 改變主結論時，先問使用者。
+   - 新論文的但書，全冊只講一次（見「講稿」第 9 條）。
+6. **資料範圍**：
+   - 我們自己未發表的資料，不當成文獻證據。
+   - 已發表論文的資料（包含細胞株）可以列。
+7. **用語**：同一份簡報的術語要統一，並記在 `BRIEF.md`，例如全冊用「long read」，不用「長讀」（2026-10-20 使用者指定）。
 
 ### 文字與表格
@@ -86,4 +112,5 @@
 4. 判斷論文有無 single-cell ground-truth 演化樹時，以 PhyClone 的 sc 演化樹為標準。
 5. 不要用觀眾不懂的黑話。黑話包括內部代號（C1、B04、K10、F1、C0、Phase 0）、未解釋的縮寫（PS、CP、AD、sc3、1A）、工具名（Battenberg、MuTect）與程式欄位名（tumour_content、major_cn）。必要的術語在第一次出現時，用圖或一句白話解釋。
+   - 例外：使用者指定要標工具名時，照指定標出，並在講稿用一句白話說明它做什麼（例如「PyClone-VI 依突變比例分群，ClonEvol 排出候選樹」）。（2026-10-20 加入）
 6. 頁面文字和圖一一對應：
    - 每個重點文字都要有對應的圖。
@@ -92,4 +119,5 @@
 8. 文字太小看不清時，先刪字，不要縮小字級。刪字後仍放不下，依「結構與內容」第 2 條處理。
 9. 圖中文字只放名詞或短語，整句放講稿。
+10. 圖上不用「雜訊」這類抽象詞。改寫成觀眾看得懂的具體現象，例如「VAF 估不準」。（2026-10-20 加入）
 
 ### 講稿
@@ -127,4 +155,6 @@
    | unphased | `#9AA3AE` |
 
+   read 位點、SNV 標示、IGV 圖、演化樹的畫法細則見第 8 條索引。
+
 5. 對照圖：
    - 兩個東西要比較時，可以用左右兩欄：左邊放基準，右邊放新做法，同一列放同一件事。例如預設做法對新方法、論文主張對實際行為、nominal purity 對實測 purity。單一概念不用硬湊對照，直接畫一張圖。
@@ -132,2 +162,13 @@
    - 結果用 ✓／✗ 加文字，不只靠顏色。
 6. 回饋或人工介入的箭頭用虛線，主流程用實線。
+7. 列出困難情境、陷阱或限制時，每一項都要畫出發生原因的機制示意圖（例如資料長怎樣、為什麼推錯）。不要只放名稱和代表圖示。原因的完整說明放講稿。（2026-10-20 加入）細則見第 8 條索引 D 節。
+8. **生物基因畫法細則索引。** 有日期的生物基因畫法規則已拆到 `report/BIO_DRAWING_RULES.md`。平時不用讀。畫的圖含下列關鍵字時，先讀該檔對應小節再畫：
+
+   | 關鍵字 | 小節 |
+   |---|---|
+   | read 位點、alt／ref 圖例、SNV 名稱（SNV1、SNV2） | A |
+   | IGV、read 堆疊、read 層資料、HP1／HP2 分區 | B |
+   | 演化樹、clone tree、設計樹／真值樹、軟體輸出樹、節點 CCF | C |
+   | subclonal CN、copy number、低 purity、低深度、陷阱或限制的機制圖 | D |
+
+   新增這類規則時，寫進該檔對應小節並附日期，再更新本表。

commit 6e51ec4ae43fdf38c0aca899e52f57f9038a92da
Author: paulboul1013 <paulboul1013@gmail.com>
Date:   Tue Oct 20 21:36:24 2026 +0800

    docs(claude): require Traditional Chinese in all replies
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/CLAUDE.md b/CLAUDE.md
index 5e40205..c05c276 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -47,4 +47,5 @@ python -m unittest phyclone.tests.unit_tests.test_tree.<Class>.<method>
 ## 工作慣例
 
+- **【強制】所有回答一律使用繁體中文**，包括對話回覆、摘要與說明；技術名詞依下一條保留英文。不論前文或工具輸出是什麼語言，都不可改用英文回答。
 - 文件以**繁體中文**撰寫，技術名詞（SNV、CCF、multiplicity、topology、purity、ESS 等）保留英文。
 - 製作 PPT／投影片時，原始檔一律輸出到 `report/<簡報名稱>/`（例如 `report/sc_groundtruth_slides/`），不要放在 `research/` 或暫存目錄。

commit 9ac5274ca0adca81b7c7db2404e6dbac9fa0e7a0
Author: paulboul1013 <paulboul1013@gmail.com>
Date:   Tue Oct 20 11:19:07 2026 +0800

    docs(report): refocus 10-21 deck on validation data availability
    
    Rebuild the 10-21 deck around one question: does any data set have both
    a single-cell truth tree and long-read features, and how did prior work
    build simulated and real data? Outline v5 -> v5.3 after two rounds of
    two-reviewer checks; 9 pages plus a terms page, published to the same
    artifact. Old v4 slides and the live backup are kept in old_v4_slides/.
    
    Also merge the pasted rule set into report_rule.md, add sections 10-11
    to VISUAL_SPEC.md, and remove the excluded papers from slides, outlines
    and briefs.
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/report/report_rule.md b/report/report_rule.md
index 2e0426a..baa4e46 100644
diff --git a/CLAUDE.md b/CLAUDE.md
index c05c276..f77709c 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -25,5 +25,6 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 - `daily/`：每日工作日誌 HTML（由 `daily-log` skill 產生；`.data/`、`.worklog_scan/` 是它的掃描產物）。日誌只作導覽，不能當成事實來源。
 - `report/`：PPT／投影片的輸出目錄（見工作慣例）。
-- `tools/`：視覺化元件產生腳本（`build_visual_components.py` 會呼叫 `~/.codex/skills/svg-component-builder`）。
+- `tools/`：視覺化元件產生腳本（`build_visual_components.py` 會呼叫 `~/.codex/skills/svg-component-builder`），以及資料分析腳本（例如 `pcdh_entropy.py`）。
+- `lab_report/`：實驗結果，一個實驗一個目錄（`YYYY-MM-DD_<主題>/`），內含 `README.md`（結論、資料、做法、結果、限制）與結果檔。產生結果的腳本放 `tools/`。
 
 ## PhyClone 常用指令
```
