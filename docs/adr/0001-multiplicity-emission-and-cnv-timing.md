# ADR 0001: Marginalized multiplicity with CNV-timing-aware emission

- Status: Accepted; PhyClone/PyClone-VI-style xi emission synchronized in C++ and Python; full validation pending
- Date: 2026-08-28
- Scope: mutation multiplicity, genotype candidates, CNV timing, and output

## Context

The candidate tumor-tree state currently contains the tree topology `T` and
clone-specific local fractions `eta`. The cumulative CCF/`phi` is derived from
them. Mutation multiplicity is biologically relevant to the allele-count
emission, but it need not be another persistent tree coordinate.

The literature separates these layers. PhyClone uses descendant-summed
cellular prevalence at the tree layer and delegates allele-count modeling to a
copy-number-aware PyClone likelihood. PhyloSub and PyClone marginalize
genotype candidates in the emission. PhyloWGS and DeCiFer show that CNV timing,
allele-specific copy number, and mutation loss can require richer event or
genotype candidates than one static scalar multiplicity.

The current repository now uses a minimal PhyClone/PyClone-VI-style `xi`
emission with per-SNV CN/timing genotype candidates. It keeps the v4 input
contract unchanged: normal copy number is currently fixed to `2.0`, and the
sequencing-error rate is a model-side constant `0.001`. A richer
clone-specific CNV event history remains future work.

## Decision

1. Do not add a per-SNV multiplicity trajectory to the persistent candidate-
   tumor-tree state.
2. Marginalize multiplicity/genotype/event candidates inside the allele-count
   likelihood:

   $$
   L_i(\phi)
   =
   \sum_{g\in\mathcal{G}_i}
   P(g\mid C_i)\,P(D_i\mid\phi,g,C_i).
   $$

3. The target candidate set must be able to distinguish an SNV that occurred
   before a CNV from one that occurred after a CNV when the supplied data can
   support that distinction. A single site-level `m_i` remains acceptable only
   for the simpler static-CN baseline.
4. Output one global multiplicity posterior per SNV. The output is aggregated
   over retained candidate trees and clone responsibilities; it is not a
   claim about one specific topology/clone joint draw.
5. Use the integrated PhyClone/PyClone-VI-style expected ALT probability
   (repository notation `xi`) as the active VAF emission. For each candidate
   genotype `g`, use copy-number-weighted normal/reference/variant populations
   and marginalize candidate likelihoods with their priors. The current
   candidate set includes mutation-before-CN candidates with mutated copy
   counts `1..major_cn`, plus a mutation-after-CN, one-mutated-copy candidate
   when `total_cn != 2`.

## Why

- Marginalization retains copy-number uncertainty without multiplying the
  topology search space by every SNV's discrete state.
- CNV timing remains available as an emission explanation instead of being
  incorrectly represented by a single universal `m_i`.
- A global per-SNV posterior is useful for diagnostics while keeping its
  interpretation honest about the missing clone-conditioned joint state.

## Consequences

Positive consequences:

- Amplification and LOH can affect the expected VAF without forcing all of the
  effect into CCF.
- The candidate-tree search remains smaller than a fully joint topology,
  assignment, and genotype sampler.
- The model can later add clone-specific genotype/event candidates without
  changing the meaning of `T`, `eta`, or cumulative `phi`.

Costs and limitations:

- The exact genotype/event candidate set and prior must be specified and
  validated; marginalization does not solve CCF–multiplicity
  non-identifiability by itself.
- The current candidate set is a minimal timing-aware approximation; it does
  not encode a clone-specific CNV event history, allele phase, or mutation-loss
  state.
- A global multiplicity posterior cannot answer which multiplicity belongs to
  one exact topology and clone assignment without additional conditional
  responsibility output.
- Suspected mutation loss is to be flagged as an outlier while retaining the
  CCF/`phi` definition; the exact outlier rule and any future DCF-like
  extension remain unspecified.

## Not decided by this ADR

- The exact evidence and threshold for flagging a mutation-loss outlier, and
  whether a future DCF-like extension is needed.
- Whether the current fixed normal CN and error-rate assumptions should become
  input fields in a future contract.
- The richer prior over clone-specific CNV timing, allele-specific copy number,
  and genotype candidates.

## Evidence

- [Multiplicity latent-variable review](../../research/multiplicity_latent_variable_review.md)
- [Current model target/spec](../../model.md:29)
- [Current genotype candidate construction](../../inference/src/model.cpp:131)
- [Current likelihood marginalization](../../inference/src/model.cpp:255)
