# Methods Validation: main paper vs supplement vs implementation

## Scope, versions, and decision rule

This validation independently compared the local main-paper extraction (`phyclone.pdf`), supplement (`btaf344_supplementary_data/supp.pdf`), and the checked-out repository. The paper benchmarks **PhyClone 0.7.0** (main paper §2.4.2, p.5; `.agent_workspace/paper/phyclone_layout.txt:347-356`). The repository is **0.8.0**, commit `27383246c1aff7b1d62c02662017bd61bfdfbc33` (`PhyClone/pyproject.toml:5-18`; local tag/HEAD inspection). Where relevant, the local Git tag `0.7.0` was also inspected to separate paper-era behavior from later drift.

Classification meanings:

- `EXACT`: the mathematical/algorithmic behavior is directly represented in code, allowing ordinary numerical discretization.
- `APPROXIMATE`: the same intended construct is implemented with a material numerical or heuristic approximation.
- `PAPER_ONLY`: described in paper/supplement but not exposed by this checkout.
- `CODE_ONLY`: current behavior not described by paper/supplement.
- `ADDITIONAL_IMPLEMENTATION_DETAIL`: implementation choice consistent with, but more specific than, the publications.
- `POSSIBLE_MISMATCH`: evidence does not justify claiming equivalence, or source contains an unresolved correctness concern.

## Executive verdict

The central method is faithfully represented: the PyClone allele-count likelihood; copy-number and tumour-content correction; CRP clustering; rooted-forest/tree construction; descendant-sum cellular prevalence; grid-based collapsed likelihood; bottom-up SMC; admissible-order Particle Gibbs; pre-cluster atoms; and the two fixed-node-count auxiliary moves all have direct code counterparts.

Four claims require prominent qualification:

1. **Outlier marginalization is not the direct grid analogue of the published single Uniform integral.** This discrepancy exists in both tag `0.7.0` and current `0.8.0`, so it cannot be dismissed as post-paper version drift.
2. **Current 0.8.0 bootstrap sampling with active outliers uses branch probabilities inconsistent with its own `log_p` proposal density.** The `0.7.0` implementation used consistent intervals, and the paper benchmarks used the semi-adapted kernel, so this is a current optional-kernel issue rather than an explanation of the reported benchmark results.
3. **Subtree PG is publication-described and implemented, but both 0.7.0 and 0.8.0 source retain an explicit TODO questioning whether the random subtree-selection term is missing.** It is disabled by default (`subtree_update_prob=0`).
4. **The current CLI and direct Python API have materially different defaults.** They must not be merged into one “default parameters” list, and neither should replace the explicit v0.7.0 benchmark settings.

## Cross-source validation matrix

| Method component | Classification | Independent validation and evidence |
|---|---|---|
| Input observations | `EXACT` with `CODE_ONLY` filtering | Paper requires per-SNV allele counts, CN information and tumour content (main §2.2, p.3; layout `181-190`). Code builds one multi-sample likelihood grid per mutation (`data/pyclone.py:17-79,355-403`). Current preprocessing additionally removes `major_cn=0`, duplicate mutation IDs, and mutations absent from any sample (`data/pyclone.py:197-260`), which the method text does not state. |
| Missing tumour content / error rate | `ADDITIONAL_IMPLEMENTATION_DETAIL` | The publications treat tumour content as an input and define sequencing error (supplement S1.1, pp.1-2; layout `16-22`). Code silently supplies tumour content `1.0` and error rate `1e-3` when columns are absent (`data/pyclone.py:263-268`). This operational convenience increases the risk of an unintended purity assumption. |
| PyClone expected VAF | `EXACT` | Supplement S1.1 defines the normal/reference/variant mixture and the CN-weighted `xi(G,rho_bar,t)` (pp.1-2; layout `13-76`). Code uses masses `(1-t, t(1-f), tf)`, weights by CN and genotype-specific mutant fraction, normalizes, and mixes plausible genotypes (`utils/math_utils.py:179-244`). |
| Binomial / Beta-Binomial likelihood | `EXACT` | Supplement S1.1 specifies both densities and Beta-Binomial mean/precision parameterization (p.1; layout `50-76`). Code evaluates either density across a `linspace(0,1,L)` CCF grid (`data/pyclone.py:365-403`; `utils/math_utils.py:159-166,179-244`). |
| Major-copy genotype prior | `EXACT` | Supplement S1.2 enumerates mutation-before-CNA and mutation-after-CNA cases with equal weights (p.2; layout `82-97`). `get_major_cn_prior` constructs these cases and sets `log_pi=-log(number of cases)` (`data/pyclone.py:324-352`). |
| Mutation partition / CRP | `EXACT` up to a state-independent normalizer | Supplement S1.3 gives `p(b|alpha) proportional to alpha^|b| product_b (|b|-1)!` (p.3; layout `144-152`). `FSCRPDistribution.compute_CRP_prior` implements exactly these state-dependent terms (`tree/distributions.py:56-65`). |
| Alpha hyperparameter update | `ADDITIONAL_IMPLEMENTATION_DETAIL` | Supplement S2.2 says alpha is resampled between iterations but does not give its hyperprior (p.9; layout `513-519`). Code defaults to updating alpha with `GammaPriorConcentrationSampler(0.01,0.01)` (`run.py:382-392`; update at `run.py:292-313`; sampler formula in `mcmc/concentration.py:11-60`). |
| Forest prior and dummy root | `EXACT`, after final-score adjustment | Supplement S1.3 samples a uniform rooted forest and attaches all forest roots to dummy root `r`; its Cayley normalizer is `1/(|b|+1)^(|b|-1)` (pp.2-3; layout `99-156`). Code represents the dummy root explicitly and excludes it from biological node counts (`tree/tree.py:22-24,64-69,92-102`); `FSCRPDistribution.log_p` contains the Cayley term (`tree/distributions.py:43-54`). |
| Single-root preference | `EXACT` | Supplement S1.3.1 replaces the unadjusted final topology prior by a `C=1000` penalty per additional subroot and subtree-count normalization (pp.3-4; layout `158-188`). `log_p_one` uses `c_const=1000`, the root-count term and subroot Cayley counts (`tree/distributions.py:12-14,67-121`). Therefore “uniform tree prior” is incomplete for final states; only the pre-adjustment forest prior is uniform. |
| Child-order multiplicity correction | `ADDITIONAL_IMPLEMENTATION_DETAIL` | Code subtracts `sum_v log(outdegree(v)!)` from both prior scores (`tree/base.py:93-100`; `tree/distributions.py:52,87`). This corrects multiplicity of ordered internal graph/proposal representations; the paper does not state this implementation-level factor separately. No contrary publication equation was found. |
| Dirichlet prevalence prior | `EXACT` for `kappa=1`; `PAPER_ONLY` for arbitrary kappa | Supplement S1.3 writes symmetric `Dirichlet(kappa 1)` and S1.5 specializes its fast cumulative recursion to `kappa=1` (pp.2-5; layout `105-125,265-289`). Code has no user-facing kappa: every node grid starts with a uniform `-log(L)` prior and `compute_log_S` performs the kappa=1 cumulative sum (`tree/base.py:27-35`; `tree/tree_node.py:11-13,59-69`; `tree/utils.py:7-25`). Thus the implemented model is the stated kappa=1 case, not a general Dirichlet-kappa implementation. |
| Dummy-root prevalence dimension | `EXACT`, publication typo resolved | Main paper says `|b|+1=|V|`, consistent with a prevalence component for the empty root (main §2.2, p.3; layout `209-212`). Supplement S1.3 first defines post-attachment `V=V' union {r}` but then says `|b|=|V|` (p.3; layout `108-124`), an internal off-by-one notation conflict. Code gives the dummy root the same grid prior and evaluates the completed tree at root mass 1 (`tree/tree.py:22-24`; `tree/base.py:27-35`; `tree/distributions.py:151-163`). **Resolved:** the supplement prose equality is a notation error; main paper plus implementation support `|V|=|b|+1` when `V` includes the dummy root. |
| Clonal to cellular prevalence | `EXACT` | Both publications define cellular prevalence at node `v` as the sum of clonal masses in its descendant subtree (main §2.2, p.3; supplement S1.3, p.3, layout `126-143`). Code convolves child `R` arrays, cumulatively integrates allowable child mass, and multiplies by the node emission (`tree/tree_node.py:59-69`; `tree/utils.py:7-57`). Output backtracking computes clonal mass as parent CCF minus summed child CCF (`process_trace/map.py:24-40,127-157`). |
| Multi-sample prevalence | `EXACT` | Supplement S1.3 shares the partition/tree but uses a prevalence dimension per region/sample (p.3; Fig. S2). Code likelihood grids have shape samples by grid points and performs each convolution independently across sample dimensions (`data/pyclone.py:375-403`; `tree/utils.py:39-57`). |
| Collapsed likelihood / DP | `APPROXIMATE` as explicitly stated | The publications integrate node clonal prevalence, change to cellular prevalence, discretize to a finite grid, and use child convolutions plus a cumulative sum, returning `R_r(1)` (supplement S1.4-S1.5, pp.4-5; layout `190-298`). Code is the direct kappa=1 grid analogue (`tree/tree_node.py:43-69`; `tree/utils.py:7-68`; completed score at `tree/distributions.py:151-163`). Approximation is solely the finite CCF grid and floating-point convolution, not a different inferential target. |
| Complexity claim | `POSSIBLE_MISMATCH` in prose, resolved by supplement | Main paper states the marginal likelihood is computed in `O(|V|^2)` (main §2.2.1, p.3; layout `173-179`). Supplement gives `O(V(NL + CSL^2))`, explicitly depending on mutations, samples, grid size, and maximum out-degree (S1.5, p.5; layout `292-298`). Code indeed performs per-node/per-sample grid convolution, direct below grid size 1000 and FFT otherwise (`tree/utils.py:28-68`). **Resolved for reporting:** cite the supplement expression as the detailed bound; do not present the main-paper `O(|V|^2)` as a general runtime bound without assumptions that the paper does not state. |
| Pre-clustering | `EXACT` | Main §2.2.2 says members of an input cluster cannot split, while distinct preclusters may merge in one inferred node (p.3; layout `180-199`). Code sums all member log-likelihood grids into one `DataPoint`, so PG moves that atom as a unit while multiple atoms may occupy a node (`data/pyclone.py:82-115`; tree node addition at `tree/tree_node.py:35-50`). |
| Bottom-up SMC state space | `EXACT` | Main §2.3 and supplement S1.6 allow adding a datum to an existing forest root or creating a new root with any possibly empty subset of current roots as children (main pp.3-4, layout `246-283`; supplement p.6, layout `331-389`). Current bootstrap, fully adapted and semi-adapted kernels construct those states; semi-adapted enumerates existing-root/outlier options and samples one new-root child set (`smc/kernels/semi_adapted.py:31-130`). |
| Semi-adapted proposal | `EXACT` | Publications describe a 50/50 structural choice, probability-scored existing assignments, and a randomly selected child subset for a new node (supplement S1.6.2, p.6). Code uses the same structure (`smc/kernels/semi_adapted.py:31-75,77-130`). It is both the current CLI default and the v0.7.0 benchmark kernel (`cli.py:316-326`; main §2.4.2, p.5). |
| Admissible-order Particle Gibbs | `EXACT` | Supplement S1.6.3 defines `Sigma(T)`, descendant-before-parent order, within-node shuffles, sibling bridge shuffles, and root interleaving of outliers (p.7; layout `393-421`). Code samples this ordering and runs conditional SMC retaining the current path (`smc/utils.py:98-135`; `mcmc/particle_gibbs.py:22-49`; `smc/samplers/conditional.py:15-121`). |
| Burn-in | `ADDITIONAL_IMPLEMENTATION_DETAIL` | Code uses ordinary/unconditional SMC during burn-in, applies the auxiliary moves, discards that trace, and initializes the main chain from the highest `log_p_one` tree seen rather than the last state (`run.py:316-369`; `smc/samplers/unconditional.py`). This is a heuristic initialization procedure, not posterior sampling, and is not derived in the method equations. |
| Data-point reassignment | `EXACT` behavior, `POSSIBLE_MISMATCH` correctness note | Main §2.3.2 says reassignment occurs only if removing a datum does not empty the node, hence topology/node count stay fixed (p.4; layout `259-277`). Code does precisely this and scores all existing nodes plus optional outlier (`mcmc/gibbs_mh.py:22-66`). However the class has an explicit TODO asking whether the special no-empty-node condition makes the update valid (`mcmc/gibbs_mh.py:7-11`). The intended move matches the paper; formal transition-kernel correctness remains unresolved in source. |
| Prune-regraft move | `EXACT` | Main §2.3.2 describes detaching a subtree and Gibbs-sampling an attachment among all nodes (p.4). Code detaches a randomly chosen biological subtree, considers every remaining node and the dummy root, and samples using the full score with the attachment multiplicity term (`mcmc/gibbs_mh.py:69-129`). Node count and cluster assignment are unchanged. |
| Subtree PG | `POSSIBLE_MISMATCH` | Supplement S1.6.4 says a mutation is sampled, its parent becomes the update root, and full-tree likelihood corrects final weights (p.7; layout `423-438`). Code follows this outline (`mcmc/particle_gibbs.py:52-110`) but explicitly asks whether random node-choice probability needs an additional term (`87-88`). The TODO is also present in tag `0.7.0` (`0.7.0:phyclone/mcmc/particle_gibbs.py`, function `_correct_weights`, lines 83-85). Default probability is 0 in both versions, so the uncertain path is off unless explicitly enabled (`run.py:53,275-278`). |
| Outlier state structure | `EXACT` at model level | Main §2.2.3 and supplement S1.7 define a binary outlier indicator: non-outliers enter the tree; outliers have an independent PyClone likelihood and Uniform cellular-prevalence prior (main p.3, layout `201-237`; supplement pp.7-8, layout `440-472`). Code maintains a dedicated outlier bucket, adds the Bernoulli prior term, and excludes outliers from the tree DP (`tree/distributions.py:124-204`). It does **not** infer a deletion/loss edge. |
| Outlier Uniform marginal | `POSSIBLE_MISMATCH` — unresolved | The publication formula is one integral, `integral_0^1 f(x|rho) d rho` (main §2.2.3, p.3; supplement S1.7, pp.7-8). For an `L`-point grid the direct rectangular analogue is `L^-1 sum_i f_i`. Code first cumulative-sums `f_i/L` through each endpoint `j`, then averages those cumulative values over `j`, yielding `L^-2 sum_j sum_{i<=j} f_i` (`data/base.py:29-34`; consumed at `tree/distributions.py:186-203`). A constant likelihood should integrate to 1, but code gives `(L+1)/(2L)` per sample. This topology-dependent factor is repeated per outlier and can change posterior outlier odds. The same computation is present in paper-era tag `0.7.0` (`0.7.0:phyclone/data/base.py:29-34`). No derivation or focused outlier-marginal test was found. |
| Data-informed loss/outlier prior | `APPROXIMATE` plus extra detail | Supplement S1.7.1 chooses a truncal cluster by per-sample maximum CCF/tie-breaking mean and flags nontruncal clusters whose chromosome-concentration null has `p<0.01`, using 10,000 draws and low/high priors 0.0001/0.4 (p.8; layout `474-491`). Code implements these elements (`data/cluster_outlier_probabilities.py:9-67,105-151`) but ignores genomic position despite the supplement listing it as input, skips clusters smaller than 4, and additionally requires expected/observed unique chromosomes `>1` (`29-66`). Missing `chrom`, `cellular_prevalence`, or `sample_id` causes fallback to the global prior (`data/pyclone.py:148-164`). |
| Cluster-level outlier behavior | `ADDITIONAL_IMPLEMENTATION_DETAIL` | One precluster is one `DataPoint`; its emission is the sum of member log-likelihoods and its outlier/non-outlier log prior is multiplied by cluster size (`data/pyclone.py:82-115,184-194`). Therefore the entire input cluster is marked outlier or retained together. This is consistent with the no-splitting precluster rule, but the publication writes the outlier indicator per mutation and does not spell out this all-or-none consequence. |
| Bootstrap with active outliers | `POSSIBLE_MISMATCH` in 0.8.0, version-resolved | Current proposal density assigns 0.1 to outlier and `(1-0.1)/2=0.45` to each structural branch (`smc/kernels/base.py:107-121`; `smc/kernels/bootstrap.py:44-84`). Current sampling intervals instead yield 0.1 outlier, 0.35 existing, and 0.55 new (`bootstrap.py:88-104`) because the second threshold is `_half_val` rather than `outlier_prob + _half_val`. Tag 0.7.0 used intervals `[0,0.45)`, `[0.45,0.9)`, `[0.9,1)` consistently (`0.7.0:phyclone/smc/kernels/bootstrap.py:62-98`). **Resolved as version drift:** the mismatch is current 0.8.0 only; it does not affect paper benchmarks because they used semi-adapted, but current bootstrap+outlier inference should not be trusted without correction/testing. |
| Reported `joint-likelihood` / MAP topology | `ADDITIONAL_IMPLEMENTATION_DETAIL` and naming caveat | Paper §2.4.2 says the final tree is selected by MAP joint-likelihood (p.5). Code stores `log_p_one`, which includes CRP/tree/outlier priors plus marginalized data likelihood, under HDF5 field name `log_p`; default MAP selects its maximum (`utils/utils.py:55-70`; `utils/save_hdf5.py:83-111`; `process_trace/process_trace.py:27-58`). It is an unnormalized joint posterior score, not a likelihood-only quantity. |
| Reinstating prevalences | `PAPER_ONLY` for sampling; `EXACT` for MAP | Main §2 says collapsed prevalences may be reinstantiated by MAP **or sampling** (p.2; layout `89-90`). Current output code only exposes max-product/grid backtracking for node CCF and clonal prevalence (`process_trace/map.py:6-40,43-157`; called by `process_trace/process_trace.py:272-303`). No posterior prevalence sampler was found in the checkout. |

## Parameters: benchmark vs paper-era defaults vs current defaults

These are three different statements and must remain separate.

### Published benchmark configuration (`STATED`)

PhyClone 0.7.0: four independent chains, 100 burn-in iterations, 5000 MCMC iterations, 100 particles, Beta-Binomial density, semi-adapted proposal; loss-enabled runs set `--assign-loss-prob` with low/high priors 0.0001/0.4; final topology selected by MAP joint score (main §2.4.2, p.5; layout `347-356`).

### Tag 0.7.0 operational defaults (`IMPLEMENTED`)

The tag's CLI agrees on burn-in 100, iterations 5000, particles 100, Beta-Binomial, semi-adapted, grid 101, precision 400, alpha initial 1 with update, outlier probability 0, resampling threshold 0.5, subtree probability 0, and one chain unless overridden (`0.7.0:phyclone/cli.py`, run options lines 145-330). Thus the benchmark explicitly overrode only chain count and enabled loss assignment where applicable. The direct `run()` precision default was already 1.0 rather than CLI 400 (`0.7.0:phyclone/run.py:28-55`).

### Current 0.8.0 defaults (`IMPLEMENTED`)

Current CLI: burn-in 1000, iterations 10000, one chain, grid 101, particles 100, precision 400, Beta-Binomial, semi-adapted, outlier probability 0, alpha initial 1 with update, one reassignment and one prune-regraft sweep, subtree probability 0, and ESS resampling threshold 0.5 (`cli.py:243-447`). Direct `run()` instead defaults to burn-in 100, iterations 5000 and precision 1.0 (`run.py:31-57`). `load_data()` alone defaults outlier probability to `1e-4` (`data/pyclone.py:17-29`), but both public pathways normally pass their own value.

There is also a current CLI/API activation divergence: CLI callbacks change global outlier probability 0 to `1e-4` when either loss-prior mode is requested (`cli.py:202-217`), whereas direct `run(assign_loss_prob=True, outlier_prob=0)` decides that outlier modelling is inactive before loading cluster priors (`run.py:59-85`).

## Conflict register

### C1 — Supplement prevalence-vector dimension

- **Claim:** whether dummy root has a prevalence component.
- **Source A:** main §2.2 says `|b|+1=|V|` (p.3).
- **Source B:** supplement S1.3 prose says `|b|=|V|` after defining `V=V' union {r}` (p.3; layout `108-124`).
- **Code:** dummy root has a uniform grid prior and completed score fixes its cellular prevalence/mass at 1 (`tree/tree.py:22-24`; `tree/base.py:27-35`; `tree/distributions.py:151-163`).
- **Status:** **RESOLVED** as an off-by-one notation error in supplement prose; use `|b|` biological nodes plus one dummy-root component.

### C2 — Marginalization complexity

- **Claim:** runtime is `O(|V|^2)`.
- **Source A:** main §2.2.1, p.3.
- **Source B:** supplement S1.5 gives `O(V(NL+CSL^2))`, p.5.
- **Code:** mutation-grid aggregation and child convolutions depend on `N,S,L,C` (`tree/tree_node.py:43-69`; `tree/utils.py:28-68`).
- **Status:** **RESOLVED for synthesis:** the supplement is the complete parameterized complexity statement; main-paper shorthand must be qualified.

### C3 — Published outlier integral vs implemented computation

- **Claim:** an outlier is marginalized under one Uniform cellular-prevalence integral.
- **Publication:** main §2.2.3 and supplement S1.7.
- **Code:** triangular double sum in `DataPoint.__init__` (`data/base.py:29-34`), in both 0.7.0 and 0.8.0.
- **Possible explanation:** reuse of the tree residual-mass cumulative operator, but this would add an undocumented latent integration and fails the constant-integrand normalization check.
- **Status:** **UNRESOLVED; likely implementation mismatch.**

### C4 — Current bootstrap proposal sampling vs `log_q`

- **Claim:** bootstrap chooses outlier/existing/new according to its recorded proposal density.
- **Source A:** `log_p` assigns 0.1/0.45/0.45 (`smc/kernels/base.py:118-121`; `smc/kernels/bootstrap.py:44-84`).
- **Source B:** current `sample()` realizes 0.1/0.35/0.55 (`smc/kernels/bootstrap.py:88-104`).
- **Historical check:** tag 0.7.0 realizes 0.1/0.45/0.45.
- **Status:** **RESOLVED as a current 0.8.0 regression, still operationally unfixed.** It is outside the paper's semi-adapted benchmark path.

### C5 — Subtree PG correction

- **Claim:** full-tree likelihood correction makes subtree PG target the posterior.
- **Publication:** supplement S1.6.4, p.7.
- **Code:** follows the described correction but asks whether subtree selection probability is missing (`mcmc/particle_gibbs.py:87-110`; same TODO in tag 0.7.0).
- **Status:** **UNRESOLVED.** Disabled by default; do not state formal correctness as verified.

### C6 — Current CLI vs Python API defaults

- **Claim:** “the current default” is one parameter set.
- **Source A:** CLI 1000/10000/400 for burn-in/iterations/precision (`cli.py:260-395`).
- **Source B:** direct API 100/5000/1.0 (`run.py:31-53`).
- **Status:** **RESOLVED by interface qualification:** report defaults per entry point, not as one package-wide set.

## High-risk interpretation constraints for the Integrator

1. Describe mutation loss as an **outlier accommodation mechanism**, not explicit evolutionary loss-edge inference.
2. State that purity and CN are fixed inputs to the likelihood; PhyClone does not infer them.
3. State that preclusters cannot split and are also all-or-none under the implemented outlier state.
4. State that current exported prevalences are conditional grid MAP reconstructions, not posterior means or credible intervals.
5. Keep the nominal uniform forest prior separate from the `C=1000` final single-root preference.
6. Quote the supplement's parameterized DP complexity, and treat the main `O(|V|^2)` phrase as shorthand.
7. Do not generalize benchmark v0.7.0 parameters into current 0.8.0 CLI defaults.
8. Carry C3 and C5 as unresolved method risks; carry C4 as a confirmed current-version implementation regression outside the reported benchmark kernel.

## Validation limits

- No source outside `/bip8_disk/boyu114/main_work/research/phyclone_research` was read.
- The comparison is static plus algebraic. Dependency/Python-version limitations recorded by the Code Analyst prevented broad runtime test execution; no failed import is treated as an algorithm failure.
- The repository contains tag 0.7.0, enabling targeted version checks, but the exact paper experiment artifacts were not regenerated here.

