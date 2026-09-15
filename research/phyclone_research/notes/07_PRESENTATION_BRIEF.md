# PhyClone presentation brief

## One sentence

PhyClone jointly infers mutation clusters and clone ancestry from bulk-tumour sequencing by combining a tree-structured non-parametric prior, CN/purity-aware allele likelihood, collapsed prevalence integration and Particle-Gibbs SMC, with an outlier state that accommodates—but does not mechanistically locate—mutation loss.

## 30-second version

Bulk sequencing mixes clones, so clustering mutations by prevalence does not reveal ancestry and often leaves several compatible trees. PhyClone places a Bayesian prior directly on mutation clusters and their forest/tree, sums clone masses down each descendant subtree to predict cellular prevalence, integrates those masses out efficiently, and explores tree space with Particle Gibbs. Across synthetic benchmarks it is usually among the most accurate methods, and in one validated HGSOC patient it best recovers a mutation-loss pattern; the trade-offs are substantial computation, dependence on CN/purity and pre-clustering, and unresolved outlier-implementation details.

## Three-minute version

1. **Problem:** Bulk specimens are mixtures. A mutation’s VAF/CCF constrains ancestry but does not uniquely determine it; deletion can violate the infinite-sites inheritance rule.
2. **Gap:** Many approaches either cluster without jointly inferring topology, return limited uncertainty, or struggle with large posterior spaces.
3. **Idea:** FS-CRP jointly chooses mutation partition and forest. Each sample receives Dirichlet clone masses, and mutation CCF is the sum of masses in its descendant subtree.
4. **Likelihood/inference:** PyClone corrects read counts for CN and purity. A grid dynamic program integrates prevalence; semi-adapted bottom-up SMC inside auxiliary-order Particle Gibbs explores variable-size trees.
5. **Robustness:** An outlier state removes incompatible mutation/cluster evidence from the tree; it does not infer a deletion edge.
6. **Evidence:** On TSSB-Low PhyClone significantly wins every comparator in AD F-score. Across TSSB-High, Pairtree and CONIPHER-NN, no competitor significantly wins AD. In HGSOC patient 3 it is uniquely best on both point metrics under WGS and WGS+targeted inputs.
7. **Boundaries:** Pre-clusters cannot split, CN/purity are fixed, recorded runtime is often materially higher than fastBE and some other baselines, memory is also higher in several complete-case summaries, but XLSX memory units and some resource cells are missing; real evidence is three patients, and current outlier marginalization differs from the publication formula.

## Suggested 10-slide talk (10–15 minutes)

### Slide 1 — The question: what clones are present, and who descended from whom?

- **Key message:** Bulk sequencing observes mixtures, not cells or lineages.
- **Evidence:** Main Introduction pp.1–2.
- **Suggested visual:** Two bulk samples containing the same three colored clones at different proportions, beside two competing compatible trees.
- **Speaker point:** “The same mutation clusters can fit more than one ancestry; uncertainty is part of the biological result.”

### Slide 2 — Why clustering alone is insufficient

- **Key message:** Similar CCF groups mutations, while cross-sample prevalence constraints only partially order the groups.
- **Evidence:** Main Introduction pp.1–2; Supplement Figs.S5–S7 for reachability intuition.
- **Suggested visual:** CCF matrix with an ancestor ≥ descendant constraint and a sample-wise order reversal proving two branches.
- **Speaker point:** Separate three tasks: estimate CCF, cluster mutations, infer topology.

### Slide 3 — PhyClone in one pipeline

- **Key message:** Reads/CN/purity → optional pre-clustering → Bayesian tree posterior → MAP/consensus/topologies.
- **Evidence:** Main Fig.1 p.2; current `cli.py`, `run.py`, `process_trace/`.
- **Suggested visual:** Reuse the architecture flow from `01_PAPER_BIG_PICTURE.md`.
- **Speaker point:** WGS practicality relies on external pre-clustering; PhyClone may merge but cannot split supplied clusters.

### Slide 4 — Core model: FS-CRP plus subtree prevalence

- **Key message:** Cluster number, assignment and topology are one random object.
- **Evidence:** Main §2.1–§2.2 pp.2–3; Supplement S1.3 pp.2–3.
- **Suggested visual:** Small dummy-rooted forest with node-exclusive masses `rho_v`; shade a subtree to show `rho_bar_v=sum descendants rho`.
- **Speaker point:** This identity turns the biological inheritance rule into the statistical constraint.

### Slide 5 — From reads to tree score

- **Key message:** PyClone emission accounts for purity/CN; a dynamic program integrates clone masses.
- **Evidence:** Supplement S1.1–S1.5 pp.1–5; Algorithm 1 p.13; `math_utils.py`, `tree/utils.py`.
- **Suggested visual:** Three-population VAF mixture feeding a post-order child-convolution tree.
- **Speaker point:** State dimension does not grow with sample count, but compute still scales with samples/grid: `O(V(NL+CSL²))`.

### Slide 6 — Exploring tree space

- **Key message:** Semi-adapted bottom-up SMC proposes trees; Particle Gibbs resamples admissible mutation order to escape fixed-order restrictions.
- **Evidence:** Main §2.3 pp.3–4; Supplement S1.6 pp.6–7; Figs.S4–S8.
- **Suggested visual:** SMC particles over time with one retained conditional path.
- **Speaker point:** Reassignment and prune-regraft improve mixing but do not change node count; PG does.

### Slide 7 — Mutation loss as robust exclusion

- **Key message:** Tree-incompatible mutations can enter an outlier bucket rather than distort the tree.
- **Evidence:** Main §2.2.3 p.3; Supplement S1.7 pp.7–8; Main Fig.2; S4/S19.
- **Suggested visual:** A mutation deleted on a descendant branch, then routed to outlier bucket `-1`.
- **Speaker point:** At 20% simulated loss, mean AD is 0.9557 with outliers versus 0.7149 without. This is a favourable internal ablation and does not localize the loss edge.

### Slide 8 — Synthetic evidence: accurate, but not cheap

- **Key message:** PhyClone is usually top-tier for topology; computational cost is a real trade-off.
- **Evidence:** Main Figs.3–5; S2/S3/S5/S6/S7 and S15–S25.
- **Suggested visual:** Two-axis summary: AD ranking versus mean runtime, highlighting TSSB-Low PhyClone AD 0.9835/time 253 s, PhyloWGS AD 0.9046/time 37,563 s, fastBE AD 0.9014/time 3.33 s.
- **Speaker point:** Preserve exceptions: CONIPHER wins TSSB-High V; under CONIPHER-noise, three methods are statistically tied in AD.

### Slide 9 — Real evidence: HGSOC patient 3

- **Key message:** PhyClone best matches the validated patient-3 tree under both count sources.
- **Evidence:** Main Fig.6 pp.8–9; Supplement Table S1 p.27; S10/S11.
- **Suggested visual:** Ground truth and PhyClone/competitor patient-3 trees; annotate two excluded lost clusters.
- **Speaker point:** WGS V/AD 0.845/0.819; WGS+targeted 1.0/0.929. This is one key case in a three-patient cohort.

### Slide 10 — What to believe, and what remains open

- **Key message:** Strong topology-aware framework and evidence, bounded by modelling and implementation risks.
- **Evidence:** Main Discussion p.8; code validation.
- **Suggested visual:** Two-column “Supported / Not established.”
- **Speaker point:**
  - Supported: joint clustering/topology, effective multi-sample constraints, strong benchmark AD, robust exclusion case.
  - Not established: universal superiority, explicit loss-edge history, subclonal CN, condition-specific CN-error flatness, cheap computation.
  - Engineering warning: paper used 0.7.0; current is 0.8.0. Published outlier integral and both versions’ implementation disagree; 0.8.0 bootstrap+outlier has a separate regression.

## Optional backup slides

1. **Formula sheet:** `xi(G,rho_bar,t)`, descendant-sum identity and collapsed integral.
2. **Statistical detail:** failure penalties, Friedman/Nemenyi `p<0.01`, and posterior metric results.
3. **Implementation map:** paper 0.7.0 versus current 0.8.0 defaults and risks.
4. **Failure cases:** pre-cluster false merge, subclonal CN, poor PG mixing, outlier-prior sensitivity.

## Questions likely from a professor

**Does PhyClone infer mutation loss?**  It infers that a mutation/pre-cluster is incompatible with the tree and assigns it to an outlier state. It does not infer the deletion edge or a mechanistic loss history.

**Why marginalize prevalence?**  It removes continuous sample-specific nuisance parameters from tree-state exploration and lets more samples add evidence without enlarging the sampled discrete state dimension. Evaluation still costs more with samples.

**What is actually non-parametric?**  The CRP gives an unknown number of mutation clusters/nodes; the topology is coupled through the forest prior.

**Could pre-clustering bias the result?**  Yes. False splits may be repaired by merging; false merges are irreversible downstream.

**Is PhyClone always best?**  No. CONIPHER has significantly better TSSB-High V-measure; several AD comparisons are ties, and faster methods use far fewer resources.

**Can the paper results be regenerated from this checkout?**  Not fully. The checkout lacks the benchmark/statistics pipeline, and current code is 0.8.0 rather than the benchmarked 0.7.0.

**What is the highest-priority technical follow-up?**  Derive/test the outlier marginal against the published uniform integral, then correct/test the current bootstrap+outlier proposal; keep subtree PG disabled until its transition correction is resolved.
