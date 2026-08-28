# Tumor-evolution multiplicity latent-variable review

> Scope: compare how tumor-evolution methods treat mutation multiplicity, with
> special attention to PhyClone and the active C++ runtime in this repository.
> This note records evidence and the design choices confirmed on 2026-08-28;
> remaining open items are explicitly marked below.
>
> Investigation date: 2026-08-28 (Asia/Taipei).

## Executive answer

The important correction is that “PhyClone has no multiplicity” is too strong.
The 2025 PhyClone paper does not expose a standalone `m` in its tree-level
`rho -> bar-rho` conversion, and its main model description does not present a
dedicated multiplicity output column. However, PhyClone explicitly delegates
the allele-count emission to a copy-number- and tumor-content-corrected PyClone
likelihood. The original PyClone genotype-aware model represents the number of
variant copies through a genotype state and sums over genotype states in the
likelihood. Thus there are two different statements:

1. **Tree-layer statement:** PhyClone uses clonal prevalence `rho` and
   descendant-summed cellular prevalence `bar-rho`; no separate multiplicity
   symbol is shown in that conversion.
2. **Emission-layer statement:** the inherited PyClone emission can represent
   multiplicity through the number of variant alleles in a genotype and can
   marginalize that genotype uncertainty.

The active repository is therefore not equivalent to “PhyClone without
multiplicity.” It now uses a minimal PhyClone/PyClone-VI-compatible version of
the second pattern: it derives finite CN/timing genotype candidates from the
canonical major/minor copy-number fields, computes copy-weighted `xi`, and
marginalizes those candidates inside the site likelihood. Multiplicity is not
part of the persistent candidate-tree state.

There is no primary paper found that mandates the complete combination used by
this repository. The literature contains all three broad patterns:

| Pattern | Meaning | Representative evidence |
|---|---|---|
| Multiplicity/genotype is an inferred state | The sampler or optimizer carries a discrete genotype/event choice, possibly including the number of mutated copies. | PyClone genotype states; PhyloWGS CNV/SSM event relationships; DeCiFer mutation multiplicity. |
| Multiplicity/genotype is marginalized in the emission | The method sums over plausible genotype or multiplicity states while inferring trees, clusters, or prevalence. | PyClone, PhyloSub, and the PhyClone emission layer. |
| No explicit multiplicity model | The method consumes VAF or copy-number-corrected cellular frequencies and builds a tree without a visible mutation-copy latent variable. | Pairtree and CITUP at the tree layer; simple diploid-heterozygous versions of earlier methods. |

## What “multiplicity” means here

In this note, mutation multiplicity means the number of copies at a locus that
carry the SNV in a cell genotype. It is not the total copy number, not CCF, and
not the number of cells carrying the SNV. DeCiFer defines an SNV-locus genotype
as `(x, y, m)`, where `x` and `y` are allele-specific copy numbers and `m` is
the number of copies carrying the mutation. The CCF is the fraction of cancer
cells whose genotype has `m >= 1`.[DeCiFer primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)

For a mixture of genotype states, the VAF is conceptually a copy-weighted
quantity:

$$
\operatorname{VAF}
=
\frac{\sum_{(x,y,m)}m\,g_{(x,y,m)}}
       {\sum_{(x,y,m)}(x+y)\,g_{(x,y,m)}}.
$$

The numerator is why CCF alone is insufficient when copy number or the number
of mutated copies varies. The same CCF can produce different VAFs under
different `m`, `x`, and `y`; conversely, the same VAF can be explained by
different CCF/multiplicity combinations. This is a scientific identifiability
statement supported by the genotype/VAF definitions in [DeCiFer](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)
and by the genotype-aware emission in [PyClone's primary supplementary note](https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf).

For this repository's active simplified emission, the code uses a different,
explicit formula:

$$
q_i(\phi,m)=
\operatorname{clamp}\!\left(
\frac{\rho_{\mathrm{ASCAT}}\,\phi\,m}
     {(1-\rho_{\mathrm{ASCAT}})\,2+\rho_{\mathrm{ASCAT}}\,\mathrm{total\_cn}_i},
10^{-12},1-10^{-12}\right).
$$

This formula is a **current-runtime observation**, not a universal VAF-to-CCF
law. It is implemented in [`expected_alt_probability`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:206), with the denominator prepared at load time in [`load_canonical_table`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:329). The target/spec document describes a richer genotype candidate `g` and `xi`, but explicitly says that the current C++/Python runtime is not synchronized with that target/spec.[`model.md`](/bip8_disk/boyu114/main_work/model.md:154)

## PhyClone: what is and is not absent

The PhyClone paper defines a vector `rho` of clonal prevalences, obtains
cellular prevalence `bar-rho` by summing a node and all nodes in its subtree,
and evaluates allele counts with a PyClone-based corrected likelihood. It then
integrates the node prevalence vector over its simplex for collapsed inference.
These are separate operations: descendant summation and prevalence
marginalization do not by themselves define whether the allele emission has a
multiplicity variable.[PhyClone primary paper, model and marginalization sections](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)

The original PyClone model makes the hidden genotype explicit. For each SNV it
uses categorical genotype states for normal, reference-cancer, and
variant-cancer populations. If `g` is a genotype, `c(g)` is its total copy
number and `b(g)` is its number of variant alleles; for example, `AAB` has
three total copies and one variant copy. The allele-count likelihood sums over
the possible genotype states with their prior probabilities.[PyClone primary supplementary note, genotype and likelihood equations](https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf)

The same supplementary note distinguishes several genotype-prior choices. In
particular, its total-copy-number prior allows any positive number of variant
copies, while its parental-copy-number prior allows one variant copy or a copy
count tied to a parental allele and interprets multiple variant copies as a
mutation that preceded amplification. This is multiplicity-aware modeling even
though the public PyClone result is primarily cellular-prevalence densities and
mutation-clustering probabilities rather than a standard per-SNV multiplicity
table.[PyClone primary supplementary note, prior strategies](https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf)

Therefore:

- “PhyClone's displayed `VAF/CCF` conversion has no explicit `m`” — **supported**.
- “PhyClone's full emission has no multiplicity/genotype uncertainty” — **not
  supported**; its stated PyClone emission can contain that uncertainty.
- “PhyClone's standard output is a multiplicity-posterior table like this repo's
  output” — **not established by the main paper**; the paper describes tree,
  cluster, and prevalence results, not the repository's exact artifact schema.

## Current repository behavior

The following are `current` implementation observations, verified against
source rather than relying only on daily notes.

| Behavior | Evidence | Status |
|---|---|---|
| Each loaded SNV stores internal multiplicity candidates and their prior; these are not canonical input columns. | [`Site` fields](/bip8_disk/boyu114/main_work/inference/include/tumor_tree_inference/model.hpp:10); forbidden legacy input columns and internal derivation are in [`model.cpp`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:24). | `current` |
| Candidates are derived from integer `major_cn`/`minor_cn`; mutation-before-CN candidates use mutated copy counts `1..major_cn`, and a mutation-after-CN one-copy candidate is added when `total_cn != 2`. | [`derive_genotype_candidates`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:131). | `current` |
| The loader derives the candidate support after validating ASCAT CN and purity; the canonical table does not provide a multiplicity column. | [`load_canonical_table`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:329). | `current` |
| For fixed `phi`, the site likelihood is a prior-weighted log-sum-exp over CN/timing candidates, each using copy-weighted expected ALT probability `xi`. | [`site_log_likelihood`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:255). | `current` |
| The conditional multiplicity posterior is calculated from the same candidate components. | [`site_multiplicity_posterior`](/bip8_disk/boyu114/main_work/inference/src/model.cpp:235). | `current` |
| The tree-level site score sums over clone possibilities using `log(eta[node]) + site_log_likelihood(phi[node])`; clone assignment is therefore integrated during scoring. | [`site_mixture_log_likelihood`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:180). | `current` |
| `phi` is derived from topology and descendant sums of `eta`; it is not an independent sampled multiplicity-like state. | [`visit_phi` and `cumulative_phi`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:69). | `current` |
| The persistent candidate-tree state contains topology and `eta`; initialization and later proposals update these quantities. | Initialization at [`algorithm.cpp`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:904) and rejuvenation at [`algorithm.cpp`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:925). | `current` |
| A per-SNV multiplicity posterior artifact is emitted with rows keyed by mutation and candidate multiplicity, not by clone and multiplicity. | [`multiplicity_posterior_tsv`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:828). The contract checks the four-column layout in [`contract_test.py`](/bip8_disk/boyu114/main_work/inference/tests/contract_test.py:276). | `current` |
| Final clone assignment is a MAP summary calculated after candidate-tree inference; it is not a persistent joint assignment state. | [`rb_map_assignments`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:501) and final aggregation at [`algorithm.cpp`](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:1068). | `current` |
| Diagnostics label topology/`eta` as state variables and assignment/multiplicity as Rao–Blackwellized variables. | [`diagnostics` metadata](/bip8_disk/boyu114/main_work/inference/src/algorithm.cpp:1158). | `current` |

The active runtime can therefore be summarized as:

$$
\begin{aligned}
\phi_v(T,\eta)
  &= \eta_v + \sum_{w\in\operatorname{descendants}_T(v)}\eta_w,\\
L_i(\phi_v)
  &= \sum_{m\in M_i}\pi_i(m\mid C_i)
     \operatorname{Binomial}\!\left(A_i\mid N_i,q_i(\phi_v,m)\right),\\
L_i(T,\eta)
  &= \sum_v \eta_v L_i(\phi_v).
\end{aligned}
$$

This equation is an `inferred` abstraction of the two source functions; the
exact numerical implementation is the linked C++ source. It means the current
runtime **does model multiplicity**, but as a loader-derived, per-site
candidate set marginalized in the emission—not as a value carried alongside
each candidate tree.

One additional boundary matters: the target/spec model describes a richer
genotype candidate set with CN timing, allele-specific states, and `m`, and
explicitly warns that it is not yet the active runtime. See [`model.md`](/bip8_disk/boyu114/main_work/model.md:187) and [`model.md`](/bip8_disk/boyu114/main_work/model.md:221). A review must not cite the target/spec `xi` as if the current executable already implemented it.

## Primary-source method crosswalk

The labels below describe the role of multiplicity in the cited method, not
whether a paper uses the literal letter `m`. Some papers encode the same
biology as a genotype, a CNV/SSM event relationship, or a precomputed cellular
frequency.

| Method | What the primary source says | Multiplicity classification | Main advantage | Main limitation relevant here |
|---|---|---|---|---|
| **PhyClone** (Hurtado, Bouchard-Côté, Roth, 2025) | Builds a tree-structured clustering model with clonal prevalence `rho`, descendant-summed cellular prevalence `bar-rho`, and a PyClone copy-number/tumor-content corrected emission; integrates `rho` during tree inference. | **Tree layer: no standalone `m`; emission: inherited genotype-aware PyClone likelihood can marginalize multiplicity/genotype.** | Lower-dimensional tree inference and explicit posterior uncertainty over trees; prevalence can be reinstantiated after tree inference. | A user reading only the tree equation may miss genotype/multiplicity uncertainty; the main paper does not define this repository's per-SNV `multiplicity_posterior.tsv.gz` output. [Primary paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563) |
| **PyClone** (Roth et al., 2014) | Uses genotype states `psi=(g_N,g_R,g_V)`, defines total copies `c(g)` and variant copies `b(g)`, and sums over genotype states in the allele-count likelihood. | **Explicit hidden genotype; multiplicity is encoded in `b(g)` and marginalized in the likelihood.** | Separates cellular prevalence from genotype uncertainty and can use allele-specific CN priors; avoids forcing every mutation to be diploid heterozygous. | Results depend on genotype-prior quality; the authors note uncertainty and model difficulty when populations do not share one genotype. It is a flat mutation-clustering model, not a tree inference method. [Primary article](https://www.nature.com/articles/nmeth.2883), [primary supplementary note](https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf) |
| **PhyloSub** (Jiao et al., 2014) | Associates each SNV with a latent lineage and a genotype/zygosity/CN variable; the methods section sums over possible genotype `g` when obtaining the posterior of the SNV population frequency. | **Genotype-aware and likelihood-marginalized; no separate public `m` output.** | Retains tree uncertainty and propagates genotype uncertainty into frequency inference. | The original framing commonly uses heterozygous normal-CN SNVs; more complex CN states increase uncertainty and computation. [Primary paper](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-15-35) |
| **PhyloWGS** (Deshwar et al., 2015) | Integrates SSMs and CNVs. For an SSM overlapping a CNV, the expected allele frequency depends on whether the SSM precedes/follows the CNV or is on another branch, and on the maternal/paternal copy counts; the method considers phasing possibilities in the likelihood. | **Event/genotype state rather than a single `m` symbol; multiplicity is represented through CNV–SSM timing and mutated-copy counts.** | Can explain amplified or deleted loci whose VAF cannot be interpreted from CCF alone; jointly uses CNV and SSM phylogenetic relationships. | Requires CNV preprocessing and, for amplification cases, allele-specific copy decomposition; event relationships create a larger, harder inference problem. [Primary paper](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8) |
| **Canopy** (Jiang et al., 2016) | Infers a phylogeny using SNAs and CNAs and derives a general VAF/MCF relationship for different SNA–CNA evolutionary cases; its model includes uncertainty about whether an SNA lies on the major or minor allele after a CN event. | **CNA/event-aware; not presented as a standalone per-SNV `m` state or repository-style multiplicity output.** | Uses CNAs and SNAs jointly, allowing VAF changes caused by amplification or loss to inform the evolutionary history. | Event-aware formulas and multi-sample parameters are more complex; the method requires CNA input and its public output is not a per-SNV multiplicity posterior. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC5027458/), [primary DOI](https://doi.org/10.1073/pnas.1605069113) |
| **Pairtree** (Wintersinger et al., 2022) | Converts VAF/read-count data to CNA-corrected subclonal frequencies, then searches clone trees whose descendant-summed frequencies fit those estimates; the main model describes tree uncertainty and does not expose a multiplicity latent variable. | **Pre-corrected frequency approach at the main tree layer; explicit multiplicity is not established in the main paper.** | Scales to larger numbers of subclones and samples and reports multiple plausible trees with posterior-like weights. | Any multiplicity/CNA mistake made during the VAF-to-frequency preprocessing can propagate into the tree; the tree search itself cannot recover information discarded before tree inference. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/) |
| **CITUP** (Malikic et al., 2015) | Takes mutation-frequency estimates, assigns mutations to nodes, solves for clone proportions under descendant-sum constraints, and selects solutions using a BIC objective; the paper's basic frequency definition is diploid-heterozygous oriented and the method is limited in its handling of CN changes. | **No explicit multiplicity latent variable in the tree objective; relies on supplied/corrected mutation frequencies and assumptions.** | Fast/tractable optimization for its supported problem and gives an explicit tree-plus-assignment solution. | Hard frequency preprocessing assumptions make amplification/LOH situations difficult; BIC/optimization does not provide the same genotype/multiplicity posterior as an emission-marginalized Bayesian model. [Primary paper](https://academic.oup.com/bioinformatics/article/31/9/1349/200674) |
| **DeCiFer** (Satas et al., 2021) | Defines genotype `(x,y,m)`, challenges constant mutation multiplicity, introduces DCF for mutation loss, and jointly estimates multiplicity-related states and clusters using an evolutionary model. | **Explicit multiplicity-aware inference; supports multiplicity differences across evolutionary contexts rather than one fixed `m` for every SNV.** | Can avoid explaining systematic VAF patterns by implausible repeated mutations and can represent mutation loss with DCF. | More realistic state space and event assumptions increase computational and modeling complexity; DCF is not identical to the repository's CCF/`phi` definition. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/), [primary DOI](https://doi.org/10.1016/j.cels.2021.07.006) |

### A crucial distinction: explicit `m` versus genotype-aware inference

The literature does not use a single naming convention. These are not
equivalent implementation choices:

- `m_i` as one site-level integer for every cancer cell carrying SNV `i`.
- `m_{i,v}` as a clone/lineage-specific mutated-copy count.
- `g_{i,v}=(x,y,m)` as a richer genotype state that also records total and
  allele-specific CN.
- An event state saying whether the SNV preceded or followed a CNV, from which
  the mutated-copy count is implied.
- A precomputed CCF/subclonal-frequency value in which multiplicity has already
  been selected or averaged before tree inference.

The first option is not sufficient when subclonal CN changes can make the same
SNV have different copy states in different descendants. PhyloWGS and DeCiFer
are the clearest primary-source warnings against collapsing every such case to
one site-level number.[PhyloWGS CNV/SSM relationship model](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8), [DeCiFer genotype model](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)

## Three repository design options

### Option A — carry multiplicity/genotype in the candidate-tree state

A literal version would extend each candidate state with something like
`m_i`, but a biologically richer version would need `g_{i,v}` or event-linked
states when copy number differs across clones:

$$
p(T,\eta,G\mid D)
\propto
p(T)\,p(\eta\mid T)\,p(G\mid C,T)
\prod_i P(D_i\mid T,\eta,G).
$$

Here `G` is deliberately written as a genotype/event collection rather than
assuming that one scalar `m_i` is always enough.

Potential benefits:

- Produces a joint posterior sample in which tree, clone prevalence, CN/event
  relationship, and multiplicity can be queried together.
- Allows multiplicity to affect tree proposals directly rather than only through
  a pre-averaged emission.
- Can support clone-specific multiplicity and mutation-loss logic if the state
  is defined at the correct lineage level.

Costs and risks:

- Increases state dimension by roughly the number of SNVs, or by the number of
  SNV-by-lineage genotype relationships in the richer version.
- Needs valid proposals, priors, and acceptance calculations for discrete
  genotype/event moves; poor mixing can be worse than uncertainty from a
  marginalized model.
- A naive single `m_i` state can be less correct than the current marginalization
  if descendants have different CN histories.
- Output becomes harder to summarize because tree uncertainty and genotype
  uncertainty are coupled; label alignment across candidate trees is required.

### Option B — marginalize multiplicity only inside the likelihood

This is the current runtime pattern:

$$
L_i(\phi)
=
\sum_{m\in M_i}
\pi_i(m\mid C_i)
P(D_i\mid \phi,m,C_i).
$$

Potential benefits:

- Keeps the topology/`eta` state small while retaining multiplicity uncertainty
  in the evidence used to score each candidate tree.
- Avoids prematurely choosing a single multiplicity from a noisy VAF.
- Naturally supports a posterior responsibility for each candidate multiplicity,
  as the current runtime does.
- Is compatible with the core idea in PyClone and PhyloSub that genotype
  uncertainty can be integrated in the allele-count likelihood.[PyClone](https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf), [PhyloSub](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-15-35)

Costs and risks:

- The tree sampler does not carry a joint per-draw multiplicity assignment, so
  a downstream question such as “which multiplicity co-occurs with this exact
  topology and clone assignment?” requires conditional responsibility
  reconstruction.
- A weak or overly uniform candidate prior can spread likelihood mass across
  implausible states; a strong prior can hide genuine CN-timing uncertainty.
- If the candidate set is only site-level and static, it may not represent
  clone-specific CN changes or mutation loss.
- Marginalization can make debugging less transparent because a good tree score
  may be supported by several biologically different genotype explanations.

### Option C — do not model multiplicity

The simplest version fixes one mutated copy, usually corresponding to a
diploid-heterozygous assumption. In the current repository's denominator this
would amount to evaluating the emission with `m=1` only:

$$
L_i(\phi)
=
P\!\left(D_i\mid q_i(\phi,m=1),C_i\right).
$$

An even more aggressive version does not use local CN in the VAF correction and
uses a diploid proxy such as `VAF ≈ purity * CCF / 2`. These are different
assumptions and should not be conflated.

Potential benefits:

- Lowest computational and implementation complexity.
- Easier to explain and easier to compare with methods whose inputs are already
  CCF or diploid-normalized mutation frequencies.
- Fewer latent states and fewer prior choices can make small-data behavior more
  stable when CN information is unreliable.

Costs and risks:

- Amplification can increase VAF without increasing the fraction of cells that
  carry the mutation; a fixed `m=1` model can therefore overestimate CCF.
- Loss of one allele, LOH, and other CN states can change VAF without the same
  change in cellular prevalence; the tree can then place a mutation in the
  wrong clone or prefer the wrong topology.
- It discards uncertainty that the read counts and CN context cannot resolve.
- DeCiFer reports that constant-multiplicity assumptions can create implausible
  evolutionary explanations, while PhyloWGS shows that CNV/SSM relationships can
  change the expected VAF.[DeCiFer](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/), [PhyloWGS](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8)

## Difference in observable behavior

| Situation | Carry `m`/genotype in state | Marginalize `m` in likelihood | Do not model `m` |
|---|---|---|---|
| Diploid, heterozygous, no CN event | Usually agrees with the other two if the state prior favors `m=1`. | Usually adequate and smooth. | Often adequate under the assumption. |
| Amplification of a mutated allele | Can associate the amplified copy count with the relevant lineage/event if the state is rich enough. | Can retain several copy-count explanations and propagate them into tree scores. | Tends to interpret extra VAF as extra cellular prevalence. |
| LOH or deletion affecting the locus | Can represent timing and loss explicitly, but needs a larger event model. | Can represent it only if the candidate set includes the relevant genotype/event states. | Can bias CCF and tree placement. |
| Low depth / weak CN evidence | May jump between poorly identified discrete states and mix slowly. | Usually reflects uncertainty more gracefully, but depends strongly on candidate priors. | May be numerically stable but scientifically overconfident. |
| Need a per-SNV multiplicity result | Natural if the state is retained and summarized. | Possible as a posterior responsibility, but not a joint state unless reconstructed conditionally. | Impossible by design. |
| Need a scalable tree search | More expensive as state dimension grows. | Keeps tree search smaller. | Cheapest. |
| Need mutation-loss or clone-specific CN timing | Possible only with an appropriately rich state, not one scalar `m_i`. | Possible only if the marginalized candidates encode those histories. | Not represented. |

The main trade-off is therefore not simply “more realism versus less realism.”
It is:

> **joint interpretability and event coupling** versus **state dimension and
> mixing**, with **marginalization** as a middle path whose validity depends on
> whether the candidate set is rich enough.

## Inferences for this repository, kept separate from literature facts

The following are `inferred` implications of the current code and the cited
models, not claims that a paper requires a particular repository choice.

1. The current repository already pays the main scientific cost of including
   multiplicity in the emission: `m` changes `q`, and the candidate prior changes
   the integrated likelihood. Replacing it with `m=1` would be a real model
   change, not merely an output-format change.

2. The current repository's multiplicity posterior is averaged across retained
   candidate-tree draws and does not include a clone column. That is suitable
   for “what multiplicities remain plausible for this SNV overall,” but not for
   “what multiplicity was used in this exact clone/topology explanation.” The
   latter requires clone-conditioned responsibilities or an explicit joint
   state.

3. The current candidate support is generated from static major/minor CN. It
   should not be described as a full PhyloWGS/DeCiFer-style CN-timing model. The
   target/spec document itself distinguishes richer `G_i` candidates from the
   current runtime.[`model.md`](/bip8_disk/boyu114/main_work/model.md:187)

4. If the scientific goal is only tree topology and CCF/`phi`, marginalizing
   multiplicity may be enough. If the goal includes timing of CN events,
   allele-specific evolutionary history, or mutation-loss interpretation, the
   unresolved choice is not merely whether to store `m`; it is whether to model
   a lineage-specific genotype/event state.

5. If the project claims that CCF is the fraction of cancer cells carrying the
   SNV, a multiplicity-aware emission is especially important in CN-altered
   regions. If the project instead restricts all eligible SNVs to diploid,
   heterozygous loci, the no-multiplicity option becomes a narrower but explicit
   scientific scope rather than a general model.

## Decisions recorded from the design interview

The following decisions were confirmed on 2026-08-28:

1. **Multiplicity role — B:** keep multiplicity out of the persistent
   candidate-tree state and marginalize it inside the allele-count likelihood.
2. **CNV timing — B:** the target model must be able to represent whether an
   SNV occurred before or after a CNV. This requires genotype/event candidates
   inside the marginalized emission; a single static scalar `m_i` is not enough
   for every possible lineage-specific history.
3. **Multiplicity output — A:** report one global per-SNV multiplicity
   posterior. It must be labeled as aggregated across candidate trees and
   clone responsibilities, not as a multiplicity jointly attached to one
   specific topology and clone assignment.
4. **Mutation loss — C:** preserve the existing CCF/`phi` meaning, but allow
   suspected mutation-loss loci to be flagged as outliers rather than forcing
   them to satisfy the descendant-sum constraint. This does not yet define a
   DCF replacement or the exact outlier eligibility rule.

Q4 (the formal VAF emission target) was confirmed as Candidate B on 2026-08-28.
The integrated PhyClone-compatible `xi` emission is now synchronized in the C++
and Python runtime and protected by deterministic tests. The current `q_repo`
is retained as a historical baseline; PyClone-VI pre-clustering remains an
optional workflow and is not part of the active scorer. The full predictive and
posterior validation gates remain open.

## Open design decisions

No choice is made here. These are the decisions that must be settled before a
model or contract change:

1. **Scope of CN heterogeneity:** Is `major_cn/minor_cn` a static locus summary
   shared by every clone, or can CN differ by lineage?
2. **State granularity:** The confirmed emission-level design needs a genotype/
   event candidate when representing clone-specific CN and mutation timing; the
   remaining question is the exact candidate set and prior.
4. **Mutation-loss outlier rule:** Which CNV evidence and posterior threshold
   are sufficient to flag a locus as a possible mutation-loss outlier? A future
   DCF-like extension remains a separate scope decision.[DeCiFer](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/)
5. **Prior ownership:** Should multiplicity priors be uniform over CN-derived
   candidates, informed by allele-specific CN and timing, or learned from an
   external caller? PyClone documents that genotype-prior quality can materially
   affect prevalence and clustering.[PyClone supplementary note](https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf)
6. **Validation target:** Will evaluation score tree topology only, or also VAF
   reconstruction, CCF/DCF accuracy, multiplicity calibration, and the rate of
   implausible homoplasy explanations?
7. **Runtime/spec synchronization:** Which parts of the richer clone-specific
   `G_i`/`xi` target should be added next beyond the already synchronized minimal
   emission in [`model.md`](/bip8_disk/boyu114/main_work/model.md:154)?
   contract?

## Evidence boundaries and gaps

### Evidence layers searched

- Lab knowledge base: `/big8_disk/liaoyoyo2001/Knowledge` was available and was
  searched first for `multiplicity`, `CCF`, `VAF`, copy number, and tumor-tree
  method terms. It contains useful VAF/CN interpretation notes but no focused
  lab-canonical primary-source note that settles the three design options; this
  is a `not-found` result, not evidence that the literature is empty.
- Current repository: `/bip8_disk/boyu114/main_work` was available. Recent
  `daily/` HTML was used only for orientation; current claims above were checked
  against C++ source, headers, tests, and `model.md` target/spec boundaries.
- Historical project knowledge base: `/bip8_disk/boyu114/bip8_disk_boyu_database` was
  available, but no historical claim was needed to answer the multiplicity
  comparison, so it was not used as authority for current behavior.

### Delegation status

The main investigation used four parallel read-only subagents covering the lab
knowledge base, current repository, primary literature, and research-note
synthesis. The coordinator independently rechecked the repository claims and
integrated the evidence. The note writer itself did not dispatch additional
subagents.

### Interpretation cautions

- “No explicit `m` found in a paper” means the paper's main model/output
  description does not expose that variable. It does not prove that an
  implementation never uses an equivalent genotype or CN-event state.
- The literal symbol `m` is not a field-name standard across tumor-evolution
  methods. `b(g)`, mutated-copy count, allele-specific genotype, and CNV/SSM
  timing can encode the same or a richer latent quantity.
- Primary papers often separate tree inference from the allele-count emission.
  The tree equation alone is insufficient to classify the emission's treatment
  of multiplicity.
- The active repository's C++ baseline and the richer `model.md` target/spec are
  not interchangeable evidence. The former establishes current behavior; the
  latter records an intended or exploratory model boundary.

## Primary-source index

| Method/source | Primary URL |
|---|---|
| PhyClone | https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563 |
| PyClone article | https://www.nature.com/articles/nmeth.2883 |
| PyClone supplementary model | https://www.stat.ubc.ca/~bouchard/pub/sup-Roth2014PyClone.pdf |
| PhyloSub | https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-15-35 |
| PhyloWGS | https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0602-8 |
| Canopy | https://pmc.ncbi.nlm.nih.gov/articles/PMC5027458/ |
| Pairtree | https://pmc.ncbi.nlm.nih.gov/articles/PMC9780082/ |
| CITUP | https://academic.oup.com/bioinformatics/article/31/9/1349/200674 |
| DeCiFer | https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/ |
