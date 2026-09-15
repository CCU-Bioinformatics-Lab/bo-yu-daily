# XLSX Analyst Report

Analysed workbooks (read-only):

1. `Experiment_Performance_Metrics.xlsx`
2. `Experiment_Friedman_Nemenyi_Tests.xlsx`
3. `Experiment_Posterior_Metrics.xlsx`

All three contain only visible worksheets, no merged cells, and no formulas. Cell ranges below include the header row. Numeric reconstructions are arithmetic means over nonblank raw cells unless stated otherwise; failed rows generally contain blank result fields and are excluded from the corresponding mean.

## Workbook schema

### `Experiment_Performance_Metrics.xlsx`

| Sheets | Range | Dataset/condition fields | Methods | Metrics/result fields | Replication |
|---|---:|---|---|---|---|
| S2 TSSB-Low | A1:L3001 | depth=1000; mutations=100; samples=2,4,8,16,128 | PhyClone, PhyloWGS, CONIPHER, fastBE, Orchard, Pairtree | V-measure, predicted/true mutation count, AD F-score, Success, memory, time | run; 100 rows per method × sample count (500/method) |
| S3 TSSB-High | A1:L2001 | depth=1000; mutations=10000; samples=2,4,8,16 | PhyClone, CONIPHER, fastBE, Orchard, Pairtree | same as S2 | run; 100 rows per method × sample count (400/method) |
| S4 FS-CRP Loss | A1:M601 | depth=1000; mutations=600; samples=8; mutation-loss proportion=0,0.1,0.2 | PhyClone, PhyClone-N | same plus `mut_loss_prop` | run; 100 rows per method × loss level (300/method) |
| S5 Pairtree | A1:M2881 | depth=50,200,1000; clusters=3,10,30,100; mutations=30–10000; samples=1,3,10,30,100 | PhyClone, CONIPHER, fastBE, Orchard, Pairtree | same as S2 | run=1–4; 576/method |
| S6 CONIPHER No-Noise | A1:J751 | `sim_name`; samples=2–11 | PhyClone, CONIPHER, fastBE, Orchard, Pairtree | V-measure, mutation counts, AD F-score, Success, memory, time | 150 simulations/method |
| S7 CONIPHER Noise | A1:J751 | `sim_name`; samples=2–13 | same five | same | 150 simulations/method |
| S8/S9 HGSOC p2 | A1:I6 each | WGS / WGS+Targeted; run=p2 | same five | V-measure, mutation counts, AD F-score, Success, memory, time | one result/method |
| S10/S11 HGSOC p3 | A1:I6 each | WGS / WGS+Targeted; run=p3 | same five | same | one result/method |
| S12/S13 HGSOC p9 | A1:I6 each | WGS / WGS+Targeted; run=p9 | same five | same | one result/method |
| S14 Copy Number Error | A1:J2251 | `sim_name`; samples=2–11; **no error-proportion column** | same five | same as S6 | 450 rows/method; apparently 3 × 150 simulations, but row-to-error-level mapping is unresolved |

Exact columns:

- S2/S3 `A:L`: program, depth, num_mutations, num_samples, run, v_measure, num_mutations_pred, num_mutations_true, ancestor_descendant_f_score, Success, memory, time.
- S4 `A:M`: adds `mut_loss_prop` before run.
- S5 `A:M`: program, depth, num_clusters, num_mutations, num_samples, run, then the same result fields.
- S6/S7/S14 `A:J`: program, sim_name, num_samples, v_measure, num_mutations_pred, num_mutations_true, ancestor_descendant_f_score, Success, memory, time.
- S8–S13 `A:I`: program, run, v_measure, num_mutations_pred, num_mutations_true, ancestor_descendant_f_score, Success, memory, time.

### `Experiment_Friedman_Nemenyi_Tests.xlsx`

| Sheet(s) | Range | Schema / role |
|---|---:|---|
| S15 TSSB-Low, Friedman | A1:C5 | metric, p_value, significant |
| S16 TSSB-Low, Nemenyi | A1:G61 | metric, prog_1, prog_2, p_value, mean_diff, better_performer_of_pair, significant |
| S17 TSSB-High, Friedman | A1:C5 | Friedman schema |
| S18 TSSB-High, Nemenyi | A1:G41 | Nemenyi schema |
| S19 FS-CRP Loss, Nemenyi | A1:F5 | Nemenyi schema **without `significant`** |
| S20 Pairtree, Friedman | A1:C5 | Friedman schema |
| S21 Pairtree, Nemenyi | A1:G41 | Nemenyi schema |
| S22 CONIPHER No-Noise, Friedman | A1:C5 | Friedman schema |
| S23 CONIPHER No-Noise, Nemenyi | A1:G41 | Nemenyi schema |
| S24 CONIPHER Noise, Friedman | A1:C5 | Friedman schema |
| S25 CONIPHER Noise, Nemenyi | A1:G41 | Nemenyi schema |
| S26 Copy Number Error, Friedman | A1:C5 | Friedman schema |
| S27 Copy Number Error, Nemenyi | A1:G41 | Nemenyi schema |

Metrics are AD F-score, V-measure, time, and memory. Every Friedman sheet reports a significant omnibus result for all four metrics; many p-values are stored as literal `0`, which should be read as numerical underflow/rounding, not mathematical proof of exactly zero.

### `Experiment_Posterior_Metrics.xlsx`

| Sheet | Range | Dataset fields | Methods | Metrics |
|---|---:|---|---|---|
| S28 Pairtree Posterior Metrics | A1:L2881 | depth, clusters, mutations, samples, run | same five non-PhyloWGS methods | relationship reconstruction error (RRE), number of RRE trees, perplexity, number of perplexity trees, truth perplexity, log perplexity ratio (LPR) |
| S29 Pairtree Posterior Friedman | A1:C3 | metric | — | omnibus p/significance for RRE/LPR |
| S30 Pairtree Posterior Nemenyi | A1:G21 | method pair | five methods | pairwise RRE/LPR |
| S31 TSSB-Low Posterior Metrics | A1:K2501 | depth=1000, mutations=100, samples=2,4,8,16,128, run | same five | same, except no cluster-count field |
| S32 TSSB-Low Posterior Friedman | A1:C3 | metric | — | omnibus RRE/LPR |
| S33 TSSB-Low Posterior Nemenyi | A1:G21 | method pair | five methods | pairwise RRE/LPR |
| S34 TSSB-High Posterior Metrics | A1:K2001 | depth=1000, mutations=10000, samples=2,4,8,16, run | same five | same |
| S35 TSSB-High Post. Friedman | A1:C3 | metric | — | omnibus RRE/LPR |
| S36 TSSB-High Posterior Nemenyi | A1:G21 | method pair | five methods | pairwise RRE/LPR |

Raw sheet sizes imply 576, 500, and 400 rows per method in S28, S31, and S34, matching their corresponding performance sheets after excluding PhyloWGS from TSSB-Low posterior analysis.

## Reconstructed key results

### Accuracy and resource means

[INFERRED] These means are reconstructed directly from all available nonblank raw cells; the workbooks do not provide aggregate formulas.

| Dataset (raw range) | Method | n / successes | mean V | mean AD F | mean time | mean memory |
|---|---|---:|---:|---:|---:|---:|
| TSSB-Low (S2!A2:L3001) | PhyClone | 500/500 | 0.99496 | **0.98350** | 253.26 | 1101.13 |
|  | Orchard | 500/500 | 0.99321 | 0.97981 | 7.98 | 150.48 |
|  | Pairtree | 500/500 | 0.99321 | 0.97622 | 100.68 | 1114.43 |
|  | fastBE | 500/500 | 0.99321 | 0.90144 | 3.33 | 45.76 |
|  | CONIPHER | 500/473 | 0.99140 | 0.88251 | 55.05 | 129.10 |
|  | PhyloWGS | 500/476 | 0.81468 | 0.90456 | 37562.9 | 258.63 |
| TSSB-High (S3!A2:L2001) | PhyClone | 400/400 | 0.94806 | **0.96092** | 539.99 | 1261.31 |
|  | Pairtree | 400/400 | 0.94464 | 0.96039 | 173.92 | 1176.12 |
|  | Orchard | 400/400 | 0.94464 | 0.95979 | 13.68 | 175.85 |
|  | CONIPHER | 400/396 | **0.96454** | 0.93272 | 2421.94 | 727.22 |
|  | fastBE | 400/400 | 0.94469 | 0.92466 | 1.88 | 34.88 |
| Pairtree synthetic (S5!A2:M2881) | PhyClone | 576/576 | **0.82234** | **0.78931** | 1634.27 | 1661.44 |
|  | Orchard | 576/576 | 0.82163 | 0.77033 | 1894.89 | 534.32 |
|  | Pairtree | 576/576 | 0.82163 | 0.76741 | 3133.27 | 92.17 |
|  | fastBE | 576/576 | 0.82163 | 0.69636 | 5.90 | 52.66 |
|  | CONIPHER | 576/545 | 0.81968 | 0.61007 | 679.45 | 232.21 |
| CONIPHER no-noise (S6!A2:J751) | PhyClone | 150/150 | **0.85419** | **0.93064** | 817.35 | 1179.72 |
|  | fastBE | 150/150 | 0.85304 | 0.91341 | 2.40 | 34.50 |
|  | CONIPHER | 150/150 | 0.84832 | 0.88602 | 54.63 | 178.18 |
| CONIPHER noise (S7!A2:J751) | CONIPHER | 150/150 | **0.77541** | **0.73492** | 65.90 | 171.29 |
|  | PhyClone | 150/150 | 0.76750 | 0.73093 | 968.28 | 1216.79 |
|  | fastBE | 150/150 | 0.76089 | 0.72630 | 2.81 | 36.82 |
| Copy-number error (S14!A2:J2251) | PhyClone | 450/450 | 0.81224 | **0.89162** | 1123.55 | 1144.63 |
|  | fastBE | 450/450 | 0.80977 | 0.87372 | 27.04 | 13.92 |
|  | CONIPHER | 450/450 | **0.82146** | 0.84999 | 102.68 | 172.17 |

Lower time/memory is better. The reconstructed means show the central trade-off: PhyClone generally has the strongest AD reconstruction but is much slower and more memory-intensive than fastBE and usually Orchard/CONIPHER.

### TSSB condition trend

[INFERRED] On TSSB-Low, PhyClone mean AD F-score rises from 0.9302 (2 samples) to 0.9904 (4), 0.9969 (8), and 1.0000 (16 and 128); corresponding mean V-measure is 0.9790, 0.9971, 0.9987, 1.0000, 0.9999. On TSSB-High, mean AD F-score is 0.9333, 0.9749, 0.9581, 0.9773 for 2,4,8,16 samples. (S2!A2:L3001; S3!A2:L2001, grouped by column D.) This supports a strong result overall but not monotonic improvement in the high-mutation setting.

### Mutation-loss robustness

| Loss proportion | PhyClone V / AD F | PhyClone-N V / AD F | Locator |
|---:|---:|---:|---|
| 0.0 | 0.99777 / 0.99417 | 0.99757 / 0.99633 | S4!A2:M601, grouped by E=0 |
| 0.1 | 0.99793 / 0.97165 | 0.98711 / 0.83845 | S4!A2:M601, grouped by E=0.1 |
| 0.2 | 0.99690 / 0.95570 | 0.96741 / 0.71486 | S4!A2:M601, grouped by E=0.2 |

[INFERRED] The outlier/loss-aware configuration (`PhyClone`) has little advantage with no loss and a large advantage as loss increases. The Nemenyi table reports PhyClone better than PhyClone-N by mean differences 0.1240 AD and 0.01350 V, both `p=0.001`; it is also modestly better in time/memory by the workbook’s direction label. (S19!A2:F5.)

### Posterior metrics

Lower RRE and LPR are treated as better, consistent with each Nemenyi sheet’s `better_performer_of_pair` column.

| Dataset/range | Method | mean RRE | mean LPR |
|---|---|---:|---:|
| TSSB-Low, S31!A2:K2501 | PhyClone | **0.00795** | **0.00739** |
|  | CONIPHER | 0.05928 | 0.16371 |
|  | fastBE | 0.07800 | 2.51397 |
|  | Orchard | 0.09607 | 0.06883 |
|  | Pairtree | 0.09920 | 0.06870 |
| TSSB-High, S34!A2:K2001 | CONIPHER | **0.06204** | 0.05394 |
|  | PhyClone | 0.08409 | **-0.00940** |
|  | fastBE | 0.11669 | 0.26518 |
|  | Pairtree | 0.37388 | 0.01281 |
|  | Orchard | 0.37492 | 0.01356 |
| Pairtree synthetic, S28!A2:L2881 | Pairtree | **0.15753** | 0.91430 |
|  | Orchard | 0.16357 | 0.90141 |
|  | PhyClone | 0.16776 | **0.89007** |
|  | fastBE | 0.24682 | 4.87973 |
|  | CONIPHER | 0.25945 | 1.46048 |

Pairwise support involving PhyClone:

- [STATED] TSSB-Low: PhyClone is significant and better than all four alternatives on both RRE and LPR (S33!A2:G21; PhyClone comparisons at rows 5,8,10,11,15,18,20,21).
- [STATED] TSSB-High: PhyClone is significantly better than fastBE, Orchard, and Pairtree on RRE; CONIPHER’s small RRE advantage is marked non-significant (`p=0.01004`, `significant=0`). PhyClone is significantly best against all four on LPR. (S36!A2:G21; same comparison-row pattern.)
- [STATED] Pairtree synthetic: PhyClone’s RRE differences from Orchard and Pairtree are non-significant, while it is significantly better than CONIPHER/fastBE. For LPR it is significant against CONIPHER, fastBE, and Pairtree, but not Orchard (`p=0.01144`, `significant=0`). (S30!A2:G21.)
- [STATED] The declared decision threshold is `p<0.01` (main §2.4.3), so values such as 0.01004, 0.01144, and 0.04278 are correctly marked non-significant under the stated rule. The workbook does not expose the underlying rank/block preprocessing, and some omnibus p-values are not exactly reproducible from visible cells.

### HGSOC exact reconstruction and mapping

The six five-row sheets exactly reconstruct Supplement Table S1 after rounding to two decimals. Each source range is A2:I6 in the named sheet.

| Patient | Input | PhyClone V / AD F | Best/tie interpretation | XLSX sheet |
|---|---|---:|---|---|
| 2 | WGS | 0.77875 / 0.88824 | AD tied with fastBE; all V equal | S8 |
| 2 | WGS+T | 1.00000 / 1.00000 | AD/V tied with CONIPHER and fastBE | S9 |
| 3 | WGS | 0.84514 / 0.81905 | best V and AD | S10 |
| 3 | WGS+T | 1.00000 / 0.92935 | best V and AD | S11 |
| 9 | WGS | 0.90876 / 0.94782 | tied with CONIPHER/fastBE | S12 |
| 9 | WGS+T | 1.00000 / 1.00000 | tied with CONIPHER/fastBE/Orchard | S13 |

All 30 method-runs report `Success=1`. These are single cases, so they are descriptive and do not support population-level statistical claims.

## Paper/supplement figure and table mapping

The mappings below are [STATED] by `supp.pdf` pp. 27–28 unless noted.

| Paper object | XLSX evidence | Reliability |
|---|---|---|
| Supplement Tables S2–S14 | Matching S2–S14 sheets in Performance workbook | exact by sheet title/range |
| Supplement Tables S15–S27 | Matching S15–S27 sheets in Friedman/Nemenyi workbook | exact by sheet title/range |
| Supplement Tables S28–S36 | Matching S28–S36 sheets in Posterior workbook | exact by sheet title/range |
| Figure S10 posterior panels | S28/S31/S34 raw posterior metrics | high: dataset+metric+methods match; precise plotting/filtering code not in XLSX |
| Figure S11 TSSB-Low runtime | S2 time column L | high for values; plotting/filtering details unresolved |
| Figures S12–S13 Pairtree stratifications | S5 AD plus S28 RRE/LPR; group by samples/nodes or ratios | high for source data; plot transforms unresolved |
| Figure S14 CN perturbation | S14 raw performance | partial: dataset and metrics match, but error-proportion labels are absent |
| Figures S15/S16 and Table S1 | S8–S13 HGSOC sheets | exact numeric table match; topology drawings themselves are not encoded in XLSX |

UNRESOLVED: Mapping to numbered **main-paper** figures/tables cannot be established from the XLSX and supplement alone without reading the main paper; no unsupported mapping is asserted here.

## Anomalies and caveats

1. **Copy-number condition missing.** S14 has 450 rows per method versus 150 in S6, compatible with three perturbation levels, but there is no `error_proportion` column. The mapping of individual rows to 0/0.1/0.2 is UNRESOLVED without evaluation code or metadata. Consequently, no condition-specific CN-error mean is reported.
2. **Significance metadata incomplete.** S19 omits the `significant` column. All other Nemenyi sheets contain it. The raw `p=0.001` values are reported, but correction/decision status cannot be recovered from S19 itself.
3. **Literal zero p-values.** Numerous omnibus/pairwise p-values are stored as `0`; these likely reflect numeric underflow or export rounding and should be rendered `p` below machine/export precision, not `p=0` as a probability claim.
4. **Implicit correction.** Some Nemenyi rows have `p<0.05` yet `significant=0` (examples: S18 row 8, `p=0.04278`; S25 rows 18/20/21, `p≈0.023–0.0258`; S30 row 20, `p=0.01144`; S36 row 5, `p=0.01004`). The multiple-testing procedure/alpha is not documented in workbook cells.
5. **Failures and blanks.** S2 has 51 failures: CONIPHER 27 and PhyloWGS 24. S3 has 4 failures, all CONIPHER. S5 has 31 failures, all CONIPHER. Result cells are blank for these rows, making complete-case means potentially optimistic for methods with failures. (S2!G2:L3001; S3!G2:L2001; S5!H2:M2881.)
6. **Resource units absent.** Columns are named `time` and `memory` without units in XLSX. Supplement Figure S11 establishes seconds for its time plot, but memory units remain UNRESOLVED from these sources.
7. **Method identity and stochastic comparability.** Some methods have identical V-measure in real and synthetic rows because they appear to use the same input clustering, while PhyClone sometimes predicts fewer mutations and a different clustering (e.g. patient 3). This makes topology and clustering comparisons intertwined and should be stated when interpreting AD F-score.
8. **Posterior metric direction.** Lower-is-better is inferred from `better_performer_of_pair` and signs in S30/S33/S36, not explicitly documented in the raw metric sheet headers.

## Evidence labels summary

- `[STATED]`: exact workbook cells/sheet mappings or supplement-declared mappings.
- `[INFERRED]`: aggregates computed from raw cells, metric-direction deduction, and experimental interpretation.
