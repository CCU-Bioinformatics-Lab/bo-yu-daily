# C++ tumor-tree inference backend

This directory contains the active, replaceable C++17 backend for the
canonical model table. Python owns table construction, grouped holdout,
provenance and outer diagnostics; this executable owns Rao–Blackwellized
annealed SMC.

## Architecture

```text
CanonicalTable loader → AlgorithmRegistry → rao_blackwellized_annealed_smc
       │                         │
       └─ immutable SNV rows     └─ particle/repeat parallel execution
```

The particle state is `(topology, eta)`: a legal tree with one tumor founder
and a positive local-mass simplex. `phi`/CCF is derived from descendant sums.
SNV assignment and multiplicity are integrated inside the site likelihood and
reported as posterior responsibilities; they are not external table fields.

At each annealing stage the backend increases `beta`, checks conditional and
weighted particle ESS, applies systematic resampling when required, then runs
topology and eta rejuvenation. The final population is published with equal
weights. The likelihood uses bulk counts, ASCAT static CN and `rho_ASCAT`; HP
counts are validated supplementary information and are not a Model A term.

## Build

```bash
cmake -S inference -B inference/build -DCMAKE_BUILD_TYPE=Release
cmake --build inference/build --parallel
ctest --test-dir inference/build --output-on-failure
```

For a clean workspace build, use `/tmp/tumor_tree_inference_build`. The
workflow locates the executable through `TUMOR_TREE_INFERENCE_BIN` or
`inference/build/tumor_tree_inference`.

## CLI

```bash
inference/build/tumor_tree_inference run \
  --algorithm rao_blackwellized_annealed_smc \
  --input likelihood_input.tsv.gz \
  --outdir output/cpp_smoke \
  --seed 20260820 --num-nodes 6 \
  --annealing-stages 64 --particles 1024 \
  --ess-threshold 0.5 --purity 0.99 \
  --checkpoint-every 1 --threads 4 --repeats 4 \
  [--exclude-file holdout.ids]
```

`--annealing-stages` limits the beta schedule, `--particles` sets the
population size, and `--repeats` launches independent populations with
different derived seeds. `--threads` controls repeat parallelism and the
site scorer without nested oversubscription. `--resume` only accepts a
completed immutable repeat; an unfinished checkpoint is fail-closed.

## Input contract

The loader requires schema `hcc1395_tumor_tree_input/v4`:

```text
mutation_id chrom pos ref alt ref_reads alt_reads total_reads
hp1_1_ref hp1_1_alt hp2_1_ref hp2_1_alt
major_cn minor_cn total_cn rho_ASCAT model_include model_status
```

Only `model_include=yes` and `model_status=eligible` rows enter the model.
Counts, depth, ASCAT purity and CN consistency are validated. The loader
builds CN-constrained multiplicity support from major/minor CN; old
`multiplicity_candidates`, `multiplicity_prior`, `multiplicity_posteriors` and
`tumor_dna_fraction` columns are rejected. PS is upstream phase provenance,
not a direct likelihood column.

## Artifacts

Each completed repeat writes:

- `samples.jsonl.gz`: equal-weight records marked `sample_kind=smc_particle`;
- `particle_history.jsonl.gz`: stage weights and ancestor records;
- `multiplicity_posterior.tsv.gz`: per-SNV, per-candidate posterior output;
- `posterior_summary.tsv.gz`: CCF/phi medians and 95% intervals;
- `topology_summary.tsv`: canonical edge support;
- `representative_tree.json`: selected topology and assignment summary;
- `diagnostics.json`: beta, ESS, resampling, diversity and rejuvenation metrics;
- `checkpoint.json.gz`: particle state, weights, ancestry and RNG audit;
- `smc_complete.json`: terminal completion marker, written last.

A failed process must be rerun into a fresh output directory unless a complete
immutable repeat already exists. The Python workflow never promotes partial
artifacts.
