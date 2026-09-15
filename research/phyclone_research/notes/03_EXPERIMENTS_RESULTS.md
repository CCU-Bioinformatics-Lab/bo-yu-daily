# Experiments and results

## Common evaluation design

[STATED] Synthetic data were pre-clustered with PyClone-VI 0.1.6 using 100 initial clusters, 100 random restarts and Binomial density; the pre-clustered inputs were supplied to CONIPHER, Pairtree, Orchard, fastBE, and PhyClone. PhyloWGS was not listed as receiving these pre-clusters and should be treated as the non-preclustered comparator. HGSOC used clusters from the original study. Each method/trial had a 48-hour cap. PhyClone 0.7.0 used four chains, 100 burn-in iterations, 5,000 MCMC iterations, 100 particles, Beta-Binomial density and semi-adapted proposals; its point tree maximized the joint score. (Main §2.4.2, p.5.)

Baselines were PhyloWGS, Pairtree, CONIPHER, Orchard and fastBE; PhyloWGS was dropped after TSSB-Low because of runtime and lack of an accuracy advantage. (Main Table 1, p.4; §3.2, pp.6–7.)

### Metrics and statistics

| Metric | Object | Direction | Evidence |
|---|---|---:|---|
| V-measure | mutation clustering | higher | Main §2.4.3, pp.5–6 |
| AD F-score | ancestor–descendant relation between mutation pairs in selected tree | higher | Main §2.4.3; Supplement Fig.S9 p.20 |
| RRE | likelihood-weighted evolutionary-relation reconstruction | lower | Main §2.4.3; direction confirmed by S30/S33/S36 |
| LPR | prevalence/VAF reconstruction relative to truth | lower; may be negative | Main §2.4.3; S30/S33/S36 |

[STATED] Point metrics use each method’s selected/default top tree; posterior metrics average unique solutions with likelihood weights. All methods’ LPR solutions were rescored using the PhyClone marginalisation. RRE/LPR are absent for CONIPHER datasets because those data violate perfect-phylogeny conditions required for enumeration. (Main §2.4.2–§2.4.3, pp.5–6.)

[STATED] Each metric first receives a Friedman omnibus test. Pairwise Nemenyi follows when `p<0.01`, and pairwise `p<0.01` is the stated decision threshold. Every supplied `significant` flag agrees with this rule—there is no need to infer an undocumented correction.

[INFERRED, numerically validated] Statistical sheets penalize missing/failed values rather than dropping them: point V/AD=0, posterior RRE=1 and LPR=1.5 reproduce pairwise mean differences. Descriptive means below use nonblank raw cells and are labelled accordingly; tested means differ for methods with failures.

## E1. Outlier component under simulated mutation loss

**Question.** Does the outlier state protect the inferred tree when deletion makes inherited mutations disappear?

**Dataset/setup.** [STATED] Trees/clusters come from the FS-CRP prior. For loss fraction 0, 0.1 or 0.2, selected mutations are placed on one chromosome, a descendant of their origin is chosen as the loss node, and the relevant downstream prevalence is subtracted. There are 100 trials/level, 600 SNVs, depth 1,000, eight samples and purity 1.0. (Main §2.4.1.1, pp.4–5.)

**Comparison.** PhyClone with (`PhyClone`) versus without (`PhyClone-N`) the outlier mechanism. Metrics: V and AD F. Main Fig.2; raw S4 `A2:M601`; test S19 `A2:F5`.

| Loss | PhyClone V / AD | PhyClone-N V / AD |
|---:|---:|---:|
| 0.0 | 0.99777 / 0.99417 | 0.99757 / 0.99633 |
| 0.1 | 0.99793 / 0.97165 | 0.98711 / 0.83845 |
| 0.2 | 0.99690 / 0.95570 | 0.96741 / 0.71486 |

[STATED + XLSX] Pooled PhyClone advantages are 0.013501 V and 0.123960 AD, each `p=0.001`. S19 lacks a `significant` column, but both meet the declared 0.01 threshold.

**Supported claim.** The outlier mechanism strongly limits degradation under this simulated loss process, with negligible no-loss cost.

**Caveat.** The authors explicitly say this generator favours PhyClone and omit external baselines. The pooled test does not establish significance separately at each loss level. It validates robust exclusion, not deletion-edge localization.

## E2. TSSB-Low: Bayesian accuracy and sample scaling

**Question.** How do methods compare under a Bayesian generator equivalent to the model behind PhyloWGS?

**Dataset/setup.** [STATED] Diploid heterozygous mutations, depth 1,000, purity 1.0, 100 SNVs, sample counts 2/4/8/16/128, 100 trials/level. Six methods. (Main §2.4.1.2, p.5; Fig.3.)

**Raw evidence.** S2 `A2:L3001` contains 500 rows/method. Failures: 27 CONIPHER and 24 PhyloWGS; none for the other four.

| Method | success/500 | nonblank mean V | nonblank mean AD | mean time |
|---|---:|---:|---:|---:|
| PhyClone | 500 | 0.99496 | **0.98350** | 253.26 |
| Orchard | 500 | 0.99321 | 0.97981 | 7.98 |
| Pairtree | 500 | 0.99321 | 0.97622 | 100.68 |
| fastBE | 500 | 0.99321 | 0.90144 | 3.33 |
| CONIPHER | 473 | 0.99140 | 0.88251 | 55.05 |
| PhyloWGS | 476 | 0.81468 | 0.90456 | 37,562.90 |

PhyClone AD increases from 0.9302 (2 samples) to 0.9904 (4), 0.9969 (8) and 1.0 (16/128), grouping S2 by column D.

**Statistics.** S15 `A2:C5` has significant omnibus results for all metrics. S16 `A2:G61` says PhyClone beats every comparator in AD (`p<=0.000636`); only PhyloWGS is significantly worse in V. PhyloWGS is significantly slower than PhyClone (`p=5.88e-7`) and all other methods.

**Supported claim.** [STATED, supported] PhyClone has the strongest tested accuracy profile and is far faster than non-preclustered PhyloWGS.

**Caveat.** “Fully Bayesian inference can be more accurate” is not a controlled causal comparison: algorithms, pre-clustering and representations differ at once.

## E3. Transfer across generators

### Data

- [STATED] **TSSB-High:** 10,000 SNVs, depth 1,000, purity 1.0, 2/4/8/16 samples, 100 trials/level. S3 `A2:L2001`.
- [STATED] **Pairtree:** nodes `K={3,10,30,100}`, samples `M={1,3,10,30,100}`, depths 50/200/1000, mutations `K*N` for `N={10,20,100}`, four replicates. S5 `A2:M2881`.
- [STATED] **CONIPHER no-noise:** 150 published simulations, grouped as 2–3, 4–7 and 8+ samples. S6 `A2:J751`.

[RESOLVED] The Pairtree prose appears to define a 720-case full grid, but S5 contains 144 combinations × four replicates = 576/method. Missing combinations are exactly `K=30 or 100` with `M=1 or 3`; all retained `K,M` pairs contain all depth × mutation-density settings. The paper’s total 576 is supported, while the exclusion rule is unstated.

### Descriptive results

| Dataset | PhyClone V / AD | Selected comparator V / AD |
|---|---:|---:|
| TSSB-High | 0.94806 / **0.96092** | CONIPHER **0.96454** / 0.93272 |
| Pairtree | **0.82234 / 0.78931** | Pairtree 0.82163 / 0.76741; Orchard 0.82163 / 0.77033 |
| CONIPHER-NN | **0.85419 / 0.93064** | fastBE 0.85304 / 0.91341; CONIPHER 0.84832 / 0.88602 |

Failures: TSSB-High has four CONIPHER point failures; Pairtree has 31. Other methods have none. Posterior missingness is six and 32 CONIPHER rows respectively.

### Pairwise conclusions

[STATED + XLSX] S18/S21/S23 show:

- PhyClone significantly beats Orchard and Pairtree in AD in all three datasets.
- CONIPHER significantly beats PhyClone only for TSSB-High V-measure.
- PhyClone significantly beats fastBE in AD on Pairtree, but not TSSB-High or CONIPHER-NN.
- No method significantly beats PhyClone in AD.

**Conflict.** In CONIPHER-NN, raw nonblank means imply fastBE−PhyClone AD = `-0.01723008`, but S23 row 8 reports `+0.00095026` and calls fastBE better (`p=0.94951`, non-significant). The decision “no significant difference” survives, but direction/effect size is **UNRESOLVED**.

### Posterior conclusions

| Dataset | Method | mean RRE | mean LPR | Raw range |
|---|---|---:|---:|---|
| TSSB-Low | PhyClone | **0.00795** | **0.00739** | S31!A2:K2501 |
|  | CONIPHER | 0.05928 | 0.16371 | same |
|  | Orchard | 0.09607 | 0.06883 | same |
| TSSB-High | CONIPHER | **0.06204** | 0.05394 | S34!A2:K2001 |
|  | PhyClone | 0.08409 | **-0.00940** | same |
|  | Pairtree | 0.37388 | 0.01281 | same |
| Pairtree | Pairtree | **0.15753** | 0.91430 | S28!A2:L2881 |
|  | Orchard | 0.16357 | 0.90141 | same |
|  | PhyClone | 0.16776 | **0.89007** | same |

[STATED + XLSX] On Pairtree, PhyClone significantly beats CONIPHER/fastBE in RRE and CONIPHER/fastBE/Pairtree in LPR, but not Orchard in either. On TSSB-High, it beats fastBE/Orchard/Pairtree in RRE; CONIPHER’s lower RRE misses the 0.01 threshold (`p=0.0100406`); PhyClone beats all four in LPR. On TSSB-Low, PhyClone beats all four in both metrics. (S30/S33/S36 `A2:G21`.)

**Interpretation.** Cross-generator accuracy is supported. All methods degrade as nodes grow relative to samples (Supplement Figs.S12–S13), but “do not expect significantly more clones than samples” is an empirical recommendation, not a theorem.

## E4. Noise and ISA violations

**Question/setup.** [STATED] CONIPHER dataset 1 comprises 150 simulations with ISA violations attributed to sequencing error or mutation loss, split into three sample-count strata. (Main §2.4.1.4, §3.4; Fig.5.)

**Evidence.** All S7 `A2:J751` rows succeed. Nonblank means: CONIPHER V/AD 0.77541/0.73492; PhyClone 0.76750/0.73093; fastBE 0.76089/0.72630. S24 omnibus results are significant. S25 says these three do not differ significantly in AD, while each beats Orchard/Pairtree; no PhyClone V comparison meets `p<0.01`.

**Supported claim.** [STATED] PhyClone is competitive and in the top indistinguishable AD group. The experiment does not prove superiority or separate sequencing-error from loss robustness.

## E5. Copy-number perturbation

**Question/setup.** [STATED] In CONIPHER-NN, 0/0.1/0.2 of regions per sample receive ±1 changes to major CN, minor CN, or both. Metrics are V and AD, stratified into 2–3, 4–7, 8+ samples. (Supplement Fig.S14, p.25.)

**Pooled evidence.** S14 `A2:J2251` has 450 successful rows/method. Means: PhyClone 0.81224/0.89162; CONIPHER 0.82146/0.84999; fastBE 0.80977/0.87372. S27 shows PhyClone significantly beats fastBE/Orchard/Pairtree in both metrics and CONIPHER in AD; CONIPHER’s V advantage is not significant.

**Evidence ceiling.** S14 lacks a perturbation-level column. Pooled ranking is supported, but the statement that increasing error proportion has little effect cannot be independently reconstructed from XLSX: **UNRESOLVED**. The authors’ suggested mechanism—shared PyClone-VI preprocessing plus genotype uncertainty—is explicitly speculative and common preprocessing may mask downstream sensitivity.

## E6. Real HGSOC reconstruction

**Question/setup.** [STATED] Patients 2, 3 and 9 have WGS and WGS+targeted-count inputs; ground-truth trees derive from single-cell/targeted validation. Predictions are pruned to ground-truth-defining mutations and emptied nodes collapsed before scoring. CONIPHER uses `min_cluster_size=3`. (Main §2.4.1.5, pp.5–6; §2.4.2 p.5.)

| Patient | Input | PhyClone V / AD | Comparative interpretation | Cells |
|---|---|---:|---|---|
| 2 | WGS | 0.77875 / 0.88824 | AD tied with fastBE | S8!A2:I6 |
| 2 | WGS+T | 1 / 1 | tied with CONIPHER/fastBE | S9!A2:I6 |
| 3 | WGS | **0.84514 / 0.81905** | unique best V and AD | S10!A2:I6 |
| 3 | WGS+T | **1 / 0.92935** | unique best V and AD | S11!A2:I6 |
| 9 | WGS | 0.90876 / 0.94782 | tied with CONIPHER/fastBE | S12!A2:I6 |
| 9 | WGS+T | 1 / 1 | tied with CONIPHER/fastBE/Orchard | S13!A2:I6 |

All 30 runs have `Success=1` and reproduce Supplement Table S1 after two-decimal rounding. Main Fig.6, rather than XLSX, supports that PhyClone excludes two lost patient-3 clusters in both inputs; CONIPHER/fastBE retain them and do not reconstruct the full topology. Pairtree completion does not contradict the paper’s qualitative difficulty obtaining a valid single-rooted DAG.

**Supported claim.** [STATED, descriptive] The patient-3 case supports loss-aware reconstruction. With only three patients, one cancer type, no inferential statistics, and truth-subset pruning/collapse, it does not establish clinical generality and may hide extra-node/assignment errors.

## Statistical and artifact caveats

1. Literal XLSX `p=0` is numerical/export underflow, not probability zero.
2. Some Friedman p-values do not exactly reproduce from visible raw cells under straightforward matching (e.g. S17 V, S22 AD, S26 AD/V), though every `p<0.01` decision remains unchanged. Evaluation code/snapshot is absent: UNRESOLVED.
3. Resource units are absent; Figure S11 explicitly labels time in seconds. Pairtree resource data are incomplete even among `Success=1`: Orchard memory has 5/576 nonblank cells and Pairtree 199/576. Do not interpret their raw memory means as full-grid estimates.
4. Point and posterior missing counts differ, so pipeline success is not the same as evaluable posterior output.
5. Non-significance is not equivalence; pooled tests can hide condition-specific reversals.

## Supported final experimental claim

The supplied evidence supports that PhyClone is usually among the most accurate evaluated methods, has clear benefit from its outlier state in a favourable mutation-loss ablation, uses additional samples effectively, and recovers a validated patient-3 loss pattern. It does not support universal superiority, inexpensive computation, a formal clone/sample identifiability bound, condition-specific CN-error robustness from XLSX alone, or population-level clinical efficacy.
