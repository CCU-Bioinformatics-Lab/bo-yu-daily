# lab_report 索引

一個實驗一個目錄（`YYYY-MM-DD_<主題>/README.md`）。本檔列出每個實驗的一句結論和狀態。整理日期：2026-11-04。

**先看這幾份：**

1. `2026-11-01_diplosim_purity_summary/`：diplosim 在 HCC1395 5 個 purity 上的驗證總結（10-31 到 11-01 的六步）。
2. `2026-11-03_diplosim_mask_ig_loci/`、`2026-11-03_diplosim_vmr_t50_repeats/`：總結之後還沒解開的兩個差距，原因都在真實端。
3. `../diplosim/DECISIONS.md`：每個實驗最後採用了什麼。

**狀態：**

- **現行**：目前的結論或方法，可以直接引用。
- **已整理**：結果已寫進另一份總結，要細節才看這裡。
- **被取代**：有更新的版本，以後者為準。
- **原始輸出**：沒有 README，只有表和圖；說明寫在另一份 README。
- **依賴已刪**：用到的資料在 2026-11-04 刪除，結論可讀，重跑不了。

新增實驗時，在對應的表加一列；某個實驗被取代時，改它的狀態。

## diplosim 驗證：HCC1395 purity holdout（10-31 至 11-03）

| 目錄 | 結論 | 狀態 |
|---|---|---|
| `2026-11-03_diplosim_mask_ig_loci` | 低 purity 的 LOH 比例對不上，不是 diplosim 的問題：normal（B 細胞株）在抗體基因區少一條 allele；真實端排除 3 區後對上 | 現行 |
| `2026-11-03_diplosim_vmr_t50_repeats` | t50 的 depth VMR 只高出模擬區間 0.07，原因是 reference 重複序列 | 現行 |
| `2026-11-01_diplosim_purity_summary` | 六步後 13 項通過數從 8/6/5/3/1 升到 12/13/12/11/8（t50→t10）；低 purity 的差距多來自量測端 | 現行（總結） |
| `2026-11-01_diplosim_detection_curve` | 加 ClairS 偵測曲線後，低 purity 明顯改善（步驟 ⑥） | 已整理 → summary |
| `2026-11-01_diplosim_purity_normal_share` | purity 換算加入 normal 的 tumor 比例 c，t40、t30 各多過 1–2 項（步驟 ⑤） | 已整理 → summary |
| `2026-11-01_diplosim_matched_normal` | 加配對 normal 與 ClairS normal-AF 規則，通過數幾乎沒變（步驟 ④） | 已整理 → summary |
| `2026-11-01_diplosim_knob_ranges` | 旋鈕改成範圍抽樣，落在區間內的項數變多（步驟 ③） | 已整理 → summary |
| `2026-11-01_diplosim_split_alt_mistag` | 用逐位點 mistag 取代大的 base error，「alt 分在兩條 HP」不再隨 purity 變大（步驟 ②） | 已整理 → summary |
| `2026-11-01_diplosim_phi_from_normal` | 從純 normal 量 depth φ，依估計式在 0.006–0.025 | 已整理 → summary |
| `2026-11-01_clairs_detection_curve` | ClairS 偵測曲線和 purity 有關，一條共用曲線不夠；曲線檔是 `tools/clairs_detection_curve_hcc1395.tsv` | 現行（偵測曲線的來源） |
| `2026-10-31_diplosim_purity_holdout_v2` | 修正比較流程後重跑 5 個 purity，VAF 差距大幅縮小（步驟 ①） | 已整理 → summary；取代 v1 |
| `2026-10-31_diplosim_purity_holdout` | 第一版 holdout：purity 越低差距越大 | 被取代 → v2 |
| `2026-10-31_diplosim_purity_holdout_plan` | holdout 的計畫與示意圖 | 被取代 → 已執行（v1、v2）；11-04 投影片仍引用 |
| `2026-10-31_ppc_distance_score` | PPC 改用距離評分；CN 相關 6 項 `--prop-pos-lost` 0.45 與 0.5 最接近 | 現行（評分方法） |

## diplosim 調參：只用 t50_n00（10-31）

結論都已寫進 `../diplosim/DECISIONS.md` 2026-10-31 列。這些目錄的 `tables/real_per_snv.tsv`、`clairs_hc_sites.tsv` 是 HCC1395 t50 真實資料表的副本（內容相同）；目前程式引用 `2026-10-31_diplosim_ppc_hcc1395_lost045/tables/`。

| 目錄 | 結論 | 狀態 |
|---|---|---|
| `2026-10-31_cn_state_ascat_vs_diplosim` | diplosim 只產生 5 種 CN 狀態，對不上 ASCAT（例如 (3,0)），促成「第二次 truncal CNA」 | 現行（證據） |
| `2026-10-31_diplosim_ppc_hcc1395_lost045` | `--prop-pos-lost 0.45`：14 項中 7 項在範圍內 | 已整理；真實資料表的引用來源 |
| `2026-10-31_diplosim_ppc_hcc1395_lost05` | `--prop-pos-lost 0.5`：在範圍內從 5 項變 7 項 | 已整理 |
| `2026-10-31_diplosim_ppc_hcc1395_wgd_lost045` | 加 clonal WGD 變差（7 → 2 項） | 已整理（未採用） |
| `2026-10-31_diplosim_ppc_hcc1395_second05` | 加第二次 CNA 0.5，7 → 5 項 | 已整理（單獨用變差；後來和 `mult_t0.8` 一起用） |
| `2026-10-31_diplosim_ppc_hcc1395_cnloh_second05` | 再加 `cnloh_B`，只剩 4 項 | 已整理（單獨用變差；後來和 `mult_t0.8` 一起用） |
| `2026-10-31_diplosim_ppc_hcc1395_tagbeta` | 每位點 tag 機率 ~ Beta，tag 相關 3 項都對上 | 已整理（採用，`tag_concentration`） |
| `2026-10-31_diplosim_ppc_hcc1395_err001` | mistag 與 base error 各 0.01 太多（0.058 對真實 0.028） | 已整理 |
| `2026-10-31_diplosim_ppc_hcc1395_err0005_pur097` | 錯誤率 0.005 剛好（0.026 對 0.028） | 已整理 |
| `2026-10-31_diplosim_ppc_hcc1395_base001` | 只把 base error 調到 0.01 也能對上「alt 分在兩條 HP」 | 已整理 |
| `2026-10-31_diplosim_ppc_hcc1395_pur097_base0005` | mistag 與 base error 的效果大致相加 | 已整理 |
| `2026-10-31_diplosim_ppc_hcc1395_gainB2` | `gain_B` 比重加倍，HP 內 VAF 中位數差距減半 | 已整理 |
| `2026-10-31_diplosim_ppc_hcc1395_mult_t0.8` | SNV 可排在兩次 CNA 之間＋truncal 0.8，multiplicity 對上 | 已整理（採用） |
| `2026-10-31_diplosim_ppc_hcc1395_depthdisp0.03` | depth 改 negative binomial，φ 0.03 時 VMR 對上 | 已整理（採用，`--depth-dispersion`） |
| `2026-10-31_diplosim_ppc_hcc1395_truncal09` | truncal 0.9 整體變差 | 已整理（未採用） |
| `…_depthdisp0.01`、`…_depthdisp0.02` | — | 原始輸出 → `depthdisp0.03` |
| `…_mult_t0.6`、`…_mult_t0.7`、`…_early_b0.6`、`…_early_b0.7`、`…_early_b0.8` | — | 原始輸出 → `mult_t0.8`、`gainB2` |
| `…_gainB3` | — | 原始輸出 → `gainB2` |
| `…_err0005` | — | 原始輸出 → `err0005_pur097` |
| `…_pur097_mistag0005`、`…_pur097_noerr` | — | 原始輸出 → `pur097_base0005` |

## 真實資料量測

| 目錄 | 結論 | 狀態 |
|---|---|---|
| `2026-10-30_ascat_hcc1395_5khz` | HCC1395 ONT 5kHz 的 ASCAT：purity 0.97、ploidy 3.06；diplosim 的驗證目標，不當輸入 | 現行 |
| `2026-10-25_seqc2_hcc1395_measured_purity` | `tX_nY` 是 tumor DNA 比例；實測細胞 purity 較低（例：t20 0.32） | 現行（`docs/tumor_sample.md` 引用） |
| `2026-10-25_hcc1395_hp_split` | 92.2% 的 somatic SNV 的 alt read 集中在同一條 HP | 現行 |
| `2026-10-25_hg008_truth_tree_plausibility` | HG008 有 haplotype-specific gain 與 CN timing 的真實實例 | 現行（證據） |
| `2026-10-27_hg008_sc_tree_check` | 119 顆 PTA 單細胞支持 truncal → {SC9, SC14, SC24, SC28} → {SC14, SC28} | 依賴已刪（clone 樹輸入） |

## 樹重建方法（PhyClone／haploclone 的依據）

| 目錄 | 結論 | 狀態 |
|---|---|---|
| `2026-10-24_hp_truth_tree_phyclone` | HP 設計真值樹的基線：加第二個 sample 後 4 個 clone 全對 | 現行（基線） |
| `2026-10-25_hp_a1a2_vs_base` | A2（loss-aware emission）解決突變遺失 P3 | 現行（A1／A2 依據） |
| `2026-10-25_typical_truth_tree` | 典型樹的參數都取自真實 cohort 中位數 | 現行 |
| `2026-10-26_c4_error_model` | pair score 的錯誤率設成真實值時，模式 1（clone 被拆開）消失 | 依賴已刪（模擬資料） |
| `2026-10-26_c4_hp_uncertain` | 加 HP 不確定性修好目標錯誤，但整體變差 | 依賴已刪 |
| `2026-10-26_c4_truth_vs_map` | 129 個 run 幾乎沒有抽樣問題；模式 2 來自 FSCRP prior | 依賴已刪 |
| `2026-10-27_v4_evaluator` | 評估程式重現論文 2,832 列中的 2,830 列 | 現行（haploclone V4） |

## 模擬器選擇

| 目錄 | 結論 | 狀態 |
|---|---|---|
| `2026-10-22_pairtree_conipher_sim_rerun` | CONIPHER 的生成程式可逐 byte 重現 benchmark；Pairtree 沒存 seed | 現行（diplosim 以 CONIPHER 為起點的依據） |

## 已刪除的實驗

2026-11-04 刪除了已排除路線（PCDH、FS-CRP 重跑、TRACERx／PCAWG 統計等）和舊模擬器的實驗。有進 git 的可用 `git show efb15e9:lab_report/<目錄>/README.md` 取回（2026-10-25 的 c4、random_tree 系列），其餘沒進 git，無法取回。
