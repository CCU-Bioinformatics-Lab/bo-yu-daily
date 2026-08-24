# C++ inference contract tests

These black-box tests exercise the C++ Rao–Blackwellized annealed-SMC
executable through its public CLI. They use only Python's standard library and
do not import the Python workflow.

## CLI contract

```text
inference_binary run \
  --input canonical.tsv \
  --output output_dir \
  --algorithm rao_blackwellized_annealed_smc \
  --seed 20260820 \
  --repeats 1 --threads 1 \
  --annealing-stages 24 --particles 32 \
  --num-nodes 2 --rho-ascat 0.99
```

The `run` subcommand, `--output`, and `--rho-ascat` are accepted as friendly
aliases for `--outdir` and `--purity`. The canonical table must use
`hcc1395_tumor_tree_input/v4` and include all four HP count fields. The loader
builds multiplicity candidates from major/minor CN; no multiplicity column is
read.

The tests verify that changing only supplementary HP allocation does not
change the Model A likelihood or multiplicity posterior, that every particle
has one tumor founder, that `phi` is the descendant sum of `eta`, and that
beta reaches one with valid ESS/resampling/rejuvenation diagnostics.

## Output contract

One repeat contains:

```text
samples.jsonl.gz
particle_history.jsonl.gz
multiplicity_posterior.tsv.gz
posterior_summary.tsv.gz
topology_summary.tsv
diagnostics.json
representative_tree.json
checkpoint.json.gz
smc_complete.json
```

With `--repeats 2`, the same artifacts are written under `repeat_01/` and
`repeat_02/`, with distinct derived seeds. Completed output directories are
immutable. Invalid schema, purity mismatch, unknown algorithm, and overwrite
attempts exit non-zero without leaving an `smc_complete.json` marker.

## Running

```bash
inference/tests/run_contract_tests.sh inference/build/tumor_tree_inference
```

The test uses a temporary output root and does not modify repository outputs.
