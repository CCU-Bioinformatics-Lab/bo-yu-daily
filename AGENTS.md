# Repository Guidelines

## Project Structure & Module Organization

- `inference/` contains the active C++17 SMC backend: public headers in `include/`, implementation in `src/`, and C++/contract tests in `tests/`.
- `tumor_tree_pipeline/` contains the Python workflow, input contracts, configurations, diagnostics, and Python tests/fixtures.
- Root Markdown files define the research modules: `data.md`, `model.md`, `inference_algo.md`, `output.md`, `validation.md`, and `experiment_workflow.md`.
- `output/` stores generated input bundles and experiment artifacts; `daily/YYYYMMDD/` stores daily HTML records. Treat generated outputs as provenance records, not source code.

## Build, Test, and Development Commands

```bash
cmake -S inference -B inference/build -DCMAKE_BUILD_TYPE=Release
cmake --build inference/build --parallel
ctest --test-dir inference/build --output-on-failure
inference/tests/run_contract_tests.sh inference/build/tumor_tree_inference
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tumor_tree_pipeline/tests -p 'test_*.py'
```

Use the fixture smoke workflow before larger experiments:

```bash
TUMOR_TREE_INFERENCE_THREADS=4 PYTHONDONTWRITEBYTECODE=1 \
  python3 -m tumor_tree_pipeline run \
  --config tumor_tree_pipeline/configs/smoke.active.json
```

Follow `experiment_workflow.md` for pilot/formal gates and stop conditions.

## Coding Style & Naming Conventions

Preserve the existing C++17 style: four-space indentation, `PascalCase` types, and `snake_case` functions/files. Use Python `snake_case`, `test_*.py` test names, and explicit type/contract checks where already present. No repository-wide formatter is configured; keep diffs focused and readable.

## Testing Guidelines

Add or update tests with behavior changes. C++ contract/smoke tests belong in `inference/tests`; Python workflow tests belong in `tumor_tree_pipeline/tests`. Run both suites for backend or workflow changes. Do not claim a pilot is formal validation: inspect its receipts and diagnostics.

## Research and Data Boundaries

Keep the v4 canonical input contract and `rho_ASCAT` purity boundary intact. Multiplicity is inferred inside the C++ model; do not reintroduce legacy input columns such as `tumor_dna_fraction`. Keep model, inference, output, and validation descriptions modular.

## Agent Information Retrieval

When investigating repository state, first scan relevant `daily/` HTML for a quick overview of recent decisions and experiments. Then follow `README.md`'s order—`arch.md` → `data.md` → `model.md` → `inference_algo.md` → `output.md` → `validation.md`—and verify claims against source code, tests, manifests, and receipts. Treat daily HTML as orientation/history, not authority; never use it alone. Separate current, historical, and uncommitted work.

## Commit & Pull Request Guidelines

Recent history uses scoped conventional prefixes such as `feat:`, `fix:`, `docs:`, `data:`, `refactor:`, and `docs(daily):`. Use a short imperative subject and one logical change per commit. PRs should describe affected modules, tests run, experiment/output provenance, and any known gate limitations. For HTML changes, include a screenshot or rendered-file path; do not commit unrelated generated artifacts or rewrite remote history.
