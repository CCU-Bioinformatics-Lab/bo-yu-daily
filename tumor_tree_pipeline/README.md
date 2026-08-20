# Tumor-tree pipeline

This package is the version-controlled execution source for the HCC1395
30,490-site finite-K candidate tumor-tree analysis.

## Module interfaces

- `input_table.build_model_table(...)`: validated counts + ASCAT CN/purity →
  canonical site-level table and provenance manifest.
- `sampler.run_chain(...)`: one immutable finite-K chain from the canonical
  table.
- `workflow.run_experiment(...)`: smoke, pilot, K sensitivity, purity
  sensitivity, multi-chain diagnostics, holdouts, and atomic status markers.

## Non-negotiable invariants

- Purity is the ASCAT output `rho_ASCAT`; there is no
  `tumor_dna_fraction` compatibility interface.
- Multiplicity enters as a CN-only `multiplicity_prior`.  Bulk REF/ALT counts
  are used once, in the likelihood.
- PS never enters the likelihood.  It may be used for read-level audit and
  grouped holdout only.
- Canonical loading is fail closed: no legacy files, diploid CN, or point
  multiplicity fallbacks.
- The eta root is residual tumor-population mass; normal contamination is
  handled only by `rho_ASCAT` in the emission model.
- Production output directories are immutable and receive `_SUCCESS` only
  after every required gate passes.

Large BAM/VCF/ASCAT inputs remain outside Git and are referenced by manifests
with paths, metadata, and hashes.
