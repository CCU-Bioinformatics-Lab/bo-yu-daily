# Evidence matrix

`—` means that source is not the appropriate evidence type, not necessarily that the claim is false. Version-sensitive implementation cells refer to checkout 0.8.0 unless explicitly marked 0.7.0.

| Claim | Main paper | Supplement | XLSX | Code | Type | Confidence |
|---|---|---|---|---|---|---|
| Bulk samples only partially identify clone ancestry; posterior uncertainty is scientifically relevant | Intro pp.1–2 | Figs.S5–S7 pp.16–18 illustrate ordering/tree ambiguity | — | trace preserves multiple states | STATED | HIGH |
| FS-CRP jointly models unknown mutation partition and rooted forest/tree | §2.1 pp.2–3 | S1.3 pp.2–3 | — | `tree/distributions.py:43-65` | STATED/IMPLEMENTED | HIGH |
| In-tree mutation CCF is descendant-subtree sum of clone-exclusive prevalences | §2.2 p.3 | S1.3 p.3 | — | `tree/tree_node.py:59-69`; `process_trace/map.py:127-157` | STATED/IMPLEMENTED | HIGH |
| Allele likelihood accounts for reads, CN and purity via PyClone genotype mixture | §2.2 p.3 | S1.1–S1.2 pp.1–2 | — | `utils/math_utils.py:179-244`; `data/pyclone.py:299-403` | STATED/IMPLEMENTED | HIGH |
| CN and purity are fixed inputs, not inferred | implied by §2/Fig.1 | S1.1 pp.1–2 | — | schemas and `data/pyclone.py` | IMPLEMENTED/INFERRED | HIGH |
| Pre-clusters cannot split but may merge | §2.2.2 p.3 | — | common preprocessing described in §2.4.2 | `data/pyclone.py:82-115` | STATED/IMPLEMENTED | HIGH |
| Collapsing prevalence removes continuous variables from tree sampling | §2.2.1 p.3; Discussion p.8 | S1.4–S1.5 pp.4–5 | posterior metrics use collapsed scores | `tree/utils.py`; `tree/distributions.py:151-163` | STATED/IMPLEMENTED | HIGH |
| Detailed DP cost is `O(V(NL+CSL^2))`, not generally just `O(V^2)` | shorthand in §2.2.1 p.3 | S1.5 p.5 | — | per-sample grid convolution `tree/utils.py:28-68` | STATED/IMPLEMENTED | HIGH; resolved wording conflict |
| Final score strongly prefers one subroot (`C=1000`) | not detailed | S1.3.1 pp.3–4 | — | `tree/distributions.py:12-14,67-121` | STATED/IMPLEMENTED | HIGH |
| Semi-adapted bottom-up SMC inside auxiliary-order PG is the core sampler | §2.3–§2.3.1 pp.3–4 | S1.6–S1.6.3 pp.6–7 | benchmark config stated, not raw | `smc/kernels/semi_adapted.py`; `mcmc/particle_gibbs.py` | STATED/IMPLEMENTED | HIGH |
| Outlier state accommodates inheritance violations but does not infer loss edges | §2.2.3 p.3 | S1.7 pp.7–8 | loss ablation S4/S19; HGSOC S10/S11 | bucket `-1`, no loss-edge variable | STATED + INFERRED boundary | HIGH |
| Published outlier integral equals current code | single integral §2.2.3 | single integral S1.7 | — | triangular double sum `data/base.py:29-34`, both versions | INFERRED—REJECTED | HIGH that equivalence is unsupported; mismatch unresolved |
| Data-informed loss prior uses chromosome concentration, 10,000 draws and 0.0001/0.4 priors | benchmark options §2.4.2 p.5 | S1.7.1 p.8 | — | `cluster_outlier_probabilities.py:24-151`, with extra filters | STATED/IMPLEMENTED | HIGH; APPROXIMATE details |
| Outlier-enabled PhyClone resists simulated loss | §3.1/Fig.2 p.6 | — | S4 `A2:M601`; S19 `A2:F5` | feature exists; experiment pipeline absent | STATED | HIGH within biased ablation |
| TSSB-Low: PhyClone beats every method in AD and PhyloWGS is far slower | §3.2/Fig.3 pp.6–7 | Figs.S10–S11 pp.21–22 | S2/S15/S16 | benchmark pipeline absent | STATED | HIGH |
| No method significantly beats PhyClone in AD across TSSB-High/Pairtree/CONIPHER-NN | §3.3/Fig.4 pp.7–8 | Fig.S10/S12–13 | S18/S21/S23 | — | STATED | HIGH; one raw S23 direction conflict is non-decision-changing |
| CONIPHER significantly beats PhyClone in TSSB-High V-measure | §3.3 p.7 | — | S18 row 15: `p=2.90e-8` | — | STATED | HIGH |
| CONIPHER-noise top AD group is PhyClone/CONIPHER/fastBE | §3.4/Fig.5 pp.7–8 | — | S7/S25 | — | STATED | HIGH |
| CN-error pooled ranking favors PhyClone in AD; the paper reports minimal impact across perturbation levels, but condition-specific flatness is not independently reconstructible from S14 because error-level labels are absent | §3.4 p.7 | Fig.S14 p.25 | S14/S27 supports pooled rank but lacks error level | — | STATED for pooled; INFERRED/UNRESOLVED for trend | MEDIUM |
| HGSOC patient 3 is best reconstructed by PhyClone and two lost clusters are excluded | §3.5/Fig.6 pp.8–9 | Table S1 p.27 | S10/S11 exact metrics | outlier structure only; no experiment data | STATED | HIGH for case, LOW for generalization |
| Current exported prevalence is posterior mean/interval | main says MAP or sampling may reinstate, §2 p.2 | — | — | only max-product grid backtracking `process_trace/map.py` | INFERRED—REJECTED | HIGH |
| Current 0.8.0 bootstrap+outlier proposal is self-consistent | — | generic bootstrap description S1.6.2 | — | sampled 0.1/0.35/0.55 vs logged 0.1/0.45/0.45 | INFERRED—REJECTED | HIGH; current regression |
| Subtree PG formal correctness is verified | — | claims correction, S1.6.4 p.7 | — | TODO in 0.7.0/0.8.0 | INFERRED—REJECTED | MEDIUM-HIGH; UNRESOLVED |
| Current operational defaults equal paper benchmark settings | benchmark 0.7.0 §2.4.2 p.5 | — | — | 0.8.0 CLI/API differ | INFERRED—REJECTED | HIGH |
| PhyClone is universally superior and computationally cheap | no such bounded claim | — | accuracy exceptions and resource cost | runtime structure/cost | INFERRED—REJECTED | HIGH |

## Conflict register

### Resolved

1. **Dummy-root dimension:** supplement’s `|b|=|V|` after adding root conflicts with main `|b|+1=|V|`; code includes root mass. Resolve as supplement notation error.
2. **Complexity:** use supplement `O(V(NL+CSL²))`; main `O(V²)` is incomplete shorthand.
3. **Bootstrap regression provenance:** 0.8.0 has mismatched sampling/log probabilities; 0.7.0 was consistent and paper benchmark used semi-adapted. Resolved as current-version regression, not a paper-result mechanism.
4. **“Significant” threshold:** all worksheet flags agree with the main paper’s explicit `p<0.01`; no hidden multiplicity correction is needed.
5. **Pairtree count:** 576 is explained by omission of `K=30/100` with `M=1/3`; the paper does not state that exclusion rule.

### Unresolved

1. **Outlier marginal:** publication single uniform integral versus code triangular double sum in both versions; likely implementation mismatch.
2. **Subtree PG:** source TODO questions selection-probability term; path off by default.
3. **CONIPHER-NN fastBE versus PhyClone AD:** raw mean direction conflicts with S23 row 8, although `p=0.94951` keeps the same non-significant conclusion.
4. **Friedman exact p-values:** several do not reproduce exactly from visible workbook cells; decisions remain identical.
5. **CN-error trend:** error-level labels missing from S14.
6. **Timeout/statistics pipeline:** absent from repository, so penalties were inferred algebraically rather than read from code.
