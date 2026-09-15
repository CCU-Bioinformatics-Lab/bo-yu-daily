# Final integrator revision

## Disposition

Final state: **COMPLETE**. The independent reviewer verdict was PASS WITH CORRECTIONS. All six findings were independently checked against the workspace evidence and applied; no reviewer item was rejected.

## Corrections applied

| Finding | Evidence rechecked | Revision |
|---|---|---|
| R1 HIGH: shared pre-clustering included PhyloWGS ambiguously | Main paper extraction explicitly lists CONIPHER, Pairtree, Orchard, fastBE and PhyClone as recipients (`.agent_workspace/paper/phyclone_raw.txt:590-598`); validator packet agrees (`.agent_workspace/experiments/experiment_validation.md:7`) | Corrected `notes/03_EXPERIMENTS_RESULTS.md`, `notes/06_ASSUMPTIONS_LIMITATIONS.md`, and `.agent_workspace/paper/assumptions.md`. TSSB-Low PhyloWGS is explicitly described as the non-preclustered comparator. |
| R2 MEDIUM: timeout handling overstated as absent | Current checkout exposes `--max-time` (`PhyClone/phyclone/cli.py:330`) and checks elapsed time in burn-in/main loops (`run.py:289,359`); validator confirms benchmark/evaluation pipeline is absent | Corrected `notes/06_ASSUMPTIONS_LIMITATIONS.md`: application stop exists, while benchmark timeout preprocessing and missing-value/penalty handling remain absent, so paper-era 48-hour results are not reproducible from the repository. |
| R3 MEDIUM: CN-error flatness labelled established | S14/S27 support pooled ranking, but S14 has no perturbation-level label; paper reports minimal impact, which cannot be reconstructed condition-by-condition | Corrected the CN-error row in `notes/05_EVIDENCE_MATRIX.md` to separate pooled support from the unresolved condition-specific trend. |
| R4 MEDIUM: workbook threshold interpretation contradicted paper | Main §2.4.3 and validator packet declare `p<0.01`; supplied flags agree with that threshold (`.agent_workspace/experiments/experiment_validation.md:9`) | Corrected `.agent_workspace/xlsx/xlsx_analysis.md:149`; removed the unsupported hidden multiple-comparison-correction inference. |
| R5 MEDIUM: presentation called memory categorically high | S11 establishes seconds for the plotted runtime; XLSX memory units are absent and Pairtree resource cells are incomplete (`notes/03_EXPERIMENTS_RESULTS.md:155`) | Corrected `notes/07_PRESENTATION_BRIEF.md` to state the supported runtime/resource trade-off and explicitly qualify missing memory units/cells. |
| R6 LOW: package absence attributed to Python 3.10 | Repository declares Python ≥3.12; observed collection failures were unavailable `numba`, `networkx`, and `xxhash` packages; `test_root_term` passed | Corrected `notes/04_CODE_MAPPING.md` to describe the environment/package limitation without attributing it to the interpreter version. |

## Preserved unresolved conflicts

The revision does not over-resolve evidence ceilings. The canonical notes still mark as unresolved: the published uniform outlier integral versus triangular code sum; subtree-PG selection-probability TODO; CONIPHER-NN fastBE/PhyClone raw-versus-S23 AD direction; exact reproduction of selected Friedman p-values; S14 perturbation-level labels; and the absent benchmark timeout/statistics pipeline. The 0.8.0 bootstrap-with-outliers mismatch remains a confirmed current-version regression, distinct from the semi-adapted benchmark path. Paper v0.7.0 versus inspected checkout v0.8.0 remains explicit.

## Canonical-note integrity check

All eight required notes remain present, non-empty, and structurally complete:

1. `00_SOURCE_MAP.md` — inventory, source relationships, architecture, workbook schema, evidence map, question coverage, unresolved items.
2. `01_PAPER_BIG_PICTURE.md` — motivation, gap, core idea, architecture, experiments, validated claims, contribution ceiling.
3. `02_METHODS_DEEP_DIVE.md` — inputs, variables, emissions, priors, prevalence, DP, inference, outliers, outputs, defaults, conflicts.
4. `03_EXPERIMENTS_RESULTS.md` — common design, metrics, E1–E6, raw/statistical evidence, caveats, final claim.
5. `04_CODE_MAPPING.md` — paper-to-source mapping, runtime behavior, defaults, tests, warnings.
6. `05_EVIDENCE_MATRIX.md` — claim-level cross-source matrix and resolved/unresolved conflict register.
7. `06_ASSUMPTIONS_LIMITATIONS.md` — biological, statistical, computational, dataset assumptions, limitations, failure cases, evidence ceiling.
8. `07_PRESENTATION_BRIEF.md` — short narrative, ten-slide brief, backup slides, anticipated questions.

## Primary-question coverage (1–36)

All 36 questions in `RESEARCH_PLAN.md` have an answer or an explicit evidence ceiling:

- 1–4 motivation, importance, prior limits, difficulty → `notes/01` (stated/inferred boundary).
- 5–17 core idea, inputs, mutation/cluster/tree representation, CN/purity/VAF, likelihood, priors, prevalence, inference, preprocessing, outliers, outputs → `notes/02` (including implementation/version caveats).
- 18–25 experiment aims, datasets, generation, baselines, metrics, results, XLSX support, statistical/experimental caveats → `notes/03` (including pre-clustering, S14 and timeout ceilings).
- 26–30 code locations, equation mapping, paper/code consistency, code-only details, defaults → `notes/04` (including package/test qualification).
- 31 contribution → `notes/01` and `notes/07` (narrowly bounded; no universal-superiority claim).
- 32–36 biological, statistical, computational assumptions, known limitations, failure cases → `notes/06` (with inference labels and unresolved conflicts).

`notes/00_SOURCE_MAP.md` independently records this same coverage map and the six global unresolved items.

## Completion criteria audit

All `RESEARCH_PLAN.md` completion criteria are satisfied: source map, research question, method architecture/equations, experiments, XLSX schema and mappings, paper↔code map, classified assumptions/limitations, conflict register, evidence matrix, presentation brief, reviewer pass, unsupported-claim handling, and explicit unresolved-issue list.

