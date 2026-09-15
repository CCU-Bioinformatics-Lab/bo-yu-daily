# 主論文關鍵主張帳本

| ID | Claim | Type | Primary evidence | Confidence / boundary |
|---|---|---|---|---|
| C01 | Bulk mixture makes clonal phylogeny only partially identifiable; Bayesian posterior is appropriate to retain compatible trees. | [STATED] | Introduction, pp.1–2 | HIGH；conceptual motivation |
| C02 | FS-CRP jointly supplies a non-parametric prior over mutation partition and rooted forest/tree topology. | [STATED] | §2.1, pp.2–3 | HIGH |
| C03 | Node clonal prevalences have a Dirichlet prior and cellular prevalence is descendant-subtree sum, enforcing ISA inheritance/additivity. | [STATED] | §2.1–2.2, pp.2–3; cellular-prevalence identity | HIGH |
| C04 | PyClone emission uses allele counts corrected for copy number and tumour content. | [STATED] | §2.2, p.3 | MEDIUM in main paper；full equation deferred to supp |
| C05 | Marginalizing `rho` enables inference in a parameter space whose dimension does not depend on sample count. | [STATED] | §2.2.1, p.3; Discussion, p.8 | HIGH for state-space dimension, not runtime independence |
| C06 | Marginalized likelihood can be computed by DP in `O(|V|^2)`. | [STATED] | §2.2.1, p.3 | MEDIUM；derivation in supp S1.5 |
| C07 | Pre-clusters are indivisible, but distinct pre-clusters may merge in one PhyClone node. | [STATED] | §2.2.2, p.3 | HIGH |
| C08 | Outlier SNVs use Uniform cellular-prevalence prior and an independently integrated PyClone likelihood rather than tree-constrained prevalence. | [STATED] | §2.2.3, p.3; outlier joint likelihood | HIGH |
| C09 | Outlier assignment flags incompatibility; it does not explicitly localize mutation-loss edges. | [INFERRED] | absence of loss-edge variable in §2.2.3 formula; Fig.6 dashed inferred outliers | HIGH as model-structure inference; code/supp confirm needed |
| C10 | Bottom-up SMC is embedded in Particle Gibbs with mutation ordering as auxiliary variable to make all trees reachable. | [STATED] | §2.3–2.3.1, pp.3–4 | HIGH |
| C11 | SPR and node-reassignment moves improve mixing without changing node count. | [STATED] | §2.3.2, p.4 | HIGH |
| C12 | Outlier-enabled PhyClone is much more robust than PC-N as simulated loss rises, with no apparent no-loss penalty. | [STATED] | §3.1, Fig.2, p.6 | MEDIUM-HIGH；biased self-model simulation, no cross-method test |
| C13 | On TSSB-Low, PhyClone significantly wins all methods in AD F-score, RRE, LPR; wins PhyloWGS in V-measure; PhyloWGS is >10× slower. | [STATED] | §3.2, pp.6–7; Fig.3; supp Figs 10–11 | HIGH for reported tests; exact values outside main |
| C14 | Across TSSB-High/Pairtree/CONIPHER-NN, no method significantly beats PhyClone in AD F-score; CONIPHER beats it in TSSB-High V-measure. | [STATED] | §3.3, p.7; Fig.4 | HIGH; preserves exception |
| C15 | PhyClone tends to benefit more from increasing samples (higher medians, smaller IQRs), while all methods degrade as node/sample ratio rises. | [STATED] | §3.3, p.7; Figs 3–4; supp Figs 12–13 | MEDIUM；“tends”/descriptive, exact slope absent |
| C16 | One should not expect to resolve significantly more clones than bulk samples. | [STATED] | author interpretation, §3.3, p.7 | MEDIUM；empirical heuristic, not theorem |
| C17 | On CONIPHER-noise AD F-score, PhyClone/CONIPHER/fastBE are indistinguishable and all beat Pairtree/Orchard. | [STATED] | §3.4, Fig.5, p.7 | HIGH |
| C18 | Apparent robustness to CN perturbation likely comes partly from shared PyClone-VI preprocessing/genotype uncertainty. | [STATED] author hypothesis | §3.4, p.7; supp Fig.14 | MEDIUM/INFERENTIAL wording required |
| C19 | In HGSOC patient 3, PhyClone alone among discussed complete reconstructions excludes two lost SNV clusters in both count settings and matches ground truth better. | [STATED] | §3.5, pp.7–8; Fig.6, p.9; supp Table 1 | HIGH for reported case; small real cohort |
| C20 | PhyClone is robust and scalable to WGS and many samples. | [STATED] | Abstract; Discussion, p.8; §3.2–3.5 | MEDIUM-HIGH; WGS scalability relies on pre-clustering and 48-h benchmark |
| C21 | PhyClone's key stated limitation is inability of the underlying PyClone genotype correction to model subclonal CNV regions. | [STATED] | Discussion, p.8 | HIGH |
| C22 | “No significant competitor advantage” establishes universal superiority. | [INFERRED—REJECTED] | Statistical logic vs §2.4.3/§3 | HIGH that this overclaim is invalid |

## Claims requiring independent source validation

- C04/C06: full Supplement equations and implementation mapping.
- C12–C20: XLSX reconstruction for exact ranks, P-values, timeouts, raw distributions and figure mappings.
- C20: repository version/default verification; main paper only states benchmark v0.7.0 and settings.
- C09/C21: code inspection for actual outlier/CNV behavior.

