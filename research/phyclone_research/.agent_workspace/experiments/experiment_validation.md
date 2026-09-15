# Experiment validation

Scope: main paper `phyclone.pdf`, supplement `btaf344_supplementary_data/supp.pdf`, the three supplied XLSX workbooks (via the lossless cell exports under `.agent_workspace/xlsx/`), repository `PhyClone/`, and the four first-stage analyst packets. All numerical conclusions below were independently recomputed from cell exports; analyst prose was not treated as evidence.

## Common design and evidence rules

- [STATED] Synthetic data were pre-clustered with PyClone-VI 0.1.6 (100 initial clusters, 100 restarts, binomial density); all five later-stage methods received the same clusters. HGSOC used published clusters. Each method/trial had a 48 h limit. PhyClone 0.7.0 used 4 chains, 100 burn-in iterations, 5,000 MCMC iterations, 100 particles, beta-binomial density and the semi-adapted kernel; its reported point tree was MAP joint-likelihood. (Main §2.4.2, p.5.)
- [STATED] Point metrics are V-measure (clustering; higher better) and ancestor–descendant F-score (topology/assignment; higher better). Posterior metrics are likelihood-weighted RRE and LPR (lower better); all methods' LPR solutions were rescored with PhyClone's marginalisation. (Main §2.4.3, pp.5–6.)
- [STATED] The declared decision rule is Friedman omnibus `p<0.01`, followed by pairwise Nemenyi `p<0.01`; direction is taken from the mean difference. Every `significant` flag in S16/S18/S21/S23/S25/S27/S30/S33/S36 agrees exactly with `p<0.01`. Values around 0.01–0.043 marked false therefore reflect the declared threshold, not evidence of a hidden correction.
- [IMPLEMENTED/ABSENT] The checked-out repository implements inference but contains no benchmark metric, Friedman/Nemenyi, plotting, timeout, or missing-value pipeline (`rg` found no evaluation definitions). Exact reproduction of the authors' evaluation preprocessing from code is therefore UNRESOLVED.
- [INFERRED, numerically exact] Statistical sheets penalise failed/missing outcomes rather than using complete-case means: missing point V/AD values are effectively 0; missing posterior RRE values are effectively 1; missing LPR values are effectively 1.5. These constants exactly reconstruct the Nemenyi `mean_diff` values involving CONIPHER/PhyloWGS. Raw descriptive means over nonblank values must not be confused with the tested means.

## E1. Does the outlier state protect against mutation loss?

**Question → dataset → setup.** [STATED] FS-CRP simulations deliberately lose mutation sets in descendant branches. Loss fractions are 0, 0.1 and 0.2; 100 trials/level; 600 SNVs, depth 1,000, 8 samples, purity 1.0. This is an internal ablation, PhyClone with loss/outlier modelling (`PhyClone`) versus naïve (`PhyClone-N`). (Main §2.4.1.1 and §3.1; Fig.2.)

**Metric → raw evidence → result.** S4 (`A2:M601`) has 300 rows/method and no failures:

| loss | PhyClone V / AD | PhyClone-N V / AD |
|---:|---:|---:|
| 0.0 | 0.99777 / 0.99417 | 0.99757 / 0.99633 |
| 0.1 | 0.99793 / 0.97165 | 0.98711 / 0.83845 |
| 0.2 | 0.99690 / 0.95570 | 0.96741 / 0.71486 |

S19 reports overall PhyClone advantages of 0.013501 V and 0.123960 AD, both `p=0.001`. S19 has no `significant` column, but both pass the paper's declared 0.01 threshold.

**Interpretation → supported claim.** [STATED, SUPPORTED] The outlier state has negligible cost at zero loss and strongly limits degradation under this simulated loss mechanism.

**Caveats.** The authors explicitly say the generator favours PhyClone and omit external baselines. The test is pooled across loss levels, so it does not separately establish significance at each fraction. The data support robust outlier classification, not localisation of the biological deletion branch.

## E2. TSSB-Low: accuracy and scaling under a Bayesian generator

**Question → dataset → setup.** [STATED] Compare accuracy/efficiency when data arise from a defined TSSB model equivalent to PhyloWGS's model. One hundred SNVs, depth 1,000, purity 1.0, sample counts 2/4/8/16/128, 100 trials/level. Six methods: PhyClone, PhyloWGS, Pairtree, CONIPHER, Orchard and fastBE. (Main §2.4.1.2, §3.2; Fig.3.)

**Raw evidence.** S2 (`A2:L3001`) contains 500 rows/method. Failures: CONIPHER 27, PhyloWGS 24, all others 0. Nonblank descriptive means are PhyClone V=0.99496, AD=0.98350, time=253.26; PhyloWGS V=0.81468, AD=0.90456, time=37,562.90. PhyClone AD rises from 0.9302 at 2 samples to 1.0000 at 16/128; this trend is not a guarantee of monotonicity in other datasets.

**Statistical result.** S15 omnibus tests are significant for AD, V, time and memory. S16 says PhyClone beats every comparator in AD (`p<=0.000636`), but in V only PhyloWGS is significantly worse; no method significantly beats PhyClone. PhyloWGS is significantly slower than PhyClone (`p=5.88e-7`) and all other methods. Independent Friedman recomputation exactly reproduces S15 AD and resource p-values when failed accuracy is scored zero.

**Interpretation → supported claim.** [STATED, SUPPORTED WITH QUALIFICATION] PhyClone achieved the best tested accuracy profile and was far faster than non-preclustered PhyloWGS. The claim that “fully Bayesian inference can be more accurate” is suggestive, not a controlled Bayesian-versus-non-Bayesian causal comparison: model, inference and pre-clustering differ simultaneously.

## E3. Robustness across TSSB-High, Pairtree and CONIPHER-NN generators

**Datasets/setup.** [STATED]

- TSSB-High: 10,000 SNVs, depth 1,000, purity 1.0, samples 2/4/8/16, 100 trials/level (S3: 400/method).
- Pairtree: `K={3,10,30,100}`, `M={1,3,10,30,100}`, `D={50,200,1000}`, mutations `K*N`, `N={10,20,100}`, 4 replicates (S5: 576/method).
- CONIPHER no-noise: 150 published simulations, grouped as 2–3, 4–7 and 8+ samples (S6: 150/method).

**Replicate-count resolution.** [RESOLVED] The apparent full-grid count is 720, but S5 contains only 144 parameter combinations ×4 replicates=576. The omitted combinations are exactly `K=30 or 100` with `M=1 or 3`; all remaining `K,M` pairs contain the full 3-depth ×3-N grid. Thus the paper's 576 is supported, while its prose does not state the exclusion rule.

**Raw evidence and missingness.** S3 has 4 CONIPHER failures; S5 has 31 CONIPHER point failures. Posterior sheets have still more missing CONIPHER solutions: S34 6/400, S28 32/576. No other method has missing point/posterior values. Selected nonblank means:

| dataset | PhyClone V / AD | notable comparator |
|---|---:|---:|
| TSSB-High | 0.94806 / 0.96092 | CONIPHER 0.96454 / 0.93272 |
| Pairtree | 0.82234 / 0.78931 | Pairtree 0.82163 / 0.76741; CONIPHER 0.81968 / 0.61007 |
| CONIPHER-NN | 0.85419 / 0.93064 | CONIPHER 0.84832 / 0.88602; fastBE 0.85304 / 0.91341 |

**Point statistical result.** S18/S21/S23 support the main-paper wording: PhyClone significantly beats Orchard and Pairtree in AD on all three datasets; beats CONIPHER in both metrics except TSSB-High V, where CONIPHER significantly wins; beats fastBE in AD on Pairtree but not on TSSB-High or CONIPHER-NN. No method significantly beats PhyClone in AD.

**Posterior result.** S28/S30, S34/S36 show: on Pairtree, PhyClone significantly beats CONIPHER/fastBE in RRE and CONIPHER/fastBE/Pairtree in LPR, but not Orchard in either metric; on TSSB-High it beats fastBE/Orchard/Pairtree in RRE, CONIPHER's lower raw RRE is not significant (`p=0.0100406`), and PhyClone beats all four in LPR. These exactly match main §3.3.

**Interpretation/caveats.** [SUPPORTED] Relative accuracy robustness across three generators is supported. The “do not expect many more clones than samples” statement is an empirical recommendation from Figs S12–S13, not an identifiability theorem. Pairtree's design is an incomplete factorial grid, and pooled tests weight the retained grid rather than a full grid. PhyClone time/memory costs are substantial (e.g. Pairtree mean time 1,634 s, mean memory 1,661 in unspecified units).

## E4. Noise / ISA violations

**Question → dataset.** [STATED] CONIPHER dataset 1 contains 150 simulations with ISA violations attributed to sequencing error or mutation loss; the same five methods and three sample-count strata are used. (Main §2.4.1.4, §3.4; Fig.5.)

**Raw/statistical evidence.** S7 has 150 successful rows/method. Means: CONIPHER V/AD=0.77541/0.73492, PhyClone=0.76750/0.73093, fastBE=0.76089/0.72630. S24 omnibus tests are significant. S25 shows no significant AD differences among these three, while each significantly beats Orchard and Pairtree; no comparator significantly beats PhyClone. For V, no PhyClone comparison reaches the declared 0.01 threshold.

**Claim.** [STATED, SUPPORTED] PhyClone is competitive under this noise generator and belongs to the top statistically indistinguishable AD group. This does not establish superiority over CONIPHER/fastBE or distinguish sequencing-error robustness from mutation-loss robustness.

## E5. Copy-number perturbation

**Question → dataset/setup.** [STATED] CONIPHER-NN is perturbed at per-sample region proportions 0/0.1/0.2 by ±1 changes to major/minor CN; outcomes are V and AD (Supplement Fig.S14, p.25).

**Raw evidence.** S14 has 450 successful rows/method, consistent with 3×150, but has no perturbation-level column. Pooled means: PhyClone V/AD=0.81224/0.89162; CONIPHER=0.82146/0.84999; fastBE=0.80977/0.87372. S26/S27 show PhyClone significantly beats fastBE/Orchard/Pairtree in both metrics and CONIPHER in AD; CONIPHER's higher V is not significant.

**Claim/caveat.** [STATED, PARTIALLY SUPPORTED] The pooled ranking claim is supported. The stronger visual claim that increasing CN-error proportion has minimal impact cannot be independently reconstructed from S14 because row-to-0/0.1/0.2 mapping is absent; **UNRESOLVED**. The suggested PyClone-VI/genotype-uncertainty mechanism is explicitly speculative and all methods shared the same preprocessing, which can mask downstream sensitivity.

## E6. HGSOC mutation-loss reconstructions

**Question → dataset/setup.** [STATED] Patients 2, 3 and 9; WGS and WGS+Targeted inputs; ground-truth-defining mutation subsets came from single-cell/targeted validation. Before scoring, predictions were pruned to that subset and newly empty nodes collapsed. CONIPHER used `min_cluster_size=3`. (Main §2.4.1.5, §2.4.2, §3.5; Fig.6; Supp Figs S15–S16/Table S1.)

**Raw evidence.** S8–S13 each contain one row/method; all 30 rows have `Success=1` and exactly reproduce Table S1 after two-decimal rounding. PhyClone V/AD: patient 2 WGS 0.77875/0.88824, WGS+T 1/1; patient 3 WGS 0.84514/0.81905, WGS+T 1/0.92935; patient 9 WGS 0.90876/0.94782, WGS+T 1/1. PhyClone is uniquely best on both metrics for patient 3 and ties the best AD values for patients 2/9.

**Qualitative mapping/result.** Main Fig.6 maps to S10/S11 and shows patient 3; Supp Figs S15/S16 map to S8/S9 and S12/S13. The images, not XLSX, support the claim that PhyClone excludes two lost patient-3 clusters. Pairtree's `Success=1` only shows pipeline completion; it does not contradict the paper's qualitative statement that its output struggled to form a valid single-rooted DAG.

**Claim/caveats.** [STATED, SUPPORTED DESCRIPTIVELY] Patient-3 reconstruction and loss handling are supported for these cases. `n=3`, one cancer type, no inferential statistics, and evaluation after ground-truth-subset pruning/collapse prevent population-level claims and may hide extra-node/assignment errors.

## Figure/table → workbook map

| publication object | workbook evidence |
|---|---|
| Main Fig.2 | Performance S4; tests S19 |
| Main Fig.3 | Performance S2; tests S15–S16 |
| Main Fig.4 A/B, C/D, E/F | Performance S3, S5, S6; tests S17–S23 |
| Main Fig.5 | Performance S7; tests S24–S25 |
| Main Fig.6 | HGSOC S10–S11 plus topology image |
| Supp Fig.S10 | Posterior S28/S31/S34; tests S29–S36 |
| Supp Fig.S11 | S2 time column (seconds stated only in caption) |
| Supp Figs.S12–S13 | S5 AD and S28 RRE/LPR stratifications |
| Supp Fig.S14 | S14 pooled raw values; perturbation labels missing |
| Supp Figs.S15–S16 / Table S1 | S8–S9 / S12–S13 / all S8–S13 |

## Statistical cross-check and conflicts

1. Independent SciPy Friedman reconstruction exactly matches several workbook p-values (e.g. S15 AD, S17 AD, S20 AD, S24 AD/V) and all workbook decisions remain the same at `alpha=0.01`. Other exact p-values do not reproduce from the visible raw cells under straightforward block matching, despite unchanged decisions (examples: S17 V, S22 AD, S26 AD/V). **UNRESOLVED:** evaluation code, rounding/ranking preprocessing, or the exact analysis snapshot is absent.
2. **CONFLICT — UNRESOLVED.** In CONIPHER-NN, raw S6 means give fastBE−PhyClone AD = `0.91340695−0.93063703 = −0.01723008`, but S23 reports `mean_diff=+0.00095026` and labels fastBE the better performer (`p=0.94951`, nonsignificant). The inferential conclusion “no significant difference” survives, but effect direction/value does not.
3. Literal XLSX p-values of `0` are numerical/export underflow, not probability exactly zero.
4. Performance failure counts are S2: 27 CONIPHER +24 PhyloWGS; S3: 4 CONIPHER; S5: 31 CONIPHER. Posterior missing counts differ: S31 35 CONIPHER, S34 6, S28 32. Therefore point-run success and availability of posterior evaluation are not identical.
5. Pairtree S5 resource missingness is severe despite `Success=1`: Orchard memory has only 5/576 nonblank values and Pairtree 199/576; its memory comparison should not be interpreted as a reliable full-grid resource estimate. Memory units are absent from XLSX and remain **UNRESOLVED**.

## Bottom-line evidence ceiling

The supplied evidence supports that PhyClone is usually among the most accurate methods, is uniquely robust in its own mutation-loss ablation, benefits strongly from multi-sample information, and can recover the validated patient-3 loss pattern. It does **not** support universal superiority, low computational cost, a population-level clinical claim, a formal clones-versus-samples limit, or condition-specific CN-error robustness from the XLSX alone.
