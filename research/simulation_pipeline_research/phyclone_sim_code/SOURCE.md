# 程式來源對照

- 上游：`https://github.com/Roth-Lab/PhyClone.git`
- 版本：submodule commit `2738324`（Merge pull request #18 from Roth-Lab/drop_pickle）
- 複製日期：2026-10-21
- 授權：GPL-3.0，全文見 [`LICENSE.md`](LICENSE.md)。

這裡的檔案是**未修改的快照**，只供閱讀與對照。檔案內的 import 仍指向 `phyclone.tests.utilities.*`。要執行，請在已安裝 PhyClone 的環境中跑 submodule 內的原檔。

## 檔案對照

| 本目錄 | 上游路徑（相對 `research/phyclone_research/PhyClone/`） | 角色 |
|---|---|---|
| `utilities/fscrp.py` | `phyclone/tests/utilities/fscrp.py` | 生成樹：CRP 分群 → 樹 → clonal／cellular prevalence |
| `utilities/sim_data_on_tree.py` | `phyclone/tests/utilities/sim_data_on_tree.py` | 在樹上生成 CN、genotype、ref／alt 計數，並轉成 likelihood grid |
| `utilities/simulate.py` | `phyclone/tests/utilities/simulate.py` | 玩具資料：直接用 Binomial(n, p) 產生一個 data point |
| `utilities/importance_sampler.py` | `phyclone/tests/utilities/importance_sampler.py` | 用 importance sampling 估計固定樹的 likelihood（驗證用） |
| `utilities/exact_posterior.py` | `phyclone/tests/utilities/exact_posterior.py` | 小資料的 posterior 窮舉（驗證用） |
| `utilities/old_implementations.py` | `phyclone/tests/utilities/old_implementations.py` | `exact_posterior.py` 依賴的舊版 `OldTree` |
| `tests/test_marginalisation.py` | `phyclone/tests/integration_tests/test_marginalisation.py` | 補充文件 S2.3.2：模擬 → PhyClone likelihood vs IS likelihood |
| `tests/test_pg_posterior.py` | `phyclone/tests/unit_tests/test_pg_posterior.py` | 補充文件 S2.3.1：模擬 → PG sampler vs 窮舉 posterior |
| `examples/mixing_small.tsv` | `examples/data/mixing_small.tsv` | PhyClone 輸入格式範例 |
| `examples/mixing_small_clusters.tsv` | `examples/data/mixing_small_clusters.tsv` | cluster 輸入格式範例 |

`examples/` 的 mutation ID 含 1000 Genomes 樣本名（NA12878 等），推測是細胞混合實驗的真實資料，不是模擬資料。〔推論〕

## 模擬器依賴的推理端程式（未複製）

| 上游路徑 | 被誰用 | 用途 |
|---|---|---|
| `phyclone/data/pyclone.py::get_major_cn_prior` | `sim_data_on_tree.py` | 由 major／minor CN 列出候選 genotype 與均勻 prior |
| `phyclone/data/pyclone.py::SampleDataPoint`、`PyCloneDataPoint.to_likelihood_grid` | `sim_data_on_tree.py`、`importance_sampler.py` | 把計數轉成 CCF grid 上的 log-likelihood |
| `phyclone/data/pyclone.py::compute_outlier_prob` | `simulate.py` | outlier prior 的 log 值 |
| `phyclone/data/base.py::DataPoint` | `simulate.py`、`sim_data_on_tree.py` | 推理端的 data point 物件 |

`phyclone/tests/` 內其他測試（`test_proposal_caching.py`、`test_prune_regraph_sampler.py`、`test_rustworkx.py`、`test_tree_shell_node_adder.py`、`test_pg_subtree_posterior.py`、`test_clonal_prev.py`）也呼叫這些模擬函式，但只拿它們當測試輸入，沒有複製。
