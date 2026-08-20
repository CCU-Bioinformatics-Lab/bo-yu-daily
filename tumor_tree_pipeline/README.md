# Tumor-tree pipeline

This package is the version-controlled execution source for the HCC1395
30,490-site finite-K candidate tumor-tree analysis.

## Module interfaces

- `input_table.build_model_table(...)`: validated bulk/HP counts plus ASCAT
  CN/purity → canonical site-level table and provenance manifest.
- `cpp_backend.run_chain_cpp(...)`: the active C++17 finite-K plain
  Metropolis-Hastings chain backend from the canonical table.
- `sampler.run_chain(...)`: retained Python reference implementation used for
  model-contract tests and numerical comparison; the default workflow does
  not use it for inference.
- `workflow.run_experiment(...)`: smoke, pilot, K sensitivity, purity
  sensitivity, independent chains for diagnostics, holdouts, and atomic status
  markers.

## Baseline input → latent state → output

```text
canonical likelihood_input.tsv.gz + ChainConfig
        │
        │  per SNV: bulk REF/ALT, HP1-1/HP2-1 counts,
        │  ASCAT major/minor/total CN, CN-only multiplicity_prior,
        │  rho_ASCAT = 0.99
        ▼
latent state: finite-K topology T, SNV assignment z, prevalence eta
        │
        │  C++ plain MH proposal and accept/reject per iteration
        ▼
samples.jsonl.gz + diagnostics.json + representative_tree.json
        + checkpoint.json.gz + chain_complete.json
```

The baseline uses the canonical table as its observed-data input. The latent
state contains only the tree topology, the clone assignment of each included
SNV, and the prevalence vector `eta` (with the root as residual tumor mass).
Multiplicity is integrated using the fixed CN-only prior; it is not a separate
sampled state. The chain output contains retained posterior draws, acceptance
diagnostics, a representative tree, and checkpoint audit metadata. C++ resume
is currently fail-closed until its versioned restore reader is implemented.

## Non-negotiable invariants

- Purity is the ASCAT output `rho_ASCAT = 0.99`; there is no
  `tumor_dna_fraction` compatibility interface.
- Multiplicity enters as a CN-only `multiplicity_prior`. Bulk REF/ALT counts are
  used once in the observation likelihood.
- The active inference method is one plain finite-K Metropolis-Hastings kernel:
  each iteration proposes one update to the topology, one SNV assignment, or
  `eta`, then applies the usual posterior-ratio accept/reject rule.
- PS is LongPhase-S upstream phasing metadata. It helps establish consistent
  HP labels/counts and therefore can affect the derived `H_i` indirectly. Once
  the table is built, PS is not a direct downstream likelihood column, a
  clone-assignment prior, or a topology-edge constraint; it may remain in
  provenance/read-level audit and grouped holdout metadata.
- Canonical loading is fail closed: no legacy files, diploid CN, or point
  multiplicity fallbacks.
- Normal contamination is handled only by `rho_ASCAT` in the emission model;
  the eta root is residual tumor-population mass.
- Production output directories are immutable and receive `_SUCCESS` only
  after every required gate passes.

Large BAM/VCF/ASCAT inputs remain outside Git and are referenced by manifests
with paths, metadata, and hashes.
