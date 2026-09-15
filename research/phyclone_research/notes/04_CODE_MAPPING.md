# Paper-to-code mapping

Inspected implementation: PhyClone **0.8.0**, commit `27383246c1aff7b1d62c02662017bd61bfdfbc33`. Paper experiments: **0.7.0**. `EXACT` permits the publication’s stated numerical grid approximation; `POSSIBLE_MISMATCH` is preserved when equivalence is not justified.

| Paper concept | Paper location | Source file / function | Runtime behavior | Match |
|---|---|---|---|---|
| Main tidy input | Main §2/Fig.1 p.2 | `data/validator/PhyClone_schema.json`; `data/pyclone.py:197-280` | Validates rows; drops major-CN-zero and incomplete mutations; supplies purity/error defaults | EXACT + ADDITIONAL_IMPLEMENTATION_DETAIL |
| PyClone CN/purity VAF | Supp S1.1 pp.1–2 | `utils/math_utils.py:179-244`, `log_pyclone_*`; `data/pyclone.py:299-403` | Three-population CN-weighted genotype mixture over CCF grid | EXACT |
| Major-CN genotype prior | Supp S1.2 p.2 | `data/pyclone.py:324-352`, `get_major_cn_prior` | Before/after CNA candidates with equal weights | EXACT |
| Pre-clustering atom | Main §2.2.2 p.3 | `data/pyclone.py:82-115,184-194` | Sums member log grids; atom can merge but never split | EXACT |
| CRP partition prior | Main §2.1–2.2 pp.2–3; Supp S1.3 | `tree/distributions.py:56-65` | `alpha^K prod (size-1)!`, omitting state-independent normalizer | EXACT |
| Dummy-root forest | Main §2.1 p.2; Supp S1.3 | `tree/tree.py:19-43`; `tree/distributions.py:43-54` | Explicit root, multiple root children encode forest; Cayley term | EXACT |
| Final single-root preference | Supp S1.3.1 pp.3–4 | `tree/distributions.py:12-14,67-121`; `tree/base.py:93-100` | `C=1000` root penalty and representation multiplicity correction | EXACT + extra detail |
| Dirichlet prevalence | Main §2.1–2.2; Supp S1.3–S1.5 | `tree/base.py:27-35`; `tree/utils.py:7-25` | Uniform grids and cumulative integration implement `kappa=1`; no arbitrary kappa | EXACT for kappa=1; PAPER_ONLY general kappa |
| Descendant-sum CCF | Main §2.2 p.3 | `tree/tree_node.py:35-69`; `tree/utils.py:39-57` | Child likelihood convolution imposes parent ≥ summed children | EXACT |
| Collapsed likelihood | Main §2.2.1 p.3; Supp S1.4–S1.5 | `tree/tree_node.py:43-69`; `tree/utils.py:7-68`; `tree/distributions.py:151-163` | Finite-grid post-order DP, complete root mass at 1 | APPROXIMATE as stated |
| Multi-sample model | Main §2.2 p.3; Supp Fig.S2 | `data/pyclone.py:375-403`; `tree/utils.py:39-57` | Shared tree/partition, independent sample grid operations | EXACT |
| SMC target/growth states | Main §2.3 pp.3–4; Supp S1.6 p.6 | `tree/tree_shell_node_adder.py`; `smc/kernels/base.py:46-75` | Add to existing root, create root above subset, or outlier | EXACT |
| Semi-adapted proposal | Supp S1.6.2 p.6 | `smc/kernels/semi_adapted.py:31-130` | Scores existing assignments, samples new-root child subset | EXACT; benchmark/default path |
| Fully adapted proposal | Supp S1.6.2 p.6 | `smc/kernels/fully_adapted.py` | Enumerates all `2^R` subsets | EXACT |
| Bootstrap proposal | Supp S1.6.2 p.6 | `smc/kernels/bootstrap.py` | Prior-like random proposal | EXACT without outliers; 0.8.0 POSSIBLE_MISMATCH with outliers |
| ESS/resampling | Supp S1.6/Fig.S4 | `smc/swarm/swarm.py:21-61`; `smc/samplers/standard.py:22-44` | Stable normalized weights; multinomial resampling at relative ESS threshold | ADDITIONAL_IMPLEMENTATION_DETAIL |
| Admissible order | Main §2.3.1 p.4; Supp S1.6.3 p.7 | `smc/utils.py:19-135` | Descendant-before-parent, within-node and bridge shuffles | EXACT |
| Whole-tree Particle Gibbs | Main §2.3.1 p.4 | `mcmc/particle_gibbs.py:8-49`; `smc/samplers/conditional.py` | Conditional path plus final weighted particle | EXACT |
| Subtree Particle Gibbs | Supp S1.6.4 p.7 | `mcmc/particle_gibbs.py:52-110` | Mutation-weighted root selection, full-tree correction | POSSIBLE_MISMATCH: source TODO; default off |
| Reassignment move | Main §2.3.2 p.4 | `mcmc/gibbs_mh.py:7-66` | Moves nonsingleton data to existing node/outlier; node count fixed | EXACT behavior; correctness TODO |
| Prune-regraft | Main §2.3.2 p.4 | `mcmc/gibbs_mh.py:69-129` | Enumerates new attachment including dummy root | EXACT |
| Binary outlier state | Main §2.2.3 p.3; Supp S1.7 | `tree/distributions.py:124-204`; tree outlier bucket `-1` | Excludes outlier atom from tree and applies prior/independent score | EXACT structurally |
| Uniform outlier integral | same | `data/base.py:29-34` | Cumulative plus second grid average, not single rectangle integral | POSSIBLE_MISMATCH in 0.7.0 and 0.8.0 |
| Data-informed loss prior | Supp S1.7.1 p.8 | `data/cluster_outlier_probabilities.py:24-151` | Truncal chromosome null; min cluster 4 and ratio>1 additions | APPROXIMATE + extra detail |
| Alpha resampling | Supp S2.2 p.9 | `mcmc/concentration.py:11-60`; `run.py:292-313,382-392` | Optional Gamma-prior auxiliary update | ADDITIONAL_IMPLEMENTATION_DETAIL |
| Caches/TreeHolder | Supp S2.1–S2.2 pp.9–10 | `utils/cache.py`, `hashing_utils.py`, `tree_shell_node_adder.py`, kernels | Bounded convolution/tree/proposal caching | EXACT/extra detail |
| Trace | Main output overview p.2 | `utils/save_hdf5.py` | HDF5 states, timing, alpha, node/outlier/root counts | ADDITIONAL_IMPLEMENTATION_DETAIL |
| MAP tree | Main §2.4.2 p.5 | `process_trace/process_trace.py:27-58` | Maximizes prior-inclusive `log_p_one`, despite “joint-likelihood” name | EXACT intent; naming caveat |
| Consensus | Main general output claim | `process_trace/consensus.py:81-111` | Compatible clades; default effectively count × best score | ADDITIONAL_IMPLEMENTATION_DETAIL |
| Prevalence reinstatement | Main §2 p.2 | `process_trace/map.py:6-157` | Conditional grid max-product backtracking only | EXACT MAP; PAPER_ONLY posterior sampling |
| Benchmark metrics/statistics | Main §2.4.3 | absent | No V/AD/RRE/LPR/Friedman/Nemenyi pipeline in checkout | PAPER_ONLY |

## Operational defaults

| Setting | Published benchmark 0.7.0 | Current 0.8.0 CLI | Current 0.8.0 direct `run()` |
|---|---:|---:|---:|
| chains | 4 | 1 | 1 |
| burn-in | 100 | 1000 | 100 |
| iterations | 5000 | 10000 | 5000 |
| particles | 100 | 100 | 100 |
| density | beta-binomial | beta-binomial | beta-binomial |
| precision | not separately stated; 0.7 CLI 400 | 400 | 1.0 |
| proposal | semi-adapted | semi-adapted | semi-adapted |
| grid points | 0.7 default 101 | 101 | 101 |
| global outlier prior | low/high 0.0001/0.4 when loss assignment enabled | 0 unless activated | 0 |
| subtree PG | 0 by 0.7 default | 0 | 0 |

## Tests and verification limits

[STATED] Supplement S2.3 describes exact small-posterior tests for all three PG kernels and marginalisation comparisons against a 1,000,000-draw Dirichlet importance sampler over at least ten trees (pp.10–11). [IMPLEMENTED] Matching test modules exist. In this workspace, `test_root_term` passed all eight tests. Other selected modules could not be collected in the available Python 3.10 environment because required packages (`numba`, `networkx`, `xxhash`) were unavailable; the repository declares Python ≥3.12. No import failure is treated as an algorithm failure.

## Current-use warnings

1. Avoid `bootstrap` with active outliers in 0.8.0 until the 0.1/0.35/0.55 sampled versus 0.1/0.45/0.45 recorded probabilities are fixed/tested. Paper benchmarks used semi-adapted and are not implicated.
2. Keep subtree PG disabled unless its selection-probability TODO is resolved.
3. Treat outlier posterior odds cautiously because the implemented outlier marginal does not match the published single integral.
4. Use CLI/API-specific defaults explicitly; preferably pass all critical values.
5. Validate cluster/main mutation concordance and purity/CN fields before running; code has edge cases that can omit or misalign malformed data.
