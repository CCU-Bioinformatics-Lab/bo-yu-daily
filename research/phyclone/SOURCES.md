# Sources and provenance

研究日期：2026-08-25（Asia/Taipei）。以下以 primary sources 為主；GitHub source code 以保存的 commit hash 為準。

## Paper

| ID | Primary source | Local copy | 用途 |
|---|---|---|---|
| `paper-oup` | [Bioinformatics article](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563), DOI [`10.1093/bioinformatics/btaf344`](https://doi.org/10.1093/bioinformatics/btaf344) | `PhyClone_paper.pdf` | 正式論文、方法、實驗與 discussion |
| `paper-pmc` | [PubMed Central full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12964358/) | `PhyClone_paper.xml` | 結構化全文、figure、data/code availability |
| `paper-supp` | [Europe PMC supplementary files](https://europepmc.org/articles/PMC12964358/bin/btaf344_supplementary_data.zip) | `btaf344_supplementary_data.zip`, `paper_supplement/` | Supplementary Methods、correctness tests、metrics tables |
| `paper-data` | [Zenodo benchmark data concept DOI](https://doi.org/10.5281/zenodo.13240565); latest record [15065504](https://zenodo.org/records/15065504) | URL/DOI recorded; data not duplicated here | TSSB/FS-CRP synthetic、method inputs/outputs |
| `paper-code-archive` | [Zenodo PhyClone Code v0.7.0](https://zenodo.org/records/15062185), concept DOI [10.5281/zenodo.15062184](https://doi.org/10.5281/zenodo.15062184) | URL/DOI recorded; current Git clone below | exact paper benchmarking source provenance |

SHA-256：

- `PhyClone_paper.pdf`: `a4b296065e2223ad74be4eb8d88f6731428423fe00c64c8f92a7a63533d50871`
- `PhyClone_paper.xml`: `8c9f16e8f75e3ebf0638126b1537d00b925fb7a1c3614963c4fbf52ebd7b02e8`
- `btaf344_supplementary_data.zip`: `072f2b3e0c40be6984d9e232bbae7929cf2174d93d7de60891d74be63c224ab6`

## Official source repositories

| ID | Repository | Local commit | License / role |
|---|---|---|---|
| `code-phyclone` | [Roth-Lab/PhyClone](https://github.com/Roth-Lab/PhyClone) | `27383246c1aff7b1d62c02662017bd61bfdfbc33` | GPL-3.0-or-later; model, PG-SMC, HDF5 trace and summarisation |
| `code-workflow` | [Roth-Lab/PhyClone-Workflow](https://github.com/Roth-Lab/PhyClone-Workflow) | `66b63a3502d2eaebdc986cf8d97ab57cb651b2b2` | GPL-3.0; PyClone-VI → PhyClone Snakemake workflow |

The clones were downloaded with `--depth 1` on 2026-08-25. They are retained as research artifacts; they are not vendored into the active inference build.

## Local evidence anchors used by the explainer

- Paper model and experiments: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone_paper.xml`
- Supplementary model/inference/correctness: `/bip8_disk/boyu114/main_work/research/phyclone/paper_supplement/content/supp.pdf`
- Input schema: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/validator/PhyClone_schema.json`
- Cluster schema: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/validator/cluster_file_schema.json`
- Input filtering/loading: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/pyclone.py`
- Run options: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/cli.py`
- Trace layout: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/utils/save_hdf5.py`
- Result materialisation: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/process_trace/process_trace.py`
- End-to-end workflow: `/bip8_disk/boyu114/main_work/research/phyclone/PhyClone-Workflow/workflow/rules/phyclone.smk`
