# Methods Validator status

State: **COMPLETE**

Completed scope:

- Independently read and compared the main-paper, supplement, and code evidence packets.
- Re-read the extracted primary-source method passages and current source modules cited in the validation.
- Compared current checkout `0.8.0` with local tag `0.7.0` for the highest-risk version-sensitive findings.
- Validated model, allele-count likelihood, CN/purity handling, priors, tree representation, clonal/cellular prevalence, DP marginalization, SMC/PG inference, preprocessing, pre-clustering, outliers, loss heuristic, outputs, and defaults.
- Classified findings as `EXACT`, `APPROXIMATE`, `PAPER_ONLY`, `CODE_ONLY`, `ADDITIONAL_IMPLEMENTATION_DETAIL`, or `POSSIBLE_MISMATCH`.
- Recorded six explicit conflicts with resolved/unresolved status and stable evidence locators.

Primary results:

1. Central paper/supplement method maps closely to code.
2. Published outlier Uniform integral vs implemented triangular double sum: **UNRESOLVED, likely mismatch**, present in 0.7.0 and 0.8.0.
3. Bootstrap with active outliers: **confirmed 0.8.0 proposal/log-density regression**; 0.7.0 was consistent and paper benchmarks used semi-adapted.
4. Subtree PG correctness: **UNRESOLVED**, with explicit TODO in both versions; path disabled by default.
5. Supplement dummy-root dimension typo and paper complexity shorthand: **RESOLVED through code/supplement reconciliation**.
6. CLI/API defaults: **RESOLVED by keeping entry points and benchmark configuration separate**.

Output:

- `.agent_workspace/methods/methods_validation.md`
- `.agent_workspace/methods/status.md`

Boundary honored: wrote only under `.agent_workspace/methods/`; did not modify `notes/` or source artifacts; did not read outside the workspace root.
