# PhyClone source map

## Scope and evidence vocabulary

This research package was reconstructed entirely from `/bip8_disk/boyu114/main_work/research/phyclone_research`; no source outside that workspace was used.

- `[STATED]`: explicitly stated in the paper or supplement.
- `[IMPLEMENTED]`: directly established by the checked-out source code.
- `[INFERRED]`: an analysis or consequence not explicitly claimed by the authors.
- `UNRESOLVED`: available evidence does not support a reliable conclusion.

Important version boundary: the experiments in the paper used **PhyClone 0.7.0** (main paper §2.4.2, p.5). The inspected checkout is clean **PhyClone 0.8.0**, commit `27383246c1aff7b1d62c02662017bd61bfdfbc33`. Version-sensitive findings are identified explicitly rather than attributed retroactively to the paper results.

## Workspace inventory and immutable identifiers

| Source | Role | SHA-256 / version |
|---|---|---|
| `phyclone.pdf` | Main research story, primary method, experimental design and headline claims | `413500e0f30e19d23aaf3fcf99014240fd87036319300053ba0264ab6c7787ad` |
| `btaf344_supplementary_data/supp.pdf` | Full mathematical derivation, PG-SMC details, caching/tests, supplementary figures/table map | `d40aa2d3672aebe175ece825e2888b45ff705750bd0946c07641dabd2ebfdf5b` |
| `Experiment_Performance_Metrics.xlsx` | Raw point-estimate accuracy, success, runtime and memory results; Supplement Tables S2–S14 | `d9e00c3029d16523b318d2b2d7ffe35929eeb6d7406e9fd60c59b3dcbab88c6d` |
| `Experiment_Friedman_Nemenyi_Tests.xlsx` | Omnibus and pairwise tests; Supplement Tables S15–S27 | `eabda8bdfe0e8daa502a20a4a14c0532ca6e686b014960c760bb5d0c2bc5eebe` |
| `Experiment_Posterior_Metrics.xlsx` | Raw RRE/LPR and tests; Supplement Tables S28–S36 | `6c25a17d3876930fff83576dd3703ce16cf172a5d33dab7edaf76830973d6268` |
| `PhyClone/` | Current implementation, input/output contract, defaults and tests | tag `0.8.0`, commit `27383246c1aff7b1d62c02662017bd61bfdfbc33` |
| `RESEARCH_PLAN.md` | Research protocol and completion contract | `a222f82b236646163215d21b25b0a53b7ebf036c2a83ff53bcc9c7cbf84dfc3b` |

No independent raw BAM/VCF, simulation seeds, evaluation scripts, or paper-result trace files are present. The XLSX workbooks are the supplied result artifacts; the application repository does not contain the benchmark/statistics pipeline.

## Source relationship

```text
Main paper (question, model, benchmark design, claims)
       ├── Supplement (derivations, algorithms, extra figures, table index)
       ├── XLSX (raw results and statistical decisions)
       └── Repository (runtime contract and implementation)

Paper version: 0.7.0                    Inspected code: 0.8.0
       └──────── version-sensitive validation ────────┘
```

The main paper and supplement establish intended behavior. The checkout validates current behavior, but cannot automatically validate paper-era results. Local tag `0.7.0` was consulted by the Methods Validator for the outlier integral, bootstrap proposal and subtree-PG findings.

## Repository architecture relevant to the research questions

| Stage | Module(s) | Research role |
|---|---|---|
| CLI/API orchestration | `phyclone/cli.py`, `phyclone/run.py` | Parameter parsing, chains, burn-in, PG/SMC loop, trace writing |
| Input and likelihood-grid construction | `phyclone/data/pyclone.py`, `data/base.py`, `data/validator/*.json` | Tidy input contract, filtering, CN/purity correction, pre-cluster atoms, outlier marginal |
| Loss-prior heuristic | `data/cluster_outlier_probabilities.py` | Truncal cluster and chromosome-concentration test |
| Emission mathematics | `utils/math_utils.py` | Binomial/Beta-Binomial PyClone genotype mixture |
| Tree state and DP | `tree/tree.py`, `tree/base.py`, `tree/tree_node.py`, `tree/utils.py` | Dummy-root forest, mutation assignments, descendant convolution/cumulative integration |
| Joint prior/score | `tree/distributions.py` | CRP, forest prior, root penalty, outlier prior/likelihood |
| SMC proposals | `smc/kernels/{bootstrap,fully_adapted,semi_adapted}.py` | Bottom-up tree growth and proposal densities |
| Particle system/order | `smc/samplers/*.py`, `smc/swarm/swarm.py`, `smc/utils.py` | ESS/resampling, conditional/unconditional SMC, admissible permutations |
| MCMC moves | `mcmc/particle_gibbs.py`, `mcmc/gibbs_mh.py`, `mcmc/concentration.py` | Whole/subtree PG, reassignment, prune-regraft, alpha update |
| Outputs | `utils/save_hdf5.py`, `process_trace/*.py` | Trace, MAP, consensus, topology report, Newick/TSV/prevalences |
| Verification | `phyclone/tests/` | Exact small posterior, marginalisation, root term, order and convolution checks |

## XLSX schema

### Performance workbook

| Sheet(s) | Range | Dataset / condition | Methods | Metric / result | Replicates |
|---|---:|---|---|---|---|
| S2 TSSB-Low | A1:L3001 | depth 1000; 100 SNVs; samples 2/4/8/16/128 | six, including PhyloWGS | V, mutation counts, AD F, success, memory, time | 100/condition/method |
| S3 TSSB-High | A1:L2001 | depth 1000; 10,000 SNVs; samples 2/4/8/16 | five | same | 100/condition/method |
| S4 FS-CRP Loss | A1:M601 | 600 SNVs; 8 samples; loss 0/0.1/0.2 | PhyClone, PhyClone-N | same plus loss proportion | 100/condition/method |
| S5 Pairtree | A1:M2881 | depth, nodes, mutations, samples | five | same | 4/retained combination; 576/method |
| S6/S7 CONIPHER | A1:J751 each | no-noise/noise; simulation ID and samples | five | V, AD F, success, memory, time | 150/method |
| S8–S13 HGSOC | A1:I6 each | patients 2/3/9 × WGS/WGS+targeted | five | V, AD F, success, memory, time | one/method |
| S14 CN Error | A1:J2251 | simulation ID and samples; perturbation label absent | five | V, AD F, success, memory, time | 450/method |

### Statistical workbook

- Friedman sheets S15/S17/S20/S22/S24/S26: `A1:C5` (`metric`, `p_value`, `significant`).
- Nemenyi sheets S16 `A1:G61`; S18/S21/S23/S25/S27 `A1:G41`: metric, method pair, p, mean difference, better performer, significance.
- S19 FS-CRP Loss is `A1:F5` and omits the `significant` column.

### Posterior workbook

- Raw metrics: S28 Pairtree `A1:L2881`, S31 TSSB-Low `A1:K2501`, S34 TSSB-High `A1:K2001`.
- Fields: method, RRE, number of evaluated trees, design variables, perplexity, truth perplexity and LPR.
- Omnibus: S29/S32/S35 `A1:C3`; pairwise: S30/S33/S36 `A1:G21`.

All 35 sheets are visible; none contains formulas or merged cells. Memory units are absent. Figure S11 establishes seconds for its runtime panel, but the workbook alone does not define time units globally.

## Publication object → raw evidence map

| Publication object | Evidence |
|---|---|
| Main Fig.2 | Performance S4; tests S19 |
| Main Fig.3 | Performance S2; tests S15–S16 |
| Main Fig.4 panels A/B, C/D, E/F | Performance S3, S5, S6; tests S17–S23 |
| Main Fig.5 | Performance S7; tests S24–S25 |
| Main Fig.6 | HGSOC S10/S11 plus the topology image |
| Supplement Fig.S10 | Posterior S28/S31/S34; tests S29–S36 |
| Supplement Fig.S11 | S2 time column L |
| Supplement Figs.S12–S13 | S5 AD and S28 RRE/LPR grouped by nodes/samples |
| Supplement Fig.S14 | S14 pooled values; error-level row labels are missing |
| Supplement Figs.S15–S16 / Table S1 | S8–S9 / S12–S13 / S8–S13 |

## Primary-question coverage

- Motivation and contribution: `01_PAPER_BIG_PICTURE.md`.
- Inputs, variables, model, likelihood, priors, prevalence, inference, preprocessing, outliers and outputs: `02_METHODS_DEEP_DIVE.md`.
- Every major experiment, data, baselines, metrics, quantitative results and caveats: `03_EXPERIMENTS_RESULTS.md`.
- Equations/defaults/runtime behavior and code-version differences: `04_CODE_MAPPING.md`.
- Claim-level cross-source traceability and conflicts: `05_EVIDENCE_MATRIX.md`.
- Biological/statistical/computational/data assumptions, limitations and failure cases: `06_ASSUMPTIONS_LIMITATIONS.md`.
- 10–15 minute teaching/report narrative: `07_PRESENTATION_BRIEF.md`.

## Global unresolved items

1. The exact benchmark evaluation/statistics code and timeout preprocessing are absent.
2. S14 does not encode the 0/0.1/0.2 copy-number perturbation level per row.
3. Several Friedman p-values cannot be reproduced exactly from visible cells under straightforward blocking, although every `p<0.01` decision is unchanged.
4. Current environment lacks required dependencies/Python version for the full test suite; only `test_root_term` was run (8 passing tests). This is an environment limitation, not an assertion failure.

