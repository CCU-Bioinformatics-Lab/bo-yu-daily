# C++ tumor-tree inference backend

This directory is the active, replaceable C++17 backend for the canonical model
table. The Python workflow still owns table construction, grouped holdout,
provenance, and diagnostics; its default chain runner calls this executable.

## Architecture

```text
CanonicalTable loader  ->  AlgorithmRegistry  ->  Algorithm::run
        |                         |
        +-- immutable sites       +-- plain_metropolis_hastings
                                  +-- future algorithm implementations
```

`Algorithm` is the seam for adding another sampler. Register a new
implementation in `src/registry.cpp` and expose its name through the CLI. Each chain owns its
`std::mt19937_64`, latent state, output directory, and counters. No chain shares
mutable state. The likelihood scorer parallelizes independent site rows; its
final state score is reduced in site order, so `--threads 1` and `--threads 2`
are deterministic for the same chain configuration.

The current state is exactly `(parents, eta, z)`. Every iteration chooses one
of three proposal moves with probability 1/3 and performs one MH decision:

- assignment: move one SNV to another clone;
- eta: Dirichlet random walk, concentration 80, with proposal correction;
- topology: one valid parent reassignment, with finite-support correction.

There is no Gibbs sweep, eta bridge, assignment mixture, split-merge move, or
overdispersed initialization in this backend. Multiplicity is a CN-only prior
and is marginalized inside the site emission calculation.

## Build

```bash
cmake -S inference -B inference/build -DCMAKE_BUILD_TYPE=Release
cmake --build inference/build --parallel
ctest --test-dir inference/build --output-on-failure
```

For a clean workspace build, use `/tmp/tumor_tree_inference_build` instead of
`inference/build`. The Python workflow locates the executable through
`TUMOR_TREE_INFERENCE_BIN` or `inference/build/tumor_tree_inference`.

The only external library is zlib, used for `.tsv.gz`, `samples.jsonl.gz`, and
`checkpoint.json.gz`. JSON is emitted by the small checked-in writer in
`src/json.cpp`; no third-party JSON library is required.

## CLI

```bash
inference/build/tumor_tree_inference \
  --algorithm plain_metropolis_hastings \
  --input likelihood_input.tsv.gz \
  --outdir output/cpp_smoke \
  --seed 20260820 --num-nodes 6 --iterations 1500 --burnin 1000 \
  --thin 1 --purity 0.99 --checkpoint-every 100 \
  --threads 4 --chains 4 [--exclude-file holdout.ids]
```

With one chain, artifacts are written directly under `--outdir`. With more
than one chain they are written under `--outdir/chain_01`, `chain_02`, etc.
`--threads` controls site scoring for one chain and chain-level parallelism for
multiple chains to avoid nested oversubscription. `--resume` is accepted only
to fail closed with an explicit unsupported message. The current checkpoint is
an audit/state snapshot, not a supported restore input. No Python workflow or
ESS-extension path may treat its presence as evidence that a chain resumed;
start a fresh output directory until a versioned C++ restore reader exists.

The Python workflow invokes one chain at a time, keeping each chain's output
directory independent. Set `TUMOR_TREE_INFERENCE_THREADS` to a positive integer
to parallelize site scoring inside each workflow chain. The standalone CLI can
parallelize independent chains with `--chains N`; it assigns separate derived
seeds and avoids nested chain/site oversubscription.

## Input contract

The loader requires the existing model columns:

```text
mutation_id chrom pos ref alt bulk_ref bulk_alt bulk_depth
hp1_1_ref hp1_1_alt hp2_1_ref hp2_1_alt
major_cn minor_cn total_cn rho_ASCAT
multiplicity_candidates multiplicity_prior model_include model_status
```

Only `model_include=yes` and `model_status=eligible` rows enter the model.
Counts, depth, ASCAT purity, CN consistency, candidate ordering, and prior
normalization are validated. `tumor_dna_fraction` and
`multiplicity_posteriors` are rejected. PS is not a direct C++ likelihood
column; its upstream phasing role is represented by the already materialized
HP1-1/HP2-1 counts.

## Artifacts

Each completed chain writes the schema consumed by the Python diagnostics
adapter:

- `samples.jsonl.gz`: one retained record per line with `iteration`,
  `log_posterior`, `parents`, `eta`, `phi`, and `occupancy`;
- `diagnostics.json`: algorithm, input hash, config, roles, proposal counters,
  acceptance rates, posterior summary, and `phi_mean`;
- `representative_tree.json`: `selected_edges`,
  `best_sample_assignments`, and `posterior_map_assignments`;
- `checkpoint.json.gz`: version, input hash, config, exclusions, state, score,
  counters, retained samples, assignment counts, best sample, and serialized
  RNG state for audit/forward implementation work; it is not currently
  accepted by `--resume`;
- `chain_complete.json`: terminal completion marker written last.

Each chain directory also has an internal short-lived `.run.lock` during
execution. It is removed after completion or failure and prevents two
processes from claiming the same output directory. A failed process must be
rerun into a fresh directory; the C++ backend does not currently restore from
its checkpoint.
