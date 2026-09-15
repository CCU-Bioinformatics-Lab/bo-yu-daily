# Experiment Validator status

State: **COMPLETE**

Completed:

- Reconstructed all six major experimental units as question → dataset/setup → baselines → metrics → raw XLSX evidence → reported result → interpretation → supported claim.
- Independently recomputed central means, condition trends, success/failure counts, posterior missingness, HGSOC values, and pairwise directions.
- Checked every Nemenyi `significant` flag against the paper's `p<0.01` rule.
- Recomputed Friedman tests from visible raw cells and documented exact matches plus non-decision-changing p-value discrepancies.
- Resolved the Pairtree 576-versus-720 issue from the actual omitted `K,M` combinations.
- Identified failure penalties (V/AD=0, RRE=1, LPR=1.5), severe Pairtree resource missingness, absent CN perturbation labels, and the S6/S23 fastBE–PhyClone AD conflict.
- Mapped main/supplement figures and tables to workbook sheets.
- Confirmed the repository checkout lacks the paper's evaluation/statistics pipeline.

Unresolved items are explicitly retained in `experiment_validation.md`; no files outside `.agent_workspace/experiments/` were modified.
