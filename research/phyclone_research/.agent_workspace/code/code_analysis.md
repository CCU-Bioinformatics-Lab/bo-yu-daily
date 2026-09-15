# PhyClone implementation analysis

Status: **COMPLETE for static code analysis; PARTIAL for runtime validation** (the installed Python 3.10 environment lacks `numba`, `networkx`, and `xxhash`, while this checkout declares Python >=3.12 and those dependencies).

Evidence vocabulary in this document:

- **[IMPLEMENTED]** is directly established by repository code at commit `27383246c1aff7b1d62c02662017bd61bfdfbc33` (package version 0.8.0).
- **[INFERRED]** is a consequence of the implementation or a code/paper comparison, not an explicit author statement.
- Paper mapping refers only to the local `phyclone.pdf` and `btaf344_supplementary_data/supp.pdf`; no external source was used.

## 1. End-to-end runtime map

**[IMPLEMENTED]** The executable entry point is `phyclone.cli:main` (`pyproject.toml:41-42`). The analysis path is:

1. `phyclone/cli.py:243-450`, Click command `run`: parse and validate CLI parameters.
2. `phyclone/run.py:31-152`, `run`: seed RNG, call `load_data`, run one chain locally or several chains through a spawn-based `ProcessPoolExecutor`, then save the trace.
3. `phyclone/data/pyclone.py:17-79`, `load_data`: validate/filter input, construct a per-mutation or per-input-cluster likelihood grid, and attach log outlier priors.
4. `phyclone/run.py:187-239`, `run_phyclone_chain`: instantiate an `FSCRPDistribution`, `TreeJointDistribution`, proposal kernel and MCMC/SMC samplers; initialize all data in one node; run heuristic burn-in and then the main chain.
5. `phyclone/run.py:242-298`, `_run_main_sampler`: each iteration performs either full-tree or subtree Particle Gibbs, then configured data-point reassignment and prune-regraft sweeps, optionally stores the state, and then optionally samples CRP concentration `alpha`.
6. `phyclone/utils/save_hdf5.py:6-204`: write samples, likelihood-grid `DataPoint`s, cluster mapping, trace statistics and deduplicated tree objects to HDF5.
7. `phyclone/process_trace/process_trace.py`: turn the HDF5 trace into MAP, consensus, or ranked-topology products, including Newick, mutation/clone TSV and sample-prevalence TSV.

No variational-inference implementation exists in this repository. PyClone-VI is only an optional external pre-clustering source. No benchmark/evaluation CLI or paper experiment pipeline is present; repository evaluation is primarily a test suite.

## 2. Input contract and preprocessing

### 2.1 Main input

**[IMPLEMENTED]** `phyclone/data/validator/PhyClone_schema.json` requires one tidy row per mutation/sample with:

`mutation_id`, `sample_id`, `ref_counts`, `alt_counts`, `major_cn`, `minor_cn`, `normal_cn`.

Optional fields are `tumour_content`, `error_rate`, and `chrom`. Counts and copy numbers must be non-negative integers; `normal_cn >= 1`. The schema only imposes lower bounds on tumour content and error rate, not upper bounds. `InputValidator` (`validator/input_validator.py:17-203`) auto-detects delimiters/compression, drops exact duplicate rows, validates known columns, but does not reject unknown columns.

**[IMPLEMENTED]** Actual cleanup order (`data/pyclone.py:197-280`) is significant:

- Rows with `major_cn == 0` are removed first (`251-260`).
- Sample names are collected after that removal (`201`).
- A mutation is retained only when its row count equals the total sample count (`224-248`). A row count below that is treated as partial absence; above it as duplication.
- Missing `error_rate` becomes `1e-3`; missing `tumour_content` becomes `1.0` (`263-268`).
- Samples are lexicographically sorted, mutations grouped in sorted order, and `sample_id` coerced to pandas string (`201`, `278-289`).

**[INFERRED]** The row-count test does not explicitly verify one distinct row for every distinct sample. A mutation with duplicate non-identical rows in one sample and no row in another can have the expected total row count and escape this filter, then violate later sample alignment. This is a plausible malformed-input failure case.

### 2.2 Cluster/pre-cluster input

**[IMPLEMENTED]** `cluster_file_schema.json` requires only `mutation_id`, `cluster_id`; optional fields are `sample_id`, `cellular_prevalence`, `outlier_prob`, and `chrom`. `load_data` turns each input cluster into one atomic `DataPoint` (`data/pyclone.py:82-115`): individual mutations' log-likelihood grids are summed, and the cluster's log outlier/non-outlier probabilities are multiplied in probability space by multiplying their log probabilities by cluster size (`103`, `184-194`).

Consequences:

- **[IMPLEMENTED]** Mutations in an input cluster can never be split by PhyClone because the sampler sees one `DataPoint`.
- **[IMPLEMENTED]** Different input clusters can be assigned to the same inferred tree node, so PhyClone can merge/refine an over-split pre-clustering.
- **[IMPLEMENTED]** Without a cluster file, each mutation is one `DataPoint`, so both clustering and topology are inferred jointly.
- **[INFERRED]** Complexity scales with the number of `DataPoint`s after pre-clustering, explaining the WGS recommendation, while the emission construction still processes every mutation once.

There is no independent pre-clustering algorithm in this repository. `README.md:273-282` recommends external PyClone-VI settings (`num-clusters 40`, `mix-weight-prior 1000`, `num-restarts 100`).

**[INFERRED]** Main-input/cluster-file mutation-set concordance is not validated. The outer merge at `data/pyclone.py:84` followed by `groupby("cluster_id")` can silently omit main-input mutations lacking a cluster assignment; conversely cluster-only mutations produce a missing `PyCloneDataPoint` and can fail during likelihood construction. This deserves an input-integrity check in downstream use.

## 3. PyClone allele-count emission: paper equations to code

Local supplement S1.1 defines three populations: normal, tumour-reference, and tumour-variant. With tumour content `t` and cellular prevalence/CCF `f`, their weights are `(1-t, t(1-f), tf)`. For candidate genotype `c`, expected VAF is copy-number-weighted variant-allele expectation divided by expected total copy number. Allele counts use Binomial or mean/precision Beta-Binomial and are marginalized across plausible genotypes.

**[IMPLEMENTED]** This maps exactly at the computational level to:

- `data/pyclone.py:299-321`, `create_sample_data_point`: stores ref count as `a`, alt count as `b`, genotype copy-number matrix `cn`, allele fractions `mu`, log genotype prior `log_pi`, and tumour content `t`.
- `utils/math_utils.py:180-212`, `log_pyclone_beta_binomial_pdf`, and `215-244`, `log_pyclone_binomial_pdf`: build `population_prior = [1-t, t(1-f), tf]`; compute
  `e_vaf = sum_i population_prior[i] * cn[c,i] * mu[c,i] / sum_i population_prior[i] * cn[c,i]`;
  evaluate alt count `b` out of `a+b`; add genotype log prior; `log_sum_exp` over genotype states.
- Beta-Binomial parameters are `a = e_vaf * precision`, `b = precision - a` (`math_utils.py:206-210`).
- `PyCloneDataPoint.to_likelihood_grid` (`data/pyclone.py:365-403`) evaluates this at `np.linspace(0,1,grid_size)` independently for every sample.

### 3.1 Copy-number/genotype prior

**[IMPLEMENTED]** `get_major_cn_prior` (`data/pyclone.py:324-352`) implements supplement S1.2's “major copy number” method:

- Reject `major_cn < minor_cn`.
- Let total tumour CN be `major + minor`.
- For a mutation before the CN event, enumerate mutated multiplicity `x = 1..major_cn`, with normal/reference CN `normal_cn` and tumour variant allele fraction `x/total_cn` (clipped by sequencing error).
- If tumour total CN differs from normal CN, add one mutation-after-CN state with tumour reference and variant total CN both equal to tumour total CN and mutated fraction `1/total_cn`.
- Assign every candidate state equal prior mass `1 / number_of_states`.

**[INFERRED]** There is no explicit subclonal CN state, uncertainty distribution over allele-specific CN, or joint inference of CN. CN and tumour content are fixed inputs; uncertainty is only over the enumerated mutation timing/multiplicity states conditional on those inputs. This is a central failure mode when CN calls or purity are wrong.

## 4. Cluster, clone, tree, and forest representation

**[IMPLEMENTED]** `Tree` is a directed non-multigraph backed by `rustworkx.PyDiGraph` (`tree/tree.py:19-43`). It includes an empty dummy root named `"root"`; biological clone nodes have integer IDs; outliers live in a special data bucket `-1` and are not graph nodes (`tree/base.py:12-35`). Multiple children of the dummy root encode a rooted forest. A non-dummy node contains one or more `DataPoint`s and therefore represents an inferred clone/cluster. Edges run parent to child.

**[IMPLEMENTED]** Each `TreeNode` stores:

- `log_p`: uniform grid prior plus emission log likelihoods for data originating at that node;
- `log_r`: recursively marginalized likelihood of the subtree;
- a set of data-point indices (`tree/tree_node.py:8-79`).

**[IMPLEMENTED]** Tree identity/hash is `(frozenset of descendant-data clades, frozenset of outlier indices)` (`tree/base.py:37-60`). Thus node labels and child ordering do not define distinct states. `multiplicity` subtracts `sum_v log(outdegree(v)!)` in the prior (`tree/base.py:93-100`), accounting for symmetries/order multiplicity in the represented topology.

**[INFERRED]** “Topology” in trace aggregation is not merely an unlabeled graph shape: clades encode which input data points lie below every node, and the outlier set is included. Two identical shapes with different mutation/cluster assignments are different `tree_hash` states.

## 5. Cellular and clonal prevalence marginalization

The local supplement S1.3 defines clonal prevalence `rho_v` as the mass originating at node `v` and cellular prevalence `rho_bar_v = rho_v + sum_children rho_bar_child`, enforcing the infinite-sites/additivity constraint. S1.4–S1.5 integrates the Dirichlet(1) node parameters on a grid. Its dynamic program defines child convolution `D`, cumulative residual-mass sum `S`, and `R_v = likelihood_v * S_v`, with final likelihood `R_root(1)`.

**[IMPLEMENTED]** The code mapping is:

- Uniform Dirichlet-grid factor: `BaseTree.__init__`, `tree/base.py:27-35`, sets every grid prior to `-log(L+1)` (the CLI calls the number of points `grid_size`, default 101).
- Node emission product: `TreeNode.add_data_point[_list]`, `tree/tree_node.py:35-50`, sums per-data log likelihoods into `log_p`.
- `D` recursion: `tree/utils.py:28-57`, `compute_log_D`, performs convolution of child `log_R`s after log stabilization.
- Direct convolution is used below grid size 1000; FFT convolution at 1000+ (`tree/utils.py:60-68`).
- `S` recursion: `tree/utils.py:7-25`, cumulative `logaddexp` of `D` over the prevalence grid.
- `R_v`: `TreeNode.update_node_from_child_r_vals`, `tree/tree_node.py:59-69`, sets `log_r = log_p + log_s`, or `log_r = log_p` at a leaf.
- Post-order evaluation and incremental path updates: `Tree.update`, `_update_path_to_root`, `_update_node`, `tree/tree.py:384-426`.
- Complete-tree constraint: `TreeJointDistribution.log_p_one`, `tree/distributions.py:151-163`, takes the last grid cell of the dummy root in every sample, i.e. total cellular/clonal mass 1.
- Partial-tree scoring: `TreeJointDistribution.log_p`, lines 137-149, sums over dummy-root grid positions. At the final SMC step, `AbstractSMCSampler._get_log_w` replaces the partial target with `log_p_one` (`smc/samplers/base.py:52-58`).

**[IMPLEMENTED]** Multi-sample support is factorized over samples conditional on a common clustering/topology: all grid arrays have shape `(number_of_samples, grid_size)` and final log likelihoods are summed over sample dimensions (`tree/distributions.py:144-159`). There is no cross-sample prevalence prior coupling beyond the shared tree.

### 5.1 Point prevalence estimates

**[IMPLEMENTED]** Prevalences are integrated out during inference, not stored per trace state. For an output tree, `process_trace/map.py:16-168` runs a max-product analogue of the marginalization recursion, fixes dummy-root index to the final grid point (1.0), and backtracks maximizing grid assignments. It reports:

- `ccf` = node cellular-prevalence grid index divided by `grid_size-1`;
- `clonal_prev` = node CCF minus the sum of immediate-child CCFs (`map.py:24-40`).

**[INFERRED]** These are conditional MAP-like prevalence assignments for the selected/constructed point tree, not posterior means or likelihood-weighted prevalence averages over the sampled posterior. Output outliers are assigned zero CCF/clonal prevalence (`process_trace.py:276-301`).

## 6. FS-CRP and final-tree prior

Local supplement S1.3 gives `b ~ CRP(alpha)` and a uniform rooted-forest prior conditional on the number of blocks; S1.3.1 adds a final-state root-count penalty with constant `C=1000` and topology-count correction.

**[IMPLEMENTED]** `FSCRPDistribution` (`tree/distributions.py:7-121`) implements two related targets:

- CRP term: `K log(alpha) + sum_blocks log((size_b-1)!)` (`56-65`). Normalizing constants depending only on N are omitted.
- Partial SMC tree prior `log_p`: subtract `(K-1) log(K+1)` and tree multiplicity (`43-54`), matching the uniform forest count up to representation constants.
- Completed-tree prior `log_p_one`: replaces that forest-size term with sub-root-specific Cayley/topology counts plus the normalized `C=1000` root penalty, then subtracts multiplicity (`67-121`).

**[IMPLEMENTED]** `TreeJointDistribution` adds this prior, the prevalence-marginalized emission, and (when active) outlier prior/marginal likelihood (`124-204`). The trace field named `log_p` actually stores `log_p_one` (`utils/save_hdf5.py:78-115`).

**[INFERRED]** Therefore CLI/README phrases such as “highest joint-likelihood” refer to the full unnormalized joint posterior score (tree/partition prior plus data likelihood and outlier terms), not a likelihood-only statistic.

### 6.1 Concentration hyperparameter

**[IMPLEMENTED]** `alpha` starts at the CLI value (default 1.0). If updates are enabled, `GammaPriorConcentrationSampler(0.01,0.01)` uses the Escobar-West auxiliary-beta mixture update (`mcmc/concentration.py:11-60`). Outlier data are excluded from K and N (`run.py:304-313`). Alpha is updated after the trace append in each iteration (`run.py:283-293`), so the stored alpha describes the score at that state before the next update.

## 7. Outlier/loss model

Local paper section 2.2.3 and supplement S1.7 define Bernoulli outlier indicator `o_n`, prior `nu_n`, independent Uniform-prevalence PyClone marginal likelihood for an outlier, and the usual tree likelihood for a non-outlier.

**[IMPLEMENTED]** Runtime outlier modelling is globally active iff the `outlier_prob` reaching `run()` is greater than zero (`run.py:61`). With active modelling:

- each data point contributes log `nu` if placed in the `-1` bucket, or log `(1-nu)` if on-tree (`tree/distributions.py:193-204`);
- its precomputed independent marginal emission is added if outlier (`data/base.py:29-36`, `tree/distributions.py:186-191`);
- all proposals may assign it to the outlier bucket;
- outliers participate in admissible-order permutation sampling and are included in subtree resampling (`smc/utils.py:98-135`, `mcmc/particle_gibbs.py:63-83`).

**[IMPLEMENTED]** A pre-clustered `DataPoint` is all-or-none outlier: its prior terms are `cluster_size * log(nu)` and `cluster_size * log(1-nu)`, and its likelihood grid is the sum over member mutations (`data/pyclone.py:82-115,184-194`). Thus the implementation preserves a supplied cluster as a unit even for loss classification.

### 7.1 Data-informed cluster loss prior

**[IMPLEMENTED]** `data/cluster_outlier_probabilities.py` implements:

1. Determine candidate truncal clusters as those tied for maximum `cellular_prevalence` in each sample; choose the unique candidate present in all samples, otherwise choose the candidate with greatest overall mean (`90-132`).
2. Use the truncal cluster's empirical list of chromosomes as a background (`67-78`).
3. For each non-truncal cluster with at least 4 mutations, make 10,000 without-replacement draws of equal size (resizing the background if needed), count draws having fewer unique chromosomes than observed, and set `p=max(count,1)/10000` (`24-63`).
4. Mark a cluster high-loss only if `p < 0.01` **and** expected unique chromosomes / observed unique chromosomes is greater than 1 (`59-61`). The second condition is an additional implementation detail absent from the supplement prose.
5. Assign high or low prior, CLI defaults high=0.4; low is the global outlier probability (`64-88`).

The feature needs `chrom`, `cellular_prevalence`, and `sample_id`; `chrom` may be merged from main data (`data/pyclone.py:148-180`). Missing required optional columns cause a fallback to the global prior, not failure.

### 7.2 Possible outlier marginalization mismatch

**[IMPLEMENTED]** For likelihood-grid values `f_i`, `DataPoint.__init__` (`data/base.py:29-34`) computes, per sample:

`logsumexp_j( log(1/L) + logsumexp_{i<=j}(log f_i + log(1/L)) )`,

equivalent in probability space to `L^-2 * sum_j sum_{i<=j} f_i`, before summing sample log scores.

**[INFERRED — POSSIBLE_MISMATCH, UNRESOLVED]** Paper/supplement S1.7 writes a single Uniform integral `integral_0^1 f(x|rho) d rho`, whose direct grid analogue would be `L^-1 sum_i f_i`. The code instead applies a cumulative `S` operation and a second uniform-grid sum. This may intentionally embed an unreported residual/dummy-root prevalence integration, but that justification is not documented and no focused outlier-marginal test was found. Do not describe these as exactly equivalent without author confirmation or a dedicated numerical derivation/test.

## 8. Inference and proposals

### 8.1 SMC state growth

Local supplement S1.6 describes bottom-up SMC under an admissible permutation `sigma`. **[IMPLEMENTED]** At each datum, proposal states are:

- add it to any current forest root (existing node); or
- create a new root whose children are any subset of current roots; or
- when enabled, mark it outlier.

This is implemented through lightweight `TreeHolder`/`TreeShellNodeAdder` objects (`tree/tree_shell_node_adder.py`) so likelihood/prior-relevant state can be computed without building a full `Tree`. `Kernel.create_particle` applies the standard incremental target/proposal weight, and includes admissible-permutation density during Particle Gibbs (`smc/kernels/base.py:46-75`).

`ParticleSwarm` normalizes weights stably and computes relative ESS (`smc/swarm/swarm.py:21-61`). Multinomial resampling occurs when relative ESS `<= resample_threshold` (`smc/samplers/standard.py:22-44`), default 0.5.

### 8.2 Three proposal kernels

- **[IMPLEMENTED] Bootstrap** (`smc/kernels/bootstrap.py`): prior-like cheap proposal. When nonempty and no outliers, half the mass goes to uniformly choosing an existing root; half to a new root. For a new root, number of children is uniform on `0..R`, then the subset is uniform conditional on its size. With active outliers, a fixed proposal probability 0.1 is reserved for outlier; the residual is split in half. **Potential code concern:** the branching thresholds at `bootstrap.py:99-104` compare `u` to `outlier_prob` and `_half_val=(1-outlier_prob)/2` rather than to `outlier_prob + _half_val`, so with 0.1 outlier probability the realized existing-node interval is only `(0.1,0.45)` and new-node probability is 0.55, while `log_p` assigns 0.45 to each structural branch. This proposal sampling/log-density inconsistency is **[INFERRED — POSSIBLE_MISMATCH, UNRESOLVED]**.
- **[IMPLEMENTED] Fully adapted** (`smc/kernels/fully_adapted.py`): enumerate every new-node child subset (`2^R`), every existing-root assignment, and optional outlier, then sample proportional to full partial-tree `log_p`. Most accurate per proposal but exponential in number of roots.
- **[IMPLEMENTED] Semi-adapted, CLI default** (`smc/kernels/semi_adapted.py`): when the tree is nonempty, choose 50/50 between (a) all existing-root assignments plus optional outlier, weighted by partial-tree `log_p`, and (b) one randomly generated new-root child subset. It avoids `2^R` enumeration. On an empty tree, it weights the sole new node and optional outlier by `log_p`.

### 8.3 Particle Gibbs and ordering

**[IMPLEMENTED]** Fixed bottom-up ordering prevents an early datum from later becoming ancestor of a later datum. `RootPermutationDistribution.sample` (`smc/utils.py:98-135`) recursively:

- emits descendants before parent-node data;
- bridge-shuffles sibling-subtree sequences while preserving internal orders;
- shuffles data within a node;
- bridge-shuffles outliers with tree data at the dummy root.

`log_count`/`log_pdf` (`smc/utils.py:19-95`) count this admissible permutation space. `ParticleGibbsTreeSampler` samples such a sigma, runs conditional SMC retaining a path for the current tree, then selects a final weighted particle (`mcmc/particle_gibbs.py:8-49`; `smc/samplers/conditional.py`). This is the direct code realization of supplement S1.6.3.

**[IMPLEMENTED]** Burn-in is different: `UnconditionalSMCSampler` samples an ordering from the current tree but runs ordinary SMC and selects a weighted result (`smc/samplers/unconditional.py`). `run._run_burnin` discards the burn-in trace and returns the highest `log_p_one` tree seen, not the last tree (`run.py:316-370`). README explicitly calls this heuristic and says it does not target the posterior.

### 8.4 Additional MCMC moves; split/merge status

**[IMPLEMENTED]** Each main iteration executes:

1. full-tree PG, or subtree PG with probability `subtree_update_prob`;
2. `num_samples_data_point` reassignment sweeps;
3. `num_samples_prune_regraph` subtree attachment sweeps;
4. optional concentration update (`run.py:267-293`).

Data-point reassignment (`mcmc/gibbs_mh.py:7-66`) shuffles data points and, only when the old node has >1 item, Gibbs-samples among all existing nodes and optional outlier using `log_p_one`; it preserves topology and node count. It deliberately cannot empty a node.

Prune-regraph (`gibbs_mh.py:69-129`) selects a graph node uniformly, removes its whole subtree, enumerates attachment to every remaining biological node or dummy root, and samples using `log(number_of_children_at_attachment+1) + log_p_one(new_tree)`. It preserves clustering and node count.

Subtree PG (`mcmc/particle_gibbs.py:52-110`) samples a mutation-weighted node, takes its parent as subtree root, moves all outliers into the subtree update, conditionally resamples it, grafts it back and corrects particle weights using the full-tree target. The source contains an explicit TODO questioning whether random node-choice probability needs an additional term (`87-88`); correctness is therefore **UNRESOLVED** in the implementation itself. CLI default subtree-update probability is 0, so this path is off by default.

There are no named reversible-jump “split” or “merge” move classes. **[IMPLEMENTED]** Node-count and partition changes occur inside whole-tree/subtree PG reconstruction: adding to an existing root coalesces data; creating a new root makes another cluster. The auxiliary data-point move can merge assignments into an existing node but cannot delete the emptied source node because it never moves singleton nodes.

## 9. Results and trace semantics

### 9.1 Trace

**[IMPLEMENTED]** HDF5 contains input samples, data-point likelihood grids and outlier terms, optional original mutation-to-precluster mapping, RNG seed, per-chain iterations/times/alpha/full score/node count/outlier count/root count, and deduplicated graph/node-data states (`utils/save_hdf5.py`). `thin=1` stores iteration zero and every iteration; the condition is `i % thin == 0` (`run.py:286`).

### 9.2 MAP

**[IMPLEMENTED]** `phyclone map` default `map_type=joint-likelihood` chooses the single trace row with greatest stored `log_p_one`; `frequency` chooses the topology-state with greatest sample count, retaining that group's best-score representative (`process_trace/process_trace.py:27-58,199-211`). It then emits Newick and TSV tables.

### 9.3 Consensus

**[IMPLEMENTED]** `phyclone consensus` aggregates clades over unique topology-states. Counts mode weights by sample frequency. Default “joint-likelihood” mode normalizes one best log score per topology, then `clade_probabilities` multiplies that topology weight by its count (`process_trace.py:67-116`; `process_trace/consensus.py:81-105`). Compatible clades above the threshold are assembled into a consensus graph.

**[INFERRED]** Default weighted consensus is therefore based on `count * exp(best topology score)`, not a direct sum of per-draw posterior weights. Also, `key_above_threshold` uses strict `>` despite its docstring saying “above or equal” (`consensus.py:109-111`); a clade exactly at 0.5 is excluded under the default 0.5 threshold.

### 9.4 Topology report

**[IMPLEMENTED]** States are grouped by tree hash, ranked by best full score, assigned IDs `t_0...`, and reported with count and representative iteration. An optional tar.gz contains Newick and result/prevalence TSVs for requested top states (`process_trace.py:121-211`).

## 10. Defaults and hidden constants

### 10.1 User-facing CLI defaults (`cli.py:243-447`)

| Parameter | Default | Implementation meaning |
|---|---:|---|
| burnin | 1000 | heuristic unconditional SMC iterations; Click clamps minimum to 1 |
| num-iters | 10000 | post-burn-in MCMC iterations |
| thin | 1 | store when `i % thin == 0` |
| num-chains | 1 | README recommends >=4 |
| cluster-file | none | mutations are atomic input data points |
| density | beta-binomial | alternative binomial |
| outlier-prob | 0 | outlier modelling inactive |
| proposal | semi-adapted | bootstrap / fully-adapted alternatives |
| max-time | infinity | timer covers burn-in plus main chain |
| concentration-update | true | Gamma(0.01, rate 0.01) auxiliary update |
| concentration-value | 1.0 | initial/fixed alpha |
| grid-size | 101 | points spanning 0..1; minimum 11 |
| num-particles | 100 | SMC/PG particles |
| num-samples-data-point | 1 | full assignment sweeps per iteration |
| num-samples-prune-regraph | 1 | topology attachment sweeps per iteration |
| subtree-update-prob | 0.0 | subtree PG off by default |
| precision | 400 | Beta-Binomial precision |
| print-freq | 100 | progress interval |
| resample-threshold | 0.5 | relative ESS threshold |
| seed | none | machine entropy |
| assign-loss-prob | false | data-informed cluster loss prior off |
| user-provided-loss-prob | false | supplied per-cluster outlier prior off |
| high-loss-prob | 0.4 | high prior under data-informed assignment |

Additional constants: proposal outlier probability 0.1 (`smc/kernels/base.py:118-121`); loss assignment minimum cluster size 4 and 10,000 trials, p<0.01 plus ratio>1 (`data/pyclone.py:28`; `cluster_outlier_probabilities.py:24-61`); final root penalty C=1000 (`tree/distributions.py:12`); convolution caches 4096/2048 entries (`tree/utils.py`); proposal caches 2048 entries (`smc/kernels/*`).

### 10.2 API/CLI default conflict

**CONFLICT — UNRESOLVED as an API design issue**

- CLI `run`: burn-in 1000, iterations 10000, precision 400 (`cli.py:260-395`).
- Direct Python `phyclone.run.run`: burn-in 100, iterations 5000, precision 1.0 (`run.py:31-51`).
- `load_data` itself defaults global outlier probability to `1e-4`, while both CLI and `run.run` explicitly default/pass 0 (`data/pyclone.py:17-28`; `run.py:45,84`).

CLI invocations receive the published operational defaults, but direct API callers who omit keywords run a materially different analysis. This should be reported, not silently collapsed into one default set.

### 10.3 Validation edge cases

- **[IMPLEMENTED]** `_validate_positive_value` accepts zero because it rejects only values `<0` (`cli.py:229-232`), even though options say positive. Precision zero is numerically invalid for the Beta-Binomial shapes; max-time zero is accepted.
- **[IMPLEMENTED]** CLI global outlier probability is clamped to [0,1], but cluster-file schema gives `outlier_prob` only a lower bound and no maximum. User-provided values >1 can reach `log1p(-p)` in `compute_outlier_prob`, producing invalid values.
- **[IMPLEMENTED]** Enabling either loss-prior flag with global prior 0 changes it to `1e-4` in the Click callback (`cli.py:202-217`). Calling `run.run` directly does not execute this callback; with `assign_loss_prob=True, outlier_prob=0`, `outlier_modelling_active` remains false even though cluster probabilities can be assigned. This is another CLI/API behavioral divergence.

## 11. Evaluation and correctness evidence in the repository

No paper benchmark scripts or metric implementation (V-measure, ancestor-descendant F-score, LPR, runtime aggregation) are included in this checkout. Hence paper experimental outputs cannot be regenerated from the application repository alone.

The code does contain:

- `tests/unit_tests/test_pg_posterior.py`: compare all three PG kernels against exact enumerated small posteriors, tolerance 0.02. These tests configure outliers false.
- `tests/unit_tests/test_pg_subtree_posterior.py`: analogous subtree PG comparisons.
- `tests/integration_tests/test_marginalisation.py`: compare dynamic-programming likelihood to a million-draw Dirichlet importance sampler across simulated CN/read-count settings, using a permutation t-test; these are extremely expensive and do not test the outlier marginal.
- `test_clonal_prev.py`, `test_root_term.py`, `test_sigma_sampling.py`, `test_fft_convolve.py`, `test_convolution_caching.py`, `test_load_pyclone_data.py`, `test_setup_cluster_df.py`, `test_tree_shell_node_adder.py`: targeted checks for backtracked prevalence, C=1000 root penalty, admissible permutations, direct/FFT convolution equality, input/CN processing, cluster loss priors and lightweight proposal trees.

Runtime check in this analysis: `test_root_term` completed successfully (8 tests) under the available Python, but five requested modules failed import before collection because required packages `numba`, `networkx`, or `xxhash` are absent. This is an environment failure, not a test assertion failure. The checkout declares Python >=3.12 while available `python3` is 3.10, so installing/running the full suite here was not attempted.

## 12. Code/paper consistency summary

| Concept | Status | Evidence and qualification |
|---|---|---|
| PyClone tumour-content/CN-corrected VAF | EXACT | Supplement S1.1; `math_utils.py:180-244` |
| major-CN genotype prior | EXACT | Supplement S1.2; `data/pyclone.py:324-352` |
| CRP partition prior | EXACT up to omitted N-only normalizer | Supplement S1.3; `distributions.py:56-65` |
| uniform forest prior and C=1000 root penalty | IMPLEMENTED with representation corrections | S1.3/S1.3.1; `distributions.py:43-121`, multiplicity term |
| Dirichlet(1), cellular=sum descendant clonal | EXACT computational analogue | S1.3–S1.5; `tree_node.py`, `tree/utils.py` |
| grid DP marginalization and complete mass=1 | EXACT | S1.5; `tree/utils.py`, `log_p_one` |
| pre-cluster atoms may merge but never split | EXACT | paper 2.2.2; `data/pyclone.py:82-115` plus PG construction |
| semi-adapted bottom-up SMC | EXACT | paper 2.3 / supplement S1.6; `smc/kernels/semi_adapted.py` |
| admissible-order Particle Gibbs | EXACT | S1.6.3; `smc/utils.py`, `mcmc/particle_gibbs.py` |
| extra reassignment and prune-regraft moves | EXACT | paper 2.3.2; `mcmc/gibbs_mh.py` |
| subtree PG | IMPLEMENTED but source flags correctness TODO | S1.6.4; `mcmc/particle_gibbs.py:52-110` |
| outlier indicator and prior | EXACT at structural level | paper 2.2.3/S1.7; `TreeJointDistribution` |
| independent outlier Uniform marginal | POSSIBLE_MISMATCH | paper has one integral; code uses cumulative plus second grid sum |
| data-informed loss prior | APPROXIMATE/extra detail | implementation adds `estimate>1`; uses chromosome only, no genomic position |
| bootstrap with active outliers | POSSIBLE_MISMATCH | sample branch probabilities disagree with `log_p` branch masses |
| paper benchmark evaluation | PAPER_ONLY in this repo | no evaluation pipeline/metrics beyond correctness tests |
| caching/lightweight tree optimization | CODE + supplement S2 | `tree_shell_node_adder.py`, cache decorators, `TreeHolder` |

## 13. Failure cases and limitations derivable from implementation

These are **[INFERRED]**, grounded in the cited behavior:

1. Wrong fixed purity or CN calls distort the CCF likelihood and genotype mixture; PhyClone does not infer either quantity.
2. Subclonal CN and mutation loss are not explicitly modeled as evolutionary events; the outlier state discards the offending datum/cluster from topology rather than locating a loss edge.
3. With pre-clustering, one wrong cluster can neither split nor be partially marked outlier; evidence is pooled by summing log likelihoods and exponentiating its outlier prior by cluster size.
4. A coarse CCF grid discretizes both scoring and reported prevalence. Increasing the grid raises convolution cost; direct convolution is quadratic in grid size before switching to FFT at 1000.
5. Fully adapted proposals scale exponentially in the number of current roots (`2^R` child subsets); semi-adapted trades proposal quality for one random subset.
6. PG path degeneracy can freeze early/deep structure; subtree PG is intended to help but is disabled by default and carries a correctness TODO.
7. One default chain is poor for convergence assessment even though README recommends at least four. Output provides no convergence diagnostic such as R-hat/ESS across MCMC draws.
8. MAP/consensus prevalence is point-optimized conditional on one constructed topology; uncertainty in prevalence is not exported.
9. The final prior strongly prefers fewer dummy-root children by factor C=1000 per additional root (with normalization). In weak data, this implementation choice can dominate forest structure.
10. Cluster/main mutation mismatch and insufficient range validation can cause silent omission or invalid numerics as described above.

## 14. Items for Methods Validator / Integrator

1. Carry forward the two high-priority **POSSIBLE_MISMATCH** items: outlier Uniform marginalization and bootstrap active-outlier proposal/log-q inconsistency.
2. State package version explicitly: paper experiments say PhyClone 0.7.0; analyzed checkout is 0.8.0 at commit `2738324`. Treat differences as version drift unless confirmed in the paper-era tag.
3. Keep CLI defaults separate from direct Python API defaults.
4. Describe `log_p` output as an unnormalized joint posterior score, despite UI naming it joint-likelihood.
5. Do not claim explicit loss-edge inference: code has an outlier/loss bucket only.
6. Do not claim posterior mean prevalence: results use max-product backtracking conditional on a point topology.
7. Mark benchmark regeneration from code as unavailable; only correctness/equation-level tests are present.

