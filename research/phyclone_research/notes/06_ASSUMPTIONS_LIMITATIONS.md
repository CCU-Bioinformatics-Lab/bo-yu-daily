# Assumptions, limitations and failure cases

## Biological assumptions

1. [STATED] **ISA inheritance for in-tree SNVs.** A mutation born at node `v` is present in all descendants; its CCF equals descendant-subtree clone mass. (Main Introduction pp.1–2; §2.2 p.3.)
2. [STATED] **Shared history within a node/cluster.** Mutations assigned together share an origin/evolutionary history. (Main §2.1, p.2.)
3. [STATED] **Related samples share one phylogeny.** Samples have separate prevalence vectors but a common partition/tree. (Main §2.2 p.3; Supplement Fig.S2 p.12.)
4. [STATED] **Three-population locus model.** For an SNV, cells are treated as normal, tumour-reference or tumour-variant with constant genotype within each subpopulation. (Supplement S1.1 p.1.)
5. [INFERRED] **Outlier is not causal loss.** The same state can absorb deletion, CN error, alignment/count error or other incompatibility; no deletion branch or recurrence is inferred.

## Statistical assumptions

1. [STATED] Partition follows CRP; pre-adjustment topology is uniform over rooted forests; final state adds a strong `C=1000` single-root preference. (Supplement S1.3–S1.3.1 pp.2–4.)
2. [STATED/IMPLEMENTED] Prevalence follows symmetric Dirichlet; code implements only `kappa=1`. (Supplement S1.3–S1.5; `tree/utils.py`.)
3. [STATED] Mutations are conditionally independent in the likelihood given tree, assignment and prevalence. (Main §2.2 p.3.)
4. [STATED] Allele counts follow Binomial/Beta-Binomial PyClone emission conditional on fixed CN/purity and enumerated genotype states. (Supplement S1.1–S1.2.)
5. [STATED] Outlier CCF has a uniform prior and per-datum Bernoulli prior `nu`; [IMPLEMENTED] pre-clusters are all-or-none and their log prior is multiplied by cluster size.
6. [INFERRED] `alpha`, grid resolution, root penalty and outlier prior can materially affect node number, topology and exclusion, but no broad sensitivity analysis is supplied.
7. [INFERRED] Likelihood-weighted posterior metrics and the common PhyClone LPR evaluator provide consistency but may still favour assumptions shared with PhyClone.

## Computational assumptions

1. [STATED] WGS-scale work practically requires pre-clustering; unclustered complexity rises sharply. (Main §2.2.2 p.3.)
2. [STATED] Fixed-order SMC cannot reach all trees; auxiliary-order PG is required. (Main §2.3.1 p.4.)
3. [INFERRED] Theoretical reachability does not establish adequate finite-chain mixing. Current default is one chain, while README recommends at least four.
4. [STATED/IMPLEMENTED] Fully adapted proposal is exponential in current root count; semi-adapted samples one subset to trade proposal quality for cost.
5. [STATED] DP cost depends on nodes, mutations, samples, grid and out-degree: `O(V(NL+CSL²))`. (Supplement S1.5 p.5.)
6. [IMPLEMENTED] Grid 101, bounded caches and optional FFT are performance choices; results remain discretized.
7. [STATED/IMPLEMENTED] Paper trials had a 48-hour cap. The checkout has an application-level `--max-time` stop, but the benchmark timeout preprocessing and missing-value/penalty handling are absent; the paper’s 48-hour results therefore cannot be reproduced from this repository.

## Dataset and evaluation assumptions

1. [STATED] Synthetic data were pre-clustered with PyClone-VI; the five later-stage methods listed above—CONIPHER, Pairtree, Orchard, fastBE, and PhyClone—share those pre-clusters. The TSSB-Low PhyloWGS comparison is not under that common preprocessing because PhyloWGS was not listed as receiving the pre-clusters. HGSOC shares original-study clusters. Tree-builder effects are therefore conditional on a common preprocessing stage for those five methods.
2. [STATED] V/AD use a selected point tree; RRE/LPR use weighted unique solutions. A single MAP tree can conceal multimodality.
3. [STATED] RRE requires perfect-phylogeny-compatible truth and is omitted on CONIPHER datasets.
4. [STATED] HGSOC evaluation removes mutations not defining ground truth and collapses newly empty nodes, potentially hiding over-resolution.
5. [INFERRED] Failure penalties (0 for point accuracy, 1/1.5 for posterior metrics) affect statistical contrasts; complete-case descriptive means are not test means.
6. [INFERRED] The Pairtree benchmark is an incomplete factorial grid and pooled results apply only to retained conditions.

## Author-stated limitations

- Bulk sequencing only partially identifies topology, even across regions. (Main Introduction pp.1–2.)
- Mutation loss violates basic ISA/additivity. (Main Introduction p.2; §3.1 p.6.)
- The underlying PyClone genotype correction cannot model subclonal CNV regions. (Main Discussion p.8.)
- Fixed SMC order restricts reachable trees without Particle Gibbs. (Main §2.3.1 p.4.)
- Direct WGS without pre-clustering is computationally difficult. (Main §2.2.2 p.3.)
- The FS-CRP loss ablation is intentionally biased toward PhyClone. (Main §3.1 p.6.)

## Inferred limitations

- [INFERRED] A false merge in pre-clustering sets a hard resolution ceiling because PhyClone cannot split it.
- [INFERRED] Outlier-labelled mutations lose phylogenetic placement; a biologically important loss event is represented only as exclusion.
- [INFERRED] A strong root penalty can dominate weak data and underrepresent genuine multi-root uncertainty.
- [INFERRED] Wrong purity/CN can create confident but incorrect CCF evidence; systematic errors need not look like outliers.
- [INFERRED] Coarse grids bias scoring/prevalence; fine grids raise convolution cost.
- [INFERRED] Consensus/MAP outputs compress posterior uncertainty, and exported prevalence lacks intervals.
- [INFERRED] Only three HGSOC patients, with one strongest loss case, cannot support broad clinical generalization.

## Implementation-specific limitations and conflicts

1. **Published/implemented outlier mismatch — UNRESOLVED.** A single uniform integral is published, but 0.7.0 and 0.8.0 compute a triangular double sum. The constant-integrand normalization check fails.
2. **Subtree PG — UNRESOLVED.** Source TODO questions a missing subtree-selection probability; default is off.
3. **Current bootstrap+outlier — confirmed 0.8.0 regression.** Sampled branch masses differ from logged proposal masses; paper’s semi-adapted path is unaffected.
4. **CLI/API divergence.** Burn-in/iterations/precision and loss activation differ; critical parameters should be explicit.
5. **Input concordance edge case.** Main-input and cluster-file mutation sets are not robustly cross-validated; malformed duplicate/sample patterns may omit or misalign data.
6. **Validation gaps.** Full tests could not run in the current Python/dependency environment, and no paper evaluation pipeline is included.

## Failure-case matrix

| Condition | Why failure is plausible | Evidence / mitigation |
|---|---|---|
| Clone count far exceeds informative samples | Many sibling/ancestor structures satisfy prevalence constraints | Main §3.3; Figs.S12–S13. Add independent samples or lower claim ceiling. |
| False-merged pre-cluster | Atomic `DataPoint` cannot split | Main §2.2.2; `data/pyclone.py:82-115`. Improve/pre-audit clustering. |
| Subclonal or wrong CN | Emission assumes fixed clonal locus genotype candidates | Main Discussion p.8; S1.1–S1.2. Exclude/flag affected regions or use richer CN model. |
| Wrong tumour purity | Expected VAF shifts in every locus | `math_utils.py:179-244`; missing input silently defaults to 1.0. Supply validated purity. |
| Low depth / few mutations | Broad emission leaves multiple trees compatible | likelihood structure. Report posterior alternatives, not only MAP. |
| High `nu` | Compatible noisy evidence may be discarded | outlier Bernoulli prior. Perform prior sensitivity. |
| Low `nu` | Loss/error datum can distort clustering/topology | Fig.2/S4. Inspect posterior outlier counts and sensitivity. |
| Explicit loss-edge question | Model has no loss-edge variable | Main §2.2.3 and bucket `-1`. Use another mechanistic model or phrase as incompatibility. |
| Many current forest roots | Fully adapted proposal costs `2^R`; root penalty may dominate | S1.6.2/code. Use semi-adapted and diagnose roots/mixing. |
| Deep trees / long sequences | PG genealogy degeneracy freezes early structure | S1.6.4. Multiple chains; subtree PG is intended but currently unresolved. |
| Bootstrap + outliers in 0.8.0 | incorrect proposal/log-q weights | current `bootstrap.py`; avoid path until fixed. |
| Posterior multimodality | MAP/consensus hides competing topologies | HDF5/topology report. Report multiple topology weights. |
| CN perturbation interpretation | S14 lacks condition label | do not claim condition-specific numerical trend from XLSX. |
| Timeouts/missing solutions | Penalty choices alter comparisons | S2/S3/S5/S28/S31/S34. Report failures and penalty convention. |

## Practical evidence ceiling

PhyClone is best described as a topology-aware Bayesian deconvolution system that is often accurate and robust to certain incompatible mutations, conditional on input CN/purity and pre-clustering. It is not an explicit mutation-loss history model, does not eliminate partial identifiability, and is not computationally cheap in absolute terms.
