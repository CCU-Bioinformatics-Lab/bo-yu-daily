# PhyloWGS model review

> Scope: original PhyloWGS paper and the official `morrislab/phylowgs` repository only. This is a model and sampler review for the current ASCAT + long-read/HP-count tumor-tree project. No code change is proposed in this file.

## Primary sources

- Deshwar et al., *PhyloWGS: Reconstructing subclonal composition and evolution from whole-genome sequencing of tumors* ([Genome Biology / DOI](https://link.springer.com/article/10.1186/s13059-015-0602-8), [author manuscript](https://arxiv.org/abs/1406.7250)).
- Official implementation: [`morrislab/phylowgs`](https://github.com/morrislab/phylowgs).
- Official input specification: [`README.md`](https://github.com/morrislab/phylowgs/blob/master/README.md) and [CNV parser README](https://github.com/morrislab/phylowgs/blob/master/parser/README.md).
- Official sampler code: [`evolve.py`](https://github.com/morrislab/phylowgs/blob/master/evolve.py), [`tssb.py`](https://github.com/morrislab/phylowgs/blob/master/tssb.py), and [`mh.cpp`](https://github.com/morrislab/phylowgs/blob/master/mh.cpp).

## 1. Generative model

### SSM observation and population frequency

For SSM \(i\), the original input is:

- \(a_i\): reference-allele reads;
- \(b_i\): variant-allele reads;
- \(d_i=a_i+b_i\): total reads;
- \(\mu_i^r\): probability of observing the reference allele in the reference population;
- \(\mu_i^v\): probability of observing the reference allele in the variant population;
- \(\tilde{\phi}_i\): fraction of cells carrying that SSM, called SSM population frequency in the paper.

The observation model is

\[
a_i \mid d_i,\tilde{\phi}_i,\mu_i^r,\mu_i^v
\sim \operatorname{Binomial}\left(d_i,
(1-\tilde{\phi}_i)\mu_i^r+\tilde{\phi}_i\mu_i^v\right).
\]

In a diploid, CNV-free locus, the paper uses approximately \(\mu_i^v=0.5\), so a heterozygous SSM has expected VAF near \(\tilde{\phi}_i/2\), after sequencing-error adjustment. The model clusters mutations with equal \(\tilde{\phi}\) while inferring the tree at the same time; it does not first require a fixed number of VAF clusters.

### Tree prior and clonal-frequency constraint

PhyloWGS uses a tree-structured stick-breaking process (TSSB), written as

\[
\mathcal{G}\sim\operatorname{TSSB}(\alpha,\gamma,H),
\qquad \tilde{\eta}_i\sim\mathcal{G}.
\]

The paper describes \(\alpha\) as controlling tree height and \(\gamma\) as controlling tree width. The base distribution uses `Uniform(0, 1)` for the root frequency and, for a child \(v\),

\[
H_v=\operatorname{Uniform}\left(0,
\phi_{\operatorname{par}(v)}-
\sum_{w\in\mathcal{S}(v)}\phi_w\right),
\]

which keeps the parent frequency large enough to contain its children.

The implementation uses auxiliary node masses \(\eta_v\) rather than proposing constrained \(\phi_v\) directly:

\[
\phi_v=\eta_v+\sum_{w\in\mathcal{D}(v)}\eta_w
      =\eta_v+\sum_{w\in\mathcal{C}(v)}\phi_w.
\]

Therefore \(\phi_v\geq\sum_{w\in\mathcal{C}(v)}\phi_w\) by construction. This reparameterization is central: the sampler moves masses on a simplex and derives valid clonal frequencies from the tree.

### CNV integration

PhyloWGS does not infer raw CNV segment states from read depth itself. It expects CNV preprocessing to provide the CNV population frequency \(\tilde{\phi}_j\), total copy number \(C_j\), and, when needed, maternal/paternal copy numbers \(C_j^m,C_j^p\).

1. **CNV without an overlapping SSM:** it creates a pseudo-SSM with approximately
   \[
   b_j/(a_j+b_j)\approx \tilde{\phi}_j/2,
   \]
   and chooses pseudo-depth to represent the uncertainty/evidence of the CNV.
2. **CNV overlapping an SSM:** for each clone population \(u\), the model accumulates reference and variant copy mass \(N_i^r,N_i^v\), then uses
   \[
   \zeta_i=\frac{N_i^r(1-\epsilon)+N_i^v\epsilon}{N_i^r+N_i^v},
   \qquad
   a_i\sim\operatorname{Binomial}(d_i,\zeta_i).
   \]
3. The \(N_i^r,N_i^v\) update depends on whether the population contains the SSM, whether it is affected by the CNV, and whether the SSM occurred before or after the CNV. If the SSM precedes an amplification, the two maternal/paternal placements are evaluated using \(C_i^m,C_i^p\); if phase is unavailable, the paper averages the two likelihoods.

The key PhyloWGS idea is that the SSM–CNV evolutionary relationship determines the VAF correction. CNV and SSM are not independently clustered and joined afterward.

## 2. Actual MCMC state and update schedule

The effective state contains:

- a rooted TSSB tree and its parent/child links;
- assignment of every SSM or pseudo-SSM/CNV datum to a node;
- node-local masses and stick-breaking weights;
- derived \(\phi_v\) values / cumulative child masses;
- TSSB hyperparameters (`dp_alpha`, `dp_gamma`, `alpha_decay`);
- the observed SSM/CNV data and their error/CNV-placement metadata.

The official `evolve.py` loop is, in order:

1. `tssb.resample_assignments()`;
2. `tssb.cull_tree()`;
3. the C++ `metropolis(...)` step for continuous node masses;
4. `tssb.resample_sticks()`;
5. `tssb.resample_stick_orders()`;
6. slice-sample TSSB hyperparameters;
7. record the complete-data log likelihood and tree sample.

The C++ `mh.cpp` step is not a topology move. For each sample/time point it proposes node-local masses with a Dirichlet proposal whose concentration is approximately

\[
\alpha_i^{\text{proposal}}=\text{MH\_STD}\,\pi_i+1.
\]

The acceptance log-ratio combines the old/new data posterior and the forward/reverse Dirichlet proposal-density correction. On acceptance it updates `pi` and the cumulative `param` values. The paper reports 5,000 inner MH iterations and a Dirichlet proposal scale of 100 for its experiments; the repository README exposes these as configurable settings.

## 3. How topology is explored — and what it does **not** do

The important finding for the current failure is:

> PhyloWGS does not use a single-parent topology MH proposal such as “pick one existing clone and randomly change its parent.” It also does not expose an explicit NNI, SPR, or split–merge topology kernel in the official sampler code.

Topology changes arise indirectly from the TSSB assignment sampler:

- `resample_assignments()` processes each datum and uses a slice-sampling procedure to propose a new TSSB location. A datum can move to another existing node or to a newly spawned child path.
- `find_node()` extends the stick representation and spawns a child when the sampled slice reaches an unrepresented stick interval.
- `cull_tree()` removes empty trailing child nodes after reassignment.
- `resample_stick_orders()` redraws the sibling order, can allocate an additional child, removes unrepresented children, and then resamples sticks.
- `resample_sticks()` updates the Beta stick variables from child-data counts.

Thus, the tree is a nonparametric allocation structure whose occupied nodes and sibling ordering change as assignments and sticks are resampled. This avoids the specific problem in the current C++ implementation: a parent rewrite can alter the prevalence contribution of an entire clone across roughly 30,000 SNVs in one low-probability proposal. In PhyloWGS, the topology-changing part is separated from the continuous mass MH step, and the assignment proposal is restricted by a slice level rather than proposing an arbitrary parent for a whole clone.

This is an implementation-based inference, not a claim that PhyloWGS always mixes well. Its assignment update is still datum-wise, so strongly correlated mutations may require many iterations to move together. The official code should therefore not be described as a guaranteed solution to topology mixing or as a split–merge sampler.

## 4. What can be ported to this repository

### Reasonable reusable ideas

1. Keep the current ASCAT/HP-count likelihood, but reparameterize clone prevalence with nonnegative node masses \(\eta\) and derive parent prevalence by descendant sums.
2. Replace the current whole-clone parent-rewire proposal with a TSSB-inspired allocation kernel: move one SNV/CNV-observation assignment through existing clone nodes, allow birth of an occupied child, remove empty nodes, and resample sibling order/sticks.
3. Keep the continuous prevalence update as a separate Dirichlet random-walk MH block, with forward/reverse proposal correction and explicit acceptance diagnostics.
4. Run multiple independently seeded chains. The official repository recommends four concurrent chains because multiple chains improve posterior approximation; they do not reduce the runtime of one chain.

### Non-portable assumptions and required adaptations

| PhyloWGS assumption | Why it cannot be copied directly into the current model |
|---|---|
| Input is SSM `a,d,mu_r,mu_v` plus CNV `a,d,ssms` | The current model has REF/ALT counts, ASCAT total/major/minor CN, multiplicity posterior, ASCAT purity, and HP1/HP2 counts. HP counts cannot be reduced to `mu_r`/`mu_v` without losing the long-read observation model. |
| \(\tilde{\phi}\) is a per-event population frequency | It is not the same object as global `rho_ASCAT=0.99`. The official parser describes CNV cellular prevalence as the fraction of all sample cells carrying the event, not simply the fraction of tumor cells. Purity must remain a separate mixture parameter or be explicitly converted to an all-cell prevalence convention. |
| CNV events have prevalence and sometimes \(C^m,C^p\) | ASCAT segment CN alone does not provide CNV-event prevalence or the evolutionary timing of an SSM relative to a CNV. A direct port needs a CNV-event layer, a principled multiplicity/allelic-copy mapping, or a CN-stable-region restriction. |
| Infinite-sites assumption for SSMs | It can be a useful SNV prior, but PS/HP phase blocks are chromosome-copy linkage, not automatically clone ancestry. A PS group must not be treated as one evolutionary node without a likelihood or proposal model that justifies the correlation. |
| Variable-size TSSB tree | The current experiment uses finite `K` sensitivity settings. A faithful port needs birth/death or allocation-based variable node count; a finite-\(K\) approximation must state that it is not the original TSSB prior. |
| No SSM phasing required | PhyloWGS averages maternal/paternal CNV placements when phase is unavailable. The current project specifically wants long-read HP information, so the HP likelihood should be retained as an additional observation, not discarded in favor of PhyloWGS's unphased shortcut. |

## Bottom line for the next C++ revision

The most faithful lesson is **not** “add a more aggressive parent MH move.” It is:

\[
\text{tree allocation / occupied-node changes}
\quad\perp\quad
\text{continuous clone-mass MH}.
\]

For this repository, the next design should first implement a finite-tree, TSSB-inspired assignment/birth/cull/order kernel around the existing ASCAT + multiplicity + HP-count likelihood. Only afterward should we decide whether a true variable-\(K\) TSSB prior and explicit CNV pseudo-observations are scientifically justified. This preserves the current data model while addressing the observed zero topology-acceptance failure without pretending that ASCAT purity, SNV multiplicity, and PhyloWGS population frequency are interchangeable.

