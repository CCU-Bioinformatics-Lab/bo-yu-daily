# C++ tumor-tree inference backend

This directory is the active, replaceable C++17 backend for the canonical model
table. The Python workflow still owns table construction, grouped holdout,
provenance, and diagnostics; its default chain runner calls this executable.

Until the C++ implementation, rebuilt canonical input, tests, and workflow
gates are synchronized and passing, backend outputs are `diagnostic-only`.
Legacy-schema artifacts are rejected and cannot be promoted to formal output.

## Architecture

```text
CanonicalTable loader  ->  AlgorithmRegistry  ->  Algorithm::run
        |                         |
        +-- immutable sites       +-- phylowgs_inspired_tssb_mcmc
                                  +-- future algorithm implementations
```

`Algorithm` is the seam for adding another sampler. Register a new
implementation in `src/registry.cpp` and expose its name through the CLI. Each chain owns its
`std::mt19937_64`, latent state, output directory, and counters. No chain shares
mutable state. The likelihood scorer parallelizes independent site rows; its
final state score is reduced in site order, so `--threads 1` and `--threads 2`
are deterministic for the same chain configuration.

The current sampled state is exactly `(parents, eta, z)`, where `eta` is the simplex
of local clone masses and `phi` is the descendant-sum frequency for each node.
This is a finite-truncated, TSSB-inspired approximation of PhyloWGS, not a
claim to reproduce its full infinite tree implementation. Every iteration is
a compound MCMC sweep:

- assignment: categorical Gibbs update for every SNV using local mass and the
  Model A bulk/CN/purity emission; HP counts are supplementary and are not read
  by the active primary likelihood;
- eta: Dirichlet proposal centred on assignment counts and TSSB-shaped depth/
  width prior, accepted with an MH emission correction;
- topology: conditional subtree prune-and-regraft Gibbs draw over every legal
  parent for one selected node.

The original PhyloWGS uses TSSB assignments, stick/order resampling and
hyperparameter updates. This backend keeps a fixed K candidate-node set for the
current workflow and uses a PhyloWGS-style CN-constrained latent multiplicity
emission: the loader creates candidate copy counts from major/minor CN, the
Model A emission updates their posterior responsibility with bulk counts,
static-CN context, fixed `rho_ASCAT=0.99`, and clone prevalence, and the result is written to
`multiplicity_posterior.tsv.gz`. PS is upstream provenance for HP counts, not a
direct tree-likelihood column.

The active structural assumptions are exactly one tumor founder below the
structural root, no-loss/infinite-sites inheritance for SNVs, and static ASCAT
CN context across tumor clones. The baseline sequencing-error rate is fixed at
`e=0.005`. `phi` is derived from descendant sums; it is summarized as a CCF
posterior median with a 95% credible interval.

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
  --algorithm phylowgs_inspired_tssb_mcmc \
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

The loader requires the schema `hcc1395_tumor_tree_input/v4` model columns:

```text
mutation_id chrom pos ref alt ref_reads alt_reads total_reads
hp1_1_ref hp1_1_alt hp2_1_ref hp2_1_alt
major_cn minor_cn total_cn rho_ASCAT model_include model_status
```

Only `model_include=yes` and `model_status=eligible` rows enter the model.
Counts, depth, ASCAT purity and CN consistency are validated. After parsing
`major_cn` and `minor_cn`, the loader creates the internal multiplicity support
and CN prior used by the likelihood. The emission then computes a posterior
responsibility for every candidate at each sampled clone prevalence. The old
`multiplicity_candidates` and `multiplicity_prior` table fields, as well as
`tumor_dna_fraction` and `multiplicity_posteriors`, are rejected. PS is not a
direct C++ likelihood column; its upstream phasing role is retained only as
supplementary HP1-1/HP2-1 counts for QC, provenance, holdout, and future Model B.
The active Model A scorer must not treat those HP counts as an additional
likelihood term.

Promotion additionally requires prior predictive checks for topology depth,
branch count, and clone mass, plus posterior predictive checks for bulk
ALT-count behavior and holdout performance. Topology and edge support are
reported after clone-label canonicalization; CCF is reported as a posterior
median with a 95% credible interval.

## Artifacts

Each completed chain writes the schema consumed by the Python diagnostics
adapter:

- `samples.jsonl.gz`: one retained record per line with `iteration`,
  `log_posterior`, `parents`, `eta`, `phi`, and `occupancy`;
- `multiplicity_posterior.tsv.gz`: one row per SNV/candidate multiplicity with
  `prior` and retained-draw `posterior_mean`; this is a model output, never an
  input column;
- `diagnostics.json`: algorithm, input hash, config, roles, proposal counters,
  acceptance rates, posterior summary, and `phi_mean`;
- `representative_tree.json`: `selected_edges`,
  `best_sample_assignments`, and `posterior_map_assignments`;
- `posterior_summary.tsv.gz`: CCF posterior medians and 95% credible intervals;
- `topology_summary.tsv`: label-invariant topology and edge-support summary;
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
