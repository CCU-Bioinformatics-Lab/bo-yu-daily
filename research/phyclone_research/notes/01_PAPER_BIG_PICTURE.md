# PhyClone: the big picture

## One-sentence summary

[STATED] PhyClone is a Bayesian non-parametric method that takes allele counts, copy number and tumour content from one or more related bulk-tumour samples and jointly infers mutation clusters and their clone phylogeny, using an FS-CRP prior, a collapsed prevalence likelihood, Particle-Gibbs SMC, and an outlier state for mutations incompatible with tree inheritance. (Main Abstract; §2–§2.3, pp.2–4; Discussion, p.8.)

## Problem → gap → core idea → evidence → contribution

### Problem and importance

[STATED] Cancer progression, treatment resistance and metastasis are shaped by the composition and ancestry of genetically distinct cell populations. Single-cell sequencing is informative but costly and technically difficult; bulk sequencing is common but mixes clones, so their phylogeny must be computationally deconvolved. (Main Introduction, p.1.)

### Existing gap

[STATED] Mutation clustering by similar cellular prevalence can identify populations but does not itself determine their ancestry. Under the infinite-sites assumption (ISA), an ancestor mutation cannot have lower cellular prevalence than its descendant, yet one or a few bulk samples often leave sibling versus ancestor relationships indistinguishable. Cross-sample prevalence reversals add information but still leave a set of compatible trees. Genomic deletion can additionally remove mutations and violate the additivity constraints. (Main Introduction, pp.1–2.)

[INFERRED] The real target is therefore not a single plausible tree but a posterior over unknown cluster count, assignment and topology while integrating high-dimensional sample-specific prevalence nuisance parameters.

### Core idea

[STATED] PhyClone couples four components:

1. A forest-structured Chinese restaurant process (FS-CRP) jointly assigns mutations to an unknown number of clone nodes and places those nodes in a forest/tree.
2. Clone-exclusive prevalence follows a Dirichlet prior; a node mutation’s cellular prevalence is the sum over that node’s descendant subtree, imposing phylogenetic inheritance.
3. These prevalences are integrated out on a discrete grid by dynamic programming, leaving a collapsed score over clustering/topology.
4. Bottom-up SMC is embedded in Particle Gibbs and resamples the mutation order so the chain can explore variable-size tree states. (Main §2.1–§2.3, pp.2–4; Supplement S1.3–S1.6, pp.2–7.)

[STATED] An optional outlier state gives tree-incompatible mutations an independent PyClone emission integrated over a uniform cellular-prevalence prior. It is motivated by mutation loss, CN error and allele-count noise. (Main §2.2.3, p.3; Supplement S1.7, pp.7–8.)

### Architecture

```text
Per mutation × sample:
ref/alt reads + major/minor/normal CN + tumour content
                         ↓
optional external pre-clustering (recommended at WGS scale)
                         ↓
PyClone likelihood grid over cellular prevalence
                         ↓
FS-CRP: mutation partition + rooted forest/dummy-root tree
                         ↓
Dirichlet clone masses → descendant-sum cellular prevalences
                         ↓
grid DP integrates prevalence; score includes priors/outliers
                         ↓
semi-adapted SMC inside Particle Gibbs + mixing moves
                         ↓
HDF5 posterior trace → MAP / consensus / topology report
                         ↓
Newick tree + mutation/clone and sample-prevalence TSVs
```

The pre-clustering constraint is asymmetric: supplied clusters cannot split, but several supplied clusters may merge into one inferred node. (Main §2.2.2, p.3; implemented in `data/pyclone.py:82-115`.)

## What the experiments ask

| Experiment | Question | Main evidence |
|---|---|---|
| FS-CRP loss ablation | Does the outlier state protect against simulated mutation loss? | Main Fig.2; XLSX S4/S19 |
| TSSB-Low | Is posterior/tree reconstruction accurate and scalable under a Bayesian generator? | Main Fig.3; Supplement Figs.S10–S11; XLSX S2/S15–16/S31–33 |
| TSSB-High, Pairtree, CONIPHER-NN | Does performance transfer across mutation scale and generators? | Main Fig.4; Supplement Figs.S10/S12–13; XLSX S3/S5/S6 and tests |
| CONIPHER-noise | Is the method competitive when ISA is violated? | Main Fig.5; XLSX S7/S24–25 |
| CN perturbation | Does sample-specific CN error change relative performance? | Supplement Fig.S14; XLSX S14/S26–27 |
| HGSOC | Can the outlier mechanism recover validated real mutation-loss patterns? | Main Fig.6; Supplement Figs.S15–16/Table S1; XLSX S8–S13 |

## Results that survive cross-validation

- [STATED + XLSX] In the intentionally favourable FS-CRP loss ablation, outlier-enabled PhyClone stays accurate as loss rises: at 20% loss, mean AD F-score is 0.95570 versus 0.71486 without the outlier model (S4!A2:M601); the pooled AD advantage is 0.12396, `p=0.001` (S19!A2:F5).
- [STATED + XLSX] TSSB-Low gives PhyClone the strongest tested accuracy profile. Its nonblank mean V/AD is 0.99496/0.98350, it significantly beats every comparator in AD, and PhyloWGS is more than two orders of magnitude slower by the raw mean (253 versus 37,563 seconds; S2/S16).
- [STATED + XLSX] Across TSSB-High, Pairtree and CONIPHER-NN, no method significantly beats PhyClone in AD. The important exception is clustering: CONIPHER significantly beats PhyClone in TSSB-High V-measure. (S18/S21/S23.)
- [STATED + XLSX] On CONIPHER-noise, PhyClone, CONIPHER and fastBE form the top statistically indistinguishable AD group, all ahead of Orchard and Pairtree. This supports competitiveness, not superiority. (S7/S25.)
- [STATED + XLSX] In pooled CN-error data, PhyClone significantly beats all four alternatives in AD, but CONIPHER’s higher V-measure is not significant. Condition-specific robustness versus perturbation level is UNRESOLVED because S14 omits the error-level column. (S14/S27.)
- [STATED + XLSX] In HGSOC patient 3, PhyClone alone obtains the best V/AD for both WGS (0.84514/0.81905) and WGS+targeted (1.0/0.92935); the topology image supports its exclusion of two lost clusters. The cohort is only three patients. (Main Fig.6; S10/S11; Supplement Table S1.)

## Contribution, stated narrowly

[STATED] The methodological contribution is the combination of a tree-structured non-parametric clustering prior, efficient collapsed tree likelihood, and auxiliary-order Particle-Gibbs SMC, with optional pre-clustering and robust outlier handling. The empirical contribution is evidence that the system is usually among the most accurate evaluated approaches across several generators and can recover one strongly validated real loss case. (Main Abstract; §3.1–§3.5; Discussion, p.8.)

[INFERRED] The most distinctive contribution is not the PyClone emission alone, but the integration of that emission with topology-aware clustering and posterior exploration whose discrete state dimension does not grow with sample count.

## Claim ceiling

The evidence does **not** establish universal superiority, low computational cost, a population-level clinical claim, or a theorem that clone count cannot exceed sample count. “No significant competitor advantage” is not equivalence. Mutation loss is accommodated by excluding incompatible evidence; no deletion edge is inferred. Current code is v0.8.0, while reported benchmarks used v0.7.0.

