# Paper Analyst unresolved items and cross-validation requests

## Required resources that are in workspace but outside this role's read scope

These are not missing globally; they are delegated to other analysts under the plan.

1. **Supplement equations/algorithm.** Verify PyClone emission, FS-CRP prior mass, `kappa`, DP marginalization, SMC targets/weights and outlier implementation against `btaf344_supplementary_data/supp.pdf`.
2. **XLSX mapping.** Map Figs 2–5 and supplementary Figs/Tables to exact workbook sheets/ranges; recover exact values/P-values/ranks/timeouts.
3. **Code mapping.** Confirm paper equations, loss probability semantics, pre-cluster indivisibility/merge, output tree selection, prevalence re-instantiation and current defaults in `PhyClone/`.

## Specific unresolved or potentially conflicting claims

### U01 — Pairtree dataset count

[STATED] §2.4.1.3 (p.5) lists `K` 4 levels × `M` 5 × `D` 3 × `N` 3 × 4 replicates, which naïvely gives 720, but states total 576 datasets.

Status: **UNRESOLVED**. Likely some parameter combinations were absent/invalid; supplement or XLSX must identify exclusions.

### U02 — RRE direction/formula

[STATED] Main paper describes RRE qualitatively but does not explicitly state direction in the prose excerpt; likely lower is better by “error,” but exact definition must come from supplement/evaluation code.

Status: **UNRESOLVED**.

### U03 — `O(|V|^2)` dependence

[STATED] Main paper says DP computes marginalized likelihood in `O(|V|^2)` (§2.2.1, p.3), but does not specify other factors (samples, grid size, mutations).

Status: **UNRESOLVED** as a complete runtime complexity claim; do not repeat as total algorithm complexity.

### U04 — Uniform forest prior and empty root

[STATED] §2.1 says directed rooted forests are uniformly sampled and converted by adding empty root; §2.2 uses `|b|+1=|V|` Dirichlet dimension. The exact prior normalization and empty-root prevalence interpretation are absent.

Status: **UNRESOLVED**.

### U05 — Outlier units

[STATED] Main method defines per-SNV `nu_n`/`o_n`, whereas HGSOC result describes removing two SNV clusters. Whether pre-clustered inputs share one outlier indicator or individual SNVs can diverge must be checked in supplement/code.

Status: **UNRESOLVED / POSSIBLE PAPER–CODE DETAIL**.

### U06 — Benchmark “defaults”

[STATED] §2.4.2 gives PhyClone v0.7.0 benchmark parameters and labels 0.0001/0.4 as accompanying default outlier probabilities. It does not establish the defaults of the workspace code version.

Status: **UNRESOLVED until code analyst maps version and CLI**.

### U07 — Posterior metric scoring fairness

[STATED] All LPR method solutions were scored using PhyClone marginalization “to not bias” results (§2.4.3, p.6).

[INFERRED] A common evaluator improves consistency but may still align structurally with PhyClone assumptions; evaluation code/supplement needed.

Status: **UNRESOLVED caveat**, not an asserted conflict.

### U08 — Timeout handling

[STATED] 48-h wall-clock cap per method/trial (§2.4.2, p.5); main paper does not say how timeouts enter plots/tests.

Status: **UNRESOLVED**.

### U09 — CN robustness explanation

[STATED] Authors hypothesize minimal CN-error impact arises from common PyClone-VI preprocessing and genotype uncertainty (§3.4, p.7).

Status: **UNRESOLVED causal mechanism**; retain wording “authors believe/likely.”

### U10 — Multi-sample collapsed integral

[STATED] Main equations use one sample for uncluttered notation and say each region gets a Dirichlet vector (§2.2, p.3). Exact factorization/integration across samples not printed.

Status: **UNRESOLVED pending Supplement**.

## Skill-procedure constraint

The `bioinformatics-knowledge` skill normally requires lab/current/historical searches outside this directory and at least two additional evidence workers. The assigned Paper Analyst scope explicitly prohibits any read outside `/bip8_disk/boyu114/main_work/research/phyclone_research`, and the research plan already delegates independent paper/supplement/XLSX/code roles within limited concurrency. No external path was probed and no extra worker was spawned from this role. Thus the skill's multi-source/multi-worker gate is **NOT SATISFIED**, by deliberate scope compliance; this does not reduce the completeness of the main-paper extraction but means no lab/historical claims are made here.

