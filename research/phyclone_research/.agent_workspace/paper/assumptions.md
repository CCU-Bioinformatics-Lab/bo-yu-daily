# Assumptions, limitations, and failure cases from the main paper

## Biological assumptions

- [STATED] **Infinite-sites inheritance for in-tree SNVs.** A mutation originating at v is propagated to all descendants; cellular prevalence is the v-subtree mass。（Introduction, pp.1–2；§2.1–2.2, pp.2–3）
- [STATED] **Shared evolutionary history within cluster.** SNVs in a cluster are assumed to share evolutionary history and map one-to-one from cluster to node。（§2.1, p.2）
- [STATED] **Related samples share a phylogeny.** Multi-region samples differ in prevalence vectors but use the same mutation/tree structure。（§2/§2.2, pp.2–3）
- [STATED] **Mutation loss is possible.** The basic additivity model can fail under genomic deletion; robust extension permits affected SNVs to be outliers。（Introduction, p.2；§2.2.3, p.3）
- [INFERRED] **Outlier ≠ mechanistic loss reconstruction.** Since outliers get unconstrained prevalence and no loss edge, model support for “loss” is phenomenological, not a unique biological event history。

## Statistical assumptions

- [STATED] Mutation partition follows CRP; topology conditional on partition is selected uniformly from directed rooted forests; node prevalence is Dirichlet on simplex。（§2.1, pp.2–3）
- [STATED] Allele counts follow the PyClone emission conditional on cellular prevalence, CN and tumour content。（§2.2, p.3）
- [STATED] Basic likelihood factorizes over mutations conditional on latent tree/partition/prevalence。（§2.2 basic likelihood, p.3）
- [STATED] Outlier prevalence has Uniform prior on `[0,1]`; each SNV has prior outlier probability `nu_n`。（§2.2.3, p.3）
- [INFERRED] `alpha`, `kappa`, `nu` influence cluster complexity, clone mass and robust exclusion; the main paper provides benchmark `nu` values but no sensitivity analysis in the cited main figures。
- [INFERRED] Posterior accuracy depends on allele-count/CN/purity calibration; systematic biases coherent across samples can yield confident wrong topology rather than obvious outliers。

## Computational assumptions

- [STATED] For WGS-size inputs, pre-clustering is practically recommended; without it complexity rises drastically。（§2.2.2, p.3）
- [STATED] The bottom-up SMC proposal only considers adding to existing roots or forming a new node above a random subset of roots at each step; PG resampling of order restores reachability in theory。（§2.3–2.3.1, pp.3–4）
- [INFERRED] Reachability is not the same as adequate finite-run mixing; 4 chains/5000 iterations/100 particles are experimental choices, and main paper provides no convergence diagnostics。
- [STATED] Each method/trial was capped at 48 h；timeouts may affect observed scalability。（§2.4.2, p.5）

## Dataset/evaluation assumptions

- [STATED] Synthetic data were pre-clustered with PyClone-VI; the pre-clustered inputs were supplied to CONIPHER, Pairtree, Orchard, fastBE and PhyClone. PhyloWGS was not listed as receiving these pre-clusters and is the non-preclustered comparator in TSSB-Low. HGSOC shares clusters from the original study。（§2.4.2, p.5）
- [STATED] V-measure and AD F-score use a selected single tree; posterior metrics use likelihood-weighted unique solutions。（§2.4.2–2.4.3, pp.5–6）
- [STATED] RRE presumes perfect-phylogeny-compatible data; omitted for CONIPHER datasets because enumeration fails。（§2.4.3, p.6）
- [STATED] HGSOC metrics prune inferred solutions to ground-truth-defining mutations and collapse emptied nodes。（§2.4.1.5, pp.5–6）

## Author-stated limitations

1. [STATED] Bulk data can only partially resolve topology; even multi-region sampling gives limited identifiability。（Introduction, pp.1–2）
2. [STATED] Basic additivity/ISA is violated by mutation loss。（Introduction, p.2；§3.1, p.6）
3. [STATED] **Key PhyClone limitation:** underlying PyClone mutational-genotype correction cannot model subclonal CNV regions。（Discussion, p.8）
4. [STATED] Fixed SMC data order excludes some trees; auxiliary-order Particle Gibbs is required。（§2.3.1, p.4）
5. [STATED] Direct un-preclustered WGS analysis has drastically larger computational complexity。（§2.2.2, p.3）

## Inferred limitations / failure cases

| Condition | Why it may fail | Evidence/reasoning |
|---|---|---|
| True cluster split hidden by pre-clustering false merge | PhyClone never splits a supplied pre-cluster | [INFERRED] from §2.2.2, p.3 |
| Number of clones far exceeds informative samples | Prevalence constraints weakly identify relationships; observed degradation tracks nodes/samples ratio | [STATED]/[INFERRED], §3.3, p.7 |
| Subclonal CNV changes expected VAF | PyClone genotype model cannot represent it, corrupting cellular-prevalence likelihood | [STATED], Discussion, p.8 |
| Multiple non-loss violations (CN error, contamination, sequencing artifacts) | Same generic outlier state can absorb them; “lost” label is not causally unique | [INFERRED] from §2.2.3 and §3.4 |
| Loss pattern requires explicit placement/recurrent events | No loss-edge latent variable in main formula; output only excludes SNV | [INFERRED], §2.2.3/Fig.6 |
| Low-depth or purity/CN misspecification | Emission provides weak or biased cellular-prevalence evidence, leaving many trees compatible | [INFERRED] from input/likelihood and motivation |
| Finite PG/SMC poor mixing | All trees may be reachable but modes can remain hard to traverse; added moves do not change node count | [INFERRED] from §2.3.1–2.3.2 |
| Outlier prior too high | Compatible but noisy SNVs may be removed, reducing tree evidence | [INFERRED] from `nu_n` role |
| Outlier prior too low | Loss/error SNVs force wrong assignments/topology | [INFERRED] from `nu_n` role and Fig.2 |
| Single-tree reporting hides posterior ambiguity | MAP/top tree may overstate certainty when posterior is multimodal | [INFERRED] from Bayesian objective vs §2.4.2 selection |
| HGSOC post-processing | Removing non-ground-truth SNVs/collapsing nodes may hide over-resolution or assignment mistakes | [INFERRED] from §2.4.1.5 |

## Experimental caveats against overclaiming

- [STATED] FS-CRP-loss ablation is explicitly biased toward PhyClone。
- [INFERRED] All methods receiving common PyClone-VI clusters confounds preprocessing robustness with tree-builder robustness, especially CN perturbation。
- [INFERRED] 48-h caps can turn runtime difficulty into missing/partial outcomes; main text does not state handling。
- [INFERRED] Friedman–Nemenyi non-significance is not evidence of equivalence。
- [INFERRED] Only three real HGSOC patients and one detailed loss case sharply limit biological generalization。
