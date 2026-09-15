# Code Analyst status

Overall: **COMPLETE**

Substatus:

- Repository inventory and version: COMPLETE
- Input/schema/preprocessing: COMPLETE
- Likelihood/CNV/tumour-content mapping: COMPLETE
- FS-CRP/tree/cluster representation: COMPLETE
- Cellular/clonal prevalence and DP marginalization: COMPLETE
- Outlier and data-informed loss handling: COMPLETE
- SMC/Particle Gibbs/proposals/additional moves: COMPLETE
- Trace/MAP/consensus/topology outputs: COMPLETE
- Defaults and CLI/API conflicts: COMPLETE
- Static tests/evaluation inventory: COMPLETE
- Runtime validation: PARTIAL — environment lacks declared dependencies and required Python version

Files written:

- `.agent_workspace/code/code_analysis.md`
- `.agent_workspace/code/status.md`

Important unresolved findings delivered:

1. Possible mismatch between the paper's single Uniform outlier integral and code's cumulative-plus-second-grid-sum marginal.
2. Possible bootstrap proposal sampling/log-density inconsistency when outlier modelling is active.
3. Subtree PG correctness TODO in source.
4. Material CLI vs direct-Python defaults and outlier-activation differences.
5. No paper benchmark/evaluation pipeline in this repository checkout.

Runtime evidence:

- `test_root_term`: 8 tests passed.
- Five other requested test modules could not import because `numba`, `networkx`, or `xxhash` are unavailable under local Python 3.10; repository requires Python >=3.12. This is an environment limitation, not an assertion failure.
