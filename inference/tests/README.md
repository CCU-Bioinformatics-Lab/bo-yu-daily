# C++ inference contract tests

These are black-box tests for the C++ plain Metropolis--Hastings executable.
They use only Python's standard library and do not import the Python pipeline.
The tests deliberately live under `inference/tests/` so the C++ implementation
can be replaced without changing the test seam.

## CLI contract under test

The executable is invoked as:

```text
inference_binary run \
  --input canonical.tsv \
  --output output_dir \
  --algorithm plain_metropolis_hastings \
  --seed 20260820 \
  --chains 1 --threads 1 \
  --iterations 24 --burnin 8 --thin 1 --num-nodes 2 \
  --rho-ascat 0.99
```

The `run` subcommand, `--output`, and `--rho-ascat` are compatibility aliases
for the canonical `--outdir` and `--purity` interface.

The canonical table must contain the current `hcc1395_tumor_tree_input/v2`
required columns, including all four HP fields:
`hp1_1_ref`, `hp1_1_alt`, `hp2_1_ref`, and `hp2_1_alt`. Every included row
must carry `rho_ASCAT=0.99`; multiplicity is represented by the CN-only
`multiplicity_candidates` and `multiplicity_prior` fields.

## Output contract

For one chain, the output directory contains the five required artifacts:

```text
samples.jsonl.gz
diagnostics.json
representative_tree.json
checkpoint.json.gz
chain_complete.json
```

For `--chains 2`, the same five artifacts are required under `chain_01/` and
`chain_02/`. Each chain's `diagnostics.json` records a distinct derived seed.
The diagnostics also identify plain MH, schema `v2`, the observed site count,
state variables `[parents, eta, z]`, ASCAT purity, and the CN-only
multiplicity-marginalized site term.

`--threads 1` and `--threads 2` must produce identical decompressed artifacts.
If an implementation intentionally permits thread-order differences, the
outputs may differ only when `diagnostics.json` contains a non-empty
`deterministic_policy` string explaining that policy.

Completed output directories are immutable. Invalid schema, any
`rho_ASCAT`/`--rho-ascat` mismatch, an unknown algorithm, and attempts to
overwrite a completed directory must exit non-zero and must not leave a
`chain_complete.json` marker.

## Running

After the CMake build:

```bash
inference/tests/run_contract_tests.sh inference/build/tumor_tree_inference
```

The wrapper also checks `INFERENCE_BINARY` and the conventional paths under
`inference/build/`. A CMake project can register the same seam with:

```cmake
add_test(
  NAME inference_contract
  COMMAND ${Python3_EXECUTABLE}
          ${CMAKE_CURRENT_SOURCE_DIR}/tests/contract_test.py
          --binary $<TARGET_FILE:tumor_tree_inference>
)
```

The test exits non-zero on any contract violation and uses a temporary output
root, so it never modifies repository `output/` artifacts.
