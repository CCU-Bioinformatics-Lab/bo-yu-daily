# 2026-10-19 痕跡

- 模式：補寫 2026-10-19（整個日曆日，不動游標）｜既有 2026-10-19.json → 增補
- 掃描區間：2026-10-19T00:00:00 ~ 2026-10-19T23:59:59
- 其中重疊區（已讀過，只供補脈絡）：2026-10-19T00:00:00 ~ 2026-10-19T00:00:00
- ⚠️ 日期標籤 2026-10-19 只是檔名，不等於內容的涵蓋範圍（見上）

## git commits

- 097932c 19:18 chore(daily): add shared stylesheet for work logs
- 5df7a82 19:14 chore(daily): move day logs out of nested daily/daily/
- 5f0f31d 19:01 chore(daily): add 2026-10-19 work log and scan artifacts
- 91826b9 19:01 docs(report): add report rules, global visual spec, and 10-21 deck
- 65d54d9 19:01 docs(data): verify data provenance and competitor code
- 21fcced 19:01 docs(research): add SMC-Het benchmark notes and compatible scores
- a38cc57 19:01 docs(research): classify papers by platform x single-cell truth

## commit 改動的檔案

### 097932c chore(daily): add shared stylesheet for work logs
```
 daily/assets/style.css | 227 +++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 227 insertions(+)
```
### 5df7a82 chore(daily): move day logs out of nested daily/daily/
```
 daily/{daily => }/2026-10-19.html | 4 ++--
 daily/README.md                   | 6 +++---
 daily/index.html                  | 2 +-
 3 files changed, 6 insertions(+), 6 deletions(-)
```
### 5f0f31d chore(daily): add 2026-10-19 work log and scan artifacts
```
 .gitignore                                        |    1 +
 .worklog_scan/2026-10-19/candidates.json          |   17 +
 .worklog_scan/2026-10-19/layered.json             |  102 +
 .worklog_scan/2026-10-19/session-manifest.json    |   58 +
 .worklog_scan/2026-10-19/signals.md               |  146 +
 .worklog_scan/2026-10-19/traces.md                |  217 ++
 .worklog_scan/2026-10-19/transcript.txt           | 3437 +++++++++++++++++++++
 .worklog_scan/2026-10-19/transcript_user_only.txt |  762 +++++
 daily/.data/2026-10-19.json                       |  333 ++
 daily/.data/_cursor.json                          |    5 +
 daily/README.md                                   |   36 +
 daily/daily/2026-10-19.html                       |   49 +
 daily/index.html                                  |   16 +
 13 files changed, 5179 insertions(+)
```
### 91826b9 docs(report): add report rules, global visual spec, and 10-21 deck
```
 CLAUDE.md                                          |   1 +
 report/2026_10_21_slides/BRIEF.md                  | 127 ++++++
 report/2026_10_21_slides/OUTLINE.md                | 121 ++++++
 report/2026_10_21_slides/OUTLINE_v3.2.md           | 131 ++++++
 report/2026_10_21_slides/VISUALS.md                | 177 ++++++++
 .../old_27p_slides/s1-benchmark-scan.html          |  46 ++
 .../old_27p_slides/s1-categories.html              |  38 ++
 .../old_27p_slides/s1-why-truth.html               |  31 ++
 .../old_27p_slides/s2-hcc1395-baseline.html        |  42 ++
 .../old_27p_slides/s2-hcc1395-ref.html             |  47 ++
 .../old_27p_slides/s2-inventory.html               |  62 +++
 .../old_27p_slides/s2-sim-vs-real.html             |  29 ++
 .../old_27p_slides/s2-validation-layers.html       |  62 +++
 .../old_27p_slides/s3-clone-def.html               |  58 +++
 .../old_27p_slides/s3-papers-io.html               |  51 +++
 .../old_27p_slides/s3-subclonal-cn.html            |  38 ++
 .../old_27p_slides/s4-architecture.html            |  78 ++++
 .../old_27p_slides/s4-hp-semantics.html            |  56 +++
 .../old_27p_slides/s4-novelty.html                 |  65 +++
 .../old_27p_slides/s4-pair-patterns.html           |  95 +++++
 .../old_27p_slides/s4-short-vs-long.html           |  92 ++++
 .../old_27p_slides/s4-topology-constraint.html     |  35 ++
 .../old_27p_slides/s5-metrics.html                 |  80 ++++
 .../2026_10_21_slides/old_27p_slides/s5-next.html  |  56 +++
 .../old_27p_slides/s5-smchet-decompose.html        |  72 ++++
 .../old_27p_slides/s5-smchet-findings.html         |  35 ++
 report/2026_10_21_slides/old_v3_slides/agenda.html |  56 +++
 report/2026_10_21_slides/old_v3_slides/cover.html  |  12 +
 report/2026_10_21_slides/old_v3_slides/deck.json   |   1 +
 report/2026_10_21_slides/old_v3_slides/s1-gap.html | 154 +++++++
 .../2026_10_21_slides/old_v3_slides/s1-lung.html   |  94 ++++
 .../2026_10_21_slides/old_v3_slides/s2-data.html   |  69 +++
 .../old_v3_slides/s2-hcc1395.html                  |  45 ++
 .../old_v3_slides/s3-phyclone-io.html              | 100 +++++
 .../old_v3_slides/s3-pitfalls.html                 | 107 +++++
 report/2026_10_21_slides/old_v3_slides/s4-hp.html  | 101 +++++
 .../2026_10_21_slides/old_v3_slides/s4-pair.html   |  40 ++
 .../2026_10_21_slides/old_v3_slides/s5-score.html  |  46 ++
 .../2026_10_21_slides/old_v3_slides/s5-smchet.html |  61 +++
 .../2026_10_21_slides/old_v3_slides/summary.html   |  45 ++
 report/2026_10_21_slides/project/deck.json         |   1 +
 .../2026_10_21_slides/project/slides/agenda.html   |  41 ++
 report/2026_10_21_slides/project/slides/cover.html |  11 +
 .../project/slides/s1-hcc1395.html                 | 131 ++++++
 .../project/slides/s2-phyclone-io.html             | 100 +++++
 .../project/slides/s2-pitfalls.html                | 111 +++++
 .../2026_10_21_slides/project/slides/s3-gap.html   | 116 +++++
 report/2026_10_21_slides/project/slides/s4-hp.html | 110 +++++
 .../2026_10_21_slides/project/slides/s4-pair.html  |  40 ++
 .../project/slides/s5-validate.html                |  80 ++++
 .../2026_10_21_slides/project/slides/summary.html  |  47 ++
 report/2026_10_21_slides/sources/s5908_text.md     | 474 +++++++++++++++++++++
 report/VISUAL_SPEC.md                              | 200 +++++++++
 report/data.png                                    | Bin 171385 -> 0 bytes
 report/data_hp.png                                 | Bin 194102 -> 0 bytes
 report/report_rule.md                              | 116 +++++
 report/sc_groundtruth_slides/project/deck.json     |   1 -
 .../project/slides/overview.html                   | 133 ------
 58 files changed, 4234 insertions(+), 134 deletions(-)
```
### 65d54d9 docs(data): verify data provenance and competitor code
```
 research/CONTEXT.md                                |  2 +-
 research/terminology/terms.tsv                     |  2 +-
 .../tumor_phylogeny_2026/methods_survey/README.md  |  4 +--
 .../papers/M03_donmez_aacr2026/README.md           | 30 ++++++++++++++++--
 .../references/R01_mcpherson_hgsoc_2016/README.md  |  8 ++++-
 tumor_sample.md                                    | 37 +++++++++++++++++++++-
 6 files changed, 75 insertions(+), 8 deletions(-)
```
### 21fcced docs(research): add SMC-Het benchmark notes and compatible scores
```
 evaluation_v1.md                                   |   95 +
 .../tumor_phylogeny_2026/methods_survey/README.md  |    1 +
 .../papers/M07_smchet_benchmark_2024/README.md     |  213 +++
 .../papers/M07_smchet_benchmark_2024/paper.txt     | 1930 ++++++++++++++++++++
 .../M07_smchet_benchmark_2024/pmc_fulltext.txt     |  547 ++++++
 .../M07_smchet_benchmark_2024/supplement.txt       |  739 ++++++++
 .../workers/W8_benchmark_update_2026-10-18.md      |   71 +
 7 files changed, 3596 insertions(+)
```
### a38cc57 docs(research): classify papers by platform x single-cell truth
```
 CLAUDE.md                                          |   1 +
 research/INDEX.md                                  |   1 +
 research/PAPER_CATEGORIES.md                       | 169 +++++++++++++++++++++
 .../hcc1395_tumor_evolution_tree_review/README.md  |  25 +++
 research/paper_categories.tsv                      |  23 +++
 .../c1_bulk_short_read/M05                         |   1 +
 .../c1_bulk_short_read/M07                         |   1 +
 .../c1_read_cooccurrence_short/B02                 |   1 +
 .../c1_read_cooccurrence_short/M02                 |   1 +
 .../c1_single_cell_input_no_truth/B07              |   1 +
 .../c1_single_cell_input_no_truth/M04              |   1 +
 .../C2_long_read_feature/c2_local_order/M03        |   1 +
 .../c2_long_read_data_only/B01                     |   1 +
 .../C2_long_read_feature/c2_molecular_history/B08  |   1 +
 .../C2_long_read_feature/c2_sample_tree_sv/B06     |   1 +
 .../c3a_patient_sc_reference/A01                   |   1 +
 .../c3a_patient_sc_reference/A02                   |   1 +
 .../c3a_patient_sc_reference/A03                   |   1 +
 .../c3a_patient_sc_reference/A04                   |   1 +
 .../c3a_patient_sc_reference/A05                   |   1 +
 .../c3a_patient_sc_reference/B03                   |   1 +
 .../c3a_patient_sc_reference/R01                   |   1 +
 .../c3a_sc_benchmark_truth/M01                     |   1 +
 .../c3a_sc_benchmark_truth/M06                     |   1 +
 .../C3a_sc_truth_x_short_read/c3a_sc_partial/B05   |   1 +
 .../C3a_sc_truth_x_short_read/c3a_sc_partial/H01   |   1 +
 .../c3b_topology_constraint_sc_partial/B04         |   1 +
 .../phyclone_research/notes/zh-TW/00_SOURCE_MAP.md |  25 +++
 research/tools/sync_paper_categories.py            | 164 ++++++++++++++++++++
 research/tumor_phylogeny_2026/README.md            |   2 +
 research/tumor_phylogeny_2026/catalog.json         |  14 ++
 .../tumor_phylogeny_2026/methods_survey/README.md  |   2 +
 .../papers/M01_phyclone_2025/README.md             |  25 +++
 .../papers/M02_treeclone_2019/README.md            |  25 +++
 .../papers/M03_donmez_aacr2026/README.md           |  25 +++
 .../papers/M04_pharming_2026/README.md             |  25 +++
 .../papers/M05_tusv_ext_2022/README.md             |  25 +++
 .../papers/M06_phylex_2023/README.md               |  25 +++
 .../papers/A01_ovarian_cfDNA_2025/README.md        |  25 +++
 .../papers/A02_sprinter_2025/README.md             |  25 +++
 .../papers/A03_pancreatic_snDNA_2023/README.md     |  25 +++
 .../papers/A04_aml_strandseq_2024/README.md        |  25 +++
 .../papers/A05_mpal_multiome_2024/README.md        |  25 +++
 .../papers/B01_melanoma_longread_2026/README.md    |  25 +++
 .../papers/B02_myeloma_linkedread_2021/README.md   |  25 +++
 .../README.md                                      |  25 +++
 .../B04_lung_longread_phasing_2022/README.md       |  25 +++
 .../papers/B05_medicc2_2022/README.md              |  25 +++
 .../B06_hcc_multisite_longread_2025/README.md      |  25 +++
 .../papers/B07_numbat_2022/README.md               |  25 +++
 .../papers/B08_hpv_integration_2023/README.md      |  25 +++
 .../references/R01_mcpherson_hgsoc_2016/README.md  |  25 +++
 52 files changed, 948 insertions(+)
```

## 未提交的變動

```
 M .worklog_scan/2026-10-19/traces.md
 M .worklog_scan/2026-10-19/transcript.txt
 M .worklog_scan/2026-10-19/transcript_user_only.txt
 M daily/.data/2026-10-19.json
 M daily/2026-10-19.html
 M report/2026_10_21_slides/BRIEF.md
 M report/2026_10_21_slides/OUTLINE_v3.2.md
 M report/2026_10_21_slides/VISUALS.md
 M report/2026_10_21_slides/old_27p_slides/s1-benchmark-scan.html
 M report/2026_10_21_slides/old_27p_slides/s1-categories.html
 M report/2026_10_21_slides/old_27p_slides/s3-papers-io.html
 M report/2026_10_21_slides/old_27p_slides/s4-novelty.html
 M report/2026_10_21_slides/project/deck.json
 M report/2026_10_21_slides/project/slides/agenda.html
 M report/2026_10_21_slides/project/slides/cover.html
 D report/2026_10_21_slides/project/slides/s1-hcc1395.html
 D report/2026_10_21_slides/project/slides/s2-phyclone-io.html
 D report/2026_10_21_slides/project/slides/s2-pitfalls.html
 D report/2026_10_21_slides/project/slides/s3-gap.html
 D report/2026_10_21_slides/project/slides/s4-hp.html
 D report/2026_10_21_slides/project/slides/s4-pair.html
 D report/2026_10_21_slides/project/slides/s5-validate.html
 M report/2026_10_21_slides/project/slides/summary.html
 M report/2026_10_21_slides/sources/s5908_text.md
 M report/VISUAL_SPEC.md
 M report/report_rule.md
 M research/CONTEXT.md
 M research/PAPER_CATEGORIES.md
 M research/SYNTHESIS_phyclone_longphase.md
 M research/TERMINOLOGY.md
 M research/paper_categories.tsv
 D research/papers_by_category/C1_short_read_or_unspecified/c1_read_cooccurrence_short/B02
 D research/papers_by_category/C2_long_read_feature/c2_local_order/M03
 D research/papers_by_category/C2_long_read_feature/c2_molecular_history/B08
 D research/papers_by_category/C2_long_read_feature/c2_sample_tree_sv/B06
 M research/terminology/corpus.tsv
 M research/terminology/evidence.tsv
 M research/terminology/terms.tsv
 M research/tumor_phylogeny_2026/B_SUMMARY.md
 M research/tumor_phylogeny_2026/CODE_AVAILABILITY.md
 M research/tumor_phylogeny_2026/INTERSECTION_SUMMARY.md
 M research/tumor_phylogeny_2026/README.md
 M research/tumor_phylogeny_2026/REPO_IMPROVEMENTS.md
 M research/tumor_phylogeny_2026/SEARCH_LOG.md
 M research/tumor_phylogeny_2026/catalog.json
 M research/tumor_phylogeny_2026/manifest.json
 M research/tumor_phylogeny_2026/manifest.tsv
 M research/tumor_phylogeny_2026/methods_survey/README.md
D  research/tumor_phylogeny_2026/methods_survey/papers/M03_donmez_aacr2026/README.md
D  research/tumor_phylogeny_2026/methods_survey/papers/M03_donmez_aacr2026/abstract.txt
 M research/tumor_phylogeny_2026/methods_survey/workers/W4_read_phasing_longread.md
 M research/tumor_phylogeny_2026/methods_survey/workers/W7_proceedings_2025_2026.md
 M research/tumor_phylogeny_2026/methods_survey/workers/W8_benchmark_update_2026-10-18.md
 D research/tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/README.md
 D research/tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/paper.txt
 D research/tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/PDF_PROVENANCE.md
 D research/tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/README.md
 D research/tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/oa_metadata.json
 D research/tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/paper.txt
 D research/tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/supplement.txt
```

## 當天新增或修改的檔案（排除 .git / 掃描暫存 / 大型二進位）

```
daily/2026-10-19.html
daily/assets/style.css
daily/.data/2026-10-19.json
daily/.data/_cursor.json
daily/.data/_private/2026-10-19.evidence.json
daily/index.html
daily/README.md
.gitignore
report/2026_10_21_slides/BRIEF.md
report/2026_10_21_slides/old_27p_slides/s1-benchmark-scan.html
report/2026_10_21_slides/old_27p_slides/s1-categories.html
report/2026_10_21_slides/old_27p_slides/s3-papers-io.html
report/2026_10_21_slides/old_27p_slides/s4-novelty.html
report/2026_10_21_slides/old_v3_slides/agenda.html
report/2026_10_21_slides/old_v3_slides/cover.html
report/2026_10_21_slides/old_v3_slides/deck.json
report/2026_10_21_slides/old_v3_slides/s1-gap.html
report/2026_10_21_slides/old_v3_slides/s1-lung.html
report/2026_10_21_slides/old_v3_slides/s2-data.html
report/2026_10_21_slides/old_v3_slides/s2-hcc1395.html
report/2026_10_21_slides/old_v3_slides/s3-phyclone-io.html
report/2026_10_21_slides/old_v3_slides/s3-pitfalls.html
report/2026_10_21_slides/old_v3_slides/s4-hp.html
report/2026_10_21_slides/old_v3_slides/s4-pair.html
report/2026_10_21_slides/old_v3_slides/s5-score.html
report/2026_10_21_slides/old_v3_slides/s5-smchet.html
report/2026_10_21_slides/old_v3_slides/summary.html
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
report/2026_10_21_slides/OUTLINE.md
report/2026_10_21_slides/OUTLINE_v3.2.md
report/2026_10_21_slides/OUTLINE_v5.1.md
report/2026_10_21_slides/OUTLINE_v5.2.md
report/2026_10_21_slides/OUTLINE_v5.3.md
report/2026_10_21_slides/OUTLINE_v5.md
report/2026_10_21_slides/project/deck.json
report/2026_10_21_slides/project/slides/agenda.html
report/2026_10_21_slides/project/slides/cover.html
report/2026_10_21_slides/project/slides/s1-count.html
report/2026_10_21_slides/project/slides/s1-features.html
report/2026_10_21_slides/project/slides/s1-terms.html
report/2026_10_21_slides/project/slides/s2-longread.html
report/2026_10_21_slides/project/slides/s2-sc-trees.html
report/2026_10_21_slides/project/slides/s2-sim-layers.html
report/2026_10_21_slides/project/slides/s2-smchet.html
report/2026_10_21_slides/project/slides/summary.html
report/2026_10_21_slides/REVIEW_v5.md
report/2026_10_21_slides/sources/s5908_text.md
report/2026_10_21_slides/VISUALS.md
report/report_rule.md
report/VISUAL_SPEC.md
research/CONTEXT.md
research/hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md
research/PAPER_CATEGORIES.md
research/paper_categories.tsv
research/phyclone_research/notes/zh-TW/00_SOURCE_MAP.md
research/SYNTHESIS_phyclone_longphase.md
research/terminology/corpus.tsv
research/terminology/evidence.tsv
research/TERMINOLOGY.md
research/terminology/terms.tsv
research/tumor_phylogeny_2026/B_SUMMARY.md
research/tumor_phylogeny_2026/catalog.json
research/tumor_phylogeny_2026/CODE_AVAILABILITY.md
research/tumor_phylogeny_2026/INTERSECTION_SUMMARY.md
research/tumor_phylogeny_2026/longread_tree_search_2026-10-19/raw/search_A_cooccurrence.md
research/tumor_phylogeny_2026/longread_tree_search_2026-10-19/raw/search_B_haplotype_cn.md
research/tumor_phylogeny_2026/longread_tree_search_2026-10-19/raw/search_C_singlecell_methyl_sv.md
research/tumor_phylogeny_2026/longread_tree_search_2026-10-19/raw/search_D_repos_preprints.md
research/tumor_phylogeny_2026/longread_tree_search_2026-10-19/README.md
research/tumor_phylogeny_2026/manifest.json
research/tumor_phylogeny_2026/manifest.tsv
research/tumor_phylogeny_2026/methods_survey/papers/M01_phyclone_2025/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M02_treeclone_2019/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M04_pharming_2026/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M05_tusv_ext_2022/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M06_phylex_2023/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M08_bitphylogeny_2015/paper.txt
research/tumor_phylogeny_2026/methods_survey/papers/M08_bitphylogeny_2015/paper.xml
```

## commit 動過的檔案（git 記錄，不受 mtime 覆蓋）

```
CLAUDE.md
daily/2026-10-19.html
daily/assets/style.css
daily/daily/2026-10-19.html
daily/.data/2026-10-19.json
daily/.data/_cursor.json
daily/index.html
daily/README.md
evaluation_v1.md
.gitignore
report/2026_10_21_slides/BRIEF.md
report/2026_10_21_slides/old_27p_slides/s1-benchmark-scan.html
report/2026_10_21_slides/old_27p_slides/s1-categories.html
report/2026_10_21_slides/old_27p_slides/s1-why-truth.html
report/2026_10_21_slides/old_27p_slides/s2-hcc1395-baseline.html
report/2026_10_21_slides/old_27p_slides/s2-hcc1395-ref.html
report/2026_10_21_slides/old_27p_slides/s2-inventory.html
report/2026_10_21_slides/old_27p_slides/s2-sim-vs-real.html
report/2026_10_21_slides/old_27p_slides/s2-validation-layers.html
report/2026_10_21_slides/old_27p_slides/s3-clone-def.html
report/2026_10_21_slides/old_27p_slides/s3-papers-io.html
report/2026_10_21_slides/old_27p_slides/s3-subclonal-cn.html
report/2026_10_21_slides/old_27p_slides/s4-architecture.html
report/2026_10_21_slides/old_27p_slides/s4-hp-semantics.html
report/2026_10_21_slides/old_27p_slides/s4-novelty.html
report/2026_10_21_slides/old_27p_slides/s4-pair-patterns.html
report/2026_10_21_slides/old_27p_slides/s4-short-vs-long.html
report/2026_10_21_slides/old_27p_slides/s4-topology-constraint.html
report/2026_10_21_slides/old_27p_slides/s5-metrics.html
report/2026_10_21_slides/old_27p_slides/s5-next.html
report/2026_10_21_slides/old_27p_slides/s5-smchet-decompose.html
report/2026_10_21_slides/old_27p_slides/s5-smchet-findings.html
report/2026_10_21_slides/old_v3_slides/agenda.html
report/2026_10_21_slides/old_v3_slides/cover.html
report/2026_10_21_slides/old_v3_slides/deck.json
report/2026_10_21_slides/old_v3_slides/s1-gap.html
report/2026_10_21_slides/old_v3_slides/s1-lung.html
report/2026_10_21_slides/old_v3_slides/s2-data.html
report/2026_10_21_slides/old_v3_slides/s2-hcc1395.html
report/2026_10_21_slides/old_v3_slides/s3-phyclone-io.html
report/2026_10_21_slides/old_v3_slides/s3-pitfalls.html
report/2026_10_21_slides/old_v3_slides/s4-hp.html
report/2026_10_21_slides/old_v3_slides/s4-pair.html
report/2026_10_21_slides/old_v3_slides/s5-score.html
report/2026_10_21_slides/old_v3_slides/s5-smchet.html
report/2026_10_21_slides/old_v3_slides/summary.html
report/2026_10_21_slides/OUTLINE.md
report/2026_10_21_slides/OUTLINE_v3.2.md
report/2026_10_21_slides/project/deck.json
report/2026_10_21_slides/project/slides/agenda.html
report/2026_10_21_slides/project/slides/cover.html
report/2026_10_21_slides/project/slides/s1-hcc1395.html
report/2026_10_21_slides/project/slides/s2-phyclone-io.html
report/2026_10_21_slides/project/slides/s2-pitfalls.html
report/2026_10_21_slides/project/slides/s3-gap.html
report/2026_10_21_slides/project/slides/s4-hp.html
report/2026_10_21_slides/project/slides/s4-pair.html
report/2026_10_21_slides/project/slides/s5-validate.html
report/2026_10_21_slides/project/slides/summary.html
report/2026_10_21_slides/sources/s5908_text.md
report/2026_10_21_slides/VISUALS.md
report/data_hp.png
report/data.png
report/report_rule.md
report/sc_groundtruth_slides/project/deck.json
report/sc_groundtruth_slides/project/slides/overview.html
report/VISUAL_SPEC.md
research/CONTEXT.md
research/hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/README.md
research/INDEX.md
research/PAPER_CATEGORIES.md
research/paper_categories.tsv
research/papers_by_category/C1_short_read_or_unspecified/c1_bulk_short_read/M05
research/papers_by_category/C1_short_read_or_unspecified/c1_bulk_short_read/M07
research/papers_by_category/C1_short_read_or_unspecified/c1_read_cooccurrence_short/B02
research/papers_by_category/C1_short_read_or_unspecified/c1_read_cooccurrence_short/M02
research/papers_by_category/C1_short_read_or_unspecified/c1_single_cell_input_no_truth/B07
research/papers_by_category/C1_short_read_or_unspecified/c1_single_cell_input_no_truth/M04
research/papers_by_category/C2_long_read_feature/c2_local_order/M03
research/papers_by_category/C2_long_read_feature/c2_long_read_data_only/B01
research/papers_by_category/C2_long_read_feature/c2_molecular_history/B08
research/papers_by_category/C2_long_read_feature/c2_sample_tree_sv/B06
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/A01
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/A02
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/A03
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/A04
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/A05
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/B03
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_patient_sc_reference/R01
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_sc_benchmark_truth/M01
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_sc_benchmark_truth/M06
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_sc_partial/B05
research/papers_by_category/C3a_sc_truth_x_short_read/c3a_sc_partial/H01
research/papers_by_category/C3b_sc_truth_x_long_read/c3b_topology_constraint_sc_partial/B04
research/phyclone_research/notes/zh-TW/00_SOURCE_MAP.md
research/terminology/terms.tsv
research/tools/sync_paper_categories.py
research/tumor_phylogeny_2026/catalog.json
research/tumor_phylogeny_2026/methods_survey/papers/M01_phyclone_2025/README.md
research/tumor_phylogeny_2026/methods_survey/papers/M02_treeclone_2019/README.md
```

## 當天新增的圖


## 當天的 .meta.json（含指令列、seed、參數）


## 當天新增或改動的結果表（前 15 行）

### research/paper_categories.tsv
```
id	category	subtype	sc_truth_strength	title	year	doc_type	material	platform_class	platform_detail	long_read_role	long_read_features	single_cell_truth	single_cell_tech	input_is_single_cell	tree_type	cross_tags	keywords_en	keywords_zh	summary_zh	borderline_zh	dir	readme	extra_readmes
M05	C1	c1_bulk_short_read	none	TUSV-ext: Reconstructing tumor clonal lineage trees incorporating SNVs, CNAs and SVs	2022	method	mixed	short_or_unspecified	multi-region bulk short-read WGS; simulated (no platform)	none		simulated_only		false	clone_tree; cn_event_tree	structural_variant; latent_allele_phasing; multi_region	tusv-ext; ilp; gurobi; multi-region bulk; snv; structural variation; sv breakpoint; allele-specific copy number; latent allele phasing; dollo; deconvolution; prostate cancer	整數線性規劃; 結構變異; 等位基因特異拷貝數; 多區域取樣; 潛在定相	ILP 聯合 SNV/SV/CNA 建樹；phasing 是潛變數。	沒有 long-read 特徵。潛在 allele 變數 D 可改吃觀測到的 HP（屬本 repo 推論）。	tumor_phylogeny_2026/methods_survey/papers/M05_tusv_ext_2022	tumor_phylogeny_2026/methods_survey/papers/M05_tusv_ext_2022/README.md	
M07	C1	c1_bulk_short_read	none	SMC-Het DREAM: Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction	2024	benchmark	simulated	short_or_unspecified	simulated Illumina WGS (BAMSurgeon on GM24385)	none		simulated_only		false	clone_tree	simulated_benchmark; evaluation_metrics	smc-het; dream challenge; bamsurgeon; battenberg; mutect; single-sample bulk; subclonal reconstruction; nrpcc; phylowgs; dpclust; simulated tumors; co-clustering; ancestor-descendant matrix	社群基準測試; 模擬腫瘤; 單樣本; 次克隆重建; 拷貝數	短讀模擬的單樣本 benchmark，比較 31 個方法。	真值是模擬設計，不來自 single-cell。long-read phasing 只列為未來工作。	tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024	tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/README.md	
M02	C1	c1_read_cooccurrence_short	none	TreeClone: Reconstruction of tumor subclone phylogeny based on mutation pairs using next generation sequencing data	2019	method	mixed	short_or_unspecified	Illumina HiSeq PE100 WES; simulated	none		simulated_only		false	clone_tree	read_cooccurrence_model; transferable_to_long_read; copy_neutral_only	treeclone; mutation pairs; read-level co-occurrence; local haplotype; lochap; paired-end reads; multinomial read classes; copy-neutral; bayesian mcmc; parallel tempering; lung adenocarcinoma; multi-region	突變對; 同一 read 共現; 局部 haplotype; 肺腺癌; 亞克隆演化樹	用同 read 上的 SNV pair 推 clone tree；只用 short read。	likelihood 以同 read 共現為核心，但只在短 PE reads 上評估。likelihood 不依賴 read 長度，可移植到 long read。真值只來自模擬。	tumor_phylogeny_2026/methods_survey/papers/M02_treeclone_2019	tumor_phylogeny_2026/methods_survey/papers/M02_treeclone_2019/README.md	
M08	C1	c1_read_cooccurrence_short	none	BitPhylogeny: a probabilistic framework for reconstructing intra-tumor phylogenies	2015	method	mixed	short_or_unspecified	454/Roche bisulfite amplicon reads (IRX2 locus, Sottoriva colon cancer); single-cell exome (Hou 2012 MPN); simulated	none		simulated_only	single-cell exome (Hou 2012 MPN, input only, no truth tree)	true	clone_tree	read_cooccurrence_model; transferable_to_long_read; methylation; single_cell_input; no_copy_number	bitphylogeny; tssb; tree-structured stick-breaking; read-level pattern; methyltype; co-occurrence; joint clustering and tree inference; clones at inner nodes; bisulfite sequencing; colon cancer; myeloproliferative neoplasm; single-cell exome; mcmc; mpear	樹狀 stick-breaking; read 層級 pattern; 共現; 甲基化; clone 與樹聯合推論; 大腸癌; 骨髓增生性腫瘤	每條 read 的多位點 pattern 當一次抽樣，用 TSSB 聯合推 clone 與樹；沒有 CN。	454 bisulfite read 和 single-cell exome 都不是 ONT／PacBio long read，平台軸算短讀。MPN 案例輸入是 single cell，但沒有真值樹，準確度只來自模擬，所以放 C1。共現透過整條 read 共用一個 clone 來源進入模型，可移植到 long read。	tumor_phylogeny_2026/methods_survey/papers/M08_bitphylogeny_2015	tumor_phylogeny_2026/methods_survey/papers/M08_bitphylogeny_2015/README.md	
B07	C1	c1_single_cell_input_no_truth	none	Haplotype-aware analysis of somatic copy number variations from single-cell transcriptomes (Numbat)	2022	method	mixed	short_or_unspecified	10x scRNA-seq (short read); Eagle2 population phasing reference	none		scrna_only	10x scRNA-seq; NCI-N87 paired scDNA (CN check only)	true	cell_tree; cn_event_tree	single_cell_input; haplotype_specific_cn; population_phasing	numbat; scrna-seq; haplotype-aware hmm; allele-specific copy number; cnloh; eagle2 population phasing; perfect phylogeny; scistree; multiple myeloma; anaplastic thyroid cancer; single-cell cnv; clonal architecture	單細胞轉錄體; 單倍型感知; 拷貝數變異; 族群相位; 中性拷貝數LOH; 細胞演化樹	scRNA 加族群 phasing 推 CNV 細胞樹；不是 long read。	phasing 來自 Eagle2 族群參考，不來自 read。scDNA 只佐證 CN calls，不提供參考 topology，所以放 C1。	tumor_phylogeny_2026/papers/B07_numbat_2022	tumor_phylogeny_2026/papers/B07_numbat_2022/README.md	
M04	C1	c1_single_cell_input_no_truth	none	Pharming: Joint Clonal Tree Reconstruction of SNV and Copy Number Aberration Evolution from Single-Cell DNA Sequencing of Tumors	2026	method	mixed	short_or_unspecified	low-pass scDNA (ACT, DLP+); simulated	none		simulated_only	ACT; DLP+	true	clone_tree; cn_event_tree; mutation_tree	single_cell_input; haplotype_specific_cn; snv_cna_joint	pharming; scdna-seq; low-pass single-cell; act; dlp+; joint snv cna tree; haplotype-specific copy number; cnrein; dollo snv loss; infinite alleles cna; triple-negative breast cancer; ovarian cancer cell lines	單細胞 DNA 定序; SNV 與 CNA 聯合演化樹; haplotype 特異 CN; 三陰性乳癌; 卵巢癌細胞株	單細胞 SNV+CNA 聯合 clone tree；只有模擬真值。	方法從病人 scDNA 推樹，但論文不把結果當參考答案，也不與獨立 sc 樹比對。準確度只來自模擬，所以放 C1。	tumor_phylogeny_2026/methods_survey/papers/M04_pharming_2026	tumor_phylogeny_2026/methods_survey/papers/M04_pharming_2026/README.md	
B01	C2	c2_long_read_data_only	none	Long-read sequencing of single cell-derived melanoma sublines reveals divergent and parallel genomic and epigenomic evolutionary trajectories	2026	application	mouse	long_read_data_only	ONT R10.4 PromethION bulk WGS per subline	tree_input	ONT SNV genotypes (tree); Severus SV and 5mC DMR placed on fixed tree	single_cell_derived_lines	single-cell cloning to sublines; scRNA-seq (phenotype only)	false	clone_tree	single_cell_derived_lines; treeharmonizer; methylation; structural_variant; mouse	scistree; treeharmonizer; oxford nanopore; long-read wgs; single cell-derived sublines; mouse melanoma; b2905; structural variants; severus; wakhan; methylation dmr; variant placement	長讀定序; 單細胞衍生亞株; 小鼠黑色素瘤; 結構變異; 甲基化; 變異放置	ONT SNV 建樹；SV／甲基化只事後放上固定樹。	資料是 ONT，但只有 SNV genotype 進入 ScisTree。沒有共現、phasing 或 SV 約束 topology，所以放 C2 的「只用 long-read 資料」子類。sublines 由單細胞衍生，但沒有 sc 定序真值樹。	tumor_phylogeny_2026/papers/B01_melanoma_longread_2026	tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/README.md	
A01	C3a	c3a_patient_sc_reference	reference_tree	Tracking clonal evolution during treatment in ovarian cancer using cell-free DNA	2025	application	human_patient	short_or_unspecified	DLP+ scWGS (Illumina)	none		patient_scdna_reference_tree	DLP+ scWGS	true	cell_tree; clone_tree; cn_event_tree	haplotype_specific_cn; structural_variant; longitudinal; cfdna	hgsoc; ovarian cancer; cfdna; scwgs; dlp+; medicc2; signals; allele-specific copy number; structural variants; ccf calibration; longitudinal; wgd	卵巢癌; 游離DNA; 單細胞DNA; 等位基因特異拷貝數; 縱向追蹤; 結構變異	病人 scWGS 建 MEDICC2 樹；cfDNA 追蹤抗藥 clone。	clade 到 clone 的定義是人工選取。這是參考樹，不是絕對真值。haplotype 是 SIGNALS homolog CN，不是 read phasing。	tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025	tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md	
A02	C3a	c3a_patient_sc_reference	reference_tree	Characterizing the evolutionary dynamics of cancer proliferation in single-cell clones with SPRINTER	2025	method	human_patient	short_or_unspecified	DLP+ scWGS (Illumina)	none		patient_scdna_reference_tree	DLP+ scWGS	true	clone_tree; cn_event_tree	cell_cycle; metastasis; wgd	sprinter; nsclc; scwgs; dlp+; cell cycle; s-phase; huntress; medicc2; machina; metastatic seeding; ctdna shedding; copy number	單細胞DNA; 細胞週期; 肺癌; 轉移播種; 拷貝數; 循環腫瘤DNA	SPRINTER 校正 S 期 CN；病人 scDNA 樹連結增殖與轉移。	FACS/EdU 真值只驗證 S 期判定，不驗證 topology。MEDICC2 CNA 樹固定在 HUNTRESS topology 上，不能當獨立驗證。	tumor_phylogeny_2026/papers/A02_sprinter_2025	tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md	
A03	C3a	c3a_patient_sc_reference	reference_tree	Application of high-throughput single-nucleus DNA sequencing in pancreatic cancer	2023	application	human_patient	short_or_unspecified	Tapestri snDNA amplicon panel (Illumina)	none		patient_scdna_reference_tree	Tapestri snDNA	true	clone_tree; mutation_tree	amplicon_panel; metastasis	pdac; pancreatic cancer; sndna-seq; tapestri; amplicon panel; scg; smad4 deletion; kras; allelic dropout; doublet; mutual exclusivity; clone phylogeny	胰臟癌; 單核DNA定序; 擴增子面板; 互斥變異; 等位基因脫落; 克隆樹	Tapestri snDNA 建 PA04 的 SNV+SMAD4 刪除 clone 樹。	完整樹只有 PA04 一位病人，且受 93 基因 panel 限制。	tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023	tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md	
A04	C3a	c3a_patient_sc_reference	reference_tree	Single-cell multiomics analysis reveals dynamic clonal evolution and targetable phenotypes in acute myeloid leukemia with complex karyotype	2024	application	mixed	short_or_unspecified	Strand-seq scTRIP (Illumina NextSeq); OGM validation	none		patient_scdna_reference_tree	Strand-seq scTRIP; CITE-seq	true	clone_tree; cn_event_tree	haplotype_specific_cn; structural_variant; strand_seq_phasing; pdx	ck-aml; acute myeloid leukemia; strand-seq; sctrip; chromosome-length haplotype; structural variants; chromothripsis; bfb; optical genome mapping; pdx; haplotype-aware copy number	急性骨髓性白血病; 複雜核型; 單細胞結構變異; 染色體長度單倍型; 染色體碎裂; 人工整理樹	Strand-seq 單細胞 SV+單倍型建 CK-AML 人工 clone 樹。	haplotype 來自 Strand-seq 模板股，不是 long read。OGM 是光學圖譜，不是定序 read。材料含病人與 PDX。	tumor_phylogeny_2026/papers/A04_aml_strandseq_2024	tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md	
A05	C3a	c3a_patient_sc_reference	reference_tree	Multiomic single cell sequencing identifies stemlike nature of mixed phenotype acute leukemia	2024	application	human_patient	short_or_unspecified	DAb-seq (Tapestri) amplicon; Illumina NovaSeq	none		patient_scdna_reference_tree	DAb-seq scDNA+protein; CITE-seq	true	mutation_tree; clone_tree	amplicon_panel; phenotype	mpal; mixed phenotype acute leukemia; dab-seq; tapestri; scdna; scite; mutation tree; cite-seq; surface protein; flt3 itd; leukemia gene panel	混合表型急性白血病; 單細胞DNA; 突變樹; 表面蛋白; 克隆表型; 基因面板	DAb-seq 單細胞 DNA 以 SCITE 建 MPAL 突變樹。	只有 20 基因 driver panel。參考樹是固定錯誤模型下的 SCITE 輸出。	tumor_phylogeny_2026/papers/A05_mpal_multiome_2024	tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md	
B03	C3a	c3a_patient_sc_reference	reference_tree	Single-cell genomic variation induced by mutational processes in cancer	2022	application	mixed	short_or_unspecified	DLP+ scDNA-seq (Illumina); ONT PromethION for SV validation only	validation_only	ONT read-spanned SV support (validation); WhatsHap haplotag (validation)	patient_scdna_reference_tree	DLP+ scDNA-seq; scRNA-seq	true	cell_tree; cn_event_tree	haplotype_specific_cn; long_read_validation_only; parallel_evolution; pdx; roth_lab	signals; dlp+; scdna-seq; sitka; haplotype-specific copy number; hgsc; tnbc; pdx; 184-htert; parallel evolution; cnloh; hlamp; oxford nanopore validation; mutational processes	單細胞DNA; 單倍型特異拷貝數; 卵巢癌; 三陰性乳癌; 平行演化; 長讀驗證	scDNA total-CN 建細胞樹；ONT 只驗證 SV。	ONT 不進入建樹，只做正交驗證，所以平台軸算短讀。材料混合細胞株、PDX 與病人組織。sitka 樹是推論結果，不是獨立真值。	tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022	tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/README.md	
R01	C3a	c3a_patient_sc_reference	reference_tree	McPherson 2016: Divergent modes of clonal spread and intraperitoneal mixing in high-grade serous ovarian cancer	2016	reference_truth_source	human_patient	short_or_unspecified	Illumina HiSeq WGS; targeted amplicon MiSeq; single-nucleus targeted PCR	none		patient_scdna_reference_tree	single-nucleus targeted PCR (Fluidigm Access Array, MiSeq); SCG genotyper	true	clone_tree; sample_tree	phyclone_truth_source; mutation_loss; multi_region; roth_lab	high-grade serous ovarian cancer; single-nucleus sequencing; targeted deep sequencing; scg; pyclone; stochastic dollo; infinite sites with loss; multi-region wgs; clone tree; phyclone truth tree; intraperitoneal spread	卵巢癌; 單核定序; 真值樹; 多區域取樣; 突變流失	病人單核 PCR 建樹；是 PhyClone HGSOC 真值樹來源。	真值是模型樹（SCG、cluster 二值化、bulk 加權 stochastic Dollo、人工標記），不完全獨立於 bulk。7 位病人中只有 3 位有單核資料。	tumor_phylogeny_2026/references/R01_mcpherson_hgsoc_2016	tumor_phylogeny_2026/references/R01_mcpherson_hgsoc_2016/README.md	
```
### research/terminology/corpus.tsv
```
source	unit	family	kind	lines	sha256
research/phyclone_research/notes/00_SOURCE_MAP.md	PC	PhyClone	research-note	117	79dbbf2fb664da978b20a85867e92e7f6c96d89fc7aa9cb47e98b45f3e3e95ff
research/phyclone_research/notes/01_PAPER_BIG_PICTURE.md	PC	PhyClone	research-note	84	41f6cba6092eda705988e70bcc899d4037896d7beaed31e9d23ff2045f2fb37d
research/phyclone_research/notes/02_METHODS_DEEP_DIVE.md	PC	PhyClone	research-note	238	f5b63b83f6f333e1b8c7c3705940c2ea55f4adca94bb3a908ddb4eca3dc0dc6e
research/phyclone_research/notes/03_EXPERIMENTS_RESULTS.md	PC	PhyClone	research-note	161	1d4198e5a3788877af9361ed4e2e2146c8dba92163d8b45ee16e0bf1f059fb16
research/phyclone_research/notes/04_CODE_MAPPING.md	PC	PhyClone	research-note	64	cfc0b18f53b1a68bf7374775886a44667f6b26ce334f70f1624bda652d2f8a75
research/phyclone_research/notes/05_EVIDENCE_MATRIX.md	PC	PhyClone	research-note	50	3081c5dffe9c664fc8b423fc15423382f1a2298582ab2aec366c138e3a9746a8
research/phyclone_research/notes/06_ASSUMPTIONS_LIMITATIONS.md	PC	PhyClone	research-note	89	c0bd1b7b3360cb5b1e7387c08c076962099a5e9f6152afa0834b387a9091cea5
research/phyclone_research/notes/07_PRESENTATION_BRIEF.md	PC	PhyClone	research-note	117	b7f388a1abccbbb876cb0031f5a64e9818f2e4384c0234ab9a79889b37db5403
research/phyclone_research/notes/zh-TW/00_SOURCE_MAP.md	PC	PhyClone	research-note	116	d8988b5a1db5b2e11140ae6b1b9c3cec1a1cf280722c76677446de067b9fb208
research/phyclone_research/notes/zh-TW/01_PAPER_BIG_PICTURE.md	PC	PhyClone	research-note	83	4887cd8b0516508e7b20b980af618710853fff290c5f8a3668c8705d50635809
research/phyclone_research/notes/zh-TW/02_METHODS_DEEP_DIVE.md	PC	PhyClone	research-note	237	405c878b217fb8080552677f2ea648f59dd078dd5584a802ed25b4f2621c3b52
research/phyclone_research/notes/zh-TW/03_EXPERIMENTS_RESULTS.md	PC	PhyClone	research-note	161	58fbb30d06ae34410c214190cca1dadd02f75b0fe56e325d71426b2eb6df62ec
research/phyclone_research/notes/zh-TW/04_CODE_MAPPING.md	PC	PhyClone	research-note	64	bc7e08248beed9c49422219ed776e3bf47555cdbfb5adeb84cdc57fcb7ee39a7
research/phyclone_research/notes/zh-TW/05_EVIDENCE_MATRIX.md	PC	PhyClone	research-note	50	12ab12186697edfa4891bb49332798081ef5bdf82d898a631736e6026f89e91c
```
### research/terminology/evidence.tsv
```
id	unit	family	source	line	matched	excerpt	source_kind	status	role
T001	A02	Survey2026	research/tumor_phylogeny_2026/papers/A02_sprinter_2025/paper.txt	508	tumor phylogen	plicability of DLP+ metastatic migration patterns48. We reconstructed the tumor phylogeny	paper-text	current	lexical-occurrence
T001	A03	Survey2026	research/tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md	15	clone phylogen	CG）的 multilayer/multistate clustering 分成 7 群。Fig.6b 再將 cluster-defining SNV/CNV events 排成 clone phylogeny，呈現 driver SNV、廣泛 CN 及逐步 focal deletion 的關係。8 個 amplicons 代表該 panel 覆蓋區域，不能推成完整無缺口的整個 gene/genome 刪除真值。	paper-note	current	lexical-occurrence
T001	B01	Survey2026	research/tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt	149	tumor phylogen	While the tumor phylogeny described above accurately reﬂects the (Supplementary Table S4). Proportionally, SVs were distributed simi-	paper-text	current	lexical-occurrence
T001	B03	Survey2026	research/tumor_phylogeny_2026/papers/B03_singlecell_mutational_processes_2022/paper.txt	1825	Cancer phylogen	 37. Salehi, S. et al. Cancer phylogenetic tree inference at scale from 1000s of single cell	paper-text	current	lexical-occurrence
T001	B05	Survey2026	research/tumor_phylogeny_2026/papers/B05_medicc2_2022/paper.txt	124	cancer phylogen	 Fig. 1 MEDICC2 algorithm. a MEDICC2 infers cancer phylogenies from SCNA data from single cells or	paper-text	current	lexical-occurrence
T001	B07	Survey2026	research/tumor_phylogeny_2026/papers/B07_numbat_2022/paper.txt	267	tumor phylogen	 tumor phylogeny can be inferred 24,25. To perform joint inference of single-cell CNV profiles and	paper-text	current	lexical-occurrence
T001	HCC	HCC1395	research/hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md	1	腫瘤演化樹	# 02. 腫瘤演化樹如何重建	research-note	current	lexical-occurrence
T001	PC	PhyClone	research/phyclone_research/notes/01_PAPER_BIG_PICTURE.md	5	clone phylogen	om one or more related bulk-tumour samples and jointly infers mutation clusters and their clone phylogeny, using an FS-CRP prior, a collapsed prevalence likelihood, Particle-Gibbs SMC, and an outlier state for mutations incompatible with tree inheritance. (Main Ab	research-note	current	lexical-occurrence
T001	SYN	Synthesis	research/tumor_phylogeny_2026/README.md	1	腫瘤演化樹	# 腫瘤演化樹文獻調查：single cell × long read × haplotype	cross-study-synthesis	current	lexical-occurrence
T002	A01	Survey2026	research/tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/README.md	9	克隆	第一類 A：直接取自高級別漿液性卵巢癌（HGSOC）病人的 single-cell whole-genome DNA 資料，建立 genetic phylogeny，再追蹤治療中的克隆比例。24 名病人提供 21,916 顆 tumor cells（每人 232–2,094 顆）；摘要的 **18 名**是主要多年縱向追蹤分析人數，不能和整體 scWGS cohort 混寫。不是 RNA-only 推樹，也不是 cell line。這篇未使用 ONT/PacBio 長讀或 linked reads 	paper-note	current	lexical-occurrence
T002	A02	Survey2026	research/tumor_phylogeny_2026/papers/A02_sprinter_2025/README.md	3	clones	 et al. **Characterizing the evolutionary dynamics of cancer proliferation in single-cell clones with SPRINTER.** *Nature Genetics* **57**, 103–114 (2025). DOI: [10.1038/s41588-024-01989-z](https://doi.org/10.1038/s41588-024-01989-z)。2024-11-29 online，2025	paper-note	current	lexical-occurrence
T002	A03	Survey2026	research/tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023/README.md	9	clone	plicons/93 genes 的 **DNA panel**，不是 scRNA 推 CNV。matched bulk WES/WGS 用來驗證重要 variants。主要完整 clone tree 是 **PA04 一名病人**的 3 個區域樣本，不能聲稱 16 名病人都建立了全基因組高解析演化樹。沒有 long-read 或 linked-read 推樹。	paper-note	current	lexical-occurrence
T002	A04	Survey2026	research/tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/README.md	17	clone	以 Bayesian segment genotype likelihood 判斷 SV，後續人工檢查。細胞依共享 SV 分群；通常至少 3 個 cells 共享一組 SV 才定 clone，但對清楚的 progeny 可接受更少 cells。Fig.2 的 clone hierarchy 是**人工整理的樹**，不是一個經外部真值驗證的自動推樹器。	paper-note	current	lexical-occurrence
T002	A05	Survey2026	research/tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/README.md	9	clones	leukemia genes，識別 27 個 pathogenic/likely pathogenic mutations 與 36 個 genetically distinct clones。沒有 long reads/linked reads，亦不是 RNA-only 推樹。	paper-note	current	lexical-occurrence
```
### research/terminology/terms.tsv
```
id	category	zh	en	abbreviation	definition	aliases	boundary	definition_status	scope	study_count	studies	family_count	pattern
T001	演化與樹	腫瘤演化樹	tumor phylogeny		描述腫瘤細胞群之祖先關係的樹狀模型。它由資料與假設推得。	tumour phylogeny; tumor evolutionary tree; clone phylogeny	敘述特定結果時，另寫明節點代表細胞、克隆、突變或樣本。	inferred	shared	8	A02,A03,B01,B03,B05,B07,HCC,PC	3	tumou?r phylogen|腫瘤演化樹|clonal evolution tree|cancer phylogen|clone phylogen
T002	演化與樹	克隆	clone		本研究解析度下，共享特定遺傳歷史的細胞群。	clonal population; 克隆群	不要把統計群集或單倍型直接稱為克隆。	inferred	shared	13	A01,A02,A03,A04,A05,B01,B03,B04,B05,B07,HCC,PC,PW	3	\bclones?\b|克隆
T003	演化與樹	亞克隆	subclone		腫瘤內可由遺傳差異區分的克隆群。	subclonal population	指出相對的祖先或比較範圍；低 VAF 本身不能證明亞克隆。	inferred	shared	13	A01,A02,A03,A04,A05,B01,B03,B04,B05,B07,HCC,PC,PW	3	\bsubclon(?:e|es|al)\b|亞克隆
T004	演化與樹	克隆演化	clonal evolution		細胞群隨時間累積遺傳改變，形成不同克隆的過程。	clonal evolutionary history	克隆比例變動不一定代表新增遺傳事件。	inferred	shared	8	A01,A02,A03,A04,A05,B01,B07,HCC	2	clonal evolution|克隆演化
T005	演化與樹	腫瘤內異質性	intratumor heterogeneity	ITH	同一腫瘤內，細胞或細胞群之間存在的差異。	intratumoral heterogeneity; intra-tumour heterogeneity	標明差異屬於基因型、拷貝數、表觀遺傳或表型。	inferred	shared	7	A03,A04,B01,B03,B05,B07,HCC	2	intratumou?ral? heterogeneity|intra.tumou?r heterogeneity|\bITH\b|異質性
T006	演化與樹	克隆樹	clone tree		以克隆為節點，表示克隆祖先關係的樹。	clonal tree; clone phylogeny	不要與樣本樹、細胞樹或突變樹互換。	inferred	shared	5	A02,A03,A04,B03,B07	1	clone tree|clonal tree|clonal phylogen|克隆樹
T007	演化與樹	細胞樹	cell tree		以個別細胞為觀測末端，表示推定親緣關係的樹。	cell phylogeny; single-cell phylogeny	細胞的相似度分群圖不會自動成為細胞演化樹。	inferred	shared	6	A01,A02,A03,B03,B05,B07	1	cell tree|cell phylogen|single.cell phylogen|細胞樹
T008	演化與樹	樣本樹	sample tree		以樣本為觀測末端，表示樣本間關係的樹。	sample phylogeny	同一樣本可能含多個克隆；樣本樹不直接給出克隆樹。	inferred	supporting	0		0	sample tree|sample phylogen|樣本樹
T009	演化與樹	突變樹	mutation tree		以突變事件為節點，表示事件先後或祖先關係的樹。	event tree	部分方法將共同發生的突變置於同一節點，須另行說明。	inferred	shared	2	A05,B05	1	mutation tree|event tree|突變樹
T010	演化與樹	樹拓樸	tree topology		樹的節點連接方式與祖先關係。	topology; tree structure; 拓撲	統一寫「拓樸」；拓樸本身不包含分支長度或細胞比例。	inferred	shared	11	A01,A02,A03,B01,B03,B04,B05,B07,HCC,PC,PW	3	topolog|拓樸|拓撲
T011	演化與樹	節點	node		樹中代表指定生物單位或事件的元素。	vertex	先寫明節點代表什麼；虛擬根節點不一定代表真實細胞。	inferred	shared	9	A01,A02,B01,B03,B05,B07,HCC,PC,PW	3	\bnodes?\b|節點
T012	演化與樹	邊	edge		連接兩個節點的關係。	tree edge	有根演化樹的邊有祖先方向；邊的存在不表示已有直接實驗驗證。	inferred	shared	5	A01,A02,B07,HCC,PC	3	\bedges?\b|tree edge|逐邊
T013	演化與樹	根節點	root node		指定有根樹之祖先方向的起點。	root	區分正常細胞根、腫瘤祖先根與計算用虛擬根。	inferred	shared	2	B01,PC	2	root node|rooted tree|根節點|虛擬根
T014	演化與樹	子樹	subtree		由一個節點及其所含後代構成的樹。	descendant subtree	計算 CCF 時，說明是否包含子樹內的所有後代。	inferred	shared	2	B01,PC	2	\bsubtrees?\b|子樹
```
### research/tumor_phylogeny_2026/manifest.tsv
```
id	selection	doi	file	version	source_url	pages	bytes	sha256
A01	A_core	10.1038/s41586-025-09580-0	papers/A01_ovarian_cfDNA_2025/paper.pdf	published	https://www.nature.com/articles/s41586-025-09580-0.pdf	30	43664316	6f610ce0e553751e56036830923d0bb8becf8a759cd333f043f6113263bc4b13
A02	A_core	10.1038/s41588-024-01989-z	papers/A02_sprinter_2025/paper.pdf	published	https://www.nature.com/articles/s41588-024-01989-z.pdf	34	17981707	8bf2a203efc1375eb22f25ab8d4bc4beaa52cff711700119a16cb51e93dea152
A03	A_core	10.1038/s41467-023-36344-z	papers/A03_pancreatic_snDNA_2023/paper.pdf	published	https://www.nature.com/articles/s41467-023-36344-z.pdf	14	3367020	1607997a06a29b67e8be78c93e18838b24d367082a0b17abaa8217ddbca19f0c
A04	A_core	10.1038/s41588-024-01999-x	papers/A04_aml_strandseq_2024/paper.pdf	published	https://www.nature.com/articles/s41588-024-01999-x.pdf	39	15925353	9a040a76357a1e0b573dc9c2e4fdc96659cc45336884bccb001a9f04178508bc
A05	A_core	10.1038/s41467-024-52317-2	papers/A05_mpal_multiome_2024/paper.pdf	published	https://www.nature.com/articles/s41467-024-52317-2.pdf	17	4800782	77786c0dc2f63a13ae97eb66695781047840207adaa70f40dd60ea9439016fd4
B01	B_core	10.1038/s41467-026-75172-9	papers/B01_melanoma_longread_2026/paper.pdf	published	https://www.nature.com/articles/s41467-026-75172-9.pdf	21	5028596	8811bc50ebff622b1b3663f9b25e9a749e818488a7510fb67a49187557ceb475
B03	bridge	10.1038/s41586-022-05249-0	papers/B03_singlecell_mutational_processes_2022/paper.pdf	published	https://www.nature.com/articles/s41586-022-05249-0.pdf	30	46233326	eb6086d36613473f256502e2fdfc6655525620f5601e03cf72cce79bf0f1d6bb
B04	B_core	10.1038/s41467-022-31133-6	papers/B04_lung_longread_phasing_2022/paper.pdf	published	https://www.nature.com/articles/s41467-022-31133-6.pdf	17	3695682	e13aa7957455432171cf39edd4fee9c09ad257d4f53328d9b48e58fddcd12e21
B04	B_core	10.1038/s41467-022-31133-6	papers/B04_lung_longread_phasing_2022/supplement.pdf	supplement	see paper README	58	11757184	d30f94ed901c5f886dd89d50ea264866c5b221498610c43effa51dc807e053de
B05	method_comparator	10.1186/s13059-022-02794-9	papers/B05_medicc2_2022/paper.pdf	published_corrected_2023	https://genomebiology.biomedcentral.com/counter/pdf/10.1186/s13059-022-02794-9	27	4413650	1dc022bbb36f2050f50ddbdd89bcf2464f32063079385890ae80cbe1b1ab9089
B07	B_core	10.1038/s41587-022-01468-y	papers/B07_numbat_2022/paper.pdf	biorxiv_v1_2022-02-10; formal published HTML cross-checked	https://www.biorxiv.org/content/10.1101/2022.02.07.479314v1.full.pdf	40	38204002	b2edf784a9d2f5c435e072e32afa8ed7188cb95ac810d7bb58df9f4cbde4a9e3
```

## 追蹤清單當天的改動（CLAUDE.md evaluation_v1.md research/INDEX.md research/CONTEXT.md research/phyclone_research/RESEARCH_PLAN.md research/phyclone_research/notes/ report/report_rule.md）

```diff
commit 91826b9938c53631f7847a67a65a8a5fddc27f5f
Author: paulboul1013 <paulboul1013@gmail.com>
Date:   Mon Oct 19 19:01:55 2026 +0800

    docs(report): add report rules, global visual spec, and 10-21 deck
    
    - report_rule.md: personal slide rules (outline review, structure,
      text, script, figures, fixed HP palette).
    - VISUAL_SPEC.md: global spec for common biology diagrams,
      extracted from the 10-21 deck's VISUALS.md.
    - 2026_10_21_slides/: outline, BRIEF, visuals, and slides.
    - Remove the old sc_groundtruth_slides draft and loose PNGs.
    - CLAUDE.md: read and update report_rule.md before slide work.
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/CLAUDE.md b/CLAUDE.md
index b0e237c..5e40205 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -49,4 +49,5 @@ python -m unittest phyclone.tests.unit_tests.test_tree.<Class>.<method>
 - 文件以**繁體中文**撰寫，技術名詞（SNV、CCF、multiplicity、topology、purity、ESS 等）保留英文。
 - 製作 PPT／投影片時，原始檔一律輸出到 `report/<簡報名稱>/`（例如 `report/sc_groundtruth_slides/`），不要放在 `research/` 或暫存目錄。
+- 收到任何製作或修改 PPT／投影片報告的指令時，先把該指令併入 `report/report_rule.md` 的「個人風格」對應區塊，再動手。製作前先讀這份規則檔並遵守。
 - 做研究 claim 時，要區分 nominal purity 與實測 purity，也要區分論文主張與程式實際行為，並標明證據來源。
 - 回答時採用 **ASD-STE100（Simplified Technical English）** 風格：一句只說一件事、句子短（說明句約 25 字詞內、指令句約 20 字詞內）、用主動語態、一個詞只用一個意思、指令用祈使句、先寫結論或動作再寫原因。中文回答也套用相同原則；技術名詞照上方規則保留英文。
diff --git a/report/report_rule.md b/report/report_rule.md
new file mode 100644
index 0000000..2e0426a
--- /dev/null
+++ b/report/report_rule.md
@@ -0,0 +1,116 @@
+# 報告與投影片規則
+
+本檔記錄使用者對 PPT／投影片報告的個人風格。收到新的報告指令時，把它併入下方對應區塊。
+
+## 規則效力
+
+- 標為 **【必要】** 的條文一定要做。當次指令不能取消。
+- 其餘條文是預設做法，不是死板格式。當次指令與預設衝突時，以當次指令為準。
+- 條文寫「可以」的是選用。
+
+## 個人風格
+
+### 製作流程
+
+1. **【必要】大綱審查（動手製作前一定要做）。** 收到使用者的大綱後，同時開兩個 subagent，各扮演一個角色審查大綱：
+   - **邏輯漏洞審查者**：找故事邏輯的缺口、跳躍、矛盾，以及提出後沒有回答的問題。
+   - **生物資訊教授**：檢查生物與演算法內容是否正確，術語是否用對，論證是否站得住。
+
+   規則：
+   - 兩位都要看完整大綱，並各自給出建議。
+   - 整合兩位的意見，寫成一份審查摘要，交給製作報告的 subagent。
+   - 大綱要通過兩位的建議才能開始製作。有角色提出的問題沒有解決時，先修改大綱補救，再審查一次。修改大綱時遵守「結構與內容」第 1 條。
+   - 審查先看故事主軸：整份大綱要有一個主問題，每段都要推進這個主問題。段落之間只是並列、和主問題無關時，判為發散。
+2. **【必要】** 大綱邏輯先和使用者確認通過，才可以修改或製作報告。
+3. 把投影片原始檔輸出到 `report/<簡報名稱>/`。不要放在 `research/` 或暫存目錄。
+4. 用 `/slides`（claude.ai Slides artifact type）製作最終成品。
+5. 每一個大綱段落用一個 subagent 製作。該 subagent 負責這個段落的全部頁面。不要每一頁各開一個 subagent。另開一個 subagent review 內容與排版。
+   - 交給 subagent 的是檔案路徑（大綱、審查摘要、`BRIEF.md`），不要貼全文。subagent 只回摘要與檔案位置。
+   - review 排版時，看渲染出來的縮圖，不要把整份原始碼讀進 context。
+6. 全部段落完成後，另開一個 subagent 檢查整份報告的故事邏輯。檢查項目：
+   - 每個概念在使用前已經解釋過。
+   - 前一頁的結論能接到下一頁的問題。
+   - 前面提出的問題，後面有回答。
+   - 總結沒有出現前面沒講過的新內容。
+   - 頁與頁之間沒有重複或互相矛盾。
+   - 同一概念全冊用同一個名稱、顏色、圖示（見「圖」第 4 條）。
+   - 假想的例子與數值沒有被讀成實測。
+   依檢查結果修改後，才算完成。
+7. 修改既有報告的範圍：
+   - 一般修改只動被指到的頁，不重跑整個流程。
+   - 要求「嚴格重新修改」時，從第 1 步重跑完整流程。逐頁對照本規則檢查，違反的地方全部改掉，不要只修局部。
+
+### 結構與內容
+
+1. 以使用者給的大綱為主軸。不要改動大綱的順序與標題意思。需要改動時，先問使用者，不要自行改動。
+2. 頁數控制：
+   - 每個大綱段落放 1–2 頁，以減少製作 token。
+   - 大綱的邏輯有缺口時，自行加頁補足。把加的頁放在大綱對應段落內。
+   - 文字放不下時，先依「文字與表格」第 8 條刪字。刪字後仍放不下才拆頁，該段落仍盡量不超過 2 頁。
+3. 每頁只講重點。內容要簡單。
+4. 議程頁只用一種分法說明接下來的內容（例如三個子問題）。不要再用第二種分法（例如五段順序條）重講一次。卡片上也不要標段落編號。
+5. 內容主要取自近期的建樹研究 session 與 repo 文件。
+6. 區分論文主張、程式實際行為與分析推論。
+7. 區分 nominal purity 與實測 purity。
+8. 標題可以寫成這頁的結論，一句話內講完，不寫成主題名。
+9. 數字附單位。量測方式記在 `BRIEF.md`。
+10. `BRIEF.md` 記錄：
+    - 來源（建代號表，只列一次）。
+    - 哪些例子與數值是假想的。
+    - 數字怎麼量的。
+    - 哪些是論文主張／程式行為／分析推論。
+    - 每頁圖的草圖（見「圖」第 1 條）。
+
+### 文字與表格
+
+1. 文字用 ASD-STE100 風格。少用長段文字。
+2. 有或無的欄位只寫「有」或「無」。不要加「部分強」之類的修飾，也不要加旁邊小字。
+3. 定序平台欄位寫「長讀」或「短讀」，再寫有無 BAM 可下載。
+4. 判斷論文有無 single-cell ground-truth 演化樹時，以 PhyClone 的 sc 演化樹為標準。
+5. 不要用觀眾不懂的黑話。黑話包括內部代號（C1、B04、M03、K10、F1、C0、Phase 0）、未解釋的縮寫（PS、CP、AD、sc3、1A）、工具名（Battenberg、MuTect）與程式欄位名（tumour_content、major_cn）。必要的術語在第一次出現時，用圖或一句白話解釋。
+6. 頁面文字和圖一一對應：
+   - 每個重點文字都要有對應的圖。
+   - 頁面文字只描述當頁示意圖呈現的事實。圖沒有畫出的內容不要寫在頁面上。
+7. 補充說明、限制、但書與推論細節放進講稿，不要顯示在頁面上。
+8. 文字太小看不清時，先刪字，不要縮小字級。刪字後仍放不下，依「結構與內容」第 2 條處理。
+9. 圖中文字只放名詞或短語，整句放講稿。
+
+### 講稿
+
+1. 講稿只講重點。先講這頁的結論，再沿著圖講原因。
+2. 每頁講稿控制在約一分鐘，中文約 200–250 字。
+3. 用口語寫，要能直接念出來。可以用「我們」「大家看這裡」這類說法。
+4. 黑話規則同「文字與表格」第 5 條。
+5. 不要在講稿放 repo 路徑、章節編號或內部代號。來源記錄放在該簡報的 `BRIEF.md`。
+6. 講稿叫觀眾看某個圖元素後，接著只講該元素上看得到的東西。用它的位置、顏色與上面的字指路（例如「左邊藍色這張」）。不要改用另一個元素的編號（例如看卡片時講「第一段到第五段」）。要講另一個元素時，先明確把觀眾的視線移過去（例如「再看最下面這條」）。
+7. 頁與頁之間的橋接：
+   - 段落之間必須橋接，不要從上一段的結論直接跳到新主題。上一頁結尾先用一句話說明下一段為什麼和這頁有關（例如「長讀為什麼可能補上這兩個陷阱」），再提問。下一頁開頭的結論要直接回答這個問題。
+   - 同一段落內的頁可以用一句話接到下一頁的問題。接不自然就不寫。
+8. 講到假想例子或推論時，用口語說清楚，例如「舉個例子」「這是我們的推論，論文沒有這樣寫」。
+9. 同一個但書全冊只講一次，放在第一次需要的那頁，後面不重複。
+
+### 圖
+
+1. 畫圖順序：
+   1. 先查 `report/VISUAL_SPEC.md`（全域生物示意圖規格）。概念已在該檔時，照它的構圖與易錯點畫。
+   2. 該檔沒有的概念，開一個 subagent 搜尋該概念的精確描述與參考示意圖。多份簡報都會用到時，把結果加進 `VISUAL_SPEC.md`。
+   3. 在 `BRIEF.md` 用 ASCII 或幾行文字畫草圖：誰和誰比、哪裡沒有、結論是什麼。
+   4. 結構確認後才畫細節。
+2. 優先畫簡易示意圖，不要整頁都是文字。用生物基因參考示意圖呈現概念，例如染色體、haplotype、read、SNV、clone tree。
+3. 舊 PPT 的圖只作參考。不要整批複製貼上舊圖。
+4. 同一概念全冊同色同圖示，不要中途更換。haplotype read 用下列固定配色區分：
+
+   | 類別 | 顏色 |
+   |---|---|
+   | HP1 | `#2C5F9E` |
+   | HP1-1（HP1 上帶 SNV） | `#8FB3E0` |
+   | HP2 | `#D9772B` |
+   | HP2-1（HP2 上帶 SNV） | `#F2B880` |
+   | somatic SNV | `#D23A2E` |
+   | unphased | `#9AA3AE` |
+
+5. 對照圖：
+   - 兩個東西要比較時，可以用左右兩欄：左邊放基準，右邊放新做法，同一列放同一件事。例如預設做法對新方法、論文主張對實際行為、nominal purity 對實測 purity。單一概念不用硬湊對照，直接畫一張圖。
+   - 基準那側沒有的東西用斜線底表示。
+   - 結果用 ✓／✗ 加文字，不只靠顏色。
+6. 回饋或人工介入的箭頭用虛線，主流程用實線。

commit 65d54d90c3b3f473041b372a26a97b51f7c902c0
diff --git a/report/report_rule.md b/report/report_rule.md
index 2e0426a..baa4e46 100644
--- a/report/report_rule.md
+++ b/report/report_rule.md
@@ -62,4 +62,21 @@
     - 每頁圖的草圖（見「圖」第 1 條）。
 
+11. 主軸以使用者指定的主題為準。擬大綱前，先用一句話寫出主問題，對照使用者的原話。大綱內容偏離該主題時，刪掉偏離的段落，不要保留。
+
+### 各簡報主軸
+
+- **2026-10-21 報告**（2026-10-19 指定）：只分兩大段。
+  1. 文獻調查：有沒有研究同時用 single-cell 定序建立真值樹來驗證，並用 long read、haplotype、phase set 等特徵重建演化樹。
+  2. 各論文的模擬資料與真實資料怎麼產生，作為我們做驗證資料的參考。
+  - 整份不放小鼠子株長讀研究（Liu 2026）。
+  - 收錄標準：論文至少要用一個建樹工具（現成軟體或自己的演算法）。只做 VAF 分群、畫圖（例如 Fishplot）或人工整理的樹不算。用現成工具也算，例如 ScisTree、ClonEvol。
+  - 依上述標準，整份不放：HPV 整合長讀研究（Akagi 2023）、骨髓瘤 linked-read 研究（Liu 2021）。
+  - 整份不放肝癌多點長讀研究（Zeng 2025）。它用 neighbor-joining 建樣本樹，但使用者決定不收。
+  - 整份不放肺癌細胞株長讀摘要（Donmez 2026，AACR 摘要）。
+  - 篇數以去掉上述論文之後的 17 篇計算。
+  - 不放我們自己的 6 株 ONT 細胞株。
+  - 已發表論文的細胞株資料（HCC1395 社群資料）可以列，因為它們是論文資料，不是我們的對照。
+  - 全冊用「長讀」，不用「long read」（封面標題也是）。
+
 ### 文字與表格
 
@@ -68,5 +85,5 @@
 3. 定序平台欄位寫「長讀」或「短讀」，再寫有無 BAM 可下載。
 4. 判斷論文有無 single-cell ground-truth 演化樹時，以 PhyClone 的 sc 演化樹為標準。
-5. 不要用觀眾不懂的黑話。黑話包括內部代號（C1、B04、M03、K10、F1、C0、Phase 0）、未解釋的縮寫（PS、CP、AD、sc3、1A）、工具名（Battenberg、MuTect）與程式欄位名（tumour_content、major_cn）。必要的術語在第一次出現時，用圖或一句白話解釋。
+5. 不要用觀眾不懂的黑話。黑話包括內部代號（C1、B04、K10、F1、C0、Phase 0）、未解釋的縮寫（PS、CP、AD、sc3、1A）、工具名（Battenberg、MuTect）與程式欄位名（tumour_content、major_cn）。必要的術語在第一次出現時，用圖或一句白話解釋。
 6. 頁面文字和圖一一對應：
    - 每個重點文字都要有對應的圖。
diff --git a/research/CONTEXT.md b/research/CONTEXT.md
index 1d66877..8d49fbd 100644
--- a/research/CONTEXT.md
+++ b/research/CONTEXT.md
@@ -71,5 +71,5 @@ _原文定位_：[A01 L15](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/RE
 _別名與對照_：sample phylogeny。
 _用詞界線_：同一樣本可能含多個克隆；樣本樹不直接給出克隆樹。
-_原文定位_：[B06 L1](tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/README.md)。
+_原文定位_：本次語料沒有原文定位。
 
 **T009 突變樹（mutation tree）**
@@ -199,5 +199,5 @@ _原文定位_：[HCC L31](hcc1395_golden_tree_research/hcc1395_tumor_evolution_
 _別名與對照_：clone expansion。
 _用詞界線_：說明是絕對數量增加或相對比例增加。
-_原文定位_：[B02 L27](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/README.md)；[B01 L1053](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。
+_原文定位_：[B01 L1053](tumor_phylogeny_2026/papers/B01_melanoma_longread_2026/paper.txt)。
 
 **T127 葉節點（leaf node）**
@@ -629,5 +629,5 @@ _用詞界線_：計算 switch error rate 時，寫明可評估的相鄰位點
 _原文定位_：[B05 L43](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.md)；[B04 L183](tumor_phylogeny_2026/papers/B04_lung_longread_phasing_2022/paper.txt)。
 
-**T053 分子連鎖（molecular linkage）**
+**T053 分子連鎖（molecular linkage）**〔支援詞〕
 
 變異由同一分子來源的觀測連接起來的證據。
@@ -635,5 +635,5 @@ _原文定位_：[B05 L43](tumor_phylogeny_2026/papers/B05_medicc2_2022/README.m
 _別名與對照_：read-level linkage; long-range linkage。
 _用詞界線_：區分實測同一長讀段與條碼重建的長分子來源。
-_原文定位_：[PW L145](hcc1395_golden_tree_research/phylowgs_model_review.md)；[B06 L43](tumor_phylogeny_2026/papers/B06_hcc_multisite_longread_2025/README.md)。
+_原文定位_：[PW L145](hcc1395_golden_tree_research/phylowgs_model_review.md)。
 
 **T054 同一分子共現（same-molecule co-occurrence）**
@@ -1007,5 +1007,5 @@ _原文定位_：[A04 L9](tumor_phylogeny_2026/papers/A04_aml_strandseq_2024/REA
 _別名與對照_：transcript abundance。
 _用詞界線_：RNA 表現量不同不直接表示 DNA 拷貝數或基因型不同。
-_原文定位_：[B02 L21](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/README.md)；[A01 L1617](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。
+_原文定位_：[A01 L1617](tumor_phylogeny_2026/papers/A01_ovarian_cfDNA_2025/paper.txt)。
 
 **T152 表觀遺傳狀態（epigenetic state）**
@@ -1079,5 +1079,5 @@ _原文定位_：[A03 L27](tumor_phylogeny_2026/papers/A03_pancreatic_snDNA_2023
 _別名與對照_：molecular identifier。
 _用詞界線_：UMI 不等於細胞條碼；錯誤與碰撞的處理依分析流程而定。
-_原文定位_：[A05 L602](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/paper.txt)；[B02 L1020](tumor_phylogeny_2026/papers/B02_myeloma_linkedread_2021/paper.txt)。
+_原文定位_：[A05 L602](tumor_phylogeny_2026/papers/A05_mpal_multiome_2024/paper.txt)。
 
 **T187 細胞狀態（cell state）**
```
