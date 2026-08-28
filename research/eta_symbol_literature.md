# `η` in tumor-evolution tree models

## Concise conclusion

先前把 `η` 說成「repo-specific」不夠精確，應更正如下：

> `η` 作為樹節點的 **exclusive/local population mass**，在 PhyloSub 與 PhyloWGS 的原始模型中已有明確先例；Pairtree 的官方程式／輸出也使用 `eta` 表示 exclusive population frequencies。可是 `η` 不是 tumor-tree literature 的 universal symbol。不同模型使用不同符號，因此本 repo 應把 `η` 標成「採用 PhyloWGS/PhyloSub 相容語意的 project notation」，而不是宣稱所有論文都如此命名。

本 repo 的對應關係是：

$$
\eta_v = \text{只在節點 }v\text{ 起源的 tumor-cell mass},
\qquad
\phi_v = \eta_v + \sum_{w\in\operatorname{Desc}(v)}\eta_w.
$$

這個語意與 PhyloWGS 的公式相同；但本 repo 的有限 `K`、Dirichlet mass prior、proposal 與 likelihood 仍是本 repo 的模型實作，不等於完整 PhyloWGS 或 PhyloSub。

## Primary-source crosswalk

| Model | Exclusive/local quantity | Cumulative prevalence / CCF-like quantity | Assignment or mixture notation | What `η` means there |
|---|---|---|---|---|
| Original TSSB | Node mixture mass is $\pi_\epsilon$ | No tumor-specific CCF notion | Data choose a node/path $\epsilon_n$; $\nu_\epsilon$ is the stop-at-node break and $\psi_\epsilon$ controls child branching | Not the node mass. In the optional parameter-transition example, $\eta$ is a parent-to-child shrinkage coefficient. |
| PhyloSub | $\eta_v$ auxiliary node weights with $\sum_v\eta_v=1$ | $\phi_v$ / $\varphi_v$ SNV population frequency, obtained by summing the node and descendants | TSSB node/path assignment; the paper also uses $\tilde\eta_i^t$ for an SSM/sample auxiliary weight | Explicitly the auxiliary/exclusive mass parameterization. |
| PhyloWGS | $\eta_v$; its CNV equations multiply copy counts by $\eta_u$ | $\phi_v$ SSM population frequency, $\phi_v=\eta_v+\sum_{w\in D(v)}\eta_w$ | $\tilde\eta_i\sim\mathcal G$ is the TSSB draw for datum `i`; $\mathcal G\sim\mathrm{TSSB}(\alpha,\gamma,H)$ | Explicitly the local/exclusive mass construction used to enforce tree-compatible frequencies. |
| PhyloClone | $\rho_v$ = **clonal prevalence**, the malignant cells originating at node `v` | $\bar\rho_v$ = **cellular prevalence**, $\bar\rho_v=\sum_{v'\in V_v}\rho_{v'}$ | $v_n$ is the tree node assigned to mutation cluster `b` containing mutation `n` | Not local mass in the model. In the official code, an `eta` variable is used as a Beta auxiliary draw in the concentration-parameter sampler. |
| Pairtree | Official output/source names this $\eta$ “population frequencies” of subpopulations | Official output/source names this $\phi$ “tree-constrained subclonal frequencies”, the sum over a subclone and descendants | Mutation clusters are attached to subclones; tree MCMC scores candidate trees and their fitted frequencies | A compatible naming convention, but not evidence of a universal standard. |

## Evidence from the primary sources

### PhyloSub and PhyloWGS

The PhyloSub paper describes a node's population as the cells with the lineage genotype **and no input mutations from descendants**; an SNV's population frequency is then the sum over the lineage where it appeared and its descendants. In its constrained parameterization, it introduces auxiliary weights $\eta_v$ and derives $\phi_v$ by descendant summation. See [Jiao et al., PhyloSub (2014), original paper](https://doi.org/10.1186/1471-2105-15-35).

PhyloWGS states the notation explicitly: $\eta_v$ are node-level auxiliary variables summing to one, while $\phi_v$ is the SSM population frequency obtained from the node and all descendants. It separately uses $\tilde\eta_i$ for the TSSB latent variable associated with SSM `i`. See [Deshwar et al., PhyloWGS, Methods](https://doi.org/10.1186/s13059-015-0602-8), especially the PhyloSub-model and TSSB sections. The [official PhyloWGS `tssb.py`](https://github.com/morrislab/phylowgs/blob/master/tssb.py) implements the same idea with code names `main`, `sticks`, and `get_mixture()` rather than a field literally named `eta`.

Therefore, `eta = local mass` is a genuine PhyloSub/PhyloWGS convention, not merely a symbol invented in this repository.

### Original TSSB

The original TSSB paper uses $\pi_\epsilon$ for the probability mass of a node's partition. It constructs this from $\nu_\epsilon$ stop/pass breaks and $\psi_\epsilon$ child-branching breaks; assignments are represented by tree paths. It does not define $\eta$ as a node mass. Its separate Gaussian-diffusion example uses $\eta$ as a parent-to-child coefficient. See [Adams, Ghahramani & Jordan, original TSSB paper (NeurIPS 2010)](https://papers.neurips.cc/paper_files/paper/2010/file/a5e00132373a7031000fd987a3c9f87b-Paper.pdf), Eq. (2) and the hierarchical-prior section.

This is the clearest reason not to call `η` universal: even the prior process on which PhyloSub/PhyloWGS are based uses a different mass symbol.

### PhyClone

PhyloClone deliberately uses a different pair of symbols. Its paper defines $\rho_v$ as clonal prevalence (malignant cells originating at node `v`) and $\bar\rho_v$ as cellular prevalence (the node plus descendants), then uses $v_n$ for the node associated with mutation cluster `n`. See [Hurtado et al., PhyClone (Bioinformatics)](https://doi.org/10.1093/bioinformatics/btaf344), Methods §2.1–2.2, and the [official PhyClone source](https://github.com/Roth-Lab/PhyClone/tree/27383246c1aff7b1d62c02662017bd61bfdfbc33).

The official source's [concentration sampler](https://github.com/Roth-Lab/PhyClone/blob/27383246c1aff7b1d62c02662017bd61bfdfbc33/phyclone/mcmc/concentration.py#L31-L60) uses a scalar `eta` for the Beta auxiliary variable in a Gamma-prior concentration update. The source's [FS-CRP test utility](https://github.com/Roth-Lab/PhyClone/blob/27383246c1aff7b1d62c02662017bd61bfdfbc33/phyclone/tests/utilities/fscrp.py#L7-L23) calls the two prevalence quantities `clonal_prev` and `cellular_prev`, not `eta` and `phi`.

### Pairtree

Pairtree's original paper defines an exclusive **population frequency** for each subpopulation and a cumulative **tree-constrained subclonal frequency** for each subclone, equal to the sum over that subclone's subpopulations and descendants. Its official output contract names the corresponding matrices `eta` and `phi`, respectively. See [Wintersinger et al., Pairtree (Blood Cancer Discovery)](https://doi.org/10.1158/2643-3230.BCD-21-0092) and the [official Pairtree README/output source](https://github.com/morrislab/pairtree#pairtree-outputs).

Pairtree is useful corroboration for the symbol pairing, but it does not make the pairing universal: the paper's conceptual terms are population frequency and subclonal frequency, while other models use cellular prevalence, clonal prevalence, or other symbols.

## Implication for this repository

The current backend's [`Particle::eta`](../inference/src/algorithm.cpp#L32-L35) is a positive simplex, and [`cumulative_phi`](../inference/src/algorithm.cpp#L69-L92) recursively sums descendants. That is scientifically defensible as a **PhyloWGS/PhyloSub-compatible notation choice**.

The documentation should use this wording:

> In this repository, $\eta_v$ denotes clone-specific local fraction by convention. This follows the $\eta_v\to\phi_v$ construction used explicitly by PhyloSub/PhyloWGS, but $\eta$ is not a universal tumor-tree symbol; PhyClone uses $\rho_v$ and $\bar\rho_v$, while original TSSB uses $\pi,\nu,\psi$.

Do not write “the literature defines `η` as local mass” without naming PhyloSub/PhyloWGS, and do not equate this notation with PhyClone's $\rho$ unless the symbol translation is stated.
