# Independent reviewer report

## Verdict

**PASS WITH CORRECTIONS.** The eight canonical notes are unusually well cross-linked and preserve the major paper/code/XLSX conflicts. The high-risk claims were rechecked against `phyclone.pdf`, `supp.pdf`, the supplied cell exports, and the current source. One high-severity experimental-design statement is wrong/ambiguous, and several medium/low issues should be corrected before presentation or final handoff.

The two major implementation warnings are supported: the published outlier model is a single Uniform integral but `data/base.py:29-34` computes a triangular cumulative-grid expression in both the paper-era and current code; and current 0.8.0 bootstrap sampling with active outliers has realized branch probabilities 0.1/0.35/0.55 while `log_p` records 0.1/0.45/0.45 (`smc/kernels/base.py:118-121`, `bootstrap.py:44-104`). The benchmark used semi-adapted proposals, so neither finding invalidates the reported benchmark by itself. The subtree-PG TODO is also real and the default is zero.

## Findings requiring action

### R1 — HIGH — shared-preclustering claim includes PhyloWGS

- **Target:** `notes/03_EXPERIMENTS_RESULTS.md:5`; `notes/06_ASSUMPTIONS_LIMITATIONS.md:33`; related analyst packet `.agent_workspace/paper/assumptions.md:61`.
- **Problem:** “the same pre-clusters were supplied to downstream methods” and “all synthetic downstream methods share PyClone-VI pre-clusters” can be read as including PhyloWGS. The main paper §2.4.2 p.5 explicitly lists the recipients as CONIPHER, Pairtree, Orchard, fastBE, and PhyClone; PhyloWGS is not in that list. The validator packet correctly says “all five later-stage methods” (`.agent_workspace/experiments/experiment_validation.md:7`).
- **Why it matters:** It changes the fairness interpretation of TSSB-Low and the runtime/accuracy comparison with PhyloWGS. The notes otherwise correctly call PhyloWGS “non-preclustered” at `notes/01_PAPER_BIG_PICTURE.md:69`.
- **Exact correction:** Replace with: “Synthetic data were pre-clustered with PyClone-VI; the pre-clustered inputs were supplied to CONIPHER, Pairtree, Orchard, fastBE, and PhyClone. PhyloWGS was not listed as receiving these pre-clusters and should be treated as the non-preclustered comparator.” In `notes/06`, replace “Synthetic methods share PyClone-VI pre-clusters” with “The five later-stage methods listed above share PyClone-VI pre-clusters; the TSSB-Low PhyloWGS comparison is not under that common preprocessing.”

### R2 — MEDIUM — timeout wording overstates what is absent

- **Target:** `notes/06_ASSUMPTIONS_LIMITATIONS.md:29` (“Timeout handling is absent from the checkout”); contrast `notes/00_SOURCE_MAP.md:113` and `.agent_workspace/experiments/experiment_validation.md:10`.
- **Problem:** The application checkout does implement a runtime limit (`--max-time` in `cli.py`, timer checks in `run.py:289` and `run.py:359`). What is absent is the paper’s benchmark/evaluation timeout preprocessing and missing-value/penalty pipeline, not all timeout handling.
- **Exact correction:** “The checkout has an application-level `--max-time` stop, but the benchmark timeout preprocessing and missing-value/penalty handling are absent; the paper’s 48-hour results therefore cannot be reproduced from this repository.”

### R3 — MEDIUM — evidence matrix labels CN-error flatness as established

- **Target:** `notes/05_EVIDENCE_MATRIX.md:25` claim column.
- **Problem:** The row is worded as “condition-specific flatness is established,” then qualifies it as unresolved. S14 contains 450 rows/method but no per-row 0/0.1/0.2 perturbation label, so only the pooled ranking is independently supported. The authors’ “minimal impact” statement is in the paper, but its condition-specific numerical trend cannot be reconstructed from the workbook.
- **Exact correction:** Change the claim to “CN-error pooled ranking favors PhyClone in AD; the paper reports minimal impact across perturbation levels, but condition-specific flatness is not independently reconstructible from S14 because error-level labels are absent.” Keep confidence `MEDIUM`.

### R4 — MEDIUM — packet-level statistics interpretation contradicts the primary-source decision rule

- **Target:** `.agent_workspace/xlsx/xlsx_analysis.md:146-149`, especially line 149.
- **Problem:** It says flags with `p<0.05` and `significant=0` “evidently reflect a multiple-comparison threshold/correction” and that the correction/alpha is unidentified. The main paper §2.4.3 p.6 explicitly declares `p<0.01` for both Friedman gating and pairwise Nemenyi decisions, and `.agent_workspace/experiments/experiment_validation.md:9` independently confirms every supplied flag agrees with `p<0.01`. This packet statement is inconsistent with the canonical notes (`notes/03:20`, `notes/05:40`).
- **Exact correction:** Replace line 149 with: “The declared decision threshold is `p<0.01` (main §2.4.3), so values such as 0.01004, 0.01144, and 0.04278 are correctly marked non-significant under the stated rule. The workbook does not expose the underlying rank/block preprocessing, and some omnibus p-values are not exactly reproducible from visible cells.” Do not infer an undocumented multiplicity correction.

### R5 — MEDIUM — presentation says memory is high despite unknown units/incomplete cells

- **Target:** `notes/07_PRESENTATION_BRIEF.md:19`; related `notes/07:74-77` and `notes/03:155`.
- **Problem:** “runtime/memory are high” is categorical. Runtime is labelled seconds only for the Supplement Fig. S11 plot; XLSX memory units are absent, and Pairtree resource columns are heavily missing (e.g. Orchard memory 5/576 and Pairtree 199/576 nonblank). The supplied means support a resource trade-off, not a unit-independent claim of high memory.
- **Exact correction:** “Recorded runtime is often materially higher than fastBE and some other baselines; memory is also higher in several complete-case summaries, but XLSX memory units and some resource cells are missing.” Keep the stronger runtime examples on Slide 8, where seconds are established for the plotted runtime data.

### R6 — LOW — environment/test sentence attributes missing packages to Python 3.10

- **Target:** `notes/04_CODE_MAPPING.md:56`.
- **Problem:** “Python 3.10 lacks required `numba`, `networkx` or `xxhash`” conflates interpreter version with packages absent from the environment. The repository declares Python 3.12, while the observed failures were import/dependency/environment failures.
- **Exact correction:** “`test_root_term` passed all eight tests. Other selected modules could not be collected in the available Python 3.10 environment because required packages (`numba`, `networkx`, `xxhash`) were unavailable; the repository declares Python ≥3.12. No import failure is treated as an algorithm failure.”

## Confirmed high-risk quantitative and implementation checks

These checks found no additional correction to the canonical notes:

- FS-CRP loss: S4 gives 20% AD means 0.95570 (PhyClone) and 0.71486 (PhyClone-N); S19 gives pooled AD difference 0.1239600297 and `p=0.001`. S19 has no `significant` column, so the notes correctly rely on the paper’s `p<0.01` rule.
- TSSB-Low: S2 complete-case means are V/AD 0.99496/0.98350 and mean times about 253.26 versus 37,562.90 seconds for PhyClone/PhyloWGS; S16 marks all PhyClone-vs-comparator AD pairs significant, with the largest reported p-value 0.0006358823.
- TSSB-High/Pairtree/CONIPHER-NN: S18/S21/S23 support “no significant competitor wins PhyClone in AD,” with CONIPHER’s TSSB-High V-measure exception. The S23 fastBE–PhyClone AD row really conflicts with raw S6 means (`+0.00095026` in S23 versus raw nonblank difference `-0.01723008`); the non-significant decision is unchanged. The conflict is correctly retained in `notes/03:98` and `notes/05:47`.
- CONIPHER-noise: S7/S25 support the top AD group PhyClone/CONIPHER/fastBE and their separation from Orchard/Pairtree; the notes do not turn non-significance into equivalence.
- CN-error: S14/S27 support pooled AD ranking only. The missing error-level label caveat is correct.
- HGSOC: S8–S13 reproduce Supplement Table S1 after rounding; patient 3 is uniquely best on both point metrics in WGS and WGS+targeted. The topology/loss statement requires the paper figure, not XLSX alone, and the notes say so.
- The paper/supplement/code version boundary is correctly preserved: reported benchmark v0.7.0 versus inspected code v0.8.0. CLI and direct-API defaults are correctly separated.
- The root-dimension and complexity conflicts are handled correctly by distinguishing the supplement’s off-by-one notation and the detailed `O(V(NL+CSL^2))` bound from the main-paper shorthand `O(|V|^2)`.

## Coverage of all 36 required questions

All questions have an answer or an explicit evidence ceiling. The coverage is complete by topic:

| Questions | Canonical note | Review result |
|---|---|---|
| 1–4 motivation, importance, prior limits, difficulty | `notes/01` | Answered with stated/inferred boundary |
| 5–17 model, inputs, variables, likelihood, priors, prevalence, inference, preprocessing, outliers, outputs | `notes/02` | Answered; implementation conflicts and version qualifiers retained |
| 18–25 experiment aims, datasets, generation, baselines, metrics, results, XLSX support, caveats | `notes/03` | Answered; fix R1 and retain S14/S23/timeout ceilings |
| 26–30 code locations, equation mapping, consistency, code-only details, defaults | `notes/04` | Answered; fix R2/R6 wording |
| 31 contribution | `notes/01` and `notes/07` | Narrowly stated; no universal-superiority overclaim |
| 32–36 biological, statistical, computational assumptions, known limits, failure cases | `notes/06` | Answered; fix R1/R2/R3 and preserve inference labels |

The completion contract is met after the six corrections above. No missing primary question requires new source collection.

## Presentation and claim ceiling

The presentation brief has the right focus: problem → model → inference → loss-aware exclusion → synthetic evidence → HGSOC case → limitations. Keep the following boundaries visible during delivery:

- “Outlier” means tree-incompatibility accommodation, not deletion-edge or mechanistic loss inference.
- “No significant competitor advantage” is not equivalence or universal superiority.
- The TSSB-Low PhyloWGS runtime comparison is additionally a preprocessing comparison because PhyloWGS was not listed among the five precluster recipients.
- HGSOC evidence is three patients, with ground-truth-subset pruning/collapse; it is descriptive, not clinical validation.
- Memory units and CN-error level-specific trends are not supported by the supplied XLSX.

## Recommended disposition

Apply R1 before finalizing the experiment/assumptions notes, apply R2–R6 as wording and packet consistency fixes, and retain the unresolved outlier-marginal, subtree-PG, S23-direction, Friedman-reproduction, S14-label, and evaluation-pipeline items exactly as unresolved. The evidence model and severity boundaries are otherwise ready for handoff.
