# Tumor-tree pipeline

This package is the version-controlled execution source for the HCC1395
30,490-site candidate tumor-tree analysis.

The model contract is [`../model.md`](../model.md); the replaceable inference
contract is [`../inference_algo.md`](../inference_algo.md). This package owns
table construction, workflow control, grouped holdout handling, provenance
and diagnostics.

## Module interfaces

- `input_table.build_model_table(...)`: validated bulk/HP counts plus ASCAT
  CN/purity → canonical site-level table and provenance manifest.
- `cpp_backend.run_smc_cpp(...)`: invoke the active C++17 finite-K
  Rao–Blackwellized annealed-SMC backend from the canonical table.
- `workflow.run_experiment(...)`: smoke, pilot, K sensitivity, purity
  sensitivity, independent SMC repeats, grouped holdouts, atomic status
  markers, and durable execution trace.

The complete cross-module workflow is in
[`../experiment_workflow.md`](../experiment_workflow.md).

## Input → particle state → output

```text
canonical likelihood_input.tsv.gz
        │  bulk reads + ASCAT CN + rho_ASCAT
        ▼
SMC particles: legal topology + eta
        │  beta schedule, ESS, resampling, rejuvenation
        ▼
samples + CCF/phi + topology + assignment + multiplicity posterior
```

Model A uses bulk counts, ASCAT CN, fixed `rho_ASCAT=0.99`, and multiplicity
support built inside the C++ loader. HP counts remain supplementary and are
not a primary likelihood term. `phi` is derived from descendant sums and the
structural tumor root has frequency one.

## Invariants

- Purity is the ASCAT output `rho_ASCAT = 0.99`; there is no
  `tumor_dna_fraction` interface.
- `multiplicity_candidates` and `multiplicity_prior` are not canonical table
  fields; the loader creates their internal support from major/minor CN.
- The active backend is `rao_blackwellized_annealed_smc`; its particle state is
  topology and eta, while assignment and multiplicity are marginalized and
  summarized after inference.
- PS is upstream phase provenance for HP counts. It is not a clone label,
  topology edge, or direct Model A likelihood feature.
- Exactly one tumor founder, no-loss/infinite-sites SNV inheritance, fixed K
  candidate nodes (`K=6` primary; `K=4/8` sensitivity), and static ASCAT CN are
  the current structural assumptions.
- Output directories are immutable. A run gets `_SUCCESS` only after every
  requested stage and gate passes; failures get `_FAILED` and an execution
  trace.

Large BAM/VCF/ASCAT inputs remain outside Git and are referenced by manifests
with paths, metadata and hashes.
