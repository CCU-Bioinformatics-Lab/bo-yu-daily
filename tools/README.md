# tools 索引

分析與繪圖腳本。整理日期：2026-11-04。每支腳本開頭的 docstring 有完整用法；本檔只說「哪支做什麼、先用哪支」。

從 repo 根目錄執行（`python3 -I tools/<腳本>`）。新寫腳本時，先查本檔有沒有能用的，再新增；新增後在對應的表加一列。

## 共用核心（先用這些）

以下腳本被多個實驗或其他腳本使用。改它們會影響很多結果，改之前先跑一次舊的實驗對照。

| 腳本 | 做什麼 | 被誰用 |
|---|---|---|
| `diplosim_ppc_hcc1395.py` | diplosim 和真實 HCC1395 的比較主程式：`real`（真實端 pileup）、`sim`（跑 diplosim）、`compare`（統計量與圖） | 19 個實驗、7 支腳本 |
| `diplosim_purity_holdout_v2.sh` | 一個 purity 跑完整比較流程：`NAME PURITY COVERAGE REAL_DIR` | purity holdout 系列 |
| `plot_diplosim_ppc_hcc1395.py` | PPC 的圖：每個統計量一格，模擬分布對真實值 | PPC 系列 |
| `ppc_distance_score.py` | 用距離（相對差距、z）評分 PPC，取代「在不在區間內」 | holdout、投影片 |
| `diplosim_ppc_mask_real.py` | 只重算真實端，可排除指定區域（例：抗體基因區），模擬端沿用 | `2026-11-03_diplosim_mask_ig_loci` |
| `diplosim_estimate_knobs.py` | 不跑模擬，直接從真實資料估 diplosim 旋鈕 | 11-01 系列 |
| `hcc1395_hp_split_prepare.sh` → `hcc1395_hp_split.py` | 真實 HCC1395 的 phasing、haplotag，再量 somatic SNV 的 HP 訊號 | PPC 真實端 |
| `seqc2_hcc1395_purity.py` | 用 SEQC2 真值量 HCC1395 subsample 的實測 purity | 5 支腳本 |
| `check_slides.py` | 檢查投影片是否符合 `report/report_rule.md` 的規則 | 每次做投影片（`CLAUDE.md` 交付 5） |

## diplosim 驗證主流程

> **2026-11-04 起暫停**（`diplosim/DECISIONS.md`）。以下只供重現既有結果，不要用來開新的 HCC1395 實驗。

1. **真實端（每個 subsample 一次）：** `bash tools/diplosim_purity_holdout_one.sh ...`：haplotag、ClairS HC 位點、pileup。
2. **模擬＋比較：** 設定 `OUT_ROOT`、`DIPLOSIM_PPC_RANGES=tools/diplosim_knob_ranges_hcc1395.tsv`、`KNOBS`，再跑 `bash tools/diplosim_purity_holdout_v2.sh <purity> <purity 範圍> <coverage> <真實端目錄>`。
3. **評分與畫圖：** `ppc_distance_score.py`、`plot_purity_holdout_trend.py`。
4. **只改真實端：** `diplosim_ppc_mask_real.py`。

完整指令照抄最新一次實驗：`lab_report/2026-11-01_diplosim_detection_curve/README.md` 第 3 節（`KNOBS` 見 `2026-11-01_diplosim_matched_normal`）。t50 的真實端表在 `lab_report/2026-10-31_diplosim_ppc_hcc1395_lost045/tables/`。

## 資料檔

| 檔案 | 內容 | 來源 |
|---|---|---|
| `diplosim_knob_ranges_hcc1395.tsv` | diplosim 旋鈕的抽樣範圍（flag、lo、hi、lin／log） | `lab_report/2026-11-01_diplosim_knob_ranges` |
| `clairs_detection_curve_hcc1395.tsv` | ClairS 在 HCC1395 的偵測曲線 P(called \| alt reads) | `lab_report/2026-11-01_clairs_detection_curve` |

## 依主題

### diplosim 驗證（單次分析與圖）

| 腳本 | 做什麼 |
|---|---|
| `diplosim_purity_holdout_one.sh` | 一個 subsample 的真實端處理 |
| `cn_state_ascat_vs_diplosim.py` | CN 狀態分布：ASCAT（真實）對 diplosim |
| `split_alt_by_alt_count.py` | 「alt 分在兩條 HP」依 alt 數分組 |
| `plot_purity_holdout_trend.py` | purity 對統計量：真實值對模擬 95% 區間 |
| `plot_diplosim_purity_summary.py` | 10-31 至 11-01 holdout 的總結圖 |
| `plot_clairs_detection_curve.py` | ClairS 偵測曲線圖 |
| `plot_mask_ig_loh.py` | 抗體基因區遮罩前後的 LOH 比例 |
| `plot_vmr_repeat_cause.py` | t50 depth VMR 偏高的原因圖 |
| `plot_depth_vmr_explainer.py` | 解釋 depth VMR 與 φ（「預設」那一格的輸入已刪，畫不出來） |
| `plot_diplosim_demo.py` | 同一 seed 三種參數的示範圖 |
| `draw_error_knobs.py`、`draw_tag_knobs.py` | 11-04 投影片的錯誤旋鈕、tag 旋鈕示意圖（不是資料） |
| `draw_diplosim_purity_holdout_plan.py` | holdout 計畫示意圖 |

### 真實資料量測

| 腳本 | 做什麼 |
|---|---|
| `measure_snv_base_error.py` | normal 樣本在 somatic SNV 位點的鹼基錯誤率（預設輸出路徑指向已刪目錄，執行時請指定輸出） |
| `normal_allelic_dispersion.py` | normal 樣本 germline het 的 allele 計數分散度 |
| `seqc2_hcc1395_clonality.py` | SEQC2 真值 VAF＋ASCAT CN 估 truncal SNV 比例 |
| `seqc2_snv_neighbors.py` | somatic SNV 的鄰居數：SEQC2 真值、均勻分布、模擬資料 |
| `caller_detection_calibration.py` | ONT somatic caller 對 SEQC2 真值的靈敏度 |
| `ascat_hcc1395_5khz/run_ascat.sh`（→ `run_ascat.R`） | HCC1395 ONT 5kHz 的 ASCAT |

### HG008

HG008 的 bulk 資料用共用副本 `/big8_disk/yungjen114/data/HG008/`（`docs/tumor_sample.md`「HG008」）。下列腳本多數需要 8 株 clone 或單細胞資料，共用副本沒有，目前跑不了。

| 腳本 | 做什麼 |
|---|---|
| `hg008_truth_tree_stats.py` | HG008 CN／SNV 統計（寫死的 `benchmark_data/GIAB/HG008` 已不存在） |
| `hg008_clone_tree.py` → `hg008_clone_events.py` → `hg008_bulk_hp.py` | clone 樹分析步驟 1–3 |
| `hg008_clone_hp_orient.py` | 每個 clone 樹 SNV 的 assembly haplotype |
| `hg008_sc_tree_check.py` | 用 119 顆 PTA 單細胞檢查 clone 樹 |
| `draw_hg008_clone_tree.py` | 畫 clone 樹與事件 |

### 樹重建（PhyClone 的 Python 版擴充；已移植到 haploclone）

`phyclone_hp.py`（A1／A2 emission）與 `phyclone_pairs.py`（C4 read 共現）是 Python 參考實作，Rust 版在 haploclone（`rust/docs/PORTING.md`）。新的實驗用 haploclone。

| 腳本 | 做什麼 |
|---|---|
| `phyclone_hp.py`、`phyclone_pairs.py`、`test_phyclone_pairs.py` | A1／A2、C4 的 Python 實作與測試 |
| `eval_hp_truth_phyclone.py` | MAP 結果對設計真值樹評分（被 5 支腳本使用） |
| `hp_truth_tree_to_phyclone.py`、`draw_hp_truth_tree.py`、`typical_truth_tree.py` | 設計真值樹：轉成輸入、畫圖、典型樹 |
| `summarize_hp_truth_topologies.py`、`summarize_random_tree_methods.py`、`eval_random_tree_phyclone.py` | 真值樹與隨機樹實驗的彙總 |
| `c4_pair_evidence.py`、`c4_pair_weight_diagnostics.py`、`c4_posthoc.py`、`c4_truth_vs_map.py`、`summarize_c4_robustness.py`、`summarize_truth_vs_map.py` | C4 診斷（輸入的模擬資料已在 11-04 刪除） |
| `eval_phyclone_dataset.py`、`test_eval_phyclone_dataset.py` | 論文 benchmark 的評估程式（haploclone V4） |

### 模擬器選擇（CONIPHER、Pairtree）

| 腳本 | 做什麼 |
|---|---|
| `conipher_sim_rerun.py` → `conipher_sim_check.py` | 重跑 CONIPHER benchmark 並核對 |
| `conipher_wgd_multiplicity.py` | CONIPHER clonal WGD 下的 truncal multiplicity |
| `pairtree_sim_check.py`、`pairtree_sim_to_phyclone.py` | 重跑 Pairtree 模擬並轉格式 |

### 其他

| 腳本 | 做什麼 |
|---|---|
| `draw_claude_md_workflow.py` | 把 `CLAUDE.md` 的工作流程畫成泳道圖 |
| `remote_zip_extract.py` | 用 HTTP Range 只解壓遠端 zip 的部分檔案 |
