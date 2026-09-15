# Supplement Analyst Report

Source: `btaf344_supplementary_data/supp.pdf` (28 PDF pages). Page locators below are PDF page numbers and coincide with the printed supplement page number.

## What the supplement adds

### Allele-count likelihood and copy-number correction

- [STATED] The observed data are mutant read count `x` out of depth `d`, for `N` mutations across `S` samples. Each locus is represented by normal, cancer-reference, and cancer-variant subpopulations with joint genotype `G=(G_N,G_R,G_V)`, tumour content `t`, and mutation cellular prevalence `rho_bar`. The expected variant-read probability `xi(G,rho_bar,t)` is a copy-number-weighted mixture of those three populations, with sequencing error bounded by `epsilon`. Likelihood is Binomial, or Beta-Binomial with mean `xi` and precision `gamma` under overdispersion. Unknown joint genotype is integrated out using weights `pi_i`; the resulting mixture is called the PyClone emission density. (S1.1, pp. 1–2; equations for `mu`, `xi`, Binomial/Beta-Binomial and genotype mixture.)
- [STATED] Cellular prevalence is the sum of the clonal prevalences of all populations carrying the mutation. Clonal prevalence is the inferential primitive, while cellular prevalence is what enters the allele-count likelihood. (S1.1, p. 2, final paragraph.)
- [STATED] The “major copy number” genotype prior considers mutation-before-CNA and mutation-after-CNA cases and assigns equal prior mass to all plausible genotypes. When allele-specific copy number is absent, total CN can be placed in `c_major` and `c_minor=0`. (S1.2, p. 2.)
- [INFERRED] Equal genotype weights are a convenience prior, not evidence that mutation timing alternatives are biologically equiprobable. This can make posterior uncertainty sensitive to which plausible genotypes are enumerated. (Reasoning from S1.2, p. 2.)

### Generative model, partitions, trees, and prevalences

- [STATED] Mutations are partitioned with a Chinese restaurant process, `b|alpha ~ CRP(alpha)`. Conditional on `|b|`, a rooted forest is uniform over forests of that size; all forest roots are attached to a dummy root to form a rooted tree. Node clonal prevalences follow a symmetric Dirichlet prior `rho|kappa ~ Dirichlet(kappa 1_|V|)`. (S1.3, pp. 2–3; graphical models Figure S1/S2, p. 12.)
- [STATED] For node `v`, mutation cellular prevalence is the sum of clonal prevalence over the subtree rooted at `v`: `rho_bar_v = sum_{v' in V_v} rho_v' = rho_v + sum_{v' in C_v} rho_bar_v'`. The likelihood factorises over mutations as `prod_n f(x_n|rho_bar_vn)`. (S1.3, p. 3.)
- [STATED] Multi-sample inference uses a region-specific Dirichlet prevalence vector while sharing partition/tree structure; Figure S2 explicitly indexes sample/region `m`. (S1.3, p. 3; Figure S2, p. 12.)
- [STATED] The CRP density is proportional to `alpha^|b| prod_{block in b} (|block|-1)!`; the forest prior normaliser follows Cayley’s formula, `1/(|b|+1)^(|b|-1)`. (S1.3, p. 3.)

### Root-topology adjustment

- [STATED] The unadjusted prior exhibited a bias toward several children under the dummy root (a multi-rooted forest after dummy-root removal). The final topology score is adjusted so a one-subroot tree is 1000 times likelier than a two-subroot tree, successively, using `C=1000`, a normalising `Z`, and a multiplicity term `w` based on Cayley counts for each subroot subtree. (S1.3.1, pp. 3–4.)
- [INFERRED] This is an empirically motivated structural regulariser layered on the nominal uniform-forest prior, so “uniform tree prior” alone is an incomplete description of the final scoring rule. (S1.3 versus S1.3.1, pp. 2–4.)

### Collapsing prevalence and dynamic programming

- [STATED] Inference collapses the node clonal-prevalence vector `rho` out of `p(X,b,T,rho)`. After changing variables to subtree cellular prevalences, the feasible domain enforces each parent prevalence to be at least the sum of its children. The continuous integral is approximated on `Phi={0,1/L,...,1}`. (S1.4, p. 4.)
- [STATED] The subtree likelihood recursion has three parts: convolve child recursions `D_v`, sum over total child prevalence while applying residual-node prior weight `S_v`, then multiply by the local mutation emission product `ell_v`. With `kappa=1`, the `S_v` recurrence reduces to a cumulative sum. The root likelihood is `R_r(1)`. (S1.5, pp. 4–5; Algorithm 1, p. 13, lines 1–38.)
- [STATED] The dynamic-programming complexity is `O(V(NL + CSL^2))`, with nodes `V`, mutations `N`, grid size `L`, maximum out-degree `C`, and samples `S`. (S1.5, p. 5.)
- [INFERRED] Grid discretisation trades numerical fidelity for speed/memory; the supplement does not report a sensitivity analysis over `L`, so discretisation error remains unquantified here. (S1.4–S1.5, pp. 4–5.)

### SMC and Particle Gibbs inference

- [STATED] SMC grows a forest bottom-up in fixed mutation order `sigma`, iteratively adding a datum either to an existing node or to a new node that adopts a possibly empty subset of existing roots. The target sequence is `gamma_t=p(X_t,b_t,T_t)`, ending at the desired collapsed joint target. (S1.6–S1.6.2, p. 6.)
- [STATED] Three proposal kernels are defined: bootstrap (cheap/random, poor proposals), fully adapted (enumerates outcomes, expensive), and semi-adapted (scores all existing-node attachments but samples children for a new node). The semi-adapted proposal is used in practice as the quality/complexity compromise. (S1.6.2, p. 6.)
- [STATED] A fixed ordering makes some trees unreachable (Figures S5–S7, pp. 16–18). Particle Gibbs alternates conditional SMC for `p(T|X,sigma)` with valid-order resampling from `p(sigma|T)`; orderings are formed recursively by shuffling within nodes and bridge-shuffling child lists. Outliers are interleaved at the root. (S1.6.3, p. 7; Figures S8, p. 19.)
- [STATED] To reduce Particle Gibbs path degeneracy, subtrees are updated. A mutation is chosen uniformly, its node’s parent becomes the subtree root, the subtree is resampled, and the full-tree likelihood enters the final importance weight. Choosing the parent permits dummy-root attachment changes. (S1.6.4, p. 7.)

### Outlier model and mutation-loss heuristic

- [STATED] Infinite-sites propagation can be violated by CNA-mediated mutation loss, while erroneous CN or allele counts can produce noise. Each mutation has an outlier prior `nu_n`; outliers use the PyClone emission with cellular prevalence drawn uniformly and numerically integrated, rather than joining the tree. Proposal, order-resampling, and subtree updates all explicitly include outliers. (S1.7, pp. 7–8.)
- [STATED] For clustered input with genomic positions and cellular-prevalence information, clusters receive user-defined low/high outlier priors, default `0.0001` and `0.4`. The truncal cluster is selected by maximum cellular prevalence across samples, breaking ties by maximum mean prevalence. For each non-truncal cluster of size `|m|`, 10,000 draws from the truncal chromosome distribution form a null for its number of unique chromosomes; `p<0.01` receives the high outlier prior. (S1.7.1, p. 8.)
- [INFERRED] The heuristic treats unusually concentrated chromosome locations as a proxy for possible mutation loss. It depends on correct truncal-cluster selection and on the truncal mutation chromosome distribution being a suitable background. (Reasoning from S1.7.1, p. 8.)

### Implementation details and correctness tests

- [STATED] PhyClone is Python 3 and reported as developed/tested only on Linux. Emission grids and outlier marginals are precomputed in `DataPoint`; convolution results, trees, and proposal distributions use bounded LRU caches. Convolution keys rely on contiguous array bytes and xxHash3. `TreeHolder` is the low-memory cached representation that can still score partial/full trees. (S2–S2.2.3, pp. 9–10.)
- [STATED] Exact-enumeration tests compare PG-SMC posteriors with exactly enumerated small problems for bootstrap, fully adapted, and semi-adapted kernels. (S2.3.1, p. 10.)
- [STATED] Marginalisation tests compare the DP likelihood against an importance sampler drawing Dirichlet clonal prevalences for 1,000,000 iterations per trial, over at least ten independently simulated trees; passing requires an independent two-sample, two-tailed t-test to find the likelihood distributions statistically equal. (S2.3.2, p. 11.)
- [INFERRED] “Failure to reject equality” in a t-test is not an equivalence test; therefore this suite is supportive but does not mathematically prove equality of the DP and importance-sampling estimators. (Reasoning from S2.3.2, p. 11.)

## Additional experiments, datasets, and figures

- [STATED] Figure S10 reports posterior metrics—log perplexity ratio and relationship reconstruction error—on pre-clustered Pairtree, TSSB-Low (low SNV count), and TSSB-High (high SNV count) noise-free synthetic datasets. Methods shown: CONIPHER, fastBE, Orchard, Pairtree, PhyClone. (p. 21.)
- [STATED] Figure S11 reports runtime versus sample count for the small TSSB dataset and additionally includes PhyloWGS. (p. 22.)
- [STATED] Figures S12–S13 stratify Pairtree synthetic results by samples, nodes, and sample/node ratios using log perplexity ratio, relationship reconstruction error, and AD F-score. (pp. 23–24.)
- [STATED] Figure S14 perturbs proportions `p={0,0.1,0.2}` of per-sample regions in CONIPHER no-noise data. Perturbations increase/decrease major or minor CN by one, or both by one; outcomes are V-measure and AD F-score stratified into 2–3, 4–7, and 8+ samples. (p. 25.)
- [STATED] Figures S15–S16 compare reconstructed HGSOC patient 2 and 9 phylogenies from WGS versus WGS+targeted data against ground truth inferred from single-cell and targeted deep sequencing. Compared methods are PhyClone with outlier modelling, CONIPHER, Pairtree, fastBE, and Orchard. (pp. 25–26.)
- [STATED] Table S1 gives HGSOC patients 2, 3, and 9 V-measure/AD F-score. PhyClone is tied for best AD score for patient 2 (WGS/WGS+T: 0.89/1.00) and patient 9 (0.95/1.00), and is best for patient 3 (0.82/0.93); it uniquely improves patient-3 V-measure from 0.85 to 1.00 with targeted data. (p. 27.)
- [STATED] Tables S2–S14, S15–S27, and S28–S36 are delegated to the three XLSX files. The exact sheet-to-table mapping is enumerated on pp. 27–28. (See XLSX Analyst report for cell-level reconstruction.)

## Main-paper concept → supplementary evidence map

| Main-paper concept | Supplement locator | Added detail |
|---|---|---|
| CN/purity-aware observation model | S1.1–S1.2, pp. 1–2 | Full variant-probability mixture, overdispersion option, genotype marginalisation |
| Mutation clusters and tree prior | S1.3, pp. 2–3 | CRP partition, uniform rooted forest, dummy root, Dirichlet clonal prevalences |
| Phylogenetic sum constraint | S1.3–S1.4, pp. 3–4 | Cellular prevalence equals subtree clonal-prevalence sum; feasible domain |
| Single-root preference | S1.3.1, pp. 3–4 | Explicit `C=1000` topology penalty and multiplicity normalisation |
| Tree likelihood | S1.4–S1.5, pp. 4–5; Algorithm 1 p. 13 | Collapsed grid approximation and post-order DP, including complexity |
| Inference | S1.6–S1.6.4, pp. 6–7; Figures S4–S8, pp. 15–19 | Target densities, proposal variants, Particle Gibbs ordering, subtree updates |
| Outlier/loss robustness | S1.7–S1.7.1, pp. 7–8 | Mixture state and chromosome-locality heuristic/default priors |
| Engineering/runtime feasibility | S2.1–S2.2.3, pp. 9–10 | Precomputation, convolution/tree/proposal caches, TreeHolder |
| Validation of implementation | S2.3.1–S2.3.2, pp. 10–11 | Exact enumeration and importance-sampling comparison tests |
| Synthetic posterior evaluation | Figure S10, p. 21; Figures S12–S14, pp. 23–25 | Extra metrics and stratifications |
| Real HGSOC evaluation | Figures S15–S16, pp. 25–26; Table S1, p. 27 | Per-patient trees and numeric reconstruction metrics |

## Limitations and unresolved points

- [STATED] The model’s inheritance constraint can be broken by CNA-driven mutation loss; CN/read errors can also create outliers. (S1.7, p. 7.)
- [STATED] Pure fixed-order SMC cannot reach all trees, and PG suffers path degeneracy for long sequences/deep nodes. (S1.6, p. 6; S1.6.4, p. 7.)
- [STATED] Runtime grows as `O(V(NL+CSL^2))` for likelihood marginalisation; fully adapted proposals become expensive because they enumerate root-child subsets. (S1.5, p. 5; S1.6.2, p. 6.)
- [STATED] Platform validation is Linux-only. (S2, p. 9.)
- [INFERRED] Symmetric Dirichlet prevalence, CRP clustering, equal plausible-genotype weights, grid discretisation, and a fixed 1000-fold root penalty are consequential modelling choices whose sensitivity is not quantified in this supplement.
- UNRESOLVED: TSSB/Pairtree synthetic data generation parameters (tree generator, replicate count, depth/noise mechanism) are not specified in `supp.pdf`; some condition columns/replicate counts are recoverable from XLSX, but complete simulation procedures require another workspace source.
- UNRESOLVED: Default `alpha`, `kappa`, grid size `L`, particle count, iteration count, cache sizes, and Beta-Binomial precision are not stated in `supp.pdf`.

