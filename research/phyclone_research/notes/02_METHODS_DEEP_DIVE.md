# PhyClone methods deep dive

## 1. Input and inferential target

[STATED] For one or more related tumour samples, each somatic SNV supplies reference/alternate read counts, allele-specific copy number and tumour-content estimates. The target is a posterior over clone/node count, mutation-to-node assignment and clone ancestry; sample-specific prevalence is integrated out during tree inference. (Main §2 and Fig.1, p.2; §2.2, p.3.)

[IMPLEMENTED] The current main-input schema requires `mutation_id`, `sample_id`, `ref_counts`, `alt_counts`, `major_cn`, `minor_cn`, `normal_cn`; `tumour_content`, `error_rate`, `chrom` are optional (`data/validator/PhyClone_schema.json`). Missing tumour content becomes 1.0 and missing error rate 0.001; rows with major CN 0 and mutations not represented in all retained samples are removed (`data/pyclone.py:197-280`). Purity and CN are fixed inputs, not inferred.

An optional cluster file requires `mutation_id`, `cluster_id` and may include `sample_id`, `cellular_prevalence`, `outlier_prob`, `chrom`. [IMPLEMENTED] One supplied cluster becomes one atomic `DataPoint`: it cannot split, several `DataPoint`s can merge at a node, and the whole pre-cluster is all-or-none outlier (`data/pyclone.py:82-115,184-194`).

## 2. Variables and meanings

| Symbol | Meaning | Biological meaning | Inferential role |
|---|---|---|---|
| `N`, `S` | mutations, samples | observed loci and related specimens | dataset dimensions |
| `x`, `d` | alternate and total read counts | sequencing support at a locus | allele-count likelihood |
| `G=(G_N,G_R,G_V)` | normal, cancer-reference, cancer-variant genotypes | copy/mutant allele states in three populations | expected VAF and genotype mixture |
| `t` | tumour content/purity | fraction of sequenced cells that are malignant | mixture weight in emission |
| `rho_v` | clonal prevalence of node `v` | malignant-cell fraction originating at that clone only | Dirichlet latent mass |
| `rho_bar_v` | cellular prevalence/CCF at node `v` | malignant-cell fraction carrying mutation(s) born at `v` | argument of PyClone emission |
| `b` | partition of mutations | mutations sharing an evolutionary origin/history | unknown clustering |
| `alpha` | CRP concentration | none directly | controls cluster-number prior |
| `F`, `T=(V,E)` | rooted forest and dummy-rooted tree | clone ancestry | topology state |
| `C_v`, `V_v` | children of `v`, nodes in its subtree | descendants carrying ancestral mutation | prevalence-sum constraint |
| `kappa` | symmetric Dirichlet concentration | none directly | prevalence prior; code implements `kappa=1` |
| `o_n`, `nu_n` | outlier indicator and prior | possible loss/error-incompatible mutation | robust mixture state |
| `sigma` | ordering of data points | none | SMC/PG auxiliary variable |
| `L` | prevalence-grid resolution parameter | none | numerical integration cost/accuracy |

## 3. Allele-count emission

### Equation

For genotype `G`, define total copy number `c(G)=a(G)+b(G)` and a sequencing-error-bounded variant fraction

```text
mu(G) = min(max(b(G)/c(G), epsilon), 1-epsilon).
```

The expected variant-read probability is

```text
xi(G,rho_bar,t) = [(1-t)c(G_N)mu(G_N)
                 + t(1-rho_bar)c(G_R)mu(G_R)
                 + t rho_bar c(G_V)mu(G_V)] / Z,

Z = (1-t)c(G_N) + t(1-rho_bar)c(G_R) + t rho_bar c(G_V).
```

Observed alternate count is Binomial or Beta-Binomial:

```text
p(x|d,G,rho_bar,t) = Binomial(x|d,xi)
```

or `BetaBinomial(x|d, mean=xi, precision=gamma)`. If genotype is uncertain,

```text
f(x|rho_bar) = sum_i pi_i p(x|d,G_i,rho_bar,t).
```

[STATED] These equations are Supplement S1.1, pp.1–2. [IMPLEMENTED] The population masses `(1-t, t(1-f), tf)`, CN-weighted VAF, genotype `logsumexp`, and Beta-Binomial `a=xi*precision`, `b=precision-a` map to `utils/math_utils.py:179-244` and `data/pyclone.py:299-403`.

### Genotype prior

[STATED] The major-copy-number prior enumerates mutation-before-CNA multiplicities `1..major_cn` and, when tumour total CN differs from normal CN, a mutation-after-CNA state; all candidates receive equal mass. If allele-specific CN is unavailable, total CN may be used as major CN with minor CN 0. (Supplement S1.2, p.2.) [IMPLEMENTED] `get_major_cn_prior`, `data/pyclone.py:324-352`, matches this construction.

[INFERRED] This integrates mutation timing/multiplicity uncertainty conditional on fixed CN; it does not model subclonal CN or infer CN uncertainty.

## 4. FS-CRP prior and tree representation

[STATED] First sample a mutation partition:

```text
b | alpha ~ CRP(alpha),
p(b|alpha) proportional to alpha^|b| product_{B in b} (|B|-1)!.
```

Conditional on `|b|`, draw a rooted forest uniformly and connect all forest roots to empty dummy root `r`. For the unadjusted forest,

```text
p(F|b) = 1/(|b|+1)^(|b|-1).
```

(Supplement S1.3, pp.2–3.) [IMPLEMENTED] The CRP and Cayley terms occur in `tree/distributions.py:43-65`; `Tree` stores an explicit dummy root and biological integer nodes (`tree/tree.py:19-43`).

### Final single-root preference

[STATED] Final-state scoring penalizes multiple children under the dummy root, using `C=1000` so one subroot is 1000-fold preferred to two, successive roots likewise, with topology multiplicity normalization. (Supplement S1.3.1, pp.3–4.) [IMPLEMENTED] `tree/distributions.py:12-14,67-121` and `tree/base.py:93-100` implement the root and child-order multiplicity terms.

Therefore the accurate statement is: the **initial forest prior is uniform conditional on node count**, but final scores include a strong single-root structural regularizer.

### Resolved notation conflict

Main §2.2 (p.3) supports `|V|=|b|+1` when `V` includes the dummy root. Supplement S1.3 (p.3) says `|b|=|V|` after adding the dummy root. [IMPLEMENTED] The dummy root has a prevalence grid component and the complete score fixes its mass/CCF to 1. The supplement equality is therefore treated as an off-by-one notation error.

## 5. Clonal versus cellular prevalence

For node `v`,

```text
rho_bar_v = sum_{v' in V_v} rho_v'
          = rho_v + sum_{v' in C_v} rho_bar_v'.
```

[STATED] A mutation originating at `v` is inherited by all descendants under ISA, so its cellular prevalence is the entire subtree mass; `rho_v` is clone-exclusive mass. (Main §2.2, p.3; Supplement S1.3, p.3.) The likelihood is

```text
p(X|rho,b,T) = product_n f(x_n | rho_bar_{v_n}).
```

[IMPLEMENTED] Node emission grids are summed over assigned data points, children are convolved, and output clonal mass is parent CCF minus summed child CCF (`tree/tree_node.py:35-69`; `tree/utils.py:7-68`; `process_trace/map.py:24-40,127-157`). Multi-sample grids share `b,T` but process each sample dimension independently.

## 6. Collapsed likelihood and dynamic programming

### Equation and purpose

```text
p(X,b,T) = p(b|alpha)p(T|b)
           integral_Delta p(rho|kappa)
             product_n f(x_n|rho_bar_{v_n}) d rho.
```

`Delta` is the non-negative simplex with masses summing to one. [STATED] Integrating `rho` removes continuous prevalence variables from posterior tree exploration. (Main §2.2.1, p.3; Supplement S1.4, p.4.) The remaining discrete tree/partition state dimension does not grow with sample count, although evaluation cost does.

### Grid recurrence

Approximate each CCF on `Phi={0,1/L,...,1}`. For subtree root `v`, let `ell_v(rho_bar)` be the product of local emissions. Child recursions are convolved into `D_v`; residual mass at `v` is integrated in `S_v`; then

```text
R_v(rho_bar) = ell_v(rho_bar) S_v(rho_bar),
tree likelihood = R_r(1).
```

For implemented `kappa=1`, `S_v` is a cumulative sum. See Supplement S1.4–S1.5, pp.4–5 and Algorithm 1, p.13. [IMPLEMENTED] `tree/tree_node.py:43-69`, `tree/utils.py:7-68`, `tree/distributions.py:151-163` are the direct grid analogue.

### Complexity reconciliation

Main §2.2.1 says `O(|V|^2)` as shorthand. Supplement S1.5 gives the parameterized bound

```text
O(V (N L + C S L^2)),
```

with nodes `V`, mutations/data contributions `N`, maximum out-degree `C`, samples `S`, grid parameter `L`. Code contains per-sample grid convolutions and switches from direct to FFT at large grids (`tree/utils.py:28-68`). Use the supplement bound; do not claim runtime is sample-independent.

## 7. Inference

### Bottom-up SMC

[STATED] Under order `sigma`, SMC adds one data point at a time and targets `gamma_t=p(X_t,b_t,T_t)`. A point either joins an existing forest root or forms a new root above a possibly empty subset of roots. (Supplement S1.6–S1.6.2, p.6.)

Proposal choices:

- bootstrap: cheap prior-like random proposal;
- fully adapted: enumerate and score all states, including `2^R` child subsets;
- semi-adapted: score existing-root assignments but sample one new-root subset.

[STATED/IMPLEMENTED] Semi-adapted is the practical compromise and both paper benchmark and current CLI choice (`smc/kernels/semi_adapted.py:31-130`). Relative ESS triggers multinomial resampling at current default threshold 0.5 (`smc/swarm/swarm.py:21-61`; `smc/samplers/standard.py:22-44`).

### Particle Gibbs and mutation order

A fixed bottom-up order makes some ancestor states unreachable. [STATED] PG alternates conditional SMC for `p(T|X,sigma)` with resampling a valid `sigma|T`; descendants precede parent-node mutations, sibling sequences are bridge-shuffled, and outliers interleave at the root. (Main §2.3.1, p.4; Supplement S1.6.3, p.7; Figs.S5–S8.) [IMPLEMENTED] `smc/utils.py:19-135`, `mcmc/particle_gibbs.py:8-49` and `smc/samplers/conditional.py` implement this.

### Additional moves

- Data-point reassignment samples another existing node/outlier only when the source node will remain nonempty; topology/node count stay fixed (`mcmc/gibbs_mh.py:7-66`).
- Prune-regraft detaches a subtree and resamples its attachment; cluster/node count stay fixed (`mcmc/gibbs_mh.py:69-129`).
- Whole-tree/subtree PG supplies node-number changes. There are no separately named reversible-jump split/merge moves.
- Subtree PG is designed to reduce PG path degeneracy by updating shorter paths (Supplement S1.6.4, p.7), but its implementation retains a TODO about a possible missing subtree-selection term in both 0.7.0 and 0.8.0 (`mcmc/particle_gibbs.py:52-110`). It is off by default. Formal correctness is UNRESOLVED.

### Burn-in

[IMPLEMENTED] Burn-in uses heuristic unconditional SMC, discards all burn-in states, and initializes the main chain at the best `log_p_one` state seen, not its final state (`run.py:316-369`). It does not target the posterior and is an initialization procedure, not posterior evidence.

## 8. Outlier/loss model

### Published model

```text
p(X,b,T,o) = product_n [nu_n integral_0^1 f(x_n|rho)d rho]^{I(o_n=1)}
             × p(b|alpha)p(T|b)
             × integral p(rho|kappa)
                 product_n [(1-nu_n)f(x_n|rho_bar_vn)]^{I(o_n=0)} d rho.
```

[STATED] Outliers are excluded from the inheritance-constrained tree and get an independent uniform-CCF PyClone likelihood. Proposal/order/subtree updates include them. (Main §2.2.3, p.3; Supplement S1.7, pp.7–8.) This accommodates incompatibility; it does not locate a loss edge.

### Data-informed prior

[STATED] The supplement chooses a truncal cluster by maximal CCF, generates 10,000 chromosome-background draws for each nontruncal cluster, and assigns low/high prior 0.0001/0.4 at `p<0.01` (S1.7.1, p.8). [IMPLEMENTED] Current code also skips clusters smaller than four and requires expected/observed unique-chromosome ratio `>1`; genomic position is not used despite supplement prose listing it (`data/cluster_outlier_probabilities.py:24-67,90-151`). Missing required metadata falls back to the global prior.

### Unresolved publication/code mismatch

The published outlier term has one uniform integral. Code in both 0.7.0 and 0.8.0 computes

```text
L^-2 sum_j sum_{i<=j} f_i
```

instead of the direct rectangular analogue `L^-1 sum_i f_i` (`data/base.py:29-34`). For a constant likelihood, code gives `(L+1)/(2L)` rather than 1 per sample. This factor repeats per outlier and may change posterior outlier odds. No documented derivation or focused test resolves it: **CONFLICT, UNRESOLVED; likely implementation mismatch.**

## 9. Output

[IMPLEMENTED] Sampling writes an HDF5 trace with input likelihood grids, chain/iteration/timing/alpha/node/outlier/root statistics and deduplicated tree states (`utils/save_hdf5.py`). Post-processing provides:

- MAP: highest `log_p_one` state by default; despite UI wording “joint-likelihood,” this score contains CRP/tree/outlier priors plus marginalized likelihood (`process_trace/process_trace.py:27-58`).
- Consensus: compatible high-weight clades; current default effectively uses topology count times exponentiated best topology score, not a direct sum of draw weights (`process_trace/consensus.py:81-111`).
- Topology report: ranked unique topology states, counts and optional Newick/result archives.
- Prevalence TSV: conditional grid max-product/backtracked CCF/clonal prevalence, not posterior mean or interval (`process_trace/map.py`).

Main §2 (p.2) mentions MAP **or sampling** prevalence reinstatement; current checkout exposes MAP-like backtracking but no posterior prevalence sampler. This is `PAPER_ONLY` for sampling.

## 10. Parameter sets that must not be conflated

### Published v0.7.0 benchmark configuration

[STATED] Four chains, burn-in 100, 5,000 iterations, 100 particles, Beta-Binomial, semi-adapted proposal; outlier runs used `--assign-loss-prob`, low/high 0.0001/0.4; selected tree was MAP joint score. (Main §2.4.2, p.5.)

### Current v0.8.0 CLI defaults

[IMPLEMENTED] Burn-in 1,000; iterations 10,000; one chain; grid 101 points; particles 100; precision 400; Beta-Binomial; semi-adapted; global outlier probability 0; alpha starts at 1 and is updated with Gamma(0.01,0.01) hyperprior machinery; one reassignment and one prune-regraft sweep; subtree probability 0; resampling threshold 0.5 (`cli.py:243-447`, `run.py:382-392`). README recommends at least four chains.

### Current direct Python API defaults

[IMPLEMENTED] `run()` instead defaults to burn-in 100, iterations 5,000 and precision 1.0 (`run.py:31-57`). CLI callbacks also activate `1e-4` global outlier probability when a loss-prior flag is requested; direct `run(assign_loss_prob=True,outlier_prob=0)` can leave outlier modelling inactive. Report defaults per entry point.

## 11. Method-level conflict register

| Conflict | Sources | Status |
|---|---|---|
| Dummy-root dimension | main `|b|+1=|V|`; supplement `|b|=|V|`; code includes root | RESOLVED: supplement notation typo |
| Complexity | main `O(|V|^2)`; supplement/code include `N,S,L,C` | RESOLVED: use detailed supplement bound |
| Outlier uniform integral | one integral in paper; triangular double sum in 0.7.0/0.8.0 | UNRESOLVED; likely mismatch |
| Bootstrap+outlier proposal | 0.8.0 sampled 0.1/0.35/0.55 vs logged 0.1/0.45/0.45 | RESOLVED as current regression; unfixed, not benchmark path |
| Subtree-PG transition | supplement claims full-score correction; source questions selection term | UNRESOLVED; disabled by default |
| CLI/API defaults | materially different parameter defaults | RESOLVED by interface-specific reporting |

