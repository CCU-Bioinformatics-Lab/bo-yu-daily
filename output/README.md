# Generated experiment outputs

Large input tables, checkpoints, logs, and posterior samples are intentionally
ignored by Git.  Each immutable run may commit only its small reproducibility
receipt: manifests, exact command, QA/gate summaries, diagnostics summary,
representative tree, and final `_SUCCESS` or `_FAILED` marker.

The authoritative execution code lives in `tumor_tree_pipeline/`; generated
artifacts are never a substitute for versioned source and tests.
